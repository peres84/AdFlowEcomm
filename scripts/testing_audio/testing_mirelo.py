"""
Mirelo.ai Audio Generation Testing Script

✅ TESTING CONFIGURATION:
- Service: Mirelo.ai (AI-powered sound effects generation)
- Input: Video file (MP4)
- Output: Audio file with generated sound effects
- Model: v1.5 (default)

This script demonstrates the complete workflow:
1. Create customer asset (get upload URL)
2. Upload video file to Mirelo
3. Generate sound effects from video
4. Download generated audio
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# ---------------------------------------
# 🔧 CONFIGURATION
# ---------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
ENV_PATH = os.path.join(ROOT_DIR, ".env")

load_dotenv(ENV_PATH)

MIRELO_API_URL = "https://api.mirelo.ai"
API_KEY = os.getenv("MIRELO_API_KEY")

# Input video (from Runware generation)
VIDEO_PATH = os.path.join(SCRIPT_DIR, "results/d5d8763b-7c73-4d54-b9ca-23dbc50c8bf6.mp4")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")

# Audio generation parameters
TEXT_PROMPT = "Cinematic background music with smooth transitions, professional product showcase atmosphere"
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


def main():
    """Main workflow for Mirelo audio generation."""
    
    print("🎵 Mirelo.ai Audio Generation Test")
    print("=" * 60)
    
    # Validate API key
    if not API_KEY:
        print("❌ Missing MIRELO_API_KEY in .env file.")
        return
    
    # Validate video file
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video not found at {VIDEO_PATH}")
        print(f"   Please ensure you have a generated video from Runware first.")
        return
    
    ensure_results_folder()
    
    try:
        # Step 1: Create customer asset
        customer_asset_id, upload_url = create_customer_asset(API_KEY)
        
        # Step 2: Upload video
        upload_video(upload_url, VIDEO_PATH)
        
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
        
        for i, audio_url in enumerate(audio_urls, 1):
            # Create filename based on customer asset ID
            filename = f"audio_{customer_asset_id}_sample{i}.mp3"
            save_path = os.path.join(RESULTS_DIR, filename)
            
            print(f"\n   Audio {i}/{len(audio_urls)}:")
            success = download_audio(audio_url, save_path)
            
            if success:
                print(f"   ✅ Saved: {filename}")
        
        print(f"\n{'=' * 60}")
        print(f"✅ AUDIO GENERATION COMPLETE!")
        print(f"   Original video: {os.path.basename(VIDEO_PATH)}")
        print(f"   Generated audio files: {len(audio_urls)}")
        print(f"   Location: {RESULTS_DIR}")
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
