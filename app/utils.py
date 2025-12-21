"""
Utility functions for Universal Converter.
"""
import shutil
import os
import re

def check_ffmpeg():
    """Check if FFmpeg is installed on the system."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return True, ffmpeg_path
    return False, None

def get_output_dir():
    """Get or create the output directory for converted files."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "converted_files")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    return output_dir

def clean_filename(filename: str) -> str:
    """
    Sanitize filename for security.
    Removes path injection, special characters and Turkish chars.
    """
    if not filename:
        return "unnamed_file"
    
    filename = filename.replace('\\', '/')
    filename = os.path.basename(filename)
    
    filename = filename.replace('\x00', '')
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    
    dangerous_chars = '<>:"|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    tr_replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'
    }
    for char, replacement in tr_replacements.items():
        filename = filename.replace(char, replacement)
    
    filename = filename.replace(' ', '_')
    
    while '..' in filename:
        filename = filename.replace('..', '.')
    
    if not filename or filename == '.':
        filename = "unnamed_file"
    
    return filename
