# 📥 MarkItDown GUI 설치 가이드

> 이 문서는 컴퓨터 초보자도 쉽게 따라할 수 있도록 작성된 상세 설치 안내서입니다.

## 목차
- [설치 전 확인사항](#설치-전-확인사항)
- [방법 1: 실행파일로 설치 (가장 쉬움)](#방법-1-실행파일로-설치-가장-쉬움)
- [방법 2: Python으로 설치](#방법-2-python으로-설치)
- [설치 확인하기](#설치-확인하기)
- [자주 발생하는 문제 해결](#자주-발생하는-문제-해결)

---

## 설치 전 확인사항

### 💻 컴퓨터 사양 확인
- **운영체제**: Windows 10 이상 (Windows 11 권장)
- **메모리**: 최소 4GB (8GB 권장)
- **저장공간**: 최소 2GB 여유 공간
- **인터넷**: 초기 설치 시 필요

### 확인 방법
1. **내 컴퓨터** 아이콘에서 마우스 오른쪽 클릭
2. **속성** 선택
3. 시스템 정보에서 Windows 버전과 RAM 확인

---

## 방법 1: 실행파일로 설치 (가장 쉬움)

> 💡 **추천!** 개발 지식이 없어도 쉽게 설치할 수 있습니다.

### 📌 Step 1: 실행파일 다운로드

1. 웹 브라우저를 열고 GitHub 릴리즈 페이지 접속
   ```
   https://github.com/[사용자명]/MarkItDownGUI/releases
   ```

2. 최신 버전의 **MarkItDown_GUI_Complete.exe** 클릭하여 다운로드
   - 파일 크기: 약 100-150MB
   - 다운로드 위치: 보통 `다운로드` 폴더

### 📌 Step 2: 프로그램 설치

1. 다운로드한 **MarkItDown_GUI_Complete.exe** 파일을 더블클릭

2. Windows 보안 경고가 나타나면:
   - "추가 정보" 클릭
   - "실행" 버튼 클릭
   
   > ⚠️ 이 경고는 정상적인 현상입니다. 프로그램이 Microsoft 인증을 받지 않아서 나타납니다.

3. 프로그램이 자동으로 실행됩니다

### 📌 Step 3: 바탕화면 바로가기 만들기

1. 실행파일을 원하는 폴더로 이동 (예: `C:\Program Files\MarkItDown`)
2. 파일에서 마우스 오른쪽 클릭
3. "바로 가기 만들기" 선택
4. 생성된 바로가기를 바탕화면으로 이동

---

## 방법 2: Python으로 설치

> 더 많은 기능과 최신 업데이트를 원하시는 분들을 위한 방법입니다.

### 📌 Step 1: Python 설치

#### 1.1 Python 다운로드
1. Python 공식 웹사이트 접속: https://www.python.org
2. "Downloads" 메뉴에서 **Python 3.12** 다운로드
3. **중요!** 설치 시작 화면에서 반드시 체크:
   - ✅ "Add Python to PATH" 

#### 1.2 Python 설치 확인
1. **시작** 메뉴에서 "명령 프롬프트" 또는 "cmd" 검색
2. 검은 창이 열리면 다음 입력:
   ```
   python --version
   ```
3. `Python 3.12.x`가 표시되면 성공!

### 📌 Step 2: MarkItDown GUI 다운로드

#### 2.1 ZIP 파일로 다운로드 (쉬운 방법)
1. GitHub 페이지 접속
2. 초록색 **Code** 버튼 클릭
3. **Download ZIP** 선택
4. 다운로드한 ZIP 파일을 원하는 위치에 압축 해제
   - 추천 위치: `C:\MarkItDownGUI`

#### 2.2 Git으로 다운로드 (선택사항)
```cmd
git clone https://github.com/[사용자명]/MarkItDownGUI.git
cd MarkItDownGUI
```

### 📌 Step 3: 프로그램 설치

1. **명령 프롬프트** 열기 (관리자 권한 추천)

2. MarkItDown 폴더로 이동:
   ```cmd
   cd C:\MarkItDownGUI\MarkItDownGUI
   ```

3. 가상환경 생성:
   ```cmd
   python -m venv venv
   ```

4. 가상환경 활성화:
   ```cmd
   venv\Scripts\activate
   ```
   > 성공하면 명령줄 앞에 `(venv)`가 표시됩니다

5. 필요한 프로그램 설치:
   ```cmd
   pip install -r requirements.txt
   ```
   > 이 과정은 5-10분 정도 걸립니다. 커피 한 잔 하고 오세요! ☕

### 📌 Step 4: PDF 지원 추가 설치 (선택사항)

PDF 파일을 더 잘 변환하려면:
```cmd
python install_pdf_dependencies.py
```

---

## 설치 확인하기

### 방법 1 사용자 (실행파일)
1. 설치한 **MarkItDown_GUI_Complete.exe** 더블클릭
2. 프로그램 창이 열리면 성공!

### 방법 2 사용자 (Python)
1. 명령 프롬프트에서:
   ```cmd
   cd C:\MarkItDownGUI\MarkItDownGUI
   venv\Scripts\activate
   python main.py
   ```
2. 프로그램 창이 열리면 성공!

---

## 자주 발생하는 문제 해결

### ❌ "python이 내부 또는 외부 명령... 아닙니다"
- **원인**: Python이 설치되지 않았거나 PATH에 추가되지 않음
- **해결**: 
  1. Python 재설치
  2. 설치 시 "Add Python to PATH" 체크 확인

### ❌ "pip가 인식되지 않습니다"
- **원인**: pip가 설치되지 않음
- **해결**:
  ```cmd
  python -m ensurepip --upgrade
  ```

### ❌ "PyQt6 설치 실패"
- **원인**: Visual C++ 재배포 가능 패키지 부재
- **해결**: 
  1. Microsoft Visual C++ 재배포 가능 패키지 설치
  2. https://aka.ms/vs/17/release/vc_redist.x64.exe 다운로드 및 설치

### ❌ 프로그램이 시작되지 않음
- **원인**: 의존성 패키지 누락
- **해결**:
  ```cmd
  pip install --upgrade pip
  pip install -r requirements.txt --force-reinstall
  ```

### ❌ "NO_PDF_LIBRARY" 경고
- **원인**: PDF 처리 라이브러리 미설치
- **해결**:
  ```cmd
  pip install pdfplumber PyPDF2
  ```

---

## 🎉 설치 완료!

축하합니다! MarkItDown GUI가 성공적으로 설치되었습니다.

### 다음 단계
- 📖 [사용 설명서](USER_MANUAL_KR.md)를 읽고 프로그램 사용법을 익혀보세요
- 🚀 [빠른 시작 가이드](QUICK_START_KR.md)로 바로 시작해보세요

### 도움이 필요하신가요?
- 📧 이메일: support@markitdown.com
- 💬 GitHub Issues: [문제 신고하기](https://github.com/[사용자명]/MarkItDownGUI/issues)

---

*이 문서는 일반 사용자를 위해 쉽게 작성되었습니다. 개발자를 위한 고급 설치 옵션은 [개발자 문서](../README.md)를 참조하세요.*