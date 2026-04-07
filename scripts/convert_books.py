"""
Convert all PDFs in book-pdf/ to Markdown files in book-md/.
Uses pymupdf4llm for extraction, which preserves Arabic text and layout.
"""

import pathlib
import sys
import pymupdf4llm

BOOK_PDF_DIR = pathlib.Path(__file__).parent.parent / "book-pdf"
BOOK_MD_DIR = pathlib.Path(__file__).parent.parent / "book-md"

BOOK_MD_DIR.mkdir(exist_ok=True)

pdfs = sorted(BOOK_PDF_DIR.glob("*.pdf"))

if not pdfs:
    print(f"No PDFs found in {BOOK_PDF_DIR}")
    sys.exit(1)

for pdf_path in pdfs:
    # e.g. "Fluent in Levantine Arabic - Ad - Muna Khalil.pdf"
    # → "fluent-levantine-ad.md"
    parts = pdf_path.stem.split(" - ")
    short_name = "-".join(p.strip().lower().replace(" ", "-") for p in parts[:2])
    md_path = BOOK_MD_DIR / f"{short_name}.md"

    print(f"Converting: {pdf_path.name}")
    print(f"       → {md_path.name}")

    md_text = pymupdf4llm.to_markdown(str(pdf_path))
    md_path.write_text(md_text, encoding="utf-8")

    size_kb = md_path.stat().st_size // 1024
    print(f"  Done — {size_kb} KB written\n")

print("All books converted.")
