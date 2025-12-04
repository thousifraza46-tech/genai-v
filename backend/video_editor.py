"""
Video Editor Module - Handles video editing operations using MoviePy
"""
import os
import tempfile
from typing import List, Dict, Any
from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    AudioFileClip,
)
from moviepy.video.fx.all import (
    resize,
    speedx,
    fadein,
    fadeout,
    crop,
    rotate,
    mirror_x,
    mirror_y,
)
import requests
from pathlib import Path


class VideoEditor:
    """Handles video editing operations"""

    def __init__(self, output_dir: str = "assets/edited_videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download_video(self, url: str, output_path: str) -> str:
        """Download video from URL"""
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    def apply_clip_edits(
        self, clip: VideoFileClip, settings: Dict[str, Any]
    ) -> VideoFileClip:
        """Apply all editing operations to a single clip"""

        # Trim
        trim_start = settings.get("trimStart", 0)
        trim_end = settings.get("trimEnd", clip.duration)
        clip = clip.subclip(trim_start, min(trim_end, clip.duration))

        # Speed
        speed = settings.get("speed", 1.0)
        if speed != 1.0:
            clip = clip.fx(speedx, speed)

        # Volume
        volume = settings.get("volume", 100) / 100.0
        if clip.audio and volume != 1.0:
            clip = clip.volumex(volume)

        # Fade in/out
        fade_in = settings.get("fadeIn", 0)
        fade_out = settings.get("fadeOut", 0)
        if fade_in > 0:
            clip = clip.fx(fadein, fade_in)
        if fade_out > 0:
            clip = clip.fx(fadeout, fade_out)

        # Brightness and Contrast
        brightness = settings.get("brightness", 100) / 100.0
        contrast = settings.get("contrast", 100) / 100.0
        if brightness != 1.0 or contrast != 1.0:
            # Apply brightness and contrast adjustments
            clip = clip.fl_image(
                lambda image: self._adjust_brightness_contrast(
                    image, brightness, contrast
                )
            )

        # Rotation
        rotation = settings.get("rotation", 0)
        if rotation != 0:
            clip = clip.fx(rotate, rotation)

        # Flip
        flip_h = settings.get("flipH", False)
        flip_v = settings.get("flipV", False)
        if flip_h:
            clip = clip.fx(mirror_x)
        if flip_v:
            clip = clip.fx(mirror_y)

        return clip

    def _adjust_brightness_contrast(
        self, image, brightness: float, contrast: float
    ):
        """Adjust brightness and contrast of an image"""
        import numpy as np

        # Brightness adjustment
        image = image * brightness

        # Contrast adjustment
        if contrast != 1.0:
            mean = image.mean()
            image = (image - mean) * contrast + mean

        # Clip values to valid range
        image = np.clip(image, 0, 255)
        return image.astype("uint8")

    def export_video(self, clips_data: List[Dict[str, Any]]) -> str:
        """
        Export final video from multiple clips

        Args:
            clips_data: List of clip configurations with URL and editing settings

        Returns:
            Path to the exported video file
        """
        temp_dir = tempfile.mkdtemp()
        downloaded_clips = []
        edited_clips = []

        try:
            # Download and process each clip
            for idx, clip_data in enumerate(clips_data):
                # Get video URL/path
                video_url = clip_data.get("url")
                
                # Check if it's a local file path or URL
                if video_url.startswith('/assets/'):
                    # Local file - convert URL to path
                    video_path = video_url.replace('/assets/', 'assets/')
                    if not os.path.exists(video_path):
                        raise Exception(f"Video file not found: {video_path}")
                    temp_video_path = video_path
                elif video_url.startswith('http'):
                    # Remote URL - download it
                    temp_video_path = os.path.join(temp_dir, f"clip_{idx}.mp4")
                    print(f"[Editor] Downloading clip {idx+1}...")
                    self.download_video(video_url, temp_video_path)
                    downloaded_clips.append(temp_video_path)
                else:
                    # Assume it's a local path
                    temp_video_path = video_url
                    if not os.path.exists(temp_video_path):
                        raise Exception(f"Video file not found: {temp_video_path}")

                print(f"[Editor] Processing clip {idx+1}/{len(clips_data)}: {os.path.basename(temp_video_path)}")
                
                # Load clip
                clip = VideoFileClip(temp_video_path)

                # Apply edits
                edited_clip = self.apply_clip_edits(clip, clip_data)
                edited_clips.append(edited_clip)

            # Concatenate all clips
            if len(edited_clips) == 1:
                final_clip = edited_clips[0]
            else:
                final_clip = concatenate_videoclips(edited_clips, method="compose")

            # Export final video
            import time
            output_filename = f"edited_video_{int(time.time())}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)

            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=os.path.join(temp_dir, "temp-audio.m4a"),
                remove_temp=True,
                fps=24,
            )

            # Clean up
            for clip in edited_clips:
                clip.close()

            return output_path

        except Exception as e:
            # Clean up on error
            for clip in edited_clips:
                try:
                    clip.close()
                except:
                    pass
            raise Exception(f"Video export failed: {str(e)}")

        finally:
            # Clean up temporary files
            for temp_file in downloaded_clips:
                try:
                    os.remove(temp_file)
                except:
                    pass
            try:
                os.rmdir(temp_dir)
            except:
                pass


# Initialize editor instance
editor = VideoEditor()
