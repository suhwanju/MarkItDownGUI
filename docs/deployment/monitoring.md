# Monitoring & Logging

## Overview

This guide covers comprehensive monitoring and logging strategies for the MarkItDown GUI application, including system health monitoring, application performance tracking, error logging, and alerting mechanisms.

## Logging Architecture

### Log Levels and Categories
```python
# markitdown_gui/core/logging_config.py
import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class LogCategory(Enum):
    APPLICATION = "application"
    CONVERSION = "conversion"
    UI = "ui"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ERROR = "error"

class StructuredLogger:
    def __init__(self, name: str, category: LogCategory):
        self.logger = logging.getLogger(name)
        self.category = category
        
    def log_structured(self, level: int, message: str, **kwargs):
        """Log with structured data"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'category': self.category.value,
            'message': message,
            'context': kwargs
        }
        
        self.logger.log(level, json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        self.log_structured(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log_structured(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log_structured(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log_structured(logging.DEBUG, message, **kwargs)

def setup_logging(config: Dict[str, Any]):
    """Set up application logging"""
    log_level = getattr(logging, config.get('level', 'INFO').upper())
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if config.get('console', {}).get('enabled', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.get('console', {}).get('level', 'WARNING')))
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    file_config = config.get('file', {})
    if file_config.get('enabled', True):
        log_dir = os.path.expanduser(config.get('directory', './logs'))
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'markitdown-gui.log')
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=file_config.get('max_size_mb', 10) * 1024 * 1024,
            backupCount=file_config.get('backup_count', 5)
        )
        file_handler.setLevel(log_level)
        
        # JSON formatter for structured logging
        json_formatter = JsonFormatter()
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)
    
    # Create category-specific loggers
    loggers = {}
    for category in LogCategory:
        logger = StructuredLogger(f"markitdown.{category.value}", category)
        loggers[category.value] = logger
    
    return loggers

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured log entries"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value
        
        return json.dumps(log_entry)
```

### Application Logging
```python
# markitdown_gui/core/app_logger.py
from .logging_config import StructuredLogger, LogCategory
import traceback
import functools
from typing import Callable, Any

class ApplicationLogger:
    def __init__(self):
        self.app_logger = StructuredLogger('markitdown.app', LogCategory.APPLICATION)
        self.conversion_logger = StructuredLogger('markitdown.conversion', LogCategory.CONVERSION)
        self.ui_logger = StructuredLogger('markitdown.ui', LogCategory.UI)
        self.performance_logger = StructuredLogger('markitdown.performance', LogCategory.PERFORMANCE)
        self.security_logger = StructuredLogger('markitdown.security', LogCategory.SECURITY)
        self.error_logger = StructuredLogger('markitdown.error', LogCategory.ERROR)
    
    def log_application_start(self, version: str, config: Dict[str, Any]):
        """Log application startup"""
        self.app_logger.info(
            "Application started",
            version=version,
            config_summary=self._sanitize_config(config)
        )
    
    def log_application_shutdown(self, reason: str = "normal"):
        """Log application shutdown"""
        self.app_logger.info("Application shutdown", reason=reason)
    
    def log_conversion_start(self, file_count: int, total_size_mb: float):
        """Log conversion batch start"""
        self.conversion_logger.info(
            "Conversion batch started",
            file_count=file_count,
            total_size_mb=total_size_mb
        )
    
    def log_conversion_complete(self, results: Dict[str, Any]):
        """Log conversion batch completion"""
        self.conversion_logger.info(
            "Conversion batch completed",
            success_count=results.get('successful_conversions', 0),
            failure_count=results.get('failed_conversions', 0),
            total_time_seconds=results.get('total_time_seconds', 0),
            success_rate=results.get('success_rate', 0)
        )
    
    def log_file_conversion(self, file_path: str, success: bool, 
                           processing_time: float, error: str = None):
        """Log individual file conversion"""
        if success:
            self.conversion_logger.info(
                "File converted successfully",
                file_path=file_path,
                processing_time_seconds=processing_time
            )
        else:
            self.conversion_logger.error(
                "File conversion failed",
                file_path=file_path,
                processing_time_seconds=processing_time,
                error_message=error
            )
    
    def log_ui_action(self, action: str, component: str, **kwargs):
        """Log UI interactions"""
        self.ui_logger.debug(
            f"UI action: {action}",
            component=component,
            **kwargs
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Log performance metrics"""
        self.performance_logger.info(
            f"Performance metric: {metric_name}",
            metric=metric_name,
            value=value,
            unit=unit
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        self.security_logger.warning(
            f"Security event: {event_type}",
            event_type=event_type,
            **details
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with full context"""
        self.error_logger.error(
            f"Error occurred: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=traceback.format_exc(),
            context=context or {}
        )
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config for logging"""
        sanitized = {}
        sensitive_keys = {'password', 'token', 'key', 'secret'}
        
        for key, value in config.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_config(value)
            else:
                sanitized[key] = value
        
        return sanitized

def log_exceptions(logger_func: Callable = None):
    """Decorator to automatically log exceptions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger_func:
                    logger_func(e, {
                        'function': func.__name__,
                        'args': str(args)[:100],  # Limit args length
                        'kwargs': str(kwargs)[:100]
                    })
                raise
        return wrapper
    return decorator

# Global application logger
app_logger = ApplicationLogger()
```

## System Health Monitoring

### Health Check System
```python
# markitdown_gui/core/health_monitor.py
import psutil
import os
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.details is None:
            self.details = {}

class HealthMonitor:
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.health_checks: Dict[str, Callable] = {}
        self.last_results: Dict[str, HealthCheck] = {}
        self.monitoring = False
        self.monitor_thread = None
        self.status_callbacks: List[Callable] = []
        
        # Register default health checks
        self.register_default_checks()
    
    def register_health_check(self, name: str, check_func: Callable[[], HealthCheck]):
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    def register_default_checks(self):
        """Register default system health checks"""
        self.register_health_check("memory_usage", self.check_memory_usage)
        self.register_health_check("disk_space", self.check_disk_space)
        self.register_health_check("cpu_usage", self.check_cpu_usage)
        self.register_health_check("thread_count", self.check_thread_count)
        self.register_health_check("temp_directory", self.check_temp_directory)
        self.register_health_check("output_directory", self.check_output_directory)
    
    def start_monitoring(self):
        """Start health monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.run_all_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                app_logger.log_error(e, {"component": "health_monitor"})
                time.sleep(self.check_interval)
    
    def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}
        
        for name, check_func in self.health_checks.items():
            try:
                result = check_func()
                results[name] = result
                self.last_results[name] = result
                
                # Log critical issues
                if result.status == HealthStatus.CRITICAL:
                    app_logger.error_logger.error(
                        f"Critical health check failure: {name}",
                        check_name=name,
                        message=result.message,
                        details=result.details
                    )
                
            except Exception as e:
                error_result = HealthCheck(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {str(e)}"
                )
                results[name] = error_result
                self.last_results[name] = error_result
        
        # Notify status callbacks
        overall_status = self.get_overall_status()
        for callback in self.status_callbacks:
            try:
                callback(overall_status, results)
            except Exception:
                pass
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.last_results:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in self.last_results.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif HealthStatus.UNKNOWN in statuses:
            return HealthStatus.UNKNOWN
        else:
            return HealthStatus.HEALTHY
    
    def check_memory_usage(self) -> HealthCheck:
        """Check system memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Get configured memory limit
        from .config_manager import config_manager
        max_memory = config_manager.get('performance.memory.max_usage_mb', 512)
        
        usage_percent = (memory_mb / max_memory) * 100
        
        if usage_percent > 90:
            status = HealthStatus.CRITICAL
            message = f"Memory usage critical: {memory_mb:.1f}MB ({usage_percent:.1f}%)"
        elif usage_percent > 75:
            status = HealthStatus.WARNING
            message = f"Memory usage high: {memory_mb:.1f}MB ({usage_percent:.1f}%)"
        else:
            status = HealthStatus.HEALTHY
            message = f"Memory usage normal: {memory_mb:.1f}MB ({usage_percent:.1f}%)"
        
        return HealthCheck(
            name="memory_usage",
            status=status,
            message=message,
            details={
                "memory_mb": memory_mb,
                "max_memory_mb": max_memory,
                "usage_percent": usage_percent
            }
        )
    
    def check_disk_space(self) -> HealthCheck:
        """Check available disk space"""
        from .config_manager import config_manager
        output_dir = config_manager.get('directories.output', './markdown')
        
        try:
            disk_usage = psutil.disk_usage(output_dir)
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            total_gb = disk_usage.total / 1024 / 1024 / 1024
            usage_percent = ((disk_usage.total - disk_usage.free) / disk_usage.total) * 100
            
            if free_gb < 0.1:  # Less than 100MB
                status = HealthStatus.CRITICAL
                message = f"Disk space critical: {free_gb:.1f}GB free"
            elif free_gb < 1.0:  # Less than 1GB
                status = HealthStatus.WARNING
                message = f"Disk space low: {free_gb:.1f}GB free"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space adequate: {free_gb:.1f}GB free"
            
            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                details={
                    "free_gb": free_gb,
                    "total_gb": total_gb,
                    "usage_percent": usage_percent,
                    "output_directory": output_dir
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check disk space: {str(e)}"
            )
    
    def check_cpu_usage(self) -> HealthCheck:
        """Check CPU usage"""
        process = psutil.Process()
        cpu_percent = process.cpu_percent(interval=1)
        
        if cpu_percent > 90:
            status = HealthStatus.WARNING
            message = f"CPU usage high: {cpu_percent:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"CPU usage normal: {cpu_percent:.1f}%"
        
        return HealthCheck(
            name="cpu_usage",
            status=status,
            message=message,
            details={"cpu_percent": cpu_percent}
        )
    
    def check_thread_count(self) -> HealthCheck:
        """Check thread count"""
        process = psutil.Process()
        thread_count = process.num_threads()
        
        if thread_count > 100:
            status = HealthStatus.WARNING
            message = f"High thread count: {thread_count}"
        else:
            status = HealthStatus.HEALTHY
            message = f"Thread count normal: {thread_count}"
        
        return HealthCheck(
            name="thread_count",
            status=status,
            message=message,
            details={"thread_count": thread_count}
        )
    
    def check_temp_directory(self) -> HealthCheck:
        """Check temp directory accessibility"""
        from .config_manager import config_manager
        temp_dir = config_manager.get('directories.temp', './temp')
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(temp_dir, '.health_check')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return HealthCheck(
                name="temp_directory",
                status=HealthStatus.HEALTHY,
                message=f"Temp directory accessible: {temp_dir}"
            )
            
        except Exception as e:
            return HealthCheck(
                name="temp_directory",
                status=HealthStatus.CRITICAL,
                message=f"Temp directory not accessible: {str(e)}",
                details={"temp_directory": temp_dir}
            )
    
    def check_output_directory(self) -> HealthCheck:
        """Check output directory accessibility"""
        from .config_manager import config_manager
        output_dir = config_manager.get('directories.output', './markdown')
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Test write access
            test_file = os.path.join(output_dir, '.health_check')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            return HealthCheck(
                name="output_directory",
                status=HealthStatus.HEALTHY,
                message=f"Output directory accessible: {output_dir}"
            )
            
        except Exception as e:
            return HealthCheck(
                name="output_directory",
                status=HealthStatus.CRITICAL,
                message=f"Output directory not accessible: {str(e)}",
                details={"output_directory": output_dir}
            )
    
    def add_status_callback(self, callback: Callable):
        """Add callback for status changes"""
        self.status_callbacks.append(callback)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for external monitoring"""
        overall_status = self.get_overall_status()
        
        return {
            "overall_status": overall_status.value,
            "timestamp": time.time(),
            "checks": {
                name: {
                    "status": check.status.value,
                    "message": check.message,
                    "timestamp": check.timestamp
                }
                for name, check in self.last_results.items()
            }
        }

# Global health monitor
health_monitor = HealthMonitor()
```

## Performance Metrics Collection

### Metrics Collection System
```python
# markitdown_gui/core/metrics_collector.py
import time
import threading
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
import statistics

@dataclass
class Metric:
    name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

class MetricsCollector:
    def __init__(self, retention_minutes: int = 60):
        self.retention_seconds = retention_minutes * 60
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque())
        self.aggregated_metrics: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def record_metric(self, name: str, value: float, unit: str = "", 
                     tags: Dict[str, str] = None):
        """Record a metric value"""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            tags=tags or {}
        )
        
        with self.lock:
            self.metrics[name].append(metric)
            
            # Log to application logger
            app_logger.log_performance_metric(name, value, unit)
    
    def record_timing(self, operation: str, duration_seconds: float, 
                     tags: Dict[str, str] = None):
        """Record operation timing"""
        self.record_metric(f"{operation}_duration", duration_seconds, "seconds", tags)
    
    def record_counter(self, name: str, increment: int = 1, 
                      tags: Dict[str, str] = None):
        """Record counter increment"""
        self.record_metric(f"{name}_count", increment, "count", tags)
    
    def record_gauge(self, name: str, value: float, unit: str = "",
                    tags: Dict[str, str] = None):
        """Record gauge value"""
        self.record_metric(f"{name}_gauge", value, unit, tags)
    
    def get_metric_stats(self, name: str, duration_minutes: int = 5) -> Optional[Dict]:
        """Get statistics for a metric over specified duration"""
        cutoff_time = time.time() - (duration_minutes * 60)
        
        with self.lock:
            if name not in self.metrics:
                return None
            
            recent_metrics = [
                m for m in self.metrics[name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return None
            
            values = [m.value for m in recent_metrics]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'latest': values[-1],
                'unit': recent_metrics[-1].unit,
                'timespan_minutes': duration_minutes
            }
    
    def get_throughput_stats(self, operation: str, 
                           duration_minutes: int = 5) -> Dict[str, float]:
        """Get throughput statistics for an operation"""
        cutoff_time = time.time() - (duration_minutes * 60)
        
        with self.lock:
            count_metric = f"{operation}_count"
            duration_metric = f"{operation}_duration"
            
            if count_metric not in self.metrics:
                return {}
            
            recent_counts = [
                m for m in self.metrics[count_metric]
                if m.timestamp >= cutoff_time
            ]
            
            recent_durations = [
                m for m in self.metrics.get(duration_metric, [])
                if m.timestamp >= cutoff_time
            ]
            
            total_operations = sum(m.value for m in recent_counts)
            total_time = sum(m.value for m in recent_durations)
            
            return {
                'operations_per_minute': total_operations / duration_minutes if duration_minutes > 0 else 0,
                'average_duration_seconds': total_time / len(recent_durations) if recent_durations else 0,
                'total_operations': total_operations,
                'total_time_seconds': total_time
            }
    
    def _cleanup_loop(self):
        """Clean up old metrics"""
        while True:
            try:
                cutoff_time = time.time() - self.retention_seconds
                
                with self.lock:
                    for name, metric_deque in self.metrics.items():
                        # Remove old metrics
                        while metric_deque and metric_deque[0].timestamp < cutoff_time:
                            metric_deque.popleft()
                
                time.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                app_logger.log_error(e, {"component": "metrics_cleanup"})
                time.sleep(300)
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """Export metrics in specified format"""
        if format == "prometheus":
            return self._export_prometheus()
        elif format == "json":
            return self._export_json()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        with self.lock:
            for name, metric_deque in self.metrics.items():
                if not metric_deque:
                    continue
                
                latest_metric = metric_deque[-1]
                
                # Add help and type comments
                lines.append(f"# HELP {name} {name} metric")
                lines.append(f"# TYPE {name} gauge")
                
                # Add metric line
                tags_str = ""
                if latest_metric.tags:
                    tag_pairs = [f'{k}="{v}"' for k, v in latest_metric.tags.items()]
                    tags_str = "{" + ",".join(tag_pairs) + "}"
                
                lines.append(f"{name}{tags_str} {latest_metric.value}")
        
        return "\n".join(lines)
    
    def _export_json(self) -> str:
        """Export metrics in JSON format"""
        import json
        
        export_data = {
            "timestamp": time.time(),
            "metrics": {}
        }
        
        with self.lock:
            for name, metric_deque in self.metrics.items():
                if not metric_deque:
                    continue
                
                export_data["metrics"][name] = [
                    {
                        "value": m.value,
                        "unit": m.unit,
                        "timestamp": m.timestamp,
                        "tags": m.tags
                    }
                    for m in metric_deque
                ]
        
        return json.dumps(export_data, indent=2)

# Global metrics collector
metrics_collector = MetricsCollector()

# Convenience functions for common metrics
def time_operation(operation_name: str):
    """Decorator to time operations"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_timing(
                    operation_name, 
                    duration,
                    {"success": str(success)}
                )
        return wrapper
    return decorator
```

## Alerting System

### Alert Management
```python
# markitdown_gui/core/alerting.py
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Callable, Optional
from enum import Enum
from dataclasses import dataclass
import requests

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: float
    resolved: bool = False
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class AlertManager:
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.notification_channels: Dict[str, Callable] = {}
        
        # Load configuration
        from .config_manager import config_manager
        self.config = config_manager.get_section('alerting')
        
        # Register notification channels
        self.register_notification_channels()
    
    def register_notification_channels(self):
        """Register available notification channels"""
        if self.config.get('email', {}).get('enabled', False):
            self.notification_channels['email'] = self.send_email_notification
        
        if self.config.get('webhook', {}).get('enabled', False):
            self.notification_channels['webhook'] = self.send_webhook_notification
        
        if self.config.get('desktop', {}).get('enabled', True):
            self.notification_channels['desktop'] = self.send_desktop_notification
    
    def create_alert(self, severity: AlertSeverity, title: str, message: str,
                    source: str, context: Dict[str, Any] = None) -> str:
        """Create a new alert"""
        import uuid
        
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            id=alert_id,
            severity=severity,
            title=title,
            message=message,
            source=source,
            timestamp=time.time(),
            context=context or {}
        )
        
        self.active_alerts[alert_id] = alert
        
        # Send notifications
        self.send_notifications(alert)
        
        # Log alert
        app_logger.error_logger.error(
            f"Alert created: {title}",
            alert_id=alert_id,
            severity=severity.value,
            source=source,
            message=message
        )
        
        return alert_id
    
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            
            app_logger.app_logger.info(
                "Alert resolved",
                alert_id=alert_id
            )
    
    def send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        severity_channels = {
            AlertSeverity.INFO: ['desktop'],
            AlertSeverity.WARNING: ['desktop', 'email'],
            AlertSeverity.ERROR: ['desktop', 'email', 'webhook'],
            AlertSeverity.CRITICAL: ['desktop', 'email', 'webhook']
        }
        
        channels = severity_channels.get(alert.severity, ['desktop'])
        
        for channel in channels:
            if channel in self.notification_channels:
                try:
                    self.notification_channels[channel](alert)
                except Exception as e:
                    app_logger.log_error(e, {
                        "component": "alerting",
                        "channel": channel,
                        "alert_id": alert.id
                    })
    
    def send_desktop_notification(self, alert: Alert):
        """Send desktop notification"""
        try:
            from PyQt6.QtWidgets import QSystemTrayIcon
            from PyQt6.QtGui import QIcon
            
            # This would integrate with the main application's system tray
            # For now, just log the notification
            app_logger.app_logger.info(
                f"Desktop notification: {alert.title}",
                alert_id=alert.id,
                message=alert.message
            )
        except Exception as e:
            pass  # Desktop notifications may not be available
    
    def send_email_notification(self, alert: Alert):
        """Send email notification"""
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled', False):
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_address')
            msg['To'] = ', '.join(email_config.get('to_addresses', []))
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Create email body
            body = f"""
Alert: {alert.title}
Severity: {alert.severity.value.upper()}
Source: {alert.source}
Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}

Message:
{alert.message}

Context:
{json.dumps(alert.context, indent=2)}
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config.get('smtp_host'), email_config.get('smtp_port', 587))
            server.starttls()
            server.login(email_config.get('username'), email_config.get('password'))
            
            text = msg.as_string()
            server.sendmail(msg['From'], email_config.get('to_addresses', []), text)
            server.quit()
            
        except Exception as e:
            app_logger.log_error(e, {
                "component": "email_notification",
                "alert_id": alert.id
            })
    
    def send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""
        webhook_config = self.config.get('webhook', {})
        
        if not webhook_config.get('enabled', False):
            return
        
        try:
            payload = {
                'alert_id': alert.id,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'source': alert.source,
                'timestamp': alert.timestamp,
                'context': alert.context
            }
            
            response = requests.post(
                webhook_config.get('url'),
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=30
            )
            
            response.raise_for_status()
            
        except Exception as e:
            app_logger.log_error(e, {
                "component": "webhook_notification",
                "alert_id": alert.id
            })
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get summary of alerts by severity"""
        active_alerts = self.get_active_alerts()
        
        summary = {severity.value: 0 for severity in AlertSeverity}
        
        for alert in active_alerts:
            summary[alert.severity.value] += 1
        
        return summary

# Global alert manager
alert_manager = AlertManager()

# Integration with health monitoring
def setup_health_alerting():
    """Set up alerting for health monitoring"""
    def health_status_callback(overall_status, check_results):
        for name, check in check_results.items():
            if check.status == HealthStatus.CRITICAL:
                alert_manager.create_alert(
                    AlertSeverity.CRITICAL,
                    f"Health Check Failed: {name}",
                    check.message,
                    "health_monitor",
                    check.details
                )
            elif check.status == HealthStatus.WARNING:
                alert_manager.create_alert(
                    AlertSeverity.WARNING,
                    f"Health Check Warning: {name}",
                    check.message,
                    "health_monitor",
                    check.details
                )
    
    health_monitor.add_status_callback(health_status_callback)
```

## Monitoring Dashboard

### Web-based Monitoring Interface
```python
# markitdown_gui/monitoring/web_dashboard.py
from flask import Flask, jsonify, render_template_string
import threading
from typing import Dict, Any

class MonitoringDashboard:
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = Flask(__name__)
        self.setup_routes()
        self.server_thread = None
    
    def setup_routes(self):
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_HTML)
        
        @self.app.route('/api/health')
        def health_status():
            return jsonify(health_monitor.get_health_summary())
        
        @self.app.route('/api/metrics')
        def metrics():
            return jsonify({
                'timestamp': time.time(),
                'metrics': self.get_current_metrics()
            })
        
        @self.app.route('/api/alerts')
        def alerts():
            active_alerts = alert_manager.get_active_alerts()
            return jsonify([
                {
                    'id': alert.id,
                    'severity': alert.severity.value,
                    'title': alert.title,
                    'message': alert.message,
                    'timestamp': alert.timestamp
                }
                for alert in active_alerts
            ])
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics for dashboard"""
        return {
            'memory_usage': metrics_collector.get_metric_stats('memory_usage_gauge'),
            'cpu_usage': metrics_collector.get_metric_stats('cpu_usage_gauge'),
            'conversion_throughput': metrics_collector.get_throughput_stats('file_conversion'),
            'active_threads': metrics_collector.get_metric_stats('thread_count_gauge')
        }
    
    def start(self):
        """Start the monitoring dashboard"""
        if self.server_thread and self.server_thread.is_alive():
            return
        
        self.server_thread = threading.Thread(
            target=lambda: self.app.run(host='0.0.0.0', port=self.port, debug=False),
            daemon=True
        )
        self.server_thread.start()
        
        print(f"Monitoring dashboard started on http://localhost:{self.port}")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MarkItDown GUI Monitoring</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric-card { border: 1px solid #ddd; padding: 15px; margin: 10px; border-radius: 5px; }
        .alert { padding: 10px; margin: 5px; border-radius: 3px; }
        .alert-critical { background-color: #f8d7da; border-color: #f5c6cb; }
        .alert-warning { background-color: #fff3cd; border-color: #ffeaa7; }
        .status-healthy { color: green; }
        .status-warning { color: orange; }
        .status-critical { color: red; }
    </style>
</head>
<body>
    <h1>MarkItDown GUI Monitoring Dashboard</h1>
    
    <div id="health-status">
        <h2>System Health</h2>
        <div id="health-summary"></div>
    </div>
    
    <div id="metrics">
        <h2>Performance Metrics</h2>
        <div id="metrics-summary"></div>
    </div>
    
    <div id="alerts">
        <h2>Active Alerts</h2>
        <div id="alerts-list"></div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setInterval(updateDashboard, 30000);
        updateDashboard();
        
        function updateDashboard() {
            updateHealth();
            updateMetrics();
            updateAlerts();
        }
        
        function updateHealth() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    const summary = document.getElementById('health-summary');
                    summary.innerHTML = `
                        <div class="metric-card">
                            <h3>Overall Status: <span class="status-${data.overall_status}">${data.overall_status.toUpperCase()}</span></h3>
                            <ul>
                                ${Object.entries(data.checks).map(([name, check]) => 
                                    `<li><strong>${name}:</strong> <span class="status-${check.status}">${check.message}</span></li>`
                                ).join('')}
                            </ul>
                        </div>
                    `;
                })
                .catch(error => console.error('Error updating health:', error));
        }
        
        function updateMetrics() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    const summary = document.getElementById('metrics-summary');
                    summary.innerHTML = `
                        <div class="metric-card">
                            <h3>Performance Metrics</h3>
                            <p>Memory Usage: ${data.metrics.memory_usage ? data.metrics.memory_usage.latest + ' MB' : 'N/A'}</p>
                            <p>CPU Usage: ${data.metrics.cpu_usage ? data.metrics.cpu_usage.latest + '%' : 'N/A'}</p>
                            <p>Conversion Rate: ${data.metrics.conversion_throughput ? data.metrics.conversion_throughput.operations_per_minute + ' files/min' : 'N/A'}</p>
                        </div>
                    `;
                })
                .catch(error => console.error('Error updating metrics:', error));
        }
        
        function updateAlerts() {
            fetch('/api/alerts')
                .then(response => response.json())
                .then(data => {
                    const alertsList = document.getElementById('alerts-list');
                    if (data.length === 0) {
                        alertsList.innerHTML = '<p>No active alerts</p>';
                    } else {
                        alertsList.innerHTML = data.map(alert => `
                            <div class="alert alert-${alert.severity}">
                                <strong>${alert.title}</strong><br>
                                ${alert.message}<br>
                                <small>${new Date(alert.timestamp * 1000).toLocaleString()}</small>
                            </div>
                        `).join('');
                    }
                })
                .catch(error => console.error('Error updating alerts:', error));
        }
    </script>
</body>
</html>
"""

# Global monitoring dashboard
monitoring_dashboard = MonitoringDashboard()
```

## Related Documentation

- 🚀 [Deployment Guide](deployment.md) - Production deployment
- ⚙️ [Configuration Management](configuration.md) - Environment settings  
- 📊 [Performance Tuning](performance.md) - Optimization guidelines
- 🔒 [Security Guidelines](security.md) - Security best practices

---

**Last Updated**: 2025-01-13  
**Version**: 1.0.0  
**Status**: 🚧 In Development