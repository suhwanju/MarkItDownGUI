models 모듈
===========

.. automodule:: markitdown_gui.core.models
   :members:
   :undoc-members:
   :show-inheritance:

개요
----

models 모듈은 MarkItDown GUI 애플리케이션에서 사용되는 모든 데이터 구조와 모델을 정의합니다.
데이터클래스(dataclass)와 열거형(Enum)을 사용하여 타입 안전성과 명확한 데이터 구조를 제공합니다.

주요 기능
--------

* **타입 안전성**: 강타입 데이터 모델로 오류 방지
* **데이터 검증**: 자동 유효성 검사 및 변환
* **직렬화**: JSON/설정 파일과의 호환성
* **속성 접근**: 계산된 속성을 통한 편의 기능
* **확장성**: 새로운 데이터 타입 쉽게 추가 가능

데이터 모델
----------

파일 관련 모델
~~~~~~~~~~~~~

FileType (열거형)
~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.FileType
   :members:
   :undoc-members:

   지원되는 파일 형식을 정의하는 열거형입니다.

   **Office 문서:**
   
   * ``DOCX`` - Microsoft Word 문서
   * ``PPTX`` - Microsoft PowerPoint 프레젠테이션  
   * ``XLSX`` - Microsoft Excel 스프레드시트
   * ``XLS`` - Microsoft Excel 97-2003 스프레드시트

   **PDF 문서:**
   
   * ``PDF`` - Adobe PDF 문서

   **이미지 파일:**
   
   * ``JPG``, ``JPEG`` - JPEG 이미지
   * ``PNG`` - PNG 이미지
   * ``GIF`` - GIF 애니메이션 이미지
   * ``BMP`` - 비트맵 이미지
   * ``TIFF`` - TIFF 이미지

   **오디오 파일:**
   
   * ``MP3`` - MP3 오디오 파일
   * ``WAV`` - WAV 오디오 파일

   **웹/텍스트 파일:**
   
   * ``HTML``, ``HTM`` - HTML 웹 페이지
   * ``CSV`` - CSV 데이터 파일
   * ``JSON`` - JSON 데이터 파일
   * ``XML`` - XML 데이터 파일
   * ``TXT`` - 일반 텍스트 파일

   **아카이브 파일:**
   
   * ``ZIP`` - ZIP 압축 파일

   **전자책:**
   
   * ``EPUB`` - EPUB 전자책

   **기타:**
   
   * ``UNKNOWN`` - 지원되지 않는 파일 형식

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import FileType, get_file_type
      from pathlib import Path

      # 파일 타입 확인
      file_path = Path("document.docx")
      file_type = get_file_type(file_path)
      
      if file_type == FileType.DOCX:
          print("Microsoft Word 문서입니다.")
      elif file_type == FileType.UNKNOWN:
          print("지원되지 않는 파일 형식입니다.")

FileInfo (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.FileInfo
   :members:
   :undoc-members:

   개별 파일의 정보를 저장하는 데이터클래스입니다.

   :param path: 파일 경로
   :type path: Path
   :param name: 파일 이름
   :type name: str
   :param size: 파일 크기 (바이트)
   :type size: int
   :param modified_time: 수정 시간
   :type modified_time: datetime
   :param file_type: 파일 타입
   :type file_type: FileType
   :param is_selected: 선택 여부
   :type is_selected: bool
   :param conversion_status: 변환 상태
   :type conversion_status: ConversionStatus

   **속성:**

   .. automethod:: size_formatted
      :property:

      파일 크기를 사람이 읽기 쉬운 형태로 반환합니다.

      :returns: 포맷된 파일 크기 (예: "1.5 MB")
      :rtype: str

   .. automethod:: extension
      :property:

      파일 확장자를 반환합니다.

      :returns: 소문자 확장자 (예: ".pdf")
      :rtype: str

   **예제:**

   .. code-block:: python

      from pathlib import Path
      from datetime import datetime
      from markitdown_gui.core.models import FileInfo, FileType, ConversionStatus

      # 파일 정보 생성
      file_info = FileInfo(
          path=Path("/home/user/document.pdf"),
          name="document.pdf",
          size=1024000,  # 1MB
          modified_time=datetime.now(),
          file_type=FileType.PDF,
          is_selected=True,
          conversion_status=ConversionStatus.PENDING
      )

      print(f"파일 크기: {file_info.size_formatted}")  # "1000.0 KB"
      print(f"확장자: {file_info.extension}")  # ".pdf"

변환 관련 모델
~~~~~~~~~~~~~

ConversionStatus (열거형)
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.ConversionStatus
   :members:
   :undoc-members:

   파일 변환의 상태를 나타내는 열거형입니다.

   * ``PENDING`` - 변환 대기 중
   * ``IN_PROGRESS`` - 변환 진행 중
   * ``SUCCESS`` - 변환 성공
   * ``FAILED`` - 변환 실패
   * ``CANCELLED`` - 변환 취소됨

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import ConversionStatus

      # 상태 확인
      if status == ConversionStatus.SUCCESS:
          print("변환이 성공적으로 완료되었습니다.")
      elif status == ConversionStatus.FAILED:
          print("변환 중 오류가 발생했습니다.")

ConversionResult (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.ConversionResult
   :members:
   :undoc-members:

   파일 변환 결과를 저장하는 데이터클래스입니다.

   :param file_info: 변환된 파일 정보
   :type file_info: FileInfo
   :param status: 변환 상태
   :type status: ConversionStatus
   :param output_path: 출력 파일 경로
   :type output_path: Path, optional
   :param error_message: 오류 메시지
   :type error_message: str, optional
   :param conversion_time: 변환 시간 (초)
   :type conversion_time: float, optional
   :param metadata: 추가 메타데이터
   :type metadata: Dict[str, Any], optional

   **속성:**

   .. automethod:: is_success
      :property:

      변환 성공 여부를 반환합니다.

      :returns: 변환 성공 시 True
      :rtype: bool

   .. automethod:: conversion_time_formatted
      :property:

      변환 시간을 포맷된 문자열로 반환합니다.

      :returns: 포맷된 변환 시간 (예: "1.5s", "500ms")
      :rtype: str

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import ConversionResult, ConversionStatus

      # 성공한 변환 결과
      result = ConversionResult(
          file_info=file_info,
          status=ConversionStatus.SUCCESS,
          output_path=Path("/output/document.md"),
          conversion_time=2.5,
          metadata={"pages": 10, "word_count": 1500}
      )

      if result.is_success:
          print(f"변환 완료: {result.conversion_time_formatted}")

ConversionProgress (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.ConversionProgress
   :members:
   :undoc-members:

   배치 변환의 진행 상황을 추적하는 데이터클래스입니다.

   :param total_files: 전체 파일 수
   :type total_files: int
   :param completed_files: 완료된 파일 수
   :type completed_files: int
   :param current_file: 현재 처리 중인 파일
   :type current_file: str, optional
   :param current_status: 현재 상태 메시지
   :type current_status: str

   **속성:**

   .. automethod:: progress_percent
      :property:

      진행률을 퍼센트로 반환합니다.

      :returns: 진행률 (0.0-100.0)
      :rtype: float

   .. automethod:: is_complete
      :property:

      작업 완료 여부를 반환합니다.

      :returns: 모든 파일 처리 완료 시 True
      :rtype: bool

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import ConversionProgress

      progress = ConversionProgress(
          total_files=10,
          completed_files=7,
          current_file="document8.pdf",
          current_status="OCR 처리 중..."
      )

      print(f"진행률: {progress.progress_percent:.1f}%")  # "70.0%"
      print(f"완료 여부: {progress.is_complete}")  # False

설정 모델
~~~~~~~~

AppConfig (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.AppConfig
   :members:
   :undoc-members:

   애플리케이션의 전체 설정을 저장하는 데이터클래스입니다.

   **일반 설정:**

   :param language: 인터페이스 언어 ('ko', 'en', 'ja')
   :type language: str
   :param theme: UI 테마 ('light', 'dark', 'auto')
   :type theme: str

   **변환 설정:**

   :param output_directory: 출력 디렉토리
   :type output_directory: Path
   :param max_concurrent_conversions: 최대 동시 변환 수
   :type max_concurrent_conversions: int
   :param include_subdirectories: 하위 디렉토리 포함 여부
   :type include_subdirectories: bool

   **파일 설정:**

   :param supported_extensions: 지원되는 확장자 목록
   :type supported_extensions: List[str]
   :param max_file_size_mb: 최대 파일 크기 (MB)
   :type max_file_size_mb: int

   **LLM 설정:**

   :param llm_provider: LLM 공급업체
   :type llm_provider: str
   :param llm_model: LLM 모델명
   :type llm_model: str
   :param enable_llm_ocr: LLM OCR 활성화 여부
   :type enable_llm_ocr: bool

   **UI 설정:**

   :param window_width: 창 너비
   :type window_width: int
   :param window_height: 창 높이
   :type window_height: int
   :param recent_directories: 최근 사용 디렉토리
   :type recent_directories: List[str]

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import AppConfig
      from pathlib import Path

      # 기본 설정 생성
      config = AppConfig()
      
      # 설정 수정
      config.language = 'en'
      config.theme = 'dark'
      config.output_directory = Path('/home/user/markdown_output')
      config.max_concurrent_conversions = 5
      config.enable_llm_ocr = True

      print(f"언어: {config.language}")
      print(f"테마: {config.theme}")
      print(f"출력 디렉토리: {config.output_directory}")

LLM 관련 모델
~~~~~~~~~~~~

LLMProvider (열거형)
~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.LLMProvider
   :members:
   :undoc-members:

   LLM 서비스 공급업체를 나타내는 열거형입니다.

   * ``OPENAI`` - OpenAI GPT 모델
   * ``AZURE_OPENAI`` - Azure OpenAI 서비스
   * ``LOCAL`` - 로컬 LLM 모델
   * ``ANTHROPIC`` - Anthropic Claude 모델
   * ``GOOGLE`` - Google AI 모델

LLMConfig (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.LLMConfig
   :members:
   :undoc-members:

   LLM 서비스 설정을 저장하는 데이터클래스입니다.

   **기본 설정:**

   :param provider: LLM 공급업체
   :type provider: LLMProvider
   :param model: 모델명
   :type model: str
   :param api_key: API 키
   :type api_key: str, optional
   :param base_url: 기본 URL (사용자 정의 엔드포인트용)
   :type base_url: str, optional

   **요청 설정:**

   :param temperature: 응답 창의성 (0.0-2.0)
   :type temperature: float
   :param max_tokens: 최대 토큰 수
   :type max_tokens: int
   :param timeout: 요청 타임아웃 (초)
   :type timeout: int

   **OCR 설정:**

   :param enable_ocr: OCR 기능 활성화
   :type enable_ocr: bool
   :param ocr_language: OCR 언어 설정
   :type ocr_language: str
   :param max_image_size: 최대 이미지 크기
   :type max_image_size: int

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import LLMConfig, LLMProvider

      # OpenAI 설정
      openai_config = LLMConfig(
          provider=LLMProvider.OPENAI,
          model="gpt-4o-mini",
          temperature=0.1,
          max_tokens=4096,
          enable_ocr=True,
          ocr_language="ko"
      )

      # Azure OpenAI 설정
      azure_config = LLMConfig(
          provider=LLMProvider.AZURE_OPENAI,
          model="gpt-4",
          base_url="https://your-resource.openai.azure.com/",
          api_version="2024-02-15-preview"
      )

TokenUsage (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.TokenUsage
   :members:
   :undoc-members:

   LLM API 토큰 사용량 정보를 저장하는 데이터클래스입니다.

   :param usage_type: 사용 유형
   :type usage_type: TokenUsageType
   :param prompt_tokens: 프롬프트 토큰 수
   :type prompt_tokens: int
   :param completion_tokens: 완료 토큰 수
   :type completion_tokens: int
   :param total_tokens: 전체 토큰 수
   :type total_tokens: int
   :param timestamp: 사용 시간
   :type timestamp: datetime

   **속성:**

   .. automethod:: cost_estimate
      :property:

      예상 비용을 USD로 계산합니다.

      :returns: 예상 비용 (USD)
      :rtype: float

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import TokenUsage, TokenUsageType

      usage = TokenUsage(
          usage_type=TokenUsageType.OCR,
          prompt_tokens=150,
          completion_tokens=500,
          total_tokens=650
      )

      print(f"예상 비용: ${usage.cost_estimate:.4f}")

LLMResponse (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.LLMResponse
   :members:
   :undoc-members:

   LLM API 응답을 저장하는 데이터클래스입니다.

   :param content: 응답 내용
   :type content: str
   :param usage: 토큰 사용량
   :type usage: TokenUsage
   :param model: 사용된 모델
   :type model: str
   :param provider: LLM 공급업체
   :type provider: LLMProvider
   :param success: 성공 여부
   :type success: bool
   :param error_message: 오류 메시지
   :type error_message: str, optional
   :param response_time: 응답 시간 (초)
   :type response_time: float

   **속성:**

   .. automethod:: is_success
      :property:

      응답 성공 여부를 반환합니다.

      :returns: 성공 시 True
      :rtype: bool

OCR 관련 모델
~~~~~~~~~~~~

OCRRequest (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.OCRRequest
   :members:
   :undoc-members:

   OCR 요청 정보를 저장하는 데이터클래스입니다.

   :param image_path: 이미지 파일 경로
   :type image_path: Path
   :param language: OCR 언어 설정
   :type language: str
   :param max_size: 최대 이미지 크기
   :type max_size: int
   :param prompt: 추가 프롬프트
   :type prompt: str, optional

   **속성:**

   .. automethod:: image_exists
      :property:

      이미지 파일 존재 여부를 확인합니다.

      :returns: 파일이 존재하면 True
      :rtype: bool

OCRResult (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.OCRResult
   :members:
   :undoc-members:

   OCR 처리 결과를 저장하는 데이터클래스입니다.

   :param text: 추출된 텍스트
   :type text: str
   :param confidence: 신뢰도 점수
   :type confidence: float
   :param language_detected: 감지된 언어
   :type language_detected: str, optional
   :param processing_time: 처리 시간
   :type processing_time: float
   :param token_usage: 토큰 사용량
   :type token_usage: TokenUsage, optional
   :param error_message: 오류 메시지
   :type error_message: str, optional

   **속성:**

   .. automethod:: is_success
      :property:

      OCR 성공 여부를 반환합니다.

      :returns: 성공 시 True
      :rtype: bool

통계 모델
~~~~~~~~

LLMStats (데이터클래스)
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: markitdown_gui.core.models.LLMStats
   :members:
   :undoc-members:

   LLM 사용 통계를 저장하는 데이터클래스입니다.

   :param total_requests: 전체 요청 수
   :type total_requests: int
   :param successful_requests: 성공한 요청 수
   :type successful_requests: int
   :param failed_requests: 실패한 요청 수
   :type failed_requests: int
   :param total_tokens_used: 사용된 총 토큰 수
   :type total_tokens_used: int
   :param total_cost_estimate: 총 예상 비용
   :type total_cost_estimate: float
   :param average_response_time: 평균 응답 시간
   :type average_response_time: float

   **속성:**

   .. automethod:: success_rate
      :property:

      성공률을 퍼센트로 반환합니다.

      :returns: 성공률 (0.0-100.0)
      :rtype: float

   **메서드:**

   .. automethod:: add_request

      새로운 요청 결과를 통계에 추가합니다.

      :param response: LLM 응답 객체
      :type response: LLMResponse

유틸리티 함수
-----------

.. autofunction:: markitdown_gui.core.models.get_file_type

   파일 경로로부터 파일 타입을 결정합니다.

   :param file_path: 파일 경로
   :type file_path: Path
   :returns: 파일 타입
   :rtype: FileType

   **예제:**

   .. code-block:: python

      from pathlib import Path
      from markitdown_gui.core.models import get_file_type, FileType

      # 파일 타입 확인
      file_type = get_file_type(Path("document.docx"))
      
      if file_type == FileType.DOCX:
          print("Word 문서입니다.")
      elif file_type == FileType.UNKNOWN:
          print("지원되지 않는 파일입니다.")

상수 및 매핑
-----------

FILE_TYPE_ICONS
~~~~~~~~~~~~~~~

.. autodata:: markitdown_gui.core.models.FILE_TYPE_ICONS

   파일 타입별 아이콘 파일명 매핑 딕셔너리입니다.

   **예제:**

   .. code-block:: python

      from markitdown_gui.core.models import FILE_TYPE_ICONS, FileType

      # 파일 타입별 아이콘 가져오기
      docx_icon = FILE_TYPE_ICONS[FileType.DOCX]  # "document.png"
      pdf_icon = FILE_TYPE_ICONS[FileType.PDF]    # "pdf.png"
      unknown_icon = FILE_TYPE_ICONS[FileType.UNKNOWN]  # "file.png"

사용 예제
--------

파일 정보 생성 및 관리
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pathlib import Path
   from datetime import datetime
   from markitdown_gui.core.models import (
       FileInfo, FileType, ConversionStatus, 
       ConversionResult, get_file_type
   )

   # 파일 정보 생성
   file_path = Path("/home/user/document.pdf")
   file_info = FileInfo(
       path=file_path,
       name=file_path.name,
       size=file_path.stat().st_size,
       modified_time=datetime.fromtimestamp(file_path.stat().st_mtime),
       file_type=get_file_type(file_path)
   )

   print(f"파일: {file_info.name}")
   print(f"크기: {file_info.size_formatted}")
   print(f"타입: {file_info.file_type.value}")

변환 결과 처리
~~~~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.models import ConversionResult, ConversionStatus

   # 변환 결과 생성
   result = ConversionResult(
       file_info=file_info,
       status=ConversionStatus.SUCCESS,
       output_path=Path("/output/document.md"),
       conversion_time=3.2,
       metadata={
           "pages": 15,
           "word_count": 2500,
           "images_extracted": 3
       }
   )

   # 결과 확인
   if result.is_success:
       print(f"변환 완료: {result.conversion_time_formatted}")
       print(f"출력 파일: {result.output_path}")
       print(f"페이지 수: {result.metadata['pages']}")

LLM 설정 및 사용량 추적
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.models import (
       LLMConfig, LLMProvider, TokenUsage, 
       TokenUsageType, LLMStats
   )

   # LLM 설정
   llm_config = LLMConfig(
       provider=LLMProvider.OPENAI,
       model="gpt-4o-mini",
       temperature=0.1,
       max_tokens=4096,
       enable_ocr=True
   )

   # 토큰 사용량 기록
   usage = TokenUsage(
       usage_type=TokenUsageType.OCR,
       prompt_tokens=200,
       completion_tokens=800,
       total_tokens=1000
   )

   # 통계 관리
   stats = LLMStats()
   response = LLMResponse(
       content="추출된 텍스트...",
       usage=usage,
       model="gpt-4o-mini",
       provider=LLMProvider.OPENAI,
       response_time=2.5
   )
   stats.add_request(response)

   print(f"성공률: {stats.success_rate:.1f}%")
   print(f"총 비용: ${stats.total_cost_estimate:.4f}")

배치 변환 진행률 추적
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.models import ConversionProgress

   # 진행률 객체 생성
   progress = ConversionProgress(
       total_files=20,
       completed_files=0
   )

   # 파일별 진행 상황 업데이트
   for i, file_name in enumerate(file_list):
       progress.current_file = file_name
       progress.current_status = f"변환 중: {file_name}"
       
       # 변환 작업 수행...
       
       progress.completed_files = i + 1
       print(f"진행률: {progress.progress_percent:.1f}%")
       
       if progress.is_complete:
           print("모든 파일 변환 완료!")
           break

설정 관리
~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.models import AppConfig
   from pathlib import Path

   # 설정 생성 및 수정
   config = AppConfig()
   
   # 기본 설정
   config.language = 'ko'
   config.theme = 'dark'
   config.output_directory = Path('/home/user/markdown')
   
   # 변환 설정
   config.max_concurrent_conversions = 5
   config.include_subdirectories = True
   config.max_file_size_mb = 200
   
   # LLM 설정
   config.llm_provider = 'openai'
   config.llm_model = 'gpt-4o-mini'
   config.enable_llm_ocr = True
   config.ocr_language = 'auto'
   
   # UI 설정
   config.window_width = 960
   config.window_height = 800
   config.recent_directories = [
       '/home/user/documents',
       '/home/user/downloads'
   ]

타입 검증 및 변환
~~~~~~~~~~~~~~~

.. code-block:: python

   from markitdown_gui.core.models import FileType, ConversionStatus
   from pathlib import Path

   def validate_file_for_conversion(file_path: Path) -> bool:
       """파일이 변환 가능한지 확인"""
       file_type = get_file_type(file_path)
       
       # 지원되는 파일 타입인지 확인
       if file_type == FileType.UNKNOWN:
           return False
       
       # 파일 크기 확인 (100MB 제한)
       if file_path.stat().st_size > 100 * 1024 * 1024:
           return False
           
       return True

   def get_status_message(status: ConversionStatus) -> str:
       """상태에 따른 메시지 반환"""
       messages = {
           ConversionStatus.PENDING: "변환 대기 중",
           ConversionStatus.IN_PROGRESS: "변환 진행 중",
           ConversionStatus.SUCCESS: "변환 완료",
           ConversionStatus.FAILED: "변환 실패",
           ConversionStatus.CANCELLED: "변환 취소됨"
       }
       return messages.get(status, "알 수 없는 상태")

관련 모듈
--------

* :doc:`config_manager` - 설정 관리 (AppConfig 사용)
* :doc:`file_manager` - 파일 관리 (FileInfo 사용)
* :doc:`conversion_manager` - 변환 관리 (ConversionResult 사용)
* :doc:`llm_manager` - LLM 관리 (LLMConfig, TokenUsage 사용)

.. seealso::

   * :doc:`../user-guide/configuration` - 설정 사용자 가이드
   * :doc:`../developer/data-models` - 개발자 데이터 모델 가이드