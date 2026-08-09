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


# Bench words that can never be a judge's surname. The wrapped continuation of
# a byline-shaped sentence opens with one of these, and reading it as a name
# manufactures a byline mid-sentence.
_BENCH_WORDS = frozenset(
    {
        "judge",
        "judges",
        "justice",
        "justices",
        "chief",
        "chancellor",
        "magistrate",
        "commissioner",
    }
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


def _snap_displaced_fragments(chars: list) -> None:
    """Snap a short run of glyphs drawn far off its own baseline back onto the
    row it belongs to — in place, before any line clustering.

    A glyph the body face lacks is fetched from a substitute font, and the
    substitution can carry a large vertical offset. Arizona sets the '¶' of a
    pin cite from Cambria a full 26pt BELOW its line, which is close enough to
    the NEXT row for pdfplumber to cluster it there — and because a row is
    rebuilt in x order, the fragment lands *inside a word*: 'subsection' came
    out 'sub¶se 1c7ti.o n'. That is silent corruption of opinion text, so it
    has to be corrected at char level; by the time lines exist the damage is
    done.

    The hole is the proof. The row the fragment came FROM still has a gap at
    exactly the fragment's x-span, because the glyphs were lifted out of it.
    Requiring the fragment to sit inside that gap and fill most of it — in a
    font the host row does not otherwise use, a real distance away — leaves
    ordinary baseline jitter (an italic run 1pt high, a superscript mark) to
    the line-level merge, which already handles it correctly."""
    printable = [c for c in chars if (c.get("text") or "").strip()]
    if len(printable) < 12:
        return
    rows: dict = {}
    for c in printable:
        rows.setdefault(round(c["top"], 1), []).append(c)
    hosts = {t: v for t, v in rows.items() if len(v) >= 10}
    if not hosts:
        return

    def fonts(cs):
        return {(c.get("fontname") or "").split("+")[-1] for c in cs}

    for top, frag in rows.items():
        if not (1 <= len(frag) <= 6):
            continue
        # The fragment already HAS a line: a bold speaker name set a fraction
        # of a point below the roman text it belongs to. Ordinary line
        # clustering owns that; snapping it would hand it to whichever row's
        # hole it happens to fit, which in a transcript is the NEXT speaker's
        # ('Brown' + 'Tucker' → 'BTruocwkner').
        if any(abs(htop - top) < 4.0 for htop in hosts):
            continue
        f_fonts = fonts(frag)
        fx0 = min(c["x0"] for c in frag)
        fx1 = max(c["x1"] for c in frag)
        best = None
        for htop, hcs in hosts.items():
            gap = abs(htop - top)
            # A REAL displacement, not baseline jitter: an italic run or a
            # superscript sits within a point or two of its row, and the
            # line-level merge already reunites those correctly.
            if not (4.0 <= gap <= 32.0):
                continue
            if f_fonts & fonts(hcs):
                continue
            cs = sorted(hcs, key=lambda c: c["x0"])
            spaces = sorted(
                g for g in (b["x0"] - a["x1"] for a, b in zip(cs, cs[1:])) if g > 0.5
            )
            if not spaces:
                continue
            word_gap = spaces[len(spaces) // 2]
            for a, b in zip(cs, cs[1:]):
                hole = b["x0"] - a["x1"]
                if hole < 2.0 * word_gap:
                    continue
                if fx0 < a["x1"] - 1.5 or fx1 > b["x0"] + 1.5:
                    continue
                if (fx1 - fx0) < 0.5 * hole:
                    continue
                if best is None or gap < best[0]:
                    best = (gap, hcs)
                break
        if best is None:
            continue
        host = best[1][0]
        dt = host["top"] - top
        # Move the WHOLE run, blanks included. The fragment's own spaces ('¶ 17.'
        # carries one) share its baseline; leaving them behind reopens the hole
        # the glyphs came out of and the word breaks there instead
        # ('subsection' → 'subse ctio n').
        move = list(frag)
        for c in chars:
            if (c.get("text") or "").strip():
                continue
            if abs(round(c["top"], 1) - top) > 0.05:
                continue
            # Keyed on the FONT, not an x-window: a blank set in the substitute
            # face on the fragment's own baseline is the fragment's own space,
            # wherever its advance width happens to end.
            if (c.get("fontname") or "").split("+")[-1] in f_fonts:
                move.append(c)
        for c in move:
            c["top"] = host["top"]
            c["bottom"] = host["bottom"]
            if "doctop" in c:
                c["doctop"] = c["doctop"] + dt


def _reunite_offset_glyphs(lines: list) -> list:
    """Put a stray glyph drawn off its own baseline back into the hole it came
    from.

    A glyph the body face lacks is set from a substitute font, and the
    substitute can carry its own vertical offset: ca7's '3 ½ inches' draws the
    '½' from Cambria a full 26pt BELOW the line it belongs to, where it lands
    between two later rows. It is too far away to overlap its own line, and
    close enough to the wrong one to be merged into it mid-word ('Th½e
    statute'), which corrupts that row and orphans the two real ones.

    The hole is the proof: the host line has a gap at exactly the stray
    glyph's x-span, because the glyph was cut out of it. Match on that — a
    lone glyph, no line of its own, and a gap it fits to the point — and no
    ordinary short line (a caption's 'v.', a page number) can be captured."""
    if len(lines) < 2:
        return lines

    def printable(l):
        return [c for c in (l.get("chars") or []) if (c.get("text") or "").strip()]

    strays, hosts = [], []
    for l in lines:
        (strays if len(printable(l)) <= 2 else hosts).append(l)
    if not strays or not hosts:
        return lines

    def fonts(l):
        return {
            (c.get("fontname") or "")
            for c in (l.get("chars") or [])
            if (c.get("text") or "").strip()
        }

    absorbed = set()
    for s in strays:
        height = max(s["bottom"] - s["top"], 1.0)
        s_fonts = fonts(s)
        # If the fragment sits on ITS OWN line already — a bold speaker name
        # set 0.6pt below the roman text it belongs to — leave it alone. The
        # ordinary line merge owns that case. Without this the ≥4pt
        # 'real displacement' guard below excludes the correct host and lets
        # the fragment be claimed by the NEXT line down, whose hole it also
        # happens to fit: Kentucky's transcript turned 'Brown' and 'Tucker'
        # into 'BTruocwkner'.
        if any(
            o is not s and abs(o["top"] - s["top"]) < 4.0 and len(printable(o)) > 2
            for o in lines
        ):
            continue
        best = None
        for h in hosts:
            if abs(h["top"] - s["top"]) > 2.5 * height:
                continue
            # The displaced glyph is one the body face LACKS, fetched from a
            # substitute font — that substitution is what carries the rogue
            # vertical offset in the first place. A page folio is set in the
            # body's own face, so requiring a different font keeps the folio
            # out even when it happens to fit a hole.
            if s_fonts & fonts(h) or not s_fonts:
                continue
            cs = sorted(printable(h), key=lambda c: c["x0"])
            # The hole has to be a HOLE — far wider than the line's own word
            # space. A page folio ('6') is one glyph too, and it will fit an
            # ordinary space between two words if nothing rules that out; it
            # then reads as 'had6 negotiated'. Measured: a real hole runs ~3.4×
            # the line's word gap, a coincidental fit ~1.0×.
            spaces = sorted(
                g for g in (b["x0"] - a["x1"] for a, b in zip(cs, cs[1:])) if g > 0.5
            )
            if not spaces:
                continue
            word_gap = spaces[len(spaces) // 2]
            for a, b in zip(cs, cs[1:]):
                if (b["x0"] - a["x1"]) < 2.0 * word_gap:
                    continue
                # The glyph has to SIT IN the hole: inside the gap, and filling
                # nearly all of it — a word space's worth of slack, no more.
                slack = (b["x0"] - a["x1"]) - (s["x1"] - s["x0"])
                if (
                    0 <= slack <= 6
                    and s["x0"] >= a["x1"] - 1.5
                    and s["x1"] <= b["x0"] + 1.5
                ):
                    d = abs(h["top"] - s["top"])
                    if best is None or d < best[0]:
                        best = (d, h)
                    break
        if best is None:
            continue
        h = best[1]
        h["chars"] = sorted(
            list(h.get("chars") or []) + list(s.get("chars") or []),
            key=lambda c: c["x0"],
        )
        h["x0"] = min(h["x0"], s["x0"])
        h["x1"] = max(h["x1"], s["x1"])
        h["text"] = "".join(c["text"] for c in h["chars"])
        absorbed.add(id(s))
    if not absorbed:
        return lines
    return [l for l in lines if id(l) not in absorbed]


def _is_typed_rule_text(text: str) -> bool:
    """A rule the page TYPES rather than draws ('______' / '------'). It marks
    a boundary between headmatter components, so a tight run must not run
    through it."""
    bare = (text or "").strip()
    return len(bare) >= 3 and set(bare) <= set("_-—–= *")


class BaseExtractor:
    # ====================================================================
    # CLASS CONFIG (each court subclass overrides these)
    # ====================================================================
    court_id: str = ""
    court_label: str = ""  # -> <court>
    author_titles: tuple = ("Justice",)  # ("Judge", "Presiding Judge") ...
    # Document styles that are classified but not parsed into opinions.
    SKIP_BODY_TYPES: tuple = ()
    # Most documents use one footnote sequence per opinion. A separate
    # writing can restart numbering inside the same extracted opinion, so a
    # court may opt to preserve duplicate labels rather than discard them.
    dedupe_footnote_labels: bool = True

    # ====================================================================
    # LAYOUT DEFAULTS (override per-court if layout differs)
    # ====================================================================
    margin_top: float = 39
    margin_bottom: float = 725
    # When True, printed folios are captured as page metadata, removed from the
    # text stream, and emitted exactly once at their reading-order boundary.
    # The court's printed value wins over the physical PDF page index (covers
    # and separate writings can offset/reset numbering).
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
    # The two measured-geometry adaptations of classify_segment. On by
    # default — the engine adapts to the document, not the court — but a
    # fidelity-locked court whose tuned constants ARE its contract (Alabama:
    # byte-identical to the old ca1/casebody) can pin its behavior.
    measured_gap_bands: bool = True
    split_quote_runs: bool = True
    # When no byline is found anywhere, fall back to the unsigned-order shape:
    # body starts at the 'ORDER …' heading, author is the '/s/ Name' signature.
    # (delaware.py keeps its own richer version; Alabama is fidelity-locked.)
    order_heading_fallback: bool = True
    # Surface what the margin bands cut (deduped) in the Removed box.
    surface_margin_furniture: bool = True
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
    # OPT-IN: fold a block QUOTATION that a page break interrupted, the way a
    # paragraph is already folded. Off by default because the fold rests on the
    # court setting a justified right measure — where the measure is ragged,
    # 'this line reached the margin' proves nothing and two adjacent quotations
    # would fuse.
    fold_quotes_across_pages: bool = False

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
    # A PDF can be born-digital and still be unreadable: when a font declares
    # glyphs but ships no ToUnicode map, the text layer extracts as '(cid:36)
    # (cid:83)...' instead of characters. Nothing downstream can work with that
    # — the bylines, margins and font sizes are all intact, so the document parses
    # into a confident-looking opinion made of nothing. Treated as non-digital
    # (flagged, not processed) once unmapped glyphs are this fraction of the
    # text. Corpus-wide the worst genuinely-readable document sits at 0.04 and
    # a CID-broken one at 0.63+, so the band between them is wide; a court whose
    # template mixes a broken decorative font into good text can raise it.
    cid_unreadable_max_frac: float = 0.35

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

    def footnote_sep_min_width(self, page) -> float:
        """Narrowest rule that can be a footnote separator, in points.

        Scaled to the sheet rather than fixed at 100pt, which silently assumed
        a 612pt letter page. Six courts print on a narrow reporter sheet —
        neb/nebctapp/or/orctapp/ca9 at 396pt, olc at 423 — where the separator
        is drawn ~96pt wide. That is proportionally WIDER than a letter-page
        rule (24% of the sheet against 16%), yet it fell just under the fixed
        minimum, so every footnote in those volumes was lost. On a letter page
        this returns ~98, so nothing already working moves."""
        return max(60.0, (getattr(page, "width", 612.0) or 612.0) * 0.16)

    def cid_unreadable(self, pdf) -> tuple[bool, int]:
        """Whether the text layer is mostly unmapped glyphs, and how many.

        A font that declares glyphs without a ToUnicode CMap extracts as
        '(cid:36)(cid:83)(cid:83)...'. The page geometry is untouched, so such a
        document sails through every layout cue and parses into an opinion whose
        text is machine noise — worse than failing, because it looks processed.
        Measured against the readable characters so a stray unmapped ligature
        in an otherwise fine document never trips it."""
        import re as _re

        cid = readable = 0
        for page in pdf.pages:
            text = page.extract_text() or ""
            cid += text.count("(cid:")
            readable += len(
                _re.sub(r"\(cid:\d+\)", "", text).replace(" ", "").replace("\n", "")
            )
        if not cid:
            return False, 0
        return cid / (cid + readable + 1) >= self.cid_unreadable_max_frac, cid

    def matches_expected_layout(self, pdf) -> bool:
        """True if the PDF looks like a typical document for this court.
        Subclasses override to check layout signatures (e.g. a caption
        divider on page 1). Used to flag non-standard documents."""
        return True

    def prepare_document(self, pdf) -> None:
        """Collect optional document-wide signals before page extraction."""

    def extract(self, pdf_path: str) -> ExtractedDocument:
        """Convert a PDF into a structured ``ExtractedDocument``."""
        all_segments = []
        footnote_lines_by_page = {}
        footnote_tables_by_page = {}
        images_by_page = {}
        tables_by_page = {}
        page1_rules = []
        layout_ok = True
        # Physical PDF page -> court-printed folio. Populated before margin
        # furniture is discarded; a court may override ``detect_printed_folio``
        # for a folio embedded in a running header.
        self._printed_folio_by_page = {}
        # Measured per-document body geometry (see _measure_doc_geometry);
        # None until the whole document has been read, and stays None when the
        # document is too small to measure confidently.
        self._doc_geom = None
        # Unsigned-order fallback state (see find_authors). Reset per document
        # so a batch run can't leak one PDF's order anchor into the next.
        self._order_start = None
        self._order_author = None
        # Margin-band furniture captured by page_lines, keyed digitless so a
        # per-page stamp dedupes to one Removed-box row.
        self._margin_dropped = {}
        # Folios ``build_opinion`` removes from the body (see ``add_para``),
        # kept so the Removed box can show them instead of the sweep reporting
        # them unplaced.
        self._folio_dropped = []
        # Running headers ``_drop_running_header`` cuts from continuation
        # pages. Recorded for the same reason as the folios: the reviewer has
        # to be able to see that a repeated docket line was removed rather
        # than swallowed. Deduped on the way into the Removed box, so a header
        # repeated on 28 pages shows once, not 28 times.
        self._running_header_dropped = []
        # This document's own word list (see _learn_vocabulary). Reset per
        # document so one PDF's vocabulary can't decide another's hyphens.
        self._doc_words = set()
        # Per-page ink and image coverage — see the page loop and
        # _warn_image_only_pages.
        self._page_ink = {}
        self._page_img_share = {}
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
            cid_broken, n_cid = self.cid_unreadable(pdf)
            if cid_broken:
                doc = ExtractedDocument(
                    court_id=self.court_id,
                    court_label=self.court_label,
                    doc_type=DocType.UNKNOWN,
                    n_pages=n_pages,
                    non_digital=True,
                    cid_glyphs=n_cid,
                    source_path=pdf_path,
                )
                doc.warnings.append(
                    f"unreadable text layer: {n_cid} unmapped (cid:N) glyphs — the "
                    "PDF's font declares no character mapping; not processed"
                )
                return doc
            self.prepare_document(pdf)
            layout_ok = self.matches_expected_layout(pdf)
            self._hm_caption_box = None
            cap_page = self.caption_page(pdf)
            self._caption_pno = cap_page.page_number if cap_page is not None else 1
            self._page1_width = cap_page.width if cap_page is not None else 612.0
            self._premeasure_geometry(pdf)
            if cap_page is not None:
                page1_rules = self._page1_rules(cap_page)
                self._hm_caption_box = self._page1_caption_box(cap_page)
                try:
                    from .captionfp import classify_page

                    self._caption_fp = classify_page(cap_page)
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
                if page.page_number == self._caption_pno and sep_y is not None:
                    # The caption page's footnote separator is NOT a headmatter
                    # divider — without this it leaks into the styled summary
                    # as a spurious full-width rule at the bottom.
                    page1_rules = [t for t in page1_rules if t < sep_y - 1]
                lines = self.page_lines(page)  # also applies correct_page_geometry
                folio = self.detect_printed_folio(page, lines)
                if folio is not None:
                    self._printed_folio_by_page[page.page_number] = folio

                def is_registered_folio(line):
                    if folio is None:
                        return False
                    value = self._page_number_value(self.line_plain_text(line))
                    if value != folio:
                        return False
                    if self.line_alignment(line, page.width) not in ("C", "R"):
                        return False
                    if (
                        line.get("top", 0) < 100
                        or line.get("top", 0) > page.height - 120
                    ):
                        return True
                    # The fixed band above disagrees with the one
                    # ``detect_printed_folio`` uses to REGISTER a folio (85pt),
                    # so a folio between the two is registered as this page's
                    # number and then not filtered out of the footnote zone.
                    # ca3/hartmann sets its folio at y=668.4 of 792 — 3.6pt
                    # outside the band — and the dissent gained two footnotes
                    # whose entire text was '2' and '3'.
                    #
                    # Measure against the PAGE'S OWN content instead of a
                    # constant: a footer is the last line on the page and a
                    # header is the first, wherever the court chooses to set
                    # it. Additive to the band, so this only ever removes
                    # furniture that was leaking through.
                    tops = [l["top"] for l in lines if l is not line]
                    if not tops:
                        return True
                    return line["top"] >= max(tops) or line["top"] <= min(tops)
                # Capture ground-truth text from the corrected line objects,
                # not raw ``page.extract_text()``. Some PDFs emit overlapping
                # glyphs twice (e.g. ``TTuucckkeerr`` in Kentucky transcripts)
                # while the line builder correctly de-duplicates them. Using
                # raw text here made real rendered content appear unplaced.
                source_pages.append(
                    (
                        page.page_number,
                        [self.line_plain_text(line).strip() for line in lines if self.line_plain_text(line).strip()],
                    )
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

                # RECORD the folio rows this page removes. A folio normally
                # rides along in a cross-page paragraph merge as a
                # <pagenumber/> marker, which is why most pages leave no trace
                # of it — but a page that opens a FRESH paragraph has no merge
                # to carry it, and removing it here silently left that page's
                # number reading as unplaced content.
                for l in lines:
                    if is_registered_folio(l):
                        t = self.line_plain_text(l).strip()
                        if t:
                            self._folio_dropped.append(t)
                body_lines = [
                    l
                    for l in lines
                    if (sep_y is None or l["top"] < sep_y)
                    and not in_any_table(l)
                    and not is_registered_folio(l)
                ]
                fn_lines = [
                    l
                    for l in lines
                    if sep_y is not None
                    and l["top"] >= sep_y
                    and not in_any_table(l)
                    and not self._is_separator_text(l)
                    and not is_registered_folio(l)
                ]
                for seg in self.segment_lines(body_lines, pw):
                    # Classification is deferred until every page's lines are
                    # in: classify_segment judges indents against the
                    # document's own measured body column (``_doc_geom``),
                    # which can only be measured once the whole document has
                    # been read.
                    all_segments.append((page.page_number, seg, None))
                if fn_lines:
                    footnote_lines_by_page[page.page_number] = fn_lines
                imgs = self.extract_page_images(page)
                if imgs:
                    images_by_page[page.page_number] = imgs
                # A page whose content is a picture is a scan stapled into a
                # born-digital document. Whatever it says is pixels, so no
                # parsing will recover it, and the gap it leaves is
                # indistinguishable downstream from a parsing failure —
                # ca11/roger_tejon's footnote 5 lives on such a page, and the
                # document reported only 'footnote sequence breaks: missing 5'.
                #
                # Recorded for EVERY page, not just those bearing an image:
                # the test is against the document's own norm, and a norm
                # measured only over its scanned pages calls the scan typical.
                # Judged later, in _warn_image_only_pages.
                self._page_ink[page.page_number] = sum(
                    1 for c in page.chars if (c.get("text") or "").strip()
                )
                self._page_img_share[page.page_number] = max(
                    (
                        (i["x1"] - i["x0"]) * (i["bottom"] - i["top"])
                        for i in page.images
                    ),
                    default=0,
                ) / max(1.0, page.width * page.height)
                # A table drawn BELOW the footnote separator belongs to the
                # footnote, not the opinion body. Its rows are already kept out
                # of ``fn_lines`` by ``in_any_table``, so emitting it as a body
                # block put the table in a different section from the sentence
                # that introduces it (hawapp/yang_1 footnote 7: 'the sum of the
                # subtotals for each … category:' and then the table, three
                # sections apart). Split them here so each half goes home.
                # Only when the page also has footnote PROSE. A table that
                # fills the whole zone on its own (md/kapneck p24) leaves no
                # footnote to attach to, and moving it out of the body would
                # lose it outright — so that one stays a body table.
                if tables and sep_y is not None and fn_lines:
                    body_tbl = [t for t in tables if t["bbox"][1] < sep_y]
                    fn_tbl = [t for t in tables if t["bbox"][1] >= sep_y]
                    if fn_tbl:
                        footnote_tables_by_page[page.page_number] = fn_tbl
                    tables = body_tbl
                if tables:
                    tables_by_page[page.page_number] = tables

        # Before ANY text is joined — extract_headmatter builds the syllabus
        # rows, and those wrap-heal too.
        self._learn_vocabulary(source_pages)
        # The residual sweep proves every source LINE lands somewhere, but an
        # image is not a line — a full-page screenshot leaves no text for the
        # sweep to miss, so images fell outside the completeness guarantee
        # entirely. Count them here so the guarantee can cover them too.
        self._images_found = sum(len(v) for v in images_by_page.values())
        self._measure_doc_geometry(all_segments)
        all_segments = [
            (page_no, seg, self.classify_segment(seg))
            for page_no, seg, _ in all_segments
        ]
        all_segments = self._split_quote_runs(all_segments)
        all_segments = self._split_segments_at_bylines(all_segments)
        author_indices = self.find_authors(all_segments)
        if not author_indices and self.order_heading_fallback:
            # Pipeline-level so it applies under every family's find_authors
            # override: a docket with no byline anywhere is an unsigned order,
            # not a document that is all headmatter.
            author_indices = self._order_fallback(all_segments)
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
                    hm_pages,
                    footnote_lines_by_page,
                    seen_labels=seen_labels,
                    footnote_tables_by_page=footnote_tables_by_page,
                )
        elif footnote_lines_by_page:
            # No authored opinion (an order / notice): the footnote-zone text
            # still has to be accounted for, so attach every footnote to the
            # headmatter rather than dropping it.
            doc.headmatter_footnotes = self.build_footnotes(
                set(footnote_lines_by_page),
                footnote_lines_by_page,
                seen_labels=seen_labels,
                footnote_tables_by_page=footnote_tables_by_page,
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
                    # Give this writing every table on the pages it owns,
                    # including pages made ENTIRELY of table rows (and thus
                    # absent from ``all_segments`` / ``op_pages``).
                    tables_by_page={
                        p: t for p, t in tables_by_page.items() if p in owned_pages
                    },
                    footnote_tables_by_page={
                        p: t
                        for p, t in footnote_tables_by_page.items()
                        if p in owned_pages
                    },
                )
            )

        if self._order_start is not None and doc.opinions:
            # The unsigned-order fallback found the body via the ORDER title;
            # its single writing is an order, not a majority opinion.
            doc.opinions[0].type = "order"

        if not layout_ok:
            doc.warnings.append("layout does not match expected court format")
        fp = getattr(self, "_caption_fp", (None, None, None))
        if fp and fp[2]:
            doc.caption_box = dict(doc.caption_box or {})
            doc.caption_box["fp_id"], doc.caption_box["fp_style"] = fp[1], fp[2]
        # Page ownership above splits the footnote zones at each writing's FIRST
        # SEGMENT, which is right only when a writing starts at the top of a
        # page. A writing that opens PARTWAY DOWN one takes the whole of that
        # page's footnote zone with it, including the notes the writing above
        # called (pacommwct's conformed signature parses as a byline and hands
        # the trailing ORDER the majority's last page — 18 of 18 notes in
        # city_of_philadelphia). The body's own marks settle it; see
        # ``courts/_footnoteattr``. Imported here, not at module scope, because
        # that module imports this one.
        #
        # This runs BEFORE _sweep_residual so the two footnote warnings are
        # stated against the CORRECTED document — otherwise a document this
        # fixes keeps reporting itself broken.
        from .courts._footnoteattr import reattribute_footnotes_by_mark

        reattribute_footnotes_by_mark(doc)
        self._sweep_residual(doc, source_pages)
        return doc

    def _sweep_residual(self, doc: ExtractedDocument, source_pages) -> None:
        """Completeness safety net: any source line the pipeline placed in no
        rendered section lands in ``doc.residual`` (tagged content/furniture),
        so nothing is silently lost — it surfaces in the Removed box."""
        folios = [f for f in (getattr(self, "_folio_dropped", None) or []) if f]
        if folios:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                f for f in dict.fromkeys(folios) if f not in have
            ]
        margin = getattr(self, "_margin_dropped", None) or {}
        if margin:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                t for t in margin.values() if t not in have
            ]
        # Running headers cut from continuation pages. Without this the header
        # is genuinely gone: the coverage audit calls a repeated margin line
        # 'furniture' and stops counting it, which is an AUDIT-side bucket, not
        # a place the reviewer can look. A docket line removed from 28 pages
        # left no trace anywhere in the rendered document (alacivapp
        # 'CL-2025-0736'), so removal could not be distinguished from loss.
        headers = [h for h in (getattr(self, "_running_header_dropped", None) or []) if h]
        if headers:
            have = set(doc.dropped)
            doc.dropped = list(doc.dropped) + [
                h for h in dict.fromkeys(headers) if h not in have
            ]
        try:
            from .audit import sweep_unplaced

            doc.residual = sweep_unplaced(doc, source_pages)
        except Exception as e:  # the sweep is a safety net, never a hard failure
            doc.warnings.append(f"residual sweep failed: {type(e).__name__}: {e}")
        # Measured once and shared: a note printed on a scanned page cannot be
        # read at all, so the footnote checks have to know which pages those
        # are before they call a missing note a loss.
        scanned = self._scanned_page_numbers()
        self._warn_footnote_gaps(doc, scanned)
        self._warn_mis_zoned_footnotes(doc)
        self._warn_orphan_footnote_refs(doc)
        self._warn_body_in_headmatter(doc)
        self._warn_dropped_images(doc)
        self._warn_image_only_pages(doc)

    def _scanned_page_numbers(self) -> list:
        """The document's image-only pages, measured against its own pages.

        A scan is not always textless — cacd 996274's scanned cover carries a
        91-character stamp layer over a full-page image while its digital pages
        run to ~2,800. A page is a scan when a picture covers most of it and
        its text is a small fraction of what this document sets on a normal
        page."""
        ink = getattr(self, "_page_ink", None) or {}
        share = getattr(self, "_page_img_share", None) or {}
        if not ink:
            return []
        typical = median(sorted(ink.values()))
        # Compare against the fullest pages, not the median of a document whose
        # pages are mostly scans — otherwise a wholly scanned filing calls its
        # own blank norm 'typical' and reports nothing.
        busiest = max(ink.values(), default=0)
        norm = max(typical, busiest * 0.4)
        return sorted(
            pno
            for pno, n in ink.items()
            if share.get(pno, 0) >= 0.5 and n <= max(norm * 0.15, 0)
        )

    def _warn_image_only_pages(self, doc: ExtractedDocument) -> None:
        """Pages whose content is a picture rather than text — OCR territory.

        The image is kept, but any TEXT drawn inside it is pixels and cannot be
        read. Saying so is the difference between a known limit and an apparent
        bug: ca11/roger_tejon's footnote 5 sits on such a page, and the
        document reported only 'footnote sequence breaks: missing 5'.

        Measured against the document's OWN pages, because a scan is not always
        textless — cacd 996274's scanned cover carries a 91-character stamp
        layer over a full-page image while its digital pages run to ~2,800.
        A page is a scan when a picture covers most of it and its text is a
        small fraction of what this document sets on a normal page.

        The measurement itself lives in ``_scanned_page_numbers`` because the
        footnote checks read it too."""
        pages = self._scanned_page_numbers()
        if not pages:
            return
        shown = ", ".join(str(p) for p in pages[:8])
        more = "" if len(pages) <= 8 else f" (+{len(pages) - 8} more)"
        doc.warnings.append(
            f"page {shown}{more}: scanned image, not text — the picture is "
            f"kept, but its content needs OCR and is not extracted"
        )

    def _warn_dropped_images(self, doc: ExtractedDocument) -> None:
        """An embedded image that reached no section.

        The completeness proof reads ``source_pages``, which holds text LINES,
        so an image is invisible to it: ca11/roger_tejon dropped three
        full-page screenshots out of five images and the sweep reported nothing
        unplaced, because a page carrying only an image contributes no line to
        miss. Counting extracted images against placed ones closes that hole."""
        found = getattr(self, "_images_found", 0)
        if not found:
            return
        # A document with no opinion body has nowhere to place an image, so the
        # count proves nothing — Alabama's no-opinion orders carry a seal and
        # a signature graphic and would report both as lost on every run.
        if not any(op.blocks for op in doc.opinions):
            return
        placed = sum(
            1
            for op in doc.opinions
            for block in op.blocks
            if block.kind == "image"
        )
        if placed < found:
            doc.warnings.append(
                f"{found - placed} of {found} embedded image(s) were not "
                f"placed in any section"
            )

    @staticmethod
    def _warn_body_in_headmatter(doc: ExtractedDocument) -> None:
        """The byline was matched too late and the opinion is in headmatter.

        Headmatter is *defined* as whatever precedes the first opinion start,
        so a byline matched near the END of a document silently converts almost
        all of it into front matter. cadc/municipal_energy_agency_of_nebraska
        matched 'Per Curiam' on page 6 — the conformed signature standing above
        the clerk's block — and a six-page judgment came out as 75 headmatter
        rows against 3 body blocks. Nothing objected: doc_type stayed
        'opinion', no warning was raised, and ingest's ``suspect`` flag asks
        only whether the body is EMPTY, which the signature satisfied.

        Judged against the document's own size rather than a fixed count: a
        real opinion sets far more body than front matter, so front matter that
        outweighs a body of under one block per page means the anchor is
        wrong."""
        if doc.n_pages < 3:
            return
        blocks = sum(len(op.blocks) for op in doc.opinions)
        rows = len([r for r in (doc.summary or []) if r])
        if blocks < doc.n_pages and rows > max(blocks, 4):
            doc.warnings.append(
                f"body may be misfiled as headmatter: {rows} headmatter rows "
                f"against {blocks} body block(s) over {doc.n_pages} pages — "
                f"check that the opinion's byline was found in the right place"
            )

    _MARK_OPEN = "<footnotemark>"
    _MARK_CLOSE = "</footnotemark>"

    @classmethod
    def _footnote_marks(cls, text: str) -> list:
        """Every footnote-mark value in ``text``, in order of appearance."""
        return [value for value, _before in cls._footnote_mark_uses(text)]

    @classmethod
    def _footnote_mark_uses(cls, text: str) -> list:
        """Every mark in ``text`` as ``(value, text preceding it)``.

        The preceding text is what tells a footnote reference apart from a
        typographic look-alike, and it can only be read at the point of use —
        the same '*' is a real mark in one sentence and a reporter pincite in
        the next, so the judgement has to be per occurrence, not per label."""
        out, i = [], 0
        while True:
            a = text.find(cls._MARK_OPEN, i)
            if a == -1:
                return out
            b = text.find(cls._MARK_CLOSE, a)
            if b == -1:
                return out
            value = text[a + len(cls._MARK_OPEN) : b].strip()
            if value:
                out.append((value, cls._visible_text(text[:a])))
            i = b + len(cls._MARK_CLOSE)

    @staticmethod
    def _visible_text(markup: str) -> str:
        """``markup`` with its tags removed — the words a reader sees."""
        out, depth = [], 0
        for ch in markup:
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                out.append(ch)
        return "".join(out)

    # -- false-alarm rules -------------------------------------------------
    # Everything below decides whether a mark/label really names a footnote.
    # None of it touches extraction: no note is built, moved or dropped here.
    # The rules exist because an unfounded warning costs more than silence —
    # 192 documents carry a footnote warning and roughly a tenth of them were
    # measured as false alarms, which is enough noise to make the count
    # meaningless. Each rule below was confirmed by hand against the source.

    @staticmethod
    def _is_reporter_pincite(before: str) -> bool:
        """'…, 2023 WL 12052104, *5' — the star points at a page, not a note.

        Westlaw cites a slip opinion by a starred screen page, and the star is
        set exactly like a footnote mark, so ``line_inline_text`` wraps it.
        Read the citation backwards instead of the glyph: a star that follows
        'WL <digits>,' (optionally 'at') is a pincite. Confirmed in five conn
        documents, e.g. state_v._rohena_1's '2023 WL 12052104, *5'."""
        s = before.rstrip()
        if s.endswith(" at") or s.endswith(",at"):
            s = s[:-2].rstrip()
        if not s.endswith(","):
            return False
        s = s[:-1].rstrip()
        digits = len(s)
        while digits and s[digits - 1].isdigit():
            digits -= 1
        if digits == len(s):  # no volume/document number — not a citation
            return False
        s = s[:digits].rstrip()
        return s.endswith("WL") and (len(s) == 2 or not s[-3].isalnum())

    @staticmethod
    def _numbering_of(labels) -> tuple:
        """``(highest, widest)`` of the numeric labels a writing prints."""
        values = [
            int(text)
            for label in labels
            if (text := str(label or "").strip().rstrip(".")) and text.isdigit()
        ]
        if not values:
            return (0, 0)
        return (max(values), max(len(str(v)) for v in values))

    @classmethod
    def _outside_the_numbering(cls, mark: str, labels) -> bool:
        """A numeric mark the writing's own numbering cannot account for.

        Two shapes, both source typesetting rather than a missing note:

        * **Marks printed hard against each other.** gamd 139124.28.0 sets
          'GRANTED.123' where notes 1, 2 and 3 are each built and each has its
          own separator rule; the three raised glyphs read as one mark '123'.
          ark/mmsc_llc prints two contiguous 8.04pt glyphs '12' for a note
          whose own label glyph is '1'.
        * **A mark below the numbering.** alaska's democratic-party opinion
          calls '0' where notes run 1-89; no court numbers a note 0.

        The first guard is the WIDTH of the mark. '21' after a writing that
        holds 1-20 is exactly what a genuinely lost last note looks like, and
        it is kept — the mark has no more digits than a label the writing
        prints. Only a mark wider than anything the court numbered, whose
        opening digits are themselves a note that WAS built, is called an
        artifact.

        Width alone is NOT enough, and the caller supplies the second guard.
        mich/people_v._kardasz numbers a writing to 58 and calls 105 and 106,
        which this test would dismiss on width — but both notes are printed,
        sitting in the body on pages 57-58 because the separator was missed.
        ``_warn_orphan_footnote_refs`` therefore never asks this question about
        a mark whose own note opens a body block."""
        if not mark.isdigit():
            return False
        highest, widest = cls._numbering_of(labels)
        if not highest:
            return False
        value = int(mark)
        if value < 1:
            return True
        if len(mark) <= widest or value <= highest:
            return False
        held = {str(l or "").strip().rstrip(".") for l in labels}
        return any(mark[:n] in held for n in range(1, len(mark)))

    @classmethod
    def _numbering_is_settled(cls, opinion, pool=()) -> bool:
        """Is this writing's numbered footnote bookkeeping self-consistent?

        Settled means the checks agree with one another: every NUMBER the body
        calls is answered by a note, every numbered note is called by a mark,
        the run has no break, and no note came out unlabelled. When all of
        that holds there is nothing for a warning to be about, so a lone
        contrary signal is far likelier to be a look-alike than the one true
        sign of a loss.

        Read on the numbers alone, because the symbols are exactly what is in
        question when this is asked — an appendix legend's '*' would otherwise
        make a document unable to vouch for the numbering it got right."""
        held = set()
        for fn in opinion.footnotes:
            label = str(fn.label or "").strip()
            if not label or label == "?":
                return False  # an unlabelled note is itself an open question
            held.add(label)
        called = set()
        for block in opinion.blocks:
            called.update(cls._footnote_marks(block.text))
        answerable = held | set(pool)
        numbers = sorted(
            int(text)
            for label in held
            if (text := label.rstrip(".")) and text.isdigit()
        )
        if any(b - a > 1 for a, b in zip(numbers, numbers[1:])):
            return False
        if any(m.isdigit() and m not in answerable for m in called):
            return False
        return all(label in called for label in held if label.isdigit())

    @staticmethod
    def _is_legend_marker(mark: str, uses: int) -> bool:
        """A symbol that labels the ITEMS OF A LIST rather than a note.

        olc/department_of_agriculture_preferences prints an appendix of statute
        headings and marks them '*', '†' and '*†', explaining in the body what
        each one means; its own six numbered notes are all built. Every one of
        those asterisks is set exactly like a footnote mark, so 27 of them read
        as one enormous missing note.

        Two things separate a legend from a reference. A footnote is called
        once, or twice where a court repeats a citation — a legend marker is
        stamped on item after item. And a legend combines its symbols ('*†'
        for an item that is both), which a footnote label never does: a court
        that doubles a symbol repeats the SAME one ('**', '††')."""
        if mark.isalnum() or any(ch.isalnum() for ch in mark):
            return False
        return uses > 2 or len(set(mark)) > 1

    @classmethod
    def _warn_mis_zoned_footnotes(cls, doc: ExtractedDocument) -> None:
        """A body block that OPENS with a footnote mark is a footnote the zone
        logic missed.

        Footnote capture hangs on ONE boolean per page — whether
        ``find_footnote_separator`` found the rule. ``extract`` builds
        ``fn_lines`` only ``if sep_y is not None``, so when that gate fails the
        page's whole footnote zone is delivered as body text instead, and
        nothing says a word. A 194-page SCOTUS opinion lost footnotes 14-16 to
        a position test, and ca2 lost Salters' footnote 1 to a mis-measured
        rail; neither produced a warning, and both were found only by hand.

        The loss is self-evident in the output, though. ``line_inline_text``
        had already recognised the raised, reduced-size label and wrapped it in
        <footnotemark> — so the inline renderer and the zone logic contradict
        each other about the same line, and the contradiction costs nothing to
        detect. A block that STARTS with a mark is a footnote's opening line
        sitting in the body.

        The one thing that looks identical and is not a footnote is an
        ENUMERATED LIST whose numeral the court raised: wash/marquez_vargas
        sets a raised 9pt '1' opening an indented item inside a quoted
        certified question on page 21, and all 28 of its notes are built. The
        discriminator is the writing's own bookkeeping — if the label is
        already built here, and the writing's numbering is settled (every mark
        answered by a note, every note called by a mark, no break in the run),
        then nothing is missing and this opening numeral is a numeral. Any
        inconsistency at all and the hit stands, which is why
        ca3/international_brotherhood keeps its page-18 hit."""
        hits = []
        pool = {
            str(fn.label or "").strip()
            for fn in (doc.headmatter_footnotes or [])
        }
        for op in doc.opinions:
            settled = cls._numbering_is_settled(op, pool)
            held = pool | {str(fn.label or "").strip() for fn in op.footnotes}
            for block in op.blocks:
                if block.text.lstrip().startswith(cls._MARK_OPEN):
                    marks = cls._footnote_marks(block.text)
                    label = marks[0] if marks else "?"
                    if settled and label in held:
                        continue
                    hits.append((block.page, label))
        if not hits:
            return
        shown = ", ".join(f"{label} (p{page})" for page, label in hits[:6])
        more = "" if len(hits) <= 6 else f" (+{len(hits) - 6} more)"
        doc.warnings.append(
            f"footnote text left in the body: {shown}{more} — the page's "
            f"footnote separator was not found, so the zone was read as prose"
        )

    @classmethod
    def _warn_orphan_footnote_refs(cls, doc: ExtractedDocument) -> None:
        """A mark in the body with no footnote to match it.

        This is the direct statement of 'the footnote was not found', and it
        catches what the sequence check structurally cannot: a missing FIRST
        note leaves no gap at all (ca2 Salters ran 2, 3 and read as complete).
        Headmatter notes count toward the pool — a caption-page note about
        party substitution is a real footnote, and treating it as missing was
        what made an earlier hand scan report three false failures."""
        pool = {
            str(fn.label or "").strip()
            for fn in (doc.headmatter_footnotes or [])
        }
        missing = []
        for op in doc.opinions:
            labels = pool | {str(fn.label or "").strip() for fn in op.footnotes}
            uses = []
            in_body = set()
            for block in op.blocks:
                uses.extend(cls._footnote_mark_uses(block.text))
                # The note's own opening line, left in the body because the
                # page's separator was missed. Whatever else the mark looks
                # like, a note that is PRINTED and not built is a real loss,
                # so nothing below may dismiss it: mich/people_v._kardasz
                # calls 105 and 106 out of a writing numbered to 58, and both
                # notes are sitting on pages 57-58 as prose.
                if block.text.lstrip().startswith(cls._MARK_OPEN):
                    opening = cls._footnote_marks(block.text)
                    if opening:
                        in_body.add(opening[0])
            times = Counter(mark for mark, _before in uses)
            settled = cls._numbering_is_settled(op, pool)
            seen = set()
            for mark, before in uses:
                if mark in labels or mark in seen:
                    continue
                if mark in in_body:
                    seen.add(mark)
                    missing.append(mark)
                    continue
                # Not every raised glyph is a reference. Judge each USE: a
                # star following a Westlaw cite is a page pointer, and a mark
                # wider than any number the writing prints is two marks set
                # touching, or a source typo. Neither is a note the extractor
                # failed to find. A legend's symbol is only dismissed where
                # the writing's numbering is settled, so a document with a
                # real footnote problem never has one waved through.
                if set(mark) == {"*"} and cls._is_reporter_pincite(before):
                    continue
                if cls._outside_the_numbering(mark, labels):
                    continue
                if settled and cls._is_legend_marker(mark, times[mark]):
                    continue
                seen.add(mark)
                missing.append(mark)
        if missing:
            shown = ", ".join(missing[:8])
            more = "" if len(missing) <= 8 else f" (+{len(missing) - 8} more)"
            doc.warnings.append(
                f"footnote referenced but never built: {shown}{more}"
            )

    @classmethod
    def _warn_footnote_gaps(cls, doc: ExtractedDocument, scanned=()) -> None:
        """Flag a BREAK in the numbered footnote sequence.

        A whole footnote can go missing without the coverage audit noticing:
        its text is prose, and prose that appears nowhere else still matches
        the audit's substring test often enough to read as covered — CA1's
        footnote 2 vanished with the labels running 1, 3, 4 and nothing said a
        word. The numbering is the court's own checksum, so read it: any gap
        in an otherwise consecutive run means a note was dropped on the floor.

        Read PER WRITING. Pooling every opinion's labels into one set was a
        blind spot exactly where it mattered: SCOTUS restarts its numbering at
        1 for each writing, so the concurrence's missing 14, 15 and 16 were
        'filled' by the dissents' own 14, 15 and 16 and the check stayed
        silent through a 194-page loss.

        Numbered notes only. A court that labels with '*' / '†' is not
        sequential and has nothing to check.

        A gap is only evidence of a LOSS if the court's numbering is the
        court's own. Two things break that assumption, and both are reported
        rather than assumed away:

        * **The source itself skips.** ind/in_the_matter_of_james_steven_cox
          really does number its sixth note '64' — the body reads 'sanction.64',
          the note reads '64As mentioned…', and the file draws only two
          separator rules. mass/khoda runs 8 → 10 with no mark 9 printed
          anywhere. Nothing was lost, so nothing is reported: a gap has to be
          CALLED by a mark in the body to count. That test is only trustworthy
          when the writing's marks corroborate the notes it did build, so it is
          applied only where every one of the writing's own labels is also
          called — acca/nelson builds notes 9-12 that no mark calls, so its
          missing 5 stays flagged, as it should.
        * **The note is a picture.** ca11/roger_tejon's note 5 is printed on
          page 17, a full-page image with no text layer, and acca/ayuso's notes
          2 and 3 on its page 2. There is no reading it without OCR. The gap is
          still reported — it is a real absence — but it says why, and the
          mark test above is NOT applied, because a scan swallows the mark as
          readily as the note."""
        gaps = []
        for op in doc.opinions:
            labels = sorted(
                {
                    int(text)
                    for fn in op.footnotes
                    if (text := str(fn.label or "").strip().rstrip("."))
                    and text.isdigit()
                }
            )
            if len(labels) < 2:
                continue
            breaks = [
                n for a, b in zip(labels, labels[1:]) for n in range(a + 1, b)
            ]
            if breaks and not scanned:
                called = set()
                for block in op.blocks:
                    called.update(cls._footnote_marks(block.text))
                corroborated = all(str(n) in called for n in labels)
                if corroborated:
                    breaks = [n for n in breaks if str(n) in called]
            gaps.extend(breaks)
        if gaps:
            shown = ", ".join(str(n) for n in sorted(set(gaps))[:8])
            more = "" if len(set(gaps)) <= 8 else f" (+{len(set(gaps)) - 8} more)"
            note = ""
            if scanned:
                pages = ", ".join(str(p) for p in scanned[:6])
                note = (
                    f" — page {pages} of this document is a scanned image with "
                    f"no text layer, so a note printed there cannot be read "
                    f"(see the scanned-image warning); OCR, not an extraction "
                    f"fault"
                )
            doc.warnings.append(
                f"footnote sequence breaks: missing {shown}{more}{note}"
            )

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
        if hm.get("headnotes"):
            doc.headnotes = hm["headnotes"]

    # ====================================================================
    # DOCUMENT-TYPE IDENTIFIER
    # ====================================================================
    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        """Identify the document *style*: opinion / order / notice / unknown.

        Not every PDF a court publishes is an authored opinion. The default
        heuristic: an authored byline => OPINION; otherwise look at the text
        for order / notice cues. Subclasses refine this for their court."""
        if getattr(self, "_order_start", None) is not None:
            return DocType.ORDER
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
    def caption_page(self, pdf):
        """The page carrying the case caption. Page 1 for almost every court —
        but a court that prints an official summary / publication-notice sheet
        AHEAD of the caption (the Colorado Court of Appeals) must measure its
        caption geometry, drawn rules and fingerprint on the page that actually
        holds the caption, not on the sheet in front of it."""
        return pdf.pages[0] if pdf.pages else None

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

        min_w = self._rule_min_width(p1)

        tops = []
        for r in p1.rects:
            if (
                r["height"] < 2
                and (r["x1"] - r["x0"]) > min_w
                and _outside_caption(r["top"])
                and not _is_underline(r["top"])
            ):
                tops.append(r["top"])
        for ln in p1.lines:
            if (
                (ln["x1"] - ln["x0"]) > min_w
                and _outside_caption(ln["top"])
                and not _is_underline(ln["top"])
            ):
                tops.append(ln["top"])
        for img in p1.images:
            if (
                (img.get("height") or 0) < 5
                and img.get("width", 0) > min_w
                and _outside_caption(img["top"])
                and not _is_underline(img["top"])
            ):
                tops.append(img["top"])
        return sorted(tops)

    # Default floor for a drawn horizontal rule to count as a divider. Short
    # marks are normally underlines or artefacts.
    rule_width_min = 50.0

    def _rule_min_width(self, p1) -> float:
        """The narrowest drawn rule on THIS page that is still a divider.

        The D.C. Circuit separates its caption components with a 36pt
        ornament centred on the page axis, repeated between each one — under
        the flat 50pt floor all four were discarded and the caption lost
        every rule the page draws.

        An ornament is identifiable by construction rather than by width: it
        is centred on the page, and it REPEATS at exactly the same span. A
        one-off short mark (an underline, a stray box edge) does neither, so
        the floor only comes down when both hold."""
        page_mid = float(p1.width) / 2
        spans = Counter()
        for r in p1.rects:
            if r["height"] < 2:
                spans[(round(r["x0"], 1), round(r["x1"], 1))] += 1
        for ln in p1.lines:
            if abs(ln["bottom"] - ln["top"]) < 2:
                lo, hi = sorted((ln["x0"], ln["x1"]))
                spans[(round(lo, 1), round(hi, 1))] += 1
        floor = self.rule_width_min
        for (x0, x1), count in spans.items():
            width = x1 - x0
            if count < 2 or width >= floor or width < 10:
                continue
            if abs((x0 + x1) / 2 - page_mid) <= 6:
                floor = min(floor, width - 1)
        return floor

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
                    "bottom": img["bottom"],
                    "x0": img["x0"],
                    "x1": img["x1"],
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
            # The COLUMN divider is the interior vertical nearest mid-page. A
            # boxed caption also has edge verticals, and pleading paper draws
            # full-height margin/border rails at the very edges — neither is a
            # column divider, so restrict to the interior band before choosing.
            # If nothing sits interior (the caption is held by a glyph rail
            # like ')' rather than a drawn rule), leave vx None so the split
            # falls back to mid-page instead of snapping to a margin rail.
            mid = page.width / 2
            interior = [
                v for v in verts if page.width * 0.25 < v[0] < page.width * 0.75
            ]
            if interior:
                best = min(interior, key=lambda v: abs(v[0] - mid))
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
        lines = _reunite_offset_glyphs(lines)
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
            prev_sizes = sorted(
                float(c.get("size") or 0)
                for c in (prev.get("chars") or [])
                if (c.get("text") or "").strip() and c.get("size")
            )
            line_sizes = sorted(
                float(c.get("size") or 0)
                for c in (ln.get("chars") or [])
                if (c.get("text") or "").strip() and c.get("size")
            )
            size_compatible = True
            if prev_sizes and line_sizes:
                a = prev_sizes[len(prev_sizes) // 2]
                b = line_sizes[len(line_sizes) // 2]
                size_compatible = max(a, b) <= 1.8 * max(min(a, b), 0.1)
            prev_arial = any(
                "arial" in (c.get("fontname") or "").lower()
                for c in (prev.get("chars") or [])
                if (c.get("text") or "").strip()
            )
            line_arial = any(
                "arial" in (c.get("fontname") or "").lower()
                for c in (ln.get("chars") or [])
                if (c.get("text") or "").strip()
            )
            # E-filing stamps are frequently Arial overlays on a differently
            # faced slip-opinion banner.  Their boxes overlap vertically but
            # they are independent rows/columns, not an italic run belonging
            # to the opinion line underneath.
            if min(prev.get("top", 999), ln.get("top", 999)) < 220 and (
                prev_arial != line_arial
            ):
                size_compatible = False
            if merged_chars and size_compatible and v_overlap > 0.45 * min_h:
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
        """Adjust raw char geometry on ``page`` (in place) before any line
        clustering. A court whose font declares a broken glyph bounding box
        overrides this to snap chars back to their true row (see Maine); the
        completeness audit calls it too, so it reads the same corrected text
        the extractor does.

        The base behaviour is to drop OVERSTRUCK glyphs — a character redrawn
        at a position another copy of it already occupies. Conformed
        signatures are often darkened by stamping the judge's name dozens of
        times at one spot, which reads out as
        'CCCCCCCCCCCCCCCCCOOLLLLEEEENN DD. HHHHHOOOOLLLLLLAANNDD'. Two
        distinct glyphs never share a position, so a repeat there is the same
        glyph struck again, not new text."""
        chars = page.chars
        # Word's PDF footnote field can leave a microscopic ``0F`` field-code
        # run under the real superscript label.  At roughly one point high it
        # is not visible and pdfplumber's ordinary ``extract_text`` omits it,
        # but our char-faithful inline renderer used to emit it as literal
        # body text (``...57.)0F¹``).  Remove only alphanumeric micro-glyphs;
        # ordinary small caps, subscripts, and footnote marks are several
        # points larger and remain untouched.
        micro = [
            i
            for i, c in enumerate(chars)
            if (c.get("text") or "").isalnum()
            and 0 < float(c.get("size") or 0) <= 1.5
        ]
        for i in reversed(micro):
            del chars[i]
        # Sorted by glyph then POSITION, so every copy of one stamp lands
        # beside its originals: the restamps scatter by hundredths of a point,
        # which a fixed grid would split across two buckets, and ordering by
        # x0 before top keeps two stamps of the same letter on one line from
        # interleaving and breaking the run.
        order = sorted(
            range(len(chars)),
            key=lambda i: (
                chars[i].get("text") or "",
                chars[i]["x0"],
                chars[i]["top"],
            ),
        )
        dupes, anchor = [], None
        for i in order:
            c = chars[i]
            if (
                anchor is not None
                and (c.get("text") or "") == (anchor.get("text") or "")
                and abs(c["top"] - anchor["top"]) <= 0.5
                and abs(c["x0"] - anchor["x0"]) <= 0.5
            ):
                dupes.append(i)
            else:
                anchor = c
        for i in sorted(dupes, reverse=True):
            del chars[i]
        _snap_displaced_fragments(chars)

    def page_lines(self, page) -> list:
        """Return text lines after filtering header/footer margins. If the
        page has a vertical caption-column divider, split chars into
        left/right columns BEFORE clustering so the columns don't merge."""
        self.correct_page_geometry(page)
        self._capture_margin_band(page)
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

        out_lines = self._merge_interleaved(
            self._text_lines(page.filter(outside_caption))
        )
        for l in out_lines:
            l["_caption_col"] = None
        left_lines = self._merge_interleaved(
            self._text_lines(page.filter(left_of_divider))
        )
        for l in left_lines:
            l["_caption_col"] = "L"
        right_lines = self._merge_interleaved(
            self._text_lines(page.filter(right_of_divider))
        )
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
        previous = None
        for ln in sorted(lines, key=lambda l: l.get("top", 0)):
            if ln.get("top", 0) > self.running_header_max_top:
                break
            if previous is not None:
                height = max(
                    previous.get("bottom", previous.get("top", 0))
                    - previous.get("top", 0),
                    1,
                )
                # "Contiguous" is geometric as well as textual. A citation
                # near the top of the page can contain a valid docket token
                # but sit a full paragraph lead below the real running header.
                if ln.get("top", 0) - previous.get("top", 0) > max(30, 2 * height):
                    break
            if self.is_docket_line(ln.get("text") or ""):
                drop.add(id(ln))
                previous = ln
            else:
                break
        if not drop:
            return lines
        if not hasattr(self, "_running_header_dropped"):
            self._running_header_dropped = []
        for l in lines:
            if id(l) in drop:
                t = " ".join((l.get("text") or "").split())
                if t:
                    self._running_header_dropped.append(t)
        return [l for l in lines if id(l) not in drop]

    def is_docket_line(self, text) -> bool:
        """Hook: True if ``text`` is a docket-number running-header line.
        Default False; courts using ``running_header_docket`` implement it."""
        return False

    @staticmethod
    def is_rule_text(text: str, glyphs: str = "_-—–") -> bool:
        """True if ``text`` is a TYPED horizontal rule — see
        ``captionfp.is_typed_rule``, the one definition of the shape, which
        the caption fingerprint measures with as well."""
        from .captionfp import is_typed_rule

        return is_typed_rule(text, glyphs)

    def _is_separator_text(self, line) -> bool:
        return self.is_rule_text((line.get("text") or ""), "_-=")

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

    @staticmethod
    def _page_number_value(text: str) -> str | None:
        """Normalized value from a standalone printed folio."""
        t = str(text or "").strip()
        low = t.lower()
        if low.startswith("page "):
            t = t[5:].strip()
        core = t.strip("-–—  ")
        return core if core.isdigit() and len(core) <= 4 else None

    def detect_printed_folio(self, page, lines) -> str | None:
        """Return the court-printed folio for ``page`` when geometrically clear.

        The raw page is inspected because a real folio normally sits outside
        ``margin_top``/``margin_bottom`` and has already disappeared from
        ``page_lines``. A candidate must be a standalone numeric line in a
        shallow top/bottom margin. As a compatibility path for courts that
        intentionally retain inter-paragraph folios, similarly isolated lines
        from ``page_lines`` are considered too.
        """
        candidates = []
        try:
            raw_lines = page.filter(
                lambda obj: obj.get("upright", True) is not False
            ).extract_text_lines()
        except Exception:
            raw_lines = []
        numeric_lines = []
        for line in raw_lines:
            value = self._page_number_value(line.get("text") or "")
            if value is not None:
                numeric_lines.append((line, value))

        # Pleading paper prints a complete 1..28 (or similar) line-number
        # rail down one side.  Its first and last entries sit inside the page
        # margins and otherwise look exactly like folios.  Identify the rail
        # from its repeated x-position and tall vertical span, then exclude
        # every member; a real centered/right footer on the same page remains.
        rail_ids = set()
        for line, _value in numeric_lines:
            xmid = (line.get("x0", 0) + line.get("x1", 0)) / 2
            same_rail = [
                other
                for other, _v in numeric_lines
                if abs(
                    ((other.get("x0", 0) + other.get("x1", 0)) / 2) - xmid
                )
                <= 10
            ]
            if (
                len(same_rail) >= 8
                and max(x.get("top", 0) for x in same_rail)
                - min(x.get("top", 0) for x in same_rail)
                > page.height * 0.5
            ):
                rail_ids.update(id(x) for x in same_rail)

        for line, value in numeric_lines:
            if id(line) in rail_ids:
                continue
            top = line.get("top", 0)
            if top < 85 or top > page.height - 85:
                edge_distance = min(top, max(0, page.height - line.get("bottom", top)))
                candidates.append((edge_distance, value))
        if candidates:
            candidates.sort(key=lambda item: item[0])
            return candidates[0][1]

        # Some reporters place a bare folio between the last line and the next
        # page's continued paragraph, still inside the configured body margin.
        for line in lines:
            value = self._page_number_value(self.line_plain_text(line))
            if value is None:
                continue
            align = self.line_alignment(line, page.width)
            if align in ("C", "R") and (
                line.get("top", 0) < 100
                or line.get("top", 0) > page.height - 120
            ):
                return value
        return None

    def printed_folio(self, physical_page: int) -> str | None:
        """Folio at a physical page, using PDF order only as a true fallback."""
        folios = getattr(self, "_printed_folio_by_page", {})
        if folios:
            # Once a document demonstrates printed numbering, never invent a
            # number for its unnumbered cover/notice pages.
            return folios.get(physical_page)
        return str(physical_page)

    def page_marker(self, physical_page: int) -> str:
        value = self.printed_folio(physical_page)
        return f'<pagenumber value="{value}"/>' if value is not None else ""

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

    def _capture_margin_band(self, page) -> None:
        """Record what ``filter_margins`` is about to cut, so it can surface
        in the Removed box instead of vanishing.

        The margin bands are geometry: whatever prints there — a CM/ECF
        header stamp, a form footer ('CV-90 (10/08) CIVIL MINUTES - GENERAL
        Page 1 of 1') — is page furniture BY POSITION, no text rules needed.
        But 'drop only identified junk, and surface it': cutting the chars
        silently made a one-page form's footer read as unplaced content in
        the audit (repetition can't identify furniture with one page).
        Deduped by digitless key: a stamp that repeats on every page shows
        once."""
        if not self.surface_margin_furniture:
            return
        try:
            band = page.filter(lambda o: not self.filter_margins(o))
            lines = self._text_lines(band)
        except Exception:
            return
        store = getattr(self, "_margin_dropped", None)
        if store is None:
            store = self._margin_dropped = {}
        for line in lines:
            text = self.line_plain_text(line).strip()
            if not text:
                continue
            key = "".join(c for c in text if not c.isdigit())
            store.setdefault(key, text)

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
        x0_max = self.body_baseline_x0 + 4
        divider = self.find_caption_divider(page)
        cap_bot = divider[2] if divider else None
        min_w = self.footnote_sep_min_width(page)

        thin_rules = [
            r
            for r in list(page.rects) + list(page.lines)
            if abs(r.get("height", 0)) < 2
        ]

        def shares_row(r):
            """A second rule at the same height, spanning a different part of
            the measure: this one is a BOX EDGE — a table cell's side, a form
            grid, a caption box — not a footnote separator.

            The test only starts to matter once the rule no longer has to sit
            low on the page, because a table's cells are set in reduced type
            and so corroborate exactly like a separator: ortc/d.e._shaw
            appended 881 words of a statutory comparison table to footnote 2,
            and nysupct's disposition checkbox grid ('CASE DISPOSED X
            NON-FINAL DISPOSITION ...') became a footnote. ``_circuit._sep_at``
            and ``_oregon._reporter_sep_rule`` already use it. A PDF that
            represents the same rule as both a rect and a vector line must not
            count as its own partner."""
            for o in thin_rules:
                if o is r or abs(o["top"] - r["top"]) > 2:
                    continue
                if abs(o["x0"] - r["x0"]) <= 2 and abs(o["x1"] - r["x1"]) <= 2:
                    continue
                return True
            return False

        def scan(objs, width_min, floor, corroborate):
            out = []
            for r in objs:
                if not (
                    abs(r.get("height", 0)) < 2
                    and (r["x1"] - r["x0"]) >= width_min
                    and r["x0"] <= x0_max
                    and r["top"] > floor
                ):
                    continue
                if cap_bot is not None and abs(r["top"] - cap_bot) <= 4:
                    continue
                if shares_row(r):
                    continue
                if not corroborate(r["top"]):
                    continue
                out.append(r)
            return out

        # Some courts STROKE the separator as a vector line instead of filling
        # a thin rect (neb, nd, conn, gactapp, nysurct ...). Their page.rects is
        # empty, so a rect-only scan finds nothing and every footnote in the
        # volume is silently lost — body text and all.
        shapes = (page.rects, page.lines)

        def first_hit(width_min, floor, corroborate):
            for objs in shapes:
                hits = scan(objs, width_min, floor, corroborate)
                if hits:
                    return min(hits, key=lambda r: r["top"])["top"]
            return None

        # STEP 1 — the rule, corroborated by SMALLER TEXT below it.
        #
        # The floor is a property of the CAPTION PAGE, not of footnotes. There
        # it earns its keep: the caption's own shelf sits low on a long caption
        # and, with the syllabus set under it in reduced type, corroborates
        # like a separator. On a continuation page there is no caption to
        # confuse, and a rule is high only because its own footnote is long —
        # olc/lifeline p5 draws its separator at y=360.1 of a 657pt sheet and
        # missed the 0.55 line by 1.25 points, losing five footnotes to the
        # body. (``_circuit._sep_at`` splits its floor the same way.)
        caption_page = page.page_number == getattr(self, "_caption_pno", 1)
        by_size = lambda top: self._rule_over_footnotes(page, top)
        sep = first_hit(min_w, page.height * (0.55 if caption_page else 0.10), by_size)
        if sep is not None:
            return sep

        # STEP 2 — the rule, corroborated by a RAISED LABEL below it. Size
        # proves nothing on a court that sets footnotes at BODY size and raises
        # only the label digit: cadc/np_red_rock and cod 252728 run 12pt on
        # both sides of the rule, so step 1 rejected a rule sitting right on
        # top of the notes and lost every footnote on the page.
        #
        # The label is strong enough evidence to relax the two geometric floors
        # that step 1 needs. Width: olc draws its rule 72pt wide, under the
        # ~98pt minimum. Height: a footnote long enough to fill a page pushes
        # the next page's rule far up it (scotus trump_v._barbara p37, y=291 of
        # 792), and 0.55 threw that away.
        #
        # That width relaxation was written as a flat 60pt, which is the letter
        # sheet's measure smuggled in as a constant — 60/612 of the page. Six
        # courts print on a narrow reporter sheet (neb, nebctapp, or, orctapp,
        # ca9 at 396pt; olc at 423), where a proportionally WIDER rule falls
        # under it: ortc draws 58.5pt on a 396pt sheet and missed by 1.5pt,
        # losing footnotes in 16 of 30 documents. Written as the share it
        # always was, a letter page keeps exactly today's 60pt.
        sep = first_hit(
            min(min_w, (getattr(page, "width", 612.0) or 612.0) * (60.0 / 612.0)),
            page.height * 0.25,
            lambda top: self._labelled_note_below(page, top),
        )
        if sep is not None:
            return sep

        # STEP 3 — a separator drawn as TEXT rather than as a shape.
        sep = self._footnote_sep_text(page)
        if sep is not None:
            return sep

        # STEP 4 — NO separator drawn at all (pasuperct draws none anywhere;
        # several cadc documents mark the zone only by a 12pt -> 11pt drop).
        return self._footnote_zone_by_size(page)

    def _labelled_note_below(self, page, rule_top) -> bool:
        """Does the first text line under ``rule_top`` open with a raised
        footnote label?

        This is the corroboration that survives body-size footnotes, where
        'smaller text below' cannot help: np_red_rock sets 12pt above the rule
        and 12pt below it, and raises only the label — '1' at 8.04pt on a 12pt
        line."""
        below = [
            line
            for line in page.extract_text_lines()
            if line["top"] > rule_top + 1 and (line.get("chars") or [])
        ]
        if not below:
            return False
        return self.detect_footnote_label(min(below, key=lambda l: l["top"])) is not None

    def footnote_sep_fixed_left_rule(self, page, width=144.0, tol=6.0, x0_max=None):
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
        position fence is needed. A court whose template indents the separator
        past the body margin (flnd draws the 2-inch rule at a 1.5-inch indent)
        can widen the left-edge window via ``x0_max``.

        The left-edge window also reaches the PAGE's own rail, not only
        ``body_baseline_x0``. That class constant is a court-wide guess, and
        as a bound it excluded by construction every court whose body sits
        right of it: Texas sets its body at 108 and mdag at 133.2 against a
        default window of 76, so no rule could ever match and every footnote
        on those pages was delivered as prose.

        A rule beyond the configured margin has to open a LABELLED note,
        though. At the configured margin the rule's own width is the signature
        and nothing else need be true — that is the whole point of this
        finder: it is for courts whose notes are body-sized, where 'smaller
        text below' cannot see the boundary. Out at the page's rail it is not
        enough, because a conformed SIGNATURE rule is also a 144pt rule at the
        text rail: nmariana stacks three of them above 'ALEXANDRO C. CASTRO,
        Chief Justice / ...', and an uncorroborated widening delivered the
        signature roster and counsel block as a footnote in 15 of 20
        documents. A signature rule has a name under it, never a raised
        label."""
        strict_x0 = self.body_baseline_x0 + 4
        if x0_max is None:
            rail = self._page_text_rail(page)
            x0_max = max(strict_x0, (rail + 4) if rail is not None else strict_x0)
        else:
            strict_x0 = x0_max
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
            if r["x0"] > strict_x0 and not self._labelled_note_below(page, r["top"]):
                continue
            if best is None or r["top"] < best:
                best = r["top"]
        return best

    # Last step of the separator chain: find the footnote zone on a page that
    # draws NO separator at all, from the drop in type size. On by default —
    # pasuperct draws no rule anywhere in the corpus and lost its footnotes in
    # 28 of 30 documents. Opt OUT on a court that sets small-print matter in
    # the BODY (a block quotation in reduced type), where the drop means
    # something else.
    footnote_zone_by_size: bool = True

    def _footnote_zone_by_size(self, page) -> Optional[float]:
        """Top of a footnote zone identified by TYPE SIZE, not by a rule.

        Footnote capture is gated on ``find_footnote_separator`` returning a y,
        and several cadc documents draw no separator whatsoever — no rect, no
        line. The zone is marked the way a typesetter marks it: the type drops
        (12pt body to 11pt), the first line carries a raised label in its
        hanging indent, and it runs to the foot of the page. Eight cadc
        documents delivered their footnotes as body prose because none of that
        was read.

        Requires all three, so a stray small line cannot open a zone: the run
        must reach the bottom of the page, its first line must carry a footnote
        label, and there must be body-size text above it.

        Read over the MARGIN BAND, not the raw page. Every cue here — 'set
        smaller than the body', 'runs to the foot of the page' — is also true
        of a running FOOTER, and a footer is exactly what prints below the
        bottom margin. Scanning the raw page let one open a zone on every page
        of a document that had a real footnote higher up, and the footnote was
        delivered as body prose while the footer became its text: wawd
        356996's 'ORDER DENYING PLAINTIFF'S MOTION ... - 1' at y=753 of 792
        (bottom margin 725), ilsd 106722's 'Page 2 of 11', flnd 541641's
        'CASE NO: 3:26cv3359-MCR-ZCB', kyed's Word source path. The pipeline
        has already ruled all of those out as furniture by position; asking
        the same predicate here keeps the two decisions from contradicting
        each other on the same line."""
        if not self.footnote_zone_by_size:
            return None
        lines = [
            l
            for l in page.extract_text_lines()
            if (l.get("chars") or []) and self._line_in_margin_band(l)
        ]
        if len(lines) < 2:
            return None
        lines.sort(key=lambda l: l["top"])
        sizes = [self._line_type_size(l["chars"]) for l in lines]
        common = Counter(sizes).most_common()
        # The body is the size the page sets MOST of, not its largest. Taking
        # the largest made any page whose headings run one step above the body
        # read the body itself as a footnote zone: la/in_re_henry_l._klein p2
        # turned the opinion's opening paragraph into a footnote, and
        # la/monroe p26 swallowed an entire separate writing, because a 15pt
        # caption outranked the 14pt opinion under it.
        #
        # It must stay a PER-PAGE statistic. A document-wide type size reads
        # every page a court sets in reduced type — a syllabus, a panel line —
        # as a footnote zone: measured against conn's document body it opened
        # one on 36 of 50 syllabus pages.
        #
        # On a TIE the body is the larger of the two. A page whose lower two
        # thirds is footnote sets as much footnote type as body type, and
        # which one won was down to dict insertion order: olc/lifeline p5 is
        # 20 lines at 9pt against 20 at 11pt, called a 9pt body, and lost four
        # footnotes.
        top_hits = max((hits for _s, hits in common if hits >= 3), default=0)
        body = (
            max(s for s, hits in common if hits == top_hits) if top_hits else None
        )
        if body is None:
            return None

        def is_folio(line):
            # The printed folio sits BELOW the footnotes at body size; it must
            # not close the run before it starts.
            return self._page_number_value(self.line_plain_text(line)) is not None

        start = None
        for i in range(len(lines) - 1, -1, -1):
            if is_folio(lines[i]):
                continue
            if sizes[i] <= body - 0.5:
                start = i
            else:
                break
        if start is None or start == 0:
            # THE MODE IS THE NOTE'S OWN SIZE WHEN THE NOTE FILLS THE PAGE. A
            # footnote long enough to take two thirds of its page sets more
            # lines than the body standing above it, so the page's commonest
            # size IS the footnote's and no drop is visible from it:
            # cadc/venezuela_us_srl p12 is 21 lines of 11pt note under 14 of
            # 12pt body, and footnote 5 was delivered as body prose.
            #
            # Read the trailing run against the type ABOVE it instead — and
            # require that run to open on a LABEL, because the label is the
            # only cue separating it from a page whose body merely sits under a
            # larger heading. That page has the identical size profile:
            # la/in_re_henry_l._klein p2 is 19 lines of 14pt opinion under a
            # 5-line 15pt caption, and reading it this way turned the opinion's
            # opening paragraph into a footnote. Its first line begins 'This
            # disciplinary matter arises...' at full body size; venezuela's
            # begins with a 6.96pt '5' on an 11pt line.
            start = self._labelled_size_drop(lines, sizes, is_folio)
            return None if start is None else lines[start]["top"] - 1
        # A zone normally opens on a labelled note. One that does not is a
        # CONTINUATION carried over from the previous page — np_red_rock's
        # page 9 ends with the tail of page 8's footnote — and requiring a
        # label there left those lines in the body, where they also defeated
        # the 'nothing below this byline' test that identifies the closing
        # signature, so the whole judgment stayed in headmatter.
        #
        # A continuation is admitted on position instead: it must run to the
        # FOOT of the page, which a mid-page run of small type never does —
        # and there must BE a previous page for it to continue. On the caption
        # page there is not, and everything the court sets under the caption
        # (the panel line, the syllabus, the counsel block) is smaller than the
        # body and runs to the foot: conn/state_of_connecticut_judicial_branch
        # delivered 'McDonald, D'Auria, Ecker, Dannehy and Suarez, Js.
        # Syllabus The complainant, M, ...' as a footnote on 41 of 50
        # documents. A real caption-page note carries its label ('*', '1'), so
        # the labelled path still finds it.
        if self.detect_footnote_label(lines[start]) is None:
            if page.page_number <= getattr(self, "_caption_pno", 1):
                return None
            last = max(
                (l for l in lines[start:] if not is_folio(l)),
                key=lambda l: l.get("bottom", l["top"]),
                default=None,
            )
            if last is None or last.get("bottom", last["top"]) < page.height * 0.82:
                return None
        return lines[start]["top"] - 1

    def _labelled_size_drop(self, lines, sizes, is_folio) -> Optional[int]:
        """Index of a trailing run of smaller type that OPENS ON A LABEL.

        The second reading of ``_footnote_zone_by_size``, used only where the
        first found no drop at all. It asks nothing of how much of the page the
        run covers — that is exactly the question the first reading gets wrong
        — but pays for it by demanding two things the first does not: every
        line above the run is a clear step larger, and the run's first line
        carries a footnote label. No continuation is admitted here; an unlabelled
        run is what a body under a heading looks like."""
        idx = [i for i in range(len(lines)) if not is_folio(lines[i])]
        if len(idx) < 4:
            return None
        note = sizes[idx[-1]]
        start = None
        for i in reversed(idx):
            if sizes[i] <= note + 0.25:
                start = i
            else:
                break
        if start is None:
            return None
        above = [sizes[i] for i in idx if i < start]
        if len(above) < 3 or min(above) <= note + 0.5:
            return None
        if self.detect_footnote_label(lines[start]) is None:
            return None
        return start

    @staticmethod
    def _page_text_rail(page):
        """The page's own left text rail — the leftmost x0 that RECURS among
        its full-measure lines. Recurrence is what makes 'leftmost' safe: one
        outdented stray cannot move the rail. None on a page too sparse to
        measure, so a caller keeps its own fallback.

        Lifted here from ``_circuit``, where it was written, after ``tex`` and
        ``_oregon`` each grew their own copy on the same day for the same
        reason: the separator starts at the measure the DOCUMENT is set to,
        which is not the court-wide ``body_baseline_x0`` constant. Measured
        across cadc, the rule starts at the page's own rail in 371 of 377
        cases."""
        xs: dict = {}
        for line in page.extract_text_lines():
            if line.get("x1", 0) - line.get("x0", 0) < page.width * 0.45:
                continue
            key = round(line.get("x0", 0))
            xs[key] = xs.get(key, 0) + 1
        recurring = [x for x, hits in xs.items() if hits >= 2]
        return float(min(recurring)) if recurring else None

    def _line_in_margin_band(self, line) -> bool:
        """Would the pipeline KEEP this text line, or is it margin furniture?

        Asked of the line's own chars with the court's own ``filter_margins``,
        so a per-court override (a font-keyed stamp filter, a page-1 exception)
        answers for itself rather than being second-guessed here."""
        for char in line.get("chars") or []:
            try:
                if self.filter_margins(char):
                    return True
            except Exception:
                return True
        return False

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
        # Width is the gate only when a court has CONFIGURED one. Left
        # unconfigured this returned None outright, so a court whose separator
        # is a typed underscore rule lost every footnote it had: pasuperct
        # draws no rect and no vector line anywhere, marks the zone with a row
        # of 8pt underscores, and sets the notes themselves at body size —
        # nothing else in the chain can see that. Unconfigured, the rule is
        # accepted on corroboration instead: a raised footnote label on the
        # first line beneath it.
        configured = self.footnote_sep_text_min_width
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
            if configured is not None:
                if (ln["x1"] - ln["x0"]) < configured:
                    continue
            elif not self._labelled_note_below(page, ln["top"]):
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

        deep_flags = self._deep_indent_flags(lines)

        segments = []
        current = []
        prev_i = None
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
                # A bold RUN inside a body line — a case name in a citation —
                # does not make that line a heading, and must not cut the
                # paragraph in half. Only a line that is bold THROUGHOUT is a
                # structural change; ``line_meta``'s dominant-font bold says
                # merely that most of the line's glyphs are bold, which a long
                # citation achieves on its own.
                bold_changed = self.bold_breaks_segment and (
                    self._line_all_bold(line) != self._line_all_bold(current[-1])
                )
                # A short line that simply fails to reach the right margin
                # reads as 'centered' — its midpoint drifts to the middle of
                # the measure. So a C↔L flip is only a structural change when
                # the 'centered' line opens well RIGHT of the paragraph's own
                # left margin; a line flush with that margin is the short LAST
                # line of the paragraph above, or the first line under a
                # heading, and joining it is correct. Both directions matter:
                # the short line can be the one arriving (L→C) or the one
                # already in hand (C→L). All other transitions stay boundaries.
                align_changed = align != prev_align
                if {prev_align, align} == {"C", "L"}:
                    suspect = line if align == "C" else current[-1]
                    neighbour = current[-1] if align == "C" else line
                    # Measure the margin from the OTHER lines — the suspect's
                    # own x0 must not define the margin it is tested against,
                    # or a heading alone in the segment always looks flush.
                    above = [l["x0"] for l in current if l is not suspect]
                    # Nothing above it to measure against — a heading standing
                    # alone in the segment — so compare with the line it would
                    # join instead.
                    para_left = (
                        max(self.body_baseline_x0, min(above))
                        if above
                        else neighbour["x0"]
                    )
                    # A block quote's item line hangs half an inch out from its
                    # own continuation and is still one block; a centered
                    # heading stands a full inch or more right of the text
                    # around it. Two indent steps sits between the two.
                    align_changed = (
                        suspect["x0"] > para_left + 2 * self.indent_step
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
                    prev_deep = bool(prev_i is not None and deep_flags[prev_i])
                    this_deep = bool(deep_flags[i])
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
            prev_i = i
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

    def _deep_indent_flags(self, lines) -> list:
        """Per-line: is this line a BLOCK-QUOTE left edge (as opposed to a
        paragraph's first-line indent)? Used by ``segment_lines`` on
        ``blockquote_by_indent`` courts to split a quote into its own segment
        when spacing alone can't.

        Two lines get excluded from 'deep':

        * a line that OPENS a numbered paragraph ('¶13 …') — its continuations
          wrap back to the body margin, so its indent is a first line (wis);
        * a LONE deep line whose neighbours sit back at the body margin. A
          block quote holds its left edge for at least two consecutive lines;
          one indented line followed by lines that wrap out to the margin is a
          first-line indent. Courts that indent the first line a full two
          inches (the New York districts' Courier template) land past the
          quote threshold, and without this every paragraph would be cut after
          its opening line.
        """
        if not self.blockquote_by_indent:
            return [False] * len(lines)
        # The deep-indent boundary is measured from the DOCUMENT's body column
        # when known (the pre-pass supplies it during segmentation): a
        # narrow-measure chambers sets its whole body past the constant
        # boundary, which read every line as quote-deep and cut the body into
        # one segment per line.
        base = self.body_baseline_x0
        geom = getattr(self, "_doc_geom", None)
        if geom and self.measured_gap_bands:
            base = max(base, geom["body_x0"])
        deep = base + 1.5 * self.indent_step
        raw = [
            l["x0"] >= deep and not self._begins_paragraph_block([l]) for l in lines
        ]
        out = []
        for i, d in enumerate(raw):
            if d:
                d = any(
                    0 <= j < len(lines)
                    and raw[j]
                    and abs(lines[j]["x0"] - lines[i]["x0"]) <= 3
                    for j in (i - 1, i + 1)
                )
            out.append(d)
        return out

    def classify_segment(self, seg) -> str:
        """notice / blockquote / body / single / spaced."""
        # Some courts (notably Kentucky) set an entire quoted exhibit at a
        # deeper left margin. Font changes inside that exhibit—section titles,
        # numbered headings, ellipses—can split it into one-line segments, so
        # apply the quote geometry before the length/gap classification.
        if self.blockquote_by_indent and self._is_quote_like_segment(seg):
            return "blockquote"
        if len(seg) == 1:
            # A standalone ellipsis is commonly an omitted portion inside a
            # quoted statute, rule, transcript, or record excerpt. It is a
            # structural quote line even though segmentation gives it no
            # neighboring lines from which to infer that context.
            if self.line_plain_text(seg[0]).strip() in ("...", "…", ". . ."):
                return "blockquote"
            return "single"
        gaps = [seg[i + 1]["top"] - seg[i]["top"] for i in range(len(seg) - 1)]
        med = median(gaps)
        tight_max, single_max, double_max = self._effective_gap_bands()
        if med < tight_max:
            kind = "notice"
        elif med < single_max:
            kind = "blockquote"
        elif med < double_max:
            kind = "body"
        else:
            kind = "spaced"
        # A both-margins-indented run is a block quote regardless of which tight
        # gap band its (often sub-body) leading lands in — geometry, not gaps.
        if kind in ("notice", "body") and self._is_indented_blockquote(seg):
            kind = "blockquote"
        return kind

    def _is_quote_like_segment(self, seg) -> bool:
        """True for any segment wholly inside a court's quote measure.

        Unlike ``_is_indented_blockquote`` this also accepts one-line and
        bold-heading segments, allowing a multi-line quoted statute or policy
        excerpt to keep one semantic container across internal typography.
        """
        if not seg:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        # Judge the quote measure against the DOCUMENT's own body column when
        # it was measurable — same floor/cap semantics as
        # _is_indented_blockquote. A chambers that typesets its orders on a
        # narrow law-review measure (txwd: body at x0=144, right 468) is not
        # one long quotation of itself.
        base_left = self.body_baseline_x0
        right_edge = pw - self.body_baseline_x0
        geom = getattr(self, "_doc_geom", None)
        if geom and self.measured_gap_bands:
            base_left = max(base_left, geom["body_x0"])
            right_edge = min(right_edge, geom["right_x1"])
        quote_left = base_left + 1.5 * self.para_indent_min
        quote_right = right_edge - 24
        left = min(line["x0"] for line in seg)
        # A centered section heading can also fit inside both numerical
        # margins. A real quotation starts near the body column and moves
        # inward; reject lines whose entire segment lives in the centered
        # half of the page.
        if left > pw * 0.4:
            return False
        if all(self._line_all_bold(line) for line in seg):
            return False
        return (
            left >= quote_left
            and max(line["x1"] for line in seg) <= quote_right
        )

    def _premeasure_geometry(self, pdf) -> None:
        """A quick first read of the document's geometry BEFORE the page loop.

        Segmentation runs inside the loop and needs the body column too — a
        narrow-measure chambers (txwd at x0=144/468) otherwise has its body
        split line-by-line as quote runs before classification ever sees the
        measured profile. Sampled from a few interior pages (the caption page
        skews the columns); the full-precision measurement over every
        collected line replaces it after the loop."""
        lines = []
        try:
            pages = pdf.pages[1:4] or pdf.pages[:1]
            for page in pages:
                for line in page.extract_text_lines():
                    if (line.get("text") or "").strip() and line["top"] > 80:
                        lines.append(line)
        except Exception:
            return
        if len(lines) < 12:
            return
        x1s = sorted(l["x1"] for l in lines)
        right_x1 = x1s[int(0.95 * (len(x1s) - 1))]
        full = [l for l in lines if l["x1"] >= right_x1 - 36]
        if len(full) < 6:
            return
        body_x0 = Counter(round(l["x0"]) for l in full).most_common(1)[0][0]
        leads = Counter()
        for a, b in zip(lines, lines[1:]):
            gap = round(b["top"] - a["top"])
            if 5 < gap < 60:
                leads[gap] += 1
        lead = (
            float(leads.most_common(1)[0][0])
            if sum(leads.values()) >= 8
            else None
        )
        self._doc_geom = {
            "body_x0": float(body_x0),
            "right_x1": float(right_x1),
            "lead": lead,
        }

    def _measure_doc_geometry(self, all_segments) -> None:
        """Measure THIS document's body column from its own lines.

        ``body_baseline_x0`` is a per-court constant — a guess about where a
        court usually sets its body margin. Judged against that guess, a court
        whose real column sits further right (a federal circuit at x0≈108, the
        body running to x1≈504 on 612pt paper) reads as "indented on both
        margins" and its entire body classifies as one long block quote. The
        cure is to measure, not tune: take the lines that RUN TO the right
        measure — wrapped continuations, the one population that always sits on
        the true body margin — and read the column off their modal x0.

        Sets ``self._doc_geom = {"body_x0", "right_x1"}``, or leaves it None
        when the document is too small to measure confidently (a 1-page order):
        callers fall back to the constants.
        """
        lines = [l for _, seg, _ in all_segments for l in seg]
        if len(lines) < 12:
            return
        x1s = sorted(l["x1"] for l in lines)
        # The right measure, read robustly: the 95th-percentile x1 rather than
        # the max, so one stray wide line (a stamp, a rotated margin note the
        # geometry fix missed) can't stretch it.
        right_x1 = x1s[int(0.95 * (len(x1s) - 1))]
        # Full lines: those reaching within half an inch of the right measure.
        # Quotes and headings stop short by construction; these are the body's
        # wrapped continuation lines, which sit ON the left body margin.
        full = [l for l in lines if l["x1"] >= right_x1 - 36]
        if len(full) < 6:
            return
        body_x0 = Counter(round(l["x0"]) for l in full).most_common(1)[0][0]
        # The document's dominant leading, from consecutive same-segment line
        # pairs. A court can print two templates (Georgia: 16pt single-spaced
        # slips AND 36pt double-spaced disciplinary opinions; DC: double-spaced
        # opinions AND 16pt single-spaced orders), so the lead is a fact about
        # the document, never about the court.
        leads = Counter()
        for _, seg, _ in all_segments:
            for a, b in zip(seg, seg[1:]):
                gap = round(b["top"] - a["top"])
                if 5 < gap < 60:
                    leads[gap] += 1
        lead = (
            float(leads.most_common(1)[0][0])
            if sum(leads.values()) >= 8
            else None
        )
        self._doc_geom = {
            "body_x0": float(body_x0),
            "right_x1": float(right_x1),
            "lead": lead,
        }

    def _split_quote_runs(self, all_segments) -> list:
        """Split quote-geometry runs out of single-spaced body segments.

        In a single-spaced document a block quote keeps the body's leading, so
        gap-based segmentation never separates it: quote and body arrive as
        one segment whose min(x0) is the body margin, and the whole thing
        classifies as body (ohioctcl bankston: a 4-line R.C. 2743.75 quotation
        at x0 108-144 / x1≈504 inside a 72→540 body). Walk each body segment,
        cut it at transitions between body-column lines and lines wholly
        inside the quote measure, and keep a cut only when the indented run
        independently passes ``_is_indented_blockquote`` — anything else
        (centered headings, ragged short lines) leaves the segment untouched.
        """
        geom = getattr(self, "_doc_geom", None)
        if not geom or not self.split_quote_runs:
            return all_segments
        pw = getattr(self, "_page1_width", None) or 612.0
        body_x0 = max(self.body_baseline_x0, geom["body_x0"])
        right = min(pw - self.body_baseline_x0, geom["right_x1"])

        def indented(line):
            # Both margins per line: a paragraph FIRST line shares the quote's
            # left indent but runs to the full measure (ohioctcl '{¶7} …' at
            # x0=108/x1=540 directly under a 108/504 quote) — it ends the run.
            # Runs this splits too finely simply fail the ≥3-line acceptance
            # and merge back into the body, so nothing fragments.
            return line["x0"] >= body_x0 + 15 and line["x1"] <= right - 24

        out = []
        for page_no, seg, kind in all_segments:
            if kind != "body" or len(seg) < 4:
                out.append((page_no, seg, kind))
                continue
            pieces = [[seg[0]]]
            for line in seg[1:]:
                if indented(line) == indented(pieces[-1][-1]):
                    pieces[-1].append(line)
                else:
                    pieces.append([line])
            # ≥3 lines: a body paragraph's own indented FIRST line is one
            # line, and two stacked short one-line paragraphs (common in
            # {¶N} courts) share an indent without being a quote. Three
            # both-margins-indented lines with a common edge is quote
            # geometry.
            accepted = {
                i
                for i, piece in enumerate(pieces)
                if len(piece) >= 3
                and indented(piece[0])
                and self._is_indented_blockquote(piece)
            }
            if not accepted:
                out.append((page_no, seg, kind))
                continue
            merged = []  # (is_quote, lines) with non-quote neighbors joined
            for i, piece in enumerate(pieces):
                if i in accepted:
                    merged.append((True, list(piece)))
                elif merged and not merged[-1][0]:
                    merged[-1][1].extend(piece)
                else:
                    merged.append((False, list(piece)))
            for is_quote, lines in merged:
                if is_quote:
                    out.append((page_no, lines, "blockquote"))
                else:
                    out.append((page_no, lines, self.classify_segment(lines)))
        return out

    def _is_indented_blockquote(self, seg) -> bool:
        """True if ``seg`` is a multi-line run indented on BOTH margins — the
        geometric signature of a block quote: left indented in from the body
        margin, the longest line still short of the right margin (where a body
        paragraph runs flush), AND a consistent flush-left edge (≥2 lines share
        the block's left column). The last requirement rejects centered/short
        headings, which are also both-margins-indented but vary their left edge
        line-to-line.

        Margins come from the document itself when it was big enough to
        measure (``_doc_geom``), floored/capped by the class constants so a
        hand-tuned court is never judged against LOOSER margins than its own:
        the measured column can only pull the thresholds inward, toward the
        text that is actually on the page."""
        if len(seg) < 2:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        geom = getattr(self, "_doc_geom", None)
        base_left = self.body_baseline_x0
        right = pw - self.body_baseline_x0
        if geom:
            base_left = max(base_left, geom["body_x0"])
            right = min(right, geom["right_x1"])
        left = base_left + self.para_indent_min
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

    def _line_all_bold(self, line) -> bool:
        """True when a line's boldness is STRUCTURAL — a heading — rather than
        a bold run inside prose.

        Two conditions. Every printable glyph must be bold: a body line
        carrying a bold case name is only *mostly* bold, which the dominant
        font reports as bold outright. And the line must stop short of the
        right measure: a heading is short, whereas a case name long enough to
        fill a whole line of a string citation runs to the margin like any
        other body line and is still prose.
        """
        # Judge boldness on LETTERS AND DIGITS only. Quotation marks, periods
        # and brackets are routinely left in the roman face inside an
        # otherwise-bold passage, and counting them would call a fully bold
        # block quote line ('"The parties acknowledge and agree that this')
        # mixed, splitting the quote at its own opening quote mark.
        seen = False
        for c in line.get("chars") or []:
            t = c.get("text") or ""
            if not t.strip() or not t.isalnum():
                continue
            seen = True
            if "Bold" not in (c.get("fontname") or ""):
                return False
        if not seen:
            return False
        pw = getattr(self, "_page1_width", None) or 612.0
        right_edge = pw - self.body_baseline_x0
        return line["x1"] < right_edge - 0.06 * (right_edge - self.body_baseline_x0)

    @staticmethod
    def _line_all_emphasized(line) -> bool:
        """True when every alphanumeric glyph is bold or italic/oblique."""
        seen = False
        for char in line.get("chars") or []:
            text = char.get("text") or ""
            if not any(ch.isalnum() for ch in text):
                continue
            seen = True
            font = char.get("fontname", "") or ""
            if not any(style in font for style in ("Bold", "Italic", "Oblique")):
                return False
        return seen

    def line_alignment(self, line, page_width) -> str:
        x0 = line["x0"]
        x1 = line["x1"]
        width = x1 - x0
        cx = (x0 + x1) / 2
        # A line that FILLS the document's measured column is justified prose,
        # never centered — a narrow-measure court (cafc's 324pt column at
        # x0=144) puts every full line's midpoint exactly on the page axis,
        # and reading those as 'C' turned body lines into bold headings and
        # cut paragraphs at every alignment flip. Centering is judged inside
        # the measured column; only genuinely short lines can be centered.
        full_measure = False
        geom = getattr(self, "_doc_geom", None)
        if geom and self.measured_gap_bands:
            column = geom["right_x1"] - geom["body_x0"]
            if column > 100:
                full_measure = width >= 0.82 * column
        if (
            not full_measure
            and x0 > 100
            and abs(cx - page_width / 2) < 25
            and width < page_width * 0.55
        ):
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

    def _effective_gap_bands(self) -> tuple:
        """The gap bands, rescaled to THIS document's measured lead when the
        configured bands contradict it.

        At-or-below single_max covers three failure shapes: a lead inside the
        blockquote band (DC's 16pt against tight 16 / single 22 — a
        single-spaced order from a double-spaced court reads as one long
        quote); one below even the notice band (cacd civil minutes at 15.3pt,
        where the ruling classified 'notice' and never split into
        paragraphs); and a lead sitting exactly ON a band edge (cafc's 14pt
        against single_max 14 — ±0.05pt gap jitter then coin-flips every
        line's zone, shredding segments). Every consumer — classify_segment,
        gap_bucket/line_zone — must read the SAME bands or they disagree at
        exactly these edges."""
        tight, single, double = (
            self.gap_tight_max,
            self.gap_single_max,
            self.gap_double_max,
        )
        geom = getattr(self, "_doc_geom", None)
        lead = (geom or {}).get("lead") if self.measured_gap_bands else None
        if lead and lead <= single:
            return 0.45 * lead, 0.85 * lead, 1.5 * lead
        return tight, single, double

    def gap_bucket(self, g) -> Optional[str]:
        if g is None:
            return None
        tight, single, double = self._effective_gap_bands()
        if g < tight:
            return "tight"
        if g < single:
            return "single"
        if g < double:
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
        return self.is_rule_text(line.get("text") or "")

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
        if getattr(self, "_order_start", None) is not None:
            # The unsigned-order fallback anchors on the ORDER title, which is
            # body content, not a byline; the author is the /s/ signature.
            return (self._order_author or ""), [line]
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
        # A judge's SURNAME is never itself a bench word. When a byline-shaped
        # sentence wraps, its continuation can open with the tail of the title
        # ('Judge, Joseph F. Bianco, and Michael H. Park, Circuit Judges,
        # dissents by opinion' — the second line of 'Richard J. Sullivan,
        # Circuit Judge, joined by Debra Ann Livingston, Chief / Judge, …'),
        # and the grammar then reads 'Judge' as the name. That false byline is
        # a segment boundary, so the sentence was cut in half mid-phrase.
        name = m.group("name")
        if name.rstrip(".").lower() in _BENCH_WORDS:
            return None
        kind = m.group("kind1") or m.group("kind2")
        return name, m.group("title"), kind

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

    def _order_fallback(self, all_segments) -> list:
        """No byline anywhere: an unsigned ORDER. Without this, the whole
        document lands in headmatter (delch wsp_usa: a 12-page numbered-
        paragraph order became 375 summary rows). The body starts at the
        'ORDER …' title ('ORDER', 'ORDER GRANTING DEFENDANT'S MOTION TO
        DISMISS'); the author, when present, is the conformed '/s/ Name'
        signature with its adjacent title line."""
        start = next(
            (
                i
                for i, (_p, seg, _k) in enumerate(all_segments)
                if seg
                and self.line_plain_text(seg[0]).strip().upper().startswith("ORDER")
            ),
            None,
        )
        if start is None:
            return []
        self._order_start = start
        self._order_author = self._conformed_signature_author(all_segments)
        return [start]

    def _conformed_signature_author(self, all_segments):
        """'/s/ Name' (or '/s Name') plus its adjacent judicial title line —
        title-first ('Chancellor Kathaleen St. J. McCormick') or title-last
        ('Abigail M. LeGrow, Justice') both appear across courts."""
        lines = [l for _p, seg, _k in all_segments for l in seg]
        titles = ("justice", "judge", "chancellor", "magistrate", "commissioner")
        for i, line in enumerate(lines):
            t = self.line_plain_text(line).strip()
            if not t.lower().startswith(("/s/", "/s ")):
                continue
            name = t[3:].strip()
            if i + 1 < len(lines):
                nxt = self.line_plain_text(lines[i + 1]).strip()
                if any(w in nxt.lower() for w in titles):
                    return f"{name}, {nxt}" if not nxt.lower().startswith(
                        titles
                    ) else nxt
            return name
        return None

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
            if align == "L" and _is_typed_rule_text(self.line_plain_text(line)):
                out_events.append((pno, top, self.paragraph_text([line])))
                i += 1
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
                    # A CHANGE OF TYPE SIZE ends the run. CA11 sets each party
                    # at 14pt and its qualifier at 12pt directly under it
                    # ('EDDIE LAMPERT,' over 'individually,'); both are
                    # left-aligned and single-spaced, and the qualifier's
                    # indent is under the 12pt bar, so gap and indent alone
                    # merged the entire party list into one paragraph. Size is
                    # the signal the page itself uses to separate them.
                    # Size, NOT font name: an italic case name can dominate a
                    # prose line's font without ending the paragraph.
                    prev_size = self.line_meta(group[-1])[0]
                    this_size = self.line_meta(l2)[0]
                    if prev_size and this_size and abs(this_size - prev_size) > 0.6:
                        break
                    # A TYPED rule ('------' / '______') separates components;
                    # it is a divider the page draws in text, so a run must end
                    # at it and the next run must start after it. Without this
                    # the panel line, the caption's top border and the party
                    # names all merged into one row (ca2), because they are all
                    # left-aligned and tightly spaced.
                    if _is_typed_rule_text(self.line_plain_text(l2)):
                        break
                    group.append(l2)
                    j += 1
                    if _is_typed_rule_text(self.line_plain_text(l2)):
                        break
                text = " ".join(self.paragraph_text([l]) for l in group)
                out_events.append((pno, top, text))
                i = j
            else:
                text = self.paragraph_text([line])
                if align == "C":
                    text = f"<centered>{text}</centered>"
                elif align == "R" and self.mark_flush_right:
                    # A row pinned to the RIGHT margin kept its text but lost
                    # its alignment: only 'C' was marked, so CA11's italic
                    # status labels ('Plaintiff-Appellant' / 'Cross-Appellees')
                    # — set flush right against the parties on the left — came
                    # back left-aligned and the caption read as a flat list.
                    text = f"<flushright>{text}</flushright>"
                out_events.append((pno, top, text))
                i += 1

        cap_pno = getattr(self, "_caption_pno", 1)
        for div_top in page1_rules or []:
            out_events.append((cap_pno, div_top, self.HEADMATTER_DIVIDER))
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
        """Return the semantic block tag from paragraph geometry.

        Across reporters, a short centered row (occasionally a tight wrapped
        pair) set wholly in bold or uppercase is a section heading.  Recognize
        that shared visual grammar here so ``CONCLUSION`` / ``STANDARD OF
        REVIEW`` does not require a court-by-court word list.
        """
        if lines and len(lines) <= 3:
            pw = getattr(self, "_page1_width", None) or 612.0
            centered = all(self.line_alignment(line, pw) == "C" for line in lines)
            texts = [(line.get("text") or "").strip() for line in lines]
            compact = sum(len(text) for text in texts) <= 180
            emphasized = all(self._line_all_emphasized(line) for line in lines)
            letters = "".join(ch for text in texts for ch in text if ch.isalpha())
            all_caps = bool(letters) and letters.upper() == letters
            ornament = "".join(texts).replace(" ", "")
            ornamental_break = (
                len(ornament) >= 3 and all(ch in "*•·" for ch in ornament)
            )
            plain = " ".join(texts).strip()
            short_section_row = (
                len(plain) <= 100
                and len(plain.split()) <= 14
                and not plain.endswith((".", "?", "!"))
            )
            if centered and compact and (
                emphasized or all_caps or ornamental_break or short_section_row
            ):
                return "heading"
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
        # The configured floor can sit ABOVE the document's real body column
        # (cacd civil minutes print at x0=54 under the default 72, indenting
        # paragraph first lines to 90 — below 72+28, so nothing ever split).
        # The measured column caps the constant; courts that tuned a high
        # baseline measure the same value and are unaffected.
        floor = self.body_baseline_x0
        geom = getattr(self, "_doc_geom", None)
        if geom and self.measured_gap_bands:
            floor = min(floor, geom["body_x0"])
        indent_min = max(floor, seg_left) + self.para_indent_min
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
        of May, 2026.') where neither line reaches the measure.

        A group is first cut where it crosses between the body column and a
        RIGHT-hand column. A signature block is set in its own column in the
        right half of the measure; body prose is never set there, and a line
        that jumps back to the body margin below it cannot be its
        continuation. That cut is what separates 'United States Magistrate
        Judge' from the 'Dated: …' / 'Rochester, New York' stamp beneath it.
        Every line of a right-column run is its own line for the same reason:
        nothing in that column wrapped."""
        if not self.split_line_stacks:
            return paras
        pw = getattr(self, "_page1_width", None) or 612.0
        page_right = pw - self.body_baseline_x0

        out = []
        for grp in paras:
            # Measure a run in ITS OWN column, not the page's. A block set in
            # from the body margin (a quote, a quoted rule) has a narrower
            # measure — inset from the right by the same step it is inset from
            # the left — so judging its wrap against the PAGE measure reads
            # every one of its lines as 'never reached the margin' and
            # explodes a wrapped quote into one paragraph per line.
            left, right_edge = self._run_measure(grp, pw, page_right)
            measure = right_edge - left
            wrap_min = right_edge - 0.15 * measure
            right_col = left + 0.35 * measure
            for run in self._split_at_column_change(grp, right_col):
                # An all-centered run is a wrapped centered heading — one
                # heading, never a stack. A MIXED run (name off-axis over a
                # coincidentally center-ish title line) is still a stack.
                if len(run) >= 2 and all(
                    self.line_alignment(l, pw) == "C" for l in run
                ):
                    out.append(run)
                elif len(run) >= 2 and (
                    all(l["x1"] < wrap_min for l in run)
                    or all(l["x0"] >= right_col for l in run)
                ):
                    out.extend([l] for l in run)
                else:
                    out.append(run)
        return out

    def _quote_insets(self, lines, op_body_left) -> dict:
        """A block quote's own measure, as a fraction of the body measure.

        A quote is set in from BOTH margins, and the review column is narrower
        than the printed page, so reproducing the inset in absolute points
        overshoots — badly, for a quote inset a full inch. Fractions of the
        opinion's measure reproduce the page's proportions at any column
        width. The left edge comes from the quote's own column (its leftmost
        line), not its first line, which may carry a paragraph indent of its
        own. The right inset is measured from the quote's longest line and
        capped at the left inset: a quote is inset roughly symmetrically, and a
        run of short ragged lines must not read as a deeply inset measure.
        """
        pw = getattr(self, "_page1_width", None) or 612.0
        page_right = pw - self.body_baseline_x0
        measure = page_right - op_body_left
        if measure <= 0 or not lines:
            return {}
        left_inset = max(0.0, min(l["x0"] for l in lines) - op_body_left)
        right_inset = min(
            max(0.0, page_right - max(l["x1"] for l in lines)), left_inset
        )
        if left_inset < 6:
            return {}
        return {
            "inset_left_pct": round(100.0 * left_inset / measure, 2),
            "inset_right_pct": round(100.0 * right_inset / measure, 2),
        }

    def _run_measure(self, grp, pw, page_right) -> tuple:
        """The left and right edges of the column ``grp`` is actually set in.

        Default: the page's body measure. But a run indented in from the body
        margin on BOTH sides — a block quote or a quoted subdivision, holding
        one left edge for at least two lines — is set in its own narrower
        column, and that is where its lines wrap. Typesetting insets such a
        block from the right by the same step it is inset from the left, so the
        left indent gives the right edge without having to trust the longest
        line. A run whose text runs on past that symmetric edge is not a
        symmetric block (a hanging indent, a shifted column), and keeps the
        page measure.
        """
        base = self.body_baseline_x0
        if len(grp) < 2:
            return base, page_right
        x0s = [l["x0"] for l in grp]
        left = min(x0s)
        inset = left - base
        if inset < self.para_indent_min or left > pw * 0.4:
            return base, page_right
        if sum(1 for x in x0s if abs(x - left) <= 3) < 2:
            return base, page_right
        if max(l["x1"] for l in grp) > page_right - inset + 6:
            return base, page_right
        return left, page_right - inset

    @staticmethod
    def _split_at_column_change(grp, right_col) -> list:
        """Cut ``grp`` wherever consecutive lines sit in different columns —
        one in the body column, the next in the right-hand column, or back."""
        runs: list = []
        for line in grp:
            side = line["x0"] >= right_col
            if runs and runs[-1][0] == side:
                runs[-1][1].append(line)
            else:
                runs.append((side, [line]))
        return [lines for _side, lines in runs]

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
        """Split a block quote without destroying meaningful internal form.

        A tight line run is not always one paragraph. Transcripts use a new
        speaker label for each turn, and quoted statutes/rules use numbered or
        lettered subdivisions. Those boundaries are structural even when the
        PDF gives every line identical leading. Ordinary wrapped prose keeps
        the existing gap-based behavior.
        """
        if not seg:
            return []
        paras = [[seg[0]]]
        gaps = [seg[i + 1]["top"] - seg[i]["top"] for i in range(len(seg) - 1)] or [0]
        med_gap = median(gaps)
        for i in range(1, len(seg)):
            line = seg[i]
            gap_b = line["top"] - seg[i - 1]["top"]
            if gap_b > med_gap * 1.4 or self._structured_quote_start(line):
                paras.append([line])
            else:
                paras[-1].append(line)
        return self._explode_line_stacks(paras)

    def _structured_quote_start(self, line) -> bool:
        """Whether a quote line opens a transcript turn or rule subdivision.

        Speaker labels are recognized from a short label ending in a colon
        whose label glyphs are bold/emphasized in the source PDF. Requiring
        that visual cue avoids mistaking ordinary quoted prose such as
        ``Note: ...`` for a transcript. Numbered/lettered starts are useful
        for statutes, regulations, jury instructions, and quoted rules; they
        are deliberately limited to the conventional subdivision shapes.
        """
        text = self.line_plain_text(line).strip()
        if not text:
            return False
        # Transcript exhibits often identify each turn by time rather than a
        # bold role label: ``[7:13 p.m.] Brown: ...``. The speaker may be
        # omitted (``[6:11 p.m.] : ...``), but the timestamp still marks a
        # new turn. Wrapped continuation lines do not begin with this shape
        # and therefore remain attached to the preceding turn.
        close = text.find("]") if text.startswith("[") else -1
        if close > 0 and self._is_timestamp_turn(text, close):
            return True
        if self._is_subdivision_start(text):
            return True
        colon = text.find(":")
        if colon <= 0 or colon > 60 or colon + 1 >= len(text):
            return False
        if not text[colon + 1].isspace():
            return False
        label = text[:colon].strip()
        if not label or len(label.split()) > 8:
            return False
        chars = line.get("chars") or []
        colon_i = next(
            (i for i, char in enumerate(chars) if (char.get("text") or "") == ":"),
            None,
        )
        if colon_i is None:
            return False
        label_chars = [c for c in chars[:colon_i] if (c.get("text") or "").isalnum()]
        if not label_chars:
            return False
        emphasized = sum(
            1
            for c in label_chars
            if any(style in (c.get("fontname") or "") for style in ("Bold", "Italic", "Oblique"))
        )
        return emphasized / len(label_chars) >= 0.75

    @staticmethod
    def _is_timestamp_turn(text: str, close: int) -> bool:
        """Parse ``[h:mm a.m.] Speaker: text`` without text-pattern regexes."""
        stamp = "".join(text[1:close].lower().split())
        if len(stamp) < 7 or ":" not in stamp:
            return False
        if not (stamp.endswith("a.m.") or stamp.endswith("p.m.")):
            return False
        hour, minute_and_meridiem = stamp.split(":", 1)
        minute = minute_and_meridiem[:2]
        if not (hour.isdigit() and minute.isdigit() and len(minute) == 2):
            return False
        colon = text.find(":", close + 1)
        return colon > close + 1 and colon < close + 62 and colon + 1 < len(text) and text[colon + 1].isspace()

    @staticmethod
    def _is_subdivision_start(text: str) -> bool:
        """Recognize common statute/rule subdivision markers structurally."""
        t = text.lstrip()
        if not t:
            return False
        if t.startswith("("):
            end = t.find(")")
            if end > 1 and (t[1:end].isdigit() or (len(t[1:end]) == 1 and t[1:end].isalpha())):
                return end + 1 < len(t) and t[end + 1].isspace()
        dot = t.find(".")
        if dot == 1 and (t[0].isalpha() or t[0].lower() in "ivxlcdm"):
            return dot + 1 < len(t) and t[dot + 1].isspace()
        return False

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
    @staticmethod
    def _line_type_size(chars) -> float:
        """The line's own type size — measured from glyphs that print INK.

        A blank glyph's size is not evidence about the size of the type it sits
        in. Justified setting can widen an inter-sentence space by giving it its
        own larger font instance: berk_v._choy p16 sets a single 11pt SPACE in
        the middle of a 9pt footnote line. Counting it made the line read as
        11pt type, which put the 9pt PROSE inside the small-glyph band — so the
        footnote's own 7pt label stopped being the shortest run on the line and
        the mark test rejected it, leaving '1To the extent that ...' with the
        label welded to the first word."""
        inked = [
            round(c.get("size", 0), 1)
            for c in chars
            if (c.get("text") or "").strip()
        ]
        return max(inked) if inked else max(
            (round(c.get("size", 0), 1) for c in chars), default=0.0
        )

    def _footnote_mark_chars(self, chars, body_size) -> list:
        """Per-char: may this small glyph be read as a footnote MARK?

        Being smaller than the rest of the line is necessary but not
        sufficient. A mark is a SHORT run — one to three label characters and
        nothing else. A longer small run, or one carrying letters, is ordinary
        small print sharing the line: the Wisconsin caption sets
        'Cir. Ct. No.  2024CV549' at 9pt beside a 13pt 'Appeal No.  2025AP825',
        and on size alone its digits read as a string of footnote references.
        """
        # A mark is RAISED. A small glyph sitting BELOW the line's own baseline
        # is a subscript — the digits of a chemical formula (C₁₀H₁₅N), which
        # read out as 'C H N' once the digits are taken for footnote
        # references and dropped from the text.
        full_tops = [
            c.get("top")
            for c in chars
            if round(c.get("size", 0), 1) > body_size - 1.5
            and (c.get("text") or "").strip()
            and c.get("top") is not None
        ]
        base_top = min(full_tops) if full_tops else None
        small = [
            round(c.get("size", 0), 1) <= body_size - 1.5
            and bool((c.get("text") or "").strip())
            and (
                base_top is None
                or c.get("top") is None
                or c["top"] <= base_top + 1.0
            )
            for c in chars
        ]
        out = [False] * len(chars)
        i = 0
        while i < len(chars):
            if not small[i]:
                i += 1
                continue
            j = i
            while j < len(chars) and (
                small[j] or not (chars[j].get("text") or "").strip()
            ):
                j += 1
            run = [c for c in chars[i:j] if (c.get("text") or "").strip()]
            labels = [c for c in run if c["text"] in self.FOOTNOTE_LABEL_CHARS]
            # Punctuation may ride along with a mark — a bracketed editorial
            # reference sets its closing ']' at the same reduced size. What
            # disqualifies a run is LETTERS (a small-print docket number,
            # '2024CV549') or more label characters than a mark ever has.
            if (
                labels
                and len(labels) <= 3
                and not any(c["text"].isalpha() for c in run)
            ):
                for k in range(i, j):
                    out[k] = small[k]
            i = j
        return out

    # Floor for the inferred word-break gap.  Historic fixed threshold; the
    # measured value below only ever rises above it.
    space_gap_min = 1.5
    # Alabama is fidelity-locked and opts out: measuring the threshold closes
    # the space it sets between a double and a single quote ('" \'Access' ->
    # '"\'Access'), which moves its byte-identical output.
    measured_space_gap: bool = True
    # Mark a headmatter row that is set flush RIGHT, so the renderer can hold
    # it at the margin.  Alabama opts out for the same fidelity reason: its
    # 'Clerk, Supreme Court of Alabama' sits flush right and would gain the
    # marker.
    mark_flush_right: bool = True

    def _inferred_space_gap(self, chars) -> float:
        """The x-gap that means a word break on THIS line, measured.

        A fixed threshold misreads a letter-spaced line.  CA10's 13pt bold
        caption tracks every glyph ~1.0pt apart and opens ~2.0pt after a
        hyphen, so ``(D.C. No. 1:21-CV-00923-GPG-STV)`` rebuilt as
        ``1:21-CV-00923- GPG- STV`` — spaces the page never set.

        Read the line's own typography instead of guessing.  The modal gap
        between adjacent glyphs is the line's tracking; the width of its own
        space glyph is what a word break costs.

        When the page sets real space glyphs, every word break is already
        encoded — so a gap narrower than one of those spaces cannot be a
        break, it is justification tracking (CA10 opens 3.0pt inside
        'Plaintiffs' on a justified line whose spaces are all explicit).
        Require the full measured word-break advance there.

        A line carrying NO space glyph keeps the historic floor.  There is
        nothing to measure against on such a line, and its modal gap is not
        tracking at all — on an ornamental break ('* * *') the only gaps
        present ARE the word gaps, so treating them as tracking raised the
        threshold above them and closed the rule up to '***'."""
        if not self.measured_space_gap:
            return self.space_gap_min
        gaps = []
        widths = []
        prev = None
        for c in chars:
            text = c.get("text") or ""
            if text == " ":
                widths.append(c["x1"] - c["x0"])
            elif prev is not None:
                gaps.append(c["x0"] - prev)
            prev = None if text == " " else c["x1"]
        if not gaps:
            return self.space_gap_min
        gaps.sort()
        track = gaps[len(gaps) // 2]
        if not widths:
            return self.space_gap_min
        widths.sort()
        return max(self.space_gap_min, track + widths[len(widths) // 2])

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
        body_size = self._line_type_size(chars)
        space_gap = self._inferred_space_gap(chars)
        mark_ok = self._footnote_mark_chars(chars, body_size)
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

        for _ci, c in enumerate(chars):
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
                if gap > space_gap:
                    if cur_fn:
                        parts.append(f"<footnotemark>{escape(cur_fn)}</footnotemark>")
                        cur_fn = ""
                        buf += " "
                    elif buf and not buf.endswith(" "):
                        buf += " "

            small = mark_ok[_ci]
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
        space_gap = self._inferred_space_gap(chars)
        prev_x1 = None
        prev_pos = None
        for c in chars:
            pos = (round(c["x0"], 1), round(c["x1"], 1), c.get("text"))
            if pos == prev_pos:  # skip a double-emitted ligature glyph
                continue
            prev_pos = pos
            if (
                prev_x1 is not None
                and (c["x0"] - prev_x1) > space_gap
                and out
                and not out[-1].endswith(" ")
            ):
                out.append(" ")
            out.append(c.get("text") or "")
            prev_x1 = c["x1"]
        return "".join(out)

    # Rejoin a word the page broke across a line with a hyphen. Alabama is
    # fidelity-locked to the old ca1/casebody output and opts out.
    rejoin_wrapped_hyphens: bool = True

    def _learn_vocabulary(self, source_pages) -> None:
        """The document's own word list, used to tell a line-break hyphen from a
        real compound hyphen.

        There is no geometric difference between the two: 'Switzer-' at the end
        of a justified line and 'natural-' in 'natural-born' are the same glyph
        in the same font at the same right measure. What DOES separate them is
        the document's own vocabulary — an opinion repeats its terms, so
        'Switzerland' appears unbroken somewhere else on the page or in the
        footnotes, and 'natural-born' appears unbroken WITH its hyphen. Measured
        on trump_v._barbara: of 518 hyphen line-breaks, 422 are proved soft this
        way outright, and the handful of genuine compounds ('natural-born',
        'quasi-sovereign', 'domicile-based') are the ones the hyphenated form
        rescues."""
        words = set()
        for _pno, lines in source_pages:
            for line in lines:
                for tok in line.split():
                    tok = tok.strip("“”\"'’‘()[]{}.,;:!?*†‡§¶").lower()
                    # A token that ENDS in a hyphen is itself a broken word; it
                    # is no evidence of anything unbroken.
                    if tok.endswith("-"):
                        continue
                    if tok and all(c.isalpha() or c in "-’'" for c in tok):
                        words.add(tok)
        self._doc_words = words

    def _hyphen_break_at(self, markup):
        """``(index_of_hyphen, word_before_it)`` when ``markup`` ends — ignoring
        inline tags and trailing space — on a hyphen that closes a word; else
        None. The hyphen may sit inside markup ('<em>Switzer-</em>')."""
        depth = 0
        vis = []  # (index in markup, char)
        for i, ch in enumerate(markup):
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                vis.append((i, ch))
        while vis and vis[-1][1].isspace():
            vis.pop()
        if not vis or vis[-1][1] != "-":
            return None
        word = []
        for _i, ch in reversed(vis[:-1]):
            if ch.isalpha() or ch in "’'":
                word.append(ch)
            else:
                break
        if not word:
            return None  # a dash standing alone, not a broken word
        return vis[-1][0], "".join(reversed(word))

    @staticmethod
    def _head_word_span(markup) -> tuple:
        """``(leading word of markup's visible text, index just past it)``.
        Inline tags and leading space are skipped, so the word is found even
        behind a ``<pagenumber .../>`` marker or an opening ``<em>``."""
        depth = 0
        out = []
        end = 0
        for i, ch in enumerate(markup):
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                if ch.isalpha() or (out and ch in "’'"):
                    out.append(ch)
                    end = i + 1
                elif out or not ch.isspace():
                    break
        return "".join(out), end

    def _head_word(self, markup) -> str:
        """The leading word of ``markup``'s visible text, tags skipped."""
        return self._head_word_span(markup)[0]

    def _compound_hyphen(self, left, right) -> bool:
        """Was the hyphen between ``left`` and ``right`` PRINTED, or inserted by
        the line breaker? True = printed, so it survives the join.

        Read off the document's own vocabulary, in order of how much each
        reading proves:

        1. the halves appear joined and unbroken somewhere ('Switzerland') —
           the hyphen was the line breaker's. This settles about two thirds of
           them on its own.
        2. they appear joined WITH the hyphen ('natural-born', 'state-created',
           'pre-certification') — printed.

        Otherwise the hyphen came from the line break. That is the right
        default by a wide margin, and it is the only reading with evidence
        behind it: a rule inferring a compound from each HALF being a word the
        document uses ('of' + 'access') was measured at roughly even odds — it
        rescued 'of-access' and 'so-called' but also produced 'Like-wise' and
        'an-swer', because a prefix syllable is often a word too. What survives
        is 'cross-jurisdictional' read as one word in a document that never
        prints it unbroken — rare, and far less damage than 'Switzer- land'."""
        vocab = getattr(self, "_doc_words", None) or set()
        if (left + right).lower() in vocab:
            return False
        return (left + "-" + right).lower() in vocab

    def join_wrapped_lines(self, texts) -> str:
        """Join a paragraph's rendered lines, healing words the page broke with
        a hyphen. Without this the text reads 'Switzer- land', 'citizen- ship',
        'malprac- tice' — and those survive all the way into CourtListener's
        rendered HTML."""
        if not self.rejoin_wrapped_hyphens:
            # Byte-for-byte the join this replaced, empty rows included.
            return " ".join(texts)
        texts = [t for t in texts if t]
        if not texts:
            return ""
        out = texts[0]
        for nxt in texts[1:]:
            broken = self._hyphen_break_at(out)
            head = self._head_word(nxt) if broken else ""
            # Only a LOWERCASE continuation is a broken word. A capitalized one
            # is the second element of a compound ('Franco-American'), which
            # keeps its printed hyphen and its line break.
            if broken and head and head[:1].islower():
                hy, left = broken
                if self._compound_hyphen(left, head):
                    out = out + nxt  # a real compound: close the space, keep '-'
                else:
                    out = out[:hy] + out[hy + 1 :] + nxt
                continue
            out = out + " " + nxt
        return out

    def paragraph_text(self, lines) -> str:
        return self.join_wrapped_lines(
            [self.line_inline_text(l) for l in lines]
        )

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
        footnote_tables_by_page=None,
    ) -> Opinion:
        images_by_page = images_by_page or {}
        footnote_tables_by_page = footnote_tables_by_page or {}
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
        quote_xs = [
            l["x0"]
            for k in range(op_start, op_end)
            for l in all_segments[k][1]
            if all_segments[k][2] == "blockquote"
        ]
        quote_left = min(quote_xs) if quote_xs else self.body_baseline_x0
        # This opinion's right measure, for judging whether a line WRAPPED.
        op_right = max(
            (
                l["x1"]
                for k in range(op_start, op_end)
                for l in all_segments[k][1]
            ),
            default=None,
        )
        # (page_no, lines) of the last block added under each kind, so a
        # quotation broken by a page break can be folded back together.
        last_of_kind: dict = {}

        def folds_after_page_break(tag, lines, page_no) -> bool:
            """Does ``lines`` continue the quotation in ``blocks[-1]``?

            A page break must not break a paragraph (and a block quotation is a
            paragraph). The ``p`` branch below has always folded; quotations
            never did, so THOMAS's Speck denial came out as one block ending
            'after his' and a second starting 'father returned with him'.

            Three things have to hold, all measured: the quotation above ran to
            the RIGHT MEASURE (a line ending short of it had finished, so
            nothing follows it), the new lines resume in the same column, and
            they do not open a new item of their own."""
            if tag != "blockquote" or not self.fold_quotes_across_pages:
                return False
            if not blocks or blocks[-1].kind != "blockquote":
                return False
            prev = last_of_kind.get("blockquote")
            if not prev or prev[0] == page_no or op_right is None:
                return False
            if lines[0].get("_hang_marker"):
                return False
            if abs(lines[0]["x0"] - prev[1][0]["x0"]) > 3:
                return False
            return prev[1][-1]["x1"] >= op_right - 6

        def add_para(tag, lines, page_no):
            if not lines:
                return
            txt = self.paragraph_text(lines)
            if not txt.strip():
                return
            if tag == "p" and txt.strip() in ("...", "…", ". . ."):
                tag = "blockquote"
            if self._is_page_number_text(txt):
                value = self._page_number_value(txt)
                registered = getattr(self, "_printed_folio_by_page", {}).get(page_no)
                if registered is not None and value == registered:
                    return  # registered folio furniture, never body text
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
            ) or folds_after_page_break(tag, lines, page_no):
                marker = self.page_marker(page_no)
                prev_text = blocks[-1].text
                broken = (
                    self._hyphen_break_at(prev_text)
                    if self.rejoin_wrapped_hyphens
                    else None
                )
                head, cut = self._head_word_span(txt) if broken else ("", 0)
                if broken and head[:1].islower():
                    # The page broke a WORD across the fold. Heal it, and set
                    # the page marker down after the whole word rather than
                    # inside it.
                    hy, _left = broken
                    blocks[-1].text = (
                        prev_text[:hy]
                        + prev_text[hy + 1 :]
                        + txt[:cut]
                        + (f" {marker}" if marker else "")
                        + txt[cut:]
                    )
                else:
                    middle = f" {marker}" if marker else ""
                    blocks[-1].text = f"{prev_text}{middle} {txt}"
            else:
                payload = {}
                first_line_indent = lines[0].get("_first_line_indent")
                if tag == "p" and first_line_indent:
                    payload["first_line_indent"] = round(
                        float(first_line_indent), 1
                    )
                if tag == "blockquote":
                    # Preserve the quote's absolute inset from the opinion's
                    # body margin. Measuring from quote_left made every
                    # quote's first line appear to have zero indent whenever
                    # the quote was internally flush-left.
                    indent = max(0.0, first_x0 - op_body_left)
                    if indent >= 6:
                        payload["indent"] = round(indent, 1)
                    payload.update(self._quote_insets(lines, op_body_left))
                blocks.append(Block(kind=tag, text=txt, page=page_no, payload=payload))
            if tag == "p":
                last_body_page[0] = page_no
            last_of_kind[tag] = (page_no, lines)

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

        # An image ABOVE the opinion's first line, on the page the opinion
        # starts on, sits in the caption zone — a filing stamp, a seal, a
        # caption-box graphic. It is headmatter furniture, never the ruling's
        # opening block, so it must not be pulled into the body.
        start_pno, start_seg, _sk = all_segments[op_start]
        start_top = start_seg[0]["top"] if start_seg else 0.0
        # ``op_pages`` holds only pages that contributed a body SEGMENT. A page
        # whose entire content is an image — a scanned order page stapled to a
        # digital caption (cacd 980704: page 2 is one full-page scan) — is
        # absent, and its image silently disappeared. The last opinion owns
        # any trailing image-only pages; nothing else can.
        img_pages = set(op_pages)
        if op_pages:
            # A page whose ENTIRE content is one image contributes no segment,
            # so it never reaches op_pages and its image was dropped without a
            # word. The trailing case was already covered; the MIDDLE was not —
            # ca11/roger_tejon sets three full-page screenshots at pages 12, 17
            # and 19 of a dissent running from 11 to 25, and all three
            # vanished. A page inside this writing's own span belongs to it:
            # no other writing can claim it.
            lo, hi = min(op_pages), max(op_pages)
            img_pages |= {p for p in images_by_page if lo < p < hi}
        if op_end >= len(all_segments) and op_pages:
            last_body_pg = max(op_pages)
            img_pages |= {p for p in images_by_page if p > last_body_pg}
        for pno in img_pages:
            for img in images_by_page.get(pno, []):
                if pno == start_pno and img["bottom"] <= start_top:
                    continue
                events.append((pno, img["top"], "image", img))
        # ``tables_by_page`` is already ownership-filtered by the caller. A
        # table-only continuation page contributes no prose segment, so it is
        # not in ``op_pages``; nevertheless its table belongs in this writing.
        op_pages |= set(tables_by_page)
        for pno in tables_by_page:
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
                            "has_header": payload.get("has_header", True),
                            "continuation": payload.get("continuation", False),
                        },
                    )
                )
            else:
                add_para(kind_, payload, page_no)

        op.blocks = blocks
        self._ensure_opinion_page_markers(op, op_pages)
        # A long footnote can consume an entire intervening page. Such a page
        # contributes no body segment, so it is absent from ``op_pages`` even
        # though extraction correctly placed its lines in this opinion's
        # already ownership-filtered footnote mapping. Include those keys or
        # the middle page of a cross-page footnote silently disappears.
        footnote_pages = op_pages | set(footnote_lines_by_page)
        op.footnotes = self.build_footnotes(
            footnote_pages,
            footnote_lines_by_page,
            seen_labels=set(),
            footnote_tables_by_page=footnote_tables_by_page,
        )
        return op

    def _ensure_opinion_page_markers(self, op: Opinion, op_pages: set) -> None:
        """Ensure one printed-folio marker for every substantive opinion page.

        A cross-page paragraph merge may already have placed the marker inside
        the previous page's block. If the new page instead starts a paragraph,
        prepend its marker to that page's first textual block. This makes marker
        presence independent of paragraph grouping.
        """
        rendered = " ".join(str(block.text or "") for block in op.blocks)
        for physical_page in sorted(op_pages):
            marker = self.page_marker(physical_page)
            if not marker or marker in rendered:
                continue
            first = next(
                (
                    block
                    for block in op.blocks
                    if block.page == physical_page
                    and block.kind not in ("image", "table")
                    and str(block.text or "").strip()
                ),
                None,
            )
            if first is None:
                continue
            first.text = f"{marker} {first.text}"
            rendered += " " + marker

    def build_footnotes(
        self,
        pages,
        footnote_lines_by_page,
        seen_labels=None,
        footnote_tables_by_page=None,
    ) -> list:
        """Group footnote lines for ``pages`` into ``Footnote`` objects.
        Cross-page continuation: lines without a leading small-digit label
        belong to the previous footnote."""
        if seen_labels is None:
            seen_labels = set()
        footnote_tables_by_page = footnote_tables_by_page or {}
        grouped = []  # [(label, [lines], opens_a_zone)]
        current = []
        current_label = None
        opens = False
        first_on_page = True
        for page_no in sorted(pages):
            first_on_page = True
            for line in footnote_lines_by_page.get(page_no, []):
                label = self.detect_footnote_label(line)
                if label is not None:
                    if current:
                        grouped.append((current_label, current, opens))
                    current_label = label
                    current = [line]
                    # Does this group stand at the HEAD of this page's footnote
                    # zone? That position is what identifies a carry-over.
                    opens = first_on_page
                    first_on_page = False
                else:
                    if current:
                        current.append(line)
                    else:
                        current = [line]
                        current_label = "?"
                        opens = first_on_page
                        first_on_page = False
        if current:
            grouped.append((current_label, current, opens))

        out = []
        by_label: dict = {}
        for label, lines, opens in grouped:
            if label in seen_labels and self.dedupe_footnote_labels:
                # A footnote too long for one page RESUMES on the next under its
                # own label. That is the same footnote, not a repeat, so
                # dropping it as a duplicate silently discarded the rest of it —
                # a whole page of quoted statute in hawapp/elizares.
                #
                # Identified by POSITION, not by the printed '(...continued)'
                # marker: only a carry-over can stand at the HEAD of a page's
                # footnote zone under a label already used, because labels run
                # in order through the document. A repeat further down a zone is
                # a genuine duplicate and still deduped.
                if opens:
                    fn = self.build_footnote_with_tables(
                        label, lines, footnote_tables_by_page
                    )
                    if fn.paragraphs:
                        prev = by_label.get(label)
                        if prev is not None:
                            prev.paragraphs = list(prev.paragraphs) + list(
                                fn.paragraphs
                            )
                            continue
                        out.append(fn)
                        by_label[label] = fn
                continue
            fn = self.build_footnote_with_tables(
                label, lines, footnote_tables_by_page
            )
            if fn.paragraphs:
                out.append(fn)
                by_label[label] = fn
                seen_labels.add(label)
        return out

    def detect_footnote_label(self, line) -> Optional[str]:
        """If ``line`` starts a new footnote, return its label; else None."""
        chars = line.get("chars") or []
        if not chars:
            return None
        plain = self.line_plain_text(line).strip()
        # Some courts place the raised label on a line by itself above
        # body-sized footnote prose. There is then no larger glyph on the same
        # line against which to prove superscripting, but inside a
        # separator-delimited footnote zone a short label-only line is
        # structurally unambiguous.
        if (
            plain
            and len(plain) <= 3
            and all(char in self.FOOTNOTE_LABEL_CHARS for char in plain)
        ):
            return plain
        body_size = self._line_type_size(chars)
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

    @staticmethod
    def _footnote_table_html(rows) -> str:
        """A footnote's table as inline markup.

        ``Footnote.paragraphs`` carries ``(tag, text)`` pairs, so a table is
        stored as one ``('table', markup)`` paragraph. Cells are escaped here,
        exactly as the body-table renderer does, so the string is safe to emit
        verbatim and the audit can read the cell text straight out of it."""
        if not rows:
            return ""
        out = ["<table>"]
        for ri, row in enumerate(rows):
            cell = "th" if ri == 0 else "td"
            out.append("<tr>")
            for c in row:
                out.append(f"<{cell}>{escape(str(c or ''))}</{cell}>")
            out.append("</tr>")
        out.append("</table>")
        return "".join(out)

    def _footnote_zone_tables(self, lines, footnote_tables_by_page) -> list:
        """Footnote-zone tables that fall within ``lines``' vertical span."""
        if not footnote_tables_by_page or not lines:
            return []
        pnos = set()
        for l in lines:
            chars = l.get("chars") or []
            pnos.add(
                (chars[0].get("page_number") if chars else l.get("page_number")) or 1
            )
        lo = min(l["top"] for l in lines)
        hi = max((l.get("bottom") or l["top"]) for l in lines)
        cand = [
            t
            for pno, tbls in footnote_tables_by_page.items()
            if pno in pnos
            for t in tbls
            if lo - 60 <= t["bbox"][1] <= hi + 60
        ]
        return sorted(cand, key=lambda t: t["bbox"][1])

    def build_footnote_with_tables(
        self, label, lines, footnote_tables_by_page
    ) -> Footnote:
        """Build a footnote whose zone also contains one or more TABLES.

        The table's own rows never reach ``lines`` — ``in_any_table`` filters
        them out — so the prose above and below a table would otherwise fuse
        into one paragraph and the table would have nowhere to sit. Split the
        lines at each table's bounding box instead, so the footnote reads
        prose / table / prose exactly as printed (hawapp/yang_1 footnote 7:
        'the sum of the subtotals for each … category:', the HRS table, then
        the arithmetic that totals it)."""
        tables = self._footnote_zone_tables(lines, footnote_tables_by_page)
        if not tables:
            return self.build_footnote(label, lines)
        fn = Footnote(label=label)
        rest = list(lines)
        for t in tables:
            btop = t["bbox"][1]
            above = [l for l in rest if (l.get("bottom") or l["top"]) <= btop + 2]
            rest = [l for l in rest if (l.get("bottom") or l["top"]) > btop + 2]
            if above:
                fn.paragraphs.extend(self.build_footnote(label, above).paragraphs)
            markup = self._footnote_table_html(t.get("rows") or [])
            if markup:
                fn.paragraphs.append(("table", markup))
        if rest:
            fn.paragraphs.extend(self.build_footnote(label, rest).paragraphs)
        return fn

    def build_footnote(self, label, lines) -> Footnote:
        fn = Footnote(label=label)
        if not lines:
            return fn
        paras, fn_baseline = self.split_footnote_paragraphs(lines)
        for i, plines in enumerate(paras):
            groups = self._split_footnote_structure(plines, fn_baseline)
            for group_i, (group, is_quote) in enumerate(groups):
                txt = self.join_wrapped_lines(
                    [self.line_inline_text(l) for l in group]
                ).strip()
                if i == 0 and group_i == 0 and txt.startswith("<footnotemark>"):
                    end = txt.find("</footnotemark>")
                    if end != -1:
                        txt = txt[end + len("</footnotemark>") :].lstrip()
                if not txt:
                    continue
                first_text = (group[0].get("text") or "").lstrip()
                tag = "blockquote" if (is_quote or (first_text.startswith(('"', "“")) and fn_baseline is not None and group[0]["x0"] > fn_baseline + 10)) else "p"
                fn.paragraphs.append((tag, txt))
        return fn

    def _split_footnote_structure(self, lines, fn_baseline):
        """Keep indented quoted rules/statutes structured inside footnotes."""
        if not lines:
            return []
        out = []
        current = [lines[0]]
        quoted = False
        for line in lines[1:]:
            text = (line.get("text") or "").strip()
            deeper = fn_baseline is not None and line["x0"] > fn_baseline + 10
            subdivision = self._is_subdivision_start(text)
            if subdivision or (deeper and not quoted):
                out.append((current, quoted))
                current = [line]
                quoted = True
            elif quoted and not deeper:
                out.append((current, True))
                current = [line]
                quoted = False
            else:
                current.append(line)
        out.append((current, quoted))
        return out
