# Upgrade Plan - 70% Accuracy Target

## Current Status
- Face detection rate: **10%**
- Target: **70%**
- Gap: 60% improvement needed

## Root Cause Analysis
1. **Face too small/distant** in shopping_korea.mp4
2. **Multiple detection methods not fully utilized**
3. **No image preprocessing** (upscaling, enhancement)
4. **Gender/age models are placeholders** (not real detection)

## Upgrade Strategy

### Phase 1: Maximize Face Detection (Target: 50% → 70%)
**Actions**:
1. ✅ Multiple detection methods (MediaPipe, MTCNN, Haar) - already implemented
2. ❌ **Add image upscaling** before detection
3. ❌ **Add contrast enhancement** for small faces
4. ❌ **Tune detection parameters** per method
5. ❌ **Use ROI (Region of Interest) enhancement** in person crop

### Phase 2: Real Gender Classification (Target: Replace placeholder)
**Actions**:
1. ❌ **Download/implement gender classifier model**
   - Options: 
     - Hugging Face model (rizvandwiki/gender-classification)
     - Retrain simple CNN on face features
     - Use facial feature-based heuristics
2. ✅ Ensure consistent assignment per track ID

### Phase 3: Real Age Estimation (Target: Replace placeholder)
**Actions**:
1. ❌ **Download/implement age estimation model**
   - Options:
     - Use lightweight ML model
     - Feature-based estimation
     - Pre-trained model

## Implementation Priority

### Priority 1: Image Preprocessing
```python
def enhance_image_for_detection(img):
    # 1. Upscale 2x for small faces
    # 2. Increase contrast
    # 3. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # 4. Sharpen
    return enhanced_img
```

### Priority 2: Tune Detection Parameters
```python
# MediaPipe: lower confidence threshold
min_detection_confidence=0.05  # was 0.1

# MTCNN: adjust parameters
# Haar: dynamic minSize based on person crop
```

### Priority 3: Multi-Scale Detection
```python
def detect_faces_multi_scale(person_crop):
    # 1. Original crop
    # 2. 1.5x upscaled
    # 3. 2x upscaled
    # Merge results with NMS
```

## Expected Results

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Face detection | 10% | 70% | **7x** |
| Gender accuracy | 0% | >70% | Real detection |
| Age accuracy | 0% | >70% | Real detection |
| Processing FPS | 22 | >15 | Maintain speed |

## Timeline
- Phase 1: 2-3 hours (image preprocessing + tuning)
- Phase 2: 3-4 hours (gender model)
- Phase 3: 2-3 hours (age model)
- Testing: 1 hour
- **Total: ~10 hours**

