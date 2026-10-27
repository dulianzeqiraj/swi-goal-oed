"""MONTIMI-GO test bed: grids, history, candidate wells, parameter draws and the safe-rate search shared by the stages.

Scenario. A vertical section 4 km long and 60 m thick (top 10 m below sea level), the pre-development equilibrium,
then 50 years of pumping 4 m2/d per metre of coast from a well field 1.5 km from the coast (its screen is salinised
at the end, as at the coastal wells of the field site), then a 30-year decision horizon. The decision: where to put
the new supply well (2.0, 2.5, 3.0 or 3.5 km), where to put one recharge well injecting 1 m2/d of fresh water
(none, 0.5, 1.0, 1.5 = the old well field, 2.0, 2.5 or 3.0 km), and how much to pump, such that the probability that
the supply screen exceeds 250 mg/L of chloride at the end of the horizon is at most alpha = 10 %."""
import numpy as np
import mg_model as M

DT_YR, HIST_YR, FORE_YR = 0.5, 50.0, 30.0
NH, NF = int(HIST_YR / DT_YR), int(FORE_YR / DT_YR)
T0 = HIST_YR * M.YR
ALPHA = 0.10
QR = 1.0
Q_HIST = 4.0
Q_MAX = 12.0

GF = M.uniform_grid(120, 20)                 # the full assembly's grid (33 m x 3 m)
GU = M.uniform_grid(40, 20)                  # uniform coarse grid (100 m x 3 m)


def snap(x, g=GF):
    return float(g.xc[g.column(x)])


X_HIST = snap(1500.0)
XS = [snap(x) for x in (2000.0, 2500.0, 3000.0, 3500.0)]
XR = [None] + [snap(x) for x in (500.0, 1000.0, 1500.0, 2000.0, 2500.0, 3000.0)]
LAYOUTS = [dict(xs=xs, xr=xr) for xs in XS for xr in XR if xr is None or abs(xr - xs) > 1.0]
HIST = dict(xs=X_HIST, Q=Q_HIST)


def lay_name(L):
    return f"S{L['xs'] / 1000:.1f}" + ('' if L['xr'] is None else f"-R{L['xr'] / 1000:.1f}")


def forecast_layout(L, Q):
    d = dict(xs=L['xs'], Q=Q)
    if L['xr'] is not None:
        d.update(xr=L['xr'], qr=QR)
    return d


def draws(n, seed):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        xi = rng.standard_normal(4)
        aL = 20.0 * np.exp(0.4 * xi[2])
        out.append(dict(K=100.0 * np.exp(0.25 * xi[0]), q_in=4.0 * np.exp(0.2 * xi[1]), aL=aL, aT=aL / 10.0,
                        b_c=(0.3, float(rng.uniform(0.3, 0.9))), eta_rate=float(max(0.0, 4.0 + 2.0 * xi[3]))))
    return out


DES = draws(40, 2026)[:25]        # design draws: the assemblies choose on these
EVA = draws(40, 4052)[:25]        # evaluation draws: the full assembly judges the choices on these
MED = dict(K=100.0, q_in=4.0, aL=20.0, aT=2.0, b_c=(0.3, 0.6), eta_rate=4.0)


ASSEMBLIES = {
    'F': dict(grid='F', opts={}),                                                        # full assembly
    'G': dict(grid='G', opts=dict(memory_h=(False, False), slr=False)),                  # goal-guided
    'U': dict(grid='U', opts=dict(memory_h=(False, False), slr=False)),                  # same terms, uniform mesh
    'S': dict(grid='G', opts=dict(memory_h=(False, False), slr=False, coupling='split')),  # goal mesh, lagged coupling
    'N': dict(grid='G', opts=dict(memory_h=(False, False), slr=False, immobile=(False, False))),  # goal mesh, no immobile zones
}


def present_state(g, P, opts):
    """pre-development equilibrium and 50 years of history with the old well field."""
    m = M.Model(g, P=P, opts=opts, dt_yr=DT_YR)
    y0 = m.steady()
    m.run(y0=y0, schedule=[(NH, HIST)], keep=False, toe=True)
    return y0, m.y_end, m.z_end, m.toe_x


def forecast(g, P, opts, y, z, L, Q, keep=False, toe=False):
    m = M.Model(g, P=P, opts=opts, dt_yr=DT_YR)
    J = m.run(y0=y, z0=z, schedule=[(NF, forecast_layout(L, Q))], t0=T0, keep=keep, toe=toe)
    return J, m


def q_crit(fJ, thr=M.EPS_LIM, guess=5.0, tol=0.01, maxev=12):
    """largest rate Q in [0, Q_MAX] with J(Q) <= thr (J increasing in Q): bracketed secant on log J."""
    ev = {}

    def f(Q):
        if Q not in ev:
            ev[Q] = fJ(Q)
        return ev[Q]
    lo, hi = 0.0, Q_MAX
    if f(0.0) > thr:
        return 0.0, len(ev)
    q1 = min(max(guess, 0.2), Q_MAX - 0.2)
    j1 = f(q1)
    if j1 <= thr:
        lo = q1; q2 = min(q1 * 1.25 + 0.3, Q_MAX)
    else:
        hi = q1; q2 = max(q1 * 0.8 - 0.3, 0.05)
    j2 = f(q2)
    if j2 <= thr: lo = max(lo, q2)
    else: hi = min(hi, q2)
    if lo == Q_MAX or (q2 == Q_MAX and j2 <= thr):
        return Q_MAX, len(ev)
    pts = [(q1, j1), (q2, j2)]
    while hi - lo > tol and len(ev) < maxev:
        (qa, ja), (qb, jb) = pts[-2], pts[-1]
        la, lb, lt = np.log(max(ja, 1e-30)), np.log(max(jb, 1e-30)), np.log(thr)
        q = qb + (lt - lb) * (qb - qa) / (lb - la) if abs(lb - la) > 1e-12 else 0.5 * (lo + hi)
        if not (lo < q < hi) or not np.isfinite(q):
            q = 0.5 * (lo + hi)
        jq = f(q)
        if jq <= thr: lo = q
        else: hi = q
        pts.append((q, jq))
        if abs(np.log(max(jq, 1e-30)) - lt) < 2e-3:
            return q, len(ev)
    return lo, len(ev)
