# Centralia Rewrite Plan

## 1. Objective

Rewrite Centralia as a predictable, end-to-end legal PDF extraction system that
preserves the useful behavior and output contract of the current project without
reproducing its accumulated parser sprawl.

The rewrite succeeds when every supported document follows one observable path:

```text
PDF
  -> source observations
  -> normalized layout
  -> document and layout classification
  -> semantic zoning
  -> canonical legal document
  -> fidelity validation
  -> renderers and persistence
```

The canonical structured legal document is the system's primary product. HTML,
Harvard casebody XML, JSON, review pages, and database records are projections of
that document. They must not perform extraction or silently repair parser output.

## 2. Product Boundaries

The rewrite includes:

- PDF text, geometry, font, rule, image, and table observation.
- Born-digital detection and explicit handling of scanned/OCR and damaged text
  layers.
- Document-type classification.
- Headmatter, opinion, footnote, blockquote, table, signature, trailer, notice,
  and page-furniture extraction.
- A versioned canonical document model and schema-compatible legacy export.
- Coverage auditing, structural validation, warnings, and review diagnostics.
- JSON, HTML, and Harvard casebody XML rendering.
- CLI and Python APIs.
- Django ingestion, persistence, admin/review integration, and regeneration
  workflows.
- Migration of all courts currently considered supported by Centralia.

The first release does not include a new OCR engine. Scanned or image-only PDFs
receive an explicit unsupported/review status. Existing usable OCR text layers may
be observed, but their geometry is not treated as reliable without a later,
separately tested OCR pipeline.

## 3. Design Rules

1. **One owner per decision.** Each extraction fact is produced by one stage.
   Later stages may consume or reject it, but may not independently rediscover and
   overwrite it.
2. **Evidence travels with results.** Structured values retain their source page,
   bounding boxes or source lines, producing stage, and confidence/review state.
3. **No silent loss.** Every source element ends as authored content, recognized
   furniture, an intentional duplicate, or unresolved residual content.
4. **Shared mechanics before court exceptions.** Geometry, font runs, indentation,
   repetition, and boundaries drive shared behavior. Court-specific code is used
   only for genuinely distinctive conventions.
5. **Classification is separate from extraction.** Document type, layout family,
   and semantic zones are explicit outputs rather than side effects of body parsing.
6. **Renderers are pure consumers.** A renderer may format or omit a field according
   to its public format, but it cannot move content between semantic sections.
7. **Fidelity includes structure.** Covered text is still wrong if it is attached to
   the wrong opinion, footnote, caption, signature, or semantic block.
8. **Failure is inspectable.** A failed or partial extraction returns diagnostics and
   evidence instead of an empty document that looks successful.

## 4. Target Architecture

### 4.1 Source layer

Create an immutable source representation independent of semantic parsing:

- `SourceDocument`: file identity, page count, PDF metadata, digital/OCR status,
  global warnings, and pages.
- `SourcePage`: dimensions, rotation, lines, characters/runs, vector rules, images,
  and tables.
- `SourceLine` and `SourceRun`: normalized text plus original text, geometry, font
  attributes, writing direction, and stable source identifiers.
- `SourceArtifact`: CID glyphs, duplicate/overlapping glyphs, malformed mappings,
  or image-only regions that could not be represented as ordinary text.

This layer owns PDF-library interaction, coordinate normalization, duplicate glyph
handling, and collection of raw evidence. No court logic belongs here.

### 4.2 Layout layer

Transform source observations into a `LayoutDocument` containing:

- learned body rail, margins, dominant font sizes, line spacing, and columns;
- physical and printed page-number candidates;
- repeated top/bottom furniture candidates;
- caption rules and divider geometry;
- footnote separators and footnote zones;
- reading-order groups and paragraph-continuation evidence;
- table, image, and indentation regions.

Layout analysis may return multiple scored candidates when the page is ambiguous.
It does not decide legal meaning.

### 4.3 Classification and zoning layer

Classify the document as `opinion`, `order`, `notice`, `filing`,
`certificate-of-judgment`, or `unknown`. Separately classify its layout family.

Assign each source element to one semantic zone:

- publication notice or filing stamp;
- caption/headmatter;
- syllabus or reporter headnotes;
- opinion body;
- footnote;
- table or image;
- signature;
- counsel/end matter;
- running furniture;
- unresolved.

Zone assignments contain a reason, producing rule/detector, confidence, and source
identifiers. Conflicts are resolved centrally using explicit stage precedence; court
configuration cannot mutate already finalized assignments.

### 4.4 Assembly layer

Assemble zones into the canonical document. This stage owns:

- headmatter criteria and raw loss-resistant headmatter;
- opinion boundaries, types, authors, and repeated captions;
- paragraph joining and inline formatting;
- blockquotes, transcript turns, statute/rule subdivisions, headings, and lists;
- footnote labels, references, paragraphs, tables, and opinion attachment;
- signatures and counsel tails;
- page markers and source provenance;
- dropped furniture and unresolved residuals.

Multi-opinion documents must keep each writing's caption, body, footnotes, and
signature together. Writings are not merged merely because author or type matches.

### 4.5 Validation and audit layer

Run validation after assembly and before rendering or persistence:

- source coverage and duplicate-placement checks;
- substantive residual detection;
- body-required checks based on document type;
- orphan, duplicate, and numbering-gap footnote checks;
- opinion-boundary and caption consistency checks;
- suspicious body text in headmatter or furniture checks;
- CID, image-only page, and unreadable-text warnings;
- model/schema validation.

Validation returns a structured `AuditReport` with severity, code, message, source
references, and affected canonical nodes. A document may be `valid`, `review`, or
`failed`. Substantive content may not be reclassified as furniture merely to improve
coverage metrics.

### 4.6 Adapters and application layer

- JSON, HTML, and casebody XML renderers consume only the canonical model.
- A legacy serializer emits the current `ExtractedDocument` field shape and preserves
  downstream schema compatibility.
- A persistence adapter maps canonical documents and audit reports into Django models.
- Ingestion records source identity, parser/model version, extraction status, audit
  summary, and generated artifacts so reruns are reproducible.
- Admin/review pages show source evidence beside canonical placement and make residual,
  warning, signature, trailer, and dropped-furniture decisions visible.

## 5. Public Interfaces

Keep a small compatibility surface while introducing the staged engine:

```python
from centralia import extract

result = extract(pdf_path, court_id="ala")
result.document       # canonical document
result.audit          # structured AuditReport
result.status         # valid | review | failed
result.pipeline       # parser/model/config versions and stage diagnostics
```

Retain `get_extractor(court_id).extract(pdf_path)` as a compatibility adapter until
all callers migrate. Its return value must match the legacy structured schema.

The CLI will support:

```text
centralia extract COURT PDF [--json | --html | --xml] [--output PATH]
centralia audit COURT PDF [--report PATH]
centralia ingest COURT PATH [--recursive] [--resume]
centralia regenerate [--court COURT] [--document ID] [--format FORMAT]
centralia compare COURT PDF --against legacy
```

All commands return non-zero status for pipeline failure. Audit/review status is
reported distinctly from execution failure so batch work can continue and queue
documents for review.

## 6. Court Configuration Strategy

Each court selects a reusable layout-family profile and supplies only its deltas.
Profiles provide detectors and thresholds for common families such as:

- state appellate single-column opinions;
- ruled or parenthesis-column captions;
- federal appellate opinions;
- federal district docket-filed orders;
- bankruptcy and administrative appellate decisions;
- multi-writing/slip-opinion bundles.

Configuration can adjust measurable layout properties, enable reusable detectors,
and recognize court-specific contiguous furniture. A custom hook must declare its
input stage and typed output; it cannot access or mutate the final document globally.

Every exception requires fixtures that demonstrate both the intended match and a
nearby case it must not match. Raw-text matching is limited to stable court labels,
document headings, and boilerplate boundaries where geometry alone is insufficient.

## 7. Implementation Sequence

### Milestone 0: Baseline and inventory

- Freeze the existing public fields, renderer outputs, registry, supported courts,
  document types, and Django ingestion behavior as the compatibility baseline.
- Build a corpus manifest containing source hash, court, document kind, known layout
  traits, expected outputs, and known current defects.
- Select representative fixtures for every structural feature and court family.
- Record current extraction, audit, HTML, JSON, XML, and persistence results without
  declaring known defects to be desired behavior.

Exit gate: the team can distinguish compatibility requirements from current parser
bugs, and every supported court belongs to a migration family.

### Milestone 1: Pipeline foundation

- Establish package structure, typed stage contracts, canonical model versioning,
  diagnostics, and deterministic serialization.
- Implement source observation and normalized geometry.
- Add stage tracing and source identifiers before semantic parsing begins.
- Build test helpers for exact source placement and structural comparisons.

Exit gate: a PDF can be converted deterministically into inspectable source and layout
representations with no semantic extraction.

### Milestone 2: Reference vertical slice

- Implement the full pipeline for one representative born-digital appellate court,
  using Alabama as the compatibility reference.
- Complete headmatter, opinions, paragraph structure, footnotes, furniture, residuals,
  validation, all renderers, and legacy export.
- Add Django ingestion and review display for this court so the architectural boundary
  is tested end to end.

Exit gate: the reference corpus passes schema, fidelity, rendering, audit, and
persistence acceptance tests.

### Milestone 3: Shared layout families

- Add profiles in increasing structural difficulty: caption variants, federal
  appellate, federal district filings, multi-writing documents, tables/transcripts,
  and unusual signatures/end matter.
- Migrate a small representative set for each family first.
- Change shared stages when a behavior generalizes; add narrow court deltas only after
  shared logic is shown insufficient by fixtures.

Exit gate: each family passes its representative corpus with no substantive residuals
and no regression in previously completed families.

### Milestone 4: Full court migration

- Move remaining courts family by family.
- Run differential outputs and classify every difference as an intentional correction,
  a representation-only change, or a regression.
- Keep unsupported courts on the legacy path until their family gate passes.
- Track migration state explicitly in the registry: `legacy`, `shadow`, `new`, or
  `blocked`.

Exit gate: all currently supported courts run on the new pipeline; blocked documents
are individual documented exceptions, not entire silently failing court families.

### Milestone 5: Cutover and retirement

- Run new and legacy extraction in shadow mode against production-like batches.
- Compare schema, coverage, structural fidelity, runtime, and failure rates.
- Switch readers and ingestion to the new result after court-family acceptance.
- Keep rollback at the registry/configuration level during the observation period.
- Remove the legacy extractor only after all consumers use the canonical API or legacy
  adapter and regeneration has been verified.

Exit gate: the new system is the sole extractor, historical documents can be
reproduced, and legacy code can be removed without changing public outputs.

## 8. Test Strategy and Quality Gates

### Unit and contract tests

- Coordinate normalization, reading order, repeated furniture, caption rules,
  footnote separators, font runs, and duplicate glyphs.
- Paragraph joins, hyphenation, inline formatting, blockquotes, transcript turns,
  subdivisions, lists, tables, and image blocks.
- Document classification, opinion boundaries, author/type detection, signatures,
  notices, and counsel tails.
- Canonical schema round trips and legacy-schema serialization.
- Pure renderer tests proving that rendering does not mutate or reclassify content.

### Corpus and regression tests

- Golden structured fixtures for representative documents.
- Source-to-node coverage assertions rather than text-only snapshots.
- Differential JSON/XML comparisons with normalized handling of harmless serialization
  differences.
- HTML structural snapshots plus targeted visual review for captions, footnotes,
  blockquotes, tables, signatures, and multi-opinion boundaries.
- Negative fixtures for each court-specific detector.

### Required gate for every migrated court family

1. Compilation and complete automated test suite pass.
2. No source element is silently lost or multiply claimed.
3. No substantive residual remains in the accepted corpus.
4. Furniture removal is limited to recognizable contiguous units.
5. Opinion, caption, footnote, signature, and trailer ownership is correct.
6. Structured schema remains compatible or the approved migration adapter covers the
   difference.
7. HTML and at least one machine-readable renderer agree with the canonical structure.
8. Runtime and memory stay within the baseline budget established in Milestone 0.

## 9. Data Migration and Operations

- Version canonical schema, pipeline, court profile, and renderer independently.
- Store source hashes and versions with every persisted extraction.
- Make ingestion idempotent and resumable; rerunning the same source/version must not
  create duplicate logical documents.
- Preserve prior generated artifacts during migration so output changes are auditable.
- Add a regeneration queue that can target one document, court, profile, parser
  version, or renderer version.
- Expose aggregate operational metrics: valid/review/failed counts, substantive
  residuals, warning codes, unsupported scans, processing time, and failure stage.
- Roll out by court family with registry-level rollback; do not perform a single
  irreversible all-court cutover.

## 10. Definition of Done

The rewrite is complete when:

- all courts marked supported in the existing Centralia registry are migrated;
- the canonical model is the only source consumed by renderers and persistence;
- existing external document fields remain available through the stable schema or
  compatibility adapter;
- the accepted corpus has no unplaced substantive content;
- legal structure is preserved for headmatter, opinions, footnotes, blockquotes,
  tables, signatures, multi-opinion boundaries, and end matter;
- failures and partial results are explicit, reproducible, and reviewable;
- ingestion and regeneration are idempotent and version-aware;
- the old parsing path can be removed without leaving a production consumer behind.

## 11. Fixed Assumptions

- Python remains the implementation language and the package initially targets the
  current Python 3.13 environment.
- `/Users/Palin/Code/centralia` is the legacy reference implementation and corpus
  source; this workspace is the clean rewrite.
- The existing `ExtractedDocument` fields are the compatibility baseline, not a
  requirement to preserve the current internal dataclass design.
- The canonical model may add typed nodes, source spans, provenance, confidence,
  versioning, and audit state without breaking legacy consumers.
- Current output differences caused by known extraction defects are corrected and
  documented rather than preserved for byte-for-byte compatibility.
- Representative family migration is the required rollout strategy, while the final
  target remains complete replacement of all currently supported courts.
