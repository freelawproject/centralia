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
        lines = super().page_lines(page)
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
                merged = dict(l)
                merged["chars"] = (l.get("chars") or []) + (
                    lines[i + 1].get("chars") or []
                )
                out.append(merged)
                i += 2
                continue
            out.append(l)
            i += 1
        return out

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
