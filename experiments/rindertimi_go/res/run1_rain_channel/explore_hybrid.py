"""FunDPS with rain guidance only (scenario A ensemble), then the ensemble smoother with the exact solver for B and C,
on the same truths; compared with the exact posterior of each scenario."""
import json, os, sys, time
import numpy as np
D = '/home/user/swi-goal-oed/experiments/rindertimi_go'
sys.path.insert(0, D)
import rgo_model as M, rgo_net as N, rgo_fundps as F
import jax
st = json.load(open(os.path.join(D, 'res', 'rgo_norm.json')))
p = N.load_params(os.path.join(D, 'res', 'rgo_params.npz'))
G, cQ = M.response_matrix(); mu, Sig = M.prior_z()
Rm = F.solver_matrices()
rng = np.random.default_rng(77)
wP = float(sys.argv[1]); ns = int(sys.argv[2]); ncase = int(sys.argv[3]); loss = sys.argv[4]
run = F.make_sampler(p, nstep=80, loss=loss)
res = {s: [] for s in ('A', 'B_es', 'C_es')}
for c in range(ncase):
    P, f = M.rain_weeks(rng, 1); P = P[:, 0]; f = f[:, 0]
    z = mu + np.linalg.cholesky(Sig + 1e-12 * np.eye(M.NZ)) @ rng.standard_normal(M.NZ)
    kap = M.KAP_MED * np.exp(M.KAP_LSD * rng.standard_normal())
    gk = M.kappa_response(f)
    tr = M.fields_from_z(z[:, None], np.array([kap]), f, G, cQ, gk)
    truth = dict(h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0], P=P, kappa=kap, f=f)
    rowsB = M.observation_rows(rng, 'B')
    rowsC = rowsB + [('eta', n) for n in range(M.NT)]
    yB = np.array([truth['h'].reshape(-1)[i] + M.SIG_H * rng.standard_normal() for k, i in rowsB])
    yC = np.concatenate([yB, truth['eta'] + M.SIG_ETA * rng.standard_normal(M.NT)])
    exA = M.exact_posterior(np.array([]), [], f, G, cQ, mu, Sig, rng=rng)
    exB = M.exact_posterior(yB, rowsB, f, G, cQ, mu, Sig, rng=rng)
    exC = M.exact_posterior(yC, rowsC, f, G, cQ, mu, Sig, rng=rng)
    o = F.obs_arrays([], np.array([]), P, st)
    t0 = time.time()
    a, _ = run(o, (wP, 0.0, 0.0), jax.random.PRNGKey(500 + c), ns=ns)
    tA = time.time() - t0
    ensA = N.from_field(a, st)
    ensA['h'] = np.moveaxis(M.simulate(ensA['h'][:, :, 0].T, ensA['eta'].T, ensA['qL'].T, ensA['r'].T), 2, 0)
    ensB = F.es_update(ensA, rowsB, yB, Rm, rng)
    ensC = F.es_update(ensA, rowsC, yC, Rm, rng)
    for key, ens, ex in (('A', ensA, exA), ('B_es', ensB, exB), ('C_es', ensC, exC)):
        s = F.summarise(ens, truth, ex)
        s['P_rms'] = float(np.sqrt(np.mean((ens['P'] - P[None]) ** 2)))
        kf = F.kappa_from_samples(ens['r'], f)
        s['kappa'] = (float(kf.mean()), float(kf.std()), float(ex['kappa_samples'].mean()), float(ex['kappa_samples'].std()), float(kap))
        res[key].append(s)
    print(f'case {c}: FunDPS-A {tA:.0f}s', flush=True)
for key, out in res.items():
    m = lambda k, q: np.mean([s[k][q] for s in out])
    print(f'{key} {loss} wP={wP:g} ns={ns} | ' + ' '.join(f'{k}: {m(k, "rmse_f") / m(k, "rmse_e"):.2f}x sd{m(k, "sd_ratio"):.2f} cov{m(k, "cov_f"):.2f}/{m(k, "cov_e"):.2f}' for k in ('eta', 'qL', 'r', 'h0'))
          + f' | P_rms {np.mean([s["P_rms"] for s in out]):.1f} | kappa ' + ' '.join(f'{s["kappa"][0]:.3f}±{s["kappa"][1]:.3f}/{s["kappa"][2]:.3f}±{s["kappa"][3]:.3f}({s["kappa"][4]:.3f})' for s in out), flush=True)
