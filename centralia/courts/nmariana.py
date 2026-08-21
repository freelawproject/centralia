"""Supreme Court of the Commonwealth of the Northern Mariana Islands.

An E-FILED stamp block tops page 1 ('E-FILED / CNMI SUPREME COURT /
E-filed: … / Clerk Review: … / Filing ID / Case No / Judy Aldan') —
furniture, dropped and surfaced. A letterspaced decorative banner and a
'SLIP OPINION' label precede the caption; the byline is TITLE-FIRST with
a colon: 'C.J. CASTRO:' / 'J. MANGLONA:' and the body follows.
"""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme

_REV = ("C.J.", "J.", "J.P.T.")


class NorthernMarianaSupreme(AbbrevTitleSupreme):
    court_id = "nmariana"
    court_label = "Supreme Court of the Commonwealth of the Northern Mariana Islands."

    # TWO RULE POPULATIONS, NOTHING BETWEEN. Censused over every thin rule in
    # the corpus (assets/nmariana, 2026-08):
    #
    #     x0~70-130   w~140    162 rules   the separator: 144pt at the rail
    #     x0~140-150  w~320    104 rules   a CENTRED divider (mid = page mid
    #                                      ±2pt) drawn under the banner on the
    #                                      caption page and above the roster
    #
    # The centred divider was being chosen as the separator on 46 pages: its
    # x0 of ~142 sits just inside StateSupreme's left-quarter fence (153 on
    # this page size), and everything under it — 'SLIP OPINION / Cite as: … /
    # CHIEF JUSTICE ALEXANDRO C. CASTRO …' — was delivered as a '?' footnote
    # in 27 documents. The width cap splits the populations with 60pt of
    # clearance on either side; no genuine separator in the corpus is wider
    # than ~150.
    footnote_sep_max_width = 200
    abbrev_titles = (
        ("CJ.", "Chief Justice"),  # 'CASTRO, CJ.:' typo variant
    ) + AbbrevTitleSupreme.abbrev_titles

    def parse_author_line(self, text):
        # 'C.J. CASTRO:' — abbreviated title FIRST, all-caps surname, colon
        t = text.strip().rstrip(":").strip()
        for ab in _REV:
            if t.startswith(ab + " "):
                name = t[len(ab) :].strip()
                if (
                    name
                    and 1 <= len(name.split()) <= 3
                    and name == name.upper()
                    and all(
                        c.isalpha() or c in " -.'" for c in name
                    )
                ):
                    full = {"C.J.": "Chief Justice", "J.": "Justice",
                            "J.P.T.": "Justice Pro Tempore"}[ab]
                    return name, full, None
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if text.endswith(":") and self.parse_author_line(text) is not None:
            return text, ""
        return super()._byline_split(line)

    def page_lines(self, page):
        if not hasattr(self, "_cnmi_dropped"):
            self._cnmi_dropped = []
        lines = super().page_lines(page)
        if page.page_number != 1:
            return lines
        kept = []
        for l in lines:
            t = self.line_plain_text(l).strip()
            low = t.lower()
            if l.get("top", 0) < 130 and (
                low.startswith(("e-filed", "clerk review", "filing id", "case no"))
                or t == "CNMI SUPREME COURT"
                or (len(t.split()) <= 3 and l.get("top", 0) < 125 and not t.isupper())
            ):
                if t:
                    self._cnmi_dropped.append(t)
                continue
            kept.append(l)
        return kept

    def extract(self, pdf_path: str):
        self._cnmi_dropped = []
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages) -> None:
        """Flush the E-FILED stamp block onto the document BEFORE the
        completeness sweep.

        The sweep runs INSIDE ``super().extract()``, so adding the stamp to
        ``doc.dropped`` after that call returned was too late: every stamp row
        ('E-FILED / CNMI SUPREME COURT / E-filed: … / Clerk Review: … /
        Filing ID: … / Case No.: … / Judy Aldan') was reported unplaced on the
        four fixtures that carry one — 26 lines — while sitting in the Removed
        box the whole time.
        """
        extra = list(dict.fromkeys(getattr(self, "_cnmi_dropped", []) or []))
        if extra:
            doc.dropped = list(doc.dropped) + extra
        super()._sweep_residual(doc, source_pages)
