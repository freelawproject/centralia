"""Wisconsin Court of Appeals.

Intermediate appellate court. Author byline at the opinion start ('NAME, Judge.' / 'NAME, J.' / 'PER CURIAM'); the shared appellate base reuses the abbreviated-title parser and drops the trial-judge / panel-roster caption lines.

Page 1 opens with a two-column masthead. The LEFT column is the clerk's filing
stamp — 'DATED AND FILED', the decision date, the clerk's name and title — which
is headmatter. The RIGHT column, under its own 'NOTICE' heading, is the standing
publication notice ('This opinion is subject to further editing…'), which is
boilerplate on every decision and belongs in the Removed box. The two columns
share baselines, so pdfplumber reads them as single interleaved lines
('Samuel A. Christensen petition to review an adverse decision by the') and they
have to be separated by x before either can be classified.
"""

from __future__ import annotations

from ._appellate import StateAppellate


class WisconsinCourtOfAppeals(StateAppellate):
    court_id = "wisctapp"
    court_label = "Wisconsin Court of Appeals."
    strip_para_marker = True  # byline opens with the paragraph marker: "¶1 HRUZ, J."

    # The publication notice is set in small print (8pt) against a masthead
    # otherwise set at 12-14pt.
    _notice_max_size = 9.0
    # Runs must share a left rail to this tolerance to count as one column.
    _rail_tol = 2.5
    # Every continuation page repeats the appeal number at the top right
    # ('No.  2025AP825') — a running header, not body text.
    running_header_docket = True

    def is_docket_line(self, text) -> bool:
        t = (text or "").strip()
        low = t.lower()
        if not (low.startswith("no.") or low.startswith("nos.")):
            return False
        rest = t.split(".", 1)[1].strip()
        # A separate writing repeats the appeal number with its part tag —
        # '(C)' for the concurrence, '(D)' for the dissent.
        if rest.endswith(")") and "(" in rest:
            rest = rest[: rest.rfind("(")].strip()
        toks = rest.replace(",", " ").split()
        return bool(toks) and all(any(ch.isdigit() for ch in tk) for tk in toks)

    @staticmethod
    def _x_runs(line, gap=6.0) -> list:
        """Split a line's chars into runs separated by an x-gap. The masthead's
        two columns share baselines, so they arrive as one line object and can
        only be told apart by where their glyphs sit."""
        chars = [c for c in (line.get("chars") or [])]
        if not chars:
            return []
        chars.sort(key=lambda c: c["x0"])
        runs, cur = [], [chars[0]]
        for c in chars[1:]:
            if c["x0"] - cur[-1]["x1"] > gap:
                runs.append(cur)
                cur = [c]
            else:
                cur.append(c)
        runs.append(cur)
        return [r for r in runs if any((c.get("text") or "").strip() for c in r)]

    def extract(self, pdf_path):
        self._notice_runs = []
        self._caption_appeal_numbers = set()
        doc = super().extract(pdf_path)
        if self._notice_runs:
            doc.dropped = list(doc.dropped) + [" ".join(self._notice_runs)]
        return doc

    @staticmethod
    def _appeal_number(text):
        """Return a bare Wisconsin appellate docket token, or ``None``."""
        token = (text or "").strip().strip(",;")
        upper = token.upper()
        if "AP" not in upper or not any(ch.isdigit() for ch in upper):
            return None
        if any(ch.isspace() for ch in token):
            return None
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
        return token if all(ch in allowed for ch in upper) else None

    @staticmethod
    def _circuit_number(text):
        token = (text or "").strip().strip(",;")
        upper = token.upper()
        if not any(tag in upper for tag in ("CM", "CF", "CV", "JV", "FA")):
            return None
        if not any(ch.isdigit() for ch in upper) or any(ch.isspace() for ch in token):
            return None
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
        return token if all(ch in allowed for ch in upper) else None

    def _caption_dockets(self, lines):
        """Read the two docket columns between their printed caption labels."""
        ordered = sorted(lines, key=lambda line: (line.get("top", 0), line.get("x0", 0)))
        start = None
        stop = None
        for i, line in enumerate(ordered):
            text = " ".join(self.line_plain_text(line).split()).lower()
            if start is None and (
                text.startswith("appeal no.") or text.startswith("appeal nos.")
            ):
                start = i
                continue
            if start is not None and text.startswith("state of wisconsin"):
                stop = i
                break
        if start is None:
            return [], []
        band = ordered[start : stop if stop is not None else len(ordered)]
        pw = getattr(self, "_page1_width", 612.0) or 612.0
        appeals, circuits = [], []
        for line in band:
            for token in self.line_plain_text(line).split():
                if line.get("x0", 0) < pw / 2:
                    number = self._appeal_number(token)
                    if number and number not in appeals:
                        appeals.append(number)
                else:
                    number = self._circuit_number(token)
                    if number and number not in circuits:
                        circuits.append(number)
        return appeals, circuits

    def _masthead_bottom(self, page) -> float:
        """The masthead ends at the caption band's first full-width rule."""
        tops = [
            r["top"]
            for r in list(page.rects) + list(page.lines)
            if abs(r["bottom"] - r["top"]) < 2.5
            and (r["x1"] - r["x0"]) > page.width * 0.4
        ]
        return min(tops) if tops else page.height * 0.45

    def _notice_rail(self, runs, pw) -> float | None:
        """The x the notice column is set against: the left edge shared by the
        small-print runs in the right half of the masthead. A column is at
        least three runs deep, which no incidental right-hand run reaches."""
        from collections import Counter

        xs = Counter()
        for x0, _top, size, _text in runs:
            if size <= self._notice_max_size and x0 > pw * 0.5:
                xs[round(x0 / self._rail_tol)] += 1
        if not xs:
            return None
        bucket, n = xs.most_common(1)[0]
        return bucket * self._rail_tol if n >= 3 else None

    def page_lines(self, page):
        """Split the masthead's two columns and route the notice column to
        ``dropped``, keeping the clerk's filing stamp beside it as headmatter."""
        lines = super().page_lines(page)
        if not hasattr(self, "_caption_appeal_numbers"):
            self._caption_appeal_numbers = set()

        # Learn every docket in the page-one consolidated-caption band.  On
        # continuation pages Wisconsin prints one of those bare numbers at the
        # extreme upper-right.  Remove only that repeated geometric header;
        # docket citations in body text remain untouched.
        caption_appeals, _caption_circuits = self._caption_dockets(lines)
        if caption_appeals:
            self._caption_appeal_numbers.update(caption_appeals)
        elif self._caption_appeal_numbers:
            filtered = []
            for line in lines:
                text = self.line_plain_text(line).strip()
                if (
                    line.get("top", 0) < 70
                    and line.get("x0", 0) > page.width * 0.7
                    and text in self._caption_appeal_numbers
                ):
                    continue
                filtered.append(line)
            lines = filtered
        # The masthead is NOT always page 1: a published opinion carries a
        # reporter cover sheet (the citation, 'Complete Title of Case',
        # counsel, panel) ahead of it, so the decision masthead can land on
        # page 3. Rather than assume a page, let the notice column identify
        # itself — three or more small-print runs sharing a rail in the right
        # half, above the caption's first full-width rule. Nothing else on any
        # page has that shape, so the search is safe to run everywhere.
        pw = page.width
        bottom = self._masthead_bottom(page)
        band = [l for l in lines if l["top"] < bottom]
        runs = [
            (r[0]["x0"], l["top"], r[0].get("size", 0), self.line_plain_text({"chars": r}))
            for l in band
            for r in self._x_runs(l)
        ]
        rail = self._notice_rail(runs, pw)
        if rail is None:
            return lines
        # The notice column runs from its heading down to its last line; a
        # right-hand run BELOW it (the 'Cir. Ct. No. …' half of the docket row)
        # is caption content, not notice.
        # Only runs ON the rail bound the column. A small-print run further
        # right and lower down ('Cir. Ct. No.  2024CV549') is caption content
        # and must not extend the notice's reach down over it.
        rail_tops = [
            t
            for x0, t, sz, _ in runs
            if abs(x0 - rail) <= self._rail_tol and sz <= self._notice_max_size
        ]
        if not rail_tops:
            return lines
        # Bound the column at BOTH ends. Its own 'NOTICE' heading sits about a
        # line above the first small-print run, but the reporter citation
        # ('2026 WI App 23') is flush right higher up the same page and is not
        # part of the notice.
        first, last = min(rail_tops) - 24, max(rail_tops) + 4

        def in_notice(char) -> bool:
            return (
                char["x0"] >= rail - self._rail_tol
                and first <= char["top"] <= last
            )

        out = []
        for line in lines:
            if line["top"] >= bottom:
                out.append(line)
                continue
            chars = line.get("chars") or []
            keep = [c for c in chars if not in_notice(c)]
            taken = self.line_plain_text(
                {"chars": [c for c in chars if in_notice(c)]}
            ).strip()
            if taken:
                self._notice_runs.append(taken)
            if not any((c.get("text") or "").strip() for c in keep):
                continue
            out.extend(self._split_columns({**line, "chars": keep}))
        return out

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Populate both consolidated appeal and circuit-court dockets."""
        result = super().extract_headmatter(headmatter_segs, page1_rules)
        appeals, circuits = [], []
        pages = {}
        for seg in headmatter_segs:
            for line in seg:
                chars = line.get("chars") or []
                pno = (
                    chars[0].get("page_number") if chars else line.get("page_number")
                ) or 1
                pages.setdefault(pno, []).append(line)
        for lines in pages.values():
            page_appeals, page_circuits = self._caption_dockets(lines)
            for number in page_appeals:
                if number not in appeals:
                    appeals.append(number)
            for number in page_circuits:
                if number not in circuits:
                    circuits.append(number)
        if appeals:
            result["docketnumber"] = ", ".join(appeals)
        if circuits:
            result["otherdocket"] = ", ".join(circuits)
        return result

    def _split_columns(self, line) -> list:
        """Emit one line per COLUMN of a masthead row.

        The masthead pairs a left-hand run with a right-hand one on a shared
        baseline — 'STATE OF WISCONSIN' beside 'IN COURT OF APPEALS', with
        'DISTRICT IV' under the latter on the next baseline. Read as one line
        the two columns are glued into a single string and the right column's
        second row is orphaned below it. Split at the x-gap and each column
        keeps its own alignment, so the right-hand rows stack together as
        printed."""
        runs = self._x_runs(line, gap=18.0)
        if len(runs) < 2:
            if not runs:
                return []
            return [self._as_line(line, runs[0])]
        return [self._as_line(line, r) for r in runs]

    @staticmethod
    def _as_line(line, run) -> dict:
        out = dict(line)
        out["chars"] = run
        out["text"] = "".join(c.get("text") or "" for c in run)
        out["x0"] = min(c["x0"] for c in run)
        out["x1"] = max(c["x1"] for c in run)
        return out

    def find_footnote_separator(self, page):
        # A long rule separates headmatter from the opinion; only treat a rule
        # with footnote-sized text below it as the footnote separator, so that
        # divider doesn't chop the ¶1 byline + body.
        return self._footnote_sep_small_text_below(page)
