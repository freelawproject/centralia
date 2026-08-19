"""Styled headmatter reproduction: the page's OWN formatting, extracted.

Alignment per line (centered stays centered, right stays right, and a row
centered on its own column axis uses ``rel``), bold/italic inline, vertical
rhythm via Gap, rules only where the page draws them (Rule), nothing for a
Divider. The caption block renders its two columns with the rail glyph or
drawn border the fingerprint measured — the SAME object the classifier used.
"""

from __future__ import annotations

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
