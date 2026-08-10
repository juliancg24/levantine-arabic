# levantine-arabic

Personal workspace for learning Syrian Levantine Arabic, used alongside in-person lessons and homework. Cursor acts as a supplementary tutor in this project — see `.cursor/rules/language-learning-assistant.mdc` for its teaching style and responsibilities.

## Project Structure

- **`notes/Julian & Mona.md`** — Running lesson notes. Read at the start of every tutoring session to track what's already been covered.
- **`book-md/`** — Markdown extracts of *Fluent in Levantine Arabic* by Muna Khalil, OCR'd from the scanned PDFs. Contains lesson structure, grammar explanations, and Arabic script.
  - `fluent-in-levantine-arabic-lo.md` — Part 1 (Beginner / Low Intermediate)
  - `fluent-in-levantine-arabic-in.md` — Part 2 (Intermediate)
  - `fluent-in-levantine-arabic-ad.md` — Part 3 (Upper Intermediate / Advanced)

  Load only the relevant volume/section when needed for a given lesson — avoid loading all three at once.
- **`book-pdf/`** — Raw scanned PDFs of the same three textbook volumes. Attach a PDF directly (@-mention) when you need the original page images — e.g. to double-check vocabulary tables, conjugation grids, exercises, or to verify OCR accuracy against `book-md/`.
- **`scripts/`** — OCR/conversion tooling used to generate `book-md/` from `book-pdf/`.
  - `convert_books.py`
  - `convert_books_surya.py` — current pipeline (Surya OCR), used to extract Arabic script into `book-md/`.
- **`.ocr-raw/`, `.ocr-test/`** — scratch/working output from the OCR conversion process.
- **`.cursor/rules/language-learning-assistant.mdc`** — always-on rule defining the assistant's tutoring style, responsibilities, and session structure.

## Typical Workflow

1. At the start of a session, review `notes/Julian & Mona.md` for context on prior lessons and progress.
2. For homework help or grammar review, load the relevant `book-md/` volume for lesson content (Arabic script included).
3. If Arabic script in `book-md/` is missing, garbled, or higher fidelity is needed, attach the corresponding PDF from `book-pdf/` directly.
4. Update the lesson notes at the end of a session to keep progress tracked for next time.
