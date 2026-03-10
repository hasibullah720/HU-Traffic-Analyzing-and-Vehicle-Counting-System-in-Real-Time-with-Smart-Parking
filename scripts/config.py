"""
Configuration file for HU Traffic Analyzing System
Contains all system constants and settings
"""

import os

# Get paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')
VIDEO_DIR = os.path.join(DATA_DIR, 'traffic_videos')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')

# Vehicle Classes
VEHICLE_CLASSES = ['car', 'motorcycle', 'bus', 'truck']

# Extended vehicle classes for custom trained models
EXTENDED_VEHICLE_CLASSES = [
    'car', 'truck', 'bus', 'motorcycle', 'bicycle', 
    'van', 'pickup', 'ambulance', 'fire_truck', 'police_car'
]

# YOLO Model Settings
YOLO_MODEL = os.path.join(MODELS_DIR, 'yolov8n.pt')
USE_CUSTOM_MODEL = False  # Set to True if using custom trained model
CONFIDENCE_THRESHOLD = 0.25  # Lower threshold for better detection
IOU_THRESHOLD = 0.45

# Parking Settings
TOTAL_PARKING_SLOTS = 100
PARKING_SLOTS = [f"P{i+1}" for i in range(TOTAL_PARKING_SLOTS)]

# Rental Pricing (PKR) - As per Architecture
RENTAL_PRICES = {
    'motorcycle': 100,  # Bike: 100 PKR
    'car': 200,         # Car: 200 PKR
    'bus': 400,         # Bus: 400 PKR
    'truck': 500,       # Truck: 500 PKR
    'van': 300          # Van: 300 PKR
}

# Discount Settings - As per Architecture
DAILY_CUSTOMER_DISCOUNT = 0.10  # 10% discount for daily customers

# Database Settings (CSV-based)
TRAFFIC_LOGS_CSV = os.path.join(DATABASE_DIR, 'traffic_logs.csv')
RENTAL_RECORDS_CSV = os.path.join(DATABASE_DIR, 'rental_records.csv')

# Video/Camera Settings
VIDEO_SOURCE = None  # None requires selection, 0 for webcam, or path to video file
FRAME_WIDTH = 640  # Reduced for faster processing (was 1280)
FRAME_HEIGHT = 480  # Reduced for faster processing (was 720)
FPS = 30

# Performance Settings (Optimized for speed - targeting 30+ FPS)
FRAME_SKIP = 2  # Process every Nth frame for detection (lower = more detections)
PREPROCESS_TARGET_SIZE = (640, 640)  # Larger size for better detection accuracy
MAX_AGE = 90  # Tracker keeps tracks without detection (must be > FRAME_SKIP * 10)
YOLO_IMGSZ = 640  # YOLOv8 inference image size (larger = better detection)

# Detection Line Settings (for counting)
DETECTION_LINE_Y = 400  # Y-coordinate for counting line
LINE_THICKNESS = 3

# GUI Settings
GUI_TITLE = "HU Traffic Monitoring System"
GUI_WIDTH = 1400
GUI_HEIGHT = 900
UPDATE_INTERVAL = 30  # milliseconds

# Colors (BGR format for OpenCV)
COLOR_CAR = (255, 0, 0)      # Blue
COLOR_BIKE = (0, 255, 0)     # Green
COLOR_BUS = (0, 0, 255)      # Red
COLOR_TRUCK = (255, 255, 0)  # Cyan
COLOR_VAN = (255, 0, 255)    # Magenta
COLOR_LINE = (0, 255, 255)   # Yellow
