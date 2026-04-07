"""
Convert all PDFs in book-pdf/ to Markdown using marker-pdf.
marker uses a deep-learning pipeline that handles Arabic script and
complex scanned layouts better than Tesseract-based tools.

Usage:
    .venv/bin/python scripts/convert_books_marker.py
"""

import os
import pathlib
import sys

# Force CPU — MPS (Apple Metal) causes tensor bounds errors with these PDFs
os.environ["TORCH_DEVICE"] = "cpu"

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

ROOT = pathlib.Path(__file__).parent.parent
BOOK_PDF_DIR = ROOT / "book-pdf"
BOOK_MD_DIR = ROOT / "book-md"
BOOK_MD_DIR.mkdir(exist_ok=True)

pdfs = sorted(BOOK_PDF_DIR.glob("*.pdf"))

if not pdfs:
    print(f"No PDFs found in {BOOK_PDF_DIR}")
    sys.exit(1)  

print("Loading marker models (first run downloads ~2 GB of weights)...")
models = create_model_dict()
print("Models ready.\n")

# pdftext_workers=1 avoids ProcessPoolExecutor which crashes on macOS with some PDFs
converter = PdfConverter(artifact_dict=models, config={"pdftext_workers": 1})

for pdf_path in pdfs:
    parts = pdf_path.stem.split(" - ")
    short_name = "-".join(p.strip().lower().replace(" ", "-") for p in parts[:2])
    md_path = BOOK_MD_DIR / f"{short_name}.md"

    print(f"Converting: {pdf_path.name}")
    print(f"       → {md_path.name}")

    rendered = converter(str(pdf_path))
    md_text, _, _ = text_from_rendered(rendered)

    md_path.write_text(md_text, encoding="utf-8")
    size_kb = md_path.stat().st_size // 1024
    print(f"  Done — {size_kb} KB written\n")

print("All books converted.")
