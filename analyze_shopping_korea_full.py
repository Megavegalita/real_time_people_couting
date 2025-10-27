"""
Complete Analysis with Gender & Age - Shopping Korea Video

This script integrates gender and age analysis with person tracking.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import json
import sys

# Add gender_analysis to path
sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject

# Import gender analysis
from core.services.classification import PersonAnalysisService
from core.services.face_processing import FaceProcessor


class CompleteAnalyzer:
    """Complete analyzer with gender & age detection."""
    
    def __init__(self, prototxt: str = "detector/MobileNetSSD_deploy.prototxt",
                 model: str = "detector/MobileNetSSD_deploy.caffemodel"):
        """Initialize analyzer."""
        print(f"📦 Loading MobileNetSSD model...")
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        print(f"✅ Model loaded\n")
        
        print(f"📦 Loading Gender/Age analysis services...")
        self.person_service = PersonAnalysisService()
        self.face_processor = FaceProcessor()
        print(f"✅ Gender/Age services loaded\n")
        
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects: Dict[int, TrackableObject] = {}
        
        # Statistics
        self.stats = {
            'frame_count': 0,
            'total_detections': 0,
            'people_in': 0,
            'people_out': 0,
            'gender_male': 0,
            'gender_female': 0,
            'age_sum': 0,
            'age_count': 0,
            'analyses_success': 0,
            'analyses_failed': 0,
            'person_entries': [],
            'person_exits': []
        }
    
    def analyze_frame(self, frame: np.ndarray, width: int, height: int,
                     confidence: float = 0.4) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Analyze frame with gender & age."""
        frame_count = self.stats['frame_count']
        self.stats['frame_count'] += 1
        
        # Resize for detection
        frame_resized = cv2.resize(frame, (500, 500))
        
        # Convert to blob
        blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
        
        # Detect
        self.net.setInput(blob)
        detections = self.net.forward()
        
        rects = []
        detection_info = []
        
        for i in range(detections.shape[2]):
            confidence_score = detections[0, 0, i, 2]
            
            if confidence_score > confidence:
                idx = int(detections[0, 0, i, 1])
                
                if idx == 15:  # Person
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    rects.append((startX, startY, endX, endY))
                    detection_info.append({
                        'bbox': (startX, startY, endX-startX, endY-startY),
                        'confidence': confidence_score,
                        'rect': (startX, startY, endX, endY)
                    })
                    self.stats['total_detections'] += 1
        
        # Update tracker
        objects = self.ct.update(rects) if rects else {}
        
        # Process tracking and analysis
        for idx, (objectID, centroid) in enumerate(objects.items()):
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
                
                # Try gender/age analysis for new person
                if idx < len(detection_info):
                    info = detection_info[idx]
                    self._analyze_gender_age(frame, objectID, info, to)
            else:
                direction = centroid[1] - to.centroids[-1][1]
                to.centroids.append(centroid)
                
                if not to.counted:
                    if direction < 0:
                        self.stats['people_out'] += 1
                        to.counted = True
                        self.stats['person_exits'].append({
                            'person_id': objectID,
                            'frame': frame_count
                        })
                        print(f"  🚪 Person {objectID} EXIT")
                    else:
                        self.stats['people_in'] += 1
                        to.counted = True
                        self.stats['person_entries'].append({
                            'person_id': objectID,
                            'frame': frame_count
                        })
                        print(f"  🚶 Person {objectID} ENTRY")
        
        # Draw annotations
        annotated = self.draw_complete_overlays(frame.copy(), rects, objects, frame_count)
        
        return annotated, self.stats
    
    def _analyze_gender_age(self, frame: np.ndarray, person_id: int,
                           detection_info: Dict, trackable_obj: TrackableObject):
        """Analyze gender and age for a person."""
        try:
            bbox = detection_info['bbox']
            
            # Analyze
            result = self.person_service.analyze_person(
                frame=frame,
                person_id=person_id,
                bbox=bbox,
                camera_id="shopping_korea"
            )
            
            if result and result.get('status') == 'success':
                trackable_obj.gender = result.get('gender', 'unknown')
                trackable_obj.age = result.get('age', -1)
                trackable_obj.gender_confidence = result.get('gender_confidence', 0.0)
                trackable_obj.age_confidence = result.get('age_confidence', 0.0)
                trackable_obj.analyzed = True
                trackable_obj.face_bbox = result.get('face_bbox')
                
                self.stats['analyses_success'] += 1
                
                # Update stats
                if result['gender'] == 'male':
                    self.stats['gender_male'] += 1
                elif result['gender'] == 'female':
                    self.stats['gender_female'] += 1
                
                self.stats['age_sum'] += result.get('age', 0)
                self.stats['age_count'] += 1
                
                print(f"  ✓ Person {person_id}: {result['gender']}, {result['age']}y")
            else:
                self.stats['analyses_failed'] += 1
                trackable_obj.analyzed = False
                
        except Exception as e:
            self.stats['analyses_failed'] += 1
            trackable_obj.analyzed = False
    
    def draw_complete_overlays(self, frame: np.ndarray, rects: List[Tuple],
                              objects: Dict, frame_count: int) -> np.ndarray:
        """Draw complete overlays with gender & age info."""
        
        # Draw detection boxes
        for (startX, startY, endX, endY) in rects:
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        
        # Draw tracking with gender/age info
        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to:
                # Draw centroid
                cv2.circle(frame, (centroid[0], centroid[1]), 6, (0, 255, 0), -1)
                
                # Draw trajectory
                if len(to.centroids) > 1:
                    for i in range(1, len(to.centroids)):
                        cv2.line(frame,
                                tuple(to.centroids[i-1]),
                                tuple(to.centroids[i]),
                                (255, 255, 0), 2)
                
                # Status
                status = "TRACKED"
                if to.counted:
                    direction = "OUT" if to.centroids[0][1] > centroid[1] else "IN"
                    status = f"✓ {direction}"
                
                # Gender & Age info
                if hasattr(to, 'analyzed') and to.analyzed:
                    gender = getattr(to, 'gender', 'unknown')
                    age = getattr(to, 'age', -1)
                    gender_conf = getattr(to, 'gender_confidence', 0.0)
                    
                    gender_info = f"{gender.upper()}"
                    age_info = f"{age}y"
                    
                    # Draw gender & age
                    x, y = centroid[0], centroid[1]
                    
                    cv2.rectangle(frame,
                                 (x - 40, y - 80),
                                 (x + 100, y - 10),
                                 (0, 0, 0), -1)
                    
                    cv2.putText(frame, f"ID: {objectID}",
                               (x - 35, y - 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                               (255, 255, 255), 1, cv2.LINE_AA)
                    
                    cv2.putText(frame, gender_info,
                               (x - 35, y - 45),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                               (0, 255, 0), 1, cv2.LINE_AA)
                    
                    cv2.putText(frame, age_info,
                               (x - 35, y - 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                               (255, 255, 0), 1, cv2.LINE_AA)
                    
                    cv2.putText(frame, status,
                               (x - 35, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                               (200, 200, 200), 1, cv2.LINE_AA)
                else:
                    # Just ID and status
                    x, y = centroid[0], centroid[1]
                    cv2.rectangle(frame,
                                 (x - 40, y - 50),
                                 (x + 80, y - 10),
                                 (0, 0, 0), -1)
                    
                    cv2.putText(frame, f"ID: {objectID}",
                               (x - 35, y - 35),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                               (255, 255, 255), 1, cv2.LINE_AA)
                    
                    cv2.putText(frame, status,
                               (x - 35, y - 15),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                               (200, 200, 200), 1, cv2.LINE_AA)
        
        # Draw complete stats panel
        stats = [
            f"Frame: {frame_count}",
            f"Detections: {len(rects)}",
            f"Tracked: {len(objects)}",
            f"In: {self.stats['people_in']}",
            f"Out: {self.stats['people_out']}",
            f"Male: {self.stats['gender_male']}",
            f"Female: {self.stats['gender_female']}",
            f"Age avg: {self.stats['age_sum']/self.stats['age_count']:.0f}" if self.stats['age_count'] > 0 else "Age avg: -",
            f"Analysis: {self.stats['analyses_success']}"
        ]
        
        for i, text in enumerate(stats):
            cv2.rectangle(frame, (10, 10 + i*30), (350, 35 + i*30), (0, 0, 0), -1)
            cv2.putText(frame, text, (15, 28 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       (0, 255, 255), 1, cv2.LINE_AA)
        
        return frame


def analyze_complete(video_path: str, output_path: str, max_frames: int = 200):
    """Analyze video with complete gender & age analysis."""
    
    print(f"\n{'='*80}")
    print(f"🔍 COMPLETE ANALYSIS - Gender & Age Integration")
    print(f"{'='*80}")
    print(f"Input: {video_path}")
    print(f"Output: {output_path}")
    print(f"{'='*80}\n")
    
    analyzer = CompleteAnalyzer()
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open: {video_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Resolution: {width}x{height}, FPS: {fps}\n")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    
    print(f"🎬 Processing with gender & age analysis...\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count > max_frames:
            break
        
        if frame_count % 50 == 0:
            print(f"  Frame {frame_count}/{max_frames} | "
                  f"Tracked: {len(analyzer.trackableObjects)} | "
                  f"Gender: M:{analyzer.stats['gender_male']} F:{analyzer.stats['gender_female']} | "
                  f"Analysis: {analyzer.stats['analyses_success']}")
        
        annotated, stats = analyzer.analyze_frame(frame, width, height)
        out.write(annotated)
    
    cap.release()
    out.release()
    
    print(f"\n{'='*80}")
    print(f"✅ ANALYSIS COMPLETE")
    print(f"{'='*80}\n")
    print(f"📊 FINAL RESULTS:")
    print(f"  - Frames: {stats['frame_count']}")
    print(f"  - Detections: {stats['total_detections']}")
    print(f"  - People IN: {stats['people_in']}")
    print(f"  - People OUT: {stats['people_out']}")
    print(f"  - Male: {stats['gender_male']}")
    print(f"  - Female: {stats['gender_female']}")
    if stats['age_count'] > 0:
        print(f"  - Average Age: {stats['age_sum']/stats['age_count']:.1f}")
    print(f"  - Analysis Success: {stats['analyses_success']}")
    print(f"  - Analysis Failed: {stats['analyses_failed']}")
    print(f"\n📹 Output: {output_path}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    video_path = "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4"
    output_path = "output/shopping_korea_with_gender_age.mp4"
    
    analyze_complete(video_path, output_path, max_frames=200)
    
    print("\n✅ Complete!\n")

