"""
OCR Result Formatter
OCR 결과 포맷터

Formats OCR results for display in UI components.
Provides confidence score display, processing method indicators, and quality metrics.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTextEdit, QProgressBar, QGroupBox, QScrollArea,
    QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCharFormat, QTextCursor
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models import (
    OCREnhancementResult, QualityMetrics, QualityLevel,
    OCREnhancementType, LayoutInfo, OCRStatusInfo
)
from ...models import FileInfo, OCRResult
from ...logger import get_logger

logger = get_logger(__name__)


class ConfidenceScoreWidget(QWidget):
    """신뢰도 점수 표시 위젯"""

    def __init__(self, confidence: float = 0.0):
        super().__init__()
        self._confidence = confidence
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 신뢰도 레이블
        self.confidence_label = QLabel("신뢰도:")
        self.confidence_label.setFont(QFont("맑은 고딕", 9))
        layout.addWidget(self.confidence_label)

        # 신뢰도 프로그레스 바
        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMinimum(0)
        self.confidence_bar.setMaximum(100)
        self.confidence_bar.setFixedHeight(16)
        self.confidence_bar.setTextVisible(True)
        layout.addWidget(self.confidence_bar)

        # 신뢰도 품질 표시
        self.quality_label = QLabel("")
        self.quality_label.setFont(QFont("맑은 고딕", 8))
        layout.addWidget(self.quality_label)

        self._update_display()

    def set_confidence(self, confidence: float):
        """신뢰도 설정"""
        self._confidence = max(0.0, min(1.0, confidence))
        self._update_display()

    def _update_display(self):
        """디스플레이 업데이트"""
        percentage = int(self._confidence * 100)
        self.confidence_bar.setValue(percentage)
        self.confidence_bar.setFormat(f"{percentage}%")

        # 신뢰도별 색상 및 라벨
        quality_info = self._get_quality_info(self._confidence)

        self.confidence_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {quality_info['color']};
                border-radius: 2px;
            }}
            QProgressBar {{
                border: 1px solid #CCCCCC;
                border-radius: 2px;
                text-align: center;
                font-size: 9px;
            }}
        """)

        self.quality_label.setText(quality_info['label'])
        self.quality_label.setStyleSheet(f"color: {quality_info['color']};")

    def _get_quality_info(self, confidence: float) -> Dict[str, str]:
        """신뢰도별 품질 정보"""
        if confidence >= 0.95:
            return {'color': '#2E7D32', 'label': '최고'}
        elif confidence >= 0.80:
            return {'color': '#4CAF50', 'label': '좋음'}
        elif confidence >= 0.60:
            return {'color': '#FF9800', 'label': '보통'}
        elif confidence >= 0.40:
            return {'color': '#F57C00', 'label': '낮음'}
        else:
            return {'color': '#D32F2F', 'label': '매우낮음'}


class ProcessingMethodIndicator(QWidget):
    """처리 방법 표시기"""

    def __init__(self, method: str = "", processing_time: float = 0.0):
        super().__init__()
        self._method = method
        self._processing_time = processing_time
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 방법 레이블
        self.method_label = QLabel("처리 방법:")
        self.method_label.setFont(QFont("맑은 고딕", 9))
        layout.addWidget(self.method_label)

        # 방법 표시
        self.method_display = QLabel(self._get_method_display(self._method))
        self.method_display.setFont(QFont("맑은 고딕", 9, QFont.Weight.Bold))
        layout.addWidget(self.method_display)

        layout.addStretch()

        # 처리 시간
        self.time_label = QLabel(f"처리 시간: {self._processing_time:.2f}초")
        self.time_label.setFont(QFont("맑은 고딕", 8))
        self.time_label.setStyleSheet("color: #666;")
        layout.addWidget(self.time_label)

    def set_method(self, method: str, processing_time: float = 0.0):
        """방법 설정"""
        self._method = method
        self._processing_time = processing_time

        self.method_display.setText(self._get_method_display(method))
        self.time_label.setText(f"처리 시간: {processing_time:.2f}초")

        # 방법별 색상
        color = self._get_method_color(method)
        self.method_display.setStyleSheet(f"color: {color};")

    def _get_method_display(self, method: str) -> str:
        """방법 표시 텍스트"""
        method_names = {
            'llm': 'LLM 기반 OCR',
            'tesseract': 'Tesseract OCR',
            'offline': '오프라인 OCR',
            'enhanced': '개선된 OCR',
            'hybrid': '하이브리드 OCR'
        }
        return method_names.get(method.lower(), method or '알 수 없음')

    def _get_method_color(self, method: str) -> str:
        """방법별 색상"""
        method_colors = {
            'llm': '#4CAF50',
            'tesseract': '#2196F3',
            'offline': '#FF9800',
            'enhanced': '#9C27B0',
            'hybrid': '#673AB7'
        }
        return method_colors.get(method.lower(), '#666666')


class QualityMetricsWidget(QWidget):
    """품질 메트릭 위젯"""

    def __init__(self, metrics: Optional[QualityMetrics] = None):
        super().__init__()
        self._metrics = metrics or QualityMetrics()
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 전체 품질 표시
        overall_layout = QHBoxLayout()
        overall_layout.addWidget(QLabel("전체 품질:"))

        self.overall_quality_label = QLabel()
        self.overall_quality_label.setFont(QFont("맑은 고딕", 10, QFont.Weight.Bold))
        overall_layout.addWidget(self.overall_quality_label)

        overall_layout.addStretch()
        layout.addLayout(overall_layout)

        # 세부 메트릭
        metrics_frame = QFrame()
        metrics_frame.setFrameStyle(QFrame.Shape.Box)
        metrics_frame.setStyleSheet("background-color: #F8F9FA; border: 1px solid #E0E0E0;")
        layout.addWidget(metrics_frame)

        metrics_layout = QVBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(8, 8, 8, 8)

        # 개별 점수들
        self.confidence_widget = self._create_metric_widget("신뢰도", self._metrics.confidence_score)
        self.clarity_widget = self._create_metric_widget("명확성", self._metrics.clarity_score)
        self.completeness_widget = self._create_metric_widget("완전성", self._metrics.completeness_score)
        self.consistency_widget = self._create_metric_widget("일관성", self._metrics.consistency_score)

        for widget in [self.confidence_widget, self.clarity_widget,
                      self.completeness_widget, self.consistency_widget]:
            metrics_layout.addWidget(widget)

        # 통계 정보
        stats_layout = QHBoxLayout()

        self.char_count_label = QLabel(f"문자: {self._metrics.character_count}")
        self.word_count_label = QLabel(f"단어: {self._metrics.word_count}")
        self.line_count_label = QLabel(f"줄: {self._metrics.line_count}")

        for label in [self.char_count_label, self.word_count_label, self.line_count_label]:
            label.setFont(QFont("맑은 고딕", 8))
            label.setStyleSheet("color: #666;")
            stats_layout.addWidget(label)

        stats_layout.addStretch()
        metrics_layout.addLayout(stats_layout)

        self._update_display()

    def _create_metric_widget(self, name: str, score: float) -> QWidget:
        """메트릭 위젯 생성"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 2, 0, 2)

        # 이름
        name_label = QLabel(f"{name}:")
        name_label.setFont(QFont("맑은 고딕", 9))
        name_label.setFixedWidth(60)
        layout.addWidget(name_label)

        # 점수 바
        score_bar = QProgressBar()
        score_bar.setMinimum(0)
        score_bar.setMaximum(100)
        score_bar.setValue(int(score * 100))
        score_bar.setFixedHeight(14)
        score_bar.setTextVisible(True)
        score_bar.setFormat(f"{score:.1%}")

        # 점수별 색상
        color = self._get_score_color(score)
        score_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
            QProgressBar {{
                border: 1px solid #CCCCCC;
                border-radius: 2px;
                text-align: center;
                font-size: 8px;
            }}
        """)

        layout.addWidget(score_bar)

        return widget

    def set_metrics(self, metrics: QualityMetrics):
        """메트릭 설정"""
        self._metrics = metrics
        self._update_display()

    def _update_display(self):
        """디스플레이 업데이트"""
        # 전체 품질 업데이트
        quality_info = self._get_quality_display_info(self._metrics.overall_quality)
        self.overall_quality_label.setText(quality_info['text'])
        self.overall_quality_label.setStyleSheet(f"color: {quality_info['color']};")

        # 통계 업데이트
        self.char_count_label.setText(f"문자: {self._metrics.character_count}")
        self.word_count_label.setText(f"단어: {self._metrics.word_count}")
        self.line_count_label.setText(f"줄: {self._metrics.line_count}")

    def _get_score_color(self, score: float) -> str:
        """점수별 색상"""
        if score >= 0.90:
            return '#2E7D32'
        elif score >= 0.70:
            return '#4CAF50'
        elif score >= 0.50:
            return '#FF9800'
        elif score >= 0.30:
            return '#F57C00'
        else:
            return '#D32F2F'

    def _get_quality_display_info(self, quality: QualityLevel) -> Dict[str, str]:
        """품질 표시 정보"""
        quality_info = {
            QualityLevel.EXCELLENT: {'text': '최고 품질', 'color': '#2E7D32'},
            QualityLevel.GOOD: {'text': '좋은 품질', 'color': '#4CAF50'},
            QualityLevel.FAIR: {'text': '보통 품질', 'color': '#FF9800'},
            QualityLevel.POOR: {'text': '낮은 품질', 'color': '#F57C00'},
            QualityLevel.VERY_POOR: {'text': '매우 낮은 품질', 'color': '#D32F2F'}
        }
        return quality_info.get(quality, {'text': '알 수 없음', 'color': '#666666'})


class EnhancementSummaryWidget(QWidget):
    """개선 요약 위젯"""

    def __init__(self, enhancements: List[OCREnhancementType] = None):
        super().__init__()
        self._enhancements = enhancements or []
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 제목
        title_label = QLabel("적용된 개선사항")
        title_label.setFont(QFont("맑은 고딕", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # 개선 목록
        self.enhancement_tree = QTreeWidget()
        self.enhancement_tree.setHeaderLabels(["개선 유형", "설명", "효과"])
        self.enhancement_tree.setFixedHeight(120)
        layout.addWidget(self.enhancement_tree)

        self._update_display()

    def set_enhancements(self, enhancements: List[OCREnhancementType],
                        enhancement_details: Dict[str, Any] = None):
        """개선사항 설정"""
        self._enhancements = enhancements
        self._enhancement_details = enhancement_details or {}
        self._update_display()

    def _update_display(self):
        """디스플레이 업데이트"""
        self.enhancement_tree.clear()

        if not self._enhancements:
            item = QTreeWidgetItem(["개선사항 없음", "기본 OCR 처리만 적용됨", ""])
            self.enhancement_tree.addTopLevelItem(item)
            return

        for enhancement in self._enhancements:
            info = self._get_enhancement_info(enhancement)
            item = QTreeWidgetItem([info['name'], info['description'], info['effect']])
            self.enhancement_tree.addTopLevelItem(item)

        # 컬럼 크기 조정
        self.enhancement_tree.resizeColumnToContents(0)
        self.enhancement_tree.resizeColumnToContents(1)
        self.enhancement_tree.resizeColumnToContents(2)

    def _get_enhancement_info(self, enhancement: OCREnhancementType) -> Dict[str, str]:
        """개선 정보"""
        enhancement_info = {
            OCREnhancementType.ACCURACY_BOOST: {
                'name': '정확도 향상',
                'description': 'AI 모델을 이용한 텍스트 정확도 개선',
                'effect': '높음'
            },
            OCREnhancementType.PREPROCESSING: {
                'name': '이미지 전처리',
                'description': '이미지 품질 개선 및 노이즈 제거',
                'effect': '중간'
            },
            OCREnhancementType.POST_PROCESSING: {
                'name': '텍스트 후처리',
                'description': '맞춤법 검사 및 형식 정리',
                'effect': '중간'
            },
            OCREnhancementType.LANGUAGE_DETECTION: {
                'name': '언어 감지',
                'description': '자동 언어 인식 및 최적화',
                'effect': '낮음'
            },
            OCREnhancementType.CONFIDENCE_ANALYSIS: {
                'name': '신뢰도 분석',
                'description': '결과 신뢰도 평가 및 개선',
                'effect': '낮음'
            },
            OCREnhancementType.LAYOUT_ANALYSIS: {
                'name': '레이아웃 분석',
                'description': '문서 구조 인식 및 순서 복원',
                'effect': '높음'
            },
            OCREnhancementType.QUALITY_ASSESSMENT: {
                'name': '품질 평가',
                'description': '결과 품질 측정 및 리포팅',
                'effect': '낮음'
            }
        }

        return enhancement_info.get(enhancement, {
            'name': enhancement.value,
            'description': '알 수 없는 개선사항',
            'effect': '알 수 없음'
        })


class OCRResultFormatter(QObject):
    """OCR 결과 포맷터"""

    # 시그널
    format_requested = pyqtSignal(OCREnhancementResult)

    def __init__(self):
        super().__init__()
        logger.debug("OCRResultFormatter 초기화됨")

    def create_result_display_widget(self, result: OCREnhancementResult) -> QWidget:
        """결과 표시 위젯 생성"""
        widget = QTabWidget()

        # 기본 정보 탭
        basic_tab = self._create_basic_info_tab(result)
        widget.addTab(basic_tab, "기본 정보")

        # 품질 메트릭 탭
        quality_tab = self._create_quality_metrics_tab(result)
        widget.addTab(quality_tab, "품질 분석")

        # 개선 내역 탭
        enhancement_tab = self._create_enhancement_tab(result)
        widget.addTab(enhancement_tab, "개선 내역")

        # 텍스트 결과 탭
        text_tab = self._create_text_result_tab(result)
        widget.addTab(text_tab, "텍스트 결과")

        return widget

    def _create_basic_info_tab(self, result: OCREnhancementResult) -> QWidget:
        """기본 정보 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 파일 정보
        file_info_group = QGroupBox("파일 정보")
        file_info_layout = QVBoxLayout(file_info_group)

        file_name_label = QLabel(f"파일명: {result.file_info.name}")
        file_path_label = QLabel(f"경로: {result.file_info.path}")
        file_size_label = QLabel(f"크기: {result.file_info.size_formatted}")

        for label in [file_name_label, file_path_label, file_size_label]:
            label.setFont(QFont("맑은 고딕", 9))
            file_info_layout.addWidget(label)

        layout.addWidget(file_info_group)

        # 처리 정보
        processing_info_group = QGroupBox("처리 정보")
        processing_info_layout = QVBoxLayout(processing_info_group)

        # 처리 방법 표시기
        method = self._determine_processing_method(result)
        method_indicator = ProcessingMethodIndicator(method, result.processing_time)
        processing_info_layout.addWidget(method_indicator)

        # 신뢰도 표시
        confidence_widget = ConfidenceScoreWidget(result.quality_metrics.confidence_score)
        processing_info_layout.addWidget(confidence_widget)

        layout.addWidget(processing_info_group)

        # 상태 정보
        status_info_group = QGroupBox("상태 정보")
        status_info_layout = QVBoxLayout(status_info_group)

        status_label = QLabel(f"상태: {result.status_info.status.value}")
        timestamp_label = QLabel(f"처리 시간: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        elapsed_label = QLabel(f"소요 시간: {result.status_info.elapsed_time:.2f}초")

        for label in [status_label, timestamp_label, elapsed_label]:
            label.setFont(QFont("맑은 고딕", 9))
            status_info_layout.addWidget(label)

        layout.addWidget(status_info_group)

        layout.addStretch()
        return widget

    def _create_quality_metrics_tab(self, result: OCREnhancementResult) -> QWidget:
        """품질 메트릭 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 품질 메트릭 위젯
        quality_widget = QualityMetricsWidget(result.quality_metrics)
        layout.addWidget(quality_widget)

        # 개선 비율
        if result.improvement_ratio > 0:
            improvement_group = QGroupBox("개선 효과")
            improvement_layout = QVBoxLayout(improvement_group)

            improvement_label = QLabel(f"개선 비율: {result.improvement_ratio:.1%}")
            improvement_label.setFont(QFont("맑은 고딕", 10, QFont.Weight.Bold))
            improvement_layout.addWidget(improvement_label)

            summary_label = QLabel(result.enhancement_summary)
            summary_label.setWordWrap(True)
            improvement_layout.addWidget(summary_label)

            layout.addWidget(improvement_group)

        # 감지된 문제점 및 제안사항
        if result.quality_metrics.detected_issues or result.quality_metrics.suggestions:
            issues_group = QGroupBox("분석 결과")
            issues_layout = QVBoxLayout(issues_group)

            if result.quality_metrics.detected_issues:
                issues_label = QLabel("감지된 문제점:")
                issues_label.setFont(QFont("맑은 고딕", 9, QFont.Weight.Bold))
                issues_layout.addWidget(issues_label)

                for issue in result.quality_metrics.detected_issues:
                    issue_label = QLabel(f"• {issue}")
                    issue_label.setStyleSheet("color: #D32F2F; margin-left: 10px;")
                    issues_layout.addWidget(issue_label)

            if result.quality_metrics.suggestions:
                suggestions_label = QLabel("개선 제안:")
                suggestions_label.setFont(QFont("맑은 고딕", 9, QFont.Weight.Bold))
                issues_layout.addWidget(suggestions_label)

                for suggestion in result.quality_metrics.suggestions:
                    suggestion_label = QLabel(f"• {suggestion}")
                    suggestion_label.setStyleSheet("color: #2E7D32; margin-left: 10px;")
                    issues_layout.addWidget(suggestion_label)

            layout.addWidget(issues_group)

        layout.addStretch()
        return widget

    def _create_enhancement_tab(self, result: OCREnhancementResult) -> QWidget:
        """개선 내역 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 개선 요약 위젯
        enhancement_widget = EnhancementSummaryWidget(
            result.applied_enhancements,
            result.enhancement_details
        )
        layout.addWidget(enhancement_widget)

        # 성능 오버헤드
        if result.enhancement_overhead > 0:
            overhead_group = QGroupBox("성능 영향")
            overhead_layout = QVBoxLayout(overhead_group)

            overhead_label = QLabel(f"추가 처리 시간: {result.enhancement_overhead:.2f}초")
            base_time_label = QLabel(f"기본 처리 시간: {result.processing_time - result.enhancement_overhead:.2f}초")
            total_time_label = QLabel(f"총 처리 시간: {result.processing_time:.2f}초")

            for label in [base_time_label, overhead_label, total_time_label]:
                label.setFont(QFont("맑은 고딕", 9))
                overhead_layout.addWidget(label)

            layout.addWidget(overhead_group)

        layout.addStretch()
        return widget

    def _create_text_result_tab(self, result: OCREnhancementResult) -> QWidget:
        """텍스트 결과 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 결과 비교 (원본 vs 개선)
        if result.enhanced_text != result.original_result.text:
            splitter = QSplitter(Qt.Orientation.Horizontal)

            # 원본 결과
            original_group = QGroupBox("원본 OCR 결과")
            original_layout = QVBoxLayout(original_group)

            original_text = QTextEdit()
            original_text.setPlainText(result.original_result.text)
            original_text.setReadOnly(True)
            original_text.setFont(QFont("맑은 고딕", 9))
            original_layout.addWidget(original_text)

            splitter.addWidget(original_group)

            # 개선된 결과
            enhanced_group = QGroupBox("개선된 OCR 결과")
            enhanced_layout = QVBoxLayout(enhanced_group)

            enhanced_text = QTextEdit()
            enhanced_text.setPlainText(result.enhanced_text)
            enhanced_text.setReadOnly(True)
            enhanced_text.setFont(QFont("맑은 고딕", 9))
            enhanced_layout.addWidget(enhanced_text)

            splitter.addWidget(enhanced_group)

            layout.addWidget(splitter)
        else:
            # 단일 결과 표시
            text_group = QGroupBox("OCR 결과")
            text_layout = QVBoxLayout(text_group)

            result_text = QTextEdit()
            result_text.setPlainText(result.enhanced_text)
            result_text.setReadOnly(True)
            result_text.setFont(QFont("맑은 고딕", 9))
            text_layout.addWidget(result_text)

            layout.addWidget(text_group)

        return widget

    def format_result_summary(self, result: OCREnhancementResult) -> str:
        """결과 요약 포맷"""
        lines = []

        # 기본 정보
        lines.append(f"파일: {result.file_info.name}")
        lines.append(f"상태: {result.status_info.status.value}")
        lines.append(f"신뢰도: {result.quality_metrics.confidence_score:.1%}")

        # 품질 정보
        quality_text = self._get_quality_text(result.quality_metrics.overall_quality)
        lines.append(f"품질: {quality_text}")

        # 개선 정보
        if result.is_improved:
            lines.append(f"개선 비율: {result.improvement_ratio:.1%}")
            lines.append(f"적용된 개선: {len(result.applied_enhancements)}개")

        # 처리 시간
        lines.append(f"처리 시간: {result.processing_time:.2f}초")

        return "\n".join(lines)

    def create_compact_display(self, result: OCREnhancementResult) -> QWidget:
        """간소 표시 위젯 생성 (파일 리스트용)"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)

        # 신뢰도 표시
        confidence_widget = ConfidenceScoreWidget(result.quality_metrics.confidence_score)
        confidence_widget.setFixedHeight(20)
        layout.addWidget(confidence_widget)

        # 품질 표시
        quality_info = self._get_quality_display_info(result.quality_metrics.overall_quality)
        quality_label = QLabel(quality_info['text'])
        quality_label.setFont(QFont("맑은 고딕", 8))
        quality_label.setStyleSheet(f"color: {quality_info['color']};")
        layout.addWidget(quality_label)

        # 개선 표시
        if result.is_improved:
            improvement_label = QLabel(f"+{result.improvement_ratio:.0%}")
            improvement_label.setFont(QFont("맑은 고딕", 8, QFont.Weight.Bold))
            improvement_label.setStyleSheet("color: #4CAF50;")
            layout.addWidget(improvement_label)

        return widget

    def _determine_processing_method(self, result: OCREnhancementResult) -> str:
        """처리 방법 결정"""
        if OCREnhancementType.ACCURACY_BOOST in result.applied_enhancements:
            return 'llm'
        elif result.quality_metrics.confidence_score > 0.8:
            return 'tesseract'
        else:
            return 'offline'

    def _get_quality_text(self, quality: QualityLevel) -> str:
        """품질 텍스트"""
        quality_texts = {
            QualityLevel.EXCELLENT: '최고',
            QualityLevel.GOOD: '좋음',
            QualityLevel.FAIR: '보통',
            QualityLevel.POOR: '낮음',
            QualityLevel.VERY_POOR: '매우낮음'
        }
        return quality_texts.get(quality, '알 수 없음')

    def _get_quality_display_info(self, quality: QualityLevel) -> Dict[str, str]:
        """품질 표시 정보"""
        quality_info = {
            QualityLevel.EXCELLENT: {'text': '최고', 'color': '#2E7D32'},
            QualityLevel.GOOD: {'text': '좋음', 'color': '#4CAF50'},
            QualityLevel.FAIR: {'text': '보통', 'color': '#FF9800'},
            QualityLevel.POOR: {'text': '낮음', 'color': '#F57C00'},
            QualityLevel.VERY_POOR: {'text': '매우낮음', 'color': '#D32F2F'}
        }
        return quality_info.get(quality, {'text': '알 수 없음', 'color': '#666666'})