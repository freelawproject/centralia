# centralia

Court PDF opinion extractor: a PDF plus a court id in, a typed document out.

Requires Python 3.12 or newer.

```sh
python -m pip install centralia
```

```python
from centralia import read

r = read("opinion.pdf", court_id="nmariana")   # path, bytes, or file object

r["status"]       # valid | review | scanned | failed
r["cluster"]      # the case: citation, docket, dates (as printed + ISO), panel, parties
r["opinions"]     # one entry per writing, each with its author, pages, html and text
r["diagnostics"]  # page facts and anything unplaced — reported, never judged
r["html"]         # the document's text, without review furniture
r["review_html"]  # the reviewer's page: criteria box, Removed panel, role tints
r["casebody"]     # Harvard casebody XML
```

Lower level, for callers that want the objects:

```python
from centralia import extract, render_opinion

result = extract("opinion.pdf", court_id="mont")
result.document          # typed Document
result.trace             # per-decision evidence chains
render_opinion(result.document.opinions[0])
```

Dates are returned twice: as the court printed them (`date_filed`) and as
`YYYY-MM-DD` where that can be read without guessing (`date_filed_iso`, or
`None`). `diagnostics["dates_unparsed"]` names the ones that did not parse.

`status` is a report, not a gate. `diagnostics` carries the page-level facts a
caller needs to decide for itself: which pages are a raster (`scan_pages`),
which pages have no text layer at all so their words are absent
(`text_missing_pages`), which carry unmapped glyphs (`cid_pages`), and what
the extractor could not place (`residual`).
