"""Alaska-specific layout overrides shared by Alaska Supreme and Ct of App.

No regex (see the project's no-regex preference): the parsing leans on font
style, position, and plain string patterns instead.

Page-1 structure (both Alaska courts):

  1. Notice  — a 'NOTICE' header + an italic correction block, at the very top.
  2. Court name banner ('IN THE COURT OF APPEALS OF THE STATE OF ALASKA' /
     'THE SUPREME COURT OF THE STATE OF ALASKA').
  3. Two-column case caption, split by a column of `)` chars at x≈306:
     LEFT = party names + roles, RIGHT = Supreme/Superior Court Nos.,
     'O P I N I O N', 'No. 7802 – Feb 20, 2026'.
  4. Single-column metadata (still caption): 'Appeal from ...' (history),
     'Appearances: ...' (attorneys), 'Before: ...' (judges).
  5. The opinion body, opening with an author byline.

The notice is everything before the court banner — dropped into the review
'Removed' bucket; everything from the banner on is returned verbatim.
"""

from __future__ import annotations

from typing import Optional

from ..base import BaseExtractor
from ..models import Block


# x0 < 250 => LEFT caption column (party names); >= 250 => RIGHT column
# (docket / opinion label / date). The `)` divider sits at x≈306.
_COLUMN_SPLIT_X = 250

_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

# Author title prefixes, longest first so "Chief Justice" wins over "Justice".
_TITLES = (
    "Chief Justice",
    "Senior Justice",
    "Presiding Justice",
    "Associate Justice",
    "Chief Judge",
    "Senior Judge",
    "Presiding Judge",
    "Justice",
    "Judge",
)

_DOCKET_PREFIXES = ("Supreme Court No.", "Court of Appeals No.")
_LOWER_PREFIXES = ("Superior Court No.", "Trial Court No.", "District Court No.")
_DASHES = "–—-"


class BaseAlaskaExtractor(BaseExtractor):
    # Alaska body is more tightly spaced than Alabama's.
    gap_tight_max = 13.5
    gap_single_max = 18.0
    gap_double_max = 28.0

    # ---------------------------------------------------------------- pipeline
    def extract(self, pdf_path):
        """Base pipeline, then promote Alaska section headings (bold ALL-CAPS
        lines like 'FACTS AND PROCEEDINGS' and 'A. ...' subsections) from
        paragraphs to heading blocks. The big roman section numerals are
        decorative images and are left as the base produced them."""
        doc = super().extract(pdf_path)
        for op in doc.opinions:
            op.blocks = [self._maybe_heading(b) for b in op.blocks]
        return doc

    @staticmethod
    def _maybe_heading(block):
        if block.kind != "p" or not block.text:
            return block
        t = block.text.strip()
        words = t.split()
        caps = (
            t.upper() == t
            and any(c.isalpha() for c in t)
            and 1 <= len(words) <= 7
            and not t.endswith(".")
        )
        sub = (
            len(t) >= 3
            and "A" <= t[0] <= "Z"
            and t[1] == "."
            and t[2:3] == " "
            and len(words) <= 10
        )
        if caps or sub:
            block.kind = "heading"
        return block

    # ---------------------------------------------------------------- author
    def find_authors(self, all_segments) -> list:
        """Author bylines, minus any with no opinion body before the next one —
        a 'Judge X, writing for the Court.' cover/summary byline repeated above
        the opinion proper would otherwise spawn an empty opinion."""
        cands = [
            i
            for i, (_p, seg, kind) in enumerate(all_segments)
            if kind != "notice"
            and seg
            and self.parse_author_line((seg[0].get("text") or "").strip())
        ]
        out = []
        for n, i in enumerate(cands):
            end = cands[n + 1] if n + 1 < len(cands) else len(all_segments)
            seg0 = all_segments[i][1]
            has_body = len(seg0) > 1 or any(
                all_segments[k][1] and not self._byline_at(all_segments[k][1][0])
                for k in range(i + 1, end)
            )
            if has_body:
                out.append(i)
        return out

    def parse_author_line(self, text):
        """Standard 'PATE, Justice.' (handled by the base) plus the reversed
        Alaska Court of Appeals form 'Judge HARBISON, writing for the Court.'."""
        result = super().parse_author_line(text)
        if result is not None:
            return result
        return self._parse_reversed_author(text)

    @staticmethod
    def _parse_reversed_author(text):
        t = text.strip()
        if t.endswith("."):
            t = t[:-1]
        for title in _TITLES:
            if not t.startswith(title + " "):
                continue
            rest = t[len(title) + 1 :].strip()
            if "," in rest:
                name, kind = rest.split(",", 1)
                name, kind = name.strip(), kind.strip()
            else:
                name, kind = rest.strip(), None
            if not _is_caps_name(name):
                return None
            if kind and "writing" in kind.lower():
                kind = None  # 'writing for the Court' = majority
            return name, title, kind
        return None

    # ---------------------------------------------------------------- caption
    def find_caption_divider(self, page):
        """(x, top, bottom) of the caption column divider, or None. A vertical
        rect/line (Ct of App) or a column of `)` chars (Supreme)."""
        for r in page.rects:
            if r["width"] < 2 and r["height"] > 30:
                return r["x0"], r["top"], r["bottom"]
        for ln in page.lines:
            x0 = ln["x0"]
            x1 = ln.get("x1", x0)
            if abs(x1 - x0) < 2 and (ln["bottom"] - ln["top"]) > 30:
                return x0, ln["top"], ln["bottom"]
        from collections import Counter

        paren_chars = [c for c in page.chars if c.get("text") == ")"]
        if len(paren_chars) < 3:
            return None
        buckets = Counter(round(c["x0"] / 2) * 2 for c in paren_chars)
        bucket_x, count = buckets.most_common(1)[0]
        if count < 3:
            return None
        matching = [c for c in paren_chars if abs(c["x0"] - bucket_x) < 2]
        return (
            float(bucket_x),
            min(c["top"] for c in matching),
            max(c["bottom"] for c in matching),
        )

    def page_lines(self, page):
        """Extract lines, column-splitting caption rows that span a vertical
        column divider."""
        divider = self.find_caption_divider(page)
        if divider is None:
            return super().page_lines(page)

        div_x, div_top, div_bot = divider
        m_top, m_bot = self.margin_top, self.margin_bottom

        def in_body_margin(obj):
            return m_top <= obj["top"] <= m_bot

        def outside_caption(obj):
            return in_body_margin(obj) and not (div_top <= obj["top"] <= div_bot)

        def left_of_divider(obj):
            return (
                in_body_margin(obj)
                and div_top <= obj["top"] <= div_bot
                and obj["x1"] <= div_x
            )

        def right_of_divider(obj):
            return (
                in_body_margin(obj)
                and div_top <= obj["top"] <= div_bot
                and obj["x0"] >= div_x
            )

        lines = []
        lines += page.filter(outside_caption).extract_text_lines()
        lines += page.filter(left_of_divider).extract_text_lines()
        lines += page.filter(right_of_divider).extract_text_lines()
        lines.sort(key=lambda l: (l["top"], l["x0"]))
        return lines

    # ---------------------------------------------------------------- footnote
    def find_footnote_separator(self, page) -> Optional[float]:
        """Hairline rect = footnote separator. Left-anchored rect, width >= 100,
        height < 2, in the bottom ~45% of the page (so the caption underline up
        top isn't mis-classified)."""
        cutoff = page.height * 0.55
        candidates = [
            r
            for r in page.rects
            if r["height"] < 2
            and (r["x1"] - r["x0"]) >= 100
            and r["x0"] < 100
            and r["top"] > cutoff
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda r: r["top"])["top"]

    # ---------------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = {
            "decisiondate": None,
            "court": self.court_label,
            "docketnumber": None,
            "parties": [],
            "motion": None,
            "parentcase": None,
            "lowercourt": None,
            "history": None,
            "attorneys": None,
            "judges": None,
            "otherdocket": None,
        }
        party_lines = []
        summary_pos = []  # (top, x0, text) for layout-preserved summary
        notice_lines = []
        current_block = None  # in-progress labeled block: history/attorneys/judges

        # The notice sits before the court banner. If the banner is present,
        # everything before it is the notice; otherwise we drop nothing.
        has_banner = any(
            self._is_banner((ln.get("text") or "").strip())
            for seg in headmatter_segs
            for ln in seg
        )
        seen_banner = not has_banner

        for seg in headmatter_segs:
            for line in seg:
                text = (line.get("text") or "").strip()
                if not text:
                    continue

                if not seen_banner:
                    if self._is_banner(text):
                        seen_banner = True
                        summary_pos.append((round(line["top"]), line["x0"], text))
                    else:
                        notice_lines.append(text)
                    continue

                summary_pos.append((round(line["top"]), line["x0"], text))
                x0 = line["x0"]

                if x0 >= _COLUMN_SPLIT_X:
                    self._extract_right_column(text, out)
                    continue

                lt = text.lower()
                if lt.startswith("appeal from"):
                    out["history"] = self._extend(out.get("history"), text)
                    current_block = "history"
                    continue
                if text.startswith("Appearances:"):
                    out["attorneys"] = self._extend(
                        out.get("attorneys"), text[len("Appearances:") :].strip()
                    )
                    current_block = "attorneys"
                    continue
                if text.startswith("Before:"):
                    out["judges"] = self._extend(
                        out.get("judges"), text[len("Before:") :].strip()
                    )
                    current_block = "judges"
                    continue
                if current_block is not None and 100 <= x0 < _COLUMN_SPLIT_X:
                    out[current_block] = self._extend(out.get(current_block), text)
                    continue

                cleaned = text.rstrip(") ").strip()
                if cleaned and cleaned != ")":
                    party_lines.append(cleaned)

        if out["decisiondate"] is None and out["otherdocket"]:
            d = self._find_date(out["otherdocket"])
            if d:
                out["decisiondate"] = d

        out["parties"] = party_lines
        out["summary"] = self._layout_rows(summary_pos)
        out["dropped"] = [" ".join(notice_lines)] if notice_lines else []
        return out

    @staticmethod
    def _is_banner(text: str) -> bool:
        """The court-name banner: an ALL-CAPS line naming the court/state."""
        u = text.upper()
        return text == u and "COURT" in u and "ALASKA" in u and len(text.split()) >= 4

    @staticmethod
    def _extend(prev, addition):
        return (prev + " " + addition) if prev else addition

    def _extract_right_column(self, text, out):
        """Right-column caption data — court numbers, opinion no., date. Plain
        string matching, no regex."""
        t = text.lstrip(") ").strip()

        for prefix in _DOCKET_PREFIXES:
            if prefix in t and out["docketnumber"] is None:
                out["docketnumber"] = t[t.index(prefix) :].strip()
                return
        for prefix in _LOWER_PREFIXES:
            if prefix in t:
                out["lowercourt"] = t[t.index(prefix) :].strip()
                return
        if "".join(t.split()).upper() == "OPINION":
            return  # decorative 'O P I N I O N'
        if t.startswith("No."):
            toks = t.split()
            if len(toks) >= 2:
                out["otherdocket"] = "No. " + toks[1]
            d = self._find_date(t)
            if d:
                out["decisiondate"] = d

    @staticmethod
    def _find_date(text: str) -> Optional[str]:
        """Return a 'Month D, YYYY' substring, or None. No regex."""
        words = text.split()
        for i, w in enumerate(words):
            if w.strip(",.") in _MONTHS and i + 1 < len(words):
                return " ".join(words[i:]).strip()
        return None

    @staticmethod
    def _layout_rows(items: list) -> list:
        """Reconstruct the caption's visual layout: lines sharing a row (same
        ``top``) are placed on one text line, each at a column derived from its
        x0, so the two-column caption lines up when rendered in a whitespace-
        preserving block."""
        if not items:
            return []
        items.sort(key=lambda r: (r[0], r[1]))
        char_w = 6.2  # approx caption glyph advance (pt)
        rows, segs, cur_top = [], [], None

        def emit(parts):
            line = ""
            for x0, text in parts:
                col = max(len(line) + (1 if line else 0), int((x0 - 72) / char_w))
                line += " " * (col - len(line)) + text
            return line

        for top, x0, text in items:
            if cur_top is not None and abs(top - cur_top) > 3:
                rows.append(emit(segs))
                segs = []
            segs.append((x0, text))
            cur_top = top
        if segs:
            rows.append(emit(segs))
        return rows


def _is_caps_name(name: str) -> bool:
    """True if ``name`` looks like an ALL-CAPS surname (optionally Mc/Mac),
    e.g. 'HARBISON', 'McCONAHY', 'TERRELL JOINS' is rejected via word count."""
    toks = name.split()
    if not toks or len(toks) > 2:
        return False
    for tok in toks:
        core = tok
        if core.startswith("Mc"):
            core = core[2:]
        elif core.startswith("Mac"):
            core = core[3:]
        if not (core and core.isalpha() and core.isupper()):
            return False
    return True
