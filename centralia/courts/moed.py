"""United States District Court, Eastern District of Missouri.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

moed sets its footnotes at BODY size with only the reference mark superscripted,
so the base's footnote-separator test — which expects the text below the rule to
be a smaller point size — rejects the (short, left-anchored) separator and the
footnote reads as body. Recognize the separator by the small superscript label
opening the first line below it instead.
"""

from __future__ import annotations

from ._district import DistrictBase


class EasternDistrictOfMissouri(DistrictBase):
    court_id = "moed"
    court_label = "United States District Court, Eastern District of Missouri."

    # moed centers a page number ('- 2 -') in the bottom margin. It sits BELOW
    # the footnote separator, so it would otherwise be swept into the footnote
    # flow (or read as a stray body line on pages with no footnotes). Drop it as
    # page furniture and surface it in the Removed box.
    def extract(self, pdf_path):
        self._dropped_page_nums = []
        doc = super().extract(pdf_path)
        extra = sorted(set(self._dropped_page_nums))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def page_lines(self, page):
        lines = super().page_lines(page)
        cutoff = page.height * 0.8
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) > cutoff and self._is_page_number_text(t):
                self._dropped_page_nums.append(t)
            else:
                kept.append(l)
        return kept

    def _rule_over_footnotes(self, page, rule_top) -> bool:
        if super()._rule_over_footnotes(page, rule_top):
            return True
        # The footnote body matches the body point size (so the median-size
        # test fails); the tell is a small superscript marker starting the
        # first line just below the rule.
        below = [
            ln
            for ln in page.extract_text_lines()
            if rule_top + 2 < ln["top"] <= rule_top + 40
        ]
        if not below:
            return False
        below.sort(key=lambda ln: ln["top"])
        chars = below[0].get("chars") or []
        if not chars:
            return False
        body = max((c.get("size", 0) for c in chars), default=0)
        first = chars[0]
        return (
            first.get("text", "") in self.FOOTNOTE_LABEL_CHARS
            and round(first.get("size", 0), 1) <= body - 1.5
        )
