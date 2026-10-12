"""Re-estimate the key 5-well designs with a 4x larger inner ensemble (48 000 realizations: the
12 000 of stage 1 plus 36 000 new ones) and fresh outer noise. Low effective sample sizes bias the
re-weighting estimator upwards, so this checks that the 5-well percentages are not an artefact."""
import sys, os, json, time
import numpy as np
from multiprocessing import Pool
import fk_ens as FE

OUT = sys.argv[1]
SN, HC, AREA_T = 0.2, 1.0, 100.0
NAMES = ['area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS']


def h(p):
    p = np.clip(p, 0.0, 1.0)
    return -(np.where(p > 0, p * np.log(np.where(p > 0, p, 1.0)), 0.0) + np.where(p < 1, (1 - p) * np.log(np.where(p < 1, 1 - p, 1.0)), 0.0))


if __name__ == '__main__':
    t0 = time.time()
    f = f'{OUT}/ens_extra.npz'
    if not os.path.exists(f):
        np.savez(f, inner=FE.ensemble(36000, 20000))
    E = np.load(f'{OUT}/ens.npz'); X = np.load(f)['inner']
    inner = np.vstack([E['inner'], X]); outer = E['outer']
    print(f'inner {len(inner)} ({time.time() - t0:.0f}s)')
    M = json.load(open(f'{OUT}/meta.json')); CAND, iA, iB = np.array(M['CAND']), M['iA'], M['iB']; ids = np.array(M['ids'])
    R5 = np.load(f'{OUT}/d5.npz'); D5, LIN5 = R5['D'], R5['LIN']
    picks = {'published': tuple(D5[int(R5['pub'])])}
    for j, nm in enumerate(NAMES):
        picks[nm] = tuple(D5[int(LIN5[:, j].argmax())])
    for k, g in enumerate(['rA', 'rAB', 'rArea']):
        picks['best_' + g] = tuple(int(v) for v in R5['gbest'][k])
    q = np.stack([inner[:, iA] < HC, np.minimum(inner[:, iA], inner[:, iB]) < HC, inner[:, 32] > AREA_T], 1).astype(np.float32)
    rng = np.random.default_rng(404)
    Y = outer + SN * rng.standard_normal(outer.shape)
    out = {}
    for nm, d in picks.items():
        cols = CAND[list(d)]
        S = np.zeros((len(outer), len(inner)), np.float32)
        for c in cols:
            S += (Y[:, c, None].astype(np.float32) - inner[None, :, c].astype(np.float32)) ** 2
        S -= S.min(1, keepdims=True); S *= np.float32(-1 / (2 * SN * SN)); np.maximum(S, -80, out=S); np.exp(S, out=S)
        sw = S.sum(1, dtype=np.float64); p = (S @ q).astype(np.float64) / sw[:, None]
        ess = float((sw ** 2 / np.einsum('ij,ij->i', S, S)).mean())
        out[nm] = {'design': [str(ids[c]) for c in cols], 'eig': (h(q.mean(0)) - h(p).mean(0)).tolist(), 'ess': ess}
    for k, g in enumerate(['rA', 'rAB', 'rArea']):
        b = max(v['eig'][k] for v in out.values())
        for v in out.values():
            v.setdefault('pct', {})[g] = v['eig'][k] / b
    json.dump(out, open(f'{OUT}/check5.json', 'w'), indent=1)
    for nm, v in out.items():
        print(f"{nm:10s} {' '.join(v['design']):26s} ESS {v['ess']:7.0f}  " + '  '.join(f"{g} {v['pct'][g]:.3f}" for g in ['rA', 'rAB', 'rArea']))
    print(f'done {time.time() - t0:.0f}s')
