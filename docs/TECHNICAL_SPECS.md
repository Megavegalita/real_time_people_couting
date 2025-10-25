# Real-Time People Counting System - Technical Specifications

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Real-Time People Counting System              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Video     │    │   Frame     │    │ Detection   │         │
│  │   Input     │───▶│ Processing  │───▶│   Engine    │         │
│  │ (Webcam/IP) │    │             │    │ MobileNetSSD│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                │                │              │
│                                ▼                ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Display   │◀───│   Counting  │◀───│  Tracking   │         │
│  │   Output    │    │   Logic     │    │  System     │         │
│  │             │    │             │    │ CentroidTracker│        │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                │                │              │
│                                ▼                ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Email     │    │   Data      │    │  Utility    │         │
│  │   Alerts    │◀───│  Logging    │◀───│  Modules    │         │
│  │             │    │             │    │ (Threading)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### 1. Input Processing
- **Video Source**: Webcam (0), IP Camera (URL), or Video File
- **Frame Capture**: Continuous frame reading with optional threading
- **Preprocessing**: Resize to 500px width, BGR to RGB conversion

### 2. Detection Pipeline
- **Skip Frame Logic**: Expensive detection every 30 frames
- **MobileNetSSD**: Person detection with confidence filtering
- **Bounding Box Extraction**: Coordinates for detected persons

### 3. Tracking System
- **Centroid Calculation**: Center point of bounding boxes
- **Object Association**: Distance-based matching algorithm
- **ID Management**: Unique identifier assignment and maintenance

### 4. Counting Logic
- **Direction Analysis**: Movement direction based on centroid history
- **Line Crossing Detection**: Entry/exit determination
- **State Management**: Trackable object counting status

### 5. Output Generation
- **Visual Display**: Real-time counting information overlay
- **Alert System**: Email notifications for threshold breaches
- **Data Logging**: CSV export for analysis

## Algorithm Details

### Centroid Tracking Algorithm

```python
def update(self, rects):
    # 1. Calculate input centroids from bounding boxes
    inputCentroids = np.zeros((len(rects), 2), dtype="int")
    for (i, (startX, startY, endX, endY)) in enumerate(rects):
        cX = int((startX + endX) / 2.0)
        cY = int((startY + endY) / 2.0)
        inputCentroids[i] = (cX, cY)
    
    # 2. Compute distance matrix between existing and new centroids
    D = dist.cdist(np.array(objectCentroids), inputCentroids)
    
    # 3. Find optimal matching using Hungarian algorithm approach
    rows = D.min(axis=1).argsort()
    cols = D.argmin(axis=1)[rows]
    
    # 4. Update existing objects or register new ones
    for (row, col) in zip(rows, cols):
        if D[row, col] <= self.maxDistance:
            objectID = objectIDs[row]
            self.objects[objectID] = inputCentroids[col]
            self.disappeared[objectID] = 0
```

### Counting Algorithm

```python
def determine_direction_and_count(self, objectID, centroid, trackableObject):
    # Calculate movement direction
    y_coordinates = [c[1] for c in trackableObject.centroids]
    direction = centroid[1] - np.mean(y_coordinates)
    
    # Check if object has been counted
    if not trackableObject.counted:
        # Entry: moving down and below center line
        if direction > 0 and centroid[1] > H // 2:
            totalDown += 1
            trackableObject.counted = True
            
        # Exit: moving up and above center line  
        elif direction < 0 and centroid[1] < H // 2:
            totalUp += 1
            trackableObject.counted = True
```

## Performance Characteristics

### Detection Performance
- **Model Size**: ~10MB (MobileNetSSD)
- **Inference Time**: 50-100ms per frame
- **Memory Usage**: ~200MB for model loading
- **Accuracy**: 90%+ for person detection

### Tracking Performance
- **Association Time**: <1ms per object
- **Memory Overhead**: ~1KB per tracked object
- **Max Objects**: 50+ simultaneous tracking
- **Tracking Accuracy**: 95%+ for continuous movement

### System Performance
- **Frame Rate**: 15-30 FPS (hardware dependent)
- **Latency**: <100ms with threading
- **CPU Usage**: 30-70% (multi-core)
- **Memory Usage**: 300-500MB total

## Configuration Parameters

### Detection Parameters
```python
CONFIDENCE_THRESHOLD = 0.4      # Minimum detection confidence
SKIP_FRAMES = 30                 # Detection frequency
FRAME_WIDTH = 500                # Processing width
```

### Tracking Parameters
```python
MAX_DISAPPEARED = 40             # Frames before deregistration
MAX_DISTANCE = 50                # Max association distance
```

### Alert Parameters
```python
THRESHOLD = 10                   # People limit for alerts
EMAIL_DELAY = 0                  # Alert frequency control
```

## Data Structures

### TrackableObject
```python
class TrackableObject:
    objectID: int                # Unique identifier
    centroids: List[Tuple]       # Historical positions
    counted: bool                # Counting status
```

### Detection Result
```python
detection = {
    'confidence': float,         # Detection confidence
    'class_id': int,            # Class index (15 for person)
    'bbox': Tuple[int, int, int, int]  # Bounding box coordinates
}
```

### Counting Data
```python
counting_data = {
    'move_in': List[int],        # Entry counts
    'move_out': List[int],       # Exit counts
    'in_time': List[str],        # Entry timestamps
    'out_time': List[str]        # Exit timestamps
}
```

## Error Handling

### Detection Errors
- **Low Confidence**: Filtered out automatically
- **No Detections**: Graceful handling with empty results
- **Model Loading**: Error checking for file existence

### Tracking Errors
- **Association Failures**: New object registration
- **Disappeared Objects**: Automatic cleanup
- **Memory Overflow**: Object limit enforcement

### System Errors
- **Camera Failures**: Automatic reconnection attempts
- **Email Failures**: Non-blocking error handling
- **File I/O Errors**: Graceful degradation

## Testing and Validation

### Unit Tests
- CentroidTracker association logic
- TrackableObject state management
- Email alert functionality
- Configuration loading

### Integration Tests
- End-to-end counting accuracy
- Multi-threading performance
- Alert system reliability
- Data logging integrity

### Performance Tests
- Frame rate benchmarks
- Memory usage monitoring
- CPU utilization analysis
- Latency measurements

## Deployment Considerations

### Hardware Requirements
- **Minimum**: 4GB RAM, Dual-core CPU
- **Recommended**: 8GB RAM, Quad-core CPU
- **Optimal**: 16GB RAM, Multi-core CPU with GPU

### Software Dependencies
- **Python**: 3.11.3 (recommended)
- **OpenCV**: 4.5.5.64
- **NumPy**: 1.24.3
- **dlib**: 19.24.1

### Network Requirements
- **Bandwidth**: 1-5 Mbps for IP cameras
- **Latency**: <100ms for real-time performance
- **Reliability**: Stable connection for continuous operation

## Security and Privacy

### Data Protection
- **Local Processing**: No cloud data transmission
- **Encryption**: SSL/TLS for email communication
- **Access Control**: File system permissions
- **Data Retention**: Configurable log cleanup

### System Security
- **Input Validation**: Configuration file checking
- **Error Handling**: Secure error messages
- **Resource Limits**: Memory and CPU constraints
- **Update Management**: Dependency version control

## Monitoring and Maintenance

### System Monitoring
- **Performance Metrics**: FPS, CPU, Memory usage
- **Error Logging**: Comprehensive error tracking
- **Alert Status**: Email system health
- **Data Quality**: Counting accuracy validation

### Maintenance Tasks
- **Model Updates**: Periodic retraining
- **Dependency Updates**: Security patches
- **Log Cleanup**: Automated data management
- **Performance Tuning**: Optimization adjustments

## Future Development Roadmap

### Short-term Improvements
- **Multi-camera Support**: Synchronized counting
- **Web Interface**: Remote monitoring dashboard
- **API Integration**: RESTful service endpoints
- **Mobile App**: Remote control and monitoring

### Long-term Enhancements
- **Deep Learning Tracking**: Advanced tracking algorithms
- **Cloud Integration**: Scalable cloud deployment
- **Analytics Platform**: Advanced reporting and insights
- **Edge Computing**: Optimized embedded solutions

This technical specification provides comprehensive details about the system architecture, algorithms, and implementation considerations for the real-time people counting system.
