# centralia

Court PDF opinion extractor: a PDF plus a court id in, a typed document out.

**[Try it in your browser →](https://freelawproject.github.io/centralia/)**
No install, nothing uploaded — the real package runs client-side on
[Pyodide](https://pyodide.org), and your PDF is parsed in the tab.

```sh
python -m pip install centralia      # Python 3.12+
```

```python
from centralia import read

r = read("opinion.pdf", court_id="mont")   # path, bytes, or file object

r["cluster"]["docket_number"]              # 'DA 25-0040'
[o["author"] for o in r["opinions"]]
# ['Justice Laurie McKinnon delivered the Opinion of the Court.',
#  'Justice James Jeremiah Shea, concurring.',
#  'Justice Jim Rice, dissenting.']
```

Three writings, each with its own author, footnotes and text — recovered from
a PDF that labels none of them.

## The problem it solves

Getting the *text* out of a court PDF is easy; `pdftotext` does it. What is
hard is that an opinion is a document with **parts**, and the PDF says nothing
about them. Nothing marks which lines are the caption, where the syllabus ends
and the opinion begins, which paragraphs belong to the dissent rather than the
majority, whose footnote is whose, or which line is a page number instead of a
sentence. All of it has to be recovered from how the page is *set* — position,
size, leading, indentation, and the rules the printer drew.

And every court sets its pages differently. centralia reads **241** of them.

Thresholds are measured from each document's own geometry rather than tuned
per court, and nothing is ever dropped silently: every row removed as
furniture is returned in `removed`, with the page and box it came from, so
"did we lose anything?" is arithmetic instead of a judgment call.

Of the 241 courts wired, **191 are released** through this API — meaning every
document in that court's test corpus has been read and checked by a human. The
rest raise rather than quietly returning a worse reading (see
[Courts still being worked on](#courts-still-being-worked-on)).

## What `read` returns

```python
r["status"]        # valid | review | scanned | failed
r["court_id"]      # the id you passed, echoed back
r["cluster"]       # the case: citation, docket, dates (as printed + ISO), panel, parties
r["opinions"]      # one entry per writing: author, pages, footnotes, html and text
r["headmatter"]    # the caption block: rows, by_role, text, html, html_inline,
                   #   footnotes, untinted
r["endmatter"]     # anything after the last writing, same shape, minus the notes
r["sections"]      # named sections the court printed (syllabus, headnotes) where it did
r["removed"]       # every row taken out as furniture: kind, page, text, bbox
r["warnings"]      # what the reader wants you to know about the source
r["diagnostics"]   # page facts and anything unplaced — reported, never judged
r["html"]          # the document's text, without review furniture
r["review_html"]   # the reviewer's page: criteria box, Removed panel, role tints
r["casebody"]      # Harvard casebody XML
r["versions"]      # what produced this reading, centralia's own version first
```

`headmatter` and `endmatter` carry a `by_role` map — which rows the court's own
reader claimed and as what (`court`, `caption`, `docket`, `date`, `title`,
`counsel`, `panel`, `citation`, `lower-court`, `syllabus`, `case-info`,
`author`) — and `untinted`, the rows no reader claimed. That second number is
the honest measure of how much of a caption was actually read.

`removed` is the audit trail: nothing is dropped silently, so a running head,
a folio, an e-filing stamp, a chambers letterhead or a caption-box graphic all
appear here with the page and box they came from.

### The HTML an ingest stores

A writing's `html`, and the cover's `html_inline`, are the *portable* renders:
no chip a host page would print itself, nothing set in classes only this
package's stylesheet knows, and the footnotes **wired** — each mark anchors to
its note and each note links back, namespaced per writing (`ref-o2-7` /
`fn-o2-7`) so several writings shown on one host page, each restarting its
numbering at 1, cannot collide. The cover's notes travel inside `html_inline`
rather than beside it, so a substituted party's `*` is not a dangling mark.
`review_html` is the other kind: the reviewer's page, which does assume our CSS.

`versions` names the centralia that wrote the payload alongside the pipeline's
own versions, so a consumer decides payload shape by a number instead of
sniffing the markup.

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
`render_hm_inline`, `render_casebody`, `opinion_text`, and
`render_opinion_ingest(op, ns, hm_sig="")` — the portable form of a writing
that `read` puts in `opinions[].html`, where `render_opinion` is the review
page's own drawing. Plus the model types (`Document`, `Criteria`, `Meta`,
`Opinion`) and the date helpers `to_iso` / `all_iso`. Pass
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


## Contributing

[**DEVELOPMENT.md**](DEVELOPMENT.md) is the orientation: how the engine works
and why it works that way, the eleven pipeline stages, a file-by-file map,
when page geometry can be trusted and when it cannot, how a court is added,
the five oracles that say whether a reading is right, and what is left to do.

The test corpus is ~10,000 real court PDFs. It is too large for git, so it
lives as a list of links:

```sh
uv sync --dev
uv run python scripts/fetch_corpus.py               # fetch the corpus
uv run python harness/cli.py render $(ls assets)    # render every court
uv run python harness/cli.py serve                  # the review viewer
```
