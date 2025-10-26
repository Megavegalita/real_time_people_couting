"""
Constants for People Counting System
====================================

Centralized constants to replace magic numbers throughout the codebase.
"""

# Tracking constants
class Tracking:
    """Constants for object tracking."""
    MAX_DISAPPEARED: int = 40  # Maximum frames before deregistering object
    MAX_DISTANCE: int = 50      # Maximum centroid distance for association


# Detection constants
class Detection:
    """Constants for object detection."""
    CONFIDENCE_THRESHOLD: float = 0.4    # Minimum confidence for detection
    SKIP_FRAMES: int = 10                # Frames to skip between detections
    FRAME_WIDTH: int = 500                  # Resized frame width
    BLOB_SCALE: float = 0.007843         # Blob scaling factor
    BLOB_MEAN: float = 127.5              # Blob mean subtraction


# Timer constants
class Timer:
    """Constants for timing operations."""
    MAX_DURATION_SECONDS: int = 28800    # 8 hours in seconds
    FRAME_BUFFER: int = 2                 # Seconds to wait for stream


# Drawing constants
class Drawing:
    """Constants for visual elements."""
    LINE_COLOR: tuple = (0, 0, 0)         # Black
    LINE_THICKNESS: int = 3
    TEXT_COLOR_WHITE: tuple = (255, 255, 255)  # White
    TEXT_COLOR_BLACK: tuple = (0, 0, 0)  # Black
    TEXT_THICKNESS: int = 2
    CIRCLE_RADIUS: int = 4
    CIRCLE_THICKNESS: int = -1  # Filled circle
    FONT_TYPE = None  # cv2.FONT_HERSHEY_SIMPLEX


# Alert constants
class Alert:
    """Constants for alerting system."""
    THRESHOLD: int = 10                   # People count threshold
    EMAIL_COOLDOWN: int = 60              # Seconds between alerts


# Video constants
class Video:
    """Constants for video processing."""
    VIDEO_FOURCC: str = "mp4v"            # Video codec
    VIDEO_FPS: int = 30                   # Output video FPS
    QUEUE_TIMEOUT: float = 1.0            # Queue read timeout


# MobileNetSSD class labels
CLASSES: list = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"
]

# Person class index (used for filtering detections)
PERSON_CLASS_IDX: int = 15  # Index of "person" in CLASSES list


# Direction detection
class Direction:
    """Constants for direction detection."""
    UP: int = -1      # Negative direction (moving up)
    DOWN: int = 1     # Positive direction (moving down)
    THRESHOLD: int = 0  # Zero threshold for direction


# Status strings
class Status:
    """Status strings for processing."""
    WAITING: str = "Waiting"
    DETECTING: str = "Detecting"
    TRACKING: str = "Tracking"
    COMPLETED: str = "completed"
    ERROR: str = "error"


# UI labels
class Labels:
    """UI text labels."""
    PREDICTION_BORDER: str = "-Prediction border - Entrance-"
    ALERT_MESSAGE: str = "-ALERT: People limit exceeded-"
    EXIT: str = "Exit"
    ENTER: str = "Enter"
    STATUS: str = "Status"
    TOTAL_PEOPLE: str = "Total people inside"


# File paths
class Paths:
    """Common file paths."""
    CONFIG: str = "utils/config.json"
    LOG_DATA: str = "utils/data/logs/counting_data.csv"
    DETECTOR_PROTOTXT: str = "detector/MobileNetSSD_deploy.prototxt"
    DETECTOR_MODEL: str = "detector/MobileNetSSD_deploy.caffemodel"

