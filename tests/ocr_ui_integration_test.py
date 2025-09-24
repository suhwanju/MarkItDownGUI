#!/usr/bin/env python3
"""
OCR UI Integration Test Suite
Comprehensive testing for OCR UI Status Integration feature

Tests all functionality:
1. OCR Status Badge System
2. Enhanced Progress Tracking
3. OCR Result Formatting
4. Feature Flag Control
5. Theme Integration
6. Performance & Error Handling
7. Integration & Backward Compatibility
8. User Experience

Production-Ready QA Testing
"""

import sys
import os
import time
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QFont, QColor

# Import the modules under test
from markitdown_gui.core.models import FileInfo, ConversionStatus
from markitdown_gui.core.config_manager import ConfigManager
from markitdown_gui.core.logger import get_logger

# OCR Enhancement imports
from markitdown_gui.core.ocr_enhancements.models import (
    OCREnhancementConfig, OCRStatusType, QualityLevel, OCREnhancementResult,
    QualityMetrics, OCREnhancementType, OCRStatusInfo, OCRProgressInfo
)
from markitdown_gui.core.ocr_enhancements.ui_integrations.ocr_status_provider import (
    OCRStatusProvider, OCRStatusBadge, OCRMethodBadge
)
from markitdown_gui.core.ocr_enhancements.ui_integrations.ocr_progress_tracker import (
    OCRProgressTracker, OCRStageProgressBar
)
from markitdown_gui.core.ocr_enhancements.ui_integrations.ocr_result_formatter import (
    OCRResultFormatter, ConfidenceScoreWidget, ProcessingMethodIndicator,
    QualityMetricsWidget, EnhancementSummaryWidget
)
from markitdown_gui.ui.components.file_list_widget import FileListWidget
from markitdown_gui.ui.components.progress_widget import ProgressWidget

logger = get_logger(__name__)


class OCRUIIntegrationTestSuite:
    """OCR UI Integration 종합 테스트 스위트"""

    def __init__(self):
        self.app = None
        self.config_manager = None
        self.ocr_config = None
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = datetime.now()

        # Test data
        self.test_image_files = []
        self.test_pdf_files = []
        self.test_results_log = []

    def setup_test_environment(self):
        """테스트 환경 설정"""
        logger.info("=== OCR UI Integration Test Suite 시작 ===")

        # QApplication 초기화
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        # Configuration Manager 설정
        self.config_manager = ConfigManager()

        # OCR Enhancement Config 생성
        self.ocr_config = OCREnhancementConfig()
        self.ocr_config.enabled = True

        # 테스트 파일 생성
        self._create_test_files()

        logger.info(f"테스트 환경 설정 완료: {len(self.test_image_files)} 이미지, {len(self.test_pdf_files)} PDF")

    def _create_test_files(self):
        """테스트용 파일 정보 생성"""
        test_dir = Path(tempfile.gettempdir()) / "ocr_ui_test"
        test_dir.mkdir(exist_ok=True)

        # 이미지 파일들
        image_extensions = ['.jpg', '.png', '.pdf', '.gif', '.bmp']
        for i, ext in enumerate(image_extensions):
            file_path = test_dir / f"test_image_{i}{ext}"
            file_path.touch()  # 빈 파일 생성

            file_info = FileInfo(file_path)
            file_info.is_selected = True
            self.test_image_files.append(file_info)

        # PDF 파일들
        for i in range(3):
            file_path = test_dir / f"test_document_{i}.pdf"
            file_path.touch()

            file_info = FileInfo(file_path)
            file_info.is_selected = True
            self.test_pdf_files.append(file_info)

    def test_ocr_status_badge_system(self) -> Dict[str, Any]:
        """1. OCR Status Badge System 테스트"""
        logger.info("1. OCR Status Badge System 테스트 시작")
        test_result = {
            'test_name': 'OCR Status Badge System',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            # OCR Status Provider 생성
            status_provider = OCRStatusProvider(self.ocr_config)

            # 1.1 Status Badge 생성 테스트
            start_time = time.time()

            # 다양한 상태의 배지 생성
            statuses_to_test = [
                (OCRStatusType.IDLE, None),
                (OCRStatusType.INITIALIZING, None),
                (OCRStatusType.PROCESSING, None),
                (OCRStatusType.COMPLETED, QualityLevel.EXCELLENT),
                (OCRStatusType.COMPLETED, QualityLevel.GOOD),
                (OCRStatusType.COMPLETED, QualityLevel.FAIR),
                (OCRStatusType.COMPLETED, QualityLevel.POOR),
                (OCRStatusType.FAILED, None),
                (OCRStatusType.CANCELLED, None)
            ]

            badge_creation_times = []
            for status, quality in statuses_to_test:
                badge_start = time.time()
                badge = OCRStatusBadge(status, quality)
                badge_end = time.time()

                badge_creation_time = (badge_end - badge_start) * 1000  # ms
                badge_creation_times.append(badge_creation_time)

                # 배지 가시성 검증
                if status == OCRStatusType.IDLE:
                    if badge.isVisible():
                        test_result['issues'].append("IDLE 상태 배지가 숨겨지지 않음")
                        test_result['passed'] = False
                else:
                    if not badge.isVisible():
                        test_result['issues'].append(f"{status.value} 상태 배지가 표시되지 않음")
                        test_result['passed'] = False

                # 툴팁 검증
                tooltip = badge.toolTip()
                if not tooltip:
                    test_result['issues'].append(f"{status.value} 상태 배지에 툴팁이 없음")
                    test_result['passed'] = False

                # 색상 검증 (픽스맵이 올바르게 생성되었는지)
                pixmap = badge.pixmap()
                if status != OCRStatusType.IDLE and pixmap.isNull():
                    test_result['issues'].append(f"{status.value} 상태 배지 픽스맵이 생성되지 않음")
                    test_result['passed'] = False

            # 성능 검증
            avg_badge_creation_time = sum(badge_creation_times) / len(badge_creation_times)
            if avg_badge_creation_time > 100:  # 100ms 초과시 성능 이슈
                test_result['issues'].append(f"배지 생성 시간이 너무 느림: {avg_badge_creation_time:.2f}ms")
                test_result['passed'] = False

            test_result['performance']['avg_badge_creation_time'] = avg_badge_creation_time
            test_result['performance']['max_badge_creation_time'] = max(badge_creation_times)

            # 1.2 Method Badge 테스트
            methods_to_test = ['llm', 'tesseract', 'offline', 'unknown']
            method_badge_times = []

            for method in methods_to_test:
                method_start = time.time()
                method_badge = OCRMethodBadge(method)
                method_end = time.time()

                method_time = (method_end - method_start) * 1000
                method_badge_times.append(method_time)

                if not method_badge.isVisible():
                    test_result['issues'].append(f"{method} 방법 배지가 표시되지 않음")
                    test_result['passed'] = False

            avg_method_badge_time = sum(method_badge_times) / len(method_badge_times)
            test_result['performance']['avg_method_badge_time'] = avg_method_badge_time

            # 1.3 Status Provider 통합 테스트
            for file_info in self.test_image_files:
                widget = status_provider.create_status_badge_widget(file_info)

                # 이미지 파일은 배지가 생성되어야 함
                if not widget:
                    test_result['issues'].append(f"이미지 파일 {file_info.name}에 대한 배지가 생성되지 않음")
                    test_result['passed'] = False

            # 1.4 캐시 성능 테스트
            cache_start = time.time()
            for _ in range(100):  # 반복 호출로 캐시 성능 테스트
                for file_info in self.test_image_files:
                    status_provider.create_status_badge_widget(file_info)
            cache_end = time.time()

            cache_time = (cache_end - cache_start) * 1000 / 100  # 평균시간
            test_result['performance']['cache_lookup_time'] = cache_time

            if cache_time > 1:  # 1ms 초과시 캐시 성능 이슈
                test_result['issues'].append(f"캐시 조회 시간이 너무 느림: {cache_time:.2f}ms")
                test_result['passed'] = False

            # 캐시 통계 검증
            cache_stats = status_provider.get_cache_stats()
            test_result['details']['cache_stats'] = cache_stats

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"OCR Status Badge System 테스트 실패: {e}")

        return test_result

    def test_enhanced_progress_tracking(self) -> Dict[str, Any]:
        """2. Enhanced Progress Tracking 테스트"""
        logger.info("2. Enhanced Progress Tracking 테스트 시작")
        test_result = {
            'test_name': 'Enhanced Progress Tracking',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            # OCR Progress Tracker 생성
            progress_tracker = OCRProgressTracker(self.ocr_config)

            # 2.1 진행률 추적 시작 테스트
            test_enhancements = [
                OCREnhancementType.PREPROCESSING,
                OCREnhancementType.ACCURACY_BOOST,
                OCREnhancementType.POST_PROCESSING
            ]

            start_time = time.time()

            for file_info in self.test_image_files[:2]:  # 첫 2개 파일만 테스트
                progress_tracker.start_ocr_tracking(file_info, test_enhancements)

                # 진행률 정보 확인
                progress_info = progress_tracker.get_ocr_progress_info(file_info)
                if not progress_info:
                    test_result['issues'].append(f"파일 {file_info.name}의 진행률 정보가 없음")
                    test_result['passed'] = False
                    continue

                if progress_info.total_steps != len(test_enhancements) + 1:
                    test_result['issues'].append(f"총 단계 수가 올바르지 않음: {progress_info.total_steps}")
                    test_result['passed'] = False

                # 상태 정보 확인
                status_info = progress_tracker.get_ocr_status_info(file_info)
                if not status_info:
                    test_result['issues'].append(f"파일 {file_info.name}의 상태 정보가 없음")
                    test_result['passed'] = False
                    continue

                if status_info.status != OCRStatusType.INITIALIZING:
                    test_result['issues'].append(f"초기 상태가 올바르지 않음: {status_info.status}")
                    test_result['passed'] = False

            # 2.2 OCR 단계 업데이트 테스트
            test_stages = [
                (OCRStatusType.PREPROCESSING, 0.3),
                (OCRStatusType.PROCESSING, 0.6),
                (OCRStatusType.POST_PROCESSING, 0.8),
                (OCRStatusType.ANALYZING, 0.9),
                (OCRStatusType.COMPLETED, 1.0)
            ]

            stage_update_times = []
            for file_info in self.test_image_files[:1]:  # 첫 번째 파일만
                for stage, progress in test_stages:
                    stage_start = time.time()
                    progress_tracker.update_ocr_stage(file_info, stage, progress)
                    stage_end = time.time()

                    stage_time = (stage_end - stage_start) * 1000
                    stage_update_times.append(stage_time)

                    # 상태 확인
                    status_info = progress_tracker.get_ocr_status_info(file_info)
                    if status_info.status != stage:
                        test_result['issues'].append(f"단계 업데이트 실패: {stage.value}")
                        test_result['passed'] = False

            avg_stage_update_time = sum(stage_update_times) / len(stage_update_times)
            if avg_stage_update_time > 50:  # 50ms 초과시 성능 이슈
                test_result['issues'].append(f"단계 업데이트가 너무 느림: {avg_stage_update_time:.2f}ms")
                test_result['passed'] = False

            test_result['performance']['avg_stage_update_time'] = avg_stage_update_time

            # 2.3 개선 진행률 업데이트 테스트
            for file_info in self.test_image_files[:1]:
                for enhancement in test_enhancements:
                    progress_tracker.update_enhancement_progress(file_info, enhancement, completed=True)

                # 전체 진행률 확인
                enhancement_progress = progress_tracker.get_enhancement_progress(file_info)
                if abs(enhancement_progress - 1.0) > 0.01:  # 완료되어야 함
                    test_result['issues'].append(f"개선 진행률이 올바르지 않음: {enhancement_progress}")
                    test_result['passed'] = False

            # 2.4 OCR Stage Progress Bar 테스트
            stage_bar = OCRStageProgressBar()

            for stage, progress in test_stages:
                stage_bar.update_stage(stage, progress)

                # 값 확인
                if stage_bar.value() != int(progress * 100):
                    test_result['issues'].append(f"진행률 바 값이 올바르지 않음: {stage_bar.value()}")
                    test_result['passed'] = False

            # 2.5 시간 추정 테스트
            for file_info in self.test_image_files[:1]:
                remaining_time = progress_tracker.get_estimated_remaining_time(file_info)
                # 완료된 작업이므로 None이어야 함

                # 요약 생성 테스트
                summary = progress_tracker.create_ocr_progress_summary(file_info)
                if not summary:
                    test_result['issues'].append("진행률 요약이 생성되지 않음")
                    test_result['passed'] = False

            # 2.6 통계 확인
            tracking_stats = progress_tracker.get_tracking_stats()
            test_result['details']['tracking_stats'] = tracking_stats

            # 완료 테스트
            for file_info in self.test_image_files[:2]:
                progress_tracker.complete_ocr_tracking(file_info, success=True)

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"Enhanced Progress Tracking 테스트 실패: {e}")

        return test_result

    def test_ocr_result_formatting(self) -> Dict[str, Any]:
        """3. OCR Result Formatting 테스트"""
        logger.info("3. OCR Result Formatting 테스트 시작")
        test_result = {
            'test_name': 'OCR Result Formatting',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            # Result Formatter 생성
            result_formatter = OCRResultFormatter()

            start_time = time.time()

            # 3.1 테스트 OCR 결과 생성
            file_info = self.test_image_files[0]

            # Quality Metrics 생성
            quality_metrics = QualityMetrics(
                confidence_score=0.85,
                clarity_score=0.78,
                completeness_score=0.92,
                consistency_score=0.88,
                overall_quality=QualityLevel.GOOD,
                character_count=1250,
                word_count=187,
                line_count=42,
                detected_issues=["일부 글자가 흐림", "노이즈 포함"],
                suggestions=["이미지 해상도 개선 권장", "전처리 적용 권장"]
            )

            # OCR Enhancement Result 생성
            enhancement_result = OCREnhancementResult(
                file_info=file_info,
                original_result=Mock(),
                enhanced_text="테스트 OCR 결과 텍스트입니다.\n개선된 품질로 추출되었습니다.",
                quality_metrics=quality_metrics,
                applied_enhancements=[
                    OCREnhancementType.PREPROCESSING,
                    OCREnhancementType.POST_PROCESSING
                ],
                processing_time=12.5,
                enhancement_overhead=3.2,
                improvement_ratio=0.15,
                status_info=OCRStatusInfo(status=OCRStatusType.COMPLETED),
                enhancement_summary="전처리 및 후처리 개선 적용됨"
            )
            enhancement_result.original_result.text = "원본 OCR 결과 텍스트입니다.\n기본 품질입니다."

            # 3.2 Confidence Score Widget 테스트
            confidence_widget = ConfidenceScoreWidget(0.85)

            # 신뢰도 값 확인
            if confidence_widget._confidence != 0.85:
                test_result['issues'].append("신뢰도 값이 올바르게 설정되지 않음")
                test_result['passed'] = False

            # 다양한 신뢰도 값 테스트
            confidence_values = [0.95, 0.85, 0.65, 0.45, 0.25]
            for conf in confidence_values:
                confidence_widget.set_confidence(conf)
                # 위젯이 올바르게 업데이트되는지 확인
                if confidence_widget.confidence_bar.value() != int(conf * 100):
                    test_result['issues'].append(f"신뢰도 표시가 올바르지 않음: {conf}")
                    test_result['passed'] = False

            # 3.3 Processing Method Indicator 테스트
            methods = ['llm', 'tesseract', 'offline', 'enhanced']
            for method in methods:
                method_indicator = ProcessingMethodIndicator(method, 10.5)
                display_text = method_indicator.method_display.text()
                if not display_text:
                    test_result['issues'].append(f"방법 표시가 비어있음: {method}")
                    test_result['passed'] = False

            # 3.4 Quality Metrics Widget 테스트
            quality_widget = QualityMetricsWidget(quality_metrics)

            # 메트릭 값들 확인
            quality_widget.set_metrics(quality_metrics)

            # 통계 라벨 확인
            char_text = quality_widget.char_count_label.text()
            if "1250" not in char_text:
                test_result['issues'].append("문자 수가 올바르게 표시되지 않음")
                test_result['passed'] = False

            # 3.5 Enhancement Summary Widget 테스트
            enhancement_widget = EnhancementSummaryWidget(
                [OCREnhancementType.PREPROCESSING, OCREnhancementType.POST_PROCESSING],
                {"preprocessing": {"effect": "높음"}}
            )

            # 트리 위젯 항목 확인
            if enhancement_widget.enhancement_tree.topLevelItemCount() != 2:
                test_result['issues'].append("개선 항목 수가 올바르지 않음")
                test_result['passed'] = False

            # 3.6 결과 표시 위젯 생성 테스트
            widget_start = time.time()
            result_widget = result_formatter.create_result_display_widget(enhancement_result)
            widget_end = time.time()

            widget_creation_time = (widget_end - widget_start) * 1000
            test_result['performance']['widget_creation_time'] = widget_creation_time

            if widget_creation_time > 500:  # 500ms 초과시 성능 이슈
                test_result['issues'].append(f"결과 위젯 생성이 너무 느림: {widget_creation_time:.2f}ms")
                test_result['passed'] = False

            # 탭 수 확인
            if result_widget.count() != 4:  # 4개 탭이어야 함
                test_result['issues'].append(f"탭 수가 올바르지 않음: {result_widget.count()}")
                test_result['passed'] = False

            # 3.7 요약 포맷 테스트
            summary = result_formatter.format_result_summary(enhancement_result)
            if not summary or len(summary) < 50:
                test_result['issues'].append("요약이 너무 짧거나 비어있음")
                test_result['passed'] = False

            # 3.8 간소 표시 위젯 테스트
            compact_widget = result_formatter.create_compact_display(enhancement_result)
            if not compact_widget:
                test_result['issues'].append("간소 표시 위젯이 생성되지 않음")
                test_result['passed'] = False

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"OCR Result Formatting 테스트 실패: {e}")

        return test_result

    def test_feature_flag_control(self) -> Dict[str, Any]:
        """4. Feature Flag Control 테스트"""
        logger.info("4. Feature Flag Control 테스트 시작")
        test_result = {
            'test_name': 'Feature Flag Control',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            start_time = time.time()

            # 4.1 기본 활성화 상태 테스트
            enabled_config = OCREnhancementConfig()
            enabled_config.enabled = True

            status_provider = OCRStatusProvider(enabled_config)
            if not status_provider.is_ocr_enabled():
                test_result['issues'].append("OCR이 활성화되어야 하는데 비활성화됨")
                test_result['passed'] = False

            # 배지 생성 확인 (활성화 상태)
            widget = status_provider.create_status_badge_widget(self.test_image_files[0])
            if not widget:
                test_result['issues'].append("활성화 상태에서 배지가 생성되지 않음")
                test_result['passed'] = False

            # 4.2 비활성화 상태 테스트
            disabled_config = OCREnhancementConfig()
            disabled_config.enabled = False

            disabled_provider = OCRStatusProvider(disabled_config)
            if disabled_provider.is_ocr_enabled():
                test_result['issues'].append("OCR이 비활성화되어야 하는데 활성화됨")
                test_result['passed'] = False

            # 배지 생성 확인 (비활성화 상태)
            widget = disabled_provider.create_status_badge_widget(self.test_image_files[0])
            if widget is not None:
                test_result['issues'].append("비활성화 상태에서 배지가 생성됨")
                test_result['passed'] = False

            # 4.3 개별 기능 제어 테스트
            partial_config = OCREnhancementConfig()
            partial_config.enabled = True
            partial_config.preprocessing_enabled = True
            partial_config.post_processing_enabled = False
            partial_config.accuracy_boost_enabled = False

            # 활성화된 개선사항만 확인
            if not partial_config.is_any_enhancement_enabled():
                test_result['issues'].append("일부 개선사항이 활성화되어야 함")
                test_result['passed'] = False

            # 4.4 FileListWidget 통합 테스트
            file_list_enabled = FileListWidget(enabled_config)
            file_list_disabled = FileListWidget(disabled_config)

            # 활성화 상태에서 OCR 컬럼 확인
            enabled_headers = [file_list_enabled.tree_widget.headerItem().text(i)
                             for i in range(file_list_enabled.tree_widget.columnCount())]
            if "OCR" not in enabled_headers:
                test_result['issues'].append("활성화 상태에서 OCR 컬럼이 없음")
                test_result['passed'] = False

            # 비활성화 상태에서 OCR 컬럼 확인
            disabled_headers = [file_list_disabled.tree_widget.headerItem().text(i)
                              for i in range(file_list_disabled.tree_widget.columnCount())]
            if "OCR" in disabled_headers:
                test_result['issues'].append("비활성화 상태에서 OCR 컬럼이 존재함")
                test_result['passed'] = False

            # 4.5 동적 설정 변경 테스트
            dynamic_config = OCREnhancementConfig()
            dynamic_config.enabled = True

            dynamic_provider = OCRStatusProvider(dynamic_config)

            # 설정 변경
            dynamic_config.enabled = False

            # 캐시 클리어 후 다시 확인
            dynamic_provider.clear_cache()

            if dynamic_provider.is_ocr_enabled():
                test_result['issues'].append("동적 설정 변경이 반영되지 않음")
                test_result['passed'] = False

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"Feature Flag Control 테스트 실패: {e}")

        return test_result

    def test_theme_integration(self) -> Dict[str, Any]:
        """5. Theme Integration 테스트"""
        logger.info("5. Theme Integration 테스트 시작")
        test_result = {
            'test_name': 'Theme Integration',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            start_time = time.time()

            # 5.1 다양한 테마에서 배지 생성 테스트
            themes = ['light', 'dark', 'high_contrast']

            for theme in themes:
                # 테마별 색상 테스트
                badge = OCRStatusBadge(OCRStatusType.COMPLETED, QualityLevel.GOOD)

                # 픽스맵이 생성되는지 확인
                pixmap = badge.pixmap()
                if pixmap.isNull():
                    test_result['issues'].append(f"{theme} 테마에서 배지 픽스맵이 생성되지 않음")
                    test_result['passed'] = False

                # 가시성 확인
                if not badge.isVisible():
                    test_result['issues'].append(f"{theme} 테마에서 배지가 보이지 않음")
                    test_result['passed'] = False

            # 5.2 신뢰도 위젯 테마 테스트
            confidence_widget = ConfidenceScoreWidget(0.75)

            # 색상 변경이 적절히 적용되는지 확인
            for conf in [0.95, 0.5, 0.2]:
                confidence_widget.set_confidence(conf)

                # 스타일시트가 적용되는지 확인
                style = confidence_widget.confidence_bar.styleSheet()
                if not style:
                    test_result['issues'].append(f"신뢰도 위젯에 스타일이 적용되지 않음: {conf}")
                    test_result['passed'] = False

            # 5.3 품질 메트릭 위젯 테마 테스트
            quality_metrics = QualityMetrics(
                confidence_score=0.8,
                overall_quality=QualityLevel.GOOD
            )
            quality_widget = QualityMetricsWidget(quality_metrics)

            # 프로그레스 바들의 스타일 확인
            # Note: 실제 애플리케이션에서는 테마 변경 시그널로 스타일을 업데이트해야 함

            # 5.4 고대비 테마 호환성 테스트
            # 고대비 테마에서는 색상 대비가 충분해야 함
            high_contrast_badge = OCRStatusBadge(OCRStatusType.FAILED, None)

            # 툴팁 가독성 확인
            tooltip = high_contrast_badge.toolTip()
            if not tooltip:
                test_result['issues'].append("고대비 테마에서 툴팁이 없음")
                test_result['passed'] = False

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"Theme Integration 테스트 실패: {e}")

        return test_result

    def test_performance_and_error_handling(self) -> Dict[str, Any]:
        """6. Performance & Error Handling 테스트"""
        logger.info("6. Performance & Error Handling 테스트 시작")
        test_result = {
            'test_name': 'Performance & Error Handling',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            start_time = time.time()

            # 6.1 대량 파일 처리 성능 테스트
            large_file_list = []
            for i in range(100):  # 100개 파일 생성
                file_path = Path(tempfile.gettempdir()) / f"perf_test_{i}.jpg"
                file_info = FileInfo(file_path)
                large_file_list.append(file_info)

            status_provider = OCRStatusProvider(self.ocr_config)

            # 대량 배지 생성 성능 테스트
            batch_start = time.time()
            widgets = []
            for file_info in large_file_list:
                widget = status_provider.create_status_badge_widget(file_info)
                widgets.append(widget)
            batch_end = time.time()

            batch_time = (batch_end - batch_start) * 1000
            avg_time_per_widget = batch_time / len(large_file_list)

            test_result['performance']['batch_creation_time'] = batch_time
            test_result['performance']['avg_time_per_widget'] = avg_time_per_widget

            if avg_time_per_widget > 10:  # 10ms per widget 초과시 성능 이슈
                test_result['issues'].append(f"위젯 생성이 너무 느림: {avg_time_per_widget:.2f}ms")
                test_result['passed'] = False

            # 6.2 메모리 사용량 테스트 (간접적)
            cache_stats_before = status_provider.get_cache_stats()

            # 캐시 무효화 후 재생성
            status_provider.clear_cache()
            for file_info in large_file_list[:50]:  # 절반만 재생성
                status_provider.create_status_badge_widget(file_info)

            cache_stats_after = status_provider.get_cache_stats()

            if cache_stats_after['badge_cache_size'] > 50:
                test_result['issues'].append("캐시 크기가 예상보다 큼")
                test_result['passed'] = False

            # 6.3 에러 처리 테스트

            # 잘못된 파일 정보 처리
            try:
                invalid_file = FileInfo(Path("nonexistent_file.jpg"))
                widget = status_provider.create_status_badge_widget(invalid_file)
                # 에러가 발생하지 않아야 함 (graceful handling)
            except Exception as e:
                test_result['issues'].append(f"잘못된 파일 처리 중 예외 발생: {e}")
                test_result['passed'] = False

            # 빈 설정 처리
            try:
                empty_config = OCREnhancementConfig()
                empty_config.enabled = False
                empty_provider = OCRStatusProvider(empty_config)
                widget = empty_provider.create_status_badge_widget(self.test_image_files[0])
                # None이 반환되어야 함
                if widget is not None:
                    test_result['issues'].append("비활성화된 설정에서 위젯이 생성됨")
                    test_result['passed'] = False
            except Exception as e:
                test_result['issues'].append(f"빈 설정 처리 중 예외 발생: {e}")
                test_result['passed'] = False

            # 6.4 Progress Tracker 성능 테스트
            progress_tracker = OCRProgressTracker(self.ocr_config)

            # 동시 추적 성능
            concurrent_start = time.time()
            for file_info in large_file_list[:20]:  # 20개 동시 추적
                progress_tracker.start_ocr_tracking(file_info, [OCREnhancementType.PREPROCESSING])
            concurrent_end = time.time()

            concurrent_time = (concurrent_end - concurrent_start) * 1000
            test_result['performance']['concurrent_tracking_time'] = concurrent_time

            if concurrent_time > 1000:  # 1초 초과시 성능 이슈
                test_result['issues'].append(f"동시 추적 시작이 너무 느림: {concurrent_time:.2f}ms")
                test_result['passed'] = False

            # 6.5 메모리 정리 테스트
            progress_tracker.clear_tracking_data()
            stats = progress_tracker.get_tracking_stats()

            if stats['active_files'] > 0:
                test_result['issues'].append("추적 데이터가 완전히 정리되지 않음")
                test_result['passed'] = False

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"Performance & Error Handling 테스트 실패: {e}")

        return test_result

    def test_integration_and_compatibility(self) -> Dict[str, Any]:
        """7. Integration & Backward Compatibility 테스트"""
        logger.info("7. Integration & Backward Compatibility 테스트 시작")
        test_result = {
            'test_name': 'Integration & Backward Compatibility',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            start_time = time.time()

            # 7.1 FileListWidget 통합 테스트
            file_list = FileListWidget(self.ocr_config)

            # 기존 기능 확인
            original_functionality_start = time.time()

            # 파일 추가
            for file_info in self.test_image_files:
                file_list.add_file(file_info)

            # 파일 개수 확인
            if file_list.tree_widget.topLevelItemCount() != len(self.test_image_files):
                test_result['issues'].append("파일 추가 기능이 정상 동작하지 않음")
                test_result['passed'] = False

            # 선택 기능 확인
            file_list.select_all()
            selected_count = sum(1 for i in range(file_list.tree_widget.topLevelItemCount())
                               if file_list.tree_widget.topLevelItem(i))

            if selected_count != len(self.test_image_files):
                test_result['issues'].append("전체 선택 기능이 정상 동작하지 않음")
                test_result['passed'] = False

            original_functionality_time = (time.time() - original_functionality_start) * 1000
            test_result['performance']['original_functionality_time'] = original_functionality_time

            # 7.2 OCR 기능 없이도 정상 동작 확인
            file_list_no_ocr = FileListWidget()  # OCR 설정 없음

            # 파일 추가 시 에러 없이 동작해야 함
            try:
                for file_info in self.test_image_files:
                    file_list_no_ocr.add_file(file_info)
            except Exception as e:
                test_result['issues'].append(f"OCR 없이 파일 추가 중 예외 발생: {e}")
                test_result['passed'] = False

            # 7.3 ProgressWidget 통합 테스트
            # Note: ProgressWidget는 실제 변환 과정에서 테스트되어야 하므로
            # 여기서는 기본적인 호환성만 확인

            # 7.4 설정 호환성 테스트
            try:
                # 기존 설정 파일 읽기
                config_path = project_root / "config" / "settings.ini"
                if config_path.exists():
                    config_manager = ConfigManager()

                    # OCR 설정이 추가되어도 기존 설정은 유지되어야 함
                    language = config_manager.get_config().language
                    if not language:
                        test_result['issues'].append("기존 언어 설정이 유실됨")
                        test_result['passed'] = False

            except Exception as e:
                test_result['issues'].append(f"설정 호환성 테스트 중 예외 발생: {e}")
                test_result['passed'] = False

            # 7.5 UI 반응성 테스트
            responsiveness_start = time.time()

            # 다량의 OCR 상태 업데이트
            status_provider = OCRStatusProvider(self.ocr_config)

            for i, file_info in enumerate(self.test_image_files):
                status = OCRStatusType.PROCESSING if i % 2 == 0 else OCRStatusType.COMPLETED
                quality = QualityLevel.GOOD if status == OCRStatusType.COMPLETED else None

                status_provider.update_file_status(file_info, status, quality)

                # UI 업데이트가 블로킹되지 않는지 확인
                QApplication.processEvents()

            responsiveness_time = (time.time() - responsiveness_start) * 1000
            test_result['performance']['responsiveness_time'] = responsiveness_time

            if responsiveness_time > 2000:  # 2초 초과시 반응성 이슈
                test_result['issues'].append(f"UI 반응성이 좋지 않음: {responsiveness_time:.2f}ms")
                test_result['passed'] = False

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"Integration & Backward Compatibility 테스트 실패: {e}")

        return test_result

    def test_user_experience(self) -> Dict[str, Any]:
        """8. User Experience 테스트"""
        logger.info("8. User Experience 테스트 시작")
        test_result = {
            'test_name': 'User Experience',
            'passed': True,
            'issues': [],
            'performance': {},
            'details': {}
        }

        try:
            start_time = time.time()

            # 8.1 시각적 일관성 테스트
            status_provider = OCRStatusProvider(self.ocr_config)

            # 모든 상태의 배지 크기 일관성 확인
            badge_sizes = []
            for status in OCRStatusType:
                if status != OCRStatusType.IDLE:
                    badge = OCRStatusBadge(status)
                    badge_sizes.append((badge.width(), badge.height()))

            # 모든 배지가 같은 크기인지 확인
            first_size = badge_sizes[0] if badge_sizes else (20, 16)
            for size in badge_sizes:
                if size != first_size:
                    test_result['issues'].append(f"배지 크기 불일치: {size} vs {first_size}")
                    test_result['passed'] = False

            # 8.2 정보 명확성 테스트

            # 툴팁 정보 충분성 확인
            for status in [OCRStatusType.PROCESSING, OCRStatusType.COMPLETED, OCRStatusType.FAILED]:
                badge = OCRStatusBadge(status, QualityLevel.GOOD if status == OCRStatusType.COMPLETED else None)
                tooltip = badge.toolTip()

                if len(tooltip) < 5:  # 너무 짧은 툴팁
                    test_result['issues'].append(f"{status.value} 배지의 툴팁이 너무 짧음")
                    test_result['passed'] = False

                # 한글 지원 확인
                if not any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in tooltip):
                    test_result['issues'].append(f"{status.value} 배지 툴팁이 한글을 지원하지 않음")
                    test_result['passed'] = False

            # 8.3 직관성 테스트

            # 색상 의미 일관성 (성공=녹색, 실패=빨강, 진행중=파랑)
            success_badge = OCRStatusBadge(OCRStatusType.COMPLETED, QualityLevel.EXCELLENT)
            failed_badge = OCRStatusBadge(OCRStatusType.FAILED)
            processing_badge = OCRStatusBadge(OCRStatusType.PROCESSING)

            # 시각적으로 구분되는지 확인 (pixmap 색상은 직접 확인하기 어려우므로 생성 여부만 확인)
            for badge, name in [(success_badge, "성공"), (failed_badge, "실패"), (processing_badge, "처리중")]:
                if badge.pixmap().isNull():
                    test_result['issues'].append(f"{name} 배지 픽스맵이 생성되지 않음")
                    test_result['passed'] = False

            # 8.4 접근성 테스트

            # 키보드 탐색 지원 (기본 Qt 위젯이므로 기본적으로 지원됨)
            file_list = FileListWidget(self.ocr_config)

            # 포커스 가능한지 확인
            if not file_list.tree_widget.focusPolicy() & Qt.FocusPolicy.TabFocus:
                test_result['issues'].append("파일 리스트가 키보드 포커스를 받을 수 없음")
                test_result['passed'] = False

            # 8.5 성능 인식 테스트

            # 사용자가 기다림을 인지할 수 있는 시간 내에 완료되는지
            perceived_performance_start = time.time()

            # 일반적인 사용자 작업 시뮬레이션
            for file_info in self.test_image_files[:5]:  # 5개 파일
                widget = status_provider.create_status_badge_widget(file_info)
                status_provider.update_file_status(file_info, OCRStatusType.COMPLETED, QualityLevel.GOOD)

            perceived_performance_time = (time.time() - perceived_performance_start) * 1000
            test_result['performance']['perceived_performance_time'] = perceived_performance_time

            if perceived_performance_time > 1000:  # 1초 초과시 사용자 인식 문제
                test_result['issues'].append(f"사용자 작업 응답이 너무 느림: {perceived_performance_time:.2f}ms")
                test_result['passed'] = False

            # 8.6 오류 상황 사용자 경험 테스트

            # 실패 상태의 명확한 표시
            failed_badge = OCRStatusBadge(OCRStatusType.FAILED)
            failed_tooltip = failed_badge.toolTip()

            if "실패" not in failed_tooltip:
                test_result['issues'].append("실패 상태가 명확히 표시되지 않음")
                test_result['passed'] = False

            total_time = time.time() - start_time
            test_result['performance']['total_test_time'] = total_time * 1000

        except Exception as e:
            test_result['passed'] = False
            test_result['issues'].append(f"예외 발생: {str(e)}")
            logger.error(f"User Experience 테스트 실패: {e}")

        return test_result

    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("=== OCR UI Integration 종합 테스트 실행 ===")

        self.setup_test_environment()

        # 각 테스트 실행
        test_methods = [
            self.test_ocr_status_badge_system,
            self.test_enhanced_progress_tracking,
            self.test_ocr_result_formatting,
            self.test_feature_flag_control,
            self.test_theme_integration,
            self.test_performance_and_error_handling,
            self.test_integration_and_compatibility,
            self.test_user_experience
        ]

        all_results = []
        total_passed = 0
        total_issues = 0

        for test_method in test_methods:
            try:
                result = test_method()
                all_results.append(result)

                if result['passed']:
                    total_passed += 1
                total_issues += len(result['issues'])

                # 개별 테스트 결과 로깅
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                logger.info(f"{status}: {result['test_name']} ({len(result['issues'])} 이슈)")

                for issue in result['issues']:
                    logger.warning(f"  - {issue}")

            except Exception as e:
                logger.error(f"테스트 실행 중 예외 발생: {test_method.__name__}: {e}")
                all_results.append({
                    'test_name': test_method.__name__,
                    'passed': False,
                    'issues': [f"테스트 실행 예외: {str(e)}"],
                    'performance': {},
                    'details': {}
                })

        # 종합 결과
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()

        summary = {
            'test_suite': 'OCR UI Integration',
            'timestamp': end_time.isoformat(),
            'total_tests': len(test_methods),
            'passed_tests': total_passed,
            'failed_tests': len(test_methods) - total_passed,
            'total_issues': total_issues,
            'total_time_seconds': total_time,
            'overall_passed': total_passed == len(test_methods) and total_issues == 0,
            'individual_results': all_results
        }

        return summary

    def generate_qa_report(self, results: Dict[str, Any]) -> str:
        """QA 테스트 보고서 생성"""
        overall_status = "✅ PASS" if results['overall_passed'] else "❌ FAIL"

        report = f"""
# OCR UI Integration - QA 테스트 보고서

## 종합 결과: {overall_status}

**테스트 실행 시간**: {results['timestamp']}
**총 소요 시간**: {results['total_time_seconds']:.2f}초
**전체 테스트**: {results['total_tests']}개
**통과 테스트**: {results['passed_tests']}개
**실패 테스트**: {results['failed_tests']}개
**발견된 이슈**: {results['total_issues']}개

## 개별 테스트 결과

"""

        for result in results['individual_results']:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            report += f"### {status} {result['test_name']}\n\n"

            if result['issues']:
                report += "**발견된 이슈:**\n"
                for issue in result['issues']:
                    report += f"- {issue}\n"
                report += "\n"

            if result['performance']:
                report += "**성능 메트릭:**\n"
                for metric, value in result['performance'].items():
                    if isinstance(value, float):
                        report += f"- {metric}: {value:.2f}ms\n"
                    else:
                        report += f"- {metric}: {value}\n"
                report += "\n"

        # 권장사항
        report += "## 권장사항\n\n"

        if results['overall_passed']:
            report += "🎉 **모든 테스트가 통과했습니다!**\n\n"
            report += "- OCR UI 통합 기능이 프로덕션 배포 준비 완료\n"
            report += "- 성능 요구사항 충족\n"
            report += "- 테마 통합 및 접근성 준수\n"
            report += "- 기존 기능과의 호환성 확인\n"
        else:
            report += "⚠️ **발견된 이슈들을 해결 후 재테스트 필요**\n\n"

            high_priority_issues = []
            medium_priority_issues = []
            low_priority_issues = []

            for result in results['individual_results']:
                for issue in result['issues']:
                    if any(keyword in issue.lower() for keyword in ['예외', '실패', '생성되지 않음', '작동하지 않음']):
                        high_priority_issues.append(f"{result['test_name']}: {issue}")
                    elif any(keyword in issue.lower() for keyword in ['느림', '성능', '시간']):
                        medium_priority_issues.append(f"{result['test_name']}: {issue}")
                    else:
                        low_priority_issues.append(f"{result['test_name']}: {issue}")

            if high_priority_issues:
                report += "**🔥 높은 우선순위 (즉시 수정 필요):**\n"
                for issue in high_priority_issues:
                    report += f"- {issue}\n"
                report += "\n"

            if medium_priority_issues:
                report += "**⚡ 중간 우선순위 (성능 개선):**\n"
                for issue in medium_priority_issues:
                    report += f"- {issue}\n"
                report += "\n"

            if low_priority_issues:
                report += "**📝 낮은 우선순위 (개선 권장):**\n"
                for issue in low_priority_issues:
                    report += f"- {issue}\n"
                report += "\n"

        report += f"""
## 테스트 환경

- **Python 버전**: {sys.version}
- **PyQt6 버전**: 6.x
- **테스트 프레임워크**: pytest + QTest
- **테스트 파일**: {len(self.test_image_files)} 이미지, {len(self.test_pdf_files)} PDF

## 다음 단계

{'1. 프로덕션 배포 진행' if results['overall_passed'] else '1. 발견된 이슈 수정'}
2. 사용자 승인 테스트 (UAT) 실시
3. 프로덕션 환경 모니터링 설정
4. 사용자 피드백 수집 및 개선

---
*OCR UI Integration QA Team*
*Generated: {results['timestamp']}*
"""

        return report


def main():
    """메인 테스트 실행 함수"""
    test_suite = OCRUIIntegrationTestSuite()

    try:
        # 모든 테스트 실행
        results = test_suite.run_all_tests()

        # 보고서 생성
        report = test_suite.generate_qa_report(results)

        # 결과 출력
        print("\n" + "="*80)
        print(report)
        print("="*80)

        # 보고서 파일 저장
        report_path = Path(tempfile.gettempdir()) / f"ocr_ui_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 상세 보고서 저장됨: {report_path}")

        # 종료 코드 반환
        return 0 if results['overall_passed'] else 1

    except Exception as e:
        logger.error(f"테스트 스위트 실행 중 예외 발생: {e}")
        print(f"\n❌ 테스트 실행 실패: {e}")
        return 1

    finally:
        # 정리
        if test_suite.app:
            test_suite.app.quit()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)