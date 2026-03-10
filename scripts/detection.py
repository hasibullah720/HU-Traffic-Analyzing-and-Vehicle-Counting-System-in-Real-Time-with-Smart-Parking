"""
Vehicle Detector Module for HU Traffic Analyzing System
Uses YOLOv8 for real-time vehicle detection
"""

import cv2
import numpy as np
from ultralytics import YOLO
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import config
import utils


class VehicleDetector:
    """Detects vehicles using YOLOv8 model"""
    
    def __init__(self, model_path=None, use_custom_model=False):
        """
        Initialize YOLOv8 detector
        
        Args:
            model_path: Path to YOLO model file
            use_custom_model: If True, expects custom trained model with specific classes
        """
        self.model_path = model_path or config.YOLO_MODEL
        self.model = None
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
        self.iou_threshold = config.IOU_THRESHOLD
        self.use_custom_model = use_custom_model
        
        # Default COCO vehicle classes (for pretrained models)
        self.coco_vehicle_classes = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        
        # Extended vehicle classes (for custom trained models)
        self.extended_vehicle_classes = {
            0: 'car',
            1: 'truck',
            2: 'bus',
            3: 'motorcycle',
            4: 'bicycle',
            5: 'van',
            6: 'pickup',
            7: 'ambulance',
            8: 'fire_truck',
            9: 'police_car'
        }
        
        # Select appropriate mapping
        self.vehicle_classes = self.extended_vehicle_classes if use_custom_model else self.coco_vehicle_classes
        
        self.load_model()
    
    def load_model(self):
        """Load YOLOv8 model"""
        try:
            self.model = YOLO(self.model_path)
            
            # Auto-detect if using custom model
            model_classes = self.model.names
            if len(model_classes) > 80:  # Custom model likely has fewer specific classes
                self.use_custom_model = True
                self.vehicle_classes = {i: name for i, name in model_classes.items()}
            elif self.use_custom_model:
                # Custom model specified, use its classes
                self.vehicle_classes = {i: name for i, name in model_classes.items()}
            
            print(f"✓ YOLOv8 model loaded: {self.model_path}")
            print(f"  Model type: {'Custom trained' if self.use_custom_model else 'COCO pretrained'}")
            print(f"  Vehicle classes: {len(self.vehicle_classes)}")
            
        except Exception as e:
            print(f"✗ Error loading YOLO model: {e}")
            print("  Make sure ultralytics is installed: pip install ultralytics")
            print("  The model will be downloaded automatically on first run")
    
    def detect(self, frame):
        """
        Detect vehicles in frame
        
        Args:
            frame: Input frame/image
        
        Returns:
            List of detections: [{'bbox': (x1,y1,x2,y2), 'class': 'car', 'confidence': 0.95}, ...]
        """
        if self.model is None:
            return []
        
        detections = []
        
        try:
            # Run inference with detection optimized settings
            results = self.model(
                frame,
                imgsz=config.YOLO_IMGSZ,  # Detection image size
                conf=self.confidence_threshold,  # Set confidence threshold
                verbose=False,
                half=False,  # FP16 inference (enable if GPU available)
                device='cpu'  # Explicitly use CPU (change to 0 for GPU)
            )
            
            # Process results
            total_objects = 0
            for result in results:
                boxes = result.boxes
                total_objects = len(boxes)
                
                for box in boxes:
                    # Get box data
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy()
                    
                    # For custom models, accept all classes
                    # For COCO models, filter only vehicle classes
                    if self.use_custom_model:
                        is_vehicle = cls in self.vehicle_classes
                        vehicle_type = self.vehicle_classes.get(cls, 'unknown')
                    else:
                        is_vehicle = cls in self.vehicle_classes
                        vehicle_type = self.vehicle_classes.get(cls, 'unknown')
                    
                    # Check if it's a vehicle class and meets confidence threshold
                    if is_vehicle and conf >= self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        detection = {
                            'bbox': (x1, y1, x2, y2),
                            'class': vehicle_type,
                            'confidence': conf,
                            'class_id': cls
                        }
                        
                        detections.append(detection)
                        
                        # Debug: Print detection
                        if len(detections) <= 10:  # Limit debug output
                            print(f"✓ Detected {vehicle_type}: conf={conf:.2f}, bbox=({x1},{y1},{x2},{y2})")
                    
                    # Check if it's a vehicle class and meets confidence threshold
                    if cls in self.vehicle_classes and conf >= self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        detection = {
                            'bbox': (x1, y1, x2, y2),
                            'class': self.vehicle_classes[cls],
                            'confidence': conf,
                            'class_id': cls
                        }
                        
                        detections.append(detection)
                        
                        # Debug: Print detection
                        if len(detections) <= 10:  # Limit debug output
                            print(f"✓ Detected {vehicle_type}: conf={conf:.2f}, bbox=({x1},{y1},{x2},{y2})")
            
            # Debug: Show detection summary
            if total_objects > 0 or len(detections) > 0:
                print(f"[YOLO] Total objects: {total_objects}, Vehicle detections: {len(detections)}")
            
        except Exception as e:
            print(f"✗ Detection error: {e}")
        
        return detections
    
    def detect_and_draw(self, frame):
        """
        Detect vehicles and draw bounding boxes
        
        Args:
            frame: Input frame
        
        Returns:
            Tuple: (annotated_frame, detections)
        """
        detections = self.detect(frame)
        annotated_frame = frame.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            vehicle_class = detection['class']
            confidence = detection['confidence']
            
            # Get color for vehicle type
            color = utils.get_vehicle_color(vehicle_class)
            
            # Draw bounding box
            annotated_frame = utils.draw_detection_box(
                annotated_frame,
                bbox,
                vehicle_class.capitalize(),
                color,
                confidence
            )
        
        return annotated_frame, detections
    
    def batch_detect(self, frames):
        """
        Detect vehicles in multiple frames (batch processing)
        
        Args:
            frames: List of frames
        
        Returns:
            List of detection results for each frame
        """
        if self.model is None:
            return [[] for _ in frames]
        
        all_detections = []
        
        try:
            results = self.model(frames, verbose=False)
            
            for result in results:
                frame_detections = []
                boxes = result.boxes
                
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy()
                    
                    if cls in self.vehicle_classes and conf >= self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, xyxy)
                        
                        detection = {
                            'bbox': (x1, y1, x2, y2),
                            'class': self.vehicle_classes[cls],
                            'confidence': conf,
                            'class_id': cls
                        }
                        
                        frame_detections.append(detection)
                
                all_detections.append(frame_detections)
        
        except Exception as e:
            print(f"✗ Batch detection error: {e}")
        
        return all_detections
    
    def count_vehicles_by_type(self, detections):
        """
        Count vehicles by type from detections
        
        Args:
            detections: List of detection dictionaries
        
        Returns:
            Dictionary with counts per vehicle type
        """
        counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0
        }
        
        for detection in detections:
            vehicle_class = detection['class']
            if vehicle_class in counts:
                counts[vehicle_class] += 1
        
        return counts
    
    def filter_detections_by_area(self, detections, min_area=1000):
        """
        Filter detections by minimum bounding box area
        
        Args:
            detections: List of detections
            min_area: Minimum area threshold
        
        Returns:
            Filtered detections
        """
        filtered = []
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            area = (x2 - x1) * (y2 - y1)
            
            if area >= min_area:
                filtered.append(detection)
        
        return filtered
    
    def get_detection_at_point(self, detections, point):
        """
        Get detection that contains a specific point
        
        Args:
            detections: List of detections
            point: Point (x, y)
        
        Returns:
            Detection dict or None
        """
        x, y = point
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            
            if x1 <= x <= x2 and y1 <= y <= y2:
                return detection
        
        return None
    
    def set_confidence_threshold(self, threshold):
        """Set confidence threshold for detections"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        print(f"Confidence threshold set to: {self.confidence_threshold}")
    
    def get_model_info(self):
        """Get information about loaded model"""
        if self.model is None:
            return {"status": "Not loaded"}
        
        return {
            "model": self.model_path,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold,
            "vehicle_classes": list(self.vehicle_classes.values())
        }


class RegionOfInterest:
    """Define and manage Region of Interest (ROI) for detection"""
    
    def __init__(self, points=None):
        """
        Initialize ROI
        
        Args:
            points: List of points defining polygon [(x1,y1), (x2,y2), ...]
        """
        self.points = points
        self.mask = None
    
    def set_points(self, points):
        """Set ROI points"""
        self.points = points
        self.mask = None
    
    def create_mask(self, frame_shape):
        """
        Create binary mask for ROI
        
        Args:
            frame_shape: Shape of frame (height, width)
        """
        if self.points is None:
            return None
        
        height, width = frame_shape[:2]
        self.mask = np.zeros((height, width), dtype=np.uint8)
        
        points_array = np.array(self.points, dtype=np.int32)
        cv2.fillPoly(self.mask, [points_array], 255)
        
        return self.mask
    
    def apply_mask(self, frame):
        """
        Apply ROI mask to frame
        
        Args:
            frame: Input frame
        
        Returns:
            Masked frame
        """
        if self.mask is None:
            self.create_mask(frame.shape)
        
        if self.mask is None:
            return frame
        
        masked_frame = cv2.bitwise_and(frame, frame, mask=self.mask)
        return masked_frame
    
    def is_point_in_roi(self, point):
        """
        Check if point is inside ROI
        
        Args:
            point: Point (x, y)
        
        Returns:
            Boolean
        """
        if self.points is None:
            return True
        
        x, y = point
        
        # Use OpenCV pointPolygonTest
        points_array = np.array(self.points, dtype=np.int32)
        result = cv2.pointPolygonTest(points_array, (x, y), False)
        
        return result >= 0
    
    def draw_roi(self, frame, color=(0, 255, 0), thickness=2):
        """
        Draw ROI on frame
        
        Args:
            frame: Input frame
            color: Color of ROI boundary
            thickness: Line thickness
        """
        if self.points is None:
            return frame
        
        points_array = np.array(self.points, dtype=np.int32)
        cv2.polylines(frame, [points_array], True, color, thickness)
        
        return frame


# Test function
if __name__ == "__main__":
    print("Testing Vehicle Detector...")
    
    # Initialize detector
    detector = VehicleDetector()
    
    # Print model info
    info = detector.get_model_info()
    print(f"Model info: {info}")
    
    # Test with sample image (if available)
    # Create a blank test image
    test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Detect (will be empty for blank image)
    detections = detector.detect(test_frame)
    print(f"Detections found: {len(detections)}")
    
    print("✓ Detector test completed!")
