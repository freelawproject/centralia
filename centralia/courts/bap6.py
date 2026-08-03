"""Bankruptcy Appellate Panel of the Sixth Circuit.

'NOT RECOMMENDED FOR PUBLICATION' + 'File Name:' cover lines, a
box-drawing caption (┐ │ ┘ glyphs), 'Appeal from …', the panel roster
('Before: BAUKNIGHT, Chief Judge; GREGG, and MASHBURN, Bankruptcy
Appellate Panel Judges.'), a COUNSEL block, then a centered 'OPINION'
heading and the byline with the body inline: 'JOHN T. GREGG, Bankruptcy
Appellate Panel Judge. Doug Woods, the appellant …'.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

_TITLES = (
    "Chief Bankruptcy Appellate Panel Judge",
    "Bankruptcy Appellate Panel Judge",
    "Circuit Judge",  # direct-appeal Sixth Circuit opinions in the corpus
    "Chief Judge",
    "Judge",
)


class SixthCircuitBAP(StateSupreme):
    court_id = "bap6"
    court_label = "Bankruptcy Appellate Panel of the Sixth Circuit."
    author_titles = _TITLES
    drop_notice_in_body = False
    # BAP6's ordinary body is double-spaced at roughly 20.7pt.  The shared
    # classifier's 22pt cutoff therefore mistakes nearly every body segment
    # for a single-spaced blockquote.
    gap_single_max = 18
    # True BAP6 block quotes are set in from both margins and single-spaced;
    # identify those geometrically after the ordinary body leading is fixed.
    blockquote_by_indent = True

    def parse_author_line(self, text):
        parsed = super().parse_author_line(text)
        if parsed is not None:
            return parsed
        t = (text or "").strip().rstrip(".")
        for title in _TITLES:
            suffix = ", " + title
            if not t.endswith(suffix):
                continue
            name = t[: -len(suffix)].strip()
            tokens = name.replace("-", " ").split()
            # BAP bylines can begin with an initial (``C. KATHRYN
            # PRESTON``), which the generic full-name grammar intentionally
            # excludes.  The BAP's all-caps name plus its distinctive full
            # title is sufficiently narrow.
            if 2 <= len(tokens) <= 5 and all(
                token.rstrip(".").replace("'", "").isupper()
                and token.rstrip(".").replace("'", "").isalpha()
                for token in tokens
            ):
                return name, title, None
        return None

    def _is_indented_blockquote(self, seg):
        # Issue-list continuations use a deeper hanging indent (x≈144), while
        # an actual BAP6 block quote begins at the normal quote edge (x≈108).
        # The shared broad test consequently treated list continuations as
        # quotes; keep the geometric test but reject that deeper edge.
        if not super()._is_indented_blockquote(seg):
            return False
        return min(line["x0"] for line in seg) <= self.body_baseline_x0 + 40

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        rows = result.get("summary", [])
        start = next(
            (
                i
                for i, row in enumerate(rows)
                if isinstance(row, dict)
                and row.get("__hm__")
                and "IN RE:" in str(row.get("html", ""))
            ),
            None,
        )
        end = next(
            (
                i
                for i, row in enumerate(rows)
                if i > (start if start is not None else -1)
                and isinstance(row, dict)
                and row.get("__hm__")
                and "Appeal from" in str(row.get("html", ""))
            ),
            None,
        )
        if start is None or end is None:
            return result

        left, right, source_rows = [], [], []
        for row in rows[start:end]:
            if not isinstance(row, dict) or not row.get("__hm__"):
                if row == "":
                    left.append("")
                    right.append("")
                continue
            text = str(row.get("html", ""))
            source_rows.append(text)
            marker = "│>" if "│>" in text else None
            if marker is None:
                for candidate in ("┐", "┘", "│"):
                    if candidate in text:
                        marker = candidate
                        break
            if marker is None:
                left.append(text)
                right.append("")
                continue
            ltext, rtext = text.split(marker, 1)
            left.append(ltext.strip())
            right.append(rtext.strip())

        result["summary"] = rows[:start] + [
            {
                "__caption__": True,
                "left": left,
                "right": right,
                "rail": "|",
                "shape": "old-faithful",
                "rail_rows": len(left),
                # The drawn border replaces the source rail glyphs visually;
                # retain the original rows for completeness accounting.
                "source": source_rows,
            }
        ] + rows[end:]
        return result

    def _byline_split(self, line):
        # 'JOHN T. GREGG, Bankruptcy Appellate Panel Judge. <body inline>'
        # — non-bold, period-terminated byline with the body following on
        # the same line. The panel roster ('Before: …; …, and …') never
        # matches: it starts with 'Before:' and names several judges.
        text = self.line_plain_text(line).strip()
        if text.startswith("Before"):
            return None
        for t in _TITLES:
            key = ", " + t + "."
            ki = text.find(key)
            if 0 < ki < 40:
                head = text[: ki + len(key) - 1]
                if self.parse_author_line(head) is not None:
                    return head + ".", text[ki + len(key) :].strip()
        if text.upper().startswith("PER CURIAM"):
            ends = [text.find(c) for c in ".:" if text.find(c) != -1]
            i = min(ends) if ends else -1
            if i == -1:
                return text, ""
            return text[: i + 1], text[i + 1 :].strip()
        return super()._byline_split(line)
