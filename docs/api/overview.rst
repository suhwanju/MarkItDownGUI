API 개요
========

MarkItDown GUI API 문서에 오신 것을 환영합니다. 이 섹션에서는 애플리케이션의 모든 모듈, 클래스, 함수에 대한 포괄적이고 상세한 정보를 제공합니다.

아키텍처 개요
-----------

MarkItDown GUI는 계층화된 아키텍처로 설계되었으며, 다음과 같은 주요 레이어로 구성되어 있습니다:

.. graphviz::

   digraph ArchitectureOverview {
       rankdir=TB;
       node [shape=box, style=rounded];
       
       // UI 레이어
       subgraph cluster_ui {
           label="Presentation Layer (UI)";
           style=filled;
           color=lightblue;
           
           MainWindow [label="MainWindow"];
           Components [label="UI Components"];
           Dialogs [label="Dialog Windows"];
       }
       
       // 비즈니스 로직 레이어
       subgraph cluster_business {
           label="Business Logic Layer";
           style=filled;
           color=lightgreen;
           
           ConversionManager [label="Conversion Manager"];
           FileManager [label="File Manager"];
           LLMManager [label="LLM Manager"];
       }
       
       // 코어 서비스 레이어
       subgraph cluster_core {
           label="Core Services Layer";
           style=filled;
           color=lightyellow;
           
           ConfigManager [label="Config Manager"];
           I18nManager [label="I18n Manager"];
           ThemeManager [label="Theme Manager"];
           AccessibilityManager [label="Accessibility Manager"];
       }
       
       // 데이터/모델 레이어
       subgraph cluster_data {
           label="Data & Model Layer";
           style=filled;
           color=lightcoral;
           
           Models [label="Data Models"];
           Logger [label="Logger"];
           Exceptions [label="Exceptions"];
       }
       
       // 의존성 관계
       MainWindow -> Components;
       MainWindow -> Dialogs;
       MainWindow -> ConversionManager;
       
       ConversionManager -> FileManager;
       ConversionManager -> LLMManager;
       ConversionManager -> ConfigManager;
       
       Components -> ThemeManager;
       Components -> I18nManager;
       Components -> AccessibilityManager;
       
       FileManager -> Models;
       LLMManager -> Models;
       ConfigManager -> Models;
       
       ConversionManager -> Logger;
       FileManager -> Logger;
       ConfigManager -> Logger;
   }

Core Modules (핵심 모듈)
~~~~~~~~~~~~~~~~~~~~~~~

**설정 및 구성 관리:**

* :doc:`core/config_manager` - 애플리케이션 설정 관리 및 영속화
* :doc:`core/models` - 데이터 모델 및 구조체 정의
* :doc:`core/logger` - 통합 로깅 시스템

**변환 엔진:**

* :doc:`core/conversion_manager` - 파일 변환 오케스트레이션
* :doc:`core/file_manager` - 파일 시스템 관리 및 I/O 작업
* :doc:`core/llm_manager` - LLM API 클라이언트 및 토큰 관리

**사용자 경험:**

* :doc:`core/i18n_manager` - 국제화 및 다국어 지원
* :doc:`core/theme_manager` - UI 테마 관리 및 동적 스타일링
* :doc:`core/accessibility_manager` - 접근성 기능 및 WCAG 준수

**시스템 통합:**

* :doc:`core/api_client` - 외부 API 통신 및 네트워킹
* :doc:`core/exceptions` - 커스텀 예외 클래스 및 에러 처리

UI Components (사용자 인터페이스)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**메인 인터페이스:**

* :doc:`ui/main_window` - 애플리케이션 메인 윈도우 및 레이아웃 관리

**재사용 가능한 컴포넌트:**

* :doc:`ui/components/file_list_widget` - 파일 목록 표시 및 관리 위젯
* :doc:`ui/components/progress_widget` - 진행률 표시 및 상태 모니터링
* :doc:`ui/components/log_widget` - 실시간 로그 표시 및 필터링
* :doc:`ui/components/theme_selector` - 테마 선택 및 미리보기

**대화상자 및 팝업:**

* :doc:`ui/dialogs/settings_dialog` - 종합 설정 관리 인터페이스
* :doc:`ui/dialogs/preview_dialog` - 변환 결과 미리보기
* :doc:`ui/dialogs/file_viewer_dialog` - 통합 파일 뷰어

Utilities (유틸리티)
~~~~~~~~~~~~~~~~~~

* :doc:`utils/file_handler` - 파일 처리 및 유효성 검사 유틸리티
* :doc:`utils/performance_optimizer` - 성능 최적화 및 메모리 관리
* :doc:`utils/error_handler` - 전역 에러 처리 및 복구 메커니즘

모듈별 상세 문서
--------------

.. toctree::
   :maxdepth: 3
   :caption: API 참조
   
   core/index
   ui/index
   utils/index

주요 특징
--------

**타입 안전성**

모든 모듈은 Python 타입 힌트를 사용하여 타입 안전성을 보장합니다:

.. code-block:: python

   from typing import Optional, List, Dict, Any
   from pathlib import Path
   from markitdown_gui.core.models import FileInfo, ConversionResult

   def convert_files(files: List[FileInfo]) -> List[ConversionResult]:
       """파일 목록을 변환하여 결과를 반환합니다."""
       pass

**비동기 처리**

대용량 파일 처리와 LLM API 호출을 위한 비동기 처리를 지원합니다:

.. code-block:: python

   import asyncio
   from markitdown_gui.core.llm_manager import LLMManager

   async def process_with_llm(content: str) -> str:
       llm_manager = LLMManager()
       result = await llm_manager.process_async(content)
       return result.content

**이벤트 기반 아키텍처**

PyQt6 신호/슬롯 시스템을 활용한 느슨한 결합:

.. code-block:: python

   from PyQt6.QtCore import pyqtSignal, QObject

   class ConversionManager(QObject):
       progress_updated = pyqtSignal(int)  # 진행률 업데이트 신호
       conversion_completed = pyqtSignal(str)  # 변환 완료 신호
       
       def start_conversion(self, file_path: str):
           # 변환 로직...
           self.progress_updated.emit(50)  # 신호 발송

자동 생성 API 문서
----------------

전체 API 문서는 소스코드의 docstring에서 자동으로 생성됩니다.

.. autosummary::
   :toctree: generated/
   :recursive:
   
   markitdown_gui

주요 클래스 다이어그램
-------------------

.. graphviz::

   digraph G {
       rankdir=TB;
       node [shape=box, style=rounded];
       
       MainWindow -> ConfigManager;
       MainWindow -> I18nManager;
       MainWindow -> AccessibilityManager;
       MainWindow -> ThemeManager;
       
       ConfigManager -> FileHandler;
       I18nManager -> Logger;
       AccessibilityManager -> Logger;
       ThemeManager -> Logger;
       
       ConversionWidget -> ApiClient;
       SettingsDialog -> ConfigManager;
       ThemeSelector -> ThemeManager;
   }

사용 예제
--------

기본 사용법
~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.config_manager import ConfigManager
   from markitdown_gui.ui.main_window import MainWindow
   
   # 설정 관리자 초기화
   config_manager = ConfigManager()
   config = config_manager.load_config()
   
   # 메인 윈도우 생성
   main_window = MainWindow(config_manager)
   main_window.show()

설정 관리
~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.config_manager import ConfigManager
   
   config_manager = ConfigManager()
   
   # 설정 로드
   config = config_manager.load_config()
   
   # 설정 수정
   config['theme'] = 'dark'
   config['language'] = 'ko'
   
   # 설정 저장
   config_manager.save_config(config)

테마 변경
~~~~~~~~

.. code-block:: python

   from markitdown_gui.utils.theme_manager import ThemeManager
   
   theme_manager = ThemeManager()
   
   # 다크 테마 적용
   theme_manager.apply_theme('dark')
   
   # 커스텀 테마 생성
   custom_theme = theme_manager.create_custom_theme(
       primary_color='#3498db',
       secondary_color='#2c3e50'
   )
   theme_manager.apply_theme(custom_theme)

API 참조
-------

상세한 API 참조는 다음 섹션에서 확인할 수 있습니다:

* :doc:`core` - 핵심 모듈
* :doc:`components` - UI 컴포넌트
* :doc:`configuration` - 설정 관리
* :doc:`events` - 이벤트 시스템
* :doc:`plugins` - 플러그인 시스템