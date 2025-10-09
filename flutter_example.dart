// ============================================
// ImageForge AI - Flutter Integration Example
// ============================================

import 'dart:io';
import 'package:dio/dio.dart';

// 1. API Service Class
class ImageForgeAPI {
  static const String baseUrl = 'https://YOUR_REPLIT_URL.replit.app';
  final Dio _dio = Dio(BaseOptions(baseUrl: baseUrl));

  /// Main method: Process image and save to Supabase
  Future<Map<String, dynamic>> processAndSave({
    required String imagePath,
    required String feature, // 'cartoonify', 'hd-upscale', 'remove-bg', 'restore'
    bool saveToStorage = true,
    String? userId,
    int? scale,
    String? style,
  }) async {
    FormData formData = FormData.fromMap({
      'image': await MultipartFile.fromFile(imagePath),
      'feature': feature,
      'save_storage': saveToStorage.toString(),
      if (userId != null) 'user_id': userId,
      if (scale != null) 'scale': scale.toString(),
      if (style != null) 'style': style,
    });

    Response response = await _dio.post('/api/ai/process-and-save', data: formData);
    return response.data;
  }
}

// 2. Usage Example
void main() async {
  final api = ImageForgeAPI();
  
  // Example: Cartoonify image
  var result = await api.processAndSave(
    imagePath: '/path/to/image.jpg',
    feature: 'cartoonify',
    saveToStorage: true,
    userId: 'demo-user-123',
    style: 'anime',
  );
  
  print('Success: ${result['success']}');
  print('Image URL: ${result['storage_url']}');
  print('Filename: ${result['filename']}');
}

// 3. Available Features
/*
  - cartoonify (style: anime, cartoon, sketch)
  - hd-upscale (scale: 2, 4)
  - remove-bg
  - restore
*/

// 4. Response Format (with storage)
/*
{
  "success": true,
  "message": "Image processed and saved to Supabase",
  "storage_url": "https://[project].supabase.co/storage/v1/object/public/ai-photos/...",
  "filename": "cartoonify_20251009_075440_abc123.png",
  "path": "user-123/cartoonify_20251009_075440_abc123.png",
  "feature": "cartoonify"
}
*/
