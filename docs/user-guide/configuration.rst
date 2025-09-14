환경 설정
========

MarkItDown GUI의 상세한 설정 옵션들을 설명합니다.

일반 설정
--------

애플리케이션 설정
~~~~~~~~~~~~~~

.. list-table:: 기본 설정
   :widths: 30 70
   :header-rows: 1

   * - 설정 항목
     - 설명
   * - 언어
     - 인터페이스 언어 선택 (한국어, English 등)
   * - 테마
     - 라이트/다크/자동 모드
   * - 폰트 크기
     - UI 폰트 크기 조절 (8pt ~ 24pt)
   * - 시작 시 업데이트 확인
     - 애플리케이션 시작 시 자동 업데이트 확인

파일 처리 설정
~~~~~~~~~~~~~

.. code-block:: json

   {
     "file_handling": {
       "max_file_size": "100MB",
       "supported_extensions": [
         ".pdf", ".docx", ".pptx", ".txt",
         ".png", ".jpg", ".jpeg", ".gif"
       ],
       "auto_cleanup": true,
       "backup_original": false,
       "default_output_format": "markdown"
     }
   }

변환 설정
--------

품질 및 성능
~~~~~~~~~~~

.. list-table:: 변환 품질 설정
   :widths: 25 25 50
   :header-rows: 1

   * - 설정
     - 기본값
     - 설명
   * - OCR 품질
     - 중간
     - 이미지 텍스트 인식 품질
   * - 병렬 처리
     - 활성화
     - CPU 코어 수에 따른 병렬 처리
   * - 메모리 제한
     - 2GB
     - 최대 메모리 사용량 제한
   * - 캐시 사용
     - 활성화
     - 변환 결과 캐싱

OCR 설정
~~~~~~~~

.. code-block:: yaml

   ocr_settings:
     engine: "tesseract"  # tesseract, paddleocr, easyocr
     languages: ["kor", "eng", "jpn"]
     confidence_threshold: 0.8
     preprocessing:
       denoise: true
       deskew: true
       enhance_contrast: true

언어 및 지역 설정
---------------

다국어 지원
~~~~~~~~~~

언어별 설정:

.. code-block:: json

   {
     "languages": {
       "ko": {
         "name": "한국어",
         "rtl": false,
         "date_format": "YYYY-MM-DD",
         "number_format": "#,###.##"
       },
       "en": {
         "name": "English",
         "rtl": false,
         "date_format": "MM/DD/YYYY",
         "number_format": "#,###.##"
       },
       "ar": {
         "name": "العربية",
         "rtl": true,
         "date_format": "DD/MM/YYYY",
         "number_format": "#,###.##"
       }
     }
   }

지역 설정
~~~~~~~~

* **시간대**: 자동 감지 또는 수동 설정
* **통화**: 기본 통화 단위 설정
* **측정 단위**: 미터법/야드파운드법
* **키보드 레이아웃**: 언어별 키보드 설정

테마 및 UI 설정
--------------

테마 시스템
~~~~~~~~~~

내장 테마:

.. list-table:: 내장 테마
   :widths: 20 40 40
   :header-rows: 1

   * - 테마명
     - 특징
     - 적용 상황
   * - Light
     - 밝은 배경, 어두운 텍스트
     - 일반적인 사무환경
   * - Dark
     - 어두운 배경, 밝은 텍스트
     - 야간 작업, 눈의 피로 감소
   * - High Contrast
     - 고대비 색상
     - 시각 장애인, 저시력자
   * - System
     - 운영체제 설정 따름
     - 자동 적응

사용자 정의 테마
~~~~~~~~~~~~~~

.. code-block:: css

   /* 커스텀 테마 예제 */
   .custom-theme {
     --primary-color: #3498db;
     --secondary-color: #2c3e50;
     --background-color: #ffffff;
     --text-color: #333333;
     --accent-color: #e74c3c;
     
     --font-family: 'Noto Sans KR', sans-serif;
     --font-size-base: 14px;
     --border-radius: 4px;
     --spacing-unit: 8px;
   }

접근성 설정
----------

시각적 접근성
~~~~~~~~~~~

.. code-block:: json

   {
     "accessibility": {
       "high_contrast": false,
       "large_fonts": false,
       "screen_reader_support": true,
       "keyboard_navigation": true,
       "focus_indicators": true,
       "color_blind_friendly": true
     }
   }

키보드 및 마우스
~~~~~~~~~~~~~

* **키보드 전용 탐색**: Tab, Shift+Tab, 화살표 키
* **사용자 정의 단축키**: 기능별 단축키 재할당
* **마우스 감도**: 더블클릭 속도, 드래그 임계값
* **터치 지원**: 터치스크린 환경 최적화

고급 설정
--------

성능 최적화
~~~~~~~~~~

.. code-block:: ini

   [performance]
   # CPU 사용률 제한 (%)
   max_cpu_usage = 80

   # 메모리 사용률 제한 (%)
   max_memory_usage = 75

   # 병렬 워커 수 (-1: 자동)
   worker_threads = -1

   # 캐시 크기 (MB)
   cache_size = 512

   # 가비지 컬렉션 임계값
   gc_threshold = 1000

로깅 설정
~~~~~~~~

.. code-block:: yaml

   logging:
     level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
     format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
     file: "markitdown_gui.log"
     max_size: "10MB"
     backup_count: 5
     
   console_logging:
     enabled: true
     level: WARNING

네트워크 설정
~~~~~~~~~~~

.. code-block:: json

   {
     "network": {
       "proxy": {
         "enabled": false,
         "host": "",
         "port": 8080,
         "username": "",
         "password": ""
       },
       "timeout": 30,
       "retry_attempts": 3,
       "user_agent": "MarkItDown GUI/0.1.0"
     }
   }

플러그인 설정
-----------

플러그인 관리
~~~~~~~~~~~

.. code-block:: json

   {
     "plugins": {
       "enabled": true,
       "auto_load": true,
       "search_paths": [
         "./plugins",
         "~/.markitdown-gui/plugins"
       ],
       "blacklist": [],
       "settings": {
         "ocr_enhance": {
           "enabled": true,
           "model": "large"
         },
         "table_detector": {
           "enabled": true,
           "confidence": 0.85
         }
       }
     }
   }

설정 파일 관리
-----------

설정 파일 위치
~~~~~~~~~~~~

* **Windows**: `%APPDATA%\\MarkItDown GUI\\config.json`
* **macOS**: `~/Library/Application Support/MarkItDown GUI/config.json`
* **Linux**: `~/.config/markitdown-gui/config.json`

설정 백업 및 복원
~~~~~~~~~~~~~~

.. code-block:: bash

   # 설정 백업
   markitdown-gui --export-config config_backup.json

   # 설정 복원
   markitdown-gui --import-config config_backup.json

   # 기본 설정으로 리셋
   markitdown-gui --reset-config

명령줄 설정
~~~~~~~~~~

.. code-block:: bash

   # 특정 설정으로 실행
   markitdown-gui --config custom_config.json

   # 설정 값 직접 지정
   markitdown-gui --theme dark --language ko --quality high