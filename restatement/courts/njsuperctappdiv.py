"""New Jersey Superior Court, Appellate Division.

The opinion is introduced by 'The opinion of the court was delivered by' and the
author follows as 'FIRKO, J.A.D.' / 'SUMNERS, JR., C.J.A.D.' — a surname (with
an optional 'JR.') and an Appellate-Division title. A 'PER CURIAM' opinion is
handled by the base.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# Longest first so 'C.J.A.D.'/'P.J.A.D.' win over the bare 'J.A.D.'.
_TITLES = (", C.J.A.D.", ", P.J.A.D.", ", J.A.D.")


class NewJerseySuperiorCourtAppellateDivision(StateSupreme):
    court_id = "njsuperctappdiv"
    court_label = "New Jersey Superior Court, Appellate Division."

    def parse_author_line(self, text):
        t = text.strip()
        for ti in _TITLES:
            idx = t.find(ti)
            if idx != -1 and idx > 0:
                name = t[:idx].strip()
                if (
                    name
                    and name.replace(",", "")
                    .replace(".", "")
                    .replace(" ", "")
                    .isalpha()
                ):
                    return name, "Judge", None
        return super().parse_author_line(text)
