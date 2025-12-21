"""
Universal Media Converter
Converts video/audio files using FFmpeg.
Supports: MP4, AVI, MKV, MOV, WEBM, MP3, WAV, FLAC, AAC, OGG, etc.
"""
import os
import asyncio
import shutil

async def convert_media(input_path: str, output_dir: str, target_format: str, quality: str = "high") -> dict:
    """Generic FFmpeg converter for video and audio files."""
    try:
        ffmpeg_cmd = shutil.which("ffmpeg")
        if not ffmpeg_cmd:
            return {"success": False, "error": "FFmpeg not found on system"}

        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        cmd = [ffmpeg_cmd, '-y', '-i', input_path]

        if target_format in ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a']:
            cmd.append('-vn')
            
            if target_format == 'mp3':
                cmd.extend(['-acodec', 'libmp3lame', '-ab', '192k'])
            elif target_format == 'wav':
                cmd.extend(['-acodec', 'pcm_s16le', '-ar', '44100'])
            elif target_format == 'aac':
                cmd.extend(['-acodec', 'aac', '-ab', '192k'])
            elif target_format == 'ogg':
                cmd.extend(['-acodec', 'libvorbis', '-aq', '5'])
            elif target_format == 'flac':
                cmd.extend(['-acodec', 'flac'])
            elif target_format == 'm4a':
                cmd.extend(['-acodec', 'aac', '-ab', '192k'])
                
        elif target_format == 'gif':
            cmd.extend(['-vf', 'fps=10,scale=480:-1:flags=lanczos'])
            
        elif target_format in ['mp4', 'webm', 'avi', 'mkv']:
            if target_format == 'mp4':
                cmd.extend(['-c:v', 'libx264', '-c:a', 'aac', '-movflags', 'faststart'])
                if quality == 'high':
                    cmd.extend(['-crf', '18', '-preset', 'slow'])
                else:
                    cmd.extend(['-crf', '23', '-preset', 'veryfast'])
            elif target_format == 'webm':
                cmd.extend(['-c:v', 'libvpx-vp9', '-c:a', 'libopus', '-b:v', '2M'])
            elif target_format == 'avi':
                cmd.extend(['-c:v', 'mpeg4', '-c:a', 'mp3', '-q:v', '5'])
            elif target_format == 'mkv':
                cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])

        cmd.append(output_path)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        
        if process.returncode == 0:
            return {"success": True, "output_path": output_path, "filename": output_filename}
        else:
            error_msg = stderr.decode()[:150] if stderr else "Unknown error"
            return {"success": False, "error": f"FFmpeg error: {error_msg}"}

    except asyncio.TimeoutError:
        return {"success": False, "error": "Operation timed out (5 min)"}
    except Exception as e:
        return {"success": False, "error": str(e)}
