"""PERTEJ-GO ("pertej": beyond): a transparent, learnable boundary condition for the coastal-aquifer flow equation.
Numerical checks N1-N4 of the theory note. usage: python pertej_exp.py  ->  res/pertej.json, res/pertej_series.npz

Test bed: a 1-D coastal aquifer, 10 km from the sea, cell-centred finite volumes (100 m), implicit Euler, daily steps,
20 years. The sea is a fixed head at x = 0; the far end is closed. The model sees only the first 2 km; the boundary at
2 km must stand in for the 8 km of aquifer beyond it. Recharge and pumping act inside the model domain.

N1 (Proposition 1): the exterior is replaced exactly by a positive Robin term plus positive first-order compartments;
   positive reduced versions fitted by nonnegative least squares; fixed-head, no-flow and calibrated-GHB boundaries.
N2 (Proposition 3): positive exponential sums for the half-order impedance of a semi-infinite exterior; the count of
   terms against the predicted count.
N3 (Proposition 2): energy of the unforced model with a passive boundary and with a negative conductance.
N4 (Proposition 4): the boundary identified from two noisy piezometers in a source-free band; seasonal forcing against
   broadband forcing; a closure source inside and outside the band; prediction under a new drought and pumping regime.
N5 (Section 7): a learned prior (regularizer) on the boundary, trained on 400 simulated exteriors; the identifications
   of N4 repeated with a prior whose ranges contain the truth and with a prior built on a wrong geology.
N6 (Section 8): a sea-level rise of 0.5 m in 20 years; how much less fresh water reaches the sea with each inland
   boundary (the reason the assembly note cut sea-level rise was its inland boundary).
"""
import json
import os
import time

import numpy as np
from scipy.linalg import cholesky, eigh, lu_factor, lu_solve, solve_triangular
from scipy.optimize import brentq, least_squares, nnls

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
T0 = time.time()

T, S, DX, DT = 500.0, 0.05, 100.0, 1.0            # m2/d, storage coefficient, m, d
NF, NM = 100, 20                                   # cells of the full aquifer and of the model domain
YEARS = 20
NT = int(round(365.25 * YEARS / DT))
c = T / DX                                         # conductance between neighbouring cells (per unit width)
CS = 2 * T / DX                                    # conductance from the first cell to the sea
WELL, PIEZ, B1, B2, BC = 9, 14, 17, 18, NM - 1    # well 0.95 km, piezometer 1.45 km, band piezometers, boundary cell
R0, Q0 = 5e-4, 0.6                                 # mean recharge (m/d) and pumping (m2/d per metre of coast)
RNG = np.random.default_rng(20261109)
OMEGA_BAND = (2 * np.pi / (40 * 365.25), 2 * np.pi / 5.0)


def tridiag(n, sea=True):
    A = np.zeros((n, n))
    for i in range(n - 1):
        A[i, i] += c; A[i + 1, i + 1] += c; A[i, i + 1] -= c; A[i + 1, i] -= c
    if sea:
        A[0, 0] += CS
    return A


def forcing(kind, nt=NT, drought=None, q_new=None):
    t = np.arange(1, nt + 1) * DT
    r = R0 * (1 + 0.8 * np.sin(2 * np.pi * t / 365.25))
    if drought is not None:
        a, b, f = drought
        r = np.where((t >= a) & (t < b), f * r, r)
    if kind == 'seasonal':
        Q = np.full(nt, Q0)
    else:
        Q = np.empty(nt); k = 0
        while k < nt:
            n = int(RNG.integers(180, 1081)); Q[k:k + n] = RNG.uniform(0.3, 1.0); k += n
        month = (t // 30.4375).astype(int)
        Q *= (1 + 0.15 * RNG.uniform(-1, 1, month.max() + 1))[month]
    if q_new is not None:
        a, b, val = q_new
        Q = np.where((t >= a) & (t < b), val, Q)
    return t, r, Q


def source_vector(n, r, Q, psi=None, psi_cell=None):
    f = np.zeros(n)
    f[:NM] += r * DX
    f[WELL] -= Q
    if psi is not None:
        f[psi_cell] += psi
    return f


def run_full(t, r, Q, psi=None, psi_cell=None, eta=None):
    """The whole 10 km aquifer from its steady state; eta: sea level above its initial value (m)."""
    A = tridiag(NF)
    M = S * DX
    f0 = source_vector(NF, R0, Q0)
    h = np.linalg.solve(A, f0)
    lu = lu_factor(np.eye(NF) * M / DT + A)
    out = np.empty((len(t), NF))
    for k in range(len(t)):
        f = source_vector(NF, r[k], Q[k], None if psi is None else psi[k], psi_cell)
        if eta is not None:
            f[0] += CS * eta[k]
        h = lu_solve(lu, M / DT * h + f)
        out[k] = h
    return out


def exact_exterior():
    """Exterior cells NM..NF-1 seen from the last model cell: the exact positive Robin + compartment representation."""
    ne = NF - NM
    Ab = tridiag(ne, sea=False)
    Ab[0, 0] += c                                   # coupling to the boundary cell (the interface head)
    mu, phi = eigh(Ab / (S * DX))
    w = c ** 2 * phi[0] ** 2 / (S * DX * mu)
    C = c - w.sum()
    return max(C, 0.0), w, mu, C


def Z(s, C, w, mu):
    s = np.atleast_1d(s)[:, None]
    return C + (w[None, :] * s / (s + mu[None, :])).sum(1)


def run_truncated(t, r, Q, C, w, mu, H, h0, psi=None, psi_cell=None, eta=None):
    """Model domain only; boundary flux out of the last cell q = C u + sum_m w_m (u - y_m), y_m' = mu_m (u - y_m),
    u = h_BC - H. Starts from the steady state h0 with the compartments at rest (y = 0)."""
    A = tridiag(NM)
    M = S * DX
    a = 1.0 / (1.0 + DT * mu)
    G = C + np.sum(w * a)                           # implicit-Euler effective conductance
    A[BC, BC] += G
    lu = lu_factor(np.eye(NM) * M / DT + A)
    y = np.zeros_like(mu)
    h = h0.copy()
    out = np.empty((len(t), NM)); flux = np.empty(len(t)); energy = np.empty(len(t))
    for k in range(len(t)):
        rhs = M / DT * h + source_vector(NM, r[k], Q[k], None if psi is None else psi[k], psi_cell)
        rhs[BC] += G * H + np.sum(w * a * y)
        if eta is not None:
            rhs[0] += CS * eta[k]
        h = lu_solve(lu, rhs)
        u = h[BC] - H
        y = a * (y + DT * mu * u)
        out[k] = h
        flux[k] = C * u + np.sum(w * (u - y))
        energy[k] = 0.5 * M * np.sum((h - H) ** 2) + 0.5 * np.sum(np.where(mu > 0, w / mu, 0.0) * y ** 2)
    return out, flux, energy


def fit_positive(Ztarget_fun, M_terms, band=OMEGA_BAND, n_freq=240):
    om = np.geomspace(band[0], band[1], n_freq)
    mu = np.geomspace(band[0] / 3, band[1] * 3, M_terms)
    s = 1j * om
    Zt = Ztarget_fun(s)
    cols = [np.ones_like(s)] + [s / (s + m) for m in mu]
    Aw = np.array(cols).T / np.abs(Zt)[:, None]
    bw = Zt / np.abs(Zt)
    A = np.vstack([Aw.real, Aw.imag]); b = np.concatenate([bw.real, bw.imag])
    x, _ = nnls(A, b)
    return x[0], x[1:], mu


def rms(a):
    return float(np.sqrt(np.mean(np.asarray(a) ** 2)))


R = {'setup': dict(T=T, S=S, DX=DX, DT=DT, NF=NF, NM=NM, years=YEARS, c=c, well_km=(WELL + 0.5) * DX / 1000,
                   piez_km=(PIEZ + 0.5) * DX / 1000, band_piez_km=[(B1 + 0.5) * DX / 1000, (B2 + 0.5) * DX / 1000],
                   boundary_km=NM * DX / 1000, diffusivity=T / S, R0=R0, Q0=Q0)}

# ------------------------------------------------------------------------------------------------ N1
print('N1 exact and reduced boundaries', flush=True)
t, r, Q = forcing('broadband')
full = run_full(t, r, Q)
Cx, wx, mux, C_raw = exact_exterior()
A0 = tridiag(NF); h0_full = np.linalg.solve(A0, source_vector(NF, R0, Q0)); H = h0_full[BC]; h0 = h0_full[:NM]
exact, qx, _ = run_truncated(t, r, Q, Cx, wx, mux, H, h0=h0)
N1 = dict(n_compartments=len(mux), C_exact=C_raw, sum_w=float(wx.sum()), c=c, mu_min=float(mux.min()),
          mu_max=float(mux.max()), slowest_years=float(1 / mux.min() / 365.25),
          exact_err=dict(piez=float(np.abs(exact[:, PIEZ] - full[:, PIEZ]).max()),
                         bc=float(np.abs(exact[:, BC] - full[:, BC]).max())), cases={})
series = {'t': t, 'full_bc': full[:, BC], 'full_piez': full[:, PIEZ]}
Zex = lambda s: Z(s, Cx, wx, mux)
for M_terms in (3, 6, 12):
    Cf, wf, muf = fit_positive(Zex, M_terms)
    tr, _, _ = run_truncated(t, r, Q, Cf, wf, muf, H, h0=h0)
    om = np.geomspace(*OMEGA_BAND, 400)
    zerr = np.abs(Z(1j * om, Cf, wf, muf) - Zex(1j * om)) / np.abs(Zex(1j * om))
    N1['cases'][f'pertej_M{M_terms}'] = dict(rms_piez=rms(tr[:, PIEZ] - full[:, PIEZ]), rms_bc=rms(tr[:, BC] - full[:, BC]),
                                             max_bc=float(np.abs(tr[:, BC] - full[:, BC]).max()),
                                             z_err_max=float(zerr.max()), z_err_med=float(np.median(zerr)),
                                             n_positive=int((wf > 0).sum()))
    series[f'pertej_M{M_terms}_bc'] = tr[:, BC]
nofl, _, _ = run_truncated(t, r, Q, 0.0, np.zeros(1), np.ones(1), H, h0=h0)
fixd, _, _ = run_truncated(t, r, Q, c, np.zeros(1), np.ones(1), H, h0=h0)
best = (np.inf, None, None)
for Cg in np.geomspace(1e-4 * c, 10 * c, 70):
    g, _, _ = run_truncated(t, r, Q, Cg, np.zeros(1), np.ones(1), H, h0=h0)
    e = rms(g[:, PIEZ] - full[:, PIEZ])
    if e < best[0]:
        best = (e, Cg, g)
for name, tr in (('no_flow', nofl), ('fixed_head', fixd), ('ghb_calibrated', best[2])):
    N1['cases'][name] = dict(rms_piez=rms(tr[:, PIEZ] - full[:, PIEZ]), rms_bc=rms(tr[:, BC] - full[:, BC]),
                             max_bc=float(np.abs(tr[:, BC] - full[:, BC]).max()))
    series[f'{name}_bc'] = tr[:, BC]
N1['ghb_C'] = float(best[1]); N1['ghb_C_over_c'] = float(best[1] / c)
N1['head_range_bc'] = float(full[:, BC].max() - full[:, BC].min())
R['N1'] = N1
print(f'  exact max err {N1["exact_err"]}  ({time.time() - T0:.0f} s)', flush=True)

# ------------------------------------------------------------------------------------------------ N2
print('N2 half-order impedance', flush=True)
N2 = {'rows': []}
for decades in (4, 6):
    wmin = 2 * np.pi / (30 * 365.25)
    wmax = wmin * 10 ** decades
    om = np.geomspace(wmin, wmax, 2000)
    for eps in (1e-2, 1e-3):
        L = np.log(1 / eps)
        Xm = np.log(wmin) + 2 * np.log(np.pi * eps / 2)
        Xp = np.log(wmax) + 2 * np.log(2 / (np.pi * eps))
        eta = np.pi ** 2 / L
        M_pred = int(np.ceil((Xp - Xm) / eta)) + 1
        def err_for(M):
            x = np.linspace(Xm, Xp, M); h = x[1] - x[0] if M > 1 else 1.0
            mu = np.exp(x); w = (h / np.pi) * np.exp(x / 2)
            s = 1j * om
            Zt = (w[None, :] * s[:, None] / (s[:, None] + mu[None, :])).sum(1)
            return float(np.max(np.abs(Zt - np.sqrt(s)) / np.abs(np.sqrt(s))))
        e_pred = err_for(M_pred)
        M_min = next(M for M in range(2, 200) if err_for(M) <= eps)
        N2['rows'].append(dict(decades=decades, eps=eps, M_pred=M_pred, err_at_M_pred=e_pred, M_min_same_window=M_min))
curve = {}
wmin = 2 * np.pi / (30 * 365.25); om = np.geomspace(wmin / 10, wmin * 1e5, 400)
for M in (4, 8, 13):
    eps = 1e-2; L = np.log(1 / eps)
    Xm = np.log(wmin) + 2 * np.log(np.pi * eps / 2); Xp = np.log(wmin * 1e4) + 2 * np.log(2 / (np.pi * eps))
    x = np.linspace(Xm, Xp, M); h = x[1] - x[0]
    mu = np.exp(x); w = (h / np.pi) * np.exp(x / 2); s = 1j * om
    Zt = (w[None, :] * s[:, None] / (s[:, None] + mu[None, :])).sum(1)
    curve[M] = np.abs(Zt - np.sqrt(s)) / np.abs(np.sqrt(s))
series['n2_omega'] = om
for M, v in curve.items():
    series[f'n2_err_M{M}'] = v
R['N2'] = N2

# ------------------------------------------------------------------------------------------------ N3
print('N3 passivity', flush=True)
nt3 = int(5 * 365.25)
t3 = np.arange(1, nt3 + 1) * DT
z = np.zeros(nt3)
hb = np.zeros(NM); hb[8:13] = 1.0
N3 = {}
def run_unforced(C, w, mu):
    A = tridiag(NM); M = S * DX; a = 1 / (1 + DT * mu); G = C + np.sum(w * a); A[BC, BC] += G
    lu = lu_factor(np.eye(NM) * M / DT + A); h = hb.copy(); y = np.zeros_like(mu); E = np.empty(nt3)
    for k in range(nt3):
        rhs = M / DT * h; rhs[BC] += np.sum(w * a * y)
        h = lu_solve(lu, rhs); u = h[BC]; y = a * (y + DT * mu * u)
        E[k] = 0.5 * M * np.sum(h ** 2) + 0.5 * np.sum(w / mu * y ** 2)
    return E
E_pass = run_unforced(Cx, wx, mux)
N3['passive'] = dict(E0=float(0.5 * S * DX * np.sum(hb ** 2)), E_end=float(E_pass[-1]),
                     monotone=bool(np.all(np.diff(E_pass) <= 1e-12)))
series['n3_t'] = t3; series['n3_E_passive'] = E_pass
def semi_discrete_rate(n, G):
    """Largest eigenvalue of the unforced semi-discrete model (n cells, boundary conductance G); > 0 means growth."""
    A = tridiag(n); A[n - 1, n - 1] += G
    return float(np.linalg.eigvalsh(-A / (S * DX)).max())


Lm = NM * DX
for alpha in (0.02, 0.2):
    E_neg = run_unforced(-alpha * c, np.zeros(1), np.ones(1))
    k = max(1, int(0.8 * nt3))
    rate = float(np.log(E_neg[-1] / E_neg[k - 1]) / (2 * (t3[-1] - t3[k - 1])))
    # continuum: tanh(z)/z = T/(alpha c L), lambda = T z^2/(S L^2); a root exists only if alpha c L/T > 1
    tgt = T / (alpha * c * Lm)
    lam = T * brentq(lambda q: np.tanh(q) / q - tgt, 1e-6, 50) ** 2 / (S * Lm ** 2) if tgt < 1 else None
    lam_d = semi_discrete_rate(NM, -alpha * c)
    N3[f'negative_{alpha}'] = dict(E_end_over_E0=float(E_neg[-1] / E_neg[0]), growth_rate_per_day=rate,
                                   predicted_rate=lam, predicted_rate_semidiscrete=lam_d,
                                   predicted_rate_implicit_euler=float(-np.log(1 - lam_d * DT) / DT) if lam_d > 0 else None,
                                   threshold_alpha=float(DX / Lm), threshold_alpha_discrete=float(1 / (NM - 0.5)))
    series[f'n3_E_neg_{alpha}'] = E_neg
# the same non-passive boundary (alpha = 0.02, stable in the 2 km model) in longer models
N3['length_test'] = [dict(L_km=n * DX / 1000, alpha_threshold=float(1 / (n - 0.5)),
                          rate_per_day=semi_discrete_rate(n, -0.02 * c)) for n in (20, 40, 60, 80)]
R['N3'] = N3

# ------------------------------------------------------------------------------------------------ N4
print('N4 identifiability', flush=True)
mu_grid = np.geomspace(OMEGA_BAND[0] / 3, OMEGA_BAND[1] * 3, 12)
A_IE = 1 / (1 + DT * mu_grid)


def band_model(theta, o17, rr, h18_0):
    """Cells 18-19 driven by the observed head of cell 17 and the known recharge; boundary = positive compartments."""
    M = S * DX
    C, w = theta[0], theta[1:]
    G = C + np.sum(w * A_IE)
    A11, A12, A21, A22 = M / DT + 2 * c, -c, -c, M / DT + c + G
    det = A11 * A22 - A12 * A21
    h18, h19 = h18_0, H; y = np.zeros_like(mu_grid); out = np.empty(len(o17)); wa = w * A_IE
    for k in range(len(o17)):
        b1 = M / DT * h18 + c * o17[k] + rr[k] * DX
        b2 = M / DT * h19 + G * H + np.dot(wa, y) + rr[k] * DX
        h18 = (b1 * A22 - A12 * b2) / det; h19 = (A11 * b2 - A21 * b1) / det
        y = A_IE * (y + DT * mu_grid * (h19 - H)); out[k] = h18
    return out


def identify(o17, o18, rr):
    """Output-error fit of the nonnegative boundary parameters (no differentiation of noisy data)."""
    res = least_squares(lambda th: band_model(th, o17, rr, o18[0]) - o18, np.full(13, c / 13.0), bounds=(0, np.inf),
                        x_scale='jac', max_nfev=300)
    return res.x[0], res.x[1:]


BANDS = dict(low=(2 * np.pi / (200 * 365.25), 2 * np.pi / (40 * 365.25)), mid=(2 * np.pi / (10 * 365.25), 2 * np.pi / 30),
             high=(2 * np.pi / 10, 2 * np.pi / 2.5))


def bands_error(Cf, wf):
    out = {}
    for name, (lo, hi) in BANDS.items():
        om = np.geomspace(lo, hi, 100)
        out[name] = float(np.median(np.abs(Z(1j * om, Cf, wf, mu_grid) - Zex(1j * om)) / np.abs(Zex(1j * om))))
    return out


# the prediction test: a drought (recharge x 0.3 in years 3-8) and pumping of 1.2 m2/d from year 2, ten years
tp, rp, Qp = forcing('seasonal', nt=int(10 * 365.25), drought=(3 * 365.25, 8 * 365.25, 0.3), q_new=(2 * 365.25, 1e9, 1.2))
full_p = run_full(tp, rp, Qp)
N4 = {'cases': {}}
DATA = {}
om_plot = np.geomspace(2 * np.pi / (200 * 365.25), 2 * np.pi / 2.5, 300)
series['n4_omega'] = om_plot; series['n4_Z_exact'] = np.abs(Zex(1j * om_plot))
for kind in ('seasonal', 'broadband'):
    t4, r4, Q4 = forcing(kind)
    f4 = run_full(t4, r4, Q4)
    for sig in (0.002, 0.01):
        o17 = f4[:, B1] + sig * RNG.standard_normal(len(t4)); o18 = f4[:, B2] + sig * RNG.standard_normal(len(t4))
        Cf, wf = identify(o17, o18, r4)
        pred, _, _ = run_truncated(tp, rp, Qp, Cf, wf, mu_grid, H, h0=h0)
        key = f'{kind}_{int(sig * 1000)}mm'
        DATA[key] = (o17, o18, r4, Cf, wf)
        series[f'n4_pred_{key}'] = pred[:, BC]
        N4['cases'][key] = dict(kind=kind, noise_m=sig, C=float(Cf), n_positive=int((wf > 1e-9).sum()),
                                band_err=bands_error(Cf, wf), pred_rms_piez=rms(pred[:, PIEZ] - full_p[:, PIEZ]),
                                pred_rms_bc=rms(pred[:, BC] - full_p[:, BC]),
                                pred_max_bc=float(np.abs(pred[:, BC] - full_p[:, BC]).max()))
        series[f'n4_Z_{key}'] = np.abs(Z(1j * om_plot, Cf, wf, mu_grid))
        print(f'  {key}: {N4["cases"][key]["band_err"]}', flush=True)
# the exact boundary and the plain alternatives on the same prediction
ex_p, _, _ = run_truncated(tp, rp, Qp, Cx, wx, mux, H, h0=h0)
fx_p, _, _ = run_truncated(tp, rp, Qp, c, np.zeros(1), np.ones(1), H, h0=h0)
nf_p, _, _ = run_truncated(tp, rp, Qp, 0.0, np.zeros(1), np.ones(1), H, h0=h0)
gh_p, _, _ = run_truncated(tp, rp, Qp, best[1], np.zeros(1), np.ones(1), H, h0=h0)
N4['prediction_reference'] = dict(exact=rms(ex_p[:, BC] - full_p[:, BC]), fixed_head=rms(fx_p[:, BC] - full_p[:, BC]),
                                  no_flow=rms(nf_p[:, BC] - full_p[:, BC]), ghb_calibrated=rms(gh_p[:, BC] - full_p[:, BC]),
                                  head_change_bc=float(full_p[:, BC].max() - full_p[:, BC].min()))
series['n4_pred_t'] = tp; series['n4_pred_full'] = full_p[:, BC]; series['n4_pred_ghb'] = gh_p[:, BC]
# a closure source inside and outside the band (broadband forcing, 2 mm noise)
t4, r4, Q4 = forcing('broadband')
psi = 0.15 * np.sin(2 * np.pi * t4 / 365.25 + 1.0) + 0.1 * (t4 > 6 * 365.25)
for cell, name in ((BC, 'psi_in_band'), (12, 'psi_outside_band')):
    f4 = run_full(t4, r4, Q4, psi=psi, psi_cell=cell)
    o17 = f4[:, B1] + 0.002 * RNG.standard_normal(len(t4)); o18 = f4[:, B2] + 0.002 * RNG.standard_normal(len(t4))
    Cf, wf = identify(o17, o18, r4)
    N4[name] = dict(cell_km=(cell + 0.5) * DX / 1000, band_err=bands_error(Cf, wf), C=float(Cf),
                    psi_amplitude=0.15, psi_step=0.1)
    series[f'n4_Z_{name}'] = np.abs(Z(1j * om_plot, Cf, wf, mu_grid))
    print(f'  {name}: {N4[name]["band_err"]}', flush=True)
R['N4'] = N4

# ------------------------------------------------------------------------------------------------ N5
print('N5 learned prior', flush=True)
RNG5 = np.random.default_rng(5)
OM_PR = np.geomspace(2 * np.pi / (200 * 365.25), 2 * np.pi / 2.5, 24)


def features(C, w, mu):
    """What the prior sees: log Re Z and log Im Z at 24 frequencies (200 years to 2.5 days)."""
    Zp = Z(1j * OM_PR, C, w, mu)
    return np.concatenate([np.log(Zp.real + 1e-9), np.log(Zp.imag + 1e-9)])


def random_exterior(rng, T_rng, S_rng, n_rng):
    """A plausible exterior: n_rng cells of 100 m, correlated heterogeneous T (median in T_rng), S in S_rng, closed or
    leaky (to a river or lake) at the far end. Exact boundary by Proposition 1."""
    n = int(rng.integers(n_rng[0], n_rng[1] + 1))
    g = np.empty(n); g[0] = rng.standard_normal()
    for i in range(1, n):
        g[i] = 0.9 * g[i - 1] + np.sqrt(1 - 0.81) * rng.standard_normal()
    Te = np.exp(rng.uniform(np.log(T_rng[0]), np.log(T_rng[1]))) * np.exp(0.5 * g)
    Se = np.exp(rng.uniform(np.log(S_rng[0]), np.log(S_rng[1])))
    cc = 2 * Te[:-1] * Te[1:] / (DX * (Te[:-1] + Te[1:]))
    Ab = np.zeros((n, n)); i = np.arange(n - 1)
    Ab[i, i] += cc; Ab[i + 1, i + 1] += cc; Ab[i, i + 1] -= cc; Ab[i + 1, i] -= cc
    c_int = 2 * T * Te[0] / (DX * (T + Te[0]))
    Ab[0, 0] += c_int
    leaky = bool(rng.uniform() < 0.5)
    if leaky:
        Ab[-1, -1] += Te[-1] / DX * np.exp(rng.uniform(np.log(0.1), np.log(2.0)))
    mu, phi = eigh(Ab / (Se * DX))
    w = c_int ** 2 * phi[0] ** 2 / (Se * DX * mu)
    return max(c_int - w.sum(), 0.0), w, mu, leaky


class Prior:
    """Gaussian on the 48 log-impedance features of an ensemble of simulated exteriors (with 1% shrinkage). A neural
    density (for example a normalizing flow) would replace it for a richer ensemble; the use below is the same."""

    def __init__(self, rng, T_rng, S_rng, n_rng, K=400):
        ens = [random_exterior(rng, T_rng, S_rng, n_rng) for _ in range(K)]
        F = np.array([features(Ck, wk, muk) for Ck, wk, muk, _ in ens])
        self.fm = F.mean(0)
        Sig = np.cov(F.T); Sig += 0.01 * np.trace(Sig) / len(self.fm) * np.eye(len(self.fm))
        self.Rch = cholesky(Sig, lower=True)
        self.d_ens = np.array([self.maha(f) for f in F])
        self.Zabs = np.array([np.abs(Z(1j * om_plot, Ck, wk, muk)) for Ck, wk, muk, _ in ens])
        self.info = dict(K=K, T_median_range=list(T_rng), S_range=list(S_rng), length_km=[n_rng[0] / 10, n_rng[1] / 10],
                         leaky_fraction=float(np.mean([e[3] for e in ens])), n_features=len(self.fm),
                         ens_maha_p50=float(np.median(self.d_ens)), ens_maha_p99=float(np.quantile(self.d_ens, 0.99)))

    def res(self, C, w, mu):
        return solve_triangular(self.Rch, features(C, w, mu) - self.fm, lower=True)

    def maha(self, f):
        return float(np.sum(solve_triangular(self.Rch, f - self.fm, lower=True) ** 2))

    def pct(self, d):
        return float(np.mean(self.d_ens < d))


def identify_map(o17, o18, rr, sigma, prior):
    """Output error plus the learned prior: the noise level and the ensemble fix the weight, nothing is tuned."""
    f = lambda th: np.concatenate([(band_model(th, o17, rr, o18[0]) - o18) / sigma, prior.res(th[0], th[1:], mu_grid)])
    res = least_squares(f, np.full(13, c / 13.0), bounds=(0, np.inf), x_scale='jac', max_nfev=300)
    return res.x[0], res.x[1:]


# 'near': ranges that contain the truth; 'shifted': a geology that is wrong (a less conductive, less storative aquifer)
PRIORS = dict(near=Prior(RNG5, (150, 1500), (0.01, 0.2), (30, 150)),
              shifted=Prior(RNG5, (40, 160), (0.004, 0.02), (30, 150)))
N5 = dict(priors={}, cases={})
for name, pr in PRIORS.items():
    d_truth = pr.maha(features(Cx, wx, mux))
    N5['priors'][name] = dict(pr.info, truth_mahalanobis=d_truth, truth_percentile=pr.pct(d_truth))
    series[f'n5_{name}_Z_q05'], series[f'n5_{name}_Z_q50'], series[f'n5_{name}_Z_q95'] = \
        np.quantile(pr.Zabs, [0.05, 0.5, 0.95], axis=0)
for key, (o17, o18, rr, Cf, wf) in DATA.items():
    sig_hat = rms(band_model(np.concatenate([[Cf], wf]), o17, rr, o18[0]) - o18)
    out = dict(sigma_hat=sig_hat, band_err_plain=N4['cases'][key]['band_err'],
               pred_rms_bc_plain=N4['cases'][key]['pred_rms_bc'])
    for name, pr in PRIORS.items():
        Cm, wm = identify_map(o17, o18, rr, sig_hat, pr)
        pred, _, _ = run_truncated(tp, rp, Qp, Cm, wm, mu_grid, H, h0=h0)
        d_plain, d_map = pr.maha(features(Cf, wf, mu_grid)), pr.maha(features(Cm, wm, mu_grid))
        out[name] = dict(band_err=bands_error(Cm, wm), pred_rms_bc=rms(pred[:, BC] - full_p[:, BC]),
                         maha_plain=d_plain, maha_map=d_map, pct_plain=pr.pct(d_plain), pct_map=pr.pct(d_map))
        series[f'n5_Z_{name}_{key}'] = np.abs(Z(1j * om_plot, Cm, wm, mu_grid))
        series[f'n5_pred_{name}_{key}'] = pred[:, BC]
    N5['cases'][key] = out
    print(f"  {key}: plain {out['band_err_plain']}  near {out['near']['band_err']}  shifted {out['shifted']['band_err']}",
          flush=True)
R['N5'] = N5

# ------------------------------------------------------------------------------------------------ N6
print('N6 sea-level rise', flush=True)
eta = 0.5 * t / t[-1]                                   # 0.5 m in 20 years, on top of the forcing of N1
full_s = run_full(t, r, Q, eta=eta)


def discharge_change(h_eta, h_ref):
    """Change of the fresh discharge to the sea (m2/d per metre of coast); negative: less fresh water reaches it."""
    return CS * ((h_eta[:, 0] - eta) - h_ref[:, 0])


q_sea_ref = float(np.mean(CS * full[:, 0]))
N6 = dict(rise_m=0.5, years=YEARS, q_sea_mean_ref=q_sea_ref, cases={})
specs = [('full', None), ('pertej_M6', fit_positive(Zex, 6)), ('pertej_M12', fit_positive(Zex, 12)),
         ('no_flow', (0.0, np.zeros(1), np.ones(1))), ('fixed_head', (c, np.zeros(1), np.ones(1))),
         ('ghb_calibrated', (best[1], np.zeros(1), np.ones(1)))]
for name, spec in specs:
    if spec is None:
        dq = discharge_change(full_s, full)
    else:
        a1, _, _ = run_truncated(t, r, Q, *spec, H, h0, eta=eta)
        a0, _, _ = run_truncated(t, r, Q, *spec, H, h0)
        dq = discharge_change(a1, a0)
    N6['cases'][name] = dict(deficit_m3_per_m=float(-np.sum(dq) * DT), dq_end=float(dq[-1]),
                             dq_end_rel=float(dq[-1] / q_sea_ref))
    series[f'n6_dq_{name}'] = dq
    print(f"  {name}: deficit {N6['cases'][name]['deficit_m3_per_m']:.1f} m3/m, end {dq[-1]:.4f} m2/d", flush=True)
R['N6'] = N6
R['runtime_s'] = time.time() - T0
os.makedirs(RES, exist_ok=True)
with open(os.path.join(RES, 'pertej.json'), 'w') as fh:
    json.dump(R, fh, indent=1)
np.savez_compressed(os.path.join(RES, 'pertej_series.npz'), **series)
print(f'saved res/pertej.json ({R["runtime_s"]:.0f} s)')
