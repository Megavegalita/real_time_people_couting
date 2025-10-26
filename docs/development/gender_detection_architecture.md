# Gender & Age Detection Microservices Architecture

**Project**: Multi-Camera Face Analysis System  
**Version**: 1.0  
**Date**: 2024-10-26  
**Branch**: gender_detection

---

## 📋 Executive Summary

### Objective
Xây dựng hệ thống phân tích đặc trưng khuôn mặt để nhận diện giới tính và độ tuổi cho nhiều camera đồng thời, với kiến trúc microservices, xử lý song song, và phản hồi nhanh.

### Key Requirements
1. **Multi-Camera Support**: Xử lý đồng thời nhiều camera
2. **Face Feature Extraction**: Trích xuất đặc trưng khuôn mặt một lần duy nhất
3. **Gender & Age Detection**: Phân tích giới tính và độ tuổi
4. **Microservices Architecture**: Các service độc lập, dễ scale
5. **Parallel Processing**: Xử lý song song với high throughput
6. **Low Latency**: Phản hồi nhanh <100ms per request
7. **Clean Code**: Type hints, documentation đầy đủ
8. **Production Ready**: Error handling, logging, monitoring

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    MULTI-CAMERA LAYER                  │
├─────────────────────────────────────────────────────────┤
│  Camera 1  │  Camera 2  │  Camera 3  │  ...  │  Camera N │
└────────────┴─────────────┴─────────────┴───────┴─────────┘
                    ↓                         ↓
┌─────────────────────────────────────────────────────────┐
│              FACE PROCESSING SERVICE                    │
├─────────────────────────────────────────────────────────┤
│  • Face Detection (MTCNN/MediaPipe)                    │
│  • Feature Extraction (FaceNet/DLib)                    │
│  • Queue Management                                     │
│  • Batch Processing                                     │
└─────────────────────────────────────────────────────────┘
                    ↓                         ↓
┌─────────────────────────────────────────────────────────┐
│         GENDER/AGE CLASSIFICATION SERVICE                │
├─────────────────────────────────────────────────────────┤
│  • Gender Classifier (HuggingFace/MLP)                 │
│  • Age Predictor (Regression/Classification)            │
│  • Result Aggregation                                   │
└─────────────────────────────────────────────────────────┘
                    ↓                         ↓
┌─────────────────────────────────────────────────────────┐
│              RESULT STORAGE SERVICE                     │
├─────────────────────────────────────────────────────────┤
│  • Database (PostgreSQL/MongoDB)                       │
│  • Cache (Redis)                                        │
│  • File Storage (CSV/JSON)                              │
└─────────────────────────────────────────────────────────┘
                    ↓                         ↓
┌─────────────────────────────────────────────────────────┐
│              MONITORING & LOGGING                        │
├─────────────────────────────────────────────────────────┤
│  • Prometheus Metrics                                  │
│  • Structured Logging                                  │
│  • Error Tracking                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
gender_analysis/
├── README.md                           # Main documentation
├── requirements.txt                     # Dependencies
├── .env.example                        # Environment variables
│
├── config/
│   ├── __init__.py
│   ├── settings.py                      # Configuration management
│   └── camera_config.py                # Camera configurations
│
├── core/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── face.py                       # Face detection models
│   │   ├── gender.py                     # Gender classification
│   │   └── age.py                        # Age estimation
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_processing.py           # Face detection service
│   │   ├── feature_extraction.py        # Feature extraction
│   │   ├── classification.py             # Gender/age classification
│   │   └── result_handler.py            # Result processing
│   │
│   └── utils/
│       ├── __init__.py
│       ├── queue_manager.py              # Queue management
│       ├── batch_processor.py            # Batch processing
│       └── performance_monitor.py       # Performance tracking
│
├── workers/
│   ├── __init__.py
│   ├── camera_worker.py                 # Camera processing worker
│   ├── face_worker.py                   # Face detection worker
│   └── classification_worker.py         # Classification worker
│
├── api/
│   ├── __init__.py
│   ├── main.py                          # FastAPI application
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── health.py                    # Health check
│   │   ├── camera.py                    # Camera endpoints
│   │   └── results.py                   # Results endpoints
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── face.py                      # Face schemas
│       ├── gender.py                    # Gender schemas
│       └── age.py                       # Age schemas
│
├── storage/
│   ├── __init__.py
│   ├── database.py                      # Database connection
│   ├── cache.py                         # Cache layer
│   └── file_writer.py                   # File storage
│
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py                       # Prometheus metrics
│   ├── logger.py                        # Structured logging
│   └── health_check.py                  # Health monitoring
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_face_processing.py
│   │   ├── test_classification.py
│   │   └── test_services.py
│   │
│   ├── integration/
│   │   ├── test_multi_camera.py
│   │   └── test_pipeline.py
│   │
│   └── fixtures/
│       └── sample_data/
│
├── scripts/
│   ├── deploy.sh                         # Deployment script
│   ├── setup_env.sh                      # Environment setup
│   └── run_tests.sh                      # Test runner
│
└── docs/
    ├── architecture.md                   # This file
    ├── api_reference.md                  # API documentation
    ├── deployment.md                     # Deployment guide
    └── DEVELOPMENT.md                    # Development guide
```

---

## 🔧 Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Main language |
| **API Framework** | FastAPI | 0.104+ | REST API |
| **Async Runtime** | asyncio | Built-in | Async processing |
| **Message Queue** | Redis/RabbitMQ | Latest | Task queue |
| **Database** | PostgreSQL | 15+ | Data storage |
| **Cache** | Redis | 7+ | Fast caching |
| **Monitoring** | Prometheus | Latest | Metrics |
| **Logging** | structlog | Latest | Structured logs |

### ML/AI Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| **OpenCV** | Computer vision | 4.12+ |
| **MTCNN** | Face detection | 0.1.1 |
| **face_recognition** | Face features | 1.3.0 |
| **DeepFace** | Face analysis | 0.0.79 |
| **transformers** | HuggingFace models | 4.35+ |
| **torch** | PyTorch | 2.1+ |

---

## 🎯 Service Architecture

### 1. Camera Processing Service

**Purpose**: Nhận video streams từ nhiều camera, phát hiện person và face

**Responsibilities**:
- Nhận video frames từ cameras
- Person detection (MobileNetSSD)
- Face detection (MTCNN/MediaPipe)
- Crop face regions
- Gửi face crops đến Feature Extraction Service

**Input**: Video frames từ cameras  
**Output**: Face crops + metadata (camera_id, person_id, timestamp)

**Tech Stack**:
- FastAPI with WebSocket support
- OpenCV for video processing
- MTCNN for face detection
- Threading for multi-camera

### 2. Face Feature Extraction Service

**Purpose**: Trích xuất đặc trưng khuôn mặt một lần duy nhất

**Responsibilities**:
- Nhận face crops
- Extract face embeddings (128-dim hoặc 512-dim)
- Cache features để tránh extract lại
- Gửi features đến Classification Service

**Input**: Face crops (image)  
**Output**: Face embeddings (vector) + metadata

**Tech Stack**:
- FaceNet hoặc DLib face_recognition
- NumPy for array operations
- Redis for caching

**Key Feature**: Extract features ONCE, reuse for multiple analyses

### 3. Gender/Age Classification Service

**Purpose**: Phân tích giới tính và độ tuổi từ face features

**Responsibilities**:
- Nhận face embeddings
- Gender classification (male/female)
- Age estimation (continuous value)
- Confidence scoring
- Gửi kết quả đến Result Storage

**Input**: Face embeddings  
**Output**: Gender + Age + Confidence scores

**Tech Stack**:
- HuggingFace models (gender-classification)
- Scikit-learn MLP classifier
- PyTorch/TensorFlow for inference

### 4. Result Storage Service

**Purpose**: Lưu trữ và quản lý kết quả phân tích

**Responsibilities**:
- Lưu results vào database
- Cache popular queries
- Export to CSV/JSON
- API để query results

**Input**: Analysis results  
**Output**: Stored data + query APIs

**Tech Stack**:
- PostgreSQL for structured data
- Redis for caching
- Pandas for data manipulation

---

## 🔄 Workflow Design

### Complete Pipeline

```
┌────────────────────────────────────────────────────────┐
│  CAMERA LAYER (Multiple Cameras)                      │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Camera 1 ─────┐                                        │
│  Camera 2 ─────┤                                       │
│  Camera 3 ─────┼──→ Video Frames                       │
│  Camera N ─────┤                                       │
│                                                         │
└────────────────────────────────────────────────────────┘
                    ↓ (WebSocket/RTSP)
┌────────────────────────────────────────────────────────┐
│  CAMERA WORKER (Parallel Processing)                  │
├────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Worker 1    │  │ Worker 2    │  │ Worker 3    │    │
│  │ Camera 1    │  │ Camera 2    │  │ Camera 3    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  • Receive frames                                     │
│  • Person detection (MobileNetSSD)                  │
│  • Centroid tracking                                  │
│  • Send to Face Processing                            │
└────────────────────────────────────────────────────────┘
                    ↓ (Queue)
┌────────────────────────────────────────────────────────┐
│  FACE PROCESSING SERVICE                               │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │ Queue: Face Crops                              │   │
│  │ ├─ camera_id, person_id, face_crop, timestamp │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ Batch Processing (10 faces per batch)           │   │
│  │ ├─ Extract features (FaceNet)                  │   │
│  │ ├─ Batch inference: 10 faces → 10 vectors    │   │
│  │ └─ VERY FAST: ~50ms per batch                  │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ Cache features in TrackableObject               │   │
│  │ ├─ person_id → face_features (128-dim)         │   │
│  │ ├─ Extract ONCE per person                     │   │
│  │ └─ Reuse for subsequent analysis               │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
                    ↓ (Queue)
┌────────────────────────────────────────────────────────┐
│  CLASSIFICATION SERVICE                                │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │ Queue: Face Features                           │   │
│  │ ├─ person_id, face_features (128-dim)         │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ Gender Classifier                               │   │
│  │ ├─ Input: 128-dim face_features                │   │
│  │ ├─ Model: rizvandwiki/gender-classification   │   │
│  │ ├─ OR: Lightweight MLP (offline)              │   │
│  │ └─ Output: male/female + confidence           │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ Age Predictor                                   │   │
│  │ ├─ Input: Same 128-dim features               │   │
│  │ ├─ Model: Regression model                    │   │
│  │ └─ Output: age + confidence                   │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ Update TrackableObject                          │   │
│  │ ├─ person.gender = "male"                     │   │
│  │ ├─ person.age = 25                            │   │
│  │ ├─ person.gender_confidence = 0.95             │   │
│  │ └─ person.age_confidence = 0.88                │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────────────┐
│  RESULT STORAGE                                         │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐   │
│  │ PostgreSQL Database                              │   │
│  │ Table: person_analysis                            │   │
│  │ ├─ id, camera_id, person_id                     │   │
│  │ ├─ timestamp, gender, age                       │   │
│  │ ├─ gender_confidence, age_confidence            │   │
│  │ └─ location, direction                          │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ Redis Cache                                     │   │
│  │ ├─ Recent results (1 hour TTL)                │   │
│  │ └─ Fast query for dashboard                    │   │
│  └────────────────────────────────────────────────┘   │
│                    ↓                                   │
│  ┌────────────────────────────────────────────────┐   │
│  │ CSV Export                                      │   │
│  │ ├─ Daily/hourly reports                        │   │
│  │ └─ Analytics-ready data                        │   │
│  └────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### PostgreSQL Tables

```sql
-- Main analysis results table
CREATE TABLE person_analysis (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) NOT NULL,
    person_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    gender VARCHAR(10) NOT NULL,  -- 'male' or 'female'
    gender_confidence FLOAT NOT NULL,
    age INTEGER NOT NULL,
    age_confidence FLOAT NOT NULL,
    location VARCHAR(100),
    direction VARCHAR(20),  -- 'IN' or 'OUT'
    face_features JSONB,  -- Store 128-dim vector
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_camera_person (camera_id, person_id),
    INDEX idx_timestamp (timestamp)
);

-- Camera configurations
CREATE TABLE cameras (
    camera_id VARCHAR(50) PRIMARY KEY,
    camera_name VARCHAR(100) NOT NULL,
    stream_url TEXT NOT NULL,
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Daily statistics
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_people INTEGER DEFAULT 0,
    male_count INTEGER DEFAULT 0,
    female_count INTEGER DEFAULT 0,
    avg_age FLOAT,
    hour_breakdown JSONB,  -- Hourly statistics
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(camera_id, date)
);
```

### Redis Cache Structure

```redis
# Face features cache (avoid re-extraction)
face:features:{person_id}:{camera_id} → {
    "features": [128-dim array],
    "timestamp": "2024-10-26T10:30:00",
    "extraction_time": 0.005  # seconds
}

# Recent results (1 hour TTL)
results:recent:{camera_id} → [
    {"person_id": 1, "gender": "male", "age": 25, ...},
    {"person_id": 2, "gender": "female", "age": 30, ...}
]
```

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)

**Milestones**:
- [ ] Set up project structure
- [ ] Install and configure dependencies
- [ ] Implement basic configuration management
- [ ] Set up database schema
- [ ] Create basic logging and monitoring

**Deliverables**:
- Project structure created
- Database tables ready
- Basic API skeleton
- Environment configuration

### Phase 2: Core Services (Week 2)

**Milestones**:
- [ ] Implement Camera Processing Service
- [ ] Implement Face Detection Service
- [ ] Implement Feature Extraction Service
- [ ] Unit tests for services

**Deliverables**:
- Face detection working
- Feature extraction working
- Tests passing

### Phase 3: Classification (Week 3)

**Milestones**:
- [ ] Implement Gender Classification
- [ ] Implement Age Estimation
- [ ] Integration testing
- [ ] Performance optimization

**Deliverables**:
- Gender/Age detection working
- Accuracy validation
- Performance benchmarks

### Phase 4: Multi-Camera & Parallel (Week 4)

**Milestones**:
- [ ] Implement multi-camera support
- [ ] Implement parallel processing
- [ ] Queue management
- [ ] Load testing

**Deliverables**:
- Multiple cameras working
- Parallel processing optimized
- Stress testing results

### Phase 5: Production Ready (Week 5)

**Milestones**:
- [ ] Error handling
- [ ] Monitoring & alerting
- [ ] Documentation
- [ ] Deployment scripts

**Deliverables**:
- Production-ready system
- Full documentation
- Deployment guide

---

## 🔒 Error Handling Strategy

### Error Types

1. **Camera Errors**: Connection lost, stream down
2. **Face Detection Errors**: No face found, low quality
3. **Classification Errors**: Low confidence, ambiguous
4. **System Errors**: Memory, disk, network

### Handling Approach

```python
# Structured error handling
try:
    result = process_face(crop)
except FaceDetectionError:
    # Retry with different model
    result = fallback_detection(crop)
except ClassificationError:
    # Return low confidence result
    result = {"gender": "unknown", "confidence": 0.5}
except SystemError:
    # Log and skip
    logger.error("System error, skipping")
    continue
```

---

## 📈 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Face Detection** | < 15ms | Per face |
| **Feature Extraction** | < 10ms | Per face |
| **Gender Classification** | < 5ms | Per face |
| **Age Estimation** | < 5ms | Per face |
| **Total Latency** | < 50ms | End-to-end |
| **Throughput** | > 100 faces/sec | Per worker |
| **Memory** | < 2GB | Per service |
| **CPU** | < 80% | Average |

---

## 📝 Code Standards

### Type Hints (100% Coverage)

```python
def extract_face_features(
    face_crop: np.ndarray,
    model: Callable[[np.ndarray], np.ndarray]
) -> Tuple[np.ndarray, float]:
    """
    Extract face features from cropped face image.
    
    Args:
        face_crop: Face image as numpy array (BGR format)
        model: Face embedding model function
        
    Returns:
        Tuple of (features: 128-dim vector, confidence: float)
        
    Raises:
        ValueError: If face crop is invalid
        ModelError: If feature extraction fails
    """
    # Implementation
```

### Documentation Style

- Google-style docstrings
- Inline comments for complex logic
- Type hints for all functions
- Error documentation
- Usage examples

---

## 🎯 Success Criteria

- ✅ Support 10+ cameras simultaneously
- ✅ Process 100+ faces per second
- ✅ < 50ms end-to-end latency
- ✅ 95%+ gender accuracy
- ✅ Age MAE < 5 years
- ✅ 99.9% uptime
- ✅ Clean, documented code
- ✅ Production ready

---

**Next Steps**: Begin Phase 1 implementation

