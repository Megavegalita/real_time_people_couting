"""
Integration Test: Add Gender & Age Analysis to People Counter

This script integrates the new gender_analysis module with the existing
people_counter.py system to add gender and age detection.
"""

import sys
import cv2
import numpy as np
from pathlib import Path

# Add gender_analysis to path
sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from typing import Dict, Any, List, Tuple, Optional
import imutils
import argparse
from imutils.video import FPS, VideoStream
from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
import time
import json

# Import gender analysis components
from core.services.classification import PersonAnalysisService, analysis_service
from core.services.face_processing import FaceProcessor


def integrate_gender_age_analysis(
    video_path: str,
    prototxt: str = "detector/MobileNetSSD_deploy.prototxt",
    model: str = "detector/MobileNetSSD_deploy.caffemodel",
    confidence: float = 0.4,
    skip_frames: int = 30,
    output_path: str = "output_with_gender_age.mp4",
    max_frames: int = 200
) -> Dict[str, Any]:
    """
    Integrate gender and age analysis with people counter.
    
    Args:
        video_path: Path to input video
        prototxt: Path to MobileNetSSD prototxt
        model: Path to MobileNetSSD model
        confidence: Detection confidence threshold
        skip_frames: Frames to skip between detections
        output_path: Output video path
        max_frames: Maximum frames to process
        
    Returns:
        Statistics dictionary
    """
    print(f"\n{'='*70}")
    print(f"🚀 INTEGRATING GENDER & AGE ANALYSIS WITH PEOPLE COUNTER")
    print(f"{'='*70}")
    print(f"Input: {video_path}")
    print(f"Max frames: {max_frames}")
    print(f"{'='*70}\n")
    
    # Load MobileNetSSD model
    print("📦 Loading MobileNetSSD model...")
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    print("✅ Model loaded")
    
    # Initialize services
    print("🔧 Initializing services...")
    face_processor = FaceProcessor()
    person_service = PersonAnalysisService()
    print("✅ Services initialized")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return {}
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\n📹 Video Info:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {total_frames}")
    
    # Create output writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Initialize tracker
    ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    trackableObjects: Dict[int, TrackableObject] = {}
    objects = {}  # Initialize objects dict
    
    # Statistics
    stats = {
        'frame_count': 0,
        'detections': 0,
        'people_in': 0,
        'people_out': 0,
        'gender_male': 0,
        'gender_female': 0,
        'age_sum': 0,
        'age_count': 0,
        'analyses_done': 0,
        'analyses_failed': 0
    }
    
    # FPS tracking
    fps_tracker = FPS().start()
    
    print(f"\n🎬 Processing video...")
    print(f"{'─'*70}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        stats['frame_count'] += 1
        
        if stats['frame_count'] > max_frames:
            break
        
        if stats['frame_count'] % 30 == 0:
            print(f"  Frame {stats['frame_count']}/{total_frames} | "
                  f"Total: {stats['people_in'] + stats['people_out']} | "
                  f"Analyzed: {stats['analyses_done']}")
        
        # Resize frame
        frame_resized = cv2.resize(frame, (500, 500))
        
        # Skip detection for performance
        if stats['frame_count'] % skip_frames == 0:
            # Convert to blob
            blob = cv2.dnn.blobFromImage(
                frame_resized,
                0.007843,
                (500, 500),
                127.5
            )
            
            # Detect objects
            net.setInput(blob)
            detections = net.forward()
            
            rects = []
            
            for i in range(detections.shape[2]):
                confidence_score = detections[0, 0, i, 2]
                
                if confidence_score > confidence:
                    idx = int(detections[0, 0, i, 1])
                    
                    # Only detect person (class 15)
                    if idx == 15:
                        box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                        (startX, startY, endX, endY) = box.astype("int")
                        
                        rects.append((startX, startY, endX, endY))
                        stats['detections'] += 1
            
            # Update tracker
            objects = ct.update(rects)
            
            for (objectID, centroid) in objects.items():
                to = trackableObjects.get(objectID, None)
                
                if to is None:
                    # New person detected
                    to = TrackableObject(objectID, centroid)
                    trackableObjects[objectID] = to
                else:
                    # Update existing person
                    direction = centroid[1] - to.centroids[-1][1]
                    to.centroids.append(centroid)
                    
                    # Check if person passed the line
                    if not to.counted:
                        if direction < 0:
                            stats['people_out'] += 1
                            to.counted = True
                        else:
                            stats['people_in'] += 1
                            to.counted = True
                    
                    # Analyze gender & age on tracked person
                    if not to.counted or not hasattr(to, 'analyzed'):
                        try:
                            # Get person bounding box
                            person_rect = None
                            for rect in rects:
                                if rect is not None:
                                    person_rect = rect
                                    break
                            
                            if person_rect is not None:
                                startX, startY, endX, endY = person_rect
                                
                                # Extract person crop
                                person_crop = frame[startY:endY, startX:endX]
                                
                                if person_crop.size > 0:
                                    # Analyze gender & age using full frame and person bbox
                                    result = person_service.analyze_person(
                                        frame=frame,
                                        person_id=objectID,
                                        bbox=(startX, startY, endX-startX, endY-startY),
                                        camera_id="test_camera"
                                    )
                                    
                                    if result and result.get('status') == 'success':
                                        to.gender = result.get('gender')
                                        to.age = result.get('age')
                                        to.analyzed = True
                                        stats['analyses_done'] += 1
                                        
                                        # Update statistics
                                        if result['gender'] == 'male':
                                            stats['gender_male'] += 1
                                        elif result['gender'] == 'female':
                                            stats['gender_female'] += 1
                                        
                                        stats['age_sum'] += result.get('age', 0)
                                        stats['age_count'] += 1
                                    else:
                                        stats['analyses_failed'] += 1
                                        
                        except Exception as e:
                            stats['analyses_failed'] += 1
        
        # Draw tracking info
        for (objectID, centroid) in objects.items():
            to = trackableObjects.get(objectID, None)
            
            # Draw ID
            text = f"ID {objectID}"
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            
            # Draw gender & age if analyzed
            if to and hasattr(to, 'analyzed') and to.analyzed:
                gender_age = f"{to.gender}, {to.age}y"
                cv2.putText(frame, gender_age, (centroid[0] - 10, centroid[1] + 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 2)
        
        # Draw statistics
        info = [
            f"Frame: {stats['frame_count']}",
            f"People In: {stats['people_in']}",
            f"People Out: {stats['people_out']}",
            f"Total: {stats['people_in'] + stats['people_out']}",
            f"Male: {stats['gender_male']}",
            f"Female: {stats['gender_female']}",
        ]
        
        y_offset = 30
        for info_line in info:
            cv2.putText(frame, info_line, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 30
        
        out.write(frame)
        fps_tracker.update()
    
    # Cleanup
    cap.release()
    out.release()
    fps_tracker.stop()
    
    # Print results
    print(f"\n{'='*70}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 STATISTICS:")
    print(f"  - Frames processed: {stats['frame_count']}")
    print(f"  - People detected: {stats['detections']}")
    print(f"  - People in: {stats['people_in']}")
    print(f"  - People out: {stats['people_out']}")
    print(f"  - Total tracked: {stats['people_in'] + stats['people_out']}")
    print(f"\n🎯 Gender Analysis:")
    print(f"  - Male: {stats['gender_male']}")
    print(f"  - Female: {stats['gender_female']}")
    if stats['age_count'] > 0:
        print(f"  - Average age: {stats['age_sum']/stats['age_count']:.1f} years")
    print(f"\n🔧 Technical:")
    print(f"  - Analyses done: {stats['analyses_done']}")
    print(f"  - Analyses failed: {stats['analyses_failed']}")
    print(f"  - FPS: {fps_tracker.fps():.2f}")
    print(f"\n📹 Output saved: {output_path}")
    print(f"{'='*70}\n")
    
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test gender & age integration")
    parser.add_argument("-i", "--input", required=True, help="Input video path")
    parser.add_argument("-o", "--output", default="output_with_gender_age.mp4",
                       help="Output video path")
    parser.add_argument("-m", "--max-frames", type=int, default=200,
                       help="Max frames to process")
    parser.add_argument("-s", "--skip-frames", type=int, default=30,
                       help="Frames to skip between detections")
    
    args = parser.parse_args()
    
    stats = integrate_gender_age_analysis(
        video_path=args.input,
        output_path=args.output,
        max_frames=args.max_frames,
        skip_frames=args.skip_frames
    )
    
    print("\n✅ Test complete!\n")

