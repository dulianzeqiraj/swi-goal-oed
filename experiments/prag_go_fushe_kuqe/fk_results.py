"""Collect the Fushe-Kuqe PRAG-GO results into results_raw.json and results_summary.csv."""
import json, csv, os
import numpy as np
from scipy.stats import spearmanr

NAMES = ['area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS']
GOALS = ['rA', 'rAB', 'rArea']
PRIORS = ['base', 'rho805', 'fine']


def H(p):
    return float(-(p * np.log(p) + (1 - p) * np.log(1 - p)))


res = {}
for pr in PRIORS:
    d = f'res_{pr}'
    if not os.path.exists(f'{d}/d5.npz'):
        continue
    M = json.load(open(f'{d}/meta.json')); ids = np.array(M['ids']); CAND = np.array(M['CAND'])
    R3 = np.load(f'{d}/d3.npz'); R5 = np.load(f'{d}/d5.npz')
    LIN3, EX3, D3 = R3['LIN'], R3['EX'], R3['D']
    LIN5, D5, pool, EXp = R5['LIN'], R5['D'], list(R5['pool']), R5['EXp']
    inner = np.load(f'{d}/ens.npz')['inner']
    out = {'P0': M['P0'], 'H0': [H(p) for p in M['P0']], 'A': ids[M['iA']], 'B': ids[M['iB']],
           'pB': float((inner[:, M['iB']] < 1.0).mean())}
    w = lambda d: [str(ids[CAND[v]]) for v in d]
    out['opt3'] = {g: {'val': float(EX3[:, k].max()), 'design': w(D3[int(EX3[:, k].argmax())]), 'ess': float(EX3[int(EX3[:, k].argmax()), 3])}
                   for k, g in enumerate(GOALS)}
    out['c3'] = {}
    for j, nm in enumerate(NAMES):
        i = int(LIN3[:, j].argmax())
        out['c3'][nm] = {'design': w(D3[i]), **{g: float(EX3[i, k] / EX3[:, k].max()) for k, g in enumerate(GOALS)},
                         **{'rho_' + g: float(spearmanr(LIN3[:, j], EX3[:, k]).correlation) for k, g in enumerate(GOALS)}}
    ref = [max(EXp[:, k].max(), R5['gval'][k]) for k in range(3)]
    out['best5'] = {g: {'val': float(ref[k]), 'design': w(R5['gbest'][k])} for k, g in enumerate(GOALS)}
    pub = int(R5['pub'])
    out['c5'] = {'published': {'design': w(D5[pub]), **{g: float(EXp[pool.index(pub), k] / ref[k]) for k, g in enumerate(GOALS)},
                               'ess': float(EXp[pool.index(pub), 3])}}
    for j, nm in enumerate(NAMES):
        i = int(LIN5[:, j].argmax())
        out['c5'][nm] = {'design': w(D5[i]), **{g: float(EXp[pool.index(i), k] / ref[k]) for k, g in enumerate(GOALS)},
                         'ess': float(EXp[pool.index(i), 3])}
    out['pool_size'] = len(pool)
    # rank correlation on the random part of the 5-well pool (3000 random designs + the top picks)
    for j, nm in enumerate(NAMES):
        out['c5'][nm]['rho_rAB'] = float(spearmanr(LIN5[pool, j], EXp[:, 1]).correlation)
    if os.path.exists(f'{d}/conv.json'):
        out['conv'] = json.load(open(f'{d}/conv.json'))
    res[pr] = out
mar = json.load(open('res_base/mar.json')) if os.path.exists('res_base/mar.json') else None
json.dump({'res': res, 'mar': mar}, open('results_raw.json', 'w'), indent=1)

with open('results_summary.csv', 'w', newline='') as f:
    wr = csv.writer(f, lineterminator='\n')
    wr.writerow(['prior', 'budget', 'criterion', 'design', 'pct_opt_riskA', 'pct_opt_riskAorB', 'pct_opt_area_gt_100'])
    for pr, o in res.items():
        for nm, r in o['c3'].items():
            wr.writerow([pr, 3, nm, ' '.join(r['design'])] + [f"{100 * r[g]:.1f}" for g in GOALS])
        for nm, r in o['c5'].items():
            wr.writerow([pr, 5, nm, ' '.join(r['design'])] + [f"{100 * r[g]:.1f}" for g in GOALS])
        wr.writerow([pr, 3, 'exact_optimum_nats', ''] + [f"{o['opt3'][g]['val']:.4f}" for g in GOALS])
        wr.writerow([pr, 5, 'best_found_nats', ''] + [f"{o['best5'][g]['val']:.4f}" for g in GOALS])
    if mar:
        wr.writerow([])
        wr.writerow(['MAR design', 'sites', 'Q_m3_per_day_per_site', 'P_A', 'P_B', 'P_A_or_B', 'mean_area_km2'])
        wr.writerow(['none', '', 0, mar['base']['pA'], mar['base']['pB'], mar['base']['pAB'], f"{mar['base']['area']:.2f}"])
        for k in ['area', 'prag', 'ens']:
            for r in mar[k]['rows']:
                wr.writerow([k, ' '.join(mar[k]['ids']), r['Q'], r['pA'], r['pB'], r['pAB'], f"{r['area']:.2f}"])
for pr, o in res.items():
    print(pr, 'P0', np.round(o['P0'], 3), '| 3w area->rArea %.3f rAB %.3f rA %.3f | prag rAB %.3f | 5w pub rArea %.3f rAB %.3f rA %.3f | prag5 rAB %.3f' % (
        o['c3']['area']['rArea'], o['c3']['area']['rAB'], o['c3']['area']['rA'], o['c3']['pragLin']['rAB'],
        o['c5']['published']['rArea'], o['c5']['published']['rAB'], o['c5']['published']['rA'], o['c5']['pragLin']['rAB']))
