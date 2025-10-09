# 🎨 ImageForge AI Photo Editor

> **Flutter mobile app + Flask API backend** for AI-powered photo editing features similar to Glam AI

[![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B?logo=flutter)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com)
[![Replicate](https://img.shields.io/badge/Replicate-API-orange)](https://replicate.com)
[![Supabase](https://img.shields.io/badge/Supabase-Storage-3ECF8E?logo=supabase)](https://supabase.com)

## 📱 Features

### 🔥 Top Hits
- ✨ **AI Hugs** - Generate hugging photos from 2 images
- 👶 **Future Baby** - Predict your future baby
- 🎭 **Cartoonify** - Anime/Cartoon/Sketch styles
- 🎬 **Template Swap** - Face swap with templates (Ghostface, Fashion, etc.)

### 🎨 Enhancement
- 📸 **HD Upscale** - 2x/4x image resolution
- 🔧 **Fix Old Photo** - Restore old/damaged photos
- 🌈 **Colorize** - Colorize black & white images

### 🖼️ Creative Tools
- 🗑️ **Remove Background** - AI background removal
- 👤 **Face Swap** - Swap faces between 2 images
- 🎨 **Style Transfer** - Artistic style transformation
- 🗺️ **Depth Map** - Generate depth maps

**Total: 11 AI Features**

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Flutter App    │ ← Mobile (Android/iOS)
│  (Frontend)     │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│   Flask API     │ ← Backend (Python)
│   (Replit)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────────┐
│Replicate│ │   Supabase   │
│   API   │ │   Storage    │
└─────────┘ └──────────────┘
```

### Tech Stack

**Frontend:**
- Flutter 3.0+
- Material Design 3
- HTTP package for API calls

**Backend:**
- Flask 3.0 (Python)
- Gunicorn (Production WSGI)
- Replicate API (Primary AI provider)
- Hugging Face API (Fallback)
- Supabase Storage (Image persistence)

**Deployment:**
- Backend: Replit Autoscale
- Frontend: Android APK / iOS IPA

---

## 🚀 Quick Start

### Backend (API Server)

**On Replit (Production):**
```bash
# Already deployed at:
https://aiforce-onenearcelo.replit.app
```

**Local Development:**
```bash
# Clone repo (hoặc pull nếu đã có)
git clone https://github.com/YOUR_USERNAME/imageforge-ai-photo-editor.git
cd imageforge-ai-photo-editor

# Nếu lỗi Android build, xem: ANDROID_BUILD_FIX.md

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python app.py
# Server: http://localhost:5000
```

### Frontend (Flutter App)

```bash
# Navigate to Flutter app
cd flutter_app

# Clean & install dependencies
flutter clean
flutter pub get

# Run on device/emulator
flutter run

# Build APK (Android)
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk

# ⚠️ Nếu lỗi "Android v1 embedding", đã fix sẵn!
# Xem: ANDROID_BUILD_FIX.md
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| **📍 [START_HERE.md](START_HERE.md)** | **Start here** - Quick overview |
| [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) | Ready to push GitHub checklist ✅ |
| [GITHUB_AND_LOCAL_BUILD.md](GITHUB_AND_LOCAL_BUILD.md) | Push to GitHub & build APK locally |
| [ANDROID_BUILD_FIX.md](ANDROID_BUILD_FIX.md) | Fix Android v1 embedding error 🔧 |
| [HOW_TO_RUN_FLUTTER_APP.md](HOW_TO_RUN_FLUTTER_APP.md) | Detailed Flutter app setup |
| [FLUTTER_APP_SUMMARY.md](FLUTTER_APP_SUMMARY.md) | Complete Flutter app summary |
| [API_INTEGRATION.md](API_INTEGRATION.md) | Backend API documentation |
| [SUPABASE_INTEGRATION.md](SUPABASE_INTEGRATION.md) | Supabase storage guide |
| [DEPLOYMENT_FIX.md](DEPLOYMENT_FIX.md) | Deployment troubleshooting |

---

## 🔧 Configuration

### Backend Environment Variables

Create `.env` file:
```bash
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxxxxxxxxxxxx
HUGGINGFACE_API_TOKEN=hf_xxxxxxxxxxxxx  # Optional fallback
```

### Flutter API Configuration

**File:** `flutter_app/lib/config/api_config.dart`
```dart
class ApiConfig {
  static const String baseUrl = 'https://aiforce-onenearcelo.replit.app';
}
```

---

## 📂 Project Structure

```
.
├── flutter_app/                # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/api_config.dart
│   │   ├── models/
│   │   ├── services/api_service.dart
│   │   ├── screens/
│   │   └── widgets/
│   ├── android/
│   ├── ios/
│   └── pubspec.yaml
├── app.py                      # Flask backend
├── routes/
│   └── advanced_features.py    # Advanced endpoints
├── utils/
│   ├── replicate_processor.py  # Replicate API client
│   ├── supabase_storage.py     # Storage client
│   └── image_processor.py
├── static/                     # Web testing UI
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🌐 API Endpoints

### Basic Features
- `POST /api/ai/hd-image` - HD upscale (2x/4x)
- `POST /api/ai/fix-old-photo` - Restore old photos
- `POST /api/ai/cartoonify` - Cartoonify image
- `POST /api/ai/swap-face` - Face swap
- `POST /api/ai/style-transfer` - Style transfer

### Advanced Features
- `POST /api/advanced/ai-hugs` - AI hugs
- `POST /api/advanced/future-baby` - Future baby
- `POST /api/advanced/remove-background` - Remove BG
- `POST /api/advanced/depth-map` - Depth map
- `POST /api/advanced/colorize` - Colorize

### Templates
- `GET /api/templates/list` - List templates
- `POST /api/templates/face-swap` - Template face swap

### Health
- `GET /healthz` - Health check
- `GET /api` - API info

**Full API docs:** [API_INTEGRATION.md](API_INTEGRATION.md)

---

## 🎯 Development Workflow

### 1. **Local Development**

```bash
# Backend (Terminal 1)
python app.py

# Flutter (Terminal 2)
cd flutter_app
flutter run
```

### 2. **Testing**

```bash
# Test backend API
curl http://localhost:5000/api

# Test Flutter app
flutter run
# Or open Web UI: http://localhost:5000
```

### 3. **Build & Deploy**

```bash
# Build Flutter APK
cd flutter_app
flutter build apk --release

# Deploy backend (on Replit)
# Just push to Replit Git → Auto-deploy
```

---

## 🔐 Security

- ✅ All secrets in `.env` (gitignored)
- ✅ CORS configured for security
- ✅ API key rotation via Replicate/Supabase
- ✅ No hardcoded credentials

**Never commit:**
- `.env` file
- API keys/tokens
- Database credentials

---

## 📊 Stats

- 📱 **11 AI Features**
- 🎨 **3 Flutter Screens**
- 💻 **1,899 Lines of Dart Code**
- 🐍 **465 Lines of Python Code**
- 📦 **10+ Dependencies**
- ⚡ **Production Ready**

---

## 🐛 Troubleshooting

### Flutter App

**Issue:** Cannot connect to API
```bash
# Check API URL in lib/config/api_config.dart
# Must be: https://aiforce-onenearcelo.replit.app
```

**Issue:** Build failed
```bash
flutter clean
flutter pub get
flutter build apk --release
```

### Backend API

**Issue:** Health check failing
```bash
# Check logs in Replit
# Ensure /healthz endpoint returns 200 OK
```

**Issue:** AI processing timeout
```bash
# Increase timeout in deployment config
# Default: 120s (sufficient for most operations)
```

**More troubleshooting:** [DEPLOYMENT_FIX.md](DEPLOYMENT_FIX.md)

---

## 🚢 Deployment

### Backend (Replit)

✅ Already deployed: `https://aiforce-onenearcelo.replit.app`

Configuration:
- **Type:** Autoscale
- **Server:** Gunicorn (2 workers)
- **Timeout:** 120s
- **Health check:** `/healthz`

### Frontend (Mobile App)

```bash
# Build APK
cd flutter_app
flutter build apk --release

# Output
build/app/outputs/flutter-apk/app-release.apk
```

**Distribution options:**
- Direct APK install
- Google Play Store
- TestFlight (iOS)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

This project is proprietary. All rights reserved.

---

## 🙏 Acknowledgments

- **Replicate** - AI model inference
- **Hugging Face** - ML models
- **Supabase** - Image storage
- **Flutter** - Mobile framework
- **Flask** - Web framework

---

## 📞 Support

- 📖 Documentation: See all `.md` files
- 🐛 Issues: Create GitHub issue
- 📧 Contact: [Your email/contact]

---

## 🎉 Ready to Use!

**Quick Start:**
1. ✅ Backend running: https://aiforce-onenearcelo.replit.app
2. ✅ Flutter app configured
3. ✅ API keys setup
4. ✅ Build APK: `flutter build apk --release`

**Let's build something amazing! 🚀**
