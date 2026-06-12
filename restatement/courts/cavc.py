"""United States Court of Appeals for Veterans Claims.

A CM/ECF-style header tops every page ('Case: 24-9605 Page: 1 of 10
Filed: 05/13/2026') — furniture, dropped and surfaced. The caption names
the panel ('Before ALLEN, Chief Judge, and BARTLEY and LAURER, Judges.');
orders are single-spaced (tight segments stay in the body) and close
'DATED: … PER CURIAM.' — the author when no byline names a judge.
"""

from __future__ import annotations

from ._district import DistrictBase


class VeteransClaimsCourt(DistrictBase):
    court_id = "cavc"
    court_label = "United States Court of Appeals for Veterans Claims."

    def page_lines(self, page):
        if not hasattr(self, "_cavc_dropped"):
            self._cavc_dropped = []
        lines = super().page_lines(page)
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) < 30 and t.lower().startswith("case:"):
                self._cavc_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def extract(self, pdf_path: str):
        self._cavc_dropped = []
        doc = super().extract(pdf_path)
        if self._cavc_dropped:
            seen, extra = set(), []
            for t in self._cavc_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        # 'DATED: … PER CURIAM.' close — the Court speaks per curiam. The
        # 'Before ALLEN, …' panel roster is not an author.
        for o in doc.opinions:
            if (o.author or "").startswith("Before"):
                o.author = ""
        if doc.opinions and not doc.opinions[0].author:
            op = doc.opinions[-1]
            for b in op.blocks[-3:]:
                if "PER CURIAM" in self._untag(str(b.text)).upper():
                    for o in doc.opinions:
                        if not o.author:
                            o.author = "PER CURIAM"
                    break
        return doc