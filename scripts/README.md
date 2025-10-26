# 🧪 Test Scripts

## 📋 Danh Sách Scripts

### Test Scripts

1. **test_consistency.py**
   - Test consistency của parallel processing
   - Chạy cùng video 3 lần để verify

2. **test_multiple_videos.py**
   - Test parallel với nhiều videos

3. **test_multiple_workers_accuracy.py**
   - Test accuracy với multiple workers

4. **test_parallel_vs_original.py**
   - So sánh kết quả giữa original và parallel

5. **test_parallel_different_videos.py**
   - Test với các video files khác nhau

6. **test_accuracy_fixed.py**
   - Test duplicate prevention

7. **verify_fix.py**
   - Verify bug fixes

8. **run_final_comparison.py**
   - Final comparison test

### Cách Sử Dụng

```bash
# Test consistency
python scripts/test_consistency.py

# Test multiple videos
python scripts/test_multiple_videos.py

# Test with different videos
python scripts/test_parallel_different_videos.py

# Compare with original
python scripts/test_parallel_vs_original.py
```

## 📊 Notes

- Scripts tạo ra test results tạm thời
- Results được clean tự động sau khi test
- Không cần commit test results

---

**For documentation**: Xem `docs/testing/`
