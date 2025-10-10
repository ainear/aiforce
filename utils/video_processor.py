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
        self.hf_timeout = 7  # 7 seconds timeout cho mỗi HF model
        
        # Hugging Face Pro models (order by priority)
        self.hf_models = [
            {
                "name": "tonyassi/vfs2-cpu",
                "params": ["input_image", "input_video", "gender"],
                "video_format": "dict"
            },
            {
                "name": "MarkoVidrih/video-face-swap",
                "params": ["face", "video"],
                "video_format": "file"
            }
        ]
        
        # Replicate Pro models (WORKING 2025) - WITH VERSION HASH
        self.replicate_models = [
            "arabyai-replicate/roop_face_swap:11b6bf0f4e14d808f655e87e5448233cceff10a45f659d71539cafb7163b2e84",
        ]
    
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
            
            # Prepare arguments based on model config
            if "input_image" in params and "input_video" in params:
                # tonyassi/vfs2-cpu format
                if video_format == "dict":
                    job = client.submit(
                        input_image=handle_file(face_image_path),
                        input_video={"video": handle_file(video_path)},
                        device='cpu',
                        selector='many',
                        gender=gender if gender != "all" else None,
                        race=None,
                        order=None,
                        api_name="/predict"
                    )
                    result = job.result()
                    # Extract video path from result
                    if isinstance(result, dict) and "video" in result:
                        result = result["video"]
                    elif isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], dict) and "video" in result[0]:
                            result = result[0]["video"]
                else:
                    result = client.predict(
                        handle_file(face_image_path),
                        handle_file(video_path),
                        api_name="/predict"
                    )
            elif "face" in params and "video" in params:
                # MarkoVidrih format (2 params only)
                result = client.predict(
                    handle_file(face_image_path),
                    handle_file(video_path),
                    api_name="/predict"
                )
            else:
                # Default fallback
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
        
        # Save face image to temp file
        face_path = self._save_temp_file(face_image.stream if hasattr(face_image, 'stream') else face_image, '.jpg')
        video_path = self._save_temp_file(video_file.stream if hasattr(video_file, 'stream') else video_file, '.mp4')
        
        # Open files for Replicate
        with open(face_path, 'rb') as f1, open(video_path, 'rb') as f2:
            # Try models in order
            for model_name in self.replicate_models:
                try:
                    print(f"[Replicate] Trying model: {model_name}")
                    
                    output = replicate.run(
                        model_name,
                        input={
                            "swap_image": f1,      # Face to swap
                            "target_video": f2     # Video to swap into
                        }
                    )
                    
                    # Download result
                    if isinstance(output, str):
                        video_url = output
                    elif isinstance(output, list) and len(output) > 0:
                        video_url = output[0]
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
    
    def swap_face_video(self, face_image, video_file, provider="auto", gender="all"):
        """
        Main video face swap method
        
        Args:
            face_image: Face image file
            video_file: Video file
            provider: "huggingface", "replicate", or "auto" (try HF first, fallback to Replicate)
            gender: "all", "male", "female" (for HF models)
        
        Returns:
            (video_path/url, provider_used, model_used)
        """
        print(f"[VideoSwap] Starting with provider: {provider}")
        
        if provider == "huggingface":
            # HuggingFace only
            result, model = self.swap_face_huggingface(face_image, video_file, gender)
            return result, "huggingface", model
        
        elif provider == "replicate":
            # Replicate only
            result, model = self.swap_face_replicate(face_image, video_file)
            return result, "replicate", model
        
        else:  # "auto"
            # Try HuggingFace first, fallback to Replicate
            try:
                result, model = self.swap_face_huggingface(face_image, video_file, gender)
                return result, "huggingface", model
            except Exception as hf_error:
                print(f"[VideoSwap] HF failed: {hf_error}, trying Replicate...")
                
                try:
                    result, model = self.swap_face_replicate(face_image, video_file)
                    return result, "replicate", model
                except Exception as rep_error:
                    raise Exception(f"Both providers failed. HF: {hf_error}, Replicate: {rep_error}")
