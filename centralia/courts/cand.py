"""United States District Court, Northern District of California.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

The court's own letterhead is printed SIDEWAYS up the left pleading margin
('United States District Court' / 'Northern District of California'), one
rotated glyph per row. pdfplumber reports those glyphs as ``upright`` (their
text matrix is rotated, not their glyph box), so nothing upstream can filter
them: they are interleaved into the body rows a glyph at a time ('u o r o 13
After more than six years …'). They are removed by their ROTATED TEXT MATRIX in
``correct_page_geometry`` — the one hook the coverage sweep reads the page
through as well — and recorded in the Removed box.
"""

from __future__ import annotations

import html
import re

from ..models import DocType
from ._district import DistrictBase

_TAG = re.compile(r"<[^>]+>")


class NorthernDistrictOfCalifornia(DistrictBase):
    # 28-line pleading paper runs the last numbered line to top≈730-739, past
    # the 725 default — so the final line of EVERY page was being discarded as
    # footer, mid-sentence ('...its membership database does not have entry').
    # The page number sits at 750+ with an empty band between, so 745 keeps the
    # body whole and still drops the folio.
    margin_bottom = 745

    @staticmethod
    def _is_rotated(char) -> bool:
        """True when the glyph is drawn on a rotated baseline.

        An upright glyph's text matrix is (size, 0, 0, size, x, y); the
        sideways letterhead's is (0, 1, -1, 0, x, y). ``upright`` cannot be
        used — pdfplumber reports these glyphs as upright.
        """
        if char.get("upright", True) is False:
            return True
        matrix = char.get("matrix")
        if not matrix or len(matrix) < 4:
            return False
        return abs(matrix[1]) > 0.01 or abs(matrix[2]) > 0.01

    def correct_page_geometry(self, page) -> None:
        """Remove the sideways pleading-margin letterhead, then apply the base
        overstrike fix.

        The removal has to happen HERE: this is the hook the completeness
        sweep and the audit read the page through, so a glyph merely skipped
        during line building would still count as lost text.
        """
        chars = page.chars
        rotated = [i for i, char in enumerate(chars) if self._is_rotated(char)]
        if rotated:
            if getattr(self, "_cand_dropped", None) is None:
                self._cand_dropped = []
            # Group the glyph columns by x, each read bottom-to-top (the
            # baseline runs up the page), so the letterhead is recorded in
            # reading order rather than reversed.
            columns: dict = {}
            for i in rotated:
                char = chars[i]
                columns.setdefault(round(char["x0"] / 8), []).append(char)
            for _key, column in sorted(columns.items()):
                text = "".join(
                    (char.get("text") or "")
                    for char in sorted(column, key=lambda c: -c["top"])
                ).strip()
                if text:
                    self._cand_dropped.append(
                        "[sideways margin letterhead removed: " + text + "]"
                    )
            for i in reversed(rotated):
                del chars[i]
        super().correct_page_geometry(page)

    def page_lines(self, page):
        # The shared district base swaps in a FILTERED page to cut the
        # pleading-paper line-number gutter, and a filtered page's char list is
        # a COPY — geometry corrected on it never reaches the real page the
        # coverage sweep reads. So correct the real page first.
        self.correct_page_geometry(page)
        return super().page_lines(page)

    def extract(self, pdf_path: str):
        self._cand_dropped = []
        doc = super().extract(pdf_path)
        self._clean_accepted_proposed_order(doc)
        if doc.doc_type == DocType.ORDER:
            for opinion in doc.opinions:
                opinion.type = "order"
        return doc

    def find_footnote_separator(self, page):
        """Reject the pleading form's footer rule as a footnote separator.

        The footer is a horizontal rule followed only by line 28's folio/case
        number and the running filing title.  Its leading ``28`` otherwise
        looks exactly like a footnote label and turns every page footer into
        one synthetic footnote.
        """
        sep = super().find_footnote_separator(page)
        if sep is None:
            return None
        below = [
            self.line_plain_text(line).strip()
            for line in page.extract_text_lines()
            # The folio/case-number row sits immediately ABOVE the rule and
            # the running title immediately below it.
            if line.get("top", 0) >= sep - 20
            and self.line_plain_text(line).strip()
        ]
        joined = " ".join(below).upper()
        has_case_folio = "CASE NO." in joined or "CASE NUMBER" in joined
        has_running_title = "STIPULATION" in joined and "ORDER" in joined
        if has_case_folio and has_running_title:
            return None
        return sep

    def classify_document_type(self, all_segments, author_indices, n_pages):
        # A signed ruling whose caption title starts "ORDER ..." is an order,
        # not a generic authored opinion.  The judicial signature remains the
        # dispositive distinction from an unsigned proposed order or party
        # filing.
        has_judicial_signature = self._signature_author(all_segments) is not None
        if has_judicial_signature:
            for _page, segment, _kind in all_segments[:20]:
                for line in segment:
                    text = self.line_plain_text(line).strip().upper()
                    if text.startswith("ORDER ") or text == "ORDER":
                        return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    @staticmethod
    def _caption_plain(block) -> str:
        rows = []
        for side in ("left", "right"):
            for row in block.get(side, []):
                value = row.get("h", "") if isinstance(row, dict) else row
                text = html.unescape(_TAG.sub("", str(value))).strip()
                if text:
                    rows.append(text)
        return "\n".join(rows)

    def _clean_accepted_proposed_order(self, doc) -> None:
        """Clean filing-template matter around a judge-adopted proposal.

        An accepted proposed order remains an order, but the submitting
        lawyers' two-column address roster is not judicial headmatter.  Move
        that roster to Removed so it stays visible and auditable.  Also keep
        the pleading footer out of the judicial signature and normalize the
        honorific that the signature parser included in the author name.
        """
        kept = []
        for item in doc.summary:
            if isinstance(item, dict) and item.get("__caption__"):
                plain = self._caption_plain(item)
                low = plain.lower()
                is_attorney_roster = (
                    "attorneys for" in low
                    and ("telephone:" in low or "facsimile:" in low)
                )
                if is_attorney_roster:
                    doc.dropped.append(
                        "[submitting attorney headmatter removed]\n" + plain
                    )
                    continue
            kept.append(item)
        doc.summary = kept

        for opinion in doc.opinions:
            author = opinion.author or ""
            for prefix in ("The Honorable ", "Honorable "):
                if author.startswith(prefix):
                    opinion.author = author[len(prefix) :].strip()
                    break

        signature = []
        for item in doc.signature:
            if isinstance(item, str):
                plain = html.unescape(_TAG.sub("", item)).strip()
                if re.search(r"-\s*\d+\s*-\s*Case No\.", plain, re.I):
                    doc.dropped.append(plain)
                    continue
            signature.append(item)
        doc.signature = signature

    def _sweep_residual(self, doc, source_pages):
        """Record the removed letterhead BEFORE the completeness sweep runs —
        the sweep happens inside ``super().extract()``, so a later append to
        ``doc.dropped`` would leave the rows reading as unplaced content."""
        seen, extra = set(), []
        for text in getattr(self, "_cand_dropped", []) or []:
            if text not in seen:
                seen.add(text)
                extra.append(text)
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    court_id = "cand"
    court_label = "United States District Court, Northern District of California."
