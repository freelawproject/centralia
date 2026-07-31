"""United States District Court, Central District of California.

The CACD docket in this reporter is a mix of two very different things, and the
distinction is what a reader most needs:

  * a court RULING — a 'CIVIL MINUTES - GENERAL' minute order (author on the
    'Present: The Honorable NAME, UNITED STATES DISTRICT JUDGE' line, ruling from
    'Proceedings:'), or a memorandum/order the judge signed (a signature block
    ending 'UNITED STATES DISTRICT JUDGE'); and
  * an attorney FILING — a motion, a position paper, or a [PROPOSED] order on
    California pleading paper (numbered lines, an attorney caption block). It
    carries no judicial author; it becomes a ruling only once the judge signs
    it (a signed [PROPOSED] order is then a real order).

The district base always finds *some* author (falling back to the caption's
assigned-judge line), so a bare filing would otherwise read as a judge-authored
opinion. Classify the document by the two ruling signals — a minute-order
header or a judge signature at the foot — and mark everything else FILING,
dropping the fabricated author so it is not presented as the court's opinion.

PARAGRAPH FORMAT — THE LEADING IS PER DOCUMENT, NOT PER COURT
-------------------------------------------------------------
No other court in the corpus is this typographically heterogeneous: the review
notes count 30 distinct styles across 40 documents, with body leading ranging
from 12pt to 25.5pt and body faces from Courier to Garamond. The shared
paragraph grammar reads spacing against FIXED bands (tight < 16 < single < 22 <
double < 40), which only works when a court's body leading is stable. Here it
is not, so a chambers that sets its orders SINGLE-SPACED at 16.1pt landed every
one of its paragraphs in the 'single' band — and the whole ruling came back
rendered as block quotes instead of prose. That is the 'return things in
paragraph format' complaint.

The fix is to measure the document's OWN body leading (``_measure_body_lead``)
and scale the three bands to it, so 'tight', 'single' and 'double' mean tighter
than / equal to / looser than THIS document's body — whatever that is. Real
block quotes then come from where they always should: both-margins indentation
(``DistrictBase.blockquote_by_indent``), not from an absolute point size.
"""

from __future__ import annotations

from collections import Counter

import pdfplumber

from ..models import DocType
from ._district import DistrictBase


def _squeeze(text: str) -> str:
    """Letters only, lowercased, with runs of a repeated letter collapsed to one
    — so a font that renders each glyph several times ('UUnniitttteeeedd
    SSttaatteess DDiissttrriicctt JJuuddggee') and the interleaved line numbers
    both normalize to plain 'unitedstatesdistrictjudge'. The target titles have
    no doubled letters, so collapsing is lossless for the match."""
    letters = [c.lower() for c in text if c.isalpha()]
    out = []
    for c in letters:
        if not out or out[-1] != c:
            out.append(c)
    return "".join(out)


# A judge's conformed-signature title line at the foot of a signed ruling —
# with the common 'District Court Judge' variant alongside the plain forms.
_JUDGE_TITLES_SQ = tuple(
    _squeeze(t)
    for t in (
        "United States District Judge",
        "United States District Court Judge",
        "United States Magistrate Judge",
        "United States Circuit Judge",
        "United States Bankruptcy Judge",
    )
)


class CentralDistrictOfCalifornia(DistrictBase):
    court_id = "cacd"
    court_label = "United States District Court, Central District of California."
    # CACD pleading-paper footnotes can sit below the usual district footer
    # cutoff (including a one-line note at y≈740). Keep the note text while
    # still excluding the centered page folio at y≈753.
    margin_bottom = 748.0

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # Some CACD orders have no drawn rule before a bottom footnote. The
        # first line instead starts with a raised label followed by normal-size
        # note text; use that typography and its lower-page position as the
        # separator.
        candidates = []
        for line in page.extract_text_lines():
            chars = line.get("chars") or []
            if len(chars) < 2 or line.get("top", 0) < page.height * 0.72:
                continue
            first = chars[0]
            if first.get("text") not in self.FOOTNOTE_LABEL_CHARS:
                continue
            rest = [c.get("size", 0) for c in chars[1:] if c.get("size")]
            if not rest or first.get("size", 0) > max(rest) - 1.5:
                continue
            candidates.append(line["top"])
        return min(candidates) if candidates else None

    def find_authors(self, all_segments) -> list:
        self._district_author = (
            self._present_author(all_segments)
            or self._signature_author(all_segments)
            or self._byline_author(all_segments)
            or self._caption_judge(all_segments)
        )
        # Minute order: the ruling proper starts at the 'Proceedings:' line.
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self.line_plain_text(seg[0]).strip().lower().startswith(
                "proceedings:"
            ):
                return [i]
        return super().find_authors(all_segments)

    def _is_ruling(self, pdf_path) -> bool:
        """True when the document is a court ruling, not an attorney filing: a
        'CIVIL MINUTES' minute order, or a judge's conformed-signature title line
        ('... UNITED STATES DISTRICT/MAGISTRATE JUDGE') anywhere in the document.
        The signature can sit mid-page (ahead of a footnote), a page or two
        before a trailing service exhibit, and can be glyph-duplicated by a bad
        font — so the whole text is matched, squeezed. A pleading-paper filing's
        caption never carries the full title, and an unsigned proposed order
        carries only a blank signature line, so neither trips the match."""
        with pdfplumber.open(pdf_path) as pdf:
            pages = pdf.pages
            if not pages:
                return False
            full = "\n".join((p.extract_text() or "") for p in pages)
        if "CIVIL MINUTES" in full:
            return True
        squeezed = _squeeze(full)
        return any(t in squeezed for t in _JUDGE_TITLES_SQ)

    def extract(self, pdf_path):
        doc = super().extract(pdf_path)
        if doc.non_digital:
            return doc
        if not self._is_ruling(pdf_path):
            doc.doc_type = DocType.FILING
            # No judicial author on an attorney filing — the base fell back to
            # the caption's assigned judge, which is not the document's author.
            for op in doc.opinions:
                op.author = ""
        return doc
