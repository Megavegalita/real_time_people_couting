#!/bin/bash

# Quick Verification Script
# Tests optimized code with a short video

set -e  # Exit on error

echo "========================================"
echo "Quick Verification Test"
echo "========================================"

# Activate venv
source venv/bin/activate

echo ""
echo "Testing optimized people_counter.py..."
echo "Command: python people_counter.py --prototxt detector/MobileNetSSD_deploy.prototxt --model detector/MobileNetSSD_deploy.caffemodel --input utils/data/tests/test_1.mp4 --confidence 0.4 --skip-frames 30"
echo ""

# Run with timeout to avoid hanging
timeout 60 python people_counter.py \
    --prototxt detector/MobileNetSSD_deploy.prototxt \
    --model detector/MobileNetSSD_deploy.caffemodel \
    --input utils/data/tests/test_1.mp4 \
    --confidence 0.4 \
    --skip-frames 30 \
    || echo "❌ Test failed or timed out"

echo ""
echo "✅ Test completed"
echo ""

