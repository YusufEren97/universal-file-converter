"""
Data Converter - Enhanced Version
Converts data files between CSV, XLSX, JSON, XML, HTML, TXT formats using Pandas.
"""
import os
import pandas as pd
import asyncio


async def convert_doc(input_path: str, output_dir: str, target_format: str) -> dict:
    """Data file converter supporting CSV, XLSX, JSON, XML, HTML, TXT."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_data, input_path, output_dir, target_format)


def _process_data(input_path: str, output_dir: str, target_format: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        # === READ INPUT ===
        df = None
        
        if ext == '.csv':
            df = pd.read_csv(input_path, encoding='utf-8')
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path)
        elif ext == '.json':
            # Try different JSON formats
            try:
                df = pd.read_json(input_path)
            except:
                df = pd.read_json(input_path, lines=True)
        elif ext == '.xml':
            df = pd.read_xml(input_path)
        elif ext == '.html':
            # Read first table from HTML
            tables = pd.read_html(input_path)
            if tables:
                df = tables[0]
            else:
                return {"success": False, "error": "No tables found in HTML file"}
        elif ext == '.txt':
            # Try tab-separated first, then comma
            try:
                df = pd.read_csv(input_path, sep='\t', encoding='utf-8')
            except:
                try:
                    df = pd.read_csv(input_path, encoding='utf-8')
                except:
                    # Plain text - read as single column
                    with open(input_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    df = pd.DataFrame({'content': [line.strip() for line in lines if line.strip()]})
        else:
            return {"success": False, "error": f"Unsupported source format: {ext}"}

        if df is None or df.empty:
            return {"success": False, "error": "Could not read data from file"}

        # === WRITE OUTPUT ===
        if target_format == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8')
            
        elif target_format == 'xlsx':
            df.to_excel(output_path, index=False, engine='openpyxl')
            
        elif target_format == 'json':
            df.to_json(output_path, orient='records', indent=2, force_ascii=False)
            
        elif target_format == 'xml':
            df.to_xml(output_path, index=False, root_name='data', row_name='record')
            
        elif target_format == 'html':
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 1200px; 
            margin: 40px auto; 
            padding: 20px; 
        }}
        h1 {{ color: #333; }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        th {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 15px; 
            text-align: left;
            font-weight: 600;
        }}
        td {{ 
            padding: 10px 15px; 
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{ background-color: #f8f9fa; }}
        tr:nth-child(even) {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{name}</h1>
    {df.to_html(index=False, classes='data-table', border=0)}
</body>
</html>"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        elif target_format == 'txt':
            df.to_csv(output_path, index=False, sep='\t', encoding='utf-8')
            
        else:
            return {"success": False, "error": f"Unsupported target format: {target_format}"}

        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"Data conversion error: {str(e)}"}
