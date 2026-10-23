"""Stdlib colour maths for the 2G worked examples (build-time only, not shipped).

OKLab / OKLCH (Ottosson 2020), sRGB gamut search for Cmax(L, h), WCAG 2 contrast,
APCA-W3 0.0.98G-4g Lc. Ramp construction follows notes/2-shared-constants.md exactly.
Run `python colour.py` to check the shared-constants test vectors.
"""
from __future__ import annotations

import math
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- sRGB <-> linear

def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb)


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


# ---------------------------------------------------------------- OKLab / OKLCH

def linear_to_oklab(r: float, g: float, b: float):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear(L: float, a: float, b: float):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def hex_to_oklch(h: str):
    L, a, b = linear_to_oklab(*(srgb_to_linear(c) for c in hex_to_rgb(h)))
    C = math.hypot(a, b)
    hue = math.degrees(math.atan2(b, a)) % 360 if C > 1e-6 else 0.0
    return L, C, hue


def oklch_to_linear(L: float, C: float, h: float):
    a = C * math.cos(math.radians(h))
    b = C * math.sin(math.radians(h))
    return oklab_to_linear(L, a, b)


def in_gamut(L: float, C: float, h: float, eps: float = 1e-6) -> bool:
    return all(-eps <= c <= 1 + eps for c in oklch_to_linear(L, C, h))


def oklch_to_hex(L: float, C: float, h: float) -> str:
    lin = oklch_to_linear(L, C, h)
    return rgb_to_hex(tuple(linear_to_srgb(max(0.0, min(1.0, c))) for c in lin))


def cmax(L: float, h: float, tol: float = 1e-4) -> float:
    """Largest in-sRGB-gamut chroma at this L and h (binary search)."""
    lo, hi = 0.0, 0.5
    if not in_gamut(L, 0.0, h):
        return 0.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if in_gamut(L, mid, h):
            lo = mid
        else:
            hi = mid
    return lo


def fmt_oklch(h: str) -> str:
    L, C, hue = hex_to_oklch(h)
    return f"oklch({L:.3f} {C:.4f} {hue:.2f})"


# ---------------------------------------------------------------- WCAG 2

def wcag_luminance(h: str) -> float:
    r, g, b = (srgb_to_linear(c) for c in hex_to_rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_ratio(fg: str, bg: str) -> float:
    l1, l2 = wcag_luminance(fg), wcag_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- APCA-W3 0.0.98G-4g

def _apca_y(h: str) -> float:
    r, g, b = hex_to_rgb(h)
    y = (r ** 2.4) * 0.2126729 + (g ** 2.4) * 0.7151522 + (b ** 2.4) * 0.0721750
    if y < 0.022:  # soft black clamp
        y += (0.022 - y) ** 1.414
    return y


def apca_lc(text: str, bg: str) -> float:
    ytxt, ybg = _apca_y(text), _apca_y(bg)
    if abs(ybg - ytxt) < 0.0005:
        return 0.0
    if ybg > ytxt:  # dark text on light background
        sapc = (ybg ** 0.56 - ytxt ** 0.57) * 1.14
        out = 0.0 if sapc < 0.1 else sapc - 0.027
    else:  # light text on dark background
        sapc = (ybg ** 0.65 - ytxt ** 0.62) * 1.14
        out = 0.0 if sapc > -0.1 else sapc + 0.027
    return out * 100


# ---------------------------------------------------------------- shared constants

STEPS = (50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950)
LIGHT_L = dict(zip(STEPS, (0.975, 0.935, 0.885, 0.810, 0.720, 0.630, 0.540, 0.460, 0.380, 0.300, 0.240)))
DARK_L = dict(zip(STEPS, (0.960, 0.900, 0.810, 0.710, 0.610, 0.510, 0.420, 0.340, 0.270, 0.210, 0.160)))
PROFILE = dict(zip(STEPS, (0.15, 0.25, 0.40, 0.60, 0.80, 0.95, 1.00, 0.92, 0.80, 0.65, 0.50)))
NEUTRAL_N = dict(zip(STEPS, (0.006, 0.010, 0.014, 0.018, 0.020, 0.020, 0.020, 0.018, 0.016, 0.014, 0.012)))
DARK_SURFACE_CAP = 0.045
NEUTRAL_CAP = 0.03


def seed_share(seed_hex: str) -> float:
    L, C, h = hex_to_oklch(seed_hex)
    cm = cmax(L, h)
    return C / cm if cm > 0 else 0.0


def nearest_step(L: float, table: dict) -> int:
    return min(table, key=lambda s: abs(table[s] - L))


def build_ramp(seed_hex: str, mode: str = "light", pin: bool = True) -> dict[int, str]:
    """Accent/voice ramp per shared constants §2. Returns {step: hex}."""
    L0, C0, h = hex_to_oklch(seed_hex)
    s = seed_share(seed_hex)
    table = LIGHT_L if mode == "light" else DARK_L
    mult = 1.0 if mode == "light" else 0.85
    out = {}
    pinned = nearest_step(L0, table) if pin else None
    for step in STEPS:
        if step == pinned:
            out[step] = seed_hex.lower()
            continue
        L = table[step]
        C = s * PROFILE[step] * mult * cmax(L, h)
        if mode == "dark" and step in (800, 900, 950):
            C = min(C, DARK_SURFACE_CAP)
        out[step] = oklch_to_hex(L, C, h)
    return out


def build_neutral(tint_hex: str, mode: str = "light", tint: float = 1.0) -> dict[int, str]:
    _, _, h = hex_to_oklch(tint_hex)
    table = LIGHT_L if mode == "light" else DARK_L
    return {step: oklch_to_hex(table[step], min(NEUTRAL_CAP, tint * NEUTRAL_N[step]), h) for step in STEPS}


def pair(fg: str, bg: str) -> str:
    return f"WCAG {wcag_ratio(fg, bg):.2f}:1, APCA Lc {apca_lc(fg, bg):+.1f}"


def flags(a: str, b: str) -> list[str]:
    """Vibrating / vanishing flags for an adjacent pair (shared §3)."""
    La, Ca, ha = hex_to_oklch(a)
    Lb, Cb, hb = hex_to_oklch(b)
    dh = abs((ha - hb + 180) % 360 - 180)
    out = []
    if dh >= 100 and Ca >= 0.10 and Cb >= 0.10 and abs(La - Lb) < 0.15:
        out.append("VIBRATING")
    if abs(La - Lb) < 0.10 and dh < 40:
        out.append("VANISHING")
    return out


def self_test() -> None:
    checks = [
        ("APCA #888888 on #ffffff", apca_lc("#888888", "#ffffff"), 63.06),
        ("APCA #ffffff on #888888", apca_lc("#ffffff", "#888888"), -68.54),
        ("APCA #000000 on #ffffff", apca_lc("#000000", "#ffffff"), 106.04),
        ("APCA #ffffff on #000000", apca_lc("#ffffff", "#000000"), -107.88),
        ("WCAG #777777 on #ffffff", wcag_ratio("#777777", "#ffffff"), 4.48),
    ]
    ok = True
    for name, got, want in checks:
        good = abs(got - want) <= 0.1 if "APCA" in name else abs(got - want) <= 0.01
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} {name}: {got:.2f} (want {want})")
    L, C, h = hex_to_oklch("#ff0000")
    good = abs(L - 0.628) < 0.001 and abs(C - 0.2577) < 0.0005 and abs(h - 29.23) < 0.01
    ok &= good
    print(f"{'PASS' if good else 'FAIL'} OKLCH #ff0000: L {L:.3f} C {C:.4f} h {h:.2f} (want 0.628 0.2577 29.23)")
    print("ALL PASS" if ok else "SOME FAILED")


if __name__ == "__main__":
    self_test()
