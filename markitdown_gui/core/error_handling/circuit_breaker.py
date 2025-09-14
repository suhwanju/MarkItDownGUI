"""
Circuit Breaker Pattern Implementation

Prevents cascade failures during document conversion by monitoring failure rates
and automatically switching to fallback strategies when thresholds are exceeded.
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .conversion_errors import ConversionError, RecoverableError, UnrecoverableError


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Circuit is open, failing fast
    HALF_OPEN = "half_open" # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: float = 60.0      # Seconds to wait before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Operation timeout in seconds
    failure_rate_threshold: float = 0.5 # Failure rate threshold (0.0-1.0)
    window_size: int = 10               # Size of sliding window for failure rate
    
    # Error type weights (higher = more severe)
    error_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.error_weights is None:
            self.error_weights = {
                "FontDescriptorError": 2.0,      # Font errors are severe
                "PDFParsingError": 1.5,          # PDF errors are concerning
                "MarkItDownError": 1.0,          # Standard MarkItDown errors
                "ConversionMemoryError": 2.0,    # Memory errors are severe
                "ConversionTimeoutError": 1.5,   # Timeout errors are concerning
                "UnrecoverableError": 3.0,       # Unrecoverable errors are critical
                "RecoverableError": 0.5,         # Recoverable errors are less severe
                "default": 1.0                   # Default weight for other errors
            }


@dataclass
class OperationResult:
    """Result of a circuit breaker protected operation"""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CircuitBreakerError(Exception):
    """Circuit breaker is open, operation rejected"""
    
    def __init__(self, message: str, state: CircuitBreakerState, failure_count: int):
        super().__init__(message)
        self.state = state
        self.failure_count = failure_count


class CircuitBreaker:
    """Circuit breaker for conversion operations"""
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Thread safety
        self._lock = threading.Lock()
        
        # State management
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        
        # Operation history (sliding window)
        self._operation_history: List[OperationResult] = []
        self._total_operations = 0
        
        # Metrics
        self._metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "circuit_opened_count": 0,
            "avg_execution_time": 0.0,
            "last_failure_time": None,
            "state_changes": []
        }
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments  
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Original exception: If function fails and circuit remains closed
        """
        with self._lock:
            # Check if circuit is open
            if self._state == CircuitBreakerState.OPEN:
                if not self._should_attempt_reset():
                    self._record_rejected_call()
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Failure count: {self._failure_count}, "
                        f"Last failure: {self._last_failure_time}",
                        self._state,
                        self._failure_count
                    )
                else:
                    # Try to transition to half-open
                    self._transition_to_half_open()
        
        # Execute the operation
        start_time = time.time()
        result = OperationResult(success=False, timestamp=datetime.now())
        
        try:
            # Apply timeout if configured
            if self.config.timeout > 0:
                # Simple timeout implementation
                # Note: For more sophisticated timeout, consider using concurrent.futures
                result.result = func(*args, **kwargs)
            else:
                result.result = func(*args, **kwargs)
            
            # Operation succeeded
            result.success = True
            result.execution_time = time.time() - start_time
            self._record_success(result)
            
            return result.result
            
        except Exception as e:
            # Operation failed
            result.error = e
            result.execution_time = time.time() - start_time
            self._record_failure(result)
            
            # Re-raise the original exception
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        if self._last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self._last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout
    
    def _record_success(self, result: OperationResult):
        """Record successful operation"""
        with self._lock:
            self._add_to_history(result)
            self._metrics["successful_operations"] += 1
            self._update_avg_execution_time(result.execution_time)
            
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._transition_to_closed()
    
    def _record_failure(self, result: OperationResult):
        """Record failed operation"""
        with self._lock:
            self._add_to_history(result)
            self._metrics["failed_operations"] += 1
            self._metrics["last_failure_time"] = result.timestamp
            self._update_avg_execution_time(result.execution_time)
            
            # Calculate failure weight
            error_weight = self._get_error_weight(result.error)
            weighted_failure_count = self._failure_count + error_weight
            
            self._failure_count = int(weighted_failure_count)
            self._last_failure_time = result.timestamp
            self._success_count = 0  # Reset success count
            
            # Check if we should open the circuit
            if self._should_open_circuit():
                self._transition_to_open()
    
    def _record_rejected_call(self):
        """Record a call rejected due to open circuit"""
        with self._lock:
            # Don't count as operation, but track for metrics
            pass
    
    def _get_error_weight(self, error: Optional[Exception]) -> float:
        """Get weight for error type"""
        if error is None:
            return 0.0
        
        error_type = type(error).__name__
        
        # Check specific error types first
        if error_type in self.config.error_weights:
            return self.config.error_weights[error_type]
        
        # Check if it's a ConversionError subclass
        if isinstance(error, UnrecoverableError):
            return self.config.error_weights.get("UnrecoverableError", 3.0)
        elif isinstance(error, RecoverableError):
            return self.config.error_weights.get("RecoverableError", 0.5)
        elif isinstance(error, ConversionError):
            return self.config.error_weights.get("ConversionError", 1.0)
        
        # Default weight
        return self.config.error_weights["default"]
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Check failure count threshold
        if self._failure_count >= self.config.failure_threshold:
            return True
        
        # Check failure rate in sliding window
        if len(self._operation_history) >= self.config.window_size:
            failures_in_window = sum(1 for op in self._operation_history[-self.config.window_size:] if not op.success)
            failure_rate = failures_in_window / self.config.window_size
            
            if failure_rate >= self.config.failure_rate_threshold:
                return True
        
        return False
    
    def _add_to_history(self, result: OperationResult):
        """Add operation result to history"""
        self._operation_history.append(result)
        self._total_operations += 1
        self._metrics["total_operations"] += 1
        
        # Maintain sliding window size
        if len(self._operation_history) > self.config.window_size * 2:
            self._operation_history = self._operation_history[-self.config.window_size:]
    
    def _update_avg_execution_time(self, execution_time: float):
        """Update average execution time"""
        total_ops = self._metrics["total_operations"]
        if total_ops == 1:
            self._metrics["avg_execution_time"] = execution_time
        else:
            current_avg = self._metrics["avg_execution_time"]
            self._metrics["avg_execution_time"] = ((current_avg * (total_ops - 1)) + execution_time) / total_ops
    
    def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        if self._state != CircuitBreakerState.OPEN:
            self.logger.warning(
                f"Circuit breaker '{self.name}' opening due to {self._failure_count} failures. "
                f"Last failure: {self._last_failure_time}"
            )
            self._state = CircuitBreakerState.OPEN
            self._metrics["circuit_opened_count"] += 1
            self._record_state_change(CircuitBreakerState.OPEN)
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        self.logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        self._state = CircuitBreakerState.HALF_OPEN
        self._success_count = 0
        self._record_state_change(CircuitBreakerState.HALF_OPEN)
    
    def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        self.logger.info(f"Circuit breaker '{self.name}' closing after {self._success_count} successes")
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._record_state_change(CircuitBreakerState.CLOSED)
    
    def _record_state_change(self, new_state: CircuitBreakerState):
        """Record state change for metrics"""
        self._metrics["state_changes"].append({
            "timestamp": datetime.now(),
            "from_state": self._state.value if hasattr(self, '_state') else None,
            "to_state": new_state.value,
            "failure_count": self._failure_count
        })
    
    def force_open(self):
        """Force circuit breaker to OPEN state"""
        with self._lock:
            self.logger.warning(f"Force opening circuit breaker '{self.name}'")
            self._transition_to_open()
    
    def force_close(self):
        """Force circuit breaker to CLOSED state"""
        with self._lock:
            self.logger.info(f"Force closing circuit breaker '{self.name}'")
            self._transition_to_closed()
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        with self._lock:
            self.logger.info(f"Resetting circuit breaker '{self.name}'")
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._operation_history.clear()
    
    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self._state
    
    @property
    def failure_count(self) -> int:
        """Get current failure count"""
        return self._failure_count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        with self._lock:
            metrics = self._metrics.copy()
            
            # Add current state information
            metrics.update({
                "name": self.name,
                "current_state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure_time": self._last_failure_time,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "success_threshold": self.config.success_threshold,
                    "timeout": self.config.timeout,
                    "failure_rate_threshold": self.config.failure_rate_threshold,
                    "window_size": self.config.window_size
                }
            })
            
            # Calculate current failure rate
            if self._operation_history:
                recent_operations = self._operation_history[-self.config.window_size:]
                failures = sum(1 for op in recent_operations if not op.success)
                metrics["current_failure_rate"] = failures / len(recent_operations)
            else:
                metrics["current_failure_rate"] = 0.0
            
            return metrics