"""
Gender and Age Classification Service

This module integrates gender classification and age estimation
with face feature extraction for complete analysis pipeline.
"""

from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from datetime import datetime

from core.models.gender import gender_classifier
from core.models.age import age_estimator
from core.services.feature_extraction import FaceFeatureExtractor, CachedFeatureExtractor
from core.services.face_processing import FaceProcessor
import cv2


class PersonAnalysisService:
    """
    Complete person analysis service.
    
    Combines face detection, feature extraction, gender classification,
    and age estimation into a single workflow.
    """
    
    def __init__(self) -> None:
        """Initialize person analysis service."""
        self.face_processor = FaceProcessor()
        self.feature_extractor = CachedFeatureExtractor()
        self.gender_classifier = gender_classifier
        self.age_estimator = age_estimator
    
    def _preprocess_crop(self, crop: np.ndarray, upscale_factor: int = 3) -> np.ndarray:
        """
        Preprocess person crop to improve face detection.
        
        Args:
            crop: Person crop image
            upscale_factor: How much to upscale (default: 3x)
            
        Returns:
            Preprocessed crop
        """
        # Upscale
        h, w = crop.shape[:2]
        upscaled = cv2.resize(crop, (w * upscale_factor, h * upscale_factor), 
                            interpolation=cv2.INTER_CUBIC)
        
        # Enhance contrast
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Slight sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    def analyze_person(
        self,
        frame: np.ndarray,
        person_id: int,
        bbox: Tuple[int, int, int, int],
        camera_id: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Analyze a person: detect face, extract features, classify gender, estimate age.
        
        Args:
            frame: Full frame image
            person_id: Unique person identifier
            bbox: Person bounding box (x, y, width, height)
            camera_id: Camera identifier
            
        Returns:
            Dictionary with analysis results:
                - gender: 'male' or 'female'
                - gender_confidence: float
                - age: int
                - age_confidence: float
                - face_features: 128-dim array
                - timestamp: datetime
        """
        # Extract face crop from person bbox
        x, y, w, h = bbox
        height, width = frame.shape[:2]
        
        # Ensure bbox is within frame
        x = max(0, min(x, width))
        y = max(0, min(y, height))
        w = min(w, width - x)
        h = min(h, height - y)
        
        if w <= 0 or h <= 0:
            return self._create_failed_result("Invalid bounding box")
        
        person_crop = frame[y:y+h, x:x+w]
        
        # Method 1: Try detecting face in preprocessed person crop
        preprocessed = self._preprocess_crop(person_crop)
        face_results = self.face_processor.process_frame(preprocessed)
        
        # Method 2: If no face in crop, try full frame region
        if len(face_results) == 0:
            # Expand bbox region for detection in full frame
            expanded_bbox = (
                max(0, x - w//2), 
                max(0, y - h//2),
                min(width, x + w + w//2) - max(0, x - w//2),
                min(height, y + h + h//2) - max(0, y - h//2)
            )
            
            x_exp, y_exp, w_exp, h_exp = expanded_bbox
            region = frame[y_exp:y_exp+h_exp, x_exp:x_exp+w_exp]
            
            if region.size > 0:
                face_results = self.face_processor.process_frame(region)
        
        # Method 3: Use direct face detection on full frame
        if len(face_results) == 0:
            face_results = self.face_processor.process_frame(frame)
            
            # Match faces to person bbox
            filtered_faces = []
            for face_crop, face_info in face_results:
                fx, fy, fw, fh = face_info['box']
                
                # Check if face is within person bbox (with some tolerance)
                if (x <= fx <= x + w and y <= fy <= y + h) or \
                   (x - fw//2 <= fx <= x + w + fw//2 and 
                    y - fh//2 <= fy <= y + h + fh//2):
                    filtered_faces.append((face_crop, face_info))
            
            face_results = filtered_faces
        
        if len(face_results) == 0:
            return self._create_failed_result("No face detected")
        
        # Get first face
        face_crop, face_info = face_results[0]
        
        # Extract features (cached)
        features = self.feature_extractor.get_or_extract_features(
            person_id, 
            face_crop,
            face_info['box']
        )
        
        if features is None:
            return self._create_failed_result("Feature extraction failed")
        
        # Classify gender
        try:
            gender, gender_conf = self.gender_classifier.predict(features)
        except Exception as e:
            return self._create_failed_result(f"Gender classification failed: {e}")
        
        # Estimate age
        try:
            age, age_conf = self.age_estimator.predict(features)
        except Exception as e:
            return self._create_failed_result(f"Age estimation failed: {e}")
        
        # Compile results
        result = {
            'person_id': person_id,
            'camera_id': camera_id,
            'gender': gender,
            'gender_confidence': float(gender_conf),
            'age': int(age),
            'age_confidence': float(age_conf),
            'face_features': features.tolist(),  # Convert to list for JSON
            'bbox': bbox,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
        
        return result
    
    def _create_failed_result(self, reason: str) -> Dict[str, Any]:
        """Create a failed result dictionary."""
        return {
            'gender': 'unknown',
            'gender_confidence': 0.0,
            'age': -1,
            'age_confidence': 0.0,
            'status': 'failed',
            'reason': reason
        }
    
    def batch_analyze(
        self,
        frame: np.ndarray,
        person_data: List[Tuple[int, Tuple[int, int, int, int]]],
        camera_id: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple persons in batch.
        
        Args:
            frame: Full frame image
            person_data: List of (person_id, bbox) tuples
            camera_id: Camera identifier
            
        Returns:
            List of analysis results
        """
        results = []
        for person_id, bbox in person_data:
            result = self.analyze_person(frame, person_id, bbox, camera_id)
            results.append(result)
        
        return results


# Global service instance
analysis_service = PersonAnalysisService()
