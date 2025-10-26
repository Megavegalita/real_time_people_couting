"""
Parallel People Counter - Main Orchestrator
============================================

Manages multiple worker threads for parallel processing of cameras/videos.
"""

import cv2
import logging
import time
from threading import Thread
from queue import Queue, Empty
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from parallel.worker import PeopleCounterWorker
from parallel.utils.result_handler import ResultHandler
from parallel.utils.logger import ParallelLogger

logger = logging.getLogger(__name__)


class ParallelPeopleCounter:
    """
    Main orchestrator for parallel people counting.
    """

    def __init__(
        self,
        worker_count: int = 4,
        result_output: str = "parallel/results/",
        log_dir: str = "parallel/logs/",
        log_level: str = "INFO"
    ):
        """
        Initialize ParallelPeopleCounter.

        Args:
            worker_count: Number of worker threads
            result_output: Directory for results
            log_dir: Directory for logs
            log_level: Logging level
        """
        self.worker_count = worker_count
        self.result_output = result_output
        self.log_dir = log_dir
        self.log_level = log_level

        # Queues
        self.task_queue = Queue()
        self.result_queue = Queue()
        
        # Track sources to prevent duplicates
        self.added_sources = set()  # Track sources to ensure uniqueness

        # Workers and model
        self.workers: List[PeopleCounterWorker] = []
        self.net = None
        self.running = False

        # Result handler
        self.result_handler = ResultHandler(output_dir=result_output)

        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'start_time': None,
            'end_time': None
        }

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        logger.info(f"Initialized ParallelPeopleCounter with {worker_count} workers")

    def load_model(self, prototxt: str, model: str):
        """
        Load MobileNetSSD model.

        Args:
            prototxt: Path to prototxt file
            model: Path to model file
        """
        logger.info("Loading MobileNetSSD model...")
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        logger.info("Model loaded successfully")

    def add_camera(
        self,
        source: str,
        camera_id: str = None,
        alias: str = None,
        threshold: int = 10,
        priority: int = 1,
        **kwargs
    ):
        """
        Add camera to processing queue.

        Args:
            source: Camera source (0 for webcam, RTSP URL for IP camera)
            camera_id: Unique camera identifier
            alias: Human-readable name
            threshold: People count threshold
            priority: Task priority (higher = more important)
            **kwargs: Additional camera configuration
        """
        # ACCURACY PRIORITY: Prevent duplicate sources
        if source in self.added_sources:
            logger.warning(f"⚠️  Source '{source}' already in queue. Skipping duplicate to ensure accuracy.")
            logger.warning(f"   This prevents race conditions and maintains consistency.")
            return
        
        if camera_id is None:
            camera_id = f"camera_{int(time.time())}"

        if alias is None:
            alias = camera_id

        task = {
            'task_id': f"camera_{camera_id}",
            'type': 'camera',
            'camera_id': camera_id,
            'source': source,
            'alias': alias,
            'threshold': threshold,
            'priority': priority,
            'status': 'pending',
            **kwargs
        }

        self.task_queue.put(task)
        self.added_sources.add(source)  # Mark as added
        self.stats['total_tasks'] += 1
        logger.info(f"✓ Added camera: {alias} ({camera_id})")

    def add_video(
        self,
        video_path: str,
        video_id: str = None,
        alias: str = None,
        threshold: int = 5,
        priority: int = 2,
        **kwargs
    ):
        """
        Add video to processing queue.

        Args:
            video_path: Path to video file
            video_id: Unique video identifier
            alias: Human-readable name
            threshold: People count threshold
            priority: Task priority
            **kwargs: Additional video configuration
        """
        # ACCURACY PRIORITY: Prevent duplicate sources
        if video_path in self.added_sources:
            logger.warning(f"⚠️  Video '{video_path}' already in queue. Skipping duplicate to ensure accuracy.")
            logger.warning(f"   Multiple workers processing the same video causes race conditions.")
            return
        
        if video_id is None:
            video_id = f"video_{int(time.time())}"

        if alias is None:
            alias = video_id

        task = {
            'task_id': f"video_{video_id}",
            'type': 'video',
            'video_id': video_id,
            'source': video_path,
            'alias': alias,
            'threshold': threshold,
            'priority': priority,
            'status': 'pending',
            **kwargs
        }

        self.task_queue.put(task)
        self.added_sources.add(video_path)  # Mark as added
        self.stats['total_tasks'] += 1
        logger.info(f"✓ Added video: {alias} ({video_id})")

    def start_processing(self, config: Dict[str, Any] = None):
        """
        Start parallel processing.

        Args:
            config: Additional configuration (skip_frames, confidence, etc.)
        """
        if self.net is None:
            raise ValueError("Model must be loaded before starting processing")

        if config is None:
            config = {
                'skip_frames': 30,
                'confidence': 0.4,
                'Thread': False
            }

        self.running = True
        self.stats['start_time'] = time.time()

        logger.info("Starting parallel processing...")

        # Start result collector
        result_thread = Thread(target=self._collect_results, daemon=True)
        result_thread.start()

        # Create and start workers
        for i in range(self.worker_count):
            worker = PeopleCounterWorker(
                worker_id=f"worker_{i+1:02d}",
                task_queue=self.task_queue,
                result_queue=self.result_queue,
                net=self.net,
                config=config,
                task_config=config
            )
            worker.start()
            self.workers.append(worker)
            logger.info(f"Started worker {i+1}/{self.worker_count}")

    def _collect_results(self):
        """Collect results from workers."""
        while self.running:
            try:
                result = self.result_queue.get(timeout=1)
                if result:
                    task_id = result.get('task_id', 'unknown')
                    self.result_handler.add_result(task_id, result)

                    if result.get('status') == 'completed':
                        self.stats['completed_tasks'] += 1
                        logger.info(f"Task completed: {task_id}")
                else:
                    # Non-blocking put back if needed
                    continue

            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error collecting results: {e}", exc_info=True)

    def stop_processing(self):
        """Stop all workers and processing."""
        logger.info("Stopping parallel processing...")
        self.running = False

        # Send shutdown signals
        for _ in self.workers:
            self.task_queue.put(None)

        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)

        self.stats['end_time'] = time.time()
        elapsed = self.stats['end_time'] - self.stats['start_time']

        logger.info(f"Processing stopped. Total time: {elapsed:.2f}s")
        logger.info(f"Completed: {self.stats['completed_tasks']}/{self.stats['total_tasks']} tasks")

    def get_results(self) -> Dict[str, Any]:
        """Get all results."""
        return self.result_handler.get_all_results()

    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        summary = self.result_handler.get_summary()
        summary['stats'] = self.stats.copy()
        return summary

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()

    def get_latest_results(self) -> Dict[str, Any]:
        """Get latest results for all tasks."""
        all_results = self.get_results()
        latest = {}
        for task_id, results in all_results.items():
            if results:
                latest[task_id] = results[-1]
        return latest

    def print_dashboard(self):
        """Print real-time dashboard."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("Parallel People Counting System - Dashboard")
        print("=" * 60)

        print(f"\nWorkers: {len(self.workers)} active | Tasks: {summary['total_tasks']}")
        print("-" * 60)

        for task_id, task_info in summary.get('tasks', {}).items():
            alias = task_id.split('_', 1)[-1]
            status = task_info['status']
            fps = task_info['latest_fps']
            total_in = task_info['total_in']
            total_out = task_info['total_out']
            current = task_info['current_count']

            status_symbol = "✓" if status == 'completed' else "▶" if status == 'running' else "✗"

            print(f"{status_symbol} {alias}:")
            print(f"    Status: {status} | FPS: {fps:.1f}")
            print(f"    In: {total_in} | Out: {total_out} | Current: {current}")

        overall = summary.get('overall', {})
        print(f"\n{'-' * 60}")
        print(f"Total: In: {overall.get('total_in', 0)} | "
              f"Out: {overall.get('total_out', 0)} | "
              f"Net: {overall.get('net_count', 0)}")
        print("=" * 60 + "\n")

    def export_results(self, format: str = 'json'):
        """
        Export results to file.

        Args:
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            self.result_handler.export_to_json()
        elif format == 'csv':
            results = self.get_results()
            for task_id in results:
                self.result_handler.export_to_csv(task_id)
        else:
            logger.error(f"Unknown export format: {format}")

