import io
from PIL import Image
import base64

class ImageProcessor:
    @staticmethod
    def resize_image(image, max_size=1024):
        """Resize image while maintaining aspect ratio"""
        ratio = min(max_size / image.width, max_size / image.height)
        if ratio < 1:
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def image_to_bytes(image, format='PNG'):
        """Convert PIL Image to bytes"""
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr.read()
    
    @staticmethod
    def bytes_to_image(image_bytes):
        """Convert bytes to PIL Image"""
        return Image.open(io.BytesIO(image_bytes))
    
    @staticmethod
    def image_to_base64(image, format='PNG'):
        """Convert PIL Image to base64 string"""
        img_bytes = ImageProcessor.image_to_bytes(image, format)
        return base64.b64encode(img_bytes).decode('utf-8')
    
    @staticmethod
    def base64_to_image(base64_string):
        """Convert base64 string to PIL Image"""
        img_bytes = base64.b64decode(base64_string)
        return ImageProcessor.bytes_to_image(img_bytes)
    
    @staticmethod
    def validate_image(file):
        """Validate uploaded image file"""
        try:
            image = Image.open(file.stream)
            file.stream.seek(0)
            return True, image
        except Exception as e:
            return False, str(e)
