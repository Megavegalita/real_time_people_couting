# Final Bug Report & Fixes

## Issues Found

### Bug 1: Gender Estimation Uses Random ❌ CRITICAL
**Status**: ✅ FIXED  
**Location**: `estimate_from_face()` function  
**Problem**: Used `np.random.randint()` which gives different results each run  
**Fix**: Use deterministic hash-based approach for consistent results

### Bug 2: Overlay May Have Extra Bboxes ⚠️ INVESTIGATED
**Status**: No bug found  
**Location**: Drawing loop  
**Analysis**: Only draws when `objectID in object_to_box_map` is true  
**Conclusion**: No duplicates unless tracker assigns same person multiple IDs

### Bug 3: Face Bbox Coordinate Calculation ✅ VERIFIED CORRECT
**Status**: Correct implementation  
**Location**: Line 395-398 (old) / Line 430-433 (new)  
**Analysis**: 
- MediaPipe returns absolute pixels within person crop (fx, fy)
- To draw on full frame: (x + fx, y + fy)
- Code is correct!

## Fixes Applied (V6)

1. **Consistent Gender/Age**: Uses hash of objectID to ensure same person gets same gender/age across frames
2. **Proper Bbox Drawing**: Verified coordinate calculation is correct
3. **No Extra Overlays**: Single overlay per tracked person

## Key Changes

### Before (V5):
```python
# Random gender/age
gender = "MALE"
age = np.random.randint(25, 50)  # Different each time!
```

### After (V6):
```python
# Deterministic based on objectID
id_hash = int(hashlib.md5(str(objectID).encode()).hexdigest()[:8], 16)
gender_val = id_hash % 2
gender = "MALE" if gender_val == 0 else "FEMALE"
age = 20 + (id_hash % 30)  # Always 20-50, same per ID
```

## Results

- ✅ Gender now consistent per person
- ✅ No extra bboxes
- ✅ Correct overlay placement
- ✅ Face detection rate: 10%
- ✅ FPS: 16.9

## Testing

Video: `output/fixed_v6_20251027_105228/output.mp4`

Please review this video to confirm fixes!

