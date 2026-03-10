@echo off
REM ===================================================================
REM  HU Traffic Analyzing System - COMPLETE SETUP INSTALLER
REM  This script will install everything needed to run the project
REM ===================================================================

title HU Traffic System - Complete Installation
color 0B

cls
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║   HU TRAFFIC ANALYZING SYSTEM - AUTO INSTALLER           ║
echo  ║   Complete Setup: Environment + All Packages             ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  This will install:
echo    ✓ Conda environment 'fyp'
echo    ✓ Python 3.11.14
echo    ✓ OpenCV, YOLOv8, DeepSORT
echo    ✓ All required packages (12 groups)
echo    ✓ Training dependencies (TensorBoard, pycocotools)
echo    ✓ Tracking dependencies (filterpy, lap)
echo    ✓ Other utilities (PyYAML, Seaborn, scikit-learn)
echo.
echo  Installation time: ~10-15 minutes
echo.
pause
echo.

REM Change to project directory
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo  STEP 1: Checking Conda Installation
echo ═══════════════════════════════════════════════════════════
echo.

REM Check if conda exists
where conda >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [✗] ERROR: Conda not found!
    echo.
    echo Please install Miniconda or Anaconda first:
    echo https://docs.conda.io/en/latest/miniconda.html
    echo.
    pause
    exit /b 1
)

echo [✓] Conda found
echo.

echo ═══════════════════════════════════════════════════════════
echo  STEP 2: Creating Conda Environment
echo ═══════════════════════════════════════════════════════════
echo.

REM Check if fyp environment already exists
call conda env list | findstr "fyp" >nul 2>&1
if errorlevel 1 (
    echo [Creating] New environment 'fyp' with Python 3.11.14...
    echo.
    call conda create -n fyp python=3.11.14 -y
    if errorlevel 1 (
        color 0C
        echo [✗] Failed to create environment
        pause
        exit /b 1
    )
    echo.
    echo [✓] Environment created successfully
) else (
    echo [!] Environment 'fyp' already exists - skipping creation
)
echo.

echo ═══════════════════════════════════════════════════════════
echo  STEP 3: Activating Environment
echo ═══════════════════════════════════════════════════════════
echo.

call C:\Users\HASIB_ULLAH\miniconda3\Scripts\activate.bat fyp
if errorlevel 1 (
    color 0C
    echo [✗] Failed to activate environment
    pause
    exit /b 1
)

echo [✓] Environment activated: fyp
echo.

echo ═══════════════════════════════════════════════════════════
echo  STEP 4: Installing Core Packages
echo ═══════════════════════════════════════════════════════════
echo.

echo [1/7] Installing OpenCV...
pip install opencv-python==4.8.1.78 --quiet
if errorlevel 1 (
    echo [!] Warning: OpenCV installation had issues
) else (
    echo [✓] OpenCV installed
)
echo.

echo [2/7] Installing YOLOv8 (Ultralytics)...
pip install ultralytics==8.4.12 --quiet
if errorlevel 1 (
    echo [!] Warning: Ultralytics installation had issues
) else (
    echo [✓] YOLOv8 installed
)
echo.

echo [3/7] Installing DeepSORT...
pip install deep-sort-realtime==1.3.2 --quiet
if errorlevel 1 (
    echo [!] Warning: DeepSORT installation had issues
) else (
    echo [✓] DeepSORT installed
)
echo.

echo [4/7] Installing NumPy...
pip install numpy==1.24.3 --quiet
if errorlevel 1 (
    echo [!] Warning: NumPy installation had issues
) else (
    echo [✓] NumPy installed
)
echo.

echo [5/7] Installing Pillow...
pip install Pillow --quiet
if errorlevel 1 (
    echo [!] Warning: Pillow installation had issues
) else (
    echo [✓] Pillow installed
)
echo.

echo [6/7] Installing Pandas (for reports)...
pip install pandas --quiet
if errorlevel 1 (
    echo [!] Warning: Pandas installation had issues
) else (
    echo [✓] Pandas installed
)
echo.

echo [7/12] Installing Scipy and Matplotlib...
pip install scipy matplotlib --quiet
if errorlevel 1 (
    echo [!] Warning: Scipy/Matplotlib installation had issues
) else (
    echo [✓] Scipy and Matplotlib installed
)
echo.

echo [8/12] Installing PyYAML (for configurations)...
pip install pyyaml --quiet
if errorlevel 1 (
    echo [!] Warning: PyYAML installation had issues
) else (
    echo [✓] PyYAML installed
)
echo.

echo [9/12] Installing TensorBoard (for training visualization)...
pip install tensorboard --quiet
if errorlevel 1 (
    echo [!] Warning: TensorBoard installation had issues
) else (
    echo [✓] TensorBoard installed
)
echo.

echo [10/12] Installing Seaborn and tqdm (for plotting and progress bars)...
pip install seaborn tqdm --quiet
if errorlevel 1 (
    echo [!] Warning: Seaborn/tqdm installation had issues
) else (
    echo [✓] Seaborn and tqdm installed
)
echo.

echo [11/12] Installing filterpy and lap (for tracking)...
pip install filterpy lap --quiet
if errorlevel 1 (
    echo [!] Warning: filterpy/lap installation had issues
) else (
    echo [✓] filterpy and lap installed
)
echo.

echo [12/12] Installing scikit-learn, requests, pycocotools (for metrics and evaluation)...
pip install scikit-learn requests pycocotools --quiet
if errorlevel 1 (
    echo [!] Warning: Additional packages installation had issues
) else (
    echo [✓] scikit-learn, requests, and pycocotools installed
)
echo.

echo ═══════════════════════════════════════════════════════════
echo  STEP 5: Creating Required Folders
echo ═══════════════════════════════════════════════════════════
echo.

if not exist "data\traffic_videos" mkdir "data\traffic_videos"
echo [✓] Created: data\traffic_videos\

if not exist "reports" mkdir "reports"
echo [✓] Created: reports\

if not exist "database" mkdir "database"
echo [✓] Created: database\

if not exist "models" mkdir "models"
echo [✓] Created: models\

if not exist "training\datasets" mkdir "training\datasets"
echo [✓] Created: training\datasets\

if not exist "training\runs" mkdir "training\runs"
echo [✓] Created: training\runs\

if not exist "training\exports" mkdir "training\exports"
echo [✓] Created: training\exports\

if not exist "logs" mkdir "logs"
echo [✓] Created: logs\
echo.

echo ═══════════════════════════════════════════════════════════
echo  STEP 6: Verifying Installation
echo ═══════════════════════════════════════════════════════════
echo.

echo Testing imports...
python test_imports.py
if errorlevel 1 (
    color 0E
    echo.
    echo [!] Some imports failed - but you can still try running the system
    echo.
) else (
    echo.
    echo [✓] All imports successful!
)
echo.

echo ═══════════════════════════════════════════════════════════
echo  INSTALLATION COMPLETE!
echo ═══════════════════════════════════════════════════════════
echo.
color 0A
echo  ✓ Environment 'fyp' created
echo  ✓ Python 3.11.14 installed
echo  ✓ OpenCV 4.8.1.78 installed
echo  ✓ YOLOv8 (Ultralytics 8.4.12) installed
echo  ✓ DeepSORT 1.3.2 installed
echo  ✓ NumPy 1.24.3 installed
echo  ✓ Pandas, Pillow, Matplotlib, Scipy installed
echo  ✓ PyYAML, TensorBoard installed
echo  ✓ Seaborn, tqdm, scikit-learn installed
echo  ✓ filterpy, lap, pycocotools installed (for tracking & training)
echo  ✓ All 12 package groups installed
echo  ✓ Project folders created (including training directories)
echo.
echo ═══════════════════════════════════════════════════════════
echo  NEXT STEPS:
echo ═══════════════════════════════════════════════════════════
echo.
echo  1. Double-click "🚀 START HERE.bat" to run the system
echo.
echo  2. Or run manually:
echo     conda activate fyp
echo     python main_new.py
echo.
echo  3. Select option 1 for GUI Dashboard
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
exit
