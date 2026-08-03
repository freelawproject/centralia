"""Supreme Court of the State of Montana.

Reversed prose byline, not bold and not all-caps:
  'Justice Beth Baker delivered the Opinion of the Court.'      (majority)
  'Chief Justice Cory J. Swanson delivered the Opinion of the Court.'
  'Justice Katherine M. Bidegaray, concurring in part and dissenting in part'
A plural 'Justices X and Y join in the ...' line is a joinder, not a new
opinion, and is left as body (it does not start with the singular title).
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

_TITLES = ("Chief Justice", "Justice")
_DELIVERS = "delivered the opinion"


def _is_title_name(name: str) -> bool:
    """Title-case judge name, 1–4 tokens, allowing a middle initial ('M.')."""
    toks = name.split()
    if not (1 <= len(toks) <= 4):
        return False
    for tok in toks:
        core = tok.rstrip(".").replace("'", "").replace("-", "")
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class MontanaSupreme(StateSupreme):
    court_id = "mont"
    court_label = "Supreme Court of the State of Montana."

    def parse_author_line(self, text):
        t = text.strip()
        for title in _TITLES:
            if not t.startswith(title + " "):
                continue
            rest = t[len(title) + 1 :]
            low = rest.lower()
            if _DELIVERS in low and "of the court" in low:
                name = rest[: low.find("delivered")].strip().rstrip(",")
                if _is_title_name(name):
                    return name, title, None
            if "," in rest:
                name, kind = rest.split(",", 1)
                name, kind = name.strip(), kind.strip().rstrip(".")
                if _is_title_name(name) and (
                    "concur" in kind.lower() or "dissent" in kind.lower()
                ):
                    return name, title, kind
            break
        return super().parse_author_line(text)
