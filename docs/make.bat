@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help
if "%1" == "help" goto help
if "%1" == "clean" goto clean
if "%1" == "html" goto html
if "%1" == "livehtml" goto livehtml
if "%1" == "apidoc" goto apidoc
if "%1" == "fullbuild" goto fullbuild
if "%1" == "install-deps" goto install-deps

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
echo.
echo.Custom targets for MarkItDown GUI documentation:
echo.  install-deps  Install documentation dependencies
echo.  clean         Clean build directory
echo.  html          Build HTML documentation
echo.  livehtml      Build HTML with auto-reload
echo.  apidoc        Generate API documentation
echo.  fullbuild     Full rebuild including API docs
goto end

:install-deps
echo Installing documentation dependencies...
pip install -r requirements-docs.txt
goto end

:clean
echo Cleaning build directory...
if exist "%BUILDDIR%" rmdir /s /q "%BUILDDIR%"
if exist "autoapi\generated" rmdir /s /q "autoapi\generated"
for /r %%i in (*.pyc) do del "%%i"
for /d /r %%i in (__pycache__) do rmdir /s /q "%%i"
goto end

:html
echo Building HTML documentation...
%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%\html %SPHINXOPTS% %O%
echo.
echo Build finished. The HTML pages are in %BUILDDIR%\html.
goto end

:livehtml
echo Starting live HTML build...
sphinx-autobuild -b html %SOURCEDIR% %BUILDDIR%\html --host 0.0.0.0 --port 8000
goto end

:apidoc
echo Generating API documentation...
sphinx-apidoc -f -o autoapi\generated ..\markitdown_gui
echo API documentation generated.
goto end

:fullbuild
echo Starting full documentation build...
call :clean
call :apidoc
call :html
echo Full documentation build completed.
goto end

:end
popd