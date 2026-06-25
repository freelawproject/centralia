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

import pdfplumber

from .models import ExtractedDocument


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
    ("em", "strong", "u", "footnotemark", "pagenumber", "sup", "sub")
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
            name = s[j + 1 : k].strip("/").split()[0].split("=")[0].lower()
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


def _norm(s: str) -> str:
    """Whitespace-removed, tag-stripped, unescaped, ligature-expanded,
    lowercased — one extractor keeps 'Plaintiﬀ' where extract_text says
    'Plaintiff', so both sides expand."""
    s = _unescape_xml(_strip_tags(s))
    for lig, exp in _LIGATURES:
        if lig in s:
            s = s.replace(lig, exp)
    return "".join(s.split()).lower()


def _chunk(x):
    """Yield text from a value that may be a str, a caption-columns dict, or a
    styled headmatter row ({'__hm__': True, 'html': ...})."""
    if isinstance(x, dict):
        if x.get("html"):
            yield _strip_tags(str(x["html"]))
        for key in ("left", "right"):
            for line in x.get(key, []) or []:
                if isinstance(line, dict):  # faithful cell: {'h': html, ...}
                    yield _strip_tags(str(line.get("h", "")))
                elif line:
                    yield _strip_tags(str(line))
        if x.get("__hmrow__"):  # three-zone flush-right row
            for key in ("l", "c", "r"):
                if x.get(key):
                    yield _strip_tags(str(x[key]))
    elif x:
        yield str(x)


def _doc_chunks(doc: ExtractedDocument):
    """Kept content ONLY — everything the extractor surfaced as real content.
    ``doc.dropped`` is deliberately excluded so the audit can match kept and
    removed text against separate haystacks and tell them apart."""
    for s in doc.summary:
        yield from _chunk(s)
    yield from doc.trailer
    for s in getattr(doc, "signature", []) or []:
        if not isinstance(s, dict):  # image rows carry no text
            yield _strip_tags(str(s))
    for s in getattr(doc, "syllabus", []) or []:
        yield from _chunk(s)
    for s in getattr(doc, "headnotes", []) or []:
        yield from _chunk(s)
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
    # A line that is nothing but caption-rail glyphs ('§' / ') )') — the drawn
    # rail of a two-column caption, not content.
    if stripped and all(c in ")]§|* " for c in stripped):
        return True
    # Glyphs the PDF maps to no unicode point come through as '(cid:NN)' tokens
    # — the source carries no text there, so the line is unauditable junk.
    if "(cid:" in raw:
        return True
    if _is_filing_stamp(raw):
        return True
    return False


def _matches(raw: str, haystack: str) -> bool:
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
    # A ':'-gutter caption line, right-column only ('  : Superior Court ...'):
    # the extractor keeps the text without the gutter colon.
    if ":" in needle and needle.strip(":") and needle.strip(":") in haystack:
        return True
    stripped = raw.strip()
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
            if _matches(raw, kept):
                continue
            if pno in table_pages and all(
                _norm(t) in kept for t in raw.split() if _norm(t)
            ):
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


def audit_coverage(
    doc: ExtractedDocument, pdf_path: str, extractor=None
) -> AuditResult:
    kept = _norm(" ".join(c for c in _doc_chunks(doc) if c))
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
            pages_lines.append(
                (page.page_number, (gt.extract_text() or "").splitlines())
            )
    furniture = _running_furniture(pages_lines)
    for pno, lines in pages_lines:
        for raw in lines:
            if not raw.strip():
                continue
            total += 1
            # Kept content takes precedence: a line that is real content AND
            # happens to recur in the Removed box counts as kept.
            if _matches(raw, kept):
                continue
            if pno in table_pages and all(
                _norm(t) in kept for t in raw.split() if _norm(t)
            ):
                continue
            # Routed to the Removed box (doc.dropped).
            if dropped_hay and _matches(raw, dropped_hay):
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
