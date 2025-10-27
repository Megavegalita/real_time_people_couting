"""
Metrics Collection for Prometheus

This module provides Prometheus-compatible metrics for monitoring.
"""

from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime
import time


# Counters
faces_detected_counter = Counter(
    'faces_detected_total',
    'Total number of faces detected'
)

gender_classified_counter = Counter(
    'gender_classified_total',
    'Total number of gender classifications',
    ['gender']
)

age_estimated_counter = Counter(
    'age_estimated_total',
    'Total number of age estimations'
)

analysis_errors_counter = Counter(
    'analysis_errors_total',
    'Total number of analysis errors',
    ['error_type']
)

# Histograms
processing_time_histogram = Histogram(
    'analysis_processing_time_seconds',
    'Time spent on analysis',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

feature_extraction_time = Histogram(
    'feature_extraction_time_seconds',
    'Time spent on feature extraction',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
)

# Gauges
active_cameras_gauge = Gauge(
    'active_cameras',
    'Number of active cameras'
)

queue_size_gauge = Gauge(
    'task_queue_size',
    'Current size of task queue'
)

cache_size_gauge = Gauge(
    'feature_cache_size',
    'Number of cached features'
)


class MetricsCollector:
    """
    Metrics collector and exporter.
    """
    
    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.start_time = time.time()
    
    def record_face_detection(self) -> None:
        """Record face detection."""
        faces_detected_counter.inc()
    
    def record_gender_classification(self, gender: str) -> None:
        """Record gender classification."""
        gender_classified_counter.labels(gender=gender).inc()
    
    def record_age_estimation(self) -> None:
        """Record age estimation."""
        age_estimated_counter.inc()
    
    def record_analysis_error(self, error_type: str) -> None:
        """Record analysis error."""
        analysis_errors_counter.labels(error_type=error_type).inc()
    
    def record_processing_time(self, duration: float) -> None:
        """Record processing time."""
        processing_time_histogram.observe(duration)
    
    def record_feature_extraction_time(self, duration: float) -> None:
        """Record feature extraction time."""
        feature_extraction_time.observe(duration)
    
    def update_active_cameras(self, count: int) -> None:
        """Update active cameras count."""
        active_cameras_gauge.set(count)
    
    def update_queue_size(self, size: int) -> None:
        """Update queue size."""
        queue_size_gauge.set(size)
    
    def update_cache_size(self, size: int) -> None:
        """Update cache size."""
        cache_size_gauge.set(size)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        from prometheus_client import generate_latest, REGISTRY
        return generate_latest(REGISTRY).decode('utf-8')


# Global metrics collector
metrics_collector = MetricsCollector()

