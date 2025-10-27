"""
Final Production System - Complete with Real Gender/Age

Integrates all components:
- Accurate bounding boxes
- Tracking (CentroidTracker)
- Real gender/age analysis
- Professional overlay
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import time
from typing import Dict, Any, List, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from core.services.face_processing import FaceProcessor
from core.services.classification import PersonAnalysisService


class CompleteProductionSystem:
    """Final complete production system."""
    
    def __init__(self):
        """Initialize."""
        print("📦 Loading complete system...")
        
        # Person detector
        self.net = cv2.dnn.readNetFromCaffe(
            "detector/MobileNetSSD_deploy.prototxt",
            "detector/MobileNetSSD_deploy.caffemodel"
        )
        
        # Face processor
        self.face_processor = FaceProcessor()
        
        # Gender/Age service (real implementation)
        self.person_service = PersonAnalysisService()
        
        # Tracker
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects: Dict[int, TrackableObject] = {}
        
        # Analysis cache
        self.analysis_results: Dict[int, Dict[str, Any]] = {}
        
        print("✅ Complete system loaded\n")
    
    def detect_people_and_faces(self, frame: np.ndarray) -> Tuple[List, List]:
        """Detect both people and faces."""
        h, w = frame.shape[:2]
        
        # Detect people
        frame_resized = cv2.resize(frame, (500, 500))
        blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        people_boxes = []
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            idx = int(detections[0, 0, i, 1])
            
            if conf > 0.4 and idx == 15:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (px1, py1, px2, py2) = box.astype("int")
                
                # Store as (x, y, width, height) for tracking
                people_boxes.append({
                    'rect': (px1, py1, px2 - px1, py2 - py1),
                    'bbox': (px1, py1, px2, py2),
                    'confidence': float(conf)
                })
        
        # Detect faces in full frame
        face_results = self.face_processor.process_frame(frame)
        
        return people_boxes, face_results
    
    def match_face_to_person(self, person_box: Tuple, face_results: List) -> Tuple:
        """Match face to person using IoU."""
        px1, py1, px2, py2 = person_box
        
        best_face = None
        best_iou = 0
        
        for face_crop, face_info in face_results:
            fx, fy, fw, fh = face_info['box']
            fx2, fy2 = fx + fw, fy + fh
            
            # IoU
            inter_x1 = max(px1, fx)
            inter_y1 = max(py1, fy)
            inter_x2 = min(px2, fx2)
            inter_y2 = min(py2, fy2)
            
            if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                person_area = (px2 - px1) * (py2 - py1)
                face_area = fw * fh
                union_area = person_area + face_area - inter_area
                
                iou = inter_area / union_area if union_area > 0 else 0
                
                if iou > best_iou and iou > 0.05:
                    best_iou = iou
                    best_face = (face_crop, face_info, iou)
        
        return best_face
    
    def analyze_person_with_real_service(self, frame: np.ndarray, person_id: int, bbox: Tuple) -> Dict:
        """Analyze person using real gender/age service."""
        try:
            result = self.person_service.analyze_person(
                frame=frame,
                person_id=person_id,
                bbox=bbox,
                camera_id="shopping_korea"
            )
            
            if result and result.get('status') == 'success':
                return result
            else:
                # Return placeholder if analysis fails
                return {
                    'gender': 'unknown',
                    'age': -1,
                    'gender_confidence': 0.0,
                    'age_confidence': 0.0,
                    'status': 'failed',
                    'reason': result.get('reason', 'unknown')
                }
        except Exception as e:
            return {
                'gender': 'unknown',
                'age': -1,
                'gender_confidence': 0.0,
                'age_confidence': 0.0,
                'status': 'failed',
                'reason': str(e)
            }
    
    def process_frame(self, frame: np.ndarray, frame_idx: int) -> np.ndarray:
        """Process frame with all features."""
        annotated = frame.copy()
        h, w = frame.shape[:2]
        
        # Detect
        people_boxes, face_results = self.detect_people_and_faces(frame)
        
        # Update tracker
        rects = [person['rect'] for person in people_boxes]
        objects = self.ct.update(rects)
        
        # Process each tracked person
        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
            else:
                to.centroids.append(centroid)
            
            # Get person bbox
            if objectID < len(people_boxes):
                person = people_boxes[objectID]
                px1, py1, px2, py2 = person['bbox']
                
                # Try to match face
                face_match = self.match_face_to_person(person['bbox'], face_results)
                
                # Analyze if not cached
                if objectID not in self.analysis_results:
                    bbox_for_analysis = person['rect']
                    analysis = self.analyze_person_with_real_service(
                        frame, objectID, bbox_for_analysis
                    )
                    self.analysis_results[objectID] = analysis
                else:
                    analysis = self.analysis_results[objectID]
                
                # Draw body bbox (thick green)
                cv2.rectangle(annotated, (px1, py1), (px2, py2), (0, 255, 0), 3)
                
                # Draw trajectory
                if len(to.centroids) > 1:
                    for i in range(1, len(to.centroids)):
                        cv2.line(annotated,
                                tuple(to.centroids[i-1]),
                                tuple(to.centroids[i]),
                                (255, 255, 0), 2)
                
                # Draw centroid
                cv2.circle(annotated, centroid, 6, (0, 255, 0), -1)
                
                # Draw face bbox if matched
                if face_match:
                    face_crop, face_info, iou = face_match
                    fx, fy, fw, fh = face_info['box']
                    cv2.rectangle(annotated, (fx, fy), (fx+fw, fy+fh), (255, 0, 0), 2)
                
                # Draw info
                info_parts = [f"ID:{objectID}"]
                
                if analysis.get('gender') and analysis['gender'] != 'unknown':
                    info_parts.append(analysis['gender'].upper())
                    if analysis.get('gender_confidence', 0) > 0.5:
                        info_parts.append(f"{analysis['gender_confidence']:.0%}")
                
                if analysis.get('age') and analysis['age'] > 0:
                    info_parts.append(f"{analysis['age']}y")
                    if analysis.get('age_confidence', 0) > 0.5:
                        info_parts.append(f"{analysis['age_confidence']:.0%}")
                
                info_text = " ".join(info_parts)
                
                # Info background
                (tw, th), _ = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(annotated,
                             (px1, py1 - th - 15),
                             (px1 + tw + 15, py1),
                             (0, 0, 0), -1)
                
                # Text
                cv2.putText(annotated, info_text,
                           (px1 + 8, py1 - 8),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                           (255, 255, 255), 2, cv2.LINE_AA)
        
        # Stats
        stats_y = 30
        for stat in [f"Frame: {frame_idx}",
                     f"Tracking: {len(objects)}",
                     f"Total IDs: {len(self.trackableObjects)}",
                     f"Analyses: {len(self.analysis_results)}"]:
            cv2.rectangle(annotated, (10, stats_y-20), (280, stats_y+10), (0, 0, 0), -1)
            cv2.putText(annotated, stat, (15, stats_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (0, 255, 255), 2, cv2.LINE_AA)
            stats_y += 35
        
        return annotated
    
    def process_video(self, video_path: str, output_path: str, max_frames: int = 200):
        """Process video."""
        print(f"\n{'='*80}")
        print(f"🚀 COMPLETE PRODUCTION SYSTEM")
        print(f"{'='*80}\n")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        print(f"📹 {w}x{h}, {fps} FPS\n🎬 Processing...\n")
        
        start = time.time()
        frame_count = 0
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            annotated = self.process_frame(frame, frame_count)
            
            if frame_count % 20 == 0:
                elapsed = (time.time() - start) / (frame_count + 1) * 1000
                print(f"  Frame {frame_count}: {len(self.trackableObjects)} IDs, "
                      f"{len(self.analysis_results)} analyses, {elapsed:.0f}ms")
            
            out.write(annotated)
            frame_count += 1
        
        total = time.time() - start
        
        cap.release()
        out.release()
        
        # Save analysis results
        results_path = output_path.replace('.mp4', '_results.json')
        with open(results_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print(f"✅ COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Frames: {frame_count}")
        print(f"📊 Tracked: {len(self.trackableObjects)}")
        print(f"📊 Analyses: {len(self.analysis_results)}")
        print(f"📊 FPS: {frame_count/total:.1f}")
        print(f"📊 Time: {total:.1f}s")
        print(f"\n📹 Video: {output_path}")
        print(f"📄 Results: {results_path}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    system = CompleteProductionSystem()
    system.process_video(
        "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        "output/complete_production.mp4",
        max_frames=200
    )

