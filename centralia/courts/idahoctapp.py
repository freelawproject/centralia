"""Idaho Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class IdahoCourtOfAppeals(StateAppellate):
    court_id = "idahoctapp"
    court_label = "Idaho Court of Appeals."
    fold_page_numbers = True  # bare page numbers -> inline page-break markers

    # Senior/visiting judges sit by designation as 'NAME, Judge Pro Tem'
    # (no trailing period). Add the spelled-out pro-tempore titles so the
    # byline grammar recognizes the opinion start; without them the whole
    # document falls into headmatter (state_v._reyes).
    author_titles = ("Judge Pro Tempore", "Judge Pro Tem") + StateAppellate.author_titles

    # Idaho sets the body at 1.5 leading (~21pt) and single-spaces block quotes
    # / footnotes at ~14pt. The default bands (single<22) read the 21pt body as
    # a block quote, tagging the whole opinion as quoted. Shift the bands down
    # so 14→single (block quote) and 21→body.
    gap_tight_max = 11
    gap_single_max = 17

    # A centered line at most this fraction of the measure is a bare section
    # number, not the first row of a wrapped heading.
    section_number_max_frac = 0.10

    def split_body_paragraphs(self, seg) -> list:
        out = []
        for para in super().split_body_paragraphs(seg):
            out.extend(self._split_section_number(para))
        return out

    def _split_section_number(self, para) -> list:
        """Idaho centers the section NUMBER on its own line above the section
        title — 'III.' then 'ANALYSIS', 'IV.' then 'CONCLUSION'. Both rows are
        centered and exactly one body leading apart, so they read as one
        wrapped heading and join into 'III. ANALYSIS' on a single line.

        They are two rows in the PDF and must stay two rows. The base leaves
        centered groups joined on purpose — a centered heading that wraps IS
        one heading — so the split is by width: a wrapped heading's first row
        runs out near the full measure, while a bare numeral is a few glyphs
        ('III.' is 17pt against a 468pt measure)."""
        if len(para) < 2:
            return [para]
        pw = getattr(self, "_page1_width", None) or 612.0
        measure = pw - 2 * self.body_baseline_x0
        first = para[0]
        width = first["x1"] - first["x0"]
        if width > measure * self.section_number_max_frac:
            return [para]
        # Centered: the row's midpoint sits on the page axis.
        if abs((first["x0"] + first["x1"]) / 2 - pw / 2) > 12:
            return [para]
        return [[first]] + self._split_section_number(para[1:])

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Fold the ')'-railed caption (The Banded Bracket) into a two-column
        block so parties sit left of the centered rail and the docket/clerk
        column sits right — like delch/wash."""
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_rail_caption(d["summary"], ")")
        return d
