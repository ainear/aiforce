#!/usr/bin/env python3
"""
Test API endpoint with Supabase Storage
"""
import requests
from PIL import Image
import io

# Create a test image
print("📸 Creating test image...")
test_image = Image.new('RGB', (200, 200), color='blue')
img_bytes = io.BytesIO()
test_image.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Test endpoint
url = 'http://localhost:5000/api/ai/process-and-save'

print("\n🧪 Test 1: Process WITHOUT storage (return image bytes)")
print("-" * 50)
files = {'image': ('test.png', img_bytes, 'image/png')}
data = {
    'feature': 'cartoonify',
    'style': 'anime',
    'save_storage': 'false'  # Don't save to storage
}

response = requests.post(url, files=files, data=data)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
if response.status_code == 200:
    print(f"✅ Success! Received image ({len(response.content)} bytes)")
else:
    print(f"❌ Failed: {response.text}")

# Reset image bytes
img_bytes.seek(0)

print("\n🧪 Test 2: Process WITH storage (save to Supabase)")
print("-" * 50)
files = {'image': ('test.png', img_bytes, 'image/png')}
data = {
    'feature': 'cartoonify',
    'style': 'anime',
    'save_storage': 'true',  # Save to Supabase
    'user_id': 'demo-user-123'
}

response = requests.post(url, files=files, data=data)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")

if response.status_code == 200:
    result = response.json()
    print(f"✅ Success!")
    print(f"   Message: {result.get('message')}")
    print(f"   Storage URL: {result.get('storage_url')}")
    print(f"   Filename: {result.get('filename')}")
    print(f"   Path: {result.get('path')}")
    
    # Test if URL is accessible
    print(f"\n🔗 Testing if URL is publicly accessible...")
    storage_url = result.get('storage_url')
    if storage_url:
        url_response = requests.get(storage_url)
        if url_response.status_code == 200:
            print(f"✅ Image is publicly accessible!")
            print(f"   Image size: {len(url_response.content)} bytes")
        else:
            print(f"❌ Image not accessible (status {url_response.status_code})")
else:
    print(f"❌ Failed: {response.text}")

print("\n" + "=" * 50)
print("🎉 Test completed!")
print("\n📝 New Endpoint Available:")
print("   POST /api/ai/process-and-save")
print("   - Parameters:")
print("     • image (file): Image to process")
print("     • feature (text): hd-upscale, cartoonify, restore, remove-bg")
print("     • save_storage (text): 'true' to save to Supabase")
print("     • user_id (text): Optional user ID")
print("     • scale/style: Feature-specific params")
