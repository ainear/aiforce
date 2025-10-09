import io
from flask import send_file, jsonify
from utils.supabase_storage import SupabaseStorage

def process_and_respond(result_image, feature_type='general', save_to_storage=False, user_id=None):
    """
    Helper to process AI result image and return appropriate response
    
    Args:
        result_image: PIL Image object
        feature_type: Type of AI feature (for storage naming)
        save_to_storage: If True, save to Supabase and return JSON with URL
        user_id: Optional user ID for organizing files
    
    Returns:
        Flask response (image bytes or JSON with URL)
    """
    
    # If save_to_storage is requested, upload to Supabase
    if save_to_storage:
        storage = SupabaseStorage()
        upload_result = storage.upload_image(result_image, user_id, feature_type)
        
        if upload_result['success']:
            # Return JSON with image URL
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            
            return jsonify({
                'success': True,
                'message': 'Image processed and saved',
                'storage_url': upload_result['url'],
                'filename': upload_result['filename'],
                'path': upload_result['path']
            })
        else:
            # Storage failed, still return image bytes
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
    
    # Default: return image bytes
    output = io.BytesIO()
    result_image.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')
