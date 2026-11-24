"""Gates of the pore-scale solver: (1) drag of a square array of cylinders in Stokes flow against the series of Sangani &
Acrivos (1982), (2) closure of the energy budget, (3) independence of the permeability from the viscosity and the force."""
import json, sys, time
import numpy as np
import lbm


def sangani_acrivos(c):
    return 4 * np.pi / (np.log(c ** -0.5) - 0.738 + c - 0.887 * c ** 2 + 2.038 * c ** 3)


def steady(solid, nu, g, tol=1e-9, block=500, max_steps=400000):
    f, fn = lbm.init(solid)
    acc = np.zeros((7,) + solid.shape)
    u_old, n = 0.0, 0
    while n < max_steps:
        f, fn, s = lbm.advance(f, fn, solid, nu, g, 0.0, block, acc)
        n += block
        if abs(s[0] - u_old) < tol * abs(s[0]) and n > 4 * block:
            break
        u_old = s[0]
    return s, n


out = []
t0 = time.time()
for L, a in ((64, 11.42), (64, 16.0), (128, 32.0), (96, 24.0)):
    c0 = (L - 1) / 2.0
    solid = lbm.disks_mask(L, L, [(c0, c0)], a)
    c_nom = np.pi * a * a / L ** 2
    c_grid = solid.mean()
    for nu, g in ((1 / 6, 1e-6), (0.02, 1e-7), (1 / 6, 2e-6)):
        s, n = steady(solid, nu, g)
        U, V, ke, phi = s
        k_sim = g * L * L / (nu * U)
        rec = dict(L=L, a=a, c_nominal=c_nom, c_grid=float(c_grid), nu=nu, g=g, steps=n, U=U, K=nu * U / g,
                   Re=U * 2 * a / nu, k_sim=k_sim, k_SA_nominal=sangani_acrivos(c_nom), k_SA_grid=sangani_acrivos(c_grid),
                   energy_in=g * U, dissipation=phi, budget_error=phi / (g * U) - 1)
        out.append(rec)
        print(f"L={L} a={a} c={c_nom:.4f}/{c_grid:.4f} nu={nu:.4f} g={g:.0e} steps={n} Re={rec['Re']:.2e} K={rec['K']:.4f} "
              f"k_sim={k_sim:.3f} SA(nom)={rec['k_SA_nominal']:.3f} SA(grid)={rec['k_SA_grid']:.3f} "
              f"dev(nom)={k_sim / rec['k_SA_nominal'] - 1:+.4f} budget={rec['budget_error']:+.5f}", flush=True)
print('time', round(time.time() - t0, 1), 's')
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'gates.json', 'w'), indent=1)
