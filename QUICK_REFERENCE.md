# 🚀 Video Face Swap - Quick Reference

## ✅ TỔNG KẾT API & MODELS (CẢ 2 ĐỀU HOẠT ĐỘNG!)

### 📊 So Sánh Nhanh

| Feature | Replicate | VModel |
|---------|-----------|--------|
| **Model** | arabyai-replicate/roop_face_swap | vmodel/video-face-swap-pro |
| **Version** | 11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84 | 537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224 |
| **API** | replicate.run() | POST /api/tasks/v1/create |
| **Status Check** | N/A (sync) | GET /api/tasks/v1/get/{task_id} |
| **Giá** | $0.14/video | $0.03/giây (~$0.10) |
| **Tốc độ** | ~77s | 15-51s |
| **Audio** | ✅ Preserved | ✅ Preserved |
| **Requirements** | REPLICATE_PRO_TOKEN | VMODEL_API_TOKEN + Supabase |
| **Status** | ✅ WORKING | ✅ WORKING |

---

## 🔧 REPLICATE API

### Setup
```bash
REPLICATE_PRO_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Code
```python
import replicate

model = "arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84"

with open('face.jpg', 'rb') as f1, open('video.mp4', 'rb') as f2:
    output = replicate.run(
        model,
        input={
            "swap_image": f1,
            "target_video": f2
        }
    )

video_url = output if isinstance(output, str) else output[0]
```

### ⚠️ Lưu Ý
- PHẢI dùng full version ID (64-char hash)
- Audio tự động preserve
- Synchronous API (không cần poll)

---

## 🔧 VMODEL API

### Setup
```bash
VMODEL_API_TOKEN=vmodel-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
```

### Step 1: Upload to Supabase
```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Upload face
supabase.storage.from_('ai-photos').upload(
    'temp/face.jpg',
    face_bytes,
    file_options={"content-type": "image/jpeg"}
)
face_url = supabase.storage.from_('ai-photos').get_public_url('temp/face.jpg')

# Upload video
supabase.storage.from_('ai-photos').upload(
    'temp/video.mp4',
    video_bytes,
    file_options={"content-type": "video/mp4"}
)
video_url = supabase.storage.from_('ai-photos').get_public_url('temp/video.mp4')
```

### Step 2: Create Task
```python
import requests

response = requests.post(
    "https://api.vmodel.ai/api/tasks/v1/create",
    headers={
        "Authorization": f"Bearer {VMODEL_API_TOKEN}",
        "Content-Type": "application/json"
    },
    json={
        "version": "537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224",
        "input": {
            "target": face_url,
            "source": video_url,
            "disable_safety_checker": True
        }
    }
)

result = response.json()
task_id = result['result']['task_id'] if result.get('code') == 200 else result.get('task_id')
```

### Step 3: Poll Status
```python
import time

time.sleep(2)  # Initial delay

for i in range(60):
    status = requests.get(
        f"https://api.vmodel.ai/api/tasks/v1/get/{task_id}",
        headers={"Authorization": f"Bearer {VMODEL_API_TOKEN}"}
    ).json()
    
    task_status = status['result'] if 'result' in status else status
    
    if task_status['status'] == 'succeeded':
        video_url = task_status['output'][0]
        break
    
    time.sleep(3)
```

### ⚠️ Lưu Ý
- Endpoint phải là `/get/{task_id}` (có `/get/`)
- Cần URLs (upload Supabase trước)
- Response có thể nested `{'code': 200, 'result': {...}}`
- Audio tự động preserve

---

## 🎯 AUTO MODE (RECOMMENDED)

### Logic
```python
try:
    # Try Replicate first
    video_url = swap_with_replicate(face, video)
    return video_url, "replicate"
except:
    # Fallback to VModel
    video_url = swap_with_vmodel(face, video)
    return video_url, "vmodel"
```

### Khi Nào Dùng Gì?
- **Auto**: Production (best reliability)
- **Replicate**: Cần stability, không cần speed
- **VModel**: Cần speed, có Supabase

---

## 📝 API ENDPOINTS

### Replicate
```
POST https://api.replicate.com/v1/predictions
Authorization: Token {REPLICATE_PRO_TOKEN}
```

### VModel
```
POST https://api.vmodel.ai/api/tasks/v1/create
GET  https://api.vmodel.ai/api/tasks/v1/get/{task_id}
Authorization: Bearer {VMODEL_API_TOKEN}
```

---

## ✅ CHECKLIST

### Replicate
- [ ] API token: https://replicate.com/account/api-tokens
- [ ] Add to secrets: `REPLICATE_PRO_TOKEN`
- [ ] Dùng full version ID (64-char)
- [ ] Test với face.jpg + video.mp4

### VModel
- [ ] API token: https://vmodel.ai/account/api-tokens
- [ ] Supabase project: https://supabase.com/dashboard
- [ ] Create bucket: `ai-photos` (public)
- [ ] Add secrets: `VMODEL_API_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`
- [ ] Test endpoint `/get/{task_id}`

---

## 🧪 TEST COMMANDS

### cURL Replicate
```bash
curl -X POST https://YOUR_API/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=replicate"
```

### cURL VModel
```bash
curl -X POST https://YOUR_API/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=vmodel"
```

### cURL Auto
```bash
curl -X POST https://YOUR_API/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=auto"
```

---

## 🚨 COMMON ERRORS

### Replicate 404
```
❌ arabyai-replicate/roop_face_swap
✅ arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84
```

### VModel 404
```
❌ GET /api/tasks/v1/{task_id}
✅ GET /api/tasks/v1/get/{task_id}
```

### VModel "Need URLs"
```
❌ Direct file upload
✅ Upload to Supabase → Get URL → Pass to VModel
```

---

## 📚 FULL DOCS

- English: `VIDEO_FACE_SWAP_API_GUIDE.md`
- Tiếng Việt: `VIDEO_FACE_SWAP_VIETNAMESE.md`

**Last Updated: October 2025 ✅**
