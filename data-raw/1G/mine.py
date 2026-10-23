"""Measure the area share of each colour on Wada's four-colour plates (241-348).

Build-time tool (not shipped). Needs pypdfium2, Pillow, numpy, scipy (all user-site).
Only derived numbers (area shares) are written out; renders stay in the git-ignored
notes/wada-pages/1G folder.

Layout of every four-colour plate: one plate per PDF page, plate number printed top-left,
PDF page = plate - 89. Four rectangles forming a cross: top, middle-left, middle-right, bottom.
Rectangle areas encode the proportion of each colour.

Method per plate
  1. render the page (SCALE), keep the upper part (swatch area, text lives below)
  2. paper colour = median of the top strip; swatch mask = OKLab distance to paper > T_PAPER,
     small components (specks, page number, margin rule) removed, holes filled
  3. k-means (k=4, k-means++ restarts) on the eroded swatch pixels in OKLab
  4. every swatch pixel goes to its nearest cluster centre -> area shares
  5. clusters are matched to the website's 4 hex colours by optimal assignment (24 permutations,
     minimum summed OKLab distance); the website's order (hex_1..hex_4) gives color_index
  6. confidence combines match quality, assignment margin and spatial compactness
"""
import csv
import glob
import os
import sys
import itertools
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import pypdfium2 as pdfium

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PAGES = os.path.join(REPO, "notes", "wada-pages", "1G")
OUT_CSV = os.path.join(os.path.dirname(HERE), "wada-proportions.csv")
DIAG_CSV = os.path.join(HERE, "diagnostics.csv")
PDF = glob.glob(r"D:\Code\Skill\Art References\*Seigensha*.pdf")[0]
PALETTES = os.path.join(HERE, "palettes.csv")

SCALE = 3.0          # render scale (page 271.6 pt wide -> 815 px; native scan is ~5x)
PAGE_OFFSET = 89     # pdf page = plate - 89
SWATCH_BOTTOM = 0.60  # swatches end above 60% of page height; names start below
T_PAPER = 0.045      # OKLab distance from paper to count as swatch
MIN_COMP = 0.004     # drop components smaller than this share of the image
ERODE = 3            # px erosion before clustering (avoids edge/emboss pixels)


def srgb_to_oklab(rgb):
    c = rgb.astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.stack([
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s], axis=-1)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.uint8)


def kmeans(X, k, restarts=8, iters=40, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        # k-means++
        C = [X[rng.integers(len(X))]]
        for _ in range(k - 1):
            d = np.min(((X[:, None, :] - np.array(C)[None]) ** 2).sum(-1), axis=1)
            C.append(X[rng.choice(len(X), p=d / d.sum())])
        C = np.array(C)
        for _ in range(iters):
            lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(-1), axis=1)
            newC = np.array([X[lab == j].mean(0) if np.any(lab == j) else C[j] for j in range(k)])
            if np.allclose(newC, C, atol=1e-6):
                break
            C = newC
        lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(-1), axis=1)
        inertia = ((X - C[lab]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, C)
    return best[1]


def load_plates():
    out = {}
    with open(PALETTES, encoding="utf8") as f:
        for r in csv.DictReader(f):
            if r["slug"].startswith("wada-"):
                n = int(r["slug"].split("-")[1])
                if n >= 241:
                    out[n] = [r[f"hex_{i}"] for i in (1, 2, 3, 4)]
    return out


def analyse(img, hexes):
    """img: PIL RGB page render. Returns dict with shares (in website order) and diagnostics."""
    a = np.asarray(img.convert("RGB"))
    H, W, _ = a.shape
    y1 = int(SWATCH_BOTTOM * H)
    roi = a[:y1]
    lab = srgb_to_oklab(roi)
    paper = np.median(lab[: int(0.02 * H)].reshape(-1, 3), axis=0)
    dist = np.sqrt(((lab - paper) ** 2).sum(-1))
    mask = dist > T_PAPER
    mask = ndi.binary_opening(mask, iterations=1)
    cl, n = ndi.label(mask)
    sizes = ndi.sum(mask, cl, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes > MIN_COMP * H * W
    touch = np.unique(np.concatenate([cl[:, 0], cl[:, -1]]))   # scan shadow along the page edge
    keep[touch[touch > 0]] = False
    mask = ndi.binary_fill_holes(keep[cl])
    inner = ndi.binary_erosion(mask, iterations=ERODE)
    X = lab[inner]
    if len(X) < 2000:
        return None
    sub = X[:: max(1, len(X) // 40000)]
    C = kmeans(sub, 4)
    # interior pixels: nearest centre by colour. Rim pixels (scanner halo / blended edges, the
    # outer ERODE px of the mask) copy the label of the nearest interior pixel instead, so the
    # blended rim cannot inflate one cluster.
    d2 = ((lab[inner][:, None, :] - C[None]) ** 2).sum(-1)
    lblimg = np.full(mask.shape, -1, int)
    lblimg[inner] = np.argmin(d2, axis=1)
    idx = ndi.distance_transform_edt(~inner, return_distances=False, return_indices=True)
    filled = lblimg[idx[0], idx[1]]
    lblimg[mask] = filled[mask]
    counts = np.bincount(lblimg[mask], minlength=4).astype(float)
    shares_cluster = counts / counts.sum()

    # geometric (positional) regions: the authoritative measurement
    got = geometry(mask, lab)
    if got is None:
        return None
    reg, ginfo = got
    gcount = np.array([(reg == k).sum() for k in range(4)], float)
    gshares = gcount / gcount.sum()
    inner_reg = np.where(inner, reg, -1)
    RC = np.array([np.median(lab[inner_reg == k], axis=0) for k in range(4)])   # region colours

    # match regions -> website hex colours (optimal assignment over 24 permutations)
    Hx = srgb_to_oklab(np.array([hex_to_rgb(h) for h in hexes]))
    D = np.sqrt(((RC[:, None, :] - Hx[None]) ** 2).sum(-1))  # region x hex
    costs = sorted((sum(D[perm[j], j] for j in range(4)), perm) for perm in itertools.permutations(range(4)))
    best_cost, perm = costs[0]           # perm[j] = region holding website colour j
    margin = costs[1][0] - best_cost
    shares = [gshares[perm[j]] for j in range(4)]
    match_d = [D[perm[j], j] for j in range(4)]
    sep = min(np.sqrt(((RC[i] - RC[j]) ** 2).sum()) for i in range(4) for j in range(i + 1, 4))

    # cross-check: colour k-means shares matched to the same regions (cluster whose centre is nearest region colour)
    Dk = np.sqrt(((C[:, None, :] - RC[None]) ** 2).sum(-1))
    kperm = min(itertools.permutations(range(4)), key=lambda p: sum(Dk[p[j], j] for j in range(4)))
    ks = np.array([shares_cluster[kperm[j]] for j in range(4)])      # k-means share of region j
    agree = float(np.abs(ks - gshares).max())
    # geometry sanity: the four rectangles should be near-equal and each one solid
    spread = float(gshares.max() - gshares.min())
    solid = []
    for k in range(4):
        l2, k2 = ndi.label(reg == k)
        sz = ndi.sum(reg == k, l2, range(1, k2 + 1))
        solid.append(sz.max() / sz.sum())
    return dict(shares=shares, match_d=match_d, mean_d=float(np.mean(match_d)), max_d=float(np.max(match_d)),
                margin=float(margin), compact=float(min(solid)), sep=float(sep), agree=agree, spread=spread,
                centers=RC, perm=perm, mask=mask, lblimg=reg, paper=paper,
                mask_share=float(mask.sum() / (H * W)), ginfo=ginfo)


def geometry(mask, lab):
    """Independent estimate from the cross layout: returns region label image (0 top, 1 mid-left,
    2 mid-right, 3 bottom, -1 outside) or None."""
    w = mask.sum(1)
    if w.max() == 0:
        return None
    mid = np.where(w > 0.8 * w.max())[0]
    # use the longest contiguous run of 'wide' rows as the middle row
    runs = np.split(mid, np.where(np.diff(mid) > 3)[0] + 1)
    run = max(runs, key=len)
    m0, m1 = run[0], run[-1]
    ys, xs = np.where(mask)
    reg = np.full(mask.shape, -1, int)
    rows = np.arange(mask.shape[0])[:, None] * np.ones((1, mask.shape[1]), int)
    reg[mask & (rows < m0)] = 0
    reg[mask & (rows > m1)] = 3
    midmask = mask & (rows >= m0) & (rows <= m1)
    cols = np.where(midmask.any(0))[0]
    xa, xb = cols[0], cols[-1]
    inner = midmask[m0 + 4: m1 - 3]
    labm = lab[m0 + 4: m1 - 3]
    colmean = np.array([labm[:, x][inner[:, x]].mean(0) if inner[:, x].sum() > 3 else np.zeros(3) for x in range(mask.shape[1])])
    g = np.sqrt(((colmean[3:] - colmean[:-3]) ** 2).sum(-1))  # change across 3 px
    lo, hi = int(xa + 0.3 * (xb - xa)), int(xa + 0.7 * (xb - xa))
    xs_split = lo + int(np.argmax(g[lo:hi])) + 2
    reg[midmask & (np.arange(mask.shape[1])[None, :] < xs_split)] = 1
    reg[midmask & (np.arange(mask.shape[1])[None, :] >= xs_split)] = 2
    return reg, (m0, m1, xa, xb, xs_split)

def confidence(r):
    """min of five terms, each in [0,1]. Shares themselves come from geometry, so the terms
    check (a) the colours really match the website hex, (b) the colour->index assignment is
    unambiguous, (c) the layout was found cleanly (solid rectangles), (d) the four rectangles
    are near-equal (they should be), and (e) an independent colour k-means agrees."""
    q = np.clip(1 - (r["max_d"] - 0.08) / 0.17, 0, 1)     # 0.08 ok .. 0.25 bad (website hex idealised, scans drift)
    m = np.clip(r["margin"] / 0.08, 0, 1)
    c = np.clip((r["compact"] - 0.95) / 0.04, 0, 1)
    g = np.clip(1 - (r["spread"] - 0.02) / 0.04, 0, 1)
    k = np.clip(1 - (r["agree"] - 0.02) / 0.04, 0, 1)
    return float(min(q, m, c, g, k))


def main():
    os.makedirs(PAGES, exist_ok=True)
    plates = load_plates()
    doc = pdfium.PdfDocument(PDF)
    rows, diag = [], []
    only = [int(x) for x in sys.argv[1:]] or sorted(plates)
    for n in only:
        pg = n - PAGE_OFFSET
        img = doc[pg - 1].render(scale=SCALE).to_pil().convert("RGB")
        r = analyse(img, plates[n])
        if r is None:
            print(n, "FAILED (no swatch)")
            diag.append([n, pg, "fail"] + [""] * 10)
            for i in range(4):
                rows.append([n, i + 1, plates[n][i], "", pg, 0.0])
            continue
        conf = confidence(r)
        tot = sum(r["shares"])
        for i in range(4):
            rows.append([n, i + 1, plates[n][i], f"{r['shares'][i] / tot:.4f}", pg, f"{conf:.2f}"])
        diag.append([n, pg, "ok", f"{conf:.2f}", f"{r['mean_d']:.3f}", f"{r['max_d']:.3f}", f"{r['margin']:.3f}",
                     f"{r['compact']:.3f}", f"{r['sep']:.3f}", f"{r['mask_share']:.3f}", f"{r['agree']:.3f}", f"{r['spread']:.3f}", " ".join(f"{s:.3f}" for s in r["shares"])])
        print(n, pg, f"conf={conf:.2f} agree={r['agree']:.3f} spread={r['spread']:.3f} maxd={r['max_d']:.3f} margin={r['margin']:.3f} compact={r['compact']:.3f} sep={r['sep']:.3f}",
              " ".join(f"{s:.3f}" for s in r["shares"]))
        # debug overlay: label map recoloured with the website hex colours (derived image, git-ignored folder)
        lb = r["lblimg"]
        dbg = np.full(lb.shape + (3,), 235, np.uint8)
        inv = {r["perm"][j]: j for j in range(4)}
        for c, j in inv.items():
            dbg[lb == c] = hex_to_rgb(plates[n][j])
        a = np.asarray(img)[: lb.shape[0]]
        both = np.concatenate([a, dbg], axis=1)
        Image.fromarray(both).resize((both.shape[1] // 2, both.shape[0] // 2)).save(os.path.join(PAGES, f"dbg{n}.png"))
    if not sys.argv[1:]:
        with open(OUT_CSV, "w", newline="", encoding="utf8") as f:
            w = csv.writer(f)
            w.writerow(["plate", "color_index", "hex", "area_share", "pdf_page", "confidence"])
            w.writerows(rows)
        with open(DIAG_CSV, "w", newline="", encoding="utf8") as f:
            w = csv.writer(f)
            w.writerow(["plate", "pdf_page", "status", "conf", "mean_d", "max_d", "margin", "compact", "sep", "mask_share", "agree", "spread", "shares"])
            w.writerows(diag)


if __name__ == "__main__":
    main()
