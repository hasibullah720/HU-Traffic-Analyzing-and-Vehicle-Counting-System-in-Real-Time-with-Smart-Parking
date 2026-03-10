"""
Pre-Processing Module for Video Input
Resize and Normalize frames as per architecture
"""

import cv2
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import config


class PreProcessor:
    """Pre-process video frames before detection"""
    
    def __init__(self, target_size=(640, 640)):
        """
        Initialize pre-processor
        
        Args:
            target_size: Target size for resizing (width, height)
        """
        self.target_size = target_size
        self.original_size = None
    
    def resize(self, frame):
        """
        Resize frame to target size
        
        Args:
            frame: Input frame
        
        Returns:
            Resized frame
        """
        if frame is None:
            return None
        
        # Store original size for reverse transformation
        self.original_size = (frame.shape[1], frame.shape[0])
        
        # Resize frame
        resized = cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)
        
        return resized
    
    def normalize(self, frame):
        """
        Normalize frame pixel values
        
        Args:
            frame: Input frame
        
        Returns:
            Normalized frame
        """
        if frame is None:
            return None
        
        # Convert to float32
        normalized = frame.astype(np.float32)
        
        # Normalize to [0, 1]
        normalized = normalized / 255.0
        
        return normalized
    
    def denormalize(self, frame):
        """
        Denormalize frame back to uint8
        
        Args:
            frame: Normalized frame
        
        Returns:
            Denormalized frame
        """
        if frame is None:
            return None
        
        # Convert back to [0, 255]
        denormalized = (frame * 255.0).astype(np.uint8)
        
        return denormalized
    
    def process(self, frame, normalize=False):
        """
        Apply full pre-processing pipeline
        
        Args:
            frame: Input frame
            normalize: Whether to normalize pixel values
        
        Returns:
            Processed frame
        """
        if frame is None:
            return None
        
        # Resize frame
        processed = self.resize(frame)
        
        # Apply normalization if requested
        if normalize:
            processed = self.normalize(processed)
        
        return processed
    
    def scale_bbox(self, bbox):
        """
        Scale bounding box from resized to original coordinates
        
        Args:
            bbox: Bounding box in resized coordinates (x1, y1, x2, y2)
        
        Returns:
            Bounding box in original coordinates
        """
        if self.original_size is None:
            return bbox
        
        x1, y1, x2, y2 = bbox
        
        # Calculate scale factors
        scale_x = self.original_size[0] / self.target_size[0]
        scale_y = self.original_size[1] / self.target_size[1]
        
        # Scale coordinates
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)
        
        return (x1, y1, x2, y2)
    
    def enhance_contrast(self, frame):
        """
        Enhance frame contrast using CLAHE
        
        Args:
            frame: Input frame
        
        Returns:
            Enhanced frame
        """
        if frame is None:
            return None
        
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        enhanced = cv2.merge([l, a, b])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def reduce_noise(self, frame):
        """
        Reduce noise using bilateral filter
        
        Args:
            frame: Input frame
        
        Returns:
            Filtered frame
        """
        if frame is None:
            return None
        
        # Apply bilateral filter
        filtered = cv2.bilateralFilter(frame, 9, 75, 75)
        
        return filtered


# Test function
if __name__ == "__main__":
    print("Testing Pre-Processor...")
    
    # Initialize pre-processor
    preprocessor = PreProcessor(target_size=(640, 640))
    
    # Create dummy frame
    test_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    print(f"Original shape: {test_frame.shape}")
    
    # Process frame
    processed = preprocessor.process(test_frame)
    
    print(f"Processed shape: {processed.shape}")
    
    # Test bbox scaling
    bbox = (100, 100, 200, 200)
    scaled_bbox = preprocessor.scale_bbox(bbox)
    
    print(f"Original bbox: {bbox}")
    print(f"Scaled bbox: {scaled_bbox}")
    
    print("✓ Pre-processor test completed!")
