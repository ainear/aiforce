# 🚨 FIX LỖI PRODUCTION - REPLIT SHIELD BLOCKING

## ⚠️ VẤN ĐỀ

Mobile app báo lỗi **"Exception: Network error"** cho TẤT CẢ tính năng khi gọi production URL:
```
https://aiforce-onenearcelo.replit.app
```

## 🔍 NGUYÊN NHÂN

**Replit Shield** đang block external requests!

```bash
# Test production URL:
curl -I https://aiforce-onenearcelo.replit.app/healthz

# Kết quả:
HTTP/2 307 
location: https://replit.com/__replshield?redirect=...
```

→ Tất cả requests bị redirect đến Replit Shield page thay vì đến app!

## ✅ GIẢI PHÁP

### **Option 1: Disable Replit Shield (RECOMMENDED)** ⭐

Bạn cần vào Replit Deployment settings và **tắt Replit Shield**:

1. **Vào Replit project:** https://replit.com/@onenearcelo/aiforce

2. **Click tab "Deployments"** (biểu tượng rocket 🚀)

3. **Click vào deployment hiện tại** (aiforce-onenearcelo.replit.app)

4. **Tìm "Security" hoặc "Shield" settings**

5. **Disable/Turn OFF "Replit Shield"** hoặc "External Access Protection"

6. **Save/Apply changes**

7. **Test lại:**
   ```bash
   curl https://aiforce-onenearcelo.replit.app/healthz
   # Should return: {"status":"ok"}
   ```

### **Option 2: Use Replit Auth**

Nếu muốn giữ Shield, cần integrate Replit Auth vào Flutter app (phức tạp hơn).

### **Option 3: Custom Domain**

Setup custom domain sẽ bypass Replit Shield (cần domain riêng).

---

## 🧪 KIỂM TRA SAU KHI FIX

### 1. Test Production Health Check:
```bash
curl https://aiforce-onenearcelo.replit.app/healthz
```

**Expected:**
```json
{"status":"ok"}
```

### 2. Test Templates Endpoint:
```bash
curl https://aiforce-onenearcelo.replit.app/api/templates/list
```

**Expected:**
```json
{
  "status": "success",
  "templates": [...],
  "total": 15
}
```

### 3. Test từ Mobile App:

Sau khi disable Shield, test lại tất cả features:
- ✅ AI Hugs
- ✅ Face Swap
- ✅ Template Face Swap
- ✅ Cartoonify
- ✅ HD Upscale
- ...tất cả 11 features

---

## 🔧 TẠM THỜI: DÙNG DEV URL

**Nếu không thể disable Shield ngay**, tạm thời sử dụng **Development URL**:

### Cách 1: Deploy riêng mới

1. Trong Replit, click "Deploy" → "New Deployment"
2. Chọn deployment type khác (không có Shield)
3. Copy URL mới

### Cách 2: Local Backend (Testing Only)

Sử dụng ngrok để expose local backend:

```bash
# Install ngrok
npm install -g ngrok

# Expose local backend
ngrok http 5000

# Copy HTTPS URL (e.g., https://abc123.ngrok.io)
# Update Flutter app config
```

**Update Flutter:**
```dart
// flutter_app/lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'https://YOUR-NGROK-URL';  // ← Change here
  // ...
}
```

---

## 📱 FLUTTER APP CONFIG

Sau khi có URL hoạt động (sau khi disable Shield hoặc dùng ngrok):

**File: `flutter_app/lib/config/api_config.dart`**

```dart
class ApiConfig {
  // Production API URL (sau khi disable Shield)
  static const String baseUrl = 'https://aiforce-onenearcelo.replit.app';
  
  // Hoặc dùng custom URL nếu cần:
  // static const String baseUrl = 'https://your-custom-domain.com';
  // static const String baseUrl = 'https://abc123.ngrok.io';
  
  // Timeouts
  static const int connectTimeout = 60000;
  static const int receiveTimeout = 60000;
}
```

---

## 🎯 CHECKLIST

- [ ] **Bước 1:** Vào Replit Deployments settings
- [ ] **Bước 2:** Disable Replit Shield
- [ ] **Bước 3:** Test health check endpoint với curl
- [ ] **Bước 4:** Test templates endpoint
- [ ] **Bước 5:** Pull Flutter code mới (nếu có update)
- [ ] **Bước 6:** Rebuild APK
- [ ] **Bước 7:** Test tất cả features trên mobile

---

## 📸 SCREENSHOTS CẦN TÌM

Trong Replit Deployments settings, tìm:
- ⚙️ **Security Settings**
- 🛡️ **Replit Shield** toggle
- 🔒 **External Access** options
- 🌐 **Public Access** settings

**Turn OFF/Disable** bất kỳ protection nào đang block external requests.

---

## ⚡ EXPECTED RESULT

Sau khi disable Shield:

**✅ Curl test:**
```bash
$ curl https://aiforce-onenearcelo.replit.app/api/templates/list
{
  "status": "success",
  "templates": [
    {
      "id": "female_bedroom_aesthetic",
      "name": "Bedroom Aesthetic",
      "imageUrl": "https://aiforce-onenearcelo.replit.app/static/templates/female/bedroom_aesthetic.jpg",
      "category": "Female"
    },
    ...
  ],
  "total": 15
}
```

**✅ Mobile app:**
- Không còn "Network error"
- Tất cả features hoạt động
- Template gallery hiển thị hình
- AI processing thành công

---

## 🆘 NẾU VẪN KHÔNG ĐƯỢC

1. **Check Replit Deployment Status:**
   - Deployment có đang running không?
   - URL có đúng không?

2. **Try Alternative Deployment:**
   - Create new deployment
   - Try "Static" deployment type (if available)
   - Try "Autoscale" with different settings

3. **Check Flutter App:**
   - Có update API URL đúng chưa?
   - Dio client có config đúng không?
   - Internet connection từ mobile OK không?

4. **Check Backend Logs:**
   - Requests có đến backend không?
   - Backend có lỗi gì không?

---

## 📞 CONTACT SUPPORT

Nếu không thể disable Shield:
- Email: support@replit.com
- Hoặc contact qua Replit Discord/Forum
- Explain: "Need to disable Replit Shield for mobile app API access"

---

**TÓM LẠI:** Vào Replit Deployments → Disable Shield → Test → Rebuild APK → Success! 🚀
