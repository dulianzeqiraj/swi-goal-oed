"""ROOT-GO, proof of concept: where is a saline body rooted?

usage: python root_poc.py [n_truths] [workers] [seed]        -> res/root_poc.json

The synthetic coastal section of HYPOTHESIS-GO (../hipoteza_go/hip_core.py). For a truth (hydraulic parameters and
source strengths drawn in their intervals) the steady chloride field is the sum of the tagged fields of five saline
sources: the sea (enters through the sea face), the lagoon (leaks through the top near the coast), an anthropogenic
load (flux through the top), deep water (flux through the base) and legacy salinity (released inside the aquifer).
Two rules are applied to an image of the field.
  - 'touch': for a point p, the connected set of cells whose chloride is at least that of p (less a margin for the
    noise), and the source boundaries that this set touches. This is Proposition 3 read literally.
  - 'ascent': every cell is given to the local maximum that steepest ascent reaches (the basins of the superlevel-set
    filtration); maxima whose persistence is below a threshold are merged into their higher neighbour. The root of a
    point is the place of the maximum of its basin: the sea face, the top (lagoon or surface), the base, or the
    interior ('none', which Proposition 3 reserves for an internal source).
No field data are used."""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hipoteza_go'))
import hip_core as H  # noqa: E402

SRC = ['MS', 'LG', 'AN', 'RS', 'DB']
ROOT = {'MS': 'sea', 'LG': 'lagoon', 'AN': 'surface', 'DB': 'base', 'RS': 'none'}
KEY = {'MS': 'W_MS', 'LG': 'W_LG', 'AN': 'G_AN', 'RS': 'G_RS', 'DB': 'G_DB'}
CL_MIN = 250.0                     # mg/L: points below are not classified
CASES = [('clean image', 0.0, 1), ('noise 10%', 0.10, 1), ('noise 30%', 0.30, 1), ('coarse image, noise 10%', 0.10, 2)]
MARGIN = 2.0                       # 'touch': the level is lowered by MARGIN standard deviations of the noise
PERSIST = 1.0                      # 'ascent': maxima below PERSIST standard deviations of the noise are merged
P_CLEAN = 0.02                     # the same threshold for a clean image (natural logarithm of chloride)


def strengths(rng):
    return dict(MS=rng.uniform(19500, 21500), LG=rng.uniform(7800, 19350), FW=rng.uniform(10, 25),
                AN=0.0 if rng.uniform() < 0.3 else rng.uniform(0.03, 0.2),
                RS=0.0 if rng.uniform() < 0.3 else rng.uniform(0.003, 0.02),
                DB=0.0 if rng.uniform() < 0.5 else rng.uniform(0.2, 1.0))


def zones(nz, nx, f):
    """Boundary cells of every root on an image coarsened by the factor f (f x 2f blocks in z and x)."""
    xc = (np.arange(nx) + 0.5) * H.L / nx
    Z = {k: np.zeros((nz, nx), bool) for k in ('sea', 'lagoon', 'surface', 'base')}
    Z['sea'][:, 0] = True
    Z['lagoon'][0, (xc >= H.ZONES['lagoon'][0]) & (xc <= H.ZONES['lagoon'][1])] = True
    Z['surface'][0, (xc >= H.ZONES['an'][0]) & (xc <= H.ZONES['an'][1])] = True
    Z['base'][-1, (xc >= H.ZONES['db'][0]) & (xc <= H.ZONES['db'][1])] = True
    return Z


def nearest_root(nz, nx):
    """Baseline: the nearest source zone on the section scaled to a unit square (legacy: its release zone)."""
    xc = (np.arange(nx) + 0.5) / nx; zc = (np.arange(nz) + 0.5) / nz
    X, Zz = np.meshgrid(xc, zc)

    def box(x0, x1, z0, z1):
        dx = np.maximum(0, np.maximum(x0 - X, X - x1)); dz = np.maximum(0, np.maximum(z0 - Zz, Zz - z1))
        return np.hypot(dx, dz)
    L, B = H.L, H.B
    d = {'sea': X, 'lagoon': box(H.ZONES['lagoon'][0] / L, H.ZONES['lagoon'][1] / L, 0, 0),
         'surface': box(H.ZONES['an'][0] / L, H.ZONES['an'][1] / L, 0, 0),
         'base': box(H.ZONES['db'][0] / L, H.ZONES['db'][1] / L, 1, 1),
         'none': box(H.ZONES['rs'][0] / L, H.ZONES['rs'][1] / L, H.ZONES['rs'][2] / B, H.ZONES['rs'][3] / B)}
    names = list(d)
    return np.array(names)[np.argmin(np.stack([d[k] for k in names]), axis=0)]


def basins(v, thr):
    """Basin of every cell under steepest ascent with merging of maxima of persistence below thr (union-find over
    the cells in decreasing order). Returns the flat index of the maximum of the basin of every cell."""
    nz, nx = v.shape
    flat = v.ravel(); order = np.argsort(-flat, kind='stable')
    parent = -np.ones(flat.size, int); top = np.zeros(flat.size, int)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for c in order:
        j, i = divmod(int(c), nx)
        nb = [n for n in ((j - 1) * nx + i if j > 0 else -1, (j + 1) * nx + i if j < nz - 1 else -1,
                          j * nx + i - 1 if i > 0 else -1, j * nx + i + 1 if i < nx - 1 else -1) if n >= 0 and parent[n] >= 0]
        if not nb:
            parent[c] = c; top[c] = c
            continue
        hi = max(nb, key=lambda n: flat[n])                       # steepest ascent
        r = find(hi); parent[c] = r
        for n in nb:
            q = find(n)
            if q == r:
                continue
            lo_, hi_ = (q, r) if flat[top[q]] < flat[top[r]] else (r, q)
            if flat[top[lo_]] - flat[c] < thr:                    # a maximum of low persistence: merge it
                parent[lo_] = hi_; r = find(c)
    return np.array([top[find(c)] for c in range(flat.size)]).reshape(nz, nx)


def root_of(idx, nz, nx, Z, tol=0):
    """Place of a maximum; tol cells of tolerance at the boundary (a smoothed image shifts a maximum by a cell)."""
    j, i = divmod(int(idx), nx)
    if i <= tol:
        return 'sea'
    if j <= tol:
        return 'lagoon' if Z['lagoon'][0, i] else 'surface'
    if j >= nz - 1 - tol:
        return 'base'
    return 'none'


def coarsen(a, f):
    if f == 1:
        return a
    nz, nx = a.shape
    return a.reshape(nz // f, f, nx // (2 * f), 2 * f).mean(axis=(1, 3))


def one(seed):
    rng = np.random.default_rng(seed)
    th = H.draw_theta(rng, 1)[0]
    s = H.section_of(th)
    for (m, beta, maxit) in ((8, 0.5, 250), (20, 0.2, 300)):
        s.solve_steady(m=m, beta=beta, maxit=maxit)
        if s.dc < 1e-6:
            break
    if s.dc >= 1e-6:
        return dict(seed=seed, ok=False)
    tg = s.tagged(); S = strengths(rng)
    parts = {k: (S[k] * tg[KEY[k]]).reshape(H.NZ, H.NX) for k in SRC}
    c = sum(parts.values()) + S['FW'] * tg['W_FW'].reshape(H.NZ, H.NX)
    out = dict(seed=seed, ok=True, rs=bool(S['RS'] > 0), cases={})
    for name, sig, f in CASES:
        img = coarsen(c, f); P = {k: coarsen(v, f) for k, v in parts.items()}
        nz, nx = img.shape
        noisy = img * np.exp(sig * rng.standard_normal(img.shape))
        Z = zones(nz, nx, f); near = nearest_root(nz, nx)
        dom = np.array(SRC)[np.argmax(np.stack([P[k] for k in SRC]), axis=0)]
        share = np.max(np.stack([P[k] for k in SRC]), axis=0) / np.maximum(img, 1e-9)
        logv = np.log(np.maximum(noisy, 1.0))
        if sig > 0:
            logv = ndimage.gaussian_filter(logv, 1.0, mode='nearest')
        bas = basins(logv, max(P_CLEAN, PERSIST * sig))
        tol = 1 if sig > 0 else 0
        body = []                                   # one record per saline body: source at its core, its root, size
        for m in np.unique(bas):
            jm, im = divmod(int(m), nx)
            if img[jm, im] < CL_MIN:
                continue
            body.append([str(dom[jm, im]), root_of(m, nz, nx, Z, tol), int(np.sum((bas == m) & (img >= CL_MIN))),
                         float(share[jm, im])])
        rec = []
        step = (2, 4) if f == 1 else (1, 2)
        for j in range(0, nz, step[0]):
            for i in range(0, nx, step[1]):
                if img[j, i] < CL_MIN or share[j, i] < 0.5:
                    continue
                lab, _ = ndimage.label(noisy >= noisy[j, i] * np.exp(-MARGIN * sig))
                comp = lab == lab[j, i]
                T = sorted(k for k in Z if np.any(comp & Z[k]))
                rec.append([str(dom[j, i]), '+'.join(T) if T else 'none', str(near[j, i]), root_of(bas[j, i], nz, nx, Z, tol),
                            float(img[j, i])])
        out['cases'][name] = dict(points=rec, bodies=body)
    return out


def main():
    nt = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2027
    t0 = time.time()
    with Pool(nw) as pool:
        res = pool.map(one, [seed + 1000 * k for k in range(nt)])
    json.dump(dict(cases=[c[0] for c in CASES], margin=MARGIN, persist=PERSIST, cl_min=CL_MIN, runs=res), open(os.path.join(HERE, 'res', 'root_poc.json'), 'w'))
    print('done', f'{time.time() - t0:.0f}s', 'converged', sum(r['ok'] for r in res), 'of', nt)


if __name__ == '__main__':
    main()
