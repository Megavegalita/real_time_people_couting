"""
Detailed Analysis - Shopping Korea Video Only

Focused analysis specifically for shopping_korea.mp4 video.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import json

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject


class ShoppingKoreaAnalyzer:
    """Specialized analyzer for shopping_korea.mp4."""
    
    def __init__(self, prototxt: str = "detector/MobileNetSSD_deploy.prototxt",
                 model: str = "detector/MobileNetSSD_deploy.caffemodel"):
        """Initialize analyzer."""
        print(f"📦 Loading MobileNetSSD model...")
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        print(f"✅ Model loaded\n")
        
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects: Dict[int, TrackableObject] = {}
        
        # Detailed statistics
        self.stats = {
            'frame_count': 0,
            'total_detections': 0,
            'people_in': 0,
            'people_out': 0,
            'tracking_data': [],
            'detection_per_frame': [],
            'person_entries': [],
            'person_exits': []
        }
    
    def analyze_frame(self, frame: np.ndarray, width: int, height: int, 
                     confidence: float = 0.4) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Analyze a single frame."""
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
        frame_detections = 0
        
        for i in range(detections.shape[2]):
            confidence_score = detections[0, 0, i, 2]
            
            if confidence_score > confidence:
                idx = int(detections[0, 0, i, 1])
                
                if idx == 15:  # Person
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (startX, startY, endX, endY) = box.astype("int")
                    rects.append((startX, startY, endX, endY))
                    frame_detections += 1
                    self.stats['total_detections'] += 1
        
        self.stats['detection_per_frame'].append(frame_detections)
        
        # Update tracker
        objects = self.ct.update(rects) if rects else {}
        
        # Process tracking
        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                # New person
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
                print(f"  🆕 Person {objectID} detected at frame {frame_count}")
            else:
                # Existing person
                direction = centroid[1] - to.centroids[-1][1]
                to.centroids.append(centroid)
                
                # Check crossing
                if not to.counted:
                    if direction < 0:  # Moving up
                        self.stats['people_out'] += 1
                        to.counted = True
                        self.stats['person_exits'].append({
                            'person_id': objectID,
                            'frame': frame_count,
                            'position': tuple(centroid)
                        })
                        print(f"  🚪 Person {objectID} EXIT at frame {frame_count}")
                    else:  # Moving down
                        self.stats['people_in'] += 1
                        to.counted = True
                        self.stats['person_entries'].append({
                            'person_id': objectID,
                            'frame': frame_count,
                            'position': tuple(centroid)
                        })
                        print(f"  🚶 Person {objectID} ENTRY at frame {frame_count}")
        
        # Draw annotations
        annotated = self.draw_annotations(frame.copy(), rects, objects, frame_count)
        
        return annotated, self.stats
    
    def draw_annotations(self, frame: np.ndarray, rects: List[Tuple],
                        objects: Dict, frame_count: int) -> np.ndarray:
        """Draw comprehensive annotations."""
        
        # Draw all detections
        for (startX, startY, endX, endY) in rects:
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        
        # Draw tracking with detailed info
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
                
                # Draw info box
                info_lines = [
                    f"ID: {objectID}",
                    f"Status: {status}",
                    f"Path: {len(to.centroids)} pts"
                ]
                
                x, y = centroid[0], centroid[1]
                
                # Background for text
                for i, line in enumerate(info_lines):
                    (w, h), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame,
                                 (x - 10, y - 60 + i*20),
                                 (x + w + 5, y - 40 + i*20),
                                 (0, 0, 0), -1)
                
                # Text
                for i, line in enumerate(info_lines):
                    cv2.putText(frame, line,
                               (x - 5, y - 45 + i*20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                               (255, 255, 255), 1, cv2.LINE_AA)
        
        # Draw comprehensive stats panel
        stats = [
            f"Frame: {frame_count}",
            f"Detections: {len(rects)}",
            f"Tracked: {len(objects)}",
            f"Total People IN: {self.stats['people_in']}",
            f"Total People OUT: {self.stats['people_out']}",
            f"Total Count: {self.stats['people_in'] + self.stats['people_out']}"
        ]
        
        for i, text in enumerate(stats):
            cv2.rectangle(frame, (10, 10 + i*35), (400, 40 + i*35), (0, 0, 0), -1)
            cv2.putText(frame, text, (15, 32 + i*35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (0, 255, 255), 2, cv2.LINE_AA)
        
        return frame


def analyze_shopping_korea(
    video_path: str,
    output_path: str,
    max_frames: int = 500,
    output_json: str = "output/analysis_report.json"
):
    """Analyze shopping_korea.mp4 in detail."""
    
    print(f"\n{'='*80}")
    print(f"🔍 DETAILED ANALYSIS - Shopping Korea Video")
    print(f"{'='*80}")
    print(f"Input: {video_path}")
    print(f"Output: {output_path}")
    print(f"Max frames: {max_frames}")
    print(f"{'='*80}\n")
    
    # Initialize
    analyzer = ShoppingKoreaAnalyzer()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open: {video_path}")
        return
    
    # Get properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 Video Properties:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {total_frames}")
    print(f"\n🎬 Starting detailed analysis...\n")
    
    # Create output writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count > max_frames:
            break
        
        # Analyze frame
        annotated, stats = analyzer.analyze_frame(frame, width, height)
        
        # Show progress
        if frame_count % 100 == 0:
            print(f"\n📊 Progress Report (Frame {frame_count}/{max_frames}):")
            print(f"  - Current tracked: {len(analyzer.trackableObjects)}")
            print(f"  - People IN: {stats['people_in']}")
            print(f"  - People OUT: {stats['people_out']}")
            print(f"  - Total detections: {stats['total_detections']}\n")
        
        out.write(annotated)
    
    # Cleanup
    cap.release()
    out.release()
    
    # Save detailed report
    report = {
        'video_info': {
            'path': video_path,
            'resolution': f"{width}x{height}",
            'fps': fps,
            'total_frames': total_frames,
            'processed_frames': frame_count
        },
        'statistics': {
            'total_detections': stats['total_detections'],
            'people_in': stats['people_in'],
            'people_out': stats['people_out'],
            'total_tracked': stats['people_in'] + stats['people_out'],
            'avg_detections_per_frame': sum(stats['detection_per_frame']) / len(stats['detection_per_frame'])
        },
        'person_entries': stats['person_entries'],
        'person_exits': stats['person_exits'],
        'tracking_details': {
            'total_persons_tracked': len(analyzer.trackableObjects),
            'persons_per_frame': stats['detection_per_frame']
        }
    }
    
    # Save report
    with open(output_json, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print final results
    print(f"\n{'='*80}")
    print(f"✅ ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"\n📊 FINAL STATISTICS:")
    print(f"  - Frames processed: {frame_count}")
    print(f"  - People detected: {stats['total_detections']}")
    print(f"  - People IN: {stats['people_in']}")
    print(f"  - People OUT: {stats['people_out']}")
    print(f"  - Total tracked: {stats['people_in'] + stats['people_out']}")
    print(f"  - Average detections/frame: {sum(stats['detection_per_frame'])/len(stats['detection_per_frame']):.1f}")
    print(f"\n📄 Detailed report: {output_json}")
    print(f"📹 Output video: {output_path}")
    print(f"{'='*80}\n")
    
    return report


if __name__ == "__main__":
    import sys
    
    video_path = "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4"
    output_video = "output/shopping_korea_analysis.mp4"
    output_json = "output/analysis_report.json"
    max_frames = 500
    
    report = analyze_shopping_korea(
        video_path=video_path,
        output_path=output_video,
        max_frames=max_frames,
        output_json=output_json
    )
    
    print("\n✅ Analysis complete!\n")

