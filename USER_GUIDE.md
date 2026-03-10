# 📚 USER GUIDE
## HU Traffic Analyzing and Vehicle Counting System

**Complete Step-by-Step Instructions**

---

## Table of Contents
1. [First Time Setup](#first-time-setup)
2. [Starting the System](#starting-the-system)
3. [Using GUI Dashboard](#using-gui-dashboard)
4. [Console Mode](#console-mode)
5. [Generating Reports](#generating-reports)
6. [Managing Data](#managing-data)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Best Practices](#tips--best-practices)

---

## 1. First Time Setup

### Step 1.1: Open Anaconda Prompt
- Search for "Anaconda Prompt" in Windows Start Menu
- Right-click → Run as Administrator (optional but recommended)

### Step 1.2: Activate Environment
```bash
conda activate fyp
```
You should see `(fyp)` appear at the beginning of your command line.

### Step 1.3: Navigate to Project Folder
```bash
cd "C:\Users\HASIB_ULLAH\Documents\HU Traffic Analyzing and Vehicle Counting System in Real-Time with Smart Parking and Vehicle Rental Management"
```

### Step 1.4: Verify Installation
```bash
python test_imports.py
```

**Expected Output:**
```
Testing imports...
--------------------------------------------------
✓ PreProcessor imported
✓ ReportGenerator imported
✓ VehicleDetector imported
✓ VehicleTracker imported
✓ VehicleCounter imported
✓ ParkingManager imported
✓ RentalManager imported
✓ CSVDatabase imported
✓ ModernDashboard imported
--------------------------------------------------
✓ All imports successful!
```

If you see any ✗ marks, refer to the [Troubleshooting](#troubleshooting) section.

---

## 2. Starting the System

### Option A: Using Command Line

1. **Open Anaconda Prompt**
2. **Activate Environment**:
   ```bash
   conda activate fyp
   ```
3. **Navigate to Project**:
   ```bash
   cd "C:\Users\HASIB_ULLAH\Documents\HU Traffic Analyzing and Vehicle Counting System in Real-Time with Smart Parking and Vehicle Rental Management"
   ```
4. **Run Main Script**:
   ```bash
   python main_new.py
   ```

### Option B: Using VS Code

1. Open VS Code
2. Open the project folder
3. Select Python interpreter: `fyp` environment
4. Open `main_new.py`
5. Click the ▶ Run button (top right)

### Mode Selection Screen

You will see:
```
============================================================
               WELCOME TO
     HU TRAFFIC ANALYZING & VEHICLE COUNTING SYSTEM
          with Smart Parking & Rental Management
============================================================

Select mode:
1. GUI Dashboard (Recommended)
2. Console Mode
3. Use Video File

Enter choice (1-3):
```

**Choose:**
- **1** for GUI Dashboard (Best for most users)
- **2** for Console Mode (Lightweight, no GUI)
- **3** to process a specific video file

---

## 3. Using GUI Dashboard

### 3.1 Starting GUI Mode

1. Enter `1` when prompted
2. Wait for GUI to load (5-10 seconds)
3. Main dashboard window will appear

### 3.2 Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  HU TRAFFIC ANALYZING SYSTEM                        [X] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Video Feed - 800x600px]                              │
│                                                         │
├──────────────┬──────────────┬──────────────┬───────────┤
│ 🚗 Cars: 0   │ 🏍️ Bikes: 0  │ 🚌 Buses: 0  │ 🚚 Trucks: 0 │
├──────────────┴──────────────┴──────────────┴───────────┤
│ 🅿️ Parking: 100 Available | 0 Occupied                │
├─────────────────────────────────────────────────────────┤
│ 💰 Recent Transactions:                                │
│  Type     | Fee    | Discount | Total                  │
│  ───────────────────────────────────────               │
│                                                         │
└─────────────────────────────────────────────────────────┘
│ ▶ Start | ⏸ Stop | 📹 Upload | 📷 Webcam | 📊 Reports │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Control Buttons

#### ▶ Start Button
- **Function**: Begin video processing
- **Steps**:
  1. Click "▶ Start"
  2. System initializes camera/video
  3. Video feed appears in main window
  4. Vehicle detection begins automatically

#### ⏸ Stop Button
- **Function**: Pause video processing
- **Steps**:
  1. Click "⏸ Stop"
  2. Processing pauses
  3. Last frame remains displayed
  4. Statistics preserved

#### 📹 Upload Button
- **Function**: Select video file
- **Steps**:
  1. Click "📹 Upload"
  2. File dialog opens
  3. Select .mp4, .avi, or .mov file
  4. Click "▶ Start" to begin processing

**Supported Formats:**
- MP4 (Recommended)
- AVI
- MOV
- MKV

#### 📷 Webcam Button
- **Function**: Switch to webcam input
- **Steps**:
  1. Click "📷 Webcam"
  2. System switches to camera 0
  3. Click "▶ Start" to begin
  4. If camera 0 doesn't work, edit `config.py` and change `VIDEO_SOURCE` to 1 or 2

#### 📊 Reports Button
- **Function**: Generate analytics reports
- **Details**: See [Section 5](#5-generating-reports)

### 3.4 Statistics Display

#### Vehicle Count Cards
- **Location**: Top row, 4 colored cards
- **Information**:
  - 🚗 **Cars** (Blue) - Total cars detected
  - 🏍️ **Bikes** (Green) - Total motorcycles detected
  - 🚌 **Buses** (Purple) - Total buses detected
  - 🚚 **Trucks** (Orange) - Total trucks detected

Updates in real-time as vehicles cross the counting line.

#### Parking Status
- **Location**: Below vehicle cards
- **Information**:
  - Available slots
  - Occupied slots
  - Total capacity (100)
  - Occupancy percentage

#### Revenue Table
- **Location**: Bottom section
- **Columns**:
  - Vehicle Type
  - Base Fee (PKR)
  - Discount Applied (PKR)
  - Final Fee (PKR)
  - Timestamp

Shows last 10 transactions by default.

#### FPS Counter
- **Location**: Bottom right corner
- **Purpose**: Shows system performance
- **Good Performance**: 25-60 FPS
- **Low Performance**: < 20 FPS (see optimization tips)

---

## 4. Console Mode

### 4.1 Starting Console Mode

1. Run `python main_new.py`
2. Enter `2` when prompted
3. OpenCV window will appear

### 4.2 Console Window Controls

- **q** - Quit the application
- **s** - Print statistics to console
- **ESC** - Exit the application

### 4.3 Console Display

The OpenCV window shows:
- Live video feed
- Bounding boxes around detected vehicles
- Unique IDs above each vehicle
- Counting line (red horizontal line)
- Count overlay (top-left corner)

### 4.4 Console Output

Terminal displays:
```
============================================================
          HU TRAFFIC ANALYZING SYSTEM
      Real-Time Vehicle Counting & Management
============================================================

Initializing components...
✓ All components initialized!
✓ Video source opened: 0

✓ Console mode
Press 'q' to quit, 's' for stats
```

Press 's' to see:
```
Stats: {'total': 15, 'car': 8, 'motorcycle': 5, 'bus': 1, 'truck': 1}
```

---

## 5. Generating Reports

### 5.1 Using Reports Button (GUI)

1. **Click** the "📊 Reports" button in navigation bar
2. **Wait** for processing (2-5 seconds)
3. **Success Dialog** appears showing:
   ```
   Reports Generated
   
   All reports generated successfully!
   
   ✓ Vehicle Count
   ✓ Parking Usage
   ✓ Daily Revenue
   ✓ Overall Statistics
   
   Location: reports/
   ```
4. **Click "OK"** to close dialog

### 5.2 Report Locations

All reports saved to:
```
reports/
├── vehicle_count_20240115.txt
├── parking_usage_20240115.txt
├── daily_revenue_20240115.txt
└── overall_statistics_20240115.txt
```

Date format: YYYYMMDD

### 5.3 Report Contents

#### Vehicle Count Report
```
========================================
     VEHICLE COUNT REPORT
     Date: 2024-01-15
========================================

Total Vehicles Counted: 45

Breakdown by Type:
------------------
Cars:       25 (55.56%)
Motorcycles: 12 (26.67%)
Buses:       5 (11.11%)
Trucks:      3 (6.67%)

Generated: 2024-01-15 14:30:45
```

#### Parking Usage Report
```
========================================
     PARKING USAGE REPORT
     Date: 2024-01-15
========================================

Total Entries: 45
Total Exits: 38
Current Occupancy: 7 vehicles

Occupancy Rate: 7.00%
Available Slots: 93

Peak Hours:
-----------
10:00 AM - 12:00 PM: 15 entries
2:00 PM - 4:00 PM: 12 entries

Generated: 2024-01-15 14:30:45
```

#### Daily Revenue Report
```
========================================
     DAILY REVENUE REPORT
     Date: 2024-01-15
========================================

Revenue by Vehicle Type:
------------------------
Cars:       25 × 200 PKR = 5,000 PKR
Motorcycles: 12 × 100 PKR = 1,200 PKR
Buses:       5 × 400 PKR = 2,000 PKR
Trucks:      3 × 500 PKR = 1,500 PKR

Gross Revenue: 9,700 PKR
Discounts:     970 PKR (10%)
Net Revenue:   8,730 PKR

Transaction Count: 45
Average per Vehicle: 194 PKR

Generated: 2024-01-15 14:30:45
```

#### Overall Statistics Report
```
========================================
  OVERALL TRAFFIC STATISTICS
========================================

Cumulative Statistics (All Time):
----------------------------------
Total Vehicles Tracked: 1,234
Total Revenue: 245,600 PKR

Vehicle Type Distribution:
--------------------------
Cars:       650 (52.68%)
Motorcycles: 384 (31.12%)
Buses:       125 (10.13%)
Trucks:      75 (6.08%)

Parking Statistics:
-------------------
Total Parking Events: 1,234
Average Occupancy: 15 vehicles
Peak Occupancy: 45 vehicles
Utilization Rate: 45%

Revenue Statistics:
-------------------
Average Daily Revenue: 8,520 PKR
Highest Daily Revenue: 12,450 PKR
Lowest Daily Revenue: 3,200 PKR

Generated: 2024-01-15 14:30:45
```

### 5.4 Opening Reports

**Method 1: File Explorer**
1. Navigate to project folder
2. Open `reports/` folder
3. Double-click any `.txt` file
4. Opens in Notepad

**Method 2: Command Line**
```bash
cd reports
notepad vehicle_count_20240115.txt
```

**Method 3: Excel/Spreadsheet**
- Reports are formatted for easy copy-paste to Excel
- Use fixed-width font (Courier New) for proper alignment

---

## 6. Managing Data

### 6.1 Database Files

Located in `database/` folder:

#### traffic_logs.csv
```csv
timestamp,vehicle_id,vehicle_type,confidence,event
2024-01-15 10:30:45,1,car,0.92,counted
2024-01-15 10:31:12,2,motorcycle,0.88,counted
2024-01-15 10:32:05,3,car,0.95,counted
```

**Open with:**
- Microsoft Excel
- Google Sheets
- LibreOffice Calc
- Any text editor

#### rental_records.csv
```csv
date,vehicle_type,base_fee,discount_applied,final_fee
2024-01-15,car,200,20,180
2024-01-15,motorcycle,100,10,90
2024-01-15,bus,400,40,360
```

### 6.2 Viewing Database

**Using Excel:**
1. Open Excel
2. File → Open
3. Navigate to `database/` folder
4. Select `traffic_logs.csv` or `rental_records.csv`
5. Click "Open"

**Using Python:**
```python
import pandas as pd

# Read traffic logs
logs = pd.read_csv('database/traffic_logs.csv')
print(logs.head())

# Read rental records
rentals = pd.read_csv('database/rental_records.csv')
print(rentals.head())
```

### 6.3 Backing Up Data

**Manual Backup:**
1. Navigate to project folder
2. Copy `database/` folder
3. Paste to safe location (USB drive, cloud storage)
4. Rename with date: `database_backup_20240115`

**Automated Backup Script:**
```bash
# Run this weekly
xcopy "database" "backups\database_%date:~-4,4%%date:~-10,2%%date:~-7,2%" /E /I
```

### 6.4 Clearing Data

**Clear Today's Data Only:**
- No built-in function
- Manually edit CSV files
- Filter by date and delete rows

**Clear All Data:**
1. Navigate to `database/` folder
2. Delete `traffic_logs.csv`
3. Delete `rental_records.csv`
4. Re-run system to create new files

**⚠️ Warning**: This permanently deletes all data. Backup first!

---

## 7. Troubleshooting

### Problem: "ImportError: No module named X"

**Solution:**
```bash
# Activate environment
conda activate fyp

# Install missing package
pip install [package_name]

# Verify
python test_imports.py
```

### Problem: "Camera not detected"

**Solution 1:** Try different camera indices
```python
# Edit scripts/config.py
VIDEO_SOURCE = 1  # Try 1, 2, 3 instead of 0
```

**Solution 2:** Check camera permissions
- Windows Settings → Privacy → Camera
- Enable camera access for applications

**Solution 3:** Use video file instead
- Click "📹 Upload" in GUI
- Select a test video file

### Problem: "Low FPS (< 15)"

**Solution 1:** Close other applications
- Close browsers, games, streaming apps
- Free up RAM and CPU

**Solution 2:** Use smaller frame size
```python
# Edit scripts/config.py
FRAME_WIDTH = 640  # Instead of 1280
FRAME_HEIGHT = 480  # Instead of 720
```

**Solution 3:** Reduce preprocessing
```python
# Edit scripts/preprocessing.py
# Comment out contrast enhancement and noise reduction
# Use only resizing
```

### Problem: "GUI not opening"

**Solution 1:** Install tkinter
```bash
conda install tk
```

**Solution 2:** Use console mode
- Select option 2 when starting
- Console mode doesn't require GUI

**Solution 3:** Update graphics drivers
- Visit GPU manufacturer website
- Download latest drivers

### Problem: "Detection not accurate"

**Solution 1:** Adjust confidence threshold
```python
# Edit scripts/config.py
CONFIDENCE_THRESHOLD = 0.3  # Lower from 0.5
```

**Solution 2:** Improve lighting
- Use brighter environment
- Add artificial lighting
- Avoid backlighting

**Solution 3:** Use better quality video
- Higher resolution (720p+)
- Stable camera position
- Clear view of vehicles

### Problem: "Reports not generating"

**Solution 1:** Check database files exist
```bash
# List database files
dir database\*.csv
```

**Solution 2:** Check reports folder exists
```bash
# Create if missing
mkdir reports
```

**Solution 3:** Check permissions
- Right-click project folder
- Properties → Security
- Ensure "Write" permission enabled

---

## 8. Tips & Best Practices

### For Best Detection Results

1. **Camera Placement**
   - Mount at 30-45° angle
   - Height: 3-5 meters
   - Clear, unobstructed view
   - Avoid direct sunlight

2. **Lighting**
   - Even, diffused lighting
   - Avoid shadows
   - Use IR lights for night vision

3. **Video Quality**
   - Minimum 720p resolution
   - 25-30 FPS recommended
   - Stable mounting (no vibration)

### For System Performance

1. **Hardware**
   - SSD instead of HDD for faster I/O
   - 16GB RAM recommended
   - Dedicated GPU preferred (NVIDIA)

2. **Software**
   - Keep environment updated
   - Close unnecessary applications
   - Use YOLOv8 nano model (fastest)

3. **Configuration**
   - Adjust frame size based on hardware
   - Lower confidence threshold if missing detections
   - Increase confidence threshold if too many false positives

### For Data Management

1. **Regular Backups**
   - Weekly database backups
   - Monthly full project backups
   - Use cloud storage for redundancy

2. **Database Maintenance**
   - Archive old data quarterly
   - Keep recent 3 months in active database
   - Clear logs after generating reports

3. **Report Organization**
   - Generate reports daily
   - Archive monthly reports to separate folder
   - Use consistent naming convention

### For Academic Presentation

1. **Demo Preparation**
   - Test with sample videos beforehand
   - Prepare 2-3 different test scenarios
   - Have backup video files ready

2. **Documentation**
   - Print key reports
   - Take screenshots of GUI
   - Document any customizations made

3. **Q&A Preparation**
   - Know your configuration values
   - Understand YOLOv8 architecture
   - Be familiar with DeepSORT algorithm

---

## Quick Reference Commands

```bash
# Activate Environment
conda activate fyp

# Navigate to Project
cd "C:\Users\HASIB_ULLAH\Documents\HU Traffic Analyzing and Vehicle Counting System..."

# Run System
python main_new.py

# Test Imports
python test_imports.py

# View Database
python -c "import pandas as pd; print(pd.read_csv('database/traffic_logs.csv').tail())"

# Check Configuration
python -c "from scripts import config; print(config.RENTAL_PRICES)"

# List Reports
dir reports\*.txt

# Open Latest Report
notepad reports\vehicle_count_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
```

---

## Keyboard Shortcuts (Console Mode)

| Key | Action |
|-----|--------|
| q | Quit application |
| s | Show statistics |
| ESC | Exit |
| Space | Pause/Resume |

## GUI Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Start processing |
| Ctrl+P | Stop processing |
| Ctrl+U | Upload video |
| Ctrl+W | Switch to webcam |
| Ctrl+R | Generate reports |
| Ctrl+Q | Quit application |

---

## Support Contacts

**For Technical Issues:**
- Check this guide first
- Review README.md
- Check CHANGELOG.md for known issues

**For Academic Questions:**
- Consult project supervisor
- Refer to proposal document
- Review architecture diagram

---

**Guide Version:** 1.0  
**Last Updated:** January 2024  
**Compatibility:** Windows 10/11, Python 3.11.14

---
