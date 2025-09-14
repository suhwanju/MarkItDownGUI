문제 해결
========

MarkItDown GUI 사용 중 발생할 수 있는 문제들과 해결 방법을 안내합니다.

일반적인 문제
-----------

애플리케이션 시작 오류
~~~~~~~~~~~~~~~~~~

**증상**: 애플리케이션이 시작되지 않음

**원인과 해결방법**:

1. **Python 버전 확인**
   
   .. code-block:: bash
   
      python --version
      # Python 3.8 이상 필요

2. **PyQt6 설치 확인**
   
   .. code-block:: bash
   
      python -c "import PyQt6; print('PyQt6 설치됨')"

3. **의존성 재설치**
   
   .. code-block:: bash
   
      pip uninstall markitdown-gui
      pip install markitdown-gui

변환 관련 문제
------------

파일 변환 실패
~~~~~~~~~~~~

**증상**: 특정 파일이 변환되지 않음

**진단 단계**:

1. **파일 형식 확인**
   
   .. list-table:: 지원되는 파일 형식
      :widths: 30 70
      :header-rows: 1
   
      * - 형식
        - 확장자
      * - 문서
        - .pdf, .docx, .pptx, .txt
      * - 이미지
        - .png, .jpg, .jpeg, .gif, .bmp

2. **파일 크기 확인**
   
   .. note::
      최대 파일 크기: 100MB
      
      더 큰 파일의 경우 파일을 분할하여 처리하세요.

3. **파일 권한 확인**
   
   .. code-block:: bash
   
      # 파일 권한 확인 (Linux/macOS)
      ls -la 파일명.pdf
      
      # 읽기 권한이 없다면
      chmod +r 파일명.pdf

4. **메모리 사용량 확인**
   
   .. code-block:: bash
   
      # 시스템 메모리 확인
      free -h  # Linux
      top      # macOS

**해결 방법**:

.. code-block:: python

   # 변환 옵션 조정
   config = {
       "quality": "medium",  # high → medium으로 변경
       "memory_limit": "1GB",  # 메모리 제한 설정
       "timeout": 300  # 타임아웃 늘리기
   }

품질 문제
~~~~~~~~

**OCR 인식률이 낮을 때**:

1. **이미지 전처리**
   
   .. code-block:: python
   
      # 설정에서 전처리 옵션 활성화
      preprocessing_options = {
          "denoise": True,
          "enhance_contrast": True,
          "deskew": True,
          "upscale": True
      }

2. **언어 설정 확인**
   
   .. code-block:: text
   
      설정 → 변환 → OCR 언어 → 한국어 + 영어

3. **품질 모드 변경**
   
   .. code-block:: text
   
      설정 → 변환 → 품질 → 높음

성능 문제
--------

느린 변환 속도
~~~~~~~~~~~~

**원인 분석**:

1. **시스템 리소스 확인**
   
   .. code-block:: bash
   
      # CPU 사용률
      htop  # Linux
      Activity Monitor  # macOS
      Task Manager  # Windows

2. **메모리 사용량**
   
   .. code-block:: bash
   
      # 메모리 사용량 모니터링
      watch -n 1 free -h

**최적화 방법**:

1. **병렬 처리 조정**
   
   .. code-block:: json
   
      {
        "performance": {
          "worker_threads": 4,  # CPU 코어 수에 맞게 조정
          "batch_size": 5,      # 배치 크기 줄이기
          "memory_limit": "2GB"
        }
      }

2. **캐시 활용**
   
   .. code-block:: json
   
      {
        "cache": {
          "enabled": true,
          "size": "512MB",
          "cleanup_interval": 3600
        }
      }

메모리 부족 오류
~~~~~~~~~~~~~

**증상**: "메모리가 부족합니다" 오류 메시지

**해결 방법**:

1. **가용 메모리 확보**
   
   .. code-block:: bash
   
      # 다른 애플리케이션 종료
      # 브라우저 탭 정리
      # 시스템 재시작

2. **설정 조정**
   
   .. code-block:: json
   
      {
        "memory": {
          "limit": "1GB",
          "gc_threshold": 500,
          "auto_cleanup": true
        }
      }

UI 및 인터페이스 문제
-----------------

화면 표시 문제
~~~~~~~~~~~~

**증상**: UI가 깨져 보이거나 글자가 안 보임

**해결 방법**:

1. **DPI 설정 확인**
   
   .. code-block:: bash
   
      # 고해상도 디스플레이 설정
      export QT_AUTO_SCREEN_SCALE_FACTOR=1
      python main.py

2. **폰트 설정 확인**
   
   .. code-block:: text
   
      설정 → 외관 → 폰트 → 시스템 기본값

3. **테마 재설정**
   
   .. code-block:: text
   
      설정 → 외관 → 테마 → 기본값으로 재설정

한글 입력 문제
~~~~~~~~~~~~

**증상**: 한글 입력이 안 되거나 깨짐

**해결 방법**:

1. **입력기 설정**
   
   .. code-block:: bash
   
      # Linux
      export QT_IM_MODULE=fcitx
      # 또는
      export QT_IM_MODULE=ibus

2. **인코딩 확인**
   
   .. code-block:: bash
   
      export LANG=ko_KR.UTF-8
      export LC_ALL=ko_KR.UTF-8

접근성 문제
---------

키보드 탐색 문제
~~~~~~~~~~~~~

**증상**: Tab 키로 이동이 안 됨

**해결 방법**:

1. **접근성 모드 활성화**
   
   .. code-block:: text
   
      설정 → 접근성 → 키보드 탐색 활성화

2. **포커스 표시기 활성화**
   
   .. code-block:: text
   
      설정 → 접근성 → 포커스 표시기 → 강조 표시

스크린 리더 호환성
~~~~~~~~~~~~~~~

**증상**: 스크린 리더가 제대로 읽지 못함

**해결 방법**:

1. **접근성 API 활성화**
   
   .. code-block:: bash
   
      # Windows
      set QT_ACCESSIBILITY=1
      
      # Linux
      export QT_ACCESSIBILITY=1

2. **스크린 리더별 설정**
   
   .. list-table:: 스크린 리더 호환성
      :widths: 30 70
      :header-rows: 1
   
      * - 스크린 리더
        - 권장 설정
      * - NVDA
        - 브라우즈 모드 해제
      * - JAWS
        - PC 커서 모드 사용
      * - Orca
        - 애플리케이션 모드 활성화

로그 및 디버깅
-----------

로그 파일 확인
~~~~~~~~~~~~

**로그 파일 위치**:

* **Windows**: `%APPDATA%\\MarkItDown GUI\\logs\\`
* **macOS**: `~/Library/Logs/MarkItDown GUI/`
* **Linux**: `~/.local/share/markitdown-gui/logs/`

**로그 레벨 설정**:

.. code-block:: json

   {
     "logging": {
       "level": "DEBUG",  # 상세한 로그를 위해
       "console": true,   # 콘솔 출력 활성화
       "file": true       # 파일 저장 활성화
     }
   }

디버그 모드 실행
~~~~~~~~~~~~~

.. code-block:: bash

   # 디버그 모드로 실행
   python main.py --debug

   # 상세 로그 출력
   python main.py --verbose

   # 프로파일링 모드
   python main.py --profile

고급 문제 해결
-----------

설정 파일 복구
~~~~~~~~~~~~

.. code-block:: bash

   # 설정 파일 백업
   cp ~/.config/markitdown-gui/config.json config.backup

   # 기본 설정으로 재설정
   markitdown-gui --reset-config

   # 특정 설정만 재설정
   markitdown-gui --reset theme language

데이터베이스 재구축
~~~~~~~~~~~~~~~

.. code-block:: bash

   # 캐시 삭제
   rm -rf ~/.cache/markitdown-gui/

   # 임시 파일 정리
   rm -rf /tmp/markitdown-gui-*

   # 애플리케이션 재시작
   markitdown-gui --rebuild-cache

지원 요청
--------

문제 보고 방법
~~~~~~~~~~~~

1. **로그 파일 수집**
2. **시스템 정보 확인**
3. **재현 단계 정리**
4. **GitHub Issues에 보고**

시스템 정보 수집
~~~~~~~~~~~~~

.. code-block:: bash

   # 시스템 정보 수집 스크립트
   python -c "
   import sys, platform
   print(f'Python: {sys.version}')
   print(f'Platform: {platform.platform()}')
   print(f'Architecture: {platform.architecture()}')
   "

지원 채널
~~~~~~~~

* **GitHub Issues**: https://github.com/your-repo/issues
* **사용자 포럼**: https://forum.markitdown-gui.com
* **이메일 지원**: support@markitdown-gui.com
* **실시간 채팅**: Discord 서버