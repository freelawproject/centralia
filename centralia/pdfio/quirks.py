"""Named pdfplumber quirk repairs. Every repair fires a trace event.

All of these are ports of behaviors the old system proved on the corpus —
see docs/lessons/pdfplumber-quirks.md. Char-level repairs run before line
clustering (by the time lines exist the damage is done); line-level repairs
run right after.
"""

from __future__ import annotations

import re

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


# The words a court's page carries in every language this corpus is in. Used
# as PROOF: an English page decodes with 'the', 'and', 'of' in it; a page
# decoded on the wrong offset carries none of them, and vowel counting cannot
# tell the two apart ('(cid:16)' spells 'cid' often enough to pass).
_PROOF_WORDS = (" the ", " and ", " of ", " to ", " that ", " is ", " we ",
                " court ", " for ", " this ", " not ", " in ")


def mac_ordered_fonts(chars_by_page) -> set:
    """Which of a DOCUMENT'S fonts are addressed by glyph id, decided once
    over every page.

    THE ORDERING IS A PROPERTY OF THE FONT, NOT OF THE PAGE, and proof does
    not arrive evenly: texapp's docketing statement proves itself on page 1
    ('Amended/Corrected Statement Appellate Court…') and then its own later
    pages carry too few words to prove anything, so 2,290 glyphs kept their
    literals in a document whose ordering was settled on the first sheet.
    pasuperct/holbrook is the same story in miniature -- the only broken page
    it has says 'J-S15004-26 / - 23 - / Date: 7/29/2026', which no vocabulary
    test can ever pass. Asked once per document, both are answered.
    """
    per: dict = {}
    unmapped: set = set()
    for chars in chars_by_page:
        for c in chars:
            font = str(c.get("fontname"))
            per.setdefault(font, []).append(c)
            if _CID_RE.match(c.get("text") or ""):
                unmapped.add(font)
    # …AND WHAT THE PAPER ALREADY SAYS ELSEWHERE IS PROOF TOO. Some fonts
    # never carry prose at all: pasuperct/holbrook's one broken page reads
    # 'J-S15004-26 / - 23 - / Date: 7/29/2026', and no vocabulary test will
    # ever pass it. But 'J-S15004-26' is the running head on the other 22
    # pages, set in a font that mapped correctly — so a decode that
    # reproduces a distinctive string the document ALREADY carries has
    # confirmed itself against the document's own text. A wrong offset
    # cannot spell the court's docket number by accident.
    sound = "".join((c.get("text") or "") for font, cs in per.items()
                    if font not in unmapped for c in cs)
    known = {t for t in re.split(r"\s+", sound) if len(t) >= 6}
    proven = set()
    for font in unmapped:
        out = []
        for c in per[font]:
            t = c.get("text") or ""
            m = _CID_RE.match(t)
            code = int(m.group(1)) if m else _font_code(t)
            out.append(_mac_glyph(code) if code is not None else t)
        flat = "".join(out)
        if not _reads_like_text(flat):
            continue
        dec = " ".join(flat.split()).lower()
        if sum(1 for w in _PROOF_WORDS if w in f" {dec} ") >= 3:
            proven.add(font)
            continue
        if any(t in known for t in flat.split() if len(t) >= 6):
            proven.add(font)
    return proven


def decode_cid_glyphs(chars: list, event, proven=frozenset()) -> None:
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
        # A font the DOCUMENT has already proved needs no page's permission.
        if font in proven:
            continue
        mapped = [_mac_glyph(n) for _, n in hits if _mac_glyph(n)]
        # A HANDFUL OF UNKNOWN CODES IS NOT A WRONG OFFSET. cit sets its
        # citation run in a 27-glyph subset that decodes to ', 10 CIT 399,
        # 40405' with six glyphs at code 239 -- past everything this table
        # knows -- and at 21 of 27 in range it failed a 95% coverage bar and
        # kept its literals. The offset is proven by what DOES decode; the
        # rest decode to nothing, exactly as they render now.
        if len(mapped) < max(4, int(0.75 * len(hits))):
            continue                     # offset can't cover this font
        letters = [ch for ch in mapped if ch.isalpha()]
        others = [ch for ch in mapped
                  if not (ch.isalnum() or ch in " .,;:!?()[]'\"-–—&$%/§*†‡")]
        vowels = sum(1 for ch in letters if ch.lower() in "aeiouáéíóú")
        if (not letters or others
                or vowels < 0.15 * len(letters)):
            continue                     # decodes to junk — keep literals
        for i, n in hits:
            ch = _mac_glyph(n)
            if ch:
                chars[i]["text"] = ch
                decoded += 1
    if decoded:
        # Small subsets (a 4-glyph 'hnhn' font inside 'Jo?nson') can't
        # prove themselves — too few letters for the vowel test; once a
        # sibling font proved the +29 ordering on this page, decode their
        # in-range letters too.
        # THE ORDERING BELONGS TO THE PRODUCER, NOT TO ONE SUBSET, so the
        # size bar is gone: cit/american_brass_rod sets 'New York, New York'
        # in one 18-glyph subset (which proves itself) and 'ly ' and two
        # spaces in two more (which cannot -- no vowels, no letters), and
        # those kept their '(cid:N)' literals on a page whose ordering was
        # already established. A font that DISAGREES with the ordering still
        # refuses it above; this only vouches for the ones with nothing to
        # say either way.
        for font, hits in by_font.items():
            for i, n in hits:
                ch = _mac_glyph(n)
                if ch and (ch.isalnum()
                           or ch in " .,;:'\"-()\u00a7\u2018\u2019\u201c\u201d"):
                    if chars[i].get("text") != ch:
                        chars[i]["text"] = ch
                        decoded += 1
    # …AND SOME FONTS HAND BACK THE WRONG LETTERS INSTEAD OF '(cid:N)'.
    # Where pdfminer holds a PARTIAL encoding for a subset it prints what
    # StandardEncoding gives for the glyph's code, so the page comes back in
    # readable characters that are the wrong ones: pasuperct's closing sheet
    # reads 'LUPDI(cid:3)ZH(cid:3)DQG' for 'affirm we and', and only its
    # spaces, digits and punctuation arrive as '(cid:N)'. The loop above
    # cannot see that -- it inspects the unmapped glyphs alone, and here they
    # carry no letters at all, so its own plausibility test refuses the font
    # ('letters=0') and 21 of pasuperct's 42 records graded F on a page that
    # was fully recoverable (the user, 2026-08-23).
    #
    # The signature is mechanical, not linguistic: a font whose every glyph
    # reports width 0.0 is one pdfminer could not measure OR map, and its
    # codes are the subset's glyph ids. The decode still has to prove itself,
    # and vowel counting cannot do it -- '(cid:16)' spells 'cid' often enough
    # to pass -- so the proof is the DOCUMENT'S OWN VOCABULARY: an English
    # page carries 'the', 'and', 'of'; a shifted one carries none of them.
    per_font: dict = {}
    for i, c in enumerate(chars):
        per_font.setdefault(str(c.get("fontname")), []).append(i)
    for font, idxs in per_font.items():
        if font not in by_font:
            continue                     # nothing unmapped: nothing to prove
        if any(chars[i].get("width") for i in idxs):
            continue                     # the font has advances: it is sound
        out = []
        for i in idxs:
            t = chars[i].get("text") or ""
            m = _CID.match(t)
            code = int(m.group(1)) if m else _font_code(t)
            out.append(_mac_glyph(code) if code is not None else t)
        if font not in proven:
            dec = " ".join("".join(out).split()).lower()
            if sum(1 for w in _PROOF_WORDS if w in f" {dec} ") < 3:
                continue                 # nothing readable to go on
            if not _reads_like_text("".join(out)):
                continue
        for i, ch in zip(idxs, out):
            if chars[i].get("text") != ch:
                chars[i]["text"] = ch
                decoded += 1
    if proven:
        # The document's own verdict, applied. A font with advances is decoded
        # only where pdfminer said '(cid:N)' -- its other characters are the
        # ones it mapped correctly; a font with NO advances has all of them
        # wrong, and all of them are decoded.
        _zero: dict = {}
        for i, c in enumerate(chars):
            _zero.setdefault(str(c.get("fontname")), []).append(i)
        for font, idxs in _zero.items():
            if font not in proven:
                continue
            flat = not any(chars[i].get("width") for i in idxs)
            for i in idxs:
                t = chars[i].get("text") or ""
                m = _CID_RE.match(t)
                if not (m or flat):
                    continue
                code = int(m.group(1)) if m else _font_code(t)
                if code is None:
                    continue
                ch = _mac_glyph(code)
                if ch and chars[i]["text"] != ch:
                    chars[i]["text"] = ch
                    decoded += 1
    for i in reversed(notdef):
        del chars[i]
    if decoded or notdef:
        event("cid-glyphs",
              f"decoded {decoded} cid glyphs (+29), "
              f"dropped {len(notdef)} .notdef")



_CID_RE = __import__("re").compile(r"^\(cid:(\d+)\)$")

# THE STANDARD MACINTOSH GLYPH ORDER, past the ASCII run. A subset font
# addressed by glyph id spells its text as `id + 29` from glyph 3 (space) to
# glyph 97 ('~'); above that the order is a list of NAMED glyphs, and these
# four are the ones the corpus actually uses. Derived, not remembered: each
# was learned by decoding pasuperct's broken pages and aligning the result
# against poppler's text for the same page, and each vote was unanimous
# (31/31 for the apostrophe, 7/7, 6/6, 3/3). My own recollection of the order
# was off by one past glyph 178, which is exactly why the table is measured.
_MAC_TAIL = {134: "\u00a7", 179: "\u201c", 180: "\u201d", 182: "\u2019"}
# …AND THE CODE A DISPLAYED CHARACTER CAME FROM. pdfminer does not always
# print '(cid:N)': where it has a partial encoding it prints the glyph
# StandardEncoding gives for that code, so the code has to be read back OUT
# of the character it printed. For ASCII the two coincide; these are the rest.
_STD_INV = {"\u2019": 39, "\u2018": 96, "\u201c": 170, "\u201d": 186,
            "\u2013": 177, "\u2014": 208, "\ufb01": 174, "\ufb02": 175,
            "\u00a7": 167, "\u00b6": 182, "\u2020": 178, "\u2021": 179,
            "\u2022": 183, "\u2026": 188, "\u00b7": 180, "\u201e": 185,
            "\u201a": 184, "\u0192": 166, "\u00a5": 165, "\u00a3": 163,
            "\u00a2": 162, "\u2044": 164, "\u00a1": 161, "\u00ab": 171,
            "\u00bb": 187, "\u2039": 172, "\u203a": 173}


def _mac_glyph(code: int) -> str:
    """The character a glyph id spells in the standard Macintosh ordering."""
    if code < 3:
        return ""
    if code <= 97:
        return chr(code + 29)
    return _MAC_TAIL.get(code, "")


def _font_code(text: str) -> int | None:
    """The code the FONT used for this extracted character."""
    if len(text) != 1:
        return None
    return ord(text) if ord(text) < 128 else _STD_INV.get(text)


# What a court's page is made of, once decoded. Deliberately generous: the
# test below is a JUNK RATE, not a whitelist, because a whitelist fails on the
# one character nobody thought of. pasuperct rules its footnote separator with
# forty-four underscores — glyph 66, decoding to '_' — and an 'others must be
# empty' test threw away a page that had already decoded perfectly
# ('Consequently, we conclude that the trial court's order …') over that one
# rule (the user, 2026-08-23: 'why doesnt this ... remove the CIDs here?').
_PAGE_CHARS = (" .,;:!?()[]{}'\"-\u2013\u2014&$%/\u00a7*\u2020\u2021_@#+=<>|~^`\\"
               "\u2018\u2019\u201c\u201d\u00b6\u00a9\u00ae\u00b0\u00bd\u00be")


def _reads_like_text(s: str) -> bool:
    """The same test this module has always applied to a candidate decode:
    letters dominate, vowels are present, and next to nothing outside a legal
    page's own character set survives. A wrong-but-plausible word is worse
    than visible '(cid:)' garbage, so an implausible font keeps its literals."""
    letters = [ch for ch in s if ch.isalpha()]
    junk = sum(1 for ch in s if not (ch.isalnum() or ch in _PAGE_CHARS))
    vowels = sum(1 for ch in letters if ch.lower() in "aeiou")
    return (bool(letters) and vowels >= 0.15 * len(letters)
            and junk <= 0.02 * max(1, len(s)))


def restore_zero_advance_order(chars: list, event) -> None:
    """A FONT WITH NO WIDTHS HAS NO POSITIONS EITHER, so its text must be read
    in the order the page DRAWS it.

    pasuperct's closing sheet is set in a subset whose descriptor carries no
    widths at all ('Could not get FontBBox … None cannot be parsed as 4
    floats'), so every glyph on it reports width 0.0 and x0 == x1: 348 chars
    all standing at x 72. Read in position order — which is what every line
    walk in this package does — the words come out shuffled ('IRMAF WE AND'
    for 'affirm we and'), and the page renders as nonsense even once its
    glyphs are decoded. The DRAW order is intact, so each row's chars are
    given synthetic advances in stream order: the row keeps its own left
    edge, and half the type size per glyph is close enough for a walk that
    only asks which piece comes first. Geometry on such a page is the
    reader's best reconstruction, never the page's own measure."""
    rows: dict = {}
    for c in chars:
        if c.get("width") or not c.get("upright", True):
            continue
        if (c.get("x1") or 0) - (c.get("x0") or 0) > 0.01:
            continue
        rows.setdefault(round(c.get("top") or 0.0, 1), []).append(c)
    moved = 0
    for _top, run in rows.items():
        if len(run) < 4:
            continue
        left = min(c["x0"] for c in run)
        x = left
        for c in run:
            step = (c.get("size") or 12.0) * (0.28 if (c.get("text") or "") == " "
                                              else 0.5)
            c["x0"] = x
            c["x1"] = x + step
            c["width"] = step
            x += step
            moved += 1
    if moved:
        event("zero-advance-order",
              f"{moved} glyphs in {len(rows)} rows re-laid in draw order")


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


# STACKED ROWS, not one row with an offset run: the share of the merged ink
# covered twice, AND how evenly the ink divides between the two lines. Both
# thresholds must be met to refuse a merge — see the measurement in
# `merge_interleaved`.
_STACKED_ROW_COLLISION = 0.25
_STACKED_ROW_BALANCE = 0.85


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
            # TWO STACKED ROWS COLLIDE; AN OFFSET RUN FILLS A GAP. The width
            # test below compares total ink against the union SPAN, which a
            # two-column line satisfies for free — its two short columns
            # leave most of the measure empty however they are stacked. So a
            # letterhead's own rows were fused into one: almd/70991.238.0
            # sets 'David J. Smith' over 'Clerk of Court' at x72 and 'For
            # rules and forms visit' over 'www.ca11.uscourts.gov' at x306,
            # 8.6pt apart, and the merge rendered
            # 'DClaevrikd  oJf.  CSmouitrht' (the user, 2026-08-22: 'this is
            # a letter').
            #
            # TWO SIGNALS, AND BOTH ARE REQUIRED. Neither separates the
            # families alone — measured across five courts, a genuine merge
            # reaches a collision of 0.201 (minnag's scanned AG opinion,
            # whose OCR baselines really do overlap) and an ink balance of
            # 0.78 ('1.' over 'OF' on nevapp's raster), so either test alone
            # refuses a merge that belongs. What no genuine merge does is
            # score high on both: the highest is 0.78 balance at 0.000
            # collision, or 0.32 balance at 0.201. The letterhead is 0.96
            # and 0.445.
            #
            #   collision — the share of the merged ink covered twice once
            #     the glyphs are laid in x order. An offset run fills a gap
            #     its host left and tiles; two stacked rows cover the same
            #     span twice and nearly every neighbour collides.
            #   balance   — the smaller row's ink over the larger's. A
            #     merge that belongs is a host plus a FRAGMENT ('proc', ':',
            #     'Ave.', 'Appellants,'); two rows of a letterhead are both
            #     whole.
            _seq = sorted(merged_chars, key=lambda c: c["x0"])
            _collide = 0.0
            for _a, _b in zip(_seq, _seq[1:]):
                _ov = min(_a["x1"], _b["x1"]) - max(_a["x0"], _b["x0"])
                if _ov > 0:
                    _collide += _ov
            _ink_a = sum(c["x1"] - c["x0"] for c in _printable(prev))
            _ink_b = sum(c["x1"] - c["x0"] for c in _printable(ln))
            _balance = min(_ink_a, _ink_b) / max(_ink_a, _ink_b, 0.1)
            if (_collide >= _STACKED_ROW_COLLISION * max(glyphs, 0.1)
                    and _balance >= _STACKED_ROW_BALANCE):
                out.append(ln)
                continue
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
                         offset_max: float = 5.0,
                         skip: set | None = None) -> None:
    """Mark chars underlined by a hairline rect near the baseline
    (sets ``_underline=True`` on the char dicts). The char box's bottom
    includes descender space, so a true underline may measure slightly
    ABOVE it (nh draws at −1.3pt) — a strike-through sits at −4 and
    below, outside the window.

    ``skip``: rect ids withheld from the pass — a drawn table's cell borders
    sit exactly where an underline sits (see pdfio.tables.row_edge_rects)."""
    hairlines = [r for r in rects
                 if r.get("height", 0) < 2 and (r["x1"] - r["x0"]) > 6
                 and not (skip and id(r) in skip)]
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


# A HIGHLIGHTER IS DRAWN, NOT WRITTEN. Where a chambers (or whoever filed the
# paper) highlights a passage, the PDF fills a coloured rectangle BEHIND the
# glyphs and the text layer says nothing about it — so the emphasis, which is
# the whole point of the marking, is invisible to a reader of the extraction.
# alnd/201258.14.0 highlights 40 spans on its first page in pure yellow
# (non-stroking colour 1,1,0) and they came out as ordinary prose (the user,
# 2026-08-22).
#
# Not an annotation: a PDF /Highlight annot is a different animal and this
# corpus does not use it — these are painted rects, which is why they survive
# flattening.
#
# A HIGHLIGHT IS A BLOCK OF COLOUR, and that is what separates it from every
# other rect the page draws: an underline and a table border are hairlines
# (see `tag_underlined_chars`, height < 2), a redaction is BLACK and stands
# where the glyphs are missing, and the paper itself is white. So the test is
# a fill that is neither near-white nor near-black, tall enough to sit behind
# a row of type, with type inside it.
_HL_MIN_HEIGHT = 5.0
# How far from white or black a fill must be to be a highlighter's colour.
# Measured: the yellow is (1, 1, 0) — 1.0 off white on its blue channel and
# 2.0 off black across the three. Grey page furniture sits within 0.12 of the
# diagonal and is excluded by the saturation floor rather than by brightness.
_HL_SATURATION = 0.25


def _fill_rgb(rect) -> tuple | None:
    """A rect's fill as (r, g, b) in 0..1, or None when it has none. PDF fills
    arrive as a scalar (grey), a 3-tuple (RGB) or a 4-tuple (CMYK)."""
    col = rect.get("non_stroking_color")
    if col is None:
        return None
    if isinstance(col, (int, float)):
        return (float(col),) * 3
    vals = [float(v) for v in col]
    if len(vals) == 1:
        return (vals[0],) * 3
    if len(vals) == 3:
        return tuple(vals)
    if len(vals) == 4:
        c, m_, y, k = vals
        return (max(0.0, 1 - min(1, c + k)), max(0.0, 1 - min(1, m_ + k)),
                max(0.0, 1 - min(1, y + k)))
    return None


def highlight_rects(rects: list) -> list:
    """The rects that are highlighter marks — a saturated fill, tall enough to
    stand behind a row of type."""
    out = []
    for r in rects:
        if (r.get("height") or (r["bottom"] - r["top"])) < _HL_MIN_HEIGHT:
            continue
        rgb = _fill_rgb(r)
        if rgb is None:
            continue
        if max(rgb) - min(rgb) < _HL_SATURATION:
            continue          # white, black or grey: the paper or a redaction
        out.append(r)
    return out


def tag_highlighted_chars(rects: list, lines: list) -> int:
    """Mark chars standing on a highlighter's fill (``_highlight=True`` on the
    char dicts). Returns the number of rows touched."""
    marks = highlight_rects(rects)
    if not marks:
        return 0
    n = 0
    for line in lines:
        chars = line.get("chars") or []
        if not chars:
            continue
        hit = False
        for c in chars:
            cmid = (c["x0"] + c["x1"]) / 2
            cvmid = (c["top"] + c["bottom"]) / 2
            for r in marks:
                if (r["x0"] - 1 <= cmid <= r["x1"] + 1
                        and r["top"] - 1 <= cvmid <= r["bottom"] + 1):
                    c["_highlight"] = True
                    hit = True
                    break
        if hit:
            n += 1
    return n


# --------------------------------------------------------------------------
# redaction boxes
# --------------------------------------------------------------------------

# A name blacked out for privacy is DRAWN, not written: the PDF fills a small
# black rectangle where the glyphs stood, and the text layer says nothing at
# all. Read as text the sentence loses its subject — acca/kindschi says "the
# victim ran into SPC who testified" 31 times over — and when the box is the
# last thing on a line, that line ends bare and the paragraph below welds
# itself on ("B. Victim's Statement to SPC" fused into "Appellant alleges").
#
# So the box becomes what it replaced: chars. One block glyph per glyph-width
# of box, at the box's own place in the line, CLONED FROM THE LINE'S OWN TYPE
# so every later stage measures it like any other word. The clone keeps the
# template's top/bottom and size rather than the rect's: the box is drawn a
# little taller than the type it covers, and a line's band and its measured
# top are load-bearing (see build_page's topping pass).
#
# The size window is what separates a redaction from the other black things a
# court draws, and it is deliberately SMALL: only a box the size of a word.
# MEASURED, and the band between the two populations is empty — acca's 31
# redactions run 14.7-33.2pt wide and 8.4-12.6pt tall (a name), while the
# black fills of njd 512314.29 and nynd 141588.92 run 124-468pt wide and are
# NOT redactions at all (the user read those pages, 2026-08-21). The cap sits
# in the empty band. A wider redaction is therefore MISSED, not misread,
# which is the safe direction: a bar stamped over a rule would delete a
# document's furniture boundary. Rules proper never reach this pass —
# collect_rules takes rects under 2.5pt in one dimension.
_REDACT_MIN_W = 6.0
_REDACT_MAX_W = 72.0
_REDACT_MIN_H = 4.0
_REDACT_MAX_H = 26.0
# How far from the box its line's nearest glyph may sit and still make the box
# INLINE. A redaction stands in a sentence, touching the words on either side;
# a black square alone in the middle of a figure is not a lost name.
_REDACT_INLINE_GAP = 24.0
REDACTION_GLYPH = "█"          # FULL BLOCK — N of them are one solid bar


# …AND SOMETIMES THE BAR IS A CHARACTER. The pass below reads redactions the
# page DRAWS as filled rects; akd/62768.505.0 does it the other way — the bar
# is a glyph in the text layer, a hyphen from a bold font rendered 30pt wide
# over 12pt type. Nothing about the char stream says 'redaction': the text
# came out as 'relationship with- throughout her', so the reader lost the
# subject of the sentence AND the record was graded down for 18 broken
# hyphen-joins that were never hyphens (the user, 2026-08-23: 'shouldnt this
# one identfiy redactions? … and teh boxes?').
#
# MEASURED, on that document: its real hyphens are 3.8-5.7pt wide, and its
# bars 28.4-29.9pt — a full em-dash is 1.0em, so a thin punctuation mark set
# wider than 1.5em is not that mark. The height test keeps it to a bar as
# tall as the type it covers, and the black fill is what makes it a bar
# rather than a rule.
_BAR_CHARS = frozenset("-\u2010\u2011\u2012\u2013\u2014\u2015_\u00ad")
_BAR_MIN_EM = 1.5              # wider than any dash the character could be
_BAR_MIN_HEIGHT_EM = 0.55      # as tall as the type, not a rule


def _is_black_glyph(c) -> bool:
    nsc = c.get("non_stroking_color")
    if isinstance(nsc, (list, tuple)):
        return bool(nsc) and all(v == 0 for v in nsc)
    return nsc in (0, 0.0)


def convert_bar_glyphs(lines: list, event) -> None:
    """Turn a glyph that IS a black bar into block glyphs, in place.

    The same output as `insert_redaction_boxes` — one `REDACTION_GLYPH` per
    glyph-width of bar — so every later stage, and every reader, sees a
    redaction rather than a stray dash."""
    n = 0
    for line in lines:
        chars = line.get("chars") or []
        ink = [c for c in chars if (c.get("text") or "").strip()]
        if not ink:
            continue
        widths = sorted((c["x1"] - c["x0"]) for c in ink
                        if (c.get("text") or "") not in (" ", ""))
        glyph_w = widths[len(widths) // 2] if widths else 5.0
        if glyph_w <= 0.5:
            glyph_w = 5.0
        out: list = []
        hit = False
        for c in chars:
            txt = c.get("text") or ""
            size = c.get("size") or 0.0
            w = c["x1"] - c["x0"]
            h = c["bottom"] - c["top"]
            if (txt in _BAR_CHARS and size > 0
                    and w >= _BAR_MIN_EM * size
                    and h >= _BAR_MIN_HEIGHT_EM * size
                    and _is_black_glyph(c)):
                k = max(1, int(round(w / glyph_w)))
                step = w / k
                for i in range(k):
                    b = dict(c)
                    b["text"] = REDACTION_GLYPH
                    b["x0"] = c["x0"] + i * step
                    b["x1"] = c["x0"] + (i + 1) * step
                    b["width"] = step
                    b["_redaction"] = True
                    b.pop("_underline", None)
                    out.append(b)
                hit = True
                n += 1
                continue
            out.append(c)
        if not hit:
            continue
        line["chars"] = out
        line["text"] = "".join(c.get("text") or "" for c in out)
    if n:
        event("redaction", f"{n} blacked-out glyphs read as block glyphs")


def _is_black_fill(rect) -> bool:
    if not rect.get("fill"):
        return False
    nsc = rect.get("non_stroking_color")
    if isinstance(nsc, (list, tuple)):
        return bool(nsc) and all(v == 0 for v in nsc)
    return nsc in (0, 0.0)


def insert_redaction_boxes(rects: list, lines: list, event,
                           skip: set | None = None) -> None:
    """Turn each blacked-out box into block glyphs inside its own line.

    ``skip``: rect ids withheld — a drawn table's cell borders and fills are
    not redactions (see pdfio.tables.row_edge_rects)."""
    boxes = []
    for r in rects:
        if skip and id(r) in skip:
            continue
        if not _is_black_fill(r):
            continue
        w = r["x1"] - r["x0"]
        h = r.get("height", r["bottom"] - r["top"])
        if _REDACT_MIN_W <= w <= _REDACT_MAX_W and _REDACT_MIN_H <= h <= _REDACT_MAX_H:
            boxes.append(r)
    if not boxes:
        return
    n_boxes = 0
    for line in lines:
        chars = line.get("chars") or []
        ink = [c for c in chars if (c.get("text") or "").strip()]
        if not ink:
            continue
        top = min(c["top"] for c in ink)
        bottom = max(c["bottom"] for c in ink)
        # The line's own glyph advance, so a wide box loses more glyphs than a
        # narrow one and the bar keeps the name's length.
        widths = sorted((c["x1"] - c["x0"]) for c in ink
                        if (c.get("text") or "") != " ")
        glyph_w = widths[len(widths) // 2] if widths else 5.0
        if glyph_w <= 0.5:
            glyph_w = 5.0
        added = []
        for r in boxes:
            if r.get("_redaction_used"):
                continue
            cy = (r["top"] + r["bottom"]) / 2
            if not (top - 1.0 <= cy <= bottom + 1.0):
                continue
            # REVERSE VIDEO IS NOT A REDACTION: a black box with glyphs of its
            # own is a highlighted word (its white type is already gone —
            # drop_white_glyphs ran first), and stamping blocks over it would
            # delete text the court wrote.
            if any(r["x0"] - 0.5 <= (c["x0"] + c["x1"]) / 2 <= r["x1"] + 0.5
                   for c in ink):
                continue
            near = min((max(r["x0"] - c["x1"], c["x0"] - r["x1"], 0.0)
                        for c in ink), default=None)
            if near is None or near > _REDACT_INLINE_GAP:
                continue
            template = min(ink, key=lambda c: max(r["x0"] - c["x1"],
                                                  c["x0"] - r["x1"], 0.0))
            n = max(1, int(round((r["x1"] - r["x0"]) / glyph_w)))
            step = (r["x1"] - r["x0"]) / n
            for i in range(n):
                c = dict(template)
                c["text"] = REDACTION_GLYPH
                c["x0"] = r["x0"] + i * step
                c["x1"] = r["x0"] + (i + 1) * step
                c["width"] = step
                c["_redaction"] = True
                c.pop("_underline", None)
                added.append(c)
            r["_redaction_used"] = True
            n_boxes += 1
        if not added:
            continue
        chars.extend(added)
        chars.sort(key=lambda c: c["x0"])
        line["chars"] = chars
        line["x0"] = min(c["x0"] for c in chars)
        line["x1"] = max(c["x1"] for c in chars)
        line["text"] = "".join(c.get("text") or "" for c in chars)
    for r in boxes:
        r.pop("_redaction_used", None)
    if n_boxes:
        event("redaction", f"{n_boxes} blacked-out boxes read as block glyphs")


# --------------------------------------------------------------------------
# glyph rails
# --------------------------------------------------------------------------

# A COLUMN OF ONE GLYPH IS A RAIL, NOT A RUN OF FOOTNOTE LABELS. A pleading
# caption is ruled with a stacked glyph — ')' (asbca, ortc, ca6), ':'
# (njtaxct), '§' (texbizct) — and each glyph is a line of its own beside the
# party column. Three of those characters are also FOOTNOTE LABELS, so a
# '§'-only line read as a label opened a note on the caption row beside it:
# texbizct/energy_founders_fund_v._daskevich published eleven of its own
# caption rows as headmatter footnotes, '§PHILLIP DASKEVICH and CRIS',
# '§CURNUTT DASKEVICH, both' … (the user, 2026-08-21).
#
# What separates the two is the COLUMN. A label stands once; a rail stacks.
# The test is therefore three or more single-glyph lines of the SAME character
# at the SAME x — which no footnote series satisfies, because a court that
# labels its notes with symbols walks the series ('*', '†', '‡') rather than
# repeating one glyph, and numbered notes are not one character three times.
_RAIL_STACK_MIN = 3
_RAIL_X_WINDOW = 3.0


def tag_rail_glyphs(lines: list, event) -> None:
    """Mark the glyphs of a stacked one-character rail (``_rail=True``)."""
    stacks: dict = {}
    for ln in lines:
        chars = [c for c in (ln.get("chars") or [])
                 if (c.get("text") or "").strip()]
        if len(chars) != 1:
            continue
        c = chars[0]
        stacks.setdefault(((c.get("text") or ""),
                           round(c["x0"] / _RAIL_X_WINDOW)), []).append(c)
    total = 0
    glyphs: set = set()
    for (glyph, _x), cs in stacks.items():
        if len(cs) < _RAIL_STACK_MIN:
            continue
        for c in cs:
            c["_rail"] = True
        total += len(cs)
        glyphs.add(glyph)
    if total:
        event("glyph-rail",
              f"{total} stacked {sorted(glyphs)} glyphs tagged as a rail")
