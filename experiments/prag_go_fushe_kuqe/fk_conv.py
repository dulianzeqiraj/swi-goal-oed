"""Convergence check of the re-weighting estimator on the 3-well designs: the designs that matter
(top 5 per goal and each criterion's pick) are re-estimated on two independent halves of the
inner ensemble with fresh outer noise."""
import sys, json
import numpy as np

OUT = sys.argv[1]
SN, HC, AREA_T = 0.2, 1.0, 100.0
NAMES = ['area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS']
E = np.load(f'{OUT}/ens.npz'); R = np.load(f'{OUT}/d3.npz'); M = json.load(open(f'{OUT}/meta.json'))
inner, outer = E['inner'], E['outer']; D, EX, LIN = R['D'], R['EX'], R['LIN']
CAND, iA, iB = np.array(M['CAND']), M['iA'], M['iB']


def h(p):
    p = np.clip(p, 0.0, 1.0)
    return -(np.where(p > 0, p * np.log(np.where(p > 0, p, 1.0)), 0.0) + np.where(p < 1, (1 - p) * np.log(np.where(p < 1, 1 - p, 1.0)), 0.0))


def eig(d, idx, seed):
    cols = CAND[list(d)]
    gi = inner[idx][:, cols]
    q = np.stack([inner[idx, iA] < HC, np.minimum(inner[idx, iA], inner[idx, iB]) < HC, inner[idx, 32] > AREA_T], 1).astype(float)
    rng = np.random.default_rng(seed)
    y = outer[:, cols] + SN * rng.standard_normal((len(outer), len(cols)))
    S = ((y[:, None, :] - gi[None, :, :]) ** 2).sum(-1)
    S -= S.min(1, keepdims=True)
    w = np.exp(-np.minimum(S / (2 * SN * SN), 80.0))
    p = (w @ q) / w.sum(1, keepdims=True)
    return h(q.mean(0)) - h(p).mean(0)


half1, half2 = np.arange(0, 6000), np.arange(6000, 12000)
res = {}
for gk, gname in enumerate(['rA', 'rAB', 'rArea']):
    order = np.argsort(-EX[:, gk])
    picks = {f'top{r + 1}': int(order[r]) for r in range(5)}
    for j, nm in enumerate(NAMES):
        picks[nm] = int(np.argmax(LIN[:, j]))
    rows = {nm: (float(EX[i, gk]), float(eig(D[i], half1, 101)[gk]), float(eig(D[i], half2, 202)[gk])) for nm, i in picks.items()}
    b0 = max(r[0] for r in rows.values()); b1 = max(r[1] for r in rows.values()); b2 = max(r[2] for r in rows.values())
    res[gname] = {nm: [r[0] / b0, r[1] / b1, r[2] / b2] for nm, r in rows.items()}
    print(f'== {gname}')
    for nm, r in rows.items():
        print(f'  {nm:8s} full {r[0]:.4f} ({r[0] / b0:.3f})  half1 {r[1]:.4f} ({r[1] / b1:.3f})  half2 {r[2]:.4f} ({r[2] / b2:.3f})')
json.dump(res, open(f'{OUT}/conv.json', 'w'), indent=1)
