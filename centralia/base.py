"""Court-pluggable PDF extractor.

``BaseExtractor.extract(pdf_path)`` turns one court PDF into a structured
``ExtractedDocument`` (see ``centralia.models``). The base class holds the
deterministic layout heuristics; each court subclass overrides only the hook
points where its typesetting differs.

The pipeline, one method per responsibility:

    extract(pdf_path) -> ExtractedDocument
      iter pages: find_footnote_separator / page_lines / filter_margins
                  segment_lines / classify_segment
      find_authors / parse_author_line / normalize_opinion_type
      classify_document_type            <- the document-style identifier
      extract_headmatter
      build_opinions / build_footnotes

Text + layout primitives (line_meta, line_alignment, line_inline_text,
paragraph splitting, footnote-label detection) are court-agnostic and are
ported unchanged from the original casebody engine.
"""

from __future__ import annotations

import re
from collections import Counter
from statistics import median
from typing import Optional
from xml.sax.saxutils import escape

import pdfplumber

from .models import (
    Block,
    DocType,
    ExtractedDocument,
    Footnote,
    Opinion,
)


def _is_per_curiam(text: str) -> bool:
    """True for an uppercase 'PER CURIAM' byline (optional trailing period),
    case-sensitive, whitespace-insensitive. No regex."""
    t = text.strip()
    if t.endswith("."):
        t = t[:-1]
    return " ".join(t.split()) == "PER CURIAM"


_ORDER_CUES = (
    "it is ordered",
    "it is hereby ordered",
    "is hereby denied",
    "is hereby granted",
    "petition for",
    "is dismissed",
    "is denied",
    "is granted",
    "rehearing",
    "mandate",
)
_NOTICE_CUES = (
    "no opinions",
    "notice",
    "clerk of",
    "calendar",
    "this opinion is subject",
)


class BaseExtractor:
    # ====================================================================
    # CLASS CONFIG (each court subclass overrides these)
    # ====================================================================
    court_id: str = ""
    court_label: str = ""  # -> <court>
    author_titles: tuple = ("Justice",)  # ("Judge", "Presiding Judge") ...
    # Document styles that are classified but not parsed into opinions.
    SKIP_BODY_TYPES: tuple = ()

    # ====================================================================
    # LAYOUT DEFAULTS (override per-court if layout differs)
    # ====================================================================
    margin_top: float = 39
    margin_bottom: float = 725
    # When True, a body "paragraph" that is just a bare page number ('4' /
    # '- 12 -') is dropped from the body; the cross-page paragraph merge then
    # rejoins the split paragraph with a <pagenumber> marker. Default False so
    # courts whose page numbers already sit in the margin are unaffected.
    fold_page_numbers: bool = False
    body_baseline_x0: float = 72.0
    # A body line whose x0 exceeds ``body_baseline_x0 + para_indent_min`` starts a
    # new paragraph (a first-line indent). Default 28 suits ~half-inch indents;
    # narrow-indent reporters (e.g. Connecticut, ~10pt) lower it.
    para_indent_min: float = 28.0
    indent_step: float = 36.0
    gap_tight_max: float = 16  # < this = tight (notice-like)
    gap_single_max: float = 22  # < this = single (blockquote / footnote)
    gap_double_max: float = 40  # < this = double (body); >= this = boundary
    # Some courts double-space the body but single-space block quotes at a tight
    # ~13-15pt leading — below ``gap_tight_max`` — so a quote reads as a 'notice'
    # and renders as body prose. When True, a both-margins-indented multi-line
    # run is re-tagged as a block quote by its geometry (CLAUDE.md principle 7),
    # whatever tight gap band its leading lands in. Off by default so the gap
    # bands are the sole classifier (Alabama fidelity).
    blockquote_by_indent: bool = False
    # A line-to-line change in bold normally marks a structural boundary
    # (heading / byline). Courts that bold text *inline* for emphasis — e.g.
    # Puerto Rico bolds dates and times mid-paragraph — set this False so an
    # emphasized line does not split the paragraph; their headings still
    # separate by alignment, size, and gap.
    bold_breaks_segment: bool = True
    # OPT-IN: a paragraph group in which NO line reaches the right measure is
    # a *stack* (name/title sign-off, roster) — one block per line, since a
    # line that ends far short of the margin never wrapped. Off by default:
    # Alabama's fidelity-locked output joins its no-opinion order rosters and
    # transcript-quote continuations, so the rule must not fire there.
    split_line_stacks: bool = False

    underline_offset_min: float = 0.0
    underline_offset_max: float = 5.0

    # ---- Opt-in reusable hooks (courts turn these on via config) --------
    # If set to (x0, x1), the footnote-zone separator is the rect whose left
    # and right edges match exactly; otherwise baseline-anchored detection.
    footnote_sep_rect: tuple | None = None
    # Some courts (e.g. Utah) draw the footnote separator as a full-measure
    # line of '_' TEXT rather than a vector rule, and set their footnotes at
    # body size — so neither the rect scan nor the 'smaller text below'
    # discriminator finds it, and the footnotes fall into the body. Set this to
    # the minimum separator width (pt) to detect that underscore line in the
    # lower half of the page. None disables it (rect-based detection only).
    footnote_sep_text_min_width: float | None = None
    # Some courts set footnotes at BODY size (only the label digit is raised),
    # so the 'smaller text below the rule' discriminator never fires. When
    # True, the separator is found structurally instead: a thin rule at the
    # body's left margin standing clear of any text line (a rule inside a
    # text line's band is a case-name underline), with footnote matter below
    # — a raised label digit, or single-spaced text where the body is
    # double-spaced. (washctapp, ohioctapp)
    footnote_sep_structural: bool = False
    # Drop a repeating docket-number running header from the top of
    # continuation pages (2+).
    running_header_docket: bool = False
    running_header_max_top: float = 200.0
    # Strip a trailing footnote-reference mark from a candidate author byline
    # before matching (e.g. "McCOOL, Justice.1" / "SELLERS, Justice.*").
    strip_author_trailing_mark: bool = False
    # A midpoint-centered line at/above this size is a centered banner
    # regardless of width. None disables.
    banner_center_min_size: float | None = None
    # Drop 'notice'-classified segments (publication advisories) from the
    # raw headmatter dump.
    skip_notice_headmatter: bool = False
    # Drop 'notice'-classified segments (tightly-spaced) from the opinion body.
    # Correct for double-spaced courts (Alabama) where a body 'notice' is stray
    # advisory text; WRONG for single-spaced courts whose whole body reads as
    # 'notice' by gap — those set this False so no body content is dropped.
    drop_notice_in_body: bool = True

    HEADMATTER_DIVIDER = "__DIVIDER__"
    # Star, dagger, double-dagger, section, paragraph + digits.
    FOOTNOTE_LABEL_CHARS = set("0123456789*†‡§¶**")
    # Some courts number paragraphs with a raised, bracket-wrapped pinpoint
    # ('{1}' — New Mexico; '[1]' — Indiana Court of Appeals). The digit is
    # small + a label char, so it otherwise reads as a footnote reference; a
    # court with this convention sets this True so a digit BETWEEN '{'/'[' and
    # '}'/']' stays inline paragraph-number content.
    bracket_pinpoint: bool = False

    # A page counts as "scanned" when a single image covers at least this
    # fraction of the page area. A born-digital opinion never rasterizes a
    # whole page; a scan does it on every page.
    non_digital_page_cover_frac: float = 0.85
    # The document is treated as a non-born-digital scan when at least this
    # fraction of its pages are scanned. The two signals together cleanly
    # separate scans (≈1.0) from digital PDFs that carry one decorative
    # full-page image (a lone exhibit/signature page, well under this).
    non_digital_min_page_frac: float = 0.6
    # A full-page image on PAGE 1 carrying fewer than this many real text chars
    # is a scanned caption page (only the ECF header as text) — the headmatter
    # and the opinion's opening are a raster. A born-digital opinion's page 1
    # always sets the caption in real text, well above this; a decorative
    # letterhead image sits under real text, also above it.
    non_digital_page1_text_max: int = 200
    # ...but a raster page 1 only makes the WHOLE document non-digital when there
    # is no born-digital body to parse elsewhere. A page with at least this many
    # real chars counts as a body page; if two or more sit beyond page 1, the
    # opinion body is digital (a scanned cover/letterhead over a real opinion —
    # Texas AG letters, a scanned order page ahead of a digital memorandum) and
    # the document is processed. One-or-none (only a certificate-of-service or a
    # mid-order fragment follows the rastered caption) → the document is a scan.
    non_digital_body_page_min_chars: int = 500

    # ====================================================================
    # MAIN PIPELINE
    # ====================================================================
    def _page_image_covered(self, page) -> bool:
        page_area = page.width * page.height
        if not page_area:
            return False
        for im in page.images:
            img_area = (im["x1"] - im["x0"]) * (im["bottom"] - im["top"])
            if img_area / page_area >= self.non_digital_page_cover_frac:
                return True
        return False

    def is_non_digital(self, pdf) -> bool:
        """True when the PDF is a scanned image rather than a born-digital
        document. Detected by a full-page raster image on most pages (an OCR'd
        scan), OR by an image-only page 1 whose caption is a raster with only
        the ECF header as text — the engine's geometry cues are unreliable
        either way, so the caller skips processing and only flags the document."""
        pages = pdf.pages
        if not pages:
            return False
        scanned = sum(1 for page in pages if self._page_image_covered(page))
        if scanned / len(pages) >= self.non_digital_min_page_frac:
            return True
        first = pages[0]
        if self._page_image_covered(first):
            real = len([c for c in first.chars if (c.get("text") or "").strip()])
            body_pages = sum(
                1
                for p in pages[1:]
                if len([c for c in p.chars if (c.get("text") or "").strip()])
                >= self.non_digital_body_page_min_chars
            )
            if real < self.non_digital_page1_text_max and body_pages <= 1:
                return True
        return False

    def matches_expected_layout(self, pdf) -> bool:
        """True if the PDF looks like a typical document for this court.
        Subclasses override to check layout signatures (e.g. a caption
        divider on page 1). Used to flag non-standard documents."""
        return True

    def extract(self, pdf_path: str) -> ExtractedDocument:
        """Convert a PDF into a structured ``ExtractedDocument``."""
        all_segments = []
        footnote_lines_by_page = {}
        images_by_page = {}
        tables_by_page = {}
        page1_rules = []
        layout_ok = True
        source_pages = []  # (page_number, [text lines]) — ground truth for the residual sweep
        with pdfplumber.open(pdf_path) as pdf:
            n_pages = len(pdf.pages)
            if self.is_non_digital(pdf):
                doc = ExtractedDocument(
                    court_id=self.court_id,
                    court_label=self.court_label,
                    doc_type=DocType.UNKNOWN,
                    n_pages=n_pages,
                    non_digital=True,
                    source_path=pdf_path,
                )
                doc.warnings.append(
                    "non-born-digital (scanned image + OCR text layer); not processed"
                )
                return doc
            layout_ok = self.matches_expected_layout(pdf)
            self._hm_caption_box = None
            self._page1_width = pdf.pages[0].width if pdf.pages else 612.0
            if pdf.pages:
                page1_rules = self._page1_rules(pdf.pages[0])
                self._hm_caption_box = self._page1_caption_box(pdf.pages[0])
                try:
                    from .captionfp import classify_page

                    self._caption_fp = classify_page(pdf.pages[0])
                except Exception:
                    self._caption_fp = (None, None, None)
            for page in pdf.pages:
                pw = page.width
                # The structural opt-in replaces separator detection outright,
                # at the call site — family bases override
                # find_footnote_separator freely, and the flag must win over
                # any of them (a court can't know which base it sits on).
                sep_y = (
                    self._footnote_sep_structural(page)
                    if self.footnote_sep_structural
                    else self.find_footnote_separator(page)
                )
                if page.page_number == 1 and sep_y is not None:
                    # The page-1 footnote separator is NOT a headmatter
                    # divider — without this it leaks into the styled summary
                    # as a spurious full-width rule at the bottom.
                    page1_rules = [t for t in page1_rules if t < sep_y - 1]
                lines = self.page_lines(page)  # also applies correct_page_geometry
                # Capture the upright ground-truth text for the residual sweep,
                # the same way audit.py reads it (geometry already corrected).
                gt = page.filter(lambda o: o.get("upright", True) is not False)
                source_pages.append(
                    (page.page_number, (gt.extract_text() or "").splitlines())
                )
                tables = self.extract_page_tables(page)
                table_bboxes = [t["bbox"] for t in tables]

                def in_any_table(l):
                    for bx0, btop, bx1, bbottom in table_bboxes:
                        if (
                            l["top"] >= btop
                            and l["top"] <= bbottom
                            and l["x0"] >= bx0 - 2
                            and l["x1"] <= bx1 + 2
                        ):
                            return True
                    return False

                body_lines = [
                    l
                    for l in lines
                    if (sep_y is None or l["top"] < sep_y) and not in_any_table(l)
                ]
                fn_lines = [
                    l
                    for l in lines
                    if sep_y is not None
                    and l["top"] >= sep_y
                    and not in_any_table(l)
                    and not self._is_separator_text(l)
                ]
                for seg in self.segment_lines(body_lines, pw):
                    all_segments.append(
                        (page.page_number, seg, self.classify_segment(seg))
                    )
                if fn_lines:
                    footnote_lines_by_page[page.page_number] = fn_lines
                imgs = self.extract_page_images(page)
                if imgs:
                    images_by_page[page.page_number] = imgs
                if tables:
                    tables_by_page[page.page_number] = tables

        all_segments = self._split_segments_at_bylines(all_segments)
        author_indices = self.find_authors(all_segments)
        doc_type = self.classify_document_type(all_segments, author_indices, n_pages)

        boundary = author_indices[0] if author_indices else len(all_segments)
        headmatter_segs = [s for _, s, _ in all_segments[:boundary]]
        headmatter = self.extract_headmatter(headmatter_segs, page1_rules=page1_rules)

        doc = ExtractedDocument(
            court_id=self.court_id,
            court_label=self.court_label,
            doc_type=doc_type,
            n_pages=n_pages,
            layout_ok=layout_ok,
            source_path=pdf_path,
            cid_glyphs=sum(
                ln.count("(cid:") for _pno, lines in source_pages for ln in lines
            ),
        )
        self._apply_headmatter(doc, headmatter)

        # Some document styles (e.g. a certificate of judgment) are identified
        # but deliberately not parsed into opinions.
        if doc_type in self.SKIP_BODY_TYPES:
            doc.warnings.append(f"body not parsed for doc_type={doc_type}")
            if not layout_ok:
                doc.warnings.append("layout does not match expected court format")
            self._sweep_residual(doc, source_pages)
            return doc

        opinion_ranges = []
        for j, ai in enumerate(author_indices):
            end = (
                author_indices[j + 1]
                if j + 1 < len(author_indices)
                else len(all_segments)
            )
            opinion_ranges.append((ai, end))

        # Footnotes on pages before the first opinion belong to headmatter.
        first_op_page = (
            all_segments[opinion_ranges[0][0]][0]
            if opinion_ranges and all_segments
            else None
        )
        seen_labels: set = set()
        if first_op_page is not None:
            hm_pages = {pno for pno in footnote_lines_by_page if pno < first_op_page}
            if hm_pages:
                doc.headmatter_footnotes = self.build_footnotes(
                    hm_pages, footnote_lines_by_page, seen_labels=seen_labels
                )
        elif footnote_lines_by_page:
            # No authored opinion (an order / notice): the footnote-zone text
            # still has to be accounted for, so attach every footnote to the
            # headmatter rather than dropping it.
            doc.headmatter_footnotes = self.build_footnotes(
                set(footnote_lines_by_page),
                footnote_lines_by_page,
                seen_labels=seen_labels,
            )

        # Exclusive page ownership so shared-page footnotes aren't duplicated.
        op_start_pages = [all_segments[s][0] for s, _ in opinion_ranges]
        for idx, (op_start, op_end) in enumerate(opinion_ranges):
            start_pg = op_start_pages[idx]
            end_pg = (
                op_start_pages[idx + 1] - 1
                if idx + 1 < len(op_start_pages)
                else n_pages
            )
            owned_pages = set(range(start_pg, end_pg + 1))
            owned_fn = {
                p: lines
                for p, lines in footnote_lines_by_page.items()
                if p in owned_pages
            }
            doc.opinions.append(
                self.build_opinion(
                    op_start,
                    op_end,
                    all_segments=all_segments,
                    footnote_lines_by_page=owned_fn,
                    images_by_page=images_by_page,
                    tables_by_page=tables_by_page,
                )
            )

        if not layout_ok:
            doc.warnings.append("layout does not match expected court format")
        fp = getattr(self, "_caption_fp", (None, None, None))
        if fp and fp[2]:
            doc.caption_box = dict(doc.caption_box or {})
            doc.caption_box["fp_id"], doc.caption_box["fp_style"] = fp[1], fp[2]
        self._sweep_residual(doc, source_pages)
        return doc

    def _sweep_residual(self, doc: ExtractedDocument, source_pages) -> None:
        """Completeness safety net: any source line the pipeline placed in no
        rendered section lands in ``doc.residual`` (tagged content/furniture),
        so nothing is silently lost — it surfaces in the Removed box."""
        try:
            from .audit import sweep_unplaced

            doc.residual = sweep_unplaced(doc, source_pages)
        except Exception as e:  # the sweep is a safety net, never a hard failure
            doc.warnings.append(f"residual sweep failed: {type(e).__name__}: {e}")

    def _apply_headmatter(self, doc: ExtractedDocument, hm: dict) -> None:
        """Copy the recognized headmatter dict onto the document fields."""
        if hm.get("court"):
            doc.court_label = hm["court"]
        doc.decision_date = hm.get("decisiondate")
        doc.docket_number = hm.get("docketnumber")
        doc.other_docket = hm.get("otherdocket")
        parties = hm.get("parties")
        if isinstance(parties, str):
            parties = [parties]
        doc.parties = list(parties or [])
        doc.motion = hm.get("motion")
        doc.history = hm.get("history")
        doc.parent_case = hm.get("parentcase")
        doc.lower_court = hm.get("lowercourt")
        doc.disposition = hm.get("disposition")
        doc.attorneys = hm.get("attorneys")
        doc.judges = hm.get("judges")
        doc.submitted = hm.get("submitted")
        doc.summary = hm.get("summary") or []
        doc.headmatter_lines = hm.get("headmatter_lines") or []
        doc.caption_box = hm.get("caption_box")
        doc.dropped = hm.get("dropped") or []
        if hm.get("syllabus"):
            doc.syllabus = hm["syllabus"]

    # ====================================================================
    # DOCUMENT-TYPE IDENTIFIER
    # ====================================================================
    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        """Identify the document *style*: opinion / order / notice / unknown.

        Not every PDF a court publishes is an authored opinion. The default
        heuristic: an authored byline => OPINION; otherwise look at the text
        for order / notice cues. Subclasses refine this for their court."""
        if author_indices:
            return DocType.OPINION
        text = " ".join(
            (l.get("text") or "") for _, seg, _ in all_segments for l in seg
        ).lower()
        if not text.strip():
            return DocType.UNKNOWN
        if any(cue in text for cue in _ORDER_CUES):
            return DocType.ORDER
        if any(cue in text for cue in _NOTICE_CUES):
            return DocType.NOTICE
        return DocType.UNKNOWN

    # ====================================================================
    # PAGE-1 HORIZONTAL RULES
    # ====================================================================
    def _page1_rules(self, p1) -> list:
        """Tops of horizontal rules on page 1 (caption-zone dividers).
        The same visual rule may be a hairline RECT, a vector LINE, or a
        small embedded IMAGE — collect all three, excluding caption-box
        internals and text underlines."""
        cap_div = self.find_caption_divider(p1)

        def _outside_caption(top):
            if cap_div is None:
                return True
            cap_top, cap_bot = cap_div[1], cap_div[2]
            return not (cap_top - 2 <= top <= cap_bot + 6)

        p1_lines = p1.extract_text_lines()

        def _is_underline(top):
            for tl in p1_lines:
                if 0 <= (top - tl["bottom"]) <= 5:
                    return True
            return False

        # Every thin rule span rides along UNFILTERED for the open-caption
        # fold — it claims rules inside its own caption zone (including ones
        # the divider filters call caption-internal) and renders each at its
        # true width/side rather than as a full-width divider. Verticals ride
        # along too: a drawn mid rule between the caption columns renders as
        # the '|' divider, not as whitespace.
        spans = []  # (top, x0, x1)
        vspans = []  # (x, top, bottom)
        for r in p1.rects:
            if r["height"] < 2 and (r["x1"] - r["x0"]) > 50:
                spans.append((r["top"], r["x0"], r["x1"]))
            elif (r["x1"] - r["x0"]) < 2 and r["height"] > 30:
                vspans.append((r["x0"], r["top"], r["bottom"]))
        for ln in p1.lines:
            if abs(ln["x1"] - ln["x0"]) > 50:
                spans.append(
                    (ln["top"], min(ln["x0"], ln["x1"]), max(ln["x0"], ln["x1"]))
                )
            elif (
                abs(ln["x1"] - ln["x0"]) < 2
                and abs(ln["bottom"] - ln["top"]) > 30
            ):
                vspans.append(
                    (ln["x0"], min(ln["top"], ln["bottom"]), max(ln["top"], ln["bottom"]))
                )
        self._p1_rule_spans = sorted(spans)
        self._p1_vrule_spans = sorted(vspans)

        tops = []
        for r in p1.rects:
            if (
                r["height"] < 2
                and (r["x1"] - r["x0"]) > 50
                and _outside_caption(r["top"])
                and not _is_underline(r["top"])
            ):
                tops.append(r["top"])
        for ln in p1.lines:
            if (
                (ln["x1"] - ln["x0"]) > 50
                and _outside_caption(ln["top"])
                and not _is_underline(ln["top"])
            ):
                tops.append(ln["top"])
        for img in p1.images:
            if (
                (img.get("height") or 0) < 5
                and img.get("width", 0) > 50
                and _outside_caption(img["top"])
                and not _is_underline(img["top"])
            ):
                tops.append(img["top"])
        return sorted(tops)

    # ====================================================================
    # TABLES
    # ====================================================================
    def extract_page_tables(self, page) -> list:
        """Return [{'bbox', 'rows'}] for each REAL table — pdfplumber's
        ``find_tables`` flags indented blockquotes as 2-column tables, so
        validate: >=3 rows, >=2 columns each >50% filled."""
        out = []
        try:
            tables = page.find_tables()
        except Exception:
            return out
        for t in tables:
            try:
                rows = t.extract()
            except Exception:
                continue
            if not rows or len(rows) < 3:
                continue
            n_cols = max(len(r) for r in rows)
            if n_cols < 2:
                continue
            col_fills = []
            for c in range(n_cols):
                non_empty = sum(1 for r in rows if c < len(r) and (r[c] or "").strip())
                col_fills.append(non_empty / len(rows))
            if sum(1 for f in col_fills if f > 0.5) < 2:
                continue
            out.append({"bbox": t.bbox, "rows": rows})
        return out

    # ====================================================================
    # IMAGES
    # ====================================================================
    def extract_page_images(self, page) -> list:
        """Return [{page, top, x0, width, height, data}] with ``data`` a
        base64 PNG data URI per embedded image."""
        if not page.images:
            return []
        import base64
        from io import BytesIO

        out = []
        for img in page.images:
            bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
            try:
                cropped = page.crop(bbox)
                pil_img = cropped.to_image(resolution=150).original
                buf = BytesIO()
                pil_img.save(buf, format="PNG")
                data = base64.b64encode(buf.getvalue()).decode("ascii")
            except Exception:
                continue
            out.append(
                {
                    "page": page.page_number,
                    "top": img["top"],
                    "x0": img["x0"],
                    "width": img["width"],
                    "height": img["height"],
                    "data": f"data:image/png;base64,{data}",
                }
            )
        return out

    # ====================================================================
    # PER-PAGE EXTRACTION (overridable for unusual layouts)
    # ====================================================================
    def _page1_caption_box(self, page) -> Optional[dict]:
        """Geometry of a ruled caption box on page 1: the vertical divider
        rule and the horizontal rules, for a faithful headmatter facsimile.
        Returns None if there are no such rules."""
        verts = []
        for r in page.rects:
            if (r["x1"] - r["x0"]) < 2 and (r["bottom"] - r["top"]) > 30:
                verts.append(
                    (round(r["x0"], 1), round(r["top"], 1), round(r["bottom"], 1))
                )
        vx = vtop = vbottom = None
        if verts:
            # The COLUMN divider is the vertical nearest mid-page — a boxed
            # caption also has edge verticals, which must not win.
            mid = page.width / 2
            best = min(verts, key=lambda v: abs(v[0] - mid))
            vx, vtop, vbottom = best
        hrules = []
        for r in page.rects:
            if (r["bottom"] - r["top"]) < 2 and (r["x1"] - r["x0"]) > 20:
                hrules.append(
                    (round(r["top"], 1), round(r["x0"], 1), round(r["x1"], 1))
                )
        if vx is None and not hrules:
            return None
        return {
            "vx": vx,
            "vtop": vtop,
            "vbottom": vbottom,
            "hrules": hrules,
            "verts": verts,
        }

    def find_caption_divider(self, page):
        """Return (x, top, bottom) of a vertical caption-column divider, or
        None. Some courts draw the caption as a two-column box with a
        vertical rule down the middle. (A court with stacked/consolidated
        caption boxes whose divider must span them all overrides this in its
        own file; see akd.py.)"""
        for r in page.rects:
            if r["width"] < 2 and r["height"] > 30:
                return r["x0"], r["top"], r["bottom"]
        for ln in page.lines:
            x0 = ln["x0"]
            x1 = ln.get("x1", x0)
            if abs(x1 - x0) < 2 and (ln["bottom"] - ln["top"]) > 30:
                return x0, ln["top"], ln["bottom"]
        return None

    @staticmethod
    def _text_lines(source) -> list:
        """``extract_text_lines`` that keeps the real space characters in each
        line's char list (``keep_blank_chars=True``).

        pdfplumber otherwise consumes spaces as word separators and drops them
        from ``line['chars']``, leaving the body rebuild (``line_inline_text`` /
        ``line_plain_text``) to re-infer word breaks from x-gaps. That fails on
        tightly tracked fonts — Connecticut's Century Schoolbook sets the
        inter-word gap at ~1.4pt, just under the 1.5pt space threshold, so
        'and that, because' rebuilt as 'andthat,because'. Keeping the real
        spaces lets the rebuild emit them directly; the gap heuristic still
        covers lines that genuinely lack space glyphs."""
        return source.extract_text_lines(keep_blank_chars=True)

    @staticmethod
    def _merge_interleaved(lines):
        """An italic span set on a slightly offset baseline becomes its own
        line object ('Bell Atl. Corp. v. Twombly' floating 4.8pt above its
        roman host line) and would sort mid-sentence. Two lines whose
        vertical extents overlap strongly and whose glyphs interleave
        without colliding are ONE visual row — merge them in x order."""
        if len(lines) < 2:
            return lines
        lines = sorted(lines, key=lambda l: (l["top"], l["x0"]))
        out = [lines[0]]
        for ln in lines[1:]:
            prev = out[-1]
            v_overlap = min(prev["bottom"], ln["bottom"]) - max(
                prev["top"], ln["top"]
            )
            min_h = max(
                min(prev["bottom"] - prev["top"], ln["bottom"] - ln["top"]), 1.0
            )
            merged_chars = sorted(
                list(prev.get("chars") or []) + list(ln.get("chars") or []),
                key=lambda c: c["x0"],
            )
            if merged_chars and v_overlap > 0.45 * min_h:
                union = max(c["x1"] for c in merged_chars) - min(
                    c["x0"] for c in merged_chars
                )
                glyphs = sum(c["x1"] - c["x0"] for c in merged_chars)
                if glyphs <= union * 1.05:  # interleaved, not colliding
                    m = dict(prev)
                    m["chars"] = merged_chars
                    m["x0"] = min(prev["x0"], ln["x0"])
                    m["x1"] = max(prev["x1"], ln["x1"])
                    m["top"] = min(prev["top"], ln["top"])
                    m["bottom"] = max(prev["bottom"], ln["bottom"])
                    m["text"] = "".join(c["text"] for c in merged_chars)
                    out[-1] = m
                    continue
            out.append(ln)
        return out

    def correct_page_geometry(self, page) -> None:
        """Hook: adjust raw char geometry on ``page`` (in place) before any line
        clustering. Default no-op. A court whose font declares a broken glyph
        bounding box overrides this to snap chars back to their true row (see
        Maine); the completeness audit calls it too, so it reads the same
        corrected text the extractor does."""

    def page_lines(self, page) -> list:
        """Return text lines after filtering header/footer margins. If the
        page has a vertical caption-column divider, split chars into
        left/right columns BEFORE clustering so the columns don't merge."""
        self.correct_page_geometry(page)
        divider = self.find_caption_divider(page)
        if divider is None:
            lines = self._text_lines(page.filter(self.filter_margins))
            lines = self._merge_interleaved(lines)
            self._tag_underlined_chars(page, lines)
            return self._maybe_drop_running_header(page, lines)

        div_x, div_top, div_bot = divider

        def in_body_margin(obj):
            return self.filter_margins(obj)

        def outside_caption(obj):
            return in_body_margin(obj) and not (div_top <= obj["top"] <= div_bot)

        def left_of_divider(obj):
            return (
                in_body_margin(obj)
                and div_top <= obj["top"] <= div_bot
                and obj["x1"] <= div_x
            )

        def right_of_divider(obj):
            return (
                in_body_margin(obj)
                and div_top <= obj["top"] <= div_bot
                and obj["x0"] >= div_x
            )

        out_lines = self._text_lines(page.filter(outside_caption))
        for l in out_lines:
            l["_caption_col"] = None
        left_lines = self._text_lines(page.filter(left_of_divider))
        for l in left_lines:
            l["_caption_col"] = "L"
        right_lines = self._text_lines(page.filter(right_of_divider))
        for l in right_lines:
            l["_caption_col"] = "R"
        lines = out_lines + left_lines + right_lines
        lines.sort(key=lambda l: (l["top"], l["x0"]))
        self._tag_underlined_chars(page, lines)
        return self._maybe_drop_running_header(page, lines)

    def _maybe_drop_running_header(self, page, lines) -> list:
        if self.running_header_docket and page.page_number > 1 and lines:
            return self._drop_running_header(lines)
        return lines

    def _drop_running_header(self, lines) -> list:
        """Drop a contiguous block of docket-number lines from the top of a
        continuation page. The header height varies (consolidated cases wrap
        over several lines), so anchor on the docket predicate and stop at the
        first non-docket line."""
        drop = set()
        for ln in sorted(lines, key=lambda l: l.get("top", 0)):
            if ln.get("top", 0) > self.running_header_max_top:
                break
            if self.is_docket_line(ln.get("text") or ""):
                drop.add(id(ln))
            else:
                break
        if not drop:
            return lines
        return [l for l in lines if id(l) not in drop]

    def is_docket_line(self, text) -> bool:
        """Hook: True if ``text`` is a docket-number running-header line.
        Default False; courts using ``running_header_docket`` implement it."""
        return False

    def _is_separator_text(self, line) -> bool:
        text = (line.get("text") or "").strip()
        return len(text) >= 4 and set(text).issubset({"_", "-", "=", " "})

    @staticmethod
    def _is_page_number_text(text: str) -> bool:
        """True if ``text`` is just a page number ('4' / '- 12 -' / 'Page 3'),
        possibly with surrounding dashes — body furniture, not a paragraph."""
        import re as _re

        t = _re.sub(r"<[^>]+>", "", text).strip()
        low = t.lower()
        if low.startswith("page "):
            t = t[5:].strip()
        core = t.strip("-–—  ")
        return core.isdigit() and len(core) <= 4

    def _tag_underlined_chars(self, page, lines) -> None:
        """Mark chars whose glyph is underlined by a hairline rect near the
        baseline. Sets ``_underline=True`` on the char dicts."""
        rects = [
            r for r in page.rects if r.get("height", 0) < 2 and (r["x1"] - r["x0"]) > 6
        ]
        if not rects:
            return
        for line in lines:
            chars = line.get("chars") or []
            if not chars:
                continue
            baseline = max(c["bottom"] for c in chars)
            line_rects = [
                r
                for r in rects
                if (
                    self.underline_offset_min
                    <= (r["top"] - baseline)
                    <= self.underline_offset_max
                )
                and r["x0"] < chars[-1]["x1"]
                and r["x1"] > chars[0]["x0"]
            ]
            if not line_rects:
                continue
            for c in chars:
                cmid = (c["x0"] + c["x1"]) / 2
                for r in line_rects:
                    if r["x0"] - 1 <= cmid <= r["x1"] + 1:
                        c["_underline"] = True
                        break

    def filter_margins(self, obj):
        if obj["top"] < self.margin_top or obj["top"] > self.margin_bottom:
            return None
        return True

    def find_footnote_separator(self, page) -> Optional[float]:
        """y (top) of a footnote-zone separator rect, or None.

        If ``footnote_sep_rect`` is configured, the separator is the rect whose
        left/right edges match exactly. Otherwise: a thin horizontal rule
        anchored near the body baseline, >=100pt wide, in the bottom half."""
        if self.footnote_sep_structural:
            return self._footnote_sep_structural(page)
        if self.footnote_sep_rect is not None:
            sx0, sx1 = self.footnote_sep_rect
            for r in page.rects:
                if r["x0"] == sx0 and r["x1"] == sx1:
                    return r["top"]
            return None
        cutoff = page.height * 0.55
        x0_max = self.body_baseline_x0 + 4
        divider = self.find_caption_divider(page)
        cap_bot = divider[2] if divider else None
        candidates = []
        for r in page.rects:
            if not (
                r["height"] < 2
                and (r["x1"] - r["x0"]) >= 100
                and r["x0"] <= x0_max
                and r["top"] > cutoff
            ):
                continue
            if cap_bot is not None and abs(r["top"] - cap_bot) <= 4:
                continue
            if not self._rule_over_footnotes(page, r["top"]):
                continue
            candidates.append(r)
        if candidates:
            return min(candidates, key=lambda r: r["top"])["top"]
        return self._footnote_sep_text(page)

    def footnote_sep_fixed_left_rule(self, page, width=144.0, tol=6.0):
        """Footnote separator = the fixed-width thin rule the court draws at the
        left body margin (a 2-inch / 144pt rule is the common Word/CM-ECF and
        reporter footnote divider), with text directly below it. Keyed on that
        known separator — no positional cutoff — so it is found wherever the
        rule falls: near the page foot on a short footnote, high up on a
        continuation page whose long footnote fills most of the column (mich).
        Reliable where the footnote text is BODY-sized, so the 'small text below
        the rule' heuristic can't see the boundary. Returns the topmost such
        rule's top, or None. The width/x0 signature is distinct from a caption
        divider (full-width) or a right-shifted signature rule, so no page-
        position fence is needed."""
        x0_max = self.body_baseline_x0 + 4
        best = None
        for r in page.rects:
            if r["height"] >= 2.5:
                continue
            if abs((r["x1"] - r["x0"]) - width) > tol:
                continue
            if r["x0"] > x0_max:
                continue
            if not any(
                r["top"] < c["top"] < page.height and (c.get("text") or "").strip()
                for c in page.chars
            ):
                continue
            if best is None or r["top"] < best:
                best = r["top"]
        return best

    def _footnote_sep_structural(self, page) -> Optional[float]:
        """Structural footnote-separator detection for body-size-footnote
        courts (``footnote_sep_structural``): a thin rule at the body's left
        margin, standing clear of any text line (a rule inside a text line's
        band is a case-name underline, not a separator), with footnote matter
        below it — either a raised label digit, or single-spaced text where
        the body is double-spaced. Caption shelves and conformed-signature
        rules carry double-spaced text below and drop out."""
        chars = [c for c in page.chars if (c.get("text") or "").strip()]
        if not chars:
            return None
        body = Counter(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        pw, cutoff = page.width, page.height * 0.45
        text_lines = page.extract_text_lines()

        cands = []
        for r in page.rects:
            if (
                r["bottom"] - r["top"] < 2.5
                and (r["x1"] - r["x0"]) >= 60
                and r["x0"] < pw * 0.35
                and r["top"] > cutoff
            ):
                cands.append((r["top"], r["x0"], r["x1"]))
        for ln in page.lines:
            if (
                abs(ln["bottom"] - ln["top"]) < 2.5
                and abs(ln["x1"] - ln["x0"]) >= 60
                and min(ln["x0"], ln["x1"]) < pw * 0.35
                and ln["top"] > cutoff
            ):
                cands.append(
                    (ln["top"], min(ln["x0"], ln["x1"]), max(ln["x0"], ln["x1"]))
                )

        good = []
        for top, rx0, rx1 in cands:
            # An underline sits INSIDE the band of the text line it decorates.
            if any(
                tl["top"] - 1 <= top <= tl["bottom"] + 2
                and tl["x0"] < rx1
                and tl["x1"] > rx0
                for tl in text_lines
            ):
                continue
            below = sorted(
                (tl for tl in text_lines if tl["top"] > top + 1),
                key=lambda tl: tl["top"],
            )[:4]
            if not below:
                continue
            first_chars = below[0].get("chars") or []
            label = first_chars and round(first_chars[0].get("size", 0)) <= body - 3
            gaps = [b["top"] - a["top"] for a, b in zip(below, below[1:])]
            single = gaps and gaps[0] < body * 1.4  # single vs double leading
            if label or single:
                good.append(top)
        return min(good) if good else None

    def _footnote_sep_text(self, page) -> Optional[float]:
        """Top of a full-measure underscore-TEXT footnote separator in the lower
        half of the page, or None. Gated by ``footnote_sep_text_min_width`` —
        for courts (e.g. Utah) that draw the separator as a line of '_' text
        rather than a vector rule. The line itself is later dropped from the
        footnote flow by ``_is_separator_text``."""
        if self.footnote_sep_text_min_width is None:
            return None
        cutoff = page.height * 0.5
        best = None
        for ln in page.extract_text_lines():
            t = (ln.get("text") or "").strip()
            # Width (footnote_sep_text_min_width) is the real gate; the char
            # floor only rejects a 1–2 char stray. A short 8pt rule (Oregon's
            # ~14-char '____' band) is a valid separator, so keep the floor low.
            if len(t) < 6 or any(c != "_" for c in t):
                continue
            if ln["top"] <= cutoff:
                continue
            if (ln["x1"] - ln["x0"]) < self.footnote_sep_text_min_width:
                continue
            if best is None or ln["top"] < best:
                best = ln["top"]
        return best

    def _rule_over_footnotes(self, page, rule_top) -> bool:
        """Discriminate a footnote separator from a full-width section/caption
        divider by what sits below it. A footnote rule has *footnote-size* text
        below — set smaller than the body text just above it. A divider (e.g.
        the rule above 'MEMORANDUM OPINION') has body-size text below, so the
        body just resumes; treating it as a footnote rule would shove that body
        into the footnote flow (the ded bug).

        Width can't make this call: a full-measure footnote rule and a
        full-measure divider are the same ~0.76-of-page width. Returns True when
        the rule should be taken as a footnote separator."""
        above, below = [], []
        for ln in page.extract_text_lines():
            chars = ln.get("chars") or []
            sizes = [c["size"] for c in chars if c.get("size")]
            if not sizes:
                continue
            sz = median(sizes)
            top = ln["top"]
            if rule_top - 120 <= top < rule_top - 2:
                above.append(sz)
            elif rule_top + 2 < top <= rule_top + 200:
                below.append(sz)
        if not below:
            return False  # nothing below -> not a footnote rule
        if not above:
            return True  # footnote-heavy page with no body just above
        return median(below) < median(above) - 0.75

    # ====================================================================
    # SEGMENTATION (lines -> segments)
    # ====================================================================
    def segment_lines(self, lines, page_width) -> list:
        """Group lines into segments using zone/font/bold/align/separator."""
        zones = []
        for i, line in enumerate(lines):
            # A '_seg_break' line opens just below a DRAWN structural rule
            # (wvnd's Kleeh title rule): its upstairs neighbor sits across
            # the rule and must not color its zone.
            prev_top = (
                lines[i - 1]["top"]
                if i > 0 and not line.get("_seg_break")
                else None
            )
            next_top = lines[i + 1]["top"] if i + 1 < len(lines) else None
            zones.append(self.line_zone(prev_top, line["top"], next_top))

        segments = []
        current = []
        prev_size = prev_bold = prev_align = prev_top = prev_zone = None
        for i, line in enumerate(lines):
            size, _, bold = self.line_meta(line)
            align = self.line_alignment(line, page_width)
            sep = self.is_separator_line(line)
            zone = zones[i]
            if line.get("_seg_break") and current:
                segments.append(current)
                current = []
                prev_size = prev_bold = prev_align = prev_top = prev_zone = None

            if sep:
                if current:
                    segments.append(current)
                    current = []
                segments.append([line])
                prev_size, prev_bold, prev_align, prev_top, prev_zone = (
                    size,
                    bold,
                    align,
                    line["top"],
                    None,
                )
                continue

            if current:
                gap = line["top"] - prev_top
                big_gap = gap > self.gap_double_max
                size_changed = abs(size - prev_size) >= 1.0
                bold_changed = bold != prev_bold and self.bold_breaks_segment
                # C→L is not a structural change: it just means the last line
                # of a justified paragraph is short and doesn't reach the right
                # margin. All other alignment transitions remain boundaries.
                align_changed = align != prev_align and not (
                    prev_align == "C" and align == "L"
                )
                zone_changed = prev_zone is not None and zone != prev_zone
                col_changed = line.get("_caption_col") != current[-1].get(
                    "_caption_col"
                )
                author_break = (
                    self.parse_author_line((line.get("text") or "").strip()) is not None
                )
                # Indent-aware segmentation (blockquote_by_indent courts). A run
                # deeply indented past a first-line paragraph indent is a block
                # quote; when the body and the quote share the same leading (a
                # fully single-spaced opinion), the gap/zone signals can't split
                # it, so the quote dissolves into the body segment. Break when a
                # line crosses that deep-indent boundary in either direction so
                # the quote lands in its own segment — geometry, not spacing.
                # Inside such a block, the L↔C flip from short centered lines is
                # not a structural boundary, so suppress the alignment break.
                indent_changed = False
                if self.blockquote_by_indent:
                    deep = self.body_baseline_x0 + 1.5 * self.indent_step
                    # A line at the deep indent that OPENS a numbered paragraph
                    # ('¶13 ...') is a first-line indent, not a block-quote edge
                    # — its continuations wrap back to the body margin. Excluding
                    # it stops the quote-split from fragmenting such a paragraph
                    # on courts whose ¶ indent equals the quote indent (wis).
                    prev_deep = current[-1]["x0"] >= deep and not (
                        self._begins_paragraph_block([current[-1]])
                    )
                    this_deep = line["x0"] >= deep and not (
                        self._begins_paragraph_block([line])
                    )
                    indent_changed = prev_deep != this_deep
                    if prev_deep and this_deep:
                        align_changed = False
                if (
                    big_gap
                    or size_changed
                    or bold_changed
                    or align_changed
                    or zone_changed
                    or col_changed
                    or author_break
                    or indent_changed
                ):
                    segments.append(current)
                    current = []

            current.append(line)
            prev_size, prev_bold, prev_align, prev_top, prev_zone = (
                size,
                bold,
                align,
                line["top"],
                zone,
            )
        if current:
            segments.append(current)
        return segments

    def classify_segment(self, seg) -> str:
        """notice / blockquote / body / single / spaced."""
        if len(seg) == 1:
            return "single"
        gaps = [seg[i + 1]["top"] - seg[i]["top"] for i in range(len(seg) - 1)]
        med = median(gaps)
        if med < self.gap_tight_max:
            kind = "notice"
        elif med < self.gap_single_max:
            kind = "blockquote"
        elif med < self.gap_double_max:
            kind = "body"
        else:
            kind = "spaced"
        # A both-margins-indented run is a block quote regardless of which tight
        # gap band its (often sub-body) leading lands in — geometry, not gaps.
        if (
            self.blockquote_by_indent
            and kind in ("notice", "body")
            and self._is_indented_blockquote(seg)
        ):
            kind = "blockquote"
        return kind

    def _is_indented_blockquote(self, seg) -> bool:
        """True if ``seg`` is a multi-line run indented on BOTH margins — the
        geometric signature of a block quote: left indented in from the body
        margin, the longest line still short of the right margin (where a body
        paragraph runs flush), AND a consistent flush-left edge (≥2 lines share
        the block's left column). The last requirement rejects centered/short
        headings, which are also both-margins-indented but vary their left edge
        line-to-line."""
        if len(seg) < 2:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        left = self.body_baseline_x0 + self.para_indent_min
        right = pw - self.body_baseline_x0
        x0s = [l["x0"] for l in seg]
        x1s = [l["x1"] for l in seg]
        # Indented in from the left, longest line short of the right — and the
        # left edge modest (a body quote indents a step or two; a signature /
        # right-aligned block sits out past ~40% of the page and is NOT a quote).
        if not (left <= min(x0s) <= pw * 0.4 and max(x1s) <= right - 24):
            return False
        edge = min(x0s)
        return sum(1 for x in x0s if abs(x - edge) <= 3) >= 2

    # ====================================================================
    # LAYOUT PRIMITIVES
    # ====================================================================
    def line_meta(self, line) -> tuple:
        chars = line.get("chars") or []
        if not chars:
            return 0.0, "", False
        sizes = Counter(round(c.get("size", 0), 1) for c in chars)
        fonts = Counter((c.get("fontname") or "") for c in chars)
        size = sizes.most_common(1)[0][0]
        fontname = fonts.most_common(1)[0][0]
        return size, fontname.split("+")[-1], "Bold" in fontname

    def line_alignment(self, line, page_width) -> str:
        x0 = line["x0"]
        x1 = line["x1"]
        width = x1 - x0
        cx = (x0 + x1) / 2
        if x0 > 100 and abs(cx - page_width / 2) < 25 and width < page_width * 0.55:
            a = "C"
        elif x0 <= 200:
            a = "L"
        elif x0 > page_width * 0.6:
            a = "R"
        else:
            a = "L"
        # A wide, genuinely midpoint-centered banner at/above
        # banner_center_min_size is centered regardless of width (it spans
        # past the width cap that keeps justified body lines left-aligned).
        if a != "C" and self.banner_center_min_size is not None:
            size, _, _ = self.line_meta(line)
            if size >= self.banner_center_min_size and abs(cx - page_width / 2) < 25:
                a = "C"
        return a

    def gap_bucket(self, g) -> Optional[str]:
        if g is None:
            return None
        if g < self.gap_tight_max:
            return "tight"
        if g < self.gap_single_max:
            return "single"
        if g < self.gap_double_max:
            return "double"
        return "boundary"

    def line_zone(self, prev_top, top, next_top) -> str:
        gb = self.gap_bucket((top - prev_top) if prev_top is not None else None)
        ga = self.gap_bucket((next_top - top) if next_top is not None else None)
        if gb == "tight" or ga == "tight":
            return "tight"
        if gb == "single" or ga == "single":
            return "single"
        if gb == "double" or ga == "double":
            return "double"
        return "isolated"

    def is_separator_line(self, line) -> bool:
        t = (line.get("text") or "").strip()
        return len(t) >= 4 and all(c in "_-—–" for c in t)

    # ====================================================================
    # AUTHOR DETECTION
    # ====================================================================
    def _author_pattern(self):
        """The one place we keep a regex: the author-byline grammar.

        An author line is 'NAME, [Chief/Presiding/...]TITLE[ (kind) | , kind].'
        — a small grammar with an optional name-continuation ({0,4} initials
        or words), an optional title prefix, and two alternative 'kind' forms.
        Matching it correctly needs the alternation + backtracking a regex
        gives for free; a hand-rolled parser here would be longer and easier
        to get subtly wrong. Name may be an ALL-CAPS surname, Title Case, or a
        full given-name + initials + surname, with optional Mc/Mac prefix."""
        titles = "|".join(re.escape(t) for t in self.author_titles)
        return re.compile(
            r"^(?P<name>(?:Mc|Mac)?[A-Z][A-Za-z]+"
            r"(?:[\s-](?:[A-Z]\.|[A-Z][A-Za-z]+)){0,4})"
            rf",\s+(?P<title>"
            r"(?:Chief\s+|Presiding\s+|Associate\s+|Senior\s+|Retired\s+|Acting\s+)?"
            rf"(?:{titles}))"
            r"(?:"
            r"\s*\((?P<kind1>[^)]+)\)"
            r"|,\s+(?P<kind2>[^.]+?)"
            r")?"
            r"\.?$"
        )

    def skip_headmatter_segment(self, seg) -> bool:
        """Hook: return True to drop a segment from the raw headmatter dump.
        Honors ``skip_notice_headmatter``; subclasses may extend."""
        if self.skip_notice_headmatter and self.classify_segment(seg) == "notice":
            return True
        return False

    @staticmethod
    def _strip_trailing_author_mark(text: str) -> str:
        """Strip a trailing footnote-reference mark from an author byline
        (e.g. 'McCOOL, Justice.1' -> 'McCOOL, Justice.'). No regex."""
        marks = set("0123456789*†‡")
        t = text.rstrip()
        i = len(t)
        while i > 0 and t[i - 1] in marks:
            i -= 1
        if i == len(t):
            return text
        return t[:i].rstrip()

    def split_author_line(self, line) -> tuple:
        """Hook: split an author line into (author_text, extra_body_lines).
        Default: the whole line is the author, no inline body content."""
        return (line.get("text") or "").strip(), []

    def parse_author_line(self, text) -> Optional[tuple]:
        """Return (name, title, kind) or None."""
        text = text.strip()
        if self.strip_author_trailing_mark:
            text = self._strip_trailing_author_mark(text)
        if _is_per_curiam(text):
            return ("PER CURIAM", "per curiam", None)
        m = self._author_pattern().match(text)
        if not m:
            return None
        kind = m.group("kind1") or m.group("kind2")
        return m.group("name"), m.group("title"), kind

    def _byline_at(self, line) -> bool:
        """True if ``line`` begins an opinion (an author byline). Default uses
        the byline parser; courts with bold/inline bylines override."""
        return self.parse_author_line((line.get("text") or "").strip()) is not None

    def _split_segments_at_bylines(self, all_segments) -> list:
        """Split any segment at an interior author byline, so every opinion's
        byline starts its own segment. A byline can appear mid-segment when it
        runs inline with the opinion text after a preceding disposition. Courts
        whose bylines always start a segment (e.g. Alabama) are unaffected."""
        out = []
        for page_no, seg, kind in all_segments:
            cuts = [j for j in range(1, len(seg)) if self._byline_at(seg[j])]
            if not cuts:
                out.append((page_no, seg, kind))
                continue
            bounds = [0] + cuts + [len(seg)]
            for a, b in zip(bounds, bounds[1:]):
                sub = seg[a:b]
                if sub:
                    out.append((page_no, sub, self.classify_segment(sub)))
        return out

    def find_authors(self, all_segments) -> list:
        """Indices into all_segments where each opinion starts."""
        out = []
        for i, (_, seg, kind) in enumerate(all_segments):
            if kind == "notice":
                continue
            if self.parse_author_line(seg[0]["text"].strip()):
                out.append(i)
        return out

    def normalize_opinion_type(self, kind) -> str:
        if kind is None:
            return "majority"
        k = kind.lower()
        # The combined concur-and-dissent check must precede the bare 'dissent'
        # check, or 'concurring in part and dissenting in part' short-circuits to
        # a plain dissent.
        if "concur" in k and "part" in k and "dissent" in k:
            return "concurring-in-part-and-dissenting-in-part"
        if "dissent" in k:
            return "dissent"
        if "concur" in k and "result" in k:
            return "concurrence-in-result"
        if "concur" in k:
            return "concurrence"
        return k.replace(" ", "-")

    # ====================================================================
    # HEADMATTER (default = verbatim dump; court bases override)
    # ====================================================================
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Default: dump every headmatter line verbatim, in document order,
        preserving inline formatting. Centered lines wrapped in <centered>;
        tight left-aligned runs joined into one paragraph; page-1 rules
        inserted as __DIVIDER__ markers. Court bases override for
        field-by-field categorization."""
        items = []
        dropped = []
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                txt = " ".join((l.get("text") or "").strip() for l in seg).strip()
                if txt:
                    dropped.append(txt)
                continue
            for line in seg:
                if not (line.get("text") or "").strip():
                    continue
                pno = line.get("page_number")
                if pno is None and line.get("chars"):
                    pno = line["chars"][0].get("page_number", 1)
                align = self.line_alignment(line, 612)
                col = line.get("_caption_col")
                items.append((pno or 1, line["top"], line, align, col))
        items.sort(key=lambda x: (x[0], x[1]))

        out_events = []
        i = 0
        while i < len(items):
            pno, top, line, align, col = items[i]
            if col in ("L", "R"):
                left, right = [], []
                j = i
                while (
                    j < len(items) and items[j][4] in ("L", "R") and items[j][0] == pno
                ):
                    _, _, lj, _, cj = items[j]
                    (left if cj == "L" else right).append(lj)
                    j += 1

                def render_col(lines):
                    parts = []
                    for ln in lines:
                        t = self.paragraph_text([ln])
                        a = self.line_alignment(ln, 612)
                        if a == "C":
                            t = f"<centered>{t}</centered>"
                        parts.append(t)
                    return parts

                marker = {
                    "__caption__": True,
                    "left": render_col(left),
                    "right": render_col(right),
                }
                out_events.append((pno, top, marker))
                i = j
                continue
            if align == "L":
                group = [line]
                j = i + 1
                baseline = self.body_baseline_x0
                while j < len(items):
                    p2, t2, l2, a2, c2 = items[j]
                    if p2 != pno or a2 != "L" or c2 is not None:
                        break
                    if (t2 - items[j - 1][1]) > 22:
                        break
                    prev_x0 = group[-1].get("x0", 0)
                    this_x0 = l2.get("x0", 0)
                    if this_x0 > prev_x0 + 12 and prev_x0 <= baseline + 6:
                        break
                    group.append(l2)
                    j += 1
                text = " ".join(self.paragraph_text([l]) for l in group)
                out_events.append((pno, top, text))
                i = j
            else:
                text = self.paragraph_text([line])
                if align == "C":
                    text = f"<centered>{text}</centered>"
                out_events.append((pno, top, text))
                i += 1

        for div_top in page1_rules or []:
            out_events.append((1, div_top, self.HEADMATTER_DIVIDER))
        out_events.sort(key=lambda e: (e[0], e[1]))
        return {
            "court": self.court_label,
            "summary": [text for _, _, text in out_events],
            "dropped": dropped,
        }

    # ====================================================================
    # PARAGRAPH SPLITTING (within a segment)
    # ====================================================================
    def classify_paragraph(self, lines) -> str:
        """Return the tag for a paragraph: 'p' or 'blockquote'."""
        return "p"

    def split_body_paragraphs(self, seg) -> list:
        """In a body segment, an indented first line marks a paragraph start.
        The indent threshold scales with the court's body baseline
        (``body_baseline_x0 + para_indent_min``) so wide-margin courts (federal
        circuits at x0≈108-156) split on their real indent rather than a fixed
        x0 — for the default baseline 72 / indent 28 this is the historical
        ``x0 > 100``.

        The baseline is also re-derived from the SEGMENT's own left margin
        (the leftmost / continuation-line x0), floored at the configured
        ``body_baseline_x0``: pleading-paper and shifted-column layouts set
        the body column well right of the page baseline (caed at x0≈104), so
        an absolute threshold would read every continuation line as
        'indented' and emit one paragraph per line. Flooring keeps courts
        that tuned a high baseline unaffected."""
        if not seg:
            return []
        seg_left = min(l["x0"] for l in seg)
        indent_min = max(self.body_baseline_x0, seg_left) + self.para_indent_min
        # Lines must clear a *second* indent threshold to be treated as a
        # multi-line indented block rather than a paragraph first line.
        # A paragraph first line lands just above indent_min; a blockquote
        # sits a full para_indent_min deeper.
        block_min = indent_min + self.para_indent_min
        paras = [[seg[0]]]
        for i in range(1, len(seg)):
            line = seg[i]
            prev = seg[i - 1]
            if line["x0"] > indent_min:
                # Deeply indented AND same x0 as the immediately preceding
                # line: continuation of a multi-line indented block-quote.
                # Otherwise: a new paragraph (first-line indent or level shift).
                if line["x0"] > block_min and abs(line["x0"] - prev["x0"]) <= 3:
                    paras[-1].append(line)
                else:
                    paras.append([line])
            else:
                paras[-1].append(line)
        return self._explode_line_stacks(paras)

    def _explode_line_stacks(self, paras) -> list:
        """Split a *stack* back into one paragraph per line. A group of lines
        in which NO line reaches the right measure never wrapped — a line that
        ends far short of the margin cannot have a continuation, so joining
        the group produced a run-on ('SARAH PIERCE Special Master'). Stacks
        are name/title sign-offs and rosters; prose is protected because any
        real multi-line paragraph has full wrapped lines. Centered groups are
        left joined — a centered heading that wraps IS one heading
        (CLAUDE.md principle 7). Opt-in via ``split_line_stacks`` — proven to
        over-fire on default: Alabama's fidelity-locked no-opinion rosters,
        and two-line ragged sentences ('Delivered and filed on the / 21st day
        of May, 2026.') where neither line reaches the measure."""
        if not self.split_line_stacks:
            return paras
        pw = getattr(self, "_page1_width", None) or 612.0
        right_edge = pw - self.body_baseline_x0
        measure = right_edge - self.body_baseline_x0
        wrap_min = right_edge - 0.15 * measure
        out = []
        for grp in paras:
            # An all-centered group is a wrapped centered heading — one
            # heading, never a stack. A MIXED group (name off-axis over a
            # coincidentally center-ish title line) is still a stack.
            if (
                len(grp) >= 2
                and all(l["x1"] < wrap_min for l in grp)
                and not all(self.line_alignment(l, pw) == "C" for l in grp)
            ):
                out.extend([l] for l in grp)
            else:
                out.append(grp)
        return out

    def _wrap_continuation_max(self) -> float:
        """The largest first-line x0 still treated as a wrapped continuation of
        the previous body paragraph when it lands at the top of a new page (see
        ``build_opinion``). Defaults to the body baseline; hanging-marker courts
        (where wrapped text sits right of the paragraph marker) raise it."""
        return self.body_baseline_x0 + 6

    def _begins_paragraph_block(self, lines) -> bool:
        """Whether ``lines`` itself starts a fresh body paragraph (e.g. a
        numbered-paragraph marker) and so must never be folded into the prior
        paragraph as a page-break continuation. Default: nothing does."""
        return False

    def split_blockquote_paragraphs(self, seg) -> list:
        """In a blockquote segment, a gap > 1.4x median splits paragraphs."""
        if not seg:
            return []
        paras = [[seg[0]]]
        gaps = [seg[i + 1]["top"] - seg[i]["top"] for i in range(len(seg) - 1)] or [0]
        med_gap = median(gaps)
        for i in range(1, len(seg)):
            line = seg[i]
            gap_b = line["top"] - seg[i - 1]["top"]
            if gap_b > med_gap * 1.4:
                paras.append([line])
            else:
                paras[-1].append(line)
        return self._explode_line_stacks(paras)

    def split_footnote_paragraphs(self, lines) -> tuple:
        """Split footnote lines into paragraphs. Returns (paras, fn_baseline).
        A line opens a new paragraph if it both starts with an open quote AND
        is deeper than the footnote baseline; a return from indent to baseline
        also starts a new paragraph."""
        if not lines:
            return [], None
        wrap_x0s = [l["x0"] for l in lines[1:]]
        fn_baseline = (
            Counter(wrap_x0s).most_common(1)[0][0] if wrap_x0s else lines[0]["x0"]
        )
        paras = [[lines[0]]]
        for i in range(1, len(lines)):
            line = lines[i]
            prev = lines[i - 1]
            text = (line.get("text") or "").lstrip()
            starts_quote = text.startswith(('"', "“")) and line["x0"] > fn_baseline + 10
            returned_to_prose = (
                i > 1
                and line["x0"] <= fn_baseline + 4
                and prev["x0"] > fn_baseline + 10
            )
            if starts_quote or returned_to_prose:
                paras.append([line])
            else:
                paras[-1].append(line)
        return paras, fn_baseline

    # ====================================================================
    # TEXT (inline formatting)
    # ====================================================================
    def line_inline_text(self, line) -> str:
        """Render a line's text with inline formatting preserved:
          - <footnotemark>N</footnotemark> for superscript label chars
          - <strong>...</strong> for bold runs
          - <em>...</em> for italic / oblique runs
          - <u>...</u> for underlined runs
        Inserts spaces where the inter-char x-gap exceeds 1.5pt."""
        chars = line.get("chars") or []
        if not chars:
            return ""
        body_size = max(round(c["size"], 1) for c in chars)
        parts = []
        buf = ""
        in_bold = in_italic = in_underline = False
        cur_fn = ""
        prev_x1 = None
        prev_pos = None
        in_brace = False

        def style_wrap(text):
            t = escape(text)
            if in_italic:
                t = f"<em>{t}</em>"
            if in_bold:
                t = f"<strong>{t}</strong>"
            if in_underline:
                t = f"<u>{t}</u>"
            return t

        def flush_buf():
            nonlocal buf
            if not buf:
                return
            parts.append(style_wrap(buf))
            buf = ""

        for c in chars:
            # Some fonts double-emit a ligature glyph ('fi'/'ffl') as two
            # identical chars at the exact same coordinates; extract_text dedups
            # them but the raw char list does not. Skip the overlapping copy so
            # the rebuilt text doesn't read 'offifices' for 'offices'.
            pos = (round(c["x0"], 1), round(c["x1"], 1), c.get("text"))
            if pos == prev_pos:
                continue
            prev_pos = pos
            if self.bracket_pinpoint:
                if c["text"] in "{[":
                    in_brace = True
                elif c["text"] in "}]":
                    in_brace = False
            fn = c.get("fontname") or ""
            ch_bold = "Bold" in fn
            ch_italic = ("Italic" in fn) or ("Oblique" in fn)
            ch_underline = bool(c.get("_underline"))

            if prev_x1 is not None:
                gap = c["x0"] - prev_x1
                if gap > 1.5:
                    if cur_fn:
                        parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
                        cur_fn = ""
                        buf += " "
                    elif buf and not buf.endswith(" "):
                        buf += " "

            small = round(c["size"], 1) <= body_size - 1.5
            is_label = c["text"] in self.FOOTNOTE_LABEL_CHARS and not in_brace
            if small and is_label:
                flush_buf()
                cur_fn += c["text"]
            else:
                if cur_fn:
                    parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
                    cur_fn = ""
                style_changed = (
                    ch_bold != in_bold
                    or ch_italic != in_italic
                    or ch_underline != in_underline
                )
                if style_changed and buf:
                    flush_buf()
                    in_bold, in_italic, in_underline = (
                        ch_bold,
                        ch_italic,
                        ch_underline,
                    )
                elif not buf:
                    in_bold, in_italic, in_underline = (
                        ch_bold,
                        ch_italic,
                        ch_underline,
                    )
                buf += c["text"]
            prev_x1 = c["x1"]

        if cur_fn:
            parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
        flush_buf()
        return "".join(parts)

    def line_plain_text(self, line) -> str:
        """The line's text as plain characters, with the same gap-based space
        insertion ``line_inline_text`` uses but WITHOUT the inline markup tags
        (<strong>/<em>/<footnotemark>/...) or entity escaping.

        Byline/structural parsing needs this: pdfplumber's ``line['text']`` can
        drop the spaces between kerned glyphs (a small-caps name renders as
        'DWIGHT E.TARWATER,J.,delivered'), which breaks the name grammar, while
        ``line_inline_text`` would feed it '<strong>...' markup. This gives the
        correctly-spaced plain text both need."""
        chars = line.get("chars") or []
        if not chars:
            return ""
        out = []
        prev_x1 = None
        prev_pos = None
        for c in chars:
            pos = (round(c["x0"], 1), round(c["x1"], 1), c.get("text"))
            if pos == prev_pos:  # skip a double-emitted ligature glyph
                continue
            prev_pos = pos
            if (
                prev_x1 is not None
                and (c["x0"] - prev_x1) > 1.5
                and out
                and not out[-1].endswith(" ")
            ):
                out.append(" ")
            out.append(c.get("text") or "")
            prev_x1 = c["x1"]
        return "".join(out)

    def paragraph_text(self, lines) -> str:
        return " ".join(self.line_inline_text(l) for l in lines)

    # ====================================================================
    # BODY BUILDING (structured model, not XML)
    # ====================================================================
    def build_opinion(
        self,
        op_start,
        op_end,
        *,
        all_segments,
        footnote_lines_by_page,
        images_by_page=None,
        tables_by_page=None,
    ) -> Opinion:
        images_by_page = images_by_page or {}
        tables_by_page = tables_by_page or {}
        author_seg = all_segments[op_start][1]
        author_text, inline_body_lines = self.split_author_line(author_seg[0])
        # A structurally-detected byline (e.g. a colon form) may not be
        # parseable by parse_author_line; only the kind is needed here.
        _parsed = self.parse_author_line(author_text)
        kind = _parsed[2] if _parsed else None
        op = Opinion(
            type=self.normalize_opinion_type(kind),
            # Justified byline columns leave word-spacing runs in the text
            # ('KELLY  C.  BRONIEC') — collapse to single spaces (verified a
            # no-op on the fidelity-locked Alabama corpus).
            author=" ".join(author_text.split()),
        )

        op_pages = set()
        blocks: list[Block] = []
        last_body_page = [None]

        # The continuation margin of THIS opinion's body — the leftmost body
        # line x0 (indents sit right of it). A page-top line at this margin
        # continues the prior paragraph; the page-break fold is measured from
        # here so shifted columns (pleading paper at x0≈104) fold correctly,
        # not just the page baseline.
        body_xs = [
            l["x0"]
            for k in range(op_start, op_end)
            for l in all_segments[k][1]
            if all_segments[k][2] == "body"
        ]
        op_body_left = min(body_xs) if body_xs else self.body_baseline_x0

        def add_para(tag, lines, page_no):
            if not lines:
                return
            txt = self.paragraph_text(lines)
            if not txt.strip():
                return
            if self.fold_page_numbers and self._is_page_number_text(txt):
                return  # bare page number — drop; merge spans the gap
            first_x0 = lines[0]["x0"]
            # re-base the court's continuation slop on THIS opinion's body
            # column so a shifted column (caed x0≈104) folds page-top
            # continuations — but keep the same tight slop, so block-style
            # courts (no first-line indent) don't over-merge across pages
            wrap_max = max(
                self._wrap_continuation_max(),
                op_body_left + (self._wrap_continuation_max() - self.body_baseline_x0),
            )
            if (
                tag == "p"
                and blocks
                and blocks[-1].kind == "p"
                and last_body_page[0] is not None
                and page_no != last_body_page[0]
                and first_x0 < wrap_max
                and not self._begins_paragraph_block(lines)
            ):
                blocks[-1].text += f' <pagenumber value="{page_no}"/> {txt}'
            else:
                blocks.append(Block(kind=tag, text=txt, page=page_no))
            if tag == "p":
                last_body_page[0] = page_no

        events = []
        for k in range(op_start, op_end):
            page_no, seg, skind = all_segments[k]
            op_pages.add(page_no)
            if skind == "notice" and self.drop_notice_in_body:
                continue
            if k == op_start:
                lines_after = list(inline_body_lines) + list(seg[1:])
                for p in self.split_body_paragraphs(lines_after):
                    if p:
                        events.append((page_no, p[0]["top"], "p", p))
                continue
            if self.is_separator_line(seg[0]):
                continue
            if skind == "body":
                for p in self.split_body_paragraphs(seg):
                    if p:
                        tag = self.classify_paragraph(p)
                        events.append((page_no, p[0]["top"], tag, p))
            elif skind == "blockquote":
                for p in self.split_blockquote_paragraphs(seg):
                    if p:
                        events.append((page_no, p[0]["top"], "blockquote", p))
            elif skind == "single":
                if seg:
                    # classify_paragraph defaults to 'p'; courts whose
                    # blockquotes are geometry-identified (Tennessee) can tag a
                    # stranded single quote line correctly.
                    events.append(
                        (page_no, seg[0]["top"], self.classify_paragraph(seg), seg)
                    )
            elif skind in ("notice", "spaced"):
                # A kept tight/loose segment (single-spaced body on courts with
                # drop_notice_in_body=False) — return it as body paragraphs so
                # nothing is dropped. Alabama never reaches here (it drops
                # notice earlier and has no body 'spaced' segments).
                for p in self.split_body_paragraphs(seg):
                    if p:
                        tag = self.classify_paragraph(p)
                        events.append((page_no, p[0]["top"], tag, p))

        for pno in op_pages:
            for img in images_by_page.get(pno, []):
                events.append((pno, img["top"], "image", img))
        for pno in op_pages:
            for tbl in tables_by_page.get(pno, []):
                events.append((pno, tbl["bbox"][1], "table", tbl))

        events.sort(key=lambda e: (e[0], e[1]))

        for page_no, top, kind_, payload in events:
            if kind_ == "image":
                blocks.append(
                    Block(
                        kind="image",
                        page=page_no,
                        payload={
                            "src": payload["data"],
                            "width": payload["width"],
                            "height": payload["height"],
                        },
                    )
                )
            elif kind_ == "table":
                blocks.append(
                    Block(
                        kind="table",
                        page=page_no,
                        payload={
                            "rows": payload.get("rows") or [],
                        },
                    )
                )
            else:
                add_para(kind_, payload, page_no)

        op.blocks = blocks
        op.footnotes = self.build_footnotes(
            op_pages, footnote_lines_by_page, seen_labels=set()
        )
        return op

    def build_footnotes(self, pages, footnote_lines_by_page, seen_labels=None) -> list:
        """Group footnote lines for ``pages`` into ``Footnote`` objects.
        Cross-page continuation: lines without a leading small-digit label
        belong to the previous footnote."""
        if seen_labels is None:
            seen_labels = set()
        grouped = []  # [(label, [lines])]
        current = []
        current_label = None
        for page_no in sorted(pages):
            for line in footnote_lines_by_page.get(page_no, []):
                label = self.detect_footnote_label(line)
                if label is not None:
                    if current:
                        grouped.append((current_label, current))
                    current_label = label
                    current = [line]
                else:
                    if current:
                        current.append(line)
                    else:
                        current = [line]
                        current_label = "?"
        if current:
            grouped.append((current_label, current))

        out = []
        for label, lines in grouped:
            if label in seen_labels:
                continue
            fn = self.build_footnote(label, lines)
            if fn.paragraphs:
                out.append(fn)
                seen_labels.add(label)
        return out

    def detect_footnote_label(self, line) -> Optional[str]:
        """If ``line`` starts a new footnote, return its label; else None."""
        chars = line.get("chars") or []
        if not chars:
            return None
        body_size = max(round(c["size"], 1) for c in chars)
        first = chars[0]
        first_small = round(first["size"], 1) <= body_size - 1.5
        if not (first_small and first["text"] in self.FOOTNOTE_LABEL_CHARS):
            return None
        label_chars = []
        for c in chars:
            if (
                round(c["size"], 1) <= body_size - 1.5
                and c["text"] in self.FOOTNOTE_LABEL_CHARS
            ):
                label_chars.append(c["text"])
            else:
                break
        return "".join(label_chars) or "?"

    def build_footnote(self, label, lines) -> Footnote:
        fn = Footnote(label=label)
        if not lines:
            return fn
        paras, fn_baseline = self.split_footnote_paragraphs(lines)
        for i, plines in enumerate(paras):
            txt = " ".join(self.line_inline_text(l) for l in plines).strip()
            if i == 0 and txt.startswith("<footnotemark>"):
                end = txt.find("</footnotemark>")
                if end != -1:
                    txt = txt[end + len("</footnotemark>") :].lstrip()
            if not txt:
                continue
            first_text = (plines[0].get("text") or "").lstrip()
            deeper = fn_baseline is not None and plines[0]["x0"] > fn_baseline + 10
            tag = (
                "blockquote" if (first_text.startswith(('"', "“")) and deeper) else "p"
            )
            fn.paragraphs.append((tag, txt))
        return fn
