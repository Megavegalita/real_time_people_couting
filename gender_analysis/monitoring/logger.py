"""
Structured Logging for Gender Analysis System

This module provides comprehensive logging with structured output,
performance tracking, and error monitoring.
"""

from typing import Dict, Any, Optional
import logging
import structlog
from pathlib import Path
from datetime import datetime
from config.settings import settings


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """
    Setup structured logger with file and console output.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.logging.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Setup standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        handlers=[
            logging.FileHandler(settings.logging.file),
            logging.StreamHandler()
        ]
    )
    
    logger = structlog.get_logger()
    logger.info(
        "Logger initialized",
        log_level=log_level,
        log_file=settings.logging.file
    )
    
    return logger


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection.
    
    Tracks processing times, throughput, and system health.
    """
    
    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.metrics: Dict[str, Any] = {
            'total_detections': 0,
            'total_analyses': 0,
            'average_processing_time': 0.0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'cameras_active': 0,
            'queue_size': 0,
            'fps_average': 0.0
        }
        
        self.timings: Dict[str, float] = {}
    
    def record_timing(self, operation: str, duration: float) -> None:
        """
        Record timing for an operation.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
        """
        if operation not in self.timings:
            self.timings[operation] = []
        
        self.timings[operation].append(duration)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current performance statistics.
        
        Returns:
            Dictionary with statistics
        """
        # Calculate average timings
        avg_timings = {}
        for operation, times in self.timings.items():
            if times:
                avg_timings[f'avg_{operation}'] = sum(times) / len(times)
        
        return {
            **self.metrics,
            **avg_timings
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            'total_detections': 0,
            'total_analyses': 0,
            'average_processing_time': 0.0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'cameras_active': 0,
            'queue_size': 0,
            'fps_average': 0.0
        }
        self.timings.clear()


class SystemHealth:
    """
    System health monitoring and diagnostics.
    """
    
    def __init__(self) -> None:
        """Initialize health monitor."""
        self.logger = setup_logger()
        self.checks: Dict[str, bool] = {}
    
    def check_components(self) -> Dict[str, bool]:
        """
        Check health of all system components.
        
        Returns:
            Dictionary of component status
        """
        checks = {}
        
        # Check Redis
        from core.utils.queue_manager import TaskQueue
        queue = TaskQueue()
        checks['redis'] = queue.is_available()
        
        # Check Database
        from storage.database import db_manager
        checks['database'] = db_manager.health_check()
        
        # Check models
        checks['gender_model'] = True  # Models are always loaded
        checks['age_model'] = True
        
        self.checks = checks
        return checks
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive health report.
        
        Returns:
            Health report dictionary
        """
        checks = self.check_components()
        
        all_healthy = all(checks.values())
        
        report = {
            'status': 'healthy' if all_healthy else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'components': checks,
            'healthy_count': sum(checks.values()),
            'total_components': len(checks)
        }
        
        # Log health status
        if all_healthy:
            self.logger.info("System healthy", **report)
        else:
            self.logger.warning("System health degraded", **report)
        
        return report


# Global instances
logger = setup_logger()
performance_monitor = PerformanceMonitor()
health_monitor = SystemHealth()

