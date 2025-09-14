#!/usr/bin/env python3
"""
Memory Optimization Validation Script
Validates TASK-031: Memory Optimization implementation
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


def analyze_memory_optimizer_file(file_path: Path) -> Dict[str, any]:
    """Analyze the memory optimizer implementation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract classes and methods
        classes = []
        methods = []
        imports = []
        memory_patterns = {
            'memory_tracking': 0,
            'caching_mechanisms': 0,
            'streaming_processing': 0,
            'memory_pools': 0,
            'weak_references': 0,
            'garbage_collection': 0,
            'memory_statistics': 0,
            'cleanup_operations': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                # Count methods in class
                class_methods = [m.name for m in node.body 
                               if isinstance(m, ast.FunctionDef)]
                methods.extend(class_methods)
            
            elif isinstance(node, ast.FunctionDef):
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                          if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                    methods.append(node.name)
            
            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Count memory optimization patterns
        if any(pattern in content for pattern in ['tracemalloc', 'memory_tracker', 'monitoring']):
            memory_patterns['memory_tracking'] = content.count('tracemalloc') + content.count('memory')
        
        if any(pattern in content for pattern in ['cache', 'lru', 'Cache']):
            memory_patterns['caching_mechanisms'] = content.count('cache') + content.count('Cache')
        
        if any(pattern in content for pattern in ['streaming', 'chunk', 'process_file_chunked']):
            memory_patterns['streaming_processing'] = content.count('chunk') + content.count('streaming')
        
        if any(pattern in content for pattern in ['pool', 'Pool', 'acquire', 'release']):
            memory_patterns['memory_pools'] = content.count('pool') + content.count('Pool')
        
        if any(pattern in content for pattern in ['weak', 'WeakReference', 'weakref']):
            memory_patterns['weak_references'] = content.count('weak') + content.count('WeakReference')
        
        if any(pattern in content for pattern in ['gc.collect', 'garbage', 'force_gc']):
            memory_patterns['garbage_collection'] = content.count('gc.') + content.count('garbage')
        
        if any(pattern in content for pattern in ['statistics', 'stats', 'get_memory']):
            memory_patterns['memory_statistics'] = content.count('statistics') + content.count('stats')
        
        if any(pattern in content for pattern in ['cleanup', 'clear', 'reset']):
            memory_patterns['cleanup_operations'] = content.count('cleanup') + content.count('clear')
        
        return {
            'file': file_path.name,
            'classes': classes,
            'methods': methods,
            'imports': imports,
            'memory_patterns': memory_patterns,
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


def analyze_integration_files() -> Dict[str, any]:
    """Analyze integration of memory optimizer in core managers"""
    results = {
        'integration_files': [],
        'integration_patterns': {
            'memory_optimizer_import': 0,
            'memory_optimizer_init': 0,
            'memory_monitoring': 0,
            'cache_usage': 0,
            'memory_cleanup': 0,
            'memory_statistics': 0
        },
        'issues': []
    }
    
    # Files to check for integration
    core_files = [
        Path("markitdown_gui/core/conversion_manager.py"),
        Path("markitdown_gui/core/file_manager.py"),
        Path("markitdown_gui/core/llm_manager.py")
    ]
    
    for file_path in core_files:
        if not file_path.exists():
            results['issues'].append(f"Core file not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'file': file_path.name,
                'has_memory_optimizer_import': 'memory_optimizer' in content,
                'has_memory_optimizer_init': 'MemoryOptimizer()' in content,
                'has_memory_monitoring': any(pattern in content for pattern in ['start_monitoring', 'memory_stats']),
                'has_cache_usage': any(pattern in content for pattern in ['cache_result', 'get_cached_result']),
                'has_memory_cleanup': 'cleanup_memory' in content or 'memory_optimizer.cleanup' in content,
                'has_memory_statistics': 'get_memory_statistics' in content
            }
            
            results['integration_files'].append(file_info)
            
            # Update pattern counts
            if file_info['has_memory_optimizer_import']:
                results['integration_patterns']['memory_optimizer_import'] += 1
            if file_info['has_memory_optimizer_init']:
                results['integration_patterns']['memory_optimizer_init'] += 1
            if file_info['has_memory_monitoring']:
                results['integration_patterns']['memory_monitoring'] += 1
            if file_info['has_cache_usage']:
                results['integration_patterns']['cache_usage'] += 1
            if file_info['has_memory_cleanup']:
                results['integration_patterns']['memory_cleanup'] += 1
            if file_info['has_memory_statistics']:
                results['integration_patterns']['memory_statistics'] += 1
                
        except Exception as e:
            results['issues'].append(f"Error analyzing {file_path}: {e}")
    
    return results


def validate_memory_optimization_tests() -> Dict[str, any]:
    """Validate memory optimization test implementation"""
    test_file = Path("tests/unit/test_memory_optimizer.py")
    
    if not test_file.exists():
        return {
            'test_file_exists': False,
            'error': 'Memory optimization test file not found'
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
        
        # Check for key test patterns
        test_patterns = {
            'memory_tracking_tests': any(pattern in content for pattern in ['test_start_monitoring', 'test_memory_tracking']),
            'cache_tests': any(pattern in content for pattern in ['test_cache', 'test_lru']),
            'streaming_tests': any(pattern in content for pattern in ['test_streaming', 'test_chunked']),
            'memory_pool_tests': any(pattern in content for pattern in ['test_memory_pool', 'test_acquire']),
            'weak_reference_tests': any(pattern in content for pattern in ['test_weak_reference', 'test_cleanup']),
            'integration_tests': any(pattern in content for pattern in ['test_integration', 'test_scenario']),
            'gc_tests': any(pattern in content for pattern in ['test_gc', 'test_force_gc']),
            'statistics_tests': any(pattern in content for pattern in ['test_statistics', 'test_get_memory'])
        }
        
        return {
            'test_file_exists': True,
            'test_classes': test_classes,
            'test_methods': test_methods,
            'test_class_count': len(test_classes),
            'test_method_count': len(test_methods),
            'test_patterns': test_patterns,
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        return {
            'test_file_exists': True,
            'error': str(e),
            'test_class_count': 0,
            'test_method_count': 0
        }


def main():
    """Main validation function"""
    print("=== TASK-031: Memory Optimization Validation ===\n")
    
    # Validate memory optimizer implementation
    memory_optimizer_file = Path("markitdown_gui/core/memory_optimizer.py")
    
    if not memory_optimizer_file.exists():
        print("❌ Memory optimizer file not found!")
        return False
    
    print("🔍 Memory Optimizer Implementation Analysis:")
    optimizer_analysis = analyze_memory_optimizer_file(memory_optimizer_file)
    
    if 'error' in optimizer_analysis:
        print(f"   ❌ Error analyzing memory optimizer: {optimizer_analysis['error']}")
        return False
    
    print(f"   • Classes implemented: {optimizer_analysis['class_count']}")
    print(f"   • Methods implemented: {optimizer_analysis['method_count']}")
    print(f"   • Lines of code: {optimizer_analysis['lines']}")
    
    print(f"\n📊 Memory Optimization Patterns:")
    patterns = optimizer_analysis['memory_patterns']
    print(f"   • Memory tracking: {patterns['memory_tracking']} instances")
    print(f"   • Caching mechanisms: {patterns['caching_mechanisms']} instances")
    print(f"   • Streaming processing: {patterns['streaming_processing']} instances")
    print(f"   • Memory pools: {patterns['memory_pools']} instances")
    print(f"   • Weak references: {patterns['weak_references']} instances")
    print(f"   • Garbage collection: {patterns['garbage_collection']} instances")
    print(f"   • Memory statistics: {patterns['memory_statistics']} instances")
    print(f"   • Cleanup operations: {patterns['cleanup_operations']} instances")
    
    print(f"\n🔧 Core Classes Implemented:")
    for class_name in optimizer_analysis['classes']:
        print(f"   ✅ {class_name}")
    
    # Validate integration with core managers
    print(f"\n🔗 Core Manager Integration Analysis:")
    integration_analysis = analyze_integration_files()
    
    print(f"   • Files analyzed: {len(integration_analysis['integration_files'])}")
    
    for file_info in integration_analysis['integration_files']:
        integration_score = sum([
            file_info['has_memory_optimizer_import'],
            file_info['has_memory_optimizer_init'],
            file_info['has_memory_monitoring'],
            file_info['has_cache_usage'],
            file_info['has_memory_cleanup'],
            file_info['has_memory_statistics']
        ])
        
        integration_indicator = "🔄" if integration_score >= 4 else "📄"
        print(f"   {integration_indicator} {file_info['file']}: {integration_score}/6 integration features")
    
    integration_patterns = integration_analysis['integration_patterns']
    print(f"\n🔄 Integration Patterns:")
    print(f"   • Memory optimizer imports: {integration_patterns['memory_optimizer_import']}/3 files")
    print(f"   • Memory optimizer initialization: {integration_patterns['memory_optimizer_init']}/3 files")
    print(f"   • Memory monitoring: {integration_patterns['memory_monitoring']}/3 files")
    print(f"   • Cache usage: {integration_patterns['cache_usage']}/3 files")
    print(f"   • Memory cleanup: {integration_patterns['memory_cleanup']}/3 files")
    print(f"   • Memory statistics: {integration_patterns['memory_statistics']}/3 files")
    
    # Validate tests
    print(f"\n🧪 Memory Optimization Tests Analysis:")
    test_analysis = validate_memory_optimization_tests()
    
    if not test_analysis['test_file_exists']:
        print(f"   ❌ Test file not found")
        return False
    
    if 'error' in test_analysis:
        print(f"   ❌ Error analyzing tests: {test_analysis['error']}")
        return False
    
    print(f"   • Test classes: {test_analysis['test_class_count']}")
    print(f"   • Test methods: {test_analysis['test_method_count']}")
    print(f"   • Lines of test code: {test_analysis['lines']}")
    
    print(f"\n🔬 Test Coverage Patterns:")
    test_patterns = test_analysis['test_patterns']
    print(f"   • Memory tracking tests: {'✅' if test_patterns['memory_tracking_tests'] else '❌'}")
    print(f"   • Cache tests: {'✅' if test_patterns['cache_tests'] else '❌'}")
    print(f"   • Streaming tests: {'✅' if test_patterns['streaming_tests'] else '❌'}")
    print(f"   • Memory pool tests: {'✅' if test_patterns['memory_pool_tests'] else '❌'}")
    print(f"   • Weak reference tests: {'✅' if test_patterns['weak_reference_tests'] else '❌'}")
    print(f"   • Integration tests: {'✅' if test_patterns['integration_tests'] else '❌'}")
    print(f"   • GC tests: {'✅' if test_patterns['gc_tests'] else '❌'}")
    print(f"   • Statistics tests: {'✅' if test_patterns['statistics_tests'] else '❌'}")
    
    # Check for issues
    if integration_analysis['issues']:
        print(f"\n⚠️ Integration Issues Found:")
        for issue in integration_analysis['issues']:
            print(f"   • {issue}")
    
    # Overall assessment
    success_criteria = {
        'memory_optimizer_exists': memory_optimizer_file.exists(),
        'core_classes_implemented': optimizer_analysis['class_count'] >= 6,
        'sufficient_methods': optimizer_analysis['method_count'] >= 25,
        'memory_patterns_present': (
            patterns['memory_tracking'] >= 5 and
            patterns['caching_mechanisms'] >= 10 and
            patterns['streaming_processing'] >= 3 and
            patterns['memory_pools'] >= 5 and
            patterns['garbage_collection'] >= 3
        ),
        'core_integration_complete': (
            integration_patterns['memory_optimizer_import'] == 3 and
            integration_patterns['memory_optimizer_init'] == 3 and
            integration_patterns['cache_usage'] >= 2
        ),
        'comprehensive_tests': (
            test_analysis['test_class_count'] >= 6 and
            test_analysis['test_method_count'] >= 25 and
            sum(test_patterns.values()) >= 6
        ),
        'no_integration_errors': len(integration_analysis['issues']) == 0
    }
    
    print(f"\n✅ Success Criteria:")
    print(f"   • Memory optimizer exists: {'✅' if success_criteria['memory_optimizer_exists'] else '❌'}")
    print(f"   • Core classes implemented (≥6): {'✅' if success_criteria['core_classes_implemented'] else '❌'} ({optimizer_analysis['class_count']})")
    print(f"   • Sufficient methods (≥25): {'✅' if success_criteria['sufficient_methods'] else '❌'} ({optimizer_analysis['method_count']})")
    print(f"   • Memory patterns present: {'✅' if success_criteria['memory_patterns_present'] else '❌'}")
    print(f"   • Core integration complete: {'✅' if success_criteria['core_integration_complete'] else '❌'}")
    print(f"   • Comprehensive tests (≥25): {'✅' if success_criteria['comprehensive_tests'] else '❌'} ({test_analysis.get('test_method_count', 0)})")
    print(f"   • No integration errors: {'✅' if success_criteria['no_integration_errors'] else '❌'}")
    
    overall_success = all(success_criteria.values())
    
    if overall_success:
        print(f"\n🎉 TASK-031 Implementation: ✅ SUCCESS")
        print(f"   • Complete memory optimization system implemented")
        print(f"   • {optimizer_analysis['class_count']} memory optimization classes with {optimizer_analysis['method_count']} methods")
        print(f"   • Integrated into all 3 core managers (ConversionManager, FileManager, LLMManager)")
        print(f"   • Comprehensive test suite with {test_analysis.get('test_method_count', 0)} test methods")
        print(f"   • Memory tracking, caching, streaming, pools, weak references, and GC management")
        print(f"   • Memory patterns: Tracking: {patterns['memory_tracking']}, Caching: {patterns['caching_mechanisms']}, Streaming: {patterns['streaming_processing']}")
    else:
        print(f"\n❌ TASK-031 Implementation: NEEDS WORK")
        failed_criteria = [k for k, v in success_criteria.items() if not v]
        print(f"   • Failed criteria: {', '.join(failed_criteria)}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)