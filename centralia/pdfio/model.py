"""The line/page model every downstream consumer shares.

Lines keep their raw pdfplumber char dicts (with real space glyphs — see
build._text_lines) so later stages can re-measure anything; the computed
views (plain text, type size, boldness) are cached on first use.

Nothing here is court-specific and nothing is dropped: rotated text and
whatever else can't be represented as an ordinary line is carried on the
PageModel as artifacts, so the audit can always account for it.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import cached_property


@dataclass(eq=False)
class Line:
    """One visual text line (or one side of a split visual row)."""

    id: int                     # stable within the document
    page: int                   # 1-based page number
    x0: float
    x1: float
    top: float
    bottom: float
    chars: list                 # raw pdfplumber char dicts, space glyphs kept
    col: str | None = None      # "L"/"R" when split at a vertical rule
    row: int | None = None      # shared by lines split out of one visual row

    @cached_property
    def plain(self) -> str:
        """Plain text with measured word breaks (see text.plain_text)."""
        from .text import plain_text
        return plain_text(self.chars)

    @cached_property
    def size(self) -> float:
        """The line's own type size — the MODE over inked glyphs, ties toward
        larger (a few oversized glyphs must not redefine the line; a lone
        justification space with its own font instance is not evidence).

        SMALL CAPS report the full size: cafc sets attorney names in small
        caps, which lowered the row's dominant size below its neighbours and
        split the counsel block mid-word. When every glyph at the smaller
        size is uppercase-or-non-alpha AND the larger size is present on the
        same row, the smaller tier is a typeface choice, not a size change."""
        inked = [(round(c.get("size", 0) or 0, 1), c.get("text") or "")
                 for c in self.chars if (c.get("text") or "").strip()]
        if not inked:
            return max((round(c.get("size", 0) or 0, 1) for c in self.chars),
                       default=0.0)
        counts = Counter(s for s, _ in inked)
        top = max(counts.values())
        mode = max(s for s, n in counts.items() if n == top)
        biggest = max(counts)
        if biggest > mode:
            smaller = [t for s, t in inked if s < biggest]
            if smaller and all(not ch.isalpha() or ch.isupper()
                               for t in smaller for ch in t):
                return biggest
        return mode

    @cached_property
    def font(self) -> str:
        fonts = Counter((c.get("fontname") or "") for c in self.chars
                        if (c.get("text") or "").strip())
        return (fonts.most_common(1)[0][0] if fonts else "").split("+")[-1]

    @cached_property
    def bold(self) -> bool:
        return "Bold" in self.font

    @cached_property
    def all_bold(self) -> bool:
        """Every alphanumeric glyph bold. Punctuation is routinely left roman
        inside a bold passage, so it doesn't vote."""
        seen = False
        for c in self.chars:
            t = c.get("text") or ""
            if not t.strip() or not t.isalnum():
                continue
            seen = True
            if "Bold" not in (c.get("fontname") or ""):
                return False
        return seen

    @cached_property
    def all_emphasized(self) -> bool:
        """Every alphanumeric glyph bold OR italic/oblique."""
        seen = False
        for c in self.chars:
            t = c.get("text") or ""
            if not any(ch.isalnum() for ch in t):
                continue
            seen = True
            f = c.get("fontname") or ""
            if not any(s in f for s in ("Bold", "Italic", "Oblique")):
                return False
        return seen

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    def __repr__(self) -> str:  # keeps debug dumps readable
        return (f"Line(p{self.page} #{self.id} top={self.top:.1f} "
                f"x0={self.x0:.1f} {self.plain[:40]!r})")


@dataclass(frozen=True)
class DrawnRule:
    """A horizontal rule the PDF actually draws (rect, vector line, or a
    hairline image), merged from its pieces. `strokes` counts how many raw
    pieces were merged in — a triple-stroke pleading rail reports 3."""

    page: int
    top: float
    x0: float
    x1: float
    source: str          # "rect" | "line" | "image"
    strokes: int = 1

    @property
    def width(self) -> float:
        return self.x1 - self.x0


@dataclass(frozen=True)
class VRule:
    """A vertical rule (caption divider, pleading gutter, box edge)."""

    page: int
    x: float
    top: float
    bottom: float
    source: str
    strokes: int = 1

    @property
    def height(self) -> float:
        return self.bottom - self.top


@dataclass(frozen=True)
class TableGrid:
    """A table the page DRAWS: the edges of a ruled box and of the rules
    inside it. ``col_edges``/``row_edges`` are the drawn rules themselves, so
    n edges bound n-1 cells; the cell text is read off the lines that sit
    inside each one (see pdfio.tables)."""

    page: int
    col_edges: tuple[float, ...]     # vertical rule x, left -> right
    row_edges: tuple[float, ...]     # horizontal rule top, top -> bottom

    @property
    def x0(self) -> float:
        return self.col_edges[0]

    @property
    def x1(self) -> float:
        return self.col_edges[-1]

    @property
    def top(self) -> float:
        return self.row_edges[0]

    @property
    def bottom(self) -> float:
        return self.row_edges[-1]

    @property
    def n_cols(self) -> int:
        return len(self.col_edges) - 1

    @property
    def n_rows(self) -> int:
        return len(self.row_edges) - 1

    def holds(self, line) -> bool:
        """True if this text line sits inside the box."""
        mid_y = (line.top + line.bottom) / 2
        return (self.top - 2.0 <= mid_y < self.bottom
                and self.x0 - 6.0 <= line.x0 <= self.x1 + 6.0)


@dataclass(frozen=True)
class ImageRef:
    page: int
    x0: float
    x1: float
    top: float
    bottom: float
    name: str = ""


@dataclass
class PageModel:
    number: int                 # 1-based
    width: float
    height: float
    lines: list[Line] = field(default_factory=list)
    h_rules: list[DrawnRule] = field(default_factory=list)
    v_rules: list[VRule] = field(default_factory=list)
    tables: list[TableGrid] = field(default_factory=list)
    images: list[ImageRef] = field(default_factory=list)
    has_diagonal: bool = False  # diagonal strokes (X-capped pleading boxes)
    rotated_text: str = ""      # sideways glyphs, in PDF char order (furniture)
    ink_chars: int = 0          # printable upright glyph count (scan triage)
    cid_chars: int = 0          # unmapped (cid:N) glyph count
    image_area: float = 0.0     # summed image area / page area, 0..1
    # Every distinct /BaseFont the page's glyphs name, kept WHOLE — with the
    # subset tag that `Line.font` strips off. The tag is the evidence: a
    # born-digital page embeds its faces and pdfminer reports them subsetted
    # ('BCDEEE+TimesNewRomanPSMT'), while an OCR text layer names the
    # non-embedded standard faces or Tesseract's own 'GlyphLessFont'. That is
    # what tells a scan from a page merely printed over a background image —
    # see classify.ocr_text_layer.
    fonts: set = field(default_factory=set)
    events: list = field(default_factory=list)  # (quirk, detail) trace events

    def event(self, quirk: str, detail: str) -> None:
        self.events.append((quirk, detail))


@dataclass
class PdfModel:
    path: str
    pages: list[PageModel] = field(default_factory=list)

    @property
    def n_pages(self) -> int:
        return len(self.pages)

    def all_lines(self):
        for page in self.pages:
            yield from page.lines
