# restatement

A court-pluggable PDF opinion extractor: give it a court PDF and a court id, get back
one structured `ExtractedDocument`. Rendering (Harvard casebody XML, JSON, …) is a
separate concern that consumes that model.

```python
from restatement import get_extractor
doc = get_extractor("ala").extract("path/to/opinion.pdf")
#  -> ExtractedDocument: doc.doc_type, doc.decision_date, doc.opinions, ...

from restatement.render import render_casebody
xml = render_casebody(doc)
```

```
python -m restatement.cli ala opinion.pdf          # human-readable criteria summary
python -m restatement.cli ala opinion.pdf --xml    # Harvard casebody XML
python -m restatement.cli ala opinion.pdf --json   # full ExtractedDocument as JSON
```

---

## Where this came from

`restatement` is a clean reimplementation of the extraction "guts" from the older
`ca1` repo. That repo carried two parallel extractors; we ported **`casebody/`**
(standalone, Harvard casebody XML, one subclass per court) and deliberately left
behind the Django-coupled `extractor/` + `circuits/` system.

The point of the rewrite was to keep the proven layout heuristics but put them behind
a cleaner contract.

## The contract

Extraction is modeled after Juriscraper's opinion scrapers: the base class defines
**what gets returned** — a fixed field set — and each court subclass fills or overrides
only the parts that differ for its layout. The return value is a structured
`ExtractedDocument` (the "criteria"), never an XML string.

`ExtractedDocument` (see `restatement/models.py`) carries:

- **Provenance / classification** — `court_id`, `court_label`, `doc_type`, `n_pages`,
  `layout_ok`, `source_path`
- **Headmatter criteria** — `decision_date`, `docket_number`, `parties`, `disposition`,
  `panel` / `judges`, `attorneys`, `history`, `lower_court`, and more
- **Body** — `opinions` (each an `Opinion` of `type` + `author` + `blocks` +
  `footnotes`), plus `headmatter_footnotes`
- **Diagnostics** — `warnings`

Inline formatting (`<em>`, `<strong>`, `<u>`, `<footnotemark>`, `<pagenumber>`) is baked
into the paragraph/footnote strings rather than held as a nested run-tree. That keeps
the layout logic intact and lets any renderer pass the markup straight through.

## Document-type identifier

Not everything a court publishes is an opinion. Before any body parsing, the extractor
classifies the document into a `DocType`:

`opinion` · `order` · `notice` · `certificate-of-judgment` · `unknown`

A court lists styles it classifies but does **not** parse via `SKIP_BODY_TYPES`. For
Alabama, `CERTIFICATE OF JUDGMENT` (detected from a page-1 centered heading) is
recognized and tagged but its body is skipped.

## How courts plug in

Reusable mechanics live on `BaseExtractor`; courts stay thin. Most per-court behavior is
opt-in via class-level config flags rather than overridden methods:

| flag | what it does |
|------|--------------|
| `footnote_sep_rect` | x-range of the rect that marks the footnote separator line |
| `running_header_docket` | drop the repeated docket running-header on pages 2+ |
| `strip_author_trailing_mark` | trim a trailing mark off the author byline |
| `banner_center_min_size` | font size at/above which a line is treated as a centered banner |
| `skip_notice_headmatter` | skip headmatter segments on notice-style docs |

`AlabamaSupreme` (`restatement/courts/ala.py`) is the first and reference court — it sets
all five flags and is otherwise a thin subclass. Unknown court ids fall back to
`GenericExtractor`.

The author-byline parser is the **only** place that uses regex; everything else is
deterministic layout logic over pdfplumber geometry. (We avoid regex unless it's
genuinely warranted.)

## Layout

```
restatement/
  models.py           ExtractedDocument / Opinion / Block / Footnote / DocType — the contract
  base.py             BaseExtractor: all the shared layout heuristics + hooks
  registry.py         court id -> extractor class
  cli.py              python -m restatement.cli
  courts/
    ala.py            AlabamaSupreme — reference court
    generic.py        fallback extractor for unknown courts
  render/
    casebody.py       ExtractedDocument -> Harvard casebody XML
```

## Fidelity

The rewrite is verified byte-for-byte against the original `ca1/casebody` output across
the full Alabama corpus (466 PDFs). The only diff is a Pillow-version PNG re-encode of an
embedded image, which is structurally identical. To re-check a single PDF:

```
diff <(python -m restatement.cli ala FILE.pdf --xml) \
     <(cd ../ca1 && python -m casebody.cli ala FILE.pdf)
```

## Status & next steps

- ✅ Alabama Supreme Court — opinions and no-opinion decisions parse as opinions;
  certificates of judgment classified but not parsed.
- Next courts are added by subclassing `BaseExtractor`, setting the config flags for
  their layout, and registering the id in `registry.py`.