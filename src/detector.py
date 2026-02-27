"""
Face detection using robust multi-cascade strategy.
Falls back gracefully for best multi-angle detection.
"""
import cv2
import numpy as np
import time
from typing import Optional, List
import os

from utils import BoundingBox, FaceDetectionResult, current_time_ms


class FaceDetector:
    """Robust multi-cascade face detector."""
    
    def __init__(self, model_selection: int = 0, min_confidence: float = 0.5):
        """
        Initialize face detector with fast, sensitive cascade strategy.
        Optimized for instant detection over false positive reduction.
        
        Args:
            model_selection: Unused (kept for API compatibility)
            min_confidence: Minimum detection confidence threshold (0.0-1.0)
        """
        self.min_confidence = min_confidence
        self.detection_count = 0
        
        # Load multiple cascade classifiers
        cascade_path = cv2.data.haarcascades
        
        self.cascades = []
        
        # Primary cascade: Front face (FAST & SENSITIVE)
        frontal = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_frontalface_default.xml'
        )
        if not frontal.empty():
            # minNeighbors=4 = fast detection, prioritizes sensitivity
            self.cascades.append(('frontal', frontal, {'scaleFactor': 1.1, 'minNeighbors': 4}))
        
        # Profile cascade: Side faces (FAST)
        profile = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_profileface.xml'
        )
        if not profile.empty():
            # minNeighbors=4 for very fast profile detection
            self.cascades.append(('profile', profile, {'scaleFactor': 1.1, 'minNeighbors': 4}))
        
        print(f"[INFO] Loaded {len(self.cascades)} face cascades (FAST MODE - instant detection)")
    
    def detect(self, frame: np.ndarray) -> FaceDetectionResult:
        """
        Run face detection using STRICT cascades.
        Applies NMS and filtering to eliminate false positives.
        
        Args:
            frame: BGR image (OpenCV format)
        
        Returns:
            FaceDetectionResult with normalized bounding boxes and confidences
        """
        h, w = frame.shape[:2]
        all_detections = []  # All detections before NMS
        
        # Convert to grayscale once
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Skip histogram equalization for speed - use as-is
        # gray = cv2.equalizeHist(gray)  # REMOVED for instant detection
        
        # Minimum face size (absolute pixels) - SMALLER for faster detection
        min_face_size = min(30, min(w, h) // 12)  # Allow very small faces for instant detection
        max_face_size = min(w, h) // 2
        
        # Try each cascade
        for cascade_name, cascade, params in self.cascades:
            try:
                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=params['scaleFactor'],
                    minNeighbors=params['minNeighbors'],  # Fast: low minNeighbors
                    minSize=(min_face_size, min_face_size),
                    maxSize=(max_face_size, max_face_size)
                )
                
                for (x, y, fw, fh) in faces:
                    # Filter: Face must be reasonably sized (not too small)
                    face_area = fw * fh
                    frame_area = w * h
                    area_ratio = face_area / frame_area
                    
                    # Only keep faces that are 0.2% to 50% of frame (VERY LENIENT for instant detection)
                    if area_ratio < 0.002:  # Allow very small faces
                        continue
                    if area_ratio > 0.5:  # Too large
                        continue
                    
                    # Normalize coordinates
                    x_min = max(0, x / w)
                    y_min = max(0, y / h)
                    x_max = min(1, (x + fw) / w)
                    y_max = min(1, (y + fh) / h)
                    
                    # Estimate confidence based on cascade and area
                    base_confidence = 0.7 if cascade_name == 'frontal' else 0.6
                    size_confidence = min(1.0, area_ratio * 100)  # Larger faces = more confident
                    confidence = base_confidence + (size_confidence * 0.2)
                    
                    all_detections.append({
                        'box': (x_min, y_min, x_max, y_max),
                        'confidence': confidence,
                        'area': area_ratio,
                        'cascade': cascade_name
                    })
                    
            except Exception as e:
                print(f"[WARNING] Cascade '{cascade_name}' error: {e}")
        
        # Apply Non-Maximum Suppression (NMS) to remove overlaps
        # FAST MODE: Very lenient NMS (0.15 threshold) to keep all faces
        filtered_detections = self._nms(all_detections, iou_threshold=0.15)
        
        # Convert to output format
        boxes = []
        confidences = []
        for det in filtered_detections:
            x_min, y_min, x_max, y_max = det['box']
            boxes.append(BoundingBox(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max))
            confidences.append(det['confidence'])
        
        self.detection_count += 1
        
        return FaceDetectionResult(
            boxes=boxes,
            confidences=confidences,
            timestamp_ms=current_time_ms()
        )
    
    def _nms(self, detections: List[dict], iou_threshold: float = 0.3) -> List[dict]:
        """
        Apply Non-Maximum Suppression to remove overlapping detections.
        Keeps only the best non-overlapping faces.
        
        Args:
            detections: List of detection dicts with 'box' and 'confidence'
            iou_threshold: IoU threshold for merging overlaps
            
        Returns:
            Filtered list of detections
        """
        if not detections:
            return []
        
        # Sort by confidence (descending)
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        kept = []
        for current in sorted_dets:
            # Check if current overlaps significantly with any kept detection
            should_keep = True
            for kept_det in kept:
                iou = self._compute_iou(current['box'], kept_det['box'])
                if iou > iou_threshold:
                    should_keep = False
                    break
            
            if should_keep:
                kept.append(current)
        
        return kept
    
    def _compute_iou(self, box1: tuple, box2: tuple) -> float:
        """
        Compute Intersection over Union (IoU) between two boxes.
        Boxes are (x_min, y_min, x_max, y_max) normalized 0-1.
        """
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Intersection area
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Union area
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        iou = inter_area / union_area if union_area > 0 else 0
        return iou
    
    def get_detection_count(self) -> int:
        """Get total number of detections run."""
        return self.detection_count
