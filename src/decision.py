"""
Privacy decision logic with debounce and watching heuristic.
Determines when to trigger privacy mode based on face detection and identity verification.
"""
import time
import numpy as np
from typing import List, Optional
from utils import FaceDetectionResult, PrivacyDecision, BoundingBox


class PrivacyDecisionEngine:
    """Manages privacy decision logic with debounce and position stability."""
    
    def __init__(
        self,
        face_count_threshold: int = 2,
        area_ratio_threshold: float = 0.02,
        debounce_on_frames: int = 2,
        debounce_off_seconds: float = 0.8,
        debounce_off_frames: int = 30,
        use_identity_verification: bool = False,
    ):
        """
        Initialize privacy decision engine.
        
        Args:
            face_count_threshold: Trigger privacy if other_faces >= this count
            area_ratio_threshold: Only consider faces with area ratio >= this (watching heuristic)
            debounce_on_frames: Number of consecutive "risk" frames before turning ON
            debounce_off_seconds: Time in safe state before turning OFF
            debounce_off_frames: Number of consecutive safe frames before turning OFF (in addition to time)
            use_identity_verification: If True, only count non-ME faces
        """
        self.face_count_threshold = face_count_threshold
        self.area_ratio_threshold = area_ratio_threshold
        self.debounce_on_frames = debounce_on_frames
        self.debounce_off_seconds = debounce_off_seconds
        self.debounce_off_frames = debounce_off_frames
        self.use_identity_verification = use_identity_verification
        
        # Debounce state
        self.privacy_on = False
        self.risk_counter = 0
        self.safe_frame_counter = 0
        self.safe_start_time = None
        self.decision_history = []
        
        # Position stability tracking (for watching heuristic)
        self.last_other_positions = []
        self.position_stability_frames = 5  # Number of frames to track
    
    def decide(
        self,
        detection_result: FaceDetectionResult,
        frame_width: int,
        frame_height: int,
        identities: Optional[List] = None,
    ) -> PrivacyDecision:
        """
        Make a privacy decision based on detections.
        
        Args:
            detection_result: Face detection output
            frame_width: Frame width in pixels (for area ratio calculation)
            frame_height: Frame height in pixels
            identities: Optional list of FaceIdentity objects (from verifier)
        
        Returns:
            PrivacyDecision with privacy_on flag and reason
        """
        frame_area = frame_width * frame_height
        
        # Count "other" faces and compute risk score
        other_face_count = 0
        risk_score = 0.0
        reason = ""
        
        # If verification is enabled, use identity labels
        if self.use_identity_verification and identities is not None:
            other_faces = [f for f in identities if f.label == "OTHER"]
            
            for identity in other_faces:
                box = identity.box
                box_area_normalized = box.area()
                box_area_pixels = box_area_normalized * frame_area
                area_ratio = box_area_pixels / frame_area
                
                # Watching heuristic: only count faces that are close enough
                if area_ratio >= self.area_ratio_threshold:
                    other_face_count += 1
                    risk_score = max(risk_score, area_ratio)
            
            me_face_count = len([f for f in identities if f.label == "ME"])
            total_faces = len(identities)
        else:
            # No verification: count all faces beyond threshold  
            visible_face_count = 0
            for i, box in enumerate(detection_result.boxes):
                box_area_normalized = box.area()
                box_area_pixels = box_area_normalized * frame_area
                area_ratio = box_area_pixels / frame_area
                
                if area_ratio >= self.area_ratio_threshold:
                    visible_face_count += 1
                    risk_score = max(risk_score, area_ratio)
            
            other_face_count = max(0, visible_face_count - 1)  # Assume one is "ME"
            me_face_count = 1 if visible_face_count > 0 else 0
            total_faces = len(detection_result.boxes)
        
        # Determine current frame's risk status
        is_risky = other_face_count >= self.face_count_threshold
        
        # Apply debounce logic
        if is_risky:
            self.risk_counter += 1
            self.safe_frame_counter = 0  # Reset safe counter
            self.safe_start_time = None
            
            if self.risk_counter >= self.debounce_on_frames:
                self.privacy_on = True
                if self.use_identity_verification:
                    reason = f"Risk: {other_face_count} OTHER face(s) detected (area: {risk_score:.3f})"
                else:
                    reason = f"Risk: {total_faces} faces, {other_face_count} above threshold"
        else:
            # Safe frame detected - but keep blur ON for extended time + many frames
            self.risk_counter = 0
            self.safe_frame_counter += 1
            
            if self.safe_start_time is None:
                self.safe_start_time = time.time()
            
            time_safe = time.time() - self.safe_start_time
            
            # Turn OFF only if BOTH conditions met:
            # 1. Enough time has passed (debounce_off_seconds)
            # 2. Enough safe frames have been seen (debounce_off_frames)
            if time_safe >= self.debounce_off_seconds and self.safe_frame_counter >= self.debounce_off_frames:
                self.privacy_on = False
                self.safe_frame_counter = 0
                if self.use_identity_verification:
                    reason = f"Safe: {me_face_count} ME, {other_face_count} OTHER"
                else:
                    reason = f"Safe: {total_faces} faces detected"
            else:
                remaining_time = max(0, self.debounce_off_seconds - time_safe)
                remaining_frames = max(0, self.debounce_off_frames - self.safe_frame_counter)
                reason = f"Holding blur ({remaining_time:.1f}s, {remaining_frames} frames)"
        
        decision = PrivacyDecision(
            privacy_on=self.privacy_on,
            reason=reason,
            risk_score=risk_score,
            other_face_count=other_face_count
        )
        
        self.decision_history.append((time.time(), decision))
        # Keep only last 100 decisions
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
        
        return decision
    
    def reset(self):
        """Reset decision engine state (e.g., on pause/resume)."""
        self.privacy_on = False
        self.risk_counter = 0
        self.safe_frame_counter = 0
        self.safe_start_time = None
    
    def get_decision_history(self):
        """Get recent decision history."""
        return self.decision_history
