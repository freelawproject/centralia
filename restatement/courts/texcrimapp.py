"""Texas Court of Criminal Appeals.

The State's highest criminal court. Each published PDF carries a single opinion
(a separate concurrence/dissent is filed as its own document), opened by a bold
announcement byline that names the author and a verb:

    'PARKER, J., delivered the opinion of the Court in which ...'   (majority)
    'RICHARDSON, J., delivered the opinion of the Court ...'
    'Schenck, P.J., filed a dissenting opinion in which ...'        (dissent)
    'Finley, J., filed a concurring opinion in which ...'           (concurrence)
    'SCHENCK, P.J., filed a concurring and dissenting opinion ...'  (concur+dissent)
    'Per curiam.'                                                   (per curiam)

The surname may be all-caps ('PARKER') or title-case ('Schenck'); the title is
abbreviated ('J.' / 'P.J.' / 'C.J.'). The announcement runs on to list the
judges who joined and the separate writings filed by others ('... MCCLURE, J.,
concurred. SCHENCK, P.J., filed a ...') — those name *other* documents, so only
the FIRST byline is the author of this opinion. A centered 'OPINION' header
follows, then the body.
"""

from __future__ import annotations

from typing import Optional

from ._appellate import StateAppellate

# Abbreviated titles this court uses, longest first ('P.J.'/'C.J.' before 'J.').
_TCCA_TITLES = (("P.J.", "Presiding Judge"), ("C.J.", "Chief Judge"), ("J.", "Judge"))
# Verbs that mark an authorship announcement (not a join/vote line).
_TCCA_VERBS = ("delivered", "filed", "announced")


class TexasCourtOfCriminalAppeals(StateAppellate):
    court_id = "texcrimapp"
    court_label = "Texas Court of Criminal Appeals."
    # The body is double-spaced; quoted material (block quotes of the notices of
    # appeal, statutes) is single-spaced and would be classified 'notice' by gap
    # and dropped — keep all body content.
    drop_notice_in_body = False

    def find_footnote_separator(self, page) -> Optional[float]:
        # The title page's caption-box bottom rule sits in the lower half and
        # would otherwise be mistaken for a footnote separator, dropping the
        # byline + body of a separate writing below it.
        return self._footnote_sep_small_text_below(page)

    @staticmethod
    def _tcca_name_ok(name: str) -> bool:
        toks = name.split()
        if not toks or len(toks) > 3:
            return False
        return all(
            t[:1].isupper() and t.replace("'", "").replace("-", "").isalpha()
            for t in toks
        )

    def _tcca_byline(self, text: str):
        """Parse an announcement byline -> (name, title, kind) or None."""
        t = text.strip()
        if t.lower().startswith("per curiam"):
            return ("PER CURIAM", "per curiam", None)
        if "," not in t:
            return None
        name, after = (s.strip() for s in t.split(",", 1))
        title = next((full for ab, full in _TCCA_TITLES if after.startswith(ab)), None)
        if title is None or not self._tcca_name_ok(name):
            return None
        ab = next(ab for ab, _f in _TCCA_TITLES if after.startswith(ab))
        rest = after[len(ab) :].lstrip(", ").lower()
        verb = rest.split()[0] if rest.split() else ""
        if verb not in _TCCA_VERBS:
            return None
        if "concur" in rest and "dissent" in rest:
            kind = "concurring in part and dissenting in part"
        elif "concur" in rest:
            kind = "concurring"
        elif "dissent" in rest:
            kind = "dissenting"
        else:
            kind = None
        return name, title, kind

    def parse_author_line(self, text):
        r = self._tcca_byline(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_at(self, line) -> bool:
        return self._tcca_byline(self.line_plain_text(line).strip()) is not None

    def find_authors(self, all_segments) -> list:
        self._tcca_pc = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            r = self._tcca_byline(self.line_plain_text(seg[0]).strip())
            if r is not None:
                if r[0] == "PER CURIAM":
                    self._tcca_pc = i
                return [i]  # one opinion per PDF; later announcements name others
        return []

    def split_author_line(self, line):
        if getattr(self, "_tcca_pc", None) is not None:
            return "", [line]  # 'Per curiam.' opens the body
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_tcca_pc", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op
