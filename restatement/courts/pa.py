"""Supreme Court of Pennsylvania.

Byline leads with the title and a 'DECIDED:' date: 'JUSTICE DOUGHERTY DECIDED:
MAY 19, 2026'. The panel roster ('TODD, C.J., DONOHUE, ..., JJ.') and the
running header ('[J-22-2025] [MO: Dougherty, J.]') are not verb-phrase bylines
and are excluded by the reversed-justice base.

Each opinion is filed as its own PDF and labels its kind on page 1 — 'OPINION'
(majority / announcing the judgment), 'CONCURRING OPINION', 'DISSENTING OPINION',
'CONCURRING AND DISSENTING OPINION'. The byline carries no kind, so the label is
read off page 1 and applied to the opinion.

The caption is a two-column block split by a ':' gutter — the parties on the left
('COMMONWEALTH ... Appellee / v. / JAMAR FOSTER, Appellant') and the docket +
appeal history on the right ('No. 12 WAP 2024 / Appeal from the Order ...'). It
is rendered as aligned columns so the headmatter reads cleanly instead of mashing
the two sides onto one line.
"""

from __future__ import annotations

from ._reversedjustice import ReversedJusticeSupreme

_TYPE_LABELS = {
    "OPINION": "majority",
    "OPINION ANNOUNCING THE JUDGMENT OF THE COURT": "majority",
    "CONCURRING OPINION": "concurrence",
    "DISSENTING OPINION": "dissent",
    "CONCURRING AND DISSENTING OPINION": "concurring-in-part-and-dissenting-in-part",
}


class PennsylvaniaSupreme(ReversedJusticeSupreme):
    court_id = "pa"
    court_label = "Supreme Court of Pennsylvania."

    # ------------------------------------------------------- opinion kind
    def extract(self, pdf_path):
        self._pa_type = None
        return super().extract(pdf_path)

    def find_authors(self, all_segments) -> list:
        self._pa_type = None
        for _p, seg, _k in all_segments:
            for ln in seg:
                lbl = self.line_plain_text(ln).strip().upper()
                if lbl in _TYPE_LABELS:
                    self._pa_type = _TYPE_LABELS[lbl]
                    break
            if self._pa_type:
                break
        return super().find_authors(all_segments)

    def build_opinion(self, *args, **kwargs):
        op = super().build_opinion(*args, **kwargs)
        if getattr(self, "_pa_type", None):
            op.type = self._pa_type
        return op

    # ------------------------------------------------------- headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        d = self._styled_headmatter(headmatter_segs, page1_rules)
        d["summary"] = self._fold_caption(d["summary"])
        return d

    @staticmethod
    def _fold_caption(rows: list) -> list:
        """Collapse the run of ':'-gutter caption rows into one two-column
        ``__caption__`` block (parties left, docket/appeal history right)."""
        out, left, right = [], [], []

        def flush():
            if left or right:
                out.append({"__caption__": True, "left": list(left), "right": list(right)})
                left.clear()
                right.clear()

        for r in rows:
            html = r.get("html", "") if isinstance(r, dict) else str(r)
            text = _strip_tags(html)
            # The gutter colon is set off by spaces (' : '); a colon inside a
            # party name ('IN RE: DRAVO ...') has no leading space, so splitting
            # on ' : ' targets only the real gutter.
            if " : " in text:
                lpart, rpart = text.split(" : ", 1)
                if lpart.strip():
                    left.append(lpart.strip())
                if rpart.strip():
                    right.append(rpart.strip())
            elif text.startswith(":"):
                rest = text[1:].strip()
                if rest:
                    right.append(rest)  # right-only continuation line
            elif text.endswith(":"):
                rest = text[:-1].strip()
                if rest:
                    left.append(rest)  # left-only line ending at the gutter
            else:
                flush()
                out.append(r)
        flush()
        return out


def _strip_tags(html: str) -> str:
    out, depth = [], 0
    for ch in html:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    import html as _h

    return _h.unescape("".join(out)).strip()
