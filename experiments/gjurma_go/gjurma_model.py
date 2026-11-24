"""GJURMA-GO: multi-species transport with a stoichiometric learned closure and memory for a coastal aquifer.

A 1D flow line from the coast (x = 0) to the recharge zone (x = L) with the abstraction field at X_P. Seven species
(mmol/L): Cl, Na, K, Ca, Mg, SO4, HCO3. The whole ensemble is simulated at once: every array has a leading ensemble
axis.

Processes of the TRUTH (and of the oracle model, whose structure is exact but whose parameters are unknown):
  advection (upwind, inflow form, valid with the sink at X_P) and dispersion (D = alpha_L |v| + D_m);
  mobile-immobile mass transfer with the silt-clay intercalations (rate a_mt, capacity ratio b_im): the memory term;
  sulfate reduction in the immobile (organic-rich silt-clay) zone, first order, SO4 -> 2 HCO3;
  cation exchange in the mobile zone in local equilibrium (Gaines-Thomas, Na reference, capacity E meq/L pore water).

Models fitted to data:
  'classical'  the single-salt model of the base paper extended to all species by conservative mixing;
  'free'       conservative transport + memory + a learned closure for EVERY species (no stoichiometry);
  'gjurma'     conservative transport + memory + a learned closure confined to the span of the stoichiometric matrix
               N (three exchange reactions, sulfate reduction, calcite), so Cl is closure-free;
  'oracle'     the truth's structure with unknown parameters.
Each learned exchange term is a learned exchanger with memory (a loading that relaxes toward a learned equilibrium with
the seawater fraction f from Cl); sulfate reduction is first order in c_SO4 in the clay zone, and calcite is
proportional to the total exchange (see closure()). A relic marine exchanger in the central band can be switched on
with F_RELIC > 0 (off in all reported runs).
"""
import numpy as np

SPECIES = ['Cl', 'Na', 'K', 'Ca', 'Mg', 'SO4', 'HCO3']
NS = len(SPECIES)
Z = np.array([-1, 1, 1, 2, 2, -2, -1], float)
MW = np.array([35.453, 22.990, 39.098, 40.078, 24.305, 96.06, 61.017])
FRESH_MGL = np.array([12.92, 17.75, 1.80, 32.74, 24.56, 58.56, 182.16])        # well 193 (sheet 5)
SEA_MGL = np.array([19353., 10781., 399., 412., 1284., 2712., 145.])            # standard seawater
FRESH = FRESH_MGL / MW
SEA = SEA_MGL / MW
I_CL, I_NA, I_K, I_CA, I_MG, I_SO4, I_HCO3 = range(7)

# stoichiometric matrix (mmol of species per unit of reaction), columns: Na-Ca, Na-Mg, K-Ca exchange (per meq),
# sulfate reduction (per mmol SO4), calcite dissolution (per mmol)
NSTO = np.zeros((NS, 5))
NSTO[I_NA, 0], NSTO[I_CA, 0] = -1.0, 0.5
NSTO[I_NA, 1], NSTO[I_MG, 1] = -1.0, 0.5
NSTO[I_K, 2], NSTO[I_CA, 2] = -1.0, 0.5
NSTO[I_SO4, 3], NSTO[I_HCO3, 3] = -1.0, 2.0
NSTO[I_CA, 4], NSTO[I_HCO3, 4] = 1.0, 2.0

# grid and time
L, NX = 15000.0, 75
DX = L / NX
XC = (np.arange(NX) + 0.5) * DX
X_P = 6000.0
I_P = int(X_P // DX)
WELLS = {'503': 1000.0, '341': 2000.0, '340': 4500.0, '193': 12000.0}     # assumed distances from the coast
I_W = {w: int(x // DX) for w, x in WELLS.items()}
T0, T1, DT = 1950.0, 2045.0, 0.25
TIMES = np.arange(T0, T1 + 1e-9, DT)
D_M = 0.03                                                   # m2/yr


def coastal_velocity(t):
    """Base history of the pore velocity in the coastal segment (m/yr, landward positive): natural seaward flow,
    heavy pumping, a pause with partial freshening, renewed pumping (status quo continues after 2025)."""
    return np.where(t < 1975, -15.0, np.where(t < 1990, 200.0, np.where(t < 2000, -40.0, 50.0)))


V_INLAND = -50.0                                             # toward the sink (seaward), m/yr
F0_RISE = 1.0                                                # factor by which the coastal salinity has grown by 2045


def boundary_factor(t):
    """Salinity of the water entering at the coast relative to f0: constant until 2000, then growing linearly
    (thickening of the wedge under the coastal sector) to F0_RISE times f0 in 2045."""
    return 1.0 + (np.asarray(F0_RISE) - 1.0) * np.clip((t - 2000.0) / 45.0, 0.0, 1.0)
SR_ZONE = (XC < X_P).astype(float)                           # organic-rich silt-clay cover near the coast
RELIC_ZONE = ((XC > 3500.0) & (XC < 7000.0)).astype(float)   # relic marine exchanger (central delta)
F_RELIC = 0.0                                                # seawater fraction of the relic pore water (0: off)
CLOSURE_CAP = 200.0                                          # bound on a learned source term (mmol/L/yr): stability guard
C_CAP = 2000.0                                               # bound on any concentration (mmol/L): stability guard

# Gaines-Thomas selectivities relative to Na (Appelo-Postma style): K_Na\K, K_Na\Ca, K_Na\Mg
K_TRUE = np.array([0.2, 0.4, 0.5])


def exchanger(c, logK):
    """Equivalent fractions (Na, K, Ca, Mg) in equilibrium with solution c (mmol/L); logK = log of (K_Na\\K,
    K_Na\\Ca, K_Na\\Mg), shape (..., 3) broadcastable."""
    na, k, ca, mg = (np.maximum(c[..., i], 1e-12) * 1e-3 for i in (I_NA, I_K, I_CA, I_MG))   # mol/L
    KK, KC, KM = (np.exp(logK[..., j]) for j in range(3))
    b = 1.0 + k / (KK * na)
    a = ca / (KC ** 2 * na ** 2) + mg / (KM ** 2 * na ** 2)
    bna = 2.0 / (b + np.sqrt(b * b + 4.0 * a))                      # root of a x^2 + b x - 1 = 0 (stable form)
    return np.stack([bna, bna * k / (KK * na), bna ** 2 * ca / (KC ** 2 * na ** 2), bna ** 2 * mg / (KM ** 2 * na ** 2)], -1)


ZC = np.array([1.0, 1.0, 2.0, 2.0])                          # charges of Na, K, Ca, Mg
IC = [I_NA, I_K, I_CA, I_MG]


def solve_cations(T, E, logK, y0, iters=6, tol=1e-10):
    """Find cation concentrations y (mmol/L, shape (..., 4)) with z y + E beta(y) = T."""
    ly = np.log(np.maximum(y0, 1e-9))
    for _ in range(iters):
        y = np.exp(ly)
        c = np.zeros(y.shape[:-1] + (NS,))
        c[..., IC] = y
        F = ZC * y + E[..., None] * exchanger(c, logK) - T
        if np.abs(F).max() < tol * (1.0 + np.abs(T).max()):
            break
        Jm = np.empty(y.shape + (4,))
        h = 1e-6
        for j in range(4):
            c2 = c.copy()
            c2[..., IC[j]] = y[..., j] * np.exp(h)
            Fj = ZC * c2[..., IC] + E[..., None] * exchanger(c2, logK) - T
            Jm[..., j] = (Fj - F) / h
        Jm = Jm + 1e-9 * np.eye(4)
        step = np.linalg.solve(Jm, -F[..., None])[..., 0]
        ly = ly + np.clip(step, -2.0, 2.0)
    return np.exp(ly)


def bc_sea(f0):
    return f0[..., None] * SEA + (1 - f0[..., None]) * FRESH


def simulate(P, model='truth', obs_times=None, keep=False):
    """Run the ensemble. P is a dict of arrays of shape (Ne,):
      s_v, alpha_L, f0 (all models); a_mt, b_im (memory, all but 'classical'); E, logK (3 cols), k_sr ('truth'/'oracle');
      theta (Ne, 11) for 'gjurma' or (Ne, 35) for 'free'.
    Returns {time: mobile concentrations (Ne, NX, NS)} at obs_times (and the full record if keep)."""
    ne = P['s_v'].shape[0]
    obs_times = [] if obs_times is None else list(obs_times)
    react = model in ('truth', 'oracle')
    memory = model != 'classical'
    c = np.broadcast_to(FRESH, (ne, NX, NS)).copy()
    cim = c.copy()
    if react:
        E = P['E']
        logK = P['logK'][:, None, :]
        # relic marine exchanger in the central band (Holocene marine sediments of the delta): the exchanger starts in
        # equilibrium with water of seawater fraction F_RELIC there, with fresh water in the pores
        cw = np.broadcast_to(FRESH, (ne, NX, NS)).copy()
        relic = RELIC_ZONE[None, :, None] * F_RELIC
        cw = relic * SEA + (1 - relic) * FRESH
        beta = exchanger(cw, logK)
        Tex = E[:, None, None] * beta                            # exchanger loading (meq/L) per cation
    out = {}
    f0 = P['f0']
    alpha = P['alpha_L'][:, None]
    if model == 'gjurma':
        qh = np.zeros((ne, NX, 3))                               # learned exchanger loadings (meq/L), one per reaction
    elif model == 'free':
        qh = np.zeros((ne, NX, NS))                              # learned loadings, one per species
    rec = [] if keep else None
    for n, t in enumerate(TIMES):
        vc = coastal_velocity(t) * P['s_v']
        cb = bc_sea(f0 * boundary_factor(t))
        # face velocities: faces j+1/2 for j = -1..NX-1 (NX+1 faces)
        xf = np.arange(NX + 1) * DX
        uf = np.where(xf[None, :] <= X_P, vc[:, None], V_INLAND)
        vcell = np.where(XC[None, :] < X_P, vc[:, None], V_INLAND)
        D = alpha * np.abs(vcell) + D_M
        # explicit transport with sub-steps that keep advection + dispersion stable
        cfl = (np.abs(vcell) * DT / DX + 2.0 * D * DT / DX ** 2).max()
        nsub = max(1, int(np.ceil(cfl / 0.8)))
        dts = DT / nsub
        Df = np.concatenate([D[:, :1], 0.5 * (D[:, 1:] + D[:, :-1]), D[:, -1:]], 1)
        right = np.broadcast_to(FRESH, (ne, NS))
        for _ in range(nsub):
            left = np.where((vc > 0)[:, None], cb, c[:, 0, :])
            cg = np.concatenate([left[:, None, :], c, right[:, None, :]], 1)
            upin = np.maximum(uf[:, :-1], 0)[..., None] * (cg[:, :-2] - c)          # inflow from the left
            dnin = np.maximum(-uf[:, 1:], 0)[..., None] * (cg[:, 2:] - c)           # inflow from the right
            flux = Df[..., None] * (cg[:, 1:] - cg[:, :-1]) / DX
            c = c + dts * ((upin + dnin) / DX + (flux[:, 1:] - flux[:, :-1]) / DX)
        if memory:
            a = P['a_mt'][:, None, None]; b = P['b_im'][:, None, None]
            ex = a * (c - cim) * DT
            cim = cim + ex
            c = c - b * ex
        if react:
            # sulfate reduction in the immobile zone
            r = P['k_sr'][:, None] * SR_ZONE[None, :] * cim[..., I_SO4] * DT
            cim[..., I_SO4] -= r
            cim[..., I_HCO3] += 2 * r
            # exchange equilibrium in the mobile zone: conserve z c + E beta per cation
            T = ZC * c[..., IC] + Tex
            y = solve_cations(T, np.broadcast_to(E[:, None], (ne, NX)), logK, c[..., IC])
            c[..., IC] = y
            Tex = T - ZC * y
        f = (c[..., I_CL] - FRESH[I_CL]) / (SEA[I_CL] - FRESH[I_CL])
        if model in ('gjurma', 'free'):
            src, qh = closure(P['theta'], f, c, qh, model)
            c = c + DT * np.clip(src, -CLOSURE_CAP, CLOSURE_CAP)
        c = np.clip(np.nan_to_num(c, nan=1e-6, posinf=C_CAP), 1e-6, C_CAP)
        for to in obs_times:
            if abs(t - to) < DT / 2:
                out[to] = c.copy()
        if keep:
            rec.append(c.copy())
    if keep:
        out['record'] = np.array(rec)
    return out


def closure(theta, f, c, qh, model):
    """Learned source term (mmol/L/yr), shape (Ne, NX, NS), and the updated hidden loadings.
    Each exchange-type term is a learned exchanger with memory: a loading q relaxes toward a learned equilibrium
    Q f/(f + h) with time scale tau, and its rate of change is the reaction rate (uptake while q rises). Uptake is
    limited by the availability of the consumed ion (its concentration over its conservative-mixing value).
      'gjurma': three exchange reactions (Na-Ca, Na-Mg, K-Ca: log Q, log h, log tau each), first-order sulfate
                reduction in the clay zone (log rate) and calcite (rate per unit change of the exchange); the source is
                N r, so Cl is untouched.
      'free':   one learned exchanger per species (log Q, log h, log tau, signed by a sign parameter s) and a
                first-order term b c in the clay zone, for every species including Cl."""
    mix = f[..., None] * SEA + (1 - f[..., None]) * FRESH
    avail = np.clip(c / np.maximum(mix, 1e-9), 0.0, 3.0)
    fp = np.maximum(f, 0.0)
    if model == 'gjurma':
        th = theta[:, None, :]
        Q = np.exp(th[..., [0, 3, 6]]); h = np.exp(th[..., [1, 4, 7]]); tau = np.exp(th[..., [2, 5, 8]])
        qeq = Q * fp[..., None] / (fp[..., None] + h)
        rate = (qeq - qh) / tau                                   # meq/L/yr, positive = uptake of Na (or K)
        ion = np.stack([avail[..., I_NA], avail[..., I_NA], avail[..., I_K]], -1)
        rate = np.where(rate > 0, rate * np.minimum(ion, 1.0), rate)
        qh = qh + DT * rate
        r = np.concatenate([rate, (np.exp(th[..., 9]) * c[..., I_SO4] * SR_ZONE[None, :])[..., None],
                            (th[..., 10] * rate.sum(-1))[..., None]], -1)       # (Ne, NX, 5)
        return r @ NSTO.T, qh
    th = theta.reshape(theta.shape[0], 1, NS, 5)
    Q = np.exp(th[..., 0]); h = np.exp(th[..., 1]); tau = np.exp(th[..., 2]); sgn = np.tanh(th[..., 3])
    qeq = Q * fp[..., None] / (fp[..., None] + h)
    rate = (qeq - qh) / tau
    rate = np.where(rate > 0, rate * np.minimum(avail, 1.0), rate)
    qh = qh + DT * rate
    return -sgn * rate + th[..., 4] * c * SR_ZONE[None, :, None], qh
