"""Trademark Trial and Appeal Board.

A centered USPTO mailing-address masthead tops page 1 (P.O. Box, contact
number/email, mailing dates) — administrative furniture, dropped and
surfaced. The caption is centered between '_____' dividers; a 'Before
Lykos, English and Cohen, Administrative Trademark Judges.' panel roster
precedes the byline 'Opinion by Cohen, Administrative Trademark Judge:' —
the single opinion follows ('Decision: The opposition is dismissed.').
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class TrademarkBoard(StateSupreme):
    court_id = "ttab"
    court_label = "Trademark Trial and Appeal Board."

    def parse_author_line(self, text):
        """'Opinion by Cohen, Administrative Trademark Judge:' — md-style
        prefix byline with a colon; 'By the Board:' for institutional
        rulings. Parseable here so the base splits segments at the byline
        even when it runs mid-segment."""
        t = text.strip()
        if t.startswith("Opinion by ") and t.rstrip().endswith(":"):
            rest = t[len("Opinion by ") :].rstrip(": ").strip()
            name = rest.split(",")[0].strip()
            title = (
                rest.split(",", 1)[1].strip()
                if "," in rest
                else "Administrative Trademark Judge"
            )
            return name, title, None
        if t.rstrip(": ").lower() == "by the board":
            return "By the Board", "Board", None
        # An interlocutory order is signed by a Board attorney rather than a
        # judge ('Michael Webster, Managing Interlocutory Attorney'), with no
        # 'Opinion by' prefix. Without it the writing had no byline at all and
        # the fallback opened the body at the caption, emptying the headmatter.
        # The plural roster ('Before English, Cohen, and Casagrande,
        # Administrative Trademark Judges.') keeps its plural title and so is
        # never matched here.
        head, sep, tail = t.rpartition(",")
        if sep and head.strip():
            office = tail.strip().rstrip(":.").strip()
            if office in self.SIGNER_TITLES:
                return head.strip(), office, None
        return None

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self.parse_author_line(text) is not None:
            return text, ""
        return super()._byline_split(line)

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        if out:
            return out
        # an unsigned interlocutory order: no byline anywhere — the order
        # body starts at the first body-kind segment after the caption
        for i, (_p, _seg, kind) in enumerate(all_segments):
            if kind == "body":
                return [i]
        return []

    def split_author_line(self, line):
        text = self.line_plain_text(line).strip()
        if self.parse_author_line(text) is None:
            return "", [line]  # body-fallback start: no author to claim
        return super().split_author_line(line)

    # The caption opens with the agency banner, set ROMAN and CENTERED. The
    # letterhead masthead prints the identical words BOLD in the right-hand
    # address column, so face + centering — not the text — separates them.
    CAPTION_BANNER = "UNITED STATES PATENT AND TRADEMARK OFFICE"
    # Order-style decisions carry no banner; their caption opens at the
    # proceeding number.
    CAPTION_NUMBER_STARTS = (
        "Opposition No.",
        "Cancellation No.",
        "Serial No.",
        "Reexamination No.",
        "Expungement No.",
        "Concurrent Use No.",
    )

    def _masthead_bottom(self, lines) -> float | None:
        """y where the caption begins on page 1 — everything above it is the
        USPTO letterhead masthead (agency address block, contact number and
        email, the precedential-status stamp, and the mailing/hearing date).

        Anchored on the caption's own first row so the masthead band cannot
        swallow caption content. The previous text-keyed drop list ate the
        caption's banner and its 'Trademark Trial and Appeal Board' row, and
        it could not see the stamp at all on the two order-style decisions,
        where pdfplumber merges the left-hand stamp column into the address
        column ('PRECEDENT OF THE P.O. Box 1451')."""
        for l in sorted(lines, key=lambda l: l.get("top", 0)):
            t = " ".join(self.line_plain_text(l).split())
            if t.upper() == self.CAPTION_BANNER and not self.line_meta(l)[2]:
                return l["top"]
            if t.startswith(self.CAPTION_NUMBER_STARTS):
                return l["top"]
        return None

    def page_lines(self, page):
        if not hasattr(self, "_ttab_dropped"):
            self._ttab_dropped = []
        lines = super().page_lines(page)
        if page.page_number != getattr(self, "_caption_pno", 1):
            return lines
        bottom = self._masthead_bottom(lines)
        if bottom is None:
            return lines
        kept = []
        for l in lines:
            if l.get("top", 0) < bottom - 1:
                t = self.line_plain_text(l).strip()
                if t:
                    self._ttab_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def _sweep_residual(self, doc, source_pages) -> None:
        """Register the masthead in ``dropped`` BEFORE the completeness sweep
        runs — otherwise furniture filtered out in ``page_lines`` has no home
        yet and the sweep reports it as unplaced content."""
        seen, extra = set(), []
        for t in getattr(self, "_ttab_dropped", []):
            if t and t not in seen:
                seen.add(t)
                extra.append(t)
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    def extract(self, pdf_path: str):
        self._ttab_dropped = []
        self._ttab_author = None
        return super().extract(pdf_path)
