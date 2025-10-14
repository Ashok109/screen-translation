# PowerShell script to set up the environment and run the application

$VenvDir = ".venv"

# Check if Python is available
try {
    python --version | Out-Null
}
catch {
    Write-Host "Python is not found in PATH. Please install Python and add it to your PATH."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the virtual environment directory exists
if (-not (Test-Path -Path "$VenvDir\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating one in '$VenvDir'..."
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "Activating virtual environment..."
& "$VenvDir\Scripts\Activate.ps1"

# Check if torch is already installed
$torchCheck = pip show torch
if ($torchCheck) {
    Write-Host "PyTorch is already installed. Skipping installation."
}
else {
    Write-Host "PyTorch not found. Checking for NVIDIA GPU..."
    
    # Check for NVIDIA GPU using Get-Command
    $nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($nvidiaSmi) {
        Write-Host "NVIDIA GPU detected. Installing PyTorch with CUDA support..."
        pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126
    }
    else {
        Write-Host "No NVIDIA GPU detected. Installing CPU-only PyTorch..."
        pip3 install torch torchvision
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyTorch."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "Installing or updating other required packages..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies from requirements.txt."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting the application..."
python main.py

Write-Host "Application finished."
Read-Host "Press Enter to exit"
