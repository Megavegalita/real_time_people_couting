# Kế Hoạch Nâng Cấp Chất Lượng Phân Tích

**Date**: 2024-10-27  
**Priority**: High  
**Status**: Planning

---

## 🎯 Objectives

### Primary Goals
1. ✅ Fix face detection cho video góc rộng
2. ✅ Implement gender & age prediction
3. ✅ Improve detection accuracy
4. ✅ Support multiple camera configurations

### Success Criteria
- Face detection success rate: > 80%
- Gender prediction accuracy: > 70%
- Age estimation accuracy: ±5 years
- Processing speed: > 20 FPS

---

## 📊 Current Issues

### Issue 1: Face Detection Failing
- **Problem**: People too distant, faces 20-40px (need 50px minimum)
- **Impact**: No gender/age data
- **Priority**: HIGH

### Issue 2: Limited to Haar Cascade
- **Problem**: Old technology, poor for small faces
- **Impact**: Limited detection capability
- **Priority**: HIGH

### Issue 3: No Fallback Mechanism
- **Problem**: Single detection method
- **Impact**: All-or-nothing approach
- **Priority**: MEDIUM

---

## 🔧 Proposed Solutions

### Solution 1: DNN Face Detection (Priority: HIGH)

**Technology**: OpenCV DNN Face Detector  
**Benefits**:
- Can detect faces 20-30 pixels (vs 50px for Haar)
- Better accuracy for small/distant faces
- Modern deep learning approach

**Implementation**:
```python
# Phase 1: Download DNN models
config_url = "deploy.prototxt"
model_url = "res10_300x300_ssd_iter_140000.caffemodel"

# Phase 2: Integrate DNN detector
class DNNFaceDetector:
    def __init__(self):
        self.net = cv2.dnn.readNet(model_path, config_path)
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4
    
    def detect(self, image):
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300))
        self.net.setInput(blob)
        detections = self.net.forward()
        # Process and return faces
```

**Timeline**: 2-3 hours  
**Resources**: OpenCV, pretrained models

---

### Solution 2: Body-Based Gender Estimation (Priority: MEDIUM)

**Technology**: Deep learning on body features  
**Benefits**:
- Works for distant people (no face needed)
- Alternative when face detection fails
- Good for surveillance scenarios

**Implementation**:
```python
# Use whole-body features for gender
class BodyGenderEstimator:
    def estimate_gender(self, person_crop):
        # Extract body features
        # Use CNN or traditional ML
        # Return gender prediction
        pass
```

**Timeline**: 3-4 hours  
**Resources**: Training data, ML model

---

### Solution 3: Multi-Scale Detection (Priority: MEDIUM)

**Technology**: Multiple detection scales  
**Benefits**:
- Detect faces at various distances
- Auto-adjust to video characteristics
- Improve coverage

**Implementation**:
```python
def detect_faces_multi_scale(image):
    # Try multiple scales
    scales = [1.0, 0.75, 0.5, 2.0]
    all_faces = []
    
    for scale in scales:
        scaled = cv2.resize(image, (0,0), fx=scale, fy=scale)
        faces = detector.detect(scaled)
        # Rescale back to original
        all_faces.extend(faces)
    
    return all_faces
```

**Timeline**: 1-2 hours  
**Resources**: None

---

### Solution 4: Image Preprocessing (Priority: LOW)

**Technology**: Enhancement before detection  
**Benefits**:
- Improve face visibility
- Increase detection rate
- Low cost

**Implementation**:
```python
def preprocess_for_face_detection(image):
    # Enhance contrast
    image = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
    
    # Sharpen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    image = cv2.filter2D(image, -1, kernel)
    
    # Denoise
    image = cv2.bilateralFilter(image, 9, 75, 75)
    
    return image
```

**Timeline**: 1 hour  
**Resources**: None

---

## 📅 Implementation Plan

### Phase 1: Quick Win (Week 1)
**Duration**: 1 week  
**Focus**: DNN Face Detector

#### Day 1-2: Setup DNN
- Download models
- Implement DNNFaceDetector class
- Test on sample images

#### Day 3-4: Integration
- Integrate with PersonAnalysisService
- Update classification.py
- Test on shopping_korea.mp4

#### Day 5: Testing
- Test on multiple videos
- Measure success rate
- Compare with Haar Cascade

**Deliverables**:
- DNNFaceDetector implementation
- Updated classification service
- Test results

---

### Phase 2: Backup Strategy (Week 2)
**Duration**: 1 week  
**Focus**: Body-based estimation

#### Day 1-2: Research
- Survey body-based gender models
- Choose best approach
- Setup training data

#### Day 3-4: Implementation
- Implement body feature extraction
- Train/predict gender
- Integrate as fallback

#### Day 5: Testing
- Test fallback mechanism
- Measure accuracy
- Document results

**Deliverables**:
- BodyGenderEstimator class
- Fallback mechanism
- Accuracy report

---

### Phase 3: Optimization (Week 3)
**Duration**: 1 week  
**Focus**: Performance & accuracy

#### Day 1-2: Multi-scale detection
- Implement multi-scale
- Test on various videos
- Measure improvement

#### Day 3-4: Preprocessing
- Implement image enhancement
- Test preprocessing effects
- Optimize parameters

#### Day 5: End-to-end testing
- Full pipeline testing
- Performance measurement
- Final optimization

**Deliverables**:
- Optimized pipeline
- Performance report
- Final documentation

---

## 💰 Resource Requirements

### Technical Resources
1. **Models**: DNN face detector models (~10MB)
2. **Training data**: Gender/age datasets (if needed)
3. **GPU**: Optional for faster processing

### Human Resources
1. **Developer**: 1 person, 3 weeks part-time
2. **Tester**: 1 person, 3 weeks part-time

### Budget
- Models: Free (open source)
- Development time: ~60 hours
- Testing time: ~20 hours
- **Total**: ~80 hours

---

## 📋 Task Breakdown

### Task 1: DNN Face Detector (Priority: P0)
- [ ] Download DNN models
- [ ] Implement DNNFaceDetector
- [ ] Test on sample images
- [ ] Integrate with classification service
- [ ] Test on shopping_korea.mp4
- [ ] Measure success rate

**Time**: 10-15 hours  
**Risk**: Low  
**Impact**: High

---

### Task 2: Body-Based Gender (Priority: P1)
- [ ] Research models
- [ ] Choose approach
- [ ] Implement BodyGenderEstimator
- [ ] Train/predict
- [ ] Test as fallback
- [ ] Measure accuracy

**Time**: 15-20 hours  
**Risk**: Medium  
**Impact**: Medium

---

### Task 3: Multi-Scale Detection (Priority: P2)
- [ ] Implement multi-scale
- [ ] Test various scales
- [ ] Optimize parameters
- [ ] Test on videos

**Time**: 5-10 hours  
**Risk**: Low  
**Impact**: Medium

---

### Task 4: Image Preprocessing (Priority: P3)
- [ ] Implement enhancement
- [ ] Test preprocessing
- [ ] Optimize parameters
- [ ] Integrate

**Time**: 5-10 hours  
**Risk**: Low  
**Impact**: Low

---

## 🎯 Success Metrics

### Face Detection
- **Current**: 0% success rate
- **Target**: > 80% success rate
- **Measurement**: Test on 100 video frames

### Gender Prediction
- **Current**: N/A
- **Target**: > 70% accuracy
- **Measurement**: Compare with ground truth

### Age Estimation
- **Current**: N/A
- **Target**: ±5 years accuracy
- **Measurement**: MAE metric

### Performance
- **Current**: 20+ FPS
- **Target**: Maintain 20+ FPS
- **Measurement**: Profile execution

---

## 🚀 Implementation Steps

### Week 1: DNN Integration
```bash
# Day 1-2: Setup
cd gender_analysis/core/services
mkdir face_detectors
# Download DNN models
# Create DNNFaceDetector class

# Day 3-4: Integration
# Update PersonAnalysisService
# Add DNN as primary detector
# Test integration

# Day 5: Testing
python test_dnn_integration.py
python test_shopping_korea.py
```

### Week 2: Fallback Strategy
```bash
# Day 1-2: Research
# Survey body-based models
# Choose best approach

# Day 3-4: Implementation
# Create BodyGenderEstimator
# Implement fallback logic
# Test on shopping_korea.mp4

# Day 5: Testing
python test_fallback.py
```

### Week 3: Optimization
```bash
# Day 1-2: Multi-scale
# Implement multi-scale detection
# Test on multiple videos

# Day 3-4: Preprocessing
# Implement image enhancement
# Optimize parameters

# Day 5: Final testing
python test_full_pipeline.py
```

---

## 📊 Risk Assessment

### Risk 1: DNN Performance
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Use lightweight model, optimize parameters

### Risk 2: Accuracy Issues
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Multiple models, ensemble approach

### Risk 3: Performance Degradation
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Profile & optimize, use caching

---

## ✅ Expected Outcomes

### After Phase 1
- Face detection working on shopping_korea.mp4
- Gender/age data available
- Improved success rate

### After Phase 2
- Fallback mechanism active
- Multi-method detection
- Better coverage

### After Phase 3
- Optimized pipeline
- Best performance
- Production-ready

---

## 🎯 Timeline Summary

| Phase | Duration | Focus | Deliverable |
|-------|----------|-------|-------------|
| 1 | Week 1 | DNN Integration | Working face detection |
| 2 | Week 2 | Fallback | Body-based gender |
| 3 | Week 3 | Optimization | Final system |
| **Total** | **3 weeks** | **Complete** | **Production-ready** |

---

## 📝 Next Steps

1. **Approve plan** ✅
2. **Start Phase 1**: DNN Integration
3. **Daily updates**: Progress tracking
4. **Weekly review**: Results & adjustments

**Ready to start Phase 1!** 🚀

