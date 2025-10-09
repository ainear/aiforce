# 🚀 Hướng Dẫn Chạy Flutter App - ImageForge AI

## ✅ Setup trong 3 bước đơn giản

### Bước 1: Cài đặt Flutter SDK (nếu chưa có)

#### Windows
```bash
# Download Flutter SDK từ: https://docs.flutter.dev/get-started/install/windows
# Giải nén và thêm vào PATH
```

#### macOS
```bash
# Dùng Homebrew
brew install flutter
```

#### Linux
```bash
# Download từ: https://docs.flutter.dev/get-started/install/linux
```

Kiểm tra:
```bash
flutter doctor
```

---

### Bước 2: Setup Project

```bash
# Di chuyển vào thư mục Flutter app
cd flutter_app

# Cài đặt dependencies
flutter pub get
```

---

### Bước 3: Cấu hình API URL

**Mở file:** `flutter_app/lib/config/api_config.dart`

**Thay đổi dòng này:**
```dart
static const String baseUrl = 'https://YOUR_REPLIT_URL.replit.app';
```

**Lấy URL từ đâu?**
1. Mở Replit project của bạn
2. Server đang chạy ở port 5000
3. Copy URL từ webview preview
4. Ví dụ: `https://abc-xyz-123-456.replit.app`

---

## 🎮 Chạy App

### Option 1: Command Line (Nhanh nhất)

```bash
# Liệt kê devices
flutter devices

# Chạy trên device/emulator
flutter run
```

### Option 2: VS Code

1. Mở thư mục `flutter_app` trong VS Code
2. Cài extension "Flutter" và "Dart"
3. Chọn device từ thanh status bar
4. Nhấn F5 hoặc Run > Start Debugging

### Option 3: Android Studio

1. Mở thư mục `flutter_app` như project
2. Chọn device từ toolbar
3. Click Run button (▶️)

---

## 📱 Setup Device/Emulator

### Android Emulator

```bash
# Tạo emulator mới
flutter emulators --create

# Hoặc dùng Android Studio > AVD Manager > Create Virtual Device
```

### iOS Simulator (chỉ macOS)

```bash
# Mở simulator
open -a Simulator
```

### Physical Device

**Android:**
1. Bật Developer Options
2. Bật USB Debugging
3. Kết nối qua USB

**iOS:**
1. Kết nối iPhone qua USB
2. Trust computer
3. Run từ Xcode

---

## 🎯 Test Features

### 1. Test Basic Feature (HD Upscale)

1. Mở app
2. Scroll xuống section "Enhancement"
3. Tap vào "HD Upscale"
4. Tap "Chọn ảnh" → Chọn 1 ảnh
5. Chọn scale: 2x hoặc 4x
6. Tap "Áp dụng AI Effect"
7. Đợi ~10-30 giây
8. Xem kết quả!

### 2. Test Template Face Swap

1. Mở app
2. Scroll xuống section "Top Hits"
3. Tap vào "Template Swap"
4. Chọn 1 template từ gallery
5. Tap "Tải ảnh của bạn lên"
6. Chọn ảnh khuôn mặt
7. Tap "Swap Face with Template"
8. Xem kết quả magic!

### 3. Test AI Hugs

1. Tap vào "AI Hugs" (Top Hits)
2. Upload ảnh người thứ 1
3. Upload ảnh người thứ 2
4. Tap "Áp dụng AI Effect"
5. Xem ảnh ôm nhau!

---

## 🐛 Troubleshooting

### ❌ Error: "Connection refused"

**Nguyên nhân:** Backend API chưa chạy

**Fix:**
```bash
# Quay lại Replit, restart workflow
python app.py
```

---

### ❌ Error: "No devices found"

**Fix:**
```bash
# Kiểm tra devices
flutter devices

# Nếu rỗng, tạo emulator:
flutter emulators --create

# Hoặc kết nối physical device
```

---

### ❌ Error: "Image picker không hoạt động"

**Android Fix:**
- Kiểm tra `android/app/src/main/AndroidManifest.xml`
- Đảm bảo có permissions: Camera, Storage

**iOS Fix:**
- Kiểm tra `ios/Runner/Info.plist`
- Đảm bảo có description cho Camera, Photo Library

---

### ❌ Error: "Package not found"

**Fix:**
```bash
flutter clean
flutter pub get
```

---

### ❌ API trả về error

**Kiểm tra:**
1. ✅ Backend đang chạy?
2. ✅ API URL đúng chưa?
3. ✅ Internet connection OK?
4. ✅ Check backend logs

---

## 📦 Build Production APK

### Android APK

```bash
flutter build apk --release
```

**Output:** `build/app/outputs/flutter-apk/app-release.apk`

**Test APK:**
```bash
flutter install
```

---

### iOS IPA (cần macOS + Xcode)

```bash
flutter build ios --release
```

---

## 🎨 Customize

### Đổi màu theme

**File:** `lib/main.dart`

```dart
theme: ThemeData(
  primarySwatch: Colors.blue,  // Đổi màu
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.blue,
  ),
),
```

### Đổi tên app

**Android:** `android/app/src/main/AndroidManifest.xml`
```xml
android:label="Tên App Mới"
```

**iOS:** `ios/Runner/Info.plist`
```xml
<key>CFBundleDisplayName</key>
<string>Tên App Mới</string>
```

---

## 📊 Features trong App

| Feature | Endpoint | Input |
|---------|----------|-------|
| HD Upscale | `/api/ai/hd-image` | 1 ảnh + scale (2/4) |
| Cartoonify | `/api/ai/cartoonify` | 1 ảnh + style |
| Remove BG | `/api/advanced/remove-background` | 1 ảnh |
| Restore Photo | `/api/ai/fix-old-photo` | 1 ảnh |
| Face Swap | `/api/ai/swap-face` | 2 ảnh |
| AI Hugs | `/api/advanced/ai-hugs` | 2 ảnh |
| Future Baby | `/api/advanced/future-baby` | 2 ảnh |
| Template Swap | `/api/templates/face-swap` | 1 ảnh + template_id |
| Style Transfer | `/api/ai/style-transfer` | 1 ảnh + style |
| Depth Map | `/api/advanced/depth-map` | 1 ảnh |
| Colorize | `/api/advanced/colorize` | 1 ảnh |

**Tổng: 11 features!**

---

## 📚 Tài Liệu Thêm

- 📖 [README.md](flutter_app/README.md) - Full documentation
- 🚀 [QUICKSTART.md](flutter_app/QUICKSTART.md) - 5-minute guide
- 📱 [FLUTTER_APP_SUMMARY.md](FLUTTER_APP_SUMMARY.md) - Complete summary
- 🔌 [API_INTEGRATION.md](API_INTEGRATION.md) - API docs

---

## ✅ Checklist

Trước khi chạy app:

- [ ] Flutter SDK đã cài đặt (`flutter doctor`)
- [ ] Dependencies đã cài (`flutter pub get`)
- [ ] API URL đã cấu hình (`api_config.dart`)
- [ ] Backend API đang chạy (Replit)
- [ ] Device/Emulator đã sẵn sàng
- [ ] Permissions đã cấu hình (Android/iOS)

Sau khi chạy app:

- [ ] App mở thành công
- [ ] Home screen hiển thị 11 features
- [ ] Test ít nhất 1 feature (HD Upscale)
- [ ] Image picker hoạt động
- [ ] Result hiển thị đúng

---

## 🎉 Kết Luận

App đã sẵn sàng! Chỉ cần 3 bước:

1. ✅ `flutter pub get`
2. ✅ Sửa API URL
3. ✅ `flutter run`

**Enjoy testing! 🚀**
