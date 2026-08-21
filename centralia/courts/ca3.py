"""United States Court of Appeals for the Third Circuit."""

from __future__ import annotations

from collections import Counter

import pdfplumber

from ..base import BaseExtractor
from ..models import Block
from ._circuit import FederalCircuitBase
from .generic import _is_name


class ThirdCircuit(FederalCircuitBase):
    court_id = "ca3"
    court_label = "United States Court of Appeals for the Third Circuit."
    circuit_phrase = "third circuit"

    # Headmatter criteria: typed rules; 'Before:' roster runs the argued/decided dates on the same row.
    parse_criteria_enabled = True
    criteria_lift_publication = True
    counsel_label_trails = True
    # CA3 runs the roster onto the submission row and the origin onto the
    # caption's last row; both splits now live in the family base.
    roster_can_share_row = True
    history_can_share_row = True

    # CA3 usually prints no appearances at all — court, docket, case name,
    # prior history, then the roster or a submission/filing date. Where it DOES
    # print them, the identifying label comes AFTER the names:
    #     Donovan J. Cocas  Laura S. Irwin  OFFICE OF UNITED STATES ATTORNEY...
    #     Counsel for Appellee
    # so the block is claimed backwards from its label (see
    # ``counsel_label_trails``). Everything else stays unrecorded.

    # CA3 runs the submission line and the panel roster together on ONE row:
    #   'Submitted Pursuant to Third Circuit LAR 34.1(a) June 5, 2026
    #    Before:  BIBAS, CHUNG, and ROTH, Circuit Judges'
    # Every other circuit opens the roster at the start of its own row, so the
    # shared opener test never sees this one and the panel goes unread.
    # The qualifiers CA3 puts in front of the bench word, so the clause is
    # taken from its start ('Magistrate Judge ...') and not from 'Judge'.
    _BENCH_QUALIFIERS = (
        "district", "magistrate", "circuit", "chief", "senior", "bankruptcy",
        "u.s.", "us", "united", "states", "honorable",
    )

    @staticmethod
    def _split_lower_docket(text):
        """(forum, lower docket, lower judge) for CA3's own history line.

        CA3 states all three inline and in two different arrangements:

            ... for the Middle District of Pennsylvania
                (District Court No.: 3:23-cr-00095-001)
                District Judge: Honorable Julia K. Munley
            ... the U.S. District Court, D.N.J.
                Magistrate Judge Cathy L. Waldor, No. 2:17-cv-07386

        The shared reader knows the bracketed CA1 judge and the CA11 'D.C.
        Docket No.' marker, neither of which CA3 prints, so it left the whole
        sentence in ``prior_history``. Read the parenthesis and the bench
        clause out of it first, then hand the remainder to the family reader
        for anything it still recognises."""
        docket = judge = None
        # The parenthesised docket — '(District Court No.: 3:23-cr-00095-001)'.
        open_at = text.find("(")
        if open_at >= 0:
            close_at = text.find(")", open_at)
            inner = (text[open_at + 1 : close_at] if close_at > open_at
                     else text[open_at + 1 :]).strip()
            if "No" in inner and any(c.isdigit() for c in inner):
                docket = inner
                end = close_at + 1 if close_at > open_at else len(text)
                text = (text[:open_at] + " " + text[end:]).strip()
        # The bench clause — from its qualifier to the comma that closes it,
        # or to the end of the line where nothing closes it.
        tokens = text.split()
        for i, tok in enumerate(tokens):
            if tok.strip(".,:;").lower() != "judge":
                continue
            start = i
            while start and tokens[start - 1].strip(".,:").lower() \
                    in ThirdCircuit._BENCH_QUALIFIERS:
                start -= 1
            end = len(tokens)
            for j in range(i + 1, len(tokens)):
                if tokens[j].endswith(","):
                    end = j + 1
                    break
            judge = " ".join(tokens[start:end]).strip(" ,")
            tokens = tokens[:start] + tokens[end:]
            text = " ".join(tokens)
            break
        forum, more_docket, more_judge = FederalCircuitBase._split_lower_docket(text)
        # What is left can still carry a bare 'No. 2:17-cv-07386'.
        if docket is None and more_docket is None:
            at = forum.find("No. ")
            if at > 0 and any(c.isdigit() for c in forum[at:]):
                docket = forum[at:].strip(" ,.")
                forum = forum[:at].strip(" ,")
        return forum.strip(" ,"), docket or more_docket, judge or more_judge

    def _tail_kind(self, text):
        """CA3 tags the advocate who argued inside the appearance itself —
        'Joel S. Sansone (Argued) Law Offices of Joel Sansone 603 Stanwix
        Street ...', 'Christian T. Haugsby [ARGUED]'. That marker is the
        court's own announcement that the row is an appearance, and it is the
        only announcement the first entry of a block carries: the 'Counsel for
        Appellant' label comes at the END of the entry, not the start."""
        flat = " ".join(text.split()).lower()
        if "(argued)" in flat or "[argued]" in flat:
            return "counsel"
        return super()._tail_kind(text)

    # Published CA3 opinions use a narrow x≈144..468 body measure. The federal
    # default x≈72 makes ordinary prose appear deeply indented and therefore
    # quote-like.
    body_baseline_x0 = 144.0
    # The justified right measure, filled in per document by
    # ``_measure_body_template`` (the corpus runs at both x1≈468 and x1≈540).
    body_right_rail = None
    gap_tight_max = 12.0
    # Main text leads at ~17pt; genuinely single-spaced quotations are tighter.
    gap_single_max = 16.0
    gap_double_max = 38.0
    blockquote_by_indent = True
    # CA3 prints NO running header — not on any page of the corpus (no line
    # above 110pt repeats on even three continuation pages in any of the 50
    # fixtures). The family default drops everything above 95pt on pages 2+ to
    # clear the circuits that DO carry a centered 'No. <docket>' head; here that
    # band is body. CA3 sets two measures — a bound one whose continuation pages
    # open at ~146pt (the cutoff is harmless) and a slip one that opens at ~74pt
    # — and on the slip measure the cutoff silently ate the first two lines of
    # every page: body prose, section heads, panel rosters, and whole bylines
    # ('HARDIMAN, Circuit Judge.'). Lowered below ``margin_top`` (39) so the
    # page edge alone bounds the band.
    page2_header_cutoff = 30.0
    dedupe_footnote_labels = False

    def prepare_document(self, pdf):
        """Keep page-top prose when CA3 has no repeated running header.

        The circuit family reserves the first 95 points of continuation pages
        for a docket header.  Some CA3 opinions instead continue body text at
        the top of page 2; only the panel roster form is a reliable header
        signal for this corpus.
        """
        self._drop_page2_header = False
        if len(pdf.pages) > 1:
            top = [
                (line.get("text") or "").strip().lower()
                for line in pdf.pages[1].extract_text_lines()
                if line.get("top", 0) < self.page2_header_cutoff
            ]
            self._drop_page2_header = any(line.startswith("before:") for line in top)

    def filter_margins(self, obj):
        # CA3's nonprecedential-opinion marker may carry an asterisk footnote
        # below the normal bottom margin on page 1.
        if obj.get("page_number", 1) == 1 and obj.get("top", 0) > self.margin_bottom:
            return True
        if (
            obj.get("page_number", 1) > 1
            and obj.get("top", 0) < self.page2_header_cutoff
            and not getattr(self, "_drop_page2_header", False)
        ):
            return BaseExtractor.filter_margins(self, obj)
        return super().filter_margins(obj)

    def find_footnote_separator(self, page):
        """CA3's 2-inch footnote rule, wherever this document's template sets it.

        The band below is the BOUND measure's rule: at the body rail x≈144, and
        indented from it at x0=162 in some chambers, which is why the window
        reaches right as well.

        Everything else is left to the shared chain, which reads the WIDTH the
        court draws instead of predicting an x0. That matters here because CA3
        prints on two measures and the rule travels with the measure. Measured
        over the 53-document corpus: on every one of the 22 pages where this
        band answers None and the shared chain answers a y, the shape it takes
        is exactly 144.0pt wide, and it sits either at x0=180 — the bound
        measure's rule, drawn one paragraph indent right of its 144pt rail
        (mccarthy pp. 3, 6, 8, 10, 12, 13; ibew pp. 16-18) — or at x0=72, which
        is the SLIP measure's own rail (evans 7 pages, kovalev 2, bankole,
        givey, yew, thompson). There is no third population, and every one of
        the 22 opens a raised label.

        WHAT USED TO BE HERE, AND WHY IT IS GONE: a fallback that took the
        first line below 0.55 x page height whose ``detect_footnote_label``
        answered anything, with no separator of any kind. A footnote requires a
        separator. That fallback opened a zone on 589 of this corpus's pages;
        566 of them held nothing but the printed page folio, which then shipped
        as a footnote whose entire text was its own label — 33 of the 35 phantom
        footnotes in the whole 6,707-document corpus were these. On three more
        it took a CENTRED SECTION NUMBER ('1' under 'A' under 'III', set at
        body size on the page axis, indistinguishable from a folio by that
        test) and swallowed the rest of the page's prose into a fake note:
        mcgoveran pp. 5-6, prospect_capital p14. And where it did land on a
        real note it was worse than the rule it stood in for, because it starts
        at the LABEL: mccarthy p12 draws its separator at y=357.8 and the
        fallback answered 530.1, leaving footnote 7 in the body between them.
        """
        separator = self._sep_at(
            page, self.body_baseline_x0 - 4, self.body_baseline_x0 + 24
        )
        if separator is not None:
            return separator
        separator = BaseExtractor.find_footnote_separator(self, page)
        if separator is not None:
            return separator
        # THE UNRULED CAPTION STAR NOTE — a matched pair with no separator
        # anywhere: naacp_delaware rules nothing on any of its six pages, sets
        # 'NONPRECEDENTIAL OPINION*' in the caption and '*This is not an
        # opinion of the full Court ...' at the very foot of page 1. Nothing
        # like the removed fallback above: star family only (the folio
        # phantoms were DIGITS), the caption page only, the bottom quarter
        # only, and only with the TRAILING star reference printed above it —
        # a note without its mark stays unread, exactly as before.
        if page.page_number == getattr(self, "_caption_pno", 1):
            lines = page.extract_text_lines()
            has_ref = any(
                (l.get("text") or "").rstrip().endswith(("*", "†", "‡"))
                and l["top"] < page.height * 0.75
                for l in lines
            )
            if has_ref:
                for l in lines:
                    t = (l.get("text") or "").strip()
                    if (
                        l["top"] > page.height * 0.75
                        and len(t) > 2
                        and t[0] in "*†‡"
                        and (t[1] == " " or t[1].isalpha())
                    ):
                        return l["top"] - 1.0
        return None

    def matches_expected_layout(self, pdf):
        """Accept CA3's abbreviated first-page court banner.

        Some opinions spell out ``United States Court of Appeals`` while
        others use ``U.S. Court of Appeals`` and wrap ``CIRCUIT`` onto the
        next line.  The shared circuit check handles the former, but its
        same-line phrase check misses this valid CA3 variant.
        """
        if super().matches_expected_layout(pdf):
            return True
        if not pdf.pages:
            return False
        text = " ".join(
            (line.get("text") or "")
            for line in pdf.pages[0].extract_text_lines()
        ).lower()
        return "u.s. court of appeals" in text and "third" in text and "circuit" in text

    def detect_printed_folio(self, page, lines):
        """CA3 sets its folio just below the text block rather than down in the
        sheet's bottom margin — top≈667 on a 792pt page, and ≈621 once a
        separate writing starts (each writing is paginated as its own slip
        document and restarts at 1). Both sit well inside the shared detector's
        ``height - 85`` edge band, so the folio is never registered and the bare
        number falls through into the opinion body as a paragraph.

        Read it by structure instead of by distance from the paper's edge: the
        last line on the page, standing alone as a centered number, cut off from
        the text above it by a gap wider than the court's double space."""
        folio = super().detect_printed_folio(page, lines)
        if folio is not None:
            return folio
        try:
            raw = page.filter(
                lambda o: o.get("upright", True) is not False
            ).extract_text_lines()
        except Exception:
            return None
        if len(raw) < 2:
            return None
        last = raw[-1]
        if self._page_number_value((last.get("text") or "").strip()) is None:
            return None
        if self.line_alignment(last, page.width) != "C":
            return None
        # POSITION, not the gap above it. This used to require the folio to
        # stand more than gap_double_max (38pt) below the line above it, which
        # is a paragraph-spacing constant asked of page furniture. CA3 prints
        # the folio at a CONSTANT top=668.3 on every page, so whether the test
        # passed depended only on where that page's text block happened to end
        # on the 17.2pt body grid: 20 of defense_distributed's 39 pages cleared
        # it and 19 did not, for an identical folio. A folio that fails to
        # register is never filtered — both is_zone_folio and
        # is_registered_folio open with `if folio is None: return False` — so
        # the bare number survives into the footnote zone and becomes a
        # footnote whose label and whose entire text are the page number.
        # 33 such phantoms existed, every one of the corpus's total.
        # international_brotherhood puts its folio one ordinary line (15.0pt)
        # below the block, which no gap threshold could ever admit.
        #
        # What identifies it is what it IS: the last line on the page, standing
        # alone, centred, and nothing but a bare integer. All four already hold
        # by the time we are here.
        return self._page_number_value((last.get("text") or "").strip())

    def page_lines(self, page):
        """Measure each line's top from its BODY glyphs, ignoring superscripts.

        A superscript footnote marker is set above the body baseline, so
        pdfplumber reports the whole line as starting ~1.5pt higher than its
        neighbours. At CA3's 13pt leading that is enough to drop the gap under
        ``gap_tight_max`` (11.4 against a 12.0 threshold), which reads as a
        single-spaced run: the paragraph splits at the marker, the two-line
        fragment classifies as a notice and is discarded from the body
        (rti_restoration p.31, 'under the MPPAA.1'). A footnote marker must
        never break a paragraph, so take the top from the line's dominant
        size and leave everything else — chars included — untouched."""
        lines = super().page_lines(page)
        for line in lines:
            chars = line.get("chars") or []
            if len(chars) < 2:
                continue
            size, _font, _bold = self.line_meta(line)
            body = [
                c
                for c in chars
                if abs(round(c.get("size", 0), 1) - size) < 0.6
                and (c.get("text") or "").strip()
            ]
            if not body or len(body) == len(chars):
                continue
            top = min(c["top"] for c in body)
            if 0 < top - line["top"] < 3:
                line["top"] = top
        return lines

    def classify_paragraph(self, lines):
        """Promote the court's short, fully-bold centered section rows."""
        if (
            len(lines) == 1
            and self.line_alignment(lines[0], getattr(self, "_page1_width", 612.0))
            == "C"
            and self._line_all_bold(lines[0])
        ):
            return "heading"
        return super().classify_paragraph(lines)

    def _byline_split(self, line):
        """Accept CA3's all-caps, punctuation-free byline variant — and reject
        the closing 'BY THE COURT,' of an order, which is a SIGNATURE."""
        found = super()._byline_split(line)
        if found is not None:
            return None if self._is_signature_column(line) else found
        text = (line.get("text") or "").strip()
        if "," not in text:
            return None
        name, title = (part.strip() for part in text.split(",", 1))
        if _is_name(name) and title.upper() == "CIRCUIT JUDGE":
            return text, ""
        return None

    def _is_signature_column(self, line) -> bool:
        """True for a 'BY THE COURT,' / 'PER CURIAM' line set in the RIGHT-hand
        signature column rather than at the body rail.

        A byline OPENS a body: it starts at the left rail with the opinion's
        first sentence running on from it. CA3's orders close instead with a
        conformed signature stacked in the right half of the measure —
        'BY THE COURT,' over 's/ <Name>' over the bench title, above a drawn
        signature rule. Read as a byline it becomes the only 'opinion' in the
        document, and the order's actual text is stranded in the headmatter
        (schuster_1, jerome_brown, whittaker_clark_1)."""
        text = (line.get("text") or "").strip().lower()
        if not text.startswith(("by the court", "per curiam")):
            return False
        # A byline starts AT the body rail (or one indent in). The signature
        # column is tabbed a full inch or more right of it — x0≈288 on the
        # 72pt measure, ≈369 on the 108pt one.
        return line.get("x0", 0) > self.body_baseline_x0 + 72

    def _split_segments_at_bylines(self, all_segments):
        """Also cut a segment immediately AFTER a 'Present:' panel roster.

        An order sets its roster only ~35pt above the first line of the order
        itself — inside the court's double space — so the two arrive as one
        segment and the roster (headmatter) cannot be told from the order text
        (body). Splitting here lets ``_percuriam_start`` open the body at the
        line after the roster instead of at the signature further down."""
        out = []
        for page_no, seg, kind in super()._split_segments_at_bylines(all_segments):
            marks = (self._roster_end(seg), self._order_title_index(seg))
            cuts = sorted({m + 1 for m in marks if m is not None and m + 1 < len(seg)})
            if not cuts:
                out.append((page_no, seg, kind))
                continue
            bounds = [0] + cuts + [len(seg)]
            for a, b in zip(bounds, bounds[1:]):
                sub = seg[a:b]
                if sub:
                    out.append((page_no, sub, self.classify_segment(sub)))
        return out

    def _order_title_index(self, seg):
        """Index of a centered 'ORDER …' title inside a segment, or None.

        A clerk's order runs its title straight into its text with no extra
        space, so title and order arrive as one segment (and, on a one-page
        order, the caption's closing lines come with them). Cut on the turn
        from centered title to left-aligned text."""
        width = getattr(self, "_page1_width", None) or 612.0
        for j, line in enumerate(seg[:-1]):
            if not self.line_plain_text(line).strip().upper().startswith("ORDER"):
                continue
            if self.line_alignment(line, width) != "C":
                continue
            if self.line_alignment(seg[j + 1], width) == "C":
                continue
            return j
        return None

    def _roster_end(self, seg):
        """Index of the LAST line of a 'Present:' panel roster, or None.

        The roster opens 'Present:' and closes on the line that names the
        bench — 'Present: KRAUSE, MATEY, and SCIRICA, Circuit Judges' on a
        panel, wrapping to a second line on an en banc court ('Present:
        HARDIMAN, KRAUSE, … PHIPPS,' / 'FREEMAN, … and MASCOTT, Circuit
        Judges.'), which is why the bench title cannot be required on the
        opening line."""
        start = next(
            (
                j
                for j, line in enumerate(seg)
                if self.line_plain_text(line).strip().lower().startswith("present:")
            ),
            None,
        )
        if start is None:
            return None
        for j in range(start, min(len(seg), start + 4)):
            if "judge" in self.line_plain_text(seg[j]).strip().lower():
                return j
        return start

    def _order_body_start(self, all_segments, first_byline):
        """Index of the segment opening an unsigned ORDER's text, or None.

        CA3's unsigned orders name their panel with a 'Present:' roster where
        the family base knows only the argued-opinion form, 'Before: <judges>'.
        Without this the order's text belongs to no opinion and is left in the
        headmatter, while the 'BY THE COURT,' signature below it is mistaken
        for the byline (schuster_1, jerome_brown, khalil, whittaker_clark_1).
        On an en banc denial of rehearing the roster reverts to the same
        'Before:' the argued opinions use (adolph_michelin), so the roster
        alone cannot say "order". What can is the conformed signature that
        closes one — 'BY THE COURT,' set in the right-hand column. Requiring it
        between the roster and the first byline keeps an argued opinion's
        roster from ever being read as the head of an order.
        """
        # The roster's wrap can land in a segment of its own (khalil's en banc
        # court runs to two lines that segment apart), so track where the run
        # CLOSES — on the line naming the bench — not where it opens.
        panel, open_for = None, 0
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            for line in seg:
                text = self.line_plain_text(line).strip().lower()
                if text.startswith(("present:", "before:")):
                    panel, open_for = i, 0 if "judge" in text else 3
                elif open_for:
                    panel, open_for = i, 0 if "judge" in text else open_for - 1
        if panel is None:
            return self._titled_order_start(all_segments, first_byline)
        start = None
        for j in range(panel + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            start = j
            break
        if start is None or start >= first_byline:
            return None
        signed = any(
            self._is_signature_column(line)
            for _pno, seg, _kind in all_segments[start:first_byline]
            for line in seg
        )
        return start if signed else None

    def _titled_order_start(self, all_segments, first_byline):
        """Index of the body of a clerk's administrative order, or None.

        These carry no panel at all — a centered 'ORDER AMENDING OPINION'
        title over the order's text, closing 'For the Court,' over the Clerk's
        name (josue_sanchez). With nothing to mark a body, the whole order sat
        in the headmatter and the document returned no writing whatsoever.
        Only consulted for a document with no byline and no roster."""
        if first_byline < len(all_segments):
            return None
        width = getattr(self, "_page1_width", None) or 612.0
        title = next(
            (
                i
                for i, (_pno, seg, _kind) in enumerate(all_segments)
                if seg
                and self.line_plain_text(seg[-1]).strip().upper().startswith("ORDER")
                and self.line_alignment(seg[-1], width) == "C"
            ),
            None,
        )
        if title is None:
            return None
        for j in range(title + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def find_authors(self, all_segments):
        """Add what the strict form-based pass cannot see on its own: a byline
        whose kind clause WRAPS onto the next line, and the unsigned order that
        a panel roster opens."""
        self._order_start = None
        found = list(super().find_authors(all_segments))
        self._wrapped_starts = set(self._wrapped_byline_starts(all_segments))
        for i in self._wrapped_starts:
            if i not in found:
                found.append(i)
        # An order's text always precedes any separate writing attached to it
        # (khalil, michelin print the denial first and the dissents after).
        first = min(found) if found else len(all_segments)
        order = self._order_body_start(all_segments, first)
        if order is not None:
            self._order_start = order
            self._pc_starts.add(order)
            if order not in found:
                found.append(order)
        return sorted(found)

    def _wrapped_byline_starts(self, all_segments) -> list:
        """Segments opening with a byline that wraps over two lines.

        'KRAUSE, Circuit Judge, joined by RESTREPO and FREEMAN,' /
        'Circuit Judges, dissenting sur denial of rehearing en banc.'
        — the first line carries no kind, so on its own it parses as nothing
        and the whole separate writing goes undetected. Gated on the open
        comma that the wrap leaves behind, so an ordinary byline (which closes
        on its own line) is never re-parsed."""
        out = []
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if len(seg) < 2:
                continue
            first = self.line_plain_text(seg[0]).strip()
            if not first.endswith(","):
                continue
            joined = f"{first} {self.line_plain_text(seg[1]).strip()}"
            probe = {"text": joined, "x0": seg[0].get("x0", 0)}
            if self._byline_split(probe) is not None:
                out.append(i)
        return out

    def classify_document_type(self, all_segments, author_indices, n_pages):
        """A 'Present:' roster with no byline is an ORDER, not an opinion —
        the family default calls anything with an opinion start an opinion."""
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def extract(self, pdf_path):
        self._counsel_lines = []
        self._order_start = None
        self._measure_body_template(pdf_path)
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """Flush the harvested counsel addendum onto the document BEFORE the
        completeness sweep runs — appending it after ``extract`` returns would
        put it there after the sweep had already read the sections, so every
        counsel line would be reported unplaced while sitting in the trailer."""
        if self._counsel_lines:
            doc.trailer = list(doc.trailer) + self._counsel_lines
        super()._sweep_residual(doc, source_pages)

    def _measure_body_template(self, pdf_path):
        """Derive CA3's body rail, right measure and leading from the document
        itself."""
        x0s = Counter()
        x1s = Counter()
        page_rows = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    lines = super().page_lines(page)
                    usable = [
                        line
                        for line in lines
                        if 75 < line.get("top", 0) < page.height - 75
                        and line.get("x0", 0) < page.width * 0.42
                        and line.get("x1", 0) > page.width * 0.55
                    ]
                    x0s.update(round(line["x0"]) for line in usable)
                    x1s.update(round(line["x1"]) for line in usable)
                    page_rows.append(usable)
        except Exception:
            return
        if not x0s:
            return
        baseline = float(x0s.most_common(1)[0][0])
        if x1s:
            # The justified right measure. Counsel appearances are set as a
            # list and never reach it — that is what separates them from body.
            self.body_right_rail = float(x1s.most_common(1)[0][0])
        gaps = Counter()
        # Leading measured PER PAGE as well as document-wide. A stapled
        # decision sets each writing to its own measure: hartmann's majority
        # runs on a 15.0pt lead and PHIPPS's dissent on 13.0pt, so the single
        # document-wide value put gap_single_max at 13.5 and every line of the
        # dissent read as tighter-than-body — the whole writing came out as
        # block quotation. A quotation is set tighter than the body on ITS OWN
        # page, which is the only comparison that holds across writings.
        self._page_leading = {}
        for lines in page_rows:
            ordered = sorted(lines, key=lambda line: line["top"])
            here = Counter()
            for above, below in zip(ordered, ordered[1:]):
                gap = below["top"] - above["top"]
                if (
                    abs(above["x0"] - baseline) <= 4
                    and abs(below["x0"] - baseline) <= 4
                    and 10 <= gap <= 24
                ):
                    gaps[round(gap, 1)] += 1
                    here[round(gap, 1)] += 1
            if here and ordered:
                pno = (ordered[0].get("chars") or [{}])[0].get("page_number")
                if pno is not None:
                    self._page_leading[pno] = here.most_common(1)[0][0]
        self.body_baseline_x0 = baseline
        if gaps:
            leading = gaps.most_common(1)[0][0]
            # Put the dominant body leading just inside the body band. Inset
            # quote geometry remains available independently.
            self.gap_single_max = max(self.gap_tight_max + 0.5, leading - 1.5)

    def classify_segment(self, seg):
        """Judge 'tighter than the body' against THIS PAGE's leading.

        The shared bands are set from one document-wide leading, which cannot
        describe a stapled decision whose writings are set differently
        (hartmann: majority 15.0pt, dissent 13.0pt). A segment running at its
        own page's body leading is body, whatever the document-wide band says
        — otherwise the more tightly set writing is read as one long
        quotation."""
        kind = super().classify_segment(seg)
        if kind != "blockquote" or len(seg) < 2:
            return kind
        pno = (seg[0].get("chars") or [{}])[0].get("page_number")
        lead = getattr(self, "_page_leading", {}).get(pno)
        if lead is None:
            return kind
        ordered = sorted(seg, key=lambda line: line["top"])
        gaps = [
            round(b["top"] - a["top"], 1) for a, b in zip(ordered, ordered[1:])
        ]
        inner = [g for g in gaps if 8 <= g <= 24]
        if inner and Counter(inner).most_common(1)[0][0] >= lead - 0.6:
            return "body"
        return kind

    @staticmethod
    def _plain(text):
        out, inside = [], False
        for char in str(text or ""):
            if char == "<":
                inside = True
            elif char == ">":
                inside = False
            elif not inside:
                out.append(char)
        return "".join(out).strip()

    # ------------------------------------------------------ counsel addendum
    # CA3 prints the counsel appearances as an ADDENDUM, after the opinion they
    # belong to — at the end of the document when there is one writing, and
    # between the majority's disposition and the next byline when there is more
    # than one (kalshiex pp. 18-20 → ROTH's dissent p. 21; massey p. 27 → BOVE's
    # concurrence p. 28; energy_harbor p. 9 → SMITH's dissent p. 10).
    #
    # Cut it at the SEGMENT level, before paragraphs are built. Cutting blocks
    # afterwards cannot work: the page-break continuation join folds the first
    # appearance group onto the majority's closing paragraph ("… We will affirm.
    # Matthew J. Platkin Liza B. Fleming …"), and by then the geometry that
    # identifies the block is gone.
    def build_opinion(self, op_start, op_end, *, all_segments, **kwargs):
        if op_start in getattr(self, "_wrapped_starts", ()):
            all_segments = self._join_wrapped_byline(all_segments, op_start)
        all_segments, op_end = self._isolate_counsel_segment(
            all_segments, op_start, op_end
        )
        cut = self._counsel_block_start(all_segments, op_start, op_end)
        if cut is not None:
            for _pno, seg, _kind in all_segments[cut:op_end]:
                for line in seg:
                    text = self.line_inline_text(line).strip()
                    if text:
                        self._counsel_lines.append(text)
            op_end = cut
        rows = self._divider_rows(all_segments, op_start, op_end)
        op = super().build_opinion(
            op_start, op_end, all_segments=all_segments, **kwargs
        )
        return self._split_star_breaks(op, rows)

    def _join_wrapped_byline(self, all_segments, op_start):
        """Fold a two-line byline into one line before the opinion is built.

        The builder reads the byline off the segment's FIRST line only, so a
        byline that wraps leaves its own tail ('Circuit Judges, dissenting sur
        denial of rehearing en banc.') standing as the opening sentence of the
        body, and the author parses out of the half-clause above it. Join the
        pair — with an explicit spacer, since the second line's glyphs restart
        at the left rail and the gap-based text builder would otherwise run the
        two together ('FREEMAN,Circuit Judges')."""
        pno, seg, kind = all_segments[op_start]
        if len(seg) < 2:
            return all_segments
        head, tail = seg[0], seg[1]
        head_chars = list(head.get("chars") or [])
        tail_chars = list(tail.get("chars") or [])
        if not head_chars or not tail_chars:
            return all_segments
        edge = head_chars[-1]
        spacer = dict(edge)
        spacer["text"] = " "
        spacer["x0"] = edge["x1"] + 2
        spacer["x1"] = edge["x1"] + 3
        merged = self._rebuild_line(head, head_chars + [spacer] + tail_chars)
        merged["chars"] = head_chars + [spacer] + tail_chars
        merged["x0"], merged["x1"] = head.get("x0", 0), head.get("x1", 0)
        merged["text"] = (
            f"{self.line_plain_text(head).strip()} "
            f"{self.line_plain_text(tail).strip()}"
        )
        out = list(all_segments)
        out[op_start] = (pno, [merged] + list(seg[2:]), kind)
        return out

    def _divider_rows(self, all_segments, op_start, op_end) -> list:
        """The centered glyph dividers this writing prints between its parts.

        Read as SHAPE, from the lines, before anything is joined into a
        paragraph — the way the Tennessee title anchor is read. Five tests, and
        each one has a rival it exists to exclude:

          * every token on the row is the SAME single non-alphanumeric glyph,
            three or more of them — a run of one repeated mark, so a citation's
            '*5' pincite or a lone '*' footnote mark cannot qualify;
          * the row measures CENTERED on the page axis — the court sets these
            on the axis, body prose is justified to the rail;
          * it spans at most half the text measure — a full-measure row of
            glyphs would be a rule, not a break;
          * it stands clear of the row above it by more than the court's own
            single space, which is what makes it a standalone row rather than
            part of the paragraph above;
          * the writing's own segments are the only place looked, so a divider
            in another writing cannot split this one's prose.

        Returned as TOKEN RUNS, longest first: the court sets two spaces
        between the glyphs and the rendered paragraph carries one, so the row
        is matched token by token and never as a raw substring. Longest first
        so a five-star row is never taken for a three-star one with two stars
        left over.

        WHAT THIS REPLACES: a regex, ``^(<pagenumber/>)?(\\* \\* \\*)\\s+(.+)$``.
        Per the working rules the author byline grammar in ``base`` is the only
        sanctioned pattern in the codebase; a court file must be regex-free. It
        was also wrong, and only measurement of the row could have caught it:
        the pattern counts EXACTLY THREE stars, and CA3 prints five of them in
        nine documents and four in one. united_states_v._jabar_evans p18 sets
        '* * * *' and shipped a heading of '* * *' with the fourth star glued
        to the front of the next paragraph ('* For these above-stated reasons,
        we will affirm …'), which reads as a footnote mark on the holding."""
        rows = []
        measure = (self.body_right_rail or 0.0) - self.body_baseline_x0
        page_width = getattr(self, "_page1_width", 612.0) or 612.0
        for idx in range(max(0, op_start), min(op_end, len(all_segments))):
            _pno, seg, _kind = all_segments[idx]
            for i, line in enumerate(seg):
                text = self._plain(line.get("text"))
                tokens = text.split()
                if len(tokens) < 3 or any(t != tokens[0] for t in tokens):
                    continue
                if len(tokens[0]) != 1 or tokens[0].isalnum():
                    continue
                if self.line_alignment(line, page_width) != "C":
                    continue
                if measure > 0 and (line["x1"] - line["x0"]) > measure * 0.5:
                    continue
                if i and (line["top"] - seg[i - 1]["top"]) <= self.gap_single_max:
                    continue
                run = tuple(tokens)
                if run not in rows:
                    rows.append(run)
        rows.sort(key=len, reverse=True)
        return rows

    def _split_star_breaks(self, op, rows):
        """Keep CA3's centered ``* * *`` transitions as visible separators.

        The PDF text layer places the separator line immediately before the
        next paragraph, so the shared paragraph builder joins them. In the
        rendered review that makes the stars look like paragraph text instead
        of the standalone centered break the court printed.

        ``rows`` names the divider by its own measured glyph run, so the split
        here only has to find where that run ends — never to guess what a
        divider might look like."""
        if not rows:
            return op
        blocks = []
        for block in op.blocks:
            rest = str(block.text or "")
            folio = ""
            # A page break falling on the divider puts the folio marker in
            # front of it; it belongs to the prose that follows, as it did
            # before.
            if rest.startswith("<pagenumber "):
                close = rest.find("/>")
                if close > 0:
                    folio, rest = rest[: close + 2], rest[close + 2 :].lstrip()
            if block.kind != "p":
                blocks.append(block)
                continue
            for run in rows:
                parts = rest.split(None, len(run))
                if len(parts) <= len(run) or tuple(parts[: len(run)]) != run:
                    continue
                tail = parts[len(run)].strip()
                if not tail:
                    continue
                blocks.append(
                    Block(kind="heading", text=" ".join(run), page=block.page)
                )
                block.text = f"{folio} {tail}" if folio else tail
                break
            blocks.append(block)
        op.blocks = blocks
        return op

    def _isolate_counsel_segment(self, all_segments, op_start, op_end):
        """Split a segment that holds the opinion's LAST PARAGRAPH and the
        counsel addendum together, so the cut can fall between them.

        The addendum is cut at segment granularity, which assumes the boundary
        is a segment boundary. In difraia it is not: the closing paragraph
        ('… VACATE the dismissal of the state-law negligence claim, and
        REMAND.') and 'Counsel for Appellant' land in ONE segment, so taking
        the addendum took the conclusion with it — seven lines of the holding
        delivered as trailing matter, unjoined, line by line.

        The boundary is measurable. The addendum is set as its own column, at
        its own left edge and ragged right; the body is justified to the rail.
        So the split is the first line that both starts at the caption's x0 and
        stops short of the right measure — which the conclusion's short last
        line ('… and REMAND.') does not, because it sits at the paragraph
        continuation margin, not the caption's."""
        rail = getattr(self, "body_right_rail", None)
        if rail is None:
            return all_segments, op_end
        out, shift = [], 0
        for idx, entry in enumerate(all_segments):
            pno, seg, kind = entry
            if not (op_start < idx < op_end) or not self._has_counsel_caption(seg):
                out.append(entry)
                continue
            cap = next(
                (
                    j for j, line in enumerate(seg)
                    if self._plain(line.get("text")).startswith("Counsel for")
                    and self._line_all_italic(line)
                ),
                None,
            )
            if cap is None:
                out.append(entry)
                continue
            cap_x0 = seg[cap].get("x0", 0)
            while cap - 1 >= 0:
                prev = seg[cap - 1]
                if (
                    abs(prev.get("x0", 0) - cap_x0) <= 2
                    and prev.get("x1", 0) < rail - 6
                ):
                    cap -= 1
                else:
                    break
            if cap == 0:
                out.append(entry)
                continue
            out.append((pno, seg[:cap], kind))
            out.append((pno, seg[cap:], kind))
            shift += 1
        return out, op_end + shift

    def _counsel_block_start(self, all_segments, op_start, op_end):
        """Index of the segment opening the counsel addendum, or None.

        Anchored on the italic ``Counsel for …`` caption CA3 prints over every
        appearance group — then widened backwards over any name run set above
        its caption, because the court prints the caption BELOW its names in
        some opinions (kalshiex) and ABOVE them in others (massey,
        energy_harbor). The caption alone therefore does not bound the block.
        """
        cap = next(
            (
                i
                for i in range(op_start + 1, op_end)
                if self._has_counsel_caption(all_segments[i][1])
            ),
            None,
        )
        if cap is None:
            return None
        while (
            cap - 1 > op_start
            and self._is_list_segment(all_segments[cap - 1][1])
            and not self._is_closing_prose(all_segments[cap - 1][1])
        ):
            cap -= 1
        return cap

    def _is_closing_prose(self, seg) -> bool:
        """A short segment that is nonetheless a SENTENCE, not a name run.

        ``_is_list_segment`` asks only whether any line reaches the justified
        measure, and a one-line closing paragraph never does — so
        rohan_lyttle's holding ('For the stated reasons, we will affirm the
        judgment.') was ragged, short, and swept into the counsel addendum
        along with the '***' above it.

        Geometry cannot separate those two: one indented short line looks
        exactly like a name. What separates them is that a holding is a
        finished sentence and an appearance is a label — 'Robert J. Daniels'
        and 'Office of United States Attorney' neither run to a full clause nor
        close on a stop."""
        text = " ".join(
            self._plain(line.get("text")) for line in seg
        ).strip()
        return text.endswith((".", "!", "?")) and len(text.split()) >= 6

    def _has_counsel_caption(self, seg) -> bool:
        """True if a segment carries an italic ``Counsel for …`` caption."""
        for line in seg:
            if not self._plain(line.get("text")).startswith("Counsel for"):
                continue
            if self._line_all_italic(line):
                return True
        return False

    def _is_list_segment(self, seg) -> bool:
        """A segment set as a LIST rather than as prose: no line reaches the
        justified right measure. Counsel names, firms and addresses are set
        ragged-right; body prose is justified to the rail on every line but its
        last, so a whole segment that never reaches it cannot be body."""
        rail = getattr(self, "body_right_rail", None)
        if not seg or rail is None:
            return False
        return max(line.get("x1", 0) for line in seg) < rail - 6

    @staticmethod
    def _line_all_italic(line) -> bool:
        """Every letter/digit on the line set in the italic face."""
        seen = False
        for c in line.get("chars") or []:
            t = c.get("text") or ""
            if not t.strip() or not t.isalnum():
                continue
            seen = True
            fn = c.get("fontname") or ""
            if "Italic" not in fn and "Oblique" not in fn:
                return False
        return seen
