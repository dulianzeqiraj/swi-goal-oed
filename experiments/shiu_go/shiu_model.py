"""SHIU-GO: the stochastic forcing of a coastal aquifer (rain, soil water, recharge) discovered from irregular,
incomplete observations, either as a separate jump SDE (route A) or as a term added to the flow equation (route B).

Test bed: the linear coastal aquifer of ASIMILIMI-GO (5 km, sea Dirichlet at x = 0 through a half cell, no flow
inland, T = 1000 m2/d, Sy = 0.1), here in 25 cells, with a well at 1.5 km and four piezometers. The recharge comes
from a rain-soil-vadose chain:

  rain        marked Poisson process, seasonal rate lambda(t) and seasonal exponential depths (mean abar(t)),
              with a wetness multiplier per year (wet, normal, dry and drought years);
  soil water  ds = -[Ep(t) min(1, s/sw) + L(s)] dt + min(a, sbar - s) dN   (bucket, jump SDE),
              L(s) = kL ((s - sfc)+ / (sbar - sfc))^bL  (drainage beyond field capacity);
  vadose      Erlang-2 delay of the drainage (two linear reservoirs, time constant tau each);
  error       R = (1 + e) R_det, e an Ornstein-Uhlenbeck process (multiplicative recharge error).

Observations follow the setting of Krach, Nubel & Teichmann (SPA 2026): random observation times and random masks.
Heads at four piezometers are observed on random days (probability 0.15 per day), each piezometer with probability
0.6, with noise sd 0.02 m. Rain, potential evapotranspiration, sea level and pumping are known daily inputs.

Given rain and the forcing law, the system is linear and Gaussian in (h, e), so the Kalman filter with the true law
gives the exact conditional expectation E[X_t | A_t] (the oracle), and the forecast loss of any other model exceeds
the oracle's by the masked mean-square distance between the two forecasts (Lemma 4.2 of Krach et al.)."""
import numpy as np
from numba import njit

OMEGA = 2 * np.pi / 365.0
YEAR = 365
YEAR_MULT = np.array([1.0, 0.9, 1.1,                    # spin-up, no head data
                      1.0, 1.35, 0.8, 1.0, 0.6, 1.15,   # training years 3-8
                      1.0, 0.4, 1.25, 0.9])             # test years 9-12 (year 10: drought)
ENV = np.array([-1, -1, -1, 1, 2, 0, 1, 0, 2, 1, 0, 2, 1])   # 0 dry, 1 normal, 2 wet (training environments)
N_YEARS = len(YEAR_MULT)
TRAIN = (3 * YEAR, 9 * YEAR)
TEST = (9 * YEAR, 13 * YEAR)
DROUGHT = (10 * YEAR, 11 * YEAR)

RAIN_LAW = dict(c0=-1.667, c1=0.8, d0=2.526, d1=0.3)
SOIL_KNOWN = dict(sbar=200.0, sw=120.0)
TRUE = dict(sfc=130.0, kL=25.0, bL=3.0, tau=20.0, sig_e=0.25, tau_e=90.0)
SIG_H, SIG_O = 3e-4, 0.02          # head process noise (m per day per cell), observation noise (m)
P_DAY, P_WELL = 0.15, 0.6


# ------------------------------------------------------------------------------------------------------------ aquifer
def aquifer(L=5000.0, N=25, T=1000.0, Sy=0.1, x_well=1500.0, piezo=(250.0, 1250.0, 2750.0, 4250.0), dt=1.0):
    """Implicit-Euler daily propagator of Sy dh/dt = T d2h/dx2 + R - Q delta_w, sea head at x = 0, no flow at L."""
    dx = L / N
    A = np.zeros((N, N))
    for i in range(N):
        if i > 0:
            A[i, i - 1] += T / dx ** 2; A[i, i] -= T / dx ** 2
        if i < N - 1:
            A[i, i + 1] += T / dx ** 2; A[i, i] -= T / dx ** 2
    A[0, 0] -= 2 * T / dx ** 2
    bsea = np.zeros(N); bsea[0] = 2 * T / dx ** 2
    Mi = np.linalg.inv(Sy * np.eye(N) - dt * A)
    ew = np.zeros(N); ew[int(x_well // dx)] = 1.0 / dx
    H = np.zeros((len(piezo), N))
    for k, xp in enumerate(piezo):
        H[k, int(xp // dx)] = 1.0
    return dict(N=N, dx=dx, xc=(np.arange(N) + 0.5) * dx, F=Sy * Mi, g_eta=dt * Mi @ bsea,
                g_r=dt * Mi @ np.ones(N), g_q=-dt * Mi @ ew, H=H, Sy=Sy, T=T, L=L, piezo=np.array(piezo))


def steady(aq, eta, R_m, Q):
    """Steady head for constant sea level eta (m), recharge R_m (m/d) and pumping Q (m2/d)."""
    I = np.eye(aq['N'])
    return np.linalg.solve(I - aq['F'], aq['g_eta'] * eta + aq['g_r'] * R_m + aq['g_q'] * Q)


# ------------------------------------------------------------------------------------------------------------ forcing
def days_axis(n=N_YEARS * YEAR):
    return np.arange(n) + 0.5


def pet(t):
    return 2.8 - 2.2 * np.cos(OMEGA * (t - 15.0))                       # mm/d


def rain_rates(t, law=RAIN_LAW, mult=None):
    lam = np.exp(law['c0'] + law['c1'] * np.cos(OMEGA * (t - 15.0)))
    if mult is not None:
        lam = lam * mult
    abar = np.exp(law['d0'] + law['d1'] * np.cos(OMEGA * (t - 15.0)))
    return lam, abar


def year_mult(n):
    return YEAR_MULT[np.minimum(np.arange(n) // YEAR, N_YEARS - 1)]


def simulate_rain(rng, n=N_YEARS * YEAR):
    t = days_axis(n)
    lam, abar = rain_rates(t, mult=year_mult(n))
    k = rng.poisson(lam)
    P = np.where(k > 0, rng.gamma(np.maximum(k, 1), abar), 0.0)
    return P, k


@njit(cache=True)
def bucket(P, Ep, sbar, sw, sfc, kL, bL, nsub, s0):
    """Daily soil-water bucket: the day's rain enters at the start (excess above sbar runs off), then ET and
    drainage act over the day in nsub explicit substeps. Returns daily drainage D (mm/d) and end-of-day storage."""
    n = P.shape[0]
    D = np.empty(n); S = np.empty(n)
    s = s0; h = 1.0 / nsub
    for i in range(n):
        s += min(P[i], sbar - s)
        d = 0.0
        for j in range(nsub):
            ex = (s - sfc) / (sbar - sfc)
            Lk = kL * ex ** bL if ex > 0 else 0.0
            et = Ep[i] * min(1.0, s / sw)
            tot = et + Lk
            ds = tot * h
            if ds > s:
                ds = s
            if tot > 0:
                d += ds * Lk / tot
            s -= ds
        D[i] = d; S[i] = s
    return D, S


@njit(cache=True)
def erlang2(u, tau):
    """Exact daily Erlang-2 filter (two linear reservoirs with time constant tau) of a daily input held constant."""
    a = np.exp(-1.0 / tau); b = a / tau
    n = u.shape[0]
    out = np.empty(n)
    r1 = u[0]; r2 = u[0]
    for i in range(n):
        r2n = a * r2 + b * r1 + (1.0 - a - b) * u[i]
        r1 = a * r1 + (1.0 - a) * u[i]
        r2 = r2n
        out[i] = r2
    return out


def recharge_det(P, Ep, sfc, kL, bL, tau, nsub=6, sbar=SOIL_KNOWN['sbar'], sw=SOIL_KNOWN['sw']):
    D, S = bucket(P, Ep, sbar, sw, sfc, kL, bL, nsub, 0.5 * (sw + sfc))
    return erlang2(D, tau), D, S


def ou(rng, n, sd, tau):
    phi = np.exp(-1.0 / tau)
    x = np.empty(n); x[0] = sd * rng.standard_normal()
    w = rng.standard_normal(n) * sd * np.sqrt(1 - phi ** 2)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + w[i]
    return x


def sea_level(rng, n):
    t = days_axis(n)
    eta = 0.15 * np.cos(OMEGA * (t - 300.0)) + ou(rng, n, 0.06, 20.0)
    surge = np.zeros(n)
    on = rng.random(n) < 4.0 / YEAR
    amp = np.where(on, 0.25 + rng.exponential(0.5, n), 0.0)
    s = 0.0
    for i in range(n):
        s = s * np.exp(-1.0 / 2.0) + amp[i]
        surge[i] = s
    return eta + surge


def pumping(n):
    t = days_axis(n)
    return 1.2 * (1.0 + 0.6 * np.sin(OMEGA * (t - 105.0)))           # m2/d per metre of coast


# ------------------------------------------------------------------------------------------------------------ twin
def simulate_twin(seed, aq=None):
    """One synthetic truth with random observation times and masks."""
    aq = aq or aquifer()
    rng = np.random.default_rng(seed)
    n = N_YEARS * YEAR
    t = days_axis(n)
    P, kev = simulate_rain(rng, n)
    Ep = pet(t)
    Rdet, D, S = recharge_det(P, Ep, TRUE['sfc'], TRUE['kL'], TRUE['bL'], TRUE['tau'], nsub=24)
    e = ou(rng, n, TRUE['sig_e'], TRUE['tau_e'])
    R = Rdet * (1.0 + e)                                               # mm/d
    eta = sea_level(rng, n)
    Q = pumping(n)
    h0 = steady(aq, 0.0, Rdet[:3 * YEAR].mean() / 1000.0, Q.mean())
    N = aq['N']
    h = np.empty((n, N))
    hc = h0.copy()
    wn = rng.standard_normal((n, N)) * SIG_H
    for i in range(n):
        hc = aq['F'] @ hc + aq['g_eta'] * eta[i] + aq['g_r'] * R[i] / 1000.0 + aq['g_q'] * Q[i] + wn[i]
        h[i] = hc
    X = h @ aq['H'].T
    obs_day = rng.random(n) < P_DAY
    obs_day[:3 * YEAR] = False
    mask = (rng.random((n, aq['H'].shape[0])) < P_WELL) & obs_day[:, None]
    none = obs_day & ~mask.any(1)
    for i in np.where(none)[0]:
        mask[i, rng.integers(aq['H'].shape[0])] = True
    y = np.where(mask, X + SIG_O * rng.standard_normal(X.shape), np.nan)
    return dict(seed=seed, t=t, P=P, kev=kev, Ep=Ep, Rdet=Rdet, D=D, S=S, e=e, R=R, eta=eta, Q=Q, h0=h0, X=X,
                y=y, mask=mask, obs_day=obs_day)


# ------------------------------------------------------------------------------------------------------------ filter
@njit(cache=True)
def kf(F, gr, base, bx, phi, qx, sh2, so2, H, y, mask, m0, P0, x0v, store_gain):
    """Kalman filter for z = (h, x): z_n = A_n z_{n-1} + c_n + w_n, A_n = [[F, gr*bx_n], [0, phi]], c_n = (base_n, 0).
    Process noise sh2 per head cell and qx for x; observations y_n = H h_n + noise on the masked rows.
    Returns, per observation day: sum of squared innovations, number observed, -log predictive density,
    number inside the 90% interval, the gap since the previous observation day; and the filtered x mean/variance
    per day. If store_gain, also the gains (for the linear response features of route B)."""
    N = F.shape[0]; nd = base.shape[0]; m = H.shape[0]
    z = np.zeros(N + 1); z[:N] = m0; z[N] = 0.0
    Pz = np.zeros((N + 1, N + 1)); Pz[:N, :N] = P0; Pz[N, N] = x0v
    A = np.zeros((N + 1, N + 1)); A[:N, :N] = F; A[N, N] = phi
    Qz = np.zeros((N + 1, N + 1))
    for i in range(N):
        Qz[i, i] = sh2
    Qz[N, N] = qx
    nev = 0
    for n in range(nd):
        if mask[n].any():
            nev += 1
    sse = np.zeros(nev); nob = np.zeros(nev); nll = np.zeros(nev); cov90 = np.zeros(nev)
    day = np.zeros(nev, dtype=np.int64); gap = np.zeros(nev)
    xm = np.zeros(nd); xv = np.zeros(nd)
    hm = np.zeros((nd, m)); hv = np.zeros((nd, m))
    K_all = np.zeros((nev, N + 1, m)) if store_gain else np.zeros((1, 1, 1))
    nu_all = np.zeros((nev, m))
    k = 0; last = -1
    for n in range(nd):
        for i in range(N):
            A[i, N] = gr[i] * bx[n]
        zn = A @ z
        zn[:N] += base[n]
        z = zn
        Pz = A @ Pz @ A.T + Qz
        if mask[n].any():
            idx = np.where(mask[n])[0]
            mo = idx.shape[0]
            Hs = np.zeros((mo, N + 1))
            for a in range(mo):
                Hs[a, :N] = H[idx[a]]
            nu = np.empty(mo)
            for a in range(mo):
                nu[a] = y[n, idx[a]] - (Hs[a] @ z)
            S = Hs @ Pz @ Hs.T
            for a in range(mo):
                S[a, a] += so2
            Si = np.linalg.inv(S)
            K = Pz @ Hs.T @ Si
            z = z + K @ nu
            Pz = Pz - K @ S @ K.T
            Pz = 0.5 * (Pz + Pz.T)
            sse[k] = (nu ** 2).sum(); nob[k] = mo
            sgn, ld = np.linalg.slogdet(S)
            nll[k] = 0.5 * (ld + nu @ Si @ nu + mo * np.log(2 * np.pi))
            c = 0.0
            for a in range(mo):
                if abs(nu[a]) <= 1.6448536 * np.sqrt(S[a, a]):
                    c += 1.0
            cov90[k] = c; day[k] = n; gap[k] = n - last if last >= 0 else 0
            for a in range(mo):
                nu_all[k, idx[a]] = nu[a]
            if store_gain:
                for a in range(mo):
                    K_all[k, :, idx[a]] = K[:, a]
            last = n; k += 1
        xm[n] = z[N]; xv[n] = Pz[N, N]
        for a in range(m):
            hm[n, a] = H[a] @ z[:N]
            hv[n, a] = H[a] @ Pz[:N, :N] @ H[a]
    return sse, nob, nll, cov90, day, gap, xm, xv, K_all, nu_all, hm, hv


@njit(cache=True)
def kf_response(F, gr, base, bx, phi, H, mask, K_all, m0):
    """Mean recursion of the filter with stored gains and zero data: the predicted observations (before each
    update) caused by the input `base` alone. Linear in the input, so it gives the response features of route B."""
    N = F.shape[0]; nd = base.shape[0]
    z = np.zeros(N + 1); z[:N] = m0
    nev = K_all.shape[0]; mobs = H.shape[0]
    out = np.zeros((nev, mobs))
    A = np.zeros((N + 1, N + 1)); A[:N, :N] = F; A[N, N] = phi
    k = 0
    for n in range(nd):
        for i in range(N):
            A[i, N] = gr[i] * bx[n]
        zn = A @ z
        zn[:N] += base[n]
        z = zn
        if mask[n].any():
            pred = H @ z[:N]
            nu = np.zeros(mobs)
            for a in range(mobs):
                if mask[n, a]:
                    out[k, a] = pred[a]
                    nu[a] = -pred[a]
            z = z + K_all[k] @ nu
            k += 1
    return out


def run_filter(aq, tw, R_det_mm, mode, sig_x, tau_x, store_gain=False):
    """mode 'mult': R = R_det (1 + x), x ~ OU(sig_x, tau_x); mode 'add': R = R_det + x (mm/d)."""
    n = len(tw['t'])
    base = (np.outer(tw['eta'], aq['g_eta']) + np.outer(R_det_mm / 1000.0, aq['g_r'])
            + np.outer(tw['Q'], aq['g_q']))
    bx = R_det_mm / 1000.0 if mode == 'mult' else np.full(n, 1.0 / 1000.0)
    phi = np.exp(-1.0 / tau_x)
    qx = sig_x ** 2 * (1 - phi ** 2)
    P0 = np.eye(aq['N']) * 0.3 ** 2
    y = np.nan_to_num(tw['y'])
    out = kf(aq['F'], aq['g_r'], base, bx, phi, qx, SIG_H ** 2, SIG_O ** 2, aq['H'], y, tw['mask'], tw['h0'],
             P0, sig_x ** 2, store_gain)
    keys = ('sse', 'nob', 'nll', 'cov90', 'day', 'gap', 'xm', 'xv', 'K', 'nu', 'hm', 'hv')
    r = dict(zip(keys, out))
    r['bx'], r['base'], r['phi'] = bx, base, phi
    return r


def window(r, lo, hi):
    w = (r['day'] >= lo) & (r['day'] < hi)
    return dict(loss=float(r['sse'][w].mean()), nll=float(r['nll'][w].sum() / r['nob'][w].sum()),
                cov=float(r['cov90'][w].sum() / r['nob'][w].sum()), n=int(w.sum()))
