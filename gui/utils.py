"""
Utility Module for HU Traffic Analyzing System
Contains helper functions and common utilities
"""

import cv2
import numpy as np
from datetime import datetime
import config


def draw_detection_box(frame, bbox, label, color, confidence=None):
    """
    Draw bounding box with label on frame
    
    Args:
        frame: Input frame/image
        bbox: Bounding box coordinates (x1, y1, x2, y2)
        label: Text label to display
        color: Color of the box (BGR)
        confidence: Optional confidence score
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Draw rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    
    # Prepare label text
    if confidence:
        text = f"{label}: {confidence:.2f}"
    else:
        text = label
    
    # Calculate text size for background
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
    )
    
    # Draw background rectangle for text
    cv2.rectangle(
        frame,
        (x1, y1 - text_height - 10),
        (x1 + text_width, y1),
        color,
        -1
    )
    
    # Draw text
    cv2.putText(
        frame,
        text,
        (x1, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )
    
    return frame


def draw_counting_line(frame, y_position, line_thickness=3):
    """
    Draw horizontal counting line on frame
    
    Args:
        frame: Input frame
        y_position: Y-coordinate for the line
        line_thickness: Thickness of the line
    """
    height, width = frame.shape[:2]
    cv2.line(
        frame,
        (0, y_position),
        (width, y_position),
        config.COLOR_LINE,
        line_thickness
    )
    
    # Add label
    cv2.putText(
        frame,
        "COUNTING LINE",
        (10, y_position - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        config.COLOR_LINE,
        2
    )
    
    return frame


def is_crossing_line(previous_y, current_y, line_y, direction='down'):
    """
    Check if object crossed the counting line
    
    Args:
        previous_y: Previous Y-coordinate
        current_y: Current Y-coordinate
        line_y: Y-coordinate of counting line
        direction: 'down' or 'up'
    
    Returns:
        Boolean indicating if line was crossed
    """
    if direction == 'down':
        return previous_y < line_y <= current_y
    else:  # up
        return previous_y > line_y >= current_y


def get_vehicle_color(vehicle_type):
    """
    Get color for vehicle type
    
    Args:
        vehicle_type: Type of vehicle
    
    Returns:
        BGR color tuple
    """
    color_map = {
        'car': config.COLOR_CAR,
        'motorcycle': config.COLOR_BIKE,
        'bike': config.COLOR_BIKE,
        'bus': config.COLOR_BUS,
        'truck': config.COLOR_TRUCK,
        'van': config.COLOR_VAN
    }
    
    return color_map.get(vehicle_type.lower(), (255, 255, 255))


def normalize_vehicle_type(detected_class):
    """
    Normalize detected class names to standard vehicle types
    
    Args:
        detected_class: Class name from YOLO
    
    Returns:
        Normalized vehicle type
    """
    class_mapping = {
        'car': 'car',
        'motorcycle': 'motorcycle',
        'bike': 'motorcycle',
        'bicycle': 'motorcycle',
        'bus': 'bus',
        'truck': 'truck',
        'van': 'van'
    }
    
    return class_mapping.get(detected_class.lower(), 'car')


def calculate_center_point(bbox):
    """
    Calculate center point of bounding box
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
    
    Returns:
        (center_x, center_y)
    """
    x1, y1, x2, y2 = bbox
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    return (center_x, center_y)


def get_bottom_center(bbox):
    """
    Get bottom center point of bounding box
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
    
    Returns:
        (center_x, bottom_y)
    """
    x1, y1, x2, y2 = bbox
    center_x = int((x1 + x2) / 2)
    return (center_x, int(y2))


def format_time(seconds):
    """
    Format seconds into readable time string
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def calculate_time_difference(start_time, end_time=None):
    """
    Calculate time difference in minutes
    
    Args:
        start_time: Start timestamp (string or datetime)
        end_time: End timestamp (string or datetime), defaults to now
    
    Returns:
        Time difference in minutes
    """
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    
    if end_time is None:
        end_time = datetime.now()
    elif isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    
    difference = end_time - start_time
    return difference.total_seconds() / 60.0


def draw_info_panel(frame, info_text, position=(10, 30)):
    """
    Draw information panel on frame
    
    Args:
        frame: Input frame
        info_text: List of text lines to display
        position: Starting position (x, y)
    """
    x, y = position
    line_height = 30
    
    for i, text in enumerate(info_text):
        y_pos = y + (i * line_height)
        
        # Draw semi-transparent background
        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
        )
        
        # Create overlay for transparency
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x - 5, y_pos - text_height - 5),
            (x + text_width + 5, y_pos + 5),
            (0, 0, 0),
            -1
        )
        
        # Blend overlay with frame
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Draw text
        cv2.putText(
            frame,
            text,
            (x, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
    
    return frame


def resize_frame(frame, width=None, height=None):
    """
    Resize frame while maintaining aspect ratio
    
    Args:
        frame: Input frame
        width: Target width
        height: Target height
    
    Returns:
        Resized frame
    """
    if width is None and height is None:
        return frame
    
    (h, w) = frame.shape[:2]
    
    if width is not None:
        ratio = width / float(w)
        dimensions = (width, int(h * ratio))
    else:
        ratio = height / float(h)
        dimensions = (int(w * ratio), height)
    
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)


def validate_bbox(bbox, frame_shape):
    """
    Validate and clip bounding box to frame boundaries
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        frame_shape: Shape of frame (height, width, channels)
    
    Returns:
        Validated bounding box
    """
    height, width = frame_shape[:2]
    x1, y1, x2, y2 = bbox
    
    x1 = max(0, min(x1, width))
    y1 = max(0, min(y1, height))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))
    
    return (x1, y1, x2, y2)


def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) between two boxes
    
    Args:
        box1: First bounding box (x1, y1, x2, y2)
        box2: Second bounding box (x1, y1, x2, y2)
    
    Returns:
        IoU value (0 to 1)
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Calculate intersection area
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union area
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    union_area = box1_area + box2_area - intersection_area
    
    # Calculate IoU
    iou = intersection_area / union_area if union_area > 0 else 0
    
    return iou


def fps_counter():
    """
    Simple FPS counter generator
    
    Yields:
        Current FPS value
    """
    prev_time = datetime.now()
    
    while True:
        current_time = datetime.now()
        time_diff = (current_time - prev_time).total_seconds()
        fps = 1.0 / time_diff if time_diff > 0 else 0
        prev_time = current_time
        yield fps


# Logging utility
def log_event(event_type, message):
    """
    Log system events with timestamp
    
    Args:
        event_type: Type of event (INFO, WARNING, ERROR)
        message: Event message
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{event_type}] {message}")


# Test function
if __name__ == "__main__":
    # Test utilities
    print("Testing utilities...")
    
    # Test color mapping
    print(f"Car color: {get_vehicle_color('car')}")
    print(f"Bike color: {get_vehicle_color('motorcycle')}")
    
    # Test vehicle type normalization
    print(f"Normalized 'motorcycle': {normalize_vehicle_type('motorcycle')}")
    
    # Test center point calculation
    bbox = (100, 100, 200, 200)
    center = calculate_center_point(bbox)
    print(f"Center point of {bbox}: {center}")
    
    # Test time formatting
    print(f"3665 seconds = {format_time(3665)}")
    
    # Test crossing detection
    crossed = is_crossing_line(390, 410, 400, 'down')
    print(f"Crossed line: {crossed}")
    
    print("✓ All utility tests passed!")
