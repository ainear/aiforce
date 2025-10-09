#!/usr/bin/env python3
"""
Test Supabase connection and storage upload
"""
import os
from PIL import Image
from utils.supabase_storage import SupabaseStorage

def test_supabase():
    print("🔍 Testing Supabase Connection...")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')[:30]}..." if os.getenv('SUPABASE_URL') else "SUPABASE_URL: Not found")
    print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:30]}..." if os.getenv('SUPABASE_KEY') else "SUPABASE_KEY: Not found")
    print()
    
    # Initialize storage
    storage = SupabaseStorage()
    
    if not storage.client:
        print("❌ Supabase client not initialized. Check credentials!")
        return False
    
    print("✅ Supabase client initialized successfully!")
    
    # Create a test image
    print("\n📸 Creating test image...")
    test_image = Image.new('RGB', (100, 100), color='red')
    
    # Test upload
    print("📤 Testing upload to Supabase Storage...")
    result = storage.upload_image(
        test_image,
        user_id='test-user',
        feature_type='connection-test'
    )
    
    if result['success']:
        print("✅ Upload successful!")
        print(f"   URL: {result['url']}")
        print(f"   Path: {result['path']}")
        print(f"   Filename: {result['filename']}")
        
        # Test delete
        print("\n🗑️  Testing delete...")
        delete_result = storage.delete_image(result['path'])
        if delete_result['success']:
            print("✅ Delete successful!")
        else:
            print(f"❌ Delete failed: {delete_result.get('error')}")
        
        return True
    else:
        print(f"❌ Upload failed: {result.get('error')}")
        return False

if __name__ == "__main__":
    success = test_supabase()
    
    if success:
        print("\n🎉 All Supabase tests passed!")
        print("\n📝 Next steps:")
        print("1. ✅ Supabase is connected")
        print("2. 👉 Add storage endpoints to app.py")
        print("3. 👉 Test from Flutter app")
    else:
        print("\n❌ Supabase test failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Check if SUPABASE_URL and SUPABASE_KEY are set in Secrets")
        print("2. Check if 'ai-photos' bucket exists in Supabase")
        print("3. Check if bucket is set to PUBLIC")
