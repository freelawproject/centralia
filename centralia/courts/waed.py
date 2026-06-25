"""United States District Court, Eastern District of Washington.

CM/ECF filing — a single ruling by one judge, on numbered pleading paper.

waed quirks:
  * a RED filing stamp sits top-right of page 1 ('FILED IN THE / U.S.
    DISTRICT COURT / EASTERN DISTRICT OF WASHINGTON / <date> / SEAN F.
    MCAVOY, CLERK') — furniture, dropped and surfaced;
  * the BLUE CM/ECF bates header ('Case 2:24-cv-00417-SAB ECF No. 36 filed
    04/07/26 PageID.615 Page 1 of 8') is removed by the margin filter — its
    removal is NOTED in the dropped box so the review shows what was taken;
  * the page-1 caption closes with a BOTH-SIDES horizontal rule meeting the
    mid vertical (y≈461); the generic separator scan can mistake that
    caption shelf for the footnote rule, which shoves the order's opening
    body into the footnote flow as a '?'-label footnote. The real separator
    is the classic ~144pt rule (y≈691) — caption-band rules are excluded
    via the page-1 fingerprint;
  * orders are signed with an INKED SIGNATURE IMAGE over 'DATED this …' —
    harvested to the Signature section by the shared base; the judge's name
    is pixels, so the author stays empty rather than guessed.
"""

from __future__ import annotations

from ._district import DistrictBase


class EasternDistrictOfWashington(DistrictBase):
    court_id = "waed"
    court_label = "United States District Court, Eastern District of Washington."

    # ------------------------------------------------------- page furniture
    def page_lines(self, page):
        if not hasattr(self, "_waed_dropped"):
            self._waed_dropped = []
        # note the blue CM/ECF bates header before the margin filter eats it
        # (red stamp lines can merge into this band too — record them all)
        if page.page_number == 1:
            try:
                first = True
                for tl in page.extract_text_lines():
                    t = (tl.get("text") or "").strip()
                    if tl["top"] < 28 and t:
                        if first:
                            self._waed_dropped.append(
                                "[blue CM/ECF bates header removed: "
                                + t
                                + " — and on every page]"
                            )
                            first = False
                        else:
                            self._waed_dropped.append(t)
            except Exception:
                pass
        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        pw = page.width
        kept = []
        for l in lines:
            if l.get("top", 0) >= 165:
                kept.append(l)
                continue
            # the red FILED stamp: top-right corner block. Its lines can merge
            # onto the bates header's baseline, so split each top-band line's
            # chars at wide x-gaps and drop only the right-zone runs.
            runs, cur = [], []
            for c in sorted(l.get("chars") or [], key=lambda c: c["x0"]):
                if cur and c["x0"] - cur[-1]["x1"] > 30:
                    runs.append(cur)
                    cur = [c]
                else:
                    cur.append(c)
            if cur:
                runs.append(cur)
            keep_chars, dropped_any = [], False
            for r in runs:
                if r[0]["x0"] >= pw * 0.6:
                    t = "".join(c.get("text") or "" for c in r).strip()
                    if t:
                        self._waed_dropped.append(t)
                    dropped_any = True
                else:
                    keep_chars.extend(r)
            if not dropped_any:
                kept.append(l)
            elif keep_chars:
                nl = dict(l)
                nl["chars"] = keep_chars
                nl["text"] = "".join(c.get("text") or "" for c in keep_chars)
                nl["x0"] = min(c["x0"] for c in keep_chars)
                nl["x1"] = max(c["x1"] for c in keep_chars)
                kept.append(nl)
        return kept

    def extract(self, pdf_path: str):
        self._waed_dropped = []
        doc = super().extract(pdf_path)
        if self._waed_dropped:
            seen, extra = set(), []
            for t in self._waed_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    # footnote separator: the caption-shelf exclusion now lives in
    # DistrictBase.find_footnote_separator (shared — wawd had the same bug).
