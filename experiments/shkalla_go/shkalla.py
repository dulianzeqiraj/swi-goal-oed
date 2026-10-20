"""SHKALLA-GO forward model: calcite rate laws derived from a surface reaction graph (matrix-tree theorem) and their
use in the freshwater-seawater mixing zone and in an injection-barrier scenario.

Surface graph. A kink on a calcite step alternates between a carbonate-terminated state K and a calcium-terminated
state K'. Ca2+ attaches to K (rate kA aCa) and detaches from K' (rate b1); CO3^2- attaches to K' (rate kC aCO3),
which advances the kink by one growth unit, and detaches backwards (rate b2). Mg2+ blocks K (dead-end state, constant
KM) and SO4^2- blocks K' (dead-end state, constant KS). By the matrix-tree theorem the stationary step flux is
    J = (kA aCa kC aCO3 - b1 b2) / D,  D = (b1 + kC aCO3)(1 + aMg/KM) + (b2 + kA aCa)(1 + aSO4/KS),
and detailed balance at Omega = 1 (Haldane) gives b1 b2 = kA kC Ksp, so that J = kA kC Ksp (Omega - 1) / D.
With x_A = aCa/aCa*, x_C = aCO3/aCO3* at the calcite-saturated reference water (aCa* aCO3* = Ksp) the rate law is
    R = rho (Omega - 1) / [ (1 - w)(1 + psi x_C)(1 + aMg/KM) + w (1 + x_A/psi)(1 + aSO4/KS) ]          (graph law)
with five parameters: the field prefactor rho (mmol/L/day), the attachment/detachment ratio psi, the weight
w = b2/(b1 + b2), and the inhibition constants KM and KS (activities in mmol). The usual practice is the
transition-state law in Omega alone,
    R = kappa (1 - Omega)^n                                                                       (TST law)

Chemistry. PHREEQC (phreeqc.dat, 15 C) through phreeqpython, tabulated once for two mixing lines:
  'nat': fresh groundwater (calcite-saturated, log pCO2 -2.0) and intruded seawater (calcite-saturated, log pCO2 -2.5);
  'bar': injected soft water (Ca 0.5, alkalinity 1.0 mmol/kgw, not stabilized, log pCO2 -2.0) and the same
         seawater: the hydraulic-barrier scenario.
For each seawater fraction f and calcite dissolved dCa the table holds log10 of the activities of Ca2+, CO3^2-, Mg2+,
SO4^2- (mmol), log10 Omega(calcite) and the calcite capacity dsat(f).

Transport. Transverse mixing between a fresh (or injected) layer and a saline layer flowing in parallel, as in
TRETJA-GO: v dc/dx = D_T d2c/dz2 + R, marched in x; f is conservative, dCa reacts. Batched over parameter sets.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.join(HERE, 'shkalla_table.npz')
TEMP = 15.0
LINES = ('nat', 'bar')
DMAX = {'nat': 0.20, 'bar': 0.60}
SPECIES = ('Ca+2', 'CO3-2', 'Mg+2', 'SO4-2')
TINY = 1e-12


def _waters(pp):
    fresh = pp.add_solution({'temp': TEMP, 'units': 'mmol/kgw', 'Na': 1.0, 'Cl': 1.0, 'Mg': 0.5, 'S(6)': 0.5})
    fresh.equalize(['Calcite', 'CO2(g)'], [0.0, -2.0])
    sea = pp.add_solution({'temp': TEMP, 'units': 'ppm', 'pH': 8.22, 'Ca': 412.3, 'Mg': 1291.8, 'Na': 10768.0,
                           'K': 399.1, 'Cl': 19353.0, 'S(6)': 2712.0, 'Alkalinity': '141.682 as HCO3', 'density': 1.023})
    sea.equalize(['Calcite', 'CO2(g)'], [0.0, -2.5])
    inj = pp.add_solution({'temp': TEMP, 'units': 'mmol/kgw', 'Ca': 0.5, 'Na': 1.0, 'Cl': 1.0,
                           'Alkalinity': '1.0 as HCO3'})
    inj.equalize(['CO2(g)'], [-2.0])
    return fresh, sea, inj


def build_table(nf=101, nd=81):
    """log10 activities and Omega on (f, dCa) for both lines, and the calcite capacity (requires phreeqpython)."""
    from phreeqpython import PhreeqPython
    pp = PhreeqPython(database='phreeqc.dat')
    fresh, sea, inj = _waters(pp)
    ends = {'nat': fresh, 'bar': inj}
    F = np.linspace(0.0, 1.0, nf)
    out = {'F': F}
    for L in LINES:
        A = ends[L]
        Dg = np.linspace(0.0, DMAX[L], nd)
        la = np.zeros((len(SPECIES), nf, nd)); lom = np.zeros((nf, nd)); dsat = np.zeros(nf)
        for i, f in enumerate(F):
            for j, d in enumerate(Dg):
                m = pp.mix_solutions({A: 1 - f, sea: f})
                if d > 0:
                    m.add('CaCO3', d, 'mmol')
                for k, sp in enumerate(SPECIES):
                    la[k, i, j] = np.log10(max(m.activity(sp), TINY))
                lom[i, j] = m.si('Calcite')
                m.forget()
            m0 = pp.mix_solutions({A: 1 - f, sea: f}); ca0 = m0.total('Ca', 'mmol'); m0.forget()
            ms = pp.mix_solutions({A: 1 - f, sea: f}); ms.saturate('Calcite', 0.0)
            dsat[i] = max(ms.total('Ca', 'mmol') - ca0, 0.0); ms.forget()
        out[f'D_{L}'] = Dg; out[f'la_{L}'] = la; out[f'lom_{L}'] = lom; out[f'dsat_{L}'] = dsat
    out['ref_la'] = np.array([np.log10(fresh.activity('Ca+2')), np.log10(fresh.activity('CO3-2'))])
    out['ends'] = np.array([fresh.pH, sea.pH, inj.pH, inj.si('Calcite'), fresh.total('Ca', 'mmol'),
                            sea.total('Ca', 'mmol'), inj.total('Ca', 'mmol')])
    np.savez(TABLE, **out)
    return load_table()


def load_table():
    if not os.path.exists(TABLE):
        return build_table()
    t = np.load(TABLE)
    return {k: t[k] for k in t.files}


class Chem:
    """Bilinear interpolation of the tables of one mixing line."""
    def __init__(self, tab, line):
        self.F = tab['F']; self.D = tab[f'D_{line}']
        self.T = np.concatenate([tab[f'la_{line}'], tab[f'lom_{line}'][None]], axis=0)   # [5, nf, nd]
        self.S = tab[f'dsat_{line}']
        self.df = self.F[1] - self.F[0]; self.dd = self.D[1] - self.D[0]

    def state(self, f, d):
        """log10 [aCa, aCO3, aMg, aSO4, Omega] at (f, d); arrays of equal shape."""
        fi = np.clip(f / self.df, 0, len(self.F) - 1 - 1e-9)
        di = np.clip(d / self.dd, 0, len(self.D) - 1 - 1e-9)
        i0 = fi.astype(int); j0 = di.astype(int)
        tf = fi - i0; td = di - j0
        T = self.T
        return (T[:, i0, j0] * (1 - tf) * (1 - td) + T[:, i0 + 1, j0] * tf * (1 - td)
                + T[:, i0, j0 + 1] * (1 - tf) * td + T[:, i0 + 1, j0 + 1] * tf * td)

    def dsat(self, f):
        return np.interp(f, self.F, self.S)

    def state_shared(self, fz, d):
        """As state() when every row of d shares the seawater fractions fz (shape [nz]); d has shape [P, nz]."""
        fi = np.clip(fz / self.df, 0, len(self.F) - 1 - 1e-9)
        i0 = fi.astype(int); tf = (fi - i0)[:, None]
        Tz = self.T[:, i0, :] * (1 - tf) + self.T[:, i0 + 1, :] * tf          # [5, nz, nd]
        di = np.clip(d / self.dd, 0, len(self.D) - 1 - 1e-9)
        j0 = di.astype(int); td = di - j0
        cols = np.arange(fz.shape[0])[None, :]
        return Tz[:, cols, j0] * (1 - td) + Tz[:, cols, j0 + 1] * td


# ---------------------------------------------------------------- rate laws
def graph_shape(la, psi, w, KM, KS, ref):
    """(Omega - 1)/P(a) for the graph law with unit prefactor. la: log10 [aCa, aCO3, aMg, aSO4, Omega] (leading axis 5);
    parameters broadcast against the remaining axes. ref: log10 [aCa*, aCO3*]."""
    xA = 10.0 ** (la[0] - ref[0]); xC = 10.0 ** (la[1] - ref[1])
    m = 10.0 ** la[2] / KM; s = 10.0 ** la[3] / KS
    om = 10.0 ** la[4]
    P = (1.0 - w) * (1.0 + psi * xC) * (1.0 + m) + w * (1.0 + xA / psi) * (1.0 + s)
    return (om - 1.0) / P


def tst_shape(la, n):
    om = 10.0 ** la[4]
    return -np.clip(1.0 - om, 0.0, None) ** n


GEOM = dict(v=0.2, alpha_t=0.05, Dm=8.6e-5, phi=0.30, L=1000.0, zmax=40.0, nz=120, dx=2.5, x_obs=500.0,
            z_obs=(-6.0, -3.0, 0.0, 3.0, 6.0))


def simulate(rate, chem, g=GEOM, nsub=2):
    """March the mixing zone to x = L for a batch of parameter sets.
    rate(la) returns the dissolution rate (mmol/L/day, >= 0) for the batch, la of shape [5, P, nz].
    Returns the dCa profile at x_obs (at the sampling depths) and G, the calcite dissolved (mol per m of coast per year)."""
    nz = g['nz']; z = np.linspace(-g['zmax'], g['zmax'], nz); dz = z[1] - z[0]
    DT = g['alpha_t'] * g['v'] + g['Dm']
    dt = g['dx'] / g['v']
    lam = DT * dt / dz ** 2
    A = np.eye(nz) * (1 + 2 * lam) - lam * (np.eye(nz, k=1) + np.eye(nz, k=-1))
    A[0, 1] = -2 * lam; A[-1, -2] = -2 * lam
    Ainv = np.linalg.inv(A).T
    f = np.where(z < 0, 1.0, 0.0)[None, :]
    P = rate.P
    d = np.zeros((P, nz))
    nx = int(round(g['L'] / g['dx'])); kobs = int(round(g['x_obs'] / g['dx']))
    obs = None
    for k in range(nx):
        f = f @ Ainv
        d = d @ Ainv
        fz = f[0]
        cap = chem.dsat(fz)[None, :]
        h = dt / nsub
        for _ in range(nsub):
            la = chem.state_shared(fz, d)
            r = rate(la)
            d = d + np.minimum(r * h, np.clip(cap - d, 0.0, None))
        if k + 1 == kobs:
            obs = interp_rows(z, d, g['z_obs'])
    G = g['phi'] * g['v'] * d.sum(axis=1) * dz * 365.0
    return dict(z=z, f=f[0], d_end=d, obs=obs, G=G)


def interp_rows(z, d, zq):
    idx = np.clip(np.searchsorted(z, zq) - 1, 0, len(z) - 2)
    w = (np.asarray(zq) - z[idx]) / (z[idx + 1] - z[idx])
    return d[:, idx] * (1 - w) + d[:, idx + 1] * w


class GraphRate:
    """Batch of graph-law parameter sets: arrays of shape [P]."""
    def __init__(self, rho, psi, w, KM, KS, ref):
        self.p = [np.asarray(v, float)[:, None] for v in (rho, psi, w, KM, KS)]
        self.ref = ref; self.P = self.p[0].shape[0]

    def __call__(self, la):
        rho, psi, w, KM, KS = self.p
        return np.clip(-rho * graph_shape(la, psi, w, KM, KS, self.ref), 0.0, None)


class TSTRate:
    def __init__(self, kappa, n):
        self.k = np.asarray(kappa, float)[:, None]; self.n = np.asarray(n, float)[:, None]; self.P = self.k.shape[0]

    def __call__(self, la):
        return np.clip(-self.k * tst_shape(la, self.n), 0.0, None)
