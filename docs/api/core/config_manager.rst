config_manager 모듈
==================

.. automodule:: markitdown_gui.core.config_manager
   :members:
   :undoc-members:
   :show-inheritance:

개요
----

ConfigManager 클래스는 MarkItDown GUI 애플리케이션의 모든 설정을 관리하는 핵심 컴포넌트입니다.
INI 파일과 JSON 파일을 사용하여 사용자 설정, 파일 타입 설정, LLM 설정 등을 저장하고 관리합니다.

주요 기능
--------

* **설정 파일 관리**: INI 및 JSON 형식의 설정 파일 읽기/쓰기
* **LLM 설정**: OpenAI, Azure OpenAI 등 다양한 LLM 공급업체 설정
* **UI 설정**: 창 크기, 테마, 언어 등 사용자 인터페이스 설정
* **파일 타입 관리**: 지원되는 파일 형식 및 확장자 관리
* **보안 관리**: API 키는 keyring을 통한 안전한 저장

ConfigManager 클래스
-------------------

.. autoclass:: markitdown_gui.core.config_manager.ConfigManager
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:

   .. automethod:: __init__

      설정 관리자를 초기화합니다.

      :param config_dir: 설정 파일이 저장될 디렉토리 경로
      :type config_dir: Path, optional

   .. automethod:: load_config

      설정 파일에서 애플리케이션 설정을 로드합니다.

      :returns: 로드된 애플리케이션 설정
      :rtype: AppConfig
      :raises Exception: 설정 파일 읽기 실패 시

      **예제:**

      .. code-block:: python

         config_manager = ConfigManager()
         config = config_manager.load_config()
         print(f"현재 테마: {config.theme}")

   .. automethod:: save_config

      현재 설정을 파일에 저장합니다.

      :param config: 저장할 설정 객체 (None이면 현재 설정 저장)
      :type config: AppConfig, optional
      :returns: 저장 성공 여부
      :rtype: bool

      **예제:**

      .. code-block:: python

         config_manager = ConfigManager()
         config = config_manager.get_config()
         config.theme = 'dark'
         config_manager.save_config(config)

   .. automethod:: get_config

      현재 로드된 설정을 반환합니다.

      :returns: 현재 애플리케이션 설정
      :rtype: AppConfig

   .. automethod:: update_config

      설정을 부분적으로 업데이트합니다.

      :param kwargs: 업데이트할 설정 키-값 쌍
      :type kwargs: dict

      **예제:**

      .. code-block:: python

         config_manager.update_config(
             theme='dark',
             language='ko',
             max_concurrent_conversions=5
         )

   .. automethod:: get_llm_config

      LLM 관련 설정을 반환합니다.

      :returns: LLM 설정 객체
      :rtype: LLMConfig

      **예제:**

      .. code-block:: python

         llm_config = config_manager.get_llm_config()
         print(f"LLM 제공업체: {llm_config.provider}")
         print(f"모델: {llm_config.model}")

   .. automethod:: update_llm_config

      LLM 설정을 업데이트합니다.

      :param llm_config: 새로운 LLM 설정
      :type llm_config: LLMConfig

   .. automethod:: is_llm_configured

      LLM이 올바르게 설정되었는지 확인합니다.

      :returns: LLM 설정 완료 여부
      :rtype: bool

   .. automethod:: add_recent_directory

      최근 사용한 디렉토리를 추가합니다.

      :param directory: 추가할 디렉토리 경로
      :type directory: str

      **예제:**

      .. code-block:: python

         config_manager.add_recent_directory("/home/user/documents")

   .. automethod:: reset_to_default

      모든 설정을 기본값으로 리셋합니다.

      **예제:**

      .. code-block:: python

         config_manager.reset_to_default()

   .. automethod:: get_ocr_settings

      OCR 관련 설정을 반환합니다.

      :returns: OCR 설정 딕셔너리
      :rtype: Dict[str, Any]

      **반환 값 예시:**

      .. code-block:: python

         {
             'enable_llm_ocr': True,
             'ocr_language': 'ko',
             'max_image_size': 2048
         }

   .. automethod:: update_ocr_settings

      OCR 설정을 업데이트합니다.

      :param kwargs: OCR 설정 키-값 쌍
      :type kwargs: dict

      **예제:**

      .. code-block:: python

         config_manager.update_ocr_settings(
             enable_llm_ocr=True,
             ocr_language='en',
             max_image_size=4096
         )

   .. automethod:: get_token_usage_settings

      토큰 사용량 추적 설정을 반환합니다.

      :returns: 토큰 사용량 설정 딕셔너리
      :rtype: Dict[str, Any]

설정 파일 구조
--------------

settings.ini
~~~~~~~~~~~~

.. code-block:: ini

   [General]
   language = ko
   theme = auto

   [Conversion]
   output_directory = ./output
   max_concurrent_conversions = 3
   include_subdirectories = true
   max_file_size_mb = 100

   [LLM]
   llm_provider = openai
   llm_model = gpt-4o-mini
   enable_llm_ocr = true
   ocr_language = ko
   max_image_size = 2048
   llm_temperature = 0.7
   llm_max_tokens = 4000
   track_token_usage = true
   token_usage_limit_monthly = 1000000

   [UI]
   window_width = 1200
   window_height = 800
   recent_directories = /home/user/docs,/home/user/projects

file_types.json
~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "supported_extensions": [
       ".docx", ".pptx", ".xlsx", ".pdf", 
       ".jpg", ".jpeg", ".png", ".mp3", 
       ".wav", ".html", ".csv", ".txt"
     ],
     "file_type_descriptions": {
       ".docx": "Microsoft Word 문서",
       ".pdf": "PDF 문서",
       ".jpg": "JPEG 이미지"
     }
   }

사용 예제
--------

기본 사용법
~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.config_manager import ConfigManager

   # 설정 관리자 생성
   config_manager = ConfigManager()

   # 설정 로드
   config = config_manager.load_config()

   # 설정 조회
   print(f"현재 언어: {config.language}")
   print(f"현재 테마: {config.theme}")
   print(f"출력 디렉토리: {config.output_directory}")

설정 수정
~~~~~~~~

.. code-block:: python

   # 개별 설정 업데이트
   config_manager.update_config(
       theme='dark',
       language='en',
       max_concurrent_conversions=5
   )

   # 또는 설정 객체 직접 수정 후 저장
   config = config_manager.get_config()
   config.theme = 'light'
   config.output_directory = Path('/home/user/output')
   config_manager.save_config(config)

LLM 설정 관리
~~~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.models import LLMConfig, LLMProvider

   # 현재 LLM 설정 확인
   llm_config = config_manager.get_llm_config()
   print(f"LLM 제공업체: {llm_config.provider}")

   # LLM 설정 업데이트
   new_llm_config = LLMConfig(
       provider=LLMProvider.AZURE,
       model="gpt-4",
       base_url="https://your-resource.openai.azure.com/",
       api_version="2024-02-15-preview",
       temperature=0.5,
       max_tokens=2000
   )
   config_manager.update_llm_config(new_llm_config)

최근 디렉토리 관리
~~~~~~~~~~~~~~~~

.. code-block:: python

   # 최근 사용 디렉토리 추가
   config_manager.add_recent_directory("/home/user/documents")
   config_manager.add_recent_directory("/home/user/projects")

   # 최근 디렉토리 목록 확인
   config = config_manager.get_config()
   for directory in config.recent_directories:
       print(f"최근 디렉토리: {directory}")

OCR 설정 관리
~~~~~~~~~~~~

.. code-block:: python

   # OCR 설정 확인
   ocr_settings = config_manager.get_ocr_settings()
   print(f"OCR 활성화: {ocr_settings['enable_llm_ocr']}")

   # OCR 설정 업데이트
   config_manager.update_ocr_settings(
       enable_llm_ocr=True,
       ocr_language='en',
       max_image_size=4096
   )

토큰 사용량 설정
~~~~~~~~~~~~~~

.. code-block:: python

   # 토큰 사용량 설정 확인
   token_settings = config_manager.get_token_usage_settings()
   print(f"토큰 추적: {token_settings['track_token_usage']}")

   # 월간 토큰 제한 설정
   config_manager.update_config(
       track_token_usage=True,
       token_usage_limit_monthly=500000
   )

고급 사용법
~~~~~~~~~~

.. code-block:: python

   from pathlib import Path

   # 커스텀 설정 디렉토리 사용
   custom_config_dir = Path("/etc/markitdown-gui")
   config_manager = ConfigManager(config_dir=custom_config_dir)

   # 설정 완전성 검사
   if config_manager.is_llm_configured():
       print("LLM이 올바르게 설정되었습니다.")
   else:
       print("LLM 설정이 필요합니다.")

   # 설정 초기화
   config_manager.reset_to_default()
   print("설정이 기본값으로 리셋되었습니다.")

관련 모듈
--------

* :doc:`models` - AppConfig, LLMConfig 등 설정 모델
* :doc:`logger` - 로깅 시스템
* :doc:`../ui/settings_dialog` - 설정 UI

.. seealso::

   * :class:`markitdown_gui.core.models.AppConfig` - 애플리케이션 설정 모델
   * :class:`markitdown_gui.core.models.LLMConfig` - LLM 설정 모델
   * :doc:`../user-guide/configuration` - 설정 사용자 가이드