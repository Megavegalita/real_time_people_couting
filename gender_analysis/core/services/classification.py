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
        
        # Detect face in person crop
        face_results = self.face_processor.process_frame(person_crop)
        
        # Debug info
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Person {person_id}: processing crop size {person_crop.shape}, face results: {len(face_results)}")
        
        if len(face_results) == 0:
            # Try with full frame for very small crops
            if person_crop.shape[0] < 50 or person_crop.shape[1] < 50:
                logger.debug(f"Person {person_id}: Small crop, trying face detection in bbox region")
                # Try detecting face in the person bbox region of full frame
                x, y, w, h = bbox
                person_region = frame[max(0,y-20):min(height,y+h+20), max(0,x-20):min(width,x+w+20)]
                face_results = self.face_processor.process_frame(person_region)
                logger.debug(f"Person {person_id}: Full region face results: {len(face_results)}")
        
        if len(face_results) == 0:
            return self._create_failed_result("No face detected")
        
        # Get first face
        face_crop, face_info = face_results[0]
        
        # Extract features (cached)
        features = self.feature_extractor.get_or_extract_features(
            person_id, 
            person_crop,
            face_info['box']
        )
        
        if features is None:
            return self._create_failed_result("Feature extraction failed")
        
        # Classify gender
        gender, gender_conf = self.gender_classifier.predict(features)
        
        # Estimate age
        age, age_conf = self.age_estimator.predict(features)
        
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

