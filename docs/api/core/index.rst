Core 모듈
=========

MarkItDown GUI의 핵심 기능을 제공하는 모듈들입니다.

.. toctree::
   :maxdepth: 2
   :caption: Core 모듈

   config_manager
   logger
   models
   conversion_manager
   file_manager
   i18n_manager
   theme_manager
   accessibility_manager
   llm_manager
   api_client
   exceptions

모듈 개요
--------

**설정 및 구성**

* :doc:`config_manager` - 애플리케이션 설정 관리
* :doc:`models` - 데이터 모델 및 구조체 정의
* :doc:`logger` - 로깅 시스템

**변환 엔진**

* :doc:`conversion_manager` - 파일 변환 관리
* :doc:`file_manager` - 파일 시스템 관리
* :doc:`llm_manager` - LLM API 관리
* :doc:`api_client` - 외부 API 클라이언트

**사용자 경험**

* :doc:`i18n_manager` - 국제화 및 번역 관리
* :doc:`theme_manager` - UI 테마 관리
* :doc:`accessibility_manager` - 접근성 기능 관리

**오류 처리**

* :doc:`exceptions` - 커스텀 예외 클래스들

아키텍처 다이어그램
-----------------

.. graphviz::

   digraph CoreModules {
       rankdir=TB;
       node [shape=box, style=rounded];
       
       // 설정 레이어
       subgraph cluster_config {
           label="Configuration Layer";
           style=filled;
           color=lightgrey;
           
           ConfigManager;
           Models;
           Logger;
       }
       
       // 변환 레이어  
       subgraph cluster_conversion {
           label="Conversion Layer";
           style=filled;
           color=lightblue;
           
           ConversionManager;
           FileManager;
           LLMManager;
           ApiClient;
       }
       
       // UI 레이어
       subgraph cluster_ui {
           label="UI Support Layer";
           style=filled;
           color=lightgreen;
           
           I18nManager;
           ThemeManager;
           AccessibilityManager;
       }
       
       // 유틸리티 레이어
       subgraph cluster_utils {
           label="Utility Layer";
           style=filled;
           color=lightyellow;
           
           Exceptions;
       }
       
       // 의존성 관계
       ConversionManager -> FileManager;
       ConversionManager -> LLMManager;
       ConversionManager -> ConfigManager;
       
       LLMManager -> ApiClient;
       LLMManager -> ConfigManager;
       
       FileManager -> ConfigManager;
       FileManager -> Logger;
       
       I18nManager -> ConfigManager;
       ThemeManager -> ConfigManager;
       AccessibilityManager -> ConfigManager;
       
       ConfigManager -> Models;
       ConfigManager -> Logger;
   }

의존성 매트릭스
--------------

다음 표는 각 모듈 간의 의존성 관계를 보여줍니다:

+--------------------+-------------+--------+-------+---------+
| 모듈               | ConfigMgr   | Logger | Models| FileMgr |
+====================+=============+========+=======+=========+
| config_manager     | -           | ✓      | ✓     | -       |
+--------------------+-------------+--------+-------+---------+
| conversion_manager | ✓           | ✓      | ✓     | ✓       |
+--------------------+-------------+--------+-------+---------+
| file_manager       | ✓           | ✓      | ✓     | -       |
+--------------------+-------------+--------+-------+---------+
| llm_manager        | ✓           | ✓      | ✓     | -       |
+--------------------+-------------+--------+-------+---------+
| i18n_manager       | ✓           | ✓      | -     | -       |
+--------------------+-------------+--------+-------+---------+
| theme_manager      | ✓           | ✓      | -     | -       |
+--------------------+-------------+--------+-------+---------+
| accessibility_mgr  | ✓           | ✓      | ✓     | -       |
+--------------------+-------------+--------+-------+---------+

사용 패턴
--------

일반적인 모듈 사용 패턴:

.. code-block:: python

   # 1. 설정 관리자 초기화 (항상 첫 번째)
   from markitdown_gui.core.config_manager import ConfigManager
   config_manager = ConfigManager()
   config = config_manager.load_config()
   
   # 2. 로깅 시스템 설정
   from markitdown_gui.core.logger import setup_logging, get_logger
   setup_logging()
   logger = get_logger(__name__)
   
   # 3. UI 지원 모듈들 초기화
   from markitdown_gui.core.i18n_manager import init_i18n
   from markitdown_gui.core.theme_manager import init_theme_manager
   from markitdown_gui.core.accessibility_manager import init_accessibility_manager
   
   i18n_manager = init_i18n(app)
   theme_manager = init_theme_manager(config)
   accessibility_manager = init_accessibility_manager(config)
   
   # 4. 변환 시스템 초기화
   from markitdown_gui.core.file_manager import FileManager
   from markitdown_gui.core.conversion_manager import ConversionManager
   
   file_manager = FileManager(config)
   conversion_manager = ConversionManager(config, file_manager)

성능 고려사항
-----------

**초기화 순서**

모듈들은 다음 순서로 초기화해야 합니다:

1. ConfigManager (모든 다른 모듈이 의존)
2. Logger (조기 진단을 위해)
3. Models (데이터 구조 정의)
4. 나머지 모듈들 (의존성에 따라)

**메모리 관리**

* ConfigManager는 싱글톤 패턴 사용
* Logger는 모듈별 인스턴스 관리
* 대용량 파일 처리 시 FileManager의 청크 처리 사용

**병렬 처리**

* ConversionManager는 멀티스레딩 지원
* LLMManager는 비동기 요청 처리
* FileManager는 동시 파일 액세스 제어

테스트 전략
----------

각 모듈의 테스트 전략:

**단위 테스트**

.. code-block:: python

   # config_manager 테스트
   def test_config_manager():
       config_manager = ConfigManager()
       config = config_manager.load_config()
       assert config.language in ['ko', 'en', 'ja']

**통합 테스트**

.. code-block:: python

   # 변환 시스템 통합 테스트
   def test_conversion_integration():
       config_manager = ConfigManager()
       file_manager = FileManager(config_manager.get_config())
       conversion_manager = ConversionManager(
           config_manager.get_config(), 
           file_manager
       )
       
       # 테스트 파일 변환
       result = conversion_manager.convert_file("test.pdf")
       assert result.status == ConversionStatus.COMPLETED

디버깅 가이드
-----------

**로그 레벨 설정**

.. code-block:: python

   # 개발 모드 로깅
   from markitdown_gui.core.logger import setup_logging
   setup_logging(level='DEBUG', console=True)

**설정 문제 진단**

.. code-block:: python

   # 설정 검증
   config_manager = ConfigManager()
   config = config_manager.load_config()
   
   print(f"설정 파일 위치: {config_manager.config_dir}")
   print(f"LLM 설정 완료: {config_manager.is_llm_configured()}")

**변환 오류 진단**

.. code-block:: python

   # 변환 시스템 상태 확인
   from markitdown_gui.core.conversion_manager import ConversionManager
   
   conversion_manager = ConversionManager(config, file_manager)
   status = conversion_manager.get_system_status()
   print(f"변환 시스템 상태: {status}")

모범 사례
--------

**에러 처리**

.. code-block:: python

   from markitdown_gui.core.exceptions import (
       ConfigurationError, 
       ConversionError, 
       LLMError
   )
   
   try:
       # 변환 작업
       result = conversion_manager.convert_file(file_path)
   except ConversionError as e:
       logger.error(f"변환 실패: {e}")
       # 사용자에게 알림
   except LLMError as e:
       logger.error(f"LLM 오류: {e}")
       # LLM 설정 확인 요청

**리소스 관리**

.. code-block:: python

   # 컨텍스트 매니저 사용
   with conversion_manager.batch_context():
       for file_path in file_paths:
           conversion_manager.queue_conversion(file_path)

**설정 업데이트**

.. code-block:: python

   # 설정 변경 시 관련 모듈들 업데이트
   def update_settings(new_config):
       config_manager.save_config(new_config)
       
       # 관련 모듈들에 설정 변경 알림
       theme_manager.update_config(new_config)
       i18n_manager.update_config(new_config)
       conversion_manager.update_config(new_config)

API 버전 호환성
--------------

현재 API 버전: **0.1.0**

**호환성 정책**

* 마이너 버전 업데이트: 하위 호환성 보장
* 메이저 버전 업데이트: 마이그레이션 가이드 제공
* 디프리케이션: 최소 2개 마이너 버전 동안 경고

**API 변경 로그**

버전 0.1.0 (현재)
~~~~~~~~~~~~~~~~

* 초기 API 릴리스
* 모든 핵심 모듈 포함
* 기본 변환 기능 지원