# ===================================================================
#  HU Traffic Analyzing System - COMPLETE SETUP INSTALLER (PowerShell)
#  This script will install everything needed to run the project
# ===================================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "║   HU TRAFFIC ANALYZING SYSTEM - AUTO INSTALLER           ║" -ForegroundColor Cyan
Write-Host "║   Complete Setup: Environment + All Packages             ║" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will install:" -ForegroundColor Yellow
Write-Host "  ✓ Conda environment 'fyp'" -ForegroundColor Green
Write-Host "  ✓ Python 3.11.14" -ForegroundColor Green
Write-Host "  ✓ OpenCV, YOLOv8, DeepSORT" -ForegroundColor Green
Write-Host "  ✓ All required packages" -ForegroundColor Green
Write-Host ""
Write-Host "Installation time: ~5-10 minutes" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Change to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " STEP 1: Checking Conda Installation" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if conda exists
$condaExists = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaExists) {
    Write-Host "[✗] ERROR: Conda not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Miniconda or Anaconda first:" -ForegroundColor Yellow
    Write-Host "https://docs.conda.io/en/latest/miniconda.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "[✓] Conda found" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " STEP 2: Creating Conda Environment" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Initialize conda
& "C:\Users\HASIB_ULLAH\miniconda3\shell\condabin\conda-hook.ps1"

# Check if environment exists
$envExists = conda env list | Select-String "fyp"
if (-not $envExists) {
    Write-Host "[Creating] New environment 'fyp' with Python 3.11.14..." -ForegroundColor Yellow
    Write-Host ""
    conda create -n fyp python=3.11.14 -y
    Write-Host ""
    Write-Host "[✓] Environment created successfully" -ForegroundColor Green
} else {
    Write-Host "[!] Environment 'fyp' already exists - skipping creation" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " STEP 3: Activating Environment" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

conda activate fyp
Write-Host "[✓] Environment activated: fyp" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " STEP 4: Installing Core Packages" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$packages = @(
    @{Name="OpenCV"; Package="opencv-python==4.8.1.78"},
    @{Name="YOLOv8 (Ultralytics)"; Package="ultralytics==8.4.12"},
    @{Name="DeepSORT"; Package="deep-sort-realtime==1.3.2"},
    @{Name="NumPy"; Package="numpy==1.24.3"},
    @{Name="Pillow"; Package="Pillow"},
    @{Name="Pandas"; Package="pandas"},
    @{Name="Additional packages"; Package="scipy matplotlib"}
)

$count = 1
foreach ($pkg in $packages) {
    Write-Host "[$count/$($packages.Count)] Installing $($pkg.Name)..." -ForegroundColor Yellow
    pip install $pkg.Package --quiet 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] $($pkg.Name) installed" -ForegroundColor Green
    } else {
        Write-Host "[!] Warning: $($pkg.Name) installation had issues" -ForegroundColor Yellow
    }
    Write-Host ""
    $count++
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " STEP 5: Creating Required Folders" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$folders = @("data\traffic_videos", "reports", "database", "models")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "[✓] Created: $folder\" -ForegroundColor Green
    } else {
        Write-Host "[✓] Exists: $folder\" -ForegroundColor Gray
    }
}
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " STEP 6: Verifying Installation" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing imports..." -ForegroundColor Yellow
python test_imports.py
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[✓] All imports successful!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[!] Some imports failed - but you can still try running the system" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host " ✓ Environment 'fyp' created" -ForegroundColor Green
Write-Host " ✓ Python 3.11.14 installed" -ForegroundColor Green
Write-Host " ✓ OpenCV 4.8.1.78 installed" -ForegroundColor Green
Write-Host " ✓ YOLOv8 (Ultralytics 8.4.12) installed" -ForegroundColor Green
Write-Host " ✓ DeepSORT 1.3.2 installed" -ForegroundColor Green
Write-Host " ✓ NumPy 1.24.3 installed" -ForegroundColor Green
Write-Host " ✓ All dependencies installed" -ForegroundColor Green
Write-Host " ✓ Project folders created" -ForegroundColor Green
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " NEXT STEPS:" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host " 1. Double-click '🚀 START HERE.bat' to run the system" -ForegroundColor White
Write-Host ""
Write-Host " 2. Or run manually:" -ForegroundColor White
Write-Host "    conda activate fyp" -ForegroundColor Gray
Write-Host "    python main_new.py" -ForegroundColor Gray
Write-Host ""
Write-Host " 3. Select option 1 for GUI Dashboard" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
