"""
Parallel People Counting System
===============================

A multi-threaded, parallel processing system for counting people from multiple cameras or videos simultaneously.

Usage:
    from parallel import ParallelPeopleCounter
    
    counter = ParallelPeopleCounter(worker_count=4)
    counter.add_camera("rtsp://camera1")
    counter.start_processing()
"""

from parallel.parallel_people_counter import ParallelPeopleCounter
from parallel.worker import PeopleCounterWorker

__version__ = "1.0.0"
__all__ = ["ParallelPeopleCounter", "PeopleCounterWorker"]

