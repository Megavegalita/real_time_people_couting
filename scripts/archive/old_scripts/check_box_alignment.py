"""
Check box alignment - verify which box corresponds to which overlay
"""

import cv2
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker

# Capture frame 13
cap = cv2.VideoCapture("utils/data/tests/shopping_korea.mp4")
cap.set(cv2.CAP_PROP_POS_FRAMES, 13)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Failed to read frame")
    exit()

h, w = frame.shape[:2]
annotated = frame.copy()

# Detect
net = cv2.dnn.readNetFromCaffe(
    "detector/MobileNetSSD_deploy.prototxt",
    "detector/MobileNetSSD_deploy.caffemodel"
)

frame_resized = cv2.resize(frame, (500, 500))
blob = cv2.dnn.blobFromImage(frame_resized, 0.007843, (500, 500), 127.5)
net.setInput(blob)
detections = net.forward()

boxes = []
boxes_full_info = []
for i in range(detections.shape[2]):
    conf = detections[0, 0, i, 2]
    idx = int(detections[0, 0, i, 1])
    
    if conf > 0.4 and idx == 15:
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (px1, py1, px2, py2) = box.astype("int")
        boxes.append((px1, py1, px2 - px1, py2 - py1))
        boxes_full_info.append({
            'bbox': (px1, py1, px2 - px1, py2 - py1),
            'detection_idx': i,
            'confidence': conf
        })

print(f"Found {len(boxes)} people detected\n")

# Track
ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
objects = ct.update(boxes)

print(f"Tracker returns {len(objects)} objects\n")

# Show each box and label with index
for idx, box_info in enumerate(boxes_full_info):
    x, y, w_box, h_box = box_info['bbox']
    
    # Find corresponding objectID
    box_center = (x + w_box // 2, y + h_box // 2)
    
    # Draw box in different colors
    color = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)][idx % 4]
    
    cv2.rectangle(annotated, (x, y), (x+w_box, y+h_box), color, 3)
    
    # Label
    label = f"Box{idx}"
    for (objectID, centroid) in objects.items():
        distance = np.sqrt((centroid[0] - box_center[0])**2 + 
                           (centroid[1] - box_center[1])**2)
        if distance < 10:
            label += f"->ID{objectID}"
            break
    
    cv2.putText(annotated, label, (x+5, y+30),
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)

cv2.imwrite("output/check_box_alignment_frame13.jpg", annotated)
print("Saved: output/check_box_alignment_frame13.jpg\n")

