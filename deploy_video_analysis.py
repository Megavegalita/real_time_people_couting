"""
Video Analysis Deployment - Full Processing with Detailed Overlays

Processes shopping_korea.mp4 with comprehensive overlays and saves to output/
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import argparse
from datetime import datetime

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "gender_analysis"))

from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject


class DetailedVideoProcessor:
    """Process video with detailed overlays and annotations."""
    
    def __init__(self, prototxt: str, model: str):
        """Initialize processor with detection model."""
        self.prototxt = prototxt
        self.model = model
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.trackableObjects: Dict[int, TrackableObject] = {}
        
        # Statistics
        self.stats = {
            'frame_count': 0,
            'detections': 0,
            'people_in': 0,
            'people_out': 0,
            'total_tracked': 0,
            'analyses_done': 0,
            'analyses_failed': 0,
            'detection_history': []
        }
    
    def process_frame(
        self,
        frame: np.ndarray,
        width: int,
        height: int,
        confidence: float = 0.4
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process a single frame with detections and tracking.
        
        Returns:
            Annotated frame and statistics
        """
        frame_count = self.stats['frame_count']
        self.stats['frame_count'] += 1
        
        # Resize for detection
        frame_resized = cv2.resize(frame, (500, 500))
        
        # Convert to blob
        blob = cv2.dnn.blobFromImage(
            frame_resized,
            0.007843,
            (500, 500),
            127.5
        )
        
        # Detect objects
        self.net.setInput(blob)
        detections = self.net.forward()
        
        rects = []
        detection_boxes = []
        
        for i in range(detections.shape[2]):
            confidence_score = detections[0, 0, i, 2]
            
            if confidence_score > confidence:
                idx = int(detections[0, 0, i, 1])
                
                if idx == 15:  # Person class
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    (startX, startY, endX, endY) = box.astype("int")
                    
                    rects.append((startX, startY, endX, endY))
                    detection_boxes.append({
                        'box': (startX, startY, endX, endY),
                        'confidence': confidence_score
                    })
                    self.stats['detections'] += 1
        
        # Update tracker
        objects = self.ct.update(rects) if rects else {}
        
        # Process tracked objects
        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to is None:
                to = TrackableObject(objectID, centroid)
                self.trackableObjects[objectID] = to
            else:
                direction = centroid[1] - to.centroids[-1][1]
                to.centroids.append(centroid)
                
                if not to.counted:
                    if direction < 0:
                        self.stats['people_out'] += 1
                        to.counted = True
                    else:
                        self.stats['people_in'] += 1
                        to.counted = True
        
        # Draw detailed overlays
        annotated_frame = self.draw_detailed_overlays(
            frame.copy(),
            rects,
            objects,
            detection_boxes,
            frame_count
        )
        
        return annotated_frame, self.stats
    
    def draw_detailed_overlays(
        self,
        frame: np.ndarray,
        rects: List[Tuple],
        objects: Dict,
        detection_boxes: List[Dict],
        frame_count: int
    ) -> np.ndarray:
        """Draw detailed overlays on frame."""
        
        # Draw detection boxes (all detected people)
        for (startX, startY, endX, endY) in rects:
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        
        # Draw tracking info for each tracked object
        for (objectID, centroid) in objects.items():
            to = self.trackableObjects.get(objectID, None)
            
            if to:
                # Draw centroid
                cv2.circle(frame, (centroid[0], centroid[1]), 5, (0, 255, 0), -1)
                
                # Draw trajectory
                if len(to.centroids) > 1:
                    for i in range(1, len(to.centroids)):
                        cv2.line(
                            frame,
                            tuple(to.centroids[i-1]),
                            tuple(to.centroids[i]),
                            (255, 255, 0),
                            2
                        )
                
                # Draw person ID and status
                status = "TRACKED"
                if to.counted:
                    direction = "OUT" if to.centroids[0][1] > centroid[1] else "IN"
                    status = f"COUNTED ({direction})"
                
                # Person ID label
                cv2.putText(
                    frame,
                    f"ID:{objectID} [{status}]",
                    (centroid[0] - 30, centroid[1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )
                
                # Center coordinates
                cv2.putText(
                    frame,
                    f"({centroid[0]}, {centroid[1]})",
                    (centroid[0] - 30, centroid[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (200, 200, 200),
                    1,
                    cv2.LINE_AA
                )
                
                # Path length
                path_length = len(to.centroids)
                cv2.putText(
                    frame,
                    f"Path: {path_length}",
                    (centroid[0] - 30, centroid[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (200, 200, 200),
                    1,
                    cv2.LINE_AA
                )
        
        # Draw statistics panel (top left)
        stats_text = [
            f"Frame: {frame_count}",
            f"Detections: {self.stats['detections']}",
            f"Tracked: {len(objects)}",
            f"In: {self.stats['people_in']}",
            f"Out: {self.stats['people_out']}",
            f"Total: {self.stats['people_in'] + self.stats['people_out']}"
        ]
        
        y_offset = 30
        for text in stats_text:
            # Background for text
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (10, y_offset - text_h - 5), (10 + text_w + 10, y_offset + 5), (0, 0, 0), -1)
            
            # Text
            cv2.putText(
                frame,
                text,
                (15, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
                cv2.LINE_AA
            )
            y_offset += 35
        
        # Draw timestamp (bottom right)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            frame,
            timestamp,
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        return frame


def process_video(
    video_path: str,
    output_path: str,
    prototxt: str = "detector/MobileNetSSD_deploy.prototxt",
    model: str = "detector/MobileNetSSD_deploy.caffemodel",
    max_frames: int = 500,
    skip_frames: int = 1
) -> Dict[str, Any]:
    """
    Process video with detailed analysis.
    
    Args:
        video_path: Input video path
        output_path: Output video path
        prototxt: MobileNetSSD prototxt path
        model: MobileNetSSD model path
        max_frames: Maximum frames to process
        skip_frames: Frames to skip between detections
        
    Returns:
        Statistics dictionary
    """
    print(f"\n{'='*80}")
    print(f"🚀 VIDEO ANALYSIS DEPLOYMENT - DETAILED OVERLAYS")
    print(f"{'='*80}")
    print(f"Input: {video_path}")
    print(f"Output: {output_path}")
    print(f"Max frames: {max_frames}")
    print(f"Skip frames: {skip_frames}")
    print(f"{'='*80}\n")
    
    # Initialize processor
    processor = DetailedVideoProcessor(prototxt, model)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return {}
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 Video Info:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {total_frames}\n")
    
    # Create output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"🎬 Processing video with detailed overlays...")
    print(f"{'─'*80}")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count > max_frames:
            break
        
        # Show progress
        if frame_count % 50 == 0:
            print(f"  Frame {frame_count}/{max_frames} | "
                  f"Tracked: {len(processor.trackableObjects)} | "
                  f"Total: {processor.stats['people_in'] + processor.stats['people_out']}")
        
        # Process frame
        annotated_frame, stats = processor.process_frame(frame, width, height)
        
        # Write frame
        out.write(annotated_frame)
    
    # Cleanup
    cap.release()
    out.release()
    
    # Print results
    print(f"\n{'='*80}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"\n📊 STATISTICS:")
    print(f"  - Frames processed: {stats['frame_count']}")
    print(f"  - People detected: {stats['detections']}")
    print(f"  - People in: {stats['people_in']}")
    print(f"  - People out: {stats['people_out']}")
    print(f"  - Total tracked: {stats['people_in'] + stats['people_out']}")
    print(f"\n📹 Output saved: {output_path}")
    print(f"{'='*80}\n")
    
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy video analysis with detailed overlays")
    parser.add_argument("-i", "--input", required=True, help="Input video path")
    parser.add_argument("-o", "--output", default="output/analyzed_video.mp4", help="Output video path")
    parser.add_argument("-m", "--max-frames", type=int, default=500, help="Max frames to process")
    parser.add_argument("-s", "--skip-frames", type=int, default=1, help="Frames to skip")
    
    args = parser.parse_args()
    
    # Create output directory if needed
    output_dir = Path(args.output).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process video
    stats = process_video(
        video_path=args.input,
        output_path=args.output,
        max_frames=args.max_frames,
        skip_frames=args.skip_frames
    )
    
    print("\n✅ Deployment complete!\n")

