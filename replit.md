# AI Photo Editing Backend API

## Overview
This project is a Flask-based REST API providing AI-powered photo editing features for integration with Flutter mobile applications. It aims to offer serverless AI image processing capabilities, similar to Glam AI, utilizing models from Replicate and Hugging Face. Key features include face swapping, image upscaling, old photo restoration, cartoonify effects, style transfer, template-based transformations, and video face swapping. The project emphasizes robust error handling, automatic fallback mechanisms, and persistent image storage.

## User Preferences
- **Primary**: Replicate API (arabyai-replicate/roop_face_swap) - Stable, audio preserved ✅
- **Fallback 1**: VModel.AI - Premium quality, faster, commercial license, audio preserved ✅
- **Fallback 2-5**: HuggingFace Spaces (4 providers) - FREE backup options via Gradio Client API ✅
- Planning to integrate with Supabase for user data storage
- Target platform: Flutter mobile app (Vietnamese user, builds APK locally in VS Code)
- Prefer cloud-based API approach over local model hosting

## System Architecture

### Stack
- **Backend Framework**: Flask (Python)
- **Primary AI Provider**: Replicate API (arabyai-replicate/roop_face_swap)
- **Fallback AI Providers**: 
  - VModel.AI (video-face-swap-pro)
  - 4x HuggingFace Spaces (tonyassi, MarkoVidrih, ALSv, prithivMLmods) via Gradio Client
- **Image Storage**: Supabase Storage
- **Image Processing**: Pillow (PIL), Replicate SDK, Gradio Client
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
- **Video Face Swap** (✅ 6 PROVIDERS - AUDIO PRESERVED):
    - `/api/video/face-swap`: Video face swapping with 6+ provider options:
      - `auto`: Replicate → VModel → 4 HF Spaces fallback chain (RECOMMENDED) ⭐
      - `replicate`: arabyai-replicate/roop_face_swap ($0.14, ~77s, stable) ✅
      - `vmodel`: VModel.AI premium ($0.10, 15-30s, faster) ✅
      - `hf-tonyassi`: HuggingFace tonyassi Space (FREE, gender filtering) ✅
      - `hf-marko`: HuggingFace MarkoVidrih Space (FREE) ✅
      - `hf-alsv`: HuggingFace ALSv Space (FREE) ✅
      - `hf-prithiv`: HuggingFace prithivMLmods Space (FREE) ✅
    - `/api/video/providers`: Lists all 6+ providers and their details
    - **Replicate & VModel preserve original video audio!**
    - **Status**: 6 providers (2 paid + 4 FREE HF Spaces) - Oct 2025
- **Template Video Face Swap** (✅ NEW FEATURE):
    - `/api/template-video/list`: List available template videos
    - `/api/template-video/preview/{filename}`: Preview template video
    - `/api/template-video/swap`: Swap user face into template video (user chỉ upload face, không cần video)
    - `/api/template-video/upload-template`: Upload new template (admin)
    - **Use case**: User upload face → Swap vào video template có sẵn
    - **Providers**: ✅ Replicate, ✅ VModel (reuse VideoFaceSwapProcessor)
    - **Web UI**: `/template-video-swap` for testing
- **Storage Integration**:
    - `/api/ai/process-and-save`: Processes images and optionally saves to Supabase Storage, returning a public URL.

### UI/UX and Testing
- A comprehensive web testing UI (`static/index.html`) is provided for live testing of all API features, including image upload, result preview, and download options.
- The Flutter mobile application is designed with Material 3, featuring a modern UI with three main screens: Home, Feature Detail, and Template Gallery.

### System Design
- **Video Face Swap Architecture**:
  - Auto mode: 6-provider fallback chain
    1. Replicate (stable, $0.14, ~77s) 
    2. VModel (premium, $0.10, 15-30s)
    3-6. 4x HuggingFace Spaces (FREE, queue-based)
  - Audio preservation: Replicate & VModel keep original video audio
  - Replicate model: arabyai-replicate/roop_face_swap (must use full version ID)
  - VModel: Premium quality with commercial license, requires Supabase
  - HuggingFace Spaces: FREE backup via Gradio Client API (tonyassi, marko, alsv, prithiv)
- Image storage is handled by Supabase Storage, ensuring persistent access via public URLs.
- CORS is enabled to facilitate seamless integration with the Flutter mobile application.
- Health check endpoints (`/healthz`, `/health`) are implemented for production monitoring.
- The system is designed for production readiness, utilizing Gunicorn for deployment.

## External Dependencies

### API Providers (Video Face Swap)
- **Replicate API** (PRIMARY): 
  - Model: `arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84`
  - Cost: $0.14 per video
  - Speed: ~77 seconds
  - Audio: ✅ Preserved
  - Quality: Good, stable
  - API Key: `REPLICATE_PRO_TOKEN`
  - **Note:** Must use full version ID to avoid 404 errors
  
- **VModel.AI** (FALLBACK):
  - Model: `vmodel/video-face-swap-pro`
  - Cost: $0.03/second (~$0.10 per short video)
  - Speed: ~15-30 seconds (faster!)
  - Audio: ✅ Preserved
  - Quality: Premium, commercial license
  - API Key: `VMODEL_API_TOKEN`
  - **Note:** Requires Supabase (uploads files → gets URLs → calls VModel)

- **HuggingFace Spaces** (FREE BACKUP - 4 PROVIDERS):
  - **tonyassi/video-face-swap**: Gender filtering support, most popular
  - **MarkoVidrih/video-face-swap**: Basic video face swap
  - **ALSv/video-face-swap**: Alternative free option
  - **prithivMLmods/Video-Face-Swapper**: Educational model
  - Cost: FREE (queue-based, may be slower)
  - Quality: Preview mode (downsampled for free tier)
  - API: Gradio Client API
  - **Note:** Used as fallback when Replicate/VModel fail or for cost-free testing

### Storage & Framework
- **Supabase Storage**: Used for persistent storage of processed images, configured with a public `ai-photos` bucket.
- **Flask**: Python web framework.
- **Flask-CORS**: Enables Cross-Origin Resource Sharing.
- **Pillow (PIL)**: Python Imaging Library for image manipulation.
- **requests**: HTTP client for external API calls.
- **python-dotenv**: Manages environment variables.
- **replicate (Python SDK)**: Client library for interacting with the Replicate API.
- **supabase (Python SDK)**: Client library for interacting with Supabase services.
- **gradio-client**: Client library for calling HuggingFace Spaces via Gradio API.