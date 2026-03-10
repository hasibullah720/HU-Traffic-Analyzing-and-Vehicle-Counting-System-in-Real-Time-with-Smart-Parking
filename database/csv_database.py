"""
CSV Database Manager for HU Traffic System
Manages traffic logs and rental records using CSV files
"""

import csv
import os
from datetime import datetime


class CSVDatabase:
    """Manages data storage using CSV files"""
    
    def __init__(self, database_path='database'):
        """
        Initialize CSV database manager
        
        Args:
            database_path: Path to database folder
        """
        self.database_path = database_path
        self.traffic_logs_file = os.path.join(database_path, 'traffic_logs.csv')
        self.rental_records_file = os.path.join(database_path, 'rental_records.csv')
        
        # Create database folder if not exists
        os.makedirs(database_path, exist_ok=True)
        
        # Initialize CSV files
        self.initialize_files()
    
    def initialize_files(self):
        """Create CSV files with headers if they don't exist"""
        # Traffic logs headers
        traffic_headers = [
            'timestamp', 'track_id', 'vehicle_type', 'confidence', 'action'
        ]
        
        if not os.path.exists(self.traffic_logs_file):
            with open(self.traffic_logs_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(traffic_headers)
            print(f"✓ Created traffic logs: {self.traffic_logs_file}")
        
        # Rental records headers
        rental_headers = [
            'rental_id', 'track_id', 'vehicle_type', 'entry_time', 'exit_time',
            'duration_minutes', 'base_rent', 'discount', 'total_rent', 'parking_slot'
        ]
        
        if not os.path.exists(self.rental_records_file):
            with open(self.rental_records_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(rental_headers)
            print(f"✓ Created rental records: {self.rental_records_file}")
    
    def log_traffic_event(self, track_id, vehicle_type, confidence, action='detected'):
        """
        Log a traffic event
        
        Args:
            track_id: Vehicle tracking ID
            vehicle_type: Type of vehicle
            confidence: Detection confidence
            action: Action type (detected, counted, entered, exited)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(self.traffic_logs_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    track_id,
                    vehicle_type,
                    f"{confidence:.2f}",
                    action
                ])
            return True
        except Exception as e:
            print(f"✗ Error logging traffic event: {e}")
            return False
    
    def add_rental_record(self, rental_data):
        """
        Add a rental record
        
        Args:
            rental_data: Dictionary with rental information
        """
        try:
            # Generate rental ID
            rental_id = self.get_next_rental_id()
            
            with open(self.rental_records_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    rental_id,
                    rental_data.get('track_id', ''),
                    rental_data.get('vehicle_type', ''),
                    rental_data.get('entry_time', ''),
                    rental_data.get('exit_time', ''),
                    rental_data.get('duration_minutes', 0),
                    rental_data.get('base_rent', 0),
                    rental_data.get('discount', 0),
                    rental_data.get('total_rent', 0),
                    rental_data.get('parking_slot', '')
                ])
            
            print(f"✓ Rental record added: ID-{rental_id}")
            return rental_id
        except Exception as e:
            print(f"✗ Error adding rental record: {e}")
            return None
    
    def get_next_rental_id(self):
        """Get next available rental ID"""
        try:
            with open(self.rental_records_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                rows = list(reader)
                if rows:
                    last_id = int(rows[-1][0])
                    return last_id + 1
                return 1
        except:
            return 1
    
    def get_traffic_logs(self, limit=100):
        """
        Get recent traffic logs
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of traffic log dictionaries
        """
        logs = []
        try:
            with open(self.traffic_logs_file, 'r') as f:
                reader = csv.DictReader(f)
                logs = list(reader)
                if limit:
                    logs = logs[-limit:]
        except Exception as e:
            print(f"✗ Error reading traffic logs: {e}")
        
        return logs
    
    def get_rental_records(self, limit=100):
        """
        Get recent rental records
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of rental record dictionaries
        """
        records = []
        try:
            with open(self.rental_records_file, 'r') as f:
                reader = csv.DictReader(f)
                records = list(reader)
                if limit:
                    records = records[-limit:]
        except Exception as e:
            print(f"✗ Error reading rental records: {e}")
        
        return records
    
    def get_today_stats(self):
        """Get today's statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Count vehicles by type
        vehicle_counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0,
            'total': 0
        }
        
        try:
            with open(self.traffic_logs_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['timestamp'].startswith(today) and row['action'] == 'counted':
                        vehicle_type = row['vehicle_type'].lower()
                        if vehicle_type in vehicle_counts:
                            vehicle_counts[vehicle_type] += 1
                            vehicle_counts['total'] += 1
        except Exception as e:
            print(f"✗ Error getting today's stats: {e}")
        
        return vehicle_counts
    
    def get_total_revenue(self):
        """Calculate total revenue from rental records"""
        total_revenue = 0.0
        
        try:
            with open(self.rental_records_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_revenue += float(row.get('total_rent', 0))
        except Exception as e:
            print(f"✗ Error calculating revenue: {e}")
        
        return total_revenue
    
    def close(self):
        """Close database (cleanup if needed)"""
        print("✓ CSV Database closed")


# Test function
if __name__ == "__main__":
    print("Testing CSV Database...")
    
    # Initialize database
    db = CSVDatabase()
    
    # Log traffic event
    db.log_traffic_event(1, 'car', 0.95, 'detected')
    db.log_traffic_event(2, 'motorcycle', 0.88, 'counted')
    
    # Add rental record
    rental = {
        'track_id': 1,
        'vehicle_type': 'car',
        'entry_time': '2026-03-06 10:00:00',
        'exit_time': '2026-03-06 14:00:00',
        'duration_minutes': 240,
        'base_rent': 400,
        'discount': 80,
        'total_rent': 320,
        'parking_slot': 'P-045'
    }
    db.add_rental_record(rental)
    
    # Get stats
    print(f"Today's stats: {db.get_today_stats()}")
    print(f"Total revenue: {db.get_total_revenue()} PKR")
    
    print("✓ CSV Database test completed!")
