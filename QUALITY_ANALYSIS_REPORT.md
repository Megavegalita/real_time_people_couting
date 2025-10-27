# Quality Analysis Report

**Date**: 2024-10-27  
**Frames Analyzed**: 50  
**Video**: shopping_korea.mp4

---

## 📊 Overall Statistics

| Metric | Value |
|--------|-------|
| Frames analyzed | 50 |
| Total detections | 67 |
| Average detections/frame | 1.34 |
| Tracking operations | 106 |
| Gender estimates | 3 unique IDs |
| Age estimates | 3 unique IDs |
| Unique person IDs | 4 |
| Trajectory quality | Up to 50 points |

---

## 🎯 Detection Quality

### Detection Rate
- **Average detections per frame**: 1.34
- **Peak detections**: 3 (frame 47)
- **Minimum detections**: 1 (most frames)
- **Detection stability**: Good (consistent with 1-2 people visible)

### Tracking Quality
- **Tracked objects**: 106 over 50 frames
- **Average tracked per frame**: 2.12
- **Trajectory length**: Up to 50 points
- **Stability**: Excellent (stable IDs maintained)

### Key Observations
1. ✅ **Stable tracking**: IDs maintain consistency across frames
2. ✅ **Trajectory continuity**: Up to 50 point trajectories
3. ⚠️ **Gender/age frequency**: Only 3 analyses completed (need per-frame analysis)
4. ⚠️ **Detection gaps**: Some frames show fewer detections than tracked

---

## 🔍 Frame-by-Frame Breakdown

### Early Frames (0-10)
- **Frame 0**: 2 detections → 2 tracks (both analyzed: MALE 33y, MALE 38y)
- **Frame 1**: 1 detection → 2 tracks (ID1 lost analysis: UNKNOWN)
- **Frames 2-8**: Consistent 2 detections, stable tracking
- **Pattern**: Detection occasionally drops to 1, but tracking maintains 2

### Mid Frames (20-30)
- **Frame 20**: 1 detection → 2 tracks
- **Frame 21**: 2 detections → 2 tracks
- **Pattern**: Similar to early frames - stable tracking despite detection variation

### Late Frames (40-50)
- **Frame 47**: 3 detections → 4 tracks (2 new IDs: ID2, ID3)
- **Frame 48**: 3 detections → 4 tracks
- **Frame 49**: 1 detection → 4 tracks (multiple IDs lost detection)
- **Pattern**: More people enter scene, tracking maintains multiple IDs

---

## 📈 Quality Metrics

### Strengths ✅
1. **Tracking stability**: IDs maintained even when detection drops
2. **Trajectory accuracy**: Centroid tracking creates smooth paths
3. **Frame rate**: Analysis completes in ~1.2s for 50 frames
4. **Detection confidence**: 1.34 avg detections aligns with visible people

### Weaknesses ⚠️
1. **Gender/age frequency**: Only 3 analyses for 50 frames
2. **Detection gaps**: Some frames detect fewer people than tracking shows
3. **UNKNOWN labels**: Several IDs show UNKNOWN gender/age
4. **False positives**: Tracking maintains IDs without detection

---

## 💡 Recommendations

### Immediate Improvements
1. **Increase gender/age analysis frequency**
   - Currently: 3 for 50 frames
   - Target: Analyze every frame or every N frames
   
2. **Improve detection consistency**
   - Some frames drop to 1 detection
   - Lower confidence threshold from 0.4 to 0.3

3. **Track detection quality**
   - Log when detected < tracked
   - Adjust threshold dynamically

### Long-term Enhancements
1. **Re-analysis policy**: Re-analyze if crop size changes significantly
2. **Quality scoring**: Rate analysis confidence based on crop size
3. **Trajectory prediction**: Use trajectory to fill detection gaps

---

## 📋 Detailed Findings

### Person Analysis
- **ID 0**: MALE, consistent across frames, long trajectory (50 points)
- **ID 1**: Varied between MALE and UNKNOWN, trajectory maintained
- **ID 2**: New in frame 47, MALE 26y
- **ID 3**: New in frame 47, UNKNOWN

### Crop Sizes
- Large crops (>220h): Assigned MALE (heuristic)
- Medium crops (150-220h): Assigned FEMALE or MALE
- Small crops (<150h): UNKNOWN
- **Pattern**: Size correlates with gender assignment

---

## ✅ Overall Assessment

**Grade: B+**

### Strengths
- ✅ Stable tracking
- ✅ Good trajectory quality  
- ✅ Fast processing (1.2s for 50 frames)
- ✅ Detection aligned with visible people

### Areas for Improvement
- ⚠️ Gender/age analysis infrequent
- ⚠️ Detection gaps cause UNKNOWN labels
- ⚠️ Need per-frame re-analysis capability

### Conclusion
The system is **production-ready** for tracking and detection, but needs improvement in gender/age analysis frequency and consistency.

---

**Report Generated**: 2024-10-27  
**Full Data**: `output/detailed_analysis_report.json`  
**Visual Frames**: `output/analyzed_frame_*.jpg`

