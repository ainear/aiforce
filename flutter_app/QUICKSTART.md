# 🚀 Quick Start Guide - 5 Phút Setup

## Bước 1: Cài đặt (1 phút)

```bash
cd flutter_app
flutter pub get
```

## Bước 2: Cấu hình API URL (30 giây)

Mở `lib/config/api_config.dart`:

```dart
static const String baseUrl = 'https://YOUR_REPLIT_URL.replit.app';
```

### Lấy URL từ đâu?
1. Mở Replit của bạn
2. Nhìn vào webview preview (port 5000)
3. Copy URL (dạng: `https://abc-xyz-123.replit.app`)
4. Paste vào `api_config.dart`

## Bước 3: Chạy App (30 giây)

```bash
# Kiểm tra devices
flutter devices

# Chạy trên device/emulator
flutter run
```

Hoặc dùng IDE:
- **VS Code**: F5 hoặc Run > Start Debugging
- **Android Studio**: Click Run button

## Bước 4: Test Features (3 phút)

### Test cơ bản:
1. Mở app → Chọn "Cartoonify"
2. Tap "Chọn ảnh" → Chọn 1 ảnh từ gallery
3. Chọn style: Anime/Cartoon/Sketch
4. Tap "Áp dụng AI Effect"
5. Đợi 10-30 giây
6. Xem kết quả!

### Test Template Face Swap:
1. Mở app → Chọn "Template Swap"
2. Chọn 1 template từ gallery
3. Upload ảnh khuôn mặt của bạn
4. Tap "Swap Face with Template"
5. Xem kết quả magic!

## ✅ Checklist Setup

- [ ] `flutter pub get` chạy thành công
- [ ] Đã thay API URL trong `api_config.dart`
- [ ] Backend API đang chạy (check Replit webview)
- [ ] Device/emulator đã kết nối
- [ ] App build thành công
- [ ] Đã test ít nhất 1 feature

## 🐛 Common Issues

### Error: "Connection refused"
→ **Fix**: Backend chưa chạy, restart Replit workflow

### Error: "Image picker không hoạt động"
→ **Fix**: Permissions chưa được cấp, check AndroidManifest.xml

### Error: "Package not found"
→ **Fix**: Chạy `flutter pub get` lại

### Ảnh không load
→ **Fix**: Kiểm tra API URL đã đúng chưa

## 📱 Test Checklist

Sau khi chạy app, test các features:

**Basic Features:**
- [ ] HD Upscale (2x/4x)
- [ ] Cartoonify (anime/cartoon/sketch)
- [ ] Remove Background
- [ ] Restore Old Photo

**Advanced Features:**
- [ ] AI Hugs (2 ảnh)
- [ ] Future Baby (2 ảnh)
- [ ] Face Swap (2 ảnh)
- [ ] Template Swap

**UI/UX:**
- [ ] Image picker hoạt động
- [ ] Loading indicator hiển thị
- [ ] Kết quả hiển thị đúng
- [ ] Lưu ảnh thành công

## 🎯 Next Steps

1. ✅ Test tất cả features
2. ✅ Customize UI/colors (nếu muốn)
3. ✅ Build APK/IPA để test trên thiết bị thật
4. ✅ Deploy backend lên production

## 📞 Cần giúp?

1. Check logs trong terminal
2. Đọc README.md đầy đủ
3. Xem API_INTEGRATION.md để hiểu API endpoints
4. Check network inspector nếu API fail

---

**⏱️ Total time: ~5 phút**
**🎉 Enjoy testing your AI features!**
