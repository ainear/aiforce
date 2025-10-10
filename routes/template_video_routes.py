"""
Template Video Face Swap Routes
User uploads face, API swaps into pre-existing template videos
"""

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from utils.video_processor import VideoFaceSwapProcessor

template_video_bp = Blueprint('template_video', __name__)
video_processor = VideoFaceSwapProcessor()

# Template videos directory
TEMPLATES_DIR = os.path.join('static', 'templates', 'videos')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@template_video_bp.route('/list', methods=['GET'])
def list_templates():
    """List all available template videos"""
    try:
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        
        templates = []
        for filename in os.listdir(TEMPLATES_DIR):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                file_path = os.path.join(TEMPLATES_DIR, filename)
                file_size = os.path.getsize(file_path)
                
                templates.append({
                    'id': filename.rsplit('.', 1)[0],  # filename without extension
                    'filename': filename,
                    'url': f'/api/template-video/preview/{filename}',
                    'size': file_size,
                    'size_mb': round(file_size / 1024 / 1024, 2)
                })
        
        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@template_video_bp.route('/preview/<filename>', methods=['GET'])
def preview_template(filename):
    """Serve template video for preview"""
    try:
        return send_from_directory(TEMPLATES_DIR, filename)
    except Exception as e:
        return jsonify({'error': 'Template not found'}), 404

@template_video_bp.route('/swap', methods=['POST'])
def swap_face_with_template():
    """
    Swap user's face into a template video
    
    Form data:
    - face_image: User's face image file
    - template_id: Template video ID (filename without extension)
    - provider: auto/replicate/vmodel (default: auto)
    """
    try:
        # Validate face image
        if 'face_image' not in request.files:
            return jsonify({'error': 'Missing face_image'}), 400
        
        face_image = request.files['face_image']
        
        if not face_image or not allowed_file(face_image.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({'error': 'Invalid face image format'}), 400
        
        # Get template ID
        template_id = request.form.get('template_id')
        if not template_id:
            return jsonify({'error': 'Missing template_id'}), 400
        
        # Find template video file
        template_file = None
        for filename in os.listdir(TEMPLATES_DIR):
            if filename.rsplit('.', 1)[0] == template_id:
                template_file = filename
                break
        
        if not template_file:
            return jsonify({'error': f'Template not found: {template_id}'}), 404
        
        template_path = os.path.join(TEMPLATES_DIR, template_file)
        
        # Get provider
        provider = request.form.get('provider', 'auto')
        if provider not in ['auto', 'replicate', 'vmodel']:
            return jsonify({'error': f'Invalid provider: {provider}'}), 400
        
        print(f"[TemplateAPI] Face swap request: template={template_id}, provider={provider}")
        
        # Open template video as file object
        with open(template_path, 'rb') as video_file:
            # Process video face swap
            result, provider_used, model_used = video_processor.swap_face_video(
                face_image, 
                video_file, 
                provider
            )
        
        return jsonify({
            'success': True,
            'video_url': result,
            'template_id': template_id,
            'template_name': template_file,
            'provider': provider_used,
            'model': model_used,
            'audio_preserved': True
        })
        
    except Exception as e:
        print(f"[TemplateAPI] Error: {e}")
        return jsonify({
            'error': str(e),
            'details': 'Failed to swap face with template'
        }), 500

@template_video_bp.route('/upload-template', methods=['POST'])
def upload_template():
    """
    Upload a new template video (admin feature)
    
    Form data:
    - template_video: Video file
    - template_name: Optional custom name
    """
    try:
        if 'template_video' not in request.files:
            return jsonify({'error': 'Missing template_video'}), 400
        
        template_video = request.files['template_video']
        
        if not template_video or not template_video.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        # Get custom name or use original filename
        custom_name = request.form.get('template_name', '')
        if custom_name:
            filename = secure_filename(custom_name)
            # Ensure it has video extension
            if not filename.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                filename += '.mp4'
        else:
            filename = secure_filename(template_video.filename)
        
        # Save template
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        save_path = os.path.join(TEMPLATES_DIR, filename)
        template_video.save(save_path)
        
        file_size = os.path.getsize(save_path)
        
        return jsonify({
            'success': True,
            'message': 'Template uploaded successfully',
            'template': {
                'id': filename.rsplit('.', 1)[0],
                'filename': filename,
                'url': f'/api/template-video/preview/{filename}',
                'size_mb': round(file_size / 1024 / 1024, 2)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@template_video_bp.route('/delete/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template video (admin feature)"""
    try:
        # Find template file
        template_file = None
        for filename in os.listdir(TEMPLATES_DIR):
            if filename.rsplit('.', 1)[0] == template_id:
                template_file = filename
                break
        
        if not template_file:
            return jsonify({'error': 'Template not found'}), 404
        
        template_path = os.path.join(TEMPLATES_DIR, template_file)
        os.remove(template_path)
        
        return jsonify({
            'success': True,
            'message': f'Template {template_id} deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
