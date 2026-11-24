"""Aggregate kalibgo_runs.json into kalibgo_results.json and print tables."""
import json
import numpy as np
import kalibgo as KG
D = json.load(open('kalibgo_runs.json'))
recs = D['recs']
METH = ['bayes', 'safe10', 'bag', 'kalib', 'oracle']

def agg(get):
    v = lambda f: np.array([f(get(r)) for r in recs], float)
    err = v(lambda x: x['err'])
    out = dict(err_med=float(np.median(err)), p90=float(np.percentile(err, 90)), cov=float(np.mean(v(lambda x: x['cov']))),
               wid=float(np.median(v(lambda x: x['wid']))), eta=float(np.median(v(lambda x: x['eta']))))
    x0 = get(recs[0])
    if 'deg' in x0:
        out['deg'] = float(np.mean(v(lambda x: x['deg']))); out['s2'] = float(np.median(v(lambda x: x['s2'])))
    return out

out = {'n_truths': len(recs), 'sig': D['sig'], 'NE_BASE': D['NE_BASE'], 'B': D['B'],
       'ETAS': [float(e) for e in KG.ETAS], 'E1': {}, 'E2': {}, 'bootcov': {}}
for ne in D['NES']:
    out['E1'][str(ne)] = {m: agg(lambda r, ne=ne, m=m: r['E1'][str(ne)][m]) for m in METH}
    bc = np.array([r['E1'][str(ne)]['kalib']['bootcov'] for r in recs])
    out['bootcov'][str(ne)] = {'med': np.median(bc, 0).tolist(), 'q25': np.quantile(bc, 0.25, 0).tolist(), 'q75': np.quantile(bc, 0.75, 0).tolist()}
out['E2']['base'] = {m: agg(lambda r, m=m: r['E1'][str(D['NE_BASE'])][m]) for m in METH}
for a in ['coast', 'near', 'spread']:
    out['E2'][a] = {m: agg(lambda r, a=a, m=m: r['E2'][a][m]) for m in METH}

print('E1  ne  method   err_med  p90   cov90  width90  deg   s2    eta')
for ne in D['NES']:
    for m in METH:
        a = out['E1'][str(ne)][m]
        print(f"   {ne:4d} {m:7s} {a['err_med']:7.1f} {a['p90']:6.1f}  {a['cov']:.2f}  {a['wid']:7.1f}  {a.get('deg', 0):4.1f} {a.get('s2', 0):.3f} {a['eta']:.3f}")
print('E2  addition method err_med p90 cov90 width90 eta')
for a in ['base', 'coast', 'near', 'spread']:
    for m in METH:
        x = out['E2'][a][m]
        print(f"   {a:7s} {m:7s} {x['err_med']:7.1f} {x['p90']:6.1f}  {x['cov']:.2f}  {x['wid']:7.1f}  eta {x['eta']:.3f}")

# design decision: each pipeline picks the addition with the largest reduction of its own interval width,
# then infers the toe with its own method; realized error and coverage follow.
ADDS = ['coast', 'near', 'spread']
dec = {}
for m in ['bayes', 'safe10', 'bag', 'kalib']:
    picks, errs, covs, wids, worth_all = [], [], [], [], []
    for r in recs:
        base = r['E1'][str(D['NE_BASE'])][m]['wid']
        worth = [base - r['E2'][a][m]['wid'] for a in ADDS]
        worth_all.append(worth)
        a = ADDS[int(np.argmax(worth))]
        picks.append(a); errs.append(r['E2'][a][m]['err']); covs.append(r['E2'][a][m]['cov']); wids.append(r['E2'][a][m]['wid'])
    errs = np.array(errs); wa = np.array(worth_all)
    dec[m] = {'pick_frac': {a: float(np.mean([p == a for p in picks])) for a in ADDS},
              'worth_med': {a: float(np.median(wa[:, i])) for i, a in enumerate(ADDS)},
              'err_med': float(np.median(errs)), 'p90': float(np.percentile(errs, 90)), 'cov': float(np.mean(covs)),
              'wid': float(np.median(wids))}
out['decision'] = dec
json.dump(out, open('kalibgo_results.json', 'w'), indent=1)
print('decision pipelines:')
for m, x in dec.items():
    print(f"   {m:7s} picks {x['pick_frac']}  worth {x['worth_med']}  err_med {x['err_med']:.1f}  p90 {x['p90']:.1f}  cov {x['cov']:.2f}  wid {x['wid']:.0f}")
