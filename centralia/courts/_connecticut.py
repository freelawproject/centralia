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
from statistics import median

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
        # One judge 'joins', two or more 'join' — a plural roster ('with whom
        # McDONALD and ECKER, Js., join') is the common shape for a separate
        # writing, so matching only the singular missed those outright.
        joined = {t.strip(".,;:") for t in low.split()} & {"join", "joins", "joined"}
        if ", with whom" in low and joined:
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

    def find_authors(self, all_segments) -> list:
        """A joinder byline wraps across two lines —

            D'AURIA, J., with whom McDONALD and ECKER,
            Js., join, dissenting in part. In State v. Purcell, ...

        so the first line carries no verb and parses as nothing on its own. A
        separate writing published as its own file then yields no opinion at
        all, taking its footnotes with it. Retry those as a joined pair, gated
        on the 'with whom' shape so ordinary bylines are left alone."""
        found = list(super().find_authors(all_segments))
        for i, (_p, seg, _kind) in enumerate(all_segments):
            # No kind filter: Connecticut's centered measure classifies most
            # body segments as 'notice', bylines included.
            if i in found or len(seg) < 2:
                continue
            first = self.line_plain_text(seg[0]).strip()
            if ", with whom" not in first.lower():
                continue
            pair = f"{first} {self.line_plain_text(seg[1]).strip()}"
            if self.parse_author_line(pair):
                found.append(i)
        return sorted(found)

    def find_footnote_separator(self, page):
        """Connecticut strokes its rules as vector lines rather than filled
        rects. The shared finder scans only ``page.rects`` — which is empty on
        every page here — so it finds no separator and the footnotes are lost
        wholesale, body text and all.

        Same predicate as the base (thin, >=100pt wide, at the body margin,
        footnote-sized text below), applied to the strokes — but bounded by the
        head band rather than the base's half-page cutoff. A long footnote
        pushes its separator well up the sheet (alers_v._bemer draws it at
        385pt on a 792pt page, above the base's 435pt cutoff, and the footnote
        it opens was silently lost). The running-head rules at 163.8/180.2 read
        as footnote separators on the 'small text below' test alone, so they
        still have to be excluded by position — the head band does that, and
        nothing but head furniture ever sits above 185pt here."""
        sep = super().find_footnote_separator(page)
        if sep is not None:
            return sep
        cutoff = 185.0
        x0_max = self.body_baseline_x0 + 4
        tops = [
            l["top"]
            for l in page.lines
            if abs(l.get("height", 0)) < 2
            and (l["x1"] - l["x0"]) >= 100
            and l["x0"] <= x0_max
            and l["top"] > cutoff
            and self._rule_over_footnotes(page, l["top"])
        ]
        return min(tops) if tops else None

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
        # Drop the running head. A slip opinion carries one line (the short
        # 'X v. Y' case name); the bound Connecticut Reports carry two — a
        # volume/page/date band ('354 Conn. 151 FEBRUARY, 2026 153') above the
        # case name. Both sit above the body and are set smaller than it, so
        # the head is the run of undersized lines at the page top.
        #
        # Left in, that band is not just noise: it lands mid-sentence between
        # the page's first line and the paragraph continuing from the previous
        # page, so every paragraph spanning a page break is split in three.
        # Anchored on position alone. Font size cannot make this call: the
        # syllabus is itself set at 8pt, so on syllabus pages the 8pt head is
        # not "smaller than the body" and survives. Nor can wording: an
        # 'In re Hunter T.' head carries no ' v. '. But the reporter's measure
        # is rigid — across both corpora the only lines above 185pt on a
        # continuation page are head furniture (the volume/date band at 150.5
        # and the case name at ~169, wrapping to a second row on long names),
        # and the body never opens above 187.7.
        if page.page_number > 1:
            out = [l for l in out if l.get("top", 0) >= 185]
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
