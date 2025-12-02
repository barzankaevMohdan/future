"""
Video streaming module.

Manages current frame state and MJPEG stream generation for Flask.
Thread-safe frame access using locks.
"""

import threading
import time
from typing import Optional, Generator
import numpy as np
import cv2


# Global state
_current_frame: Optional[np.ndarray] = None
_frame_lock = threading.Lock()


def set_frame(frame: np.ndarray) -> None:
    """
    Update current frame (thread-safe).
    
    Args:
        frame: New frame to set
    """
    global _current_frame
    with _frame_lock:
        _current_frame = frame.copy() if frame is not None else None


def get_frame_copy() -> Optional[np.ndarray]:
    """
    Get a copy of current frame (thread-safe).
    
    Returns:
        Copy of current frame or None
    """
    with _frame_lock:
        return _current_frame.copy() if _current_frame is not None else None


def is_streaming() -> bool:
    """
    Check if streaming is active.
    
    Returns:
        True if current frame exists
    """
    with _frame_lock:
        return _current_frame is not None


def generate_mjpeg_frames() -> Generator[bytes, None, None]:
    """
    Generate MJPEG frames for Flask streaming.
    
    Yields:
        JPEG frame bytes with multipart headers
    """
    while True:
        frame = get_frame_copy()
        
        if frame is None:
            time.sleep(0.1)
            continue
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        if not ret:
            time.sleep(0.033)
            continue
        
        # Yield frame with multipart headers
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        # ~30 FPS
        time.sleep(0.033)








