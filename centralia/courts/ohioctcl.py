"""Ohio Court of Claims.

Ohio-style: a '[Cite as …]' line above the banner (dropped + surfaced),
a whitespace caption that names the judge inline ('Requester    Judge
Lisa L. Sadler' / 'v.    DECISION AND ENTRY'), then '{¶1}'-numbered
paragraphs. Later pages carry a 'Case No. … -2- DECISION & ENTRY' running
head; the tail has 'Filed <date> / Sent to S.C. Reporter <date>' clerk
stamps — furniture, dropped and surfaced.
"""

from __future__ import annotations

from .generic import GenericExtractor


class OhioCourtOfClaims(GenericExtractor):
    court_id = "ohioctcl"
    court_label = "Ohio Court of Claims."

    # the '[Cite as …]' line sits at top≈38 — keep it in the flow so the
    # cite drop below can record it (default margin_top=39 ate it silently)
    margin_top = 30
    # exhibit-table rows are tightly pitched and read as 'notice' — keep
    # them in the body (completeness-first)
    drop_notice_in_body = False

    def extract_page_tables(self, page):
        # completeness-first (the district rule): exhibit tables stay as
        # body lines so their rows are never excluded
        return []

    def page_lines(self, page):
        if not hasattr(self, "_octcl_dropped"):
            self._octcl_dropped = []
        lines = super().page_lines(page)
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            low = t.lower()
            # cite line / running head / clerk stamps
            if t.startswith("[Cite as ") or (
                page.page_number > 1
                and l.get("top", 0) < 60
                and low.startswith("case no.")
            ) or low.startswith(("filed ", "sent to s.c. reporter")):
                if t:
                    self._octcl_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def find_authors(self, all_segments) -> list:
        # author: the caption's inline 'Judge NAME' / 'Magistrate NAME';
        # the opinion starts at the first '{¶' paragraph
        self._octcl_author = None
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            for l in seg:
                t = self.line_plain_text(l).strip()
                if self._octcl_author is None:
                    for key in ("Judge ", "Magistrate "):
                        ki = t.find(key)
                        if ki >= 0:
                            cand = t[ki + len(key) :].strip()
                            if 2 <= len(cand.split()) <= 4 and all(
                                w[:1].isupper() for w in cand.split()
                            ):
                                self._octcl_author = key + cand
                                break
            if start is None and seg and self.line_plain_text(seg[0]).lstrip().startswith(
                "{¶"
            ):
                start = i
        return [start] if start is not None else super().find_authors(all_segments)

    def split_author_line(self, line):
        return (getattr(self, "_octcl_author", None) or ""), [line]

    def extract(self, pdf_path: str):
        self._octcl_dropped = []
        doc = super().extract(pdf_path)
        if self._octcl_dropped:
            seen, extra = set(), []
            for t in self._octcl_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc
