#!/usr/bin/env python3
"""handoff.py - hand a validated palette to the neighbouring design skills through shared files.

Writes (all derived from one tokens JSON, so they cannot disagree):
  DESIGN.md             project root; ONLY the text between our markers is ever rewritten
                          frontmatter  colors:  between '# acp:begin tokens' and '# acp:end tokens'
                          body  '## Colors'     between '<!-- acp:begin colors v1 -->' and '<!-- acp:end colors -->'
                        missing file  -> palette-only seed is created
                        existing file without our markers -> markers are inserted, a diff is printed,
                        and --yes is required to write
  design/palette.json   source of truth (provenance, roles, ramps, light/dark sets, contrast, adjustments,
                        proportion targets, handoff.claude_md)
  design/tokens.css     two-tier CSS custom properties (primitives, then semantic --color-* with light,
                        prefers-color-scheme dark and [data-theme=dark]) plus alias blocks for Taste,
                        UI/UX Pro Max and interface-design token names
  CLAUDE.md, AGENTS.md  only with --claude-md yes: a marker-delimited pointer (--claude-md no removes it);
                        never the home directory

Re-running with the same input is byte-identical. Exit codes: 0 done | 1 contrast gate fails |
2 bad input or broken markers | 3 DESIGN.md insertion needs --yes | 4 --claude-md yes without --user-confirmed.

Examples:
  python3 scripts/handoff.py --palette wada-229 --strategy restrained --project-dir ./myapp
  python3 scripts/handoff.py --tokens tokens.json --project-dir . --yes --claude-md yes
  python3 scripts/handoff.py --tokens tokens.json --dry-run
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colorlib as cl  # noqa: E402
import build_tokens as bt  # noqa: E402
import validate as vd  # noqa: E402

HANDOFF_VERSION = 1
FM_BEGIN_TEXT = "# acp:begin tokens (artistic-color-palettes; do not edit between markers)"
FM_END_TEXT = "# acp:end tokens"
BODY_BEGIN = "<!-- acp:begin colors v1 -->"
BODY_END = "<!-- acp:end colors -->"
PTR_BEGIN = "<!-- acp:begin pointer v1 -->"
PTR_END = "<!-- acp:end pointer -->"
PTR_TEXT = ("Colour: the project palette lives in DESIGN.md (## Colors) and design/tokens.css. Use those tokens; "
            "do not choose new colours. Palette decisions come from the artistic-color-palettes skill.")
SEED_COMMENT = "<!-- acp:seed palette-only; Impeccable's document command will fill the other sections -->"

RE_FM_BEGIN = re.compile(r"^[ \t]*# acp:begin tokens\b")
RE_FM_END = re.compile(r"^[ \t]*# acp:end tokens\b")
RE_BODY_BEGIN = re.compile(r"^[ \t]*<!-- acp:begin colors v\d+ -->[ \t]*$")
RE_BODY_END = re.compile(r"^[ \t]*<!-- acp:end colors -->[ \t]*$")
RE_PTR_BEGIN = re.compile(r"^[ \t]*<!-- acp:begin pointer v\d+ -->[ \t]*$")
RE_PTR_END = re.compile(r"^[ \t]*<!-- acp:end pointer -->[ \t]*$")
CANONICAL = ["overview", "colors", "typography", "layout", "elevation", "shapes", "components", "do's"]


class HandoffError(Exception):
    pass


# --------------------------------------------------------------------------- small text helpers


def hx(value: str) -> str:
    return value.upper()


def entry(name: str, hex_: str, desc: str) -> str:
    return f"- **{name}** ({hx(hex_)} / {cl.hex_oklch_css(hex_)}): {desc}"


def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def write_bytes_if_changed(path: Path, text: str) -> str:
    """Write UTF-8 text with the newlines it already carries; return 'created' | 'updated' | 'unchanged'."""
    data = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() == data:
            return "unchanged"
        status = "updated"
    else:
        status = "created"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return status


def role_hex(tokens: dict, mode: str, token: str) -> str:
    return tokens["roles"][mode][token]["hex"]


def has_role(tokens: dict, token: str) -> bool:
    return token in tokens["roles"]["light"]


def member_name(tokens: dict, key: str | None) -> str:
    for m in tokens["palette"]["members"]:
        if m["key"] == key:
            return m["name"]
    return key or ""


def ref_label(role: dict) -> str:
    if role.get("adjusted"):
        return f"adjusted from {role['adjusted']['from_ref'].replace(':', '-')}"
    if role.get("alias_of"):
        return f"same as {role['alias_of']}"
    ref = role["ref"]
    if ref == "transparent":
        return "transparent"
    if ref.startswith("literal:"):
        return "white" if ref.endswith("#ffffff") else "low-chroma hover"
    if ref == "ground:seed":
        return "palette ground"
    return ref.replace(":", "-")


# --------------------------------------------------------------------------- frontmatter + region content


def frontmatter_keys(tokens: dict) -> list[str]:
    keys = ["bg", "bg-subtle", "surface", "border", "border-strong", "text", "text-muted", "accent", "accent-hover",
            "on-accent", "accent-text", "accent-subtle", "focus", "action", "action-hover", "on-action", "action-border"]
    keys += [k for k in tokens["roles"]["light"] if re.fullmatch(r"(brand|voice-\d+|success|warning|danger|info)", k)]
    roles = tokens["roles"]["light"]
    return [k for k in keys if k in roles and not roles[k].get("transparent")]


def frontmatter_entries(tokens: dict, prefix: str) -> list[tuple[str, str]]:
    return [(prefix + k, hx(role_hex(tokens, "light", k))) for k in frontmatter_keys(tokens)]


def block_primary(tokens: dict) -> list[str]:
    a = member_name(tokens, tokens["assignment"]["accent"])
    light = tokens["roles"]["light"]
    style = (tokens.get("policy") or {}).get("action_style", "solid")
    on = light["on-action"]
    on_name = "white" if on["ref"].startswith("literal:") else "the near-black neutral" if on["ref"].startswith("neutral:9") else "the body or accent text colour"
    if style == "solid":
        main = entry(f"{a} Accent", role_hex(tokens, "light", "accent"), f"the one solid action colour (light mode); text on it is {on_name}.")
    else:
        main = entry(f"{a} Accent", role_hex(tokens, "light", "accent"), "the accent colour: action borders, marks and links (never a text ground).")
    out = [main,
           entry(f"{a} Accent Text", role_hex(tokens, "light", "accent-text"), "links and accent-coloured text on the page."),
           entry(f"{a} Accent Tint", role_hex(tokens, "light", "accent-subtle"), "selected and hover backgrounds, quiet badges.")]
    if style == "tinted":
        out.append(entry(f"{a} Action Tint", role_hex(tokens, "light", "action"),
                         f"action fill (tinted style): a pale tint with an accent border ({hx(role_hex(tokens, 'light', 'action-border'))}); "
                         f"the label is {on_name}; no saturated colour sits behind text."))
    elif style == "outline":
        out.append(f"- **{a} Action Outline**: transparent fill with an accent border ({hx(role_hex(tokens, 'light', 'action-border'))}) and an accent-text label "
                   f"({hx(role_hex(tokens, 'light', 'on-action'))}); hover fill {hx(role_hex(tokens, 'light', 'action-hover'))}.")
    return out


def block_secondary(tokens: dict) -> list[str]:
    out = []
    asg = tokens["assignment"]
    if asg.get("brand") and has_role(tokens, "brand"):
        out.append(entry(f"{member_name(tokens, asg['brand'])} Brand", role_hex(tokens, "light", "brand"),
                         "the committed colour that carries large surfaces (hero, sections)."))
    for i, key in enumerate(asg["voices"][:2], 1):
        if has_role(tokens, f"voice-{i}"):
            out.append(entry(f"{member_name(tokens, key)} Voice", role_hex(tokens, "light", f"voice-{i}"),
                             f"voice colour {i}: the exact plate colour as a region fill (bands, sections, tags); chart marks and icons use voice-{i}-mark; never the call to action."))
    return out


def block_tertiary(tokens: dict) -> list[str]:
    out = []
    asg = tokens["assignment"]
    for i, key in enumerate(asg["voices"][2:], 3):
        if has_role(tokens, f"voice-{i}"):
            out.append(entry(f"{member_name(tokens, key)} Voice", role_hex(tokens, "light", f"voice-{i}"), f"voice colour {i}."))
    for s in ("success", "warning", "danger", "info"):
        if has_role(tokens, s):
            src = asg["status"][s]
            if src["source"] == "palette":
                where = f"taken from the palette ({member_name(tokens, src['member'])})"
            elif src["source"] == "default-reseeded":
                where = "from the default seed, re-seeded away from the accent hue (pair it with an icon and a label)"
            else:
                where = "from the default seeds (no palette colour fits this meaning)"
            out.append(entry(s.capitalize(), role_hex(tokens, "light", s), f"status colour, {where}."))
    return out


def block_neutral(tokens: dict) -> list[str]:
    n = member_name(tokens, tokens["assignment"]["neutral_from"])
    rows = [("Page", "bg", "the page background"), ("Surface", "surface", "cards and panels"),
            ("Subtle Surface", "bg-subtle", "wells, table stripes"), ("Divider", "border", "dividers and quiet borders"),
            ("Control Border", "border-strong", "borders that carry meaning (inputs, 3:1 against the page)"),
            ("Text", "text", "body text"), ("Muted Text", "text-muted", "secondary text")]
    out = [f"The neutral ramp is tinted with {n} (chroma capped at 0.03), never plain grey.", ""]
    out += [entry(name, role_hex(tokens, "light", tok), desc) for name, tok, desc in rows]
    return out


def named_rules(tokens: dict) -> list[str]:
    st, mode = tokens["strategy"]["name"], tokens["strategy"]["mode"]
    p = tokens["proportions"]
    rules = [f"- **The {st} Rule.** Colour strategy {st}, mode {mode}. Do not mix strategies on one surface."]
    if "secondary_pct" in p:  # Full palette states the two bands itself
        palette_part = (f"secondary {p['secondary_pct'][0]}-{p['secondary_pct'][1]}%, "
                        f"tertiary {p['tertiary_pct'][0]}-{p['tertiary_pct'][1]}%")
    else:
        palette_part = f"{p['palette_means']} {p['palette_pct'][0]}-{p['palette_pct'][1]}%"
    parts = [f"ground and neutrals {p['neutrals_pct'][0]}-{p['neutrals_pct'][1]}%", palette_part,
             f"accent {p['accent_pct'][0]}-{p['accent_pct'][1]}%"]
    rules.append(f"- **The Proportion Rule.** Screen share: {'; '.join(parts)}. {bt.PROPORTION_LABEL}")
    for m in p.get("modifiers", []):
        rules.append(f"- **The Accent Restraint Rule.** {m[0].upper() + m[1:]}.")
    if "ground_shares_pct" in p:
        shares = ", ".join(f"{member_name(tokens, k)} {v}%" for k, v in p["ground_shares_pct"].items())
        rules.append(f"- **The Measured Ground Rule.** Ground shares follow the painting's measured coverage: {shares}; accents at most {p['accents_total_max_pct']}% together.")
    pol = tokens.get("policy") or {}
    tm = f"{pol.get('text_min', 4.5):g}"
    lm = f"{pol.get('large_text_min', 3.0):g}"
    rules.append(f"- **The Contrast Floor Rule.** Body and label text {tm}:1, large text {lm}:1, non-text UI (focus ring, control borders, icons, chart marks) 3:1, "
                 "measured with WCAG 2 for every pair in both modes; APCA Lc is reported against 75 body, 60 labels, 45 large text and fine detail, 30 solid UI. "
                 "Region fills (voice and brand colours) keep the exact plate colour: only text placed on them is gated, and each has a -mark step for chart marks and icons.")
    style = pol.get("action_style", "solid")
    forced = pol.get("on_accent", "auto")
    wording = {
        "solid": "Primary actions are a solid accent fill with a measured label.",
        "tinted": "Primary actions are a pale accent tint with an accent border and the body text colour as label; no saturated colour sits behind text.",
        "outline": "Primary actions are transparent with an accent border and an accent-text label; no saturated colour sits behind text.",
    }[style]
    if forced != "auto" and style == "solid":
        wording += f" The label is forced {forced}; the fill moves to the nearest step that passes."
    rules.append(f"- **The Action Style Rule.** {wording} Use --color-action, --color-action-hover, --color-on-action and --color-action-border.")
    rules.append("- **The Composed Dark Rule.** Dark mode is a separately composed ramp (lower chroma, wider dark-end steps), never the light ramp inverted; every pair is re-measured.")
    return rules


def token_tables(tokens: dict) -> list[str]:
    out = ["| Token | Light | Dark | Light source | Dark source |", "|---|---|---|---|---|"]
    for tok, lrole in tokens["roles"]["light"].items():
        drole = tokens["roles"]["dark"][tok]
        out.append(f"| `--color-{tok}` | {hx(lrole['hex'])} | {hx(drole['hex'])} | {ref_label(lrole)} | {ref_label(drole)} |")
    return out


def contrast_block(tokens: dict) -> list[str]:
    c = tokens["contrast"]
    s = c["summary"]
    gated = [p for p in c["pairs"] if p["gate"]]
    worst = min(gated, key=lambda p: p["wcag"] / p["wcag_min"])
    out = [f"{s['pairs']} pairs measured in light and dark; {len(gated)} are gated and "
           f"{'all pass' if c['gate_pass'] else 'NOT ALL PASS'} (tightest: {worst['fg']} on {worst['bg']}, {worst['mode']}, {worst['wcag']}:1 against {worst['wcag_min']}:1). "
           f"APCA Lc is below its target on {s['apca_below_target']} pairs; WCAG 2 is the gate.", "",
           "| Pair | Mode | WCAG 2 | APCA Lc |", "|---|---|---|---|"]
    keep = [("text", "bg"), ("text", "surface"), ("text-muted", "bg"), ("text-muted", "surface"), ("accent-text", "bg"),
            ("on-accent", "accent"), ("accent", "bg"), ("focus", "bg"), ("border-strong", "bg")]
    for fg, bg in keep:
        for mode in ("light", "dark"):
            for p in c["pairs"]:
                if p["fg"] == fg and p["bg"] == bg and p["mode"] == mode:
                    out.append(f"| `{fg}` on `{bg}` | {mode} | {p['wcag']}:1 | {abs(p['apca']):.0f} |")
    flags = [f for f in c["flags"] if f["type"] in ("vibrating", "vanishing", "cvd", "state_sibling")]
    if flags:
        kinds = sorted({f["type"] for f in flags})
        out += ["", f"Flags to design around (see design/palette.json): {', '.join(kinds)} ({len(flags)} findings). "
                    "Do not rely on colour alone to tell the accent from status colours."]
    return out


def adjustments_block(tokens: dict) -> list[str]:
    adj = tokens.get("adjustments") or []
    if not adj:
        return ["No role needed adjusting: every gated pair passed with the ramp values as generated."]
    out = ["Lightness-only changes made to pass the gate (hue kept):", ""]
    for a in adj:
        moved = f" (moved step: {a['moved_step']})" if a.get("moved_step") else ""
        out.append(f"- `{a['role']}` ({a['mode']}): {hx(a['before_hex'])} to {hx(a['after_hex'])}, L {a['before_L']} to {a['after_L']}, "
                   f"ratio {a['before_ratio']}:1 to {a['after_ratio']}:1 against `{a['against']}`; reason: {a['reason']}{moved}.")
    return out


def neighbour_map(tokens: dict, css_path: str) -> list[str]:
    L = lambda t: hx(role_hex(tokens, "light", t))  # noqa: E731
    out = [f"- Taste: `--bg` {L('bg')}, `--surface` {L('bg-subtle')}, `--ink` {L('text')}, `--muted` {L('text-muted')}, "
           f"`--accent` {L('accent')} (the one accent), `--accent-ink` {L('on-accent')}. Run Taste with `--keep palette`; "
           "pass `--allow palette-purple` if the palette has violet or indigo, and expect its inspector to question a cream plus terracotta ground. "
           "With Taste loaded the stricter numbers win: accent < 5%, ground <= 90%, separate surfaces by lightness, not lines."]
    out.append(f"- UI/UX Pro Max: `--color-primary` and `--color-accent` {L('accent')}, `--color-background` {L('bg')}, `--color-foreground` {L('text')}, "
               f"`--color-card` {L('surface')}, `--color-muted-foreground` {L('text-muted')}, `--color-border` {L('border')}, "
               f"`--color-destructive` {L('danger')}, `--color-ring` {L('focus')}. Keep its pattern and type output, take colours from `{css_path}`; never edit its MASTER.md without consent.")
    out.append("- interface-design: `--foreground`, `--secondary`, `--muted`, `--faint`, `--accent` resolve to the semantic tokens in the alias block of the CSS file.")
    pal = [f"{member_name(tokens, tokens['assignment']['accent'])} {L('accent')} (accent)"]
    for i, key in enumerate(tokens["assignment"]["voices"][:3], 1):
        pal.append(f"{member_name(tokens, key)} {L(f'voice-{i}')} (voice)")
    pal += [f"{member_name(tokens, tokens['assignment']['neutral_from'])}-tinted neutrals {L('bg')} to {L('text')}"]
    out.append("- Theme Factory custom theme, colour bullets: " + "; ".join(pal) + ".")
    return out


def section(heading: str | None, lines: list[str]) -> str:
    if not lines:
        return ""
    return ("" if heading is None else heading + "\n\n") + "\n".join(lines)


def usage_notes_block(notes_text: str | None) -> str:
    """Free-form usage guidance supplied with --notes, rendered inside our region. Headings are flattened to bold lines so the
    note cannot add document sections of its own."""
    if not notes_text or not notes_text.strip():
        return ""
    lines = []
    for ln in notes_text.replace("\r\n", "\n").strip().split("\n"):
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", ln)
        lines.append(f"**{m.group(1)}**" if m else ln.rstrip())
    return "#### Usage notes\n\n" + "\n".join(lines)


def render_region(tokens: dict, css_path: str, json_path: str, template_path: Path, usage_notes: str | None = None) -> list[str]:
    tpl = template_path.read_text(encoding="utf-8")
    m = re.search(r"<!-- template:begin -->\n(.*?)<!-- template:end -->", tpl.replace("\r\n", "\n"), re.S)
    if not m:
        raise HandoffError(f"template markers missing in {template_path}")
    body = m.group(1)
    p = tokens["palette"]
    names = ", ".join(mm["name"] for mm in p["members"])
    character = (f"{p['title']}: {len(p['members'])} colours ({names}), composed as a {tokens['strategy']['name']} palette for "
                 f"{'an' if tokens['strategy']['mode'][0] in 'AEIOU' else 'a'} {tokens['strategy']['mode']} surface, with a separately composed dark mode.")
    if p["source_type"] == "kasane":
        prov = f"Provenance: {p['label']}. Credit: {p['credit']}"
    else:
        prov = f"Provenance: {p['label']}. Credit: {p['credit']}. Licence: {p['licence']}."
    if p.get("kasane_note"):
        prov += f" Kasane note: {p['kasane_note']} (the shared colour is the page, so the edge accent is the layer that separates best from it)."
    if p.get("drift_note"):
        prov += f" Note: {p['drift_note']}"
    if p["source_type"] == "kasane":
        prov += " Hex values are interpretations of plant-dyed silk colours."
    subs = {
        "CHARACTER": character,
        "PROVENANCE": prov,
        "PRIMARY_SECTION": section("### Primary", block_primary(tokens)),
        "SECONDARY_SECTION": section("### Secondary", block_secondary(tokens)),
        "TERTIARY_SECTION": section("### Tertiary", block_tertiary(tokens)),
        "NEUTRAL_SECTION": section("### Neutral", block_neutral(tokens)),
        "NAMED_RULES_SECTION": section("### Named Rules", named_rules(tokens)),
        "TOKEN_TABLES": section("#### Token tables", token_tables(tokens)),
        "CONTRAST": section("#### Measured contrast", contrast_block(tokens)),
        "ADJUSTMENTS": section("#### Adjustments", adjustments_block(tokens)),
        "KEEP_IN_SYNC": section("#### Keep in sync", [
            "Do not change a colour here without re-validating: edit nothing between the acp markers by hand. Change the palette or strategy, "
            "then re-run `scripts/handoff.py` (idempotent). If Impeccable's document step asks refresh, overwrite or merge, choose merge and re-run it."]),
        "POINTERS": section("#### Hand-off files", [f"- Tokens: `{css_path}` (primitives, then semantic `--color-*`, light, dark and `[data-theme=dark]`).",
                                                   f"- Source of truth: `{json_path}` (provenance, ramps, contrast, adjustments)."]),
        "NEIGHBOUR_MAP": section("#### Neighbour map", neighbour_map(tokens, css_path)),
        "USAGE_NOTES": usage_notes_block(usage_notes),
    }
    text = body
    for k, v in subs.items():
        text = text.replace("{{" + k + "}}", v)
    text = re.sub(r"\n{3,}", "\n\n", text).strip("\n")
    return text.split("\n")


# --------------------------------------------------------------------------- DESIGN.md editing


def find_pair(lines: list[str], begin_re, end_re, what: str):
    b = [i for i, ln in enumerate(lines) if begin_re.match(ln.rstrip("\r"))]
    e = [i for i, ln in enumerate(lines) if end_re.match(ln.rstrip("\r"))]
    if not b and not e:
        return None
    if len(b) != 1 or len(e) != 1 or e[0] < b[0]:
        raise HandoffError(f"DESIGN.md has damaged or duplicated {what} markers (begin at {b}, end at {e}); fix them by hand, nothing was written")
    return b[0], e[0]


def find_frontmatter(lines: list[str]):
    i = 0
    while i < len(lines):
        raw = lines[i].lstrip("\ufeff").rstrip("\r")
        if raw.strip() == "" or re.match(r"^\s*<!--.*-->\s*$", raw):
            i += 1
            continue
        break
    if i < len(lines) and lines[i].lstrip("\ufeff").rstrip("\r") == "---":
        for j in range(i + 1, len(lines)):
            if lines[j].rstrip("\r") == "---":
                return i, j
    return None


def cr(crlf: bool) -> str:
    return "\r" if crlf else ""


def build_fm_block(entries: list[tuple[str, str]], indent: str, crlf: bool) -> list[str]:
    c = cr(crlf)
    return [indent + FM_BEGIN_TEXT + c] + [f'{indent}{k}: "{v}"{c}' for k, v in entries] + [indent + FM_END_TEXT + c]


def build_body_block(content: list[str], crlf: bool) -> list[str]:
    c = cr(crlf)
    return [BODY_BEGIN + c] + [ln + c for ln in content] + [BODY_END + c]


def existing_color_keys(lines: list[str]) -> set[str]:
    keys = set()
    for ln in lines:
        m = re.match(r"^[ \t]+(\"[^\"]+\"|'[^']+'|[A-Za-z0-9_.\-]+)\s*:", ln.rstrip("\r"))
        if m:
            keys.add(m.group(1).strip("\"'"))
    return keys


def apply_design_md(old: str, entries: list[tuple[str, str]], region: list[str], name: str, description: str):
    """-> (new_text, mode) where mode is 'markers' (replace only), 'inserted' (markers were missing) or 'unchanged'."""
    crlf = "\r\n" in old
    eol = "\r\n" if crlf else "\n"
    lines = old.split("\n")
    inserted = False
    # ---- frontmatter
    fm = find_frontmatter(lines)
    fm_pair = find_pair(lines, RE_FM_BEGIN, RE_FM_END, "frontmatter")
    if fm_pair:
        b, e = fm_pair
        indent = re.match(r"^[ \t]*", lines[b]).group(0)
        inner = [f'{indent}{k}: "{v}"' + cr(crlf) for k, v in entries]
        lines[b + 1:e] = inner
    else:
        inserted = True
        if fm:
            s, t = fm
            colors_idx = next((i for i in range(s + 1, t) if re.match(r"^colors:\s*(#.*)?$", lines[i].rstrip("\r"))), None)
            if colors_idx is not None:
                end_map = next((i for i in range(colors_idx + 1, t) if re.match(r"^\S", lines[i].rstrip("\r")) and lines[i].strip() != ""), t)
                keys = existing_color_keys(lines[colors_idx + 1:end_map])
                clash = sorted(keys & {k for k, _ in entries})
                if clash:
                    raise HandoffError("the existing colors: map already defines " + ", ".join(clash) +
                                       "; re-run with --key-prefix acp- (or another prefix). Nothing was written")
                lines[colors_idx + 1:colors_idx + 1] = build_fm_block(entries, "  ", crlf)
            elif any(re.match(r"^colors:", ln) for ln in lines[s + 1:t]):
                pass  # inline / flow-style colors: leave the frontmatter alone; the body region still lands
            else:
                lines[t:t] = ["colors:" + cr(crlf)] + build_fm_block(entries, "  ", crlf)
        else:
            head = ["---" + cr(crlf), f"name: {json.dumps(name, ensure_ascii=False)}" + cr(crlf),
                    f"description: {json.dumps(description, ensure_ascii=False)}" + cr(crlf), "colors:" + cr(crlf)]
            head += build_fm_block(entries, "  ", crlf) + ["---" + cr(crlf)]
            k = 0
            while k < len(lines) and re.match(r"^\s*<!--.*-->\s*$", lines[k].lstrip("\ufeff").rstrip("\r")):
                k += 1
            lines[k:k] = head
    # ---- body
    body_pair = find_pair(lines, RE_BODY_BEGIN, RE_BODY_END, "colors")
    block = build_body_block(region, crlf)
    if body_pair:
        b, e = body_pair
        lines[b:e + 1] = block
    else:
        inserted = True
        h_idx = next((i for i, ln in enumerate(lines) if re.match(r"^##\s+Colors\s*$", ln.rstrip("\r"))), None)
        blank = cr(crlf)
        if h_idx is not None:
            end = next((i for i in range(h_idx + 1, len(lines)) if re.match(r"^## ", lines[i])), len(lines))
            p = end
            while p - 1 > h_idx and lines[p - 1].strip() == "":
                p -= 1
            lines[p:p] = [blank] + block
        else:
            fm2 = find_frontmatter(lines)
            start = (fm2[1] + 1) if fm2 else 0
            pos = len(lines)
            for i in range(start, len(lines)):
                m = re.match(r"^##\s+(.*?)\s*$", lines[i].rstrip("\r"))
                if m and not lines[i].startswith("###"):
                    low = m.group(1).lower()
                    idx = next((j for j, c in enumerate(CANONICAL) if low.startswith(c)), None)
                    if idx is not None and idx > CANONICAL.index("colors"):
                        pos = i
                        break
            new = ["## Colors" + cr(crlf)] + block
            if pos == len(lines):
                if lines[-1] != "":
                    lines.append("")  # make the file end with a newline
                at = len(lines) - 1
                prefix = [] if (at == 0 or lines[at - 1].strip() == "") else [blank]
                lines[at:at] = prefix + new
            else:
                prefix = [] if (pos == start or lines[pos - 1].strip() == "") else [blank]
                lines[pos:pos] = prefix + new + [blank]
    new_text = "\n".join(lines)
    if new_text == old:
        return new_text, "unchanged"
    return new_text, "inserted" if inserted else "markers"


def existing_palette_found(old: str) -> bool:
    """True when the file already holds a palette of its own: colour keys in the frontmatter colors: map, or prose under
    ## Colors, outside our markers."""
    lines = old.split("\n")
    fm = find_frontmatter(lines)
    if fm:
        inner = lines[fm[0] + 1:fm[1]]
        start = next((i for i, ln in enumerate(inner) if re.match(r"^colors:\s*(#.*)?$", ln.rstrip("\r"))), None)
        if start is not None:
            end = next((i for i in range(start + 1, len(inner)) if re.match(r"^\S", inner[i].rstrip("\r")) and inner[i].strip()), len(inner))
            block = inner[start + 1:end]
            mine = find_pair(block, RE_FM_BEGIN, RE_FM_END, "frontmatter")
            if mine:
                block = block[:mine[0]] + block[mine[1] + 1:]
            if existing_color_keys(block):
                return True
    h = next((i for i, ln in enumerate(lines) if re.match(r"^##\s+Colors\s*$", ln.rstrip("\r"))), None)
    if h is not None:
        end = next((i for i in range(h + 1, len(lines)) if re.match(r"^## ", lines[i])), len(lines))
        sec = lines[h + 1:end]
        mine = find_pair(sec, RE_BODY_BEGIN, RE_BODY_END, "colors")
        if mine:
            sec = sec[:mine[0]] + sec[mine[1] + 1:]
        if any(ln.strip() for ln in sec):
            return True
    return False


def seed_design_md(entries, region, name, description) -> str:
    # the frontmatter must open on line 1 (parsers look for it there); our seed comment is the first line of the body
    out = ["---", f"name: {json.dumps(name, ensure_ascii=False)}", f"description: {json.dumps(description, ensure_ascii=False)}", "colors:"]
    out += build_fm_block(entries, "  ", False)
    out += ["---", SEED_COMMENT, "", "## Colors"] + build_body_block(region, False) + [""]
    return "\n".join(out)


# --------------------------------------------------------------------------- CSS


def css_var(role: dict, mode: str) -> tuple[str, str]:
    """-> (value, trailing comment)"""
    if role.get("adjusted") and not role.get("alias_of"):
        return role["hex"], f"/* adjusted from {role['adjusted']['from_ref'].replace(':', '-')} {role['adjusted']['from_hex']} */"
    if role.get("alias_of"):
        return f"var(--color-{role['alias_of']})", ""
    ref = role["ref"]
    if ref == "transparent":
        return "transparent", ""
    if ref.startswith("literal:"):
        return ref.split(":", 1)[1], ""
    if ref == "ground:seed":
        return "var(--ground-seed)", ""
    name, step = ref.split(":")
    return (f"var(--{name}-dark-{step})" if mode == "dark" else f"var(--{name}-{step})"), ""


def semantic_decls(tokens: dict, mode: str, indent: str) -> list[str]:
    out = []
    for tok, role in tokens["roles"][mode].items():
        val, note = css_var(role, mode)
        out.append(f"{indent}--color-{tok}: {val};" + (f" {note}" if note else ""))
    return out


def alias_decls(tokens: dict) -> list[str]:
    roles = tokens["roles"]["light"]
    brand = "brand" in roles
    primary = "brand" if brand else "accent"
    secondary = "voice-1" if "voice-1" in roles else "accent-hover"
    o = ["  /* Taste */",
         "  --bg: var(--color-bg);", "  --surface: var(--color-bg-subtle); /* a separated step: Taste wants surfaces told apart by tone, not lines */",
         "  --ink: var(--color-text);",
         "  --muted: var(--color-text-muted); /* also interface-design */", "  --accent: var(--color-accent); /* also interface-design */",
         "  --accent-ink: var(--color-on-accent);"]
    for i in range(1, 12):
        if f"voice-{i}" in roles:
            o += [f"  --field-{i}: var(--color-voice-{i});", f"  --field-{i}-ink: var(--color-on-voice-{i});"]
    o += ["  /* UI/UX Pro Max (--color-accent, --color-on-accent and --color-border are already defined above) */",
          f"  --color-primary: var(--color-{primary});", f"  --color-on-primary: var(--color-on-{primary});",
          f"  --color-secondary: var(--color-{secondary});",
          f"  --color-on-secondary: var(--color-on-{secondary if secondary != 'accent-hover' else 'accent'});",
          "  --color-background: var(--color-bg);", "  --color-foreground: var(--color-text);", "  --color-card: var(--color-surface);",
          "  --color-card-foreground: var(--color-text);", "  --color-muted: var(--color-bg-subtle);",
          "  --color-muted-foreground: var(--color-text-muted);", "  --color-destructive: var(--color-danger);",
          "  --color-on-destructive: var(--color-on-danger);", "  --color-ring: var(--color-focus);",
          "  /* interface-design (two text tiers here: --secondary and --muted both map to the muted text colour) */",
          "  --foreground: var(--color-text);", "  --secondary: var(--color-text-muted);", "  --faint: var(--color-border-subtle);"]
    return o


def render_css(tokens: dict) -> str:
    p = tokens["palette"]
    L = []
    L.append("/* acp:tokens v1 - generated by artistic-color-palettes (scripts/handoff.py). Do not edit by hand; re-run the script. */")
    credit = p["credit"]
    if p["source_type"] in ("wada_plate", "editorial", "painting", "kasane", "custom"):
        L.append(f"/* {credit} */")
    L.append(f"/* {p['label']} */")
    if p.get("drift_note"):
        L.append(f"/* {p['drift_note']} */")
    if p["source_type"] == "kasane":
        L.append(f"/* Strategy {tokens['strategy']['name']}, mode {tokens['strategy']['mode']}. */")
    else:
        L.append(f"/* Strategy {tokens['strategy']['name']}, mode {tokens['strategy']['mode']}. Licence: {p['licence']}. */")
    L.append("")
    L.append(":root {")
    L.append("  /* ---- primitives: light ramps (OKLCH-built; steps 50-950) ---- */")
    for rname, ramp in tokens["ramps"].items():
        if "light" not in ramp:
            continue
        L.append(f"  --{rname}-seed: {ramp['seed']};")
        for s in bt.STEPS:
            note = " /* pinned seed */" if ramp["pinned"]["light"] == s else ""
            L.append(f"  --{rname}-{s}: {ramp['light'][s]};{note}")
    if "ground" in tokens["ramps"]:
        L.append(f"  --ground-seed: {tokens['ramps']['ground']['seed']};")
    L.append("")
    L.append("  /* ---- the palette's own colours, exactly as sampled (always available as primitives) ---- */")
    for m in tokens["palette"]["members"]:
        L.append(f"  --palette-{m['key']}: {m['hex']};")
    L.append("")
    L.append("  /* ---- primitives: dark ramps (composed separately, not the light ramps reversed) ---- */")
    for rname, ramp in tokens["ramps"].items():
        if "dark" not in ramp:
            continue
        for s in bt.STEPS:
            note = " /* pinned seed */" if ramp["pinned"]["dark"] == s else ""
            L.append(f"  --{rname}-dark-{s}: {ramp['dark'][s]};{note}")
    L.append("}")
    L.append("")
    L.append("/* ---- semantic tier: light ---- */")
    L.append(":root,")
    L.append('[data-theme="light"] {')
    L.append("  color-scheme: light;")
    L += semantic_decls(tokens, "light", "  ")
    L.append("}")
    L.append("")
    L.append("/* ---- semantic tier: dark (follows the system unless data-theme=light) ---- */")
    L.append("@media (prefers-color-scheme: dark) {")
    L.append('  :root:not([data-theme="light"]) {')
    L.append("    color-scheme: dark;")
    L += semantic_decls(tokens, "dark", "    ")
    L.append("  }")
    L.append("}")
    L.append("")
    L.append('[data-theme="dark"] {')
    L.append("  color-scheme: dark;")
    L += semantic_decls(tokens, "dark", "  ")
    L.append("}")
    L.append("")
    L.append("/* ---- aliases: neighbour skills' token names resolve to the semantic tier (no second palette) ---- */")
    L.append(":root,")
    L.append("[data-theme] {")
    L += alias_decls(tokens)
    L.append("}")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- JSON


def render_palette_json(tokens: dict, claude_md, paths: dict, usage_notes: str | None = None) -> str:
    out = {
        "schema": "acp-palette/1",
        "name": tokens["name"],
        "palette": tokens["palette"],
        "strategy": tokens["strategy"],
        "policy": tokens.get("policy"),
        "inputs": tokens["inputs"],
        "assignment": tokens["assignment"],
        "ramps": tokens["ramps"],
        "roles": tokens["roles"],
        "proportions": tokens["proportions"],
        "contrast": tokens["contrast"],
        "adjustments": tokens["adjustments"],
        "warnings": tokens["warnings"],
        "notes": tokens["notes"],
        "handoff": {
            "version": HANDOFF_VERSION,
            "design_md": paths["design_md"], "tokens_css": paths["tokens_css"], "palette_json": paths["palette_json"],
            "claude_md": claude_md,
            "usage_notes": usage_notes,
            "markers": {"frontmatter": [FM_BEGIN_TEXT, FM_END_TEXT], "body": [BODY_BEGIN, BODY_END], "pointer": [PTR_BEGIN, PTR_END]},
        },
    }
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- CLAUDE.md / AGENTS.md pointer


def pointer_lines(crlf: bool) -> list[str]:
    c = cr(crlf)
    return [PTR_BEGIN + c, PTR_TEXT + c, PTR_END + c]


def update_pointer_file(path: Path, enable: bool) -> str:
    if not path.exists():
        if not enable:
            return "absent"
        return write_bytes_if_changed(path, "\n".join(pointer_lines(False)) + "\n")
    old = read_text(path)
    crlf = "\r\n" in old
    eol = "\r\n" if crlf else "\n"
    lines = old.split("\n")
    pair = find_pair(lines, RE_PTR_BEGIN, RE_PTR_END, f"{path.name} pointer")
    if enable:
        if pair:
            lines[pair[0]:pair[1] + 1] = pointer_lines(crlf)
            new = "\n".join(lines)
        else:
            base = old if (old == "" or old.endswith("\n")) else old + eol
            sep = eol if base.strip() != "" else ""
            new = base + sep + eol.join([PTR_BEGIN, PTR_TEXT, PTR_END]) + eol
        return write_bytes_if_changed(path, new)
    if not pair:
        return "no pointer present"
    b0, e0 = pair
    if b0 > 0 and lines[b0 - 1].strip() == "":
        b0 -= 1
    del lines[b0:e0 + 1]
    new = "\n".join(lines)
    if new.strip() == "":
        path.unlink()
        return "removed (the file held only the pointer)"
    return write_bytes_if_changed(path, new)


# --------------------------------------------------------------------------- main


def _norm(p: Path) -> str:
    return os.path.normcase(str(p.resolve()))


def _within(child: str, parent: str) -> bool:
    return child == parent or child.startswith(parent.rstrip("\\/") + os.sep)


def protected_paths() -> list[Path]:
    home = Path.home().resolve()
    return [home / ".claude", home / ".codex", home / ".agents"]


def path_inside_protected(path: Path) -> bool:
    c = _norm(path)
    return any(_within(c, _norm(p)) for p in protected_paths())


def protected_dir_problem(project_dir: Path) -> str | None:
    """Why this project directory must not receive hand-off files, or None. Refused: the home folder, any folder above it,
    and ~/.claude, ~/.codex, ~/.agents (or anything inside them): those hold the user's global agent settings."""
    proj = _norm(project_dir)
    home = _norm(Path.home())
    if _within(home, proj):
        return ("--project-dir is the home folder or a folder above it; this skill never writes project files there "
                "(global agent settings live in the home folder).")
    if path_inside_protected(project_dir):
        return "--project-dir is inside ~/.claude, ~/.codex or ~/.agents (the user's global agent folders)."
    return None


def load_or_build(args) -> dict:
    if args.tokens:
        return bt.load_tokens(args.tokens)
    roles = bt.parse_roles_arg(args.roles)
    if args.accent:
        roles["accent"] = args.accent
    if args.neutral_from:
        roles["neutral"] = args.neutral_from
    return bt.build_tokens(args.palette, args.hex, args.strategy, args.mode, roles, args.pin, args.tint, args.name, provenance_label=args.provenance,
                           on_accent=args.on_accent, action_style=args.action_style, text_min=args.text_min)


def err_line(exc) -> str:
    """'error: <message>' without doubling a prefix the message already carries."""
    msg = str(exc)
    while msg.lower().startswith("error: "):
        msg = msg[7:]
    return f"error: {msg}"


def main(argv=None) -> int:
    cl.configure_stdio()
    ap = argparse.ArgumentParser(
        prog="handoff.py",
        description="Write DESIGN.md (marker regions only), design/palette.json, design/tokens.css and optionally the CLAUDE.md/AGENTS.md "
                    "pointer from a validated palette. Idempotent.",
        epilog="Exit codes: 0 done | 1 contrast gate fails | 2 bad input, broken markers or a data-source --provenance | 3 DESIGN.md insertion needs --yes | "
               "4 --claude-md yes without --user-confirmed, or --project-dir at/above the home folder or inside ~/.claude, ~/.codex, ~/.agents.",
    )
    src = ap.add_argument_group("palette source (one of)")
    src.add_argument("--tokens", help="tokens JSON from build_tokens.py / validate.py ('-' = stdin)")
    src.add_argument("--palette", help="palette id; build_tokens + validate --fix are run for you")
    src.add_argument("--hex", help="explicit hex list; build_tokens + validate --fix are run for you")
    bg = ap.add_argument_group("build options (with --palette / --hex)")
    bg.add_argument("--strategy", default="restrained")
    bg.add_argument("--mode", default="operate")
    bg.add_argument("--roles")
    bg.add_argument("--accent")
    bg.add_argument("--neutral-from", dest="neutral_from")
    bg.add_argument("--pin", default="all")
    bg.add_argument("--on-accent", dest="on_accent", choices=("auto", "light", "dark"), default="auto",
                    help="label colour on the accent fill: auto | light (e.g. 'white button text'; the fill moves to the nearest darker passing step) | dark")
    bg.add_argument("--action-style", dest="action_style", choices=("solid", "tinted", "outline"), default="solid",
                    help="solid accent fill (default) | tinted (pale tint + accent border + text label) | outline (transparent, accent border, accent-text label)")
    bg.add_argument("--text-min", dest="text_min", type=float, default=4.5,
                    help="WCAG ratio floor for body and label text (default 4.5; large-text floor rises to text-min/1.5 above 4.5)")
    bg.add_argument("--provenance", help="provenance label for --hex input (default: Original composition (colours supplied by the user)); labels that name a data "
                         "source (Wada plate, editorial palette, Sampled from, Kasane, colorcombinations.org) are refused with exit 2")
    bg.add_argument("--tint", type=float, default=1.0)
    ap.add_argument("--name", help="design name for a new DESIGN.md (default: palette title)")
    ap.add_argument("--project-dir", type=Path, default=Path.cwd(), help="project root (default: current directory)")
    ap.add_argument("--design-dir", default="design", help="folder for palette.json and tokens.css, relative to the project (default: design)")
    ap.add_argument("--claude-md", choices=("yes", "no", "declined"), help="yes: write the pointer into CLAUDE.md and AGENTS.md (needs --user-confirmed); "
                                                                           "no: remove it; declined: record that the user said no (writes nothing). Omit to leave as is.")
    ap.add_argument("--user-confirmed", action="store_true", help="records that the user explicitly said yes to the CLAUDE.md pointer in this conversation; "
                                                                  "required for --claude-md yes (refused with exit 4 otherwise), meaningless for no / declined")
    ap.add_argument("--notes", type=Path, help="text or markdown file with usage guidance; rendered as a '#### Usage notes' block INSIDE our "
                                               "## Colors marker region and regenerated on every run (it is remembered in palette.json, so a re-run "
                                               "without --notes keeps it). Write nothing about colour outside the markers; put it here.")
    ap.add_argument("--no-notes", action="store_true", help="drop remembered usage notes")
    ap.add_argument("--key-prefix", default="", help="prefix for our frontmatter colour keys (use if the existing colors: map clashes)")
    ap.add_argument("--yes", action="store_true", help="allow inserting our markers into an existing DESIGN.md that has none")
    ap.add_argument("--dry-run", action="store_true", help="write nothing; print a summary for a new DESIGN.md, or the diff when an existing one would change")
    ap.add_argument("--diff", action="store_true", help="with --dry-run: print the full proposed DESIGN.md as a diff even when the file is new")
    ap.add_argument("--allow-failing", action="store_true", help="hand off even if the WCAG gate fails (not recommended)")
    args = ap.parse_args(argv)
    if sum(bool(x) for x in (args.tokens, args.palette, args.hex)) != 1:
        ap.error("give exactly one of --tokens, --palette or --hex")
    guard = protected_dir_problem(args.project_dir)
    if guard:
        print(err_line(f"{guard} Nothing was written."), file=sys.stderr)
        return 4
    if args.claude_md == "yes" and not args.user_confirmed:
        print("error: --claude-md yes writes into the project's CLAUDE.md and AGENTS.md, so it needs the user's explicit yes in this conversation; "
              "ask once, then re-run with --claude-md yes --user-confirmed. Nothing was written.", file=sys.stderr)
        return 4
    if args.user_confirmed and args.claude_md != "yes":
        print("note: --user-confirmed only matters with --claude-md yes; ignored.", file=sys.stderr)

    try:
        tokens = load_or_build(args)
    except SystemExit as exc:
        print(err_line(exc), file=sys.stderr)
        return 2
    if tokens["palette"].get("source_type") == "custom":
        try:
            bt.check_provenance_label(tokens["palette"].get("label"))
        except SystemExit as exc:
            print(exc.code, file=sys.stderr)
            return 2
    if tokens.get("contrast") is None:
        vd.validate_tokens(tokens, do_fix=True)
    if not tokens["contrast"]["gate_pass"] and not args.allow_failing:
        print(vd.text_report(tokens, False), file=sys.stderr)
        print("error: the WCAG gate fails, nothing was written (run validate.py --fix or use --allow-failing)", file=sys.stderr)
        return 1
    if args.name:
        tokens["name"] = args.name

    proj = args.project_dir.resolve()
    design_dir = Path(args.design_dir)
    paths = {"design_md": "DESIGN.md", "tokens_css": (design_dir / "tokens.css").as_posix(), "palette_json": (design_dir / "palette.json").as_posix()}
    skill_root = cl.skill_root()
    template = skill_root / "assets" / "palette-handoff.template.md"
    pj_prev = proj / paths["palette_json"]
    usage_notes = None
    if args.notes:
        try:
            usage_notes = args.notes.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: cannot read --notes file: {exc}", file=sys.stderr)
            return 2
    elif pj_prev.exists() and not args.no_notes:
        try:
            usage_notes = json.loads(read_text(pj_prev)).get("handoff", {}).get("usage_notes")
        except (ValueError, OSError):
            usage_notes = None
    try:
        region = render_region(tokens, paths["tokens_css"], paths["palette_json"], template, usage_notes)
        entries = frontmatter_entries(tokens, args.key_prefix)
        description = f"Palette-only seed from {tokens['palette']['label']}; Impeccable's document command will fill the other sections."
        dm_path = proj / "DESIGN.md"
        if dm_path.exists():
            old = read_text(dm_path)
            new_text, how = apply_design_md(old, entries, region, tokens["name"], description)
        else:
            old, new_text, how = "", seed_design_md(entries, region, tokens["name"], description), "created"
    except HandoffError as exc:
        print(err_line(exc), file=sys.stderr)
        return 2

    # CLAUDE.md state to record
    claude_md = "not_asked"
    pj_path = proj / paths["palette_json"]
    if pj_path.exists():
        try:
            claude_md = json.loads(read_text(pj_path)).get("handoff", {}).get("claude_md")
            claude_md = "not_asked" if claude_md is None else claude_md  # a stored no / declined / false is kept
        except (ValueError, OSError):
            claude_md = "not_asked"
    if args.claude_md == "yes":
        claude_md = True
    elif args.claude_md == "no":
        claude_md = False
    elif args.claude_md == "declined":
        claude_md = "declined"

    results: list[str] = []
    code = 0
    if args.dry_run:
        if how == "created" and not args.diff:
            print(f"DESIGN.md: would be created ({new_text.count(chr(10)) + 1} lines; add --diff to see the text)")
            print(f"  provenance: {tokens['palette']['label']}")
            print(f"  strategy / mode: {tokens['strategy']['name']}, {tokens['strategy']['mode']} | gate "
                  f"{'pass' if tokens['contrast']['gate_pass'] else 'FAIL'}")
            print("  regions: frontmatter colours between '# acp:begin tokens' / '# acp:end tokens'; "
                  "'## Colors' body between '<!-- acp:begin colors v1 -->' / '<!-- acp:end colors -->'")
        else:
            diff = list(difflib.unified_diff(old.split("\n"), new_text.split("\n"), "DESIGN.md (current)", "DESIGN.md (proposed)", lineterm=""))
            print(f"DESIGN.md: {how}" + ("" if diff else " (no changes)"))
            if diff:
                print("\n".join(diff))
        print(f"{paths['palette_json']} and {paths['tokens_css']}: would be (re)written; nothing written (--dry-run)")
        return 0

    # DESIGN.md without our markers: show the proposal and write NOTHING (companions and pointer files included) until --yes
    if how == "inserted" and not args.yes:
        diff = list(difflib.unified_diff(old.split("\n"), new_text.split("\n"), "DESIGN.md (current)", "DESIGN.md (proposed)", lineterm=""))
        print("DESIGN.md has none of our markers; proposed insertion (nothing was written):")
        print("\n".join(diff))
        if existing_palette_found(old):
            print("existing palette found: choose replace or refine (SKILL.md step 1) before --yes")
        print("Re-run with --yes to apply the insertion above; DESIGN.md, design/palette.json and design/tokens.css are written only then.")
        return 3
    # companions (wholly ours)
    results.append(f"{paths['palette_json']}: {write_bytes_if_changed(pj_path, render_palette_json(tokens, claude_md, paths, usage_notes))}")
    results.append(f"{paths['tokens_css']}: {write_bytes_if_changed(proj / paths['tokens_css'], render_css(tokens))}")
    # DESIGN.md
    if how == "inserted" and not args.yes:
        diff = list(difflib.unified_diff(old.split("\n"), new_text.split("\n"), "DESIGN.md (current)", "DESIGN.md (proposed)", lineterm=""))
        print("DESIGN.md has none of our markers; proposed insertion (nothing in DESIGN.md was written):")
        print("\n".join(diff))
        results.append("DESIGN.md: NOT written (re-run with --yes to apply the insertion above)")
        code = 3
    else:
        if how == "inserted":
            print("DESIGN.md: inserting our markers; diff:")
            print("\n".join(difflib.unified_diff(old.split("\n"), new_text.split("\n"), "DESIGN.md (current)", "DESIGN.md (proposed)", lineterm="")))
        results.append(f"DESIGN.md: {write_bytes_if_changed(dm_path, new_text) if how != 'unchanged' else 'unchanged'}")
    # pointer files
    if args.claude_md in ("yes", "no"):
        for fname in ("CLAUDE.md", "AGENTS.md"):
            if path_inside_protected(proj / fname):
                print(f"error: refusing to write {fname} inside the user's home-level agent folders.", file=sys.stderr)
                return 4
        for fname in ("CLAUDE.md", "AGENTS.md"):
            try:
                results.append(f"{fname}: {update_pointer_file(proj / fname, args.claude_md == 'yes')}")
            except HandoffError as exc:
                print(err_line(exc), file=sys.stderr)
                return 2
    elif args.claude_md == "declined":
        results.append("CLAUDE.md / AGENTS.md: untouched (recorded handoff.claude_md = declined)")
    print(f"handoff: {tokens['palette']['label']} | {tokens['strategy']['name']}, {tokens['strategy']['mode']} | gate "
          f"{'pass' if tokens['contrast']['gate_pass'] else 'FAIL'}")
    for r in results:
        print("  " + r)
    return code


if __name__ == "__main__":
    sys.exit(main())
