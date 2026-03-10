"""
YOLOv8 Training Script for Vehicle Detection
Trains a custom YOLOv8 model on vehicle dataset with extensive augmentation
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import torch
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts import config


class VehicleDetectionTrainer:
    """Train YOLOv8 model for vehicle detection"""
    
    def __init__(self, 
                 model_size='n',  # n, s, m, l, x
                 data_yaml='dataset/data.yaml',
                 project_name='vehicle_detection_training'):
        """
        Initialize trainer
        
        Args:
            model_size: YOLOv8 model size (n=nano, s=small, m=medium, l=large, x=xlarge)
            data_yaml: Path to dataset YAML configuration
            project_name: Project name for saving results
        """
        self.model_size = model_size
        self.data_yaml = Path(PROJECT_ROOT) / data_yaml
        self.project_name = project_name
        self.model = None
        
        # Training configuration
        self.training_config = {
            'epochs': 150,              # Number of training epochs
            'imgsz': 640,               # Image size for training
            'batch': 16,                # Batch size (adjust based on GPU memory)
            'patience': 30,             # Early stopping patience
            'optimizer': 'AdamW',       # Optimizer (AdamW, SGD, Adam)
            'lr0': 0.001,              # Initial learning rate
            'lrf': 0.01,               # Final learning rate (lr0 * lrf)
            'momentum': 0.937,          # SGD momentum
            'weight_decay': 0.0005,     # Weight decay
            'warmup_epochs': 3.0,       # Warmup epochs
            'warmup_momentum': 0.8,     # Warmup initial momentum
            'warmup_bias_lr': 0.1,      # Warmup initial bias lr
            'cos_lr': True,             # Use cosine learning rate scheduler
            
            # Data augmentation
            'hsv_h': 0.015,            # HSV-Hue augmentation
            'hsv_s': 0.7,              # HSV-Saturation augmentation
            'hsv_v': 0.4,              # HSV-Value augmentation
            'degrees': 10.0,           # Rotation (+/- deg)
            'translate': 0.1,          # Translation (+/- fraction)
            'scale': 0.5,              # Scaling (+/- gain)
            'shear': 0.0,              # Shear (+/- deg)
            'perspective': 0.0,        # Perspective (+/- fraction)
            'flipud': 0.0,             # Flip up-down (probability)
            'fliplr': 0.5,             # Flip left-right (probability)
            'mosaic': 1.0,             # Mosaic augmentation (probability)
            'mixup': 0.2,              # MixUp augmentation (probability)
            'copy_paste': 0.1,         # Copy-paste augmentation (probability)
            
            # Additional settings
            'device': 0 if torch.cuda.is_available() else 'cpu',  # GPU device
            'workers': 8,              # DataLoader workers
            'project': project_name,   # Project name
            'name': f'yolov8{model_size}_vehicle',  # Experiment name
            'exist_ok': True,          # Overwrite existing project
            'pretrained': True,        # Use pretrained weights
            'verbose': True,           # Verbose output
            'save': True,              # Save checkpoints
            'save_period': 10,         # Save checkpoint every x epochs
            'cache': False,            # Cache images (True, False, 'ram', 'disk')
            'rect': False,             # Rectangular training
            'resume': False,           # Resume training from last checkpoint
            'amp': True,               # Automatic Mixed Precision training
            'fraction': 1.0,           # Dataset fraction to train on
            'profile': False,          # Profile ONNX and TensorRT speeds
            'freeze': None,            # Freeze layers (list or int)
        }
        
        print("=" * 70)
        print(" " * 20 + "YOLOv8 Vehicle Detection Training")
        print("=" * 70)
        print(f"Model: YOLOv8{model_size}")
        print(f"Dataset: {self.data_yaml}")
        print(f"Device: {self.training_config['device']}")
        print(f"Image Size: {self.training_config['imgsz']}")
        print(f"Batch Size: {self.training_config['batch']}")
        print(f"Epochs: {self.training_config['epochs']}")
        print("=" * 70)
    
    def verify_dataset(self):
        """Verify dataset structure and configuration"""
        print("\n[1] Verifying dataset...")
        
        # Check if data.yaml exists
        if not self.data_yaml.exists():
            print(f"✗ Dataset configuration not found: {self.data_yaml}")
            print("\nCreate dataset structure:")
            print("  dataset/")
            print("  ├── images/")
            print("  │   ├── train/")
            print("  │   ├── val/")
            print("  │   └── test/")
            print("  ├── labels/")
            print("  │   ├── train/")
            print("  │   ├── val/")
            print("  │   └── test/")
            print("  └── data.yaml")
            return False
        
        # Load and verify data.yaml
        with open(self.data_yaml, 'r') as f:
            data_config = yaml.safe_load(f)
        
        print(f"✓ Found data.yaml")
        print(f"  Classes: {len(data_config.get('names', []))}")
        print(f"  Names: {data_config.get('names', [])}")
        
        # Check directories
        dataset_root = self.data_yaml.parent
        train_images = dataset_root / 'images' / 'train'
        val_images = dataset_root / 'images' / 'val'
        
        if train_images.exists():
            train_count = len(list(train_images.glob('*.*')))
            print(f"✓ Training images: {train_count}")
        else:
            print(f"✗ Training images not found: {train_images}")
            return False
        
        if val_images.exists():
            val_count = len(list(val_images.glob('*.*')))
            print(f"✓ Validation images: {val_count}")
        else:
            print(f"✗ Validation images not found: {val_images}")
            return False
        
        return True
    
    def load_model(self):
        """Load YOLOv8 model"""
        print("\n[2] Loading model...")
        
        model_name = f'yolov8{self.model_size}.pt'
        self.model = YOLO(model_name)
        
        print(f"✓ Loaded {model_name}")
        print(f"  Parameters: {sum(p.numel() for p in self.model.model.parameters()):,}")
        
        return self.model
    
    def train(self, custom_config=None):
        """
        Train the model
        
        Args:
            custom_config: Optional dictionary to override training config
        
        Returns:
            Training results
        """
        if not self.verify_dataset():
            print("\n✗ Dataset verification failed. Cannot start training.")
            return None
        
        if self.model is None:
            self.load_model()
        
        # Update config with custom settings
        if custom_config:
            self.training_config.update(custom_config)
        
        print("\n[3] Starting training...")
        print(f"    This may take several hours depending on dataset size and hardware.")
        print(f"    Training progress will be saved to: {self.training_config['project']}/")
        print(f"    Best model will be saved as: runs/detect/{self.training_config['name']}/weights/best.pt")
        print("\n" + "=" * 70)
        
        try:
            # Start training
            results = self.model.train(
                data=str(self.data_yaml),
                **self.training_config
            )
            
            print("\n" + "=" * 70)
            print("✓ Training completed successfully!")
            print(f"  Best model: {self.model.trainer.best}")
            print(f"  Results saved to: {self.model.trainer.save_dir}")
            print("=" * 70)
            
            return results
            
        except Exception as e:
            print(f"\n✗ Training error: {e}")
            return None
    
    def validate(self, model_path=None):
        """
        Validate trained model
        
        Args:
            model_path: Path to trained model (default: use best.pt from training)
        
        Returns:
            Validation results
        """
        print("\n[4] Validating model...")
        
        if model_path:
            self.model = YOLO(model_path)
        elif self.model is None:
            print("✗ No model loaded. Train first or provide model_path.")
            return None
        
        try:
            results = self.model.val(
                data=str(self.data_yaml),
                imgsz=self.training_config['imgsz'],
                batch=self.training_config['batch'],
                device=self.training_config['device']
            )
            
            print("\n" + "=" * 70)
            print("Validation Results:")
            print("=" * 70)
            print(f"  mAP50:       {results.box.map50:.4f}")
            print(f"  mAP50-95:    {results.box.map:.4f}")
            print(f"  Precision:   {results.box.mp:.4f}")
            print(f"  Recall:      {results.box.mr:.4f}")
            print("=" * 70)
            
            return results
            
        except Exception as e:
            print(f"✗ Validation error: {e}")
            return None
    
    def export_model(self, model_path=None, formats=None):
        """
        Export model to different formats
        
        Args:
            model_path: Path to model to export
            formats: List of formats ['onnx', 'torchscript', 'coreml', 'tflite']
        """
        if formats is None:
            formats = ['onnx']
        
        if model_path:
            self.model = YOLO(model_path)
        
        print(f"\n[5] Exporting model to formats: {formats}")
        
        for fmt in formats:
            try:
                self.model.export(format=fmt)
                print(f"✓ Exported to {fmt}")
            except Exception as e:
                print(f"✗ Failed to export to {fmt}: {e}")


def main():
    """Main training pipeline"""
    print("\n" + "=" * 70)
    print(" " * 15 + "YOLOv8 Vehicle Detection Training")
    print(" " * 20 + "HU Traffic Analyzing System")
    print("=" * 70)
    
    # Configuration
    MODEL_SIZE = 'n'  # Change to 's', 'm', 'l', or 'x' for larger models
    DATA_YAML = 'dataset/data.yaml'
    
    # Initialize trainer
    trainer = VehicleDetectionTrainer(
        model_size=MODEL_SIZE,
        data_yaml=DATA_YAML,
        project_name='vehicle_detection_training'
    )
    
    # Custom training configuration (optional)
    custom_config = {
        'epochs': 150,      # Increase for better results
        'batch': 16,        # Decrease if GPU memory error
        'imgsz': 640,       # Image size
        'patience': 30,     # Early stopping
    }
    
    # Train model
    results = trainer.train(custom_config=custom_config)
    
    if results:
        # Validate model
        trainer.validate()
        
        # Export model (optional)
        # trainer.export_model(formats=['onnx'])
        
        print("\n✓ Training pipeline completed!")
        print(f"\nTo use the trained model:")
        print(f"  1. Copy best.pt to models/ directory")
        print(f"  2. Update config.py: YOLO_MODEL = 'models/best.pt'")
        print(f"  3. Run the main system: python main_new.py")
    else:
        print("\n✗ Training failed. Check dataset and configuration.")


if __name__ == '__main__':
    main()
