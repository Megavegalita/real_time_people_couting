"""
Optimize Workflow - Accuracy & Performance Enhancement

Analyzes current workflow and implements optimizations.
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


class OptimizedAnalysis:
    """Optimized analysis for better accuracy and performance."""
    
    def __init__(self):
        """Initialize with optimizations."""
        print("📦 Loading models...")
        
        from pathlib import Path
        prototxt = "detector/MobileNetSSD_deploy.prototxt"
        model = "detector/MobileNetSSD_deploy.caffemodel"
        
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        
        # Initialize with optimizations
        self.face_processor = FaceProcessor()
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects: dict = {}
        
        # Performance cache
        self.face_cache = {}
        self.frame_count = 0
        
        print("✅ Models loaded\n")
    
    def match_faces_to_persons_advanced(
        self, 
        frame, 
        people_boxes, 
        face_results,
        tolerance: int = 150
    ):
        """
        Advanced face-person matching with multiple strategies.
        
        Returns:
            List of (person_box, face_crop, match_confidence)
        """
        matches = []
        
        for px, py, pex, pey in people_boxes:
            person_center_x = px + (pex - px) // 2
            person_center_y = py + (pey - py) // 2
            person_area = (pex - px) * (pey - py)
            
            best_match = None
            best_score = 0
            
            for face_crop, face_info in face_results:
                fx, fy, fw, fh = face_info['box']
                face_center_x = fx + fw // 2
                face_center_y = fy + fh // 2
                
                # Strategy 1: Distance-based scoring
                distance = np.sqrt(
                    (face_center_x - person_center_x)**2 + 
                    (face_center_y - person_center_y)**2
                )
                distance_score = 1.0 / (1.0 + distance / 100)
                
                # Strategy 2: Overlap scoring
                overlap_x = max(0, min(pex, fx + fw) - max(px, fx))
                overlap_y = max(0, min(pey, fy + fh) - max(py, fy))
                overlap_area = overlap_x * overlap_y
                overlap_score = overlap_area / person_area
                
                # Strategy 3: Size scoring (face should be proportional)
                face_area = fw * fh
                size_ratio = min(face_area, person_area) / max(face_area, person_area)
                
                # Combined score
                total_score = (distance_score * 0.4 + 
                              overlap_score * 0.4 + 
                              size_ratio * 0.2)
                
                if total_score > best_score and total_score > 0.3:
                    best_score = total_score
                    best_match = (face_crop, face_info)
            
            if best_match:
                matches.append((people_boxes.index((px, py, pex, pey)), best_match[0], best_match[1], best_score))
        
        return matches
    
    def detect_faces_optimized(self, frame):
        """Optimized face detection with caching."""
        # Use cache for nearby frames
        cache_key = f"frame_{self.frame_count // 3}"  # Cache every 3 frames
        
        if cache_key in self.face_cache:
            return self.face_cache[cache_key]
        
        # Detect faces
        face_results = self.face_processor.process_frame(frame)
        
        # Cache result
        self.face_cache[cache_key] = face_results
        return face_results
    
    def process_video_optimized(self, video_path, output_path, max_frames=200):
        """Process video with optimizations."""
        print(f"\n{'='*80}")
        print(f"🚀 OPTIMIZED ANALYSIS")
        print(f"{'='*80}\n")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Statistics
        stats = {
            'people': 0,
            'faces': 0,
            'matches': 0,
            'avg_match_score': 0.0,
            'processing_times': []
        }
        
        print("🎬 Processing with optimizations...\n")
        
        start_time = time.time()
        
        while self.frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_start = time.time()
            
            # Detect faces with caching
            face_results = self.detect_faces_optimized(frame)
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
            
            # Advanced matching
            matches = self.match_faces_to_persons_advanced(frame, people_boxes, face_results)
            stats['matches'] += len(matches)
            
            if len(matches) > 0:
                avg_score = sum(m[3] for m in matches) / len(matches)
                stats['avg_match_score'] += avg_score
            
            # Draw
            # Person boxes
            for px, py, pex, pey in people_boxes:
                cv2.rectangle(frame, (px, py), (pex, pey), (0, 255, 0), 2)
            
            # Faces
            for face_crop, face_info in face_results:
                fx, fy, fw, fh = face_info['box']
                cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (255, 0, 0), 2)
            
            # Matches
            for match in matches:
                idx, face_crop, face_info, score = match
                px, py, pex, pey = people_boxes[idx]
                fx, fy, fw, fh = face_info['box']
                
                # Line connecting person to face
                person_center = (px + (pex-px)//2, py + (pey-py)//2)
                face_center = (fx + fw//2, fy + fh//2)
                cv2.line(frame, person_center, face_center, (0, 255, 255), 3)
                
                # Score
                cv2.putText(frame, f"{score:.2f}", 
                           (fx, fy - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.5, (0, 255, 255), 2)
            
            # Stats overlay
            cv2.putText(frame, f"Frame: {self.frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"People: {len(people_boxes)}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces: {len(face_results)}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Matches: {len(matches)}", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if self.frame_count % 20 == 0:
                elapsed = time.time() - frame_start
                print(f"  Frame {self.frame_count}: {len(people_boxes)} people, "
                      f"{len(face_results)} faces, {len(matches)} matches, "
                      f"{elapsed*1000:.0f}ms")
            
            stats['processing_times'].append(time.time() - frame_start)
            out.write(frame)
            self.frame_count += 1
        
        total_time = time.time() - start_time
        
        cap.release()
        out.release()
        
        # Calculate statistics
        avg_match_score = stats['avg_match_score'] / (stats['matches'] or 1)
        avg_fps = self.frame_count / total_time
        avg_frame_time = np.mean(stats['processing_times']) * 1000
        
        print(f"\n{'='*80}")
        print(f"✅ OPTIMIZED ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"📊 RESULTS:")
        print(f"  - Frames processed: {self.frame_count}")
        print(f"  - People detected: {stats['people']}")
        print(f"  - Faces detected: {stats['faces']}")
        print(f"  - Matches: {stats['matches']}")
        print(f"  - Match rate: {stats['matches']/stats['people']*100:.1f}%")
        print(f"  - Avg match score: {avg_match_score:.2f}")
        print(f"  - Performance: {avg_fps:.1f} FPS")
        print(f"  - Avg frame time: {avg_frame_time:.0f}ms")
        print(f"  - Total time: {total_time:.1f}s")
        print(f"\n📹 Output: {output_path}")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    analyzer = OptimizedAnalysis()
    analyzer.process_video_optimized(
        video_path="/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4",
        output_path="output/optimized_analysis.mp4",
        max_frames=200
    )

