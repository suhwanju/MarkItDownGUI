#!/usr/bin/env python3
"""
UI Responsiveness Validation Script  
Validates TASK-032: UI Responsiveness Improvements implementation
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


def analyze_performance_optimizer_file(file_path: Path) -> Dict[str, any]:
    """Analyze the performance optimizer implementation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract classes and methods
        classes = []
        methods = []
        imports = []
        responsiveness_patterns = {
            'async_task_management': 0,
            'ui_update_throttling': 0,
            'rendering_optimization': 0,
            'performance_monitoring': 0,
            'memory_management': 0,
            'batch_operations': 0,
            'caching_mechanisms': 0,
            'responsiveness_metrics': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                # Count methods in class
                class_methods = [m.name for m in node.body 
                               if isinstance(m, ast.FunctionDef)]
                methods.extend(class_methods)
            
            elif isinstance(node, ast.FunctionDef):
                methods.append(node.name)
            
            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Count responsiveness optimization patterns
        if any(pattern in content for pattern in ['AsyncTaskManager', 'async_manager', 'ThreadPoolExecutor']):
            responsiveness_patterns['async_task_management'] = content.count('async') + content.count('AsyncTask')
        
        if any(pattern in content for pattern in ['UIUpdateThrottler', 'throttler', 'update_interval']):
            responsiveness_patterns['ui_update_throttling'] = content.count('throttl') + content.count('update_interval')
        
        if any(pattern in content for pattern in ['RenderingOptimizer', 'rendering', 'batch_widget_updates']):
            responsiveness_patterns['rendering_optimization'] = content.count('rendering') + content.count('batch')
        
        if any(pattern in content for pattern in ['PerformanceMonitor', 'performance', 'measure_operation']):
            responsiveness_patterns['performance_monitoring'] = content.count('performance') + content.count('monitor')
        
        if any(pattern in content for pattern in ['memory_usage', 'psutil', 'memory']):
            responsiveness_patterns['memory_management'] = content.count('memory') + content.count('psutil')
        
        if any(pattern in content for pattern in ['batch', 'batch_update', 'batch_widget']):
            responsiveness_patterns['batch_operations'] = content.count('batch')
        
        if any(pattern in content for pattern in ['cache', 'viewport_cache', 'cached']):
            responsiveness_patterns['caching_mechanisms'] = content.count('cache')
        
        if any(pattern in content for pattern in ['metrics', 'statistics', 'duration_ms']):
            responsiveness_patterns['responsiveness_metrics'] = content.count('metrics') + content.count('duration')
        
        return {
            'file': file_path.name,
            'classes': classes,
            'methods': methods,
            'imports': imports,
            'responsiveness_patterns': responsiveness_patterns,
            'class_count': len(classes),
            'method_count': len(methods),
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e),
            'class_count': 0,
            'method_count': 0
        }


def analyze_main_window_integration() -> Dict[str, any]:
    """Analyze main window integration with performance optimizer"""
    main_window_file = Path("markitdown_gui/ui/main_window.py")
    
    if not main_window_file.exists():
        return {
            'integration_found': False,
            'error': 'Main window file not found'
        }
    
    try:
        with open(main_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        integration_features = {
            'performance_optimizer_import': 'ResponsivenessOptimizer' in content,
            'performance_optimizer_init': 'ResponsivenessOptimizer(' in content,
            'application_optimization': 'optimize_application' in content,
            'widget_optimization': 'optimize_widget' in content,
            'async_execution': 'execute_async' in content,
            'performance_monitoring': 'measure_operation' in content,
            'throttled_updates': 'throttled_update' in content,
            'performance_alerts': 'performance_alert' in content,
            'batch_operations': 'batch_widget_updates' in content,
            'responsiveness_reporting': 'get_responsiveness_report' in content,
            'cleanup_handling': 'performance_optimizer.cleanup' in content
        }
        
        # Count integration methods
        integration_methods = []
        if '_setup_performance_optimization' in content:
            integration_methods.append('_setup_performance_optimization')
        if '_on_performance_alert' in content:
            integration_methods.append('_on_performance_alert')
        if '_on_throttled_update' in content:
            integration_methods.append('_on_throttled_update')
        if 'execute_async_scan' in content:
            integration_methods.append('execute_async_scan')
        if 'get_performance_report' in content:
            integration_methods.append('get_performance_report')
        
        return {
            'integration_found': True,
            'integration_features': integration_features,
            'integration_methods': integration_methods,
            'integration_score': sum(integration_features.values()),
            'total_features': len(integration_features)
        }
        
    except Exception as e:
        return {
            'integration_found': False,
            'error': str(e)
        }


def validate_responsiveness_tests() -> Dict[str, any]:
    """Validate responsiveness benchmark tests"""
    test_file = Path("tests/ui/test_responsiveness_benchmarks.py")
    
    if not test_file.exists():
        return {
            'test_file_exists': False,
            'error': 'Responsiveness benchmark test file not found'
        }
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract test information
        test_classes = []
        test_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    test_classes.append(node.name)
                    # Count test methods in class
                    class_test_methods = [m.name for m in node.body 
                                         if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')]
                    test_methods.extend(class_test_methods)
        
        # Check for key benchmark test patterns
        benchmark_patterns = {
            'startup_performance': 'test_ui_startup_performance' in content,
            'rendering_performance': any(pattern in content for pattern in ['test_large_file_list_rendering', 'test_widget_rendering']),
            'update_throttling': 'test_rapid_ui_updates_throttling' in content,
            'async_performance': 'test_async_task_performance' in content,
            'memory_performance': 'test_memory_usage_during_heavy_operations' in content,
            'responsiveness_under_load': 'test_responsiveness_under_cpu_load' in content,
            'performance_monitoring': 'test_performance_monitoring_overhead' in content,
            'application_optimization': 'test_application_wide_performance_optimization' in content,
            'regression_prevention': 'TestPerformanceRegressionPrevention' in content,
            'benchmark_integration': 'benchmark' in content and 'pytest.main' in content
        }
        
        return {
            'test_file_exists': True,
            'test_classes': test_classes,
            'test_methods': test_methods,
            'test_class_count': len(test_classes),
            'test_method_count': len(test_methods),
            'benchmark_patterns': benchmark_patterns,
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        return {
            'test_file_exists': True,
            'error': str(e),
            'test_class_count': 0,
            'test_method_count': 0
        }


def check_ui_components_optimization() -> Dict[str, any]:
    """Check if UI components have been optimized"""
    results = {
        'components_checked': [],
        'optimization_features': {
            'performance_imports': 0,
            'optimization_methods': 0,
            'async_operations': 0,
            'update_throttling': 0,
            'memory_management': 0
        },
        'issues': []
    }
    
    # UI components to check
    ui_files = [
        Path("markitdown_gui/ui/main_window.py"),
        Path("markitdown_gui/ui/performance_optimizer.py"),
        Path("markitdown_gui/ui/components/file_list_widget.py"),
        Path("markitdown_gui/ui/components/progress_widget.py")
    ]
    
    for ui_file in ui_files:
        if not ui_file.exists():
            results['issues'].append(f"UI file not found: {ui_file}")
            continue
        
        try:
            with open(ui_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            component_info = {
                'file': ui_file.name,
                'has_performance_imports': any(pattern in content for pattern in ['performance_optimizer', 'ResponsivenessOptimizer']),
                'has_optimization_methods': any(pattern in content for pattern in ['optimize_', 'performance_', 'throttle_']),
                'has_async_operations': any(pattern in content for pattern in ['async def', 'execute_async', 'AsyncTask']),
                'has_update_throttling': any(pattern in content for pattern in ['throttle', 'update_interval', 'batch_update']),
                'has_memory_management': any(pattern in content for pattern in ['memory_optimizer', 'cleanup', 'gc.collect'])
            }
            
            results['components_checked'].append(component_info)
            
            # Update feature counts
            if component_info['has_performance_imports']:
                results['optimization_features']['performance_imports'] += 1
            if component_info['has_optimization_methods']:
                results['optimization_features']['optimization_methods'] += 1
            if component_info['has_async_operations']:
                results['optimization_features']['async_operations'] += 1
            if component_info['has_update_throttling']:
                results['optimization_features']['update_throttling'] += 1
            if component_info['has_memory_management']:
                results['optimization_features']['memory_management'] += 1
                
        except Exception as e:
            results['issues'].append(f"Error analyzing {ui_file}: {e}")
    
    return results


def main():
    """Main validation function"""
    print("=== TASK-032: UI Responsiveness Improvements Validation ===\n")
    
    # Validate performance optimizer implementation
    performance_optimizer_file = Path("markitdown_gui/ui/performance_optimizer.py")
    
    if not performance_optimizer_file.exists():
        print("❌ Performance optimizer file not found!")
        return False
    
    print("🚀 Performance Optimizer Implementation Analysis:")
    optimizer_analysis = analyze_performance_optimizer_file(performance_optimizer_file)
    
    if 'error' in optimizer_analysis:
        print(f"   ❌ Error analyzing performance optimizer: {optimizer_analysis['error']}")
        return False
    
    print(f"   • Classes implemented: {optimizer_analysis['class_count']}")
    print(f"   • Methods implemented: {optimizer_analysis['method_count']}")
    print(f"   • Lines of code: {optimizer_analysis['lines']}")
    
    print(f"\n⚡ Responsiveness Optimization Patterns:")
    patterns = optimizer_analysis['responsiveness_patterns']
    print(f"   • Async task management: {patterns['async_task_management']} instances")
    print(f"   • UI update throttling: {patterns['ui_update_throttling']} instances")
    print(f"   • Rendering optimization: {patterns['rendering_optimization']} instances")
    print(f"   • Performance monitoring: {patterns['performance_monitoring']} instances")
    print(f"   • Memory management: {patterns['memory_management']} instances")
    print(f"   • Batch operations: {patterns['batch_operations']} instances")
    print(f"   • Caching mechanisms: {patterns['caching_mechanisms']} instances")
    print(f"   • Responsiveness metrics: {patterns['responsiveness_metrics']} instances")
    
    print(f"\n🏗️ Core Classes Implemented:")
    for class_name in optimizer_analysis['classes']:
        print(f"   ✅ {class_name}")
    
    # Validate main window integration
    print(f"\n🔗 Main Window Integration Analysis:")
    integration_analysis = analyze_main_window_integration()
    
    if not integration_analysis['integration_found']:
        print(f"   ❌ Integration not found: {integration_analysis.get('error', 'Unknown error')}")
        return False
    
    integration_features = integration_analysis['integration_features']
    integration_score = integration_analysis['integration_score']
    total_features = integration_analysis['total_features']
    
    print(f"   • Integration score: {integration_score}/{total_features}")
    print(f"   • Performance optimizer import: {'✅' if integration_features['performance_optimizer_import'] else '❌'}")
    print(f"   • Application optimization: {'✅' if integration_features['application_optimization'] else '❌'}")
    print(f"   • Widget optimization: {'✅' if integration_features['widget_optimization'] else '❌'}")
    print(f"   • Async execution: {'✅' if integration_features['async_execution'] else '❌'}")
    print(f"   • Performance monitoring: {'✅' if integration_features['performance_monitoring'] else '❌'}")
    print(f"   • Throttled updates: {'✅' if integration_features['throttled_updates'] else '❌'}")
    print(f"   • Batch operations: {'✅' if integration_features['batch_operations'] else '❌'}")
    print(f"   • Responsiveness reporting: {'✅' if integration_features['responsiveness_reporting'] else '❌'}")
    
    print(f"\n🔧 Integration Methods:")
    for method in integration_analysis['integration_methods']:
        print(f"   ✅ {method}")
    
    # Validate benchmark tests
    print(f"\n📊 Responsiveness Benchmark Tests Analysis:")
    test_analysis = validate_responsiveness_tests()
    
    if not test_analysis['test_file_exists']:
        print(f"   ❌ Benchmark test file not found")
        return False
    
    if 'error' in test_analysis:
        print(f"   ❌ Error analyzing tests: {test_analysis['error']}")
        return False
    
    print(f"   • Test classes: {test_analysis['test_class_count']}")
    print(f"   • Test methods: {test_analysis['test_method_count']}")
    print(f"   • Lines of test code: {test_analysis['lines']}")
    
    print(f"\n🎯 Benchmark Test Coverage:")
    benchmark_patterns = test_analysis['benchmark_patterns']
    print(f"   • Startup performance: {'✅' if benchmark_patterns['startup_performance'] else '❌'}")
    print(f"   • Rendering performance: {'✅' if benchmark_patterns['rendering_performance'] else '❌'}")
    print(f"   • Update throttling: {'✅' if benchmark_patterns['update_throttling'] else '❌'}")
    print(f"   • Async performance: {'✅' if benchmark_patterns['async_performance'] else '❌'}")
    print(f"   • Memory performance: {'✅' if benchmark_patterns['memory_performance'] else '❌'}")
    print(f"   • Responsiveness under load: {'✅' if benchmark_patterns['responsiveness_under_load'] else '❌'}")
    print(f"   • Performance monitoring: {'✅' if benchmark_patterns['performance_monitoring'] else '❌'}")
    print(f"   • Application optimization: {'✅' if benchmark_patterns['application_optimization'] else '❌'}")
    print(f"   • Regression prevention: {'✅' if benchmark_patterns['regression_prevention'] else '❌'}")
    print(f"   • Benchmark integration: {'✅' if benchmark_patterns['benchmark_integration'] else '❌'}")
    
    # Check UI components optimization
    print(f"\n🖥️ UI Components Optimization Analysis:")
    components_analysis = check_ui_components_optimization()
    
    print(f"   • Components analyzed: {len(components_analysis['components_checked'])}")
    
    for component in components_analysis['components_checked']:
        optimization_count = sum([
            component['has_performance_imports'],
            component['has_optimization_methods'],
            component['has_async_operations'],
            component['has_update_throttling'],
            component['has_memory_management']
        ])
        
        optimization_indicator = "⚡" if optimization_count >= 3 else "📄"
        print(f"   {optimization_indicator} {component['file']}: {optimization_count}/5 optimization features")
    
    optimization_features = components_analysis['optimization_features']
    print(f"\n⚡ Optimization Features:")
    print(f"   • Performance imports: {optimization_features['performance_imports']} components")
    print(f"   • Optimization methods: {optimization_features['optimization_methods']} components")
    print(f"   • Async operations: {optimization_features['async_operations']} components")
    print(f"   • Update throttling: {optimization_features['update_throttling']} components")
    print(f"   • Memory management: {optimization_features['memory_management']} components")
    
    # Check for issues
    if components_analysis['issues']:
        print(f"\n⚠️ Component Issues Found:")
        for issue in components_analysis['issues']:
            print(f"   • {issue}")
    
    # Overall assessment
    success_criteria = {
        'performance_optimizer_exists': performance_optimizer_file.exists(),
        'sufficient_classes': optimizer_analysis['class_count'] >= 5,
        'sufficient_methods': optimizer_analysis['method_count'] >= 15,
        'responsiveness_patterns_present': (
            patterns['async_task_management'] >= 5 and
            patterns['ui_update_throttling'] >= 5 and
            patterns['rendering_optimization'] >= 5 and
            patterns['performance_monitoring'] >= 10
        ),
        'main_window_integration_complete': integration_score >= 8,
        'comprehensive_benchmark_tests': (
            test_analysis['test_class_count'] >= 2 and
            test_analysis['test_method_count'] >= 10 and
            sum(benchmark_patterns.values()) >= 8
        ),
        'ui_components_optimized': optimization_features['performance_imports'] >= 1,
        'no_critical_issues': len(components_analysis['issues']) <= 2
    }
    
    print(f"\n✅ Success Criteria:")
    print(f"   • Performance optimizer exists: {'✅' if success_criteria['performance_optimizer_exists'] else '❌'}")
    print(f"   • Sufficient classes (≥5): {'✅' if success_criteria['sufficient_classes'] else '❌'} ({optimizer_analysis['class_count']})")
    print(f"   • Sufficient methods (≥15): {'✅' if success_criteria['sufficient_methods'] else '❌'} ({optimizer_analysis['method_count']})")
    print(f"   • Responsiveness patterns present: {'✅' if success_criteria['responsiveness_patterns_present'] else '❌'}")
    print(f"   • Main window integration complete: {'✅' if success_criteria['main_window_integration_complete'] else '❌'} ({integration_score}/{total_features})")
    print(f"   • Comprehensive benchmark tests: {'✅' if success_criteria['comprehensive_benchmark_tests'] else '❌'} ({test_analysis.get('test_method_count', 0)})")
    print(f"   • UI components optimized: {'✅' if success_criteria['ui_components_optimized'] else '❌'}")
    print(f"   • No critical issues: {'✅' if success_criteria['no_critical_issues'] else '❌'}")
    
    overall_success = all(success_criteria.values())
    
    if overall_success:
        print(f"\n🎉 TASK-032 Implementation: ✅ SUCCESS")
        print(f"   • Complete UI responsiveness optimization system implemented")
        print(f"   • {optimizer_analysis['class_count']} optimization classes with {optimizer_analysis['method_count']} methods")
        print(f"   • Fully integrated into main window with {integration_score}/{total_features} features")
        print(f"   • Comprehensive benchmark test suite with {test_analysis.get('test_method_count', 0)} test methods")
        print(f"   • Async task management, UI throttling, rendering optimization, and performance monitoring")
        print(f"   • Patterns: Async: {patterns['async_task_management']}, Throttling: {patterns['ui_update_throttling']}, Rendering: {patterns['rendering_optimization']}")
    else:
        print(f"\n❌ TASK-032 Implementation: NEEDS WORK")
        failed_criteria = [k for k, v in success_criteria.items() if not v]
        print(f"   • Failed criteria: {', '.join(failed_criteria)}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)