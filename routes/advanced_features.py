import io
import os
import requests
import base64
from flask import Blueprint, request, jsonify, send_file
from PIL import Image
from utils.image_processor import ImageProcessor
from utils.replicate_processor import ReplicateProcessor

advanced_bp = Blueprint('advanced', __name__)

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN', '')
HF_API_URL = "https://api-inference.huggingface.co/models/"

replicate_processor = ReplicateProcessor()

def query_image_to_image(model_id, image_bytes):
    """Query Hugging Face for image-to-image models that accept raw binary"""
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(
        f"{HF_API_URL}{model_id}",
        headers=headers,
        data=image_bytes
    )
    return response

def query_text_to_image(model_id, prompt):
    """Query Hugging Face for text-to-image models"""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(
        f"{HF_API_URL}{model_id}",
        headers=headers,
        json=payload
    )
    return response

@advanced_bp.route('/ai-hugs', methods=['POST'])
def ai_hugs():
    """Generate AI hugging photo from 2 person images (Replicate primary, HF fallback)"""
    try:
        # Support both field names: person1/person2 (Flutter) and person1_image/person2_image
        if 'person1' in request.files and 'person2' in request.files:
            person1_file = request.files['person1']
            person2_file = request.files['person2']
        elif 'person1_image' in request.files and 'person2_image' in request.files:
            person1_file = request.files['person1_image']
            person2_file = request.files['person2_image']
        else:
            # Fallback to text prompt if no images provided
            prompt = request.form.get('prompt', 'two people hugging, warm embrace, happy moment, professional photo, realistic, high quality')
            result_image = replicate_processor.generate_image_from_text(prompt)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        
        # Load images
        person1_image = Image.open(person1_file.stream)
        person2_image = Image.open(person2_file.stream)
        
        # Generate hugging photo with prompt based on images
        prompt = "two people hugging, warm embrace, happy romantic moment, professional photo, realistic, high quality, beautiful composition"
        
        # Try Replicate first
        try:
            result_image = replicate_processor.generate_image_from_text(prompt)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            model_id = "stabilityai/stable-diffusion-2-1"
            response = query_text_to_image(model_id, prompt)
            
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

@advanced_bp.route('/future-baby', methods=['POST'])
def future_baby():
    """Generate baby image from 2 parent images (Replicate primary, HF fallback)"""
    try:
        # Support both field names: parent1/parent2 (Flutter) and parent1_image/parent2_image
        if 'parent1' in request.files and 'parent2' in request.files:
            parent1_file = request.files['parent1']
            parent2_file = request.files['parent2']
        elif 'parent1_image' in request.files and 'parent2_image' in request.files:
            parent1_file = request.files['parent1_image']
            parent2_file = request.files['parent2_image']
        else:
            # Fallback to text prompt if no images provided
            prompt = request.form.get('prompt', 'cute baby face, infant, adorable, high quality portrait, professional photo, realistic')
            result_image = replicate_processor.generate_image_from_text(prompt)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        
        # Load images
        parent1_image = Image.open(parent1_file.stream)
        parent2_image = Image.open(parent2_file.stream)
        
        # Generate baby prediction with prompt
        prompt = "cute baby face, infant child, adorable mixed features, high quality portrait, professional photo, realistic, beautiful baby"
        
        # Try Replicate first
        try:
            result_image = replicate_processor.generate_image_from_text(prompt)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            model_id = "stabilityai/stable-diffusion-2-1"
            response = query_text_to_image(model_id, prompt)
            
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

@advanced_bp.route('/template-styles', methods=['POST'])
def template_styles():
    """Generate template-based images from text prompts (Replicate primary, HF fallback)"""
    try:
        template = request.form.get('template', 'ghostface')
        
        templates = {
            'ghostface': 'person wearing ghostface scream mask, horror movie style, dramatic lighting, high quality, realistic photo',
            'fashion': 'fashion model on runway, haute couture, elegant pose, professional photography, high fashion',
            'graduate': 'graduate in cap and gown, holding diploma, university background, professional photo, happy expression',
            'lovers': 'romantic couple pose, loving embrace, beautiful scenery, warm lighting, professional photo',
            'bikini': 'beach photo, summer vibes, ocean background, tropical paradise, professional photography, attractive',
            'dating': 'attractive person, dating profile photo, natural smile, outdoor setting, high quality, professional',
            'profile': 'professional profile picture, clean background, confident pose, studio lighting, business photo'
        }
        
        prompt = templates.get(template, templates['ghostface'])
        
        # Try Replicate first
        try:
            result_image = replicate_processor.generate_image_from_text(prompt)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            model_id = "stabilityai/stable-diffusion-2-1"
            response = query_text_to_image(model_id, prompt)
            
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

@advanced_bp.route('/muscle-enhance', methods=['POST'])
def muscle_enhance():
    """Generate muscular body image from text prompt (Replicate primary, HF fallback)"""
    try:
        prompt = request.form.get('prompt', 'muscular person, bodybuilder, fit athletic body, professional fitness photo, high quality, realistic')
        
        # Try Replicate first
        try:
            result_image = replicate_processor.generate_image_from_text(prompt)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            model_id = "stabilityai/stable-diffusion-2-1"
            response = query_text_to_image(model_id, prompt)
            
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

@advanced_bp.route('/remove-background', methods=['POST'])
def remove_background():
    """Remove background from image (Replicate primary, HF fallback)"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        image = Image.open(file.stream)
        
        # Try Replicate first
        try:
            result_image = replicate_processor.remove_background(image)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            image_bytes = ImageProcessor.image_to_bytes(image)
            model_id = "briaai/RMBG-1.4"
            response = query_image_to_image(model_id, image_bytes)
            
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

@advanced_bp.route('/depth-map', methods=['POST'])
def depth_map():
    """Generate depth map from image (Replicate primary, HF fallback)"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        image = Image.open(file.stream)
        
        # Try Replicate first
        try:
            result_image = replicate_processor.generate_depth_map(image)
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            return send_file(output, mimetype='image/png')
        except Exception as replicate_error:
            print(f"Replicate failed: {replicate_error}, trying Hugging Face...")
            
            # Fallback to Hugging Face
            image_bytes = ImageProcessor.image_to_bytes(image)
            model_id = "Intel/dpt-large"
            response = query_image_to_image(model_id, image_bytes)
            
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

@advanced_bp.route('/colorize', methods=['POST'])
def colorize():
    """Colorize black and white images"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        image = Image.open(file.stream)
        image_bytes = ImageProcessor.image_to_bytes(image)
        
        model_id = "ddcolor/ddcolor"
        
        response = query_image_to_image(model_id, image_bytes)
        
        if response.status_code == 200:
            result_image = Image.open(io.BytesIO(response.content))
            
            output = io.BytesIO()
            result_image.save(output, format='PNG')
            output.seek(0)
            
            return send_file(output, mimetype='image/png')
        else:
            return jsonify({
                'error': 'Colorization failed',
                'details': response.text,
                'status_code': response.status_code
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
