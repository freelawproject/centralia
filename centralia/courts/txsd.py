"""United States District Court, Southern District of Texas.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block and treats the whole ruling as one opinion.

txsd quirks:
  * every filing carries the clerk's e-filing stamp in the TOP-RIGHT corner of
    page 1 ('United States District Court / Southern District of Texas /
    ENTERED / <date> / Nathan Ochsner, Clerk') — page furniture. Left in the
    flow it pairs with the centered court banner and folds into a phantom
    two-column caption; it is dropped (and surfaced) instead. The stamp is
    identified by FONT: it is stamped in the base-14 'Helvetica' the clerk's
    software carries, the only unsubsetted sans-serif on the sheet (every
    judge's body font is a subsetted serif — CenturySchoolbook, Times New
    Roman, BookAntiqua, Georgia). Keying on the font rather than an x
    threshold matters because pdfplumber merges the stamp's rows onto the
    court banner's baseline ('SOUTHERN DISTRICT OF TEXAS Nathan Ochsner,
    Clerk'), and the glyphs are removed in ``correct_page_geometry`` so the
    completeness sweep reads the page the same way the extractor does;
  * several rulings are flatbed scans run through OCR — the signature name
    line carries artifacts ('~ DAVID HITTNER' squiggle residue, 'Andrew S.
    Han en' split surname), which the strict name check rejects. A second,
    OCR-tolerant pass cleans junk tokens and re-joins split fragments;
  * fully scanned files with no OCR text layer yield only the stamp text —
    nothing to extract (flagged suspect by the base).
"""

from __future__ import annotations

import re

from ._district import DistrictBase, _JUDGE_TITLES, _SIG_SKIP, _is_rule


class SouthernDistrictOfTexas(DistrictBase):
    court_id = "txsd"
    court_label = "United States District Court, Southern District of Texas."

    # These judges set a shallow bottom margin: the last line of a footnote
    # lands at top≈725 and a signature block can run to top≈733, both of which
    # the default 725pt cutoff shaves off the page — silently losing footnote
    # text (2084697) and a whole conformed signature (2098261.6). The centered
    # page folio sits lower still (top≈745, or 728-738 on the scans) and is
    # folded out by the folio machinery, not by the margin.
    margin_bottom = 742

    # A subset of TXSD's CM/ECF opinions uses a left-aligned fractional folio
    # (``1 / 5``, ``2 / 5``, ...) at the bottom of every page.  The shared
    # folio parser intentionally accepts only ordinary numeric folios, so this
    # footer otherwise remains in the body/residual stream.  Keep the broader
    # syntax local to TXSD: a slash is ordinary authored text in many courts.
    _FRACTION_FOLIO = re.compile(r"^(\d{1,4})\s*/\s*(\d{1,4})$")

    @classmethod
    def _page_number_value(cls, text: str) -> str | None:
        value = super()._page_number_value(text)
        if value is not None:
            return value
        candidate = re.sub(r"<[^>]+>", "", str(text or "")).strip()
        candidate = candidate.strip("-–— ")
        match = cls._FRACTION_FOLIO.fullmatch(candidate)
        return f"{match.group(1)}/{match.group(2)}" if match else None

    @classmethod
    def _is_page_number_text(cls, text: str) -> bool:
        return cls._page_number_value(text) is not None

    # --------------------------------------------------- ENTERED stamp drop
    # The clerk's stamping software uses the PDF base-14 fonts, which carry no
    # subset tag; every judge's word processor embeds a subsetted body font
    # ('BCDEEE+TimesNewRomanPSMT'). So an unsubsetted Helvetica glyph in the
    # page-1 top band is stamp, never text the judge typed.
    _STAMP_FONTS = ("Helvetica", "Helvetica-Bold")
    _STAMP_BAND = 118.0  # bottom of the stamp band (the caption starts below)

    def correct_page_geometry(self, page) -> None:
        """Remove the clerk's 'ENTERED' stamp glyphs from page 1.

        Done here (not in ``page_lines``) so the completeness sweep and the
        audit read the page through the same removal — otherwise the stamp's
        rows, which pdfplumber merges onto the court banner's baseline, read
        back as unplaced content. The text is remembered and surfaced in
        ``doc.dropped``."""
        super().correct_page_geometry(page)
        if page.page_number != 1:
            return
        if not hasattr(self, "_txsd_dropped"):
            self._txsd_dropped = []
        chars = page.chars
        stamp = [
            i
            for i, c in enumerate(chars)
            if c.get("top", 0) < self._STAMP_BAND
            and (c.get("fontname") or "") in self._STAMP_FONTS
        ]
        if not stamp:
            return
        # Re-read the stamp in reading order (row by row, left to right) so the
        # Removed box shows it as it was printed.
        rows: dict = {}
        for i in stamp:
            c = chars[i]
            rows.setdefault(round(c["top"] / 4.0), []).append(c)
        for key in sorted(rows):
            row = sorted(rows[key], key=lambda c: c["x0"])
            text = "".join(c.get("text") or "" for c in row).strip()
            if text:
                self._txsd_dropped.append(text)
        for i in sorted(stamp, reverse=True):
            del chars[i]

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
