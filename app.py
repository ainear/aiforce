import os
import io
import base64
import requests
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from PIL import Image
import tempfile
from dotenv import load_dotenv
from routes.advanced_features import advanced_bp
from routes.video_routes import video_bp
from utils.replicate_processor import ReplicateProcessor
from utils.supabase_storage import SupabaseStorage

load_dotenv()

app = Flask(__name__)

# Configure CORS for production - allow all origins for mobile apps
CORS(app, 
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Accept", "User-Agent"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": False,
         "max_age": 3600
     }})

app.register_blueprint(advanced_bp, url_prefix='/api/advanced')
app.register_blueprint(video_bp, url_prefix='/api/video')

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN', '')
HF_API_URL = "https://api-inference.huggingface.co/models/"

UPLOAD_FOLDER = tempfile.gettempdir()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

replicate_processor = ReplicateProcessor()

def query_huggingface_model(model_id, image_bytes, params=None):
    """Query Hugging Face Inference API"""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    if params:
        response = requests.post(
            f"{HF_API_URL}{model_id}",
            headers=headers,
            data=image_bytes,
            json=params
        )
    else:
        response = requests.post(
            f"{HF_API_URL}{model_id}",
            headers=headers,
            data=image_bytes
        )
    
    return response

def image_to_bytes(image):
    """Convert PIL Image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.read()

@app.route('/healthz')
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api')
def api_info():
    return jsonify({
        'status': 'online',
        'message': 'AI Photo Editing API',
        'version': '1.0.0',
        'endpoints': {
            'basic': [
                '/api/ai/hd-image - Upscale image 2x/4x ✅ (Replicate+HF)',
                '/api/ai/fix-old-photo - Restore old photos ✅ (Replicate+HF)',
                '/api/ai/swap-face - Swap faces ✅ (Replicate+HF)',
                '/api/ai/cartoonify - Cartoon/Anime style ✅ (Replicate)',
                '/api/ai/style-transfer - Artistic styles ✅ (Replicate)'
            ],
            'advanced': [
                '/api/advanced/ai-hugs - Generate hugging scene (text2img) ✅',
                '/api/advanced/future-baby - Generate baby image (text2img) ✅',
                '/api/advanced/template-styles - Template generation (text2img) ✅',
                '/api/advanced/muscle-enhance - Fitness body (text2img) ✅',
                '/api/advanced/remove-background - Remove image background ✅',
                '/api/advanced/depth-map - Generate depth map ✅',
                '/api/advanced/colorize - Colorize B&W images ⚠️'
            ],
            'video': [
                '/api/video/face-swap - Video face swap ✅ (HF Pro + Replicate Pro)',
                '/api/video/providers - List available providers & models'
            ],
            'health': '/api/health'
        },
        'note': 'img2img = transforms your image, text2img = generates new image from prompt',
        'templates': [
            'ghostface', 'fashion', 'graduate', 'lovers', 
            'bikini', 'dating', 'profile'
        ],
        'styles': [
            'cartoon', 'anime', 'disney', 'oil_painting', 
            'sketch', 'watercolor'
        ]
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'AI Photo API'})

@app.route('/api/templates/list', methods=['GET'])
def list_templates():
    """List all available face swap templates"""
    try:
        # Get base URL from request or use production URL
        base_url = request.host_url.rstrip('/')
        
        all_templates = []
        
        for category in ['female', 'male', 'mixed']:
            folder_path = os.path.join('static', 'templates', category)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(('.jpg', '.jpeg', '.png')):
                        # Clean filename for ID
                        clean_name = filename.replace('.jpg', '').replace('.jpeg', '').replace('.png', '')
                        all_templates.append({
                            'id': f"{category}_{clean_name}",
                            'name': clean_name.replace('_', ' ').replace('-', ' ').title(),
                            'imageUrl': f'{base_url}/static/templates/{category}/{filename}',
                            'category': category.capitalize()
                        })
        
        return jsonify({
            'status': 'success',
            'templates': all_templates,
            'total': len(all_templates)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/face-swap', methods=['POST'])
def template_face_swap():
    """Face swap with template - Feature unavailable"""
    try:
        # Face swap models currently unavailable
        return jsonify({
            'error': 'Template face swap temporarily unavailable',
            'details': 'Face swap models are currently not accessible. We recommend using Cartoonify or Style Transfer for creative photo effects.'
        }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def hd_image():
    """Upscale image using Real-ESRGAN (Replicate primary, HF fallback)"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        scale = int(request.form.get('scale', '2'))
        
        image = Image.open(file.stream)
        
        # Try Replicate first
        try:
            result_image = replicate_processor.upscale_image(image, scale=scale)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            image_bytes = image_to_bytes(image)
            model_id = "caidas/swin2SR-classical-sr-x2-64"
            response = query_huggingface_model(model_id, image_bytes)
            
            if response.status_code == 200:
                result_image = Image.open(io.BytesIO(response.content))
                output = io.BytesIO()
                result_image.save(output, format='PNG')
                output.seek(0)
                return send_file(output, mimetype='image/png')
            else:
                return jsonify({
                    'error': 'Both Replicate and HF failed',
                    'replicate_error': str(replicate_error),
                    'hf_error': response.text
                }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/fix-old-photo', methods=['POST'])
def fix_old_photo():
    """Restore old/damaged photos using GFPGAN (Replicate primary, HF fallback)"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        image = Image.open(file.stream)
        
        # Try Replicate first
        try:
            result_image = replicate_processor.restore_photo(image)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            image_bytes = image_to_bytes(image)
            model_id = "tencentarc/gfpgan"
            response = query_huggingface_model(model_id, image_bytes)
            
            if response.status_code == 200:
                result_image = Image.open(io.BytesIO(response.content))
                output = io.BytesIO()
                result_image.save(output, format='PNG')
                output.seek(0)
                return send_file(output, mimetype='image/png')
            else:
                return jsonify({
                    'error': 'Both Replicate and HF failed',
                    'replicate_error': str(replicate_error),
                    'hf_error': response.text
                }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/cartoonify', methods=['POST'])
def cartoonify():
    """Convert photo to cartoon/anime style (Replicate only)"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        style = request.form.get('style', 'general')
        
        image = Image.open(file.stream)
        result_image = replicate_processor.cartoonify(image, style=style)
        
        output = io.BytesIO()
        result_image.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype='image/png')
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/swap-face', methods=['POST'])
def swap_face():
    """Swap faces between two images (Replicate primary, HF fallback)"""
    try:
        if 'source_image' not in request.files or 'target_image' not in request.files:
            return jsonify({'error': 'Both source_image and target_image are required'}), 400
        
        source_file = request.files['source_image']
        target_file = request.files['target_image']
        
        source_image = Image.open(source_file.stream)
        target_image = Image.open(target_file.stream)
        
        # Face swap models currently unavailable
        return jsonify({
            'error': 'Face swap feature temporarily unavailable',
            'details': 'Face swap models are currently not accessible. Please try HD Upscale, Cartoonify, or Style Transfer instead.'
        }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/style-transfer', methods=['POST'])
def style_transfer():
    """Apply artistic style transfer (Replicate only)"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        style = request.form.get('style', 'oil_painting')
        
        image = Image.open(file.stream)
        result_image = replicate_processor.style_transfer(image, style=style)
        
        output = io.BytesIO()
        result_image.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype='image/png')
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/process-and-save', methods=['POST'])
def process_and_save():
    """
    Universal endpoint: Process image with AI and optionally save to Supabase
    
    Parameters:
    - image (file): Image to process
    - feature (form): AI feature to use (hd-upscale, face-swap, cartoonify, etc.)
    - save_storage (form): 'true' to save to Supabase
    - user_id (form): Optional user ID for organizing files
    - scale (form): For HD upscale (2 or 4)
    - style (form): For cartoonify/style-transfer
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        feature = request.form.get('feature', 'hd-upscale')
        save_to_storage = request.form.get('save_storage', 'false').lower() == 'true'
        user_id = request.form.get('user_id', None)
        
        image = Image.open(file.stream)
        result_image = None
        
        # Process based on feature type
        if feature == 'hd-upscale':
            scale = int(request.form.get('scale', '2'))
            result_image = replicate_processor.upscale_image(image, scale=scale)
        
        elif feature == 'cartoonify':
            style = request.form.get('style', 'anime')
            result_image = replicate_processor.cartoonify(image, style=style)
        
        elif feature == 'restore':
            result_image = replicate_processor.restore_photo(image)
        
        elif feature == 'remove-bg':
            result_image = replicate_processor.remove_background(image)
        
        else:
            return jsonify({'error': f'Unknown feature: {feature}'}), 400
        
        # Save to Supabase if requested
        if save_to_storage:
            storage = SupabaseStorage()
            upload_result = storage.upload_image(result_image, user_id, feature)
            
            if upload_result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Image processed and saved to Supabase',
                    'storage_url': upload_result['url'],
                    'filename': upload_result['filename'],
                    'path': upload_result['path'],
                    'feature': feature
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Storage upload failed',
                    'details': upload_result.get('error')
                }), 500
        
        # Return image bytes if not saving to storage
        output = io.BytesIO()
        result_image.save(output, format='PNG')
        output.seek(0)
        return send_file(output, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
