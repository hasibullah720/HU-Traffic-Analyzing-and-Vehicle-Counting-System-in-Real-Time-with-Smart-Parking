"""
Dataset Preparation Utilities for Vehicle Detection Training
Prepares datasets from COCO, BDD100K, KITTI, or custom sources
"""

import os
import json
import shutil
from pathlib import Path
import yaml
import cv2
from tqdm import tqdm


class DatasetPreparer:
    """Prepare and organize dataset for YOLOv8 training"""
    
    def __init__(self, output_dir='dataset'):
        """
        Initialize dataset preparer
        
        Args:
            output_dir: Output directory for organized dataset
        """
        self.output_dir = Path(output_dir)
        
        # Vehicle classes to detect
        self.vehicle_classes = [
            'car',
            'truck',
            'bus',
            'motorcycle',
            'bicycle',
            'van',
            'pickup',
            'ambulance',
            'fire_truck',
            'police_car'
        ]
        
        # COCO class mapping (ID -> name)
        self.coco_vehicle_classes = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck',
            1: 'bicycle',  # person on bicycle -> bicycle
        }
        
        print("=" * 70)
        print(" " * 20 + "Dataset Preparation Tool")
        print("=" * 70)
        print(f"Output directory: {self.output_dir}")
        print(f"Target classes: {len(self.vehicle_classes)}")
        print("=" * 70)
    
    def create_directory_structure(self):
        """Create YOLOv8 dataset directory structure"""
        print("\n[1] Creating directory structure...")
        
        directories = [
            self.output_dir / 'images' / 'train',
            self.output_dir / 'images' / 'val',
            self.output_dir / 'images' / 'test',
            self.output_dir / 'labels' / 'train',
            self.output_dir / 'labels' / 'val',
            self.output_dir / 'labels' / 'test',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {directory}")
        
        print("✓ Directory structure created")
    
    def create_data_yaml(self):
        """Create data.yaml configuration file"""
        print("\n[2] Creating data.yaml...")
        
        # Create class index mapping
        class_names = {i: name for i, name in enumerate(self.vehicle_classes)}
        
        data_config = {
            'path': str(self.output_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': len(self.vehicle_classes),
            'names': class_names
        }
        
        yaml_path = self.output_dir / 'data.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(data_config, f, sort_keys=False)
        
        print(f"✓ Created: {yaml_path}")
        print(f"  Classes: {len(class_names)}")
        for idx, name in class_names.items():
            print(f"    {idx}: {name}")
    
    def convert_coco_to_yolo(self, 
                             coco_images_dir,
                             coco_annotations_file,
                             split='train'):
        """
        Convert COCO format annotations to YOLO format
        
        Args:
            coco_images_dir: Directory containing COCO images
            coco_annotations_file: Path to COCO annotations JSON
            split: Dataset split ('train', 'val', 'test')
        """
        print(f"\n[3] Converting COCO annotations to YOLO format ({split})...")
        
        # Load COCO annotations
        with open(coco_annotations_file, 'r') as f:
            coco_data = json.load(f)
        
        images_info = {img['id']: img for img in coco_data['images']}
        annotations = coco_data['annotations']
        
        # Group annotations by image
        image_annotations = {}
        for ann in annotations:
            image_id = ann['image_id']
            if image_id not in image_annotations:
                image_annotations[image_id] = []
            image_annotations[image_id].append(ann)
        
        # Process images
        processed_count = 0
        skipped_count = 0
        
        output_images_dir = self.output_dir / 'images' / split
        output_labels_dir = self.output_dir / 'labels' / split
        
        for image_id, anns in tqdm(image_annotations.items(), desc=f"Processing {split}"):
            if image_id not in images_info:
                continue
            
            img_info = images_info[image_id]
            img_filename = img_info['file_name']
            img_width = img_info['width']
            img_height = img_info['height']
            
            # Filter vehicle annotations
            vehicle_anns = []
            for ann in anns:
                category_id = ann['category_id']
                if category_id in self.coco_vehicle_classes:
                    vehicle_anns.append(ann)
            
            # Skip images without vehicles
            if not vehicle_anns:
                skipped_count += 1
                continue
            
            # Copy image
            src_image_path = Path(coco_images_dir) / img_filename
            if not src_image_path.exists():
                continue
            
            dst_image_path = output_images_dir / img_filename
            shutil.copy2(src_image_path, dst_image_path)
            
            # Create YOLO format label
            label_filename = Path(img_filename).stem + '.txt'
            label_path = output_labels_dir / label_filename
            
            with open(label_path, 'w') as f:
                for ann in vehicle_anns:
                    # Map COCO class to our class index
                    coco_class = ann['category_id']
                    vehicle_type = self.coco_vehicle_classes[coco_class]
                    
                    if vehicle_type not in self.vehicle_classes:
                        continue
                    
                    class_idx = self.vehicle_classes.index(vehicle_type)
                    
                    # Convert COCO bbox (x, y, w, h) to YOLO (x_center, y_center, w, h) normalized
                    bbox = ann['bbox']
                    x, y, w, h = bbox
                    
                    x_center = (x + w / 2) / img_width
                    y_center = (y + h / 2) / img_height
                    w_norm = w / img_width
                    h_norm = h / img_height
                    
                    # Write YOLO format: class x_center y_center width height
                    f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n")
            
            processed_count += 1
        
        print(f"\n✓ Conversion complete:")
        print(f"  Processed: {processed_count} images")
        print(f"  Skipped: {skipped_count} images (no vehicles)")
    
    def verify_dataset(self):
        """Verify dataset structure and content"""
        print("\n[4] Verifying dataset...")
        
        splits = ['train', 'val', 'test']
        
        for split in splits:
            images_dir = self.output_dir / 'images' / split
            labels_dir = self.output_dir / 'labels' / split
            
            if not images_dir.exists() or not labels_dir.exists():
                print(f"  ✗ {split}: Directory not found")
                continue
            
            image_count = len(list(images_dir.glob('*.*')))
            label_count = len(list(labels_dir.glob('*.txt')))
            
            print(f"  ✓ {split}: {image_count} images, {label_count} labels")
            
            # Check if counts match
            if image_count != label_count:
                print(f"    ⚠ Warning: Image/label count mismatch")
        
        # Check data.yaml
        yaml_path = self.output_dir / 'data.yaml'
        if yaml_path.exists():
            print(f"  ✓ data.yaml exists")
        else:
            print(f"  ✗ data.yaml not found")
    
    def create_sample_dataset(self, num_samples=100):
        """
        Create a small sample dataset for testing
        (Uses empty images and random labels for demonstration)
        
        Args:
            num_samples: Number of sample images per split
        """
        print(f"\n[5] Creating sample dataset ({num_samples} samples per split)...")
        
        import numpy as np
        
        for split in ['train', 'val', 'test']:
            images_dir = self.output_dir / 'images' / split
            labels_dir = self.output_dir / 'labels' / split
            
            for i in tqdm(range(num_samples), desc=f"Creating {split}"):
                # Create dummy image
                img = np.zeros((640, 640, 3), dtype=np.uint8)
                img_filename = f"sample_{split}_{i:04d}.jpg"
                img_path = images_dir / img_filename
                cv2.imwrite(str(img_path), img)
                
                # Create dummy label
                label_filename = f"sample_{split}_{i:04d}.txt"
                label_path = labels_dir / label_filename
                
                with open(label_path, 'w') as f:
                    # Random vehicle annotations
                    num_vehicles = np.random.randint(1, 5)
                    for _ in range(num_vehicles):
                        class_idx = np.random.randint(0, len(self.vehicle_classes))
                        x_center = np.random.uniform(0.2, 0.8)
                        y_center = np.random.uniform(0.2, 0.8)
                        width = np.random.uniform(0.1, 0.3)
                        height = np.random.uniform(0.1, 0.3)
                        
                        f.write(f"{class_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        print("✓ Sample dataset created")
        print("  Note: This is a dummy dataset for testing pipeline only.")
        print("  Replace with real data for actual training.")


def main():
    """Main dataset preparation pipeline"""
    print("\n" + "=" * 70)
    print(" " * 15 + "Vehicle Detection Dataset Preparation")
    print(" " * 20 + "HU Traffic Analyzing System")
    print("=" * 70)
    
    # Initialize preparer
    preparer = DatasetPreparer(output_dir='dataset')
    
    # Create directory structure
    preparer.create_directory_structure()
    
    # Create data.yaml
    preparer.create_data_yaml()
    
    # Option 1: Convert COCO dataset (if available)
    # COCO_IMAGES_DIR = '/path/to/coco/images/train2017'
    # COCO_ANNOTATIONS = '/path/to/coco/annotations/instances_train2017.json'
    # preparer.convert_coco_to_yolo(COCO_IMAGES_DIR, COCO_ANNOTATIONS, split='train')
    
    # Option 2: Create sample dataset for testing
    print("\nNo real dataset provided. Creating sample dataset for testing...")
    preparer.create_sample_dataset(num_samples=100)
    
    # Verify dataset
    preparer.verify_dataset()
    
    print("\n" + "=" * 70)
    print("Dataset preparation complete!")
    print("\nNext steps:")
    print("  1. Replace sample data with real vehicle images and annotations")
    print("  2. Or use convert_coco_to_yolo() to import COCO dataset")
    print("  3. Run training: python training/train_yolo.py")
    print("=" * 70)


if __name__ == '__main__':
    main()
