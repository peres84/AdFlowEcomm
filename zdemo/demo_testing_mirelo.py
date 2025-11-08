"""
Mirelo.ai Audio Generation Testing Script

✅ TESTING CONFIGURATION:
- Service: Mirelo.ai (AI-powered sound effects generation)
- Input: First video found in vid_test/ folder
- Output: Audio file + Video with audio merged
- Model: v1.5 (default)

This script demonstrates the complete workflow:
1. Find first video in vid_test/ folder
2. Create customer asset (get upload URL)
3. Upload video file to Mirelo
4. Generate sound effects from video
5. Download generated audio to results/
6. Merge video + audio → Save to results/

File Organization:
- vid_test/          → Input videos (original files stay here)
- results/           → Generated audio + final videos with audio
"""

import requests
import json
import os
import time
import subprocess
from dotenv import load_dotenv

# ---------------------------------------
# 🔧 CONFIGURATION
# ---------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # scripts/testing_audio/
SCRIPTS_DIR = os.path.dirname(SCRIPT_DIR)  # scripts/
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)  # project root
ENV_PATH = os.path.join(ROOT_DIR, ".env")

load_dotenv(ENV_PATH)

MIRELO_API_URL = "https://api.mirelo.ai"
API_KEY = os.getenv("MIRELO_API_KEY")

# Input video folder and results folder
VID_TEST_DIR = os.path.join(SCRIPT_DIR, "vid_test")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")

# Video path will be determined dynamically from vid_test folder
VIDEO_PATH = None

# Audio generation parameters
TEXT_PROMPT = "Christmas music and laughs that synchronize with the video itself"
MODEL_VERSION = "1.5"  # v1.5 is the latest
NUM_SAMPLES = 1  # Number of audio variations to generate
DURATION = 10  # Duration in seconds (max 10)
CREATIVITY_COEF = 5  # Creativity coefficient (1-10)
# ---------------------------------------


def ensure_results_folder():
    """Ensure results directory exists."""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"📁 Created folder: {RESULTS_DIR}")
    else:
        print(f"📁 Using existing folder: {RESULTS_DIR}")


def find_first_video():
    """
    Find the first video file in vid_test directory.
    
    Returns:
        str: Path to first video file found, or None if no videos
    """
    if not os.path.exists(VID_TEST_DIR):
        print(f"❌ vid_test directory not found: {VID_TEST_DIR}")
        return None
    
    # Supported video extensions
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    
    # Get all files in vid_test directory
    files = os.listdir(VID_TEST_DIR)
    
    # Find first video file
    for file in sorted(files):  # Sort for consistent behavior
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_path = os.path.join(VID_TEST_DIR, file)
            print(f"📹 Found video: {file}")
            return video_path
    
    print(f"❌ No video files found in {VID_TEST_DIR}")
    print(f"   Supported formats: {', '.join(video_extensions)}")
    return None


def create_customer_asset(api_key):
    """
    Step 1: Create a customer asset and get upload URL.
    
    Returns:
        tuple: (customer_asset_id, upload_url)
    """
    print("📤 Step 1: Creating customer asset...")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # Mirelo uses x-api-key header
    }
    
    payload = {
        "contentType": "video/mp4"
    }
    
    response = requests.post(
        f"{MIRELO_API_URL}/create-customer-asset",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"❌ Failed to create customer asset: {response.status_code}, {response.text}")
    
    data = response.json()
    customer_asset_id = data.get("customer_asset_id")
    upload_url = data.get("upload_url")
    
    if not customer_asset_id or not upload_url:
        raise Exception(f"⚠️ Unexpected response: {data}")
    
    print(f"✅ Customer asset created")
    print(f"   Asset ID: {customer_asset_id}")
    print(f"   Upload URL: {upload_url[:50]}...")
    
    return customer_asset_id, upload_url


def upload_video(upload_url, video_path):
    """
    Step 2: Upload video file to the pre-signed URL.
    
    Args:
        upload_url: Pre-signed URL from create_customer_asset
        video_path: Path to local video file
    """
    print(f"\n📤 Step 2: Uploading video...")
    print(f"   File: {video_path}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    # Get file size for progress
    file_size = os.path.getsize(video_path)
    print(f"   Size: {file_size / (1024*1024):.2f} MB")
    
    # Upload using PUT request (as specified in docs)
    with open(video_path, "rb") as f:
        video_data = f.read()
    
    headers = {
        "Content-Type": "video/mp4"
    }
    
    response = requests.put(
        upload_url,
        data=video_data,
        headers=headers
    )
    
    if response.status_code not in [200, 204]:
        raise Exception(f"❌ Upload failed: {response.status_code}, {response.text}")
    
    print(f"✅ Video uploaded successfully")


def generate_sfx(api_key, customer_asset_id, text_prompt, model_version, num_samples, duration, creativity_coef):
    """
    Step 3: Generate sound effects from the uploaded video.
    
    Args:
        api_key: Mirelo API key
        customer_asset_id: ID from create_customer_asset
        text_prompt: Text description for audio generation
        model_version: Model version ("1.0" or "1.5")
        num_samples: Number of audio variations (1-4)
        duration: Duration in seconds (1-10)
        creativity_coef: Creativity coefficient (1-10)
    
    Returns:
        list: URLs to generated audio files
    """
    print(f"\n🎵 Step 3: Generating sound effects...")
    print(f"   Model: v{model_version}")
    print(f"   Prompt: {text_prompt}")
    print(f"   Duration: {duration}s")
    print(f"   Samples: {num_samples}")
    print(f"   Creativity: {creativity_coef}/10")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key  # Mirelo uses x-api-key header
    }
    
    payload = {
        "customer_asset_id": customer_asset_id,
        "text_prompt": text_prompt,
        "model_version": model_version,
        "num_samples": num_samples,
        "duration": duration,
        "creativity_coef": creativity_coef,
        "return_audio_only": False  # Return audio with video context
    }
    
    response = requests.post(
        f"{MIRELO_API_URL}/video-to-sfx",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 201:
        raise Exception(f"❌ SFX generation failed: {response.status_code}, {response.text}")
    
    data = response.json()
    output_paths = data.get("output_paths", [])
    
    if not output_paths:
        raise Exception(f"⚠️ No audio files generated: {data}")
    
    print(f"✅ Sound effects generated!")
    print(f"   Generated {len(output_paths)} audio file(s)")
    
    return output_paths


def download_audio(url, save_path):
    """
    Step 4: Download generated audio file.
    
    Args:
        url: Audio file URL
        save_path: Local path to save audio
    """
    print(f"\n⬇️  Downloading audio...")
    print(f"   URL: {url[:50]}...")
    
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Audio saved at: {save_path}")
        return True
    else:
        print(f"❌ Failed to download audio: {response.status_code}")
        return False


def merge_video_audio(video_path, audio_path, output_path):
    """
    Step 5: Merge video and audio using FFmpeg.
    
    Args:
        video_path: Path to video file
        audio_path: Path to audio file (may contain video+audio from Mirelo)
        output_path: Path for output video with audio
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n🎬 Step 5: Merging video and audio...")
    print(f"   Video: {os.path.basename(video_path)}")
    print(f"   Audio: {os.path.basename(audio_path)}")
    
    try:
        # FFmpeg command to merge video and audio
        # Note: Mirelo returns MP4 with video+audio, we extract audio stream
        cmd = [
            "ffmpeg",
            "-i", video_path,      # Input video (original)
            "-i", audio_path,      # Input audio (from Mirelo, may have video too)
            "-c:v", "copy",        # Copy video codec (no re-encoding)
            "-c:a", "aac",         # Convert audio to AAC
            "-strict", "-2",       # Allow experimental AAC encoder (for older FFmpeg)
            "-map", "0:v:0",       # Map video from first input
            "-map", "1:a:0",       # Map audio from second input (audio stream only)
            "-shortest",           # End when shortest stream ends
            "-y",                  # Overwrite output file
            output_path
        ]
        
        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Video and audio merged successfully!")
        print(f"   Output: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr}")
        print(f"\n💡 Trying alternative method...")
        
        # Try alternative: use libmp3lame or copy audio codec
        try:
            cmd_alt = [
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "copy",    # Try copying audio codec instead
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd_alt, capture_output=True, text=True, check=True)
            print(f"✅ Video and audio merged successfully (alternative method)!")
            print(f"   Output: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e2:
            print(f"❌ Alternative method also failed: {e2.stderr}")
            return False
        
    except FileNotFoundError:
        print(f"❌ FFmpeg not found. Please install FFmpeg:")
        print(f"   Windows: choco install ffmpeg")
        print(f"   Mac: brew install ffmpeg")
        print(f"   Linux: apt-get install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Merge failed: {str(e)}")
        return False


def main():
    """Main workflow for Mirelo audio generation."""
    
    print("🎵 Mirelo.ai Audio Generation Test")
    print("=" * 60)
    
    # Validate API key
    if not API_KEY:
        print("❌ Missing MIRELO_API_KEY in .env file.")
        return
    
    # Find first video in vid_test directory
    print(f"\n📂 Looking for videos in: {VID_TEST_DIR}")
    video_path = find_first_video()
    
    if not video_path:
        print(f"\n❌ No video found!")
        print(f"   Please add a video file to: {VID_TEST_DIR}")
        return
    
    # Ensure results folder exists
    ensure_results_folder()
    
    try:
        # Step 1: Create customer asset
        customer_asset_id, upload_url = create_customer_asset(API_KEY)
        
        # Step 2: Upload video
        upload_video(upload_url, video_path)
        
        # Step 3: Generate sound effects
        audio_urls = generate_sfx(
            API_KEY,
            customer_asset_id,
            TEXT_PROMPT,
            MODEL_VERSION,
            NUM_SAMPLES,
            DURATION,
            CREATIVITY_COEF
        )
        
        # Step 4: Download generated audio files
        print(f"\n📥 Downloading {len(audio_urls)} audio file(s)...")
        
        audio_files = []
        for i, audio_url in enumerate(audio_urls, 1):
            # Create filename based on customer asset ID
            filename = f"audio_{customer_asset_id}_sample{i}.mp3"
            save_path = os.path.join(RESULTS_DIR, filename)
            
            print(f"\n   Audio {i}/{len(audio_urls)}:")
            success = download_audio(audio_url, save_path)
            
            if success:
                print(f"   ✅ Saved: {filename}")
                audio_files.append(save_path)
        
        # Step 5: Merge video and audio
        if audio_files:
            print(f"\n{'=' * 60}")
            print(f"🎬 Creating final video with audio...")
            
            # Use first audio file for merging
            audio_path = audio_files[0]
            
            # Create output filename
            video_basename = os.path.splitext(os.path.basename(video_path))[0]
            output_filename = f"{video_basename}_with_audio.mp4"
            output_path = os.path.join(RESULTS_DIR, output_filename)
            
            # Merge video and audio
            merge_success = merge_video_audio(video_path, audio_path, output_path)
            
            if merge_success:
                print(f"\n{'=' * 60}")
                print(f"✅ COMPLETE WORKFLOW FINISHED!")
                print(f"\n📁 File Organization:")
                print(f"   Original video (unchanged): {VID_TEST_DIR}/{os.path.basename(video_path)}")
                print(f"   Generated audio: {RESULTS_DIR}/{os.path.basename(audio_path)}")
                print(f"   Final video with audio: {RESULTS_DIR}/{output_filename}")
                print(f"\n📊 Summary:")
                print(f"   Input: {os.path.basename(video_path)}")
                print(f"   Audio samples generated: {len(audio_files)}")
                print(f"   Output: {output_filename}")
                print(f"{'=' * 60}")
            else:
                print(f"\n{'=' * 60}")
                print(f"⚠️  Audio generated but merge failed")
                print(f"   You can manually merge using FFmpeg")
                print(f"   Video: {video_path}")
                print(f"   Audio: {audio_path}")
                print(f"{'=' * 60}")
        else:
            print(f"\n{'=' * 60}")
            print(f"⚠️  No audio files downloaded")
            print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
