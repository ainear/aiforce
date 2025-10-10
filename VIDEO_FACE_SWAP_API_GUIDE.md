# 📹 Video Face Swap API - Hướng Dẫn Chi Tiết

> **Document này hướng dẫn triển khai Video Face Swap với Audio Preserved sử dụng Replicate & VModel.AI trên Replit**

---

## 📋 MỤC LỤC

1. [Tổng Quan](#tổng-quan)
2. [API Providers](#api-providers)
3. [Setup Trên Replit Mới](#setup-trên-replit-mới)
4. [Code Implementation](#code-implementation)
5. [Testing & Debugging](#testing--debugging)

---

## 🎯 TỔNG QUAN

### Hệ Thống 3-Provider
| Provider | Cost | Speed | Audio | Quality | Status |
|----------|------|-------|-------|---------|--------|
| **Auto** | $0.10-0.14 | 15-77s | ✅ | High | ⭐ Recommended |
| **Replicate** | $0.14 | ~77s | ✅ | Good, Stable | ✅ Working |
| **VModel** | ~$0.10 | 15-51s | ✅ | Premium | ✅ Working |

### Auto Mode Flow
```
1. User upload face + video
2. Try Replicate first (stable, $0.14)
   ✅ Success → Return video with audio
   ❌ Failed → Go to step 3
3. Fallback to VModel ($0.10, faster)
   ✅ Success → Return premium video with audio
   ❌ Failed → Return error
```

---

## 🔧 API PROVIDERS

### 1. REPLICATE API (PRIMARY)

#### ✅ Model Information
```
Model: arabyai-replicate/roop_face_swap
Version: 11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84
Cost: $0.14 per video
Speed: ~77 seconds
Audio: ✅ Preserved
Quality: Good, stable
Status: ✅ WORKING 2025
```

#### 📡 API Endpoint
```python
POST https://api.replicate.com/v1/predictions
```

#### 🔑 Authentication
```python
headers = {
    "Authorization": f"Token {REPLICATE_PRO_TOKEN}",
    "Content-Type": "application/json"
}
```

#### 📝 Request Format
```python
import replicate

# Must use FULL version ID (not short model name)
model_name = "arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84"

with open(face_path, 'rb') as f1, open(video_path, 'rb') as f2:
    output = replicate.run(
        model_name,
        input={
            "swap_image": f1,      # Face to swap (source face)
            "target_video": f2     # Video to swap into (target video)
        }
    )

# Output is video URL (string)
video_url = output if isinstance(output, str) else output[0]
```

#### ⚠️ Important Notes
- **MUST use full version ID** (64-char hash) để tránh 404 errors
- Model này là VIDEO face swap (không phải image swap)
- Audio được preserve tự động
- Response là string URL hoặc list[URL]

---

### 2. VMODEL.AI API (FALLBACK)

#### ✅ Model Information
```
Model: vmodel/video-face-swap-pro
Version: 537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224
Cost: $0.03/second (~$0.10 per short video)
Speed: 15-51 seconds (faster!)
Audio: ✅ Preserved
Quality: Premium, commercial license
Status: ✅ WORKING 2025
```

#### 📡 API Endpoints
```python
# Create Task
POST https://api.vmodel.ai/api/tasks/v1/create

# Check Status (⚠️ NOTE: /get/ is required!)
GET https://api.vmodel.ai/api/tasks/v1/get/{task_id}
```

#### 🔑 Authentication
```python
headers = {
    "Authorization": f"Bearer {VMODEL_API_TOKEN}",
    "Content-Type": "application/json"
}
```

#### 📝 Step 1: Upload Files to Supabase
```python
# VModel requires URLs, not files!
# Upload to Supabase Storage first

from supabase import create_client
import uuid

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
task_id = str(uuid.uuid4())[:8]

# Upload face image
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

#### 📝 Step 2: Create Task
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
            "target": face_url,    # URL to face image
            "source": video_url,   # URL to video
            "disable_safety_checker": True
        }
    }
)

result = create_response.json()

# Parse nested response: {'code': 200, 'result': {'task_id': '...', 'task_cost': ...}}
if result.get('code') == 200 and 'result' in result:
    task_id = result['result']['task_id']
else:
    task_id = result.get('task_id')  # Fallback
```

#### 📝 Step 3: Poll for Status
```python
import time

# Small delay before first check (let API index the task)
time.sleep(2)

max_retries = 60  # 3 minutes max
for i in range(max_retries):
    try:
        # ⚠️ IMPORTANT: Must use /get/{task_id} endpoint!
        status_response = requests.get(
            f"https://api.vmodel.ai/api/tasks/v1/get/{task_id}",
            headers={"Authorization": f"Bearer {VMODEL_API_TOKEN}"}
        )
        
        status_response.raise_for_status()
        status_data = status_response.json()
        
        # VModel may return nested response
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
            print(f"Task not found yet (404), retrying... ({i+1}/{max_retries})")
            time.sleep(5)  # Longer delay on 404
            continue
        raise

raise Exception("VModel processing timeout (3 minutes)")
```

#### 📋 Status Values
- `starting`: Task đang khởi động
- `processing`: Task đang xử lý
- `succeeded`: Thành công (check `output` array)
- `failed`: Thất bại (check `error` field)
- `canceled`: Bị cancel

#### ⚠️ Important Notes
- **VModel requires URLs**, không nhận file uploads trực tiếp
- **Must use `/get/{task_id}` endpoint** (không phải `/{task_id}`)
- Response format có thể là nested `{'code': 200, 'result': {...}}`
- Requires Supabase Storage để upload files trước
- Audio được preserve tự động

---

## 🚀 SETUP TRÊN REPLIT MỚI

### Bước 1: Tạo Replit Project
```bash
1. Tạo Replit → Chọn "Python"
2. Project name: imageforge-api (hoặc tên khác)
```

### Bước 2: Install Dependencies
```bash
# Add vào file requirements.txt hoặc dùng packager tool
flask
flask-cors
gunicorn
pillow
python-dotenv
replicate
requests
supabase
```

### Bước 3: Setup Environment Secrets
Vào Replit Secrets (🔒 icon) và thêm:

```bash
# REPLICATE API (Primary Provider)
REPLICATE_PRO_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Get from: https://replicate.com/account/api-tokens

# VMODEL API (Fallback Provider)
VMODEL_API_TOKEN=vmodel-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Get from: https://vmodel.ai/account/api-tokens

# SUPABASE (Required for VModel)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
# Get from: https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api

# Note: REPLICATE_API_TOKEN cũng hoạt động (alias)
```

### Bước 4: Tạo Supabase Storage Bucket
```sql
-- Vào Supabase Dashboard → Storage → Create bucket
Bucket name: ai-photos
Public: ✅ ON (để lấy public URLs)
Allowed MIME types: image/*, video/*
```

### Bước 5: Copy Source Code
```bash
# Copy các files này từ project hiện tại:
utils/video_processor.py     # Video processing logic
routes/video_routes.py        # API endpoints
static/video_swap.html        # Web UI test
app.py                        # Main Flask app
```

### Bước 6: Setup Workflow (Auto-run)
```bash
# Vào Replit → Configure Run Button
Command: gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

### Bước 7: Test API
```bash
# API sẽ chạy tại:
https://YOUR_REPLIT_NAME.replit.dev

# Test endpoints:
GET  /api/video/providers          # List providers
POST /api/video/face-swap          # Swap face in video
```

---

## 💻 CODE IMPLEMENTATION

### Full Video Processor Class

```python
# utils/video_processor.py

import os
import requests
import replicate
from supabase import create_client
import uuid
import time
from PIL import Image
import io

class VideoFaceSwapProcessor:
    def __init__(self):
        # Replicate Pro
        self.replicate_token = os.getenv('REPLICATE_PRO_TOKEN') or os.getenv('REPLICATE_API_TOKEN')
        self.replicate_models = [
            "arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84"
        ]
        
        # VModel.AI
        self.vmodel_token = os.getenv('VMODEL_API_TOKEN', '')
        
        # Supabase (for VModel file uploads)
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
    
    def swap_face_replicate(self, face_image, video_file):
        """
        Video face swap using Replicate
        Returns: (video_url, model_name)
        """
        import tempfile
        from PIL import Image
        
        # Save video to temp file
        video_path = tempfile.mktemp(suffix='.mp4')
        with open(video_path, 'wb') as f:
            f.write(video_file.read())
            video_file.seek(0)
        
        # Convert face image to JPEG
        face_img = Image.open(face_image)
        face_path = tempfile.mktemp(suffix='.jpg')
        face_img.convert('RGB').save(face_path, 'JPEG')
        face_image.seek(0)
        
        print(f"[Replicate] Image converted to JPEG: {face_path}")
        
        for model_name in self.replicate_models:
            try:
                print(f"[Replicate] Trying model: {model_name}")
                
                with open(face_path, 'rb') as f1, open(video_path, 'rb') as f2:
                    output = replicate.run(
                        model_name,
                        input={
                            "swap_image": f1,      # Face to swap
                            "target_video": f2     # Video to swap into
                        }
                    )
                
                # Handle different output formats
                if isinstance(output, str):
                    video_url = output
                elif isinstance(output, list) and len(output) > 0:
                    video_url = output[0]
                else:
                    raise Exception(f"Unexpected output format: {type(output)}")
                
                print(f"[Replicate] ✅ Success with {model_name}")
                return video_url, model_name
                
            except Exception as e:
                print(f"[Replicate] ❌ Failed with {model_name}: {e}")
                continue
        
        raise Exception("All Replicate models failed")
    
    def swap_face_vmodel(self, face_image, video_file):
        """
        Video face swap using VModel.AI
        Requires Supabase for file uploads
        Returns: (video_url, model_name)
        """
        if not self.vmodel_token:
            raise Exception("VMODEL_API_TOKEN not configured")
        
        if not self.supabase:
            raise Exception("Supabase not configured (required for VModel)")
        
        print("[VModel] Starting video face swap...")
        
        try:
            # Generate unique task ID
            task_id = str(uuid.uuid4())[:8]
            
            # Upload face image to Supabase
            face_bytes = face_image.read()
            face_image.seek(0)
            face_path = f"vmodel-temp/face_{task_id}.jpg"
            
            self.supabase.storage.from_('ai-photos').upload(
                face_path,
                face_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            face_url = self.supabase.storage.from_('ai-photos').get_public_url(face_path)
            print(f"[VModel] Uploaded to Supabase: {face_url}")
            
            # Upload video to Supabase
            video_bytes = video_file.read()
            video_file.seek(0)
            video_path = f"vmodel-temp/video_{task_id}.mp4"
            
            self.supabase.storage.from_('ai-photos').upload(
                video_path,
                video_bytes,
                file_options={"content-type": "video/mp4"}
            )
            video_url = self.supabase.storage.from_('ai-photos').get_public_url(video_path)
            print(f"[VModel] Uploaded to Supabase: {video_url}")
            
            # Create VModel task
            response = requests.post(
                "https://api.vmodel.ai/api/tasks/v1/create",
                headers={
                    "Authorization": f"Bearer {self.vmodel_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224",
                    "input": {
                        "target": face_url,
                        "source": video_url,
                        "disable_safety_checker": True
                    }
                },
                timeout=180
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse nested response
            if result.get('code') == 200 and 'result' in result:
                task_id = result['result']['task_id']
            else:
                task_id = result.get('task_id')
            
            if not task_id:
                raise Exception(f"VModel API error: {result}")
            
            print(f"[VModel] Task created: {task_id}, polling for result...")
            
            # Poll for completion
            time.sleep(2)  # Initial delay
            
            max_retries = 60  # 3 minutes max
            for i in range(max_retries):
                try:
                    status_response = requests.get(
                        f"https://api.vmodel.ai/api/tasks/v1/get/{task_id}",
                        headers={"Authorization": f"Bearer {self.vmodel_token}"}
                    )
                    
                    print(f"[VModel] Status check #{i+1}: HTTP {status_response.status_code}")
                    
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    
                    # Parse nested response
                    if 'result' in status_data and isinstance(status_data['result'], dict):
                        task_status = status_data['result']
                    else:
                        task_status = status_data
                    
                    print(f"[VModel] Status: {task_status.get('status', 'unknown')}")
                    
                    if task_status.get('status') == 'succeeded':
                        output_url = task_status.get('output', [None])[0]
                        if output_url:
                            print(f"[VModel] ✅ Success! Output: {output_url}")
                            return output_url, "vmodel/video-face-swap-pro"
                        else:
                            raise Exception("VModel returned no output URL")
                    
                    elif task_status.get('status') in ['failed', 'canceled']:
                        raise Exception(f"VModel task failed: {task_status.get('error', 'Unknown error')}")
                    
                    time.sleep(3)
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        print(f"[VModel] Task not found yet (404), retrying... ({i+1}/{max_retries})")
                        time.sleep(5)
                        continue
                    raise
            
            raise Exception("VModel processing timeout (3 minutes)")
            
        except Exception as e:
            print(f"[VModel] Error: {e}")
            raise
    
    def swap_face_video(self, face_image, video_file, provider="auto", gender="all"):
        """
        Main video face swap method with 3 providers
        
        Args:
            face_image: Face image file
            video_file: Video file
            provider: "auto" (Replicate→VModel), "replicate", or "vmodel"
            gender: "all", "male", "female" (deprecated, kept for compatibility)
        
        Returns:
            (video_url, provider_used, model_used)
        """
        print(f"[VideoSwap] Starting with provider: {provider}")
        
        if provider == "replicate":
            # Replicate only
            print("[VideoSwap] Using Replicate (arabyai-replicate/roop_face_swap)")
            result, model = self.swap_face_replicate(face_image, video_file)
            return result, "replicate", model
        
        elif provider == "vmodel":
            # VModel only
            print("[VideoSwap] Using VModel.AI")
            result, model = self.swap_face_vmodel(face_image, video_file)
            return result, "vmodel", model
        
        else:  # "auto" or any other value
            # Auto mode: Replicate primary → VModel fallback
            print("[VideoSwap] Auto mode - Replicate primary, VModel fallback")
            
            try:
                # Try Replicate first
                result, model = self.swap_face_replicate(face_image, video_file)
                return result, "replicate", model
            
            except Exception as replicate_error:
                print(f"[VideoSwap] Replicate failed: {replicate_error}")
                
                # Fallback to VModel if available
                if self.vmodel_token:
                    print("[VideoSwap] Falling back to VModel...")
                    try:
                        result, model = self.swap_face_vmodel(face_image, video_file)
                        return result, "vmodel (fallback)", model
                    except Exception as vmodel_error:
                        print(f"[VideoSwap] VModel fallback failed: {vmodel_error}")
                        raise Exception(f"Both providers failed. Replicate: {replicate_error}, VModel: {vmodel_error}")
                else:
                    print("[VideoSwap] VModel not configured, cannot fallback")
                    raise replicate_error
```

### Flask API Routes

```python
# routes/video_routes.py

from flask import Blueprint, request, jsonify
from utils.video_processor import VideoFaceSwapProcessor

video_bp = Blueprint('video', __name__)
video_processor = VideoFaceSwapProcessor()

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

@video_bp.route('/face-swap', methods=['POST'])
def video_face_swap():
    """Video face swap endpoint"""
    try:
        # Validate files
        if 'face_image' not in request.files or 'video' not in request.files:
            return jsonify({'error': 'Missing face_image or video'}), 400
        
        face_image = request.files['face_image']
        video_file = request.files['video']
        
        # Get parameters
        provider = request.form.get('provider', 'auto')  # auto, replicate, vmodel
        gender = request.form.get('gender', 'all')
        
        # Validate provider
        if provider not in ['auto', 'replicate', 'vmodel']:
            return jsonify({'error': f'Invalid provider: {provider}'}), 400
        
        print(f"[API] Video face swap request: provider={provider}, gender={gender}")
        
        # Process video
        result, provider_used, model_used = video_processor.swap_face_video(
            face_image, video_file, provider, gender
        )
        
        return jsonify({
            'success': True,
            'video_url': result,
            'provider': provider_used,
            'model': model_used,
            'audio_preserved': True
        })
        
    except Exception as e:
        print(f"[API] Video face swap error: {e}")
        return jsonify({'error': str(e)}), 500

@video_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get available video face swap providers"""
    return jsonify({
        'providers': {
            'auto': {
                'name': 'Auto (Replicate → VModel)',
                'strategy': 'Replicate primary → VModel fallback',
                'models': ['arabyai-replicate/roop_face_swap', 'vmodel/video-face-swap-pro'],
                'timeout': '15-77 seconds',
                'audio_preserved': True,
                'cost': '$0.10-0.14 per video',
                'status': '✅ RECOMMENDED'
            },
            'replicate': {
                'name': 'Replicate (Stable)',
                'models': ['arabyai-replicate/roop_face_swap'],
                'timeout': '~77 seconds',
                'audio_preserved': True,
                'cost': '$0.14 per video',
                'quality': 'Good, stable',
                'status': '✅ WORKING 2025'
            },
            'vmodel': {
                'name': 'VModel.AI (Premium)',
                'models': ['vmodel/video-face-swap-pro'],
                'timeout': '15-51 seconds',
                'audio_preserved': True,
                'cost': '$0.03/second (~$0.10 per short video)',
                'quality': 'Premium, commercial license',
                'status': '✅ WORKING 2025',
                'requirements': 'Requires Supabase'
            }
        }
    })
```

---

## 🧪 TESTING & DEBUGGING

### Test Web UI
```html
<!-- static/video_swap.html -->
<!-- Full UI để test API -->
```

### cURL Test Commands

#### Test Replicate
```bash
curl -X POST https://YOUR_REPLIT_URL/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=replicate"
```

#### Test VModel
```bash
curl -X POST https://YOUR_REPLIT_URL/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=vmodel"
```

#### Test Auto (Recommended)
```bash
curl -X POST https://YOUR_REPLIT_URL/api/video/face-swap \
  -F "face_image=@face.jpg" \
  -F "video=@video.mp4" \
  -F "provider=auto"
```

### Common Issues & Solutions

#### ❌ Issue: Replicate 404 Error
```
Solution: Sử dụng FULL version ID (64-char hash), không phải short name
✅ arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84
❌ arabyai-replicate/roop_face_swap
```

#### ❌ Issue: VModel 404 on Status Check
```
Solution: Phải dùng endpoint /get/{task_id}
✅ GET /api/tasks/v1/get/{task_id}
❌ GET /api/tasks/v1/{task_id}
```

#### ❌ Issue: VModel "URLs Required"
```
Solution: Upload files to Supabase Storage trước, rồi truyền public URLs
VModel không nhận file uploads trực tiếp!
```

### Debug Logs
```python
# Enable debug logging
print(f"[Replicate] Trying model: {model_name}")
print(f"[VModel] Task created: {task_id}")
print(f"[VModel] Status check #{i+1}: HTTP {status_response.status_code}")
print(f"[VModel] Status: {task_status.get('status')}")
```

---

## 📊 PERFORMANCE & COSTS

### Replicate Performance
- Average: ~77 seconds
- Cost: $0.14 per video
- Audio: ✅ Always preserved
- Reliability: High (stable)

### VModel Performance
- Average: 15-51 seconds (faster!)
- Cost: $0.03/second (~$0.10 for short video)
- Audio: ✅ Always preserved
- Reliability: High (with correct endpoint)

### Cost Comparison (30s video)
| Provider | Processing Time | Cost | Audio | Quality |
|----------|----------------|------|-------|---------|
| Replicate | ~77s | $0.14 | ✅ | Good |
| VModel | ~30s | ~$0.10 | ✅ | Premium |

### Recommendations
- **Auto mode**: Best cho production (fallback mechanism)
- **Replicate**: Best cho stability
- **VModel**: Best cho speed & cost (nếu có Supabase)

---

## 📚 RESOURCES

### API Documentation
- Replicate: https://replicate.com/docs
- VModel: https://vmodel.ai/docs/api/
- Supabase: https://supabase.com/docs

### Get API Keys
- Replicate: https://replicate.com/account/api-tokens
- VModel: https://vmodel.ai/account/api-tokens
- Supabase: https://supabase.com/dashboard

### Support
- Replicate: support@replicate.com
- VModel: support@vmodel.ai
- Supabase: support@supabase.com

---

## ✅ CHECKLIST TRIỂN KHAI

### Pre-deployment
- [ ] Tạo Replicate account & get API token
- [ ] Tạo VModel account & get API token
- [ ] Tạo Supabase project & setup bucket `ai-photos`
- [ ] Add secrets vào Replit
- [ ] Test cả 3 providers (auto, replicate, vmodel)

### Testing
- [ ] Upload test video + face image
- [ ] Verify audio preserved
- [ ] Check processing time
- [ ] Verify fallback mechanism (auto mode)
- [ ] Test error handling

### Production
- [ ] Enable Gunicorn workers (2-4)
- [ ] Setup timeout (300s for video processing)
- [ ] Monitor costs (Replicate + VModel usage)
- [ ] Setup error logging
- [ ] Implement rate limiting (optional)

---

## 📝 NOTES

### Audio Preservation
- ✅ Replicate: Audio preserved automatically
- ✅ VModel: Audio preserved automatically
- No additional configuration needed!

### File Size Limits
- Replicate: Up to ~100MB video
- VModel: Charged by duration (not size)
- Supabase: 50MB free tier

### Version Updates
- Replicate model: Check https://replicate.com/arabyai-replicate/roop_face_swap for updates
- VModel model: Check https://vmodel.ai/models/vmodel/video-face-swap-pro/ for updates
- Update version IDs in code if needed

---

**🎉 Document này cung cấp đầy đủ thông tin để triển khai Video Face Swap API với Audio Preserved trên Replit!**

*Last Updated: October 2025*
