"""
Fallback Strategy Manager

Manages multiple fallback conversion strategies when primary conversion fails
or circuit breaker is open. Provides graceful degradation for document conversion.
"""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Tuple
import logging
import time
from dataclasses import dataclass

from ..models import FileInfo, ConversionResult, ConversionStatus
from .conversion_errors import ConversionError, RecoverableError, UnrecoverableError
from .circuit_breaker import CircuitBreaker, CircuitBreakerState


class FallbackPriority(Enum):
    """Priority levels for fallback strategies"""
    HIGH = 1        # Try first after primary failure
    MEDIUM = 2      # Standard fallback priority
    LOW = 3         # Last resort fallback
    EMERGENCY = 4   # Only when all else fails


@dataclass
class FallbackResult:
    """Result of fallback strategy execution"""
    success: bool
    strategy_name: str
    result: Optional[ConversionResult] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    fallback_level: int = 0  # How many fallbacks deep we are


class FallbackStrategy(ABC):
    """Base class for fallback conversion strategies"""
    
    def __init__(self, name: str, priority: FallbackPriority = FallbackPriority.MEDIUM):
        self.name = name
        self.priority = priority
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._enabled = True
        self._success_count = 0
        self._failure_count = 0
        self._total_execution_time = 0.0
    
    @abstractmethod
    def can_handle(self, file_info: FileInfo, error: Optional[ConversionError] = None) -> bool:
        """
        Check if this fallback strategy can handle the file/error
        
        Args:
            file_info: File to convert
            error: Optional primary conversion error
            
        Returns:
            True if strategy can handle this case
        """
        pass
    
    @abstractmethod
    def execute(self, file_info: FileInfo, output_path: Path, 
                original_error: Optional[ConversionError] = None) -> ConversionResult:
        """
        Execute fallback conversion strategy
        
        Args:
            file_info: File to convert
            output_path: Target output path
            original_error: Optional original conversion error
            
        Returns:
            ConversionResult
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if strategy is enabled"""
        return self._enabled
    
    def enable(self):
        """Enable strategy"""
        self._enabled = True
    
    def disable(self):
        """Disable strategy"""
        self._enabled = False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        total_attempts = self._success_count + self._failure_count
        success_rate = (self._success_count / total_attempts) if total_attempts > 0 else 0.0
        avg_execution_time = (self._total_execution_time / total_attempts) if total_attempts > 0 else 0.0
        
        return {
            "name": self.name,
            "priority": self.priority.name,
            "enabled": self._enabled,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "total_attempts": total_attempts,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time
        }
    
    def _record_success(self, execution_time: float):
        """Record successful execution"""
        self._success_count += 1
        self._total_execution_time += execution_time
    
    def _record_failure(self, execution_time: float):
        """Record failed execution"""
        self._failure_count += 1
        self._total_execution_time += execution_time


class BasicTextExtractionStrategy(FallbackStrategy):
    """Basic text extraction fallback for when advanced conversion fails"""
    
    def __init__(self):
        super().__init__("basic_text_extraction", FallbackPriority.HIGH)
    
    def can_handle(self, file_info: FileInfo, error: Optional[ConversionError] = None) -> bool:
        """Can handle most text-based files"""
        # Handle PDFs with font issues
        if file_info.file_type.value == "pdf":
            return True
        
        # Handle Office documents
        if file_info.file_type.value in ["docx", "pptx", "xlsx"]:
            return True
        
        return False
    
    def execute(self, file_info: FileInfo, output_path: Path,
                original_error: Optional[ConversionError] = None) -> ConversionResult:
        """Execute basic text extraction"""
        start_time = time.time()
        
        try:
            # Simple text extraction without complex formatting
            extracted_text = self._extract_basic_text(file_info)
            
            if extracted_text.strip():
                # Save extracted text
                self._save_text_as_markdown(extracted_text, output_path, file_info)
                
                execution_time = time.time() - start_time
                self._record_success(execution_time)
                
                return ConversionResult(
                    file_info=file_info,
                    status=ConversionStatus.SUCCESS,
                    output_path=output_path,
                    conversion_time=execution_time,
                    metadata={
                        "fallback_strategy": self.name,
                        "extraction_method": "basic_text",
                        "original_error": str(original_error) if original_error else None
                    }
                )
            else:
                raise ConversionError("No text content extracted")
                
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_failure(execution_time)
            
            return ConversionResult(
                file_info=file_info,
                status=ConversionStatus.FAILED,
                error_message=f"Basic text extraction failed: {str(e)}",
                conversion_time=execution_time,
                metadata={
                    "fallback_strategy": self.name,
                    "extraction_method": "basic_text",
                    "original_error": str(original_error) if original_error else None
                }
            )
    
    def _extract_basic_text(self, file_info: FileInfo) -> str:
        """Extract basic text from file"""
        if file_info.file_type.value == "pdf":
            return self._extract_pdf_text_basic(file_info.path)
        elif file_info.file_type.value == "docx":
            return self._extract_docx_text_basic(file_info.path)
        elif file_info.file_type.value in ["txt", "md"]:
            return self._extract_plain_text(file_info.path)
        else:
            raise ConversionError(f"Basic text extraction not supported for {file_info.file_type.value}")
    
    def _extract_pdf_text_basic(self, file_path: Path) -> str:
        """Basic PDF text extraction avoiding font descriptor issues"""
        try:
            import PyPDF2
            
            text_content = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        # Simple text extraction without font processing
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append(f"## Page {page_num + 1}\n\n{page_text}\n")
                    except Exception as e:
                        # Skip problematic pages
                        self.logger.warning(f"Skipping page {page_num + 1} due to error: {e}")
                        text_content.append(f"## Page {page_num + 1}\n\n[Page could not be processed: {str(e)}]\n")
            
            return "\n".join(text_content)
            
        except ImportError:
            raise ConversionError("PyPDF2 not available for basic PDF text extraction")
    
    def _extract_docx_text_basic(self, file_path: Path) -> str:
        """Basic DOCX text extraction"""
        try:
            import docx
            
            doc = docx.Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            return "\n\n".join(text_content)
            
        except ImportError:
            raise ConversionError("python-docx not available for basic DOCX text extraction")
    
    def _extract_plain_text(self, file_path: Path) -> str:
        """Extract plain text files"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _save_text_as_markdown(self, text: str, output_path: Path, file_info: FileInfo):
        """Save extracted text as markdown with metadata header"""
        header = f"""---
# Basic Text Extraction
- **Source File**: {file_info.name}
- **Extraction Method**: Basic Text Extraction (Fallback)
- **File Type**: {file_info.file_type.value.upper()}
- **Extraction Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Note**: This is a basic text extraction due to primary conversion issues
---

"""
        
        content = header + text
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


class PlainTextFallback(FallbackStrategy):
    """Plain text output when markdown conversion fails"""
    
    def __init__(self):
        super().__init__("plain_text_fallback", FallbackPriority.LOW)
    
    def can_handle(self, file_info: FileInfo, error: Optional[ConversionError] = None) -> bool:
        """Can handle any text-extractable file as last resort"""
        return True
    
    def execute(self, file_info: FileInfo, output_path: Path,
                original_error: Optional[ConversionError] = None) -> ConversionResult:
        """Create plain text file with error information"""
        start_time = time.time()
        
        try:
            # Create informational plain text file
            content = self._create_fallback_content(file_info, original_error)
            
            # Save as .txt instead of .md
            txt_output_path = output_path.with_suffix('.txt')
            
            with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            execution_time = time.time() - start_time
            self._record_success(execution_time)
            
            return ConversionResult(
                file_info=file_info,
                status=ConversionStatus.SUCCESS,
                output_path=txt_output_path,
                conversion_time=execution_time,
                metadata={
                    "fallback_strategy": self.name,
                    "output_type": "plain_text",
                    "original_error": str(original_error) if original_error else None
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_failure(execution_time)
            
            return ConversionResult(
                file_info=file_info,
                status=ConversionStatus.FAILED,
                error_message=f"Plain text fallback failed: {str(e)}",
                conversion_time=execution_time
            )
    
    def _create_fallback_content(self, file_info: FileInfo, original_error: Optional[ConversionError] = None) -> str:
        """Create informational content for failed conversion"""
        content = f"""CONVERSION FAILED - PLAIN TEXT FALLBACK

File Information:
- File Name: {file_info.name}
- File Path: {file_info.path}
- File Size: {file_info.size_formatted}
- File Type: {file_info.file_type.value.upper()}
- Modified: {file_info.modified_time.strftime('%Y-%m-%d %H:%M:%S')}

Conversion Error:
{str(original_error) if original_error else 'Unknown error occurred during conversion'}

Recovery Suggestions:
"""
        
        if original_error and hasattr(original_error, 'recovery_suggestions'):
            for suggestion in original_error.recovery_suggestions:
                content += f"- {suggestion}\n"
        else:
            content += """- Check if the file is corrupted or password protected
- Try converting with alternative tools
- Verify file format is supported
- Contact support if the issue persists
"""
        
        content += f"\nFallback executed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return content


class FallbackManager:
    """Manages fallback strategies for conversion failures"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._strategies: List[FallbackStrategy] = []
        self._register_default_strategies()
        
        # Circuit breaker for fallback strategies
        self._fallback_circuit_breaker = CircuitBreaker("fallback_manager")
    
    def _register_default_strategies(self):
        """Register default fallback strategies"""
        self.register_strategy(BasicTextExtractionStrategy())
        self.register_strategy(PlainTextFallback())
    
    def register_strategy(self, strategy: FallbackStrategy):
        """Register a new fallback strategy"""
        self._strategies.append(strategy)
        self._strategies.sort(key=lambda s: s.priority.value)
        self.logger.info(f"Registered fallback strategy: {strategy.name}")
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """Remove a fallback strategy"""
        for i, strategy in enumerate(self._strategies):
            if strategy.name == strategy_name:
                del self._strategies[i]
                self.logger.info(f"Removed fallback strategy: {strategy_name}")
                return True
        return False
    
    def execute_fallback(self, file_info: FileInfo, output_path: Path,
                        original_error: Optional[ConversionError] = None,
                        max_attempts: int = 3) -> FallbackResult:
        """
        Execute fallback strategies in priority order
        
        Args:
            file_info: File to convert
            output_path: Target output path
            original_error: Original conversion error
            max_attempts: Maximum number of fallback attempts
            
        Returns:
            FallbackResult with execution details
        """
        self.logger.info(f"Starting fallback conversion for {file_info.name}")
        
        # Filter strategies that can handle this file/error
        applicable_strategies = [
            s for s in self._strategies 
            if s.is_enabled() and s.can_handle(file_info, original_error)
        ]
        
        if not applicable_strategies:
            return FallbackResult(
                success=False,
                strategy_name="none",
                error=ConversionError("No applicable fallback strategies found"),
                fallback_level=0
            )
        
        # Try strategies in priority order
        attempts = 0
        for strategy in applicable_strategies[:max_attempts]:
            attempts += 1
            
            try:
                self.logger.info(f"Attempting fallback strategy: {strategy.name}")
                
                # Use circuit breaker for fallback execution
                def execute_strategy():
                    return strategy.execute(file_info, output_path, original_error)
                
                result = self._fallback_circuit_breaker.call(execute_strategy)
                
                if result.status == ConversionStatus.SUCCESS:
                    self.logger.info(f"Fallback strategy '{strategy.name}' succeeded")
                    return FallbackResult(
                        success=True,
                        strategy_name=strategy.name,
                        result=result,
                        execution_time=result.conversion_time,
                        fallback_level=attempts
                    )
                else:
                    self.logger.warning(f"Fallback strategy '{strategy.name}' failed: {result.error_message}")
                    continue
                    
            except Exception as e:
                self.logger.error(f"Fallback strategy '{strategy.name}' threw exception: {e}")
                
                # If this is the last attempt, return the error
                if attempts >= max_attempts or strategy == applicable_strategies[-1]:
                    return FallbackResult(
                        success=False,
                        strategy_name=strategy.name,
                        error=e,
                        fallback_level=attempts
                    )
        
        # All fallback strategies failed
        return FallbackResult(
            success=False,
            strategy_name="all_failed",
            error=ConversionError(f"All {attempts} fallback strategies failed"),
            fallback_level=attempts
        )
    
    def get_strategies(self) -> List[FallbackStrategy]:
        """Get list of registered strategies"""
        return self._strategies.copy()
    
    def get_strategy_by_name(self, name: str) -> Optional[FallbackStrategy]:
        """Get strategy by name"""
        for strategy in self._strategies:
            if strategy.name == name:
                return strategy
        return None
    
    def enable_strategy(self, name: str) -> bool:
        """Enable a specific strategy"""
        strategy = self.get_strategy_by_name(name)
        if strategy:
            strategy.enable()
            self.logger.info(f"Enabled fallback strategy: {name}")
            return True
        return False
    
    def disable_strategy(self, name: str) -> bool:
        """Disable a specific strategy"""
        strategy = self.get_strategy_by_name(name)
        if strategy:
            strategy.disable()
            self.logger.info(f"Disabled fallback strategy: {name}")
            return True
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get fallback manager metrics"""
        strategy_metrics = [strategy.get_metrics() for strategy in self._strategies]
        
        circuit_breaker_metrics = self._fallback_circuit_breaker.get_metrics()
        
        return {
            "total_strategies": len(self._strategies),
            "enabled_strategies": len([s for s in self._strategies if s.is_enabled()]),
            "strategies": strategy_metrics,
            "circuit_breaker": circuit_breaker_metrics
        }