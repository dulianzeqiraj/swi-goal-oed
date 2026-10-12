"""Convergence check of the re-weighting EIG estimator: recompute the exact EIG of the designs
that matter (top designs and every criterion's pick) on independent halves of the inner ensemble
and with fresh outer noise, and report whether the ranking survives."""
import sys
import numpy as np

OUT = sys.argv[1]
TAU = 0.01
E = np.load(f'{OUT}/ens.npz'); R = np.load(f'{OUT}/designs_s0.01.npz')
inner, outer = E['inner'], E['outer']
D3, EX, LIN = R['D3'], R['EX'], R['LIN']
names = ['mass', 'meanAB', 'cA', 'pragAdjA', 'pragAdj', 'pragEns', 'pragNSA', 'pragNS', 'massEns']


def h(p):
    p = np.clip(p, 0.0, 1.0)
    return -(np.where(p > 0, p * np.log(np.where(p > 0, p, 1.0)), 0.0) + np.where(p < 1, (1 - p) * np.log(np.where(p < 1, 1 - p, 1.0)), 0.0))


def eig(d, idx_in, seed, s=0.01):
    gi = inner[idx_in][:, list(d)]
    q = np.stack([inner[idx_in, 32] > TAU, np.maximum(inner[idx_in, 32], inner[idx_in, 33]) > TAU], 1).astype(float)
    rng = np.random.default_rng(seed)
    y = outer[:, list(d)] + s * rng.standard_normal((len(outer), 3))
    S = ((y[:, None, :] - gi[None, :, :]) ** 2).sum(-1)
    S -= S.min(1, keepdims=True)
    w = np.exp(-S / (2 * s * s))
    p = (w @ q) / w.sum(1, keepdims=True)
    return h(q.mean(0)) - h(p).mean(0)


half1, half2 = np.arange(0, 6000), np.arange(6000, 12000)
for gk, gname in [(0, 'risk A'), (1, 'risk A or B')]:
    order = np.argsort(-EX[:, gk])
    picks = {'top%d' % (r + 1): order[r] for r in range(5)}
    for j, nm in enumerate(names):
        picks[nm] = int(np.argmax(LIN[:, j]))
    print(f'== {gname}')
    rows = []
    for nm, i in picks.items():
        e1 = eig(D3[i], half1, 101)[gk]; e2 = eig(D3[i], half2, 202)[gk]
        rows.append((nm, tuple(int(v) for v in D3[i]), EX[i, gk], e1, e2))
        print(f'  {nm:9s} {tuple(int(v) for v in D3[i])}  full {EX[i, gk]:.4f}  half1 {e1:.4f}  half2 {e2:.4f}')
    best1 = max(r[3] for r in rows); best2 = max(r[4] for r in rows)
    for nm, d, ex, e1, e2 in rows:
        if nm in names:
            print(f'  ratio {nm:9s} full {ex / EX[order[0], gk]:.3f}  half1 {e1 / best1:.3f}  half2 {e2 / best2:.3f}')
