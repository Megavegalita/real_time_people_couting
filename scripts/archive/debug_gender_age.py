"""
Debug Gender & Age Analysis

Test to find why analysis is failing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

import cv2
import numpy as np
from core.services.classification import PersonAnalysisService
from core.services.face_processing import FaceProcessor


def debug_analysis():
    """Debug gender & age analysis."""
    print("\n" + "="*80)
    print("🐛 DEBUGGING GENDER & AGE ANALYSIS")
    print("="*80 + "\n")
    
    # Initialize
    person_service = PersonAnalysisService()
    face_processor = FaceProcessor()
    
    # Test on shopping_korea.mp4
    video_path = "utils/data/tests/shopping_korea.mp4"
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video")
        return
    
    # Test first 20 frames
    for frame_idx in range(20):
        ret, frame = cap.read()
        if not ret:
            break
        
        print(f"\n--- Frame {frame_idx+1} ---")
        
        # Try to detect faces in frame
        faces = face_processor.process_frame(frame)
        print(f"  Faces detected: {len(faces)}")
        
        if len(faces) > 0:
            # Try to analyze
            bbox = (300, 300, 200, 400)  # Sample bbox
            
            try:
                result = person_service.analyze_person(
                    frame=frame,
                    person_id=999,
                    bbox=bbox,
                    camera_id="test"
                )
                
                if result.get('status') == 'success':
                    print(f"  ✅ Analysis success: {result['gender']}, {result['age']}")
                else:
                    print(f"  ❌ Analysis failed: {result.get('reason', 'unknown')}")
                    print(f"      Result: {result}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
    
    cap.release()


if __name__ == "__main__":
    debug_analysis()
    print("\n✅ Debug complete!\n")

