"""Michigan Court of Appeals.

Intermediate appellate court. Each opinion opens with a panel roster
('Before: GADOLA, C.J., and MURRAY and M. J. KELLY, JJ.') followed by the author
byline — 'NAME, J.' / 'NAME, P.J.' / 'PER CURIAM.' — then the body. A publication
notice sits at the very top of page 1.

Two court-specific fixes over the shared appellate base:

  * A half-width rule divides the caption from the panel/opinion. It sits in the
    bottom half of the page and is left-aligned, so the default footnote-separator
    finder mistakes it for a footnote rule and drops the byline + body beneath it
    (worst on a long multi-party caption that pushes the divider low). It is
    instead found by footnote-sized text directly under the rule — a real
    footnote sits in smaller type flush below, a caption divider has body-size
    text below — so the divider no longer chops the opinion.

  * The author must be a member of the 'Before:' panel. A parenthetical citation
    to another court's opinion ('... (ALITO, J., concurring), quoting ...') can
    wrap so a byline-shaped clause starts a line; restricting authors to the
    panel (or PER CURIAM) rejects those non-panel names.
"""

from __future__ import annotations

from typing import Optional

from ._appellate import StateAppellate

# Panel-roster title abbreviations, never a surname.
_TITLE_ABBR = {"JJ", "CJ", "PJ", "J", "P"}


class MichiganCourtOfAppeals(StateAppellate):
    court_id = "michctapp"
    court_label = "Michigan Court of Appeals."

    def find_footnote_separator(self, page) -> Optional[float]:
        return self._footnote_sep_small_text_below(page)

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        panel = self._panel_surnames(all_segments)
        if not panel:
            return starts
        return [
            i
            for i in starts
            if self._byline_surname(self.line_plain_text(all_segments[i][1][0]))
            in (None, *panel)
        ]

    @staticmethod
    def _norm(tok: str) -> str:
        return tok.replace(".", "").replace("'", "").replace("’", "").upper()

    def _panel_surnames(self, all_segments) -> set:
        """Surnames from the 'Before: ...' panel roster (the only judges who can
        author here). Title abbreviations (C.J./JJ.) and bare initials (M. J.)
        are excluded; apostrophes/periods are normalized so 'O'BRIEN' matches."""
        for _p, seg, _k in all_segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                if not t.lower().startswith("before"):
                    continue
                rest = t.split(":", 1)[1] if ":" in t else t[len("before"):]
                names = set()
                for tok in rest.replace(",", " ").split():
                    if not tok.strip(".").isupper():
                        continue
                    n = self._norm(tok)
                    if len(n) >= 2 and n.isalpha() and n not in _TITLE_ABBR:
                        names.add(n)
                return names
        return set()

    def _byline_surname(self, text: str):
        """Normalized surname of a byline ('M. J. KELLY, J.' -> 'KELLY'), or None
        for PER CURIAM (which any panel writes)."""
        t = (text or "").strip()
        if "per curiam" in t.lower():
            return None
        toks = t.split(",")[0].split()
        return self._norm(toks[-1]) if toks else None
