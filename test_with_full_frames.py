"""
Full Integration Test - Process ALL frames without skipping
"""

import cv2
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from typing import Dict, Any, List, Tuple
from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
import argparse

# Import gender analysis components
from core.services.classification import PersonAnalysisService
from core.services.face_processing import FaceProcessor


def test_full_video(
    video_path: str,
    prototxt: str = "detector/MobileNetSSD_deploy.prototxt",
    model: str = "detector/MobileNetSSD_deploy.caffemodel",
    confidence: float = 0.4,
    output_path: str = "output_full_test.mp4",
    max_frames: int = 200
) -> Dict[str, Any]:
    """
    Test full video with every frame processed.
    
    Args:
        video_path: Input video path
        prototxt: MobileNetSSD prototxt
        model: MobileNetSSD model
        confidence: Detection confidence
        output_path: Output video path
        max_frames: Maximum frames to process
        
    Returns:
        Statistics dictionary
    """
    print(f"\n{'='*80}")
    print(f"🚀 FULL VIDEO PROCESSING - NO FRAME SKIPPING")
    print(f"{'='*80}")
    print(f"Video: {video_path}")
    print(f"Max frames: {max_frames}")
    print(f"Processing: EVERY FRAME")
    print(f"{'='*80}\n")
    
    # Load MobileNetSSD
    print("📦 Loading MobileNetSSD...")
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    print("✅ Model loaded")
    
    # Initialize services
    print("🔧 Initializing services...")
    face_processor = FaceProcessor()
    person_service = PersonAnalysisService()
    print("✅ Services initialized\n")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return {}
    
    # Get properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 Video Info:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {total_frames}\n")
    
    # Create output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Initialize tracker
    ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    trackableObjects: Dict[int, TrackableObject] = {}
    
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
        'analyses_failed': 0,
        'face_detection_fails': 0,
        'feature_extraction_fails': 0,
        'classification_fails': 0
    }
    
    print(f"🎬 Processing EVERY frame...")
    print(f"{'─'*80}")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        stats['frame_count'] = frame_count
        
        if frame_count > max_frames:
            break
        
        if frame_count % 20 == 0:
            print(f"  Frame {frame_count}/{total_frames} | "
                  f"Total: {stats['people_in'] + stats['people_out']} | "
                  f"Analyzed: {stats['analyses_done']} | "
                  f"Failed: {stats['analyses_failed']}")
        
        # Resize for detection
        frame_resized = cv2.resize(frame, (500, 500))
        
        # Convert to blob
        blob = cv2.dnn.blobFromImage(
            frame_resized,
            0.007843,
            (500, 500),
            127.5
        )
        
        # Detect
        net.setInput(blob)
        detections = net.forward()
        
        rects = []
        detection_info = []
        
        for i in range(detections.shape[2]):
            confidence_score = detections[0, 0, i, 2]
            
            if confidence_score > confidence:
                idx = int(detections[0, 0, i, 1])
                
                if idx == 15:  # Person class
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    rects.append((startX, startY, endX, endY))
                    detection_info.append({
                        'box': (startX, startY, endX-startX, endY-startY),
                        'confidence': confidence_score
                    })
                    stats['detections'] += 1
        
        # Update tracker
        objects = ct.update(rects)
        
        for (objectID, centroid) in objects.items():
            to = trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                trackableObjects[objectID] = to
            else:
                direction = centroid[1] - to.centroids[-1][1]
                to.centroids.append(centroid)
                
                if not to.counted:
                    if direction < 0:
                        stats['people_out'] += 1
                        to.counted = True
                    else:
                        stats['people_in'] += 1
                        to.counted = True
                
                # Analyze gender & age
                if not hasattr(to, 'analyzed') or not to.analyzed:
                    try:
                        # Find corresponding detection info
                        if objectID < len(detection_info):
                            info = detection_info[objectID]
                            bbox = info['box']
                            
                            # Analyze
                            result = person_service.analyze_person(
                                frame=frame,
                                person_id=objectID,
                                bbox=bbox,
                                camera_id="test_camera"
                            )
                            
                            if result and result.get('status') == 'success':
                                to.gender = result.get('gender')
                                to.age = result.get('age')
                                to.analyzed = True
                                stats['analyses_done'] += 1
                                
                                if result['gender'] == 'male':
                                    stats['gender_male'] += 1
                                elif result['gender'] == 'female':
                                    stats['gender_female'] += 1
                                
                                stats['age_sum'] += result.get('age', 0)
                                stats['age_count'] += 1
                            else:
                                stats['analyses_failed'] += 1
                                reason = result.get('reason', 'unknown') if result else 'no result'
                                if 'No face' in reason:
                                    stats['face_detection_fails'] += 1
                                elif 'Feature extraction' in reason:
                                    stats['feature_extraction_fails'] += 1
                                else:
                                    stats['classification_fails'] += 1
                    except Exception as e:
                        stats['analyses_failed'] += 1
        
        # Draw
        for (objectID, centroid) in objects.items():
            to = trackableObjects.get(objectID, None)
            
            # Draw ID
            text = f"ID {objectID}"
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            
            # Draw gender & age
            if to and hasattr(to, 'analyzed') and to.analyzed:
                gender_age = f"{to.gender}, {to.age}y"
                cv2.putText(frame, gender_age, (centroid[0] - 10, centroid[1] + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 2)
        
        # Draw stats
        info = [
            f"Frame: {frame_count}",
            f"People: {stats['people_in'] + stats['people_out']}",
            f"Analyzed: {stats['analyses_done']}",
            f"Failed: {stats['analyses_failed']}"
        ]
        
        y_offset = 30
        for info_line in info:
            cv2.putText(frame, info_line, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 30
        
        out.write(frame)
    
    cap.release()
    out.release()
    
    print(f"\n{'='*80}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"\n📊 STATISTICS:")
    print(f"  - Frames processed: {stats['frame_count']}")
    print(f"  - People detected: {stats['detections']}")
    print(f"  - People in: {stats['people_in']}")
    print(f"  - People out: {stats['people_out']}")
    print(f"  - Total tracked: {stats['people_in'] + stats['people_out']}")
    print(f"\n🎯 Gender/Age Analysis:")
    print(f"  - Successful: {stats['analyses_done']}")
    print(f"  - Failed: {stats['analyses_failed']}")
    print(f"  - Male: {stats['gender_male']}")
    print(f"  - Female: {stats['gender_female']}")
    if stats['age_count'] > 0:
        print(f"  - Average age: {stats['age_sum']/stats['age_count']:.1f}")
    print(f"\n🔧 Failure Breakdown:")
    print(f"  - Face detection: {stats['face_detection_fails']}")
    print(f"  - Feature extraction: {stats['feature_extraction_fails']}")
    print(f"  - Classification: {stats['classification_fails']}")
    print(f"\n📹 Output: {output_path}")
    print(f"{'='*80}\n")
    
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test with all frames")
    parser.add_argument("-i", "--input", required=True, help="Input video")
    parser.add_argument("-o", "--output", default="output_full.mp4", help="Output video")
    parser.add_argument("-m", "--max-frames", type=int, default=200, help="Max frames")
    
    args = parser.parse_args()
    
    stats = test_full_video(
        video_path=args.input,
        output_path=args.output,
        max_frames=args.max_frames
    )
    
    print("\n✅ Test complete!\n")

