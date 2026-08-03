"""Shared base for state Attorney General opinions ('mdag', 'minnag',
'texag').

Letter-form rulings: headmatter is the letterhead/topic block, date, and
addressee; the body opens at the salutation ('Dear Mr. Gonzales:') or — for
formal-opinion formats with no salutation (Maryland) — at the first full
paragraph after the date line. The author is the signing officer: the name
line above (or merged with) the 'Attorney General' title near the end.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


def _is_date_row(text: str) -> bool:
    toks = text.replace(",", "").split()
    return (
        len(toks) == 3
        and toks[0].isalpha()
        and toks[1].isdigit()
        and len(toks[2]) == 4
        and toks[2].isdigit()
    )


class AGLetterBase(StateSupreme):
    def extract(self, pdf_path):
        self._letter_start = None
        self._letter_author = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        self._letter_start = None
        if starts:
            return starts
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip() if seg else ""
            if t.rstrip(":").startswith("Dear "):
                start = i
                break
        if start is None:
            # Formal-opinion format: the first wide multi-line paragraph
            # after the date row.
            pw = getattr(self, "_page1_width", 612.0) or 612.0
            seen_date = False
            for i, (_p, seg, _k) in enumerate(all_segments):
                texts = [self.line_plain_text(l).strip() for l in seg]
                if any(_is_date_row(t) for t in texts):
                    seen_date = True
                    continue
                if (
                    seen_date
                    and len(seg) >= 2
                    and max(l["x1"] - l["x0"] for l in seg) > pw * 0.5
                ):
                    start = i
                    break
        if start is None:
            # A reporter-form opinion may put the addressee and opening answer
            # in one uninterrupted segment. Split at the request line only
            # after the date-based format has had first claim; otherwise a
            # later phrase such as ``You have asked whether`` can steal page 11
            # from an opinion that began on page 1.
            for i, (pno, seg, kind) in enumerate(all_segments):
                cut = next(
                    (
                        j
                        for j, line in enumerate(seg)
                        if self.line_plain_text(line).strip().lower().startswith(
                            ("you have asked", "you ask whether")
                        )
                    ),
                    None,
                )
                if cut is None:
                    continue
                if cut:
                    before, body = seg[:cut], seg[cut:]
                    all_segments[i : i + 1] = [
                        (pno, before, self.classify_segment(before)),
                        (pno, body, self.classify_segment(body)),
                    ]
                    start = i + 1
                else:
                    start = i
                break
        if start is None:
            return []
        self._letter_start = start
        self._letter_author = self._signature_author(all_segments)
        return [start]

    def _signature_author(self, all_segments):
        """The signing officer: scanning from the end, a short title line
        containing 'Attorney General' with a name line directly above."""
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, 0, -1):
            t = lines[i]
            low = t.lower()
            if "attorney general" in low and len(t) < 45 and not low.startswith(
                ("assistant", "deputy", "the ", "office")
            ):
                name = lines[i - 1].strip()
                toks = name.replace(".", "").split()
                if 2 <= len(toks) <= 5 and all(
                    w[:1].isupper() for w in toks if w[:1].isalpha()
                ):
                    return f"{name}, {t}"
        return None

    def split_author_line(self, line):
        if getattr(self, "_letter_start", None) is not None:
            return (self._letter_author or ""), [line]
        return super().split_author_line(line)
