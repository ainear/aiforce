#!/usr/bin/env python3
"""
Simple test: Just upload image to Supabase Storage (no AI processing)
"""
from PIL import Image
from utils.supabase_storage import SupabaseStorage

print("📸 Creating test image...")
test_image = Image.new('RGB', (300, 300), color='green')

print("\n📤 Uploading to Supabase Storage...")
storage = SupabaseStorage()

result = storage.upload_image(
    test_image,
    user_id='demo-user-123',
    feature_type='test-upload'
)

if result['success']:
    print("✅ Upload successful!")
    print(f"   URL: {result['url']}")
    print(f"   Path: {result['path']}")
    print(f"   Filename: {result['filename']}")
    
    # Test if publicly accessible
    import requests
    print(f"\n🔗 Testing if URL is publicly accessible...")
    response = requests.get(result['url'])
    if response.status_code == 200:
        print(f"✅ Image is publicly accessible!")
        print(f"   Image size: {len(response.content)} bytes")
        print(f"\n🌐 You can view the image at:")
        print(f"   {result['url']}")
    else:
        print(f"❌ Not accessible (status {response.status_code})")
    
    # Cleanup
    print(f"\n🗑️  Cleaning up...")
    delete_result = storage.delete_image(result['path'])
    if delete_result['success']:
        print("✅ Test image deleted")
    
else:
    print(f"❌ Upload failed: {result.get('error')}")

print("\n🎉 Storage test completed!")
