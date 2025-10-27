"""
DNN Face Detector - Modern deep learning approach

Uses OpenCV DNN for face detection with better accuracy for small/distant faces.
Can detect faces as small as 20-30 pixels (vs 50px for Haar Cascade).
"""

from typing import List, Dict, Any
import numpy as np
import cv2
import os


class DNNFaceDetector:
    """
    DNN-based face detector using OpenCV DNN module.
    
    Better than Haar Cascade for small/distant faces.
    Can detect faces in 20-30 pixel range.
    """
    
    def __init__(self, confidence_threshold: float = 0.5, nms_threshold: float = 0.4):
        """
        Initialize DNN face detector.
        
        Args:
            confidence_threshold: Minimum confidence for detection (default: 0.5)
            nms_threshold: Non-maximum suppression threshold (default: 0.4)
        """
        self.conf_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.input_size = (300, 300)
        self.net = None
        
        # Try to load model (will fallback to Haar if not available)
        self._load_model()
    
    def _load_model(self) -> None:
        """Load DNN face detection model."""
        # Model paths (try multiple locations)
        model_paths = [
            # OpenCV DNN face detector (most common)
            cv2.data.haarcascades + 'opencv_face_detector_uint8.pb',
            'gender_analysis/models/opencv_face_detector_uint8.pb',
            # Alternative locations
            'models/opencv_face_detector_uint8.pb',
        ]
        
        config_paths = [
            cv2.data.haarcascades + 'opencv_face_detector.pbtxt',
            'gender_analysis/models/opencv_face_detector.pbtxt',
            'models/opencv_face_detector.pbtxt',
        ]
        
        # Try to load OpenCV DNN face detector
        for model_path, config_path in zip(model_paths, config_paths):
            if os.path.exists(model_path) and os.path.exists(config_path):
                try:
                    self.net = cv2.dnn.readNet(model_path, config_path)
                    print(f"✅ DNN face detector loaded from {model_path}")
                    return
                except Exception as e:
                    print(f"⚠️  Failed to load from {model_path}: {e}")
                    continue
        
        # If DNN models not found, use Haar Cascade as fallback
        print("⚠️  DNN models not found, using MediaPipe as fallback")
        self.net = None
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in image using DNN.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of face detections with 'box' and 'confidence' keys
        """
        if image is None or image.size == 0:
            return []
        
        # If DNN not available, use improved Haar Cascade
        if self.net is None:
            return self._detect_haar_fallback(image)
        
        h, w = image.shape[:2]
        
        try:
            # Create blob for DNN
            blob = cv2.dnn.blobFromImage(
                image, 1.0, self.input_size,
                [104, 117, 123], False, False, cv2.dnn.DNN_TARGET_CPU
            )
            
            # Inference
            self.net.setInput(blob)
            detections = self.net.forward()
            
            # Process detections
            faces = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > self.conf_threshold:
                    # Extract bounding box
                    x1 = int(detections[0, 0, i, 3] * w)
                    y1 = int(detections[0, 0, i, 4] * h)
                    x2 = int(detections[0, 0, i, 5] * w)
                    y2 = int(detections[0, 0, i, 6] * h)
                    
                    # Ensure valid coordinates
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)
                    
                    width = x2 - x1
                    height = y2 - y1
                    
                    # Filter out invalid boxes
                    if width > 0 and height > 0:
                        faces.append({
                            'box': (x1, y1, width, height),
                            'confidence': float(confidence)
                        })
            
            return faces
            
        except Exception as e:
            print(f"⚠️  DNN detection failed: {e}")
            return self._detect_haar_fallback(image)
    
    def _detect_haar_fallback(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Fallback to improved Haar Cascade detection."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Dynamic min size based on image dimensions
        img_h, img_w = image.shape[:2]
        min_size = min(img_h, img_w) // 20  # 5% of smallest dimension
        min_size = max(15, min(min_size, 80))  # Between 15-80 pixels
        
        try:
            detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            faces_cascade = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(min_size, min_size)
            )
            
            results = []
            for (x, y, w, h) in faces_cascade:
                results.append({
                    'box': (int(x), int(y), int(w), int(h)),
                    'confidence': 1.0
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️  Haar fallback failed: {e}")
            return []
    
    def extract_face_crop(self, image: np.ndarray, bbox: tuple) -> np.ndarray:
        """Extract face crop from image."""
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]
    
    def resize_face(self, face_crop: np.ndarray, size: tuple = (160, 160)) -> np.ndarray:
        """Resize face crop to standard size."""
        return cv2.resize(face_crop, size)

