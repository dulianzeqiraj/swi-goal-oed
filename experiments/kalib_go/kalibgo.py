"""KALIB-GO: learning rate eta calibrated on the goal (toe of the saltwater interface).

General-posterior calibration (bootstrap coverage matching) applied to the goal quantity rather than
to the parameters: for each eta on a grid, the eta-posterior 90% interval of the toe is recomputed on
B bootstrap resamples, and eta* is the largest eta whose bootstrap intervals contain the full-data
toe estimate at least 90% of the time. Also BayesBag (bagged eta=1 posterior) as a comparator.
Builds on safego.py (model, conjugate eta-posterior, SafeBayes).
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'safe_go'))   # safego.py, safego_exp.py
import safego as S

ETAS = S.ETAS                      # 1 ... 1/64
B_BOOT = 60                        # bootstrap resamples
NS_BOOT = 300                      # posterior draws per bootstrap interval
LEVEL = 0.90

def stats(Bm, y, w):
    return (Bm * w[:, None]).T @ Bm, Bm.T @ (w * y), y @ (w * y)

def goal_draws(St, prior, n, eta, rng, ns):
    """toe draws from the BMA eta-posterior given sufficient statistics St=(S, r, yy)."""
    Sm, r, yy = St
    logev, z, Linv, an, bn = prior.post(Sm, r, yy, n, eta)
    k = Sm.shape[0]
    w = S.model_weights(logev)
    ps = rng.choice(k, size=ns, p=w)
    s2 = bn[ps] / rng.gamma(an, 1.0, size=ns)
    phig = np.empty((ns, len(S.XG)))
    for p in np.unique(ps):
        sel = np.where(ps == p)[0]
        Lp = np.linalg.inv(Linv[:p + 1, :p + 1])
        mp = np.linalg.solve(Lp.T, z[:p + 1])
        eps = rng.standard_normal((len(sel), p + 1))
        beta = mp + np.sqrt(s2[sel])[:, None] * np.linalg.solve(Lp.T, eps.T).T
        phig[sel] = beta @ S.BG[:, :p + 1].T
    return S.first_root(phig), w, bn / (an - 1.0 + 1e-12)

def kalib(Bm, y, prior, rng, etas=ETAS, nb=B_BOOT, ns=NS_BOOT, level=LEVEL):
    """returns eta*, bootstrap coverage per eta, and BayesBag draws (eta=1)."""
    n = len(y)
    full = stats(Bm, y, np.ones(n))
    center = np.array([np.median(goal_draws(full, prior, n, e, rng, 1000)[0]) for e in etas])
    hits = np.zeros(len(etas))
    bag = []
    a = (1 - level) / 2
    for b in range(nb):
        c = rng.multinomial(n, np.ones(n) / n).astype(float)
        St = stats(Bm, y, c)
        for j, e in enumerate(etas):
            t, _, _ = goal_draws(St, prior, n, e, rng, ns)
            lo, hi = np.quantile(t, [a, 1 - a])
            hits[j] += lo <= center[j] <= hi
            if j == 0:
                bag.append(t)
    cov = hits / nb
    ok = np.where(cov >= level)[0]
    j = ok[0] if len(ok) else len(etas) - 1      # etas are decreasing: first ok = largest eta
    eta = etas[j]
    if 0 < j and cov[j] > cov[j - 1]:            # interpolate the crossing in log(eta)
        t = (level - cov[j - 1]) / (cov[j] - cov[j - 1])
        eta = np.exp(np.log(etas[j - 1]) + t * (np.log(etas[j]) - np.log(etas[j - 1])))
    return float(eta), cov, np.concatenate(bag)
