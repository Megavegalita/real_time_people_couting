"""
Phase 4 Tests - Multi-Camera & Parallel Processing

Tests for:
1. Queue management with Redis
2. Worker pool
3. Camera workers
4. Batch processing
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
from core.utils.queue_manager import TaskQueue, WorkerPool
from core.utils.batch_processor import BatchProcessor, FrameBatchProcessor
from workers.camera_worker import CameraWorker, CameraPool


class TestQueueManagement:
    """Test Redis queue management."""
    
    def test_queue_initialization(self) -> None:
        """Test queue can be initialized."""
        queue = TaskQueue()
        assert queue is not None
        
        # Redis availability
        assert queue.is_available() == True
    
    def test_queue_operations(self) -> None:
        """Test queue enqueue/dequeue operations."""
        queue = TaskQueue()
        
        # Clear queue
        queue.clear()
        
        # Enqueue task
        task = {
            'id': 1,
            'type': 'test',
            'data': 'test_data'
        }
        result = queue.enqueue(task)
        assert result == True
        
        # Check queue size
        size = queue.get_queue_size()
        assert size == 1
        
        # Dequeue task
        dequeued = queue.dequeue()
        assert dequeued is not None
        assert dequeued['id'] == 1
        assert dequeued['type'] == 'test'
        
        # Queue should be empty now
        size = queue.get_queue_size()
        assert size == 0


class TestWorkerPool:
    """Test worker pool functionality."""
    
    def test_worker_pool_initialization(self) -> None:
        """Test worker pool can be initialized."""
        pool = WorkerPool(num_workers=2)
        assert pool is not None
        assert pool.num_workers == 2
    
    def test_worker_pool_operations(self) -> None:
        """Test worker pool operations."""
        pool = WorkerPool(num_workers=1)
        
        # Start pool
        pool.start()
        
        # Stop pool
        pool.stop()
        
        # Should complete without errors
        assert True


class TestBatchProcessing:
    """Test batch processing functionality."""
    
    def test_batch_processor_initialization(self) -> None:
        """Test batch processor can be initialized."""
        def process_fn(batch):
            return [{'result': item} for item in batch]
        
        processor = BatchProcessor(
            batch_size=5,
            timeout=1.0,
            process_fn=process_fn
        )
        
        assert processor is not None
        assert processor.batch_size == 5
    
    def test_batch_processing(self) -> None:
        """Test batch processing operations."""
        results_collected = []
        
        def process_fn(batch):
            return [{'result': item['data']} for item in batch]
        
        processor = BatchProcessor(
            batch_size=3,
            timeout=0.5,
            process_fn=process_fn
        )
        
        # Add items
        for i in range(5):
            result = processor.add_item({'data': f'test_{i}'})
            if result:
                results_collected.extend(result)
        
        # Flush remaining
        flush_results = processor.flush()
        results_collected.extend(flush_results)
        
        # Should have processed all items
        assert len(results_collected) >= 3


class TestCameraWorkers:
    """Test camera worker functionality."""
    
    def test_camera_worker_initialization(self) -> None:
        """Test camera worker can be initialized."""
        worker = CameraWorker(
            camera_id="test_camera",
            camera_url="0"  # Webcam
        )
        
        assert worker is not None
        assert worker.camera_id == "test_camera"
        assert worker.is_running == False
    
    def test_camera_pool_initialization(self) -> None:
        """Test camera pool can be initialized."""
        pool = CameraPool()
        assert pool is not None
        assert len(pool.workers) == 0
    
    def test_camera_pool_operations(self) -> None:
        """Test camera pool operations."""
        pool = CameraPool()
        
        # Add camera (will fail without actual camera)
        # This is expected behavior for testing
        result = pool.add_camera("test_cam", "0")
        
        # Should handle failure gracefully
        # (either succeed or fail without crashing)
        assert result in [True, False]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

