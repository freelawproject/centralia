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

    def extract(self, pdf_path):
        self._stamp_dropped = []
        doc = super().extract(pdf_path)
        extra = list(dict.fromkeys(self._stamp_dropped))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def page_lines(self, page):
        lines = super().page_lines(page)
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
