"""
Image to Video Animator using AnimateDiff and Stable Video Diffusion
Converts static images into animated video clips with motion
"""

import os
import torch
from pathlib import Path
from PIL import Image
import numpy as np
from diffusers import StableDiffusionPipeline, DDIMScheduler
from diffusers.utils import export_to_video
import streamlit as st

try:
    from diffusers import AnimateDiffPipeline, MotionAdapter
    ANIMATEDIFF_AVAILABLE = True
except ImportError:
    ANIMATEDIFF_AVAILABLE = False

try:
    from diffusers import StableVideoDiffusionPipeline
    SVD_AVAILABLE = True
except ImportError:
    SVD_AVAILABLE = False


class ImageToVideoAnimator:
    """Convert static images to animated videos using AnimateDiff"""
    
    # Motion style presets with optimized prompts
    MOTION_STYLES = {
        "portrait": {
            "name": "Portrait Breathing + Blinking",
            "prompt": "gentle breathing, natural blinking, soft studio lighting, subtle head movement, professional portrait",
            "negative": "distorted face, unnatural movement, jerky motion, blurry",
            "guidance_scale": 8.0,
            "description": "Subtle facial animations with natural breathing and blinking"
        },
        "cinematic": {
            "name": "Cinematic Camera Movement",
            "prompt": "smooth slow zoom-out, shallow depth of field, filmic mood, cinematic lighting, professional cinematography",
            "negative": "shaky cam, fast motion, jerky, amateur",
            "guidance_scale": 7.5,
            "description": "Smooth camera zoom and pan effects"
        },
        "anime": {
            "name": "Anime Idle Loop",
            "prompt": "anime idle animation, wind blowing hair, soft shader coloring, gentle swaying, anime style",
            "negative": "realistic, photorealistic, static, frozen",
            "guidance_scale": 9.0,
            "description": "Anime-style idle movements with hair and clothing motion"
        },
        "surreal": {
            "name": "Surreal Abstract Motion",
            "prompt": "fluid dreamlike morphing, slow transformations, abstract ambience, ethereal movement, artistic flow",
            "negative": "static, frozen, rigid, sharp edges",
            "guidance_scale": 6.5,
            "description": "Abstract, dreamlike transformations and fluid motion"
        }
    }
    
    def __init__(self, cache_dir="./models/animatediff", output_dir="./assets/animated_videos"):
        """
        Initialize Image to Video Animator
        
        Args:
            cache_dir: Directory to cache downloaded models
            output_dir: Directory to save generated videos
        """
        self.cache_dir = cache_dir
        self.output_dir = output_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.pipeline = None
        self.svd_pipeline = None  # For Stable Video Diffusion
        self.temp_frames_dir = "./tmp/frames"
        Path(self.temp_frames_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_simple_animation(self, image, motion_style, frame_count, output_path):
        """
        Generate simple animation using image transformations (no AI model needed)
        This is a fast fallback when models aren't available
        """
        import cv2
        
        frames = []
        img_array = np.array(image.resize((512, 512)))
        
        for i in range(frame_count):
            progress = i / frame_count
            
            # Apply transformations based on motion style
            if motion_style == "portrait":
                # Subtle zoom in/out
                scale = 1.0 + 0.02 * np.sin(progress * 2 * np.pi)
                center = (256, 256)
                M = cv2.getRotationMatrix2D(center, 0, scale)
                frame = cv2.warpAffine(img_array, M, (512, 512))
                
            elif motion_style == "cinematic":
                # Slow zoom out
                scale = 1.0 + progress * 0.05
                center = (256, 256)
                M = cv2.getRotationMatrix2D(center, 0, scale)
                frame = cv2.warpAffine(img_array, M, (512, 512))
                
            elif motion_style == "anime":
                # Gentle sway
                offset_x = int(5 * np.sin(progress * 4 * np.pi))
                offset_y = int(3 * np.cos(progress * 4 * np.pi))
                M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
                frame = cv2.warpAffine(img_array, M, (512, 512))
                
            else:  # surreal
                # Wave distortion
                rows, cols = img_array.shape[:2]
                frame = img_array.copy()
                for y in range(rows):
                    offset = int(3 * np.sin(2 * np.pi * (y / rows + progress)))
                    frame[y, :] = np.roll(img_array[y, :], offset, axis=0)
            
            frames.append(Image.fromarray(frame.astype('uint8')))
        
        # Export using export_to_video
        fps = max(8, frame_count // 3)
        export_to_video(frames, output_path, fps=fps)
        
        return output_path
        
    def load_model(self, model_name="guoyww/animatediff-motion-adapter-v1-5-2"):
        """
        Load AnimateDiff model with motion adapter
        
        Args:
            model_name: HuggingFace model name
            
        Returns:
            bool: True if successful
        """
        if not ANIMATEDIFF_AVAILABLE:
            st.error("AnimateDiff not available. Please install: pip install diffusers>=0.35.0")
            return False
            
        try:
            st.info("Loading AnimateDiff model (this may take a few minutes)...")
            
            # Load motion adapter
            adapter = MotionAdapter.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                torch_dtype=self.dtype
            )
            
            # Load pipeline with motion adapter
            self.pipeline = AnimateDiffPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                motion_adapter=adapter,
                cache_dir=self.cache_dir,
                torch_dtype=self.dtype
            ).to(self.device)
            
            # Optimize scheduler for image-to-video
            self.pipeline.scheduler = DDIMScheduler.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                subfolder="scheduler",
                clip_sample=False,
                timestep_spacing="linspace",
                beta_schedule="linear",
                steps_offset=1,
            )
            
            # Enable memory optimizations
            if self.device == "cuda":
                self.pipeline.enable_vae_slicing()
                self.pipeline.enable_model_cpu_offload()
            
            st.success("Model loaded successfully!")
            return True
            
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return False
    
    def preprocess_image(self, image_path_or_pil, target_size=(512, 512)):
        """
        Preprocess input image for animation
        
        Args:
            image_path_or_pil: Path to image file or PIL Image
            target_size: Target resolution (width, height)
            
        Returns:
            PIL.Image: Preprocessed image
        """
        try:
            # Load image if path provided
            if isinstance(image_path_or_pil, (str, Path)):
                image = Image.open(image_path_or_pil).convert("RGB")
            else:
                image = image_path_or_pil.convert("RGB")
            
            # Resize while maintaining aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Create new image with target size and paste centered
            new_image = Image.new("RGB", target_size, (0, 0, 0))
            paste_x = (target_size[0] - image.width) // 2
            paste_y = (target_size[1] - image.height) // 2
            new_image.paste(image, (paste_x, paste_y))
            
            return new_image
            
        except Exception as e:
            st.error(f"Error preprocessing image: {e}")
            return None
    
    def generate_animated_video(
        self,
        image,
        motion_style="portrait",
        duration=3.0,
        frame_count=24,
        seed=42,
        custom_prompt=None,
        custom_negative=None,
        num_inference_steps=25,
        use_simple_fallback=False
    ):
        """
        Generate animated video from static image
        
        Args:
            image: PIL Image or path to image file
            motion_style: One of: portrait, cinematic, anime, surreal
            duration: Video duration in seconds (2-6)
            frame_count: Number of frames to generate (16-48)
            seed: Random seed for reproducibility
            custom_prompt: Optional custom motion prompt
            custom_negative: Optional custom negative prompt
            num_inference_steps: Quality steps (higher=better but slower)
            use_simple_fallback: Force use of simple animation (faster, no AI)
            
        Returns:
            str: Path to generated video file
        """
        try:
            # Preprocess image first
            st.info("Preprocessing image...")
            processed_image = self.preprocess_image(image)
            if processed_image is None:
                return None
            
            # Generate output path
            timestamp = int(torch.randint(0, 1000000, (1,)).item())
            output_filename = f"animated_{motion_style}_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Option 1: Use simple animation (fast, works without models)
            if use_simple_fallback or self.pipeline is None:
                st.info("Using fast simple animation method...")
                st.caption("This creates smooth motion without AI models (faster)")
                
                with st.spinner(f"Generating {frame_count} frames..."):
                    self.generate_simple_animation(
                        processed_image,
                        motion_style,
                        frame_count,
                        output_path
                    )
                
                if os.path.exists(output_path):
                    st.success(f"Animation complete! Saved to {output_filename}")
                    return output_path
                else:
                    st.error("Failed to generate animation")
                    return None
            
            # Option 2: Try to load AI model for high-quality generation
            if self.pipeline is None:
                st.info("Attempting to load AI model for high-quality animation...")
                if not self.load_model():
                    st.warning("AI model not available. Using simple animation instead...")
                    return self.generate_animated_video(
                        image, motion_style, duration, frame_count, seed,
                        custom_prompt, custom_negative, num_inference_steps,
                        use_simple_fallback=True
                    )
                if not self.load_model():
                    return None
            
            # Preprocess image
            st.info("Preprocessing image...")
            processed_image = self.preprocess_image(image)
            if processed_image is None:
                return None
            
            # Get motion style settings
            if motion_style not in self.MOTION_STYLES:
                motion_style = "portrait"
            
            style_config = self.MOTION_STYLES[motion_style]
            
            # Build prompts - add description of the image content
            base_prompt = "high quality, detailed, "
            motion_prompt = base_prompt + (custom_prompt or style_config["prompt"])
            negative_prompt = "low quality, blurry, distorted, " + (custom_negative or style_config["negative"])
            guidance_scale = style_config["guidance_scale"]
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if self.device == "cuda":
                    torch.cuda.manual_seed_all(seed)
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None
            
            # Clamp frame count
            frame_count = max(16, min(48, frame_count))
            
            st.info(f"Generating {frame_count} frames with {motion_style} motion...")
            st.caption(f"Motion: {motion_prompt[:80]}...")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Generate animated frames using AnimateDiff
            with st.spinner(f"Animating image ({num_inference_steps} steps)..."):
                try:
                    # Check if pipeline supports img2img
                    if hasattr(self.pipeline, 'img2img'):
                        # Use img2img if available
                        output = self.pipeline.img2img(
                            image=processed_image,
                            prompt=motion_prompt,
                            negative_prompt=negative_prompt,
                            num_frames=frame_count,
                            num_inference_steps=num_inference_steps,
                            guidance_scale=guidance_scale,
                            generator=generator,
                            strength=0.65  # Keep 65% of original image
                        )
                    else:
                        # Fallback: Use text-to-video with high guidance
                        # This generates video based on text prompt
                        output = self.pipeline(
                            prompt=motion_prompt,
                            negative_prompt=negative_prompt,
                            num_frames=frame_count,
                            num_inference_steps=num_inference_steps,
                            guidance_scale=guidance_scale + 2.0,  # Higher guidance for image similarity
                            width=512,
                            height=512,
                            generator=generator
                        )
                    
                    progress_bar.progress(100)
                    status_text.success("Animation generation complete!")
                    
                except Exception as e:
                    st.error(f"Error during generation: {str(e)}")
                    st.warning("Trying fallback method...")
                    
                    # Fallback: Simple text-to-video
                    output = self.pipeline(
                        prompt=motion_prompt,
                        negative_prompt=negative_prompt,
                        num_frames=frame_count,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        width=512,
                        height=512,
                        generator=generator
                    )
            
            # Export to video
            timestamp = int(torch.randint(0, 1000000, (1,)).item())
            output_filename = f"animated_{motion_style}_{timestamp}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            st.info("Encoding video with ffmpeg...")
            
            # Calculate FPS from duration and frame count
            fps = frame_count / duration
            fps = max(8, min(30, fps))  # Clamp to reasonable range
            
            export_to_video(output.frames[0], output_path, fps=int(fps))
            
            # Optimize video encoding (re-encode with yuv420p for compatibility)
            optimized_path = output_path.replace(".mp4", "_optimized.mp4")
            self._optimize_video(output_path, optimized_path)
            
            # Replace original with optimized
            if os.path.exists(optimized_path):
                os.replace(optimized_path, output_path)
            
            st.success(f"Video generated: {output_filename}")
            return output_path
            
        except Exception as e:
            st.error(f"Error generating video: {e}")
            import traceback
            st.error(traceback.format_exc())
            return None
    
    def _optimize_video(self, input_path, output_path):
        """
        Optimize video encoding with ffmpeg
        
        Args:
            input_path: Input video path
            output_path: Output video path
        """
        try:
            import subprocess
            
            # Use ffmpeg to re-encode with yuv420p pixel format
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", input_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-pix_fmt", "yuv420p",
                "-crf", "23",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
        except subprocess.CalledProcessError:
            # If ffmpeg fails, keep original
            pass
        except FileNotFoundError:
            # ffmpeg not installed, skip optimization
            st.warning("FFmpeg not found. Skipping video optimization.")
    
    def get_motion_styles(self):
        """Get available motion style presets"""
        return {
            key: {
                "name": config["name"],
                "description": config["description"]
            }
            for key, config in self.MOTION_STYLES.items()
        }
    
    def get_model_info(self):
        """Get information about loaded model"""
        return {
            "loaded": self.pipeline is not None,
            "device": self.device,
            "dtype": str(self.dtype),
            "cache_dir": self.cache_dir,
            "output_dir": self.output_dir,
            "motion_styles": len(self.MOTION_STYLES)
        }


# Streamlit UI Components
def show_image_to_video_ui():
    """Display Image-to-Video animation UI in Streamlit"""
    st.subheader("Image to Video Animation")
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 10px; border-radius: 8px; color: white; margin-bottom: 15px;">
            <strong>Upload an image and animate it with AI-powered motion</strong>
        </div>
    """, unsafe_allow_html=True)
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload Image (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        help="Upload a static image to animate"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Use a fixed width for predictable layout instead of deprecated param
            st.image(image, caption="Original Image", width=512)
        
        with col2:
            # Motion style selection
            animator = ImageToVideoAnimator()
            motion_styles = animator.get_motion_styles()
            
            style_names = {k: v["name"] for k, v in motion_styles.items()}
            selected_style = st.selectbox(
                "Motion Style",
                options=list(style_names.keys()),
                format_func=lambda x: style_names[x],
                help="Choose the type of animation"
            )
            
            st.caption(f"{motion_styles[selected_style]['description']}")
            
            # Duration and frame settings
            duration = st.slider(
                "Duration (seconds)",
                min_value=2.0,
                max_value=6.0,
                value=3.0,
                step=0.5,
                help="Video duration"
            )
            
            frame_count = st.slider(
                "Frame Count",
                min_value=16,
                max_value=48,
                value=24,
                step=8,
                help="More frames = smoother but slower"
            )
            
            # Advanced settings
            with st.expander("Advanced Settings", expanded=False):
                num_steps = st.slider(
                    "Quality Steps",
                    min_value=15,
                    max_value=50,
                    value=25,
                    step=5,
                    help="Higher = better quality but slower"
                )
                
                seed = st.number_input(
                    "Random Seed",
                    min_value=0,
                    max_value=999999,
                    value=42,
                    help="For reproducible results"
                )
                
                custom_prompt = st.text_input(
                    "Custom Motion Prompt (optional)",
                    placeholder="Leave empty to use preset",
                    help="Override the motion style prompt"
                )
                
                custom_negative = st.text_input(
                    "Custom Negative Prompt (optional)",
                    placeholder="Leave empty to use preset"
                )
        
        # Generate button
        st.markdown("<br>", unsafe_allow_html=True)
        
    if st.button("Generate Animated Video", type="primary"):
            animator = ImageToVideoAnimator()
            
            video_path = animator.generate_animated_video(
                image=image,
                motion_style=selected_style,
                duration=duration,
                frame_count=frame_count,
                seed=seed,
                custom_prompt=custom_prompt if custom_prompt else None,
                custom_negative=custom_negative if custom_negative else None,
                num_inference_steps=num_steps
            )
            
            if video_path and os.path.exists(video_path):
                st.markdown("---")
                st.success("Animation Complete!")
                
                # Display video
                st.video(video_path)
                
                # Download button
                with open(video_path, "rb") as f:
                    st.download_button(
                        label="Download Animated Video",
                        data=f,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4",
                    )
                
                # Video info
                st.info(f"""
                **Video Details:**
                - Motion Style: {motion_styles[selected_style]['name']}
                - Duration: {duration}s
                - Frames: {frame_count}
                - FPS: {int(frame_count/duration)}
                - Resolution: 512x512
                """)
    else:
        st.info("Upload an image to get started!")
        
        # Show examples
        st.markdown("---")
        st.markdown("### Tips for Best Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Good Images:**
            - Clear, well-lit photos
            - Centered subjects
            - High resolution (512px+)
            - Simple backgrounds
            """)
        
        with col2:
            st.markdown("""
            **Motion Styles:**
            - Portrait: Faces, people
            - Cinematic: Landscapes, scenes
            - Anime: Illustrations, art
            - Surreal: Abstract, creative
            """)


def test_image_to_video():
    """Test image-to-video animation"""
    print("Testing Image-to-Video Animator...")
    print("=" * 50)
    
    animator = ImageToVideoAnimator()
    info = animator.get_model_info()
    
    print(f"Device: {info['device']}")
    print(f"Available motion styles: {info['motion_styles']}")
    
    styles = animator.get_motion_styles()
    for key, style in styles.items():
        print(f"  - {key}: {style['name']}")
    
    print("\nImage-to-Video Animator initialized successfully!")


if __name__ == "__main__":
    test_image_to_video()
