"""
Enrollment script: Capture and store user's face template.
Run this once to create your face template for verification.

Usage: python enroll.py
Press 'e' to start enrollment, space to capture face samples, 'q' to quit
"""
import cv2
import numpy as np
import json
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.camera import CameraStream
from src.detector import FaceDetector
from src.embedder import FaceEmbedder
from src.utils import extract_face_crop
from src.config import Config


def enroll_user():
    """Interactive enrollment routine."""
    print("[INFO] ========== FACE ENROLLMENT ROUTINE ==========")
    print("[INFO] This will create a template of your face for verification")
    print()
    
    config = Config()
    
    # Initialize components
    camera = CameraStream(
        device_id=config.get('camera.device_id', 0),
        target_fps=config.get('camera.target_fps', 30)
    )
    
    detector = FaceDetector(min_confidence=0.5)
    embedder = FaceEmbedder()
    
    if not camera.start():
        print("[ERROR] Failed to start camera")
        return False
    
    print("[INFO] Camera started. Waiting for first frame...")
    time.sleep(1)
    
    # Enrollment state
    enrolling = False
    captured_crops = []
    captured_embeddings = []
    frame_counter = 0
    detection_result = None
    
    print()
    print("[INSTRUCTIONS]")
    print("1. Press 'e' to START enrollment")
    print("2. Your face will be detected automatically")
    print("3. Press SPACE to capture sample (capture 10-15 samples)")
    print("4. Move your head slightly between captures")
    print("5. Press 'q' to FINISH enrollment")
    print()
    
    try:
        while True:
            # Get latest frame
            frame, frame_idx = camera.get_latest_frame()
            if frame is None:
                time.sleep(0.01)
                continue
            
            h, w = frame.shape[:2]
            display = frame.copy()
            
            # Run detection every 3 frames
            if frame_counter % 3 == 0:
                frame_resized = cv2.resize(frame, (320, 240))
                detection_result = detector.detect(frame_resized)
            
            # Draw UI
            if enrolling:
                cv2.putText(
                    display,
                    "ENROLLING - Press SPACE to capture",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    display,
                    f"Captured: {len(captured_crops)} samples",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
            else:
                cv2.putText(
                    display,
                    "Press 'e' to START enrollment",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 165, 255),
                    2
                )
            
            # Draw detected faces
            if detection_result:
                for i, (box, conf) in enumerate(zip(detection_result.boxes, detection_result.confidences)):
                    bbox_pixel = box.to_pixel_coords(w, h)
                    color = (0, 255, 0) if enrolling else (100, 100, 100)
                    thickness = 3 if enrolling else 1
                    
                    cv2.rectangle(
                        display,
                        (bbox_pixel.x_min, bbox_pixel.y_min),
                        (bbox_pixel.x_max, bbox_pixel.y_max),
                        color,
                        thickness
                    )
                    cv2.putText(
                        display,
                        f"Face: {conf:.2f}",
                        (bbox_pixel.x_min, bbox_pixel.y_min - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1
                    )
            
            cv2.imshow("Face Enrollment", display)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("[INFO] Enrollment cancelled")
                break
            elif key == ord('e'):
                if not enrolling:
                    print("[INFO] Starting enrollment...")
                    enrolling = True
                    captured_crops = []
                    captured_embeddings = []
            elif key == ord(' ') and enrolling:
                # Capture face sample
                if detection_result and len(detection_result.boxes) > 0:
                    # Get largest face (assumed to be the user)
                    largest_idx = np.argmax([box.area() for box in detection_result.boxes])
                    box = detection_result.boxes[largest_idx]
                    
                    # Extract face crop
                    crop = extract_face_crop(frame, box)
                    
                    if crop is not None and crop.size > 0:
                        captured_crops.append(crop)
                        
                        # Compute embedding
                        embedding = embedder.compute_embedding(crop)
                        captured_embeddings.append(embedding)
                        
                        print(f"  Captured sample {len(captured_crops)}")  
                        
                        if len(captured_crops) >= 15:
                            print("[INFO] Reached 15 samples - enrollment complete!")
                            enrolling = False
                else:
                    print("[WARNING] No face detected in frame")
            
            frame_counter += 1
            
            # Finalize enrollment if we have enough samples
            if enrolling and len(captured_crops) >= 10:
                print("[INFO] Got 10+ samples. Press 'q' to finish, or keep capturing...")
        
        # Save enrollment if we have samples
        if len(captured_embeddings) > 0:
            print()
            print("[INFO] Finalizing enrollment...")
            
            # Average embeddings
            avg_embedding = np.mean(np.array(captured_embeddings), axis=0)
            avg_embedding = avg_embedding / (np.linalg.norm(avg_embedding) + 1e-8)
            
            # Save template
            template_path = Path(__file__).parent / "data" / "my_template.npy"
            template_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(template_path, avg_embedding)
            print(f"[OK] Template saved: {template_path}")
            
            # Save metadata
            meta = {
                "timestamp": time.time(),
                "num_samples": len(captured_crops),
                "embedding_size": len(avg_embedding),
                "model_version": "1.0",
                "threshold": 0.6
            }
            meta_path = Path(__file__).parent / "data" / "meta.json"
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
            print(f"[OK] Metadata saved: {meta_path}")
            
            print()
            print("[SUCCESS] Enrollment complete!")
            print(f"  - Captured {len(captured_crops)} face samples")
            print(f"  - Template similarity threshold: {meta['threshold']}")
            print()
            print("You can now run main.py with verification enabled.")
            return True
        else:
            print("[WARNING] No samples captured")
            return False
    
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        return False
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    success = enroll_user()
    sys.exit(0 if success else 1)
