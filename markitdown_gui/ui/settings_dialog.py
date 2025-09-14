"""
설정 다이얼로그
애플리케이션 설정을 관리하는 다이얼로그
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QFormLayout, QLineEdit, QPushButton, 
    QSpinBox, QCheckBox, QComboBox, QTextEdit, QLabel,
    QFileDialog, QMessageBox, QSlider, QSpacerItem,
    QSizePolicy, QColorDialog
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QColor

from ..core.config_manager import ConfigManager
from ..core.logger import get_logger
from ..core.models import FileConflictPolicy, FileConflictConfig
from ..core.i18n_manager import get_i18n_manager, tr
from ..core.theme_manager import get_theme_manager, ThemeType
from ..core.constants import (
    MIN_FONT_SIZE, MAX_FONT_SIZE, DEFAULT_FONT_SIZE,
    ErrorMessages, SuccessMessages, MARKDOWN_OUTPUT_DIR
)
from ..core.exceptions import (
    ConfigurationError, ValidationError, ExceptionContext
)
from ..core.utils import get_default_output_directory


logger = get_logger(__name__)


class GeneralSettingsTab(QWidget):
    """일반 설정 탭"""
    
    # 시그널
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)  # theme_type
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.i18n_manager = get_i18n_manager()
        self.theme_manager = get_theme_manager()
        self._init_ui()
        self._load_settings()
        self._setup_connections()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 언어 설정
        self.language_group = QGroupBox()
        language_layout = QFormLayout(self.language_group)
        
        self.language_combo = QComboBox()
        self.language_label = QLabel()
        
        # i18n 매니저에서 지원되는 언어 목록 가져오기
        if self.i18n_manager:
            supported_languages = self.i18n_manager.get_supported_languages()
            for lang_code, lang_info in supported_languages.items():
                display_name = f"{lang_info.native_name} ({lang_info.name})"
                self.language_combo.addItem(display_name, lang_code)
        else:
            # 기본 언어들 (i18n 매니저가 없는 경우)
            self.language_combo.addItem("한국어 (Korean)", "ko_KR")
            self.language_combo.addItem("English", "en_US")
        
        language_layout.addRow(self.language_label, self.language_combo)
        
        layout.addWidget(self.language_group)
        
        # 디렉토리 설정
        directory_group = QGroupBox("디렉토리 설정")
        directory_layout = QFormLayout(directory_group)
        
        # 기본 출력 디렉토리
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        # Set placeholder text to show the default markdown directory
        self.output_dir_edit.setPlaceholderText(f"기본값: 프로그램 폴더/{MARKDOWN_OUTPUT_DIR}")
        self.output_dir_btn = QPushButton("찾아보기")
        self.output_dir_btn.clicked.connect(self._browse_output_directory)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.output_dir_btn)
        directory_layout.addRow("출력 디렉토리:", output_layout)
        
        # Add help text for output directory
        output_help = QLabel("비워두면 프로그램 폴더의 'markdown' 디렉토리가 기본값으로 사용됩니다.")
        output_help.setStyleSheet("color: #666; font-size: 9px;")
        output_help.setWordWrap(True)
        directory_layout.addRow("", output_help)
        
        # 로그 디렉토리
        log_layout = QHBoxLayout()
        self.log_dir_edit = QLineEdit()
        self.log_dir_btn = QPushButton("찾아보기")
        self.log_dir_btn.clicked.connect(self._browse_log_directory)
        log_layout.addWidget(self.log_dir_edit)
        log_layout.addWidget(self.log_dir_btn)
        directory_layout.addRow("로그 디렉토리:", log_layout)
        
        layout.addWidget(directory_group)
        
        # UI 설정
        ui_group = QGroupBox("사용자 인터페이스")
        ui_layout = QFormLayout(ui_group)
        
        # 테마 설정
        theme_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        
        # 테마 매니저에서 사용 가능한 테마 목록 가져오기
        if self.theme_manager:
            available_themes = self.theme_manager.get_available_themes()
            for theme_type, display_name in available_themes.items():
                self.theme_combo.addItem(display_name, theme_type.value)
        else:
            # 기본 테마 목록 (테마 매니저가 없는 경우)
            self.theme_combo.addItem("시스템 기본", ThemeType.FOLLOW_SYSTEM.value)
            self.theme_combo.addItem("라이트 테마", ThemeType.LIGHT.value)
            self.theme_combo.addItem("다크 테마", ThemeType.DARK.value)
            self.theme_combo.addItem("고대비 테마", ThemeType.HIGH_CONTRAST.value)
        
        theme_layout.addWidget(self.theme_combo)
        
        # 액센트 색상 설정
        accent_layout = QHBoxLayout()
        accent_label = QLabel("액센트 색상:")
        
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setMaximumWidth(50)
        self.accent_color_btn.setMaximumHeight(25)
        self.accent_color_btn.clicked.connect(self._choose_accent_color)
        
        self.accent_color_label = QLabel("#3B82F6")  # 기본값
        self.accent_color_label.setStyleSheet("padding: 4px; border: 1px solid #ccc; background-color: white;")
        
        accent_layout.addWidget(accent_label)
        accent_layout.addWidget(self.accent_color_btn)
        accent_layout.addWidget(self.accent_color_label)
        accent_layout.addStretch()
        
        theme_layout.addLayout(accent_layout)
        ui_layout.addRow("테마:", theme_layout)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.font_size_spin.setValue(DEFAULT_FONT_SIZE)
        self.font_size_spin.setSuffix("pt")
        ui_layout.addRow("폰트 크기:", self.font_size_spin)
        
        self.auto_save_check = QCheckBox("자동 저장 활성화")
        ui_layout.addRow(self.auto_save_check)
        
        layout.addWidget(ui_group)
        
        # 시작 설정
        startup_group = QGroupBox("시작 설정")
        startup_layout = QFormLayout(startup_group)
        
        self.remember_window_check = QCheckBox("창 크기와 위치 기억")
        startup_layout.addRow(self.remember_window_check)
        
        self.restore_session_check = QCheckBox("마지막 세션 복원")
        startup_layout.addRow(self.restore_session_check)
        
        self.check_updates_check = QCheckBox("시작시 업데이트 확인")
        startup_layout.addRow(self.check_updates_check)
        
        layout.addWidget(startup_group)
        
        layout.addStretch()
        
        # 초기 UI 텍스트 설정
        self._update_ui_texts()
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        
        # i18n 매니저의 언어 변경 시그널 연결
        if self.i18n_manager:
            self.i18n_manager.language_changed.connect(self._update_ui_texts)
        
        # 테마 매니저의 시그널 연결
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_manager_changed)
            self.theme_manager.accent_changed.connect(self._on_accent_changed)
    
    def _update_ui_texts(self):
        """UI 텍스트 업데이트 (번역 적용)"""
        # 언어 설정 그룹
        self.language_group.setTitle(tr("language_group", "settings.general"))
        self.language_label.setText(tr("language_label", "settings.general"))
        
        # 디렉토리 설정은 기존 그대로 (하드코딩된 텍스트이므로 나중에 업데이트)
        # 여기서는 언어 변경에 대한 기본 구조만 설정
    
    def _on_language_changed(self, language_text: str):
        """언어 변경 핸들러"""
        if self.i18n_manager:
            # 콤보박스에서 선택된 언어 코드 가져오기
            current_index = self.language_combo.currentIndex()
            if current_index >= 0:
                language_code = self.language_combo.itemData(current_index)
                if language_code and language_code != self.i18n_manager.get_current_language():
                    # 언어 변경
                    success = self.i18n_manager.set_language(language_code)
                    if success:
                        self.language_changed.emit(language_code)
                        logger.info(f"Language changed to: {language_code}")
    
    def _on_theme_changed(self, theme_text: str):
        """테마 변경 핸들러"""
        if self.theme_manager:
            # 콤보박스에서 선택된 테마 데이터 가져오기
            current_index = self.theme_combo.currentIndex()
            if current_index >= 0:
                theme_value = self.theme_combo.itemData(current_index)
                if theme_value:
                    try:
                        theme_type = ThemeType(theme_value)
                        current_theme = self.theme_manager.get_current_theme()
                        
                        if theme_type != current_theme:
                            # 테마 변경 시그널 발송 (즉시 적용을 위해)
                            self.theme_changed.emit(theme_value)
                            logger.info(f"Theme selection changed to: {theme_value}")
                    except ValueError:
                        logger.warning(f"Invalid theme value: {theme_value}")
    
    def _on_theme_manager_changed(self, theme_name: str):
        """테마 매니저에서 테마가 변경되었을 때"""
        # 콤보박스 선택을 업데이트
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme_name:
                self.theme_combo.setCurrentIndex(i)
                break
    
    def _on_accent_changed(self, color: str):
        """액센트 색상이 변경되었을 때"""
        self._update_accent_color_display(color)
    
    def _choose_accent_color(self):
        """액센트 색상 선택 다이얼로그"""
        if not self.theme_manager:
            return
        
        # 현재 액센트 색상 가져오기
        current_color = self.theme_manager.get_current_accent()
        color = QColorDialog.getColor(
            QColor(current_color),
            self,
            "액센트 색상 선택"
        )
        
        if color.isValid():
            color_hex = color.name()
            # 테마 매니저에 색상 설정은 저장 시에 처리 (실시간 변경은 성능상 부담)
            self._update_accent_color_display(color_hex)
    
    def _update_accent_color_display(self, color: str):
        """액센트 색상 표시 업데이트"""
        # 색상 버튼과 라벨 업데이트
        self.accent_color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
        self.accent_color_label.setText(color)
    
    def _browse_output_directory(self):
        """출력 디렉토리 선택"""
        # If current text is empty, use the default directory as starting point
        current_text = self.output_dir_edit.text()
        if not current_text:
            start_dir = str(get_default_output_directory())
        else:
            start_dir = current_text
            
        directory = QFileDialog.getExistingDirectory(
            self, "출력 디렉토리 선택", start_dir
        )
        if directory:
            self.output_dir_edit.setText(directory)
    
    def _browse_log_directory(self):
        """로그 디렉토리 선택"""
        directory = QFileDialog.getExistingDirectory(
            self, "로그 디렉토리 선택", self.log_dir_edit.text()
        )
        if directory:
            self.log_dir_edit.setText(directory)
    
    def _load_settings(self):
        """설정 로드"""
        config = self.config_manager.get_config()
        
        # 언어 설정 - i18n 매니저에서 현재 언어 가져오기
        if self.i18n_manager:
            current_language = self.i18n_manager.get_current_language()
            # 콤보박스에서 해당 언어 찾기
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == current_language:
                    self.language_combo.setCurrentIndex(i)
                    break
        else:
            # 기본값 설정 (첫 번째 항목)
            self.language_combo.setCurrentIndex(0)
        
        # 디렉토리 설정 - 기본값이 설정되어 있지 않으면 빈 문자열로 표시 (플레이스홀더가 기본값을 보여줌)
        output_dir = config.get("output_directory", "")
        # Only show non-default values in the text field
        default_output = get_default_output_directory()
        if output_dir and str(output_dir) != str(default_output):
            self.output_dir_edit.setText(str(output_dir))
        else:
            self.output_dir_edit.setText("")  # Use placeholder to show default
        log_dir = config.get("log_directory", "")
        self.log_dir_edit.setText(str(log_dir) if log_dir else "")
        
        # 테마 설정
        if self.theme_manager:
            # 현재 테마 설정 로드
            current_theme = self.theme_manager.get_current_theme()
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == current_theme.value:
                    self.theme_combo.setCurrentIndex(i)
                    break
            
            # 현재 액센트 색상 표시
            current_accent = self.theme_manager.get_current_accent()
            self._update_accent_color_display(current_accent)
        else:
            # 기본 테마 매핑 (하위 호환성)
            theme_map = {"system": 0, "light": 1, "dark": 2, "follow_system": 0}
            theme_value = config.get("theme", "follow_system")
            self.theme_combo.setCurrentIndex(theme_map.get(theme_value, 0))
        
        self.font_size_spin.setValue(config.get("font_size", 10))
        self.auto_save_check.setChecked(config.get("auto_save", True))
        
        # 시작 설정
        self.remember_window_check.setChecked(config.get("remember_window", True))
        self.restore_session_check.setChecked(config.get("restore_session", False))
        self.check_updates_check.setChecked(config.get("check_updates", True))
    
    def save_settings(self) -> Dict[str, Any]:
        """설정 저장"""
        # 현재 선택된 언어 코드 가져오기
        current_index = self.language_combo.currentIndex()
        language_code = "en_US"  # 기본값
        if current_index >= 0:
            language_code = self.language_combo.itemData(current_index) or "en_US"
        
        # 현재 선택된 테마 가져오기
        theme_index = self.theme_combo.currentIndex()
        theme_value = "follow_system"  # 기본값
        if theme_index >= 0:
            theme_value = self.theme_combo.itemData(theme_index) or "follow_system"
        
        # 테마 매니저에 테마와 액센트 색상 적용
        if self.theme_manager:
            try:
                # 테마 적용
                theme_type = ThemeType(theme_value)
                self.theme_manager.set_theme(theme_type)
                
                # 액센트 색상 적용
                accent_color = self.accent_color_label.text()
                if accent_color and accent_color != self.theme_manager.get_current_accent():
                    self.theme_manager.set_accent_color(accent_color)
                    
            except (ValueError, Exception) as e:
                logger.warning(f"Failed to apply theme settings: {e}")
        
        return {
            "language": language_code,
            "output_directory": self.output_dir_edit.text(),
            "log_directory": self.log_dir_edit.text(),
            "theme": theme_value,
            "accent_color": self.accent_color_label.text(),
            "font_size": self.font_size_spin.value(),
            "auto_save": self.auto_save_check.isChecked(),
            "remember_window": self.remember_window_check.isChecked(),
            "restore_session": self.restore_session_check.isChecked(),
            "check_updates": self.check_updates_check.isChecked()
        }


class ConversionSettingsTab(QWidget):
    """변환 설정 탭"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self._init_ui()
        self._load_settings()
        self._setup_connections()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 변환 옵션
        conversion_group = QGroupBox("변환 옵션")
        conversion_layout = QFormLayout(conversion_group)
        
        self.include_metadata_check = QCheckBox("메타데이터 포함")
        conversion_layout.addRow(self.include_metadata_check)
        
        self.preserve_formatting_check = QCheckBox("포맷팅 유지")
        conversion_layout.addRow(self.preserve_formatting_check)
        
        self.extract_images_check = QCheckBox("이미지 추출")
        conversion_layout.addRow(self.extract_images_check)
        
        self.include_toc_check = QCheckBox("목차 생성")
        conversion_layout.addRow(self.include_toc_check)
        
        layout.addWidget(conversion_group)
        
        # 파일 충돌 처리 설정
        conflict_group = QGroupBox("파일 충돌 처리")
        conflict_layout = QFormLayout(conflict_group)
        
        # 기본 충돌 처리 정책
        policy_layout = QHBoxLayout()
        self.default_policy_combo = QComboBox()
        self.default_policy_combo.addItem("사용자에게 묻기", "ask_user")
        self.default_policy_combo.addItem("건너뛰기", "skip")
        self.default_policy_combo.addItem("덮어쓰기", "overwrite")
        self.default_policy_combo.addItem("이름 변경", "rename")
        self.default_policy_combo.setToolTip("파일 충돌이 발생했을 때 기본 처리 방법을 선택합니다.")
        
        self.policy_help_btn = QPushButton("도움말")
        self.policy_help_btn.setMaximumWidth(80)
        self.policy_help_btn.clicked.connect(self._show_policy_help)
        
        policy_layout.addWidget(self.default_policy_combo)
        policy_layout.addWidget(self.policy_help_btn)
        conflict_layout.addRow("기본 처리 방법:", policy_layout)
        
        # 자동 이름 변경 패턴
        rename_pattern_layout = QHBoxLayout()
        self.rename_pattern_edit = QLineEdit("{name}_{counter}{ext}")
        self.rename_pattern_edit.setToolTip(
            "파일 이름 변경 패턴을 설정합니다.\n"
            "{name}: 원본 파일명, {counter}: 순서 번호, {ext}: 확장자"
        )
        
        self.pattern_preview_btn = QPushButton("미리보기")
        self.pattern_preview_btn.setMaximumWidth(80)
        self.pattern_preview_btn.clicked.connect(self._show_rename_preview)
        
        rename_pattern_layout.addWidget(self.rename_pattern_edit)
        rename_pattern_layout.addWidget(self.pattern_preview_btn)
        conflict_layout.addRow("이름 변경 패턴:", rename_pattern_layout)
        
        # 충돌 처리 행동 옵션
        self.remember_choices_check = QCheckBox("사용자 선택 기억하기")
        self.remember_choices_check.setToolTip("동일한 충돌에 대해 이전 선택을 기억합니다.")
        conflict_layout.addRow(self.remember_choices_check)
        
        self.apply_to_all_check = QCheckBox("모든 파일에 같은 방법 적용")
        self.apply_to_all_check.setToolTip("충돌 처리 방법을 모든 파일에 일괄 적용합니다.")
        conflict_layout.addRow(self.apply_to_all_check)
        
        # 백업 및 로깅
        self.backup_original_check = QCheckBox("원본 파일 백업 생성")
        self.backup_original_check.setToolTip("파일을 덮어쓸 때 원본 파일의 백업을 생성합니다.")
        conflict_layout.addRow(self.backup_original_check)
        
        self.conflict_log_check = QCheckBox("충돌 처리 로그 기록")
        self.conflict_log_check.setToolTip("파일 충돌 처리 과정을 로그에 기록합니다.")
        conflict_layout.addRow(self.conflict_log_check)
        
        layout.addWidget(conflict_group)
        
        # 저장 위치 설정
        location_group = QGroupBox("저장 위치 설정")
        location_layout = QFormLayout(location_group)
        
        self.save_to_original_check = QCheckBox("원본 디렉토리에 저장")
        self.save_to_original_check.setToolTip("변환된 파일을 원본 파일과 같은 디렉토리에 저장합니다.")
        location_layout.addRow(self.save_to_original_check)
        
        # 커스텀 출력 디렉토리
        output_layout = QHBoxLayout()
        self.custom_output_edit = QLineEdit()
        self.custom_output_edit.setPlaceholderText(f"기본값: 프로그램 폴더/{MARKDOWN_OUTPUT_DIR}")
        self.custom_output_edit.setEnabled(False)  # 초기에는 비활성화
        self.custom_output_edit.setToolTip("원본 디렉토리에 저장하지 않을 때 사용할 출력 디렉토리를 지정합니다. 비워두면 프로그램 폴더의 'markdown' 디렉토리가 사용됩니다.")
        self.browse_output_btn = QPushButton("찾아보기")
        self.browse_output_btn.setEnabled(False)
        self.browse_output_btn.clicked.connect(self._browse_custom_output)
        
        output_layout.addWidget(self.custom_output_edit)
        output_layout.addWidget(self.browse_output_btn)
        location_layout.addRow("커스텀 출력 디렉토리:", output_layout)
        
        layout.addWidget(location_group)
        
        # 파일 처리
        processing_group = QGroupBox("파일 처리")
        processing_layout = QFormLayout(processing_group)
        
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 16)
        processing_layout.addRow("최대 작업자 수:", self.max_workers_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setSuffix("초")
        processing_layout.addRow("변환 타임아웃:", self.timeout_spin)
        
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(0, 5)
        processing_layout.addRow("재시도 횟수:", self.retry_count_spin)
        
        layout.addWidget(processing_group)
        
        # 품질 설정
        quality_group = QGroupBox("품질 설정")
        quality_layout = QFormLayout(quality_group)
        
        self.ocr_quality_combo = QComboBox()
        self.ocr_quality_combo.addItems(["낮음", "보통", "높음", "최고"])
        quality_layout.addRow("OCR 품질:", self.ocr_quality_combo)
        
        self.image_quality_spin = QSpinBox()
        self.image_quality_spin.setRange(1, 100)
        self.image_quality_spin.setSuffix("%")
        quality_layout.addRow("이미지 품질:", self.image_quality_spin)
        
        layout.addWidget(quality_group)
        
        # 출력 형식
        output_group = QGroupBox("출력 형식")
        output_layout = QFormLayout(output_group)
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["UTF-8", "UTF-16", "ASCII"])
        output_layout.addRow("인코딩:", self.encoding_combo)
        
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["시스템 기본", "LF (\\n)", "CRLF (\\r\\n)"])
        output_layout.addRow("줄 끝 문자:", self.line_ending_combo)
        
        layout.addWidget(output_group)
        
        layout.addStretch()
    
    def _setup_connections(self):
        """시그널-슬롯 연결 설정"""
        # 저장 위치 설정 연결
        self.save_to_original_check.toggled.connect(self._on_save_location_changed)
        
        # 패턴 입력 필드 실시간 업데이트
        self.rename_pattern_edit.textChanged.connect(self._validate_rename_pattern)
    
    def _on_save_location_changed(self, checked: bool):
        """저장 위치 설정 변경 핸들러"""
        # 원본 디렉토리에 저장하지 않을 때만 커스텀 출력 디렉토리 활성화
        self.custom_output_edit.setEnabled(not checked)
        self.browse_output_btn.setEnabled(not checked)
        
        if checked:
            self.custom_output_edit.clear()
    
    def _browse_custom_output(self):
        """커스텀 출력 디렉토리 선택"""
        # If current text is empty, use the default directory as starting point
        current_text = self.custom_output_edit.text()
        if not current_text:
            start_dir = str(get_default_output_directory())
        else:
            start_dir = current_text
            
        directory = QFileDialog.getExistingDirectory(
            self, "출력 디렉토리 선택", start_dir
        )
        if directory:
            self.custom_output_edit.setText(directory)
    
    def _validate_rename_pattern(self, text: str):
        """이름 변경 패턴 유효성 검사"""
        required_placeholders = ["{name}", "{ext}"]
        is_valid = all(placeholder in text for placeholder in required_placeholders)
        
        # 시각적 피드백 제공
        if is_valid or not text:
            self.rename_pattern_edit.setStyleSheet("")
            self.pattern_preview_btn.setEnabled(True)
        else:
            self.rename_pattern_edit.setStyleSheet("QLineEdit { border: 1px solid red; }")
            self.pattern_preview_btn.setEnabled(False)
    
    def _show_rename_preview(self):
        """이름 변경 패턴 미리보기"""
        pattern = self.rename_pattern_edit.text()
        if not pattern:
            pattern = "{name}_{counter}{ext}"
        
        # 예시 파일명들로 미리보기 생성
        examples = [
            ("document.md", "document_1.md"),
            ("presentation.md", "presentation_1.md"),
            ("report.md", "report_1.md")
        ]
        
        preview_text = "이름 변경 패턴 미리보기:\n\n"
        for original, _ in examples:
            name = Path(original).stem
            ext = Path(original).suffix
            renamed = pattern.format(name=name, counter=1, ext=ext)
            preview_text += f"{original} → {renamed}\n"
        
        preview_text += f"\n패턴: {pattern}\n"
        preview_text += "사용 가능한 플레이스홀더:\n"
        preview_text += "• {name}: 파일명 (확장자 제외)\n"
        preview_text += "• {counter}: 순서 번호\n"
        preview_text += "• {ext}: 파일 확장자"
        
        QMessageBox.information(self, "이름 변경 패턴 미리보기", preview_text)
    
    def _show_policy_help(self):
        """충돌 처리 정책 도움말 표시"""
        help_text = """
파일 충돌 처리 정책 설명:

🔄 사용자에게 묻기 (권장)
- 각 충돌에 대해 사용자가 직접 선택
- 가장 안전한 방법이지만 수동 개입 필요
- 대화상자에서 "모든 파일에 적용" 옵션 제공

⏭️ 건너뛰기
- 충돌하는 파일은 변환하지 않음
- 기존 파일을 보호하지만 변환되지 않은 파일이 남음
- 안전하지만 변환 완료율이 낮을 수 있음

⚠️ 덮어쓰기
- 기존 파일을 새 파일로 교체
- 빠른 처리가 가능하지만 데이터 손실 위험
- 백업 옵션과 함께 사용 권장

🔄 이름 변경
- 자동으로 새로운 파일명 생성
- 모든 파일이 변환되며 기존 파일도 보존
- 파일명 패턴 설정 필요

권장 설정:
- 일반 사용자: "사용자에게 묻기" + "백업 생성"
- 자동 처리: "이름 변경" + "백업 생성"
- 빠른 처리: "덮어쓰기" + "백업 생성" (주의 필요)
        """.strip()
        
        QMessageBox.information(self, "충돌 처리 정책 도움말", help_text)
    
    def _validate_settings(self) -> tuple[bool, str]:
        """설정 유효성 검사"""
        # 이름 변경 패턴 검사
        pattern = self.rename_pattern_edit.text().strip()
        if not pattern:
            return False, "이름 변경 패턴이 비어있습니다."
        
        required_placeholders = ["{name}", "{ext}"]
        missing_placeholders = [p for p in required_placeholders if p not in pattern]
        if missing_placeholders:
            return False, f"필수 플레이스홀더가 없습니다: {', '.join(missing_placeholders)}"
        
        # 패턴에 잘못된 문자 확인
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        pattern_without_placeholders = pattern.replace("{name}", "").replace("{counter}", "").replace("{ext}", "")
        found_invalid = [char for char in invalid_chars if char in pattern_without_placeholders]
        if found_invalid:
            return False, f"파일명에 사용할 수 없는 문자가 포함되어 있습니다: {', '.join(found_invalid)}"
        
        # 커스텀 출력 디렉토리 검사
        if not self.save_to_original_check.isChecked():
            custom_path = self.custom_output_edit.text().strip()
            if not custom_path:
                return False, "원본 디렉토리에 저장하지 않는 경우 커스텀 출력 디렉토리를 지정해야 합니다."
            
            try:
                path = Path(custom_path)
                # 부모 디렉토리가 존재하는지 확인
                if not path.parent.exists():
                    return False, f"출력 디렉토리의 상위 경로가 존재하지 않습니다: {path.parent}"
            except Exception as e:
                return False, f"출력 디렉토리 경로가 유효하지 않습니다: {str(e)}"
        
        return True, ""
    
    def _load_settings(self):
        """설정 로드"""
        config = self.config_manager.get_config()
        conversion_config = config.get("conversion", {})
        
        # 변환 옵션
        self.include_metadata_check.setChecked(
            conversion_config.get("include_metadata", True)
        )
        self.preserve_formatting_check.setChecked(
            conversion_config.get("preserve_formatting", True)
        )
        self.extract_images_check.setChecked(
            conversion_config.get("extract_images", False)
        )
        self.include_toc_check.setChecked(
            conversion_config.get("include_toc", False)
        )
        
        # 파일 충돌 설정 로드
        if hasattr(config, 'conflict_config') and config.conflict_config:
            conflict_config = config.conflict_config
        else:
            conflict_config = FileConflictConfig()  # 기본값 사용
        
        # 기본 충돌 처리 정책 설정
        policy_map = {
            FileConflictPolicy.ASK_USER: 0,
            FileConflictPolicy.SKIP: 1,
            FileConflictPolicy.OVERWRITE: 2,
            FileConflictPolicy.RENAME: 3
        }
        policy_index = policy_map.get(conflict_config.default_policy, 0)
        self.default_policy_combo.setCurrentIndex(policy_index)
        
        # 이름 변경 패턴
        self.rename_pattern_edit.setText(conflict_config.auto_rename_pattern)
        
        # 충돌 처리 행동 옵션
        self.remember_choices_check.setChecked(conflict_config.remember_choices)
        self.apply_to_all_check.setChecked(conflict_config.apply_to_all)
        
        # 백업 및 로깅
        self.backup_original_check.setChecked(conflict_config.backup_original)
        self.conflict_log_check.setChecked(conflict_config.conflict_log_enabled)
        
        # 저장 위치 설정
        save_to_original = getattr(config, 'save_to_original_directory', True)
        self.save_to_original_check.setChecked(save_to_original)
        
        # 커스텀 출력 디렉토리
        if not save_to_original and hasattr(config, 'output_directory'):
            self.custom_output_edit.setText(str(config.output_directory))
        
        # 저장 위치 변경에 따른 UI 상태 업데이트
        self._on_save_location_changed(save_to_original)
        
        # 파일 처리
        self.max_workers_spin.setValue(
            conversion_config.get("max_workers", 4)
        )
        self.timeout_spin.setValue(
            conversion_config.get("timeout", 30)
        )
        self.retry_count_spin.setValue(
            conversion_config.get("retry_count", 2)
        )
        
        # 품질 설정
        quality_map = {"low": 0, "medium": 1, "high": 2, "best": 3}
        self.ocr_quality_combo.setCurrentIndex(
            quality_map.get(conversion_config.get("ocr_quality", "medium"), 1)
        )
        self.image_quality_spin.setValue(
            conversion_config.get("image_quality", 85)
        )
        
        # 출력 형식
        encoding_map = {"utf-8": 0, "utf-16": 1, "ascii": 2}
        self.encoding_combo.setCurrentIndex(
            encoding_map.get(conversion_config.get("encoding", "utf-8"), 0)
        )
        
        line_ending_map = {"system": 0, "lf": 1, "crlf": 2}
        self.line_ending_combo.setCurrentIndex(
            line_ending_map.get(conversion_config.get("line_ending", "system"), 0)
        )
    
    def save_settings(self) -> Dict[str, Any]:
        """설정 저장"""
        # 설정 유효성 검사
        is_valid, error_message = self._validate_settings()
        if not is_valid:
            QMessageBox.warning(self.parent(), "설정 오류", error_message)
            raise ValueError(error_message)
        
        quality_values = ["low", "medium", "high", "best"]
        encoding_values = ["utf-8", "utf-16", "ascii"]
        line_ending_values = ["system", "lf", "crlf"]
        
        # 파일 충돌 설정 생성
        policy_values = [
            FileConflictPolicy.ASK_USER,
            FileConflictPolicy.SKIP,
            FileConflictPolicy.OVERWRITE,
            FileConflictPolicy.RENAME
        ]
        selected_policy = policy_values[self.default_policy_combo.currentIndex()]
        
        conflict_config = FileConflictConfig(
            default_policy=selected_policy,
            auto_rename_pattern=self.rename_pattern_edit.text().strip(),
            remember_choices=self.remember_choices_check.isChecked(),
            apply_to_all=self.apply_to_all_check.isChecked(),
            backup_original=self.backup_original_check.isChecked(),
            conflict_log_enabled=self.conflict_log_check.isChecked()
        )
        
        settings = {
            "conversion": {
                "include_metadata": self.include_metadata_check.isChecked(),
                "preserve_formatting": self.preserve_formatting_check.isChecked(),
                "extract_images": self.extract_images_check.isChecked(),
                "include_toc": self.include_toc_check.isChecked(),
                "max_workers": self.max_workers_spin.value(),
                "timeout": self.timeout_spin.value(),
                "retry_count": self.retry_count_spin.value(),
                "ocr_quality": quality_values[self.ocr_quality_combo.currentIndex()],
                "image_quality": self.image_quality_spin.value(),
                "encoding": encoding_values[self.encoding_combo.currentIndex()],
                "line_ending": line_ending_values[self.line_ending_combo.currentIndex()]
            },
            "conflict_config": conflict_config,
            "save_to_original_directory": self.save_to_original_check.isChecked()
        }
        
        # 커스텀 출력 디렉토리 설정
        if not self.save_to_original_check.isChecked():
            custom_output = self.custom_output_edit.text().strip()
            if custom_output:
                settings["output_directory"] = Path(custom_output)
        
        return settings



class SettingsDialog(QDialog):
    """설정 다이얼로그"""
    
    settings_changed = pyqtSignal()
    language_changed = pyqtSignal(str)  # 언어 변경 시그널
    theme_changed = pyqtSignal(str)     # 테마 변경 시그널
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("설정")
        self.setMinimumSize(600, 500)
        
        self._init_ui()
        self._setup_connections()
        self._load_window_settings()
        
        logger.info("설정 다이얼로그 초기화 완료")
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 탭 생성
        self.general_tab = GeneralSettingsTab(self.config_manager)
        self.tab_widget.addTab(self.general_tab, "일반")
        
        self.conversion_tab = ConversionSettingsTab(self.config_manager)
        self.tab_widget.addTab(self.conversion_tab, "변환")
        
        
        # 버튼
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("기본값 복원")
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("확인")
        self.cancel_btn = QPushButton("취소")
        self.apply_btn = QPushButton("적용")
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.ok_btn.clicked.connect(self._on_ok)
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self._apply_settings)
        self.reset_btn.clicked.connect(self._reset_settings)
        
        # 언어 변경 시그널 연결
        self.general_tab.language_changed.connect(self.language_changed.emit)
        
        # 테마 변경 시그널 연결
        self.general_tab.theme_changed.connect(self.theme_changed.emit)
    
    def _on_ok(self):
        """확인 버튼 클릭"""
        if self._apply_settings():
            self.accept()
    
    def _apply_settings(self) -> bool:
        """설정 적용"""
        try:
            # 각 탭에서 설정 수집
            settings = {}
            
            general_settings = self.general_tab.save_settings()
            settings.update(general_settings)
            
            conversion_settings = self.conversion_tab.save_settings()
            settings.update(conversion_settings)
            
            
            # FileConflictConfig 처리
            if 'conflict_config' in settings:
                conflict_config = settings.pop('conflict_config')
                self.config_manager.update_file_conflict_config(conflict_config)
            
            # 저장 위치 설정 처리
            if 'save_to_original_directory' in settings:
                save_to_original = settings.pop('save_to_original_directory')
                output_directory = settings.pop('output_directory', None)
                self.config_manager.update_save_location_settings(save_to_original, output_directory)
            
            # 나머지 설정 저장
            for key, value in settings.items():
                self.config_manager.set_value(key, value)
            
            self.config_manager.save_config()
            
            # 설정 변경 시그널 발송
            self.settings_changed.emit()
            
            logger.info("설정이 성공적으로 저장되었습니다")
            return True
            
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            QMessageBox.critical(
                self, "오류", 
                f"설정을 저장하는 중 오류가 발생했습니다:\n{str(e)}"
            )
            return False
    
    def _reset_settings(self):
        """설정 초기화"""
        reply = QMessageBox.question(
            self, "확인",
            "모든 설정을 기본값으로 초기화하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config_manager.reset_to_defaults()
                
                # 탭들 다시 로드
                self.general_tab._load_settings()
                self.conversion_tab._load_settings()
                self.llm_tab._load_settings()
                
                logger.info("설정이 기본값으로 초기화되었습니다")
                QMessageBox.information(self, "완료", "설정이 기본값으로 초기화되었습니다.")
                
            except Exception as e:
                logger.error(f"설정 초기화 실패: {e}")
                QMessageBox.critical(
                    self, "오류",
                    f"설정 초기화 중 오류가 발생했습니다:\n{str(e)}"
                )
    
    def _load_window_settings(self):
        """창 설정 로드"""
        settings = QSettings()
        
        # 창 크기 및 위치
        geometry = settings.value("settings_dialog/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 활성 탭
        current_tab = settings.value("settings_dialog/current_tab", 0, int)
        self.tab_widget.setCurrentIndex(current_tab)
    
    def _save_window_settings(self):
        """창 설정 저장"""
        settings = QSettings()
        settings.setValue("settings_dialog/geometry", self.saveGeometry())
        settings.setValue("settings_dialog/current_tab", self.tab_widget.currentIndex())
    
    def closeEvent(self, event):
        """닫기 이벤트"""
        self._save_window_settings()
        super().closeEvent(event)