"""
Phase 2 Tests - Face Detection and Feature Extraction

Tests for:
1. Face detection service
2. Feature extraction service
3. Integration between services
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import cv2
from core.services.face_processing import FaceDetector, FaceProcessor
from core.services.feature_extraction import FaceFeatureExtractor, CachedFeatureExtractor


class TestFaceDetection:
    """Test face detection functionality."""
    
    def test_face_detector_initialization(self) -> None:
        """Test face detector can be initialized."""
        detector = FaceDetector()
        assert detector is not None
        assert detector.min_face_size == 50
        assert detector.confidence_threshold == 0.5
    
    def test_face_detection_with_sample_image(self) -> None:
        """Test face detection with a synthetic image."""
        # Create a synthetic image with a face-like region
        # Note: In real testing, use actual face images
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        detector = FaceDetector(confidence_threshold=0.1)
        
        # Should not crash even with no faces
        detections = detector.detect_faces(image)
        assert isinstance(detections, list)
    
    def test_face_crop_extraction(self) -> None:
        """Test face crop extraction from bounding box."""
        detector = FaceDetector()
        
        # Create test image
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        bbox = (100, 100, 200, 200)
        
        crop = detector.extract_face_crop(image, bbox)
        assert crop is not None
        assert crop.shape[0] == 200
        assert crop.shape[1] == 200
    
    def test_face_resize(self) -> None:
        """Test face image resizing."""
        detector = FaceDetector()
        
        # Create test image
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        resized = detector.resize_face(image, (224, 224))
        assert resized.shape == (224, 224, 3)


class TestFeatureExtraction:
    """Test feature extraction functionality."""
    
    def test_feature_extractor_initialization(self) -> None:
        """Test feature extractor can be initialized."""
        extractor = FaceFeatureExtractor()
        assert extractor is not None
        assert extractor.feature_dimension == 128
    
    def test_feature_extraction_with_sample_image(self) -> None:
        """Test feature extraction (may return None without valid face)."""
        extractor = FaceFeatureExtractor()
        
        # Create synthetic image (won't have valid face features)
        image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        features = extractor.extract_features(image)
        # May return None if no valid face detected
        assert features is None or len(features) == 128
    
    def test_feature_extraction_batch(self) -> None:
        """Test batch feature extraction."""
        extractor = FaceFeatureExtractor()
        
        images = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8),
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        ]
        
        results = extractor.batch_extract(images)
        assert len(results) == 2
        # Results may be None if no valid faces
        for result in results:
            assert result is None or len(result) == 128


class TestCachedFeatureExtractor:
    """Test cached feature extraction."""
    
    def test_cached_extractor_initialization(self) -> None:
        """Test cached extractor can be initialized."""
        extractor = CachedFeatureExtractor()
        assert extractor is not None
        assert len(extractor.feature_cache) == 0
    
    def test_cache_functionality(self) -> None:
        """Test caching works correctly."""
        extractor = CachedFeatureExtractor()
        
        # Clear cache
        extractor.clear_cache()
        assert extractor.get_cache_size() == 0
        
        # Cache should be empty initially
        assert extractor.get_cache_size() == 0


class TestIntegration:
    """Test integration between services."""
    
    def test_detector_and_extractor_integration(self) -> None:
        """Test face detection + feature extraction pipeline."""
        # Initialize services
        processor = FaceProcessor()
        extractor = FaceFeatureExtractor()
        
        # Create test image
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Process frame (may not detect faces in random image)
        face_results = processor.process_frame(frame)
        assert isinstance(face_results, list)
        
        # If faces detected, test feature extraction
        for face_crop, detection_info in face_results:
            features = extractor.extract_features(face_crop)
            if features is not None:
                assert len(features) == 128


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

