# Anki Decks — Fluent in Levantine Arabic, Part 1 (complete, Lessons 1–5)

Four importable files, all tab-separated (`.tsv`) so that commas inside the English meanings don't break anything. Two come from the textbook, two from the in-person lesson notes:

| File | Cards | Deck it creates | Source |
| --- | --- | --- | --- |
| `vocab-part1-lessons1-5.tsv` | 183 | `Levantine Arabic::Part 1 Vocab` | textbook |
| `grammar-part1-lessons1-5.tsv` | 31 | `Levantine Arabic::Part 1 Grammar` | textbook |
| `vocab-lesson-notes.tsv` | 181 | `Levantine Arabic::Lesson Notes` | class notes |
| `grammar-lesson-notes.tsv` | 14 | `Levantine Arabic::Lesson Notes Grammar` | class notes |

No word appears in more than one deck. Where the textbook and the class notes teach the same word, it lives on a single card carrying both meanings — التنين is one card reading "Monday / both", طيّب is one card reading "ok / alright / delicious / fine", من is one card reading "from / than".

Every row is tagged by lesson and topic (`L1 nouns feminine`, `L3 negation`, `L4 family`, …), so you can study one lesson at a time with a filtered deck.

## Fields

**Vocabulary** — `Arabic`, `Transliteration`, `English`, `Notes`, `Example (Arabic)`, `Example (English)`, `Tags`

`Notes` carries the gender, the feminine/plural form of an adjective, or the conjugation pattern of a verb. Examples come from the book's own sentences, exercises and listening practices.

**Grammar** — `Question`, `Rule`, `Examples`, `Watch out for`, `Tags`

## Importing: the quick way

Build a single `.apkg` and open it. The package carries the note types, the card templates, the styling and the right-to-left field settings with it, so there is no manual setup in Anki at all:

```bash
.venv/bin/pip install genanki          # once
.venv/bin/python scripts/build_anki_decks.py
```

That writes `anki/levantine-arabic.apkg` (409 notes → 773 cards). Double-click it, or **File → Import** it. The file is gitignored because it's generated — re-run the script after editing any TSV.

Note GUIDs are derived from the first field with vowel marks stripped, so rebuilding and re-importing **updates** existing cards and keeps your review history, rather than creating duplicates. Stripping the harakat first means correcting a word's vowelling — the likeliest kind of future edit — doesn't read as a brand new note.

### Never change the GUID rule again

Anki matches an incoming note to an existing one by GUID alone, so the *rule* that produces the GUID is effectively permanent once a package has been imported. Changing it re-labels every affected note as new, and Anki adds it next to the copy already in the collection.

This already cost 38 duplicates once. The first package derived GUIDs from the raw first field; the vowelling pass switched to the vowel-stripped first field. Every note whose first field was already carrying a diacritic — 34 words, mostly ones written with a shadda (`سيّارة`, `جدّ`, `ستّ`, `طيّب`, `قدّيش` …) but also a few already marked for other reasons (`شكراً`, `كيفَك`, `انتَ`) — plus 4 grammar questions that quote Arabic (`أو and ولّا`, `إيمتى and لمّا`) — hashed differently under the new rule and came in as a new note, taking the collection from 409 to 447. The other 371 matched and updated silently, which is what made the number look arbitrary.

If a rebuild ever reports notes *added* when you expected only updates, that's the symptom. The fix while review history is still young is to delete and re-import: **Browse**, select the `Levantine Arabic` deck including subdecks, select all, **Notes → Delete**, then import the `.apkg` again and confirm you land on 409 notes. Once there's real scheduling to protect, the stale copies have to be hunted individually instead — an exact field search (`Arabic:سيّارة`) matches the un-vowelled leftover but not its vowelled replacement.

The vocabulary note type generates two cards per word: recognition (Arabic → English) and production (English → Arabic). Production is where gender and possessive endings really get tested, but it doubles the queue, so if you'd rather ease in: **Browse**, search `card:Production`, select all, **Suspend**. Unsuspend a tag at a time as recognition becomes automatic.

## Syncing to your phone

Import on the desktop, then press **Sync** and log in to a free ankiweb.net account. Install AnkiDroid (Android, free) or AnkiMobile (iOS, paid) and sync there with the same account. Note types, templates, RTL settings and review history all travel with the collection.

One caveat: on the *first* sync, if both sides hold data, Anki cannot merge and makes you pick a direction — the losing side is overwritten. Sync the desktop first while the phone is still empty and choose **Upload to AnkiWeb**. After that, syncing is incremental and safe both ways. Import the `.apkg` on one device only and let sync carry it to the other.

## Importing: the manual way

If you'd rather not run the script, import the TSVs directly. This needs the note types built by hand first, because Anki's built-in "Basic" type has only two fields and would discard most of each row.

### Step 1 — Create the two note types

Anki's built-in "Basic" note type only has two fields, so it would throw away most of each row. Create a note type per deck once:

1. **Tools → Manage Note Types → Add → Clone: Basic → OK**, name it `Levantine Vocab`.
2. Select it, click **Fields**, and add fields until the list reads exactly, in this order: `Arabic`, `Transliteration`, `English`, `Notes`, `Example (Arabic)`, `Example (English)`. (Rename `Front` to `Arabic` and `Back` to `Transliteration`, then add the rest.) Check **Right to left** for `Arabic` and `Example (Arabic)`.
3. Click **Cards** and set the templates:

Front:

```
<div class="ar">{{Arabic}}</div>
```

Back:

```
{{FrontSide}}
<hr id=answer>
<div class="translit">{{Transliteration}}</div>
<div class="en">{{English}}</div>
<div class="notes">{{Notes}}</div>
{{#Example (Arabic)}}<div class="ar ex">{{Example (Arabic)}}</div>{{/Example (Arabic)}}
<div class="notes">{{Example (English)}}</div>
```

Styling:

```
.card { font-family: -apple-system, Helvetica, sans-serif; font-size: 22px; text-align: center; color: #222; background: #fff; }
.ar { font-size: 44px; direction: rtl; }
.ar.ex { font-size: 30px; margin-top: 14px; }
.translit { color: #0a6; font-style: italic; }
.en { font-size: 28px; margin: 6px 0; }
.notes { font-size: 17px; color: #777; }
```

4. Repeat for a note type named `Levantine Grammar` with fields `Question`, `Rule`, `Examples`, `Watch out for` (front = `{{Question}}`, back = the other three).

If you'd rather not build card templates, you can skip step 1 and just map every column onto a note type that has enough fields — but the reversed and RTL styling above is what makes these actually pleasant to review.

### Step 2 — Import

1. In Anki: **File → Import**, pick `vocab-part1-lessons1-5.tsv`.
2. The file's header lines already tell Anki the separator (tab), the note type, the target deck, the column names, and that column 7 is the tags column — so the import screen should be pre-filled. Confirm that:
   - **Notetype** = `Levantine Vocab`, **Deck** = `Levantine Arabic::Part 1 Vocab`
   - Each column maps to the field of the same name, and column 7 maps to **Tags**
   - **Existing notes** = *Update* (so re-importing a corrected file overwrites instead of duplicating)
   - **Allow HTML in fields** = off
3. Click **Import**. Repeat for the other three files. `vocab-lesson-notes.tsv` uses the same `Levantine Vocab` note type as the textbook vocabulary, and `grammar-lesson-notes.tsv` the same `Levantine Grammar` one, so you only ever build the two note types once.

The first field (`Arabic` / `Question`) is what Anki uses to detect duplicates, so re-importing after I fix a typo elsewhere in a row will update that note rather than create a second one.

## Study one lesson at a time

Rather than dumping all 409 cards on yourself at once, use **Tools → Create Filtered Deck** with a search like:

```
deck:"Levantine Arabic::Part 1 Vocab" tag:L1
```

Sensible sequence: `L1` nouns and adjectives first, then `L1 made-up-verbs`, then `L2 verbs` and `L2 places`, then `L3 feelings`, then `L4 family`, then `L5 conjunctions` and `L5 modals`. The `L5 reading` tag holds the words that only appear in the Reading Practice dialogue at the end of Part 1 — useful conversational filler (`طيّب`, `يلّا`, `أكيد`, `يا ريت`) but lower priority than the lesson vocabulary proper. Do the grammar deck for a lesson only after the vocabulary of that lesson feels automatic — the grammar cards assume you know the words in their examples.

For the vocabulary deck it's worth also enabling a reverse card (English → Arabic) once recognition is solid; production is where the gender and possessive endings actually get tested.

## Editing in a spreadsheet

Both files open directly in Excel, Numbers or Google Sheets (**File → Import → Tab-separated**). The five lines starting with `#` at the top are Anki import directives — leave them in place and don't sort them away, and re-export as tab-separated when you're done.

## Coverage check

Coverage was verified mechanically, not by eye: every Arabic token in lessons 1–5 and in the answer key was extracted, stripped of vowel marks, and matched against the deck allowing for prefixes (ال، ب، ع، عال، بال) and possessive/verbal suffixes. Of 531 distinct tokens in the lessons, everything now resolves to a card except three groups, all deliberate:

- **Proper nouns** — the people in the exercises (رامي، سلمى، سيف، فرح، توم …) and place names used only once (لوس أنجيلوس، ديزني لاند، شط فينيس).
- **OCR corruption** in `book-md/` — e.g. `عالكتبة` for عالمكتبة, `مسوط` for مبسوط, `استتى` for استنّى, `نلدرس`, `تمكو`, `مورخيصة`, `ايتي` for ايمتى. These are extraction errors, not words.
- **Numbers** — تلاتة، سبع، طعشر، عشرين appear only incidentally inside lesson 4's listening answers (ages and years). Part 1 never teaches numbers in a vocabulary table, so they are not in the textbook deck; they are in `vocab-lesson-notes.tsv` instead, where the lessons teach them properly.

Exercise-instruction wording (املأ الفراغات التالية حسب النص) is also omitted deliberately — worth recognising, not worth drilling.

## The lesson-notes decks

`vocab-lesson-notes.tsv` and `grammar-lesson-notes.tsv` are built from `notes/Julian & Mona.md` — the running notes from the in-person lessons with Tarek, covering sessions from 29.11.2025 to 29.06.2026. They are kept separate from the textbook decks because they follow the lessons' own sequence and go well beyond Part 1.

They cover what the book never introduces: the full greetings and farewells set, numbers from zero to a hundred with the counting rules, nationalities, demonstratives beyond هادا (هدول، هداك، هديك، هدوك), the future marker رح, comparatives and superlatives, object pronouns, مشان, active participles, time units, and the two situational vocabulary sets from the role-play dialogues (the restaurant and the grocery store). Tagging here is by topic rather than lesson — `greetings`, `numbers`, `comparatives`, `restaurant`, `grocery`, `object-pronouns` and so on.

### The one conflict, on a single card

The lessons and the book disagree on the third-person possessive endings, and both are correct Levantine:

| | Damascene (in class) | book |
| --- | --- | --- |
| his house | بيتو | بيته |
| her house | بيتا | بيتها |
| their house | بيتُن | بيتهن |

The same split runs through عندو/عنده، معو/معه، بدّو/بدّه. Rather than two competing cards, the possessive-endings card in `grammar-part1-lessons1-5.tsv` teaches both variants side by side and labels which is which (tagged `lesson-vs-book`). Pick one for your own speech — the Damascene forms, since that's what you hear in class — and recognise the other.

## Source and caveats

Everything is drawn from `book-md/fluent-in-levantine-arabic-lo.md` — all five lessons of Part 1 (pages 6–70), including the vocabulary and grammar builders, the exercises, the listening practices, the Further Study sections, and the closing Reading Practice dialogue. That markdown is OCR output, so a number of words came through with wrong or excess vowel marks; I've written the standard Levantine spelling instead (for example `شنتة` rather than the OCR's `شَنَتاية`, `مبسوط` rather than `مَسوط`, `سينما` rather than `سِيْمًا`).

**On the harakat.** The vowel marks — on headwords and on every example sentence — are *not* transcribed from the book — the OCR's diacritics were too unreliable to trust. They represent standard Damascene pronunciation, written to match the transliteration column, and they mark short vowels and shadda while leaving long vowels to carry themselves (so `كْتاب`, `قَهْوِة`, `سَيَّارَة`, and `بيت` unmarked because it has nothing to mark). The book itself vowels only lightly and selectively — its printed page gives `صْغير`, `قَديم`, `حِلو` but leaves `كبير`, `جديد`, `غالي` bare — so these decks are more fully marked than the source. Worth a pass with Tarek; if he disagrees with a vowel, fix the TSV and rebuild, and the correction will land on the existing card without disturbing its scheduling. Transliteration follows the convention in `notes/Julian & Mona.md` — `'` for ق and ع, doubled letters for shadda. Worth spot-checking the Arabic against the PDF in `book-pdf/` with Tarek, and correcting rows in the spreadsheet before you get too many repetitions into them.
