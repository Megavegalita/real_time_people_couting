# Parallel People Counting System

## 📖 Tổng Quan

Hệ thống xử lý song song cho phép đếm người từ nhiều camera hoặc video cùng lúc, sử dụng kiến trúc Worker Pattern với ThreadPoolExecutor.

## ✨ Tính Năng

- ✅ **Multi-Camera Support**: Xử lý đồng thời nhiều camera IP/RTSP
- ✅ **Multi-Video Support**: Xử lý nhiều video file song song  
- ✅ **Worker Pool**: Quản lý thread pool động
- ✅ **Resource Management**: Quản lý tài nguyên hiệu quả
- ✅ **Result Aggregation**: Tập hợp kết quả từ các worker
- ✅ **Error Handling**: Xử lý lỗi cho từng camera/video độc lập
- ✅ **Real-time Monitoring**: Dashboard trực quan
- ✅ **Logging**: Ghi log riêng cho từng worker

## 🚀 Quick Start

### 1. Cài Đặt Dependencies

```bash
# Đảm bảo đã install dependencies
pip install opencv-python imutils dlib schedule scipy numpy
```

### 2. Sử Dụng từ Configuration File

```bash
# Tạo config file từ example
cp parallel/config_example.json parallel/my_config.json

# Chỉnh sửa config theo nhu cầu
nano parallel/my_config.json

# Chạy với config
python parallel/main.py \
    --config parallel/my_config.json \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --dashboard
```

### 3. Sử Dụng Command Line

```bash
# Chạy với webcam
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --camera 0

# Chạy với nhiều camera
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --camera 0 \
    --camera "rtsp://..." \
    --workers 4 \
    --dashboard

# Chạy với video
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --video utils/data/tests/test_1.mp4 \
    --export json
```

### 4. Sử Dụng Python API

```python
from parallel import ParallelPeopleCounter

# Khởi tạo
counter = ParallelPeopleCounter(worker_count=4)

# Load model
counter.load_model(
    prototxt='detector/MobileNetSSD_deploy.prototxt',
    model='detector/MobileNetSSD_deploy.caffemodel'
)

# Thêm camera
counter.add_camera(
    source="0",  # Webcam
    camera_id="webcam_01",
    alias="Main Webcam",
    threshold=10
)

# Thêm nhiều camera
counter.add_camera(
    source="rtsp://...",
    camera_id="camera_01",
    alias="IP Camera",
    threshold=15
)

# Thêm video
counter.add_video(
    video_path="utils/data/tests/test_1.mp4",
    video_id="test_video",
    alias="Test Video",
    threshold=5
)

# Bắt đầu xử lý
counter.start_processing()

# In dashboard
counter.print_dashboard()

# Lấy kết quả
results = counter.get_results()
summary = counter.get_summary()

# Dừng xử lý
counter.stop_processing()

# Export results
counter.export_results(format='json')
```

## 📋 Configuration Format

### Configuration File (config.json)

```json
{
  "parallel_config": {
    "worker_count": 4,
    "max_workers": 8,
    "result_output": "parallel/results/",
    "log_level": "INFO",
    "skip_frames": 30,
    "confidence": 0.4
  },
  "cameras": [
    {
      "camera_id": "camera_01",
      "source": "0",
      "alias": "Webcam Test",
      "location": "Building A - Main Entrance",
      "threshold": 10,
      "enabled": true,
      "type": "webcam"
    },
    {
      "camera_id": "camera_02",
      "source": "rtsp://username:password@192.168.1.100:554/...",
      "alias": "IP Camera - Main Entrance",
      "location": "Building A - Main Entrance",
      "threshold": 15,
      "enabled": true,
      "type": "rtsp"
    }
  ],
  "videos": [
    {
      "video_id": "video_01",
      "path": "utils/data/tests/test_1.mp4",
      "alias": "Test Video 1",
      "threshold": 5,
      "enabled": true
    }
  ]
}
```

## 🏗️ Kiến Trúc

### Components

1. **`ParallelPeopleCounter`** - Orchestrator chính
2. **`PeopleCounterWorker`** - Worker thread xử lý task
3. **`ConfigManager`** - Quản lý configuration
4. **`ResultHandler`** - Tập hợp và xử lý kết quả
5. **`ParallelLogger`** - Multi-worker logging

### Workflow

```
Configuration → Task Queue → Worker Pool → Result Queue → Result Handler
                     ↓                          ↓
                Workers ← Task Distribution → Workers
                     ↓                          ↓
              People Counter ← Videos/Cameras → Results
```

## 📊 Output

### Dashboard

```
============================================================
Parallel People Counting System - Dashboard
============================================================

Workers: 4 active | Tasks: 3
------------------------------------------------------------
▶ camera_01:
    Status: running | FPS: 25.3
    In: 12 | Out: 8 | Current: 4

▶ camera_02:
    Status: running | FPS: 23.1
    In: 5 | Out: 7 | Current: -2

✓ video_01:
    Status: completed | FPS: 62.4
    In: 3 | Out: 3 | Current: 0

------------------------------------------------------------
Total: In: 20 | Out: 18 | Net: +2
============================================================
```

### JSON Export

```json
{
  "export_time": "2024-01-15T10:30:00",
  "summary": {
    "total_tasks": 3,
    "tasks": {
      "camera_01": {
        "latest_fps": 25.3,
        "total_in": 12,
        "total_out": 8,
        "current_count": 4,
        "status": "completed"
      }
    },
    "overall": {
      "total_in": 20,
      "total_out": 18,
      "net_count": 2
    }
  }
}
```

## 🔧 Parameters

### Global Configuration

- `worker_count`: Số lượng worker threads (default: 4)
- `skip_frames`: Số frame bỏ qua giữa các lần detection (default: 30)
- `confidence`: Confidence threshold (default: 0.4)

### Per-Camera/Video

- `threshold`: Ngưỡng số người để alert (default: 10)
- `priority`: Độ ưu tiên task (1-5)
- `enabled`: Bật/tắt camera/video

## 📁 Cấu Trúc Thư Mục

```
parallel/
├── __init__.py
├── main.py                        # CLI entry point
├── parallel_people_counter.py     # Main orchestrator
├── worker.py                      # Worker implementation
├── config_manager.py              # Configuration management
├── config_example.json            # Example configuration
├── README.md                      # This file
└── utils/
    ├── __init__.py
    ├── result_handler.py         # Result handling
    └── logger.py                  # Multi-worker logging
```

## 🧪 Testing

### Test với 1 Camera

```bash
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --camera 0
```

### Test với Video

```bash
python parallel/main.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --video utils/data/tests/test_1.mp4
```

### Test với Config

```bash
# Create test config
cp parallel/config_example.json parallel/test_config.json

# Edit test_config.json

# Run
python parallel/main.py \
    --config parallel/test_config.json \
    --dashboard \
    --export json
```

## 🛠️ Development

### Thêm Camera

```python
counter.add_camera(
    source="rtsp://...",
    camera_id="camera_03",
    alias="New Camera",
    threshold=10,
    priority=1
)
```

### Custom Configuration

```python
config = {
    'skip_frames': 20,      # Faster detection
    'confidence': 0.5,       # Higher accuracy
    'Thread': True           # Enable threading
}
counter.start_processing(config=config)
```

## 📝 Notes

- **Model Sharing**: MobileNetSSD model được load 1 lần và chia sẻ giữa các worker
- **Thread Safety**: Tất cả queues đều thread-safe
- **Error Recovery**: Lỗi 1 camera không ảnh hưởng camera khác
- **Resource Management**: Tự động cleanup resources

## 🔍 Troubleshooting

### Vấn Đề: Camera không connect

```
Error: OpenCV: Couldn't read video stream
```

**Giải pháp:**
- Kiểm tra RTSP URL format
- Verify camera credentials
- Test camera connection trước

### Vấn Đề: Low FPS

**Giải pháp:**
- Tăng `skip_frames` (30 → 45)
- Giảm `worker_count` (4 → 2)
- Enable threading: `"Thread": true`

### Vấn Đề: Memory cao

**Giải pháp:**
- Giảm số workers
- Giảm số camera đồng thời
- Tăng `skip_frames`

## 📚 Examples

Xem thêm examples trong thư mục `parallel/examples/`

## 🤝 Contributing

Contributions are welcome! Please follow the existing code style and add tests.

## 📄 License

Same license as main project.

