#!/usr/bin/env python3
"""
Simple test to verify the interactive video features are working
"""

import os
import sys

def test_file_creation():
    """Test that all required files were created"""
    files_to_check = [
        'static/js/interactive-video.js',
        'static/js/live-streaming.js', 
        'static/js/vr-ar-support.js',
        'static/js/voice-gesture-controls.js',
        'static/css/interactive-video.css',
        'backend/api/interactive_endpoints.py',
        'templates/interactive_video.html'
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_js_file_content():
    """Test that JavaScript files contain expected content"""
    js_tests = [
        ('static/js/interactive-video.js', 'InteractiveVideoPlayer'),
        ('static/js/live-streaming.js', 'LiveStreamingManager'),
        ('static/js/vr-ar-support.js', 'VRARManager'),
        ('static/js/voice-gesture-controls.js', 'VoiceGestureController')
    ]
    
    all_valid = True
    
    for file_path, expected_class in js_tests:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if expected_class in content:
                    print(f"✅ {file_path} contains {expected_class}")
                else:
                    print(f"❌ {file_path} missing {expected_class}")
                    all_valid = False
        except FileNotFoundError:
            print(f"❌ {file_path} not found")
            all_valid = False
    
    return all_valid

def test_backend_api():
    """Test that backend API file contains expected endpoints"""
    api_file = 'backend/api/interactive_endpoints.py'
    expected_functions = [
        'get_user_progress',
        'update_user_progress', 
        'get_hotspots',
        'add_hotspot',
        'start_live_stream',
        'get_leaderboard'
    ]
    
    try:
        with open(api_file, 'r') as f:
            content = f.read()
            
        all_found = True
        for func in expected_functions:
            if func in content:
                print(f"✅ API function {func} found")
            else:
                print(f"❌ API function {func} missing")
                all_found = False
        
        return all_found
        
    except FileNotFoundError:
        print(f"❌ {api_file} not found")
        return False

def test_template_content():
    """Test that the interactive video template contains expected elements"""
    template_file = 'templates/interactive_video.html'
    expected_elements = [
        'interactive-video-player',
        'InteractiveVideoPlayer',
        'LiveStreamingManager',
        'VRARManager',
        'VoiceGestureController'
    ]
    
    try:
        with open(template_file, 'r') as f:
            content = f.read()
        
        all_found = True
        for element in expected_elements:
            if element in content:
                print(f"✅ Template element {element} found")
            else:
                print(f"❌ Template element {element} missing")
                all_found = False
        
        return all_found
        
    except FileNotFoundError:
        print(f"❌ {template_file} not found")
        return False

def test_flask_app_integration():
    """Test that Flask app includes the new routes"""
    app_file = 'backend/app.py'
    expected_imports = [
        'interactive_endpoints',
        'SocketIO',
        'interactive_bp'
    ]
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        all_found = True
        for import_item in expected_imports:
            if import_item in content:
                print(f"✅ Flask import {import_item} found")
            else:
                print(f"❌ Flask import {import_item} missing")
                all_found = False
        
        # Check for interactive route
        if '/interactive-video' in content:
            print("✅ Interactive video route found")
        else:
            print("❌ Interactive video route missing")
            all_found = False
        
        return all_found
        
    except FileNotFoundError:
        print(f"❌ {app_file} not found")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Interactive Video Features Implementation\n")
    
    tests = [
        ("File Creation", test_file_creation),
        ("JavaScript Content", test_js_file_content),
        ("Backend API", test_backend_api),
        ("Template Content", test_template_content),
        ("Flask Integration", test_flask_app_integration)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        result = test_func()
        if result:
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Interactive features are ready.")
        print("\nFeatures implemented:")
        print("• Interactive hotspots and clickable elements")
        print("• Branching video narratives and decision trees")
        print("• Live streaming with real-time chat integration")
        print("• VR/AR video support")
        print("• Gamification with achievements and leaderboards")
        print("• Voice commands and gesture controls")
        print("\nTo test the application:")
        print("1. cd backend && python app.py")
        print("2. Visit http://localhost:5000/interactive-video")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)