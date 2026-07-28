"""The returned-criteria contract.

An extractor's job is to turn a court PDF into a single structured
``ExtractedDocument``. This mirrors the Juriscraper opinion-scraper idea:
the base class defines *what gets returned* (a fixed field set), and each
court subclass only fills/overrides the parts that differ for its layout.

Rendering (Harvard casebody XML, HTML, JSON, ...) is a separate concern that
consumes this model — see ``centralia.render``.

Inline formatting inside paragraph/footnote text is preserved as a small set
of inline tags baked into the string (``<em>``, ``<strong>``, ``<u>``,
``<footnotemark>``, ``<pagenumber>``). Keeping it as marked-up text rather
than a nested run-tree keeps the proven layout logic intact and lets any
renderer pass the markup straight through.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Document type — the "document style identifier"
# ---------------------------------------------------------------------------
#
# Not everything a court publishes is an opinion. Alabama (and every other
# court) also issues orders, clerk notices, errata, etc. The extractor
# classifies the document up front so downstream consumers can branch on it
# instead of assuming an opinion body exists.


class DocType:
    OPINION = "opinion"  # has one or more authored opinions
    ORDER = "order"  # court order / per-curiam disposition, no authored opinion
    NOTICE = "notice"  # clerk notice / advisory / calendar — administrative
    # An attorney-submitted document, not a court ruling: a motion, a position
    # paper, or a [PROPOSED] order the judge has not signed. It sits on the
    # docket in the same reporter but carries no judicial author — a signed
    # order is ORDER/OPINION, an unsigned filing is FILING.
    FILING = "filing"
    # Clerk's certificate that judgment was entered — administrative, no
    # opinion body worth parsing.
    CERTIFICATE = "certificate-of-judgment"
    UNKNOWN = "unknown"  # recognizable text but no confident classification

    ALL = (OPINION, ORDER, NOTICE, FILING, CERTIFICATE, UNKNOWN)


# ---------------------------------------------------------------------------
# Body model
# ---------------------------------------------------------------------------


@dataclass
class Block:
    """One block-level element inside an opinion or order body.

    ``kind`` is one of: ``p`` | ``blockquote`` | ``heading`` | ``list-item`` |
    ``ordered-list-item`` | ``image`` | ``table``. For textual blocks the
    content is in ``text`` (inline-marked-up). Consecutive list-item blocks form
    one list. For ``image``/``table`` the content is in ``payload``.
    """

    kind: str
    text: str = ""
    page: int | None = None
    payload: dict = field(default_factory=dict)


@dataclass
class Footnote:
    label: str
    # Each paragraph is (tag, text) where tag is "p" or "blockquote".
    paragraphs: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Opinion:
    type: str  # majority | dissent | concurrence | ...
    author: str  # raw author byline, e.g. "BRYAN, Justice."
    blocks: list[Block] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level returned criteria
# ---------------------------------------------------------------------------


@dataclass
class ExtractedDocument:
    """Everything an extractor returns for one PDF.

    The headmatter fields are the structured "criteria"; ``opinions`` holds
    the body. Fields a given court doesn't populate stay at their empty
    default so consumers can rely on the shape.
    """

    # Provenance / classification
    court_id: str = ""
    court_label: str = ""
    doc_type: str = DocType.UNKNOWN
    n_pages: int = 0
    layout_ok: bool = True
    # True when the PDF is a scanned image with an OCR text layer, not a
    # born-digital document. The engine trusts page geometry (margins,
    # x-positions, font size, drawn rules); OCR'd scans report estimated,
    # unreliable geometry, so such documents are detected up front and NOT
    # processed — only flagged.
    non_digital: bool = False
    source_path: str | None = None
    # Count of unmapped '(cid:N)' glyphs in the source text — a font-encoding
    # problem (a glyph the PDF's font declares but doesn't map to a character).
    # Surfaced as a review flag; a court can map the glyph in correct_page_geometry.
    cid_glyphs: int = 0

    # Headmatter criteria
    decision_date: str | None = None
    docket_number: str | None = None
    other_docket: str | None = None
    parties: list[str] = field(default_factory=list)
    motion: str | None = None
    history: str | None = None
    parent_case: str | None = None
    lower_court: str | None = None
    disposition: str | None = None
    attorneys: str | None = None
    # The panel of judges who heard the case (structured), plus the raw
    # <judges> string as the court printed it.
    panel: list[str] = field(default_factory=list)
    judges: str | None = None
    submitted: str | None = None
    # Raw, loss-resistant headmatter dump (verbatim lines / caption columns /
    # divider markers) for anything the structured parser doesn't categorize.
    summary: list = field(default_factory=list)
    # Optional faithful headmatter: positioned lines (text/x0/top/size/bold)
    # plus the caption-box rule geometry, for a visual facsimile in the review
    # HTML. Empty when a court doesn't provide it (falls back to ``summary``).
    headmatter_lines: list = field(default_factory=list)
    caption_box: dict | None = None

    # An official syllabus / headnote / case summary that precedes the opinion
    # and is expressly not part of it (Colorado's "SUMMARY" page, Connecticut's
    # "Syllabus"). Kept as its own block, separate from headmatter and body.
    syllabus: list = field(default_factory=list)

    # Reporter headnotes that precede the opinion — bold topical headings and
    # their summary prose, set on their own page(s) before the caption
    # (Maryland's reported opinions). Their own section, not headmatter or
    # body; distinct from ``syllabus`` (a court-written case summary).
    headnotes: list = field(default_factory=list)

    # Body
    opinions: list[Opinion] = field(default_factory=list)
    headmatter_footnotes: list[Footnote] = field(default_factory=list)

    # Content found and removed from the headmatter dump (publication
    # notices, stamps, etc.) — surfaced for review, not part of the body.
    dropped: list = field(default_factory=list)

    # Trailing matter after the last opinion (counsel names/addresses, "See
    # next page for ... counsel" blocks) — surfaced separately, not body.
    trailer: list = field(default_factory=list)

    # The signature block lifted off the end of the last opinion: the '/s/'
    # conformed signature (or the underscore signature rule), the printed
    # name, and the signer's title line. Rendered as its own section.
    signature: list = field(default_factory=list)

    # Completeness safety net: source lines the pipeline placed in NO other
    # section, swept up at the end of extraction so nothing is silently lost.
    # Each entry is {"page": int, "text": str, "kind": "content" | "furniture"}
    # — "furniture" is identifiable junk (stamps/rules/running headers) and
    # "content" is real text that still needs a proper home. Rendered inside
    # the Removed box. Should be empty (of "content") when a court is done; a
    # non-empty residual is the review to-do, NOT a place to leave things.
    residual: list = field(default_factory=list)

    # Diagnostics
    warnings: list[str] = field(default_factory=list)
