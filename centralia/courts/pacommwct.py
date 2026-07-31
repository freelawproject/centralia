"""Commonwealth Court of Pennsylvania.

':'-rail caption with the docket/'Submitted:' dates in the right column,
a 'BEFORE: HONORABLE …, Judge' panel roster, then the title-first byline —
'OPINION BY JUDGE McCULLOUGH' / 'MEMORANDUM OPINION BY SENIOR JUDGE …' /
'DISSENTING OPINION BY JUDGE …' — often sharing its visual row with the
caption's right column ('BY JUDGE McCULLOUGH   FILED: May 18, 2026').
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

_BY_KEYS = (
    "OPINION BY ",
    "MEMORANDUM OPINION BY ",
    "DISSENTING OPINION BY ",
    "CONCURRING OPINION BY ",
    "OPINION NOT REPORTED",
)
_TITLE_WORDS = ("JUDGE", "PRESIDENT", "SENIOR")


class PennsylvaniaCommonwealthCourt(StateSupreme):
    court_id = "pacommwct"
    court_label = "Commonwealth Court of Pennsylvania."

    def parse_author_line(self, text):
        t = text.strip()
        up = t.upper()
        # 'OPINION BY JUDGE McCULLOUGH [FILED: …]' — title-first; the name
        # is the token run after the title words, before any 'FILED:' tail
        bi = up.find("BY")
        if (
            any(up.startswith(k.rstrip()) for k in _BY_KEYS)
            or (up.startswith("BY") and any(w in up for w in _TITLE_WORDS))
        ) and bi >= 0:
            # a re-joined wrapped byline can lack the space ('OPINION
            # BYPRESIDENT JUDGE …') — split right after the 'BY' token
            after = t[bi + 2 :].lstrip()
            toks, name = after.split(), []
            for tok in toks:
                core = tok.strip(".,:")
                cu = core.upper()
                if cu in ("JUDGE", "SENIOR", "PRESIDENT", "PRESIDENT,", "HONORABLE"):
                    continue
                if cu.startswith("FILED"):
                    break
                if core and core[0].isupper():
                    name.append(core)
                else:
                    break
            if name:
                kind = (
                    "dissenting" if "DISSENT" in up
                    else "concurring" if "CONCURR" in up else None
                )
                return " ".join(name), "Judge", kind
        return super().parse_author_line(text)

    # the byline can WRAP: 'OPINION BY' / 'PRESIDENT JUDGE COHN JUBELIRER
    # FILED: …' — join the dangling 'BY' line with the next so it parses
    def page_lines(self, page):
        # Lift the filing date off every byline row FIRST, so a byline that
        # wraps is joined without dragging the date into the join.
        lines = [self._cut_filed_zone(l) for l in super().page_lines(page)]
        out, i = [], 0
        while i < len(lines):
            l = lines[i]
            t = self.line_plain_text(l).strip().upper()
            if (
                i + 1 < len(lines)
                and t.endswith(" BY")
                and len(t) < 40
                and "OPINION" in t
            ):
                nxt = lines[i + 1]
                merged = dict(l)
                merged["chars"] = (l.get("chars") or []) + (nxt.get("chars") or [])
                # ``line_plain_text`` prefers a line's cached ``text``, so the
                # joined text has to be rebuilt too — otherwise the byline
                # parses against the dangling 'OPINION BY' alone and the author
                # comes out as the prefix.
                merged["text"] = (
                    self.line_plain_text(l).rstrip()
                    + " "
                    + self.line_plain_text(nxt).lstrip()
                )
                merged["x1"] = max(l.get("x1", 0), nxt.get("x1", 0))
                out.append(merged)
                i += 2
                continue
            out.append(l)
            i += 1
        return out

    def _cut_filed_zone(self, line):
        """Lift the filing date out of the byline's row.

        The byline shares its visual row with the last entry of the caption's
        right column — 'BY JUDGE McCULLOUGH        FILED: May 18, 2026' — two
        zones separated by a wide (>25pt) gap that pdfplumber merges into one
        line. The row opens the opinion, so keeping the date on it put a caption
        entry inside the byline; cutting it without recording it lost the date
        outright (the whole row then matched nothing and read as unplaced
        content). Split at the gap: the byline keeps the left zone, and the right
        zone is held for the headmatter, where the rest of that column lives."""
        chars = line.get("chars") or []
        text = self.line_plain_text(line).strip()
        up = text.upper()
        if len(chars) < 4 or "FILED" not in up:
            return line
        if not (" BY " in up or up.startswith("BY ") or "JUDGE" in up):
            return line
        # The gap that separates the two zones (widest run boundary >25pt).
        cut, best = None, 25.0
        prev = chars[0].get("x1", 0)
        for k, c in enumerate(chars[1:], 1):
            gap = c.get("x0", 0) - prev
            if gap > best:
                best, cut = gap, k
            prev = max(prev, c.get("x1", 0))
        if cut is None:
            return line
        left = [c for c in chars[:cut] if not (c.get("text") or "").isspace()]
        right = chars[cut:]
        rtext = self.line_plain_text({"chars": right}).strip()
        if not left or "FILED" not in rtext.upper():
            return line
        self._pa_filed.append(rtext)
        kept = dict(line)
        kept["chars"] = chars[:cut]
        kept["text"] = self.line_plain_text({"chars": chars[:cut]}).strip()
        kept["x1"] = max(c.get("x1", 0) for c in left)
        return kept

    def extract(self, pdf_path):
        self._pa_filed = []
        return super().extract(pdf_path)

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Close the headmatter with the filing date lifted off the byline row —
        it is the last entry of the caption's flush-right column ('No. 1552 C.D.
        2022' / 'Submitted: April 13, 2026' / 'FILED: May 18, 2026'), so it is
        rendered right-aligned in that column's own place."""
        d = super().extract_headmatter(headmatter_segs, page1_rules)
        for text in dict.fromkeys(getattr(self, "_pa_filed", None) or []):
            d["summary"] = list(d["summary"]) + [
                {"__hm__": True, "html": text, "rel": 1.0, "align": "R"}
            ]
        return d

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        up = text.upper()
        if (" BY " in up or up.startswith("BY ")) and any(
            w in up for w in _TITLE_WORDS
        ):
            if self.parse_author_line(text) is not None:
                # the caption's right column can share the row — keep only
                # the byline ('BY JUDGE McCULLOUGH   FILED: May 18' → cut)
                fi = up.find("FILED")
                if fi > 0:
                    text = text[:fi].rstrip()
                return text, ""
        return super()._byline_split(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        """Type the accompanying ORDER as an order, not a second majority.

        Every Commonwealth Court opinion closes with a conformed signature
        ('_____ / PATRICIA A. McCULLOUGH, Judge') and is followed by a separate
        ORDER page carrying the caption again, the centered 'ORDER' header, the
        decree and the same signature. The signature line parses as a byline, so
        that trailing material opened what looked like a second majority opinion
        — the 'over-identifying opinions because you see a judge name' the review
        notes flag. An announced writing always names itself with 'BY' ('OPINION
        BY JUDGE …', 'CONCURRING OPINION BY …'); a bare signature never does, so
        the bare form is the order."""
        op = super().build_opinion(op_start, op_end, **kwargs)
        if op.author and "BY" not in op.author.upper().split():
            op.type = "order"
        return op
