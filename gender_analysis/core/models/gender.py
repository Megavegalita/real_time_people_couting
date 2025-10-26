"""
Gender Classification Model

This module provides gender classification from face features.
Uses a lightweight MLP (Multi-Layer Perceptron) classifier.
"""

from typing import Optional, Tuple
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


class GenderClassifier:
    """
    Gender classification model using MLP.
    
    Classifies face features as male or female.
    Uses lightweight MLP for fast inference.
    """
    
    def __init__(self, model_path: Optional[str] = None) -> None:
        """
        Initialize gender classifier.
        
        Args:
            model_path: Path to saved model file (None = use default)
        """
        self.model: Optional[MLPClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.model_path: Optional[str] = model_path
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize or load gender classification model."""
        if self.model_path and Path(self.model_path).exists():
            # Load pre-trained model
            try:
                loaded = joblib.load(self.model_path)
                self.model = loaded['model']
                self.scaler = loaded['scaler']
                print(f"✅ Loaded gender model from {self.model_path}")
                return
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
        
        # Create new model with default architecture
        # Input: 128-dim face features
        # Output: 2 classes (male, female)
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32),  # 2 hidden layers
            activation='relu',
            solver='adam',
            alpha=0.0001,  # L2 regularization
            batch_size='auto',
            learning_rate='constant',
            learning_rate_init=0.001,
            max_iter=200,
            shuffle=True,
            random_state=42,
            warm_start=False,
            momentum=0.9,
            nesterovs_momentum=True,
            early_stopping=False,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-08,
            n_iter_no_change=10,
            max_fun=15000
        )
        
        # Create scaler
        self.scaler = StandardScaler()
        
        print("✅ Created new gender classification model")
    
    def predict(self, features: np.ndarray) -> Tuple[str, float]:
        """
        Predict gender from face features.
        
        Args:
            features: 128-dimensional face feature vector
            
        Returns:
            Tuple of (gender: 'male' or 'female', confidence: float)
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not initialized")
        
        # Reshape to 2D array if needed
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        # Normalize features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get gender and confidence
        gender = "male" if prediction == 1 else "female"
        confidence = float(probabilities[prediction])
        
        return gender, confidence
    
    def batch_predict(self, features_list: list) -> list:
        """
        Predict gender for multiple face features (batch processing).
        
        Args:
            features_list: List of 128-dim feature vectors
            
        Returns:
            List of (gender, confidence) tuples
        """
        results = []
        for features in features_list:
            gender, confidence = self.predict(features)
            results.append((gender, confidence))
        
        return results
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the gender classifier.
        
        Args:
            X_train: Training features (N x 128)
            y_train: Training labels (N,) - 0=female, 1=male
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not initialized")
        
        # Fit scaler on training data
        self.scaler.fit(X_train)
        
        # Transform training data
        X_train_scaled = self.scaler.transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        print("✅ Gender classifier trained")
    
    def save(self, file_path: str) -> None:
        """Save trained model to file."""
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not initialized")
        
        joblib.dump({'model': self.model, 'scaler': self.scaler}, file_path)
        print(f"✅ Saved gender model to {file_path}")


# Global classifier instance
gender_classifier = GenderClassifier()

