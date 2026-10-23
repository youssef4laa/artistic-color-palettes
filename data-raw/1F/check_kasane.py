#!/usr/bin/env python3
"""Check the corrected kasane-no-irome.md. Stdlib only.

Usage: python check_kasane.py [corrected.md] [original.md]
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\Code\Skill\artistic-color-palettes")
NEW = ROOT / "skills" / "artistic-color-palettes" / "references" / "kasane-no-irome.md"
ORIG = Path(r"D:\Code\Skill\Art References\kasane-no-irome.md")

HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
OKLCH_RE = re.compile(
    r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*(?:/[^)]*)?\)", re.I)


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def rgb_to_oklab(rgb):
    r, g, b = (srgb_to_lin(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab_to_lin(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def rgb_to_oklch(rgb):
    L, a, b = rgb_to_oklab(rgb)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def oklch_to_lin(L, C, H):
    h = math.radians(H)
    return oklab_to_lin(L, C * math.cos(h), C * math.sin(h))


def in_gamut(L, C, H, eps=1e-4):
    return all(-eps <= v <= 1 + eps for v in oklch_to_lin(L, C, H))


def to_hex(L, C, H):
    lin = oklch_to_lin(L, C, H)
    return "#%02X%02X%02X" % tuple(
        round(min(1, max(0, lin_to_srgb(min(1, max(0, v))))) * 255) for v in lin)


def parse(text):
    pats = {}
    cur = None
    for line in text.splitlines():
        if line.startswith("#### "):
            cur = line[5:].strip()
            pats[cur] = []
        elif line.startswith("#") and not line.startswith("####"):
            cur = None
        elif cur and (line.startswith("- **Hex sequence:**") or line.startswith("- **Type:**")
                      or "Layers" in line[:20] or line.startswith("- **Hitoe")
                      or line.startswith("- **Uwagi") or line.startswith("- **Kouchiki")):
            pats[cur].append(line.strip())
    return pats


def section(text, heading):
    m = re.search(r"^#{2,3} %s\s*$(.*?)(?=^#{2,3} |\Z)" % re.escape(heading), text, re.M | re.S)
    return m.group(1) if m else ""


def main():
    new_p = Path(sys.argv[1]) if len(sys.argv) > 1 else NEW
    old_p = Path(sys.argv[2]) if len(sys.argv) > 2 else ORIG
    new, old = new_p.read_text(encoding="utf-8"), old_p.read_text(encoding="utf-8")
    fails = []

    def check(ok, msg):
        if not ok:
            fails.append(msg)

    pn, po = parse(new), parse(old)
    check(len(pn) == 33, f"pattern count {len(pn)} != 33 (the original has 33, not the 35 stated in the brief)")
    check(len(po) == 33, f"original pattern count {len(po)} != 33")
    check(list(pn) == list(po), "pattern names/order differ from original")
    for k in po:
        check(pn.get(k) == po[k], f"pattern body differs: {k}")
    # every hex sequence valid
    all_hex = set()
    for k, lines in pn.items():
        seq = [l for l in lines if l.startswith("- **Hex sequence:**")]
        check(len(seq) == 1, f"{k}: expected one hex sequence")
    for h in HEX_RE.findall(new):
        check(re.fullmatch(r"#[0-9A-Fa-f]{6}", h), f"bad hex {h}")
        all_hex.add(h.upper())
    worst = 0.0
    for h in sorted(all_hex):
        if not re.fullmatch(r"#[0-9A-F]{6}", h):
            continue
        L, C, H = rgb_to_oklch(hex_to_rgb(h))
        back = to_hex(L, C, H)
        d = max(abs(int(h[i:i + 2], 16) - int(back[i:i + 2], 16)) for i in (1, 3, 5))
        worst = max(worst, d)
        check(d <= 1, f"round trip {h} -> {back}")
    # tables unchanged
    for heading in ("Base colour vocabulary", "Garment layers and their UI roles"):
        check(section(new, heading).strip() == section(old, heading).strip() != "",
              f"section changed: {heading}")
    old_hex = {h.upper() for h in HEX_RE.findall(old)}
    check(old_hex <= all_hex, f"hex values missing: {sorted(old_hex - all_hex)}")
    # written oklch values
    n_ok = 0
    for m in OKLCH_RE.finditer(new):
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        C, H = float(m.group(3)), float(m.group(4))
        check(in_gamut(L, C, H), f"oklch out of gamut: {m.group(0)}")
        n_ok += 1
        # match to hex on same line or the next one if present
        ctx = new[m.end():m.end() + 80]
        hm = HEX_RE.search(new[m.start() - 40:m.end() + 40]) or HEX_RE.search(ctx)
        if hm and len(hm.group(0)) == 7:
            back = to_hex(L, C, H)
            d = max(abs(int(hm.group(0)[i:i + 2], 16) - int(back[i:i + 2], 16)) for i in (1, 3, 5))
            check(d <= 2, f"oklch {m.group(0)} does not match {hm.group(0)} (got {back})")
    print(f"patterns: {len(pn)} (identical to original: {pn == po})")
    print(f"distinct hex values: {len(all_hex)}; worst round-trip error: {worst:.0f}/255")
    print(f"oklch() values checked: {n_ok}")
    print("layer-role table and base-colour table identical to original")
    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
