"""GARANCIA-GO: simulation-calibrated conformal guarantees for boundary conditions, the recharge coefficient and the
dispersion-zone width, when the only time series is rain.

T1  RINDERTIMI-GO test bed (scenario B: rain + four head loggers). Reconstructor: ensemble smoother from a prior
    ensemble given the rain (128 members), with the exact solver as observation operator. Its bands are compared with
    the exact posterior and corrected by (a) conformal risk control of the fraction of weeks outside the band
    (Angelopoulos et al., ICLR 2024, Theorem 1) and (b) split conformal prediction with a sup-norm score (whole-function
    coverage). Calibration cases are simulated from the physical prior, since boundary conditions are never observed.
T1A Scenario A: the rain is the only time series (no head reading). Same guarantees; the half-widths in physical units
    against scenario B give what four loggers buy.
T2  The same guarantees for few calibration simulations (n = 10 ... 200), over random calibration sets.
T3  Field check: the field draws from a shifted prior. Held-out head readings give a conformal p-value against the
    simulated cases (prior-data conflict test); then the prior is widened and the bands recalibrated.
T4  Fushe-Kuqe chloride calibration (chloride_fk, 20 000 prior draws): simulation-based coverage of the importance-
    sampling intervals for the recharge R, the K scale eta and the dispersive transition-zone width w, their
    conformal correction, and the calibrated interval for w with the real facts; the real facts one group at a time
    (heads only, chloride only, all), which shows that the heads say nothing about w.

usage: python gar_exp.py   (writes res/gar_exp.json, res/gar_exp_log.txt and res/gar_case.npz)"""
import copy
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'rindertimi_go'))
import rgo_model as M  # noqa: E402

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
NENS = 128
CH = ('eta', 'qL', 'r', 'h0')
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


# ------------------------------------------------------------------------------------------------ test bed pieces
def solver_matrices():
    nx, nt = M.NX, M.NT
    z_t, z_x = np.zeros((nt, nt)), np.zeros((nx, nt))
    return dict(h0=M.simulate(np.eye(nx), np.zeros((nt, nx)), np.zeros((nt, nx)), np.zeros((nt, nx)), Q=0.0).reshape(nx * nt, nx),
                eta=M.simulate(z_x, np.eye(nt), z_t, z_t, Q=0.0).reshape(nx * nt, nt),
                qL=M.simulate(z_x, z_t, np.eye(nt), z_t, Q=0.0).reshape(nx * nt, nt),
                r=M.simulate(z_x, z_t, z_t, np.eye(nt), Q=0.0).reshape(nx * nt, nt),
                cQ=M.simulate(np.zeros((nx, 1)), np.zeros((nt, 1)), np.zeros((nt, 1)), np.zeros((nt, 1))).reshape(nx * nt))


def daily_rain(rng):
    nd = M.SPIN + M.NT * 7
    start = rng.uniform(0, 365)
    t = start + np.arange(nd)
    lam, abar = M.SM.rain_rates(t)
    lam = lam * np.exp(M.PRI['ymult_lsd'] * rng.standard_normal())
    k = rng.poisson(lam)
    return np.where(k > 0, rng.gamma(np.maximum(k, 1), abar), 0.0)


def filtered(Pd, tau):
    """weekly mean of the Erlang-2 filtered rain inside the window (mm/d)."""
    return M.SM.erlang2(Pd, tau)[M.SPIN:].reshape(M.NT, 7).mean(1)


class Bed:
    def __init__(self, shift=None, widen=None, tau_prior_lsd=0.0):
        """shift: the field truth departs from the simulator prior; widen: the prior used by the reconstructor and
        the calibration simulations is widened."""
        self.G, self.cQ = M.response_matrix()
        self.mu, self.Sig = M.prior_z()
        self.L = np.linalg.cholesky(self.Sig + 1e-12 * np.eye(M.NZ))
        self.Rm = solver_matrices()
        self.shift = shift or {}
        self.tau_lsd = tau_prior_lsd                 # > 0: the reconstructor's members carry their own vadose delay
        w = widen or {}
        self.wmu = self.mu.copy(); self.wL = self.L.copy()
        self.k_lsd = M.KAP_LSD * w.get('kappa_lsd', 1.0)
        if w:
            D = np.ones(M.NZ)
            D[M.SL['meta']] = w.get('mean_sd', 1.0); D[M.SL['mq']] = w.get('mean_sd', 1.0)
            self.wL = np.diag(D) @ self.L

    def truth(self, rng, field=False):
        Pd = daily_rain(rng)
        f_model = filtered(Pd, M.TAU_V)
        tau_true = self.shift.get('tau', M.TAU_V) if field else M.TAU_V
        f = filtered(Pd, tau_true)
        z = self.mu + self.L @ rng.standard_normal(M.NZ)
        lk = np.log(M.KAP_MED) + M.KAP_LSD * rng.standard_normal()
        if field:
            z = z.copy()
            z[M.SL['meta']] += self.shift.get('eta_m', 0.0); z[M.SL['mq']] += self.shift.get('q_m', 0.0)
            lk += self.shift.get('log_kappa', 0.0)
        kap = np.exp(lk)
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, self.G, self.cQ, gk)
        truth = dict(h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0], f=f, kappa=kap, gk=gk,
                     f_model=f_model, Pd=Pd)
        rows = M.observation_rows(rng, 'B')
        y = np.array([truth['h'].reshape(-1)[i] + M.SIG_H * rng.standard_normal() for _, i in rows])
        # one reading in four is held out for the field check; the update uses the others
        hold = rng.random(len(rows)) < 0.25
        return truth, rows, y, hold

    def reconstruct(self, rng, truth, rows, y, use):
        f = truth['f_model']                         # the reconstructor knows the rain, filtered with its own delay
        z = self.wmu[:, None] + self.wL @ rng.standard_normal((M.NZ, NENS))
        kap = M.KAP_MED * np.exp(self.k_lsd * rng.standard_normal(NENS))
        if self.tau_lsd > 0:
            taus = M.TAU_V * np.exp(self.tau_lsd * rng.standard_normal(NENS))
            F = np.array([filtered(truth['Pd'], t) for t in taus])                        # (NENS, NT)
            gks = np.array([M.kappa_response(fi) for fi in F])                            # (NENS, NX*NT)
            h = (self.G @ z + (gks * kap[:, None]).T + self.cQ[:, None]).reshape(M.NX, M.NT, -1)
            fl = dict(h=np.moveaxis(h, 2, 0), eta=(z[M.SL['deta']] + z[M.SL['meta']]).T,
                      qL=(z[M.SL['dq']] + z[M.SL['mq']]).T, r=kap[:, None] * F + z[M.SL['e']].T)
        else:
            F = np.broadcast_to(f, (NENS, M.NT))
            fl = M.fields_from_z(z, kap, f, self.G, self.cQ, M.kappa_response(f))
        X = np.concatenate([fl['h'][:, :, 0], fl['eta'], fl['qL'], fl['r']], axis=1)
        nx, nt = M.NX, M.NT
        rr = [rows[k][1] for k in range(len(rows)) if use[k]]
        if rr:
            Hm = np.array([np.concatenate([self.Rm['h0'][i], self.Rm['eta'][i], self.Rm['qL'][i], self.Rm['r'][i]]) for i in rr])
            c = self.Rm['cQ'][rr]; yy = y[use]
            Y = X @ Hm.T + c
            Xc, Yc = X - X.mean(0), Y - Y.mean(0)
            Cxy = Xc.T @ Yc / (NENS - 1); Cyy = Yc.T @ Yc / (NENS - 1)
            K = np.linalg.solve(Cyy + M.SIG_H ** 2 * np.eye(len(yy)), Cxy.T).T
            Xa = X + (yy[None] + M.SIG_H * rng.standard_normal((NENS, len(yy))) - Y) @ K.T
        else:                                        # rain only: the prior ensemble given the rain is the answer
            Xa = X
        h0, eta, qL, r = Xa[:, :nx], Xa[:, nx:nx + nt], Xa[:, nx + nt:nx + 2 * nt], Xa[:, nx + 2 * nt:]
        kap_a = np.sum(r * F, 1) / np.sum(F * F, 1)  # least-squares recharge coefficient of each member, against its own filtered rain
        ens = dict(eta=eta, qL=qL, r=r, h0=h0, kappa=kap_a)
        out = {k: (v.mean(0), v.std(0) + 1e-9) for k, v in ens.items()}
        # predictive heads at the held-out readings (the observable proxy of the field check)
        ho = [rows[k][1] for k in range(len(rows)) if not use[k]]
        if ho:
            Hh = np.array([np.concatenate([self.Rm['h0'][i], self.Rm['eta'][i], self.Rm['qL'][i], self.Rm['r'][i]]) for i in ho])
            Yh = Xa @ Hh.T + self.Rm['cQ'][ho]
            zres = np.abs(y[~use] - Yh.mean(0)) / np.sqrt(Yh.var(0) + M.SIG_H ** 2)
            out['check'] = float(np.mean(zres))
        else:
            out['check'] = 0.0
        return out


def targets(truth):
    return dict(eta=truth['eta'], qL=truth['qL'], r=truth['r'], h0=truth['h'][:, 0], kappa=np.array([truth['kappa']]))


def run_cases(bed, n, seed, exact=False, field=False, rain_only=False):
    """rain_only: scenario A, the reconstructor and the exact posterior see the rain and no head reading."""
    rng = np.random.default_rng(seed)
    cases = []
    for i in range(n):
        truth, rows, y, hold = bed.truth(rng, field=field)
        if rain_only:
            hold = np.ones(len(rows), bool)
        rec = bed.reconstruct(rng, truth, rows, y, ~hold)
        c = dict(t=targets(truth), m={k: rec[k][0] for k in CH + ('kappa',)}, s={k: rec[k][1] for k in CH + ('kappa',)},
                 check=rec['check'], P=truth['Pd'][M.SPIN:].reshape(M.NT, 7).sum(1), f=truth['f'],
                 obs=[(rows[k][1], float(y[k])) for k in range(len(rows)) if not hold[k]])
        if exact:
            use_rows = [rows[k] for k in range(len(rows)) if not hold[k]]
            ex = M.exact_posterior(y[~hold], use_rows, truth['f'], bed.G, bed.cQ, bed.mu, bed.Sig, rng=rng, nsamp=1000)
            S = ex['samples']
            q = {}
            for k, v in (('eta', S['eta']), ('qL', S['qL']), ('r', S['r']), ('h0', S['h'][:, :, 0]),
                         ('kappa', ex['kappa_samples'][:, None])):
                lo, hi = np.quantile(v, [ALPHA / 2, 1 - ALPHA / 2], axis=0)
                q[k] = (lo, hi)
            c['ex'] = q
        cases.append(c)
    return cases


# ------------------------------------------------------------------------------------------------ conformal tools
GRID = np.linspace(0.0, 40.0, 4001)       # lambda grid, step 0.01, far beyond every simulated score


def resid(c, k):
    """standardised departures of the truth from the reconstruction, one per time (or space) point."""
    return np.abs(c['t'][k] - c['m'][k]) / c['s'][k]


def loss_matrix(cases, k):
    """L_i(lambda) on the grid: fraction of points of case i outside the band m +- lambda s (non-increasing)."""
    return np.array([(resid(c, k)[:, None] > GRID[None, :]).mean(0) for c in cases])


def crc_lambda(L, alpha=ALPHA, B=1.0):
    """conformal risk control (Theorem 1 of Angelopoulos et al., 2024): the smallest lambda with
    n/(n+1) R_n(lambda) + B/(n+1) <= alpha."""
    n = len(L)
    ok = n / (n + 1) * L.mean(0) + B / (n + 1) <= alpha
    return float(GRID[np.argmax(ok)]) if ok.any() else float(GRID[-1])


def cp_quantile(scores, alpha=ALPHA):
    n = len(scores)
    k = int(np.ceil((1 - alpha) * (n + 1)))
    return float(np.sort(scores)[k - 1]) if k <= n else np.inf


def sup_scores(cases, k):
    return np.array([resid(c, k).max() for c in cases])


def evaluate(test, k, lam, exact=True):
    fo = np.mean([np.mean(resid(c, k) > lam) for c in test])
    sim = np.mean(sup_scores(test, k) <= lam)
    out = dict(frac_out=float(fo), simultaneous=float(sim))
    if exact:
        out['width_vs_exact'] = float(np.mean([np.mean(2 * lam * c['s'][k]) / np.mean(c['ex'][k][1] - c['ex'][k][0])
                                               for c in test]))
    return out


def exact_scores(test, k):
    fo = np.mean([np.mean((c['t'][k] < c['ex'][k][0]) | (c['t'][k] > c['ex'][k][1])) for c in test])
    sim = np.mean([np.all((c['t'][k] >= c['ex'][k][0]) & (c['t'][k] <= c['ex'][k][1])) for c in test])
    return dict(frac_out=float(fo), simultaneous=float(sim), width_vs_exact=1.0)


# ------------------------------------------------------------------------------------------------ T1-T3
def split_eval(pool, k, n_cal, reps, rng, with_exact=True):
    """average over random calibration/test splits of an exchangeable pool: estimates the expected test risk and
    coverage that the conformal guarantees bound."""
    L = loss_matrix(pool, k); Ssup = sup_scores(pool, k)
    ewid = np.array([np.mean(c['ex'][k][1] - c['ex'][k][0]) for c in pool]) if with_exact else None
    swid = np.array([np.mean(2 * c['s'][k]) for c in pool])
    crc, sup, wc, ws = [], [], [], []
    for _ in range(reps):
        perm = rng.permutation(len(pool)); ci, ti = perm[:n_cal], perm[n_cal:]
        lam = crc_lambda(L[ci]); q = cp_quantile(Ssup[ci])
        crc.append(L[ti, int(round(lam / GRID[1]))].mean())
        sup.append(np.mean(Ssup[ti] <= q) if np.isfinite(q) else 1.0)
        if with_exact:
            wc.append(np.mean(lam * swid[ti] / ewid[ti])); ws.append(np.mean(q * swid[ti] / ewid[ti]) if np.isfinite(q) else np.inf)
    out = dict(crc_risk=float(np.mean(crc)), crc_risk_p10=float(np.quantile(crc, 0.1)), crc_risk_p90=float(np.quantile(crc, 0.9)),
               sup_cover=float(np.mean(sup)), sup_cover_p10=float(np.quantile(sup, 0.1)), sup_cover_p90=float(np.quantile(sup, 0.9)))
    if with_exact:
        out.update(crc_width=float(np.mean(wc)), sup_width=float(np.mean(ws)))
    return out


def t123(out):
    t0 = time.time()
    bed = Bed()
    pool = run_cases(bed, 500, 1, exact=True)
    log(f'T1 pool of {len(pool)} cases simulated in {time.time() - t0:.0f}s')
    rng = np.random.default_rng(5)
    T1 = {}
    for k in CH + ('kappa',):
        raw = evaluate(pool, k, 1.645)
        sp = split_eval(pool, k, 200, 1000, rng)
        T1[k] = dict(exact=exact_scores(pool, k), raw=raw, split=sp, lam_crc=crc_lambda(loss_matrix(pool, k)),
                     lam_sup=cp_quantile(sup_scores(pool, k)), max_score=float(sup_scores(pool, k).max()))
        log(f'T1 {k:5s} exact {T1[k]["exact"]["frac_out"]:.3f}/{T1[k]["exact"]["simultaneous"]:.2f} | raw ES '
            f'{raw["frac_out"]:.3f}/{raw["simultaneous"]:.2f} w{raw["width_vs_exact"]:.2f} | CRC risk {sp["crc_risk"]:.3f} '
            f'[{sp["crc_risk_p10"]:.3f}, {sp["crc_risk_p90"]:.3f}] w{sp["crc_width"]:.2f} | sup-CP cover {sp["sup_cover"]:.3f} '
            f'[{sp["sup_cover_p10"]:.3f}, {sp["sup_cover_p90"]:.3f}] w{sp["sup_width"]:.2f}')
    out['T1'] = T1
    out['T1_halfwidth'] = halfwidths(pool, T1)
    save_case(pool, T1)
    T2 = {}
    for n in (10, 20, 50, 100, 200):
        T2[str(n)] = {k: split_eval(pool, k, n, 1000, rng, with_exact=False) for k in ('qL', 'r', 'kappa')}
        log(f'T2 n={n:3d} ' + ' | '.join(f'{k}: CRC risk {T2[str(n)][k]["crc_risk"]:.3f} (p90 {T2[str(n)][k]["crc_risk_p90"]:.3f}), '
                                         f'sup cover {T2[str(n)][k]["sup_cover"]:.3f} (p10 {T2[str(n)][k]["sup_cover_p10"]:.3f})'
                                         for k in ('qL', 'r', 'kappa')))
    out['T2'] = T2
    # T3: the field departs from the simulator, (a) in parameters the data inform, (b) in structure
    cal_check = np.array([c['check'] for c in pool])
    pv = lambda c, ref: (1 + np.sum(ref >= c['check'])) / (len(ref) + 1)
    T3 = {}
    for name, shift in (('parameters', dict(q_m=0.8, log_kappa=np.log(1.5), eta_m=0.10)), ('delay', dict(tau=35.0))):
        field = run_cases(Bed(shift=shift), 300, 3, field=True)
        res = dict(shift={k: float(v) for k, v in shift.items()}, alarm=float(np.mean([pv(c, cal_check) <= ALPHA for c in field])))
        for k in CH + ('kappa',):
            res[k] = dict(crc=float(np.mean([np.mean(resid(c, k) > T1[k]['lam_crc']) for c in field])),
                          sup=float(np.mean(sup_scores(field, k) <= T1[k]['lam_sup'])))
        res['alarm_null'] = float(np.mean([pv(c, cal_check) <= ALPHA for c in pool]))
        T3[name] = res
        log(f'T3 {name}: alarm {res["alarm"]:.2f} (null {res["alarm_null"]:.2f}); '
            + ' '.join(f'{k} CRC {res[k]["crc"]:.3f} sup {res[k]["sup"]:.2f}' for k in CH + ('kappa',)))
    # repair of the structural error: the delay enters the prior of the reconstructor and of the calibration cases
    bed_t = Bed(tau_prior_lsd=0.5)
    pool_t = run_cases_tau(bed_t, 300, 6)
    field_t = run_cases(Bed(shift=dict(tau=35.0), tau_prior_lsd=0.5), 300, 3, field=True)
    ref_t = np.array([c['check'] for c in pool_t])
    rep = dict(tau_prior_lsd=0.5, alarm=float(np.mean([pv(c, ref_t) <= ALPHA for c in field_t])),
               max_score={k: float(sup_scores(pool_t, k).max()) for k in CH + ('kappa',)})
    for k in CH + ('kappa',):
        lam = crc_lambda(loss_matrix(pool_t, k)); q = cp_quantile(sup_scores(pool_t, k))
        rep[k] = dict(crc=float(np.mean([np.mean(resid(c, k) > lam) for c in field_t])),
                      sup=float(np.mean(sup_scores(field_t, k) <= q)),
                      width_ratio=float(np.mean([np.mean(lam * c['s'][k]) for c in field_t]) /
                                        np.mean([np.mean(T1[k]['lam_crc'] * c['s'][k]) for c in pool])))
    T3['delay_repaired'] = rep
    log('T3 delay repaired (delay in the prior): alarm ' + f'{rep["alarm"]:.2f}; '
        + ' '.join(f'{k} CRC {rep[k]["crc"]:.3f} sup {rep[k]["sup"]:.2f} width x{rep[k]["width_ratio"]:.2f}' for k in CH + ('kappa',)))
    out['T3'] = T3


UNITS = dict(eta='m', qL='m2/d', r='mm/d', h0='m', kappa='-')


def halfwidths(pool, T):
    """mean half-width of the bands in physical units: exact posterior, CRC (lambda s) and sup-norm (q s)."""
    out = {}
    for k in CH + ('kappa',):
        ex = float(np.mean([np.mean(c['ex'][k][1] - c['ex'][k][0]) / 2 for c in pool])) if 'ex' in pool[0] else None
        s = np.mean([np.mean(c['s'][k]) for c in pool])
        out[k] = dict(exact=ex, crc=float(T[k]['lam_crc'] * s), sup=float(T[k]['lam_sup'] * s), units=UNITS[k])
    return out


def save_case(pool, T):
    """one test case for the band figure: the case whose sup score for r is the median of the pool."""
    sc = sup_scores(pool, 'r')
    i = int(np.argsort(sc)[len(sc) // 2])
    c = pool[i]
    d = dict(P=c['P'], f=c['f'], obs_idx=np.array([o[0] for o in c['obs']]), obs_y=np.array([o[1] for o in c['obs']]))
    for k in CH + ('kappa',):
        d[f'{k}_t'] = c['t'][k]; d[f'{k}_m'] = c['m'][k]; d[f'{k}_s'] = c['s'][k]
        d[f'{k}_lo'] = c['ex'][k][0]; d[f'{k}_hi'] = c['ex'][k][1]
        d[f'{k}_lam_crc'] = T[k]['lam_crc']; d[f'{k}_lam_sup'] = T[k]['lam_sup']
    np.savez_compressed(os.path.join(RES, 'gar_case.npz'), index=i, **d)


def t1_rain_only(out):
    """scenario A: the rain is the only time series. The same guarantees, and what four loggers buy."""
    t0 = time.time()
    bed = Bed()
    pool = run_cases(bed, 500, 21, exact=True, rain_only=True)
    log(f'T1A pool of {len(pool)} rain-only cases simulated in {time.time() - t0:.0f}s')
    rng = np.random.default_rng(22)
    T = {}
    for k in CH + ('kappa',):
        T[k] = dict(exact=exact_scores(pool, k), raw=evaluate(pool, k, 1.645), split=split_eval(pool, k, 200, 1000, rng),
                    lam_crc=crc_lambda(loss_matrix(pool, k)), lam_sup=cp_quantile(sup_scores(pool, k)),
                    max_score=float(sup_scores(pool, k).max()))
    hw = halfwidths(pool, T)
    for k in CH + ('kappa',):
        sp = T[k]['split']
        log(f'T1A {k:5s} exact {T[k]["exact"]["frac_out"]:.3f} | raw {T[k]["raw"]["frac_out"]:.3f} | CRC risk {sp["crc_risk"]:.3f} '
            f'w{sp["crc_width"]:.2f} | sup cover {sp["sup_cover"]:.3f} w{sp["sup_width"]:.2f} | half-width exact '
            f'{hw[k]["exact"]:.3f} CRC {hw[k]["crc"]:.3f} sup {hw[k]["sup"]:.3f} {hw[k]["units"]}')
    out['T1A'] = T
    out['T1A_halfwidth'] = hw


def run_cases_tau(bed, n, seed):
    """calibration cases whose truths draw the vadose delay from the same prior as the reconstructor."""
    rng = np.random.default_rng(seed)
    cases = []
    for i in range(n):
        tau = M.TAU_V * np.exp(bed.tau_lsd * rng.standard_normal())
        b = copy.copy(bed); b.shift = dict(tau=tau)
        truth, rows, y, hold = b.truth(rng, field=True)
        rec = b.reconstruct(rng, truth, rows, y, ~hold)
        cases.append(dict(t=targets(truth), m={k: rec[k][0] for k in CH + ('kappa',)},
                          s={k: rec[k][1] for k in CH + ('kappa',)}, check=rec['check']))
    return cases


def run_cases_widened(bed, n, seed):
    """calibration truths from the widened prior (the mean departures and log kappa scaled up)."""
    rng = np.random.default_rng(seed)
    cases = []
    for i in range(n):
        P, f = M.rain_weeks(rng, 1); f = f[:, 0]
        z = bed.wmu + bed.wL @ rng.standard_normal(M.NZ)
        kap = M.KAP_MED * np.exp(bed.k_lsd * rng.standard_normal())
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, bed.G, bed.cQ, gk)
        truth = dict(h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0], f=f, kappa=kap, gk=gk)
        rows = M.observation_rows(rng, 'B')
        y = np.array([truth['h'].reshape(-1)[j] + M.SIG_H * rng.standard_normal() for _, j in rows])
        hold = rng.random(len(rows)) < 0.25
        rec = bed.reconstruct(rng, truth, rows, y, ~hold)
        cases.append(dict(t=targets(truth), m={k: rec[k][0] for k in CH + ('kappa',)},
                          s={k: rec[k][1] for k in CH + ('kappa',)}, check=rec['check']))
    return cases


# ------------------------------------------------------------------------------------------------ T4 Fushe-Kuqe
def t4(out):
    sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))
    z = np.load(os.path.join(ROOT, 'chloride_fk', 'results', 'calib_ensemble.npz'))
    S = z['S']; N = len(S)
    OBS = dict(area=0.15, area_sd=0.05, hlit=3.0, hlit_sd=1.0, f_sw=0.047, logsd=0.7, cl_ne=30.0, cl_ne_s=5.0)
    par = dict(w=np.log(z['w']), R=np.log(np.maximum(z['R'], 1e-12)), eta=np.log(z['eta']))
    lsig = lambda x: -np.logaddexp(0.0, -x)                     # log of the logistic function

    def loglik(obs):
        ll = -0.5 * ((S[:, 0] - obs['area']) / OBS['area_sd']) ** 2
        ll += -0.5 * ((S[:, 1] - obs['hlit']) / OBS['hlit_sd']) ** 2
        ll += -0.5 * ((np.log(np.maximum(S[:, 10], 1e-6)) - np.log(obs['f_sw'])) / OBS['logsd']) ** 2
        x = (obs['cl_ne'] - S[:, 4]) / OBS['cl_ne_s']
        ll += lsig(x) if obs['below'] else lsig(-x)
        return ll

    def post(ll, exclude=None):
        w = np.exp(ll - ll.max())
        if exclude is not None:
            w[exclude] = 0.0
        w /= w.sum()
        res = {}
        for k, v in par.items():
            m = float(np.sum(w * v)); s = float(np.sqrt(np.sum(w * (v - m) ** 2)))
            o = np.argsort(v); c = np.cumsum(w[o])
            lo, hi = v[o][np.searchsorted(c, ALPHA / 2)], v[o][min(np.searchsorted(c, 1 - ALPHA / 2), N - 1)]
            res[k] = (m, s, float(lo), float(hi))
        return res, float(1 / np.sum(w ** 2))

    rng = np.random.default_rng(8)
    idx = rng.choice(N, 600, replace=False)
    recs = []
    for j in idx:
        obs = dict(area=S[j, 0] + OBS['area_sd'] * rng.standard_normal(), hlit=S[j, 1] + OBS['hlit_sd'] * rng.standard_normal(),
                   f_sw=np.exp(np.log(max(S[j, 10], 1e-6)) + OBS['logsd'] * rng.standard_normal()), cl_ne=OBS['cl_ne'],
                   below=bool(rng.random() < 1 / (1 + np.exp(-(OBS['cl_ne'] - S[j, 4]) / OBS['cl_ne_s']))))
        p, ess = post(loglik(obs), exclude=j)
        recs.append(dict(j=int(j), p=p, ess=ess))
    cal, test = recs[:300], recs[300:]
    real_obs = dict(area=OBS['area'], hlit=OBS['hlit'], f_sw=OBS['f_sw'], cl_ne=OBS['cl_ne'], below=True)
    real, real_ess = post(loglik(real_obs))
    T4 = dict(ess_median=float(np.median([r['ess'] for r in recs])), real_ess=real_ess)
    for k in par:
        cov = np.mean([(r['p'][k][2] <= par[k][r['j']] <= r['p'][k][3]) for r in test])
        sc = np.array([abs(par[k][r['j']] - r['p'][k][0]) / r['p'][k][1] for r in cal])
        q = cp_quantile(sc)
        cov_cp = np.mean([abs(par[k][r['j']] - r['p'][k][0]) <= q * r['p'][k][1] for r in test])
        wid_is = np.mean([r['p'][k][3] - r['p'][k][2] for r in test]); wid_cp = np.mean([2 * q * r['p'][k][1] for r in test])
        m, s, lo, hi = real[k]
        T4[k] = dict(cover_is=float(cov), cover_conformal=float(cov_cp), q=float(q), width_ratio=float(wid_cp / wid_is),
                     real_is=[float(np.exp(lo)), float(np.exp(m)), float(np.exp(hi))],
                     real_conformal=[float(np.exp(m - q * s)), float(np.exp(m)), float(np.exp(m + q * s))],
                     prior=[float(np.exp(np.quantile(par[k], ALPHA / 2))), float(np.exp(np.median(par[k]))),
                            float(np.exp(np.quantile(par[k], 1 - ALPHA / 2)))])
        log(f'T4 {k:4s} IS 90% coverage {cov:.3f} -> conformal {cov_cp:.3f} (q {q:.2f}, width x{wid_cp / wid_is:.2f}); '
            f'Fushe-Kuqe: prior {np.round(T4[k]["prior"], 4)}, IS {np.round(T4[k]["real_is"], 4)}, '
            f'conformal {np.round(T4[k]["real_conformal"], 4)}')
    log(f'T4 ESS median {T4["ess_median"]:.0f}, real facts ESS {real_ess:.0f}')
    # which fact informs which unknown: the real facts one group at a time, and the prior rank correlations
    parts = dict(area=-0.5 * ((S[:, 0] - real_obs['area']) / OBS['area_sd']) ** 2,
                 hlit=-0.5 * ((S[:, 1] - real_obs['hlit']) / OBS['hlit_sd']) ** 2,
                 fsw=-0.5 * ((np.log(np.maximum(S[:, 10], 1e-6)) - np.log(real_obs['f_sw'])) / OBS['logsd']) ** 2,
                 ne=lsig((real_obs['cl_ne'] - S[:, 4]) / OBS['cl_ne_s']))
    groups = dict(heads=['hlit'], chloride=['area', 'fsw', 'ne'], all=['area', 'hlit', 'fsw', 'ne'])
    T4['subsets'] = {}
    for g, keys in groups.items():
        p, ess = post(sum(parts[k] for k in keys))
        T4['subsets'][g] = dict(facts=keys, ess=ess, **{k: [float(np.exp(p[k][2])), float(np.exp(p[k][0])), float(np.exp(p[k][3]))]
                                                        for k in par})
        log(f'T4 facts {g:8s} ESS {ess:7.0f} ' + ' '.join(f'{k} {np.round(T4["subsets"][g][k], 5)}' for k in par))
    rank = lambda v: np.argsort(np.argsort(v)) / (len(v) - 1.0)
    stats = dict(area=S[:, 0], hlit=S[:, 1], fsw=np.log(np.maximum(S[:, 10], 1e-6)), cl_ne=S[:, 4])
    T4['rank_corr'] = {k: {s: float(np.corrcoef(rank(par[k]), rank(v))[0, 1]) for s, v in stats.items()} for k in par}
    log('T4 prior rank correlations ' + ' | '.join(f'{k}: ' + ' '.join(f'{s} {v:+.2f}' for s, v in T4['rank_corr'][k].items())
                                                    for k in par))
    out['T4'] = T4


def main():
    os.makedirs(RES, exist_ok=True)
    t0 = time.time()
    out = dict(alpha=ALPHA, n_ens=NENS)
    t4(out)
    t123(out)
    t1_rain_only(out)
    out['seconds'] = time.time() - t0
    with open(os.path.join(RES, 'gar_exp.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'gar_exp_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
