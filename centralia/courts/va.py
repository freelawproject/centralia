"""Supreme Court of Virginia.

The majority author is announced in the caption, not signed at the body. The
caption's right column carries 'OPINION BY' over a '[CHIEF/SENIOR ]JUSTICE
<NAME>' line (often merged into the record-number row, e.g. 'v. Record No. 250365
JUSTICE JUNIUS P. FULTON, III'), then the decision date. A centered 'FROM THE
COURT OF APPEALS ...' / 'FROM THE CIRCUIT COURT ...' line closes the caption, and
the opinion body opens immediately below it (an indented paragraph, no byline or
¶ marker). So, coloctapp-style: read the author off the caption, keep the whole
caption in the headmatter, and start the majority at the first segment after the
appeal-from block ('FROM THE COURT OF APPEALS ...', or an order's 'UPON AN APPEAL
FROM A JUDGMENT RENDERED BY THE COURT OF APPEALS ...'). An unsigned per-curiam
order — caption present but no 'OPINION BY' — is authored 'PER CURIAM'.

A separate writing is signed in-body, with an ALL-CAPS title byline that names
its joiners and its kind across one or two lines:

    CHIEF JUSTICE POWELL, with whom JUSTICE MANN and JUSTICE FULTON join,
    dissenting.

Those are detected as additional opinion starts (title + ALL-CAPS surname opening
a segment whose block carries 'dissenting'/'concurring'); the byline line is kept
as the writing's opening body line. A per-curiam order — no 'OPINION BY', no
appeal-from line — falls back to the default byline search.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, _is_byline_name

# Longest-first so a compound title wins over the bare 'JUSTICE'.
_TITLES = ("ASSOCIATE JUSTICE", "SENIOR JUSTICE", "CHIEF JUSTICE", "JUSTICE")


class VirginiaSupreme(StateSupreme):
    court_id = "va"
    court_label = "Supreme Court of Virginia."

    # The convening recital that opens every Virginia ORDER ('VIRGINIA: / In the
    # Supreme Court of Virginia held at the Supreme Court Building in the / City
    # of Richmond on Thursday, the 11th day of December, 2025.'). An argued
    # opinion opens on 'PRESENT: All the Justices' and announces its author with
    # 'OPINION BY'; an order has neither.
    _ORDER_RECITAL = "in the supreme court of virginia held at"

    def extract(self, pdf_path):
        self._va_meta = {}
        self._va_is_order = False
        doc = super().extract(pdf_path)
        # A per-curiam order's single writing is an order, not a majority
        # opinion (the delaware.py model).
        if self._va_is_order:
            for op in doc.opinions:
                if op.author == "PER CURIAM":
                    op.type = "order"
        return doc

    def classify_document_type(self, all_segments, author_indices, n_pages) -> str:
        """Virginia publishes two document styles: an argued OPINION (caption
        announces the author with 'OPINION BY [CHIEF/SENIOR ]JUSTICE NAME') and
        a per-curiam ORDER (the convening recital, no announced author). The
        base classifier calls anything with a byline an opinion, so an order —
        whose writing is attributed 'PER CURIAM' — has to be told apart by its
        recital."""
        recital = any(
            self._ORDER_RECITAL in self.line_plain_text(ln).lower()
            for _p, seg, _k in all_segments
            for ln in seg
        )
        announced = bool(self._va_author_in(all_segments))
        self._va_is_order = recital and not announced
        if self._va_is_order:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def correct_page_geometry(self, page) -> None:
        """Strip Word's INVISIBLE footnote-anchor ghost.

        Virginia's opinions are set in Word, which writes a sub-visible (~1pt
        Arial) '0F' / '12F' pair beside the real superscript footnote mark. It
        sits on its own baseline, so the line rebuild folds it into the body row
        and the sentence comes out as 'the Government Data Act.0F1' — which no
        longer matches the printed 'Act.1' and lost a line per footnote anchor.
        Drop the sub-visible chars from the page's object cache so the extractor
        and the audit (which reads through this same hook) both see the real
        superscript only."""
        super().correct_page_geometry(page)
        try:
            objs = page.objects.get("char")
        except Exception:
            objs = None
        if objs:
            objs[:] = [c for c in objs if (c.get("size") or 9.0) > 1.5]

    # ----------------------------------------------------------- opinion starts
    def find_authors(self, all_segments) -> list:
        self._va_meta = {}
        # The appeal-from block closes the caption: a centered 'FROM THE ...'
        # line (opinions) or an 'UPON AN APPEAL FROM ...' block (orders).
        from_idx = None
        for i, (_p, seg, _k) in enumerate(all_segments):
            if any(self._is_appeal_from(self.line_plain_text(ln)) for ln in seg):
                from_idx = i
                break

        starts, scan_from = [], 0
        if from_idx is not None:
            # The appeal-from source can run several right-aligned lines ('UPON AN
            # APPEAL FROM A / JUDGMENT RENDERED BY THE / COURT OF APPEALS ...');
            # skip them to the first left-aligned body paragraph.
            body = from_idx + 1
            while (
                body < len(all_segments)
                and all_segments[body][1][0]["x0"] >= 300
            ):
                body += 1
            if body < len(all_segments):
                # Announced author, or an unsigned per-curiam order.
                maj = self._va_author_in(all_segments[:body]) or "PER CURIAM"
                starts.append(body)
                self._va_meta[body] = (maj, "majority")
                scan_from = body

        # In-body separate writings (dissents / concurrences).
        for i in range(scan_from, len(all_segments)):
            if i in self._va_meta:
                continue
            info = self._va_separate(all_segments[i][1])
            if info:
                starts.append(i)
                self._va_meta[i] = info

        if not starts:
            # Per-curiam order (no announced author): default byline search.
            return super().find_authors(all_segments)
        return sorted(starts)

    @staticmethod
    def _is_appeal_from(text: str) -> bool:
        """The ALL-CAPS line that closes the caption and opens the body.

        Three printed forms, all set in capitals on their own line:
        'FROM THE COURT OF APPEALS OF VIRGINIA' (a plain appeal), and the
        'UPON …' recitals the Court uses for everything else — 'UPON AN APPEAL
        FROM A JUDGMENT RENDERED BY …', 'UPON A PETITION UNDER CODE § 8.01-670.2'
        (interlocutory review), 'UPON A QUESTION OF LAW CERTIFIED BY THE UNITED
        STATES COURT OF APPEALS …' (a certified question). The capitals are the
        discriminator: an ordinary sentence opening 'Upon review, …' is not this
        line."""
        t = (text or "").strip()
        if not t or t != t.upper():
            return False
        return t.startswith("FROM THE ") or t.startswith("UPON ") or "APPEAL FROM" in t

    def _va_author_in(self, segments):
        """The announced majority author: the '[CHIEF/SENIOR ]JUSTICE <NAME>' run
        on a caption line (kept with its title, like coloctapp's 'JUDGE SCHUTZ').
        Taken from the title word to the line end, so a merged 'v. Record No.
        NNNN' lead is dropped."""
        for _p, seg, _k in segments:
            for ln in seg:
                t = self.line_plain_text(ln).strip()
                for title in _TITLES:
                    j = t.find(title + " ")
                    if j != -1:
                        return t[j:].strip()
        return None

    def _va_separate(self, seg):
        """If ``seg`` opens a separate writing, return (author, type); else None.
        The first line is a title + ALL-CAPS surname; the kind is read from the
        byline block (the disposition word can wrap onto the next line)."""
        author = self._va_title_name(self.line_plain_text(seg[0]).strip())
        if not author:
            return None
        blob = " ".join(self.line_plain_text(l) for l in seg[:3]).lower()
        if "dissent" in blob and "concur" in blob:
            return author, "concurring in part and dissenting in part"
        if "dissent" in blob:
            return author, "dissent"
        if "concur" in blob:
            return author, "concurrence"
        return None

    @staticmethod
    def _va_title_name(text):
        for title in _TITLES:
            if text.startswith(title + " "):
                name = text[len(title) + 1 :].split(",")[0].strip()
                if _is_byline_name(name):
                    return f"{title} {name}"
        return None

    # ------------------------------------------------------------ author / body
    def split_author_line(self, line):
        # Every Virginia opinion opens on text (the majority on its first body
        # paragraph, a separate writing on its byline line); keep it as the
        # opening body line and let build_opinion stamp the author/type.
        if getattr(self, "_va_meta", None):
            return "", [line]
        return super().split_author_line(line)

    def build_opinion(self, op_start, op_end, **kwargs):
        op = super().build_opinion(op_start, op_end, **kwargs)
        meta = getattr(self, "_va_meta", {}).get(op_start)
        if meta:
            op.author, op.type = meta
        return op
