"""Figures of the RINDERTIMI-GO note (English labels). usage: python rgo_figs.py OUT_DIR

fig_scheme: the pipeline, in the spirit of Figure 2 of Yao et al. (NeurIPS 2025) but drawn for the coastal aquifer: reverse
diffusion with guidance (left), training of the denoising neural operator on the physical prior (right), and the path from
the data to the boundary conditions of the coupled model (bottom). Every thumbnail is a real field: prior samples, GRF
noise and the sampler states stored by rgo_fundps.py in res/rgo_case.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rgo_model as M  # noqa: E402

RES = os.path.join(HERE, 'res')
INK, MUTED, GRID = '#1f2328', '#5b6672', '#e3e6ea'
FS = 8.6
plt.rcParams.update({'font.size': FS, 'axes.titlesize': 9.4, 'axes.labelsize': 8.8, 'xtick.labelsize': FS,
                     'ytick.labelsize': FS, 'legend.fontsize': FS, 'font.family': 'DejaVu Sans',
                     'mathtext.fontset': 'dejavusans'})
# palette of the scheme: one hue per role
C = dict(zoom_f='#e4f2e6', zoom_e='#4f9a62', no_f='#d5cdf0', no_e='#5a4aa0', lik_f='#ffe7a8', lik_e='#c48a00',
         dat_f='#dbe7fb', dat_e='#3b6db3', out_f='#fde6dc', out_e='#c4563a', sim_f='#d9f0f0', sim_e='#24838a',
         obs='#c3c7cd', arrow='#2b3440')
STRIPE_CMAPS = ('GnBu', 'RdPu', 'YlGn', 'Blues')          # eta, qL, r, f
VL, VLH = 2.4, 2.0                                        # colour limits of the normalised stripes and head map


def style(ax):
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.grid(color=GRID, lw=0.7)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------------------------------------ drawing helpers (mm)
class Canvas:
    def __init__(self, w_mm, h_mm):
        self.W, self.H = w_mm, h_mm
        self.fig = plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4), dpi=300)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w_mm); self.ax.set_ylim(0, h_mm); self.ax.axis('off')
        self.ax.set_autoscale_on(False)

    def box(self, x, y, w, h, fc, ec, lw=1.0, r=1.6, z=1, ls='-'):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}', fc=fc, ec=ec, lw=lw,
                                         zorder=z, ls=ls))

    def text(self, x, y, s, size=FS, ha='center', va='center', color=INK, weight='normal', z=30, **kw):
        self.ax.text(x, y, s, fontsize=size, ha=ha, va=va, color=color, fontweight=weight, zorder=z, **kw)

    def arrow(self, x0, y0, x1, y1, c=None, lw=1.0, rad=0.0, ls='-', head='-|>', z=25):
        self.ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=z,
                         arrowprops=dict(arrowstyle=head, color=c or C['arrow'], lw=lw, shrinkA=0, shrinkB=0, ls=ls,
                                         connectionstyle=f'arc3,rad={rad}', mutation_scale=8))

    def line(self, xs, ys, c=None, lw=0.8, ls='-', z=5):
        self.ax.plot(xs, ys, color=c or C['arrow'], lw=lw, ls=ls, zorder=z, solid_capstyle='round')

    def circle(self, x, y, r, sym, fc='white', ec=None):
        self.ax.add_patch(Circle((x, y), r, fc=fc, ec=ec or C['arrow'], lw=0.9, zorder=26))
        self.text(x, y + 0.1, sym, size=9.5, z=27)

    def inset(self, x, y, w, h):
        return self.fig.add_axes([x / self.W, y / self.H, w / self.W, h / self.H])

    def card(self, x, y, w, h, fields, obs=None, z=10, off=1.0):
        """a stack of joint-function cards; fields[0] in front. Each card: four boundary stripes (eta, qL, r, P) above
        the head map h(x, t) (time to the right, sea at the bottom)."""
        n = len(fields)
        for k in range(n - 1, -1, -1):
            self._one(x - k * off, y + k * off, w, h, fields[k], obs if k == 0 else None, z + 2 * (n - k))

    def _one(self, x, y, w, h, a, obs, z):
        ax = self.ax
        ax.add_patch(Rectangle((x, y), w, h, fc='white', ec=INK, lw=0.5, zorder=z))
        pad = 0.35
        sh, gap = 0.085 * h, 0.022 * h
        top = y + h - pad
        for c in range(4):
            y1 = top - c * (sh + gap); y0 = y1 - sh
            v = a[..., 1 + c].mean(0)[None, :]
            if obs is not None and not obs['stripe'][c]:
                ax.add_patch(Rectangle((x + pad, y0), w - 2 * pad, sh, fc=C['obs'], ec='none', zorder=z + 1))
                continue
            ax.imshow(v, extent=(x + pad, x + w - pad, y0, y1), cmap=STRIPE_CMAPS[c], vmin=-VL, vmax=VL, aspect='auto',
                      interpolation='nearest', zorder=z + 1)
        hy1 = top - 4 * (sh + gap)
        ext = (x + pad, x + w - pad, y + pad, hy1)
        if obs is None:
            ax.imshow(a[..., 0], extent=ext, origin='lower', cmap='turbo', vmin=-VLH, vmax=VLH, aspect='auto',
                      interpolation='bilinear', zorder=z + 1)
        else:
            ax.add_patch(Rectangle((ext[0], ext[2]), ext[1] - ext[0], ext[3] - ext[2], fc='#e7e9ec', ec='none', zorder=z + 1))
            xs = ext[0] + (obs['t'] + 0.5) / M.NT * (ext[1] - ext[0])
            ys = ext[2] + (obs['x'] + 0.5) / M.NX * (ext[3] - ext[2])
            ax.scatter(xs, ys, c=obs['v'], cmap='turbo', vmin=-VLH, vmax=VLH, s=4.5, marker='s', lw=0, zorder=z + 2)


def show(a, sigma=None):
    """display scaling: noisy states are shown as the network sees them, c_in * a."""
    if sigma is None:
        return a
    return a / np.sqrt(1.0 + sigma ** 2)


# ------------------------------------------------------------------------------------------------ the thumbnails
def thumbnails(case):
    """the cards of the scheme: prior samples, and the states of the FunDPS run guided by the filtered rain (test case 0)."""
    import rgo_net as N
    with open(os.path.join(RES, 'rgo_norm.json')) as fh:
        st = json.load(fh)
    rng = np.random.default_rng(5)
    a_prior, _ = M.sample_prior(rng, 3)
    D = dict(h=a_prior[:, 0], eta=a_prior[:, 1, 0], qL=a_prior[:, 2, 0], r=a_prior[:, 3, 0], f=a_prior[:, 4, 0])
    prior = N.to_field(D, st)
    g = lambda k: case[k]
    T = dict(prior=[prior[0], prior[1]])
    s_init = float(g('snap_s_init'))
    T['noise'] = [show(g('snap_a_init')[0], s_init), show(g('snap_a_init')[1], s_init)]
    s40 = float(g('snap_s_41'))                    # noise level of the state after step 40
    T['a_t'] = [show(g('snap_a_40')[0], s40), show(g('snap_a_40')[1], s40)]
    s41 = float(M_sigma(42))                       # noise level of the state after step 41
    T['x0'] = [g('snap_x0_41')[0], g('snap_x0_41')[1]]
    T['a_unc'] = [show(g('snap_au_41')[0], s41), show(g('snap_au_41')[1], s41)]
    T['a_tm1'] = [show(g('snap_a_41')[0], s41), show(g('snap_a_41')[1], s41)]
    T['a0'] = [g('snap_a_79')[0], g('snap_a_79')[1]]
    # the observation of the guidance: the filtered rain f, complete; everything else is masked
    u = np.zeros((M.NX, M.NT, 5), np.float32)
    u[..., 4] = ((g('truth_f') - st['f_mean']) / st['f_sd'])[None, :]
    T['u'] = u
    T['u_obs'] = dict(x=np.array([], int), t=np.array([], int), v=np.array([]), stripe=(False, False, False, True))
    T['st'] = st
    return T


def M_sigma(i):
    import rgo_fundps as F
    return F.sigma_schedule()[i]


# ------------------------------------------------------------------------------------------------ figure 1: the scheme
def fig_scheme(path, case, scen='B'):
    T = thumbnails(case)
    cv = Canvas(170.0, 116.0)
    ax = cv.ax
    H = cv.H
    # ---------------- titles and the separator
    cv.text(4, H - 3.2, 'Reverse diffusion sampling with FunDPS guidance', ha='left', size=9.4, weight='bold')
    cv.text(123.5, H - 3.2, 'Training', ha='left', size=9.4, weight='bold')
    cv.line([121.4, 121.4], [31.5, H - 1.0], c='#7d8793', lw=0.9, ls=(0, (3, 2.2)))
    # ---------------- top row: a_N ... [a_t -> a_{t-1}] ... a_0
    cw, ch, cy = 13.0, 16.5, 81.0
    lab_y = cy + ch + 3.4
    cv.card(7.5, cy, cw, ch, T['noise'])
    cv.text(7.5 + cw / 2 - 0.5, lab_y, r'$a_N$', size=9.6)
    cv.text(7.5 + cw / 2 - 0.5, cy - 3.0, 'GRF noise', size=FS)
    cv.text(24.2, cy + ch / 2, '···', size=11, weight='bold')
    gx0, gx1 = 29.0, 79.0
    cv.box(gx0, cy - 2.4, gx1 - gx0, ch + 7.4, C['zoom_f'], C['zoom_e'], lw=0.9, r=1.2, z=2)
    cv.card(35.0, cy, cw, ch, T['a_t'])
    cv.text(35.0 + cw / 2 - 0.5, lab_y, r'$a_t$', size=9.6)
    cv.card(61.0, cy, cw, ch, T['a_tm1'])
    cv.text(61.0 + cw / 2 - 0.5, lab_y, r'$a_{t-1}$', size=9.6)
    cv.arrow(48.6, cy + ch / 2, 59.4, cy + ch / 2)
    cv.text(83.0, cy + ch / 2, '···', size=11, weight='bold')
    ox = 104.0
    cv.card(ox, cy, cw, ch, T['a0'])
    cv.text(ox + cw / 2 - 0.5, lab_y, r'$a_0$', size=9.6)
    cv.text(ox + cw / 2 - 0.9, cy - 3.0, 'reconstructed', size=FS)
    cv.arrow(26.6, cy + ch / 2, 33.6, cy + ch / 2)
    cv.arrow(86.4, cy + ch / 2, 102.6, cy + ch / 2)
    # ---------------- the zoom box
    zx0, zx1, zy0, zy1 = 3.0, 101.0, 30.5, 72.5
    cv.line([gx0, zx0], [cy - 2.4, zy1], c='#6b7a70', lw=0.6)
    cv.line([gx1, zx1], [cy - 2.4, zy1], c='#6b7a70', lw=0.6)
    cv.box(zx0, zy0, zx1 - zx0, zy1 - zy0, C['zoom_f'], C['zoom_e'], lw=1.0, r=1.4, z=2)
    cv.text(zx1 - 2.0, zy0 + 3.0, 'FunDPS', ha='right', size=9.6, weight='bold', color='#2f6b3f')
    zw, zh, zcy = 12.0, 15.0, 50.5
    zlab = zcy + zh + 3.2
    xs = dict(at=7.0, no=23.0, x0=47.0, au=65.0, mi=82.2, atm1=87.6)
    cv.card(xs['at'], zcy, zw, zh, T['a_t'][:1] + T['a_t'][1:])
    cv.text(xs['at'] + zw / 2 - 0.5, zlab, r'$a_t$', size=9.6)
    cv.box(xs['no'], zcy + 1.2, 20.0, zh - 2.4, C['no_f'], C['no_e'], lw=1.0, r=1.4, z=12)
    cv.text(xs['no'] + 10.0, zcy + zh / 2 + 2.4, 'Neural', size=FS)
    cv.text(xs['no'] + 10.0, zcy + zh / 2 - 1.2, 'operator', size=FS)
    cv.text(xs['no'] + 10.0, zcy + zh / 2 - 4.8, r'$D_\theta$ (FNO)', size=FS)
    cv.arrow(xs['at'] + zw + 0.2, zcy + zh / 2, xs['no'] - 0.2, zcy + zh / 2)
    cv.arrow(xs['no'] + 20.2, zcy + zh / 2, xs['x0'] - 1.2, zcy + zh / 2)
    cv.card(xs['x0'], zcy, zw, zh, T['x0'])
    cv.text(xs['x0'] + zw / 2 - 0.5, zlab, r'$\hat a_0$', size=9.6)
    cv.arrow(xs['x0'] + zw + 0.2, zcy + zh / 2, xs['au'] - 1.2, zcy + zh / 2)
    cv.text(xs['au'] + zw / 2 - 0.5, zcy - 2.6, 'Heun step', size=FS, color=MUTED)
    cv.card(xs['au'], zcy, zw, zh, T['a_unc'])
    cv.text(xs['au'] + zw / 2 - 0.5, zlab, r'$\hat a_{t-1}$', size=9.6)
    cv.circle(xs['mi'], zcy + zh / 2, 1.9, '−')
    cv.arrow(xs['au'] + zw + 0.2, zcy + zh / 2, xs['mi'] - 1.9, zcy + zh / 2)
    cv.card(xs['atm1'], zcy, zw - 1.0, zh, [T['a_tm1'][0]])
    cv.text(xs['atm1'] + (zw - 1.0) / 2, zlab, r'$a_{t-1}$', size=9.6)
    cv.arrow(xs['mi'] + 1.9, zcy + zh / 2, xs['atm1'] - 0.2, zcy + zh / 2)
    cv.text((xs['mi'] + xs['atm1']) / 2 + 0.9, zcy + zh / 2 + 2.6, r'$\Pi$', size=FS, color=MUTED)
    # second row: observations -> likelihood -> gradient
    uy, uh = 33.0, 13.0
    cv.card(29.0, uy, 11.0, uh, [T['u']], obs=T['u_obs'])
    cv.text(18.0, uy + uh / 2 + 3.4, 'observation', size=FS)
    cv.text(18.0, uy + uh / 2 - 0.2, r'$u = \mathcal{A}(a)$', size=FS)
    cv.text(18.0, uy + uh / 2 - 3.8, r'filtered rain $f$', size=FS, color=MUTED)
    lx0, lx1, ly0, ly1 = 44.0, 76.0, 33.6, 45.2
    cv.box(lx0, ly0, lx1 - lx0, ly1 - ly0, C['lik_f'], C['lik_e'], lw=1.0, r=1.4, z=12)
    cv.text((lx0 + lx1) / 2, ly1 - 3.0, r'Likelihood $p(u\,|\,a)$', size=FS)
    cv.text((lx0 + lx1) / 2, ly0 + 3.2, r'$\|u - \mathcal{A}(\hat a_0)\|^2_w$', size=FS)
    cv.arrow(40.4, uy + uh / 2, lx0 - 0.2, uy + uh / 2)
    cv.arrow(xs['x0'] + zw / 2, zcy - 0.2, xs['x0'] + zw / 2, ly1 + 0.2)
    cv.circle(xs['mi'], (ly0 + ly1) / 2, 1.9, '∂')
    cv.arrow(lx1 + 0.2, (ly0 + ly1) / 2, xs['mi'] - 1.9, (ly0 + ly1) / 2)
    cv.arrow(xs['mi'], (ly0 + ly1) / 2 + 1.9, xs['mi'], zcy + zh / 2 - 1.9)
    cv.text(xs['mi'] + 2.6, (ly0 + ly1) / 2 + 5.6, r'$\zeta_t\nabla_{a}$', ha='left', size=FS, color=MUTED)
    # ---------------- training (right)
    tx0, tx1 = 123.0, 167.4
    tcx = (tx0 + tx1) / 2
    cv.box(tx0, 99.0, tx1 - tx0, 12.2, C['dat_f'], C['dat_e'], lw=1.0, r=1.4, z=2)
    cv.text(tcx, 107.9, 'Simulator prior', size=FS, weight='bold')
    cv.text(tcx, 104.4, 'rain, vadose zone, aquifer', size=FS)
    cv.text(tcx, 101.0, 'Excel: K, cover, boundary', size=FS)
    cv.arrow(tcx, 98.8, tcx, 95.6)
    cv.box(tx0, 73.5, tx1 - tx0, 21.8, '#eef4fd', C['dat_e'], lw=1.0, r=1.4, z=2)
    cv.card(127.4, 76.0, 12.0, 15.0, T['prior'])
    cv.text(154.0, 89.6, 'samples', size=FS)
    cv.text(154.0, 86.0, r'$a=(h,\eta,q_L,r,f)$', size=FS)
    cv.text(154.0, 81.4, '24,000', size=FS, color=MUTED)
    cv.text(154.0, 78.0, 'from the prior', size=FS, color=MUTED)
    nx = 148.0                                     # axis of the noising and training column
    cv.circle(nx, 67.6, 1.9, '+')
    cv.arrow(nx, 73.3, nx, 69.5)
    cv.box(tx0, 62.8, 20.4, 9.6, C['dat_f'], C['dat_e'], lw=1.0, r=1.2, z=2)
    cv.text(tx0 + 10.2, 69.6, 'GRF noise', size=FS)
    cv.text(tx0 + 10.2, 65.6, r'$\xi\sim\mathcal{N}(0,C)$', size=FS)
    cv.arrow(tx0 + 20.6, 67.6, nx - 1.9, 67.6)
    cv.text(nx + 2.6, 70.4, r'$\sigma\xi$', ha='left', size=FS, color=MUTED)
    cv.box(nx - 19.5, 49.0, 39.0, 10.6, C['no_f'], C['no_e'], lw=1.0, r=1.4, z=2)
    cv.text(nx, 56.6, r'Neural operator $D_\theta$', size=FS)
    cv.text(nx, 52.4, 'FNO, 1.6 M parameters', size=FS, color=MUTED)
    cv.arrow(nx, 65.7, nx, 59.8)
    cv.box(nx - 19.5, 33.6, 39.0, 10.6, C['lik_f'], C['lik_e'], lw=1.0, r=1.4, z=2)
    cv.text(nx, 41.0, 'Optimize the EDM loss', size=FS)
    cv.text(nx, 37.0, r'$\lambda(\sigma)\,\|D_\theta - a\|^2$', size=FS)
    cv.arrow(nx - 3.0, 48.8, nx - 3.0, 44.4)
    cv.arrow(nx + 2.0, 44.4, nx + 2.0, 48.8)
    cv.text(nx + 3.0, 46.6, r'$\nabla_\theta$', ha='left', size=FS, color=MUTED)
    rx = 169.0
    cv.line([tx1 + 0.2, rx, rx], [84.4, 84.4, 38.9], c=C['arrow'], lw=0.9)
    cv.arrow(rx, 38.9, nx + 19.7, 38.9)
    # ---------------- bottom band: data -> ensemble update with the solver -> boundary conditions -> coupled model
    by0, by1 = 2.0, 27.0
    dx0, dx1 = 3.0, 36.0
    cv.box(dx0, by0, dx1 - dx0, by1 - by0, C['dat_f'], C['dat_e'], lw=1.0, r=1.4, z=2)
    dcx = (dx0 + dx1) / 2
    cv.text(dcx, by1 - 3.2, 'Data', size=FS, weight='bold')
    cv.text(dcx, by1 - 7.0, 'rain: E-OBS,', size=FS)
    cv.text(dcx, by1 - 10.6, 'ERA5-Land, IGJEO', size=FS)
    cv.text(dcx, by1 - 15.0, r'heads $h(x_j,t)$', size=FS)
    cv.text(dcx, by1 - 18.6, r'tide gauge $\eta(t)$', size=FS)
    cv.text(dcx, by1 - 22.0, '(by scenario)', size=FS, color=MUTED)
    cv.arrow(18.0, by1 + 0.2, 18.0, zy0 + 2.4)
    cv.text(19.2, 29.0, r'$f = k_\tau * P$', ha='left', size=FS, color=MUTED)
    # ensemble update with the exact solver
    ex0, ex1 = 40.0, 67.0
    cv.box(ex0, by0, ex1 - ex0, by1 - by0, C['zoom_f'], C['zoom_e'], lw=1.0, r=1.4, z=2)
    ecx = (ex0 + ex1) / 2
    cv.text(ecx, by1 - 3.2, 'Ensemble', size=FS, weight='bold')
    cv.text(ecx, by1 - 7.0, 'update (ES)', size=FS)
    cv.text(ecx, by1 - 10.6, 'with the exact', size=FS)
    cv.text(ecx, by1 - 14.2, r'solver $\mathcal{S}$', size=FS)
    cv.text(ecx, by1 - 18.6, 'heads and tide', size=FS, color=MUTED)
    cv.text(ecx, by1 - 22.2, 'enter here', size=FS, color=MUTED)
    cv.arrow(dx1 + 0.2, 9.0, ex0 - 0.2, 9.0)
    # the FunDPS ensemble comes down the corridor and into the update
    xc = ox + cw / 2 - 0.5
    cv.line([xc, xc, ecx + 6.0], [cy - 5.2, 29.0, 29.0], c=C['arrow'], lw=1.0, z=24)
    cv.arrow(ecx + 6.0, 29.0, ecx + 6.0, by1 + 0.2)
    cv.text(xc + 1.0, 52.0, 'FunDPS ensemble', ha='left', size=FS, color=MUTED, rotation=90)
    # boundary-condition panel with four inset plots
    px0, px1 = 71.0, 128.0
    cv.box(px0, by0, px1 - px0, by1 - by0, C['out_f'], C['out_e'], lw=1.0, r=1.4, z=2)
    cv.text((px0 + px1) / 2, by1 - 3.0, 'Boundary conditions (90%)', size=FS, weight='bold')
    cv.arrow(ex1 + 0.2, (by0 + by1) / 2, px0 - 0.2, (by0 + by1) / 2)
    bc_insets(cv, case, scen, px0, by0, w=(px1 - px0 - 5.0) / 2)
    # coupled model
    sx0, sx1 = 132.0, 167.4
    cv.box(sx0, by0, sx1 - sx0, by1 - by0, C['sim_f'], C['sim_e'], lw=1.0, r=1.4, z=2)
    scx = (sx0 + sx1) / 2
    cv.text(scx, by1 - 3.2, 'Coupled', size=FS, weight='bold')
    cv.text(scx, by1 - 6.8, 'simulation', size=FS, weight='bold')
    cv.text(scx, by1 - 10.8, 'density-driven', size=FS)
    cv.text(scx, by1 - 14.4, 'flow, salt,', size=FS)
    cv.text(scx, by1 - 18.0, 'interface, wells', size=FS)
    cv.text(scx, by1 - 22.0, 'one per sample', size=FS, color=MUTED)
    cv.arrow(px1 + 0.2, (by0 + by1) / 2, sx0 - 0.2, (by0 + by1) / 2)
    cv.fig.savefig(path, dpi=300)
    plt.close(cv.fig)


def bc_insets(cv, case, scen, px0, by0, w=34.5):
    """the four reconstructed boundary conditions of scenario B (FunDPS with the rain, then the ensemble update with the
    solver): 90% band and median, truth dashed."""
    wk = np.arange(M.NT)
    spec = [('eta', r'$\eta(t)$', wk), ('qL', r'$q_L(t)$', wk), ('r', r'$r(t)$', wk), ('h0', r'$h_0(x)$', M.XC / 1000.0)]
    for j, (k, lab, xx) in enumerate(spec):
        col, row = j % 2, j // 2
        x, y = px0 + 2.0 + col * (w + 1.0), by0 + 1.6 + (1 - row) * 9.9
        ia = cv.inset(x, y, w, 8.6)
        if k == 'h0':
            fs, tv = case[f'{scen}_hyb_h0'], case['truth_h'][:, 0]
        else:
            fs, tv = case[f'{scen}_hyb_{k}'], case[f'truth_{k}']
        lo, md, hi = np.quantile(fs, [0.05, 0.5, 0.95], axis=0)
        ia.fill_between(xx, lo, hi, color='#f1a98f', alpha=0.75, lw=0)
        ia.plot(xx, md, color=C['out_e'], lw=0.9)
        ia.plot(xx, tv, color=INK, lw=0.7, ls=(0, (2, 1.2)))
        ia.set_xticks([]); ia.set_yticks([])
        for sp in ia.spines.values():
            sp.set_color('#c9a093'); sp.set_lw(0.5)
        ia.set_facecolor('white')
        ia.set_xlim(xx[0], xx[-1])
        ymin, ymax = min(lo.min(), tv.min()), max(hi.max(), tv.max())
        ia.set_ylim(ymin - 0.05 * (ymax - ymin), ymax + 0.75 * (ymax - ymin))
        ia.text(0.02, 0.93, lab, transform=ia.transAxes, ha='left', va='top', fontsize=FS, color=INK)


# ------------------------------------------------------------------------------------------------ results
SC_LAB = {'A': 'A: rain only', 'B': 'B: rain + 4 loggers', 'C': 'C: B + tide gauge'}
CH_COL = dict(eta='#2563b0', qL='#6a4fb3', r='#2E8B57', h0='#24838a')


def fig_results(path, case):
    """test case 0 in the three scenarios: exact posterior 90% band, RINDERTIMI-GO 90% band and median (FunDPS with
    the rain in A; then the ensemble update with the solver in B and C), plain FunDPS guidance (B, C), truth."""
    fig, axs = plt.subplots(3, 4, figsize=(17.0 / 2.54, 13.2 / 2.54), dpi=300)
    wk = np.arange(M.NT)
    cols = [('eta', r'sea level $\eta$ (cm)', 100.0, wk), ('qL', r'inflow $q_L$ (m²/d)', 1.0, wk),
            ('r', r'recharge $r$ (mm/d)', 1.0, wk), ('h0', 'initial head $h_0$ (cm),\nminus exact mean', 100.0, M.XC / 1000.0)]
    ours = dict(A='A_fun', B='B_hyb', C='C_hyb')

    def get(prefix, k):
        return case[f'{prefix}_{k}']
    for i, sc in enumerate('ABC'):
        for j, (k, lab, f, xx) in enumerate(cols):
            ax = axs[i, j]
            es = get(f'{sc}_ex', k) * f
            fs = get(ours[sc], k) * f
            tv = (case['truth_h'][:, 0] if k == 'h0' else case[f'truth_{k}']) * f
            ps = get(f'{sc}_pure', k) * f if (sc != 'A' and f'{sc}_pure_eta' in case) else None
            if k == 'h0':                        # the head profile: departure from the exact posterior mean
                ref = es.mean(0)
                es, fs, tv = es - ref, fs - ref, tv - ref
                ps = None if ps is None else ps - ref
            elo, ehi = np.quantile(es, [0.05, 0.95], axis=0)
            flo, fmd, fhi = np.quantile(fs, [0.05, 0.5, 0.95], axis=0)
            ax.fill_between(xx, elo, ehi, color='#cfd5dc', lw=0, label='exact posterior, 90%')
            c = CH_COL[k]
            if ps is not None:
                plo, phi = np.quantile(ps, [0.05, 0.95], axis=0)
                lc = matplotlib.colors.to_hex(np.array(matplotlib.colors.to_rgb(c)) * 0.45 + 0.55)
                ax.plot(xx, plo, color=lc, lw=0.8, ls=(0, (4, 1.5, 1, 1.5)), label='plain FunDPS, 90%')
                ax.plot(xx, phi, color=lc, lw=0.8, ls=(0, (4, 1.5, 1, 1.5)))
            ax.plot(xx, flo, color=c, lw=0.9, label='RINDËRTIMI-GO, 90%')
            ax.plot(xx, fhi, color=c, lw=0.9)
            ax.plot(xx, fmd, color=c, lw=0.6, ls=(0, (1, 1)))
            ax.plot(xx, tv, color=INK, lw=0.8, ls=(0, (3, 1.6)), label='truth')
            if k == 'eta' and sc == 'C':
                rows = case['C_rows']; yv = case['C_y']
                sel = rows[:, 0] == 1
                ax.plot(rows[sel, 1], yv[sel] * f, '.', ms=2.0, color=INK, label='tide gauge')
            style(ax)
            ax.set_xlim(xx[0], xx[-1])
            if i == 0:
                ax.set_title(lab, fontsize=FS, color=INK)
            if i == 2:
                ax.set_xlabel('week' if k != 'h0' else 'x (km)', fontsize=FS)
            else:
                ax.set_xticklabels([])
            if j == 0:
                ax.text(-0.42, 0.5, SC_LAB[sc], transform=ax.transAxes, rotation=90, ha='center', va='center',
                        fontsize=FS, color=INK, fontweight='bold')
            ax.tick_params(labelsize=FS, length=2.5, pad=1.5)
    h, l = axs[2, 0].get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, frameon=False, fontsize=FS, bbox_to_anchor=(0.53, -0.005),
               columnspacing=1.2, handlelength=2.2)
    fig.subplots_adjust(left=0.1, right=0.99, top=0.92, bottom=0.18, hspace=0.18, wspace=0.34)
    fig.savefig(path, dpi=300); plt.close(fig)


def fig_ladder(path, ev):
    """(a) posterior spread relative to the prior: exact against RINDERTIMI-GO, per boundary condition and scenario;
    (b) coverage of the 90% intervals, with plain FunDPS guidance for B and C."""
    fig = plt.figure(figsize=(17.0 / 2.54, 6.0 / 2.54), dpi=300)
    ax = fig.add_axes([0.075, 0.25, 0.5, 0.64]); bx = fig.add_axes([0.66, 0.25, 0.33, 0.64])
    chans = [('eta', r'$\eta$'), ('qL', r'$q_L$'), ('r', r'$r$'), ('h0', r'$h_0$')]
    pr = ev['prior_sd']
    meth = dict(A='fundps_A', B='hybrid_B', C='hybrid_C')
    shades = {'A': 0.45, 'B': 0.72, 'C': 1.0}
    w = 0.12
    for j, (k, lab) in enumerate(chans):
        base = np.array(matplotlib.colors.to_rgb(CH_COL[k]))
        for i, sc in enumerate('ABC'):
            a = ev['methods'][meth[sc]]['agg'][k]
            x = j + (i - 1) * 2.25 * w
            ce = base * shades[sc] + (1 - shades[sc])
            ax.bar(x - w / 2, a['sd_e'] / pr[k], width=w, color=ce, edgecolor='none', zorder=3)
            ax.bar(x + w / 2, a['sd_ratio'] * a['sd_e'] / pr[k], width=w, facecolor='white', edgecolor=ce, lw=1.0,
                   hatch='//////', zorder=3)
            ax.text(x, -0.07, sc, ha='center', va='top', fontsize=FS, color=MUTED, transform=ax.get_xaxis_transform())
    ax.set_xticks(range(len(chans))); ax.set_xticklabels([l for _, l in chans], fontsize=9.4)
    ax.tick_params(axis='x', pad=14, length=0)
    ax.set_ylabel('posterior sd / prior sd', fontsize=FS)
    ax.set_ylim(0, 1.2); style(ax); ax.grid(axis='x', visible=False)
    ax.set_title('(a) How much each condition narrows', loc='left', fontsize=9.4, color=INK)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color='#8b95a1', label='exact'),
                       Patch(facecolor='white', edgecolor='#8b95a1', hatch='//////', label='RINDËRTIMI-GO')],
              loc='upper right', frameon=False, fontsize=FS, ncol=2, bbox_to_anchor=(1.0, 1.05))
    for j, (k, lab) in enumerate(chans):
        for i, sc in enumerate('ABC'):
            a = ev['methods'][meth[sc]]['agg'][k]
            y = j + (i - 1) * 0.24
            bx.plot([a['cov_e'], a['cov_f']], [y, y], color='#c9d1d9', lw=1.0, zorder=2)
            bx.plot(a['cov_e'], y, 'o', ms=4.2, mfc='white', mec=CH_COL[k], mew=1.0, zorder=3)
            bx.plot(a['cov_f'], y, 'o', ms=4.2, color=CH_COL[k], zorder=4)
            if sc != 'A' and ev['methods'][f'pure_{sc}']['agg']:
                pp = ev['methods'][f'pure_{sc}']['agg'][k]['cov_f']
                bx.plot(pp, y, 'x', ms=4.0, color=CH_COL[k], mew=1.0, zorder=4)
            bx.text(0.03, y, sc, fontsize=FS, color=MUTED, va='center', ha='left')
    bx.axvline(0.9, color=INK, lw=0.8, ls=(0, (3, 2)))
    bx.set_yticks(range(len(chans))); bx.set_yticklabels([l for _, l in chans], fontsize=9.4)
    bx.set_xlim(0.0, 1.04); bx.invert_yaxis()
    bx.set_xlabel('coverage of the 90% interval', fontsize=FS)
    style(bx); bx.grid(axis='y', visible=False)
    bx.set_title('(b) Coverage', loc='left', fontsize=9.4, color=INK)
    bx.plot([], [], 'o', ms=4.2, mfc='white', mec=INK, label='exact')
    bx.plot([], [], 'o', ms=4.2, color=INK, label='RINDËRTIMI-GO')
    bx.plot([], [], 'x', ms=4.0, color=INK, mew=1.0, label='plain FunDPS')
    bx.legend(loc='center left', frameon=False, fontsize=FS, bbox_to_anchor=(0.1, 0.5), ncol=1, handletextpad=0.3)
    fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ Fushe-Kuqe boundary map
FK_JSON = os.path.join(HERE, '..', 'shiu_go', 'res', 'shiu_fk.json')
DER = os.path.join(HERE, '..', '..', 'chloride_fk', 'derived')
BC_COL = dict(sea='#2563b0', hill='#9a6b3c', east='#6a4fb3', south='#e07b22', north='#9a6b3c', rech='#cfe8c9',
              rech_e='#4f9a62', wells=INK, ic='#24838a', obs='#c48a00')


def grid_image(cx, cy, val, dx):
    xs = np.round(np.asarray(cx) / dx).astype(int); ys = np.round(np.asarray(cy) / dx).astype(int)
    x0, y0 = xs.min(), ys.min()
    img = np.full((ys.max() - y0 + 1, xs.max() - x0 + 1), np.nan)
    img[ys - y0, xs - x0] = val
    return img, [(x0 - 0.5) * dx, (xs.max() + 0.5) * dx, (y0 - 0.5) * dx, (ys.max() + 0.5) * dx]


def fk_geometry():
    with open(FK_JSON) as fh:
        F = json.load(fh)
    g = F['grid']
    cx, cy, sea = np.asarray(g['cx']), np.asarray(g['cy']), np.asarray(g['sea']) == 1
    rows = np.unique(cy)
    west = np.zeros(len(cx), bool); east = np.zeros(len(cx), bool)
    for y in rows:
        k = np.flatnonzero(cy == y)
        west[k[np.argmin(cx[k])]] = True; east[k[np.argmax(cx[k])]] = True
    north = cy == cy.max()
    import csv
    with open(os.path.join(DER, 'origin.csv')) as fh:
        o = next(csv.DictReader(fh))
    return dict(F=F, cx=cx, cy=cy, dx=g['dx'], sea=sea, hill=west & ~sea, east=east & ~north, north=north,
                x0=float(o['x0_m']), y0=float(o['y0_m']))


def graticule(G, lons, lats):
    """0.1 degree lines in the model frame (km, Gauss-Krueger zone 4 minus the origin of the workbook)."""
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:4326', 'EPSG:28404', always_xy=True)
    out = []
    for lo in lons:
        la = np.linspace(lats[0], lats[-1], 60)
        x, y = tr.transform(np.full_like(la, lo), la)
        out.append(((x - G['x0']) / 1000, (y - G['y0']) / 1000, f'{lo:.1f}°E'))
    for la in lats:
        lo = np.linspace(lons[0], lons[-1], 60)
        x, y = tr.transform(lo, np.full_like(lo, la))
        out.append(((x - G['x0']) / 1000, (y - G['y0']) / 1000, f'{la:.1f}°N'))
    return out


def fig_fk_bc(path):
    G = fk_geometry(); F = G['F']
    fig = plt.figure(figsize=(17.0 / 2.54, 13.2 / 2.54), dpi=300)
    ax = fig.add_axes([0.07, 0.06, 0.42, 0.9])
    cx, cy, dx = G['cx'], G['cy'], G['dx']
    img, ext = grid_image(cx, cy, np.ones(len(cx)), dx)
    ax.imshow(img, origin='lower', extent=ext, cmap=matplotlib.colors.ListedColormap([BC_COL['rech']]), vmin=0, vmax=1,
              interpolation='nearest', zorder=1)
    ga = F['grid_all']
    gcx, gcy = np.asarray(ga['cx']), np.asarray(ga['cy'])
    s = gcy < 24.0
    img2, ext2 = grid_image(gcx[s], gcy[s], np.ones(s.sum()), dx)
    ax.imshow(img2, origin='lower', extent=ext2, cmap=matplotlib.colors.ListedColormap(['#e6ebe4']), vmin=0, vmax=1,
              interpolation='nearest', zorder=1)
    import pandas as pd
    sh = pd.read_csv(os.path.join(DER, 'shoreline_polyline.csv'))
    for seg, d in sh.groupby('segment'):
        ax.plot(d['x_km'], d['y_km'], color='#7fa7d6', lw=0.9, zorder=2)
    for (xx, yy, lab) in graticule(G, np.round(np.arange(19.5, 19.95, 0.1), 1), np.round(np.arange(41.6, 42.05, 0.1), 1)):
        ax.plot(xx, yy, color='#8fb8de', lw=0.5, ls=(0, (2, 2)), zorder=2)
        lab = lab.replace('°E', '° E').replace('°N', '° N')
        if lab.endswith('E') and -6.0 < np.interp(53.9, yy, xx) < 18.0:
            ax.text(np.interp(53.9, yy, xx) + 0.3, 53.9, lab, fontsize=FS, color='#5d88b8', ha='left', va='center')
        if lab.endswith('N') and 21.0 < np.interp(-6.2, xx, yy) < 53.0:
            ax.text(-6.2, np.interp(-6.2, xx, yy) + 0.4, lab, fontsize=FS, color='#5d88b8', ha='left', va='bottom')
    m = 1.6
    ax.plot(cx[G['sea']] - 0.12, cy[G['sea']], 's', ms=m, color=BC_COL['sea'], zorder=4, lw=0)
    ax.plot(cx[G['hill']] - 0.12, cy[G['hill']], 's', ms=m, color=BC_COL['hill'], zorder=4, lw=0)
    ax.plot(cx[G['east']] + 0.12, cy[G['east']], 's', ms=m, color=BC_COL['east'], zorder=4, lw=0)
    ax.plot(cx[G['north']], cy[G['north']] + 0.12, 's', ms=m, color=BC_COL['north'], zorder=4, lw=0)
    xs24 = cx[cy == cy.min()]
    ax.plot([xs24.min() - 0.15, xs24.max() + 0.15], [23.85, 23.85], color=BC_COL['south'], lw=1.6, ls=(0, (3, 1.6)), zorder=4)
    W = F['wells']
    ax.plot(W['x_km'], W['y_km'], 'o', ms=2.0, color=INK, zorder=5, lw=0)
    b3 = F['S4']['best3']
    for wid, x, y in zip(b3['wells'], b3['x'], b3['y']):
        ax.plot(x, y, '^', ms=6.5, mfc='#ffd166', mec=INK, mew=0.8, zorder=6)
        ax.text(x + 0.55, y + 0.25, wid, fontsize=FS, color=INK, zorder=7)
    v2 = F['S4']['new_north_plain']
    ax.plot(v2['x_km'], v2['y_km'], '*', ms=11, mfc='white', mec=INK, mew=0.8, zorder=7)
    ax.text(v2['x_km'] + 0.6, v2['y_km'] + 0.4, 'V2', fontsize=FS, color=INK, zorder=7)
    import csv
    with open(os.path.join(DER, 'places.csv'), encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            x, y = float(r['x_km']), float(r['y_km'])
            if r['name'] not in ('Lezhë', 'Laç', 'Milot', 'Mamurras'):
                continue
            ax.plot(x, y, 's', ms=3, color=MUTED, zorder=5)
            ax.text(x + 0.5, y - 0.1, r['name'], fontsize=FS, color=MUTED, va='center', zorder=5)
    ax.text(-3.0, 49.0, 'Adriatic Sea', fontsize=FS, color='#2563b0', rotation=90, ha='center', va='center', style='italic')
    ax.text(13.6, 23.2, 'southern aquifer,\noutside the model', fontsize=FS, color=MUTED, ha='center', va='top', linespacing=1.2)
    ax.set_xlim(-6.5, 18.5); ax.set_ylim(20.0, 54.6)
    ax.set_aspect('equal')
    ax.set_xlabel('x (km)'); ax.set_ylabel('y (km)')
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.set_title('(a) Where each condition enters', loc='left', color=INK)
    # (b) the list of boundary conditions as coloured cards
    bx = fig.add_axes([0.505, 0.0, 0.495, 1.0]); bx.set_xlim(0, 100); bx.set_ylim(0, 100); bx.axis('off')
    bx.text(1.0, 97.4, '(b) The conditions and their data', fontsize=9.4, color=INK, va='top')
    cards = [
        ('sea', 'Sea: Dirichlet', r'$\phi=0$ at the shoreline, with sea level $\eta(t)$', 'tide gauge or sea-level product; reconstructed'),
        ('east', 'East margin: Neumann', r'$T\,\partial_n h = q_E(t)$ (inflow positive)', 'not measured; reconstructed (prior around 0)'),
        ('south', 'Model cut at y = 24 km: Neumann', r'$T\,\partial_n h = q_S(t)$', 'not measured; reconstructed from heads'),
        ('hill', 'Hills and northern margin', 'no flow, as in the calibrated model', 'checked with the head residuals'),
        ('rech', 'Land surface: areal source', r'$r = \kappa(x)\, f_{\tau(x)}(P) + e$', 'rain: E-OBS, ERA5-Land, IGJEO; τ from cover'),
        ('wells', 'Wells: point sources', r'$Q_j(t)$', 'no records yet; to be requested from the operator'),
        ('ic', 'Initial condition', r'$h_0(x,y)$, interface $\zeta_0$', 'calibrated steady state + GRF'),
        ('obs', 'Head observations', '      loggers P3, A3, A13', '      wells with K in the Excel workbook (43; scale)'),
    ]
    y, hc, gap = 92.5, 10.0, 1.15
    for key, title, eq, src_ in cards:
        col = BC_COL['rech_e'] if key == 'rech' else BC_COL[key]
        fc = BC_COL['rech'] if key == 'rech' else matplotlib.colors.to_hex(np.array(matplotlib.colors.to_rgb(col)) * 0.16 + 0.84)
        bx.add_patch(FancyBboxPatch((1.0, y - hc), 98.0, hc, boxstyle='round,pad=0,rounding_size=1.2', fc=fc, ec=col, lw=1.0))
        bx.add_patch(Rectangle((1.0, y - hc), 2.2, hc, fc=col, ec='none'))
        bx.text(5.0, y - 1.5, title, fontsize=FS, fontweight='bold', color=INK, va='top')
        bx.text(5.0, y - 4.4, eq, fontsize=FS, color=INK, va='top')
        bx.text(5.0, y - 7.2, src_, fontsize=FS, color=MUTED, va='top')
        if key == 'obs':
            bx.plot(6.6, y - 5.55, '^', ms=6.0, mfc='#ffd166', mec=INK, mew=0.8)
            bx.plot(61.0, y - 5.55, '*', ms=9.0, mfc='white', mec=INK, mew=0.8)
            bx.text(64.0, y - 4.4, 'V2 (new)', fontsize=FS, color=INK, va='top')
            bx.plot(6.6, y - 8.35, 'o', ms=2.6, color=INK, lw=0)
        y -= hc + gap
    fig.savefig(path, dpi=300); plt.close(fig)


def main(out, res_dir=None):
    global RES
    if res_dir:
        RES = res_dir
    os.makedirs(out, exist_ok=True)
    case = dict(np.load(os.path.join(RES, 'rgo_case.npz'), allow_pickle=False))
    fig_scheme(os.path.join(out, 'fig_scheme.png'), case)
    fig_fk_bc(os.path.join(out, 'fig_fk_bc.png'))
    with open(os.path.join(RES, 'rgo_eval.json')) as fh:
        ev = json.load(fh)
    fig_results(os.path.join(out, 'fig_results.png'), case)
    fig_ladder(os.path.join(out, 'fig_ladder.png'), ev)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'figs'))
