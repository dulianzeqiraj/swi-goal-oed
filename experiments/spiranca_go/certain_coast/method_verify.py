"""CERTAIN-COAST Methodology, Section 5.7: anytime-valid verification of certified miss rates (synthetic test).

Adopted frontier method, not a new contribution: test supermartingales (e-processes) and Ville's inequality
(Ramdas et al. 2023; Vovk and Wang 2021; Arnold, Henzi and Ziegel 2023 for forecast calibration). The ledger of misses is
published every quarter (Dissemination Plan), so the rate is looked at many times; a fixed-sample Clopper-Pearson test
repeated at every look loses its error guarantee, an e-process keeps it at every look and lets evidence from several
alarms be pooled.

Each alarm k gives a sequence of exceedance events; x = 1 if the event was missed. For a certified rate a:
  detect a broken alarm   H0: p <= a,  E = sum_j pi_j prod (q_j/a)^x ((1-q_j)/(1-a))^(1-x),  q_j > a
  verify a good alarm     H0: p >= a,  same form with q_j < a
Both are nonnegative supermartingales under H0, so P(sup_n E_n >= 1/beta) <= beta (Ville). The average of the alarms'
e-processes is again one, which pools evidence across alarms.

usage: python method_verify.py [OUT_DIR]   (writes method_verify.json)"""
import json
import os
import sys

import numpy as np
from scipy.stats import beta as Beta, binom

A, BETA, K, NMAX, SIMS = 0.10, 0.05, 6, 100, 20000
Q_UP = np.array([0.15, 0.20, 0.30, 0.45])          # alternatives for a broken alarm (rate above a)
C_DN = np.array([0.0, 0.3])                        # alternatives for a good alarm: q = c * a, below a
PI_DN = np.array([0.5, 0.5])
Q_DN = C_DN * A


def eprocess(x, a, qs, pi=None):
    """x: (..., n) misses in order; returns E_n for n = 1..N along the last axis (mixture of likelihood ratios)."""
    pi = np.full(len(qs), 1 / len(qs)) if pi is None else pi
    cx = np.cumsum(x, axis=-1)
    n = np.arange(1, x.shape[-1] + 1)
    out = 0.0
    for q, w in zip(qs, pi):
        with np.errstate(divide='ignore', invalid='ignore'):
            lq = np.log(q / a) if q > 0 else -np.inf
            lr = np.where(cx > 0, cx * lq, 0.0) + (n - cx) * np.log((1 - q) / (1 - a))
        out = out + w * np.exp(lr)
    return out


def first_cross(E, level):
    hit = E >= level
    return np.where(hit.any(axis=-1), hit.argmax(axis=-1) + 1, np.inf)


def cp_upper(x, n, b=BETA):
    return np.where(x >= n, 1.0, Beta.ppf(1 - b, x + 1, np.maximum(n - x, 1e-12)))


def run(seed=3):
    rng = np.random.default_rng(seed)
    res = {}
    n = np.arange(1, NMAX + 1)

    # 1. calibrated alarms (p = a, the hardest case for the null), six alarms, looked at after every event
    x = (rng.random((SIMS, K, NMAX)) < A).astype(float)
    cx = np.cumsum(x, axis=-1)
    pval = binom.sf(cx - 1, n, A)                         # P(X >= x | n, a)
    naive_every = (pval < BETA).any(axis=(1, 2)).mean()
    looks = n % 10 == 0                                   # every tenth event, roughly quarterly
    naive_quarterly = (pval[..., looks] < BETA).any(axis=(1, 2)).mean()
    single_alarm_every = (pval[:, 0, :] < BETA).any(axis=1).mean()
    E = eprocess(x, A, Q_UP)
    pooled = (E.mean(axis=1) >= 1 / BETA).any(axis=1).mean()
    bonf = (E >= K / BETA).any(axis=(1, 2)).mean()
    res['false_alarm'] = dict(naive_every_event=float(naive_every), naive_quarterly=float(naive_quarterly),
                              naive_one_alarm_every_event=float(single_alarm_every),
                              eprocess_pooled=float(pooled), eprocess_per_alarm=float(bonf))

    # 2. one alarm broken (p = 2.5a), five calibrated: detection by NMAX events and median events to detection
    for p_bad in (0.20, 0.25):
        x = (rng.random((SIMS, K, NMAX)) < A).astype(float)
        x[:, 0, :] = (rng.random((SIMS, NMAX)) < p_bad)
        E = eprocess(x, A, Q_UP)
        tp = first_cross(E.mean(axis=1), 1 / BETA)
        ta = first_cross(E[:, 0, :], K / BETA)
        res[f'detect_{p_bad:.2f}'] = dict(pooled_power=float(np.isfinite(tp).mean()),
                                          pooled_median_events=float(np.median(tp[np.isfinite(tp)])),
                                          per_alarm_power=float(np.isfinite(ta).mean()),
                                          per_alarm_median_events=float(np.median(ta[np.isfinite(ta)])))

    # 2b. a common cause: all six alarms drift to p = 0.15 (pooling helps most here)
    x = (rng.random((SIMS, K, NMAX)) < 0.15).astype(float)
    E = eprocess(x, A, Q_UP)
    tp = first_cross(E.mean(axis=1), 1 / BETA)
    ta = first_cross(E, K / BETA).min(axis=1)
    res['detect_all_0.15'] = dict(pooled_power=float(np.isfinite(tp).mean()),
                                  pooled_median_events=float(np.median(tp[np.isfinite(tp)])),
                                  per_alarm_power=float(np.isfinite(ta).mean()),
                                  per_alarm_median_events=float(np.median(ta[np.isfinite(ta)])))

    # 3. verifying a good alarm: events needed until the rate a is verified
    for p_true in (0.0, 0.03):
        x = (rng.random((SIMS, 400)) < p_true).astype(float)
        E = eprocess(x, A, Q_DN, PI_DN)
        tv = first_cross(E, 1 / BETA)
        res[f'verify_p{p_true:.2f}'] = dict(median_events=float(np.median(tv[np.isfinite(tv)])),
                                            share_verified_by_100=float((tv <= 100).mean()))
    # events needed to verify with 0, 1, 2 misses: anytime-valid e-process vs one planned Clopper-Pearson look
    def need_e(a, x):
        for m in range(x + 1, 5000):
            E = sum(w * (c ** x if x else 1.0) * ((1 - c * a) / (1 - a)) ** (m - x) for c, w in zip(C_DN, PI_DN))
            if E >= 1 / BETA:
                return m

    def need_cp(a, x):
        for m in range(x + 1, 5000):
            if Beta.ppf(1 - BETA, x + 1, m - x) <= a:
                return m
    res['events_needed'] = {f'{a:.2f}': dict(eprocess=[need_e(a, x) for x in (0, 1, 2)],
                                             clopper_pearson=[need_cp(a, x) for x in (0, 1, 2)]) for a in (0.10, 0.05)}

    # anytime-valid upper bound on the miss rate with no miss after n events (inverting the e-process in a)
    def upper(nev, x=0):
        lo, hi = 1e-6, 0.999
        for _ in range(60):
            a = 0.5 * (lo + hi)
            E = sum(w * (c ** x if x else 1.0) * ((1 - c * a) / (1 - a)) ** (nev - x) for c, w in zip(C_DN, PI_DN))
            lo, hi = (lo, a) if E >= 1 / BETA else (a, hi)
        return hi
    res['zero_miss_upper'] = {str(k): dict(anytime=float(upper(k)), cp=float(1 - BETA ** (1 / k))) for k in (12, 29, 32, 46, 60)}
    res['setup'] = dict(a=A, beta=BETA, alarms=K, events=NMAX, sims=SIMS, q_up=Q_UP.tolist(), q_dn=Q_DN.tolist(),
                        pi_dn=PI_DN.tolist(), c_dn=C_DN.tolist())
    return res


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    r = run()
    with open(os.path.join(out_dir, 'method_verify.json'), 'w') as fh:
        json.dump(r, fh, indent=1)
    print(json.dumps(r, indent=1))
