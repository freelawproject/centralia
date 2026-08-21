"""Shared layout for the Connecticut courts (conn / connappct).

Both print the same front matter, so the handling lives here once (the per-court
files stay thin — they only pick the right byline base):

  * a publication notice ('The "officially released" date ... may not be
    reproduced ...') bracketed by rows of asterisks — administrative furniture,
    routed to ``dropped``;
  * a running header (the short case name, repeated at the top of every page) —
    page furniture, dropped (the audit tolerates it as a repeated margin line);
  * page-aware headmatter so a multi-page syllabus keeps document order (the
    long syllabus spans several pages; a y-only sort interleaves them);
  * an official 'Syllabus' that follows the caption/panel and precedes the
    opinion byline — captured into the ``syllabus`` field (expressly not part of
    the opinion), leaving the caption/panel as the headmatter.
"""

from __future__ import annotations

import re
from statistics import median

from ._statesupreme import is_caps_name

_TAG = re.compile(r"<[^>]+>")


class ConnecticutStyle:
    # The Connecticut Reports set the body at a wide left margin (x0≈174) with a
    # small ~10pt first-line indent (≈184). Without this the default threshold
    # (72+28=100) treats every body line as a new paragraph, so nothing groups.
    body_baseline_x0 = 174.0
    para_indent_min = 6.0

    # THIS COURT'S SEPARATOR DECISION IS FINAL. ``find_footnote_separator``
    # below excludes rules above 185pt on purpose, because the Reports rule
    # their running heads at 163.8 and 180.2 and those pass the base chain's
    # 'footnote-size text below' test. Left to retry, the base chain answers
    # 163.8 on every body page, so every line of body text (which starts at
    # 187) counted as being INSIDE the footnote zone: body_lines came out empty,
    # segmentation saw nothing, no byline was ever at a segment head, and the
    # whole document became headmatter. That cost 22 conn and 11 connappct
    # opinions outright.
    footnote_sep_override_final = True

    # Connecticut draws its GENUINE separator against the text: 1.88pt below
    # the last body line in mutual_security_credit_union_v._hardy, inside the
    # 2pt band ``_rule_underlines_text`` reads as an underline decorating that
    # line. The shared reject-underlines veto therefore deletes this court's
    # real rule — the corpus-wide control (2,090 hand-labelled documents)
    # broke exactly two documents under a blanket veto, both conn — so the
    # family opts out.
    footnote_sep_reject_underlines = False

    # Joinder byline for a separate writing, often its own file: 'MULLINS, C. J.,
    # with whom D'AURIA, J., joins, concurring in part and dissenting in part.'
    # The kind clause wraps to the next line, so the base treats the comma after
    # the title as a roster and rejects it — recognize it here.
    def parse_author_line(self, text):
        r = super().parse_author_line(text)
        if r is not None:
            return r
        low = text.lower()
        # One judge 'joins', two or more 'join' — a plural roster ('with whom
        # McDONALD and ECKER, Js., join') is the common shape for a separate
        # writing, so matching only the singular missed those outright.
        joined = {t.strip(".,;:") for t in low.split()} & {"join", "joins", "joined"}
        if ", with whom" in low and joined:
            name = text.split(",", 1)[0].strip()
            if is_caps_name(name):
                after = text.split(",", 1)[1].lstrip()
                title = (
                    "Chief Justice"
                    if after[:4] in ("C.J.", "C. J")
                    else (
                        "Presiding Justice"
                        if after[:4] in ("P.J.", "P. J")
                        else "Justice"
                    )
                )
                kind = (
                    "concurring and dissenting"
                    if "concur" in low and "dissent" in low
                    else (
                        "concurring"
                        if "concur" in low
                        else "dissenting" if "dissent" in low else None
                    )
                )
                return name, title, kind
        return None

    # The Connecticut Reports NAME their own structure, in centred labels
    # present in every document sampled (14 of 14): 'Syllabus', 'Procedural
    # History', 'Opinion'. The byline is the first line after 'Opinion'.
    CONN_LABELS = ("Syllabus", "Procedural History", "Opinion")

    def segment_lines(self, lines, page_width) -> list:
        """Segment the Connecticut way: by the FIRST-LINE INDENT and the court's
        own centred labels.

        These Reports mark a paragraph with a 10pt first-line indent — x0=184.0
        against a 174.0 rail — and not with extra leading: on state_v._brown the
        body lead is 12.25pt and a paragraph gap is 17.87pt, while the syllabus
        above it runs 10.33pt against 16.33pt. Gap-based segmentation cannot
        separate those reliably, and when it failed it fused 47 segments into 7,
        buried 'McDONALD, J. The defendant, James Brown, appeals' inside one of
        them, and left the document with no byline at any segment head — so no
        author, no opinion start, and all 162 rows became headmatter. Twenty-two
        conn and eleven connappct documents were lost that way.

        Reading the indent instead is not a heuristic here: it is how the
        reporter sets a paragraph, and it is measured off the court's own rail.
        """
        rail = self.body_baseline_x0
        indent_at = rail + self.para_indent_min
        segments: list = []
        current: list = []

        def flush():
            if current:
                segments.append(list(current))
                current.clear()

        for line in lines:
            text = self.line_plain_text(line).strip()
            x0 = line.get("x0", 0.0)
            is_label = text in self.CONN_LABELS
            # A centred label stands alone, and so does anything set well right
            # of the indent (the 'Argued …' line, the panel roster, a running
            # head) — those are their own rows, never part of a paragraph.
            centred = x0 > indent_at + 12
            if is_label or centred or x0 >= indent_at - 1:
                flush()
            current.append(line)
            if is_label or centred:
                flush()
        flush()
        return segments

    def find_authors(self, all_segments) -> list:
        """A joinder byline wraps across two lines —

            D'AURIA, J., with whom McDONALD and ECKER,
            Js., join, dissenting in part. In State v. Purcell, ...

        so the first line carries no verb and parses as nothing on its own. A
        separate writing published as its own file then yields no opinion at
        all, taking its footnotes with it. Retry those as a joined pair, gated
        on the 'with whom' shape so ordinary bylines are left alone."""
        found = list(super().find_authors(all_segments))
        for i, (_p, seg, _kind) in enumerate(all_segments):
            # No kind filter: Connecticut's centered measure classifies most
            # body segments as 'notice', bylines included.
            if i in found or len(seg) < 2:
                continue
            first = self.line_plain_text(seg[0]).strip()
            if ", with whom" not in first.lower():
                continue
            pair = f"{first} {self.line_plain_text(seg[1]).strip()}"
            if self.parse_author_line(pair):
                found.append(i)
        return sorted(found)

    def find_footnote_separator(self, page):
        """Connecticut strokes its rules as vector lines rather than filled
        rects. The shared finder scans only ``page.rects`` — which is empty on
        every page here — so it finds no separator and the footnotes are lost
        wholesale, body text and all.

        Same predicate as the base (thin, >=100pt wide, at the body margin,
        footnote-sized text below), applied to the strokes — but bounded by the
        head band rather than the base's half-page cutoff. A long footnote
        pushes its separator well up the sheet (alers_v._bemer draws it at
        385pt on a 792pt page, above the base's 435pt cutoff, and the footnote
        it opens was silently lost). The running-head rules at 163.8/180.2 read
        as footnote separators on the 'small text below' test alone, so they
        still have to be excluded by position — the head band does that, and
        nothing but head furniture ever sits above 185pt here."""
        # The head band binds the INHERITED answer too. The advance-sheet
        # printing (Connecticut Law Journal) sets an extra header — 'Page 6
        # CONNECTICUT LAW JOURNAL March 3, 2026' at x0=138 — and on those pages
        # the shared chain answers 163.8, the running-head rule, which this
        # court's own scan would never accept. Returned unchecked, it put the
        # byline ('ALEXANDER, J. A jury found the defendant,' at y=654.9, under
        # the centred 'Opinion' label) inside the footnote zone and cost the
        # opinion. Same rule, applied to whoever proposes the y.
        cutoff = 185.0
        sep = super().find_footnote_separator(page)
        if sep is not None and sep > cutoff:
            return sep
        x0_max = self.body_baseline_x0 + 4
        tops = [
            l["top"]
            for l in page.lines
            if abs(l.get("height", 0)) < 2
            and (l["x1"] - l["x0"]) >= 100
            and l["x0"] <= x0_max
            and l["top"] > cutoff
            and self._rule_over_footnotes(page, l["top"])
        ]
        return min(tops) if tops else None

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        # The joinder byline's kind clause wraps onto the first body line; read
        # the opinion type off it.
        if "with whom" in op.author.lower() and op.type == "majority" and op.blocks:
            head = _TAG.sub("", op.blocks[0].text).lower()[:70]
            if "concur" in head and "dissent" in head:
                op.type = "concurring-in-part-and-dissenting-in-part"
            elif "dissent" in head:
                op.type = "dissent"
            elif "concur" in head:
                op.type = "concurrence"
        return op

    def extract(self, pdf_path: str):
        self._conn_notice = []
        self._conn_criteria = {}
        doc = super().extract(pdf_path)
        if self._conn_notice:
            doc.dropped = list(doc.dropped) + self._conn_notice
        self._split_syllabus(doc)
        self._publish_conn_criteria(doc)
        return doc

    def _publish_conn_criteria(self, doc) -> None:
        """Attach the named criteria, the way the circuits do.

        The circuits report a headmatter as a dict of named parts plus the NAME
        of the layout they read it with (ca2: head_docket / short_case_name /
        term / date_argued / date_decided / panel_line / counsel /
        headmatter_style). Connecticut had only the flat typed fields, so its
        review page showed an empty 'Parsed criteria' panel. The rows stay in
        ``summary`` and ``audit._doc_chunks`` reads ``criteria``, so publishing
        them moves nothing out of the audit's reach."""
        crit = dict(getattr(self, "_conn_criteria", None) or {})
        if not crit:
            return
        panel_line = crit.get("judges")
        out = {
            "court": self.court_label or self.court_id,
            "docket": crit.get("docketnumber"),
            "case_name": " v. ".join(crit.get("parties") or []) or None,
            "parties": crit.get("parties") or [],
            "panel_line": panel_line,
            "panel": self._conn_panel_names(panel_line),
            "date_argued": crit.get("submitted"),
            "date_released": crit.get("decisiondate"),
            "procedural_history": crit.get("history"),
            "counsel": crit.get("attorneys"),
            "headmatter_style": self._conn_headmatter_style(),
        }
        doc.criteria = {k: v for k, v in out.items() if v not in (None, [], "")}

    @staticmethod
    def _conn_panel_names(panel_line) -> list:
        """The panel's surnames out of the printed roster: 'Mullins, C. J., and
        McDonald, D'Auria, Ecker, Alexander, Dannehy and Bright, Js.' The
        abbreviated titles are the court's, not names, so they come off."""
        if not panel_line:
            return []
        titles = {"C. J.", "C.J.", "J.", "Js.", "P. J.", "P.J.", "C", "J", "Js"}
        names = []
        for chunk in panel_line.replace(" and ", ", ").split(","):
            t = chunk.strip().strip(".").strip()
            if not t or f"{t}." in titles or t in titles:
                continue
            if t.lower().startswith("and "):
                t = t[4:].strip()
            if t and t[0].isupper():
                names.append(t)
        return names

    def _note_law_journal(self, texts) -> None:
        """Record the advance-sheet furniture wherever a court drops it, so the
        style is known for connappct too (which has no head-band capture)."""
        # The advance sheet is identified by its RUNNING HEADER — 'Page 6
        # CONNECTICUT LAW JOURNAL March 3, 2026' — not by the phrase alone: the
        # publication notice names the Law Journal in every printing, bound
        # Reports included, so matching the phrase called all 80 documents
        # advance sheets.
        for t in texts:
            u = (t or "").upper()
            if "CONNECTICUT LAW JOURNAL" in u and u.lstrip().startswith("PAGE "):
                self._conn_law_journal = True
                break

    def _conn_headmatter_style(self) -> str:
        """Which of the court's two printings this document is.

        The bound *Connecticut Reports* and the *Connecticut Law Journal*
        advance sheet carry the same front matter in different furniture — the
        Law Journal adds a 'Page 6 CONNECTICUT LAW JOURNAL March 3, 2026' header
        at x0=138 — and naming it is what let the two be told apart when the
        advance-sheet pages were losing their bylines."""
        band = " ".join(getattr(self, "_conn_head", None) or [])
        return (
            "connecticut law journal advance sheet"
            if getattr(self, "_conn_law_journal", False) or "LAW JOURNAL" in band.upper()
            else "connecticut reports"
        )

    def page_lines(self, page):
        """Drop the asterisk-bracketed 'officially released' notice (-> dropped)
        and the repeated short-case-name running header at the page top."""
        lines = super().page_lines(page)
        out, captured, in_notice = [], [], False
        self._note_law_journal(
            (l.get("text") or "") for l in lines
        )
        for l in lines:
            t = (l.get("text") or "").strip()
            if t and len(t) >= 10 and set(t) == {"*"}:
                in_notice = not in_notice  # asterisk delimiter row
                continue
            if in_notice:
                captured.append(t)
            else:
                out.append(l)
        if captured:
            self._conn_notice.append(" ".join(captured))
        # Drop the running head. A slip opinion carries one line (the short
        # 'X v. Y' case name); the bound Connecticut Reports carry two — a
        # volume/page/date band ('354 Conn. 151 FEBRUARY, 2026 153') above the
        # case name. Both sit above the body and are set smaller than it, so
        # the head is the run of undersized lines at the page top.
        #
        # Left in, that band is not just noise: it lands mid-sentence between
        # the page's first line and the paragraph continuing from the previous
        # page, so every paragraph spanning a page break is split in three.
        # Anchored on position alone. Font size cannot make this call: the
        # syllabus is itself set at 8pt, so on syllabus pages the 8pt head is
        # not "smaller than the body" and survives. Nor can wording: an
        # 'In re Hunter T.' head carries no ' v. '. But the reporter's measure
        # is rigid — across both corpora the only lines above 185pt on a
        # continuation page are head furniture (the volume/date band at 150.5
        # and the case name at ~169, wrapping to a second row on long names),
        # and the body never opens above 187.7.
        if page.page_number > 1:
            out = [l for l in out if l.get("top", 0) >= 185]
        return out

    # ----------------------------------------------------- page-aware headmatter
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        rows = []  # (page, top, x0, text)
        for seg in headmatter_segs:
            for line in seg:
                t = (line.get("text") or "").strip()
                if not t:
                    continue
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                rows.append((pno, round(line["top"], 1), round(line["x0"], 1), t))
        out = {
            "court": self.court_label or self.court_id,
            "summary": self._paged_layout_rows(rows),  # shared (StateSupreme)
            "headmatter_lines": [],
            "caption_box": getattr(self, "_hm_caption_box", None),
            "dropped": [],
        }
        crit = self._read_conn_criteria(rows)
        self._conn_criteria = crit
        out.update(crit)
        return out

    def _read_conn_criteria(self, rows):
        """Dissect the Connecticut headmatter into its named parts.

        The Reports label their own structure, so this reads the labels and the
        paragraph indent rather than guessing:

            Argued February 5—officially released April 28, 2026
                              -> submitted (argued) + decisiondate (released)
            Procedural History
            Action to recover on a promissory note, ... Reversed; further
            proceedings.                                -> history
            Tadhg Dooley, with whom were Garrett A. Denniston ...
            Robert C. Lubus, Jr., for the appellee (plaintiff).
                                                        -> attorneys
            Opinion                                     -> end of headmatter

        The boundary between the procedural history and counsel is the indent:
        both are set as indented paragraphs (x0=184 against a 174 rail), the
        history is the FIRST one after its label, and every indented paragraph
        after it is a counsel block. The rows stay in ``summary`` either way, so
        nothing moves out of the audit's reach.
        """
        argued = released = None
        history_paras: list = []
        counsel_paras: list = []
        caption_lines: list = []
        panel_lines: list = []
        docket = None
        state = None  # None -> before the label; 'history'; 'counsel'
        indent_at = self.body_baseline_x0 + self.para_indent_min - 1

        def is_caps_row(t):
            """The party caption is set in full capitals ('THOMAS LUMPKIN, JR.
            v. NUTMEG STATE FINANCIAL CREDIT UNION'), the lowercase 'v.' aside,
            so measure the ratio rather than demanding isupper()."""
            alpha = [c for c in t if c.isalpha()]
            return bool(alpha) and sum(c.isupper() for c in alpha) >= 0.75 * len(alpha)

        def is_panel_row(t):
            """The panel names the judges and ends in their abbreviated title —
            'Mullins, C. J., and McDonald, D'Auria, Ecker,' wrapping to
            'Alexander, Dannehy and Bright, Js.'. The wrap means the first line
            carries no terminal title, so accept either half."""
            return (
                ", C. J." in t
                or t.rstrip().endswith(("Js.", ", J.", "Js", "J."))
                or (", J.," in t)
            )

        for _pno, _top, x0, text in rows:
            t = text.strip()
            if t == "Opinion":
                break
            if t == "Procedural History":
                state = "history"
                continue
            # 'Argued February 5—officially released April 28, 2026'. Split on
            # the court's own wording, not on a date pattern: the em-dash joins
            # two facts and 'officially released' names the second.
            if t.startswith("Argued ") and "officially released" in t:
                head, _, tail = t.partition("officially released")
                argued = head[len("Argued "):].strip().strip("—–-").strip()
                released = tail.strip().rstrip(".").strip()
                continue
            if state is None:
                # The court's own caption, above the reporter's first heading:
                # party rows in capitals, the docket in parentheses, the panel.
                if t.startswith("(") and t.endswith(")") and any(c.isdigit() for c in t):
                    docket = t.strip("()").strip()
                elif is_caps_row(t):
                    caption_lines.append(t)
                elif is_panel_row(t):
                    panel_lines.append(t)
                continue
            if x0 >= indent_at:
                # A fresh indented paragraph. The first one closes the history.
                if state == "history" and history_paras:
                    state = "counsel"
                (history_paras if state == "history" else counsel_paras).append([t])
            else:
                target = history_paras if state == "history" else counsel_paras
                if target:
                    target[-1].append(t)

        def joined(paras):
            if not paras:
                return None
            return "\n\n".join(self.join_wrapped_lines(p) for p in paras) or None

        caption = self.join_wrapped_lines(caption_lines) if caption_lines else None
        parties = (
            [p.strip() for p in caption.split(" v. ") if p.strip()]
            if caption and " v. " in caption
            else ([caption] if caption else [])
        )
        return {
            "submitted": argued,
            "decisiondate": released,
            "history": joined(history_paras),
            "attorneys": joined(counsel_paras),
            "docketnumber": docket,
            "parties": parties,
            "judges": self.join_wrapped_lines(panel_lines) if panel_lines else None,
        }

    @staticmethod
    def _split_syllabus(doc) -> None:
        """Move the 'Syllabus' block (from the 'Syllabus' heading to the end of
        the headmatter) out of ``summary`` into the ``syllabus`` field."""
        summary = doc.summary or []
        idx = next(
            (
                i
                for i, row in enumerate(summary)
                if str(row).strip().lower() == "syllabus"
            ),
            None,
        )
        if idx is None:
            return
        doc.syllabus = [str(r).strip() for r in summary[idx:] if str(r).strip()]
        doc.summary = summary[:idx]
