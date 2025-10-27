"""
Camera Worker for Multi-Camera Processing

This module provides workers to process multiple camera streams in parallel.
Each camera runs in its own worker thread for independent processing.
"""

from typing import Dict, Any, Optional, List, Callable
import cv2
import numpy as np
import threading
from threading import Thread, Event
import time
from config.settings import settings
from core.services.classification import analysis_service


class CameraWorker:
    """
    Worker for processing a single camera stream.
    
    Handles video capture, frame processing, and task submission.
    Each camera runs in its own thread for parallel processing.
    """
    
    def __init__(
        self, 
        camera_id: str,
        camera_url: str,
        processing_callback: Optional[Callable] = None
    ) -> None:
        """
        Initialize camera worker.
        
        Args:
            camera_id: Unique camera identifier
            camera_url: Camera stream URL or webcam index
            processing_callback: Callback function for results
        """
        self.camera_id: str = camera_id
        self.camera_url: str = camera_url
        self.callback: Optional[Callable] = None
        
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_running: bool = False
        self.worker_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        self.frame_count: int = 0
        self.last_processing_time: float = 0.0
        self.fps: float = 0.0
        
        # Processing statistics
        self.processed_count: int = 0
        self.error_count: int = 0
        
        if processing_callback:
            self.callback = processing_callback
    
    def start(self) -> bool:
        """
        Start camera worker.
        
        Returns:
            True if started successfully
        """
        if self.is_running:
            return False
        
        # Initialize camera
        try:
            self.capture = cv2.VideoCapture(self.camera_url)
            
            if not self.capture.isOpened():
                print(f"Failed to open camera {self.camera_id}")
                return False
            
            # Start worker thread
            self.is_running = True
            self.worker_thread = Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            print(f"✅ Camera worker {self.camera_id} started")
            return True
            
        except Exception as e:
            print(f"Error starting camera worker {self.camera_id}: {e}")
            return False
    
    def stop(self) -> None:
        """Stop camera worker."""
        self.is_running = False
        self.stop_event.set()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        if self.capture:
            self.capture.release()
        
        print(f"Camera worker {self.camera_id} stopped")
    
    def _worker_loop(self) -> None:
        """Main worker loop for processing frames."""
        while self.is_running and not self.stop_event.is_set():
            ret, frame = self.capture.read()
            
            if not ret:
                self.error_count += 1
                time.sleep(0.1)
                continue
            
            # Process frame
            self._process_frame(frame)
            
            # Update statistics
            self.frame_count += 1
            self._update_fps()
            
            # Small delay for performance
            time.sleep(0.01)
    
    def _process_frame(self, frame: np.ndarray) -> None:
        """
        Process a single frame.
        
        Args:
            frame: Camera frame
        """
        try:
            # Detect persons in frame
            # (This would integrate with existing person detection)
            
            # For each detected person:
            # 1. Get bounding box
            # 2. Submit for gender/age analysis
            # 3. Store results
            
            # Placeholder for integration with existing detection
            if self.callback:
                self.callback(self.camera_id, frame)
            
            self.processed_count += 1
            
        except Exception as e:
            print(f"Error processing frame in {self.camera_id}: {e}")
            self.error_count += 1
    
    def _update_fps(self) -> None:
        """Update FPS calculation."""
        current_time = time.time()
        
        if self.last_processing_time > 0:
            elapsed = current_time - self.last_processing_time
            if elapsed > 0:
                self.fps = 1.0 / elapsed
        
        self.last_processing_time = current_time
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get worker statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'camera_id': self.camera_id,
            'is_running': self.is_running,
            'fps': self.fps,
            'frames_processed': self.processed_count,
            'error_count': self.error_count,
            'total_frames': self.frame_count
        }


class CameraPool:
    """
    Pool of camera workers for multi-camera support.
    
    Manages multiple camera workers and provides unified interface.
    """
    
    def __init__(self) -> None:
        """Initialize camera pool."""
        self.workers: Dict[str, CameraWorker] = {}
        self.callbacks: Dict[str, Callable] = {}
    
    def add_camera(
        self, 
        camera_id: str, 
        camera_url: str,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Add camera to pool.
        
        Args:
            camera_id: Unique camera identifier
            camera_url: Camera stream URL
            callback: Processing callback
            
        Returns:
            True if added successfully
        """
        if camera_id in self.workers:
            print(f"Camera {camera_id} already exists")
            return False
        
        worker = CameraWorker(camera_id, camera_url, callback)
        
        if worker.start():
            self.workers[camera_id] = worker
            if callback:
                self.callbacks[camera_id] = callback
            return True
        
        return False
    
    def remove_camera(self, camera_id: str) -> bool:
        """
        Remove camera from pool.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            True if removed successfully
        """
        if camera_id not in self.workers:
            return False
        
        worker = self.workers[camera_id]
        worker.stop()
        del self.workers[camera_id]
        
        if camera_id in self.callbacks:
            del self.callbacks[camera_id]
        
        return True
    
    def stop_all(self) -> None:
        """Stop all camera workers."""
        for camera_id in list(self.workers.keys()):
            self.remove_camera(camera_id)
        
        print("All camera workers stopped")
    
    def get_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics from all cameras.
        
        Returns:
            Dictionary mapping camera_id to statistics
        """
        stats = {}
        for camera_id, worker in self.workers.items():
            stats[camera_id] = worker.get_statistics()
        
        return stats
    
    def get_active_cameras(self) -> List[str]:
        """Get list of active camera IDs."""
        return list(self.workers.keys())


# Global camera pool instance
camera_pool = CameraPool()

