"""District of Columbia Court of Appeals.

Byline is name-first with a spelled-out judicial title and a colon, running
inline with the opinion text, not bold:
  'SHANKER, Associate Judge: Appellant Khari Alston ...'      (majority)
  'THOMPSON, Senior Judge: The petitioner ...'
  'BECKWITH, Associate Judge, dissenting: ...'                (separate writing)
A 'Before MCLEESE and SHANKER, Associate Judges, and GLICKMAN, Senior ...'
panel roster (plural 'Judges', 'Before' lead) and the announcement lines
('Opinion for the court by Senior Judge THOMPSON.' / 'Dissenting opinion by
Associate Judge BECKWITH at page 31.', which have no comma after a surname) are
not opinion starts.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, _is_byline_name

_TITLES = ("Associate Judge", "Senior Judge", "Chief Judge")


class DCCourtOfAppeals(StateSupreme):
    court_id = "dc"
    court_label = "District of Columbia Court of Appeals."

    def find_footnote_separator(self, page):
        """DC draws its footnote separator as a 2-inch (144pt) rule at the left
        body margin, and sets the footnote text at the SAME 14pt as the body.

        Both halves of the generic discriminator therefore fail: there is no
        smaller-than-body text below the rule to recognize, and the bottom-half
        position fence rejects the rule outright once a footnote is long enough
        to push its own separator up the page (brooks footnote 3 runs 20 lines,
        putting the rule at y≈390 on a 792pt page). The court's rule signature
        is unmistakable on its own, so key on that and drop the fence — the
        footnote was landing in the body as a blockquote."""
        return self.footnote_sep_fixed_left_rule(page) or super().find_footnote_separator(
            page
        )

    def extract_headmatter(self, headmatter_segs, page1_rules=None):
        """Route the revision notice ('Notice: This opinion is subject to formal
        revision before publication ...') out of the headmatter into the dropped
        bucket — administrative furniture, not opinion content. It opens with
        'Notice:' and runs until the court banner."""
        hm = super().extract_headmatter(headmatter_segs, page1_rules=page1_rules)
        summary = hm.get("summary") or []
        notice, kept, in_notice = [], [], False
        for row in summary:
            if isinstance(row, dict):
                s = str(row.get("html") or row.get("text") or "").strip()
                plain = s
                for tag in ("<strong>", "</strong>", "<em>", "</em>"):
                    plain = plain.replace(tag, "")
            else:
                s = str(row).strip()
                plain = s
            if plain.lower().startswith("notice:"):
                in_notice = True
            if in_notice and "court of appeals" in plain.lower():
                in_notice = False  # banner — notice has ended
            if in_notice:
                notice.append(s)
            else:
                kept.append(row)
        if notice:
            hm["summary"] = kept
            hm["dropped"] = list(hm.get("dropped") or []) + [" ".join(notice)]
        return hm

    @staticmethod
    def _dc_per_curiam(text: str) -> bool:
        """A per curiam opinion opens with the court itself in the byline slot —
        'PER CURIAM: Petitioner Alicia Eckenrode seeks review of ...' — running
        inline with the text exactly like a named byline. Without it the whole
        opinion read as headmatter, and only the dissent (which does carry a
        named byline) came back as a writing.

        The announcement line above the opinion ('Opinion for the court PER
        CURIAM.') names the same court but is a pointer, not an opener; it
        leads with 'Opinion', so it cannot be taken here."""
        t = " ".join(text.strip().split())
        return t.upper().startswith("PER CURIAM:")

    # ------------------------------------------------------------- orders
    @classmethod
    def _is_order_heading(cls, text: str) -> bool:
        """The centered ALL-CAPS heading that opens a disciplinary order. DC
        letter-spaces it ('O R D E R'), which is why the solid-form test found
        nothing and these documents came back with no writing at all."""
        t = cls._squeeze_spaced(text.strip())
        return t in ("ORDER", "PER CURIAM ORDER")

    def find_authors(self, all_segments) -> list:
        self._order_start = None
        starts = super().find_authors(all_segments)
        if starts:
            return starts
        # No byline: a disciplinary ORDER (suspension, disbarment, reciprocal
        # discipline). The body opens at the centered 'O R D E R' heading and
        # the court signs 'PER CURIAM' on the last line, so there is no byline
        # anywhere for the normal pass to find.
        for i, (_p, seg, _k) in enumerate(all_segments):
            if seg and self._is_order_heading(self.line_plain_text(seg[0]).strip()):
                self._order_start = i
                return [i]
        return []

    def split_author_line(self, line):
        if getattr(self, "_order_start", None) is not None:
            # The heading is not a byline — it is the order's own title, and
            # the court is the author.
            return "PER CURIAM", [line]
        return super().split_author_line(line)

    def classify_document_type(self, all_segments, author_indices, n_pages):
        if getattr(self, "_order_start", None) is not None:
            from ..models import DocType

            return DocType.ORDER
        return super().classify_document_type(all_segments, author_indices, n_pages)

    def extract(self, pdf_path: str):
        self._order_start = None
        doc = super().extract(pdf_path)
        if self._order_start is not None and doc.opinions:
            doc.opinions[0].type = "order"
            self._harvest_per_curiam(doc)
        return doc

    def _harvest_per_curiam(self, doc) -> None:
        """Lift the trailing 'PER CURIAM' off the order body into the Signature
        section — it is the court subscribing the order, not a body paragraph."""
        op = doc.opinions[-1]
        if not op.blocks:
            return
        last = " ".join(self._untag(op.blocks[-1].text).split()).upper()
        if last == "PER CURIAM":
            doc.signature = [str(op.blocks[-1].text)]
            op.blocks = op.blocks[:-1]

    @staticmethod
    def _untag(text: str) -> str:
        out, i, s = [], 0, str(text)
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

    def _dc_parse(self, text: str):
        """Return (name, title, kind) or None."""
        text = text.strip()
        if self._dc_per_curiam(text):
            return "PER CURIAM", "per curiam", None
        if text.upper().startswith("BEFORE ") or "," not in text:
            return None
        name = text.split(",", 1)[0].strip()
        if not _is_byline_name(name):
            return None
        rest = text.split(",", 1)[1].strip()
        title = next((t for t in _TITLES if rest.startswith(t)), None)
        if title is None:
            return None
        # After the title comes ': <body>' (majority) or ', <kind>: <body>'.
        low = rest[len(title) :].lower()
        if "concur" in low[:30] and "dissent" in low[:30]:
            kind = "concurring in part and dissenting in part"
        elif "concur" in low[:30]:
            kind = "concurring"
        elif "dissent" in low[:30]:
            kind = "dissenting"
        else:
            kind = None
        return name, title, kind

    def parse_author_line(self, text):
        r = self._dc_parse(text)
        if r is not None:
            return r
        return super().parse_author_line(text)

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        if self._dc_parse(text) is None:
            return super()._byline_split(line)
        ci = text.find(":")
        if ci == -1:
            return text, ""
        return text[: ci + 1], text[ci + 1 :].strip()
