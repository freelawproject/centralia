"""Michigan Supreme Court.

The byline is a standalone, NON-bold, all-caps abbreviated-title line
('BOLDEN, J.' / 'CAVANAGH, C.J.'), preceded by a 'BEFORE THE ENTIRE BENCH
(except X, J.)' line; a separate writing carries the kind in a parenthetical
('ZAHRA, J. (concurring in the result only).'). Because the byline is not bold,
``require_bold_byline`` is left off and the abbreviated-title base recognizes it
from the all-caps surname + 'J.'/'C.J.' alone. A 'Chief Justice: Justices:'
panel header and the seven-justice roster are title-case, so neither parses as a
byline; the Court of Appeals panel roster carried in the syllabus
('LETICA, P.J., and O'BRIEN and CAMERON, JJ., reversed') is a comma-continuation
the base rejects.

One court-specific fix:

  * The title page sets the caption in a box whose bottom border is a full-width
    rule in the page's lower half. The default footnote-separator finder mistakes
    that caption-box rule for a footnote separator and drops everything beneath
    it — the 'BEFORE THE ENTIRE BENCH' line, the byline, and the opinion body —
    so the opinion parses to nothing. It is instead found by footnote-sized text
    sitting directly under a rule (a real footnote), so the caption box no longer
    chops the opinion.

Two court-specific structures:

  * A clerk's order (a one-page disposition headed 'Order') carries no byline;
    the order text opens with 'On order of the Court, ...' and is authored
    PER CURIAM.

  * Each section's first page (the syllabus title page, the opinion's first page)
    carries a masthead in the upper right — the 'Michigan Supreme Court /
    Lansing, Michigan' banner, the 'Chief Justice: Justices:' panel and the
    seven-justice roster, and a 'FILED <date>' stamp — plus a rotated section tab
    in the left margin ('Syllabus' / 'OPINION' / 'Order'). Both are page
    furniture (no opinion text falls there) and are routed to ``dropped``. The
    Reporter's syllabus that precedes the formal caption ('S T A T E O F
    M I C H I G A N') is captured into the ``syllabus`` field, leaving the
    caption as the headmatter.
"""

from __future__ import annotations

from typing import Optional

from ..models import DocType
from ._abbrevtitle import AbbrevTitleSupreme


class MichiganSupreme(AbbrevTitleSupreme):
    court_id = "mich"
    court_label = "Michigan Supreme Court."

    _ORDER_BODY_START = "on order of the court"
    # Michigan footnote TEXT is body-sized (13pt); only the marker is small
    # (~8.5pt), and a footnote zone often opens with a body-size continuation
    # line of the prior footnote. Scan a wider band for that marker, and require
    # it be clearly smaller than the 10.6pt byline so the title-page caption
    # divider (byline beneath) is not mistaken for a footnote separator.
    _fnsep_band = 60.0
    _fnsep_size_delta = 3.5
    _fnsep_scan_band = True

    def find_footnote_separator(self, page) -> Optional[float]:
        return self._footnote_sep_small_text_below(page)

    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        # A clerk's order is authored PER CURIAM (so author_indices is set), but
        # it is an order, not an opinion — keep the doc_type accurate.
        if getattr(self, "_mich_order", None) is not None:
            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    # ---------------------------------------------------- masthead + syllabus
    def page_lines(self, page):
        """Drop the upper-right masthead (banner + justice roster + filing
        stamp; x0 > 300, top < 210) and the rotated left-margin section tab
        ('Syllabus' / 'OPINION' / 'Order'; x0 < 55, top < 95) — page furniture,
        routed to ``dropped``. The opinion/syllabus body never sits there."""
        out = []
        for l in super().page_lines(page):
            x0, top = l.get("x0", 0), l.get("top", 0)
            if (x0 > 300 and top < 210) or (x0 < 55 and top < 95):
                t = (l.get("text") or "").strip()
                if t:
                    self._mich_furniture.append(t)
                continue
            out.append(l)
        return out

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Page-aware headmatter: the Reporter's syllabus spans several pages, so
        order rows by (page, top, x0) — a y-only sort (the default) would
        interleave the pages and scramble the holdings."""
        lines, notice = [], []
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                size, _font, bold = self.line_meta(line)
                if self.notice_max_size is not None and size <= self.notice_max_size:
                    notice.append(t)
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                lines.append(
                    {
                        "text": t,
                        "page": pno,
                        "x0": round(line["x0"], 1),
                        "top": round(line["top"], 1),
                        "size": size,
                        "bold": bold,
                    }
                )
        items = [(l["page"], l["top"], l["x0"], l["text"]) for l in lines]
        return {
            "court": self.court_label or self.court_id,
            "summary": self._paged_layout_rows(items),
            "headmatter_lines": lines,
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [" ".join(notice)] if notice else [],
        }

    @staticmethod
    def _split_syllabus(doc) -> None:
        """Move the Reporter's syllabus (everything before the formal caption,
        which opens with a letter-spaced 'S T A T E O F M I C H I G A N') out of
        ``summary`` and into the ``syllabus`` field — GROUPED into paragraphs.

        The syllabus is prose (a disclaimer, the case name, the docket line, then
        the holdings), single-spaced with a ~2× gap between paragraphs, so join
        wrapped lines by that gap instead of emitting one row per source line."""
        summary = doc.summary or []
        idx = next(
            (
                i
                for i, r in enumerate(summary)
                if "".join(str(r).split()).upper().startswith("STATEOFMICHIGAN")
            ),
            None,
        )
        if not idx:  # None or 0 — no caption found, or nothing precedes it
            return
        doc.summary = summary[idx:]

        from statistics import median

        # Group the pre-caption lines (geometry from headmatter_lines) into
        # paragraphs: a gap wider than ~1.5× the single-spaced leading, or a
        # page break, opens a new paragraph.
        pre = [
            l
            for l in (doc.headmatter_lines or [])
            if str(l.get("text", "")).strip()
            and "".join(str(l.get("text", "")).split()).upper()
            != "STATEOFMICHIGAN"
        ]
        cap_i = next(
            (
                i
                for i, l in enumerate(pre)
                if "".join(str(l.get("text", "")).split()).upper().startswith(
                    "STATEOFMICHIGAN"
                )
            ),
            len(pre),
        )
        pre = pre[:cap_i]
        if not pre:
            doc.syllabus = [str(r).strip() for r in summary[:idx] if str(r).strip()]
            return
        gaps = [
            b["top"] - a["top"]
            for a, b in zip(pre, pre[1:])
            if a.get("page") == b.get("page") and b["top"] - a["top"] > 0
        ]
        med = median(gaps) if gaps else 14.0
        paras = [[pre[0]]]
        for prev, cur in zip(pre, pre[1:]):
            same_page = prev.get("page") == cur.get("page")
            gap = cur["top"] - prev["top"]
            if not same_page or gap > med * 1.5 or gap < 0:
                paras.append([cur])
            else:
                paras[-1].append(cur)
        syl = [" ".join(l["text"] for l in grp).strip() for grp in paras]
        doc.syllabus = [s for s in syl if s]

    # ------------------------------------------------------- per-curiam orders
    def extract(self, pdf_path):
        self._mich_order = None
        self._mich_furniture = []
        doc = super().extract(pdf_path)
        if self._mich_furniture:
            doc.dropped = list(doc.dropped) + self._mich_furniture
        self._split_syllabus(doc)
        return doc

    def find_authors(self, all_segments) -> list:
        self._mich_order = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            if self.line_plain_text(seg[0]).strip().lower().startswith(
                self._ORDER_BODY_START
            ):
                self._mich_order = i
                return [i]
        return []

    def split_author_line(self, line):
        if getattr(self, "_mich_order", None) is not None:
            return "", [line]  # 'On order of the Court ...' opens the body
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        if getattr(self, "_mich_order", None) == op_start:
            op.author = "PER CURIAM"
            op.type = "majority"
        return op
