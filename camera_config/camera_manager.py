#!/usr/bin/env python3
"""
Camera Configuration Manager for Dahua RTSP Cameras
Provides utilities to manage camera configurations and validate RTSP streams
"""

import json
import os
import cv2
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CameraConfigManager:
    """Manages camera configurations for Dahua RTSP cameras"""
    
    def __init__(self, config_dir: str = "camera_config"):
        self.config_dir = config_dir
        self.ensure_config_dir()
    
    def ensure_config_dir(self) -> None:
        """Ensure the camera config directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logger.info(f"Created camera config directory: {self.config_dir}")
    
    def load_camera_config(self, config_file: str) -> Dict:
        """Load camera configuration from JSON file"""
        config_path = os.path.join(self.config_dir, config_file)
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded camera config: {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_file}: {e}")
            raise
    
    def save_camera_config(self, config: Dict, config_file: str) -> None:
        """Save camera configuration to JSON file"""
        config_path = os.path.join(self.config_dir, config_file)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved camera config: {config_file}")
        except Exception as e:
            logger.error(f"Failed to save config {config_file}: {e}")
            raise
    
    def create_camera_config(self, 
                           brand: str = "Dahua",
                           model: str = "",
                           host: str = "192.168.1.100",
                           username: str = "admin",
                           password: str = "admin",
                           company: str = "autoeyes",
                           alias: str = "",
                           location: str = "",
                           address: str = "",
                           map_location: str = "",
                           serial_number: str = "") -> Dict:
        """Create a new camera configuration"""
        
        config = {
            "camera_info": {
                "brand": brand,
                "model": model,
                "serial_number": serial_number,
                "company": company,
                "alias": alias,
                "location": location,
                "address": address,
                "map_location": map_location,
                "installation_date": datetime.now().strftime("%Y-%m-%d")
            },
            "connection": {
                "protocol": "rtsp",
                "host": host,
                "port": 554,
                "username": username,
                "password": password,
                "stream_path": "/cam/realmonitor?channel=1&subtype=0",
                "full_url": f"rtsp://{username}:{password}@{host}:554/cam/realmonitor?channel=1&subtype=0"
            },
            "video_settings": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 25,
                "codec": "H.264"
            },
            "detection_settings": {
                "roi": {
                    "enabled": True,
                    "coordinates": [
                        {"x": 100, "y": 100},
                        {"x": 800, "y": 100},
                        {"x": 800, "y": 600},
                        {"x": 100, "y": 600}
                    ]
                },
                "counting_line": {
                    "enabled": True,
                    "start_point": {"x": 0, "y": 300},
                    "end_point": {"x": 1920, "y": 300},
                    "direction": "bidirectional"
                },
                "sensitivity": 0.5,
                "min_object_size": 30,
                "max_object_size": 200
            },
            "alerts": {
                "enabled": True,
                "threshold": 5,
                "cooldown_period": 60
            },
            "network": {
                "timeout": 30,
                "retry_attempts": 3
            },
            "maintenance": {
                "status": "active",
                "health_check_interval": 300
            }
        }
        
        return config
    
    def test_rtsp_connection(self, config: Dict) -> Tuple[bool, str]:
        """Test RTSP connection to camera"""
        rtsp_url = config["connection"]["full_url"]
        
        try:
            cap = cv2.VideoCapture(rtsp_url)
            
            if not cap.isOpened():
                return False, "Failed to open RTSP stream"
            
            # Try to read a frame
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                return True, "RTSP connection successful"
            else:
                return False, "Failed to read frame from RTSP stream"
                
        except Exception as e:
            return False, f"RTSP connection error: {str(e)}"
    
    def test_http_connection(self, config: Dict) -> Tuple[bool, str]:
        """Test HTTP connection to camera web interface"""
        host = config["connection"]["host"]
        port = config["network"]["http_port"]
        
        try:
            url = f"http://{host}:{port}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return True, "HTTP connection successful"
            else:
                return False, f"HTTP connection failed with status: {response.status_code}"
                
        except Exception as e:
            return False, f"HTTP connection error: {str(e)}"
    
    def validate_config(self, config: Dict) -> List[str]:
        """Validate camera configuration"""
        errors = []
        
        # Check required fields
        required_fields = [
            "camera_info.brand",
            "camera_info.model",
            "connection.host",
            "connection.username",
            "connection.password"
        ]
        
        for field in required_fields:
            keys = field.split('.')
            current = config
            try:
                for key in keys:
                    current = current[key]
                if not current:
                    errors.append(f"Missing or empty field: {field}")
            except KeyError:
                errors.append(f"Missing field: {field}")
        
        # Validate IP address format
        host = config.get("connection", {}).get("host", "")
        if host and not self.is_valid_ip(host):
            errors.append(f"Invalid IP address format: {host}")
        
        # Validate port numbers
        ports = [
            ("connection.port", config.get("connection", {}).get("port", 0)),
            ("network.rtsp_port", config.get("network", {}).get("rtsp_port", 0)),
            ("network.http_port", config.get("network", {}).get("http_port", 0))
        ]
        
        for port_name, port in ports:
            if not (1 <= port <= 65535):
                errors.append(f"Invalid port number for {port_name}: {port}")
        
        return errors
    
    def is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                if not (0 <= int(part) <= 255):
                    return False
            return True
        except ValueError:
            return False
    
    def list_camera_configs(self) -> List[str]:
        """List all available camera configuration files"""
        config_files = []
        
        if os.path.exists(self.config_dir):
            for file in os.listdir(self.config_dir):
                if file.endswith('.json'):
                    config_files.append(file)
        
        return sorted(config_files)
    
    def get_camera_info(self, config: Dict) -> Dict:
        """Extract camera information for display"""
        return {
            "brand": config["camera_info"]["brand"],
            "model": config["camera_info"]["model"],
            "company": config["camera_info"]["company"],
            "alias": config["camera_info"]["alias"],
            "location": config["camera_info"]["location"],
            "address": config["camera_info"]["address"],
            "map_location": config["camera_info"]["map_location"],
            "host": config["connection"]["host"],
            "status": config["maintenance"]["status"],
            "rtsp_url": config["connection"]["full_url"]
        }


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Camera Configuration Manager")
    parser.add_argument("--create", help="Create new camera config")
    parser.add_argument("--test", help="Test camera connection")
    parser.add_argument("--list", action="store_true", help="List all camera configs")
    parser.add_argument("--validate", help="Validate camera config")
    
    args = parser.parse_args()
    
    manager = CameraConfigManager()
    
    if args.create:
        # Interactive camera creation
        print("Creating new camera configuration...")
        brand = input("Brand (default: Dahua): ").strip() or "Dahua"
        model = input("Model: ").strip()
        host = input("IP Address: ").strip()
        username = input("Username (default: admin): ").strip() or "admin"
        password = input("Password: ").strip()
        company = input("Company (default: autoeyes): ").strip() or "autoeyes"
        alias = input("Alias (friendly name): ").strip()
        location = input("Location: ").strip()
        address = input("Store Address: ").strip()
        map_location = input("Map Location (GPS coordinates or map link): ").strip()
        serial = input("Serial Number: ").strip()
        
        config = manager.create_camera_config(
            brand=brand, model=model, host=host,
            username=username, password=password,
            company=company, alias=alias, location=location,
            address=address, map_location=map_location,
            serial_number=serial
        )
        
        filename = f"{brand.lower()}_{model.lower().replace(' ', '_')}_config.json"
        manager.save_camera_config(config, filename)
        print(f"Camera configuration saved as: {filename}")
    
    elif args.test:
        config = manager.load_camera_config(args.test)
        print(f"Testing camera: {config['camera_info']['brand']} {config['camera_info']['model']}")
        
        rtsp_ok, rtsp_msg = manager.test_rtsp_connection(config)
        http_ok, http_msg = manager.test_http_connection(config)
        
        print(f"RTSP Test: {'✓' if rtsp_ok else '✗'} {rtsp_msg}")
        print(f"HTTP Test: {'✓' if http_ok else '✗'} {http_msg}")
    
    elif args.list:
        configs = manager.list_camera_configs()
        print("Available camera configurations:")
        for config_file in configs:
            try:
                config = manager.load_camera_config(config_file)
                info = manager.get_camera_info(config)
                alias_text = f" ({info['alias']})" if info['alias'] else ""
                location_text = f" - {info['location']}" if info['location'] else ""
                print(f"  {config_file}: {info['brand']} {info['model']}{alias_text}{location_text} at {info['host']}")
            except Exception as e:
                print(f"  {config_file}: Error loading config - {e}")
    
    elif args.validate:
        config = manager.load_camera_config(args.validate)
        errors = manager.validate_config(config)
        
        if errors:
            print(f"Validation errors for {args.validate}:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"Configuration {args.validate} is valid!")


if __name__ == "__main__":
    main()
