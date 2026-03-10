"""
Advanced Video Inference with Vehicle Tracking
Runs trained YOLOv8 model on video with DeepSORT tracking integration
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
import time
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from ultralytics import YOLO
from scripts.tracking import VehicleTracker
from scripts.counting import VehicleCounter
from scripts import config
import utils


class VideoInference:
    """Run inference on video with tracking and counting"""
    
    def __init__(self, 
                 model_path,
                 video_source=0,
                 conf_threshold=0.25,
                 iou_threshold=0.45,
                 enable_tracking=True,
                 enable_counting=True):
        """
        Initialize video inference
        
        Args:
            model_path: Path to trained YOLOv8 model
            video_source: Video file path or camera index (0 for webcam)
            conf_threshold: Confidence threshold for detection
            iou_threshold: IOU threshold for NMS
            enable_tracking: Enable DeepSORT tracking
            enable_counting: Enable vehicle counting
        """
        self.model_path = Path(model_path)
        self.video_source = video_source
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.enable_tracking = enable_tracking
        self.enable_counting = enable_counting
        
        self.model = None
        self.tracker = None
        self.counter = None
        self.cap = None
        
        self.frame_count = 0
        self.fps = 0
        self.fps_time = time.time()
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'total_detections': 0,
            'processing_times': []
        }
        
        print("=" * 70)
        print(" " * 15 + "YOLOv8 Video Inference with Tracking")
        print("=" * 70)
        print(f"Model:       {self.model_path}")
        print(f"Video:       {self.video_source}")
        print(f"Confidence:  {self.conf_threshold}")
        print(f"Tracking:    {'Enabled' if self.enable_tracking else 'Disabled'}")
        print(f"Counting:    {'Enabled' if self.enable_counting else 'Disabled'}")
        print("=" * 70)
    
    def load_model(self):
        """Load YOLOv8 model"""
        print("\n[1] Loading model...")
        
        if not self.model_path.exists():
            print(f"✗ Model not found: {self.model_path}")
            return False
        
        try:
            self.model = YOLO(str(self.model_path))
            print(f"✓ Model loaded: {self.model_path.name}")
            
            # Print model classes
            print(f"  Classes: {self.model.names}")
            
            return True
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    
    def init_video(self):
        """Initialize video capture"""
        print("\n[2] Initializing video capture...")
        
        try:
            self.cap = cv2.VideoCapture(self.video_source)
            
            if not self.cap.isOpened():
                print(f"✗ Cannot open video source: {self.video_source}")
                return False
            
            # Get video properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            source_name = "Webcam" if self.video_source == 0 else str(self.video_source)
            print(f"✓ Video source opened: {source_name}")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {fps:.2f}")
            
            return True
            
        except Exception as e:
            print(f"✗ Video error: {e}")
            return False
    
    def init_tracker(self):
        """Initialize vehicle tracker"""
        if self.enable_tracking:
            print("\n[3] Initializing DeepSORT tracker...")
            self.tracker = VehicleTracker(max_age=config.MAX_AGE)
            print("✓ Tracker initialized")
    
    def init_counter(self):
        """Initialize vehicle counter"""
        if self.enable_counting:
            print("\n[4] Initializing vehicle counter...")
            self.counter = VehicleCounter()
            print("✓ Counter initialized")
    
    def detect_frame(self, frame):
        """
        Run detection on single frame
        
        Args:
            frame: Input frame
        
        Returns:
            List of detections
        """
        # Run inference
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        
        # Extract detections
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy()
                
                x1, y1, x2, y2 = map(int, xyxy)
                
                detection = {
                    'bbox': (x1, y1, x2, y2),
                    'class': self.model.names[cls],
                    'confidence': conf,
                    'class_id': cls
                }
                
                detections.append(detection)
        
        return detections
    
    def process_frame(self, frame):
        """
        Process single frame with detection, tracking, and counting
        
        Args:
            frame: Input frame
        
        Returns:
            Processed frame with annotations
        """
        start_time = time.time()
        
        # Detect vehicles
        detections = self.detect_frame(frame)
        self.stats['total_detections'] += len(detections)
        
        # Track vehicles
        if self.enable_tracking and self.tracker:
            tracks = self.tracker.update(detections, frame)
            
            # Draw tracks
            frame = self.tracker.draw_tracks(frame, tracks)
            
            # Count vehicles
            if self.enable_counting and self.counter:
                frame = self.counter.draw_counting_line(frame)
                
                for track in tracks:
                    if not track.get('is_confirmed', True):
                        continue
                    
                    if self.tracker.check_line_crossing(
                        track['track_id'],
                        track['bbox'],
                        self.counter.line_y
                    ):
                        self.counter.update_count(track['track_id'], track['class'])
                
                # Draw counts
                counts = self.counter.get_counts()
                frame = self.draw_counts(frame, counts)
        else:
            # Just draw detections without tracking
            for detection in detections:
                bbox = detection['bbox']
                vehicle_class = detection['class']
                confidence = detection['confidence']
                
                color = self.get_color_for_class(vehicle_class)
                label = f"{vehicle_class} {confidence:.2f}"
                
                frame = utils.draw_detection_box(
                    frame, bbox, label, color, confidence
                )
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        self.stats['processing_times'].append(process_time)
        
        # Update frame count
        self.frame_count += 1
        self.stats['total_frames'] += 1
        
        # Calculate FPS
        if self.frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - self.fps_time
            if elapsed > 0:
                self.fps = 30 / elapsed
                self.fps_time = current_time
        
        # Draw FPS and info
        frame = self.draw_info(frame, len(detections), process_time)
        
        return frame
    
    def draw_counts(self, frame, counts):
        """Draw vehicle counts on frame"""
        y_offset = 30
        
        info_text = [
            f"Total: {counts['total']}",
            f"Cars: {counts['car']}",
            f"Trucks: {counts['truck']}",
            f"Buses: {counts['bus']}",
            f"Motorcycles: {counts['motorcycle']}"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(
                frame,
                text,
                (10, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        return frame
    
    def draw_info(self, frame, num_detections, process_time):
        """Draw FPS and detection info on frame"""
        height, width = frame.shape[:2]
        
        info_text = [
            f"FPS: {self.fps:.1f}",
            f"Detections: {num_detections}",
            f"Process: {process_time:.1f}ms"
        ]
        
        y_offset = height - 80
        
        for i, text in enumerate(info_text):
            cv2.putText(
                frame,
                text,
                (width - 220, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        return frame
    
    def get_color_for_class(self, class_name):
        """Get color for vehicle class"""
        color_map = {
            'car': (255, 0, 0),         # Blue
            'truck': (255, 255, 0),     # Cyan
            'bus': (0, 0, 255),         # Red
            'motorcycle': (0, 255, 0),  # Green
            'bicycle': (0, 255, 255),   # Yellow
            'van': (255, 0, 255),       # Magenta
        }
        return color_map.get(class_name.lower(), (255, 255, 255))
    
    def run(self, output_path=None, display=True):
        """
        Run inference on video
        
        Args:
            output_path: Path to save output video (optional)
            display: Display video in window
        """
        # Load model
        if not self.load_model():
            return
        
        # Initialize video
        if not self.init_video():
            return
        
        # Initialize tracker and counter
        self.init_tracker()
        self.init_counter()
        
        # Video writer
        video_writer = None
        if output_path:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            print(f"\n✓ Output video: {output_path}")
        
        print("\n[5] Running inference...")
        print("    Press 'q' to quit, 's' to save screenshot\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("✓ Video ended or cannot read frame")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Write to output video
                if video_writer:
                    video_writer.write(processed_frame)
                
                # Display
                if display:
                    cv2.imshow('Vehicle Detection - Press Q to quit', processed_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("✓ Quit by user")
                        break
                    elif key == ord('s'):
                        screenshot_path = f'screenshot_{int(time.time())}.jpg'
                        cv2.imwrite(screenshot_path, processed_frame)
                        print(f"✓ Screenshot saved: {screenshot_path}")
        
        except KeyboardInterrupt:
            print("\n✓ Interrupted by user")
        
        finally:
            # Cleanup
            if self.cap:
                self.cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()
            
            # Print statistics
            self.print_statistics()
    
    def print_statistics(self):
        """Print processing statistics"""
        print("\n" + "=" * 70)
        print("PROCESSING STATISTICS")
        print("=" * 70)
        print(f"Total frames:       {self.stats['total_frames']}")
        print(f"Total detections:   {self.stats['total_detections']}")
        print(f"Avg detections:     {self.stats['total_detections'] / max(self.stats['total_frames'], 1):.2f} per frame")
        
        if self.stats['processing_times']:
            times = np.array(self.stats['processing_times'])
            print(f"\nProcessing time:")
            print(f"  Mean:   {times.mean():.2f} ms  ({1000/times.mean():.1f} FPS)")
            print(f"  Median: {np.median(times):.2f} ms")
            print(f"  Min:    {times.min():.2f} ms")
            print(f"  Max:    {times.max():.2f} ms")
        
        if self.enable_counting and self.counter:
            counts = self.counter.get_counts()
            print(f"\nVehicle counts:")
            for vehicle_type, count in counts.items():
                if vehicle_type != 'total':
                    print(f"  {vehicle_type.capitalize():12s}: {count}")
            print(f"  {'Total':12s}: {counts['total']}")
        
        print("=" * 70)


def main():
    """Main inference pipeline"""
    print("\n" + "=" * 70)
    print(" " * 15 + "YOLOv8 Video Inference")
    print(" " * 20 + "HU Traffic Analyzing System")
    print("=" * 70)
    
    # Configuration
    MODEL_PATH = 'models/best.pt'  # Change to your trained model
    VIDEO_SOURCE = 'data/traffic_videos/sample.mp4'  # Change to your video or 0 for webcam
    OUTPUT_PATH = 'output_video.mp4'  # Optional: save output video
    
    # Initialize inference
    inference = VideoInference(
        model_path=MODEL_PATH,
        video_source=VIDEO_SOURCE,
        conf_threshold=0.25,
        iou_threshold=0.45,
        enable_tracking=True,
        enable_counting=True
    )
    
    # Run inference
    inference.run(
        output_path=OUTPUT_PATH,  # Set to None to disable saving
        display=True
    )
    
    print("\n✓ Inference complete!")


if __name__ == '__main__':
    main()
