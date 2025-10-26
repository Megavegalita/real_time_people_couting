"""
Age Estimation Model

This module provides age estimation from face features.
Uses regression models for continuous age prediction.
"""

from typing import Optional, Tuple
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


class AgeEstimator:
    """
    Age estimation model using MLP or Random Forest.
    
    Estimates age from face features as continuous value.
    Uses MLP regressor for fast inference.
    """
    
    def __init__(self, model_type: str = "mlp", model_path: Optional[str] = None) -> None:
        """
        Initialize age estimator.
        
        Args:
            model_type: 'mlp' or 'rf' (random forest)
            model_path: Path to saved model file
        """
        self.model: Optional[np.ndarray] = None
        self.scaler: Optional[StandardScaler] = None
        self.model_type: str = model_type
        self.model_path: Optional[str] = model_path
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize or load age estimation model."""
        if self.model_path and Path(self.model_path).exists():
            # Load pre-trained model
            try:
                loaded = joblib.load(self.model_path)
                self.model = loaded['model']
                self.scaler = loaded['scaler']
                print(f"✅ Loaded age model from {self.model_path}")
                return
            except Exception as e:
                print(f"Warning: Could not load model: {e}")
        
        # Create new model
        if self.model_type == "rf":
            # Random Forest for age estimation
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        else:
            # MLP Regressor (default)
            self.model = MLPRegressor(
                hidden_layer_sizes=(64, 32),
                activation='relu',
                solver='adam',
                alpha=0.0001,
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
        
        print(f"✅ Created new age estimation model ({self.model_type})")
    
    def predict(self, features: np.ndarray) -> Tuple[int, float]:
        """
        Predict age from face features.
        
        Args:
            features: 128-dimensional face feature vector
            
        Returns:
            Tuple of (age: int, confidence: float)
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not initialized")
        
        # Reshape to 2D array if needed
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        # Normalize features
        features_scaled = self.scaler.transform(features)
        
        # Predict age
        age_float = self.model.predict(features_scaled)[0]
        age = int(round(age_float))
        
        # Clamp age to reasonable range
        age = max(0, min(100, age))
        
        # Confidence based on prediction certainty
        # For regression, we use a simple heuristic
        confidence = min(1.0, 0.9)  # Placeholder confidence
        
        return age, confidence
    
    def batch_predict(self, features_list: list) -> list:
        """
        Predict age for multiple face features (batch processing).
        
        Args:
            features_list: List of 128-dim feature vectors
            
        Returns:
            List of (age, confidence) tuples
        """
        results = []
        for features in features_list:
            age, confidence = self.predict(features)
            results.append((age, confidence))
        
        return results
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the age estimator.
        
        Args:
            X_train: Training features (N x 128)
            y_train: Training ages (N,) - integers 0-100
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not initialized")
        
        # Fit scaler on training data
        self.scaler.fit(X_train)
        
        # Transform training data
        X_train_scaled = self.scaler.transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        print("✅ Age estimator trained")
    
    def save(self, file_path: str) -> None:
        """Save trained model to file."""
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not initialized")
        
        joblib.dump({'model': self.model, 'scaler': self.scaler}, file_path)
        print(f"✅ Saved age model to {file_path}")


# Global estimator instance
age_estimator = AgeEstimator(model_type="mlp")

