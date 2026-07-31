"""Supreme Court of Rhode Island.

Reversed-title prose byline, bold, running inline with the opinion text:
  'Justice Robinson, for the Court. The defendant ...'        (majority)
  'Justice Lynch Prata, for the Court. The plaintiffs ...'
  'Justice Long, concurring. ...' / 'Chief Justice Suttell, dissenting. ...'
The title leads, the (title-case) surname follows, then a role — 'for the
Court' (majority) or a concur/dissent kind. A 'Present: Suttell, C.J., ...'
panel roster and a 'Justice Goldberg did not participate.' note are NOT
bylines: the first does not lead with the singular title, the second has no
', for the Court' / kind role after the name.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

_TITLES = ("Chief Justice", "Justice")


def _is_title_name(name: str) -> bool:
    """Title-case justice name, 1–4 tokens (allows a two-word surname like
    'Lynch Prata' and a middle initial)."""
    toks = name.split()
    if not (1 <= len(toks) <= 4):
        return False
    for tok in toks:
        core = tok.rstrip(".").replace("'", "").replace("-", "")
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class RhodeIslandSupreme(StateSupreme):
    court_id = "ri"
    court_label = "Supreme Court of Rhode Island."

    def extract(self, pdf_path):
        self._ri_order_start = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._ri_order_start = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # A per-curiam order has no 'Justice X, for the Court.' byline; its body
        # opens just after the centered, letter-spaced 'O R D E R' (or 'OPINION')
        # header.
        for i, (_p, seg, _k) in enumerate(all_segments):
            head = self.line_plain_text(seg[0]).strip().replace(" ", "").upper()
            if head in ("ORDER", "OPINION") and i + 1 < len(all_segments):
                self._ri_order_start = i + 1
                return [i + 1]
        return []

    def split_author_line(self, line):
        # The order opens on body text (no byline); keep it as the first body
        # line and let build_opinion stamp PER CURIAM.
        if getattr(self, "_ri_order_start", None) is not None:
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_ri_order_start", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op

    def _ri_parse(self, text: str):
        """Return (name, title, kind, byline_end) or None."""
        for title in _TITLES:
            if not text.startswith(title + " "):
                continue
            rest = text[len(title) + 1 :]
            if "," not in rest:
                return None
            name, after = rest.split(",", 1)
            name = name.strip()
            if not _is_title_name(name):
                return None
            # A separate writing can name its joiners between the author and the
            # role: 'Justice Long, with whom Justice Lynch Prata joins,
            # dissenting.' Step over that clause so the role is read from the
            # clause that actually carries it. Without this the whole dissent was
            # missed, and its footnotes — numbered from 1 again — collided with
            # the majority's and were lost.
            while True:
                clause, sep, tail = after.partition(",")
                cl = clause.strip().lower()
                if sep and (cl.startswith("with whom") or " join" in " " + cl):
                    after = tail
                    continue
                break
            low = after.strip().lower()
            if low.startswith("for the court"):
                kind = None
            elif low.startswith("concurr") and "dissent" in low[:40]:
                kind = "concurring in part and dissenting in part"
            elif low.startswith("concurr"):
                kind = "concurring"
            elif low.startswith("dissent"):
                kind = "dissenting"
            else:
                return None
            # The byline runs to the first period after the role.
            pi = text.find(".", len(title) + 1 + len(name))
            end = pi + 1 if pi != -1 else len(text)
            return name, title, kind, end
        return None

    def parse_author_line(self, text):
        r = self._ri_parse(text.strip())
        if r is not None:
            return r[0], r[1], r[2]
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        r = self._ri_parse(text)
        if r is None:
            return super()._byline_split(line)
        end = r[3]
        return text[:end], text[end:].lstrip()
