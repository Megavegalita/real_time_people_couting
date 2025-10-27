"""
Complete Analysis Test - Shopping Korea Video

This version uses full-frame face detection then matches to person bboxes.
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from core.services.face_processing import FaceProcessor


def test_full_pipeline():
    """Test complete pipeline with full-frame face detection."""
    print("\n" + "="*80)
    print("🧪 COMPLETE ANALYSIS TEST")
    print("="*80 + "\n")
    
    # Load models
    print("📦 Loading models...")
    from pathlib import Path
    prototxt = "detector/MobileNetSSD_deploy.prototxt"
    model = "detector/MobileNetSSD_deploy.caffemodel"
    
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    face_processor = FaceProcessor()
    print("✅ Models loaded\n")
    
    # Open video
    video_path = "utils/data/tests/shopping_korea.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Cannot open video")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Resolution: {width}x{height}\n")
    
    # Statistics
    stats = {
        'frames': 0,
        'people_detected': 0,
        'faces_detected_full': 0,
        'faces_matched': 0,
        'people_with_faces': 0
    }
    
    # Process first 100 frames
    print("🎬 Processing...\n")
    
    for frame_idx in range(100):
        ret, frame = cap.read()
        if not ret:
            break
        
        stats['frames'] += 1
        
        # Detect faces in full frame
        face_results = face_processor.process_frame(frame)
        stats['faces_detected_full'] += len(face_results)
        
        # Detect people
        frame_resized = cv2.resize(frame, (500, 500))
        blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
        net.setInput(blob)
        detections = net.forward()
        
        people_in_frame = 0
        
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            idx = int(detections[0, 0, i, 1])
            
            if confidence > 0.4 and idx == 15:  # Person
                people_in_frame += 1
                stats['people_detected'] += 1
                
                # Get person bbox
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Check if any face is in this person's area
                face_found = False
                for face_crop, face_info in face_results:
                    fx, fy, fw, fh = face_info['box']
                    
                    # Check if face center is within person bbox (with tolerance)
                    face_center_x = fx + fw // 2
                    face_center_y = fy + fh // 2
                    
                    tolerance = 50  # pixels
                    if (startX - tolerance <= face_center_x <= endX + tolerance and
                        startY - tolerance <= face_center_y <= endY + tolerance):
                        face_found = True
                        stats['faces_matched'] += 1
                        break
                
                if face_found:
                    stats['people_with_faces'] += 1
        
        if frame_idx % 20 == 0:
            print(f"  Frame {frame_idx}: {people_in_frame} people, {len(face_results)} faces")
    
    cap.release()
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE")
    print(f"{'='*80}\n")
    print(f"📊 RESULTS:")
    print(f"  - Frames processed: {stats['frames']}")
    print(f"  - People detected: {stats['people_detected']}")
    print(f"  - Faces in full frames: {stats['faces_detected_full']}")
    print(f"  - Faces matched to people: {stats['faces_matched']}")
    print(f"  - People with faces: {stats['people_with_faces']}")
    print(f"  - Match rate: {stats['people_with_faces']/stats['people_detected']*100:.1f}%")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_full_pipeline()

