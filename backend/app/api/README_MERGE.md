# Video Merge Endpoint Documentation

## Overview

The video merge endpoint (`POST /api/videos/merge`) combines approved video scenes into a final 30-second advertisement video using FFmpeg's concat demuxer for lossless merging.

## Endpoint

```
POST /api/videos/merge
```

## Prerequisites

1. **FFmpeg Installation**: FFmpeg must be installed and available in the system PATH
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

2. **Session Requirements**:
   - Valid session with scene descriptions
   - All four video scenes generated (hook, problem, solution, cta)
   - Video files stored in the outputs/ directory

## Request Body

```json
{
  "session_id": "string",
  "scene_videos": {
    "hook": "/outputs/session_hook_abc123.mp4",
    "problem": "/outputs/session_problem_def456.mp4",
    "solution": "/outputs/session_solution_ghi789.mp4",
    "cta": "/outputs/session_cta_jkl012.mp4"
  }
}
```

### Fields

- `session_id` (string, required): Valid session identifier
- `scene_videos` (object, required): Mapping of scenario names to video URLs
  - Must include all four scenarios: hook, problem, solution, cta
  - Video URLs should be in format: `/outputs/filename.mp4`

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Videos merged successfully into final video",
  "final_video_url": "/outputs/session_final_xyz789.mp4",
  "duration": 30
}
```

### Error Responses

#### 400 Bad Request - Missing Scene Videos
```json
{
  "detail": "No scene videos provided for merging"
}
```

#### 400 Bad Request - Incomplete Scenes
```json
{
  "detail": "Missing video scenes for: solution, cta"
}
```

#### 404 Not Found - Invalid Session
```json
{
  "detail": "Session not found or expired"
}
```

#### 500 Internal Server Error - FFmpeg Not Available
```json
{
  "detail": "FFmpeg is not installed or not available. Cannot merge videos."
}
```

#### 500 Internal Server Error - Merge Failed
```json
{
  "detail": "Failed to merge videos: [error details]"
}
```

## Workflow

1. **Validation**:
   - Validates session exists and is not expired
   - Checks all four required scenarios are provided
   - Verifies FFmpeg is installed

2. **Preparation**:
   - Converts relative video URLs to absolute file paths
   - Validates all video files exist
   - Calculates total duration from scene descriptions

3. **Merging**:
   - Creates FFmpeg concat file with video list
   - Executes FFmpeg concat demuxer (lossless merge)
   - Stores final video in outputs/ directory

4. **Session Update**:
   - Updates session with final video URL
   - Returns response with video URL and duration

## Video Merge Order

Videos are merged in the following fixed order:
1. Hook (7 seconds)
2. Problem (7 seconds)
3. Solution (10 seconds)
4. CTA (6 seconds)

**Total Duration**: ~30 seconds

## FFmpeg Service

The merge functionality is implemented in `app/services/ffmpeg_service.py`:

### Key Methods

#### `merge_scene_videos(scene_videos, session_id)`
High-level method that orchestrates the merge process:
- Validates all required scenes are present
- Converts URLs to file paths
- Calls `stitch_videos_ffmpeg()` for actual merging
- Returns relative URL to final video

#### `stitch_videos_ffmpeg(video_paths, output_path, temp_dir)`
Low-level FFmpeg wrapper based on `scripts/utils/examples/video_helpers.py`:
- Creates concat file with video list
- Executes FFmpeg with concat demuxer
- Uses `-c copy` for lossless merging (no re-encoding)
- Cleans up temporary files

#### `check_ffmpeg_installed()`
Verifies FFmpeg availability:
- Runs `ffmpeg -version` command
- Returns True if FFmpeg is available
- Logs warning if not found

## Example Usage

### Python (requests)

```python
import requests

# Merge videos
response = requests.post(
    "http://localhost:8000/api/videos/merge",
    json={
        "session_id": "abc-123-def-456",
        "scene_videos": {
            "hook": "/outputs/abc123_hook_xyz.mp4",
            "problem": "/outputs/abc123_problem_xyz.mp4",
            "solution": "/outputs/abc123_solution_xyz.mp4",
            "cta": "/outputs/abc123_cta_xyz.mp4"
        }
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Final video: {data['final_video_url']}")
    print(f"Duration: {data['duration']} seconds")
else:
    print(f"Error: {response.json()['detail']}")
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/videos/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def-456",
    "scene_videos": {
      "hook": "/outputs/abc123_hook_xyz.mp4",
      "problem": "/outputs/abc123_problem_xyz.mp4",
      "solution": "/outputs/abc123_solution_xyz.mp4",
      "cta": "/outputs/abc123_cta_xyz.mp4"
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/videos/merge', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: 'abc-123-def-456',
    scene_videos: {
      hook: '/outputs/abc123_hook_xyz.mp4',
      problem: '/outputs/abc123_problem_xyz.mp4',
      solution: '/outputs/abc123_solution_xyz.mp4',
      cta: '/outputs/abc123_cta_xyz.mp4'
    }
  })
});

const data = await response.json();
if (response.ok) {
  console.log('Final video:', data.final_video_url);
  console.log('Duration:', data.duration, 'seconds');
} else {
  console.error('Error:', data.detail);
}
```

## Technical Details

### FFmpeg Command

The service uses FFmpeg's concat demuxer:

```bash
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.mp4 -y
```

Where `concat_list.txt` contains:
```
file '/absolute/path/to/hook.mp4'
file '/absolute/path/to/problem.mp4'
file '/absolute/path/to/solution.mp4'
file '/absolute/path/to/cta.mp4'
```

### Benefits of Concat Demuxer

- **Lossless**: No re-encoding, preserves original quality
- **Fast**: Simple file concatenation, no processing
- **Reliable**: Works with any video codec/format
- **Efficient**: Minimal CPU/memory usage

### Requirements for Concat

For best results, all input videos should have:
- Same codec (e.g., H.264)
- Same resolution (e.g., 1366x768)
- Same frame rate (e.g., 30fps)
- Same audio codec (if present)

The Runware video generation ensures these requirements are met.

## Error Handling

The service includes comprehensive error handling:

1. **Session Validation**: Checks session exists and is valid
2. **Input Validation**: Verifies all required scenes are provided
3. **File Validation**: Confirms all video files exist
4. **FFmpeg Availability**: Checks FFmpeg is installed
5. **Merge Errors**: Catches and logs FFmpeg failures
6. **Cleanup**: Removes temporary files even on failure

## Testing

Run the unit tests to verify the implementation:

```bash
# Unit tests (no server required)
python backend/test_ffmpeg_unit.py

# Integration tests (requires running server)
python backend/test_merge_api.py
```

## Related Files

- `backend/app/services/ffmpeg_service.py` - FFmpeg service implementation
- `backend/app/api/videos.py` - Video API endpoints including merge
- `backend/app/models/video.py` - Request/response models
- `scripts/utils/examples/video_helpers.py` - Original FFmpeg utilities
- `backend/test_ffmpeg_unit.py` - Unit tests
- `backend/test_merge_api.py` - Integration tests

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **7.1**: Merges four video scenes in sequence (hook, problem, solution, cta)
- **7.2**: Displays progress indicator during merge (handled by frontend)
- **7.3**: Stores final video in outputs/ directory and updates session
- **7.9**: Handles FFmpeg failures with error messages and retry capability
