"""Named pdfplumber quirk repairs. Every repair fires a trace event.

All of these are ports of behaviors the old system proved on the corpus —
see docs/lessons/pdfplumber-quirks.md. Char-level repairs run before line
clustering (by the time lines exist the damage is done); line-level repairs
run right after.
"""

from __future__ import annotations

# A FontDescriptor /Descent past this many em is not a typeface's descent —
# it is its /FontBBox depth mis-copied. MEASURED across the corpus: honest
# faces run 0.246-0.299 em (Aptos, Cambria-Bold, Cambria-Italic), the broken
# descriptors 0.660 (Tunga), 0.680/0.710 (CourierNewPSMT/-BoldMT), 0.789
# (SegoeUISymbol) and 2.464 (Cambria/CambriaMath) — a wide empty band at 0.6.
_DESCENT_MAX = 0.6


# --------------------------------------------------------------------------
# char-level
# --------------------------------------------------------------------------

def normalize_font_descent(chars: list, event) -> None:
    """Put every glyph's BOX back on its own baseline when the font lies about
    its descent.

    pdfminer derives a char's box from the baseline plus the FontDescriptor's
    /Descent (``y0 = baseline + descent * size``), so a descriptor that
    reports its /FontBBox depth instead of its real descent drops the whole
    face DOWN the page while its siblings stay put. MEASURED in
    me/adoption_by_kathleen_c.: the body face ``AEPVZY+Cambria`` declares
    Descent -2464 / Ascent 3117 — verbatim its FontBBox y-range — while
    ``Cambria-Italic`` (-279), ``Cambria-Bold`` (-299) and ``Aptos`` (-275)
    on the same page are honest. Every roman glyph therefore reports a `top`
    (2.464 - 0.277) x 14.04pt = 30.71pt too large, one row pitch (32.85pt)
    low, so the ITALIC trial-judge run on baseline 419.40 reports top 362.47
    while the roman half of its own row reports 393.15 and the roman row
    ABOVE it reports 360.27 — 2.2pt away. pdfplumber clusters within 3pt,
    welds the two, and sorts by x: 'sBuebnjseocnt,  oJ.f a pending…'.

    The cure is the baseline, which never lies: ``matrix[5]`` is the glyph's
    device-space baseline, so ``(matrix[5] - y0) / size`` recovers the
    descent the descriptor actually declared. A face whose recovered descent
    is past -0.6 em is not a typeface — real ones on this corpus run 0.246 to
    0.299 em, the bogus ones 0.66 (CourierNewPS-BoldMT) to 2.464 (Cambria) —
    and its boxes are re-hung on the page's own honest descent. The proof is
    the paper: me's top text margin reads 98.6pt (1.37in) before and 74.5pt
    (1.03in) after, on a page whose left margin is exactly 72pt.

    Rotated glyphs are skipped — their box is not a vertical shift of the
    baseline."""
    import statistics
    per: dict = {}
    for c in chars:
        m = c.get("matrix")
        size = float(c.get("size") or 0)
        if not m or size <= 0 or "y0" not in c:
            continue
        if abs(m[1]) > 1e-6 or abs(m[2]) > 1e-6:
            continue                      # rotated/skewed: not a y-shift
        per.setdefault(c.get("fontname") or "", []).append(
            (m[5] - c["y0"]) / size)
    ratios = {f: statistics.median(v) for f, v in per.items() if v}
    honest = [r for r in ratios.values() if r <= _DESCENT_MAX]
    bogus = {f: r for f, r in ratios.items() if r > _DESCENT_MAX}
    if not honest or not bogus:
        return                            # nothing to hang it from, or nothing to fix
    # Clamped to the measured band of real faces so one odd reference face
    # cannot drag a whole page off its baselines.
    ref = min(max(statistics.median(honest), 0.20), 0.35)
    moved = 0
    for c in chars:
        r = bogus.get(c.get("fontname") or "")
        if r is None:
            continue
        size = float(c.get("size") or 0)
        if size <= 0:
            continue
        d = (ref - r) * size              # negative: the box rises
        c["top"] += d
        c["bottom"] += d
        if "doctop" in c:
            c["doctop"] += d
        c["y0"] -= d
        c["y1"] -= d
        moved += 1
    if moved:
        event("font-descent",
              f"re-hung {moved} glyphs in {len(bogus)} bogus-descent "
              f"fonts on descent {ref:.3f} ("
              + ", ".join(f"{f.split('+')[-1]} {r:.2f}"
                          for f, r in sorted(bogus.items())) + ")")


def drop_white_glyphs(chars: list, event) -> None:
    """Drop glyphs PAINTED WHITE — invisible on paper, used as spacers (a
    ca8 chambers sets runs of white 'l's to space its headmatter). White is
    a COLORSPACE fact, not a number: RGB (1,1,1) is white, CMYK white is
    ZERO ink on every plate, and DeviceGray 1.0 is white only because the
    space says so — a bare (1.0,) in a Separation space is FULL colorant,
    solid black (tenn paints its whole text layer that way). An unrecorded
    or ambiguous color is not evidence and always passes."""
    white = []
    for i, c in enumerate(chars):
        col = c.get("non_stroking_color")
        if col is None or not (c.get("text") or "").strip():
            continue
        vals = col if isinstance(col, (list, tuple)) else (col,)
        try:
            floats = [float(v) for v in vals]
        except (TypeError, ValueError):
            continue
        if len(floats) == 3:
            is_white = all(v >= 0.95 for v in floats)
        elif len(floats) == 4:
            is_white = all(v <= 0.05 for v in floats)
        elif len(floats) == 1:
            is_white = (floats[0] >= 0.95
                        and "gray" in str(c.get("ncs") or "").lower())
        else:
            is_white = False
        if is_white:
            white.append(i)
    for i in reversed(white):
        del chars[i]
    if white:
        event("white-glyphs", f"dropped {len(white)} white-painted spacers")


def decode_cid_glyphs(chars: list, event) -> None:
    """Recover text from subset fonts with no ToUnicode map. pdfminer emits
    the literal '(cid:N)' for such glyphs; for the common TrueType subset
    ordering the unicode is cid+29 ('(cid:45)(cid:82)(cid:75)' -> 'Joh').
    The offset is applied PER FONT and only when the decoded result reads
    like text (letters dominate, vowels present) — wrong-but-plausible
    words would be worse than visible (cid:) garbage, so an implausible
    font keeps its literals. '(cid:0)' is .notdef noise and always drops."""
    import re as _re
    _CID = _re.compile(r"^\(cid:(\d+)\)$")
    by_font: dict[str, list[tuple[int, int]]] = {}
    notdef = []
    for i, c in enumerate(chars):
        m = _CID.match(c.get("text") or "")
        if not m:
            continue
        n = int(m.group(1))
        if n == 0:
            notdef.append(i)
            continue
        by_font.setdefault(str(c.get("fontname")), []).append((i, n))
    decoded = 0
    for font, hits in by_font.items():
        mapped = [chr(n + 29) for _, n in hits if 32 <= n + 29 <= 126]
        if len(mapped) < max(4, int(0.95 * len(hits))):
            continue                     # offset can't cover this font
        letters = [ch for ch in mapped if ch.isalpha()]
        others = [ch for ch in mapped
                  if not (ch.isalnum() or ch in " .,;:!?()[]'\"-–—&$%/§*†‡")]
        vowels = sum(1 for ch in letters if ch.lower() in "aeiouáéíóú")
        if (not letters or others
                or vowels < 0.15 * len(letters)):
            continue                     # decodes to junk — keep literals
        for i, n in hits:
            if 32 <= n + 29 <= 126:
                chars[i]["text"] = chr(n + 29)
                decoded += 1
    if decoded:
        # Small subsets (a 4-glyph 'hnhn' font inside 'Jo?nson') can't
        # prove themselves — too few letters for the vowel test; once a
        # sibling font proved the +29 ordering on this page, decode their
        # in-range letters too.
        for font, hits in by_font.items():
            if len(hits) >= 8:
                continue
            for i, n in hits:
                ch = chr(n + 29) if 32 <= n + 29 <= 126 else ""
                if ch and (ch.isalnum() or ch in " .,;:'\"-()"):
                    chars[i]["text"] = ch
                    decoded += 1
    for i in reversed(notdef):
        del chars[i]
    if decoded or notdef:
        event("cid-glyphs",
              f"decoded {decoded} cid glyphs (+29), "
              f"dropped {len(notdef)} .notdef")


def drop_micro_glyphs(chars: list, event) -> None:
    """Word's PDF footnote field can leave a microscopic ``0F`` field-code run
    under the real superscript label (~1pt high, invisible). Remove only
    alphanumeric micro-glyphs; small caps, subscripts and footnote marks are
    several points larger and remain untouched."""
    micro = [i for i, c in enumerate(chars)
             if (c.get("text") or "").isalnum()
             and 0 < float(c.get("size") or 0) <= 1.5]
    for i in reversed(micro):
        del chars[i]
    if micro:
        event("micro-glyphs", f"dropped {len(micro)} field-code glyphs")


def drop_overstruck(chars: list, event) -> None:
    """Drop OVERSTRUCK glyphs — a character redrawn at a position another copy
    already occupies. Conformed signatures are darkened by stamping the name
    dozens of times ('CCCCCCOOLLLLEEEENN DD. HHHHOOLLLAANNDD'). Two distinct
    glyphs never share a position, so a repeat there is the same glyph struck
    again, not new text.

    Sorted by glyph then POSITION so every copy of one stamp lands beside its
    originals: restamps scatter by hundredths of a point, which a fixed grid
    would split across buckets; x0 before top keeps two stamps of one letter
    on one line from interleaving."""
    order = sorted(range(len(chars)),
                   key=lambda i: (chars[i].get("text") or "",
                                  chars[i]["x0"], chars[i]["top"]))
    dupes, anchor = [], None
    for i in order:
        c = chars[i]
        if (anchor is not None
                and (c.get("text") or "") == (anchor.get("text") or "")
                and abs(c["top"] - anchor["top"]) <= 0.5
                and abs(c["x0"] - anchor["x0"]) <= 0.5):
            dupes.append(i)
        else:
            anchor = c
    for i in sorted(dupes, reverse=True):
        del chars[i]
    if dupes:
        event("overstruck", f"dropped {len(dupes)} restamped glyphs")


def snap_displaced_fragments(chars: list, event) -> None:
    """Snap a short glyph run drawn far off its own baseline back onto the row
    it belongs to — in place, before clustering.

    A glyph the body face lacks is fetched from a substitute font, and the
    substitution can carry a large vertical offset (Arizona's '¶' from Cambria
    26pt BELOW its line; rebuilt in x order it lands INSIDE a word:
    'sub¶se 1c7ti.o n'). The hole is the proof: the host row still has a gap
    at exactly the fragment's x-span. Require the fragment to sit inside that
    gap and fill most of it, in a font the host row does not use, a real
    distance away — ordinary baseline jitter stays with the line-level merge."""
    printable = [c for c in chars if (c.get("text") or "").strip()]
    if len(printable) < 12:
        return
    rows: dict = {}
    for c in printable:
        rows.setdefault(round(c["top"], 1), []).append(c)
    hosts = {t: v for t, v in rows.items() if len(v) >= 10}
    if not hosts:
        return

    def fonts(cs):
        return {(c.get("fontname") or "").split("+")[-1] for c in cs}

    snapped = 0
    deltas: list[float] = []
    unresolved: list[tuple] = []
    for top, frag in rows.items():
        if not (1 <= len(frag) <= 40):
            continue
        f_fonts = fonts(frag)
        fx0 = min(c["x0"] for c in frag)
        fx1 = max(c["x1"] for c in frag)
        # A fragment that already HAS a line of its own (a bold speaker name
        # 0.6pt below its roman host) belongs to ordinary clustering; snapping
        # it hands it to whichever row's hole it fits ('BTruocwkner').
        # EXCEPT one that INTERLEAVES its neighbor: glyph boxes overlapping
        # a row set in a different face are displaced type, not a line of
        # their own (me's italic pass prints one leading off, shredding
        # 'See State v. Pratt' into the row above).
        near = [htop for htop in hosts
                if htop != top and abs(htop - top) < 4.0]
        if near:
            # COLLISION, not span overlap: a same-line italic run
            # INTERLOCKS its row's gap at a small baseline offset (ca5's
            # 'Before <italic names>, Circuit Judges') — its glyph boxes
            # touch nothing. A DISPLACED run lands on foreign text and its
            # glyphs collide (me's 'See State v. Pratt' over 'hearsay.
            # We review').
            collisions = sum(
                1 for htop in near for c in rows[htop] for fc in frag
                if fc["x0"] < c["x1"] - 0.8 and fc["x1"] > c["x0"] + 0.8)
            near_fonts = {f for htop in near for f in fonts(rows[htop])}
            if collisions < 3 or (f_fonts & near_fonts):
                continue
        best = None
        for htop, hcs in hosts.items():
            gap = abs(htop - top)
            if not (4.0 <= gap <= 32.0):   # real displacement, not jitter
                continue
            if f_fonts & fonts(hcs):
                continue
            # INTERLOCK test: the fragment's glyphs must all fall inside
            # the host's measure without colliding with any host glyph —
            # x-positions are trustworthy even when the baseline lies, so
            # a run split across SEVERAL holes ('See id.' + 'cf.' +
            # 'Dionne v.' interlocking 'observations. ¶ 11; c…') passes
            # exactly when it belongs. Tested against the host's whole
            # LINE BAND: a small-caps roster splits across two baselines
            # (cadc's 'WALKER'), and each alone reads falsely sparse.
            hband = [c for c in printable
                     if c is not None and abs(c["top"] - htop) <= 3.5
                     and c not in frag]
            if not hband:
                continue
            hx0 = min(c["x0"] for c in hband)
            hx1 = max(c["x1"] for c in hband)
            # ENGAGEMENT, not containment: the run may own the host line's
            # TAIL ('cf. Dionne v.' continues past the row's last glyph) —
            # but a run that never enters the host's measure is a marginal
            # note, not its text.
            if fx1 <= hx0 + 2.0 or fx0 >= hx1 - 2.0:
                continue
            if any(fc["x0"] < hc["x1"] - 0.8 and fc["x1"] > hc["x0"] + 0.8
                   for fc in frag for hc in hband):
                continue
            # The frag must fit into real WHITESPACE, not kerning gaps: a
            # centered 'JUDGMENT' heading dodges a dense roster's letter
            # gaps collision-free (cadc) — but the row has no room for it.
            win = [c for c in hband if c["x1"] > fx0 and c["x0"] < fx1]
            cover = sum(min(c["x1"], fx1) - max(c["x0"], fx0) for c in win)
            frag_ink = sum(fc["x1"] - fc["x0"] for fc in frag)
            if (fx1 - fx0) - cover < 0.9 * frag_ink:
                continue
            if best is None or gap < best[0]:
                best = (gap, hcs)
        if best is None:
            # No host hole fits — remember the interleaved orphan: a
            # displaced italic HEADING has no host at all (its true band
            # is EMPTY); the successful snaps on this page measure the
            # displacement, applied in a second pass below.
            if near and len(frag) >= 4:
                unresolved.append((top, frag, f_fonts, fx0, fx1))
            continue
        host = best[1][0]
        dt = host["top"] - top
        deltas.append(dt)
        _move_run(chars, frag, f_fonts, top, host["top"],
                  host["bottom"], dt)
        snapped += 1
    # Second pass: an interleaved run with NO hole anywhere lands one
    # measured displacement DOWN when that band is clear (me's substitute
    # italic prints one leading high; a heading's own band holds nothing).
    if unresolved and not deltas:
        # No measured snap this page: the displacement is one row pitch
        # (the substitute pass prints one leading off) — estimate it from
        # the host rows' own spacing.
        tops = sorted(hosts)
        gaps = sorted(b - a for a, b in zip(tops, tops[1:])
                      if 18 <= b - a <= 44)
        if gaps:
            deltas = [gaps[len(gaps) // 2]]
    if unresolved and deltas:
        deltas.sort()
        d = deltas[len(deltas) // 2]
        for top, frag, f_fonts, fx0, fx1 in unresolved:
            tgt = top + d
            clear = not any(
                abs(c["top"] - tgt) < 3.5
                and c["x0"] < fx1 and c["x1"] > fx0
                for c in printable if c not in frag)
            if not clear:
                continue
            _move_run(chars, frag, f_fonts, top, tgt,
                      tgt + (frag[0].get("bottom", tgt) - frag[0]["top"]), d)
            snapped += 1
    if snapped:
        event("displaced-fragments", f"snapped {snapped} substitute-font runs")


def _move_run(chars: list, frag: list, f_fonts: set, top: float,
              new_top: float, new_bottom: float, dt: float) -> None:
    """Move the WHOLE run, blanks included: a blank set in the substitute
    face on the fragment's baseline is the fragment's own space — leaving
    it behind reopens the hole and the word breaks there."""
    move = list(frag)
    for c in chars:
        if (c.get("text") or "").strip():
            continue
        if abs(round(c["top"], 1) - top) > 0.05:
            continue
        if (c.get("fontname") or "").split("+")[-1] in f_fonts:
            move.append(c)
    for c in move:
        c["top"] = new_top
        c["bottom"] = new_bottom
        if "doctop" in c:
            c["doctop"] = c["doctop"] + dt


# --------------------------------------------------------------------------
# line-level
# --------------------------------------------------------------------------

def _printable(line) -> list:
    return [c for c in (line.get("chars") or []) if (c.get("text") or "").strip()]


def reunite_offset_glyphs(lines: list, event) -> list:
    """Put a stray glyph drawn off its own baseline back into the hole it came
    from (ca7's '½' from Cambria 26pt below its line, merged mid-word into the
    wrong row as 'Th½e statute'). A lone glyph, no line of its own, and a hole
    it fits to the point — a real hole runs ~3.4× the line's word gap, a
    coincidental fit ~1.0×, and requiring a DIFFERENT font keeps page folios
    out even when they happen to fit."""
    if len(lines) < 2:
        return lines

    def fonts(l):
        return {(c.get("fontname") or "") for c in _printable(l)}

    strays, hosts = [], []
    for l in lines:
        (strays if len(_printable(l)) <= 2 else hosts).append(l)
    if not strays or not hosts:
        return lines

    absorbed = set()
    for s in strays:
        height = max(s["bottom"] - s["top"], 1.0)
        s_fonts = fonts(s)
        if any(o is not s and abs(o["top"] - s["top"]) < 4.0
               and len(_printable(o)) > 2 for o in lines):
            continue  # sits on its own row already — ordinary merge owns it
        best = None
        for h in hosts:
            if abs(h["top"] - s["top"]) > 2.5 * height:
                continue
            if s_fonts & fonts(h) or not s_fonts:
                continue
            cs = sorted(_printable(h), key=lambda c: c["x0"])
            spaces = sorted(g for g in (b["x0"] - a["x1"]
                                        for a, b in zip(cs, cs[1:])) if g > 0.5)
            if not spaces:
                continue
            word_gap = spaces[len(spaces) // 2]
            for a, b in zip(cs, cs[1:]):
                if (b["x0"] - a["x1"]) < 2.0 * word_gap:
                    continue
                slack = (b["x0"] - a["x1"]) - (s["x1"] - s["x0"])
                if (0 <= slack <= 6 and s["x0"] >= a["x1"] - 1.5
                        and s["x1"] <= b["x0"] + 1.5):
                    d = abs(h["top"] - s["top"])
                    if best is None or d < best[0]:
                        best = (d, h)
                    break
        if best is None:
            continue
        h = best[1]
        h["chars"] = sorted(list(h.get("chars") or []) + list(s.get("chars") or []),
                            key=lambda c: c["x0"])
        h["x0"] = min(h["x0"], s["x0"])
        h["x1"] = max(h["x1"], s["x1"])
        h["text"] = "".join(c["text"] for c in h["chars"])
        absorbed.add(id(s))
    if not absorbed:
        return lines
    event("offset-glyphs", f"reunited {len(absorbed)} strays")
    return [l for l in lines if id(l) not in absorbed]


def merge_interleaved(lines: list, event) -> list:
    """An italic span set on a slightly offset baseline becomes its own line
    ('Bell Atl. Corp. v. Twombly' floating 4.8pt above its roman host) and
    would sort mid-sentence. Two lines whose vertical extents overlap strongly
    and whose glyphs interleave without colliding are ONE visual row.

    Guard: e-filing stamps are frequently Arial overlays on a differently
    faced banner near the page top — overlapping boxes but independent rows."""
    lines = reunite_offset_glyphs(lines, event)
    if len(lines) < 2:
        return lines
    lines = sorted(lines, key=lambda l: (l["top"], l["x0"]))
    merged_n = 0
    out = [lines[0]]
    for ln in lines[1:]:
        prev = out[-1]
        v_overlap = min(prev["bottom"], ln["bottom"]) - max(prev["top"], ln["top"])
        min_h = max(min(prev["bottom"] - prev["top"], ln["bottom"] - ln["top"]), 1.0)
        merged_chars = sorted(list(prev.get("chars") or []) + list(ln.get("chars") or []),
                              key=lambda c: c["x0"])
        prev_sizes = sorted(float(c.get("size") or 0) for c in _printable(prev)
                            if c.get("size"))
        line_sizes = sorted(float(c.get("size") or 0) for c in _printable(ln)
                            if c.get("size"))
        size_compatible = True
        if prev_sizes and line_sizes:
            a = prev_sizes[len(prev_sizes) // 2]
            b = line_sizes[len(line_sizes) // 2]
            size_compatible = max(a, b) <= 1.8 * max(min(a, b), 0.1)
        prev_arial = any("arial" in (c.get("fontname") or "").lower()
                         for c in _printable(prev))
        line_arial = any("arial" in (c.get("fontname") or "").lower()
                         for c in _printable(ln))
        if (min(prev.get("top", 999), ln.get("top", 999)) < 220
                and prev_arial != line_arial):
            size_compatible = False
        if merged_chars and size_compatible and v_overlap > 0.45 * min_h:
            union = max(c["x1"] for c in merged_chars) - min(c["x0"] for c in merged_chars)
            glyphs = sum(c["x1"] - c["x0"] for c in merged_chars)
            if glyphs <= union * 1.05:  # interleaved, not colliding
                m = dict(prev)
                m["chars"] = merged_chars
                m["x0"] = min(prev["x0"], ln["x0"])
                m["x1"] = max(prev["x1"], ln["x1"])
                m["top"] = min(prev["top"], ln["top"])
                m["bottom"] = max(prev["bottom"], ln["bottom"])
                m["text"] = "".join(c["text"] for c in merged_chars)
                out[-1] = m
                merged_n += 1
                continue
        out.append(ln)
    if merged_n:
        event("interleaved-baselines", f"merged {merged_n} offset runs")
    return out


def tag_underlined_chars(rects: list, lines: list,
                         offset_min: float = -2.5,
                         offset_max: float = 5.0) -> None:
    """Mark chars underlined by a hairline rect near the baseline
    (sets ``_underline=True`` on the char dicts). The char box's bottom
    includes descender space, so a true underline may measure slightly
    ABOVE it (nh draws at −1.3pt) — a strike-through sits at −4 and
    below, outside the window."""
    hairlines = [r for r in rects
                 if r.get("height", 0) < 2 and (r["x1"] - r["x0"]) > 6]
    if not hairlines:
        return
    for line in lines:
        chars = line.get("chars") or []
        if not chars:
            continue
        baseline = max(c["bottom"] for c in chars)
        line_rects = [r for r in hairlines
                      if offset_min <= (r["top"] - baseline) <= offset_max
                      and r["x0"] < chars[-1]["x1"] and r["x1"] > chars[0]["x0"]]
        if not line_rects:
            continue
        for c in chars:
            cmid = (c["x0"] + c["x1"]) / 2
            for r in line_rects:
                if r["x0"] - 1 <= cmid <= r["x1"] + 1:
                    c["_underline"] = True
                    break
