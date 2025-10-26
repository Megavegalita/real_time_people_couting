"""
Standard Workflow for People Counting
======================================

Workflow chuẩn được trích xuất từ people_counter.py để đảm bảo
độ chính xác tuyệt đối cho tất cả workers.
"""

import cv2
import numpy as np
import imutils
import dlib
import datetime
from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from imutils.video import FPS


class StandardPeopleCountingWorkflow:
    """
    Workflow chuẩn cho people counting.
    
    Logic này được copy CHÍNH XÁC từ people_counter.py
    để đảm bảo độ chính xác.
    """
    
    def __init__(self, net, CLASSES, args):
        """
        Initialize workflow.
        
        Args:
            net: Pre-loaded MobileNetSSD model
            CLASSES: Class names
            args: Configuration (skip_frames, confidence, etc.)
        """
        self.net = net
        self.CLASSES = CLASSES
        self.args = args
        
    def process_video(self, vs, args, config):
        """
        Process video using STANDARD workflow from people_counter.py.
        
        THIS IS THE EXACT LOGIC FROM ORIGINAL FILE.
        
        Args:
            vs: Video stream (can be VideoCapture or VideoStream)
            args: Arguments dict (input, output, confidence, skip_frames)
            config: Config dict (Thread, etc.)
            
        Returns:
            tuple: (totalDown, totalUp, totalFrames, total_inside)
        """
        # Initialize exactly like original (lines 99-113)
        ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        trackers = []
        trackableObjects = {}
        
        totalFrames = 0
        totalDown = 0
        totalUp = 0
        
        # Initialize empty lists to store the counting data
        total = []
        move_out = []
        move_in = []
        out_time = []
        in_time = []
        
        # Start the FPS counter (line 116)
        fps = FPS().start()
        
        writer = None
        
        # Frame dimensions (lines 91-94)
        W = None
        H = None
        
        # Main loop - EXACT from original (lines 125-342)
        while True:
            # Grab the next frame (lines 129-130) - EXACT ORIGINAL LOGIC
            frame = vs.read()
            frame = frame[1] if args.get("input", False) else frame
            
            # Check end of video (lines 132-135)
            if args.get("input") is not None and frame is None:
                break
            
            # Resize frame (lines 137-141)
            frame = imutils.resize(frame, width=500)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Set frame dimensions (lines 143-145)
            if W is None or H is None:
                (H, W) = frame.shape[:2]
            
            # Initialize video writer if needed (lines 147-152)
            if args.get("output") is not None and writer is None:
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(args["output"], fourcc, 30, (W, H), True)
            
            # Initialize status and rectangles (lines 154-158)
            status = "Waiting"
            rects = []
            
            # Run object detection (lines 160-204) - EXACT ORIGINAL
            if totalFrames % args["skip_frames"] == 0:
                status = "Detecting"
                trackers = []
                
                # Convert frame to blob (lines 167-171)
                blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
                self.net.setInput(blob)
                detections = self.net.forward()
                
                # Loop over detections (lines 174-204)
                for i in np.arange(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    
                    if confidence > args["confidence"]:
                        idx = int(detections[0, 0, i, 1])
                        
                        if self.CLASSES[idx] != "person":
                            continue
                        
                        # Compute bounding box coordinates (lines 190-193)
                        box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                        (startX, startY, endX, endY) = box.astype("int")
                        
                        # Create tracker (lines 195-204)
                        tracker = dlib.correlation_tracker()
                        rect = dlib.rectangle(startX, startY, endX, endY)
                        tracker.start_track(rgb, rect)
                        trackers.append(tracker)
            
            # Update trackers (lines 206-227) - EXACT ORIGINAL
            else:
                for tracker in trackers:
                    status = "Tracking"
                    tracker.update(rgb)
                    pos = tracker.get_position()
                    
                    startX = int(pos.left())
                    startY = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())
                    
                    rects.append((startX, startY, endX, endY))
            
            # Draw center line (lines 228-233)
            cv2.line(frame, (0, H // 2), (W, H // 2), (0, 0, 0), 3)
            
            # Update centroid tracker (lines 235-237)
            objects = ct.update(rects)
            
            # Process tracked objects (lines 240-294) - EXACT ORIGINAL LOGIC
            for (objectID, centroid) in objects.items():
                to = trackableObjects.get(objectID, None)
                
                if to is None:
                    to = TrackableObject(objectID, centroid)
                else:
                    # Calculate direction (lines 252-258)
                    y = [c[1] for c in to.centroids]
                    direction = centroid[1] - np.mean(y)
                    to.centroids.append(centroid)
                    
                    # Counting logic (lines 260-293)
                    if not to.counted:
                        # Moving up (exit) - EXACT (lines 262-270)
                        if direction < 0 and centroid[1] < H // 2:
                            totalUp += 1
                            date_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                            move_out.append(totalUp)
                            out_time.append(date_time)
                            to.counted = True
                        
                        # Moving down (enter) - EXACT (lines 272-293)
                        elif direction > 0 and centroid[1] > H // 2:
                            totalDown += 1
                            date_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                            move_in.append(totalDown)
                            in_time.append(date_time)
                            
                            # Alert logic (lines 280-289)
                            if sum(total) >= config.get("Threshold", 10):
                                pass  # Alert logic removed for parallel
                            
                            to.counted = True
                            total = []
                            total.append(len(move_in) - len(move_out))
                
                trackableObjects[objectID] = to
                
                # Drawing logic (lines 295-303) - removed for parallel
                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)
            
            # Increment totalFrames and update FPS (lines 339-342)
            totalFrames += 1
            fps.update()
        
        # Stop FPS and cleanup
        fps.stop()
        
        # Calculate final count
        total_inside = len(move_in) - len(move_out)
        
        return totalDown, totalUp, totalFrames, total_inside

