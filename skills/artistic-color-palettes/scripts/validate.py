#!/usr/bin/env python3
"""validate.py - measure the contrast of a build_tokens.py result and (optionally) fix it.

Reads the JSON from build_tokens.py and checks every text/surface and non-text pair in light and
dark mode:
  * WCAG 2 gate  - body text >= 4.5, large text >= 3.0, non-text UI >= 3.0  (must pass)
  * APCA-W3 Lc target (0.0.98G-4g)  - body 75, labels 60, large 45, fine detail 45, solid UI 30,
    dividers 15  (reported; --fix nudges toward it only inside a small lightness budget)
  * flags (reported, never auto-fixed): vibrating pairs (Albers 12), vanishing pairs (Albers 13),
    mid-lightness fills, CVD distinguishability of the accent against the status colours and of the
    status colours against each other, ramp lightness steps (neighbour dL >= 0.03, wider at the dark end)

--fix changes lightness only (hue kept; chroma reduced only if the new lightness leaves the sRGB
gamut), never touches page or surface colours, never darkens a pinned palette colour (the role
moves to another ramp step instead), and prints an adjustment report: role, before/after hex,
before/after OKLCH L, before/after ratio.

Policy flags recorded by build_tokens.py are honoured: --text-min raises the body/label gate (large text rises to text-min/1.5),
--on-accent light|dark keeps the label polarity (--fix never flips it, it moves the fill), --action-style tinted|outline validates
the action tokens (--color-action, -hover, -on-action, -border) instead of the solid accent pair. Voice and brand colours are
region fills (the exact plate colour): only text on them is gated (advisory when no label reaches 3:1), and their -mark step
carries the 3:1 non-text gate. A pinned palette value is never altered: a failing role moves to another step, or, when no step
passes, gets an adjusted copy while the pinned value stays in its ramp.

Exit code: 0 no gate failure (after fixing when --fix) | 1 at least one gate failure | 2 bad input.

Examples:
  python3 scripts/validate.py tokens.json
  python3 scripts/validate.py tokens.json --fix --out tokens.fixed.json
  python3 scripts/build_tokens.py --palette wada-229 | python3 scripts/validate.py - --fix --json
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colorlib as cl  # noqa: E402
import build_tokens as bt  # noqa: E402

APCA_TARGET = {"body": 75, "label": 60, "large": 45, "detail": 45, "ui": 30, "divider": 15, "advisory": 60}
WCAG_MIN = {"body": 4.5, "label": 4.5, "large": 3.0, "detail": 3.0, "ui": 3.0, "divider": None, "advisory": None}
DEFAULT_POLICY = {"text_min": 4.5, "large_text_min": 3.0, "on_accent": "auto", "action_style": "solid"}


def policy_of(tokens: dict) -> dict:
    return {**DEFAULT_POLICY, **(tokens.get("policy") or {})}


def wcag_min_for(tokens: dict, size: str):
    """Gate for a pair class, honouring --text-min (body and label text) and its large-text companion."""
    pol = policy_of(tokens)
    if size in ("body", "label"):
        return pol["text_min"]
    if size == "large":
        return pol["large_text_min"]
    return WCAG_MIN[size]
VIBRATE_HUE, VIBRATE_C, VIBRATE_DL = 100.0, 0.10, 0.15
VANISH_DL, VANISH_HUE, VANISH_C = 0.10, 40.0, 0.04
CVD_MIN_DE = 0.05
RAMP_MIN_DL = bt.MIN_STEP_DL
RAMP_DARK_END_DL = 0.05
RAMP_TOL = 0.004  # 8-bit rounding of a hex value moves its measured L by up to a few thousandths
FIX_STEP = 0.005
FIX_MAX_SHIFT = 0.70
APCA_NUDGE_MAX = 0.04
SURFACES = ("bg", "bg-subtle", "surface", "surface-hover")


# --------------------------------------------------------------------------- pair list


def fill_names(tokens: dict) -> list[str]:
    names = ["accent"]
    roles = tokens["roles"]["light"]
    for n in ["brand"] + [f"voice-{i}" for i in range(1, 12)] + ["success", "warning", "danger", "info"]:
        if n in roles:
            names.append(n)
    return names


REGION_FILLS = ("brand",)  # plus every voice-n: region fills, not gated against the page


def is_region(name: str) -> bool:
    return name in REGION_FILLS or (name.startswith("voice-") and name.count("-") == 1)


def pair_specs(tokens: dict) -> list[dict]:
    specs = []
    style = policy_of(tokens)["action_style"]

    def add(fg, bg, size, kind, label):
        specs.append({"fg": fg, "bg": bg, "size": size, "kind": kind, "label": label})

    for bg in SURFACES:
        add("text", bg, "body", "text", "text")
    for bg in SURFACES:
        add("text-muted", bg, "label", "text", "muted text")
    for bg in ("bg", "surface"):
        add("accent-text", bg, "body", "text", "link / accent text")
    add("accent-text", "accent-subtle", "label", "text", "accent text on its tint")
    if style == "solid":
        add("on-accent", "accent", "label", "text", "text on accent fill")
        add("on-accent", "accent-hover", "label", "text", "text on accent hover")
    else:
        add("on-action", "action", "label", "text", f"label on the {style} action")
        add("on-action", "action-hover", "label", "text", f"label on the {style} action, hovered")
        for bg in ("bg", "surface"):
            add("action-border", bg, "detail", "nontext", f"{style} action border")
    for f in fill_names(tokens)[1:]:
        if is_region(f):
            add(f"on-{f}", f, "region_label", "text", f"text on the {f} region fill")
        else:
            add(f"on-{f}", f, "label", "text", f"text on {f} fill")
        add(f"{f}-text", f"{f}-subtle", "label", "text", f"{f} text on its tint")
        add(f"{f}-text", "bg", "body", "text", f"{f} text on page")
        add("text", f"{f}-subtle", "body", "text", f"body text on {f} tint")
    add("text", "accent-subtle", "body", "text", "body text on accent tint")
    for bg in ("bg", "surface"):
        add("focus", bg, "detail", "nontext", "focus ring")
        add("border-strong", bg, "detail", "nontext", "control border")
    for f in fill_names(tokens):
        for bg in ("bg", "surface"):
            if is_region(f):
                add(f"{f}-mark", bg, "ui", "nontext", f"{f} chart mark / icon")
            else:
                add(f, bg, "ui", "nontext", f"{f} fill / chart mark")
    for t in ("border", "border-subtle"):
        add(t, "bg", "divider", "nontext", "decorative divider")
    return specs


# --------------------------------------------------------------------------- measuring


def hex_of(tokens: dict, mode: str, token: str) -> str:
    return tokens["roles"][mode][token]["hex"]


def measure_pair(tokens: dict, mode: str, spec: dict) -> dict | None:
    roles = tokens["roles"][mode]
    if spec["fg"] not in roles or spec["bg"] not in roles:
        return None
    fg, bg = roles[spec["fg"]]["hex"], roles[spec["bg"]]["hex"]
    ratio = cl.wcag_contrast(fg, bg)
    lc = cl.apca_lc(fg, bg)
    size = spec["size"]
    if size == "region_label":
        # text on a region fill (the exact plate colour): gated at the text floor, then at the large-text floor; if neither
        # polarity reaches 3:1 the fill is a graphic band only and the pair is advisory (application-rules section 4)
        pol = policy_of(tokens)
        size = "label" if ratio >= pol["text_min"] else "large" if ratio >= pol["large_text_min"] else "advisory"
    wmin = wcag_min_for(tokens, size)
    target = APCA_TARGET[size]
    # print-safe values: a failing value that would round up to its threshold keeps extra digits (never "4.5 < 4.5")
    w_shown = round(ratio, 2)
    if wmin is not None and ratio + 1e-9 < wmin and w_shown >= wmin:
        w_shown = math.floor(ratio * 1000) / 1000
    lc_shown = round(lc, 1)
    if abs(lc) < target and abs(lc_shown) >= target:
        lc_shown = math.copysign(math.floor(abs(lc) * 100) / 100, lc)
    return {
        "mode": mode, "fg": spec["fg"], "bg": spec["bg"], "fg_hex": fg, "bg_hex": bg, "kind": spec["kind"],
        "size": size, "label": spec["label"], "wcag": w_shown, "wcag_min": wmin,
        "wcag_pass": True if wmin is None else ratio + 1e-9 >= wmin, "gate": wmin is not None,
        "apca": lc_shown, "apca_target": target, "apca_pass": abs(lc) >= target,
    }


def measure_all(tokens: dict) -> list[dict]:
    out = []
    for mode in ("light", "dark"):
        for spec in pair_specs(tokens):
            m = measure_pair(tokens, mode, spec)
            if m:
                out.append(m)
    return out


def ramp_checks(tokens: dict) -> list[dict]:
    out = []
    for name, ramp in tokens["ramps"].items():
        if "light" not in ramp:
            continue
        for mode in ("light", "dark"):
            pinned = ramp.get("pinned", {}).get(mode)
            Ls = [cl.hex_to_oklch(ramp[mode][s])[0] for s in bt.STEPS]
            for i in range(len(bt.STEPS) - 1):
                hi, lo = Ls[i], Ls[i + 1]  # step i is lighter than step i+1
                d = hi - lo
                a, b = bt.STEPS[i], bt.STEPS[i + 1]
                need = RAMP_MIN_DL
                if mode == "dark" and i >= 6 and pinned not in (a, b):
                    need = RAMP_DARK_END_DL
                ok = d + RAMP_TOL >= need
                if not ok:
                    out.append({"ramp": name, "mode": mode, "steps": f"{a}-{b}", "dL": round(d, 4), "need": need})
    return out


def default_adjacency(tokens: dict) -> list[tuple[str, str]]:
    """Fill pairs declared as distinct regions (the vanishing check applies to these only): page/surface,
    surface/accent tint, every voice pair, and the chart series (accent plus voices)."""
    roles = tokens["roles"]["light"]
    voices = [f"voice-{i}" for i in range(1, 12) if f"voice-{i}" in roles]
    pairs = [("bg", "surface"), ("surface", "accent-subtle")]
    pairs += [(a, b) for i, a in enumerate(voices) for b in voices[i + 1:]]
    pairs += [("accent", v) for v in voices]
    return pairs


STATE_SIBLINGS = [("accent", "accent-hover"), ("surface", "surface-hover"), ("action", "action-hover")]
STATE_MIN_DL = 0.06


def parse_adjacency(spec: str) -> list[tuple[str, str]]:
    out = []
    for part in spec.split(","):
        if ":" in part:
            a, b = part.split(":", 1)
            out.append((a.strip(), b.strip()))
    return out


def flag_checks(tokens: dict, adjacency: list[tuple[str, str]] | None = None) -> list[dict]:
    flags = []
    names = fill_names(tokens)
    adjacency = default_adjacency(tokens) if adjacency is None else adjacency
    for mode in ("light", "dark"):
        roles = tokens["roles"][mode]
        fills = {n: hex_of(tokens, mode, n) for n in names}
        okl = {n: cl.hex_to_oklch(h) for n, h in fills.items()}
        status = {"success", "warning", "danger", "info"}
        # vibrating: palette fills that sit side by side, and the accent beside a status colour
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if (a in status or b in status) and "accent" not in (a, b):
                    continue
                (La, Ca, ha), (Lb, Cb, hb) = okl[a], okl[b]
                dh, dl = cl.hue_diff(ha, hb), abs(La - Lb)
                if dh >= VIBRATE_HUE and Ca >= VIBRATE_C and Cb >= VIBRATE_C and dl < VIBRATE_DL:
                    flags.append({"type": "vibrating", "mode": mode, "a": a, "b": b, "hue_diff": round(dh, 1),
                                  "dL": round(dl, 3), "advice": "keep these two apart, separate with a neutral or a lightness step"})
        # vanishing: only pairs declared as distinct regions (adjacency list)
        for a, b in adjacency:
            if a not in roles or b not in roles:
                continue
            La, Ca, ha = cl.hex_to_oklch(roles[a]["hex"])
            Lb, Cb, hb = cl.hex_to_oklch(roles[b]["hex"])
            dh, dl = cl.hue_diff(ha, hb), abs(La - Lb)
            tinted = Ca >= VANISH_C and Cb >= VANISH_C
            if dl < VANISH_DL and (dh < VANISH_HUE or not tinted):
                flags.append({"type": "vanishing", "mode": mode, "a": a, "b": b, "hue_diff": round(dh, 1) if tinted else None,
                              "dL": round(dl, 3), "advice": "adjacent regions may merge; separate them with a border, a gap or a lightness step of at least 0.10"})
        # state siblings (rest / hover): a small step is intended, but it must be visible and never the only cue
        for a, b in STATE_SIBLINGS:
            if a == "action" and policy_of(tokens)["action_style"] == "solid":
                continue  # an alias of the accent pair
            if a in roles and b in roles:
                dl = abs(cl.hex_to_oklch(roles[a]["hex"])[0] - cl.hex_to_oklch(roles[b]["hex"])[0])
                if dl < STATE_MIN_DL:
                    flags.append({"type": "state_sibling", "mode": mode, "a": a, "b": b, "dL": round(dl, 3),
                                  "advice": f"dL below {STATE_MIN_DL}: the state change is faint, add a non-colour cue (underline, outline, icon, weight)"})
        for n in names:
            meta = roles.get(f"on-{n}", {})
            if "mid_lightness_fill" in meta:
                m = meta["measured"]
                flags.append({"type": "mid_lightness_fill", "mode": mode, "a": n, "L": meta["mid_lightness_fill"],
                              "white": m["white"], "neutral_950": m["neutral-950"],
                              "advice": "both text polarities were measured; the better one was chosen"})
        cvd_set = ["accent", "success", "warning", "danger", "info"]
        for i, a in enumerate(cvd_set):
            for b in cvd_set[i + 1:]:
                if a not in fills or b not in fills:
                    continue
                low = {}
                for kind in cl.CVD_MATRICES:
                    de = cl.delta_e_ok(cl.simulate_cvd(fills[a], kind), cl.simulate_cvd(fills[b], kind))
                    if de < CVD_MIN_DE:
                        low[kind] = round(de, 3)
                if low:
                    flags.append({"type": "cvd", "mode": mode, "a": a, "b": b, "delta_e_ok": low,
                                  "normal_delta_e_ok": round(cl.delta_e_ok(fills[a], fills[b]), 3),
                                  "advice": "do not rely on colour alone; add an icon, label or lightness difference"})
    return flags


# --------------------------------------------------------------------------- fixing


def pinned_ref(tokens: dict, mode: str, token: str) -> tuple[str, str] | None:
    ref = tokens["roles"][mode][token]["ref"]
    if ":" not in ref or ref.startswith("literal:"):
        return None
    name, step = ref.split(":")
    ramp = tokens["ramps"].get(name)
    if ramp and ramp.get("pinned", {}).get(mode) == step:
        return name, step
    return None


def refresh_on(tokens: dict, mode: str, fill: str) -> None:
    on = f"on-{fill}"
    roles = tokens["roles"][mode]
    if on not in roles or roles[on].get("alias_of"):
        return
    fill_hex = roles[fill]["hex"]
    dark_hex = tokens["ramps"]["neutral"][mode]["950"]
    rw, rd = cl.wcag_contrast(bt.WHITE, fill_hex), cl.wcag_contrast(dark_hex, fill_hex)
    force = policy_of(tokens)["on_accent"] if fill == "accent" else "auto"
    light = (rw >= rd) if force == "auto" else (force == "light")  # a forced polarity is respected, never flipped
    if light:
        roles[on].update(ref=f"literal:{bt.WHITE}", hex=bt.WHITE)
    else:
        roles[on].update(ref="neutral:950", hex=dark_hex)
    roles[on]["L"] = bt.r3(cl.hex_to_oklch(roles[on]["hex"])[0])
    roles[on]["measured"] = {"white": round(rw, 2), "neutral-950": round(rd, 2)}


def gate_pairs_for(tokens: dict, mode: str, tokens_involved: set[str]) -> list[dict]:
    out = []
    for spec in pair_specs(tokens):
        if spec["fg"] in tokens_involved or spec["bg"] in tokens_involved:
            m = measure_pair(tokens, mode, spec)
            if m and m["gate"]:
                out.append(m)
    return out


def all_pass(pairs: list[dict]) -> bool:
    return all(p["wcag_pass"] for p in pairs)


def set_hex(tokens: dict, mode: str, token: str, hx: str) -> None:
    r = tokens["roles"][mode][token]
    r["hex"] = hx
    r["L"] = bt.r3(cl.hex_to_oklch(hx)[0])


def shifted_hex(hx: str, dL: float) -> str:
    L, C, h = cl.hex_to_oklch(hx)
    nL = min(0.995, max(0.02, L + dL))
    return cl.oklch_to_hex(nL, min(C, cl.max_chroma(nL, h)), h)


def try_fix_token(tokens: dict, mode: str, token: str, prefer: int) -> dict | None:
    """Find the smallest L change (or, for a pinned colour, the nearest other step) that makes every
    gated pair involving `token` pass. Mutates tokens on success and returns the adjustment record."""
    roles = tokens["roles"][mode]
    entry = roles[token]
    before_hex, before_ref = entry["hex"], entry["ref"]
    involved = {token}
    is_fill = token in fill_names(tokens)
    if is_fill:
        involved.add(f"on-{token}")
    involved |= {t for t, rr in roles.items() if rr.get("alias_of") in involved}  # tokens that mirror the moved role
    snapshot = copy.deepcopy({t: roles[t] for t in involved if t in roles})

    style = policy_of(tokens)["action_style"]

    def restore():
        for t, v in snapshot.items():
            roles[t] = copy.deepcopy(v)
        bt.sync_action_aliases(roles, style)

    pin = pinned_ref(tokens, mode, token)
    if pin:
        name, step = pin
        order = sorted((s for s in bt.STEPS if s != step), key=lambda s: (abs(bt.STEPS.index(s) - bt.STEPS.index(step)), s))
        for s in order:
            roles[token]["ref"] = f"{name}:{s}"
            set_hex(tokens, mode, token, tokens["ramps"][name][mode][s])
            if is_fill:
                refresh_on(tokens, mode, token)
            bt.sync_action_aliases(roles, style)
            if all_pass(gate_pairs_for(tokens, mode, involved)):
                return {"moved_step": f"{name}:{step} -> {name}:{s}", "reason": "pinned palette colour kept exactly; role moved to another step"}
        # no other ramp step passes (e.g. a forced light label in dark mode): the pinned colour stays untouched in its ramp and
        # in --<ramp>-seed; only this role gets a lightness-adjusted copy, and the report says so
        restore()
    for k in range(1, int(FIX_MAX_SHIFT / FIX_STEP) + 1):
        for sign in (prefer, -prefer):
            cand = shifted_hex(before_hex, sign * k * FIX_STEP)
            if cand == before_hex:
                continue
            set_hex(tokens, mode, token, cand)
            if is_fill:
                refresh_on(tokens, mode, token)
            bt.sync_action_aliases(roles, style)
            if all_pass(gate_pairs_for(tokens, mode, involved)):
                entry["adjusted"] = {"from_ref": before_ref, "from_hex": before_hex}
                return {"moved_step": None, "reason": "WCAG gate"}
    restore()
    return None


def away_from(tokens: dict, mode: str, token: str, bg_token: str) -> int:
    Lf = cl.hex_to_oklch(hex_of(tokens, mode, token))[0]
    Lb = cl.hex_to_oklch(hex_of(tokens, mode, bg_token))[0]
    return -1 if Lb > Lf else 1


def fix(tokens: dict) -> list[dict]:
    adjustments: list[dict] = []
    for _round in range(6):
        pairs = measure_all(tokens)
        failing = [p for p in pairs if p["gate"] and not p["wcag_pass"]]
        if not failing:
            break
        progressed = False
        for p in failing:
            mode = p["mode"]
            cur = measure_pair(tokens, mode, {"fg": p["fg"], "bg": p["bg"], "size": p["size"], "kind": p["kind"], "label": p["label"]})
            if cur["wcag_pass"]:
                continue
            movable = None
            if p["fg"].startswith("on-") and p["bg"] in tokens["roles"][mode] and p["bg"] not in SURFACES:
                movable = p["bg"]  # move the fill; the on-colour is re-measured
            elif p["fg"] not in SURFACES:
                movable = p["fg"]
            elif p["bg"] not in SURFACES:
                movable = p["bg"]
            if movable is None or movable.startswith("on-"):
                continue
            while tokens["roles"][mode].get(movable, {}).get("alias_of"):
                movable = tokens["roles"][mode][movable]["alias_of"]  # an alias is fixed through the role it mirrors
            ref_bg = p["bg"] if movable == p["fg"] else p["fg"]
            if movable in ("accent",) or movable in fill_names(tokens):
                ref_bg = "bg"
            prefer = away_from(tokens, mode, movable, ref_bg)
            before = hex_of(tokens, mode, movable)
            b_ratio = cl.wcag_contrast(before, hex_of(tokens, mode, ref_bg))
            res = try_fix_token(tokens, mode, movable, prefer)
            if res:
                after = hex_of(tokens, mode, movable)
                adjustments.append(adjustment_record(mode, movable, before, after, b_ratio,
                                                     cl.wcag_contrast(after, hex_of(tokens, mode, ref_bg)), ref_bg, res))
                progressed = True
        for m in ("light", "dark"):
            bt.sync_action_aliases(tokens["roles"][m], policy_of(tokens)["action_style"])
        if not progressed:
            break
    adjustments += apca_nudges(tokens)
    for m in ("light", "dark"):
        bt.sync_action_aliases(tokens["roles"][m], policy_of(tokens)["action_style"])
    return adjustments


def adjustment_record(mode, role, before, after, b_ratio, a_ratio, against, res, step_note=None) -> dict:
    return {
        "mode": mode, "role": role, "before_hex": before, "after_hex": after,
        "before_L": bt.r3(cl.hex_to_oklch(before)[0]), "after_L": bt.r3(cl.hex_to_oklch(after)[0]),
        "before_ratio": round(b_ratio, 2), "after_ratio": round(a_ratio, 2), "against": against,
        "reason": res["reason"], "moved_step": res.get("moved_step"),
    }


def apca_nudges(tokens: dict) -> list[dict]:
    """Phase 2: text roles that pass the WCAG gate but miss their APCA target are darkened/lightened
    by at most APCA_NUDGE_MAX of L, only if that reaches the target on every surface and keeps every gate."""
    out = []
    for mode in ("light", "dark"):
        for token in ("text", "text-muted", "accent-text"):
            if token not in tokens["roles"][mode] or pinned_ref(tokens, mode, token):
                continue
            specs = [s for s in pair_specs(tokens) if s["fg"] == token and s["kind"] == "text"]
            ms = [measure_pair(tokens, mode, s) for s in specs]
            ms = [m for m in ms if m]
            if not ms or all(m["apca_pass"] for m in ms):
                continue
            before = hex_of(tokens, mode, token)
            prefer = away_from(tokens, mode, token, ms[0]["bg"])
            worst_bg = min(ms, key=lambda m: abs(m["apca"]))["bg"]
            b_ratio = cl.wcag_contrast(before, hex_of(tokens, mode, worst_bg))
            prior = copy.deepcopy(tokens["roles"][mode][token])
            for k in range(1, int(APCA_NUDGE_MAX / FIX_STEP) + 1):
                cand = shifted_hex(before, prefer * k * FIX_STEP)
                set_hex(tokens, mode, token, cand)
                ms2 = [measure_pair(tokens, mode, s) for s in specs]
                ms2 = [m for m in ms2 if m]
                if all(m["apca_pass"] for m in ms2) and all_pass(gate_pairs_for(tokens, mode, {token})):
                    tokens["roles"][mode][token]["adjusted"] = {"from_ref": prior["ref"], "from_hex": before}
                    out.append(adjustment_record(mode, token, before, cand, b_ratio, cl.wcag_contrast(cand, hex_of(tokens, mode, worst_bg)),
                                                 worst_bg, {"reason": "APCA target", "moved_step": None}))
                    break
            else:
                tokens["roles"][mode][token] = prior
    return out


# --------------------------------------------------------------------------- reporting


def validate_tokens(tokens: dict, do_fix: bool = False, adjacency: list[tuple[str, str]] | None = None) -> dict:
    """Mutates `tokens` when do_fix. Returns the contrast block (also stored in tokens['contrast'])."""
    adjustments = list(tokens.get("adjustments") or [])
    if do_fix:
        adjustments += fix(tokens)
    pairs = measure_all(tokens)
    rchecks = ramp_checks(tokens)
    flags = flag_checks(tokens, adjacency)
    gate_fail = [p for p in pairs if p["gate"] and not p["wcag_pass"]]
    apca_miss = [p for p in pairs if not p["apca_pass"]]
    block = {
        "gate_pass": not gate_fail and not rchecks,
        "summary": {"pairs": len(pairs), "gate_failures": len(gate_fail), "ramp_failures": len(rchecks),
                    "apca_below_target": len(apca_miss), "flags": len(flags)},
        "pairs": pairs, "ramp_failures": rchecks, "flags": flags,
        "standards": {"wcag": "WCAG 2.x contrast ratio", "apca": "APCA-W3 0.0.98G-4g Lc (absolute value)"},
    }
    tokens["contrast"] = block
    tokens["adjustments"] = adjustments
    return block


APCA_GROUP_LIMIT = 4  # more shortfall groups than this in one mode -> collapse by role family in the text report


def role_family(role: str) -> str:
    """Coarse family for collapsing APCA shortfalls in the text report."""
    for s in ("success", "warning", "danger", "info"):
        if role == s or role.startswith(s + "-") or role.startswith("on-" + s):
            return "status roles"
    if role.startswith("voice-") or role.startswith("on-voice"):
        return "voice roles"
    if role.startswith("border"):
        return "borders"
    if role == "focus":
        return "focus ring"
    if role.startswith(("accent", "on-accent", "action", "on-action")):
        return "accent roles"
    if role.startswith("text"):
        return "text"
    return "other roles"


def fmt_lc(v: float) -> str:
    """One decimal, or two when one decimal would hide the difference (stored values already carry that precision)."""
    return f"{v:.1f}" if abs(round(v, 1) - v) < 1e-9 else f"{v:.2f}"


def text_report(tokens: dict, show_all: bool) -> str:
    c = tokens["contrast"]
    s = c["summary"]
    lines = [f"validate: {tokens['palette']['label']} | strategy {tokens['strategy']['name']}, mode {tokens['strategy']['mode']}",
             f"pairs {s['pairs']} | WCAG gate failures {s['gate_failures']} | ramp failures {s['ramp_failures']} | "
             f"APCA below target {s['apca_below_target']} | flags {s['flags']}"]
    fails = [p for p in c["pairs"] if p["gate"] and not p["wcag_pass"]]
    if fails:
        lines.append("")
        lines.append("GATE FAILURES")
        for p in fails:
            lines.append(f"  [{p['mode']}] {p['fg']} {p['fg_hex']} on {p['bg']} {p['bg_hex']}: {p['wcag']}:1 < {p['wcag_min']}:1 ({p['label']})")
    for r in c["ramp_failures"]:
        lines.append(f"  RAMP {r['ramp']} {r['mode']} steps {r['steps']}: dL {r['dL']} < {r['need']}")
    misses = [p for p in c["pairs"] if not p["apca_pass"] and p["wcag_pass"]]
    if misses:
        lines.append("")
        lines.append("APCA below target (reported; the WCAG gate decides pass/fail)")
        groups: dict[tuple, list] = {}
        for p in misses:
            groups.setdefault((p["mode"], p["fg"], p["apca_target"]), []).append(p)
        per_mode: dict[str, int] = {}
        for (mode, _fg, _t) in groups:
            per_mode[mode] = per_mode.get(mode, 0) + 1
        for mode in sorted(per_mode, key=lambda m: (m != "light", m)):
            mode_groups = {k: v for k, v in groups.items() if k[0] == mode}
            if show_all or per_mode[mode] <= APCA_GROUP_LIMIT:
                for (_m, fg, target), ps in mode_groups.items():
                    lcs = [abs(p["apca"]) for p in ps]
                    rng = fmt_lc(min(lcs)) if fmt_lc(min(lcs)) == fmt_lc(max(lcs)) else f"{fmt_lc(min(lcs))}-{fmt_lc(max(lcs))}"
                    lines.append(f"  [{mode}] {fg} on {', '.join(p['bg'] for p in ps)}: Lc {rng} < {target}")
                continue
            # many shortfalls: one line per role family with its worst pair (--all lists every pair)
            fams: dict[str, list] = {}
            for (_m, fg, _t), ps in mode_groups.items():
                fams.setdefault(role_family(fg), []).extend(ps)
            for fam, ps in fams.items():
                worst = max(ps, key=lambda p: p["apca_target"] - abs(p["apca"]))
                roles = sorted({p["fg"] for p in ps})
                lines.append(f"  [{mode}] {fam} ({len(ps)} pairs: {', '.join(roles)}): worst {worst['fg']} on {worst['bg']} "
                             f"Lc {fmt_lc(abs(worst['apca']))} < {worst['apca_target']}")
            lines.append(f"  [{mode}] (--all lists every pair)")
    if c["flags"]:
        lines.append("")
        lines.append("FLAGS (advice per flag type follows the list)")
        advice: dict[str, str] = {}
        for f in c["flags"]:
            if f["type"] == "cvd":
                low = ", ".join(f"{k} {v}" for k, v in f["delta_e_ok"].items())
                lines.append(f"  [{f['mode']}] cvd: {f['a']} vs {f['b']} dE_OK under {low} (normal vision {f['normal_delta_e_ok']})")
            elif f["type"] == "mid_lightness_fill":
                lines.append(f"  [{f['mode']}] mid-lightness fill {f['a']} (L {f['L']}): white {f['white']}:1 vs neutral-950 {f['neutral_950']}:1 measured")
            else:
                hd = f"hue diff {f['hue_diff']}, " if f.get("hue_diff") is not None else ""
                lines.append(f"  [{f['mode']}] {f['type']}: {f['a']} vs {f['b']} ({hd}dL {f['dL']})")
            if f.get("advice"):
                advice.setdefault(f["type"].replace("_", " ").replace("mid lightness fill", "mid-lightness fill"), f["advice"])
        for kind, text in advice.items():
            lines.append(f"  advice, {kind}: {text}")
    if tokens.get("adjustments"):
        lines.append("")
        lines.append("ADJUSTMENTS (lightness only; nothing else moved)")
        for a in tokens["adjustments"]:
            moved = f" [{a['moved_step']}]" if a.get("moved_step") else ""
            lines.append(f"  [{a['mode']}] {a['role']}: {a['before_hex']} -> {a['after_hex']} | L {a['before_L']} -> {a['after_L']} | "
                         f"ratio {a['before_ratio']} -> {a['after_ratio']} vs {a['against']} | {a['reason']}{moved}")
    if show_all:
        lines.append("")
        lines.append("ALL PAIRS")
        for p in c["pairs"]:
            lines.append(f"  [{p['mode']}] {p['fg']:<16} on {p['bg']:<14} {p['wcag']:>6}:1  Lc {fmt_lc(abs(p['apca'])):>6}  "
                         f"{'ok' if p['wcag_pass'] else 'FAIL'}{'' if p['apca_pass'] else ' (apca<'+str(p['apca_target'])+')'}")
    lines.append("")
    lines.append("RESULT: " + ("PASS" if c["gate_pass"] else "FAIL"))
    return "\n".join(lines)


def main(argv=None) -> int:
    cl.configure_stdio()
    ap = argparse.ArgumentParser(
        prog="validate.py",
        description="Measure WCAG 2 / APCA contrast, flags and ramp steps of a build_tokens.py result; --fix adjusts lightness only.",
        epilog="Exit codes: 0 no gate failure | 1 gate failure | 2 bad input.",
    )
    ap.add_argument("tokens", help="tokens JSON from build_tokens.py ('-' reads stdin)")
    ap.add_argument("--fix", action="store_true", help="adjust L of failing roles until the WCAG gate passes (and toward APCA targets within a small budget)")
    ap.add_argument("--out", type=Path, help="write the annotated (and fixed) tokens JSON here")
    ap.add_argument("--in-place", action="store_true", help="overwrite the input file with the annotated tokens")
    ap.add_argument("--all", action="store_true", help="list every measured pair in the text report")
    ap.add_argument("--adjacency", help="regions declared as distinct, for the vanishing check: 'bg:surface,voice-1:voice-2' "
                                        "(default: bg/surface, surface/accent-subtle, voice pairs, accent/voice chart series)")
    ap.add_argument("--json", action="store_true", help="print the annotated tokens JSON to stdout instead of the text report")
    args = ap.parse_args(argv)
    try:
        tokens = bt.load_tokens(args.tokens)
    except (OSError, ValueError, SystemExit) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    validate_tokens(tokens, args.fix, parse_adjacency(args.adjacency) if args.adjacency else None)
    text = bt.dump_tokens(tokens)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    if args.in_place and args.tokens != "-":
        Path(args.tokens).write_text(text, encoding="utf-8", newline="\n")
    if args.json:
        sys.stdout.write(text)
    else:
        print(text_report(tokens, args.all))
        if args.fix and not (args.out or args.in_place):
            print("(fixed values were not saved: add --out FILE or --in-place)")
    return 0 if tokens["contrast"]["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
