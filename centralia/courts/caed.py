"""United States District Court, Eastern District of California.

CM/ECF filing — a single ruling by one judge. The shared district base takes
the author from the signature block and treats the whole ruling as one
opinion; the pleading line-number gutter and CM/ECF header band are dropped.

Body is double-spaced with a first-line paragraph indent, and section heads
are short BOLD standalone lines — a centered title ('Screening Order') or a
left enumerator ('I. Legal Standard' / 'II. Analysis'). Those head lines are
kept out of the surrounding paragraph (each stands alone) and rendered as
headings; the generic re-based indent split handles the body paragraphs.
"""

from __future__ import annotations

import re

from ._district import DistrictBase

_TAG = re.compile(r"<[^>]+>")
_ROMAN = set("IVXLC")


def _is_section_heading(t: str) -> bool:
    t = t.strip()
    if not t or len(t) > 60:
        return False
    head, _, rest = t.partition(" ")
    num = head.rstrip(".")
    if head.endswith(".") and rest and (
        all(c in _ROMAN for c in num)
        or (len(num) == 1 and num.isalpha())
        or num.isdigit()
    ):
        return True  # 'I. Legal Standard' / 'A. …' / '1. …'
    return (
        len(t.split()) <= 6
        and not t.endswith((".", ",", ";", ":"))
        and t[0].isupper()
    )  # 'Screening Order' / 'BACKGROUND'


class EasternDistrictOfCalifornia(DistrictBase):
    court_id = "caed"
    styled_headmatter = True
    court_label = "United States District Court, Eastern District of California."

    def _is_heading_line(self, line) -> bool:
        _sz, _fn, bold = self.line_meta(line)
        return bold and _is_section_heading(self.line_plain_text(line).strip())

    def split_body_paragraphs(self, seg) -> list:
        # a bold heading line never merges into a body paragraph — it stands
        # alone, and the line after it begins a fresh paragraph
        paras, i = [], 0
        run = []
        for line in seg:
            if self._is_heading_line(line):
                if run:
                    paras.extend(super().split_body_paragraphs(run))
                    run = []
                paras.append([line])
            else:
                run.append(line)
        if run:
            paras.extend(super().split_body_paragraphs(run))
        return paras

    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            for b in op.blocks:
                if b.kind == "p" and "<strong>" in str(b.text):
                    inner = _TAG.sub("", str(b.text)).strip()
                    if self._all_bold(b.text) and _is_section_heading(inner):
                        b.kind = "heading"
        return doc

    @staticmethod
    def _all_bold(html: str) -> bool:
        outside, s = [], str(html)
        while True:
            i = s.find("<strong>")
            if i < 0:
                outside.append(s)
                break
            outside.append(s[:i])
            j = s.find("</strong>", i)
            if j < 0:
                break
            s = s[j + len("</strong>"):]
        return not any(c.isalnum() for c in _TAG.sub("", "".join(outside)))
