"""The typed document model. Every dunder sentinel of the old system is a
real variant here; consumers dispatch on type, never on magic keys.

Inline markup stays as marked-up strings — the proven vocabulary
(`<em> <strong> <u> <footnotemark>N</footnotemark> <pagenumber value=""/>
<centered> <flushright>`, literal text XML-escaped). ``Markup = str`` marks
which fields carry it.

Rule vs Divider vs Gap are three distinct things, type-enforced:
a Rule is drawn/typed BY THE PAGE and is rendered; a Divider is a semantic
boundary and draws nothing; a Gap is vertical rhythm only. "Never invent
layout" follows from the types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal, Union

Markup = str  # XML-escaped text carrying the inline-markup vocabulary


class DocType(StrEnum):
    OPINION = "opinion"
    ORDER = "order"
    RR = "report-and-recommendation"
    JUDGMENT = "judgment"
    FILING = "filing"                 # attorney filing, not the court's writing
    CERTIFICATE = "certificate-of-judgment"
    NOTICE = "notice"
    SCAN = "scan"                     # non-digital: a SUCCESS status
    HYBRID = "hybrid"                 # proposed order signed by the judge
    UNKNOWN = "unknown"


# Types for which an empty opinions list is CORRECT output.
NO_BODY_EXPECTED = frozenset(
    {DocType.NOTICE, DocType.FILING, DocType.CERTIFICATE,
     DocType.JUDGMENT, DocType.SCAN}
)


class Align(StrEnum):
    LEFT = "L"
    CENTER = "C"
    RIGHT = "R"


@dataclass(frozen=True)
class Prov:
    """Provenance: where a placed item came from. line_ids are pdfio Line ids,
    stable within one extraction of one document."""

    page: int
    line_ids: tuple[int, ...] = ()


# --------------------------------------------------------------------------
# flow content (opinion bodies, footnotes, syllabus, headnotes, trailer…)
# --------------------------------------------------------------------------

@dataclass
class Paragraph:
    text: Markup
    prov: Prov
    continuation: bool = False   # continues a paragraph from the previous page
    align: str = ""              # "right" — a signature block set right of
                                 # the measure keeps its position
    role: str = ""               # "disposition" — the closing REMANDED/
                                 # AFFIRMED block, marked for downstream


@dataclass
class Blockquote:
    text: Markup
    prov: Prov


@dataclass
class Heading:
    text: Markup
    prov: Prov
    level: int = 1


@dataclass
class ListItem:
    text: Markup
    prov: Prov
    ordered: bool = False


@dataclass
class TableBlock:
    rows: list[list[Markup]]
    prov: Prov
    has_header: bool = True


@dataclass
class ImageBlock:
    src: str                     # data: URI
    prov: Prov
    width: float = 0.0
    height: float = 0.0
    role: str = ""               # "seal" | "signature-graphic" | ""


Block = Union[Paragraph, Blockquote, Heading, ListItem, TableBlock, ImageBlock]


# --------------------------------------------------------------------------
# headmatter content — replaces __hm__/__caption__/__DIVIDER__/__RULE__/""/…
# --------------------------------------------------------------------------

@dataclass
class HmLine:
    """One styled headmatter row: the page's own alignment, size and weight.
    ``rel`` is the offset from the row's own column axis — captions centered
    on their own column (Maryland) center on that axis, not the page's."""

    text: Markup
    prov: Prov
    align: Align = Align.LEFT
    x0: float = 0.0
    size: float = 0.0
    bold: bool = False
    italic: bool = False
    rel: float = 0.0
    # What a court reader identified this row AS. The vocabulary, as of
    # 2026-08-19 — every one of these renders with its own tint and margin
    # label in `render/html.py`, and the legend names the ones a document
    # actually uses:
    #
    #   court        the court naming itself — its name, division, seat, term
    #                (called 'banner' until 2026-08-19; the old name is still
    #                 accepted by the render for back-compatibility)
    #   publication  'PUBLISHED' / 'NOT FOR PUBLICATION' / 'NOT PRECEDENTIAL'
    #   citation     the court's own public-domain cite ('2026-Ohio-2065')
    #   title        what the paper calls itself ('OPINION', 'ORDER')
    #   docket date  the numbers and the dates
    #   panel        who sat; `author` who the caption says WROTE it, where a
    #                court announces its author instead of signing
    #   caption      the parties and the pivot
    #   lower-court  the court below, its number, its judge
    #   counsel      the appearances
    #   headnotes    the Reporter's SUBJECT list — not a précis of the case
    #   summary      a précis the court or reporter actually writes
    #   disposition  what the court DID, stated in the headmatter
    #   case-info    caption apparatus that is none of the above ('Chapter 7',
    #                'Submitted on the briefs.', '(In re: …)')
    #
    # The headmatter renders WHOLE — nothing is lifted out of it — so the way
    # to show how it was read is to mark the rows in place. Empty when no
    # reader claimed the row, which is the measurement of what is unread.
    role: str = ""


@dataclass
class CaptionBlock:
    """Two-column caption, rows paired by source row. ``rail`` is the glyph
    the page draws the middle with ()], §, :, *, |…) or None for a
    whitespace gutter; ``fp`` is the measured page-1 signature — the renderer
    draws borders from THIS object, so label and reproduction cannot
    disagree."""

    left: list[HmLine] = field(default_factory=list)
    right: list[HmLine] = field(default_factory=list)
    rail: str | None = None
    rail_rows: int = 0
    style_id: str | None = None
    fp: dict = field(default_factory=dict)
    prov: Prov = field(default_factory=lambda: Prov(1))


@dataclass
class Rule:
    """The page drew (or typed) a horizontal rule — render it."""

    prov: Prov
    span: Literal["full", "left", "right", "center"] = "full"
    typed: bool = False


@dataclass
class Divider:
    """A semantic component boundary. Draws NOTHING."""

    prov: Prov


@dataclass
class Gap:
    """Vertical rhythm: a real blank band on the page."""

    lines: int = 1


HmItem = Union[HmLine, CaptionBlock, Rule, Divider, Gap, ImageBlock]


# --------------------------------------------------------------------------
# footnotes / opinions
# --------------------------------------------------------------------------

@dataclass
class Footnote:
    label: str
    blocks: list[Block] = field(default_factory=list)


@dataclass
class Opinion:
    type: str                    # majority | concurrence | dissent | order | …
    author: Markup               # the byline as printed
    author_name: str = ""
    author_title: str = ""
    author_prov: Prov = field(default_factory=lambda: Prov(1))
    caption: list[HmItem] = field(default_factory=list)
    blocks: list[Block] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    signature: list[Block] = field(default_factory=list)


# --------------------------------------------------------------------------
# criteria — ONE representation of the case metadata, no dict twin
# --------------------------------------------------------------------------

@dataclass
class Criteria:
    publication_status: str | None = None   # "published" | "unpublished"
    decision_date: str | None = None
    docket_number: str | None = None
    other_dockets: list[str] = field(default_factory=list)
    # THE PUBLIC-DOMAIN (NEUTRAL) CITATION the court assigns its own opinion
    # — '2026 IL 130930', '2026 ND 72', '2026-Ohio-2065'. It is neither a
    # docket nor a companion appeal, and stored as either it displaces a
    # real value: ill was recording the citation as `docket_number` and the
    # actual docket as `other_dockets`. Three courts print one (ill, nd,
    # ohio) and every public-domain-citation state will.
    citation: str | None = None
    # The number the court BELOW gave the case ('Bankruptcy Case No.
    # 11-43854-CJP', 'D.C. No. 2:20-cv-10719'). Distinct from
    # `other_dockets`, which is companion APPEALS consolidated into this
    # one — both were going into that bucket, so a reader could not tell
    # 'this case, downstairs' from 'another case, alongside'.
    lower_court_docket: list[str] = field(default_factory=list)
    parties: list[str] = field(default_factory=list)
    attorneys: str | None = None
    judges: str | None = None
    panel: list[str] = field(default_factory=list)
    disposition: str | None = None
    lower_court: str | None = None
    history: str | None = None
    submitted: str | None = None
    motion: str | None = None
    # --- what the page NAMES itself, kept beside the parsed forms ---------
    # The printed form and the normalized form are both facts, and choosing
    # between them loses one: the caption rows are auditable against the
    # page, the case name is queryable, and neither substitutes for the
    # other. (ca2 prints 'AMANDA BROOKS,' / 'Plaintiff-Appellant,' / 'v.
    # 25-1830-cv' / six defendant entities — joined wholesale that reads
    # 'AMANDA BROOKS, Plaintiff-Appellant, BRIGHT HORIZONS …'.)
    title: str | None = None            # 'SUMMARY ORDER' — the paper's name
    # WHO THE HEADMATTER SAYS WROTE IT. Some courts do not sign their
    # opinions; they ANNOUNCE the author on the cover, over the body — 'OPINION
    # BY / PRESIDENT JUDGE COHN JUBELIRER   FILED: May 19, 2026' (pacommwct).
    # `HmLine.role` has carried an `author` role for that row all along; this
    # is where its value goes, so the name survives even though the writing
    # itself is unsigned and has no byline of its own.
    author: str | None = None
    court: str | None = None            # the deciding court, as printed
    short_case_name: str | None = None  # the running head's own short form
    case_name: str | None = None        # 'X v. Y', built from party names
    caption: list[str] = field(default_factory=list)   # rows, verbatim
    panel_line: str | None = None       # the roster as printed
    lower_court_judge: str | None = None  # who tried it, as the origin says
    headmatter_style: str | None = None  # the layout contract recognized


# --------------------------------------------------------------------------
# side channels
# --------------------------------------------------------------------------

@dataclass
class Dropped:
    """Identified junk, surfaced: stamps, folios, running heads, seals."""

    text: str
    prov: Prov
    kind: str                    # stamp | folio | running-head | margin | rotated | …


@dataclass
class Residual:
    """A source line no stage claimed. kind='content' is the worklist;
    kind='furniture' is repeated margin matter the sweep recognized late."""

    text: str
    prov: Prov
    kind: Literal["content", "furniture"] = "content"


@dataclass
class Meta:
    court_id: str
    court_label: str = ""
    doc_type: DocType = DocType.UNKNOWN
    doc_style: str | None = None   # named layout contract that matched
    n_pages: int = 0
    source_path: str = ""
    # WHAT THE PAPER IS, as a value rather than a sentence. `doc.warnings`
    # already says it in prose, but a consumer that must DECIDE something —
    # the review banner, the casebody projection, whatever ingests this
    # downstream — should not have to match on the wording of a warning.
    #   ""          born-digital: the text is the court's own type
    #   "ocr-scan"  a scan with an OCR text layer. The content is real and
    #               usable, but every coordinate is the scanner's guess and
    #               the glyphs are a machine's reading of an image.
    #   "scan"      a scan with no usable text layer; not parsed.
    source_kind: str = ""


# --------------------------------------------------------------------------
# the document
# --------------------------------------------------------------------------

@dataclass
class Document:
    meta: Meta
    criteria: Criteria = field(default_factory=Criteria)
    headmatter: list[HmItem] = field(default_factory=list)
    headnotes: list[Block] = field(default_factory=list)
    syllabus: list[Block] = field(default_factory=list)
    summary: list[Block] = field(default_factory=list)   # staff summary
                       # ('SUMMARY*' — ca9; unlabeled front prose — tenn)
    attorneys: list[Block] = field(default_factory=list)
    opinions: list[Opinion] = field(default_factory=list)
    headmatter_footnotes: list[Footnote] = field(default_factory=list)
    signature: list[Block] = field(default_factory=list)
    trailer: list[Block] = field(default_factory=list)
    dropped: list[Dropped] = field(default_factory=list)
    residual: list[Residual] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
