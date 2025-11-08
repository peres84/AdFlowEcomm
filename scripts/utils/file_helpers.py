"""
File and Directory Helper Utilities

Common file operations used across testing scripts:
- Directory creation and validation
- File discovery and filtering
- Path resolution
- File downloads
"""

import os
import requests
from typing import List, Optional, Tuple


def ensure_directory(directory_path: str, verbose: bool = True) -> str:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to directory
        verbose: Print status messages
        
    Returns:
        str: Absolute path to directory
        
    Example:
        >>> ensure_directory("results")
        📁 Created folder: /path/to/results
    """
    abs_path = os.path.abspath(directory_path)
    
    if not os.path.exists(abs_path):
        os.makedirs(abs_path)
        if verbose:
            print(f"📁 Created folder: {abs_path}")
    else:
        if verbose:
            print(f"📁 Using existing folder: {abs_path}")
    
    return abs_path


def find_files_by_extension(
    directory: str,
    extensions: List[str],
    recursive: bool = False,
    sort: bool = True
) -> List[str]:
    """
    Find all files with specified extensions in a directory.
    
    Args:
        directory: Directory to search
        extensions: List of extensions (e.g., ['.mp4', '.avi'])
        recursive: Search subdirectories
        sort: Sort results alphabetically
        
    Returns:
        List of file paths
        
    Example:
        >>> videos = find_files_by_extension("vid_test", ['.mp4', '.avi'])
        >>> print(videos)
        ['vid_test/video1.mp4', 'vid_test/video2.mp4']
    """
    if not os.path.exists(directory):
        return []
    
    found_files = []
    
    # Normalize extensions to lowercase
    extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                  for ext in extensions]
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    found_files.append(os.path.join(root, file))
    else:
        files = os.listdir(directory)
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                found_files.append(os.path.join(directory, file))
    
    if sort:
        found_files.sort()
    
    return found_files


def find_first_file(
    directory: str,
    extensions: List[str],
    verbose: bool = True
) -> Optional[str]:
    """
    Find the first file with specified extensions (alphabetically).
    
    Args:
        directory: Directory to search
        extensions: List of extensions to look for
        verbose: Print status messages
        
    Returns:
        Path to first file found, or None
        
    Example:
        >>> video = find_first_file("vid_test", ['.mp4', '.avi'])
        📹 Found video: video1.mp4
    """
    if not os.path.exists(directory):
        if verbose:
            print(f"❌ Directory not found: {directory}")
        return None
    
    files = find_files_by_extension(directory, extensions, sort=True)
    
    if files:
        if verbose:
            print(f"📹 Found: {os.path.basename(files[0])}")
        return files[0]
    
    if verbose:
        print(f"❌ No files found in {directory}")
        print(f"   Supported formats: {', '.join(extensions)}")
    
    return None


def download_file(
    url: str,
    save_path: str,
    chunk_size: int = 8192,
    verbose: bool = True
) -> bool:
    """
    Download a file from URL with progress indication.
    
    Args:
        url: URL to download from
        save_path: Local path to save file
        chunk_size: Download chunk size in bytes
        verbose: Print status messages
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> download_file("https://example.com/file.mp4", "output.mp4")
        ⬇️  Downloading...
        ✅ File saved at: output.mp4
    """
    try:
        if verbose:
            print(f"⬇️  Downloading...")
            print(f"   URL: {url[:50]}...")
        
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            # Ensure directory exists
            directory = os.path.dirname(save_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
            
            if verbose:
                print(f"✅ File saved at: {save_path}")
            return True
        else:
            if verbose:
                print(f"❌ Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        if verbose:
            print(f"❌ Download error: {str(e)}")
        return False


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        float: File size in MB
    """
    if not os.path.exists(file_path):
        return 0.0
    
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def resolve_project_paths(script_file: str) -> Tuple[str, str, str, str]:
    """
    Resolve standard project paths from a script location.
    
    Useful for scripts in nested directories that need to find
    the project root and .env file.
    
    Args:
        script_file: __file__ from the calling script
        
    Returns:
        Tuple of (script_dir, scripts_dir, root_dir, env_path)
        
    Example:
        >>> # In scripts/testing_audio/my_script.py
        >>> script_dir, scripts_dir, root_dir, env_path = resolve_project_paths(__file__)
        >>> # script_dir = scripts/testing_audio/
        >>> # scripts_dir = scripts/
        >>> # root_dir = project root
        >>> # env_path = project_root/.env
    """
    script_dir = os.path.dirname(os.path.abspath(script_file))
    scripts_dir = os.path.dirname(script_dir)
    root_dir = os.path.dirname(scripts_dir)
    env_path = os.path.join(root_dir, ".env")
    
    return script_dir, scripts_dir, root_dir, env_path


# Video-specific extensions
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']

# Image-specific extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']

# Audio-specific extensions
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']
