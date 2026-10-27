"""Figures of the assembled-system note (MONTIMI-GO). Run after the stages; writes res/fig*.png."""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import scipy.sparse as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M

RES = os.path.join(HERE, 'res')
NAVY, ORANGE, TEAL, GREY, RED, GREEN, PURPLE = '#1F3864', '#D97706', '#0F766E', '#6B7280', '#B91C1C', '#15803D', '#6D28D9'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})


def box(ax, x, y, w, h, title, lines, color, fc='white'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012,rounding_size=0.018', fc=fc, ec=color, lw=1.6))
    ax.text(x + w / 2, y + h - 0.035, title, ha='center', va='top', fontsize=9.2, fontweight='bold', color=color)
    for k, s in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.085 - 0.045 * k, s, ha='center', va='top', fontsize=7.6, color='#1F2328')


def arrow(ax, a, b, color, style='-|>', ls='-', lw=1.5, rad=0.0, text=None, tpos=None, tcol=None):
    ar = FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=11, color=color, lw=lw, ls=ls, connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(ar)
    if text:
        ax.text(*(tpos or ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)), text, fontsize=7.2, color=tcol or color, ha='center', va='center',
                bbox=dict(fc='white', ec='none', pad=0.6))


def fig_assembly():
    fig = plt.figure(figsize=(11.0, 5.4))
    ax = fig.add_axes([0.0, 0.0, 0.64, 1.0]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.text(0.01, 0.975, '(a) The assembled system and what the goal sees', fontsize=10.5, fontweight='bold', color=NAVY, va='top')
    box(ax, 0.02, 0.62, 0.27, 0.28, 'Boundary and initial data', ['sea level: mean, rise, tides, surges', 'regional inflow, recharge, rivers', 'leaky base with memory', 'present state y(t0)'], GREY)
    box(ax, 0.36, 0.62, 0.28, 0.28, 'Flow block', ['S dh/dt + div q = wells', '- memory (kernel, tail K_h)', '+ learned closure Psi', 'Darcy with buoyancy'], NAVY, '#EEF3FA')
    box(ax, 0.36, 0.25, 0.28, 0.28, 'Salt block', ['sea fraction c from chloride', 'advection, dispersion', 'immobile zones c_k (memory)', 'screen chloride, toe X'], TEAL, '#ECFDF5')
    box(ax, 0.71, 0.25, 0.27, 0.28, 'Ion block', ['seven ions, Gaines-Thomas', 'calcite, sulfate reduction', 'electro-diffusion, closure Phi', 'algebraic exchanger'], GREY, '#F3F4F6')
    box(ax, 0.71, 0.62, 0.27, 0.28, 'Controls', ['recharge wells: site, rate', 'supply wells: site, rate', 'screens', 'chance constraint on Cl'], ORANGE, '#FFF5E1')
    box(ax, 0.02, 0.10, 0.27, 0.30, 'Goal and adjoint', ['J = screen sea fraction at t_H', 'Pr[J > eps_lim] <= alpha', 'adjoint lambda: one sweep', 'weights of every term'], RED, '#FEF2F2')
    arrow(ax, (0.29, 0.76), (0.36, 0.76), GREY)
    arrow(ax, (0.71, 0.76), (0.64, 0.76), ORANGE, text='u', tpos=(0.675, 0.79))
    arrow(ax, (0.45, 0.62), (0.45, 0.53), NAVY, text='flux q', tpos=(0.40, 0.575))
    arrow(ax, (0.55, 0.53), (0.55, 0.62), TEAL, text='density', tpos=(0.605, 0.575))
    arrow(ax, (0.64, 0.39), (0.71, 0.39), TEAL, text='q, c', tpos=(0.675, 0.42))
    arrow(ax, (0.36, 0.33), (0.29, 0.27), RED, text='J', tpos=(0.325, 0.33))
    arrow(ax, (0.22, 0.40), (0.38, 0.61), RED, ls='--', rad=-0.25, text='lambda', tpos=(0.24, 0.53))
    arrow(ax, (0.29, 0.20), (0.40, 0.25), RED, ls='--', rad=0.2)
    ax.text(0.845, 0.215, 'adjoint = 0 here:\ncut exactly (Theorem M1)', fontsize=7.6, color=RED, ha='center', va='top', style='italic')
    ax.text(0.50, 0.135, 'only two-way coupling: flow <-> salt (solved whole)', fontsize=7.8, color=NAVY, ha='center')
    ax.text(0.50, 0.095, 'everything below it is one-way (Proposition A1)', fontsize=7.8, color=NAVY, ha='center')
    # (b) Jacobian pattern on a small grid
    ax2 = fig.add_axes([0.67, 0.08, 0.31, 0.80])
    g = M.uniform_grid(8, 4)
    m = M.Model(g, layout=dict(xs=2000.0, Q=1.0))
    y = np.r_[np.ones(g.N), np.linspace(0, 1, g.N)]
    Jf = m.jac(y, y, m.dt).tocoo()
    N = g.N
    adj = (abs(m.DivGh) + sp.eye(N)).tocoo()                   # transport stencil
    blocks = [[None] * 4 for _ in range(4)]
    blocks[0][0] = Jf.tocsr()[:N, :N]; blocks[0][1] = Jf.tocsr()[:N, N:]; blocks[1][0] = Jf.tocsr()[N:, :N]; blocks[1][1] = Jf.tocsr()[N:, N:]
    blocks[2][0] = sp.kron(np.ones((7, 1)), adj); blocks[2][1] = sp.kron(np.ones((7, 1)), adj)
    blocks[2][2] = sp.kron(np.eye(7), adj) + sp.kron(np.ones((7, 7)) * np.r_[0, 1, 1, 1, 1, 0, 0][:, None] * np.r_[0, 1, 1, 1, 1, 0, 0][None, :], sp.eye(N))
    blocks[2][3] = sp.kron(np.r_[0, 1, 1, 1, 1, 0, 0][:, None] * np.ones((1, 4)), sp.eye(N))
    blocks[3][2] = sp.kron(np.ones((4, 1)) * np.r_[0, 1, 1, 1, 1, 0, 0][None, :], sp.eye(N))
    blocks[3][3] = sp.kron(np.ones((4, 4)), sp.eye(N))
    for i in range(4):
        for j in range(4):
            if blocks[i][j] is None:
                rows = [N, N, 7 * N, 4 * N][i]; cols = [N, N, 7 * N, 4 * N][j]
                blocks[i][j] = sp.csr_matrix((rows, cols))
    B = sp.bmat(blocks).tocoo()
    cols = np.where(B.row < 2 * N, np.where(B.col < 2 * N, 0, 1), np.where(B.col < 2 * N, 2, 3))
    cmap = {0: NAVY, 1: GREY, 2: TEAL, 3: GREY}
    ax2.scatter(B.col, B.row, s=0.6, c=[cmap[k] for k in cols], marker='s', linewidths=0)
    for v in (N, 2 * N, 9 * N):
        ax2.axhline(v - 0.5, color='#C9D1DC', lw=0.8); ax2.axvline(v - 0.5, color='#C9D1DC', lw=0.8)
    ax2.set_xlim(-0.5, 13 * N - 0.5); ax2.set_ylim(13 * N - 0.5, -0.5)
    ax2.set_xticks([N / 2, 1.5 * N, 5.5 * N, 11 * N]); ax2.set_xticklabels(['h', 'c', 'ions', 'beta'])
    ax2.set_yticks([N / 2, 1.5 * N, 5.5 * N, 11 * N]); ax2.set_yticklabels(['flow', 'salt', 'ions', 'exch.'])
    ax2.set_title('(b) Block Jacobian, 8 x 4 cells', fontsize=10.5, fontweight='bold', color=NAVY, loc='left')
    ax2.text(7.5 * N, 1.0 * N, 'zero blocks: nothing flows back to flow and salt', fontsize=7.3, color=RED, ha='center', va='center')
    fig.savefig(os.path.join(RES, 'figM1_assembly.png'), dpi=220)
    plt.close(fig)




def fig_section():
    """present and end-of-horizon salt field, wells, toe, and where the goal looks (time-integrated adjoint)."""
    import mg_setup as S
    st1 = json.load(open(os.path.join(RES, 'stage1.json')))
    c0 = st1['cases'][0]
    L = dict(xs=S.XS[0], xr=S.XR[5]); Q = c0['Q']
    g = S.GF
    m = M.Model(g, P=dict(S.MED), dt_yr=S.DT_YR)
    y0 = m.steady()
    J = m.run(y0=y0, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Q))])
    m.adjoint()
    N = g.N
    lam_c = np.zeros(N); lam_h = np.zeros(N)
    for n in range(S.NH + 1, S.NH + S.NF + 1):
        lam_c += np.abs(m.lam[n][N:]); lam_h += np.abs(m.lam[n][:N])
    xg = np.r_[g.xf] / 1000.0; zg = g.zf
    fig, axs = plt.subplots(3, 1, figsize=(10.5, 7.6), sharex=True)
    titles = [f'(a) Present state after 50 years of pumping 4 m²/d at 1.5 km (median aquifer)',
              f'(b) After 30 years: supply well at 2.0 km pumping {Q:.2f} m²/d, recharge well at 2.5 km (1 m²/d)',
              '(c) Where the goal looks: |adjoint| of the salt equation, integrated over the 30 years (log scale)']
    fields = [m.Y[S.NH][N:], m.Y[-1][N:], np.log10(lam_c / lam_c.max() + 1e-6)]
    for k, (ax, F) in enumerate(zip(axs, fields)):
        Fm = F.reshape(g.NZ, g.NX)
        if k < 2:
            pc = ax.pcolormesh(xg, zg, Fm, cmap='Blues', vmin=0, vmax=1, shading='flat')
            cs = ax.contour(g.xc / 1000, g.zc, Fm, levels=[M.EPS_LIM, 0.1, 0.5, 0.9], colors=[RED, '#475569', '#1E293B', '#0F172A'], linewidths=[1.4, 0.8, 1.2, 0.8])
            ax.clabel(cs, fmt={M.EPS_LIM: '250 mg/L', 0.1: '0.1', 0.5: '0.5', 0.9: '0.9'}, fontsize=6.5)
            X = m.toe(m.Y[S.NH] if k == 0 else m.Y[-1])
            ax.plot([X / 1000], [S.GF.zf[0] + 1.0], marker='^', color=ORANGE, ms=8, mec='k', mew=0.5)
            ax.text(X / 1000 + 0.04, S.GF.zf[0] + 2.5, f'toe {X:.0f} m', fontsize=7.5, color='#92400E')
        else:
            pc = ax.pcolormesh(xg, zg, Fm, cmap='magma_r', vmin=-4, vmax=0, shading='flat')
            xf = np.array(json.load(open(os.path.join(RES, 'grid_G.json')))['xf']) / 1000
            for x in xf:
                ax.plot([x, x], [-70.0, -67.0], color='#38BDF8', lw=1.0)
            ax.text(2.6, -64.5, 'ticks on the base: column edges of the goal-graded mesh', fontsize=7.2, color='#BAE6FD', va='bottom')
        if k == 0:
            ax.plot([S.X_HIST / 1000] * 2, [-30, -10], color=RED, lw=3.2, solid_capstyle='butt')
            ax.text(S.X_HIST / 1000 + 0.03, -12.5, 'old well field', fontsize=7.5, color=RED)
        else:
            ax.plot([L['xs'] / 1000] * 2, [-30, -10], color=RED, lw=3.2, solid_capstyle='butt')
            ax.plot([L['xr'] / 1000] * 2, [-70, -10], color=GREEN, lw=2.6, solid_capstyle='butt')
            ax.text(L['xs'] / 1000 - 0.03, -12.5, 'supply', fontsize=7.5, color=RED, ha='right')
            ax.text(L['xr'] / 1000 + 0.03, -12.5, 'recharge', fontsize=7.5, color=GREEN)
        ax.set_ylabel('z (m)'); ax.set_ylim(-70, -10)
        ax.set_title(titles[k], fontsize=9, loc='left', color=NAVY)
        cb = fig.colorbar(pc, ax=ax, pad=0.01, fraction=0.03)
        cb.set_label('sea fraction' if k < 2 else 'log10 relative', fontsize=7.5)
    axs[-1].set_xlabel('distance from the coast (km)')
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'figM2_section.png'), dpi=200)
    plt.close(fig)
    return dict(J=J, Q=Q, toe_present=m.toe(m.Y[S.NH]), toe_end=m.toe(m.Y[-1]), toe_pre=m.toe(m.Y[0]),
                hist_screen_cl=M.CL_F + (M.CL_S - M.CL_F) * float(M.Model(g, layout=dict(xs=S.X_HIST)).J(m.Y[S.NH])))


def fig_weights():
    st1 = json.load(open(os.path.join(RES, 'stage1.json')))
    keys = [r['key'] for r in st1['cases'][0]['terms']]
    labels = [r['label'] for r in st1['cases'][0]['terms']]
    thr = st1['tau'] * st1['eps_lim']
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    for i, k in enumerate(keys):
        ws = np.array([abs(next(r['weight'] for r in c['terms'] if r['key'] == k)) for c in st1['cases']])
        cut = k in st1['cut']
        ax.scatter(ws, [i] * len(ws), s=36, color=(GREY if cut else NAVY), zorder=3, edgecolor='white', lw=0.6)
        ax.plot([ws.min(), ws.max()], [i, i], color=(GREY if cut else NAVY), lw=2, zorder=2)
        ax.text(ws.max() * 1.6, i, 'cut' if cut else 'kept', va='center', fontsize=8, color=(GREY if cut else NAVY), fontweight='bold')
    ax.axvline(thr, color=RED, ls='--', lw=1.2)
    ax.text(thr / 1.12, -0.62, f'tolerance τ·ε_lim = {thr:.1e}', color=RED, fontsize=8, ha='right', va='center')
    ax.axvline(st1['eps_lim'], color=ORANGE, ls=':', lw=1.2)
    ax.text(st1['eps_lim'] * 1.1, -0.62, 'ε_lim (250 mg/L)', color=ORANGE, fontsize=8, va='center')
    ax.set_xscale('log'); ax.set_yticks(range(len(keys))); ax.set_yticklabels(labels)
    ax.set_xlim(1e-7, 0.2); ax.set_ylim(-0.9, len(keys) - 0.3)
    ax.set_xlabel('|goal weight| = |dJ/ds| (sea fraction at the supply screen), four reference layouts')
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'figM3_weights.png'), dpi=220)
    plt.close(fig)


def fig_place():
    import mg_setup as S
    A = json.load(open(os.path.join(RES, 'montimi.json')))
    names = A['layouts']
    QF = np.array(A['F']['qstar'])
    fig = plt.figure(figsize=(11.0, 6.4))
    ax = fig.add_axes([0.07, 0.42, 0.90, 0.52])
    x = np.arange(len(names))
    ax.plot(x, QF, 'o-', color='#111827', lw=1.6, ms=5, label='complete assembly (evaluation draws)', zorder=4)
    sty = {'G': (NAVY, 's', 'goal-guided assembly'), 'U': (TEAL, 'D', 'uniform coarse mesh, same terms'),
           'S': (ORANGE, '^', 'goal mesh, density lagged one step'), 'N': (PURPLE, 'v', 'goal mesh, no immobile zones')}
    for k, (col, mk, lab) in sty.items():
        if k not in A['assemblies']:
            continue
        ax.plot(x, A['assemblies'][k]['nomargin']['qstar'], mk, color=col, ms=5, label=lab + ' (design draws)', alpha=0.9)
        b = A['assemblies'][k]['nomargin']['best']
    bF = names.index(A['F']['best'])
    ax.axvspan(bF - 0.4, bF + 0.4, color='#FDE68A', alpha=0.5, zorder=0)
    for s in range(1, 4):
        ax.axvline(sum(1 for n in names if n.startswith('S2.0')) * 0 + [6, 12, 18][s - 1] - 0.5, color='#CBD5E1', lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=60, fontsize=7.2, ha='right')
    ax.set_ylabel('safe pumping rate Q* (m²/d per m of coast)')
    ax.set_title('(a) Safe yield of every layout at a 10% risk of exceeding 250 mg/L (S: supply well, R: recharge well, km from the coast)', fontsize=9, loc='left', color=NAVY)
    ax.legend(fontsize=7.2, loc='upper left', ncol=2, frameon=False)
    ax2 = fig.add_axes([0.07, 0.07, 0.40, 0.22])
    ks = [k for k in ('G', 'U', 'S', 'N') if k in A['assemblies']]
    r0 = [A['assemblies'][k]['nomargin']['realised_risk'] for k in ks]
    r1 = [A['assemblies'][k]['withmargin']['realised_risk'] for k in ks]
    xx = np.arange(len(ks))
    ax2.bar(xx - 0.2, r0, 0.38, color='#CBD5E1', label='without margin')
    ax2.bar(xx + 0.2, r1, 0.38, color=NAVY, label='with calibrated margin')
    ax2.axhline(A['alpha'], color=RED, ls='--', lw=1); ax2.axhline(A['alpha'] + A['beta'], color=RED, ls=':', lw=1)
    ax2.set_xticks(xx); ax2.set_xticklabels(ks); ax2.set_ylabel('risk on the complete\nassembly', fontsize=8)
    ax2.set_title('(b) Risk of the chosen layout and rate', fontsize=9, loc='left', color=NAVY)
    ax2.legend(fontsize=7, frameon=False)
    ax3 = fig.add_axes([0.57, 0.07, 0.40, 0.22])
    allr = np.concatenate([np.asarray(A['assemblies'][k]['residuals']) for k in A['assemblies'] if A['assemblies'][k].get('residuals')])
    lo_r, hi_r = float(allr.min()), float(allr.max())
    pad = 0.1 * (hi_r - lo_r + 1e-9)
    BINS = np.linspace(lo_r - pad, hi_r + pad, 25)
    for k in ks:
        r = A['assemblies'][k].get('residuals')
        if r:
            col = sty[k][0]
            ax3.hist(r, bins=BINS, histtype='step', lw=1.6, color=col, label=k)
            ax3.axvline(A['assemblies'][k]['margin'], color=col, ls='--', lw=1)
    ax3.set_xlabel('Q_c(cheap) − Q_c(complete) on calibration cases (m²/d)', fontsize=8)
    ax3.set_title('(c) Calibration of the margin', fontsize=9, loc='left', color=NAVY)
    ax3.legend(fontsize=7, frameon=False)
    fig.savefig(os.path.join(RES, 'figM4_place.png'), dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    which = sys.argv[1:] or ['assembly', 'section', 'weights', 'place']
    out = {}
    if 'assembly' in which:
        fig_assembly()
    if 'section' in which:
        out['section'] = fig_section()
    if 'weights' in which:
        fig_weights()
    if 'place' in which:
        fig_place()
    if out:
        prev = json.load(open(os.path.join(RES, 'figs.json'))) if os.path.exists(os.path.join(RES, 'figs.json')) else {}
        prev.update(out)
        json.dump(prev, open(os.path.join(RES, 'figs.json'), 'w'), indent=1)
