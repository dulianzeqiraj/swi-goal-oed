"""RITMI-GO model: the transient augmented system on the coastal flow line, with two-rate memory and a pumping
modulation during an identification experiment (review 43).

It reuses the GJURMA-GO flow line (../gjurma_go/gjurma_model.py): grid, wells, seven species (mmol/L), Gaines-Thomas
exchanger, end-members and the pumping history of the coastal segment. Differences:
  * memory with TWO immobile zones, silt (fast rate a1, capacity ratio b1) and clay (slow rate a2, capacity ratio b2),
    each mobile-immobile pair updated exactly over a step, so the kernel acting on dc/dt is completely monotone,
        kappa(s) = b1 a1 exp(-a1 s) + b2 a2 exp(-a2 s),   kappa_hat(lambda) = sum_k b_k a_k / (a_k + lambda);
  * sulfate reduction (first order, rate k_sr) only inside the clay zone of the coastal strip: an irreversible
    reaction inside an immobile zone (the reactive exception of Proposition R1);
  * cation exchange in local equilibrium in the mobile water (as in GJURMA-GO);
  * quarterly steps until 2000, monthly steps 2000-2045, and a pumping modulation delta(t) (m/yr of coastal
    velocity, scaled by s_v like the history) during the identification experiment 2026-2031. Designs: 'const',
    'sine' (period P), 'doublet' (+A for P/2, -A for P/2, repeated) and 'prbs' (balanced random +-A, slots of P)
    have zero mean, so the water supplied over the experiment is unchanged; 'block' changes the pumping by A for the
    first P years (a pause when A < 0, a surge when A > 0);
  * a steady mode: the same equations with constant forcing, run to equilibrium.
Every array has a leading ensemble axis.
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'gjurma_go'))
import gjurma_model as G                                      # noqa: E402

SPECIES, NS, MW, FRESH, SEA = G.SPECIES, G.NS, G.MW, G.FRESH, G.SEA
I_CL, I_NA, I_K, I_CA, I_MG, I_SO4, I_HCO3 = range(7)
NX, DX, XC, X_P = G.NX, G.DX, G.XC, G.X_P
W_NAMES = list(G.WELLS)                                      # 503, 341, 340, 193
I_WELLS = [G.I_W[w] for w in W_NAMES]
IC, ZC = G.IC, G.ZC
SR_ZONE = G.SR_ZONE
EXP0, EXP1, T_END = 2026.0, 2031.0, 2045.0
I5, I3 = int(5000 // DX), int(3000 // DX)
V_SQ = 50.0                                                  # status-quo coastal velocity after 2000 (m/yr)
TIMES = np.round(np.concatenate([1950.0 + 0.25 * np.arange(200), 2000.0 + np.arange(45 * 12 + 1) / 12.0]), 6)


def modulation(design, t):
    """Pumping modulation of the coastal velocity (m/yr, before the factor s_v); zero outside the experiment."""
    t = np.asarray(t, float)
    kind, A, P = design.get('kind', 'const'), float(design.get('A', 0.0)), float(design.get('P', 1.0))
    tau = t - EXP0
    on = (tau >= 0) & (t < EXP1)
    if kind == 'const' or A == 0.0:
        s = np.zeros_like(t)
    elif kind == 'sine':
        s = np.sin(2 * np.pi * tau / P)
    elif kind == 'doublet':
        s = np.where(np.mod(tau, P) < P / 2, 1.0, -1.0)
    elif kind == 'block':                                    # a pause (A < 0) or a surge (A > 0) of length P
        s = np.where(tau < P, 1.0, 0.0)
    elif kind == 'prbs':
        nsl = int(round((EXP1 - EXP0) / P))
        bits = np.array([1.0, -1.0] * (nsl // 2) + [0.0] * (nsl % 2))
        np.random.default_rng(design.get('seed', 3)).shuffle(bits)
        s = bits[np.clip(np.floor(tau / P).astype(int), 0, nsl - 1)]
    else:
        raise ValueError(kind)
    return np.where(on, A * s, 0.0)


def _pair(c, ci, a, b, dt):
    """Exact update of a mobile-immobile pair over dt (transport frozen): c + b ci is conserved and the difference
    relaxes with rate a (1 + b)."""
    M = c + b * ci
    d = (c - ci) * np.exp(-a * (1.0 + b) * dt)
    return (M + b * d) / (1.0 + b), (M - d) / (1.0 + b)


def simulate(P, design=None, snaps=(2016.0, 2045.0), steady=None):
    """P: dict of arrays (Ne,): s_v, alpha_L, f0, a1, b1, a2, b2, E, logK (Ne, 3), k_sr.
    steady: None (history 1950-2045 with the design) or dict(v=coastal velocity, years, dt) for constant forcing.
    Returns dict(times, wells (Nt, Ne, 4, NS), cl5 (Nt, Ne), snapshots {t: field (Ne, NX, NS)}, final field)."""
    design = design or {'kind': 'const'}
    ne = P['s_v'].shape[0]
    c = np.broadcast_to(FRESH, (ne, NX, NS)).copy()
    cim1, cim2 = c.copy(), c.copy()
    E = P['E']
    logK = P['logK'][:, None, :]
    Tex = E[:, None, None] * G.exchanger(c, logK)
    alpha = P['alpha_L'][:, None]
    a1, b1 = P['a1'][:, None, None], P['b1'][:, None, None]
    a2, b2 = P['a2'][:, None, None], P['b2'][:, None, None]
    ksr = P['k_sr'][:, None] * SR_ZONE[None, :]
    cb = G.bc_sea(P['f0'])
    times = TIMES if steady is None else np.arange(0.0, steady['years'] + 1e-9, steady['dt'])
    nt = times.size
    wells = np.empty((nt, ne, len(I_WELLS), NS))
    cl5 = np.empty((nt, ne))
    wells[0], cl5[0] = c[:, I_WELLS], c[:, I5, I_CL]
    out = {'times': times}
    xf = np.arange(NX + 1) * DX
    right = np.broadcast_to(FRESH, (ne, NS))
    for n in range(nt - 1):
        t, dt = times[n], times[n + 1] - times[n]
        if steady is None:
            v0 = G.coastal_velocity(t + 0.5 * dt) + modulation(design, t + 0.5 * dt)
        else:
            v0 = steady['v']
        vc = v0 * P['s_v']
        uf = np.where(xf[None, :] <= X_P, vc[:, None], G.V_INLAND)
        vcell = np.where(XC[None, :] < X_P, vc[:, None], G.V_INLAND)
        D = alpha * np.abs(vcell) + G.D_M
        cfl = (np.abs(vcell) * dt / DX + 2.0 * D * dt / DX ** 2).max()
        nsub = max(1, int(np.ceil(cfl / 0.8)))
        dts = dt / nsub
        Df = np.concatenate([D[:, :1], 0.5 * (D[:, 1:] + D[:, :-1]), D[:, -1:]], 1)
        for _ in range(nsub):
            left = np.where((vc > 0)[:, None], cb, c[:, 0, :])
            cg = np.concatenate([left[:, None, :], c, right[:, None, :]], 1)
            upin = np.maximum(uf[:, :-1], 0)[..., None] * (cg[:, :-2] - c)
            dnin = np.maximum(-uf[:, 1:], 0)[..., None] * (cg[:, 2:] - c)
            flux = Df[..., None] * (cg[:, 1:] - cg[:, :-1]) / DX
            c = c + dts * ((upin + dnin) / DX + (flux[:, 1:] - flux[:, :-1]) / DX)
        c, cim1 = _pair(c, cim1, a1, b1, dt)                  # silt: fast memory
        c, cim2 = _pair(c, cim2, a2, b2, dt)                  # clay: slow memory
        red = cim2[..., I_SO4] * (1.0 - np.exp(-ksr * dt))   # sulfate reduction inside the clay
        cim2[..., I_SO4] -= red
        cim2[..., I_HCO3] += 2.0 * red
        T = ZC * c[..., IC] + Tex                             # exchange equilibrium in the mobile water
        y = G.solve_cations(T, np.broadcast_to(E[:, None], (ne, NX)), logK, c[..., IC])
        c[..., IC] = y
        Tex = T - ZC * y
        c = np.clip(np.nan_to_num(c, nan=1e-6, posinf=G.C_CAP), 1e-6, G.C_CAP)
        wells[n + 1], cl5[n + 1] = c[:, I_WELLS], c[:, I5, I_CL]
        for s in snaps:
            if abs(times[n + 1] - s) < 1e-6:
                out[s] = c.copy()
    out.update(wells=wells, cl5=cl5, final=c)
    return out


def tindex(times, t):
    return int(np.argmin(np.abs(times - t)))
