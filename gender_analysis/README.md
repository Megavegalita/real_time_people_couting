# Gender & Age Analysis System

Multi-Camera Face Feature Analysis for Gender and Age Detection

---

## 📋 Overview

This system analyzes face features to determine gender and age for multiple camera streams simultaneously. Built with microservices architecture, parallel processing, and high-performance design.

**Key Features**:
- 🎥 Multi-camera support
- 👤 Face feature extraction (one-time)
- ♂️ Gender classification
- 🎂 Age estimation
- ⚡ High throughput (> 100 faces/sec)
- 🔄 Microservices architecture
- 📊 Real-time monitoring

---

## 🏗️ Architecture

```
Multi-Camera → Face Detection → Feature Extraction (ONCE)
                                        ↓
                              Gender/Age Classification
                                        ↓
                                Result Storage
```

### Key Principle
**Extract face features ONCE, reuse for all analyses** - This dramatically reduces processing time.

---

## 🚀 Quick Start

### 1. Installation

```bash
cd gender_analysis
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Database Setup

```bash
# Create database
createdb gender_analysis

# Run migrations (TODO: after Phase 1)
alembic upgrade head
```

### 4. Run API

```bash
python -m api.main
```

Visit: http://localhost:8001/docs

---

## 📁 Project Structure

```
gender_analysis/
├── config/           # Configuration management
├── core/
│   ├── models/      # ML models (face, gender, age)
│   ├── services/    # Business logic services
│   └── utils/        # Utility functions
├── workers/         # Parallel workers
├── api/             # FastAPI application
├── storage/         # Database and cache
├── monitoring/      # Logging and metrics
└── tests/           # Test suites

```

---

## 🧪 Testing

### Phase 1 Tests

```bash
# Run Phase 1 tests
pytest tests/unit/test_phase1/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

See `tests/PHASE_1_TEST_PLAN.md` for details.

---

## 📊 Performance Targets

| Component | Target | Status |
|-----------|--------|--------|
| Face Detection | < 15ms | ⏳ |
| Feature Extraction | < 10ms | ⏳ |
| Gender Classification | < 5ms | ⏳ |
| Age Estimation | < 5ms | ⏳ |
| **Total Latency** | **< 50ms** | ⏳ |
| **Throughput** | **> 100 faces/sec** | ⏳ |

---

## 📝 Development Phases

### Phase 1: Foundation (Week 1) ✅
- Project structure
- Dependencies
- Configuration
- Database setup
- Basic API

### Phase 2: Core Services (Week 2) ⏳
- Face detection
- Feature extraction
- Services integration

### Phase 3: Classification (Week 3) ⏳
- Gender classification
- Age estimation
- Accuracy validation

### Phase 4: Multi-Camera (Week 4) ⏳
- Parallel processing
- Queue management
- Load testing

### Phase 5: Production (Week 5) ⏳
- Error handling
- Monitoring
- Documentation
- Deployment

---

## 📚 Documentation

- **Architecture**: `docs/development/gender_detection_architecture.md`
- **Test Plans**: `docs/TEST_PLANS.md`
- **API Docs**: http://localhost:8001/docs

---

## 🔧 Configuration

See `.env.example` for all configuration options:

- Database connection
- Redis configuration
- Model selection
- Processing parameters
- Logging settings

---

## 🧪 Test Plans

Each phase has comprehensive test plans:

1. `tests/PHASE_1_TEST_PLAN.md` - Foundation tests
2. `tests/PHASE_2_TEST_PLAN.md` - Core services tests
3. `tests/PHASE_3_TEST_PLAN.md` - Classification tests
4. `tests/PHASE_4_TEST_PLAN.md` - Multi-camera tests
5. `tests/PHASE_5_TEST_PLAN.md` - Production tests

---

## 📈 Status

**Current Phase**: Phase 1 (Foundation)  
**Status**: ⏳ In Progress  
**Tests**: Phase 1 test plan ready  
**Next**: Implement core services

---

## 🎯 Goals

- ✅ Clean code with type hints
- ✅ Comprehensive documentation
- ✅ 85%+ test coverage
- ✅ Production-ready performance
- ✅ Microservices architecture

---

**Version**: 1.0.0  
**Last Updated**: 2024-10-26  
**Status**: Development

