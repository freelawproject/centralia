"""United States District Court, Western District of Virginia.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

The clerk's e-filing stamp in the page-1 top-right corner is set in a font
with no unicode mapping — its glyphs extract as '(cid:NN)' tokens overlapping
the caption lines — so those chars are stripped (the stamp's one readable
line, the filing date, stays).
"""

from __future__ import annotations

from ._district import DistrictBase


class WesternDistrictOfVirginia(DistrictBase):
    court_id = "vawd"
    styled_headmatter = True
    court_label = "United States District Court, Western District of Virginia."

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
            chars = ln.get("chars") or []
            clean = [c for c in chars if not (c.get("text") or "").startswith("(cid:")]
            if not clean:
                continue  # a pure stamp-glyph line
            if len(clean) != len(chars):
                ln = dict(ln)
                ln["chars"] = clean
                ln["x0"] = min(c["x0"] for c in clean)
                ln["x1"] = max(c["x1"] for c in clean)
            # The clerk's received stamp sits in the top-right corner above
            # the caption ('CLERKS OFFICE US DISTRICT COURT / AT ROANOKE, VA
            # / FILED / <date> / <clerk>') — furniture, recorded as dropped.
            if ln["top"] < 140 and ln["x0"] > page.width * 0.62:
                txt = self.line_plain_text(ln).strip()
                if txt:
                    self._stamp_dropped.append(txt)
                continue
            kept.append(ln)
        return kept
