# 🚀 HƯỚNG DẪN SETUP NHANH - TIẾNG VIỆT

## 📌 CHỐT LẠI: MODEL NÀO ĐANG WORK?

### ✅ **CHỈ DÙNG REPLICATE!**

```
Model: arabyai-replicate/roop_face_swap
Version: 11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84

✅ Hoạt động: 100% 
⏱️ Tốc độ: ~77 giây/video
💰 Giá: ~$0.11-0.14/video
📸 Input: JPG/PNG/WEBP (tự động convert)
🎥 Output: MP4 video
```

### ❌ **HuggingFace - KHÔNG DÙNG!**
Tất cả models HuggingFace đều LỖI → Đã disable!

---

## 🔧 CÁCH CÀI ĐẶT CHO TÀI KHOẢN REPLIT MỚI

### **BƯỚC 1: TẠO PROJECT**
```
1. Vào Replit.com
2. Create Repl → Python
3. Upload code hoặc import từ GitHub
```

### **BƯỚC 2: CÀI PACKAGES**
Tạo file `requirements.txt`:
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

Replit sẽ tự động cài!

### **BƯỚC 3: THÊM API KEY**
```
1. Vào Tools → Secrets (🔒)
2. Thêm:
   Key:   REPLICATE_PRO_TOKEN
   Value: r8_xxxxxxxxxxxxxxxxxx
```

**Lấy token ở đâu?**
```
1. Vào https://replicate.com
2. Sign up/Login
3. Settings → API Tokens
4. Copy token (bắt đầu r8_)
```

### **BƯỚC 4: SETUP WORKFLOW**
```
1. Tools → Workflows
2. Add Workflow:
   Name: Server
   Command: gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
   Port: 5000
3. Save
```

### **BƯỚC 5: CHẠY & TEST**
```
1. Click Run
2. Mở: https://YOUR_URL/video-swap
3. Upload ảnh + video
4. Đợi 1-2 phút
5. Download kết quả
```

---

## ⚡ QUICK START (5 PHÚT)

### **1. Clone Project:**
```bash
# Import vào Replit:
https://github.com/YOUR_REPO/imageforge-api
```

### **2. Thêm API Key:**
```
Secrets → REPLICATE_PRO_TOKEN → r8_xxxxx
```

### **3. Run:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

### **4. Test:**
```
https://YOUR_DEV_URL/video-swap
```

---

## 📋 FILES CẦN CÓ

```
your-project/
├── app.py                    # Main Flask app
├── requirements.txt          # Python packages
├── .env                      # Local env (optional)
│
├── routes/
│   ├── video_routes.py      # Video face swap routes
│   ├── advanced_features.py # Other AI features
│   └── ...
│
├── utils/
│   ├── video_processor.py   # Video processing logic
│   ├── replicate_processor.py
│   └── ...
│
├── static/
│   ├── video_swap.html      # Test UI
│   └── ...
│
└── templates/
    └── ...
```

---

## 🔐 SECRETS CẦN THIẾT

| Secret | Bắt Buộc? | Lấy Ở Đâu |
|--------|-----------|-----------|
| `REPLICATE_PRO_TOKEN` | ✅ BẮT BUỘC | replicate.com → Settings |
| `SUPABASE_URL` | ⚠️ Optional | supabase.com (nếu dùng storage) |
| `SUPABASE_KEY` | ⚠️ Optional | supabase.com (nếu dùng storage) |

> Video face swap CHỈ CẦN `REPLICATE_PRO_TOKEN`!

---

## 🧪 TEST API

### **Qua Web UI:**
```
URL: https://YOUR_DEV_URL/video-swap

1. Upload ảnh (JPG/PNG)
2. Upload video (MP4)
3. Provider: auto
4. Click "Swap Face"
5. Đợi ~1-2 phút
6. Download video
```

### **Qua API (cURL):**
```bash
curl -X POST https://YOUR_DEV_URL/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=auto"

# Response sau ~77s:
{
  "success": true,
  "video_url": "https://replicate.delivery/...",
  "provider": "replicate",
  "model": "arabyai-replicate/roop_face_swap"
}
```

---

## ❓ TROUBLESHOOTING

### **❌ Lỗi: "REPLICATE_PRO_TOKEN required"**
→ Thêm token vào Secrets panel

### **❌ Lỗi: "cannot identify image file"**
→ Dùng JPG/PNG (không phải HEIC/TIFF)

### **❌ Video không ra kết quả**
→ Đợi đủ 1-2 phút, check logs

### **❌ 503 Service Unavailable**
→ Restart workflow

---

## 💰 CHI PHÍ

```
Replicate: ~$0.11-0.14 mỗi video
Processing: ~77 giây

Ví dụ:
- 10 videos/ngày = ~$1.2/ngày = ~$36/tháng
- 100 videos/ngày = ~$12/ngày = ~$360/tháng
```

---

## 📱 TÍCH HỢP FLUTTER

### **Update API URL:**
```dart
// lib/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'https://YOUR_REPLIT_URL';
  static const String videoFaceSwap = '/api/video/face-swap';
}
```

### **Call API:**
```dart
final response = await http.post(
  Uri.parse('${ApiConfig.baseUrl}${ApiConfig.videoFaceSwap}'),
  body: {'provider': 'auto'},
  files: {
    'face_image': faceFile,
    'video': videoFile,
  },
);
```

---

## ✅ CHECKLIST

```
☐ Tạo Replit project
☐ Upload code
☐ Cài packages (requirements.txt)
☐ Thêm REPLICATE_PRO_TOKEN vào Secrets
☐ Setup workflow (gunicorn)
☐ Run server
☐ Test /video-swap
☐ Update Flutter app URL
```

---

## 🎯 KẾT QUẢ MONG ĐỢI

Sau khi setup:
- ✅ API chạy tại: `https://YOUR_URL`
- ✅ Test UI: `https://YOUR_URL/video-swap`
- ✅ Processing time: 1-2 phút/video
- ✅ Output: MP4 video với face đã swap

---

## 📞 HỖ TRỢ

- **Replicate Docs:** https://replicate.com/docs
- **Replit Help:** https://replit.com/support
- **Chi tiết đầy đủ:** Xem file `SETUP_GUIDE.md`

---

**DONE! Chúc thành công! 🚀**
