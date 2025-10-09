# ImageForge AI Tester - Flutter App

Flutter app đơn giản để test tất cả tính năng AI của ImageForge Backend API.

## 📱 Features

### Top Hits 🔥
- **AI Hugs** - Tạo ảnh ôm nhau từ 2 ảnh
- **Future Baby** - Dự đoán con cái tương lai
- **Cartoonify** - Chuyển thành cartoon/anime
- **Template Swap** - Face swap với templates có sẵn

### Enhancement 🎨
- **HD Upscale** - Tăng độ phân giải 2x/4x
- **Fix Old Photo** - Phục hồi ảnh cũ/mờ
- **Colorize** - Tô màu ảnh đen trắng

### Creative Tools 🖼️
- **Remove Background** - Xóa phông nền
- **Face Swap** - Hoán đổi khuôn mặt
- **Style Transfer** - Chuyển đổi phong cách nghệ thuật
- **Depth Map** - Tạo bản đồ độ sâu

## 🚀 Quick Start

### 1. Cài đặt Dependencies

```bash
cd flutter_app
flutter pub get
```

### 2. Cấu hình API URL

Mở file `lib/config/api_config.dart` và thay đổi URL:

```dart
static const String baseUrl = 'https://YOUR_REPLIT_URL.replit.app';
```

Lấy URL từ Replit webview của bạn (ví dụ: `https://abc123.replit.app`)

### 3. Chạy App

```bash
# Android
flutter run

# iOS (cần macOS)
flutter run

# Hoặc chọn device từ IDE (VS Code/Android Studio)
```

## 📦 Dependencies

```yaml
dependencies:
  # UI
  google_fonts: ^6.1.0
  
  # Networking
  dio: ^5.4.0
  http: ^1.1.2
  
  # Image
  image_picker: ^1.0.7
  cached_network_image: ^3.3.1
  photo_view: ^0.14.0
  
  # Storage & Permissions
  path_provider: ^2.1.2
  permission_handler: ^11.2.0
```

## 🔧 Platform Setup

### Android Permissions

File: `android/app/src/main/AndroidManifest.xml`

```xml
<manifest ...>
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    
    <application ...>
        ...
    </application>
</manifest>
```

### iOS Permissions

File: `ios/Runner/Info.plist`

```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>Cần truy cập thư viện ảnh để chọn ảnh cho AI processing</string>

<key>NSCameraUsageDescription</key>
<string>Cần truy cập camera để chụp ảnh</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>Cần quyền lưu ảnh vào thư viện</string>
```

## 📂 Project Structure

```
flutter_app/
├── lib/
│   ├── main.dart                    # Entry point
│   ├── config/
│   │   └── api_config.dart          # API configuration
│   ├── models/
│   │   ├── feature_model.dart       # Feature definitions
│   │   └── api_response.dart        # API response models
│   ├── services/
│   │   └── api_service.dart         # API client
│   ├── screens/
│   │   ├── home_screen.dart         # Main screen
│   │   ├── feature_detail_screen.dart
│   │   └── template_gallery_screen.dart
│   └── widgets/
│       ├── feature_card.dart        # Feature card widget
│       ├── image_picker_widget.dart # Image picker
│       └── result_display.dart      # Result display
├── pubspec.yaml
└── README.md
```

## 🎯 Usage Guide

### 1. Home Screen
- Hiển thị tất cả AI features theo category
- Tap vào feature card để mở detail screen

### 2. Feature Detail Screen
- Chọn ảnh từ gallery hoặc camera
- Điều chỉnh parameters (nếu có)
- Tap "Áp dụng AI Effect" để xử lý
- Xem kết quả và lưu ảnh

### 3. Template Gallery (Face Swap)
- Chọn template từ gallery
- Upload ảnh của bạn
- Tap "Swap Face with Template"
- Xem và lưu kết quả

## 🔄 API Integration

### Single Image Processing

```dart
final apiService = ApiService();

// HD Upscale
final response = await apiService.hdUpscale(imageFile, scale: 2);

// Cartoonify
final response = await apiService.cartoonify(imageFile, style: 'anime');

// Remove Background
final response = await apiService.removeBackground(imageFile);
```

### Two Images Processing

```dart
// Face Swap
final response = await apiService.faceSwap(sourceImage, targetImage);

// AI Hugs
final response = await apiService.aiHugs(person1, person2);

// Future Baby
final response = await apiService.futureBaby(parent1, parent2);
```

### Template Face Swap

```dart
// Get templates
final templatesResponse = await apiService.getTemplates();
List<TemplateModel> templates = templatesResponse.data ?? [];

// Swap with template
final response = await apiService.templateFaceSwap(userImage, templateId);
```

## 🐛 Troubleshooting

### Error: Connection refused
- Kiểm tra backend API đang chạy
- Kiểm tra API URL trong `api_config.dart`
- Đảm bảo device/emulator có internet

### Error: Image picker not working
- Kiểm tra permissions trong AndroidManifest.xml / Info.plist
- Request runtime permissions (tự động bởi image_picker package)

### Error: Cannot save image
- Kiểm tra storage permissions
- Sử dụng path_provider để lấy đúng thư mục

## 📸 Screenshots

### Home Screen
- Grid layout với các feature cards
- Stats card hiển thị tổng số features
- Phân loại theo categories

### Feature Detail
- Image picker với preview
- Parameter controls (scale, style)
- Processing indicator
- Result display với zoom

### Template Gallery
- Grid của template images
- Category filter
- Selected state indicator
- Face swap processing

## 🎨 Customization

### Thay đổi màu sắc

File: `lib/main.dart`

```dart
theme: ThemeData(
  primarySwatch: Colors.purple,  // Đổi màu chủ đạo
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.purple,    // Đổi seed color
  ),
),
```

### Thêm feature mới

1. Thêm vào `FeatureType` enum trong `feature_model.dart`
2. Thêm endpoint trong `api_config.dart`
3. Thêm method trong `api_service.dart`
4. Thêm feature vào `AIFeatures.categories`
5. Cập nhật `_callApiBasedOnType()` trong `feature_detail_screen.dart`

## 🚢 Build & Release

### Android APK

```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### iOS IPA (cần macOS)

```bash
flutter build ios --release
```

### Web (nếu cần)

```bash
flutter build web
```

## 📝 Notes

- App yêu cầu internet để gọi API
- Processing time: 5-60 giây tùy vào model
- Hỗ trợ Android 21+ và iOS 12+
- Ảnh được lưu vào app documents directory

## 🔗 Related Documentation

- [Backend API Documentation](../API_INTEGRATION.md)
- [Supabase Integration](../SUPABASE_INTEGRATION.md)
- [Setup Summary](../SETUP_SUMMARY.md)

## 🆘 Support

Nếu gặp vấn đề:
1. Kiểm tra backend API đang chạy
2. Xem logs trong console
3. Check network inspector
4. Đọc error messages từ API response

## 📄 License

MIT License - Free to use for testing purposes
