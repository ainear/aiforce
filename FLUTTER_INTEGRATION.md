# Flutter Integration Guide - ImageForge AI API

Hướng dẫn tích hợp ImageForge AI API vào Flutter app.

## 📦 Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  image_picker: ^1.0.4
  dio: ^5.3.3  # Alternative to http
  path_provider: ^2.1.1
```

## 🔧 API Service Class

### 1. Create API Service (`lib/services/imageforge_api.dart`)

```dart
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:http/http.dart' as http;

class ImageForgeAPI {
  // Thay YOUR_REPLIT_URL bằng URL thực tế của bạn
  static const String baseUrl = 'https://YOUR_REPLIT_URL.replit.app';
  
  final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 60),
    receiveTimeout: const Duration(seconds: 60),
  ));

  // ====== MAIN ENDPOINT: Process and Save ======
  
  /// Process image with AI and save to Supabase
  /// 
  /// [imagePath] - Path to local image file
  /// [feature] - AI feature: 'hd-upscale', 'cartoonify', 'restore', 'remove-bg'
  /// [saveToStorage] - true to save to Supabase, false to get image bytes
  /// [userId] - Optional user ID for organizing files
  /// [scale] - For hd-upscale: 2 or 4
  /// [style] - For cartoonify: 'anime', 'cartoon', 'sketch'
  Future<ProcessResult> processAndSave({
    required String imagePath,
    required String feature,
    bool saveToStorage = true,
    String? userId,
    int? scale,
    String? style,
  }) async {
    try {
      FormData formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(imagePath),
        'feature': feature,
        'save_storage': saveToStorage.toString(),
        if (userId != null) 'user_id': userId,
        if (scale != null) 'scale': scale.toString(),
        if (style != null) 'style': style,
      });

      Response response = await _dio.post(
        '/api/ai/process-and-save',
        data: formData,
      );

      if (saveToStorage) {
        // Response is JSON with storage URL
        return ProcessResult(
          success: true,
          storageUrl: response.data['storage_url'],
          filename: response.data['filename'],
          path: response.data['path'],
          message: response.data['message'],
        );
      } else {
        // Response is image bytes
        return ProcessResult(
          success: true,
          imageBytes: response.data,
        );
      }
    } catch (e) {
      return ProcessResult(
        success: false,
        error: e.toString(),
      );
    }
  }

  // ====== INDIVIDUAL FEATURE ENDPOINTS ======

  /// HD Upscale (2x or 4x)
  Future<List<int>?> hdUpscale(String imagePath, {int scale = 2}) async {
    try {
      FormData formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(imagePath),
        'scale': scale.toString(),
      });

      Response response = await _dio.post(
        '/api/ai/hd-upscale',
        data: formData,
        options: Options(responseType: ResponseType.bytes),
      );

      return response.data as List<int>;
    } catch (e) {
      print('HD Upscale error: $e');
      return null;
    }
  }

  /// Cartoonify
  Future<List<int>?> cartoonify(String imagePath, {String style = 'anime'}) async {
    try {
      FormData formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(imagePath),
        'style': style,
      });

      Response response = await _dio.post(
        '/api/ai/cartoonify',
        data: formData,
        options: Options(responseType: ResponseType.bytes),
      );

      return response.data as List<int>;
    } catch (e) {
      print('Cartoonify error: $e');
      return null;
    }
  }

  /// Remove Background
  Future<List<int>?> removeBackground(String imagePath) async {
    try {
      FormData formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(imagePath),
      });

      Response response = await _dio.post(
        '/api/ai/remove-background',
        data: formData,
        options: Options(responseType: ResponseType.bytes),
      );

      return response.data as List<int>;
    } catch (e) {
      print('Remove BG error: $e');
      return null;
    }
  }

  /// Restore Old Photo
  Future<List<int>?> restorePhoto(String imagePath) async {
    try {
      FormData formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(imagePath),
      });

      Response response = await _dio.post(
        '/api/ai/restore-photo',
        data: formData,
        options: Options(responseType: ResponseType.bytes),
      );

      return response.data as List<int>;
    } catch (e) {
      print('Restore error: $e');
      return null;
    }
  }
}

// ====== RESULT MODELS ======

class ProcessResult {
  final bool success;
  final String? storageUrl;
  final String? filename;
  final String? path;
  final String? message;
  final List<int>? imageBytes;
  final String? error;

  ProcessResult({
    required this.success,
    this.storageUrl,
    this.filename,
    this.path,
    this.message,
    this.imageBytes,
    this.error,
  });
}
```

## 📱 Example Flutter Screen

### 2. Create UI Screen (`lib/screens/ai_editor_screen.dart`)

```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/imageforge_api.dart';

class AIEditorScreen extends StatefulWidget {
  @override
  _AIEditorScreenState createState() => _AIEditorScreenState();
}

class _AIEditorScreenState extends State<AIEditorScreen> {
  final ImageForgeAPI _api = ImageForgeAPI();
  final ImagePicker _picker = ImagePicker();
  
  File? _selectedImage;
  String? _resultImageUrl;
  bool _isProcessing = false;
  String _selectedFeature = 'cartoonify';
  
  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      setState(() {
        _selectedImage = File(image.path);
        _resultImageUrl = null;
      });
    }
  }

  Future<void> _processImage() async {
    if (_selectedImage == null) return;

    setState(() => _isProcessing = true);

    try {
      // Process and save to Supabase
      ProcessResult result = await _api.processAndSave(
        imagePath: _selectedImage!.path,
        feature: _selectedFeature,
        saveToStorage: true,
        userId: 'flutter-user-123', // Replace with actual user ID
        style: _selectedFeature == 'cartoonify' ? 'anime' : null,
        scale: _selectedFeature == 'hd-upscale' ? 2 : null,
      );

      if (result.success && result.storageUrl != null) {
        setState(() {
          _resultImageUrl = result.storageUrl;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ ${result.message}')),
        );
      } else {
        throw Exception(result.error ?? 'Unknown error');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Error: $e')),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('ImageForge AI'),
        backgroundColor: Colors.deepPurple,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Feature Selector
            Card(
              child: Padding(
                padding: EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Select AI Feature:', 
                      style: TextStyle(fontWeight: FontWeight.bold)),
                    SizedBox(height: 8),
                    DropdownButton<String>(
                      value: _selectedFeature,
                      isExpanded: true,
                      items: [
                        DropdownMenuItem(value: 'cartoonify', child: Text('🎨 Cartoonify')),
                        DropdownMenuItem(value: 'hd-upscale', child: Text('⬆️ HD Upscale')),
                        DropdownMenuItem(value: 'remove-bg', child: Text('🖼️ Remove Background')),
                        DropdownMenuItem(value: 'restore', child: Text('🔧 Restore Photo')),
                      ],
                      onChanged: (value) {
                        setState(() => _selectedFeature = value!);
                      },
                    ),
                  ],
                ),
              ),
            ),
            
            SizedBox(height: 16),
            
            // Image Picker
            if (_selectedImage == null)
              ElevatedButton.icon(
                onPressed: _pickImage,
                icon: Icon(Icons.photo_library),
                label: Text('Select Image'),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.all(16),
                ),
              )
            else
              Column(
                children: [
                  Image.file(_selectedImage!, height: 200, fit: BoxFit.cover),
                  SizedBox(height: 8),
                  TextButton(
                    onPressed: _pickImage,
                    child: Text('Change Image'),
                  ),
                ],
              ),
            
            SizedBox(height: 16),
            
            // Process Button
            ElevatedButton.icon(
              onPressed: _selectedImage == null || _isProcessing 
                ? null 
                : _processImage,
              icon: _isProcessing 
                ? SizedBox(
                    width: 20, 
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Icon(Icons.auto_fix_high),
              label: Text(_isProcessing ? 'Processing...' : 'Apply AI Effect'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.all(16),
                backgroundColor: Colors.deepPurple,
              ),
            ),
            
            SizedBox(height: 24),
            
            // Result Image
            if (_resultImageUrl != null)
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Result:', 
                    style: TextStyle(
                      fontSize: 18, 
                      fontWeight: FontWeight.bold,
                    )),
                  SizedBox(height: 8),
                  Image.network(_resultImageUrl!, 
                    loadingBuilder: (context, child, progress) {
                      if (progress == null) return child;
                      return Center(child: CircularProgressIndicator());
                    },
                  ),
                  SizedBox(height: 8),
                  Text('Saved to: $_resultImageUrl', 
                    style: TextStyle(fontSize: 10, color: Colors.grey)),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
```

## 🚀 Quick Start

### 3. Update `main.dart`

```dart
import 'package:flutter/material.dart';
import 'screens/ai_editor_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ImageForge AI',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
      ),
      home: AIEditorScreen(),
    );
  }
}
```

## 📝 Usage Examples

### Example 1: Cartoonify Image

```dart
final api = ImageForgeAPI();

ProcessResult result = await api.processAndSave(
  imagePath: '/path/to/image.jpg',
  feature: 'cartoonify',
  saveToStorage: true,
  userId: 'user-123',
  style: 'anime',
);

if (result.success) {
  print('Image saved at: ${result.storageUrl}');
}
```

### Example 2: HD Upscale

```dart
ProcessResult result = await api.processAndSave(
  imagePath: '/path/to/image.jpg',
  feature: 'hd-upscale',
  saveToStorage: true,
  userId: 'user-123',
  scale: 4, // 4x upscale
);
```

### Example 3: Get Image Bytes (without saving)

```dart
ProcessResult result = await api.processAndSave(
  imagePath: '/path/to/image.jpg',
  feature: 'remove-bg',
  saveToStorage: false, // Don't save to Supabase
);

if (result.success && result.imageBytes != null) {
  // Use image bytes directly
  File outputFile = File('/output/path.png');
  await outputFile.writeAsBytes(result.imageBytes!);
}
```

## 🔧 Configuration

### Update API Base URL

In `imageforge_api.dart`, replace with your actual Replit URL:

```dart
static const String baseUrl = 'https://your-project-name.replit.app';
```

### Android Permissions (`android/app/src/main/AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
```

### iOS Permissions (`ios/Runner/Info.plist`)

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>We need access to your photos to apply AI effects</string>
<key>NSCameraUsageDescription</key>
<string>We need camera access to take photos</string>
```

## 📊 Available Features

| Feature | Endpoint | Parameters |
|---------|----------|------------|
| **HD Upscale** | `/api/ai/process-and-save` | `feature=hd-upscale`, `scale=2 or 4` |
| **Cartoonify** | `/api/ai/process-and-save` | `feature=cartoonify`, `style=anime/cartoon/sketch` |
| **Remove BG** | `/api/ai/process-and-save` | `feature=remove-bg` |
| **Restore Photo** | `/api/ai/process-and-save` | `feature=restore` |

## 🌐 Response Format

### With Storage (save_storage=true)

```json
{
  "success": true,
  "message": "Image processed and saved to Supabase",
  "storage_url": "https://[project].supabase.co/storage/v1/object/public/ai-photos/user-123/cartoonify_20251009_075440_abc123.png",
  "filename": "cartoonify_20251009_075440_abc123.png",
  "path": "user-123/cartoonify_20251009_075440_abc123.png",
  "feature": "cartoonify"
}
```

### Without Storage (save_storage=false)

Returns raw image bytes (PNG format)

## 🎯 Next Steps

1. ✅ Replace `YOUR_REPLIT_URL` with actual Replit URL
2. ✅ Add user authentication
3. ✅ Implement image gallery to view saved images
4. ✅ Add download/share functionality
5. ✅ Handle errors gracefully

## 🔗 Related Documentation

- [API_INTEGRATION.md](API_INTEGRATION.md) - Full API documentation
- [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md) - Supabase setup guide
