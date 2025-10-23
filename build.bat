@echo off
setlocal

set VENV_DIR=.venv

REM Check if the virtual environment directory exists
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Please run 'run.bat' or 'run.ps1' at least once to create it.
    pause
    exit /b 1
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo Installing/updating build dependencies...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Building executable with PyInstaller...
pyinstaller build.spec
IF %ERRORLEVEL% NEQ 0 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete! The executable can be found in the 'dist' folder.
pause
endlocal
