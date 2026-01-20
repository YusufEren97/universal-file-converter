"""
Archive Converter - Enhanced Version
Converts archive files between ZIP, 7Z, TAR, GZ, TAR.GZ formats.
"""
import os
import shutil
import asyncio
import zipfile
import tarfile

# Optional 7z support
try:
    import py7zr
    HAS_7Z = True
except ImportError:
    HAS_7Z = False


async def convert_archive(input_path: str, output_dir: str, target_format: str) -> dict:
    """Archive converter supporting ZIP, 7Z, TAR, GZ."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_archive, input_path, output_dir, target_format)


def _process_archive(input_path: str, output_dir: str, target_format: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        
        # Handle .tar.gz double extension
        if name.endswith('.tar'):
            name = name[:-4]
        
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Create temp extraction directory
        extract_dir = os.path.join(output_dir, f"_temp_{name}")
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            # === EXTRACT SOURCE ===
            ext_lower = ext.lower()
            
            if ext_lower == '.zip':
                with zipfile.ZipFile(input_path, 'r') as zf:
                    zf.extractall(extract_dir)
                    
            elif ext_lower == '.7z':
                if not HAS_7Z:
                    return {"success": False, "error": "py7zr kütüphanesi yüklü değil. 'pip install py7zr' çalıştırın."}
                with py7zr.SevenZipFile(input_path, mode='r') as zf:
                    zf.extractall(path=extract_dir)
                    
            elif ext_lower == '.tar':
                with tarfile.open(input_path, 'r') as tf:
                    tf.extractall(extract_dir)
                    
            elif ext_lower == '.gz':
                # Could be .tar.gz or just .gz
                if filename.lower().endswith('.tar.gz') or filename.lower().endswith('.tgz'):
                    with tarfile.open(input_path, 'r:gz') as tf:
                        tf.extractall(extract_dir)
                else:
                    import gzip
                    out_name = name if not name.endswith('.gz') else name[:-3]
                    out_file = os.path.join(extract_dir, out_name)
                    with gzip.open(input_path, 'rb') as f_in:
                        with open(out_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                            
            elif ext_lower == '.tgz':
                with tarfile.open(input_path, 'r:gz') as tf:
                    tf.extractall(extract_dir)
                    
            elif ext_lower == '.bz2':
                if filename.lower().endswith('.tar.bz2'):
                    with tarfile.open(input_path, 'r:bz2') as tf:
                        tf.extractall(extract_dir)
                else:
                    import bz2
                    out_name = name[:-4] if name.endswith('.bz2') else name
                    out_file = os.path.join(extract_dir, out_name)
                    with bz2.open(input_path, 'rb') as f_in:
                        with open(out_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
            else:
                return {"success": False, "error": f"Desteklenmeyen kaynak format: {ext}"}
            
            # === COMPRESS TO TARGET ===
            if target_format == 'zip':
                # Remove extension if already added by make_archive
                base_output = output_path.replace('.zip', '')
                shutil.make_archive(base_output, 'zip', extract_dir)
                
            elif target_format == '7z':
                if not HAS_7Z:
                    return {"success": False, "error": "py7zr kütüphanesi yüklü değil. 'pip install py7zr' çalıştırın."}
                with py7zr.SevenZipFile(output_path, 'w') as zf:
                    for root, dirs, files in os.walk(extract_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, extract_dir)
                            zf.write(file_path, arcname)
                            
            elif target_format == 'tar':
                with tarfile.open(output_path, 'w') as tf:
                    for item in os.listdir(extract_dir):
                        tf.add(os.path.join(extract_dir, item), arcname=item)
                        
            elif target_format in ['tar.gz', 'tgz', 'gz']:
                if target_format == 'gz':
                    output_path = output_path.replace('.gz', '.tar.gz')
                    output_filename = output_filename.replace('.gz', '.tar.gz')
                with tarfile.open(output_path, 'w:gz') as tf:
                    for item in os.listdir(extract_dir):
                        tf.add(os.path.join(extract_dir, item), arcname=item)
                        
            else:
                return {"success": False, "error": f"Desteklenmeyen hedef format: {target_format}"}
                
        finally:
            # Cleanup temp directory
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)

        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"Arşiv dönüşüm hatası: {str(e)}"}
