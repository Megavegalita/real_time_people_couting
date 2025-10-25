# Developer Guide - Real-Time People Counting System

## 🎯 System Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Video Input   │───▶│  Detection      │───▶│   Tracking      │
│                 │    │  (MobileNetSSD) │    │  (Centroid)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Logging  │◀───│   Counting      │◀───│  Direction      │
│                 │    │   Logic         │    │  Analysis        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### File Structure

```
people_counter.py           # Main application entry point
├── tracker/
│   ├── centroidtracker.py  # Centroid-based tracking algorithm
│   └── trackableobject.py  # Trackable object data structure
├── camera_config/
│   ├── camera_manager.py   # Camera configuration management
│   ├── camera_template.json # Configuration template
│   └── camera_example.py   # Usage examples
├── utils/
│   ├── config.json        # Main configuration
│   ├── mailer.py          # Email alert system
│   └── thread.py          # Performance threading
└── detector/
    ├── MobileNetSSD_deploy.caffemodel
    └── MobileNetSSD_deploy.prototxt
```

## 🔧 Core Algorithms

### 1. Detection Pipeline

```python
# MobileNetSSD Detection
def detect_people(frame, net, confidence_threshold=0.4):
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
    net.setInput(blob)
    detections = net.forward()
    
    rects = []
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            idx = int(detections[0, 0, i, 1])
            if CLASSES[idx] == "person":
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                rects.append(box.astype("int"))
    
    return rects
```

### 2. Tracking Algorithm

```python
# CentroidTracker Implementation
class CentroidTracker:
    def __init__(self, maxDisappeared=40, maxDistance=50):
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.nextObjectID = 0
    
    def update(self, rects):
        # Calculate centroids from bounding boxes
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
        
        # Compute distance matrix and associate objects
        D = dist.cdist(np.array(objectCentroids), inputCentroids)
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]
        
        # Update existing objects or register new ones
        for (row, col) in zip(rows, cols):
            if D[row, col] <= self.maxDistance:
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0
        
        return self.objects
```

### 3. Counting Logic

```python
# Direction and Counting Logic
def determine_direction_and_count(objectID, centroid, trackableObject):
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

## 🎛️ Configuration Management

### Camera Configuration System

```python
# Camera Configuration Manager
class CameraConfigManager:
    def __init__(self, config_dir="camera_config"):
        self.config_dir = config_dir
    
    def create_camera_config(self, brand="Dahua", model="", host="192.168.1.100"):
        config = {
            "camera_info": {
                "brand": brand,
                "model": model,
                "company": "autoeyes",
                "alias": "",
                "location": "",
                "address": "",
                "map_location": ""
            },
            "connection": {
                "host": host,
                "port": 554,
                "username": "admin",
                "password": "password",
                "full_url": f"rtsp://admin:password@{host}:554/cam/realmonitor?channel=1&subtype=0"
            },
            "video_settings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 25,
                "codec": "H.264"
            },
            "detection_settings": {
                "roi": {"enabled": True, "coordinates": [...]},
                "counting_line": {"enabled": True, "start_point": {...}, "end_point": {...}},
                "sensitivity": 0.5,
                "min_object_size": 30,
                "max_object_size": 200
            }
        }
        return config
```

### Main Configuration

```python
# utils/config.json
{
    "Email_Send": "sender@company.com",      # SMTP sender email
    "Email_Receive": "admin@company.com",    # Alert recipient
    "Email_Password": "app-password",        # Email app password
    "url": "0",                              # Camera source
    "ALERT": true,                           # Enable alerts
    "Threshold": 10,                         # People limit
    "Thread": true,                          # Enable threading
    "Log": true,                             # Enable logging
    "Scheduler": false,                      # Enable scheduling
    "Timer": false                           # Enable timer
}
```

## 🚀 Performance Optimization

### Threading Implementation

```python
# utils/thread.py
class ThreadingClass:
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)
        
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
    
    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(self.FPS)
    
    def read(self):
        return self.status, self.frame
```

### Skip Frame Detection

```python
# Optimized detection with skip frames
if totalFrames % args["skip_frames"] == 0:
    # Run expensive detection
    status = "Detecting"
    trackers = []
    detections = net.forward()
    # Process detections...
else:
    # Use fast correlation tracking
    status = "Tracking"
    for tracker in trackers:
        tracker.update(rgb)
        pos = tracker.get_position()
        rects.append((startX, startY, endX, endY))
```

## 📊 Data Management

### Logging System

```python
# Data logging implementation
def log_data(move_in, in_time, move_out, out_time):
    export_data = list(zip_longest(move_in, in_time, move_out, out_time))
    
    with open("utils/data/logs/counting_data.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(("Move In", "In Time", "Move Out", "Out Time"))
        wr.writerows(export_data)
```

### Email Alert System

```python
# utils/mailer.py
class Mailer:
    def send(self, email_receive):
        msg = MIMEMultipart()
        msg['From'] = config["Email_Send"]
        msg['To'] = email_receive
        msg['Subject'] = "People Count Alert"
        
        body = f"Alert! People count exceeded threshold of {config['Threshold']}"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(config["Email_Send"], config["Email_Password"])
        text = msg.as_string()
        server.sendmail(config["Email_Send"], email_receive, text)
        server.quit()
```

## 🔧 API Usage

### Camera Management API

```python
from camera_config.camera_manager import CameraConfigManager

# Initialize manager
manager = CameraConfigManager()

# Create new camera configuration
config = manager.create_camera_config(
    brand="Dahua",
    model="IPC-HFW4431R-Z",
    host="192.168.1.101",
    username="admin",
    password="password123",
    company="autoeyes",
    alias="Side Entrance Cam",
    location="Side Entrance"
)

# Save configuration
manager.save_camera_config(config, "side_entrance_camera.json")

# Test camera connection
rtsp_ok, message = manager.test_rtsp_connection(config)
print(f"RTSP Test: {message}")

# Load existing configuration
config = manager.load_camera_config("dahua_camera_config.json")
```

### Integration with Main Application

```python
# Integration example
def load_camera_config(camera_name):
    manager = CameraConfigManager()
    return manager.load_camera_config(f"{camera_name}_config.json")

# Use in people counter
config = load_camera_config("dahua")
rtsp_url = config["connection"]["full_url"]

# Initialize video capture
cap = cv2.VideoCapture(rtsp_url)
```

## 🧪 Testing

### Unit Tests

```python
# Example test structure
import unittest
from tracker.centroidtracker import CentroidTracker

class TestCentroidTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = CentroidTracker()
    
    def test_register_object(self):
        centroid = (100, 100)
        self.tracker.register(centroid)
        self.assertEqual(len(self.tracker.objects), 1)
    
    def test_update_tracking(self):
        # Test tracking update logic
        rects = [(50, 50, 150, 150)]
        objects = self.tracker.update(rects)
        self.assertIsInstance(objects, dict)
```

### Integration Tests

```python
# Camera configuration testing
def test_camera_config_creation():
    manager = CameraConfigManager()
    config = manager.create_camera_config(
        brand="Dahua",
        host="192.168.1.100"
    )
    
    assert config["camera_info"]["brand"] == "Dahua"
    assert config["connection"]["host"] == "192.168.1.100"
    assert "rtsp://" in config["connection"]["full_url"]
```

## 🐛 Debugging

### Common Issues and Solutions

#### 1. Camera Connection Issues
```python
# Debug camera connection
def debug_camera_connection(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print("Failed to open camera")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        return False
    
    print(f"Camera resolution: {frame.shape}")
    cap.release()
    return True
```

#### 2. Performance Issues
```python
# Performance monitoring
import time

def monitor_performance():
    start_time = time.time()
    
    # Your code here
    
    end_time = time.time()
    fps = 1.0 / (end_time - start_time)
    print(f"FPS: {fps:.2f}")
```

#### 3. Memory Management
```python
# Memory optimization
def optimize_memory():
    # Clear old tracking data
    if len(trackableObjects) > 100:
        old_objects = [k for k in trackableObjects.keys() if k < max(trackableObjects.keys()) - 50]
        for obj_id in old_objects:
            del trackableObjects[obj_id]
```

## 📈 Extending the System

### Adding New Camera Brands

```python
# Extend camera configuration
def create_hikvision_config(host, username, password):
    return {
        "camera_info": {
            "brand": "Hikvision",
            "model": "DS-2CD2143G0-I",
            "company": "autoeyes"
        },
        "connection": {
            "host": host,
            "username": username,
            "password": password,
            "full_url": f"rtsp://{username}:{password}@{host}:554/Streaming/Channels/101"
        }
    }
```

### Custom Detection Models

```python
# Integrate different detection models
def load_yolo_model(model_path):
    net = cv2.dnn.readNetFromDarknet(model_path + ".cfg", model_path + ".weights")
    return net

def detect_with_yolo(frame, net):
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()
    return process_yolo_outputs(outputs)
```

### Advanced Tracking Algorithms

```python
# Implement DeepSORT or other advanced trackers
class AdvancedTracker:
    def __init__(self):
        self.tracker = DeepSORT()
    
    def update(self, detections, frame):
        tracks = self.tracker.update(detections, frame)
        return tracks
```

## 🔒 Security Considerations

### Camera Security
- Change default passwords
- Use VPN for remote access
- Enable HTTPS/RTSP over TLS
- Regular firmware updates

### Data Protection
- Encrypt stored data
- Secure email credentials
- Access control for logs
- Regular backup procedures

---

This developer guide provides comprehensive technical details for extending and maintaining the real-time people counting system. For additional support, refer to the main README or create an issue in the repository.
