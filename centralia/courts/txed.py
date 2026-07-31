"""United States District Court, Eastern District of Texas.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band is dropped.
"""

from __future__ import annotations

from collections import Counter

from ._district import DistrictBase


class EasternDistrictOfTexas(DistrictBase):
    court_id = "txed"
    court_label = "United States District Court, Eastern District of Texas."

    def prepare_document(self, pdf) -> None:
        """Select the TXED body measure from the page geometry.

        Most TXED orders use the ordinary 1-inch body rail (x≈72), with
        quoted/list material pulled in to x≈144.  A smaller habeas/order
        template instead sets ordinary prose in a narrow x≈144..468 column,
        with only an 18pt first-line indent (x≈162).  Treating that template
        with the wide-page defaults labels nearly every paragraph a quote.

        The body rail is the dominant left edge of text below the caption and
        above the footer.  This is deliberately a geometry-only decision; no
        document wording is used to choose the layout.
        """
        self._txed_narrow_layout = False
        counts = Counter()
        has_wide_body_rail = False
        for page in list(pdf.pages)[:3]:
            try:
                lines = page.extract_text_lines() or []
            except Exception:
                lines = []
            for line in lines:
                text = (line.get("text") or "").strip()
                top = line.get("top", 0)
                if not text or top < 260 or top > page.height - 100:
                    continue
                x0 = round(line.get("x0", 0) / 6.0) * 6.0
                counts[x0] += 1
                if x0 <= 90:
                    has_wide_body_rail = True
        if counts:
            body_x0, count = counts.most_common(1)[0]
            if 132 <= body_x0 <= 156 and count >= 12 and not has_wide_body_rail:
                self._txed_narrow_layout = True
                self.body_baseline_x0 = body_x0
                self.para_indent_min = 12.0

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        # The narrow template is single-spaced throughout.  Its ordinary
        # paragraphs therefore land in the shared spacing-based blockquote
        # band even though their left edge is the document's body rail.
        if getattr(self, "_txed_narrow_layout", False) and kind == "blockquote":
            return "body"
        return kind

    def find_authors(self, all_segments) -> list:
        """Keep a page-one docket-control schedule in the opinion body.

        In this TXED template the schedule follows the caption as a ruled,
        two-column layout.  The shared caption fingerprint can mistake the
        schedule's repeated ``*`` rail for a continuation of the caption and
        then choose an opinion start halfway through the table.  The reliable
        geometric boundary is the centered, bold order heading followed by
        left-column date rows and right-column schedule rows.
        """
        idx = super().find_authors(all_segments)
        schedule_start = None
        for i, (pno, seg, _kind) in enumerate(all_segments):
            if pno != 1 or not seg:
                continue
            line = seg[0]
            text = self.line_plain_text(line).strip()
            if not text:
                continue
            if not (200 <= line.get("top", 0) <= 245):
                continue
            if self.line_alignment(line, getattr(self, "_page1_width", 612.0)) != "C":
                continue
            size, _font, bold = self.line_meta(line)
            if not bold or size < 11 or line.get("x1", 0) - line.get("x0", 0) > 250:
                continue
            # Confirm this is the schedule template by its immediately
            # following geometry: an introductory line, then a two-column
            # deadline row with a left date rail and a right text rail.
            following = [x for x in all_segments[i + 1 : i + 8] if x[0] == 1]
            if not following:
                continue
            has_intro = any(
                s and s[0].get("x0", 0) >= 96 and s[0].get("x0", 0) < 140
                for _p, s, _k in following[:2]
            )
            has_two_columns = any(
                s
                and 60 <= s[0].get("x0", 0) <= 90
                and any(l.get("x0", 0) >= 190 for l in s)
                for _p, s, _k in following
            )
            if has_intro and has_two_columns:
                schedule_start = i
                break
        if schedule_start is not None:
            return [schedule_start]
        return idx
