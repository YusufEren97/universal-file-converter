"""
Universal Media Converter - Enhanced Version
Converts video/audio files using FFmpeg.
Supports all common video and audio formats with quality presets.
"""
import os
import asyncio
import shutil

# Supported formats
VIDEO_FORMATS = ['mp4', 'webm', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'm4v', '3gp', 'mpeg', 'mpg', 'ts']
AUDIO_FORMATS = ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a', 'wma', 'aiff', 'opus', 'ac3', 'amr', 'm4r']


async def convert_media(input_path: str, output_dir: str, target_format: str, quality: str = "high") -> dict:
    """Generic FFmpeg converter for video and audio files."""
    try:
        # Check FFmpeg availability
        ffmpeg_cmd = shutil.which("ffmpeg")
        if not ffmpeg_cmd:
            return {"success": False, "error": "FFmpeg sistemde bulunamadı. Lütfen FFmpeg yükleyin."}

        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        # Build FFmpeg command
        cmd = [ffmpeg_cmd, '-y', '-i', input_path]
        
        # Add format-specific options
        cmd.extend(_get_format_options(target_format, quality))
        cmd.append(output_path)

        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)  # 10 min timeout
        
        if process.returncode == 0:
            return {"success": True, "output_path": output_path, "filename": output_filename}
        else:
            error_msg = stderr.decode('utf-8', errors='ignore')[:200] if stderr else "Bilinmeyen hata"
            return {"success": False, "error": f"FFmpeg hatası: {error_msg}"}

    except asyncio.TimeoutError:
        return {"success": False, "error": "İşlem zaman aşımına uğradı (10 dakika)"}
    except Exception as e:
        return {"success": False, "error": f"Medya dönüşüm hatası: {str(e)}"}


def _get_format_options(target_format: str, quality: str) -> list:
    """Get FFmpeg options for target format."""
    options = []
    
    # === AUDIO FORMATS ===
    if target_format in AUDIO_FORMATS:
        options.append('-vn')  # No video
        
        if target_format == 'mp3':
            bitrate = '320k' if quality == 'high' else '192k'
            options.extend(['-acodec', 'libmp3lame', '-ab', bitrate])
            
        elif target_format == 'wav':
            options.extend(['-acodec', 'pcm_s16le', '-ar', '44100'])
            
        elif target_format == 'aac':
            bitrate = '256k' if quality == 'high' else '192k'
            options.extend(['-acodec', 'aac', '-ab', bitrate])
            
        elif target_format == 'ogg':
            quality_level = '8' if quality == 'high' else '5'
            options.extend(['-acodec', 'libvorbis', '-aq', quality_level])
            
        elif target_format == 'flac':
            options.extend(['-acodec', 'flac', '-compression_level', '8'])
            
        elif target_format == 'm4a':
            bitrate = '256k' if quality == 'high' else '192k'
            options.extend(['-acodec', 'aac', '-ab', bitrate])
            
        elif target_format == 'opus':
            bitrate = '192k' if quality == 'high' else '128k'
            options.extend(['-acodec', 'libopus', '-ab', bitrate])
            
        elif target_format == 'aiff':
            options.extend(['-acodec', 'pcm_s16be'])
            
        elif target_format == 'ac3':
            options.extend(['-acodec', 'ac3', '-ab', '384k'])
            
        elif target_format == 'wma':
            options.extend(['-acodec', 'wmav2', '-ab', '192k'])
            
        elif target_format == 'm4r':  # iPhone ringtone
            options.extend(['-acodec', 'aac', '-ab', '128k', '-t', '30'])  # Max 30 seconds
            
    # === VIDEO FORMATS ===
    elif target_format == 'gif':
        # Animated GIF from video
        options.extend([
            '-vf', 'fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            '-loop', '0'
        ])
        
    elif target_format in VIDEO_FORMATS:
        if target_format == 'mp4':
            options.extend(['-c:v', 'libx264', '-c:a', 'aac', '-movflags', '+faststart'])
            if quality == 'high':
                options.extend(['-crf', '18', '-preset', 'slow'])
            else:
                options.extend(['-crf', '23', '-preset', 'veryfast'])
                
        elif target_format == 'webm':
            options.extend(['-c:v', 'libvpx-vp9', '-c:a', 'libopus'])
            if quality == 'high':
                options.extend(['-b:v', '4M', '-crf', '20'])
            else:
                options.extend(['-b:v', '2M', '-crf', '30'])
                
        elif target_format == 'avi':
            options.extend(['-c:v', 'mpeg4', '-c:a', 'mp3'])
            if quality == 'high':
                options.extend(['-q:v', '3'])
            else:
                options.extend(['-q:v', '6'])
                
        elif target_format == 'mkv':
            options.extend(['-c:v', 'libx264', '-c:a', 'aac'])
            if quality == 'high':
                options.extend(['-crf', '18', '-preset', 'slow'])
            else:
                options.extend(['-crf', '23', '-preset', 'veryfast'])
                
        elif target_format == 'mov':
            options.extend(['-c:v', 'libx264', '-c:a', 'aac', '-tag:v', 'avc1'])
            if quality == 'high':
                options.extend(['-crf', '18'])
            else:
                options.extend(['-crf', '23'])
                
        elif target_format == 'wmv':
            options.extend(['-c:v', 'wmv2', '-c:a', 'wmav2', '-b:v', '2M'])
            
        elif target_format == 'flv':
            options.extend(['-c:v', 'flv', '-c:a', 'mp3', '-ar', '44100'])
            
        elif target_format == 'm4v':
            options.extend(['-c:v', 'libx264', '-c:a', 'aac'])
            
        elif target_format == '3gp':
            options.extend(['-c:v', 'h263', '-c:a', 'amr_nb', '-s', '352x288', '-ar', '8000'])
            
        elif target_format in ['mpeg', 'mpg']:
            options.extend(['-c:v', 'mpeg2video', '-c:a', 'mp2'])
            
        elif target_format == 'ts':
            options.extend(['-c:v', 'libx264', '-c:a', 'aac', '-f', 'mpegts'])
    
    return options
