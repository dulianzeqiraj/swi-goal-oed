"""CERTAIN-COAST Methodology, new contribution C3 (synthetic test): what a pumping test is worth in years.

The certified safe window (C1) is limited by the part of the coast's response that the record has never seen: the
onset of seawater intrusion at the wellfield as the head between the wellfield and the sea falls. Routine operation
never goes there, so the certified boundary of the window stays far from the true one. C3 designs short pumping and
dewatering tests that approach the onset in a controlled way:

  * the response is linear in a known feature map, c(t+1) = theta . phi(c(t), h(t)) + w(t), with hinge features
    (k_i - h)^+ at fixed heads k_i, the model class of Mania, Jordan and Recht (2022);
  * the coefficients are estimated by least squares with a physics prior (ridge around the coupled-model value), and
    the self-normalised confidence set of Abbasi-Yadkori, Pal and Szepesvari (2011) holds for all weeks at once;
  * the certified boundary is the lowest head at which the chloride limit is forward-invariant for every coefficient
    vector in the confidence set: theta . phi(L, h) <= L (if chloride is at the limit L, it cannot rise above it);
  * tests are planned on the current estimate, (a) goal-oriented: the test that most raises the predicted certified
    closing year is chosen, and (b) safe: the upper confidence bound of chloride along the whole test and recovery
    must stay below a test limit; the test is valued in years through the closing year of the window.

Strategies compared on the same histories: routine operation; random perturbations of pumping and dewatering; an
E-optimal planner in the spirit of Mania et al. (2022), which raises the smallest eigenvalue of the design matrix;
the same planner with the safety filter; and the goal-oriented, safe planner of C3. All values are illustrative, not
site values; the project replaces this test system by the calibrated coupled model of WP2.

usage: python method_active.py [OUT_DIR]   (writes method_active.json)"""
import json
import os
import sys
import time

import numpy as np

# ------------------------------------------------------------------------------------------------ test system
# heads in m above mean sea level; flows in thousand m3/d (kQ); one step = one week
H0, KW, KD, RHO, SEAS, PER = 2.92, 0.06, 0.25, 0.75, 0.25, 52.0
D, Q0 = 15.0, 1.2                      # water demand (wellfield >= D) and usual port dewatering
KNOTS = np.array([0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
NF = 2 + len(KNOTS)
TH_TRUE = np.r_[0.98, 0.008, 0.0, 0.0, 0.05, 0.05, 0.0, 0.0]     # [chloride, constant, hinges at KNOTS]
TH_PRIOR = np.r_[0.977, 0.009, 0.0, 0.0, 0.03, 0.03, 0.02, 0.0]  # coupled-model (physics) prior, deliberately off
SIG_C, SIG_H = 0.005, 0.02              # chloride index noise (1 = 250 mg/L) and head noise (m) per week
# prior standard deviations: memory (flushing about 50 weeks, known to about 10%), constant, hinge slopes
S_PRIOR_SD = np.r_[0.002, 0.001, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]
LAMD = (SIG_C / S_PRIOR_SD) ** 2        # ridge weights, Lambda = diag(LAMD)
S_PRIOR = 4 * SIG_C                     # bound on the prior error in the Lambda-norm (true error 2.5 SIG_C)
DELTA = 0.05                            # failure probability of the confidence set (all weeks at once)
LIM = 0.98                              # certified chloride level (index); the limit is 1.0
C_TEST = float(os.environ.get('C_TEST', 0.70))   # chloride a test may reach (0.70 = 175 mg/L), upper bound
ALLOW = 2 * SIG_C / np.sqrt(1 - 0.98 ** 2)   # allowance for accumulated noise in the safety check
DH = 0.05                               # certified error of the head prediction from the coupled model (m)
Y0, MD, MW, YREQ = 1.2, 0.35, 0.02, 1.8  # port water-table depth y = Y0 - R + MD Qd + MW Qw must stay >= YREQ
RATE = 0.010                            # relative sea-level rise, m/yr (4 mm/yr sea level + 6 mm/yr subsidence)
HIST, CAMP, REC = 156, 78, 6            # weeks of routine record, weeks of the test campaign, recovery weeks
QW_C = np.array([15.0, 17.5, 20.0, 22.5, 25.0])
QD_C = np.arange(1.2, 4.41, 0.4)
L_C = np.array([2, 4, 6, 8])
HGRID = np.round(np.arange(0.20, 1.80001, 0.002), 4)


def hbar(t, qw, qd):
    return H0 - KW * qw - KD * qd + SEAS * np.sin(2 * np.pi * t / PER)


def feats(c, h):
    c = np.asarray(c, float); h = np.asarray(h, float)
    return np.concatenate([c[..., None], np.ones(c.shape + (1,)), np.maximum(KNOTS - h[..., None], 0.0)], axis=-1)


class Est:
    """Ridge regression around the physics prior with the self-normalised confidence radius."""

    def __init__(self):
        self.V = np.diag(LAMD); self.b = np.zeros(NF); self._upd()

    def add(self, phi, y):
        self.V += np.outer(phi, phi); self.b += phi * (y - phi @ TH_PRIOR); self._upd()

    def _upd(self):
        self.Vi = np.linalg.inv(self.V)
        self.th = TH_PRIOR + self.Vi @ self.b
        self.beta = radius(self.V)


def radius(V):
    _, ld = np.linalg.slogdet(V)
    return SIG_C * np.sqrt(2 * (0.5 * ld - 0.5 * np.log(LAMD).sum() + np.log(1 / DELTA))) + S_PRIOR


def ucb(th, Vi, beta, phi):
    return phi @ th + beta * np.sqrt(np.einsum('...i,ij,...j->...', phi, Vi, phi))


def h_cert(th, Vi, beta):
    """Lowest head (grid) such that the limit is forward-invariant at it and at every higher head."""
    ok = ucb(th, Vi, beta, feats(np.full(HGRID.shape, LIM), HGRID)) <= LIM
    bad = np.where(~ok)[0]
    if not len(bad):
        return HGRID[0]
    return HGRID[bad[-1] + 1] if bad[-1] + 1 < len(HGRID) else np.inf   # inf: nothing certified


def h_true():
    ok = feats(np.full(HGRID.shape, LIM), HGRID) @ TH_TRUE <= LIM
    bad = np.where(~ok)[0]
    return HGRID[bad[-1] + 1]


def closing(hc, dh=DH):
    """Closing sea level and year of the window when the certified boundary head is hc. Dry-season head at the
    sentinel H0 - R - KW D - KD Qd - SEAS - dh must stay above hc (B), and the port needs Qd >= A (liquefaction)."""
    c1 = H0 - KW * D - SEAS - dh
    if not np.isfinite(hc):
        return 0.0, -np.inf, (YREQ - Y0 - MW * D) / MD
    Rs = (MD * (c1 - hc) - KD * (YREQ - Y0 - MW * D)) / (MD + KD)
    return max(Rs, 0.0) / RATE, (c1 - hc) / KD, (YREQ - Y0 - MW * D) / MD


MU = KD * MD / ((MD + KD) * RATE)        # years per kQ of certified dewatering (the multiplier of Eq. mult)


# ------------------------------------------------------------------------------------------------ planning
def plan_paths(t, h, c, est):
    """All candidate tests (Qw, Qd, L) followed by REC weeks of routine operation, predicted on the estimate."""
    cand = [(qw, qd, L) for qw in QW_C for qd in QD_C for L in L_C]
    n = len(cand); S = max(L_C) + REC
    qw = np.full((n, S), D); qd = np.full((n, S), Q0); act = np.zeros((n, S), bool)
    for i, (a, b, L) in enumerate(cand):
        qw[i, :L] = a; qd[i, :L] = b; act[i, :L + REC] = True
    hs = np.zeros((n, S)); cs = np.zeros((n, S)); cu = np.zeros((n, S))
    hh = np.full(n, h); cc = np.full(n, c); cuu = np.full(n, c + 2 * SIG_C)
    for s in range(S):
        hs[:, s] = hh; cs[:, s] = cc; cu[:, s] = cuu
        hl = hh - DH - 2 * SIG_H
        cc = feats(cc, hh) @ est.th
        cuu = np.maximum(ucb(est.th, est.Vi, est.beta, feats(cuu, hl)), cc)
        hh = RHO * hh + (1 - RHO) * hbar(t + s, qw[:, s], qd[:, s])
    peak = np.where(act, cu, -np.inf).max(1) + ALLOW
    phis = feats(cs, hs) * act[..., None]
    Vafter = est.V + np.einsum('nsi,nsj->nij', phis, phis)
    unc = np.einsum('nsi,ij,nsj->ns', phis, est.Vi, phis).max(1)     # most uncertain feature reached
    return cand, qw, qd, act, peak, Vafter, unc


def choose(kind, t, h, c, est):
    cand, qw, qd, act, peak, Vafter, unc = plan_paths(t, h, c, est)
    safe = peak <= C_TEST
    if kind.startswith('eopt'):
        # raise the smallest eigenvalue; on ties, reach the most uncertain feature (the fallback of Mania et al.)
        lmin = np.linalg.eigvalsh(Vafter)[:, 0]
        score = np.round(lmin / est.V.diagonal().min(), 6) * 1e3 + unc / (1 + unc.max())
    else:  # goal: predicted certified closing year after the test (estimate kept, uncertainty shrunk)
        score = np.empty(len(cand))
        Vis = np.linalg.inv(Vafter)
        for i in range(len(cand)):
            score[i] = closing(h_cert(est.th, Vis[i], radius(Vafter[i])))[0]
    score = score - 1e-6 * np.array([L * (a - D + b) for a, b, L in cand])   # prefer smaller tests on ties
    if kind.endswith('safe'):
        if not safe.any():
            return None
        score = np.where(safe, score, -np.inf)
    i = int(np.argmax(score))
    return qw[i, act[i]], qd[i, act[i]]


# ------------------------------------------------------------------------------------------------ simulation
def run(kind, seed):
    rng = np.random.default_rng(seed)
    noise_h = rng.normal(0, SIG_H, HIST + CAMP + 40); noise_c = rng.normal(0, SIG_C, HIST + CAMP + 40)
    hist_qd = Q0 + rng.uniform(-0.2, 0.2, HIST); hist_qw = D + rng.uniform(0, 1.0, HIST)
    rk = np.random.default_rng(seed + 10_000)
    est = Est(); h = hbar(0, D, Q0); c = 0.4; t = 0
    log_c, log_h = [], []

    weekly = []

    def step(qw, qd):
        nonlocal h, c, t
        phi = feats(c, h); cn = phi @ TH_TRUE + noise_c[t]
        hn = RHO * h + (1 - RHO) * hbar(t, qw, qd) + noise_h[t]
        est.add(phi, cn); h, c, t = hn, cn, t + 1
        if t > HIST:
            weekly.append(closing(h_cert(est.th, est.Vi, est.beta))[0])

    for k in range(HIST):
        step(hist_qw[k], hist_qd[k])
    out = {'t_before': closing(h_cert(est.th, est.Vi, est.beta))[0]}
    test_weeks, extra = 0, 0.0
    while t < HIST + CAMP:
        if kind == 'routine':
            step(D, Q0); log_c.append(c); log_h.append(h)
        elif kind == 'random':
            step(D + 2.5 * rk.integers(0, 2), Q0 + 0.4 * rk.integers(0, 2)); log_c.append(c); log_h.append(h)
        else:
            sch = choose(kind, t, h, c, est)
            if sch is None:
                sch = (np.full(4, D), np.full(4, Q0))
            for a, b in zip(*sch):
                if t >= HIST + CAMP:
                    break
                test_weeks += int(a > D or b > Q0); extra += (a - D) + (b - Q0)
                step(a, b); log_c.append(c); log_h.append(h)
    hc = h_cert(est.th, est.Vi, est.beta)
    out.update(t_after=closing(hc)[0], h_cert=float(hc), B_cert=closing(hc)[1], c_max=float(max(log_c)),
               h_min=float(min(log_h)), test_weeks=test_weeks, extra_kQ_weeks=extra,
               weekly=[round(float(y), 3) for y in weekly[:CAMP]],
               theta_err=float(np.linalg.norm(est.th - TH_TRUE)),
               covered=bool(((est.th - TH_TRUE) @ est.V @ (est.th - TH_TRUE)) ** 0.5 <= est.beta))
    return out


KINDS = [('routine', 'Routine operation'), ('random', 'Random perturbations'),
         ('eopt', 'E-optimal planner (Mania et al. style)'), ('eopt_safe', 'E-optimal planner with safety filter'),
         ('goal_safe', 'Goal-oriented, safe planner (C3)')]


def main(od):
    global C_TEST
    n = int(os.environ.get('NRUN', 100))
    t0 = time.time()
    ht = h_true(); t_true, B_true, A0 = closing(ht, dh=0.0)
    res = {'params': dict(H0=H0, KW=KW, KD=KD, RHO=RHO, SEAS=SEAS, D=D, Q0=Q0, KNOTS=KNOTS.tolist(), TH_TRUE=TH_TRUE.tolist(),
                          TH_PRIOR=TH_PRIOR.tolist(), S_PRIOR=S_PRIOR, S_PRIOR_SD=S_PRIOR_SD.tolist(), SIG_C=SIG_C, SIG_H=SIG_H, DELTA=DELTA, LIM=LIM,
                          C_TEST=C_TEST, ALLOW=ALLOW, DH=DH, Y0=Y0, MD=MD, MW=MW, YREQ=YREQ, RATE=RATE, HIST=HIST,
                          CAMP=CAMP, REC=REC, NRUN=n),
           'truth': dict(h_crit=float(ht), t_close=t_true, B=B_true, A=A0, mu_years_per_kQ=MU), 'kinds': {}}
    for kind, label in KINDS:
        rs = [run(kind, 1000 + i) for i in range(n)]
        res['kinds'][kind] = {'label': label, 'runs': rs}
        ta = np.array([r['t_after'] for r in rs]); cm = np.array([r['c_max'] for r in rs])
        print(f'{label:45s} before {np.median([r["t_before"] for r in rs]):5.1f}  after {np.median(ta):5.1f} '
              f'[{np.percentile(ta, 10):4.1f}, {np.percentile(ta, 90):4.1f}]  cmax med {np.median(cm):.2f} '
              f'>test {np.mean(cm > C_TEST):.2f} >limit {np.mean(cm > 1):.2f}  cover {np.mean([r["covered"] for r in rs]):.2f} '
              f'  tw {np.median([r["test_weeks"] for r in rs]):.0f}  ({time.time() - t0:.0f}s)', flush=True)
    res['truth_print'] = f'true closing {t_true:.1f} y, B={B_true:.2f}, A={A0:.2f}, h_crit={ht:.3f}'
    print(res['truth_print'])
    # sensitivity to the chloride a test may reach (the two safe planners)
    base, ns, res['sensitivity'] = C_TEST, max(n // 2, 1), {}
    for ct in (0.55, 0.85):
        C_TEST = ct
        for kind in ('eopt_safe', 'goal_safe'):
            rs = [run(kind, 1000 + i) for i in range(ns)]
            ta = np.array([r['t_after'] for r in rs]); cm = np.array([r['c_max'] for r in rs])
            res['sensitivity'].setdefault(f'{ct:.2f}', {})[kind] = dict(
                t_after_median=float(np.median(ta)), p10=float(np.percentile(ta, 10)), p90=float(np.percentile(ta, 90)),
                c_max_p95=float(np.percentile(cm, 95)), share_above_test=float(np.mean(cm > ct)), runs=ns)
            print(f'  C_TEST {ct:.2f} {kind:10s} after {np.median(ta):5.1f}  cmax p95 {np.percentile(cm, 95):.2f}', flush=True)
    C_TEST = base
    name = os.environ.get('OUT_NAME', 'method_active.json')
    with open(os.path.join(od, name), 'w') as fh:
        json.dump(res, fh)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
