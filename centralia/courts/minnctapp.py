"""Minnesota Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.
"""

from __future__ import annotations

from statistics import median
from typing import Optional

from ..models import Block
from ._appellate import StateAppellate


class MinnesotaCourtOfAppeals(StateAppellate):
    court_id = "minnctapp"
    court_label = "Minnesota Court of Appeals."
    blockquote_by_indent = True

    def _inverted_author(self, text):
        """Parse Minnesota's ``SMITH, TRACY M., Judge`` byline variant."""
        clean = text.strip().rstrip(".")
        if "," not in clean:
            return None
        name, title = clean.rsplit(",", 1)
        name, title = name.strip(), title.strip()
        if (
            "," not in name
            or name != name.upper()
            or title not in self.author_titles
        ):
            return None
        return name, title, None

    def parse_author_line(self, text):
        return self._inverted_author(text) or super().parse_author_line(text)

    def split_author_line(self, line):
        text = self.line_plain_text(line).strip()
        if self._inverted_author(text):
            return text, []
        return super().split_author_line(line)

    def find_footnote_separator(self, page) -> Optional[float]:
        """Minnesota footnotes sit below a fixed two-inch left rule.

        Their text is the same 13-point size as the opinion, so the shared
        small-font heuristic cannot reliably distinguish the footnote zone.
        """
        return self.footnote_sep_fixed_left_rule(page)

    def segment_lines(self, lines, page_width):
        """Keep a wrapped bold hanging heading in one structural segment."""
        segments = super().segment_lines(lines, page_width)
        merged = []
        for seg in segments:
            if (
                merged
                and merged[-1]
                and seg
                and all(self.line_meta(line)[2] for line in merged[-1])
                and all(self.line_meta(line)[2] for line in seg)
                and seg[0]["top"] - merged[-1][-1]["top"] <= self.gap_tight_max
                and seg[0]["x0"]
                >= self.body_baseline_x0 + self.para_indent_min
            ):
                merged[-1].extend(seg)
            else:
                merged.append(seg)
        return merged

    def _is_banner(self, line, text: str) -> bool:
        """Whether ``line`` is one of the court's structural section banners."""
        if self.line_plain_text(line).strip().upper() != text:
            return False
        _size, _font, bold = self.line_meta(line)
        pw = getattr(self, "_page1_width", None) or 612.0
        return bold and self.line_alignment(line, pw) == "C"

    def _is_opinion_banner(self, line) -> bool:
        """Bare ``OPINION`` and qualified banners such as ``SPECIAL TERM
        OPINION`` share the same centered, bold, all-caps geometry."""
        text = self.line_plain_text(line).strip()
        words = text.split()
        if not words or words[-1].upper() != "OPINION" or text != text.upper():
            return False
        _size, _font, bold = self.line_meta(line)
        pw = getattr(self, "_page1_width", None) or 612.0
        return bold and self.line_alignment(line, pw) == "C"

    def find_authors(self, all_segments) -> list:
        """The first real byline follows the centered OPINION banner.

        The caption contains two byline-shaped lines: the disposition credits
        the author (``Bond, Judge``), and the panel roster can end with
        ``Larson, Judge.``.  Their position before the document's typographic
        OPINION boundary distinguishes them from the actual author line.
        """
        candidates = super().find_authors(all_segments)
        opinion_banner = None
        self._minn_opinion_banner_text = "OPINION"
        for i, (_page, seg, _kind) in enumerate(all_segments):
            banner = next(
                (line for line in seg if self._is_opinion_banner(line)), None
            )
            if banner is not None:
                opinion_banner = i
                self._minn_opinion_banner_text = self.line_plain_text(banner).strip()
                break
        if opinion_banner is None:
            self._minn_opinion_start = candidates[0] if candidates else None
            return candidates
        gated = [i for i in candidates if i > opinion_banner]
        self._minn_opinion_start = gated[0] if gated else None
        return gated

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Keep caption material before SYLLABUS in headmatter.

        The syllabus occupies the interval from the centered bold SYLLABUS
        banner to the centered bold OPINION banner.  Some decisions omit the
        syllabus; in those, headmatter simply ends at OPINION.
        """
        lines = [
            line
            for seg in headmatter_segs
            for line in seg
            if (line.get("text") or "").strip()
        ]
        syl_i = next(
            (i for i, line in enumerate(lines) if self._is_banner(line, "SYLLABUS")),
            None,
        )
        op_i = next(
            (i for i, line in enumerate(lines) if self._is_opinion_banner(line)),
            None,
        )
        hm_end = syl_i if syl_i is not None else op_i
        hm_lines = lines[:hm_end] if hm_end is not None else lines
        hm = super().extract_headmatter([hm_lines], page1_rules)

        if syl_i is not None:
            syl_end = op_i if op_i is not None and op_i > syl_i else len(lines)
            hm["syllabus"] = self._syllabus_rows(lines[syl_i:syl_end])
        return hm

    def _syllabus_rows(self, lines) -> list:
        """Reflow syllabus prose while retaining its centered banner."""
        if not lines:
            return []
        rows = [
            {
                "__hm__": True,
                "html": self.paragraph_text([lines[0]]),
                "rel": 1.0,
                "align": "C",
            }
        ]
        body = lines[1:]
        if not body:
            return rows
        for para in super().split_body_paragraphs(body):
            if para:
                rows.append(
                    {
                        "__hm__": True,
                        "html": self.paragraph_text(para),
                        "rel": 1.0,
                        "align": "L",
                    }
                )
        return rows

    def _is_indented_blockquote(self, seg) -> bool:
        """Minnesota quotations use a sustained inset on both margins."""
        if len(seg) < 2:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        left = self.body_baseline_x0 + self.para_indent_min
        right = pw - self.body_baseline_x0
        return (
            min(line["x0"] for line in seg) >= left
            and min(line["x0"] for line in seg) <= pw * 0.4
            and max(line["x1"] for line in seg) <= right - 24
        )

    def classify_segment(self, seg) -> str:
        kind = super().classify_segment(seg)
        # Tight hanging issue lists and bold subsection headings use the full
        # body measure.  Tight leading alone must not turn them into quotes.
        if kind == "blockquote" and not self._is_indented_blockquote(seg):
            return "body"
        return kind

    def split_body_paragraphs(self, seg) -> list:
        """Preserve tight hanging items as paragraphs, not line fragments."""
        if len(seg) < 2:
            return [seg] if seg else []
        gaps = [seg[i]["top"] - seg[i - 1]["top"] for i in range(1, len(seg))]
        pitch = median(gaps)
        if pitch >= self.gap_single_max:
            return super().split_body_paragraphs(seg)

        paras = [[seg[0]]]
        for prev, line in zip(seg, seg[1:]):
            if line["top"] - prev["top"] > pitch * 1.4:
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras

    def classify_paragraph(self, lines) -> str:
        """Centered bold opinion lines are section headings."""
        if lines:
            pw = getattr(self, "_page1_width", None) or 612.0
            if all(
                self.line_meta(line)[2]
                and self.line_alignment(line, pw) == "C"
                for line in lines
            ):
                return "heading"
        return super().classify_paragraph(lines)

    def _begins_paragraph_block(self, lines) -> bool:
        return self.classify_paragraph(lines) == "heading" if lines else False

    def build_opinion(self, op_start, op_end, **kwargs):
        opinion = super().build_opinion(op_start, op_end, **kwargs)
        if op_start == getattr(self, "_minn_opinion_start", None):
            opinion.blocks.insert(
                0,
                Block(
                    kind="heading",
                    text=getattr(self, "_minn_opinion_banner_text", "OPINION"),
                ),
            )
        return opinion
