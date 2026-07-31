"""Shared base for the byline-at-start state supreme courts.

Most state supreme courts open each opinion with an author byline, so the core
``BaseExtractor`` pipeline handles them — these subclasses mainly set the court
label and, where the court uses a reversed/prose byline ('JUSTICE KING, Opinion
of the Court:' / 'OPINION OF THE COURT BY GINOZA, J.'), add a no-regex parser
for it. No regex (see the project's no-regex preference); byline shapes are
matched with string prefixes and a caps-name check.
"""

from __future__ import annotations

from typing import Optional

from .generic import GenericExtractor


# Byline-shaped lines that are never THIS court's opinion author: the
# lower-court judge carried in the 'Appeal from' history, or a panel roster.
_NON_AUTHOR_PREFIXES = (
    "the honorable",
    "honorable ",
    "hon. ",
    "appeal from",
    "on appeal from",
    "appeal of",
    "before ",
)
_TRIAL_TITLES = ("District Judge", "Circuit Judge", "Superior Court Judge")
# A 'WE CONCUR:' / 'I DISSENT' line opens a signature roster: the justices
# joining an opinion sign below it as bare 'NAME, Title' lines (no opinion of
# their own). Those signatures are not new opinions.
_ROSTER_MARKERS = ("we concur", "i concur", "we dissent", "i dissent")


class StateSupreme(GenericExtractor):
    # Single-spaced bodies can read as 'notice' by line-gap; never drop body
    # content on that basis (completeness).
    drop_notice_in_body = False
    # These courts run the body lower than Alabama (a byline can sit at the
    # very bottom of a page); page numbers are lower still (~743), so this keeps
    # real content without pulling in the footer.
    margin_bottom = 740
    # A small-print notice can start very near the top edge (top~36); the body
    # proper sits far lower (top~120+), so a lower top margin keeps the whole
    # notice without pulling in page-top junk.
    margin_top = 32
    # If set, headmatter lines at/below this font size are the publication
    # notice (small print) and are removed into ``dropped`` — set per court that
    # actually HAS such a notice (don't assume one). None = remove nothing.
    notice_max_size: float | None = None

    # Opt-in: display the headmatter as an exact-position facsimile (x/y,
    # size, weight preserved — the '__facsimile__' summary sentinel), with
    # each line split into separately-positioned runs at column gaps so a
    # caption rail (Delaware's '§' column, the California AG ':' table)
    # keeps its true x. The plain rows still follow for the audit and DB.
    facsimile_headmatter = False

    @staticmethod
    def _fold_rail_caption(rows: list, rail: str) -> list:
        """Collapse a run of rail-glyph caption rows ('PARTY § No. 62, 2026' /
        'PARTY )') into one two-column ``__caption__`` block — parties left of
        the rail, docket/court-below right. ``rows`` is a styled summary list;
        non-caption rows pass through untouched.

        The rail is drawn one glyph PER SOURCE ROW that bore it — including the
        rail-only rows the PDF stacks between double-spaced party names ('PARTY
        )' / ')' / 'Respondent, )') — so the bracket keeps its true height and
        the left/right cells keep their vertical rhythm (blank rows aligned to
        the rail rows that carried no text)."""
        from re import sub as _sub

        out, cap_rows = [], []  # cap_rows: [(lpart, rpart)]

        def flush():
            if cap_rows:
                out.append(
                    {
                        "__caption__": True,
                        "left": [l for l, _ in cap_rows],
                        "right": [r for _, r in cap_rows],
                        "rail": rail,
                        "rail_rows": len(cap_rows),
                    }
                )
                cap_rows.clear()

        for r in rows:
            if not (isinstance(r, dict) and r.get("__hm__")):
                flush()
                out.append(r)
                continue
            text = _sub("<[^>]+>", "", str(r.get("html", "")))
            toks = text.split()
            # The rail must stand alone as its own token — a ')' inside
            # '(302) 255-0634' or a '§' in a statute cite never does.
            if rail in toks:
                idx = toks.index(rail)
                lpart = " ".join(toks[:idx]).strip()
                rpart = " ".join(t for t in toks[idx + 1 :] if t != rail).strip()
                cap_rows.append((lpart, rpart))
            else:
                flush()
                out.append(r)
        flush()
        return out

    def _fold_open_caption(self, summary, headmatter_segs, limit=None):
        """Fold an 'Open Range' caption — two columns held by whitespace alone
        (parties left, docket / division / opinion-type right of the page
        middle) — into one two-column ``__caption__`` block with no rail
        glyph, rebuilt from the page-1 line runs. pdfplumber merges the two
        columns onto single lines ('PERSON and ESTATE OF MILO No. 87593-1-I'),
        so the styled rows can't be split after the fact; the runs can.

        The caption zone is the span of rows carrying a right-column run,
        extended in BOTH directions through rows whose runs stay on one side
        of the page middle (a party row above the first docket row, a
        defendant list below the last one); a row with a run CROSSING the
        middle — banner, byline, prose — ends the zone. ``limit`` caps the
        zone by y (Ohio's '* * * * *' counsel divider). Rows the fold can't
        place stay exactly as they were."""
        import re as _re
        from statistics import median

        lines = []
        for seg in headmatter_segs:
            for l in seg:
                chars = l.get("chars") or []
                pno = (
                    chars[0].get("page_number", 1)
                    if chars
                    else l.get("page_number", 1)
                ) or 1
                if pno == 1:
                    lines.append(l)
        lines.sort(key=lambda l: l["top"])
        pw = getattr(self, "_page1_width", None) or 612.0
        mid = pw / 2 - 25
        center = pw / 2

        # One visual row per baseline: the two columns often reach page_lines
        # as SEPARATE lines at the same top ('PERSON and ESTATE OF MILO' +
        # 'No. 87593-1-I'), so fold same-top lines into one row before zoning.
        rows = []  # {top, lines, lefts, rights, crosses}
        for l in lines:
            if limit is not None and l["top"] >= limit - 1:
                continue
            runs = self._split_line_runs(l)
            lefts = [r for r in runs if r["x0"] < mid]
            rights = [r for r in runs if r["x0"] >= mid]
            crosses = any(r["x0"] < center < r["x1"] for r in runs)
            if rows and abs(l["top"] - rows[-1]["top"]) <= 2:
                m = rows[-1]
                m["lines"].append(l)
                m["lefts"] += lefts
                m["rights"] += rights
                m["crosses"] = m["crosses"] or crosses
            else:
                rows.append(
                    {
                        "top": l["top"],
                        "lines": [l],
                        "lefts": lefts,
                        "rights": rights,
                        "crosses": crosses,
                    }
                )
        hit = [i for i, r in enumerate(rows) if r["rights"]]
        if len(hit) < 2:
            return summary
        lo, hi = min(hit), max(hit)
        # extend through one-sided rows; a middle-crossing row ends the zone
        while lo > 0 and not rows[lo - 1]["crosses"]:
            lo -= 1
        while hi + 1 < len(rows) and not rows[hi + 1]["crosses"]:
            hi += 1
        zone = rows[lo : hi + 1]

        # Build the two cells, keeping the page's vertical rhythm (a 1.5-line
        # gap becomes a blank row) and the left column's role indents.
        tops = [z["top"] for z in zone]
        gaps = [b - a for a, b in zip(tops, tops[1:])]
        unit = median(gaps) if gaps else 30.0
        zone_left = min(
            (r["x0"] for z in zone for r in z["lefts"]), default=None
        )
        # Claim the DRAWN caption rules inside the zone — a shelf under the
        # party column (teela), the full rule between stacked consolidated
        # captions (aiden), the short rule under a right-cell heading — and
        # render each at its true side, not as a full-width divider after the
        # block. Claimed rules are removed from the summary's __DIVIDER__
        # rows by the splice below.
        shelves = []  # (top, side) side ∈ left / right / full
        for rt_, rx0, rx1 in getattr(self, "_p1_rule_spans", []) or []:
            if not (tops[0] - unit <= rt_ <= tops[-1] + 2 * unit):
                continue
            if limit is not None and rt_ >= limit - 1:
                continue
            if rx1 <= center + 60 and rx0 < mid:
                side = "left"
            elif rx0 >= mid - 20:
                side = "right"
            else:
                side = "full"
            # a rule drawn in pieces shares one top — first (widest-first by
            # sort) piece wins
            if not any(abs(rt_ - t) < 1.5 for t, _s in shelves):
                shelves.append((rt_, side))
        claimed_rules = len(shelves)
        # A DRAWN vertical mid rule between the columns renders as the '|'
        # divider — whitespace would drop a line the PDF draws. A partial
        # vertical (aiden: one caption of a consolidated stack) is NOT
        # stretched to full height; the columns stay whitespace-held rather
        # than inventing rule length the page doesn't have.
        rail = ""
        zone_span = max(tops[-1] - tops[0], 1.0)
        for vx, vtop, vbot in getattr(self, "_p1_vrule_spans", []) or []:
            if not (mid - 30 <= vx <= center + 30):
                continue
            overlap = min(vbot, tops[-1] + unit) - max(vtop, tops[0] - unit)
            if overlap / zone_span >= 0.6:
                rail = "|"
                break

        left_cells, right_cells = [], []
        prev = None

        def emit_shelves(upto):
            while shelves and shelves[0][0] < upto:
                _t, side = shelves.pop(0)
                left_cells.append(
                    {"__shelf__": True} if side in ("left", "full") else ""
                )
                right_cells.append(
                    {"__shelf__": True} if side in ("right", "full") else ""
                )

        for z in zone:
            emit_shelves(z["top"])
            if prev is not None and unit and (z["top"] - prev) > 1.4 * unit:
                for _ in range(max(1, round((z["top"] - prev) / unit) - 1)):
                    left_cells.append("")
                    right_cells.append("")
            prev = z["top"]
            lefts = sorted(z["lefts"], key=lambda r: r["x0"])
            rights = sorted(z["rights"], key=lambda r: r["x0"])
            lt = " ".join((r.get("text") or "").strip() for r in lefts).strip()
            rt = " ".join((r.get("text") or "").strip() for r in rights).strip()
            if (
                lt
                and lefts
                and zone_left is not None
                and lefts[0]["x0"] - zone_left > 14
            ):
                left_cells.append({"h": lt, "ind": lefts[0]["x0"] - zone_left})
            else:
                left_cells.append(lt)
            right_cells.append(rt)
        emit_shelves(float("inf"))  # trailing shelf under the last row

        # Splice: replace the styled rows that came from the zone lines with
        # the one caption block; swallow the '' gap rows between them.
        def norm(s):
            return " ".join(
                _re.sub(r"<[^>]+>", "", str(s)).replace("&amp;", "&").split()
            )

        targets = [
            " ".join((l.get("text") or "").split())
            for z in zone
            for l in z["lines"]
        ]
        out, ti, placed = [], 0, False
        dividers_left = claimed_rules
        at_tail = False  # inside/just past the block, only blanks appended
        for row in summary:
            txt = (
                norm(row.get("html", ""))
                if isinstance(row, dict) and row.get("__hm__")
                else None
            )
            if ti < len(targets) and txt is not None and txt == targets[ti]:
                if not placed:
                    out.append(
                        {
                            "__caption__": True,
                            "left": left_cells,
                            "right": right_cells,
                            "rail": rail,
                            "rail_rows": len(left_cells),
                        }
                    )
                    placed = True
                    at_tail = True
                ti += 1
                continue
            if placed and at_tail and isinstance(row, str):
                if not row.strip():
                    if ti < len(targets):
                        continue  # a gap between caption rows: in the block
                    out.append(row)
                    continue  # a blank after the block keeps us at the tail
                if row == self.HEADMATTER_DIVIDER and dividers_left > 0:
                    # this rule renders as an in-caption shelf, not a divider
                    dividers_left -= 1
                    continue
            # any other real row ends the tail
            if placed and (
                txt is not None or (isinstance(row, str) and row.strip())
            ):
                at_tail = False
            out.append(row)
        return out if placed else summary

    @staticmethod
    def _squeeze_spaced(text: str) -> str:
        """'O R D E R' → 'ORDER'.

        A court sets an order's heading letter-spaced as often as solid, and the
        two are the same word: the spacing is typography, not content. A run of
        consecutive single-character tokens is one letter-spaced word;
        multi-character tokens are left alone, so 'PER CURIAM ORDER' and a mixed
        'PER CURIAM O R D E R' both come out whole. Used by Maryland and DC,
        whose order headings are letter-spaced in some templates only — a
        heading test keyed on the solid form silently returns no writing at
        all for the spaced ones."""
        out, run = [], []
        for tok in text.split():
            if len(tok) == 1 and tok.isalpha():
                run.append(tok)
                continue
            if len(run) >= 3:
                out.append("".join(run))
            else:
                out.extend(run)
            run = []
            out.append(tok)
        if len(run) >= 3:
            out.append("".join(run))
        else:
            out.extend(run)
        return " ".join(out)

    def _split_line_runs(self, line) -> list:
        """Split a line into separately-positioned runs at column gaps
        ('GREGORY GRIFFIN, ... §' is two runs, not one string at the line's
        left edge). Word spacing is ~3-4pt; a gap past 8pt is a column."""
        chars = line.get("chars") or []
        if not chars:
            return [line]
        runs, cur = [], [chars[0]]
        for a, b in zip(chars, chars[1:]):
            if b["x0"] - a["x1"] > 8:
                runs.append(cur)
                cur = [b]
            else:
                cur.append(b)
        runs.append(cur)
        if len(runs) == 1:
            return [line]
        return [
            {
                "text": self.line_plain_text({"chars": r}),
                "chars": r,
                "x0": min(c["x0"] for c in r),
                "x1": max(c["x1"] for c in r),
                "top": line["top"],
                "bottom": line.get("bottom"),
            }
            for r in runs
        ]

    # Styled headmatter is the corpus-wide default: centered/bold rows at
    # relative size with the page's vertical gaps preserved. A court can
    # opt out back to the monospace layout dump, or up to the facsimile.
    styled_headmatter = True

    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Establish the headmatter as one section. Return ALL of it verbatim
        (styled rows by default; layout-preserved ``summary`` + positioned
        ``headmatter_lines`` for the facsimile / opt-out paths), except a
        small-print publication notice — identified by font size on courts
        that have one — which is removed into ``dropped`` complete."""
        if self.styled_headmatter and not self.facsimile_headmatter:
            return self._styled_headmatter(headmatter_segs, page1_rules)
        if self.facsimile_headmatter:
            headmatter_segs = [
                [r for line in seg for r in self._split_line_runs(line)]
                for seg in headmatter_segs
            ]
        lines, notice = [], []
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                size, _font, bold = self.line_meta(line)
                if self.notice_max_size is not None and size <= self.notice_max_size:
                    notice.append(t)
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                lines.append(
                    {
                        "text": t,
                        "x0": round(line["x0"], 1),
                        "top": round(line["top"], 1),
                        "size": size,
                        "bold": bold,
                        "page": pno,
                    }
                )
        # Keyed by (page, top, x0): headmatter that runs past page 1 (a long
        # counsel block, a syllabus) must never interleave with page-1 content
        # that happens to sit lower on its own page.
        items = [(l["page"], l["top"], l["x0"], l["text"]) for l in lines]
        summary = self._paged_layout_rows(items)
        if self.facsimile_headmatter:
            summary = [{"__facsimile__": True}] + summary
        return {
            "court": self.court_label or self.court_id,
            "summary": summary,
            "headmatter_lines": lines,
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [" ".join(notice)] if notice else [],
        }

    def styled_headmatter_rows(self, rows: list) -> list:
        """Hook: adjust the placed headmatter rows — ``(page, top, x0, payload)``,
        in reading order — before they are turned into styled summary rows.

        The payload carries ``html``/``size``/``x1``/``align`` (or ``divider``),
        so a court can reconcile a run of wrapped lines that belongs together
        before per-line measurements are frozen into the output. No-op by
        default."""
        return rows

    def _styled_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        """Style-preserving headmatter (the 'Florida' look): each line keeps its
        relative font size, bold/italic, and alignment; underscore rules become
        horizontal lines; ordering is page-aware. Opt-in — a court returns this
        from ``extract_headmatter``. A small-print notice (``notice_max_size``)
        is routed to ``dropped``."""
        from collections import Counter as _Counter

        pw = getattr(self, "_page1_width", 612.0) or 612.0
        # A notice is *small print* — smaller than the document's own body. The
        # ``notice_max_size`` cap alone misfires when a court sets it near the
        # body size and a given document is set entirely at that size (NM Ct
        # App: a 12pt notice on 14pt opinions, but other NM opinions are 12pt
        # throughout — the whole caption would be dropped). Gate the routing on
        # being strictly smaller than the dominant headmatter size as well, so
        # body-size text is never mistaken for a notice.
        hm_sizes = _Counter(
            round(self.line_meta(line)[0])
            for seg in headmatter_segs
            for line in seg
            if (line.get("text") or "").strip()
        )
        # A notice is smaller than the caption/banner. Compare against the
        # LARGEST headmatter size, not the most-common one: a multi-line notice
        # can itself be the most-common size (Georgia's 5-line 8pt advisory),
        # which would defeat a 'dominant'-based guard and leave it in.
        hm_max = max(hm_sizes) if hm_sizes else 12
        rows, notice = [], []
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                size, _font, _bold = self.line_meta(line)
                if (
                    self.notice_max_size is not None
                    and size <= self.notice_max_size
                    and round(size) < hm_max
                ):
                    notice.append(t)
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                top, x0 = round(line["top"], 1), round(line["x0"], 1)
                if all(c in "_-—–" for c in t):
                    rows.append((pno, top, x0, {"divider": True}))
                    continue
                # A row can hold more than one COLUMN. North Dakota prints the
                # party at the left margin and its status flush right on the
                # same baseline ('Jarrod Jashawn Adams,' … 'Petitioner and
                # Appellant' ending exactly at x=540), and pdfplumber hands
                # that back as one line — so a single html string collapses a
                # 184pt gap to one space. Keep the runs, positioned.
                zones = []
                runs = self._split_line_runs(line)
                if len(runs) > 1:
                    right_margin = max(r["x1"] for r in runs)
                    for a, b in zip(runs, runs[1:]):
                        if b["x0"] - a["x1"] >= 24:
                            break
                    else:
                        runs = []  # no real column gap: ordinary word spacing
                    for r in runs:
                        txt = self.line_inline_text(r)
                        if not txt.strip():
                            continue
                        near_right = abs(r["x1"] - right_margin) <= 2
                        zones.append(
                            {
                                "h": txt,
                                "x0": round(r["x0"], 1),
                                "x1": round(r["x1"], 1),
                                "align": "r" if near_right and r is runs[-1] else "l",
                            }
                        )
                payload = {
                    "html": self.line_inline_text(line),
                    "size": size,
                    "x1": round(line["x1"], 1),
                    "align": self.line_alignment(line, pw),
                }
                if len(zones) > 1:
                    payload["zones"] = zones
                rows.append((pno, top, x0, payload))
        # Preserve DRAWN caption/headmatter rules (vector lines, hairline rects,
        # rule images) as dividers at their y-position — the styled builder
        # otherwise only kept underscore-TEXT rules. Collapse near-duplicate tops
        # (the same visual rule is often captured as several rect segments).
        seen_div: list = []
        cap_pno = getattr(self, "_caption_pno", 1)
        for div_top in sorted(page1_rules or []):
            if any(abs(div_top - s) < 4 for s in seen_div):
                continue
            seen_div.append(div_top)
            rows.append((cap_pno, round(div_top, 1), 0.0, {"divider": True}))
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        rows = self.styled_headmatter_rows(rows)
        # HORIZONTAL POSITION is content. A caption indents its role lines
        # under the party they belong to ('Plaintiff,' beneath 'ALEXIS
        # STOMBAUGH,'), and pins the docket number out to the right — and a
        # row model that keeps only L/C/R alignment flattens all of that to
        # flush left, so every court needed its own column fold before its
        # caption read correctly. Measure each row's offset from the block's
        # own left edge and carry it through; the renderer indents by it.
        left_edge = min(
            (x0 for _p, _t, x0, pl in rows if "size" in pl and x0 is not None),
            default=None,
        )
        sizes = [p["size"] for _, _, _, p in rows if "size" in p]
        base = _Counter(round(s) for s in sizes).most_common(1)[0][0] if sizes else 12
        summary = []
        prev_pno = prev_top = prev_size = None
        for pno, top, _x0, p in rows:
            # Preserve the page's vertical rhythm: a gap wider than ~1.8
            # lines (or a page break) becomes a blank row.  (indent below)
            if prev_top is not None and (
                pno != prev_pno or (top - prev_top) > 1.8 * max(prev_size or 12, 9)
            ):
                if summary and summary[-1] != "":
                    summary.append("")
            prev_pno, prev_top, prev_size = pno, top, p.get("size", prev_size)
            if p.get("divider"):
                summary.append("__DIVIDER__")
            else:
                row = {
                    "__hm__": True,
                    "html": p["html"],
                    "rel": round(p["size"] / base, 3),
                    "align": p["align"],
                }
                # ``html`` is left intact so the caption folds (which read it)
                # and the audit keep working; ``zones`` is additive.
                if p.get("zones"):
                    row["zones"] = p["zones"]
                # Only a LEFT-set row carries a meaningful indent: a centered
                # or right-set row is already positioned by its alignment, and
                # padding it as well would shift it off its own axis.
                if (
                    p["align"] == "L"
                    and left_edge is not None
                    and _x0 is not None
                    and (_x0 - left_edge) >= 6
                ):
                    row["ind"] = round(_x0 - left_edge, 1)
                summary.append(row)
        return {
            "court": self.court_label or self.court_id,
            "summary": summary,
            "headmatter_lines": [],
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [" ".join(notice)] if notice else [],
        }

    @staticmethod
    def _layout_rows(items: list) -> list:
        """Lines sharing a row (same top) placed on one text line, positioned
        by x0, so a two-column caption lines up in a whitespace-preserving
        block."""
        if not items:
            return []
        items.sort(key=lambda r: (r[0], r[1]))
        char_w = 6.0
        rows, segs, cur_top = [], [], None

        def emit(parts):
            line = ""
            # Order pieces left-to-right by x0 — items on one visual row can
            # have slightly different 'top' values (a label set a hair below
            # its value), so x0, not reading order, decides column position.
            for x0, text in sorted(parts, key=lambda p: p[0]):
                col = max(len(line) + (1 if line else 0), int((x0 - 72) / char_w))
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

    @staticmethod
    def _paged_layout_rows(items: list) -> list:
        """Like ``_layout_rows`` but keyed (page, top, x0), so multi-page
        headmatter (a syllabus spanning several pages) never interleaves across
        pages. ``items`` are (page, top, x0, text) tuples."""
        if not items:
            return []
        items.sort(key=lambda r: (r[0], r[1], r[2]))
        char_w = 6.0
        rows, segs, cur = [], [], None

        def emit(parts):
            line = ""
            for px0, ptext in sorted(parts, key=lambda p: p[0]):
                col = max(len(line) + (1 if line else 0), int((px0 - 72) / char_w))
                line += " " * (col - len(line)) + ptext
            return line

        for page, top, x0, text in items:
            if cur is not None and (page != cur[0] or abs(top - cur[1]) > 3):
                rows.append(emit(segs))
                segs = []
            segs.append((x0, text))
            cur = (page, top)
        if segs:
            rows.append(emit(segs))
        return rows

    # ---------------------------------------------------------------- bylines
    def _byline_at(self, line) -> bool:
        return self._byline_split(line) is not None or super()._byline_at(line)

    # Opt-in: move a footnote whose superscript reference sits in the
    # headmatter (a caption footnote, 'TASHA MILLMAN,¹') out of the first
    # opinion into ``headmatter_footnotes`` — page ownership alone would hand
    # it to the opinion that owns the rest of page 1.
    hm_caption_footnotes = False

    def extract(self, pdf_path):
        self._hm_super_labels = set()
        doc = super().extract(pdf_path)
        labels = getattr(self, "_hm_super_labels", set())
        if self.hm_caption_footnotes and labels and doc.opinions:
            op = doc.opinions[0]
            moved = [f for f in op.footnotes if f.label in labels]
            if moved:
                op.footnotes = [f for f in op.footnotes if f.label not in labels]
                doc.headmatter_footnotes = list(doc.headmatter_footnotes) + moved
        return doc

    def _superscript_labels(self, segs) -> set:
        """Labels of superscript digit references in the given segments — a
        digit run set well below the line's dominant font size."""
        labels = set()
        for seg in segs:
            for line in seg:
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
                    t = c.get("text") or ""
                    if t.isdigit() and c.get("size", 0) < dom * 0.8:
                        run += t
                    elif run:
                        labels.add(run)
                        run = ""
                if run:
                    labels.add(run)
        return labels

    def find_authors(self, all_segments) -> list:
        """Opinion starts: a bold all-caps author byline (possibly inline with
        the opinion text), or a byline the base parser recognizes. Lines that
        look like a byline but name a lower-court judge ('The Honorable ...,
        Circuit Judge' from an 'Appeal from' block) or a panel roster
        ('Before ...') are excluded — they are not the opinion author."""
        # Pass 1: candidate bylines, dropping signatures that sit in a roster
        # zone (after a 'WE CONCUR:' marker).
        cands = []
        roster_started = False
        for i, (_pno, seg, _kind) in enumerate(all_segments):
            if not seg:
                continue
            line = seg[0]
            text = self.line_plain_text(line).strip()
            if text.lower().rstrip(":").startswith(_ROSTER_MARKERS):
                roster_started = True
                continue
            if self._is_non_author_byline(text):
                continue
            split = self._byline_split(line)
            if split is None and not self.parse_author_line(text):
                continue
            # ``require_bold_byline`` also gates detection: a roman look-alike
            # (a trial judge from the 'Appeal from' block, a roman disposition
            # summary) parses via ``parse_author_line`` — which has no font — so
            # when the split path (bold-gated) declined, require bold here too.
            if split is None and getattr(self, "require_bold_byline", False):
                fc = (line.get("chars") or [{}])[0]
                if "bold" not in (fc.get("fontname") or "").lower():
                    continue
            bare = self._is_bare_signature(text, split)
            if roster_started and bare:
                continue
            cands.append((i, bare))

        # Pass 2: a *bare* byline ('NAME, Title' with no period/colon
        # terminator and no concur/dissent kind) with no real opinion body
        # before the next byline is a sign-off (the author signing their own
        # opinion), not a new opinion. A genuine bare byline (e.g. Louisiana's
        # 'WEIMER, Chief Justice*') is followed by its opinion body and kept.
        out = []
        for n, (i, _bare) in enumerate(cands):
            end = cands[n + 1][0] if n + 1 < len(cands) else len(all_segments)
            if not self._has_body_between(all_segments, i, end):
                # A byline with no opinion body before the next byline is a
                # sign-off, a signature roster, or an announcement of a separate
                # writing ('JUSTICE X filed a concurring opinion.') — not an
                # opinion start.
                continue
            out.append(i)
        if self.hm_caption_footnotes and out:
            self._hm_super_labels = self._superscript_labels(
                seg for _, seg, _ in all_segments[: out[0]]
            )
        return out

    @staticmethod
    def _is_bare_signature(text: str, split) -> bool:
        low = text.lower()
        if "concur" in low or "dissent" in low:
            return False
        byline = (split[0] if split else text).rstrip()
        return not byline.endswith((".", ":"))

    def _has_body_between(self, all_segments, start, end) -> bool:
        """True if a real (non-roster, non-signature) segment sits between
        byline ``start`` and ``end`` — i.e. the byline has an opinion body."""
        for k in range(start + 1, end):
            seg = all_segments[k][1]
            if not seg:
                continue
            line = seg[0]
            text = self.line_plain_text(line).strip()
            if not text:
                continue
            if text.lower().rstrip(":").startswith(_ROSTER_MARKERS):
                continue
            split = self._byline_split(line)
            if (split or self.parse_author_line(text)) and self._is_bare_signature(
                text, split
            ):
                continue
            return True
        return False

    def _is_non_author_byline(self, text: str) -> bool:
        """True if ``text`` parses as a byline but is a lower-court judge or a
        panel-roster line, not this court's opinion author."""
        low = text.lower()
        if any(low.startswith(p) for p in _NON_AUTHOR_PREFIXES):
            return True
        parsed = self.parse_author_line(text)
        # A state supreme opinion is authored by a Justice / Judge OF THIS
        # court; a 'District/Circuit/Superior Court Judge' byline is the trial
        # judge carried in the 'Appeal from' history.
        if parsed and parsed[1] in _TRIAL_TITLES:
            return True
        return False

    def split_author_line(self, line) -> tuple:
        """Split a byline that runs inline with the opinion text into
        (byline_text, [body_line]); a standalone byline yields no body."""
        r = self._byline_split(line)
        if r is None:
            return super().split_author_line(line)
        byline, body = r
        if not body:
            return byline, []
        chars = line.get("chars") or []
        target = len("".join(byline.split()))
        cnt, idx = 0, len(chars)
        for k, c in enumerate(chars):
            if not c.get("text", "").isspace():
                cnt += 1
            if cnt >= target:
                idx = k + 1
                break
        body_chars = chars[idx:]
        body_line = dict(line)
        body_line["text"] = body
        body_line["chars"] = body_chars
        if body_chars:
            body_line["x0"] = body_chars[0]["x0"]
        return byline, [body_line]

    def _byline_split(self, line):
        """If ``line`` starts with a BOLD, ALL-CAPS author byline, return
        (byline_text, body_text); else None. The byline clause runs to the
        first period after the title (so a non-bold ', dissenting.' tail is
        still captured); body_text is whatever opinion text follows on the
        same line ('' if none)."""
        text = self.line_plain_text(line).strip()
        chars = line.get("chars") or []
        if not text or not chars:
            return None
        # The name must be bold (the byline's tell). Char glyphs carry no
        # inter-word spaces, so we can't reconstruct the name from them — use
        # bold-led as the discriminator and parse the name from the spaced text.
        if "bold" not in chars[0].get("fontname", "").lower():
            return None
        if "," not in text:
            return None
        name = text.split(",")[0].strip()
        if not _is_byline_name(name):
            return None
        after = text.split(",", 1)[1].lstrip()
        if not any(t in after[:40] for t in ("Justice", "Judge")):
            return None
        # byline clause runs to the first period after the title
        ti = min(
            (text.find(t) for t in ("Justice", "Judge") if text.find(t) != -1),
            default=-1,
        )
        pi = text.find(".", ti)
        if pi == -1:
            return text, ""
        return text[: pi + 1], text[pi + 1 :].strip()

    def find_footnote_separator(self, page) -> Optional[float]:
        """Footnote rule: a thin (<2pt), reasonably wide (>=100pt) horizontal
        rule in the bottom half of the page. Caption-box rules — which come as a
        LEFT+RIGHT pair at the same height, split by the vertical divider — are
        excluded so a low caption box (on a short page) isn't mistaken for the
        footnote separator. Text underlines (a rule sitting directly under a
        line of text, e.g. an underlined attorney/firm name in the counsel
        block) are excluded too — otherwise such a rule chops the opinion body
        beneath it."""
        cutoff = page.height * 0.5
        # A footnote separator is anchored at the body's left edge; a centered,
        # short rule high on a title page (e.g. a section divider under a
        # running header) is not one and must not chop the body beneath it. The
        # anchor is the page's left quarter by default; a court whose separator
        # is right-shifted (Georgia: x0≈162) or right-aligned raises
        # ``footnote_sep_x0_max``.
        left_max = self.footnote_sep_x0_max or page.width * 0.25
        # Optional per-court width cap (a court whose separator is a fixed short
        # rule, e.g. iowa's ~2-inch). None = any rule >=100pt.
        wmax = self.footnote_sep_max_width
        min_w = self.footnote_sep_min_width(page)

        def scan(objs):
            return [
                r
                for r in objs
                if abs(r.get("height", 0)) < 2
                and (r["x1"] - r["x0"]) >= min_w
                and (wmax is None or (r["x1"] - r["x0"]) <= wmax)
                and r["top"] > cutoff
                and r["x0"] < left_max
            ]

        rules = scan(page.rects)
        if not rules:
            # Some courts STROKE the separator as a vector line instead of
            # filling a thin rect, leaving page.rects empty — every footnote in
            # the volume is then lost (neb: 594 references, none recovered).
            # Consulted only when the rects found nothing, so a court that
            # already resolves via rects is untouched.
            rules = scan(page.lines)
        if not rules:
            return self._fenceless_sep(page) or self._footnote_sep_text(page)
        text_lines = page.extract_text_lines()

        def is_caption_pair(r):
            rw = r["x1"] - r["x0"]
            for o in rules:
                if o is r:
                    continue
                if (
                    abs(o["top"] - r["top"]) < 2
                    and abs((o["x1"] - o["x0"]) - rw) < 40
                    and abs(o["x0"] - r["x0"]) > 50
                ):
                    return True
            return False

        def is_underline(r):
            # A rule drawn at the baseline of a text line it horizontally
            # overlaps is underlining that text (e.g. an underlined firm name in
            # the counsel block), not a footnote separator. The baseline sits a
            # hair above the glyph box's reported bottom (descenders go lower),
            # so accept a rule anywhere within the line's vertical span down to a
            # few points below it. A real separator sits in whitespace with no
            # text line spanning its top, so it is not caught here.
            for tl in text_lines:
                if (
                    tl["top"] - 1 <= r["top"] <= tl["bottom"] + 5
                    and r["x0"] < tl["x1"]
                    and r["x1"] > tl["x0"]
                ):
                    return True
            return False

        cands = [r for r in rules if not is_caption_pair(r) and not is_underline(r)]
        if not cands:
            return self._fenceless_sep(page) or self._footnote_sep_text(page)
        return min(cands, key=lambda r: r["top"])["top"]

    def _fenceless_sep(self, page):
        """Second pass with the bottom-half fence removed.

        The fence assumes a footnote zone sits low on the page, which is true
        until a footnote is long enough to push its own separator UP: dc/brooks
        (footnote 3 runs 20 lines) puts the rule at y=234, hawapp/yang_1 at 234,
        fladistctapp/dunlap at 278 — all on a 792pt sheet, all rejected, all
        losing every footnote on the page to the body.

        Dropping the fence is only safe against a rule the court uses SOLELY as
        a footnote separator, so this asks for the 2-inch (144pt) rule at the
        left body margin — the standard Word/CM-ECF and reporter divider — and
        nothing else."""
        return self.footnote_sep_fixed_left_rule(page, width=144.0)

    # Tuning for ``_footnote_sep_small_text_below``. The default treats the line
    # directly under a rule (its topmost char, within a ~22pt band) as a footnote
    # when it is at least 1pt smaller than the body. Courts whose footnote TEXT
    # is body-sized (only the marker is small) and whose zone may open with a
    # body-size continuation line set ``_fnsep_scan_band`` to look for a small
    # marker ANYWHERE in a wider band, with a tighter delta so a slightly-smaller
    # byline is not matched (Michigan).
    _fnsep_band = 22.0
    _fnsep_size_delta = 1.0
    _fnsep_scan_band = False
    # Optional per-court footnote-separator width cap (pt): a court whose
    # separator is a fixed short rule sets this so a wider caption shelf /
    # opinion divider isn't mistaken for it (iowa ~2-inch; indctapp's 144pt
    # rule vs the 396pt full-column byline divider). None = any rule >=100pt.
    footnote_sep_max_width: float | None = None
    # Optional per-court cap on the separator's left edge (pt). Default = the
    # page's left quarter; a court whose separator is right-shifted raises it
    # (Georgia: separator at x0≈162, a right-aligned ~324pt rule).
    footnote_sep_x0_max: float | None = None

    def _footnote_sep_small_text_below(self, page):
        """Footnote separator identified by footnote-sized text below the rule —
        used by courts whose headmatter/opinion divider rules the default finder
        would otherwise mistake for the separator (and chop the body beneath).
        Returns the topmost such rule's top, or None."""
        from collections import Counter as _C

        chars = page.chars
        if not chars:
            return None
        body = _C(round(c.get("size", 0)) for c in chars).most_common(1)[0][0]
        h, cands = page.height, []
        for r in page.rects:
            if not (
                r["height"] < 2.5 and (r["x1"] - r["x0"]) >= 80 and r["top"] > h * 0.4
            ):
                continue
            below = [
                c
                for c in chars
                if r["top"] < c["top"] < r["top"] + self._fnsep_band
                and not c["text"].isspace()
            ]
            if not below:
                continue
            # Default: the line directly under the rule must be footnote-sized.
            # Scan mode: a footnote-sized glyph ANYWHERE in the band (a marker)
            # marks the separator — the zone may open with a body-size
            # continuation line of the prior footnote before that marker appears.
            size = (
                min(c.get("size", 99) for c in below)
                if self._fnsep_scan_band
                else min(below, key=lambda c: c["top"]).get("size", 99)
            )
            if size <= body - self._fnsep_size_delta:
                cands.append(r["top"])
        return min(cands) if cands else None


# Mixed-case surname prefixes whose capital-then-lowercase form precedes an
# ALL-CAPS root ('McDONALD', 'DeHOOG', 'VanDYKE'). Longest first. These only
# match the mixed-case form, never an ALL-CAPS name ('DELANEY' doesn't start
# with 'De'), so stripping them is safe.
_NAME_PREFIXES = ("Mac", "Van", "Von", "Mc", "De", "Di", "La", "Le")


def _strip_name_prefix(core: str) -> str:
    for pre in _NAME_PREFIXES:
        if core.startswith(pre) and len(core) > len(pre):
            return core[len(pre):]
    return core


def _is_byline_name(name: str) -> bool:
    """ALL-CAPS author name, allowing middle initials ('RHONDA K. WOOD'), a
    mixed-case prefix ('McDONALD', 'MacKENZIE', 'DeHOOG', 'VanDYKE'), and
    apostrophes ('D'AURIA', 'O'BRIEN'), 1–4 tokens."""
    toks = name.split()
    if not toks or len(toks) > 4:
        return False
    for tok in toks:
        core = _strip_name_prefix(
            tok.rstrip(".").replace("'", "").replace("’", "").replace("-", "")
        )
        if not (core.isalpha() and core.isupper()):
            return False
    return True


def is_caps_name(name: str) -> bool:
    """True if ``name`` looks like an ALL-CAPS surname (optionally a mixed-case
    prefix or apostrophe), 1–3 tokens — used to tell a real byline from prose."""
    toks = name.split()
    if not toks or len(toks) > 3:
        return False
    for tok in toks:
        core = _strip_name_prefix(tok.replace("'", "").replace("’", ""))
        if not (core and core.isalpha() and core.isupper()):
            return False
    return True
