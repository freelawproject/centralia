# CLAUDE.md

Working guide for this repo. (Skeleton drafted by Claude from the project's memory + session
history — review and adjust freely.)

---

## What this is

`centralia` is a juriscraper-style, extensible tool that parses **digital** court PDFs into a
structured `ExtractedDocument` and renders it (review HTML, Harvard casebody XML). It identifies
opinions and their authors, headmatter, headnotes/syllabus, blockquotes, footnotes, signatures,
and page furniture (stamps, running heads, page numbers, seals).

It is a clean reimplementation of the extraction core from the older `ca1` project — the
standalone `casebody/` guts (subclass-per-court), **not** the Django-coupled extractor. Extraction
returns a dataclass, not XML; rendering is a separate concern.

Parsing is driven by **document structure** — margins, x-position, bold/italic, font size,
centering, line spacing, drawn rules and glyph rails — **not** by regex over the text.

---

## Core principles (these are load-bearing — the user cares a lot)

1. **Structure over regex.** Prefer geometry/font/position/string-prefix cues. Regex "feels like a
   smell." The *only* sanctioned regex is the author-byline grammar in `base.py` (`_author_pattern`);
   per-court files should be regex-free.
2. **Completeness — return everything.** Every source line must land somewhere: opinion body,
   headmatter, headnotes/syllabus, footnotes, `dropped`, `signature`, or `trailer`. Never silently
   cut signature blocks, "WE CONCUR:" rosters, panels, or counsel — capture them read-only.
   `audit.py` proves this line-by-line; aim for 100% (some courts have small known residuals).
3. **Drop only identified junk**, and surface it. Notices, running headers, page numbers, bates
   stamps, seals, margin content → `dropped` (the "Removed" box), never silently discarded.
4. **Per-court isolation.** A court's quirks live in its own file so tuning one can't regress
   another. Shared behavior lives in a family base. `akd.py` and `ncwd.py` are good models for
   per-court overrides; `delaware.py` is the model for orders.
4a. **Correctness first; reusability is preferred but not required.** Fine-tune the code until it
   works *no matter what* on the court in front of you — getting it right beats keeping it generic.
   Reach for a shared base / generalizable pattern when it fits cleanly (it's the nicer outcome),
   but if a court's format demands a specific, court-local solution, write that; don't contort it to
   be reusable at the cost of correctness or clarity. Lift something into a family base only once a
   second court actually needs it.
5. **Never invent layout.** Render dividers/rails/rules *only as the PDF draws them* — a glyph rail
   → stacked glyphs, a drawn rule → a border, whitespace → nothing. Don't add a line that wasn't
   there; don't add a trailing line at the end of headmatter.
6. **Styled headmatter is the default — respect the page's formatting.** Reproduce the caption's
   look *extracted* (not a positional facsimile image):
   - **Alignment per line:** left stays left, **centered** stays centered, **right** stays right.
     Watch for captions centered on their own column axis rather than the page center
     (right-shifted captions like Maryland) — center relative to the caption block, not the page.
   - **Bold/italic** are preserved inline (`<strong>`/`<em>`) — bold banner rows, bold disposition
     lines, italic notices.
   - **Whitespace & spacing** carry meaning: keep the vertical rhythm (blank rows for real gaps),
     and keep two-column caption columns aligned. Don't collapse intentional spacing and don't add
     spacing that isn't there.
7. **Group what belongs together — take your time here.** Content that is one logical unit must come
   out as one unit, not fragmented line-by-line:
   - **Blockquotes** — consecutive both-margins-indented, single-spaced lines are one blockquote
     (geometry, not punctuation).
   - **Multi-line bold headers / dispositions** — a bold heading that wraps to a second row
     (`Tenn. R. App. P. 3 … and Remanded`, section heads, `CRIMINAL LAW – MISTRIAL – …` headnote
     topics) is one heading, joined — never split mid-phrase.
   - **Wrapped party names / bylines / counsel blocks** — fold continuations into their column or
     byline; don't orphan the second line.
   - **Paragraphs** — join wrapped lines into a paragraph; a footnote marker or page break must not
     break a paragraph.
   This grouping is where care pays off; rushing it produces output that "looks complete" but reads
   broken.
8. **Honesty about status.** Verify EVERY file before calling a court done. Label partial work
   PARTIAL; don't bury misses.

> **Roadmap:** improve the per-document **fingerprint** at the top of each review page — richer,
> more accurate structural parsing (caption style, sections present, opinion/writing breakdown,
> furniture detected) so the fingerprint becomes a trustworthy at-a-glance summary of how the
> document was understood. See `captionfp.py` (caption side) and `render/html.py` `_render_fingerprint`.

---

## Architecture

```
centralia/
  base.py            # BaseExtractor: the pipeline + the one allowed regex (byline grammar)
  models.py          # ExtractedDocument contract (the section model)
  registry.py        # EXTRACTORS dict — every court id → class
  captionfp.py       # page-1 caption fingerprint: geometry signature → catalog style
  audit.py           # per-source-line coverage proof
  cli.py             # `python -m centralia.cli ...`
  render/
    html.py          # review HTML + fingerprint chip
    casebody.py      # Harvard casebody XML
  courts/
    _statesupreme.py, _abbrevtitle.py, _reversedjustice.py,  # family bases (state high courts)
    _district.py, _circuit.py, _alabama.py, _alaska.py, ...  # other family bases
    <id>.py          # ~200 thin per-court classes, e.g. md.py, sd.py, ncwd.py
library/, webconfig/ # Django review viewer (see below)
assets/<court>/      # input PDF corpora (gitignored)
output/<court>/      # generated review HTML
tests/inspect.py     # the PDF inspection lens
```

**Pipeline** (in `base.py`): `page_lines` → `segment_lines` → `classify_segment`
(notice / blockquote / body / single / spaced) → `find_authors` → `build_opinion` →
`build_footnotes`. Headmatter = the segments before the first opinion start.

**Adding/refining a court:**
1. Inspect a sample (`tests/inspect.py <name> --geom`) — fonts, x-positions, drawn rules, byline.
2. Pick the family base whose byline/caption archetype matches; subclass it; override only the deltas.
3. Register in `registry.py` (import + `EXTRACTORS["<id>"]`).
4. Regenerate + audit; eyeball the review HTML; confirm every region is accounted for.

---

## The section model (`ExtractedDocument`)

Order as rendered: **headmatter → headnotes → syllabus → opinions → signature → trailer**, plus
`dropped` (the "Removed" box) shown up top.

| field | what it holds |
|---|---|
| `summary` (headmatter) | styled caption rows: `{__hm__, html, rel, align}`, `__caption__` two-column blocks (`left`/`right`/`rail`/`shape`), `__DIVIDER__`, `__RULE__`, `''` gaps |
| `headnotes` | reporter headnotes preceding the opinion (Maryland) — bold topical headings + prose |
| `syllabus` | court-written case summary (Colorado SUMMARY, Connecticut Syllabus, SCOTUS) |
| `opinions[]` | each: `type` (majority/concurrence/dissent/order/…), `author`, `blocks[]`, `footnotes[]` |
| `signature` | `/s/` conformed signature, printed name, title, or signature image — lifted off the opinion end |
| `dropped` | notices, stamps, seals, running furniture — surfaced, not body |
| `trailer` | trailing counsel/addresses after the last opinion |
| `caption_box` | page-1 caption geometry + `fp_id`/`fp_style` from the fingerprint |

> **Adding a new section field is a 7-place change** (learned the hard way): `models.py`,
> `render/html.py` (a `_render_*` + call site + CSS), `library/models.py` (+ a migration),
> `library/management/commands/ingest.py`, `library/views.py`, the detail template, and
> `audit.py` `_doc_chunks` — *miss the last one and the content reads as "missing" in the audit.*

---

## Dev loop

```bash
# regenerate one court's review HTML
uv run python -m centralia.cli <court> assets/<court> --html --output --index

# coverage audit (a directory, or a single PDF)
uv run python -m centralia.cli <court> assets/<court> --audit

# inspect a PDF — the primary debugging lens
uv run python tests/inspect.py <name-or-path> -p <page>   # lines: top/x0/x1/size/align/bold/font
uv run python tests/inspect.py <name-or-path> --geom      # every rect & vector line, tagged H/V/box
```

`inspect.py` resolves a bare name under `assets/`. `--geom` is how you tell a footnote separator
from a caption shelf from a box edge (each tagged with span % and page position).

---

## Review viewer (Django)

- `library/` + `webconfig/`. **Run on port 8001** (8000 is taken by another local project).
  - `uv run python manage.py runserver 8001`
- `/` serves `output/viewer.html`; `/courts/<court>/` is a rich per-court DB view.
- **Ingest** the corpus into the DB: `uv run python manage.py ingest [court ...]`
  (`--pdf <stem>` for a single document).
- **Re-run** from the viewer's `↻ re-run` button → `POST /courts/<court>/reprocess`
  (`?pdf=<stem>` to re-run one file; long-press / right-click the button for a PDF picker).
- **Review marks**: 5 tiers (nay → some → good → almost → yay ✅), per-court + per-PDF + done,
  persisted via Django `/marks` → `output/notes/_marks.json` / `_filemarks.json` / `_done.json`.
- **Sidebar groups**: `groupOf` in `output/viewer.html` and `_group` in `library/views.py`
  (District courts / Federal circuits / State courts / Misc-specialized). Keep the two in sync.

### Review marks = the worklist (use them)

The user reviews PDFs in the viewer and rates each one. These ratings are the source of truth for
what still needs work — **read them before/while working a court**, and treat the low tiers as the
to-do list.

- **`output/notes/_filemarks.json`** — **per-PDF** rating, keyed `"<court>/<stem>" → tier` where
  tier ∈ `nay` (✗ totally not working) · `some` (◔ some progress) · `good` (◑ good progress) ·
  `almost` (~ almost done) · `yay` (✅ completed). This is the granular signal: a court can be
  half-yay, half-nay. e.g. `ncmd` has 10 PDFs spread across nay/some/good/almost.
- **`output/notes/_marks.json`** — a **per-court** rating (one tier per court; set at the court
  level, coarser than the per-PDF marks — it's the sidebar chip, not a rollup of `_filemarks`).
- **`output/notes/_done.json`** — per-court "Claude-completed" flag.
- **`output/notes/<court>.md`** — the user's free-text **per-court notes** (design, quirks, what's
  broken, TODOs), one markdown file per court. **READ THIS FIRST when working a court** — it often
  contains the exact instructions/symptoms the user wants addressed. e.g. `wash.md` lists the
  GONZÁLEZ byline, "ignore margin content," "two stamps on the first page," "better headmatter,"
  "multiple opinions"; `cacd.md` says "return things in paragraph format." Notes are per-court
  (not per-PDF); the per-PDF signal is the `_filemarks.json` tier.

```bash
# the user's notes for a court — read before starting
cat output/notes/<court>.md
```

Quick ways to read them:
```bash
# per-PDF tiers for one court
python3 -c "import json;d=json.load(open('output/notes/_filemarks.json'));[print(v,k) for k,v in d.items() if k.startswith('ncmd/')]"
# everything still failing (the nay list), corpus-wide
python3 -c "import json;d=json.load(open('output/notes/_filemarks.json'));[print(k) for k,v in d.items() if v=='nay']"
```

When the user says "fix court X" or "work the nay files," pull the `nay`/`some` entries for that
court from `_filemarks.json` and use them as the diagnose-and-fix queue; re-run those specific PDFs
(`reprocess?pdf=<stem>`) as you go. Don't overwrite a user's `yay` with regressions — re-audit the
already-good files after changes.

---

## Byline families (state high courts)

Pick the base that matches the court's author byline:

- **`StateSupreme`** — bold ALL-CAPS `LASTNAME, Justice.` / colon / `PER CURIAM`
  (ariz, ark, fla, ga, nc, sd, …). Note: the byline grammar's title prefixes are
  `Chief/Presiding/Associate/Senior/Retired/Acting` + the base title word.
- **`AbbrevTitleSupreme`** — abbreviated title `NAME, J.` / `C.J.` / `J.P.T.`
  (mass, conn, kan colon-form, tenn `accept_delivered`, vt/wis `strip_para_marker`,
  neb `allow_titlecase_name`, wash em-dash, md `Opinion by NAME, C.J.` caption-prefix).
- **`ReversedJusticeSupreme`** — title-first (`JUSTICE JAMES: …`, nj/tex `…delivered…`, pa `DECIDED:`).
- **Custom** parser in the court file when none fit (mont, ky, miss, dc, ri, va).

Common knobs: `require_bold_byline`, `accept_delivered`, `strip_para_marker`,
`allow_titlecase_name`, `abbrev_titles`, `title_suffixes`.

---

## Caption fingerprint & catalog

`captionfp.py` measures one **geometric signature** of page 1 (tall verticals left/mid/right,
horizontal rules by span full/left/right and position top/bottom, glyph rails, diagonals, pleading
gutter, flush-right zones) and runs it through one ordered `_MATRIX` of predicates → a catalog
**style name**. The renderer draws borders from the *same* signature, so the label and the
reproduction can't disagree. Styles are catalogued (with ASCII art) in `library/caption_catalog.py`
and browsable at `/captions`. A few of the distinctive ones:

**Old Faithful** — one mid vertical, a half-rule closing into it at the corner:
```
            UNITED STATES DISTRICT COURT
   JANE DOE,                       │
            Plaintiff,             │   No. 2:24-cv-01234
       v.                          │   ORDER
   ACME CORPORATION,               │
            Defendant.             │
   ---------------------------------┘
```

**The Parenthetical Box / Banded Bracket** — a `)` glyph rail down the middle:
```
   TYLER HOOD,            )
            Plaintiff,    )
   v.                     )   MEMORANDUM & ORDER
   CAPSTONE LOGISTICS,    )
            Defendant.    )
```

**The Double Box** — verticals at both edges + middle, closed top & bottom.
**The I-Beam** — mid vertical, full rule top AND bottom. **The Upside-Down T** — mid vertical, full
rule only on the bottom. **The Backwards C** — mid vertical, left/full top & bottom, no left edge.
**The Twin Rail** — two mid verticals ~1–2pt apart. **The X-Capped Pleading Box** — diagonals
capping the box. **The Section-Sign / Square-Bracket / Asterisk rails** — `§` / `]` / `*` glyph
columns. **The Flush-Right Status** — nothing drawn; status labels pinned at the right margin
(`PLAINTIFF`/`APPELLEE`). **The Open Range** — two columns held by whitespace alone.

When a court's caption is mis-identified, the fix is usually a facet in `caption_signature` (a new
measurement) + one `_MATRIX` row — and an entry in `caption_catalog.py`. Keep the exemplar test set
green when you touch it.

---

## Gotchas / hard-won lessons

- **Caption boxes drawn in pieces.** Collect thin rule segments small, merge by y, *then*
  size-filter — a full-width rule drawn as short strips otherwise reads as two disjoint halves.
- **Footnote separator vs caption shelf.** The robust discriminator is *footnote-sized text directly
  below the rule* (a caption shelf has body-size text below it). Don't key on width/position alone.
- **Right-shifted captions** (Maryland) center on their own column axis, not the page center —
  compute the axis (e.g. from the caption's underscore divider) before deciding alignment.
- **Wrapped bylines** ("Concurring and Dissenting Opinion by" / name on the next line) need the two
  lines joined before parsing.
- **Interleaved columns / italic baselines.** pdfplumber can merge two visual columns onto one line
  (same top) or split an italic run onto its own offset baseline — handle via x-gap run-splitting
  and baseline merging, not text heuristics.
- **Ligatures & nbsp** in source text break naive matching — normalize (`ﬀ`→`ff`, `\xa0`→space).
- **Alabama is fidelity-locked** — byte-identical to the old ca1/casebody. Don't change shared base
  behavior in ways that move Alabama's output.

---

## Memory

Durable project notes live under `~/.claude/projects/<this-repo>/memory/` — `MEMORY.md` (index) plus
per-topic files: `centralia-architecture`, `state-supreme-courts`, `district-courts`,
`caption-styles-catalog`, `extraction-principles`, `no-regex-preference`, `resolution-honesty`,
`django-viewer-app`. Check there for the per-court quirk history before diving in.
