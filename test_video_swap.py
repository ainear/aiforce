#!/usr/bin/env python3
"""
Test script for Video Face Swap API
Tests both HuggingFace Pro and Replicate Pro providers
"""

import requests
import os
import sys
from PIL import Image
import io

# API Configuration
API_URL = "http://localhost:5000"

def test_providers_endpoint():
    """Test GET /api/video/providers"""
    print("\n" + "="*60)
    print("🔍 Testing GET /api/video/providers")
    print("="*60)
    
    response = requests.get(f"{API_URL}/api/video/providers")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"\nProviders available:")
        for provider, info in data.get('providers', {}).items():
            print(f"\n  📦 {provider.upper()}: {info['name']}")
            print(f"     Models: {info.get('models', [])}")
            if 'timeout' in info:
                print(f"     Timeout: {info['timeout']}")
            if 'pricing' in info:
                print(f"     Pricing: {info['pricing']}")
        
        print(f"\n  Supported formats:")
        print(f"     Video: {data.get('supported_formats', {}).get('video', [])}")
        print(f"     Image: {data.get('supported_formats', {}).get('image', [])}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (512, 512), color=(73, 109, 137))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def test_video_face_swap(provider='auto'):
    """Test POST /api/video/face-swap"""
    print("\n" + "="*60)
    print(f"🎬 Testing POST /api/video/face-swap (provider={provider})")
    print("="*60)
    
    # Note: This test requires actual video/image files
    # You need to provide your own test files
    
    test_face_path = "test_face.jpg"
    test_video_path = "test_video.mp4"
    
    if not os.path.exists(test_face_path):
        print(f"⚠️  Test face image not found: {test_face_path}")
        print("   Please provide a test face image (jpg/png)")
        return False
    
    if not os.path.exists(test_video_path):
        print(f"⚠️  Test video not found: {test_video_path}")
        print("   Please provide a test video (mp4/avi/mov)")
        return False
    
    files = {
        'face_image': open(test_face_path, 'rb'),
        'video_file': open(test_video_path, 'rb')
    }
    
    data = {
        'provider': provider,
        'gender': 'all'
    }
    
    print(f"📤 Uploading files...")
    print(f"   Face: {test_face_path}")
    print(f"   Video: {test_video_path}")
    print(f"   Provider: {provider}")
    
    response = requests.post(
        f"{API_URL}/api/video/face-swap",
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON response with URL
            result = response.json()
            print("✅ Success!")
            print(f"   Video URL: {result.get('video_url')}")
            print(f"   Provider used: {result.get('provider')}")
            print(f"   Model used: {result.get('model')}")
            return True
        else:
            # Video file response
            output_path = f"output_video_{provider}.mp4"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print("✅ Success!")
            print(f"   Saved to: {output_path}")
            return True
    else:
        print(f"❌ Failed: {response.status_code}")
        try:
            error = response.json()
            print(f"   Error: {error.get('error')}")
            print(f"   Details: {error.get('details')}")
        except:
            print(response.text)
        return False

def test_video_swap_validation():
    """Test API validation (missing files, invalid format, etc.)"""
    print("\n" + "="*60)
    print("🧪 Testing API Validation")
    print("="*60)
    
    # Test 1: Missing face_image
    print("\n1. Testing missing face_image...")
    response = requests.post(f"{API_URL}/api/video/face-swap")
    if response.status_code == 400:
        print("   ✅ Correctly rejected: missing face_image")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")
    
    # Test 2: Invalid provider
    print("\n2. Testing invalid provider...")
    files = {
        'face_image': create_test_image(),
        'video_file': create_test_image()
    }
    data = {'provider': 'invalid_provider'}
    
    response = requests.post(
        f"{API_URL}/api/video/face-swap",
        files=files,
        data=data
    )
    
    if response.status_code == 400:
        print("   ✅ Correctly rejected: invalid provider")
    else:
        print(f"   ❌ Unexpected response: {response.status_code}")

def main():
    print("\n" + "="*60)
    print("🚀 Video Face Swap API Test Suite")
    print("="*60)
    
    # Test 1: Check providers endpoint
    if not test_providers_endpoint():
        print("\n❌ Providers endpoint failed. Stopping tests.")
        return
    
    # Test 2: Validation tests
    test_video_swap_validation()
    
    # Test 3: Actual video swap (requires test files)
    print("\n" + "="*60)
    print("📝 To test actual video face swap:")
    print("="*60)
    print("1. Place a test face image as: test_face.jpg")
    print("2. Place a test video as: test_video.mp4")
    print("3. Run: python test_video_swap.py --swap")
    print("\nProviders to test:")
    print("  - auto (HF first, fallback to Replicate)")
    print("  - huggingface (HF Pro only)")
    print("  - replicate (Replicate Pro only)")
    
    if '--swap' in sys.argv:
        print("\n🎬 Running actual swap tests...\n")
        
        # Test with auto (HF -> Replicate fallback)
        test_video_face_swap('auto')
        
        # Test with HuggingFace only
        test_video_face_swap('huggingface')
        
        # Test with Replicate only
        test_video_face_swap('replicate')
    
    print("\n" + "="*60)
    print("✨ Test suite completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
