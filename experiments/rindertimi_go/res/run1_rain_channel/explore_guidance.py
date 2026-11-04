"""guidance settings on validation cases of scenario B (seed 77, as the tuning set)."""
import json, os, sys, time
import numpy as np
D = '/home/user/swi-goal-oed/experiments/rindertimi_go'
sys.path.insert(0, D)
import rgo_model as M, rgo_net as N, rgo_fundps as F
import jax
st = json.load(open(os.path.join(D, 'res', 'rgo_norm.json')))
p = N.load_params(os.path.join(D, 'res', 'rgo_params.npz'))
G, cQ = M.response_matrix(); mu, Sig = M.prior_z()
rng = np.random.default_rng(77)
cases = [F.make_case(rng, 'B', G, cQ, mu, Sig) for _ in range(2)]
configs = json.loads(sys.argv[1])
phys_op = F.head_operator(st)
for loss, nstep, (wP, wH), use_phys in configs:
    run = F.make_sampler(p, nstep=nstep, loss=loss, phys=phys_op if use_phys else None, bc_geom=True)
    out = []
    t0 = time.time()
    for c, (truth, rows, y, ex) in enumerate(cases):
        o = F.obs_arrays(rows, y, truth['P'], st)
        a, _ = run(o, (wP, wH, wH), jax.random.PRNGKey(100 + c), ns=16)
        if not np.all(np.isfinite(a)):
            out = None; break
        smp = N.from_field(a, st)
        s = F.summarise(smp, truth, ex)
        s['P_rms'] = float(np.sqrt(np.mean((smp['P'] - truth['P'][None]) ** 2)))
        s['phys'] = F.physics_check(smp, rows, y)
        out.append(s)
    if out is None:
        print(f'{loss} N={nstep} wP={wP:g} wH={wH:g} phys={use_phys} diverged', flush=True); continue
    m = lambda k, q: np.mean([s[k][q] for s in out])
    print(f'{loss} phys={use_phys} N={nstep} wP={wP:g} wH={wH:g} ({time.time() - t0:.0f}s) | '
          + ' '.join(f'{k}: {m(k, "rmse_f") / m(k, "rmse_e"):.2f}x sd{m(k, "sd_ratio"):.2f} cov{m(k, "cov_f"):.2f}' for k in ('eta', 'qL', 'r', 'h0'))
          + f' | P_rms {np.mean([s["P_rms"] for s in out]):.1f} | cons {100 * np.mean([s["phys"]["consistency"] for s in out]):.1f} cm'
          + f' fit_d {100 * np.mean([s["phys"]["fit_diffusion"] for s in out]):.1f} fit_p {100 * np.mean([s["phys"]["fit_physics"] for s in out]):.1f}', flush=True)
