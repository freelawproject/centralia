"""North Carolina Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class NorthCarolinaCourtOfAppeals(StateAppellate):
    court_id = "ncctapp"
    court_label = "North Carolina Court of Appeals."
    # Like the North Carolina Supreme Court template, ordinary prose is
    # double-spaced while quoted/list material is single-spaced and inset on
    # both margins.  The shared detector also requires a stable multi-line
    # left rail, so a normal first-line paragraph indent is not a blockquote.
    blockquote_by_indent = True
    fold_page_numbers = True

    def extract(self, pdf_path):
        self._ncc_dropped = []
        self._ncc_table_continuation_page = None
        doc = super().extract(pdf_path)
        if self._ncc_dropped:
            seen = set()
            uniq = [
                t for t in self._ncc_dropped if not (t in seen or seen.add(t))
            ]
            doc.dropped = list(doc.dropped) + uniq
        return doc

    def find_footnote_separator(self, page):
        """Use this reporter's fixed two-inch footnote rule.

        The generic appellate scan accepts any wide lower-page rule.  In Ahdi
        that selects the first horizontal border of a two-column assets table
        at y≈605 instead of the actual 144pt footnote rule at y≈664, routing
        the table header and first rows into the footnote zone.
        """
        return self.footnote_sep_fixed_left_rule(page, width=144.0)

    @staticmethod
    def _vertical_rail_xs(page, bbox):
        """Long vertical rule rails inside ``bbox``, de-duplicated by x."""
        x0, top, x1, bottom = bbox
        height = bottom - top
        intervals = {}
        for rect in page.rects:
            if rect.get("width", 0) >= 2 or rect.get("height", 0) < 8:
                continue
            x = round((rect["x0"] + rect["x1"]) / 2, 1)
            if not (x0 - 2 <= x <= x1 + 2):
                continue
            lo, hi = max(top, rect["top"]), min(bottom, rect["bottom"])
            if hi > lo:
                intervals.setdefault(x, []).append((lo, hi))

        rails = []
        for x, spans in intervals.items():
            merged = []
            for lo, hi in sorted(spans):
                if merged and lo <= merged[-1][1] + 1:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
                else:
                    merged.append((lo, hi))
            coverage = sum(hi - lo for lo, hi in merged)
            if coverage >= height * 0.65:
                rails.append(x)
        return sorted(rails)

    @staticmethod
    def _trim_empty_table_tail(rows):
        rows = list(rows or [])
        while rows and not any(str(cell or "").strip() for cell in rows[-1]):
            rows.pop()
        return rows

    def extract_page_tables(self, page):
        """Recover a ruled table that continues at the top of the next page.

        The first page passes the shared strict detector.  The continuation
        page contains blank category rows, so fewer than half of its cells are
        populated and that detector intentionally rejects it.  Continuation
        is proved instead by adjacency to the prior table plus three vertical
        rails spanning the candidate (outer borders and the value divider).
        Explicit rails also prevent underlined category labels from creating
        pdfplumber's four spurious columns.
        """
        tables = super().extract_page_tables(page)
        if tables:
            if any(table["bbox"][3] > page.height * 0.75 for table in tables):
                self._ncc_table_continuation_page = page.page_number + 1
            else:
                self._ncc_table_continuation_page = None
            return tables

        if page.page_number != getattr(self, "_ncc_table_continuation_page", None):
            return []

        recovered = []
        try:
            candidates = page.find_tables()
        except Exception:
            candidates = []
        for candidate in candidates:
            x0, top, x1, bottom = candidate.bbox
            if top > 150 or x1 - x0 < 300:
                continue
            rails = self._vertical_rail_xs(page, candidate.bbox)
            if len(rails) != 3:
                continue
            settings = {
                "vertical_strategy": "explicit",
                "horizontal_strategy": "lines",
                "explicit_vertical_lines": rails,
                "snap_tolerance": 3,
                "join_tolerance": 3,
                "intersection_tolerance": 3,
            }
            try:
                rebuilt = page.find_tables(settings)
            except Exception:
                rebuilt = []
            for table in rebuilt:
                rows = self._trim_empty_table_tail(table.extract())
                if len(rows) < 3 or not rows or max(map(len, rows)) != 2:
                    continue
                recovered.append(
                    {
                        "bbox": table.bbox,
                        "rows": rows,
                        "has_header": False,
                        "continuation": True,
                    }
                )
                if table.bbox[3] > page.height * 0.75:
                    self._ncc_table_continuation_page = page.page_number + 1
                else:
                    self._ncc_table_continuation_page = None
                return recovered
        self._ncc_table_continuation_page = None
        return recovered

    def _maybe_drop_running_header(self, page, lines):
        """Continuation pages carry a small-type centered running head
        ('AHDI V. AHDI' / 'Opinion of the Court', 9.5–10pt vs the 12pt body)
        and a centered '- N -' page number at the foot — margin furniture,
        dropped and surfaced."""
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number <= 1:
            return lines
        kept = []
        for ln in lines:
            size, _font, _bold = self.line_meta(ln)
            t = self.line_plain_text(ln).strip()
            top = ln.get("top", 0)
            if top < 80 and size <= 10.5 and ln.get("x0", 0) > 150:
                if t:
                    getattr(self, "_ncc_dropped", []).append(t)
                continue
            if top > 700 and self._is_page_number_text(t):
                if t:
                    getattr(self, "_ncc_dropped", []).append(t)
                continue
            kept.append(ln)
        return kept
