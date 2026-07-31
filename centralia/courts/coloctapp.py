"""Colorado Court of Appeals.

Distinct layout, tuned directly here:

  * A front-matter page precedes the opinion. It opens with a publication
    notice ('The summaries of the Colorado Court of Appeals published opinions
    constitute no part of the opinion ...') followed by an official SUMMARY /
    headnote (announcement number '2025COA88', docket + case + subject tags,
    and a prose summary). The notice goes to ``dropped`` and the summary to the
    ``syllabus`` field — neither is opinion content. The real headmatter begins
    on the next page, which opens with the 'COLORADO COURT OF APPEALS' banner.

  * The author is announced, not signed: 'Opinion by JUDGE SCHUTZ' (with
    'Grove and Bernard, JJ., concur' beneath). The opinion body opens at the
    first numbered paragraph, '¶ 1'. So the author is read off the announcement
    and the opinion starts at '¶ 1' (the announcement / counsel block stays in
    the headmatter).
"""

from __future__ import annotations

from ._appellate import StateAppellate

_NOTICE_CUE = "constitute no part of the opinion"
_NOTICE_END = "language in the opinion"
# A separate writing announces itself with the judge's title spelled out in
# caps, a comma, then the participle describing the writing:
#   'JUDGE BERGER, concurring in part and dissenting in part.'
# The majority's closing roster looks similar but takes a finite verb and no
# comma ('JUDGE GROVE and JUDGE BERNARD concur.'), so the comma plus the
# lowercase participle tail is what separates a header from a roster line.
_WRITING_TITLES = ("CHIEF JUDGE ", "SENIOR JUDGE ", "JUDGE ", "JUSTICE ")
# The caption page announces itself: the banner is its first line. Everything
# before it — however many pages the official summary runs to — is front matter.
_CAPTION_BANNER = "colorado court of appeals"


class ColoradoCourtOfAppeals(StateAppellate):
    court_id = "coloctapp"
    court_label = "Colorado Court of Appeals."

    # ---------------------------------------------------------- front matter
    def extract(self, pdf_path: str):
        self._front_notice = None
        self._front_lines = []
        self._front_pw = 612.0
        self._in_front_notice = True
        self._colo_author = None
        return super().extract(pdf_path)

    def _sweep_residual(self, doc, source_pages):
        """The front-matter notice and official summary are read off the pages
        ahead of the caption page, so they have to be attached to the document
        BEFORE the completeness sweep runs — the sweep is the last step of
        ``super().extract()``, and anything attached after it still reports as
        unplaced."""
        if self._front_notice:
            doc.dropped = list(doc.dropped) + [self._front_notice]
        if self._front_lines:
            # Formatted here, not per page: the summary's prose runs straight
            # through the page break, so the whole flow has to be in hand
            # before it can be cut into paragraphs.
            doc.syllabus = list(doc.syllabus or []) + self._summary_rows(
                self._front_pw, self._front_lines
            )
        super()._sweep_residual(doc, source_pages)

    def caption_page(self, pdf):
        """The first page whose opening line is the court banner. The official
        summary ahead of it runs to one page or two, so 'the page after the
        notice' is not reliable — the banner is.

        This is also where the caption's four full-measure rules live; measured
        on page 1 they are simply absent and the caption renders unruled."""
        for page in pdf.pages:
            try:
                lines = sorted(
                    page.extract_text_lines(), key=lambda l: l.get("top", 0)
                )
            except Exception:
                continue
            if lines and (lines[0].get("text") or "").strip().lower().startswith(
                _CAPTION_BANNER
            ):
                return page
        return pdf.pages[0] if pdf.pages else None

    def find_footnote_separator(self, page):
        """Colorado sets footnotes at the BODY size (14pt) and rules them off
        with a full-measure line — the same width as the four rules that
        divide the caption. Neither width nor type size can tell those apart,
        so the separator is found structurally instead, by the single-spaced
        matter beneath a rule that stands clear of any text line.

        On the CAPTION page that still isn't enough: its four dividers are
        full-measure rules with body text under them, and the last one would
        swallow the whole counsel block into a footnote. Colorado draws no
        footnote rule there at all — the starred assignment note under counsel
        has no divider — so the caption page simply has no separator."""
        if page.page_number == getattr(self, "_caption_pno", 1):
            return None
        return self._footnote_sep_structural(page)

    def page_lines(self, page):
        """Every page BEFORE the caption page is front matter: the publication
        notice -> dropped, the official summary after it -> syllabus. None of
        it reaches the opinion pipeline. The summary runs to a second page on
        longer cases, so the split is by position relative to the caption page,
        not by which page happens to carry the notice."""
        if page.page_number >= getattr(self, "_caption_pno", 1):
            return super().page_lines(page)
        notice, syl = [], []
        for l in sorted(page.extract_text_lines(), key=lambda l: l.get("top", 0)):
            t = (l.get("text") or "").strip()
            if not t:
                continue
            if self._in_front_notice:
                notice.append(t)
                if _NOTICE_END in t.lower():
                    self._in_front_notice = False
            else:
                l["_fm_page"] = page.page_number
                syl.append(l)
        if notice:
            self._front_notice = " ".join(
                ([self._front_notice] if self._front_notice else []) + notice
            )
        self._front_pw = page.width
        self._front_lines = list(self._front_lines) + syl
        return []

    # ----------------------------------------------------- summary formatting
    def _summary_rows(self, pw, lines):
        """The official summary as styled rows, not loose lines.

        The page sets it as: a right-aligned 'SUMMARY' label and release date,
        a centered bold announcement number, a bold left heading (docket, case
        name and subject tags) that wraps over two or three rows, then the
        prose. So the lines are first cut into runs of one alignment and one
        weight — a right- or centre-aligned line stands alone, because a label
        pinned to a margin is never wrapped text — and each run is then split
        into paragraphs at its first-line indents. A blank row is emitted only
        where the page leaves a gap wider than the neighbouring run's own line
        pitch; the double-spaced paragraphs inside one prose flow are not
        separated on the page, so no blank row goes between them."""
        if not lines:
            return []

        def same_page(a, b):
            return a.get("_fm_page") == b.get("_fm_page")

        gaps = [
            b["top"] - a["top"]
            for a, b in zip(lines, lines[1:])
            if same_page(a, b) and b["top"] - a["top"] > 1
        ]
        unit = min(gaps) if gaps else 0.0

        def bold_of(line):
            marks = [
                "bold" in (c.get("fontname") or "").lower()
                for c in (line.get("chars") or [])
            ]
            return bool(marks) and all(marks)

        def pitch(seq):
            gs = [
                b["top"] - a["top"]
                for a, b in zip(seq, seq[1:])
                if same_page(a, b) and b["top"] > a["top"]
            ]
            return min(gs) if gs else 0.0

        # ---- runs: one alignment, one weight; a margin-pinned label stands alone
        runs = []
        for line in lines:
            key = (self.line_alignment(line, pw), bold_of(line))
            if runs and runs[-1][0] == key and key[0] not in ("C", "R"):
                runs[-1][1].append(line)
            else:
                runs.append((key, [line]))

        rows = []
        for idx, ((align, _bold), run) in enumerate(runs):
            run_pitch = pitch(run) or unit
            # A gap row before this run only where the page really opens one.
            if idx:
                prev_run = runs[idx - 1][1]
                prev_last = prev_run[-1]
                if same_page(prev_last, run[0]):
                    gap = run[0]["top"] - prev_last["top"]
                    if gap > 1.35 * (pitch(prev_run) or unit):
                        rows.append("")
            # ---- paragraphs: a line set right of the run's left rail opens one
            left = min(l["x0"] for l in run)
            paras = []
            for line in run:
                if paras and line["x0"] <= left + 6:
                    paras[-1].append(line)
                else:
                    paras.append([line])
            for para in paras:
                rows.append(
                    {
                        "__hm__": True,
                        "html": self.paragraph_text(para),
                        "rel": 1.0,
                        "align": align,
                    }
                )
        return rows

    # ------------------------------------------------------ byline / ¶1 start
    @staticmethod
    def _separate_writing_byline(text):
        """('JUDGE BERGER', 'concurring in part and dissenting in part') for a
        separate writing's own header line, else ``None``."""
        t = " ".join(text.split())
        if not t.endswith(".") or "," not in t:
            return None
        if not t.startswith(_WRITING_TITLES):
            return None
        name, _, tail = t.partition(",")
        tail = tail.strip().rstrip(".").strip()
        # A participle ('concurring', 'specially concurring', 'dissenting') —
        # lowercase; the roster form has no comma at all and never reaches here.
        if not tail[:1].islower():
            return None
        return name.strip(), tail

    def find_authors(self, all_segments) -> list:
        # Author is announced ('Opinion by JUDGE SCHUTZ'); read it off. The line
        # sits inside the centered disposition block, so scan every line.
        self._colo_author = None
        self._colo_writings = {}
        for _p, seg, _k in all_segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                if t.lower().startswith("opinion by "):
                    self._colo_author = t[len("opinion by ") :].strip()
                    break
            if self._colo_author:
                break
        # The opinion body opens at the first numbered paragraph; each separate
        # writing that follows opens at its own announced header, set on its own
        # indented line clear of the body column.
        starts = []
        for i, (_p, seg, _k) in enumerate(all_segments):
            t = self.line_plain_text(seg[0]).strip()
            if not starts:
                if t.startswith("¶ 1") or t.startswith("¶1"):
                    starts.append(i)
                continue
            parsed = self._separate_writing_byline(t)
            if parsed and seg[0].get("x0", 0) > self.body_baseline_x0:
                starts.append(i)
                self._colo_writings[i] = parsed
        if starts:
            return starts
        return super().find_authors(all_segments)

    def split_author_line(self, line):
        # The opinion opens on body (¶ 1), not a byline — keep the line as body.
        if self.line_plain_text(line).strip().startswith("¶"):
            return "", [line]
        return super().split_author_line(line)

    @staticmethod
    def _numbered_paragraph_line(line):
        text = (line.get("text") or "").lstrip()
        if not text.startswith("¶"):
            return False
        tail = text[1:].lstrip()
        number = tail.split(None, 1)[0].rstrip(".") if tail else ""
        return number.isdigit()

    def _footnote_mark_chars(self, chars, body_size):
        """Colorado sets its hanging paragraph pinpoint ('¶ 12') two points
        smaller than the body, so on size alone the pilcrow and its number read
        as a footnote reference. A small run containing the pilcrow is a
        paragraph number and stays inline content — the same problem the
        ``bracket_pinpoint`` courts have with '{1}' / '[1]'."""
        out = super()._footnote_mark_chars(chars, body_size)
        i = 0
        while i < len(out):
            if not out[i]:
                i += 1
                continue
            j = i
            while j < len(out) and (
                out[j] or not (chars[j].get("text") or "").strip()
            ):
                j += 1
            if any((chars[k].get("text") or "") == "¶" for k in range(i, j)):
                for k in range(i, j):
                    out[k] = False
            i = j
        return out

    def split_body_paragraphs(self, seg):
        """Split on Colorado's hanging ``¶ N`` marker, not right indentation.

        Section headings are centered and stacked one body line apart ('I.
        Background and Procedural History' over 'A. School Violence'), so a
        centered line also opens a block: leaving/entering the centered axis
        breaks, and two centered lines a full body line apart are two
        headings. A heading that genuinely wraps stays single-spaced, well
        inside that gap, and so stays one heading."""
        if not seg:
            return []
        pw = getattr(self, "_page1_width", None) or 612.0
        paragraphs = [[seg[0]]]
        was_centered = self.line_alignment(seg[0], pw) == "C"
        for prev, line in zip(seg, seg[1:]):
            centered = self.line_alignment(line, pw) == "C"
            leading = max(1.0, prev.get("bottom", 0) - prev.get("top", 0))
            if self._numbered_paragraph_line(line):
                new_block = True
            elif centered != was_centered:
                new_block = True
            elif centered and (line["top"] - prev["top"]) > 1.6 * leading:
                new_block = True
            else:
                new_block = False
            if new_block:
                paragraphs.append([line])
            else:
                paragraphs[-1].append(line)
            was_centered = centered
        return paragraphs

    def _begins_paragraph_block(self, lines):
        return bool(lines and self._numbered_paragraph_line(lines[0]))

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        parsed = getattr(self, "_colo_writings", {}).get(op_start)
        if parsed:
            # The header's participle names the writing; the byline grammar is
            # name-first and cannot read Colorado's title-first announcement.
            op.type = self.normalize_opinion_type(parsed[1])
        elif self._colo_author:
            op.author = self._colo_author
        return op
