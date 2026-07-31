"""United States District Court, District of Columbia.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.

Three dcd-specific geometry fixes, all in ``correct_page_geometry`` so the
completeness sweep and the audit read the page exactly as the extractor does:

  * a deeper bottom margin (footnotes run to the foot of the sheet, and some
    filings are typed on 817pt paper);
  * SMALL-CAPS rows — the AO forms set 'UNITED STATES DISTRICT COURT' with
    19.9pt initial capitals and 16pt small capitals on ONE baseline, which
    pdfplumber reads as two rows ('U S D C' + 'NITED TATES ISTRICT OURT');
  * 1pt hidden footnote-reference marks ('0F', '1F') that Word writes beside
    the visible marker and that otherwise land inside the body text
    ('78 Fed. Reg. at 2112.0F1 In 2019 …').
"""

from __future__ import annotations

from ._district import DistrictBase


class DistrictOfColumbia(DistrictBase):
    court_id = "dcd"
    court_label = "United States District Court, District of Columbia."

    # dcd filings run their footnote block right down to the foot of the sheet
    # (top≈731) and some are typed on LONG paper (817pt, not 792pt), so the
    # default 725pt cutoff shaves the last line off a footnote. The centered
    # folio sits lower still (745 on letter, 755 on the long sheet) and is
    # folded out by the printed-folio machinery, which reads the RAW page and
    # is unaffected by this margin.
    margin_bottom = 770

    # Sub-visible type: nothing a reader can see is under 4pt.
    _HIDDEN_MAX_SIZE = 4.0

    def extract(self, pdf_path):
        self._dcd_hidden = {}
        return super().extract(pdf_path)

    def correct_page_geometry(self, page) -> None:
        """Snap a mixed-size row onto one baseline and lift out Word's hidden
        1pt footnote-reference marks.

        Both are glyph-level corrections, so they belong here: the audit calls
        this hook, and a change made only in ``page_lines`` would leave the
        sweep reading a different page than the extractor."""
        super().correct_page_geometry(page)
        self._snap_baselines(page)
        self._drop_hidden_marks(page)

    @staticmethod
    def _snap_baselines(page) -> None:
        """Give every char that SITS ON one baseline the same ``top``.

        A small-caps banner draws its initial capitals larger than the rest of
        the word; the glyphs share a baseline (their ``bottom`` agrees within a
        point) but their ``top`` differs by the size difference, and that is
        what pdfplumber clusters rows on — so one printed row extracts as two.
        Superscripts and subscripts do NOT share the baseline (their bottom is
        raised / dropped), so they are untouched by this."""
        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        chars.sort(key=lambda c: c["bottom"])
        groups, cur = [], []
        for c in chars:
            if cur and c["bottom"] - cur[-1]["bottom"] > 1.5:
                groups.append(cur)
                cur = []
            cur.append(c)
        if cur:
            groups.append(cur)
        for g in groups:
            tops = [c["top"] for c in g]
            if max(tops) - min(tops) <= 1.0:
                continue
            target = min(tops)
            for c in g:
                delta = target - c["top"]
                if delta:
                    c["top"] += delta
                    c["doctop"] += delta

    def _drop_hidden_marks(self, page) -> None:
        """Remove glyphs too small to be read — Word's hidden cross-reference
        text for a footnote mark ('0F' beside the visible '1'). Left in place
        they fuse into the sentence ('at 2112.0F1 In 2019 …'). The text is
        remembered so ``_sweep_residual`` can surface it in the Removed box."""
        chars = page.chars
        hits = [
            i
            for i, c in enumerate(chars)
            if (c.get("text") or "").strip()
            and c.get("size", 12.0) < self._HIDDEN_MAX_SIZE
        ]
        if not hits:
            return
        text = "".join(
            (chars[i].get("text") or "")
            for i in sorted(hits, key=lambda i: (chars[i]["top"], chars[i]["x0"]))
        ).strip()
        if text:
            stash = getattr(self, "_dcd_hidden", None)
            if stash is None:
                stash = self._dcd_hidden = {}
            stash[page.page_number] = text
        for i in sorted(hits, reverse=True):
            del chars[i]

    # Glyphs a district caption uses as its column rail.
    _RAIL_GLYPHS = ")]§:|"

    def _caption_char_runs(self, line) -> list:
        """Keep a docket LABEL that ends in the rail glyph joined to its value.

        dcd captions are railed with a stacked ':' and the docket column reads
        'Re Document Nos.:   181, 182, 184' — the label and the value are set
        with a wide gap between them, so they split into two caption runs and
        the first one ends in ':'. The shared caption folder strips a rail glyph
        off the head/tail of a run, so that colon — part of the label, not the
        rail — is eaten. A genuine rail run is a LONE glyph, never a glyph
        attached to text, so re-joining the pair (same side of the page, so a
        party name can never be pulled across the gutter) protects the label
        without touching a real rail."""
        runs = super()._caption_char_runs(line)
        if len(runs) < 2:
            return runs
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        mid = pw * 0.45
        out = [runs[0]]
        for run in runs[1:]:
            prev = out[-1]
            printable = [c for c in prev if (c.get("text") or "").strip()]
            if (
                len(printable) > 1
                and (printable[-1].get("text") or "") in self._RAIL_GLYPHS
                and (prev[0]["x0"] < mid) == (run[0]["x0"] < mid)
            ):
                out[-1] = prev + run
            else:
                out.append(run)
        return out

    def _sweep_residual(self, doc, source_pages) -> None:
        """Publish the hidden marks BEFORE the completeness sweep runs (the
        sweep happens inside ``super().extract()``, so appending afterwards
        would be too late)."""
        stash = getattr(self, "_dcd_hidden", None) or {}
        rows = [stash[p] for p in sorted(stash)]
        if rows:
            seen = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                t for t in rows if not (t in seen or seen.add(t))
            ]
        super()._sweep_residual(doc, source_pages)
