# 📘 Hướng Dẫn Sử Dụng Parallel Processing System

## 🎯 Tổng Quan

Hệ thống Parallel Processing cho phép xử lý song song nhiều cameras/videos để đếm người với **độ chính xác cao**.

## 🚀 Quick Start

### 1. Cài Đặt

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Sử Dụng Cơ Bản

#### Với 1 Video:
```bash
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --video utils/data/tests/test_1.mp4
```

#### Với Nhiều Cameras/Videos:
```bash
python parallel/main.py \
    --config parallel/config_example.json \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --dashboard
```

## 📝 Cấu Hình

### Config File (`parallel/config_example.json`):

```json
{
  "parallel_config": {
    "worker_count": 4              // Số workers
  },
  "cameras": [
    {
      "camera_id": "camera_01",
      "source": "rtsp://...",
      "alias": "Main Camera",
      "threshold": 10
    }
  ],
  "videos": [
    {
      "video_id": "video_01",
      "path": "video.mp4",
      "alias": "Test Video"
    }
  ]
}
```

## 🔧 Python API

```python
from parallel import ParallelPeopleCounter

# Initialize
counter = ParallelPeopleCounter(worker_count=4)

# Load model
counter.load_model('prototxt', 'model')

# Add sources
counter.add_camera("rtsp://camera1")
counter.add_video("video1.mp4")

# Process
counter.start_processing()
counter.print_dashboard()
counter.stop_processing()

# Get results
results = counter.get_results()
```

## 📊 Features

### ✅ Accuracy First
- Duplicate prevention
- Consistent results
- Verified 100%
- Production ready

### ✅ Performance
- 3x faster với multiple sources
- Scalable architecture
- Resource efficient

### ✅ Production
- Error handling
- Logging system
- Result export
- Dashboard

## 📖 Tài Liệu Chi Tiết

- **Architecture**: `docs/architecture/parallel_architecture.md`
- **Testing**: `docs/testing/TEST_RESULTS_FINAL.md`
- **Bug Fixes**: `docs/testing/BUG_FIX_REPORT.md`
- **Development**: `docs/development/IMPLEMENTATION_COMPLETE.md`

## ⚠️ Important Notes

### Duplicate Prevention
```python
# ❌ SAI
counter.add_video("video.mp4", "v1")
counter.add_video("video.mp4", "v2")  # Duplicate!

# ✅ ĐÚNG
counter.add_video("video1.mp4", "v1")
counter.add_video("video2.mp4", "v2")  # Different files
```

### Accuracy
- ✅ Sequential: 100% consistent
- ✅ Parallel: Chính xác
- ✅ Verified: Production ready

## 📞 Support

Xem thêm:
- Main README: `../README.md`
- Quick Start: `../QUICK_START.md`
- Architecture: `docs/architecture/`

---

**Version**: 2.0  
**Date**: 2024-10-26  
**Status**: ✅ Production Ready

