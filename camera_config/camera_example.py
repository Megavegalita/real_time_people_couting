#!/usr/bin/env python3
"""
Example script demonstrating how to use camera configurations
with the people counting system
"""

import cv2
import json
import sys
import os
from camera_manager import CameraConfigManager

def load_camera_from_config(config_file: str):
    """Load camera configuration and return OpenCV VideoCapture object"""
    
    # Initialize camera manager
    manager = CameraConfigManager()
    
    try:
        # Load camera configuration
        config = manager.load_camera_config(config_file)
        
        # Test RTSP connection
        rtsp_ok, message = manager.test_rtsp_connection(config)
        print(f"RTSP Connection Test: {message}")
        
        if not rtsp_ok:
            print("Failed to connect to camera. Please check configuration.")
            return None, None
        
        # Get RTSP URL
        rtsp_url = config["connection"]["full_url"]
        print(f"Connecting to: {rtsp_url}")
        
        # Create OpenCV VideoCapture
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            print("Failed to open video stream")
            return None, None
        
        # Set video properties from config
        video_settings = config["video_settings"]
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, video_settings["resolution"]["width"])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, video_settings["resolution"]["height"])
        cap.set(cv2.CAP_PROP_FPS, video_settings["fps"])
        
        print(f"Camera Info:")
        print(f"  Brand: {config['camera_info']['brand']}")
        print(f"  Model: {config['camera_info']['model']}")
        print(f"  Company: {config['camera_info']['company']}")
        print(f"  Alias: {config['camera_info']['alias']}")
        print(f"  Location: {config['camera_info']['location']}")
        print(f"  Address: {config['camera_info']['address']}")
        print(f"  Map Location: {config['camera_info']['map_location']}")
        print(f"  Resolution: {video_settings['resolution']['width']}x{video_settings['resolution']['height']}")
        print(f"  FPS: {video_settings['fps']}")
        
        return cap, config
        
    except Exception as e:
        print(f"Error loading camera configuration: {e}")
        return None, None

def draw_roi(frame, config):
    """Draw Region of Interest on frame"""
    roi = config["detection_settings"]["roi"]
    
    if roi["enabled"]:
        points = roi["coordinates"]
        pts = [(p["x"], p["y"]) for p in points]
        
        # Draw ROI polygon
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        
        # Draw ROI label
        cv2.putText(frame, "ROI", (points[0]["x"], points[0]["y"] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def draw_counting_line(frame, config):
    """Draw counting line on frame"""
    counting_line = config["detection_settings"]["counting_line"]
    
    if counting_line["enabled"]:
        start = counting_line["start_point"]
        end = counting_line["end_point"]
        
        # Draw counting line
        cv2.line(frame, (start["x"], start["y"]), (end["x"], end["y"]), (255, 0, 0), 2)
        
        # Draw direction arrow
        mid_x = (start["x"] + end["x"]) // 2
        mid_y = (start["y"] + end["y"]) // 2
        
        if counting_line["direction"] == "bidirectional":
            cv2.putText(frame, "<->", (mid_x - 20, mid_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        else:
            cv2.putText(frame, "->", (mid_x - 10, mid_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

def main():
    """Main function to demonstrate camera usage"""
    
    if len(sys.argv) != 2:
        print("Usage: python camera_example.py <config_file>")
        print("Example: python camera_example.py dahua_camera_config.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Load camera
    cap, config = load_camera_from_config(config_file)
    
    if cap is None or config is None:
        print("Failed to initialize camera")
        sys.exit(1)
    
    print("\nCamera stream started. Press 'q' to quit, 's' to save frame")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Failed to read frame")
                break
            
            frame_count += 1
            
            # Draw ROI and counting line
            draw_roi(frame, config)
            draw_counting_line(frame, config)
            
            # Add frame counter
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add camera info
            alias = config['camera_info']['alias'] or config['camera_info']['model']
            camera_info = f"{config['camera_info']['brand']} {alias}"
            cv2.putText(frame, camera_info, (10, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow("Camera Stream", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                filename = f"frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Frame saved as: {filename}")
    
    except KeyboardInterrupt:
        print("\nStopping camera stream...")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Camera stream stopped")

if __name__ == "__main__":
    main()
