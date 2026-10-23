#!/usr/bin/env python3
"""vocab.py - everyday colour words for search.py, read as measurable colour properties.

A query like "ocean", "pastel pink", "coffee" or "dark moody" names no palette in the data, but it does
describe colours. This table says what each word means in OKLCH terms, so search.py can find palettes by
their colours instead of by the words in their titles. search.py prints how every word was read
("read 'ocean' as colours blue or teal"), and the agent repeats that to the user: it is an
interpretation, not a fact about the source.

  spec        one colour: hue buckets (colorlib.hue_bucket) or a hue arc in degrees (lo > hi wraps
              through 0), plus optional L and C ranges.
  COLOURS     colour nouns -> specs. A palette matches when any of its colours fits any spec; the
              area share of its colours that fit ranks it.
  COMPOUNDS   two-word colour names ("sky blue", "forest green"), looked up before single words.
  MODIFIERS   light, dark, pale, muted, vivid, ... narrow the colour word that follows ("dark green":
              green with L <= 0.50). On their own they set a palette band ("a dark palette").
  THEMES      scenes, materials and styles -> colour groups and/or palette conditions (lightness band,
              chroma band, L range, tone family, number of hue families), plus moods that rank matches higher.
              A palette holding colours from more of a theme's groups ranks higher.

Product categories (fintech, bakery, SaaS, dashboard) are deliberately absent: they say nothing about
colour, and mapping them would bake in the clichés the skill exists to avoid (fintech = blue). The agent
translates a brief into colour words first.
"""
from __future__ import annotations

FULL = (0.0, 1.01)


def spec(hue=None, arc=None, L=None, C=None) -> dict:
    """hue: a bucket name or a tuple of them; arc: (lo, hi) degrees; L, C: (lo, hi) ranges."""
    buckets = (hue,) if isinstance(hue, str) else hue
    return {"buckets": frozenset(buckets) if buckets else None, "arc": arc, "L": L, "C": C}


# --------------------------------------------------------------------------- colour nouns

_burgundy = [spec(arc=(340, 40), L=(0.0, 0.45), C=(0.05, 1))]
_terracotta = [spec(arc=(25, 55), L=(0.38, 0.68), C=(0.08, 1))]
_mustard = [spec(arc=(65, 100), L=(0.55, 0.82), C=(0.08, 1))]
_olive = [spec(arc=(90, 125), L=(0.35, 0.68), C=(0.04, 0.15))]
_sage = [spec(arc=(110, 170), L=(0.55, 0.85), C=(0.02, 0.08))]
_mint = [spec(arc=(140, 185), L=(0.78, 1.01), C=(0.04, 0.16))]
_navy = [spec(hue="blue", L=(0.0, 0.42))]
_cobalt = [spec(hue="blue", C=(0.12, 1))]
_lilac = [spec(hue="purple", L=(0.65, 1.01))]
_plum = [spec(arc=(290, 350), L=(0.0, 0.50), C=(0.05, 1))]
_beige = [spec(arc=(55, 110), L=(0.78, 0.96), C=(0.02, 0.08))]
_cream = [spec(arc=(60, 115), L=(0.88, 1.01), C=(0.015, 0.08))]
_tan = [spec(arc=(55, 110), L=(0.62, 0.85), C=(0.03, 0.10))]
_slate = [spec(arc=(200, 290), L=(0.35, 0.65), C=(0.01, 0.07))]
_black = [spec(L=(0.0, 0.27), C=(0.0, 0.06))]
_white = [spec(L=(0.93, 1.01), C=(0.0, 0.04))]
_charcoal = [spec(L=(0.18, 0.42), C=(0.0, 0.05))]
_earth = [spec(arc=(35, 115), L=(0.25, 0.75), C=(0.02, 0.13))]
_coffee_brown = [spec(arc=(40, 80), L=(0.20, 0.55), C=(0.02, 0.10))]

COLOURS: dict[str, tuple[str, list[dict]]] = {  # word -> (how it is read, specs)
    "red": ("red", [spec(hue="red")]),
    "crimson": ("saturated red", [spec(hue="red", C=(0.14, 1))]),
    "scarlet": ("saturated red", [spec(hue="red", C=(0.14, 1))]),
    "vermilion": ("orange-red, saturated (hue 25-45)", [spec(arc=(25, 45), C=(0.14, 1))]),
    "burgundy": ("dark red (L <= 0.45)", _burgundy),
    "maroon": ("dark red (L <= 0.45)", _burgundy),
    "wine": ("dark red (L <= 0.45)", _burgundy),
    "oxblood": ("dark red (L <= 0.45)", _burgundy),
    "orange": ("orange", [spec(hue="orange")]),
    "tangerine": ("saturated orange", [spec(hue="orange", C=(0.13, 1))]),
    "amber": ("amber (hue 60-85, L 0.60-0.85)", [spec(arc=(60, 85), L=(0.60, 0.85), C=(0.10, 1))]),
    "coral": ("coral (hue 20-50, L 0.62-0.85)", [spec(arc=(20, 50), L=(0.62, 0.85), C=(0.08, 1))]),
    "salmon": ("coral (hue 20-50, L 0.62-0.85)", [spec(arc=(20, 50), L=(0.62, 0.85), C=(0.08, 1))]),
    "peach": ("pale orange (hue 40-80, L >= 0.78)", [spec(arc=(40, 80), L=(0.78, 1.01), C=(0.04, 0.14))]),
    "apricot": ("pale orange (hue 40-80, L >= 0.78)", [spec(arc=(40, 80), L=(0.78, 1.01), C=(0.04, 0.14))]),
    "terracotta": ("terracotta / rust (hue 25-55, L 0.38-0.68)", _terracotta),
    "rust": ("terracotta / rust (hue 25-55, L 0.38-0.68)", _terracotta),
    "brick": ("terracotta / rust (hue 25-55, L 0.38-0.68)", _terracotta),
    "clay": ("terracotta / rust (hue 25-55, L 0.38-0.68)", _terracotta),
    "yellow": ("yellow", [spec(hue="yellow")]),
    "lemon": ("light saturated yellow", [spec(hue="yellow", L=(0.82, 1.01), C=(0.10, 1))]),
    "mustard": ("mustard / ochre (hue 65-100, L 0.55-0.82)", _mustard),
    "ochre": ("mustard / ochre (hue 65-100, L 0.55-0.82)", _mustard),
    "ocher": ("mustard / ochre (hue 65-100, L 0.55-0.82)", _mustard),
    "gold": ("gold (hue 75-100, L 0.60-0.88)", [spec(arc=(75, 100), L=(0.60, 0.88), C=(0.09, 1))]),
    "golden": ("gold (hue 75-100, L 0.60-0.88)", [spec(arc=(75, 100), L=(0.60, 0.88), C=(0.09, 1))]),
    "green": ("green", [spec(hue="green")]),
    "emerald": ("saturated green (hue 140-175)", [spec(arc=(140, 175), C=(0.10, 1))]),
    "olive": ("olive (hue 90-125, L 0.35-0.68)", _olive),
    "moss": ("olive (hue 90-125, L 0.35-0.68)", _olive),
    "sage": ("sage (grey-green, L 0.55-0.85, C <= 0.08)", _sage),
    "mint": ("mint (pale green, L >= 0.78)", _mint),
    "lime": ("lime (hue 110-145, light and saturated)", [spec(arc=(110, 145), L=(0.70, 1.01), C=(0.12, 1))]),
    "chartreuse": ("lime (hue 110-145, light and saturated)", [spec(arc=(110, 145), L=(0.70, 1.01), C=(0.12, 1))]),
    "teal": ("teal", [spec(hue="teal")]),
    "turquoise": ("light teal (L >= 0.60)", [spec(hue="teal", L=(0.60, 1.01))]),
    "aqua": ("light teal (L >= 0.60)", [spec(hue="teal", L=(0.60, 1.01))]),
    "cyan": ("light teal (L >= 0.60)", [spec(hue="teal", L=(0.60, 1.01))]),
    "blue": ("blue", [spec(hue="blue")]),
    "navy": ("dark blue (L <= 0.42)", _navy),
    "indigo": ("indigo (hue 250-300, L <= 0.48)", [spec(arc=(250, 300), L=(0.0, 0.48), C=(0.05, 1))]),
    "cobalt": ("saturated blue (C >= 0.12)", _cobalt),
    "cerulean": ("cerulean (hue 215-250)", [spec(arc=(215, 250), C=(0.08, 1))]),
    "azure": ("light blue (hue 215-255, L >= 0.60)", [spec(arc=(215, 255), L=(0.60, 1.01))]),
    "purple": ("purple", [spec(hue="purple")]),
    "violet": ("purple", [spec(hue="purple")]),
    "lilac": ("light purple (L >= 0.65)", _lilac),
    "lavender": ("light purple (L >= 0.65)", _lilac),
    "plum": ("plum (hue 290-350, L <= 0.50)", _plum),
    "aubergine": ("plum (hue 290-350, L <= 0.50)", _plum),
    "eggplant": ("plum (hue 290-350, L <= 0.50)", _plum),
    "mauve": ("mauve (greyed purple-pink, C <= 0.10)", [spec(arc=(290, 355), L=(0.50, 0.85), C=(0.03, 0.10))]),
    "magenta": ("magenta (hue 320-355, C >= 0.15)", [spec(arc=(320, 355), C=(0.15, 1))]),
    "fuchsia": ("magenta (hue 320-355, C >= 0.15)", [spec(arc=(320, 355), C=(0.15, 1))]),
    "pink": ("pink", [spec(hue="pink")]),
    "rose": ("rose (hue 350-30, L 0.55-0.85)", [spec(arc=(350, 30), L=(0.55, 0.85), C=(0.05, 0.16))]),
    "blush": ("pale pink (L >= 0.80)", [spec(hue="pink", L=(0.80, 1.01))]),
    "brown": ("brown", [spec(hue="brown")]),
    "chocolate": ("dark brown (L <= 0.42)", [spec(hue="brown", L=(0.0, 0.42))]),
    "tan": ("tan / camel (hue 55-110, L 0.62-0.85, C <= 0.10)", _tan),
    "camel": ("tan / camel (hue 55-110, L 0.62-0.85, C <= 0.10)", _tan),
    "khaki": ("tan / camel (hue 55-110, L 0.62-0.85, C <= 0.10)", _tan),
    "beige": ("beige / sand (hue 55-110, L 0.78-0.96, C <= 0.08)", _beige),
    "sand": ("beige / sand (hue 55-110, L 0.78-0.96, C <= 0.08)", _beige),
    "oat": ("beige / sand (hue 55-110, L 0.78-0.96, C <= 0.08)", _beige),
    "linen": ("beige / sand (hue 55-110, L 0.78-0.96, C <= 0.08)", _beige),
    "ecru": ("beige / sand (hue 55-110, L 0.78-0.96, C <= 0.08)", _beige),
    "cream": ("cream / ivory (L >= 0.88, warm tint)", _cream),
    "ivory": ("cream / ivory (L >= 0.88, warm tint)", _cream),
    "gray": ("grey (a neutral, L 0.30-0.85)", [spec(hue="neutral", L=(0.30, 0.85))]),
    "slate": ("slate (blue-grey, L 0.35-0.65, C <= 0.07)", _slate),
    "charcoal": ("charcoal (L 0.18-0.42, C <= 0.05)", _charcoal),
    "black": ("black / ink (L <= 0.27)", _black),
    "ink": ("black / ink (L <= 0.27)", _black),
    "sumi": ("black / ink (L <= 0.27)", _black),
    "white": ("white (L >= 0.93, C <= 0.04)", _white),
    "chalk": ("white (L >= 0.93, C <= 0.04)", _white),
    "silver": ("silver (light neutral, L 0.70-0.92)", [spec(L=(0.70, 0.92), C=(0.0, 0.04))]),
    "neutral": ("a neutral (C < 0.04)", [spec(hue="neutral")]),
}

COMPOUNDS: dict[str, tuple[str, list[dict]]] = {
    "sky blue": ("light blue (L >= 0.70)", [spec(hue="blue", L=(0.70, 1.01), C=(0.03, 0.14))]),
    "baby blue": ("light blue (L >= 0.70)", [spec(hue="blue", L=(0.70, 1.01), C=(0.03, 0.14))]),
    "navy blue": ("dark blue (L <= 0.42)", _navy),
    "royal blue": ("saturated blue (C >= 0.12)", _cobalt),
    "slate blue": ("greyed blue (L 0.40-0.70, C 0.03-0.10)", [spec(hue="blue", L=(0.40, 0.70), C=(0.03, 0.10))]),
    "slate gray": ("slate (blue-grey, L 0.35-0.65, C <= 0.07)", _slate),
    "forest green": ("dark green (L <= 0.55)", [spec(hue="green", L=(0.0, 0.55))]),
    "olive green": ("olive (hue 90-125, L 0.35-0.68)", _olive),
    "sage green": ("sage (grey-green, L 0.55-0.85, C <= 0.08)", _sage),
    "mint green": ("mint (pale green, L >= 0.78)", _mint),
    "hot pink": ("saturated pink (C >= 0.15)", [spec(arc=(330, 10), L=(0.55, 0.85), C=(0.15, 1))]),
    "dusty rose": ("dusty rose (hue 350-40, L 0.55-0.80, C <= 0.10)", [spec(arc=(350, 40), L=(0.55, 0.80), C=(0.03, 0.10))]),
    "dusty pink": ("dusty rose (hue 350-40, L 0.55-0.80, C <= 0.10)", [spec(arc=(350, 40), L=(0.55, 0.80), C=(0.03, 0.10))]),
    "blood red": ("dark saturated red", [spec(hue="red", L=(0.0, 0.50), C=(0.12, 1))]),
    "brick red": ("terracotta / rust (hue 25-55, L 0.38-0.68)", _terracotta),
    "burnt orange": ("burnt orange (hue 40-65, L 0.50-0.70)", [spec(arc=(40, 65), L=(0.50, 0.70), C=(0.10, 1))]),
    "mustard yellow": ("mustard / ochre (hue 65-100, L 0.55-0.82)", _mustard),
    "lemon yellow": ("light saturated yellow", [spec(hue="yellow", L=(0.82, 1.01), C=(0.10, 1))]),
    "off white": ("off-white (L 0.90-0.99, C <= 0.05)", [spec(L=(0.90, 0.99), C=(0.0, 0.05))]),
    "earth tone": ("earth tones (hue 35-115, L 0.25-0.75, C 0.02-0.13)", _earth),
    "earth tones": ("earth tones (hue 35-115, L 0.25-0.75, C 0.02-0.13)", _earth),
}

# --------------------------------------------------------------------------- modifiers

MODIFIERS: dict[str, dict] = {
    # L / C narrow a following colour word; lightness / chroma bands apply when the word stands alone
    "light": {"L": (0.70, 1.01), "lightness": {"light"}},
    "pale": {"L": (0.75, 1.01), "C": (0.0, 0.12), "lightness": {"light"}, "chroma": {"muted", "moderate"}},
    "soft": {"L": (0.65, 1.01), "C": (0.0, 0.12), "chroma": {"muted", "moderate"}},
    "pastel": {"L": (0.75, 1.01), "C": (0.02, 0.13), "lightness": {"light"}, "chroma": {"muted", "moderate"}},
    "airy": {"L": (0.75, 1.01), "lightness": {"light"}},
    "dark": {"L": (0.0, 0.50), "lightness": {"dark"}},
    "deep": {"L": (0.0, 0.55), "C": (0.06, 1), "lightness": {"dark", "mid"}},
    "rich": {"L": (0.0, 0.60), "C": (0.08, 1), "lightness": {"dark", "mid"}, "chroma": {"moderate", "vivid"}},
    "muted": {"C": (0.0, 0.10), "chroma": {"muted"}},
    "subdued": {"C": (0.0, 0.10), "chroma": {"muted"}},
    "desaturated": {"C": (0.0, 0.10), "chroma": {"muted"}},
    "understated": {"C": (0.0, 0.10), "chroma": {"muted"}},
    "faded": {"C": (0.0, 0.10), "chroma": {"muted"}},
    "grayish": {"C": (0.0, 0.08), "chroma": {"muted"}},
    "dusty": {"L": (0.45, 0.82), "C": (0.02, 0.10), "chroma": {"muted"}},
    "smoky": {"L": (0.0, 0.65), "C": (0.0, 0.08), "chroma": {"muted", "moderate"}},
    "smoked": {"L": (0.0, 0.65), "C": (0.0, 0.08), "chroma": {"muted", "moderate"}},
    "misty": {"L": (0.60, 1.01), "C": (0.0, 0.08), "chroma": {"muted"}},
    "hazy": {"L": (0.60, 1.01), "C": (0.0, 0.08), "chroma": {"muted"}},
    "foggy": {"L": (0.60, 1.01), "C": (0.0, 0.08), "chroma": {"muted"}},
    "vivid": {"C": (0.15, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "saturated": {"C": (0.15, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "vibrant": {"C": (0.15, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "punchy": {"C": (0.15, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "intense": {"C": (0.15, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "bright": {"L": (0.55, 1.01), "C": (0.13, 1), "lightness": {"mid", "light"}, "chroma": {"moderate", "vivid"}},
    "neon": {"C": (0.18, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "electric": {"C": (0.18, 1), "chroma": {"vivid"}, "moods": ["bold"]},
    "fluorescent": {"C": (0.18, 1), "chroma": {"vivid"}, "moods": ["bold"]},
}

# --------------------------------------------------------------------------- themes (scenes, materials, styles)


def theme(desc: str, *groups: list[dict], **conditions) -> dict:
    """groups: colour groups, each a list of specs; a palette that holds colours from more groups ranks higher (coffee
    browns *with* cream beat browns alone). conditions: needs (indices of groups the palette must hold: an ember is
    the glow, not the black around it), lightness / chroma (band sets), contrast (min L range), tone ('same'),
    min_hues, moods."""
    return {"desc": desc, "groups": [list(g) for g in groups], **conditions}


_ocean = theme("colours blue or teal", [spec(hue="blue")], [spec(hue="teal")], moods=["cool"])
_coastal = theme("colours teal, light blue or sand", [spec(hue="teal")], [spec(hue="blue", L=(0.60, 1.01))], _beige)
_night = theme("a dark palette with blue, purple or near-black", [spec(hue=("blue", "purple"))], [*_black, *_charcoal],
               lightness={"dark"})
_dusk = theme("colours purple, blue or pink at mid-to-dark lightness", [spec(hue="purple")], [spec(hue="blue")],
              [spec(hue="pink")], lightness={"dark", "mid"})
_sunset = theme("saturated orange, red, pink, yellow or purple (C >= 0.08)",
                *([spec(hue=h, C=(0.08, 1))] for h in ("orange", "red", "pink", "yellow", "purple")), moods=["warm"])
_sunrise = theme("colours orange, pink or light yellow", [spec(hue="orange")], [spec(hue="pink")],
                 [spec(hue="yellow", L=(0.70, 1.01))], moods=["warm"])
_forest = theme("colours green (L <= 0.60) or olive, with brown", [spec(hue="green", L=(0.0, 0.60)), *_olive],
                [spec(hue="brown")], moods=["earthy"])
_jungle = theme("saturated greens, teal, yellow or orange", [spec(hue=("green", "teal"), C=(0.10, 1))],
                [spec(hue=("yellow", "orange"), C=(0.12, 1))], chroma={"moderate", "vivid"})
_garden = theme("colours green", [spec(hue="green"), *_olive, *_sage])
_desert = theme("colours sand, terracotta, ochre or peach", _beige, _terracotta, _mustard,
                [spec(arc=(40, 80), L=(0.78, 1.01), C=(0.04, 0.14))], moods=["warm"])
_earthy = theme("earth tones (hue 35-115, L 0.25-0.75, C 0.02-0.13) or olive", [*_earth, *_olive], moods=["earthy"])
_coffee = theme("coffee browns (hue 40-80, L 0.20-0.55) with cream or tan", [*_coffee_brown, spec(hue="brown")], [*_cream, *_tan],
                needs=(0,), moods=["warm"])
_citrus = theme("saturated yellow, orange or lime", [spec(hue="yellow", C=(0.10, 1))], [spec(hue="orange", C=(0.12, 1))],
                [spec(arc=(110, 145), L=(0.70, 1.01), C=(0.12, 1))])
_candy = theme("pink, light purple or mint, at mid-to-light lightness", [spec(hue="pink")], _lilac, _mint,
               lightness={"mid", "light"}, moods=["playful"])
_icy = theme("light blue, light teal or white", [spec(hue=("blue", "teal"), L=(0.75, 1.01))], _white, moods=["cool"])
_luxury = theme("dark-to-mid palette with gold, dark red, navy, deep green or black",
                [spec(arc=(75, 100), L=(0.60, 0.88), C=(0.09, 1))], _burgundy, _navy,
                [spec(hue=("green", "teal"), L=(0.0, 0.50))], _black, lightness={"dark", "mid"}, moods=["refined"])
_vintage = theme("a muted-to-moderate palette (no vivid colour)", chroma={"muted", "moderate"}, moods=["refined", "warm"])
_retro = theme("mustard, burnt orange, brown, olive or mid teal", _mustard, [spec(arc=(40, 65), L=(0.50, 0.70), C=(0.10, 1))],
               [spec(hue="brown")], _olive, [spec(hue="teal", L=(0.40, 0.70))], moods=["warm"])
_moody = theme("a dark, muted-to-moderate palette", lightness={"dark"}, chroma={"muted", "moderate"}, moods=["solemn"])
_minimal = theme("a muted palette with neutrals", [spec(hue="neutral")], chroma={"muted", "moderate"}, moods=["austere"])
_mono = theme("a same-tone palette (all hues within 70 degrees)", tone="same")
_contrast = theme("a palette whose L range is at least 0.50", contrast=0.50)
_brutalist = theme("black, white or grey with an L range >= 0.50", _black, _white, [spec(hue="neutral")], contrast=0.50,
                   moods=["austere", "bold"])
_cozy = theme("warm browns, soft orange, cream or dark red", [spec(hue="brown")], [spec(hue="orange", L=(0.50, 0.85))],
              _cream, _burgundy, moods=["warm"])
_fresh = theme("light greens or teal", [spec(hue=("green", "teal"), L=(0.60, 1.01))], lightness={"mid", "light"})
_playful = theme("three or more hue families, moderate-to-vivid, mid-to-light", min_hues=3,
                 chroma={"moderate", "vivid"}, lightness={"mid", "light"}, moods=["playful"])
_colourful = theme("three or more hue families", min_hues=3, chroma={"moderate", "vivid"})
_cyber = theme("magenta, purple or teal, saturated, on a mid-to-dark palette", [spec(arc=(320, 355), C=(0.15, 1))],
               [spec(hue="purple", C=(0.12, 1))], [spec(hue="teal", C=(0.10, 1))], lightness={"dark", "mid"}, moods=["bold"])
# heat: the glow is a saturated warm colour; embers, forges and molten metal set it against black or iron grey
_hot = [spec(hue=("red", "orange"), C=(0.12, 1))]
_ember = theme("glowing red or orange (C >= 0.12) on a dark-to-mid palette with black", _hot, [*_black, *_charcoal],
               needs=(0,), lightness={"dark", "mid"}, moods=["warm"])
_glow = theme("warm light: orange, amber or gold (L >= 0.65, C >= 0.08)",
              [spec(hue=("orange", "yellow"), L=(0.65, 1.01), C=(0.08, 1))], moods=["warm"])
_fire = theme("saturated red, orange or yellow (C >= 0.12)", [spec(hue="red", C=(0.14, 1))], [spec(hue="orange", C=(0.12, 1))],
              [spec(hue="yellow", C=(0.12, 1))], chroma={"moderate", "vivid"}, moods=["warm", "bold"])
_molten = theme("vivid orange or red (C >= 0.15) with black", [spec(hue=("orange", "red"), C=(0.15, 1))], _black,
                needs=(0, 1), moods=["warm", "bold"])
_forge = theme("red-orange heat (C >= 0.12) with black or iron grey, on a dark-to-mid palette", _hot,
               [*_black, *_charcoal, spec(hue="neutral", L=(0.30, 0.70))], needs=(0,), lightness={"dark", "mid"},
               moods=["warm"])
_roasted = theme("dark warm browns with rust, on a dark-to-mid palette", [spec(hue="brown"), *_coffee_brown], _terracotta,
                 needs=(0,), lightness={"dark", "mid"}, moods=["warm"])

THEMES: dict[str, dict] = {
    **dict.fromkeys(("ocean", "sea", "marine", "nautical", "maritime", "underwater"), _ocean),
    **dict.fromkeys(("coastal", "beach", "seaside"), _coastal),
    "sky": theme("light blue", [spec(hue="blue", L=(0.65, 1.01))], moods=["cool"]),
    **dict.fromkeys(("night", "midnight", "nocturnal"), _night),
    **dict.fromkeys(("dusk", "twilight"), _dusk),
    "sunset": _sunset,
    **dict.fromkeys(("sunrise", "dawn"), _sunrise),
    **dict.fromkeys(("forest", "woodland", "woods", "pine"), _forest),
    **dict.fromkeys(("jungle", "tropical", "rainforest"), _jungle),
    **dict.fromkeys(("garden", "botanical", "leafy", "foliage", "greenery"), _garden),
    **dict.fromkeys(("desert", "dune", "dunes"), _desert),
    **dict.fromkeys(("earthy", "earth", "earthen", "terra"), _earthy),
    **dict.fromkeys(("coffee", "cafe", "espresso", "mocha", "latte", "roastery"), _coffee),
    "citrus": _citrus,
    **dict.fromkeys(("candy", "bubblegum", "sweets", "confectionery"), _candy),
    **dict.fromkeys(("icy", "ice", "frost", "frosty", "glacier", "arctic"), _icy),
    **dict.fromkeys(("luxury", "luxurious", "premium", "opulent", "lavish"), _luxury),
    **dict.fromkeys(("vintage", "antique", "heritage"), _vintage),
    **dict.fromkeys(("retro", "seventies"), _retro),
    **dict.fromkeys(("moody", "brooding"), _moody),
    **dict.fromkeys(("minimal", "minimalist"), _minimal),
    **dict.fromkeys(("monochrome", "monochromatic", "tonal"), _mono),
    **dict.fromkeys(("contrast", "contrasting"), _contrast),
    **dict.fromkeys(("brutalist", "brutalism"), _brutalist),
    **dict.fromkeys(("cozy", "cosy", "hygge"), _cozy),
    "fresh": _fresh,
    **dict.fromkeys(("fun", "cheerful", "happy", "joyful"), _playful),
    **dict.fromkeys(("colorful", "colourful", "multicolor", "multicolour", "rainbow"), _colourful),
    **dict.fromkeys(("cyberpunk", "synthwave", "vaporwave"), _cyber),
    **dict.fromkeys(("ember", "cinder", "coals", "smoulder", "smouldering", "smolder", "smoldering"), _ember),
    **dict.fromkeys(("glow", "glowing", "lamplight", "candlelight", "firelight", "lantern"), _glow),
    **dict.fromkeys(("fire", "fiery", "flame", "blaze", "blazing", "bonfire", "heat", "hot"), _fire),
    **dict.fromkeys(("molten", "lava", "magma"), _molten),
    **dict.fromkeys(("forge", "furnace", "foundry", "kiln"), _forge),
    **dict.fromkeys(("roasted", "roast", "toasted", "scorched", "burnt", "charred"), _roasted),
}
THEMES["high contrast"] = _contrast  # two words: looked up like COMPOUNDS

NEGATIONS = {"not", "no", "without", "avoid", "never", "non", "nothing", "anti"}
