"""Supreme Court of Illinois.

The lead author is declared in prose: 'JUSTICE ROCHFORD delivered the judgment
of the court, with opinion.'; separate opinions open 'JUSTICE X, specially
concurring' / 'JUSTICE X, dissenting'. The body itself is paragraph-numbered
('¶ 1 ...') after an 'OPINION' heading. Treating the prose line as the opinion
start lets the core pipeline split opinions; the authorship lines remain in the
body (nothing dropped).
"""

from __future__ import annotations

from ._illinois import IllinoisStyle
from ._statesupreme import StateSupreme, is_caps_name


class IllinoisSupreme(IllinoisStyle, StateSupreme):
    court_id = "ill"
    court_label = "Supreme Court of Illinois."
    il_body_baseline = 108.0  # '¶' marker hangs at 62.6; wrapped text at 108

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        t = text.strip()
        up = t.upper()
        if up.startswith("CHIEF JUSTICE "):
            title, rest = "Chief Justice", t[len("Chief Justice ") :]
        elif up.startswith("JUSTICE "):
            title, rest = "Justice", t[len("Justice ") :]
        else:
            return None
        low = rest.lower()
        if " delivered " in low:
            name, kind = rest[: low.index(" delivered")].strip(), None
        elif "," in rest:
            name, kind = rest.split(",", 1)
            name, kind = name.strip(), kind.strip()
        else:
            return None
        if not is_caps_name(name):
            return None
        return name, title, kind
