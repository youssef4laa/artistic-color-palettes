#!/usr/bin/env python3
"""Compare Wada's printed CMYK index with the colorcombinations.org hex values.

Stdlib only.  Run:  python compare.py   (optionally --threshold 0.05)

Inputs (relative to this file):
  ../wada-index.csv        transcription of the printed index (no,kanji,kana,english,c,m,y,k,...)
  palettes.csv             https://colorcombinations.org/data/palettes.csv  (wada-* rows)
  mattdesl-colors.json     mattdesl/dictionary-of-colour-combinations colors.json (MIT)

Conversions CMYK (0-100 as printed) -> sRGB:
  naive : R = 255*(1-c)*(1-k) etc.  (what a quick script would do)
  gcr   : an ink-limited, K-as-its-own-ink model, documented in cmyk_gcr() below.

Distance: Euclidean in OKLab (Bjorn Ottosson's matrices), 0-1 scale, so 0.02 is roughly
a just-noticeable difference and 0.05 is clearly visible.
"""
import argparse
import csv
import json
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- colour maths


def srgb_to_lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def lin_to_srgb(v):
    v = max(0.0, min(1.0, v))
    v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
    return 255.0 * v


def hex_to_rgb(h):
    h = h.strip().lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def linrgb_to_oklab(r, g, b):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def rgb_to_oklab(rgb):
    return linrgb_to_oklab(*(srgb_to_lin(c) for c in rgb))


def oklab_to_oklch(lab):
    L, a, b = lab
    h = math.degrees(math.atan2(b, a)) % 360
    return (L, math.hypot(a, b), h)


def de_ok(p, q):
    return math.dist(p, q)


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(round(max(0, min(255, c)))) for c in rgb)


# ---------------------------------------------------------------- CMYK -> sRGB


def cmyk_naive(c, m, y, k):
    """c,m,y,k in 0-100. Plain 255*(1-c)*(1-k)."""
    c, m, y, k = (x / 100.0 for x in (c, m, y, k))
    return tuple(255.0 * (1 - ch) * (1 - k) for ch in (c, m, y))


# Approximate solid-ink colours of a coated SWOP-like press (sRGB, as commonly
# quoted for Process Cyan / Magenta / Yellow / Black solids).  They are
# approximations, not a measured profile.
INK_C = (0, 174, 239)
INK_M = (236, 0, 140)
INK_Y = (255, 242, 0)
INK_K = (35, 31, 32)
TAC = 3.00      # total ink limit: C+M+Y+K <= 300 % (K counted as one ink)
DOT_GAIN = 0.12  # extra mid-tone coverage at 50 % nominal (12 % dot gain)


def cmyk_gcr(c, m, y, k):
    """GCR-aware, ink-limited CMYK -> sRGB.

    1. Treat K as a fourth, independent ink (that is what GCR/UCR separations
       assume: neutral density lives in K, so C/M/Y are small where K is large).
    2. Apply the ink limit: if C+M+Y+K exceeds 300 %, scale all four down
       proportionally (never raises coverage).
    3. Dot gain: effective coverage a' = a + 4*g*a*(1-a), g = 0.12.
    4. Mix subtractively in linear light, multiplicatively per channel:
           R_lin = prod_i ( 1 - a_i + a_i * T_i )
       where T_i is the linear-light colour of the solid ink i on paper (white).
       Combined with the solid-ink K of about sRGB 35,31,32 this gives a rich
       black a little above 0 instead of pure 0.
    A multiplicative (Beer-Lambert-like) model is a coarse stand-in for a real
    ICC profile; it is meant to show how far a more press-like conversion moves
    the colours relative to the naive formula, not to replace a profile.
    """
    a = [x / 100.0 for x in (c, m, y, k)]
    total = sum(a)
    if total > TAC:
        a = [x * TAC / total for x in a]
    a = [x + 4 * DOT_GAIN * x * (1 - x) for x in a]
    a = [min(1.0, x) for x in a]
    inks = [INK_C, INK_M, INK_Y, INK_K]
    out = []
    for ch in range(3):
        v = 1.0
        for cov, ink in zip(a, inks):
            t = srgb_to_lin(ink[ch])
            v *= 1 - cov + cov * t
        out.append(lin_to_srgb(v))
    return tuple(out)


# ---------------------------------------------------------------- name matching

ALIASES = {
    # spelling variants seen on the site / in mattdesl vs the printed index
    'sulpher': 'sulphur', 'ochre': 'ocher', 'krongbergs': 'kronbergs',
    'artemesia': 'artemisia', 'pomegranite': 'pomegranate', 'veronia': 'vernonia',
    'antwarp': 'antwarp',  # kept as printed; listed so the table is explicit
}


def norm(name):
    s = re.sub(r'[^a-z]', '', name.lower())
    for k, v in ALIASES.items():
        s = s.replace(k, v)
    return s


# duplicated English names in the printed index, disambiguated by plate number
DUP_SITE = {12: 'Eugenia Red A', 13: 'Eugenia Red B',
            134: 'Grayish Lavender - A', 135: 'Grayish Lavender - B'}


# ---------------------------------------------------------------- loading


def load_index():
    with open(os.path.join(HERE, '..', 'wada-index.csv'), encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['no'] = int(r['no'])
        r['cmyk'] = tuple(int(r[k]) for k in 'cmyk')
    return rows


def load_site():
    """name -> (hex, set of plate slugs). Wada rows only."""
    site = {}
    with open(os.path.join(HERE, 'palettes.csv'), encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            if not r['slug'].startswith('wada-'):
                continue
            for i in range(1, 5):
                nm = r.get('color_%d' % i)
                if nm:
                    site.setdefault(nm, set()).add(r['hex_%d' % i].lower())
    return site


def load_matt():
    with open(os.path.join(HERE, 'mattdesl-colors.json'), encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--threshold', type=float, default=0.05)
    args = ap.parse_args()
    thr = args.threshold
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    idx = load_index()
    site = load_site()
    matt = load_matt()
    site_norm = {}
    for nm, hx in site.items():
        site_norm.setdefault(norm(nm), []).append(nm)

    results = []
    unmatched = []
    used_site = set()
    for r in idx:
        no, eng = r['no'], r['english']
        site_name, how = None, None
        if no in DUP_SITE and DUP_SITE[no] in site:
            site_name, how = DUP_SITE[no], 'number (duplicate name)'
        elif eng in site:
            site_name, how = eng, 'exact'
        else:
            cands = [n for n in site_norm.get(norm(eng), []) if n not in DUP_SITE.values()]
            if len(cands) == 1:
                site_name, how = cands[0], 'normalised spelling'
        if site_name is None:
            unmatched.append(r)
            continue
        used_site.add(site_name)
        hx = sorted(site[site_name])
        sh = hx[0]
        row = dict(r)
        row.update(site_name=site_name, how=how, site_hex=sh, site_hexes=hx)
        c, m, y, k = r['cmyk']
        row['naive_rgb'] = cmyk_naive(c, m, y, k)
        row['gcr_rgb'] = cmyk_gcr(c, m, y, k)
        row['site_lab'] = rgb_to_oklab(hex_to_rgb(sh))
        row['naive_lab'] = rgb_to_oklab(tuple(round(v) for v in row['naive_rgb']))
        row['gcr_lab'] = rgb_to_oklab(tuple(round(v) for v in row['gcr_rgb']))
        row['de_naive'] = de_ok(row['naive_lab'], row['site_lab'])
        row['de_gcr'] = de_ok(row['gcr_lab'], row['site_lab'])
        results.append(row)

    unused_site = sorted(set(site) - used_site)

    # mattdesl: same order as the printed index (checked by name), carries cmyk + hex
    matt_issues = []
    matt_by_no = {}
    for i, x in enumerate(matt, start=1):
        matt_by_no[i] = x
    for r in results:
        x = matt_by_no.get(r['no'])
        r['matt_hex'] = x['hex'] if x else None
        r['matt_name_ok'] = bool(x) and norm(x['name'].split('|')[0].split(' - ')[0]) == norm(r['english'].split(' - ')[0])
        if x:
            r['matt_cmyk'] = tuple(x['cmyk'])
            r['de_matt_site'] = de_ok(rgb_to_oklab(hex_to_rgb(x['hex'])), r['site_lab'])
            r['matt_cmyk_diff'] = r['matt_cmyk'] != r['cmyk']
    for r in idx:
        x = matt_by_no.get(r['no'])
        if x and tuple(x['cmyk']) != r['cmyk']:
            matt_issues.append((r, x))

    n = len(results)
    print('# Wada CMYK index vs colorcombinations.org hex')
    print()
    print('- index rows: %d; site Wada colour names: %d; matched: %d; unmatched index rows: %d; '
          'site names unused: %d' % (len(idx), len(site), n, len(unmatched), len(unused_site)))
    how_counts = {}
    for r in results:
        how_counts[r['how']] = how_counts.get(r['how'], 0) + 1
    print('- match method: ' + ', '.join('%s=%d' % kv for kv in sorted(how_counts.items())))
    print('- site names with more than one hex across plates: %d' %
          sum(1 for v in site.values() if len(v) > 1))
    print('- mattdesl entries: %d; matched by position and name: %d' %
          (len(matt), sum(1 for r in results if r['matt_name_ok'])))
    print()
    for label, key in (('naive', 'de_naive'), ('gcr', 'de_gcr')):
        vals = [r[key] for r in results]
        over = sum(1 for v in vals if v > thr)
        print('- %s: mean dE_OK %.4f, median %.4f, max %.4f, > %.2f: %d of %d' %
              (label, statistics.mean(vals), statistics.median(vals), max(vals), thr, over, n))
    mv = [r['de_matt_site'] for r in results if 'de_matt_site' in r]
    print('- mattdesl hex vs site hex: mean %.4f, max %.4f, > %.2f: %d of %d' %
          (statistics.mean(mv), max(mv), thr, sum(1 for v in mv if v > thr), len(mv)))
    print()

    for label, key, rgbkey in (('naive', 'de_naive', 'naive_rgb'), ('gcr', 'de_gcr', 'gcr_rgb')):
        drift = sorted((r for r in results if r[key] > thr), key=lambda r: -r[key])
        print('## Drift > %.2f dE_OK, %s conversion (%d colours)' % (thr, label, len(drift)))
        print()
        print('| no | name | CMYK | site hex | %s hex | dE | site L C h | conv L C h |' % label)
        print('|---|---|---|---|---|---|---|---|')
        for r in drift:
            sl = oklab_to_oklch(r['site_lab'])
            cl = oklab_to_oklch(r['naive_lab' if label == 'naive' else 'gcr_lab'])
            print('| %d | %s | %d/%d/%d/%d | %s | %s | %.3f | %.2f %.3f %.0f | %.2f %.3f %.0f |' % (
                r['no'], r['english'], *r['cmyk'], r['site_hex'],
                rgb_to_hex(r[rgbkey]), r[key], *sl, *cl))
        print()

    print('## Unmatched printed-index rows (no site colour found)')
    print()
    for r in unmatched:
        print('- %d %s' % (r['no'], r['english']))
    if not unmatched:
        print('- none')
    print()
    print('## Site names not matched to any index row')
    print()
    for nm in unused_site:
        print('- %s' % nm)
    if not unused_site:
        print('- none')
    print()
    print('## Spelling differences (index vs site name)')
    print()
    for r in results:
        if r['how'] != 'exact':
            print('- %d: index "%s" -> site "%s" (%s)' % (r['no'], r['english'], r['site_name'], r['how']))
    print()
    print('## CMYK differences between my transcription and mattdesl colors.json')
    print()
    for r, x in matt_issues:
        print('- %d %s: index %s, mattdesl %s' % (r['no'], r['english'], list(r['cmyk']), x['cmyk']))
    if not matt_issues:
        print('- none')
    print()
    print('## Rows where mattdesl hex differs from site hex by > %.2f' % thr)
    print()
    for r in results:
        if r.get('de_matt_site', 0) > thr:
            print('- %d %s: site %s, mattdesl %s, dE %.3f' % (
                r['no'], r['english'], r['site_hex'], r['matt_hex'], r['de_matt_site']))


if __name__ == '__main__':
    main()
