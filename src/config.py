"""
Configuration loader.
Reads config.json and provides configuration values.
"""
import json
import os
from typing import Any, Dict


class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config.json file
        """
        self.config_path = config_path
        self.data = {}
        self.load()
    
    def load(self):
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.data = json.load(f)
                print(f"[INFO] Configuration loaded from {self.config_path}")
            else:
                print(f"[WARNING] Config file not found at {self.config_path}, using defaults")
                self.data = self._default_config()
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            self.data = self._default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key (e.g., 'camera.device_id')."""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    @staticmethod
    def _default_config() -> Dict:
        """Return default configuration."""
        return {
            "camera": {
                "device_id": 0,
                "target_fps": 30
            },
            "detection": {
                "resize_width": 320,
                "resize_height": 240,
                "detection_interval_frames": 3,
                "min_detection_confidence": 0.5
            },
            "privacy": {
                "face_count_threshold": 2,
                "area_ratio_threshold": 0.02,
                "debounce_on_frames": 2,
                "debounce_off_seconds": 0.8,
                "blur_kernel_size": 31
            },
            "ui": {
                "show_annotations": True,
                "show_fps": True
            }
        }
