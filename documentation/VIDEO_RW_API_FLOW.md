# Runware Video API - Complete Integration Guide

**✅ VERIFIED WORKING FLOW**  
This document explains the exact step-by-step process for successfully generating videos using the Runware API, based on tested and working code.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [API Endpoint & Authentication](#api-endpoint--authentication)
4. [Complete Workflow](#complete-workflow)
5. [Step-by-Step Implementation](#step-by-step-implementation)
6. [Response Structures](#response-structures)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Full Code Example](#full-code-example)

---

## Overview

### What This Flow Does

1. **Upload** a product image to Runware
2. **Submit** a video generation request with specific parameters
3. **Poll** for completion using async task checking
4. **Download** the final generated video

### Verified Configuration

```python
✅ Model: minimax:1@1 (MiniMax 01 Base)
✅ Duration: 6 seconds
✅ Dimensions: 1366x768
✅ Generation Time: ~244 seconds (4 minutes)
✅ Output Format: MP4
```

---

## Prerequisites

### Required Packages

```bash
pip install requests pillow python-dotenv
```

### Environment Setup

Create a `.env` file:

```bash
RUNWARE_API_KEY=your_api_key_here
```

### Image Requirements

- **Format:** JPEG or PNG
- **Dimensions:** Must match model requirements (1366x768 for MiniMax)
- **Size:** Recommended < 10MB
- **Quality:** High resolution for best results

---

## API Endpoint & Authentication

### Base URL

```
https://api.runware.ai/v1
```

### Headers (Required for ALL requests)

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {your_api_key}"
}
```

### Request Method

**ALL requests use POST** (even status checks)

---

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    RUNWARE VIDEO API FLOW                   │
└─────────────────────────────────────────────────────────────┘

Step 1: PREPARE IMAGE
├─ Resize to model dimensions (1366x768)
├─ Convert to JPEG if needed
└─ Encode to base64

Step 2: UPLOAD IMAGE
├─ POST to /v1 with taskType: "imageUpload"
├─ Send base64 encoded image
└─ Receive imageUUID

Step 3: SUBMIT VIDEO REQUEST
├─ POST to /v1 with taskType: "videoInference"
├─ Include imageUUID, prompt, model, dimensions
├─ Set deliveryMethod: "async"
└─ Receive taskUUID (acknowledgment)

Step 4: POLL FOR COMPLETION
├─ POST to /v1 with taskType: "getResponse"
├─ Send taskUUID to check status
├─ Wait 5 seconds between polls
├─ Check response.data[] and response.errors[]
└─ Continue until status: "success" or "error"

Step 5: DOWNLOAD VIDEO
├─ Extract videoURL from success response
├─ GET request to videoURL
└─ Save MP4 file locally

┌─────────────────────────────────────────────────────────────┐
│                    TOTAL TIME: ~4-5 minutes                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Implementation

### Step 1: Prepare Image

**Why:** Runware models require specific dimensions. MiniMax requires 1366x768.

```python
from PIL import Image
import os

def prepare_image(image_path, target_width=1366, target_height=768):
    """Resize image to model requirements."""
    img = Image.open(image_path)
    img_resized = img.resize((target_width, target_height), Image.LANCZOS)
    
    # Save as JPEG
    output_path = os.path.join(
        os.path.dirname(image_path), 
        "resized_image.jpeg"
    )
    img_resized.save(output_path, format="JPEG", quality=95)
    
    return output_path
```

**Key Points:**
- Use `Image.LANCZOS` for high-quality resizing
- Save as JPEG (widely supported)
- Quality 95 recommended for best results

---

### Step 2: Upload Image

**Endpoint:** `POST https://api.runware.ai/v1`

**Request Structure:**

```python
import base64
import uuid
import requests

def upload_image(api_key, image_path):
    """Upload image and get UUID."""
    
    # 1. Read and encode image
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    # 2. Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 3. Create payload (MUST be an array)
    payload = [
        {
            "taskType": "imageUpload",
            "taskUUID": str(uuid.uuid4()),  # Generate unique UUID
            "image": image_b64  # Base64 encoded image
        }
    ]
    
    # 4. Send request
    response = requests.post(
        "https://api.runware.ai/v1",
        headers=headers,
        json=payload
    )
    
    # 5. Handle response
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.status_code}, {response.text}")
    
    data = response.json()
    
    # 6. Extract imageUUID
    # Response can have "results" or "data" key
    data_list = data.get("results") or data.get("data") or []
    
    if not data_list or "imageUUID" not in data_list[0]:
        raise Exception(f"Unexpected response: {data}")
    
    image_uuid = data_list[0]["imageUUID"]
    return image_uuid
```

**Response Example:**

```json
{
  "data": [
    {
      "taskType": "imageUpload",
      "taskUUID": "abc-123-def-456",
      "imageUUID": "c64351d5-4c59-42f7-95e1-eace013eddab"
    }
  ]
}
```

**Critical Points:**
- ✅ Payload MUST be an array `[{...}]`
- ✅ Generate a unique `taskUUID` for each request
- ✅ Image must be base64 encoded
- ✅ Save the returned `imageUUID` for next step

---

### Step 3: Submit Video Generation Request

**Endpoint:** `POST https://api.runware.ai/v1`

**Request Structure:**

```python
def generate_video(api_key, prompt, image_id):
    """Submit video generation request."""
    
    # 1. Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 2. Generate task UUID
    task_uuid = str(uuid.uuid4())
    
    # 3. Create payload (MUST be an array)
    payload = [
        {
            "taskType": "videoInference",
            "taskUUID": task_uuid,
            "model": "minimax:1@1",  # ✅ Verified working model
            "positivePrompt": prompt,  # Your video description
            "duration": 6,  # Seconds (6 for MiniMax)
            "width": 1366,  # Required for MiniMax
            "height": 768,  # Required for MiniMax
            "outputType": "URL",  # Return video as URL
            "outputFormat": "MP4",  # MP4 or WEBM
            "deliveryMethod": "async",  # ⚠️ REQUIRED for video
            "frameImages": [
                {
                    "inputImage": image_id,  # imageUUID from Step 2
                    "frame": "first"  # Use image as first frame
                }
            ],
            "numberResults": 1  # Generate 1 video
        }
    ]
    
    # 4. Send request
    response = requests.post(
        "https://api.runware.ai/v1",
        headers=headers,
        json=payload
    )
    
    # 5. Handle response
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code}, {response.text}")
    
    data = response.json()
    
    # 6. Verify acknowledgment
    if "data" not in data or not data["data"]:
        raise Exception(f"Unexpected response: {data}")
    
    task_data = data["data"][0]
    returned_uuid = task_data.get("taskUUID")
    returned_type = task_data.get("taskType")
    
    # 7. Validate response
    if returned_uuid != task_uuid:
        raise Exception(f"UUID mismatch! Sent: {task_uuid}, Got: {returned_uuid}")
    
    if returned_type != "videoInference":
        raise Exception(f"Wrong task type: {returned_type}")
    
    # ✅ Request acknowledged
    return task_uuid
```

**Response Example (Acknowledgment):**

```json
{
  "data": [
    {
      "taskType": "videoInference",
      "taskUUID": "24cd5dff-cb81-4db5-8506-b72a9425f9d1"
    }
  ]
}
```

**Critical Points:**
- ✅ `deliveryMethod: "async"` is REQUIRED (video takes time)
- ✅ `frameImages` array must contain the uploaded `imageUUID`
- ✅ Only ONE frame image allowed for MiniMax
- ✅ Dimensions MUST match model requirements
- ✅ Response only confirms request was accepted (not completed)

---

### Step 4: Poll for Completion

**Endpoint:** `POST https://api.runware.ai/v1`

**Why Polling:** Video generation takes ~4 minutes. You must repeatedly check status.

**Request Structure:**

```python
import time

def check_task_status(api_key, task_uuid):
    """Check video generation status."""
    
    # 1. Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 2. Create getResponse payload
    payload = [
        {
            "taskType": "getResponse",  # ⚠️ Special task type for polling
            "taskUUID": task_uuid  # UUID from Step 3
        }
    ]
    
    # 3. Send request
    response = requests.post(
        "https://api.runware.ai/v1",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"Status check failed: {response.status_code}")
    
    result = response.json()
    
    # 4. Check errors array FIRST
    if "errors" in result and result["errors"]:
        for error in result["errors"]:
            if error.get("taskUUID") == task_uuid:
                return {
                    "status": "error",
                    "error": error
                }
    
    # 5. Check data array for our task
    if "data" in result and result["data"]:
        for item in result["data"]:
            if item.get("taskUUID") == task_uuid:
                return item  # Return the task data
    
    # 6. Task not found
    return {
        "status": "unknown",
        "message": "Task not found"
    }


def poll_until_complete(api_key, task_uuid, poll_interval=5):
    """Poll until video is ready."""
    
    print("⏳ Polling for completion...")
    poll_count = 0
    
    while True:
        time.sleep(poll_interval)  # Wait between polls
        poll_count += 1
        
        # Check status
        status_data = check_task_status(api_key, task_uuid)
        status = status_data.get("status")
        
        print(f"   Poll #{poll_count}: {status}")
        
        if status == "success":
            # ✅ Video is ready!
            return status_data
        
        elif status == "error":
            # ❌ Generation failed
            return status_data
        
        elif status == "processing":
            # ⏳ Still working, continue polling
            continue
        
        else:
            # Unknown status, continue polling
            continue
```

**Response Examples:**

**While Processing:**
```json
{
  "data": [
    {
      "taskType": "videoInference",
      "taskUUID": "24cd5dff-cb81-4db5-8506-b72a9425f9d1",
      "status": "processing"
    }
  ]
}
```

**When Complete:**
```json
{
  "data": [
    {
      "taskType": "videoInference",
      "taskUUID": "24cd5dff-cb81-4db5-8506-b72a9425f9d1",
      "status": "success",
      "videoUUID": "b7db282d-2943-4f12-992f-77df3ad3ec71",
      "videoURL": "https://vm.runware.ai/video/ws/5/vi/b7db282d-2943-4f12-992f-77df3ad3ec71.mp4",
      "cost": 0.18,
      "seed": 12345
    }
  ]
}
```

**When Failed:**
```json
{
  "data": [],
  "errors": [
    {
      "code": "timeoutProvider",
      "status": "error",
      "message": "Provider timeout",
      "taskUUID": "24cd5dff-cb81-4db5-8506-b72a9425f9d1"
    }
  ]
}
```

**Critical Points:**
- ✅ Use `taskType: "getResponse"` for polling
- ✅ Wait 5 seconds between polls (don't spam the API)
- ✅ Check BOTH `data[]` and `errors[]` arrays
- ✅ Match `taskUUID` to find your specific task
- ✅ Status values: `"processing"`, `"success"`, `"error"`
- ✅ Expected time: ~240 seconds (4 minutes)

---

### Step 5: Download Video

**Once status is "success", download the video:**

```python
def download_video(video_url, save_path):
    """Download video from URL."""
    
    response = requests.get(video_url, stream=True)
    
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    
    return False
```

**Critical Points:**
- ✅ Use `stream=True` for large files
- ✅ Write in chunks (8192 bytes recommended)
- ✅ Video URL is temporary (download immediately)
- ✅ Save as `.mp4` file

---

## Response Structures

### Image Upload Response

```json
{
  "data": [
    {
      "taskType": "imageUpload",
      "taskUUID": "your-task-uuid",
      "imageUUID": "c64351d5-4c59-42f7-95e1-eace013eddab"
    }
  ]
}
```

**Extract:** `imageUUID`

---

### Video Request Acknowledgment

```json
{
  "data": [
    {
      "taskType": "videoInference",
      "taskUUID": "your-task-uuid"
    }
  ]
}
```

**Meaning:** Request accepted, now poll for completion

---

### Video Status Response (Processing)

```json
{
  "data": [
    {
      "taskType": "videoInference",
      "taskUUID": "your-task-uuid",
      "status": "processing"
    }
  ]
}
```

**Action:** Continue polling

---

### Video Status Response (Success)

```json
{
  "data": [
    {
      "taskType": "videoInference",
      "taskUUID": "your-task-uuid",
      "status": "success",
      "videoUUID": "b7db282d-2943-4f12-992f-77df3ad3ec71",
      "videoURL": "https://vm.runware.ai/video/...",
      "cost": 0.18,
      "seed": 12345
    }
  ]
}
```

**Extract:** `videoURL` for download

---

### Video Status Response (Error)

```json
{
  "data": [],
  "errors": [
    {
      "code": "invalidModel",
      "status": "error",
      "message": "Invalid model parameter",
      "taskUUID": "your-task-uuid",
      "documentation": "https://runware.ai/docs/..."
    }
  ]
}
```

**Action:** Check error code and message

---

## Error Handling

### Common Errors

#### 1. Invalid Dimensions

```json
{
  "code": "invalidFrameImageWidth",
  "message": "Frame image width invalid"
}
```

**Solution:** Resize image to 1366x768 for MiniMax

---

#### 2. Invalid Model

```json
{
  "code": "invalidModel",
  "message": "Invalid model parameter"
}
```

**Solution:** Use verified model: `"minimax:1@1"`

---

#### 3. Invalid Duration

```json
{
  "code": "invalidDuration",
  "message": "Duration must be 6 for this model"
}
```

**Solution:** Use `duration: 6` for MiniMax

---

#### 4. Provider Timeout

```json
{
  "code": "timeoutProvider",
  "message": "Provider did not respond"
}
```

**Solution:** Retry the request (temporary issue)

---

### Error Handling Pattern

```python
try:
    # Step 1: Upload
    image_id = upload_image(api_key, image_path)
    
    # Step 2: Generate
    task_uuid = generate_video(api_key, prompt, image_id)
    
    # Step 3: Poll
    result = poll_until_complete(api_key, task_uuid)
    
    # Step 4: Handle result
    if result.get("status") == "success":
        video_url = result.get("videoURL")
        download_video(video_url, "output.mp4")
    else:
        error = result.get("error", {})
        print(f"Error: {error.get('message')}")
        
except Exception as e:
    print(f"Failed: {str(e)}")
```

---

## Best Practices

### 1. Image Preparation

✅ **DO:**
- Resize to exact model dimensions (1366x768)
- Use high-quality source images
- Save as JPEG with quality 95
- Keep file size under 10MB

❌ **DON'T:**
- Upload images without resizing
- Use very low quality images
- Use unsupported formats

---

### 2. API Requests

✅ **DO:**
- Always use arrays for payloads: `[{...}]`
- Generate unique UUIDs for each request
- Include all required headers
- Set `deliveryMethod: "async"` for video

❌ **DON'T:**
- Send single objects (must be arrays)
- Reuse task UUIDs
- Forget Content-Type header
- Use sync mode for video (will timeout)

---

### 3. Polling

✅ **DO:**
- Wait 5 seconds between polls
- Check both `data[]` and `errors[]` arrays
- Match taskUUID to find your task
- Set reasonable timeout (10 minutes)

❌ **DON'T:**
- Poll faster than 5 seconds (API rate limits)
- Only check `data[]` array
- Assume first item is your task
- Poll indefinitely without timeout

---

### 4. Video Download

✅ **DO:**
- Download immediately when ready
- Use streaming for large files
- Save with proper file extension (.mp4)
- Handle download failures gracefully

❌ **DON'T:**
- Delay download (URLs may expire)
- Load entire video into memory
- Assume download always succeeds

---

## Full Code Example

```python
"""
Complete Runware Video Generation Example
✅ Verified working code
"""

import requests
import uuid
import base64
import time
import os
from PIL import Image
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("RUNWARE_API_KEY")
API_URL = "https://api.runware.ai/v1"

# Configuration
IMAGE_PATH = "product.jpg"
PROMPT = "A smooth rotating video of a premium product with cinematic lighting"
OUTPUT_PATH = "output.mp4"


def prepare_image(image_path):
    """Resize image to model requirements."""
    img = Image.open(image_path)
    img_resized = img.resize((1366, 768), Image.LANCZOS)
    temp_path = "resized_temp.jpeg"
    img_resized.save(temp_path, format="JPEG", quality=95)
    return temp_path


def upload_image(api_key, image_path):
    """Upload image and return UUID."""
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = [{
        "taskType": "imageUpload",
        "taskUUID": str(uuid.uuid4()),
        "image": image_b64
    }]
    
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return (data.get("results") or data.get("data"))[0]["imageUUID"]


def generate_video(api_key, prompt, image_id):
    """Submit video generation request."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    task_uuid = str(uuid.uuid4())
    
    payload = [{
        "taskType": "videoInference",
        "taskUUID": task_uuid,
        "model": "minimax:1@1",
        "positivePrompt": prompt,
        "duration": 6,
        "width": 1366,
        "height": 768,
        "outputType": "URL",
        "outputFormat": "MP4",
        "deliveryMethod": "async",
        "frameImages": [{"inputImage": image_id, "frame": "first"}],
        "numberResults": 1
    }]
    
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    return task_uuid


def check_status(api_key, task_uuid):
    """Check video generation status."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = [{
        "taskType": "getResponse",
        "taskUUID": task_uuid
    }]
    
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    
    # Check errors
    if "errors" in result and result["errors"]:
        for error in result["errors"]:
            if error.get("taskUUID") == task_uuid:
                return {"status": "error", "error": error}
    
    # Check data
    if "data" in result and result["data"]:
        for item in result["data"]:
            if item.get("taskUUID") == task_uuid:
                return item
    
    return {"status": "unknown"}


def poll_until_complete(api_key, task_uuid):
    """Poll until video is ready."""
    print("⏳ Waiting for video generation...")
    
    while True:
        time.sleep(5)
        status_data = check_status(api_key, task_uuid)
        status = status_data.get("status")
        
        print(f"   Status: {status}")
        
        if status == "success":
            return status_data
        elif status == "error":
            raise Exception(f"Generation failed: {status_data.get('error')}")


def download_video(url, save_path):
    """Download video from URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    """Complete workflow."""
    print("🎬 Starting video generation...")
    
    # Step 1: Prepare image
    print("\n1️⃣ Preparing image...")
    resized_path = prepare_image(IMAGE_PATH)
    
    # Step 2: Upload image
    print("\n2️⃣ Uploading image...")
    image_id = upload_image(API_KEY, resized_path)
    print(f"   Image UUID: {image_id}")
    
    # Step 3: Generate video
    print("\n3️⃣ Submitting video request...")
    task_uuid = generate_video(API_KEY, PROMPT, image_id)
    print(f"   Task UUID: {task_uuid}")
    
    # Step 4: Poll for completion
    print("\n4️⃣ Polling for completion (~4 minutes)...")
    result = poll_until_complete(API_KEY, task_uuid)
    
    # Step 5: Download video
    print("\n5️⃣ Downloading video...")
    video_url = result.get("videoURL")
    download_video(video_url, OUTPUT_PATH)
    
    print(f"\n✅ SUCCESS! Video saved: {OUTPUT_PATH}")
    print(f"   Cost: ${result.get('cost', 0):.4f}")


if __name__ == "__main__":
    main()
```

---

## Summary Checklist

### Before Making Requests

- [ ] API key configured in environment
- [ ] Image resized to 1366x768
- [ ] Image saved as JPEG
- [ ] All required packages installed

### During Implementation

- [ ] All payloads are arrays `[{...}]`
- [ ] Unique UUID generated for each request
- [ ] Headers include Content-Type and Authorization
- [ ] `deliveryMethod: "async"` set for video requests
- [ ] Poll interval is 5 seconds minimum
- [ ] Check both `data[]` and `errors[]` in responses
- [ ] Match `taskUUID` to find specific task

### After Success

- [ ] Download video immediately
- [ ] Save with .mp4 extension
- [ ] Clean up temporary files
- [ ] Log cost and video UUID for tracking

---

## Additional Resources

- **Runware Docs:** https://runware.ai/docs/en/video-inference/api-reference
- **Model Reference:** See `documentation/video_models.md`
- **Helper Functions:** See `scripts/video_helpers.py`
- **Working Example:** See `testing/testing_runware.py`

---

**Last Updated:** Based on verified working code (MiniMax 01 Base, 244s generation time)
