"""Kentucky Court of Appeals.

After the 'OPINION' header and the 'BEFORE: <panel>, JUDGES.' roster, the author
signs inline with an ALL-CAPS surname, the title, and a colon: 'MCNEILL, JUDGE:
This case arises ...'. Separate writings carry the kind in the same form
('NAME, JUDGE, CONCURRING:' / 'NAME, JUDGE, DISSENTING:'). The ALL-CAPS surname
distinguishes the byline from the 'BEFORE:' panel line and the trial-court
history; bold centered section labels ('STANDARD OF REVIEW', 'ANALYSIS') are
headings in the body.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._statesupreme import is_caps_name

_KY_JUDGE_TITLES = {"judge", "chief judge", "j", "cj", "pj"}


class KentuckyCourtOfAppeals(StateAppellate):
    court_id = "kyctapp"
    court_label = "Kentucky Court of Appeals."

    def _kyctapp_byline(self, text: str):
        """Parse 'NAME, JUDGE[, KIND]:' -> (name, title, kind), or None."""
        t = (text or "").strip()
        if t.upper().startswith("PER CURIAM"):
            return "PER CURIAM", "per curiam", None
        ci = t.find(":")
        if ci == -1:
            return None
        parts = [p.strip() for p in t[:ci].split(",")]
        if len(parts) < 2 or not is_caps_name(parts[0]):
            return None
        if parts[1].lower().replace(".", "") not in _KY_JUDGE_TITLES:
            return None
        kt = " ".join(parts[2:]).upper()
        has_c, has_d = "CONCUR" in kt, "DISSENT" in kt
        kind = (
            "concurring in part and dissenting in part"
            if has_c and has_d
            else "dissenting"
            if has_d
            else "concurring"
            if has_c
            else None
        )
        return parts[0], parts[1].title(), kind

    def parse_author_line(self, text):
        r = self._kyctapp_byline(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._kyctapp_byline(text) is not None:
            ci = text.find(":")
            return text[: ci + 1], text[ci + 1 :].strip()
        return super()._byline_split(line)
