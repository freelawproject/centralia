"""Bankruptcy Appellate Panel of the Sixth Circuit.

'NOT RECOMMENDED FOR PUBLICATION' + 'File Name:' cover lines, a
box-drawing caption (┐ │ ┘ glyphs), 'Appeal from …', the panel roster
('Before: BAUKNIGHT, Chief Judge; GREGG, and MASHBURN, Bankruptcy
Appellate Panel Judges.'), a COUNSEL block, then a centered 'OPINION'
heading and the byline with the body inline: 'JOHN T. GREGG, Bankruptcy
Appellate Panel Judge. Doug Woods, the appellant …'.

The panel also issues UNSIGNED orders ('in_re_curare_laboratory_llc'): the
caption's right column carries a letter-spaced 'O R D E R' instead of a
disposition, there is no byline anywhere, and the panel closes with 'ENTERED BY
ORDER OF THE PANEL' over the clerk's name. See ``_order_fallback``.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme

_TITLES = (
    "Chief Bankruptcy Appellate Panel Judge",
    "Bankruptcy Appellate Panel Judge",
    "Circuit Judge",  # direct-appeal Sixth Circuit opinions in the corpus
    "Chief Judge",
    "Judge",
)


class SixthCircuitBAP(StateSupreme):
    court_id = "bap6"
    court_label = "Bankruptcy Appellate Panel of the Sixth Circuit."
    author_titles = _TITLES
    drop_notice_in_body = False
    # BAP6's ordinary body is double-spaced at roughly 20.7pt.  The shared
    # classifier's 22pt cutoff therefore mistakes nearly every body segment
    # for a single-spaced blockquote.
    gap_single_max = 18
    # True BAP6 block quotes are set in from both margins and single-spaced;
    # identify those geometrically after the ordinary body leading is fixed.
    blockquote_by_indent = True

    # Every continuation page opens with a one-line running head — 'Nos.
    # 18-8010/8013/8018 In re Blasingame Page 7' — at top≈55.8, with the body
    # starting at ≈97. Bound the head by the band it actually occupies so no
    # body line is ever caught.
    running_head_max_top = 70.0

    def _maybe_drop_running_header(self, page, lines):
        """Cut the continuation-page running head and record it, so it shows in
        the Removed box rather than leaking into the headmatter (it was landing
        mid-caption as 'Nos. … In re Blasingame Page 2')."""
        lines = super()._maybe_drop_running_header(page, lines)
        if page.page_number == 1:
            return lines
        if not hasattr(self, "_running_header_dropped"):
            self._running_header_dropped = []
        kept = []
        for ln in lines:
            if ln.get("top", 0) <= self.running_head_max_top:
                text = " ".join(self.line_plain_text(ln).split())
                if text:
                    self._running_header_dropped.append(text)
                continue
            kept.append(ln)
        return kept

    def parse_author_line(self, text):
        parsed = super().parse_author_line(text)
        if parsed is not None:
            return parsed
        t = (text or "").strip().rstrip(".")
        for title in _TITLES:
            suffix = ", " + title
            if not t.endswith(suffix):
                continue
            name = t[: -len(suffix)].strip()
            tokens = name.replace("-", " ").split()
            # BAP bylines can begin with an initial (``C. KATHRYN
            # PRESTON``), which the generic full-name grammar intentionally
            # excludes.  The BAP's all-caps name plus its distinctive full
            # title is sufficiently narrow.
            if 2 <= len(tokens) <= 5 and all(
                token.rstrip(".").replace("'", "").isupper()
                and token.rstrip(".").replace("'", "").isalpha()
                for token in tokens
            ):
                return name, title, None
        return None

    def _order_fallback(self, all_segments):
        """An unsigned panel order: the body opens after the panel roster.

        The shared fallback anchors on a segment whose first line reads
        'ORDER …', which this court never gives it — its order title is set
        inside the caption's right column and letter-spaced ('O R D E R'), so
        the anchor was never found and all six pages of
        ``in_re_curare_laboratory_llc`` stayed in the headmatter.

        The roster is the boundary instead: in this court everything above
        'Before: <judges>, Bankruptcy Appellate Panel Judges.' is caption, and
        below it comes either the byline (a signed opinion, which never reaches
        this fallback) or, on an unsigned order, the body itself.
        """
        anchored = super()._order_fallback(all_segments)
        if anchored:
            return anchored
        roster = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if not seg:
                continue
            text = " ".join(self.line_plain_text(l).strip() for l in seg)
            if text.startswith("Before") and text.rstrip(".").endswith(
                ("Judge", "Judges")
            ):
                roster = i
        if roster is None:
            return []
        # ONLY AN ACTUALLY UNSIGNED DOCUMENT. 'in_re_ormet_corp.' does carry a
        # byline ('JESSICA E. PRICE SMITH, Bankruptcy Appellate Panel Judge.
        # The issue on appeal …') that the byline pass fails to pick up for its
        # own reasons; anchoring it after the roster would open the writing on
        # the COUNSEL block above the OPINION AND ORDER title and dress a
        # byline bug up as a parsed order. If any line below the roster is
        # byline-shaped, leave the document alone.
        for _p, seg, _k in all_segments[roster + 1 :]:
            for line in seg:
                if self._byline_split(line) is not None:
                    return []
        for j in range(roster + 1, len(all_segments)):
            seg = all_segments[j][1]
            if not seg or self.is_separator_line(seg[0]):
                continue
            if not self.line_plain_text(seg[0]).strip():
                continue
            self._order_start = j
            self._order_author = self._conformed_signature_author(all_segments)
            return [j]
        return []

    def _has_body_between(self, all_segments, start, end) -> bool:
        """Also accept a byline whose opinion body shares its own segment.

        This panel runs the opinion's first sentence INLINE with the byline
        ('JESSICA E. PRICE SMITH, Bankruptcy Appellate Panel Judge.  The issue
        on appeal before the Panel is …') and the rest of the paragraph
        continues in the same segment. The shared base looks for the body in a
        LATER segment, so on a one-page disposition — where the byline's
        segment is the LAST one, footnotes and counsel aside — the byline read
        as a sign-off and ``in_re_ormet_corp.`` came out with no author, no
        opinion and ``doc_type=unknown``, its whole affirmance sitting in the
        headmatter.

        The split is the proof: ``_byline_split`` only returns a second element
        when real text follows the title on the byline's own line, and a bare
        signature ('C. KATHRYN PRESTON, Bankruptcy Appellate Panel Judge' with
        nothing after it) still has none.
        """
        if super()._has_body_between(all_segments, start, end):
            return True
        seg = all_segments[start][1] if start < len(all_segments) else []
        if not seg:
            return False
        text = self.line_plain_text(seg[0]).strip()
        split = self._byline_split(seg[0])
        if self._is_bare_signature(text, split):
            return False
        return len(seg) > 1 or bool(split and split[1])

    def _is_indented_blockquote(self, seg):
        # Issue-list continuations use a deeper hanging indent (x≈144), while
        # an actual BAP6 block quote begins at the normal quote edge (x≈108).
        # The shared broad test consequently treated list continuations as
        # quotes; keep the geometric test but reject that deeper edge.
        if not super()._is_indented_blockquote(seg):
            return False
        return min(line["x0"] for line in seg) <= self.body_baseline_x0 + 40

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        rows = result.get("summary", [])
        start = next(
            (
                i
                for i, row in enumerate(rows)
                if isinstance(row, dict)
                and row.get("__hm__")
                # Case-INSENSITIVE: the caption's opening row is typeset 'In
                # re:' on most of the corpus and 'IN RE:' on the rest. Keying
                # on the upper-case spelling alone silently disabled the whole
                # fold — the rail glyphs stayed embedded in the party rows and
                # every caption line became its own headmatter row.
                and "IN RE:" in str(row.get("html", "")).upper()
            ),
            None,
        )
        end = next(
            (
                i
                for i, row in enumerate(rows)
                if i > (start if start is not None else -1)
                and isinstance(row, dict)
                and row.get("__hm__")
                and "Appeal from" in str(row.get("html", ""))
            ),
            None,
        )
        if start is None or end is None:
            return result

        left, right, source_rows = [], [], []
        for row in rows[start:end]:
            if not isinstance(row, dict) or not row.get("__hm__"):
                if row == "":
                    left.append("")
                    right.append("")
                continue
            text = str(row.get("html", ""))
            source_rows.append(text)
            marker = "│>" if "│>" in text else None
            if marker is None:
                for candidate in ("┐", "┘", "│"):
                    if candidate in text:
                        marker = candidate
                        break
            if marker is None:
                left.append(text)
                right.append("")
                continue
            ltext, rtext = text.split(marker, 1)
            left.append(ltext.strip())
            right.append(rtext.strip())

        result["summary"] = rows[:start] + [
            {
                "__caption__": True,
                "left": left,
                "right": right,
                "rail": "|",
                "shape": "old-faithful",
                "rail_rows": len(left),
                # The drawn border replaces the source rail glyphs visually;
                # retain the original rows for completeness accounting.
                "source": source_rows,
            }
        ] + rows[end:]
        return result

    def _byline_split(self, line):
        # 'JOHN T. GREGG, Bankruptcy Appellate Panel Judge. <body inline>'
        # — non-bold, period-terminated byline with the body following on
        # the same line. The panel roster ('Before: …; …, and …') never
        # matches: it starts with 'Before:' and names several judges.
        text = self.line_plain_text(line).strip()
        if text.startswith("Before"):
            return None
        for t in _TITLES:
            key = ", " + t + "."
            ki = text.find(key)
            if 0 < ki < 40:
                head = text[: ki + len(key) - 1]
                if self.parse_author_line(head) is not None:
                    return head + ".", text[ki + len(key) :].strip()
        if text.upper().startswith("PER CURIAM"):
            ends = [text.find(c) for c in ".:" if text.find(c) != -1]
            i = min(ends) if ends else -1
            if i == -1:
                return text, ""
            return text[: i + 1], text[i + 1 :].strip()
        return super()._byline_split(line)
