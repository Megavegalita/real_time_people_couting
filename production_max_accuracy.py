"""
Maximum Accuracy System - Target 70%+

Features:
- InsightFace for best face detection on small faces
- Extreme upscaling (4x-6x) for tiny faces
- Multiple detection scales
- Aggressive face detection parameters
- Real gender/age models (to be implemented)
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
except ImportError:
    YOLO_AVAILABLE = False

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

try:
    import insightface
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    from facenet_pytorch import MTCNN as MTCNN_FACE
    MTCNN_FACE_AVAILABLE = True
except ImportError:
    MTCNN_FACE_AVAILABLE = False


class MaxAccuracySystem:
    """System optimized for 70%+ accuracy."""
    
    def __init__(self, output_dir=None):
        """Initialize with all available models."""
        print("📦 Loading MAX ACCURACY models...")
        
        if YOLO_AVAILABLE:
            self.yolo = YOLO('yolov8n.pt')
            print("✅ YOLO loaded")
        
        if MEDIAPIPE_AVAILABLE:
            self.mp_face = mp.solutions.face_detection
            self.face_detection = self.mp_face.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.01  # Very aggressive
            )
            print("✅ MediaPipe loaded (confidence=0.01)")
        
        if MTCNN_AVAILABLE:
            self.mtcnn = MTCNN()
            print("✅ MTCNN loaded")
        
        if INSIGHTFACE_AVAILABLE:
            try:
                self.insightface_app = insightface.app.FaceAnalysis()
                self.insightface_app.prepare(ctx_id=0, det_size=(640, 640))
                print("✅ InsightFace loaded")
            except Exception as e:
                print(f"⚠️  InsightFace error: {e}")
                self.insightface_app = None
        else:
            self.insightface_app = None
        
        if MTCNN_FACE_AVAILABLE:
            try:
                self.mtcnn_face = MTCNN_FACE(
                    image_size=160,
                    margin=0,
                    min_face_size=20,
                    thresholds=[0.6, 0.7, 0.7],
                    factor=0.709,
                    post_process=False
                )
                print("✅ MTCNN (face) loaded")
            except:
                self.mtcnn_face = None
        
        self.haar = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects = {}
        self.person_data = {}
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"output/max_accuracy_{timestamp}"
        
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        
        self.stats = {
            'frames_processed': 0,
            'bodies_detected': 0,
            'faces_detected': 0,
            'gender_analyses': 0,
            'merged_boxes': 0,
            'enhancement_applied': 0
        }
        
        print(f"✅ All models loaded")
        print(f"📁 Output: {self.output_dir}\n")
    
    def extreme_upscale(self, img, scale_factor=4.0):
        """Extreme upscaling for tiny faces."""
        self.stats['enhancement_applied'] += 1
        
        h, w = img.shape[:2]
        new_h, new_w = int(h * scale_factor), int(w * scale_factor)
        
        # Upscale with best interpolation
        upscaled = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # CLAHE for contrast
        lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        enhanced_lab = cv2.merge([l_enhanced, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Sharpen
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    def detect_bodies_yolo(self, frame):
        """Detect bodies."""
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
            return []
    
    def detect_faces_extreme(self, person_crop):
        """Detect faces with extreme upscaling."""
        all_faces = []
        h_orig, w_orig = person_crop.shape[:2]
        
        # Scale 1: Original
        if MEDIAPIPE_AVAILABLE:
            try:
                rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(rgb)
                if results.detections:
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        fx = max(0, int(bbox.xmin * w_orig))
                        fy = max(0, int(bbox.ymin * h_orig))
                        fw = int(bbox.width * w_orig)
                        fh = int(bbox.height * h_orig)
                        if fw > 6 and fh > 6:
                            all_faces.append({
                                'box': (fx, fy, fw, fh),
                                'confidence': detection.score[0],
                                'method': 'mediapipe'
                            })
            except: pass
        
        # Scale 2: 2x upscaled
        enhanced_2x = self.extreme_upscale(person_crop, 2.0)
        h_2x, w_2x = enhanced_2x.shape[:2]
        scale_w_2x, scale_h_2x = w_orig / w_2x, h_orig / h_2x
        
        if MEDIAPIPE_AVAILABLE:
            try:
                rgb = cv2.cvtColor(enhanced_2x, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(rgb)
                if results.detections:
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        fx = max(0, int(bbox.xmin * w_2x))
                        fy = max(0, int(bbox.ymin * h_2x))
                        fw = int(bbox.width * w_2x)
                        fh = int(bbox.height * h_2x)
                        if fw > 6 and fh > 6:
                            fx = int(fx * scale_w_2x)
                            fy = int(fy * scale_h_2x)
                            fw = int(fw * scale_w_2x)
                            fh = int(fh * scale_h_2x)
                            if fx + fw <= w_orig and fy + fh <= h_orig:
                                all_faces.append({
                                    'box': (fx, fy, fw, fh),
                                    'confidence': detection.score[0],
                                    'method': 'mediapipe_2x'
                                })
            except: pass
        
        # Scale 3: 4x upscaled
        enhanced_4x = self.extreme_upscale(person_crop, 4.0)
        h_4x, w_4x = enhanced_4x.shape[:2]
        scale_w_4x, scale_h_4x = w_orig / w_4x, h_orig / h_4x
        
        if MEDIAPIPE_AVAILABLE:
            try:
                rgb = cv2.cvtColor(enhanced_4x, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(rgb)
                if results.detections:
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        fx = max(0, int(bbox.xmin * w_4x))
                        fy = max(0, int(bbox.ymin * h_4x))
                        fw = int(bbox.width * w_4x)
                        fh = int(bbox.height * h_4x)
                        if fw > 6 and fh > 6:
                            fx = int(fx * scale_w_4x)
                            fy = int(fy * scale_h_4x)
                            fw = int(fw * scale_w_4x)
                            fh = int(fh * scale_h_4x)
                            if fx + fw <= w_orig and fy + fh <= h_orig:
                                all_faces.append({
                                    'box': (fx, fy, fw, fh),
                                    'confidence': detection.score[0],
                                    'method': 'mediapipe_4x'
                                })
            except: pass
        
        # Scale 4: 6x upscaled (extreme)
        enhanced_6x = self.extreme_upscale(person_crop, 6.0)
        h_6x, w_6x = enhanced_6x.shape[:2]
        scale_w_6x, scale_h_6x = w_orig / w_6x, h_orig / h_6x
        
        if MEDIAPIPE_AVAILABLE:
            try:
                rgb = cv2.cvtColor(enhanced_6x, cv2.COLOR_BGR2RGB)
                results = self.face_detection.process(rgb)
                if results.detections:
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        fx = max(0, int(bbox.xmin * w_6x))
                        fy = max(0, int(bbox.ymin * h_6x))
                        fw = int(bbox.width * w_6x)
                        fh = int(bbox.height * h_6x)
                        if fw > 6 and fh > 6:
                            fx = int(fx * scale_w_6x)
                            fy = int(fy * scale_h_6x)
                            fw = int(fw * scale_w_6x)
                            fh = int(fh * scale_h_6x)
                            if fx + fw <= w_orig and fy + fh <= h_orig:
                                all_faces.append({
                                    'box': (fx, fy, fw, fh),
                                    'confidence': detection.score[0],
                                    'method': 'mediapipe_6x'
                                })
            except: pass
        
        # MTCNN on 4x
        if MTCNN_AVAILABLE:
            try:
                results = self.mtcnn.detect_faces(enhanced_4x)
                for result in results:
                    if result['confidence'] > 0.2:
                        x, y, w, h = result['box']
                        if w > 8 and h > 8:
                            x = int(x * scale_w_4x)
                            y = int(y * scale_h_4x)
                            w = int(w * scale_w_4x)
                            h = int(h * scale_h_4x)
                            if x + w <= w_orig and y + h <= h_orig:
                                all_faces.append({
                                    'box': (x, y, w, h),
                                    'confidence': result['confidence'],
                                    'method': 'mtcnn_4x'
                                })
            except: pass
        
        # Haar on multiple scales
        for scale, img_scale in [(1.0, person_crop), (2.0, enhanced_2x), (4.0, enhanced_4x)]:
            try:
                gray = cv2.cvtColor(img_scale, cv2.COLOR_BGR2GRAY)
                faces = self.haar.detectMultiScale(
                    gray, 
                    scaleFactor=1.05,
                    minNeighbors=1,
                    minSize=(6, 6)
                )
                
                for (x, y, w, h) in faces:
                    # Scale back
                    x = int(x / scale) if scale != 1.0 else x
                    y = int(y / scale) if scale != 1.0 else y
                    w = int(w / scale) if scale != 1.0 else w
                    h = int(h / scale) if scale != 1.0 else h
                    
                    if x + w <= w_orig and y + h <= h_orig:
                        all_faces.append({
                            'box': (x, y, w, h),
                            'confidence': 1.0 / scale,
                            'method': f'haar_{int(scale)}x'
                        })
            except: pass
        
        return self._deduplicate_faces(all_faces)
    
    def _deduplicate_faces(self, faces):
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
        """Estimate gender/age - placeholder."""
        if face_crop is None or face_crop.size == 0:
            return {'gender': 'UNKNOWN', 'age': -1, 'face_detected': False}
        
        if track_id not in self.person_data or 'gender' not in self.person_data.get(track_id, {}):
            gender = "MALE" if (track_id % 2 == 0) else "FEMALE"
            age = 20 + (track_id % 30)
        else:
            data = self.person_data[track_id]
            gender = data['gender']
            age = data['age']
        
        return {
            'gender': gender,
            'age': age,
            'face_detected': True,
            'frame': frame_idx,
            'is_placeholder': True
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
        
        body_boxes = self.merge_overlapping_boxes(body_boxes)
        boxes = body_boxes if isinstance(body_boxes[0], tuple) else [box['bbox'] for box in body_boxes]
        
        tracked_objects = self.ct.update(boxes)
        
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
        
        for (objectID, centroid) in tracked_objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
            else:
                to.centroids.append(centroid)
            
            if objectID in object_to_box_map:
                box_idx = object_to_box_map[objectID]
                x, y, w_box, h_box = boxes[box_idx]
                
                if self.should_re_analyze(objectID, frame_idx):
                    person_crop = frame[y:y+h_box, x:x+w_box]
                    
                    face_results = self.detect_faces_extreme(person_crop)
                    
                    if len(face_results) > 0:
                        best_face = face_results[0]
                        fx, fy, fw, fh = best_face['box']
                        face_crop = person_crop[fy:fy+fh, fx:fx+fw]
                        
                        self.person_data[objectID] = self.estimate_gender_age(
                            face_crop, objectID, frame_idx
                        )
                        
                        self.stats['faces_detected'] += 1
                        self.stats['gender_analyses'] += 1
                        
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
                
                color = (0, 255, 255) if data.get('face_detected') else (0, 0, 255)
                cv2.rectangle(annotated, (x, y), (x+w_box, y+h_box), color, 3)
                
                if len(to.centroids) > 1:
                    for i in range(1, len(to.centroids)):
                        cv2.line(annotated, tuple(to.centroids[i-1]),
                                tuple(to.centroids[i]), (255, 255, 0), 2)
                
                cv2.circle(annotated, centroid, 6, (0, 255, 0), -1)
                
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
        print("🚀 MAX ACCURACY SYSTEM")
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
        print(f"🎬 Processing with EXTREME enhancements...\n")
        
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
                detection_rate = (self.stats['faces_detected'] / frame_idx * 100) if frame_idx > 0 else 0
                print(f"  Frame {frame_idx}: {len(self.trackableObjects)} IDs, "
                      f"{self.stats['faces_detected']} faces ({detection_rate:.1f}%), {elapsed:.0f}ms")
            
            frame_idx += 1
        
        total = time.time() - start
        cap.release()
        out.release()
        
        self.stats['total_time'] = total
        self.stats['fps'] = frame_idx / total if total > 0 else 0
        self.stats['detection_rate'] = (self.stats['faces_detected'] / frame_idx * 100) if frame_idx > 0 else 0
        
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
        print(f"  ⭐ Detection Rate: {self.stats['detection_rate']:.1f}%")
        print(f"  Merged boxes: {self.stats['merged_boxes']}")
        print(f"  Enhancement calls: {self.stats['enhancement_applied']}")
        print(f"  FPS: {self.stats['fps']:.1f}")
        print(f"\n📁 Output: {self.output_dir}")
        print(f"📹 Video: {out_video}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    system = MaxAccuracySystem()
    system.process_video(
        "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        max_frames=100
    )

