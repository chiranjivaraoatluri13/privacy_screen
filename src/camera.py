"""
Camera capture thread using OpenCV.
Continuously reads frames from webcam and stores in a shared buffer.
"""
import cv2
import threading
import time
from typing import Optional


class CameraStream:
    """Manages continuous camera capture in a background thread."""
    
    def __init__(self, device_id: int = 0, target_fps: int = 30):
        """
        Initialize camera stream.
        
        Args:
            device_id: Camera device ID (0 for default/built-in)
            target_fps: Target frames per second
        """
        self.device_id = device_id
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        
        self.cap = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.running = False
        self.thread = None
        
        self.frame_count = 0
        self.start_time = None
    
    def start(self) -> bool:
        """Start the camera capture thread."""
        try:
            self.cap = cv2.VideoCapture(self.device_id)
            if not self.cap.isOpened():
                print(f"[ERROR] Failed to open camera device {self.device_id}")
                return False
            
            # Set camera properties for lower latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            self.running = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            print(f"[INFO] Camera stream started (device={self.device_id}, fps={self.target_fps})")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start camera: {e}")
            return False
    
    def _capture_loop(self):
        """Background thread: continuously capture frames."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("[WARNING] Failed to read frame from camera")
                time.sleep(0.01)
                continue
            
            # Store the latest frame
            with self.frame_lock:
                self.latest_frame = frame
                self.frame_count += 1
            
            # Throttle to target FPS
            time.sleep(self.frame_time)
    
    def get_latest_frame(self) -> Optional[tuple]:
        """
        Get the latest captured frame.
        
        Returns:
            (frame, frame_count) or (None, -1) if no frame is available
        """
        with self.frame_lock:
            if self.latest_frame is None:
                return None, -1
            return self.latest_frame.copy(), self.frame_count
    
    def get_fps(self) -> float:
        """Estimate the actual capture FPS."""
        if self.start_time is None or self.frame_count < 2:
            return 0.0
        elapsed = time.time() - self.start_time
        return self.frame_count / elapsed if elapsed > 0 else 0.0
    
    def stop(self):
        """Stop the camera capture thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("[INFO] Camera stream stopped")
