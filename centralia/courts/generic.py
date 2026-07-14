"""Generic fallback extractor — broad defaults for an unknown court id.

Does not attempt to parse structured headmatter (parties, panel, etc.); it
classifies the document type, emits the court label, and extracts whatever
opinion bodies + footnotes the core pipeline detects. Write a per-court
subclass under ``centralia/courts/<court>/`` when a court needs tuning.
"""

from __future__ import annotations

from typing import Optional

from ..base import BaseExtractor


_TITLE_WORDS = ("Justice", "Judge", "Chancellor")


class GenericExtractor(BaseExtractor):
    author_titles = (
        "Chief Justice",
        "Presiding Justice",
        "Associate Justice",
        "Senior Justice",
        "Vice Chief Justice",
        "Justice",
        "Chief Judge",
        "Presiding Judge",
        "Senior Circuit Judge",
        "Circuit Judge",
        "District Judge",
        "Bankruptcy Judge",
        "Magistrate Judge",
        "Senior Judge",
        "Judge",
    )

    # ---------------------------------------------------------------- bylines
    # The common opinion-start marker across courts: a BOLD judge-name line,
    # often running inline with the opinion text — 'AFRAME, Circuit Judge. This
    # is an appeal...' / 'Fagone, U.S. Bankruptcy Appellate Panel Judge.' /
    # 'PER CURIAM. ...'. A 'Before ... Judges.' panel line (plural title) is the
    # roster, NOT the author, and is excluded.
    def find_authors(self, all_segments) -> list:
        out = []
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if not seg:
                continue
            line = seg[0]
            if self._byline_split(line) is not None or self.parse_author_line(
                (line.get("text") or "").strip()
            ):
                out.append(i)
        return out

    def _byline_at(self, line) -> bool:
        return self._byline_split(line) is not None or super()._byline_at(line)

    def _opinion_has_body(self, all_segments, start, end) -> bool:
        """True if the byline at ``start`` has an opinion body before ``end``:
        either inline body on the byline line, or a following non-byline
        segment. A byline with no body is a sign-off / trial-judge history
        line / announcement, not an opinion start."""
        seg0 = all_segments[start][1]
        if seg0:
            split = self._byline_split(seg0[0])
            if (split and split[1]) or len(seg0) > 1:
                return True
        for k in range(start + 1, end):
            seg = all_segments[k][1]
            if seg and self._byline_split(seg[0]) is None:
                return True
        return False

    def split_author_line(self, line) -> tuple:
        r = self._byline_split(line)
        if r is None:
            return super().split_author_line(line)
        byline, body = r
        if not body:
            return byline, []
        chars = line.get("chars") or []
        target = len("".join(byline.split()))
        cnt, idx = 0, len(chars)
        for k, c in enumerate(chars):
            if not c.get("text", "").isspace():
                cnt += 1
            if cnt >= target:
                idx = k + 1
                break
        body_chars = chars[idx:]
        body_line = dict(line)
        body_line["text"] = body
        body_line["chars"] = body_chars
        if body_chars:
            body_line["x0"] = body_chars[0]["x0"]
        return byline, [body_line]

    def _byline_split(self, line):
        """If ``line`` begins with a BOLD judge-name byline, return
        (byline_text, body_text); else None. byline runs to the first '.'/':'
        after the title; body_text is the inline opinion text after it."""
        text = (line.get("text") or "").strip()
        chars = line.get("chars") or []
        if not text or not chars:
            return None
        if "bold" not in chars[0].get("fontname", "").lower():
            return None
        up = text.upper()
        if up.startswith("PER CURIAM"):
            i = text.find(".")
            return (text, "") if i == -1 else (text[: i + 1], text[i + 1 :].strip())
        if up.startswith("BEFORE "):  # panel roster, not the author
            return None
        if "," not in text:
            return None
        name = text.split(",", 1)[0].strip()
        if not _is_name(name):
            return None
        head = text.split(",", 1)[1][:60]
        # a singular title (plural 'Judges'/'Justices' = a panel listing)
        singular = (
            ("Judge" in head and "Judges" not in head)
            or ("Justice" in head and "Justices" not in head)
            or "Chancellor" in head
        )
        if not singular:
            return None
        ti = min((text.find(t) for t in _TITLE_WORDS if text.find(t) != -1), default=-1)
        end = next((k for k in range(ti, len(text)) if text[k] in ".:"), -1)
        if end == -1:
            return text, ""
        return text[: end + 1], text[end + 1 :].strip()

    def find_footnote_separator(self, page) -> Optional[float]:
        cutoff = page.height * 0.55
        # A full-width rule may be a section/caption divider rather than a
        # footnote separator (taking it as the footnote rule shoves the body
        # into the footnote flow). Discriminate by what's below it — footnote
        # rules carry footnote-size text below; dividers carry body-size text.
        candidates = [
            r
            for r in page.rects
            if r["height"] < 2
            and (r["x1"] - r["x0"]) >= 100
            and r["x0"] < 100
            and r["top"] > cutoff
            and self._rule_over_footnotes(page, r["top"])
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda r: r["top"])["top"]

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = BaseExtractor.extract_headmatter(
            self, headmatter_segs, page1_rules=page1_rules
        )
        out["court"] = self.court_label or self.court_id
        return out


def _is_name(name: str) -> bool:
    """A judge name: 1–5 capitalized tokens (all-caps 'AFRAME' or title-case
    'Edith Brown Clement'), allowing initials/periods/hyphens."""
    toks = name.split()
    if not toks or len(toks) > 5:
        return False
    for tok in toks:
        core = tok.strip(".'-").replace("'", "")
        clean = core.replace(".", "")  # joined initials 'N.R.' -> 'NR'
        if not clean or not core[0].isupper() or not clean.isalpha():
            return False
    return True
