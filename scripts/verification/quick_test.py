#!/usr/bin/env python3
"""
Quick Test Script
=================

Simple test to verify code can run without errors.
"""

import sys
import os

def test_imports():
    """Test if all imports work correctly."""
    print("🔍 Testing imports...")
    
    try:
        from tracker.centroidtracker import CentroidTracker
        print("  ✅ tracker.centroidtracker")
    except Exception as e:
        print(f"  ❌ tracker.centroidtracker: {e}")
        return False
    
    try:
        from tracker.trackableobject import TrackableObject
        print("  ✅ tracker.trackableobject")
    except Exception as e:
        print(f"  ❌ tracker.trackableobject: {e}")
        return False
    
    try:
        from utils.thread import ThreadingClass
        print("  ✅ utils.thread")
    except Exception as e:
        print(f"  ❌ utils.thread: {e}")
        return False
    
    try:
        from utils.mailer import Mailer
        print("  ✅ utils.mailer")
    except Exception as e:
        print(f"  ❌ utils.mailer: {e}")
        return False
    
    try:
        from constants import Tracking, Detection, CLASSES
        print("  ✅ constants")
    except Exception as e:
        print(f"  ❌ constants: {e}")
        return False
    
    return True


def test_types():
    """Test if type hints work correctly."""
    print("\n🔍 Testing type hints...")
    
    try:
        from tracker.centroidtracker import CentroidTracker
        from tracker.trackableobject import TrackableObject
        
        # Test type hints
        tracker = CentroidTracker(maxDisappeared=40, maxDistance=50)
        print("  ✅ CentroidTracker types work")
        
        obj = TrackableObject(objectID=1, centroid=(100, 200))
        print("  ✅ TrackableObject types work")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Type hints error: {e}")
        return False


def test_functions():
    """Test if main functions can be called."""
    print("\n🔍 Testing function signatures...")
    
    try:
        import people_counter
        
        # Check if functions exist
        assert hasattr(people_counter, 'parse_arguments')
        assert hasattr(people_counter, 'send_mail')
        assert hasattr(people_counter, 'log_data')
        assert hasattr(people_counter, 'people_counter')
        
        print("  ✅ All functions exist")
        
        # Check return type annotations (will fail if imports broken)
        import inspect
        sig = inspect.signature(people_counter.parse_arguments)
        assert sig.return_annotation != inspect.Parameter.empty
        print("  ✅ Function annotations work")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Function test error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  QUICK VERIFICATION TEST")
    print("="*60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test types
    if not test_types():
        all_passed = False
    
    # Test functions
    if not test_functions():
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("  ✅ ALL TESTS PASSED")
        print("="*60)
        print("\n🎉 Code optimization successful!")
        print("   - All imports work")
        print("   - Type hints work")
        print("   - Functions accessible")
        print("\n📊 Ready for full verification:")
        print("   python comprehensive_verification.py")
        return True
    else:
        print("  ❌ SOME TESTS FAILED")
        print("="*60)
        print("\n⚠️  Please check error messages above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

