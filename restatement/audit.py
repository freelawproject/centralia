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

from dataclasses import dataclass
from html import unescape

import pdfplumber

from .models import ExtractedDocument


@dataclass
class AuditResult:
    total: int
    covered: int
    missing: list  # list of (page_number, line_text)

    @property
    def ok(self) -> bool:
        return not self.missing


def _strip_tags(s: str) -> str:
    """Remove <...> inline markup."""
    out = []
    depth = 0
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            if depth:
                depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _norm(s: str) -> str:
    """Whitespace-removed, tag-stripped, unescaped, lowercased."""
    s = unescape(_strip_tags(s))
    return "".join(s.split()).lower()


def _chunk(x):
    """Yield text from a value that may be a str, a caption-columns dict, or a
    styled headmatter row ({'__hm__': True, 'html': ...})."""
    if isinstance(x, dict):
        if x.get("html"):
            yield _strip_tags(str(x["html"]))
        for key in ("left", "right"):
            for line in x.get(key, []) or []:
                yield str(line)
    elif x:
        yield str(x)


def _doc_chunks(doc: ExtractedDocument):
    for s in doc.summary:
        yield from _chunk(s)
    yield from doc.dropped
    yield from doc.trailer
    yield from getattr(doc, "syllabus", []) or []
    yield from doc.parties
    for v in (
        doc.court_label,
        doc.decision_date,
        doc.docket_number,
        doc.other_docket,
        doc.motion,
        doc.history,
        doc.parent_case,
        doc.lower_court,
        doc.disposition,
        doc.attorneys,
        doc.judges,
        doc.submitted,
    ):
        if v:
            yield str(v)

    def from_footnotes(fns):
        for fn in fns:
            yield fn.label
            for _tag, text in fn.paragraphs:
                yield text

    yield from from_footnotes(doc.headmatter_footnotes)
    for op in doc.opinions:
        yield op.author
        for b in op.blocks:
            yield b.text
            if b.payload:
                for row in b.payload.get("rows", []) or []:
                    for cell in row:
                        if cell:
                            yield str(cell)
        yield from from_footnotes(op.footnotes)


def _is_filing_stamp(raw: str) -> bool:
    """Court-system furniture stamped onto the page margin — an electronic
    filing header or a reporter page footer — carrying no opinion content (the
    'bates stamps' that extraction legitimately drops). Recognized so it doesn't
    count against coverage, the same way page numbers don't."""
    low = raw.strip().lower()
    if low.startswith("usca"):  # USCA4 Appeal: / USCA11 Case:
        return True
    # Court e-publishing stamp, stamped at the page top (e.g. Nebraska):
    # 'Nebraska Supreme Court Online Library' / 'www.nebraska.gov/...' /
    # '04/21/2026 08:08 AM CDT'.
    if "online library" in low or low.startswith("www."):
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
    # Reporter page footer: '– 2 – 2819' / '- 2 - 2819' (rule + page + docket).
    body = low.strip("–—- ")
    if (
        body
        and all(c.isdigit() or c in "–—- " for c in low)
        and any(c.isdigit() for c in low)
    ):
        return True
    return False


def _covered(raw: str, haystack: str) -> bool:
    """Whether source line ``raw`` is accounted for in ``haystack``. Tolerates a
    leading pleading-paper line number ('1 ...', '23 ...'): such gutter numbers
    are merged into the row by ``extract_text`` but are layout furniture, not
    content, so the line still counts as covered if the rest of it matches."""
    needle = _norm(raw)
    if not needle:
        return True
    if needle in haystack:
        return True
    # A ':'-gutter caption line, right-column only ('  : Superior Court ...'):
    # the extractor keeps the text without the gutter colon.
    if ":" in needle and needle.strip(":") and needle.strip(":") in haystack:
        return True
    # A horizontal rule drawn as text ('______' / '------' / '******'): layout
    # furniture, not content.
    stripped = raw.strip()
    if len(stripped) >= 4 and all(c in "_-—–=*" for c in stripped):
        return True
    if _is_filing_stamp(raw):
        return True
    parts = raw.strip().split(None, 1)
    if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) <= 3:
        rest = _norm(parts[1])
        if rest and rest in haystack:
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
        if len(a) >= 6 and len(b) >= 6 and a in haystack and b in haystack:
            return True
    return False


def _furniture_key(line: str) -> str:
    """Normalized margin-line key with digit runs masked to '#', so a running
    header/footer that only varies by page number ('... Page 2 of 11' vs '...
    Page 3 of 11', or a per-page case/date stamp) collapses to one key and is
    recognized as repeated."""
    n = _norm(line)
    out, prev_digit = [], False
    for ch in n:
        if ch.isdigit():
            if not prev_digit:
                out.append("#")
            prev_digit = True
        else:
            out.append(ch)
            prev_digit = False
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
    return {n for n, pgs in margin_pages.items() if len(pgs) >= 3}


def audit_coverage(doc: ExtractedDocument, pdf_path: str) -> AuditResult:
    haystack = _norm(" ".join(c for c in _doc_chunks(doc) if c))

    total = 0
    missing = []
    with pdfplumber.open(pdf_path) as pdf:
        pages_lines = [
            (page.page_number, (page.extract_text() or "").splitlines())
            for page in pdf.pages
        ]
    furniture = _running_furniture(pages_lines)
    for pno, lines in pages_lines:
        for raw in lines:
            if not raw.strip():
                continue
            total += 1
            if _furniture_key(raw) in furniture or _covered(raw, haystack):
                continue
            missing.append((pno, raw.strip()))
    return AuditResult(total=total, covered=total - len(missing), missing=missing)


def format_report(name: str, r: AuditResult, limit: int = 40) -> str:
    pct = (100.0 * r.covered / r.total) if r.total else 100.0
    head = (
        f"{name}: {r.covered}/{r.total} lines accounted for "
        f"({pct:.1f}%), {len(r.missing)} missing"
    )
    if not r.missing:
        return head + "  ✓"
    lines = [head]
    for pno, text in r.missing[:limit]:
        lines.append(f"    p{pno}: {text[:90]!r}")
    if len(r.missing) > limit:
        lines.append(f"    … +{len(r.missing) - limit} more")
    return "\n".join(lines)
