import os
from typing import Optional

class VideoConfig:
    _instance = None
    _video_path: Optional[str] = None
    _output_dir: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VideoConfig, cls).__new__(cls)
        return cls._instance
    
    @property
    def video_path(self) -> Optional[str]:
        return self._video_path
    
    @video_path.setter
    def video_path(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file '{path}' does not exist.")
        self._video_path = path
    
    @property
    def output_dir(self) -> Optional[str]:
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self, path: str):
        os.makedirs(path, exist_ok=True)
        self._output_dir = path
    
    def reset(self):
        """Reset all configuration values."""
        self._video_path = None
        self._output_dir = None

# Create a global instance
video_config = VideoConfig() 