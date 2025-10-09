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
from utils.replicate_processor import ReplicateProcessor

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(advanced_bp, url_prefix='/api/advanced')

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

@app.route('/api/templates/list')
def list_templates():
    """List all available face swap templates"""
    try:
        templates = {
            'female': [],
            'male': [],
            'mixed': []
        }
        
        for category in ['female', 'male', 'mixed']:
            folder_path = os.path.join('static', 'templates', category)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(('.jpg', '.jpeg', '.png')):
                        templates[category].append({
                            'id': f"{category}_{filename.replace('.jpg', '').replace('.jpeg', '').replace('.png', '')}",
                            'name': filename.replace('_', ' ').replace('.jpg', '').replace('.jpeg', '').replace('.png', '').title(),
                            'url': f'/templates/{category}/{filename}',
                            'category': category
                        })
        
        return jsonify({
            'status': 'success',
            'templates': templates,
            'total': sum(len(templates[cat]) for cat in templates)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/face-swap', methods=['POST'])
def template_face_swap():
    """Face swap user's face with template image"""
    try:
        if 'face_image' not in request.files:
            return jsonify({'error': 'No face image provided'}), 400
        
        template_id = request.form.get('template_id')
        if not template_id:
            return jsonify({'error': 'No template_id provided'}), 400
        
        # Parse template_id: format is "category_filename"
        parts = template_id.split('_', 1)
        if len(parts) < 2:
            return jsonify({'error': 'Invalid template_id format'}), 400
        
        category, filename = parts[0], parts[1]
        template_path = os.path.join('static', 'templates', category, f"{filename}.jpg")
        
        if not os.path.exists(template_path):
            # Try other extensions
            template_path = os.path.join('static', 'templates', category, f"{filename}.jpeg")
            if not os.path.exists(template_path):
                template_path = os.path.join('static', 'templates', category, f"{filename}.png")
                if not os.path.exists(template_path):
                    return jsonify({'error': 'Template not found'}), 404
        
        # Load images
        face_file = request.files['face_image']
        face_image = Image.open(face_file.stream)
        template_image = Image.open(template_path)
        
        # Try Replicate face swap first
        try:
            result_image = replicate_processor.swap_face(face_image, template_image)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            from utils.image_processor import ImageProcessor
            face_bytes = ImageProcessor.image_to_bytes(face_image)
            template_bytes = ImageProcessor.image_to_bytes(template_image)
            
            # HF face swap model
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            response = requests.post(
                f"{HF_API_URL}tencent-ailab/IP-Adapter-FaceID",
                headers=headers,
                files={
                    'source_img': face_bytes,
                    'target_img': template_bytes
                }
            )
            
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

@app.route('/api/ai/hd-image', methods=['POST'])
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
        
        # Try Replicate first
        try:
            result_image = replicate_processor.swap_face(source_image, target_image)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            source_bytes = image_to_bytes(source_image)
            target_bytes = image_to_bytes(target_image)
            
            model_id = "tonyassi/face-swap"
            files = {
                'source_image': source_bytes,
                'target_image': target_bytes
            }
            
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            response = requests.post(
                f"{HF_API_URL}{model_id}",
                headers=headers,
                files=files
            )
            
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
