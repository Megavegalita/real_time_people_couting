# Critical Issues Analysis

## Problems Identified (from video inspection)

### Issue 1: Multiple Bounding Boxes for Same Person ❌
**Symptoms**:
- Yellow box (ID:0 MALE 26y) around upper body
- Red box (ID:1 (no face)) around lower body
- Same person detected twice

**Root Cause**:
- MobileNetSSD/YOLO creates overlapping boxes
- No NMS (Non-Maximum Suppression) before tracking
- IoU threshold too low (0.3)

**Technical Details**:
```
Detection 0: (671, 145, 356, 660) - Upper body
Detection 1: (609, 429, 432, 664) - Lower body
IoU = 0.35 (overlaps!)
```

**Fix**:
- Need NMS with IoU > 0.5 threshold
- Or better merging algorithm

### Issue 2: Wrong Gender Identification ❌
**Symptoms**:
- Person appears female but labeled "MALE"
- Same ID consistently wrong across frames

**Root Cause**:
- Gender based on hash of objectID
- NOT based on visual features
- Current code:
```python
import hashlib
id_hash = int(hashlib.md5(str(objectID).encode()).hexdigest()[:8], 16)
gender = "MALE" if (id_hash % 2 == 0) else "FEMALE"
```

**This is completely random and wrong!**

## Required Fixes

### Fix 1: Better NMS/B昂ing
```python
def apply_nms(boxes, confidences, iou_threshold=0.5):
    """Apply Non-Maximum Suppression."""
    indices = cv2.dnn.NMSBoxes(
        [list(b['bbox']) for b in boxes],
        [b['confidence'] for b in boxes],
        0.5,  # conf_threshold
        iou_threshold
    )
    
    return [boxes[i] for i in indices if len(indices) > 0]
```

### Fix 2: Remove Hash-Based Gender ❌
**Current (WRONG)**:
```python
import hashlib
id_hash = int(hashlib.md5(str(objectID).encode()).hexdigest()[:8], 16)
gender = "MALE" if (id_hash % 2 == 0) else "FEMALE"  # ❌ RANDOM!
```

**Should be**:
```python
# Option 1: Use actual gender classifier (not implemented yet)
gender = gender_classifier.predict(face_features)

# Option 2: Use visual heuristics
# Option 3: Leave as UNKNOWN until real model is added
```

## Summary

**The fundamental issue is**:
1. ✅ Box merging exists but IoU threshold (0.3) too low
2. ❌ Gender completely arbitrary (hash-based)
3. Need NMS with higher threshold
4. Need actual gender classification model

**Next Steps**:
1. Increase IoU threshold to 0.5 for better filtering
2. Add NMS before tracking
3. Replace hash-based gender with placeholder "UNKNOWN" until real model
4. Or use visual-based heuristics (better than hash)

