# 🧪 Hướng Dẫn Chạy Verification

**Date**: 2024-10-26  
**Purpose**: Verify optimization không làm thay đổi logic và performance

---

## 🚀 Cách Chạy

### Option 1: Comprehensive Verification (Recommended)

Chạy kiểm tra toàn bộ tự động:

```bash
python comprehensive_verification.py
```

Script này sẽ:
- ✅ Chạy single processing (people_counter.py)
- ✅ Chạy parallel processing (parallel/main.py)
- ✅ Đo performance (FPS, memory, CPU)
- ✅ So sánh kết quả accuracy
- ✅ Tạo report chi tiết

### Option 2: Manual Individual Tests

#### Test 1: Single Processing

```bash
python people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --input utils/data/tests/test_1.mp4 \
    --confidence 0.4 \
    --skip-frames 30
```

**Nhận kết quả gì**:
- Total In: X people
- Total Out: Y people  
- Current Count: Z people
- FPS: ~XX

**Lưu lại kết quả**: Ghi nhận các số đếm này

#### Test 2: Parallel Processing

```bash
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --video utils/data/tests/test_1.mp4 \
    --workers 2 \
    --log-level INFO
```

**Nhận kết quả gì**:
- Total In: X people (phải GIỐNG single processing)
- Total Out: Y people (phải GIỐNG single processing)
- Current Count: Z people (phải GIỐNG single processing)

**So sánh**:
- In count phải IDENTICAL
- Out count phải IDENTICAL
- Current count phải IDENTICAL

---

## 📊 Expected Results

### Accuracy Check

| Metric | Single | Parallel | Match? |
|--------|--------|----------|--------|
| Total In | X | X | ✅ Must be equal |
| Total Out | Y | Y | ✅ Must be equal |
| Current Count | Z | Z | ✅ Must be equal |

### Performance Check

| Metric | Single | Parallel | Acceptable? |
|--------|--------|----------|------------|
| FPS | X | >= 0.95*X | ✅ Yes if >= 95% |
| Memory | Y | <= 1.10*Y | ✅ Yes if <= 110% |
| Duration | T1 | T2 | ✅ Any |

---

## 🎯 Success Criteria

### Accuracy: **100% Required**

```
✅ Total In: Must be IDENTICAL
✅ Total Out: Must be IDENTICAL  
✅ Current Count: Must be IDENTICAL
❌ NO TOLERANCE allowed for accuracy
```

### Performance: **>= 95% Required**

```
✅ FPS: >= 95% of single processing
✅ Memory: <= 110% of single processing
✅ CPU: <= 105% of single processing
⚠️  Small variations acceptable due to system load
```

---

## 📝 Interpreting Results

### ✅ Good Results

```
Accuracy: 100% match ✓
Performance: 98% FPS ✓
Memory: 102% usage ✓

VERDICT: ✅ OPTIMIZATION SAFE
```

### ⚠️ Warning Results

```
Accuracy: 100% match ✓
Performance: 92% FPS ⚠️
Memory: 115% usage ⚠️

VERDICT: ⚠️  NEED INVESTIGATION
```

### ❌ Failed Results

```
Accuracy: 95% match ❌
Performance: 80% FPS ❌

VERDICT: ❌ REVERT CHANGES
```

---

## 🔍 What to Look For

### Accuracy Verification

1. **Counting Numbers Must Match**:
   - Both should count same number of people in/out
   - Current count should be identical

2. **Tracking IDs Must Be Consistent**:
   - Objects should be tracked with same IDs
   - No double counting or missing counts

3. **Direction Detection**:
   - Entry/exit directions should match
   - No reversed directions

### Performance Verification

1. **FPS Should Be Similar**:
   - Parallel might be slightly different due to overhead
   - But should be >= 95% of single

2. **Memory Should Be Reasonable**:
   - Parallel uses more memory (multiple workers)
   - But should be <= 110% of single

3. **CPU Usage**:
   - Parallel should use more CPU (multi-threading)
   - But efficiency should be maintained

---

## 📁 Output Files

After running verification, check:

```
verification_results/
├── single_processing_result.json
├── parallel_processing_result.json
└── summary.json
```

### Single Processing Results

```json
{
  "label": "single_processing",
  "success": true,
  "duration": 45.2,
  "total_in": 28,
  "total_out": 15,
  "current_count": 13,
  "fps": 15.3,
  "memory_avg_mb": 245.5,
  "memory_peak_mb": 280.2
}
```

### Parallel Processing Results

```json
{
  "label": "parallel_processing",
  "success": true,
  "duration": 42.8,
  "total_in": 28,
  "total_out": 15,
  "current_count": 13,
  "fps": 16.1,
  "memory_avg_mb": 268.3,
  "memory_peak_mb": 310.5
}
```

### Summary

```json
{
  "timestamp": "2024-10-26T...",
  "accuracy_match": true,
  "performance_ratio": 0.98
}
```

---

## ⚠️ Troubleshooting

### Issue: Test Video Not Found

**Error**: `Test video not found: utils/data/tests/test_1.mp4`

**Solution**:
```bash
# Check if video exists
ls utils/data/tests/

# Use different video if needed
python comprehensive_verification.py --video path/to/your/video.mp4
```

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'tracker'`

**Solution**:
```bash
# Make sure you're in project root
pwd  # Should show project directory

# Run from correct directory
cd /Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting
python comprehensive_verification.py
```

### Issue: Model Files Not Found

**Error**: `Cannot open detector/MobileNetSSD_deploy.prototxt`

**Solution**:
```bash
# Verify model files exist
ls detector/
# Should show:
# - MobileNetSSD_deploy.prototxt
# - MobileNetSSD_deploy.caffemodel
```

---

## 🎉 Expected Final Output

```
======================================================================
  COMPREHENSIVE VERIFICATION
  Testing Single vs Parallel Processing
======================================================================

======================================================================
  🔵 SINGLE PROCESSING TEST
======================================================================

📊 Running people_counter.py (original)...
   Command: python people_counter.py ...
   ✅ Completed in 45.2s

======================================================================
  🟢 PARALLEL PROCESSING TEST
======================================================================

📊 Running parallel/main.py...
   Command: python parallel/main.py ...
   ✅ Completed in 42.8s

======================================================================
  📊 COMPARISON RESULTS
======================================================================

🔵 Single Processing:
   Status: ✅ Success
   Duration: 45.2s
   Total In: 28
   Total Out: 15
   Current Count: 13
   FPS: 15.3
   Memory Avg: 245.5 MB
   Memory Peak: 280.2 MB

🟢 Parallel Processing:
   Status: ✅ Success
   Duration: 42.8s
   Total In: 28
   Total Out: 15
   Current Count: 13
   FPS: 16.1
   Memory Avg: 268.3 MB
   Memory Peak: 310.5 MB

📈 Performance Comparison:
   Duration Difference: -2.4s (faster!)
   Speedup: 1.06x
   Memory Difference: +9.3%

✅ Accuracy Check:
   ✅ Perfect match: In=0, Out=0

======================================================================
  📋 VERIFICATION SUMMARY
======================================================================

✅ Tests Completed
   Single Processing: ✅ Pass
   Parallel Processing: ✅ Pass

   Results saved to: verification_results/

🎉 VERIFICATION PASSED!
```

---

**Next Steps After Verification**:
1. If results match 100%: ✅ Proceed with confidence
2. If minor differences: ⚠️  Investigate specific areas
3. If major differences: ❌ Revert changes and debug

