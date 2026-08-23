"""Rebuilding text from chars: measured word breaks, no guessed constants.

pdfplumber's own ``line['text']`` drops spaces between kerned glyphs (a
small-caps name renders 'DWIGHT E.TARWATER,J.,delivered'), so every consumer
uses this rebuild instead. The word-break threshold is MEASURED per line —
see docs/lessons/measured-geometry.md for the two bugs that wrote the rules.
"""

from __future__ import annotations

import re

# Floor for the inferred word-break gap. Historic fixed threshold; the
# measured value below only ever rises above it.
SPACE_GAP_MIN = 1.5


def inferred_space_gap(chars: list) -> float:
    """The x-gap that means a word break on THIS line, measured.

    The modal gap between adjacent glyphs is the line's tracking; the width of
    its own space glyph is what a word break costs. When the page sets real
    space glyphs, a gap narrower than one of those spaces is justification
    tracking, not a break — require the full measured word-break advance.

    A line carrying NO space glyph keeps the historic floor: there is nothing
    to measure against, and on an ornamental break ('* * *') the only gaps
    present ARE the word gaps — treating them as tracking closed the rule up
    to '***' and deleted body text. No evidence → the floor, unchanged."""
    gaps: list[float] = []
    widths: list[float] = []
    prev = None
    for c in chars:
        text = c.get("text") or ""
        if text == " ":
            widths.append(c["x1"] - c["x0"])
        elif prev is not None:
            gaps.append(c["x0"] - prev)
        prev = None if text == " " else c["x1"]
    if not gaps or not widths:
        return SPACE_GAP_MIN
    gaps.sort()
    widths.sort()
    track = gaps[len(gaps) // 2]
    return max(SPACE_GAP_MIN, track + widths[len(widths) // 2])


def inline_text(chars: list, label_chars: set, canon, mark_flags: list | None,
                bracket_pinpoint: bool = False) -> str:
    """The line's text with inline formatting preserved: <strong>/<em>/<u>/
    <mark> runs, <footnotemark>N</footnotemark> for raised label glyphs (per
    ``mark_flags``, computed by the footnote subsystem's mark test), literal
    text XML-escaped, word breaks measured. Ported from the old
    line_inline_text: double-emitted ligature glyphs skipped."""
    from html import escape

    if not chars:
        return ""
    space_gap = inferred_space_gap(chars)
    parts: list[str] = []
    buf = ""
    in_bold = in_italic = in_underline = in_highlight = False
    cur_fn = ""
    prev_x1 = None
    prev_pos = None
    in_brace = False

    def style_wrap(text: str) -> str:
        t = escape(text)
        if in_italic:
            t = f"<em>{t}</em>"
        if in_bold:
            t = f"<strong>{t}</strong>"
        if in_underline:
            t = f"<u>{t}</u>"
        if in_highlight:
            t = f"<mark>{t}</mark>"
        return t

    def flush_buf():
        nonlocal buf
        if buf:
            parts.append(style_wrap(buf))
            buf = ""

    for ci, c in enumerate(chars):
        pos = (round(c["x0"], 1), round(c["x1"], 1), c.get("text"))
        if pos == prev_pos:
            continue
        prev_pos = pos
        if bracket_pinpoint:
            if c.get("text") in "{[":
                in_brace = True
            elif c.get("text") in "}]":
                in_brace = False
        fn = c.get("fontname") or ""
        ch_bold = "Bold" in fn
        ch_italic = ("Italic" in fn) or ("Oblique" in fn)
        ch_underline = bool(c.get("_underline"))
        ch_highlight = bool(c.get("_highlight"))
        if prev_x1 is not None:
            gap = c["x0"] - prev_x1
            # A STYLE CHANGE is itself word-boundary evidence (mont sets
            # 'defendants <em>Dennis E. Lind</em>' with no space glyph and
            # a gap under the justified line's full word-break) — words
            # don't change face mid-word, so half the measured break
            # suffices there. A lowercase→UPPERCASE transition says the
            # same ('defendantsDennis'); Mc/Van prefixes survive because
            # their internal gap is kerning-tight, nowhere near half a
            # word break.
            thresh = space_gap
            prev_txt = chars[ci - 1].get("text") or "" if ci else ""
            cur_txt = c.get("text") or ""
            if (ch_bold != in_bold or ch_italic != in_italic
                    or ch_underline != in_underline
                    or (prev_txt[-1:].islower() and cur_txt[:1].isupper())):
                thresh = max(SPACE_GAP_MIN, (space_gap + SPACE_GAP_MIN) / 2)
            if gap > thresh:
                if cur_fn:
                    parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
                    cur_fn = ""
                    buf += " "
                elif buf and not buf.endswith(" "):
                    buf += " "
        small = bool(mark_flags[ci]) if mark_flags else False
        is_label = canon(c.get("text") or "") in label_chars and not in_brace
        if small and is_label:
            flush_buf()
            cur_fn += canon(c.get("text") or "")
        else:
            if cur_fn:
                parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
                cur_fn = ""
            style_changed = (ch_bold != in_bold or ch_italic != in_italic
                             or ch_underline != in_underline
                             or ch_highlight != in_highlight)
            if style_changed and buf:
                flush_buf()
                in_bold, in_italic, in_underline, in_highlight = (
                    ch_bold, ch_italic, ch_underline, ch_highlight)
            elif not buf:
                in_bold, in_italic, in_underline, in_highlight = (
                    ch_bold, ch_italic, ch_underline, ch_highlight)
            buf += c.get("text") or ""
        prev_x1 = c["x1"]
    if cur_fn:
        parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
    flush_buf()
    out = "".join(parts)
    # A style run holding ONLY whitespace is debris (a bold space between
    # bold words emits '<strong> </strong>') — the space itself stays.
    out = re.sub(r"<(strong|em|u)>(\s*)</\1>", r"\2", out)
    return out


def plain_text(chars: list) -> str:
    """The line's text as plain characters with gap-based space insertion.
    Double-emitted ligature glyphs (two identical chars at identical
    coordinates) are skipped so 'offices' doesn't read 'offifices'."""
    if not chars:
        return ""
    out: list[str] = []
    space_gap = inferred_space_gap(chars)
    prev_x1 = None
    prev_pos = None
    for c in chars:
        pos = (round(c["x0"], 1), round(c["x1"], 1), c.get("text"))
        if pos == prev_pos:
            continue
        prev_pos = pos
        if (prev_x1 is not None and (c["x0"] - prev_x1) > space_gap
                and out and not out[-1].endswith(" ")):
            out.append(" ")
        out.append(c.get("text") or "")
        prev_x1 = c["x1"]
    return "".join(out)
