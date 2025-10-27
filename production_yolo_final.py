"""
Production System - YOLO Final

Complete system with:
- YOLOv8 for body detection
- MediaPipe/MTCNN for face detection
- CentroidTracker (simple, reliable)
- Gender/age analysis
- Box merging
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import time
from datetime import datetime
import json
import os

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject

# YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    print("✅ YOLO available")
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  YOLO not available")

# Face detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except:
    MEDIAPIPE_AVAILABLE = False

try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
except:
    MTCNN_AVAILABLE = False


class YOLOFinalSystem:
    """Complete YOLO-based system."""
    
    def __init__(self, output_dir=None):
        """Initialize."""
        print("📦 Loading YOLO models...")
        
        if YOLO_AVAILABLE:
            self.yolo = YOLO('yolov8n.pt')
            print("✅ YOLO loaded")
        else:
            print("❌ YOLO not available")
            sys.exit(1)
        
        # Face detection
        if MEDIAPIPE_AVAILABLE:
            self.mp_face = mp.solutions.face_detection
            self.face_detection = self.mp_face.FaceDetection(
                model_selection=1, min_detection_confidence=0.1
            )
            print("✅ MediaPipe loaded")
        
        if MTCNN_AVAILABLE:
            self.mtcnn = MTCNN()
            print("✅ MTCNN loaded")
        
        self.haar = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects = {}
        self.person_data = {}
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"output/yolo_final_{timestamp}"
        
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        
        self.stats = {
            'frames_processed': 0,
            'bodies_detected': 0,
            'faces_detected': 0,
            'gender_analyses': 0,
            'merged_boxes': 0
        }
        
        print(f"✅ Models loaded")
        print(f"📁 Output: {self.output_dir}\n")
    
    def detect_bodies_yolo(self, frame):
        """Detect bodies with YOLO."""
        try:
            results = self.yolo(frame, classes=[0], conf=0.3, verbose=False)
            
            boxes = []
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    
                    boxes.append({
                        'bbox': (int(x1), int(y1), int(x2-x1), int(y2-y1)),
                        'confidence': float(conf)
                    })
            
            return boxes
        except Exception as e:
            print(f"⚠️  YOLO error: {e}")
            return []
    
    def detect_faces_multi_method(self, person_crop):
        """Detect faces with all methods."""
        all_faces = []
        
        if MEDIAPIPE_AVAILABLE:
            try:
                rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(rgb)
                
                if results.detections:
                    h, w = person_crop.shape[:2]
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        fx = max(0, int(bbox.xmin * w))
                        fy = max(0, int(bbox.ymin * h))
                        fw = int(bbox.width * w)
                        fh = int(bbox.height * h)
                        
                        if fw > 10 and fh > 10:
                            all_faces.append({
                                'box': (fx, fy, fw, fh),
                                'confidence': detection.score[0],
                                'method': 'mediapipe'
                            })
            except: pass
        
        if MTCNN_AVAILABLE:
            try:
                results = self.mtcnn.detect_faces(person_crop)
                for result in results:
                    if result['confidence'] > 0.5:
                        x, y, w, h = result['box']
                        if w > 10 and h > 10:
                            all_faces.append({
                                'box': (x, y, w, h),
                                'confidence': result['confidence'],
                                'method': 'mtcnn'
                            })
            except: pass
        
        try:
            gray = cv2.cvtColor(person_crop, cv2.COLOR_BGR2GRAY)
            faces = self.haar.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(10, 10))
            for (x, y, w, h) in faces:
                all_faces.append({
                    'box': (x, y, w, h),
                    'confidence': 1.0,
                    'method': 'haar'
                })
        except: pass
        
        return self._deduplicate(all_faces)
    
    def _deduplicate(self, faces):
        """Remove duplicates."""
        if not faces:
            return []
        
        faces.sort(key=lambda x: x['confidence'], reverse=True)
        unique = []
        
        for face in faces:
            fx, fy, fw, fh = face['box']
            overlaps = False
            
            for existing in unique:
                ex, ey, ew, eh = existing['box']
                x1, y1 = max(fx, ex), max(fy, ey)
                x2, y2 = min(fx + fw, ex + ew), min(fy + fh, ey + eh)
                
                if x2 > x1 and y2 > y1:
                    inter = (x2 - x1) * (y2 - y1)
                    union = fw * fh + ew * eh - inter
                    if inter / union > 0.3:
                        overlaps = True
                        break
            
            if not overlaps:
                unique.append(face)
        
        return unique
    
    def merge_overlapping_boxes(self, boxes):
        """Merge overlapping boxes."""
        if not boxes or len(boxes) == 1:
            return boxes
        
        merged = []
        used = set()
        
        for i, box1 in enumerate(boxes):
            if i in used:
                continue
            
            x1, y1, w1, h1 = box1['bbox']
            merged_box = [x1, y1, w1, h1]
            
            for j, box2 in enumerate(boxes):
                if i >= j or j in used:
                    continue
                
                x2, y2, w2, h2 = box2['bbox']
                
                x1_i = max(x1, x2)
                y1_i = max(y1, y2)
                x2_i = min(x1 + w1, x2 + w2)
                y2_i = min(y1 + h1, y2 + h2)
                
                if x2_i > x1_i and y2_i > y1_i:
                    inter = (x2_i - x1_i) * (y2_i - y1_i)
                    union = w1 * h1 + w2 * h2 - inter
                    iou = inter / union if union > 0 else 0
                    
                    if iou > 0.3:
                        new_x = min(x1, x2)
                        new_y = min(y1, y2)
                        new_w = max(x1 + w1, x2 + w2) - new_x
                        new_h = max(y1 + h1, y2 + h2) - new_y
                        
                        merged_box = [new_x, new_y, new_w, new_h]
                        used.add(j)
                        self.stats['merged_boxes'] += 1
                        break
            
            merged.append(tuple(merged_box))
        
        return merged
    
    def estimate_gender_age(self, face_crop, track_id, frame_idx):
        """Estimate gender/age."""
        if face_crop is None or face_crop.size == 0:
            return {'gender': 'UNKNOWN', 'age': -1, 'face_detected': False}
        
        # FIX: Do NOT use hash-based gender (completely wrong!)
        # TODO: Replace with actual gender classifier or visual heuristics
        # For now: Use track_id for consistency but acknowledge it's not real
        
        # Store first-time assignment based on track_id for consistency
        if track_id not in self.person_data or 'gender' not in self.person_data.get(track_id, {}):
            # Assign based on track_id modulo for consistency
            # This is NOT real gender detection, just for demo
            gender_id = track_id % 2
            gender = "MALE" if gender_id == 0 else "FEMALE"
            age = 20 + (track_id % 30)
            
            # Log that this is placeholder
            print(f"⚠️  Warning: Gender assigned to track_id {track_id} is PLACEHOLDER, not real detection")
        
        return {
            'gender': gender if 'gender' in locals() else 'UNKNOWN',
            'age': age if 'age' in locals() else -1,
            'face_detected': True,
            'frame': frame_idx,
            'is_placeholder': True  # Flag that this is not real detection
        }
    
    def should_re_analyze(self, track_id, frame_idx):
        """Re-analysis check."""
        if track_id not in self.person_data:
            return True
        last_frame = self.person_data[track_id].get('frame', 0)
        if frame_idx - last_frame > 30:
            return True
        if not self.person_data[track_id].get('face_detected', False):
            return True
        return False
    
    def process_frame(self, frame, frame_idx):
        """Process frame."""
        h, w = frame.shape[:2]
        annotated = frame.copy()
        
        # YOLO body detection
        body_boxes = self.detect_bodies_yolo(frame)
        self.stats['bodies_detected'] += len(body_boxes)
        
        if not body_boxes:
            return annotated
        
        # Merge overlapping
        body_boxes = self.merge_overlapping_boxes(body_boxes)
        
        # Prepare for tracking (box is now tuple from merge)
        boxes = body_boxes if isinstance(body_boxes[0], tuple) else [box['bbox'] for box in body_boxes]
        
        # Track with CentroidTracker
        tracked_objects = self.ct.update(boxes)
        
        # Create mapping: objectID -> box index
        if len(boxes) > 0 and len(tracked_objects) > 0:
            distance_matrix = np.zeros((len(tracked_objects), len(boxes)))
            object_list = list(tracked_objects.keys())
            
            for i, (objectID, centroid) in enumerate(tracked_objects.items()):
                for j, box in enumerate(boxes):
                    x, y, w_box, h_box = box
                    box_center = (x + w_box // 2, y + h_box // 2)
                    distance_matrix[i, j] = np.sqrt(
                        (centroid[0] - box_center[0])**2 + 
                        (centroid[1] - box_center[1])**2
                    )
            
            object_to_box_map = {}
            used_boxes = set()
            
            for object_idx, objectID in enumerate(object_list):
                best_box_idx = None
                best_distance = float('inf')
                
                for box_idx in range(len(boxes)):
                    if box_idx not in used_boxes:
                        dist = distance_matrix[object_idx, box_idx]
                        if dist < best_distance:
                            best_distance = dist
                            best_box_idx = box_idx
                
                if best_box_idx is not None:
                    object_to_box_map[objectID] = best_box_idx
                    used_boxes.add(best_box_idx)
        else:
            object_to_box_map = {}
        
        # Process each tracked object
        for (objectID, centroid) in tracked_objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
            else:
                to.centroids.append(centroid)
            
            # Find corresponding box - FIX: Use map
            if objectID in object_to_box_map:
                box_idx = object_to_box_map[objectID]
                x, y, w_box, h_box = boxes[box_idx]
                
                # Face detection and analysis
                if self.should_re_analyze(objectID, frame_idx):
                    person_crop = frame[y:y+h_box, x:x+w_box]
                    
                    face_results = self.detect_faces_multi_method(person_crop)
                    
                    if len(face_results) > 0:
                        best_face = face_results[0]
                        fx, fy, fw, fh = best_face['box']
                        face_crop = person_crop[fy:fy+fh, fx:fx+fw]
                        
                        self.person_data[objectID] = self.estimate_gender_age(
                            face_crop, objectID, frame_idx
                        )
                        
                        self.stats['faces_detected'] += 1
                        self.stats['gender_analyses'] += 1
                        
                        # Draw face bbox
                        cv2.rectangle(annotated, 
                                     (x + fx, y + fy),
                                     (x + fx + fw, y + fy + fh),
                                     (255, 0, 0), 2)
                    else:
                        self.person_data[objectID] = {
                            'gender': 'UNKNOWN',
                            'age': -1,
                            'face_detected': False,
                            'frame': frame_idx
                        }
                
                data = self.person_data.get(objectID, {})
                
                # Draw person bbox
                color = (0, 255, 255) if data.get('face_detected') else (0, 0, 255)
                cv2.rectangle(annotated, (x, y), (x+w_box, y+h_box), color, 3)
                
                # Trajectory
                if len(to.centroids) > 1:
                    for i in range(1, len(to.centroids)):
                        cv2.line(annotated, tuple(to.centroids[i-1]),
                                tuple(to.centroids[i]), (255, 255, 0), 2)
                
                cv2.circle(annotated, centroid, 6, (0, 255, 0), -1)
                
                # Info
                info = f"ID:{objectID}"
                if data.get('face_detected'):
                    info += f" {data['gender']}"
                    if data.get('age', -1) > 0:
                        info += f" {data['age']}y"
                else:
                    info += " (no face)"
                
                (tw, th), _ = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(annotated, (x, y-th-15), (x+tw+15, y), (0, 0, 0), -1)
                cv2.putText(annotated, info, (x+8, y-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Stats
        stats = [
            f"Frame {frame_idx}",
            f"Detected: {len(boxes)}",
            f"Tracking: {len(tracked_objects)}",
            f"Faces: {self.stats['faces_detected']}"
        ]
        
        y = 30
        for stat in stats:
            cv2.rectangle(annotated, (10, y-20), (280, y+10), (0, 0, 0), -1)
            cv2.putText(annotated, stat, (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 35
        
        cv2.imwrite(f"{self.output_dir}/frame_{frame_idx:05d}.jpg", annotated)
        self.stats['frames_processed'] += 1
        
        return annotated
    
    def process_video(self, video_path: str, max_frames: int = 100):
        """Process video."""
        print("\n" + "="*80)
        print("🚀 YOLO FINAL SYSTEM")
        print("="*80 + "\n")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = f"{self.output_dir}/output.mp4"
        out = cv2.VideoWriter(out_video, fourcc, fps, (w, h))
        
        print(f"📹 {w}x{h} @ {fps} FPS\n")
        print(f"🎬 Processing...\n")
        
        start = time.time()
        frame_idx = 0
        
        while frame_idx < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            annotated = self.process_frame(frame, frame_idx)
            out.write(annotated)
            
            if frame_idx % 10 == 0:
                elapsed = (time.time() - start) / (frame_idx + 1) * 1000
                print(f"  Frame {frame_idx}: {len(self.trackableObjects)} IDs, "
                      f"{self.stats['faces_detected']} faces, {elapsed:.0f}ms")
            
            frame_idx += 1
        
        total = time.time() - start
        cap.release()
        out.release()
        
        self.stats['total_time'] = total
        self.stats['fps'] = frame_idx / total if total > 0 else 0
        
        with open(f"{self.output_dir}/stats.json", 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"\n{'='*80}")
        print("✅ COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Results:")
        print(f"  Frames: {frame_idx}")
        print(f"  Tracked IDs: {len(self.trackableObjects)}")
        print(f"  Bodies: {self.stats['bodies_detected']}")
        print(f"  Faces: {self.stats['faces_detected']}")
        print(f"  Gender analyses: {self.stats['gender_analyses']}")
        print(f"  Merged boxes: {self.stats['merged_boxes']}")
        print(f"  Detection rate: {self.stats['faces_detected']/frame_idx*100:.1f}%")
        print(f"  FPS: {self.stats['fps']:.1f}")
        print(f"\n📁 Output: {self.output_dir}")
        print(f"📹 Video: {out_video}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    system = YOLOFinalSystem()
    system.process_video(
        "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        max_frames=100
    )

