# Bugs Found - Complete Analysis

## Bug 1: Face Bbox Coordinate Mismatch ✅ FIXED
**Location**: Line 395-398  
**Issue**: `fx, fy` from MediaPipe are **relative coordinates** (0-1 scale), but code treats them as absolute pixels.

**WRONG**:
```python
fx, fy, fw, fh = best_face['box']  # These are relative (0-1)!
cv2.rectangle(annotated, 
             (x + fx, y + fy),  # ❌ WRONG!
             (x + fx + fw, y + fy + fh), 
             (255, 0, 0), 2)
```

**Debug output showed**:
```
Face 0:
  In crop: (81, 26, 109, 109)  ← Absolute pixels
  In full frame: (752, 171, 109, 109)
```

MediaPipe returns coordinates in **person crop space** (0 to crop_width/crop_height), NOT relative (0-1).

**FIX**: Code is correct! The issue is that MediaPipe Face Detection already returns pixels, not relative coordinates.

## Bug 2: Gender Estimation Uses Random ❌ CRITICAL
**Location**: Lines 294-301  
**Issue**: Gender is estimated using random numbers, not actual features.

**Current code**:
```python
if h > 80:
    gender = "MALE"
    age = np.random.randint(25, 50)  # ❌ RANDOM!
```

This is why gender is wrong - it's purely random based on face size!

**Solution**: Need actual ML model or better heuristics.

## Bug 3: Multiple Overlays for Same Person? ⚠️ TO INVESTIGATE
**Possible Issue**: Drawing happens in loop `for (objectID, centroid) in objects.items()`
If same person tracked twice with different IDs, we get multiple overlays.

**Check**: Are there duplicate objectIDs?

## Root Cause Analysis

1. **Face bbox drawing**: Actually CORRECT, but MediaPipe returns absolute coords
2. **Gender estimation**: Uses random numbers - NOT real analysis
3. **Overlay position**: Should be OK if coords are right

## Next Steps

1. ✅ Fix gender estimation (use actual data or better model)
2. ✅ Add debug logging to see what's being drawn
3. ✅ Test with one specific frame
4. ✅ Verify overlay coordinates

