#!/bin/bash

# Activate virtual environment and run the people counter
source venv/bin/activate

# Default to webcam (config.json: url="0")
if [ -z "$1" ]; then
    echo "Starting people counter with webcam..."
    python people_counter.py \
        --prototxt detector/MobileNetSSD_deploy.prototxt \
        --model detector/MobileNetSSD_deploy.caffemodel
elif [ "$1" = "video" ]; then
    VIDEO_FILE="$2"
    if [ -z "$VIDEO_FILE" ]; then
        VIDEO_FILE="utils/data/tests/test_1.mp4"
    fi
    echo "Starting people counter with video file: $VIDEO_FILE"
    python people_counter.py \
        --prototxt detector/MobileNetSSD_deploy.prototxt \
        --model detector/MobileNetSSD_deploy.caffemodel \
        --input "$VIDEO_FILE"
elif [ "$1" = "help" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: ./run.sh [mode]"
    echo ""
    echo "Modes:"
    echo "  (no args)  - Run with webcam (default)"
    echo "  video      - Run with video file (default: utils/data/tests/test_1.mp4)"
    echo "  video <path> - Run with specific video file"
    echo "  help       - Show this help message"
else
    echo "Unknown mode: $1"
    echo "Use './run.sh help' for usage information"
fi

