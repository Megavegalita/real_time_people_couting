"""
Test DNN Face Detector Integration

Test the new DNN face detector on shopping_korea.mp4 video.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

import cv2
import numpy as np
from core.services.face_detectors.dnn_face import DNNFaceDetector
from core.services.face_processing import FaceProcessor


def test_dnn_detector():
    """Test DNN detector on sample video."""
    print("\n" + "="*80)
    print("🧪 TESTING DNN FACE DETECTOR")
    print("="*80 + "\n")
    
    # Initialize
    print("📦 Initializing DNN face detector...")
    dnn_detector = DNNFaceDetector()
    print("✅ DNN detector ready\n")
    
    # Test on shopping_korea.mp4
    video_path = "utils/data/tests/shopping_korea.mp4"
    
    print(f"📹 Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Cannot open video")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📹 Resolution: {width}x{height}, FPS: {fps}\n")
    
    # Test first 100 frames
    frame_count = 0
    faces_found = 0
    
    print("🎬 Testing on first 100 frames...\n")
    
    while frame_count < 100:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count % 20 == 0:
            print(f"  Processing frame {frame_count}...")
        
        # Try face detection on full frame
        faces = dnn_detector.detect(frame)
        
        if len(faces) > 0:
            faces_found += len(faces)
            print(f"  ✓ Frame {frame_count}: {len(faces)} face(s) detected")
    
    cap.release()
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE")
    print(f"{'='*80}")
    print(f"📊 RESULTS:")
    print(f"  - Frames tested: {frame_count}")
    print(f"  - Faces detected: {faces_found}")
    print(f"  - Average per frame: {faces_found/frame_count:.2f}")
    print(f"{'='*80}\n")


def test_face_processor():
    """Test FaceProcessor with DNN."""
    print("\n" + "="*80)
    print("🧪 TESTING FACE PROCESSOR WITH DNN")
    print("="*80 + "\n")
    
    # Initialize
    processor = FaceProcessor()
    
    # Test on shopping_korea.mp4
    video_path = "utils/data/tests/shopping_korea.mp4"
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video")
        return
    
    # Test first 50 frames
    frame_count = 0
    total_faces = 0
    
    print("🎬 Testing FaceProcessor...\n")
    
    while frame_count < 50:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count % 10 == 0:
            print(f"  Processing frame {frame_count}...")
        
        # Process frame
        results = processor.process_frame(frame)
        
        if len(results) > 0:
            total_faces += len(results)
            print(f"  ✓ Frame {frame_count}: {len(results)} face(s) processed")
    
    cap.release()
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETE")
    print(f"{'='*80}")
    print(f"📊 RESULTS:")
    print(f"  - Frames tested: {frame_count}")
    print(f"  - Faces processed: {total_faces}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Test 1: DNN detector directly
    test_dnn_detector()
    
    # Test 2: FaceProcessor with DNN
    test_face_processor()
    
    print("\n✅ All tests complete!\n")

