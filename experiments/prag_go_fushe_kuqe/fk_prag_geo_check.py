"""Re-check of the 5-well results of fk_prag_geo.py with a 4x larger inner ensemble (as fk_check5.py).

With 12 000 inner realizations the re-weighting estimate of the exact EIG of the best 5-well designs
rests on an effective sample of about 20, where it is biased upwards. This script re-estimates, with
48 000 inner (and the same 2 000 outer) realizations, the exact EIG of: the 40 best 5-well designs of
each goal under the 12 000 ensemble, and the best design of every criterion. Percentages are
relative to the best of these designs under the 48 000 ensemble.
Run: python3 fk_prag_geo_check.py [base|rho805]  (after fk_prag_geo.py; ~6 min, ~8 GB RAM)
"""
import sys, json, time
import numpy as np
import fk_prag_geo as P

PRIOR = sys.argv[1] if len(sys.argv) > 1 else 'base'
N_INNER = 48000

if __name__ == '__main__':
    t0 = time.time()
    R = json.load(open(f'{P.OUT}/prag_{PRIOR}.json'))
    Z = np.load(f'{P.OUT}/prag_{PRIOR}_d5.npz')
    D, LIN, EX = Z['D'], Z['LIN'], Z['EX']
    sel = set()
    for gk in range(3):
        sel |= set(np.argsort(-EX[:, gk])[:40].tolist())
    for j in range(len(P.NAMES)):
        sel.add(int(LIN[:, j].argmax()))
    sel = sorted(sel)
    inner = P.ensemble(N_INNER, 21000); outer = P.ensemble(2000, 5000)       # same outer seeds as fk_prag_geo.py
    print(f'ensembles {time.time() - t0:.0f}s')
    NC, IA, IB, IR = P.NC, P.IA, P.IB, P.IR
    T = R['area_threshold_km2']
    QIN = np.stack([inner[:, IA] < P.HC, np.minimum(inner[:, IA], inner[:, IB]) < P.HC, inner[:, IR] > T], 1).astype(np.float64)
    P.P0 = QIN.mean(0); P.QW = QIN.astype(np.float32)
    rng = np.random.default_rng(11)
    y = outer[:, :NC] + P.SN * rng.standard_normal(outer[:, :NC].shape)
    P.DK = np.empty((NC, y.shape[0], N_INNER), dtype=np.float32)
    for k in range(NC):
        P.DK[k] = (y[:, k, None] - inner[None, :, k]) ** 2
    EXc = np.array([P.exact_one(tuple(D[i])) for i in sel])
    print(f'{len(sel)} designs re-estimated {time.time() - t0:.0f}s')
    out = {'prior': PRIOR, 'n_inner': N_INNER, 'n_designs': len(sel), 'P0': P.P0.tolist(), 'goals': {}}
    for gk, gn in enumerate(P.GOALS):
        ex = EXc[:, gk]; b = int(ex.argmax())
        G = {'best': {'wells': P.ids[list(D[sel[b]])].tolist(), 'eig': float(ex[b]), 'ess': float(EXc[b, 3])}, 'criteria': {}}
        for j, nm in enumerate(P.NAMES):
            k = sel.index(int(LIN[:, j].argmax()))
            G['criteria'][nm] = {'wells': P.ids[list(D[sel[k]])].tolist(), 'eig': float(ex[k]), 'pct_best': float(100 * ex[k] / ex[b])}
        out['goals'][gn] = G
        print(f'{gn}: best {G["best"]["wells"]} {ex[b]:.3f} nats (ESS {EXc[b, 3]:.0f}); '
              + ', '.join(f'{nm} {G["criteria"][nm]["pct_best"]:.0f}%' for nm in P.NAMES))
    json.dump(out, open(f'{P.OUT}/prag_{PRIOR}_check5.json', 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s')
