"""United States District Court, Middle District of North Carolina.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Some ncmd rulings (the Magistrate Judge 'MEMORANDUM OPINION AND RECOMMENDATION'
docs) are set in TWO COLUMNS — left column x≈72-293, right column x≈324-540, a
whitespace gutter between. pdfplumber clusters by baseline, so the two columns
merge onto one line and read straight across ('The plaintiff … violated federal
…'), scrambling the text. ``page_lines`` detects the gutter and reflows each
page into proper reading order: full-width rows (banner / heading) in place,
then the left column top-to-bottom, then the right column. Single-column
rulings fall through to the base unchanged.
"""

from __future__ import annotations

from ._district import DistrictBase


class MiddleDistrictOfNorthCarolina(DistrictBase):
    court_id = "ncmd"
    court_label = "United States District Court, Middle District of North Carolina."

    # ------------------------------------------------------ two-column reflow
    def classify_segment(self, seg) -> str:
        """Two-column ncmd rulings are SINGLE-spaced, so a normal body
        paragraph's tight line pitch lands in the base's 'notice' band (which
        is for small-print blocks) and would emit one block per line. A real
        notice/footnote is also small-FONT; a single-spaced body paragraph is
        body-size. Re-tag tight, body-size, multi-line segments as body."""
        k = super().classify_segment(seg)
        if k == "notice" and getattr(self, "_ncmd_two_col", False) and len(seg) >= 2:
            # never re-tag the page-1 caption (it is also tight) — its band
            # comes from the fingerprint's ')' rail extent
            if not self._in_caption_band(seg):
                from collections import Counter

                sizes = Counter(
                    round(c.get("size", 0))
                    for l in seg
                    for c in (l.get("chars") or [])
                    if (c.get("text") or "").strip()
                )
                if sizes and sizes.most_common(1)[0][0] >= 12:
                    return "body"
        return k

    def _in_caption_band(self, seg) -> bool:
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        rb = sig.get("rail_band") if sig else None
        if not rb:
            return False
        line = seg[0]
        chars = line.get("chars") or []
        pno = (chars[0].get("page_number") if chars else None) or 1
        return pno == 1 and line.get("top", 0) <= rb[1] + 4

    # Opinion start: the document heading sits right below the caption; the
    # reflow can split it ('MEMORANDUM OPINION AND RECOMMENDATION / OF UNITED
    # STATES / MAGISTRATE JUDGE'), so the exact-phrase heading scan misses it
    # and the body fallback would start AT the caption. Start at the first
    # page-1 segment below the ')' rail band instead (the ncwd pattern).
    def find_authors(self, all_segments) -> list:
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        rb = sig.get("rail_band") if sig else None
        if rb and getattr(self, "_ncmd_two_col", False):
            self._district_author = (
                self._signature_author(all_segments)
                or self._present_author(all_segments)
                or self._byline_author(all_segments)
                or self._caption_judge(all_segments)
            )
            for i, (pno, seg, _k) in enumerate(all_segments):
                if pno != 1:
                    break
                if seg and seg[0].get("top", 0) > rb[1] + 4:
                    return [i]
        return super().find_authors(all_segments)

    def split_body_paragraphs(self, seg):
        """Paragraph-start indent is relative to the COLUMN's own left edge.
        The base measures it from the page body baseline (x≈72); the right
        column starts at x≈324, so every right-column line would read as
        'indented' and become its own paragraph. Re-base on the segment's
        minimum x0 so first-line indents split correctly within each column."""
        if not getattr(self, "_ncmd_two_col", False) or len(seg) < 2:
            return super().split_body_paragraphs(seg)
        base = min(l["x0"] for l in seg)
        indent_min = base + self.para_indent_min
        paras = [[seg[0]]]
        for line in seg[1:]:
            if line["x0"] > indent_min:
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def page_lines(self, page):
        self.correct_page_geometry(page)
        raw = self._text_lines(page.filter(self.filter_margins))
        g = self._two_col_gutter(raw, page.width)
        if g is None:
            return super().page_lines(page)  # single column → base handles it
        self._ncmd_two_col = True

        out, left, right = [], [], []

        def flush():
            # Tag each column distinctly so segment_lines breaks at the
            # left→right transition (col_changed) — otherwise the negative
            # top jump between columns doesn't trigger a break and the two
            # columns merge into one segment, defeating the per-column
            # paragraph re-base.
            for l in sorted(left, key=lambda l: l["top"]):
                l["_caption_col"] = "BL"
                out.append(l)
            for l in sorted(right, key=lambda l: l["top"]):
                l["_caption_col"] = "BR"
                out.append(l)
            left.clear()
            right.clear()

        for l in sorted(raw, key=lambda l: l["top"]):
            printable = [
                c for c in (l.get("chars") or []) if (c.get("text") or "").strip()
            ]
            if not printable:
                continue
            lc = [c for c in printable if c["x1"] <= g]
            rc = [c for c in printable if c["x0"] >= g]
            straddle = any(c["x0"] < g < c["x1"] for c in printable)
            if straddle or not (lc and rc):
                # a full-width row (banner / centered heading) is a barrier
                # between column bands; a purely one-sided row joins its column
                if not straddle and lc and not rc:
                    left.append(l)
                elif not straddle and rc and not lc:
                    right.append(l)
                else:
                    flush()
                    out.append(l)
            else:
                # a merged two-column row — split it at the gutter
                left.append(self._mk_line(lc))
                right.append(self._mk_line(rc))
        flush()
        self._tag_underlined_chars(page, out)
        return self._maybe_drop_running_header(page, out)

    @staticmethod
    def _two_col_gutter(lines, pw):
        """Gutter x of a two-column body, or None. Merged two-column rows all
        START at the left margin, so line-start clustering can't see the
        split — instead measure per-x LINE COVERAGE (how many rows have a
        glyph at each x) and look for a central VALLEY (the gutter, crossed by
        almost nothing) between two populated column peaks. A full-width banner
        crosses the gutter but is only one or two rows, so the valley stays
        deep."""
        w = int(pw) + 1
        cover = [0] * w
        nrows = 0
        for l in lines:
            cs = [c for c in (l.get("chars") or []) if (c.get("text") or "").strip()]
            if not cs:
                continue
            nrows += 1
            for c in cs:
                for i in range(max(0, int(c["x0"])), min(w - 1, int(c["x1"])) + 1):
                    cover[i] += 1
        if nrows < 6:
            return None
        lo, hi = int(pw * 0.42), int(pw * 0.56)
        peak_l = max(cover[int(pw * 0.15):int(pw * 0.40)] or [0])
        peak_r = max(cover[int(pw * 0.58):int(pw * 0.80)] or [0])
        if peak_l < 5 or peak_r < 5:
            return None
        gx = min(range(lo, hi), key=lambda i: cover[i])
        if cover[gx] > 0.2 * min(peak_l, peak_r):
            return None  # no clear gutter — single column
        return gx

    @staticmethod
    def _mk_line(chars):
        """A synthetic line dict over one column's subset of a row's chars,
        carrying the fields the rebuild + segmentation read."""
        return {
            "chars": chars,
            "text": "".join(c.get("text") or "" for c in chars),
            "top": min(c["top"] for c in chars),
            "bottom": max(c["bottom"] for c in chars),
            "x0": min(c["x0"] for c in chars),
            "x1": max(c["x1"] for c in chars),
        }
