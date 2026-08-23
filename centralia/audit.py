"""Coverage + correctness auditing.

This module starts with the NORMALIZATION layer, ported verbatim in behavior
from the old repo's ``centralia/audit.py`` (`_norm` and helpers). Those rules
are battle-tested against the full corpus: ligatures, spaced letterforms,
hyphen/dash deletion, box-drawing glyphs, footnote-mark glyphs (including
Symbol-font Private Use codepoints), the Hawaiian ʻokina's five spellings, and
the renderer's five XML escapes. Every rule is applied to BOTH sides of a
match, so nothing can hide behind it.

Coverage and correctness gates are added in Phase 2 — they iterate the typed
model via ``sections.iter_text`` instead of sentinel-sniffing dicts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_KNOWN_TAGS = frozenset(
    # 'table'/'tr'/'th'/'td' appear when a footnote carries a printed table;
    # 'centered'/'flushright' are alignment markers — layout, not content.
    ("em", "strong", "u", "mark", "footnotemark", "pagenumber", "sup", "sub",
     "table", "tr", "th", "td", "centered", "flushright")
)


def strip_tags(s: str) -> str:
    """Remove the extractor's inline markup tags ONLY. Literal angle-bracket
    source text ('<the insurer will indemnify ...>' in a quoted policy) is
    content, not markup, and must survive on both sides of the match."""
    out, i = [], 0
    while True:
        j = s.find("<", i)
        if j == -1:
            out.append(s[i:])
            break
        k = s.find(">", j)
        name = ""
        if k != -1:
            # An EMPTY pair of brackets is source text, not markup — a redacted
            # span typed as '<>' or '< >' leaves nothing between them.
            parts = s[j + 1 : k].strip("/").split()
            if parts:
                name = parts[0].split("=")[0].lower()
        if k != -1 and name in _KNOWN_TAGS:
            out.append(s[i:j])
            i = k + 1
        else:
            out.append(s[i : j + 1])
            i = j + 1
    return "".join(out)


def unescape_xml(s: str) -> str:
    """Reverse only the XML escapes the renderer produces. ``html.unescape``
    would also fire on legacy no-semicolon entities inside real source text
    ('TENN.COMP.R.&REGS.' → 'TENN.COMP.R.®S.'), breaking coverage matching.
    '&amp;' is reversed last so escaped-escape sequences don't double-decode."""
    for ent, ch in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                    ("&#39;", "'"), ("&amp;", "&")):
        s = s.replace(ent, ch)
    return s


_LIGATURES = (("ﬀ", "ff"), ("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬃ", "ffi"), ("ﬄ", "ffl"))

# The Hawaiian ʻokina has no single encoding across the corpus: extractors keep
# 'HAWAIʻI' while extract_text reports the same glyph as a SPACE ('HAWAI I'),
# and other files spell it '‘', '#' or the unmapped '(cid:35)'. norm() removes
# whitespace anyway, so deleting the mark makes every spelling converge on
# 'HAWAII' — applied to both sides, it only reconciles the same word with
# itself.
_OKINA = ("(cid:35)", "ʻ", "‘", "ʼ", "`")

# Punctuation that PDF text layers spell inconsistently between the extractor's
# output and extract_text: not significant for coverage matching.
_DASHES = ("-", "—", "–", "―", "‒", "‑")


def _is_box_glyph(c: str) -> bool:
    """Unicode Box Drawing (U+2500–U+257F): courts that draw the caption box
    with glyphs emit these on the text layer; they are layout, never prose."""
    return "─" <= c <= "╿"


def _is_mark_glyph(c: str) -> bool:
    """A footnote MARK glyph — the star family, daggers, section/pilcrow, and
    the Private Use codepoints a Symbol-font asterisk arrives as
    (U+F000–U+F0FF). A note's label is lifted into ``Footnote.label`` and a
    reference is wrapped in <footnotemark>, so the glyph on the source line
    frequently has no counterpart at all in the kept text."""
    return c in "*∗⁎﹡＊†‡§¶" or "\uf000" <= c <= "\uf0ff"


_SPACED_LETTERFORMS = re.compile(r"\b(?:[a-z]-){2,}[a-z]-?", re.IGNORECASE)


def norm(s: str) -> str:
    """Whitespace-removed, tag-stripped, unescaped, ligature-expanded,
    lowercased — one text layer keeps 'Plaintiﬀ' where another says
    'Plaintiff', so both sides expand."""
    s = unescape_xml(strip_tags(s))
    for mark in _OKINA:
        if mark in s:
            s = s.replace(mark, "")
    # A few embedded fonts expose spaced letterforms as ``a-n-y-`` while the
    # page text layer reports ``any``; ordinary compounds are unaffected.
    s = _SPACED_LETTERFORMS.sub(lambda m: m.group(0).replace("-", ""), s)
    # Discretionary hyphenation and the inline-byline em-dash both leave a dash
    # on exactly one side of the match; punctuation, not content.
    for dash in _DASHES:
        if dash in s:
            s = s.replace(dash, "")
    if any(_is_box_glyph(c) for c in s):
        s = "".join(c for c in s if not _is_box_glyph(c))
    if any(_is_mark_glyph(c) for c in s):
        s = "".join(c for c in s if not _is_mark_glyph(c))
    for lig, exp in _LIGATURES:
        if lig in s:
            s = s.replace(lig, exp)
    return "".join(s.split()).lower()


# --------------------------------------------------------------------------
# coverage — every source line lands somewhere
# --------------------------------------------------------------------------
#
# Unlike the old system, coverage consumes the SAME PdfModel the extraction
# read (no second parse with re-applied geometry corrections): ground truth
# and output share one line model by construction.

@dataclass
class AuditResult:
    total: int = 0
    missing: list = field(default_factory=list)     # (page, text) — the failure
    dropped: list = field(default_factory=list)     # matched the Removed box
    furniture: list = field(default_factory=list)   # identified by shape

    @property
    def covered(self) -> int:
        return self.total - len(self.missing)

    @property
    def ok(self) -> bool:
        return not self.missing


def _is_folio_text(text: str) -> bool:
    t = text.strip()
    if t.lower().startswith("page "):
        t = t[5:].strip()
    core = t.strip("-–— ")
    return core.isdigit() and len(core) <= 4


def _is_rule_text(text: str) -> bool:
    bare = (text or "").strip().strip("xX ").strip()
    return len(bare) >= 3 and set(bare) <= set("_-—–=* ")


def coverage(doc, pdf_model) -> AuditResult:
    """Line-coverage proof. Remember: this is the WEAK signal (see
    docs/lessons/coverage-vs-correctness.md) — the correctness gates in the
    harness compare opinion counts and per-section word mass."""
    from .sections import SECTIONS, section_text

    kept = "".join(
        norm(chunk)
        for spec in SECTIONS if spec.audited
        for chunk in section_text(doc, spec)
    )
    dropped_hay = "".join(norm(d.text) for d in doc.dropped)

    result = AuditResult()
    for line in pdf_model.all_lines():
        plain = line.plain
        t = norm(plain)
        if not t:
            continue  # blanks, box glyphs, bare dashes normalize away
        result.total += 1
        if t in kept:
            continue
        if _is_folio_text(plain) or _is_rule_text(plain):
            result.furniture.append((line.page, plain))
            continue
        if t in dropped_hay:
            result.dropped.append((line.page, plain))
            continue
        result.missing.append((line.page, plain))
    return result
