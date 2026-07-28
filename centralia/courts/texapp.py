"""Texas Court of Appeals.

Intermediate appellate court. Single ruling by one judge; the author comes from the signature block and the whole ruling is one opinion (district-court model).
"""

from __future__ import annotations

from statistics import median

from ._district import DistrictBase


class TexasCourtOfAppeals(DistrictBase):
    court_id = "texapp"
    court_label = "Texas Court of Appeals."
    # Unlike a trial-court order, these slips put the panel and opinion
    # announcement in a narrow, centered stack.  That geometry is not a
    # quotation: the ordinary line-pitch classifier still finds real quoted
    # material, while the district-wide both-margins rule would turn
    # "Before Justices ..." / "Memorandum Opinion by ..." into blockquotes.
    blockquote_by_indent = False

    def find_footnote_separator(self, page):
        sep = super().find_footnote_separator(page)
        if sep is None:
            return None
        # The Thirteenth District caption and the Fort Worth short-form
        # dispositions use full-measure horizontal shelves.  They can occur
        # low on page 1 and have smaller regular text below, but are not
        # footnote rules.  A Texas footnote separator is the conventional
        # two-inch (144pt) left rule; reject any shelf spanning most of the
        # text measure.
        for r in page.rects:
            if abs(r.get("top", 0) - sep) <= 2:
                if (r.get("x1", 0) - r.get("x0", 0)) > page.width * 0.5:
                    return None
        return sep

    @staticmethod
    def _name_after(text: str, cue: str) -> str | None:
        low = text.lower()
        at = low.find(cue)
        if at < 0:
            return None
        name = text[at + len(cue) :].strip().rstrip(".")
        return name if name and len(name.split()) <= 6 else None

    def _texas_author(self, all_segments):
        """Read the court's explicit opinion announcement.

        The corpus mixes traditional ``NAME, Justice`` bylines with the
        Thirteenth District's ``Memorandum Opinion by Justice NAME`` and
        ``Per Curiam Memorandum Opinion`` rows.  Prefer those declarations to
        DistrictBase's generic signature scan, which can otherwise promote a
        lawyer or trial judge mentioned near the end of an opinion.
        """
        lines = [
            self.line_plain_text(line).strip()
            for _p, seg, _kind in all_segments
            for line in seg
            if self.line_plain_text(line).strip()
        ]
        for text in lines:
            low = text.lower()
            if low.rstrip(".") == "per curiam" or (
                "per curiam" in low and "opinion" in low
            ):
                return "PER CURIAM"
            if low.startswith("opinion by:"):
                name = text.split(":", 1)[1].strip().rstrip(".")
                if name:
                    return name
            for cue, title in (
                ("memorandum opinion by chief justice ", "Chief Justice"),
                ("opinion by chief justice ", "Chief Justice"),
                ("memorandum opinion by justice ", "Justice"),
                ("opinion by justice ", "Justice"),
            ):
                name = self._name_after(text, cue)
                if name:
                    return f"{name}, {title}"
        for text in lines:
            low = text.rstrip(".").lower()
            if (
                low.endswith((", justice", ", chief justice"))
                and not low.startswith(
                    ("honorable ", "before ", "sitting:", "panel ")
                )
                and len(text.split()) <= 7
            ):
                return text.rstrip(".")
        # Traditional slips set the printed name immediately over the lone
        # judicial-title row at the right margin.
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].rstrip(".").lower() in ("justice", "chief justice"):
                name = lines[i - 1].strip()
                if name and len(name.split()) <= 6:
                    title = lines[i].rstrip(".")
                    return f"{name.title() if name.isupper() else name}, {title}"
        return None

    def find_authors(self, all_segments) -> list:
        # Fourth Court slips place the complete appellate caption, panel,
        # filing date, and disposition under a top "MEMORANDUM OPINION"
        # banner. That banner is headmatter, not the start of prose. The final
        # metadata rows can share a segment with the opening paragraph, so cut
        # the segment immediately after the disposition row.
        body_start = None
        has_opinion_by = any(
            self.line_plain_text(line).strip().lower().startswith("opinion by:")
            for _p, seg, _kind in all_segments[:16]
            for line in seg
        )
        if has_opinion_by:
            for i, (pno, seg, kind) in enumerate(all_segments[:16]):
                delivered = next(
                    (
                        j
                        for j, line in enumerate(seg)
                        if self.line_plain_text(line)
                        .strip()
                        .lower()
                        .startswith("delivered and filed:")
                    ),
                    None,
                )
                if delivered is None:
                    continue
                cut = delivered + 1
                while cut < len(seg):
                    text = self.line_plain_text(seg[cut]).strip()
                    letters = [c for c in text if c.isalpha()]
                    if letters and text == text.upper() and len(text) <= 90:
                        cut += 1  # disposition row
                        continue
                    break
                if cut < len(seg):
                    before, body = seg[:cut], seg[cut:]
                    replacement = []
                    if before:
                        replacement.append((pno, before, self.classify_segment(before)))
                    replacement.append((pno, body, self.classify_segment(body)))
                    all_segments[i : i + 1] = replacement
                    body_start = i + (1 if before else 0)
                elif i + 1 < len(all_segments):
                    body_start = i + 1
                break

        if body_start is None:
            has_court_banner = any(
                "court of appeals" in self.line_plain_text(line).strip().lower()
                for _p, seg, _kind in all_segments[:12]
                for line in seg
            )
            if has_court_banner:
                for i, (pno, seg, _kind) in enumerate(all_segments[:16]):
                    if (
                        pno == 1
                        and seg
                        and self._is_heading(seg[0])
                        and i + 1 < len(all_segments)
                    ):
                        # The slip's document-type banner closes its appellate
                        # caption. The authored prose begins in the following
                        # segment; keep the banner with the caption.
                        body_start = i + 1
                        break

        starts = super().find_authors(all_segments)
        author = self._texas_author(all_segments)
        # Override only with a court-authorship declaration.  An empty author
        # is preferable to guessing from a party/counsel name.
        self._district_author = author or ""
        self._district_author_source = "texas-announcement" if author else None
        return [body_start] if body_start is not None else starts

    def classify_document_type(self, all_segments, author_indices, n_pages):
        from ..models import DocType

        # Occasionally a docket download is a party's motion rather than a
        # disposition.  Require both the attorney sign-off and its service
        # certificate; neither phrase pair occurs in a judicial opinion.
        lows = [
            self.line_plain_text(line).strip().lower()
            for _p, seg, _kind in all_segments
            for line in seg
        ]
        if any(t.startswith("respectfully submitted") for t in lows) and any(
            "certificate of service" in t for t in lows
        ):
            return DocType.FILING
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def _rule_over_footnotes(self, page, rule_top) -> bool:
        """Texas draws full-width DOUBLED rules as caption-banner dividers in
        the headmatter ('… EDINBURG' ─── parties ─── 'ON APPEAL …' ───
        'MEMORANDUM OPINION'). The base test — smaller *median* text below —
        misfires here because the whole opinion body (12pt) is smaller than the
        bold 14–16pt caption banner, so the boundary rule reads as a footnote
        separator and swallows the opinion start.

        Decide on the line IMMEDIATELY below the rule instead: a real footnote
        rule has small, non-bold footnote text there; a banner divider has bold
        (and usually larger) banner text. Bold-below ⇒ not a footnote rule."""
        below = above = None
        for ln in page.extract_text_lines():
            chars = ln.get("chars") or []
            sizes = [c["size"] for c in chars if c.get("size")]
            if not sizes:
                continue
            sz = median(sizes)
            bold = any("Bold" in (c.get("fontname") or "") for c in chars)
            dy = ln["top"] - rule_top
            if 2 < dy <= 60 and (below is None or ln["top"] < below[0]):
                below = (ln["top"], sz, bold)
            elif -60 <= dy < -2 and (above is None or ln["top"] > above[0]):
                above = (ln["top"], sz, bold)
        if below is None:
            return False
        _, bsz, bbold = below
        if bbold:
            return False  # a bold caption-banner divider, not a footnote rule
        asz = above[1] if above else bsz + 1.0
        return bsz < asz - 0.75
