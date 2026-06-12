"""United States District Court, Southern District of Texas.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block and treats the whole ruling as one opinion.

txsd quirks:
  * every filing carries the clerk's e-filing stamp in the TOP-RIGHT corner of
    page 1 ('United States District Court / Southern District of Texas /
    ENTERED / <date> / Nathan Ochsner, Clerk') — page furniture. Left in the
    flow it pairs with the centered court banner and folds into a phantom
    two-column caption; it is dropped (and surfaced) instead;
  * several rulings are flatbed scans run through OCR — the signature name
    line carries artifacts ('~ DAVID HITTNER' squiggle residue, 'Andrew S.
    Han en' split surname), which the strict name check rejects. A second,
    OCR-tolerant pass cleans junk tokens and re-joins split fragments;
  * fully scanned files with no OCR text layer yield only the stamp text —
    nothing to extract (flagged suspect by the base).
"""

from __future__ import annotations

from ._district import DistrictBase, _JUDGE_TITLES, _SIG_SKIP, _is_rule


class SouthernDistrictOfTexas(DistrictBase):
    court_id = "txsd"
    court_label = "United States District Court, Southern District of Texas."

    # --------------------------------------------------- ENTERED stamp drop
    def page_lines(self, page):
        if not hasattr(self, "_txsd_dropped"):
            self._txsd_dropped = []
        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        pw = page.width
        kept = []
        for l in lines:
            if l.get("top", 0) >= 110:
                kept.append(l)
                continue
            # The stamp occupies the top-right corner; pdfplumber can merge a
            # stamp line onto the centered banner's baseline ('UNITED STATES
            # DISTRICT COURT April 10, 2026'), so split the line's chars at
            # wide x-gaps and drop only the runs fully right of ~0.72 pw.
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
                if r[0]["x0"] >= pw * 0.72:
                    t = "".join(c.get("text") or "" for c in r).strip()
                    if t:
                        self._txsd_dropped.append(t)
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
        self._txsd_dropped = []
        doc = super().extract(pdf_path)
        if self._txsd_dropped:
            seen, extra = set(), []
            for t in self._txsd_dropped:
                if t not in seen:
                    seen.add(t)
                    extra.append(t)
            doc.dropped = list(doc.dropped) + extra
        return doc

    # ----------------------------------------------- OCR-tolerant signature
    def _signature_author(self, all_segments):
        author = super()._signature_author(all_segments)
        if author:
            return author
        # OCR pass: clean each candidate line (drop letterless junk tokens
        # like '~', re-join an OCR-split surname fragment 'Han en' → 'Hanen')
        # and re-test with the same walk-back-from-title scan.
        lines = [
            self.line_plain_text(l).strip()
            for _p, seg, _k in all_segments
            for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, -1, -1):
            low = lines[i].lower().strip().rstrip(".")
            if not any(
                low == t.rstrip(".") or low.endswith(" " + t.rstrip("."))
                for t in _JUDGE_TITLES
            ):
                continue
            for j in range(i - 1, max(-1, i - 5), -1):
                cand = self._ocr_clean(lines[j])
                clow = cand.lower()
                if _is_rule(cand) or any(clow.startswith(s) for s in _SIG_SKIP):
                    continue
                if self._ocr_name_ok(cand):
                    return cand.rstrip(",")
            break
        return None

    @staticmethod
    def _ocr_clean(text: str) -> str:
        toks = [t for t in text.split() if any(c.isalpha() for c in t)]
        # re-join a short all-lowercase fragment onto the preceding token
        # ('Han en' — OCR split the surname)
        out = []
        for t in toks:
            if out and t.islower() and len(t) <= 3 and out[-1][:1].isupper():
                out[-1] = out[-1] + t
            else:
                out.append(t)
        return " ".join(out)

    @staticmethod
    def _ocr_name_ok(text: str) -> bool:
        toks = text.rstrip(",").split()
        if not (2 <= len(toks) <= 5):
            return False
        for tok in toks:
            core = tok.rstrip(".,").replace("-", "").replace("'", "")
            if core.lower() in ("jr", "sr", "ii", "iii", "iv"):
                continue
            if not core or not core[0].isupper() or not core.isalpha():
                return False
        return True
