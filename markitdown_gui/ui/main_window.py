"""
메인 윈도우 UI
애플리케이션의 주요 사용자 인터페이스
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFileDialog, QCheckBox, QProgressBar,
    QTextEdit, QSplitter, QGroupBox, QStatusBar, QMenuBar,
    QMessageBox, QComboBox, QDialog
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont

from ..core.config_manager import ConfigManager
from ..core.models import AppConfig, FileInfo, ConversionStatus, FileConflictConfig, FileConflictPolicy
from ..core.logger import get_logger, add_ui_logging
from ..core.file_manager import FileManager
from ..core.conversion_manager import ConversionManager
from ..core.file_conflict_handler import FileConflictHandler
from ..core.i18n_manager import get_i18n_manager, init_i18n, tr
from ..core.theme_manager import get_theme_manager, init_theme_manager
from ..core.accessibility_manager import (
    get_accessibility_manager, init_accessibility_manager, AccessibilityFeature
)
from ..core.keyboard_navigation import get_keyboard_navigation_manager, init_keyboard_navigation_manager
from ..core.utils import get_default_output_directory
from .components.file_list_widget import FileListWidget
from .components.progress_widget import ProgressWidget
from .components.log_widget import LogWidget
from .preview_dialog import PreviewDialog
from .settings_dialog import SettingsDialog
from .file_viewer_dialog import FileViewerDialog
from .performance_optimizer import ResponsivenessOptimizer


logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        
        # i18n 시스템 초기화
        self.i18n_manager = get_i18n_manager()
        if not self.i18n_manager:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            self.i18n_manager = init_i18n(app)
        
        # 테마 시스템 초기화
        self.theme_manager = get_theme_manager()
        if not self.theme_manager:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            self.theme_manager = init_theme_manager(app, config_manager.config_dir)
        
        # 접근성 시스템 초기화
        self.accessibility_manager = get_accessibility_manager()
        if not self.accessibility_manager:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            self.accessibility_manager = init_accessibility_manager(app, config_manager.config_dir)
        
        # 키보드 네비게이션 초기화
        self.keyboard_navigation = get_keyboard_navigation_manager()
        if not self.keyboard_navigation:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            self.keyboard_navigation = init_keyboard_navigation_manager(app)
        
        # 성능 최적화 초기화
        self.performance_optimizer = ResponsivenessOptimizer(self)
        
        # 매니저들 초기화
        self.file_manager = FileManager()
        
        # 파일 충돌 설정 로드
        self.conflict_config = self._load_conflict_config()
        
        # 향상된 변환 매니저 초기화 (직접 파일 저장 지원)
        self.conversion_manager = ConversionManager(
            output_directory=self.config.output_directory,
            conflict_config=self.conflict_config,
            save_to_original_dir=getattr(self.config, 'save_to_original_dir', True)
        )
        
        # ConversionManager의 내부 conflict_handler에 대한 참조
        self.conflict_handler = self.conversion_manager._conflict_handler
        
        # UI 성능 최적화 적용
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            self.performance_optimizer.optimize_application(app)
        
        # UI 초기화 (성능 측정)
        with self.performance_optimizer.measure_operation("ui_initialization"):
            self._init_ui()
            self._setup_menu_bar()
            self._setup_status_bar()
            self._setup_connections()
            self._setup_managers()
            
        # 성능 최적화 연결
        self._setup_performance_optimization()
        
        # 접근성 설정
        self._setup_accessibility()
        
        # 설정 복원
        self._restore_settings()
        
        # i18n 연결
        self._setup_i18n_connections()
        
        # 초기 UI 텍스트 설정
        self._update_ui_texts()
        
        logger.info("메인 윈도우 초기화 완료")
    
    def _init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("MarkItDown GUI Converter")
        self.setMinimumSize(1000, 700)
        
        # 윈도우 아이콘 설정
        self._set_window_icon()
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 디렉토리 선택 영역
        dir_group = self._create_directory_group()
        main_layout.addWidget(dir_group)
        
        # 분할기로 파일 리스트와 하단 영역 나누기
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 파일 리스트 위젯
        self.file_list_widget = FileListWidget()
        splitter.addWidget(self.file_list_widget)
        
        # 하단 영역 (진행률, 로그, 버튼들)
        bottom_widget = self._create_bottom_widget()
        splitter.addWidget(bottom_widget)
        
        # 분할기 비율 설정 (70:30)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # 액션 버튼들
        action_layout = self._create_action_buttons()
        main_layout.addLayout(action_layout)
    
    def _create_directory_group(self) -> QGroupBox:
        """디렉토리 선택 그룹 생성"""
        group = QGroupBox("디렉토리 선택")
        group.setObjectName("directory_selection_group")
        layout = QVBoxLayout(group)
        
        # 첫 번째 행: 디렉토리 경로와 찾아보기 버튼
        dir_layout = QHBoxLayout()
        
        self.dir_label = QLabel("디렉토리를 선택해주세요...")
        self.dir_label.setObjectName("directory_path_label")
        self.dir_label.setStyleSheet("padding: 8px; border: 1px solid #ccc; background-color: white;")
        # 접근성 속성 설정
        self.dir_label.setAccessibleName("선택된 디렉토리 경로")
        self.dir_label.setAccessibleDescription("변환할 파일들이 있는 디렉토리의 경로가 표시됩니다")
        dir_layout.addWidget(self.dir_label, 1)
        
        self.browse_btn = QPushButton("찾아보기...")
        self.browse_btn.setObjectName("browse_directory_btn")
        self.browse_btn.setMinimumWidth(100)
        self.browse_btn.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        # 접근성 속성 설정
        self.browse_btn.setAccessibleName("디렉토리 찾아보기")
        self.browse_btn.setAccessibleDescription("변환할 파일들이 있는 디렉토리를 선택하는 대화상자를 엽니다")
        self.browse_btn.setToolTip("클릭하여 디렉토리를 선택하세요 (단축키: Ctrl+D)")
        dir_layout.addWidget(self.browse_btn)
        
        layout.addLayout(dir_layout)
        
        # 두 번째 행: 옵션들
        options_layout = QHBoxLayout()
        
        self.subdirs_check = QCheckBox("하위 디렉토리 포함")
        self.subdirs_check.setObjectName("include_subdirs_checkbox")
        self.subdirs_check.setChecked(self.config.include_subdirectories)
        self.subdirs_check.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        # 접근성 속성 설정
        self.subdirs_check.setAccessibleName("하위 디렉토리 포함")
        self.subdirs_check.setAccessibleDescription("선택된 디렉토리의 하위 디렉토리도 포함하여 파일을 검색합니다")
        self.subdirs_check.setToolTip("체크하면 하위 디렉토리의 파일들도 함께 변환합니다")
        options_layout.addWidget(self.subdirs_check)
        
        # 최근 디렉토리 선택
        recent_label = QLabel("최근 사용:")
        recent_label.setObjectName("recent_directories_label")
        recent_label.setAccessibleName("최근 사용한 디렉토리")
        options_layout.addWidget(recent_label)
        
        self.recent_combo = QComboBox()
        self.recent_combo.setObjectName("recent_directories_combo")
        self.recent_combo.setMinimumWidth(200)
        self.recent_combo.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        # 접근성 속성 설정
        self.recent_combo.setAccessibleName("최근 사용한 디렉토리 목록")
        self.recent_combo.setAccessibleDescription("최근에 사용한 디렉토리 목록에서 선택할 수 있습니다")
        self.recent_combo.setToolTip("최근에 사용한 디렉토리 중 하나를 선택하세요")
        # 라벨과 콤보박스 연결
        recent_label.setBuddy(self.recent_combo)
        
        self._update_recent_directories()
        options_layout.addWidget(self.recent_combo)
        
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        return group
    
    def _create_bottom_widget(self) -> QWidget:
        """하단 위젯 생성 (진행률과 로그)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 진행률 위젯
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # 로그 위젯
        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget)
        
        # UI 로깅 연결
        add_ui_logging(self.log_widget)
        
        return widget
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """액션 버튼들 생성"""
        layout = QHBoxLayout()
        
        # 왼쪽 버튼들
        self.scan_btn = QPushButton("파일 스캔")
        self.scan_btn.setObjectName("scan_files_btn")
        self.scan_btn.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        # 접근성 속성 설정
        self.scan_btn.setAccessibleName("파일 스캔")
        self.scan_btn.setAccessibleDescription("선택된 디렉토리에서 변환 가능한 파일들을 검색합니다")
        self.scan_btn.setToolTip("디렉토리를 스캔하여 변환 가능한 파일들을 찾습니다")
        layout.addWidget(self.scan_btn)
        
        self.convert_btn = QPushButton("선택된 파일 변환")
        self.convert_btn.setObjectName("convert_files_btn")
        self.convert_btn.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        self.convert_btn.setEnabled(False)
        # 접근성 속성 설정
        self.convert_btn.setAccessibleName("선택된 파일 변환")
        self.convert_btn.setAccessibleDescription("선택된 파일들을 마크다운 형식으로 변환합니다")
        self.convert_btn.setToolTip("선택된 파일들을 마크다운으로 변환합니다")
        layout.addWidget(self.convert_btn)
        
        layout.addStretch()
        
        # 오른쪽 버튼들
        self.preview_btn = QPushButton("미리보기")
        self.preview_btn.setObjectName("preview_file_btn")
        self.preview_btn.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        self.preview_btn.setEnabled(False)
        # 접근성 속성 설정
        self.preview_btn.setAccessibleName("파일 미리보기")
        self.preview_btn.setAccessibleDescription("선택된 파일의 마크다운 변환 결과를 미리 봅니다")
        self.preview_btn.setToolTip("선택된 파일의 마크다운 변환 결과를 미리보기 창에서 확인합니다 (단축키: F3)")
        layout.addWidget(self.preview_btn)
        
        # 변환 설정 버튼
        self.conversion_settings_btn = QPushButton("변환 설정")
        self.conversion_settings_btn.setObjectName("conversion_settings_btn")
        self.conversion_settings_btn.setMinimumHeight(44)  # 접근성 터치 타겟 크기
        # 접근성 속성 설정
        self.conversion_settings_btn.setAccessibleName("변환 설정")
        self.conversion_settings_btn.setAccessibleDescription("파일 변환 설정과 충돌 해결 정책을 구성합니다")
        self.conversion_settings_btn.setToolTip("파일 변환 설정과 충돌 해결 정책을 구성합니다")
        layout.addWidget(self.conversion_settings_btn)
        
        # 충돌 상태 표시 (직접 파일 저장에서 중요)
        self.conflict_status_label = QLabel("충돌 정책: 자동 이름 변경")
        self.conflict_status_label.setObjectName("conflict_status_label")
        self.conflict_status_label.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
        layout.addWidget(self.conflict_status_label)
        
        # 초기 충돌 상태 표시 업데이트
        self._update_conflict_status_display()
        
        return layout
    
    def _setup_menu_bar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")
        
        # 디렉토리 선택
        select_dir_action = QAction("디렉토리 선택(&D)", self)
        select_dir_action.setShortcut("Ctrl+D")
        select_dir_action.triggered.connect(self._browse_directory)
        file_menu.addAction(select_dir_action)
        
        file_menu.addSeparator()
        
        # 종료
        exit_action = QAction("종료(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 편집 메뉴
        edit_menu = menubar.addMenu("편집(&E)")
        
        # 전체 선택/해제
        select_all_action = QAction("전체 선택(&A)", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.file_list_widget.select_all)
        edit_menu.addAction(select_all_action)
        
        select_none_action = QAction("전체 해제(&N)", self)
        select_none_action.setShortcut("Ctrl+Shift+A")
        select_none_action.triggered.connect(self.file_list_widget.select_none)
        edit_menu.addAction(select_none_action)
        
        # 보기 메뉴
        view_menu = menubar.addMenu("보기(&V)")
        
        # 로그 표시/숨기기
        self.toggle_log_action = QAction("로그 표시(&L)", self)
        self.toggle_log_action.setCheckable(True)
        self.toggle_log_action.setChecked(True)
        self.toggle_log_action.triggered.connect(self._toggle_log_visibility)
        view_menu.addAction(self.toggle_log_action)
        
        view_menu.addSeparator()
        
        # 원본 파일 보기
        view_file_action = QAction("선택된 파일 보기(&F)", self)
        view_file_action.setShortcut("F3")
        view_file_action.triggered.connect(self._view_selected_file)
        view_menu.addAction(view_file_action)
        
        # 도구 메뉴
        tools_menu = menubar.addMenu("도구(&T)")
        
        # 설정
        settings_action = QAction("설정(&S)", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # 변환 설정
        conversion_settings_action = QAction("변환 설정(&C)", self)
        conversion_settings_action.setShortcut("Ctrl+Shift+C")
        conversion_settings_action.triggered.connect(self._show_conversion_settings)
        tools_menu.addAction(conversion_settings_action)
        
        tools_menu.addSeparator()
        
        # 충돌 정책 빠른 선택
        conflict_menu = tools_menu.addMenu("충돌 정책(&P)")
        
        self.auto_rename_action = QAction("자동 이름 변경", self)
        self.auto_rename_action.setCheckable(True)
        self.auto_rename_action.triggered.connect(lambda: self._set_conflict_policy(FileConflictPolicy.RENAME))
        conflict_menu.addAction(self.auto_rename_action)
        
        self.overwrite_action = QAction("덮어쓰기", self)
        self.overwrite_action.setCheckable(True)
        self.overwrite_action.triggered.connect(lambda: self._set_conflict_policy(FileConflictPolicy.OVERWRITE))
        conflict_menu.addAction(self.overwrite_action)
        
        self.skip_action = QAction("건너뛰기", self)
        self.skip_action.setCheckable(True)
        self.skip_action.triggered.connect(lambda: self._set_conflict_policy(FileConflictPolicy.SKIP))
        conflict_menu.addAction(self.skip_action)
        
        self.ask_user_action = QAction("사용자에게 묻기", self)
        self.ask_user_action.setCheckable(True)
        self.ask_user_action.triggered.connect(lambda: self._set_conflict_policy(FileConflictPolicy.ASK_USER))
        conflict_menu.addAction(self.ask_user_action)
        
        # 현재 충돌 정책 표시
        self._update_conflict_policy_menu()
        
        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말(&H)")
        
        # 정보
        about_action = QAction("정보(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """상태바 설정"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 상태 메시지
        self.status_bar.showMessage("준비")
        
        # 오른쪽에 파일 개수 표시
        self.file_count_label = QLabel("파일: 0개")
        self.status_bar.addPermanentWidget(self.file_count_label)
        
        # 선택된 파일 개수 표시
        self.selected_count_label = QLabel("선택: 0개")
        self.status_bar.addPermanentWidget(self.selected_count_label)
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        # 디렉토리 선택 버튼
        self.browse_btn.clicked.connect(self._browse_directory)
        
        # 최근 디렉토리 콤보박스
        self.recent_combo.currentTextChanged.connect(self._on_recent_directory_selected)
        
        # 하위 디렉토리 포함 체크박스
        self.subdirs_check.toggled.connect(self._on_subdirs_option_changed)
        
        # 액션 버튼들
        self.scan_btn.clicked.connect(self._scan_directory)
        self.convert_btn.clicked.connect(self._convert_files)
        self.preview_btn.clicked.connect(self._preview_markdown)
        self.conversion_settings_btn.clicked.connect(self._show_conversion_settings)
        
        # 파일 리스트 위젯 연결
        self.file_list_widget.selection_changed.connect(self._on_file_selection_changed)
        self.file_list_widget.double_clicked.connect(self._on_file_double_clicked)
        self.file_list_widget.export_requested.connect(self._export_single_file)
        
        # 진행률 위젯 연결
        self.progress_widget.cancel_requested.connect(self._on_conversion_cancel_requested)
    
    def _setup_managers(self):
        """매니저들 시그널-슬롯 연결"""
        # 파일 매니저 연결
        self.file_manager.scan_progress_updated.connect(self._on_scan_progress)
        self.file_manager.file_found.connect(self._on_file_found)
        self.file_manager.scan_completed.connect(self._on_scan_completed)
        self.file_manager.scan_error.connect(self._on_scan_error)
        
        # 변환 매니저 연결
        self.conversion_manager.conversion_progress_updated.connect(self._on_conversion_progress)
        self.conversion_manager.file_conversion_started.connect(self._on_file_conversion_started)
        self.conversion_manager.file_conversion_completed.connect(self._on_file_conversion_completed)
        self.conversion_manager.conversion_completed.connect(self._on_conversion_completed)
        self.conversion_manager.conversion_error.connect(self._on_conversion_error)
    
    def _update_recent_directories(self):
        """최근 디렉토리 목록 업데이트"""
        self.recent_combo.clear()
        if self.config.recent_directories:
            self.recent_combo.addItems(self.config.recent_directories)
    
    def _browse_directory(self):
        """디렉토리 선택 대화상자"""
        current_dir = str(Path.home())
        if self.config.recent_directories:
            current_dir = self.config.recent_directories[0]
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "변환할 파일들이 있는 디렉토리를 선택하세요",
            current_dir
        )
        
        if directory:
            self._set_current_directory(directory)
    
    def _set_current_directory(self, directory: str):
        """현재 디렉토리 설정"""
        self.current_directory = Path(directory)
        self.dir_label.setText(directory)
        
        # 최근 디렉토리에 추가
        self.config_manager.add_recent_directory(directory)
        self._update_recent_directories()
        
        # 스캔 버튼 활성화
        self.scan_btn.setEnabled(True)
        self.status_bar.showMessage(f"디렉토리 선택됨: {directory}")
        
        logger.info(f"디렉토리 선택됨: {directory}")
    
    def _on_recent_directory_selected(self, directory: str):
        """최근 디렉토리 선택시"""
        if directory and directory != self.dir_label.text():
            self._set_current_directory(directory)
    
    def _on_subdirs_option_changed(self, checked: bool):
        """하위 디렉토리 포함 옵션 변경시"""
        self.config.include_subdirectories = checked
        logger.debug(f"하위 디렉토리 포함 옵션 변경: {checked}")
    
    def _scan_directory(self):
        """디렉토리 스캔"""
        if not hasattr(self, 'current_directory'):
            QMessageBox.warning(self, "경고", "디렉토리를 먼저 선택해주세요.")
            return
        
        if self.file_manager.is_scanning():
            QMessageBox.information(self, "정보", "이미 스캔이 진행 중입니다.")
            return
        
        # UI 상태 업데이트
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("스캔 중...")
        self.file_list_widget.clear()
        self.status_bar.showMessage("디렉토리 스캔 중...")
        
        # 스캔 시작
        success = self.file_manager.scan_directory_async(
            directory=self.current_directory,
            include_subdirectories=self.config.include_subdirectories,
            supported_extensions=self.config.supported_extensions,
            max_file_size_mb=self.config.max_file_size_mb
        )
        
        if not success:
            self._reset_scan_ui()
            QMessageBox.warning(self, "오류", "스캔을 시작할 수 없습니다.")
        
        logger.info(f"디렉토리 스캔 시작: {self.current_directory}")
    
    def _convert_files(self):
        """선택된 파일들 변환 (향상된 직접 파일 저장)"""
        selected_files = self.file_list_widget.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "정보", "변환할 파일을 선택해주세요.")
            return
        
        if self.conversion_manager.is_converting():
            QMessageBox.information(self, "정보", "이미 변환이 진행 중입니다.")
            return
        
        # MarkItDown 라이브러리 확인
        if not self.conversion_manager.is_markitdown_available():
            QMessageBox.critical(
                self, "오류", 
                "MarkItDown 라이브러리가 설치되지 않았습니다.\n\n"
                "다음 명령어로 설치해주세요:\n"
                "pip install markitdown[all]"
            )
            return
        
        # 파일 검증
        invalid_files = []
        for file_info in selected_files:
            is_valid, error_msg = self.conversion_manager.validate_file_for_conversion(file_info)
            if not is_valid:
                invalid_files.append(f"• {file_info.name}: {error_msg}")
        
        if invalid_files:
            error_text = "다음 파일들은 변환할 수 없습니다:\n\n" + "\n".join(invalid_files)
            QMessageBox.warning(self, "변환 불가", error_text)
            return
        
        # 충돌 설정 업데이트
        self.conversion_manager.set_conflict_policy(self.conflict_config.default_policy)
        
        # UI 상태 업데이트
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("변환 중...")
        self.progress_widget.start_progress(len(selected_files))
        
        # 변환 시작 (향상된 변환 매니저 사용)
        success = self.conversion_manager.convert_files_async(selected_files)
        
        if not success:
            self._reset_conversion_ui()
            QMessageBox.warning(self, "오류", "변환을 시작할 수 없습니다.")
        
        logger.info(f"파일 변환 시작: {len(selected_files)}개 (충돌 정책: {self.conflict_config.default_policy.value})")
    
    def _preview_markdown(self):
        """마크다운 미리보기"""
        selected_files = self.file_list_widget.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "정보", "미리보기할 파일을 선택해주세요.")
            return
        
        if len(selected_files) > 1:
            QMessageBox.information(self, "정보", "미리보기는 한 번에 하나의 파일만 가능합니다.")
            return
        
        file_info = selected_files[0]
        
        # 이미 변환된 파일이 있는지 확인
        output_dir = getattr(self.config, 'output_directory', None)
        if not output_dir:
            output_dir = get_default_output_directory()
        output_file = output_dir / f"{file_info.path.stem}.md"
        
        if output_file.exists():
            # 변환된 파일 미리보기
            dialog = PreviewDialog(self)
            dialog.set_markdown_file(output_file)
            dialog.exec()
        else:
            # 변환되지 않은 파일 - 미리 변환해서 보여주기
            reply = QMessageBox.question(
                self, "미리보기",
                f"'{file_info.name}' 파일이 아직 변환되지 않았습니다.\n"
                "미리보기를 위해 변환하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._preview_unconverted_file(file_info)
        
        logger.info(f"마크다운 미리보기: {file_info.name}")
    
    def _preview_unconverted_file(self, file_info: FileInfo):
        """변환되지 않은 파일의 미리보기"""
        try:
            # 임시 변환 수행
            result = self.conversion_manager.convert_single_file(file_info)
            
            if result.is_success:
                dialog = PreviewDialog(self)
                dialog.set_markdown_file(result.output_path)
                dialog.exec()
            else:
                QMessageBox.critical(
                    self, "변환 오류",
                    f"파일 변환에 실패했습니다:\n{result.error_message}"
                )
        
        except Exception as e:
            logger.error(f"미리보기용 변환 실패: {e}")
            QMessageBox.critical(
                self, "오류",
                f"미리보기 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def _show_conversion_settings(self):
        """변환 설정 다이얼로그 표시"""
        from .settings_dialog import SettingsDialog
        
        try:
            dialog = SettingsDialog(self.config_manager, self)
            dialog.tab_widget.setCurrentIndex(1)  # Set to conversion settings tab (index 1)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 설정 업데이트
                self.config_manager.load_config()
                self._load_conflict_config()
                self._update_conflict_status_display()
                self._update_conflict_policy_menu()
                
                self.status_bar.showMessage("변환 설정이 업데이트되었습니다.", 3000)
                logger.info("변환 설정이 업데이트되었습니다.")
                
        except ImportError:
            # 변환 설정 다이얼로그가 없는 경우 기본 설정 창 표시
            self._show_basic_conversion_settings()
        except Exception as e:
            logger.error(f"변환 설정 다이얼로그 오류: {e}")
            QMessageBox.warning(self, "오류", f"변환 설정을 열 수 없습니다: {str(e)}")
    
    def _on_file_selection_changed(self, selected_count: int, total_count: int):
        """파일 선택 변경시"""
        self.selected_count_label.setText(f"선택: {selected_count}개")
        self.file_count_label.setText(f"파일: {total_count}개")
        
        # 버튼 상태 업데이트
        self.convert_btn.setEnabled(selected_count > 0)
        self.preview_btn.setEnabled(selected_count == 1)
    
    def _on_file_double_clicked(self, file_info):
        """파일 더블클릭시"""
        try:
            # 원본 파일 뷰어 열기
            dialog = FileViewerDialog(file_info, self)
            dialog.exec()
        except Exception as e:
            logger.error(f"파일 뷰어 열기 실패: {e}")
            QMessageBox.warning(self, "오류", f"파일을 열 수 없습니다:\n{str(e)}")
    
    def _toggle_log_visibility(self, visible: bool):
        """로그 위젯 표시/숨기기"""
        self.log_widget.setVisible(visible)
    
    def _view_selected_file(self):
        """선택된 파일 보기"""
        selected_files = self.file_list_widget.get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "정보", "파일을 선택해주세요.")
            return
        
        if len(selected_files) > 1:
            QMessageBox.information(self, "정보", "하나의 파일만 선택해주세요.")
            return
        
        # 첫 번째 선택된 파일 보기
        self._on_file_double_clicked(selected_files[0])
    
    def _export_single_file(self, file_info: FileInfo):
        """단일 파일 내보내기"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            # 저장할 파일명 생성
            default_name = f"{file_info.path.stem}.md"
            
            # 파일 저장 다이얼로그
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "마크다운으로 내보내기",
                default_name,
                "Markdown 파일 (*.md);;텍스트 파일 (*.txt);;모든 파일 (*.*)"
            )
            
            if not filename:
                return
            
            # 단일 파일 변환 수행
            self.status_bar.showMessage(f"파일 변환 중: {file_info.name}")
            
            # 임시로 선택 상태를 True로 설정
            original_selected = file_info.is_selected
            file_info.is_selected = True
            
            try:
                # 변환 매니저를 사용하여 변환
                result = self.conversion_manager.convert_single_file(file_info)
                
                if result.is_success:
                    # 변환된 내용을 지정된 파일에 저장
                    output_path = Path(filename)
                    output_path.write_text(result.content, encoding='utf-8')
                    
                    self.status_bar.showMessage(f"내보내기 완료: {output_path.name}", 5000)
                    QMessageBox.information(
                        self, "내보내기 완료", 
                        f"파일이 성공적으로 내보내기되었습니다:\n{output_path}"
                    )
                    
                    logger.info(f"단일 파일 내보내기 완료: {file_info.name} -> {output_path}")
                else:
                    # 변환 실패
                    error_msg = result.error_message or "알 수 없는 오류"
                    self.status_bar.showMessage("내보내기 실패", 5000)
                    QMessageBox.critical(
                        self, "내보내기 실패",
                        f"파일 변환 중 오류가 발생했습니다:\n{error_msg}"
                    )
                    logger.error(f"단일 파일 내보내기 실패: {file_info.name} - {error_msg}")
                    
            finally:
                # 원래 선택 상태로 복원
                file_info.is_selected = original_selected
                
        except Exception as e:
            self.status_bar.showMessage("내보내기 오류", 5000)
            logger.error(f"단일 파일 내보내기 오류: {e}")
            QMessageBox.critical(
                self, "오류",
                f"파일 내보내기 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def _show_settings(self):
        """설정 다이얼로그 표시"""
        dialog = SettingsDialog(self.config_manager, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.language_changed.connect(self._on_language_changed)
        dialog.theme_changed.connect(self._on_theme_changed)
        dialog.exec()
    
    def _on_language_changed(self, language_code: str):
        """언어 변경 처리"""
        try:
            if self.i18n_manager:
                success = self.i18n_manager.set_language(language_code)
                if success:
                    logger.info(f"Language changed to: {language_code}")
                    # UI 텍스트와 폰트가 자동으로 업데이트됨 (시그널 연결)
                else:
                    logger.error(f"Failed to change language to: {language_code}")
        except Exception as e:
            logger.error(f"Error changing language: {e}")
    
    def _on_theme_changed(self, theme_value: str):
        """테마 변경 처리"""
        try:
            if self.theme_manager:
                # 테마는 이미 settings dialog에서 적용되었으므로 
                # 여기서는 로그만 남기고 추가 처리는 하지 않음
                logger.info(f"Theme changed to: {theme_value}")
            else:
                logger.warning("Theme manager not available")
        except Exception as e:
            logger.error(f"Error processing theme change: {e}")
    
    def _on_settings_changed(self):
        """설정 변경시 처리"""
        try:
            # 설정 다시 로드
            self.config = self.config_manager.get_config()
            
            # 변환 매니저 출력 디렉토리 업데이트
            if hasattr(self.config, 'output_directory'):
                self.conversion_manager.output_directory = self.config.output_directory
            
            # 최근 디렉토리 업데이트
            self._update_recent_directories()
            
            # 상태바 메시지
            self.status_bar.showMessage("설정이 적용되었습니다", 3000)
            
            logger.info("설정이 성공적으로 적용되었습니다")
            
        except Exception as e:
            logger.error(f"설정 적용 실패: {e}")
            QMessageBox.warning(self, "경고", f"설정 적용 중 오류가 발생했습니다:\n{str(e)}")
    
    def _show_about(self):
        """정보 다이얼로그 표시"""
        QMessageBox.about(
            self,
            "프로그램 정보",
            "MarkItDown GUI Converter v0.1.0\n\n"
            "Microsoft MarkItDown 라이브러리를 사용하여\n"
            "다양한 문서를 검색해서 일괄 Markdown 변환하는 도구입니다."            
        )
    
    def _setup_i18n_connections(self):
        """i18n 시스템 연결"""
        if self.i18n_manager:
            self.i18n_manager.language_changed.connect(self._update_ui_texts)
            self.i18n_manager.language_changed.connect(self._apply_language_font)
    
    def _update_ui_texts(self):
        """UI 텍스트 업데이트 (번역 적용)"""
        if not self.i18n_manager:
            return
        
        # 창 제목
        self.setWindowTitle(tr("title", "window"))
        
        # 상태바 기본 메시지 
        self.status_bar.showMessage(tr("ready", "window"))
        
        # 디렉토리 그룹 (라벨은 이미 생성된 후라서 직접 업데이트)
        if hasattr(self, 'dir_label') and self.dir_label.text().startswith("디렉토리"):
            self.dir_label.setText(tr("label_placeholder", "directory"))
        
        logger.debug("UI texts updated for current language")
    
    def _apply_language_font(self):
        """현재 언어에 맞는 폰트 적용"""
        if not self.i18n_manager:
            return
            
        try:
            # 기본 폰트 사이즈 가져오기 (설정에서)
            base_font_size = getattr(self.config, 'font_size', 10)
            
            # 현재 언어에 최적화된 폰트 가져오기
            optimal_font = self.i18n_manager.get_current_font(base_font_size)
            
            # 안전한 폰트 적용 (DirectWrite 오류 방지)
            try:
                from ..core.font_manager import get_font_manager
                font_manager = get_font_manager()
                font_manager.set_application_font(optimal_font)
            except Exception as font_error:
                logger.warning(f"Font manager not available, using direct setting: {font_error}")
                # 기존 방식으로 fallback
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    app.setFont(optimal_font)
                
            logger.debug(f"Font applied: {optimal_font.family()}, {optimal_font.pointSize()}pt")
        except Exception as e:
            logger.warning(f"Failed to apply language font: {e}")
    
    def _restore_settings(self):
        """윈도우 설정 복원"""
        settings = QSettings()
        
        # 윈도우 크기와 위치 복원
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(self.config.window_width, self.config.window_height)
        
        # 윈도우 상태 복원
        window_state = settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
    
    def _save_settings(self):
        """윈도우 설정 저장"""
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # 설정 매니저에도 저장
        self.config_manager.save_config(self.config)
    
    def _setup_accessibility(self):
        """접근성 설정"""
        try:
            if not self.accessibility_manager:
                logger.warning("Accessibility manager not available")
                return
                
            # 메인 윈도우를 접근성 시스템에 등록
            self.accessibility_manager.register_widget(
                self,
                widget_id="main_window",
                accessible_name="MarkItDown GUI Converter",
                accessible_description="Microsoft MarkItDown 라이브러리를 사용하여 다양한 문서를 Markdown으로 변환하는 애플리케이션",
                help_text="F1키를 누르면 도움말을 볼 수 있습니다"
            )
            
            # 주요 UI 컴포넌트들을 접근성 시스템에 등록
            if hasattr(self, 'dir_label'):
                self.accessibility_manager.register_widget(
                    self.dir_label,
                    widget_id="directory_path_display",
                    accessible_name="선택된 디렉토리 경로",
                    accessible_description="현재 선택된 디렉토리의 경로가 표시됩니다"
                )
            
            if hasattr(self, 'browse_btn'):
                self.accessibility_manager.register_widget(
                    self.browse_btn,
                    widget_id="browse_directory_button",
                    accessible_name="디렉토리 찾아보기 버튼",
                    accessible_description="파일 탐색기를 열어 변환할 파일들이 있는 디렉토리를 선택합니다",
                    help_text="디렉토리를 선택하려면 클릭하거나 Ctrl+D를 누르세요"
                )
            
            if hasattr(self, 'scan_btn'):
                self.accessibility_manager.register_widget(
                    self.scan_btn,
                    widget_id="scan_files_button",
                    accessible_name="파일 스캔 버튼",
                    accessible_description="선택된 디렉토리에서 변환 가능한 파일들을 찾습니다",
                    help_text="파일 검색을 시작하려면 클릭하세요"
                )
            
            if hasattr(self, 'convert_btn'):
                self.accessibility_manager.register_widget(
                    self.convert_btn,
                    widget_id="convert_files_button", 
                    accessible_name="파일 변환 버튼",
                    accessible_description="선택된 파일들을 마크다운 형식으로 변환합니다",
                    help_text="파일 변환을 시작하려면 클릭하세요"
                )
            
            if hasattr(self, 'file_list_widget'):
                self.accessibility_manager.register_widget(
                    self.file_list_widget,
                    widget_id="file_list",
                    accessible_name="파일 목록",
                    accessible_description="변환 가능한 파일들의 목록입니다. 체크박스로 변환할 파일을 선택할 수 있습니다",
                    help_text="스페이스키로 선택/해제, Ctrl+A로 전체 선택, Ctrl+Shift+A로 전체 해제"
                )
            
            if hasattr(self, 'progress_widget'):
                self.accessibility_manager.register_widget(
                    self.progress_widget,
                    widget_id="conversion_progress",
                    accessible_name="변환 진행률",
                    accessible_description="파일 변환 작업의 진행 상황을 표시합니다"
                )
            
            if hasattr(self, 'log_widget'):
                self.accessibility_manager.register_widget(
                    self.log_widget,
                    widget_id="activity_log",
                    accessible_name="작업 로그",
                    accessible_description="애플리케이션의 작업 내역과 메시지들이 표시됩니다"
                )
                
                # 로그 위젯을 라이브 리전으로 등록
                if self.accessibility_manager.screen_reader_bridge:
                    from ..core.screen_reader_support import LiveRegionType, AnnouncementPriority
                    self.accessibility_manager.screen_reader_bridge.register_live_region(
                        self.log_widget,
                        region_type=LiveRegionType.LOG,
                        priority=AnnouncementPriority.POLITE,
                        label="작업 로그"
                    )
            
            # 키보드 네비게이션 컨텍스트 등록
            if self.keyboard_navigation:
                main_context = self.keyboard_navigation.register_context(self)
                
                # 스킵 링크 추가 (메인 콘텐츠로 바로가기)
                if hasattr(self, 'file_list_widget'):
                    self.keyboard_navigation.add_skip_link(
                        "main_content",
                        self.browse_btn,  # 소스: 첫 번째 버튼
                        self.file_list_widget  # 타겟: 메인 콘텐츠 영역
                    )
            
            # 접근성 기능 활성화
            accessibility_features = [
                AccessibilityFeature.KEYBOARD_NAVIGATION,
                AccessibilityFeature.SCREEN_READER,
                AccessibilityFeature.FOCUS_INDICATORS,
                AccessibilityFeature.TOOLTIPS,
                AccessibilityFeature.MOTOR_ACCESSIBILITY,
                AccessibilityFeature.ANNOUNCEMENTS
            ]
            
            for feature in accessibility_features:
                self.accessibility_manager.enable_feature(feature)
            
            # 상태 변경 알림 설정
            if hasattr(self, 'subdirs_check'):
                self.subdirs_check.toggled.connect(
                    lambda checked: self._announce_state_change(
                        "하위 디렉토리 포함", 
                        "활성화" if checked else "비활성화"
                    )
                )
            
            # 접근성 검증 수행 (개발 모드에서만)
            import os
            if os.getenv('MARKITDOWN_DEBUG'):
                QTimer.singleShot(2000, self._run_accessibility_validation)
            
            logger.info("접근성 설정 완료")
            
        except Exception as e:
            logger.error(f"접근성 설정 중 오류 발생: {e}")
    
    def _announce_state_change(self, element_name: str, new_state: str):
        """상태 변경 알림"""
        try:
            if self.accessibility_manager and self.accessibility_manager.screen_reader_bridge:
                message = f"{element_name} {new_state}"
                self.accessibility_manager.announce_message(message, "assertive")
        except Exception as e:
            logger.debug(f"상태 변경 알림 실패: {e}")
    
    def _run_accessibility_validation(self):
        """접근성 검증 실행 (개발용)"""
        try:
            if self.accessibility_manager and self.accessibility_manager.validator:
                result = self.accessibility_manager.validate_compliance()
                
                logger.info(f"접근성 검증 결과: {result.score:.1f}점")
                logger.info(f"총 {len(result.issues)}개 문제 발견")
                
                # 심각한 문제가 있으면 로그에 기록
                if result.critical_issues:
                    logger.warning(f"심각한 접근성 문제 {len(result.critical_issues)}개 발견")
                    for issue in result.critical_issues[:3]:  # 처음 3개만 표시
                        logger.warning(f"- {issue.title}: {issue.description}")
                
        except Exception as e:
            logger.error(f"접근성 검증 실행 중 오류: {e}")
    
    def closeEvent(self, event):
        """윈도우 닫기 이벤트 (향상된 정리 지원)"""
        # 진행 중인 작업 확인
        if self.file_manager.is_scanning() or self.conversion_manager.is_converting():
            reply = QMessageBox.question(
                self, "종료 확인",
                "작업이 진행 중입니다. 정말 종료하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # 작업 취소
            if self.file_manager.is_scanning():
                self.file_manager.cancel_scan()
            if self.conversion_manager.is_converting():
                self.conversion_manager.cancel_conversion()
        
        try:
            # 충돌 설정 저장
            self._save_conflict_config()
            
            # 테마 매니저 정리
            if self.theme_manager:
                self.theme_manager.save_settings()
            
            # 접근성 매니저 정리
            if self.accessibility_manager:
                self.accessibility_manager.cleanup()
            
            # 키보드 네비게이션 정리
            if self.keyboard_navigation:
                self.keyboard_navigation.cleanup()
            
            # 충돌 핸들러 정리
            if hasattr(self, 'conflict_handler') and self.conflict_handler:
                self.conflict_handler.cleanup()
            
            self._save_settings()
            logger.info("애플리케이션 종료 (직접 파일 저장 시스템 적용)")
            
        except Exception as e:
            logger.error(f"애플리케이션 종료 중 오류: {e}")
        
        event.accept()
    
    # 스캔 관련 이벤트 핸들러들
    def _on_scan_progress(self, current: int, total: int):
        """스캔 진행률 업데이트"""
        self.status_bar.showMessage(f"스캔 중... ({current}/{total})")
    
    def _on_file_found(self, file_info: FileInfo):
        """파일 발견시"""
        self.file_list_widget.add_file(file_info)
    
    def _on_scan_completed(self, file_infos: list):
        """스캔 완료시"""
        count = len(file_infos)
        self.status_bar.showMessage(f"스캔 완료: {count}개 파일 발견")
        self._reset_scan_ui()
        
        if count == 0:
            QMessageBox.information(
                self, "스캔 완료",
                "지원하는 파일을 찾을 수 없습니다.\n\n"
                "지원 형식: docx, pptx, xlsx, pdf, jpg, png, txt, html 등"
            )
        else:
            # 일부 파일을 기본 선택
            for file_info in file_infos[:5]:  # 처음 5개 파일 선택
                file_info.is_selected = True
            self.file_list_widget._update_count_display()
    
    def _on_scan_error(self, error_message: str):
        """스캔 오류시"""
        self.status_bar.showMessage("스캔 실패")
        self._reset_scan_ui()
        QMessageBox.critical(self, "스캔 오류", f"스캔 중 오류가 발생했습니다:\n{error_message}")
    
    def _reset_scan_ui(self):
        """스캔 UI 상태 리셋"""
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("파일 스캔")
    
    # 변환 관련 이벤트 핸들러들
    def _on_conversion_progress(self, progress):
        """변환 진행률 업데이트 (향상된 진행률 정보 포함)"""
        self.progress_widget.update_progress(progress)
        
        # 충돌 감지 시 상태바에 표시
        if hasattr(progress, 'conflicts_detected') and progress.conflicts_detected > 0:
            self.status_bar.showMessage(
                f"변환 중... ({progress.completed_files}/{progress.total_files}) - 충돌 {progress.conflicts_detected}건 감지"
            )
        elif hasattr(progress, 'current_status'):
            self.status_bar.showMessage(
                f"변환 중... ({progress.completed_files}/{progress.total_files}) - {progress.current_status}"
            )
        
        # 현재 단계별 처리 상황을 로그에 기록
        if hasattr(progress, 'current_progress_status'):
            logger.debug(f"변환 단계: {progress.current_progress_status.value} - {progress.current_status}")
    
    def _on_file_conversion_started(self, file_info: FileInfo):
        """파일 변환 시작시"""
        self.file_list_widget.update_file_status(file_info, ConversionStatus.IN_PROGRESS)
        logger.info(f"변환 시작: {file_info.name}")
    
    def _on_file_conversion_completed(self, result):
        """파일 변환 완료시"""
        file_info = result.file_info
        status = result.status
        
        self.file_list_widget.update_file_status(file_info, status)
        
        if result.is_success:
            logger.info(f"변환 성공: {file_info.name} -> {result.output_path.name}")
        else:
            logger.error(f"변환 실패: {file_info.name} - {result.error_message}")
    
    def _on_conversion_completed(self, results: list):
        """전체 변환 완료시 (향상된 직접 파일 저장 완료)"""
        success_count = len([r for r in results if r.is_success])
        total_count = len(results)
        
        # 충돌 통계 수집
        conflicts_resolved = 0
        files_renamed = 0
        files_overwritten = 0
        files_skipped = 0
        
        for result in results:
            if hasattr(result, 'conflict_status'):
                if result.conflict_status:
                    conflicts_resolved += 1
                    if 'renamed' in str(result.conflict_status).lower():
                        files_renamed += 1
                    elif 'overwritten' in str(result.conflict_status).lower():
                        files_overwritten += 1
                    elif 'skipped' in str(result.conflict_status).lower():
                        files_skipped += 1
        
        self._reset_conversion_ui()
        
        message = f"변환 완료: {success_count}/{total_count} 성공"
        if conflicts_resolved > 0:
            message += f", 충돌 {conflicts_resolved}건 해결"
        
        self.progress_widget.finish_progress(
            success=success_count > 0,
            message=message
        )
        
        # 상태바 업데이트
        self.status_bar.showMessage(message, 5000)
        
        # 상세 결과 요약 다이얼로그
        summary_text = f"변환이 완료되었습니다.\n\n"
        summary_text += f"총 파일: {total_count}개\n"
        summary_text += f"성공: {success_count}개\n"
        
        if success_count < total_count:
            failed_count = total_count - success_count
            summary_text += f"실패: {failed_count}개\n"
        
        if conflicts_resolved > 0:
            summary_text += f"\n충돌 해결:\n"
            if files_renamed > 0:
                summary_text += f"• 이름 변경: {files_renamed}개\n"
            if files_overwritten > 0:
                summary_text += f"• 덮어쓰기: {files_overwritten}개\n"
            if files_skipped > 0:
                summary_text += f"• 건너뛰기: {files_skipped}개\n"
        
        # 파일 저장 위치 정보
        if getattr(self.config, 'save_to_original_dir', True):
            summary_text += f"\n파일들이 원본과 같은 위치에 저장되었습니다."
        else:
            output_dir = getattr(self.config, 'output_directory', None)
            if output_dir:
                summary_text += f"\n파일들이 출력 폴더에 저장되었습니다: {output_dir}"
            else:
                default_dir = get_default_output_directory()
                summary_text += f"\n파일들이 기본 출력 폴더에 저장되었습니다: {default_dir}"
        
        if success_count == total_count:
            QMessageBox.information(self, "변환 완료", summary_text)
        else:
            summary_text += "\n\n자세한 내용은 로그를 확인해주세요."
            QMessageBox.warning(self, "변환 완료", summary_text)
        
        logger.info(f"변환 완료 - 성공: {success_count}, 실패: {total_count - success_count}, 충돌 해결: {conflicts_resolved}")
    
    def _on_conversion_error(self, error_message: str):
        """변환 오류시 (향상된 오류 처리)"""
        self._reset_conversion_ui()
        self.progress_widget.finish_progress(success=False, message="변환 오류")
        
        # 상세 오류 정보 제공
        error_details = f"변환 중 오류가 발생했습니다:\n\n{error_message}\n\n"
        
        # 일반적인 해결 방법 제안
        error_details += "해결 방법:\n"
        error_details += "• 파일이 다른 프로그램에서 사용 중인지 확인\n"
        error_details += "• 파일 권한 및 디스크 공간 확인\n"
        error_details += "• 마크다운 라이브러리 재설치 (pip install --upgrade markitdown)\n"
        error_details += "• 충돌 정책 변경 (자동 이름 변경 가능)"
        
        QMessageBox.critical(self, "변환 오류", error_details)
        
        logger.error(f"변환 오류: {error_message}")
    
    def _on_conversion_cancel_requested(self):
        """변환 취소 요청시"""
        if self.conversion_manager.is_converting():
            reply = QMessageBox.question(
                self, "변환 취소",
                "변환을 취소하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.conversion_manager.cancel_conversion()
    
    def _reset_conversion_ui(self):
        """변환 UI 상태 리셋"""
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("선택된 파일 변환")
    
    def _setup_performance_optimization(self):
        """성능 최적화 설정"""
        try:
            # 주요 위젯들 성능 최적화
            widgets_to_optimize = [
                self.file_list_widget,
                self.progress_widget,
                self.log_widget
            ]
            
            for widget in widgets_to_optimize:
                if widget:
                    self.performance_optimizer.optimize_widget(widget)
            
            # 성능 모니터 연결
            self.performance_optimizer.performance_alert.connect(self._on_performance_alert)
            
            # UI 업데이트 제한기 연결
            self.performance_optimizer.update_throttler.update_requested.connect(self._on_throttled_update)
            
            # 비동기 작업 관리자 연결
            self.performance_optimizer.async_manager.task_started.connect(self._on_async_task_started)
            self.performance_optimizer.async_manager.task_progress.connect(self._on_async_task_progress)
            self.performance_optimizer.async_manager.task_completed.connect(self._on_async_task_completed)
            self.performance_optimizer.async_manager.task_failed.connect(self._on_async_task_failed)
            
            logger.info("성능 최적화 설정 완료")
            
        except Exception as e:
            logger.error(f"성능 최적화 설정 오류: {e}")
    
    def _on_performance_alert(self, operation_name: str, duration_ms: float):
        """성능 경고 처리"""
        logger.warning(f"느린 작업 감지: {operation_name} - {duration_ms:.1f}ms")
        
        # 매우 느린 작업의 경우 사용자에게 알림
        if duration_ms > 5000:  # 5초 이상
            self.status_bar.showMessage(
                f"느린 작업이 감지되었습니다: {operation_name}", 3000
            )
    
    def _on_throttled_update(self, update_data):
        """제한된 UI 업데이트 처리"""
        # 업데이트 데이터에 따른 처리
        if isinstance(update_data, dict):
            update_type = update_data.get('type')
            
            if update_type == 'file_list_update':
                # 파일 목록 업데이트
                files = update_data.get('files', [])
                self._update_file_list_display(files)
                
            elif update_type == 'progress_update':
                # 진행률 업데이트
                progress = update_data.get('progress', 0)
                message = update_data.get('message', '')
                self._update_progress_display(progress, message)
                
            elif update_type == 'status_update':
                # 상태 메시지 업데이트
                message = update_data.get('message', '')
                timeout = update_data.get('timeout', 0)
                self.status_bar.showMessage(message, timeout)
    
    def _update_file_list_display(self, files):
        """파일 목록 표시 업데이트"""
        if hasattr(self, 'file_list_widget'):
            with self.performance_optimizer.measure_operation("file_list_update"):
                # 대량 업데이트를 위한 배치 처리
                def batch_update(widgets):
                    self.file_list_widget.set_files(files)
                
                self.performance_optimizer.rendering_optimizer.batch_widget_updates(
                    [self.file_list_widget], batch_update
                )
    
    def _update_progress_display(self, progress: int, message: str):
        """진행률 표시 업데이트"""
        if hasattr(self, 'progress_widget'):
            self.progress_widget.update_progress(progress, message)
    
    def _on_async_task_started(self, task_id: str, description: str):
        """비동기 작업 시작"""
        logger.info(f"비동기 작업 시작: {task_id} - {description}")
        self.status_bar.showMessage(f"작업 시작: {description}")
    
    def _on_async_task_progress(self, task_id: str, progress: int):
        """비동기 작업 진행률"""
        # 진행률 업데이트를 throttling으로 처리
        self.performance_optimizer.throttled_update({
            'type': 'async_progress',
            'task_id': task_id,
            'progress': progress
        })
    
    def _on_async_task_completed(self, task_id: str, result):
        """비동기 작업 완료"""
        logger.info(f"비동기 작업 완료: {task_id}")
        self.status_bar.showMessage("작업 완료", 2000)
    
    def _on_async_task_failed(self, task_id: str, error_message: str):
        """비동기 작업 실패"""
        logger.error(f"비동기 작업 실패: {task_id} - {error_message}")
        self.status_bar.showMessage(f"작업 실패: {error_message}", 5000)
    
    def execute_async_scan(self):
        """비동기 디렉토리 스캔"""
        if not hasattr(self, 'current_directory'):
            QMessageBox.warning(self, "경고", "디렉토리를 먼저 선택해주세요.")
            return
        
        def scan_task(progress_callback=None):
            """스캔 작업 함수"""
            try:
                # 스캔 실행
                files = []
                # 여기에 실제 스캔 로직을 구현
                # progress_callback을 사용하여 진행률 업데이트
                
                return files
            except Exception as e:
                logger.error(f"비동기 스캔 실패: {e}")
                raise
        
        # 비동기 작업 시작
        self.performance_optimizer.execute_async(
            scan_task,
            "디렉토리 스캔 중..."
        )
    
    def get_performance_report(self) -> dict:
        """성능 보고서 생성"""
        return self.performance_optimizer.get_responsiveness_report()
    
    def closeEvent(self, event):
        """윈도우 닫기 이벤트"""
        try:
            # 성능 최적화기 정리
            if hasattr(self, 'performance_optimizer'):
                self.performance_optimizer.cleanup()
            
            # 설정 저장
            self._save_settings()
            
            # 매니저들 정리
            if hasattr(self, 'file_manager') and self.file_manager.is_scanning():
                self.file_manager.cancel_scan()
            
            if hasattr(self, 'conversion_manager') and self.conversion_manager.is_converting():
                self.conversion_manager.cancel_conversion()
            
            event.accept()
            
        except Exception as e:
            logger.error(f"윈도우 종료 중 오류: {e}")
            event.accept()  # 오류가 있어도 종료
    
    def _load_conflict_config(self) -> FileConflictConfig:
        """충돌 설정 로드"""
        try:
            settings = QSettings()
            policy_value = settings.value("conversion/conflict_policy", FileConflictPolicy.RENAME.value)
            policy = FileConflictPolicy(policy_value)
            
            return FileConflictConfig(
                default_policy=policy,
                ask_user_timeout=settings.value("conversion/ask_user_timeout", 30),
                preserve_original=settings.value("conversion/preserve_original", False, bool),
                backup_existing=settings.value("conversion/backup_existing", True, bool)
            )
        except Exception as e:
            logger.warning(f"충돌 설정 로드 실패, 기본값 사용: {e}")
            return FileConflictConfig()
    
    def _save_conflict_config(self):
        """충돌 설정 저장"""
        try:
            settings = QSettings()
            settings.setValue("conversion/conflict_policy", self.conflict_config.default_policy.value)
            settings.setValue("conversion/ask_user_timeout", self.conflict_config.ask_user_timeout)
            settings.setValue("conversion/preserve_original", self.conflict_config.preserve_original)
            settings.setValue("conversion/backup_existing", self.conflict_config.backup_existing)
            settings.sync()
        except Exception as e:
            logger.error(f"충돌 설정 저장 실패: {e}")
    
    def _set_conflict_policy(self, policy: FileConflictPolicy):
        """충돌 정책 설정"""
        self.conflict_config.default_policy = policy
        self._save_conflict_config()
        self._update_conflict_status_display()
        self._update_conflict_policy_menu()
        
        policy_names = {
            FileConflictPolicy.RENAME: "자동 이름 변경",
            FileConflictPolicy.OVERWRITE: "덮어쓰기",
            FileConflictPolicy.SKIP: "건너뛰기",
            FileConflictPolicy.ASK_USER: "사용자에게 묻기"
        }
        
        self.status_bar.showMessage(f"충돌 정책이 '{policy_names[policy]}'로 변경되었습니다.", 3000)
        logger.info(f"충돌 정책 변경: {policy.value}")
    
    def _update_conflict_status_display(self):
        """충돌 상태 표시 업데이트"""
        policy_names = {
            FileConflictPolicy.RENAME: "자동 이름 변경",
            FileConflictPolicy.OVERWRITE: "덮어쓰기",
            FileConflictPolicy.SKIP: "건너뛰기",
            FileConflictPolicy.ASK_USER: "사용자에게 묻기"
        }
        
        policy_name = policy_names.get(self.conflict_config.default_policy, "알 수 없음")
        self.conflict_status_label.setText(f"충돌 정책: {policy_name}")
    
    def _update_conflict_policy_menu(self):
        """충돌 정책 메뉴 업데이트"""
        # 모든 액션 체크 해제
        for action in [self.auto_rename_action, self.overwrite_action, self.skip_action, self.ask_user_action]:
            action.setChecked(False)
        
        # 현재 정책에 해당하는 액션 체크
        policy_actions = {
            FileConflictPolicy.RENAME: self.auto_rename_action,
            FileConflictPolicy.OVERWRITE: self.overwrite_action,
            FileConflictPolicy.SKIP: self.skip_action,
            FileConflictPolicy.ASK_USER: self.ask_user_action
        }
        
        current_action = policy_actions.get(self.conflict_config.default_policy)
        if current_action:
            current_action.setChecked(True)
    
    def _show_basic_conversion_settings(self):
        """기본 변환 설정 다이얼로그"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QCheckBox, QSpinBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("변환 설정")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 폼 레이아웃
        form_layout = QFormLayout()
        
        # 충돌 정책 선택
        policy_combo = QComboBox()
        policy_combo.addItem("자동 이름 변경", FileConflictPolicy.RENAME)
        policy_combo.addItem("덮어쓰기", FileConflictPolicy.OVERWRITE)
        policy_combo.addItem("건너뛰기", FileConflictPolicy.SKIP)
        policy_combo.addItem("사용자에게 묻기", FileConflictPolicy.ASK_USER)
        
        # 현재 정책 선택
        for i in range(policy_combo.count()):
            if policy_combo.itemData(i) == self.conflict_config.default_policy:
                policy_combo.setCurrentIndex(i)
                break
        
        form_layout.addRow("파일 충돌 시:", policy_combo)
        
        # 기타 설정
        backup_check = QCheckBox()
        backup_check.setChecked(self.conflict_config.backup_existing)
        form_layout.addRow("기존 파일 백업:", backup_check)
        
        timeout_spin = QSpinBox()
        timeout_spin.setRange(5, 300)
        timeout_spin.setValue(self.conflict_config.ask_user_timeout)
        timeout_spin.setSuffix("초")
        form_layout.addRow("사용자 응답 대기시간:", timeout_spin)
        
        layout.addLayout(form_layout)
        
        # 버튼들
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 설정 적용
            self.conflict_config.default_policy = policy_combo.currentData()
            self.conflict_config.backup_existing = backup_check.isChecked()
            self.conflict_config.ask_user_timeout = timeout_spin.value()
            
            self._save_conflict_config()
            self._update_conflict_status_display()
            self._update_conflict_policy_menu()
    
    def _set_window_icon(self):
        """윈도우 아이콘 설정"""
        try:
            from pathlib import Path
            
            # 아이콘 파일 경로들 (우선순위 순)
            icon_paths = [
                Path("resources/icons/app_icon.png"),  # 루트 resources 디렉토리
                Path("markitdown_gui/resources/icons/app_icon.png"),  # GUI 리소스 디렉토리
                Path("markitdown.png"),  # 원본 파일
            ]
            
            # 첫 번째로 존재하는 아이콘 파일 사용
            for icon_path in icon_paths:
                if icon_path.exists():
                    icon = QIcon(str(icon_path))
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        logger.info(f"윈도우 아이콘 설정 완료: {icon_path}")
                        return
                    else:
                        logger.warning(f"아이콘 파일을 로드할 수 없음: {icon_path}")
                else:
                    logger.debug(f"아이콘 파일 없음: {icon_path}")
            
            logger.warning("사용 가능한 아이콘 파일을 찾을 수 없음")
            
        except Exception as e:
            logger.error(f"윈도우 아이콘 설정 실패: {e}")