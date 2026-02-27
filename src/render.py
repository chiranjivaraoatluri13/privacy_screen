"""
Rendering and obfuscation (blur) for privacy mode.
Handles UI drawing, annotations, and privacy blur overlay.
"""
import cv2
import numpy as np
from typing import List, Optional

from utils import BoundingBox, FaceDetectionResult, PrivacyDecision


class PrivacyRenderer:
    """Renders frames with privacy blur and annotations."""
    
    def __init__(
        self,
        blur_kernel_size: int = 31,
        show_annotations: bool = True,
        show_fps: bool = True,
    ):
        """
        Initialize renderer.
        
        Args:
            blur_kernel_size: Gaussian blur kernel size (must be odd)
            show_annotations: Whether to draw face boxes and labels
            show_fps: Whether to display FPS counter
        """
        self.blur_kernel_size = blur_kernel_size
        if blur_kernel_size % 2 == 0:
            self.blur_kernel_size += 1  # Ensure odd
        
        self.show_annotations = show_annotations
        self.show_fps = show_fps
        
        self.frame_count = 0
        self.last_fps = 0.0
        self.last_fps_time = 0
    
    def render(
        self,
        frame: np.ndarray,
        privacy_on: bool,
        detection_result: Optional[FaceDetectionResult] = None,
        decision: Optional[PrivacyDecision] = None,
        current_fps: float = 0.0,
        identities: Optional[List] = None,
    ) -> np.ndarray:
        """
        Render frame with privacy blur and annotations.
        
        Args:
            frame: Original BGR frame
            privacy_on: Whether privacy mode is active
            detection_result: Face detection results
            decision: Privacy decision info
            current_fps: Current frame rate
            identities: Optional list of FaceIdentity objects
            identities: Optional list of FaceIdentity objects
        
        Returns:
            Rendered frame (BGR)
        """
        h, w = frame.shape[:2]
        output = frame.copy()
        
        # Apply privacy blur if active - FULL SCREEN BLUR
        if privacy_on:
            # Apply strong Gaussian blur to entire frame
            output = cv2.GaussianBlur(output, (self.blur_kernel_size, self.blur_kernel_size), 0)
            # Apply dark red overlay to completely obscure content
            privacy_indicator = np.zeros_like(output)
            privacy_indicator[:, :] = (100, 50, 50)  # Dark red tint
            output = cv2.addWeighted(output, 0.3, privacy_indicator, 0.7, 0)
        
        # Draw annotations
        if identities is not None:
            self._draw_annotations(output, detection_result, privacy_on, identities)
        elif self.show_annotations and detection_result:
            self._draw_annotations(output, detection_result, privacy_on)
        
        # Draw status and decision info
        self._draw_status(output, privacy_on, decision, current_fps)
        
        self.frame_count += 1
        return output
    
    def _draw_annotations(
        self,
        frame: np.ndarray,
        detection_result: FaceDetectionResult = None,
        privacy_on: bool = False,
        identities: Optional[List] = None,
    ):
        """Draw face bounding boxes and labels."""
        h, w = frame.shape[:2]
        
        if detection_result is None:
            return
        
        # If we have identity information, use it; otherwise just show detections
        if identities is not None:
            for identity in identities:
                bbox_pixel = identity.box.to_pixel_coords(w, h)
                
                # Color by identity
                if identity.label == "ME":
                    color = (0, 255, 0)  # Green
                    label = f"ME: {identity.similarity:.2f}"
                else:
                    color = (0, 0, 255)  # Red
                    label = f"OTHER: {identity.similarity:.2f}"
                
                thickness = 3 if identity.label == "ME" else 2
                
                # Draw bounding box
                cv2.rectangle(
                    frame,
                    (bbox_pixel.x_min, bbox_pixel.y_min),
                    (bbox_pixel.x_max, bbox_pixel.y_max),
                    color,
                    thickness
                )
                
                # Draw label
                cv2.putText(
                    frame,
                    label,
                    (bbox_pixel.x_min, bbox_pixel.y_min - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )
        else:
            # No identity info, just show detections
            for i, (box, conf) in enumerate(zip(detection_result.boxes, detection_result.confidences)):
                bbox_pixel = box.to_pixel_coords(w, h)
                
                # Choose color (red for privacy mode, green for normal)
                color = (0, 0, 255) if privacy_on else (0, 255, 0)
                thickness = 2
                
                # Draw bounding box
                cv2.rectangle(
                    frame,
                    (bbox_pixel.x_min, bbox_pixel.y_min),
                    (bbox_pixel.x_max, bbox_pixel.y_max),
                    color,
                    thickness
                )
                
                # Draw confidence label
                label = f"Face {i+1}: {conf:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (bbox_pixel.x_min, bbox_pixel.y_min - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )
    
    def _draw_status(
        self,
        frame: np.ndarray,
        privacy_on: bool,
        decision: Optional[PrivacyDecision],
        current_fps: float,
    ):
        """Draw status information on frame."""
        h, w = frame.shape[:2]
        
        # Privacy status
        privacy_text = "PRIVACY ON" if privacy_on else "PRIVACY OFF"
        privacy_color = (0, 0, 255) if privacy_on else (0, 255, 0)
        
        cv2.putText(
            frame,
            privacy_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            privacy_color,
            2
        )
        
        # Decision reason
        if decision:
            reason_text = decision.reason[:50]  # Truncate long reasons
            cv2.putText(
                frame,
                reason_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
        
        # FPS
        if self.show_fps:
            fps_text = f"FPS: {current_fps:.1f}"
            cv2.putText(
                frame,
                fps_text,
                (w - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                1
            )
        
        # Camera indicator (blinking dot)
        indicator_color = (0, 255, 0)
        cv2.circle(frame, (w - 20, 20), 8, indicator_color, -1)
