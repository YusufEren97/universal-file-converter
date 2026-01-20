"""
PDF Converter - Enhanced Version
Converts PDF files to DOCX (with formatting), TXT, HTML, MD, RTF, and images.
Uses pdf2docx for high-quality DOCX conversion.
"""
import os
import asyncio


async def convert_pdf(input_path: str, output_dir: str, target_format: str) -> dict:
    """PDF converter supporting multiple output formats with formatting preservation."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_pdf, input_path, output_dir, target_format)


def _process_pdf(input_path: str, output_dir: str, target_format: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        if target_format in ['docx', 'doc']:
            return _pdf_to_docx(input_path, output_path, output_filename)
        elif target_format == 'txt':
            return _pdf_to_txt(input_path, output_path, output_filename)
        elif target_format == 'html':
            return _pdf_to_html(input_path, output_path, output_filename, name)
        elif target_format == 'md':
            return _pdf_to_md(input_path, output_path, output_filename, name)
        elif target_format == 'rtf':
            return _pdf_to_rtf(input_path, output_path, output_filename)
        elif target_format in ['png', 'jpg', 'jpeg']:
            return _pdf_to_images(input_path, output_dir, target_format, name)
        else:
            return {"success": False, "error": f"Unsupported target format for PDF: {target_format}"}

    except Exception as e:
        return {"success": False, "error": f"PDF conversion error: {str(e)}"}


def _pdf_to_docx(input_path: str, output_path: str, output_filename: str) -> dict:
    """Convert PDF to DOCX with formatting preservation using pdf2docx."""
    try:
        from pdf2docx import Converter
        
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        
        if os.path.exists(output_path):
            return {"success": True, "output_path": output_path, "filename": output_filename}
        return {"success": False, "error": "DOCX file was not created"}
        
    except ImportError:
        return {"success": False, "error": "pdf2docx not installed. Run 'pip install pdf2docx'"}
    except Exception as e:
        # Fallback to basic text extraction if pdf2docx fails
        return _pdf_to_docx_fallback(input_path, output_path, output_filename, str(e))


def _pdf_to_docx_fallback(input_path: str, output_path: str, output_filename: str, original_error: str) -> dict:
    """Fallback: Basic PDF to DOCX conversion using PyPDF2 + python-docx."""
    try:
        import PyPDF2
        from docx import Document
        
        text_content = ""
        with open(input_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n\n"
        
        if not text_content.strip():
            return {"success": False, "error": f"Could not extract text from PDF. Original error: {original_error}"}
        
        doc = Document()
        for para in text_content.split('\n'):
            if para.strip():
                doc.add_paragraph(para)
        doc.save(output_path)
        
        return {
            "success": True, 
            "output_path": output_path, 
            "filename": output_filename,
            "note": "Basic text extraction used (formatting may be limited)"
        }
    except Exception as e:
        return {"success": False, "error": f"PDF conversion failed: {str(e)}"}


def _pdf_to_txt(input_path: str, output_path: str, output_filename: str) -> dict:
    """Extract text from PDF."""
    try:
        import PyPDF2
    except ImportError:
        return {"success": False, "error": "PyPDF2 not installed. Run 'pip install PyPDF2'"}

    text_content = ""
    
    with open(input_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content += f"--- Page {i+1} ---\n{page_text}\n\n"

    if not text_content.strip():
        return {"success": False, "error": "Could not extract text from PDF (may be image-based)"}

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    return {"success": True, "output_path": output_path, "filename": output_filename}


def _pdf_to_html(input_path: str, output_path: str, output_filename: str, name: str) -> dict:
    """Convert PDF to HTML."""
    try:
        import PyPDF2
    except ImportError:
        return {"success": False, "error": "PyPDF2 not installed. Run 'pip install PyPDF2'"}

    text_content = ""
    with open(input_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n\n"

    if not text_content.strip():
        return {"success": False, "error": "Could not extract text from PDF (may be image-based)"}

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 800px; 
            margin: 40px auto; 
            padding: 20px; 
            line-height: 1.6; 
        }}
        p {{ margin: 1em 0; }}
    </style>
</head>
<body>
    <h1>{name}</h1>
"""
    for para in text_content.split('\n'):
        if para.strip():
            html_content += f"    <p>{para}</p>\n"
    html_content += "</body>\n</html>"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {"success": True, "output_path": output_path, "filename": output_filename}


def _pdf_to_md(input_path: str, output_path: str, output_filename: str, name: str) -> dict:
    """Convert PDF to Markdown."""
    try:
        import PyPDF2
    except ImportError:
        return {"success": False, "error": "PyPDF2 not installed. Run 'pip install PyPDF2'"}

    text_content = ""
    with open(input_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n\n"

    if not text_content.strip():
        return {"success": False, "error": "Could not extract text from PDF (may be image-based)"}

    md_content = f"# {name}\n\n"
    for para in text_content.split('\n'):
        if para.strip():
            md_content += f"{para}\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return {"success": True, "output_path": output_path, "filename": output_filename}


def _pdf_to_rtf(input_path: str, output_path: str, output_filename: str) -> dict:
    """Convert PDF to RTF."""
    try:
        import PyPDF2
    except ImportError:
        return {"success": False, "error": "PyPDF2 not installed. Run 'pip install PyPDF2'"}

    text_content = ""
    with open(input_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n\n"

    if not text_content.strip():
        return {"success": False, "error": "Could not extract text from PDF (may be image-based)"}

    rtf_content = "{\\rtf1\\ansi\\deff0\n"
    for para in text_content.split('\n'):
        if para.strip():
            escaped = para.encode('unicode_escape').decode('ascii')
            rtf_content += f"\\par {escaped}\n"
    rtf_content += "}"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rtf_content)
    
    return {"success": True, "output_path": output_path, "filename": output_filename}


def _pdf_to_images(input_path: str, output_dir: str, target_format: str, name: str) -> dict:
    """Convert PDF pages to images using PyMuPDF (no Poppler needed)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return {"success": False, "error": "PyMuPDF yüklü değil. 'pip install PyMuPDF' çalıştırın."}
    
    try:
        pdf_doc = fitz.open(input_path)
        output_files = []
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            # Higher resolution for better quality (2x = 144 DPI)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            
            img_filename = f"{name}_page_{page_num + 1}.{target_format}"
            img_path = os.path.join(output_dir, img_filename)
            
            if target_format.lower() in ['jpg', 'jpeg']:
                pix.save(img_path, output="jpeg", jpg_quality=95)
            else:
                pix.save(img_path)
            
            output_files.append(img_filename)
        
        pdf_doc.close()
        
        if output_files:
            return {
                "success": True, 
                "output_path": os.path.join(output_dir, output_files[0]), 
                "filename": output_files[0],
                "all_files": output_files,
                "note": f"{len(output_files)} sayfa resmi oluşturuldu"
            }
        
        return {"success": False, "error": "Sayfa dönüştürülemedi"}
        
    except Exception as e:
        return {"success": False, "error": f"PDF→resim dönüşüm hatası: {str(e)}"}
