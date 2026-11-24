"""RRJEDHA-GO, E3: a designed pumping rotation. Each year pumping is drawn at random from the operator's own
toe rule pi(a | R) (estimated in E1), independently of drought and of last year's decision. Then the standard
transfer entropy I(dX; A | R) is itself the interventional flow for that rule, and no drought record is needed.
Population values (200 000 wells) and estimation from n wells (200 data sets, well bootstrap); adds 'E3' to
rrjedha_results.json."""
import json, time
import numpy as np
from multiprocessing import Pool
import rrjedha as Rj
from rrjedha_exp import NBIG, NS, REPS, B


def job(args):
    n, seed, dbins, dxbins, pi_r = args
    rng = np.random.default_rng(seed)
    d = Rj.simulate(n, rng, dbins=dbins, dxbins=dxbins, policy='random', pi_r=pi_r)
    est = Rj.estimates(d)
    wells = d['well']; rows = [np.nonzero(wells == w)[0] for w in range(n)]
    bt = []
    for _ in range(B):
        pick = rng.integers(0, n, n); idx = np.concatenate([rows[w] for w in pick])
        bt.append(Rj.estimates(d, idx=idx)['te_obs'])
    e = est['te_obs']
    return dict(te_obs=e, te_obs_bc=float(2 * e - np.mean(bt)),
                ci=[float(np.quantile(bt, 0.025)), float(np.quantile(bt, 0.975))],
                ci_bc=[float(2 * e - np.quantile(bt, 0.975)), float(2 * e - np.quantile(bt, 0.025))])


if __name__ == '__main__':
    t0 = time.time()
    RS = json.load(open('rrjedha_results.json'))
    dbins, dxbins = np.array(RS['dbins']), np.array(RS['dxbins'])
    # operator's marginal toe rule P(A = 1 | R = r), from the observational population run
    pi_r = np.array(RS['desc']['pA_by_R'])
    rng = np.random.default_rng(20261017)
    big = Rj.simulate(NBIG, rng, dbins=dbins, dxbins=dxbins, policy='random', pi_r=pi_r)
    pop = Rj.estimates(big); tr = Rj.truth(big); pop['te_do'] = tr['te_do']
    print('population (rotation)', {k: round(float(v), 5) for k, v in pop.items()}, f'{time.time() - t0:.0f}s', flush=True)
    jobs = [(n, 9000 + 1000 * i + r, dbins, dxbins, pi_r) for i, n in enumerate(NS) for r in range(REPS)]
    with Pool(4) as pool:
        out = pool.map(job, jobs, chunksize=2)
    E3 = dict(pop={k: float(v) for k, v in pop.items()}, pi_r=pi_r.tolist())
    for i, n in enumerate(NS):
        oo = out[i * REPS:(i + 1) * REPS]; E3[str(n)] = {}
        for k, ck in (('te_obs', 'ci'), ('te_obs_bc', 'ci_bc')):
            v = np.array([o[k] for o in oo])
            E3[str(n)][k] = dict(mean=float(v.mean()), sd=float(v.std()), bias=float(v.mean() - pop['te_do']),
                                 rmse=float(np.sqrt(np.mean((v - pop['te_do']) ** 2))),
                                 cover=float(np.mean([o[ck][0] <= pop['te_do'] <= o[ck][1] for o in oo])))
        print(n, {k: (round(v['mean'], 4), round(v['sd'], 4), v['cover']) for k, v in E3[str(n)].items()}, flush=True)
    RS['E3'] = E3
    json.dump(RS, open('rrjedha_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
