"""
파일 리스트 위젯
파일들을 표시하고 선택할 수 있는 위젯
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QHeaderView, QCheckBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QAction

from typing import List, Optional
from pathlib import Path

from ...core.models import FileInfo, ConversionStatus
from ...core.logger import get_logger


logger = get_logger(__name__)


class FileListWidget(QWidget):
    """파일 리스트 위젯"""
    
    # 시그널
    selection_changed = pyqtSignal(int, int)  # 선택된 개수, 전체 개수
    double_clicked = pyqtSignal(object)  # 더블클릭된 파일 정보
    export_requested = pyqtSignal(object)  # 내보내기 요청된 파일 정보
    
    def __init__(self):
        super().__init__()
        self.file_items = {}  # Path -> QTreeWidgetItem 매핑
        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 상단: 선택 옵션들
        top_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("전체 선택")
        self.select_all_btn.setMaximumWidth(80)
        top_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("전체 해제")
        self.select_none_btn.setMaximumWidth(80)
        top_layout.addWidget(self.select_none_btn)
        
        top_layout.addStretch()
        
        # 파일 개수 표시
        self.count_label = QLabel("파일: 0개")
        top_layout.addWidget(self.count_label)
        
        layout.addLayout(top_layout)
        
        # 파일 트리 위젯
        self.tree_widget = QTreeWidget()
        self._setup_tree_widget()
        layout.addWidget(self.tree_widget)
    
    def _setup_tree_widget(self):
        """트리 위젯 설정"""
        # 컬럼 설정
        columns = ["선택", "아이콘", "파일명", "크기", "수정일", "타입", "상태"]
        self.tree_widget.setHeaderLabels(columns)
        
        # 헤더 설정
        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 선택
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 아이콘
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 파일명
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 크기
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # 수정일
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # 타입
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # 상태
        
        # 컬럼 너비 설정
        self.tree_widget.setColumnWidth(0, 50)   # 선택
        self.tree_widget.setColumnWidth(1, 30)   # 아이콘
        
        # 기타 설정
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setRootIsDecorated(False)
        self.tree_widget.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree_widget.setSortingEnabled(True)
        
        # 컨텍스트 메뉴 활성화
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    
    def _setup_connections(self):
        """시그널-슬롯 연결"""
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_none_btn.clicked.connect(self.select_none)
        
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree_widget.itemChanged.connect(self._on_item_changed)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def clear(self):
        """모든 항목 제거"""
        self.tree_widget.clear()
        self.file_items.clear()
        self._update_count_display()
    
    def add_file(self, file_info: FileInfo):
        """파일 추가"""
        item = QTreeWidgetItem(self.tree_widget)
        
        # 체크박스
        checkbox = QCheckBox()
        checkbox.setChecked(file_info.is_selected)
        checkbox.stateChanged.connect(lambda state, fi=file_info: self._on_checkbox_changed(fi, state))
        self.tree_widget.setItemWidget(item, 0, checkbox)
        
        # 아이콘 (임시로 텍스트 사용)
        item.setText(1, "📄")
        
        # 파일 정보
        item.setText(2, file_info.name)
        item.setText(3, file_info.size_formatted)
        item.setText(4, file_info.modified_time.strftime("%Y-%m-%d %H:%M"))
        item.setText(5, file_info.file_type.value.upper())
        item.setText(6, self._get_status_text(file_info.conversion_status))
        
        # 데이터 저장
        item.setData(0, Qt.ItemDataRole.UserRole, file_info)
        self.file_items[file_info.path] = item
        
        self._update_count_display()
        logger.debug(f"파일 추가됨: {file_info.name}")
    
    def add_files(self, file_infos: List[FileInfo]):
        """여러 파일 추가"""
        for file_info in file_infos:
            self.add_file(file_info)
    
    def remove_file(self, file_info: FileInfo):
        """파일 제거"""
        if file_info.path in self.file_items:
            item = self.file_items[file_info.path]
            index = self.tree_widget.indexOfTopLevelItem(item)
            self.tree_widget.takeTopLevelItem(index)
            del self.file_items[file_info.path]
            self._update_count_display()
    
    def update_file_status(self, file_info: FileInfo, status: ConversionStatus):
        """파일 변환 상태 업데이트"""
        if file_info.path in self.file_items:
            item = self.file_items[file_info.path]
            item.setText(6, self._get_status_text(status))
            file_info.conversion_status = status
    
    def get_all_files(self) -> List[FileInfo]:
        """모든 파일 정보 반환"""
        files = []
        for item in self.file_items.values():
            file_info = item.data(0, Qt.ItemDataRole.UserRole)
            if file_info:
                files.append(file_info)
        return files
    
    def get_selected_files(self) -> List[FileInfo]:
        """선택된 파일들 반환"""
        selected = []
        for item in self.file_items.values():
            file_info = item.data(0, Qt.ItemDataRole.UserRole)
            if file_info and file_info.is_selected:
                selected.append(file_info)
        return selected
    
    def select_all(self):
        """전체 선택"""
        for item in self.file_items.values():
            file_info = item.data(0, Qt.ItemDataRole.UserRole)
            if file_info:
                file_info.is_selected = True
                checkbox = self.tree_widget.itemWidget(item, 0)
                if checkbox:
                    checkbox.setChecked(True)
    
    def select_none(self):
        """전체 해제"""
        for item in self.file_items.values():
            file_info = item.data(0, Qt.ItemDataRole.UserRole)
            if file_info:
                file_info.is_selected = False
                checkbox = self.tree_widget.itemWidget(item, 0)
                if checkbox:
                    checkbox.setChecked(False)
    
    def _get_status_text(self, status: ConversionStatus) -> str:
        """상태를 텍스트로 변환"""
        status_texts = {
            ConversionStatus.PENDING: "대기",
            ConversionStatus.IN_PROGRESS: "변환 중",
            ConversionStatus.SUCCESS: "완료",
            ConversionStatus.FAILED: "실패",
            ConversionStatus.CANCELLED: "취소됨"
        }
        return status_texts.get(status, "알 수 없음")
    
    def _update_count_display(self):
        """개수 표시 업데이트"""
        total_count = len(self.file_items)
        selected_count = len(self.get_selected_files())
        
        self.count_label.setText(f"파일: {total_count}개")
        self.selection_changed.emit(selected_count, total_count)
    
    def _on_checkbox_changed(self, file_info: FileInfo, state: int):
        """체크박스 상태 변경시"""
        file_info.is_selected = (state == Qt.CheckState.Checked.value)
        self._update_count_display()
    
    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """아이템 변경시"""
        # 필요시 추가 로직 구현
        pass
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """아이템 더블클릭시"""
        file_info = item.data(0, Qt.ItemDataRole.UserRole)
        if file_info:
            self.double_clicked.emit(file_info)
    
    def _show_context_menu(self, position):
        """컨텍스트 메뉴 표시"""
        item = self.tree_widget.itemAt(position)
        if not item:
            return
        
        file_info = item.data(0, Qt.ItemDataRole.UserRole)
        if not file_info:
            return
        
        menu = QMenu(self)
        
        # 선택/해제
        if file_info.is_selected:
            select_action = QAction("선택 해제", self)
            select_action.triggered.connect(lambda: self._toggle_selection(file_info))
        else:
            select_action = QAction("선택", self)
            select_action.triggered.connect(lambda: self._toggle_selection(file_info))
        menu.addAction(select_action)
        
        menu.addSeparator()
        
        # 파일 열기
        open_action = QAction("파일 열기", self)
        open_action.triggered.connect(lambda: self._open_file(file_info))
        menu.addAction(open_action)
        
        # 폴더에서 보기
        show_in_folder_action = QAction("폴더에서 보기", self)
        show_in_folder_action.triggered.connect(lambda: self._show_in_folder(file_info))
        menu.addAction(show_in_folder_action)
        
        menu.addSeparator()
        
        # 변환하여 내보내기
        convert_action = QAction("변환하여 내보내기", self)
        convert_action.triggered.connect(lambda: self._export_file(file_info))
        menu.addAction(convert_action)
        
        # 메뉴 표시
        global_pos = self.tree_widget.mapToGlobal(position)
        menu.exec(global_pos)
    
    def _toggle_selection(self, file_info: FileInfo):
        """선택 상태 토글"""
        file_info.is_selected = not file_info.is_selected
        item = self.file_items[file_info.path]
        checkbox = self.tree_widget.itemWidget(item, 0)
        if checkbox:
            checkbox.setChecked(file_info.is_selected)
    
    def _open_file(self, file_info: FileInfo):
        """파일 열기"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                import os
                os.startfile(str(file_info.path))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_info.path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(file_info.path)])
        except Exception as e:
            logger.error(f"파일 열기 실패: {e}")
    
    def _show_in_folder(self, file_info: FileInfo):
        """폴더에서 보기"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.run(["explorer", "/select,", str(file_info.path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", "-R", str(file_info.path)])
            else:  # Linux
                folder_path = file_info.path.parent
                subprocess.run(["xdg-open", str(folder_path)])
        except Exception as e:
            logger.error(f"폴더에서 보기 실패: {e}")
    
    def _export_file(self, file_info: FileInfo):
        """파일 내보내기 요청"""
        self.export_requested.emit(file_info)