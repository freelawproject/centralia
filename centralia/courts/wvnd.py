"""United States District Court, Northern District of West Virginia.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Two page-1 layouts:

  * A plain style (Times) with a bare, centered page number low on each page —
    body-size, so it can't be told from prose by font; ``fold_page_numbers``
    turns it into a page-break marker instead of a stray body paragraph.
  * A Kleeh style (Courier) that closes the headmatter with a **full-width rule**
    drawn directly beneath the document-type title (a centered, often multi-line
    'MEMORANDUM OPINION AND ORDER GRANTING …' heading). The rule is the
    headmatter/body boundary: the title belongs to the headmatter (one grouped
    heading), the body begins below the rule.
"""

from __future__ import annotations

from ._district import DistrictBase

# The Kleeh-style headmatter rule spans essentially the full text column
# (x0≈70.5, x1≈541.5). Match on width so an interior underline / section rule
# can't be mistaken for it.
_HM_RULE_MIN_WIDTH = 350.0


class NorthernDistrictOfWestVirginia(DistrictBase):
    court_id = "wvnd"
    court_label = "United States District Court, Northern District of West Virginia."

    # wvnd centers a bare page number low on the page (body-size, so it can't be
    # told from prose by font); fold it into a page-break marker so it stops
    # reading as its own body paragraph.
    fold_page_numbers = True

    def _headmatter_rule_top(self):
        """Top of the full-width rule that closes the Kleeh-style headmatter
        (drawn beneath the document-type title), or None. Taken from the page-1
        caption-box geometry already measured by the base."""
        box = getattr(self, "_hm_caption_box", None) or {}
        tops = [
            top
            for top, x0, x1 in box.get("hrules", []) or []
            if (x1 - x0) >= _HM_RULE_MIN_WIDTH
        ]
        return min(tops) if tops else None

    def find_authors(self, all_segments) -> list:
        result = super().find_authors(all_segments)
        rule_top = self._headmatter_rule_top()
        if rule_top is None or not result:
            return result
        # The body begins at the first page-1 segment below the rule; the
        # document-type title above it stays in the headmatter.
        start = result[0]
        for i, (pno, seg, _kind) in enumerate(all_segments):
            if pno == 1 and seg and seg[0].get("top", 0) > rule_top + 2:
                return [i] if i > start else result
        return result

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        rule_top = self._headmatter_rule_top()
        if rule_top is None:
            return super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        # The document-type title is the single-spaced run of lines just above
        # the rule, set off from the (double-spaced) party caption by a blank
        # line. Split it off BEFORE the caption logic runs — a wrapped title
        # line that spans mid-page ('MOTION TO AMEND COMPLAINT [ECF NO. 16]')
        # would otherwise be mistaken for a two-column caption row. Group it
        # into one heading and close the headmatter with the drawn rule.
        title_lines, caption_segs = self._split_title(headmatter_segs, rule_top)
        out = super().extract_headmatter(caption_segs, page1_rules=page1_rules)
        if title_lines:
            html = " ".join(
                self.line_inline_text(l) for l in title_lines
            ).strip()
            heading = {"__hm__": True, "html": html, "rel": 1.0, "align": "C"}
            out["summary"] = list(out.get("summary") or []) + [heading, "__RULE__"]
        return out

    def _split_title(self, headmatter_segs, rule_top):
        """Return (title_lines, caption_segs): the contiguous single-spaced run
        of lines immediately above the rule (the document-type title), and the
        remaining headmatter segments (the party caption) with those lines
        removed."""
        below = [
            l
            for seg in headmatter_segs
            for l in seg
            if self.line_plain_text(l).strip() and l.get("top", 0) < rule_top
        ]
        below.sort(key=lambda l: l["top"])
        if not below:
            return [], headmatter_segs
        title = [below[-1]]
        for l in reversed(below[:-1]):
            if title[0]["top"] - l["top"] <= 20:  # same single-spaced block
                title.insert(0, l)
            else:
                break
        title_top = title[0]["top"]
        caption_segs = [
            kept
            for seg in headmatter_segs
            if (kept := [l for l in seg if l.get("top", 0) < title_top - 1])
        ]
        return title, caption_segs
