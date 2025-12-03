# -*- coding: utf-8 -*-
"""
HuggingFace AI Service Integration
Provides Image-to-Video conversion using Stable Video Diffusion
with fallback to local animation
"""

import requests
import os
from typing import Optional
from config import HUGGINGFACE_TOKEN, DEEPAI_API_KEY

class HuggingFaceService:
    """AI service for Image-to-Video conversion using DeepAI"""
    
    def __init__(self):
        self.api_key = HUGGINGFACE_TOKEN
        self.deepai_key = DEEPAI_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://api-inference.huggingface.co/models"
        self.use_fallback = False
        print(f"[AI Service] Initialized with DeepAI key: {self.deepai_key[:20]}...")
    
    def _create_animated_video_fallback(self, image_path: str, output_path: str) -> str:
        """Create animated video using local libraries (fallback method)"""
        try:
            from PIL import Image
            import numpy as np
            import cv2
            
            print("[HuggingFace] Using fallback: Creating animated video with zoom/pan effects")
            
            # Load image
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            # Resize to reasonable dimensions
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            img_array = np.array(img)
            height, width = img_array.shape[:2]
            
            # Video settings
            fps = 30
            duration = 5  # Increased to 5 seconds for smoother animation
            num_frames = fps * duration
            
            # Create video writer with H.264 codec for better browser compatibility
            # Try different codecs in order of preference
            fourcc_options = [
                cv2.VideoWriter_fourcc(*'avc1'),  # H.264 - best for web
                cv2.VideoWriter_fourcc(*'H264'),  # Alternative H.264
                cv2.VideoWriter_fourcc(*'X264'),  # x264 encoder
                cv2.VideoWriter_fourcc(*'mp4v'),  # Fallback
            ]
            
            out = None
            for fourcc in fourcc_options:
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                if out.isOpened():
                    print(f"[HuggingFace] Using codec: {fourcc}")
                    break
                out.release()
            
            if out is None or not out.isOpened():
                raise Exception("Could not initialize video writer with any codec")
            
            print(f"[HuggingFace] Generating {num_frames} frames at {fps} FPS with advanced animations...")
            
            # Enhanced animation: Zoom + Pan + Slight Rotation
            for i in range(num_frames):
                progress = i / num_frames
                
                # Smooth easing function (ease-in-out)
                eased_progress = 0.5 - 0.5 * np.cos(progress * np.pi)
                
                # Dynamic zoom (1.0 to 1.3 with ease)
                zoom = 1.0 + (0.3 * eased_progress)
                
                # Pan effect (move from bottom-right to top-left slightly)
                pan_x = int((width * 0.1) * (1 - eased_progress))
                pan_y = int((height * 0.1) * (1 - eased_progress))
                
                # Calculate crop region for zoom with pan
                crop_w = int(width / zoom)
                crop_h = int(height / zoom)
                
                # Center point with pan offset
                center_x = (width // 2) + pan_x
                center_y = (height // 2) + pan_y
                
                x = max(0, min(width - crop_w, center_x - crop_w // 2))
                y = max(0, min(height - crop_h, center_y - crop_h // 2))
                
                # Crop the image
                cropped = img_array[y:y+crop_h, x:x+crop_w]
                
                # Resize to original dimensions
                frame = cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LANCZOS4)
                
                # Add subtle brightness variation (pulsing effect)
                brightness_factor = 1.0 + (0.05 * np.sin(progress * np.pi * 2))
                frame = np.clip(frame * brightness_factor, 0, 255).astype(np.uint8)
                
                # Optional: Add slight rotation for first/last frames (smooth transition)
                if i < fps * 0.5 or i > num_frames - (fps * 0.5):
                    rotation_angle = 0.5 * np.sin(progress * np.pi * 2)
                    M = cv2.getRotationMatrix2D((width/2, height/2), rotation_angle, 1.0)
                    frame = cv2.warpAffine(frame, M, (width, height), borderMode=cv2.BORDER_REFLECT)
                
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                out.write(frame_bgr)
            
            out.release()
            
            # Verify the file was created and has content
            if not os.path.exists(output_path):
                raise Exception("Video file was not created")
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception("Video file is empty")
            
            print(f"[HuggingFace] ✅ Fallback video created: {output_path} ({file_size} bytes)")
            
            return output_path
            
        except ImportError as e:
            raise Exception(f"Required libraries not installed: {e}. Install with: pip install opencv-python pillow numpy")
        except Exception as e:
            raise Exception(f"Failed to create animated video: {e}")
    
    def image_to_video(self, image_path: str, output_path: str = None, 
                       model: str = "stabilityai/stable-video-diffusion-img2vid-xt") -> str:
        """
        Convert static image to animated video using Stable Video Diffusion
        
        Args:
            image_path: Path to input image
            output_path: Path to save output video (optional)
            model: HuggingFace model to use
            
        Returns:
            Path to generated video file
        """
        print(f"[HuggingFace] Converting image to video: {image_path}")
        print(f"[HuggingFace] Using model: {model}")
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        print(f"[AI Service] Image size: {len(image_bytes)} bytes")
        
        # Generate output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_animated.mp4"
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Try DeepAI API first
        # Note: DeepAI doesn't have a direct image-to-video endpoint
        # We'll use local fallback which creates high-quality zoom animations
        print(f"[AI Service] DeepAI API key configured: {self.deepai_key[:20]}...")
        print(f"[AI Service] Using optimized local video generation (DeepAI has no video endpoint)")
        print(f"[AI Service] Output path: {output_path}")
        return self._create_animated_video_fallback(image_path, output_path)
        
        # DeepAI API attempt (kept for reference if they add video endpoints)
        """
        try:
            print(f"[AI Service] Attempting DeepAI image-to-video conversion...")
            
            with open(image_path, 'rb') as img_file:
                response = requests.post(
                    "https://api.deepai.org/api/video-generator",
                    files={'image': img_file},
                    headers={'api-key': self.deepai_key},
                    timeout=120
                )
            
            print(f"[AI Service] DeepAI Response status: {response.status_code}")
            print(f"[AI Service] DeepAI Response text: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[AI Service] DeepAI response: {result}")
                
                # DeepAI returns a URL to the generated video
                if 'output_url' in result:
                    video_url = result['output_url']
                    print(f"[AI Service] Downloading video from: {video_url}")
                    
                    # Download the video
                    video_response = requests.get(video_url, timeout=60)
                    
                    if video_response.status_code == 200:
                        # Save video
                        if output_path is None:
                            base_name = os.path.splitext(image_path)[0]
                            output_path = f"{base_name}_animated.mp4"
                        
                        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            f.write(video_response.content)
                            f.flush()
                            os.fsync(f.fileno())
                        
                        video_size = os.path.getsize(output_path)
                        print(f"[AI Service] ✅ DeepAI video generated: {output_path} ({video_size} bytes)")
                        return output_path
            
            # If DeepAI fails, use fallback
            print(f"[AI Service] DeepAI failed (status {response.status_code}), using fallback")
            
        except Exception as e:
            print(f"[AI Service] DeepAI error: {e}, using fallback method")
        """
        
        # HuggingFace API code (requires PRO subscription) - kept for reference
        """
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=image_bytes,
                timeout=300  # 5 minutes timeout for video generation
            )
            
            print(f"[HuggingFace] Response status: {response.status_code}")
            print(f"[HuggingFace] Response headers: {dict(response.headers)}")
            
            if response.status_code == 503:
                # Model is loading
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                estimated_time = error_data.get('estimated_time', 20)
                raise Exception(f"Model is currently loading. Please wait {estimated_time} seconds and try again.")
            
            if response.status_code != 200:
                error_msg = f"HF API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', response.text)}"
                except:
                    error_msg += f" - {response.text[:200]}"
                print(f"[HuggingFace] ❌ {error_msg}")
                raise Exception(error_msg)
            
            # Check if response is valid video data
            content_type = response.headers.get('content-type', '')
            if 'video' not in content_type and 'application/octet-stream' not in content_type:
                print(f"[HuggingFace] ⚠️ Unexpected content-type: {content_type}")
                # Try to parse as JSON error
                try:
                    error_data = response.json()
                    raise Exception(f"API returned error: {error_data}")
                except:
                    pass
            
            video_bytes = response.content
            print(f"[HuggingFace] Received {len(video_bytes)} bytes of video data")
            
            # Save video
            if output_path is None:
                base_name = os.path.splitext(image_path)[0]
                output_path = f"{base_name}_animated.mp4"
            
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
                f.flush()
                os.fsync(f.fileno())
            
            # Verify file was written
            if not os.path.exists(output_path):
                raise Exception("Failed to save video file")
            
            video_size = os.path.getsize(output_path)
            print(f"[HuggingFace] ✅ Video generated: {output_path} ({video_size} bytes)")
            
            return output_path
            
        except requests.exceptions.Timeout:
            print("[HuggingFace] ⚠️ API request timed out, using fallback method")
            self.use_fallback = True
            return self._create_animated_video_fallback(image_path, output_path or f"{os.path.splitext(image_path)[0]}_animated.mp4")
        except requests.exceptions.ConnectionError:
            print("[HuggingFace] ⚠️ Connection error, using fallback method")
            self.use_fallback = True
            return self._create_animated_video_fallback(image_path, output_path or f"{os.path.splitext(image_path)[0]}_animated.mp4")
        except Exception as e:
            error_str = str(e)
            if "Model is currently loading" in error_str:
                raise
            # For any other HuggingFace API error, try fallback
            print(f"[HuggingFace] ⚠️ API error ({error_str}), using fallback method")
            self.use_fallback = True
            return self._create_animated_video_fallback(image_path, output_path or f"{os.path.splitext(image_path)[0]}_animated.mp4")
        """
    
    def image_bytes_to_video_bytes(self, image_bytes: bytes, 
                                    model: str = "stabilityai/stable-video-diffusion-img2vid-xt") -> bytes:
        """
        Convert image bytes to video bytes
        
        Args:
            image_bytes: Image data as bytes
            model: HuggingFace model to use
            
        Returns:
            Video data as bytes
        """
        print(f"[HuggingFace] Converting image bytes to video (size: {len(image_bytes)} bytes)")
        
        url = f"{self.base_url}/{model}"
        
        response = requests.post(
            url,
            headers=self.headers,
            data=image_bytes,
            timeout=300
        )
        
        if response.status_code != 200:
            error_msg = f"HF API Error: {response.status_code} - {response.text}"
            print(f"[HuggingFace] ❌ {error_msg}")
            raise Exception(error_msg)
        
        print(f"[HuggingFace] ✅ Video generated ({len(response.content)} bytes)")
        return response.content


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("Testing HuggingFace Image-to-Video Service")
    print("=" * 60)
    
    try:
        hf = HuggingFaceService()
        print("✅ Service initialized successfully!")
        print(f"API Key: {hf.api_key[:20]}...")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
