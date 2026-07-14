"""United States District Court, Western District of Wisconsin.

CM/ECF filing — a single ruling by one judge. The shared district base takes the
author from the signature block (or an opening byline / 'Present:' minute line)
and treats the whole ruling as one opinion; the CM/ECF header band (top margin)
is dropped.

Three wiwd-specific tweaks:

  * A short, one-page order signs at the very bottom of the page ('BY THE COURT:'
    / '/s/' / 'WILLIAM M. CONLEY' / 'District Judge' at top≈700-744). The default
    ``margin_bottom`` of 725 clipped the name and title, so the signature author
    was lost (and a body line wrapping into the bottom margin was dropped too).
    The bottom margin is lowered to keep the signature and any low body line.
  * Re-including that band re-admits the bare page-number footer ('1', '2', ...)
    that sits in the same y-band as the signature. It can't be separated by
    position, so it is dropped by CONTENT — a bare integer in the bottom band —
    and routed to ``dropped``.
  * The opinion start. wiwd captions carry the document-type label *inline*
    ('Plaintiff, ORDER' / 'Petitioner, OPINION AND ORDER'), and the ruling then
    repeats a bare 'ORDER' / 'OPINION' as a section heading above the decretal
    paragraphs. The shared base starts the opinion at the first such heading,
    which buries the entire discussion (everything before the heading) in the
    headmatter. Instead, the opinion here starts at the first substantive-prose
    line *after* the caption's party designation ('Defendant.' / 'Respondents.'),
    so the discussion stays in the opinion and the caption stays headmatter.
"""

from __future__ import annotations

from ._district import DistrictBase

# Party designations that close the caption block. A line whose text before any
# comma is one of these (singular/plural) is the caption's party-role line; the
# opinion body begins at the first real sentence after it.
_PARTY_DESIGNATIONS = frozenset(
    {
        "plaintiff",
        "plaintiffs",
        "defendant",
        "defendants",
        "petitioner",
        "petitioners",
        "respondent",
        "respondents",
        "appellant",
        "appellants",
        "appellee",
        "appellees",
        "movant",
        "movants",
        "intervenor",
        "intervenors",
        "claimant",
        "claimants",
        "debtor",
        "debtors",
        "complainant",
        "complainants",
        "relator",
        "relators",
    }
)


class WesternDistrictOfWisconsin(DistrictBase):
    court_id = "wiwd"
    court_label = "United States District Court, Western District of Wisconsin."

    # The signature 'District Judge' line sits as low as top≈744; keep it (and a
    # body line wrapping to top≈727) rather than the default 725 cutoff.
    margin_bottom = 756.0
    # Ordered-relief lists hang their continuations at x0=126 — exactly the
    # default deep-indent boundary (72 + 1.5*36), so every item was split from
    # its own wrapped line. Raise the step past the hang; real quotes (144+)
    # still clear it.
    indent_step = 40
    # The signature stack ('JAMES D. PETERSON' / 'District Judge') is a
    # short-line stack — one line per block, so the harvest lifts the name
    # and title as separate lines.
    split_line_stacks = True

    # Bottom band (top > height - this) where the bare page-number footer sits.
    _footer_band_pt = 70.0

    def split_body_paragraphs(self, seg):
        """Ordered-relief lists are single-spaced (~14pt) with a double gap
        (~26pt) between items, and the whole run lands in ONE kept-'notice'
        segment — the base indent splitter can't see the item boundaries, so
        split on the gap first, then apply the indent logic within each item.
        Double-spaced body segments have uniform gaps and pass through
        unsplit."""
        if not seg:
            return []
        from statistics import median

        gaps = [b["top"] - a["top"] for a, b in zip(seg, seg[1:])]
        med = median(gaps) if gaps else 0.0
        groups = [[seg[0]]]
        for line, g in zip(seg[1:], gaps):
            if med and g > 1.4 * med:
                groups.append([line])
            else:
                groups[-1].append(line)
        return [p for grp in groups for p in super().split_body_paragraphs(grp)]

    def extract(self, pdf_path: str):
        self._wiwd_footer = []
        doc = super().extract(pdf_path)
        extra = sorted(set(self._wiwd_footer), key=lambda t: (len(t), t))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        return doc

    def page_lines(self, page):
        lines = super().page_lines(page)
        cutoff = page.height - self._footer_band_pt
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            if l.get("top", 0) > cutoff and t.isdigit() and len(t) <= 4:
                self._wiwd_footer.append(t)  # bare page-number footer
            else:
                kept.append(l)
        return kept

    # ------------------------------------------------------------ opinion start
    def _is_party_designation(self, line) -> bool:
        """A caption party-role line ('Defendant.' / 'Plaintiff, ORDER' /
        'Respondents.') — the role word, before any comma, is a designation."""
        t = self.line_plain_text(line).strip()
        if not t:
            return False
        head = t.split(",", 1)[0].strip().rstrip(".").lower()
        return head in _PARTY_DESIGNATIONS

    def _is_prose_line(self, line) -> bool:
        """A real body sentence, as opposed to caption material (party names,
        designations, dockets, the court banner, a bare section heading). Body
        sentences carry several fully-lowercase function/verb words ('is', 'the',
        'has', 'order'); a caption party line like 'E. EMMERICH, Warden, and'
        carries at most one, and all-caps names/headings carry none."""
        t = self.line_plain_text(line).strip()
        if len(t) < 25 or not t[:1].isalpha():
            return False
        if t.lower().startswith("v. "):
            return False
        lower_words = sum(1 for w in t.split() if w.isalpha() and w.islower())
        return lower_words >= 2

    def find_authors(self, all_segments) -> list:
        # Author: inherited (signature block / 'Present:' line / byline / caption).
        self._district_author = (
            self._signature_author(all_segments)
            or self._present_author(all_segments)
            or self._byline_author(all_segments)
            or self._caption_judge(all_segments)
        )
        # Opinion start: the first body sentence after the caption's party
        # designation. When the designation and that sentence land in one segment
        # (the gap between them is too small to split), divide it so the
        # designation stays headmatter and the sentence opens the opinion.
        seen_designation = False
        for i, (pg, seg, kind) in enumerate(all_segments):
            for li, line in enumerate(seg):
                if self._is_party_designation(line):
                    seen_designation = True
                    continue
                if seen_designation and self._is_prose_line(line):
                    if li > 0:
                        all_segments[i] = (pg, seg[:li], kind)
                        all_segments.insert(i + 1, (pg, seg[li:], kind))
                        return [i + 1]
                    return [i]
        # No caption designation (an unusual layout): fall back to the base's
        # heading / first-body detection.
        return super().find_authors(all_segments)
