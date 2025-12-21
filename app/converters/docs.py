"""
Data Converter
Converts data files between CSV, XLSX, JSON formats using Pandas.
"""
import os
import pandas as pd
import asyncio

async def convert_doc(input_path: str, output_dir: str, target_format: str) -> dict:
    """Data file converter supporting CSV, XLSX, JSON, TXT."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _process_data, input_path, output_dir, target_format)

def _process_data(input_path: str, output_dir: str, target_format: str) -> dict:
    try:
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        ext = ext.lower()
        output_filename = f"{name}.{target_format}"
        output_path = os.path.join(output_dir, output_filename)

        if ext == '.csv':
            df = pd.read_csv(input_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path)
        elif ext == '.json':
            df = pd.read_json(input_path)
        elif ext == '.txt':
            try:
                df = pd.read_csv(input_path, sep='\t')
            except:
                df = pd.read_csv(input_path)
        else:
            return {"success": False, "error": f"Unsupported source format: {ext}"}

        if target_format == 'csv':
            df.to_csv(output_path, index=False)
        elif target_format == 'xlsx':
            df.to_excel(output_path, index=False, engine='openpyxl')
        elif target_format == 'json':
            df.to_json(output_path, orient='records', indent=2)
        elif target_format == 'txt':
            df.to_csv(output_path, index=False, sep='\t')
        else:
            return {"success": False, "error": f"Unsupported target format: {target_format}"}

        return {"success": True, "output_path": output_path, "filename": output_filename}

    except Exception as e:
        return {"success": False, "error": f"Data conversion error: {str(e)}"}
