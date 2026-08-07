"""Oregon Tax Court, Magistrate Division.

')'-rail caption under the 'IN THE OREGON TAX COURT / MAGISTRATE
DIVISION' banner, a centered decision heading ('DECISION' / 'DECISION OF
DISMISSAL' / 'ORDER …'), and a closing block 'This document was signed by
Magistrate Richard D. Davis and entered on <date>' that names the author.
A running footer ('ORDER TC-MD 250545R 6') sits in the bottom margin.
"""

from __future__ import annotations

from collections import Counter
from statistics import median

from ._district import DistrictBase


class OregonTaxMagistrate(DistrictBase):
    court_id = "ortc"
    court_label = "Oregon Tax Court, Magistrate Division."

    # Quoted statutes are single-spaced at ~14pt but indented on the LEFT only
    # (they run to the full right margin), so the both-margins ``blockquote_by_
    # indent`` test misses them and their ~14pt leading falls below the default
    # gap_tight_max (16) into the 'notice' band. Lower the tight threshold so a
    # single-spaced run lands in the blockquote band (body stays double-spaced
    # at ~28pt).
    gap_tight_max = 12

    def extract(self, pdf_path):
        self._ortc_band = {}
        self._ortc_rails = Counter()
        return super().extract(pdf_path)

    # ------------------------------------------------------------------
    # Footnote separator
    #
    # The chain this court inherits cannot see either of its separators.
    # ``GenericExtractor`` (which sits between DistrictBase and the base
    # chain) asks for a RECT at least 100pt wide whose top is below
    # ``page.height * 0.55`` — three assumptions, and this corpus breaks
    # all of them:
    #
    #   * the Oregon Tax Reports setting (a 396pt sheet) STROKES its rules
    #     as vector lines, so ``page.rects`` is empty on every page;
    #   * that setting draws the separator 58.5pt wide — 19% of its own
    #     301.5pt measure, proportionally WIDER than a letter-page rule,
    #     yet far under the 100pt floor;
    #   * the height fence throws away the rule of any footnote long
    #     enough to push it up the page. ringo page 5 is ONE footnote,
    #     top to bottom, and its continuation rule sits at y=85 of 792.
    #
    # So measure the page instead: the separator is a thin rule standing
    # at the page's own left text rail, shorter than that page's measure,
    # ALONE on its baseline (a table row rule has sibling segments to its
    # right at the same y — the Oregon reporter draws table rows starting
    # with a segment exactly as wide as the separator), and with nothing
    # but smaller-than-body type below it. No position fence at all.
    # ------------------------------------------------------------------

    @staticmethod
    def _measured_rail(page):
        """The page's own left text rail and text measure, read off the
        lines it sets at full measure. Recurrence is what makes 'leftmost'
        safe — one outdented stray cannot move the rail."""
        counts, right = Counter(), []
        for line in page.extract_text_lines():
            if (line["x1"] - line["x0"]) < page.width * 0.45:
                continue
            counts[round(line["x0"])] += 1
            right.append(line["x1"])
        recurring = [x for x, hits in counts.items() if hits >= 2]
        if not recurring:
            return None, None
        rail = float(min(recurring))
        return rail, max(right) - rail

    @staticmethod
    def _thin_rules(page):
        """(top, x0, width) for every thin horizontal shape, stroked or
        filled — this court uses vector lines, the CM/ECF filings use
        filled rects."""
        out = []
        for objs in (page.rects, page.lines):
            for shape in objs:
                if abs(shape["bottom"] - shape["top"]) < 2:
                    out.append(
                        (
                            shape["top"],
                            min(shape["x0"], shape["x1"]),
                            abs(shape["x1"] - shape["x0"]),
                        )
                    )
        return out

    def find_footnote_separator(self, page):
        sep = self._measured_footnote_rule(page)
        if sep is not None:
            return sep
        return super().find_footnote_separator(page)

    def _measured_footnote_rule(self, page):
        rail, measure = self._measured_rail(page)
        rails = set()
        if rail is not None:
            rails.add(rail)
            store = getattr(self, "_ortc_rails", None)
            if store is None:
                store = self._ortc_rails = Counter()
            store[round(rail)] += 1
            # A page that is nothing BUT a long footnote sets its whole
            # measure at the note's indent, so its own rail reads as that
            # indent (the wrong-statistic trap). The rail the document has
            # been using on every page before it is the other candidate.
            rails.add(float(store.most_common(1)[0][0]))
        if not rails or not measure:
            return None
        shapes = self._thin_rules(page)
        text_lines = [
            line
            for line in page.extract_text_lines()
            if (line.get("text") or "").strip() and (line.get("chars") or [])
        ]
        best = None
        for top, x0, width in shapes:
            if not any(abs(x0 - r) <= 2 for r in rails):
                continue
            # Short of the full measure: a rule spanning the whole measure
            # at the rail is the reporter's running-head rule.
            if not (measure * 0.05 <= width <= measure * 0.9):
                continue
            # A table row rule carries sibling segments at the same y.
            if any(
                abs(other_top - top) <= 1 and other_x0 > x0 + width / 2
                for other_top, other_x0, _w in shapes
            ):
                continue
            above = [
                self._line_type_size(line["chars"])
                for line in text_lines
                if line["bottom"] <= top + 1
            ]
            below = [
                self._line_type_size(line["chars"])
                for line in text_lines
                if line["top"] > top + 1
            ]
            if not below:
                continue
            # Everything below is footnote type. Nothing above at all means
            # the rule opens the page — the continuation separator over a
            # footnote that ran off the previous page.
            if above and max(below) >= median(above) - 0.5:
                continue
            if best is None or top < best:
                best = top
        return best

    def page_lines(self, page):
        """Record the Oregon Tax Reports running head before the margin filter
        discards it.

        The corpus holds two document styles. Magistrate Division DECISIONs are
        letter-size (612pt) CM/ECF filings with nothing in the top margin.
        Regular Division opinions are the REPORTER setting on a narrow 396pt
        sheet, and every page of those carries exactly one running-head line in
        the top margin — 'No. 9 October 28, 2022 173' on the opening page, then
        alternating '<folio> <case name>' and 'Cite as 25 OTR 173 (2022)
        <folio>'. It is page furniture, but it has to be SURFACED rather than
        silently clipped, so stash it here for ``_sweep_residual`` to publish to
        the Removed box."""
        band = [
            l
            for l in self._text_lines(page.filter(lambda o: o["top"] < self.margin_top))
            if (l.get("text") or "").strip()
        ]
        if band:
            stash = getattr(self, "_ortc_band", None)
            if stash is None:
                stash = self._ortc_band = {}
            stash[page.page_number] = [
                (l.get("text") or "").strip() for l in band
            ]
        return super().page_lines(page)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Publish the reporter running head to ``doc.dropped`` BEFORE the
        completeness sweep reads it — the sweep runs inside ``extract()``."""
        stash = getattr(self, "_ortc_band", None) or {}
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
        if not getattr(self, "_district_author", None):
            self._district_author = self._signed_by(all_segments)
        return out

    @staticmethod
    def _is_fully_bold(text) -> bool:
        """A block whose entire content is bold (bold or bold-italic). The
        appeal-rights boilerplate and the 'signed by … entered on' line are set
        this way; regular-Roman body prose and italic-only lead-in terms
        ('<em>Webster's</em> defines …') are not."""
        s = str(text).strip()
        return s.startswith("<strong>") and s.endswith("</strong>")

    def _harvest_signature(self, doc):
        """Peel the trailing bold notices (appeal-rights advisory, 'This
        document was signed by … entered on <date>') off the opinion into
        ``doc.dropped`` — keyed on font/style, not wording — then let the
        district signature harvest run on what remains."""
        if doc.opinions:
            op = doc.opinions[-1]
            blocks = op.blocks
            peeled = []
            while blocks and self._is_fully_bold(blocks[-1].text):
                peeled.append(self._untag(blocks[-1].text).strip())
                blocks = blocks[:-1]
            if peeled:
                op.blocks = blocks
                doc.dropped = list(doc.dropped or []) + list(reversed(peeled))
        super()._harvest_signature(doc)

    def _signed_by(self, all_segments):
        """Author from 'This document was signed by [Presiding] Magistrate
        Richard D. Davis and entered on <date>.'"""
        for _p, seg, _k in all_segments:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                for key in (
                    "signed by presiding magistrate ",
                    "signed by magistrate ",
                ):
                    ki = low.find(key)
                    if ki < 0:
                        continue
                    name = []
                    for tok in t[ki + len(key) :].split():
                        core = tok.strip(".,")
                        if tok.lower() in ("and", "on") or not core:
                            break
                        if core[0].isupper():
                            name.append(core + "." if len(core) == 1 else core)
                        else:
                            break
                    if name:
                        return " ".join(name)
        return None
