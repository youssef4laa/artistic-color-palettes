#!/usr/bin/env python3
"""preview.py - one self-contained HTML page that shows 3-5 palette candidates as applied mini-layouts.

For every candidate the page builds the tokens (build_tokens.py), makes them pass the contrast gate
(validate.py --fix, lightness only) and renders the same mini-layout - page, header, card, text,
buttons, link, table, bar chart, tags, status chips - in light, dark and greyscale (luminance-matched
grey, so you can judge the value structure), each labelled with its provenance. The band heights
follow the strategy's proportion targets (the skill's own convention, not Wada's).

No network, no external fonts, no scripts: just HTML and CSS. The script writes the file and prints its path.

Examples:
  python3 scripts/preview.py --palette wada-229 --palette wada-100 --palette paint-the-great-wave-off-kanagawa
  python3 scripts/preview.py --palette ed-kurenai-kon --palette kasane-fuji --hex "#9a2a2a,#1b2a4e,#f4eee0" --strategy committed --out out/preview.html
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import colorlib as cl  # noqa: E402
import build_tokens as bt  # noqa: E402
import validate as vd  # noqa: E402

E = html.escape


def css_vars(tokens: dict, mode: str, grey: bool = False) -> str:
    src = "light" if grey else mode
    parts = []
    for tok, role in tokens["roles"][src].items():
        v = cl.to_greyscale(role["hex"]) if grey else role["hex"]
        parts.append(f"--{tok}:{v}")
    return ";".join(parts)


def bands(tokens: dict) -> list[tuple[str, str, float, str]]:
    """(background token, text token, height weight, label) for the hero stack, from the strategy."""
    st = tokens["strategy"]["name"]
    p = tokens["proportions"]
    has = lambda t: t in tokens["roles"]["light"]  # noqa: E731
    out: list[tuple[str, str, float, str]] = []
    if st == "Committed" and has("brand"):
        w = sum(p["palette_pct"]) / 2
        out.append(("brand", "on-brand", w, f"brand colour, target {p['palette_pct'][0]}-{p['palette_pct'][1]}%"))
    elif st == "Full palette":
        if has("voice-1"):
            out.append(("voice-1", "on-voice-1", sum(p["secondary_pct"]) / 2, f"secondary {p['secondary_pct'][0]}-{p['secondary_pct'][1]}%"))
        if has("voice-2"):
            out.append(("voice-2", "on-voice-2", sum(p["tertiary_pct"]) / 2, f"tertiary {p['tertiary_pct'][0]}-{p['tertiary_pct'][1]}%"))
    return out


def panel(tokens: dict, idx: int, kind: str) -> str:
    mode = "dark" if kind == "dark" else "light"
    style = css_vars(tokens, mode, grey=(kind == "grey"))
    roles = tokens["roles"]["light"]
    voices = [t for t in roles if t.startswith("voice-") and t.count("-") == 1]
    status = [t for t in ("success", "warning", "danger", "info") if t in roles]
    stack = bands(tokens)
    bands_html = "".join(
        f'<div class="band" style="flex:{w:.0f};background:var(--{bg});color:var(--{fg})"><span>{E(label)}</span></div>'
        for bg, fg, w, label in stack)
    bars = voices[:4] or ["accent"]
    chart = "".join(
        f'<i style="height:{h}%;background:var(--{t + "-mark" if t.startswith("voice-") else t})"></i>'
        for t, h in zip(["accent"] + bars, (82, 61, 74, 44, 58)))
    tags = "".join(f'<span class="tag" style="background:var(--{v}-subtle);color:var(--{v}-text)">{v.replace("-", " ")}</span>' for v in voices[:3])
    chips = "".join(f'<span class="chip" style="background:var(--{s}-subtle);color:var(--{s}-text);border-color:var(--{s})">{s}</span>' for s in status)
    return f"""<div class="panel {kind}" style="{style}">
  <div class="tag-line">{E(kind)}</div>
  <header><b>Brand</b><nav><a>Docs</a><a>Pricing</a></nav><button class="btn">Get started</button></header>
  <main>
    {bands_html}
    <div class="body">
      <h3>Heading in text colour</h3>
      <p>Body copy sits on the page colour. <a>A link in accent text</a> and <span class="muted">muted secondary text</span>.</p>
      <div class="card">
        <h4>Card on surface</h4>
        <p class="muted">Quiet detail line with a divider below.</p>
        <hr>
        <div class="row"><button class="btn">Primary</button><button class="btn ghost">Secondary</button><input value="Focus ring" class="field"></div>
        <div class="row">{tags}{chips}</div>
      </div>
      <div class="split">
        <table><thead><tr><th>Item</th><th>Qty</th></tr></thead><tbody><tr><td>Alpha</td><td>12</td></tr><tr class="alt"><td>Beta</td><td>7</td></tr></tbody></table>
        <div class="chart">{chart}</div>
      </div>
    </div>
  </main>
</div>"""


PAGE_CSS = """
:root{color-scheme:light dark;--pg:#f4f4f2;--ink:#1c1c1a;--mute:#5d5d58;--line:#cfcfca;--card:#fff}
@media (prefers-color-scheme:dark){:root{--pg:#161615;--ink:#ecece8;--mute:#a5a5a0;--line:#3a3a37;--card:#1f1f1d}}
*{box-sizing:border-box}
body{margin:0;background:var(--pg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:0}
.note{color:var(--mute);font-size:13px;margin:4px 0}
.cand{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:20px 0}
.swatches{display:flex;gap:4px;margin:10px 0;flex-wrap:wrap}
.sw{min-width:92px;flex:1;padding:8px;border-radius:6px;font:12px/1.3 ui-monospace,Consolas,monospace;border:1px solid rgba(128,128,128,.35)}
.props{display:flex;height:16px;border-radius:8px;overflow:hidden;margin:8px 0 2px;border:1px solid var(--line)}
.props i{display:block}
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:12px}
.panel{background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:10px;overflow:hidden;font-size:13px;display:flex;flex-direction:column;min-height:420px}
.panel .tag-line{font:11px ui-monospace,Consolas,monospace;text-transform:uppercase;letter-spacing:.08em;padding:4px 10px;background:var(--bg-subtle);color:var(--text-muted)}
.panel header{display:flex;align-items:center;gap:12px;padding:8px 10px;background:var(--surface);border-bottom:1px solid var(--border)}
.panel nav{display:flex;gap:10px;margin-right:auto}
.panel a{color:var(--accent-text);text-decoration:underline;cursor:pointer}
.panel main{display:flex;flex-direction:column;flex:1}
.band{display:flex;align-items:center;padding:8px 12px;min-height:26px;font-size:12px}
.body{padding:10px 12px;flex:9}
.panel h3{margin:0 0 4px;font-size:16px}.panel h4{margin:0;font-size:14px}.panel p{margin:4px 0}
.muted{color:var(--text-muted)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:10px;margin:8px 0}
.card hr{border:0;border-top:1px solid var(--border-subtle);margin:8px 0}
.row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0}
.btn{background:var(--action);color:var(--on-action);border:1px solid var(--action-border);border-radius:6px;padding:5px 10px;font:inherit;cursor:pointer}
.btn:hover{background:var(--action-hover)}
.btn.ghost{background:transparent;color:var(--text);border:1px solid var(--border-strong)}
.field{background:var(--surface);color:var(--text);border:1px solid var(--border-strong);border-radius:6px;padding:4px 8px;font:inherit;outline:2px solid var(--focus);outline-offset:1px;width:110px}
.tag,.chip{border-radius:999px;padding:1px 8px;font-size:11px}.chip{border:1px solid}
.split{display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:end;margin-top:8px}
table{border-collapse:collapse;width:100%;font-size:12px}
th,td{text-align:left;padding:4px 6px;border-bottom:1px solid var(--border-subtle)}th{background:var(--bg-subtle)}
tr.alt td{background:var(--surface-hover)}
.chart{display:flex;gap:6px;align-items:flex-end;height:70px;border-bottom:1px solid var(--border)}
.chart i{flex:1;display:block;border-radius:3px 3px 0 0}
@media (max-width:520px){.split{grid-template-columns:1fr}}
"""


def candidate_html(tokens: dict, idx: int) -> str:
    p = tokens["palette"]
    st = tokens["strategy"]["name"]
    prop = tokens["proportions"]
    sw = "".join(
        f'<div class="sw" style="background:{m["hex"]};color:{cl.best_text_color(m["hex"])[0]}">{E(m["name"])}<br>{m["hex"]}<br>{" / ".join(str(v) for v in m["oklch"][:2])}</div>'
        for m in p["members"])
    low = lambda t: tokens["roles"]["light"][t]["hex"] if t in tokens["roles"]["light"] else "#888888"  # noqa: E731
    segs = [("neutrals", prop["neutrals_pct"], low("bg")), ("palette", prop["palette_pct"], low("brand" if "brand" in tokens["roles"]["light"] else "voice-1")),
            ("accent", prop["accent_pct"], low("accent"))]
    bar = "".join(f'<i title="{n} {lo}-{hi}%" style="width:{(lo + hi) / 2:.1f}%;background:{c}"></i>' for n, (lo, hi), c in segs)
    drift = f'<p class="note">Note: {E(p["drift_note"])}</p>' if p.get("drift_note") else ""
    adj = tokens.get("adjustments") or []
    return f"""<section class="cand" id="c{idx}">
  <h2>{idx + 1}. {E(p['title'])}{(' ' + E(p['title_ja'])) if p['title_ja'] else ''}</h2>
  <p class="note"><b>{E(p['label'])}</b> | {E(p['credit'])} | licence {E(p['licence'])}</p>{drift}
  <div class="swatches">{sw}</div>
  <p class="note">{E(st)} / {E(tokens['strategy']['mode'])}: neutrals {prop['neutrals_pct'][0]}-{prop['neutrals_pct'][1]}%, {E(prop['palette_means'])} {prop['palette_pct'][0]}-{prop['palette_pct'][1]}%, accent {prop['accent_pct'][0]}-{prop['accent_pct'][1]}%. {len(adj)} lightness adjustment(s) made to pass the contrast gate; tone family: {E(p['tone_family'] or 'n/a')}.</p>
  <div class="props">{bar}</div>
  <p class="note">Bar = midpoints of the strategy's targets (the skill's own convention, not Wada's equal-area swatches).</p>
  <div class="panels">{panel(tokens, idx, 'light')}{panel(tokens, idx, 'dark')}{panel(tokens, idx, 'grey')}</div>
</section>"""


def render_page(cands: list[dict]) -> str:
    body = "\n".join(candidate_html(t, i) for i, t in enumerate(cands))
    first = cands[0]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Palette preview</title>
<style>{PAGE_CSS}</style></head>
<body><div class="wrap">
<h1>Palette preview</h1>
<p class="note">{len(cands)} candidates, strategy {E(first['strategy']['name'])}, mode {E(first['strategy']['mode'])}. Each is shown as light, dark (composed, not inverted) and greyscale (luminance-matched). Colours that failed the contrast gate were adjusted in lightness only.</p>
{body}
<p class="note">Palette data: colorcombinations.org (CC BY 4.0), mattdesl digitisation (MIT), Sanzo Wada (public domain); kasane base hex after Wikipedia (CC BY-SA 4.0). Generated by artistic-color-palettes preview.py.</p>
</div></body></html>
"""


def main(argv=None) -> int:
    cl.configure_stdio()
    ap = argparse.ArgumentParser(
        prog="preview.py",
        description="Write one self-contained HTML page comparing 3-5 palette candidates as applied mini-layouts "
                    "(light, dark, greyscale) at the strategy's proportion targets, labelled with provenance.",
    )
    ap.add_argument("--palette", action="append", default=[], help="palette id (repeat 3-5 times)")
    ap.add_argument("--hex", action="append", default=[], help="explicit hex list as a candidate (repeatable)")
    ap.add_argument("--strategy", default="restrained", help="restrained | committed | full-palette | drenched")
    ap.add_argument("--mode", default="operate", help="persuade | operate | read | experience")
    ap.add_argument("--out", type=Path, default=Path("palette-preview.html"), help="output HTML file (default ./palette-preview.html)")
    ap.add_argument("--any-count", action="store_true", help="allow fewer than 3 or more than 5 candidates")
    ap.add_argument("--data-dir", type=Path, help="folder with palettes.csv (default <skill>/data)")
    args = ap.parse_args(argv)
    n = len(args.palette) + len(args.hex)
    if not args.any_count and not 3 <= n <= 5:
        print(f"error: give 3 to 5 candidates (got {n}); use --any-count to override", file=sys.stderr)
        return 2
    if n < 1:
        print("error: no candidates", file=sys.stderr)
        return 2
    cands = []
    try:
        for pid in args.palette:
            t = bt.build_tokens(palette=pid, strategy=args.strategy, mode=args.mode, data_dir=args.data_dir)
            vd.validate_tokens(t, do_fix=True)
            cands.append(t)
        for spec in args.hex:
            t = bt.build_tokens(hexes=spec, strategy=args.strategy, mode=args.mode)
            vd.validate_tokens(t, do_fix=True)
            cands.append(t)
    except SystemExit as exc:
        msg = str(exc)
        while msg.lower().startswith("error: "):
            msg = msg[7:]
        print(f"error: {msg}", file=sys.stderr)
        return 2
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_page(cands), encoding="utf-8", newline="\n")
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
