"""
Quality Assurance checks for Runware prompts.
Validates that generated prompts meet all requirements.
"""

from typing import Dict, List, Any, Tuple


def check_image_prompt_quality(prompt_data: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Check if an image prompt meets quality requirements.
    
    Args:
        prompt_data: Dictionary with use_case, runware_prompt, logo_integration
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    runware_prompt = prompt_data.get("runware_prompt", "").lower()
    
    # Check for specific lighting mention
    lighting_keywords = [
        "lighting", "light", "illumination", "studio", "golden hour",
        "daylight", "diffused", "shadow", "bright", "soft", "hard"
    ]
    if not any(keyword in runware_prompt for keyword in lighting_keywords):
        issues.append("Missing specific lighting description")
    
    # Check for composition details
    composition_keywords = [
        "close-up", "mid-shot", "wide", "angle", "framing", "position",
        "center", "third", "rule of thirds", "foreground", "background"
    ]
    if not any(keyword in runware_prompt for keyword in composition_keywords):
        issues.append("Missing composition details (framing, position)")
    
    # Check for materials/textures
    material_keywords = [
        "material", "texture", "surface", "finish", "wood", "metal",
        "fabric", "glass", "concrete", "matte", "glossy", "smooth"
    ]
    if not any(keyword in runware_prompt for keyword in material_keywords):
        issues.append("Missing materials/textures description")
    
    # Check for quality/resolution mention
    quality_keywords = [
        "1024", "professional", "social-media", "high quality", "high-quality",
        "resolution", "polished", "commercial"
    ]
    if not any(keyword in runware_prompt for keyword in quality_keywords):
        issues.append("Missing quality/resolution specification")
    
    # Check prompt length (should be substantial)
    if len(prompt_data.get("runware_prompt", "")) < 100:
        issues.append("Prompt too short (should be 3-5 sentences, detailed)")
    
    # Check for scene description integration (this is harder to validate automatically)
    # We'll just check that prompt is not too generic
    
    is_valid = len(issues) == 0
    return is_valid, issues


def check_video_scene_quality(scene_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check if a video scene description meets quality requirements.
    
    Args:
        scene_data: Dictionary with scene details
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check visual description
    if not scene_data.get("visual_description") or len(scene_data.get("visual_description", "")) < 50:
        issues.append("Visual description too short or missing")
    
    # Check camera/movement
    if not scene_data.get("camera_movement") or len(scene_data.get("camera_movement", "")) < 20:
        issues.append("Camera/movement description too short or missing")
    
    # Check lighting & mood
    if not scene_data.get("lighting_mood") or len(scene_data.get("lighting_mood", "")) < 20:
        issues.append("Lighting & mood description too short or missing")
    
    # Check audio design
    audio_design = scene_data.get("audio_design", {})
    
    if not audio_design.get("music") or len(audio_design.get("music", "")) < 10:
        issues.append("Background music description missing or too short")
    
    if not audio_design.get("dialog") or len(audio_design.get("dialog", "")) < 10:
        issues.append("Dialog/narration missing or too short (REQUIRED)")
    
    if not audio_design.get("balance"):
        issues.append("Audio balance specification missing")
    
    # Check duration matches expected
    scene_num = scene_data.get("scene_number", 0)
    expected_durations = {1: 7, 2: 7, 3: 10, 4: 6}
    if scene_data.get("duration") != expected_durations.get(scene_num):
        issues.append(f"Duration mismatch: expected {expected_durations.get(scene_num)}s, got {scene_data.get('duration')}s")
    
    # Check engagement target
    if not scene_data.get("engagement_target"):
        issues.append("Engagement target missing")
    
    # Scene-specific checks
    if scene_num == 3:  # Solution scene
        if not scene_data.get("benefits_showcased"):
            issues.append("Scene 3 (Solution) missing benefits showcased")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def validate_image_prompts(prompts: List[Dict[str, str]]) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate all image prompts meet quality requirements.
    
    Args:
        prompts: List of image prompt dictionaries
        
    Returns:
        Tuple of (all_valid, validation_report)
    """
    all_valid = True
    report = {
        "total_prompts": len(prompts),
        "valid_prompts": 0,
        "invalid_prompts": 0,
        "prompt_details": []
    }
    
    for i, prompt in enumerate(prompts, 1):
        is_valid, issues = check_image_prompt_quality(prompt)
        
        prompt_detail = {
            "prompt_number": i,
            "use_case": prompt.get("use_case", "Unknown"),
            "is_valid": is_valid,
            "issues": issues
        }
        
        report["prompt_details"].append(prompt_detail)
        
        if is_valid:
            report["valid_prompts"] += 1
        else:
            report["invalid_prompts"] += 1
            all_valid = False
    
    return all_valid, report


def validate_video_scenes(scenes: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate all video scenes meet quality requirements.
    
    Args:
        scenes: List of video scene dictionaries
        
    Returns:
        Tuple of (all_valid, validation_report)
    """
    all_valid = True
    report = {
        "total_scenes": len(scenes),
        "valid_scenes": 0,
        "invalid_scenes": 0,
        "scene_details": []
    }
    
    for scene in scenes:
        is_valid, issues = check_video_scene_quality(scene)
        
        scene_detail = {
            "scene_number": scene.get("scene_number", 0),
            "scene_name": scene.get("scene_name", "Unknown"),
            "duration": scene.get("duration", 0),
            "is_valid": is_valid,
            "issues": issues
        }
        
        report["scene_details"].append(scene_detail)
        
        if is_valid:
            report["valid_scenes"] += 1
        else:
            report["invalid_scenes"] += 1
            all_valid = False
    
    # Check we have exactly 4 scenes
    if len(scenes) != 4:
        all_valid = False
        report["error"] = f"Expected 4 scenes, got {len(scenes)}"
    
    return all_valid, report


def generate_quality_report(
    image_prompts: List[Dict[str, str]] = None,
    video_scenes: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a comprehensive quality report for prompts.
    
    Args:
        image_prompts: Optional list of image prompts to validate
        video_scenes: Optional list of video scenes to validate
        
    Returns:
        Comprehensive quality report dictionary
    """
    report = {
        "image_prompts": None,
        "video_scenes": None,
        "overall_valid": True
    }
    
    if image_prompts:
        is_valid, img_report = validate_image_prompts(image_prompts)
        report["image_prompts"] = img_report
        if not is_valid:
            report["overall_valid"] = False
    
    if video_scenes:
        is_valid, vid_report = validate_video_scenes(video_scenes)
        report["video_scenes"] = vid_report
        if not is_valid:
            report["overall_valid"] = False
    
    return report
