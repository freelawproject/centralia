"""United States District Court, Western District of Texas.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Two txwd-specific structures the shared base mis-reads:

1. **Footnote labels are NOT a pleading-paper line-number rail.** txwd rulings
   set footnotes at the left text margin, each opening with its number
   ('6 Id. at 4.' / '7 Sentencing Tr. …'), so a page carrying eight or more
   footnotes shows a far-left column of small sequential integers — exactly the
   shape the base's no-rule pleading-gutter fallback looks for. It then dropped
   every char left of that column's right edge, eating the FIRST GLYPH of every
   body line on the page ('MAIC' → 'AIC'). See ``_pleading_gutter_by_numbers``.

2. **Standing orders have no caption at all.** The judges' 'STANDING ORDER IN
   CIVIL CASES' sheets open with a centred bold title and go straight into
   numbered instructions; there is no party caption. The numbered list items
   ('(1) Counsel shall confer …' / '(2) …' / '(3) …') stack three '(' glyphs in
   one x-column, which the caption fingerprint read as a parenthetical rail —
   putting the caption's bottom edge two thirds of the way down page 1 and so
   dumping the whole first page of the order into headmatter, line by line
   instead of as paragraphs. See ``_caption_band_bottom``.
"""

from __future__ import annotations

from ._district import DistrictBase

# A page-1 caption sits directly under the court banner, in the top quarter of
# the sheet; every real txwd caption rail ('§', ')') in the corpus begins
# between y=125 and y=143. A glyph column that only starts a third of the way
# down the page is body text that happens to line up, not a caption rail.
_RAIL_TOP_MAX = 200.0

# A pleading-paper line-number rail runs the full height of the sheet (1-28).
# A footnote-label column occupies only the bottom fifth.
_GUTTER_MIN_SPAN = 0.5
_GUTTER_MIN_COUNT = 15


class WesternDistrictOfTexas(DistrictBase):
    court_id = "txwd"
    court_label = "United States District Court, Western District of Texas."

    # ------------------------------------------- footnote labels vs. a gutter
    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """Infer a line-number gutter from the number column ONLY when the
        column really runs down the page.

        The base fallback accepts any far-left stack of eight mostly-sequential
        integers. On txwd that matches the footnote labels at the foot of the
        page, and the caller then filters out every char left of the column —
        which is the body's own left margin, so the first letter of every line
        on the page is lost. A genuine 1-28 pleading rail is distinguishable by
        geometry: ~25 numbers spanning most of the page height. A footnote block
        gives 8-10 numbers inside the bottom fifth.
        """
        gx = DistrictBase._pleading_gutter_by_numbers(page)
        if gx is None:
            return None
        tops = [
            w["top"]
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if len(tops) < _GUTTER_MIN_COUNT:
            return None
        span = (max(tops) - min(tops)) / max(page.height, 1.0)
        return gx if span >= _GUTTER_MIN_SPAN else None

    # --------------------------------------------- the title is not the ruling
    def find_authors(self, all_segments) -> list:
        """Keep a captionless sheet's CENTRED TITLE in the headmatter.

        Judge Garcia's standing order sets its title at 14pt — the same size as
        the body — and every page-1 segment is single-spaced, so no segment
        classifies as 'body' and the base's last-resort fallback ('the first
        multi-line blockquote') lands on the title itself. The title then
        rendered as the ruling's opening paragraph, leaving the headmatter with
        nothing but the two rules that UNDERLINE the title — which, with no row
        above them to attach to, drew as two full-width dividers that the page
        never had.

        A centred block at the head of page 1 that is not one of the recognised
        document-type headings is the sheet's title: the ruling starts at the
        first line back at the body margin.
        """
        idx = super().find_authors(all_segments)
        if not idx:
            return idx
        start = idx[0]
        pno, seg, _kind = all_segments[start]
        if pno != 1 or not seg or self._is_heading(seg[0]):
            return idx
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        if not all(self.line_alignment(l, pw) == "C" for l in seg):
            return idx
        for j in range(start + 1, len(all_segments)):
            pno2, seg2, _k2 = all_segments[j]
            if pno2 != 1:
                break
            if (
                seg2
                and self.line_alignment(seg2[0], pw) == "L"
                and seg2[0]["x0"] <= self.body_baseline_x0 + 4
            ):
                return [j]
        return idx

    # ------------------------------------------- hanging-indent continuations
    def segment_lines(self, lines, page_width) -> list:
        """Re-join a wrapped line that the base cut into its own segment.

        The standing orders are set as a single-spaced outline: each item's
        FIRST line hangs out to the left of its continuations
        ('(1) Counsel shall confer …' at x=112, the rest at x=130; '• To
        facilitate …' at x=148, the rest at x=166), and emphasis switches from
        roman to bold mid-sentence. Every one of those is a segment boundary for
        the base (indent shift, bold flip), so one outline item arrived as two
        or three segments and rendered as two or three paragraphs, splitting
        sentences mid-phrase.

        The join is purely geometric: a line that reached the right measure
        WRAPPED, so the line one pitch below it — at its own margin or one
        hanging-indent step in from it — is its continuation, not a new
        paragraph.
        """
        segs = super().segment_lines(lines, page_width)
        out: list = []
        for seg in segs:
            if out and self._continues_previous(out[-1], seg, page_width):
                out[-1] = out[-1] + seg
            else:
                out.append(seg)
        return out

    def _continues_previous(self, prev, seg, page_width) -> bool:
        if not prev or not seg:
            return False
        last, first = prev[-1], seg[0]
        if self.is_separator_line(last) or self.is_separator_line(first):
            return False
        # Same type size — a heading never continues into body text.
        if abs(self.line_meta(last)[0] - self.line_meta(first)[0]) >= 1.0:
            return False
        # One line pitch below: single-spaced continuation, no paragraph gap.
        height = max(last["bottom"] - last["top"], 1.0)
        gap = first["top"] - last["top"]
        if not 0 < gap <= 1.4 * height:
            return False
        # The line above must have reached the measure — only a full line wraps.
        right_edge = page_width - self.body_baseline_x0
        measure = right_edge - self.body_baseline_x0
        if last["x1"] < right_edge - 0.06 * measure:
            return False
        # The continuation sits at the same margin, or one hanging-indent step
        # in from it. Anything further right is a nested block, not a wrap.
        if not (
            last["x0"] - 2 <= first["x0"] <= last["x0"] + 1.5 * self.indent_step
        ):
            return False
        # Every line of the continuation shares that margin.
        return all(abs(l["x0"] - first["x0"]) <= 3 for l in seg)

    # --------------------------------------------- standing orders: no caption
    def _caption_band_bottom(self):
        """The caption's bottom edge — or None on a sheet with no caption.

        A standing order's numbered list stacks '(' glyphs in one column well
        below the title. The fingerprint reports that column as a rail, and the
        base would then treat everything above its last glyph as caption. A
        caption band that does not START in the top quarter of page 1 is not a
        caption, so report 'no band' and let the opinion open at the first body
        paragraph under the title.
        """
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        if sig:
            rail_band = sig.get("rail_band")
            if rail_band and rail_band[0] > _RAIL_TOP_MAX:
                if not sig.get("vmid") and not sig.get("typed_band"):
                    return None
        return super()._caption_band_bottom()
