"""Shared base for state supreme courts whose byline abbreviates the justice
title to 'J.' / 'C.J.' / 'P.J.' after an all-caps surname:

    'GAZIANO, J. This case arises ...'      (Massachusetts; space + inline body)
    'GONZÁLEZ, J.—Our constitutional ...'    (Washington; em-dash + inline body)
    'DEWINE, J.'                             (Ohio; standalone, bold)
    'BOLDEN, J.'                             (Michigan; standalone, bold)
    'BOLDEN, J. (concurring).'               (concurrence/dissent kind clause)
    'STEGALL, J.: Bethany King ...'          (Kansas; colon + inline body)
    'TARWATER, J., delivered the opinion ...' (Tennessee; opt-in prose byline)

The all-caps surname plus the abbreviated title is the discriminator, so no
bold requirement is needed by default (Massachusetts and Washington bylines are
not bold) — courts whose body could otherwise collide set ``require_bold_byline``
to lean on the bold tell as well. A lower-court judge ('Michael K. Callan, J.')
is rejected because its name is title-case, and a 'Present: Budd, C.J., ...'
panel roster is rejected because the text before the title is not a clean
surname.
"""

from __future__ import annotations

from ._statesupreme import StateSupreme, _is_byline_name

# Longest-first so 'C.J.'/'P.J.' win over the bare 'J.'. Spaced variants
# ('C. J.' / 'P. J.') are listed too — Connecticut spaces the abbreviation.
_ABBREV = (
    ("C.J.", "Chief Justice"),
    ("C. J.", "Chief Justice"),
    ("P.J.", "Presiding Justice"),
    ("P. J.", "Presiding Justice"),
    ("J.", "Justice"),
)
_KIND_WORDS = ("concur", "dissent")
# Verbs that turn an otherwise-rejected comma-continuation into a real byline,
# on courts that announce authorship in prose ('NAME, J., delivered the opinion
# of the Court, in which ...'). Opt-in via ``accept_delivered`` so the default
# (Mass./Wash./Ohio/Mich.) still treats a comma-continuation as a roster.
_DELIVER_VERBS = ("delivered", "filed", "authored", "announced", "wrote")


class AbbrevTitleSupreme(StateSupreme):
    # Set True for courts whose real byline is bold (Ohio, Michigan): it lets a
    # non-bold authorship summary ('DEWINE, J., authored the opinion ...') be
    # ignored while the bold 'DEWINE, J.' byline is kept.
    require_bold_byline = False
    # Set True for courts whose opinion byline IS the prose authorship line
    # ('NAME, J., delivered the opinion of the Court, in which ...'), with no
    # separate short byline (Tennessee). Leave False where such a line is only
    # a summary above a real short byline (would otherwise double-count).
    accept_delivered = False
    # Set True for courts whose byline opens with a paragraph number
    # ('¶ 1. EATON, J. ...' / '¶1 NAME, J. ...'): the marker is stripped for
    # parsing but kept in the byline text (Vermont, Wisconsin).
    strip_para_marker = False
    # Set True for courts whose surname is title-case, not all-caps, before the
    # abbreviated title ('Papik, J.' — Nebraska).
    allow_titlecase_name = False

    def _name_ok(self, name: str) -> bool:
        if _is_byline_name(name):
            return True
        if not self.allow_titlecase_name:
            return False
        toks = name.split()
        if not toks or len(toks) > 4:
            return False
        return all(
            t[:1].isupper() and t.rstrip(".").replace("'", "").isalpha() for t in toks
        )

    @staticmethod
    def _para_marker_len(text: str) -> int:
        """Length of a leading '¶ N.' / '¶N' paragraph marker (0 if none)."""
        if not text.startswith("¶"):
            return 0
        i, n = 1, len(text)
        while i < n and text[i] == " ":
            i += 1
        while i < n and (text[i].isdigit() or text[i] == "."):
            i += 1
        while i < n and text[i] == " ":
            i += 1
        return i

    def _abbrev_parse(self, text: str):
        """Parse an abbreviated-title byline. Return
        (name, title, kind, byline_end) or None, where ``byline_end`` is the
        index in ``text`` just past the byline clause (the rest is inline body).
        """
        text = text.strip()
        if "," not in text:
            return None
        name = text.split(",", 1)[0].strip()
        if not self._name_ok(name):
            return None
        after = text.split(",", 1)[1].lstrip()
        for ab, full in _ABBREV:
            if not after.startswith(ab):
                continue
            end = text.find(ab) + len(ab)
            tail = text[end:].lstrip()
            low = tail.lower()
            nxt = tail[:1]
            # ': ' colon form ('STEGALL, J.: Bethany King ...') — the colon
            # joins the byline; the opinion text follows it (Kansas).
            if nxt == ":":
                ci = text.find(":", end)
                return name, full, None, ci + 1
            # ', concurring.' / ' (dissenting)' kind clause — the kind word must
            # come DIRECTLY after the comma/paren. A prose continuation that
            # merely contains it later ('NAME, J., joins the foregoing opinion
            # concurring in part ...' — a joinder) is not a byline.
            head = tail.lstrip(", (").lower()
            if nxt in (",", "(") and any(head.startswith(k) for k in _KIND_WORDS):
                stop = next((k for k in range(end, len(text)) if text[k] in ".)"), -1)
                if stop != -1:
                    if (
                        text[stop] == ")"
                        and stop + 1 < len(text)
                        and text[stop + 1] == "."
                    ):
                        stop += 1
                    kind = text[end : stop + 1].strip(" .()—–,")
                    return name, full, kind, stop + 1
            # A bare comma-continuation after the title is normally a summary or
            # panel roster ('BOONSTRA, P.J., and ... JJ.'), NOT a byline — unless
            # this court announces authorship in prose and the continuation is an
            # opinion verb ('TARWATER, J., delivered the opinion of the Court').
            if nxt == ",":
                if self.accept_delivered:
                    verb = (low.lstrip(", ").split() or [""])[0]
                    if verb in _DELIVER_VERBS:
                        kind = (
                            "concurring"
                            if "concurr" in low
                            else "dissenting" if "dissent" in low else None
                        )
                        return name, full, kind, len(text)
                return None
            return name, full, None, end
        return None

    def _byline_split(self, line):
        text = self.line_plain_text(line).strip()
        chars = line.get("chars") or []
        if not text or not chars:
            return None
        # A leading paragraph marker is not part of the byline grammar; parse
        # the text after it, but keep the marker in the returned byline so the
        # paragraph number still appears in the output.
        m = self._para_marker_len(text) if self.strip_para_marker else 0
        body_off, rest = m, text[m:]
        if (
            self.require_bold_byline
            and "bold" not in chars[0].get("fontname", "").lower()
        ):
            return None
        # A genuine per-curiam byline is set in caps ('PER CURIAM' / 'PER
        # CURIAM: <body>'); match the literal so a wrapped body line that merely
        # opens with the words 'per curiam opinion' (prose about a lower court's
        # per curiam) is not mistaken for one.
        if rest.startswith("PER CURIAM"):
            # 'PER CURIAM.' or 'PER CURIAM: <body>' — end the byline at the
            # first '.'/':' (a colon comes before the body's first sentence
            # period, so it wins where the court uses the colon form).
            ends = [rest.find(c) for c in ".:" if rest.find(c) != -1]
            i = min(ends) if ends else -1
            if i == -1:
                return text, ""
            return text[: body_off + i + 1], rest[i + 1 :].strip()
        r = self._abbrev_parse(rest)
        if r is None:
            return None
        _name, _title, _kind, end = r
        return text[: body_off + end], rest[end:].lstrip(" —–")

    def parse_author_line(self, text):
        if self.strip_para_marker:
            text = text[self._para_marker_len(text) :]
        r = self._abbrev_parse(text)
        if r is not None:
            name, title, kind, _end = r
            return name, title, kind
        return super().parse_author_line(text)
