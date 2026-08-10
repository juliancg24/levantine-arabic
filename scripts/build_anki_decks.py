"""Build a single .apkg from the TSV decks in anki/.

The .apkg carries the note types, right-to-left settings and card styling with
it, so importing it needs no manual setup in Anki. Re-run after editing any
TSV; note GUIDs are derived from the first field, so a re-import updates
existing cards instead of duplicating them.

    .venv/bin/python scripts/build_anki_decks.py
"""

import csv
import pathlib
import re
import sys

import genanki

# Vowel marks are the field most likely to be corrected later, so they are
# stripped before deriving a note's GUID — otherwise re-vowelling a word would
# look like a brand new note and duplicate the card.
HARAKAT = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANKI_DIR = ROOT / "anki"
OUT = ANKI_DIR / "levantine-arabic.apkg"

# Fixed IDs so that re-importing updates the same decks and note types
# rather than creating parallel copies.
VOCAB_MODEL_ID = 1607392319
GRAMMAR_MODEL_ID = 1607392320

CSS = """
.card {
  font-family: -apple-system, Helvetica, sans-serif;
  font-size: 22px;
  text-align: center;
  color: #222;
  background: #fff;
  padding: 18px;
}
.ar { font-size: 44px; direction: rtl; line-height: 1.5; }
.ar.ex { font-size: 30px; margin-top: 14px; }
.translit { color: #0a8060; font-style: italic; margin-top: 4px; }
.en { font-size: 28px; margin: 8px 0; }
.notes { font-size: 16px; color: #777; margin-top: 6px; }
.q { font-size: 26px; }
.rule { font-size: 21px; margin: 10px 0; text-align: left; }
.examples { font-size: 21px; direction: rtl; text-align: right; margin: 10px 0; }
.warn { font-size: 17px; color: #b05000; text-align: left; margin-top: 12px; }
hr#answer { margin: 16px 0; }
"""

VOCAB_MODEL = genanki.Model(
    VOCAB_MODEL_ID,
    "Levantine Vocab",
    fields=[
        {"name": "Arabic", "rtl": True},
        {"name": "Transliteration"},
        {"name": "English"},
        {"name": "Notes"},
        {"name": "Example (Arabic)", "rtl": True},
        {"name": "Example (English)"},
    ],
    templates=[
        {
            "name": "Recognition",
            "qfmt": '<div class="ar">{{Arabic}}</div>',
            "afmt": """{{FrontSide}}
<hr id=answer>
<div class="translit">{{Transliteration}}</div>
<div class="en">{{English}}</div>
{{#Notes}}<div class="notes">{{Notes}}</div>{{/Notes}}
{{#Example (Arabic)}}<div class="ar ex">{{Example (Arabic)}}</div>{{/Example (Arabic)}}
{{#Example (English)}}<div class="notes">{{Example (English)}}</div>{{/Example (English)}}""",
        },
        {
            "name": "Production",
            "qfmt": '<div class="en">{{English}}</div>{{#Notes}}<div class="notes">{{Notes}}</div>{{/Notes}}',
            "afmt": """{{FrontSide}}
<hr id=answer>
<div class="ar">{{Arabic}}</div>
<div class="translit">{{Transliteration}}</div>
{{#Example (Arabic)}}<div class="ar ex">{{Example (Arabic)}}</div>{{/Example (Arabic)}}""",
        },
    ],
    css=CSS,
)

GRAMMAR_MODEL = genanki.Model(
    GRAMMAR_MODEL_ID,
    "Levantine Grammar",
    fields=[
        {"name": "Question"},
        {"name": "Rule"},
        {"name": "Examples", "rtl": True},
        {"name": "Watch out for"},
    ],
    templates=[
        {
            "name": "Rule",
            "qfmt": '<div class="q">{{Question}}</div>',
            "afmt": """{{FrontSide}}
<hr id=answer>
<div class="rule">{{Rule}}</div>
{{#Examples}}<div class="examples">{{Examples}}</div>{{/Examples}}
{{#Watch out for}}<div class="warn">{{Watch out for}}</div>{{/Watch out for}}""",
        }
    ],
    css=CSS,
)

# tsv filename -> (deck id, deck name, model)
DECKS = [
    ("vocab-part1-lessons1-5.tsv", 2081234501, "Levantine Arabic::Part 1 Vocab", VOCAB_MODEL),
    ("grammar-part1-lessons1-5.tsv", 2081234502, "Levantine Arabic::Part 1 Grammar", GRAMMAR_MODEL),
    ("vocab-lesson-notes.tsv", 2081234503, "Levantine Arabic::Lesson Notes", VOCAB_MODEL),
    ("grammar-lesson-notes.tsv", 2081234504, "Levantine Arabic::Lesson Notes Grammar", GRAMMAR_MODEL),
]


def read_rows(path):
    """Yield (fields, tags) from a TSV, skipping the # directive header."""
    with path.open(encoding="utf-8") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if not row or row[0].startswith("#"):
                continue
            yield row[:-1], row[-1].split()


def main():
    decks = []
    total = 0
    for filename, deck_id, deck_name, model in DECKS:
        path = ANKI_DIR / filename
        deck = genanki.Deck(deck_id, deck_name)
        expected = len(model.fields)
        for fields, tags in read_rows(path):
            if len(fields) != expected:
                sys.exit(f"{filename}: expected {expected} fields, got {len(fields)}: {fields[:1]}")
            deck.add_note(
                genanki.Note(
                    model=model,
                    fields=fields,
                    tags=tags,
                    # Stable per-word GUID keeps re-imports as updates.
                    guid=genanki.guid_for(deck_name, HARAKAT.sub("", fields[0])),
                )
            )
        print(f"{deck_name}: {len(deck.notes)} notes")
        total += len(deck.notes)
        decks.append(deck)

    genanki.Package(decks).write_to_file(OUT)
    print(f"\n{total} notes written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
