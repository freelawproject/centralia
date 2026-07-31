"""Missouri Court of Appeals.

The author is signed at the end as 'NAME, Judge' / 'NAME, Chief Judge', in
Title-Case or ALL-CAPS ('EDWARD R. ARDINI, JR., JUDGE', 'JAMES M. DOWD, JUDGE').
The shared MissouriStyle matches the title case-insensitively; the appellate base
drops the trial-judge / panel-roster lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._missouri import MissouriStyle


# En/em dash setting off the Southern District's signature ROLE annotation.
# A plain hyphen is excluded so a hyphenated surname is never split.
_ROLE_DASHES = ("–", "—")


class MissouriCourtOfAppeals(MissouriStyle, StateAppellate):
    court_id = "moctapp"
    court_label = "Missouri Court of Appeals."

    def parse_author_line(self, text):
        """Read a signature that carries the Southern District's ROLE
        annotation: 'GARY W. LYNCH, Senior Judge. – OPINION AUTHOR' /
        'DON E. BURRELL, Judge – CONCURS'.

        The annotation belongs to the panel roster, not to the title, and it
        defeats both parsers — the shared Missouri matcher reads the title as
        'senior judge. – opinion author', and the base byline grammar only
        tolerates the tail after an ABBREVIATED title ('WEST, J. – CONCURS'
        parses, 'LYNCH, Senior Judge. – OPINION AUTHOR' does not). Strip the
        annotation and parse the signature itself; ``_mo_sig_role`` still reads
        the role off the full line, so 'OPINION AUTHOR' vs 'CONCURS' keeps
        telling the author apart from a concurring panel member."""
        t = text.strip()
        for dash in _ROLE_DASHES:
            i = t.rfind(dash)
            if i <= 0:
                continue
            tail = t[i + 1 :].strip()
            if (
                tail
                and tail == tail.upper()
                and all(c.isalpha() or c.isspace() for c in tail)
            ):
                r = super().parse_author_line(t[:i].strip())
                if r:
                    return r
        return super().parse_author_line(text)
