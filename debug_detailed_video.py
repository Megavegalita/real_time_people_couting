"""
Detailed debugging - Check why 2 boxes for same person and wrong gender

Issues visible:
1. ID:0 MALE 26y (yellow box) - wrong gender, female identified as male
2. ID:1 (no face) (red box) - overlaps with ID:0, same person
3. Why is person detector creating 2 boxes for 1 person?
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject


def debug_frame_detailed():
    """Debug frame to see detection details."""
    print("\n" + "="*80)
    print("🔍 DETAILED FRAME DEBUG")
    print("="*80 + "\n")
    
    # Load frame
    video_path = "utils/data/tests/shopping_korea.mp4"
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 13)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Cannot load frame")
        return
    
    h, w = frame.shape[:2]
    print(f"📹 Frame size: {w}x{h}")
    
    # Person detection
    net = cv2.dnn.readNetFromCaffe(
        "detector/MobileNetSSD_deploy.prototxt",
        "detector/MobileNetSSD_deploy.caffemodel"
    )
    
    frame_resized = cv2.resize(frame, (500, 500))
    blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
    net.setInput(blob)
    detections = net.forward()
    
    print("\n📋 DETECTION DETAILS:")
    print("-" * 80)
    
    det_list = []
    for i in range(detections.shape[2]):
        conf = detections[0, 0, i, 2]
        idx = int(detections[0, 0, i, 1])
        
        if conf > 0.3 and idx == 15:  # Person class
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (px1, py1, px2, py2) = box.astype("int")
            
            # Calculate center and size
            center_x = (px1 + px2) // 2
            center_y = (py1 + py2) // 2
            width = px2 - px1
            height = py2 - py1
            
            det_list.append({
                'det_idx': i,
                'confidence': conf,
                'bbox': (px1, py1, px2, py2),
                'center': (center_x, center_y),
                'size': (width, height),
                'area': width * height
            })
    
    print(f"\n🎯 Detected {len(det_list)} people:\n")
    
    for idx, det in enumerate(det_list):
        print(f"Detection {idx}:")
        print(f"  Confidence: {det['confidence']:.3f}")
        print(f"  Bbox: {det['bbox']}")
        print(f"  Center: {det['center']}")
        print(f"  Size: {det['size']}")
        print(f"  Area: {det['area']}")
        
        # Check if overlaps with other detection
        for other_idx, other_det in enumerate(det_list):
            if idx != other_idx:
                # Calculate IoU
                b1 = det['bbox']
                b2 = other_det['bbox']
                
                x1 = max(b1[0], b2[0])
                y1 = max(b1[1], b2[1])
                x2 = min(b1[2], b2[2])
                y2 = min(b1[3], b2[3])
                
                if x2 > x1 and y2 > y1:
                    inter = (x2 - x1) * (y2 - y1)
                    union = det['area'] + other_det['area'] - inter
                    iou = inter / union
                    
                    print(f"  ⚠️  Overlaps with Detection {other_idx}: IoU = {iou:.2f}")
        print()
    
    # Now check tracking
    print("\n" + "="*80)
    print("🎯 TRACKING ANALYSIS:")
    print("="*80 + "\n")
    
    ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    
    # Convert to tracking format
    boxes_for_tracking = []
    for det in det_list:
        px1, py1, px2, py2 = det['bbox']
        boxes_for_tracking.append((px1, py1, px2 - px1, py2 - py1))
    
    print(f"📦 Boxes sent to tracker: {len(boxes_for_tracking)}")
    for idx, box in enumerate(boxes_for_tracking):
        print(f"  Box {idx}: {box}")
    
    # Update tracker
    tracked_objects = ct.update(boxes_for_tracking)
    
    print(f"\n🏷️  Tracked objects: {len(tracked_objects)}")
    for objectID, centroid in tracked_objects.items():
        print(f"  Object ID {objectID}: centroid {centroid}")
    
    # Visualize
    annotated = frame.copy()
    
    # Draw all detections
    for idx, det in enumerate(det_list):
        px1, py1, px2, py2 = det['bbox']
        
        # Color: overlap detection
        color = (0, 255, 0) if idx == 0 else (0, 0, 255)
        cv2.rectangle(annotated, (px1, py1), (px2, py2), color, 3)
        
        # Label
        label = f"D{idx}: {det['confidence']:.2f}"
        cv2.putText(annotated, label, (px1 + 10, py1 + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Draw tracked objects
    for objectID, centroid in tracked_objects.items():
        cv2.circle(annotated, centroid, 10, (255, 255, 0), -1)
        cv2.putText(annotated, f"ID{objectID}", 
                   (centroid[0] + 15, centroid[1]),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Save
    cv2.imwrite("output/debug_frame_detailed.jpg", annotated)
    print(f"\n✅ Saved: output/debug_frame_detailed.jpg")
    print(f"\n{'='*80}")
    print("🔍 ANALYSIS COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    debug_frame_detailed()

