# Chi Tiết Các Nhiệm Vụ Nâng Cấp

**Date**: 2024-10-27  
**Plan**: 3-week implementation

---

## 📅 Timeline Overview

```
Week 1: DNN Face Detector (HIGH PRIORITY)
Week 2: Fallback Strategy (MEDIUM PRIORITY)
Week 3: Optimization & Polish (LOW PRIORITY)
```

---

## 🎯 Week 1: DNN Face Detection

### Day 1: Setup DNN Models

**Tasks**:
- [ ] Research available DNN face detection models
- [ ] Download OpenCV DNN models
- [ ] Setup model directory structure
- [ ] Test model loading

**Commands**:
```bash
mkdir -p gender_analysis/models
cd gender_analysis/models

# Download OpenCV face detector
wget https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel

# Or use mediapipe (better alternative)
pip install mediapipe
```

**Deliverable**: Models downloaded and ready

---

### Day 2: Implement DNNFaceDetector

**Tasks**:
- [ ] Create `DNNFaceDetector` class
- [ ] Implement detection method
- [ ] Add confidence threshold
- [ ] Test on sample images

**File**: `gender_analysis/core/services/face_detectors/dnn_face.py`

**Code Structure**:
```python
class DNNFaceDetector:
    def __init__(self, confidence=0.5):
        self.conf_threshold = confidence
        self.net = None
        self._load_model()
    
    def detect(self, image):
        # Detect faces with DNN
        pass
    
    def _load_model(self):
        # Load pre-trained model
        pass
```

**Testing**: 
```python
# Test on sample images
python test_dnn_face_detector.py
```

---

### Day 3: Integration

**Tasks**:
- [ ] Integrate DNNFaceDetector into PersonAnalysisService
- [ ] Update classification.py
- [ ] Add fallback logic
- [ ] Test integration

**File Updates**:
- `gender_analysis/core/services/classification.py`
- `gender_analysis/core/services/face_processing.py`

**Integration**:
```python
# In PersonAnalysisService
def __init__(self):
    self.face_detector = DNNFaceDetector()  # New
    # or
    self.face_detector = HaarFaceDetector()  # Fallback
```

---

### Day 4: Testing & Validation

**Tasks**:
- [ ] Test on shopping_korea.mp4
- [ ] Test on other videos
- [ ] Measure success rate
- [ ] Compare with Haar Cascade

**Testing**:
```bash
# Test on shopping_korea
python analyze_shopping_korea_full.py

# Measure results
python test_face_detection_accuracy.py
```

**Expected Results**:
- Success rate: > 80%
- Gender data available
- Age data available

---

### Day 5: Documentation

**Tasks**:
- [ ] Document DNN usage
- [ ] Create usage examples
- [ ] Update API docs
- [ ] Commit changes

**Files**:
- `UPGRADE_WEEK1_COMPLETE.md`
- `docs/DNN_USAGE.md`

---

## 🎯 Week 2: Fallback Strategy

### Day 1-2: Research & Design

**Tasks**:
- [ ] Research body-based gender estimation
- [ ] Choose best approach
- [ ] Design BodyGenderEstimator class
- [ ] Plan training data

**Research Topics**:
- Whole-body gender recognition
- CNN-based approaches
- Traditional feature-based methods

---

### Day 3-4: Implementation

**Tasks**:
- [ ] Implement BodyGenderEstimator
- [ ] Add body feature extraction
- [ ] Train/predict model
- [ ] Integrate as fallback

**File**: `gender_analysis/core/services/body_gender.py`

---

### Day 5: Testing

**Tasks**:
- [ ] Test fallback mechanism
- [ ] Measure accuracy
- [ ] Compare with face-based
- [ ] Document results

---

## 🎯 Week 3: Optimization

### Day 1-2: Multi-Scale Detection

**Tasks**:
- [ ] Implement multi-scale face detection
- [ ] Test on various videos
- [ ] Optimize parameters
- [ ] Measure improvement

---

### Day 3-4: Preprocessing

**Tasks**:
- [ ] Implement image enhancement
- [ ] Test preprocessing effects
- [ ] Optimize parameters
- [ ] Integrate

---

### Day 5: Final Testing

**Tasks**:
- [ ] End-to-end testing
- [ ] Performance profiling
- [ ] Final optimizations
- [ ] Complete documentation

---

## 📊 Success Metrics

### Weekly Targets

**Week 1**:
- DNN face detector working
- Success rate > 50%
- Gender/age data available

**Week 2**:
- Fallback mechanism active
- Coverage improved
- Success rate > 70%

**Week 3**:
- Fully optimized
- Success rate > 80%
- Production-ready

---

## 🔧 Technical Details

### DNN Face Detector Implementation

**File**: `gender_analysis/core/services/face_detectors/dnn_face.py`

```python
import cv2
import numpy as np

class DNNFaceDetector:
    def __init__(self, confidence=0.5, nms=0.4):
        self.conf_threshold = confidence
        self.nms_threshold = nms
        self.net = None
        self.input_size = (300, 300)
        self._load_model()
    
    def _load_model(self):
        """Load DNN face detection model."""
        config = "models/opencv_face_detector.pbtxt"
        model = "models/opencv_face_detector_uint8.pb"
        
        try:
            self.net = cv2.dnn.readNet(model, config)
            print("✅ DNN face detector loaded")
        except Exception as e:
            print(f"❌ Failed to load DNN model: {e}")
            self.net = None
    
    def detect(self, image):
        """Detect faces in image."""
        if self.net is None:
            return []
        
        h, w = image.shape[:2]
        
        # Create blob
        blob = cv2.dnn.blobFromImage(
            image, 1.0, self.input_size,
            [104, 117, 123], False, False
        )
        
        # Inference
        self.net.setInput(blob)
        detections = self.net.forward()
        
        # Process detections
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.conf_threshold:
                # Get bounding box
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * w)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * w)
                
                width = x2 - x1
                height = y2 - y1
                
                faces.append({
                    'box': (x1, y1, width, height),
                    'confidence': float(confidence)
                })
        
        return faces
```

---

## 🧪 Testing Plan

### Test 1: Basic Detection
```python
# Test DNN on sample images
python test_dnn_basic.py
```

### Test 2: Integration
```python
# Test with PersonAnalysisService
python test_integration.py
```

### Test 3: Video Testing
```python
# Test on shopping_korea.mp4
python test_shopping_korea_dnn.py
```

### Test 4: Performance
```python
# Measure FPS and accuracy
python test_performance.py
```

---

## 📈 Progress Tracking

### Daily Checklist

**Week 1**:
- [ ] Day 1: Models downloaded
- [ ] Day 2: DNN detector implemented
- [ ] Day 3: Integration complete
- [ ] Day 4: Testing done
- [ ] Day 5: Documentation complete

**Week 2**:
- [ ] Day 1-2: Research done
- [ ] Day 3-4: Fallback implemented
- [ ] Day 5: Testing complete

**Week 3**:
- [ ] Day 1-2: Multi-scale done
- [ ] Day 3-4: Preprocessing done
- [ ] Day 5: Final testing complete

---

## ✅ Deliverables

### Week 1
1. DNNFaceDetector class
2. Integration with PersonAnalysisService
3. Test results
4. Documentation

### Week 2
1. BodyGenderEstimator class
2. Fallback mechanism
3. Test results
4. Documentation

### Week 3
1. Optimized pipeline
2. Performance report
3. Final documentation
4. Production-ready system

---

**Ready to start Week 1!** 🚀

