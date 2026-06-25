"""Arizona Court of Appeals.

Shares the Arizona page mechanics (running-header drop, ¶-marker body grouping,
centered headings, page-aware headmatter) with the Supreme Court via
``ArizonaStyle``. What is specific here:

  * the byline is name-first and letter-spaced: 'M O R S E, Judge:' /
    'J A C O B S, Judge, dissenting:' / 'C A T T A N I, Judge, dissenting in
    part.'. The spaced capitals are collapsed to a surname ('MORSE');
  * the trial-court judge in the caption ('The Honorable ... , Judge') is not
    an author and is excluded;
  * unlike the Supreme Court, the running header stays 'Opinion of the Court'
    even on a separate writing's pages, so opinion boundaries come from these
    body bylines (handled by the shared base's byline scan), not header
    transitions.
"""

from __future__ import annotations

from ._appellate import StateAppellate
from ._arizona import ArizonaStyle
from ._statesupreme import is_caps_name


class ArizonaCourtOfAppeals(ArizonaStyle, StateAppellate):
    court_id = "arizctapp"
    court_label = "Arizona Court of Appeals."

    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        t = text.strip()
        if t.lower().startswith("the honorable"):  # trial-court judge
            return None
        name, sep, after = t.partition(",")
        if not sep:
            return None
        rest = after.strip()
        # Title-led: 'Judge' / 'Presiding Judge' / 'Chief Judge' /
        # 'Vice Chief Judge', optionally followed by a kind ('dissenting').
        title = None
        for cand in ("Vice Chief Judge", "Chief Judge", "Presiding Judge", "Judge"):
            if rest.lower().startswith(cand.lower()):
                title = cand
                rest = rest[len(cand) :]
                break
        if title is None:
            return None
        # Collapse letter-spaced capitals: 'M O R S E' -> 'MORSE'.
        toks = name.split()
        if toks and all(len(tk) == 1 for tk in toks):
            name = "".join(toks)
        else:
            name = name.strip()
        if not is_caps_name(name):
            return None
        kind = rest.strip(" ,.:").strip() or None
        return name, title, kind
