"""
Model Validation and Testing Script
Validates trained YOLOv8 model and displays detailed metrics
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np
from tqdm import tqdm

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


class ModelValidator:
    """Validate and test YOLOv8 vehicle detection model"""
    
    def __init__(self, model_path, data_yaml='dataset/data.yaml'):
        """
        Initialize validator
        
        Args:
            model_path: Path to trained model (.pt file)
            data_yaml: Path to dataset YAML configuration
        """
        self.model_path = Path(model_path)
        self.data_yaml = Path(PROJECT_ROOT) / data_yaml
        self.model = None
        
        print("=" * 70)
        print(" " * 20 + "Model Validation Tool")
        print("=" * 70)
        print(f"Model: {self.model_path}")
        print(f"Dataset: {self.data_yaml}")
        print("=" * 70)
    
    def load_model(self):
        """Load trained model"""
        print("\n[1] Loading model...")
        
        if not self.model_path.exists():
            print(f"✗ Model not found: {self.model_path}")
            return False
        
        try:
            self.model = YOLO(str(self.model_path))
            print(f"✓ Model loaded: {self.model_path.name}")
            return True
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    
    def validate(self, imgsz=640, batch=16, conf_thres=0.25):
        """
        Validate model on validation set
        
        Args:
            imgsz: Image size for validation
            batch: Batch size
            conf_thres: Confidence threshold
        
        Returns:
            Validation results
        """
        if self.model is None:
            if not self.load_model():
                return None
        
        print("\n[2] Running validation...")
        print(f"    Image size: {imgsz}")
        print(f"    Batch size: {batch}")
        print(f"    Confidence threshold: {conf_thres}")
        
        try:
            results = self.model.val(
                data=str(self.data_yaml),
                imgsz=imgsz,
                batch=batch,
                conf=conf_thres,
                iou=0.6,
                device='cpu',  # Change to 0 for GPU
                workers=4,
                verbose=True
            )
            
            print("\n" + "=" * 70)
            print("VALIDATION RESULTS")
            print("=" * 70)
            
            # Overall metrics
            print("\nOverall Metrics:")
            print(f"  mAP50:           {results.box.map50:.4f}")
            print(f"  mAP50-95:        {results.box.map:.4f}")
            print(f"  Precision:       {results.box.mp:.4f}")
            print(f"  Recall:          {results.box.mr:.4f}")
            
            # Per-class metrics
            if hasattr(results.box, 'maps'):
                print("\nPer-Class mAP50:")
                class_names = self.model.names
                for i, map_val in enumerate(results.box.maps):
                    class_name = class_names.get(i, f"class_{i}")
                    print(f"  {class_name:15s}: {map_val:.4f}")
            
            # Speed metrics
            if hasattr(results, 'speed'):
                print("\nSpeed:")
                print(f"  Preprocess:  {results.speed['preprocess']:.1f} ms")
                print(f"  Inference:   {results.speed['inference']:.1f} ms")
                print(f"  Postprocess: {results.speed['postprocess']:.1f} ms")
            
            print("=" * 70)
            
            return results
            
        except Exception as e:
            print(f"✗ Validation error: {e}")
            return None
    
    def test_on_images(self, test_images_dir, output_dir='validation_output', conf_thres=0.25):
        """
        Test model on test images and save visualizations
        
        Args:
            test_images_dir: Directory containing test images
            output_dir: Directory to save output images
            conf_thres: Confidence threshold
        """
        if self.model is None:
            if not self.load_model():
                return
        
        print(f"\n[3] Testing on images from: {test_images_dir}")
        
        test_images_dir = Path(test_images_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Get image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(test_images_dir.glob(ext))
        
        if not image_files:
            print(f"✗ No images found in {test_images_dir}")
            return
        
        print(f"Found {len(image_files)} images")
        
        # Process images
        for img_path in tqdm(image_files, desc="Processing"):
            try:
                # Run inference
                results = self.model(
                    str(img_path),
                    conf=conf_thres,
                    iou=0.6,
                    verbose=False
                )
                
                # Get annotated image
                annotated = results[0].plot()
                
                # Save output
                output_path = output_dir / img_path.name
                cv2.imwrite(str(output_path), annotated)
                
            except Exception as e:
                print(f"✗ Error processing {img_path.name}: {e}")
        
        print(f"\n✓ Output saved to: {output_dir}")
    
    def benchmark_speed(self, num_iterations=100, imgsz=640):
        """
        Benchmark model inference speed
        
        Args:
            num_iterations: Number of iterations for benchmarking
            imgsz: Image size
        """
        if self.model is None:
            if not self.load_model():
                return
        
        print(f"\n[4] Benchmarking speed ({num_iterations} iterations)...")
        
        # Create dummy image
        dummy_image = np.zeros((imgsz, imgsz, 3), dtype=np.uint8)
        
        # Warmup
        for _ in range(10):
            self.model(dummy_image, verbose=False)
        
        # Benchmark
        import time
        times = []
        
        for _ in tqdm(range(num_iterations), desc="Benchmarking"):
            start_time = time.time()
            self.model(dummy_image, verbose=False)
            end_time = time.time()
            times.append(end_time - start_time)
        
        times = np.array(times) * 1000  # Convert to ms
        
        print("\n" + "=" * 70)
        print("SPEED BENCHMARK")
        print("=" * 70)
        print(f"  Mean:    {times.mean():.2f} ms  ({1000/times.mean():.1f} FPS)")
        print(f"  Median:  {np.median(times):.2f} ms")
        print(f"  Min:     {times.min():.2f} ms  ({1000/times.min():.1f} FPS)")
        print(f"  Max:     {times.max():.2f} ms")
        print(f"  Std:     {times.std():.2f} ms")
        print("=" * 70)
    
    def compare_models(self, other_model_path):
        """
        Compare this model with another model
        
        Args:
            other_model_path: Path to another model for comparison
        """
        print(f"\n[5] Comparing with: {other_model_path}")
        
        if self.model is None:
            if not self.load_model():
                return
        
        # Validate current model
        print("\nValidating current model...")
        results1 = self.validate()
        
        # Validate other model
        print(f"\nValidating comparison model...")
        other_validator = ModelValidator(other_model_path, self.data_yaml)
        results2 = other_validator.validate()
        
        if results1 and results2:
            print("\n" + "=" * 70)
            print("MODEL COMPARISON")
            print("=" * 70)
            print(f"{'Metric':<20} {'Model 1':<15} {'Model 2':<15} {'Difference':<15}")
            print("-" * 70)
            
            metrics = [
                ('mAP50', 'map50'),
                ('mAP50-95', 'map'),
                ('Precision', 'mp'),
                ('Recall', 'mr')
            ]
            
            for metric_name, metric_key in metrics:
                val1 = getattr(results1.box, metric_key)
                val2 = getattr(results2.box, metric_key)
                diff = val1 - val2
                diff_str = f"+{diff:.4f}" if diff > 0 else f"{diff:.4f}"
                
                print(f"{metric_name:<20} {val1:<15.4f} {val2:<15.4f} {diff_str:<15}")
            
            print("=" * 70)


def main():
    """Main validation pipeline"""
    print("\n" + "=" * 70)
    print(" " * 15 + "YOLOv8 Model Validation")
    print(" " * 20 + "HU Traffic Analyzing System")
    print("=" * 70)
    
    # Configuration
    MODEL_PATH = 'vehicle_detection_training/yolov8n_vehicle/weights/best.pt'
    DATA_YAML = 'dataset/data.yaml'
    
    # Initialize validator
    validator = ModelValidator(MODEL_PATH, DATA_YAML)
    
    # Validate model
    validator.validate(imgsz=640, batch=16, conf_thres=0.25)
    
    # Test on images (optional)
    # validator.test_on_images('dataset/images/test', output_dir='validation_output')
    
    # Benchmark speed
    validator.benchmark_speed(num_iterations=100, imgsz=640)
    
    # Compare with another model (optional)
    # validator.compare_models('models/yolov8n.pt')
    
    print("\n✓ Validation complete!")


if __name__ == '__main__':
    main()
