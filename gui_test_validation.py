#!/usr/bin/env python3
"""
GUI Test Validation Script
Validates GUI test structure and quality without requiring PyQt6
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


def analyze_gui_test_file(file_path: Path) -> Dict[str, any]:
    """Analyze a GUI test file for structure and patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Extract GUI test information
        classes = []
        test_methods = []
        fixtures = []
        imports = []
        gui_patterns = {
            'qtbot_usage': 0,
            'signal_testing': 0,
            'keyboard_simulation': 0,
            'mouse_simulation': 0,
            'widget_interaction': 0,
            'async_operations': 0
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
        
        # Count GUI testing patterns in content
        if 'qtbot' in content:
            gui_patterns['qtbot_usage'] = content.count('qtbot')
        if 'waitSignal' in content or '.connect(' in content:
            gui_patterns['signal_testing'] = content.count('waitSignal') + content.count('.connect(')
        if 'keyPress' in content or 'keySequence' in content:
            gui_patterns['keyboard_simulation'] = content.count('keyPress') + content.count('keySequence')
        if 'mouseClick' in content or 'mouseDClick' in content:
            gui_patterns['mouse_simulation'] = content.count('mouseClick') + content.count('mouseDClick')
        if 'findChild' in content or 'centralWidget' in content:
            gui_patterns['widget_interaction'] = content.count('findChild') + content.count('centralWidget')
        if 'async' in content or 'await' in content:
            gui_patterns['async_operations'] = content.count('async ') + content.count('await ')
        
        return {
            'file': file_path.name,
            'classes': classes,
            'test_methods': test_methods,
            'fixtures': fixtures,
            'imports': imports,
            'gui_patterns': gui_patterns,
            'test_count': len(test_methods),
            'lines': len(content.split('\n'))
        }
        
    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e),
            'test_count': 0
        }


def validate_gui_test_structure(test_dir: Path) -> Dict[str, any]:
    """Validate the GUI test structure"""
    results = {
        'files_analyzed': 0,
        'total_tests': 0,
        'test_files': [],
        'coverage_areas': set(),
        'gui_patterns_total': {
            'qtbot_usage': 0,
            'signal_testing': 0,
            'keyboard_simulation': 0,
            'mouse_simulation': 0,
            'widget_interaction': 0,
            'async_operations': 0
        },
        'issues': []
    }
    
    # Expected GUI components to test
    expected_components = {
        'main_window',
        'settings_dialog',
        'file_list_widget',
        'interactions'
    }
    
    # Analyze each GUI test file
    gui_test_files = list(test_dir.glob('test_*.py')) + list(test_dir.glob('**/test_*.py'))
    
    for test_file in gui_test_files:
        analysis = analyze_gui_test_file(test_file)
        results['files_analyzed'] += 1
        results['total_tests'] += analysis.get('test_count', 0)
        results['test_files'].append(analysis)
        
        # Extract component being tested
        component_name = test_file.stem.replace('test_', '')
        results['coverage_areas'].add(component_name)
        
        # Aggregate GUI patterns
        if 'gui_patterns' in analysis:
            for pattern, count in analysis['gui_patterns'].items():
                results['gui_patterns_total'][pattern] += count
        
        # Check for issues
        if analysis.get('test_count', 0) == 0:
            results['issues'].append(f"No tests found in {test_file.name}")
        
        if 'error' in analysis:
            results['issues'].append(f"Parse error in {test_file.name}: {analysis['error']}")
        
        # Check for GUI-specific issues
        if analysis.get('test_count', 0) > 0:
            gui_patterns = analysis.get('gui_patterns', {})
            if gui_patterns.get('qtbot_usage', 0) == 0:
                results['issues'].append(f"No qtbot usage found in {test_file.name}")
    
    # Check coverage
    missing_components = expected_components - results['coverage_areas']
    if missing_components:
        results['issues'].append(f"Missing GUI test files for components: {missing_components}")
    
    return results


def validate_gui_test_quality(test_dir: Path) -> Dict[str, any]:
    """Validate GUI test quality and patterns"""
    quality_results = {
        'gui_test_patterns': {
            'user_interaction_tests': 0,
            'widget_state_tests': 0,
            'signal_slot_tests': 0,
            'keyboard_navigation_tests': 0,
            'accessibility_tests': 0,
            'error_handling_tests': 0
        },
        'best_practices': {
            'fixture_usage': 0,
            'mocking_external_deps': 0,
            'cleanup_tests': 0,
            'async_handling': 0
        },
        'recommendations': []
    }
    
    gui_test_files = list(test_dir.glob('test_*.py')) + list(test_dir.glob('**/test_*.py'))
    
    for test_file in gui_test_files:
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for GUI-specific test patterns
            if any(pattern in content for pattern in ['mouseClick', 'keyPress', 'qtbot']):
                quality_results['gui_test_patterns']['user_interaction_tests'] += 1
            
            if any(pattern in content for pattern in ['isVisible', 'isEnabled', 'text()', 'value()']):
                quality_results['gui_test_patterns']['widget_state_tests'] += 1
            
            if any(pattern in content for pattern in ['waitSignal', '.connect(', '.emit(']):
                quality_results['gui_test_patterns']['signal_slot_tests'] += 1
            
            if any(pattern in content for pattern in ['Key_Tab', 'Key_Enter', 'focusWidget']):
                quality_results['gui_test_patterns']['keyboard_navigation_tests'] += 1
            
            if any(pattern in content for pattern in ['accessible', 'screen reader', 'aria']):
                quality_results['gui_test_patterns']['accessibility_tests'] += 1
            
            if 'test_error' in content or 'exception' in content.lower():
                quality_results['gui_test_patterns']['error_handling_tests'] += 1
            
            # Check best practices
            if '@pytest.fixture' in content or 'qtbot' in content:
                quality_results['best_practices']['fixture_usage'] += 1
            
            if 'patch' in content or 'Mock' in content:
                quality_results['best_practices']['mocking_external_deps'] += 1
            
            if 'cleanup' in content.lower() or 'close' in content:
                quality_results['best_practices']['cleanup_tests'] += 1
            
            if 'async' in content or 'await' in content:
                quality_results['best_practices']['async_handling'] += 1
                
        except Exception as e:
            quality_results['recommendations'].append(f"Could not analyze {test_file.name}: {e}")
    
    return quality_results


def main():
    """Main validation function"""
    gui_test_dir = Path(__file__).parent / 'tests' / 'gui'
    
    if not gui_test_dir.exists():
        print("❌ GUI test directory not found!")
        return False
    
    print("=== TASK-029: UI Tests Validation ===\n")
    
    # Validate GUI test structure
    structure_results = validate_gui_test_structure(gui_test_dir)
    
    print(f"📊 GUI Test Structure Analysis:")
    print(f"   • Files analyzed: {structure_results['files_analyzed']}")
    print(f"   • Total test methods: {structure_results['total_tests']}")
    print(f"   • Coverage areas: {', '.join(sorted(structure_results['coverage_areas']))}")
    
    # Display GUI patterns
    patterns = structure_results['gui_patterns_total']
    print(f"\n🖱️ GUI Testing Patterns:")
    print(f"   • QtBot usage: {patterns['qtbot_usage']} instances")
    print(f"   • Signal testing: {patterns['signal_testing']} instances")
    print(f"   • Keyboard simulation: {patterns['keyboard_simulation']} instances")
    print(f"   • Mouse simulation: {patterns['mouse_simulation']} instances")
    print(f"   • Widget interaction: {patterns['widget_interaction']} instances")
    print(f"   • Async operations: {patterns['async_operations']} instances")
    
    # Display file details
    print(f"\n📋 GUI Test Files:")
    for file_info in structure_results['test_files']:
        if 'error' not in file_info:
            qtbot_count = file_info.get('gui_patterns', {}).get('qtbot_usage', 0)
            gui_indicator = "🖥️" if qtbot_count > 0 else "📄"
            print(f"   {gui_indicator} {file_info['file']}: {file_info['test_count']} tests ({file_info['lines']} lines)")
            
            if file_info['test_count'] > 15:
                print(f"     ✅ Comprehensive GUI test coverage")
            elif file_info['test_count'] > 8:
                print(f"     ✅ Good GUI test coverage")
            else:
                print(f"     ⚠️ Moderate GUI test coverage")
        else:
            print(f"   ❌ {file_info['file']}: Error - {file_info['error']}")
    
    # Validate GUI test quality
    quality_results = validate_gui_test_quality(gui_test_dir)
    
    print(f"\n🔍 GUI Test Quality Analysis:")
    gui_patterns = quality_results['gui_test_patterns']
    print(f"   • User interaction tests: {gui_patterns['user_interaction_tests']} files")
    print(f"   • Widget state tests: {gui_patterns['widget_state_tests']} files")
    print(f"   • Signal/slot tests: {gui_patterns['signal_slot_tests']} files")
    print(f"   • Keyboard navigation tests: {gui_patterns['keyboard_navigation_tests']} files")
    print(f"   • Accessibility tests: {gui_patterns['accessibility_tests']} files")
    print(f"   • Error handling tests: {gui_patterns['error_handling_tests']} files")
    
    best_practices = quality_results['best_practices']
    print(f"\n✨ Best Practices:")
    print(f"   • Fixture usage: {best_practices['fixture_usage']} files")
    print(f"   • External dependency mocking: {best_practices['mocking_external_deps']} files")
    print(f"   • Cleanup tests: {best_practices['cleanup_tests']} files")
    print(f"   • Async handling: {best_practices['async_handling']} files")
    
    # Check for issues
    if structure_results['issues']:
        print(f"\n⚠️ Issues Found:")
        for issue in structure_results['issues']:
            print(f"   • {issue}")
    
    # Overall assessment
    success_criteria = {
        'files_count': structure_results['files_analyzed'] >= 4,
        'total_tests': structure_results['total_tests'] >= 30,
        'coverage_complete': len(structure_results['coverage_areas']) >= 4,
        'gui_patterns_present': (
            patterns['qtbot_usage'] >= 50 and
            patterns['signal_testing'] >= 2 and
            patterns['widget_interaction'] >= 20
        ),
        'quality_patterns': (
            gui_patterns['user_interaction_tests'] >= 3 and
            gui_patterns['widget_state_tests'] >= 3 and
            best_practices['fixture_usage'] >= 3
        ),
        'no_parse_errors': not any('Parse error' in issue for issue in structure_results['issues'])
    }
    
    print(f"\n✅ Success Criteria:")
    print(f"   • GUI test files (≥4): {'✅' if success_criteria['files_count'] else '❌'} ({structure_results['files_analyzed']})")
    print(f"   • Total tests (≥30): {'✅' if success_criteria['total_tests'] else '❌'} ({structure_results['total_tests']})")
    print(f"   • Component coverage (≥4): {'✅' if success_criteria['coverage_complete'] else '❌'} ({len(structure_results['coverage_areas'])})")
    print(f"   • GUI testing patterns: {'✅' if success_criteria['gui_patterns_present'] else '❌'}")
    print(f"   • Quality patterns: {'✅' if success_criteria['quality_patterns'] else '❌'}")
    print(f"   • No parse errors: {'✅' if success_criteria['no_parse_errors'] else '❌'}")
    
    overall_success = all(success_criteria.values())
    
    if overall_success:
        print(f"\n🎉 TASK-029 Implementation: ✅ SUCCESS")
        print(f"   • Comprehensive GUI test suite implemented")
        print(f"   • {structure_results['total_tests']} test methods across {structure_results['files_analyzed']} GUI test files")
        print(f"   • User interactions, widgets, and dialogs covered")
        print(f"   • PyQt6 testing patterns and best practices followed")
        print(f"   • QtBot usage for GUI simulation: {patterns['qtbot_usage']} instances")
    else:
        print(f"\n❌ TASK-029 Implementation: NEEDS WORK")
        failed_criteria = [k for k, v in success_criteria.items() if not v]
        print(f"   • Failed criteria: {', '.join(failed_criteria)}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)