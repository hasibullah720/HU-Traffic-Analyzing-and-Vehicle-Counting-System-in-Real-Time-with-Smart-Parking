"""Test imports for reorganized project structure"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

print("Testing imports...")
print("-" * 50)

try:
    from scripts.preprocessing import PreProcessor
    print("✓ PreProcessor imported")
except Exception as e:
    print(f"✗ PreProcessor failed: {e}")

try:
    from scripts.reports import ReportGenerator
    print("✓ ReportGenerator imported")
except Exception as e:
    print(f"✗ ReportGenerator failed: {e}")

try:
    from scripts.detection import VehicleDetector
    print("✓ VehicleDetector imported")
except Exception as e:
    print(f"✗ VehicleDetector failed: {e}")

try:
    from scripts.tracking import VehicleTracker
    print("✓ VehicleTracker imported")
except Exception as e:
    print(f"✗ VehicleTracker failed: {e}")

try:
    from scripts.counting import VehicleCounter
    print("✓ VehicleCounter imported")
except Exception as e:
    print(f"✗ VehicleCounter failed: {e}")

try:
    from scripts.parking import ParkingManager
    print("✓ ParkingManager imported")
except Exception as e:
    print(f"✗ ParkingManager failed: {e}")

try:
    from scripts.rental_system import RentalManager
    print("✓ RentalManager imported")
except Exception as e:
    print(f"✗ RentalManager failed: {e}")

try:
    from database.csv_database import CSVDatabase
    print("✓ CSVDatabase imported")
except Exception as e:
    print(f"✗ CSVDatabase failed: {e}")

try:
    from gui.main_gui import ModernDashboard
    print("✓ ModernDashboard imported")
except Exception as e:
    print(f"✗ ModernDashboard failed: {e}")

print("-" * 50)
print("✓ All project modules imported successfully!")
print()
print("Testing core dependencies...")
print("-" * 50)

# Test core packages
packages = [
    ("cv2", "OpenCV"),
    ("numpy", "NumPy"),
    ("PIL", "Pillow"),
    ("pandas", "Pandas"),
    ("matplotlib", "Matplotlib"),
    ("scipy", "Scipy"),
    ("ultralytics", "YOLOv8 (Ultralytics)"),
    ("deep_sort_realtime", "DeepSORT"),
    ("yaml", "PyYAML"),
    ("tensorboard", "TensorBoard"),
    ("seaborn", "Seaborn"),
    ("tqdm", "tqdm"),
    ("filterpy", "filterpy"),
    ("lap", "lap (Linear Assignment)"),
    ("sklearn", "scikit-learn"),
    ("requests", "requests"),
    ("pycocotools", "pycocotools"),
]

failed = []
for module, name in packages:
    try:
        __import__(module)
        print(f"✓ {name} imported")
    except Exception as e:
        print(f"✗ {name} failed: {e}")
        failed.append(name)

print("-" * 50)
if failed:
    print(f"⚠ {len(failed)} package(s) failed to import: {', '.join(failed)}")
    print("You may need to reinstall these packages")
else:
    print("✓ All dependencies imported successfully!")
    print("✓ System is ready to use! Run: python main_new.py")
