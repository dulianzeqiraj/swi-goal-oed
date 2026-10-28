"""Two diagrams for the note on the assembly and the solution algorithm (large type):
  figA1_coupling.png   how the assembled equations are coupled, with the decision layer closing the loop
  figA2_flowchart.png  the solution algorithm (preparation, decision search, one season)"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED = '#1f2933', '#52606d'
C = dict(inp=('#fff4e0', '#c27c12'), phys=('#e8f1fb', '#2e6db4'), core=('#f5f8fc', '#9db2d6'), dec=('#e6f5ee', '#1e8a5a'),
         goal=('#fdecec', '#b03a3a'), adj=('#f1ecfa', '#6a4fb3'), cond=('#fff8d6', '#b8920f'), term=('#eceff3', '#52606d'))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'mathtext.fontset': 'dejavusans'})
FB, FT, FS = 11.0, 12.0, 10.0          # body, title, small


def box(ax, x, y, w, h, title, body='', kind='phys', fs=FB, tfs=FT, r=0.1):
    fc, ec = C[kind]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f'round,pad=0.02,rounding_size={r}', fc=fc, ec=ec, lw=1.6, zorder=2))
    if body:
        ax.text(x, y + h / 2 - 0.1, title, ha='center', va='top', fontsize=tfs, fontweight='bold', color=ec, zorder=3)
        ax.text(x, y - 0.13, body, ha='center', va='center', fontsize=fs, color=INK, zorder=3, linespacing=1.4)
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=fs, color=INK, zorder=3, linespacing=1.35)


def diamond(ax, x, y, w, h, text, fs=FB):
    fc, ec = C['cond']
    ax.add_patch(Polygon([(x - w / 2, y), (x, y + h / 2), (x + w / 2, y), (x, y - h / 2)], closed=True, fc=fc, ec=ec, lw=1.6, zorder=2))
    ax.text(x, y, text, ha='center', va='center', fontsize=fs, color=INK, zorder=3, linespacing=1.3)


def arrow(ax, pts, label=None, lpos=None, color=MUTED, lw=1.5, fs=FS, ha='center', va='bottom', rot=0):
    for (x0, y0), (x1, y1) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, zorder=1, solid_capstyle='round')
    ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, mutation_scale=14), zorder=1)
    if label:
        lx, ly = lpos if lpos else ((pts[-2][0] + pts[-1][0]) / 2, (pts[-2][1] + pts[-1][1]) / 2)
        ax.text(lx, ly, label, fontsize=fs, color=color, ha=ha, va=va, zorder=4, rotation=rot,
                bbox=dict(fc='white', ec='none', pad=0.8, alpha=0.9))


def dbl(ax, p0, p1, color):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='<|-|>', color=color, lw=1.5, mutation_scale=13), zorder=1)


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis('off')
    return fig, ax


# ====================================================================== Figure A1: coupling of the assembled equations
def fig_coupling():
    fig, ax = canvas(13.4, 9.0)
    fc, ec = C['core']
    ax.add_patch(FancyBboxPatch((3.25, 1.25), 5.7, 7.55, boxstyle='round,pad=0.02,rounding_size=0.14', fc=fc, ec=ec, lw=1.4, ls='--', zorder=0))
    ax.text(6.1, 8.62, 'Assembled system: one coupled block per step', ha='center', va='center', fontsize=FT, fontweight='bold', color='#2e6db4')
    box(ax, 6.1, 7.6, 5.5, 1.3, '(6) Boundaries and sources',
        r'sea face: $h=(1+\delta)\eta_\xi(t)-\delta z$, $c=1$ on inflow' '\n'
        r'inland: $q_n=q_{in}R_{\xi,t}$, $c=0$;  top and base closed' '\n'
        r'wells: $W=-\overline{Q}(1+u_t)\,e_Q(x_s)-H_t\,e_P$', kind='inp')
    box(ax, 4.65, 5.85, 2.7, 1.45, '(1) Flow, memory',
        r'$S_s\partial_t h+\nabla\cdot\mathbf{q}=W$' '\n' r'$-\Sigma_k\, s_k a_k(h-h_k)$' '\n' r'$\partial_t h_k=a_k(h-h_k)$')
    box(ax, 7.55, 5.85, 2.7, 1.75, '(3) Salt, immobile zones',
        r'$n\partial_t c+\nabla\cdot(\mathbf{q}c)-c\nabla\cdot\mathbf{q}$' '\n' r'$-\nabla\cdot(n\mathbf{D}\nabla c)$' '\n'
        r'$+\Sigma_k\, n b_k a_k(c-c_k)=0$' '\n' r'$\partial_t c_k=a_k(c-c_k)$')
    box(ax, 6.3, 4.1, 2.2, 0.95, '(2) Darcy', r'$\mathbf{q}=-\mathbf{K}(\nabla h+\delta c\,\mathbf{e}_z)$', fs=10.5)
    box(ax, 8.2, 4.1, 1.4, 1.2, '(4) Dispersion', r'$nD_m+$' '\n' r'$(\alpha_L q_n^2+\alpha_T q_t^2)$' '\n' r'$/\,|\mathbf{q}|$', fs=9.5, tfs=10.5)
    box(ax, 6.5, 2.3, 2.6, 1.2, '(5) Ions, one way', 'Cl, Na, K, Ca, Mg, SO$_4$, HCO$_3$\nsame operator +\nGaines–Thomas exchange', fs=10)
    box(ax, 4.15, 2.3, 1.6, 1.2, '(11) Adjoint', r'$J_n^{\top}\lambda_n=g_n$' '\n' r'$-B_{n+1}^{\top}\lambda_{n+1}$' '\n' r'$\rightarrow d\mathcal{J}/dp$', kind='adj', fs=10, tfs=10.5)
    dbl(ax, (5.35, 5.125), (5.75, 4.575), '#2e6db4')
    ax.text(5.42, 4.78, r'$h,\ \nabla\!\cdot\mathbf{q}$', fontsize=FS, color='#2e6db4', ha='right', va='center')
    dbl(ax, (7.05, 4.975), (6.95, 4.575), '#b03a3a')
    ax.text(7.12, 4.82, r'$\mathbf{q}\!\downarrow\ \delta c\!\uparrow$', fontsize=FS, color='#b03a3a', ha='left', va='center')
    arrow(ax, [(7.4, 4.1), (7.5, 4.1)], color='#2e6db4')
    arrow(ax, [(8.2, 4.7), (8.2, 4.975)], color='#2e6db4')
    arrow(ax, [(6.4, 3.625), (6.4, 2.9)], r'$\mathbf{q},\,c$', (6.47, 3.26), color=MUTED, ha='left', va='center')
    arrow(ax, [(4.65, 6.95), (4.65, 6.575)], color='#c27c12')
    arrow(ax, [(7.55, 6.95), (7.55, 6.725)], color='#c27c12')
    box(ax, 1.6, 7.2, 2.95, 2.0, 'Storyline $\\xi$, weather $\\omega$',
        r'$R_{\xi,t}$: recharge' '\n' r'(intense rain: $r^{eff}\neq r^{g}$)' '\n' r'$\eta_\xi(t)$: sea level, surge' '\n' r'$h_{\xi,t}$: private abstraction' '\n' r'(drought, causal change)', kind='inp', fs=10.5)
    box(ax, 1.6, 4.75, 2.95, 1.75, 'Decisions $d$',
        r'$x_s$: supply-well screen' '\n' r'$u_t$: pumping rule' '\n' r'$H_{max}$: drought cap' '\n' r'$m,\ \sigma$: alarm, samples', kind='dec', fs=10.5)
    box(ax, 1.6, 2.45, 2.95, 1.55, '(7) Initial state',
        'steady state ' r'$R(y^0)=0$' '\n' '+ 100 years spin-up\n' r'$\rightarrow (y^0,z^0)$ starts every run', kind='term', fs=10.5)
    arrow(ax, [(3.08, 7.95), (3.35, 7.95)], color='#c27c12')
    arrow(ax, [(3.08, 5.3), (3.17, 5.3), (3.17, 7.25), (3.35, 7.25)], color='#1e8a5a')
    arrow(ax, [(3.35, 2.3), (3.12, 2.3), (3.12, 4.3), (3.08, 4.3)], color='#6a4fb3')
    ax.text(3.3, 1.55, r'gradient for $x_s$ $\uparrow$', fontsize=9.5, color='#6a4fb3', ha='left', va='center')
    box(ax, 11.15, 7.7, 3.4, 1.3, '(8) Goal at the screen',
        r'$J_t=|\Gamma_s|^{-1}\int_{\Gamma_s}c\,dz$' '\n' r'$\mathrm{Cl}_t>250\ \mathrm{mg/L}\Leftrightarrow J_t>\varepsilon_{lim}$', kind='goal', fs=10.5)
    box(ax, 11.15, 6.15, 3.4, 1.3, 'SPIRANCA-GO alarm (13)',
        r'$\hat{Y}_t$ from heads + anchors $r,p$' '\n' r'margin $m=q_{1-\alpha}+\overline{\delta}\max\{0,\ell\}$', kind='dec', fs=10.5)
    box(ax, 11.15, 4.6, 3.4, 1.3, 'ROJA-GO watch (14)',
        r'detectors $F_t$ $\rightarrow$ extra sample' '\n' r'window $K_t$: $K^2(K+1)=2\sigma^2/(\rho\Delta)^2$', kind='dec', fs=10.3)
    box(ax, 11.15, 3.15, 3.4, 1.0, 'Decision rule (13)', r'$u_{t+1}=u_{cut}$ if $A_t$, else $u_{dec}$', kind='dec', fs=10.5)
    box(ax, 11.15, 1.75, 3.4, 1.15, 'Objective (12)',
        r'$\max_d\ \min_\xi\ \mathbb{E}[\mathrm{water}]$' '\n' r'exceedance $\leq\varepsilon$ in every $\xi$', kind='goal', fs=10.5)
    arrow(ax, [(8.9, 6.4), (9.25, 6.4), (9.25, 7.7), (9.45, 7.7)], r'$c$', (9.3, 7.05), color='#b03a3a', ha='left', va='center')
    arrow(ax, [(5.07, 5.125), (5.07, 1.45), (9.05, 1.45), (9.05, 5.9), (9.45, 5.9)], color='#2e6db4')
    ax.text(7.3, 1.47, 'heads at the piezometers', fontsize=FS, color='#2e6db4', ha='center', va='bottom')
    arrow(ax, [(12.85, 7.7), (13.02, 7.7), (13.02, 4.6), (12.85, 4.6)], 'yearly sample', (13.17, 6.15), color='#b03a3a', ha='center', va='center', fs=9.5, rot=90)
    arrow(ax, [(11.15, 5.5), (11.15, 5.25)], color='#1e8a5a')
    arrow(ax, [(11.15, 3.95), (11.15, 3.65)], r'$A_t$', (11.22, 3.8), color='#1e8a5a', ha='left', va='center')
    arrow(ax, [(11.15, 2.65), (11.15, 2.33)], color='#1e8a5a')
    arrow(ax, [(9.45, 2.95), (9.25, 2.95), (9.25, 0.75), (0.05, 0.75), (0.05, 4.75), (0.125, 4.75)], color='#1e8a5a')
    ax.text(4.6, 0.68, r'feedback: $u_{t+1}$ enters the sources of the next step', fontsize=FS, color='#1e8a5a', ha='center', va='top')
    fig.savefig(os.path.join(OUT, 'figA1_coupling.png'), dpi=200)
    plt.close(fig)


# ====================================================================== Figure A2: flowchart of the solution algorithm
def fig_flow():
    fig, ax = canvas(13.4, 9.5)
    cols = [(2.0, 'Prepare (once per aquifer)', 3.6), (6.35, 'Decide (outer loops)', 3.8), (10.85, 'One season t (30 ms)', 3.95)]
    for x, t, w in cols:
        ax.add_patch(FancyBboxPatch((x - w / 2 - 0.08, 0.1), w + 0.16, 9.25, boxstyle='round,pad=0.02,rounding_size=0.12', fc='#fafbfc', ec='#d9dee3', lw=1.0, zorder=0))
        ax.text(x, 9.12, t, ha='center', va='center', fontsize=FT + 0.5, fontweight='bold', color=INK)
    x1, x2, x3 = cols[0][0], cols[1][0], cols[2][0]
    w1, w2, w3 = 3.45, 3.65, 3.85
    box(ax, x1, 8.45, 1.6, 0.48, 'Start', kind='term', fs=FT)
    box(ax, x1, 7.45, w1, 1.05, 'Grid and parameters', '39 × 20 mesh (780 cells)\n' r'$\theta=(K,q_{in},\alpha_L,a_k,b_k,\ldots)$', kind='term')
    box(ax, x1, 6.1, w1, 1.05, 'Initial state (7)', r'steady: Newton on $R(y^0)=0$' '\n' r'tol $10^{-11}$ (0.8 s)')
    box(ax, x1, 4.75, w1, 1.05, 'Spin-up', '100 years of private\nabstraction ' r'$\rightarrow z^0$')
    box(ax, x1, 3.4, w1, 1.05, 'Record (80 years)', 'heads, anchors ' r'$r,\ p$,' '\nchloride, season by season')
    box(ax, x1, 1.95, w1, 1.15, 'Fit the decision layer', 'alarm: anchor regression,\n' r'margin $m$; watch thresholds', kind='dec')
    box(ax, x1, 0.62, w1, 0.78, r'End: decision $d^*$' '\n' 'with margin and sampling plan', kind='term', fs=10.5)
    for ya, yb in ((8.21, 7.98), (6.92, 6.63), (5.57, 5.28), (4.22, 3.93), (2.87, 2.53)):
        arrow(ax, [(x1, ya), (x1, yb)])
    arrow(ax, [(x1 + w1 / 2, 1.95), (4.1, 1.95), (4.1, 8.28), (x2 - w2 / 2, 8.28)])
    box(ax, x2, 8.0, w2, 1.05, 'Candidate decision', r'$d=(x_s,u_{dec},u_{cut},B,H_{max})$' '\n' r'grid; $x_s$ by adjoint gradient (11)', kind='dec', fs=10.3)
    box(ax, x2, 6.75, w2, 1.0, r'Storyline $\xi$, weather $\omega$', 'ordinary, intense rain, drought,\ncausal change, compound', kind='inp', fs=10.3)
    box(ax, x2, 5.6, w2, 0.85, 'Simulate 30 years', r'season loop $\rightarrow$', fs=10.5)
    diamond(ax, x2, 4.45, 2.9, 1.0, r'all $\xi,\omega$ done?')
    diamond(ax, x2, 3.1, 3.3, 1.15, 'exceedance ' r'$\leq\varepsilon$' '\nin every ' r'$\xi$ (13)?')
    box(ax, x2, 1.95, w2, 0.75, 'Objective (12)', 'keep the best ' r'$d$', kind='goal', fs=10.5)
    diamond(ax, x2, 0.95, 2.8, 0.7, 'more candidates?', fs=10.5)
    arrow(ax, [(x2, 7.47), (x2, 7.25)])
    arrow(ax, [(x2, 6.25), (x2, 6.03)])
    arrow(ax, [(x2, 5.17), (x2, 4.95)])
    arrow(ax, [(x2, 3.95), (x2, 3.68)], 'yes', (x2 + 0.1, 3.82), ha='left', va='center')
    arrow(ax, [(x2, 2.52), (x2, 2.33)], 'yes', (x2 + 0.1, 2.43), ha='left', va='center')
    arrow(ax, [(x2, 1.57), (x2, 1.3)])
    arrow(ax, [(x2 - 1.45, 4.45), (x2 - 1.95, 4.45), (x2 - 1.95, 6.75), (x2 - w2 / 2, 6.75)], 'no', (x2 - 1.5, 4.5), ha='right')
    arrow(ax, [(x2 + 1.65, 3.1), (x2 + 1.98, 3.1), (x2 + 1.98, 0.95), (x2 + 1.4, 0.95)], 'no', (x2 + 1.7, 3.15), ha='left')
    arrow(ax, [(x2 - 1.4, 0.95), (x2 - 2.08, 0.95), (x2 - 2.08, 7.75), (x2 - w2 / 2, 7.75)], 'yes', (x2 - 1.45, 1.0), ha='right')
    arrow(ax, [(x2, 0.6), (x2, 0.3), (x1 + w1 / 2, 0.3)], 'no', (x2 + 0.1, 0.45), ha='left', va='center')
    gx = (x2 + w2 / 2 + 0.08 + x3 - w3 / 2 - 0.08) / 2
    arrow(ax, [(x2 + w2 / 2, 5.6), (gx - 0.1, 5.6), (gx - 0.1, 8.3), (x3 - w3 / 2, 8.3)])
    arrow(ax, [(x3 - 0.95, 0.6), (gx + 0.1, 0.6), (gx + 0.1, 4.45), (x2 + 1.45, 4.45)])
    ax.text(x3 - 1.0, 0.65, 'no: scores', fontsize=FS, color=MUTED, ha='right', va='bottom', bbox=dict(fc='white', ec='none', pad=0.8))
    box(ax, x3, 8.3, w3, 0.95, 'Sources of season t', r'$Q_t=\overline{Q}(1+u_t)$;  $H_t=\overline{H}\min(h_t,H_{max})$' '\n' 'in a declared drought', kind='inp', fs=10.3)
    box(ax, x3, 7.12, w3, 0.95, 'Predictor', r'lagged $\mathbf{D}$, memory sources;' '\n' 'flow, then salt', fs=10.5)
    box(ax, x3, 5.92, w3, 1.0, 'Chord Newton (10)', r'$J\,\delta y=-R_n(y)$;  $y\leftarrow y+\delta y$' '\n' '6.4 iterations on average', fs=10.5)
    diamond(ax, x3, 4.7, 3.3, 1.0, r'$|\delta c|<10^{-10}$, $|\delta h|<10^{-8}$?', fs=10.5)
    box(ax, x3, 3.5, w3, 0.95, 'Update (9)', r'states $z^n=\alpha z^{n-1}+\beta y^n$;' '\n' r'ions; goal $J_t$ (8)', fs=10.5)
    box(ax, x3, 2.3, w3, 1.05, 'Alarm and watch (13), (14)', r'$\hat{Y}_t$, detectors $F_t$, samples,' '\n' r'window $K_t$, alarm $A_t$', kind='dec', fs=10.5)
    box(ax, x3, 1.35, w3, 0.55, r'$u_{t+1}=u_{cut}$ if $A_t$, else $u_{dec}$', kind='dec', fs=10.5)
    diamond(ax, x3, 0.6, 1.9, 0.55, r'$t<T$?', fs=10.5)
    for ya, yb in ((7.82, 7.6), (6.64, 6.42), (5.42, 5.2), (2.97, 2.83), (1.77, 1.63), (1.07, 0.88)):
        arrow(ax, [(x3, ya), (x3, yb)])
    arrow(ax, [(x3, 4.2), (x3, 3.98)], 'yes', (x3 + 0.1, 4.09), ha='left', va='center')
    arrow(ax, [(x3 + 1.65, 4.7), (x3 + 2.05, 4.7), (x3 + 2.05, 5.92), (x3 + w3 / 2, 5.92)], 'no', (x3 + 1.72, 4.75), ha='left')
    arrow(ax, [(x3 + 0.95, 0.6), (x3 + 2.2, 0.6), (x3 + 2.2, 8.3), (x3 + w3 / 2, 8.3)], r'yes: $t+1$', (x3 + 1.05, 0.65), ha='left')
    fig.savefig(os.path.join(OUT, 'figA2_flowchart.png'), dpi=200)
    plt.close(fig)


if __name__ == '__main__':
    fig_coupling(); fig_flow()
    print('ok')
