"""
Queue Management for Parallel Processing

This module provides queue management using Redis for task distribution
across multiple workers. Supports batching and parallel processing.
"""

from typing import List, Optional, Dict, Any
import json
import time
import redis
from threading import Thread, Event
from queue import Queue
from config.settings import settings


class TaskQueue:
    """
    Redis-based task queue for parallel processing.
    
    Manages task distribution across multiple workers using Redis.
    Supports task queuing, batching, and worker management.
    """
    
    def __init__(self, queue_name: str = "gender_analysis") -> None:
        """
        Initialize task queue.
        
        Args:
            queue_name: Name of the Redis queue
        """
        self.queue_name: str = queue_name
        self.redis_client: Optional[redis.Redis] = None
        self._initialize_redis()
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                password=settings.redis.password,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Redis connection failed: {e}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    def enqueue(self, task: Dict[str, Any]) -> bool:
        """
        Add task to queue.
        
        Args:
            task: Task data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            task_json = json.dumps(task, default=str)
            self.redis_client.rpush(self.queue_name, task_json)
            return True
        except Exception as e:
            print(f"Failed to enqueue task: {e}")
            return False
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Remove and return task from queue.
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            Task dictionary or None if timeout/empty
        """
        if not self.is_available():
            return None
        
        try:
            if timeout:
                result = self.redis_client.blpop(self.queue_name, timeout=int(timeout))
                if result:
                    _, task_json = result
                    return json.loads(task_json)
                return None
            else:
                result = self.redis_client.lpop(self.queue_name)
                if result:
                    return json.loads(result)
                return None
        except Exception as e:
            print(f"Failed to dequeue task: {e}")
            return None
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        if not self.is_available():
            return 0
        try:
            return self.redis_client.llen(self.queue_name)
        except Exception:
            return 0
    
    def clear(self) -> None:
        """Clear all tasks from queue."""
        if self.is_available():
            self.redis_client.delete(self.queue_name)


class WorkerPool:
    """
    Worker pool for parallel task processing.
    
    Manages multiple workers to process tasks in parallel.
    """
    
    def __init__(self, num_workers: int = 4) -> None:
        """
        Initialize worker pool.
        
        Args:
            num_workers: Number of worker threads
        """
        self.num_workers: int = num_workers
        self.workers: List[Thread] = []
        self.shutdown_event = Event()
        self.task_queue: TaskQueue = TaskQueue()
        self.results_queue: Queue = Queue()
    
    def start(self) -> None:
        """Start all worker threads."""
        if not self.task_queue.is_available():
            print("Warning: Redis not available, workers cannot start")
            return
        
        for i in range(self.num_workers):
            worker = Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)
        
        print(f"✅ Started {self.num_workers} workers")
    
    def stop(self) -> None:
        """Stop all workers."""
        self.shutdown_event.set()
        for worker in self.workers:
            worker.join(timeout=5)
        self.workers.clear()
        print("Workers stopped")
    
    def _worker_loop(self, worker_id: int) -> None:
        """Main worker loop for processing tasks."""
        while not self.shutdown_event.is_set():
            # Get task from queue
            task = self.task_queue.dequeue(timeout=settings.processing.queue_timeout)
            
            if task is not None:
                try:
                    # Process task
                    result = self._process_task(task)
                    if result:
                        self.results_queue.put({
                            'worker_id': worker_id,
                            'task_id': task.get('id'),
                            'result': result,
                            'status': 'success'
                        })
                except Exception as e:
                    self.results_queue.put({
                        'worker_id': worker_id,
                        'task_id': task.get('id'),
                        'error': str(e),
                        'status': 'failed'
                    })
            
            # Small delay to prevent CPU spin
            time.sleep(0.01)
    
    def _process_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single task.
        
        Args:
            task: Task data
            
        Returns:
            Processing result
        """
        # This will be implemented by specific worker implementations
        task_type = task.get('type')
        
        if task_type == 'gender_age_analysis':
            # Process gender and age analysis
            from core.services.classification import analysis_service
            
            return analysis_service.analyze_person(
                frame=task.get('frame'),
                person_id=task.get('person_id'),
                bbox=task.get('bbox'),
                camera_id=task.get('camera_id')
            )
        
        return None
    
    def submit_task(self, task: Dict[str, Any]) -> bool:
        """Submit task to queue."""
        return self.task_queue.enqueue(task)
    
    def get_results(self, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get results from processing.
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of results
        """
        results = []
        count = 0
        
        while count < (max_results or float('inf')):
            if self.results_queue.empty():
                break
            
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
                count += 1
            except:
                break
        
        return results

