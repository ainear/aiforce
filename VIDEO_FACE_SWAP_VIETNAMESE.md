# 📹 Hướng Dẫn API Video Face Swap Tiếng Việt

> **Document hướng dẫn triển khai Video Face Swap có giữ nguyên Audio bằng Replicate & VModel.AI trên Replit**

---

## 📋 MỤC LỤC

1. [Tổng Quan](#tổng-quan)
2. [Thông Tin API](#thông-tin-api)
3. [Hướng Dẫn Setup](#hướng-dẫn-setup)
4. [Code Mẫu](#code-mẫu)
5. [Test & Debug](#test--debug)

---

## 🎯 TỔNG QUAN

### Hệ Thống 3 Provider
| Provider | Giá | Tốc độ | Audio | Chất lượng | Trạng thái |
|----------|-----|--------|-------|------------|------------|
| **Auto** | $0.10-0.14 | 15-77s | ✅ | Cao | ⭐ Đề xuất |
| **Replicate** | $0.14 | ~77s | ✅ | Tốt, Ổn định | ✅ Hoạt động |
| **VModel** | ~$0.10 | 15-51s | ✅ | Cao cấp | ✅ Hoạt động |

### Cách Hoạt động Auto Mode
```
1. User upload ảnh khuôn mặt + video
2. Thử Replicate trước (ổn định, $0.14)
   ✅ Thành công → Trả về video có audio
   ❌ Thất bại → Chuyển bước 3
3. Dự phòng VModel ($0.10, nhanh hơn)
   ✅ Thành công → Trả về video cao cấp có audio
   ❌ Thất bại → Báo lỗi
```

---

## 🔧 THÔNG TIN API

### 1. REPLICATE API (CHÍNH)

#### ✅ Thông Tin Model
```
Model: arabyai-replicate/roop_face_swap
Version: 11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84
Giá: $0.14 mỗi video
Tốc độ: ~77 giây
Audio: ✅ Giữ nguyên
Chất lượng: Tốt, ổn định
Trạng thái: ✅ HOẠT ĐỘNG 2025
```

#### 📝 Cách Dùng
```python
import replicate

# PHẢI dùng FULL version ID (64 ký tự hash)
model_name = "arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84"

with open(face_path, 'rb') as f1, open(video_path, 'rb') as f2:
    output = replicate.run(
        model_name,
        input={
            "swap_image": f1,      # Ảnh khuôn mặt để swap
            "target_video": f2     # Video đích
        }
    )

# Output là URL video
video_url = output if isinstance(output, str) else output[0]
```

#### ⚠️ Lưu Ý Quan Trọng
- **PHẢI dùng full version ID** (hash 64 ký tự) để tránh lỗi 404
- Model này dùng cho VIDEO (không phải ảnh)
- Audio tự động giữ nguyên
- Response có thể là string URL hoặc list[URL]

---

### 2. VMODEL.AI API (DỰ PHÒNG)

#### ✅ Thông Tin Model
```
Model: vmodel/video-face-swap-pro
Version: 537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224
Giá: $0.03/giây (~$0.10 cho video ngắn)
Tốc độ: 15-51 giây (nhanh hơn!)
Audio: ✅ Giữ nguyên
Chất lượng: Cao cấp, license thương mại
Trạng thái: ✅ HOẠT ĐỘNG 2025
```

#### 📡 API Endpoints
```python
# Tạo Task
POST https://api.vmodel.ai/api/tasks/v1/create

# Check Trạng thái (⚠️ CHÚ Ý: phải có /get/!)
GET https://api.vmodel.ai/api/tasks/v1/get/{task_id}
```

#### 📝 Bước 1: Upload Files lên Supabase
```python
# VModel cần URLs, không nhận files trực tiếp!
# Upload lên Supabase Storage trước

from supabase import create_client
import uuid

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
task_id = str(uuid.uuid4())[:8]

# Upload ảnh khuôn mặt
face_path = f"vmodel-temp/face_{task_id}.jpg"
supabase.storage.from_('ai-photos').upload(
    face_path,
    face_image_bytes,
    file_options={"content-type": "image/jpeg"}
)
face_url = supabase.storage.from_('ai-photos').get_public_url(face_path)

# Upload video
video_path = f"vmodel-temp/video_{task_id}.mp4"
supabase.storage.from_('ai-photos').upload(
    video_path,
    video_bytes,
    file_options={"content-type": "video/mp4"}
)
video_url = supabase.storage.from_('ai-photos').get_public_url(video_path)
```

#### 📝 Bước 2: Tạo Task
```python
create_response = requests.post(
    "https://api.vmodel.ai/api/tasks/v1/create",
    headers={
        "Authorization": f"Bearer {VMODEL_API_TOKEN}",
        "Content-Type": "application/json"
    },
    json={
        "version": "537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224",
        "input": {
            "target": face_url,    # URL ảnh khuôn mặt
            "source": video_url,   # URL video
            "disable_safety_checker": True
        }
    }
)

result = create_response.json()

# Parse response lồng nhau: {'code': 200, 'result': {'task_id': '...', 'task_cost': ...}}
if result.get('code') == 200 and 'result' in result:
    task_id = result['result']['task_id']
else:
    task_id = result.get('task_id')  # Dự phòng
```

#### 📝 Bước 3: Kiểm Tra Trạng Thái
```python
import time

# Delay nhỏ trước khi check lần đầu
time.sleep(2)

max_retries = 60  # Tối đa 3 phút
for i in range(max_retries):
    try:
        # ⚠️ QUAN TRỌNG: Phải dùng endpoint /get/{task_id}!
        status_response = requests.get(
            f"https://api.vmodel.ai/api/tasks/v1/get/{task_id}",
            headers={"Authorization": f"Bearer {VMODEL_API_TOKEN}"}
        )
        
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # VModel có thể trả response lồng nhau
        if 'result' in status_data and isinstance(status_data['result'], dict):
            task_status = status_data['result']
        else:
            task_status = status_data
        
        if task_status.get('status') == 'succeeded':
            output_url = task_status.get('output', [None])[0]
            return output_url
        
        elif task_status.get('status') in ['failed', 'canceled']:
            raise Exception(f"VModel task failed: {task_status.get('error')}")
        
        time.sleep(3)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Task chưa tìm thấy (404), thử lại... ({i+1}/{max_retries})")
            time.sleep(5)  # Delay lâu hơn khi 404
            continue
        raise
```

#### ⚠️ Lưu Ý Quan Trọng
- **VModel cần URLs**, không nhận file uploads trực tiếp
- **Phải dùng endpoint `/get/{task_id}`** (không phải `/{task_id}`)
- Response format có thể lồng nhau `{'code': 200, 'result': {...}}`
- Cần Supabase Storage để upload files trước
- Audio tự động giữ nguyên

---

## 🚀 HƯỚNG DẪN SETUP

### Bước 1: Tạo Project Replit
```bash
1. Vào Replit → Chọn "Python"
2. Tên project: imageforge-api (hoặc tên khác)
```

### Bước 2: Cài Dependencies
```bash
# Tạo file requirements.txt
flask
flask-cors
gunicorn
pillow
python-dotenv
replicate
requests
supabase
```

### Bước 3: Setup Secrets
Vào Replit Secrets (icon 🔒) và thêm:

```bash
# REPLICATE API (Provider chính)
REPLICATE_PRO_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Lấy từ: https://replicate.com/account/api-tokens

# VMODEL API (Provider dự phòng)
VMODEL_API_TOKEN=vmodel-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Lấy từ: https://vmodel.ai/account/api-tokens

# SUPABASE (Cần cho VModel)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
# Lấy từ: https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
```

### Bước 4: Tạo Supabase Storage Bucket
```sql
-- Vào Supabase Dashboard → Storage → Create bucket
Tên bucket: ai-photos
Public: ✅ BẬT (để lấy public URLs)
Allowed MIME types: image/*, video/*
```

### Bước 5: Copy Code
```bash
# Copy các files sau từ project mẫu:
utils/video_processor.py     # Logic xử lý video
routes/video_routes.py        # API endpoints
static/video_swap.html        # Web UI test
app.py                        # Flask app chính
```

### Bước 6: Setup Workflow
```bash
# Vào Replit → Configure Run Button
Command: gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

### Bước 7: Test API
```bash
# API sẽ chạy tại:
https://TÊN_REPLIT_CỦA_BẠN.replit.dev

# Test endpoints:
GET  /api/video/providers          # Liệt kê providers
POST /api/video/face-swap          # Swap face trong video
```

---

## 💻 CODE MẪU

### Class Xử Lý Video Đầy Đủ
(Xem file `VIDEO_FACE_SWAP_API_GUIDE.md` cho code đầy đủ)

### Flask API Routes
```python
# routes/video_routes.py

from flask import Blueprint, request, jsonify
from utils.video_processor import VideoFaceSwapProcessor

video_bp = Blueprint('video', __name__)
video_processor = VideoFaceSwapProcessor()

@video_bp.route('/face-swap', methods=['POST'])
def video_face_swap():
    """Endpoint swap face trong video"""
    try:
        if 'face_image' not in request.files or 'video' not in request.files:
            return jsonify({'error': 'Thiếu face_image hoặc video'}), 400
        
        face_image = request.files['face_image']
        video_file = request.files['video']
        provider = request.form.get('provider', 'auto')
        
        # Xử lý video
        result, provider_used, model_used = video_processor.swap_face_video(
            face_image, video_file, provider
        )
        
        return jsonify({
            'success': True,
            'video_url': result,
            'provider': provider_used,
            'model': model_used,
            'audio_preserved': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🧪 TEST & DEBUG

### Test Bằng cURL

#### Test Replicate
```bash
curl -X POST https://YOUR_REPLIT_URL/api/video/face-swap \
  -F "face_image=@khuon_mat.jpg" \
  -F "video=@video.mp4" \
  -F "provider=replicate"
```

#### Test VModel
```bash
curl -X POST https://YOUR_REPLIT_URL/api/video/face-swap \
  -F "face_image=@khuon_mat.jpg" \
  -F "video=@video.mp4" \
  -F "provider=vmodel"
```

#### Test Auto (Đề xuất)
```bash
curl -X POST https://YOUR_REPLIT_URL/api/video/face-swap \
  -F "face_image=@khuon_mat.jpg" \
  -F "video=@video.mp4" \
  -F "provider=auto"
```

### Các Lỗi Thường Gặp

#### ❌ Lỗi: Replicate 404
```
Giải pháp: Dùng FULL version ID (hash 64 ký tự)
✅ arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84
❌ arabyai-replicate/roop_face_swap
```

#### ❌ Lỗi: VModel 404 khi check status
```
Giải pháp: Phải dùng endpoint /get/{task_id}
✅ GET /api/tasks/v1/get/{task_id}
❌ GET /api/tasks/v1/{task_id}
```

#### ❌ Lỗi: VModel "Cần URLs"
```
Giải pháp: Upload files lên Supabase trước, rồi gửi public URLs
VModel không nhận file uploads trực tiếp!
```

---

## 📊 SO SÁNH HIỆU NĂNG

### Replicate
- Trung bình: ~77 giây
- Giá: $0.14 mỗi video
- Audio: ✅ Luôn giữ nguyên
- Độ tin cậy: Cao (ổn định)

### VModel
- Trung bình: 15-51 giây (nhanh hơn!)
- Giá: $0.03/giây (~$0.10 cho video ngắn)
- Audio: ✅ Luôn giữ nguyên
- Độ tin cậy: Cao (với endpoint đúng)

### So Sánh Chi Phí (video 30s)
| Provider | Thời gian xử lý | Chi phí | Audio | Chất lượng |
|----------|----------------|---------|-------|------------|
| Replicate | ~77s | $0.14 | ✅ | Tốt |
| VModel | ~30s | ~$0.10 | ✅ | Cao cấp |

### Khuyến Nghị
- **Auto mode**: Tốt nhất cho production (có cơ chế dự phòng)
- **Replicate**: Tốt nhất về độ ổn định
- **VModel**: Tốt nhất về tốc độ & giá (nếu có Supabase)

---

## ✅ CHECKLIST TRIỂN KHAI

### Chuẩn bị
- [ ] Tạo tài khoản Replicate & lấy API token
- [ ] Tạo tài khoản VModel & lấy API token
- [ ] Tạo project Supabase & setup bucket `ai-photos`
- [ ] Thêm secrets vào Replit
- [ ] Test cả 3 providers (auto, replicate, vmodel)

### Testing
- [ ] Upload video + ảnh khuôn mặt thử
- [ ] Kiểm tra audio có giữ nguyên không
- [ ] Kiểm tra thời gian xử lý
- [ ] Kiểm tra cơ chế dự phòng (auto mode)
- [ ] Test xử lý lỗi

### Production
- [ ] Bật Gunicorn workers (2-4)
- [ ] Setup timeout (300s cho xử lý video)
- [ ] Theo dõi chi phí (Replicate + VModel)
- [ ] Setup error logging
- [ ] Implement rate limiting (tùy chọn)

---

## 📚 TÀI LIỆU THAM KHẢO

### Docs API
- Replicate: https://replicate.com/docs
- VModel: https://vmodel.ai/docs/api/
- Supabase: https://supabase.com/docs

### Lấy API Keys
- Replicate: https://replicate.com/account/api-tokens
- VModel: https://vmodel.ai/account/api-tokens
- Supabase: https://supabase.com/dashboard

---

## 📝 GHI CHÚ QUAN TRỌNG

### Về Audio
- ✅ Replicate: Audio tự động giữ nguyên
- ✅ VModel: Audio tự động giữ nguyên
- Không cần cấu hình thêm!

### Giới Hạn File
- Replicate: Tối đa ~100MB video
- VModel: Tính phí theo thời lượng (không phải size)
- Supabase: 50MB free tier

---

**🎉 Chúc bạn triển khai thành công Video Face Swap API!**

*Cập nhật lần cuối: Tháng 10 năm 2025*
