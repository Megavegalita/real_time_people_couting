"""
Optimized Workflow V2 - Better Accuracy

Improved matching algorithm for higher match rate.
"""

import cv2
import numpy as np
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from core.services.face_processing import FaceProcessor


class OptimizedAnalysisV2:
    """V2 with improved matching accuracy."""
    
    def __init__(self):
        """Initialize."""
        print("📦 Loading models...")
        
        prototxt = "detector/MobileNetSSD_deploy.prototxt"
        model = "detector/MobileNetSSD_deploy.caffemodel"
        
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.face_processor = FaceProcessor()
        
        print("✅ Models loaded\n")
    
    def match_faces_v2(self, people_boxes, face_results):
        """
        Improved matching with IoU (Intersection over Union).
        
        Args:
            people_boxes: List of (x1, y1, x2, y2)
            face_results: List of (face_crop, face_info)
        
        Returns:
            List of (person_idx, face_idx, iou_score)
        """
        matches = []
        
        for idx, person_box in enumerate(people_boxes):
            px1, py1, px2, py2 = person_box
            person_area = (px2 - px1) * (py2 - py1)
            
            best_match = None
            best_iou = 0
            
            for face_idx, (face_crop, face_info) in enumerate(face_results):
                fx, fy, fw, fh = face_info['box']
                
                # Calculate IoU
                fx2 = fx + fw
                fy2 = fy + fh
                
                inter_x1 = max(px1, fx)
                inter_y1 = max(py1, fy)
                inter_x2 = min(px2, fx2)
                inter_y2 = min(py2, fy2)
                
                if inter_x2 > inter_x1 and inter_y2 > inter_y1:
                    inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                    face_area = fw * fh
                    union_area = person_area + face_area - inter_area
                    
                    iou = inter_area / union_area if union_area > 0 else 0
                    
                    if iou > best_iou and iou > 0.1:  # Minimum threshold
                        best_iou = iou
                        best_match = (idx, face_idx, iou)
            
            if best_match:
                matches.append(best_match)
        
        # Remove duplicate face matches
        seen_faces = set()
        unique_matches = []
        for match in matches:
            person_idx, face_idx, iou = match
            if face_idx not in seen_faces:
                seen_faces.add(face_idx)
                unique_matches.append(match)
        
        return unique_matches
    
    def process_video_v2(self, video_path, output_path, max_frames=200):
        """Process with improved matching."""
        print(f"\n{'='*80}")
        print(f"🚀 OPTIMIZED ANALYSIS V2")
        print(f"{'='*80}\n")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        stats = {'people': 0, 'faces': 0, 'matches': 0, 'times': []}
        
        print("🎬 Processing V2...\n")
        start = time.time()
        frame_count = 0
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_start = time.time()
            
            # Detect faces
            face_results = self.face_processor.process_frame(frame)
            stats['faces'] += len(face_results)
            
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
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (px1, py1, px2, py2) = box.astype("int")
                    people_boxes.append((px1, py1, px2, py2))
                    stats['people'] += 1
            
            # Improved matching
            matches = self.match_faces_v2(people_boxes, face_results)
            stats['matches'] += len(matches)
            
            # Draw
            for px1, py1, px2, py2 in people_boxes:
                cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 255, 0), 2)
            
            for face_crop, face_info in face_results:
                fx, fy, fw, fh = face_info['box']
                cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (255, 0, 0), 2)
            
            for person_idx, face_idx, iou in matches:
                px1, py1, px2, py2 = people_boxes[person_idx]
                fx, fy, fw, fh = face_results[face_idx][1]['box']
                
                cv2.line(frame, 
                         (px1 + (px2-px1)//2, py1 + (py2-py1)//2),
                         (fx + fw//2, fy + fh//2),
                         (0, 255, 255), 3)
                
                cv2.putText(frame, f"IoU:{iou:.2f}", 
                           (fx, fy-5), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 255), 2)
            
            cv2.putText(frame, f"F:{frame_count} P:{len(people_boxes)} "
                           f"F:{len(face_results)} M:{len(matches)}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (255, 255, 255), 2)
            
            stats['times'].append(time.time() - frame_start)
            
            if frame_count % 20 == 0:
                elapsed = (time.time() - frame_start) * 1000
                print(f"  Frame {frame_count}: {len(people_boxes)} people, "
                      f"{len(face_results)} faces, {len(matches)} matches, "
                      f"{elapsed:.0f}ms")
            
            out.write(frame)
            frame_count += 1
        
        total = time.time() - start
        avg_time = np.mean(stats['times']) * 1000
        avg_fps = frame_count / total
        
        print(f"\n{'='*80}")
        print(f"✅ V2 COMPLETE")
        print(f"{'='*80}")
        print(f"📊 RESULTS:")
        print(f"  - Frames: {frame_count}")
        print(f"  - People: {stats['people']}")
        print(f"  - Faces: {stats['faces']}")
        print(f"  - Matches: {stats['matches']}")
        print(f"  - Match rate: {stats['matches']/stats['people']*100:.1f}%")
        print(f"  - Performance: {avg_fps:.1f} FPS")
        print(f"  - Avg time: {avg_time:.0f}ms")
        print(f"\n📹 Output: {output_path}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    analyzer = OptimizedAnalysisV2()
    analyzer.process_video_v2(
        "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        "output/optimized_v2.mp4",
        200
    )

