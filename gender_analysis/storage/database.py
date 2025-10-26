"""
Database Connection and Models

This module handles database connections, session management, and
defines SQLAlchemy models for the gender analysis system.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from config.settings import settings

# Base class for all models
Base = declarative_base()


class PersonAnalysis(Base):
    """Main table storing person analysis results."""
    
    __tablename__ = "person_analysis"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    camera_id = Column(String(50), nullable=False, index=True)
    person_id = Column(Integer, nullable=False, index=True)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Analysis results
    gender = Column(String(10), nullable=False)  # 'male' or 'female'
    gender_confidence = Column(Float, nullable=False)
    
    age = Column(Integer, nullable=False)
    age_confidence = Column(Float, nullable=False)
    
    # Location and movement
    location = Column(String(100), nullable=True)
    direction = Column(String(20), nullable=True)  # 'IN' or 'OUT'
    
    # Face features storage (128-dim vector as JSON)
    face_features = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<PersonAnalysis(id={self.id}, camera={self.camera_id}, gender={self.gender}, age={self.age})>"


class Camera(Base):
    """Camera configurations."""
    
    __tablename__ = "cameras"
    
    camera_id = Column(String(50), primary_key=True)
    camera_name = Column(String(100), nullable=False)
    stream_url = Column(String(500), nullable=False)
    location = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Camera(id={self.camera_id}, name={self.camera_name}, active={self.is_active})>"


class DailyStats(Base):
    """Daily statistics aggregation."""
    
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    
    # Counts
    total_people = Column(Integer, default=0)
    male_count = Column(Integer, default=0)
    female_count = Column(Integer, default=0)
    
    # Age statistics
    avg_age = Column(Float, nullable=True)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    
    # Hourly breakdown (JSON)
    hour_breakdown = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<DailyStats(camera={self.camera_id}, date={self.date}, total={self.total_people})>"


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self) -> None:
        """Initialize database manager with connection pooling."""
        self.engine = create_engine(
            settings.database.url,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            echo=False  # Set to True for SQL query logging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def initialize_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """
        Context manager for database sessions.
        
        Automatically commits on success and rolls back on error.
        
        Example:
            with db_manager.session_scope() as session:
                person = PersonAnalysis(...)
                session.add(person)
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """
        Check database connection health.
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute("SELECT 1")
            return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager()

