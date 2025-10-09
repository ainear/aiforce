import os
import io
from datetime import datetime
from supabase import create_client, Client
from PIL import Image
import uuid

class SupabaseStorage:
    """
    Supabase Storage Manager for AI Photo Editor
    Saves processed images to Supabase Storage bucket
    """
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if self.supabase_url and self.supabase_key:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.client = None
            print("Warning: Supabase credentials not found. Storage disabled.")
    
    def upload_image(self, image, user_id=None, feature_type='general'):
        """
        Upload processed image to Supabase Storage
        
        Args:
            image: PIL Image object
            user_id: Optional user ID for organizing files
            feature_type: Type of AI feature (hd-upscale, face-swap, etc.)
        
        Returns:
            dict with 'success', 'url', 'path'
        """
        if not self.client:
            return {'success': False, 'error': 'Supabase not configured'}
        
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{feature_type}_{timestamp}_{unique_id}.png"
            
            # Add user folder if user_id provided
            if user_id:
                filepath = f"{user_id}/{filename}"
            else:
                filepath = f"public/{filename}"
            
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Upload to Supabase Storage bucket 'ai-photos'
            response = self.client.storage.from_('ai-photos').upload(
                filepath,
                img_byte_arr.read(),
                file_options={"content-type": "image/png"}
            )
            
            # Get public URL
            public_url = self.client.storage.from_('ai-photos').get_public_url(filepath)
            
            return {
                'success': True,
                'url': public_url,
                'path': filepath,
                'filename': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_image_url(self, filepath):
        """Get public URL for stored image"""
        if not self.client:
            return None
        
        return self.client.storage.from_('ai-photos').get_public_url(filepath)
    
    def delete_image(self, filepath):
        """Delete image from storage"""
        if not self.client:
            return {'success': False, 'error': 'Supabase not configured'}
        
        try:
            self.client.storage.from_('ai-photos').remove([filepath])
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_user_images(self, user_id):
        """List all images for a user"""
        if not self.client:
            return []
        
        try:
            files = self.client.storage.from_('ai-photos').list(user_id)
            return files
        except Exception as e:
            print(f"Error listing images: {e}")
            return []
