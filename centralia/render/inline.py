"""Inline-markup passthrough: the model's marked-up strings -> review HTML.

The vocabulary (<em> <strong> <u> <footnotemark> <pagenumber/> <centered>
<flushright>) passes through with only presentation rewrites; literal text is
already XML-escaped by the extractor.
"""

from __future__ import annotations

import re

_PAGENUM = re.compile(r'<pagenumber value="([^"]*)"\s*/>')
_FNMARK = re.compile(r"<footnotemark>([^<]*)</footnotemark>")


def footnote_slug(label: str) -> str:
    """An id-safe fragment for a footnote label, the SAME from both ends.

    A mark and its note only ever see the label — '7', '*', a dagger — so
    the slug has to be derivable from the label alone or the two sides
    cannot agree on an anchor. Alphanumeric labels pass through; a symbol
    becomes its codepoints ('*' -> 'u42'), which is stable, id-safe, and
    never collides with a printed number.
    """
    cleaned = "".join(ch for ch in (label or "") if ch.isalnum())
    return cleaned or "u" + "-".join(str(ord(ch)) for ch in label or "?")


def mark_slugs(markups: list[str]) -> set[str]:
    """Every footnote mark set in these strings, as slugs.

    This is how a note body knows whether its back-link has somewhere to
    land: a note whose reference was never printed (or never read) gets a
    plain label instead of a link to nowhere.
    """
    out: set[str] = set()
    for markup in markups:
        for label in _FNMARK.findall(markup or ""):
            out.add(footnote_slug(label))
    return out


def inline_to_html(markup: str, fn_ns: str | None = None) -> str:
    """The model's inline vocabulary as HTML.

    With ``fn_ns`` set, a footnote mark becomes a real anchor — an id on the
    mark and an href to its note — namespaced so that several writings on
    one page, each restarting its notes at 1, cannot collide. Without it,
    the mark stays the inert review-page <sup>, whose linking the viewer
    does not need.
    """
    s = markup or ""
    s = _PAGENUM.sub(lambda mo: f'<span class="pg" title="page {mo.group(1)}">'
                                f"{mo.group(1)}</span>", s)
    if fn_ns:
        s = _FNMARK.sub(
            lambda mo: (
                f'<sup class="fnmark" id="ref-{fn_ns}-'
                f'{footnote_slug(mo.group(1))}">'
                f'<a href="#fn-{fn_ns}-{footnote_slug(mo.group(1))}">'
                f"{mo.group(1)}</a></sup>"),
            s)
    else:
        s = _FNMARK.sub(lambda mo: f'<sup class="fnmark">{mo.group(1)}</sup>', s)
    s = s.replace("<centered>", '<span class="ctr">').replace("</centered>", "</span>")
    s = s.replace("<flushright>", '<span class="fr">').replace("</flushright>", "</span>")
    return s
