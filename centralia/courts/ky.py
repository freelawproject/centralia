"""Supreme Court of Kentucky.

The lead opinion is an opinion-of-the-court heading naming the author after the
title: 'OPINION OF THE COURT BY JUSTICE CONLEY' / 'OPINION OF THE COURT BY CHIEF
JUSTICE BISIG' / 'CONCURRING OPINION BY JUSTICE KELLER'. Like Hawaiʻi's 'OPINION
OF THE COURT BY GINOZA, J.' form, but Kentucky carries the spelled-out title
('JUSTICE'/'CHIEF JUSTICE') before the surname, which is stripped to the name.

Separate writings are signed differently — an ALL-CAPS surname, an abbreviated
title, the kind, and a colon, running inline with the opinion text: 'NICKELL,
J., DISSENTING: Respectfully, I dissent ...' / 'THOMPSON, J., CONCURRING BY
SEPARATE OPINION: ...' / 'BISIG, J., CONCURRING IN PART, DISSENTING IN PART:
...'. The ALL-CAPS surname distinguishes the byline from the lead opinion's
lowercase announcement of it ('Nickell, J., dissents by separate opinion ...').
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, is_caps_name

# Longest-first so the part/dissent compound wins over the bare forms.
_KY_BYLINES = (
    (
        "CONCURRING IN PART AND DISSENTING IN PART OPINION BY",
        "concurring in part and dissenting in part",
    ),
    ("CONCURRING IN RESULT OPINION BY", "concurring in result"),
    ("CONCURRING OPINION BY", "concurring"),
    ("DISSENTING OPINION BY", "dissenting"),
    ("OPINION OF THE COURT BY", None),
    ("OPINION AND ORDER BY", None),
    ("OPINION BY", None),
)
_KY_TITLES = ("CHIEF JUSTICE", "JUSTICE")


class KentuckySupreme(StateSupreme):
    court_id = "ky"
    court_label = "Supreme Court of Kentucky."

    def extract_page_images(self, page) -> list:
        """Kentucky slip opinions carry a court-seal watermark image centered
        on every page (the same 'Im2' object, 363x294 at x≈124/top≈249). The
        body text is drawn over it, so cropping the image region rasterizes
        that text back in — making the harvested 'image' look like page
        content. The full text layer is intact, so don't render any image
        back: drop them all."""
        return []

    # ------------------------------------------------------- byline parsing
    def parse_author_line(self, text):
        t = text.strip().rstrip(".")
        up = t.upper()
        for prefix, kind in _KY_BYLINES:
            if not up.startswith(prefix):
                continue
            name = t[len(prefix):].strip()
            upn = name.upper()
            for title in _KY_TITLES:
                if upn.startswith(title + " "):
                    name = name[len(title) + 1:].strip()
                    break
            name = name.split(",")[0].strip()
            if name:
                return name, "Justice", kind
        sep = self._ky_separate(text)
        if sep is not None:
            return sep[0], "Justice", sep[1]
        return super().parse_author_line(text)

    @staticmethod
    def _ky_separate(text: str):
        """Parse an in-body separate-writing byline ('NICKELL, J., DISSENTING:')
        -> (name, kind, byline_end_index), or None. The surname must be ALL-CAPS
        (the lowercase 'Nickell, J., dissents ...' announcement is not a byline)
        and the title abbreviated ('J.' / 'C.J.')."""
        ci = text.find(":")
        if ci == -1:
            return None
        parts = [p.strip() for p in text[:ci].split(",")]
        if len(parts) < 3:
            return None
        name, title = parts[0], parts[1].replace(".", "").upper()
        if title not in ("J", "CJ") or not is_caps_name(name):
            return None
        kind_text = " ".join(parts[2:]).upper()
        has_c, has_d = "CONCURRING" in kind_text, "DISSENTING" in kind_text
        if has_c and has_d:
            kind = "concurring in part and dissenting in part"
        elif has_d:
            kind = "dissenting"
        elif has_c:
            kind = "concurring"
        else:
            return None
        return name, kind, ci + 1

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        sep = self._ky_separate(text)
        if sep is not None:
            end = sep[2]
            return text[:end], text[end:].strip()
        return super()._byline_split(line)
