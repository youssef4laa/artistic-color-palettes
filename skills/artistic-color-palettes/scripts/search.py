#!/usr/bin/env python3
"""search.py - find palettes in data/palettes.csv (Wada plates, editorial palettes, paintings, kasane).

Ranking is BM25-lite (k1 1.5, b 0.75) over title, colour names, moods, hue, era, season and the
provenance label, plus measured colour matches for everyday colour words (scripts/vocab.py). Hard
filters: --count --mood --hue --lightness --chroma --near --era --source-type --season. Nothing is
ever invented: an unknown id, a plate number outside 1-348 or a request for Wada's Vol. 2 gets a
plain "not in the data" message and a non-zero exit; a query with no match says so and returns
nothing (it never pads with unrelated rows).

Choices a user of this script should know:
  * Everyday colour words are read as colour properties (vocab.py): colour nouns (teal, navy, olive, cream), modifiers that
    narrow the next colour word or set a palette band (dark green; pastel; muted), and scenes or styles (ocean, coffee,
    sunset, luxury, moody). Each reading is printed ("read 'ocean' as ...") and is an interpretation to pass on, not a fact
    about the source. A word after not / no / without / avoid is not searched; the script says so.
  * --hue matches every hue the palette contains (data column hues, measured from the hex values; teal is its own bucket),
    so "--hue blue" finds a plate with one blue colour; plates with more blue rank higher.
  * --lightness bands the area-weighted mean OKLCH L (dark < 0.50 <= mid < 0.72 <= light); --chroma bands the most
    saturated colour's C (muted < 0.11 <= moderate < 0.17 <= vivid). Both also take numeric ranges such as 0.6-0.8.
    Area weights: paintings by measured coverage, kasane with the hitoe at 10 %, Wada and editorial rows equal.
  * --near HEX (repeatable; a #rrggbb in the query works too) keeps palettes holding a colour within --near-max (default
    0.08 dE_OK) of every given hex, nearest first. When nothing is that close it says so and names the closest colour and
    its distance; it never widens the radius by itself. A bare #rgb made only of digits (#229) still reads as a plate.
  * Kasane and paintings carry measured moods (mood_source 'measured', rules in build_data.py); Wada and editorial rows
    carry the site's tags (mood_source 'site'). 'refined' is never measured.
  * --count takes one number, a comma list or a range (3 | 3,4 | 2-3; 2-6 colours), any of which may match.
  * Words like "three colours" become a hard --count; wada / painting / kasane / editorial become a source filter; calm,
    quiet -> serene. "earthy" soft-expands to earth-tone words at half weight and also reads as earth-tone colours; unless
    a source filter is active the best-scoring Wada plate is guaranteed a slot in the results (when --limit is 3 or more).
  * Words that describe the product rather than its colours (fintech, dashboard, bakery) are not in the vocabulary on
    purpose; with nothing else to go on the script reports no match and asks for colour words or filters.
  * "japanese" (and japan, ...) matches the Japanese eras including showa (the Wada plates) and spreads the top results: the best Wada
    plate and the best kasane pattern are always included when any match, and at most one candidate sits on a cream / kinari / gofun
    ground (L >= 0.90, C <= 0.06, hue 60-100) unless the query asks for calm / serene / quiet.
  * "japanese" + painting puts Hokusai's Great Wave first (the only East Asian work) with a note.

A named kasane pattern that is not among the 33 (x-gasane, x no nioi, x no usuyo; macrons ignored) or a quoted title with no match
  exits 2 with no rows; query words the data does not contain are always listed ("Words not found in the data").

Exit codes: 0 results printed | 1 no match | 2 not in the data / bad input.

Examples:
  python3 scripts/search.py earthy three colours
  python3 scripts/search.py "calm blue" --source-type wada_plate --limit 3 --json
  python3 scripts/search.py ocean pastel
  python3 scripts/search.py --near "#2a9d8f" --count 3
  python3 scripts/search.py --hue teal,green --lightness dark --chroma muted
  python3 scripts/search.py --id wada-229
  python3 scripts/search.py japanese painting
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colorlib as cl  # noqa: E402
import vocab as cv  # noqa: E402  (the colour vocabulary; 'vocab' below is the data's word set)

K1, B = 1.5, 0.75
FACET_BASE, FACET_SHARE, FACET_VARIETY, FACET_MOOD = 1.0, 2.0, 1.0, 0.5  # vocabulary match: see facet_score()
NEAR_WEIGHT, HUE_WEIGHT = 3.0, 1.0
NEAR_MAX_DEFAULT = 0.08
COUNT_RANGE = (2, 6)  # distinct colours per palette that --count accepts
SOURCE_TYPES = ("wada_plate", "editorial", "painting", "kasane")
STOPWORDS = set("to in on at is of by or an if no so do be we it as the and for are was with some something me i want need a".split())
GENERIC = set("color colors palette palettes combination combinations scheme schemes hex wada plate plates dictionary "
              "tone tones shade shades hue hues vibe vibes feel feeling look style aesthetic".split())
SYNONYMS = {  # spelling variants -> canonical token
    "colour": "color", "colours": "colors", "grey": "gray", "greys": "grays", "greyish": "grayish",
    "calm": "serene", "quiet": "serene", "peaceful": "serene", "gentle": "serene",
    "loud": "bold", "strong": "bold", "cold": "cool", "fall": "autumn",
}
HUE_ALIASES = {"grey": "neutral", "gray": "neutral", "violet": "purple", "cyan": "teal", "turquoise": "teal", "aqua": "teal"}
SKIP_AFTER_NEGATION = {"too", "so", "very", "overly", "a", "the", "any", "really"}
EXPANSIONS = {  # soft expansions (half weight): a word with no direct hit in the data
    "earthy": ["earth", "brown", "sienna", "umber", "ochre", "ocher", "olive", "tobacco", "sepia", "russet", "clay"],
    "natural": ["earthy", "olive", "sage", "moss"],
    "autumn": ["maple", "momiji", "chrysanthemum", "russet", "kuchiba"],
    "spring": ["blossom", "sakura", "plum", "wisteria"],
}
JAPAN_WORDS = {"japan", "japanese", "ukiyo", "ukiyoe", "nihon", "eastern", "asian"}
JAPAN_ERAS = ["edo", "heian", "kamakura", "muromachi", "meiji", "showa"]
PAINTING_WORDS = {"painting", "paintings", "painter", "artwork", "artworks", "masterpiece"}
SOURCE_WORDS = {
    "wada": "wada_plate", "editorial": "editorial", "kasane": "kasane", "painting": "painting",
    "paintings": "painting", "painter": "painting", "artwork": "painting", "artworks": "painting",
}
NUMBER_WORDS = {"two": 2, "three": 3, "four": 4}

_VOL2 = re.compile(r"\bvol(?:ume|\.)?\s*\.?\s*(?:2|ii|two)\b|\bsecond\s+volume\b|\b2020\s+(?:volume|edition|set)\b", re.I)
_PLATE = [
    re.compile(r"\b(?:wada[\s-]*)?(?:plate|no\.?|number|#)[\s-]*#?\s*(\d{1,5})\b", re.I),
    re.compile(r"\bwada[\s-]+#?(\d{1,5})\b", re.I),
]
_COUNT = re.compile(r"\b(2|3|4|two|three|four)[\s-]*(?:colou?rs?|tones?|shades?)\b", re.I)
_HEX_IN_TEXT = re.compile(r"(?<![\w#])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?!\w)")


def extract_hexes(text: str) -> tuple[list[str], str]:
    """#rrggbb / #rgb colours in a free-text query -> (hex list, the text without them). An all-digit #rgb (#229) is
    left in place: it reads as a plate number."""
    found: list[str] = []

    def take(m: re.Match) -> str:
        if len(m.group(1)) == 3 and m.group(1).isdigit():
            return m.group(0)
        found.append(cl.normalize_hex(m.group(0)))
        return " "

    return found, _HEX_IN_TEXT.sub(take, text)


# --------------------------------------------------------------------------- colour vocabulary (vocab.py)


def _singular(w: str) -> list[str]:
    out = [w]
    if w.endswith("es") and len(w) > 4:
        out.append(w[:-2])
    if w.endswith("s") and len(w) > 3:
        out.append(w[:-1])
    return out


def _lookup(canon: list[str], k: int) -> tuple[int, dict | None]:
    """The vocabulary entry that starts at word k: (number of words it uses, facet) or (0, None)."""
    if k + 1 < len(canon):
        two = f"{canon[k]} {canon[k + 1]}"
        if two in cv.COMPOUNDS:
            desc, specs = cv.COMPOUNDS[two]
            return 2, {"word": two, "desc": "a colour: " + desc, "groups": [specs]}
        if two in cv.THEMES:
            return 2, {"word": two, **cv.THEMES[two]}
    if k < len(canon):
        for w in _singular(canon[k]):
            if w in cv.COLOURS:
                desc, specs = cv.COLOURS[w]
                return 1, {"word": canon[k], "desc": "a colour: " + desc, "groups": [specs]}
            if w in cv.THEMES:
                return 1, {"word": canon[k], **cv.THEMES[w]}
    return 0, None


def _intersect(a, b):
    if b is None:
        return a
    if a is None:
        return b
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (lo, hi) if lo < hi else False


def _range_text(name: str, r: tuple[float, float]) -> str:
    if r[0] <= 0:
        return f"{name} <= {r[1]:.2f}"
    if r[1] >= 1:
        return f"{name} >= {r[0]:.2f}"
    return f"{name} {r[0]:.2f}-{r[1]:.2f}"


def _bands_text(f: dict) -> str:
    bits = []
    if f.get("lightness"):
        bits.append("lightness " + " or ".join(b for b in cl.LIGHTNESS_BANDS if b in f["lightness"]))
    if f.get("chroma"):
        bits.append("chroma " + " or ".join(b for b in cl.CHROMA_BANDS if b in f["chroma"]))
    return ", ".join(bits)


def read_vocab(words: list[str], data_vocab: set[str]) -> tuple[list[dict], set[int], set[int], set[int], set[int], list[str]]:
    """Read everyday colour words. -> (facets, indices the vocabulary used, indices of its colour / scene nouns (these
    also count as BM25 terms when the data has them, so 'pink' finds 'Eosine Pink'), indices of words in a compound or
    narrowed by a modifier (their name matches only rank palettes that fit the reading: 'pastel pink' does not take
    'Eosine Pink', L 0.72, on its name), negated indices, negated words worth reporting). A modifier narrows the colour
    word or scene after it; alone it sets a palette band."""
    canon = [SYNONYMS.get(w, w) for w in words]
    facets: list[dict] = []
    used: set[int] = set()
    nouns: set[int] = set()
    narrowed: set[int] = set()
    negated: set[int] = set()
    reported: list[str] = []
    i = 0
    while i < len(canon):
        w = canon[i]
        if w in cv.NEGATIONS:
            j = i + 1
            while j < len(canon) and canon[j] in SKIP_AFTER_NEGATION:
                j += 1
            if j < len(canon):
                n = max(1, _lookup(canon, j)[0])
                span = range(j, j + n)
                if any(canon[k] in cv.MODIFIERS or _lookup(canon, k)[1] or canon[k] in data_vocab for k in span):
                    reported.append(" ".join(words[k] for k in span))
                negated.update(span)
                used.update(range(i, j + n))
                i = j + n
            else:
                used.add(i)
                i += 1
            continue
        mod = cv.MODIFIERS.get(w)
        if mod is not None:
            n, ent = _lookup(canon, i + 1)
            if ent and ent.get("groups"):
                groups = [[s for s in ({**s, "L": _intersect(s["L"], mod.get("L")), "C": _intersect(s["C"], mod.get("C"))}
                                       for s in g) if s["L"] is not False and s["C"] is not False] for g in ent["groups"]]
                narrow = ", ".join(_range_text(k, mod[k]) for k in ("L", "C") if mod.get(k))
                facets.append({**ent, "word": f"{words[i]} {ent['word']}", "groups": groups,  # an emptied group fits nothing
                               "needs_colour": True, "desc": f"{ent['desc']}, narrowed by '{w}' to {narrow}",
                               "moods": list(dict.fromkeys(list(ent.get("moods", [])) + list(mod.get("moods", []))))})
                used.update(range(i, i + 1 + n))
                narrowed.update(range(i + 1, i + 1 + n))
                i += 1 + n
                continue
            ranks = [cv.spec(L=mod.get("L"), C=mod.get("C"))] if mod.get("L") or mod.get("C") else []
            facets.append({"word": words[i], "groups": [ranks] if ranks else [], "needs_colour": False,
                           "lightness": mod.get("lightness"), "chroma": mod.get("chroma"),
                           "moods": list(mod.get("moods", [])), "desc": "a palette with " + _bands_text(mod)})
            used.add(i)
            i += 1
            continue
        n, ent = _lookup(canon, i)
        if ent:
            facets.append(ent)
            used.update(range(i, i + n))
            (narrowed if n > 1 else nouns).update(range(i, i + n))  # 'slate blue' is not 'Deep Slate Olive'
            i += n
            continue
        i += 1
    for f in facets:  # a word that names colours fits only palettes holding one (after "dark", "lemon" fits none)
        f["needs_colour"] = f.get("needs_colour", bool(f.get("groups")))
    return facets, used, nouns, narrowed, negated, reported


def facet_score(profile: dict, row: dict, f: dict) -> float:
    """0 when the palette does not fit the word. Otherwise FACET_BASE + FACET_SHARE x the area share of its colours that
    fit the word's colour specs (0.5 when the word only sets palette conditions) + FACET_VARIETY x the share of the
    word's colour groups it holds (up to three; words with one group get none) + FACET_MOOD when it carries one of the
    word's moods. A palette condition (band, L range, tone, hue count) failing gives 0; so does a colour word with no
    fitting colour, or a theme whose required group ('needs') the palette lacks. A lone modifier ('pastel') ranks by
    the share of colours that fit it but needs none."""
    if f.get("lightness") and profile["lightness"] not in f["lightness"]:
        return 0.0
    if f.get("chroma") and profile["chroma"] not in f["chroma"]:
        return 0.0
    if f.get("contrast") and profile["l_range"] < f["contrast"]:
        return 0.0
    if f.get("tone") and row["tone_family"] != f["tone"]:
        return 0.0
    if f.get("min_hues") and len(set(profile["hue_shares"]) - {"neutral"}) < f["min_hues"]:
        return 0.0
    groups = f.get("groups") or []
    share, variety = 0.5, 0.0
    for k in f.get("needs", ()):  # groups the palette must hold (the glow of an ember)
        if not any(colour_fits(x, s) for x in profile["colours"] for s in groups[k]):
            return 0.0
    if groups:
        specs = [s for g in groups for s in g]
        share = sum(x["w"] for x in profile["colours"] if any(colour_fits(x, s) for s in specs))
        if share <= 0 and f.get("needs_colour"):
            return 0.0
        if len(groups) > 1:
            held = sum(1 for g in groups if any(colour_fits(x, s) for x in profile["colours"] for s in g))
            variety = min(held, 3) / min(len(groups), 3)
    mood = FACET_MOOD if set(f.get("moods", [])) & set(row["moods"].split(";")) else 0.0
    return FACET_BASE + FACET_SHARE * share + FACET_VARIETY * variety + mood


def colour_fits(x: dict, s: dict) -> bool:
    if s["buckets"] is not None and x["bucket"] not in s["buckets"]:
        return False
    if s["arc"] is not None:
        lo, hi = s["arc"]
        inside = lo <= x["h"] < hi if lo <= hi else (x["h"] >= lo or x["h"] < hi)
        if not inside or x["C"] < (s["C"][0] if s["C"] else cl.CHROMATIC_MIN):
            return False
    if s["L"] is not None and not s["L"][0] <= x["L"] < s["L"][1]:
        return False
    if s["C"] is not None and not s["C"][0] <= x["C"] < s["C"][1]:
        return False
    return True


# --------------------------------------------------------------------------- tokenising / BM25


def tokenize(text: str) -> list[str]:
    toks = []
    for t in re.findall(r"\w+", text.lower()):
        t = SYNONYMS.get(t, t)
        if len(t) < 2 and not t.isdigit():
            continue
        if t in STOPWORDS:
            continue
        toks.append(t)
    return toks


def load_aliases(data_dir: Path) -> dict[str, list[str]]:
    """colour name (lower) -> alternative spellings, from data/colors.csv (if present)."""
    p = data_dir / "colors.csv"
    out: dict[str, list[str]] = {}
    if not p.exists():
        return out
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            al = [a for a in r["aliases"].split(";") if a]
            if al:
                out[r["name"].lower()] = al
    return out


def doc_text(row: dict, aliases: dict[str, list[str]]) -> str:
    names = row["color_names"].replace(";", " ")
    extra = []
    for n in row["color_names"].split(";"):
        extra += aliases.get(n.lower(), [])
    parts = [row["title"], row["title_ja"], names, " ".join(extra), row["moods"].replace(";", " "), row["hue"],
             row["era"], row["season"], row["label"], row["source_type"].replace("_", " ")]
    return " ".join(p for p in parts if p)


class BM25:
    def __init__(self, docs: list[list[str]]):
        self.docs = docs
        self.n = len(docs)
        self.avgdl = (sum(len(d) for d in docs) / self.n) if self.n else 1.0
        self.df: dict[str, int] = {}
        self.tf: list[dict[str, int]] = []
        for d in docs:
            counts: dict[str, int] = {}
            for t in d:
                counts[t] = counts.get(t, 0) + 1
            self.tf.append(counts)
            for t in counts:
                self.df[t] = self.df.get(t, 0) + 1

    def idf(self, t: str) -> float:
        df = self.df.get(t, 0)
        return math.log((self.n - df + 0.5) / (df + 0.5) + 1)

    def score(self, i: int, weighted_terms: dict[str, float]) -> float:
        tf, dl = self.tf[i], len(self.docs[i])
        s = 0.0
        for t, w in weighted_terms.items():
            f = tf.get(t, 0)
            if not f:
                continue
            s += w * self.idf(t) * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / self.avgdl))
        return s


# --------------------------------------------------------------------------- query parsing


def parse_query(query: str, vocab: set[str], moods: set[str]) -> dict:
    """Split a free-text query into hard hints, flags and weighted BM25 terms."""
    info: dict = {"vol2": False, "plate": None, "count": None, "source_type": None, "japan": False,
                  "painting_scope": False, "terms": {}, "dropped": [], "notes": [], "facets": [], "near": [],
                  "negated": []}
    info["near"], q = extract_hexes(query.strip())
    if _VOL2.search(q):
        info["vol2"] = True
        return info
    for rx in _PLATE:
        m = rx.search(q)
        if m:
            info["plate"] = int(m.group(1))
            return info
    m = _COUNT.search(q)
    rest = q
    if m:
        v = m.group(1).lower()
        info["count"] = int(v) if v.isdigit() else NUMBER_WORDS[v]
        rest = q[: m.start()] + " " + q[m.end():]
    words = re.findall(r"\w+", rest.lower())
    if info["count"] is None:
        for w in words:
            if w in NUMBER_WORDS and len(words) > 1:
                info["count"] = NUMBER_WORDS[w]
                words.remove(w)
                break
    source_hits = [SOURCE_WORDS[w] for w in words if w in SOURCE_WORDS]
    if source_hits:
        info["source_type"] = source_hits[0]
    info["painting_scope"] = any(w in PAINTING_WORDS for w in words)
    info["facets"], used, nouns, narrowed, negated, info["negated"] = read_vocab(words, vocab)
    info["boost"] = {SYNONYMS.get(words[k], words[k]): 1.0 for k in narrowed if SYNONYMS.get(words[k], words[k]) in vocab}
    terms: dict[str, float] = {}
    for idx, w in enumerate(words):
        if idx in negated or (idx in used and (idx not in nouns or SYNONYMS.get(w, w) not in vocab)):
            continue  # read by the colour vocabulary only (or negated): not a BM25 term, not an unknown word
        if w in JAPAN_WORDS:
            info["japan"] = True
            continue
        if w in PAINTING_WORDS or w in ("wada", "editorial", "kasane"):
            info["dropped"].append(w)
            continue
        canon = SYNONYMS.get(w, w)
        if canon in STOPWORDS or canon in GENERIC or (len(canon) < 2 and not canon.isdigit()):
            if canon in GENERIC:
                info["dropped"].append(w)
            continue
        terms[canon] = max(terms.get(canon, 0.0), 1.0)
        for e in EXPANSIONS.get(canon, []):
            e = SYNONYMS.get(e, e)
            if e not in terms:
                terms[e] = 0.5
    if info["japan"] and not info["painting_scope"] and info["source_type"] != "painting":
        for e in JAPAN_ERAS:
            terms.setdefault(e, 0.5)
    info["terms"] = terms
    return info


# --------------------------------------------------------------------------- lookup / rendering


def fold(text: str) -> str:
    """Lower-case ASCII form: macrons and other accents removed (K\u014dri -> kori)."""
    import unicodedata

    t = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in t if not unicodedata.combining(ch))


_KASANE_NAME = re.compile(r"[a-z]+-gasane|[a-z]+[- ]no[- ](?:nioi|usuyo)")
_QUOTED = re.compile(r"[\"\u201c\u201d]([^\"\u201c\u201d]+)[\"\u201c\u201d]")


def missing_title(query: str, rows: list[dict]) -> str | None:
    """A pattern or title the user named that is not in the data, or None. Covers kasane names (-gasane, X no nioi,
    X no usuyo; macrons ignored) and quoted titles, which must match a title exactly (as a phrase)."""
    folded = fold(query)
    ids = {r["id"] for r in rows}
    for m in _KASANE_NAME.finditer(folded):
        name = re.sub(r"[ ]", "-", m.group(0))
        if f"kasane-{name}" not in ids:
            return m.group(0)
    for m in _QUOTED.finditer(query):
        phrase = fold(m.group(1)).strip()
        if phrase and not any(phrase in fold(" ".join([r["title"], r["title_ja"], r["color_names"].replace(";", " ")])) for r in rows):
            return m.group(1).strip()
    return None


def is_cream_ground(row: dict) -> bool:
    """Lightest member is a cream / kinari / gofun ground: OKLCH L >= 0.90, C <= 0.06, hue 60-100 degrees."""
    best = max((cl.hex_to_oklch(h) for h in row["colors"].split(";") if h), key=lambda x: x[0])
    return best[0] >= 0.90 and best[1] <= 0.06 and 60 <= best[2] <= 100


def japan_spread(scored: list[tuple[int, float]], rows: list[dict], limit: int, allow_cream: bool) -> list[tuple[int, float]]:
    """Result list for a Japan-word query: the best Wada plate and the best kasane pattern are always in (when any match),
    and at most one candidate sits on a cream/kinari/gofun ground unless the query asks for calm. Keeps score order."""
    creams = {i for i, _ in scored if is_cream_ground(rows[i])}
    chosen: list[tuple[int, float]] = []

    def can_add(i: int) -> bool:
        return allow_cream or i not in creams or not any(c in creams for c, _ in chosen)

    for kind in ("wada_plate", "kasane"):
        pick = next(((i, sc) for i, sc in scored if rows[i]["source_type"] == kind and i not in creams), None) \
            or next(((i, sc) for i, sc in scored if rows[i]["source_type"] == kind and can_add(i)), None)
        if pick and pick not in chosen and len(chosen) < limit:
            chosen.append(pick)
    for item in scored:
        if len(chosen) >= limit:
            break
        if item not in chosen and can_add(item[0]):
            chosen.append(item)
    order = {i: k for k, (i, _) in enumerate(scored)}
    return sorted(chosen, key=lambda t: order[t[0]])


def plate_from_id(text: str) -> int | None:
    m = re.match(r"^\s*(?:wada)?[\s-]*(?:plate)?[\s-]*#?(\d{1,5})\s*$", text, re.I)
    return int(m.group(1)) if m else None


def render_row(row: dict, score: float | None = None, near: list[dict] | None = None) -> dict:
    members = cl.row_members(row)
    profile = cl.palette_profile(row)
    out = {
        "id": row["id"], "source_type": row["source_type"], "title": row["title"], "title_ja": row["title_ja"],
        "colors": members, "hue": row["hue"], "hues": [h for h in row["hues"].split(";") if h],
        "moods": [m for m in row["moods"].split(";") if m], "mood_source": row["mood_source"],
        "tone": {"lightness": profile["lightness"], "l_mean": round(profile["l_mean"], 3),
                 "chroma": profile["chroma"], "c_max": round(profile["c_max"], 3)},
        "era": row["era"], "season": row["season"], "count": int(row["count"] or 0),
        "tone_family": row["tone_family"], "label": row["label"], "source_url": row["source_url"],
        "licence": row["licence"],
    }
    if row["source_type"] == "painting":
        out["drift"] = row["drift"] == "true"
        if out["drift"]:
            out["drift_note"] = cl.DRIFT_NOTE
    if near:
        out["near"] = near
    if score is not None:
        out["score"] = round(score, 3)
    return out


def format_text(i: int, r: dict, full: bool = False) -> str:
    """Default listing is compact; --full adds the source URL, licence and score lines."""
    lines = []
    others = [h for h in r["hues"] if h != r["hue"]]
    meta = [f"{r['count']} colours", r["hue"] + (f" (also {', '.join(others)})" if others else ""),
            f"{r['tone']['lightness']}, {r['tone']['chroma']}"]
    if r["moods"]:
        meta.append(", ".join(r["moods"]) + (" (measured)" if r["mood_source"] == "measured" else ""))
    if r["era"]:
        meta.append(r["era"])
    if r["season"]:
        meta.append(r["season"].lower())
    meta.append(f"{r['tone_family']}-tone")
    head = f"{i}. {r['id']}  {r['title']}"
    if r["title_ja"]:
        head += f"  {r['title_ja']}"
    lines.append(head)
    lines.append("   " + " | ".join(m for m in meta if m))
    cols = []
    for c in r["colors"]:
        bit = f"{c['hex']} {c['name']}".strip()
        if c["coverage"]:
            bit += f" ({c['coverage']}%)"
        cols.append(bit)
    lines.append("   colors: " + ", ".join(cols))
    for n in r.get("near", []):
        lines.append(f"   nearest to {n['query']}: {n['hex']} {n['name']}".rstrip() + f" (dE_OK {n['delta_e']:.3f})")
    lines.append(f"   label: {r['label']}")
    if r.get("drift_note"):
        lines.append(f"   drift: {r['drift_note']}")
    if full:
        lines.append(f"   source: {r['source_url']}   licence: {r['licence']}")
        if "score" in r:
            lines.append(f"   score: {r['score']}")
    return "\n".join(lines)


def emit(args, payload: dict, rows_out: list[dict], code: int) -> int:
    if args.json:
        payload["results"] = rows_out
        payload["exit_code"] = code
        print(json.dumps(payload, ensure_ascii=False))  # compact: every field kept, no indentation
        return code
    if payload.get("message"):
        print(payload["message"], file=sys.stderr if code == 2 else sys.stdout)
    for n in payload.get("notes", []):
        print(f"note: {n}")
    for i, r in enumerate(rows_out, 1):
        print(format_text(i, r, full=getattr(args, "full", False)))
        print()
    return code


# --------------------------------------------------------------------------- main search


def run(args, rows: list[dict], aliases: dict) -> int:
    by_id = {r["id"]: r for r in rows}
    payload: dict = {"query": " ".join(args.query), "notes": []}

    if args.id:
        key = args.id.strip().lower()
        n = plate_from_id(key) if not key.startswith(("ed-", "paint-", "kasane-")) else None
        if n is not None:
            if not 1 <= n <= 348:
                payload["message"] = (f"Plate {n} is not in the data: the Dictionary has plates 1-348 "
                                      "(Vol. 2 plates are not included). Nothing was substituted.")
                return emit(args, payload, [], 2)
            key = f"wada-{n}"
        if key not in by_id:
            payload["message"] = f"'{args.id}' is not in the data. Nothing was substituted."
            close = difflib.get_close_matches(key, list(by_id), n=3, cutoff=0.8)
            if close:
                payload["message"] += " Closest ids: " + ", ".join(close) + "."
            return emit(args, payload, [], 2)
        return emit(args, payload, [render_row(by_id[key])], 0)

    moods = {m for r in rows for m in r["moods"].split(";") if m}
    docs = [tokenize(doc_text(r, aliases)) for r in rows]
    vocab = {t for d in docs for t in d}
    query = " ".join(args.query)
    info = parse_query(query, vocab, moods)

    if info["vol2"]:
        payload["message"] = ("Wada's Dictionary Vol. 2 (2020) plates are not in the data; only Vol. 1 plates 1-348 "
                              "(1933-34) are included. Nothing was substituted.")
        return emit(args, payload, [], 2)
    gone = missing_title(query, rows)
    if gone:
        payload["message"] = f"'{gone}' is not in the data. Nothing was substituted."
        return emit(args, payload, [], 2)
    if info["plate"] is not None:
        n = info["plate"]
        if not 1 <= n <= 348:
            payload["message"] = (f"Plate {n} is not in the data: the Dictionary has plates 1-348. "
                                  "Nothing was substituted.")
            return emit(args, payload, [], 2)
        return emit(args, payload, [render_row(by_id[f"wada-{n}"])], 0)

    # filters
    source_type = args.source_type or info["source_type"]
    try:
        counts = parse_counts(args.count) if args.count else ({info["count"]} if info["count"] is not None else set())
        mood_set = parse_list(args.mood)
        if mood_set - moods:
            raise ValueError(f"--mood: {', '.join(sorted(mood_set - moods))} is not a mood in the data "
                             f"(moods: {', '.join(sorted(moods))})")
        hue_set = {HUE_ALIASES.get(h, h) for h in parse_list(args.hue)}
        if hue_set - set(cl.HUE_BUCKETS):
            raise ValueError(f"--hue: {', '.join(sorted(hue_set - set(cl.HUE_BUCKETS)))} is not a hue "
                             f"(choose from {', '.join(cl.HUE_BUCKETS)})")
        light_ranges = parse_ranges(args.lightness, cl.LIGHTNESS_BANDS, "--lightness")
        chroma_ranges = parse_ranges(args.chroma, cl.CHROMA_BANDS, "--chroma")
        near = []
        for h in [t for v in (args.near or []) for t in re.split(r"[,;\s]+", v) if t] + info["near"]:
            if not cl.is_hex(h):
                raise ValueError(f"--near: '{h}' is not a hex colour (#rrggbb or #rgb)")
            if cl.normalize_hex(h) not in near:
                near.append(cl.normalize_hex(h))
        if near and not args.near_max > 0:
            raise ValueError("--near-max must be above 0")
    except ValueError as e:
        payload["message"] = f"error: {e}"
        return emit(args, payload, [], 2)
    era = args.era.lower() if args.era else None
    season = args.season.lower() if args.season else None
    active = {k: v for k, v in dict(count=sorted(counts) or None, mood=sorted(mood_set) or None, hue=sorted(hue_set) or None,
                                    lightness=args.lightness, chroma=args.chroma, era=era, season=season,
                                    source_type=source_type, near=near or None,
                                    near_max=args.near_max if near else None).items() if v}
    payload["filters"] = active
    profiles = [cl.palette_profile(r) for r in rows]

    def passes(i: int) -> bool:
        r, p = rows[i], profiles[i]
        if counts and int(r["count"] or 0) not in counts:
            return False
        if mood_set and not (mood_set & set(r["moods"].split(";"))):
            return False
        if hue_set and not (hue_set & set(r["hues"].split(";"))):
            return False
        if light_ranges and not any(lo <= p["l_mean"] < hi for lo, hi in light_ranges):
            return False
        if chroma_ranges and not any(lo <= p["c_max"] < hi for lo, hi in chroma_ranges):
            return False
        if era and r["era"].lower() != era:
            return False
        if season and season not in r["season"].lower():
            return False
        if source_type and r["source_type"] != source_type:
            return False
        return True

    base_pool = [i for i in range(len(rows)) if passes(i)]
    near_hits = {i: nearest_members(rows[i], near) for i in base_pool} if near else {}
    pool = [i for i in base_pool if all(h["delta_e"] <= args.near_max for h in near_hits[i])] if near else base_pool

    def bonus(i: int) -> float:
        b = NEAR_WEIGHT * sum(1 - h["delta_e"] / args.near_max for h in near_hits[i]) if near else 0.0
        return b + HUE_WEIGHT * sum(profiles[i]["hue_shares"].get(h, 0.0) for h in hue_set)

    terms, facets = info["terms"], info["facets"]
    known = {t: w for t, w in terms.items() if t in vocab}
    hokusai_id = "paint-the-great-wave-off-kanagawa"
    scored: list[tuple[int, float]] = []
    bm = BM25(docs)
    if terms or facets:
        for i in pool:
            fs = sum(facet_score(profiles[i], rows[i], f) for f in facets)
            s = (bm.score(i, known) if known else 0.0) + fs
            if s > 0:
                boost = bm.score(i, info["boost"]) if fs > 0 and info["boost"] else 0.0
                scored.append((i, s + boost + bonus(i)))
    elif near or active or info["japan"] or info["dropped"]:
        scored = [(i, bonus(i)) for i in pool]  # filter-only request: nearest / most of the hue first, then table order
    scored.sort(key=lambda t: (-t[1], t[0]))

    # Hokusai first for a Japanese-painting request (the only East Asian work among the 25)
    painting_scope = source_type == "painting" or info["painting_scope"]
    if info["japan"] and painting_scope and hokusai_id in by_id:
        hi = next(i for i, r in enumerate(rows) if r["id"] == hokusai_id)
        if hi in pool:
            scored = [(hi, max([s for i, s in scored if i == hi] or [0.0]) + 1000.0)] + [t for t in scored if t[0] != hi]
            payload["notes"].append("Hokusai's Great Wave is the only East Asian work among the 25 paintings; the others are European or American. "
                                    "It is shown first and is a woodblock print, so impressions vary.")
            if not terms and not facets:
                scored = scored[:1]

    limit = max(1, args.limit)
    chosen = scored[:limit]
    if info["japan"] and not painting_scope and scored:
        chosen = japan_spread(scored, rows, limit, allow_cream="serene" in terms)
    # keep the Dictionary visible: if no source filter is active, make sure the best Wada plate is included
    if not source_type and limit >= 3 and chosen:
        if not any(rows[i]["source_type"] == "wada_plate" for i, _ in chosen):
            extra = next(((i, s) for i, s in scored[limit:] if rows[i]["source_type"] == "wada_plate"), None)
            if extra:
                chosen = chosen[: limit - 1] + [extra]

    readings = [f"read '{f['word']}' as {f['desc']}" + (f" (palettes tagged {' or '.join(f['moods'])} rank higher)"
                                                        if f.get("moods") else "") for f in facets]
    payload["read_as"] = {f["word"]: f["desc"] for f in facets}
    negated_note = ("not searched (it follows not / no / without): " + ", ".join(info["negated"]) +
                    "; to exclude it, use a filter such as --lightness, --chroma or --hue") if info["negated"] else ""
    unknown = [t for t, w in terms.items() if w >= 1.0 and t not in vocab]

    if not chosen:
        msg = "No palettes in the data match this request. Nothing was substituted."
        if near and base_pool and not pool:
            need, i, h = min(((max(x["delta_e"] for x in near_hits[i]), i, near_hits[i]) for i in base_pool),
                             key=lambda t: (t[0], t[1]))
            closest = "; ".join(f"{x['hex']} {x['name']}".rstrip() + f" at dE_OK {x['delta_e']:.3f} from {x['query']}" for x in h)
            others = {k for k in active if k not in ("near", "near_max")}
            msg = (f"No palette in the data has a colour within dE_OK {args.near_max:.2f} of {', '.join(near)}"
                   + (" with the other filters applied" if others else "") + ". Nothing was substituted. "
                   f"Closest: {rows[i]['id']} ({closest}). Re-run with --near-max {math.ceil(need * 100) / 100:.2f} "
                   "to list the nearest palettes, and present them as a looser match.")
        elif active:
            msg += " Filters applied: " + ", ".join(f"{k}={v}" for k, v in active.items()) + "."
        if readings:
            msg += " Words were " + "; ".join(readings) + "."
        if unknown:
            msg += " Words not found in the data: " + ", ".join(unknown) + "."
            sugg = []
            for t in unknown:
                sugg += difflib.get_close_matches(t, sorted(vocab), n=2, cutoff=0.75)
            if sugg:
                msg += " Did you mean: " + ", ".join(dict.fromkeys(sugg)) + "?"
            if not facets and not known:
                msg += (" If these words describe the product rather than its colours, describe the colours instead (a hue,"
                        " light or dark, muted or vivid, a scene or material such as ocean, coffee, forest, sunset) or use"
                        " --hue, --lightness, --chroma, --mood or --near.")
        if negated_note:
            msg += " Note: " + negated_note + "."
        payload["message"] = msg
        return emit(args, payload, [], 1)

    payload["notes"].extend(readings)
    if negated_note:
        payload["notes"].append(negated_note)
    if unknown:
        payload["notes"].append("Words not found in the data: " + ", ".join(unknown) + ".")
    if info["dropped"]:
        payload["notes"].append("ignored generic words: " + ", ".join(info["dropped"]))
    rows_out = [render_row(rows[i], s if s < 1000 else None, near_hits.get(i)) for i, s in chosen]
    return emit(args, payload, rows_out, 0)


def parse_counts(text: str) -> set[int]:
    """--count values: numbers or ranges, comma list = any ('3', '3,4', '2-3')."""
    out: set[int] = set()
    for tok in parse_list(text):
        m = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", tok)
        if not m:
            raise ValueError(f"--count: '{tok}' is not a number or a range such as 2-3")
        lo, hi = sorted((int(m.group(1)), int(m.group(2) or m.group(1))))
        if lo < COUNT_RANGE[0] or hi > COUNT_RANGE[1]:
            raise ValueError(f"--count: palettes in the data have {COUNT_RANGE[0]}-{COUNT_RANGE[1]} colours, not '{tok}'")
        out.update(range(lo, hi + 1))
    return out


def parse_list(text: str | None) -> set[str]:
    return {t.strip().lower() for t in (text or "").replace(";", ",").split(",") if t.strip()}


def parse_ranges(text: str | None, bands: dict[str, tuple[float, float]], flag: str) -> list[tuple[float, float]]:
    """Band names or numeric ranges ('light', '0.6-0.8'), comma list = any."""
    out = []
    for tok in parse_list(text):
        if tok in bands:
            out.append(bands[tok])
            continue
        m = re.fullmatch(r"(\d*\.?\d+)\s*-\s*(\d*\.?\d+)", tok)
        if not m:
            raise ValueError(f"{flag}: '{tok}' is neither a band ({', '.join(bands)}) nor a range such as 0.6-0.8")
        lo, hi = sorted((float(m.group(1)), float(m.group(2))))
        out.append((lo, hi + 1e-9))
    return out


def nearest_members(row: dict, targets: list[str]) -> list[dict]:
    """For each target hex: the palette colour closest to it in OKLab, and the distance."""
    members = cl.row_members(row)
    out = []
    for q in targets:
        d, k = min((cl.delta_e_ok(q, m["hex"]), k) for k, m in enumerate(members))
        out.append({"query": q, "hex": members[k]["hex"], "name": members[k]["name"], "delta_e": round(d, 4)})
    return out

def main(argv=None) -> int:
    cl.configure_stdio()
    ap = argparse.ArgumentParser(
        prog="search.py",
        description="Search the palette table (Wada plates, editorial palettes, paintings, kasane). "
                    "Never invents a result: missing ids, plates outside 1-348 and Vol. 2 requests are reported as not in the data.",
        epilog="Exit codes: 0 results | 1 no match | 2 not in the data / bad input.",
    )
    ap.add_argument("query", nargs="*", help="free-text query, e.g. 'earthy three colours'")
    ap.add_argument("--id", help="exact lookup: wada-229, ed-kurenai-kon, paint-the-kiss, kasane-fuji (or a bare plate number)")
    ap.add_argument("--count", help="number of distinct colours, 2-6: one number, a comma list or a range (3 | 3,4 | 2-3)")
    ap.add_argument("--mood", help="austere bold cool earthy playful refined serene solemn warm (comma list = any); kasane "
                                   "and paintings carry measured moods (never 'refined')")
    ap.add_argument("--hue", help="a hue the palette contains, measured from its hex values (comma list = any): red orange "
                                  "yellow green teal blue purple pink brown neutral")
    ap.add_argument("--lightness", help="area-weighted mean OKLCH L: dark (< 0.50) | mid | light (>= 0.72), or a range "
                                        "such as 0.6-0.8 (comma list = any)")
    ap.add_argument("--chroma", help="OKLCH C of the most saturated colour: muted (< 0.11) | moderate | vivid (>= 0.17), "
                                     "or a range such as 0-0.1 (comma list = any)")
    ap.add_argument("--near", action="append", help="hex the palette must hold a close colour to (repeat or comma list: "
                                                    "every one must match); a #rrggbb in the query works too")
    ap.add_argument("--near-max", dest="near_max", type=float, default=NEAR_MAX_DEFAULT,
                    help="largest OKLab distance (dE_OK) that counts as near (default 0.08; about 0.02 is barely "
                         "visible, 0.05 clearly visible)")
    ap.add_argument("--era", help="showa edo heian kamakura muromachi meiji")
    ap.add_argument("--source-type", dest="source_type", choices=SOURCE_TYPES, help="restrict to one family")
    ap.add_argument("--season", help="kasane season words, e.g. 'summer', 'late autumn'")
    ap.add_argument("--limit", type=int, default=5, help="maximum results (default 5)")
    ap.add_argument("--full", action="store_true", help="also print the source URL, licence and score per result (the default "
                                                       "listing omits them; handoff.py writes credits from the data)")
    ap.add_argument("--json", action="store_true", help="compact JSON output (all fields, including source_url and licence)")
    ap.add_argument("--data-dir", type=Path, default=cl.data_dir(), help="folder holding palettes.csv (default: <skill>/data)")
    args = ap.parse_intermixed_args(argv)
    if not args.query and not args.id and not any([args.count, args.mood, args.hue, args.lightness, args.chroma, args.near,
                                                   args.era, args.source_type, args.season]):
        ap.print_help()
        return 2
    rows = cl.load_palette_rows(args.data_dir / "palettes.csv")
    aliases = load_aliases(args.data_dir)
    return run(args, rows, aliases)


if __name__ == "__main__":
    sys.exit(main())
