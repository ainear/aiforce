import io
import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.video_processor import VideoFaceSwapProcessor

video_bp = Blueprint('video', __name__)
video_processor = VideoFaceSwapProcessor()

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@video_bp.route('/face-swap', methods=['POST'])
def video_face_swap():
    """
    Video Face Swap API
    
    Multipart form-data:
    - face_image: Image file (face to swap)
    - video_file: Video file (video to swap into)
    - provider: "auto", "huggingface", or "replicate" (default: "auto")
    - gender: "all", "male", "female" (for HF models, default: "all")
    
    Returns:
    - Video file (if successful)
    - JSON error (if failed)
    """
    try:
        # Validate files
        if 'face_image' not in request.files:
            return jsonify({'error': 'No face_image provided'}), 400
        if 'video_file' not in request.files:
            return jsonify({'error': 'No video_file provided'}), 400
        
        face_image = request.files['face_image']
        video_file = request.files['video_file']
        
        if face_image.filename == '':
            return jsonify({'error': 'No face_image selected'}), 400
        if video_file.filename == '':
            return jsonify({'error': 'No video_file selected'}), 400
        
        # Validate file extensions
        if not allowed_file(face_image.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({'error': f'Invalid image format. Allowed: {ALLOWED_IMAGE_EXTENSIONS}'}), 400
        if not allowed_file(video_file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({'error': f'Invalid video format. Allowed: {ALLOWED_VIDEO_EXTENSIONS}'}), 400
        
        # Get parameters
        provider = request.form.get('provider', 'auto')  # auto, huggingface, replicate
        gender = request.form.get('gender', 'all')       # all, male, female
        
        # Validate provider
        if provider not in ['auto', 'replicate', 'vmodel']:
            return jsonify({'error': f'Invalid provider: {provider}. Use: auto, replicate, or vmodel'}), 400
        
        # Validate gender
        if gender not in ['all', 'male', 'female']:
            return jsonify({'error': f'Invalid gender: {gender}. Use: all, male, or female'}), 400
        
        print(f"[API] Video face swap request: provider={provider}, gender={gender}")
        
        # Process video face swap
        result, provider_used, model_used = video_processor.swap_face_video(
            face_image=face_image,
            video_file=video_file,
            provider=provider,
            gender=gender
        )
        
        # Handle different result types
        if isinstance(result, str):
            # Result is a URL (from Replicate)
            return jsonify({
                'success': True,
                'video_url': result,
                'provider': provider_used,
                'model': model_used,
                'message': f'Video face swap completed using {provider_used}/{model_used}'
            })
        else:
            # Result is a file path (from HuggingFace)
            return send_file(
                result,
                mimetype='video/mp4',
                as_attachment=True,
                download_name='face_swapped_video.mp4'
            )
    
    except Exception as e:
        error_msg = str(e)
        print(f"[API] Video face swap error: {error_msg}")
        
        # Check for specific errors and provide helpful messages
        if "HUGGINGFACE_PRO_TOKEN" in error_msg:
            return jsonify({
                'error': 'HuggingFace Pro token required',
                'details': 'Please add HUGGINGFACE_PRO_TOKEN to environment secrets',
                'setup_url': 'https://huggingface.co/settings/tokens'
            }), 503
        
        if "VMODEL_API_TOKEN" in error_msg:
            return jsonify({
                'error': 'VModel API token required',
                'details': 'Please add VMODEL_API_TOKEN to environment secrets',
                'setup_url': 'https://vmodel.ai'
            }), 503
        
        if "REPLICATE_PRO_TOKEN" in error_msg:
            return jsonify({
                'error': 'Replicate Pro token required',
                'details': 'Please add REPLICATE_PRO_TOKEN to environment secrets',
                'setup_url': 'https://replicate.com/account/api-tokens'
            }), 503
        
        # FFmpeg or video format errors
        if "ffmpeg" in error_msg.lower():
            return jsonify({
                'error': 'Video format not supported',
                'details': 'Try converting your video to MP4 (H.264) or use a different video',
                'suggestion': 'Switch to HuggingFace provider or use Auto mode for fallback'
            }), 400
        
        # Timeout errors
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            return jsonify({
                'error': 'Processing timeout',
                'details': 'Video processing took too long',
                'suggestion': 'Try a shorter video or use HuggingFace provider'
            }), 408
        
        # All providers failed
        if "both providers failed" in error_msg.lower() or "all" in error_msg.lower():
            return jsonify({
                'error': 'All AI providers failed',
                'details': error_msg,
                'suggestion': 'Please try again with a different video or check API tokens'
            }), 503
        
        # Generic error
        return jsonify({
            'error': 'Video face swap failed',
            'details': error_msg,
            'suggestion': 'Try using Auto or HuggingFace provider'
        }), 500

@video_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get available video face swap providers and models"""
    return jsonify({
        'providers': {
            'auto': {
                'name': 'Auto (Smart Fallback)',
                'strategy': 'Replicate primary → VModel fallback',
                'models': ['codeplugtech/face-swap', 'vmodel/video-face-swap-pro'],
                'timeout': '15-90 seconds',
                'audio_preserved': True,
                'cost': '$0.0026-0.10 per video',
                'status': '✅ RECOMMENDED'
            },
            'replicate': {
                'name': 'Replicate (Fast & Cheap)',
                'models': [
                    'codeplugtech/face-swap'
                ],
                'features': ['video'],
                'pricing': '~$0.11-0.14 per run',
                'speed': '~77 seconds average',
                'timeout': '10-15 seconds',
                'audio_preserved': True,
                'cost': '$0.0026 per video (~384 videos per $1)',
                'status': '✅ WORKING 2025'
            },
            'vmodel': {
                'name': 'VModel.AI (Premium)',
                'models': [
                    'vmodel/video-face-swap-pro'
                ],
                'timeout': '15-30 seconds',
                'audio_preserved': True,
                'cost': 'Per-second pricing (~$0.10 per video)',
                'quality': 'Premium, commercial license',
                'status': '✅ WORKING 2025'
            }
        },
        'supported_formats': {
            'video': list(ALLOWED_VIDEO_EXTENSIONS),
            'image': list(ALLOWED_IMAGE_EXTENSIONS)
        },
        'usage': {
            'provider_auto': 'Replicate primary (fast, cheap) → VModel fallback (premium)',
            'provider_replicate': 'Replicate only - codeplugtech/face-swap with audio ($0.0026/video)',
            'provider_vmodel': 'VModel only - premium quality with commercial license',
            'audio_note': '✅ All providers preserve original audio!'
        }
    })
