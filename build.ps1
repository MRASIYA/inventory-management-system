# Flask Application Build Script for Windows
# Usage: .\build.ps1 [development|production|docker|clean]

param(
    [Parameter(Position=0)]
    [ValidateSet("development", "production", "docker", "clean", "")]
    [string]$Mode = "development"
)

$ErrorActionPreference = "Stop"

Write-Host "Flask Application Build Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Python not found. Please install Python 3.8 or later." -ForegroundColor Red
        return $false
    }
}

function Test-PipEnv {
    try {
        $pipVersion = pip --version 2>&1
        Write-Host "✓ Pip found: $pipVersion" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Pip not found. Please install pip." -ForegroundColor Red
        return $false
    }
}

function Install-Dependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✗ requirements.txt not found" -ForegroundColor Red
        exit 1
    }
}

function New-VirtualEnvironment {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "Virtual environment already exists" -ForegroundColor Yellow
    } else {
        python -m venv venv
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Virtual environment created" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
            exit 1
        }
    }
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    
    if ($env:VIRTUAL_ENV) {
        Write-Host "✓ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to activate virtual environment" -ForegroundColor Red
    }
}

function Initialize-Application {
    Write-Host "Initializing application..." -ForegroundColor Yellow
    
    # Create required directories
    $directories = @("backups", "static/css", "static/js", "static/images")
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✓ Created directory: $dir" -ForegroundColor Green
        }
    }
    
    # Create sample Excel file if it doesn't exist
    if (!(Test-Path "ISSUES.xlsx")) {
        Write-Host "Creating sample Excel file..." -ForegroundColor Yellow
        python -c "
import pandas as pd
sample_data = {
    'Materials': ['Material_001', 'Material_002', 'Material_003'],
    'Issued': [0, 0, 0],
    'Received': [100, 50, 75],
    'Return': [0, 0, 5]
}
df = pd.DataFrame(sample_data)
df.to_excel('ISSUES.xlsx', sheet_name='Sheet1', index=False)
print('Sample Excel file created')
"
    }
}

function Start-DevelopmentServer {
    Write-Host "Starting Flask development server..." -ForegroundColor Yellow
    Write-Host "Application will be available at: http://127.0.0.1:5000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
    Write-Host ""
    
    $env:FLASK_APP = "app.py"
    $env:FLASK_ENV = "development"
    $env:FLASK_DEBUG = "True"
    
    python app.py
}

function Start-ProductionServer {
    Write-Host "Starting Flask production server with Gunicorn..." -ForegroundColor Yellow
    Write-Host "Application will be available at: http://0.0.0.0:8000" -ForegroundColor Cyan
    Write-Host ""
    
    $env:FLASK_ENV = "production"
    $env:FLASK_DEBUG = "False"
    
    gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 30 app:app
}

function Build-DockerImage {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        docker build -t flask-inventory-app .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Docker image built successfully" -ForegroundColor Green
            Write-Host "To run the container: docker run -p 5000:5000 flask-inventory-app" -ForegroundColor Cyan
        } else {
            Write-Host "✗ Failed to build Docker image" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Docker not found. Please install Docker." -ForegroundColor Red
    }
}

function Remove-BuildArtifacts {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    
    $itemsToRemove = @(
        "venv",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "build",
        "dist",
        "*.egg-info"
    )
    
    foreach ($item in $itemsToRemove) {
        if (Test-Path $item) {
            Remove-Item -Path $item -Recurse -Force
            Write-Host "✓ Removed: $item" -ForegroundColor Green
        }
    }
}

function Show-Help {
    Write-Host "Flask Application Build Script" -ForegroundColor Green
    Write-Host "=============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\build.ps1 [mode]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Modes:" -ForegroundColor Yellow
    Write-Host "  development  - Set up development environment and start dev server (default)" -ForegroundColor White
    Write-Host "  production   - Set up production environment and start with Gunicorn" -ForegroundColor White
    Write-Host "  docker       - Build Docker image" -ForegroundColor White
    Write-Host "  clean        - Clean build artifacts and virtual environment" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1                 # Development mode" -ForegroundColor White
    Write-Host "  .\build.ps1 development     # Development mode" -ForegroundColor White
    Write-Host "  .\build.ps1 production      # Production mode" -ForegroundColor White
    Write-Host "  .\build.ps1 docker          # Build Docker image" -ForegroundColor White
    Write-Host "  .\build.ps1 clean           # Clean artifacts" -ForegroundColor White
}

# Main execution
switch ($Mode) {
    "development" {
        if (!(Test-Python) -or !(Test-PipEnv)) { exit 1 }
        New-VirtualEnvironment
        Install-Dependencies
        Initialize-Application
        Start-DevelopmentServer
    }
    "production" {
        if (!(Test-Python) -or !(Test-PipEnv)) { exit 1 }
        New-VirtualEnvironment
        Install-Dependencies
        Initialize-Application
        Start-ProductionServer
    }
    "docker" {
        Build-DockerImage
    }
    "clean" {
        Remove-BuildArtifacts
        Write-Host "✓ Clean completed" -ForegroundColor Green
    }
    "" {
        Show-Help
    }
}

Write-Host ""
Write-Host "Build script completed!" -ForegroundColor Green
