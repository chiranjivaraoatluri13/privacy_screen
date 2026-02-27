"""
Main application entry point.
Orchestrates camera capture, face detection, verification, privacy decisions, and rendering.

Stages: 1 (Face detection + blur), 2+ (Verification), with debounce and watching heuristic
"""
import cv2
import numpy as np
import time
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from camera import CameraStream
from detector import FaceDetector
from embedder import FaceEmbedder
from verify import FaceVerifier
from decision import PrivacyDecisionEngine
from render import PrivacyRenderer
from config import Config
from utils import extract_face_crop
from fullscreen_overlay import initialize_overlay, show_privacy_overlay, hide_privacy_overlay


class SensitiveContentOverlay:
    """Demo overlay showing simulated sensitive content."""
    
    def __init__(self):
        """Initialize overlay."""
        self.text = "SENSITIVE: Password: SecureP@ssw0rd | Credit Card: 4532-1234-5678-9010"
        self.color = (50, 50, 200)
    
    def render(self, frame: np.ndarray) -> np.ndarray:
        """Render sensitive content overlay (blurred when privacy_on)."""
        h, w = frame.shape[:2]
        
        # Create a semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, h - 50), (w - 10, h - 10), self.color, -1)
        
        # Blend the rectangle
        alpha = 0.3
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Add text
        cv2.putText(
            frame,
            self.text,
            (20, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        return frame


def setup_logging():
    """Setup logging for the application."""
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"privacy_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """Main application loop."""
    logger = setup_logging()
    
    logger.info("========== CAMERA ACCESS PRIVACY PROTECTION SYSTEM ==========")
    logger.info("Stages: 1 (Detection) + 2 (Enrollment) + 3 (Verification) + 4 (Heuristic) + 5 (Pro)")
    logger.info("")
    
    # Load configuration
    config = Config()
    
    # Check for enrollment template
    template_path = Path(__file__).parent.parent / "data" / "my_template.npy"
    # TEMPORARILY DISABLE VERIFICATION - USE SIMPLE FACE COUNT LOGIC
    enable_verification = False  # Force disable for now
    
    if enable_verification:
        logger.info("[OK] Template found - Face verification ENABLED")
    else:
        logger.info("[--] Template not found - Face verification DISABLED")
        logger.info("    Run 'python enroll.py' to create a template")
    
    # Initialize components
    logger.info("Initializing components...")
    
    camera = CameraStream(
        device_id=config.get('camera.device_id', 0),
        target_fps=config.get('camera.target_fps', 30)
    )
    
    detector = FaceDetector(
        model_selection=0,
        min_confidence=config.get('detection.min_detection_confidence', 0.5)
    )
    
    embedder = FaceEmbedder()
    
    verifier = None
    if enable_verification:
        verifier = FaceVerifier(
            template_path=str(template_path),
            similarity_threshold=config.get('privacy.verification_threshold', 0.6)
        )
    
    decision_engine = PrivacyDecisionEngine(
        face_count_threshold=config.get('privacy.face_count_threshold', 2),
        area_ratio_threshold=config.get('privacy.area_ratio_threshold', 0.02),
        debounce_on_frames=config.get('privacy.debounce_on_frames', 2),
        debounce_off_seconds=config.get('privacy.debounce_off_seconds', 0.8),
        debounce_off_frames=config.get('privacy.debounce_off_frames', 30),
        use_identity_verification=enable_verification,
    )
    
    renderer = PrivacyRenderer(
        blur_kernel_size=config.get('privacy.blur_kernel_size', 31),
        show_annotations=config.get('ui.show_annotations', True),
        show_fps=config.get('ui.show_fps', True),
    )
    
    overlay = SensitiveContentOverlay()
    
    # Initialize fullscreen privacy overlay
    logger.info("Initializing fullscreen overlay...")
    initialize_overlay()
    logger.info("[OK] Fullscreen overlay ready")
    
    # Load UI settings
    headless_mode = config.get('ui.headless', False)
    if headless_mode:
        logger.info("[OK] Running in HEADLESS MODE (background only)")
    
    # Start camera
    if not camera.start():
        logger.error("Failed to start camera. Exiting.")
        return
    
    # Wait for first frame
    logger.info("Waiting for first frame...")
    time.sleep(1)
    
    logger.info("")
    logger.info("Starting main loop. Controls:")
    logger.info("  'q' - Quit")
    logger.info("  'p' - Pause/Resume detection")
    logger.info("  'r' - Reset decision engine")
    logger.info("  'd' - Toggle demo sensitive content overlay")
    logger.info("  's' - Toggle annotations")
    logger.info("")
    
    resize_width = config.get('detection.resize_width', 320)
    resize_height = config.get('detection.resize_height', 240)
    detect_interval = config.get('detection.detection_interval_frames', 3)
    
    frame_counter = 0
    fps_counter = 0
    fps_time = time.time()
    detection_count = 0
    embedding_count = 0
    privacy_transitions = 0
    last_privacy_state = False
    
    detection_result = None
    privacy_decision = None
    identities = None
    paused = False
    show_demo_overlay = False
    
    try:
        while True:
            # Get latest frame
            frame, frame_idx = camera.get_latest_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            h, w = frame.shape[:2]
            
            # Run face detection every N frames
            if frame_counter % detect_interval == 0 and not paused:
                # Resize for faster detection
                frame_resized = cv2.resize(frame, (resize_width, resize_height))
                detection_result = detector.detect(frame_resized)
                detection_count += 1
                
                identities = None
                if enable_verification and verifier and detection_result.num_faces() > 0:
                    # Extract and compute embeddings for all faces
                    crops = [extract_face_crop(frame, box) for box in detection_result.boxes]
                    embeddings = embedder.compute_batch_embeddings(crops)
                    embedding_count += len(embeddings)
                    
                    # Verify identities
                    identities = verifier.verify_batch(embeddings, detection_result.boxes)
                
                # Make privacy decision
                privacy_decision = decision_engine.decide(
                    detection_result,
                    frame_width=w,
                    frame_height=h,
                    identities=identities
                )
                
                # Log privacy transitions
                if privacy_decision.privacy_on != last_privacy_state:
                    privacy_transitions += 1
                    state = "ON" if privacy_decision.privacy_on else "OFF"
                    logger.info(f"[{detection_count}] Privacy turned {state}: {privacy_decision.reason}")
                    last_privacy_state = privacy_decision.privacy_on
                    
                    # Show/hide fullscreen overlay
                    if privacy_decision.privacy_on:
                        show_privacy_overlay()
                    else:
                        hide_privacy_overlay()
            
            # Calculate FPS
            fps_counter += 1
            current_time = time.time()
            if current_time - fps_time >= 1.0:
                current_fps = fps_counter / (current_time - fps_time)
                fps_counter = 0
                fps_time = current_time
            else:
                current_fps = 0.0
            
            # Render frame
            if not paused:
                rendered = renderer.render(
                    frame,
                    privacy_decision.privacy_on if privacy_decision else False,
                    detection_result,
                    privacy_decision,
                    current_fps,
                    identities=identities
                )
                
                # Add demo overlay if enabled and privacy is OFF
                if show_demo_overlay and not (privacy_decision and privacy_decision.privacy_on):
                    rendered = overlay.render(rendered)
            else:
                rendered = frame.copy()
                cv2.putText(
                    rendered,
                    "PAUSED",
                    (w // 2 - 80, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 165, 255),
                    3
                )
            
            # Display frame
            if not headless_mode:
                cv2.imshow("Camera Access - Privacy Protection", rendered)
            
            # Handle keyboard input
            if not headless_mode:
                key = cv2.waitKey(1) & 0xFF
            else:
                key = -1
                time.sleep(0.01)  # Prevent CPU spinning in headless mode
            
            if key == ord('q'):
                logger.info("Quit requested")
                break
            elif key == ord('p'):
                paused = not paused
                state = "PAUSED" if paused else "RESUMED"
                logger.info(f"{state}")
            elif key == ord('r'):
                decision_engine.reset()
                logger.info("Decision engine reset")
            elif key == ord('d'):
                show_demo_overlay = not show_demo_overlay
                state = "ON" if show_demo_overlay else "OFF"
                logger.info(f"Demo overlay: {state}")
            elif key == ord('s'):
                renderer.show_annotations = not renderer.show_annotations
                state = "ON" if renderer.show_annotations else "OFF"
                logger.info(f"Annotations: {state}")
            
            frame_counter += 1
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        # Cleanup and final logging
        logger.info("")
        logger.info("========== SESSION STATISTICS ==========")
        logger.info(f"Total frames processed: {frame_counter}")
        logger.info(f"Total detections: {detection_count}")
        logger.info(f"Total embeddings computed: {embedding_count}")
        logger.info(f"Privacy transitions: {privacy_transitions}")
        logger.info(f"Final camera FPS: {camera.get_fps():.1f}")
        logger.info("")
        
        camera.stop()
        cv2.destroyAllWindows()
        logger.info("Application closed successfully")


if __name__ == "__main__":
    main()
