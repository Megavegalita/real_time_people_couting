"""
Test with Real Person Bounding Boxes

Test gender/age analysis with actual person detections from MobileNetSSD.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

import cv2
import numpy as np
from core.services.classification import PersonAnalysisService

# Load MobileNetSSD for person detection
prototxt = "detector/MobileNetSSD_deploy.prototxt"
model = "detector/MobileNetSSD_deploy.caffemodel"


def test_with_real_detections():
    """Test with actual person detections."""
    print("\n" + "="*80)
    print("🧪 TESTING WITH REAL PERSON DETECTIONS")
    print("="*80 + "\n")
    
    # Load models
    print("📦 Loading models...")
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    person_service = PersonAnalysisService()
    print("✅ Models loaded\n")
    
    video_path = "utils/data/tests/shopping_korea.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Cannot open video")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    successes = 0
    failures = 0
    
    # Test first 50 frames
    for frame_idx in range(50):
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % 10 == 0:
            print(f"\n--- Frame {frame_idx+1} ---")
        
        # Detect people
        frame_resized = cv2.resize(frame, (500, 500))
        blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
        
        net.setInput(blob)
        detections = net.forward()
        
        person_count = 0
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            idx = int(detections[0, 0, i, 1])
            
            if confidence > 0.4 and idx == 15:  # Person
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Create bbox (x, y, w, h)
                bbox = (startX, startY, endX - startX, endY - startY)
                
                # Try gender/age analysis
                try:
                    result = person_service.analyze_person(
                        frame=frame,
                        person_id=frame_idx * 1000 + person_count,
                        bbox=bbox,
                        camera_id="test"
                    )
                    
                    if result.get('status') == 'success':
                        successes += 1
                        print(f"  ✓ Person {person_count}: {result['gender']}, {result['age']}y")
                    else:
                        failures += 1
                        reason = result.get('reason', 'unknown')
                        if 'No face' in reason:
                            failures += 1
                        elif 'Feature extraction' in reason:
                            pass  # Expected for now
                
                except Exception as e:
                    failures += 1
                
                person_count += 1
                if person_count >= 3:  # Max 3 per frame for speed
                    break
    
    cap.release()
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE")
    print(f"{'='*80}")
    print(f"📊 RESULTS:")
    print(f"  - Successful: {successes}")
    print(f"  - Failed: {failures}")
    print(f"  - Total: {successes + failures}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_with_real_detections()

