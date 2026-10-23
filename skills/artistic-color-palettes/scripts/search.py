#!/usr/bin/env python3
"""search.py - find palettes in data/palettes.csv (Wada plates, editorial palettes, paintings, kasane).

Ranking is BM25-lite (k1 1.5, b 0.75) over title, colour names, moods, hue, era, season and the
provenance label. Hard filters: --count --mood --hue --era --source-type --season. Nothing is
ever invented: an unknown id, a plate number outside 1-348 or a request for Wada's Vol. 2 gets a
plain "not in the data" message and a non-zero exit; a query with no match says so and returns
nothing (it never pads with unrelated rows).

Choices a user of this script should know:
  * Words like "three colours" become a hard --count; wada / painting / kasane / editorial become a source filter; calm,
    quiet -> serene. "earthy" has no Wada plate with that mood in the data (only editorial rows carry it), so it soft-expands
    to earth-tone words at half weight, and unless a source filter is active the best-scoring Wada plate is guaranteed a
    slot in the results (when --limit is 3 or more).
  * "japanese" (and japan, ...) matches the Japanese eras including showa (the Wada plates) and spreads the top results: the best Wada
    plate and the best kasane pattern are always included when any match, and at most one candidate sits on a cream / kinari / gofun
    ground (L >= 0.90, C <= 0.06, hue 60-100) unless the query asks for calm / serene / quiet.
  * "japanese" + painting puts Hokusai's Great Wave first (the only East Asian work) with a note.

A named kasane pattern that is not among the 33 (x-gasane, x no nioi, x no usuyo; macrons ignored) or a quoted title with no match
  exits 2 with no rows; query words the data does not contain are always listed ("Words not found in the data").

Exit codes: 0 results printed | 1 no match | 2 not in the data / bad input.

Examples:
  python scripts/search.py earthy three colours
  python scripts/search.py "calm blue" --source-type wada_plate --limit 3 --json
  python scripts/search.py --id wada-229
  python scripts/search.py japanese painting
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

K1, B = 1.5, 0.75
SOURCE_TYPES = ("wada_plate", "editorial", "painting", "kasane")
STOPWORDS = set("to in on at is of by or an if no so do be we it as the and for are was with some something me i want need a".split())
GENERIC = set("color colors palette palettes combination combinations scheme schemes hex wada plate plates dictionary".split())
SYNONYMS = {  # spelling variants -> canonical token
    "colour": "color", "colours": "colors", "grey": "gray", "greys": "grays", "greyish": "grayish",
    "calm": "serene", "quiet": "serene", "peaceful": "serene", "gentle": "serene",
    "loud": "bold", "strong": "bold", "dark": "austere", "vivid": "bold",
}
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
                  "painting_scope": False, "terms": {}, "dropped": [], "notes": []}
    q = query.strip()
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
    terms: dict[str, float] = {}
    for w in words:
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


def render_row(row: dict, score: float | None = None) -> dict:
    members = cl.row_members(row)
    out = {
        "id": row["id"], "source_type": row["source_type"], "title": row["title"], "title_ja": row["title_ja"],
        "colors": members, "hue": row["hue"], "moods": [m for m in row["moods"].split(";") if m],
        "era": row["era"], "season": row["season"], "count": int(row["count"] or 0),
        "tone_family": row["tone_family"], "label": row["label"], "source_url": row["source_url"],
        "licence": row["licence"],
    }
    if row["source_type"] == "painting":
        out["drift"] = row["drift"] == "true"
        if out["drift"]:
            out["drift_note"] = cl.DRIFT_NOTE
    if score is not None:
        out["score"] = round(score, 3)
    return out


def format_text(i: int, r: dict) -> str:
    lines = []
    meta = [f"{r['count']} colours", r["hue"]]
    if r["moods"]:
        meta.append(", ".join(r["moods"]))
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
    lines.append(f"   label: {r['label']}")
    if r.get("drift_note"):
        lines.append(f"   drift: {r['drift_note']}")
    lines.append(f"   source: {r['source_url']}   licence: {r['licence']}")
    if "score" in r:
        lines.append(f"   score: {r['score']}")
    return "\n".join(lines)


def emit(args, payload: dict, rows_out: list[dict], code: int) -> int:
    if args.json:
        payload["results"] = rows_out
        payload["exit_code"] = code
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return code
    if payload.get("message"):
        print(payload["message"], file=sys.stderr if code == 2 else sys.stdout)
    for n in payload.get("notes", []):
        print(f"note: {n}")
    for i, r in enumerate(rows_out, 1):
        print(format_text(i, r))
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
    count = args.count if args.count is not None else info["count"]
    source_type = args.source_type or info["source_type"]
    if args.mood:
        mood_set = {m.strip().lower() for m in args.mood.replace(";", ",").split(",") if m.strip()}
    else:
        mood_set = set()
    hue = args.hue.lower() if args.hue else None
    era = args.era.lower() if args.era else None
    season = args.season.lower() if args.season else None
    active = {k: v for k, v in dict(count=count, mood=sorted(mood_set) or None, hue=hue, era=era,
                                    season=season, source_type=source_type).items() if v}
    payload["filters"] = active

    def passes(r: dict) -> bool:
        if count is not None and int(r["count"] or 0) != count:
            return False
        if mood_set and not (mood_set & set(r["moods"].split(";"))):
            return False
        if hue and r["hue"].lower() != hue:
            return False
        if era and r["era"].lower() != era:
            return False
        if season and season not in r["season"].lower():
            return False
        if source_type and r["source_type"] != source_type:
            return False
        return True

    pool = [i for i, r in enumerate(rows) if passes(r)]
    terms = info["terms"]
    hokusai_id = "paint-the-great-wave-off-kanagawa"
    scored: list[tuple[int, float]] = []
    bm = BM25(docs)
    if terms:
        known = {t: w for t, w in terms.items() if t in vocab}
        if known:
            scored = [(i, bm.score(i, known)) for i in pool]
            scored = [(i, s) for i, s in scored if s > 0]
    elif active or info["japan"] or info["dropped"]:
        scored = [(i, 0.0) for i in pool]  # filter-only request: stable table order
    scored.sort(key=lambda t: (-t[1], t[0]))

    # Hokusai first for a Japanese-painting request (the only East Asian work among the 25)
    painting_scope = source_type == "painting" or info["painting_scope"]
    if info["japan"] and painting_scope and hokusai_id in by_id:
        hi = next(i for i, r in enumerate(rows) if r["id"] == hokusai_id)
        if hi in pool:
            scored = [(hi, max([s for i, s in scored if i == hi] or [0.0]) + 1000.0)] + [t for t in scored if t[0] != hi]
            payload["notes"].append("Hokusai's Great Wave is the only East Asian work among the 25 paintings; the others are European or American. "
                                    "It is shown first and is a woodblock print, so impressions vary.")
            if not terms:
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

    if not chosen:
        unknown = [t for t in terms if t not in vocab and terms[t] >= 1.0]
        msg = "No palettes in the data match this request. Nothing was substituted."
        if active:
            msg += " Filters applied: " + ", ".join(f"{k}={v}" for k, v in active.items()) + "."
        if unknown:
            msg += " Words not found in the data: " + ", ".join(unknown) + "."
            sugg = []
            for t in unknown:
                sugg += difflib.get_close_matches(t, sorted(vocab), n=2, cutoff=0.75)
            if sugg:
                msg += " Did you mean: " + ", ".join(dict.fromkeys(sugg)) + "?"
        payload["message"] = msg
        return emit(args, payload, [], 1)

    unknown_words = [t for t, w in terms.items() if w >= 1.0 and t not in vocab]
    if unknown_words:
        payload["notes"].append("Words not found in the data: " + ", ".join(unknown_words) + ".")
    if info["dropped"]:
        payload["notes"].append("ignored generic words: " + ", ".join(info["dropped"]))
    rows_out = [render_row(rows[i], s if s < 1000 else None) for i, s in chosen]
    return emit(args, payload, rows_out, 0)


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
    ap.add_argument("--count", type=int, choices=(2, 3, 4, 5, 6), help="number of distinct colours")
    ap.add_argument("--mood", help="austere bold cool earthy playful refined serene solemn warm (comma list = any)")
    ap.add_argument("--hue", help="dominant hue: red orange yellow green blue purple pink brown neutral")
    ap.add_argument("--era", help="showa edo heian kamakura muromachi meiji")
    ap.add_argument("--source-type", dest="source_type", choices=SOURCE_TYPES, help="restrict to one family")
    ap.add_argument("--season", help="kasane season words, e.g. 'summer', 'late autumn'")
    ap.add_argument("--limit", type=int, default=5, help="maximum results (default 5)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--data-dir", type=Path, default=cl.data_dir(), help="folder holding palettes.csv (default: <skill>/data)")
    args = ap.parse_intermixed_args(argv)
    if not args.query and not args.id and not any([args.count, args.mood, args.hue, args.era, args.source_type, args.season]):
        ap.print_help()
        return 2
    rows = cl.load_palette_rows(args.data_dir / "palettes.csv")
    aliases = load_aliases(args.data_dir)
    return run(args, rows, aliases)


if __name__ == "__main__":
    sys.exit(main())
