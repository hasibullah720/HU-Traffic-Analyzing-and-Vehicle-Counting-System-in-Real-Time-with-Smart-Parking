"""
Vehicle Tracker Module for HU Traffic Analyzing System
Uses DeepSORT for multi-object tracking
"""

import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
from scripts import config


class VehicleTracker:
    """Tracks vehicles across frames using DeepSORT"""
    
    def __init__(self, max_age=70):
        """
        Initialize DeepSORT tracker
        
        Args:
            max_age: Maximum frames to keep track without detection (increased for frame skipping)
        """
        self.tracker = None
        self.max_age = max_age
        self.tracks_history = {}  # Store tracking history
        self.counted_ids = set()  # IDs that have been counted
        self.track_positions = {}  # Previous positions for each track
        
        self.initialize_tracker()
    
    def initialize_tracker(self):
        """Initialize DeepSORT tracker with optimized settings for performance"""
        try:
            self.tracker = DeepSort(
                max_age=self.max_age,  # Higher age to survive frame skipping
                n_init=1,  # Fast confirmation (required with FRAME_SKIP>1)
                max_iou_distance=0.7,
                max_cosine_distance=0.5,  # More relaxed for FRAME_SKIP=3
                nn_budget=None,  # Disable feature budget for speed
                embedder="mobilenet",
                embedder_gpu=False,
                embedder_wts=None,  # Use default weights (faster)
                polygon=False,  # Disable polygon mode (faster)
                today=None
            )
            print("✓ DeepSORT tracker initialized (optimized for performance)")
        except Exception as e:
            print(f"✗ Error initializing tracker: {e}")
            print("  Make sure deep-sort-realtime is installed: pip install deep-sort-realtime")
    
    def update(self, detections, frame):
        """
        Update tracker with new detections
        
        Args:
            detections: List of detections from detector
            frame: Current frame
        
        Returns:
            List of tracks with IDs and information
        """
        if self.tracker is None:
            return []
        
        tracks = []
        
        try:
            # Convert detections to DeepSORT format
            # Format: [[x1, y1, w, h, confidence], ...]
            deepsort_detections = []
            
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                w = x2 - x1
                h = y2 - y1
                confidence = det['confidence']
                class_name = det['class']
                
                # DeepSORT format: ([left, top, width, height], confidence, class_name)
                deepsort_detections.append(([x1, y1, w, h], confidence, class_name))
            
            # Update tracker
            tracked_objects = self.tracker.update_tracks(deepsort_detections, frame=frame)
            
            # Process tracked objects
            for track in tracked_objects:
                is_confirmed = track.is_confirmed()
                if not is_confirmed:
                    # With frame skipping, tentative tracks may be dropped before confirmation.
                    # Show freshly detected tentative tracks so users can see tracking immediately.
                    if not detections or getattr(track, 'time_since_update', 1) > 0:
                        continue
                
                track_id = track.track_id
                bbox = track.to_ltrb()  # Get bbox in (left, top, right, bottom) format
                
                # Get vehicle class from detection
                vehicle_class = 'car'  # default
                if hasattr(track, 'det_class') and track.det_class is not None:
                    vehicle_class = track.det_class
                
                track_info = {
                    'track_id': track_id,
                    'bbox': tuple(map(int, bbox)),
                    'class': vehicle_class,
                    'confidence': track.det_conf if hasattr(track, 'det_conf') else 1.0,
                    'is_confirmed': is_confirmed
                }
                
                tracks.append(track_info)
                
                # Update tracking history
                if track_id not in self.tracks_history:
                    self.tracks_history[track_id] = {
                        'first_seen': 0,
                        'positions': [],
                        'class': vehicle_class
                    }
                
                # Store position
                center = utils.get_bottom_center(bbox)
                self.tracks_history[track_id]['positions'].append(center)
                
                # Limit history length
                if len(self.tracks_history[track_id]['positions']) > 30:
                    self.tracks_history[track_id]['positions'].pop(0)
        
        except Exception as e:
            print(f"✗ Tracking error: {e}")
        
        return tracks
    
    def draw_tracks(self, frame, tracks):
        """
        Draw tracking information on frame
        
        Args:
            frame: Input frame
            tracks: List of tracks from update method
        
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        for track in tracks:
            track_id = track['track_id']
            bbox = track['bbox']
            vehicle_class = track['class']
            
            # Get color for vehicle type
            color = utils.get_vehicle_color(vehicle_class)
            
            # Draw bounding box with confidence
            label = f"ID:{track_id} {vehicle_class}"
            confidence = track.get('confidence', None)
            annotated_frame = utils.draw_detection_box(
                annotated_frame,
                bbox,
                label,
                color,
                confidence
            )
            
            # Draw trajectory if available
            if track_id in self.tracks_history:
                positions = self.tracks_history[track_id]['positions']
                
                # Draw trajectory line
                for i in range(1, len(positions)):
                    if positions[i - 1] is None or positions[i] is None:
                        continue
                    cv2.line(
                        annotated_frame,
                        positions[i - 1],
                        positions[i],
                        color,
                        2
                    )
        
        return annotated_frame
    
    def check_line_crossing(self, track_id, bbox, line_y):
        """
        Check if track crossed the counting line
        
        Args:
            track_id: ID of the track
            bbox: Current bounding box
            line_y: Y-coordinate of counting line
        
        Returns:
            Boolean indicating if line was crossed
        """
        # Get bottom center of bounding box
        current_pos = utils.get_bottom_center(bbox)
        current_y = current_pos[1]
        
        # Check if we have previous position
        if track_id not in self.track_positions:
            self.track_positions[track_id] = current_y
            return False
        
        previous_y = self.track_positions[track_id]
        
        # Update current position
        self.track_positions[track_id] = current_y
        
        # Check if already counted
        if track_id in self.counted_ids:
            return False
        
        # Check if crossed line (moving downward)
        if utils.is_crossing_line(previous_y, current_y, line_y, direction='down'):
            self.counted_ids.add(track_id)
            return True
        
        return False
    
    def get_track_info(self, track_id):
        """
        Get tracking history for a specific track
        
        Args:
            track_id: Track ID
        
        Returns:
            Track history dictionary or None
        """
        return self.tracks_history.get(track_id, None)
    
    def reset_counting(self):
        """Reset counted IDs (for new counting session)"""
        self.counted_ids.clear()
        print("✓ Counting reset")
    
    def get_active_tracks_count(self):
        """Get number of currently active tracks"""
        return len(self.tracks_history)

    def has_confirmed_tracks(self):
        """Check whether DeepSORT currently has any confirmed tracks."""
        if self.tracker is None or not hasattr(self.tracker, 'tracker'):
            return False

        internal_tracker = self.tracker.tracker
        if not hasattr(internal_tracker, 'tracks'):
            return False

        for track in internal_tracker.tracks:
            if track.is_confirmed():
                return True

        return False
    
    def clean_old_tracks(self, max_history=100):
        """
        Clean up old tracks from history
        
        Args:
            max_history: Maximum number of tracks to keep
        """
        if len(self.tracks_history) > max_history:
            # Remove oldest tracks
            sorted_tracks = sorted(
                self.tracks_history.items(),
                key=lambda x: x[1]['first_seen']
            )
            
            tracks_to_remove = sorted_tracks[:len(self.tracks_history) - max_history]
            
            for track_id, _ in tracks_to_remove:
                del self.tracks_history[track_id]
                if track_id in self.track_positions:
                    del self.track_positions[track_id]


class VehicleCounter:
    """Counts vehicles crossing a detection line"""
    
    def __init__(self, line_y=None):
        """
        Initialize vehicle counter
        
        Args:
            line_y: Y-coordinate of counting line
        """
        self.line_y = line_y or config.DETECTION_LINE_Y
        self.counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0,
            'total': 0
        }
        self.counted_track_ids = set()
    
    def update_count(self, track_id, vehicle_class):
        """
        Update count for a vehicle class
        
        Args:
            track_id: Track ID
            vehicle_class: Type of vehicle
        """
        if track_id in self.counted_track_ids:
            return False
        
        # Normalize vehicle class
        vehicle_class = utils.normalize_vehicle_type(vehicle_class)
        
        if vehicle_class in self.counts:
            self.counts[vehicle_class] += 1
            self.counts['total'] += 1
            self.counted_track_ids.add(track_id)
            
            utils.log_event("COUNT", f"Vehicle counted - ID:{track_id} Type:{vehicle_class}")
            return True
        
        return False
    
    def get_counts(self):
        """Get current counts"""
        return self.counts.copy()
    
    def reset_counts(self):
        """Reset all counts"""
        self.counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0,
            'total': 0
        }
        self.counted_track_ids.clear()
        utils.log_event("INFO", "Counts reset")
    
    def draw_counting_line(self, frame):
        """Draw counting line on frame"""
        return utils.draw_counting_line(frame, self.line_y)
    
    def draw_counts(self, frame, position=(10, 30)):
        """
        Draw count statistics on frame
        
        Args:
            frame: Input frame
            position: Starting position for text
        """
        info_text = [
            f"Total: {self.counts['total']}",
            f"Cars: {self.counts['car']}",
            f"Bikes: {self.counts['motorcycle']}",
            f"Buses: {self.counts['bus']}",
            f"Trucks: {self.counts['truck']}"
        ]
        
        return utils.draw_info_panel(frame, info_text, position)
    
    def set_line_position(self, y):
        """Set counting line Y-coordinate"""
        self.line_y = y
        utils.log_event("INFO", f"Counting line set to Y={y}")


class SpeedEstimator:
    """Estimate vehicle speed based on pixel movement"""
    
    def __init__(self, pixels_per_meter=10, fps=30):
        """
        Initialize speed estimator
        
        Args:
            pixels_per_meter: Calibration factor
            fps: Frame rate
        """
        self.pixels_per_meter = pixels_per_meter
        self.fps = fps
        self.track_speeds = {}
    
    def calculate_speed(self, track_id, previous_pos, current_pos):
        """
        Calculate speed for a track
        
        Args:
            track_id: Track ID
            previous_pos: Previous position (x, y)
            current_pos: Current position (x, y)
        
        Returns:
            Speed in km/h
        """
        # Calculate distance in pixels
        distance_pixels = np.sqrt(
            (current_pos[0] - previous_pos[0]) ** 2 +
            (current_pos[1] - previous_pos[1]) ** 2
        )
        
        # Convert to meters
        distance_meters = distance_pixels / self.pixels_per_meter
        
        # Calculate speed (distance per frame to km/h)
        speed_mps = distance_meters * self.fps  # meters per second
        speed_kmh = speed_mps * 3.6  # km/h
        
        self.track_speeds[track_id] = speed_kmh
        
        return speed_kmh
    
    def get_speed(self, track_id):
        """Get speed for a track"""
        return self.track_speeds.get(track_id, 0.0)


# Test function
if __name__ == "__main__":
    print("Testing Vehicle Tracker...")
    
    # Initialize tracker
    tracker = VehicleTracker()
    
    # Initialize counter
    counter = VehicleCounter(line_y=400)
    
    print(f"Counting line at Y={counter.line_y}")
    print(f"Initial counts: {counter.get_counts()}")
    
    # Test counting
    counter.update_count(1, 'car')
    counter.update_count(2, 'motorcycle')
    counter.update_count(3, 'bus')
    
    print(f"After counting: {counter.get_counts()}")
    
    print("✓ Tracker test completed!")
