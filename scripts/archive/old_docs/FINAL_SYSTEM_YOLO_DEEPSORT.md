# Final System Architecture - YOLO + Deep Sort

## Architecture Overview

```
Frame Input
    ↓
YOLO Body Detection (detect people)
    ↓
Deep Sort Tracking (assign IDs, maintain trajectories)
    ↓
YOLO Face Detection (detect faces in tracked persons)
    ↓
Gender/Age Analysis (analyze detected faces)
    ↓
Visualization (draw boxes, labels, overlays)
```

## Components

### 1. YOLO Body Detection
- Model: YOLOv8 (people detection)
- Input: Full frame
- Output: Person bounding boxes
- Advantages: More accurate than MobileNetSSD

### 2. Deep Sort Tracking
- Track objects across frames
- Assign stable IDs
- Maintain trajectories
- Better than CentroidTracker

### 3. YOLO Face Detection
- Model: YOLOv8 or custom face model
- Input: Person crop
- Output: Face bounding box
- More accurate than MediaPipe for small faces

### 4. Gender/Age Analysis
- Only if face detected
- Use visual features or ML model
- Consistent per person

## Implementation Plan

### Step 1: Install YOLO
```bash
pip install ultralytics
```

### Step 2: Download Models
- YOLOv8n.pt (nano) or YOLOv8s.pt (small) for body
- face.pt for face detection (if available)

### Step 3: Integrate Deep Sort
- Already have deep-sort-realtime installed
- Replace CentroidTracker

### Step 4: Workflow
1. YOLO body detection on full frame
2. Deep Sort tracks each person
3. For each tracked person:
   - Extract person crop
   - YOLO face detection
   - If face found → gender/age analysis
4. Draw results

## Advantages

| Component | Before | After |
|-----------|--------|-------|
| Body Detection | MobileNetSSD | YOLOv8 |
| Face Detection | MediaPipe/MTCNN | YOLO Face |
| Tracking | CentroidTracker | Deep Sort |
| Accuracy | Medium | High |
| Speed | Fast | Fast (with GPU) |

## Expected Results

- ✅ More accurate body detection
- ✅ Better face detection for small/distant faces
- ✅ Stable tracking with Deep Sort
- ✅ Proper ID assignment
- ✅ Consistent gender/age per person

