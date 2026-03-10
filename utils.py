"""
Utility Functions for HU Traffic Analyzing System
Helper functions for drawing, colors, and geometric calculations
"""

import cv2
import numpy as np
from scripts import config


def get_vehicle_color(vehicle_class):
    """
    Get color for vehicle class
    
    Args:
        vehicle_class: Type of vehicle (car, motorcycle, bus, truck, van)
    
    Returns:
        BGR color tuple
    """
    color_map = {
        'car': config.COLOR_CAR,
        'motorcycle': config.COLOR_BIKE,
        'bus': config.COLOR_BUS,
        'truck': config.COLOR_TRUCK,
        'van': config.COLOR_VAN
    }
    
    return color_map.get(vehicle_class.lower(), (255, 255, 255))  # Default white


def get_bottom_center(bbox):
    """
    Get bottom center point of bounding box
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
    
    Returns:
        Tuple (x, y) of bottom center point
    """
    x1, y1, x2, y2 = bbox
    center_x = int((x1 + x2) / 2)
    bottom_y = int(y2)
    return (center_x, bottom_y)


def get_center(bbox):
    """
    Get center point of bounding box
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
    
    Returns:
        Tuple (x, y) of center point
    """
    x1, y1, x2, y2 = bbox
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    return (center_x, center_y)


def draw_detection_box(frame, bbox, label, color, confidence=None, thickness=2):
    """
    Draw bounding box with label and confidence on frame
    
    Args:
        frame: Input frame
        bbox: Bounding box (x1, y1, x2, y2)
        label: Text label to display
        color: BGR color tuple
        confidence: Confidence score (optional)
        thickness: Line thickness
    
    Returns:
        Annotated frame
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Draw rectangle
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # Prepare label with confidence
    if confidence is not None:
        display_text = f"{label} {confidence:.2f}"
    else:
        display_text = label
    
    # Prepare label background
    label_size, _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    label_w, label_h = label_size
    
    # Draw label background
    cv2.rectangle(
        frame,
        (x1, y1 - label_h - 10),
        (x1 + label_w + 10, y1),
        color,
        -1
    )
    
    # Draw label text
    cv2.putText(
        frame,
        display_text,
        (x1 + 5, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )
    
    return frame


def draw_text(frame, text, position, font_scale=0.6, color=(255, 255, 255), thickness=2):
    """
    Draw text on frame with background
    
    Args:
        frame: Input frame
        text: Text to display
        position: (x, y) position
        font_scale: Font scale
        color: Text color (BGR)
        thickness: Text thickness
    
    Returns:
        Annotated frame
    """
    x, y = position
    
    # Get text size
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    text_w, text_h = text_size
    
    # Draw background
    cv2.rectangle(
        frame,
        (x - 5, y - text_h - 5),
        (x + text_w + 5, y + 5),
        (0, 0, 0),
        -1
    )
    
    # Draw text
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA
    )
    
    return frame


def draw_line(frame, y_position, color=None, thickness=None):
    """
    Draw horizontal line across frame
    
    Args:
        frame: Input frame
        y_position: Y coordinate for line
        color: Line color (default: config.COLOR_LINE)
        thickness: Line thickness (default: config.LINE_THICKNESS)
    
    Returns:
        Frame with line drawn
    """
    if color is None:
        color = config.COLOR_LINE
    
    if thickness is None:
        thickness = config.LINE_THICKNESS
    
    height, width = frame.shape[:2]
    cv2.line(frame, (0, y_position), (width, y_position), color, thickness)
    
    return frame


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
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union


def resize_frame(frame, target_size):
    """
    Resize frame to target size
    
    Args:
        frame: Input frame
        target_size: Tuple (width, height)
    
    Returns:
        Resized frame
    """
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)


def format_time(seconds):
    """
    Format seconds to HH:MM:SS
    
    Args:
        seconds: Number of seconds
    
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_currency(amount):
    """
    Format amount as currency (PKR)
    
    Args:
        amount: Numeric amount
    
    Returns:
        Formatted currency string
    """
    return f"Rs. {amount:,.2f}"


def validate_bbox(bbox, frame_shape):
    """
    Validate and clamp bounding box to frame boundaries
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        frame_shape: Frame shape (height, width, channels)
    
    Returns:
        Valid bounding box
    """
    height, width = frame_shape[:2]
    x1, y1, x2, y2 = bbox
    
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))
    
    return (x1, y1, x2, y2)


def draw_fps(frame, fps, position=(10, 30)):
    """
    Draw FPS counter on frame
    
    Args:
        frame: Input frame
        fps: FPS value
        position: Text position (x, y)
    
    Returns:
        Annotated frame
    """
    fps_text = f"FPS: {fps:.1f}"
    return draw_text(frame, fps_text, position, color=(0, 255, 0))


def point_in_polygon(point, polygon):
    """
    Check if point is inside polygon
    
    Args:
        point: Tuple (x, y)
        polygon: List of points [(x1,y1), (x2,y2), ...]
    
    Returns:
        Boolean indicating if point is inside
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def calculate_distance(point1, point2):
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: Tuple (x1, y1)
        point2: Tuple (x2, y2)
    
    Returns:
        Distance value
    """
    x1, y1 = point1
    x2, y2 = point2
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def normalize_vehicle_type(vehicle_class):
    """
    Normalize vehicle type to standard format
    
    Args:
        vehicle_class: Vehicle type string
    
    Returns:
        Normalized vehicle type
    """
    vehicle_class = vehicle_class.lower().strip()
    
    # Map variations to standard types
    type_map = {
        'bike': 'motorcycle',
        'motorbike': 'motorcycle',
        'cycle': 'motorcycle',
        'van': 'car',
        'sedan': 'car',
        'suv': 'car',
        'lorry': 'truck',
        'semi': 'truck',
        'trailer': 'truck'
    }
    
    return type_map.get(vehicle_class, vehicle_class)


def log_event(event_type, message):
    """
    Log system event (console output)
    
    Args:
        event_type: Type of event (INFO, COUNT, ERROR, etc.)
        message: Event message
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {event_type}: {message}")


def draw_counting_line(frame, y_position, color=None, thickness=None):
    """
    Draw counting line with label
    
    Args:
        frame: Input frame
        y_position: Y coordinate for line
        color: Line color (default: config.COLOR_LINE)
        thickness: Line thickness (default: config.LINE_THICKNESS)
    
    Returns:
        Frame with counting line
    """
    if color is None:
        color = config.COLOR_LINE
    
    if thickness is None:
        thickness = config.LINE_THICKNESS
    
    height, width = frame.shape[:2]
    
    # Draw line
    cv2.line(frame, (0, y_position), (width, y_position), color, thickness)
    
    # Draw label
    label = "COUNTING LINE"
    cv2.putText(
        frame,
        label,
        (width // 2 - 80, y_position - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
        cv2.LINE_AA
    )
    
    return frame


def draw_info_panel(frame, info_text, position=(10, 30), bg_color=(0, 0, 0), text_color=(255, 255, 255)):
    """
    Draw information panel with multiple lines
    
    Args:
        frame: Input frame
        info_text: List of text lines
        position: Starting position (x, y)
        bg_color: Background color (BGR)
        text_color: Text color (BGR)
    
    Returns:
        Frame with info panel
    """
    x, y = position
    line_height = 25
    padding = 10
    
    # Calculate panel size
    max_width = 0
    for text in info_text:
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        max_width = max(max_width, text_size[0])
    
    panel_width = max_width + 2 * padding
    panel_height = len(info_text) * line_height + padding
    
    # Draw background panel
    cv2.rectangle(
        frame,
        (x - padding, y - 20),
        (x + panel_width, y + panel_height - 20),
        bg_color,
        -1
    )
    
    # Draw semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x - padding, y - 20),
        (x + panel_width, y + panel_height - 20),
        bg_color,
        -1
    )
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Draw text lines
    for i, text in enumerate(info_text):
        text_y = y + i * line_height
        cv2.putText(
            frame,
            text,
            (x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            text_color,
            1,
            cv2.LINE_AA
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
