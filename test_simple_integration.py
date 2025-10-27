"""
Simple Integration Test - Just test face detection first
"""

import cv2
import sys
from pathlib import Path

# Test basic face detection
video_path = "utils/data/tests/shopping_korea.mp4"

print(f"\n{'='*70}")
print(f"🧪 SIMPLE FACE DETECTION TEST")
print(f"{'='*70}\n")

# Open video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"❌ Cannot open video: {video_path}")
    sys.exit(1)

# Get video info
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"📹 Video Info:")
print(f"  - Resolution: {width}x{height}")
print(f"  - FPS: {fps}")
print(f"  - Total frames: {total_frames}\n")

# Initialize face detector (OpenCV Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

if face_cascade.empty():
    print("❌ Cannot load face detection model!")
    sys.exit(1)

print("✅ Face detector initialized\n")

# Process first 50 frames
frame_count = 0
faces_detected = 0
frames_with_faces = 0

print("🎬 Processing video...")
print(f"{'─'*70}")

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame_count += 1
    
    if frame_count > 50:  # Test first 50 frames
        break
    
    if frame_count % 10 == 0:
        print(f"  Frame {frame_count}/50...")
    
    # Resize frame
    frame_resized = cv2.resize(frame, (500, 500))
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    if len(faces) > 0:
        frames_with_faces += 1
        faces_detected += len(faces)
        
        # Draw bounding boxes
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_resized, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Display frame
    if frame_count <= 10:  # Show first 10 frames
        cv2.imshow('Face Detection Test', frame_resized)
        cv2.waitKey(30)

cap.release()
cv2.destroyAllWindows()

print(f"\n{'='*70}")
print(f"✅ PROCESSING COMPLETE")
print(f"{'='*70}")
print(f"\n📊 STATISTICS:")
print(f"  - Frames processed: {frame_count}")
print(f"  - Frames with faces: {frames_with_faces}")
print(f"  - Faces detected: {faces_detected}")
print(f"  - Average faces per frame with faces: {faces_detected/frames_with_faces:.1f}" if frames_with_faces > 0 else "")
print(f"{'='*70}\n")

