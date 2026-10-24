#!/usr/bin/env python3
"""build_tokens.py - turn one palette into OKLCH ramps and two-tier design tokens.

Input : a palette id from data/palettes.csv (--palette wada-229) or an explicit hex list
        (--hex "#f3a257,#253122,Paper=#f3ebda"), plus a colour strategy and mode.
Output: JSON (stdout or --out) that validate.py, preview.py and handoff.py consume:
        palette provenance, role assignment, ramps (light + separately composed dark),
        semantic roles for light and dark, voice and status colours, proportion targets.

All numbers come from notes/2-shared-constants.md (sources branch) (ramp L tables, chroma profile, role map,
proportion targets) and are held as module constants below.

Choices a user of this script should know:
  * --pin all (default): every palette colour is kept exactly (its hex is the ramp step with the nearest L, also exported
    as --<ramp>-seed). Voice and brand solids are non-text fills and ARE the exact plate colour; their -text and -subtle
    variants are generated steps chosen by measurement. The accent uses the pinned step only within one step of its role
    default and when the gate passes. A Drenched surface is the exact palette colour.
  * Status colours: palette member in the application-rules hue window (and 15+ degrees from the accent) else a default seed;
    solids sit at fixed steps (light warning 400, success 700, danger 600, info 500; dark warning 300, success 600,
    danger 400, info 500) so they also differ in lightness. validate.py may still lift a step to pass the 3:1 gate.
  * Drenched: page = the palette colour; text polarity is chosen by measurement (mid-lightness colours get the darkest or
    lightest neutral), tints and text on fills follow the page polarity. This construction is the skill's own.
  * Neutral ramp tint: the ground/palest tinted palette colour unless --neutral-from says otherwise.

Examples:
  python3 scripts/build_tokens.py --palette wada-229 --strategy restrained --out tokens.json
  python3 scripts/build_tokens.py --hex "#9a2a2a,#1b2a4e,#f4eee0" --strategy committed --mode persuade
  python3 scripts/build_tokens.py --palette paint-the-great-wave-off-kanagawa --accent "accent 5"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colorlib as cl  # noqa: E402

SCHEMA = "acp-tokens/1"

# --------------------------------------------------------------------------- shared constants (2-shared-constants.md)

STEPS = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]
LIGHT_L = dict(zip(STEPS, [0.975, 0.935, 0.885, 0.810, 0.720, 0.630, 0.540, 0.460, 0.380, 0.300, 0.240]))
DARK_L = dict(zip(STEPS, [0.960, 0.900, 0.810, 0.710, 0.610, 0.510, 0.420, 0.340, 0.270, 0.210, 0.160]))
PROFILE = dict(zip(STEPS, [0.15, 0.25, 0.40, 0.60, 0.80, 0.95, 1.00, 0.92, 0.80, 0.65, 0.50]))
DARK_CHROMA_FACTOR = 0.85
DARK_SURFACE_STEPS = ("800", "900", "950")
DARK_SURFACE_CHROMA_CAP = 0.045
NEUTRAL_N = dict(zip(STEPS, [0.006, 0.010, 0.014, 0.018, 0.020, 0.020, 0.020, 0.018, 0.016, 0.014, 0.012]))
NEUTRAL_CAP = 0.03
MIN_STEP_DL = 0.03
PIN_MAX_DL = 0.06
PIN_ROLE_WINDOW = 1  # a role takes the pinned seed step only within this many steps of its default step (amendment v2, item 5)
PIN_GAP = 0.036  # gap used when a pinned seed pushes neighbours (8-bit rounding keeps the measured gap >= 0.03)

WCAG_BODY, WCAG_LARGE, WCAG_NONTEXT = 4.5, 3.0, 3.0


def large_text_min(text_min: float) -> float:
    """Large-text gate: stays 3.0 at the default body floor and rises in step (text_min / 1.5) when the body floor is raised."""
    return round(max(WCAG_LARGE, text_min / 1.5), 2)
MID_L_RANGE = (0.50, 0.70)

STRATEGIES = {  # Impeccable's names verbatim; targets are percentages (min, max)
    "Restrained": {"neutrals": (85, 95), "palette": (0, 5), "accent": (2, 8),
                   "palette_label": "voice colours"},
    "Committed": {"neutrals": (35, 65), "palette": (30, 60), "accent": (0, 8),
                  "palette_label": "one palette colour (the brand colour)"},
    "Full palette": {"neutrals": (45, 65), "palette": (20, 45), "accent": (0, 8),
                     "palette_label": "secondary 15-30% and tertiary 5-15%",
                     "secondary": (15, 30), "tertiary": (5, 15)},
    "Drenched": {"neutrals": (5, 30), "palette": (60, 90), "accent": (0, 8),
                 "palette_label": "palette surface"},
}
STRATEGY_ALIASES = {"restrained": "Restrained", "committed": "Committed", "full": "Full palette",
                    "full-palette": "Full palette", "fullpalette": "Full palette", "full palette": "Full palette",
                    "drenched": "Drenched"}
MODES = {"persuade": "Persuade", "operate": "Operate", "read": "Read", "experience": "Experience"}
BOLD_STRATEGIES = {"Committed", "Full palette", "Drenched"}
PROPORTION_LABEL = ("Proportion targets are this skill's own convention (Impeccable's strategy names, "
                    "numbers from the skill's shared constants); Wada's plates show equal-area swatches for convenience only.")

# Status colours, exactly as printed in references/application-rules.md section 2 (amendment v2, item 6)
STATUS_WINDOWS = {  # OKLCH hue windows (degrees) a palette member must fall in
    "success": (135.0, 165.0),
    "warning": (65.0, 95.0),
    "danger": (15.0, 40.0),
    "info": (230.0, 270.0),
}
STATUS_DEFAULTS = {  # default seeds: (L, C, h)
    "danger": (0.55, 0.19, 27.0),
    "warning": (0.72, 0.15, 72.0),
    "success": (0.55, 0.14, 150.0),
    "info": (0.55, 0.13, 250.0),
}
# Status fill steps (orchestrator gate decision): different lightness per status so they differ by more than hue.
STATUS_STEPS = {
    "light": {"warning": "400", "success": "700", "danger": "600", "info": "500"},
    "dark": {"warning": "300", "success": "600", "danger": "400", "info": "500"},
}
STATUS_ACCENT_MIN_HUE_DIFF = 15.0  # a status within 15 degrees of the accent is re-seeded
STATUS_MIN_CHROMA = 0.09  # skill's own floor so a washed-out palette member never becomes a status colour
WHITE = "#ffffff"

# semantic tokens: (token, light ref, dark ref); refs are "ramp:step", "measure" (white or neutral-950)
STANDARD_ROLES = [
    ("bg", "neutral:50", "neutral:950"),
    ("bg-subtle", "neutral:100", "neutral:900"),
    ("surface", "neutral:50", "neutral:900"),
    ("surface-hover", "neutral:200", "neutral:800"),
    ("border-subtle", "neutral:200", "neutral:800"),
    ("border", "neutral:300", "neutral:700"),
    ("border-strong", "neutral:500", "neutral:500"),
    ("text", "neutral:900", "neutral:50"),
    ("text-muted", "neutral:700", "neutral:200"),
    ("accent", "accent:600", "accent:500"),
    ("accent-hover", "accent:700", "accent:400"),
    ("on-accent", "measure", "measure"),
    ("accent-text", "accent:700", "accent:200"),
    ("accent-subtle", "accent:100", "accent:900"),
    ("focus", "accent:500", "accent:400"),
]
FILL_TRIPLE = [("", "{r}:600", "{r}:500"), ("-subtle", "{r}:100", "{r}:900"), ("-text", "{r}:700", "{r}:300")]

# --------------------------------------------------------------------------- small helpers


def slugify(text: str) -> str:
    import unicodedata

    t = unicodedata.normalize("NFKD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t or "colour"


def hue_in_window(h: float, win: tuple[float, float]) -> bool:
    lo, hi = win
    return lo <= h <= hi if lo <= hi else (h >= lo or h <= hi)


def window_centre(win: tuple[float, float]) -> float:
    lo, hi = win
    if lo <= hi:
        return (lo + hi) / 2
    return ((lo + hi + 360) / 2) % 360


def r3(x: float) -> float:
    return round(float(x), 4)


def oklch_list(hx: str) -> list[float]:
    L, C, h = cl.hex_to_oklch(hx)
    return [r3(L), r3(C), round(h, 2)]


# --------------------------------------------------------------------------- members


class Member:
    def __init__(self, key: str, name: str, hex_: str, roles: list[str], coverage: str = ""):
        self.key, self.name, self.hex = key, name, cl.normalize_hex(hex_)
        self.roles, self.coverage = roles, coverage
        self.L, self.C, self.h = cl.hex_to_oklch(self.hex)
        self.cov = 0.5 if coverage.startswith("<") else (float(coverage) if coverage else 0.0)

    def to_json(self) -> dict:
        d = {"key": self.key, "name": self.name, "hex": self.hex, "oklch": oklch_list(self.hex), "roles": self.roles}
        if self.coverage:
            d["coverage_pct"] = self.coverage
        return d


def members_from_row(row: dict) -> list[Member]:
    out: list[Member] = []
    by_hex: dict[str, Member] = {}
    keys: set[str] = set()
    for i, m in enumerate(cl.row_members(row)):
        hx = cl.normalize_hex(m["hex"])
        if hx in by_hex:
            if m["role"]:
                by_hex[hx].roles.append(m["role"])
            continue
        name = m["name"] or f"colour {i + 1}"
        key = slugify(name)
        n = 2
        while key in keys:
            key = f"{slugify(name)}-{n}"
            n += 1
        keys.add(key)
        mem = Member(key, name, hx, [m["role"]] if m["role"] else [], m["coverage"])
        by_hex[hx] = mem
        out.append(mem)
    return out


def members_from_hex(spec: str) -> list[Member]:
    out, keys = [], set()
    for i, part in enumerate(p.strip() for p in spec.split(",") if p.strip()):
        if "=" in part:
            name, hx = part.split("=", 1)
            name = name.strip()
        else:
            name, hx = f"Colour {i + 1}", part
        if not cl.is_hex(hx.strip()):
            raise SystemExit(f"error: not a hex colour: {hx!r}")
        key = slugify(name)
        n = 2
        while key in keys:
            key = f"{slugify(name)}-{n}"
            n += 1
        keys.add(key)
        if any(m.hex == cl.normalize_hex(hx) for m in out):
            continue
        out.append(Member(key, name, hx.strip(), []))
    if len(out) < 1:
        raise SystemExit("error: --hex needs at least one colour")
    return out


def find_member(members: list[Member], ref: str) -> Member:
    """Resolve a user reference: 1-based index, hex, key, or (partial, case-insensitive) name."""
    r = ref.strip()
    if r.isdigit() and 1 <= int(r) <= len(members):
        return members[int(r) - 1]
    if cl.is_hex(r):
        hx = cl.normalize_hex(r)
        for m in members:
            if m.hex == hx:
                return m
        raise SystemExit(f"error: {r} is not one of the palette's colours ({', '.join(m.hex for m in members)})")
    low = r.lower()
    for m in members:
        if m.key == slugify(r) or m.name.lower() == low:
            return m
    hits = [m for m in members if low in m.name.lower() or low in m.key]
    if len(hits) == 1:
        return hits[0]
    names = ", ".join(f"{i + 1}={m.name}" for i, m in enumerate(members))
    raise SystemExit(f"error: cannot resolve colour {ref!r} ({'ambiguous' if hits else 'no match'}); choose one of: {names}")


# --------------------------------------------------------------------------- role assignment


def accent_score(m: Member) -> float:
    s = m.C
    if m.L > 0.92 or m.L < 0.18:
        s *= 0.3
    return s


def pick_accent(members: list[Member], exclude: set[str]) -> Member:
    pool = [m for m in members if m.key not in exclude] or list(members)
    prefer = [m for m in pool if set(m.roles) & {"accent", "hitoe"}]
    for group in (prefer, pool):
        good = [m for m in group if m.C >= 0.06 and 0.18 <= m.L <= 0.92]
        if good:
            return max(good, key=accent_score)
    return max(pool, key=lambda m: m.C)


def pick_ground(members: list[Member]) -> Member | None:
    grounds = [m for m in members if "ground" in m.roles]
    if grounds:
        return max(grounds, key=lambda m: m.cov)
    pale = [m for m in members if m.L >= 0.85 and m.C <= 0.08]
    return max(pale, key=lambda m: m.L) if pale else None


def ground_usable(m: Member | None) -> bool:
    return bool(m) and m.L >= 0.85 and m.C <= 0.08


def pick_brand(members: list[Member], exclude: set[str]) -> Member:
    pool = [m for m in members if m.key not in exclude and m.C >= 0.05 and 0.2 <= m.L <= 0.9]
    if not pool:
        pool = [m for m in members if m.key not in exclude] or list(members)
    grounds = [m for m in pool if "ground" in m.roles]
    if grounds:
        return max(grounds, key=lambda m: m.cov)
    return max(pool, key=lambda m: m.C)


def pick_neutral_from(members: list[Member], ground: Member | None) -> Member:
    if ground is not None and ground.C >= 0.008:
        return ground
    tinted = [m for m in members if m.C >= 0.012]
    if tinted:
        return max(tinted, key=lambda m: m.L)
    return max(members, key=lambda m: m.C)


def kasane_edge_accent(members: list[Member], asg: dict):
    """Kasane only. When the hitoe colour is the same hex as one of the layer colours it is merged into one member, so no other
    colour may be called hitoe. If the page (drench, brand or ground) uses that shared colour, the edge accent is the layer that
    separates from it best: largest dL with a passing 3:1 non-text contrast, labelled by its own layer name.
    Returns (member, note) or None."""
    shared = next((m for m in members if "hitoe" in m.roles and any(r.startswith("layer") for r in m.roles)), None)
    if shared is None:
        return None
    users = {m.key for m in (asg.get("drench"), asg.get("brand"), asg.get("ground")) if m}
    if shared.key not in users:
        return None
    cands = [m for m in members if m.key != shared.key and any(r.startswith("layer") for r in m.roles)
             and cl.wcag_contrast(m.hex, shared.hex) >= WCAG_NONTEXT]
    if not cands:
        return None
    best = max(cands, key=lambda m: (abs(m.L - shared.L), m.C))
    n_shared = next(r for r in shared.roles if r.startswith("layer")).replace("layer", "")
    n_best = next(r for r in best.roles if r.startswith("layer")).replace("layer", "")
    return best, f"hitoe equals layer {n_shared}; accent taken from layer {n_best}"


def assign_roles(members: list[Member], strategy: str, overrides: dict[str, str]) -> dict:
    notes: list[str] = []
    ov = {k: find_member(members, v) for k, v in overrides.items() if v}
    ground = ov.get("ground") or pick_ground(members)
    brand = drench = None
    if strategy == "Committed":
        brand = ov.get("brand") or pick_brand(members, {ground.key} if ground and ground_usable(ground) else set())
    if strategy == "Drenched":
        drench = ov.get("drench") or ov.get("brand") or pick_brand(members, set())
    used = {m.key for m in (brand, drench) if m}
    accent = ov.get("accent") or pick_accent(members, used)
    if accent.key in used and len([m for m in members if m.C >= 0.04]) < 2:
        notes.append(f"{accent.name} is the only chromatic colour, so the accent shares the "
                     f"{'brand' if brand else 'drench'} hue and is told apart by lightness.")
    neutral = ov.get("neutral") or pick_neutral_from(members, ground)
    taken = {accent.key} | used
    voices: list[Member] = []
    ranked = sorted([m for m in members if m.key not in taken and m.C >= 0.02], key=lambda m: (-m.C, members.index(m)))
    if strategy == "Full palette":
        ranked = [m for m in ranked if not (ground_usable(ground) and m.key == ground.key)]
        voices = ranked[:6]
    elif strategy == "Committed":
        voices = [m for m in ranked if not (ground_usable(ground) and m.key == ground.key)][:6]
    else:
        voices = [m for m in ranked if not (ground and m.key == ground.key and m.C < 0.04)][:6]
    unused = [m.name for m in members if m.key not in {x.key for x in voices} | taken | {neutral.key}]
    return {"accent": accent, "neutral": neutral, "ground": ground, "brand": brand, "drench": drench,
            "voices": voices, "unused": unused, "notes": notes}


# --------------------------------------------------------------------------- ramps


def _place_pin(table: dict[str, float], seed_L: float):
    nearest = min(STEPS, key=lambda s: abs(table[s] - seed_L))
    if abs(table[nearest] - seed_L) > PIN_MAX_DL:
        return None
    Ls = dict(table)
    Ls[nearest] = seed_L
    idx = STEPS.index(nearest)
    for j in range(idx - 1, -1, -1):
        Ls[STEPS[j]] = max(Ls[STEPS[j]], Ls[STEPS[j + 1]] + PIN_GAP)
    for j in range(idx + 1, len(STEPS)):
        Ls[STEPS[j]] = min(Ls[STEPS[j]], Ls[STEPS[j - 1]] - PIN_GAP)
    if Ls[STEPS[0]] > 0.995 or Ls[STEPS[-1]] < 0.05:
        return None
    return nearest, Ls


def build_chromatic_ramp(seed_hex: str, pin: bool) -> dict:
    L0, C0, h = cl.hex_to_oklch(seed_hex)
    cmax0 = cl.max_chroma(L0, h)
    share = min(1.0, C0 / cmax0) if cmax0 > 1e-6 else 0.0
    ramp = {"seed": cl.normalize_hex(seed_hex), "seed_oklch": oklch_list(seed_hex), "share": r3(share), "hue": round(h, 2),
            "pinned": {"light": None, "dark": None}, "light": {}, "dark": {}}
    for mode, table in (("light", LIGHT_L), ("dark", DARK_L)):
        Ls, pinned_step = dict(table), None
        if pin:
            placed = _place_pin(table, L0)
            if placed:
                pinned_step, Ls = placed
        for s in STEPS:
            if s == pinned_step:
                ramp[mode][s] = ramp["seed"]
                continue
            L = Ls[s]
            c = share * PROFILE[s] * cl.max_chroma(L, h)
            if mode == "dark":
                c *= DARK_CHROMA_FACTOR
                if s in DARK_SURFACE_STEPS:
                    c = min(c, DARK_SURFACE_CHROMA_CAP)
            ramp[mode][s] = cl.oklch_to_hex(L, c, h)
        ramp["pinned"][mode] = pinned_step
    return ramp


def build_neutral_ramp(tint_hex: str, tint: float) -> dict:
    _, _, h = cl.hex_to_oklch(tint_hex)
    ramp = {"seed": cl.normalize_hex(tint_hex), "seed_oklch": oklch_list(tint_hex), "tint": tint, "hue": round(h, 2),
            "pinned": {"light": None, "dark": None}, "light": {}, "dark": {}}
    for mode, table in (("light", LIGHT_L), ("dark", DARK_L)):
        for s in STEPS:
            c = min(NEUTRAL_CAP, tint * NEUTRAL_N[s])
            ramp[mode][s] = cl.oklch_to_hex(table[s], c, h)
    return ramp


# --------------------------------------------------------------------------- semantic roles


class Roles:
    """Resolves refs to hex for one mode and records meta."""

    def __init__(self, ramps: dict, mode: str, text_min: float = WCAG_BODY, on_accent: str = "auto"):
        self.ramps, self.mode = ramps, mode
        self.text_min, self.on_accent = text_min, on_accent
        self.out: dict[str, dict] = {}

    def hex_of(self, ref: str) -> str:
        if ref.startswith("literal:"):
            return ref.split(":", 1)[1]
        if ref == "ground:seed":
            return self.ramps["ground"]["seed"]
        name, step = ref.split(":")
        return self.ramps[name][self.mode][step]

    def set(self, token: str, ref: str, **meta) -> str:
        hx = self.hex_of(ref)
        L = cl.hex_to_oklch(hx)[0]
        self.out[token] = {"ref": ref, "hex": hx, "L": r3(L), **meta}
        return hx

    def measure_on(self, token: str, fill_hex: str, force: str = "auto") -> str:
        """Choose white or neutral-950 text on a fill by WCAG ratio; record both ratios.
        force='light' / 'dark' pins the polarity (a brand rule such as 'white button text')."""
        dark_ref = "neutral:950"
        dark_hex = self.hex_of(dark_ref)
        rw, rd = cl.wcag_contrast(WHITE, fill_hex), cl.wcag_contrast(dark_hex, fill_hex)
        light = (rw >= rd) if force == "auto" else (force == "light")
        ref, hx = (f"literal:{WHITE}", WHITE) if light else (dark_ref, dark_hex)
        L = cl.hex_to_oklch(fill_hex)[0]
        meta = {"measured": {"white": round(rw, 2), "neutral-950": round(rd, 2)}}
        if force != "auto":
            meta["forced_polarity"] = force
        if MID_L_RANGE[0] <= L <= MID_L_RANGE[1]:
            meta["mid_lightness_fill"] = r3(L)
        self.set(token, ref, **meta)
        return hx


def _shift(step: str, by: int) -> str:
    i = max(0, min(len(STEPS) - 1, STEPS.index(step) + by))
    return STEPS[i]


def label_ratio(r: Roles, fill_hex: str) -> float:
    """Best (or, when on-accent is forced, the forced) label ratio on a fill."""
    rw, rd = cl.wcag_contrast(WHITE, fill_hex), cl.wcag_contrast(r.hex_of("neutral:950"), fill_hex)
    if r.on_accent == "light":
        return rw
    if r.on_accent == "dark":
        return rd
    return max(rw, rd)


def fill_ok(r: Roles, fill_hex: str) -> bool:
    bgs = [r.out["bg"]["hex"]]
    if "surface" in r.out:
        bgs.append(r.out["surface"]["hex"])
    if any(cl.wcag_contrast(fill_hex, b) < WCAG_NONTEXT for b in bgs):
        return False
    return label_ratio(r, fill_hex) >= r.text_min


def _first_ok(r: Roles, refs: list[str], bg_hex: str, floor: float | None = None) -> str:
    """First ref whose text colour reaches the floor on bg; else the ref with the best ratio."""
    floor = r.text_min if floor is None else floor
    best = max(refs, key=lambda x: cl.wcag_contrast(r.hex_of(x), bg_hex))
    for ref in refs:
        if cl.wcag_contrast(r.hex_of(ref), bg_hex) >= floor:
            return ref
    return best


def _drench_light(r: Roles, dr: dict) -> bool:
    """Light-mode surfaces for the Drenched strategy: the page is the palette colour itself.
    Returns True when the text on it is light (the 'dark style' step choices then apply to tints)."""
    seed_L = cl.hex_to_oklch(dr["seed"])[0]
    step = dr["pinned"]["light"] or min(STEPS, key=lambda s: abs(LIGHT_L[s] - seed_L))
    bg_hex = dr["light"][step]
    rd = max(cl.wcag_contrast(r.hex_of("neutral:900"), bg_hex), cl.wcag_contrast(r.hex_of("neutral:950"), bg_hex))
    rl = cl.wcag_contrast(r.hex_of("neutral:50"), bg_hex)
    dark_text = rd >= rl
    if dark_text:
        text = _first_ok(r, ["neutral:900", "neutral:950"], bg_hex)
        muted = _first_ok(r, ["neutral:700", "neutral:800", "neutral:900", "neutral:950"], bg_hex)
    else:
        text = "neutral:50"
        muted = _first_ok(r, ["neutral:200", "neutral:100", "neutral:50"], bg_hex)
    idx = STEPS.index(step)
    # move the other surfaces away from the text colour when there is room, else toward it
    if dark_text:
        sgn = -1 if idx >= 3 else 1
    else:
        sgn = 1 if idx <= 8 else -1
    r.set("bg", f"drench:{step}", drench_surface=True)
    r.set("surface", f"drench:{step}")
    text_hex = r.hex_of(text)
    for token, off in (("bg-subtle", 1), ("surface-hover", 2)):
        n = off
        while n > 0 and cl.wcag_contrast(text_hex, dr["light"][_shift(step, sgn * n)]) < r.text_min:
            n -= 1
        r.set(token, f"drench:{_shift(step, sgn * n)}")
    r.set("border-subtle", r.out["surface-hover"]["ref"])
    r.set("border", f"drench:{_shift(step, sgn * 3)}")
    r.set("border-strong", f"drench:{_shift(step, sgn * 5)}")
    r.set("text", text)
    r.set("text-muted", muted)
    return not dark_text


ACTION_STYLES = ("solid", "tinted", "outline")
ON_ACCENT_CHOICES = ("auto", "light", "dark")
HOVER_CHROMA_MAX = 0.04  # tinted / outline hover fills stay this close to neutral
HOVER_DL = 0.07

# tokens that mirror another role (kept in step by sync_action_aliases, also after validate --fix)
ACTION_ALIASES = {
    "solid": {"action": "accent", "action-hover": "accent-hover", "on-action": "on-accent", "action-border": "accent"},
    "tinted": {"action": "accent-subtle", "on-action": "text", "on-accent": "text", "action-border": "accent"},
    "outline": {"on-action": "accent-text", "on-accent": "accent-text", "action-border": "accent"},
}


def sync_action_aliases(roles: dict, style: str) -> None:
    """Make the action tokens that mirror another role carry that role's current value."""
    for tok, src in ACTION_ALIASES[style].items():
        s = roles[src]
        roles[tok] = {"ref": s["ref"], "hex": s["hex"], "L": s["L"], "alias_of": src}


def low_chroma_hover(ramps: dict, mode: str, dark_style: bool) -> str:
    """Hover fill for the tinted / outline action: one clear lightness step from the tint, chroma capped at 0.04."""
    acc = ramps["accent"]
    table = LIGHT_L if mode == "light" else DARK_L
    base = table["900" if dark_style else "100"]
    L = base + (HOVER_DL if dark_style else -HOVER_DL)
    c = min(HOVER_CHROMA_MAX - 0.002, acc["share"] * PROFILE["800" if dark_style else "200"] * cl.max_chroma(L, acc["hue"]))
    return cl.oklch_to_hex(L, c, acc["hue"])


def mark_step(r: Roles, name: str, current: str, surfaces: list[str]) -> str:
    """Nearest step of the ramp whose colour clears 3:1 against the page and surface (the current step if it does)."""
    ramp = r.ramps[name][r.mode]
    if all(cl.wcag_contrast(ramp[current], b) >= WCAG_NONTEXT for b in surfaces):
        return current
    page_dark = cl.hex_to_oklch(surfaces[0])[0] < 0.5
    i = STEPS.index(current)
    for d in range(1, len(STEPS)):
        order = (i - d, i + d) if page_dark else (i + d, i - d)
        for j in order:
            if 0 <= j < len(STEPS) and all(cl.wcag_contrast(ramp[STEPS[j]], b) >= WCAG_NONTEXT for b in surfaces):
                return STEPS[j]
    return current


def build_semantic(ramps: dict, mode: str, strategy: str, ground_ok: bool, assignment_keys: dict, notes: list[str],
                   policy: dict | None = None) -> dict:
    policy = {"text_min": WCAG_BODY, "on_accent": "auto", "action_style": "solid", **(policy or {})}
    r = Roles(ramps, mode, policy["text_min"], policy["on_accent"])
    force = policy["on_accent"]
    style = policy["action_style"]
    is_light = mode == "light"
    dark_style = not is_light  # step choices for tints/text on the palette fills follow the page polarity
    if "drench" in ramps:
        if is_light:
            dark_style = _drench_light(r, ramps["drench"])
        else:
            for token, ref in (("bg", "drench:900"), ("bg-subtle", "drench:800"), ("surface", "drench:800"),
                               ("surface-hover", "drench:700"), ("border-subtle", "drench:700"), ("border", "drench:600"),
                               ("border-strong", "drench:500"), ("text", "neutral:50"), ("text-muted", "neutral:200")):
                r.set(token, ref, **({"drench_surface": True} if token == "bg" else {}))
    else:
        for token, lref, dref in STANDARD_ROLES:
            if token in ("bg", "bg-subtle", "surface", "surface-hover", "border-subtle", "border", "border-strong", "text", "text-muted"):
                ref = lref if is_light else dref
                if token == "surface" and is_light and ground_ok and strategy == "Full palette":
                    ref = "ground:seed"
                r.set(token, ref)
    # ---- accent family. The pinned plate colour is the accent fill whenever it passes the fill gate (3:1 against the
    # page, label at text_min), wherever it sits on the ramp; accent-text and focus take it only within one step of
    # their default (amendment v2, item 5). A pinned value is never changed: a failing role moves to another step.
    acc = ramps["accent"]
    pinned = acc["pinned"][mode]
    default = {"accent": "500" if dark_style else "600", "accent-text": "200" if dark_style else "700",
               "focus": "400" if dark_style else "500"}
    surfaces = [r.out["bg"]["hex"], r.out["surface"]["hex"]]

    def gate_ok(role: str, hx: str) -> bool:
        if role == "accent":
            return fill_ok(r, hx)
        if role == "accent-text":
            return all(cl.wcag_contrast(hx, b) >= r.text_min for b in surfaces)
        return all(cl.wcag_contrast(hx, b) >= WCAG_NONTEXT for b in surfaces)  # focus

    chosen = dict(default)
    used, not_used = [], []
    if pinned:
        seed_hex = acc[mode][pinned]
        if gate_ok("accent", seed_hex):
            chosen["accent"] = pinned
            used.append("accent")
        else:
            not_used.append(f"accent (the seed fails the fill gate; the role stays on accent-{default['accent']})")
        for role in ("accent-text", "focus"):
            dstep = default[role]
            if abs(STEPS.index(pinned) - STEPS.index(dstep)) <= PIN_ROLE_WINDOW:
                if gate_ok(role, seed_hex):
                    chosen[role] = pinned
                    used.append(role)
                else:
                    not_used.append(f"{role} (the seed fails the gate; default accent-{dstep} kept)")
            else:
                not_used.append(f"{role} (default accent-{dstep} is more than one step from accent-{pinned})")
        if used:
            notes.append(f"{mode}: the pinned accent seed {acc['seed']} (accent-{pinned}) is used for: {', '.join(used)}.")
        if not_used:
            notes.append(f"{mode}: the pinned accent seed {acc['seed']} (accent-{pinned}) was not used for: {'; '.join(not_used)}.")
    if (force != "auto" or pinned == chosen["accent"]) and not gate_ok("accent", acc[mode][chosen["accent"]]):
        # the fill role moves to the nearest step that passes (a forced light label means darker, a forced dark label lighter);
        # the pinned colour itself is never touched
        toward_dark = (force == "light") or (force == "auto" and not dark_style)
        start = STEPS.index(chosen["accent"])
        for j in range(1, len(STEPS)):
            idx = start + j if toward_dark else start - j
            if 0 <= idx < len(STEPS) and gate_ok("accent", acc[mode][STEPS[idx]]):
                notes.append(f"{mode}: accent fill moved from accent-{chosen['accent']} to accent-{STEPS[idx]} "
                             f"({'forced ' + force + ' label' if force != 'auto' else 'fill gate'}).")
                chosen["accent"] = STEPS[idx]
                break
    fill_step = chosen["accent"]
    r.set("accent", f"accent:{fill_step}")
    r.measure_on("on-accent", r.out["accent"]["hex"], force)
    # hover: the adjacent step that increases contrast with the label (light label -> darker step)
    label_is_light = r.out["on-accent"]["ref"].startswith("literal:") or cl.hex_to_oklch(r.out["on-accent"]["hex"])[0] > 0.6
    r.set("accent-hover", f"accent:{_shift(fill_step, 1 if label_is_light else -1)}")
    r.set("accent-text", f"accent:{chosen['accent-text']}")
    r.set("accent-subtle", "accent:900" if dark_style else "accent:100")
    r.set("focus", f"accent:{chosen['focus']}")
    # surface-hover follows the same polarity rule relative to the text colour when there is room for a distinct step
    text_light = cl.hex_to_oklch(r.out["text"]["hex"])[0] > 0.6
    rest = r.out["surface"]["ref"]
    if rest.count(":") == 1 and not rest.startswith(("literal", "ground")):
        rname, rstep = rest.split(":")
        want = _shift(rstep, 1 if text_light else -1)
        cand_ref = f"{rname}:{want}"
        if want != rstep and cand_ref != r.out["bg"]["ref"] and r.hex_of(cand_ref) != r.out["bg"]["hex"]:
            r.set("surface-hover", cand_ref, polarity_rule=True)
        else:
            notes.append(f"{mode}: surface-hover kept at its table default (no distinct step in the contrast-increasing direction).")
    # ---- action style: solid (alias of the accent tokens), tinted (pale tint + accent border + text label) or outline
    if style != "solid":
        hover = low_chroma_hover(ramps, mode, dark_style)
        r.out["action-hover"] = {"ref": f"literal:{hover}", "hex": hover, "L": r3(cl.hex_to_oklch(hover)[0]),
                                 "low_chroma_hover": True}
        if style == "outline":
            bg = r.out["bg"]["hex"]
            r.out["action"] = {"ref": "transparent", "hex": bg, "L": r.out["bg"]["L"], "transparent": True}
    # ---- brand, voices, statuses.
    # Brand and voice colours are REGION fills (bands, sections, tags): the exact plate colour whenever the ramp is pinned,
    # not gated against the page; only text placed on them is gated (on-* chosen by measurement). `-mark` is the nearest
    # step that clears 3:1 against the page, for chart marks, icons and meaningful edges. Status colours are marks/icons,
    # so they keep the fixed steps (a lightness cue besides hue) and the 3:1 gate.
    for name in assignment_keys["fill_ramps"]:
        ramp = ramps[name]
        is_status = name in STATUS_STEPS["light"]
        default_step = STATUS_STEPS["dark" if dark_style else "light"][name] if is_status else ("500" if dark_style else "600")
        step = default_step
        pin_step = ramp.get("pinned", {}).get(mode)
        if pin_step:
            seed_hex = ramp[mode][pin_step]
            if not is_status:
                step = pin_step
            else:
                near = abs(STEPS.index(pin_step) - STEPS.index(default_step)) <= PIN_ROLE_WINDOW
                ok = all(cl.wcag_contrast(seed_hex, b) >= WCAG_NONTEXT for b in surfaces)
                if near and ok:
                    step = pin_step
                elif not ok:
                    notes.append(f"{mode}: {name} seed {seed_hex} (at {name}-{pin_step}) is below 3:1 against the page, so its solid uses {name}-{step}.")
                else:
                    notes.append(f"{mode}: {name} seed {seed_hex} (at {name}-{pin_step}) was not used for its solid (default {name}-{default_step}).")
        r.set(name, f"{name}:{step}")
        if not is_status:
            m = mark_step(r, name, step, surfaces)
            r.set(f"{name}-mark", f"{name}:{m}", same_as_region=(m == step))
        for suffix, l, d in FILL_TRIPLE[1:]:
            r.set(f"{name}{suffix}", (d if dark_style else l).format(r=name))
        r.measure_on(f"on-{name}", r.out[name]["hex"])
    sync_action_aliases(r.out, style)
    return r.out


# --------------------------------------------------------------------------- proportions


def build_proportions(strategy: str, accent_seed_C: float, accent_fill_C: float, source_type: str,
                      members: list[Member], roles: dict) -> dict:
    spec = STRATEGIES[strategy]
    accent_lo, accent_hi = spec["accent"]
    modifiers = []
    chroma = max(accent_seed_C, accent_fill_C)
    if chroma >= 0.15:
        accent_hi = min(accent_hi, 5)
        accent_lo = min(accent_lo, accent_hi)
        modifiers.append("accent chroma >= 0.15: accent capped at 5% (Albers 9)")
    if source_type == "kasane":
        accent_lo = min(5, accent_hi)
        modifiers.append("kasane: the edge layer (hitoe) takes 5-10% of the page; capped by the accent limit above")
    out = {
        "strategy": strategy,
        "neutrals_pct": list(spec["neutrals"]),
        "palette_pct": list(spec["palette"]),
        "palette_means": spec["palette_label"],
        "accent_pct": [accent_lo, accent_hi],
        "modifiers": modifiers,
        "label": PROPORTION_LABEL,
    }
    if "secondary" in spec:
        out["secondary_pct"] = list(spec["secondary"])
        out["tertiary_pct"] = list(spec["tertiary"])
    if source_type == "painting":
        grounds = [m for m in members if "ground" in m.roles]
        total = sum(m.cov for m in grounds) or 1.0
        mid = (spec["neutrals"][0] + spec["neutrals"][1]) / 2 if strategy != "Drenched" else (spec["palette"][0] + spec["palette"][1]) / 2
        out["ground_shares_pct"] = {m.key: round(mid * m.cov / total, 1) for m in grounds}
        out["ground_shares_basis"] = "measured canvas coverage of the three ground colours, scaled to the strategy's ground band"
        out["accents_total_max_pct"] = 8
    return out


# --------------------------------------------------------------------------- credit / provenance


_DATA_SOURCE_LABEL = re.compile(r"^(wada plate|plate \d|editorial palette|sampled from|kasane no irome|kasane:)", re.I)
PROVENANCE_REFUSAL = "provenance labels for data sources come from data/palettes.csv; use --palette <id>"


def check_provenance_label(label: str | None) -> None:
    """A free-text provenance label (--hex input) must never claim a data source: plates, editorial palettes, paintings and
    kasane patterns get their label from data/palettes.csv only."""
    if not label:
        return
    text = label.strip()
    if _DATA_SOURCE_LABEL.match(text) or "colorcombinations.org" in text.lower():
        raise SystemExit(f"error: {PROVENANCE_REFUSAL}")


KASANE_COURTESY = "Base colours after Wikipedia, 'Traditional colors of Japan' (CC BY-SA 4.0); pattern after Heian kasane no irome."
DEFAULT_CUSTOM_LABEL = "Original composition (colours supplied by the user)"


def provenance(row: dict | None, members: list[Member], label: str | None = None) -> dict:
    if row is None:
        text = (label or "").strip() or DEFAULT_CUSTOM_LABEL
        return {"id": "custom", "source_type": "custom", "title": "Custom palette", "title_ja": "",
                "label": text, "source_url": "", "licence": "user-supplied",
                "credit": text if label else "Original composition", "tone_family": "", "drift": False}
    st = row["source_type"]
    credit = {
        "wada_plate": f"Wada plate {row['id'].split('-')[1]} via colorcombinations.org (CC BY 4.0)",
        "editorial": f"Editorial palette {row['title']} by colorcombinations.org (CC BY 4.0)",
        "painting": f"{row['title']} palette sampled by colorcombinations.org (CC BY 4.0); artwork public domain",
        "kasane": KASANE_COURTESY,
    }[st]
    # a kasane palette carries a courtesy credit, not a "Licence: CC-BY-SA" line, in generated files (the data row keeps its licence)
    return {"id": row["id"], "source_type": st, "title": row["title"], "title_ja": row["title_ja"], "label": row["label"],
            "source_url": row["source_url"], "licence": KASANE_COURTESY if st == "kasane" else row["licence"], "credit": credit, "tone_family": row["tone_family"],
            "drift": row["drift"] == "true", "drift_note": cl.DRIFT_NOTE if row["drift"] == "true" else "",
            "hue": row["hue"], "season": row["season"]}


# --------------------------------------------------------------------------- main builder


def _green_dominant(hx: str) -> bool:
    r, g, b = cl.parse_hex(hx)
    return g > 1.1 * r and g > 1.1 * b


def pick_status(members: list[Member], excluded: set[str], accent_hue: float) -> dict:
    """Status colours per references/application-rules.md section 2: a palette member whose OKLCH hue falls in the
    status window and is at least 15 degrees from the accent; otherwise the default seed, re-seeded away from the accent
    when it sits within 15 degrees of it. Danger is never green-dominant."""
    out = {}
    taken: set[str] = set()
    for name, win in STATUS_WINDOWS.items():
        cands = [m for m in members if m.key not in excluded | taken and m.C >= STATUS_MIN_CHROMA
                 and hue_in_window(m.h, win) and 0.3 <= m.L <= 0.85
                 and cl.hue_diff(m.h, accent_hue) >= STATUS_ACCENT_MIN_HUE_DIFF]
        if name == "danger":
            cands = [m for m in cands if not _green_dominant(m.hex)]
        if cands:
            centre = (win[0] + win[1]) / 2
            m = min(cands, key=lambda c: cl.hue_diff(c.h, centre))
            taken.add(m.key)
            out[name] = {"source": "palette", "member": m.key, "seed": m.hex, "non_colour_cue_needed": False}
            continue
        L, C, h = STATUS_DEFAULTS[name]
        rec = {"source": "default", "member": None, "non_colour_cue_needed": False}
        if cl.hue_diff(h, accent_hue) < STATUS_ACCENT_MIN_HUE_DIFF:
            # re-seed: rotate away from the accent until 16 degrees apart, towards the side that stays closer to the window
            options = [(accent_hue + 16.0) % 360.0, (accent_hue - 16.0) % 360.0]
            centre = (win[0] + win[1]) / 2
            h = min(options, key=lambda x: cl.hue_diff(x, centre))
            rec.update(source="default-reseeded", non_colour_cue_needed=True,
                       reason=f"the default {name} hue is within {STATUS_ACCENT_MIN_HUE_DIFF:.0f} degrees of the accent; "
                              "re-seeded away from it, so give this status an icon and a text label as well")
        seed = cl.oklch_to_hex(L, C, h)
        if name == "danger" and _green_dominant(seed):
            seed = cl.oklch_to_hex(*STATUS_DEFAULTS["danger"])
        rec["seed"] = seed
        out[name] = rec
    return out


def parse_pin(value: str, assignment: dict, members: list[Member]) -> set[str]:
    v = (value or "").strip().lower()
    if v in ("", "none"):
        return set()
    chroma_names = {"accent"} | ({"brand"} if assignment["brand"] else set()) | ({"drench"} if assignment["drench"] else set())
    voice_names = {f"voice-{i + 1}" for i in range(len(assignment["voices"]))}
    if v == "all":
        return chroma_names | voice_names
    out = set()
    for part in v.split(","):
        part = part.strip()
        if part in chroma_names | voice_names:
            out.add(part)
        elif part:
            m = find_member(members, part)
            if assignment["accent"].key == m.key:
                out.add("accent")
            if assignment["brand"] and assignment["brand"].key == m.key:
                out.add("brand")
            if assignment["drench"] and assignment["drench"].key == m.key:
                out.add("drench")
            for i, vm in enumerate(assignment["voices"]):
                if vm.key == m.key:
                    out.add(f"voice-{i + 1}")
    return out


def build_tokens(palette: str | None = None, hexes: str | None = None, strategy: str = "Restrained", mode: str = "Operate",
                 roles: dict[str, str] | None = None, pin: str = "all", tint: float = 1.0,
                 name: str | None = None, data_dir: Path | None = None, provenance_label: str | None = None,
                 on_accent: str = "auto", action_style: str = "solid", text_min: float = WCAG_BODY) -> dict:
    if bool(palette) == bool(hexes):
        raise SystemExit("error: give exactly one of --palette or --hex")
    strategy = STRATEGY_ALIASES.get(strategy.strip().lower(), strategy)
    if strategy not in STRATEGIES:
        raise SystemExit(f"error: unknown strategy {strategy!r}; use restrained, committed, full-palette or drenched")
    mode_name = MODES.get(mode.strip().lower())
    if not mode_name:
        raise SystemExit(f"error: unknown mode {mode!r}; use persuade, operate, read or experience")
    row = None
    if palette:
        rows = cl.load_palette_rows((data_dir or cl.data_dir()) / "palettes.csv")
        by_id = {r["id"]: r for r in rows}
        if palette not in by_id:
            raise SystemExit(f"error: '{palette}' is not in the data (nothing was substituted); try search.py")
        row = by_id[palette]
        members = members_from_row(row)
    else:
        members = members_from_hex(hexes)
    if on_accent not in ON_ACCENT_CHOICES:
        raise SystemExit(f"error: --on-accent must be one of {', '.join(ON_ACCENT_CHOICES)}")
    if action_style not in ACTION_STYLES:
        raise SystemExit(f"error: --action-style must be one of {', '.join(ACTION_STYLES)}")
    if not 3.0 <= text_min <= 21.0:
        raise SystemExit("error: --text-min must be between 3 and 21")
    policy = {"text_min": float(text_min), "large_text_min": large_text_min(text_min), "on_accent": on_accent, "action_style": action_style}
    warnings: list[str] = []
    notes: list[str] = []
    if strategy in BOLD_STRATEGIES and mode_name in ("Operate", "Read"):
        warnings.append(f"{strategy} is a bolder strategy than usual for a {mode_name} surface; Impeccable keeps the bolder "
                        "strategies for Persuade and Experience surfaces. Confirm with the user.")
    asg = assign_roles(members, strategy, roles or {})
    kasane_note = None
    if row is not None and row["source_type"] == "kasane" and "accent" not in (roles or {}):
        pick = kasane_edge_accent(members, asg)
        if pick:
            member, note = pick
            asg = assign_roles(members, strategy, {**(roles or {}), "accent": member.key})
            kasane_note = note
            m_layer = next(r for r in member.roles if r.startswith("layer"))
            member.name = f"{member.name} ({m_layer.replace('layer', 'layer ')})"
    notes += asg["notes"]
    if kasane_note:
        notes.append(kasane_note)
    pins = parse_pin(pin, asg, members)

    ramps: dict[str, dict] = {}
    ramps["neutral"] = build_neutral_ramp(asg["neutral"].hex, tint)
    ramps["accent"] = build_chromatic_ramp(asg["accent"].hex, "accent" in pins)
    fill_ramps: list[str] = []
    if asg["brand"]:
        ramps["brand"] = build_chromatic_ramp(asg["brand"].hex, "brand" in pins)
        fill_ramps.append("brand")
    if asg["drench"]:
        ramps["drench"] = build_chromatic_ramp(asg["drench"].hex, True)  # the surface colour is always kept exactly
    for i, vm in enumerate(asg["voices"]):
        nm = f"voice-{i + 1}"
        ramps[nm] = build_chromatic_ramp(vm.hex, nm in pins)
        fill_ramps.append(nm)
    if asg["ground"]:
        ramps["ground"] = {"seed": asg["ground"].hex, "seed_oklch": oklch_list(asg["ground"].hex)}
    excluded = {asg["accent"].key} | ({asg["brand"].key} if asg["brand"] else set()) | ({asg["drench"].key} if asg["drench"] else set())
    status = pick_status(members, excluded, asg["accent"].h)
    for sname, rec in status.items():
        pin_it = rec["source"] == "palette" and (pin.strip().lower() == "all" or sname in pin.lower().split(","))
        ramps[sname] = build_chromatic_ramp(rec["seed"], pin_it)
        fill_ramps.append(sname)

    for sname, rec in status.items():
        if rec.get("non_colour_cue_needed"):
            notes.append(f"status {sname}: {rec['reason']}.")
    gok = ground_usable(asg["ground"])
    sem = {}
    for mode_key in ("light", "dark"):
        sem[mode_key] = build_semantic(ramps, mode_key, strategy, gok, {"fill_ramps": fill_ramps}, notes, policy)
    if strategy == "Full palette" and asg["ground"] and not gok:
        notes.append(f"Ground colour {asg['ground'].name} ({asg['ground'].hex}) is not a pale paper colour, so --color-surface stays on the neutral ramp.")

    accent_fill_C = cl.hex_to_oklch(sem["light"]["accent"]["hex"])[1]
    props = build_proportions(strategy, asg["accent"].C, accent_fill_C, row["source_type"] if row else "custom", members, asg)
    check_provenance_label(provenance_label)
    if provenance_label and row is not None:
        raise SystemExit("error: --provenance only applies to --hex input; palette ids keep their data-derived label")
    prov = provenance(row, members, provenance_label)
    title = name or (prov["title"] if row else "Custom palette")
    assignment = {
        "accent": asg["accent"].key, "neutral_from": asg["neutral"].key,
        "ground": asg["ground"].key if asg["ground"] else None, "ground_used_as_surface": bool(gok and strategy == "Full palette"),
        "brand": asg["brand"].key if asg["brand"] else None, "drench": asg["drench"].key if asg["drench"] else None,
        "voices": [m.key for m in asg["voices"]], "unused": asg["unused"],
        "pinned": sorted(pins), "status": status,
    }
    return {
        "schema": SCHEMA, "generated_by": "build_tokens.py",
        "name": title,
        "inputs": {"palette": palette, "hex": hexes, "strategy": strategy, "mode": mode_name, "roles": roles or {}, "pin": pin, "tint": tint},
        "palette": {**prov, "kasane_note": kasane_note, "members": [m.to_json() for m in members]},
        "strategy": {"name": strategy, "mode": mode_name},
        "policy": policy,
        "kasane_note": kasane_note,
        "assignment": assignment,
        "ramps": ramps,
        "roles": sem,
        "proportions": props,
        "warnings": warnings, "notes": notes,
        "contrast": None, "adjustments": [],
    }


# --------------------------------------------------------------------------- io helpers shared with other scripts


def load_tokens(path: str) -> dict:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    if data.get("schema") != SCHEMA:
        raise SystemExit(f"error: {path} is not an {SCHEMA} file")
    return data


def dump_tokens(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def parse_roles_arg(spec: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (spec or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            k = k.strip().lower()
            if k not in ("accent", "ground", "brand", "drench", "neutral"):
                raise SystemExit(f"error: unknown role {k!r} in --roles; use accent, ground, brand, drench, neutral")
            out[k] = v.strip()
    return out


def main(argv=None) -> int:
    cl.configure_stdio()
    ap = argparse.ArgumentParser(
        prog="build_tokens.py",
        description="Build OKLCH ramps, semantic light/dark roles, voice and status colours and proportion targets "
                    "from one palette (id from data/palettes.csv, or an explicit hex list). Emits JSON for validate.py, "
                    "preview.py and handoff.py.",
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--palette", help="palette id, e.g. wada-229, ed-kurenai-kon, paint-the-kiss, kasane-fuji")
    src.add_argument("--hex", help="comma-separated hex colours, optionally named: 'Paper=#f3ebda,#223344'")
    ap.add_argument("--strategy", default="restrained", help="restrained | committed | full-palette | drenched (default restrained)")
    ap.add_argument("--mode", default="operate", help="surface mode: persuade | operate | read | experience (default operate)")
    ap.add_argument("--roles", help="role assignment: accent=NAME,ground=NAME,brand=NAME,drench=NAME,neutral=NAME "
                                    "(NAME = colour name, 1-based index or hex)")
    ap.add_argument("--accent", help="shorthand for --roles accent=...")
    ap.add_argument("--neutral-from", dest="neutral_from", help="palette colour that tints the neutral ramp (name, index or hex)")
    ap.add_argument("--pin", default="all", help="ramps whose palette colour is kept exactly at its nearest step: "
                                                 "all (default: every palette colour stays visible) | none | comma list (accent,brand,voice-1,... or colour names)")
    ap.add_argument("--tint", type=float, default=1.0, help="neutral tint strength multiplier (default 1.0; chroma is capped at 0.03)")
    ap.add_argument("--on-accent", dest="on_accent", choices=ON_ACCENT_CHOICES, default="auto",
                    help="label colour on the accent fill: auto (measure, default) | light (e.g. a brand rule 'white button text': "
                         "the label is forced light and the accent fill moves to the nearest darker step that passes) | dark")
    ap.add_argument("--action-style", dest="action_style", choices=ACTION_STYLES, default="solid",
                    help="how primary actions look: solid (accent fill, default) | tinted (pale accent tint + accent border + body-text "
                         "label, for 'no saturated colour behind text') | outline (transparent, accent border, accent-text label). "
                         "Always emits --color-action, -action-hover, -on-action, -action-border")
    ap.add_argument("--text-min", dest="text_min", type=float, default=WCAG_BODY,
                    help="WCAG ratio floor for body and label text (default 4.5; e.g. 7 for 'comfortably above minimum'); "
                         "the large-text floor rises to text-min/1.5 when above 4.5 (3.0 otherwise)")
    ap.add_argument("--name", help="display name for the design (default: palette title)")
    ap.add_argument("--provenance", help="provenance label for --hex input (refused if it names a data source: Wada plate / editorial palette / Sampled from / Kasane / colorcombinations.org), e.g. \"Original composition by this skill (not a plate)\" "
                                         "(default: Original composition (colours supplied by the user))")
    ap.add_argument("--out", type=Path, help="write JSON here instead of stdout")
    ap.add_argument("--data-dir", type=Path, help="folder with palettes.csv (default <skill>/data)")
    args = ap.parse_args(argv)
    roles = parse_roles_arg(args.roles)
    if args.accent:
        roles["accent"] = args.accent
    if args.neutral_from:
        roles["neutral"] = args.neutral_from
    try:
        data = build_tokens(args.palette, args.hex, args.strategy, args.mode, roles, args.pin, args.tint, args.name, args.data_dir, args.provenance,
                            args.on_accent, args.action_style, args.text_min)
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            return 2
        raise
    text = dump_tokens(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}  ({data['palette']['label']}; strategy {data['strategy']['name']}, mode {data['strategy']['mode']})")
    else:
        sys.stdout.write(text)
    for w in data["warnings"]:
        print(f"warning: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
