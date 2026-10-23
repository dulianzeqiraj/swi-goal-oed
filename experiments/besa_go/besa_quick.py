"""BESA-GO quick check: every estimator and both checks on one simulated data set per scenario and sample size
(n = 1500, 6000, 100 000). About 3 minutes; prints one line per data set."""
import time, numpy as np
import besa_model as M, besa_est as B
for name, kw in [('correct', dict(cop=M.COMMON)), ('pumpdep', dict(cop=M.PUMPDEP)), ('wrongprop', dict(cop=M.COMMON, past=M.WRONGPROP)),
                 ('both', dict(cop=M.PUMPDEP, past=M.WRONGPROP)), ('skewdry', dict(cop=dict(rho1=(0.5, 0.5), rho2=(0.55, 0.55)), copula='skewdry'))]:
    for n in (1500, 6000, 100000):
        t0 = time.time()
        D = M.simulate(n, np.random.default_rng(11), **kw)
        o = B.besa(D)
        print(f"{name:9s} n={n:6d} [{time.time()-t0:5.1f}s] " + ' '.join(f"{m}:{o[m][0]:.3f}/{o[m][1]:.3f}" for m in B.METHODS) + f"  T={o["test"][0]:.1f} p={o["test"][1]:.3f} Tf={o["test"][2]:.1f} LR={o["test"][4]:.1f} pLR={o["test"][5]:.3f} br={o["test"][6]}", flush=True)
