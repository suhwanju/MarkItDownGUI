# MarkItDown GUI 실행파일 빌드 가이드

## 개요
이 문서는 MarkItDown GUI 애플리케이션을 Windows 실행파일(.exe)로 빌드하는 과정을 설명합니다.

## 필수 환경

### 시스템 요구사항
- Windows 10/11
- Python 3.10+ 
- 최소 4GB RAM (빌드 과정에서 메모리 사용량 높음)
- 최소 2GB 디스크 공간

### 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 기본 의존성 설치
pip install -r requirements.txt
```

## 의존성 설치

### 1. 기본 의존성
```bash
pip install PyQt6 pyinstaller psutil keyring
```

### 2. MarkItDown 완전 설치 (모든 포맷 지원)
```bash
# 기존 markitdown 제거 (있는 경우)
pip uninstall markitdown -y

# 모든 포맷 지원 포함 설치
pip install markitdown python-pptx pdfminer-six
```

### 3. 추가 의존성 (필요시)
```bash
pip install aiohttp magika beautifulsoup4 requests
```

## 실행파일 빌드 과정

### 1. 기본 빌드 명령어
```bash
venv/Scripts/pyinstaller.exe --onefile --windowed --name="MarkItDown_GUI" main.py
```

### 2. 완전 기능 빌드 (권장)
```bash
venv/Scripts/pyinstaller.exe \
  --onefile \
  --windowed \
  --name="MarkItDown_GUI_Complete" \
  --collect-all markitdown \
  --collect-all magika \
  --add-data "venv/Lib/site-packages/magika/models;magika/models" \
  --hidden-import=markitdown \
  --hidden-import=magika \
  --hidden-import=pptx \
  --hidden-import=pdfminer.six \
  --hidden-import=cryptography \
  --hidden-import=keyring \
  --hidden-import=psutil \
  --exclude-module=markdown \
  main.py
```

### 3. 디버그 버전 빌드
```bash
venv/Scripts/pyinstaller.exe \
  --onefile \
  --console \
  --name="MarkItDown_GUI_Debug" \
  --collect-all markitdown \
  --collect-all magika \
  --add-data "venv/Lib/site-packages/magika/models;magika/models" \
  --hidden-import=markitdown \
  --hidden-import=magika \
  --hidden-import=pptx \
  --hidden-import=pdfminer.six \
  --hidden-import=cryptography \
  --exclude-module=markdown \
  main.py
```

## 빌드 매개변수 설명

### 기본 매개변수
- `--onefile`: 단일 실행파일로 빌드
- `--windowed`: 콘솔 창 숨김 (GUI 앱용)
- `--console`: 콘솔 창 표시 (디버그용)
- `--name`: 출력 파일명

### 의존성 포함
- `--collect-all markitdown`: MarkItDown 라이브러리 전체 포함
- `--collect-all magika`: 파일 타입 감지 라이브러리 포함
- `--add-data`: 데이터 파일 추가 (magika 모델 파일들)
- `--hidden-import`: 숨겨진 import 명시적 포함

### 제외 모듈
- `--exclude-module=markdown`: 충돌 방지를 위해 markdown 모듈 제외

## 지원 파일 형식

빌드된 실행파일은 다음 형식을 지원합니다:

### 기본 지원
- **.txt** - 텍스트 파일
- **.md** - 마크다운 파일
- **.html** - HTML 파일
- **.xml** - XML 파일

### PDF/Office 지원 (python-pptx, pdfminer-six 포함)
- **.pdf** - PDF 문서
- **.pptx** - PowerPoint 프레젠테이션
- **.docx** - Word 문서 (mammoth 포함시)
- **.xlsx** - Excel 스프레드시트 (openpyxl 포함시)

### 이미지/멀티미디어 (추가 의존성 필요)
- **.png, .jpg, .jpeg** - 이미지 파일
- **.mp3, .wav** - 오디오 파일 (speechrecognition 포함시)

## 빌드 문제 해결

### 1. 메모리 부족 오류
```bash
# Windows 가상 메모리 증가 또는
# 더 적은 의존성으로 빌드
venv/Scripts/pyinstaller.exe --onefile --windowed --name="MarkItDown_GUI_Minimal" \
  --hidden-import=markitdown \
  --hidden-import=magika \
  --exclude-module=markdown \
  main.py
```

### 2. 의존성 누락 오류
실행 중 "Module not found" 오류 발생시:
```bash
# 누락된 모듈을 명시적으로 포함
--hidden-import=[모듈명]
```

### 3. 파일 변환 실패
특정 파일 형식 변환 실패시:
```bash
# 해당 형식의 의존성 확인 및 설치
pip install [필요한 라이브러리]
# 빌드 명령어에 --hidden-import 추가
```

### 4. Magika 모델 파일 오류
"model dir not found" 오류 발생시:
```bash
# magika 모델 파일 경로 확인
--add-data "venv/Lib/site-packages/magika/models;magika/models"
```

## 빌드 결과 검증

### 1. 기본 실행 테스트
```bash
# 실행파일 실행 (5초 후 종료)
timeout 5 ./dist/MarkItDown_GUI_Complete.exe
echo "실행 성공"
```

### 2. 의존성 테스트 스크립트
```python
# test_deps.py
from markitdown import MarkItDown
import pptx
import pdfminer
print("모든 의존성 정상 로드")
```

### 3. 변환 기능 테스트
- 샘플 PDF, PPTX 파일로 변환 테스트
- 에러 로그 확인 (error.log 파일)

## 빌드 시간 및 크기

### 예상 빌드 시간
- **기본 빌드**: 2-5분
- **완전 빌드**: 5-15분 (의존성에 따라)
- **디버그 빌드**: 3-8분

### 예상 파일 크기
- **기본 빌드**: 60-80MB
- **완전 빌드**: 100-150MB
- **디버그 빌드**: 비슷 (콘솔 창만 차이)

## 배포 준비

### 1. 최종 테스트
- [ ] 다양한 파일 형식 변환 테스트
- [ ] 다른 Windows 시스템에서 실행 테스트
- [ ] 의존성 없는 환경에서 실행 테스트

### 2. 배포 패키지 구성
```
MarkItDown_GUI_Release/
├── MarkItDown_GUI_Complete.exe    # 메인 실행파일
├── README.txt                     # 사용법 안내
├── LICENSE                        # 라이선스 파일
└── samples/                       # 샘플 파일들
    ├── sample.pdf
    ├── sample.pptx
    └── sample.docx
```

### 3. 사용자 안내사항
- Windows Defender 예외 설정 필요할 수 있음
- 첫 실행시 시간이 걸릴 수 있음
- 임시 폴더에 파일 압축 해제 과정 있음

## 자동화 스크립트

### 빌드 자동화 스크립트 (build.bat)
```batch
@echo off
echo MarkItDown GUI 빌드 시작...

echo 의존성 확인 중...
venv\Scripts\pip.exe install markitdown python-pptx pdfminer-six

echo 빌드 중... (5-15분 소요)
venv\Scripts\pyinstaller.exe --onefile --windowed --name="MarkItDown_GUI_Complete" --collect-all markitdown --collect-all magika --add-data "venv/Lib/site-packages/magika/models;magika/models" --hidden-import=markitdown --hidden-import=magika --hidden-import=pptx --hidden-import=pdfminer.six --hidden-import=cryptography --exclude-module=markdown main.py

if exist dist\MarkItDown_GUI_Complete.exe (
    echo 빌드 성공! 파일 위치: dist\MarkItDown_GUI_Complete.exe
) else (
    echo 빌드 실패. 로그를 확인하세요.
)

pause
```

## 참고사항

### 라이선스 및 의존성
- PyQt6: GPL v3 / Commercial
- MarkItDown: MIT
- PyInstaller: GPL v2 / Commercial

### 성능 최적화
- UPX를 사용한 실행파일 압축 가능 (선택사항)
- 불필요한 의존성 제거로 크기 감소 가능
- 가상환경을 깨끗하게 유지하여 빌드 시간 단축

### 보안 고려사항
- 코드 서명 인증서 적용 권장
- 바이러스 백신 오탐지 대비 필요
- 실행파일 무결성 검증 제공 권장

---

## 버전 기록

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0 | 2025-09-14 | 초기 빌드 가이드 작성 |
| 1.1 | 2025-09-14 | PDF/PPTX 의존성 추가, magika 모델 포함 |

## 문의 및 지원

빌드 과정에서 문제 발생시 error.log 파일과 함께 문의해 주세요.