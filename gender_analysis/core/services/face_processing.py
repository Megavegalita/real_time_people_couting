"""
Face Detection and Processing Service

This module provides face detection capabilities using MTCNN and other methods.
It detects faces in images and extracts face regions for further processing.
"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

from config.settings import settings


class FaceDetector:
    """
    Face detection service using OpenCV's DNN face detector.
    
    Detects faces in images and returns bounding boxes.
    Optimized for real-time processing with adjustable parameters.
    """
    
    def __init__(self, min_face_size: int = 50, confidence_threshold: float = 0.5) -> None:
        """
        Initialize face detector with OpenCV DNN.
        
        Args:
            min_face_size: Minimum face size in pixels (default: 50)
            confidence_threshold: Minimum confidence for detection (default: 0.5)
        """
        self.min_face_size: int = min_face_size
        self.confidence_threshold: float = confidence_threshold
        
        # Initialize OpenCV face detector
        self.detector: Optional[cv2.CascadeClassifier] = None
        self._initialize_detector()
    
    def _initialize_detector(self) -> None:
        """Initialize OpenCV face detector with configured settings."""
        try:
            # Use Haar Cascade for face detection (comes with OpenCV)
            self.detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except Exception as e:
            print(f"Warning: Face detector initialization failed: {e}")
            self.detector = None
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect all faces in an image.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of face detections with keys:
                - 'box': (x, y, width, height) bounding box
                - 'confidence': Detection confidence score (always 1.0 for Haar)
                
        Raises:
            ValueError: If image is invalid
        """
        if self.detector is None:
            raise RuntimeError("Face detector not initialized")
        
        if image is None or image.size == 0:
            raise ValueError("Invalid image provided")
        
        # Convert to grayscale for Haar Cascade
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(self.min_face_size, self.min_face_size)
        )
        
        # Format results
        results = []
        for (x, y, w, h) in faces:
            # Filter by minimum size
            if w >= self.min_face_size and h >= self.min_face_size:
                results.append({
                    'box': (int(x), int(y), int(w), int(h)),
                    'confidence': 1.0  # Haar Cascade doesn't provide confidence
                })
        
        return results
    
    def extract_face_crop(
        self, 
        image: np.ndarray, 
        bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Extract face region as cropped image.
        
        Args:
            image: Full image as numpy array
            bbox: Bounding box as (x, y, width, height)
            
        Returns:
            Cropped face image or None if invalid
        """
        if image is None or image.size == 0:
            return None
        
        x, y, w, h = bbox
        
        # Ensure coordinates are within image bounds
        height, width = image.shape[:2]
        x = max(0, min(x, width))
        y = max(0, min(y, height))
        w = min(w, width - x)
        h = min(h, height - y)
        
        if w <= 0 or h <= 0:
            return None
        
        # Crop and return
        face_crop = image[y:y+h, x:x+w]
        return face_crop
    
    def resize_face(self, face_image: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        Resize face image to target size for model input.
        
        Args:
            face_image: Face crop image
            target_size: Target size as (width, height)
            
        Returns:
            Resized image
        """
        return cv2.resize(face_image, target_size, interpolation=cv2.INTER_AREA)
    
    def batch_detect(self, images: List[np.ndarray]) -> List[List[Dict[str, Any]]]:
        """
        Detect faces in multiple images (batch processing).
        
        Args:
            images: List of images
            
        Returns:
            List of detection results for each image
        """
        results = []
        for image in images:
            detections = self.detect_faces(image)
            results.append(detections)
        
        return results


class FaceProcessor:
    """
    High-level face processing service.
    
    Combines detection, cropping, and preprocessing for easy use.
    """
    
    def __init__(self) -> None:
        """Initialize face processor with detector."""
        self.detector: FaceDetector = FaceDetector(
            min_face_size=settings.face_detection.min_size,
            confidence_threshold=settings.face_detection.confidence
        )
    
    def process_frame(
        self, 
        frame: np.ndarray, 
        max_faces: Optional[int] = None
    ) -> List[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Process a frame to detect and extract faces.
        
        Args:
            frame: Input frame/image
            max_faces: Maximum number of faces to detect (None = all)
            
        Returns:
            List of (face_crop, detection_info) tuples
        """
        # Detect faces
        detections = self.detector.detect_faces(frame)
        
        # Limit number of faces
        if max_faces and len(detections) > max_faces:
            detections = detections[:max_faces]
        
        results = []
        for detection in detections:
            # Extract face crop
            face_crop = self.detector.extract_face_crop(frame, detection['box'])
            
            if face_crop is not None:
                # Resize for model input
                resized_face = self.detector.resize_face(face_crop)
                
                results.append((resized_face, detection))
        
        return results

