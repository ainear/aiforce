# Supabase Storage Integration Guide

## 📦 Tổng Quan

API hiện tại đã được tích hợp **Supabase Storage** để lưu trữ ảnh đã xử lý cho user.

**Kiến trúc:**
```
Flutter App → Replit API → Replicate AI (xử lý ảnh)
                ↓
         Supabase Storage (lưu ảnh kết quả)
```

## 🔧 Cách Setup Supabase

### Bước 1: Tạo Supabase Project
1. Truy cập [supabase.com](https://supabase.com)
2. Đăng ký/Đăng nhập
3. Tạo project mới (miễn phí 500MB)

### Bước 2: Tạo Storage Bucket
1. Vào **Storage** trong dashboard
2. Tạo bucket mới: `ai-photos`
3. Chọn **Public bucket** (để user có thể download)
4. Save

### Bước 3: Lấy API Credentials
1. Vào **Settings** → **API**
2. Copy:
   - **Project URL** (VD: `https://xxxxx.supabase.co`)
   - **anon/public key** (key công khai)

### Bước 4: Thêm vào Environment Variables

Thêm vào file `.env`:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Hoặc add vào **Replit Secrets** (Tools → Secrets):
- `SUPABASE_URL`
- `SUPABASE_KEY`

## 📝 Cách Sử Dụng

### Module đã tạo:

1. **`utils/supabase_storage.py`** - Supabase Storage Manager
   - `upload_image()` - Upload ảnh
   - `get_image_url()` - Lấy URL
   - `delete_image()` - Xóa ảnh
   - `list_user_images()` - List ảnh của user

2. **`utils/response_helper.py`** - Helper xử lý response
   - Tự động lưu vào Supabase nếu cần
   - Return URL hoặc image bytes

3. **`example_supabase_endpoints.py`** - Ví dụ endpoints mới

### Option 1: Tự Động Lưu (Recommended)

Copy code từ `example_supabase_endpoints.py` vào `app.py`:

**Endpoint mới với storage:**
```
POST /api/ai/hd-image-storage
POST /api/ai/swap-face-storage
POST /api/storage/list/<user_id>
POST /api/storage/delete
```

**Cách gọi từ Flutter:**
```dart
// Upload và lưu vào Supabase
var request = http.MultipartRequest(
  'POST', 
  Uri.parse('$baseUrl/api/ai/hd-image-storage')
);

request.files.add(
  await http.MultipartFile.fromPath('image', imageFile.path)
);
request.fields['scale'] = '2';
request.fields['save_storage'] = 'true';  // Lưu vào Supabase
request.fields['user_id'] = 'user123';    // Optional

var response = await request.send();
var responseData = await response.stream.bytesToString();
var json = jsonDecode(responseData);

// Lấy URL ảnh đã lưu
String imageUrl = json['storage_url'];  
// VD: https://xxxxx.supabase.co/storage/v1/object/public/ai-photos/user123/hd-upscale_20251009_abc123.png
```

### Option 2: Manual Control

Tự gọi storage khi cần:
```python
from utils.supabase_storage import SupabaseStorage

# Trong endpoint của bạn
storage = SupabaseStorage()
result = storage.upload_image(
    result_image, 
    user_id='user123',
    feature_type='hd-upscale'
)

if result['success']:
    url = result['url']  # Public URL
    path = result['path']  # Storage path
```

## 🎯 Response Format

### Khi `save_storage=true`:
```json
{
  "success": true,
  "message": "Image processed and saved",
  "storage_url": "https://xxxxx.supabase.co/storage/v1/object/public/ai-photos/user123/face-swap_20251009_abc123.png",
  "filename": "face-swap_20251009_abc123.png",
  "path": "user123/face-swap_20251009_abc123.png"
}
```

### Khi `save_storage=false` (default):
- Response: Binary image data (như cũ)
- Content-Type: `image/png`

## 📱 Flutter Integration

### 1. Service Class
```dart
class AIPhotoAPI {
  final String baseUrl = 'https://your-replit-url.repl.co';
  
  Future<Map<String, dynamic>> hdImageWithStorage(
    File imageFile, 
    String userId,
    {int scale = 2}
  ) async {
    var request = http.MultipartRequest(
      'POST', 
      Uri.parse('$baseUrl/api/ai/hd-image-storage')
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path)
    );
    request.fields['scale'] = scale.toString();
    request.fields['save_storage'] = 'true';
    request.fields['user_id'] = userId;
    
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    return jsonDecode(responseData);
  }
  
  Future<List<dynamic>> getUserImages(String userId) async {
    var response = await http.get(
      Uri.parse('$baseUrl/api/storage/list/$userId')
    );
    
    var data = jsonDecode(response.body);
    return data['images'];
  }
}
```

### 2. Display Saved Images
```dart
// Hiển thị ảnh từ Supabase URL
Image.network(
  'https://xxxxx.supabase.co/storage/v1/object/public/ai-photos/user123/image.png',
  loadingBuilder: (context, child, progress) {
    if (progress == null) return child;
    return CircularProgressIndicator();
  },
)
```

## 💾 Storage Organization

Files được tổ chức theo cấu trúc:
```
ai-photos/
├── user123/
│   ├── hd-upscale_20251009_abc123.png
│   ├── face-swap_20251009_def456.png
│   └── cartoonify_20251009_ghi789.png
├── user456/
│   └── ...
└── public/
    └── ... (nếu không có user_id)
```

## 🔐 Security Notes

- ✅ Bucket `ai-photos` là **public** - user có thể download
- ✅ Chỉ dùng **anon key** - không cần auth để upload
- ⚠️ Production nên add:
  - Row Level Security (RLS) policies
  - File size limits
  - Rate limiting

## 📊 Supabase Free Tier

- ✅ 500MB storage (đủ ~1000-2000 ảnh)
- ✅ 2GB bandwidth/tháng
- ✅ Unlimited API requests
- Nâng cấp: $25/tháng → 8GB storage

## 🚀 Deploy Checklist

1. ✅ Tạo Supabase project
2. ✅ Tạo bucket `ai-photos` (public)
3. ✅ Add `SUPABASE_URL` và `SUPABASE_KEY` vào Replit Secrets
4. ✅ Copy endpoints từ `example_supabase_endpoints.py` vào `app.py`
5. ✅ Deploy Replit app
6. ✅ Test upload từ Flutter app

## ❓ FAQs

**Q: Có cần xóa ảnh cũ không?**
A: Nên implement auto-delete ảnh sau 7-30 ngày để tiết kiệm storage.

**Q: Làm sao để ảnh private (chỉ user mới xem được)?**
A: Đổi bucket sang private + implement RLS policies + dùng signed URLs.

**Q: Upload bị lỗi 413 (file too large)?**
A: Resize ảnh xuống max 1024px trước khi upload.

## 📚 Tài Liệu

- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Python Client](https://supabase.com/docs/reference/python/storage-from-upload)
