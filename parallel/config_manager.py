"""
Configuration Manager for Parallel People Counting
===================================================

Manages multi-camera/video configuration and validation.
"""

import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages configuration for parallel people counting system.
    """

    def __init__(self, config_path: str):
        """
        Initialize ConfigManager with config file.

        Args:
            config_path: Path to JSON configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise

    def _validate_config(self):
        """Validate configuration structure."""
        required_keys = ['parallel_config', 'cameras', 'videos']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required key in config: {key}")

        # Validate parallel_config
        parallel_config = self.config.get('parallel_config', {})
        if 'worker_count' not in parallel_config:
            logger.warning("worker_count not specified, defaulting to 4")
            parallel_config['worker_count'] = 4

        # Validate cameras
        for i, camera in enumerate(self.config.get('cameras', [])):
            if 'camera_id' not in camera:
                raise ValueError(f"Camera {i} missing camera_id")
            if 'source' not in camera:
                raise ValueError(f"Camera {i} missing source")

        # Validate videos
        for i, video in enumerate(self.config.get('videos', [])):
            if 'video_id' not in video:
                raise ValueError(f"Video {i} missing video_id")
            if 'path' not in video:
                raise ValueError(f"Video {i} missing path")

        logger.info("Configuration validation passed")

    def get_parallel_config(self) -> Dict[str, Any]:
        """Get parallel processing configuration."""
        return self.config.get('parallel_config', {})

    def get_enabled_cameras(self) -> List[Dict[str, Any]]:
        """Get list of enabled cameras."""
        cameras = self.config.get('cameras', [])
        return [cam for cam in cameras if cam.get('enabled', True)]

    def get_enabled_videos(self) -> List[Dict[str, Any]]:
        """Get list of enabled videos."""
        videos = self.config.get('videos', [])
        return [vid for vid in videos if vid.get('enabled', True)]

    def get_camera_config(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific camera."""
        for camera in self.get_enabled_cameras():
            if camera.get('camera_id') == camera_id:
                return camera
        return None

    def get_video_config(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific video."""
        for video in self.get_enabled_videos():
            if video.get('video_id') == video_id:
                return video
        return None

    def create_tasks(self) -> List[Dict[str, Any]]:
        """
        Create task list from configuration.

        Returns:
            List of task dictionaries
        """
        tasks = []

        # Create tasks for enabled cameras
        for camera in self.get_enabled_cameras():
            task = {
                'task_id': f"camera_{camera['camera_id']}",
                'type': 'camera',
                'camera_id': camera['camera_id'],
                'source': camera['source'],
                'alias': camera.get('alias', camera['camera_id']),
                'location': camera.get('location', ''),
                'threshold': camera.get('threshold', 10),
                'config': camera,
                'priority': 1,
                'status': 'pending'
            }
            tasks.append(task)

        # Create tasks for enabled videos
        for video in self.get_enabled_videos():
            task = {
                'task_id': f"video_{video['video_id']}",
                'type': 'video',
                'video_id': video['video_id'],
                'source': video['path'],
                'alias': video.get('alias', video['video_id']),
                'threshold': video.get('threshold', 5),
                'config': video,
                'priority': 2,  # Lower priority than cameras
                'status': 'pending'
            }
            tasks.append(task)

        logger.info(f"Created {len(tasks)} tasks from configuration")
        return tasks

    def get_worker_count(self) -> int:
        """Get configured worker count."""
        return self.config.get('parallel_config', {}).get('worker_count', 4)

    def get_log_level(self) -> str:
        """Get configured log level."""
        return self.config.get('parallel_config', {}).get('log_level', 'INFO')

    def get_result_output_dir(self) -> str:
        """Get result output directory."""
        return self.config.get('parallel_config', {}).get('result_output', 'parallel/results/')

