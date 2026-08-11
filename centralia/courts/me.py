"""Maine Supreme Judicial Court.

Standalone abbreviated-title byline, not bold, left-aligned at the body margin
and set off from the centered case caption above it by a large vertical gap:
'LIPEZ, J.' / 'MEAD, J.' / 'STANFILL, C.J.' / 'HJELM, A.R.J.' (Active Retired
Justice — handled by the shared abbreviation table). A full-court decision opens
instead with 'JUDGMENT OF THE COURT' (no named author), recognized here as a
per-curiam-style byline. The opinion body follows on the next lines, its
paragraphs numbered '[¶1]', '[¶2]', ...

Footnote marks
--------------
The footnote-reference superscripts (~9pt) and the hanging footnote-block
numbers (~7pt) are set small and slightly raised, so pdfplumber clusters each
onto its own line — leaking the in-body reference as a stray '1' paragraph and,
in the footnote block, hiding the number from the label detector (which expects
the digit to lead a larger-text line). We re-attach each isolated small-digit
line to the line just below it: the body reference becomes an inline
``<footnotemark>`` and the block number leads its footnote text, so the
per-number split works.

Italic-font baseline bug
------------------------
This reporter's italic font (Cambria-Italic — case citations, signals, and the
parenthetical trial-judge name) declares an inflated glyph bounding box, so
pdfplumber computes those chars' ``top``/``bottom`` ~one line too high and
clusters them onto the wrong row — scrambling the text ('Court (Aranson, J.)'
splits, with the italic name reported a line above its own parentheses). The
text-matrix baseline (``matrix[5]``) is correct for every glyph regardless of
its box, so we re-derive each char's ``top`` from the baseline before the line
clustering runs. Done per font size, keyed off the well-behaved roman glyphs at
that size, so a misboxed glyph is snapped back onto its true row and the line
then reads in x-order.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median
from typing import Optional

from ._abbrevtitle import AbbrevTitleSupreme

# Per-curiam-style openers: the whole line is the byline (no named author), and
# the opinion body begins on the following line.
_COURT_OPENERS = frozenset({"JUDGMENT OF THE COURT", "OPINION OF THE COURT"})


class MaineSupreme(AbbrevTitleSupreme):
    court_id = "me"
    court_label = "Maine Supreme Judicial Court."

    def extract(self, pdf_path):
        self._advisory_start = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        for i, (_p, seg, _kind) in enumerate(all_segments):
            if not seg:
                continue
            text = self.line_plain_text(seg[0]).strip().lower()
            if text.startswith("to the maine legislature"):
                self._advisory_start = i
                return [i]
        return []

    def split_author_line(self, line):
        if getattr(self, "_advisory_start", None) is not None:
            return "THE JUSTICES", [line]
        return super().split_author_line(line)

    @staticmethod
    def correct_page_geometry(page) -> None:
        """Snap each char's ``top``/``bottom`` back to the row implied by its
        text-matrix baseline, fixing the italic font's inflated-box mis-rows.

        For a correctly-boxed glyph, ``top + matrix[5]`` is a constant at a given
        font size (the baseline sits a fixed distance below the page top). The
        median of that sum over all chars of a size is dominated by the roman
        majority, so ``const[size] - matrix[5]`` is the *true* top for any glyph
        at that size; glyphs whose reported top differs (the misboxed italics)
        are moved onto it. Mutates the char dicts in place so the unchanged
        clustering in ``BaseExtractor.page_lines`` sees corrected geometry."""
        chars = page.chars
        sums = defaultdict(list)
        for c in chars:
            m = c.get("matrix")
            if m:
                sums[round(c["size"], 1)].append(c["top"] + m[5])
        const = {sz: median(v) for sz, v in sums.items()}
        for c in chars:
            m = c.get("matrix")
            if not m:
                continue
            k = round(c["size"], 1)
            if k not in const:
                continue
            delta = (const[k] - m[5]) - c["top"]
            if abs(delta) <= 1.0:  # already on its true row (roman glyphs)
                continue
            c["top"] += delta
            c["bottom"] += delta
            c["doctop"] = c.get("doctop", c["top"]) + delta
            if "y0" in c:
                c["y0"] -= delta
            if "y1" in c:
                c["y1"] -= delta

    def page_lines(self, page):
        lines = self._attach_footnote_marks(super().page_lines(page))
        # Drop the running-header page number (a bare digit alone in the top
        # margin), which otherwise leaks into the body as its own paragraph.
        return [
            l
            for l in lines
            if not (l["top"] < 100 and (l.get("text") or "").strip().isdigit())
        ]

    def find_footnote_separator(self, page) -> Optional[float]:
        """Maine sets footnotes off with a short rule at the left margin
        (x0≈72, ~144pt wide). It is present on every footnote page but often
        sits well above the bottom half, where the shared finder's bottom-half
        cutoff misses it and the footnotes then fall through into the body. Key
        off the rule's distinctive signature instead, confirming footnote-sized
        (smaller-than-body) text sits just below it."""
        chars = page.chars
        if not chars:
            return None
        body = Counter(
            round(c["size"]) for c in chars if not (c.get("text") or "").isspace()
        ).most_common(1)[0][0]
        cands = sorted(
            (
                r
                for r in page.rects
                if r["height"] < 2.5
                and 70 <= r["x0"] <= 76
                and 138 <= (r["x1"] - r["x0"]) <= 152
            ),
            key=lambda r: r["top"],
        )
        for r in cands:
            below = [
                round(c["size"])
                for c in chars
                if r["top"] < c["top"] < r["top"] + 30 and not (c.get("text") or "").isspace()
            ]
            if below and min(below) < body:
                return r["top"]
        # DECLINE, DON'T DENY. The test above wants footnote-size type within
        # 30pt below the rule, which a zone opening with the unlabelled tail of
        # a note carried from the previous page cannot show — tabarek_t.h.
        # _aldarraji page 4 runs seven lines of note 1's continuation at body
        # size before note 2 begins. Returning None put the shared chain out of
        # reach, and that page cost TWO notes: 2 was never built, and 1 was
        # truncated, its continuation delivered as body prose.
        return super().find_footnote_separator(page)

    def _is_mark_line(self, line) -> bool:
        """A line that is nothing but a small footnote label — an in-body
        reference superscript (~9pt) or a hanging footnote-block number (~7pt)
        that pdfplumber split onto its own line. Capped below the body (14pt)
        and footnote text (11pt) so a header page number (12pt) is not caught."""
        chars = [c for c in (line.get("chars") or []) if (c.get("text") or "").strip()]
        if not chars or len(chars) > 3:
            return False
        text = "".join(c["text"] for c in chars).strip()
        if not text or any(ch not in self.FOOTNOTE_LABEL_CHARS for ch in text):
            return False
        return max(round(c["size"], 1) for c in chars) <= 10.0

    def _attach_footnote_marks(self, lines: list) -> list:
        """Merge each isolated small-label line into the line just below it (the
        line it marks), placing its char(s) by x. The merged label then renders
        as an inline ``<footnotemark>`` in the body, or leads its footnote text in
        the block so the per-number label split fires."""
        order = sorted(range(len(lines)), key=lambda i: (round(lines[i]["top"], 1), lines[i]["x0"]))
        consumed = set()
        for pos, i in enumerate(order):
            ln = lines[i]
            if not self._is_mark_line(ln):
                continue
            target = None
            for j in order[pos + 1 :]:  # nearest non-mark line below, within a line
                cand = lines[j]
                if cand["top"] - ln["top"] > 22:
                    break
                if not self._is_mark_line(cand):
                    target = cand
                    break
            if target is None:
                continue
            target["chars"] = sorted(
                (target.get("chars") or []) + ln["chars"], key=lambda c: c["x0"]
            )
            target["x0"] = min(c["x0"] for c in target["chars"])
            target["x1"] = max(c["x1"] for c in target["chars"])
            target["text"] = self.line_plain_text({"chars": target["chars"]})
            consumed.add(i)
        return [ln for k, ln in enumerate(lines) if k not in consumed]

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if text.upper() in _COURT_OPENERS:
            return text, ""
        if self._panel_byline(text) is not None:
            return text, ""
        return super()._byline_split(line)

    @staticmethod
    def _panel_byline(text: str):
        """A judicial-discipline panel may author jointly as a roster.

        This is distinct from the page-top ``Panel:`` metadata because it has
        no prefix and consists entirely of capitalized names plus judicial
        abbreviations.
        """
        t = (text or "").strip().rstrip(".")
        if not t or t.startswith("Panel:") or ", and " not in t:
            return None
        if not any(mark in t for mark in (", J.", ", C.J.", ", A.R.J.")):
            return None
        words = t.replace(",", " ").replace(".", " ").split()
        allowed = {"J", "CJ", "ARJ", "AND"}
        if not words or not all(word.isupper() or word.upper() in allowed for word in words):
            return None
        return t

    def parse_author_line(self, text):
        panel = self._panel_byline(text)
        if panel is not None:
            return panel, "panel", None
        return super().parse_author_line(text)
