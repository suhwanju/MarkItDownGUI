설치 가이드
===========

.. include:: ../../README.md
   :parser: myst_parser.sphinx_

시스템 요구사항
--------------

* Python 3.8 이상
* PyQt6 6.5.0 이상
* 최소 4GB RAM
* 1GB 디스크 공간

설치 방법
--------

pip를 통한 설치
~~~~~~~~~~~~~~

.. code-block:: bash

   pip install markitdown-gui

소스코드를 통한 설치
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/your-repo/markitdown-gui.git
   cd markitdown-gui
   pip install -r requirements.txt
   python main.py

의존성 설치
----------

필수 의존성
~~~~~~~~~~

.. code-block:: bash

   pip install PyQt6 markitdown requests

선택적 의존성
~~~~~~~~~~~

.. code-block:: bash

   # 추가 파일 형식 지원을 위해
   pip install python-docx python-pptx Pillow

설치 확인
--------

설치가 완료되면 다음 명령어로 확인할 수 있습니다:

.. code-block:: bash

   python -c "import markitdown_gui; print('설치 완료!')"

문제 해결
--------

일반적인 설치 문제와 해결 방법:

PyQt6 설치 오류
~~~~~~~~~~~~~~

.. code-block:: bash

   # Ubuntu/Debian
   sudo apt-get install python3-pyqt6
   
   # macOS
   brew install pyqt6
   
   # Windows
   pip install --upgrade pip
   pip install PyQt6

권한 오류
~~~~~~~~

.. code-block:: bash

   # 사용자 디렉토리에 설치
   pip install --user markitdown-gui