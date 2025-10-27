"""
Debug Overlay Issue - Find why wrong gender/age is displayed

Issue: Shows "ID:1 MALE" when only 1 person visible (female)
Need to check bounding box alignment and overlay placement
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject


class DebugOverlay:
    """Debug overlay placement and person data."""
    
    def __init__(self):
        self.net = cv2.dnn.readNetFromCaffe(
            "detector/MobileNetSSD_deploy.prototxt",
            "detector/MobileNetSSD_deploy.caffemodel"
        )
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects = {}
        self.person_data = {}
    
    def estimate_from_body(self, person_crop):
        """Simple estimation."""
        if person_crop is None or person_crop.size == 0:
            return {'gender': 'UNKNOWN', 'age': -1, 'conf': 0.0}
        
        h, w = person_crop.shape[:2]
        aspect_ratio = w / h if h > 0 else 1
        
        print(f"      DEBUG: Crop size: {h}x{w}, aspect: {aspect_ratio:.2f}")
        
        if h > 250 and w > 120 and aspect_ratio > 0.6:
            gender = "MALE"
            age = np.random.randint(25, 50)
            conf = 0.7
        elif h > 200:
            if h > 220:
                gender = "MALE"
                age = np.random.randint(22, 45)
            else:
                gender = "FEMALE"
                age = np.random.randint(20, 40)
            conf = 0.6
        elif h > 150:
            gender = "FEMALE"
            age = np.random.randint(18, 35)
            conf = 0.65
        else:
            gender = "UNKNOWN"
            age = -1
            conf = 0.3
        
        print(f"      DEBUG: Estimate: {gender}, {age}")
        
        return {
            'gender': gender,
            'gender_confidence': conf,
            'age': age,
            'age_confidence': conf * 0.8
        }
    
    def debug_frame(self, frame, frame_idx):
        """Debug a single frame."""
        h, w = frame.shape[:2]
        annotated = frame.copy()
        
        # Detect
        frame_resized = cv2.resize(frame, (500, 500))
        blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        boxes = []
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            idx = int(detections[0, 0, i, 1])
            
            if conf > 0.4 and idx == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (px1, py1, px2, py2) = box.astype("int")
                boxes.append((px1, py1, px2 - px1, py2 - py1))
        
        print(f"\n    Frame {frame_idx}: {len(boxes)} people detected")
        
        # Update tracker
        objects = self.ct.update(boxes)
        
        print(f"    Tracked objects: {len(objects)}")
        print(f"    TrackableObjects: {len(self.trackableObjects)}")
        print(f"    Person data: {list(self.person_data.keys())}")
        
        for (objectID, centroid) in objects.items():
            print(f"      ObjectID: {objectID}, Centroid: {centroid}")
            
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
                print(f"        NEW trackable object created")
            else:
                to.centroids.append(centroid)
                print(f"        Existing, has {len(to.centroids)} points")
            
            # Get bbox
            if objectID < len(boxes):
                x, y, w_box, h_box = boxes[objectID]
                print(f"        Bbox: ({x}, {y}, {w_box}, {h_box})")
                
                # Analyze
                if objectID not in self.person_data:
                    crop = frame[y:y+h_box, x:x+w_box]
                    print(f"        Analyzing person {objectID}...")
                    self.person_data[objectID] = self.estimate_from_body(crop)
                
                data = self.person_data[objectID]
                print(f"        Data for ID {objectID}: {data['gender']}, {data['age']}")
                
                # Draw
                cv2.rectangle(annotated, (x, y), (x+w_box, y+h_box), (0, 255, 0), 3)
                
                if len(to.centroids) > 1:
                    for i in range(1, len(to.centroids)):
                        cv2.line(annotated, tuple(to.centroids[i-1]),
                                tuple(to.centroids[i]), (255, 255, 0), 2)
                
                cv2.circle(annotated, centroid, 6, (0, 255, 0), -1)
                
                # Info
                info = f"ID:{objectID}"
                if data['gender'] != 'UNKNOWN':
                    info += f" {data['gender']}"
                if data['age'] > 0:
                    info += f" {data['age']}y"
                
                print(f"        Drawing overlay: {info}")
                
                (tw, th), _ = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(annotated, (x, y-th-15), (x+tw+15, y), (0, 0, 0), -1)
                cv2.putText(annotated, info, (x+8, y-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                print(f"        WARNING: objectID {objectID} >= len(boxes) {len(boxes)}")
                print(f"        This means overlay might be drawing for wrong person!")
        
        # Stats
        stats = [f"Frame {frame_idx}",
                f"Tracking: {len(objects)}",
                f"Total: {len(self.trackableObjects)}"]
        
        y = 30
        for stat in stats:
            cv2.rectangle(annotated, (10, y-20), (250, y+10), (0, 0, 0), -1)
            cv2.putText(annotated, stat, (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 35
        
        return annotated


def debug_video():
    """Debug the video."""
    print("\n" + "="*80)
    print("🐛 DEBUGGING OVERLAY ISSUE")
    print("="*80 + "\n")
    
    debugger = DebugOverlay()
    
    video_path = "utils/data/tests/shopping_korea.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Cannot open video")
        return
    
    # Test first 50 frames
    frame_idx = 0
    
    while frame_idx < 50:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx == 13:  # Frame with issue
            print(f"\n{'='*60}")
            print(f"DEBUGGING FRAME {frame_idx}")
            print(f"{'='*60}")
            
            annotated = debugger.debug_frame(frame, frame_idx)
            
            # Save debug frame
            cv2.imwrite(f"output/debug_frame_{frame_idx}.jpg", annotated)
            print(f"\n✅ Debug frame saved: output/debug_frame_{frame_idx}.jpg")
            print(f"{'='*60}\n")
        
        frame_idx += 1
    
    cap.release()
    
    print("\n✅ Debug complete!\n")


if __name__ == "__main__":
    debug_video()

