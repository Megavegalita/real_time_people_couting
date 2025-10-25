# Real-Time People Counting System

A comprehensive, production-ready people counting system for business applications using computer vision and AI.

<div align="center">
<img src="https://imgur.com/SaF1kk3.gif" width="550">
<p><strong>Live Demo</strong></p>
</div>

## 🎯 Overview

This system provides **real-time people counting** for stores, buildings, shopping malls, and commercial spaces. It features:

- **Real-time detection** using MobileNetSSD
- **Robust tracking** with centroid-based algorithms
- **Camera configuration** system for Dahua RTSP cameras
- **Alert system** with email notifications
- **Data logging** for analytics
- **Performance optimization** with threading

## 🚀 Quick Start

### Prerequisites
- Python 3.11.3+
- OpenCV 4.x
- Camera or video source

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Megavegalita/real_time_people_couting.git
cd real_time_people_couting
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the system:**
```bash
# Edit utils/config.json
{
    "Email_Send": "your-email@gmail.com",
    "Email_Receive": "admin@company.com", 
    "Email_Password": "your-app-password",
    "url": "0",  # 0 for webcam, or RTSP URL
    "ALERT": true,
    "Threshold": 10,
    "Thread": true,
    "Log": true
}
```

### Running the System

#### Webcam
```bash
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel
```

#### IP Camera (Dahua)
```bash
# First configure camera
python camera_config/camera_manager.py --create

# Then run with camera config
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel
```

#### Video File
```bash
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel --input utils/data/tests/test_1.mp4
```

## 📁 Project Structure

```
real_time_people_couting/
├── camera_config/              # Camera configuration system
│   ├── camera_template.json    # Configuration template
│   ├── camera_manager.py       # Configuration management
│   └── README.md              # Camera setup guide
├── detector/                   # AI models
│   ├── MobileNetSSD_deploy.caffemodel
│   └── MobileNetSSD_deploy.prototxt
├── tracker/                    # Tracking algorithms
│   ├── centroidtracker.py     # Centroid-based tracking
│   └── trackableobject.py     # Object state management
├── utils/                      # Utilities and config
│   ├── config.json            # Main configuration
│   ├── mailer.py              # Email alerts
│   ├── thread.py              # Performance threading
│   └── data/logs/             # Data storage
├── people_counter.py           # Main application
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🔧 Camera Configuration

### Dahua RTSP Cameras

The system includes a comprehensive camera configuration system for Dahua cameras:

#### Create Camera Configuration
```bash
python camera_config/camera_manager.py --create
```

#### Test Camera Connection
```bash
python camera_config/camera_manager.py --test dahua_camera_config.json
```

#### List All Cameras
```bash
python camera_config/camera_manager.py --list
```

### Configuration Example
```json
{
  "camera_info": {
    "brand": "Dahua",
    "model": "IPC-HFW4431R-Z",
    "company": "autoeyes",
    "alias": "Main Entrance Cam",
    "location": "Main Entrance",
    "address": "123 Main Street, City, State 12345",
    "map_location": "40.7128,-74.0060"
  },
  "connection": {
    "host": "192.168.1.100",
    "username": "admin",
    "password": "password123",
    "full_url": "rtsp://admin:password123@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0"
  }
}
```

## 🧠 Technical Details

### Detection System
- **Model**: MobileNetSSD (Single Shot Detector)
- **Architecture**: MobileNet backbone for efficiency
- **Classes**: 21 object classes including "person"
- **Performance**: 50-100ms inference time
- **Accuracy**: 90%+ for person detection

### Tracking System
- **Algorithm**: Centroid-based tracking with distance association
- **Features**: 
  - Unique ID assignment
  - Movement direction detection
  - Disappearance handling
  - Hungarian algorithm for optimal matching
- **Parameters**:
  - `maxDisappeared`: 40 frames
  - `maxDistance`: 50 pixels

### Performance Optimization
- **Skip Frame Detection**: Every 30 frames
- **dlib Correlation Tracking**: Fast intermediate tracking
- **Threading Support**: Reduces latency
- **Memory Efficient**: Centroid-only storage

## ⚙️ Configuration Options

### Main Configuration (`utils/config.json`)

```json
{
    "Email_Send": "sender@company.com",      // Email for alerts
    "Email_Receive": "admin@company.com",    // Alert recipient
    "Email_Password": "app-password",        // Email password
    "url": "0",                              // Camera source (0=webcam, URL=IP)
    "ALERT": true,                           // Enable email alerts
    "Threshold": 10,                         // People count threshold
    "Thread": true,                          // Enable threading
    "Log": true,                             // Enable data logging
    "Scheduler": false,                      // Enable scheduling
    "Timer": false                           // Enable timer
}
```

### Command Line Options

```bash
python people_counter.py [OPTIONS]

Options:
  --prototxt PATH          Path to prototxt file (required)
  --model PATH             Path to model file (required)
  --input PATH             Input video file (optional)
  --output PATH            Output video file (optional)
  --confidence FLOAT       Detection confidence (default: 0.4)
  --skip-frames INT        Skip frames between detections (default: 30)
```

## 📊 Features

### Real-Time Alerts
- **Email Notifications**: Automatic alerts when threshold exceeded
- **Configurable Thresholds**: Set custom people limits
- **Real-Time Monitoring**: Continuous surveillance

### Data Logging
- **CSV Export**: Daily counting data
- **Timestamp Tracking**: Entry/exit times
- **Analytics Ready**: Data for business intelligence

### Performance Features
- **Threading**: Multi-threaded processing for better performance
- **Scheduling**: Automatic start/stop at specified times
- **Timer**: Configurable execution duration
- **Memory Management**: Efficient resource usage

## 🔍 Troubleshooting

### Common Issues

#### Camera Connection Problems
```bash
# Test camera connection
python camera_config/camera_manager.py --test your_camera_config.json

# Check RTSP URL format
rtsp://username:password@ip:port/cam/realmonitor?channel=1&subtype=0
```

#### Performance Issues
- Enable threading: `"Thread": true`
- Reduce skip frames: `--skip-frames 15`
- Lower confidence: `--confidence 0.3`

#### Email Alerts Not Working
- Check email credentials
- Use app-specific passwords for Gmail
- Verify SMTP settings

### RTSP URL Formats for Dahua Cameras

```
# Main Stream (High Resolution)
rtsp://username:password@ip:port/cam/realmonitor?channel=1&subtype=0

# Sub Stream (Low Resolution)  
rtsp://username:password@ip:port/cam/realmonitor?channel=1&subtype=1

# Alternative Formats
rtsp://username:password@ip:port/Streaming/Channels/101
rtsp://username:password@ip:port/live/ch00_0
rtsp://username:password@ip:port/unicast/c1/s0/live
```

## 📈 Business Applications

### Use Cases
- **Retail Stores**: Customer counting and analytics
- **Shopping Malls**: Foot traffic monitoring
- **Office Buildings**: Occupancy management
- **COVID-19 Compliance**: Capacity monitoring
- **Security**: Access control and monitoring

### Benefits
- **Real-Time Monitoring**: Immediate insights
- **Automated Alerts**: Staff notifications
- **Data Analytics**: Historical trend analysis
- **Cost Effective**: Open source solution
- **Scalable**: Multiple camera support

## 🛠️ Development

### Adding New Features
1. **Camera Support**: Add new camera configurations
2. **Detection Models**: Integrate different AI models
3. **Tracking Algorithms**: Implement advanced tracking
4. **Analytics**: Add business intelligence features

### API Integration
```python
from camera_config.camera_manager import CameraConfigManager

# Load camera configuration
manager = CameraConfigManager()
config = manager.load_camera_config("camera_config.json")

# Use with people counter
rtsp_url = config["connection"]["full_url"]
```

## 📚 Dependencies

### Core Requirements
```
opencv-python==4.12.0.88
numpy==2.2.6
imutils==0.5.4
dlib==19.24.1
scipy
schedule
```

### Installation
```bash
pip install -r requirements.txt
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check the LICENSE file for details.

## 🙏 Acknowledgments

- Based on PyImageSearch's people counter tutorial
- MobileNetSSD model from OpenCV
- dlib correlation tracking
- Community contributions

---

**Company**: autoeyes  
**Version**: 2.0  
**Last Updated**: 2024

For technical support or questions, please refer to the documentation or create an issue in the repository.