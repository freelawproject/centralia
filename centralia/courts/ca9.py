"""United States Court of Appeals for the Ninth Circuit."""

from __future__ import annotations

from ._circuit import FederalCircuitBase
from .generic import _is_name


class NinthCircuit(FederalCircuitBase):
    court_id = "ca9"
    court_label = "United States Court of Appeals for the Ninth Circuit."
    circuit_phrase = "ninth circuit"
    body_baseline_x0 = 54.0
    gap_tight_max = 10.0
    gap_single_max = 12.0
    gap_double_max = 22.0

    # The family's blanket page-2 cutoff (95pt) assumes a deep running header.
    # The Ninth has none that deep: its reporter-format published opinions
    # print ONE short head line ('2 USA V. SANCHEZ') inside the top 40pt and
    # open real text at top~73, and its memorandum format prints no head at
    # all. So the blanket cutoff swallowed the first one or two real lines of
    # every continuation page — headmatter rows ('Argued and Submitted ...',
    # 'Opinion by Judge R. Nelson;'), body text, and even a concurrence byline.
    # The head is identified by its own geometry below instead.
    page2_header_cutoff = 0.0
    # ... and the head is let THROUGH filter_margins (default margin_top 39 sits
    # just below it) so it can be recorded in `dropped` rather than vanish.
    margin_top = 30.0

    # Running-head signature: pinned in the top band and set smaller than the
    # 12/14pt body (8pt, or 10pt in some volumes). Footnote text is also 10pt
    # but always sits below the footnote rule, far outside this band.
    running_head_max_top = 60.0
    running_head_max_size = 10.5
    running_head_first_page = 1  # an amended opinion heads page 1 as well

    # A tight-gapped run inside the Ninth's single-spaced body is NOT an
    # advisory notice — it is content whose leading is compressed, e.g. the
    # two-column sentencing-guidelines table in United States v. Kheyre, whose
    # wrapped cells sit ~7pt apart. Dropping 'notice' segments (the default,
    # right for double-spaced courts) silently deleted those rows.
    drop_notice_in_body = False

    def extract(self, pdf_path):
        self._pc_order_starts = set()
        return super().extract(pdf_path)

    def _maybe_drop_running_header(self, page, lines):
        lines = super()._maybe_drop_running_header(page, lines)
        return self._join_wrapped_bylines(self._drop_head_band(page, lines))

    # ------------------------------------------------------- wrapped bylines
    def _join_wrapped_bylines(self, lines):
        """Fold a byline that WRAPS onto a second line back into one line.

        A separate writing names its kind in the byline, which can run past the
        reporter measure's 288pt column:

            BEA, Circuit Judge, concurring in part and dissenting in
            part:
            BERZON, Circuit Judge, with whom W. FLETCHER,
            Circuit Judge, joins, concurring:

        The terminator then sits on the SECOND line, so the first line parses as
        an unterminated byline (or not at all) and the remainder is orphaned as
        a stray body paragraph — which also mis-typed the writing, since the
        'dissenting in part' half of the kind never reached the parser.

        A join is only made when the two lines TOGETHER parse as a terminated
        byline and the second is part of the same single-spaced run (not a new,
        indented paragraph), so ordinary prose can never be folded."""
        out = []
        skip = False
        for i, ln in enumerate(lines):
            if skip:
                skip = False
                continue
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            joined = self._byline_join_candidate(ln, nxt)
            if joined is not None:
                out.append(joined)
                skip = True
                continue
            out.append(ln)
        return out

    def _byline_join_candidate(self, line, nxt):
        """The single merged line for a two-line byline, or None."""
        if nxt is None:
            return None
        text = (line.get("text") or "").strip()
        if not text or text.endswith((".", ":")) or "," not in text:
            return None
        if not _is_name(text[: text.index(",")].strip()):
            return None
        # Same single-spaced run, and the continuation is not a fresh indented
        # paragraph (a byline's runover returns to the body margin).
        gap = nxt.get("top", 0) - line.get("top", 0)
        if not 0 < gap <= self.gap_single_max + 2:
            return None
        if nxt.get("x0", 0) > line.get("x0", 0) + 2:
            return None
        merged = self._rebuild_line(
            line, list(line.get("chars") or []) + list(nxt.get("chars") or [])
        )
        merged["text"] = f"{text} {(nxt.get('text') or '').strip()}"
        split = self._byline_split(merged)
        if split is None or not split[0].rstrip().endswith((".", ":")):
            return None
        return merged

    # ------------------------------------------------------------- bylines
    # Most Ninth bylines spell the bench title out ('NGUYEN, Circuit Judge:'),
    # which the family detector already reads. But the published reports also
    # set a separate writing with the ABBREVIATED reporter title —
    # 'R. Nelson, J., concurring:' / 'Forrest, J., dissenting.' — and those were
    # invisible to a detector keyed on the word 'Judge'. The writing was then
    # swept into the majority, and because its footnotes restart at 1 they
    # collided with the majority's labels and were discarded outright.
    abbrev_bench_titles = ("C.J.", "J.")

    def _byline_split(self, line):
        # The page-1 headmatter names the writings in CENTERED descriptor rows
        # ('Opinion by Judge Nguyen;' / 'Concurrence by Judge R. Nelson' /
        # 'Per Curiam Opinion'). A real byline is flush at the body's left
        # margin, so a centered candidate is a descriptor, not an opinion start
        # — without this, 'Per Curiam Opinion' opened an opinion in the middle
        # of the caption and swallowed the rest of the headmatter.
        if self.line_alignment(line, getattr(self, "_page1_width", 612.0)) == "C":
            return None
        found = super()._byline_split(line)
        if found is not None:
            return found
        return self._abbrev_byline_split((line.get("text") or "").strip())

    def _abbrev_byline_split(self, text):
        """The abbreviated-title byline, as (byline_text, inline_body) or None.

        Everything between the name's comma and the abbreviation must be title
        qualifiers, which is what keeps a citation parenthetical out: in
        'Flores Molina, 37 F.4th at 648 (VanDyke, J., dissenting).' the run up
        to the 'J.' is sentence text, not a title run, so it is rejected."""
        if not text or "," not in text:
            return None
        comma = text.index(",")
        if not _is_name(text[:comma].strip()):
            return None
        for title in self.abbrev_bench_titles:
            start = comma + 1
            while True:
                idx = text.find(title, start)
                if idx == -1:
                    break
                end = idx + len(title)
                if not self._is_title_run(text[comma + 1 : idx]):
                    start = end
                    continue
                j = end
                while j < len(text) and text[j] == " ":
                    j += 1
                if j >= len(text):
                    return text, ""
                if text[j] in ".:":
                    return text[: j + 1], text[j + 1 :].strip()
                if text[j] == ",":
                    k = self._kind_clause_end(text, j)
                    if k is not None:
                        return text[: k + 1], text[k + 1 :].strip()
                start = end
        return None

    def parse_author_line(self, text):
        found = super().parse_author_line(text)
        if found is not None:
            return found
        # Same abbreviated form, for LABELLING (name / title / concur-dissent
        # kind). The family parser demands the spelled-out office in the part
        # after the comma, so 'Forrest, J., dissenting.' produced no kind and
        # the writing would have been typed 'majority'.
        split = self._abbrev_byline_split((text or "").strip())
        if split is None:
            return None
        byline = split[0].strip().rstrip(".:").strip()
        if "," not in byline:
            return None
        name, rest = byline.split(",", 1)
        name, rest = name.strip(), rest.strip()
        low = rest.lower()
        kind = None
        for k in (
            "concurring in part and dissenting in part",
            "concurring in the judgment and dissenting in part",
            "concurring and dissenting",
            "concurring in the judgment",
            "concurring in part",
            "dissenting in part",
            "concurring",
            "dissenting",
        ):
            if k in low:
                kind = k
                break
        return (name, rest, kind)

    # ---------------------------------------------------------- order style
    # The reporter format hands off from headmatter to the ruling with a
    # standalone BOLD CENTERED heading: 'OPINION' for an argued opinion,
    # 'ORDER' for a motions ruling (a stay pending appeal, an amendment on
    # rehearing). A signed opinion follows the heading with a byline, but an
    # unsigned ORDER has none — and the family's fallback looks for a
    # 'Before … Circuit Judges.' roster, which in this format WRAPS ('Before:
    # Andrew D. Hurwitz and Roopali H. Desai, Circuit / Judges.*') so the
    # 'Judge' never appears on the roster's own line. The result was that the
    # whole order (Background, Discussion, disposition) stayed in the
    # headmatter and the document reported zero opinions.
    _BODY_HEADINGS = ("ORDER", "OPINION")

    def _percuriam_start(self, all_segments):
        self._pc_order_starts = set()
        heading = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if len(seg) != 1:
                continue
            line = seg[0]
            words = self.line_plain_text(line).strip().upper().split()
            if not words or words[-1] not in self._BODY_HEADINGS:
                continue
            if len(words) > 2:  # 'ORDER' / 'AMENDED ORDER', never a sentence
                continue
            if self.line_alignment(
                line, getattr(self, "_page1_width", 612.0)
            ) != "C" or not self._line_all_bold(line):
                continue
            heading = i
        if heading is not None:
            start = self._first_content_after(all_segments, heading)
            if start is not None:
                word = self.line_plain_text(all_segments[heading][1][0]).strip().upper()
                if word.split()[-1] == "ORDER":
                    self._pc_order_starts = {start}
                return start
        return super()._percuriam_start(all_segments)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        # The document STYLE follows the heading that opened the ruling: an
        # unsigned ruling under the bold 'ORDER' heading is an order, even
        # though locating its body gives it an author index.
        if getattr(self, "_pc_order_starts", None):
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        # A ruling opened by the bold 'ORDER' heading is an order, not a
        # majority opinion; the review page and the casebody both key off type.
        if op_start in getattr(self, "_pc_order_starts", set()):
            op.type = "order"
        return op

    def _first_content_after(self, all_segments, i):
        for j in range(i + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def find_footnote_separator(self, page):
        return self._sep_at(page, 50, 60)

    def skip_headmatter_segment(self, seg) -> bool:
        if seg and (seg[0].get("text") or "").strip().upper() in (
            "FOR PUBLICATION",
            "NOT FOR PUBLICATION",
        ):
            return True
        return super().skip_headmatter_segment(seg)
