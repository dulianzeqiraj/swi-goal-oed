"""One pore-scale run of the KAOS-GO experiment: flow through a periodic cell of randomly placed cylinders under a uniform
body force.  Spin-up, sampling of the cell means and of the time-averaged fields, and (optionally) the largest Lyapunov
exponent from a twin run with renormalisation (Benettin).

usage: python kaos_run.py --out run.npz [--L 384 --a 12 --n 64 --gap 4 --seed 1] --nu 0.01 --g 6e-6
                          [--spin 40000 --samp 60000 --every 20 --init state.npz --state state_out.npz --lyap 0]
"""
import argparse
import json
import time

import numpy as np

import lbm


def geometry(L, a, n, gap, seed, square=False, scale=1.0):
    if scale != 1.0:                       # the same arrangement on a finer lattice: base cell L/scale, radius a/scale
        pts, _ = geometry(int(round(L / scale)), a / scale, n, gap / scale, seed, square)
        pts = (pts + 0.5) * scale - 0.5
        return pts, lbm.disks_mask(L, L, pts, a)
    if square:
        m = int(round(np.sqrt(n)))
        s = L / m
        pts = np.array([((i + 0.5) * s - 0.5, (j + 0.5) * s - 0.5) for i in range(m) for j in range(m)])
    else:
        pts = lbm.random_disks(L, L, n, a, gap, np.random.default_rng(seed))
    return pts, lbm.disks_mask(L, L, pts, a)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--L', type=int, default=384)
    p.add_argument('--a', type=float, default=12.0)
    p.add_argument('--n', type=int, default=64)
    p.add_argument('--gap', type=float, default=4.0)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--square', action='store_true')
    p.add_argument('--scale', type=float, default=1.0, help='refinement of a base cell L/scale, a/scale')
    p.add_argument('--nu', type=float, required=True)
    p.add_argument('--g', type=float, required=True)
    p.add_argument('--gy', type=float, default=0.0)
    p.add_argument('--spin', type=int, default=40000)
    p.add_argument('--samp', type=int, default=60000)
    p.add_argument('--every', type=int, default=20)
    p.add_argument('--init', default=None)
    p.add_argument('--state', default=None)
    p.add_argument('--lyap', type=int, default=0, help='steps of the twin run (0: none)')
    p.add_argument('--lyap_every', type=int, default=200)
    p.add_argument('--fields', action='store_true', help='store the time-averaged fields')
    p.add_argument('--steady_tol', type=float, default=0.0, help='stop the spin-up when the cell flux is steady to this tolerance')
    a = p.parse_args()

    t0 = time.time()
    pts, solid = geometry(a.L, a.a, a.n, a.gap, a.seed, a.square, a.scale)
    f, fn = lbm.init(solid)
    if a.init:
        with np.load(a.init) as z:
            assert z['f'].shape == f.shape
            f[:] = z['f']
    # spin-up
    n_spin, u_old = 0, 0.0
    acc0 = np.zeros((7,) + solid.shape)
    while n_spin < a.spin:
        f, fn, s = lbm.advance(f, fn, solid, a.nu, a.g, a.gy, 500, acc0)
        n_spin += 500
        if not np.isfinite(s[0]):
            raise RuntimeError('unstable run')
        if a.steady_tol > 0 and n_spin >= 4000 and abs(s[0] - u_old) < a.steady_tol * abs(s[0]):
            break
        u_old = s[0]
    # sampling
    acc = np.zeros((7,) + solid.shape)
    ns = a.samp // a.every
    ts = np.zeros((ns, 4))
    for k in range(ns):
        f, fn, s = lbm.advance(f, fn, solid, a.nu, a.g, a.gy, a.every, acc)
        ts[k] = s
    if not np.isfinite(ts).all():
        raise RuntimeError('unstable run')
    out = dict(ts=ts, pts=pts, solid=solid)
    U = ts[:, 0].mean() if ns else s[0]
    meta = dict(L=a.L, a=a.a, n=a.n, gap=a.gap, seed=a.seed, square=a.square, scale=a.scale, nu=a.nu, g=a.g, gy=a.gy, spin=n_spin,
                samp=a.samp, every=a.every, porosity=float(1 - solid.mean()), U=float(U), Re=float(U * 2 * a.a / a.nu))
    if ns:
        m = acc / ns
        fluid = ~solid
        nall = solid.size
        phi_tot = 2 * a.nu * m[6].sum() / nall                       # rho ~ 1: mean dissipation per node
        phi_mean = 2 * a.nu * (m[3] ** 2 + m[5] ** 2 + 2 * m[4] ** 2).sum() / nall
        tke = 0.5 * (m[2] - m[0] ** 2 - m[1] ** 2)
        meta.update(V=float(ts[:, 1].mean()), U_std=float(ts[:, 0].std()), phi=float(phi_tot), phi_mean_flow=float(phi_mean),
                    phi_ts=float(ts[:, 3].mean()), tke=float(tke.sum() / nall), ke_mean_flow=float(0.5 * (m[0] ** 2 + m[1] ** 2).sum() / nall),
                    umax=float(np.sqrt(m[2].max())))
        if a.fields:
            out.update(ubar=m[0].astype(np.float32), vbar=m[1].astype(np.float32), tke=tke.astype(np.float32),
                       phi_field=(2 * a.nu * m[6]).astype(np.float32),
                       phi_mean_field=(2 * a.nu * (m[3] ** 2 + m[5] ** 2 + 2 * m[4] ** 2)).astype(np.float32))
    # largest Lyapunov exponent: twin run, perturbed by a slightly different force for 500 steps, renormalised
    if a.lyap > 0:
        f2, fn2 = f.copy(), fn.copy()
        f2, fn2, _ = lbm.advance(f2, fn2, solid, a.nu, a.g * (1 + 1e-4), a.gy, 500)
        f, fn, _ = lbm.advance(f, fn, solid, a.nu, a.g, a.gy, 500)
        d0 = lbm.diff_norm(f, f2, solid)
        nl = a.lyap // a.lyap_every
        gr = np.zeros(nl)
        for k in range(nl):
            f, fn, _ = lbm.advance(f, fn, solid, a.nu, a.g, a.gy, a.lyap_every)
            f2, fn2, _ = lbm.advance(f2, fn2, solid, a.nu, a.g, a.gy, a.lyap_every)
            d = lbm.diff_norm(f, f2, solid)
            gr[k] = np.log(d / d0) / a.lyap_every
            f2 = f + (f2 - f) * (d0 / d)
        out['lyap_rates'] = gr
        half = gr[nl // 2:]
        meta.update(lyap=float(half.mean()), lyap_d0=float(d0))
    meta['seconds'] = round(time.time() - t0, 1)
    out['meta'] = json.dumps(meta)
    np.savez_compressed(a.out, **out)
    if a.state:
        np.savez(a.state, f=f)
    print(json.dumps(meta))


if __name__ == '__main__':
    main()
