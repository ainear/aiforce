# AI Photo Editing Backend API

## Overview
This project is a Flask-based REST API providing AI-powered photo editing features for integration with Flutter mobile applications. It aims to offer serverless AI image processing capabilities, similar to Glam AI, utilizing models from Replicate and Hugging Face. Key features include face swapping, image upscaling, old photo restoration, cartoonify effects, style transfer, template-based transformations, and video face swapping. The project emphasizes robust error handling, automatic fallback mechanisms, and persistent image storage.

## User Preferences
- **Primary**: Replicate API (yan-ops/face_swap) - Stable, 105M+ runs, audio preserved ✅
- **Fallback**: VModel.AI - Premium quality, commercial license, audio preserved ✅
- **Disabled**: HuggingFace Pro (all models had compatibility issues)
- Planning to integrate with Supabase for user data storage
- Target platform: Flutter mobile app (Vietnamese user, builds APK locally in VS Code)
- Prefer cloud-based API approach over local model hosting

## System Architecture

### Stack
- **Backend Framework**: Flask (Python)
- **Primary AI Provider**: Replicate API (yan-ops/face_swap)
- **Fallback AI Provider**: VModel.AI (video-face-swap-pro)
- **Disabled Provider**: HuggingFace (compatibility issues with all video models)
- **Image Storage**: Supabase Storage
- **Image Processing**: Pillow (PIL), Replicate SDK
- **CORS**: Flask-CORS

### Core Features and Endpoints
- **Basic Photo Editing**:
    - `/api/ai/hd-image`: Upscales images.
    - `/api/ai/fix-old-photo`: Restores old photos.
    - `/api/ai/cartoonify`: Applies cartoon/anime styles.
    - `/api/ai/swap-face`: Swaps faces between images.
    - `/api/ai/style-transfer`: Applies artistic style transfer.
- **Advanced Photo Editing**:
    - `/api/advanced/ai-hugs`: Generates hugging photos.
    - `/api/advanced/future-baby`: Predicts future baby faces.
    - `/api/advanced/template-styles`: Applies template transformations.
    - `/api/advanced/muscle-enhance`: Enhances body physique.
    - `/api/advanced/remove-background`: Removes image backgrounds.
    - `/api/advanced/depth-map`: Generates depth maps.
    - `/api/advanced/colorize`: Colorizes black and white images.
- **Template Face Swap**:
    - `/api/templates/list`: Lists available face swap templates.
    - `/api/templates/face-swap`: Swaps user faces with templates.
- **Video Face Swap** (✅ AUDIO PRESERVED):
    - `/api/video/face-swap`: Video face swapping with 3 provider options:
      - `auto`: Replicate primary → VModel fallback (RECOMMENDED)
      - `replicate`: yan-ops/face_swap (popular, stable, 105M+ runs)
      - `vmodel`: VModel.AI premium (~15-30s, commercial license)
    - `/api/video/providers`: Lists available video face swap providers and models.
    - **All providers preserve original video audio!**
- **Storage Integration**:
    - `/api/ai/process-and-save`: Processes images and optionally saves to Supabase Storage, returning a public URL.

### UI/UX and Testing
- A comprehensive web testing UI (`static/index.html`) is provided for live testing of all API features, including image upload, result preview, and download options.
- The Flutter mobile application is designed with Material 3, featuring a modern UI with three main screens: Home, Feature Detail, and Template Gallery.

### System Design
- **Video Face Swap Architecture**:
  - Auto mode: Replicate (fast, cheap) → VModel (premium) fallback
  - Audio preservation: All providers keep original video audio
  - Replicate model: yan-ops/face_swap (105M+ runs, proven stable)
  - VModel: Premium quality with commercial license
  - HuggingFace: DISABLED due to compatibility issues
- Image storage is handled by Supabase Storage, ensuring persistent access via public URLs.
- CORS is enabled to facilitate seamless integration with the Flutter mobile application.
- Health check endpoints (`/healthz`, `/health`) are implemented for production monitoring.
- The system is designed for production readiness, utilizing Gunicorn for deployment.

## External Dependencies

### API Providers (Video Face Swap)
- **Replicate API** (PRIMARY): 
  - Model: `yan-ops/face_swap`
  - Popularity: 105M+ runs (most stable)
  - Speed: Varies by video length
  - Audio: ✅ Preserved
  - API Key: `REPLICATE_PRO_TOKEN`
  
- **VModel.AI** (FALLBACK):
  - Model: `vmodel/video-face-swap-pro`
  - Cost: $0.03/second (~$0.10 per short video)
  - Speed: ~15-30 seconds
  - Audio: ✅ Preserved
  - Quality: Premium, commercial license
  - API Key: `VMODEL_API_TOKEN`
  - **Note:** Requires Supabase (uploads files → gets URLs → calls VModel)

- **HuggingFace** (DISABLED):
  - All models failed due to compatibility issues
  - No longer used in production

### Storage & Framework
- **Supabase Storage**: Used for persistent storage of processed images, configured with a public `ai-photos` bucket.
- **Flask**: Python web framework.
- **Flask-CORS**: Enables Cross-Origin Resource Sharing.
- **Pillow (PIL)**: Python Imaging Library for image manipulation.
- **requests**: HTTP client for external API calls.
- **python-dotenv**: Manages environment variables.
- **replicate (Python SDK)**: Client library for interacting with the Replicate API.
- **supabase (Python SDK)**: Client library for interacting with Supabase services.