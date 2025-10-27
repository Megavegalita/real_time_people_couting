"""
Integration Test - Gender & Age Analysis with Real Video

Tests the complete system with shopping_korea.mp4 video.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from core.services.classification import analysis_service
from core.services.face_processing import FaceProcessor
from core.utils.queue_manager import TaskQueue


def process_video_with_gender_age(
    video_path: str,
    output_path: str = "output_with_gender_age.mp4",
    max_frames: int = 100
) -> Dict[str, Any]:
    """
    Process video with gender and age analysis.
    
    Args:
        video_path: Path to input video
        output_path: Path to output video
        max_frames: Maximum frames to process (for testing)
        
    Returns:
        Statistics dictionary
    """
    print(f"\n{'='*60}")
    print(f"🚀 Testing Gender & Age Analysis System")
    print(f"{'='*60}")
    print(f"Input video: {video_path}")
    print(f"Max frames: {max_frames}")
    print(f"{'='*60}\n")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video {video_path}")
        return {}
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📹 Video Info:")
    print(f"  - Resolution: {width}x{height}")
    print(f"  - FPS: {fps}")
    print(f"  - Total frames: {total_frames}")
    print()
    
    # Create output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Statistics
    stats = {
        'total_frames': 0,
        'frames_with_faces': 0,
        'faces_detected': 0,
        'gender_male': 0,
        'gender_female': 0,
        'age_total': 0,
        'age_sum': 0,
        'errors': 0
    }
    
    # Person tracking (simple version)
    person_count = 0
    processed_persons = set()
    
    frame_count = 0
    
    print(f"🎬 Processing video...")
    print(f"{'─'*60}")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count > max_frames:
            break
        
        if frame_count % 30 == 0:
            print(f"  Processing frame {frame_count}/{total_frames}...")
        
        # Simulate person detection (using face detection)
        face_processor = FaceProcessor()
        face_results = face_processor.process_frame(frame)
        
        if len(face_results) > 0:
            stats['frames_with_faces'] += 1
            
            for face_crop, face_info in face_results:
                stats['faces_detected'] += 1
                person_id = frame_count * 1000 + len(stats['faces_detected'])
                
                # Get face bounding box
                bbox = face_info.get('box', (0, 0, 0, 0))
                x, y, w, h = bbox
                
                # Analyze person (gender & age)
                try:
                    # For testing, we need to simulate person crop
                    # Extract the face region from frame
                    person_crop = face_crop  # Already cropped
                    
                    # Create a simple mock bbox for full frame
                    full_bbox = (max(0, x - 50), max(0, y - 50), w + 100, h + 100)
                    
                    # Note: In real implementation, this would integrate with
                    # existing person detection from MobileNetSSD
                    # For now, we're using face detection as a demo
                    
                    # Try to analyze if we have a valid crop
                    if person_crop is not None and person_crop.size > 0:
                        # Run analysis
                        result = analysis_service.analyze_person(
                            frame=frame,
                            person_id=person_id,
                            bbox=(x, y, w, h),
                            camera_id="test_camera"
                        )
                        
                        if result.get('status') == 'success':
                            # Update statistics
                            if result['gender'] == 'male':
                                stats['gender_male'] += 1
                            elif result['gender'] == 'female':
                                stats['gender_female'] += 1
                            
                            stats['age_sum'] += result['age']
                            stats['age_total'] += 1
                            
                            # Draw results on frame
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            label = f"{result['gender']}, {result['age']}y"
                            cv2.putText(frame, label, (x, y-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            stats['errors'] += 1
                    else:
                        stats['errors'] += 1
                        
                except Exception as e:
                    print(f"  ⚠️  Error analyzing person: {e}")
                    stats['errors'] += 1
        
        # Write frame to output
        out.write(frame)
        stats['total_frames'] += 1
    
    # Cleanup
    cap.release()
    out.release()
    
    # Print statistics
    print(f"\n{'='*60}")
    print(f"✅ Processing Complete!")
    print(f"{'='*60}")
    print(f"📊 Statistics:")
    print(f"  - Frames processed: {stats['total_frames']}")
    print(f"  - Frames with faces: {stats['frames_with_faces']}")
    print(f"  - Faces detected: {stats['faces_detected']}")
    print(f"  - Male detected: {stats['gender_male']}")
    print(f"  - Female detected: {stats['gender_female']}")
    if stats['age_total'] > 0:
        print(f"  - Average age: {stats['age_sum']/stats['age_total']:.1f}")
    print(f"  - Errors: {stats['errors']}")
    print(f"{'='*60}")
    
    return stats


if __name__ == "__main__":
    video_path = "../../utils/data/tests/shopping_korea.mp4"
    
    print("\n" + "="*60)
    print("🧪 GENDER & AGE ANALYSIS INTEGRATION TEST")
    print("="*60)
    
    # Run test
    stats = process_video_with_gender_age(
        video_path=video_path,
        output_path="output_gender_age_test.mp4",
        max_frames=100  # Test with first 100 frames
    )
    
    print("\n✅ Test complete!")
    print(f"📹 Output video: output_gender_age_test.mp4")
    print()

