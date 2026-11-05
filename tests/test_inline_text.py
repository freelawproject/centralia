"""inline_text: the line's inline markup rebuilt from its glyphs."""
import pytest

from centralia.pdfio.text import inline_text

ROMAN = "Times-Roman"
ITALIC = "Times-Italic"
BOLD_ITALIC = "Times-BoldItalic"


def _chars(*runs):
    """Glyphs for ``(text, fontname[, options])`` runs, set left to right
    with a 3pt word gap on each space. ``options`` may give ``gap`` (extra
    space before the run's first glyph, e.g. an italic overhang) and
    ``underline``."""
    chars, x = [], 0.0
    for text, font, *rest in runs:
        opts = rest[0] if rest else {}
        x += opts.get("gap", 0.0)
        for ch in text:
            if ch == " ":
                x += 3.0
                continue
            c = {"text": ch, "fontname": font, "x0": x, "x1": x + 5.0}
            if opts.get("underline"):
                c["_underline"] = True
            chars.append(c)
            x += 5.0
    return chars


def _inline(*runs):
    return inline_text(_chars(*runs), set(), lambda t: t, None)


# #48: SCOTUS sets the period of 'Id.' in roman; eyecite only reads the
# period inside the styled run as a short-form citation. (A word break after
# a styled run lands inside it, '<em>Id. </em>at', as for every other run.)

@pytest.mark.parametrize("word", ["Id", "id", "Ibid", "ibid"])
def test_roman_period_joins_italic_id(word):
    assert _inline(("See ", ROMAN), (word, ITALIC), (". at 745.", ROMAN)) == \
        f"See <em>{word}. </em>at 745."


def test_overhang_gap_before_the_period_is_not_a_word_break():
    # montana v. planned parenthood: 4.7pt between the italic 'd' and '.'
    # used to print '<em>Ibid </em>.'
    assert _inline(("parents. ", ROMAN), ("Ibid", ITALIC),
                   (". Similarly", ROMAN, {"gap": 4.7})) == \
        "parents. <em>Ibid. </em>Similarly"


def test_roman_period_joins_underlined_id():
    # ca1 underlines its signals: '<u>Id</u>.'
    assert _inline(("record. ", ROMAN), ("Id", ROMAN, {"underline": True}),
                   (".", ROMAN)) == "record. <u>Id.</u>"


def test_roman_period_joins_bold_italic_id():
    assert _inline(("Id", BOLD_ITALIC), (".", ROMAN)) == \
        "<strong><em>Id.</em></strong>"


@pytest.mark.parametrize("lead", ["See id", "(id", "“Id"])
def test_roman_period_joins_id_after_other_italics(lead):
    assert _inline((lead, ITALIC), (".", ROMAN)) == f"<em>{lead}.</em>"


def test_italic_period_unchanged():
    assert _inline(("Id.", ITALIC), (", at 745.", ROMAN)) == \
        "<em>Id.</em>, at 745."


@pytest.mark.parametrize("words", ["Smith v. Jones", "Rapid", "Idaho", "Ide"])
def test_period_after_other_italics_stays_roman(words):
    assert _inline((words, ITALIC), (".", ROMAN)) == f"<em>{words}</em>."


def test_roman_id_is_untouched():
    assert _inline(("Id. at 745.", ROMAN)) == "Id. at 745."
