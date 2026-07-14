"""North Carolina Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class NorthCarolinaCourtOfAppeals(StateAppellate):
    court_id = "ncctapp"
    court_label = "North Carolina Court of Appeals."

    def extract(self, pdf_path):
        self._ncc_dropped = []
        doc = super().extract(pdf_path)
        if self._ncc_dropped:
            seen = set()
            uniq = [
                t for t in self._ncc_dropped if not (t in seen or seen.add(t))
            ]
            doc.dropped = list(doc.dropped) + uniq
        return doc

    def _maybe_drop_running_header(self, page, lines):
        """Continuation pages carry a small-type centered running head
        ('AHDI V. AHDI' / 'Opinion of the Court', 9.5–10pt vs the 12pt body)
        and a centered '- N -' page number at the foot — margin furniture,
        dropped and surfaced."""
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number <= 1:
            return lines
        kept = []
        for ln in lines:
            size, _font, _bold = self.line_meta(ln)
            t = self.line_plain_text(ln).strip()
            top = ln.get("top", 0)
            if top < 80 and size <= 10.5 and ln.get("x0", 0) > 150:
                if t:
                    getattr(self, "_ncc_dropped", []).append(t)
                continue
            if top > 700 and self._is_page_number_text(t):
                if t:
                    getattr(self, "_ncc_dropped", []).append(t)
                continue
            kept.append(ln)
        return kept
