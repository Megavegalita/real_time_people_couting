# 🚀 Quick Start Guide

## ✅ System Ready!

Your real-time people counting system is fully configured and ready to use.

## 🎯 Quick Commands

### **Run with Webcam**
```bash
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel
```

### **Run with Video File**
```bash
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel --input path/to/video.mp4
```

### **Run with IP Camera**
1. Edit `utils/config.json`:
```json
{
    "url": "rtsp://username:password@ip:port/stream"
}
```
2. Run:
```bash
python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel
```

## ⚙️ Configuration

### **Basic Settings** (`utils/config.json`)
```json
{
    "url": "0",                    // 0=webcam, URL=IP camera
    "ALERT": false,                // Enable email alerts
    "Threshold": 5,                // People count limit
    "Thread": true,                // Enable threading
    "Log": true                    // Enable data logging
}
```

### **Camera Configuration**
```bash
# Create camera config
python camera_config/camera_manager.py --create

# Test camera connection
python camera_config/camera_manager.py --test your_config.json
```

## 📊 Features

- **Real-time Detection**: MobileNetSSD person detection
- **Robust Tracking**: Centroid-based object tracking
- **Email Alerts**: Automatic notifications when threshold exceeded
- **Data Logging**: CSV export for analytics
- **Performance**: Threading support for better FPS
- **Camera Support**: Dahua RTSP camera integration

## 🔧 Troubleshooting

### **Low FPS**
- Enable threading: `"Thread": true`
- Lower confidence: `--confidence 0.3`
- Reduce skip frames: `--skip-frames 15`

### **Camera Issues**
- Test connection: `python camera_config/camera_manager.py --test config.json`
- Check RTSP URL format
- Verify credentials

### **Detection Issues**
- Adjust confidence threshold
- Check lighting conditions
- Ensure stable camera position

## 📈 Performance Tips

1. **Use Threading**: Enable for better performance
2. **Optimize Resolution**: Lower resolution = higher FPS
3. **Skip Frames**: Adjust based on your needs
4. **Confidence Threshold**: Lower for more detections

## 📚 Documentation

- **Main Guide**: [README.md](./README.md) - Complete system overview
- **Developer Guide**: [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) - Technical details
- **Camera Config**: [camera_config/README.md](./camera_config/README.md) - Camera setup

## 🎯 Next Steps

1. **Test with your camera**: Configure IP camera settings
2. **Set up alerts**: Configure email notifications
3. **Customize settings**: Adjust thresholds and parameters
4. **Monitor performance**: Check FPS and accuracy
5. **Deploy**: Set up for production use

---

**Need Help?** Check the main README.md for detailed documentation or create an issue in the repository.
