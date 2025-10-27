"""
Debug single frame to identify issues

Check:
1. Are there multiple bboxes for same person?
2. Is face bbox drawn correctly?
3. Is gender/age displayed correctly?
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject

# Import face detection from V5
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    MTCNN_AVAILABLE = False


def test_single_frame():
    """Test single frame to debug issues."""
    print("\n" + "="*80)
    print("🔍 DEBUGGING SINGLE FRAME")
    print("="*80 + "\n")
    
    # Load frame 13 (problematic frame)
    video_path = "utils/data/tests/shopping_korea.mp4"
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 13)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Cannot load frame 13")
        return
    
    print(f"📹 Frame 13 loaded: {frame.shape}")
    
    # Person detection
    net = cv2.dnn.readNetFromCaffe(
        "detector/MobileNetSSD_deploy.prototxt",
        "detector/MobileNetSSD_deploy.caffemodel"
    )
    
    h, w = frame.shape[:2]
    frame_resized = cv2.resize(frame, (500, 500))
    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
    net.setInput(blob)
    detections = net.forward()
    
    boxes = []
    for i in range(detections.shape[2]):
        conf = detections[0, 0, i, 2]
        idx = int(detections[0, 0, i, 1])
        
        if conf > 0.3 and idx == 15:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (px1, py1, px2, py2) = box.astype("int")
            boxes.append((px1, py1, px2 - px1, py2 - py1))
    
    print(f"\n✅ Detected {len(boxes)} people")
    
    # Face detection test
    if MEDIAPIPE_AVAILABLE:
        mp_face_detection = mp.solutions.face_detection
        face_detection = mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.1
        )
        
        print("\n🔍 Testing face detection on each person:")
        print("-" * 80)
        
        annotated = frame.copy()
        
        for idx, (px, py, pw, ph) in enumerate(boxes):
            print(f"\nPerson {idx}:")
            print(f"  Bbox: ({px}, {py}, {pw}, {ph})")
            
            # Extract person crop
            person_crop = frame[py:py+ph, px:px+pw]
            
            if person_crop.size == 0:
                print("  ⚠️  Empty crop!")
                continue
            
            print(f"  Crop size: {person_crop.shape}")
            
            # Face detection
            rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb)
            
            face_count = 0
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    fx = int(bbox.xmin * pw)
                    fy = int(bbox.ymin * ph)
                    fw = int(bbox.width * pw)
                    fh = int(bbox.height * ph)
                    
                    # Fix: fx, fy are relative to person crop, NOT full frame
                    # Correct drawing:
                    # - Person bbox at full frame coordinates (px, py, px+pw, py+ph)
                    # - Face bbox at person crop coordinates (fx, fy) within crop
                    # - To draw face on full frame: (px + fx, py + fy)
                    
                    print(f"  🎯 Face {face_count}:")
                    print(f"     In crop: ({fx}, {fy}, {fw}, {fh})")
                    print(f"     In full frame: ({px + fx}, {py + fy}, {fw}, {fh})")
                    
                    # Draw person bbox (green)
                    cv2.rectangle(annotated, (px, py), (px+pw, py+ph), (0, 255, 0), 3)
                    
                    # Draw face bbox (blue) - MUST use correct coordinates
                    # fx, fy are relative to person crop (0,0)
                    # To draw on full frame: px + fx, py + fy
                    cv2.rectangle(annotated, 
                                 (px + fx, py + fy),  # CORRECT!
                                 (px + fx + fw, py + fy + fh),
                                 (255, 0, 0), 2)
                    
                    # Draw person ID
                    cv2.putText(annotated, f"P{idx}", (px + 10, py + 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    face_count += 1
            
            if face_count == 0:
                print("  ⚠️  No face detected")
                
                # Draw person bbox in red (no face)
                cv2.rectangle(annotated, (px, py), (px+pw, py+ph), (0, 0, 255), 3)
        
        # Save debug frame
        cv2.imwrite("output/debug_frame13_detailed.jpg", annotated)
        print(f"\n✅ Saved: output/debug_frame13_detailed.jpg")
        print(f"📊 Total faces detected: {face_count}")


if __name__ == "__main__":
    test_single_frame()

