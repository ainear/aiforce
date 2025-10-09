# AI Photo Editing Backend API

## Project Overview
Flask-based REST API for AI-powered photo editing features including face swap, image upscaling, old photo restoration, cartoonify effects, and style transfer. Built to integrate with Flutter mobile apps.

## Purpose
Provide serverless AI image processing capabilities using Hugging Face Inference API models for a mobile app similar to Glam AI, with features like:
- Face swapping
- HD image upscaling (Real-ESRGAN)
- Old photo restoration (GFPGAN)
- Cartoonify and style transfer
- Template-based transformations (Ghostface, Fashion, Graduate, etc.)
- Future baby prediction
- AI hugs generation
- Professional headshots

## Current State
✅ Flask API server running on port 5000
✅ **Replicate API integration (primary)** with Hugging Face fallback
✅ **Supabase Storage integration** - Persistent image storage fully functional
✅ All features fully working: HD upscale, restore, face swap, cartoonify, style transfer
✅ Advanced endpoints: background removal, depth map, AI hugs, future baby, templates
✅ Automatic fallback logic for maximum reliability
✅ CORS enabled for cross-origin requests
✅ Comprehensive API documentation updated for Replicate
✅ Production-ready with robust error handling
✅ **Web Testing UI** - Beautiful interface to test all API features
✅ **Flutter Integration Guide** - Complete Flutter code examples and documentation

## Recent Changes
- **2025-10-09**: Flutter Mobile App Complete ✅
  - Created complete Flutter app with 11 AI features
  - Beautiful UI/UX with Material 3 design
  - 3 main screens: Home, Feature Detail, Template Gallery
  - Full API integration with all backend endpoints
  - Android & iOS ready with permissions configured
  - 1800+ lines of production-ready code
  - Complete documentation (README, QUICKSTART)
  - All features matching Glam AI reference images
  
- **2025-10-09**: Supabase Storage Integration Complete ✅
  - Created Supabase project and storage bucket "ai-photos"
  - Configured public access policies (SELECT & INSERT)
  - Added SUPABASE_URL and SUPABASE_KEY to Replit Secrets
  - Implemented SupabaseStorage module for upload/delete operations
  - Added `/api/ai/process-and-save` endpoint with storage support
  - Successfully tested image upload and public URL access
  - Created comprehensive Flutter integration guide
  - All documentation updated (SUPABASE_INTEGRATION.md, FLUTTER_INTEGRATION.md)
  
- **2025-10-09**: Imported to Replit & Setup Complete
  - Successfully imported ImageForge project from ZIP file
  - Installed all Python dependencies (Flask, Replicate, Pillow, etc.)
  - Configured REPLICATE_API_TOKEN secret
  - Set up Flask server workflow on port 5000
  - Configured deployment for autoscale (production-ready)
  - Web UI fully functional and tested
  
- **2025-10-09**: Template Face Swap System Added
  - Created template gallery with 12 professional photos (female/male/mixed)
  - API endpoints for listing templates and face swapping with templates
  - Beautiful template gallery UI with category organization
  - Live template preview and selection
  - Face upload with preview before swap
  - Production-ready template face swap feature
  
- **2025-10-09**: Web Testing UI Added
  - Created beautiful web interface to test all API features
  - Tabbed layout: Basic Features, Advanced Features & Template Face Swap
  - Live image upload and result preview
  - Download processed images
  - Responsive design with gradient UI
  - All features accessible from browser
  
- **2025-10-09**: Replicate API Integration (Major Update)
  - Migrated to Replicate API as primary provider
  - Implemented automatic fallback to Hugging Face
  - All features now fully functional (cartoonify, style transfer, face swap)
  - Added ReplicateProcessor module with robust error handling
  - Updated all endpoints with dual-provider support
  - Updated documentation for production readiness
  
- **2025-10-08**: Initial project setup
  - Created Flask application with image processing endpoints
  - Integrated Hugging Face Inference API
  - Added basic and advanced feature routes
  - Created API integration documentation
  - Set up workflow for running server

## Architecture

### Stack
- **Backend Framework**: Flask (Python)
- **Primary AI Provider**: Replicate API (stable, feature-complete)
- **Fallback AI Provider**: Hugging Face Inference API
- **Image Storage**: Supabase Storage (persistent, public URLs)
- **Image Processing**: Pillow (PIL), Replicate SDK
- **CORS**: Flask-CORS for Flutter app integration

### Project Structure
```
.
├── flutter_app/                # Flutter mobile app (NEW!)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/api_config.dart
│   │   ├── models/
│   │   ├── services/api_service.dart
│   │   ├── screens/
│   │   └── widgets/
│   ├── android/
│   ├── ios/
│   ├── pubspec.yaml
│   ├── README.md
│   └── QUICKSTART.md
├── app.py                      # Main Flask application
├── routes/
│   ├── __init__.py
│   └── advanced_features.py    # Advanced AI endpoints
├── utils/
│   ├── __init__.py
│   ├── image_processor.py      # Image processing utilities
│   ├── replicate_processor.py  # Replicate API integration
│   ├── supabase_storage.py     # Supabase Storage integration
│   └── response_helper.py      # Response formatting utilities
├── static/                     # Web UI files
│   ├── index.html             # Testing interface
│   ├── styles.css             # UI styling
│   └── script.js              # API integration JS
├── test_api.py                 # API testing script
├── API_INTEGRATION.md          # Flutter integration guide
├── FLUTTER_INTEGRATION.md      # Complete Flutter code examples
├── SUPABASE_INTEGRATION.md     # Supabase setup & usage guide
├── IMPLEMENTATION_NOTES.md     # Technical details & architecture
├── flutter_example.dart        # Quick Flutter code example
├── .env.example                # Environment variables template
└── replit.md                   # This file
```

### Endpoints

**Basic Features:**
- `/api/ai/hd-image` - Upscale images 2x/4x ✅ (Replicate+HF)
- `/api/ai/fix-old-photo` - Restore old/damaged photos ✅ (Replicate+HF)
- `/api/ai/cartoonify` - Cartoon/Anime style ✅ (Replicate)
- `/api/ai/swap-face` - Face swapping between images ✅ (Replicate+HF)
- `/api/ai/style-transfer` - Artistic style transfer ✅ (Replicate)

**Advanced Features:**
- `/api/advanced/ai-hugs` - Generate hugging photos ✅ (Replicate+HF)
- `/api/advanced/future-baby` - Baby face prediction ✅ (Replicate+HF)
- `/api/advanced/template-styles` - Template transformations ✅ (Replicate+HF)
- `/api/advanced/muscle-enhance` - Fitness body ✅ (Replicate+HF)
- `/api/advanced/remove-background` - Background removal ✅ (Replicate+HF)
- `/api/advanced/depth-map` - Depth mapping ✅ (Replicate+HF)
- `/api/advanced/colorize` - Colorize B&W images ⚠️ (HF only)

**Template Face Swap:**
- `/api/templates/list` - List all face swap templates ✅
- `/api/templates/face-swap` - Swap user face with template ✅ (Replicate+HF)

**Storage Endpoints:**
- `/api/ai/process-and-save` - Process image & optionally save to Supabase ✅
  - Supports all AI features (hd-upscale, cartoonify, restore, remove-bg)
  - Returns storage URL when `save_storage=true`
  - Returns image bytes when `save_storage=false`

## User Preferences
- Primary: Replicate API for stable, reliable AI processing
- Fallback: Hugging Face Pro token for backup and higher rate limits
- Planning to integrate with Supabase for user data storage
- Target platform: Flutter mobile app
- Prefer cloud-based API approach (Replicate/HF) over local model hosting

## Dependencies
- flask - Web framework
- flask-cors - CORS support
- pillow - Image processing
- requests - HTTP client for API calls
- python-dotenv - Environment configuration
- replicate - Replicate API SDK
- supabase - Supabase client for storage

## Environment Variables
Required in `.env` / Replit Secrets:
- `REPLICATE_API_TOKEN` - Replicate API token (primary provider) ✅
- `HUGGINGFACE_API_TOKEN` - Hugging Face API token (Pro recommended)
- `SUPABASE_URL` - Supabase project URL ✅
- `SUPABASE_KEY` - Supabase API key (anon/public) ✅
- `SESSION_SECRET` - Flask session secret

## Integration Notes

### For Flutter App
1. Use multipart/form-data for image uploads
2. All endpoints return PNG image data on success
3. Error responses are JSON with `error` and `details` fields
4. Processing time: 5-30 seconds depending on model
5. See `API_INTEGRATION.md` for Flutter code examples

### Alternative Services
- **Replicate API**: ✅ Integrated as primary provider
- **Hugging Face API**: ✅ Integrated as fallback provider
- **Supabase Storage**: ✅ Fully integrated for permanent image storage
  - Bucket: `ai-photos` (public read access)
  - Automatic URL generation for stored images
  - User-organized file structure: `user-id/feature_timestamp_uuid.png`

## Development Commands
- Run server: `python app.py`
- Test endpoints: `python test_api.py`
- Port: 5000 (webview enabled)

## Next Steps (Future Phase)
- ✅ Supabase Storage integration (COMPLETE)
- ✅ Flutter integration documentation (COMPLETE)
- Add user authentication (Supabase Auth)
- Implement rate limiting
- Create payment integration for premium features
- Add job queue for batch processing
- Optimize model selection based on performance
- Add image caching layer
- Add image gallery/history feature
- Deploy with production WSGI server (gunicorn)

## Notes
- Server runs in debug mode for development
- All requests require valid Hugging Face API token
- CORS enabled for all origins (configure for production)
- Images processed in memory, no local storage currently
- Models load on-demand via Hugging Face Inference API
