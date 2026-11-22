"""T1R: rain-conditional calibration. The simulated aquifers of the calibration set and the field aquifer share one
observed rain record: the unknowns are drawn from the prior given that rain. The cases are then exchangeable given the
rain, so the guarantees of T1 hold for that very record. Two records from the rain law, a dry and a wet 64-week window
(the 3rd driest and 3rd wettest of 40 draws), scenario B (4 loggers).

usage: python gar_rainc.py   (writes res/gar_rainc.json)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gar_exp as G  # noqa: E402

M = G.M


def pick_records(seed=41, k=40):
    rng = np.random.default_rng(seed)
    recs = [G.daily_rain(rng) for _ in range(k)]
    tot = np.array([r[M.SPIN:].sum() for r in recs])
    o = np.argsort(tot)
    return {'dry': (recs[o[2]], float(tot[o[2]])), 'wet': (recs[o[-3]], float(tot[o[-3]]))}, float(np.median(tot))


def main():
    t0 = time.time()
    recs, med = pick_records()
    out = dict(median_window_rain_mm=med, records={})
    for j, (name, (Pd, tot)) in enumerate(recs.items()):
        G.daily_rain = lambda rng, Pd=Pd: Pd.copy()          # every case sees the same observed rain
        pool = G.run_cases(G.Bed(), 400, 61 + j, exact=True)
        rng = np.random.default_rng(71 + j)
        res = {}
        for k in G.CH + ('kappa',):
            sp = G.split_eval(pool, k, 200, 1000, rng)
            lam, q = G.crc_lambda(G.loss_matrix(pool, k)), G.cp_quantile(G.sup_scores(pool, k))
            s = float(np.mean([np.mean(c['s'][k]) for c in pool]))
            res[k] = dict(crc_risk=sp['crc_risk'], sup_cover=sp['sup_cover'], crc_width=sp['crc_width'],
                          halfwidth_crc=lam * s, halfwidth_sup=q * s, units=G.UNITS[k])
        out['records'][name] = dict(window_rain_mm=tot, mean_f=float(np.mean(G.filtered(Pd, M.TAU_V))), targets=res)
        print(f'{name}: {tot:.0f} mm in the window (median {med:.0f}); ' + ' | '.join(
            f'{k} CRC {v["crc_risk"]:.3f} sup {v["sup_cover"]:.3f} hw {v["halfwidth_crc"]:.3f}' for k, v in res.items()),
            flush=True)
    with open(os.path.join(G.RES, 'gar_rainc.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
