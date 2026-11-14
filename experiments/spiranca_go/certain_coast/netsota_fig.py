"""CERTAIN-COAST: a one-dimensional illustration of a monitoring network that is optimal today and not tomorrow.

A sharp-interface wedge (Glover's solution) in a confined coastal aquifer: the toe lies at X = delta*K*B^2/(2q), where q
is the fresh outflow per unit width of coast. Relative sea-level rise R(t) = eta(t) - u_z(t) (sea level plus subsidence)
lowers the fresh outflow, q(t) = q0 - a*R(t) with a = K*B/L, and the toe moves inland. Chloride sensors at the base of
the aquifer read s_i = Phi((X - x_i)/w) + noise, where w is the width of the mixing zone. The network is designed to
estimate (X, w) by D-optimality (log det of the Fisher matrix), greedily, among candidate positions every 20 m.

Three networks are compared over 40 years, with the D-efficiency eff(t) = (det F(xi; X_t) / det F(xi*_t; X_t))^(1/2):
the network optimal today, a network designed for the whole horizon (robust: the average log det over the toe
positions of the next 40 years), and the optimal network of each year (re-designed). The lifetime of a network is the
first year at which its efficiency falls below 1 - eps. All values are illustrative, not measured at the sites.

usage: python netsota_fig.py OUT.png [OUT.json]"""
import json
import sys

import numpy as np

DELTA, K, B, L = 0.025, 40.0, 40.0, 4000.0       # density ratio, conductivity m/d, thickness m, distance to inland head m
Q0 = 1.2                                          # fresh outflow today, m2/d per m of coast
RATE = 0.012                                      # relative sea-level rise, m/yr (4 mm/yr sea level + 8 mm/yr subsidence)
W, SIGMA = 40.0, 0.05                             # width of the mixing zone (m) and sensor noise (relative salinity)
CAND = np.arange(400.0, 1201.0, 20.0)             # candidate sensor positions, m from the coast
N_SENS, YEARS, EPS = 5, np.arange(0, 41), 0.5


def toe(t):
    q = Q0 - (K * B / L) * RATE * t
    return DELTA * K * B ** 2 / (2.0 * q)


def jac(x, X, w=W):
    z = (X - x) / w
    phi = np.exp(-0.5 * z ** 2) / np.sqrt(2 * np.pi)
    return np.stack([phi / w, -phi * z / w], axis=-1)        # d s / d(X, w)


def logdet(sel, Xs):
    """Average log det of the Fisher matrix of the sensors `sel` over the toe positions Xs."""
    vals = []
    for X in np.atleast_1d(Xs):
        J = jac(CAND[sel], X)
        F = J.T @ J / SIGMA ** 2 + 1e-9 * np.eye(2)
        vals.append(np.linalg.slogdet(F)[1])
    return float(np.mean(vals))


def greedy(Xs, n=N_SENS):
    sel = []
    for _ in range(n):
        best = max((k for k in range(len(CAND)) if k not in sel), key=lambda k: logdet(sel + [k], Xs))
        sel.append(best)
    return sorted(sel)


def main(out, out_json=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    Xt = np.array([toe(t) for t in YEARS])
    today = greedy(Xt[0])
    robust = greedy(Xt)                                       # designed for the whole horizon
    eff = {'today': [], 'robust': []}
    for X in Xt:
        best = greedy(X)
        ref = max(logdet(best, X), logdet(today, X), logdet(robust, X))   # greedy is near, not always at, the optimum
        for name, sel in (('today', today), ('robust', robust)):
            eff[name].append(float(np.exp(0.5 * (logdet(sel, X) - ref))))
    life = {k: next((int(t) for t, e in zip(YEARS, v) if e < 1 - EPS), None) for k, v in eff.items()}
    above = {k: [int(t) for t, e in zip(YEARS, v) if e >= 1 - EPS] for k, v in eff.items()}

    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.9), dpi=300, gridspec_kw={'width_ratios': [1.15, 1]})
    xs = np.linspace(0, 1200, 400)
    for t, col, ls in ((0, '#1F3864', '-'), (20, '#2E6DB4', '--'), (40, '#C00000', ':')):
        X = toe(t)
        zeta = np.sqrt(np.clip(2 * (Q0 - (K * B / L) * RATE * t) * xs / (DELTA * K), 0, None))
        a.plot(xs, -np.minimum(zeta, B), color=col, ls=ls, lw=1.4, label=f'interface, year {t} (toe {X:.0f} m)')
    a.scatter(CAND[today], np.full(N_SENS, -B), s=26, color='#1F3864', zorder=3, label='network optimal today')
    a.scatter(CAND[robust], np.full(N_SENS, -B - 4), s=26, marker='s', color='#E08A1E', zorder=3,
              label='network for the 40-year horizon')
    a.set_xlim(0, 1200); a.set_ylim(-B - 9, 2)
    a.set_xlabel('distance from the coast (m)', fontsize=8); a.set_ylabel('depth (m)', fontsize=8)
    a.tick_params(labelsize=7); a.legend(fontsize=5.8, loc='upper right', frameon=False)
    a.text(0.02, 0.06, '(a)', transform=a.transAxes, fontsize=8, fontweight='bold')
    a.text(120, -36, 'salt water', fontsize=6.5, color='#52606D')
    a.text(880, -30, 'fresh water', fontsize=6.5, color='#52606D')
    a.text(8, -1.5, 'coast', fontsize=6.5, color='#52606D')

    b.plot(YEARS, eff['today'], color='#1F3864', lw=1.6, label='optimal today')
    b.plot(YEARS, eff['robust'], color='#E08A1E', lw=1.6, label='designed for 40 years')
    b.axhline(1.0, color='#7A8590', lw=0.8, ls='--', label='re-designed each year')
    b.axhline(1 - EPS, color='#C00000', lw=0.8, ls=':')
    if life['today'] is not None:
        b.axvline(life['today'], color='#1F3864', lw=0.8, ls=':')
        b.text(life['today'] + 0.6, 0.08, f'lifetime\n{life["today"]} years', fontsize=6.5, color='#1F3864')
    b.text(1, 1 - EPS + 0.02, r'$1-\varepsilon$', fontsize=7, color='#C00000')
    b.set_xlabel('years from today', fontsize=8); b.set_ylabel('D-efficiency of the network', fontsize=8)
    b.set_ylim(0, 1.05); b.set_xlim(0, 40); b.tick_params(labelsize=7)
    b.legend(fontsize=6, loc='lower right', frameon=False, bbox_to_anchor=(1.0, 0.12))
    b.text(0.02, 0.04, '(b)', transform=b.transAxes, fontsize=8, fontweight='bold')
    fig.tight_layout(); fig.savefig(out, dpi=300, bbox_inches='tight', pad_inches=0.04); plt.close(fig)

    res = {'toe_m': {str(t): round(float(toe(t)), 1) for t in (0, 10, 20, 30, 40)},
           'today_sensors_m': CAND[today].tolist(), 'robust_sensors_m': CAND[robust].tolist(),
           'eff_today': {str(t): round(eff['today'][t], 3) for t in (0, 5, 10, 20, 30, 40)},
           'eff_robust': {str(t): round(eff['robust'][t], 3) for t in (0, 5, 10, 20, 30, 40)},
           'lifetime_years': life, 'years_above': {k: [v[0], v[-1], len(v)] if v else [] for k, v in above.items()},
           'mean_eff': {k: round(float(np.mean(v)), 3) for k, v in eff.items()}, 'eps': EPS}
    if out_json:
        with open(out_json, 'w', encoding='utf-8') as fh:
            json.dump(res, fh, indent=1)
    print(json.dumps(res))
    return res


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
