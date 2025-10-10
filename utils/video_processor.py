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
        
        # Replicate Pro models (WORKING 2025) - AUDIO PRESERVED ✅
        # arabyai-replicate/roop_face_swap: $0.14/run, ~77s, VIDEO face swap with AUDIO
        # Must use full version ID to avoid 404
        self.replicate_models = [
            "arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84"
        ]
        
        # VModel.AI credentials
        self.vmodel_token = os.getenv('VMODEL_API_TOKEN', '')
        
        # HuggingFace Spaces for video face swap (FREE alternatives)
        self.hf_spaces = {
            'hf-tonyassi': 'tonyassi/video-face-swap',
            'hf-marko': 'MarkoVidrih/video-face-swap',
            'hf-alsv': 'ALSv/video-face-swap',
            'hf-prithiv': 'prithivMLmods/Video-Face-Swapper',
        }
    
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
                # Note: arabyai-replicate/roop_face_swap params are swap_image + target_video
                with open(face_path, 'rb') as f1, open(video_path, 'rb') as f2:
                    output = replicate.run(
                        model_name,
                        input={
                            "swap_image": f1,      # Face to swap (source face)
                            "target_video": f2     # Video to swap into (target video)
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
            
            # Small delay before first check (let API index the task)
            time.sleep(2)
            
            max_retries = 60  # 60 * 3s = 3 minutes max
            for i in range(max_retries):
                try:
                    status_response = requests.get(
                        f"https://api.vmodel.ai/api/tasks/v1/get/{task_id}",
                        headers={"Authorization": f"Bearer {self.vmodel_token}"}
                    )
                    
                    # Log response for debugging
                    print(f"[VModel] Status check #{i+1}: HTTP {status_response.status_code}")
                    
                    status_response.raise_for_status()
                    status_data = status_response.json()
                    
                    # VModel may return nested response like create endpoint
                    if 'result' in status_data and isinstance(status_data['result'], dict):
                        # Nested format: {'code': 200, 'result': {...}}
                        task_status = status_data['result']
                    else:
                        # Direct format
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
                    
                    # Still processing
                    time.sleep(3)
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        print(f"[VModel] Task not found yet (404), retrying... ({i+1}/{max_retries})")
                        time.sleep(5)  # Longer delay on 404
                        continue
                    raise
            
            raise Exception("VModel processing timeout (3 minutes)")
            
        except Exception as e:
            print(f"[VModel] Error: {e}")
            raise
    
    def swap_face_huggingface(self, face_image, video_file, space_name, gender="all"):
        """
        Swap face using HuggingFace Spaces (Gradio API)
        FREE alternative providers
        
        Args:
            face_image: Face image file
            video_file: Video file
            space_name: HuggingFace space name (e.g., "tonyassi/video-face-swap")
            gender: "all", "male", "female" (some spaces support this)
        
        Returns:
            (video_url, space_name)
        """
        print(f"[HF Space] Using {space_name}")
        
        try:
            from gradio_client import Client, handle_file
            
            # Save files to temp paths
            face_path = self._save_temp_file(face_image, suffix='.jpg')
            video_path = self._save_temp_file(video_file, suffix='.mp4')
            
            try:
                # Create Gradio client
                client = Client(space_name)
                print(f"[HF Space] Connected to {space_name}")
                
                # Different spaces have different APIs
                # Try common patterns
                try:
                    # Pattern 1: tonyassi/video-face-swap (image, video, gender)
                    if 'tonyassi' in space_name:
                        print(f"[HF Space] Calling with gender parameter: {gender}")
                        result = client.predict(
                            source_image=handle_file(face_path),
                            target_video=handle_file(video_path),
                            gender=gender,
                            api_name="/predict"
                        )
                    else:
                        # Pattern 2: Most other spaces (image, video only)
                        print(f"[HF Space] Calling without gender parameter")
                        result = client.predict(
                            handle_file(face_path),
                            handle_file(video_path),
                            api_name="/predict"
                        )
                    
                    print(f"[HF Space] Result type: {type(result)}")
                    print(f"[HF Space] Result: {result}")
                    
                    # Result can be a string (URL or file path) or tuple
                    if isinstance(result, tuple):
                        video_result = result[0]
                    else:
                        video_result = result
                    
                    # Check if it's a URL or file path
                    if isinstance(video_result, str):
                        if video_result.startswith('http'):
                            # It's a URL
                            return video_result, space_name
                        else:
                            # It's a file path, need to read and potentially upload
                            # For now, return the path (caller can handle upload)
                            return video_result, space_name
                    else:
                        raise Exception(f"Unexpected result type: {type(video_result)}")
                
                except Exception as api_error:
                    print(f"[HF Space] API error: {api_error}")
                    # Try without api_name parameter
                    print(f"[HF Space] Retrying without api_name...")
                    result = client.predict(
                        handle_file(face_path),
                        handle_file(video_path)
                    )
                    
                    if isinstance(result, tuple):
                        video_result = result[0]
                    else:
                        video_result = result
                    
                    if isinstance(video_result, str):
                        return video_result, space_name
                    else:
                        raise Exception(f"Unexpected result type: {type(video_result)}")
            
            finally:
                # Cleanup temp files
                try:
                    os.unlink(face_path)
                    os.unlink(video_path)
                except:
                    pass
        
        except Exception as e:
            print(f"[HF Space] Error: {e}")
            raise Exception(f"HuggingFace Space {space_name} failed: {e}")
    
    def swap_face_video(self, face_image, video_file, provider="auto", gender="all"):
        """
        Main video face swap method with multiple providers
        
        Args:
            face_image: Face image file
            video_file: Video file
            provider: "auto", "replicate", "vmodel", "hf-tonyassi", "hf-marko", "hf-alsv", "hf-prithiv"
            gender: "all", "male", "female" (supported by some providers)
        
        Returns:
            (video_url, provider_used, model_used)
        """
        print(f"[VideoSwap] Starting with provider: {provider}")
        
        # Check if it's a HuggingFace Space provider
        if provider in self.hf_spaces:
            space_name = self.hf_spaces[provider]
            print(f"[VideoSwap] Using HuggingFace Space: {provider} ({space_name})")
            result, model = self.swap_face_huggingface(face_image, video_file, space_name, gender)
            return result, provider, model
        
        elif provider == "replicate":
            # Replicate only - arabyai-replicate/roop_face_swap with audio
            print("[VideoSwap] Using Replicate (arabyai-replicate/roop_face_swap)")
            result, model = self.swap_face_replicate(face_image, video_file)
            return result, "replicate", model
        
        elif provider == "vmodel":
            # VModel only - premium quality with audio
            print("[VideoSwap] Using VModel.AI")
            result, model = self.swap_face_vmodel(face_image, video_file)
            return result, "vmodel", model
        
        else:  # "auto" or any other value
            # Auto mode: Replicate primary → VModel fallback → HF fallback
            print("[VideoSwap] Auto mode - Replicate → VModel → HF fallback chain")
            
            errors = []
            
            # Try 1: Replicate first (stable, audio preserved, $0.14)
            try:
                result, model = self.swap_face_replicate(face_image, video_file)
                return result, "replicate", model
            except Exception as replicate_error:
                print(f"[VideoSwap] Replicate failed: {replicate_error}")
                errors.append(f"Replicate: {replicate_error}")
            
            # Try 2: VModel fallback (premium, faster, $0.10)
            if self.vmodel_token:
                try:
                    print("[VideoSwap] Falling back to VModel...")
                    result, model = self.swap_face_vmodel(face_image, video_file)
                    return result, "vmodel (fallback)", model
                except Exception as vmodel_error:
                    print(f"[VideoSwap] VModel fallback failed: {vmodel_error}")
                    errors.append(f"VModel: {vmodel_error}")
            else:
                print("[VideoSwap] VModel not configured, skipping")
                errors.append("VModel: Not configured")
            
            # Try 3: HuggingFace Spaces fallback (FREE, slower)
            print("[VideoSwap] Trying HuggingFace Spaces as last resort...")
            for hf_provider, space_name in self.hf_spaces.items():
                try:
                    print(f"[VideoSwap] Trying {hf_provider} ({space_name})...")
                    result, model = self.swap_face_huggingface(face_image, video_file, space_name, gender)
                    return result, f"{hf_provider} (fallback)", model
                except Exception as hf_error:
                    print(f"[VideoSwap] {hf_provider} failed: {hf_error}")
                    errors.append(f"{hf_provider}: {hf_error}")
            
            # All providers failed
            error_summary = "\n".join(errors)
            raise Exception(f"All providers failed:\n{error_summary}")
