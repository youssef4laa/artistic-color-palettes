#!/usr/bin/env python3
"""build_data.py - build-time script: raw colorcombinations.org snapshot + kasane reference ->
the three data files the skill ships (data/palettes.csv, data/colors.csv, data/paintings.json).

Inputs (default: <repo>/data-raw, overridable with --raw):
  palettes.csv, colors.csv, wada-index.csv, paintings/*.json
  references/kasane-no-irome.md (33 layered patterns, parsed from the markdown)

Outputs (default: <skill>/data):
  palettes.csv   one table: Wada plates (348), editorial (30), paintings (25), kasane (33)
  colors.csv     the 210 site colours merged with the 159 printed Wada index rows (by name)
  paintings.json the 25 normalised painting records
  SNAPSHOT.md    gets a "Built data" block with the row counts (updated in place)

Derived columns, documented here so nobody has to guess:
  tone_family   'same' when the chromatic colours (OKLCH C >= 0.04) of the palette lie inside one
                arc of the hue circle no wider than TONE_SPREAD_DEG (70 degrees), else 'different'.
                The arc is 360 minus the largest gap between neighbouring hues. Fewer than two
                chromatic colours -> 'same'. This follows Wada's same-tone / different-tone idea
                (references/wada-method.md 3.4); the threshold is the skill's own choice.
  hue           every row: the dominant hue bucket measured from the hex values (red orange yellow
                green teal blue purple pink brown neutral; colorlib.hue_bucket), i.e. the bucket with
                the largest area-weighted OKLCH chroma above 0.04 (colorlib.palette_profile). The
                site's own dominant_hue tag is not used: it files 13 of the 348 plates under blue and
                none under purple, while 162 plates contain a blue and 77 a purple.
  hues          every hue bucket the palette contains, largest area share first (';'-joined). This is
                what search.py --hue filters on, so a plate with one blue colour is found by "blue".
                Area weights: paintings by measured coverage, kasane with the hitoe at 10 %, others equal.
  moods         Wada/editorial rows: the site's mood tags (mood_source 'site'). Paintings and kasane
                have none on the site, so they get measured moods (mood_source 'measured'), see
                measured_moods(): warm / cool (>= 60 % of the area-weighted chroma above 0.04 falls in
                the warm arc 330-115 degrees / the cool arc 130-300), serene (light band and mean C
                <= 0.10), solemn (dark band), bold (vivid band and L range >= 0.35), austere (muted
                band), earthy (>= 50 % of the area in earth tones: hue 35-115, C 0.02-0.13, L 0.25-0.75),
                playful (mean L >= 0.65, three or more hue families, C max >= 0.13). 'refined' is a
                curatorial judgement the site applies to 83 % of its rows, so it is never measured.
  count         number of distinct colours.
  pair_groups   always empty: the hex order of palettes.csv is not the on-plate position, and the 1G measurements
                (data-raw/wada-proportions.csv, 1G/diagnostics.csv) record area shares per colour, not positions,
                so which colours face each other on a four-colour plate cannot be derived from the data.
  coverage      paintings only: percent of canvas per colour, ';'-joined; '<1' kept as text.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colorlib as cl  # noqa: E402

TONE_SPREAD_DEG = 70.0
TONE_CHROMA_MIN = 0.04

PALETTE_COLUMNS = [
    "id", "source_type", "title", "title_ja", "colors", "color_names", "roles", "coverage", "hue",
    "moods", "era", "season", "count", "drift", "tone_family", "pair_groups", "label", "source_url", "licence",
    "hues", "mood_source",
]
MOOD_ORDER = ("warm", "cool", "serene", "solemn", "bold", "austere", "earthy", "playful")
COLOR_COLUMNS = [
    "slug", "name", "name_ja", "meaning", "hex", "hue_family", "palette_count", "wada_no", "wada_kanji",
    "wada_kana", "wada_print_name", "cmyk", "aliases", "oklch_l", "oklch_c", "oklch_h", "best_text",
    "best_text_ratio", "source_url", "licence",
]

LICENCE_WADA = "PD+MIT+CC-BY-4.0"
LICENCE_CC = "CC-BY-4.0"
LICENCE_KASANE = "CC-BY-SA-4.0 (base hex) + own composition"

# The 25 paintings: artist, date, drift flag, in the order of the site's table
# (Art References/colorcombinations-data.md, checked against the live pages 2026-10-22: the
# "Has the colour changed?" panel appears on exactly the six works flagged here).
PAINTINGS = [
    ("the-starry-night", "The Starry Night", "Vincent van Gogh", "1889", False),
    ("the-bedroom", "The Bedroom", "Vincent van Gogh", "1889", False),
    ("sunflowers", "Sunflowers", "Vincent van Gogh", "1888", True),
    ("cafe-terrace-at-night", "Café Terrace at Night", "Vincent van Gogh", "1888", False),
    ("a-sunday-on-la-grande-jatte", "A Sunday on La Grande Jatte", "Georges Seurat", "1884–86", True),
    ("the-great-wave-off-kanagawa", "Under the Wave off Kanagawa (The Great Wave)", "Katsushika Hokusai", "c. 1831", True),
    ("water-lilies", "Water Lilies", "Claude Monet", "1906", False),
    ("impression-sunrise", "Impression, Sunrise", "Claude Monet", "1872", False),
    ("paris-street-rainy-day", "Paris Street; Rainy Day", "Gustave Caillebotte", "1877", False),
    ("the-kiss", "The Kiss", "Gustav Klimt", "1907–08", True),
    ("the-scream", "The Scream", "Edvard Munch", "1893", True),
    ("girl-with-a-pearl-earring", "Girl with a Pearl Earring", "Johannes Vermeer", "c. 1665", True),
    ("the-birth-of-venus", "The Birth of Venus", "Sandro Botticelli", "c. 1485", False),
    ("the-night-watch", "The Night Watch", "Rembrandt van Rijn", "1642", False),
    ("at-the-moulin-rouge", "At the Moulin Rouge", "Henri de Toulouse-Lautrec", "1892–95", False),
    ("the-childs-bath", "The Child's Bath", "Mary Cassatt", "1893", False),
    ("two-sisters-on-the-terrace", "Two Sisters (On the Terrace)", "Pierre-Auguste Renoir", "1881", False),
    ("the-fighting-temeraire", "The Fighting Temeraire", "J. M. W. Turner", "1839", False),
    ("wanderer-above-the-sea-of-fog", "Wanderer above the Sea of Fog", "Caspar David Friedrich", "c. 1818", False),
    ("the-garden-of-earthly-delights", "The Garden of Earthly Delights", "Hieronymus Bosch", "c. 1500", False),
    ("the-hay-wain", "The Hay Wain", "John Constable", "1821", False),
    ("the-milkmaid", "The Milkmaid", "Johannes Vermeer", "c. 1660", False),
    ("ophelia", "Ophelia", "John Everett Millais", "1851–52", False),
    ("the-third-of-may-1808", "The Third of May 1808", "Francisco Goya", "1814", False),
    ("the-tower-of-babel", "The Tower of Babel", "Pieter Bruegel the Elder", "1563", False),
]

SPELLING_ALIASES = {  # site/mattdesl misspelling -> printed spelling (normalised letters only)
    "sulpher": "sulphur", "ochre": "ocher", "krongbergs": "kronbergs", "artemesia": "artemisia",
    "pomegranite": "pomegranate", "veronia": "vernonia",
}
DUPLICATE_INDEX_NAMES = {  # printed index number -> site colour name (the print repeats the name)
    12: "Eugenia Red A", 13: "Eugenia Red B", 134: "Grayish Lavender - A", 135: "Grayish Lavender - B",
}


# --------------------------------------------------------------------------- helpers


def label_wada(n: int) -> str:
    return f"Wada plate {n} (*A Dictionary of Color Combinations*, 1933)"


LABEL_EDITORIAL = "Editorial palette by colorcombinations.org, inspired by Wada's method"


def label_painting(title: str, artist: str, date: str) -> str:
    """Provenance label; the drift note for flagged works is a separate field (cl.DRIFT_NOTE)."""
    return f"Sampled from {title}, {artist}, {date} by colorcombinations.org"


def label_kasane(name: str) -> str:
    return f"Kasane no irome: {name} (Heian court colour layering; hex values are interpretations)"


def ascii_slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})


def tone_family(hexes: list[str]) -> str:
    hues = []
    for hx in hexes:
        _, c, h = cl.hex_to_oklch(hx)
        if c >= TONE_CHROMA_MIN:
            hues.append(h)
    if len(hues) < 2:
        return "same"
    hues.sort()
    gaps = [hues[i + 1] - hues[i] for i in range(len(hues) - 1)] + [hues[0] + 360 - hues[-1]]
    spread = 360.0 - max(gaps)
    return "same" if spread <= TONE_SPREAD_DEG else "different"


def measured_moods(row: dict) -> list[str]:
    """Mood tags measured from the colours (the rules are listed in the module docstring)."""
    p = cl.palette_profile(row)
    cs = p["colours"]

    def force(x: dict) -> float:
        return x["w"] * max(0.0, x["C"] - cl.CHROMATIC_MIN)

    moods = set()
    total = sum(force(x) for x in cs)
    if total > 0:
        if sum(force(x) for x in cs if x["h"] >= 330 or x["h"] < 115) / total >= 0.6:
            moods.add("warm")
        if sum(force(x) for x in cs if 130 <= x["h"] < 300) / total >= 0.6:
            moods.add("cool")
    if p["lightness"] == "light" and sum(x["C"] * x["w"] for x in cs) <= 0.10:
        moods.add("serene")
    if p["lightness"] == "dark":
        moods.add("solemn")
    if p["chroma"] == "vivid" and p["l_range"] >= 0.35:
        moods.add("bold")
    if p["chroma"] == "muted":
        moods.add("austere")
    if sum(x["w"] for x in cs if 35 <= x["h"] <= 115 and 0.02 <= x["C"] <= 0.13 and 0.25 <= x["L"] <= 0.75) >= 0.5:
        moods.add("earthy")
    if p["l_mean"] >= 0.65 and len({x["bucket"] for x in cs} - {"neutral"}) >= 3 and p["c_max"] >= 0.13:
        moods.add("playful")
    return [m for m in MOOD_ORDER if m in moods]


def add_measured_columns(row: dict) -> dict:
    """hue and hues from the hex values for every row; measured moods where the source has none."""
    p = cl.palette_profile(row)
    row["hue"] = p["dominant"]
    row["hues"] = ";".join(p["hue_shares"])
    if row["moods"]:
        row["mood_source"] = "site"
    else:
        row["moods"] = ";".join(measured_moods(row))
        row["mood_source"] = "measured"
    return row


def check_hexes(row_id: str, hexes: list[str]) -> list[str]:
    out = []
    for h in hexes:
        if not cl.is_hex(h):
            raise SystemExit(f"{row_id}: invalid hex {h!r}")
        out.append(cl.normalize_hex(h))
    return out


# --------------------------------------------------------------------------- palettes


def build_dictionary_rows(raw: Path) -> list[dict]:
    rows = []
    for r in read_csv(raw / "palettes.csv"):
        slug = r["slug"]
        n = int(r["color_count"])
        hexes = check_hexes(slug, [r[f"hex_{i}"] for i in range(1, n + 1)])
        names = [r[f"color_{i}"] for i in range(1, n + 1)]
        moods = ";".join(m for m in r["moods"].split("|") if m)
        m = re.match(r"^wada-(\d{3})-", slug)
        if m:
            plate = int(m.group(1))
            if not 1 <= plate <= 348:
                raise SystemExit(f"{slug}: plate number outside 1-348")
            rows.append(dict(
                id=f"wada-{plate}", source_type="wada_plate", title=r["title"], title_ja=r["title_ja"],
                colors=";".join(hexes), color_names=";".join(names), roles="", coverage="",
                hue="", moods=moods, era=r["era"], season="", count=len(set(hexes)),
                drift="", tone_family=tone_family(hexes), label=label_wada(plate),
                source_url=r["canonical_url"], licence=LICENCE_WADA,
            ))
        else:
            rows.append(dict(
                id=f"ed-{slug}", source_type="editorial", title=r["title"], title_ja=r["title_ja"],
                colors=";".join(hexes), color_names=";".join(names), roles="", coverage="",
                hue="", moods=moods, era=r["era"], season="", count=len(set(hexes)),
                drift="", tone_family=tone_family(hexes), label=LABEL_EDITORIAL,
                source_url=r["canonical_url"], licence=LICENCE_CC,
            ))
    rows.sort(key=lambda x: (0 if x["source_type"] == "wada_plate" else 1,
                             int(x["id"].split("-")[1]) if x["source_type"] == "wada_plate" else 0, x["id"]))
    return rows


def parse_coverage(text: str) -> tuple[str, int | None]:
    t = text.strip()
    if t.startswith("<"):
        return "<1", 0
    return str(int(t)), int(t)


def build_paintings(raw: Path) -> tuple[list[dict], list[dict]]:
    """-> (palette rows, painting records)"""
    rows, records = [], []
    for slug, title, artist, date, drift in PAINTINGS:
        path = raw / "paintings" / f"{slug}.json"
        src = json.loads(path.read_text(encoding="utf-8"))
        sw = src["swatches_from_page"]
        exp = [c["hex"] for c in src["export_verbatim"]["colors"]]
        hexes = check_hexes(slug, [s["hex"] for s in sw])
        if [cl.normalize_hex(h) for h in exp] != hexes:
            raise SystemExit(f"{slug}: export hex list and page swatches disagree")
        roles = [s["role"] for s in sw]
        if roles.count("ground") != 3 or roles.count("accent") != 3:
            raise SystemExit(f"{slug}: expected 3 ground + 3 accent, got {roles}")
        cov_text = [parse_coverage(s["coverage_pct_text"])[0] for s in sw]
        pid = f"paint-{slug}"
        label = label_painting(title, artist, date)
        url = src["page_url"]
        rows.append(dict(
            id=pid, source_type="painting", title=f"{title} — {artist}", title_ja="",
            colors=";".join(hexes), color_names=";".join(f"{r} {i + 1}" for i, r in enumerate(roles)),
            roles=";".join(roles), coverage=";".join(cov_text), hue="", moods="", era="",
            season="", count=len(set(hexes)), drift="true" if drift else "false",
            tone_family=tone_family(hexes), label=label, source_url=url, licence=LICENCE_CC,
        ))
        records.append(dict(
            id=pid, slug=slug, title=title, artist=artist, date=date, page_url=url,
            drift=drift, drift_note=cl.DRIFT_NOTE if drift else "", label=label,
            east_asian=(slug == "the-great-wave-off-kanagawa"),
            licence="CC BY 4.0 sampling by colorcombinations.org; artwork public domain",
            snapshot_date=src["snapshot_date"],
            colors=[dict(hex=h, role=r, coverage_pct=parse_coverage(s["coverage_pct_text"])[0],
                         oklch=[round(v, 4) for v in cl.hex_to_oklch(h)])
                    for h, r, s in zip(hexes, roles, sw)],
        ))
    return rows, records


# --------------------------------------------------------------------------- kasane

_H4 = re.compile(r"^####\s+(.*)$")
_H3 = re.compile(r"^###\s+(.*)$")
_HEXTOK = re.compile(r"`(#[0-9A-Fa-f]{6})`")
_CJK = re.compile(r"[　-ヿ㐀-鿿＀-￯]")


def _split_heading(text: str) -> tuple[str, str, str]:
    """'Kōbai no nioi 紅梅の匡 — Red-plum gradation' -> (romaji, kanji, gloss)."""
    left, _, gloss = text.partition(" — ")
    toks = left.split()
    kanji_toks = [t for t in toks if _CJK.search(t)]
    romaji = " ".join(t for t in toks if not _CJK.search(t))
    return romaji.strip(), " ".join(kanji_toks), gloss.strip()


def parse_kasane(md_path: Path) -> list[dict]:
    season = ""
    out: list[dict] = []
    cur: dict | None = None
    in_palettes = False
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_palettes = line.strip() == "## Palettes"
            cur = None
            continue
        if not in_palettes:
            continue
        m3 = _H3.match(line)
        if m3 and not line.startswith("####"):
            season = m3.group(1).strip()
            cur = None
            continue
        m4 = _H4.match(line)
        if m4:
            romaji, kanji, gloss = _split_heading(m4.group(1))
            cur = dict(romaji=romaji, kanji=kanji, gloss=gloss, season=season, type="", hitoe=None,
                       layers=[], uwagi=None, kouchiki=None, seq=[])
            out.append(cur)
            continue
        if cur is None or not line.startswith("- **"):
            continue
        key = re.match(r"- \*\*(.+?):\*\*\s*(.*)$", line)
        if not key:
            continue
        k, v = key.group(1), key.group(2)
        if k == "Type":
            cur["type"] = v.strip()
        elif k.startswith("Hitoe"):
            cur["hitoe"] = _named_hex(v)
        elif k.startswith("Layers"):
            cur["layers"] = [_named_hex(p) for p in v.split("→")]
        elif k.startswith("Uwagi"):
            cur["uwagi"] = _named_hex(v)
        elif k.startswith("Kouchiki"):
            cur["kouchiki"] = _named_hex(v)
        elif k.startswith("Hex sequence"):
            cur["seq"] = [h.lower() for h in _HEXTOK.findall(v)]
    return out


def _named_hex(text: str) -> tuple[str, str]:
    m = _HEXTOK.search(text)
    if not m:
        raise SystemExit(f"kasane: no hex in {text!r}")
    name = text[: m.start()].strip()
    return name, m.group(1).lower()


def build_kasane(md_path: Path) -> list[dict]:
    pats = parse_kasane(md_path)
    rows, seen = [], set()
    for p in pats:
        entries = [("hitoe", p["hitoe"])]
        entries += [(f"layer{i + 1}", e) for i, e in enumerate(p["layers"])]
        if p["uwagi"]:
            entries.append(("uwagi", p["uwagi"]))
        if p["kouchiki"]:
            entries.append(("kouchiki", p["kouchiki"]))
        hexes = [e[1][1] for e in entries]
        if hexes != p["seq"]:
            raise SystemExit(f"kasane {p['romaji']}: layer list and hex sequence disagree")
        hexes = check_hexes(p["romaji"], hexes)
        slug = ascii_slug(p["romaji"])
        if slug in seen:
            raise SystemExit(f"kasane: duplicate slug {slug}")
        seen.add(slug)
        title = p["romaji"] + (f" ({p['gloss']})" if p["gloss"] else "")
        rows.append(dict(
            id=f"kasane-{slug}", source_type="kasane", title=title, title_ja=p["kanji"],
            colors=";".join(hexes), color_names=";".join(e[1][0] for e in entries),
            roles=";".join(e[0] for e in entries), coverage="", hue="", moods="",
            era="heian", season=p["season"], count=len(set(hexes)), drift="",
            tone_family=tone_family(hexes), label=label_kasane(p["romaji"]),
            source_url="references/kasane-no-irome.md", licence=LICENCE_KASANE,
        ))
    return rows


# --------------------------------------------------------------------------- colours


def _norm_name(name: str) -> str:
    s = re.sub(r"[^a-z]", "", name.lower())
    for wrong, right in SPELLING_ALIASES.items():
        s = s.replace(wrong, right)
    return s


def build_colors(raw: Path) -> list[dict]:
    site = read_csv(raw / "colors.csv")
    index = read_csv(raw / "wada-index.csv")
    by_name = {r["name"]: r for r in site}
    by_norm: dict[str, list[dict]] = {}
    for r in site:
        by_norm.setdefault(_norm_name(r["name"]), []).append(r)
    attach: dict[str, dict] = {}
    for ix in index:
        no = int(ix["no"])
        eng = ix["english"]
        target = None
        if no in DUPLICATE_INDEX_NAMES and DUPLICATE_INDEX_NAMES[no] in by_name:
            target = by_name[DUPLICATE_INDEX_NAMES[no]]
        elif eng in by_name:
            target = by_name[eng]
        else:
            cands = [c for c in by_norm.get(_norm_name(eng), []) if c["name"] not in DUPLICATE_INDEX_NAMES.values()]
            if len(cands) == 1:
                target = cands[0]
        if target is None:
            raise SystemExit(f"colour index row {no} ({eng}) matches no site colour")
        if target["slug"] in attach:
            raise SystemExit(f"two index rows map to {target['name']}")
        attach[target["slug"]] = ix
    rows = []
    for r in site:
        hx = cl.normalize_hex(r["hex"])
        L, c, h = cl.hex_to_oklch(hx)
        txt, ratio = cl.best_text_color(hx)
        ix = attach.get(r["slug"])
        aliases: list[str] = []
        d = dict(
            slug=r["slug"], name=r["name"], name_ja=r["name_ja"], meaning=r["meaning"], hex=hx,
            hue_family=r["hue"], palette_count=r["palette_count"], wada_no="", wada_kanji="", wada_kana="",
            wada_print_name="", cmyk="", oklch_l=f"{L:.4f}", oklch_c=f"{c:.4f}", oklch_h=f"{h:.2f}",
            best_text=txt, best_text_ratio=f"{ratio:.2f}", source_url=r["canonical_url"],
            licence=LICENCE_CC,
        )
        if ix:
            d.update(wada_no=ix["no"], wada_kanji=ix["kanji"], wada_kana=ix["kana"],
                     wada_print_name=ix["english"], licence=LICENCE_WADA,
                     cmyk=";".join(ix[k] for k in "cmyk"))
            if ix["english"] != r["name"]:
                aliases.append(ix["english"])
        d["aliases"] = ";".join(aliases)
        rows.append(d)
    return rows


# --------------------------------------------------------------------------- snapshot note

SNAP_BEGIN = "<!-- build_data:begin -->"
SNAP_END = "<!-- build_data:end -->"


def update_snapshot(path: Path, counts: dict[str, int]) -> None:
    block = [SNAP_BEGIN, "", "## Built data (scripts/build_data.py)", "",
             "| File | Rows | Notes |", "|---|---|---|"]
    block += [
        f"| palettes.csv | {counts['palettes']} | wada_plate {counts['wada_plate']}, editorial {counts['editorial']}, "
        f"painting {counts['painting']}, kasane {counts['kasane']} |",
        f"| colors.csv | {counts['colors']} | {counts['colors_with_wada_index']} carry a printed Wada index entry (CMYK, kanji) |",
        f"| paintings.json | {counts['paintings']} | 3 ground + 3 accent each; {counts['drift']} flagged for colour drift |",
        "", SNAP_END]
    text = path.read_text(encoding="utf-8") if path.exists() else "# Snapshot of colorcombinations.org data\n"
    text = text.replace("\r\n", "\n")
    if SNAP_BEGIN in text and SNAP_END in text:
        pre = text.split(SNAP_BEGIN)[0]
        post = text.split(SNAP_END, 1)[1]
        text = pre + "\n".join(block) + post
    else:
        text = text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------- main


def main(argv=None) -> int:
    cl.configure_stdio()
    root = cl.skill_root()
    ap = argparse.ArgumentParser(
        prog="build_data.py",
        description="Build data/palettes.csv, data/colors.csv, data/paintings.json from the raw snapshot "
                    "(build-time script; the skill ships the outputs).",
    )
    ap.add_argument("--raw", type=Path, default=root.parent.parent / "data-raw", help="raw snapshot folder (default: <repo>/data-raw)")
    ap.add_argument("--out", type=Path, default=root / "data", help="output folder (default: <skill>/data)")
    ap.add_argument("--kasane", type=Path, default=root / "references" / "kasane-no-irome.md", help="kasane reference markdown")
    args = ap.parse_args(argv)

    raw, out = args.raw, args.out
    dict_rows = build_dictionary_rows(raw)
    paint_rows, records = build_paintings(raw)
    kasane_rows = build_kasane(args.kasane)
    rows = [add_measured_columns(r) for r in dict_rows + paint_rows + kasane_rows]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate palette ids")
    write_csv(out / "palettes.csv", PALETTE_COLUMNS, rows)
    colours = build_colors(raw)
    write_csv(out / "colors.csv", COLOR_COLUMNS, colours)
    (out / "paintings.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    counts = {
        "palettes": len(rows),
        **{t: sum(1 for r in rows if r["source_type"] == t) for t in ("wada_plate", "editorial", "painting", "kasane")},
        "colors": len(colours),
        "colors_with_wada_index": sum(1 for c in colours if c["wada_no"]),
        "paintings": len(records),
        "drift": sum(1 for r in records if r["drift"]),
    }
    update_snapshot(out / "SNAPSHOT.md", counts)
    print(json.dumps(counts, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
