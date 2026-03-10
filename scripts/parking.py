"""
Smart Parking Management System Module
Manages parking slots and vehicle assignments
"""

import cv2
import numpy as np
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import config
import utils


class ParkingSlot:
    """Represents a single parking slot"""
    
    def __init__(self, slot_id, position=None):
        """
        Initialize parking slot
        
        Args:
            slot_id: Unique slot identifier (e.g., 'P1', 'P2')
            position: Position coordinates (x, y, width, height) for visual representation
        """
        self.slot_id = slot_id
        self.status = 'Free'  # 'Free' or 'Occupied'
        self.vehicle_type = None
        self.track_id = None
        self.entry_time = None
        self.position = position  # For visualization
    
    def occupy(self, vehicle_type, track_id):
        """
        Mark slot as occupied
        
        Args:
            vehicle_type: Type of vehicle
            track_id: Tracking ID of vehicle
        """
        self.status = 'Occupied'
        self.vehicle_type = vehicle_type
        self.track_id = track_id
        self.entry_time = datetime.now()
        return True
    
    def free(self):
        """Mark slot as free"""
        self.status = 'Free'
        self.vehicle_type = None
        self.track_id = None
        self.entry_time = None
        return True
    
    def get_duration(self):
        """Get parking duration in minutes"""
        if self.entry_time is None:
            return 0
        
        duration = datetime.now() - self.entry_time
        return duration.total_seconds() / 60.0
    
    def is_occupied(self):
        """Check if slot is occupied"""
        return self.status == 'Occupied'
    
    def is_free(self):
        """Check if slot is free"""
        return self.status == 'Free'
    
    def get_info(self):
        """Get slot information"""
        return {
            'slot_id': self.slot_id,
            'status': self.status,
            'vehicle_type': self.vehicle_type,
            'track_id': self.track_id,
            'entry_time': self.entry_time,
            'duration': self.get_duration() if self.is_occupied() else 0
        }


class ParkingManager:
    """Manages multiple parking slots"""
    
    def __init__(self, database_manager, total_slots=None):
        """
        Initialize parking manager
        
        Args:
            database_manager: Database manager instance
            total_slots: Total number of parking slots
        """
        self.db = database_manager
        self.total_slots = total_slots or config.TOTAL_PARKING_SLOTS
        self.slots = {}
        self.vehicle_to_slot = {}  # Map track_id to slot_id
        
        self.initialize_slots()
    
    def initialize_slots(self):
        """Initialize all parking slots"""
        for i in range(self.total_slots):
            slot_id = f"P{i + 1}"
            self.slots[slot_id] = ParkingSlot(slot_id)
        
        utils.log_event("INFO", f"Initialized {self.total_slots} parking slots")
    
    def get_available_slot(self):
        """
        Get first available parking slot
        
        Returns:
            Slot ID or None if no slots available
        """
        for slot_id, slot in self.slots.items():
            if slot.is_free():
                return slot_id
        return None
    
    def assign_slot(self, track_id, vehicle_type):
        """
        Assign a parking slot to a vehicle
        
        Args:
            track_id: Vehicle tracking ID
            vehicle_type: Type of vehicle
        
        Returns:
            Assigned slot ID or None
        """
        # Check if vehicle already has a slot
        if track_id in self.vehicle_to_slot:
            return self.vehicle_to_slot[track_id]
        
        # Get available slot
        slot_id = self.get_available_slot()
        
        if slot_id is None:
            utils.log_event("WARNING", "No parking slots available")
            return None
        
        # Assign slot
        slot = self.slots[slot_id]
        slot.occupy(vehicle_type, track_id)
        self.vehicle_to_slot[track_id] = slot_id
        
        # Update database
        self.db.occupy_parking_slot(slot_id, vehicle_type, track_id)
        
        utils.log_event("INFO", f"Assigned slot {slot_id} to vehicle {track_id} ({vehicle_type})")
        
        return slot_id
    
    def release_slot(self, track_id):
        """
        Release parking slot for a vehicle
        
        Args:
            track_id: Vehicle tracking ID
        
        Returns:
            Boolean indicating success
        """
        if track_id not in self.vehicle_to_slot:
            return False
        
        slot_id = self.vehicle_to_slot[track_id]
        slot = self.slots[slot_id]
        
        # Get duration before freeing
        duration = slot.get_duration()
        
        # Free the slot
        slot.free()
        del self.vehicle_to_slot[track_id]
        
        # Update database
        self.db.free_parking_slot(slot_id)
        
        utils.log_event("INFO", f"Released slot {slot_id} from vehicle {track_id} (Duration: {duration:.1f} min)")
        
        return True
    
    def get_slot_by_track_id(self, track_id):
        """
        Get slot ID for a vehicle
        
        Args:
            track_id: Vehicle tracking ID
        
        Returns:
            Slot ID or None
        """
        return self.vehicle_to_slot.get(track_id, None)
    
    def get_slot_info(self, slot_id):
        """
        Get information about a specific slot
        
        Args:
            slot_id: Slot identifier
        
        Returns:
            Slot information dictionary
        """
        if slot_id not in self.slots:
            return None
        
        return self.slots[slot_id].get_info()
    
    def get_parking_statistics(self):
        """
        Get overall parking statistics
        
        Returns:
            Dictionary with statistics
        """
        occupied_count = sum(1 for slot in self.slots.values() if slot.is_occupied())
        free_count = self.total_slots - occupied_count
        occupancy_rate = (occupied_count / self.total_slots) * 100 if self.total_slots > 0 else 0
        
        # Count by vehicle type
        vehicle_types = {}
        for slot in self.slots.values():
            if slot.is_occupied() and slot.vehicle_type:
                vehicle_types[slot.vehicle_type] = vehicle_types.get(slot.vehicle_type, 0) + 1
        
        return {
            'total': self.total_slots,
            'occupied': occupied_count,
            'free': free_count,
            'occupancy_rate': occupancy_rate,
            'by_vehicle_type': vehicle_types
        }
    
    def get_occupied_slots(self):
        """Get list of occupied slots"""
        return [
            slot.get_info()
            for slot in self.slots.values()
            if slot.is_occupied()
        ]
    
    def get_free_slots(self):
        """Get list of free slots"""
        return [
            slot_id
            for slot_id, slot in self.slots.items()
            if slot.is_free()
        ]
    
    def is_parking_full(self):
        """Check if parking is full"""
        return self.get_available_slot() is None
    
    def get_long_parked_vehicles(self, duration_minutes=60):
        """
        Get vehicles parked longer than specified duration
        
        Args:
            duration_minutes: Duration threshold in minutes
        
        Returns:
            List of slot information
        """
        long_parked = []
        
        for slot in self.slots.values():
            if slot.is_occupied():
                if slot.get_duration() >= duration_minutes:
                    long_parked.append(slot.get_info())
        
        return long_parked


class ParkingZone:
    """Defines a parking zone area in the video frame"""
    
    def __init__(self, zone_id, points):
        """
        Initialize parking zone
        
        Args:
            zone_id: Zone identifier
            points: Polygon points defining the zone [(x1,y1), (x2,y2), ...]
        """
        self.zone_id = zone_id
        self.points = np.array(points, dtype=np.int32)
        self.vehicles_in_zone = set()
        self.entry_line = None
        self.exit_line = None
    
    def is_point_in_zone(self, point):
        """
        Check if point is inside zone
        
        Args:
            point: Point (x, y)
        
        Returns:
            Boolean
        """
        result = cv2.pointPolygonTest(self.points, point, False)
        return result >= 0
    
    def is_vehicle_in_zone(self, bbox):
        """
        Check if vehicle is in zone (using bottom center point)
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
        
        Returns:
            Boolean
        """
        center = utils.get_bottom_center(bbox)
        return self.is_point_in_zone(center)
    
    def add_vehicle(self, track_id):
        """Add vehicle to zone"""
        self.vehicles_in_zone.add(track_id)
    
    def remove_vehicle(self, track_id):
        """Remove vehicle from zone"""
        if track_id in self.vehicles_in_zone:
            self.vehicles_in_zone.remove(track_id)
    
    def get_vehicle_count(self):
        """Get number of vehicles in zone"""
        return len(self.vehicles_in_zone)
    
    def draw_zone(self, frame, color=(0, 255, 0), thickness=2):
        """
        Draw zone on frame
        
        Args:
            frame: Input frame
            color: Zone boundary color
            thickness: Line thickness
        """
        cv2.polylines(frame, [self.points], True, color, thickness)
        
        # Draw zone label
        centroid = np.mean(self.points, axis=0).astype(int)
        cv2.putText(
            frame,
            f"{self.zone_id} ({self.get_vehicle_count()})",
            tuple(centroid),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )
        
        return frame


class ParkingVisualizer:
    """Visualize parking status"""
    
    def __init__(self, parking_manager):
        """
        Initialize visualizer
        
        Args:
            parking_manager: ParkingManager instance
        """
        self.parking_manager = parking_manager
    
    def draw_parking_status(self, frame, position=(10, 30)):
        """
        Draw parking status on frame
        
        Args:
            frame: Input frame
            position: Starting position
        
        Returns:
            Annotated frame
        """
        stats = self.parking_manager.get_parking_statistics()
        
        info_text = [
            "=== PARKING STATUS ===",
            f"Total: {stats['total']}",
            f"Occupied: {stats['occupied']}",
            f"Available: {stats['free']}",
            f"Occupancy: {stats['occupancy_rate']:.1f}%"
        ]
        
        if stats['by_vehicle_type']:
            info_text.append("--- By Type ---")
            for vtype, count in stats['by_vehicle_type'].items():
                info_text.append(f"{vtype.capitalize()}: {count}")
        
        return utils.draw_info_panel(frame, info_text, position)
    
    def create_parking_grid_view(self, width=400, height=300):
        """
        Create a visual grid representation of parking slots
        
        Args:
            width: Grid width
            height: Grid height
        
        Returns:
            Grid image
        """
        grid = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        stats = self.parking_manager.get_parking_statistics()
        
        # Draw title
        cv2.putText(
            grid,
            "Parking Grid",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2
        )
        
        # Draw stats
        cv2.putText(
            grid,
            f"Occupied: {stats['occupied']} / {stats['total']}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1
        )
        
        # Draw simple grid of slots
        slots_per_row = 10
        slot_width = 35
        slot_height = 25
        margin = 5
        start_y = 80
        
        for i in range(min(50, stats['total'])):  # Show first 50 slots
            row = i // slots_per_row
            col = i % slots_per_row
            
            x = margin + col * (slot_width + margin)
            y = start_y + row * (slot_height + margin)
            
            slot_id = f"P{i + 1}"
            slot_info = self.parking_manager.get_slot_info(slot_id)
            
            if slot_info and slot_info['status'] == 'Occupied':
                color = (0, 0, 255)  # Red for occupied
            else:
                color = (0, 255, 0)  # Green for free
            
            cv2.rectangle(grid, (x, y), (x + slot_width, y + slot_height), color, -1)
            cv2.rectangle(grid, (x, y), (x + slot_width, y + slot_height), (0, 0, 0), 1)
        
        return grid


# Test function
if __name__ == "__main__":
    print("Testing Parking Management System...")
    
    # Import database for testing
    from database import DatabaseManager
    
    db = DatabaseManager("test_parking.db")
    parking_manager = ParkingManager(db, total_slots=20)
    
    # Test slot assignment
    slot1 = parking_manager.assign_slot(1, 'car')
    print(f"Assigned slot: {slot1}")
    
    slot2 = parking_manager.assign_slot(2, 'motorcycle')
    print(f"Assigned slot: {slot2}")
    
    # Get statistics
    stats = parking_manager.get_parking_statistics()
    print(f"Parking statistics: {stats}")
    
    # Release slot
    parking_manager.release_slot(1)
    
    stats = parking_manager.get_parking_statistics()
    print(f"After release: {stats}")
    
    db.close()
    
    print("✓ Parking system test completed!")
