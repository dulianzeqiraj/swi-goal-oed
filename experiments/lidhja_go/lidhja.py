"""LIDHJA-GO (lidhja: the coupling): how much error of a reactive closure leaks into chloride through the diffusion
potential of multi-ion (Nernst-Planck) transport, and the bound of Theorem 2.

Seven ions (Cl, Na, K, Ca, Mg, SO4, HCO3; mmol/L) move by advection, a mechanical dispersion D_mech common to all
ions, ion-specific molecular diffusion D_i and electromigration under zero electric current:
    flux_i = v c_i - (D_mech + D_i) dc_i/dx - z_i D_i c_i dphi/dx,
    dphi/dx = - sum_j z_j D_j dc_j/dx / sum_j z_j^2 D_j c_j      (phi = F psi / RT).
The cations exchange in local equilibrium (Gaines-Thomas, capacity E meq/L, selectivities K_Na\\K, K_Na\\Ca,
K_Na\\Mg) with the routine of ../gjurma_go. The "true" and the "wrong" closure differ only in the exchanger, which
never acts on chloride; any difference of chloride between them is the leak.

Part L  a clay lens (no flow, D_mech = 0): its edge is held at the mobile-water composition, and the chloride taken
        up by the lens is the memory term of chloride; salinisation (fresh -> 5 % sea water) and freshening.
Part P  the flow regime: the same mixing problem with a common mechanical dispersion D_mech = Pe * D_Cl for
        Pe = 0 ... 300, run to the same mixing depth.
Every case is run three ways: equal diffusivities (the leak must vanish), Fick with ion-specific diffusivities and
no electric field (no leak either), and Nernst-Planck (the leak). The bound of Theorem 2 is evaluated on the
computed fields. Writes lidhja_results.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'gjurma_go'))
import gjurma_model as G  # noqa: E402

YR = 3.15576e7
# free-water diffusion coefficients at 25 C (Li & Gregory 1974), 1e-9 m2/s -> m2/yr
D_FREE = np.array([2.032, 1.334, 1.957, 0.792, 0.706, 1.065, 1.185]) * 1e-9 * YR
Z = G.Z
I_CL = G.I_CL
IC, ZC = G.IC, G.ZC
IA = [G.I_CL, G.I_SO4, G.I_HCO3]


def neutral(c):
    """close the charge balance on HCO3"""
    c = c.copy()
    c[G.I_HCO3] += (Z * c).sum()
    return c


FRESH, SEA = neutral(G.FRESH), neutral(G.SEA)
mix = lambda f: f * SEA + (1 - f) * FRESH                     # noqa: E731


class Column:
    """1-D finite-volume column [0, L], Dirichlet composition at x = 0, no flux at x = L."""

    def __init__(self, L, nx, tau, E, logK, mode, D_mech=0.0, v=0.0):
        self.dx = L / nx
        self.x = (np.arange(nx) + 0.5) * self.dx
        self.nx = nx
        D = tau * D_FREE
        self.D = np.full(7, D[I_CL]) if mode == 'equal' else D
        self.coupled = mode == 'np'
        self.E = np.full(nx, E)
        self.logK = np.broadcast_to(np.log(logK), (nx, 3))
        self.Dm, self.v = D_mech, v

    def init(self, c0):
        self.c = np.tile(c0, (self.nx, 1))
        self.T = ZC * self.c[:, IC] + self.E[:, None] * G.exchanger(self.c, self.logK)
        return self

    def faces(self, cb):
        """face gradients and face concentrations, ghost cell at x = 0 from the boundary composition"""
        cg = np.vstack([2 * cb - self.c[0], self.c])             # ghost: boundary value at the face
        grad = (cg[1:] - cg[:-1]) / self.dx                       # faces 0 .. nx-1 (face i is left of cell i)
        cf = 0.5 * (cg[1:] + cg[:-1])
        return grad, cf

    def flux(self, cb):
        grad, cf = self.faces(cb)
        Dt = self.Dm + self.D
        J = -Dt * grad
        gphi = np.zeros(self.nx)
        if self.coupled:
            num = (Z * self.D * grad).sum(1)
            den = (Z ** 2 * self.D * np.maximum(cf, 1e-12)).sum(1)
            gphi = -num / den
            J = J - Z * self.D * cf * gphi[:, None]
        if self.v:
            cg = np.vstack([cb, self.c])                          # upwind (v > 0 into the column)
            J = J + self.v * cg[:-1]
        return J, gphi, grad, cf

    def step(self, cb, dt):
        J, gphi, grad, cf = self.flux(cb)
        Jall = np.vstack([J, np.zeros(7)])                       # no flux at x = L
        dc = -(Jall[1:] - Jall[:-1]) / self.dx * dt
        for i in IA:
            self.c[:, i] += dc[:, i]
        self.T = self.T + ZC * dc[:, IC]
        y = G.solve_cations(self.T, self.E, self.logK, self.c[:, IC])
        self.c[:, IC] = y
        return gphi, grad, cf


def run(case, mode, closure, keep_every=None):
    """case: dict(L, nx, tau, D_mech, c_init, c_bound, T_end, dt); closure: dict(E, K)."""
    col = Column(case['L'], case['nx'], case['tau'], closure['E'], closure['K'], mode, case.get('D_mech', 0.0),
                 case.get('v', 0.0)).init(case['c_init'])
    nt = int(round(case['T_end'] / case['dt']))
    hist = []
    for n in range(nt):
        col.step(case['c_bound'], case['dt'])
        if keep_every and (n + 1) % keep_every == 0:
            hist.append(col.c.copy())
    return col, np.array(hist)


def leak_and_bound(case, mode, true, wrong, nkeep=100):
    """chloride difference between the two closures and the right-hand side of Theorem 2 (on the computed fields)"""
    nt = int(round(case['T_end'] / case['dt']))
    ke = max(1, nt // nkeep)
    a, ha = run(case, mode, true, ke)
    b, hb = run(case, mode, wrong, ke)
    dt_k = ke * case['dt']
    u = hb[:, :, I_CL] - ha[:, :, I_CL]
    dx = a.dx
    sup_u2 = float((u ** 2).sum(1).max() * dx)                   # sup_t ||u||^2 (theta factored out)
    # right-hand side: 2 e^{2 Lambda T} int int D_Cl^2 c'_Cl^2 |s_R|^2 / D_tot
    Dcl, Dt = a.D[I_CL], a.Dm + a.D[I_CL]
    rhs, lam = 0.0, 0.0
    R_k, L_k = [], []
    if mode == 'np':
        for k in range(len(ha)):
            for col, h in ((a, ha), (b, hb)):
                col.c = h[k]
            ga, cfa = a.faces(case['c_bound'])
            gb, cfb = b.faces(case['c_bound'])
            Dn = a.D
            nonCl = [j for j in range(7) if j != I_CL]
            Na = (Z * (Dn - Dcl) * ga)[:, nonCl].sum(1)          # N with the chloride reference (Dbar = D_Cl)
            Nb = (Z * (Dn - Dcl) * gb)[:, nonCl].sum(1)
            Ma = (Z ** 2 * Dn * cfa).sum(1)
            Mb = (Z ** 2 * Dn * cfb).sum(1)
            gphi_a = -Na / Ma
            dcf = cfb - cfa
            sR = (Nb - Na) / Mb + gphi_a * (Z ** 2 * Dn * dcf)[:, nonCl].sum(1) / Mb
            R_k.append(float((Dcl ** 2 * cfb[:, I_CL] ** 2 * sR ** 2 / Dt).sum() * dx))
            L_k.append(float((Dcl ** 2 * gphi_a ** 2 / Dt).max()))
        R_k, L_k = np.array(R_k), np.array(L_k)
        lam = float(L_k.max())
        rhs = 2.0 * np.exp(2 * lam * case['T_end']) * float(R_k.sum() * dt_k)       # constant-Lambda Gronwall
        # time-resolved Gronwall: ||u(T)||^2 <= 2 int_0^T exp(2 int_t^T Lambda) R(t) dt
        tail = np.cumsum((L_k * dt_k)[::-1])[::-1]
        rhs_t = 2.0 * float((np.exp(2 * tail) * R_k).sum() * dt_k)
        rhs_0 = 2.0 * float(R_k.sum() * dt_k)                                        # leading order (Lambda -> 0)
    mcl_a = ha[:, :, I_CL].sum(1) * dx                           # chloride stored in the column over time
    mcl_b = hb[:, :, I_CL].sum(1) * dx
    mcl0 = case['c_init'][I_CL] * case['L']
    rel = (mcl_b - mcl_a) / np.maximum(np.abs(mcl_a - mcl0), 1e-12)
    if mode != 'np':
        rhs_t = rhs_0 = 0.0
    return dict(sup_u=float(np.sqrt(sup_u2)), bound=float(np.sqrt(rhs)) if mode == 'np' else 0.0,
                bound_t=float(np.sqrt(rhs_t)), bound_0=float(np.sqrt(rhs_0)), u_T=float(np.sqrt((u[-1] ** 2).sum() * dx)),
                max_abs_u=float(np.abs(u).max()), rel_uptake=rel.tolist(), t=(np.arange(1, len(ha) + 1) * dt_k).tolist(),
                uptake_true=(mcl_a - mcl0).tolist(), lam_T=float(lam * case['T_end']),
                profile_true=ha[-1].tolist(), profile_wrong=hb[-1].tolist(), x=a.x.tolist())


def main():
    E_LENS = 500.0                                               # meq per litre of pore water (clay)
    true = dict(E=E_LENS, K=G.K_TRUE)
    wrongs = {'E -30%': dict(E=0.7 * E_LENS, K=G.K_TRUE),
              'K_Na\\Ca x1.5, K_Na\\Mg x1.5': dict(E=E_LENS, K=G.K_TRUE * np.array([1.0, 1.5, 1.5]))}
    out = dict(D_free_m2_per_yr=D_FREE.tolist(), species=G.SPECIES)
    # ---------------- Part L: clay lens, half-thickness 1 m, tortuosity factor 0.3, 100 years
    lens = dict(L=1.0, nx=40, tau=0.3, D_mech=0.0, T_end=100.0, dt=0.01)
    scen = {'salinisation (fresh -> 5 % sea water)': (FRESH, mix(0.05)),
            'freshening (5 % sea water -> fresh)': (mix(0.05), FRESH)}
    out['L'] = {}
    for sname, (ci, cb) in scen.items():
        case = dict(lens, c_init=ci, c_bound=cb)
        out['L'][sname] = {}
        for wname, wrong in wrongs.items():
            res = {}
            for mode in ('equal', 'fick', 'np'):
                r = leak_and_bound(case, mode, true, wrong)
                res[mode] = r
                print(f'L | {sname[:12]} | {wname:28s} | {mode:5s} | max|dCl| {r["max_abs_u"]:.3e} mmol/L  '
                      f'||u|| {r["sup_u"]:.3e}  bound {r["bound"]:.3e} / {r["bound_t"]:.3e} / {r["bound_0"]:.3e}  rel uptake @100yr {r["rel_uptake"][-1]:+.4f}',
                      flush=True)
            out['L'][sname][wname] = res
    # ---------------- Part P: flow regime, common dispersion D_mech = Pe * D_Cl, same mixing depth 0.2 m
    out['P'] = {}
    tau_s = 0.5
    Dcl = tau_s * D_FREE[I_CL]
    for Pe in (0.0, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0):
        Dt = (1 + Pe) * Dcl
        T_end = 0.2 ** 2 / Dt
        dt = min(0.2 * (0.5 / 60) ** 2 / (2 * D_FREE.max() * tau_s * (1 + Pe)), T_end / 200)
        case = dict(L=0.5, nx=60, tau=tau_s, D_mech=Pe * Dcl, T_end=T_end, dt=dt, c_init=FRESH, c_bound=mix(0.05))
        wrong = dict(E=0.7 * 60.0, K=G.K_TRUE)
        res = {}
        for mode in ('equal', 'np'):
            r = leak_and_bound(case, mode, dict(E=60.0, K=G.K_TRUE), wrong)
            r = {k: r[k] for k in ('sup_u', 'u_T', 'bound', 'bound_t', 'bound_0', 'max_abs_u', 'lam_T')}
            res[mode] = r
        out['P'][str(Pe)] = res
        print(f'P | Pe {Pe:6.1f} | equal max|dCl| {res["equal"]["max_abs_u"]:.2e} | np max|dCl| '
              f'{res["np"]["max_abs_u"]:.3e} ||u|| {res["np"]["sup_u"]:.3e} bound {res["np"]["bound"]:.3e} / {res["np"]["bound_t"]:.3e}', flush=True)
    with open(os.path.join(HERE, 'lidhja_results.json'), 'w') as fh:
        json.dump(out, fh)


if __name__ == '__main__':
    main()
