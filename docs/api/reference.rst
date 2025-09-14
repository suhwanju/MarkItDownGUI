API 레퍼런스
============

이 페이지는 MarkItDown GUI의 전체 API에 대한 자동 생성된 참조 문서입니다.

.. autosummary::
   :toctree: _autosummary
   :recursive:
   :template: custom_module.rst

   markitdown_gui

모듈별 자동 문서
--------------

Core 모듈
~~~~~~~~~

.. autosummary::
   :toctree: _autosummary/core
   :nosignatures:

   markitdown_gui.core.config_manager.ConfigManager
   markitdown_gui.core.models.FileInfo
   markitdown_gui.core.models.ConversionResult
   markitdown_gui.core.models.AppConfig
   markitdown_gui.core.models.LLMConfig
   markitdown_gui.core.conversion_manager.ConversionManager
   markitdown_gui.core.file_manager.FileManager
   markitdown_gui.core.llm_manager.LLMManager
   markitdown_gui.core.i18n_manager.I18nManager
   markitdown_gui.core.theme_manager.ThemeManager
   markitdown_gui.core.accessibility_manager.AccessibilityManager
   markitdown_gui.core.logger.get_logger
   markitdown_gui.core.logger.setup_logging

UI 모듈
~~~~~~~

.. autosummary::
   :toctree: _autosummary/ui
   :nosignatures:

   markitdown_gui.ui.main_window.MainWindow
   markitdown_gui.ui.components.file_list_widget.FileListWidget
   markitdown_gui.ui.components.progress_widget.ProgressWidget
   markitdown_gui.ui.components.log_widget.LogWidget
   markitdown_gui.ui.settings_dialog.SettingsDialog

열거형 및 상수
~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary/enums
   :nosignatures:

   markitdown_gui.core.models.FileType
   markitdown_gui.core.models.ConversionStatus
   markitdown_gui.core.models.LLMProvider
   markitdown_gui.core.models.TokenUsageType

예외 클래스
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary/exceptions
   :nosignatures:

   markitdown_gui.core.exceptions.MarkItDownError
   markitdown_gui.core.exceptions.ConfigurationError
   markitdown_gui.core.exceptions.ConversionError
   markitdown_gui.core.exceptions.LLMError

전체 API 트리
-----------

.. automodule:: markitdown_gui
   :members:
   :undoc-members:
   :show-inheritance:
   :recursive:

주요 클래스 상세
--------------

ConfigManager
~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.config_manager.ConfigManager
   :members:
   :inherited-members:
   :show-inheritance:

MainWindow
~~~~~~~~~~

.. autoclass:: markitdown_gui.ui.main_window.MainWindow
   :members:
   :inherited-members:
   :show-inheritance:

ConversionManager
~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.conversion_manager.ConversionManager
   :members:
   :inherited-members:
   :show-inheritance:

FileManager
~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.file_manager.FileManager
   :members:
   :inherited-members:
   :show-inheritance:

LLMManager
~~~~~~~~~~

.. autoclass:: markitdown_gui.core.llm_manager.LLMManager
   :members:
   :inherited-members:
   :show-inheritance:

데이터 모델
~~~~~~~~~~

FileInfo
^^^^^^^^

.. autoclass:: markitdown_gui.core.models.FileInfo
   :members:
   :show-inheritance:

ConversionResult
^^^^^^^^^^^^^^^

.. autoclass:: markitdown_gui.core.models.ConversionResult
   :members:
   :show-inheritance:

AppConfig
^^^^^^^^^

.. autoclass:: markitdown_gui.core.models.AppConfig
   :members:
   :show-inheritance:

LLMConfig
^^^^^^^^^

.. autoclass:: markitdown_gui.core.models.LLMConfig
   :members:
   :show-inheritance:

함수 인덱스
----------

설정 관련 함수
~~~~~~~~~~~~

.. autofunction:: markitdown_gui.core.logger.setup_logging
.. autofunction:: markitdown_gui.core.logger.get_logger
.. autofunction:: markitdown_gui.core.i18n_manager.init_i18n
.. autofunction:: markitdown_gui.core.theme_manager.init_theme_manager
.. autofunction:: markitdown_gui.core.accessibility_manager.init_accessibility_manager

유틸리티 함수
~~~~~~~~~~~

.. autofunction:: markitdown_gui.core.models.get_file_type

상수 및 변수
----------

파일 타입 아이콘
~~~~~~~~~~~~~~

.. autodata:: markitdown_gui.core.models.FILE_TYPE_ICONS

   파일 타입별 아이콘 매핑 딕셔너리

지원되는 확장자
~~~~~~~~~~~~~

각 FileType 열거형 값에 대응하는 파일 확장자들:

.. code-block:: python

   SUPPORTED_EXTENSIONS = {
       FileType.DOCX: ['.docx'],
       FileType.PPTX: ['.pptx'],
       FileType.XLSX: ['.xlsx', '.xls'],
       FileType.PDF: ['.pdf'],
       FileType.JPG: ['.jpg', '.jpeg'],
       FileType.PNG: ['.png'],
       FileType.MP3: ['.mp3'],
       FileType.WAV: ['.wav'],
       FileType.HTML: ['.html', '.htm'],
       FileType.CSV: ['.csv'],
       FileType.TXT: ['.txt'],
       FileType.ZIP: ['.zip'],
       FileType.EPUB: ['.epub']
   }

API 버전 정보
-----------

.. autodata:: markitdown_gui.__version__

   현재 API 버전

.. autodata:: markitdown_gui.__author__

   개발자 정보

빠른 참조
--------

**핵심 클래스 생성:**

.. code-block:: python

   # 설정 관리자
   from markitdown_gui.core.config_manager import ConfigManager
   config_manager = ConfigManager()

   # 메인 윈도우
   from markitdown_gui.ui.main_window import MainWindow
   main_window = MainWindow(config_manager)

   # 변환 관리자
   from markitdown_gui.core.conversion_manager import ConversionManager
   conversion_manager = ConversionManager(config_manager.get_config())

**파일 정보 생성:**

.. code-block:: python

   from pathlib import Path
   from markitdown_gui.core.models import FileInfo, get_file_type
   
   file_path = Path("document.pdf")
   file_info = FileInfo(
       path=file_path,
       name=file_path.name,
       size=file_path.stat().st_size,
       modified_time=datetime.fromtimestamp(file_path.stat().st_mtime),
       file_type=get_file_type(file_path)
   )

**변환 실행:**

.. code-block:: python

   # 단일 파일 변환
   result = conversion_manager.convert_file(file_info)
   
   # 배치 변환
   results = conversion_manager.convert_files([file_info1, file_info2])

**LLM 설정:**

.. code-block:: python

   from markitdown_gui.core.models import LLMConfig, LLMProvider
   
   llm_config = LLMConfig(
       provider=LLMProvider.OPENAI,
       model="gpt-4o-mini",
       temperature=0.1
   )
   config_manager.update_llm_config(llm_config)

색인
----

* :ref:`genindex` - 일반 색인
* :ref:`modindex` - 모듈 색인
* :ref:`search` - 검색 페이지

.. seealso::

   * :doc:`overview` - API 개요
   * :doc:`core/index` - 코어 모듈 상세
   * :doc:`ui/index` - UI 모듈 상세