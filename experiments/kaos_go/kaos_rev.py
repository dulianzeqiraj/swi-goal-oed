"""Finite-size study of the Darcy coefficient: periodic cells of n randomly placed cylinders (solid fraction about 0.2),
Stokes regime; many realisations per size.  Output: res/rev.json (K / a^2 per realisation)."""
import json, sys, time
import numpy as np
import lbm

A, NU, G = 12.0, 1 / 6, 1e-6
PLAN = ((4, 96, 64), (16, 192, 32), (64, 384, 12))            # (grains, cell side, realisations)
out = dict(a=A, nu=NU, g=G, sizes=[])
t0 = time.time()
for n, L, m in PLAN:
    ks, cs = [], []
    for seed in range(1, m + 1):
        pts = lbm.random_disks(L, L, n, A, 4.0, np.random.default_rng(1000 * n + seed))
        solid = lbm.disks_mask(L, L, pts, A)
        f, fn = lbm.init(solid)
        acc = np.zeros((7,) + solid.shape)
        u_old, steps = 0.0, 0
        while steps < 120000:
            f, fn, s = lbm.advance(f, fn, solid, NU, G, 0.0, 500, acc)
            steps += 500
            if steps >= 4000 and abs(s[0] - u_old) < 1e-8 * abs(s[0]):
                break
            u_old = s[0]
        ks.append(NU * s[0] / G / A ** 2); cs.append(float(solid.mean()))
        print(n, seed, steps, round(ks[-1], 5), round(cs[-1], 4), round(time.time() - t0), flush=True)
    out['sizes'].append(dict(n=n, L=L, K=ks, solid=cs))
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
