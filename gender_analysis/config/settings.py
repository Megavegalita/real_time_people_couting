"""
Configuration Management for Gender Analysis System

This module handles all configuration loading, validation, and management
for the gender analysis microservices.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="postgresql://autoeyes@localhost:5432/gender_analysis")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    
    class Config:
        env_prefix = "DATABASE_"
        case_sensitive = False


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)
    password: Optional[str] = Field(default=None)
    
    @property
    def url(self) -> str:
        """Construct Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False


class APISettings(BaseSettings):
    """API server configuration settings."""
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)
    workers: int = Field(default=4)
    reload: bool = Field(default=True)
    
    class Config:
        env_prefix = "API_"
        case_sensitive = False


class FaceDetectionSettings(BaseSettings):
    """Face detection model configuration."""
    
    model: str = Field(default="mtcnn")  # Options: mtcnn, mediapipe, haarcascade
    confidence: float = Field(default=0.5)
    max_faces: int = Field(default=10)
    min_size: int = Field(default=50)
    max_size: int = Field(default=1024)
    
    class Config:
        env_prefix = "FACE_DETECTION_"
        case_sensitive = False


class FeatureExtractionSettings(BaseSettings):
    """Feature extraction configuration."""
    
    model: str = Field(default="face_recognition")  # Options: face_recognition, facenet, deepface
    dimension: int = Field(default=128)
    
    class Config:
        env_prefix = "FEATURE_EXTRACTION_"
        case_sensitive = False


class GenderClassificationSettings(BaseSettings):
    """Gender classification configuration."""
    
    model: str = Field(default="huggingface")
    model_name: str = Field(default="rizvandwiki/gender-classification")
    confidence_threshold: float = Field(default=0.6)
    
    class Config:
        env_prefix = "GENDER_MODEL_"
        case_sensitive = False


class AgeEstimationSettings(BaseSettings):
    """Age estimation configuration."""
    
    model: str = Field(default="custom_regression")
    min_age: int = Field(default=0)
    max_age: int = Field(default=100)
    confidence_threshold: float = Field(default=0.6)
    
    class Config:
        env_prefix = "AGE_MODEL_"
        case_sensitive = False


class ProcessingSettings(BaseSettings):
    """Processing configuration."""
    
    batch_size: int = Field(default=10)
    max_workers: int = Field(default=4)
    queue_timeout: float = Field(default=5.0)
    cache_ttl: int = Field(default=3600)  # 1 hour
    
    class Config:
        env_prefix = "PROCESSING_"
        case_sensitive = False


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    file: str = Field(default="logs/gender_analysis.log")
    
    class Config:
        env_prefix = "LOG_"
        case_sensitive = False


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration."""
    
    prometheus_port: int = Field(default=9090)
    health_check_interval: int = Field(default=30)
    
    class Config:
        env_prefix = "MONITORING_"
        case_sensitive = False


class CameraSettings(BaseSettings):
    """Camera configuration."""
    
    max_cameras: int = Field(default=50)
    timeout: float = Field(default=10.0)
    
    class Config:
        env_prefix = "CAMERA_"
        case_sensitive = False


class Settings(BaseSettings):
    """Main settings class combining all configurations."""
    
    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    api: APISettings = Field(default_factory=APISettings)
    face_detection: FaceDetectionSettings = Field(default_factory=FaceDetectionSettings)
    feature_extraction: FeatureExtractionSettings = Field(default_factory=FeatureExtractionSettings)
    gender_classification: GenderClassificationSettings = Field(default_factory=GenderClassificationSettings)
    age_estimation: AgeEstimationSettings = Field(default_factory=AgeEstimationSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    camera: CameraSettings = Field(default_factory=CameraSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

