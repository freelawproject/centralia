"""Page-1 caption fingerprint: geometry signature -> catalog style.

One extraction pass measures the drawn and typed structure of the caption
band on page 1; one table maps signatures to the /captions catalog styles.
The renderer draws borders from the SAME signature, so the label and the
reproduction cannot disagree.

Signature facets:
  verticals   which tall rules exist: 'left' (content left edge), 'mid'
              (between the columns), 'right' (content right edge)
  h_top       a horizontal rule at the caption's top: 'full' / 'left' /
              'right' / None
  h_bottom    same for the caption's bottom edge
  rail        a glyph rail column: ')', ']', '§', ':', '*', '}', '|' ...
  diag        True when diagonal lines cross the caption (X-capped)
  gutter      pleading line-number gutter present
  typed_rails how many TYPED rules (dash runs, optionally 'x'-capped) close
              the caption; ``typed_band`` is the band between the outermost
              two — the New York districts draw nothing and rely on these

The caption BAND is the y-range of the mid vertical when one exists, else
the span of the tall verticals, else — when the caption is closed by typed
rules alone — the band those rules enclose, else the band between the court
banner and the first body paragraph (approximated by the drawn rules' extent).
"""

from __future__ import annotations

_RAIL_CHARS = ")]§:*}|("

# Glyphs a typed horizontal rule is built from.
_RULE_GLYPHS = "_-—–"


def is_typed_rule(text: str, glyphs: str = _RULE_GLYPHS) -> bool:
    """True if ``text`` is a horizontal rule TYPED as characters rather than
    drawn as a vector: a run of rule glyphs, optionally spaced out, and
    optionally capped with an ``x`` at either end.

    The cap is the pleading caption's corner — the typewriter-era stand-in for
    the box corner a modern template draws as a vector rule
    (``-------------------x`` closing a New York caption). It is furniture
    exactly like the dashes it terminates, so a capped rule has to read as a
    rule and never as caption text.

    This is the single definition of 'typed rule' in the codebase; the
    extractor's segmentation, the styled-caption divider test and this
    fingerprint all defer to it so they cannot disagree about what a rule is.
    """
    t = (text or "").strip()
    if t[-1:] in ("x", "X"):
        t = t[:-1].rstrip()
    if t[:1] in ("x", "X"):
        t = t[1:].lstrip()
    if not t or any(c not in glyphs and c != " " for c in t):
        return False
    return sum(1 for c in t if c in glyphs) >= 4


def caption_signature(page) -> dict:
    """Measure the page-1 caption geometry. Pure geometry — no text model."""
    pw = page.width
    # --- tall verticals (drawn) ---
    raw_v = []
    for r in page.rects:
        if (r["x1"] - r["x0"]) < 2.5 and (r["bottom"] - r["top"]) >= 8:
            raw_v.append((r["x0"], r["top"], r["bottom"]))
    for ln in page.lines:
        if abs(ln["x1"] - ln["x0"]) < 2.5 and (ln["bottom"] - ln["top"]) >= 8:
            raw_v.append((ln["x0"], ln["top"], ln["bottom"]))
    # chain stacked segments at the same x into one rule (some PDFs draw a
    # 150pt vertical as five 30pt pieces)
    raw_v.sort(key=lambda v: (round(v[0], 0), v[1]))
    chained = []
    for v in raw_v:
        if (
            chained
            and abs(v[0] - chained[-1][0]) < 0.9
            and v[1] <= chained[-1][2] + 6
        ):
            chained[-1] = (chained[-1][0], chained[-1][1], max(chained[-1][2], v[2]))
        else:
            chained.append(list(v) if isinstance(v, tuple) else v)
        chained[-1] = tuple(chained[-1])
    verts = [v for v in chained if v[2] - v[1] >= 40]
    # collapse doubled strokes (twin rails draw two ~1.4pt apart)
    verts.sort()
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
        if v[0] < pw * 0.22 and (v[2] - v[1]) > page.height * 0.55:
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

    # --- typed rules closing the caption ---
    # Nothing is drawn: the caption is sandwiched between two rules TYPED as
    # dash runs and closed with the pleading corner 'x' — the New York
    # districts' template. Measured before the band, because when there is no
    # drawn anchor these rules ARE the band.
    typed = []
    try:
        for tl in page.extract_text_lines():
            if is_typed_rule(tl.get("text") or ""):
                typed.append((tl["top"], tl["bottom"], tl["x0"], tl["x1"]))
    except Exception:
        pass
    typed.sort()
    # Only the upper page can close a caption; a signature rule near the foot
    # is a different piece of furniture entirely.
    typed_upper = [t for t in typed if t[0] < page.height * 0.6]
    typed_band = (
        (typed_upper[0][0], typed_upper[-1][1]) if len(typed_upper) >= 2 else None
    )

    # --- caption band ---
    anchor = vmid or vleft or vright
    if anchor:
        band = (anchor[1] - 10, anchor[2] + 10)
    elif typed_band:
        band = (typed_band[0] - 10, typed_band[1] + 10)
    else:
        band = (60.0, page.height * 0.55)

    # --- horizontals (drawn), classified by span and position ---
    # Collect EVERY thin piece (boxes are often drawn as many short abutting
    # strips, some under 20pt), merge chains at one y, THEN size-filter — so
    # a full-width rule drawn in pieces never reads as two disjoint halves.
    raw_h = []
    for r in page.rects:
        if (r["bottom"] - r["top"]) < 2.5 and (r["x1"] - r["x0"]) >= 2.5:
            raw_h.append((r["top"], r["x0"], r["x1"]))
    for ln in page.lines:
        if abs(ln["bottom"] - ln["top"]) < 2.5 and (ln["x1"] - ln["x0"]) >= 2.5:
            raw_h.append((ln["top"], ln["x0"], ln["x1"]))
    # rules TYPED as underscore/dash runs are rules too (oknd, and the New
    # York districts' 'x'-capped caption rules)
    raw_h.extend((t[0], t[2], t[3]) for t in typed)
    # merge abutting segments drawn at one y
    raw_h.sort(key=lambda h: (round(h[0], 0), h[1]))
    hzs = []
    for h in raw_h:
        if hzs and abs(h[0] - hzs[-1][0]) < 2.5 and h[1] <= hzs[-1][2] + 6:
            hzs[-1] = (hzs[-1][0], hzs[-1][1], max(hzs[-1][2], h[2]))
        else:
            hzs.append(h)
    hzs = [h for h in hzs if h[2] - h[1] >= 60]
    mid_x = vmid[0] if vmid else pw / 2

    def span_of(h):
        _t, hx0, hx1 = h
        wide = (hx1 - hx0) > pw * 0.6
        if wide:
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

    # --- diagonals (X-capped) ---
    diag = any(
        abs(ln["x1"] - ln["x0"]) > 30 and abs(ln["bottom"] - ln["top"]) > 10
        for ln in page.lines
    )

    # --- flush-right status rows (The Flush-Right Status) ---
    # A caption with NOTHING drawn: party names at the left margin and a
    # separate short run (PLAINTIFF / APPELLEE...) pinned hard against the
    # right text margin on the same visual row. Pure positions — two-zone
    # rows are counted, the words themselves are never read.
    flush_right = 0
    two_col_ws = 0
    try:
        tls = [
            tl for tl in page.extract_text_lines()
            if tl.get("chars") and band[0] - 20 <= tl["top"] <= band[1] + 20
        ]
        if tls:
            lmargin = min(tl["x0"] for tl in tls)
            rmargin = max(tl["x1"] for tl in tls)
            mid_guess = pw / 2
            for tl in tls:
                runs, cur = [], [tl["chars"][0]]
                for c in tl["chars"][1:]:
                    if c["x0"] - cur[-1]["x1"] > 18:
                        runs.append(cur)
                        cur = [c]
                    else:
                        cur.append(c)
                runs.append(cur)
                if (
                    len(runs) >= 2
                    and runs[0][0]["x0"] < lmargin + 30
                    and runs[-1][-1]["x1"] > rmargin - 15
                    and (runs[-1][-1]["x1"] - runs[-1][0]["x0"]) < pw * 0.35
                ):
                    flush_right += 1
                # a two-column row held together by whitespace alone: a
                # left-margin run, a wide gap, and ONE other run reaching
                # past mid-page ('v.        CIVIL ACTION NO. 3:24-…').
                # Exactly two runs — a three-zone running head (left date,
                # centered term, right folio) is page furniture, not a
                # caption.
                if (
                    len(runs) == 2
                    and runs[0][0]["x0"] < lmargin + 30
                    and runs[-1][0]["x0"] - runs[0][-1]["x1"] > 30
                    and runs[-1][-1]["x1"] > mid_guess + 30
                ):
                    two_col_ws += 1
    except Exception:
        pass

    # --- glyph rail: a stacked column of identical rail glyphs ---
    rail = None
    from collections import Counter

    stacks: Counter = Counter()
    for c in page.chars:
        t = c.get("text") or ""
        if t in _RAIL_CHARS and band[0] - 20 <= c["top"] <= band[1] + 60:
            stacks[(t, round(c["x0"] / 8))] += 1
    rail_x = rail_band = None
    if stacks:
        (g, xb), n = stacks.most_common(1)[0]
        if n >= 3:
            rail = g
            rail_x = xb * 8 + 4
            ys = [
                c for c in page.chars
                if (c.get("text") or "") == g
                and round(c["x0"] / 8) == xb
                and band[0] - 20 <= c["top"] <= band[1] + 60
            ]
            if ys:
                rail_band = (
                    min(c["top"] for c in ys),
                    max(c["bottom"] for c in ys),
                )

    # Drawn strokes hugging a glyph-rail column are the rail's own cell
    # borders (Word-table captions box the ')' column), not a freestanding
    # mid divider — don't let them claim vmid/twin.
    if rail is not None and rail_x is not None and vmid is not None:
        if abs(vmid[0] - rail_x) < 12:
            vmid = None
            twin = False

    return {
        "vleft": vleft is not None,
        "vmid": vmid is not None,
        "vright": vright is not None,
        "twin": twin,
        "h_top": h_top,
        "h_bottom": h_bottom,
        "interior": interior,
        "rail": rail,
        "rail_band": rail_band,
        "typed_rails": len(typed_upper),
        "typed_band": typed_band,
        "diag": diag,
        "flush_right": flush_right,
        "two_col_ws": two_col_ws,
        "gutter": gutter_x is not None,
        "band": band,
        "mid_x": mid_x,
    }


# (style_id, display name, predicate) — first match wins, most specific first.
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
    ("old-faithful-open", "Old Faithful (open)",
     lambda s: s["vmid"]),
    ("section-rail", "The Section-Sign Rail", lambda s: s["rail"] == "§"),
    ("colon-rail", "The Colon Rail", lambda s: s["rail"] == ":"),
    ("bracket-rail", "The Square-Bracket Rail", lambda s: s["rail"] == "]"),
    ("asterisk-rail", "The Asterisk Rail", lambda s: s["rail"] == "*"),
    ("gathering-brace", "The Gathering Brace", lambda s: s["rail"] == "}"),
    ("banded-bracket", "The Banded Bracket",
     lambda s: s["rail"] in ("(", ")") and (s["h_top"] or s["h_bottom"])),
    ("parenthetical-box", "The Parenthetical Box",
     lambda s: s["rail"] in ("(", ")")),
    # Nothing drawn and no glyph rail: the caption is sandwiched between two
    # rules TYPED as dash runs, each closed with the pleading corner 'x'.
    # Placed after the glyph rails so a caption that has BOTH (the colon rail
    # dividing the columns, typed rules closing them) keeps the more specific
    # name — the band the typed rules enclose is recorded either way.
    ("typed-sandwich", "The Typewriter Sandwich",
     lambda s: s["typed_rails"] >= 2 and not s["vmid"] and not s["vleft"]
     and not s["vright"] and not s["rail"]),
    # Last: nothing drawn at all, just two-zone rows with the status label
    # pinned at the right margin.
    ("status-flush", "The Flush-Right Status",
     lambda s: s["flush_right"] >= 2 and not s["vmid"] and not s["rail"]
     and s["h_top"] is None and s["h_bottom"] is None and not s["interior"]),
    # Very last: nothing drawn, no rail — a two-column caption held
    # together by whitespace alone (parties left, docket right).
    ("open-range", "The Open Range",
     lambda s: s["two_col_ws"] >= 1 and not s["vmid"] and not s["vleft"]
     and not s["vright"] and not s["rail"] and s["h_top"] is None
     and s["h_bottom"] is None and not s["interior"]),
)


def classify_signature(sig: dict):
    """(style_id, name) or (None, None)."""
    for sid, name, pred in _MATRIX:
        try:
            if pred(sig):
                return sid, name
        except Exception:
            continue
    return None, None


def classify_page(page):
    sig = caption_signature(page)
    sid, name = classify_signature(sig)
    return sig, sid, name
