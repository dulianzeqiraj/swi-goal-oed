"""RREZJA-GO (rrezja: the radius): a radius of belief instead of a list of stakeholders. Innovation of literature
review 58 (decisive stakeholder decisions under deep uncertainty II; Oxford, Caltech, MIT, ETH Zurich, 2020-2026).

VENDIMI-GO (review 57) protects five STATED beliefs, exponential tilts of the calibrated chloride ensemble along the
mixing-zone width and the recharge. RREZJA-GO protects every belief within a relative-entropy radius rho of the
calibrated ensemble, before the data, updated by Bayes' rule with the common likelihood:

    tilt ball   B(rho) = { p_lam ∝ p exp(lam . z) : KL(p_lam || p) <= rho },  z = standardised log parameters
    group rule  a is admissible after data y  iff  max_{lam in B(rho)} P_lam(F | y, a) + 1.645 se <= alpha = 0.10

with z either the two disputed drivers (width, recharge) or all eight parameters of the ensemble (w, R, b_c, b_e,
L_B, ground, eta, Cl_s). The full relative-entropy ball (any belief, not only tilts) has the closed form
max P = klinv(P, rho) (binary relative entropy), i.e. the nominal rule with a tighter limit alpha_rho.

Propositions checked here (section 9 of the review):
  R1  full ball: sup_{KL(q||p)<=rho} q(F) = klinv_+(p(F), rho)   (exact; data-processing inequality)
  R2  tilt ball: sup P_lam(F) = P(F) + sqrt(2 rho c' S^-1 c) + O(rho), c = Cov(z, 1_F), S = Cov(z): the price of
      robustness is the radius times the part of the failure indicator explained by the drivers
  R3  tilts commute with Bayes' rule; a stated belief's radius after data is about 1/2 lam' Cov(z|y) lam
Output res/rrezja.json.   Run: python3 rrezja.py   (about 25 minutes on 4 cores)
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vendimi_go'))
import vendimi as VG  # noqa: E402  (imports ../pusi_go/pusi_analysis, which loads the ensemble)

PA = VG.PA
RES = os.path.join(HERE, 'res')
ALPHA, ZM, SG, QG, C_R, QSUM, K = VG.ALPHA, VG.ZM, VG.SG, VG.QG, VG.C_R, VG.QSUM, VG.K
NY = int(os.environ.get('RZ_NY', VG.NY))                                    # 2000 truths, as in VENDIMI-GO
NAMES = ['w', 'R', 'b_c', 'b_e', 'L_B', 'ground', 'eta', 'Cl_s']
Z8 = np.column_stack([VG.zstd(np.log(PA.P[n]), PA.W) for n in NAMES])      # (N, 8); first two columns = VG.ZZ
assert np.allclose(Z8[:, :2], VG.ZZ)
NU = int(os.environ.get('RZ_NU', 400))                                                                   # random unstated beliefs on the sphere
ns, nq = len(SG), len(QG)


def softmax_rows(A):
    A = A - A.max(1, keepdims=True); W = np.exp(A); W /= W.sum(1, keepdims=True); return W


def kl_prior(Lam, Zd, logw):
    """exact KL(p_lam || p) on the inner sample for a batch of tilts Lam (n, d)"""
    t = Lam @ Zd.T
    A = logw[None, :] + t
    mx = A.max(1, keepdims=True)
    E = np.exp(A - mx); Z = E.sum(1, keepdims=True); W = E / Z
    lse = np.log(Z[:, 0]) + mx[:, 0]
    return np.sum(W * t, 1) - lse, W


def project_exact(Lam, rho, Zd, logw, it=6):
    """scale every tilt along its ray so that KL(p_lam || p) = rho exactly (Newton on the scale)"""
    c = np.ones(len(Lam))
    for _ in range(it):
        L = Lam * c[:, None]
        kl, W = kl_prior(L, Zd, logw)
        u = Zd @ Lam.T                                                         # (ND, n)
        mu = np.sum(W * u.T, 1); var = np.maximum(np.sum(W * (u.T) ** 2, 1) - mu ** 2, 1e-12)
        dk = c * var                                                           # d KL(c lam)/dc
        c = np.clip(c - (kl - rho) / dk, 0.05 * c, 5.0 * c)
        c = np.where(np.linalg.norm(Lam, axis=1) < 1e-12, 0.0, c)
    return Lam * c[:, None]


def worst_case(LB, Fm, rho, Zd, S, Sinv, logw, it=6):
    """max over the tilt ball of the posterior failure probability, batched over truths.
    LB (nT, ND) log posterior weights of the calibrated belief, Fm (nT, ND) failure indicators."""
    nT, d = LB.shape[0], Zd.shape[1]
    lam = np.zeros((nT, d))
    first = None
    if rho > 0:
        for k in range(it):
            W = softmax_rows(LB + lam @ Zd.T)
            P = np.sum(W * Fm, 1)
            G = (W * (Fm - P[:, None])) @ Zd                                   # Cov(z, 1_F) under the current tilt
            dirn = G @ Sinv
            nrm = np.sqrt(np.maximum(np.einsum('ij,ij->i', dirn @ S, dirn), 1e-300))
            lin = np.sqrt(2 * rho) * dirn / nrm[:, None]
            if k == 0:
                first = P + np.sqrt(2 * rho) * np.sqrt(np.maximum(np.einsum('ij,ij->i', G @ Sinv, G), 0))
            lam = lin if k == 0 else 0.5 * lam + 0.5 * lin
            q = 0.5 * np.einsum('ij,ij->i', lam @ S, lam)
            lam *= np.where(q > rho, np.sqrt(rho / np.maximum(q, 1e-300)), 1.0)[:, None]
        lam = project_exact(lam, rho, Zd, logw)
    W = softmax_rows(LB + lam @ Zd.T)
    P = np.sum(W * Fm, 1)
    se = np.sqrt(np.maximum(np.sum(W ** 2 * (Fm - P[:, None]) ** 2, 1), 0))
    if first is None:
        first = P.copy()
    return P, se, lam, first


def kl_bin(a, p):
    p = np.clip(p, 1e-300, 1 - 1e-16)
    return a * np.log(a / p) + (1 - a) * np.log((1 - a) / (1 - p))


def alpha_rho(rho):
    """the nominal limit equivalent to the full ball: kl(alpha || alpha_rho) = rho, alpha_rho < alpha"""
    if rho <= 0:
        return ALPHA
    lo, hi = 0.0, ALPHA
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if kl_bin(ALPHA, mid) > rho: lo = mid
        else: hi = mid
    return hi


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    D, V, wD, wV = PA.D, PA.V, PA.wD, PA.wV
    rng = np.random.default_rng(57)                                            # same truths and noise as VENDIMI-GO
    tru = V[rng.choice(len(V), NY, p=wV)]
    FD = np.stack([np.stack([VG.fail(D, s, q) for s in SG], 1) for q in QG], 2)   # (ND, ns, nq) bool
    FT = np.stack([np.stack([VG.fail(tru, s, q) for s in SG], 1) for q in QG], 2)
    noise = rng.standard_normal((NY, 4))
    dM, BM = PA.geom(PA.cM)
    phM = PA.phi0[:, PA.iM] - VG.QA * PA.uA[:, PA.iM] - VG.QB * PA.uB[:, PA.iM]
    clM = np.log10(PA.chloride(phM, dM, BM, 'sh'))
    mon = [str(x) for x in PA.Z['mon_ids']]
    j = mon.index('A30')
    ycl = clM[tru, j] + 0.1 * noise[:, 0]
    L_cl = -0.5 * ((ycl[:, None] - clM[D, j][None, :]) / 0.1) ** 2
    logw = np.log(np.maximum(wD, 1e-300))
    ar = np.arange(NY)
    Zsets = {'z2': Z8[:, :2], 'z8': Z8}
    mom = {}
    for zn, Zall in Zsets.items():
        Zd = Zall[D]; mu = wD @ Zd; S = (Zd - mu).T @ ((Zd - mu) * wD[:, None])
        mom[zn] = (Zd, S, np.linalg.inv(S))
    out = dict(alpha=ALPHA, zm=ZM, c_r=C_R, names=NAMES, nu=NU)

    # ---------------------------------------------------------------- radii of the stated beliefs (prior, exact)
    Zd8, S8, S8i = mom['z8']
    LAM8 = np.zeros((K, 8)); LAM8[:, :2] = VG.LAM
    kl5, _ = kl_prior(LAM8, Zd8, logw)
    out['stakeholders'] = [dict(name=n, lam=[a, b], kl=float(kl5[k]), kl_quad=float(0.5 * LAM8[k] @ S8 @ LAM8[k]))
                           for k, (n, a, b) in enumerate(VG.STAKE)]
    RHO_ENV, RHO_MAX = float(kl5[4]), float(kl5.max())
    out['rho_env'], out['rho_max'] = RHO_ENV, RHO_MAX
    print('prior radii', np.round(kl5, 4), f'{time.time() - t0:.0f}s')
    # multiple correlation of failure with the drivers at the VENDIMI-GO no-data choice (s = 0.8, q = 5000)
    i08, iq5 = int(np.argmin(np.abs(SG - 0.8))), 2
    F0 = FD[:, i08, iq5].astype(float); P0 = wD @ F0
    for zn in Zsets:
        Zd, S, Si = mom[zn]; c = (Zd - wD @ Zd).T @ (wD * (F0 - P0))
        out[f'R2_{zn}'] = float(c @ Si @ c / (P0 * (1 - P0)))
    out['P_calibrated_at_vendimi_choice'] = float(P0)

    # ---------------------------------------------------------------- posterior radii after the chloride sample (R3)
    E0 = softmax_rows(L_cl + logw[None, :])                                    # (NY, ND) calibrated posterior
    post_kl = np.zeros((NY, K)); gen_eig = np.zeros(NY)
    for k in range(1, K):
        A = E0 * np.exp(Zd8 @ LAM8[k] - (Zd8 @ LAM8[k]).max())[None, :]
        Wk = A / A.sum(1, keepdims=True)
        post_kl[:, k] = np.sum(Wk * np.log(np.maximum(Wk, 1e-300) / np.maximum(E0, 1e-300)), 1)
    mu = E0 @ Zd8
    for t in range(NY):
        Sy = (Zd8 - mu[t]).T @ ((Zd8 - mu[t]) * E0[t][:, None])
        gen_eig[t] = np.max(np.real(np.linalg.eigvals(S8i @ Sy)))
    out['posterior_radii'] = dict(median=np.median(post_kl, 0).tolist(), q10=np.quantile(post_kl, 0.1, 0).tolist(),
                                  q90=np.quantile(post_kl, 0.9, 0).tolist(), gen_eig_median=float(np.median(gen_eig)),
                                  gen_eig_q90=float(np.quantile(gen_eig, 0.9)))
    print('posterior radii (median)', np.round(np.median(post_kl, 0), 4), 'gen eig', round(float(np.median(gen_eig)), 3), f'{time.time() - t0:.0f}s')

    # ---------------------------------------------------------------- unstated beliefs on the sphere of radius rho
    def sphere(rho, zn, nu, seed):
        Zd, S, Si = mom[zn]; d = Zd.shape[1]
        g = np.random.default_rng(seed).standard_normal((nu, d))
        Lr = np.linalg.cholesky(Si)                                             # S^-1/2 directions
        dirs = g @ Lr.T
        extra = np.vstack([np.eye(d), -np.eye(d)])                             # axis directions in parameter space
        dirs = np.vstack([dirs, extra])
        lam = project_exact(dirs, rho, Zd, logw)
        return lam
    Ztr = Z8[tru]

    def views_of(lams):
        A = lams @ Ztr[:, :lams.shape[1]].T
        return softmax_rows(A)                                                  # (n, NY) weights over the truths

    VIEW5 = views_of(VG.LAM)

    # ---------------------------------------------------------------- rules
    def joint_from_caps(cap):
        """cap (nT, nq) largest admissible scale index or -1; returns the joint decisive choice per truth"""
        nT = cap.shape[0]
        sU = np.where(cap >= 0, SG[np.maximum(cap, 0)], 0.0)
        net = np.where(cap >= 0, sU * QSUM - C_R * 3 * QG[None, :], -np.inf)
        feas = np.isfinite(net).any(1)
        iq = np.where(feas, np.argmax(net, 1), nq - 1)
        s = np.where(feas, sU[np.arange(nT), iq], 0.0)
        idx = np.where(feas, np.maximum(cap[np.arange(nT), iq], 0), 0)
        return s, iq, idx, feas

    def evaluate(s, iq, idx, feas, unstated):
        nT = len(s)
        if nT == 1:
            s, iq, idx, feas = [np.repeat(x, NY) for x in (s, iq, idx, feas)]
        f = FT[ar, idx, iq].astype(float)
        netv = s * QSUM - C_R * 3 * QG[iq]
        r5 = VIEW5 @ f; se5 = np.sqrt(np.sum(VIEW5 ** 2 * (f[None, :] - r5[:, None]) ** 2, 1))
        res = dict(water=float((s * QSUM).mean()), recharge=float((3 * QG[iq]).mean()), net=float(netv.mean()),
                   deadlock=float(1 - feas.mean()), q_share={str(int(q)): float(np.mean(iq == i)) for i, q in enumerate(QG)},
                   fail_by_view=r5.tolist(), fail_se_by_view=se5.tolist())
        for name, Vw in unstated.items():
            r = Vw @ f; se = np.sqrt(np.sum(Vw ** 2 * (f[None, :] - r[:, None]) ** 2, 1))
            res[f'unstated_{name}'] = dict(max=float(r.max()), se_at_max=float(se[np.argmax(r)]), share_above=float(np.mean(r > ALPHA)),
                                          share_above_2se=float(np.mean(r > ALPHA + 2 * se)), mean=float(r.mean()))
        return res

    def caps_vendimi(LL):
        WK = np.stack([VG.tilt(D, wD, VG.LAM[k]) for k in range(K)])
        FF = FD.reshape(len(D), -1).astype(float)
        UKmax = None
        for k in range(K):
            A_ = LL + np.log(np.maximum(WK[k], 1e-300))[None, :]
            E_ = softmax_rows(A_)
            P_ = E_ @ FF; E2 = E_ ** 2
            v_ = (E2 @ FF) * (1 - 2 * P_) + P_ ** 2 * E2.sum(1, keepdims=True)
            U = (P_ + ZM * np.sqrt(np.maximum(v_, 0))).reshape(-1, ns, nq)
            UKmax = U if UKmax is None else np.maximum(UKmax, U)
        ok = UKmax <= ALPHA + 1e-12
        return np.cumprod(ok, axis=1).sum(1) - 1                                  # (nT, nq)

    def caps_full(LL, rho):
        E_ = softmax_rows(LL + logw[None, :]); FF = FD.reshape(len(D), -1).astype(float)
        P_ = E_ @ FF; E2 = E_ ** 2
        v_ = (E2 @ FF) * (1 - 2 * P_) + P_ ** 2 * E2.sum(1, keepdims=True)
        U = (P_ + ZM * np.sqrt(np.maximum(v_, 0))).reshape(-1, ns, nq)
        ok = U <= alpha_rho(rho) + 1e-15
        return np.cumprod(ok, axis=1).sum(1) - 1

    def caps_ball(LL, rho, zn, collect=None):
        Zd, S, Si = mom[zn]
        LB = LL + logw[None, :]
        nT = LB.shape[0]
        cap = np.empty((nT, nq), int)
        for iq in range(nq):
            lo = np.full(nT, -1); hi = np.full(nT, ns)
            while np.any(hi - lo > 1):
                mid = np.where(hi - lo > 1, (lo + hi) // 2, np.maximum(lo, 0))
                Fm = FD[np.arange(len(D))[None, :], mid[:, None], iq].astype(float)
                P, se, lam, first = worst_case(LB, Fm, rho, Zd, S, Si, logw)
                ok = P + ZM * se <= ALPHA + 1e-12
                act = hi - lo > 1
                lo = np.where(act & ok, mid, lo); hi = np.where(act & ~ok, mid, hi)
            cap[:, iq] = lo
        return cap

    designs = {'none': np.zeros((1, len(D))), 'chloride sample (A30)': L_cl}
    UNST = {}
    for zn in ('z2', 'z8'):
        for rn, rho in (('env', RHO_ENV), ('max', RHO_MAX)):
            UNST[f'{zn}_{rn}'] = views_of(sphere(rho, zn, NU, 58))
    # the pure-width pessimist at the radius of the environmental groups
    e = np.zeros((1, 2)); e[0, 0] = 1.0
    lam_w = project_exact(e, RHO_ENV, mom['z2'][0], logw)
    out['pure_width_pessimist_lambda'] = float(lam_w[0, 0])
    UNST['width_pessimist'] = views_of(lam_w)
    out['unstated_note'] = 'views of the truths tilted by unstated beliefs on the sphere KL = rho (400 random directions plus the axis directions)'

    cache = {}

    def ball(dn, rho, zn):
        key = (dn, zn, round(rho, 6))
        if key not in cache:
            t1 = time.time()
            cache[key] = evaluate(*joint_from_caps(caps_ball(designs[dn], rho, zn)), UNST)
            print(dn, zn, round(rho, 4), 'net', round(cache[key]['net']), 'dead', round(cache[key]['deadlock'], 3),
                  'unstated z8_env max', round(cache[key]['unstated_z8_env']['max'], 3), f'{time.time() - t1:.0f}s step, {time.time() - t0:.0f}s total', flush=True)
        return cache[key]

    res = {}
    for dn, LL in designs.items():
        r = {}
        cap = caps_vendimi(LL); r['vendimi'] = evaluate(*joint_from_caps(cap), UNST)
        for rn, rho in (('env', RHO_ENV), ('max', RHO_MAX)):
            cap = caps_full(LL, rho); r[f'full_{rn}'] = evaluate(*joint_from_caps(cap), UNST)
            for zn in ('z2', 'z8'):
                r[f'ball_{zn}_{rn}'] = ball(dn, rho, zn)
        print(dn, 'vendimi net', round(r['vendimi']['net']), 'unstated z8_env max', round(r['vendimi']['unstated_z8_env']['max'], 3),
              'width pessimist', round(r['vendimi']['unstated_width_pessimist']['max'], 3), f'{time.time() - t0:.0f}s', flush=True)
        res[dn] = r
    out['designs'] = res

    # ---------------------------------------------------------------- frontier: net water against the radius (z8 ball)
    base = [0.0, 0.1, 0.2, round(RHO_ENV, 6), round(RHO_MAX, 6)]
    fr = {}
    for dn, LL in designs.items():
        rg_d = sorted(set(base + ([0.05, 0.15, 0.25, 0.35, 0.5] if dn == 'none' else [])))
        fr[dn] = dict(rho=rg_d, ball_z8=[ball(dn, rho, 'z8')['net'] for rho in rg_d],
                      full=[evaluate(*joint_from_caps(caps_full(LL, rho)), {})['net'] for rho in rg_d])
        print('frontier', dn, np.round(fr[dn]['ball_z8']), np.round(fr[dn]['full']), f'{time.time() - t0:.0f}s', flush=True)
    out['frontier'] = fr
    out['alpha_rho'] = {f'{r:.4f}': alpha_rho(r) for r in sorted(set(base + [0.05, 0.15, 0.25, 0.35, 0.5]))}

    # ---------------------------------------------------------------- R1 and R2 checks at the no-data VENDIMI choice
    Fm0 = F0[None, :]
    chk = {}
    for zn in ('z2', 'z8'):
        Zd, S, Si = mom[zn]
        rows = []
        for rho in (0.05, 0.1, RHO_ENV, RHO_MAX):
            P, se, lam, first = worst_case(logw[None, :], Fm0, rho, Zd, S, Si, logw)
            rows.append(dict(rho=rho, exact=float(P[0]), first_order=float(first[0]), lam=lam[0].tolist()))
        chk[zn] = rows
    # full ball: closed form against a brute-force search over two-point tilts q ∝ p exp(eta 1_F)
    full = []
    for rho in (0.05, 0.1, RHO_ENV, RHO_MAX):
        best = 0.0
        for eta in np.linspace(0, 12, 6001):
            wq = wD * np.exp(eta * F0); wq /= wq.sum()
            kl = np.sum(wq[wD > 0] * np.log(wq[wD > 0] / wD[wD > 0]))
            if kl <= rho: best = max(best, float(wq @ F0))
        lo, hi = P0, 1.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if kl_bin(mid, P0) < rho: lo = mid
            else: hi = mid
        full.append(dict(rho=rho, closed_form=lo, search=best))
    chk['full'] = full
    out['checks_at_vendimi_choice'] = chk
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(RES, 'rrezja.json' if not os.environ.get('RZ_NY') else 'rrezja_quick.json'), 'w'), indent=1)
    print('wrote res/rrezja.json', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
