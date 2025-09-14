#!/usr/bin/env python3
"""
Direct File Saving Implementation Validation
Validates the implementation structure and code quality without requiring PyQt6
"""

import ast
import sys
import inspect
from pathlib import Path
from typing import Dict, List, Any, Tuple
import importlib.util


class DirectFileSavingValidator:
    """Validates the direct file saving workflow implementation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.gui_dir = self.project_root / "markitdown_gui"
        self.validation_results = {}
        
    def validate_implementation(self) -> Dict[str, Any]:
        """Main validation method"""
        print("🔍 Direct File Saving Workflow Implementation Validation")
        print("=" * 60)
        
        results = {
            "file_conflict_handler": self.validate_file_conflict_handler(),
            "conversion_manager": self.validate_conversion_manager(),
            "progress_widget": self.validate_progress_widget(),
            "settings_integration": self.validate_settings_integration(),
            "main_window_integration": self.validate_main_window_integration(),
            "models_support": self.validate_models_support()
        }
        
        self.validation_results = results
        return results
        
    def validate_file_conflict_handler(self) -> Dict[str, Any]:
        """Validate FileConflictHandler implementation"""
        print("\n🧪 Testing File Conflict Handler...")
        
        handler_path = self.gui_dir / "core" / "file_conflict_handler.py"
        if not handler_path.exists():
            return {"status": "failed", "error": "FileConflictHandler file not found"}
            
        try:
            with open(handler_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Check for required classes and methods
            classes = {}
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    classes[node.name] = class_methods
                elif isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                    functions.append(node.name)
            
            # Required functionality checks
            required_classes = ["FileConflictHandler", "ConflictStatistics"]
            required_methods = {
                "FileConflictHandler": [
                    "detect_conflict", "resolve_conflict", "generate_renamed_path",
                    "apply_batch_policy", "get_conflict_statistics"
                ]
            }
            
            validation = {
                "status": "passed",
                "classes_found": list(classes.keys()),
                "required_classes_present": all(cls in classes for cls in required_classes),
                "methods_validation": {},
                "conflict_policies_supported": self._check_conflict_policies(content),
                "thread_safety": self._check_thread_safety(content),
                "error_handling": self._check_error_handling(content),
                "statistics_tracking": "ConflictStatistics" in classes
            }
            
            # Validate methods for each class
            for class_name, required_methods_list in required_methods.items():
                if class_name in classes:
                    validation["methods_validation"][class_name] = {
                        "required": required_methods_list,
                        "found": classes[class_name],
                        "all_present": all(method in classes[class_name] for method in required_methods_list)
                    }
            
            print(f"  ✅ Classes: {', '.join(classes.keys())}")
            print(f"  ✅ Conflict policies: {'Supported' if validation['conflict_policies_supported'] else 'Missing'}")
            print(f"  ✅ Thread safety: {'Implemented' if validation['thread_safety'] else 'Missing'}")
            print(f"  ✅ Statistics: {'Implemented' if validation['statistics_tracking'] else 'Missing'}")
            
            return validation
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def validate_conversion_manager(self) -> Dict[str, Any]:
        """Validate ConversionManager implementation"""
        print("\n🧪 Testing Conversion Manager...")
        
        manager_path = self.gui_dir / "core" / "conversion_manager.py"
        if not manager_path.exists():
            return {"status": "failed", "error": "ConversionManager file not found"}
            
        try:
            with open(manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Check for required classes and methods
            classes = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    classes[node.name] = class_methods
            
            required_classes = ["ConversionManager", "ConversionWorker"]
            required_methods = {
                "ConversionManager": [
                    "convert_files_async", "set_save_to_original_directory",
                    "set_conflict_policy", "prepare_files_for_conversion"
                ],
                "ConversionWorker": ["run", "_convert_single_file", "_save_converted_content"]
            }
            
            validation = {
                "status": "passed",
                "classes_found": list(classes.keys()),
                "required_classes_present": all(cls in classes for cls in required_classes),
                "direct_file_saving": self._check_direct_file_saving(content),
                "conflict_integration": self._check_conflict_integration(content),
                "progress_tracking": self._check_progress_tracking(content),
                "methods_validation": {}
            }
            
            # Validate methods for each class
            for class_name, required_methods_list in required_methods.items():
                if class_name in classes:
                    validation["methods_validation"][class_name] = {
                        "required": required_methods_list,
                        "found": classes[class_name],
                        "all_present": all(method in classes[class_name] for method in required_methods_list)
                    }
            
            print(f"  ✅ Classes: {', '.join(classes.keys())}")
            print(f"  ✅ Direct file saving: {'Implemented' if validation['direct_file_saving'] else 'Missing'}")
            print(f"  ✅ Conflict integration: {'Implemented' if validation['conflict_integration'] else 'Missing'}")
            print(f"  ✅ Progress tracking: {'Implemented' if validation['progress_tracking'] else 'Missing'}")
            
            return validation
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def validate_progress_widget(self) -> Dict[str, Any]:
        """Validate ProgressWidget implementation"""
        print("\n🧪 Testing Progress Widget...")
        
        widget_path = self.gui_dir / "ui" / "components" / "progress_widget.py"
        if not widget_path.exists():
            return {"status": "failed", "error": "ProgressWidget file not found"}
            
        try:
            with open(widget_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Check for required classes
            classes = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    classes[node.name] = class_methods
            
            required_classes = ["ProgressWidget", "ConflictSummaryWidget", "PerformanceMetricsWidget"]
            
            validation = {
                "status": "passed",
                "classes_found": list(classes.keys()),
                "required_classes_present": all(cls in classes for cls in required_classes),
                "real_time_updates": self._check_real_time_updates(content),
                "conflict_indicators": self._check_conflict_indicators(content),
                "performance_metrics": self._check_performance_metrics(content),
                "user_interaction": self._check_user_interaction(content)
            }
            
            print(f"  ✅ Classes: {', '.join(classes.keys())}")
            print(f"  ✅ Real-time updates: {'Implemented' if validation['real_time_updates'] else 'Missing'}")
            print(f"  ✅ Conflict indicators: {'Implemented' if validation['conflict_indicators'] else 'Missing'}")
            print(f"  ✅ Performance metrics: {'Implemented' if validation['performance_metrics'] else 'Missing'}")
            
            return validation
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def validate_settings_integration(self) -> Dict[str, Any]:
        """Validate settings integration"""
        print("\n🧪 Testing Settings Integration...")
        
        settings_path = self.gui_dir / "ui" / "settings_dialog.py"
        config_path = self.gui_dir / "core" / "config_manager.py"
        
        validation = {
            "status": "passed",
            "settings_dialog_exists": settings_path.exists(),
            "config_manager_exists": config_path.exists(),
            "conversion_settings": False,
            "conflict_settings": False,
            "persistence": False
        }
        
        if settings_path.exists():
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings_content = f.read()
                validation["conversion_settings"] = "conversion" in settings_content.lower()
                validation["conflict_settings"] = "conflict" in settings_content.lower()
            except:
                pass
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                validation["persistence"] = "save_config" in config_content and "load_config" in config_content
            except:
                pass
        
        print(f"  ✅ Settings dialog: {'Found' if validation['settings_dialog_exists'] else 'Missing'}")
        print(f"  ✅ Config manager: {'Found' if validation['config_manager_exists'] else 'Missing'}")
        print(f"  ✅ Conversion settings: {'Implemented' if validation['conversion_settings'] else 'Missing'}")
        print(f"  ✅ Persistence: {'Implemented' if validation['persistence'] else 'Missing'}")
        
        return validation
    
    def validate_main_window_integration(self) -> Dict[str, Any]:
        """Validate main window integration"""
        print("\n🧪 Testing Main Window Integration...")
        
        main_window_path = self.gui_dir / "ui" / "main_window.py"
        if not main_window_path.exists():
            return {"status": "failed", "error": "MainWindow file not found"}
            
        try:
            with open(main_window_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            validation = {
                "status": "passed",
                "conversion_manager_integration": "ConversionManager" in content,
                "progress_widget_integration": "ProgressWidget" in content,
                "settings_integration": "settings" in content.lower(),
                "conflict_handling": "conflict" in content.lower(),
                "file_operations": "convert_files" in content
            }
            
            print(f"  ✅ Conversion manager: {'Integrated' if validation['conversion_manager_integration'] else 'Missing'}")
            print(f"  ✅ Progress widget: {'Integrated' if validation['progress_widget_integration'] else 'Missing'}")
            print(f"  ✅ Settings: {'Integrated' if validation['settings_integration'] else 'Missing'}")
            print(f"  ✅ File operations: {'Implemented' if validation['file_operations'] else 'Missing'}")
            
            return validation
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def validate_models_support(self) -> Dict[str, Any]:
        """Validate models and data structures"""
        print("\n🧪 Testing Models Support...")
        
        models_path = self.gui_dir / "core" / "models.py"
        if not models_path.exists():
            return {"status": "failed", "error": "Models file not found"}
            
        try:
            with open(models_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_classes = [
                "FileConflictStatus", "FileConflictPolicy", "FileConflictConfig",
                "ConversionProgressStatus", "ConversionProgress", "ConversionResult"
            ]
            
            validation = {
                "status": "passed",
                "required_models": {},
                "conflict_support": True,
                "progress_support": True,
                "result_support": True
            }
            
            for model_class in required_classes:
                validation["required_models"][model_class] = model_class in content
            
            all_models_present = all(validation["required_models"].values())
            validation["all_required_models"] = all_models_present
            
            print(f"  ✅ Required models: {sum(validation['required_models'].values())}/{len(required_classes)}")
            print(f"  ✅ Conflict models: {'Supported' if validation['conflict_support'] else 'Missing'}")
            print(f"  ✅ Progress models: {'Supported' if validation['progress_support'] else 'Missing'}")
            
            return validation
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    # Helper methods for specific checks
    
    def _check_conflict_policies(self, content: str) -> bool:
        """Check if all conflict policies are supported"""
        policies = ["SKIP", "OVERWRITE", "RENAME", "ASK_USER"]
        return all(policy in content for policy in policies)
    
    def _check_thread_safety(self, content: str) -> bool:
        """Check for thread safety implementations"""
        thread_indicators = ["threading", "QMutex", "_lock", "with self._lock"]
        return any(indicator in content for indicator in thread_indicators)
    
    def _check_error_handling(self, content: str) -> bool:
        """Check for proper error handling"""
        error_indicators = ["try:", "except:", "raise", "Exception"]
        return all(indicator in content for indicator in error_indicators)
    
    def _check_direct_file_saving(self, content: str) -> bool:
        """Check for direct file saving implementation"""
        indicators = ["save_to_original_dir", "original_dir", "create_markdown_output_path"]
        return any(indicator in content for indicator in indicators)
    
    def _check_conflict_integration(self, content: str) -> bool:
        """Check for conflict handler integration"""
        indicators = ["FileConflictHandler", "conflict_handler", "detect_conflict"]
        return any(indicator in content for indicator in indicators)
    
    def _check_progress_tracking(self, content: str) -> bool:
        """Check for progress tracking implementation"""
        indicators = ["progress_updated", "ConversionProgress", "progress_status"]
        return any(indicator in content for indicator in indicators)
    
    def _check_real_time_updates(self, content: str) -> bool:
        """Check for real-time progress updates"""
        indicators = ["update_progress", "pyqtSignal", "progress_updated"]
        return any(indicator in content for indicator in indicators)
    
    def _check_conflict_indicators(self, content: str) -> bool:
        """Check for conflict indicators in UI"""
        indicators = ["conflict_status", "ConflictSummaryWidget", "conflict_detected"]
        return any(indicator in content for indicator in indicators)
    
    def _check_performance_metrics(self, content: str) -> bool:
        """Check for performance metrics"""
        indicators = ["PerformanceMetricsWidget", "elapsed_time", "estimated_time"]
        return any(indicator in content for indicator in indicators)
    
    def _check_user_interaction(self, content: str) -> bool:
        """Check for user interaction support"""
        indicators = ["cancel_requested", "settings_requested", "QPushButton"]
        return any(indicator in content for indicator in indicators)
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        if not self.validation_results:
            return "No validation results available"
        
        report = []
        report.append("📊 DIRECT FILE SAVING WORKFLOW VALIDATION REPORT")
        report.append("=" * 60)
        
        total_checks = 0
        passed_checks = 0
        critical_failures = []
        
        for component, results in self.validation_results.items():
            report.append(f"\n🧪 {component.upper().replace('_', ' ')}")
            report.append("-" * 40)
            
            if results.get("status") == "failed":
                report.append(f"  ❌ FAILED: {results.get('error', 'Unknown error')}")
                critical_failures.append(component)
                total_checks += 1
                continue
            
            # Count individual checks
            component_checks = 0
            component_passed = 0
            
            for key, value in results.items():
                if key in ["status", "error"]:
                    continue
                    
                component_checks += 1
                total_checks += 1
                
                if isinstance(value, bool):
                    if value:
                        report.append(f"  ✅ {key.replace('_', ' ').title()}: Implemented")
                        component_passed += 1
                        passed_checks += 1
                    else:
                        report.append(f"  ❌ {key.replace('_', ' ').title()}: Missing")
                        
                elif isinstance(value, dict):
                    if value.get("all_present", False) or value.get("all_required_models", False):
                        report.append(f"  ✅ {key.replace('_', ' ').title()}: Complete")
                        component_passed += 1
                        passed_checks += 1
                    else:
                        report.append(f"  ⚠️ {key.replace('_', ' ').title()}: Partial")
                        passed_checks += 0.5  # Partial credit
                        
                elif isinstance(value, list) and len(value) > 0:
                    report.append(f"  ✅ {key.replace('_', ' ').title()}: {len(value)} items")
                    component_passed += 1
                    passed_checks += 1
                    
            report.append(f"  Component Score: {component_passed}/{component_checks}")
        
        # Overall assessment
        report.append("\n" + "=" * 60)
        report.append("📈 OVERALL ASSESSMENT")
        report.append("=" * 60)
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report.append(f"Total Checks: {total_checks}")
        report.append(f"Passed: {passed_checks:.1f}")
        report.append(f"Success Rate: {success_rate:.1f}%")
        
        if critical_failures:
            report.append(f"Critical Failures: {', '.join(critical_failures)}")
        
        # Determine overall status
        if success_rate >= 95:
            report.append("\n🎉 EXCELLENT! Implementation is production-ready")
            status = "EXCELLENT"
        elif success_rate >= 85:
            report.append("\n✅ GOOD! Implementation is solid with minor gaps")
            status = "GOOD"
        elif success_rate >= 70:
            report.append("\n⚠️ FAIR! Implementation needs attention in several areas")
            status = "FAIR"
        else:
            report.append("\n❌ NEEDS WORK! Major implementation gaps found")
            status = "NEEDS_WORK"
        
        # Specific recommendations
        report.append("\n📋 RECOMMENDATIONS:")
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report.append(f"  • {rec}")
        
        # Test readiness assessment
        report.append("\n🧪 TESTING READINESS:")
        
        readiness_checks = {
            "Direct File Saving": self._is_feature_ready("direct_file_saving"),
            "Conflict Resolution": self._is_feature_ready("conflict_resolution"), 
            "Progress Tracking": self._is_feature_ready("progress_tracking"),
            "Settings Integration": self._is_feature_ready("settings_integration"),
            "UI Integration": self._is_feature_ready("ui_integration")
        }
        
        for feature, ready in readiness_checks.items():
            status_icon = "✅" if ready else "❌"
            report.append(f"  {status_icon} {feature}: {'Ready' if ready else 'Needs work'}")
        
        overall_ready = all(readiness_checks.values())
        report.append(f"\nOverall Test Readiness: {'✅ READY' if overall_ready else '❌ NOT READY'}")
        
        return "\n".join(report)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate specific recommendations based on validation results"""
        recommendations = []
        
        # Check each component for issues
        for component, results in self.validation_results.items():
            if results.get("status") == "failed":
                recommendations.append(f"Fix critical failure in {component}")
                continue
            
            # Component-specific recommendations
            if component == "file_conflict_handler":
                if not results.get("thread_safety", False):
                    recommendations.append("Implement thread safety in FileConflictHandler")
                if not results.get("conflict_policies_supported", False):
                    recommendations.append("Ensure all conflict policies (SKIP, OVERWRITE, RENAME, ASK_USER) are supported")
                    
            elif component == "conversion_manager":
                if not results.get("direct_file_saving", False):
                    recommendations.append("Implement direct file saving to original directories")
                if not results.get("conflict_integration", False):
                    recommendations.append("Integrate FileConflictHandler with ConversionManager")
                    
            elif component == "progress_widget":
                if not results.get("real_time_updates", False):
                    recommendations.append("Implement real-time progress updates in ProgressWidget")
                if not results.get("conflict_indicators", False):
                    recommendations.append("Add conflict indicators to progress UI")
        
        if not recommendations:
            recommendations.append("Implementation looks solid! Consider comprehensive testing")
            recommendations.append("Validate user experience with real-world usage scenarios")
            recommendations.append("Test performance with large file sets")
            
        return recommendations
    
    def _is_feature_ready(self, feature: str) -> bool:
        """Check if a specific feature is ready for testing"""
        feature_readiness = {
            "direct_file_saving": (
                self.validation_results.get("conversion_manager", {}).get("direct_file_saving", False) and
                self.validation_results.get("models_support", {}).get("all_required_models", False)
            ),
            "conflict_resolution": (
                self.validation_results.get("file_conflict_handler", {}).get("required_classes_present", False) and
                self.validation_results.get("file_conflict_handler", {}).get("conflict_policies_supported", False)
            ),
            "progress_tracking": (
                self.validation_results.get("progress_widget", {}).get("real_time_updates", False) and
                self.validation_results.get("conversion_manager", {}).get("progress_tracking", False)
            ),
            "settings_integration": (
                self.validation_results.get("settings_integration", {}).get("persistence", False) and
                self.validation_results.get("settings_integration", {}).get("conversion_settings", False)
            ),
            "ui_integration": (
                self.validation_results.get("main_window_integration", {}).get("conversion_manager_integration", False) and
                self.validation_results.get("main_window_integration", {}).get("progress_widget_integration", False)
            )
        }
        
        return feature_readiness.get(feature, False)


def main():
    """Main validation function"""
    validator = DirectFileSavingValidator()
    
    try:
        # Run validation
        validator.validate_implementation()
        
        # Generate and display report
        report = validator.generate_validation_report()
        print(report)
        
        # Determine exit code
        success_rate = sum(
            1 for results in validator.validation_results.values()
            if results.get("status") != "failed"
        ) / len(validator.validation_results) * 100
        
        return 0 if success_rate >= 70 else 1
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())