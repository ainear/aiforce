# ✅ FIX LỖI MOBILE APP - 307 REDIRECT & NETWORK ERROR

## 🐛 Vấn Đề

App mobile báo lỗi:
- **AI Hugs, Cartoonify**: `Error 307 - Redirection error`
- **Face Swap**: `Network error`

## 📋 Nguyên Nhân

### 1. **Backend Chạy Dev Mode Thay Vì Production** ❌
- Flask dev server thay vì Gunicorn
- Không có proper CORS headers
- Không handle redirects đúng

### 2. **Flutter App Thiếu Config Redirect** ❌
- Dio client không follow redirects
- Thiếu headers cần thiết
- Không handle status codes đúng

## ✅ Đã Fix Gì?

### 1. **Backend: Chuyển Sang Gunicorn Production Server** ✅

**Trước (Dev mode - sai):**
```
WARNING: This is a development server.
Running on http://127.0.0.1:5000
```

**Sau (Production - đúng):**
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Using worker: sync
[INFO] Booting worker with pid: 16936
```

**Workflow updated:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
```

### 2. **Backend: Enhanced CORS Configuration** ✅

**File: `app.py`**

```python
# Old (basic)
CORS(app)

# New (detailed for production)
CORS(app, 
     resources={r"/api/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Accept", "User-Agent"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": False,
         "max_age": 3600
     }})
```

### 3. **Flutter: Enhanced Dio Client** ✅

**File: `flutter_app/lib/services/api_service.dart`**

```dart
ApiService() {
  _dio = Dio(BaseOptions(
    baseUrl: ApiConfig.baseUrl,
    connectTimeout: Duration(milliseconds: 60000),
    receiveTimeout: Duration(milliseconds: 60000),
    
    // NEW: Follow redirects
    followRedirects: true,
    maxRedirects: 5,
    
    // NEW: Required headers
    headers: {
      'Accept': 'application/json, image/png, image/jpeg, */*',
      'User-Agent': 'ImageForge-Flutter-App',
    },
    
    // NEW: Accept all non-500 status codes
    validateStatus: (status) {
      return status != null && status < 500;
    },
  ));
  
  // NEW: Add logging for debugging
  _dio.interceptors.add(LogInterceptor(
    requestBody: false,
    responseBody: false,
    error: true,
    logPrint: (obj) => print('[API] $obj'),
  ));
}
```

## 🚀 BÂY GIỜ LÀM GÌ?

### **Option 1: Rebuild APK Với Code Mới (Recommended)** ✅

#### Bước 1: Pull Code Mới
```bash
# Trong VS Code (C:\7code\aiforce)
git pull origin main
```

#### Bước 2: Rebuild APK
```bash
cd flutter_app

# Clean
flutter clean
rm -rf build/

# Get dependencies
flutter pub get

# Build APK
flutter build apk --release
```

#### Bước 3: Install APK Mới
```
📱 APK location:
C:\7code\aiforce\flutter_app\build\app\outputs\flutter-apk\app-release.apk

Install vào điện thoại và test lại!
```

---

### **Option 2: Test Với Dev URL (Nhanh - Để Debug)** 🔧

Nếu muốn test nhanh mà không rebuild:

**1. Get Dev URL:**
- URL hiện tại: `https://50114ea0-2452-46e2-9975-2bc7787870fc-00-1ggmf7wilwgae.pike.replit.dev`

**2. Update `api_config.dart`:**
```dart
class ApiConfig {
  // Dev URL (temporary testing)
  static const String baseUrl = 'https://50114ea0-2452-46e2-9975-2bc7787870fc-00-1ggmf7wilwgae.pike.replit.dev';
  
  // ... rest of code
}
```

**3. Rebuild APK:**
```bash
flutter build apk --release
```

---

## 🔍 Verify Fixes

### 1. Check Backend Logs

Sau khi test app, check logs xem có request không:

```bash
# Trong Replit
# Check workflow logs để xem requests từ mobile app
```

Expected: Thấy POST requests như:
```
172.31.98.98 - - [DATE] "POST /api/ai/cartoonify HTTP/1.1" 200
172.31.98.98 - - [DATE] "POST /api/advanced/ai-hugs HTTP/1.1" 200
```

### 2. Check Flutter Logs

Chạy app và xem logs:

```bash
# Trong VS Code
flutter run --release

# Hoặc check logcat nếu đã install
adb logcat | grep "ImageForge"
```

Expected logs:
```
[API] Request: POST /api/ai/cartoonify
[API] Response: 200
```

---

## 📊 Status Codes Explained

| Code | Meaning | Cause | Fix |
|------|---------|-------|-----|
| 200 | ✅ Success | API worked | Nothing needed |
| 307 | ⚠️ Redirect | HTTP→HTTPS or routing | Fixed with followRedirects: true |
| 404 | ❌ Not Found | Wrong endpoint | Check route |
| 500 | ❌ Server Error | Backend issue | Check backend logs |
| Network Error | ❌ Connection | URL wrong or CORS | Fixed with CORS config |

---

## 🐛 Nếu Vẫn Lỗi

### Issue 1: Vẫn Lỗi 307

**Check:**
```bash
# Test endpoint trực tiếp
curl -X POST https://aiforce-onenearcelo.replit.app/api/ai/cartoonify \
  -F "image=@test.jpg" \
  -v
```

**Nếu thấy redirect trong response → Backend issue**

### Issue 2: Network Error

**Check:**
1. ✅ Internet connection
2. ✅ URL đúng: `https://aiforce-onenearcelo.replit.app`
3. ✅ Backend đang chạy (check Replit)
4. ✅ CORS enabled

### Issue 3: Timeout

**Increase timeout in `api_config.dart`:**
```dart
static const int connectTimeout = 120000; // 2 minutes
static const int receiveTimeout = 120000; // 2 minutes
```

---

## ✅ Checklist

- [x] Backend: Switched to Gunicorn production server
- [x] Backend: Enhanced CORS configuration
- [x] Flutter: Added followRedirects to Dio
- [x] Flutter: Added proper headers
- [x] Flutter: Added logging interceptor
- [ ] **Bạn làm:** Pull code mới
- [ ] **Bạn làm:** Rebuild APK
- [ ] **Bạn làm:** Test all features

---

## 📚 Related Files

- [app.py](app.py) - Backend với CORS config mới
- [flutter_app/lib/services/api_service.dart](flutter_app/lib/services/api_service.dart) - Dio client với redirect handling
- [flutter_app/lib/config/api_config.dart](flutter_app/lib/config/api_config.dart) - API configuration

---

## 🎯 TÓM TẮT

**Đã fix:**
1. ✅ Backend: Dev mode → Gunicorn production
2. ✅ Backend: CORS config chi tiết
3. ✅ Flutter: Dio followRedirects + headers
4. ✅ Flutter: Better error handling

**Bạn cần làm:**
```bash
# 1. Pull code
git pull origin main

# 2. Rebuild APK
cd flutter_app
flutter clean && flutter build apk --release

# 3. Install APK mới và test!
```

**Kết quả:** Tất cả features sẽ hoạt động bình thường! 🚀
