"""Supreme Court of South Carolina.

Reversed-title byline with a colon, bold, running inline with the opinion text:
'JUSTICE JAMES: In this case ...' / 'CHIEF JUSTICE KITTREDGE: ...' /
'PER CURIAM: ...'. A 'KITTREDGE, C.J., FEW, JAMES, HILL and VERDIN, JJ.,
concur.' line is a concurrence-vote roster (surname-first, no leading title),
not an opinion start, and is left as body. The shared reversed-title base
handles the colon form.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme


class SouthCarolinaSupreme(ReversedJusticeSupreme):
    court_id = "sc"
    court_label = "The Supreme Court of South Carolina."

    blockquote_by_indent = True
    # SC's sustained quote column starts about 36pt inside the body margin.
    # A small tolerance keeps nominal x=108 lines (often stored as 107.9) on
    # the indented side of the base segmenter's 1.5-step boundary.
    indent_step = 23.0

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        self._sc_styling_headmatter = True
        try:
            return super().extract_headmatter(headmatter_segs, page1_rules)
        finally:
            self._sc_styling_headmatter = False

    def line_alignment(self, line, page_width) -> str:
        # SC lays caption parties and counsel in a fixed x=144 text column.
        # Its short final wrap must retain that column alignment rather than
        # drift independently according to the line's midpoint.
        if (
            getattr(self, "_sc_styling_headmatter", False)
            and abs(line["x0"] - 144.0) <= 3.0
        ):
            return "L"
        return super().line_alignment(line, page_width)

    def parse_author_line(self, text):
        """SC opinions use title-first bylines; captioned trial judges do not."""
        parsed = self._rev_parse(text)
        if parsed is not None:
            return parsed
        stripped = text.strip()
        upper = stripped.upper()
        if upper == "PER CURIAM" or upper.startswith(("PER CURIAM:", "PER CURIAM.")):
            return "PER CURIAM", "per curiam", None
        return None

    def find_authors(self, all_segments) -> list:
        """Find SC's structurally reliable bylines and retain roster context.

        A separate writing's byline is usually just ``JUSTICE NAME:``; the
        preceding vote roster supplies whether it concurs or dissents.
        """
        out = []
        self._sc_kind_by_start = {}
        for i, (_, seg, _) in enumerate(all_segments):
            if not seg:
                continue
            parsed = self.parse_author_line(seg[0]["text"].strip())
            if parsed is None:
                continue
            out.append(i)
            surname = parsed[0].split()[-1].upper()
            prior_lines = [
                self.line_plain_text(line)
                for _, prev_seg, _ in all_segments[max(0, i - 8) : i]
                for line in prev_seg
            ]
            # The vote roster can announce several forthcoming writings before
            # the first of them begins.  Prefer its explicit "separate opinion"
            # window; intervening opinions may mention another justice by name.
            all_prior_lines = [
                self.line_plain_text(line)
                for _, prev_seg, _ in all_segments[:i]
                for line in prev_seg
            ]
            roster = ""
            for j in range(len(all_prior_lines) - 1, -1, -1):
                window = " ".join(all_prior_lines[j : j + 3]).upper()
                if surname in window and "SEPARATE OPINION" in window:
                    roster = window
                    break
            upper = roster or " ".join(prior_lines).upper()
            at = upper.rfind(surname)
            after = upper[at : at + 300] if at != -1 else ""
            low = after.lower()
            if "concurr" in low and "dissent" in low and "part" in low:
                self._sc_kind_by_start[i] = (
                    "concurring in part and dissenting in part"
                )
            elif "dissent" in low:
                self._sc_kind_by_start[i] = "dissenting"
            elif "concurr" in low:
                self._sc_kind_by_start[i] = "concurring"
        return out

    def build_opinion(self, op_start, op_end, **kwargs):
        opinion = super().build_opinion(op_start, op_end, **kwargs)
        kind = getattr(self, "_sc_kind_by_start", {}).get(op_start)
        if kind:
            opinion.type = self.normalize_opinion_type(kind)
        return opinion

    def find_footnote_separator(self, page):
        return self.footnote_sep_fixed_left_rule(page)

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        if kind == "blockquote" and not self._is_indented_blockquote(seg):
            return "body"
        return kind

    def _is_indented_blockquote(self, seg) -> bool:
        if super()._is_indented_blockquote(seg):
            return True
        if len(seg) < 2:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        left = self.body_baseline_x0 + self.para_indent_min
        x0s = [line["x0"] for line in seg]
        if min(x0s) < left or min(x0s) > pw * 0.4:
            return False
        # A hanging quotation may use one shallower item/section label followed
        # by deeper continuations while keeping both right margins inset.
        right = pw - self.body_baseline_x0
        if max(line["x1"] for line in seg) <= right - 24:
            return True
        # SC dialogue is a sustained left inset, usually italic, but a long
        # speaker line may reach the full right measure.
        italic = sum(
            1
            for line in seg
            if "Italic" in self.line_meta(line)[1]
        )
        return italic * 2 >= len(seg)

    def _deep_indent_flags(self, lines) -> list:
        """Sustained SC inset, allowing hanging dialogue continuations.

        A continuation can sit deeper than its speaker line, so adjacency in
        the inset zone matters more than an identical x-coordinate.  An
        ordinary paragraph's lone indented first line remains excluded.
        """
        deep = self.body_baseline_x0 + 30.0
        raw = [
            line["x0"] >= deep and not self._begins_paragraph_block([line])
            for line in lines
        ]
        return [
            flag
            and (
                (
                    i > 0
                    and raw[i - 1]
                    and lines[i]["top"] - lines[i - 1]["top"]
                    <= self.gap_single_max
                )
                or (
                    i + 1 < len(raw)
                    and raw[i + 1]
                    and lines[i + 1]["top"] - lines[i]["top"]
                    <= self.gap_single_max
                )
            )
            for i, flag in enumerate(raw)
        ]

    def paragraph_text(self, lines) -> str:
        # Dialogue blockquotes use one PDF row per speaker turn.  Preserve
        # those structural rows; ordinary prose and legal quotations continue
        # to reflow as paragraphs.
        if len(lines) >= 2 and min(line["x0"] for line in lines) >= (
            self.body_baseline_x0 + 30
        ):
            italic = sum(
                1 for line in lines if "Italic" in self.line_meta(line)[1]
            )
            if italic * 2 >= len(lines):
                return "<br>".join(self.line_inline_text(line) for line in lines)
        return super().paragraph_text(lines)

    def split_body_paragraphs(self, seg) -> list:
        """Split SC's flush-left prose and hanging lists by vertical rhythm.

        Ordinary wrapped lines retain the single line pitch.  A paragraph,
        heading, or next numbered item starts after the larger inter-block
        gap.  This also keeps a numbered item's deeper hanging continuations
        attached instead of treating every indented continuation as a new
        paragraph.
        """
        if not seg:
            return []
        out = [[seg[0]]]
        for line in seg[1:]:
            if line["top"] - out[-1][-1]["top"] > self.gap_single_max:
                out.append([line])
            else:
                out[-1].append(line)
        return out

    def classify_paragraph(self, lines) -> str:
        if lines and all(self._line_all_bold(line) for line in lines):
            return "heading"
        return super().classify_paragraph(lines)

    def _begins_paragraph_block(self, lines) -> bool:
        return bool(lines) and all(self._line_all_bold(line) for line in lines)
