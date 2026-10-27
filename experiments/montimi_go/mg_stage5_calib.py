"""MONTIMI-GO stage 5: calibration cases for the margin. C pairs (layout, design draw) drawn at random; for each, the
critical rate on the full assembly. The cheap assemblies' critical rates for the same pairs are read from stage 3.
Output res/calib.npz (layout index, draw index, Q on the full assembly)."""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M
import mg_setup as S
from mg_stage3_place import q_crit

RES = os.path.join(HERE, 'res')
C = 40


def task(args):
    d, lis, guesses = args
    P = dict(S.DES[d])
    y0, yp, zp, _ = S.present_state(S.GF, P, {})
    out = []
    for li, gs in zip(lis, guesses):
        L = S.LAYOUTS[li]
        q, n = q_crit(lambda Q: S.forecast(S.GF, P, {}, yp, zp, L, Q)[0], M.EPS_LIM, gs if np.isfinite(gs) and gs > 0 else 5.0)
        out.append((li, d, q, n))
    return out


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rng = np.random.default_rng(99)
    pairs = [(int(rng.integers(len(S.LAYOUTS))), int(rng.integers(len(S.DES)))) for _ in range(C)]
    try:
        QG = np.load(os.path.join(RES, 'qcrit_G_DES.npz'))['Q']
    except Exception:
        QG = None
    by_draw = {}
    for li, d in pairs:
        by_draw.setdefault(d, []).append(li)
    tasks = [(d, lis, [QG[d, li] if QG is not None else 5.0 for li in lis]) for d, lis in by_draw.items()]
    res = []
    with Pool(workers) as pool:
        for out in pool.imap_unordered(task, tasks):
            res += out
            print(out, flush=True)
    res = np.array(res)
    np.savez(os.path.join(RES, 'calib.npz'), layout=res[:, 0].astype(int), draw=res[:, 1].astype(int), QF=res[:, 2], nev=res[:, 3])


if __name__ == '__main__':
    main()
