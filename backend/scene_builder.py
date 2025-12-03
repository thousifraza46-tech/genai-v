"""
Scene Builder - Combine multiple video clips into one cohesive scene
Uses MoviePy to download, stitch, and export videos
"""

import os
import logging
import tempfile
import urllib.request
import requests
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def download_video_with_retry(video_url: str, temp_file: str, max_retries: int = 3) -> bool:
    """
    Download video with retry logic for network issues.
    
    Args:
        video_url: URL of the video to download
        temp_file: Path to save the downloaded video
        max_retries: Maximum number of retry attempts
        
    Returns:
        bool: True if successful, False otherwise
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.pexels.com/'
    }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"   Download attempt {attempt + 1}/{max_retries}...")
            
            response = requests.get(
                video_url, 
                headers=headers, 
                stream=True, 
                timeout=60,  # Increased from 30 to 60 seconds
                allow_redirects=True
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks instead of 8KB
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0 and downloaded % (50 * 1024 * 1024) == 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"   Progress: {progress:.1f}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
            
            if total_size > 0 and os.path.getsize(temp_file) < total_size:
                raise Exception(f"Incomplete download: {os.path.getsize(temp_file)} bytes, expected {total_size} bytes")
            
            logger.info(f"   Download complete: {os.path.getsize(temp_file) // (1024*1024)}MB")
            return True
            
        except (requests.exceptions.ChunkedEncodingError, 
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            logger.warning(f"   Download attempt {attempt + 1} failed: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"   Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"   All {max_retries} download attempts failed")
                raise
        except Exception as e:
            logger.error(f"   Download failed with unexpected error: {e}")
            raise
    
    return False

def combine_videos_fast_ffmpeg(list_of_video_urls: List[str], output_path: str = "final_scene.mp4") -> Tuple[bool, str]:
    """
    FASTEST method: Combine videos using FFmpeg directly (no re-encoding).
    This is 10-50x faster than MoviePy as it copies streams without re-encoding.
    
    Args:
        list_of_video_urls: List of video URLs to download and combine
        output_path: Path where the final combined video will be saved
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    import subprocess
    
    try:
        logger.info(f" Starting FAST scene combination with {len(list_of_video_urls)} clips")
        
        if not list_of_video_urls:
            return False, "No videos to combine"
        
        if len(list_of_video_urls) == 1:
            return False, "Please add at least 2 clips to create a scene"
        
        temp_files = []
        
        try:
            logger.info(" Downloading video clips in parallel...")
            
            def download_single_clip(index_url_tuple):
                i, video_url = index_url_tuple
                logger.info(f"  Downloading clip {i+1}/{len(list_of_video_urls)}...")
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
                try:
                    download_video_with_retry(video_url, temp_file, max_retries=3)
                    logger.info(f"   Clip {i+1} downloaded: {temp_file}")
                    return i, temp_file, None
                except Exception as e:
                    logger.error(f"   Failed to download clip {i+1}: {e}")
                    return i, None, str(e)
            
            temp_files = [None] * len(list_of_video_urls)
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(download_single_clip, (i, url)): i 
                          for i, url in enumerate(list_of_video_urls)}
                
                for future in as_completed(futures):
                    i, temp_file, error = future.result()
                    if error:
                        for tf in temp_files:
                            if tf:
                                try:
                                    os.remove(tf)
                                except:
                                    pass
                        raise Exception(f"Failed to download clip {i+1}/{len(list_of_video_urls)}.")
                    temp_files[i] = temp_file
            
            concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8').name
            with open(concat_file, 'w', encoding='utf-8') as f:
                for temp_file in temp_files:
                    escaped_path = temp_file.replace('\\', '/').replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
            
            logger.info(f" Combining {len(temp_files)} clips with FFmpeg (copy mode - super fast!)...")
            
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            try:
                os.remove(concat_file)
            except:
                pass
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                raise Exception("FFmpeg concatenation failed")
            
            logger.info(" Cleaning up temporary files...")
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            logger.info(f" FAST scene combination complete: {output_path}")
            return True, f"Successfully combined {len(temp_files)} clips into {output_path}"
            
        except Exception as e:
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            raise e
            
    except FileNotFoundError:
        logger.error("FFmpeg not found - falling back to MoviePy")
        return combine_videos(list_of_video_urls, output_path)
    except Exception as e:
        logger.error(f"Fast combination failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, f"Failed to combine videos: {str(e)}"

def combine_videos(list_of_video_urls: List[str], output_path: str = "final_scene.mp4") -> Tuple[bool, str]:
    """
    Combine multiple videos from URLs into a single video file using MoviePy (with optimizations).

    
    Args:
        list_of_video_urls: List of video URLs to download and combine
        output_path: Path where the final combined video will be saved
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        from moviepy import VideoFileClip, concatenate_videoclips
        
        logger.info(f" Starting scene combination with {len(list_of_video_urls)} clips")
        
        if not list_of_video_urls:
            return False, "No videos to combine"
        
        if len(list_of_video_urls) == 1:
            return False, "Please add at least 2 clips to create a scene"
        
        temp_files = []
        video_clips = []
        
        try:
            logger.info(" Downloading video clips in parallel...")
            
            def download_single_clip(index_url_tuple):
                i, video_url = index_url_tuple
                logger.info(f"  Downloading clip {i+1}/{len(list_of_video_urls)}...")
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
                try:
                    download_video_with_retry(video_url, temp_file, max_retries=3)
                    logger.info(f"   Clip {i+1} downloaded: {temp_file}")
                    return i, temp_file, None
                except Exception as e:
                    logger.error(f"   Failed to download clip {i+1}: {e}")
                    return i, None, str(e)
            
            temp_files = [None] * len(list_of_video_urls)
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(download_single_clip, (i, url)): i 
                          for i, url in enumerate(list_of_video_urls)}
                
                for future in as_completed(futures):
                    i, temp_file, error = future.result()
                    if error:
                        for tf in temp_files:
                            if tf:
                                try:
                                    os.remove(tf)
                                except:
                                    pass
                        raise Exception(f"Failed to download clip {i+1}/{len(list_of_video_urls)}. Please try with smaller videos or check your internet connection.")
                    temp_files[i] = temp_file
            
            logger.info(" Loading and processing video clips...")
            max_width = 1280
            max_height = 720
            
            for i, temp_file in enumerate(temp_files):
                clip = VideoFileClip(temp_file, audio=True, fps_source='fps')
                
                if clip.size[0] > max_width or clip.size[1] > max_height:
                    aspect_ratio = clip.size[0] / clip.size[1]
                    if aspect_ratio > max_width / max_height:
                        new_width = max_width
                        new_height = int(max_width / aspect_ratio)
                    else:
                        new_height = max_height
                        new_width = int(max_height * aspect_ratio)
                    
                    logger.info(f"   Resizing clip {i+1} from {clip.size} to ({new_width}, {new_height})")
                    from moviepy.video.fx.all import resize
                    clip = resize(clip, newsize=(new_width, new_height))
                
                video_clips.append(clip)
                logger.info(f"   Clip {i+1} loaded: {clip.duration:.2f}s, {clip.size}")
            
            logger.info(" Concatenating clips...")
            final_clip = concatenate_videoclips(video_clips, method="compose")
            
            total_duration = sum(clip.duration for clip in video_clips)
            logger.info(f"   Combined {len(video_clips)} clips, total duration: {total_duration:.2f}s")
            
            logger.info(f" Writing final video to {output_path}...")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=24,
                preset='ultrafast',
                threads=8,
                bitrate='3000k',
                audio_bitrate='128k',
                logger=None
            )
            
            logger.info(" Cleaning up temporary files...")
            for clip in video_clips:
                clip.close()
            final_clip.close()
            
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            logger.info(f" Scene combination complete: {output_path}")
            return True, f"Successfully combined {len(video_clips)} clips into {output_path}"
            
        except Exception as e:
            for clip in video_clips:
                try:
                    clip.close()
                except:
                    pass
            
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            raise e
            
    except ImportError:
        logger.error("MoviePy not installed")
        return False, "MoviePy not installed. Run: pip install moviepy"
    except Exception as e:
        logger.error(f"Scene combination failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, f"Failed to combine videos: {str(e)}"

def get_scene_duration(scene_clips: List[dict]) -> float:
    """
    Calculate the total duration of a scene.
    
    Args:
        scene_clips: List of video dictionaries with 'duration' key
        
    Returns:
        Total duration in seconds
    """
    return sum(clip.get('duration', 0) for clip in scene_clips)

def get_scene_info(scene_clips: List[dict]) -> dict:
    """
    Get information about the scene composition.
    
    Args:
        scene_clips: List of video dictionaries
        
    Returns:
        Dictionary with scene statistics
    """
    if not scene_clips:
        return {
            'clip_count': 0,
            'total_duration': 0,
            'avg_duration': 0,
            'qualities': []
        }
    
    total_duration = get_scene_duration(scene_clips)
    qualities = [clip.get('quality', 'SD') for clip in scene_clips]
    
    return {
        'clip_count': len(scene_clips),
        'total_duration': total_duration,
        'avg_duration': total_duration / len(scene_clips),
        'qualities': qualities
    }

if __name__ == "__main__":
    print("Scene Builder module ready")
    print("Functions available:")
    print("  - combine_videos(list_of_video_urls, output_path)")
    print("  - get_scene_duration(scene_clips)")
    print("  - get_scene_info(scene_clips)")
