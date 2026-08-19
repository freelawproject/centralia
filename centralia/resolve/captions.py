"""Page-1 caption fingerprint: geometry signature -> catalog style.

Port of the old captionfp.py onto the shared PageModel — same facets, same
ordered matrix, but no second parse of the page and no swallowed exceptions.
The signature dict is stored on the CaptionBlock the headmatter resolver
builds, and the renderer draws borders from THAT object, so the label and the
reproduction cannot disagree.

Facets: verticals (left/mid/right, twin), h_top/h_bottom span (full/left/
right), glyph rail + its band, typed rules (dash runs, x-capped) + the band
they enclose, diagonals, pleading gutter, flush-right status rows, two-column
whitespace rows.
"""

from __future__ import annotations

from collections import Counter

from ..pdfio.model import PageModel
from ..pdfio.rules import is_typed_rule

RAIL_CHARS = ")]§:*}|(│┃"


def caption_signature(pm: PageModel) -> dict:
    pw, ph = pm.width, pm.height

    # --- tall verticals (already piece-chained by pdfio; twins survive) ---
    verts = sorted((v.x, v.top, v.bottom) for v in pm.v_rules
                   if v.height >= 40)
    collapsed, twin = [], False
    for v in verts:
        if collapsed and abs(v[0] - collapsed[-1][0]) < 4:
            twin = True
            continue
        collapsed.append(v)
    gutter_x = None
    body_verts = []
    for v in collapsed:
        # a pleading gutter rule spans most of the page height at far left
        if v[0] < pw * 0.22 and (v[2] - v[1]) > ph * 0.55:
            gutter_x = v[0]
        else:
            body_verts.append(v)
    vleft = vmid = vright = None
    for v in body_verts:
        if v[0] <= pw * 0.2 and (gutter_x is None or v[0] > gutter_x + 4):
            vleft = v
        elif v[0] >= pw * 0.8:
            vright = v
        elif pw * 0.3 < v[0] < pw * 0.8:
            vmid = v

    # --- typed rules (dash runs, x-capped) ---
    typed = sorted((l.top, l.bottom, l.x0, l.x1) for l in pm.lines
                   if is_typed_rule(l.plain))
    typed_upper = [t for t in typed if t[0] < ph * 0.6]
    typed_band = ((typed_upper[0][0], typed_upper[-1][1])
                  if len(typed_upper) >= 2 else None)
    if typed_band is None:
        # ca2's summary orders OPEN the caption with one mid-page dash rule
        # (the notice block and convening recital fill the top half); the
        # closing dash lands on the next page. A lone mid-page dash with a
        # 'v.' pivot row below it opens a caption that runs to the foot.
        mids = [t for t in typed if ph * 0.3 < t[0] < ph * 0.78]
        if len(mids) == 1:
            below = [l for l in pm.lines if l.top > mids[0][1]]
            if any(" ".join(l.plain.split()).rstrip(".").lower()
                   in ("v", "vs") for l in below):
                typed_band = (mids[0][0], ph * 0.99)

    # --- caption band ---
    anchor = vmid or vleft or vright
    if anchor:
        band = (anchor[1] - 10, anchor[2] + 10)
    elif typed_band:
        band = (typed_band[0] - 10, typed_band[1] + 10)
    else:
        band = (60.0, ph * 0.55)

    # --- horizontals, classified by span and position within the band ---
    hzs = [(r.top, r.x0, r.x1) for r in pm.h_rules]
    hzs.extend((t[0], t[2], t[3]) for t in typed)
    hzs = [h for h in sorted(hzs) if h[2] - h[1] >= 60]
    mid_x = vmid[0] if vmid else pw / 2

    def span_of(h):
        _t, hx0, hx1 = h
        if (hx1 - hx0) > pw * 0.6:
            return "full"
        if hx1 <= mid_x + 10:
            return "left"
        if hx0 >= mid_x - 10:
            return "right"
        return "full"

    h_top = h_bottom = None
    interior = []
    for h in hzs:
        if not (band[0] - 16 <= h[0] <= band[1] + 16):
            continue
        if h[0] <= band[0] + 26:
            h_top = span_of(h)
        elif h[0] >= band[1] - 26:
            h_bottom = span_of(h)
        else:
            interior.append(span_of(h))

    # --- flush-right status rows / whitespace two-column rows ---
    # pdfio already split visual rows at column gaps, tagging shared `row`
    # ids; a row's pieces are its runs.
    flush_right = 0
    two_col_ws = 0
    in_band = [l for l in pm.lines
               if l.plain.strip() and band[0] - 20 <= l.top <= band[1] + 20]
    if in_band:
        lmargin = min(l.x0 for l in in_band)
        rmargin = max(l.x1 for l in in_band)
        rows: dict = {}
        for l in in_band:
            keyed = l.row if l.row is not None else f"solo-{l.id}"
            rows.setdefault(keyed, []).append(l)
        for pieces in rows.values():
            pieces.sort(key=lambda l: l.x0)
            if (len(pieces) >= 2
                    and pieces[0].x0 < lmargin + 30
                    and pieces[-1].x1 > rmargin - 15
                    and pieces[-1].width < pw * 0.35):
                flush_right += 1
            if (len(pieces) == 2
                    and pieces[0].x0 < lmargin + 30
                    and pieces[1].x0 - pieces[0].x1 > 30
                    and pieces[1].x1 > pw / 2 + 30):
                two_col_ws += 1

    # --- glyph rail: a stacked column of identical rail glyphs ---
    rail = rail_x = rail_band = None
    stacks: Counter = Counter()
    band_chars = [c for l in pm.lines for c in l.chars
                  if (c.get("text") or "") in RAIL_CHARS
                  and band[0] - 20 <= c["top"] <= band[1] + 60]
    for c in band_chars:
        stacks[((c.get("text") or ""), round(c["x0"] / 8))] += 1
    if stacks:
        (g, xb), n = stacks.most_common(1)[0]
        if n >= 3:
            rail = g
            rail_x = xb * 8 + 4
            ys = sorted((c for c in band_chars
                         if (c.get("text") or "") == g
                         and round(c["x0"] / 8) == xb),
                        key=lambda c: c["top"])
            if ys:
                # Keep the stacked caption rail, not a later prose parenthesis
                # in the same coarse x bucket: a true rail is a contiguous
                # vertical run — split at gaps far larger than its own pitch
                # and keep the longest run.
                pitches = [b["top"] - a["top"] for a, b in zip(ys, ys[1:])
                           if b["top"] > a["top"]]
                ordinary = min(pitches) if pitches else 16.0
                gap_limit = max(36.0, ordinary * 2.5)
                groups, current = [], []
                for ch in ys:
                    if current and ch["top"] - current[-1]["top"] > gap_limit:
                        groups.append(current)
                        current = []
                    current.append(ch)
                if current:
                    groups.append(current)
                ys = max(groups, key=len)
                rail_band = (min(c["top"] for c in ys),
                             max(c["bottom"] for c in ys))

    # Drawn strokes hugging a glyph-rail column are the rail's own cell
    # borders (Word-table captions box the ')' column), not a freestanding
    # mid divider.
    if rail is not None and rail_x is not None and vmid is not None:
        if abs(vmid[0] - rail_x) < 12:
            vmid = None
            twin = False

    return {
        "vleft": vleft is not None,
        "vmid": vmid is not None,
        "vright": vright is not None,
        "vmid_x": vmid[0] if vmid else None,
        "vmid_band": (vmid[1], vmid[2]) if vmid else None,
        "twin": twin,
        "h_top": h_top,
        "h_bottom": h_bottom,
        "interior": interior,
        "rail": rail,
        "rail_band": rail_band,
        "typed_rails": len(typed_upper),
        "typed_band": typed_band,
        "diag": pm.has_diagonal,
        "flush_right": flush_right,
        "two_col_ws": two_col_ws,
        "gutter": gutter_x is not None,
        "gutter_x": gutter_x,
        "band": band,
        "mid_x": mid_x,
    }


# (style_id, display name, predicate) — first match wins, most specific first.
# Catalog names/ASCII art live in the old repo's library/caption_catalog.py.
_MATRIX = (
    ("x-capped-box", "The X-Capped Pleading Box",
     lambda s: (s["diag"] or (s["rail"] == ":" and s["vleft"]))
     and (s["h_top"] is not None)),
    ("double-box", "The Double Box",
     lambda s: s["vleft"] and s["vmid"] and s["vright"]),
    ("i-beam", "The I-Beam",
     lambda s: s["vmid"] and s["h_top"] == "full" and s["h_bottom"] == "full"),
    ("backwards-c", "The Backwards C",
     lambda s: s["vmid"] and s["h_top"] in ("left", "full")
     and s["h_bottom"] in ("left", "full") and not s["vleft"]),
    ("upside-down-t", "The Upside-Down T",
     lambda s: s["vmid"] and s["h_top"] is None and s["h_bottom"] == "full"),
    ("old-faithful", "Old Faithful",
     lambda s: s["vmid"] and s["h_bottom"] == "left"),
    ("twin-rail", "The Twin Rail", lambda s: s["vmid"] and s["twin"]),
    ("old-faithful-open", "Old Faithful (open)", lambda s: s["vmid"]),
    ("section-rail", "The Section-Sign Rail", lambda s: s["rail"] == "§"),
    ("colon-rail", "The Colon Rail", lambda s: s["rail"] == ":"),
    ("bracket-rail", "The Square-Bracket Rail", lambda s: s["rail"] == "]"),
    ("asterisk-rail", "The Asterisk Rail", lambda s: s["rail"] == "*"),
    ("gathering-brace", "The Gathering Brace", lambda s: s["rail"] == "}"),
    ("banded-bracket", "The Banded Bracket",
     lambda s: s["rail"] in ("(", ")") and (s["h_top"] or s["h_bottom"])),
    ("parenthetical-box", "The Parenthetical Box",
     lambda s: s["rail"] in ("(", ")")),
    ("typed-sandwich", "The Typewriter Sandwich",
     lambda s: s["typed_rails"] >= 2 and not s["vmid"] and not s["vleft"]
     and not s["vright"] and not s["rail"]),
    ("status-flush", "The Flush-Right Status",
     lambda s: s["flush_right"] >= 2 and not s["vmid"] and not s["rail"]
     and s["h_top"] is None and s["h_bottom"] is None and not s["interior"]),
    ("open-range", "The Open Range",
     lambda s: s["two_col_ws"] >= 1 and not s["vmid"] and not s["vleft"]
     and not s["vright"] and not s["rail"] and s["h_top"] is None
     and s["h_bottom"] is None and not s["interior"]),
)


def classify_signature(sig: dict) -> tuple[str | None, str | None]:
    for sid, name, pred in _MATRIX:
        if pred(sig):
            return sid, name
    return None, None


def classify_page(pm: PageModel) -> tuple[dict, str | None, str | None]:
    sig = caption_signature(pm)
    sid, name = classify_signature(sig)
    return sig, sid, name
