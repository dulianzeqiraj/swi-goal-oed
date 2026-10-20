"""Figures of DARA-GO: figD1_problem.png, figD2_map.png, figD3_dara.png."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve
import dara_model as M
import dara_setup as S
from dara_ref import Reference, cic1, gauss_kernel
from dara_exp import MapAff

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
RS = json.load(open('dara_results.json'))
X = np.array(RS['designs'])
C_PAR, C_GOAL, C_REF = '#1D4ED8', '#C2410C', '#111827'
LV = RS['levels']
R = Reference(n=2_000_000)

# ---------------------------------------------------------------- figure 1: the test problem
fig, ax = plt.subplots(1, 3, figsize=(10.6, 3.3))
rng = np.random.default_rng(7)
xs = np.linspace(0, M.L, 401)
for e0, e1, c in zip(M.EDGES[:-1], M.EDGES[1:], ('#E0F2FE', '#F1F5F9', '#ECFDF5')):
    ax[0].axvspan(e0, e1, color=c, zorder=0)
for k, lab in enumerate(('zone 1', 'zone 2', 'zone 3')):
    ax[0].text((M.EDGES[k] + M.EDGES[k + 1]) / 2, 5.35, lab, ha='center', fontsize=7.5, color='#374151')
for z in rng.standard_normal((25, 3)):
    ax[0].plot(xs, M.head(xs, *z), color='#64748B', lw=0.6, alpha=0.7)
z0 = np.zeros(3)
ax[0].plot(xs, M.head(xs, *z0), color=C_REF, lw=1.6, label='median conductivities')
ax[0].set_xlabel('distance from the coast x (m)'); ax[0].set_ylabel('freshwater head h (m)')
ax[0].set_ylim(-0.2, 5.6)
t0 = M.toe(*z0)
ax[0].annotate(f'toe of the wedge at median\nconductivities ({t0:.0f} m)', xy=(t0, 0.05), xytext=(1300, 0.6), fontsize=7,
               arrowprops=dict(arrowstyle='->', color=C_GOAL, lw=0.8), color=C_GOAL)
ax[0].legend(frameon=False, fontsize=7, loc='upper left', bbox_to_anchor=(0.0, 0.93))
ax[0].set_title('(a) heads for 25 prior draws', fontsize=9)
zz = rng.standard_normal((200000, 3))
H = M.head(xs[1:-1, None], *zz[None, :, :].transpose(2, 0, 1))
ax[1].fill_between(xs[1:-1], np.quantile(H, 0.05, axis=1), np.quantile(H, 0.95, axis=1), color='#CBD5E1', label='prior 90% band')
ax[1].plot(xs[1:-1], np.median(H, axis=1), color=C_REF, lw=1.2, label='prior median')
ax[1].plot(xs[1:-1], H.std(axis=1), color=C_PAR, lw=1.2, ls='--', label='prior sd of the head')
ax[1].axhline(M.SIG, color='#6B7280', lw=0.8, ls=':', label=f'head error sd ({M.SIG} m)')
ax[1].set_xlabel('well position ξ (m)'); ax[1].set_ylabel('head (m)')
ax[1].legend(frameon=False, fontsize=6.8, loc='upper left')
ax[1].set_title('(b) what a well can see', fontsize=9)
ax[2].plot(X, RS['ref_eig'], color=C_PAR, lw=1.8, label='parameters: I(z; y | ξ)')
ax[2].plot(X, RS['ref_goal'], color=C_GOAL, lw=1.8, label='toe position: I(q; y | ξ)')
for v, c in ((RS['opt_ref_param'], C_PAR), (RS['opt_ref_goal'], C_GOAL)):
    ax[2].axvline(v, color=c, lw=0.8, ls=':')
ax[2].set_xlabel('well position ξ (m)'); ax[2].set_ylabel('expected information gain (nats)')
ax[2].legend(frameon=False, fontsize=7, loc='upper right')
ax[2].set_title('(c) exact information of one well', fontsize=9)
fig.tight_layout(); fig.savefig('figD1_problem.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2: what the map delivers (map D)
z = np.load('dara_maps.npz'); cores = [z[f'arr_{i}'] for i in range(6)]
A = S.Affine(); mp = MapAff(cores, A)
fig, ax = plt.subplots(1, 3, figsize=(10.6, 3.3))
keys = ['A', 'B', 'C', 'D']
lab = [f"{k}: {LV[k]['label']}" for k in keys]
err = [LV[k]['val_err'] for k in keys]
cols = ['#9CA3AF', '#93C5FD', '#3B82F6', '#1E3A8A']
ax[0].bar(range(4), err, color=cols)
for i, k in enumerate(keys):
    ax[0].text(i, err[i] * 1.12, f"{err[i] * 100:.1f}%\nranks ≤ {LV[k]['rmax']}", ha='center', fontsize=6.6)
ax[0].set_yscale('log'); ax[0].set_ylim(5e-3, 1.5)
ax[0].set_xticks(range(4)); ax[0].set_xticklabels(['A\nraw', 'B\naffine', 'C\naffine', 'D\naffine'], fontsize=7)
ax[0].set_ylabel('relative error of √density on samples')
ax[0].set_title('(a) preconditioning makes the train accurate', fontsize=9)
yy = np.linspace(-0.3, 5.3, 600)
for xi, c in ((1000.0, C_GOAL), (2500.0, C_PAR)):
    h = M.head(xi, *R.z.T)
    py = fftconvolve(cic1(h, R.y0, R.dy, R.ny), gauss_kernel(M.SIG, R.dy), mode='same') / R.dy
    ax[1].plot(R.yg, py, color=c, lw=2.2, alpha=0.35)
    Xq = np.column_stack([np.full_like(yy, xi), yy])
    ax[1].plot(yy, np.exp(mp.log_lead(Xq) - mp.log_lead(Xq[:, :1])), color=c, lw=1.0, ls='--', label=f'ξ = {xi:.0f} m')
ax[1].set_xlim(-0.3, 5.3); ax[1].set_xlabel('head y (m)'); ax[1].set_ylabel('predictive density p(y | ξ)')
ax[1].legend(frameon=False, fontsize=7, title='thick: exact, dashed: map D', title_fontsize=6.8)
ax[1].set_title('(b) predictive density of the head', fontsize=9)
xi = 1000.0
h = M.head(xi, *R.z.T)
ky = gauss_kernel(M.SIG, R.dy); kq = gauss_kernel(M.TAU, R.dq)
uq = (R.Q - R.q0) / R.dq; iq = np.clip(np.floor(uq).astype(int), 0, R.nq - 2); wq = uq - iq
uy = (h - R.y0) / R.dy; iy = np.clip(np.floor(uy).astype(int), 0, R.ny - 2); wy = uy - iy
Hh = np.zeros((R.nq, R.ny))
for a, wa in ((0, 1 - wq), (1, wq)):
    for b, wb in ((0, 1 - wy), (1, wy)):
        np.add.at(Hh, (iq + a, iy + b), wa * wb)
P = fftconvolve(fftconvolve(Hh / len(h), kq[:, None], mode='same'), ky[None, :], mode='same') / (R.dq * R.dy)
qq = np.linspace(4.6, 7.6, 500)
ax[2].plot(R.qg, R.pq, color='#9CA3AF', lw=1.0, label='prior')
for yv, c in ((0.6, '#7C3AED'), (1.0, C_GOAL), (1.6, '#059669')):
    j = int(round((yv - R.y0) / R.dy)); col = P[:, j] / (P[:, j].sum() * R.dq)
    ax[2].plot(R.qg, col, color=c, lw=2.2, alpha=0.35)
    Xq = np.column_stack([np.full_like(qq, xi), np.full_like(qq, yv), qq])
    ax[2].plot(qq, np.exp(mp.log_lead(Xq) - mp.log_lead(Xq[:, :2])), color=c, lw=1.0, ls='--', label=f'head {yv} m')
ax[2].set_xlim(4.6, 7.6); ax[2].set_xlabel('goal q = ln(toe position / m)'); ax[2].set_ylabel('posterior density p(q | y, ξ)')
ax[2].legend(frameon=False, fontsize=6.8, title='well at 1 000 m; thick: exact', title_fontsize=6.8)
ax[2].set_title('(c) toe posterior for any measured head', fontsize=9)
fig.tight_layout(); fig.savefig('figD2_map.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 3: DARA-GO
fig, ax = plt.subplots(1, 3, figsize=(10.6, 3.4))
for k, c, a in (('B', '#93C5FD', 0.55), ('D', '#1E3A8A', 0.45)):
    d = LV[k]
    ax[0].fill_between(X, d['L'], d['U'], color=c, alpha=a, lw=0, label=f'map {k}: [L, U]')
    ax[1].fill_between(X, d['Lq'], d['Lq_plus_G'], color=c, alpha=a, lw=0, label=f'map {k}: [Lq, Lq + G]')
ax[0].plot(X, RS['ref_eig'], color=C_REF, lw=1.2, label='exact')
PM = next((k for k in 'ABCD' if LV[k]['argmax']['plug_goal'] != RS['opt_ref_goal'] and k != 'A'), 'B')
ax[0].plot(X, LV[PM]['plug'], 'o', ms=2.6, color='#DC2626', label=f'map {PM}, pure-map estimate')
ax[1].plot(X, RS['ref_goal'], color=C_REF, lw=1.2, label='exact')
ax[1].plot(X, LV[PM]['plug_goal'], 'o', ms=2.6, color='#DC2626', label=f'map {PM}, pure-map estimate')
for axx, key, top, dy in ((ax[0], 'cert_param', 2.24, 0.1), (ax[1], 'cert_goal', 1.5, 0.07)):
    for k, off, c in (('B', 0.0, '#60A5FA'), ('D', dy, '#1E3A8A')):
        sel = X[np.array(LV[k][key])]
        axx.plot(sel, np.full(len(sel), top + off), 's', ms=3.2, color=c, label=f'certified set, map {k}')
ax[0].set_ylim(0, 2.45); ax[1].set_ylim(0, 1.7)
ax[0].set_xlabel('well position ξ (m)'); ax[0].set_ylabel('information (nats)')
ax[1].set_xlabel('well position ξ (m)'); ax[1].set_ylabel('information on the toe (nats)')
ax[0].legend(frameon=False, fontsize=6.2, loc='lower center', ncol=2, columnspacing=0.8)
ax[1].legend(frameon=False, fontsize=6.2, loc='center right', bbox_to_anchor=(1.0, 0.55))
ax[0].set_title('(a) parameters: certified bracket', fontsize=9)
ax[1].set_title('(b) toe position: same gap', fontsize=9)
for k, c in zip(keys, cols):
    ax[2].plot(X, np.maximum(LV[k]['G'], 1e-4), '-o', ms=2.2, lw=1.1, color=c, label=f'map {k}')
ax[2].set_yscale('log'); ax[2].set_xlabel('well position ξ (m)'); ax[2].set_ylabel('gap G = KL(true ‖ map) (nats)')
ax[2].set_ylim(2e-3, 60); ax[2].legend(frameon=False, fontsize=6.8, ncol=4, loc='upper center', columnspacing=0.8, handlelength=1.4)
ax[2].set_title('(c) the gap measures the map error', fontsize=9)
fig.tight_layout(); fig.savefig('figD3_dara.png', dpi=200); plt.close(fig)
print('figures written')
