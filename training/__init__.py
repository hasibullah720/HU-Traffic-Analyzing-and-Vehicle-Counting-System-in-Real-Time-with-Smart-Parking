"""
Training module for YOLOv8 vehicle detection
"""

__version__ = '1.0.0'

from .train_yolo import VehicleDetectionTrainer
from .prepare_dataset import DatasetPreparer
from .validate_model import ModelValidator
from .inference_video import VideoInference

__all__ = [
    'VehicleDetectionTrainer',
    'DatasetPreparer',
    'ModelValidator',
    'VideoInference'
]
