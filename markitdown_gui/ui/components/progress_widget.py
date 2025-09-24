"""
진행률 위젯
변환 진행 상황을 표시하는 위젯
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QPushButton, QGroupBox, QScrollArea, QFrame,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QSplitter,
    QSizePolicy, QStackedWidget, QToolButton, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPalette, QIcon, QFont, QPainter, QColor, QBrush, QPixmap

from ...core.models import (
    ConversionProgress, ConversionProgressStatus, FileConflictStatus,
    FileInfo, ConversionStatus
)
from ...core.logger import get_logger
from typing import Dict, List, Optional
from datetime import datetime

# OCR Enhancement imports (optional, only if feature is enabled)
try:
    from ...core.ocr_enhancements.ui_integrations import OCRProgressTracker
    from ...core.ocr_enhancements.models import OCREnhancementConfig, OCRStatusType
    OCR_PROGRESS_AVAILABLE = True
except ImportError:
    OCR_PROGRESS_AVAILABLE = False


logger = get_logger(__name__)


class StatusIcon(QLabel):
    """상태 아이콘 위젯"""
    
    def __init__(self, status: ConversionStatus = ConversionStatus.PENDING):
        super().__init__()
        self.setFixedSize(16, 16)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_status(status)
    
    def update_status(self, status: ConversionStatus):
        """상태에 따른 아이콘 업데이트"""
        colors = {
            ConversionStatus.PENDING: "#9E9E9E",
            ConversionStatus.IN_PROGRESS: "#2196F3", 
            ConversionStatus.SUCCESS: "#4CAF50",
            ConversionStatus.FAILED: "#F44336",
            ConversionStatus.CANCELLED: "#FF9800"
        }
        
        symbols = {
            ConversionStatus.PENDING: "⏳",
            ConversionStatus.IN_PROGRESS: "🔄",
            ConversionStatus.SUCCESS: "✅",
            ConversionStatus.FAILED: "❌",
            ConversionStatus.CANCELLED: "⚠️"
        }
        
        color = colors.get(status, "#9E9E9E")
        symbol = symbols.get(status, "⏳")
        
        self.setText(symbol)
        self.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.setToolTip(status.value)


class PhaseProgressBar(QProgressBar):
    """단계별 진행률 바"""

    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(100)
        self.setTextVisible(True)
        self._current_phase = ConversionProgressStatus.INITIALIZING
        self._ocr_stage = None  # OCR 단계 추적

    def update_phase(self, phase: ConversionProgressStatus, progress: float = 0.0, ocr_stage: Optional[str] = None):
        """현재 단계와 진행률 업데이트"""
        self._current_phase = phase
        self._ocr_stage = ocr_stage
        self.setValue(int(progress * 100))

        # OCR 단계가 있으면 OCR 색상 사용, 없으면 기본 색상 사용
        if ocr_stage and OCR_PROGRESS_AVAILABLE:
            color = self._get_ocr_stage_color(ocr_stage)
            display_text = self._get_ocr_stage_text(ocr_stage)
        else:
            color = self._get_conversion_phase_color(phase)
            display_text = self._get_conversion_phase_text(phase)

        self.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
            QProgressBar {{
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                text-align: center;
            }}
        """)

        # 텍스트 포맷 설정
        if ocr_stage:
            self.setFormat(f"{display_text} - %p%")
        else:
            self.setFormat("%p%")

    def _get_conversion_phase_color(self, phase: ConversionProgressStatus) -> str:
        """변환 단계별 색상"""
        phase_colors = {
            ConversionProgressStatus.INITIALIZING: "#9E9E9E",
            ConversionProgressStatus.VALIDATING_FILE: "#FF9800",
            ConversionProgressStatus.READING_FILE: "#2196F3",
            ConversionProgressStatus.PROCESSING: "#3F51B5",
            ConversionProgressStatus.CHECKING_CONFLICTS: "#FF5722",
            ConversionProgressStatus.RESOLVING_CONFLICTS: "#E91E63",
            ConversionProgressStatus.WRITING_OUTPUT: "#009688",
            ConversionProgressStatus.FINALIZING: "#4CAF50",
            ConversionProgressStatus.COMPLETED: "#4CAF50",
            ConversionProgressStatus.ERROR: "#F44336"
        }
        return phase_colors.get(phase, "#2196F3")

    def _get_conversion_phase_text(self, phase: ConversionProgressStatus) -> str:
        """변환 단계별 텍스트"""
        phase_texts = {
            ConversionProgressStatus.INITIALIZING: "초기화",
            ConversionProgressStatus.VALIDATING_FILE: "파일 검증",
            ConversionProgressStatus.READING_FILE: "파일 읽기",
            ConversionProgressStatus.PROCESSING: "변환 처리",
            ConversionProgressStatus.CHECKING_CONFLICTS: "충돌 확인",
            ConversionProgressStatus.RESOLVING_CONFLICTS: "충돌 해결",
            ConversionProgressStatus.WRITING_OUTPUT: "파일 쓰기",
            ConversionProgressStatus.FINALIZING: "마무리",
            ConversionProgressStatus.COMPLETED: "완료",
            ConversionProgressStatus.ERROR: "오류"
        }
        return phase_texts.get(phase, "처리 중")

    def _get_ocr_stage_color(self, stage: str) -> str:
        """OCR 단계별 색상"""
        if not OCR_PROGRESS_AVAILABLE:
            return "#2196F3"

        try:
            # OCRStatusType enum으로 변환하여 색상 매핑
            stage_colors = {
                "idle": "#E0E0E0",
                "initializing": "#FFC107",
                "preprocessing": "#FF9800",
                "processing": "#2196F3",
                "post_processing": "#673AB7",
                "analyzing": "#9C27B0",
                "completed": "#4CAF50",
                "failed": "#F44336",
                "cancelled": "#795548"
            }
            return stage_colors.get(stage, "#2196F3")
        except:
            return "#2196F3"

    def _get_ocr_stage_text(self, stage: str) -> str:
        """OCR 단계별 텍스트"""
        stage_texts = {
            "idle": "대기",
            "initializing": "OCR 초기화",
            "preprocessing": "이미지 전처리",
            "processing": "OCR 처리",
            "post_processing": "텍스트 후처리",
            "analyzing": "품질 분석",
            "completed": "OCR 완료",
            "failed": "OCR 실패",
            "cancelled": "OCR 취소"
        }
        return stage_texts.get(stage, "OCR 처리")


class FileProgressItem(QTreeWidgetItem):
    """파일별 진행률 아이템"""
    
    def __init__(self, file_info: FileInfo):
        super().__init__()
        self.file_info = file_info
        self.status_icon = StatusIcon(file_info.conversion_status)
        
        # 컬럼 설정
        self.setText(0, file_info.name)
        self.setText(1, file_info.progress_status.value)
        self.setText(2, file_info.conflict_status.value if file_info.conflict_status != FileConflictStatus.NONE else "")
        self.setText(3, file_info.size_formatted)
        
        # 도구 팁 설정
        self.setToolTip(0, str(file_info.path))
    
    def update_progress(self, file_info: FileInfo):
        """진행률 업데이트"""
        self.file_info = file_info
        self.setText(1, file_info.progress_status.value)
        self.setText(2, file_info.conflict_status.value if file_info.conflict_status != FileConflictStatus.NONE else "")
        self.status_icon.update_status(file_info.conversion_status)


class ConflictSummaryWidget(QWidget):
    """충돌 요약 위젯"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 제목
        title = QLabel("충돌 해결 현황")
        title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 통계 정보
        self.stats_layout = QVBoxLayout()
        layout.addLayout(self.stats_layout)
        
        self.total_conflicts_label = QLabel("총 충돌: 0")
        self.resolved_conflicts_label = QLabel("해결됨: 0")
        self.skipped_files_label = QLabel("건너뜀: 0") 
        self.overwritten_files_label = QLabel("덮어씀: 0")
        self.renamed_files_label = QLabel("이름변경: 0")
        
        for label in [self.total_conflicts_label, self.resolved_conflicts_label,
                     self.skipped_files_label, self.overwritten_files_label,
                     self.renamed_files_label]:
            label.setStyleSheet("padding: 2px; font-size: 9pt;")
            self.stats_layout.addWidget(label)
    
    def update_stats(self, progress: ConversionProgress):
        """통계 업데이트"""
        self.total_conflicts_label.setText(f"총 충돌: {progress.conflicts_detected}")
        self.resolved_conflicts_label.setText(f"해결됨: {progress.conflicts_resolved}")
        self.skipped_files_label.setText(f"건너뜀: {progress.files_skipped}")
        self.overwritten_files_label.setText(f"덮어씀: {progress.files_overwritten}")
        self.renamed_files_label.setText(f"이름변경: {progress.files_renamed}")


class PerformanceMetricsWidget(QWidget):
    """성능 메트릭 위젯"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 제목
        title = QLabel("성능 정보")
        title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 메트릭 정보
        self.elapsed_time_label = QLabel("경과 시간: --")
        self.estimated_time_label = QLabel("예상 남은 시간: --")
        self.files_per_sec_label = QLabel("처리 속도: --")
        
        for label in [self.elapsed_time_label, self.estimated_time_label, self.files_per_sec_label]:
            label.setStyleSheet("padding: 2px; font-size: 9pt;")
            layout.addWidget(label)
    
    def update_metrics(self, progress: ConversionProgress):
        """메트릭 업데이트"""
        # 경과 시간
        elapsed = progress.elapsed_time
        elapsed_str = f"{int(elapsed//60):02d}:{int(elapsed%60):02d}"
        self.elapsed_time_label.setText(f"경과 시간: {elapsed_str}")
        
        # 예상 남은 시간
        if progress.estimated_time_remaining:
            remaining = progress.estimated_time_remaining
            remaining_str = f"{int(remaining//60):02d}:{int(remaining%60):02d}"
            self.estimated_time_label.setText(f"예상 남은 시간: {remaining_str}")
        else:
            self.estimated_time_label.setText("예상 남은 시간: --")
        
        # 처리 속도
        if elapsed > 0:
            rate = progress.completed_files / elapsed
            self.files_per_sec_label.setText(f"처리 속도: {rate:.1f} 파일/초")
        else:
            self.files_per_sec_label.setText("처리 속도: --")


class ExpandableSection(QWidget):
    """확장 가능한 섹션 위젯"""
    
    def __init__(self, title: str, content_widget: QWidget):
        super().__init__()
        self.title = title
        self.content_widget = content_widget
        self.is_expanded = False
        self._init_ui()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 헤더
        self.header = QFrame()
        self.header.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 3px;
            }
        """)
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # 토글 아이콘
        self.toggle_icon = QLabel("▶")
        self.toggle_icon.setFixedWidth(16)
        header_layout.addWidget(self.toggle_icon)
        
        # 제목
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("", 9, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        layout.addWidget(self.header)
        
        # 콘텐츠 컨테이너
        self.content_container = QWidget()
        self.content_container.setVisible(False)
        self.content_container.setStyleSheet("background-color: #FFFFFF;")
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.addWidget(self.content_widget)
        
        layout.addWidget(self.content_container)
        
        # 마우스 이벤트 연결
        self.header.mousePressEvent = self._on_header_clicked
    
    def _on_header_clicked(self, event):
        """헤더 클릭 이벤트"""
        self.toggle_expansion()
    
    def toggle_expansion(self):
        """확장/축소 토글"""
        self.is_expanded = not self.is_expanded
        self.content_container.setVisible(self.is_expanded)
        self.toggle_icon.setText("▼" if self.is_expanded else "▶")


class ProgressWidget(QWidget):
    """향상된 진행률 표시 위젯"""
    
    # 시그널
    cancel_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, ocr_config: Optional[OCREnhancementConfig] = None):
        super().__init__()
        self._is_active = False
        self._file_items: Dict[str, FileProgressItem] = {}
        self._start_time = None

        # OCR 진행률 추적기 초기화 (선택적)
        self.ocr_progress_tracker = None
        if OCR_PROGRESS_AVAILABLE and ocr_config and ocr_config.enabled:
            self.ocr_progress_tracker = OCRProgressTracker(ocr_config)
            logger.debug("OCR 진행률 추적기 활성화됨")

        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#FFFFFF"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # 메인 그룹박스
        self.group_box = QGroupBox("변환 진행률")
        self.group_box.setStyleSheet("""
            QGroupBox {
                background-color: #FFFFFF;
                color: #1F1F1F;
                font-weight: bold;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 5px;
            }
            QGroupBox::title {
                background-color: #FFFFFF;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        layout.addWidget(self.group_box)
        
        group_layout = QVBoxLayout(self.group_box)
        
        # 전체 진행률 섹션
        self._create_overall_progress_section(group_layout)
        
        # 현재 파일 진행률 섹션  
        self._create_current_file_section(group_layout)
        
        # 스플리터로 상단/하단 나누기
        splitter = QSplitter(Qt.Orientation.Vertical)
        group_layout.addWidget(splitter)
        
        # 상단: 파일 목록
        self._create_file_list_section(splitter)
        
        # 하단: 정보 패널들
        self._create_info_panels(splitter)
        
        # 버튼 섹션
        self._create_button_section(group_layout)
        
        # 초기 상태에서는 숨김
        self.setVisible(False)
    
    def _create_overall_progress_section(self, parent_layout):
        """전체 진행률 섹션 생성"""
        # 전체 진행률 바
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setMinimum(0)
        self.overall_progress_bar.setMaximum(100)
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setMinimumHeight(24)
        parent_layout.addWidget(self.overall_progress_bar)
        
        # 전체 상태 정보
        status_layout = QHBoxLayout()
        
        self.overall_status_label = QLabel("준비")
        self.overall_status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_layout.addWidget(self.overall_status_label, 1)
        
        self.completion_label = QLabel("0/0 완료")
        self.completion_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(self.completion_label)
        
        parent_layout.addLayout(status_layout)
    
    def _create_current_file_section(self, parent_layout):
        """현재 파일 섹션 생성"""
        # 현재 파일 프레임
        current_file_frame = QFrame()
        current_file_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        parent_layout.addWidget(current_file_frame)
        
        current_file_layout = QVBoxLayout(current_file_frame)
        current_file_layout.setContentsMargins(8, 8, 8, 8)
        
        # 현재 파일 정보
        file_info_layout = QHBoxLayout()
        
        self.current_file_icon = StatusIcon()
        file_info_layout.addWidget(self.current_file_icon)
        
        self.current_file_label = QLabel("대기 중...")
        self.current_file_label.setStyleSheet("font-weight: bold;")
        file_info_layout.addWidget(self.current_file_label, 1)
        
        self.current_phase_label = QLabel("")
        self.current_phase_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.current_phase_label.setStyleSheet("color: #666; font-size: 9pt;")
        file_info_layout.addWidget(self.current_phase_label)
        
        current_file_layout.addLayout(file_info_layout)
        
        # 현재 파일 진행률 바
        self.current_file_progress = PhaseProgressBar()
        self.current_file_progress.setMaximumHeight(16)
        current_file_layout.addWidget(self.current_file_progress)
    
    def _create_file_list_section(self, splitter):
        """파일 목록 섹션 생성"""
        # 파일 목록
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["파일명", "상태", "충돌", "크기"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.setRootIsDecorated(False)

        self.file_tree.setStyleSheet(
            """
            QTreeWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F7F7F7;
                color: #1F1F1F;
            }
            QTreeWidget::item {
                background-color: transparent;
            }
            """
        )
        
        # 컬럼 너비 설정
        header = self.file_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # 접근성 설정
        self.file_tree.setAccessibleName("파일 변환 진행률 목록")
        self.file_tree.setAccessibleDescription("각 파일의 변환 상태와 충돌 정보를 보여줍니다")
        
        splitter.addWidget(self.file_tree)
    
    def _create_info_panels(self, splitter):
        """정보 패널들 생성"""
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_widget.setStyleSheet("background-color: #FFFFFF;")
        
        # 충돌 요약 패널
        self.conflict_summary = ConflictSummaryWidget()
        conflict_section = ExpandableSection("충돌 현황", self.conflict_summary)
        info_layout.addWidget(conflict_section)
        
        # 성능 메트릭 패널
        self.performance_metrics = PerformanceMetricsWidget()
        metrics_section = ExpandableSection("성능 정보", self.performance_metrics)
        info_layout.addWidget(metrics_section)
        
        splitter.addWidget(info_widget)
        
        # 스플리터 비율 설정 (상단 70%, 하단 30%)
        splitter.setSizes([300, 150])
    
    def _create_button_section(self, parent_layout):
        """버튼 섹션 생성"""
        button_layout = QHBoxLayout()
        
        # 설정 버튼
        self.settings_btn = QPushButton("설정")
        self.settings_btn.setMaximumWidth(60)
        self.settings_btn.setAccessibleName("충돌 처리 설정")
        button_layout.addWidget(self.settings_btn)
        
        button_layout.addStretch()
        
        # 취소 버튼
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setMaximumWidth(60)
        self.cancel_btn.setAccessibleName("변환 작업 취소")
        button_layout.addWidget(self.cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        self.settings_btn.clicked.connect(self._on_settings_clicked)

        # OCR 진행률 추적기 시그널 연결
        if self.ocr_progress_tracker:
            self.ocr_progress_tracker.progress_updated.connect(self._on_ocr_progress_updated)
            self.ocr_progress_tracker.stage_changed.connect(self._on_ocr_stage_changed)
            self.ocr_progress_tracker.ocr_completed.connect(self._on_ocr_completed)
    
    def start_progress(self, total_files: int, file_list: Optional[List[FileInfo]] = None):
        """진행률 시작"""
        self._is_active = True
        self._start_time = datetime.now()
        self.setVisible(True)
        
        # 전체 진행률 초기화
        self.overall_progress_bar.setMaximum(total_files)
        self.overall_progress_bar.setValue(0)
        self.cancel_btn.setEnabled(True)
        
        # 상태 레이블 업데이트
        self.overall_status_label.setText("변환 시작")
        self.completion_label.setText(f"0/{total_files} 완료")
        self.current_file_label.setText("시작 중...")
        
        # 파일 목록 초기화
        self.file_tree.clear()
        self._file_items.clear()
        
        if file_list:
            for file_info in file_list:
                item = FileProgressItem(file_info)
                self.file_tree.addTopLevelItem(item)
                self._file_items[str(file_info.path)] = item
        
        logger.info(f"진행률 시작: {total_files}개 파일")
    
    def update_progress(self, progress: ConversionProgress):
        """진행률 업데이트"""
        if not self._is_active:
            return
        
        # 전체 진행률 업데이트
        self.overall_progress_bar.setMaximum(progress.total_files)
        self.overall_progress_bar.setValue(int(progress.progress_percent))
        
        # 완료 정보 업데이트
        self.completion_label.setText(f"{progress.completed_files}/{progress.total_files} 완료")
        
        # 현재 파일 정보 업데이트
        if progress.current_file:
            display_name = progress.current_file
            if len(display_name) > 50:
                display_name = "..." + display_name[-47:]
            self.current_file_label.setText(display_name)
            self.current_phase_label.setText(progress.current_progress_status.value)
            
            # 현재 파일 진행률 (OCR 단계 정보 포함)
            ocr_stage = self._get_current_ocr_stage(progress.current_file) if progress.current_file else None
            self.current_file_progress.update_phase(
                progress.current_progress_status,
                progress.current_file_progress,
                ocr_stage
            )
            
            # 현재 파일 아이콘 업데이트
            if progress.current_progress_status == ConversionProgressStatus.ERROR:
                self.current_file_icon.update_status(ConversionStatus.FAILED)
            elif progress.current_progress_status == ConversionProgressStatus.COMPLETED:
                self.current_file_icon.update_status(ConversionStatus.SUCCESS)
            else:
                self.current_file_icon.update_status(ConversionStatus.IN_PROGRESS)
        
        # 전체 상태 메시지
        if progress.current_status:
            self.overall_status_label.setText(progress.current_status)
        else:
            self.overall_status_label.setText(f"변환 중 ({progress.progress_percent:.1f}%)")
        
        # 정보 패널 업데이트
        self.conflict_summary.update_stats(progress)
        self.performance_metrics.update_metrics(progress)
    
    def update_file_progress(self, file_info: FileInfo):
        """개별 파일 진행률 업데이트"""
        file_path_str = str(file_info.path)
        if file_path_str in self._file_items:
            self._file_items[file_path_str].update_progress(file_info)
    
    def finish_progress(self, success: bool = True, message: str = ""):
        """진행률 완료"""
        if not self._is_active:
            return
        
        self._is_active = False
        self.cancel_btn.setEnabled(False)
        
        if success:
            self.overall_progress_bar.setValue(self.overall_progress_bar.maximum())
            self.current_file_label.setText("완료")
            self.overall_status_label.setText(message or "모든 변환이 완료되었습니다")
            self.current_file_icon.update_status(ConversionStatus.SUCCESS)
            
            # 성공 색상
            self.overall_progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
            """)
        else:
            self.current_file_label.setText("중단됨")
            self.overall_status_label.setText(message or "변환이 중단되었습니다")
            self.current_file_icon.update_status(ConversionStatus.FAILED)
            
            # 오류 색상
            self.overall_progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #F44336;
                    border-radius: 3px;
                }
            """)
        
        # 완료 후 자동 숨김
        QTimer.singleShot(5000, self.hide_progress)
        
        logger.info(f"진행률 완료: 성공={success}, 메시지={message}")
    
    def cancel_progress(self):
        """진행률 취소"""
        if self._is_active:
            self.finish_progress(success=False, message="사용자가 취소했습니다")
            self.cancel_requested.emit()
    
    def hide_progress(self):
        """진행률 위젯 숨김"""
        self._is_active = False
        self.setVisible(False)
        
        # 상태 초기화
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setStyleSheet("")
        self.current_file_label.setText("대기 중...")
        self.overall_status_label.setText("준비")
        self.completion_label.setText("0/0 완료")
        self.current_phase_label.setText("")
        self.cancel_btn.setEnabled(False)
        
        # 파일 목록 및 정보 초기화
        self.file_tree.clear()
        self._file_items.clear()
    
    def _on_cancel_clicked(self):
        """취소 버튼 클릭시"""
        self.cancel_progress()
    
    def _on_settings_clicked(self):
        """설정 버튼 클릭시"""
        self.settings_requested.emit()

    # OCR 진행률 관련 메서드들
    def _on_ocr_progress_updated(self, file_path: str, stage: OCRStatusType, progress: float):
        """OCR 진행률 업데이트 시그널 처리"""
        if not self._is_active:
            return

        # 현재 파일인 경우 진행률 바 업데이트
        current_file_path = self._get_current_file_path()
        if current_file_path and file_path == current_file_path:
            self.current_file_progress.update_phase(
                ConversionProgressStatus.PROCESSING,
                progress,
                stage.value if hasattr(stage, 'value') else str(stage)
            )

        logger.debug(f"OCR 진행률 업데이트: {file_path} -> {stage} ({progress:.1%})")

    def _on_ocr_stage_changed(self, file_path: str, stage: OCRStatusType, description: str):
        """OCR 단계 변경 시그널 처리"""
        if not self._is_active:
            return

        # 현재 파일인 경우 상태 레이블 업데이트
        current_file_path = self._get_current_file_path()
        if current_file_path and file_path == current_file_path:
            self.current_phase_label.setText(description)

        logger.debug(f"OCR 단계 변경: {file_path} -> {stage.value}: {description}")

    def _on_ocr_completed(self, file_path: str, success: bool, message: str):
        """OCR 완료 시그널 처리"""
        logger.info(f"OCR 완료: {file_path} (성공: {success}) - {message}")

    def start_ocr_tracking(self, file_info: FileInfo, enhancements: List = None):
        """OCR 추적 시작"""
        if not self.ocr_progress_tracker:
            return

        if enhancements is None:
            enhancements = []

        self.ocr_progress_tracker.start_ocr_tracking(file_info, enhancements)

    def update_ocr_stage(self, file_info: FileInfo, stage: str, progress: float = 0.0, description: str = ""):
        """OCR 단계 업데이트"""
        if not self.ocr_progress_tracker or not OCR_PROGRESS_AVAILABLE:
            return

        try:
            # 문자열을 OCRStatusType으로 변환
            stage_enum = OCRStatusType(stage)
            self.ocr_progress_tracker.update_ocr_stage(file_info, stage_enum, progress, description)
        except (ValueError, AttributeError) as e:
            logger.warning(f"알 수 없는 OCR 단계: {stage} - {e}")

    def complete_ocr_tracking(self, file_info: FileInfo, success: bool = True, message: str = ""):
        """OCR 추적 완료"""
        if not self.ocr_progress_tracker:
            return

        self.ocr_progress_tracker.complete_ocr_tracking(file_info, success, message)

    def get_ocr_progress_summary(self, file_info: FileInfo) -> Optional[Dict]:
        """OCR 진행률 요약 반환"""
        if not self.ocr_progress_tracker:
            return None

        return self.ocr_progress_tracker.create_ocr_progress_summary(file_info)

    def _get_current_ocr_stage(self, current_file: str) -> Optional[str]:
        """현재 파일의 OCR 단계 반환"""
        if not self.ocr_progress_tracker or not current_file:
            return None

        # 파일 정보 검색
        file_info = self._find_file_info_by_name(current_file)
        if not file_info:
            return None

        # OCR 상태 정보 가져오기
        status_info = self.ocr_progress_tracker.get_ocr_status_info(file_info)
        if not status_info:
            return None

        return status_info.status.value if hasattr(status_info.status, 'value') else str(status_info.status)

    def _get_current_file_path(self) -> Optional[str]:
        """현재 처리 중인 파일 경로 반환"""
        # 현재 파일 레이블에서 파일명 추출
        current_text = self.current_file_label.text()
        if not current_text or current_text in ["대기 중...", "시작 중...", "완료", "중단됨"]:
            return None

        # 파일명으로 파일 정보 검색
        file_info = self._find_file_info_by_name(current_text.replace("...", ""))
        return str(file_info.path) if file_info else None

    def _find_file_info_by_name(self, file_name: str) -> Optional[FileInfo]:
        """파일명으로 FileInfo 검색"""
        # 간단한 파일명 매칭 (개선 가능)
        for item in self._file_items.values():
            file_info = item.file_info
            if file_info.name in file_name or file_name in file_info.name:
                return file_info
        return None

    def clear_ocr_tracking(self):
        """OCR 추적 데이터 정리"""
        if self.ocr_progress_tracker:
            self.ocr_progress_tracker.clear_tracking_data()

    def get_ocr_tracking_stats(self) -> Optional[Dict]:
        """OCR 추적 통계 반환"""
        if not self.ocr_progress_tracker:
            return None

        return self.ocr_progress_tracker.get_tracking_stats()
    
    def is_active(self) -> bool:
        """진행률이 활성화되어 있는지 확인"""
        return self._is_active
    
    def get_file_count(self) -> int:
        """파일 개수 반환"""
        return len(self._file_items)
    
    def set_expandable_sections_visibility(self, visible: bool):
        """확장 가능한 섹션들의 표시 여부 설정"""
        # 작은 화면에서는 정보 패널을 숨김
        for child in self.findChildren(ExpandableSection):
            child.setVisible(visible)
