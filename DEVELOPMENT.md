# centralia v2 — how it works, why it works that way, and what is left

A developer's orientation. Read this before the code; it exists so that the
code's thousands of comment-lines of rationale have somewhere to hang.

---

## 1. What this is

**A court PDF and a court id in; a typed, structured opinion out.**

```python
from centralia import read
r = read("opinion.pdf", court_id="mont")
```

The hard part is not "get the text out of a PDF" — `pdftotext` does that. The
hard part is that a court opinion is a *document with parts*, and the PDF says
nothing about them. There is no tag that means "this is the syllabus", "this
paragraph belongs to the dissent", "this footnote is Justice Kagan's", "this
line is a page number and not a sentence". Every one of those has to be
recovered from how the page is *set* — position, size, leading, indentation,
what the printer drew.

There are 241 courts in the corpus and each one sets its pages differently.

### What v1 was, and why v2 exists

v1 worked — it parsed most courts correctly, and its output is frozen under
`baseline/` and still used as an oracle. But it grew as an inheritance tree:
`_AlaFamily` overrode `_StateSupreme` overrode a base class, with 111 profile
knobs read at 25 different sites. Answering "who decided this line?" meant a
debugger. A fix for one court silently moved another.

v2 keeps v1's hard-won *knowledge* and throws away its *structure*. The rewrite
is not a rewrite of what the readers know; it is a rewrite of where that
knowledge is allowed to live.

---

## 2. Getting set up

Python 3.12+. The repo is `uv`-based, which is what CI uses:

```sh
uv sync --dev                             # deps, from uv.lock
uv run python scripts/fetch_corpus.py     # the test corpus: ~10,000 PDFs, 3.1 GB
uv run python harness/cli.py render ala   # render one court
uv run python harness/cli.py serve        # the review viewer, port 8002
uv run pytest -q                          # the suite
```

The only runtime dependency is `pdfplumber`. Everything else — the harness, the
viewer, the oracles — is standard library.

**The harness commands**, none of which ever run automatically:

| command | what it does |
|---|---|
| `render <court>` | run the pipeline and write the review HTML |
| `serve [port]` | the review viewer (§9) |
| `guard [court…]` | check every pinned sentinel (`--bless`, `--add`, `--prune`) |
| `quality [court…]` | mechanical defect grades from the emitted HTML |
| `coverage [court…]` | content-loss reconciliation against `pdftotext` |
| `v1diff [court…]` | diff v2 against the frozen v1 baseline |
| `audit [court…]` | the coverage/correctness gates |
| `lines <court/stem>` | the PDF lens — what the reader actually sees on a page |
| `extract`, `render`, `clview` | run the pipeline; emit the review sheet or the CourtListener view |
| `footnotes`, `fngaps` | footnote zones, and the census of gaps in them |
| `notes [court…]` | per-file review notes |
| `released --write` | regenerate `centralia/released.py` from the marks |
| `freeze <court>` | freeze a v1 baseline for A/B (runs under the old repo's env) |
| `compare`, `identity`, `truth` | A/B against a frozen baseline; old-vs-old sanity; truth-set stats |

That is the complete list (`harness/cli.py`, `COMMANDS`). Note that **`trace`
is referenced in several docstrings but is not implemented** — see §13.

### First run, in order

```sh
uv sync --dev
uv run python scripts/fetch_corpus.py               # 1. the PDFs (~3 GB, slow)
uv run python harness/cli.py render $(ls assets)    # 2. render every court
uv run python harness/cli.py quality                # 3. the grades
uv run python harness/cli.py serve                  # 4. the viewer, port 8002
```

Step 2 is the one that is easy to get wrong. **Do not reach for
`harness/rerender.sh` to bootstrap** — it loops over `ls output`, and a fresh
clone has no rendered courts yet, so it renders nothing and exits cleanly as
though it had done the work. It is for *re*-rendering an already-populated
tree. `render` itself refuses to run with no court named, for the same reason.

Step 3 is optional but cheap (seconds — it reads the emitted HTML, not the
PDFs). Without it the viewer simply shows no grades; `/api/quality` returns
`{}` and the page degrades rather than breaking. Same for `coverage`, which is
slower because it shells out to `pdftotext` per file.

**You do not have to re-review anything.** `output/notes/marks.json` is tracked
— 9,829 verdicts (9,689 `yay`, 139 `nay`, 1 `good`, and 520 files not yet
reviewed) travel with the clone. That is the whole reason `.gitignore` excludes
`output/*` but keeps `output/notes/`: renders are rebuildable, judgments are
not. `tests/fixtures/guard.json` (739 sentinels) ships too, so the guard works
immediately.

If you want a smaller, known-good corpus, `fetch_corpus.py --approved` pulls
only the 9,408 files that are signed off. `--list` shows the split per court:

```
  ilcd    42 present, 0 missing,   7 signed off  28 MARKED BAD
```

**The corpus is not in git.** `assets/` is 10,349 court PDFs and 3.1 GB. They
all came from CourtListener and are public there, so `scripts/corpus.txt`
carries one URL per file and `fetch_corpus.py` replays it. No credentials
needed — storage is public. Rebuilding the manifest (`build_corpus_manifest.py`)
needs a `CL_API_TOKEN`; downloading does not.

Storage rate-limits by IP. A fresh clone pulling ten thousand files *will* be
throttled; both scripts back off and retry rather than treating a 429 as a
missing file. Re-running skips what is already on disk.

---

## 3. The five ideas

Almost every design decision in the codebase follows from one of these. If you
understand these, the code stops looking arbitrary.

### 3.1 Measure the document; never configure the threshold

The oldest bug in this domain is the tuned constant. "A blockquote is indented
more than 30 points" is true for one court's typesetting and false for the next,
and when it is false it is *catastrophically* false — a court whose body column
sits further right reads as indented on both margins, so the entire opinion
classifies as one long quotation.

So thresholds are **measured from the document's own geometry**
(`centralia/geometry.py`). The body column is measured from the lines that run
to the full measure — wrapped continuation lines, the one population guaranteed
to sit on the true margin. Paragraph gaps derive from the document's own
dominant leading (0.45 / 0.85 / 1.5 × lead), not from fixed point values.

The rule, stated in `resolve/evidence.py`:

> Thresholds come from measured `DocGeometry`; profile constants only clamp.
> **No evidence → the floor, unchanged.**

That last clause matters more than it looks. When measurement fails, the code
returns the conservative floor. It does *not* fall back to an estimate — an
estimated threshold inverts on degenerate input and produces confident nonsense.

### 3.2 Nothing leaves the PDF silently

Every line removed from the output is recorded, with its page and bounding box,
as `Dropped` — running heads, folios, e-filing stamps, chambers letterhead,
caption-box graphics. Anything the pipeline could not place is `residual`.

This turns "did we lose something?" from a judgment call into arithmetic.
`harness coverage` compares the PDF's own text layer (via `pdftotext`, an
*independent* oracle — deliberately not the pipeline's own reading) against
everything the pipeline accounted for: rendered text **plus** the dropped and
residual boxes. Words the PDF has that nothing accounts for are the loss.

The guarantee is *"nothing vanishes unexplained"*, not *"nothing is removed"*.

There is a trap here worth knowing: coverage and correctness are **two
different counters**. A change can drive missing-words to zero by dumping page
furniture into the body. Coverage reads clean; the document is worse. Always
read both.

### 3.3 Evidence chains, not conditionals

Hard decisions — where does the footnote zone start, who wrote this section,
where does the headmatter end — are **named decision points** owned by exactly
one core resolver. Each runs an ordered chain of evidence steps, and records
which step fired plus the full chain. `harness trace` replays it.

The footnote resolver is the showcase, because in v1 this single problem
consumed roughly a quarter of all commits as scattered per-court patches. In v2
it is one file with one ordered chain:

```
configured-rect > provider candidates > structural > rule-over-smaller-text
> rule-over-labelled-note > typed-text-rule > zone-by-size (opt-in)
> indented-rule > learned-signature > tighter-leading > no-zone (floor)
```

Plus **core-owned vetoes** that apply to every candidate no matter who proposed
it: an underline is not a separator; the caption shelf is not a separator; a box
edge sharing a row with another rule is not a separator. And a floor that
refuses to guess: nothing may invent a zone without a separator.

A court can *contribute* evidence. A court can never *decide* on its own — and
specifically can never decide "there is none", because absence of evidence is
not evidence.

### 3.4 Courts are data, not code

A `CourtProfile` (`centralia/profile.py`) is frozen and holds only facts: the
byline grammar this court prints, the document styles it publishes, whether its
captions wrap, its paragraph indent, whether counsel appear after the writings.
Unknown fields are a construction error, so v1's knob sprawl cannot regrow.

Where a court genuinely needs code, it gets **one flat file**,
`centralia/courts/<court>.py`, and the rule is enforced mechanically: *a court
file may import core, and never another court file.* No families, no mixins, no
subclassing. That import restriction is what makes "nothing overrides anything"
a guarantee instead of a habit.

There are 241 such files today, averaging ~460 lines each.

**The honest qualification.** "Courts are data" holds completely for byline
grammar, footnote configuration, declared styles, indents and front matter.
It does *not* hold for headmatter. Every one of the 241 court files registers
a `@decider("headmatter.read")`, which short-circuits core — so reading the
caption page is, in practice, per-court code. That is a deliberate choice
(caption pages are where courts genuinely differ most, and the flat-file rule
keeps each one independent), but it is worth saying plainly: **111k of the
repo's 132k lines are court files, and most of that is headmatter reading.**

Beyond headmatter, court deciders are rare — `image.role` (5 courts),
`writing.covers` (4), `syllabus.pages` (3), and a handful of singletons. The
shared engine really does carry everything else.

### 3.5 The typed model replaces sentinels

v1 signalled structure with magic strings inside text (`__DIVIDER__` and
friends). v2 makes each a real type (`centralia/model.py`), and consumers
dispatch on type.

The sharpest example: **Rule, Divider and Gap are three different things.** A
`Rule` is a line the page actually draws or types, and it renders. A `Divider`
is a semantic boundary that draws nothing. A `Gap` is vertical rhythm only.
Because they are distinct types, "never invent layout" is enforced by the type
system rather than by everyone remembering.

---

## 4. The pipeline

One fixed order, no overrides, fresh state per document
(`centralia/pipeline.py`):

```
load > triage > measure > classify > furniture > footnotes > segments
     > headmatter > body > finalize > emit
```

| stage | what it does |
|---|---|
| **load** | `pdfio` — the single pass over the PDF; the only place pdfplumber is touched |
| **triage** | scan? OCR layer? unmapped glyphs? A scan is a *success* status, never a parse failure |
| **measure** | `geometry.measure` — body column, leading, type size, from the document's own lines |
| **classify** | document type from prominent headings; matches the court's declared `DocStyle` |
| **furniture** | folios, running heads/feet, stamps, gutters — by repetition and band position |
| **footnotes** | per-page zone decision via the evidence chain above |
| **segments** | lines → typed segments (body / blockquote / notice / spaced) using measured gap bands |
| **headmatter** | caption pages → styled rows + `CaptionBlock`, and the criteria fields |
| **body** | segments + zones + bylines → writings, footnotes, signature, trailer, residual |
| **finalize** | warnings, status, diagnostics |
| **emit** | review HTML, plain HTML, Harvard casebody XML, CourtListener view |

Two things to notice. **`pdfio` runs exactly once** — there is no second parse
of any page, ever, so no two stages can disagree about what is on it. And
**`pdfio` drops nothing and cuts no margins**: removing furniture is a semantic
decision, and it belongs to a resolver that sees the same lines everyone else
does.

---

## 5. The files

### Core
| file | lines | what it is |
|---|---|---|
| `pipeline.py` | 3581 | the eleven stages; the only orchestrator |
| `model.py` | 428 | the typed document model — every v1 sentinel is a real variant |
| `geometry.py` | 138 | measured `DocGeometry`. Small, and load-bearing for everything |
| `classify.py` | 357 | triage (scan/unreadable) + document-type from headings |
| `sections.py` | 133 | the *single* section declaration; renderers and audit both iterate it |
| `profile.py` | 62 | the frozen `CourtProfile` — court facts, no behavior |
| `styles.py` | 56 | named layout contracts ("pleading paper", "engraved ladder") |
| `dates.py` | 125 | printed date → ISO, or `None`. Refuses rather than guesses |
| `audit.py` | 191 | normalization + coverage/correctness gates |
| `released.py` | 264 | generated: which courts pass the public API gate |
| `settings.py` | 45 | paths and constants |

### `pdfio/` — the one pass
| file | what it is |
|---|---|
| `build.py` | PDF → `PdfModel`. Quirk repairs, line clustering, rule collection |
| `model.py` | the line/page model everything downstream shares |
| `quirks.py` (1191) | named pdfplumber repairs, each firing a trace event |
| `text.py` | rebuilding text from chars with *measured* word breaks |
| `rules.py` | drawn-rule collection: collect small, merge by y, *then* size-filter |
| `tables.py` | ruled-table recovery — a table is proved by **ink**, never by alignment |

`text.py` exists because pdfplumber's own `line['text']` drops spaces between
kerned glyphs, rendering `DWIGHT E.TARWATER,J.,delivered`. Every consumer uses
the rebuild instead.

`tables.py` is a good illustration of the house style: pdfplumber's `find_tables`
reads an indented blockquote as a two-column table, because it guesses from text
position. What a court actually *draws* is a box with rules in it, so the reading
is taken from intersecting drawn rules and is deliberately narrow — two columns
**and** two rows, both bounded by ink. Everything else stays prose.

### `resolve/` — the decisions
| file | lines | what it decides |
|---|---|---|
| `assemble.py` | 2803 | segments + zones + bylines → writings, footnotes, trailer |
| `footnotes.py` | 1239 | the footnote-zone chain, with core vetoes |
| `headmatter.py` | 1201 | caption pages → typed rows + criteria |
| `bylines.py` | 1085 | author grammar: `prose` / `abbrev` / `reversed` + per curiam |
| `furniture.py` | 626 | what is page furniture and not content |
| `segments.py` | 381 | line grouping on measured gap bands |
| `captions.py` | 257 | page-1 caption fingerprint → catalog style |
| `evidence.py` | 157 | the decision/evidence pattern itself. **Read this first** |

### `render/`
`html.py` (the review sheet you eyeball), `facsimile.py` (headmatter reproduced
with the page's own alignment and rules), `casebody.py` (Harvard XML),
`clview.py` (what a CourtListener ingest would store — and, crucially, what
*falls on the floor* in translation), `inline.py`.

### `districts/`
`ecf.py` (3198 lines) — see §7.

---

## 6. When geometry works, and when it cannot

This is the question that decides whether a court is easy or hard.

**Geometry works when the PDF is born-digital.** The court's word processor
wrote real text with real coordinates, so position, size and leading mean what
they appear to mean. Most state appellate courts and all federal circuits are
here. This is where the engine is strong and where measurement beats
configuration outright.

**Geometry is untrustworthy on scans.** `classify.triage` catches these:
pure scans and OCR-layer scans both show `image_area > 0.85` on essentially
every page, while born-digital courts show none. An OCR text layer does **not**
make geometry trustworthy — the words may be roughly right while every
coordinate is an artifact of the scanner. So an OCR scan is extracted but
flagged `review`, and a pure scan returns `scanned`, which is a *success*
status, not a parse failure.

There is a subtlety worth knowing, because it caused 231 bad records: a
stamp-only scan accumulates text across pages (a CM/ECF header repeated down
the file), so any *total*-ink floor eventually admits it as a real document.
The measurement that separates the families cleanly is the **single richest
page** — every stamp-only scan in the corpus tops out at 141 characters, and
the thinnest real cover page carries 401. The floor sits at 250.

**Geometry is defeated by unmapped glyphs.** Some PDFs embed fonts whose
character map is broken or absent, and pdfminer yields `(cid:NN)` instead of
letters. The text layer is unreadable by *every* extractor, so these route with
the scans. One recurring family is worth knowing: a subset of documents use Mac
glyph ordering, where the true character is at `code + 29` — that repair lives
in `pdfio/quirks.py`, and the proof has to be made per document.

**Which courts are hard, concretely.** Of the 50 courts held back from the
public API, **45 are federal district courts**. The other five are `minnag`,
`nycivct`, `nysupct`, `prsupreme` and `texag`.

Being scanned does **not** by itself hold a court back. `acca` and `afcca` (the
service courts of criminal appeals) are almost entirely scans, and both are
released — because a scan returns `scanned`, which is an honest status, and a
reviewer can sign off on a document the engine correctly declines to parse.
What holds the district lane back is that its dockets carry exhibits and
third-party attachments that were never typeset by the court at all, and those
produce *wrong* readings rather than honest refusals.

Breaking the 51 down by what is actually wrong (from `output/notes/marks.json`):

| | count | meaning |
|---|---|---|
| at least one file marked `nay` | 43 | genuine defects; `ilcd` 28 of 35, `cand` 15 of 22 are the worst |
| review incomplete | 7 | e.g. `nced` 1 of 29 marked, `vawd` 4 of 42 |

Only 43 of the 50 have a *known defect*; the other 7 simply have not been read.
Those are different problems and should not be worked as one pile.

---

## 7. The three lanes

Courts do not divide evenly, and the code respects the real divisions.

**State appellate courts (~150).** Each publishes its own house style, so each
gets a profile and, where needed, a flat court file. This is the long tail and
the bulk of the per-court files.

**Federal circuits (13).** A family with real shared grammar, harvested from v1
(`notes/harvest-circuits.md`). Shared *data* by explicit reference — never
behavior by inheritance.

**Federal district courts (89).** The key insight, and it is what makes this
lane tractable at all:

> 89 district corpora are not 89 papers. They are **one** paper — the CM/ECF
> pleading order — with a handful of dividers.

Every chambers uses its own Word template, but every template prints the same
five things in the same order: the ECF overlay stamp, the masthead, the caption
band, the body, the signature. The templates differ only in **what they draw
between the caption's two columns** — and that divider is *measured*, never
read. So `districts/ecf.py` holds the paper, and a district court file exists
only to register the court and record a fact the shared reader demonstrably
cannot see.

---

## 8. How you know it is right

There is no single "is this correct" test, because correctness here is partly a
human judgment. There are five oracles, each answering a different question.

| oracle | question it answers | cost |
|---|---|---|
| `guard` | did a fix break a fix? | seconds |
| `quality` | which files show mechanical defect signals? | seconds |
| `coverage` | did anything vanish unexplained? | minutes |
| `v1diff` | where does v2 disagree with v1? | minutes |
| the viewer | is the reading actually *right*? | human |

**`guard` is the one to run after every engine change.** Every fix in this
project came from a real file; the guard pins that file's *structural
signature* — how many writings, of what kind, whether the lead is bylined,
where headmatter ends, which sections exist, which criteria were found. It
deliberately excludes prose text, because it answers "is this document still
assembled the same way", which is what fixes break.

> **The guard runs as a process pool.** Never edit source while it is running —
> the workers will mix old and new code and the verdict is meaningless.

**`quality`** reads only the emitted HTML, so grading the whole corpus takes
seconds. Its signals are exactly what a reviewer would notice: pipeline warning
chips, residual content lines (the worst signal), zero opinions, missing-space
word joins (`defendantsDennis`), hyphen-join artifacts (`pro- posed`), literal
`(cid:NN)` glyphs, no attorneys section where the text clearly has counsel.

**`v1diff`** is the cheapest source of real defects: v1 was correct on most
courts, so every disagreement is either a v2 bug or a deliberate improvement.
Ranked worst-first — opinion count (did we find the right writings?), then doc
type, then footnote labels, then section word drift.

**The viewer** (`harness/cli.py serve`, port 8002) is where a human reads the
rendered page beside the source PDF and marks it. The marks are the ground
truth that everything else defers to.

---

## 9. The viewer — where reviewing actually happens

```sh
python harness/cli.py serve      # default port 8002
```

`harness/viewer.py` is a **stdlib-only HTTP server** — no Django, no
dependencies. That is deliberate: the review tool must never be the reason the
engine cannot run.

It puts three things side by side for one document:

| pane | served from | what it shows |
|---|---|---|
| the reading | `/out/` | this repo's rendered review HTML |
| the source | `/pdf/`, `/pgimg/` | the original PDF, and rasterized page images |
| v1's reading | `/old/` | the old system's render — the A/B toggle |

Plus `/cl/`, the CourtListener view: this record as an ingest would store it,
with each field showing the value, where in our model it came from, and — where
a field cannot be filled — whether that is because *the document does not carry
it* or because *CL has nowhere to put what we have*. The second kind is a
finding, and it is drawn in red.

**Marking.** The reviewer grades each file on five tiers:

```
nay  →  some  →  good  →  almost  →  yay
```

Those marks are the project's ground truth. `released.py` is derived from them
(§11), the guard's sentinels are chosen from them, and the stale-mark check
(`/api/stale`) compares a file's current rendering against the one that was
marked — so a mark silently stops counting when the reading beneath it changes.

**The API** is small and all JSON: `/api/marks`, `/api/filenotes`,
`/api/quality`, `/api/guardreview`, `/api/stale`, `/api/manifest`,
`/api/courtmeta`, `/api/notes/<court>`. `POST /api/render` re-renders a
document from inside the viewer, so a fix can be checked without leaving it.

Two rules worth knowing:

- **The old repo's marks are never written to.** They are stale, and they are
  read-only history.
- **The reviewer's prose is private.** `marks.json` is tracked — a yay/nay is a
  verdict the guard reads, and it carries no prose. `filenotes.json` and its
  journal are gitignored: they are what the reviewer wrote to themselves, in
  their own words, and are not the repo's to publish.

---

## 10. The tests

```sh
pytest -q                                  # everything
pytest -q --ignore=tests/test_guard.py     # what CI runs
```

The suite splits along one line: **tests that need the 3 GB corpus, and tests
that do not.** `conftest.py` makes every corpus-backed test skip cleanly when
the PDFs are absent, so a fresh clone with no corpus still runs the contract
tests. CI (`.github/workflows/tests.yml`, Python 3.12 and 3.13) runs exactly
that subset, explicitly ignoring `test_guard.py`.

| file | what it holds |
|---|---|
| `test_api.py` (283) | the public contract: which keys exist, the shapes behind them, that the payload survives a JSON round trip and holds no enums or dataclasses, and that a path, raw bytes and a file object are all **the same read** |
| `test_guard.py` (88) | **739 sentinels across 111 courts**, pinned in `tests/fixtures/guard.json` — the structural signature of every file this project ever fixed |
| `test_invariants.py` (198) | one pin per specific fix, each naming the record it came from |
| `test_dates.py` (66) | the date parser must read what courts print and refuse the rest |
| `test_criteria_snapshots.py` (81) | 48 headmatter snapshots across 11 courts — **not yet an assertion**, see below |

**Why the guard is a test at all.** `harness/guard.py` could always check the
sentinels; nothing ran it automatically, so a change to one court could
silently break another. `test_guard.py` wires it in. Signatures are computed
once per session in parallel, then each sentinel asserts against its pin — so
the whole suite costs about what the harness command costs.

**Why `test_invariants.py` exists separately.** The guard catches structural
*drift*; these catch the specific things that were wrong and are now right.
Each test names its record, so a failure tells you *which reading regressed*
rather than which number moved — `test_acca_redactions_become_glyphs`,
`test_nevapp_ocr_scan_is_flagged`, `test_orctapp_disposition_is_a_summary_not_the_opinion`.

**The honest gap.** `tests/fixtures/criteria.json` holds 48 snapshots, one per
printed *format* (not per file), each chosen and justified in
`tests/criteria_manifest.py` (1144 lines of "this is a shape the court really
prints and it cost real work to read"). It is genuine ground truth and it
*should* be an assertion. It is not one yet, because the snapshots are
**v1-shaped** — they name fields the way the old engine did (`date_filed`,
`panel_line`, `lower_judge`, `prior_history`) while v2 names them differently.
So the test currently reports the v1→v2 field gap instead of asserting on it.
Closing that is real, tractable work and it would meaningfully raise
confidence in the headmatter reader.

---

## 11. The release gate

`centralia/released.py` is **generated, never typed** — written by
`harness.cli released --write` from the reviewer's own marks. A court is
released when *every* record in its corpus directory has been reviewed and
*none* is marked bad.

That is deliberately a human judgment. `quality` measures mechanical signals
and `coverage` says nothing went unaccounted for; neither claims the reading is
*right*. Only a person who compared the output to the page can claim that.

**The extractor is not gated.** `extract`, `render`, the guard and the viewer
read every court. The gate applies to `centralia.read` only — the public API —
so an unreleased court raises `CourtNotReleased` rather than quietly returning
a worse reading. An *unknown* court id raises too, because core's generic
reader would return `status: valid` and just read badly, and a typo should not
look like a thin court.

Currently: **191 released, 50 held back, of 241.**

---

## 12. Where things stand

| | |
|---|---|
| courts wired | 241 |
| per-court files | 241 |
| corpus | 10,349 PDFs, 3.1 GB |
| released through the public API | **191** |
| held back | 50 — 45 federal district, 5 other |
| core engine | 20.5k lines, excluding court files |
| the 241 court files | 111k lines — the long tail, by design |
| corpus manifest resolved | 10,046 of 10,349 (97.1%) |

---

## 13. What is left

Ranked by how much they matter, not by effort.

1. **`notes/core-patch-queue.md` (2507 lines).** Defects diagnosed and *proved*
   against real files by the port agents, but not yet applied. None is
   speculative; each was reported with evidence. Apply serially, run `guard`
   behind each one. This is the highest-value backlog in the repo.

2. **Publish a release so the demo catches up.** `released.py` was regenerated
   on 2026-08-24 (this is how `scotus` reached 191), but the browser demo reads
   `RELEASED` out of the *published* wheel — so until a new version ships to
   PyPI, the public page still reports the old list. Regenerating and releasing
   belong together.

3. **The 50 held-back courts** — two different problems that should not be
   worked as one pile:
   - **43 have a known defect** (at least one `nay`), concentrated in the
     district lane: `ilcd` 28 of 35, `cand` 15 of 22. Much of this is the
     lane's structural problem — exhibits and third-party attachments the
     court never typeset — rather than a reader that misreads the court.
   - **7 are simply unread** (`nced` 1 of 29 marked, `vawd` 4 of 42). These
     need reviewer time, not engine work, and some may already be fine.

4. **`notes/review-backlog.md` (1095 lines).** Findings from the sweep
   reviewers, partly worked through — completed items are marked ✅.

5. **The 303 unresolved corpus URLs.** `scripts/corpus-unresolved.txt`. Some
   are false negatives from rate limiting rather than genuinely missing files;
   re-running the resolver from a whitelisted IP should recover them.

6. **`notes/v1-diff.md`.** Regenerate with `harness cli v1diff` and work the
   ranked list; it finds defects by machine rather than by eye.

7. **`harness trace` is documented but does not exist.** `resolve/evidence.py`,
   `profile.py` and `notes/court-files-plan.md` all describe it as the way to
   answer "why did this page decide that", and every `Decision` already records
   its full evidence chain — the data is there, the command is not. This is
   probably the cheapest large win in the repo: the evidence chains are the
   engine's best idea and nothing currently surfaces them.

8. **`@provider` is implemented and unused.** Both seams exist in
   `resolve/evidence.py`, but across 241 court files there are **241 deciders
   and zero providers** (see §3.4). Either the collaborative half of the design
   is dead code that should go, or courts should be contributing evidence where
   they currently short-circuit. That is a design decision someone needs to
   make, not a bug.

9. **Known open items** carried in the notes: EXHIBIT A attachment pages in
   district filings; a `cacd` pleading-paper case; a full re-ingest after the
   footnote hardening.

---

## 14. For a reviewer

If someone is about to read this codebase critically, these are the places
where the design is deliberate and the places where it is genuinely thin.

**Read in this order.** `resolve/evidence.py` (157 lines — the pattern the
whole engine is built on), then `geometry.py` (138), then `model.py`, then
`sections.py`. Those four are small and they explain the rest. Only then
`pipeline.py`.

**The comments are the design docs.** This codebase carries an unusual density
of rationale in comments, most of it naming the specific file and the specific
failure that produced the rule. That is intentional: a threshold without its
witness gets "cleaned up" by the next person. If you are tempted to delete a
comment, check whether it is the only record of why a constant is what it is.

**Where the risk actually is:**

- **`pipeline.py` at 3581 lines and `assemble.py` at 2803** are the two places
  the "one clear owner per decision" discipline is under most strain. If
  anything has quietly grown a second decision-maker, it is here.
- **`ecf.py` at 3198 lines** carries 89 courts on one contract. That is the
  right call, but it means one bad change touches a third of the corpus.
- **Court files are unenforced at the edges.** The no-cross-import rule is
  asserted by a test; the *spirit* — that a court file records a fact rather
  than reimplementing a reading — is not mechanically checkable. And the
  numbers suggest the spirit is under pressure: 241 headmatter deciders, 111k
  lines. The flat-file rule guarantees they cannot *entangle*, which is the
  thing that killed v1 — it does not guarantee they are small, and it does not
  stop 241 files from independently rediscovering the same reading.
- **The evidence chain's collaborative half is unused.** Zero providers across
  the whole corpus. The vetoes still apply to court decisions, so the safety
  property holds — but "courts contribute evidence, core decides" is currently
  aspirational for every point except the ones core owns outright.
- **The release gate depends on human marks**, so it is only as good as the
  reviewing, and reviewing is the scarcest resource in the project.

**What would most improve confidence:** applying the core patch queue with
`guard` behind each item, then a full `coverage` + `quality` pass, then
re-deriving `released.py` from fresh marks. In that order — the patch queue
will move the other two numbers.
