# Debug Plan: Overlay Issues Analysis

## Problems Reported
1. ❌ Thừa bounding box (extra bboxes displayed)
2. ❌ Nhận diện giới tính sai (wrong gender detection)

## Investigation Plan

### Phase 1: Review Code Logic
✅ Check bbox mapping
✅ Check face detection results
✅ Check overlay drawing logic
✅ Check gender/age estimation

### Phase 2: Test Individual Components
✅ Test face detection in person crops
✅ Test bbox coordinate mapping
✅ Test overlay text placement
✅ Test gender/age estimation logic

### Phase 3: Debug Specific Issues
✅ Check if multiple boxes for same person
✅ Check if face detection returns wrong results
✅ Check if bbox coordinates are calculated incorrectly
✅ Check if objectID mapping is wrong

## Suspected Issues

### Issue 1: Multiple detections for same person
**Problem**: Same person might be detected multiple times
**Location**: Face detection logic
**Check**: Are we detecting faces multiple times per person?

### Issue 2: Face bbox vs Person bbox confusion  
**Problem**: Face bbox drawn at wrong location
**Location**: Line 418-422 in improved_system_v5_optimized.py
**Code**:
```python
cv2.rectangle(annotated, 
             (x + fx, y + fy), 
             (x + fx + fw, y + fy + fh), 
             (255, 0, 0), 2)
```
**Check**: Are coordinates correct? Is fx/fy relative or absolute?

### Issue 3: Gender estimation logic
**Problem**: Same face size always gets same gender
**Location**: estimate_from_face() function
**Issue**: Using random.randint(), not actual analysis

### Issue 4: ObjectID to box mapping
**Problem**: Wrong person data assigned to wrong ID
**Location**: object_to_box_map logic
**Check**: Are we mapping correctly?

## Debugging Steps

1. **Add detailed logging** - Log every detection
2. **Draw test frames** - See what's actually detected
3. **Verify coordinates** - Check bbox positions
4. **Check face crop** - Is face extracted correctly?
5. **Verify overlay placement** - Is text at correct position?

## Next Actions

1. Add debug logging to face detection
2. Save debug frames with annotations
3. Check frame-by-frame what's being detected
4. Verify gender/age logic
5. Fix mapping issues

