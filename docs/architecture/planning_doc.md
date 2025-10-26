# 🚀 Parallel Processing Architecture Plan

## 📋 Tổng Quan

Xây dựng hệ thống xử lý song song cho phép đếm người từ nhiều camera hoặc video cùng lúc, sử dụng kiến trúc Worker Pattern với ThreadPoolExecutor.

## 🎯 Yêu Cầu Chính

1. **Multi-Camera Support**: Xử lý đồng thời nhiều camera IP/RTSP
2. **Multi-Video Support**: Xử lý nhiều video file song song
3. **Worker Pool**: Quản lý thread pool động
4. **Resource Management**: Quản lý tài nguyên hiệu quả
5. **Result Aggregation**: Tập hợp kết quả từ các worker
6. **Error Handling**: Xử lý lỗi cho từng camera/video độc lập
7. **Logging**: Ghi log riêng cho từng worker

## 🏗️ Kiến Trúc Chi Tiết

### 1. Cấu Trúc Thư Mục
```
parallel/
├── __init__.py
├── parallel_people_counter.py    # Main orchestrator
├── worker.py                      # Worker thread implementation
├── config_manager.py              # Configuration management
└── utils/
    ├── __init__.py
    ├── result_handler.py         # Result aggregation
    └── logger.py                  # Multi-worker logging
```

### 2. Thành Phần Core

#### A. `parallel_people_counter.py` (Orchestrator)
**Chức năng:**
- Quản lý Worker Pool
- Điều phối task cho các worker
- Tập hợp kết quả
- Quản lý lifecycle của workers

**Components:**
```python
class ParallelPeopleCounter:
    - __init__(worker_count=4)
    - add_camera(config_url, camera_id)
    - add_video(video_path, video_id)
    - start_processing()
    - stop_processing()
    - get_results()
    - get_statistics()
```

#### B. `worker.py` (Worker Thread)
**Chức năng:**
- Thực thi logic đếm người độc lập
- Xử lý một camera/video tại một thời điểm
- Trả về kết quả thời gian thực

**Components:**
```python
class PeopleCounterWorker(Thread):
    - __init__(worker_id, task_queue, result_queue)
    - run()  # Main processing loop
    - process_camera(config)  # Handle camera
    - process_video(video_path)  # Handle video
    - count_people()  # Core counting logic
```

#### C. `config_manager.py` (Configuration)
**Chức năng:**
- Quản lý cấu hình cho nhiều camera
- Validate input
- Tạo task từ config

**Components:**
```python
class ConfigManager:
    - load_multi_camera_config(json_file)
    - validate_camera_config()
    - create_task_from_config()
    - get_camera_configs()
```

#### D. `result_handler.py` (Results)
**Chức năng:**
- Tập hợp kết quả từ workers
- Lưu kết quả theo camera/video
- Cung cấp dashboard output

**Components:**
```python
class ResultHandler:
    - add_result(worker_id, result)
    - get_camera_results()
    - get_all_results()
    - export_to_csv()
    - get_dashboard_data()
```

#### E. `logger.py` (Logging)
**Chức năng:**
- Ghi log riêng cho từng worker
- Centralized logging
- Log rotation

**Components:**
```python
class ParallelLogger:
    - get_logger(worker_id)
    - info(camera_id, message)
    - error(camera_id, message)
    - debug(camera_id, message)
```

### 3. Data Structures

#### Task Format
```python
Task = {
    'task_id': str,
    'type': 'camera' | 'video',
    'source': str,  # RTSP URL or video path
    'config': dict,  # Camera config if needed
    'priority': int,
    'status': 'pending' | 'processing' | 'completed' | 'failed'
}
```

#### Result Format
```python
Result = {
    'worker_id': str,
    'task_id': str,
    'camera_id': str,
    'timestamp': datetime,
    'fps': float,
    'total_in': int,
    'total_out': int,
    'current_count': int,
    'frame_info': {
        'frame_count': int,
        'total_detections': int
    },
    'errors': list,
    'status': 'success' | 'error'
}
```

### 4. Workflow Chi Tiết

#### Khởi Tạo
1. Đọc config từ file (multi_camera_config.json)
2. Khởi tạo Worker Pool với N workers
3. Tạo task queue và result queue
4. Khởi động Result Handler

#### Xử Lý
1. **Task Distribution**:
   - Orchestrator phân task cho worker
   - Worker nhận task từ queue
   - Worker xử lý độc lập không block

2. **People Counting** (reuse logic từ people_counter.py):
   - Load model (shared hoặc per-worker)
   - Initialize centroid tracker
   - Loop frames:
     - Read frame
     - Detect persons
     - Track with centroid tracker
     - Count in/out
     - Log to result queue
   - Cleanup

3. **Result Collection**:
   - Worker gửi kết quả real-time qua result queue
   - Result handler aggregate
   - Update dashboard

#### Kết Thúc
1. Signal tất cả workers dừng
2. Đợi workers hoàn thành
3. Aggregate final results
4. Export logs
5. Cleanup resources

### 5. Thread Safety

#### Shared Resources
- **Model Loading**: Load once, share across workers
- **Result Queue**: Thread-safe queue
- **Task Queue**: Thread-safe queue
- **Logging**: Lock-based logging

#### Worker Isolation
- Mỗi worker có:
  - Tracking state riêng
  - Camera connection riêng
  - Result buffer riêng

### 6. Configuration Format

```json
{
  "parallel_config": {
    "worker_count": 4,
    "max_workers": 8,
    "result_output": "parallel/results/",
    "log_level": "INFO"
  },
  "cameras": [
    {
      "camera_id": "camera_01",
      "source": "rtsp://...",
      "alias": "Main Entrance",
      "location": "Building A",
      "threshold": 10,
      "enabled": true
    },
    {
      "camera_id": "camera_02",
      "source": "rtsp://...",
      "alias": "Side Exit",
      "location": "Building A",
      "threshold": 5,
      "enabled": true
    }
  ],
  "videos": [
    {
      "video_id": "video_01",
      "path": "utils/data/tests/test_1.mp4",
      "alias": "Test Video",
      "enabled": true
    }
  ]
}
```

### 7. Performance Optimization

#### Model Sharing
- Load MobileNetSSD model once globally
- Share across workers để tiết kiệm memory

#### Frame Skipping
- Configurable skip frames per camera
- High traffic cameras: skip more
- Low traffic cameras: skip less

#### Threading Strategy
- **Option 1**: Thread pool cố định
  - Fixed number of workers
  - Cameras chia sẻ workers
  
- **Option 2**: One worker per camera
  - Dedicated worker cho mỗi camera
  - Đảm bảo không bị block

#### Memory Management
- Limit frame buffer size
- Cleanup trackers khi camera disconnect
- Garbage collection cho completed tasks

### 8. Error Handling

#### Connection Errors
- Retry logic cho camera connection
- Auto-reconnect với exponential backoff
- Mark camera as failed sau N retries

#### Processing Errors
- Try-catch cho mỗi worker
- Log errors nhưng tiếp tục xử lý camera khác
- Report errors qua result queue

#### Resource Errors
- Memory monitoring
- CPU usage tracking
- Auto-throttle khi quá tải

### 9. Monitoring & Dashboard

#### Real-time Metrics
- FPS per camera
- Total count per camera
- Active worker count
- Queue depth
- Error rate

#### Dashboard Output
```
=========================================
Parallel People Counting System
=========================================
Workers: 4/4 active | Queue: 0 pending
-----------------------------------------
Camera 01 (Main Entrance): 
  Status: Running | FPS: 25.3
  In: 12 | Out: 8 | Current: 4

Camera 02 (Side Exit):
  Status: Running | FPS: 23.1
  In: 5 | Out: 7 | Current: -2

Camera 03 (Video Test):
  Status: Completed | FPS: 62.4
  In: 3 | Out: 3 | Current: 0

=========================================
Total: In: 20 | Out: 18 | Net: +2
=========================================
```

### 10. Logging Strategy

#### Per-Worker Logs
- `parallel/logs/worker_01.log`
- `parallel/logs/worker_02.log`
- ...

#### Per-Camera Logs
- `parallel/logs/camera_01.log`
- `parallel/logs/camera_02.log`
- ...

#### Central Log
- `parallel/logs/parallel_counter.log`

#### Format
```
[2024-01-15 10:23:45] [WORKER-01] [INFO] Starting camera_01
[2024-01-15 10:23:46] [CAMERA-01] [INFO] Frame processed: FPS=25.3
[2024-01-15 10:23:47] [CAMERA-01] [INFO] Person detected: ID=1, direction=IN
```

### 11. Integration Points

#### Sử dụng lại code hiện tại
- `tracker/centroidtracker.py` - Không sửa
- `tracker/trackableobject.py` - Không sửa
- `utils/thread.py` - Tận dụng ThreadingClass
- People counting logic - Extract thành function riêng

#### Tạo mới
- `parallel/worker.py` - Worker implementation
- `parallel/parallel_people_counter.py` - Main orchestrator
- `parallel/config_manager.py` - Config management
- `parallel/utils/result_handler.py` - Result aggregation
- `parallel/utils/logger.py` - Multi-worker logging

### 12. Usage Examples

#### Basic Usage
```python
from parallel.parallel_people_counter import ParallelPeopleCounter

counter = ParallelPeopleCounter(worker_count=4)

# Add cameras
counter.add_camera("rtsp://camera1")
counter.add_camera("rtsp://camera2")

# Add videos
counter.add_video("video1.mp4")

# Start processing
counter.start_processing()

# Get results
results = counter.get_results()
stats = counter.get_statistics()

# Stop
counter.stop_processing()
```

#### CLI Usage
```bash
python parallel/parallel_people_counter.py \
    --config parallel_config.json \
    --workers 4 \
    --output parallel/results/
```

### 13. Testing Strategy

#### Unit Tests
- Test worker initialization
- Test result handling
- Test config loading
- Test logging

#### Integration Tests
- Test 2 cameras parallel
- Test camera + video
- Test error recovery
- Test resource cleanup

#### Performance Tests
- Measure FPS degradation với N workers
- Memory usage profiling
- CPU utilization tracking

### 14. Migration Path

#### Phase 1: Core Infrastructure
- Tạo cấu trúc thư mục parallel/
- Implement ConfigManager
- Implement basic Worker
- Test với 1 camera

#### Phase 2: Parallel Processing
- Implement ThreadPool
- Implement ResultHandler
- Test với 2 cameras
- Test với 1 camera + 1 video

#### Phase 3: Error Handling & Monitoring
- Implement error recovery
- Add monitoring dashboard
- Add logging
- Test với N cameras

#### Phase 4: Optimization & Documentation
- Performance tuning
- Write documentation
- Create examples
- Create migration guide

## ✅ Các File Cần Tạo

1. `parallel/__init__.py` - Package init
2. `parallel/parallel_people_counter.py` - Main orchestrator
3. `parallel/worker.py` - Worker implementation
4. `parallel/config_manager.py` - Config management
5. `parallel/utils/__init__.py` - Utils package init
6. `parallel/utils/result_handler.py` - Result handling
7. `parallel/utils/logger.py` - Logging utilities
8. `parallel/config_example.json` - Config example
9. `parallel/README.md` - Documentation
10. `parallel/test_parallel.py` - Tests

## 🎯 Success Criteria

1. ✅ Xử lý được ít nhất 4 cameras/videos song song
2. ✅ Mỗi worker xử lý độc lập, không block
3. ✅ Kết quả được tập hợp chính xác
4. ✅ Error recovery hoạt động tốt
5. ✅ Logging đầy đủ cho debugging
6. ✅ Performance: FPS > 15 per camera/video
7. ✅ Memory usage hợp lý
8. ✅ Dễ mở rộng thêm workers

## 📝 Implementation Order

1. **Cấu trúc cơ bản** (30 min)
   - Tạo thư mục parallel/
   - Tạo các file __init__.py

2. **Config Management** (1 hour)
   - Implement ConfigManager
   - Tạo config example

3. **Worker Implementation** (2 hours)
   - Implement Worker class
   - Extract counting logic từ people_counter.py

4. **Orchestrator** (2 hours)
   - Implement ParallelPeopleCounter
   - Integrate ThreadPoolExecutor

5. **Result Handling** (1 hour)
   - Implement ResultHandler
   - Implement logging

6. **Testing & Debugging** (1 hour)
   - Test với 1-2 cameras
   - Fix bugs

7. **Documentation** (30 min)
   - Write README
   - Add examples

**Total Estimated Time: ~8 hours**

---

Chuẩn bị thực hiện theo plan này!

