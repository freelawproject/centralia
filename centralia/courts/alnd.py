"""United States District Court, Northern District of Alabama.

Shares the Alabama-district caption style — parties | case numbers separated by a
stacked divider column (']' here) — rendered as a whitespace-preserved facsimile
by the shared base (split by x-gap, so the ']' divider is handled the same as
the Middle/Southern districts' ')'). Opinion opens at the centered, bold
document title; signature-block author; bates / clerk 'FILED' stamp in the top
margin excluded.
"""

from __future__ import annotations

from ._aldistrict import AlabamaDistrictBase


class NorthernDistrictOfAlabama(AlabamaDistrictBase):
    court_id = "alnd"
    court_label = "United States District Court, Northern District of Alabama."

    # The clerk's electronic FILED stamp — 'FILED' / '<year> <Mon>-<day> <AM/PM>
    # <hh:mm>' / 'U.S. DISTRICT COURT' / 'N.D. OF ALABAMA' — is the only run on
    # the sheet set in this font: the CM/ECF header strip is LiberationSans and
    # the opinion itself is Times New Roman, so the stamp is identified by FONT,
    # not by x-position. It straddles the 39pt top margin, which lost the two
    # rows above the line while the two below it leaked into the headmatter and
    # rendered as a bogus two-column caption block ('U.S. DISTRICT COURT' /
    # 'N.D. OF ALABAMA'). Lifting the whole stamp out in one piece and
    # publishing it to the Removed box keeps it accounted for and out of the
    # caption.
    stamp_font = "Helvetica"
    stamp_max_top = 70.0

    def extract(self, pdf_path):
        self._alnd_stamp = {}
        return super().extract(pdf_path)

    def correct_page_geometry(self, page) -> None:
        """Lift the clerk FILED stamp off the page.

        Done here rather than in ``page_lines`` so the completeness audit reads
        the page exactly as the extractor does (the audit calls this hook); the
        stamp's text is stashed for ``_sweep_residual`` to publish."""
        super().correct_page_geometry(page)
        chars = page.chars
        hits = [
            i
            for i, c in enumerate(chars)
            if self.stamp_font in (c.get("fontname") or "")
            and c.get("top", 0) < self.stamp_max_top
        ]
        if not hits:
            return
        rows: dict = {}
        for i in hits:
            c = chars[i]
            rows.setdefault(round(c["top"], 0), []).append(c)
        lines = []
        for top in sorted(rows):
            text = "".join(
                (c.get("text") or "")
                for c in sorted(rows[top], key=lambda c: c["x0"])
            ).strip()
            if text:
                lines.append(text)
        if lines:
            stash = getattr(self, "_alnd_stamp", None)
            if stash is None:
                stash = self._alnd_stamp = {}
            stash[page.page_number] = lines
        for i in sorted(hits, reverse=True):
            del chars[i]

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Record the caption's verbatim rail-bearing rows on the caption block.

        Two of this district's judges set the caption rail as '}' ('The
        Gathering Brace') instead of the ']' the rest use. The rail is a
        DIVIDER, so the extractor keeps it out of the cells and the renderer
        draws it — which leaves the source row ('DANIEL L. CHAPEL, }') with no
        literal counterpart in the output. Attach those rows as the caption's
        ``source`` (the same accounting hook bap6 uses for a drawn border that
        replaces source glyphs), but ONLY after checking that every non-rail
        part of the row is already present as a cell — so this can never mask a
        genuinely dropped caption line."""
        out = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        rows = out.get("summary") or []
        cap = next(
            (r for r in rows if isinstance(r, dict) and r.get("__caption__")), None
        )
        rail = (cap or {}).get("rail")
        if not rail or len(str(rail)) != 1:
            return out

        def squash(t):
            return "".join(self._untag(str(t)).split()).lower()

        cells = set()
        for key in ("left", "right"):
            for c in cap.get(key) or []:
                s = squash(c.get("h", "") if isinstance(c, dict) else c)
                if s:
                    cells.add(s)
        src = []
        for seg in headmatter_segs:
            for line in seg:
                t = self.line_plain_text(line).strip()
                if not t or rail not in t:
                    continue
                parts = [p for p in t.split(rail) if squash(p)]
                if parts and all(squash(p) in cells for p in parts):
                    src.append(t)
        if src:
            cap["source"] = src
        return out

    def _sweep_residual(self, doc, source_pages) -> None:
        """Publish the clerk stamp to ``doc.dropped`` BEFORE the completeness
        sweep looks at it — the sweep runs inside ``super().extract()``."""
        stash = getattr(self, "_alnd_stamp", None) or {}
        rows = [t for pno in sorted(stash) for t in stash[pno]]
        if rows:
            seen = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                t for t in rows if not (t in seen or seen.add(t))
            ]
        super()._sweep_residual(doc, source_pages)
