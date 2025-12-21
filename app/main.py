"""
Universal Converter - Main API
FastAPI backend for file conversion operations.
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
import shutil
import os
import time
import threading
from .utils import check_ffmpeg, get_output_dir, clean_filename
from .converters.images import convert_image
from .converters.video import convert_media
from .converters.docs import convert_doc
from .converters.pdf import convert_pdf
from pydantic import BaseModel
import webbrowser

class ConvertRequest(BaseModel):
    file_path: str
    target_format: str
    quality: str = "high"

app = FastAPI(title="Universal Converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, 'index.html'))

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/api/check-ffmpeg")
async def api_check_ffmpeg():
    exists, path = check_ffmpeg()
    return {"installed": exists, "path": path}

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Save uploaded file temporarily and analyze its type."""
    try:
        safe_filename = clean_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        ext = os.path.splitext(safe_filename)[1].lower()
        size = os.path.getsize(file_path)
        
        file_type = "unknown"
        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.ico', '.gif', '.heic', '.svg', '.avif']:
            file_type = "image"
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']:
            file_type = "video"
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']:
            file_type = "audio"
        elif ext in ['.csv', '.xlsx', '.xls', '.json', '.txt']:
            file_type = "data"
        elif ext == '.pdf':
            file_type = "pdf"
        elif ext in ['.zip', '.7z', '.tar', '.gz']:
            file_type = "archive"

        return {
            "filename": safe_filename,
            "original_name": file.filename,
            "path": file_path,
            "type": file_type,
            "size": size,
            "extension": ext
        }
    except Exception as e:
         return JSONResponse(status_code=500, content={"message": str(e)})

@app.on_event("shutdown")
def remove_temp_files():
    if os.path.exists(UPLOAD_DIR):
        try:
            shutil.rmtree(UPLOAD_DIR)
            os.makedirs(UPLOAD_DIR)
        except:
            pass

@app.on_event("startup")
async def startup_event():
    """Open browser on startup and start cleanup thread."""
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:9999")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    def cleanup_old_files():
        while True:
            time.sleep(600)
            try:
                now = time.time()
                if os.path.exists(UPLOAD_DIR):
                    for f in os.listdir(UPLOAD_DIR):
                        fpath = os.path.join(UPLOAD_DIR, f)
                        if os.path.isfile(fpath):
                            age = now - os.path.getmtime(fpath)
                            if age > 600:
                                os.remove(fpath)
                                print(f"[Cleanup] Deleted: {f}")
            except Exception as e:
                print(f"[Cleanup] Error: {e}")
    
    cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()

@app.post("/api/convert")
async def api_convert(request: ConvertRequest):
    output_dir = get_output_dir()
    file_path = os.path.join(UPLOAD_DIR, request.file_path)
    
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {request.file_path}"}
    
    ext = os.path.splitext(file_path)[1].lower()
    result = {"success": False, "error": "Unknown file type"}

    try:
        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.ico', '.gif']:
            result = await convert_image(file_path, output_dir, request.target_format, request.quality)
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']:
            result = await convert_media(file_path, output_dir, request.target_format, request.quality)
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']:
            result = await convert_media(file_path, output_dir, request.target_format, request.quality)
        elif ext in ['.csv', '.xlsx', '.xls', '.json', '.txt']:
            result = await convert_doc(file_path, output_dir, request.target_format)
        elif ext == '.pdf':
            result = await convert_pdf(file_path, output_dir, request.target_format)
        elif ext in ['.zip', '.7z', '.tar', '.gz']:
            from .converters.archive import convert_archive
            result = await convert_archive(file_path, output_dir, request.target_format)
    except Exception as e:
        result = {"success": False, "error": f"Conversion error: {str(e)}"}
    
    return result

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download converted file."""
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(get_output_dir(), safe_filename)
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=safe_filename,
            media_type='application/octet-stream'
        )
    return JSONResponse(status_code=404, content={"error": "File not found"})

@app.post("/api/download-all")
async def download_all_files(request: dict):
    """Download multiple files as ZIP."""
    import zipfile
    import io
    
    filenames = request.get('filenames', [])
    if not filenames:
        return JSONResponse(status_code=400, content={"error": "File list empty"})

    output_dir = get_output_dir()
    zip_buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename in filenames:
                safe_name = os.path.basename(filename)
                file_path = os.path.join(output_dir, safe_name)
                if os.path.exists(file_path):
                    zip_file.write(file_path, safe_name)
        
        zip_buffer.seek(0)
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=downloads.zip"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
