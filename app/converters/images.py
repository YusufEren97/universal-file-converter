"""
Smart Image Converter
Converts images between formats using Pillow.
Supports: JPG, PNG, WEBP, HEIC, SVG, ICO, BMP, GIF, PDF
"""
from PIL import Image
import os
import asyncio
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

async def convert_image(input_path: str, output_dir: str, target_format: str, quality: str = "high") -> dict:
    """Image converter with format detection and quality settings."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_image, input_path, output_dir, target_format, quality)

def _process_image(input_path: str, output_dir: str, target_format: str, quality: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        if ext.lower() == '.svg':
            try:
                import cairosvg
                if target_format == 'png':
                    cairosvg.svg2png(url=input_path, write_to=output_path)
                    return {"success": True, "output_path": output_path, "filename": output_filename}
                elif target_format == 'pdf':
                    cairosvg.svg2pdf(url=input_path, write_to=output_path)
                    return {"success": True, "output_path": output_path, "filename": output_filename}
                else:
                     return {"success": False, "error": "SVG can only be converted to PNG or PDF."}
            except ImportError:
                 return {"success": False, "error": "cairosvg library missing."}
            except Exception as e:
                 return {"success": False, "error": f"SVG error: {str(e)}"}

        with Image.open(input_path) as img:
            if target_format in ['jpg', 'jpeg', 'bmp', 'pdf'] and img.mode in ['RGBA', 'P']:
                img = img.convert('RGB')

            save_kwargs = {}
            
            if target_format in ['jpg', 'jpeg']:
                save_kwargs = {'quality': 95, 'subsampling': 0, 'optimize': True}
                
            elif target_format == 'webp':
                save_kwargs = {'quality': 95, 'method': 4}
                
            elif target_format == 'png':
                save_kwargs = {'optimize': True}
                
            elif target_format == 'ico':
                img.thumbnail((256, 256))
                save_kwargs = {'format': 'ICO', 'sizes': [(256, 256)]}
                
            elif target_format == 'pdf':
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_path, 'PDF', resolution=100.0)
                return {"success": True, "output_path": output_path, "filename": output_filename}

            if target_format == 'heic':
                 save_kwargs = {'format': 'HEIF', 'quality': 90}

            img.save(output_path, **save_kwargs)
            
        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"Image conversion error: {str(e)}"}
