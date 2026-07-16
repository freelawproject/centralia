"""Shared base for the U.S. district courts.

A district-court filing is one ruling by one judge, not the multi-opinion
byline-at-start shape of an appellate decision. So the model differs:

  * The author is taken from the **signature block** at the end — the line
    above a 'United States District Judge' / 'Magistrate Judge' title (the most
    universal signal across districts), or, failing that, from a 'Present: The
    Honorable NAME, ... JUDGE' minute-order line, a 'THE HONORABLE NAME, U.S.D.J.'
    heading, a caption 'Judge NAME' line, or a 'NAME, J.' byline.
  * The opinion begins at the document-type heading ('MEMORANDUM OPINION AND
    ORDER' / 'ORDER' / 'REPORT AND RECOMMENDATION' / ...) — the caption above it
    is headmatter — or, if there is no heading, at the first body paragraph.
  * The whole ruling is one opinion (docket orders included, per the project's
    'treat orders as opinions' rule).

The CM/ECF header band ('Case 1:23-cv-00358 Document #: 111 Filed: ... Page 1
of 16 PageID #:...') sits in the top margin and is already excluded by
``margin_top``; per-district subclasses add any court-specific stamp handling.
No regex (project rule); headings and titles are matched with string sets.
"""

from __future__ import annotations

from .generic import GenericExtractor

# Document-type headings that open a district ruling (lowercased, exact match
# after stripping trailing punctuation). Longest/most-specific are not needed —
# any match marks the opinion start.
_HEADINGS = frozenset(
    {
        "memorandum opinion and order",
        "memorandum opinion",
        "memorandum and order",
        "memorandum order",
        "memorandum decision and order",
        "memorandum decision",
        "memorandum ruling",
        "memorandum",
        "memorandum & order",
        "opinion and order",
        "order and opinion",
        "opinion",
        "order",
        "amended memorandum opinion and order",
        "amended memorandum opinion",
        "report and recommendation",
        "report & recommendation",
        "report and recommendation of the magistrate judge",
        "findings of fact and conclusions of law",
        "findings of fact",
        "decision and order",
        "ruling",
        "judgment",
        "final judgment",
        "order and reasons",
        "memorandum ruling and order",
        "ruling and order",
        "memorandum opinion & order",
    }
)

# Opening words of a compound ALL-CAPS document title ('ORDER ADOPTING …',
# 'MEMORANDUM OPINION GRANTING …'). A short ALL-CAPS line starting with one of
# these is the ruling's title, hence its start — not trailing headmatter.
_HEADING_STARTS = frozenset(
    {"order", "memorandum", "opinion", "findings", "judgment", "decision", "report"}
)

# Judicial titles that close a signature block; the line above carries the name.
_JUDGE_TITLES = (
    "united states district judge",
    "united states magistrate judge",
    "united states bankruptcy judge",
    "united states circuit judge",
    "senior united states district judge",
    "chief united states district judge",
    "senior united states magistrate judge",
    "u.s. district judge",
    "u.s. magistrate judge",
    "u.s.d.j.",
    "u.s.m.j.",
    "chief united states magistrate judge",
    "united states district court judge",
    "chief judge",
    "senior district judge",
    "district court judge",
    "district judge",
    "magistrate judge",
)
# Lines that sit in a signature block but are not the judge's name.
_SIG_SKIP = (
    "so ordered",
    "it is so ordered",
    "dated",
    "date",
    "entered",
    "signed",
    "s/",
    "/s/",
    "by the court",
)
# A date stamp ('Dated: …' / 'Signed: …') is part of the signature block — it
# sits between the conformed signature / image and the printed name, so the
# backward scan must include it and keep going (a 'so ordered' decretal does
# NOT, hence this is a strict subset of _SIG_SKIP).
_SIG_DATE = ("dated", "date", "signed", "entered")

# Headmatter-facsimile geometry.
_CAPTION_GAP = 8.0  # x-gap (pt) that separates caption runs / the divider
_CAPTION_CHAR_W = 6.0  # monospace column width
_CAPTION_LEFT = 72.0  # left text margin (column 0)


def _is_rule(text: str) -> bool:
    t = text.strip()
    return len(t) >= 3 and all(c in "_-–—" for c in t)


def _strip_sig_prefix(text: str) -> str:
    t = text.strip()
    for p in ("/s/", "s/"):
        if t.lower().startswith(p):
            return t[len(p) :].strip()
    return t


def _looks_like_name(text: str) -> bool:
    """A judge name in a signature block: 2–5 tokens, each capitalized
    (all-caps 'ROY K. ALTMAN' or title-case 'Shalina D. Kumar'), allowing
    initials, 'Jr.'/'III', hyphens."""
    t = _strip_sig_prefix(text).rstrip(",")
    toks = t.split()
    if not (2 <= len(toks) <= 6):
        return False
    for tok in toks:
        core = tok.rstrip(".,").replace("-", "").replace("'", "")
        if core.lower() in ("jr", "sr", "ii", "iii", "iv"):
            continue
        if not core or not core[0].isupper() or not core.isalpha():
            return False
    return True


class DistrictBase(GenericExtractor):
    drop_notice_in_body = False
    # District filings double-space the body but single-space block quotes at a
    # tight leading (Courier/Times ~13-15pt) — below gap_tight_max — so an
    # indented quote reads as a 'notice'. Re-tag it by its both-margins indent.
    blockquote_by_indent = True

    def extract(self, pdf_path):
        self._hm_super_labels = set()
        doc = super().extract(pdf_path)
        labels = getattr(self, "_hm_super_labels", set())
        if labels and doc.opinions:
            op = doc.opinions[0]
            moved = [f for f in op.footnotes if f.label in labels]
            if moved:
                op.footnotes = [f for f in op.footnotes if f.label not in labels]
                doc.headmatter_footnotes = list(doc.headmatter_footnotes) + moved
        self._harvest_signature(doc)
        return doc

    @staticmethod
    def _untag(text: str) -> str:
        """Plain text of a block's inline-HTML string (no markup)."""
        out, i = [], 0
        s = str(text)
        while True:
            j = s.find("<", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            k = s.find(">", j)
            if k < 0:
                break
            i = k + 1
        return "".join(out)

    def _harvest_signature(self, doc):
        """Lift the signature block off the END of the last opinion into
        ``doc.signature``: the '/s/' conformed signature (or the underscore
        signature rule), the printed name, and the signer's title line.
        Fires only when the very last body block is a judge-title line, so
        ordinary prose endings are never touched."""
        if not doc.opinions:
            return
        op = doc.opinions[-1]
        blocks = op.blocks
        if not blocks:
            return

        def is_title(t):
            low = t.strip().rstrip(".").lower()
            return any(
                low == jt.rstrip(".") or low.endswith(" " + jt.rstrip("."))
                for jt in _JUDGE_TITLES
            )

        # An image-signed order: 'Signed: <date>' / 'ENTER: <date>' followed
        # by a signature GRAPHIC (the name + title live inside the image, so
        # there is no title text line to anchor on). The date line and the
        # image together are the signature block. A trailing bare page
        # number after the image is ignored when anchoring.
        end = len(blocks)
        while end > 0 and blocks[end - 1].kind == "p" and (
            self._untag(blocks[end - 1].text).strip().isdigit()
        ):
            end -= 1
        if end >= 2 and blocks[end - 1].kind == "image":
            prev = self._untag(blocks[end - 2].text).strip().lower()
            # a date stamp ('Signed:' / 'ENTER:' / 'Dated:') belongs WITH
            # the signature; decretal prose ('IT IS SO ORDERED.') stays in
            # the body — only the image moves.
            if any(
                prev.startswith(sk)
                for sk in ("signed", "dated", "date", "enter", "entered")
            ):
                doc.signature = [
                    str(blocks[end - 2].text),
                    {"__image__": True, **(blocks[end - 1].payload or {})},
                ]
                op.blocks = blocks[: end - 2] + blocks[end:]
            elif any(prev.startswith(sk) for sk in _SIG_SKIP):
                doc.signature = [
                    {"__image__": True, **(blocks[end - 1].payload or {})}
                ]
                op.blocks = blocks[: end - 1] + blocks[end:]
            return
        if not is_title(self._untag(blocks[-1].text)):
            return
        taken = 1
        for b in reversed(blocks[:-1]):
            if taken >= 5:
                break
            if b.kind == "image":
                taken += 1
                break  # the signature image tops the block
            t = self._untag(b.text).strip()
            low = t.lower()
            if low.startswith("/s/") or low.startswith("s/"):
                taken += 1
                break  # the conformed signature tops the block
            if len(t) >= 4 and set(t) <= {"_"}:
                taken += 1
                break  # the drawn/typed signature rule tops the block
            if any(low.startswith(sk) for sk in _SIG_DATE):
                taken += 1
                continue  # a date stamp inside the block; image/'/s/' above it
            if (
                t
                and len(t) <= 48
                and not t.endswith(".")
                and not any(low.startswith(sk) for sk in _SIG_SKIP)
                and not is_title(t)
            ):
                taken += 1  # the printed name between rule/'/s/' and title
                continue
            break
        if taken < 2:
            return
        doc.signature = [
            {"__image__": True, **(b.payload or {})}
            if b.kind == "image"
            else str(b.text)
            for b in blocks[-taken:]
        ]
        op.blocks = blocks[:-taken]

    # ----------------------------------------- pleading-paper line numbers
    def page_lines(self, page):
        """On pleading paper (California etc.), a left gutter carries the
        sequential line numbers 1-28, set off from the body by a vertical margin
        rule; pdfplumber merges each number onto its line ('1 However ...'). When
        that rule is present, drop the chars left of it so the body reads cleanly
        without the line numbers. Gated on the rule (or, when no rule is drawn,
        on the number column itself), so ordinary CM/ECF filings are untouched."""
        gx = self._pleading_gutter_x(page)
        if gx is None:
            gx = self._pleading_gutter_by_numbers(page)
        if gx is not None:
            page = page.filter(lambda c: c["x0"] >= gx - 1)
        return super().page_lines(page)

    @staticmethod
    def _pleading_gutter_by_numbers(page):
        """Gutter right-edge x inferred from the line-number column when NO
        margin rule is drawn: a far-left stack of pure integers running roughly
        1, 2, 3, … down the page. Returns the numbers' right edge (chars left of
        it are the gutter), or None. Requires a long, mostly-sequential run so an
        ordinary filing's stray leading digits never trip it."""
        nums = [
            (int(w["text"]), w["x1"], w["top"])
            for w in page.extract_words()
            if w["text"].isdigit()
            and int(w["text"]) <= 40
            and w["x0"] < 90
            and (w["x1"] - w["x0"]) < 16
        ]
        if len(nums) < 8:
            return None
        nums.sort(key=lambda n: n[2])  # top-to-bottom
        vals = [n[0] for n in nums]
        runs = sum(1 for a, b in zip(vals, vals[1:]) if b == a + 1)
        if runs < 6:
            return None
        return max(n[1] for n in nums)

    @staticmethod
    def _pleading_gutter_x(page):
        """X of the pleading margin rule that separates the line-number gutter
        from the body, or None. A tall, thin vertical rule in the left gutter
        zone (x≈50-130) spanning most of the page."""
        tall = page.height * 0.6
        xs = [
            r["x0"]
            for r in page.rects
            if (r["x1"] - r["x0"]) < 3
            and (r["bottom"] - r["top"]) > tall
            and 45 < r["x0"] < 130
        ]
        xs += [
            l["x0"]
            for l in page.lines
            if abs(l["x1"] - l["x0"]) < 3
            and abs(l["bottom"] - l["top"]) > tall
            and 45 < l["x0"] < 130
        ]
        return max(xs) if xs else None

    def find_footnote_separator(self, page):
        """The page-1 caption's closing shelf — a left rule meeting the mid
        vertical (Old Faithful) — sits past the half-page cutoff on long
        captions and the generic scan takes it for the footnote rule, which
        shoves the ruling's opening body into the footnote flow (seen on
        waed, wawd; wash has the state-court version). The page-1 caption
        fingerprint knows the caption's bottom; a 'separator' at that height
        is the shelf, so rescan strictly below it."""
        sep = super().find_footnote_separator(page)
        if sep is None:
            # Pleading paper offsets the body text column — and with it the
            # footnote rule — to the right of the page margin by the
            # line-number gutter. The base scan anchors at the nominal margin
            # and so misses the rule; re-scan anchored at the gutter (the
            # rule sits a few points right of the gutter, at the text column).
            gx = self._pleading_gutter_x(page)
            if gx is not None:
                sep = self._gutter_footnote_rule(page, gx)
        if sep is None or page.page_number != 1:
            return sep
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        cap_bottom = None
        if sig:
            rb = sig.get("rail_band")
            if rb:
                cap_bottom = rb[1]
            elif sig.get("vmid") and sig.get("band"):
                cap_bottom = sig["band"][1]
        if cap_bottom is None or sep > cap_bottom + 12:
            return sep
        gx = self._pleading_gutter_x(page)
        x0_hi = (gx + 30) if gx is not None else (self.body_baseline_x0 + 4)
        x0_lo = (gx - 2) if gx is not None else 0
        cands = [
            r["top"]
            for r in page.rects
            if r["bottom"] - r["top"] < 2.5
            and (r["x1"] - r["x0"]) >= 90
            and x0_lo <= r["x0"] <= x0_hi
            and r["top"] > cap_bottom + 12
        ]
        return min(cands) if cands else None

    def _gutter_footnote_rule(self, page, gx):
        """A footnote separator on pleading paper: a thin, left-anchored
        horizontal rule low on the page whose left edge sits at the body text
        column (a few points right of the line-number gutter). A page-1
        caption's closing shelf at the caption-band bottom is excluded."""
        cutoff = page.height * 0.55
        cap_bottom = None
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        if page.page_number == 1 and sig:
            rb = sig.get("rail_band")
            if rb:
                cap_bottom = rb[1]
            elif sig.get("vmid") and sig.get("band"):
                cap_bottom = sig["band"][1]
        cands = []
        for r in page.rects:
            if not (
                r["height"] < 2
                and (r["x1"] - r["x0"]) >= 90
                and gx - 2 <= r["x0"] <= gx + 30
                and r["top"] > cutoff
            ):
                continue
            if cap_bottom is not None and r["top"] <= cap_bottom + 12:
                continue
            cands.append(r["top"])
        return min(cands) if cands else None

    def extract_page_images(self, page):
        """Drop pleading-paper rule furniture drawn as images — the tall, narrow
        left/right margin rules, the caption-box verticals, and the thin line-
        number ticks all render as embedded images on some California filings. A
        rule is thin in one dimension; a real figure (an exhibit, a signature
        graphic) is substantial in both, so keep only images thicker than the
        rule threshold in their smaller dimension."""
        return [
            im
            for im in super().extract_page_images(page)
            if min(im["width"], im["height"]) > 10
        ]

    def extract_page_tables(self, page):
        """Completeness-first: don't lift tables into separate structures.
        District rulings embed fee schedules / claim charts / exhibits whose
        rows would otherwise be excluded from the body (their bbox is skipped)
        and lost. Leaving them as body lines keeps every row in the output."""
        return []

    # NOTE: removal of page furniture (running footers, bates) and footnote /
    # opinion-start tuning are intentionally NOT in this shared base — they are
    # per-court, so tuning one district can't regress another. A court that
    # needs them defines them in its own file (see ``akd.py`` for the model).

    # ----------------------------------------------- headmatter facsimile
    # District captions put parties on the left and case numbers on the right,
    # usually separated by a stacked column of punctuation (')' / ']' / ':') or
    # just whitespace. Render the headmatter as a whitespace-preserved facsimile
    # — each line's runs placed at their real x — so those columns line up.
    # Splitting is by x-gap, so any divider glyph works; every glyph is kept
    # (each row is one positioned string), so coverage is unaffected. Not every
    # district has a column caption, but where it does this is a clear win and
    # it is harmless (a single-column caption just renders at its x) elsewhere.
    # Styled headmatter is the default (matching the state-court families):
    # centered banner rows with bold/relative sizes and the whitespace-
    # separated caption columns folded into a two-column '__caption__' block
    # (parties left, docket/doc-title right). A court can opt back out to
    # the monospace grid with ``styled_headmatter = False``.
    styled_headmatter = True

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        out = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        if self.styled_headmatter:
            rows = self._styled_caption_rows(headmatter_segs)
            if rows:
                out["summary"] = rows
            return out
        items = []
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                continue
            for line in seg:
                if not self.line_plain_text(line).strip():
                    continue
                top = round(line.get("top", 0), 1)
                for x0, text in self._caption_runs(line):
                    items.append((top, x0, text))
        rows = self._layout_rows(items)
        if rows:
            out["summary"] = rows
        return out

    def _styled_caption_rows(self, headmatter_segs) -> list:
        """Styled headmatter rows. Runs are regrouped into VISUAL rows by
        (page, top) — page-line building sometimes splits a caption row into
        separate line objects — then a row with material on both sides of
        mid-page is a caption row (left = party, right = docket/doc-title),
        and adjacent narrow one-sided rows join their open side ('vs.',
        wrapped party names, a right-column doc-title wrap). Everything else
        is a styled row — centered when midpoint-centered, with inline
        bold/italic and relative size; underscore runs are dividers."""
        from collections import Counter

        pw = getattr(self, "_page1_width", 612.0) or 612.0
        mid = pw * 0.45
        wide = (pw - 2 * self.body_baseline_x0) * 0.7

        items = []  # (page, top, run-chars)
        for seg in headmatter_segs:
            if self.skip_headmatter_segment(seg):
                continue
            for line in seg:
                if not self.line_plain_text(line).strip():
                    continue
                chars = line.get("chars") or []
                pno = (chars[0].get("page_number") if chars else None) or 1
                for run in self._caption_char_runs(line):
                    items.append((pno, round(line["top"], 1), run))
        if not items:
            return []
        # Pleading paper offsets the text column right of the gutter, so
        # "centered" means centered on the CONTENT column, not the page.
        col_x0 = min(r[0]["x0"] for _p, _t, r in items)
        col_x1 = max(r[-1]["x1"] for _p, _t, r in items)
        col_mid = (col_x0 + col_x1) / 2
        col_w = col_x1 - col_x0
        items.sort(key=lambda r: (r[0], r[1], r[2][0]["x0"]))
        rows, cur = [], None
        for pno, top, run in items:
            if cur is not None and (pno != cur[0] or abs(top - cur[1]) > 2):
                rows.append(cur)
                cur = None
            if cur is None:
                cur = (pno, top, [])
            cur[2].append(run)
        rows.append(cur)

        sizes = [
            round(c.get("size", 0))
            for _p, _t, runs in rows
            for r in runs
            for c in r
            if (c.get("text") or "").strip()
        ]
        base = float(Counter(sizes).most_common(1)[0][0]) if sizes else 12.0

        def run_text(r):
            return self.line_plain_text({"chars": r}).strip()

        # Drawn caption-box geometry (see /captions), measured BEFORE the
        # column test: a drawn mid vertical makes every row in its y-band a
        # caption row split at the rule — a row whose runs all sit on one
        # side (a party block with no docket opposite, the lone 'Case No.'
        # line) still belongs to its column. Without the rule, two-column
        # means material on both sides of mid-page.
        box = getattr(self, "_hm_caption_box", None) or {}
        drawn_v = box.get("vx")
        verts = [v for v in box.get("verts", []) or [] if v[2] - v[1] >= 40]
        vxs = sorted({v[0] for v in verts})
        fp_sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        if fp_sig:
            # The fingerprint's verticals are gutter-filtered, so pleading
            # margin rails at the page edges can't masquerade as box sides.
            boxes = bool(
                fp_sig["vleft"] and fp_sig["vmid"] and fp_sig["vright"]
            )
        else:
            boxes = (
                len(vxs) >= 3
                and vxs[0] < pw * 0.25
                and vxs[-1] > pw * 0.7
                and any(pw * 0.4 < x < pw * 0.75 for x in vxs)
            )
        box_band = (
            (min(v[1] for v in verts), max(v[2] for v in verts)) if verts else None
        )
        v_band = None
        if drawn_v is not None:
            spans = [v for v in verts if abs(v[0] - drawn_v) < 2]
            if spans:
                v_band = (
                    min(v[1] for v in spans) - 6,
                    max(v[2] for v in spans) + 6,
                )

        two_col, row_split = [], []
        for _p, _t, runs in rows:
            in_band = (
                v_band is not None and _p == 1 and v_band[0] <= _t <= v_band[1]
            )
            split = drawn_v if (in_band and drawn_v is not None) else mid
            lefts = [r for r in runs if r[0]["x0"] < split]
            rights = [r for r in runs if r[0]["x0"] >= split]
            two_col.append((bool(lefts) and bool(rights)) or in_band)
            row_split.append(split)

        def near_caption(i) -> bool:
            lo, hi = max(0, i - 6), min(len(rows), i + 7)
            return any(two_col[j] for j in range(lo, hi))

        # Vertical rhythm: a row gap well past the page's median line pitch
        # becomes a blank row (median-adaptive, so double-spaced pleading
        # paper doesn't gap between every line).
        deltas = sorted(
            b[1] - a[1]
            for a, b in zip(rows, rows[1:])
            if a[0] == b[0] and b[1] > a[1]
        )
        med = deltas[len(deltas) // 2] if deltas else 14.0
        gap_min = med * 1.6

        # The Flush-Right Status draws nothing — its structure is per-ROW
        # alignment (party at the left margin, status label pinned at the
        # right margin, docket floating between them on the 'v.' line), so
        # stacked columns would unpair the rows. Render it as three-zone
        # rows instead of a caption block.
        fp = getattr(self, "_caption_fp", (None, None, None))
        if fp and fp[1] == "status-flush":
            return self._flush_right_rows(rows, gap_min)

        # 'Old Faithful': one mid-page vertical + a half-rule closing into
        # it at the corner. 'The Double Box': tall verticals at BOTH content
        # edges and the middle, closed top and bottom. An hrule with a text
        # line directly above it is an UNDERLINE, not a rule, and never
        # becomes a divider.
        def _is_underline(h):
            htop, hx0, hx1 = h
            for _p2, t2, runs2 in rows:
                if 0 < htop - t2 < 16:
                    rx0 = min(r[0]["x0"] for r in runs2)
                    rx1 = max(r[-1]["x1"] for r in runs2)
                    ov = min(hx1, rx1) - max(hx0, rx0)
                    if ov > 0.7 * (hx1 - hx0):
                        return True
            return False

        closing, pending_hrules, shelf_ys = False, [], []
        for h in box.get("hrules", []) or []:
            if _is_underline(h):
                continue
            if boxes and box_band and (
                abs(h[0] - box_band[0]) < 6 or abs(h[0] - box_band[1]) < 6
            ):
                continue  # the box's own top/bottom edges
            if drawn_v is not None and abs(h[2] - drawn_v) < 8:
                closing = True  # the half-rule meeting the vertical
                shelf_ys.append(h[0])
            else:
                pending_hrules.append(h[0])
        pending_hrules.sort()
        # An INTERIOR shelf (a closing rule with caption rows still below it
        # — consolidated cases stack two captions on one vertical) splits the
        # caption into stacked blocks, one per case.
        shelf_ys.sort()
        if shelf_ys and v_band is not None and shelf_ys[-1] >= v_band[1] - 12:
            shelf_ys.pop()  # the bottom close isn't an interior shelf

        out, left, right = [], [], []
        state = {"open": False, "rail": None, "rail_rows": 0}
        fp_rail = ((getattr(self, "_caption_fp", None) or ({},))[0]
                   or {}).get("rail")

        def strip_rail(run):
            """Drop a leading/trailing rail glyph that joined a text run
            (') MEMORANDUM') when it matches the caption's known rail."""
            railg = state["rail"] or fp_rail
            chars = list(run)
            while chars and not (chars[0].get("text") or "").strip():
                chars.pop(0)
            if railg and chars and (chars[0].get("text") or "") == railg:
                state["rail"] = railg
                chars.pop(0)
                while chars and not (chars[0].get("text") or "").strip():
                    chars.pop(0)
            while chars and not (chars[-1].get("text") or "").strip():
                chars.pop()
            if railg and chars and (chars[-1].get("text") or "") == railg:
                state["rail"] = railg
                chars.pop()
                while chars and not (chars[-1].get("text") or "").strip():
                    chars.pop()
            return chars

        def push(side, html, x0, top):
            """Append a cell line; a vertical gap past the caption's line
            pitch becomes a blank spacer row (double-spaced captions keep
            their air)."""
            if (
                side
                and isinstance(side[-1], dict)
                and top - side[-1]["top"] > gap_min
            ):
                side.append("")
            side.append({"h": html, "x0": round(x0, 1), "top": top})

        def cellify_pair(l_side, r_side):
            """Final PARALLEL cell arrays: the two columns merged onto one
            row grid by baseline, so a right cell renders beside the left
            row it shares on the page ('v. | Civ. Action No. …'), never
            packed to the top of its column. Indents are relative to each
            cell's own left edge, so 'Plaintiff,' sits indented under the
            party name exactly as printed; a vertical gap past the caption's
            line pitch keeps its blank spacer row on both sides."""
            ents = [("L", e) for e in l_side if isinstance(e, dict)] + [
                ("R", e) for e in r_side if isinstance(e, dict)
            ]
            ents.sort(key=lambda t: t[1]["top"])
            rows = []  # [top, left-cell, right-cell]
            for side, e in ents:
                if (
                    rows
                    and abs(e["top"] - rows[-1][0]) <= 4
                    and (rows[-1][1] if side == "L" else rows[-1][2]) is None
                ):
                    if side == "L":
                        rows[-1][1] = e
                    else:
                        rows[-1][2] = e
                else:
                    rows.append(
                        [e["top"],
                         e if side == "L" else None,
                         e if side == "R" else None]
                    )
            minx = {}
            for key, cells in (("L", [r[1] for r in rows]),
                               ("R", [r[2] for r in rows])):
                xs = [c["x0"] for c in cells if c]
                minx[key] = min(xs) if xs else 0.0

            def cell(e, key):
                if not e:
                    return ""
                return {"h": e["h"], "ind": round(e["x0"] - minx[key], 1)}

            out_l, out_r, prev = [], [], None
            for top, lc, rc in rows:
                if prev is not None and top - prev > gap_min:
                    out_l.append("")
                    out_r.append("")
                prev = top
                out_l.append(cell(lc, "L"))
                out_r.append(cell(rc, "R"))
            return out_l, out_r

        def flush():
            if left or right:
                rail = state["rail"]
                if rail is None and drawn_v is not None and not boxes:
                    rail = "|"  # a DRAWN vertical rule divides the columns
                cells_l, cells_r = cellify_pair(left, right)
                cap = {
                    "__caption__": True,
                    "left": cells_l,
                    "right": cells_r,
                    "rail": rail,
                }
                # the glyph rail is drawn once per SOURCE row that bore it —
                # render exactly that many, never one-per-cell (which would
                # invent glyphs for banner/blank rows). 0 → fall back at render.
                if state.get("rail_rows"):
                    cap["rail_rows"] = state["rail_rows"]
                state["rail_rows"] = 0
                fp = getattr(self, "_caption_fp", (None, None, None))
                if fp and fp[1] in (
                    "double-box", "old-faithful", "upside-down-t", "i-beam",
                    "backwards-c", "twin-rail", "x-capped-box", "status-flush",
                ):
                    cap["shape"] = fp[1]
                if boxes:
                    cap["boxes"] = True  # The Double Box
                elif closing and rail == "|":
                    cap["corner"] = True  # Old Faithful ┘ close
                out.append(cap)
                left.clear()
                right.clear()
            state["open"] = False
            state["rail"] = None

        prev_row = None
        for i, (_pno, _top, runs) in enumerate(rows):
            # A drawn horizontal rule above this row becomes a FULL-WIDTH
            # rule row at its position.
            while pending_hrules and _pno == 1 and _top > pending_hrules[0]:
                flush()
                if not out or out[-1] != "__RULE__":
                    out.append("__RULE__")
                pending_hrules.pop(0)
            # Passing an interior shelf closes the current stacked caption.
            while shelf_ys and _pno == 1 and _top > shelf_ys[0] + 2:
                flush()
                shelf_ys.pop(0)
            if (
                prev_row is not None
                and not (left or right)
                and (prev_row[0] != _pno or (_top - prev_row[1]) > gap_min)
                and out
                and out[-1] != ""
            ):
                out.append("")
            prev_row = (_pno, _top)
            texts = [run_text(r) for r in runs]
            joined = " ".join(t for t in texts if t)
            x0 = min(r[0]["x0"] for r in runs)
            x1 = max(r[-1]["x1"] for r in runs)
            # one rail glyph is drawn per source row that contains it — count
            # those rows so the renderer draws exactly that many (not one per
            # cell, which would invent glyphs for the banner / blank rows).
            _railg = state["rail"] or fp_rail
            if _railg and _railg in joined:
                state["rail_rows"] += 1
            if len(joined) >= 4 and all(c in "_-—–=* " for c in joined):
                flush()
                out.append("__DIVIDER__")
                continue
            if two_col[i]:
                # A run that is nothing but rail glyphs IS the column divider
                # (')' / '§' / ':' stacked down the caption) — record it for
                # the renderer, keep it out of the cells.
                cell_runs = []
                for r in runs:
                    t = run_text(r)
                    if t and all(c in ")]§|(: " for c in t):
                        state["rail"] = t[:1]
                        continue
                    cell_runs.append(r)

                for side, keep in (
                    (left, lambda r: r[0]["x0"] < row_split[i]),
                    (right, lambda r: r[0]["x0"] >= row_split[i]),
                ):
                    sruns = [strip_rail(r) for r in cell_runs if keep(r)]
                    sruns = [r for r in sruns if r]
                    if not sruns:
                        continue
                    html = " ".join(
                        self.line_inline_text({"chars": r}) for r in sruns
                    ).strip()
                    if html:
                        push(side, html, sruns[0][0]["x0"], _top)
                state["open"] = True
                continue
            # A glyph-only row (a stray ',' from interleaved caption lines)
            # never stands alone — it joins the open caption side or the
            # previous row. Rail glyphs ARE the divider, not cell text.
            if joined and not any(c.isalnum() for c in joined):
                if all(c in ")]§|(: " for c in joined):
                    state["rail"] = joined.strip()[:1]
                    continue
                if left or right:
                    side = left if x0 < row_split[i] else right
                    if side and isinstance(side[-1], dict):
                        side[-1]["h"] = (side[-1]["h"] + " " + joined).strip()
                    else:
                        push(side, joined, x0, _top)
                elif out and isinstance(out[-1], dict) and out[-1].get("__hm__"):
                    out[-1]["html"] += " " + joined
                continue
            # ±40 / 0.8: pleading-paper banners center sloppily and run wide
            # within the column; caption party rows sit 60pt+ off-center.
            # A caption role row ('Plaintiffs,' / 'Defendant.') belongs to
            # the open caption even when it sits near the column center.
            role_words = {
                "plaintiff", "plaintiffs", "defendant", "defendants",
                "petitioner", "petitioners", "respondent", "respondents",
                "appellant", "appellants", "appellee", "appellees",
            }
            if (state["open"] or near_caption(i)) and joined.rstrip(
                ".,"
            ).lower() in role_words:
                push(
                    left,
                    self.line_inline_text(
                        {"chars": [c for r in runs for c in r]}
                    ),
                    x0,
                    _top,
                )
                state["open"] = True
                continue
            # Centered on the column OR on the PAGE — a court banner ('IN THE
            # UNITED STATES DISTRICT COURT') is page-centered but the column
            # midpoint is skewed by the banner's own width, so test both; this
            # keeps the banner out of the rail caption (where it would inflate
            # the rail-glyph count with lines the PDF never drew a rail on).
            cx = (x0 + x1) / 2
            centered = (
                abs(cx - col_mid) <= 40 and (x1 - x0) < col_w * 0.8
            ) or (
                # page-centered banner: width capped against the PAGE, not the
                # column — a narrow caption column would otherwise reject the
                # wider of two banner lines and fold it into the caption
                abs(cx - pw / 2) <= 30 and (x1 - x0) < pw * 0.65
            )
            narrow = (x1 - x0) <= wide
            if (state["open"] or near_caption(i)) and narrow and not centered:
                sruns = [strip_rail(r) for r in runs]
                sruns = [r for r in sruns if r]
                if sruns:
                    push(
                        left if x0 < row_split[i] else right,
                        " ".join(
                            self.line_inline_text({"chars": r})
                            for r in sruns
                        ).strip(),
                        sruns[0][0]["x0"],
                        _top,
                    )
                state["open"] = True
                continue
            flush()
            all_chars = [c for r in runs for c in r]
            printable = [
                round(c.get("size", 0))
                for c in all_chars
                if (c.get("text") or "").strip()
            ]
            size = float(Counter(printable).most_common(1)[0][0]) if printable else base
            out.append(
                {
                    "__hm__": True,
                    "html": self.line_inline_text({"chars": all_chars}),
                    "rel": round(size / base, 3) if base else 1.0,
                    "align": "C" if centered else "L",
                }
            )
        flush()
        return out


    def _flush_right_rows(self, rows, gap_min) -> list:
        """Three-zone rows for The Flush-Right Status: each visual row keeps
        its own left / center / right runs paired (PLAINTIFF stays on the
        party's row, the docket floats centered on the 'v.' line). Inline
        bold/italic is preserved per run. One-zone rows stay ordinary styled
        rows so banners render exactly like every other court's."""
        xs = [r for _p, _t, runs in rows for r in runs]
        lmargin = min(r[0]["x0"] for r in xs)
        rmargin = max(r[-1]["x1"] for r in xs)
        out, prev = [], None
        for pno, top, runs in rows:
            if (
                prev is not None
                and (pno != prev[0] or top - prev[1] > gap_min)
                and out
                and out[-1] != ""
            ):
                out.append("")
            prev = (pno, top)
            cells = {"l": [], "c": [], "r": []}
            for r in runs:
                if r[-1]["x1"] > rmargin - 15 and r[0]["x0"] > lmargin + 30:
                    k = "r"
                elif r[0]["x0"] < lmargin + 30:
                    k = "l"
                else:
                    k = "c"
                cells[k].append(self.line_inline_text({"chars": r}))
            filled = [k for k in ("l", "c", "r") if cells[k]]
            if len(filled) == 1:
                k = filled[0]
                out.append({
                    "__hm__": True,
                    "html": " ".join(cells[k]),
                    "rel": 1.0,
                    "align": {"l": "L", "c": "C", "r": "R"}[k],
                })
            else:
                out.append({
                    "__hmrow__": True,
                    "l": " ".join(cells["l"]),
                    "c": " ".join(cells["c"]),
                    "r": " ".join(cells["r"]),
                })
        return out

    def _caption_char_runs(self, line) -> list:
        """Char runs split at the wide x-gaps that separate caption columns.
        Typewriter-set captions fill the column gap with literal space
        glyphs instead of leaving it empty, so spaces are buffered and the
        gap is measured between printable neighbors — a wide run of spaces
        splits just like a wide empty gap (the padding spaces are dropped)."""
        chars = line.get("chars") or []
        runs, cur, spaces = [], [], []
        for c in chars:
            if not (c.get("text") or "").strip():
                if cur:
                    spaces.append(c)
                continue
            if cur and c["x0"] - cur[-1]["x1"] > _CAPTION_GAP:
                runs.append(cur)
                cur = [c]
            else:
                cur.extend(spaces)
                cur.append(c)
            spaces = []
        if cur:
            runs.append(cur)
        return runs

    def _caption_runs(self, line):
        """(x0, text) runs at the wide x-gaps that separate caption columns,
        leaving ordinary word spacing within a run intact."""
        out = []
        for run in self._caption_char_runs(line):
            text = self.line_plain_text({"chars": run}).strip()
            if text:
                out.append((round(run[0]["x0"], 1), text))
        return out

    @staticmethod
    def _layout_rows(items):
        """Place runs that share a row (same top) on one line, positioned by x0
        in a monospace grid, so vertical columns (the divider) line up."""
        if not items:
            return []
        items.sort(key=lambda r: (r[0], r[1]))
        rows, segs, cur_top = [], [], None

        def emit(parts):
            line = ""
            for x0, text in sorted(parts, key=lambda p: p[0]):
                col = max(
                    len(line) + (1 if line else 0),
                    int((x0 - _CAPTION_LEFT) / _CAPTION_CHAR_W),
                )
                line += " " * (col - len(line)) + text
            return line

        for top, x0, text in items:
            if cur_top is not None and abs(top - cur_top) > 3:
                rows.append(emit(segs))
                segs = []
            segs.append((x0, text))
            cur_top = top
        if segs:
            rows.append(emit(segs))
        return rows

    # ---------------------------------------------------------------- author
    def _signature_author(self, all_segments):
        """The judge named just above a 'United States District Judge' (etc.)
        title line — scanning from the end, where the signature block sits."""
        lines = [
            self.line_plain_text(l).strip() for _p, seg, _k in all_segments for l in seg
        ]
        lines = [t for t in lines if t]
        for i in range(len(lines) - 1, -1, -1):
            low = lines[i].lower().strip().rstrip(".")
            # A signature TITLE line is short ('UNITED STATES DISTRICT
            # JUDGE', 'Thomas S. Kleeh, Chief Judge'); a body sentence that
            # merely ENDS in a title phrase ('…consent to jurisdiction of
            # the Magistrate Judge') is long — cap the endswith match so
            # decree text above it ('DISMISSED WITH PREJUDICE.') can't be
            # taken for the judge's name.
            title = next(
                (
                    t
                    for t in _JUDGE_TITLES
                    if low == t.rstrip(".")
                    or (
                        len(lines[i]) <= 52
                        and low.endswith(" " + t.rstrip("."))
                    )
                ),
                None,
            )
            if title is None:
                continue
            # name + title on ONE line ('THOMAS S. KLEEH, CHIEF JUDGE'):
            # the part before the title is the name — take it directly
            # rather than walking back into unrelated text above.
            head = lines[i][: len(lines[i]) - len(title.rstrip("."))]
            head = head.rstrip(" .").rstrip(",").strip()
            if (
                head
                and _looks_like_name(head)
                and not any(
                    w in head.lower().split()
                    for w in ("court", "courts", "division", "states", "district")
                )
            ):
                return _strip_sig_prefix(head).rstrip(",")
            # Walk back over rules / 'SO ORDERED' / 'Dated:' to the name line.
            for j in range(i - 1, max(-1, i - 5), -1):
                cand = lines[j]
                clow = cand.lower()
                if _is_rule(cand) or any(clow.startswith(s) for s in _SIG_SKIP):
                    if clow.startswith(("s/", "/s/")) and _looks_like_name(cand):
                        return _strip_sig_prefix(cand).rstrip(",")
                    continue
                if _looks_like_name(cand):
                    return _strip_sig_prefix(cand).rstrip(",")
            # Title on the same line as the name ('Dated: ... District Judge')?
        return None

    def _present_author(self, all_segments):
        """Minute-order author: 'Present: The Honorable NAME, ... JUDGE'."""
        for _p, seg, _k in all_segments:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                key = "the honorable "
                if "present:" in low and key in low and "judge" in low:
                    after = t[low.find(key) + len(key) :]
                    name = after.split(",")[0].strip()
                    if name:
                        return name
        return None

    # A surname + abbreviated/spelled-out judge title that opens the opinion
    # ('Rufe, J.' / 'Smith, Chief Judge.').
    _BYLINE_TITLES = (
        "Chief Judge",
        "Senior Judge",
        "District Judge",
        "Magistrate Judge",
        "Circuit Judge",
        "Judge",
        "C.J.",
        "J.",
        "U.S.D.J.",
        "U.S.M.J.",
    )

    _ABBREV_TITLES = ("J.", "C.J.", "P.J.", "U.S.D.J.", "U.S.M.J.")

    def _byline_author(self, all_segments, limit=12):
        """A 'NAME, <title>' byline near the top (e.g. Pennsylvania-E 'Rufe, J.
        February 27, 2026'). Scans only the opening segments so a mid-opinion
        citation can't masquerade as the author."""
        for _p, seg, _k in all_segments[:limit]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                if "," not in t or len(t) > 60:
                    continue
                name, rest = t.split(",", 1)
                name, rest = name.strip(), rest.strip()
                toks = name.replace("-", " ").split()
                if not (
                    1 <= len(toks) <= 3
                    and all(w[:1].isupper() and w.rstrip(".").isalpha() for w in toks)
                ):
                    continue
                first = rest.split()[0] if rest.split() else ""
                # 'Rufe, J.' / 'Rufe, J. <date>' or a spelled-out judge title.
                if (
                    first in self._ABBREV_TITLES
                    or rest.rstrip(".") in self._BYLINE_TITLES
                    or any(
                        rest.startswith(tt)
                        for tt in self._BYLINE_TITLES
                        if tt[0].isalpha() and len(tt) > 3
                    )
                ):
                    return name
        return None

    def _caption_judge(self, all_segments, limit=14):
        """A caption author tag: 'Judge NAME' / 'Hon. NAME' / 'Honorable NAME'
        sitting in the caption column."""
        tags = ("judge ", "hon. ", "honorable ")
        for _p, seg, _k in all_segments[:limit]:
            for l in seg:
                t = self.line_plain_text(l).strip()
                low = t.lower()
                for tag in tags:
                    if low.startswith(tag):
                        name = t[len(tag) :].split(",")[0].strip()
                        if _looks_like_name(name):
                            return name
        return None

    # ------------------------------------------------------------- opinion start
    def _is_heading(self, line) -> bool:
        """True if ``line`` is a document-type heading — an exact phrase
        ('MEMORANDUM OPINION AND ORDER' / 'ORDER' / ...; letter-spaced 'O RDER'
        matches with spaces removed), OR a compound ALL-CAPS title that opens
        with a doc-type word ('ORDER ADOPTING MEMORANDUM AND RECOMMENDATION',
        'ORDER GRANTING DEFENDANT'S MOTION …'). The compound title is the
        opinion's start, not the last line of the headmatter."""
        plain = self.line_plain_text(line).strip()
        low = plain.rstrip(".:").lower()
        if low in _HEADINGS:
            return True
        squeezed = low.replace(" ", "")
        if squeezed in {h.replace(" ", "") for h in _HEADINGS}:
            return True
        if plain and plain == plain.upper() and len(plain) < 90:
            head = low.split()
            if head and head[0].strip(",") in _HEADING_STARTS:
                return True
        return False

    def find_authors(self, all_segments) -> list:
        # Author, in order of reliability: signature block, minute-order
        # 'Present:' line, a 'NAME, J.' opening byline, a caption 'Judge NAME'.
        self._district_author = (
            self._signature_author(all_segments)
            or self._present_author(all_segments)
            or self._byline_author(all_segments)
            or self._caption_judge(all_segments)
        )
        # Opinion start: the document-type heading; else the first body segment.
        # (Courts whose ruling opens differently — e.g. an ALL-CAPS heading after
        # a ruled caption box, or a title set INSIDE the caption column with the
        # body opening 'THIS MATTER is before…' — override this in their own
        # file; see akd.py and ncwd.py.)
        start = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._is_heading(seg[0]):
                start = i
                break
        if start is None:
            for i, (_p, seg, kind) in enumerate(all_segments):
                if kind == "body":
                    start = i
                    break
        # Last resorts — a district doc always has a ruling, so an empty
        # result is always wrong: (1) a compound ALL-CAPS heading the exact
        # phrase table doesn't list ('ORDER DENYING PLAINTIFF'S MOTION TO
        # ALTER OR AMEND JUDGMENT'); (2) the first multi-line prose segment
        # when the court's line pitch classifies body as blockquote.
        if start is None:
            for i, (_p, seg, _k) in enumerate(all_segments):
                if seg and len(seg) <= 2:
                    t = self.line_plain_text(seg[0]).strip()
                    if (
                        t
                        and t == t.upper()
                        and len(t) < 90
                        and any(
                            t.startswith(w)
                            for w in (
                                "ORDER", "MEMORANDUM", "OPINION", "FINDINGS",
                                "JUDGMENT", "DECISION", "REPORT AND",
                            )
                        )
                    ):
                        start = i
                        break
        if start is None:
            for i, (_p, seg, kind) in enumerate(all_segments):
                if kind == "blockquote" and len(seg) >= 2:
                    start = i
                    break
        if start is None:
            return []
        # The opinion can never start ABOVE the page-1 caption: when the
        # fingerprint drew a caption band (mid vertical or glyph rail) and
        # the chosen start sits inside/above it (a double-spaced caption
        # classifying as 'body' pulls the fallback to the banner), advance
        # to the first segment below the band.
        sig = (getattr(self, "_caption_fp", None) or (None,))[0]
        cap_bottom = None
        if sig:
            rb = sig.get("rail_band")
            if rb:
                cap_bottom = rb[1]
            elif sig.get("vmid") and sig.get("band"):
                cap_bottom = sig["band"][1]
        if cap_bottom is not None:
            pno0, seg0, _k0 = all_segments[start]
            if pno0 == 1 and seg0 and seg0[0].get("top", 0) < cap_bottom - 4:
                # The first body line often sits flush at the band bottom
                # (the divider rule ends exactly where the prose begins), so
                # land on a segment AT the band bottom — a true caption role
                # row that slips through is swept up by the role-row scan below.
                for i, (pno, seg, _k) in enumerate(all_segments):
                    if pno == 1 and seg and seg[0].get("top", 0) > cap_bottom - 6:
                        start = i
                        break
                    if pno > 1 and seg:
                        start = i
                        break
        # A doc-title heading can sit INSIDE the caption (in the right
        # column, above 'Defendants.'); the body then starts after the
        # caption's last party-role row. The scan stops at the first wide
        # single-run line (real body text), so a body sentence that happens
        # to end '... Defendants.' can never trigger it.
        roles = {
            "plaintiff", "plaintiffs", "defendant", "defendants",
            "respondent", "respondents", "petitioner", "petitioners",
            "appellant", "appellants", "appellee", "appellees",
            "intervenor", "intervenors",
        }
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        wide = (pw - 2 * self.body_baseline_x0) * 0.7
        start_page = all_segments[start][0]
        last_role = None
        # The fallback start segment may itself BE caption rows ('C. Perez,
        # et al.,' / 'Defendants') — scan it too, not just what follows.
        for j in range(start, len(all_segments)):
            pno, seg, _k2 = all_segments[j]
            if pno != start_page:
                break
            stop = False
            for l in seg:
                runs = self._caption_char_runs(l)
                if len(runs) == 1 and (l["x1"] - l["x0"]) > wide:
                    stop = True
                    break
                t = self.line_plain_text(l).strip()
                # Role rows may be compounds ('Plaintiff/Third-Party
                # Defendant,' / 'Third-Party Plaintiffs.') — a short,
                # punctuation-terminated caption row containing a role word.
                low = t.rstrip(".,").lower()
                if low in roles or (
                    len(t) <= 45
                    and t[-1:] in ".,"
                    and any(
                        w in low.replace("/", " ").replace("-", " ").split()
                        for w in roles
                    )
                ):
                    last_role = j
            if stop:
                break
        if last_role is not None and last_role + 1 < len(all_segments):
            start = last_role + 1
        # A footnote referenced from the CAPTION (a superscript on a party
        # or title row) belongs to the headmatter — record its label so
        # ``extract`` can move it. A footnote must never go missing.
        labels = set()
        for _p3, seg3, _k3 in all_segments[:start]:
            for line in seg3:
                chars = line.get("chars") or []
                sizes = [
                    round(c.get("size", 0), 1)
                    for c in chars
                    if (c.get("text") or "").strip()
                ]
                if not sizes:
                    continue
                dom = max(set(sizes), key=sizes.count)
                run = ""
                for c in chars:
                    t3 = c.get("text") or ""
                    if t3.isdigit() and c.get("size", 0) < dom * 0.8:
                        run += t3
                    elif run:
                        labels.add(run)
                        run = ""
                if run:
                    labels.add(run)
        self._hm_super_labels = labels
        return [start]

    def split_author_line(self, line):
        """The opinion-start line is a heading, not a byline; the author comes
        from the signature block / minute line. Return (author, [heading-as-body]).
        When no structured author was found, leave it empty — guessing from the
        opening line would grab the caption banner ('UNITED STATES DISTRICT
        COURT') on a signature-less order."""
        author = getattr(self, "_district_author", None)
        return (author or "", [line])

    def classify_document_type(self, all_segments, author_indices, n_pages):
        from ..models import DocType

        if author_indices:
            return DocType.OPINION
        return super().classify_document_type(all_segments, author_indices, n_pages)
