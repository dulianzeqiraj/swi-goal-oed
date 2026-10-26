"""PUSI-GO, stage 2: well placement with the chemistry threshold against the head proxy (res/ens.npz -> res/pusi.json).

Proposition P1 of the document: in the Strack model the potential phi is linear in every well rate, and the
screen-averaged chloride of a well is a non-increasing function of phi at the well, so
    {Cl_w > 250 mg/L} = {phi_w < phi*_w(p)},
a threshold event on a linear functional with a RANDOM threshold phi*_w that carries the hydrochemistry (seawater
chloride Cl_s, freshwater chloride, width w of the mixing zone, screen depth and length, top depth d, thickness B).
The head proxy {h_w < 1 m} of PRAG-MAR is the same functional with a threshold phi_h(d) that carries no chemistry.
All objectives below differ only in the threshold tau_w; the margin is M_w = phi_w - tau_w.

Parts (weighted calibration ensemble, split by parity: even draws = design set D, odd draws = evaluation set V):
  A  thresholds and agreement of the events at the supply wells A1 and P10 (shallow screen, top 40 m), with the
     pumping rates set so that each well's own P(Cl > 250) = 1/2 on D (the PRAG-MAR rule, now on chemistry)
  B  three recharge wells (5 000 m3/d each, >= 1 km from the supply wells, >= 6 km apart in northing): closed-form
     and exact-greedy designs for the head proxy, a calibrated head threshold and the chemistry threshold; the fk
     head-proxy designs; all evaluated on V
  C  three monitoring observations among 16 wells x {head, log10 Cl at three depths}: exact EIG of the chemistry
     event by likelihood reweighting, greedy; heads only against chloride
  E  screen length of the supply wells: risk and the largest pumping scale with P(A or B fails) <= 0.10
Run: python3 pusi_analysis.py     (about 5 minutes)
"""
import os, sys, json, time
import numpy as np
from scipy.stats import norm, multivariate_normal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))
import fkcl_model as M  # noqa: E402

RES = os.path.join(HERE, 'res')
DELTA, CLF, LIM, HC, SCREEN = M.DELTA, M.CL_F, M.CL_LIMIT, 1.0, M.SCREEN
QREC, NORTH = 5000.0, 6.0
SIG_H, SIG_LCL = 0.2, 0.1                      # head error (m), log10-chloride error
NY = 2000                                      # outer draws of the EIG estimator
RISK_MAX = 0.10
YIELD_SCREEN = 20.0                            # m, supply-well screen of the safe-yield analysis (part C)

m = M.Model()
Z = np.load(os.path.join(RES, 'ens.npz'))
phi0, uA, uB = Z['phi0'], Z['uA'], Z['uB']
cS, cM, cR = Z['cS'], Z['cM'], Z['cR']
NSUP, NMON = len(cS), len(cM)
iS = np.arange(NSUP); iM = NSUP + np.arange(NMON); iR = NSUP + NMON + np.arange(len(cR))
P = {k: Z[k] for k in ('R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s')}
W = Z['weight'] / Z['weight'].sum()
N = len(W)
D, V = np.arange(0, N, 2), np.arange(1, N, 2)
wD, wV = W[D] / W[D].sum(), W[V] / W[V].sum()
ess = lambda w: float(1.0 / np.sum(w ** 2))
mon_ids = [str(x) for x in Z['mon_ids']]


# ---------------------------------------------------------------- state and thresholds (vectorised over draws)
def geom(cells):
    d = np.maximum(m.cover[cells][None, :] - P['ground'][:, None], 1.0)
    B = P['b_e'][:, None] + (P['b_c'] - P['b_e'])[:, None] * np.clip(1.0 - m.dist[cells][None, :] / P['L_B'][:, None], 0.0, 1.0)
    return d, B


def state(phi, d, B):
    ph = np.maximum(phi, 0.0)
    z2 = phi < 0.5 * DELTA * B ** 2
    h1 = phi / B + DELTA * (d + 0.5 * B)
    h = np.where(z2, DELTA * d + np.sqrt(2 * DELTA * ph), h1)
    zeta = np.where(z2, d + np.sqrt(2 * ph / DELTA), h1 / DELTA)
    return h, zeta


def chloride(phi, d, B, depth='sh', length=SCREEN):
    _, zeta = state(phi, d, B)
    L = np.minimum(length, B)
    w = P['w'][:, None] if np.ndim(phi) == 2 else P['w']
    cls = P['Cl_s'][:, None] if np.ndim(phi) == 2 else P['Cl_s']
    if depth == 'sh':
        z1 = d
    elif depth == 'mid':
        z1 = d + 0.5 * B - 0.5 * L
    else:
        z1 = d + B - L
    f = M.screen_average(z1, z1 + L, zeta, w)
    return CLF + f * (cls - CLF)


def bisect(fun, lo, hi, it=90):
    """root of a non-decreasing fun(phi) - 0 per entry (arrays)."""
    lo, hi = np.array(lo, float), np.array(hi, float)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        up = fun(mid) > 0
        hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
    return 0.5 * (lo + hi)


dS, BS = geom(cS)


def tau_chem(length=SCREEN):
    """phi* with screen chloride = LIM (top `length` m of the aquifer) at the supply wells, per draw."""
    return bisect(lambda ph: LIM - chloride(ph, dS, BS, 'sh', length), np.full(dS.shape, -1.0), np.full(dS.shape, 5e4))


def tau_head(hc):
    """phi at which the head equals hc (per draw and well); -inf when the head can never fall below hc."""
    hmin = DELTA * dS
    t = bisect(lambda ph: state(ph, dS, BS)[0] - hc, np.full(dS.shape, 0.0), np.full(dS.shape, 5e4))
    return np.where(hmin >= hc, -1e12, t)


def phi_sup(QA, QB):
    return phi0[:, iS] - QA * uA[:, iS] - QB * uB[:, iS]


def wq(x, w):
    o = np.argsort(x); c = np.cumsum(w[o]); return float(x[o][np.searchsorted(c, 0.5)])


def calibrate(tau, idx, w):
    """Q_A, Q_B with each supply well's own P(phi_w < tau_w) = 1/2 on the set idx (both wells pumping)."""
    QA = QB = 0.0
    for _ in range(80):
        lo, hi = 0.0, 2e5
        for _ in range(70):
            mid = 0.5 * (lo + hi); ph = phi_sup(mid, QB)[idx, 0]
            lo, hi = (mid, hi) if np.sum(w * (ph < tau[idx, 0])) < 0.5 else (lo, mid)
        QA = 0.5 * (lo + hi)
        lo, hi = 0.0, 2e5
        for _ in range(70):
            mid = 0.5 * (lo + hi); ph = phi_sup(QA, mid)[idx, 1]
            lo, hi = (mid, hi) if np.sum(w * (ph < tau[idx, 1])) < 0.5 else (lo, mid)
        QBn = 0.5 * (lo + hi)
        if abs(QBn - QB) < 1e-4:
            QB = QBn; break
        QB = QBn
    return QA, QB


# ---------------------------------------------------------------- recharge designs
def resp(k):
    """(N, 2) rise of phi at A and B per unit recharge at candidate k (by symmetry of the flow operator)."""
    j = iR[k]
    return np.column_stack([uA[:, j], uB[:, j]])


RESP = np.stack([resp(k) for k in range(len(cR))], 1)          # (N, nR, 2)
RD = RESP[D]                                                    # design-set copy, used by the searches
NORTHING = m.cy[cR]


def margins(tau, Q, design=()):
    M_ = phi_sup(*Q) - tau
    for k in design:
        M_ = M_ + QREC * RESP[:, k, :]
    return M_


def risk(M_, idx, w):
    return float(np.sum(w * (M_[idx].min(1) < 0)))


def ok_north(design, k):
    return all(abs(NORTHING[k] - NORTHING[j]) >= NORTH - 1e-9 for j in design)


def closed_form(tau, Q, idx, w):
    """PRAG-MAR closed form on the margin: Gaussian moments of (M_A, M_B) on idx, top 3 by -dP/dq with the
    northing rule."""
    M_ = margins(tau, Q)[idx]
    mu = w @ M_; C = (M_ - mu).T @ ((M_ - mu) * w[:, None]); s = np.sqrt(np.diag(C)); r = C[0, 1] / (s[0] * s[1])
    a, b_ = mu / s
    g = np.einsum('i,ikw->kw', w, RESP[idx])
    r = float(np.clip(r, -0.999, 0.999))
    dP = (norm.pdf(a) / s[0] * norm.cdf((b_ - r * a) / np.sqrt(1 - r * r)) * g[:, 0]
          + norm.pdf(b_) / s[1] * norm.cdf((a - r * b_) / np.sqrt(1 - r * r)) * g[:, 1])
    design = []
    for k in np.argsort(-dP):
        if ok_north(design, k):
            design.append(int(k))
        if len(design) == 3:
            break
    p0 = 1 - multivariate_normal(mean=[0, 0], cov=[[1, r], [r, 1]]).cdf([a, b_])
    return design, dict(mu=mu.tolist(), s=s.tolist(), r=r, P_gauss=float(p0))


def greedy(tau, Q, idx, w, eps=1.0):
    """greedy minimisation of the smoothed ensemble risk (logistic, scale eps m^2) under the northing rule."""
    M_ = margins(tau, Q)[idx]
    design = []
    for _ in range(3):
        best, bk = np.inf, -1
        for k in range(len(cR)):
            if k in design or not ok_north(design, k):
                continue
            Mk = (M_ + QREC * (RD[:, k, :] if idx is D else RESP[idx, k, :])).min(1)
            val = np.sum(w / (1 + np.exp(np.clip(Mk / eps, -50, 50))))
            if val < best:
                best, bk = val, k
        design.append(bk); M_ = M_ + QREC * RESP[idx, bk, :]
    return design


def swap(design, tau, Q, idx, w, eps=1.0):
    """1-swap local search from `design`: replace one site at a time by any admissible candidate while the exact
    ensemble risk on idx falls (smoothed risk breaks ties)."""
    M0 = margins(tau, Q)[idx]
    RI = RD if idx is D else RESP[idx]
    def val(dsg):
        Mk = M0 + QREC * RI[:, dsg, :].sum(1)
        mn = Mk.min(1)
        return (float(np.sum(w * (mn < 0))), float(np.sum(w / (1 + np.exp(np.clip(mn / eps, -50, 50))))))
    cur = list(design); best = val(cur); improved = True
    while improved:
        improved = False
        for pos in range(len(cur)):
            rest = cur[:pos] + cur[pos + 1:]
            for k in range(len(cR)):
                if k in cur or not ok_north(rest, k):
                    continue
                trial = rest[:pos] + [k] + rest[pos:]
                v = val(trial)
                if v < best:
                    best, cur, improved = v, trial, True
    return cur


def name_cell(k):
    c = cR[k]
    return dict(x=float(m.cx[c]), y=float(m.cy[c]))


# ---------------------------------------------------------------- monitoring (exact EIG by reweighting)
def hb(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


def main():
    t0 = time.time()
    out = dict(n_draws=int(N), ess_design=ess(wD), ess_eval=ess(wV), q_recharge=QREC, limit_mg_L=LIM, h_c=HC,
               supply=[str(x) for x in Z['supply']], screen_m=SCREEN)
    # ------------------------------------------------ A: thresholds and pumping
    tC = tau_chem()
    tH = tau_head(HC)
    QA, QB = calibrate(tC, D, wD)
    out['pumping_m3_d'] = [QA, QB]
    phS = phi_sup(QA, QB)
    hS, _ = state(phS, dS, BS)
    # calibrated head threshold: each well's weighted median head on D
    hcal = [wq(hS[D, j], wD) for j in range(2)]
    tK = np.column_stack([tau_head(hcal[0])[:, 0], tau_head(hcal[1])[:, 1]])
    out['h_cal_m'] = hcal
    cl0 = chloride(phi0[:, iS], dS, BS)
    clQ = chloride(phS, dS, BS)
    fC, fH = phS < tC, phS < tH
    fK = phS < tK
    out['A'] = dict(
        head_nopump=[[wq(state(phi0[V, j], dS[V, j], BS[V, j])[0], wV)] for j in range(2)],
        head_pumped_median=[wq(hS[V, j], wV) for j in range(2)],
        P_chem_nopump=[float(np.sum(wV * (cl0[V, j] > LIM))) for j in range(2)],
        P_chem=[float(np.sum(wV * fC[V, j])) for j in range(2)], P_chem_any=float(np.sum(wV * fC[V].any(1))),
        P_proxy=[float(np.sum(wV * fH[V, j])) for j in range(2)], P_proxy_any=float(np.sum(wV * fH[V].any(1))),
        P_cal=[float(np.sum(wV * fK[V, j])) for j in range(2)], P_cal_any=float(np.sum(wV * fK[V].any(1))),
        agree_cal_chem=[float(np.sum(wV * (fK[V, j] == fC[V, j]))) for j in range(2)],
        tau_chem_q=[[float(np.percentile(tC[V, j], q)) for q in (5, 50, 95)] for j in range(2)],
        tau_head_q=[[float(np.percentile(tH[V, j], q)) for q in (5, 50, 95)] for j in range(2)],
        tau_chem_cv=[float(np.sqrt(np.cov(tC[V, j], aweights=wV)) / np.sum(wV * tC[V, j])) for j in range(2)],
        corr_tau_phi=[float(np.corrcoef(tC[V, j], phS[V, j])[0, 1]) for j in range(2)],
        cl_pumped_q=[[float(np.percentile(clQ[V, j], q)) for q in (5, 50, 95)] for j in range(2)],
    )
    # which parameters drive the chemistry threshold (rank correlation with log w, Cl_s, ground, b_c)
    from scipy.stats import spearmanr
    out['A']['tau_drivers'] = {k: [float(spearmanr(tC[V, j], v[V]).statistic) for j in range(2)]
                               for k, v in (('w', P['w']), ('Cl_s', P['Cl_s']), ('ground', P['ground']), ('b_c', P['b_c']), ('L_B', P['L_B']))}
    print('A', json.dumps(out['A'])[:900], f'Q = {QA:.0f}, {QB:.0f}', f'{time.time() - t0:.0f}s')

    # ------------------------------------------------ B: recharge designs
    taus = dict(chem=tC, proxy=tH, cal=tK)
    designs = {'none': []}
    info = {}
    kof = {int(c): k for k, c in enumerate(cR)}
    for nm, tau in taus.items():
        dsg, inf = closed_form(tau, (QA, QB), D, wD)
        designs[f'closed_{nm}'] = dsg; info[f'closed_{nm}'] = inf
        designs[f'greedy_{nm}'] = greedy(tau, (QA, QB), D, wD)
        # multi-start 1-swap search: from the greedy design, the two fk designs and 24 random admissible designs
        starts = [designs[f'greedy_{nm}'], [kof[int(c)] for c in Z['fk_prag_mar']], [kof[int(c)] for c in Z['fk_greedy']]]
        rs = np.random.default_rng(11)
        while len(starts) < 27:
            dsg = []
            for k in rs.permutation(len(cR)):
                if ok_north(dsg, int(k)):
                    dsg.append(int(k))
                if len(dsg) == 3:
                    break
            starts.append(dsg)
        cands = [swap(st, tau, (QA, QB), D, wD) for st in starts]
        M0 = margins(tau, (QA, QB))[D]
        score = lambda dsg: (float(np.sum(wD * ((M0 + QREC * RD[:, dsg, :].sum(1)).min(1) < 0))),
                             float(np.sum(wD / (1 + np.exp(np.clip((M0 + QREC * RD[:, dsg, :].sum(1)).min(1), -50, 50))))))
        designs[f'swap_{nm}'] = min(cands, key=score)
    designs['fk_prag_mar'] = [kof[int(c)] for c in Z['fk_prag_mar']]
    designs['fk_greedy'] = [kof[int(c)] for c in Z['fk_greedy']]
    res = {}
    for dn, dsg in designs.items():
        row = dict(sites=[name_cell(k) for k in dsg])
        for nm, tau in taus.items():
            Mv = margins(tau, (QA, QB), dsg)
            row[f'P_{nm}'] = risk(Mv, V, wV)
            row[f'P_{nm}_D'] = risk(Mv, D, wD)
        res[dn] = row
    # bootstrap of the paired risk difference on V (chem): closed_cal vs closed_chem, greedy_cal vs greedy_chem
    rng = np.random.default_rng(5)
    def pair(d1, d2):
        f1 = margins(tC, (QA, QB), designs[d1])[V].min(1) < 0
        f2 = margins(tC, (QA, QB), designs[d2])[V].min(1) < 0
        diff = []
        for _ in range(400):
            ii = rng.choice(len(V), len(V), p=wV)
            diff.append(np.mean(f1[ii]) - np.mean(f2[ii]))
        return [float(np.sum(wV * f1) - np.sum(wV * f2)), float(np.std(diff))]
    out['B'] = dict(designs=res, closed_info=info,
                    diff_closed_cal_minus_chem=pair('closed_cal', 'closed_chem'),
                    diff_greedy_cal_minus_chem=pair('greedy_cal', 'greedy_chem'),
                    diff_swap_cal_minus_chem=pair('swap_cal', 'swap_chem'),
                    diff_swap_proxy_minus_chem=pair('swap_proxy', 'swap_chem'),
                    diff_greedy_proxy_minus_chem=pair('greedy_proxy', 'greedy_chem'),
                    diff_fk_prag_minus_chem=pair('fk_prag_mar', 'swap_chem'))
    # recharge needed: smallest rate per site of the chemistry design with P_chem <= RISK_MAX on V (and on the proxy)
    def need(dsg, tau, target=RISK_MAX):
        M0 = margins(tau, (QA, QB))[V]; Rsum = RESP[V][:, dsg, :].sum(1)
        f = lambda q: float(np.sum(wV * ((M0 + q * Rsum).min(1) < 0)))
        if f(0.0) <= target:
            return 0.0
        lo, hi = 0.0, 2e5
        for _ in range(60):
            mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if f(mid) > target else (lo, mid)
        return hi
    out['B']['q_needed_chem'] = need(designs['swap_chem'], tC)
    out['B']['q_needed_proxy'] = need(designs['swap_chem'], tH)
    out['B']['q_needed_cal'] = need(designs['swap_chem'], tK)
    for dn, row in res.items():
        print(f"  {dn:14s} chem {row['P_chem']:.3f}  proxy {row['P_proxy']:.3f}  cal {row['P_cal']:.3f}  ",
              ' '.join(f"({s['x']:.2f},{s['y']:.2f})" for s in row['sites']))
    print('B diffs', {k: v for k, v in out['B'].items() if k.startswith('diff') or k.startswith('q_')}, f'{time.time() - t0:.0f}s')

    # ------------------------------------------------ C: monitoring
    dM, BM = geom(cM)
    phM = phi0[:, iM] - QA * uA[:, iM] - QB * uB[:, iM]
    hM, _ = state(phM, dM, BM)
    OBS = {'head': (hM, SIG_H)}
    for dep in ('sh', 'mid', 'dp'):
        OBS[f'Cl_{dep}'] = (np.log10(chloride(phM, dM, BM, dep)), SIG_LCL)
    cand = [(k, j) for k in OBS for j in range(NMON)]
    zgoal = fC.any(1).astype(float)
    rng = np.random.default_rng(7)
    tru = V[rng.choice(len(V), NY, p=wV)]
    noise = {k: rng.standard_normal((NY, NMON)) for k in OBS}
    zD = zgoal[D]; pbar = float(np.sum(wD * zD))
    logw = np.log(np.maximum(wD, 1e-300))[None, :]

    def ll_of(k, j):
        g, s = OBS[k]
        y = g[tru, j] + s * noise[k][:, j]
        return -0.5 * ((y[:, None] - g[D, j][None, :]) / s) ** 2

    def eig_from(LL):
        A_ = LL + logw
        A_ = A_ - A_.max(1, keepdims=True)
        E_ = np.exp(A_)
        p = (E_ @ zD) / E_.sum(1)
        essi = E_.sum(1) ** 2 / (E_ ** 2).sum(1)
        return float(hb(pbar) - np.mean(hb(p))), float(np.median(essi))

    cache = {}
    def greedy_mon(allowed, nsel=3):
        LL = np.zeros((NY, len(D))); sel = []; path = []
        for _ in range(nsel):
            best = (-1, None, None)
            for c in allowed:
                if c in sel:
                    continue
                if c not in cache:
                    cache[c] = ll_of(*c)
                e, es = eig_from(LL + cache[c])
                if e > best[0]:
                    best = (e, c, es)
            sel.append(best[1]); LL = LL + cache[best[1]]
            path.append(dict(obs=best[1][0], well=mon_ids[best[1][1]], eig=best[0], inner_ess=best[2]))
        return path

    heads = [c for c in cand if c[0] == 'head']
    out['C'] = dict(p_goal=pbar, H_prior=float(hb(pbar)),
                    greedy_heads=greedy_mon(heads), greedy_all=greedy_mon(cand),
                    greedy_cl_sh=greedy_mon([c for c in cand if c[0] == 'Cl_sh']))
    # the PRAG-GO head design of the geolocated runs (A3, A10, A23) for the chemistry goal
    LL = sum(cache.setdefault(('head', mon_ids.index(n)), ll_of('head', mon_ids.index(n))) for n in ('A3', 'A10', 'A23'))
    out['C']['prag_go_heads_A3_A10_A23'] = eig_from(LL)[0]
    # decision value: the largest pumping scale s (in units of the calibrated rates) whose posterior risk of the
    # chemistry event is <= RISK_MAX, on a grid; mean yield and realised failure frequency over the truths
    SG = np.linspace(0.0, 3.0, 61)
    t20 = tau_chem(YIELD_SCREEN)
    FS = np.stack([(phi_sup(sv * QA, sv * QB)[D] < t20[D]).any(1) for sv in SG], 1).astype(float)   # (ND, ns)
    FT = np.stack([(phi_sup(sv * QA, sv * QB)[tru] < t20[tru]).any(1) for sv in SG], 1)              # (NY, ns)
    def safe_yield(obs):
        LLd = sum((cache.setdefault(c, ll_of(*c)) for c in obs), np.zeros((NY, len(D))))
        A_ = LLd + logw; A_ = A_ - A_.max(1, keepdims=True); E_ = np.exp(A_); E_ /= E_.sum(1, keepdims=True)
        Pp = E_ @ FS                                                  # (NY, ns): posterior risk at each scale
        okm = Pp <= RISK_MAX
        jmax = np.where(okm.any(1), (np.cumprod(okm, 1)).sum(1) - 1, -1)   # largest admissible index (monotone)
        sv = np.where(jmax >= 0, SG[np.maximum(jmax, 0)], 0.0)
        fail = np.where(jmax >= 0, FT[np.arange(NY), np.maximum(jmax, 0)], FT[:, 0])
        return dict(mean_scale=float(sv.mean()), yield_m3_d=float(sv.mean() * (QA + QB)), fail_rate=float(fail.mean()),
                    share_pumping=float(np.mean(sv > 0)))
    out['C']['safe_yield'] = {
        'none': safe_yield([]),
        'prag_go_heads': safe_yield([('head', mon_ids.index(n)) for n in ('A3', 'A10', 'A23')]),
        'best_3_heads': safe_yield([(p['obs'], mon_ids.index(p['well'])) for p in out['C']['greedy_heads']]),
        'best_1_cl': safe_yield([(p['obs'], mon_ids.index(p['well'])) for p in out['C']['greedy_cl_sh'][:1]]),
        'best_3_cl_sh': safe_yield([(p['obs'], mon_ids.index(p['well'])) for p in out['C']['greedy_cl_sh']]),
        'best_2_all': safe_yield([(p['obs'], mon_ids.index(p['well'])) for p in out['C']['greedy_all'][:2]]),
    }
    # the head proxy rule: pump at the largest scale with prior P(h < 1 m) <= RISK_MAX, without monitoring
    sp = max(sv for sv in SG if float(np.sum(wD * (phi_sup(sv * QA, sv * QB)[D] < tH[D]).any(1))) <= RISK_MAX)
    out['C']['proxy_rule'] = dict(scale=float(sp), yield_m3_d=float(sp * (QA + QB)),
                                  fail_rate_chem=float(np.sum(wV * (phi_sup(sp * QA, sp * QB)[V] < t20[V]).any(1))))
    out['C']['yield_screen_m'] = YIELD_SCREEN
    out['C']['fail_zero_pumping'] = float(np.sum(wV * (phi_sup(0.0, 0.0)[V] < t20[V]).any(1)))
    print('C safe yield', json.dumps(out['C']['safe_yield']), json.dumps(out['C']['proxy_rule']))
    for k in ('greedy_heads', 'greedy_cl_sh', 'greedy_all'):
        print('C', k, [(p['obs'], p['well'], round(p['eig'], 3)) for p in out['C'][k]])
    print('C prag-go heads', out['C']['prag_go_heads_A3_A10_A23'], f'{time.time() - t0:.0f}s')

    # ------------------------------------------------ E: screen length and sustainable pumping
    rows = []
    for Ls in (10.0, 20.0, 40.0):
        tCs = tau_chem(Ls)
        def pfail(s, tau):
            return float(np.sum(wV * (phi_sup(s * QA, s * QB)[V] < tau[V]).any(1)))
        lo, hi = 0.0, 20.0
        for _ in range(50):
            mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if pfail(mid, tCs) <= RISK_MAX else (lo, mid)
        rows.append(dict(screen_m=Ls, P_zero=pfail(0.0, tCs), P_at_cal=pfail(1.0, tCs), scale_max=lo, Q_max=[lo * QA, lo * QB]))
    lo, hi = 0.0, 200.0
    for _ in range(60):
        mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if float(np.sum(wV * (phi_sup(mid * QA, mid * QB)[V] < tH[V]).any(1))) <= RISK_MAX else (lo, mid)
    out['E'] = dict(rows=rows, proxy_scale_max=lo, proxy_Q_max=[lo * QA, lo * QB], risk_max=RISK_MAX)
    print('E', json.dumps(out['E']))
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(RES, 'pusi.json'), 'w'), indent=1)
    print('wrote res/pusi.json', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
