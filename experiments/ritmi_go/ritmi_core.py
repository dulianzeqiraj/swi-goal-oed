"""Priors, observation operators, goals, Fisher information and ES-MDA for RITMI-GO (review 43)."""
import numpy as np
import ritmi_model as R

logit = lambda p: np.log(p / (1 - p))
expit = lambda x: 1 / (1 + np.exp(-x))
SIG_OBS = 0.05                                               # 5 % (log scale), every datum
PARAMS = [('log_sv', 0.0, 0.3), ('log_aL', np.log(150.0), 0.4), ('logit_f0', logit(0.07), 0.35),
          ('log_a1', np.log(1.0), 0.5), ('log_b1', np.log(0.3), 0.4), ('log_a2', np.log(0.05), 0.5),
          ('log_b2', np.log(0.6), 0.4),
          ('log_E', np.log(60.0), 0.4), ('log_KK', np.log(0.2), 0.25), ('log_KC', np.log(0.4), 0.25),
          ('log_KM', np.log(0.5), 0.25), ('log_ksr', np.log(0.05), 0.6)]
NAMES = [n for n, _, _ in PARAMS]
M0 = np.array([m for _, m, _ in PARAMS]); S0 = np.array([s for _, _, s in PARAMS])
GROUPS = {'transport': [0, 1, 2], 'memory': [3, 4, 5, 6], 'exchange': [7, 8, 9, 10], 'reaction': [11]}
LABELS = ['s_v', 'alpha_L', 'f_0', 'a_1', 'b_1', 'a_2', 'b_2', 'E', 'K_K', 'K_Ca', 'K_Mg', 'k_sr']


def to_P(U):
    u = {n: U[:, i] for i, n in enumerate(NAMES)}
    return dict(s_v=np.exp(u['log_sv']), alpha_L=np.exp(u['log_aL']), f0=expit(u['logit_f0']),
                a1=np.exp(u['log_a1']), b1=np.exp(u['log_b1']), a2=np.exp(u['log_a2']), b2=np.exp(u['log_b2']),
                E=np.exp(u['log_E']), logK=np.stack([u['log_KK'], u['log_KC'], u['log_KM']], 1),
                k_sr=np.exp(u['log_ksr']))


HIST_W = ['503', '341', '340', '193']
CL_TREND = [('503', 1984.0), ('503', 1999.0), ('503', 2001.0), ('341', 1984.0), ('341', 1999.0), ('341', 2001.0)]
EXP_W = [0, 1, 2]                                           # wells 503, 341, 340 during the experiment
CL_MONTHS = np.round(R.EXP0 + np.arange(1, 61) / 12.0, 6)   # monthly Cl, Feb 2026 ... Jan 2031
ION_TIMES = np.round(R.EXP0 + 0.5 * np.arange(1, 11), 6)    # semi-annual major ions (Na ... HCO3)


def obs_hist(out):
    """The 34 data of GJURMA-GO: the seven ions at four wells in 2016 and the Cl trend at 503 and 341."""
    T, w = out['times'], out['wells']
    i16 = R.tindex(T, 2016.0)
    y = [np.log(w[i16][:, k, :] * R.MW) for k in range(4)]
    y += [np.log(w[R.tindex(T, t)][:, R.W_NAMES.index(n), R.I_CL] * R.MW[R.I_CL])[:, None] for n, t in CL_TREND]
    return np.concatenate(y, 1)


def obs_exp(out):
    """Monthly Cl at wells 503, 341 and 340 and semi-annual Na, K, Ca, Mg, SO4, HCO3 there, 2026-2031."""
    T, w = out['times'], out['wells']
    ic = [R.tindex(T, t) for t in CL_MONTHS]
    ii = [R.tindex(T, t) for t in ION_TIMES]
    ycl = np.log(w[ic][:, :, EXP_W, R.I_CL] * R.MW[R.I_CL])            # (60, Ne, 3)
    yio = np.log(w[ii][:, :, EXP_W, 1:] * R.MW[1:])                     # (10, Ne, 3, 6)
    ne = w.shape[1]
    return np.concatenate([ycl.transpose(1, 0, 2).reshape(ne, -1), yio.transpose(1, 0, 2, 3).reshape(ne, -1)], 1)


def obs_steady(out):
    """Seven ions at the four wells of a steady field."""
    c = out['final']
    return np.concatenate([np.log(c[:, i, :] * R.MW) for i in R.I_WELLS], 1)


GOALS = ['Cl at 5 km (mg/L)', 'Na at 3 km (mg/L)', 'Ca + Mg at 3 km (meq/L)', 'strip with Cl > 250 mg/L (km)']


def goals(out):
    c = out[2045.0]
    cl = c[..., R.I_CL] * R.MW[R.I_CL]
    return np.stack([cl[:, R.I5], c[:, R.I3, R.I_NA] * R.MW[R.I_NA], 2 * (c[:, R.I3, R.I_CA] + c[:, R.I3, R.I_MG]),
                     (cl > 250.0).sum(1) * R.DX / 1000.0], 1)


def salinity_cost(out, out_ref):
    """Largest extra Cl (mg/L) at the well field (5 km) from the start of the experiment to 2045, per member."""
    i0 = R.tindex(out['times'], R.EXP0)
    return ((out['cl5'][i0:] - out_ref['cl5'][i0:]) * R.MW[R.I_CL]).max(0)


def fd_ensemble(h):
    p = M0.size
    Z = np.vstack([np.zeros(p)] + [h * np.eye(p)[j] for j in range(p)] + [-h * np.eye(p)[j] for j in range(p)])
    return M0 + Z * S0


def jac(Y, h):
    p = M0.size
    return ((Y[1:p + 1] - Y[p + 1:]) / (2 * h)).T             # (outputs, standardised parameters)


def laplace(J, sig=SIG_OBS):
    """Posterior covariance in prior-standardised parameters (prior N(0, I)) for data with error sig."""
    H = J.T @ J / sig ** 2
    return np.linalg.inv(H + np.eye(H.shape[0])), H


def esmda(d, obs_fn, design, rng, ne=100, na=4, U=None):
    if U is None:
        U = M0 + S0 * rng.standard_normal((ne, M0.size))
    for it in range(na):
        Y = obs_fn(R.simulate(to_P(U), design))
        bad = ~np.isfinite(Y).all(1)
        if bad.any():
            good = np.where(~bad)[0]
            U[bad] = U[rng.choice(good, bad.sum())] + 0.05 * S0 * rng.standard_normal((bad.sum(), M0.size))
            Y = obs_fn(R.simulate(to_P(U), design))
        du = U - U.mean(0); dy = Y - Y.mean(0)
        Cuy = du.T @ dy / (ne - 1); Cyy = dy.T @ dy / (ne - 1)
        Gm = Cyy + na * SIG_OBS ** 2 * np.eye(d.size)
        Dp = d + np.sqrt(na) * SIG_OBS * rng.standard_normal((ne, d.size))
        U = U + np.linalg.solve(Gm, (Dp - Y).T).T @ Cuy.T
        U = np.clip(U, M0 - 6 * S0, M0 + 6 * S0)
    out = R.simulate(to_P(U), design)
    return U, out
