# Phase 1 Test Plan - Foundation

**Phase**: Foundation  
**Duration**: Week 1  
**Status**: In Progress

---

## 📋 Test Objectives

Verify that Phase 1 implementation meets all requirements:
- [ ] Project structure created correctly
- [ ] Dependencies installed successfully
- [ ] Configuration management working
- [ ] Database connection established
- [ ] Basic API skeleton functional
- [ ] Health check endpoint working
- [ ] Logging and monitoring setup

---

## 🧪 Test Cases

### 1. Project Structure Validation

**Objective**: Verify all directories and files are created correctly

**Test Steps**:
```bash
# Check directory structure
tree gender_analysis/

# Verify all __init__.py files exist
find gender_analysis -name "__init__.py" | wc -l
# Expected: All modules have __init__.py

# Verify requirements.txt exists
test -f gender_analysis/requirements.txt
```

**Expected Results**:
- ✅ All directories exist
- ✅ All __init__.py files present
- ✅ requirements.txt exists
- ✅ .env.example exists
- ✅ config/settings.py exists

---

### 2. Dependencies Installation

**Objective**: Install and verify all dependencies

**Test Steps**:
```bash
cd gender_analysis
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Verify critical packages
python -c "import fastapi; print(fastapi.__version__)"
python -c "import opencv; print(opencv.__version__)"
python -c "import face_recognition; print(face_recognition.__version__)"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

**Expected Results**:
- ✅ venv created successfully
- ✅ All packages installed without errors
- ✅ Critical packages import successfully
- ✅ No version conflicts

**Performance Criteria**:
- Installation time < 5 minutes
- No security warnings for critical packages

---

### 3. Configuration Management

**Objective**: Test configuration loading and validation

**Test Steps**:
```python
# Test default settings
from config.settings import settings

# Check all sub-configurations exist
assert settings.database is not None
assert settings.redis is not None
assert settings.api is not None
assert settings.face_detection is not None
assert settings.feature_extraction is not None
assert settings.gender_classification is not None
assert settings.age_estimation is not None
assert settings.processing is not None
assert settings.logging is not None
assert settings.monitoring is not None
assert settings.camera is not None

# Check default values
assert settings.api.port == 8001
assert settings.processing.batch_size == 10
assert settings.face_detection.model == "mtcnn"
```

**Expected Results**:
- ✅ All settings loaded successfully
- ✅ Default values are correct
- ✅ Type validation works
- ✅ Environment variable override works

---

### 4. Database Connection

**Objective**: Verify database connection and schema creation

**Test Steps**:
```python
# Test database connection
from storage.database import db_manager

# Health check
assert db_manager.health_check() == True

# Test session creation
with db_manager.session_scope() as session:
    # Test creating a record
    from storage.database import PersonAnalysis
    from datetime import datetime
    
    test_person = PersonAnalysis(
        camera_id="test_camera_1",
        person_id=1,
        timestamp=datetime.utcnow(),
        gender="male",
        gender_confidence=0.95,
        age=25,
        age_confidence=0.88,
        direction="IN"
    )
    session.add(test_person)
    session.commit()
    
    # Verify record was created
    result = session.query(PersonAnalysis).filter_by(camera_id="test_camera_1").first()
    assert result is not None
    assert result.gender == "male"
    assert result.age == 25

# Clean up
with db_manager.session_scope() as session:
    session.query(PersonAnalysis).filter_by(camera_id="test_camera_1").delete()
```

**Expected Results**:
- ✅ Database connection successful
- ✅ Tables created successfully
- ✅ CRUD operations work
- ✅ Transactions work correctly
- ✅ Connection pooling works

**Performance Criteria**:
- Connection establishment < 500ms
- Insert operation < 100ms
- Query operation < 50ms

---

### 5. Basic API Skeleton

**Objective**: Test basic API endpoints

**Test Steps**:
```python
# Create a simple API endpoint test
from fastapi import FastAPI
from api.endpoints import health

app = FastAPI()
app.include_router(health.router)

# Test with test client
from fastapi.testclient import TestClient
client = TestClient(app)

# Test health endpoint
response = client.get("/health")
assert response.status_code == 200
data = response.json()
assert data["status"] == "healthy"
```

**Expected Results**:
- ✅ API starts successfully
- ✅ Health endpoint responds
- ✅ Response format is correct
- ✅ Proper HTTP status codes

**Performance Criteria**:
- API startup time < 2 seconds
- Health check response time < 50ms

---

### 6. Logging and Monitoring

**Objective**: Verify logging and monitoring setup

**Test Steps**:
```python
from monitoring.logger import setup_logger
import structlog

# Setup logger
logger = setup_logger()

# Test logging
logger.info("Test info message", extra={"test": True})
logger.error("Test error message", extra={"error": "TestError"})

# Verify logs are written to file
import os
assert os.path.exists("logs/gender_analysis.log")

# Check log format
with open("logs/gender_analysis.log", "r") as f:
    first_line = f.readline()
    # Should be in JSON format
    assert "timestamp" in first_line
    assert "level" in first_line
```

**Expected Results**:
- ✅ Logger configured correctly
- ✅ Logs written to file
- ✅ JSON format structured properly
- ✅ Different log levels work

---

## 📊 Success Criteria

### Functional Requirements
- [x] Project structure created
- [ ] All dependencies installed
- [ ] Configuration management works
- [ ] Database connection established
- [ ] API skeleton functional
- [ ] Logging working
- [ ] Monitoring setup

### Performance Requirements
- [ ] API startup < 2 seconds
- [ ] Health check < 50ms
- [ ] Database connection < 500ms
- [ ] No memory leaks

### Quality Requirements
- [ ] No critical errors
- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities

---

## 🧪 Running Tests

### Automated Test Script

```bash
#!/bin/bash
# gender_analysis/scripts/run_phase1_tests.sh

echo "Running Phase 1 Tests..."
echo "=========================="

# Setup
cd gender_analysis
source venv/bin/activate

# Run tests
pytest tests/unit/test_phase1/ -v --cov=config --cov=storage --cov-report=html

# Check results
if [ $? -eq 0 ]; then
    echo "✅ All Phase 1 tests passed!"
else
    echo "❌ Some tests failed"
    exit 1
fi
```

### Manual Testing

```bash
# Test 1: Structure
./scripts/test_structure.sh

# Test 2: Dependencies
./scripts/test_dependencies.sh

# Test 3: Configuration
./scripts/test_configuration.sh

# Test 4: Database
./scripts/test_database.sh

# Test 5: API
./scripts/test_api.sh

# Test 6: Logging
./scripts/test_logging.sh
```

---

## 📈 Test Results Template

```markdown
# Phase 1 Test Results

**Date**: 2024-XX-XX  
**Status**: ✅ PASS / ❌ FAIL

## Summary
- Total Tests: XX
- Passed: XX
- Failed: XX
- Coverage: XX%

## Results
1. Structure Validation: ✅
2. Dependencies: ✅
3. Configuration: ✅
4. Database: ✅
5. API: ✅
6. Logging: ✅

## Issues Found
- None / [List issues]

## Next Steps
- Proceed to Phase 2
- Fix issues (if any)
```

---

**Status**: ⏳ In Progress  
**Next**: Begin Phase 2 once all Phase 1 tests pass

