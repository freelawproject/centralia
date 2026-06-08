"""Shared base for state supreme courts whose byline leads with the title and
an all-caps surname, then a verb phrase:

    'JUSTICE BUSBY delivered the opinion of the Court.'        (Texas)
    'CHIEF JUSTICE BLACKLOCK delivered the opinion of the Court.'
    'JUSTICE HUDDLE filed an opinion concurring in part and ...' (concur/dissent)
    'JUSTICE NORIEGA delivered the opinion of the Court.'       (New Jersey)
    'JUSTICE DOUGHERTY DECIDED: MAY 19, 2026'                   (Pennsylvania)
    'JUSTICE JAMES: In this case ...'                           (S. Carolina; colon)
    'JUSTICE NIELSEN, opinion of the Court:'                    (Utah; body byline)
    'JUSTICE PETERSEN, concurring:'                             (Utah; colon kind)

Only a verb-phrase byline counts. A syllabus heading ('JUSTICE NORIEGA, writing
for a unanimous Court.') and a panel roster ('CHIEF JUSTICE RABNER and JUSTICES
PATTERSON, ...') are not opinion starts: the first is rejected because 'writing
for' is not an opinion verb, the second because the text after the surname is
'and justices ...', not a verb phrase. This avoids the duplicate that would
arise from New Jersey's paired syllabus + opinion bylines.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

# Longest title first so 'ASSOCIATE CHIEF JUSTICE'/'CHIEF JUSTICE' win over
# 'JUSTICE'.
_TITLES = (
    "ASSOCIATE CHIEF JUSTICE",
    "VICE CHIEF JUSTICE",
    "CHIEF JUSTICE",
    "PRESIDING JUSTICE",
    "JUSTICE",
)
# Verbs that mark a real opinion byline (not a syllabus/roster line). NB:
# 'authored' is deliberately absent — Utah's title-page summary uses it
# ('JUSTICE NIELSEN authored the opinion of the Court, in which ...'), but its
# opinion body opens with a separate 'JUSTICE NIELSEN, opinion of the Court:'
# byline; treating 'authored' as a verb would double-count the two.
_OPINION_VERBS = ("delivered", "filed", "announced", "decided", "wrote", "issued")
# Endings that close a comma-form kind byline ('JUSTICE X, dissenting.' /
# Utah's colon form 'JUSTICE X, concurring:'); a syllabus sentence
# ('JUSTICE X, dissenting, stresses that ...') has none and is rejected.
_KIND_ENDINGS = (
    "concurring.",
    "dissenting.",
    "concurring",
    "dissenting",
    "part.",
    "part",
    "court.",
    "concurring:",
    "dissenting:",
    "part:",
    "court:",
)


def _allcaps_token(tok: str) -> bool:
    core = tok.rstrip(",.").replace("-", "").replace("'", "").replace(".", "")
    return bool(core) and core.isalpha() and core.isupper()


class ReversedJusticeSupreme(StateSupreme):
    # Titles this court's reversed byline may lead with, longest first. Courts
    # that also seat Judges (e.g. the West Virginia courts) extend this.
    rev_titles = _TITLES

    def _rev_parse(self, text: str):
        """Parse a 'JUSTICE NAME <verb> ...' byline -> (name, title, kind) or
        None."""
        text = text.strip()
        up = text.upper()
        title = next((t for t in self.rev_titles if up.startswith(t + " ")), None)
        if title is None:
            return None
        rest = text[len(title) + 1 :]
        name_toks = []
        sep = None  # what closed the name: ',' or ':' or None (space/verb)
        for tok in rest.split():
            bare = tok.rstrip(",:")
            # 'JUSTICE JAMES: <body>' — a colon right after the surname is a
            # byline (S. Carolina). A colon after an opinion verb ('DECIDED:')
            # is NOT the name — let the verb branch handle it.
            if (
                tok.endswith(":")
                and _allcaps_token(bare)
                and bare.lower() not in _OPINION_VERBS
            ):
                name_toks.append(bare)
                sep = ":"
                break
            if _allcaps_token(tok):
                name_toks.append(tok.rstrip(","))
                if tok.endswith(","):
                    sep = ","
                    break
            else:
                break
        if not name_toks:
            return None
        name = " ".join(name_toks)
        if sep == ":":
            return name, title.title(), None
        after = rest[len(name) :].lstrip(" ,").lower()
        kind = None
        if "concurr" in after and "dissent" in after:
            kind = "concurring in part and dissenting in part"
        elif "concurr" in after:
            kind = "concurring"
        elif "dissent" in after:
            kind = "dissenting"
        first = after.split()[0] if after.split() else ""
        is_verb = first.rstrip(":") in _OPINION_VERBS
        if is_verb:
            return name, title.title(), kind
        # 'JUSTICE NIELSEN, opinion of the Court:' — the majority body byline
        # (Utah); no concur/dissent kind.
        if after.startswith("opinion of the court"):
            return name, title.title(), None
        # A comma-form kind byline ('JUSTICE X, dissenting.' / '..., concurring:')
        # is real only if it ENDS at the kind.
        if kind and text.rstrip().lower().endswith(_KIND_ENDINGS):
            return name, title.title(), kind
        return None

    def _colon_after_name(self, text: str):
        """Index of a colon that directly follows the title+surname
        ('JUSTICE JAMES:' -> the colon), or None. Everything between the title
        and the colon must be all-caps name tokens — so Pennsylvania's
        'JUSTICE DOUGHERTY DECIDED:' (verb before the colon) and Utah's
        'JUSTICE NIELSEN, opinion of the Court:' (prose before it) do NOT
        split here."""
        up = text.upper()
        title = next((t for t in self.rev_titles if up.startswith(t + " ")), None)
        if title is None:
            return None
        ci = text.find(":")
        if ci == -1:
            return None
        toks = text[len(title) + 1 : ci].split()
        if toks and all(
            _allcaps_token(t) and t.rstrip(",").lower() not in _OPINION_VERBS
            for t in toks
        ):
            return ci
        return None

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if not text:
            return None
        up = text.upper()
        if up.startswith("PER CURIAM"):
            # 'PER CURIAM.' or 'PER CURIAM: <body>' — the byline ends at the
            # first '.'/':'.
            ends = [text.find(c) for c in ".:" if text.find(c) != -1]
            i = min(ends) if ends else -1
            return (text, "") if i == -1 else (text[: i + 1], text[i + 1 :].strip())
        if self._rev_parse(text) is None:
            return None
        ci = self._colon_after_name(text)
        if ci is not None:
            return text[: ci + 1], text[ci + 1 :].strip()
        return text, ""

    def parse_author_line(self, text):
        r = self._rev_parse(text)
        if r is not None:
            return r
        return super().parse_author_line(text)
