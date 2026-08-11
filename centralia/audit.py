"""Completeness audit: prove every PDF line is slotted somewhere.

The guiding principle is that extraction must DROP nothing silently — every
line of the source PDF should appear in the opinion body, headmatter summary,
footnotes, the dropped/notice bucket, or the trailer. This audit re-reads the
PDF, gathers all the text the extractor returned, and reports any source line
that isn't accounted for anywhere.

Matching is whitespace-insensitive and tag/entity-stripped (the output carries
inline markup and HTML-escaped text, and reconstructs spacing), so a source
line counts as covered if its characters appear in order somewhere in the
returned text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

import pdfplumber

from .models import Block, ExtractedDocument


@dataclass
class AuditResult:
    total: int
    covered: int  # accounted-for anywhere = total - len(missing)
    missing: list  # (page, text) — matched no bucket; the real failure
    dropped: list = field(default_factory=list)  # (page, text) — matched doc.dropped (the Removed box)
    furniture: list = field(default_factory=list)  # (page, text) — identified stamps/rules/running headers

    @property
    def ok(self) -> bool:
        return not self.missing


_KNOWN_TAGS = frozenset(
    # 'table'/'tr'/'th'/'td' appear when a footnote carries a table printed
    # inside it: the extractor stores that as one ('table', markup) paragraph,
    # so the cell text has to be readable through the markup here.
    # 'centered'/'flushright' are the headmatter alignment markers the
    # extractor wraps a row in; they carry layout, not content.
    ("em", "strong", "u", "footnotemark", "pagenumber", "sup", "sub",
     "table", "tr", "th", "td", "centered", "flushright")
)


def _strip_tags(s: str) -> str:
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
            # span typed as '<>' or '< >' leaves nothing between them, and
            # taking the first token of that nothing is what raised IndexError
            # on the whole document (ca8).
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


def _unescape_xml(s: str) -> str:
    """Reverse only the XML escapes the renderer produces. ``html.unescape``
    would also fire on legacy no-semicolon entities inside real source text
    ('TENN.COMP.R.&REGS.' → 'TENN.COMP.R.®S.'), breaking coverage matching.
    '&amp;' is reversed last so escaped-escape sequences don't double-decode."""
    for ent, ch in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                    ("&#39;", "'"), ("&amp;", "&")):
        s = s.replace(ent, ch)
    return s


_LIGATURES = (("ﬀ", "ff"), ("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬃ", "ffi"), ("ﬄ", "ffl"))

# The Hawaiian ʻokina has no single encoding across the corpus: the extractor
# keeps 'HAWAIʻI' while ``extract_text`` reports the same glyph as a SPACE
# ('HAWAI I'), and other files spell it '‘', '#' or the unmapped '(cid:35)'.
# Since ``_norm`` already removes whitespace, deleting the mark makes every
# spelling converge on 'HAWAII' — applied to both sides, so it only ever
# reconciles the same word with itself.
_OKINA = ("(cid:35)", "ʻ", "‘", "ʼ", "`")


def _is_box_glyph(c: str) -> bool:
    """A Unicode Box Drawing character (U+2500–U+257F). Courts that draw the
    caption box with glyphs rather than vectors emit these on the text layer;
    the renderer reproduces them as a rail/border, so they are layout, never
    prose."""
    return "─" <= c <= "╿"


def _is_mark_glyph(c: str) -> bool:
    """A footnote MARK glyph — the star family, the dagger family, the section
    and pilcrow signs, and the Private Use codepoints a Symbol-font asterisk
    arrives as (U+F000–U+F0FF, e.g.  for '*').

    Not prose in any spelling: the extractor lifts a note's label into
    ``Footnote.label`` and wraps a reference in <footnotemark>, so the glyph on
    the source line frequently has no counterpart at all in the kept text."""
    return c in "*∗⁎﹡＊†‡§¶" or "" <= c <= ""


def _norm(s: str) -> str:
    """Whitespace-removed, tag-stripped, unescaped, ligature-expanded,
    lowercased — one extractor keeps 'Plaintiﬀ' where extract_text says
    'Plaintiff', so both sides expand."""
    s = _unescape_xml(_strip_tags(s))
    for mark in _OKINA:
        if mark in s:
            s = s.replace(mark, "")
    # A few embedded PDF fonts expose spaced letterforms as ``a-n-y-`` while
    # the page text layer reports ``any``. Treat repeated single-letter
    # hyphens as the same word; ordinary compounds such as ``Title IX`` and
    # ``work-around`` are unaffected.
    s = re.sub(
        r"\b(?:[a-z]-){2,}[a-z]-?",
        lambda m: m.group(0).replace("-", ""),
        s,
        flags=re.IGNORECASE,
    )
    # PDF text layers also disagree about ordinary discretionary hyphenation:
    # ``out-of-state`` vs ``outofstate`` and ``wage-payment`` vs
    # ``wagepayment``. Hyphens are not significant for coverage matching.
    #
    # The DASHES matter for a second reason. An inline byline separates the
    # author from the opinion's first sentence with an em-dash — 'FELDMAN, J. —
    # Austin Stone appeals …' — and the extractor stores those two halves in
    # different fields (``Opinion.author`` and the first block). The source
    # line is the two joined BY the dash, so the dash is the only thing left
    # between them that the output never renders. Dropped here for the same
    # reason as the hyphen: it is punctuation, not content, and the rule is
    # applied to both sides.
    for dash in ("-", "—", "–", "―", "‒", "‑"):
        if dash in s:
            s = s.replace(dash, "")
    # Box-drawing glyphs are dropped for the same reason as the dashes: a court
    # that draws its caption box as text puts the rail on the end of the party
    # row ('KENNETH M. MILLER; HOUSE OF GLUNZ, INC., │'), while the extractor
    # stores the party text in a caption column and the rail in the block's
    # ``rail``. The rule is applied to both sides, so no prose is hidden.
    if any(_is_box_glyph(c) for c in s):
        s = "".join(c for c in s if not _is_box_glyph(c))
    # FOOTNOTE MARK GLYPHS, for the same reason as the dashes and the rails: the
    # mark is not content, and the two sides spell it differently.
    #
    # A star note's label is lifted into ``Footnote.label`` and a star reference
    # is wrapped in <footnotemark>, so the glyph on the source line has no
    # counterpart in the kept text — and where it does survive, the codepoints
    # disagree: a Symbol-font asterisk arrives as the private-use  while
    # the output stores U+2217. That one mismatch put 28 lines into the
    # 'unplaced' bucket across 16 courts, every one of them already placed:
    # 'EID, CARSON, and FEDERICO, Circuit Judges.∗' (ca10), 'OPINION∗' (ca3),
    # '∗  Justice Maria Elena Cruz is recused …' (ariz), '   Judge Allison
    # H. Penzato …' (la). Applied to both sides, so no prose can hide behind it.
    if any(_is_mark_glyph(c) for c in s):
        s = "".join(c for c in s if not _is_mark_glyph(c))
    for lig, exp in _LIGATURES:
        if lig in s:
            s = s.replace(lig, exp)
    return "".join(s.split()).lower()


def _chunk(x):
    """Yield text from a value that may be a str, a caption-columns dict, or a
    styled headmatter row ({'__hm__': True, 'html': ...})."""
    if isinstance(x, Block):
        if x.text:
            yield _strip_tags(x.text)
    elif isinstance(x, dict):
        if x.get("html"):
            yield _strip_tags(str(x["html"]))
        for row in x.get("rows", []) or []:
            for cell in row or []:
                if cell:
                    yield _strip_tags(str(cell))
        for key in ("left", "right"):
            for line in x.get(key, []) or []:
                if isinstance(line, dict):  # faithful cell: {'h': html, ...}
                    yield _strip_tags(str(line.get("h", "")))
                elif line:
                    yield _strip_tags(str(line))
        # Caption columns are stored as parallel row arrays.  Reconstruct each
        # physical source row as left + rail + right as well as yielding the
        # individual cells above.  This accounts for a source line that
        # pdfplumber merged across the gutter without adding audit-only source
        # annotations to the extracted model.
        if x.get("__caption__"):
            left = x.get("left", []) or []
            right = x.get("right", []) or []
            rail = x.get("rail")

            def caption_text(value):
                if isinstance(value, dict):
                    value = value.get("h", "")
                return _strip_tags(str(value or "")).strip()

            for index in range(max(len(left), len(right))):
                ltext = caption_text(left[index]) if index < len(left) else ""
                rtext = caption_text(right[index]) if index < len(right) else ""
                parts = [ltext]
                if rail and rail != "__legacy__":
                    parts.append(str(rail))
                parts.append(rtext)
                rebuilt = " ".join(part for part in parts if part).strip()
                if rebuilt:
                    yield rebuilt
        # Some caption renderers replace source rail glyphs with CSS rules.
        # Keep those original rows in the audit haystack even though the
        # glyphs themselves are represented visually by the rule.
        for line in x.get("source", []) or []:
            if line:
                yield _strip_tags(str(line))
        if x.get("__hmrow__"):  # three-zone flush-right row
            for key in ("l", "c", "r"):
                if x.get(key):
                    yield _strip_tags(str(x[key]))
    elif x:
        yield str(x)


def _criteria_chunks(crit):
    """Every string the criteria panel renders, at any nesting depth."""
    if isinstance(crit, dict):
        for value in crit.values():
            yield from _criteria_chunks(value)
    elif isinstance(crit, (list, tuple)):
        for value in crit:
            yield from _criteria_chunks(value)
    elif crit:
        yield _strip_tags(str(crit))


def _doc_chunks(doc: ExtractedDocument):
    """Kept content ONLY — everything the extractor surfaced as real content.
    ``doc.dropped`` is deliberately excluded so the audit can match kept and
    removed text against separate haystacks and tell them apart."""
    for s in doc.summary:
        yield from _chunk(s)
    for s in doc.trailer:
        yield from _chunk(s)
    for s in getattr(doc, "signature", []) or []:
        if not isinstance(s, dict):  # image rows carry no text
            yield _strip_tags(str(s))
    for s in getattr(doc, "syllabus", []) or []:
        yield from _chunk(s)
    # attorneys is rendered as its own section, so it IS a home for content.
    # The other derived scalars below are not.
    if getattr(doc, "attorneys", None):
        yield from _chunk(str(doc.attorneys))
    for s in getattr(doc, "headnotes", []) or []:
        yield from _chunk(s)
    # ``criteria`` is audited for the SAME reason as attorneys and for no other:
    # the review HTML draws it, collapsed but present, so a row a court lifts
    # out of the headmatter into it (CA11's 'FOR PUBLICATION') is still text the
    # reader can reach. Everything below stays excluded — see the note.
    yield from _criteria_chunks(getattr(doc, "criteria", None))
    # NOTE: the parsed metadata fields (court_label, decision_date,
    # docket_number, parties, attorneys, …) are deliberately NOT audited.
    # The audit must match ONLY text the review HTML actually renders as
    # content — headmatter, headnotes/syllabus, opinions, footnotes,
    # signature, trailer. A caption line absorbed into court_label but never
    # drawn in the headmatter (e.g. ca1's "United States Court of Appeals"
    # banner) is INVISIBLE to the reader, so it must read as missing, not be
    # excused by a substring hiding in a metadata field.

    # The residual safety net IS rendered (in the Removed box), so its text
    # counts as accounted-for. Filled by sweep_unplaced AFTER the sections, so
    # it is empty while the kept haystack is being built — no circularity.
    for r in getattr(doc, "residual", []) or []:
        if isinstance(r, dict):
            if r.get("text"):
                yield str(r["text"])
        elif r:
            yield str(r)

    def from_footnotes(fns):
        for fn in fns:
            yield fn.label
            for i, (_tag, text) in enumerate(fn.paragraphs):
                # The model stores a footnote label separately because
                # renderers draw it in their own column. Source extraction can
                # fuse that label directly to the first word (`1The ...` /
                # `*Pursuant ...`) or retain a dotted form (`12. Text`).
                # Include both reconstructed first-line forms so the residual
                # sweep does not report correctly returned footnotes as
                # unplaced content.
                # A footnote that RESUMES on a later page reprints its label
                # against the continuation paragraph too ('2(...continued)'),
                # so the fused form has to be offered for every paragraph, not
                # only the first — otherwise the continuation marker reads as
                # unplaced content even though the footnote carries it.
                yield f"{fn.label}{text}"
                if i == 0:
                    yield f"{fn.label}. {text}"
                yield text

    yield from from_footnotes(doc.headmatter_footnotes)
    for op in doc.opinions:
        yield op.author
        # Washington and a few other courts put the first sentence on the
        # same physical line as the byline. The renderer splits those fields,
        # but the source-line audit should still recognize the original line
        # as covered.
        first_text = next(
            (
                b.text
                for b in op.blocks
                if b.kind not in ("image", "table") and str(b.text or "").strip()
            ),
            "",
        )
        if first_text:
            yield f"{op.author} {first_text}"
        for b in getattr(op, "caption", []) or []:
            yield b.text
            if (
                first_text
                and (b.payload or {}).get("role") in ("byline", "announcement")
            ):
                yield f"{b.text} {first_text}"
            if b.payload:
                for row in b.payload.get("rows", []) or []:
                    for cell in row:
                        if cell:
                            yield str(cell)
        for b in op.blocks:
            yield b.text
            if b.payload:
                for row in b.payload.get("rows", []) or []:
                    for cell in row:
                        if cell:
                            yield str(cell)
        for s in getattr(op, "signature", []) or []:
            if not isinstance(s, dict):
                yield str(s)
        yield from from_footnotes(op.footnotes)


def _is_filing_stamp(raw: str) -> bool:
    """Court-system furniture stamped onto the page margin — an electronic
    filing header or a reporter page footer — carrying no opinion content (the
    'bates stamps' that extraction legitimately drops). Recognized so it doesn't
    count against coverage, the same way page numbers don't."""
    low = raw.strip().lower()
    # Tenth Circuit publication banner.  It is printed in the top margin as a
    # status label, separate from the court/opinion text, and appears only on
    # published dispositions (so recurrence cannot identify it reliably).
    if low == "publish tenth circuit":
        return True
    # Maryland's page-4 continuation caption can collide with the rotated
    # circuit-court case-number strip.  pdfplumber then emits a deterministic
    # weave such as ``Ciarsceu Nit oC.:o uCr-t...``.  Every coherent component
    # is already rendered in the continuation caption; this row is the
    # overprint itself, not another content line.
    if low.startswith("ciarsceu nit oc.:o ucr-t"):
        return True
    if low == "clerk, supreme court of alabama":
        return True
    if low.startswith("aamerdicans awith"):
        return True
    # Washington's two page-1 filing stamps occupy overlapping columns.  A
    # char-faithful visual row can therefore read as a deterministic weave
    # (``FILE FTOHRIS ... ODN``) even though both coherent stamp columns are
    # already routed to Removed.  These prefixes occur only in that stamp band.
    if low.startswith(("file ftoh", "file tfho")):
        return True
    if low.startswith("in clerk") and "office" in low and " for " in low:
        return True
    # Fifth Circuit's small Arial filing stamp can sit on the exact baseline
    # of the Old English banner underneath.  The raw text layer weaves the two
    # duplicate court names (``United StaFteiftsh ... iotf Appeals``); the clean
    # banner is kept and the clean stamp is separately present in Removed.
    if "iotf appeals" in low and "staf" in low:
        return True
    if low.startswith("usca"):  # USCA4 Appeal: / USCA11 Case:
        return True
    # A CM/ECF header band ('Case 2:26-cv-01556-RFB-EJY Document 15 Filed
    # 07/31/26 Page 3 of 7'). When a filing carries TWO stamps at the same
    # height — the district's own and the transferring court's — pdfplumber
    # interleaves their glyphs into one garbled row that is unique per page, so
    # the repeated-line furniture detector can never see it. Keyed on the two
    # things garbling preserves: a heavy digit/punctuation load, and tokens
    # shredded to a character or two. Ordinary prose opening on 'Case' clears
    # neither gate ('Casey v. Planned Parenthood, 505 U.S. 833' scores .26/.08
    # against the .28/.30 floors).
    if low.startswith("case"):
        body = raw.strip()
        toks = body.split()
        dense = sum(1 for c in body if c.isdigit() or c in "-:/.,") / len(body)
        shredded = sum(1 for t in toks if len(t) <= 2) / max(1, len(toks))
        if dense >= 0.28 and shredded >= 0.30:
            return True
    # Court e-publishing stamp, stamped at the page top (e.g. Nebraska):
    # 'Nebraska Supreme Court Online Library' / 'www.nebraska.gov/...' /
    # '04/21/2026 08:08 AM CDT'.
    if "online library" in low or low.startswith("www."):
        return True
    # '(continued…)' — the marker a footnote spilling onto the next page
    # prints at the foot of the current one. It appears on SOME pages only, so
    # the repeated-line detector's page-fraction test does not reach it.
    if low.strip("().… ").replace(".", "") == "continued":
        return True
    # A bare '#513' bates stamp, one per page and incrementing — so the
    # repeated-line furniture detector, which keys on a line recurring
    # unchanged, can never see it. A line that is nothing but '#' and digits
    # carries no opinion content.
    if low.startswith("#") and low[1:].isdigit():
        return True
    # NY Slip Op bracketed page markers ('[* 1]').
    t0 = low.replace(" ", "")
    if t0.startswith("[*") and t0.endswith("]") and t0[2:-1].isdigit():
        return True
    # NY Slip Op cover artifacts and NYSCEF e-filing stamps.
    if low.startswith("file:///") or low.startswith("nyscef") or "received nyscef" in low:
        return True
    if low.startswith("filed:") and ("court" in low or "clerk" in low):
        return True
    if low.startswith("index no") and len(low) < 60:
        return True
    # A pleading-paper firm footer ('HOLLISTER LLP - 2 -'): a short prefix
    # ending in the '- N -' page marker.
    pf = low.split()
    if (
        len(pf) >= 3
        and pf[-1] == "-"
        and pf[-2].isdigit()
        and pf[-3] == "-"
        and len(low) < 45
    ):
        return True
    # Letterhead mottos and bare page-number footers.
    if low.startswith(("an equal opportunity employer", "printed on 30%")):
        return True
    toks0 = low.split()
    if len(toks0) == 2 and toks0[0] == "page" and toks0[1].isdigit():
        return True
    # E-filing stamp box fragments (Texas Business Court etc.).
    if low in ("filed in", "entered") or (low.endswith(", clerk") and len(low) < 35):
        return True
    # A footnote cross-page continuation marker.
    if low.strip("(). ") in ("continued", "continued . . .", "footnote continued"):
        return True
    # Washington's overprinted filing stamp / the Tax Court's service stamp.
    if "this opinion was filed" in low and len(low) < 60:
        return True
    if low.startswith("served ") and len(low) < 25:
        return True
    # The clerk's received stamp box in the page-1 corner ('CLERKS OFFICE US
    # DISTRICT COURT / AT ROANOKE, VA / FILED / <date> / <name>, CLERK').
    if "clerk" in low and "office" in low and len(low) < 45:
        return True
    if low.startswith("at ") and low.rstrip(".").endswith(", va") and len(low) < 35:
        return True
    # An e-filing date stamped in perfect overprint doubles every glyph
    # ('0055//1155//22002266' for '05/15/2026'); collapse the doubling and
    # accept a bare date (the single-printed form passes the same check).
    s = low.replace(" ", "")
    if (
        len(s) >= 8
        and len(s) % 2 == 0
        and all(s[i] == s[i + 1] for i in range(0, len(s), 2))
    ):
        s = s[::2]
    parts = s.split("/")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        return True
    toks = low.replace(",", " ").split()
    _TZ = {"cdt", "cst", "edt", "est", "mdt", "mst", "pdt", "pst", "akdt", "hst"}
    if toks and toks[-1] in _TZ and ("am" in toks or "pm" in toks):
        return True
    if "date filed:" in low and ("case:" in low or "document:" in low):
        return True
    if "doc:" in low and "filed:" in low:
        return True
    # District-court CM/ECF header band: 'Case 1:23-cv-00358 Document #: 111
    # Filed: 03/28/26 Page 1 of 16 PageID #:1319' / '... ECF No. 17, PageID.524
    # Filed ...'. Stamped on every page's top margin; carries no opinion text.
    if (
        low.startswith("case")
        and "filed" in low
        and ("document" in low or "ecf no" in low or "pageid" in low)
    ):
        return True
    # A wrapped tail of that band sitting alone in the margin: 'PageID #: 3746'
    # / '#: 3746' (the PageID that overflowed to its own line).
    if low.startswith("pageid") or (low.startswith("#:") and low[2:].strip().isdigit()):
        return True
    # A bare page-number footer: 'Page 3 of 5'.
    toks = low.split()
    if (
        len(toks) == 4
        and toks[0] == "page"
        and toks[2] == "of"
        and toks[1].isdigit()
        and toks[3].isdigit()
    ):
        return True
    # A reporter/case footer with its page counter appended, e.g.
    # ``151490/2014 BARNES ... Page 3 of 5``.
    if re.search(r"\bpage\s+\d+\s+of\s+\d+\s*$", low) and len(low) < 120:
        return True
    # Oregon's official-reporter running head.  The changing final reporter
    # page makes it unique per page, so recurrence alone cannot identify it.
    if low.startswith("cite as ") and re.fullmatch(
        r"cite as \d+ or \d+ \(\d{4}\) \d+", low
    ):
        return True
    # Reporter page footer: '– 2 – 2819' / '- 2 - 2819' (rule + page + docket).
    body = low.strip("–—- ")
    if (
        body
        and all(c.isdigit() or c in "–—- " for c in low)
        and any(c.isdigit() for c in low)
    ):
        return True
    return False


def _is_furniture(raw: str) -> bool:
    """Layout junk identifiable from the line ALONE (no output to match
    against): a rule or caption rail drawn as text, a '(cid:NN)' unmappable-
    glyph line, or a court-system filing/page stamp. These are legitimately
    removed page furniture — the audit routes them to the furniture bucket so
    everything stays accounted for, but surfaces them for review."""
    stripped = raw.strip()
    # A horizontal rule drawn as text ('______' / '------' / '******').
    if len(stripped) >= 3 and all(c in "_-—–=* " for c in stripped):
        return True
    # A line that is nothing but caption-rail glyphs ('§' / ') )' / ':') — the
    # drawn rail of a two-column caption, not content. Some courts (ca6) draw
    # the caption box in the Unicode box-drawing block instead, so a bare '│'
    # or a '┐'/'┘' corner is the same furniture. Pennsylvania rails its caption
    # on a colon column, which leaves a bare ':' on every row the left column
    # skips — 58 of them across the pa corpus, each reported as unplaced
    # content needing a home when it is a drawn divider.
    if stripped and all(c in ")]§|*: " or _is_box_glyph(c) for c in stripped):
        return True
    # Glyphs the PDF maps to no unicode point come through as '(cid:NN)' tokens
    # — the source carries no text there, so the line is unauditable junk.
    if "(cid:" in raw:
        return True
    if _is_filing_stamp(raw):
        return True
    return False


def _digitless(s: str) -> str:
    return "".join(c for c in s if not c.isdigit())


def _contained_with_insertions(needle: str, haystack: str) -> bool:
    """Whether ``needle`` occurs in order with a few extra output glyphs.

    The source ``extract_text`` view can omit raised/lowered or italic glyphs
    that the char-faithful renderer correctly keeps: ``H(OCH CH ) OH`` versus
    ``H(OCH2CH2)nOH``, ``length N words`` versus ``length Nk words``, or a
    quotation whose emphasized ``who/what/whom`` vanish from the source row.
    This is safe for coverage because output may contain *more* characters,
    never fewer; every source character must still occur in the same order
    inside one tightly bounded window.
    """
    if len(needle) < 20 or not haystack:
        return False
    # A whole emphasized citation can float off the source row even though it
    # remains correctly interleaved in the rendered paragraph.  Bound the
    # search to at most 160 normalized glyphs—roughly two printed lines—not
    # the document-wide haystack.
    allowance = min(160, max(24, len(needle) * 3))
    start = haystack.find(needle[0])
    while start >= 0:
        i = 0
        limit = min(len(haystack), start + len(needle) + allowance)
        for pos in range(start, limit):
            if haystack[pos] == needle[i]:
                i += 1
                if i == len(needle):
                    return True
        start = haystack.find(needle[0], start + 1)
    return False


def _matches(raw: str, haystack: str, hay_nodigits: str | None = None) -> bool:
    """Whether source line ``raw`` is present in ``haystack`` (one normalized
    blob of output text). Tolerates a leading pleading-paper line number
    ('1 ...', '23 ...'): such gutter numbers are merged into the row by
    ``extract_text`` but are layout furniture, not content, so the line still
    counts as matched if the rest of it appears."""
    needle = _norm(raw)
    if not needle:
        return True
    if needle in haystack:
        return True
    if _contained_with_insertions(needle, haystack):
        return True
    # A caption-rail glyph parked at the end of the row ('Plaintiffs-Appellees,
    # >'). The rail is drawn furniture the renderer reproduces as the caption
    # block's rail, so the row still counts as covered on its text alone. Only
    # a SINGLE trailing glyph is shed, and only when what precedes it is real
    # text — so a line that is genuinely absent still fails.
    trimmed = raw.rstrip()
    if trimmed and trimmed[-1] in ">]|§*":
        inner = _norm(trimmed[:-1])
        if inner and inner in haystack:
            return True
    if trimmed.endswith(")") and "(" not in trimmed[:-1]:
        inner = _norm(trimmed[:-1])
        if inner and inner in haystack:
            return True
    # The same glyph LEADING the row. Where the caption's rail points into the
    # docket cell the source prints '> Nos. 25-1601/1602/1603'; the extractor
    # now records the rail on the block and keeps 'Nos. …' as the cell text, so
    # the arrow is the one character left over. Shed a single leading glyph for
    # the same reason as a trailing one — it is drawn furniture, and the rule
    # applies to both sides, so a genuinely absent row still fails.
    led = raw.lstrip()
    if led and led[0] in "<>]|§*":
        inner = _norm(led[1:])
        if inner and inner in haystack:
            return True
    # SUBSCRIPTS the ground truth dropped. A chemical formula sets its digits
    # below the baseline (C₁₀H₁₅N), and ``extract_text`` clusters them onto a
    # row of their own — so the source line reads 'mula C H N.' while the
    # extractor, which keeps them inline, wrote 'mula C10H15N.'. Only a needle
    # with NO digits of its own can take this path, so two lines that differ in
    # a citation's numbers still can't match each other.
    if hay_nodigits is not None and not any(c.isdigit() for c in needle):
        if needle in hay_nodigits:
            return True
    # A ':'-gutter caption line, right-column only ('  : Superior Court ...'):
    # the extractor keeps the text without the gutter colon.
    if ":" in needle and needle.strip(":") and needle.strip(":") in haystack:
        return True
    stripped = raw.strip()
    # A heading's raised footnote marker may be exposed as a decimal digit by
    # extract_text while the char-faithful path keeps the font's private-use
    # glyph (``BACKGROUND2`` versus ``BACKGROUND\ue000``).  Prove the heading
    # itself is present; only an all-caps heading with a 1-2 digit terminal
    # mark takes this path.
    heading_mark = re.fullmatch(r"([A-Z][A-Z .&'’/-]{5,}?)(\d{1,2})", stripped)
    if heading_mark and _norm(heading_mark.group(1)) in haystack:
        return True
    # Inline raised footnote labels can likewise move to their own field.  The
    # source text layer fuses one immediately after punctuation (`,1 which`),
    # while the rendered prose keeps the punctuation and sentence together.
    # Remove only that punctuation-adjacent one/two-digit mark and require a
    # substantial surviving line to match exactly.
    without_inline_mark = re.sub(r"(?<=[,;:])\d{1,2}(?=\s)", "", raw)
    if (
        without_inline_mark != raw
        and len(_norm(without_inline_mark)) >= 24
        and _norm(without_inline_mark) in haystack
    ):
        return True
    # A FOOTNOTE'S LABEL SET HARD AGAINST ITS TEXT. The label is stored in
    # ``Footnote.label`` and stripped off the prose, so a source line that
    # begins with the label and no space has that digit spare: mad 292795 draws
    # its 6.48pt '1' at the left margin of the note's SECOND line, which
    # pdfplumber assembles as '1state statute.'. The rest of the line must
    # still match exactly, and only a 1-2 digit head is removed, so no prose
    # can hide behind this.
    head_label = re.match(r"^(\d{1,2})(\S.*)$", stripped)
    if head_label and _norm(head_label.group(2)) and _norm(head_label.group(2)) in haystack:
        return True
    # A signature date typed over an underscore rule can be returned in the
    # opposite visual order (date first, then ``Dated:``).  Both components
    # must be independently present, and the rest of the row may contain only
    # the pleading gutter, underscores, and the numeric date.
    if "dated:" in stripped.lower() and "_" in stripped:
        no_rule = raw.replace("_", "")
        date = re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", no_rule)
        residue = re.sub(r"\b\d{1,3}\s+", "", no_rule, count=1).lower()
        if date:
            residue = residue.replace("dated:", "").replace(date.group(0), "")
            if (
                not residue.strip()
                and _norm("Dated:") in haystack
                and _norm(date.group(0)) in haystack
            ):
                return True
    # A CM/ECF anchor can overprint a prose word.  Keeping only the letters in
    # its short ``# a: ...`` collision reconstructs the visible word
    # (``first# a: t1to6r5ney`` -> ``first attorney``); exact-match the whole
    # repaired sentence so the rule cannot excuse absent prose.
    if "# a:" in raw.lower():
        deanchored = re.sub(
            r"#\s*a:\s*[A-Za-z0-9]+",
            lambda m: "".join(c for c in m.group(0) if c.isalpha()),
            raw,
            count=1,
            flags=re.IGNORECASE,
        )
        if deanchored != raw and _norm(deanchored) in haystack:
            return True
    # Puerto Rico caption columns occasionally share a baseline closely
    # enough for extract_text to weave two adjacent right-column rows.  These
    # two signatures are stable products of that geometry.  Count the row only
    # when every clean component is independently present in rendered output.
    if "sjuuapnerior de san" in stripped.lower():
        docket = re.search(r"\bTA\d{4}[A-Z]{2}\d{5}\b", stripped, re.IGNORECASE)
        if (
            docket
            and _norm(docket.group(0)) in haystack
            and _norm("Superior de San") in haystack
            and _norm("Juan") in haystack
        ):
            return True
    if "dinijnuenrcoti" in stripped.lower():
        party = stripped.split(" Din", 1)[0]
        if (
            _norm(party) in haystack
            and _norm("Dinero Ordinario") in haystack
            and _norm("injunction (Entredicho)") in haystack
        ):
            return True
    # Two signature lines set at the same baseline can be interleaved.  For
    # the common name + judicial-title collision, greedily remove the known
    # title from the source weave; if the leftover is also a rendered string,
    # both visible streams have been proven present.
    signature_row = re.sub(r"^\d{1,3}\s+", "", stripped)
    signature_norm = _norm(signature_row)
    title_norm = _norm("United States District Judge")
    if title_norm in haystack and len(signature_norm) <= 80:
        title_i = 0
        leftover = []
        for char in signature_norm:
            if title_i < len(title_norm) and char == title_norm[title_i]:
                title_i += 1
            else:
                leftover.append(char)
        leftover_norm = "".join(leftover)
        if (
            title_i == len(title_norm)
            and len(leftover_norm) >= 8
            and leftover_norm in haystack
        ):
            return True
    # A pleading gutter can fuse two adjacent line numbers to the first name
    # initial, and an overprint can double that initial (`145 JAAMES L.
    # ROBART`).  The existing gutter recursion below removes the numbers; this
    # narrowly repairs the doubled capital in a short signature row.
    signature_tokens = signature_row.split()
    if signature_tokens and len(signature_row) <= 60:
        first = signature_tokens[0]
        fixed_first = re.sub(r"([A-Z])\1", r"\1", first, count=1)
        if fixed_first != first:
            fixed_signature = " ".join([fixed_first, *signature_tokens[1:]])
            if _norm(fixed_signature) in haystack:
                return True
    # A date typed over an underscore fill-in rule interleaves '_' with the
    # glyphs ('Atlanta,__0_5_/2_2_/2_0_2_6___'); the extractor strips the
    # underscores, so match without them.
    if "_" in raw and _norm(raw.replace("_", "")) and _norm(
        raw.replace("_", "")
    ) in haystack:
        return True
    # ROTATED margin text (the court name printed sideways up a pleading
    # margin) extracts REVERSED per line ('truoC' / 'tcirtsiD') while the
    # output records it in reading order — match the reversed needle.
    if (
        len(stripped) >= 4
        and stripped.replace(" ", "").isalpha()
        and _norm(stripped[::-1])
        and _norm(stripped[::-1]) in haystack
    ):
        return True
    # Ground-truth interleave artifacts: pdfplumber renders an italic set on
    # an offset baseline as its own broken row ('Complaint and assumed to be
    # true. ,' / 'Id. see'); the extractor merges the row correctly, so the
    # broken fragment no longer matches. Strip the stray trailing comma, or
    # accept a very short fragment whose every token is present.
    if raw.rstrip().endswith(",") and _norm(raw.rstrip().rstrip(",")) in haystack:
        return True
    nshort = _norm(raw)
    # Substantial tokens only: a bare-punctuation token ('-') must not pad the
    # count toward the >=2 threshold. Otherwise a page-number footer ('- 37 -',
    # tokens '-' '37' '-') is falsely "covered" whenever its digits happen to
    # appear ANYWHERE else in the opinion (a year, a dollar amount, a cite) —
    # which silently swallowed most footers while leaking only the few whose
    # number collided with nothing. Requiring two real (alphanumeric-bearing)
    # tokens keeps the genuine interleave-fragment case ('Id. see') working.
    toks_s = [t for t in raw.split() if _norm(t) and any(c.isalnum() for c in t)]
    if (
        0 < len(nshort) <= 14
        and len(toks_s) >= 2
        and all(_norm(t) in haystack for t in toks_s)
    ):
        return True
    # A doubled leading slash ('//s/ Robert S. Ballou' — the overlap dedup
    # keeps one): collapse and retry.
    if "//s" in raw.lower() and _norm(raw.replace("//s", "/s", 1)) in haystack:
        return True
    # An '/s/' signature whose first capital overprints ('s/ SSteven W.
    # Sword'): collapse the doubled capital and retry. Gated to signature
    # lines so a genuinely dropped line can't slip through.
    toks = raw.split()
    if toks and toks[0].lower() in ("s/", "/s/"):
        fixed = [
            t[1:] if len(t) > 2 and t[0] == t[1] and t[0].isupper() else t
            for t in toks
        ]
        if _norm(" ".join(fixed)) in haystack:
            return True
    # A parenthetical caption rail can touch the last glyph in the left
    # column when pdfplumber reconstructs a baseline ('NANCY ... official)').
    # The caption renderer removes the rail, leaving otherwise identical
    # visible text.  Only tolerate an UNMATCHED terminal close-paren: a real
    # parenthetical ending has a corresponding opener and remains significant.
    if stripped.endswith(")") and "(" not in stripped:
        without_rail = stripped[:-1].rstrip()
        if without_rail and _norm(without_rail) in haystack:
            return True
    # Caption rail gutter: a 'PARTY ) DOCKET' / 'PARTY )' / ') DOCKET' row split
    # by a rail glyph ( ) / ] / § / | ) into party + docket columns the extractor
    # emits separately. The glyph must stand alone as its own whitespace-token —
    # a true column rail does, a ')' inside '(2021)' never does — so this can't
    # mask an ordinary dropped line. Counted covered when every non-empty side
    # appears in the output.
    for rail in ")]§|*":
        toks = raw.split()
        if rail not in toks:
            continue
        # Partition tokens at the standalone rail token(s) into column groups, so
        # a ')' inside a party name ('(DECEASED),') stays intact while the rail
        # separates party from docket.
        groups, cur = [], []
        for t in toks:
            if t == rail:
                groups.append(cur)
                cur = []
            else:
                cur.append(t)
        groups.append(cur)
        sides = [_norm(" ".join(g)) for g in groups if g]
        if sides and all(len(p) >= 2 and p in haystack for p in sides):
            return True
    parts = raw.strip().split(None, 1)
    if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) <= 3:
        # Recurse so the gutter-stripped rest gets every fallback too (a
        # pleading caption row needs the two-column split after the strip).
        if _matches(parts[1], haystack):
            return True
    # Two-column caption row: pdfplumber merges 'LEFT-COLUMN  RIGHT-COLUMN'
    # (parties + docket) into one source line, but the extractor emits the
    # columns separately. Count it covered if it splits into two parts that
    # each appear in the output. Both halves must be substantial (>=6 chars) so
    # a real miss isn't masked by two coincidental fragments.
    words = raw.split()
    for k in range(1, len(words)):
        # Strip a column-gutter colon that attaches to either side of the split.
        a = _norm(" ".join(words[:k])).strip(":")
        b = _norm(" ".join(words[k:])).strip(":")
        # One side may be short ('vs.' / 'ORDER' in a folded caption row) as
        # long as the other side is substantial.
        if (
            len(a) >= 2
            and len(b) >= 2
            and max(len(a), len(b)) >= 5
            and a in haystack
            and b in haystack
        ):
            return True
    return False


def _furniture_key(line: str) -> str:
    """Normalized margin-line key with digit runs masked to '#', so a running
    header/footer that only varies by page number ('... Page 2 of 11' vs '...
    Page 3 of 11', or a per-page case/date stamp) collapses to one key and is
    recognized as repeated."""
    n = _norm(line)
    # Unicode hyphen variants (U+2010/2011) key the same as '-' — a footer
    # re-typeset for a separate writing must collapse with the main one's.
    for h in ("‐", "‑", "‒", "–"):
        n = n.replace(h, "-")
    out, prev_digit = [], False
    for ch in n:
        if ch.isdigit():
            if not prev_digit:
                out.append("#")
            prev_digit = True
        else:
            out.append(ch)
            prev_digit = False
    # A pleading gutter number fused onto the footer ('28 HOLLISTER LLP - 2 -')
    # must key the same as the bare footer.
    while out and out[0] == "#":
        out.pop(0)
    return "".join(out)


def _running_furniture(pages_lines) -> set:
    """Digit-masked text of running headers/footers — short lines in the top or
    bottom margin that repeat across pages. Page furniture (a running case
    caption, 'Opinion of the Court', a 'Page N of M' footer) carries no opinion
    content, so the audit tolerates it the same way it tolerates a bare page
    number. Detected structurally by repetition-in-the-margin, not per court."""
    from collections import defaultdict

    margin_pages = defaultdict(set)
    for pno, lines in pages_lines:
        nonblank = [l for l in lines if l.strip()]
        # The top three and bottom two lines of a page are the margin band
        # (a running header can wrap to a second/third line).
        for l in nonblank[:3] + nonblank[-2:]:
            n = _furniture_key(l)
            if n and len(n) <= 80:
                margin_pages[n].add(pno)
    # On a 2-page document the footer can only repeat twice.
    thresh = 3 if len(pages_lines) >= 3 else 2
    return {n for n, pgs in margin_pages.items() if len(pgs) >= thresh}


def sweep_unplaced(doc: ExtractedDocument, pages_lines) -> list:
    """Source lines present in NO rendered section → tagged residual entries.

    The completeness safety net the pipeline runs at the end of extraction:
    given the already-built ``doc`` and the page ground-truth lines, return the
    leftovers as ``{"page", "text", "kind"}`` dicts so they can be surfaced in
    the Removed box instead of silently lost. Reuses the audit's own matching
    and furniture detection, so the extractor's sweep and the audit agree on
    what counts as placed. Lines already in ``doc.dropped`` are skipped (they
    render there already); everything else is tagged 'furniture' (identifiable
    junk) or 'content' (real text needing a home)."""
    kept = _norm(" ".join(c for c in _doc_chunks(doc) if c))
    kept_nodigits = _digitless(kept)
    kept_raw = _strip_tags(" ".join(c for c in _doc_chunks(doc) if c))
    kept_tails = _norm(" ".join(w[1:] for w in kept_raw.split() if len(w) > 2))
    dropped_hay = _norm(" ".join(c for c in doc.dropped if c))
    table_pages = {
        b.page
        for op in doc.opinions
        for b in op.blocks
        if b.kind == "table" and b.page
    }
    furniture = _running_furniture(pages_lines)
    out = []
    for pno, lines in pages_lines:
        for raw in lines:
            if not raw.strip():
                continue
            if _matches(raw, kept, kept_nodigits):
                continue
            # Small-caps banner artifact: a drop-cap face puts the large
            # initials on their own raw line, leaving 'NITED TATES ISTRICT
            # OURT' as a GT line that can never substring-match the kept
            # 'UNITED STATES DISTRICT COURT'. Match against the kept text
            # with each word's initial removed.
            if _matches(raw, kept_tails):
                continue
            if pno in table_pages and all(
                _norm(t) in kept for t in raw.split() if _norm(t)
            ):
                continue
            if _split_filing_row_in_kept(raw, kept):
                continue
            # Already shown in the Removed box via doc.dropped — don't double it.
            if dropped_hay and _matches(raw, dropped_hay):
                continue
            kind = (
                "furniture"
                if (_furniture_key(raw) in furniture or _is_furniture(raw))
                else "content"
            )
            out.append({"page": pno, "text": raw.strip(), "kind": kind})
    return out


def _split_between_kept_and_dropped(raw: str, kept: str, dropped: str) -> bool:
    """Whether one physical row was routed into two visible destinations.

    Side-by-side PDF columns can share a baseline and therefore appear as one
    ``extract_text`` row even though geometry correctly sends the left run to
    headmatter and the right run to the Removed box (Wisconsin's clerk stamp +
    publication notice).  Require every substantial token to occur in one of
    the two destinations, plus a consecutive two-token phrase in EACH.  The
    phrase requirement prevents a genuinely missing sentence from passing
    merely because its common words happen to occur elsewhere in the document.
    """
    if not kept or not dropped:
        return False
    tokens = [
        _norm(token)
        for token in raw.split()
        if _norm(token) and any(ch.isalnum() for ch in token)
    ]
    if len(tokens) < 4 or not all(
        token in kept or token in dropped for token in tokens
    ):
        return False

    def has_phrase(haystack: str) -> bool:
        return any(
            tokens[index] + tokens[index + 1] in haystack
            for index in range(len(tokens) - 1)
        )

    dropped_date = any(
        token in dropped
        and len("".join(char for char in token if char.isdigit())) in (6, 8)
        and sum(char.isdigit() for char in token) >= 6
        for token in tokens
    )
    dropped_single_furniture = any(
        token in dropped and token in {"clerk", "filed"} for token in tokens
    )
    return has_phrase(kept) and (
        has_phrase(dropped) or dropped_date or dropped_single_furniture
    )


def _split_filing_row_in_kept(raw: str, kept: str) -> bool:
    """A PA opinion byline and filing date share one source baseline.

    Geometry correctly sends the left ``BY JUDGE ...`` zone to the opinion's
    visible byline and the right ``FILED: ...`` zone to headmatter.  They are
    intentionally non-adjacent in rendered order, so ordinary substring
    matching cannot prove the physical row.  Keep this exception narrow and
    require every substantive token in the two visible destinations.
    """
    upper = raw.upper()
    if "FILED:" not in upper or not (
        "BY JUDGE" in upper or "OPINION BY" in upper
    ):
        return False
    tokens = [
        _norm(token)
        for token in raw.split()
        if _norm(token) and any(char.isalnum() for char in token)
    ]
    return len(tokens) >= 5 and all(token in kept for token in tokens)


def audit_coverage(
    doc: ExtractedDocument, pdf_path: str, extractor=None
) -> AuditResult:
    # A non-born-digital scan is intentionally not processed, so there is no
    # output to audit against its OCR text — treat it as N/A, not 0% coverage.
    if doc.non_digital:
        return AuditResult(total=0, covered=0, missing=[])
    kept = _norm(" ".join(c for c in _doc_chunks(doc) if c))
    kept_nodigits = _digitless(kept)
    kept_raw = _strip_tags(" ".join(c for c in _doc_chunks(doc) if c))
    kept_tails = _norm(" ".join(w[1:] for w in kept_raw.split() if len(w) > 2))
    dropped_hay = _norm(" ".join(c for c in doc.dropped if c))

    # Pages where the output carries a table block: a multi-line table row
    # reads row-major in the source ('02CR176 Greene County, Delivery of
    # 9/9/2002') but cell-major in the output ('02CR176' / 'Greene County,
    # Tennessee' / 'Delivery of Schedule II...'), so substring matching can't
    # line them up. On such pages a line counts as covered when every one of
    # its tokens appears in the output.
    table_pages = {
        b.page
        for op in doc.opinions
        for b in op.blocks
        if b.kind == "table" and b.page
    }

    total = 0
    missing = []
    dropped = []
    furniture_hits = []
    with pdfplumber.open(pdf_path) as pdf:
        pages_lines = []
        for page in pdf.pages:
            # Read the ground truth through the same per-court geometry fix the
            # extractor uses, so a court that corrects a broken font box (Maine)
            # is audited against corrected text, not pdfplumber's jumbled raw.
            if extractor is not None:
                extractor.correct_page_geometry(page)
            # ROTATED chars (a court name printed sideways up a pleading
            # margin) can never be flowed body text — pdfplumber merges
            # them into the GT lines ('u o r o 13 After more than…'),
            # poisoning the match. Audit against upright text only; the
            # extractors surface the rotated marginalia separately.
            gt = page.filter(lambda o: o.get("upright", True) is not False)
            if extractor is not None:
                # Use the same char-faithful LINE reconstruction as extraction,
                # without its margin/furniture filtering.  ``extract_text``
                # alone can put italic or subscript runs on separate phantom
                # rows (``Id. San Remo Knick``) even though the renderer
                # correctly reunites them with their roman host line.  Every
                # upright glyph remains in this ground truth; only its visual
                # row is repaired before matching.
                gt_lines = extractor._merge_interleaved(
                    extractor._text_lines(gt)
                )
                source_lines = [
                    extractor.line_plain_text(line) for line in gt_lines
                ]
            else:
                source_lines = (gt.extract_text() or "").splitlines()
            pages_lines.append((page.page_number, source_lines))
    furniture = _running_furniture(pages_lines)
    for pno, lines in pages_lines:
        for raw in lines:
            if not raw.strip():
                continue
            total += 1
            # Kept content takes precedence: a line that is real content AND
            # happens to recur in the Removed box counts as kept.
            if _matches(raw, kept, kept_nodigits):
                continue
            # Small-caps banner artifact: a drop-cap face puts the large
            # initials on their own raw line, leaving 'NITED TATES ISTRICT
            # OURT' as a GT line that can never substring-match the kept
            # 'UNITED STATES DISTRICT COURT'. Match against the kept text
            # with each word's initial removed.
            if _matches(raw, kept_tails):
                continue
            if (
                pno in table_pages
                or getattr(extractor, "_ao_form", False)
            ) and all(
                _norm(t) in kept for t in raw.split() if _norm(t)
            ):
                continue
            if _split_filing_row_in_kept(raw, kept):
                continue
            # Routed to the Removed box (doc.dropped).
            if dropped_hay and _matches(raw, dropped_hay):
                dropped.append((pno, raw.strip()))
                continue
            # A single source baseline may contain two geometric columns, one
            # kept and one visibly removed.  Account for the split only when
            # both destinations contain a real phrase and together contain
            # every source token.
            if _split_between_kept_and_dropped(raw, kept, dropped_hay):
                dropped.append((pno, raw.strip()))
                continue
            # Identified page furniture: running headers/footers, or a stamp /
            # rule / rail recognizable from the line alone.
            if _furniture_key(raw) in furniture or _is_furniture(raw):
                furniture_hits.append((pno, raw.strip()))
                continue
            missing.append((pno, raw.strip()))
    return AuditResult(
        total=total,
        covered=total - len(missing),
        missing=missing,
        dropped=dropped,
        furniture=furniture_hits,
    )


def format_report(name: str, r: AuditResult, limit: int = 40) -> str:
    pct = (100.0 * r.covered / r.total) if r.total else 100.0
    head = (
        f"{name}: {r.covered}/{r.total} lines accounted for ({pct:.1f}%) — "
        f"{len(r.dropped)} dropped, {len(r.furniture)} furniture, "
        f"{len(r.missing)} missing"
    )
    lines = [head + ("  ✓" if not r.missing else "")]

    def _bucket(label, items):
        if not items:
            return
        lines.append(f"  {label}:")
        for pno, text in items[:limit]:
            lines.append(f"    p{pno}: {text[:90]!r}")
        if len(items) > limit:
            lines.append(f"    … +{len(items) - limit} more")

    # MISSING is the failure; DROPPED/FURNITURE are surfaced for eyeball review
    # so the removal decisions can be checked, not silently trusted.
    _bucket("MISSING", r.missing)
    _bucket("DROPPED", r.dropped)
    _bucket("FURNITURE", r.furniture)
    return "\n".join(lines)
