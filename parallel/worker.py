"""
Worker for Parallel People Counting
====================================

Worker thread implementation that processes one camera/video at a time.
"""

import cv2
import dlib
import time
import numpy as np
import imutils
import datetime
from threading import Thread
from queue import Queue, Empty
from typing import Dict, Any, Optional
import logging

import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from imutils.video import VideoStream, FPS
from parallel.standard_workflow import StandardPeopleCountingWorkflow

# Import thread module from parent utils directory
import importlib.util
thread_spec = importlib.util.spec_from_file_location("thread", os.path.join(parent_dir, "utils", "thread.py"))
thread = importlib.util.module_from_spec(thread_spec)
thread_spec.loader.exec_module(thread)

logger = logging.getLogger(__name__)


class PeopleCounterWorker(Thread):
    """
    Worker thread for processing camera/video streams.
    """

    def __init__(
        self,
        worker_id: str,
        task_queue: Queue,
        result_queue: Queue,
        net: cv2.dnn.Net,
        config: Dict[str, Any],
        task_config: Dict[str, Any]
    ):
        """
        Initialize worker.

        Args:
            worker_id: Unique worker identifier
            task_queue: Queue for receiving tasks
            result_queue: Queue for sending results
            net: Pre-loaded MobileNetSSD model
            config: Global configuration
            task_config: Per-task configuration
        """
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.net = net
        self.config = config
        self.task_config = task_config

        self.running = False
        self.current_task: Optional[Dict[str, Any]] = None

    def run(self):
        """Main worker loop."""
        self.running = True
        logger.info(f"[WORKER-{self.worker_id}] Started")

        while self.running:
            try:
                # Get task from queue (with timeout)
                task = self.task_queue.get(timeout=1)

                if task is None:  # Shutdown signal
                    logger.info(f"[WORKER-{self.worker_id}] Received shutdown signal")
                    break
            except Empty:
                # No task available, continue waiting
                continue

            try:
                self.current_task = task
                logger.info(f"[WORKER-{self.worker_id}] Processing task: {task['task_id']}")

                # Process task
                if task['type'] == 'camera':
                    self.process_camera(task)
                elif task['type'] == 'video':
                    self.process_video(task)
                else:
                    logger.warning(f"[WORKER-{self.worker_id}] Unknown task type: {task['type']}")

                self.current_task = None
                self.task_queue.task_done()

            except Exception as e:
                logger.error(f"[WORKER-{self.worker_id}] Error processing task: {e}", exc_info=True)
                if self.current_task:
                    self.send_result({
                        'worker_id': self.worker_id,
                        'task_id': self.current_task.get('task_id', 'unknown'),
                        'status': 'error',
                        'error': str(e)
                    })

    def process_camera(self, task: Dict[str, Any]):
        """
        Process camera stream.

        Args:
            task: Task configuration
        """
        camera_id = task['camera_id']
        source = task['source']
        threshold = task.get('threshold', 10)

        logger.info(f"[WORKER-{self.worker_id}] Starting camera: {camera_id}")

        # Initialize video stream
        try:
            vs = VideoStream(source).start()
            time.sleep(2.0)

            if self.config.get("Thread", False):
                vs = thread.ThreadingClass(source)
        except Exception as e:
            logger.error(f"[WORKER-{self.worker_id}] Failed to initialize camera {camera_id}: {e}")
            return

        # Process frames
        self.count_people(
            vs=vs,
            task_id=task['task_id'],
            camera_id=camera_id,
            is_camera=True,
            threshold=threshold
        )

        # Cleanup
        try:
            if self.config.get("Thread", False):
                vs.release()
            else:
                vs.stop()
        except Exception as e:
            logger.warning(f"[WORKER-{self.worker_id}] Error releasing camera: {e}")

        logger.info(f"[WORKER-{self.worker_id}] Completed camera: {camera_id}")

    def process_video(self, task: Dict[str, Any]):
        """
        Process video file.

        Args:
            task: Task configuration
        """
        video_id = task['video_id']
        video_path = task['source']
        threshold = task.get('threshold', 5)

        logger.info(f"[WORKER-{self.worker_id}] Starting video: {video_id}")

        # Initialize video capture
        try:
            vs = cv2.VideoCapture(video_path)
        except Exception as e:
            logger.error(f"[WORKER-{self.worker_id}] Failed to open video {video_id}: {e}")
            return

        # Process frames
        self.count_people(
            vs=vs,
            task_id=task['task_id'],
            video_id=video_id,
            is_camera=False,
            threshold=threshold
        )

        # Cleanup
        vs.release()
        logger.info(f"[WORKER-{self.worker_id}] Completed video: {video_id}")

    def count_people(
        self,
        vs,
        task_id: str,
        camera_id: str = None,
        video_id: str = None,
        is_camera: bool = True,
        threshold: int = 10
    ):
        """
        Core people counting logic (extracted from people_counter.py).

        Args:
            vs: Video stream
            task_id: Task identifier
            camera_id: Camera identifier
            video_id: Video identifier
            is_camera: Whether source is camera or video
            threshold: People count threshold
        """
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]

        # Initialize tracking
        ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        trackers = []
        trackableObjects = {}

        # Counting variables
        totalFrames = 0
        totalDown = 0
        totalUp = 0
        # Initialize empty lists to store the counting data (EXACT COPY FROM ORIGINAL)
        total = []  # For alert logic (line 109 in original)
        move_out = []
        move_in = []
        out_time = []
        in_time = []

        # FPS counter
        fps = FPS().start()

        # Configuration from task_config
        skip_frames = self.task_config.get('skip_frames', 30)
        confidence = self.task_config.get('confidence', 0.4)
        
        # DEBUG: Enable detailed logging for this worker
        logger.setLevel(logging.DEBUG)
        logger.info(f"[DEBUG-WORKER-{self.worker_id}] Initialized with skip_frames={skip_frames}, confidence={confidence}")

        W = None
        H = None

        # Main processing loop
        try:
            while True:
                # Read frame - EXACT LOGIC FROM ORIGINAL
                if is_camera:
                    # For camera: vs.read() returns frame directly
                    frame = vs.read()
                else:
                    # For video: cv2.VideoCapture returns (ret, frame)
                    ret, frame = vs.read()
                    if not ret:
                        break

                # Frame validation - ONLY for video (not camera)
                # EXACT from original: frame = frame[1] if args.get("input", False) else frame
                if not is_camera:
                    if frame is None:
                        break
                else:
                    if frame is None:
                        continue  # Camera might return None occasionally

                # Resize frame - EXACT from original line 140
                frame = imutils.resize(frame, width=500)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Get frame dimensions - EXACT from original line 144-145
                if W is None or H is None:
                    (H, W) = frame.shape[:2]

                # Initialize status and rectangles
                status = "Waiting"
                rects = []

                # Run object detection
                if totalFrames % skip_frames == 0:
                    status = "Detecting"
                    trackers = []

                    # Create blob and get detections
                    blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
                    self.net.setInput(blob)
                    detections = self.net.forward()
                    logger.debug(f"[DEBUG-WORKER-{self.worker_id}] Frame {totalFrames}: Starting detection, detections shape: {detections.shape}")

                    # Process detections
                    for i in np.arange(0, detections.shape[2]):
                        confidence_score = detections[0, 0, i, 2]

                        if confidence_score > confidence:
                            idx = int(detections[0, 0, i, 1])

                            if CLASSES[idx] != "person":
                                continue

                            # Get bounding box
                            box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                            
                            # Handle NaN and invalid values
                            if np.any(np.isnan(box)) or np.any(np.isinf(box)):
                                continue
                            
                            # Handle overflow
                            box = np.clip(box, -999999, 999999)
                            startX, startY, endX, endY = [int(c) for c in box]
                            
                            # Validate bounding box
                            if endX <= startX or endY <= startY or startX < 0 or startY < 0:
                                continue

                            # Create dlib tracker
                            tracker = dlib.correlation_tracker()
                            rect = dlib.rectangle(startX, startY, endX, endY)
                            tracker.start_track(rgb, rect)
                            trackers.append(tracker)

                else:
                    # Update trackers
                    status = "Tracking"
                    rects_updated = 0
                    for tracker in trackers:
                        tracker.update(rgb)
                        pos = tracker.get_position()

                        startX = int(pos.left())
                        startY = int(pos.top())
                        endX = int(pos.right())
                        endY = int(pos.bottom())

                        rects.append((startX, startY, endX, endY))
                        rects_updated += 1
                    
                    if rects_updated > 0 and totalFrames % 30 == 0:
                        logger.debug(f"[DEBUG-WORKER-{self.worker_id}] Frame {totalFrames}: Tracking {rects_updated} objects")

                # Draw center line
                cv2.line(frame, (0, H // 2), (W, H // 2), (0, 0, 0), 3)

                # Update centroid tracker
                objects = ct.update(rects)

                # Process tracked objects
                for (objectID, centroid) in objects.items():
                    to = trackableObjects.get(objectID, None)

                    if to is None:
                        to = TrackableObject(objectID, centroid)
                    else:
                        y = [c[1] for c in to.centroids]
                        direction = centroid[1] - np.mean(y)
                        to.centroids.append(centroid)

                        # Count object movement only once
                        if not to.counted:
                            # COUNTING LOGIC:
                            # - direction < 0: Object moving UP (negative y-change)
                            # - direction > 0: Object moving DOWN (positive y-change)
                            # - centroid[1] < H//2: Object is in TOP half of frame
                            # - centroid[1] > H//2: Object is in BOTTOM half of frame
                            
                            # CASE 1: Moving UP and above center line → Person going OUT
                            if direction < 0 and centroid[1] < H // 2:
                                totalUp += 1  # Increment OUT counter
                                date_time: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                move_out.append(totalUp)  # Record the OUT event
                                out_time.append(date_time)  # Record timestamp
                                to.counted = True  # Mark object as counted to prevent double-counting
                                logger.debug(f"[WORKER-{self.worker_id}] Frame {totalFrames}: OUT event for ObjectID={objectID}, direction={direction:.2f}, centroid_y={centroid[1]}, totalUp={totalUp}")

                            # CASE 2: Moving DOWN and below center line → Person going IN
                            elif direction > 0 and centroid[1] > H // 2:
                                totalDown += 1  # Increment IN counter
                                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                move_in.append(totalDown)  # Record the IN event
                                in_time.append(date_time)  # Record timestamp
                                # Check threshold for alert (line 281 in original)
                                if sum(total) >= threshold:
                                    logger.debug(f"[WORKER-{self.worker_id}] Threshold exceeded: {sum(total)} >= {threshold}")
                                to.counted = True  # Mark object as counted to prevent double-counting
                                # Compute total people inside (EXACT COPY FROM ORIGINAL LINE 292-293)
                                total = []
                                total.append(len(move_in) - len(move_out))
                                logger.debug(f"[WORKER-{self.worker_id}] Frame {totalFrames}: IN event for ObjectID={objectID}, direction={direction:.2f}, centroid_y={centroid[1]}, totalDown={totalDown}, current_total={total[0]}")

                    trackableObjects[objectID] = to

                    # Draw object info
                    text = "ID {}".format(objectID)
                    cx, cy = int(centroid[0]), int(centroid[1])
                    cv2.putText(frame, text, (cx - 10, cy - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)

                # Update FPS and frame count FIRST
                totalFrames += 1
                fps.update()

                # Calculate current count OUTSIDE the objects loop
                total_inside = len(move_in) - len(move_out)

                # Send result periodically
                if totalFrames % 10 == 0:
                    fps.stop()
                    current_fps = fps.fps()
                    fps.start()

                    self.send_result({
                        'worker_id': self.worker_id,
                        'task_id': task_id,
                        'camera_id': camera_id,
                        'video_id': video_id,
                        'fps': current_fps,
                        'total_in': totalDown,
                        'total_out': totalUp,
                        'current_count': total_inside,
                        'status': status,
                        'frame_count': totalFrames
                    })

        except Exception as e:
            logger.error(f"[WORKER-{self.worker_id}] Error in count_people: {e}", exc_info=True)

        finally:
            # Final statistics
            try:
                fps.stop()
                elapsed_time = fps.elapsed()
                avg_fps = fps.fps()
            except:
                elapsed_time = 0
                avg_fps = 0

            # Calculate final count
            final_count = len(move_in) - len(move_out)

            self.send_result({
                'worker_id': self.worker_id,
                'task_id': task_id,
                'camera_id': camera_id,
                'video_id': video_id,
                'fps': avg_fps,
                'total_in': totalDown,
                'total_out': totalUp,
                'current_count': final_count,
                'status': 'completed',
                'frame_count': totalFrames,
                'elapsed_time': elapsed_time
            })

            logger.info(f"[WORKER-{self.worker_id}] Finished task {task_id}")

    def send_result(self, result: Dict[str, Any]):
        """Send result to result queue."""
        try:
            self.result_queue.put(result, block=False)
        except Exception as e:
            # Try with blocking if non-blocking fails
            try:
                self.result_queue.put(result, block=True, timeout=2)
            except Exception as e2:
                logger.error(f"[WORKER-{self.worker_id}] Failed to send result: {e2}")

    def stop(self):
        """Stop the worker."""
        logger.info(f"[WORKER-{self.worker_id}] Stopping...")
        self.running = False

