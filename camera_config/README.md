# Camera Configuration System - Optimized

This directory contains optimized camera configuration files with essential fields only and comprehensive inline documentation.

## Files Overview

### Configuration Files
- `camera_template.json` - Optimized template with essential fields and inline documentation
- `dahua_camera_config.json` - Production-ready example configuration
- `camera_manager.py` - Python utility for managing camera configurations
- `camera_example.py` - Example script showing camera usage

## Optimized Configuration Structure

The configuration has been streamlined to include only essential fields for camera operation:

### Camera Information
```json
{
  "camera_info": {
    "brand": "Dahua",
    "model": "IPC-HFW4431R-Z", 
    "serial_number": "DH1234567890",
    "company": "autoeyes",
    "alias": "Main Entrance Cam",
    "location": "Main Entrance",
    "address": "123 Main Street, New York, NY 10001",
    "map_location": "40.7128,-74.0060",
    "installation_date": "2024-01-15"
  }
}
```

### Connection Settings
```json
{
  "connection": {
    "host": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "admin123",
    "stream_path": "/cam/realmonitor?channel=1&subtype=0",
    "full_url": "rtsp://admin:admin123@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0"
  }
}
```

### Video Settings
```json
{
  "video_settings": {
    "resolution": {"width": 1920, "height": 1080},
    "fps": 25,
    "codec": "H.264"
  }
}
```

### Detection Settings
```json
{
  "detection_settings": {
    "roi": {
      "enabled": true,
      "coordinates": [
        {"x": 100, "y": 100},
        {"x": 800, "y": 100}, 
        {"x": 800, "y": 600},
        {"x": 100, "y": 600}
      ]
    },
    "counting_line": {
      "enabled": true,
      "start_point": {"x": 0, "y": 300},
      "end_point": {"x": 1920, "y": 300},
      "direction": "bidirectional"
    },
    "sensitivity": 0.5,
    "min_object_size": 30,
    "max_object_size": 200
  }
}
```

## Essential Fields Only

### Removed Fields (Non-Essential)
- `firmware_version` - Not needed for basic operation
- `address` - Redundant with location
- `store_manager` - Not essential for camera operation
- `notes` - Optional information
- `bitrate` - Auto-managed by camera
- `quality` - Redundant with resolution
- `stream_configs` - Simplified to single stream
- `recording` - Handled by external system
- `email_notifications` - External alert system
- `webhook_url` - External alert system
- `advanced_settings` - Camera-specific features
- `last_calibration` - Maintenance tracking
- `next_maintenance` - Maintenance tracking

### Kept Fields (Essential)
- **Camera Info**: Brand, model, serial, company, alias, location, address, map location, installation date
- **Connection**: Host, port, credentials, stream path, full URL
- **Video**: Resolution, FPS, codec
- **Detection**: ROI, counting line, sensitivity, object size limits
- **Alerts**: Enabled status, threshold, cooldown
- **Network**: Timeout, retry attempts
- **Maintenance**: Status, health check interval

## Inline Documentation

Each configuration file includes comprehensive inline documentation:

```json
{
  "_comment": "Section description",
  "_documentation": "Overall file documentation",
  "field_name": "value",
  "_doc_field_name": "Detailed explanation of this field"
}
```

### Documentation Features
- **Section Comments**: Explain each major section
- **Field Documentation**: Detailed explanation for each field
- **Usage Examples**: Show expected values and formats
- **Configuration Notes**: Important considerations

## Map Location Formats

The `map_location` field supports multiple formats for store location:

### GPS Coordinates
```
"40.7128,-74.0060"  # Latitude, Longitude (New York City)
"34.0522,-118.2437"  # Latitude, Longitude (Los Angeles)
```

### Google Maps Links
```
"https://maps.google.com/?q=123+Main+Street+New+York+NY"
"https://goo.gl/maps/ABC123"
```

### Address Format
```
"123 Main Street, New York, NY 10001"
"456 Oak Avenue, Los Angeles, CA 90210"
```

### Usage Examples
- **GPS Coordinates**: Best for precise location tracking
- **Google Maps Links**: Easy to share and view
- **Address Format**: Human-readable location information

## Dahua RTSP URL Formats

### Standard RTSP URLs for Dahua Cameras

#### Main Stream (High Resolution)
```
rtsp://username:password@ip:port/cam/realmonitor?channel=1&subtype=0
```

#### Sub Stream (Low Resolution) 
```
rtsp://username:password@ip:port/cam/realmonitor?channel=1&subtype=1
```

#### Alternative URL Formats
```
# Format 1
rtsp://username:password@ip:port/Streaming/Channels/101

# Format 2  
rtsp://username:password@ip:port/live/ch00_0

# Format 3
rtsp://username:password@ip:port/unicast/c1/s0/live
```

## Using the Camera Manager

### Command Line Usage

#### Create New Camera Configuration
```bash
python camera_manager.py --create
```

#### Test Camera Connection
```bash
python camera_manager.py --test dahua_camera_config.json
```

#### List All Configurations
```bash
python camera_manager.py --list
```

#### Validate Configuration
```bash
python camera_manager.py --validate dahua_camera_config.json
```

### Python API Usage

```python
from camera_manager import CameraConfigManager

# Initialize manager
manager = CameraConfigManager()

# Load existing configuration
config = manager.load_camera_config("dahua_camera_config.json")

# Test RTSP connection
rtsp_ok, message = manager.test_rtsp_connection(config)
print(f"RTSP Test: {message}")

# Test HTTP connection  
http_ok, message = manager.test_http_connection(config)
print(f"HTTP Test: {message}")

# Validate configuration
errors = manager.validate_config(config)
if errors:
    print("Configuration errors:", errors)

# Create new configuration
new_config = manager.create_camera_config(
    brand="Dahua",
    model="IPC-HFW4431R-Z",
    host="192.168.1.101",
    username="admin", 
    password="password123",
    company="autoeyes",
    alias="Side Entrance Cam",
    location="Side Entrance",
    address="456 Oak Avenue, Los Angeles, CA 90210",
    map_location="34.0522,-118.2437"
)

# Save configuration
manager.save_camera_config(new_config, "side_entrance_camera.json")
```

## Configuration Parameters

### Essential Parameters Only

#### Camera Information
- `brand`: Camera manufacturer
- `model`: Specific camera model
- `serial_number`: Unique identifier
- `company`: Company name (autoeyes)
- `alias`: Friendly name
- `location`: Physical location
- `address`: Full store address
- `map_location`: GPS coordinates or map link
- `installation_date`: Installation date

#### Connection Settings
- `host`: Camera IP address
- `port`: RTSP port (554)
- `username`: Login username
- `password`: Login password
- `stream_path`: RTSP stream path
- `full_url`: Complete RTSP URL

#### Video Settings
- `resolution`: Video resolution (width x height)
- `fps`: Frames per second
- `codec`: Video codec (H.264)

#### Detection Settings
- `roi.enabled`: Enable region of interest
- `roi.coordinates`: Detection area polygon
- `counting_line.enabled`: Enable counting line
- `counting_line.start_point`: Line start coordinates
- `counting_line.end_point`: Line end coordinates
- `counting_line.direction`: Counting direction
- `sensitivity`: Detection sensitivity (0.0-1.0)
- `min_object_size`: Minimum object size
- `max_object_size`: Maximum object size

#### Alert Settings
- `enabled`: Enable alerts
- `threshold`: People count threshold
- `cooldown_period`: Alert cooldown (seconds)

#### Network Settings
- `timeout`: Connection timeout (seconds)
- `retry_attempts`: Retry attempts

#### Maintenance Settings
- `status`: Camera status
- `health_check_interval`: Health check interval (seconds)

## Troubleshooting

### Common RTSP Connection Issues

1. **Authentication Failed**
   - Verify username and password
   - Check if camera requires special characters

2. **Connection Timeout**
   - Verify IP address and port
   - Check network connectivity
   - Ensure camera is powered on

3. **Stream Not Available**
   - Check if RTSP service is enabled on camera
   - Verify stream path format
   - Try alternative URL formats

4. **Poor Video Quality**
   - Adjust resolution settings
   - Check network bandwidth
   - Verify FPS settings

## Integration with People Counter

The optimized camera configuration integrates seamlessly with the people counting application:

```python
# In people_counter.py
from camera_config.camera_manager import CameraConfigManager

def load_camera_config(camera_name):
    manager = CameraConfigManager()
    return manager.load_camera_config(f"{camera_name}_config.json")

# Load camera configuration
config = load_camera_config("dahua")
rtsp_url = config["connection"]["full_url"]

# Use with OpenCV
cap = cv2.VideoCapture(rtsp_url)
```

## Benefits of Optimized Configuration

1. **Simplified Structure**: Only essential fields for operation
2. **Comprehensive Documentation**: Inline explanations for every field
3. **Reduced Complexity**: Easier to understand and maintain
4. **Faster Processing**: Less data to parse and validate
5. **Clear Purpose**: Each field has a specific function
6. **Easy Customization**: Simple to modify for different cameras

## Support

For issues with camera configurations:
1. Check camera network connectivity
2. Verify RTSP URL format
3. Test with camera's web interface
4. Review inline documentation
5. Check firewall settings