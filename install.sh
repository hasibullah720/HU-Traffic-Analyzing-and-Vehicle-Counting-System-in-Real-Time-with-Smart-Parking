#!/bin/bash

# HU Traffic System - Quick Installer for Linux/Mac

echo "============================================"
echo "  HU Traffic System - Quick Installer"
echo "============================================"
echo

echo "Installing dependencies..."
echo

pip3 install opencv-python ultralytics deep-sort-realtime numpy pillow pandas matplotlib

echo
echo "============================================"
echo "  Verifying Installation..."
echo "============================================"
echo

python3 -c "import cv2; print('✓ OpenCV installed')"
python3 -c "import ultralytics; print('✓ YOLOv8 installed')"
python3 -c "import deep_sort_realtime; print('✓ DeepSORT installed')"
python3 -c "import numpy; print('✓ NumPy installed')"
python3 -c "import PIL; print('✓ Pillow installed')"
python3 -c "import pandas; print('✓ Pandas installed')"
python3 -c "import matplotlib; print('✓ Matplotlib installed')"
python3 -c "import tkinter; print('✓ Tkinter available')"

echo
echo "============================================"
echo "  Installation Complete!"
echo "============================================"
echo
echo "You can now run: python3 main.py"
echo

read -p "Press Enter to exit..."
