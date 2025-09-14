"""
Performance Monitoring and Validation Script

Comprehensive monitoring script to validate the FontBBox solution implementation,
measure performance, and ensure system health.
"""

import asyncio
import time
import psutil
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import tempfile
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from markitdown_gui.core.conversion_manager import ConversionManager
    from markitdown_gui.core.validators import DocumentValidator, ValidationLevel
    from markitdown_gui.core.error_handling import (
        CircuitBreaker, FallbackManager, ErrorRecoveryManager,
        ErrorReporter, FontDescriptorError
    )
    from markitdown_gui.core.models import FileInfo
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    IMPORTS_AVAILABLE = False


class PerformanceMonitor:
    """Comprehensive performance monitoring for FontBBox solution"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "system_startup": {},
            "validation_performance": {},
            "error_handling_performance": {},
            "conversion_performance": {},
            "memory_usage": {},
            "recovery_performance": {}
        }
        self.test_files = []
        self._setup_test_environment()
    
    def _setup_test_environment(self):
        """Setup test files and environment"""
        print("Setting up test environment...")
        
        # Create test files with various characteristics
        self.test_files = self._create_test_files()
        print(f"Created {len(self.test_files)} test files")
    
    def _create_test_files(self) -> List[Path]:
        """Create test files for performance testing"""
        test_files = []
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="fontbbox_test_"))
        
        # 1. Simple text file
        text_file = self.temp_dir / "simple.txt"
        text_file.write_text("Simple text content for testing conversion performance.")
        test_files.append(text_file)
        
        # 2. Markdown file  
        md_file = self.temp_dir / "test.md"
        md_file.write_text("# Test Markdown\n\nThis is a test **markdown** file.")
        test_files.append(md_file)
        
        # 3. Problematic PDF (simulated)
        pdf_file = self.temp_dir / "problematic.pdf"
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Font << /F1 4 0 R >>
>>
endobj  
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica
   /FontDescriptor 5 0 R
>>
endobj
5 0 obj
<< /Type /FontDescriptor /FontName /Helvetica
   /FontBBox [None None None None]
   /ItalicAngle 0 /Ascent 718 /Descent -207
>>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000224 00000 n
0000000309 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
432
%%EOF"""
        pdf_file.write_bytes(pdf_content)
        test_files.append(pdf_file)
        
        # 4. Large text file
        large_file = self.temp_dir / "large.txt"
        content = "This is a large file for performance testing. " * 1000
        large_file.write_text(content)
        test_files.append(large_file)
        
        return test_files
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance and validation tests"""
        print("Starting comprehensive performance tests...")
        
        if not IMPORTS_AVAILABLE:
            print("Skipping tests due to import issues")
            return {"error": "Required modules not available"}
        
        # Test each component
        await self._test_system_startup()
        await self._test_validation_performance()
        await self._test_error_handling_performance()
        await self._test_conversion_performance()
        await self._test_memory_usage()
        await self._test_recovery_performance()
        
        # Generate comprehensive report
        report = self._generate_performance_report()
        
        print("Performance tests completed!")
        return report
    
    async def _test_system_startup(self):
        """Test system startup performance"""
        print("Testing system startup performance...")
        
        start_time = time.time()
        
        try:
            # Initialize core components
            conversion_manager = ConversionManager(
                output_directory=self.temp_dir / "output",
                enable_recovery=True,
                enable_monitoring=True
            )
            
            validator = DocumentValidator(ValidationLevel.STANDARD)
            circuit_breaker = CircuitBreaker("test_breaker")
            fallback_manager = FallbackManager()
            error_reporter = ErrorReporter()
            
            startup_time = time.time() - start_time
            
            self.metrics["system_startup"] = {
                "startup_time_seconds": startup_time,
                "components_initialized": 5,
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "status": "success"
            }
            
            print(f"System startup: {startup_time:.3f}s")
            
        except Exception as e:
            self.metrics["system_startup"] = {
                "status": "failed",
                "error": str(e),
                "startup_time_seconds": time.time() - start_time
            }
    
    async def _test_validation_performance(self):
        """Test PDF validation performance"""
        print("Testing validation performance...")
        
        try:
            validator = DocumentValidator(ValidationLevel.STANDARD)
            
            validation_times = []
            results = []
            
            for test_file in self.test_files:
                if validator.can_validate(test_file):
                    start_time = time.time()
                    
                    try:
                        result = validator.validate(test_file)
                        validation_time = time.time() - start_time
                        validation_times.append(validation_time)
                        results.append({"file": test_file.name, "valid": result.is_valid, "time": validation_time})
                        
                    except Exception as e:
                        validation_time = time.time() - start_time
                        results.append({"file": test_file.name, "error": str(e), "time": validation_time})
            
            self.metrics["validation_performance"] = {
                "files_tested": len(results),
                "avg_validation_time": statistics.mean(validation_times) if validation_times else 0,
                "max_validation_time": max(validation_times) if validation_times else 0,
                "min_validation_time": min(validation_times) if validation_times else 0,
                "results": results,
                "status": "success"
            }
            
            if validation_times:
                print(f"Validation performance: avg={statistics.mean(validation_times):.3f}s")
            
        except Exception as e:
            self.metrics["validation_performance"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_error_handling_performance(self):
        """Test error handling system performance"""
        print("Testing error handling performance...")
        
        try:
            circuit_breaker = CircuitBreaker("performance_test")
            error_reporter = ErrorReporter()
            
            # Test circuit breaker performance
            cb_times = []
            for i in range(100):
                start_time = time.time()
                result = circuit_breaker.call(lambda: f"success_{i}")
                cb_time = time.time() - start_time
                cb_times.append(cb_time)
                assert result == f"success_{i}"
            
            # Test error reporting performance
            er_times = []
            for i in range(50):
                start_time = time.time()
                error = FontDescriptorError(
                    f"Test FontBBox error {i}",
                    self.test_files[0] if self.test_files else None
                )
                report = error_reporter.report_error(error)
                er_time = time.time() - start_time
                er_times.append(er_time)
            
            self.metrics["error_handling_performance"] = {
                "circuit_breaker": {
                    "avg_call_time": statistics.mean(cb_times),
                    "max_call_time": max(cb_times),
                    "total_calls": len(cb_times),
                    "state": circuit_breaker.state.value
                },
                "error_reporting": {
                    "avg_report_time": statistics.mean(er_times),
                    "max_report_time": max(er_times),
                    "total_reports": len(er_times)
                },
                "status": "success"
            }
            
            print(f"Circuit breaker: avg={statistics.mean(cb_times)*1000:.1f}ms per call")
            print(f"Error reporting: avg={statistics.mean(er_times)*1000:.1f}ms per report")
            
        except Exception as e:
            self.metrics["error_handling_performance"] = {
                "status": "failed", 
                "error": str(e)
            }
    
    async def _test_conversion_performance(self):
        """Test conversion performance with error handling"""
        print("Testing conversion performance...")
        
        try:
            conversion_manager = ConversionManager(
                output_directory=self.temp_dir / "output",
                enable_recovery=True
            )
            
            conversion_times = []
            results = []
            
            for test_file in self.test_files:
                try:
                    file_info = FileInfo.from_path(test_file)
                    
                    start_time = time.time()
                    
                    # Test single file conversion (if available)
                    if hasattr(conversion_manager, 'convert_single_file'):
                        result = conversion_manager.convert_single_file(file_info)
                        conversion_time = time.time() - start_time
                        
                        conversion_times.append(conversion_time)
                        results.append({
                            "file": test_file.name,
                            "status": result.status.value if hasattr(result, 'status') else "unknown",
                            "time": conversion_time,
                            "size_bytes": test_file.stat().st_size
                        })
                    
                except Exception as e:
                    conversion_time = time.time() - start_time
                    results.append({
                        "file": test_file.name,
                        "error": str(e),
                        "time": conversion_time
                    })
            
            self.metrics["conversion_performance"] = {
                "files_processed": len(results),
                "avg_conversion_time": statistics.mean(conversion_times) if conversion_times else 0,
                "max_conversion_time": max(conversion_times) if conversion_times else 0,
                "results": results,
                "status": "success"
            }
            
            if conversion_times:
                print(f"Conversion performance: avg={statistics.mean(conversion_times):.3f}s")
            
        except Exception as e:
            self.metrics["conversion_performance"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_memory_usage(self):
        """Test memory usage under load"""
        print("Testing memory usage...")
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            # Create multiple components to test memory usage
            managers = []
            for i in range(10):
                manager = ConversionManager(
                    output_directory=self.temp_dir / f"output_{i}",
                    enable_recovery=True
                )
                managers.append(manager)
            
            peak_memory = process.memory_info().rss / 1024 / 1024
            
            # Generate error reports to test memory management
            error_reporter = ErrorReporter()
            for i in range(1100):  # More than max_reports
                error = FontDescriptorError(f"Memory test error {i}")
                error_reporter.report_error(error)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            
            self.metrics["memory_usage"] = {
                "initial_memory_mb": initial_memory,
                "peak_memory_mb": peak_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": peak_memory - initial_memory,
                "error_reports_count": len(error_reporter.get_reports()),
                "memory_management": "effective" if len(error_reporter.get_reports()) <= 1000 else "issue",
                "status": "success"
            }
            
            print(f"Memory usage: {initial_memory:.1f}MB → {peak_memory:.1f}MB → {final_memory:.1f}MB")
            
        except Exception as e:
            self.metrics["memory_usage"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_recovery_performance(self):
        """Test error recovery performance"""
        print("Testing error recovery performance...")
        
        try:
            fallback_manager = FallbackManager()
            recovery_manager = ErrorRecoveryManager(fallback_manager)
            
            recovery_times = []
            recovery_results = []
            
            for test_file in self.test_files[:3]:  # Test first 3 files
                try:
                    file_info = FileInfo.from_path(test_file)
                    
                    # Create a test error
                    test_error = FontDescriptorError(
                        "Test FontBBox error for recovery",
                        test_file
                    )
                    
                    start_time = time.time()
                    
                    recovery_result = recovery_manager.recover_from_error(
                        test_error, file_info, self.temp_dir / "recovery_output.md"
                    )
                    
                    recovery_time = time.time() - start_time
                    recovery_times.append(recovery_time)
                    
                    recovery_results.append({
                        "file": test_file.name,
                        "action": recovery_result.action_taken.value,
                        "success": recovery_result.success,
                        "time": recovery_time
                    })
                    
                except Exception as e:
                    recovery_results.append({
                        "file": test_file.name,
                        "error": str(e),
                        "time": time.time() - start_time
                    })
            
            self.metrics["recovery_performance"] = {
                "recovery_attempts": len(recovery_results),
                "avg_recovery_time": statistics.mean(recovery_times) if recovery_times else 0,
                "max_recovery_time": max(recovery_times) if recovery_times else 0,
                "successful_recoveries": len([r for r in recovery_results if r.get("success")]),
                "results": recovery_results,
                "status": "success"
            }
            
            if recovery_times:
                print(f"Recovery performance: avg={statistics.mean(recovery_times):.3f}s")
            
        except Exception as e:
            self.metrics["recovery_performance"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate overall health score
        health_score = 100
        issues = []
        
        # Check startup performance
        startup_time = self.metrics["system_startup"].get("startup_time_seconds", 0)
        if startup_time > 5.0:
            health_score -= 10
            issues.append(f"Slow startup: {startup_time:.1f}s")
        
        # Check validation performance  
        avg_validation = self.metrics["validation_performance"].get("avg_validation_time", 0)
        if avg_validation > 1.0:
            health_score -= 15
            issues.append(f"Slow validation: {avg_validation:.3f}s average")
        
        # Check memory usage
        memory_increase = self.metrics["memory_usage"].get("memory_increase_mb", 0)
        if memory_increase > 100:
            health_score -= 20
            issues.append(f"High memory usage: +{memory_increase:.1f}MB")
        
        # Check error handling
        cb_avg_time = self.metrics["error_handling_performance"].get("circuit_breaker", {}).get("avg_call_time", 0)
        if cb_avg_time > 0.001:  # 1ms
            health_score -= 10
            issues.append(f"Slow circuit breaker: {cb_avg_time*1000:.1f}ms average")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "test_duration_seconds": total_time,
            "overall_health_score": max(0, health_score),
            "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "critical",
            "issues": issues,
            "detailed_metrics": self.metrics,
            "summary": {
                "startup_time": self.metrics["system_startup"].get("startup_time_seconds"),
                "validation_performance": self.metrics["validation_performance"].get("avg_validation_time"),
                "error_handling_performance": self.metrics["error_handling_performance"].get("circuit_breaker", {}).get("avg_call_time"),
                "memory_usage": self.metrics["memory_usage"].get("memory_increase_mb"),
                "recovery_performance": self.metrics["recovery_performance"].get("avg_recovery_time")
            },
            "recommendations": self._generate_recommendations(health_score, issues)
        }
    
    def _generate_recommendations(self, health_score: int, issues: List[str]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if health_score < 50:
            recommendations.append("CRITICAL: System performance is severely degraded")
            recommendations.append("Consider reducing validation level to BASIC for better performance")
            recommendations.append("Disable recovery features temporarily if not needed")
        
        elif health_score < 80:
            recommendations.append("System performance is below optimal")
            recommendations.append("Monitor memory usage and consider increasing available memory")
            recommendations.append("Check for unnecessary background processes")
        
        if "Slow startup" in str(issues):
            recommendations.append("Consider lazy loading of non-critical components")
            recommendations.append("Pre-compile regular expressions used in validation")
        
        if "High memory usage" in str(issues):
            recommendations.append("Implement more aggressive garbage collection")
            recommendations.append("Reduce error report retention count")
        
        if "Slow validation" in str(issues):
            recommendations.append("Use BASIC validation level for better performance")
            recommendations.append("Consider async validation for batch operations")
        
        if not recommendations:
            recommendations.append("System performance is optimal")
            recommendations.append("Continue monitoring for performance regressions")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save performance report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        report_path = Path(filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Performance report saved to: {report_path.absolute()}")
    
    def cleanup(self):
        """Clean up test environment"""
        try:
            import shutil
            if hasattr(self, 'temp_dir') and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up test directory: {self.temp_dir}")
        except Exception as e:
            print(f"Cleanup warning: {e}")


async def main():
    """Main performance monitoring function"""
    print("FontBBox Solution Performance Monitor")
    print("=" * 50)
    
    monitor = PerformanceMonitor()
    
    try:
        # Run comprehensive tests
        report = await monitor.run_comprehensive_tests()
        
        # Display summary
        print("\nPerformance Test Summary:")
        print(f"Overall Health Score: {report['overall_health_score']}/100")
        print(f"Status: {report['status'].upper()}")
        
        if report.get('issues'):
            print("\nIssues Found:")
            for issue in report['issues']:
                print(f"  • {issue}")
        
        if report.get('recommendations'):
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        # Save detailed report
        monitor.save_report(report)
        
        print(f"\nTest completed in {report['test_duration_seconds']:.1f} seconds")
        
    except Exception as e:
        print(f"Performance monitoring failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        monitor.cleanup()


if __name__ == "__main__":
    asyncio.run(main())