"""Styled headmatter reproduction: the page's OWN formatting, extracted.

Alignment per line (centered stays centered, right stays right, and a row
centered on its own column axis uses ``rel``), bold/italic inline, vertical
rhythm via Gap, rules only where the page draws them (Rule), nothing for a
Divider. The caption block renders its two columns with the rail glyph or
drawn border the fingerprint measured — the SAME object the classifier used.
"""

from __future__ import annotations

from html import escape

from .. import model as m
from .inline import inline_to_html

_ALIGN_CLASS = {m.Align.LEFT: "al", m.Align.CENTER: "ac", m.Align.RIGHT: "ar"}


def _hm_line(row: m.HmLine, base_size: float) -> str:
    cls = ["hmrow", _ALIGN_CLASS[row.align]]
    style = []
    if base_size and row.size and abs(row.size - base_size) >= 1.0:
        style.append(f"font-size:{row.size / base_size:.2f}em")
    if row.rel:
        style.append(f"--rel:{row.rel:.1f}pt")
        cls.append("rel")
    # Bold/italic runs are already inline in the markup; the flags are
    # classification signals, not render instructions.
    text = inline_to_html(row.text)
    s = f' style="{";".join(style)}"' if style else ""
    r = f' data-role="{row.role}"' if row.role else ""
    return (f'<div class="{" ".join(cls)}"{s}{r} data-pg="{row.prov.page}">'
            f"{text}</div>")


def _caption(block: m.CaptionBlock, base_size: float) -> str:
    left = "".join(_hm_line(r, base_size) for r in block.left)
    right = "".join(_hm_line(r, base_size) for r in block.right)
    if block.rail == "|":
        mid = '<div class="rail drawn"></div>'
    elif block.rail:
        n = max(block.rail_rows, 1)
        glyphs = "".join(f"<span>{block.rail}</span>" for _ in range(n))
        mid = f'<div class="rail glyphs">{glyphs}</div>'
    else:
        mid = '<div class="rail open"></div>'
    style = f' data-style="{block.style_id}"' if block.style_id else ""
    return (f'<div class="caption"{style}>'
            f'<div class="cap-left">{left}</div>{mid}'
            f'<div class="cap-right">{right}</div></div>')


def render_hm_items(items: list, base_size: float = 12.0) -> str:
    out = []
    for item in items:
        match item:
            case m.HmLine():
                out.append(_hm_line(item, base_size))
            case m.CaptionBlock():
                out.append(_caption(item, base_size))
            case m.Rule():
                cls = "typedrule" if item.typed else "rule"
                out.append(f'<div class="{cls} span-{item.span}"></div>')
            case m.Divider():
                out.append('<div class="divider"></div>')   # draws nothing
            case m.Gap():
                out.append(f'<div class="gap" style="height:{item.lines}em"></div>')
            case m.ImageBlock():
                dims = ""
                if item.width and item.height:
                    dims = f' width="{item.width:.0f}" height="{item.height:.0f}"'
                out.append(f'<img class="hm-img" src="{item.src}"{dims} alt="">')
            case _:
                raise TypeError(f"render_hm_items: {type(item)!r}")
    return "".join(out)


# --------------------------------------------------------------------------
# the same cover, said in a way that survives the trip
# --------------------------------------------------------------------------
# Public: `render_hm_inline`. The class-based `render_hm_items` above needs
# this package's stylesheet to mean anything, which a consumer does not
# have — so an ingest is handed THIS instead (the user, 2026-08-24: 'i want
# to be able to [have] the same rows with the layout stated inline … because
# i want to try using this'). Both are returned; neither replaces the other.
# --------------------------------------------------------------------------
# THE LAYOUT HAS TO BE IN THE MARKUP, not in a stylesheet the receiving page
# has never seen. Every carrier below is inline: alignment as `text-align`,
# a hanging indent as `margin-left`, a two-column caption as a TABLE ROW PER
# PRINTED ROW — which is the thing that actually matters, because it keeps
# each docket number beside the party row the court set it beside instead of
# dumping every number after every party — and a rule the page draws as an
# <hr> that draws. Nothing here needs a class to mean something.
def render_hm_inline(items: list, base_size: float = 12.0,
                     fn_ns: str | None = None) -> str:
    out: list[str] = []
    for item in items:
        match item:
            case m.HmLine():
                out.append(_inline_row(item, base_size, fn_ns))
            case m.CaptionBlock():
                out.append(_inline_caption(item, base_size, fn_ns))
            case m.Rule():
                width = {"full": "100%", "left": "48%", "right": "48%",
                         "center": "40%"}.get(item.span, "100%")
                # THE SHORTHAND PUT `auto` IN THE BOTTOM SLOT. Written as
                # `margin:.45em {margin}` with margin='0 auto', the rule
                # read `margin:.45em 0 auto` — three values, which CSS takes
                # as top / left-right / bottom, so the horizontal margins
                # were ZERO and every centred rule hung off the left margin;
                # the right-hand form emitted five values and was dropped
                # whole. Measured on utah/anderson_v._hon._bates, whose
                # seven rules are all `span-center` and every one of which
                # drew hard left under centred type (the user, 2026-08-24:
                # 'the LINES it would draw are all left aligned but they
                # should probably always be centered'). Each side is now
                # written out in full, so the value cannot shift slots.
                # A RULE IS A SECTION BOUNDARY, and it needs room to read
                # as one. At .45em the divider sat as close to the row above
                # it as that row's own neighbours, so the publication
                # notice, the caption, the counsel block and the opinion
                # head ran together as one grey wall (the user, 2026-08-24:
                # 'id like to add a little vertical space betwween unique
                # sections'). Stated INLINE like everything else here: this
                # block is the portable one, handed to an ingest with no
                # stylesheet of ours to lean on.
                margin = {"center": "1.1em auto",
                          "right": "1.1em 0 1.1em auto",
                          "left": "1.1em auto 1.1em 0"}.get(item.span, "1.1em 0")
                out.append(f'<hr style="border:0;border-top:1px solid #999;'
                           f'width:{width};margin:{margin}">')
            case m.Divider():
                pass                       # a boundary, not a mark
            case m.Gap():
                out.append(f'<div style="height:{item.lines}em"></div>')
            case m.ImageBlock():
                dim = ""
                if item.width and item.height:
                    dim = f' width="{item.width:.0f}" height="{item.height:.0f}"'
                out.append(f'<img src="{item.src}"{dim} alt="">')
    return "".join(out)


def _inline_style(row: m.HmLine, base_size: float) -> str:
    bits = []
    if row.align is m.Align.CENTER:
        bits.append("text-align:center")
    elif row.align is m.Align.RIGHT:
        bits.append("text-align:right")
    if base_size and row.size and abs(row.size - base_size) >= 1.0:
        bits.append(f"font-size:{row.size / base_size:.2f}em")
    if row.rel:
        bits.append(f"margin-left:{row.rel:.0f}pt")
    return ";".join(bits)


def _inline_row(row: m.HmLine, base_size: float,
                fn_ns: str | None = None) -> str:
    # THE VOCABULARY DOES NOT TRAVEL RAW. The review row runs inline_to_html
    # (see _hm_line); this one shipped `row.text` as-is, so a cover row
    # carrying <footnotemark> or <pagenumber/> reached the ingest as model
    # tags no browser knows. Converted here like everywhere else — and with
    # `fn_ns`, a cover mark becomes a real anchor to its note.
    if not (row.text or "").strip():
        return '<div style="height:.9em"></div>'
    text = inline_to_html(row.text, fn_ns)
    style = _inline_style(row, base_size)
    # THE AIR THE PAGE LEFT, carried through. A court groups its cover with
    # blank lines as much as with rules — ca6 sets one above 'Decided and
    # Filed:', above 'Before: SILER, MOORE, …' and above 'COUNSEL' — and
    # rendered flush those rows read as a single block. The measure is the
    # page's own (see `HmLine.space_before`), stated inline because this
    # block travels to an ingest with no stylesheet of ours.
    if row.space_before:
        style = f"margin-top:{row.space_before:.2f}em" + (
            ";" + style if style else "")
    s = f' style="{style}"' if style else ""
    return f"<div{s}>{text}</div>"


def _inline_caption(block: m.CaptionBlock, base_size: float,
                    fn_ns: str | None = None) -> str:
    """A two-column caption as a table, ONE ROW PER PRINTED ROW.

    The cells are already paired by the row they came off the page on, so
    the pairing is the thing to keep: it is what puts 'Case No.
    3:25-cv-00316-SLG' beside its own action instead of after it."""
    rows = []
    rail = block.rail if block.rail and block.rail != "|" else ""
    border = ("border-left:1px solid #999"
              if block.rail == "|" else "")
    for left, right in zip(block.left, block.right):
        lt = inline_to_html(left.text, fn_ns) if left is not None else ""
        rt = inline_to_html(right.text, fn_ns) if right is not None else ""
        ls = _inline_style(left, base_size) if left is not None else ""
        rs = _inline_style(right, base_size) if right is not None else ""
        rows.append(
            '<tr>'
            f'<td style="width:52%;vertical-align:top;padding:.05em .4em .05em 0;'
            f'{ls}">{lt or "&nbsp;"}</td>'
            f'<td style="width:1em;text-align:center;vertical-align:top;'
            f'padding:.05em .3em;{border}">{escape(rail)}</td>'
            f'<td style="width:47%;vertical-align:top;padding:.05em 0 .05em .4em;'
            f'{rs}">{rt or "&nbsp;"}</td></tr>')
    top = f"{block.space_before:.2f}em" if block.space_before else ".3em"
    return ('<table style="width:100%;border-collapse:collapse;'
            f'margin:{top} 0 .3em">{"".join(rows)}</table>')
