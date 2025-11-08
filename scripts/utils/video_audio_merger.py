"""
Video-Audio Merger Utility

Professional utility for merging video and audio files using FFmpeg.
Commonly used to add AI-generated audio to videos.

Typical use case:
    1. Generate video (e.g., with Runware)
    2. Generate audio for video (e.g., with Mirelo)
    3. Merge them into final video with audio

Example:
    from scripts.utils.video_audio_merger import merge_video_audio
    
    success = merge_video_audio(
        video_path="video.mp4",
        audio_path="audio.mp3",
        output_path="final_video.mp4"
    )
"""

import subprocess
import os
from typing import Optional, Dict


def merge_video_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    video_codec: str = "copy",
    audio_codec: str = "aac",
    audio_bitrate: str = "192k",
    overwrite: bool = True,
    verbose: bool = False
) -> bool:
    """
    Merge video and audio files using FFmpeg.
    
    This function combines a video file with an audio file, creating a new
    video with the audio track. The video is not re-encoded by default (copy),
    which makes the process fast and lossless.
    
    Args:
        video_path: Path to input video file
        audio_path: Path to input audio file (MP3, WAV, AAC, etc.)
        output_path: Path for output video file
        video_codec: Video codec ("copy" for no re-encoding, or "libx264", etc.)
        audio_codec: Audio codec ("aac", "mp3", "copy", etc.)
        audio_bitrate: Audio bitrate (e.g., "192k", "256k")
        overwrite: Overwrite output file if exists
        verbose: Print FFmpeg output
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        FileNotFoundError: If video or audio file doesn't exist
        
    Example:
        >>> # Basic merge (fast, no re-encoding)
        >>> merge_video_audio("video.mp4", "audio.mp3", "output.mp4")
        
        >>> # With custom audio quality
        >>> merge_video_audio(
        ...     "video.mp4",
        ...     "audio.mp3",
        ...     "output.mp4",
        ...     audio_bitrate="256k"
        ... )
        
        >>> # Re-encode video (slower but ensures compatibility)
        >>> merge_video_audio(
        ...     "video.mp4",
        ...     "audio.mp3",
        ...     "output.mp4",
        ...     video_codec="libx264"
        ... )
    """
    # Validation
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")
    
    try:
        # Build FFmpeg command
        cmd = ["ffmpeg"]
        
        # Input files
        cmd.extend(["-i", video_path])  # Video input
        cmd.extend(["-i", audio_path])  # Audio input
        
        # Video codec
        cmd.extend(["-c:v", video_codec])
        
        # Audio codec and bitrate
        cmd.extend(["-c:a", audio_codec])
        if audio_codec == "aac":
            cmd.extend(["-strict", "-2"])  # For older FFmpeg versions
        if audio_codec != "copy":
            cmd.extend(["-b:a", audio_bitrate])
        
        # Map streams (video from first input, audio from second)
        cmd.extend(["-map", "0:v:0"])  # Video from input 0
        cmd.extend(["-map", "1:a:0"])  # Audio from input 1
        
        # End when shortest stream ends (in case of duration mismatch)
        cmd.extend(["-shortest"])
        
        # Overwrite output
        if overwrite:
            cmd.append("-y")
        
        # Output file
        cmd.append(output_path)
        
        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if verbose:
            print(f"FFmpeg output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False
        
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Mac: brew install ffmpeg")
        print("  Linux: apt-get install ffmpeg")
        return False
        
    except Exception as e:
        print(f"Merge failed: {str(e)}")
        return False


def replace_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    overwrite: bool = True
) -> bool:
    """
    Replace the audio track in a video file.
    
    This removes any existing audio and replaces it with the new audio.
    
    Args:
        video_path: Path to input video file
        audio_path: Path to new audio file
        output_path: Path for output video file
        overwrite: Overwrite output file if exists
        
    Returns:
        bool: True if successful, False otherwise
    """
    return merge_video_audio(
        video_path,
        audio_path,
        output_path,
        video_codec="copy",
        audio_codec="aac",
        overwrite=overwrite
    )


def add_background_music(
    video_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 0.3,
    overwrite: bool = True
) -> bool:
    """
    Add background music to a video while preserving original audio.
    
    This mixes the original video audio with background music at specified volumes.
    
    Args:
        video_path: Path to input video file
        music_path: Path to background music file
        output_path: Path for output video file
        music_volume: Volume of background music (0.0 to 1.0)
        overwrite: Overwrite output file if exists
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> # Add quiet background music (30% volume)
        >>> add_background_music("video.mp4", "music.mp3", "output.mp4", music_volume=0.3)
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    if not os.path.exists(music_path):
        raise FileNotFoundError(f"Music not found: {music_path}")
    
    try:
        # FFmpeg command to mix audio
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            f"[0:a]volume=1.0[a1];[1:a]volume={music_volume}[a2];[a1][a2]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest"
        ]
        
        if overwrite:
            cmd.append("-y")
        
        cmd.append(output_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Failed to add background music: {str(e)}")
        return False


def get_video_info(video_path: str) -> Optional[Dict]:
    """
    Get video metadata using FFprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dict with video info (duration, width, height, etc.) or None if failed
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        return json.loads(result.stdout)
        
    except Exception as e:
        print(f"Failed to get video info: {str(e)}")
        return None


def extract_audio(
    video_path: str,
    output_path: str,
    audio_format: str = "mp3",
    audio_bitrate: str = "192k"
) -> bool:
    """
    Extract audio from a video file.
    
    Args:
        video_path: Path to input video file
        output_path: Path for output audio file
        audio_format: Audio format (mp3, wav, aac, etc.)
        audio_bitrate: Audio bitrate (e.g., "192k", "256k")
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", audio_format if audio_format != "mp3" else "libmp3lame",
            "-b:a", audio_bitrate,
            "-y",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Failed to extract audio: {str(e)}")
        return False


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed and accessible.
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# Convenience function for quick merging
def quick_merge(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Quick merge with default settings (no re-encoding, AAC audio).
    
    Args:
        video_path: Path to video file
        audio_path: Path to audio file
        output_path: Path for output file
        
    Returns:
        bool: True if successful
    """
    return merge_video_audio(video_path, audio_path, output_path)
