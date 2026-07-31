"""United States District Court, Western District of Virginia.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

**The clerk's received stamp.** Every vawd sheet carries it in the page-1
top-right corner — 'CLERKS OFFICE US DISTRICT COURT / AT ROANOKE, VA / FILED /
<date> / LAURA A. AUSTIN, CLERK / BY: s/<deputy> / DEPUTY CLERK' — applied over
the top margin at the same heights as the court banner. Three consequences:

* pdfplumber clusters the stamp's lines onto the BANNER's baselines, so a single
  extracted line reads 'ROANOKE DIVISION BY: s/J.Vasquez'. Dropping whole lines
  cannot separate them: the stamp has to come out run by run. It is identified
  by POSITION AS A RUN — a horizontal run standing alone out past 70% of the
  page width, with a wide gap between it and the banner text to its left. Type
  size does not identify it (the deputy-clerk line is often set in the banner's
  own size), and neither does font.
* Some of its glyphs are drawn from a font with no unicode mapping and extract
  as '(cid:NN)'; those come out with the rest of the run.
* The removal happens in ``correct_page_geometry``, not ``page_lines``, because
  the completeness audit reads the page through that hook — a ``page_lines``
  edit would leave the audit comparing against a ground-truth line that still
  had the stamp fused to the banner, reporting the banner as unplaced.

The stamp text is surfaced in ``doc.dropped``, handed over in
``_sweep_residual`` so it is in place before the completeness sweep reads it
(the sweep runs inside ``BaseExtractor.extract``).
"""

from __future__ import annotations

from ._district import DistrictBase

# The stamp is applied over the top margin, level with the banner and the first
# caption rows.
_STAMP_MAX_TOP = 160.0
# Fraction of page width: nothing left of this is the stamp.
_STAMP_X0 = 0.70
# Horizontal gap (pt) that separates the stamp run from the banner text beside
# it. Inter-word gaps in a banner are a few points; the stamp stands an inch
# or more clear of it.
_RUN_GAP = 12.0
# Baseline clustering tolerance: the stamp's 8pt glyphs and the banner's 13pt
# glyphs on one visual row differ in 'top' by a few points.
_ROW_TOL = 5.0


class WesternDistrictOfVirginia(DistrictBase):
    court_id = "vawd"
    styled_headmatter = True
    court_label = "United States District Court, Western District of Virginia."

    def extract(self, pdf_path):
        self._stamp_dropped = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Hand the clerk's stamp to ``doc.dropped`` before the sweep reads it."""
        extra = [
            t
            for t in dict.fromkeys(getattr(self, "_stamp_dropped", None) or [])
            if t
        ]
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)

    # ------------------------------------------------- clerk's received stamp
    def correct_page_geometry(self, page) -> None:
        super().correct_page_geometry(page)
        if page.page_number != 1:
            return
        if getattr(self, "_stamp_dropped", None) is None:
            self._stamp_dropped = []
        chars = page.chars
        limit = page.width * _STAMP_X0
        band = [
            i for i, c in enumerate(chars) if c.get("top", 0) < _STAMP_MAX_TOP
        ]
        if not band:
            return
        band.sort(key=lambda i: (chars[i]["top"], chars[i]["x0"]))
        drop = []
        row: list = []

        def flush(row):
            """Split one visual row into runs at wide x-gaps; a run standing
            alone out at the right margin is the stamp."""
            if not row:
                return
            row = sorted(row, key=lambda i: chars[i]["x0"])
            runs, cur = [], [row[0]]
            for i in row[1:]:
                if chars[i]["x0"] - chars[cur[-1]]["x1"] > _RUN_GAP:
                    runs.append(cur)
                    cur = [i]
                else:
                    cur.append(i)
            runs.append(cur)
            for run in runs:
                inked = [i for i in run if (chars[i].get("text") or "").strip()]
                if not inked or chars[inked[0]]["x0"] <= limit:
                    continue
                text = "".join(chars[i].get("text") or "" for i in run).strip()
                if text:
                    self._stamp_dropped.append(text)
                drop.extend(run)

        for i in band:
            if row and chars[i]["top"] - chars[row[0]]["top"] > _ROW_TOL:
                flush(row)
                row = []
            row.append(i)
        flush(row)
        for i in sorted(set(drop), reverse=True):
            del chars[i]
