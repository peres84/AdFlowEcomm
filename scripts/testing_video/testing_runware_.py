"""
Runware Video Generation Testing Script

✅ VERIFIED WORKING CONFIGURATION:
- Model: minimax:1@1 (MiniMax 01 Base)
- Duration: 6 seconds
- Dimensions: 1366x768
- Generation Time: ~244 seconds (4 minutes)
- Output: https://vm.runware.ai/video/ws/5/vi/b0d6f39f-1571-4353-aadf-d7a37cba4bc1.mp4

This script demonstrates the complete workflow:
1. Upload image to Runware
2. Submit video generation request
3. Poll for completion using getResponse
4. Download final video
"""

import requests
import uuid
import json
import os
import time
import base64
from dotenv import load_dotenv
from PIL import Image

# ---------------------------------------
# 🔧 CONFIGURATION
# ---------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
ENV_PATH = os.path.join(ROOT_DIR, ".env")

load_dotenv(ENV_PATH)

RUNWARE_API_URL = "https://api.runware.ai/v1"
API_KEY = os.getenv("RUNWARE_API_KEY")

SCRIPT = "A video of a pepsi soda can that a person grabs and starts drinking in his house with cinematic lighting with Christmas decoration, studio background and a strong snowfall."
IMG_PATH = os.path.join(SCRIPT_DIR, "imgs_test/pep_can.jpeg")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")

POLL_INTERVAL = 5  # seconds between polls

# ✅ VERIFIED WORKING MODEL CONFIGURATION (MiniMax 01 Base)
# Successfully tested: ~244s generation time for 6s video
MODEL = "minimax:1@1"
MODEL_WIDTH = 1366
MODEL_HEIGHT = 768
MODEL_DURATION = 6
# ---------------------------------------


def ensure_results_folder():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"📁 Created folder: {RESULTS_DIR}")
    else:
        print(f"📁 Using existing folder: {RESULTS_DIR}")


def prepare_image(image_path, target_width=MODEL_WIDTH, target_height=MODEL_HEIGHT):
    """Resize the image to the required width and height for the model."""
    img = Image.open(image_path)
    img_resized = img.resize((target_width, target_height), Image.LANCZOS)
    temp_path = os.path.join(os.path.dirname(image_path), "resized_image.jpeg")
    img_resized.save(temp_path, format="JPEG")
    print(f"🖼️ Image resized to {target_width}x{target_height} at {temp_path}")
    return temp_path


def upload_image(api_key, image_path):
    """Uploads an image to Runware and returns its imageUUID."""
    print(f"📤 Uploading image: {image_path}")
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = [
        {
            "taskType": "imageUpload",
            "taskUUID": str(uuid.uuid4()),
            "image": image_b64
        }
    ]

    response = requests.post(RUNWARE_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"❌ Image upload failed: {response.status_code}, {response.text}")

    data = response.json()
    data_list = data.get("results") or data.get("data") or []
    if not data_list or "imageUUID" not in data_list[0]:
        raise Exception(f"⚠️ Unexpected upload response: {data}")

    image_id = data_list[0]["imageUUID"]
    print(f"✅ Image uploaded successfully. UUID: {image_id}")
    return image_id


def generate_video(api_key, prompt, image_id, duration=MODEL_DURATION, width=MODEL_WIDTH, height=MODEL_HEIGHT):
    """Send an image-to-video generation request using frameImages."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    task_uuid = str(uuid.uuid4())

    payload = [
        {
            "taskType": "videoInference",
            "taskUUID": task_uuid,
            "model": MODEL,  # ✅ Verified working: minimax:1@1
            "positivePrompt": prompt,
            "duration": duration,
            "width": width,
            "height": height,
            "outputType": "URL",
            "outputFormat": "MP4",
            "deliveryMethod": "async",
            "frameImages": [
                {"inputImage": image_id, "frame": "first"}
            ],
            "numberResults": 1
        }
    ]

    print("🎬 Sending video generation request...")
    response = requests.post(RUNWARE_API_URL, headers=headers, json=payload)

    # If failure due to invalid frame width/height, resize and retry
    if response.status_code == 400 and "invalidFrameImageWidth" in response.text:
        print("⚠️ Frame image width invalid. Resizing and retrying...")
        resized_path = prepare_image(IMG_PATH)
        image_id = upload_image(api_key, resized_path)
        payload[0]["frameImages"][0]["inputImage"] = image_id
        response = requests.post(RUNWARE_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"❌ Video request failed: {response.status_code}, {response.text}")

    data = response.json()
    
    # Verify acknowledgment
    if "data" not in data or not data["data"]:
        raise Exception(f"⚠️ Unexpected response structure: {json.dumps(data, indent=2)}")
    
    task_data = data["data"][0]
    returned_uuid = task_data.get("taskUUID")
    returned_type = task_data.get("taskType")
    
    if returned_uuid != task_uuid:
        raise Exception(f"⚠️ Task UUID mismatch! Sent: {task_uuid}, Received: {returned_uuid}")
    
    if returned_type != "videoInference":
        raise Exception(f"⚠️ Unexpected task type: {returned_type}")
    
    print("✅ Video generation request ACKNOWLEDGED by Runware API")
    print(f"   Task Type: {returned_type}")
    print(f"   Task UUID: {returned_uuid}")
    
    return task_uuid, data

def check_task_status(api_key, task_uuid):
    """
    Poll for task results using the getResponse task type.
    
    Returns a dict with:
    - status: "processing", "success", or "error"
    - data: The task data if available
    - error: Error info if failed
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = [
        {
            "taskType": "getResponse",
            "taskUUID": task_uuid
        }
    ]
    
    response = requests.post(RUNWARE_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"❌ Status check failed: {response.status_code}, {response.text}")
    
    result = response.json()
    
    # Check for errors array first
    if "errors" in result and result["errors"]:
        for error in result["errors"]:
            if error.get("taskUUID") == task_uuid:
                return {
                    "status": "error",
                    "error": error
                }
    
    # Check data array for our task
    if "data" in result and result["data"]:
        for item in result["data"]:
            if item.get("taskUUID") == task_uuid:
                return item
    
    # No matching task found
    return {
        "status": "unknown",
        "message": "Task not found in response",
        "full_response": result
    }


def download_video(url, save_path):
    print(f"⬇️  Downloading video to {save_path} ...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Video saved at: {save_path}")
    else:
        print(f"❌ Failed to download video: {response.status_code}")


def main():
    if not API_KEY:
        print("❌ Missing RW_API_KEY in .env file.")
        return

    if not os.path.exists(IMG_PATH):
        print(f"❌ Image not found at {IMG_PATH}")
        return

    ensure_results_folder()

    # Upload image and get UUID
    image_id = upload_image(API_KEY, IMG_PATH)

    # Generate video with automatic resizing if needed
    task_uuid, _ = generate_video(API_KEY, SCRIPT, image_id)
    check_num = 1
    print(f"\n🕒 Polling for video completion (checking every {POLL_INTERVAL}s)...")

    while True:
        time.sleep(POLL_INTERVAL)  # Wait before first check
        
        status_data = check_task_status(API_KEY, task_uuid)
        status = status_data.get("status")
        
        print(f"   → Poll #{check_num}: {status}")
        
        if status == "success":
            video_url = status_data.get("videoURL")
            video_uuid = status_data.get("videoUUID")
            cost = status_data.get("cost")
            seed = status_data.get("seed")
            
            print(f"\n✅ Video generation COMPLETED!")
            print(f"   Video UUID: {video_uuid}")
            if seed:
                print(f"   Seed: {seed}")
            if cost:
                print(f"   Cost: ${cost:.4f}")
            
            if video_url:
                save_path = os.path.join(RESULTS_DIR, f"{task_uuid}.mp4")
                download_video(video_url, save_path)
            else:
                print("⚠️ Task completed but no video URL found.")
                print(f"Full response: {json.dumps(status_data, indent=2)}")
            break
            
        elif status == "processing":
            # Still processing, continue polling
            check_num += 1
            continue
            
        elif status == "error":
            print(f"\n❌ Video generation FAILED")
            error_info = status_data.get("error", {})
            print(f"   Error Code: {error_info.get('code', 'unknown')}")
            print(f"   Message: {error_info.get('message', 'No message provided')}")
            if error_info.get("documentation"):
                print(f"   Docs: {error_info.get('documentation')}")
            break
            
        else:
            # Unknown status
            print(f"⚠️ Unknown status: {status}")
            print(f"Full response: {json.dumps(status_data, indent=2)}")
            check_num += 1


if __name__ == "__main__":
    main()
