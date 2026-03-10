"""
HU Traffic Analyzing and Vehicle Counting System
Real-Time with Smart Parking and Vehicle Rental Management
Main Entry Point
"""

import sys
import os
import cv2
import tkinter as tk
from datetime import datetime
import threading
import time

# Add scripts and gui to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

# Import modules from reorganized structure
from scripts import config
from scripts.preprocessing import PreProcessor
from scripts.detection import VehicleDetector
from scripts.tracking import VehicleTracker
from scripts.counting import VehicleCounter
from scripts.parking import ParkingManager
from scripts.rental_system import RentalManager
from scripts.reports import ReportGenerator
from database.csv_database import CSVDatabase
from gui.main_gui import ModernDashboard


class TrafficSystem:
    """Main Traffic Monitoring System"""
    
    def __init__(self, video_source=None):
        """Initialize the system"""
        print("=" * 60)
        print(" " * 10 + "HU TRAFFIC ANALYZING SYSTEM")
        print(" " * 5 + "Real-Time Vehicle Counting & Management")
        print("=" * 60)
        
        self.video_source = video_source or config.VIDEO_SOURCE
        self.video_capture = None
        self.is_running = False
        self.frame_count = 0
        self.fps = 0
        self.fps_time = time.time()
        
        # GUI
        self.root = None
        self.dashboard = None
        
        # Initialize components
        self.init_components()
        
        print("✓ System ready!")
    
    def init_components(self):
        """Initialize all system components"""
        print("\nInitializing components...")
        
        # Database (CSV-based)
        self.database = CSVDatabase('database')
        
        # Pre-processing (optimized for speed)
        self.preprocessor = PreProcessor(target_size=config.PREPROCESS_TARGET_SIZE)
        
        # Detection & Tracking
        # Use custom model if configured
        use_custom = getattr(config, 'USE_CUSTOM_MODEL', False)
        self.detector = VehicleDetector(use_custom_model=use_custom)
        self.tracker = VehicleTracker(max_age=config.MAX_AGE)
        self.counter = VehicleCounter()
        
        # Parking & Rental
        self.parking_manager = ParkingManager(self.database)
        self.rental_manager = RentalManager(self.database)
        
        # Report Generator
        self.report_generator = ReportGenerator(self.database)
        
        print("✓ All components initialized!")
    
    def init_video(self):
        """Initialize video capture"""
        try:
            # Check if video source is selected
            if self.video_source is None or self.video_source == "NOT_SELECTED":
                raise Exception("No video source selected. Please select a video file or webcam.")
            
            self.video_capture = cv2.VideoCapture(self.video_source)
            
            if not self.video_capture.isOpened():
                if self.video_source == 0:
                    raise Exception("Cannot open webcam. Make sure your camera is connected and not used by another app.")
                else:
                    raise Exception(f"Cannot open video file: {self.video_source}\nMake sure the file exists and is a valid video format.")
            
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
            
            source_name = "Webcam" if self.video_source == 0 else str(self.video_source)
            print(f"✓ Video source opened: {source_name}")
            return True
            
        except Exception as e:
            print(f"✗ Video error: {e}")
            return False
    
    def process_frame(self, frame):
        """Process single frame with optimization"""
        # Pre-process frame (resize only, skip normalization for speed)
        processed_frame = self.preprocessor.resize(frame)
        
        # Robust frame skipping:
        # - Detect every FRAME_SKIP frame for speed
        # - But force detection until at least one confirmed track exists
        #   (prevents tentative tracks from being dropped before confirmation)
        needs_detection = (
            self.frame_count % config.FRAME_SKIP == 0
            or not self.tracker.has_confirmed_tracks()
        )

        if needs_detection:
            # Debug: Show when detection runs
            if self.frame_count % (config.FRAME_SKIP * 10) == 0:  # Print every 10 detection cycles
                print(f"[Frame {self.frame_count}] Running YOLO detection...")
            
            detections = self.detector.detect(processed_frame)
            
            # Debug: Show detection results occasionally
            if self.frame_count % (config.FRAME_SKIP * 10) == 0:
                print(f"[Frame {self.frame_count}] Found {len(detections)} vehicles")
            
            tracks = self.tracker.update(detections, processed_frame)
        else:
            tracks = self.tracker.update([], processed_frame)
        
        # Draw on frame
        result = self.tracker.draw_tracks(processed_frame, tracks)
        
        # Count vehicles crossing line
        result = self.counter.draw_counting_line(result)
        
        for track in tracks:
            if not track.get('is_confirmed', True):
                continue
            if self.tracker.check_line_crossing(
                track['track_id'], 
                track['bbox'], 
                self.counter.line_y
            ):
                self.counter.update_count(track['track_id'], track['class'])
                self.database.log_traffic_event(
                    track['track_id'],
                    track['class'],
                    track['confidence'],
                    'counted'
                )
        
        # Update stats
        self.frame_count += 1
        
        return result, tracks
    
    def video_loop(self):
        """Main video processing loop - runs continuously with Tkinter after()"""
        if not self.is_running:
            return
        
        try:
            ret, frame = self.video_capture.read()
            
            if not ret:
                print("✗ Cannot read frame or video ended")
                self.stop()
                return
            
            # Process frame
            processed, tracks = self.process_frame(frame)
            
            # Update GUI display every frame for smooth video
            if self.dashboard:
                self.dashboard.update_video_display(processed)
                
                # Update stats every 5th frame for performance
                if self.frame_count % 5 == 0:
                    # Cache counts to avoid multiple dictionary accesses
                    counts = self.counter.get_counts()
                    stats = {
                        'total_vehicles': counts['total'],
                        'car': counts['car'],
                        'motorcycle': counts['motorcycle'],
                        'bus': counts['bus'],
                        'truck': counts['truck'],
                        'parking_occupied': len([s for s in self.parking_manager.slots.values() if s.is_occupied()]),
                        'parking_available': len([s for s in self.parking_manager.slots.values() if s.is_free()]),
                        'parking_total': config.TOTAL_PARKING_SLOTS
                    }
                    
                    self.dashboard.update_statistics(stats)
                
                # Calculate FPS less frequently
                if self.frame_count % 30 == 0:
                    self.calculate_fps()
                    self.dashboard.update_fps(self.fps)
            
            # Schedule next frame - continuous loop using Tkinter after()
            # Use 1ms delay to allow GUI to remain responsive
            if self.root:
                self.root.after(1, self.video_loop)
                
        except Exception as e:
            print(f"✗ Error in video loop: {e}")
            self.stop()
    
    def calculate_fps(self):
        """Calculate FPS"""
        if self.frame_count % 30 == 0:
            current_time = time.time()
            elapsed = current_time - self.fps_time
            if elapsed > 0:
                self.fps = 30 / elapsed
                self.fps_time = current_time
    
    def start(self):
        """Start the system"""
        if self.is_running:
            print("System already running!")
            return True
            
        print("\nStarting system...")
        
        # Get video source from dashboard if available
        if self.dashboard:
            self.video_source = self.dashboard.get_video_source()
        
        # Check if video source is selected
        if self.video_source is None or self.video_source == "NOT_SELECTED":
            if self.dashboard:
                from tkinter import messagebox
                messagebox.showwarning(
                    "No Video Source", 
                    "Please select a video source first:\n\n"
                    "• Click 'Upload Video' to use a video file\n"
                    "• Click 'Use Webcam' to use your camera"
                )
                self.dashboard.stop_system()
            else:
                print("✗ No video source selected!")
            return False
        
        if not self.init_video():
            if self.dashboard:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Cannot open video source:\n{self.video_source}")
                self.dashboard.stop_system()
            return False
        
        self.is_running = True
        
        # Sync dashboard state
        if self.dashboard:
            self.dashboard.is_running = True
            self.dashboard.append_log("System started - Detection running...")
        
        # Start video loop using Tkinter after() - non-blocking, GUI-safe
        if self.root:
            self.root.after(10, self.video_loop)
        
        print("✓ System started!")
        return True
    
    def stop(self):
        """Stop the system"""
        if self.is_running:
            print("\nStopping system...")
            self.is_running = False
            
            if self.video_capture:
                self.video_capture.release()
            
            if self.dashboard:
                self.dashboard.is_running = False
                self.dashboard.append_log("System stopped")
            
            print("✓ System stopped!")
    
    def run_with_gui(self):
        """Run with GUI"""
        self.root = tk.Tk()
        self.dashboard = ModernDashboard(self.root)
        
        # Set components
        self.dashboard.detector = self.detector
        self.dashboard.tracker = self.tracker
        self.dashboard.parking_manager = self.parking_manager
        self.dashboard.rental_manager = self.rental_manager
        self.dashboard.database = self.database
        self.dashboard.counter = self.counter
        self.dashboard.preprocessor = self.preprocessor
        self.dashboard.report_generator = self.report_generator
        
        # Set callbacks
        self.dashboard.start_btn.config(command=self.start)
        self.dashboard.stop_btn.config(command=self.stop)
        
        print("\n✓ Starting GUI...")
        self.root.mainloop()
        
        # Cleanup
        self.stop()
        self.database.close()
    
    def run_console(self):
        """Run in console mode"""
        print("\n✓ Console mode")
        print("Press 'q' to quit, 's' for stats\n")
        
        if not self.init_video():
            return
        
        self.is_running = True
        
        try:
            while self.is_running:
                ret, frame = self.video_capture.read()
                
                if not ret:
                    break
                
                processed, _ = self.process_frame(frame)
                
                # Draw counts
                processed = self.counter.draw_counts(processed)
                
                cv2.imshow('HU Traffic System', processed)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    print(f"\nStats: {self.counter.get_counts()}")
        
        except KeyboardInterrupt:
            print("\n✗ Interrupted")
        
        finally:
            self.stop()
            cv2.destroyAllWindows()
            self.database.close()


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print(" " * 15 + "WELCOME TO")
    print(" " * 5 + "HU TRAFFIC ANALYZING & VEHICLE COUNTING SYSTEM")
    print(" " * 10 + "with Smart Parking & Rental Management")
    print("=" * 60 + "\n")
    
    print("Select mode:")
    print("1. GUI Dashboard (Recommended)")
    print("2. Console Mode")
    print("3. Use Video File")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    video_source = config.VIDEO_SOURCE
    
    if choice == '3':
        video_path = input("Enter video file path: ").strip()
        if video_path:
            video_source = video_path
    
    # Create system
    system = TrafficSystem(video_source=video_source)
    
    if choice == '2':
        system.run_console()
    else:
        system.run_with_gui()
    
    print("\n" + "=" * 60)
    print(" " * 15 + "Thank you!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
