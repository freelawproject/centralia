"""Office of Legal Counsel, U.S. Department of Justice.

Small slip pages (423x657). '(Slip Opinion)' header, the opinion title,
a headnote summary (all headmatter), then 'MEMORANDUM OPINION FOR THE
GENERAL COUNSEL …' opens the single opinion. Signed at the end with the
author's name over 'Deputy/Acting Assistant Attorney General / Office of
Legal Counsel' — lifted to the Signature section and used as the author.
"""

from __future__ import annotations

from ..base import BaseExtractor
from .generic import GenericExtractor


class OfficeOfLegalCounsel(GenericExtractor):
    court_id = "olc"
    court_label = "Office of Legal Counsel, U.S. Department of Justice."

    # small page stock (423x657): the page number sits at ~595
    margin_top = 30
    margin_bottom = 588
    # OLC body is single-spaced small type — its tight line pitch reads as
    # 'notice' to the classifier; keep those segments in the body
    drop_notice_in_body = False

    def find_footnote_separator(self, page):
        """Fall through to base's measured separator chain.

        OLC prints on a 423pt slip sheet and draws its footnote rule ~72pt wide
        at the body rail (x0=48.3, the text column's own left edge).  That is a
        proportionally NORMAL separator — 17% of the sheet, the same share a
        100pt rule takes on a letter page — but ``GenericExtractor`` screens
        candidates against a flat 100pt width, which no OLC rule can clear.  The
        separator therefore read as None on every page carrying a note, and the
        whole footnote zone was delivered as body prose in 18 of 20 documents.

        ``base.find_footnote_separator`` measures the floor from the page it is
        given (``footnote_sep_min_width`` -> ~68pt here) and still demands the
        rule be corroborated by smaller text below it (OLC sets 11pt body over
        9pt notes), so nothing widens except the sheet-relative floor.  Generic's
        scan runs first and is left intact — it reaches a little further right
        (x0 < 100) than base's body-rail window.
        """
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        return BaseExtractor.find_footnote_separator(self, page)

    def extract_page_tables(self, page):
        """Rebuild OLC's four-column immigration-status comparison table.

        The PDF draws nested cell rectangles.  pdfplumber consequently emits
        twelve sparse pseudo-columns and loses the text of several rows.  The
        outer first-column cells still give reliable row boundaries; cluster
        the four outer column edges and crop each logical cell once.
        """
        tables = super().extract_page_tables(page)
        broad = next(
            (
                table
                for table in tables
                if len(table.get("rows") or []) >= 8
                and max((len(row) for row in table["rows"]), default=0) >= 8
            ),
            None,
        )
        if broad is None or "PRWORA Qualified" not in (page.extract_text() or ""):
            return tables

        bx0, btop, bx1, bbottom = broad["bbox"]
        first_cells = sorted(
            (
                rect
                for rect in page.rects
                if abs(rect["x0"] - bx0) <= 2
                and 50 <= rect["x1"] - rect["x0"] <= 90
                and rect["height"] >= 8
                and btop - 2 <= rect["top"] < bbottom
            ),
            key=lambda rect: rect["top"],
        )
        row_tops = []
        for rect in first_cells:
            if not row_tops or abs(rect["top"] - row_tops[-1]) > 2:
                row_tops.append(rect["top"])
        if len(row_tops) < 4:
            return tables
        row_edges = row_tops + [max(rect["bottom"] for rect in first_cells)]

        raw_edges = sorted(
            rect["x0"]
            for rect in page.rects
            if abs(rect["top"] - btop) <= 2 and rect["height"] >= 8
        )
        col_edges = []
        for value in raw_edges:
            if not col_edges or value - col_edges[-1] > 8:
                col_edges.append(value)
        col_edges = [value for value in col_edges if bx0 - 2 <= value < bx1 - 2]
        col_edges.append(bx1)
        if len(col_edges) != 5:
            return tables

        rows = []
        for top, bottom in zip(row_edges, row_edges[1:]):
            row = []
            for left, right in zip(col_edges, col_edges[1:]):
                cell = page.crop((left + 1, top + 1, right - 1, bottom - 1))
                text = cell.extract_text(x_tolerance=2, y_tolerance=3) or ""
                row.append(" ".join(text.splitlines()).strip())
            rows.append(row)
        rebuilt = dict(broad)
        rebuilt["rows"] = rows
        return [rebuilt if table is broad else table for table in tables]

    def find_authors(self, all_segments) -> list:
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            t = self.line_plain_text(seg[0]).strip().upper()
            if t.startswith(("MEMORANDUM OPINION", "MEMORANDUM FOR", "LETTER OPINION")):
                return [i]
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        return (getattr(self, "_olc_author", None) or ""), [line]

    def extract(self, pdf_path: str):
        self._olc_author = None
        doc = super().extract(pdf_path)
        # signature: NAME over '… Assistant Attorney General' (+ office)
        if doc.opinions:
            op = doc.opinions[-1]
            blocks = op.blocks
            for k in range(len(blocks) - 1, max(-1, len(blocks) - 5), -1):
                t = self._plain(blocks[k].text).strip()
                if t.lower().endswith("attorney general") and k > 0:
                    name = self._plain(blocks[k - 1].text).strip()
                    if 2 <= len(name.split()) <= 5 and name == name.upper():
                        take = len(blocks) - (k - 1)
                        doc.signature = [str(b.text) for b in blocks[k - 1 :]]
                        op.blocks = blocks[: k - 1]
                        op.author = name.title()
                        break
        return doc

    @staticmethod
    def _plain(text: str) -> str:
        out, i, s = [], 0, str(text)
        while True:
            j = s.find("<", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            k = s.find(">", j)
            if k < 0:
                break
            i = k + 1
        return "".join(out)
