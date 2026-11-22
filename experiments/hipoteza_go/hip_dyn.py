"""H6: pumping as a bilinear input.  Does the seawater that reaches a well under ANY admissible pumping history stay
between the steady states of the lowest and the highest admissible pumping?

For one set of hydraulic parameters the coupled system is marched (implicit Euler, half-year steps) through random
pumping histories Q(t) in [Qmin, Qmax]: piecewise constant with random levels and switching times, and the two
bang-bang histories that the auxiliary-function bound of the note singles out (the bound is affine in Q, so only the
vertices Qmin and Qmax enter its conditions).  The seawater fraction W_MS at the samples is compared with its steady
values for Qmin and Qmax.  This is the Monte Carlo side of the certified bound (lower bounds from trajectories); the
certificate itself needs a reduced model and sum-of-squares optimisation and is not computed here.
Writes res/dyn.json.  usage: python hip_dyn.py [histories] [workers]"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import hip_core as H

HERE = os.path.dirname(os.path.abspath(__file__))
TH = dict(Kx=110.0, aniso=0.04, Qin=3.2, rQ=0.35, vL=1.5e-4, sL=0.6, aL=40.0, aT=1.5)
RQ = (0.15, 0.55)                      # admissible pumping as a fraction of the inland inflow
YEARS = 150.0
REC = [float(365.25 * y) for y in np.arange(5.0, YEARS + 0.1, 5.0)]


def steady(rq):
    th = dict(TH, rQ=rq)
    s = H.section_of(th)
    for (m, beta, maxit) in ((8, 0.5, 250), (20, 0.2, 450), (8, 0.5, 800)):
        s.solve_steady(m=m, beta=beta, maxit=maxit)
        if s.dc < 1e-6:
            break
    return s


def history(seed):
    """Piecewise-constant pumping fractions; seed -1 and -2 are the two constant extremes after a start at the other
    extreme, seeds -3 and -4 are bang-bang with 20-year and 40-year periods."""
    rng = np.random.default_rng(abs(seed) + 17)
    if seed == -1:
        return [(0.0, RQ[1])]
    if seed == -2:
        return [(0.0, RQ[0])]
    if seed in (-3, -4):
        per = 20.0 if seed == -3 else 40.0
        return [(k * per, RQ[1] if k % 2 == 0 else RQ[0]) for k in range(int(YEARS / per) + 1)]
    t, out = 0.0, []
    while t < YEARS:
        out.append((t, float(rng.uniform(*RQ))))
        t += float(rng.uniform(4.0, 25.0))
    return out


def run(seed):
    hist = history(seed)
    start_rq = RQ[0] if seed != -2 else RQ[1]            # start from the steady state of the opposite extreme
    s = steady(start_rq)
    tg = s.tagged()
    cells = s.screens()

    def qw(t_days):
        y = t_days / 365.25
        r = hist[0][1]
        for (t0, v) in hist:
            if y >= t0 - 1e-9:
                r = v
        return r * TH['Qin']
    out = s.march(s.c, tg, qw, REC[-1], dt=182.625, inner=3, record=REC)
    W = np.array([s.at(out[r][1]['W_MS'], cells) for r in REC])
    toe = []
    for r in REC:
        base = out[r][0].reshape(s.nz, s.nx)[-1]
        k = np.flatnonzero(base >= 0.02)
        toe.append(0.0 if len(k) == 0 else float(s.xc[k.max()] + 0.5 * s.dx))
    return dict(seed=seed, hist=hist, W=W.tolist(), toe=toe)


def main(n_hist=20, workers=4):
    t0 = time.time()
    lo, hi = steady(RQ[0]), steady(RQ[1])
    cells = lo.screens()
    Wlo = lo.at(lo.tagged()['W_MS'], cells); Whi = hi.at(hi.tagged()['W_MS'], cells)
    seeds = [-1, -2, -3, -4] + list(range(n_hist))
    with Pool(workers) as pool:
        res = pool.map(run, seeds, chunksize=1)
    Wall = np.array([r['W'] for r in res])                       # histories x times x samples
    worst_hi = float(np.max(Wall.max(axis=(0, 1)) - Whi))        # largest excess over the steady state of Qmax
    worst_lo = float(np.max(Wlo - Wall.min(axis=(0, 1))))        # largest shortfall below the steady state of Qmin
    out = dict(theta=TH, rq=RQ, years=YEARS, rec_years=[r / 365.25 for r in REC], W_lo=Wlo.tolist(), W_hi=Whi.tolist(),
               toe_lo=lo.toe(0.02), toe_hi=hi.toe(0.02), runs=res, worst_excess=worst_hi, worst_shortfall=worst_lo,
               seconds=time.time() - t0)
    json.dump(out, open(os.path.join(HERE, 'res', 'dyn.json'), 'w'), indent=1)
    print(f'{len(seeds)} histories in {out["seconds"]:.0f}s; toe(2%) steady: {lo.toe(0.02):.0f} m at Qmin, {hi.toe(0.02):.0f} m at Qmax; '
          f'largest excess over the steady state of Qmax {worst_hi:.2e}; largest shortfall below that of Qmin {worst_lo:.2e}')


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
