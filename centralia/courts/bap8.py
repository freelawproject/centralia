"""Bankruptcy Appellate Panel of the Eighth Circuit.

The Eighth Circuit clerk's own cover sheet, banner and all: 'United States
Bankruptcy Appellate Panel / For the Eighth Circuit' set in Old English Text
MT at 21pt and 14pt, then a centered Times column fenced by TYPED rules --
underscores mostly, and a row of hyphens between the two party blocks --
carrying the BAP number ('No. 24-6011'), the 'In re:' debtor block, the
parties with their ITALIC role lines ('Creditor - Appellant', 'Debtor -
Appellee') set right of the party name, 'Appeal from United States Bankruptcy
Court / for the District of Minnesota - Minneapolis', the submitted and filed
dates, and the panel roster ('Before SURRATT-STATES, NORTON, and JONES,
Bankruptcy Judges.') flush at the rail.

The opinion opens on the next page with a plain, non-bold byline at the rail
-- 'NORTON, Bankruptcy Judge.' / 'HASTINGS, Chief Judge.' / 'PER CURIAM.' --
over a body at 14pt/20.1pt leading, x0=72, first line indented to 108.
Footnotes sit under a 144pt rule at the rail, AT BODY SIZE.

Two of this court's styles appear in the corpus: the signed opinion (with a
signed dissent on one) and the short unsigned PER CURIAM. Both are reached by
the circuit family's form-based byline; the roster is rejected by its
``_NON_AUTHOR`` list, which is what the generic parser turned into a phantom
'surratt-states-and-norton' opinion.
"""

from __future__ import annotations

from typing import Optional

from ._circuit import FederalCircuitBase


class EighthCircuitBAP(FederalCircuitBase):
    court_id = "bap8"
    court_label = "Bankruptcy Appellate Panel of the Eighth Circuit."
    circuit_phrase = "bankruptcy appellate panel"
    body_baseline_x0 = 72.0

    # Three leadings, cleanly separated: quotations and footnotes at 16.1pt,
    # the body at 20.1pt, and 36-40pt between paragraphs. The base class's
    # 16/22/40 bands put the body itself in the block-quote band and a
    # quotation in the notice band -- which the body builder DROPS.
    gap_tight_max = 10.0
    gap_single_max = 18.0
    gap_double_max = 26.0

    # No running header: every continuation page opens with real body text at
    # top~75, and the folio ('-5-') sits in the bottom margin. The family's
    # 95pt page-2 cutoff would delete the byline and the first two lines of
    # every page after the first.
    page2_header_cutoff = 0.0

    # ------------------------------------------------------------ page folds
    def build_opinion(self, op_start, op_end, **kwargs):
        """Rejoin a block quote that a page break cut mid-sentence.

        The shared cross-page fold in ``add_para`` covers ordinary paragraphs
        only, so a quotation that runs off the foot of one page and resumes at
        the head of the next comes back as two blocks. That is exactly the
        split CLAUDE.md 7 forbids, and it is common here because a footnote
        zone can eat most of a sheet: logan_riffenburg's statutory quotation
        breaks after '... to an entity that' at the foot of page 14 and resumes
        with 'purchased ... such property ...' at the top of page 15.

        (bap1 carries the same method for the same reason; the natural home is
        the circuit family base, which is off limits in this pass.)
        """
        op = super().build_opinion(op_start, op_end, **kwargs)
        op.blocks = self._fold_quote_across_pages(op.blocks)
        return op

    def _fold_quote_across_pages(self, blocks) -> list:
        out = []
        for block in blocks:
            if (
                out
                and out[-1].kind == "blockquote"
                and block.kind == "blockquote"
                and block.page == (out[-1].page or 0) + 1
                and not self._ends_sentence(out[-1].text)
            ):
                # The arriving half keeps its own <pagenumber> marker inline,
                # exactly as the shared paragraph fold does.
                out[-1].text = (out[-1].text + " " + block.text).strip()
                continue
            out.append(block)
        return out

    @staticmethod
    def _ends_sentence(text: str) -> bool:
        """Does this block close a sentence? Only a quotation left hanging
        mid-sentence is a page-break casualty; a quotation that ends on its own
        full stop, or on a citation, is complete, and the block that follows it
        at the head of the next page is a NEW quotation, not its tail
        (scott_jencks p9 ends on '..., 235 N.W. 30, 32 (Iowa 1931).' and p10
        opens a fresh quote). A quote paragraph that ends properly and is
        followed by an ellipsis-led continuation also stays its own block --
        two paragraphs of one quote is what the page shows."""
        trimmed = text.rstrip()
        # A trailing footnote reference, with or without the brackets a court
        # puts round it, is not the sentence's last word.
        if trimmed.endswith("]"):
            trimmed = trimmed[:-1].rstrip()
        if trimmed.endswith("</footnotemark>"):
            trimmed = trimmed[: trimmed.rfind("<footnotemark>")].rstrip()
        if trimmed.endswith("["):
            trimmed = trimmed[:-1].rstrip()
        # Strip the inline style tags so a bold/italic run at the end of the
        # row does not hide the punctuation underneath it.
        plain, depth = [], 0
        for ch in trimmed:
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                plain.append(ch)
        return "".join(plain).rstrip(" \"'”’)").endswith((".", "?", "!"))

    # ------------------------------------------------------------ headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """One styled row per cover-sheet line, keeping its own alignment.

        The cover is a display block of centered one-line rows on TWO axes: the
        page center carries the banner, the docket, the party names and the
        typed rules, while every role line ('Debtor', 'Creditor - Appellant',
        'U.S. Trustee - Appellee') is centered 37pt right of it, on an axis of
        its own -- the same right-shifted-caption trap CLAUDE.md records for
        Maryland. Only the panel roster is real flush-left prose, and it is the
        one row that wraps.

        Rather than hard-code the offset, MEASURE the axes: a row that starts
        right of the rail and shares its midpoint with at least one other such
        row is sitting on a centering axis, so it is centered. That finds the
        page center and the role axis together, and leaves the roster (whose
        midpoint drifts with its own length, and which starts AT the rail) as
        the left-aligned prose it is.

        The shared ``line_alignment`` cannot be used here for two reasons: it
        caps a centered row's width at 55% of the sheet, so a long party name
        ('Richard N. Berkshire, also known as Richard Noble Berkshire') reads
        left; and it has no notion of a second axis, so every role line reads
        left and renders at the far margin, nowhere near the page's.
        """
        rows, dropped, lines = [], [], []
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                text = " ".join((l.get("text") or "").strip() for l in seg).strip()
                if text:
                    dropped.append(text)
                continue
            lines.extend(l for l in seg if (l.get("text") or "").strip())

        axes = self._centering_axes(lines)
        base_size = 14.0
        prev = None
        for line in lines:
            page = line.get("page_number") or 1
            tight = prev is not None and page == prev[0] and line["top"] - prev[1] <= 24.0
            size, _, _ = self.line_meta(line)
            mid = (line["x0"] + line["x1"]) / 2.0
            centered = line["x0"] > self.body_baseline_x0 + 12 and any(
                abs(mid - axis) <= 2.5 for axis in axes
            )
            # The roster is the only prose on the sheet and the only row that
            # wraps ('Before HASTINGS, Chief Judge, SURRATT-STATES and NORTON,'
            # / 'Bankruptcy Judges.'). It is one line of text, so fold the
            # continuation back into it (CLAUDE.md 7) instead of orphaning the
            # bench title on a row of its own. A centered display row is never
            # folded: on this cover each one is its own item.
            if (
                tight
                and not centered
                and rows
                and isinstance(rows[-1], dict)
                and rows[-1].get("align") == "L"
            ):
                rows[-1]["html"] = (
                    rows[-1]["html"] + " " + self.line_inline_text(line)
                ).strip()
                prev = (page, line["top"])
                continue
            # Keep the page's rhythm: the cover is set double (32.2pt on a
            # 16.1pt line) except where two rows belong together ('Submitted:'
            # over 'Filed:'), which are consecutive.
            if prev is not None and not tight:
                rows.append("")
            prev = (page, line["top"])
            rows.append(
                {
                    "__hm__": True,
                    "html": self.line_inline_text(line),
                    "rel": round(size / base_size, 3),
                    "align": "C" if centered else "L",
                }
            )
        return {"court": self.court_label, "summary": rows, "dropped": dropped}

    def _centering_axes(self, lines) -> list:
        """Midpoints shared by two or more indented headmatter rows -- the
        caption's centering axes, measured off the page instead of assumed."""
        mids = sorted(
            (line["x0"] + line["x1"]) / 2.0
            for line in lines
            if line["x0"] > self.body_baseline_x0 + 12
        )
        axes, group = [], []
        for mid in mids:
            if group and mid - group[0] > 2.5:
                if len(group) > 1:
                    axes.append(sum(group) / len(group))
                group = []
            group.append(mid)
        if len(group) > 1:
            axes.append(sum(group) / len(group))
        return axes

    # ------------------------------------------------------------- footnotes
    def find_footnote_separator(self, page) -> Optional[float]:
        """This court sets its footnotes at BODY size (14pt), so the shared
        discriminator -- footnote-sized text directly below the rule -- can
        never fire, and that is where roy_arrieta's 31 footnotes went.

        Identify the rule by its own geometry instead: exactly 144pt wide at the
        body rail. Across the ten fixtures that width is drawn nowhere else --
        the cover sheet's rules are TYPED underscores and hyphens, not drawn
        objects, and the only other drawn hairlines in the corpus are three
        short citation underlines of 26-56pt and two of 138-142pt.

        Deliberately NO position bound. The family's 'bottom two thirds' test,
        and even a head-band floor, lose a footnote zone that has grown up the
        sheet: a dissent's string-cite footnotes fill page 13 of
        logan_riffenburg entirely, putting the rule at top=86 ABOVE that page's
        first line, and page 14's at top=135. With the family's test both pages
        read as body, which is how a dozen footnote paragraphs came back as
        block quotes of the dissent.
        """
        cands = [
            r
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2
            and abs((r["x1"] - r["x0"]) - 144.0) <= 2.0
            and abs(r["x0"] - self.body_baseline_x0) <= 4.0
        ]
        return min(c["top"] for c in cands) if cands else None
