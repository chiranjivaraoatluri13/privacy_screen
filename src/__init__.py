"""
Camera Access Privacy Protection System - Stage 1
"""

from .camera import CameraStream
from .detector import FaceDetector
from .decision import PrivacyDecisionEngine
from .render import PrivacyRenderer
from .config import Config

__version__ = "1.0.0-stage1"
__all__ = [
    'CameraStream',
    'FaceDetector',
    'PrivacyDecisionEngine',
    'PrivacyRenderer',
    'Config',
]
