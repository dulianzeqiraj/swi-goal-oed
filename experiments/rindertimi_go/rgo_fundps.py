"""FunDPS guided sampling of all boundary conditions of the RINDERTIMI-GO test bed, against the exact posterior.

Sampler: Algorithm 2 of Yao et al. (NeurIPS 2025): EDM Heun steps on sigma_max > ... > 0 from GRF noise, each followed by
the guidance step a <- a - zeta_t * grad_a sum_types w_type * mean (u - A D(a, sigma))^2 (their Eq. 14), with the weight
schedule zeta_t = sigma_t * zeta for sigma_t < 1 (their Appendix G). The observation operators A pick the rain channel
(all weeks), the heads at four piezometers on random weeks, and (scenario C) the sea level from a tide gauge.

Scenarios: A rain only (what the workbook and a rain record give); B rain + four head loggers read in 25% of the weeks;
C as B plus a weekly tide gauge. For each test truth: 32 FunDPS samples and 2000 exact posterior samples.
A physics check re-runs the simulator with the sampled boundary conditions (sea level, inflow, recharge, initial head).

usage: python rgo_fundps.py [tune|eval]   (writes res/rgo_tune.json or res/rgo_eval.json and res/rgo_case.npz)"""
import json
import os
import sys
import time

import numpy as np
import jax
import jax.numpy as jnp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rgo_model as M  # noqa: E402
import rgo_net as N  # noqa: E402

RES = os.path.join(HERE, 'res')
NSTEP, SMAX, SMIN, RHO = 80, 20.0, 0.002, 7.0
NS = 32                                    # FunDPS samples per case
MAXH = len(M.IP) * M.NT                    # padded number of head observations


def sigma_schedule(n=NSTEP):
    i = np.arange(n)
    s = (SMAX ** (1 / RHO) + i / (n - 1) * (SMIN ** (1 / RHO) - SMAX ** (1 / RHO))) ** RHO
    return np.append(s, 0.0).astype(np.float32)


# ------------------------------------------------------------------------------------------------ observations
def make_case(rng, scenario, G, cQ, mu, Sig):
    """one truth from the prior, its observations, and the exact posterior."""
    P, f = M.rain_weeks(rng, 1); P = P[:, 0]; f = f[:, 0]
    z = mu + np.linalg.cholesky(Sig + 1e-12 * np.eye(M.NZ)) @ rng.standard_normal(M.NZ)
    kap = M.KAP_MED * np.exp(M.KAP_LSD * rng.standard_normal())
    gk = M.kappa_response(f)
    tr = M.fields_from_z(z[:, None], np.array([kap]), f, G, cQ, gk)
    truth = dict(h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0], P=P, kappa=kap, f=f)
    rows = M.observation_rows(rng, scenario)
    y = []
    for kind, idx in rows:
        if kind == 'h':
            y.append(truth['h'].reshape(-1)[idx] + M.SIG_H * rng.standard_normal())
        else:
            y.append(truth['eta'][idx] + M.SIG_ETA * rng.standard_normal())
    y = np.array(y)
    ex = M.exact_posterior(y, rows, f, G, cQ, mu, Sig, rng=rng, nsamp=2000)
    return truth, rows, y, ex


def obs_arrays(rows, y, P, st):
    """padded arrays in the normalised space of the diffusion model."""
    hx = np.zeros(MAXH, np.int32); ht = np.zeros(MAXH, np.int32); hy = np.zeros(MAXH, np.float32); hw = np.zeros(MAXH, np.float32)
    ey = np.zeros(M.NT, np.float32); ew = np.zeros(M.NT, np.float32)
    k = 0
    hm = np.asarray(st['h_mean'])
    for (kind, idx), val in zip(rows, y):
        if kind == 'h':
            ix, it = divmod(idx, M.NT)
            hx[k], ht[k] = ix, it
            hy[k] = (val - hm[ix]) / st['h_sd']; hw[k] = 1.0; k += 1
        else:
            ey[idx] = (val - st['eta_mean']) / st['eta_sd']; ew[idx] = 1.0
    py = ((P - st['f_mean']) / st['f_sd']).astype(np.float32)          # P here is the filtered rain f (mm/d)
    return dict(hx=jnp.asarray(hx), ht=jnp.asarray(ht), hy=jnp.asarray(hy), hw=jnp.asarray(hw),
                ey=jnp.asarray(ey), ew=jnp.asarray(ew), py=jnp.asarray(py))


# ------------------------------------------------------------------------------------------------ sampler
def head_operator(st):
    """the aquifer solver as a linear map from the boundary and initial conditions to the head, in the normalised
    space of the diffusion model: h_norm = sum_c R_c a_c + c0 (the operator A of FunDPS may contain the PDE solution
    operator, their Section 3.1)."""
    nx, nt = M.NX, M.NT
    z_t, z_x = np.zeros((nt, nt)), np.zeros((nx, nt))
    R_h0 = M.simulate(np.eye(nx), np.zeros((nt, nx)), np.zeros((nt, nx)), np.zeros((nt, nx)), Q=0.0).reshape(nx * nt, nx)
    R_eta = M.simulate(z_x, np.eye(nt), z_t, z_t, Q=0.0).reshape(nx * nt, nt)
    R_q = M.simulate(z_x, z_t, np.eye(nt), z_t, Q=0.0).reshape(nx * nt, nt)
    R_r = M.simulate(z_x, z_t, z_t, np.eye(nt), Q=0.0).reshape(nx * nt, nt)
    c_Q = M.simulate(np.zeros((nx, 1)), np.zeros((nt, 1)), np.zeros((nt, 1)), np.zeros((nt, 1))).reshape(nx * nt)
    hm = np.asarray(st['h_mean']); hs = st['h_sd']
    # inputs are normalised: a_c = (v - mean_c)/sd_c, h0 = (h0 - h_mean)/h_sd
    sc = {k: st[k + '_sd'] for k in ('eta', 'qL', 'r')}
    mn = {k: st[k + '_mean'] for k in ('eta', 'qL', 'r')}
    const = (c_Q + R_h0 @ hm + R_eta @ np.full(nt, mn['eta']) + R_q @ np.full(nt, mn['qL']) + R_r @ np.full(nt, mn['r'])
             - np.repeat(hm, nt)) / hs
    return dict(h0=jnp.asarray(R_h0 * hs / hs, jnp.float32), eta=jnp.asarray(R_eta * sc['eta'] / hs, jnp.float32),
                qL=jnp.asarray(R_q * sc['qL'] / hs, jnp.float32), r=jnp.asarray(R_r * sc['r'] / hs, jnp.float32),
                const=jnp.asarray(const, jnp.float32))


def solver_matrices():
    """the aquifer solver as a linear map, in physical units: h = R_h0 h0 + R_eta eta + R_q qL + R_r r + c_Q."""
    nx, nt = M.NX, M.NT
    z_t, z_x = np.zeros((nt, nt)), np.zeros((nx, nt))
    return dict(h0=M.simulate(np.eye(nx), np.zeros((nt, nx)), np.zeros((nt, nx)), np.zeros((nt, nx)), Q=0.0).reshape(nx * nt, nx),
                eta=M.simulate(z_x, np.eye(nt), z_t, z_t, Q=0.0).reshape(nx * nt, nt),
                qL=M.simulate(z_x, z_t, np.eye(nt), z_t, Q=0.0).reshape(nx * nt, nt),
                r=M.simulate(z_x, z_t, z_t, np.eye(nt), Q=0.0).reshape(nx * nt, nt),
                cQ=M.simulate(np.zeros((nx, 1)), np.zeros((nt, 1)), np.zeros((nt, 1)), np.zeros((nt, 1))).reshape(nx * nt))


def es_update(ens, rows, y, Rm, rng):
    """ensemble smoother with perturbed observations (one Kalman step with ensemble covariances) on the boundary and
    initial conditions; the observation operator is the exact solver (heads) or the identity (tide gauge). The head
    of the updated members is re-simulated, so every member is a solution of the flow equation."""
    S = ens['eta'].shape[0]
    X = np.concatenate([ens['h'][:, :, 0], ens['eta'], ens['qL'], ens['r']], axis=1)          # (S, 224)
    nx, nt = M.NX, M.NT
    Hm, c, sd = [], [], []
    for kind, idx in rows:
        if kind == 'h':
            Hm.append(np.concatenate([Rm['h0'][idx], Rm['eta'][idx], Rm['qL'][idx], Rm['r'][idx]])); c.append(Rm['cQ'][idx])
            sd.append(M.SIG_H)
        else:
            e = np.zeros(X.shape[1]); e[nx + idx] = 1.0
            Hm.append(e); c.append(0.0); sd.append(M.SIG_ETA)
    Hm, c, sd = np.array(Hm), np.array(c), np.array(sd)
    Y = X @ Hm.T + c
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    Cxy = Xc.T @ Yc / (S - 1); Cyy = Yc.T @ Yc / (S - 1)
    K = np.linalg.solve(Cyy + np.diag(sd ** 2), Cxy.T).T
    Ypert = y[None] + sd[None] * rng.standard_normal((S, len(y)))
    Xa = X + (Ypert - Y) @ K.T
    h0, eta, qL, r = Xa[:, :nx], Xa[:, nx:nx + nt], Xa[:, nx + nt:nx + 2 * nt], Xa[:, nx + 2 * nt:]
    h = np.moveaxis(M.simulate(h0.T, eta.T, qL.T, r.T), 2, 0)
    return dict(h=h, eta=eta, qL=qL, r=r, f=ens['f'])


def make_sampler(p, nstep=NSTEP, loss='mse', phys=None, bc_geom=False):
    """loss 'mse': mean squared misfit per observation type (FunDPS Eq. 14); 'l2': its square root, the L2 loss type
    of FunDPS Table 4 (as in DPS, the step then does not grow with the misfit). phys: head_operator(st); then the
    heads at the piezometers are computed by the solver from the denoised boundary and initial conditions instead of
    being read from the head channel. bc_geom: the boundary channels are functions of t stored as copies along x, so
    the gradient of the guidance loss with respect to the time function is NX times the gradient with respect to one
    copy; with bc_geom the guidance step uses the gradient in the geometry of L2(0, T) for those channels."""
    gscale = jnp.asarray([1.0] + [float(M.NX) if bc_geom else 1.0] * 4, jnp.float32)
    def heads(x0, o):
        if phys is None:
            return x0[:, o['hx'], o['ht'], 0]
        k = o['hx'] * M.NT + o['ht']                      # rows of the flattened (x, t) head
        return (x0[:, :, 0, 0] @ phys['h0'][k].T + x0[:, 0, :, 1] @ phys['eta'][k].T + x0[:, 0, :, 2] @ phys['qL'][k].T
                + x0[:, 0, :, 3] @ phys['r'][k].T + phys['const'][k][None])

    def obs_loss(x0, o, wP, wH, wE):
        rP = x0[:, 0, :, 4] - o['py'][None]
        lP = jnp.mean(rP ** 2, axis=1)
        rH = heads(x0, o) - o['hy'][None]
        lH = jnp.sum(o['hw'][None] * rH ** 2, axis=1) / jnp.maximum(jnp.sum(o['hw']), 1.0)
        rE = x0[:, 0, :, 1] - o['ey'][None]
        lE = jnp.sum(o['ew'][None] * rE ** 2, axis=1) / jnp.maximum(jnp.sum(o['ew']), 1.0)
        if loss == 'l2':
            lP, lH, lE = (jnp.sqrt(v + 1e-12) for v in (lP, lH, lE))
        return jnp.sum(wP * lP + wH * lH + wE * lE)

    def guided(a, s, o, wP, wH, wE):
        sig = jnp.full((a.shape[0],), s)
        x0 = N.denoise(p, a, sig)
        return obs_loss(x0, o, wP, wH, wE), x0

    vg = jax.value_and_grad(guided, has_aux=True)

    @jax.jit
    def step(a, s, s_next, o, wP, wH, wE):
        sched = jnp.where(s < 1.0, s, 1.0)                  # zeta_t = sigma_t zeta for sigma_t < 1
        (_, x0), g = vg(a, s, o, wP * sched, wH * sched, wE * sched)
        d = (a - x0) / s
        a_e = a + (s_next - s) * d

        def heun(_):
            x0b = N.denoise(p, a_e, jnp.full((a.shape[0],), jnp.maximum(s_next, 1e-6)))
            d2 = (a_e - x0b) / jnp.maximum(s_next, 1e-6)
            return a + (s_next - s) * 0.5 * (d + d2)
        a_n = jax.lax.cond(s_next > 0, heun, lambda _: a_e, None)
        return N.project(a_n - g * gscale), x0, a_n

    def run(o, w, key, ns=NS, keep=()):
        sig = sigma_schedule(nstep)
        a = SMAX * N.grf_noise(key, ns)
        snaps = {}
        if keep:
            snaps['init'] = (np.asarray(a), np.asarray(a), np.asarray(a), float(sig[0]))
        for i in range(len(sig) - 1):
            a, x0, a_unc = step(a, sig[i], sig[i + 1], o, w[0], w[1], w[2])
            if i in keep:                      # state after the step, denoised estimate, step without guidance, sigma
                snaps[i] = (np.asarray(a), np.asarray(x0), np.asarray(a_unc), float(sig[i]))
        return np.asarray(a), snaps
    return run


# ------------------------------------------------------------------------------------------------ evaluation
def summarise(samples, truth, ex):
    """errors of the posterior means against the truth, coverage, and distance to the exact posterior."""
    out = {}
    E = ex['samples']
    pairs = dict(eta=(samples['eta'], E['eta'], truth['eta']), qL=(samples['qL'], E['qL'], truth['qL']),
                 r=(samples['r'], E['r'], truth['r']), h0=(samples['h'][:, :, 0], E['h'][:, :, 0], truth['h'][:, 0]),
                 h=(samples['h'].reshape(len(samples['h']), -1), E['h'].reshape(len(E['h']), -1), truth['h'].reshape(-1)))
    for k, (fs, es, tv) in pairs.items():
        fm, em = fs.mean(0), es.mean(0)
        esd = es.std(0) + 1e-9
        lo_f, hi_f = np.quantile(fs, [0.05, 0.95], axis=0); lo_e, hi_e = np.quantile(es, [0.05, 0.95], axis=0)
        out[k] = dict(rmse_f=float(np.sqrt(np.mean((fm - tv) ** 2))), rmse_e=float(np.sqrt(np.mean((em - tv) ** 2))),
                      cov_f=float(np.mean((tv >= lo_f) & (tv <= hi_f))), cov_e=float(np.mean((tv >= lo_e) & (tv <= hi_e))),
                      dist=float(np.mean(np.abs(fm - em) / esd)), sd_ratio=float(np.mean(fs.std(0)) / np.mean(esd)),
                      sd_e=float(np.mean(esd)))
    return out


def kappa_from_samples(r, f):
    """least-squares recharge coefficient of each sample: r ~ kappa f."""
    return (r @ f) / (f @ f)


def physics_check(samples, truth_rows, y):
    """re-simulate the head from the sampled boundary conditions; misfit to the head data and to the diffusion head."""
    h0 = samples['h'][:, :, 0].T
    hs = M.simulate(h0, samples['eta'].T, samples['qL'].T, samples['r'].T)       # (NX, NT, S)
    hs = np.moveaxis(hs, 2, 0)
    cons = float(np.sqrt(np.mean((hs - samples['h']) ** 2)))
    idx = [i for (k, i), _ in zip(truth_rows, y) if k == 'h']
    yh = np.array([v for (k, i), v in zip(truth_rows, y) if k == 'h'])
    fit_d = float(np.sqrt(np.mean((samples['h'].reshape(len(hs), -1)[:, idx] - yh) ** 2))) if len(idx) else float('nan')
    fit_p = float(np.sqrt(np.mean((hs.reshape(len(hs), -1)[:, idx] - yh) ** 2))) if len(idx) else float('nan')
    return dict(consistency=cons, fit_diffusion=fit_d, fit_physics=fit_p)


# ------------------------------------------------------------------------------------------------ paired evaluation
RAIN_CFG = [('l2', 100.0), ('l2', 300.0), ('mse', 100.0)]                 # FunDPS with the filtered rain only
PURE_CFG = [('l2', 300.0, 300.0), ('mse', 100.0, 300.0)]                  # FunDPS with every observation in its guidance
NS_A, NS_PURE, N_CASE = 128, 32, 12
BLOWUP = 1e3          # a sample larger than this (normalised units, where the prior has sd near 1) has diverged


def new_case(rng, G, cQ, mu, Sig):
    """one truth from the prior with the paired observations of scenarios A (rain), B (+ heads) and C (+ tide gauge)."""
    P, f = M.rain_weeks(rng, 1); P = P[:, 0]; f = f[:, 0]
    z = mu + np.linalg.cholesky(Sig + 1e-12 * np.eye(M.NZ)) @ rng.standard_normal(M.NZ)
    kap = M.KAP_MED * np.exp(M.KAP_LSD * rng.standard_normal())
    gk = M.kappa_response(f)
    tr = M.fields_from_z(z[:, None], np.array([kap]), f, G, cQ, gk)
    truth = dict(h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0], P=P, f=f, kappa=kap)
    rowsB = M.observation_rows(rng, 'B')
    yB = np.array([truth['h'].reshape(-1)[i] + M.SIG_H * rng.standard_normal() for _, i in rowsB])
    rowsC = rowsB + [('eta', n) for n in range(M.NT)]
    yC = np.concatenate([yB, truth['eta'] + M.SIG_ETA * rng.standard_normal(M.NT)])
    obs = dict(A=([], np.array([])), B=(rowsB, yB), C=(rowsC, yC))
    ex = {s: M.exact_posterior(y, rows, f, G, cQ, mu, Sig, rng=rng, nsamp=2000) for s, (rows, y) in obs.items()}
    return truth, obs, ex


def simulate_ens(ens):
    """the product of every method: boundary and initial conditions, with the head re-simulated from them."""
    out = dict(ens)
    out['h'] = np.moveaxis(M.simulate(ens['h'][:, :, 0].T, ens['eta'].T, ens['qL'].T, ens['r'].T), 2, 0)
    return out


def score(ens, raw, truth, ex, rows, y, secs):
    s = summarise(ens, truth, ex)
    kf = kappa_from_samples(ens['r'], truth['f'])
    s['kappa'] = dict(truth=float(truth['kappa']), exact_mean=float(ex['kappa_samples'].mean()),
                      exact_sd=float(ex['kappa_samples'].std()), fundps_mean=float(kf.mean()), fundps_sd=float(kf.std()))
    s['f_rms'] = float(np.sqrt(np.mean((ens['f'] - truth['f'][None]) ** 2)))
    s['physics'] = physics_check(raw, rows, y)                 # the diffusion head channel against the solver
    s['fit'] = physics_check(ens, rows, y)['fit_physics']      # the product against the head data
    s['seconds'] = secs; s['n_obs'] = len(rows)
    return s


def agg(res):
    out = {}
    for k in ('eta', 'qL', 'r', 'h0', 'h'):
        out[k] = {m: float(np.median([r[k][m] for r in res])) for m in res[0][k]}
        out[k]['ratio'] = float(np.median([r[k]['rmse_f'] / r[k]['rmse_e'] for r in res]))
    out['kappa'] = dict(abs_err_f=float(np.median([abs(r['kappa']['fundps_mean'] - r['kappa']['truth']) for r in res])),
                        abs_err_e=float(np.median([abs(r['kappa']['exact_mean'] - r['kappa']['truth']) for r in res])),
                        sd_f=float(np.median([r['kappa']['fundps_sd'] for r in res])),
                        sd_e=float(np.median([r['kappa']['exact_sd'] for r in res])),
                        z=float(np.median([abs(r['kappa']['fundps_mean'] - r['kappa']['exact_mean']) / r['kappa']['exact_sd'] for r in res])))
    out['f_rms'] = float(np.median([r['f_rms'] for r in res]))
    out['physics'] = {m: float(np.nanmedian([r['physics'][m] for r in res])) for m in res[0]['physics']}
    out['fit'] = float(np.nanmedian([r['fit'] for r in res]))
    out['seconds'] = float(np.median([r['seconds'] for r in res]))
    out['n_obs'] = float(np.median([r['n_obs'] for r in res]))
    return out


def h0_or(ens, k):
    """what the figures keep of an ensemble: the initial head, or a boundary condition."""
    return (ens['h'][:, :, 0] if k == 'h0' else ens[k]).astype(np.float32)


def run_method(run, st, obs_rows, obs_y, f, ns, key, keep=()):
    o = obs_arrays(obs_rows, obs_y, f, st)
    t0 = time.time()
    a, snaps = run(o, key=key, ns=ns, keep=keep)
    secs = time.time() - t0
    if not np.all(np.isfinite(a)) or np.abs(a).max() > BLOWUP:
        return None, None, secs, snaps
    raw = N.from_field(a, st)
    return simulate_ens(raw), raw, secs, snaps


def sampler(p, st, loss, w, phys=False):
    run = make_sampler(p, loss=loss, phys=head_operator(st) if phys else None)
    return lambda o, key, ns, keep=(): run(o, w, key, ns=ns, keep=keep)


def tune(p, st, G, cQ, mu, Sig):
    """guidance settings on two validation cases (seed 77), separate from the test cases."""
    rng = np.random.default_rng(77)
    cases = [new_case(rng, G, cQ, mu, Sig) for _ in range(2)]
    out = dict(rain={}, pure={})
    for loss, wP in RAIN_CFG:
        run = sampler(p, st, loss, (wP, 0.0, 0.0))
        res = []
        for c, (truth, obs, ex) in enumerate(cases):
            ens, raw, secs, _ = run_method(run, st, [], np.array([]), truth['f'], 64, jax.random.PRNGKey(70 + c))
            res.append(None if ens is None else score(ens, raw, truth, ex['A'], [], np.array([]), secs))
        if any(r is None for r in res):
            out['rain'][f'{loss}_{wP:g}'] = None; print('rain', loss, wP, 'diverged', flush=True); continue
        a = agg(res)
        a['score'] = float(np.mean([a[k]['ratio'] for k in ('eta', 'qL', 'r', 'h0')]) + abs(np.log(a['r']['sd_ratio'])))
        out['rain'][f'{loss}_{wP:g}'] = a
        print('rain', loss, wP, 'score', round(a['score'], 3), {k: (round(a[k]['ratio'], 2), round(a[k]['sd_ratio'], 2)) for k in ('eta', 'qL', 'r', 'h0')},
              'f_rms', round(a['f_rms'], 3), flush=True)
    for loss, wP, wH in PURE_CFG:
        run = sampler(p, st, loss, (wP, wH, wH), phys=True)
        res = []
        for c, (truth, obs, ex) in enumerate(cases):
            rows, y = obs['B']
            ens, raw, secs, _ = run_method(run, st, rows, y, truth['f'], NS_PURE, jax.random.PRNGKey(80 + c))
            res.append(None if ens is None else score(ens, raw, truth, ex['B'], rows, y, secs))
        if any(r is None for r in res):
            out['pure'][f'{loss}_{wP:g}_{wH:g}'] = None; print('pure', loss, wP, wH, 'diverged', flush=True); continue
        a = agg(res)
        a['score'] = float(np.mean([a[k]['ratio'] for k in ('eta', 'qL', 'r', 'h0')]))
        out['pure'][f'{loss}_{wP:g}_{wH:g}'] = a
        print('pure', loss, wP, wH, 'score', round(a['score'], 3), 'fit', round(100 * a['fit'], 1), flush=True)
    with open(os.path.join(RES, 'rgo_tune.json'), 'w') as fh:
        json.dump(out, fh)


def regroup(path):
    """apply the divergence rule to the stored cases of an evaluation and recompute the medians: a case whose posterior
    mean is more than BLOWUP prior standard deviations from the truth in some boundary condition has diverged."""
    with open(path) as fh:
        out = json.load(fh)
    pr = out['prior_sd']
    for k, m in out['methods'].items():
        ok, nd = [], 0
        for r in m['cases']:
            if r is None or max(r[c]['rmse_f'] / pr[c] for c in ('eta', 'qL', 'r', 'h0')) > BLOWUP:
                nd += 1
            else:
                ok.append(r)
        m['agg'] = agg(ok) if ok else None
        m['n_diverged'] = nd
        m['cases'] = [r if (r is not None and r in ok) else None for r in m['cases']]
    with open(path, 'w') as fh:
        json.dump(out, fh)
    return {k: m['n_diverged'] for k, m in out['methods'].items()}


def main(mode):
    with open(os.path.join(RES, 'rgo_norm.json')) as fh:
        st = json.load(fh)
    p = N.load_params(os.path.join(RES, 'rgo_params.npz'))
    G, cQ = M.response_matrix(); mu, Sig = M.prior_z()
    if mode == 'tune':
        tune(p, st, G, cQ, mu, Sig)
        return
    if mode == 'regroup':
        print('diverged cases per method:', regroup(os.path.join(RES, 'rgo_eval.json')))
        return
    with open(os.path.join(RES, 'rgo_tune.json')) as fh:
        T = json.load(fh)
    rk = min((k for k in T['rain'] if T['rain'][k]), key=lambda k: T['rain'][k]['score'])
    pk = min((k for k in T['pure'] if T['pure'][k]), key=lambda k: T['pure'][k]['score'])
    rl, rw = rk.split('_'); pl, pw, ph = pk.split('_')
    print('rain guidance', rk, '| pure guidance', pk, flush=True)
    run_rain = sampler(p, st, rl, (float(rw), 0.0, 0.0))
    run_pure = sampler(p, st, pl, (float(pw), float(ph), float(ph)), phys=True)
    Rm = solver_matrices()
    out = dict(rain=dict(loss=rl, w=float(rw)), pure=dict(loss=pl, wP=float(pw), wH=float(ph)), nstep=NSTEP,
               ns_a=NS_A, ns_pure=NS_PURE, n_case=N_CASE, methods={})
    a_pr, _ = M.sample_prior(np.random.default_rng(9), 4000)
    out['prior_sd'] = dict(eta=float(a_pr[:, 1, 0].std(0).mean()), qL=float(a_pr[:, 2, 0].std(0).mean()),
                           r=float(a_pr[:, 3, 0].std(0).mean()), h0=float(a_pr[:, 0, :, 0].std(0).mean()),
                           h=float(a_pr[:, 0].std(0).mean()))
    res = {k: [] for k in ('fundps_A', 'hybrid_B', 'hybrid_C', 'pure_B', 'pure_C')}
    rng = np.random.default_rng(501)
    pack = {}
    for c in range(N_CASE):
        truth, obs, ex = new_case(rng, G, cQ, mu, Sig)
        keep = (0, 20, 40, 41, 60, NSTEP - 1) if c == 0 else ()
        ensA, rawA, secA, snaps = run_method(run_rain, st, [], np.array([]), truth['f'], NS_A, jax.random.PRNGKey(5000 + c), keep)
        if ensA is None:                     # one retry with another key; counted in the log
            print(f'case {c}: FunDPS-A not finite, retried', flush=True)
            ensA, rawA, secA, snaps = run_method(run_rain, st, [], np.array([]), truth['f'], NS_A,
                                                 jax.random.PRNGKey(7000 + c), keep)
        res['fundps_A'].append(score(ensA, rawA, truth, ex['A'], [], np.array([]), secA))
        es_rng = np.random.default_rng(900 + c)
        for s in ('B', 'C'):
            rows, y = obs[s]
            t0 = time.time()
            ensS = es_update(ensA, rows, y, Rm, es_rng)
            res[f'hybrid_{s}'].append(score(ensS, ensS, truth, ex[s], rows, y, secA + time.time() - t0))
            ensP, rawP, secP, _ = run_method(run_pure, st, rows, y, truth['f'], NS_PURE, jax.random.PRNGKey(6000 + 10 * c + ord(s)))
            res[f'pure_{s}'].append(None if ensP is None else score(ensP, rawP, truth, ex[s], rows, y, secP))
            if c == 0:
                for k in ('h0', 'eta', 'qL', 'r'):
                    pack[f'{s}_hyb_{k}'] = h0_or(ensS, k)
                    if ensP is not None:
                        pack[f'{s}_pure_{k}'] = h0_or(ensP, k)
        if c == 0:
            for k in ('h', 'eta', 'qL', 'r', 'P', 'f'):
                pack[f'truth_{k}'] = truth[k]
            for k in ('h0', 'eta', 'qL', 'r'):
                pack[f'A_fun_{k}'] = h0_or(ensA, k)
                for s in 'ABC':
                    pack[f'{s}_ex_{k}'] = h0_or(ex[s]['samples'], k)[:400]
            pack['A_fun_raw_h'] = rawA['h'][:16]
            for s in 'BC':
                pack[f'{s}_rows'] = np.array([(0 if k == 'h' else 1, i) for k, i in obs[s][0]], dtype=np.int64)
                pack[f'{s}_y'] = obs[s][1]
            for i, (a, x0, au, sg) in snaps.items():
                pack[f'snap_a_{i}'] = a[:4]; pack[f'snap_x0_{i}'] = x0[:4]; pack[f'snap_au_{i}'] = au[:4]; pack[f'snap_s_{i}'] = sg
        line = ' | '.join(f'{k} ' + ' '.join(f'{ch} {r_[-1][ch]["rmse_f"] / r_[-1][ch]["rmse_e"]:.2f}x/{r_[-1][ch]["sd_ratio"]:.2f}'
                                              for ch in ('eta', 'qL', 'r', 'h0')) for k, r_ in res.items() if r_[-1] is not None)
        print(f'case {c} ({secA:.0f}s): {line}', flush=True)
    for k, r_ in res.items():
        ok = [x for x in r_ if x is not None]
        out['methods'][k] = dict(agg=agg(ok) if ok else None, cases=r_, n_diverged=len(r_) - len(ok))
        print(k, json.dumps(out['methods'][k]['agg'])[:500], flush=True)
    with open(os.path.join(RES, 'rgo_eval.json'), 'w') as fh:
        json.dump(out, fh)
    print('diverged cases per method:', regroup(os.path.join(RES, 'rgo_eval.json')), flush=True)
    np.savez_compressed(os.path.join(RES, 'rgo_case.npz'), **pack)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'eval')
