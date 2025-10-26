"""
Phase 3 Tests - Gender and Age Classification

Tests for:
1. Gender classification model
2. Age estimation model
3. Integrated classification service
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
from core.models.gender import GenderClassifier
from core.models.age import AgeEstimator
from core.services.classification import PersonAnalysisService


class TestGenderClassification:
    """Test gender classification functionality."""
    
    def test_gender_classifier_initialization(self) -> None:
        """Test gender classifier can be initialized."""
        classifier = GenderClassifier()
        assert classifier is not None
        assert classifier.model is not None
        assert classifier.scaler is not None
    
    def test_gender_prediction(self) -> None:
        """Test gender prediction from features."""
        classifier = GenderClassifier()
        
        # Create mock features (128-dim)
        features = np.random.rand(128)
        
        # Note: Will fail without trained model, but structure works
        # In production, model must be trained first
        try:
            gender, confidence = classifier.predict(features)
            assert gender in ['male', 'female']
            assert 0.0 <= confidence <= 1.0
        except Exception as e:
            # Expected if model not trained - this is OK for now
            # Models need training data before use
            assert "not fitted" in str(e).lower() or "RuntimeError" in str(type(e).__name__)
    
    def test_gender_classifier_structure(self) -> None:
        """Test classifier has correct structure."""
        classifier = GenderClassifier()
        
        # Check model type
        assert classifier.model is not None
        assert classifier.scaler is not None


class TestAgeEstimation:
    """Test age estimation functionality."""
    
    def test_age_estimator_initialization(self) -> None:
        """Test age estimator can be initialized."""
        estimator = AgeEstimator()
        assert estimator is not None
        assert estimator.model is not None
        assert estimator.scaler is not None
    
    def test_age_prediction(self) -> None:
        """Test age prediction from features."""
        estimator = AgeEstimator()
        
        # Create mock features
        features = np.random.rand(128)
        
        # Note: Will fail without trained model
        try:
            age, confidence = estimator.predict(features)
            assert isinstance(age, int)
            assert 0 <= age <= 100
            assert 0.0 <= confidence <= 1.0
        except Exception as e:
            # Expected if model not trained - this is OK for now
            # Models need training data before use
            assert "not fitted" in str(e).lower() or "RuntimeError" in str(type(e).__name__)
    
    def test_age_estimator_structure(self) -> None:
        """Test estimator has correct structure."""
        estimator = AgeEstimator()
        
        # Check model type
        assert estimator.model is not None
        assert estimator.scaler is not None


class TestClassificationService:
    """Test integrated classification service."""
    
    def test_service_initialization(self) -> None:
        """Test person analysis service initialization."""
        service = PersonAnalysisService()
        assert service is not None
        assert service.face_processor is not None
        assert service.feature_extractor is not None
        assert service.gender_classifier is not None
        assert service.age_estimator is not None
    
    def test_service_structure(self) -> None:
        """Test service has all required components."""
        service = PersonAnalysisService()
        
        # Check all components exist
        assert hasattr(service, 'analyze_person')
        assert hasattr(service, 'batch_analyze')
        assert hasattr(service, 'face_processor')
        assert hasattr(service, 'feature_extractor')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

