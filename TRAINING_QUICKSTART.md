# 🚀 Quick Start: Training Custom Vehicle Detection Model

## Prerequisites

```bash
pip install ultralytics opencv-python numpy PyYAML tqdm torch
```

## Method 1: Quick Test with Sample Data

```bash
# Step 1: Prepare sample dataset
python training/prepare_dataset.py

# Step 2: Train on sample data (for testing pipeline)
python training/train_yolo.py

# Step 3: Validate model
python training/validate_model.py

# Step 4: Use trained model
# Copy: vehicle_detection_training/yolov8n_vehicle/weights/best.pt → models/best.pt
# Update scripts/config.py: YOLO_MODEL = 'models/best.pt'
python main_new.py
```

## Method 2: Train with Real Data (COCO Dataset)

```python
# prepare_real_dataset.py
from training import DatasetPreparer

preparer = DatasetPreparer(output_dir='dataset')
preparer.create_directory_structure()
preparer.create_data_yaml()

# Convert COCO to YOLO format
preparer.convert_coco_to_yolo(
    coco_images_dir='/path/to/coco/train2017',
    coco_annotations_file='/path/to/coco/annotations/instances_train2017.json',
    split='train'
)

preparer.convert_coco_to_yolo(
    coco_images_dir='/path/to/coco/val2017',
    coco_annotations_file='/path/to/coco/annotations/instances_val2017.json',
    split='val'
)

preparer.verify_dataset()
```

Then train:

```bash
python training/train_yolo.py
```

## Method 3: Custom Dataset

### 1. Organize Your Images

```
dataset/
├── images/
│   ├── train/  # Put training images here
│   ├── val/    # Put validation images here
│   └── test/   # Put test images here
```

### 2. Create YOLO Format Labels

For each image, create a `.txt` file with same name:

```
# Example: image001.txt
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.15 0.2

Format: class_id x_center y_center width height (all normalized 0-1)
```

### 3. Create data.yaml

```yaml
path: dataset
train: images/train
val: images/val
test: images/test

nc: 4  # Number of classes

names:
  0: car
  1: truck
  2: bus
  3: motorcycle
```

### 4. Train

```bash
python training/train_yolo.py
```

## Training Configuration

Edit `training/train_yolo.py`:

```python
# Quick training (testing)
custom_config = {
    'epochs': 50,
    'batch': 16,
    'imgsz': 640,
}

# Full training (production)
custom_config = {
    'epochs': 150,
    'batch': 16,
    'imgsz': 640,
    'patience': 30,
}

# High accuracy training
custom_config = {
    'epochs': 300,
    'batch': 32,
    'imgsz': 1280,
    'patience': 50,
}
```

## Model Sizes

```python
# Fast but lower accuracy
trainer = VehicleDetectionTrainer(model_size='n')  # nano

# Balanced
trainer = VehicleDetectionTrainer(model_size='s')  # small

# High accuracy
trainer = VehicleDetectionTrainer(model_size='m')  # medium
trainer = VehicleDetectionTrainer(model_size='l')  # large
```

## Using Trained Model

### Option 1: Update Config

```python
# scripts/config.py
YOLO_MODEL = os.path.join(MODELS_DIR, 'best.pt')
USE_CUSTOM_MODEL = True
```

### Option 2: Direct Usage

```python
from training import VideoInference

inference = VideoInference(
    model_path='models/best.pt',
    video_source='video.mp4',
    enable_tracking=True,
    enable_counting=True
)
inference.run(display=True)
```

## Expected Training Time

| Dataset Size | Model | GPU | Time |
|--------------|-------|-----|------|
| 1,000 images | YOLOv8n | T4 | ~1 hour |
| 8,000 images | YOLOv8n | T4 | ~8 hours |
| 8,000 images | YOLOv8s | V100 | ~6 hours |
| 50,000 images | YOLOv8m | A100 | ~24 hours |

## Validation Results

After training, you'll see:

```
VALIDATION RESULTS
=============================================
Overall Metrics:
  mAP50:           0.8542
  mAP50-95:        0.6734
  Precision:       0.8123
  Recall:          0.7845

Per-Class mAP50:
  car            : 0.9012
  truck          : 0.8234
  bus            : 0.8567
  motorcycle     : 0.7956
```

## Troubleshooting

### GPU Out of Memory
```python
custom_config = {'batch': 8}  # Reduce batch size
```

### Training Too Slow
```python
custom_config = {
    'imgsz': 416,    # Smaller image size
    'batch': 32,     # Larger batch
    'workers': 8,    # More workers
}
```

### Low Accuracy
1. Train longer (more epochs)
2. Use larger model (YOLOv8s or YOLOv8m)
3. Add more diverse training data
4. Increase augmentation

## Integration Flow

```
1. Prepare Dataset → 2. Train Model → 3. Validate
        ↓                    ↓              ↓
    dataset/         best.pt created    Check mAP
                            ↓
                4. Copy to models/best.pt
                            ↓
                5. Update config.py
                            ↓
                6. Run main_new.py
```

## Video Resources

Check `training/README.md` for detailed documentation.

## Quick Commands

```bash
# Setup
pip install -r requirements.txt

# Prepare
python training/prepare_dataset.py

# Train (with sample data)
python training/train_yolo.py

# Validate
python training/validate_model.py

# Test on video
python training/inference_video.py

# Integrate
cp vehicle_detection_training/yolov8n_vehicle/weights/best.pt models/
# Edit scripts/config.py
python main_new.py
```

---

**Need Help?** Check `training/README.md` for comprehensive documentation.
