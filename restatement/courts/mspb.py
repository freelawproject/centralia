"""Merit Systems Protection Board.

Whitespace two-column caption (appellant left, 'DOCKET NUMBER' / 'DATE:'
right), a 'THIS ORDER IS NONPRECEDENTIAL' small-print notice, counsel
lines, then a centered 'REMAND ORDER' / 'FINAL ORDER' / 'OPINION AND
ORDER' heading opening the Board's single decision. Ends 'FOR THE BOARD:'
over the Clerk's signature — the signature block, not an author byline
(the Board itself decides; the author stays 'THE BOARD').
"""

from __future__ import annotations

from ._district import DistrictBase

_MSPB_HEADINGS = (
    "REMAND ORDER",
    "FINAL ORDER",
    "ORDER",
    "OPINION AND ORDER",
    "NONPRECEDENTIAL ORDER",
)


class MeritSystemsProtectionBoard(DistrictBase):
    court_id = "mspb"
    court_label = "Merit Systems Protection Board."

    def find_authors(self, all_segments) -> list:
        self._district_author = "THE BOARD"
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip().rstrip(".").upper()
            if t in _MSPB_HEADINGS:
                return [i]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        if getattr(self, "_district_author", None):
            return self._district_author, [line]
        return super().split_author_line(line)

    def _harvest_signature(self, doc):
        """'FOR THE BOARD:' + rule + 'Gina K. Grippando / Clerk of the
        Board / Washington, D.C.' — lift into the Signature section."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        idx = None
        for k in range(len(blocks) - 1, max(-1, len(blocks) - 7), -1):
            if self._untag(blocks[k].text).strip().upper().startswith(
                "FOR THE BOARD"
            ):
                idx = k
                break
        if idx is None:
            return super()._harvest_signature(doc)
        doc.signature = [str(b.text) for b in blocks[idx:]]
        op.blocks = blocks[:idx]
