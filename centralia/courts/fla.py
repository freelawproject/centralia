"""Supreme Court of Florida.

The byline comes in two forms: an unsigned ``PER CURIAM.`` opinion, or a signed
abbreviated-title byline with an all-caps surname (``GROSSHANS, J.`` /
``FRANCIS, J.`` / ``TANENBAUM, J., concurring.``). The abbreviated-title base
handles both — plain ``StateSupreme`` only recognized the spelled-out ``Justice``
title and PER CURIAM, so signed opinions came back with zero opinions (the body
then looked like it 'started on a later page')."""

from __future__ import annotations

from ._abbrevtitle import AbbrevTitleSupreme


class FloridaSupreme(AbbrevTitleSupreme):
    court_id = "fla"
    court_label = "Supreme Court of Florida."
    author_titles = ("Justice", "Chief Justice")
    # The opinion template draws a two-inch hairline at the body rail.  Notes
    # below it are often the same 14pt size as the body, so the generic
    # small-text discriminator is inapplicable; the exact rule geometry is the
    # authoritative boundary.
    footnote_sep_rect = (72.0, 216.0)

    def find_footnote_separator(self, page):
        # StateSupreme's family heuristic intentionally requires a rule in the
        # lower half. Florida's same-size notes can fill most of a page, moving
        # the fixed two-inch rule well above that cutoff. Match the template's
        # exact rail/width instead, wherever it occurs.
        for rule in list(page.rects) + list(page.lines):
            if (
                abs(rule.get("height", 0)) < 2
                and abs(rule.get("x0", 0) - 72.0) <= 1
                and abs(rule.get("x1", 0) - 216.0) <= 1
            ):
                if hasattr(self, "_fla_footnote_pages"):
                    self._fla_footnote_pages.add(page.page_number)
                return rule["top"]
        return None

    def extract(self, pdf_path):
        self._unsigned_start_line = None
        self._fla_running_furniture = []
        self._fla_footnote_pages = set()
        doc = super().extract(pdf_path)
        if self._fla_running_furniture:
            furniture = list(dict.fromkeys(self._fla_running_furniture))
            doc.dropped = list(doc.dropped) + furniture
            folded = {text.casefold() for text in furniture}
            doc.residual = [
                item
                for item in doc.residual
                if str(item.get("text", "")).casefold() not in folded
            ]
        labels = {
            footnote.label
            for opinion in doc.opinions
            for footnote in opinion.footnotes
        }
        doc.residual = [
            item
            for item in doc.residual
            if not self._returned_dotted_footnote_label(item, labels)
        ]
        # The court's issuance/certification sheet begins at A TRUE COPY and
        # can continue onto another page with a service list.  Preserve it as
        # ending matter, including the seal/signature image.
        if doc.opinions:
            blocks = doc.opinions[-1].blocks
            cut = next(
                (
                    i
                    for i, block in enumerate(blocks)
                    if block.kind != "image"
                    and self._ending_matter_starter(block.text)
                ),
                None,
            )
            if cut is not None:
                # Panel-participation rows immediately before the finality /
                # provenance section are ending matter too.  Keep the court's
                # dispositive "It is so ordered." as the last body paragraph.
                while cut > 0 and self._panel_participation(blocks[cut - 1].text):
                    cut -= 1
                doc.trailer = list(doc.trailer) + blocks[cut:]
                doc.opinions[-1].blocks = blocks[:cut]
        return doc

    @staticmethod
    def _plain_block_text(text):
        plain = (
            text.lower()
            .replace("<strong>", "")
            .replace("</strong>", "")
            .replace("<em>", "")
            .replace("</em>", "")
            .strip()
        )
        if plain.startswith("<pagenumber"):
            end = plain.find("/>")
            if end != -1:
                plain = plain[end + 2 :].lstrip()
        return plain

    def _ending_matter_starter(self, text):
        plain = self._plain_block_text(text)
        return plain.startswith(
            (
                "a true copy",
                "not final until time expires",
                "an appeal from",
                "an original proceeding",
            )
        )

    def _panel_participation(self, text):
        plain = self._plain_block_text(text)
        judicial_titles = ("j.,", "jj.,", "c.j.,", "p.j.,")
        dispositions = (
            " concur",
            " dissent",
            " did not participate",
            " recused",
        )
        return any(title in plain for title in judicial_titles) and any(
            disposition in plain for disposition in dispositions
        )

    def _returned_dotted_footnote_label(self, item, labels):
        if item.get("page") not in self._fla_footnote_pages:
            return False
        text = str(item.get("text", "")).lstrip()
        before, dot, _after = text.partition(".")
        return bool(dot and before.isdigit() and before in labels)

    @staticmethod
    def _word_page_number(text):
        words = text.strip().lower().replace("-", " ").split()
        if not words or words[0] != "page":
            return None
        ones = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19,
        }
        tens = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
        tail = words[1:]
        if len(tail) == 1:
            value = ones.get(tail[0], tens.get(tail[0]))
        elif len(tail) == 2 and tail[0] in tens and tail[1] in ones:
            value = tens[tail[0]] + ones[tail[1]]
        else:
            value = None
        return str(value) if value is not None else None

    def detect_printed_folio(self, page, lines):
        for line in page.extract_text_lines():
            value = self._word_page_number(line.get("text") or "")
            if value is not None and line.get("top", 999) < 130:
                return value
        return super().detect_printed_folio(page, lines)

    def page_lines(self, page):
        if not hasattr(self, "_fla_running_furniture"):
            self._fla_running_furniture = []
        lines = super().page_lines(page)
        kept = []
        for line in lines:
            text = self.line_plain_text(line).strip()
            running = (
                page.page_number > 1
                and line.get("top", 999) < 110
                and (
                    text.upper().startswith(("CASE NO.:", "CASE NOS.:"))
                    or self._word_page_number(text) is not None
                )
            )
            if running:
                self._fla_running_furniture.append(text)
            else:
                kept.append(line)
        return kept

    def find_authors(self, all_segments):
        starts = super().find_authors(all_segments)
        # Removing a top running header can leave a byline and its opening
        # prose in one segment. StateSupreme's signature guard examines only
        # later segments and can then discard the writing. An explicit Florida
        # concurrence/dissent byline with prose following in the same segment
        # is necessarily an opinion start, not a signature.
        for i, (_page, seg, _kind) in enumerate(all_segments):
            if not seg or i in starts:
                continue
            parsed = self.parse_author_line(self.line_plain_text(seg[0]).strip())
            if parsed is not None and parsed[2] is not None and len(seg) > 1:
                starts.append(i)
        starts.sort()
        self._unsigned_start_line = None
        # Some short constitutional-writ rulings are unsigned.  The caption
        # ends at the final party-role row; prose immediately following it is
        # the principal ruling, before any separately authored writings.
        role_at = None
        for i, (_page, seg, _kind) in enumerate(all_segments):
            if any(
                self.line_plain_text(line).strip().lower()
                in (
                    "petitioner", "petitioner(s)",
                    "respondent", "respondent(s)",
                    "complainant", "complainant(s)",
                    "appellant", "appellant(s)",
                    "appellee", "appellee(s)",
                )
                for line in seg
            ):
                role_at = i
        if role_at is not None and role_at + 1 < len(all_segments):
            candidate = role_at + 1
            if not starts or candidate < starts[0]:
                self._unsigned_start_line = all_segments[candidate][1][0]
                starts = [candidate] + starts
        return starts

    def split_author_line(self, line):
        if line is getattr(self, "_unsigned_start_line", None):
            return "PER CURIAM.", [line]
        return super().split_author_line(line)

    def detect_footnote_label(self, line):
        label = super().detect_footnote_label(line)
        if label is not None:
            return label
        # Same-size Florida notes use a hanging `1.` / `12.` label at x≈108.
        # This method sees only lines already below the exact separator, so a
        # dotted body enumeration cannot be confused for a note.
        if line.get("x0", 0) < self.body_baseline_x0 + 24:
            return None
        text = self.line_plain_text(line).lstrip()
        digits = []
        for char in text:
            if char.isdigit():
                digits.append(char)
            else:
                break
        if digits and text[len(digits) :].startswith("."):
            return "".join(digits)
        return None

    def build_footnote(self, label, lines):
        footnote = super().build_footnote(label, lines)
        # The generic builder removes superscript <footnotemark> labels.  The
        # same-size dotted form is plain text and needs the equivalent trim.
        if footnote.paragraphs:
            tag, text = footnote.paragraphs[0]
            prefix = f"{label}."
            if text.lstrip().startswith(prefix):
                pos = text.find(prefix)
                text = text[:pos] + text[pos + len(prefix) :].lstrip()
                footnote.paragraphs[0] = (tag, text)
        return footnote

    # Style-preserving headmatter (the large banner, bold party names, italic
    # posture lines, section rules) — the shared 'Florida look' helper.
    def extract_headmatter(self, headmatter_segs, page1_rules=None) -> dict:
        return self._styled_headmatter(headmatter_segs, page1_rules)

    # Announcement lines that sit above the separate writings ('TANENBAUM, J.,
    # dissents with an opinion.' / 'GROSSHANS, J., concurs with an opinion.' /
    # 'TANENBAUM, J., did not participate.') are not opinion starts — the real
    # writing opens with the participle ('... dissenting.' / '... concurring.').
    @staticmethod
    def _is_announcement(text: str) -> bool:
        low = text.lower()
        return "with an opinion" in low or "did not participate" in low

    def parse_author_line(self, text):
        if self._is_announcement(text):
            return None
        if ", specially concurring." in text.lower():
            start = text.lower().find(", specially concurring.")
            normalized = text[:start] + ", concurring." + text[
                start + len(", specially concurring.") :
            ]
            return super().parse_author_line(normalized)
        return super().parse_author_line(text)

    def _byline_split(self, line):
        if self._is_announcement(self.line_plain_text(line)):
            return None
        return super()._byline_split(line)
