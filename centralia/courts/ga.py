"""Supreme Court of Georgia."""

from __future__ import annotations

from ._statesupreme import StateSupreme


class GeorgiaSupreme(StateSupreme):
    court_id = "ga"
    court_label = "Supreme Court of Georgia."
    author_titles = ("Justice", "Chief Justice", "Presiding Justice")
    # Page numbers print as bare numbers between paragraphs — fold them into
    # page-break markers so the wrapped paragraphs rejoin.
    fold_page_numbers = True
    # Georgia's body is single-spaced (~16pt line gap) with a wide left margin
    # (baseline x0≈126, paragraphs indented to ≈162). The default thresholds
    # (tuned for double-spaced, baseline-72 courts) misread the ~16pt gap as a
    # 'notice' and split every line. Retune so the body reads as 'body' and is
    # split on the paragraph indent.
    gap_tight_max = 11
    gap_single_max = 14
    gap_double_max = 27
    body_baseline_x0 = 126.0  # base splits paragraphs at body_baseline_x0+28
    # Georgia prints a small publication advisory at the top. It is removed by
    # extract_headmatter as a contiguous NOTICE:-led block, not by font size:
    # later provenance rows ("On Appeal from", lower-court number, "Decided")
    # are also small print and must remain.
    notice_max_size = None
    # ...but that block is anchored on its 'NOTICE:' opening line, and Georgia
    # prints it from top≈20 — above the family's 32pt top margin. The anchor was
    # being filtered out before extract_headmatter ever saw it, so the block
    # went unrecognised and its remaining four lines landed in the headmatter,
    # opening mid-sentence at 'Rule 27, the Court's reconsideration'. Across the
    # whole corpus nothing above 32 is anything BUT this advisory.
    margin_top = 16
    # The footnote separator is a right-shifted ~324pt rule at x0≈162 (aligned
    # with the indented body column, not the page's left quarter).
    footnote_sep_x0_max = 170.0

    def find_footnote_separator(self, page):
        # Georgia's separator is a fixed 4.5-inch hairline from x=162 to
        # x=486. Long notes can occupy most of a page, placing that rule above
        # the StateSupreme family's midpoint cutoff. The template geometry,
        # not its vertical position, is the reliable boundary.
        for rule in list(page.rects) + list(page.lines):
            if (
                abs(rule.get("height", 0)) < 2
                and abs(rule.get("x0", 0) - 162.0) <= 1
                and abs(rule.get("x1", 0) - 486.0) <= 1
            ):
                return rule["top"]
        return None

    def detect_footnote_label(self, line):
        label = super().detect_footnote_label(line)
        if label is None:
            return None
        chars = line.get("chars") or []
        following = next(
            (
                char
                for char in chars[len(label) :]
                if (char.get("text") or "").strip()
            ),
            None,
        )
        if not chars or following is None:
            return None
        # A Georgia label is genuinely superscripted (8.5pt before 10pt note
        # prose). A body line beginning with a year can otherwise look "small"
        # if one later glyph on that line has an anomalous larger bbox.
        if chars[0].get("size", 0) > following.get("size", 0) - 1:
            return None
        return label

    def extract(self, pdf_path):
        """Georgia issues two body templates and the constants above only fit
        one of them.

        The common slip (47 of 50 in the corpus) sets the body single-spaced at
        a 16pt lead on a wide left margin. Disciplinary opinions set it
        DOUBLE-spaced at 36pt from a 72pt margin, with quotations single-spaced
        at 18pt between. Read against the single-spaced bands, a 36pt body
        exceeds ``gap_double_max`` and classifies as 'spaced' — one block per
        line, 494 of them for one opinion — while an 18pt quotation lands in
        the body band and never becomes a quote.

        So the bands are taken from the document's own dominant leading rather
        than assumed. Detection is the modal line gap, which separates the two
        templates cleanly (36 against 16) with nothing in between."""
        lead = self._ga_body_lead(pdf_path)
        if lead is not None and lead >= 30:
            # Double-spaced: quotes sit at half the body lead, so the single
            # band has to clear 18 while the body band clears 36.
            self.gap_tight_max = 13
            self.gap_single_max = 26
            self.gap_double_max = 45
            self.body_baseline_x0 = 72.0
        return super().extract(pdf_path)

    @staticmethod
    def _ga_body_lead(pdf_path):
        """Modal gap between consecutive body lines, or None."""
        from collections import Counter

        import pdfplumber

        gaps = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in (pdf.pages[2:5] or pdf.pages[:1]):
                    lines = [
                        l
                        for l in page.extract_text_lines()
                        if l["top"] > 80 and (l["text"] or "").strip()
                    ]
                    for a, b in zip(lines, lines[1:]):
                        d = round(b["top"] - a["top"])
                        if 5 < d < 60:
                            gaps.append(d)
        except Exception:
            return None
        return Counter(gaps).most_common(1)[0][0] if gaps else None

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        ordered = sorted(
            (
                line
                for seg in headmatter_segs
                for line in seg
                if (line.get("text") or "").strip()
            ),
            key=lambda line: (
                (line.get("chars") or [{}])[0].get("page_number", 1),
                line["top"],
                line["x0"],
            ),
        )
        notice_ids = set()
        start = next(
            (
                i
                for i, line in enumerate(ordered)
                if (line.get("text") or "").strip().startswith("NOTICE:")
                or (
                    "rule 27" in (line.get("text") or "").strip().lower()
                    and "reporter of decisions"
                    in " ".join(
                        (candidate.get("text") or "").strip().lower()
                        for candidate in ordered[i : i + 3]
                    )
                )
            ),
            None,
        )
        if start is not None:

            def _size(line):
                sizes = [c["size"] for c in (line.get("chars") or []) if c.get("size")]
                return min(sizes) if sizes else 0.0

            notice_ids.add(id(ordered[start]))
            previous = ordered[start]
            notice_size = _size(ordered[start])
            continuation_only = "rule 27" in (ordered[start].get("text") or "").lower()
            for line in ordered[start + 1 :]:
                # A continuation-only PDF can enter here at “Rule 27” after
                # the opening NOTICE line has already been separated. The
                # boilerplate ends at “official text”; remove the complete
                # continuation regardless of its small-print size.
                line_low = (line.get("text") or "").strip().lower()
                if "official text" in line_low:
                    notice_ids.add(id(line))
                    break
                if continuation_only:
                    notice_ids.add(id(line))
                    previous = line
                    continue
                # The advisory is one tightly-led block. A large vertical gap
                # ends it even if the next caption row happens to use small
                # type too.
                if line["top"] - previous["top"] > 22:
                    break
                # ...and so does a jump back to full type. The banner ('In the
                # Supreme Court of Georgia') sits only ~11pt under the last
                # advisory line — inside the gap window — but is set at 15pt
                # against the advisory's 8pt, so on the gap test alone it was
                # swept into the notice and removed with it.
                if notice_size and _size(line) > notice_size + 1.0:
                    break
                notice_ids.add(id(line))
                previous = line

        notice = [
            (line.get("text") or "").strip()
            for line in ordered
            if id(line) in notice_ids
        ]
        kept = [
            [line for line in seg if id(line) not in notice_ids]
            for seg in headmatter_segs
        ]
        kept = [seg for seg in kept if seg]

        result = super().extract_headmatter(kept, page1_rules)
        if notice:
            result.setdefault("dropped", []).append(" ".join(notice))

        # Pull the retained provenance rows into the document metadata as well
        # as leaving them in the styled headmatter.
        seen_appeal_source = False
        for seg in kept:
            for line in seg:
                text = (line.get("text") or "").strip()
                if not text:
                    continue
                if text.startswith("On Appeal from "):
                    result["history"] = text
                    result["lowercourt"] = text.removeprefix("On Appeal from ")
                    seen_appeal_source = True
                elif text.startswith("Decided:"):
                    result["decisiondate"] = text.removeprefix("Decided:").strip()
                elif text.startswith("No. "):
                    number = text.removeprefix("No. ").strip()
                    if seen_appeal_source:
                        result["otherdocket"] = number
                    elif "docketnumber" not in result:
                        result["docketnumber"] = number
        return result
