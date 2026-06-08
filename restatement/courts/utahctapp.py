"""Utah Court of Appeals.

Same two-part front matter as the Utah Supreme Court: a title-page authorship
summary ('JUDGE RYAN D. TENNEY authored this Opinion, in which JUDGES ORME and
HARRIS concurred except as to Part I(C) ...') that is left as headmatter, and
the actual opinion byline below it — a name-first colon line, 'TENNEY, Judge:'
(majority) or 'NAME, Judge, concurring:' / '..., dissenting:' (separate
writings). Only the colon byline starts the opinion, so the authorship summary
and its joinder roster don't leak into the body. The surname may be compound
('CHRISTIANSEN FORSTER').
"""

from __future__ import annotations

from ._appellate import StateAppellate


class UtahCourtOfAppeals(StateAppellate):
    court_id = "utahctapp"
    court_label = "Utah Court of Appeals."

    def _uca_byline(self, text: str):
        """Parse the colon body byline 'NAME, Judge[, kind]:' -> (name, title,
        kind), else None. The 'JUDGE X authored ... in which ...' authorship
        summary has no such form, so it stays headmatter."""
        t = text.strip()
        if not t.endswith(":") or "," not in t:
            return None
        name, rest = (s.strip() for s in t[:-1].split(",", 1))
        toks = name.split()
        if not toks or len(toks) > 3:
            return None
        if not all(
            k.replace("'", "").replace("-", "").isalpha() and k.isupper() for k in toks
        ):
            return None
        role = rest.lower()
        if not role.startswith("judge"):
            return None
        role = role[len("judge") :].lstrip(", ")
        if "concur" in role and "dissent" in role:
            kind = "concurring in part and dissenting in part"
        elif "concur" in role:
            kind = "concurring"
        elif "dissent" in role:
            kind = "dissenting"
        else:
            kind = None
        return name, "Judge", kind

    def parse_author_line(self, text):
        r = self._uca_byline(text)
        if r is not None:
            return r
        return super().parse_author_line(text)
