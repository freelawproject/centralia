"""Connecticut Appellate Court.

Intermediate appellate court. Author byline at the opinion start ('NAME, J.' /
'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and
drops the trial-judge / panel-roster caption lines. The Connecticut front matter
(the 'officially released' notice and the 'Syllabus') is handled by the shared
``ConnecticutStyle`` — the same as the Supreme Court.
"""

from __future__ import annotations

from collections import Counter

from ._appellate import StateAppellate
from ._connecticut import ConnecticutStyle


class ConnecticutAppellateCourt(ConnecticutStyle, StateAppellate):
    court_id = "connappct"
    court_label = "Connecticut Appellate Court."

    # ------------------------------------------------------- styled syllabus
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Measure the syllabus before the headmatter is flattened.

        ``ConnecticutStyle`` lays the headmatter out as whitespace-positioned
        plain rows, which is right for the caption but loses the syllabus: the
        blank rows that mark its paragraph breaks are not carried through, so by
        the time ``_split_syllabus`` sees it there is no way to tell one held
        point from the next. Take the measurement here, off the lines
        themselves, and keep the flattened caption exactly as it was."""
        self._conn_syllabus = self._conn_syllabus_rows(headmatter_segs)
        return super().extract_headmatter(headmatter_segs, page1_rules)

    def _conn_syllabus_rows(self, headmatter_segs) -> list:
        """The front matter from the 'Syllabus' heading on, as styled rows.

        The Connecticut Appellate Reports set this stretch as five distinct
        things — the italic 'Syllabus' and 'Procedural History' heads, the 8pt
        syllabus proper (one paragraph per held point), the centered
        argued/released line, the 11pt procedural history, and the italic
        counsel block — and it has to come out that way rather than as a dump of
        source lines.

        Grouped on the page's own measure, no wording involved:

          * a paragraph breaks where the leading exceeds the type size by more
            than a third (the reporter opens ~1.6 lines between paragraphs and
            sets them solid within one), or where a line is indented off the
            block's left margin (the 11pt paragraphs take a first-line indent);
          * a page break does NOT break a paragraph — the syllabus runs over
            onto the next sheet and resumes flush at the margin, so only the
            indent test applies there;
          * a group of one line that is centered and falls short of the measure
            is a heading or the argued/released line, and keeps its centering;
            anything else is a paragraph, its wrapped lines joined.

        Relative type size follows the same convention as the styled
        headmatter builder (each row against the block's modal size), so the
        syllabus keeps reading smaller than the procedural history exactly as
        the reporter sets it."""
        rows = []
        for seg in headmatter_segs:
            for line in seg:
                if not (line.get("text") or "").strip():
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                rows.append((pno, round(line["top"], 1), line))
        rows.sort(key=lambda r: (r[0], r[1]))
        start = next(
            (
                i
                for i, (_p, _t, ln) in enumerate(rows)
                if self.line_plain_text(ln).strip().lower() == "syllabus"
            ),
            None,
        )
        if start is None:
            return []
        block = rows[start:]
        if not block:
            return []

        left = min(round(ln["x0"], 1) for _p, _t, ln in block)
        measure = max(round(ln["x1"], 1) for _p, _t, ln in block)
        pw = getattr(self, "_page1_width", 612.0) or 612.0

        # The leading the reporter sets a size at is measured, not assumed — it
        # runs 9.9pt on 8pt type in one volume and 11.1pt in another, so any
        # fixed multiple of the type size lands on the wrong side of one of
        # them and either fuses every paragraph or splits every line.
        gaps: dict = {}
        for (pa, ta, la), (pb, tb, lb) in zip(block, block[1:]):
            sa = round(self.line_meta(la)[0] or 11)
            if pa == pb and sa == round(self.line_meta(lb)[0] or 11):
                gaps.setdefault(sa, []).append(round(tb - ta, 1))
        pitch = {
            size: Counter(g).most_common(1)[0][0] for size, g in gaps.items() if g
        }

        groups: list = []
        prev = None
        for pno, top, line in block:
            size = self.line_meta(line)[0] or 11.0
            solid = pitch.get(round(size))
            limit = solid * 1.3 if solid else size * 1.35
            indented = round(line["x0"], 1) > left + 3
            if prev is None:
                new = True
            elif prev[0] != pno:
                new = indented  # a page break alone never ends a paragraph
            else:
                new = indented or (top - prev[1]) > limit
            if new:
                groups.append([])
            groups[-1].append(line)
            prev = (pno, top)

        base = (
            Counter(
                round(self.line_meta(ln)[0] or 11) for g in groups for ln in g
            ).most_common(1)[0][0]
            or 11
        )
        out: list = []
        for g in groups:
            if out:
                out.append("")  # the real gap the reporter opens between them
            size = self.line_meta(g[0])[0] or float(base)
            align = self.line_alignment(g[0], pw)
            single_short = (
                len(g) == 1
                and align == "C"
                and round(g[0]["x1"], 1) < measure - 20
            )
            html = " ".join(
                self.line_inline_text(ln).strip() for ln in g
            ).strip()
            # An italic run that wraps ('Brendon P. / Levesque') comes back as
            # two adjacent italic spans; rejoin them so the counsel block reads
            # as the one italic name it is.
            for tag in ("em", "strong"):
                html = html.replace(f"</{tag}> <{tag}>", " ")
            out.append(
                {
                    "__hm__": True,
                    "html": html,
                    "rel": round(size / base, 3),
                    "align": "C" if single_short else "L",
                }
            )
        return out

    def _split_syllabus(self, doc) -> None:
        """Move the syllabus out of ``summary`` into the ``syllabus`` field,
        using the styled rows measured in ``extract_headmatter``. Falls back to
        the shared flat split if the measurement found nothing."""
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
        styled = getattr(self, "_conn_syllabus", None)
        doc.syllabus = styled or [
            str(r).strip() for r in summary[idx:] if str(r).strip()
        ]
        doc.summary = summary[:idx]

    def _sweep_residual(self, doc, source_pages) -> None:
        """``ConnecticutStyle`` collects the asterisk-bracketed publication
        notice while reading the pages and appends it to ``dropped`` *after*
        ``extract()`` returns — but the completeness sweep runs inside that
        call, so the notice was still unplaced when the sweep looked (24 lines
        per file, every file). Flush it before the sweep instead."""
        notice = getattr(self, "_conn_notice", None)
        if notice:
            doc.dropped = list(doc.dropped) + list(notice)
            self._conn_notice = []
        super()._sweep_residual(doc, source_pages)
