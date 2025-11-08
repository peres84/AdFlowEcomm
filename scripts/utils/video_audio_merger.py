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
from typing import Optional, Dict, List


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


def concatenate_videos(
    video_paths: List[str],
    output_path: str,
    temp_dir: Optional[str] = None,
    overwrite: bool = True,
    verbose: bool = False
) -> bool:
    """
    Concatenate multiple videos into a single video using FFmpeg concat demuxer.
    
    This is a lossless operation that preserves quality without re-encoding.
    
    Args:
        video_paths: List of video file paths in order
        output_path: Path for final concatenated video
        temp_dir: Directory for temporary concat file (default: same as output)
        overwrite: Overwrite output file if exists
        verbose: Print FFmpeg output
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not video_paths:
        raise ValueError("video_paths cannot be empty")
    
    for video_path in video_paths:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
    
    if temp_dir is None:
        temp_dir = os.path.dirname(output_path) or "."
    
    # Create concat file
    import uuid
    concat_file = os.path.join(temp_dir, f"concat_list_{uuid.uuid4().hex[:8]}.txt")
    
    try:
        with open(concat_file, "w") as f:
            for video_path in video_paths:
                abs_path = os.path.abspath(video_path)
                escaped_path = abs_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",  # No re-encoding (lossless)
            "-y" if overwrite else "-n",
            output_path
        ]
        
        if verbose:
            print(f"Concatenating {len(video_paths)} videos...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if verbose and result.stdout:
            print(f"FFmpeg output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg concatenation error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Mac: brew install ffmpeg")
        print("  Linux: apt-get install ffmpeg")
        return False
    except Exception as e:
        print(f"Concatenation failed: {str(e)}")
        return False
    finally:
        if os.path.exists(concat_file):
            try:
                os.unlink(concat_file)
            except:
                pass


def concatenate_videos_with_transitions(
    video_paths: List[str],
    output_path: str,
    transition_duration: float = 0.3,
    temp_dir: Optional[str] = None,
    overwrite: bool = True,
    verbose: bool = False
) -> bool:
    """
    Concatenate multiple videos with crossfade transitions between them.
    
    Uses FFmpeg's xfade filter for video crossfades (frames blend into each other)
    and acrossfade filter for audio crossfades (smooth audio transitions).
    
    Args:
        video_paths: List of video file paths in order
        output_path: Path for final concatenated video
        transition_duration: Duration of crossfade transition in seconds (default: 0.3)
        temp_dir: Directory for temporary files (default: same as output)
        overwrite: Overwrite output file if exists
        verbose: Print FFmpeg output
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not video_paths:
        raise ValueError("video_paths cannot be empty")
    
    if len(video_paths) < 2:
        if verbose:
            print("Only one video provided, copying without transitions")
        try:
            import shutil
            shutil.copy2(video_paths[0], output_path)
            return True
        except Exception as e:
            print(f"Failed to copy video: {str(e)}")
            return False
    
    for video_path in video_paths:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
    
    if temp_dir is None:
        temp_dir = os.path.dirname(output_path) or "."
    
    try:
        num_videos = len(video_paths)
        
        # Get video durations
        video_durations = []
        for i, video_path in enumerate(video_paths):
            info = get_video_info(video_path)
            if info and "format" in info and "duration" in info["format"]:
                duration = float(info["format"]["duration"])
                video_durations.append(duration)
            else:
                if verbose:
                    print(f"⚠️  Could not get duration for {os.path.basename(video_path)}, assuming 10s")
                video_durations.append(10.0)
        
        # Build input list
        inputs = []
        for video_path in video_paths:
            abs_path = os.path.abspath(video_path)
            inputs.extend(["-i", abs_path])
        
        # Build filter complex for crossfades
        filter_parts = []
        
        # Prepare each video stream (normalize, scale, format)
        for i in range(num_videos):
            filter_parts.append(
                f"[{i}:v]setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p[v{i}]"
            )
            filter_parts.append(
                f"[{i}:a]asetpts=PTS-STARTPTS[a{i}]"
            )
        
        # Chain crossfades for video and audio
        if num_videos == 1:
            final_video = "[v0]"
            final_audio = "[a0]"
        else:
            # First transition
            offset = video_durations[0] - transition_duration
            filter_parts.append(
                f"[v0][v1]xfade=transition=fade:duration={transition_duration}:offset={offset}[vx1]"
            )
            filter_parts.append(
                f"[a0][a1]acrossfade=d={transition_duration}[ax1]"
            )
            
            # Chain remaining transitions
            cumulative = video_durations[0] + video_durations[1] - 2 * transition_duration
            for i in range(2, num_videos):
                offset = cumulative - transition_duration
                filter_parts.append(
                    f"[vx{i-1}][v{i}]xfade=transition=fade:duration={transition_duration}:offset={offset}[vx{i}]"
                )
                filter_parts.append(
                    f"[ax{i-1}][a{i}]acrossfade=d={transition_duration}[ax{i}]"
                )
                cumulative += video_durations[i] - transition_duration
            
            final_video = f"[vx{num_videos-1}]"
            final_audio = f"[ax{num_videos-1}]"
        
        filter_complex = ";".join(filter_parts)
        
        cmd = [
            "ffmpeg",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", final_video,
            "-map", final_audio,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "medium",
            "-crf", "23",
            "-y" if overwrite else "-n",
            output_path
        ]
        
        if verbose:
            print(f"Applying crossfade transitions (duration: {transition_duration}s)...")
            print(f"Processing {num_videos} videos with frame blending...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if verbose:
            if result.stdout:
                print(f"FFmpeg output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg transition error: {e.stderr}")
        if verbose:
            print(f"Command: {' '.join(cmd)}")
        if verbose:
            print("⚠️  Crossfade failed, trying simple concatenation...")
        return concatenate_videos(video_paths, output_path, temp_dir, overwrite, verbose)
    
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Mac: brew install ffmpeg")
        print("  Linux: apt-get install ffmpeg")
        return False
    
    except Exception as e:
        print(f"Transition concatenation failed: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        if verbose:
            print("⚠️  Falling back to simple concatenation...")
        return concatenate_videos(video_paths, output_path, temp_dir, overwrite, verbose)
