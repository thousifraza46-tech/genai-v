"""
AnimateDiff Video Generator
Generates AI videos using AnimateDiff diffusion models
"""

import os
import torch
from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
from diffusers.utils import export_to_video
import streamlit as st
from pathlib import Path

class AnimateDiffGenerator:
    """Generate videos using AnimateDiff models"""
    
    def __init__(self, cache_dir="./models/animatediff"):
        """
        Initialize AnimateDiff generator
        
        Args:
            cache_dir: Directory to cache downloaded models
        """
        self.cache_dir = cache_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = None
        
    def load_model(self, model_name="guoyww/animatediff-motion-adapter-v1-5-2"):
        """
        Load AnimateDiff model
        
        Args:
            model_name: HuggingFace model name
            
        Returns:
            bool: True if successful
        """
        try:
            # Load motion adapter
            adapter = MotionAdapter.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # Load pipeline with motion adapter
            self.pipeline = AnimateDiffPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                motion_adapter=adapter,
                cache_dir=self.cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            
            # Set scheduler
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
            
            return True
            
        except Exception as e:
            st.error(f"Error loading AnimateDiff model: {e}")
            return False
    
    def generate_video(
        self,
        prompt,
        negative_prompt="low quality, blurry, distorted, watermark",
        num_frames=16,
        num_inference_steps=25,
        guidance_scale=7.5,
        seed=None,
        width=512,
        height=512
    ):
        """
        Generate video from text prompt
        
        Args:
            prompt: Text description of the video
            negative_prompt: What to avoid in the video
            num_frames: Number of frames (default 16)
            num_inference_steps: Quality vs speed (default 25)
            guidance_scale: How closely to follow prompt (default 7.5)
            seed: Random seed for reproducibility
            width: Video width (default 512)
            height: Video height (default 512)
            
        Returns:
            str: Path to generated video file
        """
        try:
            if self.pipeline is None:
                if not self.load_model():
                    return None
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
            
            # Generate video frames
            output = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_frames=num_frames,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            )
            
            # Export to video file
            output_path = f"./assets/animatediff_{hash(prompt)}.mp4"
            export_to_video(output.frames[0], output_path, fps=8)
            
            return output_path
            
        except Exception as e:
            st.error(f"Error generating AnimateDiff video: {e}")
            return None
    
    def generate_multiple_videos(
        self,
        prompts,
        **kwargs
    ):
        """
        Generate multiple videos from a list of prompts
        
        Args:
            prompts: List of text prompts
            **kwargs: Additional arguments for generate_video
            
        Returns:
            list: Paths to generated video files
        """
        videos = []
        
        for i, prompt in enumerate(prompts):
            st.info(f"Generating AnimateDiff video {i+1}/{len(prompts)}...")
            video_path = self.generate_video(prompt, **kwargs)
            
            if video_path:
                videos.append(video_path)
            
        return videos
    
    def get_model_info(self):
        """Get information about loaded model"""
        if self.pipeline is None:
            return {
                "loaded": False,
                "device": self.device,
                "cache_dir": self.cache_dir
            }
        
        return {
            "loaded": True,
            "device": self.device,
            "cache_dir": self.cache_dir,
            "dtype": str(self.pipeline.unet.dtype),
            "model": "AnimateDiff v1.5"
        }


# Streamlit UI Components
def show_animatediff_settings():
    """Display AnimateDiff generation settings in Streamlit"""
    st.subheader("AnimateDiff Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_frames = st.slider(
            "Number of Frames",
            min_value=8,
            max_value=32,
            value=16,
            step=8,
            help="More frames = longer video but slower generation"
        )
        
        num_inference_steps = st.slider(
            "Quality Steps",
            min_value=10,
            max_value=50,
            value=25,
            step=5,
            help="More steps = better quality but slower"
        )
        
        guidance_scale = st.slider(
            "Prompt Guidance",
            min_value=1.0,
            max_value=15.0,
            value=7.5,
            step=0.5,
            help="Higher = follows prompt more closely"
        )
    
    with col2:
        width = st.selectbox(
            "Video Width",
            options=[256, 384, 512, 640],
            index=2,
            help="Resolution width"
        )
        
        height = st.selectbox(
            "Video Height",
            options=[256, 384, 512, 640],
            index=2,
            help="Resolution height"
        )
        
        seed = st.number_input(
            "Random Seed (optional)",
            min_value=0,
            max_value=999999,
            value=42,
            help="Set seed for reproducible results"
        )
    
    negative_prompt = st.text_area(
        "Negative Prompt (what to avoid)",
        value="low quality, blurry, distorted, watermark, text, logo",
        help="Describe what you don't want in the video"
    )
    
    return {
        "num_frames": num_frames,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "width": width,
        "height": height,
        "seed": seed,
        "negative_prompt": negative_prompt
    }


def test_animatediff():
    """Test AnimateDiff generation"""
    print("Testing AnimateDiff Generator...")
    
    generator = AnimateDiffGenerator()
    
    # Check device
    print(f"Device: {generator.device}")
    
    # Test video generation
    test_prompt = "A cat playing with a ball of yarn, smooth motion, high quality"
    print(f"\nGenerating test video: {test_prompt}")
    
    video_path = generator.generate_video(
        prompt=test_prompt,
        num_frames=16,
        num_inference_steps=20,
        seed=42
    )
    
    if video_path:
        print(f"Video generated: {video_path}")
    else:
        print("Video generation failed")
    
    # Show model info
    info = generator.get_model_info()
    print(f"\nModel Info: {info}")


if __name__ == "__main__":
    test_animatediff()
