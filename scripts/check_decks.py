"""Check the TSV decks in anki/ for duplicates and structural problems.

Run before building, or let build_anki_decks.py run it for you.

Two distinct failure modes, both invisible in Anki itself:

* **Duplicate** — the same word carded twice, so it gets reviewed twice forever.
  Anki can't warn us, because a note's GUID includes its deck name and the two
  copies are separate notes as far as it is concerned.
* **GUID collision** — two *different* words in the same deck whose spellings
  differ only in the marks the GUID rule strips (درس lesson vs درّس to teach).
  They hash to one GUID, so importing silently keeps only one of them.

    .venv/bin/python scripts/check_decks.py
"""

import collections
import csv
import pathlib
import re
import sys

# Everything build_anki_decks.py strips before hashing a note's GUID.
GUID_STRIPPED = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
# The same, but keeping shadda, which distinguishes real words from each other.
SHORT_VOWELS = re.compile(r"[\u0610-\u061A\u064B-\u0650\u0652-\u065F\u0670\u06D6-\u06ED\u0640]")

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANKI_DIR = ROOT / "anki"

# filename -> expected number of fields, excluding the trailing tags column
DECK_FIELDS = {
    "vocab-part1-lessons1-5.tsv": 6,
    "grammar-part1-lessons1-5.tsv": 4,
    "vocab-lesson-notes.tsv": 6,
    "grammar-lesson-notes.tsv": 4,
}

# Spelling variants that make one word look like two.
VARIANTS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي"})


def word_key(headword):
    """The form used to decide whether two rows are the same word.

    Short vowels are dropped, since the same word may be vowelled differently in
    two sessions, and hamza and alef-maqsura spellings are folded, so أسبوع and
    اسبوع match. Shadda is kept: it is the only thing separating some pairs.
    """
    return SHORT_VOWELS.sub("", headword).translate(VARIANTS).strip()


def guid_key(headword):
    """What the GUID is actually derived from, for collision detection."""
    return GUID_STRIPPED.sub("", headword).strip()


def read_rows(path):
    with path.open(encoding="utf-8") as fh:
        for lineno, row in enumerate(csv.reader(fh, delimiter="\t"), start=1):
            if not row or row[0].startswith("#"):
                continue
            yield lineno, row


def run():
    problems = []
    warnings = []
    by_word = collections.defaultdict(list)
    by_guid = collections.defaultdict(list)

    for filename, nfields in DECK_FIELDS.items():
        path = ANKI_DIR / filename
        if not path.exists():
            problems.append(f"{filename}: missing")
            continue
        count = 0
        for lineno, row in read_rows(path):
            count += 1
            where = f"{filename}:{lineno}"
            if len(row) != nfields + 1:
                problems.append(
                    f"{where}: expected {nfields + 1} tab-separated columns "
                    f"(including tags), got {len(row)}"
                )
                continue
            headword, tags = row[0], row[-1]
            if not headword.strip():
                problems.append(f"{where}: empty first field")
            if not tags.strip():
                problems.append(f"{where}: no tags — the row can't be studied by topic")
            for i, value in enumerate(row):
                if value != value.strip():
                    warnings.append(f"{where}: column {i + 1} has leading/trailing space")
            by_word[word_key(headword)].append((filename, lineno, headword))
            by_guid[guid_key(headword)].append((filename, lineno, headword))
        print(f"{filename}: {count} rows")

    def describe(rows):
        where = ", ".join(f"{f}:{n}" for f, n, _ in rows)
        spellings = " / ".join(sorted({h for _, _, h in rows}))
        return spellings, where

    for rows in by_word.values():
        if len(rows) > 1:
            spellings, where = describe(rows)
            problems.append(
                f"duplicate '{spellings}' in {where} — merge the meanings onto "
                f"the existing row instead of adding a second one"
            )

    for rows in by_guid.values():
        if len(rows) < 2 or len({word_key(h) for _, _, h in rows}) < 2:
            continue  # already reported as a duplicate, or not a collision
        spellings, where = describe(rows)
        decks = {f for f, _, _ in rows}
        if len(decks) == 1:
            problems.append(
                f"GUID collision '{spellings}' in {where} — different words that "
                f"differ only by marks the GUID strips, so only one would survive "
                f"the import. Respell one of them (its bare letters must differ)."
            )
        else:
            warnings.append(
                f"'{spellings}' in {where} differ only by shadda — fine in "
                f"separate decks, but confirm they really are different words"
            )

    for warning in warnings:
        print(f"warning: {warning}")
    for problem in problems:
        print(f"error: {problem}")
    if problems:
        print(f"\n{len(problems)} problem(s) — fix before building")
    else:
        print(f"\nclean: {len(by_word)} distinct headwords, no duplicates or collisions")
    return len(problems)


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
