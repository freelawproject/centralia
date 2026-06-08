"""Shared byline parsing for the Missouri courts (Supreme + Court of Appeals).

The author is signed at the end of the opinion, centered, as 'NAME, Judge' — and
the surname casing varies: Title-Case in some ('Ginger K. Gooch, Judge', 'Zel M.
Fischer, Judge') and ALL-CAPS in others ('KELLY C. BRONIEC, JUDGE', 'EDWARD R.
ARDINI, JR., JUDGE'). The title can be 'Judge' / 'Chief Judge' / 'Presiding
Judge' / 'C.J.' / 'P.J.', also in either case. Match it case-insensitively so an
ALL-CAPS signature is recognized; the 'The Honorable ..., Judge' trial-judge line
and the 'Division Two: ...' panel line are still excluded (the first by the
shared non-author prefixes, the second because the name half holds a colon)."""

from __future__ import annotations

_MO_TITLES = {
    "judge",
    "chief judge",
    "presiding judge",
    "senior judge",
    "special judge",
    "chief justice",
    "justice",
    "cj",
    "pj",
    "j",
}


def _mo_name_ok(name: str) -> bool:
    name = name.strip()
    if not name or ":" in name:
        return False
    toks = name.replace(",", " ").split()
    if not (1 <= len(toks) <= 5):
        return False
    for tok in toks:
        core = tok.rstrip(".").replace("'", "").replace("’", "")
        if core.lower() in ("jr", "sr", "ii", "iii", "iv"):
            continue
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class MissouriStyle:
    def parse_author_line(self, text):
        t = text.strip().rstrip(".")
        if t.upper() == "PER CURIAM":
            return "PER CURIAM", "per curiam", None
        if "," in t:
            name, title = t.rsplit(",", 1)
            tl = title.strip().lower().replace(".", "")
            if tl in _MO_TITLES and _mo_name_ok(name):
                return name.strip(), title.strip().title(), None
        return super().parse_author_line(text)

    def find_authors(self, all_segments) -> list:
        self._mo_sig = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # Signature-block fallback: the author signs at the very end ('NAME,
        # Judge'), which the byline pipeline drops as a body-less sign-off. Take
        # the last such signature as the author and run the whole filing as one
        # opinion.
        author = None
        for _p, seg, _k in all_segments:
            for ln in seg:
                txt = self.line_plain_text(ln).strip()
                r = self.parse_author_line(txt)
                if r and r[1] and not self._is_non_author_byline(txt):
                    author = r[0]
        if not author:
            return []
        self._mo_sig = author
        for i, (_p, _seg, kind) in enumerate(all_segments):
            if kind == "body":
                return [i]
        return [0]

    def split_author_line(self, line):
        if getattr(self, "_mo_sig", None):
            return "", [line]  # signature-block model: opening line is body
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_mo_sig", None):
            op.author = self._mo_sig
        return op
