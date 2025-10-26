"""
Logger for Parallel People Counting
=====================================

Multi-worker logging utilities.
"""

import logging
import os
import threading
from datetime import datetime
from typing import Optional, Dict


class ParallelLogger:
    """
    Custom logger for parallel processing.
    """

    _loggers: Dict[str, logging.Logger] = {}
    _lock = threading.Lock()

    @classmethod
    def get_logger(cls, name: str = "parallel", log_dir: str = "parallel/logs/") -> logging.Logger:
        """
        Get or create a logger instance.

        Args:
            name: Logger name
            log_dir: Directory for log files

        Returns:
            Configured logger instance
        """
        with cls._lock:
            if name in cls._loggers:
                return cls._loggers[name]

            # Create logger
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)

            # Prevent duplicate handlers
            if logger.handlers:
                return logger

            # Create formatter
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # File handler
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            cls._loggers[name] = logger
            return logger

    @classmethod
    def get_worker_logger(cls, worker_id: str, log_dir: str = "parallel/logs/") -> logging.Logger:
        """Get logger for specific worker."""
        return cls.get_logger(f"worker_{worker_id}", log_dir)

    @classmethod
    def get_camera_logger(cls, camera_id: str, log_dir: str = "parallel/logs/") -> logging.Logger:
        """Get logger for specific camera."""
        return cls.get_logger(f"camera_{camera_id}", log_dir)

