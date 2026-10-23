"""Measured numbers for the three worked examples in references/style-recipes.md.

Build-time only. Every contrast figure printed here is what the reference file quotes.
Usage: python -I examples.py  (stdlib only; colour.py beside it)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from colour import (  # noqa: E402
    DARK_L, LIGHT_L, STEPS, apca_lc, build_neutral, build_ramp, cmax, flags, fmt_oklch,
    hex_to_oklch, nearest_step, oklch_to_hex, seed_share, wcag_ratio,
)

sys.stdout.reconfigure(encoding="utf-8")

# Default status seeds (the skill's own convention, see application-rules.md §6)
STATUS_SEEDS = {
    "danger": oklch_to_hex(0.55, 0.19, 27),
    "warning": oklch_to_hex(0.72, 0.15, 72),
    "success": oklch_to_hex(0.55, 0.14, 150),
    "info": oklch_to_hex(0.55, 0.13, 250),
}


def describe(name: str, h: str) -> None:
    L, C, hue = hex_to_oklch(h)
    cm = cmax(L, hue)
    print(f"  {name:<28} {h}  {fmt_oklch(h)}  Cmax {cm:.4f}  share {seed_share(h):.3f}"
          f"  nearest light step {nearest_step(L, LIGHT_L)}, dark step {nearest_step(L, DARK_L)}")


def ramp_line(label: str, ramp: dict[int, str], pinned: int | None = None) -> None:
    cells = []
    for s in STEPS:
        L, C, _ = hex_to_oklch(ramp[s])
        mark = "*" if s == pinned else ""
        cells.append(f"{s}{mark} {ramp[s]} (L {L:.3f} C {C:.3f})")
    print(f"  {label}:")
    for c in cells:
        print(f"    {c}")


def measure(label: str, fg: str, bg: str, gate: float) -> bool:
    r = wcag_ratio(fg, bg)
    lc = apca_lc(fg, bg)
    ok = r >= gate
    fl = flags(fg, bg)
    print(f"  {'PASS' if ok else 'FAIL'} {label:<52} {fg} on {bg}: WCAG {r:.2f}:1  APCA Lc {lc:+.1f}"
          f"{'  ' + ' '.join(fl) if fl else ''}")
    return ok


def adjust_L(fg: str, bg: str, gate: float, direction: int, step: float = 0.01) -> str:
    """Move fg's L only (C and h kept; C reduced only if gamut forces it) until WCAG >= gate."""
    L, C, h = hex_to_oklch(fg)
    cur = fg
    n = 0
    while wcag_ratio(cur, bg) < gate and 0.05 < L < 0.98 and n < 60:
        L += direction * step
        Cc = min(C, cmax(L, h))
        cur = oklch_to_hex(L, Cc, h)
        n += 1
    return cur


def adjust_apca(label: str, fg: str, bg: str, target: float, direction: int, step: float = 0.01) -> str:
    """APCA target adjustment: move fg's L only until |Lc| >= target; report before/after."""
    L, C, h = hex_to_oklch(fg)
    cur, n = fg, 0
    while abs(apca_lc(cur, bg)) < target and 0.05 < L < 0.98 and n < 60:
        L += direction * step
        cur = oklch_to_hex(L, min(C, cmax(L, h)), h)
        n += 1
    L0 = hex_to_oklch(fg)[0]
    L1, C1, _ = hex_to_oklch(cur)
    print(f"  ADJUST {label}: {fg} (L {L0:.3f}, WCAG {wcag_ratio(fg, bg):.2f}, Lc {apca_lc(fg, bg):+.1f})"
          f" -> {cur} (L {L1:.3f} C {C1:.3f}, WCAG {wcag_ratio(cur, bg):.2f}, Lc {apca_lc(cur, bg):+.1f}) on {bg}")
    return cur


def polarity(label: str, fill: str, light: str, dark: str, gate: float = 4.5) -> None:
    """Mid-lightness trap: measure both text polarities on a fill and choose by the gate."""
    rl, ll = wcag_ratio(light, fill), apca_lc(light, fill)
    rd, ld = wcag_ratio(dark, fill), apca_lc(dark, fill)
    Lf = hex_to_oklch(fill)[0]
    trap = "  [mid-lightness trap L 0.50-0.70]" if 0.50 <= Lf <= 0.70 else ""
    print(f"  {label} fill {fill} (L {Lf:.3f}){trap}")
    print(f"     light text {light}: WCAG {rl:.2f}:1 APCA {ll:+.1f}   dark text {dark}: WCAG {rd:.2f}:1 APCA {ld:+.1f}"
          f"   -> {'light' if rl >= rd else 'dark'} wins WCAG; {'light' if abs(ll) >= abs(ld) else 'dark'} wins APCA")


def status_block(neutral_light: dict, neutral_dark: dict) -> None:
    print("  Default status seeds and their solid/text pairs:")
    for name, seed in STATUS_SEEDS.items():
        lr = build_ramp(seed, "light", pin=False)
        dr = build_ramp(seed, "dark", pin=False)
        print(f"    {name:<8} seed {seed} {fmt_oklch(seed)}")
        measure(f"{name} text (light 700) on bg (neutral-50)", lr[700], neutral_light[50], 4.5)
        measure(f"{name} solid (light 600) as non-text on neutral-50", lr[600], neutral_light[50], 3.0)
        measure(f"{name} text (dark 300) on bg (neutral-950)", dr[300], neutral_dark[950], 4.5)


# =============================================================== Example (a)

def example_a() -> None:
    print("\n" + "=" * 100)
    print("EXAMPLE (a): SaaS analytics dashboard, Operate, Restrained, Wada plate 218")
    helvetia, lavender, plumbeous = "#005b8d", "#b5b1d8", "#70727c"
    describe("Helvetia Blue", helvetia)
    describe("Grayish Lavender - A", lavender)
    describe("Deep Violet / Plumbeous", plumbeous)

    acc_l = build_ramp(helvetia, "light")
    acc_d = build_ramp(helvetia, "dark")
    voi_l = build_ramp(lavender, "light")
    voi_d = build_ramp(lavender, "dark")
    neu_l = build_neutral(plumbeous, "light")
    neu_d = build_neutral(plumbeous, "dark")
    ramp_line("accent light (Helvetia Blue)", acc_l, nearest_step(hex_to_oklch(helvetia)[0], LIGHT_L))
    ramp_line("accent dark (Helvetia Blue)", acc_d, nearest_step(hex_to_oklch(helvetia)[0], DARK_L))
    ramp_line("voice-1 light (Grayish Lavender A)", voi_l, nearest_step(hex_to_oklch(lavender)[0], LIGHT_L))
    ramp_line("voice-1 dark (Grayish Lavender A)", voi_d, nearest_step(hex_to_oklch(lavender)[0], DARK_L))
    ramp_line("neutral light (tinted from Plumbeous hue)", neu_l)
    ramp_line("neutral dark (tinted from Plumbeous hue)", neu_d)

    print("\n  LIGHT MODE pairs")
    measure("text (neutral-900) on bg (neutral-50)", neu_l[900], neu_l[50], 4.5)
    measure("text-muted (neutral-700) on bg (neutral-50)", neu_l[700], neu_l[50], 4.5)
    measure("text (neutral-900) on surface-hover (neutral-200)", neu_l[900], neu_l[200], 4.5)
    measure("border (neutral-300) non-text on bg", neu_l[300], neu_l[50], 3.0)
    measure("accent-text/link (accent-700 = pinned Helvetia) on bg", acc_l[700], neu_l[50], 4.5)
    measure("accent solid (accent-600) non-text on bg", acc_l[600], neu_l[50], 3.0)
    polarity("accent-600 fill text polarity", acc_l[600], neu_l[50], neu_l[950])
    polarity("accent-700 (pinned) fill text polarity", acc_l[700], neu_l[50], neu_l[950])
    polarity("Plumbeous as a rail fill", plumbeous, neu_l[50], neu_l[950])
    measure("focus ring (accent-500) non-text on bg", acc_l[500], neu_l[50], 3.0)
    measure("text on accent-subtle (neutral-900 on accent-100)", neu_l[900], acc_l[100], 4.5)
    measure("accent-text on accent-subtle (accent-700 on accent-100)", acc_l[700], acc_l[100], 4.5)
    measure("voice-1 solid (pinned lavender 300) non-text on bg", voi_l[300], neu_l[50], 3.0)
    measure("text on voice-1-subtle (neutral-900 on voice-100)", neu_l[900], voi_l[100], 4.5)
    measure("voice-1 text (voice-700) on bg", voi_l[700], neu_l[50], 4.5)
    measure("chart series: voice-1-500 non-text on bg", voi_l[500], neu_l[50], 3.0)
    measure("chart series: accent-500 vs voice-1-500 adjacency", acc_l[500], voi_l[500], 1.0)
    print("  rail: Helvetia Blue 700 pinned as shell rail; rail text neutral-50")
    measure("rail text (neutral-50) on rail (accent-700 pinned)", neu_l[50], acc_l[700], 4.5)
    measure("rail muted text (accent-100) on rail", acc_l[100], acc_l[700], 4.5)
    measure("rail selected item (accent-800) non-text vs rail", acc_l[800], acc_l[700], 1.0)
    measure("rail selected item (accent-900) vs rail (dL fix)", acc_l[900], acc_l[700], 1.0)
    measure("rail selected pill (neutral-50) vs rail", neu_l[50], acc_l[700], 3.0)
    print("  border-strong candidates (meaning-bearing boundary needs >= 3.0)")
    measure("neutral-400 non-text on bg", neu_l[400], neu_l[50], 3.0)
    measure("neutral-500 non-text on bg", neu_l[500], neu_l[50], 3.0)
    measure("neutral-600 non-text on bg", neu_l[600], neu_l[50], 3.0)
    measure("neutral-500 non-text on surface-hover (neutral-200)", neu_l[500], neu_l[200], 3.0)
    measure("neutral-600 non-text on surface-hover (neutral-200)", neu_l[600], neu_l[200], 3.0)
    print("  info status re-seeded on voice-1 hue (accent hue 243 is within 15 deg of the default info 250)")
    info_alt = oklch_to_hex(0.55, 0.13, 290)
    ia_l, ia_d = build_ramp(info_alt, "light", pin=False), build_ramp(info_alt, "dark", pin=False)
    print(f"    info-alt seed {info_alt} {fmt_oklch(info_alt)}")
    measure("info-alt text (light 700) on bg", ia_l[700], neu_l[50], 4.5)
    measure("info-alt solid (light 600) non-text on bg", ia_l[600], neu_l[50], 3.0)
    measure("info-alt text (dark 300) on bg (neutral-950)", ia_d[300], neu_d[950], 4.5)
    print("  Albers 3 check: accent hue vs neutral hue")
    for n, h in (("accent", helvetia), ("voice-1", lavender), ("neutral", plumbeous)):
        print(f"    {n} hue {hex_to_oklch(h)[2]:.1f}")
    status_block(neu_l, neu_d)

    print("\n  DARK MODE pairs")
    measure("text (neutral-50) on bg (neutral-950)", neu_d[50], neu_d[950], 4.5)
    measure("text-muted (neutral-300) on bg (neutral-950)", neu_d[300], neu_d[950], 4.5)
    measure("text (neutral-50) on surface (neutral-900)", neu_d[50], neu_d[900], 4.5)
    measure("border (neutral-700) non-text on bg (neutral-950)", neu_d[700], neu_d[950], 3.0)
    measure("link (accent-300) on bg (neutral-950)", acc_d[300], neu_d[950], 4.5)
    measure("accent solid (accent-500) non-text on bg", acc_d[500], neu_d[950], 3.0)
    polarity("dark accent-500 fill text polarity", acc_d[500], neu_d[50], neu_d[950])
    polarity("dark accent-400 fill text polarity", acc_d[400], neu_d[50], neu_d[950])
    measure("focus (accent-400) non-text on bg", acc_d[400], neu_d[950], 3.0)
    measure("text on accent-subtle (neutral-50 on accent-900)", neu_d[50], acc_d[900], 4.5)
    measure("voice-1 text (voice-300) on bg", voi_d[300], neu_d[950], 4.5)
    measure("rail dark: neutral-50 on accent-700 (dark ramp)", neu_d[50], acc_d[700], 4.5)
    measure("rail dark: neutral-50 on accent-600 (= pinned Helvetia)", neu_d[50], acc_d[600], 4.5)
    measure("dark border-strong: neutral-500 non-text on bg", neu_d[500], neu_d[950], 3.0)
    measure("dark border-strong: neutral-400 non-text on bg", neu_d[400], neu_d[950], 3.0)
    measure("dark chart: voice-1 dark-400 non-text on bg", voi_d[400], neu_d[950], 3.0)
    measure("dark chart: voice-1 dark-300 non-text on bg", voi_d[300], neu_d[950], 3.0)
    print("  APCA-target adjustments (gate already passed; L moved toward target)")
    adjust_apca("dark link accent-300 -> Lc 75", acc_d[300], neu_d[950], 75, +1)
    adjust_apca("dark muted neutral-300 -> Lc 60", neu_d[300], neu_d[950], 60, +1)
    dr = build_ramp(STATUS_SEEDS["danger"], "dark", pin=False)
    measure("danger text (dark 200) on bg", dr[200], neu_d[950], 4.5)
    print("  Interval check (Albers 7): dL text/bg light vs dark")
    print(f"    light text/bg dL {abs(hex_to_oklch(neu_l[900])[0]-hex_to_oklch(neu_l[50])[0]):.3f}; "
          f"dark {abs(hex_to_oklch(neu_d[50])[0]-hex_to_oklch(neu_d[950])[0]):.3f}")
    print(f"    light accent-fill/bg dL {abs(hex_to_oklch(acc_l[600])[0]-hex_to_oklch(neu_l[50])[0]):.3f}; "
          f"dark {abs(hex_to_oklch(acc_d[500])[0]-hex_to_oklch(neu_d[950])[0]):.3f}")


# =============================================================== Example (b)

def example_b() -> None:
    print("\n" + "=" * 100)
    print("EXAMPLE (b): poster landing page, Persuade, Drenched, Wada plate 247")
    sienna, apricot, benzol, lyons = "#bb7125", "#ffdd00", "#00978d", "#1c4286"
    for n, h in (("Raw Sienna (top)", sienna), ("Apricot Yellow (bottom)", apricot),
                 ("Benzol Green (mid-left)", benzol), ("Deep Lyons Blue (mid-right)", lyons)):
        describe(n, h)
    ly_l, ly_d = build_ramp(lyons, "light"), build_ramp(lyons, "dark")
    bz_l, bz_d = build_ramp(benzol, "light"), build_ramp(benzol, "dark")
    ap_l, ap_d = build_ramp(apricot, "light"), build_ramp(apricot, "dark")
    si_l, si_d = build_ramp(sienna, "light"), build_ramp(sienna, "dark")
    neu_l, neu_d = build_neutral(lyons, "light"), build_neutral(lyons, "dark")
    ramp_line("ground ramp light (Deep Lyons Blue)", ly_l, nearest_step(hex_to_oklch(lyons)[0], LIGHT_L))
    ramp_line("ground ramp dark (Deep Lyons Blue)", ly_d, nearest_step(hex_to_oklch(lyons)[0], DARK_L))
    ramp_line("surface ramp light (Benzol Green)", bz_l, nearest_step(hex_to_oklch(benzol)[0], LIGHT_L))
    ramp_line("accent ramp light (Apricot Yellow)", ap_l, nearest_step(hex_to_oklch(apricot)[0], LIGHT_L))
    ramp_line("accent ramp dark (Apricot Yellow)", ap_d, nearest_step(hex_to_oklch(apricot)[0], DARK_L))
    ramp_line("voice ramp light (Raw Sienna)", si_l, nearest_step(hex_to_oklch(sienna)[0], LIGHT_L))
    ramp_line("neutral light (tinted from Lyons hue)", neu_l)
    ramp_line("neutral dark (tinted from Lyons hue)", neu_d)

    print("\n  LIGHT (default) appearance: the page IS Deep Lyons Blue")
    measure("body text (neutral-50) on ground (Lyons pinned)", neu_l[50], lyons, 4.5)
    measure("muted text (ground-ramp 100, tinted from blue) on ground", ly_l[100], lyons, 4.5)
    measure("headline (Apricot Yellow pinned) on ground", apricot, lyons, 3.0)
    measure("Apricot Yellow as non-text mark on ground", apricot, lyons, 3.0)
    polarity("CTA fill = Apricot Yellow (pinned)", apricot, neu_l[50], neu_l[950])
    polarity("Benzol Green band", benzol, neu_l[50], neu_l[950])
    measure("Benzol band adjacent to Lyons ground (fill/fill)", benzol, lyons, 1.0)
    polarity("Raw Sienna band", sienna, neu_l[50], neu_l[950])
    measure("Raw Sienna adjacent to Lyons ground (fill/fill)", sienna, lyons, 1.0)
    measure("Raw Sienna adjacent to Benzol (fill/fill)", sienna, benzol, 1.0)
    measure("Apricot adjacent to Benzol (fill/fill)", apricot, benzol, 1.0)
    measure("Apricot adjacent to Raw Sienna (fill/fill)", apricot, sienna, 1.0)
    measure("large text Raw Sienna-200 on ground", si_l[200], lyons, 3.0)
    measure("large text Benzol-200 on ground", bz_l[200], lyons, 3.0)
    measure("card surface (ground-ramp 800) text neutral-50", neu_l[50], ly_l[800], 4.5)
    measure("card surface (ground-ramp 800) vs ground adjacency", ly_l[800], lyons, 1.0)
    measure("focus ring (Apricot) on ground non-text", apricot, lyons, 3.0)
    measure("focus ring (Apricot) on Benzol band non-text", apricot, benzol, 3.0)
    measure("focus ring (neutral-50) on Benzol band non-text", neu_l[50], benzol, 3.0)
    print("  Body-copy band: the fill role moves to a generated step, the pinned Benzol stays for the graphic band")
    measure("body text (neutral-50) on Benzol-600 (generated)", neu_l[50], bz_l[600], 4.5)
    measure("body text (neutral-50) on Benzol-700 (generated)", neu_l[50], bz_l[700], 4.5)
    measure("Benzol-600 vs Benzol pinned adjacency", bz_l[600], benzol, 1.0)
    measure("Benzol-700 vs Benzol pinned adjacency", bz_l[700], benzol, 1.0)
    measure("Benzol-700 vs Lyons ground adjacency", bz_l[700], lyons, 1.0)
    print("  Raised panel on the drenched ground")
    measure("panel ground-950 vs ground adjacency", ly_l[950], lyons, 1.0)
    measure("body text (neutral-50) on panel ground-950", neu_l[50], ly_l[950], 4.5)
    measure("panel ground-600 vs ground adjacency", ly_l[600], lyons, 1.0)
    polarity("panel ground-600 text polarity", ly_l[600], neu_l[50], neu_l[950])
    measure("Raw Sienna large text? pinned on ground (large gate 3.0)", sienna, lyons, 3.0)
    print("  Adjustment demo: Benzol band dark text")
    before = neu_l[950]
    print(f"    neutral-950 {before} on Benzol: WCAG {wcag_ratio(before, benzol):.2f}")
    print("  Adjustment demo: white-ish text on Benzol fails; move Benzol L down, keep C,h")
    adj = adjust_L(benzol, neu_l[50], 4.5, -1)
    print(f"    Benzol {benzol} {fmt_oklch(benzol)} -> {adj} {fmt_oklch(adj)}: WCAG {wcag_ratio(neu_l[50], adj):.2f}"
          f" APCA {apca_lc(neu_l[50], adj):+.1f}")

    print("\n  DARK appearance (composed): ground deepens, Lyons becomes the band")
    measure("text (neutral-50) on bg (Lyons dark 900)", neu_d[50], ly_d[900], 4.5)
    measure("text (neutral-50) on bg (Lyons dark 950)", neu_d[50], ly_d[950], 4.5)
    measure("Lyons pinned (dark 700) band vs bg (dark 900) adjacency", lyons, ly_d[900], 1.0)
    measure("text (neutral-50) on Lyons band", neu_d[50], lyons, 4.5)
    measure("headline Apricot dark-400 on bg (dark 900)", ap_d[400], ly_d[900], 3.0)
    measure("headline Apricot pinned on bg (dark 900)", apricot, ly_d[900], 3.0)
    polarity("dark CTA fill Apricot dark-400", ap_d[400], neu_d[50], neu_d[950])
    polarity("dark CTA fill Apricot pinned", apricot, neu_d[50], neu_d[950])
    measure("Benzol dark-500 band vs bg adjacency", bz_d[500], ly_d[900], 1.0)
    polarity("Benzol dark-500 band text", bz_d[500], neu_d[50], neu_d[950])
    measure("Raw Sienna dark-300 large text on bg", si_d[300], ly_d[900], 3.0)
    measure("muted text (Lyons dark 300) on bg", ly_d[300], ly_d[900], 4.5)


# =============================================================== Example (c)

def example_c() -> None:
    print("\n" + "=" * 100)
    print("EXAMPLE (c): reading app, Read, Restrained + painting ground/accent, The Milkmaid")
    g1, g2, g3 = "#D7D1BF", "#C6BDA9", "#0F1317"
    a1, a2, a3 = "#C89D7A", "#254D83", "#3C1914"
    for n, h in (("ground 1 (19%)", g1), ("ground 2 (8%)", g2), ("ground 3 (8%)", g3),
                 ("accent tan (<1%)", a1), ("accent blue (<1%)", a2), ("accent umber (2%)", a3)):
        describe(n, h)
    neu_l, neu_d = build_neutral(g1, "light"), build_neutral(g1, "dark")
    g1_l = build_ramp(g1, "light")
    g2_l = build_ramp(g2, "light")
    blue_l, blue_d = build_ramp(a2, "light"), build_ramp(a2, "dark")
    umber_l, umber_d = build_ramp(a3, "light"), build_ramp(a3, "dark")
    tan_l, tan_d = build_ramp(a1, "light"), build_ramp(a1, "dark")
    ramp_line("neutral light (tinted from ground-1 hue)", neu_l)
    ramp_line("neutral dark (tinted from ground-1 hue)", neu_d)
    ramp_line("frame ramp light (ground-1 pinned)", g1_l, nearest_step(hex_to_oklch(g1)[0], LIGHT_L))
    ramp_line("accent light (Vermeer blue)", blue_l, nearest_step(hex_to_oklch(a2)[0], LIGHT_L))
    ramp_line("accent dark (Vermeer blue)", blue_d, nearest_step(hex_to_oklch(a2)[0], DARK_L))
    ramp_line("voice-1 light (umber)", umber_l, nearest_step(hex_to_oklch(a3)[0], LIGHT_L))
    ramp_line("voice-1 dark (umber)", umber_d, nearest_step(hex_to_oklch(a3)[0], DARK_L))
    ramp_line("voice-2 light (tan)", tan_l, nearest_step(hex_to_oklch(a1)[0], LIGHT_L))
    ramp_line("voice-2 dark (tan)", tan_d, nearest_step(hex_to_oklch(a1)[0], DARK_L))

    print("\n  LIGHT MODE pairs")
    measure("body text (ground-3 #0F1317 pinned) on column (neutral-50)", g3, neu_l[50], 4.5)
    measure("body text on frame (ground-1 pinned)", g3, g1, 4.5)
    measure("body text on surface (ground-2 pinned)", g3, g2, 4.5)
    measure("muted text (neutral-700) on column", neu_l[700], neu_l[50], 4.5)
    measure("muted text (neutral-700) on frame (ground-1)", neu_l[700], g1, 4.5)
    measure("border (ground-2 pinned) non-text on column", g2, neu_l[50], 3.0)
    measure("border (neutral-300) non-text on column", neu_l[300], neu_l[50], 3.0)
    measure("border-strong (neutral-500) non-text on column", neu_l[500], neu_l[50], 3.0)
    measure("border-strong (neutral-500) non-text on frame (ground-1)", neu_l[500], g1, 3.0)
    measure("border-strong (neutral-600) non-text on frame (ground-1)", neu_l[600], g1, 3.0)
    measure("frame (ground-1) vs column adjacency", g1, neu_l[50], 1.0)
    measure("sunken field (ground-2) vs column adjacency", g2, neu_l[50], 1.0)
    measure("surface (ground-2) vs frame (ground-1) adjacency", g2, g1, 1.0)
    measure("link (accent-700 generated) on column", blue_l[700], neu_l[50], 4.5)
    measure("link (accent-800 = pinned Vermeer blue) on column", a2, neu_l[50], 4.5)
    measure("link (pinned Vermeer blue) on frame (ground-1)", a2, g1, 4.5)
    measure("link (pinned Vermeer blue) on surface (ground-2)", a2, g2, 4.5)
    measure("heading (umber pinned) on column", a3, neu_l[50], 4.5)
    measure("heading (umber pinned) on frame", a3, g1, 4.5)
    measure("accent solid (accent-600) non-text on column", blue_l[600], neu_l[50], 3.0)
    polarity("accent-600 fill text polarity", blue_l[600], neu_l[50], g3)
    polarity("accent pinned (800) fill text polarity", a2, neu_l[50], g3)
    measure("focus (accent-500) non-text on column", blue_l[500], neu_l[50], 3.0)
    measure("tan (voice-2 pinned) non-text on column", a1, neu_l[50], 3.0)
    measure("text on highlight (ground-3 on tan voice-2-100)", g3, tan_l[100], 4.5)
    measure("text on highlight (ground-3 on tan voice-2-200)", g3, tan_l[200], 4.5)
    measure("tan-200 highlight vs column adjacency", tan_l[200], neu_l[50], 1.0)
    measure("tan-700 as text on column", tan_l[700], neu_l[50], 4.5)
    measure("link vs heading hue/L separation (accent pinned vs umber)", a2, a3, 1.0)

    print("\n  DARK MODE pairs")
    measure("text (neutral-50) on bg (neutral-950)", neu_d[50], neu_d[950], 4.5)
    measure("text (neutral-50) on surface (neutral-900)", neu_d[50], neu_d[900], 4.5)
    measure("muted (neutral-300) on bg", neu_d[300], neu_d[950], 4.5)
    measure("border (neutral-700) non-text on bg", neu_d[700], neu_d[950], 3.0)
    measure("frame dark: neutral-900 vs bg adjacency", neu_d[900], neu_d[950], 1.0)
    measure("frame dark: neutral-800 vs bg adjacency", neu_d[800], neu_d[950], 1.0)
    measure("text (neutral-50) on frame (neutral-800)", neu_d[50], neu_d[800], 4.5)
    measure("muted (neutral-300) on frame (neutral-800)", neu_d[300], neu_d[800], 4.5)
    measure("link (accent-300 dark) on bg", blue_d[300], neu_d[950], 4.5)
    adjust_apca("dark link accent-300 -> Lc 75", blue_d[300], neu_d[950], 75, +1)
    adjust_apca("dark muted neutral-300 -> Lc 60", neu_d[300], neu_d[950], 60, +1)
    measure("link (accent-300 dark) on surface (neutral-900)", blue_d[300], neu_d[900], 4.5)
    measure("heading (umber dark-300) on bg", umber_d[300], neu_d[950], 4.5)
    measure("heading (umber dark-200) on bg", umber_d[200], neu_d[950], 4.5)
    measure("accent solid (accent-500 dark) non-text on bg", blue_d[500], neu_d[950], 3.0)
    polarity("dark accent-500 fill polarity", blue_d[500], neu_d[50], neu_d[950])
    polarity("dark accent-400 fill polarity", blue_d[400], neu_d[50], neu_d[950])
    measure("highlight text: neutral-50 on tan dark-800", neu_d[50], tan_d[800], 4.5)
    measure("highlight text: neutral-50 on tan dark-700", neu_d[50], tan_d[700], 4.5)
    measure("tan dark-800 vs bg adjacency", tan_d[800], neu_d[950], 1.0)
    print("  Interval check (Albers 7)")
    print(f"    light text/column dL {abs(hex_to_oklch(g3)[0]-hex_to_oklch(neu_l[50])[0]):.3f}; "
          f"dark {abs(hex_to_oklch(neu_d[50])[0]-hex_to_oklch(neu_d[950])[0]):.3f}")
    print(f"    light frame/column dL {abs(hex_to_oklch(g1)[0]-hex_to_oklch(neu_l[50])[0]):.3f}; "
          f"dark frame/bg {abs(hex_to_oklch(neu_d[900])[0]-hex_to_oklch(neu_d[950])[0]):.3f}")


if __name__ == "__main__":
    example_a()
    example_b()
    example_c()
