"""Supreme Court of New Hampshire.

Standalone abbreviated-title byline, not bold: 'MACDONALD, C.J.' /
'COUNTWAY, J.' / 'DONOVAN, J.', with the opinion body following. A
'DONOVAN, COUNTWAY, and GOULD, JJ., concurred.' line is a signature roster
(its continuation after the surname is another name, not a title), not a new
opinion. The shared abbreviated-title base handles all of this.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class NewHampshireSupreme(AbbrevTitleSupreme):
    court_id = "nh"
    court_label = "Supreme Court of New Hampshire."
    # Block quotes are indented on both margins and single-spaced (~14pt) —
    # below gap_tight_max, so the gap bands read them as 'notice'. Re-tag them
    # by their both-margins indent (the body is double-spaced).
    blockquote_by_indent = True
    # Underline rules sit a hair ABOVE the glyph bounding-box bottom (offset
    # ~-1.2pt), so the default floor of 0.0 rejects them and underlined
    # citations ('see Sup. Ct. R.') lose their <u>. Lower the floor.
    underline_offset_min = -2.0

    _BANNER = "THE SUPREME COURT OF NEW HAMPSHIRE"

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Page 1 opens with a publication advisory ('NOTICE: This opinion is
        subject to motions for rehearing … before publication in the New
        Hampshire Reports …') above the court banner. It is set at body size, so
        the small-print notice routing misses it. Everything before the
        'THE SUPREME COURT OF NEW HAMPSHIRE' banner is this front-matter notice —
        route it to ``dropped`` and build the headmatter from the banner down."""
        banner_idx = None
        for i, seg in enumerate(headmatter_segs):
            t = " ".join((l.get("text") or "").strip() for l in seg).strip()
            if t.upper().startswith(self._BANNER):
                banner_idx = i
                break
        if not banner_idx:  # banner absent or already first — nothing to peel
            return super().extract_headmatter(headmatter_segs, page1_rules)
        notice = [
            " ".join((l.get("text") or "").strip() for l in seg).strip()
            for seg in headmatter_segs[:banner_idx]
        ]
        notice = [n for n in notice if n]
        d = super().extract_headmatter(headmatter_segs[banner_idx:], page1_rules)
        d["dropped"] = list(d.get("dropped") or []) + notice
        return d
