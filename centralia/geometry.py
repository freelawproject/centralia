"""Measured document geometry. Constants are floors/caps; measurement only
ever tightens. No evidence -> None, and callers fall back to profile floors.

Measured from the lines that RUN TO the right measure — wrapped continuation
lines, the one population that always sits on the true body margin. Judged
against a per-court constant instead, a court whose real column sits further
right reads as "indented on both margins" and its entire body classifies as
one long blockquote.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .pdfio.model import Line, PdfModel


@dataclass(frozen=True)
class DocGeometry:
    body_x0: float          # modal left edge of full-measure lines
    right_x1: float         # 95th-percentile right edge (robust to strays)
    lead: float | None      # dominant baseline-to-baseline distance
    body_size: float        # modal type size of full-measure lines
    page_width: float
    page_height: float

    @property
    def column(self) -> float:
        return self.right_x1 - self.body_x0


def measure(model: PdfModel) -> DocGeometry | None:
    """Measure the body column from the document's own lines. Interior pages
    when the document has them (the caption page skews the columns), the
    whole document otherwise. Too small to measure confidently -> None."""
    if not model.pages:
        return None
    pw = model.pages[0].width
    ph = model.pages[0].height
    if model.n_pages >= 3:
        lines = [l for p in model.pages[1:] for l in p.lines if l.plain.strip()]
    else:
        lines = [l for p in model.pages for l in p.lines
                 if l.plain.strip() and l.top > 80]
    if len(lines) < 12:
        return None
    x1s = sorted(l.x1 for l in lines)
    right_x1 = x1s[int(0.95 * (len(x1s) - 1))]
    full = [l for l in lines if l.x1 >= right_x1 - 36]
    if len(full) < 6:
        return None
    body_x0 = float(Counter(round(l.x0) for l in full).most_common(1)[0][0])
    sizes = Counter(l.size for l in full if l.size)
    body_size = float(sizes.most_common(1)[0][0]) if sizes else 0.0
    # Dominant leading from consecutive same-page line pairs. A court can
    # print two templates (16pt slips AND 36pt double-spaced opinions), so
    # the lead is a fact about the DOCUMENT, never about the court.
    leads: Counter = Counter()
    for page in model.pages:
        seq = sorted((l for l in page.lines if l.plain.strip()),
                     key=lambda l: l.top)
        for a, b in zip(seq, seq[1:]):
            gap = round(b.top - a.top)
            if 5 < gap < 60:
                leads[gap] += 1
    lead = float(leads.most_common(1)[0][0]) if sum(leads.values()) >= 8 else None
    return DocGeometry(body_x0=body_x0, right_x1=float(right_x1), lead=lead,
                       body_size=body_size, page_width=pw, page_height=ph)


def learn_vocabulary(model: PdfModel) -> set[str]:
    """The document's own word list — the discriminator for signals geometry
    can't see (line-break hyphen vs compound hyphen: 'Switzerland' appears
    unbroken somewhere; 'natural-born' appears unbroken WITH its hyphen).
    A token that ENDS in a hyphen is itself a broken word — no evidence."""
    words: set[str] = set()
    for line in model.all_lines():
        for tok in line.plain.split():
            tok = tok.strip("“”\"'’‘()[]{}.,;:!?*†‡§¶").lower()
            if tok.endswith("-"):
                continue
            if tok and all(c.isalpha() or c in "-’'" for c in tok):
                words.add(tok)
    return words


def line_alignment(line: Line, page_width: float,
                   geom: DocGeometry | None,
                   banner_center_min_size: float | None = None) -> str:
    """'C' / 'L' / 'R'. A line that FILLS the measured column is justified
    prose, never centered — a narrow-measure court puts every full line's
    midpoint on the page axis, and reading those as centered turns body lines
    into headings. Centering is judged inside the measured column; only
    genuinely short lines can be centered."""
    x0, x1 = line.x0, line.x1
    width = x1 - x0
    cx = (x0 + x1) / 2
    full_measure = False
    if geom and geom.column > 100:
        full_measure = width >= 0.82 * geom.column
    if (not full_measure and x0 > 100 and abs(cx - page_width / 2) < 25
            and width < page_width * 0.55):
        a = "C"
    elif x0 <= 200:
        a = "L"
    elif x0 > page_width * 0.6:
        a = "R"
    else:
        a = "L"
    # A wide, genuinely midpoint-centered banner at/above the configured size
    # is centered regardless of width (it spans past the width cap that keeps
    # justified body lines left-aligned).
    if a != "C" and banner_center_min_size is not None:
        if line.size >= banner_center_min_size and abs(cx - page_width / 2) < 25:
            a = "C"
    return a
