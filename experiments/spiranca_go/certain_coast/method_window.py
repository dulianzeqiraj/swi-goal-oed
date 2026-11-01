"""CERTAIN-COAST Methodology, new contributions C1 and C2 (synthetic test).

C1  The certified safe operating window: the set of wellfield pumping Q_w and port dewatering Q_d that keeps seawater
    intrusion at the wellfield, liquefaction at the port and flooding of the port within their limits at the same time,
    each with probability at least 1 - alpha; the relative sea level R*, and the year t*, at which this window closes.
C2  The value of a sensor in years: how much later the certified window closes once the sensor's data are assimilated
    (preposterior analysis), and the first-order estimate of that delay from the multiplier of the closing constraint.

Physics (standard building blocks; the contribution is the window, its closing point and their sensitivities):
  * sharp-interface single potential (Strack 1976) for an unconfined coastal aquifer, base at depth d = d0 + R below the
    sea; wells and image wells; regional freshwater discharge q from an inland water level held fixed relative to the
    land (head-controlled; Werner and Simmons 2009);
  * seawater reaches the wellfield when the stagnation (saddle) potential between the well and the sea falls below the
    toe potential; with the port dewatering well on the same flow line the saddles follow from one quadratic;
  * liquefaction potential index at the port under the design shaking, CPT-based triggering (Boulanger and Idriss 2014),
    LPI (Iwasaki et al. 1978); the water-table depth comes from the potential;
  * 100-year still water level at the port quay against the crest with freeboard.
All parameter values are illustrative, not site values. The project replaces this transect model by the calibrated
coupled model of WP2; the method is unchanged.

usage: python method_window.py [OUT_DIR]   (writes method_window.json and two figures)"""
import json
import os
import sys

import numpy as np

DELTA = 0.025
P = dict(L=6000.0, xw=2000.0, xp=600.0, re=80.0, D=15000.0, G0=3.0, crest=3.0, freeboard=0.3, amax=0.25, M=6.5,
         LPIstar=5.0, Zsand=10.0, gm=18.0, gsat=19.5, gw=9.81, Qdmax=20000.0, hmin=0.05, alpha=0.05)
# prior: lognormal K (m/d); normal aquifer depth below sea d0 (m), inland water level hL (m above sea), soil resistance
# qc1Ncs, 100-year still water level eta (m), sea-level rise rate s and land subsidence rate v (mm/yr)
PRIOR = dict(lnK=(np.log(200.0), 0.20), d0=(40.0, 2.0), hL=(6.0, 0.3), qc=(124.0, 2.5), eta=(1.20, 0.12),
             s=(4.0, 1.0), v=(6.0, 3.0))
# candidate sensors: (label, cost EUR from the Budget lines, observed quantity, noise sd)
SENSORS = [
    ('Port piezometer', 5800, 'H_port', 0.05),
    ('Sentinel piezometer', 5800, 'h_sent', 0.05),
    ('GNSS station at the port', 9700, 'v', 0.7),
    ('Two corner reflectors', 3000, 'v', 1.2),
]
XSENT = 1200.0


def sample(n, seed):
    rng = np.random.default_rng(seed)
    th = {k: rng.normal(m, s, n) for k, (m, s) in PRIOR.items()}
    th['K'] = np.exp(th.pop('lnK'))
    th['v'] = np.abs(th['v'])
    th['r'] = (th['s'] + th['v']) / 1000.0  # m/yr
    return th


# ------------------------------------------------------------------------------------------------- physics
def q_amb(K, d0, hL, R):
    return np.maximum(K / P['L'] * 0.5 * ((hL + d0) ** 2 - (1 + DELTA) * (d0 + R) ** 2), 1e-9)


def phi_toe(d0, R):
    return 0.5 * DELTA * (1 + DELTA) * (d0 + R) ** 2


def h_from_phi(phi, d):
    ptoe = 0.5 * DELTA * (1 + DELTA) * d ** 2
    z1 = np.sqrt(np.maximum(2 * phi + (1 + DELTA) * d ** 2, 0)) - d
    z2 = np.sqrt(np.maximum(2 * DELTA * phi / (1 + DELTA), 0))
    return np.where(phi >= ptoe, z1, z2)


def phi_from_h(h, d):
    z1 = 0.5 * ((h + d) ** 2 - (1 + DELTA) * d ** 2)
    z2 = (1 + DELTA) / (2 * DELTA) * h ** 2
    return np.where(h >= DELTA * d, z1, z2)


def phi_point(x, y, K, q, Qd, Qw):
    xp, xw = P['xp'], P['xw']
    f = lambda Q, xi: Q / (4 * np.pi * K) * np.log(((x - xi) ** 2 + y ** 2) / ((x + xi) ** 2 + y ** 2))
    return q / K * x + f(Qd, xp) + f(Qw, xw)


def phi_axis(x, K, q, Qd, Qw):
    xp, xw = P['xp'], P['xw']
    f = lambda Q, xi: Q / (2 * np.pi * K) * np.log(np.abs(x - xi) / (x + xi))
    return q / K * x + f(Qd, xp) + f(Qw, xw)


def cstar(K, q, Qd, Qw):
    """Potential at which the wellfield's low-potential region joins the sea: max of the saddle between the port well and
    the sea (or 0 if the port draws from the sea) and the saddle between the two wells. Both saddles are on the axis;
    with u = x^2 they are the roots of (q/K)(u-P)(u-W) + a_p(u-W) + a_w(u-P) = 0."""
    Qd = np.maximum(Qd, 1e-3)
    xp, xw = P['xp'], P['xw']
    Pp, W = xp ** 2, xw ** 2
    ap, aw = Qd * xp / (np.pi * K), Qw * xw / (np.pi * K)
    A = q / K
    B = -A * (Pp + W) + ap + aw
    C = A * Pp * W - ap * W - aw * Pp
    disc = np.sqrt(np.maximum(B ** 2 - 4 * A * C, 0))
    u1, u2 = (-B - disc) / (2 * A), (-B + disc) / (2 * A)
    ub = np.where((u2 > Pp) & (u2 < W), u2, u1)
    ua = np.where((u1 > 0) & (u1 < Pp), u1, np.nan)
    phib = phi_axis(np.sqrt(np.clip(ub, Pp, W)), K, q, Qd, Qw)
    phia = np.where(np.isnan(ua), 0.0, phi_axis(np.sqrt(np.clip(np.nan_to_num(ua, nan=1.0), 1e-6, Pp)), K, q, Qd, Qw))
    return np.maximum(phia, phib)


def lpi(zw, qc):
    zw = np.atleast_1d(zw)[:, None]; qc = np.atleast_1d(qc)[:, None]
    z = np.arange(0.05, 20.0, 0.1)[None, :]
    sv = P['gm'] * np.minimum(z, zw) + P['gsat'] * np.maximum(z - zw, 0)
    sve = sv - P['gw'] * np.maximum(z - zw, 0)
    rd = np.exp(-1.012 - 1.126 * np.sin(z / 11.73 + 5.133) + (0.106 + 0.118 * np.sin(z / 11.28 + 5.142)) * P['M'])
    csr = 0.65 * P['amax'] * sv / sve * rd
    crr = np.exp(qc / 113 + (qc / 1000) ** 2 - (qc / 140) ** 3 + (qc / 137) ** 4 - 2.80)
    msf = 1 + (np.minimum(1.09 + (qc / 180) ** 3, 2.2) - 1) * (8.64 * np.exp(-P['M'] / 4) - 1.325)
    ks = np.minimum(1 - np.minimum(1 / (37.3 - 8.27 * qc ** 0.264), 0.3) * np.log(sve / 101.325), 1.1)
    fs = crr * msf * ks / csr
    F = np.where((z > zw) & (z < P['Zsand']) & (fs < 1), 1 - fs, 0.0)
    return (F * (10 - 0.5 * z)).sum(axis=1) * 0.1


def zcrit(qc):
    """Shallowest water-table depth at which LPI under the design shaking stays at or below LPI*."""
    lo, hi = np.zeros_like(qc), np.full_like(qc, 8.0)
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        bad = lpi(mid, qc) > P['LPIstar']
        lo, hi = np.where(bad, mid, lo), np.where(bad, hi, mid)
    return hi


# ------------------------------------------------------------------------------------------------- thresholds
def thresholds(th, Rg, Qw=None):
    """Per sample and sea level: A = least dewatering that keeps LPI <= LPI* (inf if the water table would have to be
    held at sea level), B = most dewatering that keeps the wellfield free of seawater (-inf if even no dewatering fails)."""
    Qw = P['D'] if Qw is None else Qw
    K, d0, hL = th['K'], th['d0'], th['hL']
    zc = th['zc']
    n, m = len(K), len(Rg)
    A, B = np.empty((n, m)), np.empty((n, m))
    for j, R in enumerate(Rg):
        q = q_amb(K, d0, hL, R)
        d = d0 + R
        pt = phi_toe(d0, R)
        # liquefaction: water table at the port protection point must lie at or below G0 - zc (land datum)
        htar = P['G0'] - zc - R
        ptar = phi_from_h(np.maximum(htar, 0), d)
        p0 = phi_point(P['xp'], P['re'], K, q, 0.0, Qw)
        gpp = np.log((4 * P['xp'] ** 2 + P['re'] ** 2) / P['re'] ** 2) / (4 * np.pi * K)
        a = np.maximum((p0 - ptar) / gpp, 0.0)
        A[:, j] = np.where(htar <= P['hmin'], np.inf, a)
        # seawater intrusion at the wellfield: c*(Qd) >= phi_toe, c* decreasing in Qd
        ok0 = cstar(K, q, 0.0, Qw) >= pt
        okmax = cstar(K, q, P['Qdmax'], Qw) >= pt
        lo, hi = np.zeros(n), np.full(n, P['Qdmax'])
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            good = cstar(K, q, mid, Qw) >= pt
            lo, hi = np.where(good, mid, lo), np.where(good, hi, mid)
        B[:, j] = np.where(~ok0, -np.inf, np.where(okmax, P['Qdmax'], lo))
    return A, B


def observe(th, what):
    K, d0, hL = th['K'], th['d0'], th['hL']
    q = q_amb(K, d0, hL, 0.0)
    if what == 'H_port':
        return h_from_phi(phi_point(P['xp'], P['re'], K, q, 0.0, P['D']), d0)
    if what == 'h_sent':
        return h_from_phi(phi_point(XSENT, 0.0, K, q, 0.0, P['D']), d0)
    return th['v']


# ------------------------------------------------------------------------------------------------- certified closing
def wq(vals_sorted, w_sorted_cum, level):
    """Weighted quantile per column; columns pre-sorted; w_sorted_cum[:, k] cumulative weights in sorted order."""
    idx = (w_sorted_cum < level).sum(axis=0)
    idx = np.minimum(idx, vals_sorted.shape[0] - 1)
    return vals_sorted[idx, np.arange(vals_sorted.shape[1])]


class Closing:
    """Certified bounds on dewatering against time for weighted samples (weights change, sorted tables do not)."""

    def __init__(self, th, Rg, A, B, tg):
        self.tg = tg
        R = th['r'][:, None] * tg[None, :]
        dR = Rg[1] - Rg[0]
        pos = np.clip(R / dR, 0, len(Rg) - 1.000001)
        i0 = pos.astype(int); fr = pos - i0
        rows = np.arange(len(R))[:, None]

        def interp(T):
            lo, hi = T[rows, i0], T[rows, i0 + 1]
            with np.errstate(invalid='ignore'):
                v = lo + fr * (hi - lo)
            v = np.where(np.isinf(lo) | np.isinf(hi), np.where(np.isinf(hi), hi, lo), v)
            return np.where(R > Rg[-1], np.inf if T is A else -np.inf, v)
        At, Bt = interp(A), interp(B)
        self.oA, self.oB = np.argsort(At, axis=0), np.argsort(Bt, axis=0)
        cols = np.arange(len(tg))[None, :]
        self.As, self.Bs = At[self.oA, cols], Bt[self.oB, cols]
        self.flood = (R > (P['crest'] - P['freeboard'] - th['eta'])[:, None]).astype(float)
        self.cols = cols

    def curves(self, w, a=None):
        a = P['alpha'] if a is None else a
        w = w / w.sum()
        cA = np.cumsum(w[self.oA], axis=0); cB = np.cumsum(w[self.oB], axis=0)
        qA = wq(self.As, cA, 1 - a)
        qB = wq(self.Bs, cB, a)
        pF = w @ self.flood
        return qA, qB, pF

    def close(self, w, a=None):
        a = P['alpha'] if a is None else a
        qA, qB, pF = self.curves(w, a)
        tg = self.tg
        fin = np.isfinite(qA) & np.isfinite(qB)
        g = {'joint': np.where(fin, qB - qA, 1.0), 'liq_limit': np.where(np.isinf(qA), -1.0, 1.0),
             'swi': qB, 'flood': a - pF, 'dewater_cap': P['Qdmax'] - qA}
        first = {}
        for k, v in g.items():
            bad = np.nonzero(v < 0)[0]
            if len(bad) == 0:
                first[k] = (np.inf, None)
                continue
            j = bad[0]
            if j == 0:
                first[k] = (0.0, j)
                continue
            v0, v1 = v[j - 1], v[j]
            fin = np.isfinite(v0) and np.isfinite(v1) and k in ('joint', 'swi', 'flood', 'dewater_cap')
            t = tg[j - 1] + (tg[j] - tg[j - 1]) * (v0 / (v0 - v1)) if fin else tg[j]
            first[k] = (float(t), j)
        k_star = min(first, key=lambda k: first[k][0])
        return first[k_star][0], k_star, first, (qA, qB, pF)


# ------------------------------------------------------------------------------------------------- experiment
def run(N=20000, M=300, seed=7):
    th = sample(N, seed)
    th['zc'] = zcrit(th['qc'])
    Rg = np.round(np.arange(0.0, 1.81, 0.01), 4)
    A, B = thresholds(th, Rg)
    tg = np.arange(0.0, 180.01, 0.5)
    C = Closing(th, Rg, A, B, tg)
    w0 = np.ones(N)
    t_cert, k_cert, first, (qA, qB, pF) = C.close(w0)
    t_med, k_med, first_med, _ = C.close(w0, a=0.5)

    # single-hazard plans: what each believes, and when it is in fact unsafe
    tS = first['swi'][0]
    tL0 = float(tg[np.nonzero(qA > 0)[0][0]]) if (qA > 0).any() else np.inf
    tLmax = min(first['liq_limit'][0], first['dewater_cap'][0])
    tF = first['flood'][0]
    plans = {
        'joint': dict(believed=t_cert, unsafe_from=t_cert),
        'flood_only': dict(believed=tF, unsafe_from=min(tL0, tS)),
        'swi_only': dict(believed=tS, unsafe_from=tL0),
        'liq_only': dict(believed=tLmax, unsafe_from=first['joint'][0]),
    }

    # multiplier of the closing constraint (years per m3/d of margin) from the slope of the active constraint
    j = first[k_cert][1]
    cap = P['Qdmax']

    def slack(qa, qb):
        """B - A with impossible cases clipped to finite values of the right sign."""
        return np.clip(np.where(np.isfinite(qb), qb, 0.0), 0, cap) - np.clip(np.where(np.isfinite(qa), qa, cap), 0, cap)

    def at(F, t):
        k = min(max(int(np.searchsorted(tg, t)), 1), len(tg) - 1)
        return F[k - 1] + (F[k] - F[k - 1]) * (t - tg[k - 1]) / (tg[k] - tg[k - 1])
    F0 = slack(qA, qB)
    slope = (F0[j] - F0[j - 1]) / (tg[j] - tg[j - 1]) if k_cert == 'joint' else np.nan
    mu = -1.0 / slope if np.isfinite(slope) and slope < 0 else np.nan
    # envelope check: shift the liquefaction margin by delta and compare the exact and first-order closing years
    env = []
    for dlt in (-300.0, -100.0, 100.0, 300.0):
        Fd = slack(qA + dlt, qB)
        bad = np.nonzero(Fd < 0)[0]
        k = bad[0]
        t_ex = tg[k - 1] + (tg[k] - tg[k - 1]) * Fd[k - 1] / (Fd[k - 1] - Fd[k])
        env.append(dict(delta=dlt, exact=float(t_ex - t_cert), first_order=float(-mu * dlt)))

    # sensors: preposterior years gained, first-order (multiplier) estimate, classical spread reduction
    rng = np.random.default_rng(seed + 1)
    tru = sample(M, seed + 2)
    tru['zc'] = zcrit(tru['qc'])
    # present-day operational indicators for the classical criterion: port water-table depth, wellfield SWI margin
    q0 = q_amb(th['K'], th['d0'], th['hL'], 0.0)
    ind = np.vstack([P['G0'] - h_from_phi(phi_point(P['xp'], P['re'], th['K'], q0, 0.0, P['D']), th['d0']),
                     cstar(th['K'], q0, 0.0, P['D']) - phi_toe(th['d0'], 0.0)])
    sd0 = ind.std(axis=1)
    out = []
    for lab, cost, what, sd in SENSORS:
        hs, ht = observe(th, what), observe(tru, what)
        gains, lin, red, ess = [], [], [], []
        for m in range(M):
            y = ht[m] + rng.normal(0, sd)
            lw = -0.5 * ((y - hs) / sd) ** 2
            w = np.exp(lw - lw.max())
            ess.append(w.sum() ** 2 / (w ** 2).sum())
            t_post, _, _, (qA1, qB1, _) = C.close(w)
            gains.append(t_post - t_cert)
            if np.isfinite(mu):
                lin.append(mu * (at(slack(qA1, qB1), t_cert) - at(F0, t_cert)))
            wn = w / w.sum()
            mean = ind @ wn
            sdp = np.sqrt(((ind - mean[:, None]) ** 2) @ wn)
            red.append(1 - sdp / sd0)
        gains = np.array(gains)
        out.append(dict(sensor=lab, cost=cost, observes=what, noise=sd, years=float(gains.mean()),
                        years_se=float(gains.std() / np.sqrt(M)), years_per_10k=float(gains.mean() / cost * 1e4),
                        years_linear=float(np.mean(lin)) if lin else None,
                        years_linear_median=float(np.median(lin)) if lin else None,
                        years_median=float(np.median(gains)),
                        spread_reduction=float(np.mean(red)), ess_median=float(np.median(ess))))
    # closing sea level without the rate uncertainty (the window in sea-level terms)
    R_star, k_R = closing_sea_level(th, Rg, A, B, w0)
    R_star_med, k_R_med = closing_sea_level(th, Rg, A, B, w0, a=0.5)
    qA_m, qB_m, _ = C.curves(w0, 0.5)
    res = dict(params=P, prior={k: list(v) for k, v in PRIOR.items()}, N=N, M=M,
               zc_median=float(np.median(th['zc'])), r_median_mm=float(np.median(th['r']) * 1000),
               r_p5_p95_mm=[float(np.percentile(th['r'], 5) * 1000), float(np.percentile(th['r'], 95) * 1000)],
               t_cert=t_cert, closing_constraint=k_cert, t_median=t_med, closing_constraint_median=k_med,
               R_star=R_star, R_star_constraint=k_R, R_star_median=R_star_med, R_star_median_constraint=k_R_med,
               tL0=tL0, plans=plans, mu_years_per_m3d=mu, envelope=env, sensors=out,
               first={k: v[0] for k, v in first.items()},
               curves=dict(t=tg.tolist(), qA=np.where(np.isfinite(qA), qA, -1).tolist(),
                           qB=np.where(np.isfinite(qB), qB, -1).tolist(),
                           qA_med=np.where(np.isfinite(qA_m), qA_m, -1).tolist(),
                           qB_med=np.where(np.isfinite(qB_m), qB_m, -1).tolist()),
               saddle_check=check_saddle())
    return res, (th, Rg, A, B, C, qA, qB, pF)


def closing_sea_level(th, Rg, A, B, w, a=None):
    """Sea level at which the certified window closes (no rate uncertainty involved)."""
    a = P['alpha'] if a is None else a
    w = w / w.sum()
    Rf = P['crest'] - P['freeboard'] - th['eta']
    for j, R in enumerate(Rg):
        oA, oB = np.argsort(A[:, j]), np.argsort(B[:, j])
        qA = A[oA, j][min(np.searchsorted(np.cumsum(w[oA]), 1 - a), len(w) - 1)]
        qB = B[oB, j][min(np.searchsorted(np.cumsum(w[oB]), a), len(w) - 1)]
        pF = w[R > Rf].sum()
        bad = {'liq_limit': np.isinf(qA), 'swi': qB < 0, 'flood': pF > a, 'joint': np.isfinite(qA) and np.isfinite(qB) and qA > qB}
        hit = [k for k, v in bad.items() if v]
        if hit:
            return float(R), hit[0]
    return float('inf'), None


def check_saddle(n=200, seed=11, nx=420, ny=361):
    """Closed-form criterion (saddle potentials from one quadratic) against a brute-force check: does the region
    phi < phi_toe connect the wellfield to the sea on a fine grid?"""
    from scipy import ndimage
    rng = np.random.default_rng(seed)
    th = sample(n, seed)
    x = np.linspace(1.0, 2.6 * P['xw'], nx); y = np.linspace(-1.6 * P['xw'], 1.6 * P['xw'], ny)
    X, Y = np.meshgrid(x, y)
    iw = (np.argmin(np.abs(y)), np.argmin(np.abs(x - P['xw'])))
    agree, close = 0, 0
    for i in range(n):
        K, d0, hL = th['K'][i], th['d0'][i], th['hL'][i]
        R = rng.uniform(0, 1.2); Qw = rng.uniform(0.5, 1.6) * P['D']; Qd = rng.uniform(0, 1.0) * P['Qdmax']
        q = q_amb(K, d0, hL, R); pt = phi_toe(d0, R)
        cs = float(cstar(np.array([K]), np.array([q]), np.array([Qd]), np.array([Qw]))[0])
        phi = phi_point(X, Y, K, q, Qd, Qw)
        lab, _ = ndimage.label(phi < pt)
        connected = lab[iw] > 0 and lab[iw] in set(np.unique(lab[:, 0])) - {0}
        safe_closed = cs >= pt
        if abs(cs - pt) < 0.02 * pt:
            close += 1
        agree += (safe_closed == (not connected))
    return dict(cases=n, agree=int(agree), near_boundary=int(close))


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    res, _ = run()
    with open(os.path.join(out_dir, 'method_window.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k not in ('params', 'prior', 'curves')}, indent=1, default=float))
