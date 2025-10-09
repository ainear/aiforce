# AI Photo Editing API - Integration Guide

## Base URL
```
https://your-replit-domain.repl.co
```

## Authentication
Add your Hugging Face API token to the `.env` file:
```
HUGGINGFACE_API_TOKEN=your_token_here
```

## Available Endpoints

### Basic Features

#### 1. HD Image Upscaling
**Endpoint:** `POST /api/ai/hd-image`

**Parameters:**
- `image` (file, required): Image file to upscale
- `scale` (form, optional): Scale factor (default: 2)

**Example (Flutter/Dart):**
```dart
var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/api/ai/hd-image'));
request.files.add(await http.MultipartFile.fromPath('image', imagePath));
request.fields['scale'] = '2';

var response = await request.send();
var imageBytes = await response.stream.toBytes();
```

#### 2. Fix Old Photo
**Endpoint:** `POST /api/ai/fix-old-photo`

**Parameters:**
- `image` (file, required): Old/damaged photo to restore

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/api/ai/fix-old-photo \
  -F "image=@old_photo.jpg" \
  --output restored_photo.png
```

#### 3. Cartoonify
**Endpoint:** `POST /api/ai/cartoonify`

**Parameters:**
- `image` (file, required): Photo to cartoonify
- `style` (form, optional): Style type (cartoon, anime, disney)

**Available Styles:**
- `cartoon` - General cartoon style
- `anime` - Anime/manga style
- `disney` - Disney Pixar style

#### 4. Face Swap
**Endpoint:** `POST /api/ai/swap-face`

**Parameters:**
- `source_image` (file, required): Face to swap from
- `target_image` (file, required): Body/background image

**Example (Python):**
```python
import requests

files = {
    'source_image': open('face.jpg', 'rb'),
    'target_image': open('body.jpg', 'rb')
}

response = requests.post(
    'http://localhost:5000/api/ai/swap-face',
    files=files
)

with open('result.png', 'wb') as f:
    f.write(response.content)
```

#### 5. Style Transfer
**Endpoint:** `POST /api/ai/style-transfer`

**Parameters:**
- `image` (file, required): Image to transform
- `style` (form, optional): Artistic style

**Available Styles:**
- `oil_painting` - Oil painting effect
- `sketch` - Pencil sketch
- `watercolor` - Watercolor painting
- `anime` - Anime style

### Advanced Features

**Important Note:** Advanced features use AI generation models. Some features generate new images from text prompts rather than transforming your uploaded photos. For face-based transformations, combine these with the face swap feature.

#### 6. AI Hugs
**Endpoint:** `POST /api/advanced/ai-hugs`

**Parameters:**
- `prompt` (form, optional): Custom prompt for hugging scene

Generates an AI image of people hugging based on text description. For personalized results, use this with face swap.

#### 7. Future Baby
**Endpoint:** `POST /api/advanced/future-baby`

**Parameters:**
- `prompt` (form, optional): Custom prompt for baby image

Generates a cute baby image. Note: For parent-based prediction, custom training or specialized services (like BabyAC API) are recommended.

#### 8. Template Styles
**Endpoint:** `POST /api/advanced/template-styles`

**Parameters:**
- `template` (form, optional): Template name

Generates template-based images from text descriptions. Combine with face swap for personalized results.

**Available Templates:**
- `ghostface` - Ghostface/Scream mask style
- `fashion` - Fashion runway model
- `graduate` - Graduate in cap and gown
- `lovers` - Romantic couple pose
- `bikini` - Beach/summer photo
- `dating` - Dating profile photo
- `profile` - Professional profile

#### 9. Muscle Enhance
**Endpoint:** `POST /api/advanced/muscle-enhance`

**Parameters:**
- `prompt` (form, optional): Custom fitness prompt

Generates muscular/athletic body images from text description.

#### 10. Remove Background
**Endpoint:** `POST /api/advanced/remove-background`

**Parameters:**
- `image` (file, required): Image to process

Removes background from image, returns transparent PNG.

#### 11. Depth Map
**Endpoint:** `POST /api/advanced/depth-map`

**Parameters:**
- `image` (file, required): Image to analyze

Generates depth map visualization from your image.

#### 12. Colorize
**Endpoint:** `POST /api/advanced/colorize`

**Parameters:**
- `image` (file, required): Black & white image

Colorizes black and white or grayscale images.

## Flutter Integration Example

```dart
import 'package:http/http.dart' as http;
import 'dart:io';

class AIPhotoAPI {
  final String baseUrl = 'https://your-replit-domain.repl.co';
  
  Future<List<int>> hdImage(File imageFile, {int scale = 2}) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/ai/hd-image')
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path)
    );
    request.fields['scale'] = scale.toString();
    
    var response = await request.send();
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Failed to process image');
    }
  }
  
  Future<List<int>> faceSwap(File sourceImage, File targetImage) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/ai/swap-face')
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('source_image', sourceImage.path)
    );
    request.files.add(
      await http.MultipartFile.fromPath('target_image', targetImage.path)
    );
    
    var response = await request.send();
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Face swap failed');
    }
  }
  
  Future<List<int>> cartoonify(File imageFile, String style) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/ai/cartoonify')
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path)
    );
    request.fields['style'] = style;
    
    var response = await request.send();
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Cartoonify failed');
    }
  }
  
  Future<List<int>> templateStyle(String template) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/advanced/template-styles')
    );
    
    request.fields['template'] = template;
    
    var response = await request.send();
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Template style failed');
    }
  }
  
  Future<List<int>> removeBackground(File imageFile) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/advanced/remove-background')
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path)
    );
    
    var response = await request.send();
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Background removal failed');
    }
  }
  
  Future<List<int>> colorize(File imageFile) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/advanced/colorize')
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path)
    );
    
    var response = await request.send();
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Colorization failed');
    }
  }
}
```

## Response Format

### Success Response
- **Status Code:** 200
- **Content-Type:** image/png
- **Body:** Binary image data

### Error Response
- **Status Code:** 400, 500
- **Content-Type:** application/json
```json
{
  "error": "Error description",
  "details": "Additional error details"
}
```

## Rate Limits
- Hugging Face Inference API rate limits apply
- Pro token provides higher rate limits
- Consider implementing request queuing in production

## Best Practices

1. **Image Size:** Resize images to max 1024px before uploading for faster processing
2. **Error Handling:** Always implement proper error handling and retry logic
3. **Loading States:** Show loading indicators as AI processing can take 5-30 seconds
4. **Caching:** Cache processed images to reduce API calls
5. **Quality:** Use high-quality input images for best results

## Deployment Notes

When deploying to production:
1. Set `HUGGINGFACE_API_TOKEN` in environment variables
2. Consider using a production WSGI server (gunicorn)
3. Implement rate limiting and request queuing
4. Add image storage (Supabase, AWS S3, etc.) for processed images
5. Monitor API usage and costs
