#!/usr/bin/env python3
"""
Debug script to check gender estimation in first 20 frames.
"""

import cv2
import sys
sys.path.insert(0, '/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting')

from production_body_focused import BodyFocusedSystem
import numpy as np

def debug_first_20_frames():
    """Check gender estimation in first 20 seconds."""
    
    system = BodyFocusedSystem()
    video_path = "/Users/autoeyes/Project/autoeyes/vision_ai/real_time_people_couting/utils/data/tests/shopping_korea.mp4"
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Failed to open video")
        return
    
    print("\n" + "="*80)
    print("🔍 DEBUGGING FIRST 20 FRAMES")
    print("="*80 + "\n")
    
    frame_idx = 0
    max_frames = 500  # ~20 seconds @ 25fps
    
    while frame_idx < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        body_boxes = system.detect_bodies_yolo(frame)
        
        if body_boxes:
            body_boxes = system.merge_overlapping_boxes(body_boxes)
            boxes = body_boxes if isinstance(body_boxes[0], tuple) else [box['bbox'] for box in body_boxes]
            tracked_objects = system.ct.update(boxes)
            
            # Create mapping
            if len(boxes) > 0 and len(tracked_objects) > 0:
                distance_matrix = np.zeros((len(tracked_objects), len(boxes)))
                object_list = list(tracked_objects.keys())
                
                for i, (objectID, centroid) in enumerate(tracked_objects.items()):
                    for j, box in enumerate(boxes):
                        x, y, w_box, h_box = box
                        box_center = (x + w_box // 2, y + h_box // 2)
                        distance_matrix[i, j] = np.sqrt(
                            (centroid[0] - box_center[0])**2 + 
                            (centroid[1] - box_center[1])**2
                        )
                
                object_to_box_map = {}
                used_boxes = set()
                
                for object_idx, objectID in enumerate(object_list):
                    best_box_idx = None
                    best_distance = float('inf')
                    
                    for box_idx in range(len(boxes)):
                        if box_idx not in used_boxes:
                            dist = distance_matrix[object_idx, box_idx]
                            if dist < best_distance:
                                best_distance = dist
                                best_box_idx = box_idx
                    
                    if best_box_idx is not None:
                        object_to_box_map[objectID] = best_box_idx
                        used_boxes.add(best_box_idx)
            
            # Check for new analyses
            for (objectID, centroid) in tracked_objects.items():
                if objectID in object_to_box_map:
                    box_idx = object_to_box_map[objectID]
                    x, y, w_box, h_box = boxes[box_idx]
                    
                    if objectID not in system.person_data:
                        # This is new detection - will be analyzed
                        person_crop = frame[y:y+h_box, x:x+w_box]
                        h, w = person_crop.shape[:2]
                        area = h * w
                        aspect_ratio = h / w if w > 0 else 0
                        
                        print(f"\n🎯 Frame {frame_idx}: NEW PERSON (ID: {objectID})")
                        print(f"   Crop: {w}x{h} (area: {area}, aspect: {aspect_ratio:.2f})")
                        
                        if system.should_re_analyze(objectID, frame_idx):
                            result = system.estimate_from_body_features(
                                person_crop, objectID, frame_idx
                            )
                            print(f"   Gender: {result['gender']} (votes: M={result['male_votes']}, F={result['female_votes']})")
                            print(f"   Age: {result['age']}")
                            
                            # Save debug image
                            debug_img = cv2.rectangle(frame.copy(), (x, y), (x+w_box, y+h_box), (0, 255, 255), 3)
                            cv2.putText(debug_img, f"ID{objectID}: {result['gender']}", (x, y-10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                            cv2.imwrite(f"output/debug_frame_{frame_idx}_id{objectID}.jpg", debug_img)
        
        frame_idx += 1
        
        if frame_idx % 50 == 0:
            print(f"Frame {frame_idx}...")
    
    cap.release()
    print("\n✅ Debug complete!")
    print(f"📁 Debug images saved in: output/")

if __name__ == "__main__":
    debug_first_20_frames()

