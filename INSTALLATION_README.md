# 🚀 QUICK INSTALLATION GUIDE

## One-Click Complete Setup

### **Option 1: Batch File (Recommended)**
Simply **double-click** this file:
```
⚡ INSTALL_EVERYTHING.bat
```

### **Option 2: PowerShell**
Right-click and "Run with PowerShell":
```
INSTALL_EVERYTHING.ps1
```

---

## What Gets Installed Automatically

The installer will:
1. ✅ Create conda environment `fyp`
2. ✅ Install Python 3.11.14
3. ✅ Install OpenCV 4.8.1.78
4. ✅ Install YOLOv8 (Ultralytics 8.4.12)
5. ✅ Install DeepSORT 1.3.2
6. ✅ Install NumPy 1.24.3
7. ✅ Install Pillow, Pandas, and other dependencies
8. ✅ Create all required folders (data, reports, database, models)
9. ✅ Verify all imports

**Total Time**: 5-10 minutes

---

## After Installation

Once installation completes, **run the system** by double-clicking:
```
🚀 START HERE.bat
```

Then select option **1** for GUI Dashboard.

---

## Requirements

- **Conda** (Miniconda or Anaconda) must be installed
- **Internet connection** for downloading packages
- **~2GB free space** for packages

If Conda is not installed, download from:
https://docs.conda.io/en/latest/miniconda.html

---

## Manual Installation (Alternative)

If the automatic installer doesn't work, run these commands:

```bash
# Open Anaconda Prompt
conda create -n fyp python=3.11.14 -y
conda activate fyp

# Install packages
pip install opencv-python==4.8.1.78
pip install ultralytics==8.4.12
pip install deep-sort-realtime==1.3.2
pip install numpy==1.24.3
pip install Pillow pandas scipy matplotlib

# Test installation
python test_imports.py
```

---

## Troubleshooting

**Problem**: "Conda not found"
- Install Miniconda first from the link above

**Problem**: "Environment already exists"
- The installer will skip creating it and use the existing one

**Problem**: "Some packages failed to install"
- The installer will continue and you can install missing packages later
- Run: `pip install [package-name]`

**Problem**: "Import test failed"
- Check error messages
- Re-run the installer
- Try manual installation

---

## Verify Installation

After installation, check if everything works:

```bash
conda activate fyp
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

## Ready to Run!

After successful installation:
1. Double-click `🚀 START HERE.bat`
2. Choose option 1 (GUI Dashboard)
3. Click "Start" to begin processing
4. Use "Upload" for video files or "Webcam" for live feed

---

**Questions?** Check README.md or USER_GUIDE.md for detailed instructions.
