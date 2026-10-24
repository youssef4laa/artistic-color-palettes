"""Generate the README images and the social card from the skill's own data and scripts.

Writes to .github/assets/:
  palettes-{light,dark}.png      six real palettes with their provenance labels (and drift note)
  before-after-{light,dark}.png  one mini UI in a typical default palette and in tokens the skill built
  card.html                      source of the social preview
  social-preview.png             card.html at 1280 x 640 (upload under Settings > Social preview)
and .claude-plugin/icon.png (1024 x 1024), the plugin directory's listing icon.

The images are drawn as SVG and committed as PNG: Anthropic's plugin directory holds SVG files for
review because an SVG can carry code, and well-formed PNGs pass. Rendering needs Google Chrome or
Chromium (set CHROME to its path if it is not found).

Nothing here ships with the skill: both install channels copy only skills/artistic-color-palettes/.
Run from the repo root:  python3 .github/scripts/readme_assets.py
"""
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "artistic-color-palettes"
OUT = REPO / ".github" / "assets"
sys.path.insert(0, str(SKILL / "scripts"))
from colorlib import wcag_contrast  # noqa: E402

PALETTES = ["wada-218", "wada-288", "kasane-ume-gasane", "kasane-kaede-momiji",
            "paint-the-starry-night", "paint-the-great-wave-off-kanagawa"]
DEMO = ["--palette", "wada-229", "--strategy", "committed", "--mode", "persuade"]
DRIFT = "Drift: sampled as the work looks today, not the artist's original colours."

SANS = "ui-sans-serif, -apple-system, 'Segoe UI', Helvetica, Arial, 'Hiragino Sans', 'Noto Sans CJK JP', sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
# Frame colours follow GitHub's own light and dark themes so the images sit quietly in the README.
FRAME = {
    "light": {"card": "#ffffff", "line": "#d0d7de", "ink": "#1f2328", "muted": "#59636e"},
    "dark": {"card": "#151b23", "line": "#3d444d", "ink": "#f0f6fc", "muted": "#9198a1"},
}
# A typical agent default: Tailwind slate neutrals with an indigo-to-purple accent.
DEFAULT = {
    "light": {"bg": "#ffffff", "text": "#0f172a", "text-muted": "#64748b", "border": "#e2e8f0",
              "accent": "#6366f1", "on-accent": "#ffffff", "hero": ("#6366f1", "#a855f7"), "on-hero": "#ffffff"},
    "dark": {"bg": "#0f172a", "text": "#e2e8f0", "text-muted": "#94a3b8", "border": "#1e293b",
             "accent": "#6366f1", "on-accent": "#ffffff", "hero": ("#6366f1", "#a855f7"), "on-hero": "#ffffff"},
}


def load_palettes() -> list[dict]:
    rows = {r["id"]: r for r in csv.DictReader(open(SKILL / "data" / "palettes.csv", encoding="utf-8"))}
    out = []
    for pid in PALETTES:
        r = rows[pid]
        colours = []
        for h in r["colors"].split(";"):  # kasane layers repeat; show each colour once, in layer order
            if h not in colours:
                colours.append(h)
        title = re.sub(r"\s*\+\d+$", "", r["title"])
        if r["source_type"] == "painting":  # "Under the Wave off Kanagawa (The Great Wave) — Hokusai" -> "The Great Wave — Hokusai"
            name, _, artist = title.partition(" — ")
            m = re.search(r"\(([^)]+)\)", name)
            title = f"{m.group(1) if m else name} — {artist}"
        if r["title_ja"]:
            title = f"{title} {r['title_ja']}"
        out.append({"id": pid, "title": title, "label": r["label"], "colours": colours,
                    "drift": r["drift"] == "true", "type": r["source_type"]})
    return out


def build_demo_tokens() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tok = Path(tmp) / "tokens.json"
        for cmd in (["build_tokens.py", *DEMO, "--out", str(tok)], ["validate.py", str(tok), "--fix", "--in-place"]):
            subprocess.run([sys.executable, str(SKILL / "scripts" / cmd[0]), *cmd[1:]], check=True, capture_output=True)
        return json.loads(tok.read_text(encoding="utf-8"))


def ink_on(hex_: str) -> str:
    return "#000000" if wcag_contrast("#000000", hex_) >= wcag_contrast("#ffffff", hex_) else "#ffffff"


def wrap(text: str, width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + ([cur] if cur else [])


def italic_spans(text: str) -> str:
    """Markdown *italic* in a provenance label becomes an italic tspan."""
    parts = re.split(r"\*([^*]+)\*", text)
    return "".join(f'<tspan font-style="italic">{escape(p)}</tspan>' if i % 2 else escape(p) for i, p in enumerate(parts))


def palettes_svg(pals: list[dict], theme: str) -> str:
    f = FRAME[theme]
    cw, ch, gap, strip = 432, 168, 16, 76
    w, h = cw * 2 + gap, (ch + gap) * 3 - gap
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-label="Six palettes from the skill\'s data, each with its provenance label">',
           f'<style>text{{font-family:{SANS}}} .hex{{font-family:{MONO};font-size:10.5px}}</style>']
    for i, p in enumerate(pals):
        x, y = (i % 2) * (cw + gap), (i // 2) * (ch + gap)
        cid = f"c{i}"
        out.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="10"/></clipPath>')
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="10" fill="{f["card"]}"/>')
        sw = cw / len(p["colours"])
        for j, hx in enumerate(p["colours"]):
            sx = x + j * sw
            out.append(f'<rect x="{sx:.2f}" y="{y}" width="{sw + 0.5:.2f}" height="{strip}" fill="{hx}" clip-path="url(#{cid})"/>')
            out.append(f'<text class="hex" x="{sx + 8:.2f}" y="{y + strip - 9}" fill="{ink_on(hx)}">{hx}</text>')
        out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{cw - 1}" height="{ch - 1}" rx="10" fill="none" stroke="{f["line"]}"/>')
        ty = y + strip + 24
        out.append(f'<text x="{x + 14}" y="{ty}" font-size="14" font-weight="600" fill="{f["ink"]}">{escape(p["title"])}</text>')
        for k, line in enumerate(wrap(p["label"], 66)):
            out.append(f'<text x="{x + 14}" y="{ty + 19 + k * 15}" font-size="11.5" fill="{f["muted"]}">{italic_spans(line)}</text>')
        if p["drift"]:
            out.append(f'<text x="{x + 14}" y="{y + ch - 12}" font-size="11" font-style="italic" fill="{f["muted"]}">{escape(DRIFT)}</text>')
    out.append("</svg>")
    return "\n".join(out)


def mini_ui(x: int, y: int, c: dict, hero, on_hero: str, gid: str) -> list[str]:
    """One landing-page sketch, 420 x 268, in the given colours."""
    w, h = 420, 268
    fill = f"url(#{gid})" if isinstance(hero, tuple) else hero
    s = [f'<clipPath id="{gid}c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/></clipPath>',
         f'<g clip-path="url(#{gid}c)">',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c["bg"]}"/>',
         f'<circle cx="{x + 26}" cy="{y + 24}" r="7" fill="{c["accent"]}"/>',
         f'<text x="{x + 40}" y="{y + 29}" font-size="13" font-weight="700" fill="{c["text"]}">Kiln</text>',
         *[f'<text x="{x + 250 + k * 56}" y="{y + 29}" font-size="11.5" fill="{c["text-muted"]}">{t}</text>'
           for k, t in enumerate(["Glazes", "Studio", "Visit"])],
         f'<rect x="{x}" y="{y + 48}" width="{w}" height="104" fill="{fill}"/>',
         f'<text x="{x + 24}" y="{y + 90}" font-size="21" font-weight="700" fill="{on_hero}">Small-batch glazes,</text>',
         f'<text x="{x + 24}" y="{y + 116}" font-size="21" font-weight="700" fill="{on_hero}">fired every week.</text>',
         f'<text x="{x + 24}" y="{y + 180}" font-size="12.5" fill="{c["text"]}">Twelve glazes, mixed by hand and tested on real clay.</text>',
         f'<text x="{x + 24}" y="{y + 198}" font-size="12.5" fill="{c["text-muted"]}">Ships in 3 days. Free returns on unused sets.</text>',
         f'<rect x="{x + 24}" y="{y + 216}" width="118" height="34" rx="8" fill="{c["accent"]}"/>',
         f'<text x="{x + 83}" y="{y + 238}" font-size="13" font-weight="600" text-anchor="middle" fill="{c["on-accent"]}">Order a set</text>',
         f'<rect x="{x + 152.5}" y="{y + 216.5}" width="117" height="33" rx="8" fill="none" stroke="{c["border"]}"/>',
         f'<text x="{x + 211}" y="{y + 238}" font-size="13" font-weight="600" text-anchor="middle" fill="{c["text"]}">See the kiln</text>',
         "</g>"]
    if isinstance(hero, tuple):
        s.insert(0, f'<linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{hero[0]}"/>'
                    f'<stop offset="1" stop-color="{hero[1]}"/></linearGradient>')
    return s


def ratio_line(pairs: list[tuple[str, str, str, float]]) -> str:
    """name, fg, bg, WCAG 2 minimum for that text (4.5 body and labels, 3 large text)."""
    out = []
    for name, fg, bg, minimum in pairs:
        r = wcag_contrast(fg, bg)
        out.append(f"{name} {r:.2f}:1" + (f" (under {minimum:g}:1)" if r < minimum else ""))
    return " · ".join(out)


def before_after_svg(tokens: dict, theme: str) -> str:
    f = FRAME[theme]
    d = DEFAULT[theme]
    roles = {k: v["hex"] for k, v in tokens["roles"][theme].items()}
    acp = {"bg": roles["bg"], "text": roles["text"], "text-muted": roles["text-muted"], "border": roles["border-strong"],
           "accent": roles["accent"], "on-accent": roles["on-accent"]}
    w, h, pw, gap = 880, 372, 420, 40
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
         f'aria-label="The same landing page in a typical default palette and in tokens the skill built from Wada plate 229">',
         f'<style>text{{font-family:{SANS}}}</style>',
         f'<text x="0" y="16" font-size="13" font-weight="600" fill="{f["muted"]}">A typical default</text>',
         f'<text x="{pw + gap}" y="16" font-size="13" font-weight="600" fill="{f["ink"]}">Wada plate 229, built by the skill · Committed · Persuade</text>',
         *mini_ui(0, 30, d, d["hero"], d["on-hero"], f"g{theme}d"),
         *mini_ui(pw + gap, 30, acp, roles["brand"], roles["on-brand"], f"g{theme}a"),
         f'<rect x="0.5" y="30.5" width="{pw - 1}" height="267" rx="12" fill="none" stroke="{f["line"]}"/>',
         f'<rect x="{pw + gap + 0.5}" y="30.5" width="{pw - 1}" height="267" rx="12" fill="none" stroke="{f["line"]}"/>']
    left = ratio_line([("Button label", d["on-accent"], d["accent"], 4.5), ("Large heading", d["on-hero"], d["hero"][1], 3),
                       ("Body", d["text"], d["bg"], 4.5)])
    right = ratio_line([("Button label", acp["on-accent"], acp["accent"], 4.5), ("Large heading", roles["on-brand"], roles["brand"], 3),
                        ("Body", acp["text"], acp["bg"], 4.5)])
    s += [f'<text x="0" y="322" font-size="11.5" fill="{f["muted"]}">{escape(left)}</text>',
          f'<text x="{pw + gap}" y="322" font-size="11.5" fill="{f["muted"]}">{escape(right)}</text>',
          f'<text x="0" y="356" font-size="11.5" fill="{f["muted"]}">Right: roles from build_tokens.py and validate.py --fix '
          f'({theme} mode). WCAG 2 ratios from the skill\'s colorlib; minimums 4.5:1 text, 3:1 large text.</text>',
          "</svg>"]
    return "\n".join(s)


def card_html(pals: list[dict], tokens: dict) -> str:
    r = {k: v["hex"] for k, v in tokens["roles"]["dark"].items()}
    def short(p: dict) -> str:
        if p["type"] == "wada_plate":
            return p["label"].split(" (")[0] + ", 1933"
        if p["type"] == "kasane":
            return "Kasane no irome: " + p["title"].split(" (")[0]
        year = p["label"].split(" by colorcombinations")[0].rsplit(", ", 1)[1]
        return f'{p["title"].replace(" — ", ", ")}, {year}'

    bars = "\n".join(
        f'<div class="row"><div class="bar">{"".join(f"<i style=background:{h}></i>" for h in p["colours"])}</div>'
        f'<span>{escape(short(p))}</span></div>' for p in pals)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>artistic-color-palettes card</title>
<style>
  /* Colours: the dark-mode roles the skill composed from Wada plate 229 (Committed, Persuade). */
  html,body{{margin:0;height:100%;background:{r['bg']};color:{r['text']};font-family:{SANS}}}
  .card{{box-sizing:border-box;width:100vw;height:100vh;padding:5.4vw 5.6vw;display:grid;grid-template-columns:1.05fr 1fr;gap:4.6vw;align-items:center}}
  h1{{font-size:4.3vw;line-height:1.05;margin:0 0 1.8vw;letter-spacing:-.02em}}
  h1 b{{color:{r['brand']}}}
  p{{font-size:1.75vw;line-height:1.45;margin:0 0 2.2vw;color:{r['text-muted']}}}
  code{{display:inline-block;white-space:nowrap;font-family:{MONO};font-size:1.3vw;padding:.9vw 1.2vw;border-radius:.7vw;background:{r['surface']};border:1px solid {r['border']};color:{r['text']}}}
  .agents{{margin-top:1.6vw;font-size:1.3vw;color:{r['text-muted']}}}
  .row{{display:flex;flex-direction:column;gap:.55vw;margin-bottom:1.25vw}}
  .bar{{display:flex;height:3.3vw;border-radius:.6vw;overflow:hidden;box-shadow:0 0 0 1px {r['border']}}}
  .bar i{{flex:1}}
  .row span{{font-size:1.15vw;color:{r['text-muted']}}}
</style></head><body><div class="card">
<div><h1>Real artistic colour palettes for <b>coding agents</b></h1>
<p>Wada's 1933 plates, Heian kasane and public-domain paintings, turned into OKLCH tokens with measured contrast and a composed dark mode. Every colour keeps its provenance.</p>
<code>npx skills add youssef4laa/artistic-color-palettes</code>
<div class="agents">An Agent Skill for Claude Code, Codex, Cursor, Gemini CLI and more</div></div>
<div>{bars}</div>
</div></body></html>
"""


def icon_html() -> str:
    """Plugin icon: the six layers of Kasane no irome: Ume-gasane (layered plum), outermost first."""
    rows = {r["id"]: r for r in csv.DictReader(open(SKILL / "data" / "palettes.csv", encoding="utf-8"))}
    layers = []
    for h in rows["kasane-ume-gasane"]["colors"].split(";"):
        if h not in layers:
            layers.append(h)
    divs = [f'<div style="position:absolute;inset:0;background:{layers[0]}"></div>']
    for i, h in enumerate(layers[1:], 1):
        inset, radius = 82 * i, max(150 - 18 * i, 24)
        divs.append(f'<div style="position:absolute;inset:{inset}px;border-radius:{radius}px;background:{h}"></div>')
    return ('<!doctype html><html><body style="margin:0;width:1024px;height:1024px;position:relative;overflow:hidden">'
            + "".join(divs) + "</body></html>")


def find_chrome() -> str:
    candidates = [os.environ.get("CHROME", ""), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "google-chrome", "chromium", "chromium-browser", "chrome"]
    for c in candidates:
        if c and (Path(c).is_file() or shutil.which(c)):
            return c
    sys.exit("Google Chrome or Chromium is needed to render the PNGs; set CHROME to its path")


def screenshot(chrome: str, page: Path, png: Path, w: int, h: int, scale: int, transparent: bool) -> None:
    args = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
            f"--window-size={w},{h}", f"--force-device-scale-factor={scale}", f"--screenshot={png}"]
    if transparent:
        args.append("--default-background-color=00000000")
    subprocess.run([*args, page.as_uri()], check=True, capture_output=True, timeout=120)


def svg_to_png(chrome: str, svg: str, png: Path, tmp: Path) -> None:
    """Render at 2x on a transparent ground, so the PNG looks like the SVG in either GitHub theme."""
    w, h = (int(v) for v in re.search(r'width="(\d+)" height="(\d+)"', svg).groups())
    (tmp / "img.svg").write_text(svg, encoding="utf-8")
    page = tmp / "img.html"
    page.write_text(f'<!doctype html><html><body style="margin:0;background:transparent">'
                    f'<img src="img.svg" width="{w}" height="{h}" style="display:block"></body></html>', encoding="utf-8")
    screenshot(chrome, page, png, w, h, 2, True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    chrome = find_chrome()
    pals = load_palettes()
    tokens = build_demo_tokens()
    if not tokens["contrast"]["gate_pass"]:
        sys.exit("demo tokens fail the WCAG gate; pick another demo palette")
    with tempfile.TemporaryDirectory() as tmp:
        for theme in ("light", "dark"):
            svg_to_png(chrome, palettes_svg(pals, theme), OUT / f"palettes-{theme}.png", Path(tmp))
            svg_to_png(chrome, before_after_svg(tokens, theme), OUT / f"before-after-{theme}.png", Path(tmp))
        (Path(tmp) / "icon.html").write_text(icon_html(), encoding="utf-8")
        screenshot(chrome, Path(tmp) / "icon.html", REPO / ".claude-plugin" / "icon.png", 1024, 1024, 1, False)
    (OUT / "card.html").write_text(card_html(pals, tokens), encoding="utf-8")
    screenshot(chrome, OUT / "card.html", OUT / "social-preview.png", 1280, 640, 1, False)
    print("wrote", ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
