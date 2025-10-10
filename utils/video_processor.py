import os
import time
import requests
import replicate
from io import BytesIO
from PIL import Image
import base64
from gradio_client import Client
import tempfile

class VideoFaceSwapProcessor:
    """
    Video Face Swap với Hugging Face Pro + Replicate Pro
    - HF Pro: Multiple models với 5-7s timeout auto-fallback
    - Replicate Pro: Backup option
    """
    
    def __init__(self):
        self.hf_pro_token = os.getenv('HUGGINGFACE_PRO_TOKEN', '')
        self.replicate_pro_token = os.getenv('REPLICATE_PRO_TOKEN', '')
        self.hf_timeout = 60  # 60 seconds timeout for HF models (video processing takes time)
        
        # Hugging Face models - DISABLED (all models have compatibility issues)
        # Using Replicate as primary provider
        self.hf_models = []
        
        # Replicate Pro models - DISABLED FOR VIDEO (image swap only)
        # All Replicate models tested are for IMAGE face swap, not VIDEO
        # yan-ops/face_swap: 105M+ runs but IMAGE only
        # arabyai-replicate/roop_face_swap: 404 not found
        self.replicate_models = []
        
        # VModel.AI credentials
        self.vmodel_token = os.getenv('VMODEL_API_TOKEN', '')
    
    def _save_temp_file(self, file_data, suffix='.jpg'):
        """Save uploaded file to temp location"""
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        if hasattr(file_data, 'read'):
            temp.write(file_data.read())
        else:
            temp.write(file_data)
        temp.close()
        return temp.name
    
    def _try_hf_model(self, model_config, face_image_path, video_path, gender="all"):
        """Try single HF model with timeout"""
        model_name = model_config["name"]
        params = model_config["params"]
        video_format = model_config.get("video_format", "file")
        
        try:
            print(f"[HF] Trying model: {model_name}")
            start_time = time.time()
            
            from gradio_client import handle_file
            client = Client(
                model_name,
                hf_token=self.hf_pro_token if self.hf_pro_token else None
            )
            
            # Prepare arguments based on model config - simple predict only
            result = client.predict(
                handle_file(face_image_path),
                handle_file(video_path),
                api_name="/predict"
            )
            
            elapsed = time.time() - start_time
            print(f"[HF] {model_name} completed in {elapsed:.2f}s")
            
            # Check if timed out
            if elapsed > self.hf_timeout:
                raise TimeoutError(f"Model took {elapsed:.2f}s, exceeds {self.hf_timeout}s timeout")
            
            return result
            
        except TimeoutError as e:
            print(f"[HF] {model_name} timeout: {e}")
            raise
        except Exception as e:
            print(f"[HF] {model_name} failed: {e}")
            raise
    
    def swap_face_huggingface(self, face_image, video_file, gender="all"):
        """
        HuggingFace Pro video face swap với multi-model fallback
        - Timeout: 5-7s per model
        - Auto fallback nếu model chậm hoặc lỗi
        """
        if not self.hf_pro_token:
            raise Exception("HUGGINGFACE_PRO_TOKEN required for video face swap")
        
        # Save files to temp
        face_path = self._save_temp_file(face_image.stream if hasattr(face_image, 'stream') else face_image, '.jpg')
        
        # Determine video extension
        video_ext = '.mp4'
        if hasattr(video_file, 'filename'):
            if video_file.filename.endswith('.avi'):
                video_ext = '.avi'
            elif video_file.filename.endswith('.mov'):
                video_ext = '.mov'
        
        video_path = self._save_temp_file(video_file.stream if hasattr(video_file, 'stream') else video_file, video_ext)
        
        # Try each HF model with timeout
        last_error = None
        for model_config in self.hf_models:
            model_name = model_config["name"]
            try:
                result = self._try_hf_model(model_config, face_path, video_path, gender)
                
                # Success! Return video file path
                print(f"[HF] ✅ Success with {model_name}")
                return result, model_name
                
            except TimeoutError as e:
                last_error = e
                print(f"[HF] ⏱️ {model_name} timeout, trying next model...")
                continue
                
            except Exception as e:
                last_error = e
                print(f"[HF] ❌ {model_name} failed, trying next model...")
                continue
        
        # All HF models failed
        raise Exception(f"All HuggingFace models failed. Last error: {last_error}")
    
    def swap_face_replicate(self, face_image, video_file):
        """
        Replicate Pro video face swap
        - Fallback option khi HF fails
        """
        if not self.replicate_pro_token:
            raise Exception("REPLICATE_PRO_TOKEN required for Replicate video face swap")
        
        os.environ["REPLICATE_API_TOKEN"] = self.replicate_pro_token
        
        # Save face image properly for Replicate
        from PIL import Image
        import io
        
        # Read image data correctly
        if hasattr(face_image, 'stream'):
            # Flask FileStorage object
            face_image.stream.seek(0)  # Reset to beginning
            face_data = face_image.stream.read()
        elif hasattr(face_image, 'read'):
            # File-like object
            face_data = face_image.read()
        else:
            # Raw bytes
            face_data = face_image
        
        # Convert to RGB JPEG using PIL
        try:
            # Open image from bytes
            img = Image.open(io.BytesIO(face_data))
            
            # Convert to RGB (handles PNG, WEBP, RGBA, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPEG to temp file
            face_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(face_temp.name, 'JPEG', quality=95)
            face_path = face_temp.name
            face_temp.close()
            print(f"[Replicate] Image converted to JPEG: {face_path}")
        except Exception as e:
            print(f"[Replicate] Image conversion failed: {e}, using raw data")
            # Fallback: save raw data
            face_path = self._save_temp_file(face_data, '.jpg')
        
        # Save video
        video_path = self._save_temp_file(video_file.stream if hasattr(video_file, 'stream') else video_file, '.mp4')
        
        # Try models in order
        for model_name in self.replicate_models:
            try:
                print(f"[Replicate] Trying model: {model_name}")
                
                # Open files for Replicate
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
                    first_item = output[0]
                    if isinstance(first_item, str):
                        video_url = first_item
                    elif hasattr(first_item, 'url'):
                        video_url = first_item.url  # type: ignore
                    else:
                        video_url = str(first_item)
                elif hasattr(output, 'url'):
                    # FileOutput object
                    video_url = output.url  # type: ignore
                elif hasattr(output, '__str__'):
                    # Try converting to string
                    video_url = str(output)
                else:
                    raise Exception(f"Unexpected output format: {type(output)}")
                
                print(f"[Replicate] ✅ Success with {model_name}")
                return video_url, model_name
                
            except Exception as e:
                error_msg = str(e)
                try:
                    if hasattr(e, 'detail'):
                        error_msg = f"{error_msg} - {getattr(e, 'detail')}"
                except:
                    pass
                print(f"[Replicate] ❌ {model_name} failed: {error_msg}")
                continue
        
        raise Exception("All Replicate models failed")
    
    def _upload_to_supabase(self, file_data, filename):
        """Upload file to Supabase and return public URL"""
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise Exception("SUPABASE_URL and SUPABASE_KEY required for VModel (needs public URLs)")
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Upload to ai-photos bucket
        file_path = f"vmodel-temp/{filename}"
        supabase.storage.from_('ai-photos').upload(
            file_path,
            file_data,
            {"content-type": "video/mp4" if filename.endswith('.mp4') else "image/jpeg"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_('ai-photos').get_public_url(file_path)
        print(f"[VModel] Uploaded to Supabase: {public_url}")
        return public_url
    
    def swap_face_vmodel(self, face_image, video_file):
        """
        VModel.AI video face swap with audio preservation
        - Premium quality, ~15s processing
        - Audio preserved by default
        - Requires Supabase for temporary file hosting (VModel needs URLs)
        """
        if not self.vmodel_token:
            raise Exception("VMODEL_API_TOKEN required for VModel video face swap")
        
        print("[VModel] Starting video face swap...")
        
        import requests
        import uuid
        
        # Read face image
        if hasattr(face_image, 'stream'):
            face_image.stream.seek(0)
            face_data = face_image.stream.read()
        elif hasattr(face_image, 'read'):
            face_data = face_image.read()
        else:
            face_data = face_image
        
        # Read video
        if hasattr(video_file, 'stream'):
            video_file.stream.seek(0)
            video_data = video_file.stream.read()
        elif hasattr(video_file, 'read'):
            video_data = video_file.read()
        else:
            video_data = video_file
        
        # Upload files to Supabase to get public URLs
        unique_id = str(uuid.uuid4())[:8]
        try:
            face_url = self._upload_to_supabase(face_data, f"face_{unique_id}.jpg")
            video_url = self._upload_to_supabase(video_data, f"video_{unique_id}.mp4")
            
            # VModel API call with URLs (JSON format)
            response = requests.post(
                "https://api.vmodel.ai/api/tasks/v1/create",
                headers={
                    "Authorization": f"Bearer {self.vmodel_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "537e83f7ed84751dc56aa80fb2391b07696c85a49967c72c64f002a0ca2bb224",
                    "input": {
                        "target": face_url,  # URL to face image
                        "source": video_url,  # URL to video
                        "disable_safety_checker": True
                    }
                },
                timeout=180
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse VModel response format: {'code': 200, 'result': {'task_id': '...', 'task_cost': ...}}
            if result.get('code') == 200 and 'result' in result:
                task_data = result['result']
                task_id = task_data.get('task_id')
            else:
                # Fallback to old format
                task_id = result.get('task_id')
            
            if not task_id:
                raise Exception(f"VModel API error: {result}")
            
            print(f"[VModel] Task created: {task_id}, polling for result...")
            
            # Poll for completion
            import time
            max_retries = 60  # 60 * 3s = 3 minutes max
            for i in range(max_retries):
                status_response = requests.get(
                    f"https://api.vmodel.ai/api/tasks/v1/{task_id}",
                    headers={"Authorization": f"Bearer {self.vmodel_token}"}
                )
                status_response.raise_for_status()
                status_data = status_response.json()
                
                if status_data.get('status') == 'succeeded':
                    output_url = status_data.get('output', [None])[0]
                    if output_url:
                        print(f"[VModel] ✅ Success! Output: {output_url}")
                        return output_url, "vmodel/video-face-swap-pro"
                    else:
                        raise Exception("VModel returned no output URL")
                
                elif status_data.get('status') in ['failed', 'canceled']:
                    raise Exception(f"VModel task failed: {status_data.get('error', 'Unknown error')}")
                
                # Still processing
                time.sleep(3)
            
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
            # Replicate disabled for video (image swap only)
            raise Exception("Replicate video face swap disabled - all models are image-only. Use VModel instead.")
        
        elif provider == "vmodel":
            # VModel only - premium quality with audio
            print("[VideoSwap] Using VModel.AI")
            result, model = self.swap_face_vmodel(face_image, video_file)
            return result, "vmodel", model
        
        else:  # "auto" or any other value
            # Auto mode: Use VModel (Replicate disabled for video)
            print("[VideoSwap] Auto mode - Using VModel (Replicate disabled for video)")
            
            if self.vmodel_token:
                result, model = self.swap_face_vmodel(face_image, video_file)
                return result, "vmodel", model
            else:
                raise Exception("VMODEL_API_TOKEN required for video face swap (Replicate disabled for video)")
