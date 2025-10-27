"""
Final Complete Analysis with Face Matching

Detects faces in full frame, matches to person bboxes, then analyzes.
"""

import cv2
import numpy as np
from pathlib import Path
import sys
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from core.services.face_processing import FaceProcessor


class ImprovedAnalysis:
    """Improved analysis with full-frame face detection."""
    
    def __init__(self):
        """Initialize."""
        from pathlib import Path
        prototxt = "detector/MobileNetSSD_deploy.prototxt"
        model = "detector/MobileNetSSD_deploy.caffemodel"
        
        print("📦 Loading models...")
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.face_processor = FaceProcessor()
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects: Dict[int, TrackableObject] = {}
        
        print("✅ Models loaded\n")
    
    def match_faces_to_persons(self, frame, people_boxes, face_results):
        """Match detected faces to person bounding boxes."""
        matches = []
        
        for person_box in people_boxes:
            px, py, pex, pey = person_box
            
            for face_crop, face_info in face_results:
                fx, fy, fw, fh = face_info['box']
                
                # Check if face is within person bbox
                tolerance = 100
                if (px - tolerance <= fx <= pex + tolerance and
                    py - tolerance <= fy <= pey + tolerance):
                    matches.append({
                        'person_box': person_box,
                        'face_crop': face_crop,
                        'face_info': face_info
                    })
                    break
        
        return matches
    
    def process_video(self, video_path, output_path, max_frames=200):
        """Process video with improved analysis."""
        print(f"\n{'='*80}")
        print(f"🚀 IMPROVED ANALYSIS - Shopping Korea")
        print(f"{'='*80}\n")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Cannot open: {video_path}")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"📹 Resolution: {width}x{height}\n")
        print("🎬 Processing...\n")
        
        frame_count = 0
        stats = {
            'people': 0,
            'faces': 0,
            'matches': 0,
            'people_with_faces': 0
        }
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect faces in full frame
            face_results = self.face_processor.process_frame(frame)
            stats['faces'] += len(face_results)
            
            # Detect people
            frame_resized = cv2.resize(frame, (500, 500))
            blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
            self.net.setInput(blob)
            detections = self.net.forward()
            
            people_boxes = []
            
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                idx = int(detections[0, 0, i, 1])
                
                if confidence > 0.4 and idx == 15:
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (startX, startY, endX, endY) = box.astype("int")
                    people_boxes.append((startX, startY, endX, endY))
                    stats['people'] += 1
            
            # Match faces to people
            matches = self.match_faces_to_persons(frame, people_boxes, face_results)
            stats['matches'] += len(matches)
            stats['people_with_faces'] += len(matches)
            
            # Draw
            # Draw person boxes
            for px, py, pex, pey in people_boxes:
                cv2.rectangle(frame, (px, py), (pex, pey), (0, 255, 0), 2)
            
            # Draw faces
            for face_crop, face_info in face_results:
                fx, fy, fw, fh = face_info['box']
                cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (255, 0, 0), 2)
            
            # Draw matches
            for match in matches:
                px, py, pex, pey = match['person_box']
                cv2.line(frame, 
                        (px + (pex-px)//2, py), 
                        (px + (pex-px)//2, pey),
                        (0, 255, 255), 2)
            
            # Stats
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"People: {len(people_boxes)}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces: {len(face_results)}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Matches: {len(matches)}", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if frame_count % 20 == 0:
                print(f"  Frame {frame_count}: {len(people_boxes)} people, {len(face_results)} faces, {len(matches)} matches")
            
            out.write(frame)
        
        cap.release()
        out.release()
        
        print(f"\n{'='*80}")
        print(f"✅ COMPLETE")
        print(f"{'='*80}")
        print(f"📊 RESULTS:")
        print(f"  - Frames: {frame_count}")
        print(f"  - People: {stats['people']}")
        print(f"  - Faces: {stats['faces']}")
        print(f"  - Matches: {stats['matches']}")
        print(f"  - People with faces: {stats['people_with_faces']}")
        print(f"  - Match rate: {stats['matches']/stats['people']*100:.1f}%")
        print(f"\n📹 Output: {output_path}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    analyzer = ImprovedAnalysis()
    analyzer.process_video(
        video_path="/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        output_path="output/final_improved_analysis.mp4",
        max_frames=200
    )

