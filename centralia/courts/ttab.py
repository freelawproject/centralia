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

    def page_lines(self, page):
        if not hasattr(self, "_ttab_dropped"):
            self._ttab_dropped = []
        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        # the mailing masthead: the centered block above the first '_____'
        # caption divider — address/contact furniture
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) < 240 and (
                t.startswith(("P.O. Box", "General Contact", "General Email"))
                or "Mailed:" in t
                or t == "Trademark Trial and Appeal Board"
                or t == "UNITED STATES PATENT AND TRADEMARK OFFICE"
            ):
                self._ttab_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def extract(self, pdf_path: str):
        self._ttab_dropped = []
        self._ttab_author = None
        doc = super().extract(pdf_path)
        if self._ttab_dropped:
            seen, extra = set(), []
            for t in self._ttab_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc
