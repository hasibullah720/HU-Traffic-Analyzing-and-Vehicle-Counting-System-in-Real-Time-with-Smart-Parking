"""
Vehicle Counting Module for HU Traffic Analyzing System
Counts vehicles crossing detection zones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from scripts import config
import utils


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
    print("Testing Vehicle Counter...")
    
    # Initialize counter
    counter = VehicleCounter(line_y=400)
    
    print(f"Counting line at Y={counter.line_y}")
    print(f"Initial counts: {counter.get_counts()}")
    
    # Test counting
    counter.update_count(1, 'car')
    counter.update_count(2, 'motorcycle')
    counter.update_count(3, 'bus')
    
    print(f"After counting: {counter.get_counts()}")
    
    print("✓ Counter test completed!")
