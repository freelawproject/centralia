"""Kentucky Court of Appeals.

After the 'OPINION' header and the 'BEFORE: <panel>, JUDGES.' roster, the author
signs inline with an ALL-CAPS surname, the title, and a colon: 'MCNEILL, JUDGE:
This case arises ...'. Separate writings carry the kind in the same form
('NAME, JUDGE, CONCURRING:' / 'NAME, JUDGE, DISSENTING:'). The ALL-CAPS surname
distinguishes the byline from the 'BEFORE:' panel line and the trial-court
history; bold centered section labels ('STANDARD OF REVIEW', 'ANALYSIS') are
headings in the body.

Some memorandum opinions are published with NO byline at all — the roster is
followed straight by the opening paragraph and the writing closes on 'ALL
CONCUR.' ('crystal_blair-lewis_v._arh_advanced_care_inc.'). That is an unsigned
opinion of the panel; see ``page_lines`` and ``find_authors``.
"""

from __future__ import annotations

import re

from ._appellate import StateAppellate
from ._statesupreme import is_caps_name

_KY_JUDGE_TITLES = {"judge", "chief judge", "j", "cj", "pj"}


class KentuckyCourtOfAppeals(StateAppellate):
    court_id = "kyctapp"
    court_label = "Kentucky Court of Appeals."

    @staticmethod
    def _ending_matter_start(blocks):
        """Find the counsel/signature section after the ruling closes."""
        concur = None
        for i, block in enumerate(blocks):
            text = re.sub(r"<[^>]+>", "", block.text or "").strip().upper()
            if text.rstrip(":.") in {"ALL CONCUR", "ALL CONCURRED"}:
                concur = i
        start = concur + 1 if concur is not None else 0
        for i in range(start, len(blocks)):
            text = re.sub(r"<[^>]+>", "", blocks[i].text or "").strip().upper()
            if any(
                marker in text
                # SINGULAR AND PLURAL. Where one brief was filed per side the
                # court heads the column 'BRIEF FOR APPELLANT:', which is not a
                # substring of 'BRIEFS FOR' — so the appearances stayed at the
                # end of the opinion body instead of moving to the trailer.
                for marker in (
                    "ON THE BRIEFS",
                    "BRIEFS FOR",
                    "BRIEF FOR",
                    "ORAL ARGUMENT FOR",
                    "ENTERED:",
                )
            ):
                return i
        return None

    def extract(self, pdf_path: str):
        doc = super().extract(pdf_path)
        if not doc.opinions:
            return doc
        blocks = doc.opinions[-1].blocks
        cut = self._ending_matter_start(blocks)
        if cut is not None:
            doc.trailer = list(doc.trailer) + blocks[cut:]
            doc.opinions[-1].blocks = blocks[:cut]
        return doc

    def _sweep_residual(self, doc, source_pages):
        """Route the page-one release timestamp into Removed furniture.

        Kentucky's Court of Appeals prints ``RENDERED: ...`` above the
        caption.  It is intentionally outside the headmatter model, but the
        completeness sweep sees it as ordinary source text unless it is
        registered before the sweep runs.
        """
        rendered = []
        for page_no, lines in source_pages:
            if page_no != 1:
                continue
            for line in lines:
                text = line.strip()
                if re.match(r"^RENDERED:\s+.+", text, re.I):
                    rendered.append(text)
        if rendered:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                text for text in dict.fromkeys(rendered) if text not in have
            ]
        super()._sweep_residual(doc, source_pages)

    def _kyctapp_byline(self, text: str):
        """Parse 'NAME, JUDGE[, KIND]:' -> (name, title, kind), or None."""
        t = (text or "").strip()
        if t.upper().startswith("PER CURIAM"):
            return "PER CURIAM", "per curiam", None
        ci = t.find(":")
        if ci == -1:
            return None
        parts = [p.strip() for p in t[:ci].split(",")]
        if len(parts) < 2 or not is_caps_name(parts[0]):
            return None
        title_at = 1
        name = parts[0]
        # ``JONES, L., JUDGE:`` uses surname-first reporter ordering.  The
        # middle initial belongs to the author, not to the judicial title.
        if (
            len(parts) >= 3
            and len(parts[1].rstrip(".")) == 1
            and parts[1].rstrip(".").isalpha()
        ):
            name = f"{parts[0]}, {parts[1]}"
            title_at = 2
        if parts[title_at].lower().replace(".", "") not in _KY_JUDGE_TITLES:
            return None
        kt = " ".join(parts[title_at + 1 :]).upper()
        has_c, has_d = "CONCUR" in kt, "DISSENT" in kt
        kind = (
            "concurring in part and dissenting in part"
            if has_c and has_d
            else "dissenting"
            if has_d
            else "concurring"
            if has_c
            else None
        )
        return name, parts[title_at].title(), kind

    def parse_author_line(self, text):
        r = self._kyctapp_byline(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    # -------------------------------------------------- unsigned panel opinion
    def _is_panel_roster(self, line) -> bool:
        """'BEFORE: KAREM, MCNEILL, AND TAYLOR, JUDGES.' — the roster that
        introduces the court's own writing. It opens on the capitalised word and
        closes on the bench word, which is what separates it from body prose
        that merely begins a sentence with 'before'."""
        text = self.line_plain_text(line).strip()
        if not text.startswith("BEFORE"):
            return False
        return text.rstrip(".:;, ").upper().endswith(("JUDGE", "JUDGES"))

    def page_lines(self, page):
        """Close the headmatter at the panel roster.

        The roster and the opening paragraph are the same size and the same
        double leading apart, so on an unsigned opinion the segmenter joins them
        and the body's first line is buried mid-segment where ``find_authors``
        (which reads a segment's FIRST line) can never see it — all nine pages
        of blair-lewis landed in headmatter. Cutting below the roster follows
        the page's own structure: nothing above the roster is ever body, and on
        a signed opinion the line below it is the byline, which starts its own
        segment anyway.
        """
        lines = super().page_lines(page)
        for prev, line in zip(lines, lines[1:]):
            if self._is_panel_roster(prev):
                line["_seg_break"] = True
        return lines

    def _percuriam_start(self, all_segments):
        """Index of the first body segment after the panel roster, or None."""
        roster = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._is_panel_roster(seg[-1]):
                roster = i
        if roster is None:
            return None
        for j in range(roster + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            return j
        return None

    def find_authors(self, all_segments):
        self._pc_starts = set()
        out = super().find_authors(all_segments)
        if out:
            return out
        # No 'NAME, JUDGE:' anywhere: the panel published the opinion unsigned.
        # It opens immediately below the roster; the writing is the court's, so
        # the author is the panel — PER CURIAM, the same name the circuit family
        # gives an unsigned memorandum.
        start = self._percuriam_start(all_segments)
        if start is None:
            return []
        self._pc_starts.add(start)
        return [start]

    def split_author_line(self, line):
        if getattr(self, "_pc_now", False):
            return "PER CURIAM", [line]  # no byline line — keep it as body
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        self._pc_now = op_start in getattr(self, "_pc_starts", set())
        op = super().build_opinion(op_start, op_end, **kwargs)
        self._pc_now = False
        if op_start in getattr(self, "_pc_starts", set()):
            op.author = "PER CURIAM"
            op.type = self.normalize_opinion_type(None)
        return op

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._kyctapp_byline(text) is not None:
            ci = text.find(":")
            return text[: ci + 1], text[ci + 1 :].strip()
        return super()._byline_split(line)
