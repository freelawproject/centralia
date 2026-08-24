# centralia

Court PDF opinion extractor: a PDF plus a court id in, a typed document out.

Requires Python 3.12 or newer.

```sh
python -m pip install centralia
```

```python
from centralia import read

r = read("opinion.pdf", court_id="nmariana")   # path, bytes, or file object
```

## What `read` returns

```python
r["status"]        # valid | review | scanned | failed
r["court_id"]      # the id you passed, echoed back
r["cluster"]       # the case: citation, docket, dates (as printed + ISO), panel, parties
r["opinions"]      # one entry per writing, each with its author, pages, html and text
r["headmatter"]    # the caption block: rows, by_role, text, html, footnotes, untinted
r["endmatter"]     # anything after the last writing, same shape as headmatter
r["sections"]      # named sections the court printed (syllabus, headnotes) where it did
r["removed"]       # every row taken out as furniture: kind, page, text, bbox
r["warnings"]      # what the reader wants you to know about the source
r["diagnostics"]   # page facts and anything unplaced — reported, never judged
r["html"]          # the document's text, without review furniture
r["review_html"]   # the reviewer's page: criteria box, Removed panel, role tints
r["casebody"]      # Harvard casebody XML
r["versions"]      # what produced this reading
```

`headmatter` and `endmatter` carry a `by_role` map — which rows the court's own
reader claimed and as what (`court`, `caption`, `docket`, `date`, `title`,
`counsel`, `panel`, `citation`, `lower-court`, `syllabus`, `case-info`,
`author`) — and `untinted`, the rows no reader claimed. That second number is
the honest measure of how much of a caption was actually read.

`removed` is the audit trail: nothing is dropped silently, so a running head,
a folio, an e-filing stamp, a chambers letterhead or a caption-box graphic all
appear here with the page and box they came from.

## Courts still being worked on

```python
from centralia import read, released_courts, CourtNotReleased, UnknownCourt

released_courts()                      # frozenset of ids that are finished
read("x.pdf", court_id="mad")          # raises CourtNotReleased
read("x.pdf", court_id="mad", allow_pending=True)   # read it anyway
read("x.pdf", court_id="typo")         # raises UnknownCourt
```

An unregistered id raises rather than falling back: core's generic reader would
still return `status: valid`, just read worse, and a typo should not look like a
thin court.

## Lower level, for callers that want the objects

```python
from centralia import extract, render_opinion

result = extract("opinion.pdf", court_id="mont")
result.document          # typed Document
result.trace             # per-decision evidence chains
render_opinion(result.document.opinions[0])
```

Also exported: `render_html`, `render_body`, `render_headmatter`,
`render_casebody`, `opinion_text`, the model types (`Document`, `Criteria`,
`Meta`, `Opinion`), and the date helpers `to_iso` / `all_iso`. Pass
`include_document=True` to `read` to get the typed `Document` alongside the
dict.

## Dates

Dates are returned twice: as the court printed them (`date_filed`) and as
`YYYY-MM-DD` where that can be read without guessing (`date_filed_iso`, or
`None`). `diagnostics["dates_unparsed"]` names the ones that did not parse.

## Status is a report, not a gate

`diagnostics` carries the page-level facts a caller needs to decide for itself:
which pages are a raster (`scan_pages`), which pages have no text layer at all
so their words are absent (`text_missing_pages`), which carry unmapped glyphs
(`cid_pages`), and what the extractor could not place (`residual`).
