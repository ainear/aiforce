import os
import replicate
import requests
from io import BytesIO
from PIL import Image
import base64

class ReplicateProcessor:
    """
    Replicate API processor - raises exceptions on failure for endpoint fallback handling
    """
    
    def __init__(self):
        self.replicate_token = os.getenv('REPLICATE_API_TOKEN')
        self.hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
        
    def _image_to_data_uri(self, image):
        """Convert PIL Image to data URI for Replicate"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def _download_image(self, url_or_file):
        """Download image from URL/FileOutput and return PIL Image"""
        # Handle FileOutput objects (has read() method)
        if hasattr(url_or_file, 'read'):
            return Image.open(BytesIO(url_or_file.read()))
        
        # Handle FileOutput with url() method
        if hasattr(url_or_file, 'url'):
            url = url_or_file.url() if callable(url_or_file.url) else url_or_file.url
            response = requests.get(url)
            return Image.open(BytesIO(response.content))
        
        # Handle string URLs
        if isinstance(url_or_file, str):
            response = requests.get(url_or_file)
            return Image.open(BytesIO(response.content))
        
        # Try to use it as bytes directly
        try:
            return Image.open(BytesIO(url_or_file))
        except:
            raise Exception(f"Cannot handle output type: {type(url_or_file)}")
    
    def _normalize_replicate_output(self, output):
        """
        Normalize Replicate output to URL or FileOutput
        Handles: FileOutput, iterators, lists, dicts, direct URLs
        """
        # FileOutput objects - return as-is for _download_image to handle
        if hasattr(output, 'read') or hasattr(output, 'url'):
            return output
        
        # String URLs - return as-is
        if isinstance(output, str):
            return output
        
        # Lists - get first item
        if isinstance(output, list):
            if len(output) > 0:
                return self._normalize_replicate_output(output[0])
            raise Exception("Replicate returned empty list")
        
        # Dicts - extract output/url
        if isinstance(output, dict):
            if 'output' in output:
                return self._normalize_replicate_output(output['output'])
            if 'url' in output:
                return self._normalize_replicate_output(output['url'])
            raise Exception(f"Unknown dict format: {output}")
        
        # Iterators - get first item
        try:
            first_item = next(iter(output))
            return self._normalize_replicate_output(first_item)
        except (StopIteration, TypeError):
            raise Exception("Replicate returned invalid output format")
    
    def upscale_image(self, image, scale=4):
        """Upscale image using Real-ESRGAN. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("No Replicate token available")
        
        input_uri = self._image_to_data_uri(image)
        output = replicate.run(
            "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
            input={"image": input_uri, "scale": scale, "face_enhance": False}
        )
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
    
    def restore_photo(self, image, version="v1.3", scale=2):
        """Restore old/damaged photos using GFPGAN. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("No Replicate token available")
        
        input_uri = self._image_to_data_uri(image)
        output = replicate.run(
            "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3",
            input={"img": input_uri, "version": version, "scale": scale}
        )
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
    
    def swap_face(self, source_face_image, target_image):
        """Swap faces - currently disabled, use HuggingFace fallback. Raises exception."""
        # Replicate face swap models are unstable/unavailable
        # Raise exception to trigger HuggingFace fallback
        raise Exception("Replicate face swap unavailable, using HuggingFace fallback")
    
    def cartoonify(self, image, style="general"):
        """Transform photo to cartoon/anime style. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("Replicate token required for cartoonify")
        
        input_uri = self._image_to_data_uri(image)
        
        if style in ["anime", "japanese"]:
            output = replicate.run(
                "lucataco/anime-gan:3a3ddb5a2c7e8ee3181dc35aa0b01cbb9ea3a3965e4e1d36f6a2ea0cc2043cd6",
                input={"image": input_uri}
            )
        else:
            output = replicate.run(
                "catacolabs/cartoonify:f109015d60170dfb20460f17da8cb863155823c85ece1115e1e9e4ec7ef51d3b",
                input={"image": input_uri}
            )
        
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
    
    def style_transfer(self, content_image, style="oil_painting"):
        """Apply artistic style transfer. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("Replicate token required for style transfer")
        
        input_uri = self._image_to_data_uri(content_image)
        
        style_prompts = {
            "oil_painting": "oil painting, thick brush strokes, impressionist style",
            "watercolor": "watercolor painting, soft colors, flowing",
            "sketch": "pencil sketch, hand drawn, detailed lines",
            "disney": "disney pixar style, 3D animation, cute characters",
            "cartoon": "cartoon style, vibrant colors, simplified features"
        }
        
        prompt = style_prompts.get(style, style_prompts["oil_painting"])
        
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={"image": input_uri, "prompt": prompt, "strength": 0.7, "num_inference_steps": 30}
        )
        
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
    
    def remove_background(self, image):
        """Remove background from image. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("No Replicate token available")
        
        input_uri = self._image_to_data_uri(image)
        output = replicate.run(
            "lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1",
            input={"image": input_uri}
        )
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
    
    def generate_depth_map(self, image):
        """Generate depth map from image. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("No Replicate token available")
        
        input_uri = self._image_to_data_uri(image)
        output = replicate.run(
            "cjwbw/midas:7d3a9a6c8e3a0a0a0e0e0e0e0e0e0e0e0e0e0e0e",
            input={"image": input_uri}
        )
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
    
    def generate_image_from_text(self, prompt, negative_prompt="", width=512, height=512):
        """Generate image from text prompt. Raises exception on failure."""
        if not self.replicate_token:
            raise Exception("No Replicate token available")
        
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        )
        result_url = self._normalize_replicate_output(output)
        return self._download_image(result_url)
