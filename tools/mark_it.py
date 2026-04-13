#!/usr/bin/env python3
"""
Convert various document formats to Markdown using Docling.

Usage:
    python tools/mark_it.py <path-to-source>
    python tools/mark_it.py raw/documents/report.pdf
"""

import os
import sys
from pathlib import Path
from docling.document_converter import DocumentConverter

# Thiết lập đường dẫn tương tự như ingest.py
REPO_ROOT = Path(__file__).parent.parent
RAW_DIR = REPO_ROOT / "raw"

def convert_to_markdown(input_path: Path) -> Path:
    """
    Chuyển đổi file đầu vào sang Markdown và lưu vào thư mục raw/.
    """
    if not input_path.exists():
        print(f"Error: File not found at {input_path}")
        sys.exit(1)

    # Khởi tạo converter (Docling hỗ trợ sẵn PDF, DOCX, HTML, v.v.)
    converter = DocumentConverter()
    
    print(f"--- Processing: {input_path.name} ---")
    try:
        result = converter.convert(str(input_path))
        md_content = result.document.export_to_markdown()
        
        # Tạo file output trong thư mục raw/
        output_filename = f"{input_path.stem}.md"
        output_path = RAW_DIR / output_filename
        
        # Đảm bảo thư mục raw tồn tại
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        
        output_path.write_text(md_content, encoding="utf-8")
        
        print(f"--- Conversion successful: {output_path.relative_to(REPO_ROOT)} ---")
        return output_path
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/mark_it.py <path-to-source>")
        sys.exit(1)
        
    source_path = Path(sys.argv[1])
    convert_to_markdown(source_path)