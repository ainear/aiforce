# 🚀 HƯỚNG DẪN SETUP AI PHOTO EDITOR API - REPLIT

## 📋 MỤC LỤC
1. [API Models Đang Hoạt Động](#api-models)
2. [Yêu Cầu Hệ Thống](#requirements)
3. [Bước 1: Tạo Replit Project](#step1)
4. [Bước 2: Cài Đặt Dependencies](#step2)
5. [Bước 3: Cấu Hình Secrets](#step3)
6. [Bước 4: Setup Workflow](#step4)
7. [Bước 5: Test API](#step5)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 API MODELS ĐANG HOẠT ĐỘNG <a name="api-models"></a>

### ✅ **VIDEO FACE SWAP - REPLICATE (WORKING 2025)**
```
Model: arabyai-replicate/roop_face_swap
Version: 11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84

✅ Status: WORKING
⏱️ Speed: ~77 seconds trung bình
💰 Cost: ~$0.11-0.14 per video
📸 Input: JPG/PNG/WEBP (auto-convert to JPEG)
🎥 Output: MP4 video
```

### ❌ **HuggingFace Models - DISABLED**
```
Tất cả HuggingFace models đã bị disable do compatibility issues:
❌ ALSv/video-face-swap → 404 Not Found
❌ MarkoVidrih/video-face-swap → Internal API error
❌ tonyassi/vfs2-cpu → 404 Not Found

→ CHỈ DÙNG REPLICATE!
```

---

## 📦 YÊU CẦU HỆ THỐNG <a name="requirements"></a>

### **1. Python Packages (requirements.txt)**
```txt
flask>=3.1.2
flask-cors>=6.0.1
gunicorn>=23.0.0
pillow>=11.3.0
python-dotenv>=1.1.1
replicate>=1.0.7
requests>=2.32.5
supabase>=2.22.0
gradio-client
```

### **2. API Keys Cần Thiết**
| Secret Key | Bắt Buộc | Mục Đích | Lấy Ở Đâu |
|------------|----------|----------|-----------|
| `REPLICATE_PRO_TOKEN` | ✅ BẮT BUỘC | Video face swap | [replicate.com](https://replicate.com) → Settings → API Tokens |
| `SUPABASE_URL` | ⚠️ Tùy chọn | Lưu ảnh vào cloud | [supabase.com](https://supabase.com) → Project Settings → API |
| `SUPABASE_KEY` | ⚠️ Tùy chọn | Auth key cho Supabase | [supabase.com](https://supabase.com) → Project Settings → API |

> **LƯU Ý:** Video face swap CHỈ CẦN `REPLICATE_PRO_TOKEN`!

---

## 🔧 BƯỚC 1: TẠO REPLIT PROJECT <a name="step1"></a>

### **Option A: Import từ GitHub**
```bash
1. Vào Replit.com → Create Repl
2. Chọn "Import from GitHub"
3. Paste URL: https://github.com/YOUR_USERNAME/imageforge-api
4. Click "Import from GitHub"
```

### **Option B: Tạo Mới & Upload Code**
```bash
1. Create Repl → Python
2. Upload các files:
   - app.py
   - requirements.txt
   - routes/ (folder)
   - utils/ (folder)
   - static/ (folder)
   - templates/ (folder)
```

---

## 📥 BƯỚC 2: CÀI ĐẶT DEPENDENCIES <a name="step2"></a>

### **Tự Động (Replit)**
Replit sẽ tự động cài khi detect `requirements.txt`

### **Thủ Công (nếu cần)**
```bash
# Trong Replit Shell:
pip install -r requirements.txt
```

### **Verify Packages**
```bash
pip list | grep -E "(flask|replicate|supabase|pillow)"
```

Kết quả mong đợi:
```
flask                3.1.2
replicate            1.0.7
supabase             2.22.0
Pillow              11.3.0
```

---

## 🔐 BƯỚC 3: CÁU HÌNH SECRETS <a name="step3"></a>

### **1. Mở Secrets Panel**
```
Replit → Tools → Secrets (hoặc lock icon 🔒)
```

### **2. Thêm REPLICATE_PRO_TOKEN**
```bash
Key:   REPLICATE_PRO_TOKEN
Value: r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Lấy token:
1. Vào https://replicate.com
2. Sign up / Login
3. Settings → API Tokens
4. Copy token (bắt đầu với r8_)
```

### **3. (Optional) Thêm Supabase**
Chỉ cần nếu muốn lưu ảnh vào cloud storage:

```bash
Key:   SUPABASE_URL
Value: https://xxxxxxxxxxxxx.supabase.co

Key:   SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Lấy credentials:
1. Vào https://supabase.com
2. Create Project
3. Project Settings → API
4. Copy URL và anon/public key
```

---

## ⚙️ BƯỚC 4: SETUP WORKFLOW <a name="step4"></a>

### **Cách 1: Tự Động (Có Sẵn .replit File)**
```toml
# File .replit sẽ tự động chạy:
run = "gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app"
```

### **Cách 2: Thủ Công**
```bash
1. Vào Replit → Tools → Workflows
2. Click "Add Workflow"
3. Điền:
   Name: Server
   Command: gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 --access-logfile - --error-logfile - app:app
   Port: 5000
4. Click "Save"
```

### **Start Server**
```bash
# Click Run button HOẶC trong Shell:
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

---

## 🧪 BƯỚC 5: TEST API <a name="step5"></a>

### **1. Get Dev URL**
```bash
# In Replit Shell để lấy URL:
env | grep REPLIT_DEV_DOMAIN

# Hoặc lấy từ Webview panel
```

Dev URL format:
```
https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-00-xxxxxxxxxx.pike.replit.dev
```

### **2. Test Video Face Swap**

#### **Via Web UI:**
```
1. Mở: https://YOUR_DEV_URL/video-swap
2. Upload:
   - Face Image: bất kỳ ảnh (JPG/PNG/WEBP)
   - Video File: MP4 file
3. Provider: chọn "auto" (sẽ dùng Replicate)
4. Click "Swap Face in Video"
5. ĐỢI 1-2 PHÚT
6. Result: Download MP4 với face đã swap
```

#### **Via API (cURL):**
```bash
curl -X POST https://YOUR_DEV_URL/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=auto"

# Expected Response (after ~77s):
{
  "success": true,
  "video_url": "https://replicate.delivery/...",
  "provider": "replicate",
  "model": "arabyai-replicate/roop_face_swap",
  "processing_time": 77.3
}
```

### **3. Test Other Features**

```bash
# Test UI chính:
https://YOUR_DEV_URL/

# Có các features:
- HD Upscale
- Fix Old Photo
- Cartoonify
- Face Swap (ảnh)
- Style Transfer
- Background Removal
- Depth Map
- Colorize
```

---

## 🔍 TROUBLESHOOTING <a name="troubleshooting"></a>

### **❌ Lỗi: "REPLICATE_PRO_TOKEN required"**
```bash
✅ Fix:
1. Check Secrets panel có REPLICATE_PRO_TOKEN chưa
2. Restart workflow (Stop → Run)
3. Verify token hợp lệ tại replicate.com
```

### **❌ Lỗi: "cannot identify image file"**
```bash
✅ Fix:
1. Đảm bảo ảnh là JPG/PNG/WEBP (không phải HEIC/TIFF)
2. File size < 10MB
3. Image không corrupted (mở được bằng photo viewer)
```

### **❌ Lỗi: "Timeout after 300s"**
```bash
✅ Fix:
1. Video quá dài (max ~30s recommended)
2. Internet connection bị chậm
3. Replicate API đang quá tải → retry sau 5 phút
```

### **❌ Lỗi: "503 Service Unavailable"**
```bash
✅ Fix:
1. Workflow chưa chạy → Click Run
2. Check logs: Shell → cat /tmp/logs/Server_*.log
3. Restart workflow
```

### **❌ Video processing mãi không xong**
```bash
✅ Expected:
- Processing time: 1-2 phút (60-120s)
- Countdown timer sẽ hiển thị thời gian còn lại
- Nếu > 5 phút → có vấn đề

✅ Fix:
1. Check browser console (F12) xem có lỗi
2. Check server logs
3. Verify REPLICATE_PRO_TOKEN còn credits
```

---

## 📊 PRODUCTION DEPLOYMENT

### **Publish lên Replit (để dùng lâu dài):**
```bash
1. Click "Deploy" button trên Replit
2. Chọn deployment type:
   - Static: Cho website đơn giản
   - Autoscale: Cho API (RECOMMENDED)
   - VM: Cho app cần chạy 24/7

3. Configure:
   - Run command: gunicorn --bind 0.0.0.0:5000 app:app
   - Port: 5000

4. Deploy!
```

### **Custom Domain (Optional):**
```bash
1. Deploy xong → Settings
2. Add custom domain: api.yourdomain.com
3. Update DNS theo hướng dẫn
```

---

## 📱 FLUTTER APP INTEGRATION

### **Update API URL trong Flutter:**

```dart
// lib/config/api_config.dart
class ApiConfig {
  // PRODUCTION URL (sau khi deploy)
  static const String baseUrl = 'https://YOUR_DEPLOYED_URL';
  
  // HOẶC DEV URL (khi đang test)
  static const String baseUrl = 'https://xxxxxxxx.pike.replit.dev';
  
  // Video Face Swap endpoint
  static const String videoFaceSwap = '/api/video/face-swap';
}
```

### **Test từ Flutter:**
```dart
final response = await http.post(
  Uri.parse('${ApiConfig.baseUrl}${ApiConfig.videoFaceSwap}'),
  body: {
    'provider': 'auto',  // sẽ dùng Replicate
  },
  files: {
    'face_image': faceImageFile,
    'video': videoFile,
  },
);

// Expected: 1-2 phút processing
// Result: video URL để download
```

---

## 💰 COST ESTIMATION

### **Replicate Pricing:**
```
Video Face Swap: ~$0.11-0.14 per video
Processing Time: ~77 seconds average

Examples:
- 10 videos/day = $1.10-1.40/day = ~$33-42/month
- 100 videos/day = $11-14/day = ~$330-420/month

💡 Mẹo tiết kiệm:
- Cache kết quả đã xử lý
- Giới hạn video length < 30s
- Implement rate limiting
```

---

## 📞 HỖ TRỢ

### **API Documentation:**
```
GET  /api/video/providers  → List available models
POST /api/video/face-swap  → Swap face in video
GET  /healthz             → Health check
```

### **Liên Hệ:**
- **Replicate Issues:** https://replicate.com/docs
- **Replit Support:** https://replit.com/support
- **Project Issues:** GitHub Issues

---

## ✅ CHECKLIST SETUP

```
☐ 1. Tạo Replit project
☐ 2. Upload/import code
☐ 3. Verify requirements.txt
☐ 4. Thêm REPLICATE_PRO_TOKEN vào Secrets
☐ 5. Setup workflow (gunicorn command)
☐ 6. Run server
☐ 7. Test /video-swap UI
☐ 8. Verify video processing works
☐ 9. Update Flutter app URL
☐ 10. Deploy to production (optional)
```

---

## 🎉 DONE!

Sau khi setup xong, bạn có thể:
- ✅ Sử dụng video face swap API
- ✅ Tích hợp vào Flutter app
- ✅ Deploy lên production
- ✅ Scale với Replicate credits

**Test URL Mẫu:**
```
https://YOUR_DEV_URL/video-swap
```

**Happy Coding! 🚀**
