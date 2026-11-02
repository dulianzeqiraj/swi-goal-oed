"""CERTAIN-COAST Methodology, Section 7.7 (synthetic test): safe pumping tests (C3) when the prior is wrong.

The certificate of C3 (method_active.py) uses ridge regression around a prior from the calibrated model and the
self-normalised confidence set of Abbasi-Yadkori, Pal and Szepesvari (2011). Its guarantee assumes that the prior is
wrong by at most S in the Lambda-norm. That assumption cannot be checked before the tests, and an optimistic prior
(weaker onset of intrusion, faster flushing) pushes the certified boundary towards the unsafe side. Following the
robust-Bayes view that a prior is a class rather than a point (Berger, 1994) and the prior-data conflict check of
Evans and Moshonov (2006), three ways of using the prior are compared on the test system of method_active.py:

  nominal  trust the calibrated model: tight precision Lambda, radius S (as in method_active.py);
  box      trust only physics: a wide prior whose radius covers every coefficient vector in a physical box;
  checked  start nominal, and switch to the box prior as soon as the nominal prior ball no longer meets the
           box confidence set (a conflict that, with a right prior, occurs with probability at most delta).

  wide2/4  trust the calibrated model's centre and precision, but double (or quadruple) the radius S.

Priors: the right prior of method_active.py (2.5 sigma from the truth in the Lambda-norm, inside S = 4 sigma) and three
optimistic, wrong priors with the onset of intrusion 60-90% weaker and flushing 40-120% faster (5.5 to 15.7 sigma,
outside S). The planner is the goal-oriented, safe planner of C3 throughout. All values are illustrative.

Per run the output holds the certified closing year before, during (weekly) and after the campaign, the highest
chloride, whether the confidence set held the true coefficients at the end and in every week, the Lambda-distance from
the prior centre to the box confidence set (at the end, and its weekly maximum for 'checked'), the radius of the box
set and the norm of the prior error in the metric of the data (both in units of sigma).

usage: python method_prior.py [OUT_DIR]   (writes method_prior.json)"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import method_active as M  # noqa: E402

SIG = M.SIG_C
# physical box of admissible coefficients: memory (flushing 20 to 200 weeks), constant, hinge slopes
LO = np.r_[0.95, 0.0, np.zeros(len(M.KNOTS))]
HI = np.r_[0.995, 0.02, np.full(len(M.KNOTS), 0.15)]
W = (HI - LO) / 2
LAMD_N, S_N = M.LAMD.copy(), M.S_PRIOR          # nominal prior (calibrated model)
LAMD_B = (SIG / W) ** 2                         # box prior: standard deviation = half-width of the box
TH_RIGHT = M.TH_PRIOR.copy()


def wrong_prior(onset_weaker, flush_faster):
    """Optimistic prior: onset of intrusion weaker and flushing faster than in the truth, same baseline chloride."""
    lam = (1 - M.TH_TRUE[0]) * (1 + flush_faster)
    return np.r_[1 - lam, 0.4 * lam, M.TH_TRUE[2:] * (1 - onset_weaker)]


WRONG = {'wrong1': (0.6, 0.4), 'wrong2': (0.8, 0.8), 'wrong3': (0.9, 1.2)}   # (onset weaker, flushing faster)
PRIORS = {'right': TH_RIGHT, **{k: wrong_prior(*v) for k, v in WRONG.items()}}
TH_WRONG = PRIORS['wrong1']
MODE_S = {'nominal': 1, 'wide2': 2, 'wide4': 4}        # radius S as a multiple of the nominal S
GRID = {'right': ('nominal', 'wide2', 'wide4', 'box', 'checked'), 'wrong1': ('nominal', 'wide2', 'checked'),
        'wrong2': ('nominal', 'wide2', 'wide4', 'checked'), 'wrong3': ('nominal', 'wide2', 'wide4', 'checked')}


def lam_norm(d, lamd):
    return float(np.sqrt(np.sum(lamd * d ** 2)))


def s_box(th0):
    """Largest Lambda_box-distance from the prior centre to any coefficient vector in the box."""
    return float(SIG * np.sqrt(np.sum(np.maximum((LO - th0) ** 2, (HI - th0) ** 2) / W ** 2)))


class Est2:
    """Ridge regression around th0 with precision diag(lamd) and the self-normalised radius with prior bound S."""

    def __init__(self, th0, lamd, S):
        self.th0, self.lamd, self.S = th0, lamd, S
        self.V = np.diag(lamd).astype(float); self.b = np.zeros(M.NF); self._upd()

    def radius(self, V):
        _, ld = np.linalg.slogdet(V)
        return SIG * np.sqrt(2 * (0.5 * ld - 0.5 * np.log(self.lamd).sum() + np.log(1 / M.DELTA))) + self.S

    def add(self, phi, y):
        self.V += np.outer(phi, phi); self.b += phi * (y - phi @ self.th0); self._upd()

    def _upd(self):
        self.Vi = np.linalg.inv(self.V); self.th = self.th0 + self.Vi @ self.b; self.beta = self.radius(self.V)

    def covers(self, th):
        d = self.th - th
        return bool(np.sqrt(d @ self.V @ d) <= self.beta)


def dist_to_set(th0, lamd, c, V, beta):
    """min over the ellipsoid {th: |th - c|_V <= beta} of |th - th0|_Lambda (Lagrange multiplier by bisection)."""
    dv = th0 - c
    if np.sqrt(dv @ V @ dv) <= beta:
        return 0.0
    L = np.diag(lamd)

    def theta(mu):
        return np.linalg.solve(L + mu * V, L @ th0 + mu * V @ c)

    lo, hi = -12.0, 12.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        x = theta(10 ** mid) - c
        if np.sqrt(x @ V @ x) > beta:
            lo = mid
        else:
            hi = mid
    d = theta(10 ** hi) - th0
    return float(np.sqrt(d @ L @ d))


def conflict_dist(est_n, est_b):
    """Lambda-distance from the nominal prior centre to the box confidence set (Eq. conflict of the Methodology)."""
    return dist_to_set(est_n.th0, est_n.lamd, est_b.th, est_b.V, est_b.beta)


def conflict(est_n, est_b):
    """The nominal prior ball no longer meets the box confidence set: the nominal prior is wrong (or the box set
    missed the truth, probability at most delta)."""
    return conflict_dist(est_n, est_b) > est_n.S


def choose2(t, h, c, est):
    """Goal-oriented, safe test choice of C3 with the estimator's own prior (as method_active.choose 'goal_safe')."""
    cand, qw, qd, act, peak, Vafter, unc = M.plan_paths(t, h, c, est)
    safe = peak <= M.C_TEST
    if not safe.any():
        return None
    score = np.full(len(cand), -np.inf)
    for i in np.where(safe)[0]:
        Vi = np.linalg.inv(Vafter[i])
        score[i] = M.closing(M.h_cert(est.th, Vi, est.radius(Vafter[i])))[0]
    score = score - 1e-6 * np.array([L * (a - M.D + b) for a, b, L in cand])
    i = int(np.argmax(score))
    return qw[i, act[i]], qd[i, act[i]]


def run2(seed, th0, mode):
    rng = np.random.default_rng(seed)
    noise_h = rng.normal(0, M.SIG_H, M.HIST + M.CAMP + 40); noise_c = rng.normal(0, SIG, M.HIST + M.CAMP + 40)
    hist_qd = M.Q0 + rng.uniform(-0.2, 0.2, M.HIST); hist_qw = M.D + rng.uniform(0, 1.0, M.HIST)
    est_n = Est2(th0, LAMD_N, S_N * MODE_S.get(mode, 1)); est_b = Est2(th0, LAMD_B, s_box(th0))
    state = dict(h=M.hbar(0, M.D, M.Q0), c=0.4, t=0, active=(est_b if mode == 'box' else est_n), switched=None,
                 cov_all=True, dist_max=0.0)
    log_c, log_h, weekly = [], [], []

    def cert(est):
        return M.closing(M.h_cert(est.th, est.Vi, est.beta))[0]

    def step(qw, qd):
        h, c, t = state['h'], state['c'], state['t']
        phi = M.feats(c, h); cn = phi @ M.TH_TRUE + noise_c[t]
        hn = M.RHO * h + (1 - M.RHO) * M.hbar(t, qw, qd) + noise_h[t]
        est_n.add(phi, cn); est_b.add(phi, cn)
        state.update(h=hn, c=cn, t=t + 1)
        if mode == 'checked' and state['active'] is est_n:
            d = conflict_dist(est_n, est_b)
            state['dist_max'] = max(state['dist_max'], d / SIG)
            if d > est_n.S:
                state['active'] = est_b; state['switched'] = t + 1
        state['cov_all'] = state['cov_all'] and state['active'].covers(M.TH_TRUE)
        if t + 1 > M.HIST:
            weekly.append(cert(state['active']))

    for k in range(M.HIST):
        step(hist_qw[k], hist_qd[k])
    out = {'t_before': cert(state['active'])}
    test_weeks, extra = 0, 0.0
    while state['t'] < M.HIST + M.CAMP:
        sch = choose2(state['t'], state['h'], state['c'], state['active'])
        if sch is None:
            sch = (np.full(4, M.D), np.full(4, M.Q0))
        for a, b in zip(*sch):
            if state['t'] >= M.HIST + M.CAMP:
                break
            test_weeks += int(a > M.D or b > M.Q0); extra += (a - M.D) + (b - M.Q0)
            step(a, b); log_c.append(state['c']); log_h.append(state['h'])
    est = state['active']
    out.update(t_after=cert(est), c_max=float(max(log_c)), h_min=float(min(log_h)), test_weeks=test_weeks,
               extra_kQ_weeks=extra, weekly=[round(float(y), 3) for y in weekly[:M.CAMP]],
               covered=est.covers(M.TH_TRUE), covered_all=state['cov_all'], switched=state['switched'],
               final_prior=('box' if est is est_b else 'nominal'),
               dist_end=conflict_dist(est_n, est_b) / SIG, dist_max=(state['dist_max'] if mode == 'checked' else None),
               beta_box_end=est_b.beta / SIG,
               err_data_end=float(np.sqrt((th0 - M.TH_TRUE) @ (est_b.V - np.diag(LAMD_B)) @ (th0 - M.TH_TRUE))) / SIG)
    return out


def main(od):
    n = int(os.environ.get('NRUN', 200))
    t0 = time.time()
    ht = M.h_true(); t_true = M.closing(ht, dh=0.0)[0]; t_best = M.closing(ht)[0]
    res = {'params': dict(LO=LO.tolist(), HI=HI.tolist(), LAMD_N=LAMD_N.tolist(), S_N=S_N, LAMD_B=LAMD_B.tolist(),
                          PRIORS={k: v.tolist() for k, v in PRIORS.items()}, WRONG=WRONG, MODE_S=MODE_S,
                          NRUN=n, C_TEST=M.C_TEST, DELTA=M.DELTA),
           'truth': dict(t_close=t_true, t_best=t_best, h_crit=float(ht)),
           'prior_error': {k: dict(nominal=lam_norm(v - M.TH_TRUE, LAMD_N) / SIG, box=lam_norm(v - M.TH_TRUE, LAMD_B) / SIG,
                                   S_box=s_box(v) / SIG) for k, v in PRIORS.items()},
           'S_nominal_sigma': S_N / SIG, 'runs': {}}
    print('prior error (sigma, nominal norm):', {k: round(v['nominal'], 2) for k, v in res['prior_error'].items()},
          '| S =', S_N / SIG, '| S_box:', {k: round(v['S_box'], 2) for k, v in res['prior_error'].items()})
    for pk, th0 in PRIORS.items():
        for mode in GRID[pk]:
            rs = [run2(1000 + i, th0, mode) for i in range(n)]
            res['runs'][f'{pk}_{mode}'] = rs
            ta = np.array([r['t_after'] for r in rs]); cm = 250 * np.array([r['c_max'] for r in rs])
            late = np.mean([max([r['t_after']] + r['weekly']) > t_true for r in rs])
            sw = [r['switched'] for r in rs if r['switched'] is not None]
            unsafe = np.mean([max([r['t_before'], r['t_after']] + r['weekly']) > t_best + 1e-9 for r in rs])
            print(f'{pk:5s} {mode:8s} after {np.median(ta):5.1f} [{np.percentile(ta, 10):4.1f}, {np.percentile(ta, 90):4.1f}] '
                  f'late(any week) {late:.3f}  beyond best {unsafe:.3f}  cover {np.mean([r["covered"] for r in rs]):.2f} '
                  f'(all weeks {np.mean([r["covered_all"] for r in rs]):.2f})  dist_end {np.median([r["dist_end"] for r in rs]):.2f}  '
                  f'cmax p95 {np.percentile(cm, 95):.0f} >test {np.mean(cm > 250 * M.C_TEST):.3f} >250 {np.mean(cm > 250):.3f}  '
                  f'switched {len(sw) / n:.2f} (median week {np.median(sw) if sw else float("nan"):.0f})  ({time.time() - t0:.0f}s)',
                  flush=True)
    with open(os.path.join(od, os.environ.get('OUT_NAME', 'method_prior.json')), 'w') as fh:
        json.dump(res, fh)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
