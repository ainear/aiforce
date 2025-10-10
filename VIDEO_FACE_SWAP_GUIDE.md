# 🎬 Video Face Swap API - Integration Guide

## Overview

Video Face Swap API cho phép bạn swap khuôn mặt trong video với **2 providers**:
- **HuggingFace Pro**: Multi-model với auto-fallback (5-7s timeout)
- **Replicate Pro**: Backup option, ổn định

## 🔑 API Keys Required

### 1. HuggingFace Pro Token
```bash
# Lấy tại: https://huggingface.co/settings/tokens
export HUGGINGFACE_PRO_TOKEN="hf_xxxxxxxxxxxxx"
```

### 2. Replicate Pro Token
```bash
# Lấy tại: https://replicate.com/account/api-tokens
export REPLICATE_PRO_TOKEN="r8_xxxxxxxxxxxxx"
```

## 📡 API Endpoints

### 1. **GET /api/video/providers**
Lấy danh sách providers và models available

```bash
curl http://localhost:5000/api/video/providers
```

**Response:**
```json
{
  "providers": {
    "huggingface": {
      "name": "HuggingFace Pro",
      "models": [
        "tonyassi/video-face-swap",
        "ALSv/video-face-swap",
        "MarkoVidrih/video-face-swap"
      ],
      "timeout": "5-7 seconds per model",
      "auto_fallback": true,
      "supports_gender_filter": true
    },
    "replicate": {
      "name": "Replicate Pro",
      "models": [
        "arabyai-replicate/roop_face_swap"
      ],
      "features": ["video"],
      "pricing": "~$0.11 per run",
      "status": "✅ WORKING 2025"
    }
  },
  "supported_formats": {
    "video": ["mp4", "avi", "mov", "webm"],
    "image": ["jpg", "jpeg", "png", "webp"]
  }
}
```

---

### 2. **POST /api/video/face-swap**
Swap face trong video

**Parameters (multipart/form-data):**
- `face_image` (file): Ảnh khuôn mặt để swap vào
- `video_file` (file): Video cần swap
- `provider` (string, optional): `"auto"` | `"huggingface"` | `"replicate"` (default: `"auto"`)
- `gender` (string, optional): `"all"` | `"male"` | `"female"` (default: `"all"`)

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video_file=@video.mp4" \
  -F "provider=auto" \
  -F "gender=all"
```

**Response Types:**

**Success (JSON - URL response from Replicate):**
```json
{
  "success": true,
  "video_url": "https://replicate.delivery/pbxt/xyz.mp4",
  "provider": "replicate",
  "model": "yan-ops/face_swap",
  "message": "Video face swap completed using replicate/yan-ops/face_swap"
}
```

**Success (Video file - from HuggingFace):**
```
Content-Type: video/mp4
Content-Disposition: attachment; filename=face_swapped_video.mp4

[Binary video data]
```

**Error Response:**
```json
{
  "error": "Video face swap failed",
  "details": "All HuggingFace models failed. Last error: timeout"
}
```

---

## 🐍 Python Integration

### Basic Example
```python
import requests

def video_face_swap(face_image_path, video_path, provider='auto'):
    url = "http://localhost:5000/api/video/face-swap"
    
    files = {
        'face_image': open(face_image_path, 'rb'),
        'video_file': open(video_path, 'rb')
    }
    
    data = {
        'provider': provider,
        'gender': 'all'
    }
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # URL response
            result = response.json()
            print(f"Video URL: {result['video_url']}")
            return result['video_url']
        else:
            # Save video file
            with open('output.mp4', 'wb') as f:
                f.write(response.content)
            print("Saved to output.mp4")
            return 'output.mp4'
    else:
        error = response.json()
        print(f"Error: {error}")
        return None

# Usage
video_face_swap('my_face.jpg', 'input_video.mp4', provider='auto')
```

### Advanced Example with Gender Filter
```python
def swap_specific_gender(face_image_path, video_path, gender='male'):
    """Swap only male or female faces"""
    url = "http://localhost:5000/api/video/face-swap"
    
    files = {
        'face_image': open(face_image_path, 'rb'),
        'video_file': open(video_path, 'rb')
    }
    
    data = {
        'provider': 'huggingface',  # HF supports gender filter
        'gender': gender  # 'male', 'female', or 'all'
    }
    
    response = requests.post(url, files=files, data=data)
    return response

# Swap only male faces
result = swap_specific_gender('face.jpg', 'video.mp4', gender='male')
```

---

## 📱 Flutter Integration

### 1. Install Dependencies
```yaml
# pubspec.yaml
dependencies:
  http: ^1.1.0
  dio: ^5.4.0  # Alternative to http
  path_provider: ^2.1.1
  video_player: ^2.8.1
```

### 2. API Service
```dart
import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
import 'dart:io';

class VideoFaceSwapService {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: 'https://your-api-url.com',
    connectTimeout: Duration(minutes: 3),
    receiveTimeout: Duration(minutes: 3),
  ));

  Future<String?> swapFaceInVideo({
    required File faceImage,
    required File videoFile,
    String provider = 'auto',
    String gender = 'all',
  }) async {
    try {
      // Prepare multipart form data
      FormData formData = FormData.fromMap({
        'face_image': await MultipartFile.fromFile(
          faceImage.path,
          filename: 'face.jpg',
          contentType: MediaType('image', 'jpeg'),
        ),
        'video_file': await MultipartFile.fromFile(
          videoFile.path,
          filename: 'video.mp4',
          contentType: MediaType('video', 'mp4'),
        ),
        'provider': provider,
        'gender': gender,
      });

      // Send request
      Response response = await _dio.post(
        '/api/video/face-swap',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      // Handle response
      if (response.statusCode == 200) {
        if (response.data is Map) {
          // JSON response with URL
          return response.data['video_url'];
        } else {
          // Binary video data - save to file
          final appDir = await getApplicationDocumentsDirectory();
          final outputPath = '${appDir.path}/swapped_video.mp4';
          
          File outputFile = File(outputPath);
          await outputFile.writeAsBytes(response.data);
          
          return outputPath;
        }
      }
      
      return null;
    } catch (e) {
      print('Video swap error: $e');
      return null;
    }
  }
}
```

### 3. UI Implementation
```dart
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_player/video_player.dart';

class VideoFaceSwapScreen extends StatefulWidget {
  @override
  _VideoFaceSwapScreenState createState() => _VideoFaceSwapScreenState();
}

class _VideoFaceSwapScreenState extends State<VideoFaceSwapScreen> {
  File? _faceImage;
  File? _videoFile;
  String? _resultVideoPath;
  bool _isLoading = false;
  
  final VideoFaceSwapService _service = VideoFaceSwapService();
  final ImagePicker _picker = ImagePicker();
  VideoPlayerController? _videoController;

  Future<void> _pickFaceImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        _faceImage = File(image.path);
      });
    }
  }

  Future<void> _pickVideo() async {
    final XFile? video = await _picker.pickVideo(source: ImageSource.gallery);
    if (video != null) {
      setState(() {
        _videoFile = File(video.path);
      });
    }
  }

  Future<void> _swapFace() async {
    if (_faceImage == null || _videoFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please select both face image and video')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      String? resultPath = await _service.swapFaceInVideo(
        faceImage: _faceImage!,
        videoFile: _videoFile!,
        provider: 'auto',
        gender: 'all',
      );

      if (resultPath != null) {
        setState(() {
          _resultVideoPath = resultPath;
          _isLoading = false;
        });

        // Initialize video player
        if (resultPath.startsWith('http')) {
          _videoController = VideoPlayerController.network(resultPath);
        } else {
          _videoController = VideoPlayerController.file(File(resultPath));
        }
        await _videoController!.initialize();
        await _videoController!.play();
      } else {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Face swap failed')),
        );
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      print('Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Video Face Swap')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Face Image Picker
            ElevatedButton.icon(
              onPressed: _pickFaceImage,
              icon: Icon(Icons.face),
              label: Text('Select Face Image'),
            ),
            if (_faceImage != null)
              Image.file(_faceImage!, height: 200),

            SizedBox(height: 20),

            // Video Picker
            ElevatedButton.icon(
              onPressed: _pickVideo,
              icon: Icon(Icons.video_library),
              label: Text('Select Video'),
            ),
            if (_videoFile != null)
              Text('Video selected: ${_videoFile!.path.split('/').last}'),

            SizedBox(height: 20),

            // Swap Button
            ElevatedButton(
              onPressed: _isLoading ? null : _swapFace,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Swap Face'),
            ),

            SizedBox(height: 20),

            // Result Video Player
            if (_videoController != null && _videoController!.value.isInitialized)
              AspectRatio(
                aspectRatio: _videoController!.value.aspectRatio,
                child: VideoPlayer(_videoController!),
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _videoController?.dispose();
    super.dispose();
  }
}
```

---

## ⚙️ Provider Selection Guide

### **Provider: "auto" (Recommended)** ⭐
- Try HuggingFace first (5-7s timeout per model)
- Auto fallback to Replicate if HF fails
- Best reliability

```bash
curl -X POST /api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video_file=@video.mp4" \
  -F "provider=auto"
```

### **Provider: "huggingface"**
- Use HuggingFace Pro models only
- Supports gender filtering
- Fast timeout detection

```bash
curl -X POST /api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video_file=@video.mp4" \
  -F "provider=huggingface" \
  -F "gender=male"
```

### **Provider: "replicate"**
- Use Replicate Pro only
- No gender filtering
- Stable, reliable

```bash
curl -X POST /api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video_file=@video.mp4" \
  -F "provider=replicate"
```

---

## 🔧 Troubleshooting

### Error: "HUGGINGFACE_PRO_TOKEN required"
**Solution**: Add token to environment
```bash
export HUGGINGFACE_PRO_TOKEN="hf_xxxxx"
```

### Error: "All HuggingFace models failed"
**Solution**: Use Replicate fallback
```bash
# Use auto provider (automatic fallback)
provider=auto

# Or force Replicate
provider=replicate
```

### Video too large (timeout)
**Solution**: 
1. Use shorter videos (<30s)
2. Use Replicate provider (better for large files)
3. Compress video before upload

### Gender filter not working
**Solution**: Use HuggingFace provider
```bash
provider=huggingface
gender=male  # or female
```

---

## 📊 Performance

| Provider | Speed | Timeout | Reliability | Gender Filter |
|----------|-------|---------|-------------|---------------|
| HuggingFace Pro | Fast | 5-7s/model | High (multi-model) | ✅ |
| Replicate Pro | Medium | 30-60s | Very High | ❌ |
| Auto | Best | Adaptive | Highest | ✅ (via HF) |

---

## 🎯 Best Practices

1. **Use "auto" provider** for best reliability
2. **Use HuggingFace** when gender filtering needed
3. **Use Replicate** for large videos or when HF fails
4. **Keep videos under 30 seconds** for best performance
5. **Use high-quality face images** (512x512+) for better results
6. **Handle both JSON and binary responses** in your app

---

## 📝 Example Use Cases

### 1. Mobile App Face Swap
```dart
// Auto provider with gender filter
await service.swapFaceInVideo(
  faceImage: myFace,
  videoFile: targetVideo,
  provider: 'auto',
  gender: 'all'
);
```

### 2. Batch Processing
```python
videos = ['video1.mp4', 'video2.mp4', 'video3.mp4']
for video in videos:
    result = video_face_swap('face.jpg', video, provider='replicate')
    print(f'Processed: {video} -> {result}')
```

### 3. Template Video Swap
```python
# Swap face into pre-made template videos
templates = {
    'dancing': 'templates/dance.mp4',
    'singing': 'templates/sing.mp4'
}

for name, template_video in templates.items():
    result = video_face_swap(user_face, template_video)
    save_result(f'{name}_output.mp4', result)
```

---

## 🚀 Next Steps

1. ✅ Test API with sample video/image
2. ✅ Integrate into Flutter app
3. ✅ Handle loading states & errors
4. ✅ Add video preview/playback
5. ✅ Implement download functionality
6. ✅ Add template video library

---

## 📚 Resources

- **HuggingFace Models**: https://huggingface.co/spaces/tonyassi/video-face-swap
- **Replicate Models**: https://replicate.com/yan-ops/face_swap
- **Test Script**: `test_video_swap.py`
- **API Docs**: `GET /api` endpoint

---

**Created**: 2025-10-10  
**API Version**: 1.0.0  
**Status**: Production Ready ✅
