"""
Example endpoints with Supabase Storage integration
Copy these into app.py to enable storage features
"""

# Add this import at the top of app.py
# from utils.supabase_storage import SupabaseStorage
# from utils.response_helper import process_and_respond

# Example: HD Upscale with Storage Option
@app.route('/api/ai/hd-image-storage', methods=['POST'])
def hd_image_with_storage():
    """
    Upscale image and save to Supabase Storage
    
    Query params:
    - save_storage=true : Save to Supabase and return URL
    - user_id=xxx : Optional user ID for organizing files
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        scale = int(request.form.get('scale', '2'))
        save_to_storage = request.form.get('save_storage', 'false').lower() == 'true'
        user_id = request.form.get('user_id', None)
        
        image = Image.open(file.stream)
        
        # Process with Replicate
        try:
            result_image = replicate_processor.upscale_image(image, scale=scale)
        except Exception as e:
            # Fallback to HuggingFace
            image_bytes = image_to_bytes(image)
            response = query_huggingface_model("caidas/swin2SR-classical-sr-x2-64", image_bytes)
            if response.status_code != 200:
                return jsonify({'error': 'Image processing failed'}), 500
            result_image = Image.open(io.BytesIO(response.content))
        
        # Use helper to respond (with or without storage)
        return process_and_respond(
            result_image, 
            feature_type='hd-upscale', 
            save_to_storage=save_to_storage,
            user_id=user_id
        )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Example: Face Swap with Storage
@app.route('/api/ai/swap-face-storage', methods=['POST'])
def swap_face_with_storage():
    """Face swap with option to save to Supabase"""
    try:
        if 'source_image' not in request.files or 'target_image' not in request.files:
            return jsonify({'error': 'Both source_image and target_image required'}), 400
        
        source_file = request.files['source_image']
        target_file = request.files['target_image']
        save_to_storage = request.form.get('save_storage', 'false').lower() == 'true'
        user_id = request.form.get('user_id', None)
        
        source_image = Image.open(source_file.stream)
        target_image = Image.open(target_file.stream)
        
        # Try Replicate first
        try:
            result_image = replicate_processor.swap_face(source_image, target_image)
        except Exception as e:
            # Fallback to HuggingFace
            return jsonify({'error': 'Face swap failed'}), 500
        
        # Respond with or without storage
        return process_and_respond(
            result_image,
            feature_type='face-swap',
            save_to_storage=save_to_storage,
            user_id=user_id
        )
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Example: Get user's saved images
@app.route('/api/storage/list/<user_id>', methods=['GET'])
def list_user_images(user_id):
    """List all saved images for a user"""
    storage = SupabaseStorage()
    files = storage.list_user_images(user_id)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'images': files
    })


# Example: Delete saved image
@app.route('/api/storage/delete', methods=['POST'])
def delete_saved_image():
    """Delete image from Supabase Storage"""
    filepath = request.json.get('filepath')
    
    if not filepath:
        return jsonify({'error': 'filepath required'}), 400
    
    storage = SupabaseStorage()
    result = storage.delete_image(filepath)
    
    return jsonify(result)
