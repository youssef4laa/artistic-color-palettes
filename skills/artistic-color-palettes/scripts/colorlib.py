#!/usr/bin/env python3
"""colorlib.py - colour maths for the artistic-color-palettes skill (Python >= 3.10, stdlib only).

Written from the published formulas, not copied from any library:
  * sRGB <-> linear light (IEC 61966-2-1 transfer curve)
  * linear sRGB <-> OKLab <-> OKLCH (Bjorn Ottosson's matrices, published domain constants)
  * hex parsing (#rgb / #rrggbb), hex output
  * sRGB gamut test and max_chroma(L, h) (binary search, tolerance 1e-4)
  * WCAG 2.x relative luminance and contrast ratio
  * APCA-W3 0.0.98G-4g lightness contrast Lc (the SA98G constants)
  * delta E in OKLab (plain Euclidean distance, 0-1 scale)
  * colour-vision-deficiency simulation (Machado, Oliveira & Fernandes 2009 matrices,
    severity 1.0, applied to linear RGB)
  * alpha compositing in gamma-encoded sRGB (what a browser does)

Run `python3 scripts/colorlib.py --self-test` to check the test vectors from
notes/2-shared-constants.md (sources branch).  Run `python3 scripts/colorlib.py --help` for the CLI.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

# --------------------------------------------------------------------------- environment


def configure_stdio() -> None:
    """Make stdout/stderr UTF-8 (a Windows console defaults to cp1252 and crashes on Japanese)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass


def skill_root() -> Path:
    """The skill root: the folder that contains scripts/, data/, references/, assets/."""
    return Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- shared data helpers

DRIFT_NOTE = (
    "Sampled hex values show the work as it looks today; its colours are reported to have shifted "
    "since it was painted, so they are not the artist's original colours."
)


def data_dir() -> Path:
    return skill_root() / "data"


def load_palette_rows(path: Path | None = None) -> list[dict]:
    """Read data/palettes.csv (UTF-8) into a list of dicts."""
    import csv

    p = Path(path) if path else data_dir() / "palettes.csv"
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def row_members(row: dict) -> list[dict]:
    """Structured colours of a palettes.csv row: [{hex, name, role, coverage}] in table order."""
    hexes = [h for h in row["colors"].split(";") if h]
    names = row["color_names"].split(";") if row["color_names"] else [""] * len(hexes)
    roles = row["roles"].split(";") if row["roles"] else [""] * len(hexes)
    cov = row["coverage"].split(";") if row["coverage"] else [""] * len(hexes)
    return [{"hex": h, "name": names[i] if i < len(names) else "", "role": roles[i] if i < len(roles) else "",
             "coverage": cov[i] if i < len(cov) else ""} for i, h in enumerate(hexes)]


# --------------------------------------------------------------------------- hex handling

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def is_hex(value: object) -> bool:
    return isinstance(value, str) and _HEX_RE.match(value.strip()) is not None


def parse_hex(value: str) -> tuple[int, int, int]:
    """'#rgb' or '#rrggbb' (case-insensitive, '#' optional) -> (r, g, b) as 0-255 integers."""
    m = _HEX_RE.match(value.strip()) if isinstance(value, str) else None
    if not m:
        raise ValueError(f"not a hex colour: {value!r}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(rgb) -> str:
    """(r, g, b) as 0-255 numbers -> '#rrggbb' (lower case, rounded, clamped)."""
    return "#" + "".join(f"{max(0, min(255, int(round(c)))):02x}" for c in rgb)


def normalize_hex(value: str) -> str:
    return rgb_to_hex(parse_hex(value))


# --------------------------------------------------------------------------- sRGB <-> linear


def srgb_to_linear(c: float) -> float:
    """Encoded 0-1 -> linear light 0-1 (sign-preserving for out-of-range input)."""
    s = -1.0 if c < 0 else 1.0
    a = abs(c)
    return s * (a / 12.92 if a <= 0.04045 else ((a + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c: float) -> float:
    """Linear light -> encoded 0-1 (sign-preserving for out-of-range input)."""
    s = -1.0 if c < 0 else 1.0
    a = abs(c)
    return s * (12.92 * a if a <= 0.0031308 else 1.055 * a ** (1 / 2.4) - 0.055)


def hex_to_linear(value: str) -> tuple[float, float, float]:
    r, g, b = parse_hex(value)
    return srgb_to_linear(r / 255), srgb_to_linear(g / 255), srgb_to_linear(b / 255)


def linear_to_hex(r: float, g: float, b: float) -> str:
    return rgb_to_hex([255 * linear_to_srgb(min(1.0, max(0.0, c))) for c in (r, g, b)])


# --------------------------------------------------------------------------- OKLab / OKLCH


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def linear_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = _cbrt(l), _cbrt(m), _cbrt(s)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def oklab_to_oklch(L: float, a: float, b: float) -> tuple[float, float, float]:
    c = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360.0 if c > 1e-9 else 0.0
    return L, c, h


def oklch_to_oklab(L: float, C: float, h: float) -> tuple[float, float, float]:
    rad = math.radians(h)
    return L, C * math.cos(rad), C * math.sin(rad)


def hex_to_oklab(value: str) -> tuple[float, float, float]:
    return linear_to_oklab(*hex_to_linear(value))


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    return oklab_to_oklch(*hex_to_oklab(value))


def oklch_to_linear(L: float, C: float, h: float) -> tuple[float, float, float]:
    return oklab_to_linear(*oklch_to_oklab(L, C, h))


_GAMUT_EPS = 1e-6


def in_gamut(L: float, C: float, h: float, eps: float = _GAMUT_EPS) -> bool:
    """True when the OKLCH colour is inside the sRGB gamut (linear channels within [0, 1])."""
    return all(-eps <= c <= 1 + eps for c in oklch_to_linear(L, C, h))


@lru_cache(maxsize=65536)
def _max_chroma(L: float, h: float, tol: float) -> float:
    if L <= 0.0 or L >= 1.0:
        return 0.0
    lo, hi = 0.0, 0.45
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if in_gamut(L, mid, h):
            lo = mid
        else:
            hi = mid
    return lo


def max_chroma(L: float, h: float, tol: float = 1e-4) -> float:
    """Largest chroma that stays inside sRGB at lightness L and hue h (binary search)."""
    return _max_chroma(round(L, 6), round(h % 360.0, 6), tol)


def oklch_to_hex(L: float, C: float, h: float, refine: bool = True) -> str:
    """OKLCH -> '#rrggbb'.  Out-of-gamut colours keep L and h and lose chroma (never clipped per
    channel).  With refine=True the 8-bit rounding picks the nearest representable neighbour in
    OKLab, which keeps the measured L within a few thousandths of the target."""
    L = min(1.0, max(0.0, L))
    C = max(0.0, C)
    if not in_gamut(L, C, h):
        C = min(C, max_chroma(L, h))
    lin = oklch_to_linear(L, C, h)
    enc = [255 * linear_to_srgb(min(1.0, max(0.0, c))) for c in lin]
    base = [int(round(v)) for v in enc]
    if not refine:
        return rgb_to_hex(base)
    target = oklch_to_oklab(L, C, h)
    best, best_d = None, 1e9
    for dr in (-1, 0, 1):
        for dg in (-1, 0, 1):
            for db in (-1, 0, 1):
                cand = (base[0] + dr, base[1] + dg, base[2] + db)
                if any(v < 0 or v > 255 for v in cand):
                    continue
                lab = linear_to_oklab(*(srgb_to_linear(v / 255) for v in cand))
                d = (lab[0] - target[0]) ** 2 + (lab[1] - target[1]) ** 2 + (lab[2] - target[2]) ** 2
                if d < best_d:
                    best, best_d = cand, d
    return rgb_to_hex(best)


def format_oklch(L: float, C: float, h: float) -> str:
    """CSS Color 4 string, e.g. oklch(0.628 0.258 29.2)."""
    if C < 0.0005:
        h = 0.0
    return f"oklch({L:.3f} {C:.3f} {h:.1f})"


def hex_oklch_css(value: str) -> str:
    return format_oklch(*hex_to_oklch(value))


def hue_diff(h1: float, h2: float) -> float:
    """Smallest angle between two hues, 0-180 degrees."""
    d = abs((h1 - h2) % 360.0)
    return 360.0 - d if d > 180 else d


def delta_e_ok(a: str, b: str) -> float:
    """Euclidean distance in OKLab between two hex colours (0-1 scale; ~0.02 is a just-noticeable
    difference, ~0.05 is clearly visible)."""
    la, lb = hex_to_oklab(a), hex_to_oklab(b)
    return math.dist(la, lb)


# --------------------------------------------------------------------------- palette profile (build_data + search)

HUE_BUCKETS = ("red", "orange", "yellow", "green", "teal", "blue", "purple", "pink", "brown", "neutral")
CHROMATIC_MIN = 0.04  # OKLCH C below this reads as a (tinted) neutral for hue, temperature and tone
LIGHTNESS_BANDS = {"dark": (0.0, 0.50), "mid": (0.50, 0.72), "light": (0.72, 1.0001)}  # area-weighted mean L
CHROMA_BANDS = {"muted": (0.0, 0.11), "moderate": (0.11, 0.17), "vivid": (0.17, 1.0)}  # the most saturated colour
KASANE_HITOE_SHARE = 0.10  # the hitoe is an edge accent (the skill's 5-10 % convention); the layers share the rest


def hue_bucket(value: str) -> str:
    """Name a colour's hue family from OKLCH. Teal (170-215 degrees) is its own bucket, so turquoise and
    green-blue plates are not filed under blue; low chroma (C < CHROMATIC_MIN) is 'neutral'."""
    L, c, h = hex_to_oklch(value)
    if c < CHROMATIC_MIN:
        return "neutral"
    if h >= 335 or h < 12:
        return "pink" if L >= 0.6 or c < 0.12 else "red"
    if h < 40:
        return "red"
    if h < 80:
        return "brown" if L < 0.58 else "orange"
    if h < 122:
        return "brown" if (L < 0.5 and h < 100) else "yellow"
    if h < 170:
        return "green"
    if h < 215:
        return "teal"
    if h < 270:
        return "blue"
    return "purple"


def palette_weights(row: dict) -> list[float]:
    """Area weight of each colour of a palettes.csv row, summing to 1. Paintings: measured canvas coverage
    ('<1' counts as 0.5). Kasane: the hitoe edge KASANE_HITOE_SHARE, the layers share the rest. Wada plates
    and editorial palettes: equal (the plates show equal swatches)."""
    hexes = [h for h in row["colors"].split(";") if h]
    n = len(hexes)
    if row.get("source_type") == "painting" and row.get("coverage"):
        raw = [0.5 if c.strip().startswith("<") else float(c or 0) for c in row["coverage"].split(";")]
        if len(raw) == n and sum(raw) > 0:
            return [w / sum(raw) for w in raw]
    if row.get("source_type") == "kasane" and n > 1 and row.get("roles", "").split(";")[0] == "hitoe":
        return [KASANE_HITOE_SHARE] + [(1 - KASANE_HITOE_SHARE) / (n - 1)] * (n - 1)
    return [1.0 / n] * n if n else []


def band_of(value: float, bands: dict[str, tuple[float, float]]) -> str:
    return next(name for name, (lo, hi) in bands.items() if lo <= value < hi)


def palette_profile(row: dict) -> dict:
    """Measured description of a palette row: per-colour OKLCH, hue bucket and weight; the weighted mean L
    and its band; the most saturated colour's C and its band; the L range; hue shares by area; and the
    dominant hue (largest area-weighted chroma above CHROMATIC_MIN, so near-neutral grounds do not decide it)."""
    hexes = [h for h in row["colors"].split(";") if h]
    weights = palette_weights(row)
    colours = []
    for hx, w in zip(hexes, weights):
        L, c, h = hex_to_oklch(hx)
        colours.append({"hex": hx, "L": L, "C": c, "h": h, "bucket": hue_bucket(hx), "w": w})
    l_mean = sum(x["L"] * x["w"] for x in colours)
    c_max = max(x["C"] for x in colours)
    shares: dict[str, float] = {}
    force: dict[str, float] = {}
    for x in colours:
        shares[x["bucket"]] = shares.get(x["bucket"], 0.0) + x["w"]
        if x["bucket"] != "neutral":
            force[x["bucket"]] = force.get(x["bucket"], 0.0) + x["w"] * max(0.0, x["C"] - CHROMATIC_MIN)
    order = {b: i for i, b in enumerate(HUE_BUCKETS)}
    dominant = max(force.items(), key=lambda kv: (kv[1], -order[kv[0]]))[0] if force and max(force.values()) > 0 else "neutral"
    return {
        "colours": colours, "l_mean": l_mean, "lightness": band_of(l_mean, LIGHTNESS_BANDS),
        "c_max": c_max, "chroma": band_of(c_max, CHROMA_BANDS),
        "l_range": max(x["L"] for x in colours) - min(x["L"] for x in colours),
        "hue_shares": dict(sorted(shares.items(), key=lambda kv: (-kv[1], order[kv[0]]))), "dominant": dominant,
    }


# --------------------------------------------------------------------------- WCAG 2


def relative_luminance(value: str) -> float:
    r, g, b = hex_to_linear(value)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_contrast(fg: str, bg: str) -> float:
    """WCAG 2 contrast ratio (1-21), symmetric."""
    y1, y2 = relative_luminance(fg), relative_luminance(bg)
    hi, lo = (y1, y2) if y1 >= y2 else (y2, y1)
    return (hi + 0.05) / (lo + 0.05)


def best_text_color(bg: str, dark: str = "#111314", light: str = "#ffffff") -> tuple[str, float]:
    """Pick the near-black or near-white text colour that has the higher WCAG ratio on bg.
    Returns (hex, ratio)."""
    rd, rl = wcag_contrast(dark, bg), wcag_contrast(light, bg)
    return (dark, rd) if rd >= rl else (light, rl)


# --------------------------------------------------------------------------- APCA-W3 0.0.98G-4g

_APCA = dict(
    main_trc=2.4, s_r=0.2126729, s_g=0.7151522, s_b=0.0721750,
    norm_bg=0.56, norm_txt=0.57, rev_txt=0.62, rev_bg=0.65,
    blk_thrs=0.022, blk_clmp=1.414, scale_bow=1.14, scale_wob=1.14,
    lo_bow_offset=0.027, lo_wob_offset=0.027, delta_y_min=0.0005, lo_clip=0.1,
)


def _apca_luminance(value: str) -> float:
    r, g, b = parse_hex(value)
    p = _APCA
    y = (
        ((r / 255) ** p["main_trc"]) * p["s_r"]
        + ((g / 255) ** p["main_trc"]) * p["s_g"]
        + ((b / 255) ** p["main_trc"]) * p["s_b"]
    )
    if y < p["blk_thrs"]:
        y += (p["blk_thrs"] - y) ** p["blk_clmp"]
    return y


def apca_lc(text: str, background: str) -> float:
    """APCA lightness contrast Lc, signed: positive = dark text on light background, negative =
    light text on dark background.  Use abs() for a target comparison."""
    p = _APCA
    y_txt, y_bg = _apca_luminance(text), _apca_luminance(background)
    if abs(y_bg - y_txt) < p["delta_y_min"]:
        return 0.0
    if y_bg > y_txt:  # dark text on light background
        sapc = (y_bg ** p["norm_bg"] - y_txt ** p["norm_txt"]) * p["scale_bow"]
        out = 0.0 if sapc < p["lo_clip"] else sapc - p["lo_bow_offset"]
    else:  # light text on dark background
        sapc = (y_bg ** p["rev_bg"] - y_txt ** p["rev_txt"]) * p["scale_wob"]
        out = 0.0 if sapc > -p["lo_clip"] else sapc + p["lo_wob_offset"]
    return out * 100.0


# --------------------------------------------------------------------------- CVD simulation

# Machado, Oliveira & Fernandes (2009), severity 1.0, applied to linear RGB.
CVD_MATRICES = {
    "protan": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deutan": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritan": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def simulate_cvd(value: str, kind: str) -> str:
    """Hex as seen with protanopia / deuteranopia / tritanopia (severity 1.0)."""
    if kind not in CVD_MATRICES:
        raise ValueError(f"unknown CVD type {kind!r}; use one of {sorted(CVD_MATRICES)}")
    lin = hex_to_linear(value)
    m = CVD_MATRICES[kind]
    out = [sum(m[i][j] * lin[j] for j in range(3)) for i in range(3)]
    return linear_to_hex(*out)


# --------------------------------------------------------------------------- compositing / grey


def composite(fg: str, alpha: float, bg: str) -> str:
    """Source-over of fg at opacity alpha onto an opaque bg, in gamma-encoded sRGB."""
    a = min(1.0, max(0.0, alpha))
    f, b = parse_hex(fg), parse_hex(bg)
    return rgb_to_hex([a * f[i] + (1 - a) * b[i] for i in range(3)])


def to_greyscale(value: str) -> str:
    """Luminance-preserving grey (same WCAG relative luminance)."""
    y = min(1.0, max(0.0, relative_luminance(value)))
    g = 255 * linear_to_srgb(y)
    return rgb_to_hex([g, g, g])


# --------------------------------------------------------------------------- self test / CLI

TEST_VECTORS = {
    "apca #888888 on #ffffff": (lambda: apca_lc("#888888", "#ffffff"), 63.06),
    "apca #ffffff on #888888": (lambda: apca_lc("#ffffff", "#888888"), -68.54),
    "apca #000000 on #ffffff": (lambda: apca_lc("#000000", "#ffffff"), 106.04),
    "apca #ffffff on #000000": (lambda: apca_lc("#ffffff", "#000000"), -107.88),
    "wcag #777777 on #ffffff": (lambda: wcag_contrast("#777777", "#ffffff"), 4.48),
    "oklch #ff0000 L": (lambda: hex_to_oklch("#ff0000")[0], 0.628),
    "oklch #ff0000 C": (lambda: hex_to_oklch("#ff0000")[1], 0.2577),
    "oklch #ff0000 h": (lambda: hex_to_oklch("#ff0000")[2], 29.23),
}


def self_test() -> int:
    bad = 0
    for name, (fn, want) in TEST_VECTORS.items():
        got = fn()
        tol = 0.1 if name.startswith(("apca", "oklch #ff0000 h")) else 0.01
        if name.endswith(" L") or name.endswith(" C"):
            tol = 0.001
        ok = abs(got - want) <= tol
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}: got {got:.4f}, want {want}")
    return 1 if bad else 0


def _cli(argv=None) -> int:
    configure_stdio()
    ap = argparse.ArgumentParser(
        prog="colorlib.py",
        description="Colour maths helpers (OKLCH, WCAG 2, APCA, CVD). Inspect one or two hex colours.",
    )
    ap.add_argument("colors", nargs="*", help="one hex colour to inspect, or two (foreground background) to measure contrast")
    ap.add_argument("--self-test", action="store_true", help="reproduce the shared test vectors and exit")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.colors:
        ap.print_help()
        return 0
    import json

    out: dict = {}
    try:
        for i, c in enumerate(args.colors[:2]):
            hx = normalize_hex(c)
            L, C, h = hex_to_oklch(hx)
            out[f"color{i + 1}"] = {
                "hex": hx, "oklch": [round(L, 4), round(C, 4), round(h, 2)], "css": format_oklch(L, C, h),
                "max_chroma_at_L_h": round(max_chroma(L, h), 4),
                "cvd": {k: simulate_cvd(hx, k) for k in CVD_MATRICES},
            }
        if len(args.colors) >= 2:
            fg, bg = out["color1"]["hex"], out["color2"]["hex"]
            out["wcag_ratio"] = round(wcag_contrast(fg, bg), 2)
            out["apca_lc"] = round(apca_lc(fg, bg), 1)
            out["delta_e_ok"] = round(delta_e_ok(fg, bg), 4)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
