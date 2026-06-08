"""Shared layout for the Connecticut courts (conn / connappct).

Both print the same front matter, so the handling lives here once (the per-court
files stay thin — they only pick the right byline base):

  * a publication notice ('The "officially released" date ... may not be
    reproduced ...') bracketed by rows of asterisks — administrative furniture,
    routed to ``dropped``;
  * a running header (the short case name, repeated at the top of every page) —
    page furniture, dropped (the audit tolerates it as a repeated margin line);
  * page-aware headmatter so a multi-page syllabus keeps document order (the
    long syllabus spans several pages; a y-only sort interleaves them);
  * an official 'Syllabus' that follows the caption/panel and precedes the
    opinion byline — captured into the ``syllabus`` field (expressly not part of
    the opinion), leaving the caption/panel as the headmatter.
"""

from __future__ import annotations

import re

from ._statesupreme import is_caps_name

_TAG = re.compile(r"<[^>]+>")


class ConnecticutStyle:
    # The Connecticut Reports set the body at a wide left margin (x0≈174) with a
    # small ~10pt first-line indent (≈184). Without this the default threshold
    # (72+28=100) treats every body line as a new paragraph, so nothing groups.
    body_baseline_x0 = 174.0
    para_indent_min = 6.0

    # Joinder byline for a separate writing, often its own file: 'MULLINS, C. J.,
    # with whom D'AURIA, J., joins, concurring in part and dissenting in part.'
    # The kind clause wraps to the next line, so the base treats the comma after
    # the title as a roster and rejects it — recognize it here.
    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        low = text.lower()
        if ", with whom" in low and "joins" in low:
            name = text.split(",", 1)[0].strip()
            if is_caps_name(name):
                after = text.split(",", 1)[1].lstrip()
                title = (
                    "Chief Justice"
                    if after[:4] in ("C.J.", "C. J")
                    else (
                        "Presiding Justice"
                        if after[:4] in ("P.J.", "P. J")
                        else "Justice"
                    )
                )
                kind = (
                    "concurring and dissenting"
                    if "concur" in low and "dissent" in low
                    else (
                        "concurring"
                        if "concur" in low
                        else "dissenting" if "dissent" in low else None
                    )
                )
                return name, title, kind
        return None

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        # The joinder byline's kind clause wraps onto the first body line; read
        # the opinion type off it.
        if "with whom" in op.author.lower() and op.type == "majority" and op.blocks:
            head = _TAG.sub("", op.blocks[0].text).lower()[:70]
            if "concur" in head and "dissent" in head:
                op.type = "concurring-in-part-and-dissenting-in-part"
            elif "dissent" in head:
                op.type = "dissent"
            elif "concur" in head:
                op.type = "concurrence"
        return op

    def extract(self, pdf_path: str):
        self._conn_notice = []
        doc = super().extract(pdf_path)
        if self._conn_notice:
            doc.dropped = list(doc.dropped) + self._conn_notice
        self._split_syllabus(doc)
        return doc

    def page_lines(self, page):
        """Drop the asterisk-bracketed 'officially released' notice (-> dropped)
        and the repeated short-case-name running header at the page top."""
        lines = super().page_lines(page)
        out, captured, in_notice = [], [], False
        for l in lines:
            t = (l.get("text") or "").strip()
            if t and len(t) >= 10 and set(t) == {"*"}:
                in_notice = not in_notice  # asterisk delimiter row
                continue
            if in_notice:
                captured.append(t)
            else:
                out.append(l)
        if captured:
            self._conn_notice.append(" ".join(captured))
        # Drop the running header: the topmost line, a short 'X v. Y' case name.
        if out:
            top_line = min(out, key=lambda l: l.get("top", 0))
            t = (top_line.get("text") or "").strip()
            if " v. " in t and len(t) <= 80:
                out = [l for l in out if l is not top_line]
        return out

    # ----------------------------------------------------- page-aware headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        rows = []  # (page, top, x0, text)
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                rows.append((pno, round(line["top"], 1), round(line["x0"], 1), t))
        return {
            "court": self.court_label or self.court_id,
            "summary": self._paged_layout_rows(rows),  # shared (StateSupreme)
            "headmatter_lines": [],
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [],
        }

    @staticmethod
    def _split_syllabus(doc) -> None:
        """Move the 'Syllabus' block (from the 'Syllabus' heading to the end of
        the headmatter) out of ``summary`` into the ``syllabus`` field."""
        summary = doc.summary or []
        idx = next(
            (
                i
                for i, row in enumerate(summary)
                if str(row).strip().lower() == "syllabus"
            ),
            None,
        )
        if idx is None:
            return
        doc.syllabus = [str(r).strip() for r in summary[idx:] if str(r).strip()]
        doc.summary = summary[:idx]
