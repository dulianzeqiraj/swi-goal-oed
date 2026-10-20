"""TRETJA-GO forward model: non-equilibrium, nonlinear calcite dissolution in the freshwater-seawater mixing zone.

Chemistry. Fresh groundwater and intruded seawater are each in equilibrium with calcite, at different CO2 pressures
(log pCO2 = -2.0 and -2.5) and ionic strengths. Their mixtures are undersaturated (mixing corrosion), a nonlinear
effect of the speciation, computed with PHREEQC (phreeqc.dat database, 15 C) through phreeqpython. A mixture of
seawater fraction f that has dissolved an extra amount dCa of calcite has the saturation ratio Omega(f, dCa),
tabulated once on a grid.

Transport. Transverse mixing between a fresh layer and a saline layer flowing in parallel (the mixing zone below a
coastal aquifer): v dc/dx = D_T d2c/dz2 + r, marched in x like time. f is conservative; dCa reacts.

Kinetics. Dissolution only (the mixtures are undersaturated), with a nonlinear rate law that changes mechanism at a
critical saturation (a kink): r = kappa g(Omega),
    g = (1 - Omega)^n1                                      for Omega >= Omega_c   (near equilibrium)
    g = (1 - Omega_c)^n1 ((1 - Omega)/(1 - Omega_c))^n2     for Omega <  Omega_c   (far from equilibrium)
The local-equilibrium model (LEA) is the limit kappa -> infinity: dCa = dCa_sat(f) everywhere.
The model is batched over parameter sets (leading axis).
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, 'tretja_table.npz')
LOGPCO2_FRESH, LOGPCO2_SEA, TEMP = -2.0, -2.5, 15.0


def build_table(nf=101, nd=81, dmax=0.20):
    """Omega(f, dCa) and dCa_sat(f) with PHREEQC (requires phreeqpython)."""
    from phreeqpython import PhreeqPython
    pp = PhreeqPython(database='phreeqc.dat')
    fresh = pp.add_solution({'temp': TEMP, 'units': 'mmol/kgw', 'Na': 1.0, 'Cl': 1.0, 'Mg': 0.5, 'S(6)': 0.5})
    fresh.equalize(['Calcite', 'CO2(g)'], [0.0, LOGPCO2_FRESH])
    sea = pp.add_solution({'temp': TEMP, 'units': 'ppm', 'pH': 8.22, 'Ca': 412.3, 'Mg': 1291.8, 'Na': 10768.0,
                           'K': 399.1, 'Cl': 19353.0, 'S(6)': 2712.0, 'Alkalinity': '141.682 as HCO3', 'density': 1.023})
    sea.equalize(['Calcite', 'CO2(g)'], [0.0, LOGPCO2_SEA])
    F = np.linspace(0.0, 1.0, nf)
    Dg = np.linspace(0.0, dmax, nd)
    logom = np.zeros((nf, nd))
    dsat = np.zeros(nf)
    for i, f in enumerate(F):
        m = pp.mix_solutions({fresh: 1 - f, sea: f})
        ca0 = m.total('Ca', 'mmol')
        for j, d in enumerate(Dg):
            mj = pp.mix_solutions({fresh: 1 - f, sea: f})
            if d > 0:
                mj.add('CaCO3', d, 'mmol')
            logom[i, j] = mj.si('Calcite')
            mj.forget()
        ms = pp.mix_solutions({fresh: 1 - f, sea: f})
        ms.saturate('Calcite', 0.0)
        dsat[i] = ms.total('Ca', 'mmol') - ca0
        ms.forget(); m.forget()
    ends = dict(fresh_pH=fresh.pH, sea_pH=sea.pH, fresh_Ca=fresh.total('Ca', 'mmol'), sea_Ca=sea.total('Ca', 'mmol'),
                fresh_I=fresh.I, sea_I=sea.I, fresh_alk=fresh.total_element('C', 'mmol') if hasattr(fresh, 'total_element') else np.nan)
    np.savez(TABLE, F=F, D=Dg, logom=logom, dsat=dsat, **{k: np.array(v) for k, v in ends.items()})
    return load_table()


def load_table():
    if not os.path.exists(TABLE):
        return build_table()
    t = np.load(TABLE)
    return {k: t[k] for k in t.files}


class Chem:
    """bilinear interpolation of log10 Omega(f, dCa) and linear interpolation of dCa_sat(f)."""
    def __init__(self, tab):
        self.F, self.D, self.L, self.S = tab['F'], tab['D'], tab['logom'], tab['dsat']
        self.df, self.dd = self.F[1] - self.F[0], self.D[1] - self.D[0]

    def omega(self, f, d):
        fi = np.clip(f / self.df, 0, len(self.F) - 1 - 1e-9)
        di = np.clip(d / self.dd, 0, len(self.D) - 1 - 1e-9)
        i0 = fi.astype(int); j0 = di.astype(int)
        tf = fi - i0; td = di - j0
        L = self.L
        v = (L[i0, j0] * (1 - tf) * (1 - td) + L[i0 + 1, j0] * tf * (1 - td) + L[i0, j0 + 1] * (1 - tf) * td
             + L[i0 + 1, j0 + 1] * tf * td)
        return 10.0 ** v

    def dsat(self, f):
        return np.interp(f, self.F, self.S)


def rate_shape(om, n1, n2, omc):
    """g(Omega) for arrays; n1, n2, omc broadcast as [P, 1]."""
    u = np.clip(1.0 - om, 0.0, None)
    uc = 1.0 - omc
    near = u ** n1
    far = (uc ** n1) * (np.maximum(u, 1e-30) / uc) ** n2
    return np.where(om >= omc, near, far)


GEOM = dict(v=0.2, alpha_t=0.05, Dm=8.6e-5, phi=0.30, L=1000.0, zmax=40.0, nz=200, dx=2.0, x_obs=500.0,
            z_obs=(-6.0, -3.0, 0.0, 3.0, 6.0))


def simulate(kappa, n1, n2, omc, chem, g=GEOM, nsub=4, law='kink'):
    """March the mixing zone to x = L for a batch of parameter sets.
    kappa: rate prefactor (mmol/L/day); law: 'kink' (reference), 'linear' (n = 1 everywhere), 'lea' (equilibrium).
    Returns the dCa profile at x_obs (at the sampling depths) and the dissolution rate G (mol per m of coast per year)."""
    kappa = np.atleast_1d(np.asarray(kappa, float))[:, None]
    n1 = np.atleast_1d(np.asarray(n1, float))[:, None]
    n2 = np.atleast_1d(np.asarray(n2, float))[:, None]
    omc = np.atleast_1d(np.asarray(omc, float))[:, None]
    P = kappa.shape[0]
    nz = g['nz']; z = np.linspace(-g['zmax'], g['zmax'], nz); dz = z[1] - z[0]
    DT = g['alpha_t'] * g['v'] + g['Dm']
    dt = g['dx'] / g['v']                                  # days per x-step
    # implicit (backward Euler) diffusion operator with zero-gradient ends
    lam = DT * dt / dz ** 2
    A = np.eye(nz) * (1 + 2 * lam) - lam * (np.eye(nz, k=1) + np.eye(nz, k=-1))
    A[0, 1] = -2 * lam; A[-1, -2] = -2 * lam
    Ainv = np.linalg.inv(A).T
    f = np.where(z < 0, 1.0, 0.0)[None, :]
    f = np.where(z == 0, 0.5, f)
    d = np.zeros((P, nz))
    nx = int(round(g['L'] / g['dx'])); kobs = int(round(g['x_obs'] / g['dx']))
    obs = None
    for k in range(nx):
        f = f @ Ainv
        d = d @ Ainv
        if law == 'lea':
            d = np.maximum(d, chem.dsat(f))
        else:
            h = dt / nsub
            for _ in range(nsub):
                om = chem.omega(np.broadcast_to(f, d.shape), d)
                if law == 'linear':
                    gg = np.clip(1.0 - om, 0.0, None)
                else:
                    gg = rate_shape(om, n1, n2, omc)
                deficit = np.clip(chem.dsat(np.broadcast_to(f, d.shape)) - d, 0.0, None)
                d = d + np.minimum(kappa * gg * h, deficit)
        if k + 1 == kobs:
            obs = np.stack([np.interp(g['z_obs'], z, d[p]) for p in range(P)]) if P <= 2 else interp_rows(z, d, g['z_obs'])
    G = g['phi'] * g['v'] * d.sum(axis=1) * dz * 365.0        # mmol/L = mol/m3; mol per m of coast per year
    return dict(z=z, f=f[0], d_end=d, obs=obs, G=G)


def interp_rows(z, d, zq):
    idx = np.clip(np.searchsorted(z, zq) - 1, 0, len(z) - 2)
    w = (np.asarray(zq) - z[idx]) / (z[idx + 1] - z[idx])
    return d[:, idx] * (1 - w) + d[:, idx + 1] * w
