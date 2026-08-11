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
from ..models import Block

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

    def page_lines(self, page):
        """Remove printed continuation-page furniture.

        TCCA uses either a bare page number at the upper-right (the short
        per-curiam dispositions) or ``CASE NAME — N`` there (full opinions).
        Both are outside the body measure and live wholly in the top band.
        """
        lines = super().page_lines(page)
        if page.page_number == 1:
            return lines
        kept = []
        for line in lines:
            text = self.line_plain_text(line).strip()
            upper_right = line.get("x0", 0) > page.width * 0.62
            in_top_band = line.get("top", 999) < 90
            bare_number = text.isdigit() and len(text) <= 3
            numbered_head = (
                text[-1:].isdigit()
                and any(mark in text for mark in ("—", "–"))
                and len(text) <= 48
            )
            if in_top_band and upper_right and (bare_number or numbered_head):
                continue
            kept.append(line)
        return kept

    def find_footnote_separator(self, page) -> Optional[float]:
        # The title page's caption-box bottom rule sits in the lower half and
        # would otherwise be mistaken for a footnote separator, dropping the
        # byline + body of a separate writing below it.
        found = self._footnote_sep_small_text_below(page)
        if found is not None:
            return found

        # Equity-generated slips draw the same short separator as a PDF curve
        # rather than a rectangle.  Geometry is stable: a thin, left-anchored
        # horizontal stroke in the lower body, immediately followed by type at
        # least 1pt smaller than the page's dominant body face.
        from collections import Counter

        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        if not chars:
            return None
        body = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        candidates = []
        for curve in page.curves:
            width = curve.get("x1", 0) - curve.get("x0", 0)
            height = curve.get("bottom", 0) - curve.get("top", 0)
            if not (
                height < 2.5
                and 80 <= width <= page.width * 0.4
                and curve.get("x0", page.width) < page.width * 0.25
                and curve.get("top", 0) > page.height * 0.45
            ):
                continue
            below = [
                c
                for c in chars
                if curve["top"] < c["top"] < curve["top"] + 24
            ]
            if below and min(below, key=lambda c: c["top"]).get("size", 99) <= body - 1:
                candidates.append(curve["top"])
        if candidates:
            return min(candidates)
        # DECLINE, DON'T DENY. Both tests above want footnote-SIZE type directly
        # under the rule, which a zone opening with the unlabelled tail of a
        # note carried from the previous page cannot show — lewis_howard_wayne
        # sets that tail at body size on page 77 and opens note 24 two lines
        # below it. Returning None here put every shared path out of reach even
        # though all of them find the rule (``_fenceless_sep`` and the base
        # chain both return 331.32), and notes 24, 25, 28-31 and 43 were
        # delivered as body prose.
        return super().find_footnote_separator(page)

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
        author_line = kwargs["all_segments"][op_start][1][0]
        author_page = kwargs["all_segments"][op_start][0]
        parsed = self._tcca_byline(self.line_plain_text(author_line).strip())
        if parsed is not None:
            if parsed[0] == "PER CURIAM":
                op.author = parsed[0]
            else:
                abbreviation = next(
                    ab for ab, full in _TCCA_TITLES if full == parsed[1]
                )
                op.author = f"{parsed[0]}, {abbreviation}"

        # A delivered/filed announcement often wraps for two or three lines
        # before the centered OPINION banner.  Those continuation lines describe
        # votes and separately filed documents; they are not opinion text.
        if parsed is not None and parsed[0] != "PER CURIAM":
            banner = next(
                (
                    i
                    for i, block in enumerate(op.blocks[:6])
                    if "OPINION" in "".join(
                        str(block.text or "").upper().split()
                    ).replace("<STRONG>", "").replace(
                        "</STRONG>", ""
                    )
                ),
                None,
            )
            pieces = [self.line_inline_text(author_line).strip()]
            if banner is not None:
                pieces.extend(
                    str(block.text or "").strip()
                    for block in op.blocks[:banner]
                    if str(block.text or "").strip()
                )
                op.blocks = op.blocks[banner:]
            marker = self.page_marker(author_page)
            if marker:
                pieces = [piece.replace(marker, "").strip() for piece in pieces]
            announcement = " ".join(pieces).strip()
            if announcement:
                op.caption.append(
                    Block(
                        kind="p",
                        text=announcement,
                        page=author_page,
                        payload={"role": "announcement"},
                    )
                )
        if getattr(self, "_tcca_pc", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op
