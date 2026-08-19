"""The fixed pipeline. Eleven stages, one order, no overrides:

  load > triage > measure > classify > furniture > footnotes > segments
  > headmatter > body > finalize > emit

Fresh state per document; every decision in the trace. Courts appear only as
the CourtProfile handed to the resolvers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import geometry
from . import model as m
from .classify import classify_doc_type, triage
from .courts import get_profile
from .pdfio import build_pdf
from .resolve.assemble import assemble
from .resolve.bylines import BylineParser
from .resolve.captions import classify_page
from .resolve.evidence import Trace
from .resolve.footnotes import FootnoteZones
import collections as _collections
import os as _os_env
import re as _re

# A CASE CITATION inside a publication-status sentence means the sentence is
# about ANOTHER decision: a reporter or database cite, a docket number, a
# star-page. Length is NOT the discriminator — ca5 states its own status in
# 70 characters ('* This opinion is not designated for publication. See 5th
# Cir. R. 47.5.') and that one is TRUE, while mich's Reporter syllabus
# recites the court BELOW's unpublished opinion and tagged 17 of 50
# published slips wrongly.
_STATUS_CITES_ANOTHER = _re.compile(
    r"\b(?:wl|lexis)\b|\bno\.\s*\d|\bf\.\s?(?:supp|app)|"
    r"\b\d+\s+[a-z]\.\s?[a-z]?\.?\s?\d|\bat\s+\*\d")

from .resolve.evidence import NOTHING, court_decides
from .resolve.furniture import FurnitureFinder
from .resolve.headmatter import read_headmatter, _hm_line
from .resolve.segments import Segmenter
from .styles import pick as pick_style

PIPELINE_VERSION = "2.0.0a0"

# Warnings that describe the SOURCE PDF rather than the parse. These can
# never be fixed by better extraction, so they route a file to 'scanned'
# instead of 'review' and keep the defect worklist honest.
SOURCE_WARNINGS = (
    "scan with OCR text layer",
    "image-only page",
)


def _column_order(lines: list) -> list:
    """Re-read a TWO-COLUMN block in column order. Guam sets counsel as
    parallel columns ('Appearing for Plaintiff-Appellee:' left, 'Appearing
    for Defendant-Appellant:' right) that row-wise reading interleaves,
    attributing lawyers to the wrong party. Evidence required: every visual
    row splits into exactly two pieces, each column's left edge is
    consistent, and the columns never overlap. Anything less reads in the
    original order."""
    if len(lines) < 4:
        return lines
    xs = sorted(l.x0 for l in lines)
    gap, idx = max((b - a, i) for i, (a, b) in enumerate(zip(xs, xs[1:])))
    if gap < 40:
        return lines
    split_x = (xs[idx] + xs[idx + 1]) / 2
    left = [l for l in lines if l.x0 < split_x]
    right = [l for l in lines if l.x0 >= split_x]
    if len(left) < 2 or len(right) < 2:
        return lines
    if max(l.x0 for l in left) - min(l.x0 for l in left) > 14:
        return lines
    if max(l.x0 for l in right) - min(l.x0 for l in right) > 14:
        return lines
    if max(l.x1 for l in left) - 2 > min(l.x0 for l in right):
        return lines
    return (sorted(left, key=lambda l: (l.page, l.top))
            + sorted(right, key=lambda l: (l.page, l.top)))


@dataclass
class ExtractionResult:
    document: m.Document
    trace: Trace
    # valid   — fully accounted, nothing to look at
    # scanned — parsed, but the SOURCE is a scan (nothing to fix here)
    # review  — the parse left something unplaced or warned
    # failed  — no usable output
    status: str = "valid"
    versions: dict = field(default_factory=lambda: {"pipeline": PIPELINE_VERSION})


def _attached_documents(model) -> list[tuple[int, int]]:
    """Page ranges of the documents STAPLED into one PDF. A later page
    opening with a fresh 'Filed <date>' stamp AND the court's banner is a
    new cover (calctapp staples the unmodified opinion behind its
    modification order). One range = one document."""
    from .resolve.headmatter import _is_banner_row
    cuts = [0]
    for i, pm in enumerate(model.pages):
        if i == 0:
            continue
        tops = sorted((l for l in pm.lines if l.plain.strip()),
                      key=lambda l: l.top)[:4]
        has_banner = any(_is_banner_row(l.plain) for l in tops)
        # the filing stamp may be its own row ('FILED' over 'AUG 10 2026'
        # — ca9) or an inline 'Filed 7/30/26' (calctapp)
        # A filing STAMP IS SHORT. Without a bound, a sentence of the body
        # that merely opens on the word ('filed by [Ortiz's] probation
        # officer."  Accordingly, the District…') reads as a stamp, and
        # paired with a prose line carrying two court words — which
        # `_is_banner_row` accepts — it cuts a new stapled document out of
        # the middle of an opinion (ortiz-rodriguez split at page 9 and lost
        # its writing). calctapp's 'Filed 7/30/26' is 13 characters.
        has_filed = any(
            (l.plain.strip().lower().startswith("filed ")
             and len(l.plain.strip()) <= 40)
            or l.plain.strip().rstrip(":").upper() == "FILED"
            for l in tops)
        if has_banner and has_filed:
            cuts.append(i)
    cuts.append(len(model.pages))
    return list(zip(cuts, cuts[1:]))


def _shift_pages(doc: m.Document, off: int) -> None:
    """Add ``off`` to every prov page — a stapled part processed with local
    numbering keeps its true PDF pages for the viewer."""
    def fix(obj):
        prov = getattr(obj, "prov", None)
        if prov is not None:
            try:
                prov.page += off
            except Exception:
                obj.prov = m.Prov(prov.page + off, prov.line_ids)
    for it in (list(doc.headmatter) + list(doc.syllabus)
               + list(doc.attorneys) + list(doc.headnotes)
               + list(doc.signature) + list(doc.trailer)
               + list(doc.dropped) + list(doc.residual)
               + list(doc.headmatter_footnotes)):
        fix(it)
        for side in ("left", "right"):
            for row in getattr(it, side, []) or []:
                fix(row)
        for b in getattr(it, "blocks", []) or []:
            fix(b)
    for op in doc.opinions:
        try:
            op.author_prov.page += off
        except Exception:
            op.author_prov = m.Prov(op.author_prov.page + off,
                                    op.author_prov.line_ids)
        for coll in (op.caption, op.blocks, op.signature, op.footnotes):
            for it in coll or []:
                fix(it)
                for b in getattr(it, "blocks", []) or []:
                    fix(b)


def extract(pdf_path: str, court_id: str) -> ExtractionResult:
    model = build_pdf(str(pdf_path))
    bounds = _attached_documents(model)
    if len(bounds) > 1:
        results = []
        for a, b in bounds:
            part = type(model)(path=model.path, pages=model.pages[a:b])
            saved = [pm.number for pm in part.pages]
            for k, pm in enumerate(part.pages, 1):
                pm.number = k
            r = _extract_model(part, court_id, pdf_path)
            for pm, n in zip(part.pages, saved):
                pm.number = n
            _shift_pages(r.document, a)
            results.append(r)
        base = results[0]
        bd = base.document
        for r in results[1:]:
            d = r.document
            bd.headmatter.extend(d.headmatter)
            bd.syllabus.extend(d.syllabus)
            bd.attorneys.extend(d.attorneys)
            bd.headnotes.extend(d.headnotes)
            bd.opinions.extend(d.opinions)
            bd.dropped.extend(d.dropped)
            bd.residual.extend(d.residual)
            bd.headmatter_footnotes.extend(d.headmatter_footnotes)
            for w in d.warnings:
                if w not in bd.warnings:
                    bd.warnings.append(w)
            for f in ("publication_status", "decision_date", "submitted",
                      "docket_number", "judges", "disposition",
                      "lower_court", "history", "attorneys"):
                if not getattr(bd.criteria, f):
                    setattr(bd.criteria, f, getattr(d.criteria, f))
            if not bd.criteria.parties:
                bd.criteria.parties = d.criteria.parties
        bd.warnings.append(
            f"{len(bounds)} stapled documents (covers at pp "
            + ", ".join(str(a + 1) for a, _ in bounds) + ")")
        if any(r.status != "valid" for r in results):
            base.status = "review"
        return base
    return _extract_model(model, court_id, pdf_path)


def _extract_model(model, court_id: str, pdf_path) -> ExtractionResult:
    profile = get_profile(court_id)
    trace = Trace()

    for pm in model.pages:
        for quirk, detail in pm.events:
            trace.event(f"quirk.{quirk}", f"p{pm.number}: {detail}")

    meta = m.Meta(court_id=court_id, court_label=profile.court_label,
                  n_pages=model.n_pages, source_path=str(pdf_path))
    doc = m.Document(meta=meta)

    # 2 triage — a scan is a SUCCESS status, not a failure. But a scan WITH
    # a substantial text layer (OCR) holds a parseable opinion: extract it
    # and flag REVIEW — the geometry is untrusted, the words are not lost.
    verdict = triage(model)
    if verdict == "scan":
        ink = sum(p.ink_chars for p in model.pages)
        # 250, not 500: a one-page writ disposition's WHOLE text is ~350
        # chars (lactapp — 'writ dismissed' orders were stubbed empty);
        # a stamp-only overlay (CM/ECF header, ~80 chars) still stubs.
        if ink < 250:
            meta.doc_type = m.DocType.SCAN
            doc.warnings.append("non-born-digital (scan); not parsed")
            return ExtractionResult(doc, trace, status="valid")
        doc.warnings.append(
            "scan with OCR text layer; extracted, geometry untrusted")
    # A HYBRID document: born-digital cover + scanned appendix pages that
    # carry no text layer at all (wis reprints an order as page images).
    # Nothing text-based is lost, but the reader must know pages are
    # image-only.
    from .classify import SCAN_IMAGE_AREA
    _img_only = [pm.number for pm in model.pages
                 if pm.image_area > SCAN_IMAGE_AREA and pm.ink_chars < 120]
    if _img_only and verdict != "scan" and len(_img_only) < model.n_pages:
        doc.warnings.append(
            f"{len(_img_only)} image-only page(s), no text layer "
            f"(pp {_img_only[0]}–{_img_only[-1]})")
    if verdict == "unreadable":
        meta.doc_type = m.DocType.UNKNOWN
        doc.warnings.append("text layer unreadable (unmapped CID glyphs)")
        return ExtractionResult(doc, trace, status="failed")

    # 3 measure
    geom = geometry.measure(model)
    vocab = geometry.learn_vocabulary(model)
    if geom:
        trace.event("geometry", f"body_x0={geom.body_x0} right={geom.right_x1:.0f} "
                                f"lead={geom.lead} size={geom.body_size}")

    # 4 classify
    sig, cap_style, cap_name = classify_page(model.pages[0])
    doc_style = pick_style(model, sig, profile.styles)
    meta.doc_style = cap_style
    # The caption band never runs PAST an interior 'Syllabus' section
    # heading (conn sets the syllabus on the caption page and the measured
    # band swallowed its first paragraph as hmrows).
    _b0 = sig.get("band")
    if _b0:
        for _l in model.pages[0].lines:
            if " ".join(_l.plain.split()).lower() == "syllabus" \
                    and _b0[0] < _l.top < _b0[1]:
                sig["band"] = (_b0[0], _l.top - 2)
                break
    doc_type, heading = classify_doc_type(model, geom)
    meta.doc_type = doc_type
    if heading:
        trace.event("doc-type", f"{doc_type} via {heading!r}")

    # 5 furniture
    ff = FurnitureFinder(model, geom.body_x0 if geom else 72.0,
                         geom.body_size if geom else 12.0)
    content_by_page: dict[int, list] = {}
    # v1 lesson: the RUNNING HEAD is read before it is dropped — ca2's
    # corner slug ('25-246-cv' / 'Perez v. Porter') is the docket and the
    # case name, stated nowhere else on a summary order.
    _slug_docket: list[str] = []
    _slug_case: list[str] = []
    _figures: list = []
    _mastheads: list = []   # page-1 seals: headmatter, not body
    _sig_imgs: list = []    # last-page signature stamps
    # STATIONERY REPEATS; A FIGURE DOES NOT. An image printed at the SAME
    # position on page after page is the court's watermark or letterhead,
    # not something the opinion refers to — ky sets its seal at 124,249,
    # 363x294pt, on all 24 pages of every record, and it passes the figure
    # test (22% of the page, clear of both margins), so all 1,448 page
    # rasters across the court were cropped and planted in the body. This
    # is the same rule the furniture pass already applies to running heads
    # and folios, stated for images: keyed on the position and size, three
    # pages or more is stationery.
    _img_key = _collections.Counter(
        (round(_i.x0), round(_i.top), round(_i.x1 - _i.x0),
         round(_i.bottom - _i.top))
        for _pm in model.pages for _i in _pm.images)
    _STATIONERY_PAGES = 3

    def _is_stationery(_i) -> bool:
        return _img_key[(round(_i.x0), round(_i.top), round(_i.x1 - _i.x0),
                         round(_i.bottom - _i.top))] >= _STATIONERY_PAGES

    # A PAGE UNDER A FULL-BLEED RASTER IS A SCAN, and nothing on it is a
    # FIGURE. tenn's `mark_gray_v._tyson_foods_inc.` carries two images per
    # page: the whole sheet at 0,0 612x792, which the stationery rule above
    # catches, and the scan's own content area at ~77,70 472x575 — 57% of the
    # page, clear of both margins, and at coordinates that shift a point or
    # two per page, so it is not stationery and it passed the figure test on
    # all 9 pages. An opinion does not print a figure over the entire sheet it
    # is printed on; where one image covers the page, every other image on
    # that page is part of the same scan.
    _FULL_BLEED = 0.9
    _scan_pages = {
        _pm.number for _pm in model.pages
        for _i in _pm.images
        if ((_i.x1 - _i.x0) * (_i.bottom - _i.top))
        >= _pm.width * _pm.height * _FULL_BLEED}

    from .resolve.headmatter import looks_like_docket as _slug_ld
    for pm in model.pages:
        keep = []
        for line in pm.lines:
            kind = ff.kind(pm, line)
            if kind is None:
                keep.append(line)
            else:
                if kind in ("running-head", "folio") \
                        and line.top < pm.height * 0.14:
                    _t = " ".join(line.plain.split())
                    _d = _slug_ld(_t)
                    if _d and len(_t) < 30:
                        _slug_docket.append(_d)
                    elif (" v. " in _t or _t.endswith(" v.")) \
                            and len(_t) < 70:
                        _slug_case.append(_t)
                doc.dropped.append(m.Dropped(
                    text=line.plain.strip(), prov=m.Prov(pm.number, (line.id,)),
                    kind=kind))
        content_by_page[pm.number] = keep
        if pm.rotated_text:
            doc.dropped.append(m.Dropped(text=pm.rotated_text,
                                         prov=m.Prov(pm.number), kind="rotated"))
        # Page IMAGES: a sizable image INSIDE the body region is a printed
        # FIGURE (adidas's trademark exhibits) — carried into the body as
        # a data URI. Everything else (seals, logo stamps, signature
        # graphics) is surfaced as a KNOWN removal; tiny artifacts
        # (< 20pt a side) stay silent.
        for _im in pm.images:
            _w, _h = _im.x1 - _im.x0, _im.bottom - _im.top
            # AN IMAGE ABOVE ALL THE TYPE IS STATIONERY, not a figure. mo
            # sets its court seal at top 72 of 792 — 9.09%, just past the
            # 0.08 guard — so it was cropped and planted INSIDE the writing,
            # and 45 of mo's 50 opinions opened with the seal (ill's summary
            # sheet does the same at 9.09%). The user, 2026-08-19: "it
            # doesn't need to go into the opinion since it's not part of it
            # … just put it at the top centered of the headmatter".
            _first_text = min((l.top for l in pm.lines if l.plain.strip()),
                              default=0.0)
            # A SEAL IS SMALL. Standing above the type is what makes a
            # graphic stationery rather than a figure, but it does not make
            # it a SEAL: a scanned source carries the whole page as one
            # raster at 0,0, and that image is above the first text row too.
            # virginislands's `3rc__company_inc._v._boynes_trucking_system`
            # had its entire first page cropped and planted at the head of
            # the headmatter. A masthead is a device the court prints at the
            # top of its stationery, so it is bounded — measured against the
            # seals actually in the corpus, no real one comes near half the
            # measure or a quarter of the page's height.
            # …AND A MASTHEAD STANDS IN THE MEASURE. An e-filing stamp is
            # also small and also above the type, but the clerk puts it in a
            # CORNER — virginislands's sits at x0=497 of 612, hard against
            # the right edge. A device the court prints as its own
            # letterhead is centred or set at the left margin, never flush
            # to the far edge, so the graphic's centre must fall in the
            # middle of the page.
            _imid = (_im.x0 + _im.x1) / 2
            _is_masthead = (pm.number == 1 and _im.top <= _first_text
                            and _w <= pm.width * 0.55
                            and _h <= pm.height * 0.25
                            and abs(_imid - pm.width / 2) <= pm.width * 0.35
                            and not _is_stationery(_im))
            _is_figure = (
                _w >= 60 and _h >= 40
                and not _is_masthead
                and not _is_stationery(_im)
                and pm.number not in _scan_pages
                and _im.top > pm.height * 0.08
                and _im.bottom < pm.height * 0.92
                and not (pm.number == model.n_pages
                         and _im.top > pm.height * 0.55))
            if _is_masthead and _w >= 20 and _h >= 20:
                _mastheads.append(_im)
                continue
            # …and the mirror at the foot of the LAST page: an image below
            # every text row there is the court's signature stamp.
            # The floor is the last row of BODY text, not the last row of
            # anything: a chambers template prints the document's own source
            # path under the stamp, which raised the floor above the
            # signature on 8 of kyed's 25 records — and on one the stamp
            # loses to its OWN date row by 3pt. Measured over 2,217 federal
            # district files, this takes signature graphics 107 -> 276:
            # 168 files gain one, none loses one, across 44 courts.
            # THE FLOOR IS THE LAST ROW OF BODY TEXT, not the last row of
            # anything. Anything the furniture pass already classifies —
            # a folio, a running foot, a stamp, a template's own source
            # path — is not body, and counting it raised the floor above
            # the signature it was supposed to find. Stated as "not
            # furniture" rather than naming any one court's habit.
            _sig_floor = max((l.top for l in pm.lines
                              if l.plain.strip()
                              and l.top < pm.height * 0.9
                              and ff.kind(pm, l) is None),
                             default=0.0)
            if (pm.number == model.n_pages and _w >= 60 and _h >= 20
                    and _im.bottom > _sig_floor
                    and _im.top > _sig_floor - 30.0):
                _sig_imgs.append(_im)
                continue
            if _is_figure:
                _figures.append(_im)
            elif _w >= 20 and _h >= 20:
                _what = ("watermark/stationery" if _is_stationery(_im)
                         else "scanned page" if pm.number in _scan_pages
                         else "seal/logo/stamp")
                doc.dropped.append(m.Dropped(
                    text=f"graphic {_w:.0f}×{_h:.0f}pt ({_what})",
                    prov=m.Prov(pm.number), kind="image"))
    # Dedupe repeated furniture for display — but keep EVERY dropped line's
    # identity: the sweep must know page 3's folio was dropped even though
    # only page 2's shows (digitless keys collapse all folios to one entry).
    all_dropped_ids = {i for d in doc.dropped for i in d.prov.line_ids}
    seen: set[tuple[str, str]] = set()
    deduped = []
    for d in doc.dropped:
        key = (d.kind, "".join(c for c in d.text if not c.isdigit()))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(d)
    doc.dropped = deduped

    # 6 footnotes — per-page zones over content lines.
    zones = FootnoteZones(
        model, geom, profile.footnotes, court_id, trace,
        is_byline=lambda t: bool(BylineParser(profile.byline).parse(t)))
    zone_tops: dict[int, float] = {}
    zone_lines_by_page: dict[int, list] = {}
    prev_had = False
    for pm in model.pages:
        decision = zones.page_zone(pm, prev_had_zone=prev_had)
        prev_had = decision.value is not None
        if decision.value is not None:
            zone_tops[pm.number] = decision.value
            keep_ids = {l.id for l in content_by_page[pm.number]}
            zone_lines_by_page[pm.number] = [
                l for l in zones._lines_below(pm, decision.value)
                if l.id in keep_ids]

    # 7 segments — content lines above the zone.
    segmenter = Segmenter(geom, model.pages[0].width,
                          is_author_line=lambda t: bool(
                              BylineParser(profile.byline).parse(t)),
                          para_indent_min=profile.para_indent_min)
    segments_by_page = {}
    for pm in model.pages:
        cut = zone_tops.get(pm.number)
        lines = [l for l in content_by_page[pm.number]
                 if cut is None or l.top < cut]
        segments_by_page[pm.number] = segmenter.segment_page(lines, pm.number)

    # A court whose headmatter is a LAYOUT CONTRACT reads it itself, before
    # assembly. The reader claims only headmatter lines — banner, recital,
    # roster, the rule-fenced caption, the counsel block — and everything
    # below its last landmark is untouched: writings, bylines, footnote
    # zones and paragraph splitting all run exactly as they do for any other
    # court. The claim is SUBTRACTIVE, which is also what stops a panel
    # roster from reading as a byline and opening a phantom writing.
    _court_hm = court_decides("headmatter.read", court_id, trace,
                              model=model, geom=geom)
    if _court_hm is NOTHING:
        _court_hm = None
    _segments_unclaimed = {k: list(v) for k, v in segments_by_page.items()} \
        if _court_hm else None
    if _court_hm:
        # A court that reads its own headmatter also knows what KIND of
        # paper it is — and it knows before assembly, which is where the
        # type decides how writings anchor.
        _claimed = set(_court_hm.get("consumed") or ())
        from .resolve.segments import Segment as _SegHM
        for _pg, _sgs in list(segments_by_page.items()):
            _out = []
            for _sg in _sgs:
                _keep = [l for l in _sg.lines if l.id not in _claimed]
                if _keep:
                    _out.append(_SegHM(_sg.page, _keep, _sg.kind))
            segments_by_page[_pg] = _out


    # 9 body (assembly finds the opinion boundary, which stage 8 needs).
    parser = BylineParser(profile.byline)
    # SYLLABUS PAGES: a court-issued syllabus printed BEFORE the opinion's
    # own caption page (nj's 4-page cover; mich's 'Syllabus' release pages)
    # is the syllabus, not headmatter. A page whose top third sets a
    # standalone 'SYLLABUS' heading opens the block; following pages
    # continue it until a page opens with the court's banner (the real
    # caption page).
    _syl_pages: set[int] = set()
    _syl_open = False
    from .resolve.headmatter import _is_banner_row as _ibr
    for pm in model.pages:
        top_lines = [l for l in pm.lines if l.top < pm.height * 0.4]
        # The heading must OPEN the page (first three rows) — conn sets
        # 'Syllabus' as an interior section heading under the released
        # date, which is that page's apparatus, not a cover.
        first3 = sorted((l for l in pm.lines if l.plain.strip()),
                        key=lambda l: l.top)[:3]
        _big = 3 * (geom.body_size if geom else 12.0)
        has_syl = "syllabus" in profile.front_matter and any(
            " ".join(l.plain.split()).upper() == "SYLLABUS"
            and (l in first3 or (l.size or 0) >= _big)  # mich's watermark
            for l in top_lines)
        has_banner = any(_ibr(l.plain) for l in top_lines)
        if has_syl:
            _syl_open = True
        elif _syl_open and has_banner:
            _syl_open = False
        if _syl_open:
            _syl_pages.add(pm.number)

    # A court whose pages NAME their own section decides its extent outright
    # (scotus sets 'Syllabus' / 'Opinion of the Court' in every running head):
    # the printed page outranks any inference core could make from prose.
    _court_syl = court_decides("syllabus.pages", court_id, trace,
                               model=model, geom=geom)
    if _court_syl is not NOTHING:
        _syl_pages = set(_court_syl)

    # A CLERK'S COVER SHEET names itself. ri prints 'OPINION COVER SHEET'
    # on a trailing page — a label/value grid of case metadata (Written By,
    # Justices, Source of Appeal, Attorneys), never opinion text. Merged
    # into the body it reads as a phantom tail. It is apparatus: route the
    # whole page to headmatter and keep it out of assembly.
    _COVER_TITLES = ("opinion cover sheet", "cover sheet",
                     "order cover sheet")
    _cover_pages: set[int] = set()
    for pm in model.pages:
        first3 = sorted((l for l in pm.lines if l.plain.strip()),
                        key=lambda l: l.top)[:6]
        if any(" ".join(l.plain.split()).lower() in _COVER_TITLES
               for l in first3):
            _cover_pages.add(pm.number)
    _cover_lines = {p: list(segments_by_page.get(p) or [])
                    for p in _cover_pages}
    for p in _cover_pages:
        segments_by_page[p] = []

    def _assemble_with(segs):
        return assemble(model, geom, segs, zones, zone_tops,
                        zone_lines_by_page, parser, vocab, trace,
                        caption_band=sig.get("band"),
                        doc_type=meta.doc_type, syl_pages=_syl_pages,
                        front_matter=profile.front_matter,
                        para_indent_min=profile.para_indent_min,
                        headmatter_claimed=bool(_court_hm))

    assembled = _assemble_with(segments_by_page)
    if _court_hm and not assembled.opinions:
        trace.event("court.claim_no_writing",
                    "; ".join(assembled.warnings[:3]) or "(no warning)")
    # A COURT READER MAY IMPROVE THE HEADMATTER, NEVER COST THE DOCUMENT ITS
    # WRITINGS. A claim removes lines from the stream, and on a record whose
    # body anchors on something inside the claim that leaves nothing to open
    # the writing on. Where that happens the claim is withdrawn whole and
    # core reads the document as it would have without a court file — a
    # headmatter read beautifully is worth nothing beside a lost opinion.
    # …but a document that EXPECTS no body has not lost anything by having
    # none. An errata sheet or a notice is all headmatter, and withdrawing a
    # correct reading from it threw away every row (ca1's five notice
    # records rendered with an empty headmatter).
    _body_expected = meta.doc_type not in m.NO_BODY_EXPECTED
    if (_court_hm and not assembled.opinions and _segments_unclaimed
            and _body_expected):
        # First try RELEASING THE ANCHOR the reader claimed — a doc-type
        # heading the court prints ('SUMMARY ORDER') is both a headmatter row
        # and the only thing an unsigned writing can open on. Released, the
        # headmatter loses one row; withheld, the document loses its opinion.
        _anchor = set(_court_hm.get("anchor_ids") or ())
        if _anchor:
            from .resolve.segments import Segment as _SegA
            _relaxed = {}
            for _pg, _sgs in _segments_unclaimed.items():
                _keep = []
                for _sg in _sgs:
                    _ls = [l for l in _sg.lines
                           if l.id in _anchor or l.id not in _claimed]
                    if _ls:
                        _keep.append(_SegA(_sg.page, _ls, _sg.kind))
                _relaxed[_pg] = _keep
            _try2 = _assemble_with(_relaxed)
            if _try2.opinions:
                trace.event("court.anchor_released",
                            "doc-type heading returned to the stream")
                segments_by_page.clear()
                segments_by_page.update(_relaxed)
                assembled = _try2
        _retry = _assemble_with(_segments_unclaimed) \
            if not assembled.opinions else assembled
        if not assembled.opinions and _retry.opinions:
            trace.event("court.reader_withdrawn",
                        "claim cost the document its writings")
            segments_by_page.clear()
            segments_by_page.update(_segments_unclaimed)
            assembled = _retry
            _court_hm = None
    doc.opinions = assembled.opinions
    doc.dropped.extend(assembled.dropped)
    doc.headmatter_footnotes = assembled.headmatter_footnotes
    doc.warnings.extend(
        w for w in assembled.warnings
        if not (w == "no opinion start found"
                and meta.doc_type in m.NO_BODY_EXPECTED))

    # 8 headmatter — the segments before the first opinion, with two
    # section splits made at SEGMENT level:
    # - counsel: a segment naming representation ('…for the appellant',
    #   'on brief', 'Attorneys for…', 'COUNSEL OF RECORD') is the attorneys
    #   section, whatever court printed it;
    # - syllabus: a multi-line prose run set a clear step SMALLER than the
    #   body before the opinion starts (Connecticut's 8pt syllabus against
    #   an 11pt body) — measured, not configured.
    from .resolve.assemble import _segment_blocks
    # STRONG marks are representation VERBS/labels — they never occur as
    # ordinary prose. WEAK marks ('for the defendant') appear in syllabus
    # prose too, so they only vouch for SHORT blocks (nj's syllabus
    # paragraphs were classifying as counsel on 'for the defendant').
    _COUNSEL_STRONG = ("on brief", "on the brief", "attorneys for",
                       "attorney for", "counsel of record", "appearances",
                       "argued the cause", "appearing for", "pro se,",
                       ", pro se", "no appearance for",
                       "self-represented litigant")
    _COUNSEL_WEAK = ("for the appell", "for appell", "for the pet",
                     "for petition", "for the respond", "for respond",
                     "for plaintiff", "for the plaintiff", "for defendant",
                     "for the defendant", "counsel for")
    _COUNSEL_MARKS = _COUNSEL_STRONG + _COUNSEL_WEAK
    # Publisher boilerplate (Connecticut's slip cover: release-date rules,
    # modification notice, Secretary of the State copyright). A multi-line
    # run hitting TWO OR MORE cues is the notice; the one-line 'officially
    # released <date>' row hits one and survives (it carries the decision
    # date).
    _NOTICE_CUES = ("officially released", "subject to modification",
                    "advance release version", "copyrighted by the secretary",
                    "may not be reproduced", "official legal publications",
                    "in the event of discrepancies",
                    # the reporter-notice family confirmed by the notice
                    # sweep (ala/scotus/ohio/ga/mich/mass/ri/dc/alaska/wis):
                    "subject to formal revision", "reporter of decisions",
                    "advance sheet", "typographical", "formal errors",
                    "constitutes no part of the opinion", "detroit timber",
                    "superseded by the", "subject to further editing",
                    "bound volume", "readers are requested",
                    "before publication in",
                    # nj's syllabus clerk note
                    "prepared by the office of the clerk",
                    "may not summarize all portions",
                    # cal's uncertified-opinion rule
                    "prohibits courts and parties",
                    "not certified for publication",
                    # ca2's summary-order rules block
                    "do not have precedential effect",
                    "must serve a copy",
                    # fla's finality notice
                    "not final until time expires",
                    "disposition thereof if timely filed")
    # COUNSEL PRINTED INSIDE THE HEADMATTER STAYS THERE. Lifting it into a
    # section of its own leaves a hole in the block the render is supposed to
    # reproduce — the appearances vanish from where the page puts them and
    # reappear somewhere else. Their MEANING is copied into criteria instead.
    # The one exception is a court that prints its roster BELOW the writings
    # (ca3's order form); there the roster is not part of the headmatter at
    # all, and `counsel_after_writings` says so.
    _counsel_texts: list[str] = []
    hm_pages: dict[int, list] = {}
    for _cp, _csegs in _cover_lines.items():
        for _cs in _csegs:
            hm_pages.setdefault(_cp, []).extend(_cs.lines)
    history_txt: list[str] = []
    hm_mode = None
    _sum_target = None
    # bands of notice drops (page, top, bottom, x0) — a notice split across
    # segments loses its cue quorum per piece; adjacency reunites it.
    _notice_bands: list[tuple] = []
    _recital_date_found: list[str] = []
    # PUBLICATION STATUS: the cover states it outright — record it as
    # criteria (the row itself stays where the page put it).
    _PUB = ("certified for publication", "for publication",
            "to be published", "publish")
    _UNPUB = ("not to be published", "not for publication",
              "not designated for publication", "unpublished",
              "non-precedential", "do not publish",
              "not certified for publication")
    _pub_status = None
    for pm in model.pages[:2]:
        if _pub_status:
            break
        for line in pm.lines:
            low = " ".join(line.plain.split()).lower().strip(" .*†‡")
            # A STATUS IS A STATEMENT ABOUT THIS PAPER. A sentence that
            # CITES ANOTHER DECISION is about that one instead: mich's
            # Reporter syllabus recites the court below's 'unpublished per
            # curiam opinion issued on …' (17 of mich's 50 PUBLISHED slips
            # came back unpublished), idaho's majority cites 'State v.
            # Borek, No. 49021, 2022 WL 4295418', wis cites an 'unpublished
            # order at 5-10'. Length is NOT the discriminator — ca5 states
            # its own status in 70 characters ('* This opinion is not
            # designated for publication. See 5th Cir. R. 47.5.') and that
            # one is true.
            if len(low) > 200 or _STATUS_CITES_ANOTHER.search(low):
                continue
            if any(low.startswith(u) or u in low[:60] for u in _UNPUB):
                _pub_status = "unpublished"
                break
            if any(low == p0 or low.startswith(p0 + " in")
                   for p0 in _PUB) or low == "publish":
                _pub_status = "published"
                break

    # A counsel COLUMN's continuation may segment separately (guam's right
    # column runs two rows past the left, markless): a following segment
    # whose lines all sit on one of the counsel segment's column edges,
    # within a couple of leads, is the same block.
    from .resolve.segments import Segment as _SegM
    _msegs: list = []
    for seg in assembled.headmatter_segments:
        if _msegs:
            prev = _msegs[-1]
            ptext = " ".join(l.plain for l in prev.lines).lower()
            pxs = {round(p.x0) for p in prev.lines}
            if (seg.page == prev.page
                    and any(mk in ptext for mk in _COUNSEL_MARKS)
                    and seg.lines[0].top - max(p.top for p in prev.lines)
                        <= 2.2 * (geom.lead if geom else 16.0)
                    and all(any(abs(l.x0 - px) <= 3 for px in pxs)
                            for l in seg.lines)):
                _msegs[-1] = _SegM(prev.page, list(prev.lines) + list(seg.lines),
                                   prev.kind)
                continue
            # FORWARD address merge: an appearance runs on as short
            # address rows ('[ARGUED] / J. Chris White / Clark Hill /
            # 1400 Wewatta Street / Suite 550 / Denver, Colorado 80202' —
            # ca3's front roster mixes marked and unmarked rows).
            from .resolve.headmatter import find_date as _fd0
            _seg_one = " ".join(
                " ".join(l.plain.split()) for l in seg.lines).strip()
            _is_date_row = (len(seg.lines) == 1 and len(_seg_one) <= 34
                            and _fd0(_seg_one) is not None)
            ptext2 = " ".join(l.plain for l in prev.lines).lower()
            _adjacent = (not _is_date_row and seg.page == prev.page
                         and seg.lines[0].top
                             - max(p.top for p in prev.lines)
                             <= 2.5 * (geom.lead if geom else 16.0))
            # …or the block WRAPS the page: continuation opens the next
            # page's top (ca2's 'FOR RESPONDENT:' roster runs on).
            _wraps = (seg.page == prev.page + 1
                      and seg.lines[0].top
                          < model.pages[seg.page - 1].height * 0.22)
            if ((_adjacent or _wraps)
                    and (any(mk in ptext2 for mk in _COUNSEL_MARKS)
                         or "[argued]" in ptext2)
                    and all(len(l.plain.strip()) <= 55 for l in seg.lines)
                    and len(seg.lines) <= 8
                    and (any(c.isdigit() for c in " ".join(
                            l.plain for l in seg.lines))
                         or "[argued]" in " ".join(
                            l.plain for l in seg.lines).lower()
                         # an address tail may be digit-free ('…Civil
                         # Division, United / States Department of
                         # Justice, Washington, DC.')
                         or sum(l.plain.count(",") for l in seg.lines) >= 2)
                    and not any(
                        l.plain.strip().rstrip(".").isupper()
                        and len(l.plain.strip()) > 3 for l in seg.lines)):
                _msegs[-1] = _SegM(prev.page,
                                   list(prev.lines) + list(seg.lines),
                                   prev.kind)
                continue
            # BACKWARD merge: a counsel segment OPENING mid-sentence owns
            # the torn first line(s) above it — nh wraps 'Rath, Young…
            # (Adam Pignatelli on the / brief and orally), for the
            # petitioner.' and the marks all sit on the continuation. The
            # torn edge shows as the PREVIOUS line ending mid-clause — a
            # trailing INITIAL ('…Graham W.') is not a sentence terminal
            # (nh ortolano's continuation opens on a capitalized surname).
            def _open_edge(s: str) -> bool:
                if not s:
                    return False
                if not s.endswith((".", ":", ";", "”", '"', ")")):
                    return True
                return bool(len(s) >= 2 and s.endswith(".")
                            and s[-2].isupper()
                            and (len(s) == 2 or not s[-3].isalpha()))
            stext = " ".join(l.plain for l in seg.lines).lower()
            first = seg.lines[0].plain.strip()
            plast = prev.lines[-1].plain.strip()
            if (seg.page == prev.page
                    and (any(mk in stext for mk in _COUNSEL_MARKS)
                         # ANY mid-sentence opening under an open edge is
                         # the same tear (ca2 griffin's disposition
                         # paragraph split half-into-headmatter)
                         or first[:1].islower())
                    and plast and not plast.endswith((":", ";"))
                    and _open_edge(plast)
                    and len(prev.lines) <= 4
                    and seg.lines[0].top - max(p.top for p in prev.lines)
                        <= 2.2 * (geom.lead if geom else 16.0)):
                merged = _SegM(prev.page,
                               list(prev.lines) + list(seg.lines),
                               seg.kind)
                _msegs[-1] = merged
                # CHAIN back: the paragraph may wrap over SEVERAL markless
                # lines ('Upton & Hatfield… on the / memorandum of law) and
                # City of Nashua…, of / Nashua (…' — nh); keep absorbing
                # open-edged short neighbors above.
                while (len(_msegs) >= 2
                       and len(merged.lines) <= 8
                       and _msegs[-2].page == merged.page
                       and len(_msegs[-2].lines) <= 4
                       and _open_edge(
                           _msegs[-2].lines[-1].plain.strip())
                       and merged.lines[0].top
                           - max(p.top for p in _msegs[-2].lines)
                           <= 2.2 * (geom.lead if geom else 16.0)):
                    merged = _SegM(merged.page,
                                   list(_msegs[-2].lines) + list(merged.lines),
                                   merged.kind)
                    _msegs[-2:] = [merged]
                continue
        _msegs.append(seg)

    # A syllabus paragraph may OPEN on the caption page and break onto the
    # first SYLLABUS page mid-sentence (ca2 verplanck): the unterminated
    # tail before the syllabus belongs to the syllabus.
    _syl_pull: set[int] = set()
    # …and the PROSE-branch variant: a full-measure syllabus paragraph
    # opening lowercase under an open-edged paragraph half (the page break
    # tore one syllabus paragraph in two). Only where the court LABELED a
    # syllabus page — otherwise this is ordinary body prose (ca5's en banc
    # majority was pulled into a fabricated syllabus).
    for _a, _b in zip(_msegs, _msegs[1:]) if _syl_pages else ():
        if not geom or _b.page - _a.page > 1 or len(_b.lines) < 4:
            continue
        if sum(l.width for l in _b.lines) / len(_b.lines) \
                < 0.75 * geom.column:
            continue
        _bj = " ".join(l.plain.strip() for l in _b.lines).strip()
        _bfirst = _b.lines[0].plain.strip()
        _alast = _a.lines[-1].plain.strip()
        if (_bj[-1:] in '.!?”"' and _bfirst[:1].islower()
                and len(_a.lines) >= 3
                and sum(l.width for l in _a.lines) / len(_a.lines)
                    >= 0.6 * geom.column
                and _alast and not _alast.endswith(
                    (".", ":", "!", "?", "”", '"', ";"))):
            _syl_pull.add(id(_a))
    if _syl_pages:
        _P = min(_syl_pages)
        _prevsegs = [s for s in _msegs if s.page == _P - 1]
        _nextsegs = [s for s in _msegs if s.page == _P]
        if _prevsegs and _nextsegs:
            _plast = _prevsegs[-1].lines[-1].plain.strip()
            _nfirst = next((l.plain.strip() for s in _nextsegs
                            for l in s.lines if l.plain.strip()), "")
            if (_nfirst[:1].islower() and _plast
                    and not _plast.endswith(
                        (".", ":", "!", "?", '"', "”", ";"))):
                _syl_pull.add(id(_prevsegs[-1]))

    # Cover apparatus a court prints AGAIN at the head of its opinion: the
    # court names those rows, core drops them (after mining their criteria).
    _syl_drop = court_decides("syllabus.trim", court_id, trace,
                              segs=_msegs, syl_pages=_syl_pages)
    if _syl_drop is NOTHING:
        _syl_drop = set()
    # The court's own UNSIGNED writing: a disposition that stands between the
    # caption and the first byline is the Court speaking, not a caption row.
    _order_segs = court_decides("writing.unsigned", court_id, trace,
                                segs=_msegs, syl_pages=_syl_pages,
                                is_byline=lambda t: bool(parser.parse(t)))
    if _order_segs is NOTHING:
        _order_segs = set()
    _order_blocks: list = []

    for seg in _msegs:
        text = " ".join(l.plain for l in seg.lines).lower()
        plain_one = " ".join(text.split())
        # A STANDALONE publication-status banner is removed content — the
        # fact lives in criteria ('CERTIFIED FOR PUBLICATION' — calctapp).
        _one = plain_one.strip(" .*†‡")
        if len(seg.lines) <= 2 and len(_one) < 80 and (
                any(_one.startswith(u) for u in _UNPUB)
                or any(_one == p0 or _one.startswith(p0 + " in")
                       for p0 in _PUB)):
            doc.dropped.append(m.Dropped(
                text=" ".join(l.plain.strip() for l in seg.lines),
                prov=m.Prov(seg.page, tuple(l.id for l in seg.lines)),
                kind="status"))
            continue
        if len(seg.lines) >= 2 and sum(
                1 for cue in _NOTICE_CUES if cue in text) >= 2:
            doc.dropped.append(m.Dropped(
                text=" ".join(l.plain.strip() for l in seg.lines)[:1200],
                prov=m.Prov(seg.page, tuple(l.id for l in seg.lines)),
                kind="notice"))
            _notice_bands.append((seg.page,
                                  min(l.top for l in seg.lines),
                                  max(l.top for l in seg.lines),
                                  min(l.x0 for l in seg.lines)))
            continue
        if _order_segs and any(l.id in _order_segs for l in seg.lines):
            # The closing caption row and the disposition it introduces may
            # share a segment — take the order LINES and leave the rest of
            # the segment to the headmatter it belongs to.
            _olines = [l for l in seg.lines if l.id in _order_segs]
            _ohead = [l for l in seg.lines if l.id not in _order_segs]
            if _ohead:
                hm_pages.setdefault(seg.page, []).extend(_ohead)
            from .resolve.segments import Segment as _SegOrd
            _order_blocks.extend(_segment_blocks(
                _SegOrd(seg.page, _olines, "body"), segmenter, vocab))
            continue
        # A segment on a SYLLABUS page is syllabus flow, wherever its shape
        # would otherwise route it (nj cover pages rendered as 120 hmrows).
        if seg.page in _syl_pages or id(seg) in _syl_pull:
            if id(seg) in _syl_drop:
                # Dropped from the render, but still read for criteria
                # below — the cover states facts the reprint omits.
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in seg.lines),
                    prov=m.Prov(seg.page, tuple(l.id for l in seg.lines)),
                    kind="superfluous"))
                continue
            # An INSET paragraph in syllabus flow is still a paragraph —
            # the same fact conn's wholly-inset syllabus proves below; the
            # cover's first paragraph measures narrower than the rules over
            # it and the segmenter types it a quote.
            doc.syllabus.extend(
                m.Paragraph(text=b.text, prov=b.prov)
                if isinstance(b, m.Blockquote) else b
                for b in _segment_blocks(seg, segmenter, vocab,
                                         inset_flow=True))
            continue
        # The CONVENING RECITAL ('At a stated term of the United States
        # Court of Appeals…, on the 10th day of June, two thousand
        # twenty-six.') is formal apparatus carrying the DECISION DATE —
        # ca2's summary orders state it nowhere else (v1 lesson).
        if plain_one.lower().startswith("at a stated term"):
            from .resolve.headmatter import recital_date as _rd
            # The segmenter may glue the NEXT block's first line onto the
            # recital ('PRESENT: …' rode along) — the recital ends at its
            # own terminal sentence.
            _cut = len(seg.lines)
            _acc = ""
            for _i, _l in enumerate(seg.lines):
                _acc += " " + _l.plain
                if "day of" in _acc.lower() \
                        and _l.plain.strip().endswith("."):
                    _cut = _i + 1
                    break
            _head, _rest = seg.lines[:_cut], seg.lines[_cut:]
            _d = _rd(" ".join(l.plain.strip() for l in _head))
            if _d and doc.criteria.decision_date is None:
                _recital_date_found.append(_d)
            doc.dropped.append(m.Dropped(
                text=" ".join(l.plain.strip() for l in _head)[:400],
                prov=m.Prov(seg.page, tuple(l.id for l in _head)),
                kind="recital"))
            if _rest:
                hm_pages.setdefault(seg.page, []).extend(_rest)
            continue
        # 'Procedural History' (Connecticut's syllabus apparatus): the run
        # under the heading is the case's prior history.
        if plain_one.rstrip(" :") == "procedural history":
            hm_mode = "history"
            doc.syllabus.extend(_segment_blocks(seg, segmenter, vocab))
            continue
        # A STANDALONE DATE ROW is the decision date wherever the court
        # sets it — ca1 prints it under the counsel block, below a clear
        # separator; it is never an appearance. (Not while a labeled
        # section is open: its prose owns the run.)
        if hm_mode is None and len(seg.lines) == 1 and len(plain_one) <= 34:
            from .resolve.headmatter import find_date as _fd1
            _dt1 = _fd1(plain_one)
            if _dt1 and _dt1.lower() == plain_one.strip().lower():
                if doc.criteria.decision_date is None:
                    doc.criteria.decision_date = _dt1
                    _recital_date_found.append(_dt1)
                hm_pages.setdefault(seg.page, []).extend(seg.lines)
                continue
        # A 'COUNSEL' / 'APPEARANCES' SECTION HEADING is the court's own
        # signal (arizctapp prints it over the roster): everything under
        # it is attorneys until the next heading.
        if plain_one.rstrip(" :").upper() in (
                "COUNSEL", "APPEARANCES", "ATTORNEYS",
                "COUNSEL OF RECORD", "ATTORNEYS AND LAW FIRMS"):
            # The court's own COUNSEL heading stays in the headmatter with
            # the roster it heads — both are printed there.
            hm_mode = "counsel"
            _counsel_texts.append(" ".join(
                l.plain.strip() for l in seg.lines))
            hm_pages.setdefault(seg.page, []).extend(seg.lines)
            continue
        # A 'SUMMARY' / 'SYLLABUS' SECTION HEADING (ca9 sets its staff
        # summary under a bold 'SUMMARY*'): everything under it is the
        # syllabus until the next section heading.
        _band_now = sig.get("band") or (0.0, 0.0)
        _fm_kind = plain_one.rstrip(" :*†‡∗⁎﹡＊").lower()
        if (_fm_kind in profile.front_matter
                # only a heading BELOW the caption opens a section (ca9's
                # SUMMARY after the roster); scotus's page-1 'Syllabus'
                # TITLE above the caption is the cover's own apparatus.
                and (seg.page > 1 or seg.lines[0].top > _band_now[1])):
            hm_mode = "syllabus"
            # the section carries the COURT'S OWN LABEL: 'SUMMARY' is a
            # staff summary, 'SYLLABUS' the formal syllabus
            _sum_target = (doc.summary if _fm_kind == "summary"
                           else doc.syllabus)
            _sum_target.append(m.Heading(
                text=" ".join(l.plain.strip() for l in seg.lines),
                prov=m.Prov(seg.page, tuple(l.id for l in seg.lines))))
            continue
        if hm_mode == "syllabus":
            if seg.kind == "separator":
                hm_pages.setdefault(seg.page, []).extend(seg.lines)
                continue
            _letters2 = [c for c in plain_one if c.isalpha()]
            # a CAPS row closes the section only if it is a section
            # heading — a running head ('REGES V. CAUCE') is furniture
            # that survived, and a party line is not a heading
            _looks_head = (_letters2 and all(c.isupper() for c in _letters2)
                           and len(plain_one) < 60
                           and " v. " not in plain_one.lower()
                           and " v " not in plain_one.lower())
            # A section heading names what FOLLOWS: 'OPINION' (the body),
            # 'COUNSEL' (the roster). Anything else — including a caps
            # topic line inside the summary — keeps the summary open.
            _closer = plain_one.rstrip(" :*†‡∗⁎﹡＊").upper() in (
                "OPINION", "ORDER", "MEMORANDUM", "PER CURIAM",
                "OPINION OF THE COURT", "COUNSEL", "APPEARANCES")
            # A counsel mark closes the section only from a SHORT block:
            # summary prose says 'judgment for defendant' in passing.
            _counselish = (len(plain_one) <= 400
                           and any(mk in text for mk in _COUNSEL_MARKS))
            if (_closer
                    or text.startswith(("counsel", "appearances"))
                    or _counselish):
                hm_mode = None   # falls through to the counsel routing
            else:
                _sum_target.extend(
                    m.Paragraph(text=b.text, prov=b.prov)
                    if isinstance(b, m.Blockquote) else b
                    for b in _segment_blocks(seg, segmenter, vocab))
                continue
        if hm_mode == "counsel":
            if seg.kind == "separator":
                # a typed rule inside the roster is the page's own divider
                hm_pages.setdefault(seg.page, []).extend(seg.lines)
                continue
            _letters = [c for c in plain_one if c.isalpha()]
            _capsish = _letters and all(
                c.isupper() for c in _letters) and len(plain_one) < 60
            if _capsish or plain_one.lower().startswith(
                    ("before", "present")):
                hm_mode = None   # the next heading/roster ends the section
            else:
                doc.attorneys.extend(
                    _segment_blocks(seg, segmenter, vocab))
                continue
        _weak_hits = sum(1 for mark in _COUNSEL_WEAK if mark in text)
        is_counsel = (any(mark in text for mark in _COUNSEL_STRONG)
                      or (_weak_hits and len(plain_one) <= 300)
                      # TWO distinct weak marks is a roster whatever its
                      # length ('…for Plaintiffs and Appellants.' + '…for
                      # Defendant and Appellant…' — calctapp's block).
                      or _weak_hits >= 2)
        # A DISTRIBUTION line is not an appearance ('Dated: … cc: All
        # Counsel of Record' — the clerk's routing note).
        import re as _rcc
        if is_counsel and (_rcc.search(r"\bcc\s*:", text)
                           or "all counsel of record" in text):
            is_counsel = False
        # …and a brief CITATION is not an appearance (see the trailing
        # roster pass below): weak marks alone cannot carry a block whose
        # role phrase belongs to 'Brief for Respondent 26.'
        if (is_counsel and not any(mk in text for mk in _COUNSEL_STRONG)
                and _rcc.search(r"\bbriefs?\s+(?:for|of)\b|"
                                r"\breply\s+brief\b", text)):
            is_counsel = False
        if hm_mode == "history" and not is_counsel and len(plain_one) > 40:
            doc.syllabus.extend(_segment_blocks(seg, segmenter, vocab))
            from .audit import strip_tags, unescape_xml
            history_txt.append(unescape_xml(strip_tags(
                " ".join(l.plain.strip() for l in seg.lines))))
            continue
        if hm_mode == "history":
            hm_mode = None   # history mode ends at its first non-match
        if is_counsel:
            # PEEL leading history sentences off the counsel block: NJ sets
            # 'On appeal from the Superior Court…, Docket No. L-4133-23.'
            # in the same segment as 'X argued the cause for appellant…' —
            # the appeal-from line is PRIOR HISTORY, never counsel.
            _LEADS = ("on appeal from", "appeal from", "on certification",
                      "before judge")
            def _terminated(s: str) -> bool:
                # '…Tamara L.' ends on an INITIAL, not a sentence — the
                # appeal-from wrap continues ('Mosbarger, Judge.').
                if not s.endswith("."):
                    return False
                return not (len(s) >= 2 and s[-2].isupper()
                            and (len(s) == 2 or not s[-3].isalpha()))
            lines = list(seg.lines)
            peeled = []
            while lines:
                head = " ".join(lines[0].plain.split())
                if not head.lower().startswith(_LEADS) and not (
                        peeled and not _terminated(" ".join(
                            peeled[-1].plain.split()))):
                    break
                peeled.append(lines.pop(0))
            if peeled:
                hm_pages.setdefault(seg.page, []).extend(peeled)
                from .audit import strip_tags, unescape_xml
                history_txt.append(unescape_xml(strip_tags(
                    " ".join(l.plain.strip() for l in peeled))))
            # And LINE-LEVEL: a panel roster or a bare disposition inside
            # the counsel segment ('Before MCLEESE and SHANKER, Associate
            # Judges…' — dc; 'Affirmed.' — conn) is never counsel.
            _kept = []
            _roster_open = False
            # a TYPED RULE fencing the block belongs to the page's
            # furniture, not to the roster text (ca6 fences COUNSEL with
            # '________' above and below)
            from .pdfio.rules import is_typed_rule as _itr
            _rules_out = [_l for _l in lines if _itr(_l.plain.strip())]
            _no_rules = [_l for _l in lines if not _itr(_l.plain.strip())]
            if _no_rules:
                # the fence renders where the page drew it — never dropped
                hm_pages.setdefault(seg.page, []).extend(_rules_out)
                lines = _no_rules
            for _l in lines:
                _one = " ".join(_l.plain.split())
                _lw = _one.lower()
                # A roster may WRAP across rows ('Before' / 'Montecalvo,
                # Thompson, and Aframe,' / 'Circuit Judges.' — ca1): the
                # opener starts it, a judicial-title row closes it.
                if _roster_open:
                    hm_pages.setdefault(seg.page, []).append(_l)
                    if (_one.rstrip().endswith(".")
                            or _lw.rstrip(".").endswith(
                                ("judges", "justices", "judge", "justice",
                                 "jj", "j"))):
                        _roster_open = False
                    continue
                if (_lw.startswith(("before judge", "before the honorable",
                                    "before:"))
                        or (_lw.startswith("before ") and len(_one) <= 95
                            and _one.rstrip().endswith("."))):
                    hm_pages.setdefault(seg.page, []).append(_l)
                    continue
                if _lw.rstrip(":") == "before" or (
                        _lw.startswith("before ") and len(_one) <= 95
                        and not _one.rstrip().endswith(".")):
                    hm_pages.setdefault(seg.page, []).append(_l)
                    _roster_open = True
                    continue
                if _lw.rstrip(".") in ("affirmed", "reversed", "vacated",
                                       "dismissed", "dismissal affirmed",
                                       "reversed; further proceedings"):
                    history_txt.append(_one)
                    hm_pages.setdefault(seg.page, []).append(_l)
                    continue
                _kept.append(_l)
            lines = _column_order(_kept)
            if lines is not _kept:
                # Columns fired: an ADDRESS ROSTER sets one fact per line
                # ('Vincent Leon Guerrero, Esq.' / 'Attorney at Law' / …) —
                # paragraph-joining garbles it (guam); render line-per-line.
                from .resolve.footnotes import line_markup as _lm
                _counsel_texts.extend(
                    _lm(l).strip() for l in lines if _lm(l).strip())
                hm_pages.setdefault(seg.page, []).extend(lines)
            elif lines:
                from .resolve.segments import Segment as _Seg
                _counsel_texts.extend(
                    " ".join(l.plain.split()) for l in lines
                    if l.plain.strip())
                hm_pages.setdefault(seg.page, []).extend(lines)
            continue
        cap_band = sig.get("band") or (0.0, 0.0)
        in_cap_band = (seg.page == 1
                       and any(cap_band[0] - 4 <= l.top <= cap_band[1] + 4
                               for l in seg.lines))
        if (geom and len(seg.lines) >= 3 and not in_cap_band
                and all(l.size <= geom.body_size - 1.5 for l in seg.lines)
                and sum(l.width for l in seg.lines) / len(seg.lines)
                    >= 0.5 * geom.column
                # sub-body type is the evidence, but only BEFORE the body
                # begins: a labeled page, or no writing found yet
                and (seg.page in _syl_pages
                     # Where the court LABELS its syllabus pages, the label
                     # is the boundary — reduced type on an UNLABELED page is
                     # the writing's own headmatter (scotus reprints banner,
                     # docket, caption and date at the head of each writing),
                     # never a continuation of the syllabus.
                     or (not _syl_pages
                         and (not assembled.opinions
                              or seg.page <= min((o.blocks[0].prov.page
                                                  for o in assembled.opinions
                                                  if o.blocks),
                                                 default=10**6))))):
            # conn's whole syllabus is INSET, so the segmenter types its
            # headnote paragraphs as blockquotes — in sub-body syllabus
            # flow an indented paragraph is just a paragraph.
            doc.syllabus.extend(
                m.Paragraph(text=b.text, prov=b.prov)
                if isinstance(b, m.Blockquote) else b
                for b in _segment_blocks(seg, segmenter, vocab,
                                         inset_flow=True))
            continue
        # A BODY-SIZE court-written summary: a full-measure PROSE run in the
        # front matter (tenn sets its syllabus at body size between the
        # docket rules and the disposition). Prose, not caption: ≥4 lines
        # averaging ≥75% of the measure, closing on sentence punctuation.
        joined = " ".join(l.plain.strip() for l in seg.lines).strip()
        if (geom and len(seg.lines) >= 4 and not in_cap_band
                and sum(l.width for l in seg.lines) / len(seg.lines)
                    >= 0.75 * geom.column
                and joined[-1:] in ".!?”\""):
            # UNLABELED front prose is a SUMMARY only on a page the court
            # LABELED (syllabus/summary page); otherwise it is the body,
            # and inventing a section for it hides a missed opinion start
            # (ca5's en banc majority landed in a fabricated summary).
            if seg.page in _syl_pages or id(seg) in _syl_pull:
                (doc.syllabus if seg.page in _syl_pages
                 else doc.summary).extend(
                    _segment_blocks(seg, segmenter, vocab))
                continue
        hm_pages.setdefault(seg.page, []).extend(seg.lines)
    # The unsigned disposition opens the document's writings: the signed
    # opinions that follow it concur in or dissent FROM it.
    if _order_blocks:
        doc.opinions.insert(0, m.Opinion(
            type="per curiam", author="",
            author_prov=m.Prov(_order_blocks[0].prov.page),
            blocks=_order_blocks))
    # LINE-LEVEL notice peel: a notice set inside the caption band never
    # reaches the segment check above (mich's syllabus note sits between
    # masthead rows). Group hm lines by top-proximity AND shared left edge
    # (so a letterhead's right column can't be swept up), and drop any
    # multi-line group hitting two cues.
    for pg, pg_lines in hm_pages.items():
        groups: list[list] = []
        for l in sorted(pg_lines, key=lambda l: (l.top, l.x0)):
            # last COMPATIBLE group: an interleaved right-column row (the
            # letterhead beside mich's note) must not break the run.
            for g in reversed(groups):
                if (l.top - g[-1].top <= 24
                        and abs(l.x0 - g[0].x0) <= 40) or (
                        # a row-mate CONTINUATION cell ('NOTICE:' + ' This
                        # opinion is subject…' split at the label) joins its
                        # row; a distant letterhead cell (gap > 50) does not.
                        l.top - g[-1].top < 2
                        and 0 <= l.x0 - g[-1].x1 <= 50) or (
                        # a BOX centers its rows (ca10's FILED stamp):
                        # shared center axis, looser leading.
                        l.top - g[-1].top <= 34
                        and abs((l.x0 + l.x1) - (g[0].x0 + g[0].x1)) <= 40):
                    g.append(l)
                    break
            else:
                groups.append([l])
        def _is_stamp_group(g: list) -> bool:
            # A filing-stamp BLOCK: short rows only, anchored by
            # 'Electronically Filed' (haw's e-file header) or a bare
            # 'FILED' row plus a 'Clerk of Court' row (ca10's margin box).
            if len(g) < 3 or any(len(l.plain.strip()) > 48 for l in g):
                return False
            gt = " ".join(l.plain for l in g).lower()
            if "electronically filed" in gt:
                return True
            has_filed = any(l.plain.strip().rstrip(":").upper() == "FILED"
                            for l in g)
            return has_filed and "clerk of court" in gt

        held: list[list] = []
        for g in groups:
            gt = " ".join(l.plain for l in g).lower()
            cues = sum(1 for cue in _NOTICE_CUES if cue in gt)
            if _is_stamp_group(g):
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in g)[:1200],
                    prov=m.Prov(pg, tuple(l.id for l in g)),
                    kind="stamp"))
                hm_pages[pg] = [l for l in hm_pages[pg] if l not in g]
            elif len(g) >= 2 and cues >= 2:
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in g)[:1200],
                    prov=m.Prov(pg, tuple(l.id for l in g)),
                    kind="notice"))
                _notice_bands.append((pg, min(l.top for l in g),
                                      max(l.top for l in g),
                                      min(l.x0 for l in g)))
                hm_pages[pg] = [l for l in hm_pages[pg] if l not in g]
            elif len(g) >= 2 and cues >= 1:
                held.append(g)
        # A 1-cue multi-line group ABUTTING a dropped notice (same left
        # edge, within a leading or two) is the notice's other half — ri's
        # 'NOTICE: This opinion is subject to formal revision' row sits in
        # the caption segment while its tail dropped at segment level.
        for g in held:
            g_top = min(l.top for l in g)
            g_bot = max(l.top for l in g)
            g_x0 = min(l.x0 for l in g)
            if any(p == pg and abs(g_x0 - x0) <= 40
                   and (abs(g_top - bot) <= 28 or abs(top - g_bot) <= 28)
                   for p, top, bot, x0 in _notice_bands):
                doc.dropped.append(m.Dropped(
                    text=" ".join(l.plain.strip() for l in g)[:1200],
                    prov=m.Prov(pg, tuple(l.id for l in g)),
                    kind="notice"))
                hm_pages[pg] = [l for l in hm_pages[pg] if l not in g]
    span = [(pm, hm_pages[pm.number]) for pm in model.pages
            if pm.number in hm_pages]
    if _court_hm:
        # The court read its own headmatter — publish it verbatim.
        doc.headmatter = list(_court_hm.get("items") or [])
        for _k, _v in (_court_hm.get("criteria") or {}).items():
            setattr(doc.criteria, _k, _v)
        doc.attorneys.extend(_court_hm.get("attorneys") or [])
        doc.dropped.extend(_court_hm.get("dropped") or [])
        doc.summary.extend(_court_hm.get("summary") or [])
        # …and ANY HEADMATTER LINE THE READER DID NOT TAKE still gets placed
        # by the shared walk. A court reader states what it recognizes; what
        # it passes over is not thereby junk, and dropping the shared walk
        # entirely orphaned those lines into residual content (ca2's counsel
        # continuations on page 2, an immigration caption the ladder does not
        # cover). The court's CRITERIA stand — only placement is topped up.
        if span:
            _rest = read_headmatter(span, sig, cap_style, geom, trace,
                                    court_id,
                                    caption_wraps=profile.caption_wraps)
            doc.headmatter.extend(_rest.items)
    elif span:
        hm = read_headmatter(span, sig, cap_style, geom, trace, court_id,
                             caption_wraps=profile.caption_wraps)
        doc.headmatter = hm.items
        doc.criteria = hm.criteria
    if _recital_date_found and doc.criteria.decision_date is None:
        doc.criteria.decision_date = _recital_date_found[0]
    if _slug_docket and doc.criteria.docket_number is None:
        doc.criteria.docket_number = _slug_docket[0]
    if _slug_case and not doc.criteria.parties:
        _sides = [x.strip() for x in _slug_case[0].split(" v. ") if x.strip()]
        if len(_sides) == 2:
            doc.criteria.parties = _sides
    if _pub_status and doc.criteria.publication_status is None:
        doc.criteria.publication_status = _pub_status
    # Page-break tears inside the SYLLABUS flow: a continuation coming
    # back as a Blockquote (an indented rail reads as a quote) or a
    # lowercase Paragraph is the SAME paragraph (conn splits its syllabus
    # at every page turn).
    for _sec_name in ("syllabus", "summary"):
      doc_sec = getattr(doc, _sec_name)
      if doc_sec:
        from .audit import strip_tags as _st3
        _mg: list = []
        for _b in doc_sec:
            _prev_txt = (_st3(getattr(_mg[-1], "text", "") or "").rstrip()
                         if _mg and isinstance(_mg[-1], m.Paragraph) else "")
            _nxt_txt = (_st3(getattr(_b, "text", "") or "").lstrip()
                        if isinstance(_b, (m.Paragraph, m.Blockquote))
                        and getattr(_b, "text", None) else "")
            # A closing quote is terminal only if the sentence ended
            # INSIDE it: 'so ordered.”' closes, 'an “inchoate offense,”'
            # does not — the comma is the page turn's own evidence that
            # the sentence runs on (scotus tears mid-quotation).
            _end = _prev_txt[-1:]
            _terminal = (_end in '.!?:;'
                         or (_end in '"”’'
                             and _prev_txt[-2:-1] not in ',;'))
            if (_prev_txt and _nxt_txt and not _terminal
                    and _nxt_txt[:1].islower()):
                _pv = _mg[-1]
                _mg[-1] = m.Paragraph(
                    text=_pv.text.rstrip() + " " + _b.text.lstrip(),
                    prov=m.Prov(_pv.prov.page,
                                tuple(_pv.prov.line_ids)
                                + tuple(_b.prov.line_ids)))
            else:
                _mg.append(_b)
        setattr(doc, _sec_name, _mg)

    # Criteria the SYLLABUS pages carry (nj's cover holds the docket and
    # the argued/decided line; those pages bypass read_headmatter).
    if doc.syllabus or doc.summary:
        import re as _re2
        from .audit import strip_tags as _st2
        from .resolve.headmatter import date_row_value as _drv
        from .resolve.headmatter import find_date as _fd2
        from .resolve.headmatter import looks_like_docket as _ld2
        _re_syl = _re2.compile(r"\(([A-Z]{1,2}-\d{1,4}-\d{2,4})\)")
        _crit_rows = [getattr(b, "text", "") or ""
                      for b in (list(doc.syllabus) + list(doc.summary))[:60]]
        # A cover row dropped as SUPERFLUOUS still speaks: where the court
        # reprints its caption at the head of the opinion, the reprint omits
        # the argued date, which the cover states once (scotus).
        _crit_rows += [dp.text for dp in doc.dropped
                       if dp.kind == "superfluous"]
        for _row_text in _crit_rows:
            t = " ".join(_st2(_row_text).split())
            if not t:
                continue
            low = t.lower()
            # the released date may sit INSIDE a long syllabus paragraph
            # (conn joins 'Argued January 13—officially released
            # February 17, 2026*' into the flow)
            if (doc.criteria.decision_date is None
                    and "officially released" in low):
                d = _fd2(t[low.index("officially released"):][:80])
                if d:
                    doc.criteria.decision_date = d
            if len(t) > 300:
                continue
            if doc.criteria.docket_number is None:
                mm = _re_syl.search(t)
                if mm:
                    doc.criteria.docket_number = mm.group(1)
                else:
                    d0 = _ld2(t)
                    if d0:
                        doc.criteria.docket_number = d0
            if doc.criteria.decision_date is None:
                d = _drv(t) or (_fd2(t[low.index("decided"):])
                                if "decided" in low else None)
                if d:
                    doc.criteria.decision_date = d
            if doc.criteria.submitted is None and "argued" in low:
                d = _fd2(t[low.index("argued"):low.index("decided")
                           if "decided" in low else len(t)])
                if d:
                    doc.criteria.submitted = d
    # DISPOSITION marker: ca9 closes the majority with a bold standalone
    # 'REMANDED.' / 'AFFIRMED in part…' — keep it in the opinion, mark it,
    # and publish it as criteria for downstream parsing.
    _DISPO_LEADS = ("AFFIRMED", "REVERSED", "REMANDED", "VACATED",
                    "DISMISSED", "GRANTED", "DENIED", "PETITION")
    if doc.opinions:
        from .audit import strip_tags as _std
        for _op in doc.opinions:
            for _b in _op.blocks[-3:]:
                _t = _std(getattr(_b, "text", "") or "").strip()
                if (_t and len(_t) < 200
                        and _t.split()[0].rstrip(".,;").upper()
                            in _DISPO_LEADS
                        and _t.split()[0].rstrip(".,;").isupper()):
                    try:
                        _b.role = "disposition"
                    except Exception:
                        pass
                    if doc.criteria.disposition is None:
                        doc.criteria.disposition = _t
            break   # the majority only

    # A 'FILED: <date>' stamp row that opened the writing's body (its
    # row-mate byline anchored the writing) carries the DECISION DATE —
    # criteria, not prose.
    if doc.opinions and doc.opinions[0].blocks:
        from .audit import strip_tags as _st1
        from .resolve.headmatter import find_date as _fd
        import re as _re1
        _b0 = doc.opinions[0].blocks[0]
        _t0 = _st1(getattr(_b0, "text", "") or "").strip()
        if len(_t0) < 45 and _re1.match(r"^FILED\b[:\s]", _t0, _re1.I):
            _d = _fd(_t0)
            if _d:
                if doc.criteria.decision_date is None:
                    doc.criteria.decision_date = _d
                doc.dropped.append(m.Dropped(
                    text=_t0, prov=_b0.prov, kind="stamp"))
                doc.opinions[0].blocks.pop(0)

    # THE COURT'S SEAL, at the head of the headmatter where the page prints
    # it. `HmItem` already admits an ImageBlock and `render_hm_items` already
    # draws one, so this needs no new machinery — only the right destination.
    if _mastheads:
        import base64 as _mb64
        import io as _mio
        import pdfplumber as _mpp
        try:
            with _mpp.open(str(pdf_path)) as _mpdf:
                for _im in sorted(_mastheads, key=lambda i: i.top):
                    _mpg = _mpdf.pages[_im.page - 1]
                    _mcrop = _mpg.crop((max(0, _im.x0 - 2), max(0, _im.top - 2),
                                        min(_mpg.width, _im.x1 + 2),
                                        min(_mpg.height, _im.bottom + 2)))
                    _mbuf = _mio.BytesIO()
                    _mcrop.to_image(resolution=150).original.save(_mbuf, "PNG")
                    doc.headmatter.insert(0, m.ImageBlock(
                        src=("data:image/png;base64,"
                             + _mb64.b64encode(_mbuf.getvalue()).decode()),
                        prov=m.Prov(_im.page),
                        width=_im.x1 - _im.x0, height=_im.bottom - _im.top,
                        role="seal"))
        except Exception:
            # a seal is not worth failing a document over
            for _im in _mastheads:
                doc.dropped.append(m.Dropped(
                    text=(f"seal {_im.x1 - _im.x0:.0f}×"
                          f"{_im.bottom - _im.top:.0f}pt (uncropped)"),
                    prov=m.Prov(_im.page), kind="image"))

    # CONTENT FIGURES: crop each body image from the page and place it in
    # the writing at its reading position (adidas's trademark exhibits are
    # part of the opinion; v1 carried them, so do we).
    if _figures and doc.opinions:
        import base64 as _b64
        import io as _io
        import pdfplumber as _pp
        _line_top = {l.id: l.top for pm2 in model.pages for l in pm2.lines}
        with _pp.open(str(pdf_path)) as _pdf:
            for _im in _figures:
                try:
                    _pg = _pdf.pages[_im.page - 1]
                    _crop = _pg.crop((max(0, _im.x0 - 2),
                                      max(0, _im.top - 2),
                                      min(_pg.width, _im.x1 + 2),
                                      min(_pg.height, _im.bottom + 2)))
                    _pil = _crop.to_image(resolution=150).original
                    _buf = _io.BytesIO()
                    _pil.save(_buf, "PNG")
                except Exception:
                    continue
                _src = ("data:image/png;base64,"
                        + _b64.b64encode(_buf.getvalue()).decode())
                _blk = m.ImageBlock(src=_src, prov=m.Prov(_im.page),
                                    width=_im.x1 - _im.x0,
                                    height=_im.bottom - _im.top,
                                    role="figure")
                # the writing whose blocks surround the figure's position
                _placed = False
                for _op in doc.opinions:
                    _pgs = [b.prov.page for b in _op.blocks
                            if getattr(b, "prov", None)]
                    if not _pgs or not (min(_pgs) <= _im.page <= max(_pgs)):
                        continue
                    _at = len(_op.blocks)
                    for _k, _b in enumerate(_op.blocks):
                        _bpg = getattr(_b.prov, "page", 0)
                        _bt = min((_line_top.get(i, 0)
                                   for i in getattr(_b.prov, "line_ids", ())),
                                  default=0)
                        if _bpg > _im.page or (_bpg == _im.page
                                               and _bt > _im.top):
                            _at = _k
                            break
                    _op.blocks.insert(_at, _blk)
                    _placed = True
                    break
                if not _placed:
                    doc.dropped.append(m.Dropped(
                        text=(f"figure {_im.x1 - _im.x0:.0f}×"
                              f"{_im.bottom - _im.top:.0f}pt (unplaced)"),
                        prov=m.Prov(_im.page), kind="image"))

    # THE COURT'S SIGNATURE, WHERE IT IS A PICTURE. An ECF order is signed
    # with a stamp, not with type: kyed's last page carries 293x79pt of image
    # below the body and its text layer holds no 'Signed By', no 'District
    # Judge' and no judge's name at all — 22 of its 25 records are image-only
    # (2 have text, 1 has neither). Dropped as furniture, the signature
    # disappeared from the document entirely. `Opinion.signature` and
    # `ImageBlock.role="signature-graphic"` both already exist, and the
    # renderer draws an ImageBlock, so the graphic renders where the page
    # puts it — under the writing it signs, with the date line that belongs
    # to it. Only an image standing BELOW the body's last row on the LAST
    # page qualifies: anything higher is a figure the opinion discusses.
    if doc.opinions and _sig_imgs:
        import base64 as _sb64
        import io as _sio
        import pdfplumber as _spp
        _last = doc.opinions[-1]
        try:
            with _spp.open(str(pdf_path)) as _spdf:
                for _im in _sig_imgs:
                    _sp = _spdf.pages[_im.page - 1]
                    _sc = _sp.crop((max(0, _im.x0 - 2), max(0, _im.top - 2),
                                    min(_sp.width, _im.x1 + 2),
                                    min(_sp.height, _im.bottom + 2)))
                    _sb = _sio.BytesIO()
                    _sc.to_image(resolution=150).original.save(_sb, "PNG")
                    _last.signature.append(m.ImageBlock(
                        src=("data:image/png;base64,"
                             + _sb64.b64encode(_sb.getvalue()).decode()),
                        prov=m.Prov(_im.page),
                        width=_im.x1 - _im.x0, height=_im.bottom - _im.top,
                        role="signature-graphic"))
        except Exception:
            for _im in _sig_imgs:
                doc.dropped.append(m.Dropped(
                    text=(f"signature graphic {_im.x1 - _im.x0:.0f}×"
                          f"{_im.bottom - _im.top:.0f}pt (uncropped)"),
                    prov=m.Prov(_im.page), kind="signature"))

    # SIGNATURE GRAPHIC: pasuperct closes with 'Judgment Entered.' as an
    # IMAGE (prothonotary stamp + signature) over a bare typed date. The
    # image never renders; the orphan date must not read as body. Stash
    # both as a surfaced removal — the record says what stood there.
    if doc.opinions:
        import re as _re
        _last_op = doc.opinions[-1]
        while _last_op.blocks:
            _lb = _last_op.blocks[-1]
            _txt = (getattr(_lb, "text", "") or "").strip()
            if not _re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", _txt):
                break
            _pg = _lb.prov.page
            _imgs = [im for im in model.pages[_pg - 1].images
                     if (im.x1 - im.x0) >= 40 and abs(im.x1 - im.x0) < 400]
            if not _imgs:
                break
            _im = _imgs[-1]
            doc.dropped.append(m.Dropped(
                text=(f"signature graphic {_im.x1 - _im.x0:.0f}×"
                      f"{_im.bottom - _im.top:.0f}pt · dated {_txt}"),
                prov=m.Prov(_pg, tuple(_lb.prov.line_ids)),
                kind="signature"))
            _last_op.blocks.pop()

    # LEADING counsel: nd sets the roster between the byline and the ¶1
    # body — strong-marked blocks at the writing's HEAD are appearances.
    if doc.opinions:
        from .audit import strip_tags as _st0
        _first = doc.opinions[0]
        while _first.blocks:
            lw = " ".join(_st0(getattr(_first.blocks[0], "text", "")
                               or "").split()).lower()
            # …and the mark must sit in the block's CLOSING span, the same
            # rule the trailing roster uses. `_COUNSEL_STRONG` contains
            # 'pro se,', and a per curiam that opens 'Proceeding pro se,
            # Reyes-Recalde argues…' matched it on its first paragraph — so
            # the writing's opening was lifted out of the opinion and filed
            # as an appearance.
            # …and the closing span was NOT enough. ca11 opens a per curiam
            # 'Derhem, pro se on appeal, raises various arguments in support
            # of reversal.  None of them have merit, so we affirm.' — the
            # mark sits in the last 120 characters, so the writing's opening
            # was still lifted out and filed as an appearance. 'pro se'
            # describes a PARTY; every other strong mark is a representation
            # LABEL, and a roster the court prints above the body always
            # names counsel with one of those. So the leading lift does not
            # get to use it. (The TRAILING roster still may — there the row
            # is the roster, not a paragraph of the opinion.)
            _HEAD_MARKS = tuple(mk for mk in _COUNSEL_STRONG
                                if "pro se" not in mk)
            if (len(lw) <= 400
                    and any(mk in lw[-120:] for mk in _HEAD_MARKS)):
                # An appearance printed above the body is HEADMATTER, and
                # that is where it renders — not in a section of its own.
                # Its text is copied into criteria like any other counsel.
                _b0 = _first.blocks.pop(0)
                doc.headmatter.append(m.HmLine(
                    text=getattr(_b0, "text", ""), prov=_b0.prov,
                    role="counsel"))
                # The BLOCK's own text, not `lw` — `lw` is the lowercased
                # working copy the marks are matched against, and appending
                # it published every one of these appearances in lower case
                # ('kiara c. kraus-parr, grand forks, nd, for petitioner').
                _counsel_texts.append(getattr(_b0, "text", "") or lw)
            else:
                break

    # TRAILING counsel: fla/ind/ohio print the appearance roster AFTER the
    # last writing — same counsel test, different address. The roster mixes
    # marked lines with address blocks ('Indianapolis, Indiana'), so harvest
    # the WINDOW from the first strong hit to the end, not a strict walk.
    def _hm_rows(blocks):
        """The moved blocks re-read as the rows the page actually printed.
        Returns [] when provenance cannot place them, and the caller keeps
        the blocks — a roster rendered as paragraphs is worse than one
        rendered as rows, but both beat losing it."""
        _by_id = {l.id: (pm, l) for pm in model.pages for l in pm.lines}
        out = []
        for _b in blocks:
            _ids = getattr(getattr(_b, "prov", None), "line_ids", ()) or ()
            _got = [_by_id[i] for i in _ids if i in _by_id]
            if not _got:
                return []
            for _pm, _l in _got:
                _row = _hm_line(_l, _pm, geom)
                _row.role = "counsel"
                out.append(_row)
        return out

    for _last in doc.opinions:
        from .audit import strip_tags as _st
        # A TRAILING NOTICE is publisher apparatus wherever it prints. The
        # headmatter sweep never reaches it because fla sets its finality
        # notice on the LAST page, under the counsel roster. Same two-cue
        # evidence bar, applied to the tail.
        # The notice is ONE printed run that may set as several short
        # lines, each carrying a single cue ('NOT FINAL UNTIL TIME EXPIRES
        # TO FILE MOTION FOR REHEARING' / 'AND DISPOSITION THEREOF IF
        # TIMELY FILED'), so the two-cue bar is read across the run.
        # The run is exactly the trailing blocks that EACH carry a cue —
        # so it stops at the first real line above it (a counsel entry) —
        # and the run as a whole must clear the two-cue bar.
        _n = 0
        while _n < min(4, len(_last.blocks)):
            _t = _st(getattr(_last.blocks[-1 - _n], "text", "") or "")
            _tl = " ".join(_t.split()).lower()
            if len(_t) > 200 or not any(c in _tl for c in _NOTICE_CUES):
                break
            _n += 1
        if _n:
            _tail = _last.blocks[-_n:]
            _txts = [_st(getattr(b, "text", "") or "") for b in _tail]
            _joined = " ".join(" ".join(t.split()) for t in _txts).lower()
            if sum(1 for c in _NOTICE_CUES if c in _joined) >= 2:
                for _b, _t2 in zip(_tail, _txts):
                    doc.dropped.append(m.Dropped(
                        text=_t2, prov=getattr(_b, "prov", m.Prov(1)),
                        kind="notice"))
                del _last.blocks[-_n:]
        _win = _last.blocks[-12:] if profile.counsel_after_writings else []
        _lows = [" ".join(_st(getattr(b, "text", "") or "").split()).lower()
                 for b in _win]
        # 'Counsel for Appellant' and '[Argued]' count as strong HERE —
        # the trailing window is already positional evidence (ca3 lists
        # counsel after the writings in that form).
        # A counsel entry CLOSES on the party it represents (fla: '…of
        # Banker Lopez Gassler, P.A., Tampa, …, for Appellant.'). The role
        # must END the block: body prose says 'for the defendant' mid
        # sentence all the time, and matching that swept ca6's conclusion
        # paragraph and a me footnote into the attorney list.
        # The role a roster entry closes on. Matched as WHOLE WORDS: a
        # substring test on 'for the state' also matches an opinion's own
        # last sentence, 'For the stated reasons, we will affirm.', and
        # byjus_alpha published its disposition as an appearance — the
        # writing's closing line lifted out of the writing.
        _ROLE_TAIL = _re.compile(
            r"for (?:appellant|appellee|petitioner|respondent|plaintiff"
            r"|defendant|real party in interest|the state"
            r"|amicus curiae|amici curiae|amicus|amici|intervenor)s?\b")
        # A CITATION TO A PARTY'S BRIEF is an authority, never an
        # appearance: an opinion closes a paragraph 'Brief for Respondent
        # 26.' or 'Reply Brief for Petitioner 4' as often as a roster
        # closes an entry ', for Respondent.', and the role tail cannot
        # tell them apart. The citation forms are the veto — applied only
        # where the role tail is the ONLY evidence, so a real entry
        # ('…, on the briefs for appellant') still hits on its strong mark.
        import re as _rcc
        _CITE_FORM = _rcc.compile(
            r"\bbriefs?\s+(?:for|of)\b|\breply\s+brief\b"
            r"|\btr\.\s*of\s*oral\s*arg"
            # '…for Respondent 26.' — a page cite closes it, not a party
            r"|\bfor\s+(?:the\s+)?[a-z]+s?\s+\d+(?:[-–]\d+)?\s*$")
        # A CLERK'S DISTRIBUTION NOTE IS NOT AN APPEARANCE. 'Dated: March 2,
        # 2026  Amr/Cc: All counsel of record' names no one who argued
        # anything — it says who was sent a copy. Core already vetoes it
        # where counsel is routed in the headmatter; the trailing roster,
        # which only ca3 enables, never got the same veto and published the
        # note as ca3's attorneys section.
        _DISTRIB = ("cc:", "all counsel of record", "counsel of record.",
                    "/cc:", "dated:")
        # …and a note vetoed here is REMOVED, not left behind. Vetoing it
        # only stopped it being published as counsel; the block stayed in
        # the writing, where the clerk's copy list and its page numerals
        # then read as counsel-in-body and folio leaks.
        for _k, _lw in enumerate(_lows):
            if any(_d in _lw for _d in _DISTRIB) and len(_lw) <= 400:
                _b = _win[_k]
                if _b in _last.blocks:
                    doc.dropped.append(m.Dropped(
                        text=_st(getattr(_b, "text", "") or "")[:400],
                        prov=getattr(_b, "prov", m.Prov(1)),
                        kind="distribution"))
                    _last.blocks.remove(_b)
        _hits = [k for k, lw in enumerate(_lows)
                 if not any(d in lw for d in _DISTRIB)
                 # …in the entry's CLOSING span. Unbounded, 'counsel for'
                 # matched 651 characters of opinion prose — 'Wilcox faults
                 # appellate counsel for not arguing that…' — which dragged
                 # the body back into the roster and the length cap then
                 # vetoed the whole harvest. The leading lift has always
                 # confined its marks this way; this path did not.
                 and any(mk in lw[-120:] for mk in
                         _COUNSEL_STRONG + ("counsel for", "[argued]"))
                 # the role sits in the entry's CLOSING span, not mid
                 # sentence ('…, for Plaintiff and Appellants.')
                 or (_ROLE_TAIL.search(lw.rstrip(". ")[-46:])
                     and not _CITE_FORM.search(lw.rstrip(". ")))]
        if not profile.counsel_after_writings:
            _probe = _os_env.environ.get("CENTRALIA_COUNSEL_PROBE")
            if _probe:
                _plows = [" ".join(_st(getattr(b, "text", "") or "").split())
                          .lower() for b in _last.blocks[-12:]]
                _ph = [k for k, lw in enumerate(_plows)
                       if any(mk in lw for mk in
                              _COUNSEL_STRONG + ("counsel for", "[argued]"))]
                if _ph:
                    with open(_probe, "a") as _fh:
                        _fh.write(f"{court_id}\t{pdf_path}\t"
                                  f"{_plows[_ph[0]][:80]}\n")
        if _hits and (len(_win) - 1 - _hits[-1]) <= 4:
            # The roster ENDS at its last marked entry, plus any short
            # continuation rows (a firm's second address line). Running to
            # the end of the document instead swept a me footnote and a
            # ca6 conclusion paragraph in behind the counsel.
            _end = _hits[-1]
            while (_end + 1 < len(_win)
                   and len(_st(getattr(_win[_end + 1], "text", "")
                               or "")) <= 120):
                _end += 1
            _base = len(_last.blocks) - len(_win)
            _start, _stop = _base + _hits[0], _base + _end + 1
            _moved = _last.blocks[_start:_stop]
            # 600, not 400: fla sets a single 458-character appearance, and
            # one over-long entry vetoed the roster for the whole record.
            if all(len(_st(getattr(b, "text", "") or "")) <= 600
                   for b in _moved):
                del _last.blocks[_start:_stop]
                # WHERE THE PAGE PRINTS IT. A roster the court sets BELOW
                # its writings belongs after them, and `attorneys` renders
                # at order 40 — ahead of the opinions — so publishing it
                # there hoists the end of the document to the top. `trailer`
                # (order 70) is the section that keeps the page's order.
                # Its text is copied into criteria like any other counsel.
                # …AS THE PAGE PRINTS IT. The roster is a list of rows —
                # a name, a firm, an address — and assembly had welded them
                # into paragraphs ('Melissa Bayly Christopher J. Dalton
                # [Argued] Argia J. DiMarco BUCHANAN INGERSOLL & ROONEY').
                # Headmatter keeps every printed row; the endmatter is the
                # same kind of matter and is rebuilt the same way, one
                # HmLine per source line, so both read alike.
                _rows = _hm_rows(_moved)
                doc.attorneys.extend(_rows or _moved)
                _counsel_texts.extend(
                    _st(getattr(b, "text", "") or "") for b in _moved)

    if _counsel_texts and doc.criteria.attorneys is None:
        from .audit import strip_tags as _sta, unescape_xml as _uxa
        doc.criteria.attorneys = " ".join(
            _uxa(_sta(t)) for t in _counsel_texts if t.strip())[:2000]
    if doc.attorneys and doc.criteria.attorneys is None:
        from .audit import strip_tags, unescape_xml
        doc.criteria.attorneys = " ".join(
            unescape_xml(strip_tags(getattr(b, "text", "")))
            for b in doc.attorneys if getattr(b, "text", ""))[:2000]
    if history_txt and doc.criteria.history is None:
        doc.criteria.history = " ".join(history_txt)[:2000]

    # A court that read its own headmatter also knows what KIND of paper it
    # is. Applied HERE, after the writings are built: the doc-type heading
    # is what anchors an unsigned writing, so the type cannot be declared
    # before assembly without removing the anchor that finds the body. An
    # unsigned lead writing typed 'order' by that heading is the court's
    # opinion when the court says the paper is one.
    if _court_hm and _court_hm.get("doc_type_final") is not None:
        meta.doc_type = _court_hm["doc_type_final"]
        if (meta.doc_type is m.DocType.OPINION and doc.opinions
                and doc.opinions[0].type == "order"
                and not doc.opinions[0].author_name):
            doc.opinions[0].type = "majority"

    # A court that ANNOUNCES its author in the caption instead of SIGNING the
    # writing ('OPINION BY' over 'JUSTICE JUNIUS P. FULTON, III' in va's
    # caption right column) leaves core no byline to build from: core's
    # `_opinion_by` wants the label and the name on ONE line, and the
    # headmatter renders whole so nothing may be lifted out of it. The reader
    # reports what the caption announced; core parses it with the court's own
    # grammar and signs the LEAD writing — only where the document prints no
    # byline of its own, which always outranks an announcement. 44 of va's 50
    # records came back with an unauthored writing without this.
    _ann = _court_hm.get("announced_author") if _court_hm else None
    if _ann and doc.opinions and not doc.opinions[0].author_name:
        _by = parser.parse(_ann)
        if _by is not None:
            _lead = doc.opinions[0]
            _lead.author = _ann
            _lead.author_name = _by.name
            _lead.author_title = _by.title
            if _lead.type in ("order", "opinion"):
                _lead.type = "majority"

    # HEADMATTER KEEPS THE PAGE'S ORDER. A court reader claims some rows
    # and the shared walk places the rest; appending one set after the other
    # rearranges the block, which is exactly what the render must not do.
    # Sort by where the page prints each row — the only thing that ever
    # moves is a footnote, which is lifted deliberately.
    if _court_hm:
        _ordpos = {l.id: (pm.number, l.top)
                   for pm in model.pages for l in pm.lines}

        def _row_at(it):
            prov = getattr(it, "prov", None)
            pts = [_ordpos[i] for i in (prov.line_ids if prov else ())
                   if i in _ordpos]
            return min(pts) if pts else None

        # AN ITEM WITH NO LINE PROVENANCE KEEPS ITS PLACE. A seal is an
        # ImageBlock, not a line, and it is inserted at index 0 because that
        # is where the page prints it — but a sentinel sort key sank it to the
        # FOOT of every claimed headmatter that has one (mo 49/50, nd 50/50).
        # A drawn Rule has the same problem. So an id-less item inherits the
        # position of the row it stands beside: the one after it where there
        # is one, otherwise the one before. `sorted` is stable, so it keeps
        # the side of that neighbour it was emitted on.
        _keys = [_row_at(i) for i in doc.headmatter]
        for _k in range(len(_keys) - 2, -1, -1):
            if _keys[_k] is None:
                _keys[_k] = _keys[_k + 1]
        for _k in range(len(_keys)):
            if _keys[_k] is None:
                _keys[_k] = _keys[_k - 1] if _k else (0, -1.0)
        doc.headmatter = [doc.headmatter[i] for i in sorted(
            range(len(doc.headmatter)), key=lambda i: _keys[i])]

    # …and the mirror of the bisection rule: WHERE A READER CLAIMED THE
    # HEADMATTER, AN UNREAD ROW BELOW IT IS THE WRITING'S. The reader stops
    # at the court's own prose, so a row it did not identify that sits after
    # the last row it did — and before the first writing — is the opening of
    # that writing, left behind because assembly anchored deeper in the
    # document (hampton stranded 52 rows above its majority).
    if _court_hm and doc.opinions and doc.opinions[0].blocks:
        _pos0 = {l.id: (pm.number, l.top)
                 for pm in model.pages for l in pm.lines}

        def _at(obj):
            prov = getattr(obj, "prov", None)
            pts = [_pos0[i] for i in (prov.line_ids if prov else ())
                   if i in _pos0]
            return min(pts) if pts else None

        _tagged = [_at(i) for i in doc.headmatter if getattr(i, "role", "")]
        _tagged = [p for p in _tagged if p]
        _op0 = _at(doc.opinions[0].blocks[0])
        if _tagged and _op0:
            _last_read = max(_tagged)
            _moved, _kept = [], []
            for _it in doc.headmatter:
                _p = _at(_it)
                if (not getattr(_it, "role", "") and _p
                        and _last_read < _p < _op0
                        and not isinstance(_it, (m.Rule, m.CaptionBlock))):
                    _moved.append((_p, _it))
                else:
                    _kept.append(_it)
            if _moved:
                _moved.sort(key=lambda x: x[0])
                doc.opinions[0].blocks[:0] = [
                    m.Paragraph(text=getattr(i, "text", ""), prov=i.prov)
                    for _, i in _moved]
                doc.headmatter = _kept
                trace.event("court.body_reclaimed",
                            f"{len(_moved)} rows below the read headmatter")

    # An EMPTY WRITING is not a writing. The rescue anchor can open one at a
    # segment that turns out to hold nothing, and it renders as a phantom
    # 'order' beside the real opinion.
    # …and a note it was holding belongs to the HEADMATTER, which is where
    # the page prints it: campbell's caption note was attached to a phantom
    # writing, so the document showed an empty 'order' and no headmatter
    # footnote at all.
    _empty = [o for o in doc.opinions if not o.blocks and not o.author_name]
    for _o in _empty:
        doc.headmatter_footnotes.extend(_o.footnotes)
    doc.opinions = [o for o in doc.opinions if o.blocks or o.author_name]

    # …and NEITHER IS A FENCE ON ITS OWN. A court that heads its opinion
    # with its own name ('OPINION OF THE COURT', 'ORDER') prints that name
    # above the byline, and where a page break falls between the two the
    # heading assembles as a writing whose whole content is the heading —
    # schuster came out [majority 'OPINION OF THE COURT'], [majority KRAUSE,
    # …]. The heading is the next writing's opening line, so give it back:
    # fold a heading-only, unbylined writing into the writing below it. A
    # fence that anchors a real unsigned writing carries that writing's
    # prose too, so it is untouched (ca6's 'ORDER' stands as it did).
    _folded = 0
    for _i in range(len(doc.opinions) - 1, -1, -1):
        _o = doc.opinions[_i]
        if _i + 1 >= len(doc.opinions):
            continue
        _nxt = doc.opinions[_i + 1]
        _heading_only = (not _o.author_name and bool(_o.blocks) and all(
            isinstance(b, m.Heading) for b in _o.blocks))
        # …OR AN UNFINISHED RECITAL. cafc's Rule 36 judgment prints
        #
        #     THIS CAUSE having been heard and considered, it is
        #     ORDERED and ADJUDGED:
        #     PER CURIAM (DYK, MAYER, and PROST, Circuit Judges).
        #     AFFIRMED.  See Fed. Cir. R. 36.
        #
        # — ONE paper whose sentence runs straight through the byline, so
        # assembly opened a writing at the recital and another at the
        # byline. The COLON is the evidence: the recital does not end, it
        # continues into the writing below.
        #
        # Deliberately narrow. 'Any short unbylined writing folds down'
        # would destroy scotus, where an unsigned disposition ('The
        # petition for a writ of certiorari is denied.') followed by a
        # dissent is genuinely two writings — that recital ENDS, and a
        # dissent never completes another writing's sentence.
        # The recital's own first row is read as the writing's byline
        # ('THIS CAUSE having been heard and considered, it is'), so the
        # test spans the author row AND the blocks. A real byline carries a
        # bench title; this one carries none, which is the second signal.
        _txt = " ".join([_st(_o.author or "")] +
                        [_st(getattr(b, "text", "") or "")
                         for b in _o.blocks]).strip()
        _recital = (len(_o.blocks) <= 4 and len(_txt) <= 300
                    and _txt.endswith(":") and not _o.author_title
                    and bool(_nxt.author_name)
                    and _nxt.type not in ("dissent", "concurrence"))
        if not (_heading_only or _recital):
            continue
        _lead = list(_o.blocks)
        if _o.author and _st(_o.author).strip():
            # …and its byline row is PROSE. Keep it, at the top, or the
            # judgment loses the sentence it opens with.
            _lead.insert(0, m.Paragraph(text=_o.author, prov=_o.author_prov))
        _nxt.blocks = _lead + list(_nxt.blocks)
        _nxt.footnotes = list(_o.footnotes) + list(_nxt.footnotes)
        del doc.opinions[_i]
        _folded += 1
    if _folded:
        trace.event("writing.fence_folded",
                    f"{_folded} heading-only writing(s) joined the writing "
                    "below")

    # 9b INVARIANT — A WRITING IS NEVER BISECTED.
    #
    # Once a writing is assembled, the text between its first line and its
    # last belongs to it. Any row that some later rule filed as headmatter,
    # attorneys or front matter while sitting INSIDE that span was cut out
    # of the middle of an opinion, and that is always wrong however good the
    # rule's reason looked: callais lost the second half of a per curiam
    # order because one sentence of it ('…the District Court may "oversee an
    # orderly process."') carried two court words and read as a masthead;
    # pung lost a paragraph of a concurrence because it closed on 'Brief for
    # Respondent 26.' and read as an appearance. Both are the same defect,
    # so the repair is stated once, structurally, instead of patched at each
    # rule that can produce it.
    _pos = {l.id: (pm.number, l.top)
            for pm in model.pages for l in pm.lines}

    def _pt(obj):
        prov = getattr(obj, "prov", None)
        pts = [_pos[i] for i in (prov.line_ids if prov else ()) if i in _pos]
        return (min(pts), max(pts)) if pts else None

    _spans = []
    for _op in doc.opinions:
        _pts = [q for b in _op.blocks for q in ([_pt(b)] if _pt(b) else [])]
        if _pts:
            _spans.append((_op, min(p[0] for p in _pts),
                           max(p[1] for p in _pts)))
    if _spans:
        for _sec in ("headmatter", "attorneys", "syllabus", "summary"):
            _kept = []
            for _it in getattr(doc, _sec):
                _p = _pt(_it)
                _home = None
                if _p is not None and not isinstance(_it, (m.Rule,
                                                           m.CaptionBlock)):
                    for _op, _lo, _hi in _spans:
                        if _lo < _p[0] < _hi:
                            _home = _op
                            break
                if _home is None:
                    _kept.append(_it)
                    continue
                # put it back where the page printed it
                _blk = m.Paragraph(text=getattr(_it, "text", ""),
                                   prov=_it.prov)
                _at = len(_home.blocks)
                for _k, _b in enumerate(_home.blocks):
                    _bp = _pt(_b)
                    if _bp and _bp[0] > _p[0]:
                        _at = _k
                        break
                _home.blocks.insert(_at, _blk)
                # A repair that SUCCEEDED is not a parse complaint: recorded
                # in the trace, not in the warnings that gate the file.
                trace.event("invariant.reunited",
                            f"{_sec} row p{_p[0][0]}")
            setattr(doc, _sec, _kept)

    # 10 finalize — residual sweep: every content line must have landed.
    placed: set[int] = set()
    for items in (doc.headmatter, doc.attorneys, doc.syllabus, doc.summary,
                  doc.headnotes, doc.signature, doc.trailer):
        for it in items:
            prov = getattr(it, "prov", None)
            if prov is not None:
                placed.update(prov.line_ids)
            if isinstance(it, m.CaptionBlock):
                for row in it.left + it.right:
                    placed.update(row.prov.line_ids)
    for op in doc.opinions:
        placed.update(op.author_prov.line_ids)
        for b in (*op.blocks, *op.signature, *op.caption):
            placed.update(getattr(b, "prov", m.Prov(1)).line_ids)
        for fn in op.footnotes:
            for b in fn.blocks:
                placed.update(b.prov.line_ids)
    for fn in doc.headmatter_footnotes:
        for b in fn.blocks:
            placed.update(b.prov.line_ids)
    placed.update(assembled.consumed_ids)
    dropped_ids = all_dropped_ids | {
        i for d in doc.dropped for i in d.prov.line_ids}
    for pm in model.pages:
        for line in pm.lines:
            if line.id in placed or line.id in dropped_ids:
                continue
            if not line.plain.strip():
                continue
            in_zone = (pm.number in zone_tops
                       and line.top > zone_tops[pm.number] - 0.5)
            kind = "furniture" if ff.kind(pm, line) else "content"
            if in_zone and kind == "content":
                continue  # zone separators/typed rules
            # A line of PURE RAIL GLYPHS carries no words: it is the
            # caption's drawn column (pasuperct sets ':' down the middle)
            # or a typed separator. Counting it as lost content sent whole
            # courts to review over punctuation.
            if kind == "content" and not any(
                    c.isalnum() for c in line.plain):
                kind = "furniture"
            doc.residual.append(m.Residual(
                text=line.plain.strip(), prov=m.Prov(pm.number, (line.id,)),
                kind=kind))

    if meta.doc_type == m.DocType.UNKNOWN and doc.opinions:
        signed = any(op.author for op in doc.opinions)
        meta.doc_type = m.DocType.OPINION if signed else m.DocType.ORDER
    # A SIGNED writing outranks a notice classification (a slip cover's
    # 'NOTICE:' boilerplate must never validate an empty extraction).
    if meta.doc_type == m.DocType.NOTICE and any(
            op.author for op in doc.opinions):
        meta.doc_type = m.DocType.OPINION
    # A JUDGMENT heading over SUBSTANTIVE REASONING is the court's own
    # writing, not a clerk's form (ca1 heads a reasoned disposition
    # 'JUDGMENT'; ca10 heads the same thing 'ORDER AND JUDGMENT'). The
    # body itself is the evidence: a bare form has none.
    if meta.doc_type == m.DocType.JUDGMENT:
        from .audit import strip_tags as _stj
        _words = sum(len(_stj(getattr(b, "text", "") or "").split())
                     for op in doc.opinions for b in op.blocks)
        if _words >= 120:
            meta.doc_type = m.DocType.ORDER

    # 11 emit
    #
    # 'review' must mean SOMETHING TO FIX. A scanned or partly image-only
    # source is a property of the PDF, not of the parse — lumping the two
    # together buried real defects under ~100 files nobody can improve, so
    # source complaints get their own status and their own worklist.
    _src = [w for w in doc.warnings
            if any(k in w for k in SOURCE_WARNINGS)]
    _parse = [w for w in doc.warnings if w not in _src]
    status = "valid"
    if any(r.kind == "content" for r in doc.residual) or _parse:
        status = "review"
    elif not doc.opinions and meta.doc_type not in m.NO_BODY_EXPECTED:
        status = "review"
    elif _src:
        status = "scanned"
    return ExtractionResult(doc, trace, status=status)
