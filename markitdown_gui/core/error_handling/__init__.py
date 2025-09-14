"""
Error Handling Framework

Comprehensive error handling system for document conversion with circuit breaker pattern,
fallback strategies, and enhanced error reporting.
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerError
from .fallback_manager import FallbackManager, FallbackStrategy, FallbackResult
from .error_recovery import ErrorRecoveryManager, RecoveryAction, RecoveryResult
from .error_reporter import ErrorReporter, ErrorReport, ErrorSeverity
from .conversion_errors import (
    ConversionError, FontDescriptorError, PDFParsingError,
    MarkItDownError, RecoverableError, UnrecoverableError, categorize_exception
)

__all__ = [
    'CircuitBreaker',
    'CircuitBreakerState',
    'CircuitBreakerError',
    'FallbackManager',
    'FallbackStrategy',
    'FallbackResult',
    'ErrorRecoveryManager',
    'RecoveryAction',
    'RecoveryResult',
    'ErrorReporter',
    'ErrorReport', 
    'ErrorSeverity',
    'ConversionError',
    'FontDescriptorError',
    'PDFParsingError',
    'MarkItDownError',
    'RecoverableError',
    'UnrecoverableError',
    'categorize_exception'
]