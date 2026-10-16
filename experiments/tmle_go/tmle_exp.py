"""TMLE-GO experiments. T1: estimators of psi_d for three regimes (n = 2000, 500 data sets).
T2: monitoring design (what is recorded at the reviews) for the risk difference psi_hi - psi_lo,
at several numbers of wells. Writes tmle_results.json."""
import json, sys, time, warnings
import numpy as np
from multiprocessing import Pool
import tmle_go as T
warnings.filterwarnings('ignore')
N1, R1 = 2000, 500
NS2, R2 = [500, 1000, 2000, 4000, 8000], 200
DESIGNS = ['op', 'precise', 'op+D', 'precise+D']
NTRUTH = 400000


def job1(seed):
    rng = np.random.default_rng(seed); d = T.simulate(N1, rng)
    out = {reg: T.estimate(d, reg) for reg in T.REGIMES}
    out['nfollow'] = {reg: None for reg in T.REGIMES}
    out['cens'] = float(d['cens'].any(axis=1).mean()); out['nrev'] = float(d['reach'].sum(axis=1).mean())
    return out


def job2(args):
    n, seed = args
    rng = np.random.default_rng(seed); d = T.simulate(n, rng)
    res = {}
    for des in DESIGNS:
        h = T.estimate(d, 'hi', design=des, kinds=('flex',)); l = T.estimate(d, 'lo', design=des, kinds=('flex',))
        res[des] = dict(rd=h['tmle_flex'] - l['tmle_flex'], se=float(np.hypot(h['se_flex'], l['se_flex'])),
                        rd_ipw=h['ipw'] - l['ipw'], rd_naive=h['naive'] - l['naive'])
    return res


if __name__ == '__main__':
    t0 = time.time(); rng = np.random.default_rng(20261016)
    truth = {reg: T.truth(reg, NTRUTH, rng) for reg in T.REGIMES}
    print('truth', truth, f'{time.time() - t0:.0f}s', flush=True)
    with Pool(4) as pool:
        o1 = pool.map(job1, range(10000, 10000 + R1), chunksize=4)
    print('T1 done', f'{time.time() - t0:.0f}s', flush=True)
    T1 = {}
    for reg in T.REGIMES:
        T1[reg] = {}
        for k in ['naive', 'ipw', 'gcomp_mis', 'gcomp_flex', 'tmle_mis', 'tmle_flex']:
            v = np.array([o[reg][k] for o in o1]); e = dict(bias=float(v.mean() - truth[reg]), sd=float(v.std()),
                                                         rmse=float(np.sqrt(np.mean((v - truth[reg]) ** 2))))
            if k.startswith('tmle'):
                se = np.array([o[reg]['se_' + k[5:]] for o in o1])
                e['meanse'] = float(se.mean()); e['cover'] = float(np.mean(np.abs(v - truth[reg]) <= 1.96 * se))
            T1[reg][k] = e
            print(reg, k, {a: round(b, 3) for a, b in e.items()}, flush=True)
    T2 = {}
    jobs = [(n, 50000 + 1000 * i + r) for i, n in enumerate(NS2) for r in range(R2)]
    with Pool(4) as pool:
        o2 = pool.map(job2, jobs, chunksize=2)
    rd = truth['hi'] - truth['lo']
    for i, n in enumerate(NS2):
        oo = o2[i * R2:(i + 1) * R2]; T2[str(n)] = {}
        for des in DESIGNS:
            v = np.array([o[des]['rd'] for o in oo]); se = np.array([o[des]['se'] for o in oo])
            T2[str(n)][des] = dict(bias=float(v.mean() - rd), sd=float(v.std()), rmse=float(np.sqrt(np.mean((v - rd) ** 2))),
                                   meanse=float(se.mean()), cover=float(np.mean(np.abs(v - rd) <= 1.96 * se)),
                                   bias_naive=float(np.mean([o[des]['rd_naive'] for o in oo]) - rd),
                                   bias_ipw=float(np.mean([o[des]['rd_ipw'] for o in oo]) - rd))
            print(n, des, {a: round(b, 3) for a, b in T2[str(n)][des].items()}, flush=True)
    meta = dict(cens=float(np.mean([o['cens'] for o in o1])), nrev=float(np.mean([o['nrev'] for o in o1])))
    P = dict(H=T.H, RHO=T.RHO, JMAX=T.JMAX, F_LO=T.F_LO, F_HI=T.F_HI, F_PRE=T.F_PRE, s=T.P['s'], theta=T.P['theta'],
             tau=T.P['tau'], SIG_OP=T.SIG_OP, SIG_PRECISE=T.SIG_PRECISE, B=[T.B0, T.B1, T.B2, T.B3, T.BW],
             C=[T.C0, T.C1], XSTAR=T.XSTAR, N1=N1, R1=R1, NS2=NS2, R2=R2, NTRUTH=NTRUTH)
    json.dump(dict(truth=truth, rd=rd, T1=T1, T2=T2, meta=meta, P=P), open('tmle_results.json', 'w'), indent=1,
              allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
