main_window 모듈
===============

.. automodule:: markitdown_gui.ui.main_window
   :members:
   :undoc-members:
   :show-inheritance:

개요
----

MainWindow 클래스는 MarkItDown GUI 애플리케이션의 주요 사용자 인터페이스를 제공하는 핵심 컴포넌트입니다.
PyQt6 기반으로 구현되었으며, 파일 변환, 진행 상황 모니터링, 설정 관리 등의 주요 기능을 제공합니다.

주요 기능
--------

* **파일 관리**: 드래그 앤 드롭, 파일 선택, 배치 처리
* **변환 진행 상황**: 실시간 진행률 표시 및 로그 모니터링
* **설정 관리**: 사용자 설정 인터페이스 통합
* **접근성 지원**: 키보드 네비게이션, 스크린 리더 지원
* **테마 시스템**: 다크/라이트 테마 지원
* **국제화**: 다국어 인터페이스 지원

MainWindow 클래스
----------------

.. autoclass:: markitdown_gui.ui.main_window.MainWindow
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

      메인 윈도우를 초기화합니다.

      :param config_manager: 설정 관리자 인스턴스
      :type config_manager: ConfigManager

      **예제:**

      .. code-block:: python

         from markitdown_gui.core.config_manager import ConfigManager
         from markitdown_gui.ui.main_window import MainWindow

         config_manager = ConfigManager()
         main_window = MainWindow(config_manager)
         main_window.show()

신호 (Signals)
--------------

MainWindow 클래스는 다음과 같은 PyQt6 신호를 정의합니다:

.. py:attribute:: file_conversion_requested
   :type: pyqtSignal

   파일 변환이 요청되었을 때 발생하는 신호입니다.

.. py:attribute:: conversion_progress_updated
   :type: pyqtSignal

   변환 진행 상황이 업데이트될 때 발생하는 신호입니다.

.. py:attribute:: conversion_completed
   :type: pyqtSignal

   변환이 완료되었을 때 발생하는 신호입니다.

.. py:attribute:: settings_changed
   :type: pyqtSignal

   설정이 변경되었을 때 발생하는 신호입니다.

메인 메서드
----------

UI 초기화
~~~~~~~~

.. automethod:: markitdown_gui.ui.main_window.MainWindow._init_ui

   사용자 인터페이스를 초기화합니다.

   **내부 동작:**
   
   1. 메뉴바 및 툴바 설정
   2. 메인 위젯 레이아웃 구성
   3. 상태바 초기화
   4. 드래그 앤 드롭 기능 활성화

.. automethod:: markitdown_gui.ui.main_window.MainWindow._setup_menu

   메뉴바를 설정합니다.

   **메뉴 구조:**
   
   * **파일 메뉴**: 열기, 저장, 종료
   * **편집 메뉴**: 설정, 언어 변경
   * **보기 메뉴**: 테마 변경, 전체화면
   * **도구 메뉴**: 로그 보기, 성능 정보
   * **도움말 메뉴**: 정보, 단축키

.. automethod:: markitdown_gui.ui.main_window.MainWindow._setup_toolbar

   툴바를 설정합니다.

   **툴바 버튼:**
   
   * 파일 열기
   * 폴더 열기
   * 변환 시작/중지
   * 설정
   * 도움말

파일 관리
~~~~~~~~

.. automethod:: markitdown_gui.ui.main_window.MainWindow._handle_file_drop

   드래그 앤 드롭된 파일을 처리합니다.

   :param files: 드롭된 파일 목록
   :type files: List[str]

   **예제:**

   .. code-block:: python

      # 파일이 드롭되면 자동으로 호출됨
      main_window._handle_file_drop([
          '/path/to/document.pdf',
          '/path/to/image.jpg'
      ])

.. automethod:: markitdown_gui.ui.main_window.MainWindow._add_files

   파일 목록에 파일들을 추가합니다.

   :param file_paths: 추가할 파일 경로 목록
   :type file_paths: List[str]

.. automethod:: markitdown_gui.ui.main_window.MainWindow._remove_selected_files

   선택된 파일들을 목록에서 제거합니다.

.. automethod:: markitdown_gui.ui.main_window.MainWindow._clear_file_list

   파일 목록을 모두 지웁니다.

변환 관리
~~~~~~~~

.. automethod:: markitdown_gui.ui.main_window.MainWindow._start_conversion

   선택된 파일들의 변환을 시작합니다.

   **변환 과정:**
   
   1. 파일 유효성 검사
   2. 출력 디렉토리 확인
   3. 변환 작업 큐에 추가
   4. 진행률 모니터링 시작

.. automethod:: markitdown_gui.ui.main_window.MainWindow._stop_conversion

   진행 중인 변환을 중지합니다.

.. automethod:: markitdown_gui.ui.main_window.MainWindow._update_conversion_progress

   변환 진행 상황을 업데이트합니다.

   :param file_info: 파일 정보
   :type file_info: FileInfo
   :param progress: 진행률 (0-100)
   :type progress: int

설정 관리
~~~~~~~~

.. automethod:: markitdown_gui.ui.main_window.MainWindow._open_settings

   설정 대화상자를 엽니다.

   **설정 카테고리:**
   
   * 일반 설정 (언어, 테마)
   * 변환 설정 (출력 디렉토리, 동시 변환 수)
   * LLM 설정 (API 키, 모델 선택)
   * 접근성 설정

.. automethod:: markitdown_gui.ui.main_window.MainWindow._apply_settings

   변경된 설정을 적용합니다.

   :param settings: 새로운 설정
   :type settings: AppConfig

테마 및 UI
~~~~~~~~~

.. automethod:: markitdown_gui.ui.main_window.MainWindow._update_theme

   UI 테마를 업데이트합니다.

   :param theme_name: 테마 이름 ('light', 'dark', 'auto')
   :type theme_name: str

.. automethod:: markitdown_gui.ui.main_window.MainWindow._update_language

   인터페이스 언어를 변경합니다.

   :param language_code: 언어 코드 ('ko', 'en', 'ja')
   :type language_code: str

.. automethod:: markitdown_gui.ui.main_window.MainWindow._retranslate_ui

   UI 텍스트를 현재 언어로 번역합니다.

접근성 지원
~~~~~~~~~~

.. automethod:: markitdown_gui.ui.main_window.MainWindow._setup_accessibility

   접근성 기능을 설정합니다.

   **접근성 기능:**
   
   * 키보드 네비게이션
   * 스크린 리더 지원
   * 고대비 모드
   * 텍스트 크기 조정

.. automethod:: markitdown_gui.ui.main_window.MainWindow._update_accessibility

   접근성 설정을 업데이트합니다.

   :param features: 활성화할 접근성 기능 목록
   :type features: List[AccessibilityFeature]

이벤트 핸들러
-----------

.. automethod:: markitdown_gui.ui.main_window.MainWindow.closeEvent

   윈도우 종료 이벤트를 처리합니다.

   :param event: 종료 이벤트
   :type event: QCloseEvent

.. automethod:: markitdown_gui.ui.main_window.MainWindow.dragEnterEvent

   드래그 진입 이벤트를 처리합니다.

   :param event: 드래그 이벤트
   :type event: QDragEnterEvent

.. automethod:: markitdown_gui.ui.main_window.MainWindow.dropEvent

   드롭 이벤트를 처리합니다.

   :param event: 드롭 이벤트
   :type event: QDropEvent

.. automethod:: markitdown_gui.ui.main_window.MainWindow.keyPressEvent

   키보드 입력 이벤트를 처리합니다.

   :param event: 키 이벤트
   :type event: QKeyEvent

   **지원 단축키:**
   
   * Ctrl+O: 파일 열기
   * Ctrl+Shift+O: 폴더 열기  
   * F5: 변환 시작
   * Esc: 변환 중지
   * Ctrl+,: 설정
   * F11: 전체화면

사용 예제
--------

기본 사용법
~~~~~~~~~~

.. code-block:: python

   import sys
   from PyQt6.QtWidgets import QApplication
   from markitdown_gui.core.config_manager import ConfigManager
   from markitdown_gui.ui.main_window import MainWindow

   app = QApplication(sys.argv)
   
   # 설정 관리자 초기화
   config_manager = ConfigManager()
   
   # 메인 윈도우 생성 및 표시
   main_window = MainWindow(config_manager)
   main_window.show()
   
   sys.exit(app.exec())

신호 연결
~~~~~~~~

.. code-block:: python

   def on_conversion_completed():
       print("변환이 완료되었습니다!")

   def on_settings_changed():
       print("설정이 변경되었습니다!")

   # 신호 연결
   main_window.conversion_completed.connect(on_conversion_completed)
   main_window.settings_changed.connect(on_settings_changed)

커스텀 메뉴 추가
~~~~~~~~~~~~~~

.. code-block:: python

   from PyQt6.QtGui import QAction

   class CustomMainWindow(MainWindow):
       def __init__(self, config_manager):
           super().__init__(config_manager)
           self._add_custom_menu()
       
       def _add_custom_menu(self):
           # 커스텀 메뉴 추가
           custom_menu = self.menuBar().addMenu("커스텀")
           
           custom_action = QAction("커스텀 기능", self)
           custom_action.triggered.connect(self._custom_function)
           custom_menu.addAction(custom_action)
       
       def _custom_function(self):
           print("커스텀 기능 실행!")

테마 동적 변경
~~~~~~~~~~~~

.. code-block:: python

   # 테마 변경
   main_window._update_theme('dark')
   
   # 언어 변경
   main_window._update_language('en')

접근성 설정
~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.accessibility_manager import AccessibilityFeature

   # 접근성 기능 활성화
   accessibility_features = [
       AccessibilityFeature.KEYBOARD_NAVIGATION,
       AccessibilityFeature.HIGH_CONTRAST,
       AccessibilityFeature.SCREEN_READER
   ]
   main_window._update_accessibility(accessibility_features)

프로그래밍 방식 파일 추가
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # 파일 목록에 파일 추가
   file_paths = [
       '/path/to/document.pdf',
       '/path/to/presentation.pptx',
       '/path/to/spreadsheet.xlsx'
   ]
   main_window._add_files(file_paths)
   
   # 변환 시작
   main_window._start_conversion()

레이아웃 구조
-----------

메인 윈도우의 레이아웃 구조:

.. code-block:: text

   MainWindow
   ├── MenuBar
   │   ├── File Menu (파일)
   │   ├── Edit Menu (편집)
   │   ├── View Menu (보기)
   │   ├── Tools Menu (도구)
   │   └── Help Menu (도움말)
   ├── ToolBar
   │   ├── Open File Button
   │   ├── Open Folder Button
   │   ├── Convert Button
   │   ├── Settings Button
   │   └── Help Button
   ├── Central Widget
   │   ├── File Selection Area
   │   │   ├── FileListWidget
   │   │   └── Control Buttons
   │   ├── Progress Area
   │   │   ├── ProgressWidget
   │   │   └── Status Information
   │   └── Log Area
   │       └── LogWidget
   └── StatusBar
       ├── Status Text
       ├── Progress Indicator
       └── Additional Information

관련 모듈
--------

* :doc:`../core/config_manager` - 설정 관리
* :doc:`../core/conversion_manager` - 변환 관리
* :doc:`../core/file_manager` - 파일 관리
* :doc:`../core/accessibility_manager` - 접근성 관리
* :doc:`../core/theme_manager` - 테마 관리
* :doc:`components/file_list_widget` - 파일 목록 위젯
* :doc:`components/progress_widget` - 진행률 위젯
* :doc:`settings_dialog` - 설정 대화상자

.. seealso::

   * :class:`markitdown_gui.core.config_manager.ConfigManager` - 설정 관리자
   * :class:`markitdown_gui.core.models.AppConfig` - 애플리케이션 설정
   * :doc:`../user-guide/interface` - 사용자 인터페이스 가이드