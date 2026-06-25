"""Shared byline for the Mississippi appellate courts (miss / missctapp).

Both courts use the same name-first, all-caps, role-closing-with-a-colon byline;
only the title differs (the Supreme Court seats Justices, the Court of Appeals
seats Judges):

    'SULLIVAN, JUSTICE, FOR THE COURT:'                  (miss, majority)
    'COLEMAN, PRESIDING JUSTICE, FOR THE COURT:'
    'KING, JUSTICE, CONCURRING:' / '..., DISSENTING:'    (separate writings)
    'EMFINGER, J., FOR THE COURT:'                       (missctapp)
    'CARLTON, P.J., FOR THE COURT:'
    'LASSITTER, ST. PÉ, J., FOR THE COURT:'              (compound surname)

The byline is parsed field-by-field (comma-delimited): the field that exactly
matches a court title is the title; everything before it is the name (so a
compound surname carrying its own comma, 'LASSITTER, ST. PÉ', is rejoined); the
role after it gives the kind. The closing colon is the role's terminator — a
'BEFORE RANDOLPH, C.J., ...' panel roster and a vote line ('... JJ., CONCUR.
...', no closing colon) are not opinion starts. The opinion text (paragraph-
numbered '¶1. ...') follows on the next line.
"""

from __future__ import annotations

from ._statesupreme import _is_byline_name


class MississippiStyle:
    # {UPPER title field: Full title}. Subclasses set their court's titles.
    _MS_TITLE_MAP: dict = {}

    def _ms_parse(self, text: str):
        """Return (name, title, kind) or None."""
        text = text.strip()
        if not text.endswith(":") or "," not in text:
            return None
        fields = [f.strip() for f in text[:-1].split(",")]
        ti = next(
            (i for i, f in enumerate(fields) if f.upper() in self._MS_TITLE_MAP), None
        )
        if not ti:  # None, or 0 (a name must precede the title)
            return None
        name = " ".join(fields[:ti]).strip()
        if not _is_byline_name(name):
            return None
        full = self._MS_TITLE_MAP[fields[ti].upper()]
        role = " ".join(fields[ti + 1 :]).upper().strip()
        if role.startswith("FOR THE COURT"):
            kind = None
        elif "CONCUR" in role and "DISSENT" in role:
            kind = "concurring in part and dissenting in part"
        elif "CONCUR" in role:
            kind = "concurring"
        elif "DISSENT" in role:
            kind = "dissenting"
        else:
            return None
        return name, full, kind

    def parse_author_line(self, text):
        r = self._ms_parse(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._ms_parse(text) is None:
            return super()._byline_split(line)
        return text, ""
