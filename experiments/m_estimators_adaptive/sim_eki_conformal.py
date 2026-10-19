"""Proposal N4: Ensemble Kalman Inversion (EKI) as a base predictor, calibrated by split conformal
prediction on held-out piezometers, in a 2-D synthetic confined coastal aquifer.

Forward model. Steady confined flow  div(T grad h) + N = 0  on a 4 km x 2 km rectangle, 40 x 20
cell-centred finite-difference cells (100 m), T = b K with b = 20 m, harmonic face transmissivities.
x = 0 is the sea (Dirichlet h = 0 imposed at the cell face, half-cell distance), x = 4 km is the
inland boundary with a fixed head h_in = 10 m (also at the face), y = 0 and y = 2 km are no-flow,
uniform recharge N = 2e-4 m/d (73 mm/yr). The SPD system is solved with a banded Cholesky
factorisation (bandwidth 20); checked against a sparse solve and exact mass balance.

Truth (new for every replicate). log K = log 15 + Z + 2.3 * 1{channel} (K in m/d), Z a zero-mean
Gaussian random field with exponential covariance exp(-r / 800 m) (sd 1); the paleochannel is a
sinuous strip (half width 150 m) with centre line y_c(x) = y0 + 300 sin(2 pi x / 3000 + phi),
y0 ~ U(600, 1400) m, phi ~ U(0, 2 pi), crossing the whole aquifer from the inland boundary to the sea.

Inversion model (deliberately misspecified). Six zonal log K values (bands x < 1.3 km, 1.3-2.7 km,
> 2.7 km, times a north/south split at y = 1 km), recharge and boundary heads known. Gaussian prior
log K_z ~ N(log 15, 1) independently. Data: heads at 30 fitting piezometers, noise sd 0.03 m. The
fitting network is drawn once (fixed for all replicates) from the coastal design density
q(x) propto exp(-x / 1000 m), redrawn until every zone holds >= 1 piezometer (12/12/2/1/2/1).
EKI: perturbed-observation EKI of Iglesias, Law & Stuart (2013) in its Tikhonov-regularised form
(TEKI, Chada, Stuart & Tong 2020: augmented data [y; m0], Gamma~ = diag(sigma^2 I, I)), with the
Levenberg-Marquardt step rule of Iglesias (2016), rho = 0.5, plus a step-acceptance safeguard (a step is
redrawn with alpha <- 4 alpha if it more than doubles the regularised objective); 100 members, 10 iterations,
no early stopping. Without the safeguard about 1-2% of truths diverged (an overshooting step drives a zone
to very low K, heads explode and 10 iterations do not recover); pilot runs of plain EKI without the
Tikhonov/LM safeguards overflowed in some truths.
For comparison an ES-MDA ensemble (Emerick & Reynolds 2013; 10 steps, alpha_i = 10) is run from the
same initial ensemble.

Prediction targets: heads at new piezometers. Candidate locations = the 770 cells that do not hold a
fitting piezometer; "uniform" test and calibration piezometers are i.i.d. uniform over this set.
Methods at nominal 90%:
  ens   : EKI mean +- 1.645 sqrt(ensemble variance + sigma^2)
  esmda : same with the ES-MDA ensemble (comparison only)
  sc    : split conformal, score |y - mean|, n_cal = 20, threshold = ceil((n+1)(1-alpha))-th score
  scn   : normalised split conformal, score |y - mean| / sd_ens(x)  (ensemble sd)
  scf   : as scn with sd_ens replaced by sqrt(var_ens + sigma^2) (variant, table only)
Clustered calibration: calibration piezometers drawn i.i.d. from the same known design density q
(clustered toward the coast), test locations uniform. Unweighted conformal vs weighted conformal
(Tibshirani, Barber, Candes & Ramdas 2019) with weights w(x) = p_test(x) / q(x), for n_cal in
{20, 40, 80, 160}, absolute and normalised scores.
Coverage is computed EXACTLY over the uniform test distribution: for each candidate cell the
probability that y = h + eps, eps ~ N(0, sigma^2), falls in the interval, averaged over cells. It is
therefore the coverage conditional on the aquifer, the fit data and the calibration set. For each
truth K = 50 independent calibration sets are drawn; their average is the coverage conditional on
the aquifer only (marginal over calibration and test locations and noise).

Run: python3 sim_eki_conformal.py [--R 500]   Output: results/eki_conformal.json
"""
import os

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import argparse  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
from scipy.linalg import solveh_banded, cholesky  # noqa: E402
from scipy.special import ndtr  # noqa: E402

from common import dump  # noqa: E402

# ------------------------------------------------------------------ setting
LX, LY, NX, NY = 4000.0, 2000.0, 40, 20
DX, DY = LX / NX, LY / NY
NC = NX * NY
B_THICK = 20.0
RECH = 2e-4
QIN = 0.4
INLAND = 'head'   # 'head': fixed head H_IN at the inland face; 'flux': lateral inflow QIN
H_IN = 10.0
LOGK0 = np.log(15.0)
SD_GRF, ELL = 1.0, 800.0
CH_DELTA, CH_HW, CH_AMP, CH_LAMBDA = 2.3, 150.0, 300.0, 3000.0
SIG = 0.03
E, NIT = 100, 10
RHO_LM = 0.5
ACC_FAC, ACC_GROW, ACC_MAXTRY = 2.0, 4.0, 12
PRIOR_SD = 1.0
ALPHA = 0.10
Z90 = 1.6448536269514722
N_FIT = 30
N_CAL = 20
K_DRAWS = 50
N_TEST_SHOW = 30
ELL_Q = 1000.0
N_CAL_CLUST = (20, 40, 80, 160)
XBANDS = np.array([0, 1000, 2000, 3000, 4000.0])
ZONE_XB = (1300.0, 2700.0)
SEED = 20261019

IX, JY = np.meshgrid(np.arange(NX), np.arange(NY), indexing='ij')
XC = ((IX + 0.5) * DX).ravel()
YC = ((JY + 0.5) * DY).ravel()
ZONE = (np.digitize(XC, ZONE_XB) * 2 + (YC >= LY / 2)).astype(int)
NZ = 6

EAST = (IX == NX - 1).ravel()
RHS = np.full(NC, RECH * DX * DY)
if INLAND == 'flux':
    RHS[EAST] += QIN * DY


def fit_network(rng):
    """30 fitting piezometers drawn once (fixed across replicates), without replacement, from the
    coastal design density q(x) propto exp(-x / ELL_Q): the existing network is coastal, as in reality.
    The draw is repeated until every zone holds at least one piezometer (otherwise a zone is prior-only)."""
    q = np.exp(-XC / ELL_Q); q /= q.sum()
    while True:
        f = np.sort(rng.choice(NC, N_FIT, replace=False, p=q))
        if np.bincount(ZONE[f], minlength=NZ).min() >= 1:
            return f


def assemble(T):
    """Upper banded form (solveh_banded) of the SPD finite-difference matrix for each row of T (M, NC)."""
    M = T.shape[0]
    T3 = T.reshape(M, NX, NY)
    cx = 2 * T3[:, 1:, :] * T3[:, :-1, :] / (T3[:, 1:, :] + T3[:, :-1, :]) * (DY / DX)
    cy = 2 * T3[:, :, 1:] * T3[:, :, :-1] / (T3[:, :, 1:] + T3[:, :, :-1]) * (DX / DY)
    diag = np.zeros((M, NX, NY))
    diag[:, 1:, :] += cx; diag[:, :-1, :] += cx
    diag[:, :, 1:] += cy; diag[:, :, :-1] += cy
    diag[:, 0, :] += 2 * T3[:, 0, :] * DY / DX
    if INLAND == 'head':
        diag[:, -1, :] += 2 * T3[:, -1, :] * DY / DX
    ab = np.zeros((M, NY + 1, NC))
    ab[:, NY, :] = diag.reshape(M, NC)
    u1 = np.zeros((M, NX, NY)); u1[:, :, 1:] = -cy
    ab[:, NY - 1, :] = u1.reshape(M, NC)
    uN = np.zeros((M, NX, NY)); uN[:, 1:, :] = -cx
    ab[:, 0, :] = uN.reshape(M, NC)
    return ab


def solve_heads(logK):
    """logK (M, NC) -> heads (M, NC)."""
    logK = np.atleast_2d(logK)
    T = B_THICK * np.exp(logK)
    ab = assemble(T)
    rhs = np.repeat(RHS[None], T.shape[0], 0)
    if INLAND == 'head':
        rhs[:, EAST] += 2 * T[:, EAST] * DY / DX * H_IN
    return np.stack([solveh_banded(ab[m], rhs[m], check_finite=False) for m in range(ab.shape[0])])


def zonal_heads(U):
    return solve_heads(U[:, ZONE])


def channel_mask(y0, phi):
    yc = y0 + CH_AMP * np.sin(2 * np.pi * XC / CH_LAMBDA + phi)
    return np.abs(YC - yc) < CH_HW


def lm_alpha(Cgg, r, gsd, rho):
    """Levenberg-Marquardt step rule of Iglesias (2016): smallest alpha >= 1 with
    alpha || Gam^{1/2} (Cgg + alpha Gam)^{-1} r || >= rho || Gam^{-1/2} r ||,  Gam = diag(gsd^2)."""
    Gam = np.diag(gsd ** 2)
    lhs = rho * np.linalg.norm(r / gsd)

    def f(a):
        return a * np.linalg.norm(gsd * np.linalg.solve(Cgg + a * Gam, r))
    a = 1.0
    if f(a) >= lhs:
        return a
    while f(a) < lhs:
        a *= 2.0
    lo, hi = a / 2, a
    for _ in range(25):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if f(mid) < lhs else (lo, mid)
    return hi


def ensemble_kalman(U0, y, fit, rng, mda):
    """mda False: Tikhonov-regularised EKI (TEKI, Chada, Stuart & Tong 2020) = the perturbed-observation EKI
    of Iglesias, Law & Stuart (2013) applied to the augmented data z = [y; m0], G~(u) = [G(u); u],
    Gamma~ = diag(sigma^2 I, prior_sd^2 I), with the Levenberg-Marquardt step rule of Iglesias (2016), rho = RHO_LM,
    and a step-acceptance safeguard: a proposed ensemble is accepted only if the regularised objective
    J = ||Gamma~^{-1/2}(z - mean G~)||^2 is at most ACC_FAC times its current value; otherwise alpha <- ACC_GROW alpha
    and the step is redrawn (at most ACC_MAXTRY attempts; the last attempt is always accepted).
    mda True: ES-MDA (Emerick & Reynolds 2013) with alpha_i = NIT on the plain data (no safeguard).
    Returns final ensemble heads at all cells, final ensemble and diagnostics per iteration."""
    U = U0.copy(); m = len(fit); p = U.shape[1]
    if mda:
        z, gsd = y, np.full(m, SIG)
    else:
        z = np.concatenate([y, np.full(p, LOGK0)])
        gsd = np.concatenate([np.full(m, SIG), np.full(p, PRIOR_SD)])

    def aug(U, H):
        return H[:, fit] if mda else np.hstack([H[:, fit], U])

    def obj(Gt):
        return np.sum(((z - Gt.mean(0)) / gsd) ** 2)

    H = zonal_heads(U); Gt = aug(U, H)
    misfit, dspread, pspread, alphas = [], [], [], []
    n_rej = 0
    for it in range(NIT + 1):
        G = H[:, fit]; Gm = G.mean(0)
        misfit.append(np.sum((y - Gm) ** 2) / (m * SIG ** 2))
        dspread.append(np.mean(np.sum((G - Gm) ** 2, 1)) / (m * SIG ** 2))
        pspread.append(np.sqrt(np.mean(U.var(0, ddof=1))))
        if it == NIT:
            break
        dU = U - U.mean(0); dG = Gt - Gt.mean(0)
        Cug = dU.T @ dG / (E - 1); Cgg = dG.T @ dG / (E - 1)
        a = float(NIT) if mda else lm_alpha(Cgg, z - Gt.mean(0), gsd, RHO_LM)
        J0 = obj(Gt)
        for t in range(1 if mda else ACC_MAXTRY):
            Zp = z + np.sqrt(a) * gsd * rng.standard_normal((E, len(z)))
            Kt = np.linalg.solve(Cgg + a * np.diag(gsd ** 2), Cug.T)
            Un = U + (Zp - Gt) @ Kt
            Hn = zonal_heads(Un); Gn = aug(Un, Hn)
            if mda or obj(Gn) <= ACC_FAC * J0 or t == ACC_MAXTRY - 1:
                break
            a *= ACC_GROW; n_rej += 1
        alphas.append(a)
        U, H, Gt = Un, Hn, Gn
    return H, U, np.array(misfit), np.array(dspread), np.array(pspread), np.array(alphas), n_rej


def cover_prob(r, w):
    """P(|r + eps| <= w), eps ~ N(0, SIG^2); r = h - mean, w half-width (may be inf). Broadcasts."""
    with np.errstate(invalid='ignore'):
        p = ndtr((w - r) / SIG) - ndtr((-w - r) / SIG)
    return np.where(np.isinf(w), 1.0, p)


def conf_q(scores, n):
    k = int(np.ceil((n + 1) * (1 - ALPHA)))
    return np.inf if k > n else np.sort(scores)[k - 1]


def weighted_q(scores, wcal, wtest):
    """Weighted conformal quantile (Tibshirani et al. 2019) for every test weight in wtest."""
    o = np.argsort(scores); s = scores[o]; cw = np.cumsum(wcal[o]); W = cw[-1]
    thr = (1 - ALPHA) * (W + wtest)
    k = np.searchsorted(cw, thr * (1 - 1e-12), side='left')
    q = np.full(wtest.shape, np.inf)
    ok = k < len(s)
    q[ok] = s[k[ok]]
    return q


def one_truth(rep, Lc, fit, cand, qdens, rng, keep=False):
    out = {}
    # --- truth
    y0 = rng.uniform(600, 1400); phi = rng.uniform(0, 2 * np.pi)
    ch = channel_mask(y0, phi)
    logK = LOGK0 + SD_GRF * (Lc @ rng.standard_normal(NC)) + CH_DELTA * ch
    h = solve_heads(logK)[0]
    yfit = h[fit] + SIG * rng.standard_normal(len(fit))
    # --- ensemble inversion
    U0 = LOGK0 + PRIOR_SD * rng.standard_normal((E, NZ))
    He, Ue, mis, dsp, psp, alp, nrej = ensemble_kalman(U0, yfit, fit, rng, mda=False)
    Hm, Um, mis_m, dsp_m, psp_m, _, _ = ensemble_kalman(U0, yfit, fit, rng, mda=True)
    out.update(misfit=mis, dspread=dsp, pspread=psp, alpha_lm=alp, n_reject=nrej, misfit_mda=mis_m,
               dspread_mda=dsp_m, pspread_mda=psp_m)
    mu = He.mean(0); sd_e = np.sqrt(He.var(0, ddof=1)); s = np.sqrt(sd_e ** 2 + SIG ** 2)
    mu_m = Hm.mean(0); s_m = np.sqrt(Hm.var(0, ddof=1) + SIG ** 2)
    r = h - mu
    rc = r[cand]
    out['rmse'] = np.sqrt(np.mean(rc ** 2))
    out['rmse_mda'] = np.sqrt(np.mean((h - mu_m)[cand] ** 2))
    out['ens_sd'] = np.mean(sd_e[cand])
    out['ens_sd_mda'] = np.mean(np.sqrt(Hm.var(0, ddof=1))[cand])
    out['ens_sd_prior'] = np.mean(zonal_heads(U0).std(0, ddof=1)[cand])
    out['corr_logabsr_logsd'] = np.corrcoef(np.log(np.abs(rc) + 1e-3), np.log(sd_e[cand]))[0, 1]
    # --- ensemble intervals (no calibration)
    band = np.digitize(XC[cand], XBANDS[1:-1])
    nb = np.bincount(band, minlength=len(XBANDS) - 1)
    pe = cover_prob(rc, Z90 * s[cand])
    out['band_ens'] = np.bincount(band, pe, minlength=len(XBANDS) - 1) / nb
    out['cov_ens'] = pe.mean()
    out['wid_ens'] = 2 * Z90 * s[cand].mean()
    out['cov_esmda'] = cover_prob((h - mu_m)[cand], Z90 * s_m[cand]).mean()
    out['wid_esmda'] = 2 * Z90 * s_m[cand].mean()
    # --- uniform calibration, K draws. Scores |y - mu| / scale(x)
    scale = dict(sc=np.ones(NC), scn=sd_e, scf=s)   # absolute, normalised by ensemble sd, by sqrt(var + sigma^2)
    nC = len(cand)
    cov = {k: np.zeros(K_DRAWS) for k in scale}; wid = {k: np.zeros(K_DRAWS) for k in scale}
    bnd = {k: np.zeros(len(XBANDS) - 1) for k in scale}
    qs0 = {}
    for d in range(K_DRAWS):
        ci = cand[rng.integers(0, nC, N_CAL)]
        ycal = h[ci] + SIG * rng.standard_normal(N_CAL)
        ab = np.abs(ycal - mu[ci])
        for k, sk in scale.items():
            q = conf_q(ab / sk[ci], N_CAL)
            pk = cover_prob(rc, q * sk[cand])
            cov[k][d] = pk.mean(); wid[k][d] = 2 * q * sk[cand].mean()
            bnd[k] += np.bincount(band, pk, minlength=len(XBANDS) - 1) / nb / K_DRAWS
            if d == 0:
                qs0[k] = q
        if d == 0:
            cal0, ycal0 = ci, ycal
    for k in cov:
        out[f'cov_{k}_1'] = cov[k][0]; out[f'cov_{k}_avg'] = cov[k].mean()
        out[f'wid_{k}_1'] = wid[k][0]; out[f'wid_{k}_avg'] = wid[k].mean()
        out[f'band_{k}'] = bnd[k]
    # empirical coverage at 30 random test piezometers (calibration draw 0)
    ti = cand[rng.integers(0, nC, N_TEST_SHOW)]
    yt = h[ti] + SIG * rng.standard_normal(N_TEST_SHOW)
    e = np.abs(yt - mu[ti])
    out['emp30_ens'] = np.mean(e <= Z90 * s[ti])
    for k, sk in scale.items():
        out[f'emp30_{k}'] = np.mean(e <= qs0[k] * sk[ti])
    # --- clustered calibration (known design density q), uniform test
    pq = qdens / qdens.sum()
    wt = 1.0 / pq                                    # p_test / q up to a constant (p_test uniform on cand)
    for n in N_CAL_CLUST:
        acc = {k: [] for k in ('u', 'w', 'un', 'wn')}; accw = {k: [] for k in acc}; accinf = {k: [] for k in acc}
        accb = {k: np.zeros(len(XBANDS) - 1) for k in acc}; ess = []
        for d in range(K_DRAWS):
            idx = rng.choice(nC, n, p=pq)
            ci = cand[idx]
            ycal = h[ci] + SIG * rng.standard_normal(n)
            ab = np.abs(ycal - mu[ci]); abn = ab / sd_e[ci]
            w_i = wt[idx]; ess.append(w_i.sum() ** 2 / np.sum(w_i ** 2))
            qu = np.full(nC, conf_q(ab, n)); qun = np.full(nC, conf_q(abn, n))
            qw = weighted_q(ab, w_i, wt); qwn = weighted_q(abn, w_i, wt)
            for k, w in (('u', qu), ('w', qw), ('un', qun * sd_e[cand]), ('wn', qwn * sd_e[cand])):
                p = cover_prob(rc, w)
                acc[k].append(p.mean())
                accw[k].append(2 * np.median(w))
                accinf[k].append(1 - np.isfinite(w).mean())
                accb[k] += np.bincount(band, p, minlength=len(XBANDS) - 1) / nb
            if d == 0 and n == N_CAL_CLUST[0]:
                calq0 = ci
        out[f'cl{n}_ess'] = np.mean(ess)
        for k in acc:
            out[f'cl{n}_cov_{k}_1'] = acc[k][0]; out[f'cl{n}_cov_{k}_avg'] = np.mean(acc[k])
            out[f'cl{n}_medwid_{k}_avg'] = np.median(accw[k])
            out[f'cl{n}_inf_{k}_avg'] = np.mean(accinf[k])
            out[f'cl{n}_band_{k}'] = accb[k] / K_DRAWS
    if keep:
        ex = dict(logK=logK, channel=ch, y0=y0, phi=phi, h=h, mu=mu, sd_e=sd_e, s=s, mu_mda=mu_m, s_mda=s_m,
                  fit=fit, yfit=yfit, cal=cal0, ycal=ycal0, q0=qs0, test=ti, ytest=yt, cal_clust=calq0,
                  U_eki=Ue, U_mda=Um, U0=U0)
        return out, ex
    return out, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--R', type=int, default=500)
    args = ap.parse_args()
    R = args.R
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    fit = fit_network(np.random.default_rng(11))
    assert len(np.unique(fit)) == len(fit)
    cand = np.setdiff1d(np.arange(NC), fit)
    qdens = np.exp(-XC[cand] / ELL_Q)
    P = np.stack([XC, YC], 1)
    Dm = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(-1))
    Lc = cholesky(np.exp(-Dm / ELL) + 1e-10 * np.eye(NC), lower=True)
    recs = []; example = None
    for rep in range(R):
        o, ex = one_truth(rep, Lc, fit, cand, qdens, rng, keep=(rep == 0))
        recs.append(o)
        if ex is not None:
            example = ex
        if rep % 25 == 0:
            print(f'rep {rep}  {time.time() - t0:.1f}s  cov ens {o["cov_ens"]:.3f} sc {o["cov_sc_avg"]:.3f} '
                  f'scn {o["cov_scn_avg"]:.3f}  rmse {o["rmse"]:.3f}', flush=True)
    keys = recs[0].keys()
    per = {k: np.array([r[k] for r in recs]) for k in keys}
    # summaries
    summ = {}
    for k, v in per.items():
        if v.ndim == 1:
            fin = np.isfinite(v); vf = v[fin]
            summ[k] = dict(mean=vf.mean(), se=vf.std(ddof=1) / np.sqrt(fin.sum()), median=np.median(v),
                           q10=np.quantile(v, 0.1), q90=np.quantile(v, 0.9), min=v.min(), max=v.max(),
                           frac_nonfinite=1 - fin.mean())
    runtime = time.time() - t0
    res = dict(
        setting=dict(LX=LX, LY=LY, NX=NX, NY=NY, b=B_THICK, recharge=RECH, inland_bc=INLAND, h_in=H_IN, q_in=QIN, logK0=LOGK0, sd_grf=SD_GRF,
                     ell=ELL, ch_delta=CH_DELTA, ch_halfwidth=CH_HW, ch_amp=CH_AMP, ch_lambda=CH_LAMBDA, sigma=SIG,
                     E=E, n_iter=NIT, rho_lm=RHO_LM, acc_fac=ACC_FAC, acc_grow=ACC_GROW, acc_maxtry=ACC_MAXTRY, prior_sd=PRIOR_SD, alpha=ALPHA, n_cal=N_CAL, K_draws=K_DRAWS,
                     n_test_show=N_TEST_SHOW, ell_q=ELL_Q, n_cal_clust=N_CAL_CLUST, xbands=XBANDS,
                     zone_xbreaks=ZONE_XB, n_fit=len(fit), n_cand=len(cand), seed=SEED, R=R),
        grid=dict(xc=XC, yc=YC, zone=ZONE),
        per_truth=per, summary=summ, example=example, runtime_s=runtime)
    dump(res, 'eki_conformal.json')
    print(f'done R={R} in {runtime:.1f}s')
    for k in ('cov_ens', 'cov_esmda', 'cov_sc_1', 'cov_sc_avg', 'cov_scn_1', 'cov_scn_avg', 'cov_scf_avg', 'wid_ens',
              'wid_sc_avg', 'wid_scn_avg', 'wid_scf_avg', 'rmse', 'ens_sd', 'corr_logabsr_logsd'):
        print(k, {a: round(float(b), 4) for a, b in summ[k].items()})
    print('rmse_mda', {a: round(float(b), 4) for a, b in summ['rmse_mda'].items()})
    print('n_reject', {a: round(float(b), 3) for a, b in summ['n_reject'].items()},
          'truths with >=1 rejected step:', int((per['n_reject'] > 0).sum()))
    print('ess', [round(summ[f'cl{n}_ess']['mean'], 2) for n in N_CAL_CLUST])
    for n in N_CAL_CLUST:
        print(n, {k: (round(summ[f'cl{n}_cov_{k}_avg']['mean'], 4), round(summ[f'cl{n}_inf_{k}_avg']['mean'], 3))
                  for k in ('u', 'w', 'un', 'wn')})


if __name__ == '__main__':
    main()
