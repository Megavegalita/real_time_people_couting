# 🏗️ Parallel Processing Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Parallel People Counter                         │
│                       (Orchestrator)                              │
└──────────────┬──────────────────────────────────────┬──────────┘
               │                                        │
               │ Task Queue                             │ Result Queue
               │                                        │
               ▼                                        ▼
    ┌──────────────────────┐                  ┌────────────────────┐
    │                      │                  │                    │
    │  Worker Pool         │                  │  Result Handler    │
    │                      │                  │                    │
    │  [Worker 01]         │                  │  - Aggregate      │
    │  [Worker 02]  ──────┼───────────────► │  - Statistics     │
    │  [Worker 03]         │                  │  - Export         │
    │  [Worker 04]         │                  │                    │
    │                      │                  └────────────────────┘
    └──────────────────────┘
         │        │        │
         ▼        ▼        ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Camera  │ │ Camera  │ │  Video  │
    │   01    │ │   02    │ │   01    │
    └─────────┘ └─────────┘ └─────────┘
```

## Data Flow

```
1. Configuration
   └─► ConfigManager
       ├─► Validate config
       ├─► Create tasks
       └─► Add to task queue

2. Task Processing
   └─► Worker receives task from queue
       ├─► Initialize video stream
       ├─► Run people counting loop
       ├─► Send results to result queue
       └─► Cleanup and report

3. Result Collection
   └─► ResultHandler receives from queue
       ├─► Aggregate results
       ├─► Update statistics
       ├─► Print dashboard
       └─► Export to file (optional)

4. Monitoring
   └─► Logger writes to:
       ├─► Console
       ├─► Worker log files
       └─► Camera log files
```

## Component Interaction

### ParallelPeopleCounter (Main)
```
Responsibilities:
- Initialize worker pool
- Manage task queue
- Manage result queue
- Start/stop workers
- Aggregate results
- Print dashboard
- Export results
```

### PeopleCounterWorker (Worker)
```
Responsibilities:
- Receive task from queue
- Load video stream (camera/video)
- Run detection loop
- Track objects
- Count in/out
- Send results to queue
- Handle errors
```

### ConfigManager
```
Responsibilities:
- Load JSON config
- Validate structure
- Extract tasks
- Get worker count
- Get processing config
```

### ResultHandler
```
Responsibilities:
- Collect results from queue
- Store results by task_id
- Calculate statistics
- Generate summary
- Export to JSON/CSV
```

### ParallelLogger
```
Responsibilities:
- Create loggers per worker
- Create loggers per camera
- File logging
- Console logging
- Log rotation
```

## Thread Safety

### Shared Resources
```
- Model (cv2.dnn.Net): Read-only, shared across workers ✓ Safe
- Task Queue: Thread-safe Queue ✓ Safe
- Result Queue: Thread-safe Queue ✓ Safe
- Result Handler: Lock-protected ✓ Safe
```

### Worker Isolation
```
Each worker has:
- Isolated video stream connection
- Independent centroid tracker
- Separate trackable objects
- Own result buffer
```

## Performance Characteristics

### Model Loading
```
Time: ~1-2 seconds (one time)
Location: Main thread before processing
Shared: Yes, read-only across workers
Memory: ~50-100MB
```

### Worker Overhead
```
Per Worker:
- Memory: ~100-200MB
- CPU: ~10-20% (per camera at 25 FPS)
- Thread overhead: ~1-2MB
```

### Scalability
```
Number of Workers:
- 1 worker: 1 camera/video at a time
- 2 workers: 2 cameras/videos parallel
- 4 workers: 4 cameras/videos parallel (recommended)
- 8+ workers: Diminishing returns
```

## Error Handling

### Camera Connection Errors
```
1. Worker catches exception
2. Logs error with camera_id
3. Marks task as failed
4. Sends error result to queue
5. Continues with next task
6. Other cameras unaffected
```

### Processing Errors
```
1. Try-except in processing loop
2. Log error details
3. Mark task as error
4. Cleanup resources
5. Report to result handler
6. Continue with next task
```

## Resource Management

### Memory Management
```
Per Task:
- Frame buffer: ~5-10MB
- Tracker state: ~1-2MB
- Detection cache: ~10-20MB
Total per task: ~20-30MB
```

### CPU Usage
```
Per Camera (at 25 FPS):
- Detection (every 30 frames): ~10-15%
- Tracking (every frame): ~5-10%
- Total: ~15-25% per camera
```

### I/O Bandwidth
```
Camera: ~2-5 Mbps (RTSP)
Video file: Limited by disk speed
Network: Depends on camera resolution
```

## Configuration Example

```json
{
  "parallel_config": {
    "worker_count": 4,          // Number of parallel workers
    "skip_frames": 30,            // Frames to skip between detections
    "confidence": 0.4,            // Detection confidence threshold
    "result_output": "parallel/results/",
    "log_level": "INFO"
  },
  "cameras": [...],              // Camera configurations
  "videos": [...]                // Video configurations
}
```

## Usage Patterns

### Pattern 1: Single Video Processing
```
Tasks: 1
Workers: 1-2 (optimal)
Time: N/A (sequential processing)
Use case: Development, testing
```

### Pattern 2: Multiple Videos
```
Tasks: 2-4
Workers: 2-4
Time: ~N tasks / workers
Use case: Batch processing
```

### Pattern 3: Live Cameras
```
Tasks: Continuous
Workers: 4-8
Time: Ongoing
Use case: Production monitoring
```

### Pattern 4: Mixed (Cameras + Videos)
```
Tasks: M cameras + N videos
Workers: 4-8
Time: Dynamic
Use case: Hybrid processing
```

## State Machine

### Task States
```
pending → processing → completed
   │           │
   │           └─► error
   │
   └─► cancelled
```

### Worker States
```
idle → processing → idle
  │        │
  │        └─► error → idle
  │
  └─► stopped
```

## Monitoring

### Real-time Metrics
```
- Active workers
- Tasks in queue
- Completed tasks
- Failed tasks
- Total FPS
- CPU usage
- Memory usage
```

### Dashboard
```
Update frequency: 2 seconds
Display: Console
Refresh: Clear and redraw
Format: Text-based table
```

## Export Formats

### JSON Export
```json
{
  "export_time": "...",
  "summary": {...},
  "detailed_results": {...}
}
```

### CSV Export
```csv
timestamp,fps,total_in,total_out,current_count,status
2024-01-15 10:23:45,25.3,12,8,4,running
...
```

## Thread Communication

### Task Queue
```
Producer: ParallelPeopleCounter
Consumer: Workers
Type: Queue (thread-safe)
Timeout: None
Max size: Unlimited
```

### Result Queue
```
Producer: Workers
Consumer: ResultHandler
Type: Queue (thread-safe)
Timeout: 1 second
Max size: Unlimited
```

## Advantages of This Architecture

✅ **Scalability**: Easy to add more workers  
✅ **Isolation**: Errors don't affect other workers**  
✅ **Efficiency**: Shared model, efficient resource usage  
✅ **Flexibility**: Support multiple sources  
✅ **Maintainability**: Clean separation of concerns  
✅ **Performance**: True parallel processing  
✅ **Monitoring**: Built-in dashboard and logging  
✅ **Production-Ready**: Robust error handling  

---

**Design**: Worker Pool Pattern  
**Concurrency**: Thread-based  
**Communication**: Queue-based  
**State**: Isolated per worker  

