"""Furniture identification: folios, running heads/feet, stamps, gutters.

Furniture is identified by MEASUREMENT (repetition across pages, band
position, shape), never by configured margin constants that can cut through
content. Everything identified is surfaced as Dropped — never silently cut
(the audit reads dropped against its own haystack).

Kinds: folio | running-head | running-foot | stamp | gutter | rotated
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field

from ..pdfio.model import Line, PageModel, PdfModel


def is_folio_text(text: str) -> bool:
    """A standalone printed page number: '4' / '- 12 -' / 'Page 3' /
    'Page 3 of 11'."""
    t = (text or "").strip()
    low = t.lower()
    if low.startswith("page "):
        t = t[5:].strip()
        if " of " in t.lower():
            a, _, b = t.lower().partition(" of ")
            return a.strip().isdigit() and b.strip().isdigit()
    core = t.strip("-–—  ")
    return core.isdigit() and len(core) <= 4


# A WORD-PROCESSOR PATH IS NOT PROSE. Some chambers templates print the
# document's own source path under the signature — 'G:\\Judge-DLB\\DATA\\
# ORDERS\\Cov2025\\25-171 MOO re MTD.docx'. It renders as the writing's last
# paragraph, and worse, it sits BELOW the judge's signature stamp and so
# raises any "is this image below all the text" floor above the signature —
# which cost 8 of kyed's 25 records their signature. Matched over all 2,217
# federal district files it hits exactly the 10 chambers paths and nothing
# else: no 'This 20th day of May, 2026.', no 'IV. CONCLUSION', no
# '5 U.S.C. § 706', no URL, no Westlaw cite.
_FILE_PATH = re.compile(
    r'^"?(?:[A-Za-z]:|\\\\[\w.-]+)?[\\/]?[\w .$~()&-]+'
    r'(?:[\\/][\w .$~()&\'-]+){2,}\.(?:docx?|wpd|rtf|txt)"?$', re.I)


def is_chambers_path(text: str) -> bool:
    """The document's own word-processor path, printed by the template."""
    return bool(_FILE_PATH.match((text or "").strip()))


def furniture_key(text: str) -> str:
    """Repetition key: the line without its digits, so a footer that counts
    its own pages ('MEMORANDUM DECISION AND ORDER - 3') still matches."""
    return "".join(c for c in text if not c.isdigit()).strip()


def is_gutter_number(line: Line, body_x0: float,
                     column_ids: set[int] | None = None) -> bool:
    """A stationery line-number: a short numeric line wholly LEFT of the
    measured body rail (ca2's numbered paper at x0≈41 against a 72pt body;
    pleading paper's 1–28 left of the gutter rule). Cut by geometry, never by
    digit-stripping — a real label-only footnote line sits at or right of the
    body margin. Measured on PRINTABLE ink: a trailing space glyph must not
    drag the number's right edge past the rail.

    ``column_ids`` (from gutter_column_ids) adds the COLUMN evidence: a
    writing set on a narrower rail than the document's (carroll's concurrence
    at 72 against the majority's 108) prints detached footnote labels left of
    the document rail, and geometry alone reads them as margin ink. A true
    stationery number belongs to a printed column; a detached label never
    does. When the caller provides the page's columns, membership is
    required."""
    t = line.plain.strip()
    if not (t.isdigit() and len(t) <= 3):
        return False
    if column_ids is not None and line.id not in column_ids:
        return False
    ink_x1 = max((c["x1"] for c in line.chars
                  if (c.get("text") or "").strip()), default=line.x1)
    return ink_x1 <= body_x0 - 2


def gutter_column_ids(pm: PageModel) -> set[int]:
    """Line ids belonging to a stationery line-number COLUMN: five or more
    short numeric-only lines, right-aligned within 2pt (stationery numbers
    are right-justified: '9' and '10' share their ink's right edge), whose
    tops span at least 40% of the page. A scatter of detached footnote
    labels never builds that structure."""
    cands: list[tuple[float, Line]] = []
    for l in pm.lines:
        t = l.plain.strip()
        if not (t.isdigit() and len(t) <= 3):
            continue
        ink = [c["x1"] for c in l.chars if (c.get("text") or "").strip()]
        if ink:
            cands.append((max(ink), l))
    # The text block's own left edge — stationery numbering sits OUTSIDE it.
    body_lefts = sorted(l.x0 for l in pm.lines
                        if l.plain.strip() and not l.plain.strip().isdigit())
    body_left = body_lefts[len(body_lefts) // 2] if body_lefts else 0.0
    out: set[int] = set()
    for x1, _ in cands:
        group = [l for gx1, l in cands if abs(gx1 - x1) <= 2]
        if len(group) < 5:
            continue
        tops = [l.top for l in group]
        if max(tops) - min(tops) >= pm.height * 0.4:
            out.update(l.id for l in group)
            continue
        # …or a column that never enters the text block at all. A page whose
        # numbering starts below the caption spans less than the 40% floor
        # (alvarenga: 312pt against 317 needed) and is a line-number gutter
        # all the same — nothing else prints a right-aligned run of numerals
        # in the margin beside the body.
        if len(group) >= 8 and body_left and x1 < body_left - 4:
            out.update(l.id for l in group)
    return out


def _band_keys(model: PdfModel, band: str,
               body_size: float | None = None) -> set[str]:
    """Digitless keys of lines printing in a page band on 2+ pages — a court
    does not print the same sentence at the same page position twice by
    accident. Split visual rows are rejoined before keying, and both the
    piece key and the row key are learned."""
    counts: dict[str, int] = {}
    all_small: dict[str, bool] = {}
    for pm in model.pages:
        seen: set[str] = set()
        rows: dict = {}
        texts: list[tuple[str, bool]] = []
        for line in pm.lines:
            frac = line.top / pm.height
            # Top band 0.21: Connecticut's reporter row sits at exactly
            # 0.1900 of a Law Journal page and its boxed case name at 0.201.
            in_band = frac >= 0.85 if band == "bottom" else frac <= 0.22
            if not in_band:
                continue
            text = line.plain.strip()
            if not text or is_folio_text(text):
                continue
            small = (body_size is not None
                     and line.size <= body_size - 1.5)
            texts.append((text, small))
            if line.row is not None:
                rows.setdefault(line.row, []).append((text, small))
        texts.extend((" ".join(t for t, _ in pieces),
                      all(s for _, s in pieces))
                     for pieces in rows.values() if len(pieces) > 1)
        for text, small in texts:
            key = furniture_key(text)
            if key and key not in seen:
                seen.add(key)
                counts[key] = counts.get(key, 0) + 1
                all_small[key] = all_small.get(key, True) and small
    # A real running foot/head prints on MOST pages. Two occurrences out of
    # thirty-nine is not furniture — newton_v._state prints the identical
    # one-line footnote 'N A pseudonym.' on two consecutive pages, and a
    # flat >=2 ate both notes.
    #
    # EXCEPT sub-body-size TOP-band keys: a stapled document (scotus binds
    # an order and each writing into one PDF) carries per-writing running
    # heads ('Per Curiam' 9pt on 7 of 18 pages) that never reach the
    # whole-document floor — but a court never prints the same reduced-type
    # line at the page top twice by accident, and no footnote lives there.
    floor = max(2.0, 0.4 * model.n_pages)
    return {k for k, n in counts.items()
            if n >= floor or (band == "top" and all_small.get(k) and n >= 2)}


def repeated_bottom_keys(model: PdfModel) -> set[str]:
    return _band_keys(model, "bottom")


def repeated_top_keys(model: PdfModel,
                      body_size: float | None = None) -> set[str]:
    return _band_keys(model, "top", body_size)


def top_band_key_counts(model: PdfModel) -> dict[str, int]:
    """How many pages print each top-band key. The keys OVER the floor are
    the running head; the ones under it are how a STAPLED document's head
    gets lost — see `kind`'s head-second-row rule."""
    counts: dict[str, int] = {}
    for pm in model.pages:
        seen: set[str] = set()
        for line in pm.lines:
            if line.top / pm.height > 0.22:
                continue
            text = line.plain.strip()
            if not text or is_folio_text(text):
                continue
            key = furniture_key(text)
            if key and key not in seen:
                seen.add(key)
                counts[key] = counts.get(key, 0) + 1
    return counts


def top_band_key_sizes(model: PdfModel) -> dict[str, float]:
    """The SMALLEST size each top-band key prints at.

    A RUNNING HEAD IS SET AT ONE SIZE. cal prints the writing's own title
    block at body size on the writing's FIRST page ('Opinion of the Court by
    Guerrero, C. J.') and repeats the same words as an 11pt head on every
    page after it, so a test on the TEXT alone takes the body-size instance
    too — and that instance is the only row the writing can open on. It left
    the majority unbylined on 24 of cal's 30 records, whereupon
    conformed_signature_author supplied an author from opposing counsel's
    address block at the foot of the document."""
    out: dict[str, float] = {}
    for pm in model.pages:
        rows: dict = {}
        items: list[tuple[str, float]] = []
        for line in pm.lines:
            if line.top / pm.height > 0.22:
                continue
            text = line.plain.strip()
            if not text or is_folio_text(text):
                continue
            items.append((text, line.size or 0.0))
            if line.row is not None:
                rows.setdefault(line.row, []).append((text, line.size or 0.0))
        items.extend((" ".join(t for t, _ in p), min(s for _, s in p))
                     for p in rows.values() if len(p) > 1)
        for text, size in items:
            key = furniture_key(text)
            if key:
                out[key] = min(out.get(key, 1e9), size)
    return out


def head_band_rows(model: PdfModel, body_size: float) -> set[int]:
    """Rounded TOPS where sub-body running heads print on ≥40% of pages.
    The head band is POSITIONAL: a stapled document's page 1 prints its
    'Per Curiam' head exactly where every later page prints 'Opinion of
    the Court' — one occurrence of the text, dozens of the position."""
    rows: dict[int, int] = {}
    for pm in model.pages:
        seen: set[int] = set()
        for l in pm.lines:
            # Heads are SHORT lines — a full-measure reduced-type line at a
            # constant top is a continuation (kan's block quotes resume at
            # the same position on every page).
            if (l.top / pm.height <= 0.22 and l.plain.strip()
                    and not is_folio_text(l.plain)
                    and l.size and l.size <= body_size - 1.5
                    and (l.x1 - l.x0) <= 0.55 * pm.width):
                r = round(l.top)
                if r not in seen:
                    seen.add(r)
                    rows[r] = rows.get(r, 0) + 1
    floor = max(2.0, 0.4 * model.n_pages)
    return {r for r, n in rows.items() if n >= floor}


def is_bottom_furniture(line: Line, page_height: float,
                        bottom_keys: set[str]) -> bool:
    text = line.plain.strip()
    if not text:
        return True
    if is_folio_text(text):
        return True
    return (line.top > page_height * 0.85
            and furniture_key(text) in bottom_keys)


def _looks_like_efiling_stamp(text: str) -> bool:
    """The CM/ECF overlay family, identified by its fielded shape:
    'Case 3:20-cv-00187-SLG   Document 273   Filed 05/18/26   Page 1 of 5',
    'Case: 23-1234  Document: 45  Page: 1  Date Filed: ...',
    'Appellate Case: 24-8046  ...'. Field labels + separators, not prose."""
    t = " ".join(text.split())
    fields = sum(1 for f in ("Case", "Document", "Filed", "Page", "Entry",
                             "Date", "Doc", "Appellate", "USDC", "ID", "PageID")
                 if f + ":" in t or t.startswith(f + " ") or f" {f} " in t)
    digits = sum(c.isdigit() for c in t)
    return fields >= 2 and digits >= 6


# PRE-PRINTED FORM FURNITURE's band and type ceiling. Measured on nev, whose
# form number runs 3.0-6.5pt against a 12.0pt body in the last 7% of the page.
_FORM_BAND = 0.07
_FORM_SIZE_MAX = 0.6


@dataclass
class FurnitureFinder:
    """Document-level furniture state + per-line classification."""

    model: PdfModel
    body_x0: float
    body_size: float = 12.0
    bottom_keys: set[str] = field(default_factory=set)
    top_keys: set[str] = field(default_factory=set)
    top_counts: dict = field(default_factory=dict)
    top_sizes: dict = field(default_factory=dict)

    def __post_init__(self):
        self.bottom_keys = repeated_bottom_keys(self.model)
        self.top_keys = repeated_top_keys(self.model, self.body_size)
        self.top_counts = top_band_key_counts(self.model)
        self.head_rows = head_band_rows(self.model, self.body_size)
        self.top_sizes = top_band_key_sizes(self.model)
        # DOCUMENT-level gutter rail: when several pages prove a
        # line-number column at the same right edge, the remaining pages'
        # scattered numbers on that edge are the same stationery (ca2's
        # numbered paper — short pages fail the per-page span test).
        _x1s: list[float] = []
        for pm in self.model.pages:
            ids = gutter_column_ids(pm)
            if ids:
                ink = [max((c["x1"] for c in l.chars
                            if (c.get("text") or "").strip()), default=l.x1)
                       for l in pm.lines if l.id in ids]
                if ink:
                    _x1s.append(sorted(ink)[len(ink) // 2])
        self.doc_gutter_x1 = (sorted(_x1s)[len(_x1s) // 2]
                              if len(_x1s) >= 3 else None)

    def _gutter_ids(self, pm: PageModel) -> set[int]:
        if not hasattr(self, "_gutters"):
            self._gutters: dict[int, set[int]] = {}
        if pm.number not in self._gutters:
            self._gutters[pm.number] = gutter_column_ids(pm)
        return self._gutters[pm.number]

    def _row_text(self, pm: PageModel, line: Line) -> str:
        """The full VISUAL ROW's text: pdfio may have split a footer at its
        column gaps, and half a stamp doesn't look like one."""
        if line.row is None:
            return line.plain.strip()
        return " ".join(l.plain.strip() for l in pm.lines
                        if l.row == line.row).strip()

    def kind(self, pm: PageModel, line: Line) -> str | None:
        """Furniture kind, or None when the line is (potential) content."""
        text = line.plain.strip()
        if not text:
            return None
        # A court's PARAGRAPH MARKER ('{4}' — nm; '[3]' — ind; '¶ 12' —
        # ill/wis) is body text wherever it prints; no furniture rule may
        # take it.
        if re.match(r"^(?:\{\d{1,3}\}|\[\d{1,3}\]|\[?¶\s*\d{1,3}\.?\]?)$",
                    text):
            return None
        # PLEADING-PAPER FILLER: on numbered paper a court fills the unused
        # lines with '/ / /' so the numbering stays continuous. It carries
        # no words, and merged into the prose it split azd's 'Accordingly,'
        # from the 'IT IS ORDERED' sentence it introduces.
        if set(text) <= {"/", " "} and "/" in text:
            return "filler"
        frac = line.top / pm.height
        # PRE-PRINTED FORM FURNITURE: a row in tiny type, in the top or
        # bottom band, standing ENTIRELY OUTSIDE the body measure. That is
        # the court's own stationery — a form number, a seal caption — and no
        # opinion text is ever set there.
        #
        # Nevada prints '(O) 1947A' under a 'SUPREME COURT / NEVADA' seal
        # caption at the foot of every page, and its scans OCR it differently
        # every time ('(01 1947A MilDro', '0) 1947A', '(0) I 947A', '19•17A'),
        # so the repeat-keyed rules above never see it and it landed in the
        # body as a paragraph. Measured over nev: top >= 0.93 of the height,
        # 3.0-6.5pt against a 12.0pt body, and x1 <= 70.4 against a measured
        # body rail of 107 — every one of the 60 rows is clear of the measure
        # on the left. The test is 'outside the measure', not 'short and
        # small', so a genuine short row AT the rail cannot be caught by it.
        if (frac <= _FORM_BAND or frac >= 1.0 - _FORM_BAND) \
                and line.size and self.body_size \
                and line.size <= self.body_size * _FORM_SIZE_MAX \
                and (line.x1 < self.body_x0
                     or line.x0 > pm.width - self.body_x0):
            return "stamp"
        # THE DOCUMENT'S OWN SOURCE PATH is the template talking, not the
        # court — it renders as the writing's last paragraph on 10 of kyed's
        # 25 records. Surfaced as a removal so the record still says what
        # stood there.
        if is_chambers_path(text):
            return "stamp"
        row_text = self._row_text(pm, line)
        if row_text != text and (frac <= 0.15 or frac >= 0.85):
            if _looks_like_efiling_stamp(row_text):
                return "stamp"
            if frac >= 0.85 and furniture_key(row_text) in self.bottom_keys:
                return "running-foot"
        if is_gutter_number(line, self.body_x0, self._gutter_ids(pm)):
            return "gutter"
        if (self.doc_gutter_x1 is not None and text.isdigit()
                and len(text) <= 3):
            _ink = [c["x1"] for c in line.chars
                    if (c.get("text") or "").strip()]
            if _ink and abs(max(_ink) - self.doc_gutter_x1) <= 2.5 \
                    and max(_ink) <= self.body_x0 - 6:
                return "gutter"
        # bottom band starts at 0.82: ca3's half-format sheet folios its
        # pages at 84% height (the alone-on-band guard below still keeps
        # detached footnote labels).
        if is_folio_text(text) and (frac <= 0.19 or frac >= 0.82):
            # In the TOP band a numeral is a folio even beside a row-mate
            # (ca6's 'Page 2' shares its row with the running head; ca11
            # prints the folio on the first text line's row). Detached
            # footnote LABELS — the reason for the row-mate exception —
            # live at the page FOOT only.
            if frac <= 0.19:
                return "folio"
            # A foot folio prints ALONE on its band; a short numeral
            # sharing its top with text is a DETACHED footnote label
            # ('3  ' beside its note's first line — ca10). Another NUMERAL
            # is not that text: alaska and alaskactapp set a dressed folio
            # and the slip opinion's number on ONE row ('-2-   7776'), so
            # each piece vetoed the other, no band key was ever learned, and
            # the whole foot rendered as body prose — 34 of 50 alaska
            # records, 39 of 42 alaskactapp, several paragraphs per file.
            if not any(o is not line and abs(o.top - line.top) < 2
                       and o.plain.strip()
                       and not is_folio_text(o.plain.strip())
                       for o in pm.lines):
                return "folio"
            # EXCEPT a MARGIN folio: the reporter prints the page number in
            # the outer margin ON the first text line's row (or's advance
            # sheets glue '728' onto the body) — margin position is the
            # evidence.
            ink_x1 = max((c["x1"] for c in line.chars
                          if (c.get("text") or "").strip()), default=line.x1)
            if (ink_x1 <= self.body_x0 - 6
                    or line.x0 >= pm.width * 0.85):
                return "folio"
        if _looks_like_efiling_stamp(text) and (frac <= 0.15 or frac >= 0.85):
            return "stamp"
        # A CORNER STAMP: a short small-type line pinned in a top corner
        # (mont's e-filing date '03/31/2026' at 86% width, 9pt on a 13pt
        # body; its 6pt 'Case Number: …' twin). Position + reduced size —
        # the banner is centered and body-size, so it never matches.
        if (frac <= 0.19 and line.size
                and line.size <= self.body_size - 2
                and (line.x0 > pm.width * 0.6 or line.x1 < pm.width * 0.35)
                and len(text) <= 60
                # A NEUTRAL CITATION, docket, or caption LABEL in the
                # corner is content — Maine's official cite ('2026 ME 14',
                # 'Som-25-258', 'PUC-25-60') and its margin apparatus
                # ('Docket:', 'Argued:', 'Decided:') print exactly where a
                # stamp would.
                and not re.match(r"^\d{4}\s+[A-Z]{2,4}(\s+App)?\s+\d+\s*$",
                                 text)
                and not re.match(r"^[A-Z][A-Za-z]{1,3}-\d{2,4}-\d+\s*$", text)
                and not re.match(r"^[A-Z][a-z]+:\s*$", text)):
            return "stamp"
        key = furniture_key(text)
        if frac >= 0.85 and key in self.bottom_keys:
            return "running-foot"
        # Running heads only bind from page 2 on: page 1's banner is content.
        # EXCEPT a sub-body-size learned head — a stapled document's first
        # page carries the same 9pt 'Per Curiam' band as its later pages,
        # and a banner is never set below body size.
        # …but the SAME WORDS set a clear step larger are the type block's
        # own title, not the head that repeats it (see top_band_key_sizes).
        _hs = self.top_sizes.get(key)
        _oversize = bool(line.size and _hs is not None
                         and line.size >= _hs + 1.5)
        if (frac <= 0.22 and key in self.top_keys and not _oversize
                and (pm.number > 1
                     or (line.size and line.size <= self.body_size - 1.5))):
            return "running-head"
        # A HEAD'S SECOND ROW, when the head is SPLIT BETWEEN WRITINGS. The
        # 40%-of-pages floor above is calibrated for one head per document.
        # A stapled document has one per writing: cervantes_v._state runs
        # 'CERVANTES v. STATE' over 'Opinion of the Court' on the majority's
        # 10 pages, over 'Jacobs, J., Dissenting' on the dissent's 19, and
        # over 'Howe, C.J., Specially Concurring' on the concurrence's 2 —
        # of a 32-page document, so only the case name and the longest
        # writing's line clear the floor. The other two rendered INSIDE the
        # prose, mid-sentence ('Opinion of the Court retained.', 'Opinion of
        # the Court disclosure of Dr. Ramirez' Records').
        #
        # The evidence is the row ABOVE: a line is the head's second row
        # when a CONFIRMED head row prints directly over it, within a
        # leading and a half, and its own words repeat at the page top on
        # more than one page. A court does not print the same short line
        # under its running head twice by accident.
        # …with the SAME SIZE GUARD the keyed rule above keeps: cal sets the
        # writing's own title block at body size on its first page ('Opinion
        # of the Court by Guerrero, C. J.') and repeats those words as an
        # 11pt head on every page after it, so the body-size instance — the
        # only row the writing can open on — must survive. Without
        # `_oversize` here it did not, and cal's trailing counsel roster came
        # back as `attorneys` while its writings lost 30-50 blocks each.
        if frac <= 0.22 and key and not _oversize \
                and self.top_counts.get(key, 0) >= 2 \
                and (line.x1 - line.x0) <= 0.55 * pm.width:
            _lead = 1.5 * (self.body_size or 12.0)
            if any(o is not line and o.plain.strip()
                   and 0 < line.top - o.top <= _lead
                   and furniture_key(o.plain.strip()) in self.top_keys
                   for o in pm.lines):
                return "running-head"
        # The positional test: a sub-body line printed exactly on the
        # document's learned head band is the head, whatever it says (a
        # stapled document's one-page 'Per Curiam' head never repeats as
        # TEXT but always as POSITION). A true head is ISOLATED — it floats
        # clear above the text block; a page-top continuation line (kan's
        # reduced-type block quotes resume at a constant top) is flush with
        # the line below it and is CONTENT.
        if (frac <= 0.22 and line.size and not _oversize
                and line.size <= self.body_size - 1.5
                and (line.x1 - line.x0) <= 0.55 * pm.width
                and any(r in self.head_rows for r in
                        (round(line.top) - 1, round(line.top),
                         round(line.top) + 1))):
            return "running-head"
        return None
