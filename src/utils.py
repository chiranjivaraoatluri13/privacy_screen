"""
Utility functions for geometry, conversions, and common operations.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class BoundingBox:
    """Normalized bounding box (0.0 to 1.0 range)."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    
    def to_pixel_coords(self, frame_width: int, frame_height: int) -> 'BoundingBox':
        """Convert normalized coordinates to pixel coordinates."""
        return BoundingBox(
            x_min=int(self.x_min * frame_width),
            y_min=int(self.y_min * frame_height),
            x_max=int(self.x_max * frame_width),
            y_max=int(self.y_max * frame_height)
        )
    
    def width(self) -> float:
        """Width in normalized coordinates."""
        return self.x_max - self.x_min
    
    def height(self) -> float:
        """Height in normalized coordinates."""
        return self.y_max - self.y_min
    
    def area(self) -> float:
        """Area in normalized coordinates (0.0 to 1.0)."""
        return self.width() * self.height()
    
    def center(self) -> Tuple[float, float]:
        """Center point in normalized coordinates."""
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)


@dataclass
class FaceDetectionResult:
    """Output from face detection."""
    boxes: List[BoundingBox]
    confidences: List[float]
    timestamp_ms: int
    
    def num_faces(self) -> int:
        return len(self.boxes)


@dataclass
class PrivacyDecision:
    """Output from privacy decision logic."""
    privacy_on: bool
    reason: str
    risk_score: float
    other_face_count: int


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Compute cosine similarity between two embeddings."""
    # Ensure vectors are normalized
    e1 = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
    e2 = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
    return float(np.dot(e1, e2))


def extract_face_crop(frame: np.ndarray, bbox: BoundingBox) -> np.ndarray:
    """Extract face crop from frame using bounding box."""
    h, w = frame.shape[:2]
    bbox_pixel = bbox.to_pixel_coords(w, h)
    
    # Add padding
    x_min = max(0, bbox_pixel.x_min - 10)
    y_min = max(0, bbox_pixel.y_min - 10)
    x_max = min(w, bbox_pixel.x_max + 10)
    y_max = min(h, bbox_pixel.y_max + 10)
    
    return frame[y_min:y_max, x_min:x_max]


def current_time_ms() -> int:
    """Get current time in milliseconds."""
    import time
    return int(time.time() * 1000)
