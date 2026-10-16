"""KTHIMI-GO experiment. Writes kthimi_results.json.
Designs: reading noise sigma in {0, 0.01, 0.02, 0.04, 0.08, 0.16} x operator responsiveness kappa in
{0.5, 1, 2, 3}, plus no monitoring. For each design the intercept is calibrated (30 000 wells, common random
numbers) so that mean pumping equals that of the reference design (sigma = 0.02, kappa = 1, intercept 0); then
200 000 wells x 10 years give the risk, the supply and the exact sensor and feedback information."""
import json, time
import numpy as np
from multiprocessing import Pool
from scipy.stats import spearmanr
import kthimi as K

SIGS, KAPS, N = [0.0, 0.01, 0.02, 0.04, 0.08, 0.16], [0.5, 1.0, 2.0, 3.0], 200000
for p in ('../rrjedha_go/rrjedha_results.json', '../rrjedha/rrjedha_results.json'):
    try:
        DB = np.array(json.load(open(p))['dbins']); break
    except FileNotFoundError:
        continue


def job(args):
    sig, kap, nomon, target, seed = args
    b0 = K.calibrate(target, sig, kap, nomon, DB)
    d = K.simulate(N, np.random.default_rng(seed), sig, kap, b0, nomon, DB)
    inf = K.information(d, sig, kap, b0, nomon)
    return dict(sig=sig, kappa=kap, nomon=nomon, b0=b0, risk=d['risk'], supply=d['supply'],
                se=float(np.sqrt(d['risk'] * (1 - d['risk']) / N)), **inf)


if __name__ == '__main__':
    t0 = time.time()
    ref = K.simulate(N, np.random.default_rng(1), 0.02, 1.0, 0.0, False, DB, keep=False)
    target = ref['supply']
    print('target supply', round(target, 4), 'reference risk', round(ref['risk'], 4), flush=True)
    jobs = [(s, k, False, target, 1000 + 10 * i + j) for i, s in enumerate(SIGS) for j, k in enumerate(KAPS)]
    jobs.append((0.0, 1.0, True, target, 999))
    with Pool(4) as pool:
        res = pool.map(job, jobs)
    nm = [r for r in res if r['nomon']][0]
    for r in res:
        r['gain'] = nm['risk'] - r['risk']
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    mon = [r for r in res if not r['nomon']]
    rho_fb = spearmanr([r['feedback'] for r in mon], [r['risk'] for r in mon]).correlation
    rho_se = spearmanr([r['sensor'] for r in mon], [r['risk'] for r in mon]).correlation
    print('spearman risk~feedback', round(rho_fb, 3), 'risk~sensor', round(rho_se, 3), f'{time.time() - t0:.0f}s')
    json.dump(dict(target=target, ref_risk=ref['risk'], designs=res, rho_feedback=rho_fb, rho_sensor=rho_se,
                   P=dict(SIGS=SIGS, KAPS=KAPS, N=N)), open('kthimi_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
