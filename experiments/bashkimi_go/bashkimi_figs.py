"""Figure B1 of review 55 (BASHKIMI-GO): (a) one plausible aquifer: the true effect of high pumping on the seasonal
log-chloride change, the wells of the five holders and the target wells; (b) quality of the merge chosen by each
criterion relative to the BASHKIMI-GO decision value (paired difference of the expected gain, 200 aquifers), with the
physics-informed and the generic polynomial CATE model; (c) go / no-go against a merge cost: net benefit of merging
only when the decision value exceeds the cost, against always merging; (d) privacy: how often the private choice
equals the non-private one, for differential privacy alone and for the two secure-computation mechanisms.
Run after bashkimi_summary.py (both models): python3 bashkimi_figs.py
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bashkimi as B

INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'
HOLD_STYLE = [dict(c=INK, marker='^', s=34), dict(c=BLUE, marker='o', s=14), dict(c=AQUA, marker='D', s=20),
              dict(c=ORANGE, marker='s', s=34), dict(c=MAGENTA, marker='P', s=40)]


def tau_field(i):
    m = B.m
    if B.V.LZ is None:
        B.V.zeta_chol()
    rng = np.random.default_rng(550000 + i)
    th = B.V.LG @ rng.standard_normal(m.Nz); ze = B.V.draw_zeta(rng)
    lu = spla.splu(B.V.matrix(th, ze)); hn = lu.solve(m.rhs)
    gam, lam, _ = B.chem_draw(rng)
    g = np.zeros(m.Nc)
    for ch in np.array_split(B.VI, 12):
        g[ch] = B.self_drawdown(lu, ch)
    tau = np.full(m.Nc, np.nan); tau[B.VI] = B.tau_of(hn[B.VI], g[B.VI], gam, lam)
    return tau


def style(ax):
    ax.tick_params(colors=INK2, labelsize=7.5)
    for s_ in ax.spines.values():
        s_.set_color(GRID)


def main():
    S = json.load(open(os.path.join(HERE, 'res', 'bashkimi_summary.json')))
    Sp = json.load(open(os.path.join(HERE, 'res', 'bashkimi_summary_poly.json')))
    m = B.m
    fig = plt.figure(figsize=(12.0, 9.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.15], hspace=0.42, wspace=0.42)
    # ------------------------------------------------------------ (a) map
    a = fig.add_subplot(gs[0, 0]); iw = 1
    B.load_calib(); w = B.make_world(iw); tau = tau_field(iw)
    v = m.valid
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list('grey_ramp', ['#efeee9', '#9a9893', '#0b0b0b'])
    sc = a.scatter(m.cx[v], m.cy[v], s=2.2, c=np.clip(tau[v], 0, 0.6), cmap=cm, vmin=0, vmax=0.6, marker='s', lw=0, zorder=0)
    a.scatter(m.cx[m.sea_idx], m.cy[m.sea_idx], s=5, c=BLUE, marker='s', lw=0, zorder=1)
    a.annotate('sea contact', (m.cx[m.sea_idx].min(), m.cy[m.sea_idx].max()), xytext=(2, 6), textcoords='offset points',
               fontsize=7.5, color=BLUE)
    for h, x, st in zip(B.HOLDERS, w['W'], HOLD_STYLE):
        a.scatter(m.cx[x['wells']], m.cy[x['wells']], edgecolors='white', lw=0.4, zorder=4,
                  label=f"{h['name']} ({h['nw'] * h['ns']} records, {int(100 * h['p'])}% pumped high)", **st)
    a.scatter(m.cx[w['tg']], m.cy[w['tg']], s=46, facecolors='none', edgecolors=INK, lw=0.9, zorder=3, label='target wells (cap or not)')
    cb = fig.colorbar(sc, ax=a, fraction=0.035, pad=0.02); cb.ax.tick_params(labelsize=7, colors=INK2)
    cb.set_label('true effect of high pumping (log Cl)', fontsize=7.5, color=INK2)
    a.set_aspect('equal'); a.set_xlabel('Easting (km)', color=INK2, fontsize=8.5); a.set_ylabel('Northing (km)', color=INK2, fontsize=8.5)
    a.set_xlim(m.cx[v].min() - 0.6, m.cx[v].max() + 0.6); a.set_ylim(m.cy[v].min() - 0.6, m.cy[v].max() + 0.8)
    a.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fontsize=6.6, frameon=False, ncol=2, columnspacing=0.8, handletextpad=0.3)
    a.set_title('(a) Who holds which wells (one plausible aquifer)', fontsize=9.5, color=INK, loc='left')
    style(a)
    # ------------------------------------------------------------ (b) criteria
    b = fig.add_subplot(gs[0, 1])
    keys = [('n', 'largest dataset'), ('eig_all', 'EIG, all parameters'), ('eig_cate', 'EIG, CATE parameters (anchor)'),
            ('eig_goal', 'mean EIG, target CATEs')]
    for off, SS, col, lab, fc in ((-0.13, S, BLUE, 'physics-informed CATE model', BLUE), (0.13, Sp, ORANGE, 'polynomial CATE model (as the anchor)', 'white')):
        C = {c['key']: c for c in SS['criteria']}
        y = np.arange(len(keys)) + off
        mu = np.array([-C[k]['diff_vs_value'][0] for k, _ in keys]); er = np.array([C[k]['diff_vs_value'][1] for k, _ in keys])
        b.errorbar(mu, y, xerr=er, fmt='o', ms=6, color=col, mfc=fc, mec=col, lw=1.2, capsize=3, label=lab)
    b.axvline(0, color=INK2, lw=0.9)
    b.set_yticks([])
    for j, (_, l) in enumerate(keys):
        b.annotate(l, (0.015, j - 0.33), xycoords=('axes fraction', 'data'), fontsize=8, color=INK, va='center')
    b.set_ylim(-0.6, len(keys) - 0.6)
    b.invert_yaxis()
    b.set_xlabel('expected gain of its merge minus that of the BASHKIMI-GO merge (loss units, 95% CI)', color=INK2, fontsize=8)
    b.legend(loc='lower left', fontsize=7.2, frameon=True, framealpha=0.9, edgecolor=GRID)
    b.set_title('(b) Which merge each criterion picks, 200 aquifers', fontsize=9.5, color=INK, loc='left')
    b.grid(axis='x', color=GRID, lw=0.6); style(b)
    # ------------------------------------------------------------ (c) go / no-go
    c = fig.add_subplot(gs[1, 0])
    gg = S['gonogo']; cost = [x['cost'] for x in gg]
    for key, lab, col, ls, mk in (('net_rule', 'BASHKIMI-GO: merge only if value > cost', ORANGE, '-', 'o'),
                                  ('net_always', 'always merge (BASHKIMI-GO pick)', BLUE, '-', 's'),
                                  ('net_eig_always', 'always merge (anchor EIG pick)', AQUA, '--', 'D'),
                                  ('net_oracle', 'oracle (knows the gains)', INK2, ':', None)):
        yv = np.array([x[key][0] for x in gg]); ye = np.array([x[key][1] for x in gg])
        c.plot(cost, yv, ls=ls, color=col, marker=mk, ms=5, lw=1.6, label=lab)
        if key == 'net_rule':
            c.fill_between(cost, yv - ye, yv + ye, color=col, alpha=0.15, lw=0)
    c.axhline(0, color=INK2, lw=0.9)
    c.annotate('never merge', (cost[0], 0), xytext=(2, -11), textcoords='offset points', fontsize=7.5, color=INK2)
    c.set_xlabel('cost of making one merge (same units as the loss)', color=INK2, fontsize=8.5)
    c.set_ylabel('net benefit of the merge policy (mean over aquifers)', color=INK2, fontsize=8.5)
    c.legend(loc='lower left', fontsize=7.2, frameon=True, framealpha=0.9, edgecolor=GRID)
    c.set_title('(c) Is merging worth it? (physics-informed model)', fontsize=9.5, color=INK, loc='left')
    c.grid(color=GRID, lw=0.6); style(c)
    # ------------------------------------------------------------ (d) privacy
    d = fig.add_subplot(gs[1, 1])
    eps = S['privacy']['eps']
    from matplotlib.lines import Line2D
    mechs = (('A_', 'DP alone (noisy Gram matrix)', INK2, 'x'), ('B0.3_', 'MPC + clipping + noisy value', BLUE, 's'),
             ('C0.3_', 'MPC + clipping + noisy whitened information', ORANGE, 'o'))
    for SS, ls in ((S, '-'), (Sp, '--')):
        M = SS['privacy']['mech']
        for key, lab, col, mk in mechs:
            d.plot(eps, [M[f'{key}{e}']['agree'] for e in eps], ls=ls, color=col, marker=mk, ms=5, lw=1.5)
    h1 = [Line2D([], [], color=col, marker=mk, lw=1.5, label=lab) for _, lab, col, mk in mechs]
    h2 = [Line2D([], [], color=INK2, ls='-', lw=1.5, label='physics-informed model'),
          Line2D([], [], color=INK2, ls='--', lw=1.5, label='polynomial model')]
    l1 = d.legend(handles=h1, loc='upper left', fontsize=6.8, frameon=False)
    d.add_artist(l1); d.legend(handles=h2, loc='lower right', fontsize=6.8, frameon=False)
    d.axhline(0.25, color=GRID, lw=1.2); d.annotate('random choice', (eps[0], 0.25), xytext=(2, -11), textcoords='offset points', fontsize=7.5, color=INK2)
    d.set_xscale('log'); d.set_xticks(eps); d.set_xticklabels([str(e) for e in eps])
    d.set_ylim(0, 1.05)
    d.set_xlabel(r'privacy budget $\varepsilon$ per candidate ($\delta = 10^{-6}$, one record = one well-season)', color=INK2, fontsize=8)
    d.set_ylabel('private choice = non-private choice (share of aquifers)', color=INK2, fontsize=8.5)
    d.set_title('(d) Choosing privately, information clipped at 0.3', fontsize=9.5, color=INK, loc='left')
    d.grid(color=GRID, lw=0.6); style(d)
    out = os.path.join(HERE, 'res', 'figB1_bashkimi.png'); fig.savefig(out, dpi=200, bbox_inches='tight'); print('wrote', out)


if __name__ == '__main__':
    main()
