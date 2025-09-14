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
        
    def update_phase(self, phase: ConversionProgressStatus, progress: float = 0.0):
        """현재 단계와 진행률 업데이트"""
        self._current_phase = phase
        self.setValue(int(progress * 100))
        
        # 단계별 색상 설정
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
        
        color = phase_colors.get(phase, "#2196F3")
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
    
    def __init__(self):
        super().__init__()
        self._is_active = False
        self._file_items: Dict[str, FileProgressItem] = {}
        self._start_time = None
        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # 메인 그룹박스
        self.group_box = QGroupBox("변환 진행률")
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 5px;
            }
            QGroupBox::title {
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
            
            # 현재 파일 진행률
            self.current_file_progress.update_phase(
                progress.current_progress_status,
                progress.current_file_progress
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