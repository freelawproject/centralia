"""The Business Court of Texas ('texbizct').

District-court model: one ruling by one judge. Page 1 carries the clerk's
e-filing stamp in the top-right corner ('FILED IN / BUSINESS COURT OF
TEXAS / <clerk>, CLERK / ENTERED / <date>' — dropped and recorded), the
neutral citation ('2026 Tex. Bus. 23'), the banner, a '§'-railed caption,
and a '══════' boxed doc-title heading ('MEMORANDUM OPINION AND ORDER
DENYING ...' — matched by prefix since the suffix is case-specific). The
judge signs an all-caps name over 'Judge of the Texas Business Court'.
"""

from __future__ import annotations

from ._district import DistrictBase


class TexasBusinessCourt(DistrictBase):
    court_id = "texbizct"
    court_label = "The Business Court of Texas."
    # The neutral cite ('2026 Tex. Bus. 23') can sit above the default top
    # margin, merged with a stamp row — the top band is handled here.
    margin_top = 2

    # A crowded footnote zone can contain eight or more consecutive,
    # superscript labels at x≈72.  DistrictBase's no-rule pleading-paper
    # fallback reads that stack as line numbers and strips labels 17–28.
    # Business Court slips never use pleading paper, so disable both gutter
    # detectors for this court.
    @staticmethod
    def _pleading_gutter_by_numbers(page):
        return None

    @staticmethod
    def _pleading_gutter_x(page):
        return None

    def extract(self, pdf_path):
        self._stamp_dropped = []
        doc = super().extract(pdf_path)
        extra = list(dict.fromkeys(self._stamp_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def find_authors(self, all_segments):
        """Start after the final front-matter document title.

        A syllabus edition repeats the ruled caption/title on the next page;
        therefore the last front-matter ``OPINION [AND ORDER]`` title is the
        operative one. The title itself remains between its two rules in
        headmatter, and the following section/prose begins the opinion.
        """
        super().find_authors(all_segments)  # populate DistrictBase's signer
        titles = []
        for i, (page, seg, _kind) in enumerate(all_segments):
            if page <= 2 and seg and self._is_heading(seg[0]):
                titles.append(i)
        self._texbiz_start_line = None
        if not titles:
            return []
        title_i = titles[-1]
        for i in range(title_i + 1, len(all_segments)):
            seg = all_segments[i][1]
            text = self.line_plain_text(seg[0]).strip() if seg else ""
            double_rule = bool(text) and all(ch in "═=" for ch in text)
            if not seg or self.is_separator_line(seg[0]) or double_rule:
                continue
            self._texbiz_start_line = seg[0]
            return [i]
        return []

    def split_author_line(self, line):
        if line is getattr(self, "_texbiz_start_line", None):
            return getattr(self, "_district_author", None) or "", [line]
        return super().split_author_line(line)

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Separate the uncommon expressly labeled syllabus from headmatter."""
        syllabus, kept = [], []
        syllabus_page = None
        for seg in headmatter_segs:
            text = " ".join(
                self.line_plain_text(line).strip() for line in seg
            ).strip()
            chars = seg[0].get("chars") if seg else []
            page = (
                (chars or [{}])[0].get("page_number")
                if seg
                else None
            ) or (seg[0].get("page_number") if seg else None)
            if text.lower().startswith("syllabus"):
                syllabus_page = page
            if syllabus_page is not None and page == syllabus_page:
                syllabus.append(self.paragraph_text(seg))
            else:
                kept.append(seg)
        result = super().extract_headmatter(kept, page1_rules)
        if syllabus:
            result["syllabus"] = syllabus
        return result

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        # Some Business Court templates omit the drawn two-inch rule.  The
        # footnote zone still has an unambiguous geometric opening: a raised
        # numeric label at the left text margin, followed by 10pt text below a
        # 13/14pt body.  Use that first label as the boundary.  If everything
        # above it is already footnote-sized, this is a continuation page and
        # the entire text column belongs to the carried footnote.
        lines = page.extract_text_lines()
        labelled = [
            (ln, self.detect_footnote_label(ln))
            for ln in lines
            if ln.get("top", 0) < self.margin_bottom
        ]
        labelled = [(ln, lab) for ln, lab in labelled if lab and lab.isdigit()]
        if not labelled:
            return None
        first = min(labelled, key=lambda pair: pair[0]["top"])[0]
        above_sizes = []
        for ln in lines:
            if not (self.margin_top <= ln.get("top", 0) < first["top"] - 2):
                continue
            chars = ln.get("chars") or []
            if chars:
                above_sizes.append(max(c.get("size", 0) for c in chars))
        if above_sizes and max(above_sizes) <= 10.6:
            return float(self.margin_top)
        return max(float(self.margin_top), first["top"] - 2)

    def page_lines(self, page):
        lines = super().page_lines(page)
        # The e-filing system appends its own certificate-of-service sheet
        # after the signed order.  It is administrative transmission
        # furniture, not part of the judicial writing.  Identify the sheet by
        # its invariant opening sentence, then retain every source row in the
        # explicit Removed bucket for coverage/review.
        plain = [self.line_plain_text(ln).strip() for ln in lines]
        if any(
            t.lower().startswith(
                "this automated certificate of service was created by the efiling system"
            )
            for t in plain[:4]
        ):
            if getattr(self, "_stamp_dropped", None) is None:
                self._stamp_dropped = []
            self._stamp_dropped.extend(t for t in plain if t)
            return []
        if page.page_number != 1:
            return lines
        if getattr(self, "_stamp_dropped", None) is None:
            self._stamp_dropped = []
        kept = []
        for ln in lines:
            if ln["top"] >= 65:
                kept.append(ln)
                continue
            # Top band: the e-filing stamp owns the right half; the neutral
            # cite (left/center runs) stays. A row can merge both.
            keep_runs, drop_runs = [], []
            for run in self._caption_char_runs(ln):
                (drop_runs if run[0]["x0"] > page.width * 0.55 else keep_runs).append(
                    run
                )
            for run in drop_runs:
                txt = self.line_plain_text({"chars": run}).strip()
                if txt:
                    self._stamp_dropped.append(txt)
            if keep_runs:
                chars = [c for r in keep_runs for c in r]
                ln = dict(ln)
                ln["chars"] = chars
                ln["x0"] = min(c["x0"] for c in chars)
                ln["x1"] = max(c["x1"] for c in chars)
                kept.append(ln)
        return kept

    def _is_heading(self, line) -> bool:
        if super()._is_heading(line):
            return True
        low = self.line_plain_text(line).strip().lower()
        return low.startswith(
            ("memorandum opinion and order", "opinion and order", "order denying",
             "order granting")
        )

    def _signature_author(self, all_segments):
        # 'BRIAN STAGNER' over 'Judge of the Texas Business Court,'
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].lower().startswith("judge of the texas business court"):
                name = lines[i - 1]
                if name and not name.lower().startswith(("signed", "it is so")):
                    return f"{name.title() if name.isupper() else name}, Judge"
        return super()._signature_author(all_segments)
