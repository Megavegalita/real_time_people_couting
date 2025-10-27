"""
Batch Processing Utilities

This module provides batch processing capabilities for efficient
multi-frame and multi-person analysis.
"""

from typing import List, Dict, Any, Optional, Callable
import numpy as np
from collections import deque
import time
from config.settings import settings


class BatchProcessor:
    """
    Batch processor for efficient multi-frame processing.
    
    Collects multiple frames/tasks and processes them in batches
    for better performance and throughput.
    """
    
    def __init__(
        self,
        batch_size: int,
        timeout: float,
        process_fn: Callable
    ) -> None:
        """
        Initialize batch processor.
        
        Args:
            batch_size: Number of items per batch
            timeout: Maximum time to wait before processing (seconds)
            process_fn: Processing function to call on batches
        """
        self.batch_size: int = batch_size
        self.timeout: float = timeout
        self.process_fn: Callable = process_fn
        
        self.batch_queue: deque = deque()
        self.last_process_time: float = time.time()
        
        # Statistics
        self.total_batches: int = 0
        self.total_items: int = 0
        self.last_batch_time: Optional[float] = None
    
    def add_item(self, item: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Add item to batch. Process if batch is full or timeout exceeded.
        
        Args:
            item: Item to add to batch
            
        Returns:
            List of results if batch was processed, None otherwise
        """
        self.batch_queue.append(item)
        self.total_items += 1
        
        current_time = time.time()
        should_process = (
            len(self.batch_queue) >= self.batch_size or
            (current_time - self.last_process_time) >= self.timeout
        )
        
        if should_process:
            return self._process_batch()
        
        return None
    
    def _process_batch(self) -> List[Dict[str, Any]]:
        """Process current batch."""
        if len(self.batch_queue) == 0:
            return []
        
        # Extract batch
        batch = [self.batch_queue.popleft() for _ in range(len(self.batch_queue))]
        
        # Process batch
        start_time = time.time()
        results = self.process_fn(batch)
        process_time = time.time() - start_time
        
        # Update statistics
        self.total_batches += 1
        self.last_process_time = time.time()
        self.last_batch_time = process_time
        
        return results
    
    def flush(self) -> List[Dict[str, Any]]:
        """
        Process remaining items in queue.
        
        Returns:
            List of results
        """
        if len(self.batch_queue) == 0:
            return []
        
        return self._process_batch()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processor statistics."""
        return {
            'queue_size': len(self.batch_queue),
            'total_batches': self.total_batches,
            'total_items': self.total_items,
            'last_batch_time': self.last_batch_time,
            'avg_items_per_batch': (
                self.total_items / self.total_batches 
                if self.total_batches > 0 else 0
            )
        }


class FrameBatchProcessor:
    """
    Specialized batch processor for video frames.
    
    Batches frames and processes them efficiently for gender/age analysis.
    """
    
    def __init__(self, batch_size: int = 10) -> None:
        """
        Initialize frame batch processor.
        
        Args:
            batch_size: Number of frames per batch
        """
        self.batch_size = batch_size
        self.frame_buffer: List[np.ndarray] = []
        self.metadata_buffer: List[Dict[str, Any]] = []
    
    def add_frame(
        self, 
        frame: np.ndarray, 
        metadata: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Add frame to batch. Process if batch is full.
        
        Args:
            frame: Camera frame
            metadata: Frame metadata (camera_id, person_id, etc.)
            
        Returns:
            Results if batch was processed, None otherwise
        """
        self.frame_buffer.append(frame)
        self.metadata_buffer.append(metadata)
        
        if len(self.frame_buffer) >= self.batch_size:
            return self._process_batch()
        
        return None
    
    def _process_batch(self) -> List[Dict[str, Any]]:
        """Process current batch of frames."""
        results = []
        
        for i, (frame, metadata) in enumerate(zip(self.frame_buffer, self.metadata_buffer)):
            try:
                # Process single frame
                result = self._process_single_frame(frame, metadata)
                results.append(result)
            except Exception as e:
                print(f"Error processing frame {i}: {e}")
                results.append({'status': 'failed', 'error': str(e)})
        
        # Clear buffers
        self.frame_buffer.clear()
        self.metadata_buffer.clear()
        
        return results
    
    def _process_single_frame(
        self, 
        frame: np.ndarray, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single frame for gender/age analysis.
        
        Args:
            frame: Frame image
            metadata: Frame metadata
            
        Returns:
            Analysis results
        """
        from core.services.classification import analysis_service
        
        result = analysis_service.analyze_person(
            frame=frame,
            person_id=metadata.get('person_id'),
            bbox=metadata.get('bbox'),
            camera_id=metadata.get('camera_id')
        )
        
        return result
    
    def flush(self) -> List[Dict[str, Any]]:
        """Process remaining frames in buffer."""
        if len(self.frame_buffer) == 0:
            return []
        
        return self._process_batch()

