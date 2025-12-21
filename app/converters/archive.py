"""
Archive Converter
Converts archive files between ZIP, 7Z, TAR formats.
"""
import os
import shutil
import asyncio
import zipfile
import py7zr

async def convert_archive(input_path: str, output_dir: str, target_format: str) -> dict:
    """Archive converter supporting ZIP, 7Z, TAR."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_archive, input_path, output_dir, target_format)

def _process_archive(input_path: str, output_dir: str, target_format: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        extract_dir = os.path.join(output_dir, f"_temp_{name}")
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
            
        try:
            if ext.lower() == '.zip':
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif ext.lower() == '.7z':
                with py7zr.SevenZipFile(input_path, mode='r') as z:
                    z.extractall(path=extract_dir)
            elif ext.lower() in ['.tar', '.gz']:
                import tarfile
                with tarfile.open(input_path, 'r') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                 return {"success": False, "error": f"Unsupported source format: {ext}"}
                 
            if target_format == 'zip':
                shutil.make_archive(output_path.replace('.zip', ''), 'zip', extract_dir)
                
            elif target_format == '7z':
                with py7zr.SevenZipFile(output_path, 'w') as z:
                    z.writeall(extract_dir, arcname='')
                    
            elif target_format == 'tar':
                import tarfile
                with tarfile.open(output_path, "w") as tar:
                    tar.add(extract_dir, arcname=os.path.basename(extract_dir))
            else:
                return {"success": False, "error": f"Unsupported target format: {target_format}"}
                
        finally:
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)

        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"Archive conversion error: {str(e)}"}
