"""RRJEDHA-GO experiments. Writes rrjedha_results.json.
E1: population values (200 000 wells x 10 years): TE_obs, TE_cond, TE_adj, TE_adj without drought, and
    the interventional information flow TE_do from twin worlds; PID of I(dX; A, D) observational and with
    pumping assigned at random.
E2: estimation from n wells (200, 800, 3 200), 200 data sets: bias and SD of each estimator against TE_do,
    and percentile-bootstrap coverage (200 resamples of wells) for TE_adj and TE_obs; the bootstrap
    bias-corrected versions (suffix _bc) use 2 e - mean(e*) and the basic interval."""
import json, time
import numpy as np
from multiprocessing import Pool
import rrjedha as Rj
NBIG, NS, REPS, B = 200000, [200, 800, 3200], 200, 200


def pilot():
    rng = np.random.default_rng(1)
    d = Rj.simulate(20000, rng); dbins = np.quantile(d['Dc'], [1 / 3, 2 / 3])
    d = Rj.simulate(20000, rng, dbins=dbins); dxbins = np.quantile(d['dX'], [1 / 3, 2 / 3])
    return dbins, dxbins


def job(args):
    n, seed, dbins, dxbins = args
    rng = np.random.default_rng(seed)
    d = Rj.simulate(n, rng, dbins=dbins, dxbins=dxbins)
    est = Rj.estimates(d)
    wells = d['well']; rows = [np.nonzero(wells == w)[0] for w in range(n)]
    bt = {k: [] for k in ('te_obs', 'te_adj')}
    for _ in range(B):
        pick = rng.integers(0, n, n); idx = np.concatenate([rows[w] for w in pick])
        e = Rj.estimates(d, idx=idx)
        for k in bt:
            bt[k].append(e[k])
    est['ci'] = {k: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] for k, v in bt.items()}
    # bootstrap bias correction 2 e - mean(e*) and the matching basic interval [2e - q97.5, 2e - q2.5]
    for k, v in bt.items():
        est[k + '_bc'] = float(2 * est[k] - np.mean(v))
        est['ci'][k + '_bc'] = [float(2 * est[k] - np.quantile(v, 0.975)), float(2 * est[k] - np.quantile(v, 0.025))]
    est['nrows'] = int(len(d['A']))
    return est


if __name__ == '__main__':
    t0 = time.time()
    dbins, dxbins = pilot()
    rng = np.random.default_rng(20261016)
    big = Rj.simulate(NBIG, rng, dbins=dbins, dxbins=dxbins)
    pop = Rj.estimates(big); tr = Rj.truth(big); pop['te_do'] = tr['te_do']
    print('population', {k: round(v, 5) for k, v in pop.items()}, 'rows', len(big['A']), f'{time.time() - t0:.0f}s', flush=True)
    # PID: observational sources (A, D); interventional A ~ Bernoulli(1/2) via twins
    K, A, D = big['dXb'], big['A'].astype(int), big['D']
    p_obs = Rj.joint(K, A, D, sizes=(3, 2, 3))
    p_int = 0.5 * Rj.joint(big['dX0b'], np.zeros_like(A), D, sizes=(3, 2, 3)) + 0.5 * Rj.joint(big['dX1b'], np.ones_like(A), D, sizes=(3, 2, 3))
    pid = dict(obs=Rj.pid_imin(p_obs), int=Rj.pid_imin(p_int), obs_broja=Rj.pid_broja(p_obs), int_broja=Rj.pid_broja(p_int))
    print('PID', {k: {a: (round(b, 5) if isinstance(b, float) else b) for a, b in v.items()} for k, v in pid.items()}, flush=True)
    # descriptive: P(A=1 | D), mean dX by D
    desc = dict(pA_by_D=[float(A[D == k].mean()) for k in range(3)],
                dX0_by_D=[float(big['dX0'][D == k].mean()) for k in range(3)],
                dX1_by_D=[float(big['dX1'][D == k].mean()) for k in range(3)],
                pA_by_R=[float(A[big['R'] == k].mean()) for k in range(4)],
                pr=tr['pr'].tolist(), pdo=tr['pdo'].tolist(), ace=float((big['dX1'] - big['dX0']).mean()))
    jobs = [(n, 5000 + 1000 * i + r, dbins, dxbins) for i, n in enumerate(NS) for r in range(REPS)]
    with Pool(4) as pool:
        out = pool.map(job, jobs, chunksize=2)
    E2 = {}
    for i, n in enumerate(NS):
        oo = out[i * REPS:(i + 1) * REPS]; E2[str(n)] = {'rows': float(np.mean([o['nrows'] for o in oo]))}
        for k in ('te_obs', 'te_cond', 'te_adj', 'te_adj_noD', 'te_obs_bc', 'te_adj_bc'):
            v = np.array([o[k] for o in oo])
            E2[str(n)][k] = dict(mean=float(v.mean()), sd=float(v.std()), bias=float(v.mean() - pop['te_do']),
                                 rmse=float(np.sqrt(np.mean((v - pop['te_do']) ** 2))))
        for k in ('te_obs', 'te_adj', 'te_obs_bc', 'te_adj_bc'):
            E2[str(n)][k]['cover'] = float(np.mean([o['ci'][k][0] <= pop['te_do'] <= o['ci'][k][1] for o in oo]))
        print(n, {k: (round(v['mean'], 4), round(v['sd'], 4), v.get('cover')) for k, v in E2[str(n)].items() if k != 'rows'}, flush=True)
    json.dump(dict(pop=pop, pid=pid, desc=desc, E2=E2, dbins=dbins.tolist(), dxbins=dxbins.tolist(),
                   P=dict(s=Rj.P['s'], theta=Rj.P['theta'], tau=Rj.P['tau'], F_LO=Rj.F_LO, F_HI=Rj.F_HI, T=Rj.T,
                          SIG_R=Rj.SIG_R, R_EDGES=Rj.R_EDGES.tolist(), B1=Rj.B1, BR=Rj.BR.tolist(), BD=Rj.BD.tolist(),
                          NBIG=NBIG, NS=NS, REPS=REPS, B=B)),
              open('rrjedha_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
