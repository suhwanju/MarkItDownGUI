UI 모듈
=======

MarkItDown GUI의 사용자 인터페이스 컴포넌트들입니다.

.. toctree::
   :maxdepth: 2
   :caption: UI 모듈

   main_window
   components/index
   dialogs/index
   widgets/index

모듈 개요
--------

**메인 인터페이스**

* :doc:`main_window` - 애플리케이션 메인 윈도우

**재사용 가능한 컴포넌트**

* :doc:`components/file_list_widget` - 파일 목록 위젯
* :doc:`components/progress_widget` - 진행률 표시 위젯
* :doc:`components/log_widget` - 로그 표시 위젯
* :doc:`components/theme_selector` - 테마 선택 위젯

**대화상자**

* :doc:`dialogs/settings_dialog` - 설정 대화상자
* :doc:`dialogs/preview_dialog` - 미리보기 대화상자
* :doc:`dialogs/file_viewer_dialog` - 파일 뷰어 대화상자

**특수 위젯**

* :doc:`widgets/conversion_widget` - 변환 기능 위젯
* :doc:`widgets/status_widget` - 상태 표시 위젯

UI 아키텍처
----------

.. graphviz::

   digraph UIArchitecture {
       rankdir=TB;
       node [shape=box, style=rounded];
       
       // 메인 레이어
       subgraph cluster_main {
           label="Main Application";
           style=filled;
           color=lightblue;
           
           MainWindow [label="MainWindow\n(메인 윈도우)"];
       }
       
       // 컴포넌트 레이어
       subgraph cluster_components {
           label="Reusable Components";
           style=filled;
           color=lightgreen;
           
           FileListWidget [label="FileListWidget\n(파일 목록)"];
           ProgressWidget [label="ProgressWidget\n(진행률)"];
           LogWidget [label="LogWidget\n(로그)"];
           ThemeSelector [label="ThemeSelector\n(테마 선택)"];
       }
       
       // 대화상자 레이어
       subgraph cluster_dialogs {
           label="Dialog Windows";
           style=filled;
           color=lightyellow;
           
           SettingsDialog [label="SettingsDialog\n(설정)"];
           PreviewDialog [label="PreviewDialog\n(미리보기)"];
           FileViewerDialog [label="FileViewerDialog\n(파일 뷰어)"];
       }
       
       // 위젯 레이어
       subgraph cluster_widgets {
           label="Specialized Widgets";
           style=filled;
           color=lightcoral;
           
           ConversionWidget [label="ConversionWidget\n(변환 기능)"];
           StatusWidget [label="StatusWidget\n(상태 표시)"];
       }
       
       // 의존성 관계
       MainWindow -> FileListWidget;
       MainWindow -> ProgressWidget;
       MainWindow -> LogWidget;
       MainWindow -> SettingsDialog;
       MainWindow -> PreviewDialog;
       
       SettingsDialog -> ThemeSelector;
       MainWindow -> ConversionWidget;
       MainWindow -> StatusWidget;
   }

설계 원칙
--------

**모듈성 (Modularity)**

각 UI 컴포넌트는 독립적으로 개발되고 테스트될 수 있도록 설계되었습니다.

.. code-block:: python

   # 각 컴포넌트는 독립적으로 사용 가능
   from markitdown_gui.ui.components.file_list_widget import FileListWidget
   from markitdown_gui.ui.components.progress_widget import ProgressWidget
   
   # 개별 컴포넌트 생성 및 사용
   file_list = FileListWidget()
   progress = ProgressWidget()

**재사용성 (Reusability)**

공통 기능은 재사용 가능한 컴포넌트로 분리되어 있습니다.

.. code-block:: python

   # 로그 위젯은 여러 곳에서 재사용
   from markitdown_gui.ui.components.log_widget import LogWidget
   
   # 메인 윈도우에서 사용
   main_log = LogWidget("Main")
   
   # 설정 대화상자에서도 사용
   settings_log = LogWidget("Settings")

**확장성 (Extensibility)**

새로운 기능을 쉽게 추가할 수 있도록 인터페이스가 설계되었습니다.

.. code-block:: python

   # 기본 위젯을 확장하여 커스텀 기능 추가
   from markitdown_gui.ui.components.file_list_widget import FileListWidget
   
   class CustomFileListWidget(FileListWidget):
       def __init__(self):
           super().__init__()
           self.add_custom_features()
       
       def add_custom_features(self):
           # 커스텀 기능 구현
           pass

**일관성 (Consistency)**

모든 UI 컴포넌트는 일관된 스타일과 동작을 제공합니다.

.. code-block:: python

   # 모든 대화상자는 동일한 기본 클래스를 상속
   from markitdown_gui.ui.dialogs.base_dialog import BaseDialog
   
   class CustomDialog(BaseDialog):
       def __init__(self):
           super().__init__()
           self.setup_ui()

컴포넌트 계층구조
--------------

UI 컴포넌트들의 상속 계층구조:

.. code-block:: text

   QMainWindow
   └── MainWindow

   QWidget
   ├── FileListWidget
   ├── ProgressWidget
   ├── LogWidget
   ├── ConversionWidget
   └── StatusWidget

   QDialog
   ├── BaseDialog
   │   ├── SettingsDialog
   │   ├── PreviewDialog
   │   └── FileViewerDialog
   └── AboutDialog

   QComboBox
   └── ThemeSelector

이벤트 시스템
-----------

UI 컴포넌트들 간의 통신은 PyQt6의 신호/슬롯 시스템을 사용합니다.

**주요 신호들:**

.. code-block:: python

   # MainWindow 신호
   file_selected = pyqtSignal(str)
   conversion_started = pyqtSignal()
   conversion_completed = pyqtSignal()
   settings_changed = pyqtSignal()

   # FileListWidget 신호
   files_added = pyqtSignal(list)
   file_removed = pyqtSignal(str)
   selection_changed = pyqtSignal()

   # ProgressWidget 신호
   progress_updated = pyqtSignal(int)
   operation_cancelled = pyqtSignal()

**신호 연결 예제:**

.. code-block:: python

   # 컴포넌트 간 신호 연결
   main_window = MainWindow()
   file_list = FileListWidget()
   progress = ProgressWidget()

   # 파일 선택 시 변환 시작
   file_list.files_added.connect(main_window.start_conversion)
   
   # 진행률 업데이트
   main_window.conversion_progress.connect(progress.update_progress)
   
   # 변환 완료 시 로그 업데이트
   main_window.conversion_completed.connect(log_widget.add_message)

테마 시스템
----------

모든 UI 컴포넌트는 일관된 테마 시스템을 지원합니다.

**테마 적용:**

.. code-block:: python

   from markitdown_gui.core.theme_manager import get_theme_manager

   theme_manager = get_theme_manager()
   
   # 다크 테마 적용
   theme_manager.apply_theme('dark')
   
   # 라이트 테마 적용
   theme_manager.apply_theme('light')
   
   # 시스템 테마 자동 적용
   theme_manager.apply_theme('auto')

**커스텀 스타일:**

.. code-block:: python

   # 컴포넌트별 커스텀 스타일
   widget.setStyleSheet("""
       QWidget {
           background-color: #2b2b2b;
           color: #ffffff;
           border: 1px solid #555555;
       }
       
       QPushButton {
           background-color: #3c3c3c;
           border: 1px solid #666666;
           padding: 5px;
           border-radius: 3px;
       }
       
       QPushButton:hover {
           background-color: #4c4c4c;
       }
   """)

국제화 지원
----------

모든 UI 텍스트는 국제화를 지원합니다.

**번역 가능한 텍스트:**

.. code-block:: python

   from markitdown_gui.core.i18n_manager import tr

   # 번역 가능한 텍스트 사용
   button.setText(tr("변환 시작"))
   label.setText(tr("파일을 선택하세요"))
   
   # 복수형 처리
   message = tr("{count}개 파일이 선택되었습니다", count=len(files))

**지원 언어:**

* 한국어 (ko)
* 영어 (en)  
* 일본어 (ja)

접근성 지원
----------

모든 UI 컴포넌트는 접근성 기능을 지원합니다.

**키보드 네비게이션:**

.. code-block:: python

   # 탭 순서 설정
   self.setTabOrder(widget1, widget2)
   self.setTabOrder(widget2, widget3)

   # 포커스 정책 설정
   widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

**스크린 리더 지원:**

.. code-block:: python

   # 접근성 이름과 설명 설정
   widget.setAccessibleName("파일 목록")
   widget.setAccessibleDescription("변환할 파일들의 목록입니다")

   # 역할 설정
   widget.setAccessibleRole(QAccessible.Role.List)

**고대비 모드:**

.. code-block:: python

   # 고대비 스타일 적용
   if accessibility_manager.is_high_contrast_enabled():
       widget.setStyleSheet(high_contrast_stylesheet)

성능 최적화
----------

**지연 로딩:**

.. code-block:: python

   # 무거운 컴포넌트는 필요할 때 로딩
   def show_settings_dialog(self):
       if not hasattr(self, '_settings_dialog'):
           self._settings_dialog = SettingsDialog(self)
       self._settings_dialog.show()

**가상화:**

.. code-block:: python

   # 대용량 파일 목록을 위한 가상화
   class VirtualFileListWidget(QAbstractItemView):
       def __init__(self):
           super().__init__()
           self.setModel(VirtualFileListModel())

**메모리 관리:**

.. code-block:: python

   # 위젯 정리
   def closeEvent(self, event):
       self.cleanup_resources()
       super().closeEvent(event)
   
   def cleanup_resources(self):
       # 리소스 정리
       for widget in self.child_widgets:
           widget.deleteLater()

테스트 전략
----------

**단위 테스트:**

.. code-block:: python

   import pytest
   from PyQt6.QtWidgets import QApplication
   from markitdown_gui.ui.components.file_list_widget import FileListWidget

   @pytest.fixture
   def app():
       return QApplication([])

   def test_file_list_widget_creation(app):
       widget = FileListWidget()
       assert widget is not None

**통합 테스트:**

.. code-block:: python

   def test_main_window_integration(app):
       from markitdown_gui.core.config_manager import ConfigManager
       from markitdown_gui.ui.main_window import MainWindow
       
       config_manager = ConfigManager()
       main_window = MainWindow(config_manager)
       
       assert main_window.isVisible() == False
       main_window.show()
       assert main_window.isVisible() == True

**UI 테스트:**

.. code-block:: python

   from PyQt6.QtTest import QTest
   from PyQt6.QtCore import Qt

   def test_button_click(app):
       widget = SomeWidget()
       
       # 버튼 클릭 시뮬레이션
       QTest.mouseClick(widget.button, Qt.MouseButton.LeftButton)
       
       # 결과 확인
       assert widget.result_label.text() == "Expected Text"

디버깅 도구
----------

**UI 검사 도구:**

.. code-block:: python

   # 개발 모드에서 UI 계층구조 표시
   def show_widget_hierarchy(widget, indent=0):
       print("  " * indent + f"{widget.__class__.__name__}")
       for child in widget.children():
           if hasattr(child, 'children'):
               show_widget_hierarchy(child, indent + 1)

**성능 프로파일링:**

.. code-block:: python

   import cProfile
   import pstats

   def profile_ui_operation():
       profiler = cProfile.Profile()
       profiler.enable()
       
       # UI 작업 수행
       perform_ui_operation()
       
       profiler.disable()
       stats = pstats.Stats(profiler)
       stats.sort_stats('cumulative')
       stats.print_stats()

모범 사례
--------

**컴포넌트 설계:**

1. **단일 책임 원칙**: 각 컴포넌트는 하나의 명확한 기능만 담당
2. **느슨한 결합**: 컴포넌트 간 의존성 최소화
3. **높은 응집도**: 관련된 기능들을 함께 그룹화

**코드 구조:**

.. code-block:: python

   class MyWidget(QWidget):
       # 신호 정의
       data_changed = pyqtSignal(dict)
       
       def __init__(self, parent=None):
           super().__init__(parent)
           self._setup_ui()
           self._connect_signals()
           self._apply_styles()
       
       def _setup_ui(self):
           """UI 레이아웃 설정"""
           pass
       
       def _connect_signals(self):
           """신호/슬롯 연결"""
           pass
       
       def _apply_styles(self):
           """스타일 적용"""
           pass

**에러 처리:**

.. code-block:: python

   def safe_ui_operation(self):
       try:
           # UI 작업 수행
           self.perform_operation()
       except Exception as e:
           logger.error(f"UI 작업 실패: {e}")
           QMessageBox.critical(self, "오류", f"작업 중 오류가 발생했습니다: {e}")

스타일 가이드
-----------

**네이밍 규칙:**

* 클래스명: PascalCase (예: `FileListWidget`)
* 메서드명: snake_case (예: `add_file_item`)  
* 신호명: snake_case (예: `file_selected`)
* 프라이빗 메서드: _로 시작 (예: `_setup_ui`)

**코드 구성:**

1. 임포트
2. 클래스 정의 및 독스트링
3. 신호 정의
4. 초기화 메서드
5. 공개 메서드
6. 프라이빗 메서드
7. 이벤트 핸들러

API 참조
-------

자세한 API 참조는 각 모듈의 문서를 참조하세요:

* :doc:`main_window` - 메인 윈도우 API
* :doc:`components/index` - 컴포넌트 API
* :doc:`dialogs/index` - 대화상자 API  
* :doc:`widgets/index` - 위젯 API