"""
PDF Converter
Converts PDF files to TXT, DOCX, HTML, MD, RTF formats.
"""
import os
import asyncio

async def convert_pdf(input_path: str, output_dir: str, target_format: str) -> dict:
    """PDF converter supporting text extraction and document formats."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_pdf, input_path, output_dir, target_format)

def _process_pdf(input_path: str, output_dir: str, target_format: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

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

        if target_format == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
        elif target_format in ['docx', 'doc']:
            try:
                from docx import Document
            except ImportError:
                return {"success": False, "error": "python-docx not installed. Run 'pip install python-docx'"}
            
            doc = Document()
            for para in text_content.split('\n'):
                if para.strip():
                    doc.add_paragraph(para)
            doc.save(output_path)
        elif target_format == 'html':
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
        p {{ margin: 1em 0; }}
    </style>
</head>
<body>
"""
            for para in text_content.split('\n'):
                if para.strip():
                    html_content += f"    <p>{para}</p>\n"
            html_content += "</body>\n</html>"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        elif target_format == 'md':
            md_content = f"# {name}\n\n"
            for para in text_content.split('\n'):
                if para.strip():
                    md_content += f"{para}\n\n"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
        elif target_format == 'rtf':
            rtf_content = "{\\rtf1\\ansi\\deff0\n"
            for para in text_content.split('\n'):
                if para.strip():
                    escaped = para.encode('unicode_escape').decode('ascii')
                    rtf_content += f"\\par {escaped}\n"
            rtf_content += "}"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
        else:
            return {"success": False, "error": f"Unsupported target format for PDF: {target_format}"}

        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"PDF conversion error: {str(e)}"}
