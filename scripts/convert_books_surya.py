"""
Convert the three Fluent in Levantine Arabic PDFs to Arabic+English Markdown
using Surya OCR 2 (datalab-to/surya-ocr-2).

Unlike the old marker pipeline, Surya 2 runs its layout+OCR VLM through
llama.cpp on Apple Silicon (Metal), so it reads the Arabic script that the
scanned PDFs contain — the exact content missing from the earlier extracts.

Usage:
    .venv/bin/python scripts/convert_books_surya.py
    .venv/bin/python scripts/convert_books_surya.py --page-range 0,20-25
    .venv/bin/python scripts/convert_books_surya.py --force   # re-run OCR even if cached

Raw OCR output is cached under .ocr-raw/ so re-running only rebuilds Markdown
(and can resume if an OCR pass was interrupted).
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys

# Surya 2 uses llama.cpp on Apple Silicon; force it so we never fall back to a
# missing NVIDIA/vLLM backend.
os.environ.setdefault("SURYA_INFERENCE_BACKEND", "llamacpp")

from markdownify import markdownify as html_to_md

ROOT = pathlib.Path(__file__).parent.parent
BOOK_PDF_DIR = ROOT / "book-pdf"
BOOK_MD_DIR = ROOT / "book-md"
OCR_RAW_DIR = ROOT / ".ocr-raw"
SURYA_OCR = ROOT / ".venv" / "bin" / "surya_ocr"

# short-name -> source PDF filename. The "ANNOTATED" Lo is intentionally
# excluded so it doesn't collide with / overwrite the canonical Lo volume.
BOOKS = {
    "fluent-in-levantine-arabic-lo": "Fluent in Levantine Arabic - Lo - Muna Khalil.pdf",
    "fluent-in-levantine-arabic-in": "Fluent in Levantine Arabic - In - Muna Khalil.pdf",
    "fluent-in-levantine-arabic-ad": "Fluent in Levantine Arabic - Ad - Muna Khalil.pdf",
}

# Layout labels we drop from the study Markdown (repeated running heads / page numbers).
SKIP_LABELS = {"PageHeader", "PageFooter"}


def run_ocr(pdf_path: pathlib.Path, page_range: str | None, force: bool) -> pathlib.Path:
    """Run surya_ocr on a PDF (unless cached) and return its results.json path."""
    results_path = OCR_RAW_DIR / pdf_path.stem / "results.json"
    if results_path.exists() and not force and not page_range:
        print(f"  Using cached OCR: {results_path.relative_to(ROOT)}")
        return results_path

    cmd = [str(SURYA_OCR), str(pdf_path), "--output_dir", str(OCR_RAW_DIR)]
    if page_range:
        cmd += ["--page_range", page_range]
    print(f"  Running OCR (this can take a while)...")
    subprocess.run(cmd, check=True)
    return results_path


def block_to_md(block: dict) -> str | None:
    """Convert a single Surya layout block to Markdown, or None to skip it."""
    if block.get("skipped") or block.get("error"):
        return None
    if block.get("label") in SKIP_LABELS:
        return None
    html = block.get("html") or ""
    if not html.strip():
        return None
    # Keep tables as raw HTML: Markdown viewers render it, and it preserves the
    # Arabic vocab/conjugation grids far more reliably than a Markdown table.
    if block.get("label") == "Table":
        return html.strip()
    return html_to_md(html, heading_style="ATX").strip()


def results_to_md(results_path: pathlib.Path, title: str) -> str:
    data = json.loads(results_path.read_text(encoding="utf-8"))
    # results.json is keyed by the input filename (no extension).
    pages = next(iter(data.values()))

    out = [f"# {title}", ""]
    for page in pages:
        page_no = page.get("page", "?")
        blocks = sorted(page.get("blocks", []), key=lambda b: b.get("reading_order", 0))
        rendered = [md for b in blocks if (md := block_to_md(b))]
        if not rendered:
            continue
        out.append(f"<!-- page {page_no} -->")
        out.append("")
        out.append("\n\n".join(rendered))
        out.append("")
        out.append("---")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-range", default=None,
                        help="Page range to OCR, e.g. '0,20-25' (0-indexed). Omit for whole book.")
    parser.add_argument("--force", action="store_true",
                        help="Re-run OCR even if a cached results.json exists.")
    args = parser.parse_args()

    BOOK_MD_DIR.mkdir(exist_ok=True)
    OCR_RAW_DIR.mkdir(exist_ok=True)

    missing = [name for name, fn in BOOKS.items() if not (BOOK_PDF_DIR / fn).exists()]
    if missing:
        print(f"ERROR: missing PDFs for: {', '.join(missing)}")
        return 1

    for short_name, filename in BOOKS.items():
        pdf_path = BOOK_PDF_DIR / filename
        md_path = BOOK_MD_DIR / f"{short_name}.md"
        print(f"\n=== {filename} -> {md_path.name} ===")

        results_path = run_ocr(pdf_path, args.page_range, args.force)
        title = pdf_path.stem
        md_text = results_to_md(results_path, title)
        md_path.write_text(md_text, encoding="utf-8")
        print(f"  Wrote {md_path.relative_to(ROOT)} ({md_path.stat().st_size // 1024} KB)")

    print("\nAll books converted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
