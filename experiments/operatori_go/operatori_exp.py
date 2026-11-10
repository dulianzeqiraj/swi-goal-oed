"""OPERATORI-GO: boundary conditions treated as operators, after the cost-accuracy study of de Hoop, Huang, Qian and
Stuart (2022), on the dimensionless coastal strip of the deterministic-first treatment (L = 1, D = 1, sea at x = 0,
no flow at x = 1, tau_1 = 4/pi^2).

Four checks:
  1. Aquifer-filtered input dimension: number of Karhunen-Loeve (PCA) modes of the sea-level record needed for the
     head at x to within delta, against the band-limit law of Proposition A and the usual 99 %-variance PCA count.
  2. Compute, do not learn, a linear boundary operator: exact operator from model runs against a PCA-Net with a
     linear map learned from N samples (Proposition B).
  3. A kinked boundary map (capped recharge): learned PCA-Net maps (linear, random-feature ReLU) against the exact
     treatment that applies the cap to the input before the linear operator.
  4. Certified out-of-distribution guard: |error at x| <= gamma_x * ||(I - P) g|| for amplitude and memory changes.

usage: python operatori_exp.py OUT.json        (numpy only, about 1 minute)"""
import json
import sys

import numpy as np

RNG = np.random.default_rng(20261110)
L, D = 1.0, 1.0
TAU1 = 4 * L**2 / (np.pi**2 * D)
NX, T, NT = 100, 1.2, 1200
DX, DT = L / NX, T / NT
X = DX * np.arange(1, NX + 1)
TT = DT * np.arange(1, NT + 1)


def system():
    """Implicit Euler for u_t = D u_xx, u(0) = g, u_x(1) = 0 on nodes x_1..x_NX; returns A and the boundary vector."""
    r = D * DT / DX**2
    A = np.zeros((NX, NX))
    for j in range(NX):
        A[j, j] = 1 + 2 * r
        if j > 0:
            A[j, j - 1] = -r
        if j < NX - 1:
            A[j, j + 1] = -r
    A[NX - 1, NX - 2] = -2 * r          # ghost node for the no-flow end
    b = np.zeros(NX); b[0] = r           # Dirichlet value enters the first row
    return A, b


A, BVEC = system()
AINV = np.linalg.inv(A)


def operator(source):
    """Matrix M (NX x NT) with h(T) = M f for a forcing record f on the time grid; source = vector entering per step."""
    M = np.zeros((NX, NT))
    v = AINV @ source
    for k in range(NT - 1, -1, -1):      # input at step k is propagated NT-1-k further steps
        M[:, k] = v
        v = AINV @ v
    return M


def ou_cov(tau, s=1.0):
    return s**2 * np.exp(-np.abs(TT[:, None] - TT[None, :]) / tau)


def kl(C):
    lam, phi = np.linalg.eigh(C)
    i = np.argsort(lam)[::-1]
    return np.clip(lam[i], 0, None), phi[:, i]


def ou_paths(n, tau, s=1.0):
    a = np.exp(-DT / tau)
    z = np.empty((n, NT)); z[:, 0] = RNG.standard_normal(n)
    e = RNG.standard_normal((n, NT)) * np.sqrt(1 - a**2)
    for k in range(1, NT):
        z[:, k] = a * z[:, k - 1] + e[:, k]
    return s * z


def prop_a_bound(x, Om, tau, s=1.0):
    """Proposition A: stationary head variance at x from boundary frequencies above Om, for a non-increasing spectrum
    (here Ornstein-Uhlenbeck), valid for Om >= omega_L = D ln(4)^2 / (2 L^2)."""
    a = x * np.sqrt(2 / D)
    S_Om = 2 * s**2 * tau / (1 + (Om * tau)**2)
    return 16 * S_Om / np.pi * np.exp(-a * np.sqrt(Om)) * (np.sqrt(Om) / a + 1 / a**2)


def omega_x(x, delta, tau):
    lo, hi = D * np.log(4)**2 / (2 * L**2), 1e9
    if prop_a_bound(x, lo, tau) <= delta**2:
        return lo
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if prop_a_bound(x, mid, tau) > delta**2 else (lo, mid)
    return hi


def exact_tail(x, Om, tau, s=1.0):
    """(1/pi) int_Om^inf S_g |H|^2 domega with the finite-strip transfer function (Theorem 4(i) of the companion)."""
    w = np.geomspace(max(Om, 1e-6), 1e9, 400001)
    b = L * np.sqrt(2 * w / D); bp = b * (1 - x / L)
    H2 = np.exp(bp - b) * (1 + np.exp(-2 * bp) + 2 * np.cos(bp) * np.exp(-bp)) / (1 + np.exp(-2 * b) + 2 * np.cos(b) * np.exp(-b))
    S = 2 * s**2 * tau / (1 + (w * tau)**2)
    f = S * H2
    return np.trapezoid(f, w) / np.pi


def check1(rho=0.02, delta=0.25):
    tau = rho * TAU1
    M = operator(BVEC)
    C = ou_cov(tau)
    lam, phi = kl(C)
    G = M @ phi                                   # response of every node to every KL mode
    tot = (G**2 * lam).sum(axis=1)                # head variance at T from the boundary record
    tail = np.cumsum(((G**2) * lam)[:, ::-1], axis=1)[:, ::-1]   # tail[j, d] = variance left when keeping d modes
    xs = [0.02, 0.05, 0.1, 0.2, 0.3, 0.4]
    rows = []
    for xv in xs:
        j = int(round(xv / DX)) - 1
        need = 0 if tot[j] <= delta**2 else int(np.argmax(np.append(tail[j, 1:], 0.0) <= delta**2) + 1)
        Om = omega_x(xv, delta, tau)
        pred = T * Om / np.pi
        rows.append(dict(x=xv, head_sd=float(np.sqrt(tot[j])), modes_needed=need, prop_a_modes=float(pred),
                         omega=float(Om), exact_tail_at_omega=float(exact_tail(xv, Om, tau)),
                         bound_at_omega=float(prop_a_bound(xv, Om, tau))))
    frac = np.cumsum(lam) / lam.sum()
    d99 = int(np.searchsorted(frac, 0.99) + 1)
    inside = np.sqrt(tot) > delta
    shell = float(X[np.argmin(inside)]) if (~inside).any() else L
    # heads in the shell beyond x = 0.05: input KL modes against the optimal (Eckart-Young) rank, RMS error <= eps
    js = (X >= 0.05 - 1e-12) & (X < shell)
    Gs = G[js] * np.sqrt(lam)
    left_kl = np.cumsum((Gs**2).sum(axis=0)[::-1])[::-1] / js.sum()
    sv = np.linalg.svd(Gs, compute_uv=False)
    left_opt = np.cumsum((sv**2)[::-1])[::-1] / js.sum()
    comp_rank = []
    for eps in [0.1, 0.05, 0.02]:
        du_rms = int(np.argmax(np.append(left_kl[1:], 0.0) <= eps**2) + 1)
        rstar = int(np.argmax(np.append(left_opt[1:], 0.0) <= eps**2) + 1)
        comp_rank.append(dict(rms_tolerance=eps, input_kl_modes=du_rms, optimal_rank=rstar))
    return dict(rho=rho, tau_int=tau, delta=delta, window_T=T, d99_input_pca=d99, shell_width=shell,
                shell_profile_ranks=comp_rank, rows=rows), (M, lam, phi)


def rel(err, ref):
    return float(np.sqrt((err**2).sum() / (ref**2).sum()))


def check2(M, lam, phi, du, rho=0.02, x0=0.1):
    """Operator from the sea-level record to the heads at x >= x0 (outside the first part of the shell)."""
    tau = rho * TAU1
    js = X >= x0 - 1e-12
    Mo = M[js]
    gte = ou_paths(2000, tau)
    yte = gte @ Mo.T
    P = phi[:, :du]
    comp = (gte @ P) @ (P.T @ Mo.T)               # operator computed from du model runs, one per KL mode
    out = dict(x0=x0, du=du, computed_runs=du, computed_rel_error=rel(comp - yte, yte),
               computed_rms_error=float(np.sqrt(((comp - yte)**2).mean())), learned=[])
    for N in [du, 2 * du, 5 * du, 10 * du, 30 * du, 100 * du]:
        errs, rms = [], []
        for rep in range(3):
            g = ou_paths(N, tau)
            B, *_ = np.linalg.lstsq(g @ P, g @ Mo.T, rcond=None)   # PCA-Net with a linear map, least squares
            pred = (gte @ P) @ B
            errs.append(rel(pred - yte, yte)); rms.append(np.sqrt(((pred - yte)**2).mean()))
        pred = out['computed_rms_error'] * np.sqrt(1 + du / (N - du - 1)) if N > du + 1 else float('nan')
        out['learned'].append(dict(N=int(N), rel_error=float(np.mean(errs)), rms_error=float(np.mean(rms)),
                                   proposition_b_rms=float(pred)))
    return out


def rain(n, tau=0.03, m=-0.3, s=1.0):
    return np.maximum(0.0, m + s * ou_paths(n, tau))


def features(z, W, c):
    return np.maximum(0.0, z @ W + c)


def check3(du=30, width=1500, ic=0.8):
    K = operator(np.full(NX, DT))                  # uniform recharge source
    qtr_all = rain(20000)
    mu = qtr_all.mean(axis=0)
    Cq = (qtr_all - mu).T @ (qtr_all - mu) / qtr_all.shape[0]
    _, Vq = kl(Cq)
    P = Vq[:, :du]
    qte = rain(2000)
    zte = (qte - mu) @ P
    maps = {'linear (no cap)': lambda q: q @ K.T, 'capped recharge': lambda q: np.minimum(q, ic) @ K.T}
    W = RNG.standard_normal((du, width)) / np.sqrt(du) * 1.5
    c = RNG.uniform(-1, 1, width)
    res = {}
    for name, f in maps.items():
        yte = f(qte)
        rows = []
        for N in [100, 300, 1000, 3000, 10000, 20000]:
            idx = RNG.choice(qtr_all.shape[0], N, replace=False)
            q = qtr_all[idx]; y = f(q); z = (q - mu) @ P
            Bl, *_ = np.linalg.lstsq(np.c_[z, np.ones(N)], y, rcond=None)
            e_lin = rel(np.c_[zte, np.ones(len(zte))] @ Bl - yte, yte)
            F = features(z, W, c); Fte = features(zte, W, c)
            lamr = 1e-6 * np.trace(F.T @ F) / F.shape[1]
            Br = np.linalg.solve(F.T @ F + lamr * np.eye(width), F.T @ (y - y.mean(0)))
            e_rf = rel(Fte @ Br + y.mean(0) - yte, yte)
            rows.append(dict(N=N, linear_pca_net=e_lin, relu_pca_net=e_rf))
        res[name] = rows
    exact = rel(np.minimum(qte, ic) @ K.T - maps['capped recharge'](qte), maps['capped recharge'](qte))
    frac_capped = float((qte > ic).mean())
    return dict(du=du, width=width, cap=ic, fraction_of_time_capped=frac_capped, kink_on_input_rel_error=exact,
                results=res)


def check4(M, lam, phi, rho=0.02, xg=0.1, delta=0.25, band=10):
    """Certified guard at a well x: |e_x| <= sum_b gamma_b ||P_b g||, gamma_b = ||M_x P_b|| over bands of discarded
    KL modes (gamma from one adjoint run per guarded well), and the sharp alarm 2.576 * sd_hat > delta with
    sd_hat^2 = sum_b gamma_b^2 ||P_b g||^2 / n_b. du is chosen so that the in-distribution 99th percentile of |e_x| is
    at most 0.8 delta."""
    tau = rho * TAU1
    j = int(round(xg / DX)) - 1
    Mx = M[j]
    w = (Mx @ phi)**2 * lam
    tail = np.cumsum(w[::-1])[::-1]
    du = int(np.argmax(np.append(tail[1:], 0.0) <= (0.8 * delta / 2.576)**2) + 1)
    P = phi[:, :du]
    edges = list(range(du, NT, band)) + [NT]
    bands = [phi[:, a_:b_] for a_, b_ in zip(edges[:-1], edges[1:])]
    gam = np.array([np.linalg.norm(Mx @ Pb) for Pb in bands])
    gamma_single = float(np.linalg.norm(Mx - (Mx @ P) @ P.T))
    cases = {'in distribution': (tau, 1.0), 'amplitude x2 (C\'=4C)': (tau, 2.0),
             'memory x0.2 (rougher)': (0.2 * tau, 1.0), 'memory x5 (smoother)': (5 * tau, 1.0)}
    rows = []
    for name, (tt, s_) in cases.items():
        g = ou_paths(4000, tt, s_)
        err = np.abs(g @ Mx - (g @ P) @ (P.T @ Mx))
        bnd = sum(gb * np.linalg.norm(g @ Pb, axis=1) for gb, Pb in zip(gam, bands))
        sd_hat = np.sqrt(sum(gb**2 * (np.linalg.norm(g @ Pb, axis=1)**2) / Pb.shape[1] for gb, Pb in zip(gam, bands)))
        single = gamma_single * np.linalg.norm(g - (g @ P) @ P.T, axis=1)
        rows.append(dict(case=name, rms_error=float(np.sqrt((err**2).mean())), p99_error=float(np.quantile(err, 0.99)),
                         exceed=float((err > delta).mean()), median_bound=float(np.median(bnd)),
                         median_ratio=float(np.median(bnd / np.maximum(err, 1e-12))),
                         median_single_bound=float(np.median(single)),
                         bound_holds=float((err <= bnd + 1e-12).mean()), certificate_below_delta=float((bnd <= delta).mean()),
                         median_sd_estimate=float(np.median(sd_hat)), alarm=float((2.576 * sd_hat > delta).mean())))
    return dict(x=xg, du=du, band=band, delta=delta, rows=rows)


def site():
    """Proposition A with the illustrative Fushe Kuqe-Mat parameters of the companion document (Table 3): coast-normal
    length 5 km, T = 500 m2/day, Sy = 0.1 or S = 1e-4, sea-level residual s = 0.2 m with tau_int = 1 day, window
    90 days, tolerance 5 cm."""
    out = []
    for layer, Dl, xs in [('phreatic', 500 / 0.1, [25, 50, 100, 200]), ('confined', 500 / 1e-4, [250, 1000, 2500, 5000])]:
        for xv in xs:
            a = xv * np.sqrt(2 / Dl)
            f = lambda Om: 16 * (2 * 0.2**2 * 1.0 / (1 + Om**2)) / np.pi * np.exp(-a * np.sqrt(Om)) * (np.sqrt(Om) / a + 1 / a**2)
            lo = Dl * np.log(4)**2 / (2 * 5000.0**2); hi = 1e6
            if f(lo) <= 0.05**2:
                Om = lo
            else:
                for _ in range(200):
                    mid = np.sqrt(lo * hi)
                    lo, hi = (mid, hi) if f(mid) > 0.05**2 else (lo, mid)
                Om = hi
            out.append(dict(layer=layer, x_m=xv, omega_per_day=float(Om), period_hours=float(2 * np.pi / Om * 24),
                            modes_90_days=float(90 * Om / np.pi)))
    return out


def main(out):
    c1, (M, lam, phi) = check1()
    du0 = next(r['modes_needed'] for r in c1['rows'] if abs(r['x'] - 0.1) < 1e-9)
    c2 = check2(M, lam, phi, du0)
    c3 = check3()
    c4 = check4(M, lam, phi)
    res = dict(setup=dict(L=L, D=D, tau1=TAU1, nx=NX, T=T, nt=NT, dt=DT), check1=c1, check2=c2, check3=c3, check4=c4,
               site=site())
    with open(out, 'w') as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'operatori_results.json')
