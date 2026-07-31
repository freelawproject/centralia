"""California Attorney General opinions ('calag') — not a court.

Page-1 layout: a letterhead (publication notice, 'OFFICE OF THE ATTORNEY
GENERAL / State of California', the signing officer's name over their
title), a short text divider, and a colon-railed caption table (OPINION /
of / officer :: docket number, date) — all above a full-width horizontal
rule. The opinion body follows the rule. There is no byline anywhere; the
author is the officer named in the letterhead ('ROB BONTA, Attorney
General', or an acting deputy: 'FRANCESCA R. GESSNER, Acting Chief Deputy
Attorney General').

Everything above the rule is headmatter, preserved as a styled facsimile
(exact position, size, and weight — the '__facsimile__' summary sentinel);
the plain layout rows still follow it for the audit and database. A
superscript footnote reference in the headmatter (the acting officer's
title footnote) moves its footnote out of the opinion into the headmatter.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme


class CaliforniaAttorneyGeneral(StateSupreme):
    court_id = "calag"
    court_label = "Office of the Attorney General of California."
    facsimile_headmatter = True  # letterhead + ':'-railed caption table

    def segment_lines(self, lines, page_width) -> list:
        """Split a mixed-margin tight run when an indented quotation begins.
        Several AG opinions set a quote at x≈101, only 29 points right of the
        body margin, so spacing alone merges it with the preceding paragraph."""
        segments = super().segment_lines(lines, page_width)
        out = []
        deep_x = self.body_baseline_x0 + 25
        for seg in segments:
            cuts = []
            start = None
            for i, line in enumerate(seg):
                deep = line["x0"] >= deep_x
                if (
                    deep
                    and start is not None
                    and i > 0
                    and line["top"] - seg[i - 1]["top"] > self.gap_single_max
                ):
                    if i - start >= 2 and start > 0:
                        cuts.append((start, i))
                    start = i
                if deep and start is None:
                    start = i
                if (not deep or i == len(seg) - 1) and start is not None:
                    end = i if not deep else i + 1
                    if end - start >= 2 and start > 0:
                        cuts.append((start, end))
                    start = None
            if not cuts:
                out.append(seg)
                continue
            cursor = 0
            for start, end in cuts:
                if start > cursor:
                    out.append(seg[cursor:start])
                out.append(seg[start:end])
                cursor = end
            if cursor < len(seg):
                out.append(seg[cursor:])
        return out

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        # Wrapped lines of an indented statutory bullet can be tight enough
        # to enter the generic ``notice`` band.  Their shared deep left edge
        # is decisive: they are quote continuation, not furniture.
        if kind == "notice" and seg:
            if min(line["x0"] for line in seg) >= self.body_baseline_x0 + 25:
                return "blockquote"
        return kind

    def classify_paragraph(self, lines) -> str:
        """AG opinions indent quoted statutory lists instead of surrounding
        them with quotation marks.  A one-line item is a ``single`` segment,
        so the base classifier needs this narrow geometry-plus-marker check."""
        if lines:
            first = self.line_plain_text(lines[0]).lstrip()
            if lines[0]["x0"] >= self.body_baseline_x0 + 35 and (
                first.startswith("•")
                or first.startswith("(1)")
                or first.startswith("(2)")
                or first.startswith("(3)")
            ):
                return "blockquote"
        return super().classify_paragraph(lines)

    def split_body_paragraphs(self, seg) -> list:
        """Keep an indented bullet and its wrapped continuation together,
        while starting a new block at the next bullet/factor."""
        if any(
            self.line_plain_text(line).lstrip().startswith(("•", "(1)", "(2)", "(3)"))
            for line in seg
        ):
            groups = []
            current = []
            for line in seg:
                text = self.line_plain_text(line).lstrip()
                starts_item = text.startswith(("•", "(1)", "(2)", "(3)"))
                if starts_item and current:
                    groups.append(current)
                    current = []
                current.append(line)
            if current:
                groups.append(current)
            return groups
        return super().split_body_paragraphs(seg)

    def split_blockquote_paragraphs(self, seg) -> list:
        if any(
            self.line_plain_text(line).lstrip().startswith(("•", "(1)", "(2)", "(3)"))
            for line in seg
        ):
            groups = []
            current = []
            for line in seg:
                text = self.line_plain_text(line).lstrip()
                if text.startswith(("•", "(1)", "(2)", "(3)")) and current:
                    groups.append(current)
                    current = []
                current.append(line)
            if current:
                groups.append(current)
            return groups
        return super().split_blockquote_paragraphs(seg)

    def extract(self, pdf_path):
        self._split_y = None
        self._ag_author = ""
        self._hm_super_labels = set()
        doc = super().extract(pdf_path)
        # A footnote referenced from the headmatter (superscript on the
        # caption) belongs to the headmatter, not the opinion that owns the
        # rest of page 1.
        if self._hm_super_labels and doc.opinions:
            op = doc.opinions[0]
            moved = [f for f in op.footnotes if f.label in self._hm_super_labels]
            if moved:
                op.footnotes = [
                    f for f in op.footnotes if f.label not in self._hm_super_labels
                ]
                doc.headmatter_footnotes = list(doc.headmatter_footnotes) + moved
        return doc

    @staticmethod
    def _boundary_y(page):
        """The headmatter/opinion boundary: the first thin rule (possibly
        drawn as several abutting rects at one y) spanning most of the page
        width."""
        by_y: dict = {}
        for r in page.rects:
            if r["height"] < 2:
                by_y.setdefault(round(r["top"]), []).append(r)
        for y, rs in sorted(by_y.items()):
            span = max(r["x1"] for r in rs) - min(r["x0"] for r in rs)
            if span >= page.width * 0.6:
                return float(y)
        return None

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is None and page.page_number > 1:
            # Long footnotes can occupy most of a page in Attorney General
            # opinions. Their separator then sits well above the generic
            # bottom-page footnote band (page 10 of 23-1001: y≈236), but its
            # geometry remains distinctive: a thin 144pt rule beginning at the
            # 72pt text margin. Use that printed rule directly instead of a
            # vertical-position cutoff.
            rules = [
                rect
                for rect in page.rects
                if rect["height"] < 2
                and page.width * 0.18 <= rect["width"] <= page.width * 0.30
                and abs(rect["x0"] - 72) <= 8
                and 100 < rect["top"] < page.height - 60
            ]
            if rules:
                return min(rect["top"] for rect in rules)
        if sep is None or page.page_number != 1:
            return sep
        # A low-sitting boundary rule (one file draws it at y=430, past the
        # bottom-half cutoff) must not be mistaken for a footnote separator —
        # that would swallow the whole opinion body as a footnote.
        b = self._boundary_y(page)
        if b is not None and abs(sep - b) <= 2:
            return None
        return sep

    def page_lines(self, page):
        lines = super().page_lines(page)
        if page.page_number == 1:
            self._split_y = self._boundary_y(page)
        # Centered bottom folios otherwise become the last line of a footnote
        # whenever that page's notes extend to the bottom margin.
        return [
            line
            for line in lines
            if not (
                (
                    (line.get("text") or "").strip() == str(page.page_number)
                    and line["top"] > page.height - 80
                    and abs((line["x0"] + line["x1"]) / 2 - page.width / 2) < 15
                )
                or (line.get("text") or "").strip()
                in {"(continued…)", "(continued...)"}
            )
        ]

    # ------------------------------------------------------------- authors
    def find_authors(self, all_segments) -> list:
        y = getattr(self, "_split_y", None)
        start = None
        for i, (pno, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            if pno > 1 or (y is not None and seg[0]["top"] > y):
                start = i
                break
        if start is None:
            return []
        self._ag_author = self._letterhead_author(all_segments[:start])
        self._hm_super_labels = self._superscript_labels(
            seg for _, seg, _ in all_segments[:start]
        )
        return [start]

    def _letterhead_author(self, headmatter_segments) -> str:
        """The signing officer: an ALL-CAPS name directly above a mixed-case
        title ending 'Attorney General'. (The 'OFFICE OF THE ATTORNEY
        GENERAL' banner is all-caps and never matches as a title.)"""
        lines = [l for _pno, seg, _k in headmatter_segments for l in seg]
        for a, b in zip(lines, lines[1:]):
            name = self.line_plain_text(a).strip()
            title = self.line_plain_text(b).strip().rstrip(":").strip()
            while title and title[-1].isdigit():  # superscript fn ref
                title = title[:-1]
            if (
                title.endswith("Attorney General")
                and name
                and name == name.upper()
                and any(c.isalpha() for c in name)
            ):
                return f"{name}, {title}"
        return ""

    def split_author_line(self, line):
        # The opinion-start line is body text, not a byline; the author is
        # the officer from the letterhead.
        return getattr(self, "_ag_author", "") or "", [line]

    def _superscript_labels(self, segs) -> set:
        """Labels of superscript digit references — a digit run set well
        below the line's dominant font size."""
        labels = set()
        for seg in segs:
            for line in seg:
                chars = line.get("chars") or []
                sizes = [
                    round(c.get("size", 0), 1)
                    for c in chars
                    if (c.get("text") or "").strip()
                ]
                if not sizes:
                    continue
                dom = max(set(sizes), key=sizes.count)
                run = ""
                for c in chars:
                    t = c.get("text") or ""
                    if t.isdigit() and c.get("size", 0) < dom * 0.8:
                        run += t
                    elif run:
                        labels.add(run)
                        run = ""
                if run:
                    labels.add(run)
        return labels
