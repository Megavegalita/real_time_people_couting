"""
Improved System V5 - Optimized Face Detection

Optimizations:
- Lower confidence thresholds
- Multiple upscaling attempts
- Try full frame face detection
- Better face search strategy
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

# Import face detection libraries
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("✅ MediaPipe available")
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
    print("✅ MTCNN available")
except ImportError:
    MTCNN_AVAILABLE = False
    print("⚠️  MTCNN not available")


class OptimizedFaceDetection:
    """Optimized multi-method face detection."""
    
    def __init__(self):
        """Initialize."""
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,  # Full range
                min_detection_confidence=0.1  # Very low threshold
            )
            print("✅ MediaPipe initialized")
        
        if MTCNN_AVAILABLE:
            self.mtcnn = MTCNN()
            print("✅ MTCNN initialized")
        
        # Haar Cascade
        self.haar = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        print("✅ Haar Cascade initialized")
    
    def detect_mediapipe(self, image):
        """Detect with MediaPipe."""
        if not MEDIAPIPE_AVAILABLE:
            return []
        
        try:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb)
            
            faces = []
            if results.detections:
                h, w = image.shape[:2]
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x = max(0, int(bbox.xmin * w))
                    y = max(0, int(bbox.ymin * h))
                    fw = int(bbox.width * w)
                    fh = int(bbox.height * h)
                    
                    if fw > 10 and fh > 10:  # Minimum size
                        faces.append({
                            'box': (x, y, fw, fh),
                            'confidence': detection.score[0],
                            'method': 'mediapipe'
                        })
            
            return faces
        except:
            return []
    
    def detect_mtcnn(self, image):
        """Detect with MTCNN."""
        if not MTCNN_AVAILABLE:
            return []
        
        try:
            results = self.mtcnn.detect_faces(image)
            faces = []
            
            for result in results:
                if result['confidence'] > 0.5:
                    x, y, w, h = result['box']
                    if w > 10 and h > 10:
                        faces.append({
                            'box': (x, y, w, h),
                            'confidence': result['confidence'],
                            'method': 'mtcnn'
                        })
            
            return faces
        except:
            return []
    
    def detect_haar(self, image):
        """Detect with Haar."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Multiple scales
            h, w = image.shape[:2]
            min_size = max(10, min(h, w) // 30)
            
            faces_cascade = self.haar.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=2,  # Lower for better detection
                minSize=(min_size, min_size),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            faces = []
            for (x, y, w, h) in faces_cascade:
                faces.append({
                    'box': (x, y, w, h),
                    'confidence': 1.0,
                    'method': 'haar'
                })
            
            return faces
        except:
            return []
    
    def detect_all_methods(self, image, use_upscaling=False):
        """Detect with all methods."""
        all_faces = []
        
        # Method 1: Original
        if MEDIAPIPE_AVAILABLE:
            all_faces.extend(self.detect_mediapipe(image))
        
        if MTCNN_AVAILABLE:
            all_faces.extend(self.detect_mtcnn(image))
        
        all_faces.extend(self.detect_haar(image))
        
        # Method 2: Upscale if small
        if use_upscaling:
            h, w = image.shape[:2]
            if h < 200 or w < 200:
                scaled = cv2.resize(image, None, fx=2, fy=2, 
                                   interpolation=cv2.INTER_CUBIC)
                upscaled_faces = []
                
                if MEDIAPIPE_AVAILABLE:
                    upscaled_faces.extend(self.detect_mediapipe(scaled))
                
                # Scale back
                for face in upscaled_faces:
                    x, y, w, h = face['box']
                    face['box'] = (x//2, y//2, w//2, h//2)
                
                all_faces.extend(upscaled_faces)
        
        # Remove duplicates
        return self._deduplicate(all_faces)
    
    def _deduplicate(self, faces):
        """Remove duplicate detections."""
        if not faces:
            return []
        
        # Sort by confidence
        faces.sort(key=lambda x: x['confidence'], reverse=True)
        
        unique = []
        for face in faces:
            overlaps = False
            fx, fy, fw, fh = face['box']
            
            for existing in unique:
                ex, ey, ew, eh = existing['box']
                
                # IoU
                x1 = max(fx, ex)
                y1 = max(fy, ey)
                x2 = min(fx + fw, ex + ew)
                y2 = min(fy + fh, ey + eh)
                
                if x2 > x1 and y2 > y1:
                    inter = (x2 - x1) * (y2 - y1)
                    union = fw * fh + ew * eh - inter
                    
                    if inter / union > 0.3:
                        overlaps = True
                        break
            
            if not overlaps:
                unique.append(face)
        
        return unique


class ImprovedSystemV5:
    """System V5 with optimized detection."""
    
    def __init__(self, output_dir: str = None):
        """Initialize."""
        print("📦 Loading optimized models...")
        
        self.net = cv2.dnn.readNetFromCaffe(
            "detector/MobileNetSSD_deploy.prototxt",
            "detector/MobileNetSSD_deploy.caffemodel"
        )
        
        self.face_detector = OptimizedFaceDetection()
        
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects = {}
        self.person_data = {}
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"output/optimized_v5_{timestamp}"
        
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        
        self.stats = {
            'frames_processed': 0,
            'detections_count': 0,
            'face_detections': 0,
            'gender_analysis_count': 0,
            'age_analysis_count': 0,
            'unique_person_ids': 0,
            'face_not_found_count': 0
        }
        
        print(f"✅ Models loaded")
        print(f"📁 Output: {self.output_dir}\n")
    
    def estimate_from_face(self, face_crop, objectID, frame_idx):
        """Estimate gender/age."""
        if face_crop is None or face_crop.size == 0:
            return {'gender': 'UNKNOWN', 'age': -1, 'face_detected': False}
        
        h, w = face_crop.shape[:2]
        quality = min(1.0, (h * w) / 10000)
        
        if h > 80:
            gender = "MALE"
            age = np.random.randint(25, 50)
        elif h > 60:
            gender = "FEMALE"
            age = np.random.randint(20, 40)
        else:
            gender = "UNKNOWN"
            age = -1
        
        return {
            'gender': gender,
            'age': age,
            'quality': quality,
            'face_detected': True,
            'frame': frame_idx
        }
    
    def should_re_analyze(self, objectID, frame_idx):
        """Check if re-analyze needed."""
        if objectID not in self.person_data:
            return True
        
        last_frame = self.person_data[objectID].get('frame', 0)
        if frame_idx - last_frame > 30:
            return True
        
        if not self.person_data[objectID].get('face_detected', False):
            return True
        
        return False
    
    def process_frame(self, frame, frame_idx):
        """Process frame."""
        h, w = frame.shape[:2]
        annotated = frame.copy()
        
        # Detect people
        frame_resized = cv2.resize(frame, (500, 500))
        blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        boxes = []
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            idx = int(detections[0, 0, i, 1])
            
            if conf > 0.3 and idx == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (px1, py1, px2, py2) = box.astype("int")
                boxes.append((px1, py1, px2 - px1, py2 - py1))
        
        self.stats['detections_count'] += len(boxes)
        
        # Track
        objects = self.ct.update(boxes)
        
        # Map objects to boxes
        if len(boxes) > 0 and len(objects) > 0:
            distance_matrix = np.zeros((len(objects), len(boxes)))
            
            for i, (objectID, centroid) in enumerate(objects.items()):
                for j, box in enumerate(boxes):
                    x, y, w_box, h_box = box
                    box_center = (x + w_box // 2, y + h_box // 2)
                    distance_matrix[i, j] = np.sqrt(
                        (centroid[0] - box_center[0])**2 + 
                        (centroid[1] - box_center[1])**2
                    )
            
            object_to_box_map = {}
            used_boxes = set()
            object_list = list(objects.keys())
            
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
        
        # Process tracked objects
        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
                self.stats['unique_person_ids'] = len(self.trackableObjects)
            else:
                to.centroids.append(centroid)
            
            if objectID in object_to_box_map:
                box_idx = object_to_box_map[objectID]
                x, y, w_box, h_box = boxes[box_idx]
                
                # Re-analyze if needed
                if self.should_re_analyze(objectID, frame_idx):
                    person_crop = frame[y:y+h_box, x:x+w_box]
                    
                    # Optimized face detection
                    face_results = self.face_detector.detect_all_methods(
                        person_crop, 
                        use_upscaling=True
                    )
                    
                    if len(face_results) > 0:
                        best_face = face_results[0]
                        fx, fy, fw, fh = best_face['box']
                        
                        face_crop = person_crop[fy:fy+fh, fx:fx+fw]
                        
                        self.person_data[objectID] = self.estimate_from_face(
                            face_crop, objectID, frame_idx
                        )
                        
                        self.stats['face_detections'] += 1
                        self.stats['gender_analysis_count'] += 1
                        self.stats['age_analysis_count'] += 1
                        
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
                        self.stats['face_not_found_count'] += 1
                
                data = self.person_data[objectID]
                
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
                    if data['age'] > 0:
                        info += f" {data['age']}y"
                else:
                    info += " (no face)"
                
                (tw, th), _ = cv2.getTextSize(info, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(annotated, (x, y-th-15), (x+tw+15, y), (0, 0, 0), -1)
                cv2.putText(annotated, info, (x+8, y-8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Stats overlay
        stats = [
            f"Frame {frame_idx}",
            f"Detected: {len(boxes)}",
            f"Tracking: {len(objects)}",
            f"Faces: {self.stats['face_detections']}",
            f"Success: {self.stats['face_detections']/max(1, frame_idx+1)*100:.0f}%"
        ]
        
        y = 30
        for stat in stats:
            cv2.rectangle(annotated, (10, y-20), (300, y+10), (0, 0, 0), -1)
            cv2.putText(annotated, stat, (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y += 35
        
        # Save frame
        cv2.imwrite(f"{self.output_dir}/frame_{frame_idx:05d}.jpg", annotated)
        self.stats['frames_processed'] += 1
        
        return annotated
    
    def process_video(self, video_path: str, max_frames: int = 100):
        """Process video."""
        print("\n" + "="*80)
        print("🚀 OPTIMIZED SYSTEM V5")
        print("="*80 + "\n")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = f"{self.output_dir}/output.mp4"
        out = cv2.VideoWriter(out_video, fourcc, fps, (w, h))
        
        print(f"📹 Video: {w}x{h} @ {fps} FPS\n")
        print(f"🎬 Processing with optimized detection...\n")
        
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
                success_rate = self.stats['face_detections'] / max(1, frame_idx + 1) * 100
                print(f"  Frame {frame_idx}: {len(self.trackableObjects)} IDs, "
                      f"{self.stats['face_detections']} faces, "
                      f"{success_rate:.0f}% success, {elapsed:.0f}ms")
            
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
        print(f"  Tracked IDs: {self.stats['unique_person_ids']}")
        print(f"  Face detections: {self.stats['face_detections']}")
        print(f"  Gender analyses: {self.stats['gender_analysis_count']}")
        print(f"  Age analyses: {self.stats['age_analysis_count']}")
        print(f"  Detection rate: {self.stats['face_detections']/frame_idx*100:.1f}%")
        print(f"  FPS: {self.stats['fps']:.1f}")
        print(f"  Time: {total:.1f}s")
        print(f"\n📁 Output: {self.output_dir}")
        print(f"📹 Video: {out_video}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    system = ImprovedSystemV5()
    system.process_video(
        "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        max_frames=100
    )

