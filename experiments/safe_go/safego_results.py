"""Aggregate safego_runs.json into safego_results.json and print tables."""
import json
import numpy as np
D = json.load(open('safego_runs.json'))
recs = D['recs']
METH = ['bayes', 'safe', 'safe10', 'oracle']

def agg(get):
    v = lambda f: np.array([f(get(r)) for r in recs], float)
    err = v(lambda x: x['err'])
    return dict(err_med=float(np.median(err)), p90=float(np.percentile(err, 90)), rmse=float(np.sqrt(np.mean(err ** 2))), cov=float(np.mean(v(lambda x: x['cov']))),
                wid=float(np.median(v(lambda x: x['wid']))), deg=float(np.mean(v(lambda x: x['deg']))),
                s2=float(np.median(v(lambda x: x['s2']))), eta=float(np.median(v(lambda x: x['eta']))))

out = {'n_truths': len(recs), 'sig': D['sig'], 'NE_BASE': D['NE_BASE'], 'E1': {}, 'E2': {}}
for ne in D['NES']:
    out['E1'][str(ne)] = {m: agg(lambda r, ne=ne, m=m: r['E1'][str(ne)][m]) for m in METH}
out['E2']['base'] = {m: agg(lambda r, m=m: r['E1'][str(D['NE_BASE'])][m]) for m in METH}
for a in ['coast', 'near', 'spread']:
    out['E2'][a] = {m: agg(lambda r, a=a, m=m: r['E2'][a][m]) for m in METH}
json.dump(out, open('safego_results.json', 'w'), indent=1)
print('E1  ne  method   err_med  rmse   cov90  width90  deg   s2    eta')
for ne in D['NES']:
    for m in METH:
        a = out['E1'][str(ne)][m]
        print(f"   {ne:4d} {m:7s} {a['err_med']:7.1f} {a['rmse']:6.1f}  {a['cov']:.2f}  {a['wid']:7.1f}  {a['deg']:4.1f} {a['s2']:.3f} {a['eta']:.3f}")
print('E2  addition method err_med rmse cov90 width90')
for a in ['base', 'coast', 'near', 'spread']:
    for m in METH:
        x = out['E2'][a][m]
        print(f"   {a:7s} {m:7s} {x['err_med']:7.1f} {x['rmse']:6.1f}  {x['cov']:.2f}  {x['wid']:7.1f}  deg {x['deg']:.1f} eta {x['eta']:.3f}")

# ---- design decision: each pipeline picks the addition with the largest width reduction (its own
# apparent data worth), then infers the toe with its own method; realized error and coverage follow.
ADDS = ['coast', 'near', 'spread']
dec = {}
for m in ['bayes', 'safe10']:
    picks, errs, covs = [], [], []
    for r in recs:
        base = r['E1'][str(D['NE_BASE'])][m]['wid']
        worth = [base - r['E2'][a][m]['wid'] for a in ADDS]
        a = ADDS[int(np.argmax(worth))]
        picks.append(a); errs.append(r['E2'][a][m]['err']); covs.append(r['E2'][a][m]['cov'])
    errs = np.array(errs)
    dec[m] = {'pick_frac': {a: float(np.mean([p == a for p in picks])) for a in ADDS},
              'err_med': float(np.median(errs)), 'p90': float(np.percentile(errs, 90)), 'rmse': float(np.sqrt(np.mean(errs ** 2))), 'cov': float(np.mean(covs))}
out['decision'] = dec
json.dump(out, open('safego_results.json', 'w'), indent=1)
print('decision pipelines:')
for m, x in dec.items():
    print(f"   {m:7s} picks {x['pick_frac']}  err_med {x['err_med']:.1f}  p90 {x['p90']:.1f}  cov {x['cov']:.2f}")
