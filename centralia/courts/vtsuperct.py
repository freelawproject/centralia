"""Vermont Superior Court.

Intermediate appellate court. Single ruling by one judge; the author comes from the signature block and the whole ruling is one opinion (district-court model).
"""

from __future__ import annotations

from ._district import DistrictBase


class VermontSuperiorCourt(DistrictBase):
    court_id = "vtsuperct"
    court_label = "Vermont Superior Court."

    def extract(self, pdf_path):
        self._vt_stamp = {}
        return super().extract(pdf_path)

    # ------------------------------------------------------ source-quality gate
    def is_non_digital(self, pdf) -> bool:
        """Also refuse a PDF with NO text layer at all.

        The Vermont Judiciary publishes some rulings as a pure scan assembled
        from many small tiles — no single image covers the 85% of a page the
        shared raster test looks for, and there is no OCR pass either, so every
        page extracts zero characters. Nothing can be parsed from that; flag it
        as non-digital rather than emit a confident-looking empty document."""
        if super().is_non_digital(pdf):
            return True
        pages = pdf.pages
        if not pages:
            return False
        chars = sum(
            1 for p in pages for c in p.chars if (c.get("text") or "").strip()
        )
        return chars < 20 * len(pages)

    # -------------------------------------------------------- e-filing stamp
    def page_lines(self, page):
        """Record the Vermont Judiciary e-filing stamp before the margin filter
        clips it.

        Every e-filed ruling is stamped flush right in the very top margin with
        three rows — 'Vermont Superior Court' / 'Filed <mm/dd/yy>' / '<County>
        Unit' (or 'Environmental Division'). The stamp is applied by rasterising
        and re-OCRing page 1, so it comes through mangled ('7ermont
        SuperiorCourt', 'Chittenden UUnit') — machine furniture either way, but
        it has to be SURFACED, not silently clipped, so stash it for
        ``_sweep_residual`` to publish to the Removed box."""
        right_edge = (getattr(page, "width", 612.0) or 612.0) * 0.6
        band = [
            l
            for l in self._text_lines(
                page.filter(
                    lambda o: o["top"] < self.margin_top and o["x0"] >= right_edge
                )
            )
            if (l.get("text") or "").strip()
        ]
        if band:
            stash = getattr(self, "_vt_stamp", None)
            if stash is None:
                stash = self._vt_stamp = {}
            stash[page.page_number] = [
                (l.get("text") or "").strip() for l in band
            ]
        return super().page_lines(page)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Publish the e-filing stamp to ``doc.dropped`` BEFORE the completeness
        sweep reads it — the sweep runs inside ``extract()``."""
        stash = getattr(self, "_vt_stamp", None) or {}
        rows, seen = list(doc.dropped), set(doc.dropped)
        for pno in sorted(stash):
            for t in stash[pno]:
                if t not in seen:
                    seen.add(t)
                    rows.append(t)
        doc.dropped = rows
        super()._sweep_residual(doc, source_pages)

    def find_authors(self, all_segments) -> list:
        out = super().find_authors(all_segments)
        # a furniture line ('Superior Court Judge') is not a name
        au = getattr(self, "_district_author", None)
        if au and any(w in au.lower().split() for w in ("court", "division", "superior")):
            self._district_author = None
        if out and getattr(self, "_district_author", None):
            return out
        # Environmental Division decisions have no heading after the
        # masthead — the ruling starts at the first body paragraph and is
        # signed 'Electronically signed … / Thomas G. Walsh, Judge /
        # Superior Court, Environmental Division' (name + title one line).
        if not getattr(self, "_district_author", None):
            lines = [
                self.line_plain_text(l).strip()
                for _p, seg, _k in all_segments
                for l in seg
            ]
            for t in reversed(lines):
                if t.lower().rstrip(".").endswith(", judge") or t.lower().rstrip(
                    "."
                ).endswith(" judge"):
                    head = t.rsplit(",", 1)[0].strip()
                    toks = head.split()
                    if (
                        2 <= len(toks) <= 4
                        and all(w[:1].isupper() for w in toks)
                        and not any(
                            w.lower() in ("court", "superior", "division", "judge")
                            for w in toks
                        )
                    ):
                        self._district_author = head
                        break
        if out:
            return out
        # single-spaced decisions read as 'notice' to the classifier — the
        # ruling starts at the first multi-line prose segment
        for i, (_p, seg, kind) in enumerate(all_segments):
            if kind == "body" or (
                kind in ("notice", "blockquote") and len(seg) >= 3
            ):
                return [i]
        return []
