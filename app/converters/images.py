"""
Smart Image Converter - Enhanced Version
Converts images between all major formats using Pillow.
Supports: JPG, PNG, WEBP, HEIC, SVG, ICO, BMP, GIF, TIFF, AVIF, PDF
"""
import os
import asyncio
from PIL import Image

# Register HEIF/HEIC opener if available
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HAS_HEIF = True
except ImportError:
    HAS_HEIF = False

# Check AVIF support
try:
    from PIL import features
    HAS_AVIF = features.check('avif')
except:
    HAS_AVIF = False


async def convert_image(input_path: str, output_dir: str, target_format: str, quality: str = "high") -> dict:
    """Image converter with format detection and quality settings."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_image, input_path, output_dir, target_format, quality)


def _process_image(input_path: str, output_dir: str, target_format: str, quality: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        # === SVG HANDLING (Special case - vector format) ===
        if ext_lower == '.svg':
            return _convert_svg(input_path, output_path, output_filename, target_format)
        
        # === OPEN IMAGE ===
        with Image.open(input_path) as img:
            # Get original format info
            original_mode = img.mode
            
            # === FORMAT-SPECIFIC CONVERSION ===
            
            # Convert to RGB for formats that don't support alpha
            if target_format in ['jpg', 'jpeg', 'bmp', 'pdf'] and original_mode in ['RGBA', 'P', 'LA']:
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ['RGBA', 'LA']:
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Quality settings based on user preference
            quality_value = 95 if quality == 'high' else 80
            
            # === SAVE WITH FORMAT-SPECIFIC OPTIONS ===
            
            if target_format in ['jpg', 'jpeg']:
                save_kwargs = {
                    'quality': quality_value,
                    'subsampling': 0 if quality == 'high' else 2,
                    'optimize': True
                }
                img.save(output_path, 'JPEG', **save_kwargs)
                
            elif target_format == 'png':
                save_kwargs = {'optimize': True}
                if quality != 'high':
                    save_kwargs['compress_level'] = 9
                img.save(output_path, 'PNG', **save_kwargs)
                
            elif target_format == 'webp':
                save_kwargs = {
                    'quality': quality_value,
                    'method': 6 if quality == 'high' else 4
                }
                # Preserve animation for animated WebP
                if getattr(img, 'n_frames', 1) > 1:
                    save_kwargs['save_all'] = True
                img.save(output_path, 'WEBP', **save_kwargs)
                
            elif target_format == 'gif':
                if img.mode != 'P':
                    img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
                save_kwargs = {'optimize': True}
                # Preserve animation
                if getattr(img, 'n_frames', 1) > 1:
                    save_kwargs['save_all'] = True
                    save_kwargs['loop'] = 0
                img.save(output_path, 'GIF', **save_kwargs)
                
            elif target_format == 'bmp':
                img.save(output_path, 'BMP')
                
            elif target_format in ['tiff', 'tif']:
                save_kwargs = {'compression': 'tiff_lzw' if quality == 'high' else 'tiff_deflate'}
                img.save(output_path, 'TIFF', **save_kwargs)
                
            elif target_format == 'ico':
                # ICO requires specific sizes
                sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
                img_copy = img.copy()
                img_copy.thumbnail((256, 256), Image.LANCZOS)
                img_copy.save(output_path, 'ICO', sizes=sizes)
                
            elif target_format == 'pdf':
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_path, 'PDF', resolution=150.0)
                
            elif target_format in ['heic', 'heif']:
                if not HAS_HEIF:
                    return {"success": False, "error": "pillow-heif yüklü değil. 'pip install pillow-heif' çalıştırın."}
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(output_path, 'HEIF', quality=quality_value)
                
            elif target_format == 'avif':
                if not HAS_AVIF:
                    return {"success": False, "error": "AVIF desteği için Pillow 9.1+ ve libavif gerekli."}
                save_kwargs = {'quality': quality_value}
                img.save(output_path, 'AVIF', **save_kwargs)
                
            else:
                # Generic save for other formats
                img.save(output_path)
            
        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"Resim dönüşüm hatası: {str(e)}"}


def _convert_svg(input_path: str, output_path: str, output_filename: str, target_format: str) -> dict:
    """Convert SVG to raster formats using cairosvg."""
    try:
        import cairosvg
    except ImportError:
        return {"success": False, "error": "cairosvg yüklü değil. 'pip install cairosvg' çalıştırın."}
    
    try:
        if target_format == 'png':
            cairosvg.svg2png(url=input_path, write_to=output_path, scale=2.0)
        elif target_format == 'pdf':
            cairosvg.svg2pdf(url=input_path, write_to=output_path)
        elif target_format in ['jpg', 'jpeg']:
            # SVG -> PNG -> JPG
            import io
            png_data = cairosvg.svg2png(url=input_path, scale=2.0)
            with Image.open(io.BytesIO(png_data)) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(output_path, 'JPEG', quality=95)
        else:
            return {"success": False, "error": f"SVG sadece PNG, PDF veya JPG'ye dönüştürülebilir."}
            
        return {"success": True, "output_path": output_path, "filename": output_filename}
        
    except Exception as e:
        return {"success": False, "error": f"SVG dönüşüm hatası: {str(e)}"}
