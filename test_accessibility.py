#!/usr/bin/env python3
"""
Accessibility Features Test and WCAG Compliance Validation
Comprehensive testing of TASK-027 accessibility implementation
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from markitdown_gui.core.config_manager import ConfigManager
from markitdown_gui.core.accessibility_manager import (
    init_accessibility_manager, get_accessibility_manager, AccessibilityFeature
)
from markitdown_gui.core.keyboard_navigation import (
    init_keyboard_navigation_manager, get_keyboard_navigation_manager
)
from markitdown_gui.core.screen_reader_support import create_screen_reader_bridge
from markitdown_gui.core.accessibility_validator import (
    AccessibilityValidator, WCAGLevel, ValidationSeverity
)
from markitdown_gui.ui.main_window import MainWindow


class AccessibilityTester:
    """접근성 기능 테스터"""
    
    def __init__(self):
        self.results = {
            "test_summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "warnings": 0,
                "score": 0.0
            },
            "feature_tests": {},
            "wcag_compliance": {},
            "detailed_results": []
        }
        
        self.app = None
        self.main_window = None
        self.accessibility_manager = None
        self.keyboard_navigation = None
        self.validator = None
    
    def setup_test_environment(self):
        """테스트 환경 설정"""
        try:
            print("🔧 Setting up test environment...")
            
            # QApplication 생성
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # 설정 매니저 생성
            config_manager = ConfigManager()
            
            # 접근성 매니저 초기화
            self.accessibility_manager = init_accessibility_manager(self.app)
            
            # 키보드 네비게이션 초기화
            self.keyboard_navigation = init_keyboard_navigation_manager(self.app)
            
            # 메인 윈도우 생성
            self.main_window = MainWindow(config_manager)
            
            # 접근성 검증기 생성
            self.validator = AccessibilityValidator(self.accessibility_manager)
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test environment: {e}")
            return False
    
    def test_accessibility_manager(self) -> Dict[str, Any]:
        """접근성 매니저 테스트"""
        print("\n📋 Testing Accessibility Manager...")
        
        test_results = {
            "initialization": False,
            "widget_registration": False,
            "font_scaling": False,
            "feature_activation": False,
            "announcement_system": False,
            "details": []
        }
        
        try:
            # 초기화 테스트
            if self.accessibility_manager:
                test_results["initialization"] = True
                test_results["details"].append("✅ Accessibility manager initialized successfully")
            else:
                test_results["details"].append("❌ Accessibility manager not initialized")
            
            # 위젯 등록 테스트
            if self.accessibility_manager and self.main_window:
                widget_id = self.accessibility_manager.register_widget(
                    self.main_window,
                    accessible_name="Test Window",
                    accessible_description="Test window for accessibility validation"
                )
                
                if widget_id:
                    test_results["widget_registration"] = True
                    test_results["details"].append("✅ Widget registration working")
                else:
                    test_results["details"].append("❌ Widget registration failed")
            
            # 폰트 스케일링 테스트
            if self.accessibility_manager:
                # 120% 스케일 테스트
                scale_success = self.accessibility_manager.set_font_scale(1.2)
                if scale_success:
                    test_results["font_scaling"] = True
                    test_results["details"].append("✅ Font scaling working (120%)")
                    
                    # 원래 크기로 복원
                    self.accessibility_manager.set_font_scale(1.0)
                else:
                    test_results["details"].append("❌ Font scaling failed")
            
            # 기능 활성화 테스트
            if self.accessibility_manager:
                features_tested = [
                    AccessibilityFeature.KEYBOARD_NAVIGATION,
                    AccessibilityFeature.FOCUS_INDICATORS,
                    AccessibilityFeature.TOOLTIPS
                ]
                
                all_features_ok = True
                for feature in features_tested:
                    success = self.accessibility_manager.enable_feature(feature)
                    if not success:
                        all_features_ok = False
                        test_results["details"].append(f"❌ Failed to enable {feature.value}")
                
                if all_features_ok:
                    test_results["feature_activation"] = True
                    test_results["details"].append("✅ Feature activation working")
            
            # 알림 시스템 테스트
            if self.accessibility_manager:
                try:
                    success = self.accessibility_manager.announce_message(
                        "Test announcement", "polite"
                    )
                    test_results["announcement_system"] = success
                    if success:
                        test_results["details"].append("✅ Announcement system working")
                    else:
                        test_results["details"].append("⚠️ Announcement system not available")
                except Exception as e:
                    test_results["details"].append(f"⚠️ Announcement system error: {e}")
            
        except Exception as e:
            test_results["details"].append(f"❌ Accessibility manager test error: {e}")
        
        return test_results
    
    def test_keyboard_navigation(self) -> Dict[str, Any]:
        """키보드 네비게이션 테스트"""
        print("\n⌨️ Testing Keyboard Navigation...")
        
        test_results = {
            "initialization": False,
            "context_registration": False,
            "shortcut_system": False,
            "tab_order": False,
            "details": []
        }
        
        try:
            # 초기화 테스트
            if self.keyboard_navigation:
                test_results["initialization"] = True
                test_results["details"].append("✅ Keyboard navigation initialized")
            else:
                test_results["details"].append("❌ Keyboard navigation not initialized")
            
            # 컨텍스트 등록 테스트
            if self.keyboard_navigation and self.main_window:
                context = self.keyboard_navigation.register_context(self.main_window)
                if context:
                    test_results["context_registration"] = True
                    test_results["details"].append("✅ Navigation context registration working")
                else:
                    test_results["details"].append("❌ Navigation context registration failed")
            
            # 단축키 시스템 테스트
            if self.keyboard_navigation:
                shortcuts = self.keyboard_navigation.get_all_shortcuts()
                if shortcuts and "current" in shortcuts and len(shortcuts["current"]) > 0:
                    test_results["shortcut_system"] = True
                    test_results["details"].append(f"✅ Shortcut system working ({len(shortcuts['current'])} shortcuts)")
                else:
                    test_results["details"].append("❌ Shortcut system not working")
            
            # 탭 순서 테스트 (기본적인 검증)
            if self.main_window:
                # 포커스 가능한 위젯 찾기
                focusable_widgets = []
                for widget in self.main_window.findChildren(QWidget):
                    if (widget.focusPolicy() != Qt.FocusPolicy.NoFocus and 
                        widget.isVisible() and widget.isEnabled()):
                        focusable_widgets.append(widget)
                
                if len(focusable_widgets) > 0:
                    test_results["tab_order"] = True
                    test_results["details"].append(f"✅ Tab order established ({len(focusable_widgets)} focusable widgets)")
                else:
                    test_results["details"].append("⚠️ No focusable widgets found")
            
        except Exception as e:
            test_results["details"].append(f"❌ Keyboard navigation test error: {e}")
        
        return test_results
    
    def test_screen_reader_support(self) -> Dict[str, Any]:
        """스크린 리더 지원 테스트"""
        print("\n🔊 Testing Screen Reader Support...")
        
        test_results = {
            "bridge_creation": False,
            "platform_detection": False,
            "announcement_system": False,
            "live_regions": False,
            "details": []
        }
        
        try:
            # 스크린 리더 브리지 생성 테스트
            screen_reader_bridge = create_screen_reader_bridge(self.accessibility_manager)
            
            if screen_reader_bridge:
                test_results["bridge_creation"] = True
                test_results["details"].append("✅ Screen reader bridge created")
                
                # 초기화 테스트
                init_success = screen_reader_bridge.initialize()
                if init_success:
                    test_results["platform_detection"] = True
                    test_results["details"].append("✅ Screen reader platform detection working")
                    
                    # 스크린 리더 정보 확인
                    info = screen_reader_bridge.get_screen_reader_info()
                    test_results["details"].append(f"📋 Platform: {info.get('platform', 'Unknown')}")
                    test_results["details"].append(f"📋 Available: {info.get('available', False)}")
                    test_results["details"].append(f"📋 Name: {info.get('name', 'None')}")
                else:
                    test_results["details"].append("⚠️ Screen reader platform detection failed")
                
                # 알림 시스템 테스트
                try:
                    announce_success = screen_reader_bridge.announce(
                        "Test screen reader announcement", "polite"
                    )
                    test_results["announcement_system"] = announce_success
                    if announce_success:
                        test_results["details"].append("✅ Screen reader announcement working")
                    else:
                        test_results["details"].append("⚠️ Screen reader announcement not available")
                except Exception as e:
                    test_results["details"].append(f"⚠️ Screen reader announcement error: {e}")
                
                # 라이브 리전 테스트
                if self.main_window and hasattr(self.main_window, 'log_widget'):
                    try:
                        from markitdown_gui.core.screen_reader_support import LiveRegionType, AnnouncementPriority
                        live_region_success = screen_reader_bridge.register_live_region(
                            self.main_window.log_widget,
                            region_type=LiveRegionType.LOG,
                            priority=AnnouncementPriority.POLITE
                        )
                        
                        if live_region_success:
                            test_results["live_regions"] = True
                            test_results["details"].append("✅ Live regions working")
                        else:
                            test_results["details"].append("⚠️ Live regions registration failed")
                    except Exception as e:
                        test_results["details"].append(f"⚠️ Live regions test error: {e}")
            else:
                test_results["details"].append("❌ Screen reader bridge creation failed")
            
        except Exception as e:
            test_results["details"].append(f"❌ Screen reader support test error: {e}")
        
        return test_results
    
    def test_wcag_compliance(self) -> Dict[str, Any]:
        """WCAG 준수 테스트"""
        print("\n📊 Testing WCAG Compliance...")
        
        test_results = {
            "validator_creation": False,
            "application_validation": False,
            "compliance_score": 0.0,
            "compliance_level": "None",
            "critical_issues": 0,
            "major_issues": 0,
            "minor_issues": 0,
            "details": [],
            "issues_summary": []
        }
        
        try:
            # 검증기 생성 테스트
            if self.validator:
                test_results["validator_creation"] = True
                test_results["details"].append("✅ WCAG validator created")
                
                # 애플리케이션 전체 검증
                if self.main_window:
                    print("   🔍 Running comprehensive WCAG validation...")
                    validation_result = self.validator.validate_application()
                    
                    test_results["application_validation"] = True
                    test_results["compliance_score"] = validation_result.score
                    
                    compliance_level = validation_result.get_compliance_level()
                    test_results["compliance_level"] = compliance_level.value if compliance_level else "None"
                    
                    # 이슈 분류
                    test_results["critical_issues"] = len(validation_result.critical_issues)
                    test_results["major_issues"] = len(validation_result.major_issues)
                    test_results["minor_issues"] = len([i for i in validation_result.issues if i.severity == ValidationSeverity.MINOR])
                    
                    # 결과 요약
                    test_results["details"].append(f"✅ Application validation completed")
                    test_results["details"].append(f"📊 Compliance score: {validation_result.score:.1f}/100")
                    test_results["details"].append(f"🏆 Compliance level: {test_results['compliance_level']}")
                    test_results["details"].append(f"📋 Total issues: {len(validation_result.issues)}")
                    test_results["details"].append(f"   - Critical: {test_results['critical_issues']}")
                    test_results["details"].append(f"   - Major: {test_results['major_issues']}")
                    test_results["details"].append(f"   - Minor: {test_results['minor_issues']}")
                    
                    # 레벨별 점수
                    if validation_result.level_scores:
                        test_results["details"].append("📈 Level scores:")
                        for level, score in validation_result.level_scores.items():
                            test_results["details"].append(f"   - {level.value}: {score:.1f}/100")
                    
                    # 주요 이슈들 요약
                    if validation_result.critical_issues:
                        test_results["details"].append("🚨 Critical issues found:")
                        for issue in validation_result.critical_issues[:3]:  # 처음 3개만
                            test_results["issues_summary"].append({
                                "severity": issue.severity.value,
                                "title": issue.title,
                                "guideline": issue.guideline,
                                "description": issue.description
                            })
                            test_results["details"].append(f"   - {issue.guideline}: {issue.title}")
                    
                    # 자동 수정 가능한 이슈들 수정 테스트
                    auto_fixable_issues = [i for i in validation_result.issues if i.auto_fixable]
                    if auto_fixable_issues:
                        print(f"   🔧 Testing auto-fix for {len(auto_fixable_issues)} issues...")
                        fixed_count = self.validator.auto_fix_issues(auto_fixable_issues)
                        test_results["details"].append(f"🔧 Auto-fixed {fixed_count}/{len(auto_fixable_issues)} issues")
                    
                else:
                    test_results["details"].append("❌ No main window available for validation")
            else:
                test_results["details"].append("❌ WCAG validator not created")
        
        except Exception as e:
            test_results["details"].append(f"❌ WCAG compliance test error: {e}")
        
        return test_results
    
    def test_color_contrast(self) -> Dict[str, Any]:
        """색상 대비 테스트"""
        print("\n🎨 Testing Color Contrast...")
        
        test_results = {
            "contrast_calculation": False,
            "wcag_aa_compliance": False,
            "wcag_aaa_compliance": False,
            "details": []
        }
        
        try:
            from markitdown_gui.core.accessibility_validator import ColorContrastValidator
            
            validator = ColorContrastValidator()
            
            # 기본 색상 대비 테스트
            black = QColor(0, 0, 0)        # 검정
            white = QColor(255, 255, 255)  # 흰색
            gray = QColor(128, 128, 128)   # 회색
            
            # 검정/흰색 대비 (최대 대비)
            max_contrast = validator.calculate_contrast_ratio(black, white)
            if 20.0 <= max_contrast <= 21.1:  # 이론적 최대값은 21:1
                test_results["contrast_calculation"] = True
                test_results["details"].append(f"✅ Contrast calculation working (black/white: {max_contrast:.1f}:1)")
            
            # WCAG AA 기준 테스트 (4.5:1)
            aa_test_color1 = QColor(0, 0, 0)      # 검정
            aa_test_color2 = QColor(118, 118, 118) # 4.5:1 대비를 만족하는 회색
            aa_contrast = validator.calculate_contrast_ratio(aa_test_color1, aa_test_color2)
            
            if aa_contrast >= 4.5:
                test_results["wcag_aa_compliance"] = True
                test_results["details"].append(f"✅ WCAG AA contrast compliance verified ({aa_contrast:.1f}:1)")
            
            # WCAG AAA 기준 테스트 (7:1)
            aaa_test_color2 = QColor(85, 85, 85)  # 7:1 대비를 만족하는 회색
            aaa_contrast = validator.calculate_contrast_ratio(aa_test_color1, aaa_test_color2)
            
            if aaa_contrast >= 7.0:
                test_results["wcag_aaa_compliance"] = True
                test_results["details"].append(f"✅ WCAG AAA contrast compliance verified ({aaa_contrast:.1f}:1)")
            
            # 메인 윈도우 위젯들의 실제 대비 검사
            if self.main_window:
                test_widgets = []
                
                # 주요 위젯들 수집
                if hasattr(self.main_window, 'browse_btn'):
                    test_widgets.append(("Browse Button", self.main_window.browse_btn))
                if hasattr(self.main_window, 'convert_btn'):
                    test_widgets.append(("Convert Button", self.main_window.convert_btn))
                if hasattr(self.main_window, 'scan_btn'):
                    test_widgets.append(("Scan Button", self.main_window.scan_btn))
                
                failing_widgets = []
                for name, widget in test_widgets:
                    issues = validator.validate_widget_contrast(widget, WCAGLevel.AA)
                    if issues:
                        failing_widgets.append(name)
                
                if not failing_widgets:
                    test_results["details"].append("✅ All tested widgets pass WCAG AA contrast requirements")
                else:
                    test_results["details"].append(f"⚠️ {len(failing_widgets)} widgets have contrast issues: {', '.join(failing_widgets)}")
        
        except Exception as e:
            test_results["details"].append(f"❌ Color contrast test error: {e}")
        
        return test_results
    
    def test_touch_target_sizes(self) -> Dict[str, Any]:
        """터치 타겟 크기 테스트"""
        print("\n👆 Testing Touch Target Sizes...")
        
        test_results = {
            "size_validation": False,
            "compliant_widgets": 0,
            "non_compliant_widgets": 0,
            "details": []
        }
        
        try:
            MIN_SIZE = 44  # WCAG 2.1 AA 최소 터치 타겟 크기
            
            if self.main_window:
                interactive_widgets = []
                
                # 상호작용 가능한 위젯들 수집
                from PyQt6.QtWidgets import QPushButton, QCheckBox, QComboBox
                
                for widget in self.main_window.findChildren((QPushButton, QCheckBox, QComboBox)):
                    if widget.isVisible() and widget.isEnabled():
                        interactive_widgets.append(widget)
                
                compliant_count = 0
                non_compliant_widgets = []
                
                for widget in interactive_widgets:
                    size = widget.size()
                    width, height = size.width(), size.height()
                    
                    if width >= MIN_SIZE and height >= MIN_SIZE:
                        compliant_count += 1
                    else:
                        non_compliant_widgets.append({
                            "name": widget.objectName() or widget.__class__.__name__,
                            "size": f"{width}x{height}",
                            "widget": widget
                        })
                
                test_results["compliant_widgets"] = compliant_count
                test_results["non_compliant_widgets"] = len(non_compliant_widgets)
                
                if len(interactive_widgets) > 0:
                    test_results["size_validation"] = True
                    
                    compliance_rate = (compliant_count / len(interactive_widgets)) * 100
                    test_results["details"].append(f"✅ Touch target size validation completed")
                    test_results["details"].append(f"📊 Compliance rate: {compliance_rate:.1f}% ({compliant_count}/{len(interactive_widgets)})")
                    
                    if compliance_rate >= 90:
                        test_results["details"].append("🎯 Excellent touch target compliance!")
                    elif compliance_rate >= 70:
                        test_results["details"].append("👍 Good touch target compliance")
                    else:
                        test_results["details"].append("⚠️ Touch target compliance needs improvement")
                    
                    # 비준수 위젯들 나열
                    if non_compliant_widgets:
                        test_results["details"].append("📋 Non-compliant widgets:")
                        for widget_info in non_compliant_widgets[:5]:  # 처음 5개만
                            test_results["details"].append(f"   - {widget_info['name']}: {widget_info['size']}px")
                
                else:
                    test_results["details"].append("⚠️ No interactive widgets found for testing")
            
        except Exception as e:
            test_results["details"].append(f"❌ Touch target size test error: {e}")
        
        return test_results
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 Starting Accessibility Compliance Testing...")
        print("=" * 60)
        
        if not self.setup_test_environment():
            return False
        
        # 메인 윈도우 표시 (테스트를 위해)
        if self.main_window:
            self.main_window.show()
            # UI가 완전히 로드될 때까지 잠시 대기
            QTimer.singleShot(1000, self._continue_tests)
            
            # 이벤트 루프 실행
            if self.app:
                self.app.exec()
        
        return True
    
    def _continue_tests(self):
        """UI 로드 후 테스트 계속"""
        try:
            # 개별 테스트 실행
            self.results["feature_tests"]["accessibility_manager"] = self.test_accessibility_manager()
            self.results["feature_tests"]["keyboard_navigation"] = self.test_keyboard_navigation()
            self.results["feature_tests"]["screen_reader_support"] = self.test_screen_reader_support()
            self.results["feature_tests"]["color_contrast"] = self.test_color_contrast()
            self.results["feature_tests"]["touch_target_sizes"] = self.test_touch_target_sizes()
            
            # WCAG 준수 테스트 (가장 중요한 테스트)
            self.results["wcag_compliance"] = self.test_wcag_compliance()
            
            # 결과 집계
            self._calculate_test_summary()
            
            # 결과 출력
            self._print_test_results()
            
            # 결과 저장
            self._save_test_results()
            
            # 애플리케이션 종료
            if self.app:
                QTimer.singleShot(2000, self.app.quit)
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            if self.app:
                self.app.quit()
    
    def _calculate_test_summary(self):
        """테스트 결과 집계"""
        try:
            total_tests = 0
            passed_tests = 0
            warnings = 0
            
            # 기능 테스트 집계
            for test_name, test_result in self.results["feature_tests"].items():
                for check_name, check_passed in test_result.items():
                    if check_name != "details":
                        total_tests += 1
                        if check_passed:
                            passed_tests += 1
            
            # WCAG 준수 테스트 집계
            wcag_result = self.results["wcag_compliance"]
            if wcag_result.get("validator_creation", False):
                total_tests += 1
                passed_tests += 1
            
            if wcag_result.get("application_validation", False):
                total_tests += 1
                passed_tests += 1
                
                # WCAG 점수가 80점 이상이면 통과로 간주
                if wcag_result.get("compliance_score", 0) >= 80:
                    passed_tests += 1
                total_tests += 1
            
            # 경고 사항 계산
            warnings = wcag_result.get("major_issues", 0) + wcag_result.get("minor_issues", 0)
            
            # 전체 점수 계산
            if total_tests > 0:
                base_score = (passed_tests / total_tests) * 70  # 기능 테스트 70%
                wcag_score = wcag_result.get("compliance_score", 0) * 0.3  # WCAG 30%
                overall_score = base_score + wcag_score
            else:
                overall_score = 0
            
            self.results["test_summary"].update({
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "warnings": warnings,
                "score": overall_score
            })
            
        except Exception as e:
            print(f"❌ Error calculating test summary: {e}")
    
    def _print_test_results(self):
        """테스트 결과 출력"""
        try:
            print("\n" + "=" * 60)
            print("📊 ACCESSIBILITY TEST RESULTS SUMMARY")
            print("=" * 60)
            
            summary = self.results["test_summary"]
            wcag = self.results["wcag_compliance"]
            
            print(f"🧪 Total Tests: {summary['total_tests']}")
            print(f"✅ Passed: {summary['passed_tests']}")
            print(f"❌ Failed: {summary['failed_tests']}")
            print(f"⚠️  Warnings: {summary['warnings']}")
            print(f"📊 Overall Score: {summary['score']:.1f}/100")
            
            print(f"\n🏆 WCAG Compliance:")
            print(f"   Score: {wcag.get('compliance_score', 0):.1f}/100")
            print(f"   Level: {wcag.get('compliance_level', 'None')}")
            print(f"   Critical Issues: {wcag.get('critical_issues', 0)}")
            print(f"   Major Issues: {wcag.get('major_issues', 0)}")
            print(f"   Minor Issues: {wcag.get('minor_issues', 0)}")
            
            # 기능별 결과
            print(f"\n📋 Feature Test Results:")
            for test_name, test_result in self.results["feature_tests"].items():
                passed_count = sum(1 for k, v in test_result.items() if k != "details" and v)
                total_count = len([k for k in test_result.keys() if k != "details"])
                status = "✅" if passed_count == total_count else "⚠️" if passed_count > total_count // 2 else "❌"
                print(f"   {status} {test_name.replace('_', ' ').title()}: {passed_count}/{total_count}")
            
            # 전체 평가
            print(f"\n🎯 OVERALL ASSESSMENT:")
            if summary['score'] >= 90:
                print("   🌟 EXCELLENT - Outstanding accessibility compliance!")
            elif summary['score'] >= 80:
                print("   👍 GOOD - Strong accessibility support with minor improvements needed")
            elif summary['score'] >= 70:
                print("   📈 FAIR - Basic accessibility in place, improvements recommended") 
            elif summary['score'] >= 60:
                print("   ⚠️  NEEDS WORK - Significant accessibility issues to address")
            else:
                print("   🚨 POOR - Major accessibility barriers present")
            
            # 권고사항
            if wcag.get('critical_issues', 0) > 0:
                print("   🚨 CRITICAL: Address critical accessibility issues immediately")
            
            if summary['score'] < 90:
                print("   📝 RECOMMENDATION: Review and address identified issues")
                print("   📚 REFERENCE: https://www.w3.org/WAI/WCAG21/quickref/")
            
        except Exception as e:
            print(f"❌ Error printing test results: {e}")
    
    def _save_test_results(self):
        """테스트 결과 저장"""
        try:
            # 결과를 JSON 파일로 저장
            results_file = project_root / "accessibility_test_results.json"
            
            # 직렬화 가능한 형태로 변환
            serializable_results = self._make_serializable(self.results)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Test results saved to: {results_file}")
            
            # 요약 보고서도 텍스트로 저장
            report_file = project_root / "accessibility_test_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("ACCESSIBILITY TEST REPORT\n")
                f.write("=" * 40 + "\n\n")
                
                summary = self.results["test_summary"]
                wcag = self.results["wcag_compliance"]
                
                f.write(f"Overall Score: {summary['score']:.1f}/100\n")
                f.write(f"WCAG Compliance: {wcag.get('compliance_score', 0):.1f}/100 ({wcag.get('compliance_level', 'None')})\n")
                f.write(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}\n")
                f.write(f"Critical Issues: {wcag.get('critical_issues', 0)}\n")
                f.write(f"Major Issues: {wcag.get('major_issues', 0)}\n\n")
                
                # 상세 결과
                for test_name, test_result in self.results["feature_tests"].items():
                    f.write(f"{test_name.upper()}:\n")
                    for detail in test_result.get("details", []):
                        f.write(f"  {detail}\n")
                    f.write("\n")
            
            print(f"📋 Test report saved to: {report_file}")
            
        except Exception as e:
            print(f"❌ Error saving test results: {e}")
    
    def _make_serializable(self, obj):
        """객체를 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj


def main():
    """메인 함수"""
    print("🚀 MarkItDown GUI - TASK-027 Accessibility Testing")
    print("Testing comprehensive WCAG 2.1 AA compliance implementation")
    print()
    
    # 환경 변수 설정 (디버그 모드)
    os.environ['MARKITDOWN_DEBUG'] = '1'
    
    # 테스터 생성 및 실행
    tester = AccessibilityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Testing completed successfully!")
        return 0
    else:
        print("\n💥 Testing failed to complete!")
        return 1


if __name__ == "__main__":
    sys.exit(main())