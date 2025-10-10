# AI Photo Editing Backend API

## Overview
This project is a Flask-based REST API providing AI-powered photo editing features for integration with Flutter mobile applications. It aims to offer serverless AI image processing capabilities, similar to Glam AI, utilizing models from Replicate and Hugging Face. Key features include face swapping, image upscaling, old photo restoration, cartoonify effects, style transfer, template-based transformations, and video face swapping. The project emphasizes robust error handling, automatic fallback mechanisms, and persistent image storage.

## User Preferences
- Primary: Replicate API for stable, reliable AI processing
- Fallback: Hugging Face Pro token for backup and higher rate limits
- Planning to integrate with Supabase for user data storage
- Target platform: Flutter mobile app
- Prefer cloud-based API approach (Replicate/HF) over local model hosting

## System Architecture

### Stack
- **Backend Framework**: Flask (Python)
- **Primary AI Provider**: Replicate API
- **Fallback AI Provider**: Hugging Face Inference API
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
- **Video Face Swap**:
    - `/api/video/face-swap`: Performs video face swapping with multi-model fallback.
    - `/api/video/providers`: Lists available video face swap models.
- **Storage Integration**:
    - `/api/ai/process-and-save`: Processes images and optionally saves to Supabase Storage, returning a public URL.

### UI/UX and Testing
- A comprehensive web testing UI (`static/index.html`) is provided for live testing of all API features, including image upload, result preview, and download options.
- The Flutter mobile application is designed with Material 3, featuring a modern UI with three main screens: Home, Feature Detail, and Template Gallery.

### System Design
- The architecture supports automatic fallback from Replicate to Hugging Face for enhanced reliability.
- Image storage is handled by Supabase Storage, ensuring persistent access via public URLs.
- CORS is enabled to facilitate seamless integration with the Flutter mobile application.
- Health check endpoints (`/healthz`, `/health`) are implemented for production monitoring.
- The system is designed for production readiness, utilizing Gunicorn for deployment.

## External Dependencies
- **Replicate API**: Primary AI model provider for various image and video processing tasks.
- **Hugging Face Inference API**: Secondary/fallback AI model provider, including specific models for video face swapping (e.g., `tonyassi/video-face-swap`, `yoshibomball123/Video-Face-Swap`).
- **Supabase Storage**: Used for persistent storage of processed images, configured with a public `ai-photos` bucket.
- **Flask**: Python web framework.
- **Flask-CORS**: Enables Cross-Origin Resource Sharing.
- **Pillow (PIL)**: Python Imaging Library for image manipulation.
- **requests**: HTTP client for external API calls.
- **python-dotenv**: Manages environment variables.
- **replicate (Python SDK)**: Client library for interacting with the Replicate API.
- **supabase (Python SDK)**: Client library for interacting with Supabase services.
- **gradio-client**: Used for accessing Hugging Face Spaces API.