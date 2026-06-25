"""Identify a court opinion's case-caption style from page 1, structurally.

A first-cut classifier for the caption taxonomy catalogued at /captions. It reads
the two layers pdfplumber exposes — the vector layer (page.rects / page.lines:
drawn rules and boxes) and the glyph layer (page.chars: punctuation columns that
stand in for rules, plus fonts and seals) — and reports the detected facets and a
best-guess style name.

    from centralia.caption_id import classify_caption
    print(classify_caption("assets/kan/king_v._schwert.pdf"))

CLI:  uv run python -m centralia.caption_id <pdf> [<pdf> ...]
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

# Punctuation glyphs courts stack into a vertical "rail" instead of drawing a rule.
_RAIL_GLYPHS = {
    ")": "parens )",
    ":": "colon :",
    "§": "section §",
    "]": "bracket ]",
    "*": "asterisk *",
    "|": "pipe |",
}

# (columns, divider) -> the catalogued style it most resembles.
_MATCH = {
    ("two-column", "parens )"): "Parenthetical Box / Banded Bracket",
    ("two-column", "colon :"): "Colon Rail",
    ("two-column", "section §"): "Section-Sign Rail (Texas)",
    ("two-column", "bracket ]"): "Square-Bracket Rail (N.D. Ala.)",
    ("two-column", "asterisk *"): "Asterisk Rail (Maryland)",
    ("two-column", "double-pipe ||"): "Twin Rail (N.D. Iowa)",
    ("two-column", "pipe |"): "Old Faithful (typed pipe)",
    ("two-column", "rule"): "Old Faithful / drawn vertical rule",
    ("two-column", "box edge"): "Full Box",
    ("two-column", "slash /"): "Florida / Nevada slash",
    ("two-column", "whitespace gutter"): "flush two-column (whitespace gutter)",
    ("two-column", "none"): "flush / inline (no divider glyph)",
    ("three-column", "box edge"): "Three-Cell Ledger (Puerto Rico)",
    ("three-column", "rule"): "three-column ruled",
    ("one-column", "none"): "centered stack (one-column)",
}


@dataclass
class CaptionStyle:
    columns: str = "one-column"
    divider: str = "none"
    box: bool = False
    rules_h: int = 0
    double_rule: bool = False
    markers: list = field(default_factory=list)  # seal, slash, x-caps, blackletter, ...
    match: str = "?"
    evidence: dict = field(default_factory=dict)

    def __repr__(self):
        m = (" +" + ",".join(self.markers)) if self.markers else ""
        box = " box" if self.box else ""
        return (f"<{self.columns} | divider={self.divider}{box} "
                f"| h-rules={self.rules_h}{'(double)' if self.double_rule else ''}{m} "
                f"| ~ {self.match}>")


def _thin(obj, *, vertical):
    w = abs(obj["x1"] - obj["x0"])
    h = abs(obj["bottom"] - obj["top"])
    if vertical:
        return w < 3.0 and h > 55.0   # a real caption rule, not a short table line
    return h < 3.0 and w > 60.0


_DOCKET_CUES = ("no.", "no:", "no ", "case", "civil", "index", "docket",
                "c.a.", "cause", "record no", "bap", "bk.", "bankr")


def _right_metadata(chars, W):
    """A whitespace-gutter two-column caption is given away by metadata in the
    RIGHT column — a docket cue (No. / Case No. / Civil Action / Index No. …)
    whose token starts in the right portion of the page, with party text to its
    left. Centered one-column captions put the docket in the MIDDLE, so they
    don't trip this. Returns True if found."""
    from collections import defaultdict

    rows = defaultdict(list)
    for c in chars:
        rows[round(c["top"] / 4)].append(c)
    for row in rows.values():
        right = sorted((c for c in row if c["x0"] > W * 0.55), key=lambda c: c["x0"])
        has_left = any(c["x0"] < W * 0.42 for c in row)
        if not right or not has_left:
            continue
        rtext = "".join(c["text"] for c in right).lower()
        if any(q in rtext for q in _DOCKET_CUES) and any(ch.isdigit() for ch in rtext):
            return True
    return False


def classify_caption(pdf_path: str, page_index: int = 0) -> CaptionStyle:
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_index]
        W, H = page.width, page.height
        top_cut = H * 0.58  # the caption lives in the upper part of page 1
        chars = [c for c in page.chars if c["top"] < top_cut and not c["text"].isspace()]
        graphics = list(page.rects) + [
            {"x0": min(l["x0"], l["x1"]), "x1": max(l["x0"], l["x1"]),
             "top": min(l["top"], l["bottom"]), "bottom": max(l["top"], l["bottom"])}
            for l in page.lines
        ]
        ev = {}

        # -- vector rules ------------------------------------------------------
        v_rules = sorted(
            (g["x0"] + g["x1"]) / 2
            for g in graphics
            if g["top"] < top_cut and _thin(g, vertical=True) and 90 < (g["x0"]+g["x1"])/2 < W-40
        )
        h_rules = sorted(
            g["top"] for g in graphics
            if g["top"] < top_cut and _thin(g, vertical=False)
        )
        # collapse near-duplicate verticals (a "box" edge often doubles)
        v_uniq = []
        for x in v_rules:
            if not v_uniq or abs(x - v_uniq[-1]) > 8:
                v_uniq.append(x)
        # double rule = two horizontals within ~5pt
        double_rule = any(0 < h_rules[i+1]-h_rules[i] < 5 for i in range(len(h_rules)-1))
        ev["v_rules"] = [round(x) for x in v_uniq]
        ev["h_rules"] = len(h_rules)

        # -- box: verticals plus a horizontal near the top AND bottom of them --
        box = False
        if v_uniq and h_rules:
            vtops = [g for g in graphics if _thin(g, vertical=True)]
            if vtops:
                top_v = min(g["top"] for g in vtops)
                bot_v = max(g["bottom"] for g in vtops)
                has_top = any(abs(t - top_v) < 12 for t in h_rules)
                has_bot = any(abs(t - bot_v) < 12 for t in h_rules)
                box = has_top and has_bot and len(v_uniq) >= 2

        # -- glyph rails: a column of one glyph repeated down the rows ---------
        best = None  # (label, x, rows)
        for glyph, label in _RAIL_GLYPHS.items():
            buckets = defaultdict(set)
            for c in chars:
                if c["text"] == glyph and 110 < c["x0"] < W - 50:
                    buckets[round(c["x0"] / 5)].add(round(c["top"] / 5))
            if not buckets:
                continue
            xb, rows = max(buckets.items(), key=lambda kv: len(kv[1]))
            if len(rows) >= 4 and (best is None or len(rows) > best[2]):
                best = (label, xb * 5, len(rows))
        # twin pipe: two pipe columns close together
        if best and best[0] == "pipe |":
            pipe_xs = sorted({round(c["x0"]) for c in chars if c["text"] == "|"})
            if any(0 < pipe_xs[i+1]-pipe_xs[i] < 6 for i in range(len(pipe_xs)-1)):
                best = ("double-pipe ||", best[1], best[2])
        ev["rail"] = best

        # -- decide divider + column count ------------------------------------
        st = CaptionStyle(double_rule=double_rule, rules_h=len(h_rules), evidence=ev)
        interior_v = [x for x in v_uniq if 120 < x < W - 90]
        if box:
            st.box = True
            st.divider = "box edge"
            # interior verticals beyond the box's two edges => extra columns
            st.columns = "three-column" if len(v_uniq) >= 3 else "two-column"
        elif best:
            st.divider = best[0]
            st.columns = "two-column"
        elif interior_v:
            st.divider = "rule"
            st.columns = "three-column" if len(interior_v) >= 2 else "two-column"
        elif _right_metadata(chars, W):
            st.divider = "whitespace gutter"
            st.columns = "two-column"
        else:
            st.divider = "none"
            st.columns = "one-column"

        # -- special markers ---------------------------------------------------
        markers = []
        # seal: a centered, roughly-square image near the top (not a logo strip)
        for im in page.images:
            w, h = im["x1"]-im["x0"], im["bottom"]-im["top"]
            cx = (im["x0"]+im["x1"]) / 2
            if im["top"] < H*0.33 and 40 < w < 200 and 40 < h < 200 \
               and 0.6 < w/max(1, h) < 1.7 and W*0.3 < cx < W*0.7:
                markers.append("seal")
                break
        # slash terminator: a "/" sitting at the right tip of an underscore run or a
        # drawn horizontal rule (Florida/Nevada) — NOT a date like 05/03/2024.
        unders = [c for c in chars if c["text"] == "_"]
        h_ends = [(g["top"], g["x1"]) for g in graphics
                  if g["top"] < top_cut and _thin(g, vertical=False)]
        for s in (c for c in chars if c["text"] == "/"):
            near_underscore = any(abs(u["top"]-s["top"]) < 3 and 0 < s["x0"]-u["x1"] < 25
                                  for u in unders)
            near_rule_end = any(abs(t-s["top"]) < 8 and abs(x1-s["x0"]) < 12
                                for t, x1 in h_ends)
            if near_underscore or near_rule_end:
                markers.append("slash /")
                if st.divider == "none":
                    st.divider, st.columns = "slash /", "two-column"
                break
        # x-caps: an "X" at the right tip of a hyphen run (NY pleading box)
        if st.divider == "colon :" and any(
                c["text"] in ("X", "x") and c["x0"] > W * 0.45 for c in chars):
            markers.append("x-caps")
        # blackletter banner: the top centered line's font differs from the body font
        body_font = _modal_font([c for c in page.chars if c["top"] > H * 0.6])
        ban = _modal_font([c for c in chars if c["top"] < H * 0.18])
        if ban and body_font and _family(ban) != _family(body_font):
            markers.append(f"unusual-banner-font({_family(ban)})")
        # numbered gutter: small digits stacked at the far-left margin
        left_digits = {round(c["top"]) for c in chars
                       if c["text"].isdigit() and c["x0"] < 70}
        if len(left_digits) >= 6:
            markers.append("numbered-gutter")
        st.markers = markers

        st.match = _MATCH.get((st.columns, st.divider), "(unmatched)")
        return st


def _modal_font(chars):
    from collections import Counter
    fonts = Counter((c.get("fontname") or "") for c in chars)
    return fonts.most_common(1)[0][0] if fonts else ""


def _family(fontname: str) -> str:
    return (fontname or "").split("+")[-1]


def main(argv):
    for path in argv:
        try:
            print(f"{path}\n   {classify_caption(path)!r}")
        except Exception as exc:
            print(f"{path}\n   ERROR: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
