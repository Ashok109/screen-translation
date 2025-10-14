@echo off
setlocal

set VENV_DIR=.venv

REM Check if python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in PATH. Please install Python and add it to your PATH.
    pause
    exit /b 1
)

REM Check if the virtual environment directory exists
IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one in '%VENV_DIR%'...
    python -m venv %VENV_DIR%
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

REM Check if torch is already installed
pip show torch >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo PyTorch is already installed. Skipping installation.
) ELSE (
    echo PyTorch not found. Checking for NVIDIA GPU...
    
    REM Check for NVIDIA GPU by looking for nvidia-smi.exe in its default path
    IF EXIST "%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe" (
        echo NVIDIA GPU detected. Installing PyTorch with CUDA support...
        pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
    ) ELSE (
        echo No NVIDIA GPU detected. Installing CPU-only PyTorch...
        pip3 install torch torchvision
    )

    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install PyTorch.
        pause
        exit /b 1
    )
)

echo Installing or updating other required packages...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)

echo Starting the application...
python main.py

endlocal
pause
