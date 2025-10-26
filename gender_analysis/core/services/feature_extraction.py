"""
Face Feature Extraction Service

This module extracts face embeddings (features) from detected faces.
Features are extracted ONCE and cached for reuse in gender/age classification.
"""

from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import face_recognition
from core.services.face_processing import FaceProcessor, FaceDetector
from config.settings import settings


class FaceFeatureExtractor:
    """
    Face feature extraction service using face_recognition library.
    
    Extracts 128-dimensional face embeddings for classification.
    Optimized for performance with caching support.
    """
    
    def __init__(self, feature_dimension: int = 128) -> None:
        """
        Initialize feature extractor.
        
        Args:
            feature_dimension: Expected feature vector dimension (default: 128)
        """
        self.feature_dimension: int = feature_dimension
        self.face_processor: FaceProcessor = FaceProcessor()
    
    def extract_features(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face features from a single face image.
        
        Args:
            face_image: Face crop as numpy array (RGB format)
            
        Returns:
            128-dimensional feature vector or None if extraction fails
        """
        try:
            # face_recognition expects RGB format
            # Ensure image is in RGB
            if len(face_image.shape) == 3 and face_image.shape[2] == 3:
                rgb_image = np.array(face_image)
            else:
                return None
            
            # Extract encodings (128-dim vector)
            encodings = face_recognition.face_encodings(rgb_image)
            
            if len(encodings) > 0:
                # Return first face encoding
                features = np.array(encodings[0])
                return features
            else:
                return None
                
        except Exception as e:
            print(f"Feature extraction failed: {e}")
            return None
    
    def batch_extract(self, face_images: List[np.ndarray]) -> List[Optional[np.ndarray]]:
        """
        Extract features from multiple face images (batch processing).
        
        Args:
            face_images: List of face crop images
            
        Returns:
            List of feature vectors (None for failed extractions)
        """
        results = []
        for face_image in face_images:
            features = self.extract_features(face_image)
            results.append(features)
        
        return results
    
    def process_frame_to_features(
        self, 
        frame: np.ndarray
    ) -> List[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Process a frame to extract face features.
        
        Complete pipeline: Detect → Extract → Return features
        
        Args:
            frame: Input frame/image
            
        Returns:
            List of (features, detection_info) tuples
        """
        # Detect faces in frame
        face_results = self.face_processor.process_frame(frame)
        
        results = []
        for face_crop, detection_info in face_results:
            # Extract features from face crop
            features = self.extract_features(face_crop)
            
            if features is not None:
                results.append((features, detection_info))
        
        return results


class CachedFeatureExtractor:
    """
    Feature extractor with caching to avoid re-extraction.
    
    Caches extracted features by person_id to reuse across frames.
    This is the KEY OPTIMIZATION: extract features ONCE per person.
    """
    
    def __init__(self) -> None:
        """Initialize cached feature extractor."""
        self.extractor: FaceFeatureExtractor = FaceFeatureExtractor()
        self.feature_cache: Dict[int, np.ndarray] = {}
    
    def get_or_extract_features(
        self, 
        person_id: int, 
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Get cached features or extract new ones.
        
        Args:
            person_id: Unique person identifier
            frame: Full frame image
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            128-dim feature vector
        """
        # Check cache first
        if person_id in self.feature_cache:
            return self.feature_cache[person_id]
        
        # Extract face crop
        x, y, w, h = bbox
        face_crop = frame[y:y+h, x:x+w]
        
        if face_crop is None or face_crop.size == 0:
            return None
        
        # Extract features
        features = self.extractor.extract_features(face_crop)
        
        # Cache for future use
        if features is not None:
            self.feature_cache[person_id] = features
        
        return features
    
    def clear_cache(self, person_id: Optional[int] = None) -> None:
        """
        Clear feature cache.
        
        Args:
            person_id: Specific person to clear (None = clear all)
        """
        if person_id is None:
            self.feature_cache.clear()
        elif person_id in self.feature_cache:
            del self.feature_cache[person_id]
    
    def get_cache_size(self) -> int:
        """Get number of cached features."""
        return len(self.feature_cache)


# Global extractor instance
feature_extractor = FaceFeatureExtractor()
cached_extractor = CachedFeatureExtractor()

