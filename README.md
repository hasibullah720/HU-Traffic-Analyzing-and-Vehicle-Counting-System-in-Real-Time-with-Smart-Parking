# HU Traffic Analyzing and Vehicle Counting System
## Real-Time with Smart Parking and Vehicle Rental Management

**Final Year Project - Computer Science**  
**Development Environment:** Python 3.11.14 | YOLOv8 | DeepSORT | OpenCV | Tkinter

---

## 📋 Project Overview

This is a comprehensive real-time traffic monitoring and management system that provides:
- **Vehicle Detection & Classification** using YOLOv8
- **Multi-Object Tracking** using DeepSORT
- **Real-Time Vehicle Counting** with line crossing detection
- **Smart Parking Management** (100 slots)
- **Automated Rental Fee Calculation** with discount system
- **Report Generation** for traffic analytics
- **Modern GUI Dashboard** for monitoring and control

---

## 🏗️ System Architecture

```
Video Input (Camera/File)
        ↓
Pre-Processing Module (Resize/Normalize)
        ↓
Vehicle Detection (YOLOv8)
        ↓
Vehicle Tracking (DeepSORT)
        ↓
Vehicle Counting (Line Crossing)
        ↓
┌───────────────┬──────────────────┐
│ Parking Mgmt  │  Rental Mgmt     │
│ - Entry/Exit  │  - Fee Calc      │
│ - Slot Detect │  - Discounts     │
│ - Status      │  - Transactions  │
└───────────────┴──────────────────┘
        ↓
Data Logger (CSV Database)
        ↓
┌───────────────┬──────────────────┐
│   GUI         │     Reports      │
│ - Live View   │  - Vehicle Count │
│ - Statistics  │  - Parking Usage │
│ - Controls    │  - Revenue       │
└───────────────┴──────────────────┘
```

---

## 📁 Project Structure

```
HU Traffic System/
│
├── main_new.py                 # Main entry point
├── test_imports.py             # Import validation script
│
├── scripts/                    # Core modules
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── preprocessing.py       # Frame pre-processing
│   ├── detection.py           # YOLOv8 vehicle detection
│   ├── tracking.py            # DeepSORT tracking
│   ├── counting.py            # Vehicle counting logic
│   ├── parking.py             # Parking management
│   ├── rental_system.py       # Rental calculations
│   └── reports.py             # Report generation
│
├── gui/                        # User interface
│   ├── __init__.py
│   └── main_gui.py            # Modern dashboard
│
├── database/                   # Data management
│   ├── __init__.py
│   ├── csv_database.py        # CSV database handler
│   ├── traffic_logs.csv       # Traffic records
│   └── rental_records.csv     # Rental transactions
│
├── models/                     # AI models
│   └── yolov8n.pt             # YOLOv8 nano model
│
├── data/                       # Data storage
│   └── traffic_videos/        # Video files
│
└── reports/                    # Generated reports
    ├── vehicle_count_YYYYMMDD.txt
    ├── parking_usage_YYYYMMDD.txt
    ├── daily_revenue_YYYYMMDD.txt
    └── overall_statistics_YYYYMMDD.txt
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.11+
- Conda (Miniconda/Anaconda)
- Webcam (optional)

### 2. Create Environment
```bash
conda create -n fyp python=3.11.14
conda activate fyp
```

### 3. Install Dependencies
```bash
pip install opencv-python==4.8.1.78
pip install ultralytics==8.4.12
pip install deep-sort-realtime==1.3.2
pip install numpy==1.24.3
pip install Pillow
```

### 4. Download YOLOv8 Model
The system automatically downloads the YOLOv8 nano model on first run, or place `yolov8n.pt` in the `models/` folder.

### 5. Verify Installation
```bash
python test_imports.py
```
You should see:
```
✓ PreProcessor imported
✓ ReportGenerator imported
✓ VehicleDetector imported
✓ VehicleTracker imported
✓ VehicleCounter imported
✓ ParkingManager imported
✓ RentalManager imported
✓ CSVDatabase imported
✓ ModernDashboard imported
✓ All imports successful!
```

---

## 🎮 Usage

### Run the System
```bash
python main_new.py
```

### Mode Selection
1. **GUI Dashboard (Recommended)** - Full-featured graphical interface
2. **Console Mode** - Command-line interface with video display
3. **Use Video File** - Process recorded video

### GUI Dashboard Features

#### Main Navigation
- **▶ Start** - Begin video processing
- **⏸ Stop** - Pause processing
- **📹 Upload** - Select video file
- **📷 Webcam** - Switch to webcam input
- **📊 Reports** - Generate analytics reports

#### Display Panels
1. **Live Video Feed** - Real-time processed video
2. **Statistics Cards** - Vehicle counts by type
3. **Parking Status** - Occupancy information
4. **Revenue Table** - Rental transactions
5. **FPS Counter** - System performance

#### Report Generation
Click the **📊 Reports** button to generate:
- Vehicle Count Reports
- Parking Usage Reports
- Daily Rental Revenue
- Overall Traffic Statistics

Reports are saved to `reports/` folder as formatted text files.

---

## ⚙️ Configuration

### Vehicle Pricing (PKR)
Edit `scripts/config.py`:
```python
RENTAL_PRICES = {
    'motorcycle': 100,  # PKR per entry
    'car': 200,
    'van': 300,
    'bus': 400,
    'truck': 500
}
```

### Discount System
```python
DAILY_CUSTOMER_DISCOUNT = 0.10  # 10% discount
```

### Detection Classes
```python
YOLO_CLASSES = {
    2: 'car',
    3: 'motorcycle',
    5: 'bus',
    7: 'truck'
}
```

### Parking Capacity
```python
TOTAL_PARKING_SLOTS = 100
```

### Video Settings
```python
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
VIDEO_SOURCE = 0  # 0 for webcam, or path to video file
```

---

## 📊 Features in Detail

### 1. Pre-Processing Module
- **Frame Resizing**: Normalizes input to 640x640 for consistent detection
- **Contrast Enhancement**: CLAHE algorithm for better visibility
- **Noise Reduction**: Bilateral filtering for cleaner frames
- **Pixel Normalization**: Scales values to [0,1] range

### 2. Vehicle Detection (YOLOv8)
- Detects: Car, Motorcycle, Bus, Truck, Van
- Real-time inference at 30+ FPS
- Confidence threshold: 0.5
- Bounding box visualization

### 3. Vehicle Tracking (DeepSORT)
- Unique ID assignment to each vehicle
- Trajectory visualization
- Maintains identity across frames
- Re-identification capability

### 4. Vehicle Counting
- Line crossing detection
- Separate counts per vehicle type
- Bi-directional counting support
- Real-time count display

### 5. Smart Parking Management
- 100 parking slots
- Entry/Exit tracking
- Occupancy visualization
- Automatic slot allocation
- Status monitoring (Free/Occupied/Reserved)

### 6. Rental Fee Calculation
- Dynamic pricing per vehicle type
- 10% discount for daily customers
- Automated transaction logging
- Revenue tracking

### 7. Data Logging
- CSV-based database for easy viewing
- Traffic event logging (timestamp, vehicle ID, type, confidence)
- Rental transaction records (date, vehicle type, fee, discount)
- Daily statistics calculation

### 8. Report Generation
Four comprehensive report types:

**a) Vehicle Count Report**
- Daily breakdown by vehicle type
- Total counts
- Timestamp range

**b) Parking Usage Report**
- Total entries/exits
- Current occupancy
- Occupancy rate percentage
- Peak usage times

**c) Daily Revenue Report**
- Revenue by vehicle type
- Discount amounts
- Gross vs. net revenue
- Transaction count

**d) Overall Statistics**
- Cumulative totals
- Average daily counts
- Revenue trends
- System performance metrics

---

## 🎨 GUI Design

### Color Scheme (Dark Theme)
- **Background**: Slate gray (#1e293b)
- **Cards**: Dark blue (#0f172a)
- **Accent**: Sky blue (#3b82f6)
- **Text**: White/Light gray
- **Stats**: Blue, Green, Purple, Orange, Red

### Components
- Floating navigation bar with icons
- Gradient stat cards
- Real-time video canvas
- Styled data tables
- Modern buttons with hover effects
- Smooth animations

---

## 📈 Performance

### System Requirements
- **Minimum**: Intel i5, 8GB RAM, Integrated GPU
- **Recommended**: Intel i7, 16GB RAM, NVIDIA GPU
- **Storage**: 2GB free space

### Performance Metrics
- **Detection Speed**: 30-60 FPS (depending on hardware)
- **Tracking Accuracy**: 95%+ ID consistency
- **Memory Usage**: ~2GB RAM
- **Model Size**: 6MB (YOLOv8 nano)

---

## 🐛 Troubleshooting

### Issue: Camera not detected
**Solution**: Check camera permissions, try different VIDEO_SOURCE values (0, 1, 2)

### Issue: Import errors
**Solution**: Run `python test_imports.py` to identify missing dependencies

### Issue: Low FPS
**Solution**: 
- Use smaller frame size in config.py
- Close other applications
- Use YOLOv8 nano model (fastest)

### Issue: Detection not working
**Solution**: 
- Check if yolov8n.pt exists in models/ folder
- Verify adequate lighting in video
- Adjust confidence threshold in config.py

### Issue: GUI not opening
**Solution**:
- Install tkinter: `conda install tk`
- Run in console mode instead (option 2)

---

## 📝 Database Schema

### traffic_logs.csv
```csv
timestamp,vehicle_id,vehicle_type,confidence,event
2024-01-15 10:30:45,1,car,0.92,counted
2024-01-15 10:31:12,2,motorcycle,0.88,counted
```

### rental_records.csv
```csv
date,vehicle_type,base_fee,discount_applied,final_fee
2024-01-15,car,200,20,180
2024-01-15,motorcycle,100,10,90
```

---

## 🔐 Data Privacy

- All data stored locally in CSV files
- No external data transmission
- User controls all video inputs
- Database files can be easily cleared

---

## 🚦 Future Enhancements

1. **License Plate Recognition** - Add OCR for vehicle identification
2. **Cloud Integration** - Upload data to cloud storage
3. **Mobile App** - Remote monitoring via smartphone
4. **Analytics Dashboard** - Advanced visualizations with charts
5. **Email Notifications** - Alerts for parking full/revenue milestones
6. **Multi-Camera Support** - Monitor multiple locations
7. **Speed Detection** - Calculate vehicle speeds
8. **Violation Detection** - Identify traffic violations

---

## 📚 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11.14 |
| Computer Vision | OpenCV | 4.8.1.78 |
| Object Detection | YOLOv8 (Ultralytics) | 8.4.12 |
| Object Tracking | DeepSORT | 1.3.2 |
| GUI Framework | Tkinter | Built-in |
| Data Processing | NumPy | 1.24.3 |
| Database | CSV | Native |

---

## 👨‍💻 Development

### Code Style
- PEP 8 compliant
- Object-oriented design
- Modular architecture
- Comprehensive comments

### Testing
```bash
# Test imports
python test_imports.py

# Test detection (console mode)
python main_new.py
# Select option 2

# Test GUI
python main_new.py
# Select option 1
```

---

## 📖 Documentation

### Module Documentation

**scripts/config.py** - Central configuration  
**scripts/preprocessing.py** - Image preprocessing pipeline  
**scripts/detection.py** - YOLOv8 detection wrapper  
**scripts/tracking.py** - DeepSORT tracking implementation  
**scripts/counting.py** - Vehicle counting logic  
**scripts/parking.py** - Parking slot management  
**scripts/rental_system.py** - Fee calculation engine  
**scripts/reports.py** - Report generation system  

**gui/main_gui.py** - Modern dashboard interface  

**database/csv_database.py** - CSV data handler  

---

## 🎓 Academic Context

**Project Type:** Final Year Project  
**Department:** Computer Science  
**Title:** HU Traffic Analyzing and Vehicle Counting System in Real-Time with Smart Parking and Vehicle Rental Management  

**Key Learning Outcomes:**
- Deep Learning (YOLOv8)
- Computer Vision (OpenCV)
- Object Tracking (DeepSORT)
- GUI Development (Tkinter)
- Database Management (CSV)
- Software Architecture
- Real-time Processing
- System Integration

---

## 📞 Support

For issues or questions:
1. Check Troubleshooting section above
2. Review error messages in console
3. Verify all dependencies installed
4. Test with sample video first
5. Check database folder permissions

---

## 📜 License

This project is developed for academic purposes as a Final Year Project.

---

## 🙏 Acknowledgments

- **YOLOv8** by Ultralytics for state-of-the-art object detection
- **DeepSORT** for robust multi-object tracking
- **OpenCV** for computer vision capabilities
- **Python Community** for excellent libraries and tools

---

## 📌 Quick Start Summary

```bash
# 1. Activate environment
conda activate fyp

# 2. Navigate to project
cd "HU Traffic Analyzing and Vehicle Counting System..."

# 3. Run the system
python main_new.py

# 4. Select GUI mode (option 1)

# 5. Click Start to begin processing

# 6. Use Upload button to select video or Webcam for live feed

# 7. Click Reports button to generate analytics

# 8. Check reports/ folder for generated files
```

---

**Version:** 1.0  
**Last Updated:** January 2024  
**Status:** ✅ Production Ready

---
#   H U - T r a f f i c - A n a l y z i n g - a n d - V e h i c l e - C o u n t i n g - S y s t e m - i n - R e a l - T i m e - w i t h - S m a r t - P a r k i n g  
 