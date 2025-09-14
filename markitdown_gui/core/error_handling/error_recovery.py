"""
Error Recovery Manager

Coordinates error recovery actions with validation, circuit breakers, and fallback strategies.
Provides intelligent recovery decision-making for document conversion failures.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging
import time

from ..models import FileInfo, ConversionResult, ConversionStatus
from .conversion_errors import ConversionError, FontDescriptorError, PDFParsingError, RecoverableError, UnrecoverableError
from .circuit_breaker import CircuitBreaker, CircuitBreakerState
from .fallback_manager import FallbackManager, FallbackResult


class RecoveryAction(Enum):
    """Recovery action types"""
    RETRY = "retry"                          # Retry original conversion
    FALLBACK = "fallback"                    # Use fallback strategy
    VALIDATE_FIRST = "validate_first"        # Validate before retry
    REPAIR_DOCUMENT = "repair_document"      # Attempt document repair
    SKIP_FILE = "skip_file"                 # Skip this file
    ABORT_BATCH = "abort_batch"             # Abort entire batch
    USER_INTERVENTION = "user_intervention"  # Request user decision


@dataclass
class RecoveryResult:
    """Result of recovery action"""
    action_taken: RecoveryAction
    success: bool
    result: Optional[ConversionResult] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    recovery_details: Optional[Dict[str, Any]] = None


class ErrorRecoveryManager:
    """Manages error recovery strategies for document conversion"""
    
    def __init__(self, fallback_manager: Optional[FallbackManager] = None):
        self.logger = logging.getLogger(__name__)
        self.fallback_manager = fallback_manager or FallbackManager()
        
        # Recovery rules mapping error types to actions
        self._recovery_rules = self._initialize_recovery_rules()
        
        # Circuit breaker for recovery operations
        self._recovery_circuit_breaker = CircuitBreaker("error_recovery")
        
        # Recovery metrics
        self._recovery_metrics = {
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "recovery_by_action": {},
            "recovery_by_error_type": {}
        }
    
    def _initialize_recovery_rules(self) -> Dict[type, List[RecoveryAction]]:
        """Initialize recovery rules for different error types"""
        return {
            FontDescriptorError: [
                RecoveryAction.VALIDATE_FIRST,
                RecoveryAction.FALLBACK,
                RecoveryAction.USER_INTERVENTION
            ],
            PDFParsingError: [
                RecoveryAction.VALIDATE_FIRST,
                RecoveryAction.FALLBACK,
                RecoveryAction.RETRY
            ],
            RecoverableError: [
                RecoveryAction.RETRY,
                RecoveryAction.FALLBACK,
                RecoveryAction.VALIDATE_FIRST
            ],
            UnrecoverableError: [
                RecoveryAction.FALLBACK,
                RecoveryAction.SKIP_FILE
            ],
            ConversionError: [
                RecoveryAction.RETRY,
                RecoveryAction.FALLBACK,
                RecoveryAction.USER_INTERVENTION
            ]
        }
    
    def recover_from_error(self, error: ConversionError, file_info: FileInfo, output_path: Path,
                          original_converter: Optional[Callable] = None,
                          max_recovery_attempts: int = 3) -> RecoveryResult:
        """
        Attempt to recover from conversion error
        
        Args:
            error: The conversion error to recover from
            file_info: File information
            output_path: Target output path
            original_converter: Optional original conversion function to retry
            max_recovery_attempts: Maximum recovery attempts
            
        Returns:
            RecoveryResult with recovery outcome
        """
        start_time = time.time()
        self._recovery_metrics["total_recoveries"] += 1
        
        self.logger.info(f"Starting error recovery for {file_info.name}: {type(error).__name__}")
        
        try:
            # Determine recovery actions based on error type
            recovery_actions = self._get_recovery_actions(error)
            
            if not recovery_actions:
                return RecoveryResult(
                    action_taken=RecoveryAction.SKIP_FILE,
                    success=False,
                    error=ConversionError("No recovery actions available for this error type"),
                    execution_time=time.time() - start_time
                )
            
            # Try recovery actions in order
            for i, action in enumerate(recovery_actions):
                if i >= max_recovery_attempts:
                    break
                
                self.logger.info(f"Attempting recovery action: {action.value}")
                
                try:
                    result = self._execute_recovery_action(
                        action, error, file_info, output_path, original_converter
                    )
                    
                    result.execution_time = time.time() - start_time
                    
                    if result.success:
                        self.logger.info(f"Recovery successful with action: {action.value}")
                        self._record_recovery_success(action, type(error).__name__)
                        return result
                    else:
                        self.logger.warning(f"Recovery action {action.value} failed: {result.error}")
                        
                except Exception as recovery_error:
                    self.logger.error(f"Recovery action {action.value} threw exception: {recovery_error}")
                    if action == recovery_actions[-1]:  # Last action
                        return RecoveryResult(
                            action_taken=action,
                            success=False,
                            error=recovery_error,
                            execution_time=time.time() - start_time
                        )
            
            # All recovery actions failed
            self._record_recovery_failure(type(error).__name__)
            return RecoveryResult(
                action_taken=RecoveryAction.SKIP_FILE,
                success=False,
                error=ConversionError("All recovery actions failed"),
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"Error recovery process failed: {e}")
            self._record_recovery_failure(type(error).__name__)
            return RecoveryResult(
                action_taken=RecoveryAction.SKIP_FILE,
                success=False,
                error=e,
                execution_time=time.time() - start_time
            )
    
    def _get_recovery_actions(self, error: ConversionError) -> List[RecoveryAction]:
        """Get appropriate recovery actions for error type"""
        error_type = type(error)
        
        # Check for exact type match first
        if error_type in self._recovery_rules:
            return self._recovery_rules[error_type].copy()
        
        # Check for parent class matches
        for rule_type, actions in self._recovery_rules.items():
            if isinstance(error, rule_type):
                return actions.copy()
        
        # Default recovery actions
        return [RecoveryAction.FALLBACK, RecoveryAction.SKIP_FILE]
    
    def _execute_recovery_action(self, action: RecoveryAction, error: ConversionError,
                                file_info: FileInfo, output_path: Path,
                                original_converter: Optional[Callable] = None) -> RecoveryResult:
        """Execute a specific recovery action"""
        
        if action == RecoveryAction.RETRY:
            return self._retry_conversion(error, file_info, output_path, original_converter)
        
        elif action == RecoveryAction.FALLBACK:
            return self._execute_fallback(error, file_info, output_path)
        
        elif action == RecoveryAction.VALIDATE_FIRST:
            return self._validate_then_retry(error, file_info, output_path, original_converter)
        
        elif action == RecoveryAction.REPAIR_DOCUMENT:
            return self._repair_document(error, file_info, output_path)
        
        elif action == RecoveryAction.SKIP_FILE:
            return self._skip_file(error, file_info)
        
        elif action == RecoveryAction.USER_INTERVENTION:
            return self._request_user_intervention(error, file_info)
        
        else:
            return RecoveryResult(
                action_taken=action,
                success=False,
                error=ConversionError(f"Recovery action {action.value} not implemented")
            )
    
    def _retry_conversion(self, error: ConversionError, file_info: FileInfo, output_path: Path,
                         original_converter: Optional[Callable] = None) -> RecoveryResult:
        """Retry original conversion"""
        if not original_converter:
            return RecoveryResult(
                action_taken=RecoveryAction.RETRY,
                success=False,
                error=ConversionError("No original converter available for retry")
            )
        
        try:
            # Use circuit breaker for retry
            result = self._recovery_circuit_breaker.call(
                lambda: original_converter(file_info)
            )
            
            return RecoveryResult(
                action_taken=RecoveryAction.RETRY,
                success=result.status == ConversionStatus.SUCCESS,
                result=result,
                error=ConversionError(result.error_message) if result.status == ConversionStatus.FAILED else None
            )
            
        except Exception as e:
            return RecoveryResult(
                action_taken=RecoveryAction.RETRY,
                success=False,
                error=e
            )
    
    def _execute_fallback(self, error: ConversionError, file_info: FileInfo, output_path: Path) -> RecoveryResult:
        """Execute fallback conversion strategy"""
        fallback_result = self.fallback_manager.execute_fallback(
            file_info, output_path, error
        )
        
        return RecoveryResult(
            action_taken=RecoveryAction.FALLBACK,
            success=fallback_result.success,
            result=fallback_result.result,
            error=fallback_result.error,
            recovery_details={
                "fallback_strategy": fallback_result.strategy_name,
                "fallback_level": fallback_result.fallback_level
            }
        )
    
    def _validate_then_retry(self, error: ConversionError, file_info: FileInfo, output_path: Path,
                            original_converter: Optional[Callable] = None) -> RecoveryResult:
        """Validate document first, then retry conversion"""
        try:
            # Import validator here to avoid circular imports
            from ..validators import DocumentValidator, ValidationLevel
            
            # Validate document with strict level for recovery
            validator = DocumentValidator(ValidationLevel.STRICT)
            
            if validator.can_validate(file_info.path):
                validation_result = validator.validate(file_info.path)
                
                if validation_result.is_valid:
                    # Document is valid, try retry
                    return self._retry_conversion(error, file_info, output_path, original_converter)
                else:
                    # Document has validation issues, use fallback
                    self.logger.info(f"Document validation failed, using fallback for {file_info.name}")
                    return self._execute_fallback(error, file_info, output_path)
            else:
                # Can't validate, try fallback
                return self._execute_fallback(error, file_info, output_path)
                
        except Exception as e:
            # Validation failed, try fallback
            self.logger.warning(f"Validation failed during recovery: {e}")
            return self._execute_fallback(error, file_info, output_path)
    
    def _repair_document(self, error: ConversionError, file_info: FileInfo, output_path: Path) -> RecoveryResult:
        """Attempt to repair document (placeholder for future implementation)"""
        # This could be implemented with document repair tools in the future
        return RecoveryResult(
            action_taken=RecoveryAction.REPAIR_DOCUMENT,
            success=False,
            error=ConversionError("Document repair not yet implemented")
        )
    
    def _skip_file(self, error: ConversionError, file_info: FileInfo) -> RecoveryResult:
        """Skip file conversion"""
        self.logger.info(f"Skipping file {file_info.name} due to unrecoverable error")
        
        # Create a result indicating the file was skipped
        skip_result = ConversionResult(
            file_info=file_info,
            status=ConversionStatus.CANCELLED,
            error_message=f"File skipped due to error: {str(error)}",
            conversion_time=0.0,
            metadata={"recovery_action": "skip_file", "original_error": str(error)}
        )
        
        return RecoveryResult(
            action_taken=RecoveryAction.SKIP_FILE,
            success=True,  # Skipping is considered successful recovery
            result=skip_result
        )
    
    def _request_user_intervention(self, error: ConversionError, file_info: FileInfo) -> RecoveryResult:
        """Request user intervention (placeholder for UI integration)"""
        # This would integrate with UI components to show user dialog
        # For now, return failure to continue with other recovery actions
        return RecoveryResult(
            action_taken=RecoveryAction.USER_INTERVENTION,
            success=False,
            error=ConversionError("User intervention not implemented")
        )
    
    def _record_recovery_success(self, action: RecoveryAction, error_type: str):
        """Record successful recovery"""
        self._recovery_metrics["successful_recoveries"] += 1
        
        action_key = action.value
        if action_key not in self._recovery_metrics["recovery_by_action"]:
            self._recovery_metrics["recovery_by_action"][action_key] = {"success": 0, "failure": 0}
        self._recovery_metrics["recovery_by_action"][action_key]["success"] += 1
        
        if error_type not in self._recovery_metrics["recovery_by_error_type"]:
            self._recovery_metrics["recovery_by_error_type"][error_type] = {"success": 0, "failure": 0}
        self._recovery_metrics["recovery_by_error_type"][error_type]["success"] += 1
    
    def _record_recovery_failure(self, error_type: str):
        """Record failed recovery"""
        self._recovery_metrics["failed_recoveries"] += 1
        
        if error_type not in self._recovery_metrics["recovery_by_error_type"]:
            self._recovery_metrics["recovery_by_error_type"][error_type] = {"success": 0, "failure": 0}
        self._recovery_metrics["recovery_by_error_type"][error_type]["failure"] += 1
    
    def add_recovery_rule(self, error_type: type, actions: List[RecoveryAction]):
        """Add or update recovery rule for error type"""
        self._recovery_rules[error_type] = actions
        self.logger.info(f"Added recovery rule for {error_type.__name__}: {[a.value for a in actions]}")
    
    def remove_recovery_rule(self, error_type: type) -> bool:
        """Remove recovery rule for error type"""
        if error_type in self._recovery_rules:
            del self._recovery_rules[error_type]
            self.logger.info(f"Removed recovery rule for {error_type.__name__}")
            return True
        return False
    
    def get_recovery_rules(self) -> Dict[str, List[str]]:
        """Get current recovery rules"""
        return {
            error_type.__name__: [action.value for action in actions]
            for error_type, actions in self._recovery_rules.items()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get recovery metrics"""
        total_recoveries = self._recovery_metrics["total_recoveries"]
        success_rate = (
            self._recovery_metrics["successful_recoveries"] / total_recoveries 
            if total_recoveries > 0 else 0.0
        )
        
        return {
            **self._recovery_metrics,
            "success_rate": success_rate,
            "circuit_breaker": self._recovery_circuit_breaker.get_metrics(),
            "fallback_manager": self.fallback_manager.get_metrics()
        }
    
    def reset_metrics(self):
        """Reset recovery metrics"""
        self._recovery_metrics = {
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "recovery_by_action": {},
            "recovery_by_error_type": {}
        }
        self.logger.info("Reset recovery metrics")