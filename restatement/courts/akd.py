"""United States District Court, District of Alaska.

akd's PDFs have a distinctive style, so its parsing tuning lives here (not in the
shared district base) — tuning another district can't regress Alaska:

  * a ruled caption box (often two/three stacked boxes for consolidated cases)
    with a vertical divider — merged across the stacked boxes so every case's
    columns split cleanly, ignoring the full-page pleading-margin rules;
  * the opinion opens with the first ALL-CAPS heading after the caption box
    ('I. INTRODUCTION' / 'ORDER ON MOTIONS TO AMEND AND SUPPLEMENT COMPLAINT');
  * a small-font running footer in the bottom margin (a restated case caption /
    short title / page number) — page furniture, removed by KIND (small font in
    the footer band) and routed to ``dropped``; the blue CM/ECF bates line sits
    below the bottom margin already;
  * footnotes that can sit high on the page — the separator is the topmost thin
    left rule with small (footnote-size) text directly below it.

Author detection (signature block / 'Present:' minute line / opening byline /
caption 'Judge NAME') is inherited from the shared district base.
"""

from __future__ import annotations

from collections import Counter

from ._district import DistrictBase


def _is_allcaps_line(text: str) -> bool:
    """An all-caps heading line ('I. INTRODUCTION' / 'ORDER ON MOTIONS TO AMEND
    AND SUPPLEMENT COMPLAINT') — every letter uppercase, short."""
    t = text.strip()
    letters = [c for c in t if c.isalpha()]
    return len(letters) >= 2 and len(t) < 90 and all(c.isupper() for c in letters)


class DistrictOfAlaska(DistrictBase):
    court_id = "akd"
    court_label = "United States District Court, District of Alaska."

    footer_band_pt = 100  # bottom margin band where the footer sits

    # ---------------------------------------------------------- footer removal
    # The footer is identified by its CONTENT KIND, not by font size or
    # repetition: a restated case caption ('Case No. <docket>, <parties> v.
    # <parties>'), a consolidation tag ('(Lead Case) (Consolidated)'), or a page
    # number ('Page N of N'), sitting in the bottom margin band. Footnotes (also
    # small-font, also sometimes low on the page) are NOT any of these kinds, so
    # they are never caught.
    def extract(self, pdf_path: str):
        self._dropped_footer = []
        doc = super().extract(pdf_path)
        extra = sorted(set(self._dropped_footer))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    @staticmethod
    def _is_footer_furniture(text: str) -> bool:
        low = text.strip().lower()
        if low.startswith("case no."):  # restated case caption
            return True
        bare = low.replace("(", "").replace(")", "").replace(" ", "")
        if bare in ("leadcase", "consolidated", "leadcaseconsolidated"):
            return True
        toks = low.split()  # 'Page N of N'
        return (
            len(toks) == 4
            and toks[0] == "page"
            and toks[2] == "of"
            and toks[1].isdigit()
            and toks[3].isdigit()
        )

    def page_lines(self, page):
        lines = super().page_lines(page)
        h, kept = page.height, []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) > h - self.footer_band_pt and self._is_footer_furniture(
                t
            ):
                self._dropped_footer.append(t)
            else:
                kept.append(l)
        return kept

    # ------------------------------------------------------ caption box divider
    def find_caption_divider(self, page):
        """Vertical caption divider, merging the collinear rules of stacked
        consolidated boxes and ignoring full-page pleading-margin rules."""
        h, w = page.height, page.width
        verts = []

        def consider(x, t, b):
            if (b - t) <= 30 or x < 50 or x > w - 50:
                return
            if t < 40 and b > h - 40:  # full-page border rule
                return
            verts.append((x, t, b))

        for r in page.rects:
            if (r["x1"] - r["x0"]) < 2:
                consider(r["x0"], r["top"], r["bottom"])
        for ln in page.lines:
            x0, x1 = ln["x0"], ln.get("x1", ln["x0"])
            if abs(x1 - x0) < 2:
                consider(x0, ln["top"], ln["bottom"])
        if not verts:
            return None
        groups: dict = {}
        for x, t, b in verts:
            groups.setdefault(round(x / 3), []).append((x, t, b))
        best = max(groups.values(), key=lambda g: sum(b - t for _x, t, b in g))
        return (best[0][0], min(t for _x, t, _b in best), max(b for _x, _t, b in best))

    # ----------------------------------------------------- footnote separator
    def find_footnote_separator(self, page):
        """Topmost thin, left-aligned rule with small (footnote-size) text
        directly below it — finds a footnote sitting high on the page that the
        generic half-page cutoff would miss."""
        chars = page.chars
        if not chars:
            return super().find_footnote_separator(page)
        sizes = Counter(round(c.get("size", 0)) for c in chars)
        small_thresh = sizes.most_common(1)[0][0] - 1.5
        h, cands = page.height, []
        for r in page.rects:
            if not (
                r["height"] < 2.5
                and (r["x1"] - r["x0"]) >= 80
                and r["x0"] < 120
                and r["top"] > h * 0.30
            ):
                continue
            below = [
                c
                for c in chars
                if r["top"] < c["top"] < r["top"] + 22 and not c["text"].isspace()
            ]
            if (
                below
                and min(below, key=lambda c: c["top"]).get("size", 99) <= small_thresh
            ):
                cands.append(r["top"])
        if cands:
            return min(cands)
        return super().find_footnote_separator(page)

    # ------------------------------------------------------------ opinion start
    def find_authors(self, all_segments) -> list:
        # Author detection is inherited; here we set the opinion start to the
        # first ALL-CAPS heading after the ruled caption box (column-tagged), so
        # the consolidated caption stays in the headmatter.
        self._district_author = (
            self._signature_author(all_segments)
            or self._present_author(all_segments)
            or self._byline_author(all_segments)
            or self._caption_judge(all_segments)
        )
        cap_end = -1
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and seg[0].get("_caption_col") in ("L", "R"):
                cap_end = i
        if cap_end >= 0:
            for i in range(cap_end + 1, len(all_segments)):
                seg = all_segments[i][1]
                if seg and _is_allcaps_line(self.line_plain_text(seg[0]).strip()):
                    return [i]
            if cap_end + 1 < len(all_segments):
                return [cap_end + 1]
        return super().find_authors(all_segments)
