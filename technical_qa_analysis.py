#!/usr/bin/env python3
"""
Technical QA Analysis for ConversionManager Path Integration

Static analysis and technical review of the path utility integration
without requiring runtime dependencies.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import ast

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TechnicalQAAnalyzer:
    """Technical QA analyzer for ConversionManager path integration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.passed_checks = []
        
    def analyze_integration(self) -> Dict[str, Any]:
        """Perform comprehensive technical analysis"""
        print("ConversionManager Path Integration - Technical QA Analysis")
        print("="*60)
        
        results = {
            'technical_functionality': self.check_technical_functionality(),
            'performance_requirements': self.check_performance_requirements(),
            'backward_compatibility': self.check_backward_compatibility(),
            'system_integration': self.check_system_integration(),
            'error_handling': self.check_error_handling(),
            'security_considerations': self.check_security_aspects(),
            'code_quality': self.check_code_quality()
        }
        
        # Overall assessment
        results['overall_status'] = self.assess_overall_status(results)
        
        return results
    
    def check_technical_functionality(self) -> Dict[str, Any]:
        """Check technical functionality implementation"""
        print("\n=== Checking Technical Functionality ===")
        
        checks = {
            'path_utility_integration': False,
            'proper_import_statements': False,
            'function_calls_updated': False,
            'parameter_mapping': False,
            'fallback_mechanisms': False
        }
        
        # Read ConversionManager source
        conversion_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'conversion_manager.py'
        if not conversion_manager_path.exists():
            self.issues.append("ConversionManager file not found")
            return {'status': 'FAILED', 'checks': checks, 'issues': ['File not found']}
        
        with open(conversion_manager_path, 'r', encoding='utf-8') as f:
            manager_content = f.read()
        
        # Check 1: Path utility is imported
        if 'from .file_manager import resolve_markdown_output_path' in manager_content:
            checks['proper_import_statements'] = True
            self.passed_checks.append("✓ resolve_markdown_output_path properly imported")
        else:
            self.issues.append("resolve_markdown_output_path not imported")
        
        # Check 2: Function is being called in conversion workflow
        resolve_calls = len(re.findall(r'resolve_markdown_output_path\s*\(', manager_content))
        if resolve_calls >= 3:  # Should be called in multiple places
            checks['function_calls_updated'] = True
            self.passed_checks.append(f"✓ resolve_markdown_output_path called {resolve_calls} times")
        else:
            self.issues.append(f"Insufficient usage of resolve_markdown_output_path: only {resolve_calls} calls found")
        
        # Check 3: Proper parameter mapping
        param_patterns = [
            r'source_path=\s*file_info\.path',
            r'preserve_structure=',
            r'output_base_dir=',
            r'ensure_unique='
        ]
        
        matched_patterns = 0
        for pattern in param_patterns:
            if re.search(pattern, manager_content):
                matched_patterns += 1
        
        if matched_patterns >= 3:
            checks['parameter_mapping'] = True
            self.passed_checks.append(f"✓ Parameter mapping implemented ({matched_patterns}/4 patterns found)")
        else:
            self.issues.append(f"Incomplete parameter mapping: only {matched_patterns}/4 patterns found")
        
        # Check 4: Fallback to legacy system exists
        if 'create_markdown_output_path' in manager_content and 'except' in manager_content:
            checks['fallback_mechanisms'] = True
            self.passed_checks.append("✓ Fallback to legacy path system implemented")
        else:
            self.issues.append("Fallback mechanism to legacy path system not found")
        
        # Check 5: Path utility integration in key methods
        key_methods = ['_convert_single_file', 'prepare_files_for_conversion', '_get_conflict_resolution_info']
        integration_count = 0
        
        for method in key_methods:
            method_pattern = rf'def {method}\(.*?\):'
            method_match = re.search(method_pattern, manager_content, re.DOTALL)
            if method_match:
                method_start = method_match.start()
                # Find the end of the method (next def or class)
                next_def = re.search(r'\n    def ', manager_content[method_start + 1:])
                next_class = re.search(r'\nclass ', manager_content[method_start + 1:])
                
                method_end = len(manager_content)
                if next_def:
                    method_end = min(method_end, method_start + 1 + next_def.start())
                if next_class:
                    method_end = min(method_end, method_start + 1 + next_class.start())
                
                method_content = manager_content[method_start:method_end]
                if 'resolve_markdown_output_path' in method_content:
                    integration_count += 1
        
        if integration_count >= 2:
            checks['path_utility_integration'] = True
            self.passed_checks.append(f"✓ Path utility integrated in {integration_count} key methods")
        else:
            self.issues.append(f"Insufficient integration: only {integration_count} key methods use new utility")
        
        status = 'PASSED' if all(checks.values()) else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks + self.issues}
    
    def check_performance_requirements(self) -> Dict[str, Any]:
        """Check performance requirements"""
        print("\n=== Checking Performance Requirements ===")
        
        checks = {
            'efficient_path_operations': False,
            'minimal_filesystem_access': False,
            'batch_processing_support': False,
            'memory_optimization': False
        }
        
        # Read path utility source
        file_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'file_manager.py'
        if not file_manager_path.exists():
            return {'status': 'FAILED', 'checks': checks, 'issues': ['file_manager.py not found']}
        
        with open(file_manager_path, 'r', encoding='utf-8') as f:
            file_manager_content = f.read()
        
        # Check 1: Efficient pathlib usage
        if 'pathlib' in file_manager_content and '.resolve()' in file_manager_content:
            checks['efficient_path_operations'] = True
            self.passed_checks.append("✓ Efficient pathlib operations used")
        
        # Check 2: Minimal filesystem access patterns
        if 'mkdir(parents=True, exist_ok=True)' in file_manager_content:
            checks['minimal_filesystem_access'] = True
            self.passed_checks.append("✓ Efficient directory creation patterns")
        
        # Check 3: Batch processing support
        conversion_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'conversion_manager.py'
        with open(conversion_manager_path, 'r', encoding='utf-8') as f:
            manager_content = f.read()
        
        if 'prepare_files_for_conversion' in manager_content and 'for file_info in files:' in manager_content:
            checks['batch_processing_support'] = True
            self.passed_checks.append("✓ Batch processing support implemented")
        
        # Check 4: Memory optimization considerations
        if 'memory_optimizer' in manager_content or 'MemoryOptimizer' in manager_content:
            checks['memory_optimization'] = True
            self.passed_checks.append("✓ Memory optimization integrated")
        
        status = 'PASSED' if sum(checks.values()) >= 3 else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks}
    
    def check_backward_compatibility(self) -> Dict[str, Any]:
        """Check backward compatibility"""
        print("\n=== Checking Backward Compatibility ===")
        
        checks = {
            'legacy_import_preserved': False,
            'existing_interfaces_maintained': False,
            'configuration_compatibility': False,
            'gradual_migration_support': False
        }
        
        conversion_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'conversion_manager.py'
        with open(conversion_manager_path, 'r', encoding='utf-8') as f:
            manager_content = f.read()
        
        # Check 1: Legacy import still available
        if 'create_markdown_output_path' in manager_content:
            checks['legacy_import_preserved'] = True
            self.passed_checks.append("✓ Legacy path function still imported for fallback")
        
        # Check 2: Existing method signatures maintained
        method_signatures = [
            'def convert_files_async(self, files: List[FileInfo])',
            'def prepare_files_for_conversion(self, files: List[FileInfo])',
            'def set_output_directory(self, directory: Path)'
        ]
        
        maintained_signatures = 0
        for sig in method_signatures:
            if sig.replace(' ', '') in manager_content.replace(' ', '').replace('\n', ''):
                maintained_signatures += 1
        
        if maintained_signatures >= 2:
            checks['existing_interfaces_maintained'] = True
            self.passed_checks.append(f"✓ {maintained_signatures}/3 key method signatures maintained")
        
        # Check 3: Configuration compatibility
        if 'save_to_original_dir' in manager_content and 'output_directory' in manager_content:
            checks['configuration_compatibility'] = True
            self.passed_checks.append("✓ Existing configuration options preserved")
        
        # Check 4: Gradual migration support (fallback mechanisms)
        if 'except' in manager_content and 'create_markdown_output_path' in manager_content:
            checks['gradual_migration_support'] = True
            self.passed_checks.append("✓ Fallback mechanisms enable gradual migration")
        
        status = 'PASSED' if all(checks.values()) else 'PARTIALLY_PASSED' if sum(checks.values()) >= 3 else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks}
    
    def check_system_integration(self) -> Dict[str, Any]:
        """Check system integration quality"""
        print("\n=== Checking System Integration ===")
        
        checks = {
            'proper_module_coupling': False,
            'signal_handling_updated': False,
            'conflict_resolution_integration': False,
            'logging_integration': False
        }
        
        conversion_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'conversion_manager.py'
        with open(conversion_manager_path, 'r', encoding='utf-8') as f:
            manager_content = f.read()
        
        # Check 1: Proper module coupling
        if 'from .file_manager import resolve_markdown_output_path' in manager_content:
            checks['proper_module_coupling'] = True
            self.passed_checks.append("✓ Proper module coupling implemented")
        
        # Check 2: Signal handling integration
        if 'pyqtSignal' in manager_content and 'file_conversion' in manager_content:
            checks['signal_handling_updated'] = True
            self.passed_checks.append("✓ Signal handling system maintained")
        
        # Check 3: Conflict resolution integration
        if 'FileConflictHandler' in manager_content and 'conflict_info' in manager_content:
            checks['conflict_resolution_integration'] = True
            self.passed_checks.append("✓ Conflict resolution system integrated")
        
        # Check 4: Logging integration
        if 'logger.debug' in manager_content and 'resolve_markdown_output_path' in manager_content:
            checks['logging_integration'] = True
            self.passed_checks.append("✓ Logging integration for new path system")
        
        status = 'PASSED' if all(checks.values()) else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks}
    
    def check_error_handling(self) -> Dict[str, Any]:
        """Check error handling and edge cases"""
        print("\n=== Checking Error Handling ===")
        
        checks = {
            'exception_handling': False,
            'fallback_on_error': False,
            'graceful_degradation': False,
            'error_reporting': False
        }
        
        conversion_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'conversion_manager.py'
        with open(conversion_manager_path, 'r', encoding='utf-8') as f:
            manager_content = f.read()
        
        # Check 1: Exception handling around new path calls
        try_except_patterns = re.findall(r'try:(.*?)except.*?:', manager_content, re.DOTALL)
        path_related_exceptions = 0
        
        for pattern in try_except_patterns:
            if 'resolve_markdown_output_path' in pattern:
                path_related_exceptions += 1
        
        if path_related_exceptions >= 2:
            checks['exception_handling'] = True
            self.passed_checks.append(f"✓ Exception handling around path operations ({path_related_exceptions} try-except blocks)")
        
        # Check 2: Fallback on error
        if 'create_markdown_output_path' in manager_content and 'except' in manager_content:
            checks['fallback_on_error'] = True
            self.passed_checks.append("✓ Fallback mechanism on path resolution errors")
        
        # Check 3: Graceful degradation
        if 'logger.error' in manager_content and 'ValueError' in manager_content and 'OSError' in manager_content:
            checks['graceful_degradation'] = True
            self.passed_checks.append("✓ Graceful degradation with appropriate error handling")
        
        # Check 4: Error reporting
        if 'error_message' in manager_content and 'ConversionResult' in manager_content:
            checks['error_reporting'] = True
            self.passed_checks.append("✓ Error reporting integrated")
        
        status = 'PASSED' if sum(checks.values()) >= 3 else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks}
    
    def check_security_aspects(self) -> Dict[str, Any]:
        """Check security aspects of the integration"""
        print("\n=== Checking Security Aspects ===")
        
        checks = {
            'path_sanitization': False,
            'directory_traversal_prevention': False,
            'permission_validation': False,
            'secure_defaults': False
        }
        
        # Check path utility security features
        file_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'file_manager.py'
        with open(file_manager_path, 'r', encoding='utf-8') as f:
            file_manager_content = f.read()
        
        # Check 1: Path sanitization
        if 'sanitize_filename' in file_manager_content:
            checks['path_sanitization'] = True
            self.passed_checks.append("✓ Path sanitization implemented")
        
        # Check 2: Directory traversal prevention
        if 'relative_to' in file_manager_content and 'security' in file_manager_content.lower():
            checks['directory_traversal_prevention'] = True
            self.passed_checks.append("✓ Directory traversal prevention implemented")
        
        # Check 3: Permission validation
        if 'os.access' in file_manager_content or 'W_OK' in file_manager_content:
            checks['permission_validation'] = True
            self.passed_checks.append("✓ Permission validation implemented")
        
        # Check 4: Secure defaults
        if 'resolve()' in file_manager_content and 'absolute' in file_manager_content:
            checks['secure_defaults'] = True
            self.passed_checks.append("✓ Secure defaults (absolute paths) enforced")
        
        status = 'PASSED' if all(checks.values()) else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks}
    
    def check_code_quality(self) -> Dict[str, Any]:
        """Check code quality aspects"""
        print("\n=== Checking Code Quality ===")
        
        checks = {
            'documentation_quality': False,
            'type_annotations': False,
            'code_organization': False,
            'testing_considerations': False
        }
        
        file_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'file_manager.py'
        with open(file_manager_path, 'r', encoding='utf-8') as f:
            file_manager_content = f.read()
        
        conversion_manager_path = self.project_root / 'markitdown_gui' / 'core' / 'conversion_manager.py'
        with open(conversion_manager_path, 'r', encoding='utf-8') as f:
            manager_content = f.read()
        
        # Check 1: Documentation quality
        docstring_count = len(re.findall(r'""".*?"""', file_manager_content, re.DOTALL))
        if docstring_count >= 2:  # Function should have comprehensive docstring
            checks['documentation_quality'] = True
            self.passed_checks.append(f"✓ Good documentation quality ({docstring_count} docstrings in path utility)")
        
        # Check 2: Type annotations
        if 'Path,' in file_manager_content and '-> Path:' in file_manager_content:
            checks['type_annotations'] = True
            self.passed_checks.append("✓ Type annotations present")
        
        # Check 3: Code organization
        if 'def resolve_markdown_output_path' in file_manager_content and len(file_manager_content.split('\n')) < 1000:
            checks['code_organization'] = True
            self.passed_checks.append("✓ Good code organization and modularity")
        
        # Check 4: Testing considerations
        if 'Examples:' in file_manager_content or 'Test' in manager_content:
            checks['testing_considerations'] = True
            self.passed_checks.append("✓ Testing considerations included")
        
        status = 'PASSED' if sum(checks.values()) >= 3 else 'FAILED'
        return {'status': status, 'checks': checks, 'details': self.passed_checks}
    
    def assess_overall_status(self, results: Dict[str, Any]) -> str:
        """Assess overall status based on all checks"""
        print("\n=== Overall Assessment ===")
        
        critical_areas = ['technical_functionality', 'performance_requirements', 'system_integration']
        critical_passed = sum(1 for area in critical_areas if results[area]['status'] == 'PASSED')
        
        other_areas = ['backward_compatibility', 'error_handling', 'security_considerations', 'code_quality']
        other_passed = sum(1 for area in other_areas if results[area]['status'] in ['PASSED', 'PARTIALLY_PASSED'])
        
        total_score = (critical_passed * 2) + other_passed  # Weight critical areas more
        max_score = len(critical_areas) * 2 + len(other_areas)
        
        score_percentage = (total_score / max_score) * 100
        
        if score_percentage >= 90:
            return 'APPROVED'
        elif score_percentage >= 75:
            return 'APPROVED_WITH_MINOR_ISSUES'
        elif score_percentage >= 60:
            return 'NEEDS_IMPROVEMENT'
        else:
            return 'FAILED'
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive technical QA report"""
        report = []
        report.append("TECHNICAL QA REPORT - ConversionManager Path Integration")
        report.append("=" * 60)
        
        # Executive Summary
        report.append("\nEXECUTIVE SUMMARY")
        report.append("-" * 20)
        report.append(f"Overall Status: {results['overall_status']}")
        
        # Detailed Results
        report.append("\nDETAILED RESULTS")
        report.append("-" * 20)
        
        for area, result in results.items():
            if area != 'overall_status':
                report.append(f"\n{area.replace('_', ' ').title()}: {result['status']}")
                if 'checks' in result:
                    passed_checks = sum(result['checks'].values())
                    total_checks = len(result['checks'])
                    report.append(f"  Passed: {passed_checks}/{total_checks} checks")
        
        # Issues Found
        if self.issues:
            report.append("\nISSUES IDENTIFIED")
            report.append("-" * 20)
            for issue in self.issues:
                report.append(f"  • {issue}")
        
        # Successful Checks
        if self.passed_checks:
            report.append("\nSUCCESSFUL VALIDATIONS")
            report.append("-" * 20)
            for check in self.passed_checks:
                report.append(f"  {check}")
        
        # Recommendations
        report.append("\nRECOMMENDATIONS")
        report.append("-" * 20)
        
        if results['overall_status'] == 'APPROVED':
            report.append("  ✅ Implementation meets all technical requirements")
            report.append("  ✅ Ready for production deployment")
        elif results['overall_status'] == 'APPROVED_WITH_MINOR_ISSUES':
            report.append("  ⚠️  Implementation is acceptable with minor improvements needed")
            report.append("  ⚠️  Address identified issues in next iteration")
        else:
            report.append("  ❌ Implementation needs significant improvement")
            report.append("  ❌ Address all critical issues before deployment")
        
        return "\n".join(report)


def main():
    """Run technical QA analysis"""
    analyzer = TechnicalQAAnalyzer()
    results = analyzer.analyze_integration()
    
    # Generate and print report
    report = analyzer.generate_report(results)
    print(report)
    
    # Return exit code based on status
    if results['overall_status'] in ['APPROVED', 'APPROVED_WITH_MINOR_ISSUES']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())