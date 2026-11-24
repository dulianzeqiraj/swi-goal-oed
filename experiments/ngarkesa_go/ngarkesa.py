"""NGARKESA-GO forward model: electroneutral multicomponent ion transport in a coastal aquitard.

Seven major ions diffuse through a clay aquitard under the aquifer of a coastal well field:
    Na+, K+, Ca2+, Mg2+ (exchangeable cations), Cl-, SO4^2-, HCO3- (anions).
Transport is the zero-current Nernst-Planck model, the dilute and ideal limit of Onsager-Stefan-Maxwell transport
written in a salt-charge basis (Van-Brunt, Farrell & Monroe): the electric field is not a separate unknown but is
eliminated through the zero-current condition, so every face flux carries no charge and electroneutrality holds by
construction (to rounding). Cations exchange on the clay by Gaines-Thomas equilibrium with Davies activity
coefficients (PHREEQC exchange constants).

Units: concentrations in mol/m3 (= mmol/L) of porewater, lengths in m, time in years.
The model is batched: every array has a leading axis over parameter sets (formation factor F, CEC).
"""
import numpy as np

SP = ['Na', 'K', 'Ca', 'Mg', 'Cl', 'SO4', 'HCO3']
Z = np.array([1., 1., 2., 2., -1., -2., -1.])
NCAT = 4                                                   # the first four species are exchangeable cations
# tracer diffusion coefficients in free water at 25 C, 1e-9 m2/s (Li & Gregory, 1974)
D25 = np.array([1.334, 1.957, 0.792, 0.706, 2.032, 1.065, 1.185])
TFAC = (289.15 / 298.15) * (0.890 / 1.109)               # Stokes-Einstein correction to 16 C
YEAR = 3.15576e7
D0 = D25 * 1e-9 * TFAC * YEAR                              # m2/yr
LOGK = np.array([0.0, 0.7, 0.8, 0.6])                      # Gaines-Thomas: NaX, KX, CaX2, MgX2 (phreeqc.dat)
KEX = 10.0 ** LOGK
MW = {'Na': 22.99, 'Cl': 35.45}

# end members, mmol/L (standard seawater after Appelo & Postma; a Ca-HCO3 fresh groundwater)
SEA = np.array([484.8, 10.6, 10.7, 55.1, 566.0, 29.3, 2.4])
FRESH = np.array([1.0, 0.1, 2.0, 0.5, 1.0, 0.3, 4.5])
PHI, RHOB = 0.40, 1600.0                                   # porosity, bulk density (kg/m3)


def charge(c):
    return np.tensordot(Z, c, axes=([0], -2)) if c.ndim > 1 else Z @ c


def davies_gamma(c):
    """activity coefficients of the four cations from the ionic strength of the porewater (c: [..., 7, M])."""
    I = 0.5 * np.einsum('s,...sm->...m', Z ** 2, c) / 1000.0
    sI = np.sqrt(I)
    lg = -0.509 * (Z[:NCAT, None] ** 2) * (sI / (1 + sI) - 0.3 * I)[..., None, :]
    return 10.0 ** lg


def exchange_split(T, cecb, gam, a0):
    """Given total cation amounts T (mol/m3 bulk, [P, 4, M]), exchange capacity cecb (eq/m3 bulk, [P, 1, 1]) and
    activity coefficients gam ([P, 4, M]), return porewater concentrations c ([P, 4, M]), equivalent fractions and the
    exchanger variable a (the 'free site' activity of the Gaines-Thomas convention), by Newton iteration in log a."""
    z = Z[:NCAT, None]
    K = KEX[:, None] * gam / 1000.0                       # beta_s = K_s gamma_s (c_s / 1000) a^z
    la = np.log(a0)
    for _ in range(30):
        a = np.exp(la)
        az = a[:, None, :] ** z
        u = cecb * K * az / z                              # sorbed / dissolved ratio per unit c (bulk basis)
        c = T / (PHI + u)
        beta = K * c * az
        f = beta.sum(axis=1) - 1.0
        # d beta / d log a = z beta * PHI / (PHI + u)
        df = (z * beta * PHI / (PHI + u)).sum(axis=1)
        step = np.clip(f / df, -2.0, 2.0)
        la = la - step
        if np.max(np.abs(step)) < 1e-12:
            break
    a = np.exp(la)
    az = a[:, None, :] ** z
    u = cecb * K * az / z
    c = T / (PHI + u)
    return c, K * c * az, a


def equilibrate(cw, cecb):
    """exchanger in equilibrium with a given porewater cw ([P, 7, M]): returns total cation amounts and a."""
    gam = davies_gamma(cw)
    z = Z[:NCAT, None]
    K = KEX[:, None] * gam / 1000.0
    # solve sum_s K_s c_s a^z_s = 1 for a (c fixed)
    la = np.zeros(cw.shape[:1] + cw.shape[2:])
    for _ in range(60):
        a = np.exp(la)
        b = K * cw[:, :NCAT] * a[:, None, :] ** z
        f = b.sum(axis=1) - 1.0
        df = (z * b).sum(axis=1)
        step = np.clip(f / df, -2.0, 2.0)
        la -= step
        if np.max(np.abs(step)) < 1e-13:
            break
    a = np.exp(la)
    beta = K * cw[:, :NCAT] * a[:, None, :] ** z
    T = PHI * cw[:, :NCAT] + cecb * beta / z
    return T, a


def face_fluxes(c, cb, F, h):
    """zero-current Nernst-Planck fluxes (mol/m2/yr, positive downward) at the faces of the grid.
    c: [P, 7, M]; cb: boundary porewater at the top [7]; F: formation factor [P]. Face 0 is the aquifer contact
    (boundary value at distance h/2); the bottom face is closed."""
    P, S, M = c.shape
    De = D0[None, :, None] / F[:, None, None]                         # effective (bulk) coefficients
    cl = np.concatenate([np.broadcast_to(cb[None, :, None], (P, S, 1)), c], axis=2)   # [P, S, M+1]
    dx = np.full(M, h); dx[0] = h / 2
    g = (cl[:, :, 1:] - cl[:, :, :-1]) / dx                          # gradients at faces 0..M-1
    cf = 0.5 * (cl[:, :, 1:] + cl[:, :, :-1])
    num = np.einsum('s,psm->pm', Z, De * g)
    den = np.einsum('s,psm->pm', Z ** 2, De * cf)
    dpsi = -num / den                                                   # zero current: sum_s z_s J_s = 0
    J = -De * (g + Z[None, :, None] * cf * dpsi[:, None, :])
    return np.concatenate([J, np.zeros((P, S, 1))], axis=2)          # closed bottom


def simulate(F, cec, L=3.0, M=60, t1=40.0, t2=60.0, f_sea=0.25, sample_depths=(), mode='np', record_every=0.25):
    """Run the two phases for a batch of parameter sets.
    Phase 1 (t1 years): the aquifer carries a seawater-freshwater mixture (fraction f_sea) and salt enters the
    aquitard. Phase 2 (t2 years): the aquifer is freshened and salt leaves the aquitard (back-diffusion).
    mode: 'np'      zero-current Nernst-Planck with exchange (the reference model);
          'fick_i'  every ion with its own coefficient and no electrical coupling (charge is not conserved);
          'fick_1'  every ion with the chloride coefficient (electroneutral, but salt moves at the chloride rate).
    Returns the porewater profiles at the end of phase 1, the fluxes into the aquifer during phase 2 and the
    largest charge imbalance."""
    F = np.atleast_1d(np.asarray(F, float)); cec = np.atleast_1d(np.asarray(cec, float))
    P = F.size
    h = L / M
    xc = (np.arange(M) + 0.5) * h
    cecb = (cec * 0.01 * RHOB)[:, None, None]                       # meq/100 g -> eq/m3 bulk
    mix = f_sea * SEA + (1 - f_sea) * FRESH
    c = np.broadcast_to(FRESH[None, :, None], (P, 7, M)).copy()
    T, a = equilibrate(c, cecb)
    Dm = D0.copy()
    if mode == 'fick_1':
        Dm = np.full(7, D0[4])
    Dmax = Dm.max() * 1.0
    dt = 0.2 * (h / 2) ** 2 * PHI * F.min() / Dmax
    out = {'x': xc}
    rec_t, rec_J = [], []
    t, tend = 0.0, t1 + t2
    next_rec = t1 + record_every
    qimb = 0.0
    while t < tend - 1e-12:
        step = min(dt, tend - t, (t1 - t) if t < t1 - 1e-12 else np.inf)
        cb = mix if t < t1 - 1e-12 else FRESH
        if mode == 'np':
            J = face_fluxes(c, cb, F, h)
        else:
            De = Dm[None, :, None] / F[:, None, None]
            cl = np.concatenate([np.broadcast_to(cb[None, :, None], (P, 7, 1)), c], axis=2)
            dx = np.full(M, h); dx[0] = h / 2
            J = np.concatenate([-De * (cl[:, :, 1:] - cl[:, :, :-1]) / dx, np.zeros((P, 7, 1))], axis=2)
        div = (J[:, :, 1:] - J[:, :, :-1]) / h
        # cations: totals with exchange; anions: porewater only
        T = T - step * div[:, :NCAT]
        canion = c[:, NCAT:] - step * div[:, NCAT:] / PHI
        gam = davies_gamma(c)
        ccat, beta, a = exchange_split(T, cecb, gam, a)
        c = np.concatenate([ccat, canion], axis=1)
        t += step
        qimb = max(qimb, float(np.max(np.abs(charge(c)))))
        if abs(t - t1) < 1e-9:
            out['c1'] = c.copy()
            out['beta1'] = beta.copy()
        if t >= next_rec - 1e-9 and t > t1 + 1e-9:
            rec_t.append(t - t1)
            rec_J.append(-J[:, :, 0].copy())                         # flux into the aquifer (upward), mol/m2/yr
            next_rec += record_every
    out['t2'] = np.array(rec_t)
    out['Jup'] = np.stack(rec_J, axis=0)                              # [nt, P, 7]
    out['charge_max'] = qimb
    out['c_end'] = c
    if len(sample_depths):
        idx = np.clip(np.searchsorted(xc, sample_depths), 0, M - 1)
        out['samples'] = out['c1'][:, :, idx]
    return out
