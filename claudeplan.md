# Centralia v2 — Rewrite Plan

## Context

`/Users/Palin/Code/centralia` parses digital court-opinion PDFs (238 courts, ~9,400-PDF corpus) into a structured document and renders review HTML + Harvard casebody XML. It works, but three months of accretion left an architecture where **the same decision is made in 3–5 stacked places per court**: a 6,734-line `base.py` god class (596-line `extract()`, 38 stages), 936 method overrides across 270 court classes (173 never call `super()`), ~111 config knobs across 25 declaration sites, five independent headmatter readers, four caption systems (one dead), inheritance chains up to 12 deep, and two courts that bypass the engine entirely with ~2,000 private lines. `base.py` even carries workarounds for its own subclasses' overrides. The complaint — "multiple places that override things, no streamlined logic" — is exactly what exploration measured.

The evidence also shows the exit: 34% of court classes are already pure config; the missing `reset()`/`finalize()` lifecycle explains ~170 overrides by itself; measured-geometry doctrine retires most tuning knobs; and the hard-won knowledge (footnote-zone lessons that consumed ~25% of commit history, the 35-style caption catalog, 2,124 hand-labeled footnote truths, the criteria test manifest) is fully portable.

**Goal:** rebuild centralia at `/Users/Palin/Code/rewrite` as one streamlined pipeline where every decision has exactly one home; keep the information and the lessons, shed the junk.

## Locked decisions

- **Scope:** extraction core only — no Django viewer. Renderers (review HTML + casebody XML) in scope, both derived from one section declaration so they can't drift.
- **Stack:** Python 3.13 + pdfplumber + uv (all quirk knowledge is pdfplumber-shaped).
- **No file copying** — disk is tight. Config points at `/Users/Palin/Code/centralia/assets/<court>/` (PDFs) and `/Users/Palin/Code/centralia/output/notes/` (notes, `_footnotes_truth.json`) in place.
- **Alabama fidelity lock dropped** — Alabama is a normal court; ~19 legacy opt-out knobs disappear.
- **Package name: `centralia`** (v2), package dir `/Users/Palin/Code/rewrite/centralia/`.
- **Ignore old review marks/rankings** (`_marks.json` / `_filemarks.json` / `_done.json`) — stale.
- **Metadata:** decision_date + docket_number + parties gate v1 rollout per court; judges/panel/disposition/lower_court/history best-effort, tightened per family.
- **Pilot courts:** mont, ala, ca1, ca2, akd, conn, tenn, scotus + a caption-rail court and a scan-heavy court picked by census.
- **Review tooling in v1:** static self-contained `viewer.html` (keyboard nav, iframe review pages, 5-tier mark buttons, old-vs-new A/B toggle) + a tiny stdlib marks server persisting marks/notes to JSON in this repo. No Django.
- **Process rules:** never auto-run tests/audits — all verification is on-demand; conserve usage (no broad agent fanout); keep lessons in the repo (`docs/lessons/`), not in path-keyed memory dirs.

## Design thesis

The old system sprawled because courts could *replace* engine logic. The rewrite inverts this: a **fixed 11-stage pipeline** whose decisions are made by **core resolvers**, each fed an ordered **evidence chain**. Courts contribute only:
1. a validated, frozen **`CourtProfile`** (data only — unknown fields are a construction error),
2. a list of named **document styles** they publish (landmark-driven layout contracts, defined centrally),
3. rarely, registered **evidence-provider** functions that feed candidates/vetoes/support into a resolver — never a decision, and never "there is none."

No inheritance anywhere in court-land. Expected steady state: most courts are a 20–60 line profile; a few carry 1–3 providers; zero carry a pipeline.

## Package layout

```
/Users/Palin/Code/rewrite/
├── pyproject.toml               # uv; dep: pdfplumber only
├── centralia/
│   ├── __init__.py              # extract(pdf_path, court_id) -> ExtractionResult
│   ├── settings.py              # CORPUS_ROOT / NOTES_ROOT -> old repo paths; BASELINE_DIR
│   ├── pdfio/                   # THE one pass over the PDF; only pdfplumber import site
│   │   ├── model.py             # Char, Run, Line (stable ids), DrawnRule, PageModel, PdfModel
│   │   ├── build.py             # chars -> quirk-repaired -> runs -> baseline-clustered lines
│   │   ├── quirks.py            # named repairs, each fires a trace event (see below)
│   │   └── rules.py             # h/v rule chaining/merging; single is_typed_rule definition
│   ├── geometry.py              # DocGeometry: measured body_x0/right_x1/lead/body_size;
│   │                            #   profile margins are floors/caps only; doc vocabulary set
│   ├── model.py                 # typed document model (below)
│   ├── sections.py              # SECTION_SPEC — single section declaration + iter_text()
│   ├── classify.py              # scan/CID triage short-circuit + DocType classifier
│   ├── styles.py                # named layout-contract registry (document styles)
│   ├── resolve/                 # core resolvers — every decision lives in exactly one
│   │   ├── evidence.py          # Evidence, Decision, Resolver, provider registry
│   │   ├── captions.py          # caption fingerprint (captionfp port, reads PageModel)
│   │   ├── furniture.py         # folios, running heads, stamps, margin bands
│   │   ├── footnotes.py         # THE footnote-zone subsystem, evidence-chained
│   │   ├── segments.py          # line grouping: gap bands, indents, alignment
│   │   ├── headmatter.py        # ONE headmatter/criteria reader (replaces five)
│   │   ├── bylines.py           # author-byline grammar (home of the one sanctioned regex)
│   │   └── assemble.py          # opinion boundaries, blocks, footnote attach, signature,
│   │                            #   trailer, residual sweep
│   ├── pipeline.py              # fixed stage list + per-doc ExtractionState + trace
│   ├── profile.py               # CourtProfile frozen dataclass + validation
│   ├── courts/                  # one small module per court: PROFILE = CourtProfile(...)
│   ├── render/
│   │   ├── html.py              # review HTML — iterates SECTION_SPEC, typed dispatch
│   │   ├── facsimile.py         # styled headmatter/caption reproduction (same fp object)
│   │   └── casebody.py          # Harvard casebody XML — iterates SECTION_SPEC
│   └── audit.py                 # ported _norm + coverage + correctness gates
├── harness/                     # NOT installed; run only on demand
│   ├── cli.py                   # extract / render / check / census / compare / trace
│   ├── baseline.py              # freeze old-system output (lazy, per court/family — disk!)
│   ├── compare.py               # A/B vs frozen baseline; diffs bucketed & persisted
│   ├── truth.py                 # loads _footnotes_truth.json + criteria fixtures
│   ├── health.py                # 7-int health vector per file; corpus census
│   ├── viewer.html              # self-contained review shell: court/file nav, marks, A/B toggle
│   └── viewer.py                # stdlib http.server: serves output/ + marks/notes JSON API
├── output/                      # generated review HTML + marks/notes JSON (gitignored)
├── baseline/                    # generated per-family on demand (not full-corpus upfront)
├── docs/lessons/                # the durable lessons live IN the repo this time
└── tests/                       # pytest, never auto-run
```

## The typed document model (`model.py` + `sections.py`)

Every dunder sentinel becomes a real variant; inline markup stays as the proven marked-up-string vocabulary (`<em> <strong> <u> <footnotemark>N</footnotemark> <pagenumber value=""/> <centered> <flushright>`, XML-escaped).

- `DocType` enum: `OPINION ORDER RR JUDGMENT FILING CERTIFICATE NOTICE SCAN HYBRID UNKNOWN`; `SCAN` is a success status.
- **Flow blocks:** `Paragraph | Blockquote | Heading | ListItem | TableBlock | ImageRef`, each with `Prov(page, line_ids)` provenance.
- **Headmatter items** (replace `__hm__/__caption__/__DIVIDER__/__RULE__/""/__image__/__facsimile__`): `HmLine(text, align, x0, size, bold, italic, rel)` · `CaptionBlock(left, right, style_id, rail, rail_rows, fp)` — the renderer draws borders from the same measured `fp` the classifier stored · `Rule(span, typed)` (PDF drew it — render it) · `Divider` (semantic break — draw nothing) · `Gap` (spacing only). "Never invent layout" becomes type-enforced.
- **`Criteria` dataclass** — the CourtListener scalars, ONE representation (no criteria-dict twin); per-field evidence lives in the trace under `criteria.<field>`.
- `Opinion(type, author, author_name, author_title, caption, blocks, footnotes, signature)`; `Footnote(label, blocks)` (real Blocks, not `(tag, text)` tuples).
- `Document(meta, criteria, headmatter, headnotes, syllabus, attorneys, opinions, headmatter_footnotes, signature, trailer, dropped, residual, warnings)`; `Dropped(text, prov, kind)`, `Residual(text, prov, kind=content|furniture)`.
- **`SECTION_SPEC`**: one row per section (name, attr, render order, html style, casebody element, audited flag). Renderers and audit iterate the spec; `iter_text()` is one pattern-match walker replacing sentinel sniffing. The old 7–10-place field-add tax becomes **two edits** (Document field + spec row), verified by `check_spec()`.

## The engine

**Fixed pipeline** (`pipeline.py`): 1 load (pdfio) → 2 triage (scan/CID short-circuit) → 3 measure (DocGeometry + vocabulary) → 4 classify (DocType + document style + caption fingerprint) → 5 furniture → 6 footnotes (per-page zones) → 7 segments → 8 headmatter (caption + criteria + headnotes/syllabus) → 9 body (bylines → opinions → footnote assembly/attachment) → 10 finalize (signature lift, trailer, residual sweep, warnings) → 11 emit `ExtractionResult(document, trace, status, versions)` where `status ∈ valid | review | failed` (gate-driven) and `versions` stamps the pipeline/profile version into every output for A/B reproducibility. Fresh `ExtractionState` per document — no instance state, no undeclared attributes. `NO_BODY_EXPECTED` types skip opinion assembly; empty `opinions` is correct output.

Two invariants adopted from the Codex plan review: **substantive content may never be reclassified as furniture to improve a metric** (enforced in the audit gates), and **writings are never merged merely because author or type matches** (enforced in `resolve/assemble.py`). The court registry row carries an explicit rollout state (`pending | migrated | blocked`).

**No document-mutation hooks in v1.** The old 54-court `_sweep_residual` co-opt and 113 `extract()` wrappers were compensating for missing decision points; the fix is adding decision points, not hooks.

**Resolver-with-evidence-chain** (`resolve/evidence.py`): `Evidence(step, kind=candidate|veto|support, value, score, why, prov)` → deterministic merge (vetoes filter → weak candidates need support → highest score → ties by core-step order) → `Decision(point, value, fired, chain, floor_used)` recorded in the trace. Invariants enforced centrally:
- Thresholds come from DocGeometry; profile constants only clamp (floor/cap); measurement only tightens.
- **No evidence → the floor, unchanged** — never derive a fallback from the signal being disambiguated (kills the `page.height*0.5` bug class structurally).
- **Vetoes are core-owned** (underline-not-a-separator, quoted-apparatus above the page's own separator, body-text corroboration) and apply to every candidate regardless of source — dissolving the old call-site workarounds.
- Providers cannot decide "there is none"; each provider requires a fixture pair (must-fire file + near-miss); the census reports provider counts per court (sprawl monitor, soft cap 3/court).

**`resolve/footnotes.py`** is the consolidated subsystem the history demands: learned separators clustered across pages, structural thin-rule detection, typed underscore rules, body-size labels, no-rule-drawn courts, page-ownership vs mark-based attribution, PUA/symbol star canonicalization — each a named evidence step visible in traces.

**`pdfio/quirks.py`** centralizes every pdfplumber repair as a named, traced rule: stamp-split at x-gaps on banner baselines; merged-visual-columns split; offset italic baselines re-merged; broken glyph bboxes snapped only when the corrected top lands on a populated row (ʻokina rule); ligature/nbsp normalization; triple-stroke pleading-rail collapse. Kills the `page_lines`/`correct_page_geometry` override category.

**Caption fingerprint** (`resolve/captions.py`): captionfp's measurement logic ported ~1:1 but reading `PageModel` — no second parallel parse, no swallowed exceptions; the signature object stored on `CaptionBlock.fp` is what the renderer draws from, so label and reproduction cannot disagree.

## Reused from the old repo (reference in place or port as assets)

- `audit.py` `_norm` (old repo `centralia/audit.py:119-176`) — port verbatim.
- `tests/criteria_manifest.py` + `tests/fixtures/criteria.json` — port; prefix-stem matching preserved.
- `output/notes/_footnotes_truth.json` (2,124 files) — read in place via `harness/truth.py`.
- `library/caption_catalog.py` (35 named styles + ASCII art) — port as the style vocabulary for `styles.py`.
- `centralia/captionfp.py` — measurement logic ported onto PageModel.
- Scratchpad harness concepts (before/after hash compare, footnote-delta census, 7-int health vector) — promoted into `harness/`.
- Grounding files for implementers: old `centralia/models.py`, `base.py` stage structure (~645–1290) and CLASS CONFIG (~300–441), `courts/mont.py`, `courts/akd.py`, `courts/_abbrevtitle.py`, `render/html.py` sentinel dispatch, `output/notes/*.md` per-court quirk notes.

## Explicitly left behind

Subclass-per-court inheritance and family mixins; dunder-sentinel dicts; the criteria-dict/flat-scalar twin; dead modules (`caption_id.py`, `library/captions.py`, `docmarks.py`, `notes_server.py`, `notes_build.py`); the Django viewer, `ecosystem_audit.py`, `fetch.py` (old repo keeps them); the Alabama byte-fidelity lock; the 7–10-place field-add tax.

## Verification (all on-demand — never auto-run)

`harness/cli.py` subcommands:
- **`baseline freeze <court|family>`** — runs the OLD system (subprocess into old repo's venv) and stores normalized section chunks + health vectors + opinion counts + footnote labels. **Lazy, per court/family as rollout reaches them** — not full-corpus upfront (disk constraint).
- **`check <court|file>`** — correctness gates: (1) residual-content = 0; (2) opinion count matches truth/triaged baseline; (3) per-section normalized word count within tolerance of baseline (the Connecticut-341k-words gate); (4) footnote labels match `_footnotes_truth.json` exactly; (5) criteria fixtures pass; (6) doc-type census plausibility (a district >70% "opinion" fails); (7) rendered caption consumed the same fp object the classifier stored; (8) decision_date/docket_number/parties present (v1 metadata gate).
- **`compare <court>`** — A/B vs baseline; every diff bucketed `intentional-fix | representation-only | regression`, persisted so triage is resumable.
- **`census`** — health vectors rolled up per court + provider-count column.
- **`trace <file> [--decision footnote.separator]`** — per-decision evidence chains; review HTML gets a collapsed per-page "which step fired" panel.
- **`serve`** — starts the stdlib review server: `viewer.html` shell (keyboard nav, iframe per-PDF pages, 5-tier marks, old-vs-new A/B toggle per file) + JSON persistence of marks/notes under `output/notes/` in this repo.

## Review workflow (how outputs get eyeballed)

`harness render <court>` writes per-PDF review HTML + a per-court index with machine health chips (gate pass/fail per file). `harness serve` opens the viewer shell for keyboard-driven review and marking; the A/B toggle iframes the old repo's rendered page beside the new one for the same stem. Marks/notes persist as JSON/markdown in this repo (the old repo's marks are stale and stay untouched). Machine gates propose the worklist; your marks remain the human verdict.

## Phases

- **Phase 0 — Harness first.** `settings.py`, `harness/` (`_norm` port, truth loaders, criteria fixtures), `baseline freeze` for the pilot courts only; census picks the rail + scan pilot courts. *Done:* old-vs-old compare is an identity; pilot files enumerated.
- **Phase 1 — `pdfio` + `geometry`.** *Done:* deterministic line dumps for pilot files; quirks traced; measured geometry sane.
- **Phase 2 — Model + sections + renderers + audit skeleton + viewer.** *Done:* hand-built Document renders HTML + casebody and audits clean; adding a dummy section field takes exactly two edits; `harness serve` shows rendered pages in the viewer shell.
- **Phase 3 — Triage + classify + caption fingerprint.** Doc-type calibration: label ~500 files (Claude-assisted, user spot-checks in review HTML). *Done:* pilot-corpus doc-type census plausible; scans report as success; caption styles stable vs catalog.
- **Phase 4 — Footnote subsystem.** Validated directly against the 2,124-file truth (zones/labels don't need opinions). *Done:* label-match ≥ old system; every miss has a readable trace.
- **Phase 5 — Furniture + segments + headmatter/criteria.** *Done:* criteria fixtures pass for pilot courts; facsimile visually verified for the rail court and akd.
- **Phase 6 — Bylines + body assembly + finalize.** *Done:* all 10 pilot courts pass every `check` gate; A/B diffs fully triaged with zero regressions.
- **Phase 7 — Rollout by byline family** (largest first), freezing each family's baseline as reached. *Done per family:* gates pass; provider counts within cap; diffs triaged.
- **Phase 8 — Hard tail.** cal/calctapp (explore what truths their private pipelines encode before profiling them), stragglers; census becomes the standing health report.

## Relationship to PLAN.md (the Codex plan)

Adopted from it: the `valid | review | failed` status triple, per-court rollout state in the registry, the two invariants above, and version-stamped outputs. Rejected, with reasons: Django ingestion/persistence (out of scope per user), the legacy-`ExtractedDocument` compatibility serializer (would drag the dunder-sentinel format into the new code; A/B happens at normalized-text level in the harness instead), shadow-mode/production-cutover machinery (there is no production; the old repo is the rollback), the old six-value doc-type taxonomy (keeps the 88%-"opinion" misclassification), scans-as-review-status (scans are a success result), and Alabama as the lone vertical slice (the 10-court archetype pilot attacks layout diversity directly).

## Risks / open items

- **cal/calctapp** may encode domain truths absent from `base.py` and could force late core changes — budgeted exploration in Phase 8.
- **Criteria extraction is new scope**, not a port — the v1 gate is deliberately just decision_date/docket_number/parties.
- **Doc-type ground truth doesn't exist** — the ~500-file calibration pass in Phase 3 creates it.
- **Provider-sprawl relapse** — guarded by the soft cap, fixture-pair requirement, and census column; a court needing >3 providers signals a missing core evidence step or style.
- **Casebody XML**: semantic compatibility with normalized diffs, not byte compatibility (the old renderer had already drifted).
