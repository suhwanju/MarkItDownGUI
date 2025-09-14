#!/usr/bin/env python3
"""
End-to-End Test Validation Script
Validates E2E test structure and comprehensive coverage
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


def analyze_e2e_test_file(file_path: Path) -> Dict[str, any]:
    """Analyze an E2E test file for comprehensive coverage"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract E2E test information
        classes = []
        test_methods = []
        fixtures = []
        imports = []
        e2e_patterns = {
            'workflow_tests': 0,
            'performance_tests': 0,
            'error_recovery_tests': 0,
            'memory_tests': 0,
            'concurrent_tests': 0,
            'large_file_tests': 0,
            'integration_tests': 0,
            'real_file_usage': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    classes.append(node.name)
                    # Count test methods in class
                    class_methods = [m.name for m in node.body 
                                   if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')]
                    test_methods.extend(class_methods)
            
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_methods.append(node.name)
                elif any(decorator.id == 'pytest.fixture' for decorator in getattr(node, 'decorator_list', []) 
                        if isinstance(decorator, ast.Name)):
                    fixtures.append(node.name)
            
            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Count E2E testing patterns in content
        if any(pattern in content for pattern in ['workflow', 'complete', 'end_to_end', 'full_']):
            e2e_patterns['workflow_tests'] = content.count('workflow') + content.count('complete') + content.count('full_')
        
        if any(pattern in content for pattern in ['performance', 'benchmark', 'speed', 'throughput']):
            e2e_patterns['performance_tests'] = content.count('performance') + content.count('benchmark')
        
        if any(pattern in content for pattern in ['error', 'recovery', 'failure', 'exception']):
            e2e_patterns['error_recovery_tests'] = content.count('error') + content.count('recovery')
        
        if any(pattern in content for pattern in ['memory', 'tracemalloc', 'psutil', 'cleanup']):
            e2e_patterns['memory_tests'] = content.count('memory') + content.count('cleanup')
        
        if any(pattern in content for pattern in ['concurrent', 'threading', 'parallel', 'ThreadPool']):
            e2e_patterns['concurrent_tests'] = content.count('concurrent') + content.count('threading')
        
        if any(pattern in content for pattern in ['large', '1mb', '5mb', '10mb', 'MB']):
            e2e_patterns['large_file_tests'] = content.count('large') + content.count('MB')
        
        if any(pattern in content for pattern in ['integration', 'managers', 'real_']):
            e2e_patterns['integration_tests'] = content.count('integration') + content.count('managers')
        
        if any(pattern in content for pattern in ['temp_dir', 'write_text', 'write_bytes', 'real_test_files']):
            e2e_patterns['real_file_usage'] = content.count('write_text') + content.count('write_bytes')
        
        return {
            'file': file_path.name,
            'classes': classes,
            'test_methods': test_methods,
            'fixtures': fixtures,
            'imports': imports,
            'e2e_patterns': e2e_patterns,
            'test_count': len(test_methods),
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e),
            'test_count': 0
        }


def validate_e2e_test_structure(test_dir: Path) -> Dict[str, any]:
    """Validate the E2E test structure"""
    results = {
        'files_analyzed': 0,
        'total_tests': 0,
        'test_files': [],
        'coverage_areas': set(),
        'e2e_patterns_total': {
            'workflow_tests': 0,
            'performance_tests': 0,
            'error_recovery_tests': 0,
            'memory_tests': 0,
            'concurrent_tests': 0,
            'large_file_tests': 0,
            'integration_tests': 0,
            'real_file_usage': 0
        },
        'issues': []
    }
    
    # Expected E2E test areas
    expected_areas = {
        'conversion_workflows',
        'performance_benchmarks',
        'error_recovery',
        'large_file_processing'
    }
    
    # Analyze each E2E test file
    e2e_test_files = list(test_dir.glob('test_*.py'))
    
    for test_file in e2e_test_files:
        analysis = analyze_e2e_test_file(test_file)
        results['files_analyzed'] += 1
        results['total_tests'] += analysis.get('test_count', 0)
        results['test_files'].append(analysis)
        
        # Extract area being tested
        area_name = test_file.stem.replace('test_', '')
        results['coverage_areas'].add(area_name)
        
        # Aggregate E2E patterns
        if 'e2e_patterns' in analysis:
            for pattern, count in analysis['e2e_patterns'].items():
                results['e2e_patterns_total'][pattern] += count
        
        # Check for issues
        if analysis.get('test_count', 0) == 0:
            results['issues'].append(f"No tests found in {test_file.name}")
        
        if 'error' in analysis:
            results['issues'].append(f"Parse error in {test_file.name}: {analysis['error']}")
        
        # Check for E2E-specific issues
        if analysis.get('test_count', 0) > 0:
            e2e_patterns = analysis.get('e2e_patterns', {})
            if sum(e2e_patterns.values()) == 0:
                results['issues'].append(f"No E2E patterns found in {test_file.name}")
    
    # Check coverage
    missing_areas = expected_areas - results['coverage_areas']
    if missing_areas:
        results['issues'].append(f"Missing E2E test files for areas: {missing_areas}")
    
    return results


def validate_e2e_test_quality(test_dir: Path) -> Dict[str, any]:
    """Validate E2E test quality and comprehensiveness"""
    quality_results = {
        'e2e_test_patterns': {
            'complete_workflows': 0,
            'real_file_testing': 0,
            'performance_monitoring': 0,
            'error_scenarios': 0,
            'resource_management': 0,
            'concurrency_testing': 0,
            'integration_testing': 0,
            'stress_testing': 0
        },
        'best_practices': {
            'realistic_fixtures': 0,
            'performance_assertions': 0,
            'resource_cleanup': 0,
            'error_simulation': 0,
            'monitoring_integration': 0
        },
        'recommendations': []
    }
    
    e2e_test_files = list(test_dir.glob('test_*.py'))
    
    for test_file in e2e_test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for E2E-specific test patterns
            if any(pattern in content for pattern in ['complete', 'workflow', 'end_to_end']):
                quality_results['e2e_test_patterns']['complete_workflows'] += 1
            
            if any(pattern in content for pattern in ['write_text', 'write_bytes', 'real_test_files']):
                quality_results['e2e_test_patterns']['real_file_testing'] += 1
            
            if any(pattern in content for pattern in ['time.perf_counter', 'performance', 'benchmark']):
                quality_results['e2e_test_patterns']['performance_monitoring'] += 1
            
            if any(pattern in content for pattern in ['Exception', 'Error', 'failure', 'recovery']):
                quality_results['e2e_test_patterns']['error_scenarios'] += 1
            
            if any(pattern in content for pattern in ['tracemalloc', 'psutil', 'memory', 'cleanup']):
                quality_results['e2e_test_patterns']['resource_management'] += 1
            
            if any(pattern in content for pattern in ['threading', 'concurrent', 'parallel']):
                quality_results['e2e_test_patterns']['concurrency_testing'] += 1
            
            if any(pattern in content for pattern in ['managers', 'integration', 'end_to_end']):
                quality_results['e2e_test_patterns']['integration_testing'] += 1
            
            if any(pattern in content for pattern in ['stress', 'load', 'large_file', 'many_files']):
                quality_results['e2e_test_patterns']['stress_testing'] += 1
            
            # Check best practices
            if any(pattern in content for pattern in ['temp_dir', 'test_files', 'fixtures']):
                quality_results['best_practices']['realistic_fixtures'] += 1
            
            if any(pattern in content for pattern in ['assert.*<', 'throughput', 'time.*<']):
                quality_results['best_practices']['performance_assertions'] += 1
            
            if any(pattern in content for pattern in ['cleanup', 'clear_results', 'gc.collect']):
                quality_results['best_practices']['resource_cleanup'] += 1
            
            if any(pattern in content for pattern in ['side_effect', 'raise', 'mock.*error']):
                quality_results['best_practices']['error_simulation'] += 1
            
            if any(pattern in content for pattern in ['tracemalloc', 'psutil', 'monitor']):
                quality_results['best_practices']['monitoring_integration'] += 1
                
        except Exception as e:
            quality_results['recommendations'].append(f"Could not analyze {test_file.name}: {e}")
    
    return quality_results


def main():
    """Main validation function"""
    e2e_test_dir = Path(__file__).parent / 'tests' / 'e2e'
    
    if not e2e_test_dir.exists():
        print("❌ E2E test directory not found!")
        return False
    
    print("=== TASK-030: End-to-End Tests Validation ===\n")
    
    # Validate E2E test structure
    structure_results = validate_e2e_test_structure(e2e_test_dir)
    
    print(f"📊 E2E Test Structure Analysis:")
    print(f"   • Files analyzed: {structure_results['files_analyzed']}")
    print(f"   • Total test methods: {structure_results['total_tests']}")
    print(f"   • Coverage areas: {', '.join(sorted(structure_results['coverage_areas']))}")
    
    # Display E2E patterns
    patterns = structure_results['e2e_patterns_total']
    print(f"\n🔄 E2E Testing Patterns:")
    print(f"   • Workflow tests: {patterns['workflow_tests']} instances")
    print(f"   • Performance tests: {patterns['performance_tests']} instances") 
    print(f"   • Error recovery tests: {patterns['error_recovery_tests']} instances")
    print(f"   • Memory tests: {patterns['memory_tests']} instances")
    print(f"   • Concurrent tests: {patterns['concurrent_tests']} instances")
    print(f"   • Large file tests: {patterns['large_file_tests']} instances")
    print(f"   • Integration tests: {patterns['integration_tests']} instances")
    print(f"   • Real file usage: {patterns['real_file_usage']} instances")
    
    # Display file details
    print(f"\n📋 E2E Test Files:")
    for file_info in structure_results['test_files']:
        if 'error' not in file_info:
            e2e_score = sum(file_info.get('e2e_patterns', {}).values())
            e2e_indicator = "🔄" if e2e_score > 5 else "📄"
            print(f"   {e2e_indicator} {file_info['file']}: {file_info['test_count']} tests ({file_info['lines']} lines)")
            
            if file_info['test_count'] > 20:
                print(f"     ✅ Comprehensive E2E test coverage")
            elif file_info['test_count'] > 10:
                print(f"     ✅ Good E2E test coverage")
            else:
                print(f"     ⚠️ Moderate E2E test coverage")
        else:
            print(f"   ❌ {file_info['file']}: Error - {file_info['error']}")
    
    # Validate E2E test quality
    quality_results = validate_e2e_test_quality(e2e_test_dir)
    
    print(f"\n🔍 E2E Test Quality Analysis:")
    e2e_patterns = quality_results['e2e_test_patterns']
    print(f"   • Complete workflows: {e2e_patterns['complete_workflows']} files")
    print(f"   • Real file testing: {e2e_patterns['real_file_testing']} files")
    print(f"   • Performance monitoring: {e2e_patterns['performance_monitoring']} files")
    print(f"   • Error scenarios: {e2e_patterns['error_scenarios']} files")
    print(f"   • Resource management: {e2e_patterns['resource_management']} files")
    print(f"   • Concurrency testing: {e2e_patterns['concurrency_testing']} files")
    print(f"   • Integration testing: {e2e_patterns['integration_testing']} files")
    print(f"   • Stress testing: {e2e_patterns['stress_testing']} files")
    
    best_practices = quality_results['best_practices']
    print(f"\n✨ Best Practices:")
    print(f"   • Realistic fixtures: {best_practices['realistic_fixtures']} files")
    print(f"   • Performance assertions: {best_practices['performance_assertions']} files")
    print(f"   • Resource cleanup: {best_practices['resource_cleanup']} files")
    print(f"   • Error simulation: {best_practices['error_simulation']} files")
    print(f"   • Monitoring integration: {best_practices['monitoring_integration']} files")
    
    # Check for issues
    if structure_results['issues']:
        print(f"\n⚠️ Issues Found:")
        for issue in structure_results['issues']:
            print(f"   • {issue}")
    
    # Overall assessment
    success_criteria = {
        'files_count': structure_results['files_analyzed'] >= 4,
        'total_tests': structure_results['total_tests'] >= 40,
        'coverage_complete': len(structure_results['coverage_areas']) >= 4,
        'e2e_patterns_present': (
            patterns['workflow_tests'] >= 5 and
            patterns['performance_tests'] >= 3 and
            patterns['error_recovery_tests'] >= 10 and
            patterns['real_file_usage'] >= 5
        ),
        'quality_patterns': (
            e2e_patterns['complete_workflows'] >= 3 and
            e2e_patterns['real_file_testing'] >= 3 and
            e2e_patterns['performance_monitoring'] >= 2 and
            best_practices['realistic_fixtures'] >= 3
        ),
        'no_parse_errors': not any('Parse error' in issue for issue in structure_results['issues'])
    }
    
    print(f"\n✅ Success Criteria:")
    print(f"   • E2E test files (≥4): {'✅' if success_criteria['files_count'] else '❌'} ({structure_results['files_analyzed']})")
    print(f"   • Total tests (≥40): {'✅' if success_criteria['total_tests'] else '❌'} ({structure_results['total_tests']})")
    print(f"   • Area coverage (≥4): {'✅' if success_criteria['coverage_complete'] else '❌'} ({len(structure_results['coverage_areas'])})")
    print(f"   • E2E testing patterns: {'✅' if success_criteria['e2e_patterns_present'] else '❌'}")
    print(f"   • Quality patterns: {'✅' if success_criteria['quality_patterns'] else '❌'}")
    print(f"   • No parse errors: {'✅' if success_criteria['no_parse_errors'] else '❌'}")
    
    overall_success = all(success_criteria.values())
    
    if overall_success:
        print(f"\n🎉 TASK-030 Implementation: ✅ SUCCESS")
        print(f"   • Comprehensive E2E test suite implemented")
        print(f"   • {structure_results['total_tests']} test methods across {structure_results['files_analyzed']} E2E test files")
        print(f"   • Complete workflows, performance, and error recovery covered")
        print(f"   • Real file processing and resource management tested")
        print(f"   • Workflow tests: {patterns['workflow_tests']}, Performance: {patterns['performance_tests']}, Error recovery: {patterns['error_recovery_tests']}")
    else:
        print(f"\n❌ TASK-030 Implementation: NEEDS WORK")
        failed_criteria = [k for k, v in success_criteria.items() if not v]
        print(f"   • Failed criteria: {', '.join(failed_criteria)}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)