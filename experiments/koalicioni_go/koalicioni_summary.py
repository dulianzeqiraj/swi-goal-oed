"""Summary of KOALICIONI-GO (review 56): res/runs{,_drift}_N.json -> res/koalicioni_summary{,_drift}.json."""
import os, sys, json, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import koalicioni as K

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
R = json.load(open(os.path.join(HERE, 'res', f'runs{K.TAG}_{N}.json')))
NAMES = [h['name'] for h in K.B.HOLDERS[1:]]
SHORT = ['agency', 'irrigators', 'hotels', 'municipal', 'research']


def ci(x):
    x = np.asarray(x, float)
    return [float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))]


key = lambda s: ','.join(map(str, s))
S = dict(n_worlds=N, scenario='local coastal drift' if K.DRIFT else 'drift known from physics', names=NAMES,
         holders=[dict(name=h['name'], records=h['nw'] * h['ns'], d_km=list(h['d']), p_high=h['p']) for h in K.B.HOLDERS],
         costs=list(K.COSTS), nrep=K.NREP, eps=list(K.EPS), lam=K.LAM_C, sigmas=list(K.SIGMAS))
S['host_loss'] = ci([r['L0'] for r in R])
# coalitions: singles, pairs, grand
S['singles'] = [dict(name=NAMES[k], V=ci([r['V'][str(k)] for r in R]), R=ci([r['R'][str(k)] for r in R]),
                     treated=ci([r['treated'][k] for r in R])) for k in range(K.NH)]
grand = key(range(K.NH))
S['grand'] = dict(V=ci([r['V'][grand] for r in R]), R=ci([r['R'][grand] for r in R]))
S['pairs'] = {}
for a, b in itertools.combinations(range(K.NH), 2):
    pk = f'{a}{b}'
    pr = np.array([r['pairs'][pk]['pred'] for r in R]); re = np.array([r['pairs'][pk]['real'] for r in R]); eg = np.array([r['pairs'][pk]['eig'] for r in R])
    S['pairs'][f'{SHORT[a]}+{SHORT[b]}'] = dict(pred=ci(pr), real=ci(re), eig=ci(eg), share_pos_pred=float(np.mean(pr > 0)), share_pos_real=float(np.mean(re > 0)))
# calibration of coalition values
allV = np.array([[r['V'][key(s)] for s in K.SUBSETS[1:]] for r in R]); allR = np.array([[r['R'][key(s)] for s in K.SUBSETS[1:]] for r in R])
S['calibration'] = dict(pred=float(allV.mean()), real=float(allR.mean()), slope=float(np.polyfit(allV.ravel(), allR.ravel(), 1)[0]),
                        corr=float(np.corrcoef(allV.ravel(), allR.ravel())[0, 1]))
# policies
S['policies'] = {}
for c in K.COSTS:
    cs = str(c)
    row = {}
    for p in ['single', 'greedy', 'optimal', 'adaptive', 'all', 'oracle']:
        row[p] = ci([r['pol'][cs][p]['net'] for r in R])
    row['adaptive_size'] = ci([r['pol'][cs]['adaptive']['size'] for r in R])
    row['optimal_size'] = ci([len(r['pol'][cs]['optimal']['set']) for r in R])
    row['greedy_size'] = ci([len(r['pol'][cs]['greedy']['set']) for r in R])
    row['adaptive_minus_optimal'] = ci([r['pol'][cs]['adaptive']['net'] - r['pol'][cs]['optimal']['net'] for r in R])
    row['optimal_minus_greedy'] = ci([r['pol'][cs]['optimal']['net'] - r['pol'][cs]['greedy']['net'] for r in R])
    row['optimal_minus_single'] = ci([r['pol'][cs]['optimal']['net'] - r['pol'][cs]['single']['net'] for r in R])
    row['greedy_differs'] = float(np.mean([set(r['pol'][cs]['greedy']['set']) != set(r['pol'][cs]['optimal']['set']) for r in R]))
    row['optimal_has_pair_HM'] = float(np.mean([{2, 3} <= set(r['pol'][cs]['optimal']['set']) for r in R]))
    S['policies'][cs] = row
# fair shares
shV = np.array([r['shapV'] for r in R]); shR = np.array([r['shapR'] for r in R]); bzV = np.array([r['banzV'] for r in R])
S['shapley'] = dict(pred=[ci(shV[:, k]) for k in range(K.NH)], real=[ci(shR[:, k]) for k in range(K.NH)], banzhaf=[ci(bzV[:, k]) for k in range(K.NH)],
                    corr_pred_real=float(np.corrcoef(shV.ravel(), shR.ravel())[0, 1]),
                    per_record=[ci(shV[:, k] / (h['nw'] * h['ns'])) for k, h in enumerate(K.B.HOLDERS[1:])],
                    host_share=ci([r['hostShareV'] for r in R]), convex=float(np.mean([r['convV'] for r in R])),
                    core=float(np.mean([r['coreV'] for r in R])), convex_real=float(np.mean([r['convR'] for r in R])),
                    core_real=float(np.mean([r['coreR'] for r in R])))
# a stable alternative: pay each holder its marginal contribution to the grand coalition, the utility keeps the rest
def marginal_rule(v):
    full = v[grand]; x = np.array([full - v[key([j for j in range(K.NH) if j != k])] for k in range(K.NH)]); x0 = full - x.sum()
    ok = x0 >= -1e-12 and (x >= -1e-12).all()
    for s in K.SUBSETS[1:]:
        ok = ok and (x0 + x[list(s)].sum() >= v[key(s)] - 1e-12)
    return ok, (x0 / full if full > 0 else 0.0)
def pair_rule(v):
    # the complementary pair hotels (2) + municipal (3) is paid once, jointly, its marginal contribution to the grand
    # coalition, split in proportion to the two individual marginal contributions; the others as in marginal_rule
    full = v[grand]; x = np.array([full - v[key([j for j in range(K.NH) if j != k])] for k in range(K.NH)])
    joint = full - v[key([0, 1, 4])]; wt = np.clip(x[[2, 3]], 0, None); wt = wt / wt.sum() if wt.sum() > 0 else np.array([0.5, 0.5])
    x[[2, 3]] = joint * wt; x0 = full - x.sum()
    ok = x0 >= -1e-12 and (x >= -1e-12).all()
    for s in K.SUBSETS[1:]:
        ok = ok and (x0 + x[list(s)].sum() >= v[key(s)] - 1e-12)
    return ok, (x0 / full if full > 0 else 0.0)
pr_ = [pair_rule(r['V']) for r in R]; prR = [pair_rule(r['R']) for r in R]
S['pair_rule'] = dict(core=float(np.mean([m[0] for m in pr_])), host_share=ci([m[1] for m in pr_]), core_real=float(np.mean([m[0] for m in prR])))
mr = [marginal_rule(r['V']) for r in R]; mrR = [marginal_rule(r['R']) for r in R]
S['marginal_rule'] = dict(core=float(np.mean([m[0] for m in mr])), host_share=ci([m[1] for m in mr]), core_real=float(np.mean([m[0] for m in mrR])))
S['robustness'] = {sg: dict(shapley=ci([r['rob'][sg]['shapley'] for r in R]), banzhaf=ci([r['rob'][sg]['banzhaf'] for r in R]),
                            banzhaf_minus_shapley=ci([r['rob'][sg]['banzhaf'] - r['rob'][sg]['shapley'] for r in R])) for sg in R[0]['rob']}
# privacy (noise once per holder on clipped whitened information)
S['privacy'] = {}
for e in R[0]['priv']:
    S['privacy'][e] = dict(shapley_tau=ci([r['priv'][e]['shapley_tau'] for r in R]),
                           **{c: dict(net=ci([r['priv'][e][c]['net'] for r in R]), same=float(np.mean([r['priv'][e][c]['same'] for r in R]))) for c in map(str, K.COSTS)})
clipbias = np.array([[r['Vclip'][key(s)] - r['V'][key(s)] for s in K.SUBSETS[1:]] for r in R])
S['clip'] = dict(conservative=float(np.mean(clipbias <= 1e-12)), mean_bias=float(clipbias.mean()))
json.dump(S, open(os.path.join(HERE, 'res', f'koalicioni_summary{K.TAG}.json'), 'w'), indent=1)

print(S['scenario'], '| host loss', S['host_loss'])
for x in S['singles']:
    print(f"  {x['name']:24s} treated {x['treated'][0]:.2f}  V {x['V'][0]:.4f}  R {x['R'][0]:+.4f} ± {x['R'][1]:.4f}")
print('  grand', S['grand'])
for k, v in S['pairs'].items():
    print(f"  pair {k:22s} synergy pred {v['pred'][0]:+.4f}  real {v['real'][0]:+.4f} ± {v['real'][1]:.4f}  EIG {v['eig'][0]:+.3f}  P(pred>0) {v['share_pos_pred']:.2f} P(real>0) {v['share_pos_real']:.2f}")
print('calibration', S['calibration'])
for c, row in S['policies'].items():
    print(f"cost {c}: " + '  '.join(f"{p} {row[p][0]:+.4f}" for p in ['single', 'greedy', 'optimal', 'adaptive', 'all', 'oracle']),
          f"| sizes opt {row['optimal_size'][0]:.2f} adapt {row['adaptive_size'][0]:.2f} | adapt-opt {row['adaptive_minus_optimal'][0]:+.4f}±{row['adaptive_minus_optimal'][1]:.4f} opt-greedy {row['optimal_minus_greedy'][0]:+.4f}±{row['optimal_minus_greedy'][1]:.4f} opt-single {row['optimal_minus_single'][0]:+.4f}±{row['optimal_minus_single'][1]:.4f} greedy differs {row['greedy_differs']:.2f} HM in opt {row['optimal_has_pair_HM']:.2f}")
print('shapley pred', [round(x[0], 4) for x in S['shapley']['pred']], 'real', [round(x[0], 4) for x in S['shapley']['real']], 'banzhaf', [round(x[0], 4) for x in S['shapley']['banzhaf']])
print('  per record', [round(x[0], 5) for x in S['shapley']['per_record']], 'host share', S['shapley']['host_share'], 'convex', S['shapley']['convex'], 'core', S['shapley']['core'], 'corr', round(S['shapley']['corr_pred_real'], 3), 'real convex/core', S['shapley']['convex_real'], S['shapley']['core_real'])
print('marginal rule', S['marginal_rule'], 'pair rule', S['pair_rule'])
print('robustness', {k: (round(v['shapley'][0], 3), round(v['banzhaf'][0], 3), round(v['banzhaf_minus_shapley'][0], 4), round(v['banzhaf_minus_shapley'][1], 4)) for k, v in S['robustness'].items()})
for e, v in S['privacy'].items():
    print(f"privacy eps {e}: shapley tau {v['shapley_tau'][0]:.2f} | " + '  '.join(f"c{c}: net {v[c]['net'][0]:+.4f} same {v[c]['same']:.2f}" for c in map(str, K.COSTS)))
print('clip', S['clip'])
