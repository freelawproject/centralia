"""Inline-markup passthrough: the model's marked-up strings -> review HTML.

The vocabulary (<em> <strong> <u> <footnotemark> <pagenumber/> <centered>
<flushright>) passes through with only presentation rewrites; literal text is
already XML-escaped by the extractor.
"""

from __future__ import annotations

import re

_PAGENUM = re.compile(r'<pagenumber value="([^"]*)"\s*/>')
_FNMARK = re.compile(r"<footnotemark>([^<]*)</footnotemark>")


def inline_to_html(markup: str) -> str:
    s = markup or ""
    s = _PAGENUM.sub(lambda mo: f'<span class="pg" title="page {mo.group(1)}">'
                                f"{mo.group(1)}</span>", s)
    s = _FNMARK.sub(lambda mo: f'<sup class="fnmark">{mo.group(1)}</sup>', s)
    s = s.replace("<centered>", '<span class="ctr">').replace("</centered>", "</span>")
    s = s.replace("<flushright>", '<span class="fr">').replace("</flushright>", "</span>")
    return s
