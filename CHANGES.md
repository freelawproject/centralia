# Changes

## 0.0.5

### Added

- **An ingest-facing writing render, and it is what the payload carries.**
  `opinions[].html` was `render_opinion` — the review page's own drawing of a
  writing, with a type chip a host page has no use for and, on a consolidated
  record, a caption set in classes only this package's stylesheet knows. The
  new `render_opinion_ingest` (public) drops the chip, states the caption
  inline (the `render_hm_inline` technique), and WIRES the footnotes: each
  mark is an anchor to its note and each note links back, namespaced by the
  writing's `order` (`ref-o2-7` / `fn-o2-7`), so several writings on one host
  page — each restarting its notes at 1 — cannot collide. A note whose mark
  was never read keeps a plain label rather than linking to nowhere, and a
  symbol label gets a codepoint slug (`*` → `u42`) so both ends agree on an
  id the character itself could not be. The review page keeps its own render.
- **The cover's notes travel in `html_inline`.** `headmatter.footnotes` was
  data beside the blob; nothing a stored cover could show, so a substituted
  party's `*` was a dangling mark. The notes now render into `html_inline`
  itself, wired under the `hm` namespace, styled inline like everything else
  in that block.
- **The payload says which centralia wrote it.** `versions` now carries the
  installed package version alongside the pipeline's, so a consumer can
  decide payload shape by it instead of sniffing the markup.

### Fixed

- **`html_inline` no longer ships the model's vocabulary raw.** The review
  rows run `inline_to_html`; the portable rows did not, so a cover line
  carrying `<footnotemark>` or `<pagenumber/>` reached an ingest as tags no
  browser knows. Converted like everywhere else.
- **`__version__` said "0.0.3" while 0.0.4 shipped.** It is now read from the
  installed distribution — a literal nothing updates is a number that lies,
  and it is stamped into every payload now.

## 0.0.4

### Added

- **`DEVELOPMENT.md`** — how the engine works and why it works that way, for
  handing the project to someone else and for reading before a review. The
  five ideas the design rests on (measured geometry rather than tuned
  constants; nothing leaves a PDF unaccounted for; evidence chains with
  core-owned vetoes; courts as data; the typed model), the eleven pipeline
  stages, a file-by-file map, when geometry can be trusted and when it cannot,
  the three court lanes, the five oracles, the viewer, the tests, and the
  release gate — plus what is left, ranked, and where the design is thin.
- **The test corpus as a list of links.** `assets/` is 10,349 court PDFs and
  3.1 GB, excluded from git, which left a clone with readers tuned against
  documents it could not obtain. `scripts/corpus.txt` carries a public
  CourtListener storage URL for each, and `scripts/fetch_corpus.py` replays
  them — no credentials, since storage is public. `--approved` pulls only the
  files a reviewer signed off; `--verify` checks the links without
  downloading. Rate limiting is treated as rate limiting rather than as a
  missing file.

### Changed

- **`scotus` is released.** Its 100 records have been marked good for some
  time; the generated release list had simply not been re-run. 191 courts are
  now released of 241.

### Fixed

- **wva reads a memorandum decision.** The court publishes a paper the corpus
  had never sampled, and because it is unsigned — writings open at bylines —
  nothing opened one: the walk ran past the whole majority and found the
  dissent's byline on page 4. The decision itself was read as headmatter, its
  opening paragraph became the attorneys criterion, and the record reported a
  dissent with no majority. It is now a fourth declared paper, named by the
  banner it sets below its caption rather than by the words in it, and the
  masthead is claimed as the whole leading run so the court's second line
  stops arriving as part of the first party.

## 0.0.3

### Added

- `read()` returns **`html_inline`** on `headmatter` and `endmatter`: the same
  rows with the layout stated in the markup instead of in this package's
  stylesheet. `html` needs that stylesheet to mean anything, so a consumer
  without it sees a centered masthead flush left and a two-column caption
  collapsed into one — every docket number after every party rather than
  beside its own. `html_inline` carries alignment, indents, rules and the
  caption's columns inline. Both forms are returned; neither replaces the
  other.
- **`render_hm_inline`** is exported, for callers that took the `extract()`
  path and hold a `Document`.
- The README documents the real surface: all 14 keys `read()` returns, the
  `by_role` / `untinted` measures on the two role-bearing blocks, and the
  release gate (`released_courts`, `CourtNotReleased`, `allow_pending`,
  `UnknownCourt`) it had never mentioned.

### Fixed — district reading

Each measured against the corpus, not only the record that motivated it.

- A **counsel roster closes on its party**, not on the word "attorneys."
  Minnesota writes `… Minneapolis, MN 55402, for Plaintiff.` and never the
  word, so the roster never closed and the walk ran to its row cap, taking
  the opinion's opening paragraphs with it. The phrase also wraps, so the run
  is cut after the last row whose accumulated text closes an appearance.
- A **fence row's trailing rail glyph is the rail, not text.** A typed `)`,
  `X` or `:` caption rail lands on the row that closes the box; unrecognized,
  the box never closed, the band carried onto the next page and read its
  clerk stamp as a caption cell, and a second caption box opened the writing
  as body prose. 299 records across 38 courts.
- **`Miscellaneous.` and `Interested Party.`** are a party's status, not a
  docket heading and not part of the party's name. A fourth party was
  published as a second docket, and `Interested Party - Appellant` welded
  into a party name. `MISC. NO.`, `Misc. Action No.` and a bare `CIVIL
  ACTION` still read as docket labels.
- A **caption that is one centered stack has no columns to split.** A court
  that centers docket, parties, pivots, statuses, title and date on the page
  axis, one row apiece, had every party filed into the right-hand column as
  "case info."
- The **masthead may only continue on a court or a division name.** Where a
  whole caption is set in the masthead's own face, the face test claimed the
  first party as more of the court's name.
- A court's **prose byline** is read where that is the form it signs in: one
  court's records sign `SURNAME, United States Magistrate Judge.` and none
  sign the reversed form its profile declared, so the byline was body prose
  and an unsigned head typed `order` however the paper was titled.
- **One printed heading is one heading.** A wrapped heading arrived as one
  heading per row on a page carrying two leadings, because the bands were
  measured off the tighter block. Prose recovers from that; a heading has no
  mid-sentence cue, so a two-part heading rendered as nine centered blocks
  and one paper's own name as sixteen. Rows set in one type at one pitch are
  joined.
- A **caption-box graphic is not the court's device**: an e-filed caption may
  paint a fill over the box its own rows are typed in. Scoped to the first
  sheet's head band, where a caption is.
- A **chambers can misspell its own name** — one letter short of "DISTRICT"
  left a masthead with no anchor and a cover entirely unread. One letter is
  the tolerance.
- The **conjunction is not the paper's name**: `and` has to be a title word so
  `MEMORANDUM OPINION AND ORDER` reads whole, which had made every all-caps
  party row ending in `AND` a title.

### Changed — tooling

Not part of the published package.

- The regression guard reads the reviewer's marks: a file marked `nay` is
  never pinned, is held out of the verdict, and is skipped by `--bless`, so a
  rejected reading cannot be frozen as truth. `--prune` unpins existing ones.
  A bare argument may be a whole `court/stem` key, so one sentinel can be
  checked or blessed by itself.
- `guard --review` publishes the diffs the viewer can filter on, and marking a
  file good in the viewer re-pins its sentinel — approving a rendering and
  blessing its signature were two registries and two commands.
- `quality.json`, `coverage.json`, `guard-review.json` and the `.bak` copies
  are no longer tracked: every one is rebuilt by a command, and they buried
  real diffs under thousands of lines of churn.

## 0.0.2

- Support Python 3.12.

## 0.0.1

- First release to PyPI.
