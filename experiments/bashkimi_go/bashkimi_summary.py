"""Summary of BASHKIMI-GO (review 55): res/runs_200.json and res/mpc_40.json -> res/bashkimi_summary.json."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bashkimi as B

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
R = json.load(open(os.path.join(HERE, 'res', f'runs{B.TAG}_{N}.json')))
NAMES = {1: 'Monitoring agency', 2: 'Private irrigators', 3: 'Coastal hotels', 4: 'Research campaign'}
K = len(B.CAND)
G = np.array([[x['gain'] for x in r['rows']] for r in R])            # expected gain (30 data draws)
G1 = np.array([[x['gain1'] for x in r['rows']] for r in R])           # one data draw
best = G.max(1)


def ci(x):
    x = np.asarray(x, float)
    return float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))


def picks_of(key):
    return np.array([int(np.argmax([x[key] for x in r['rows']])) for r in R])


S = dict(n_worlds=N, holders=[dict(name=h['name'], wells=h['nw'], seasons=h['ns'], records=h['nw'] * h['ns'],
                                   d_km=list(h['d']), p_high=h['p']) for h in B.HOLDERS],
         n_targets=B.NT, target_d=list(B.TARGET_D), t_tol=B.T_TOL, c_cap=B.C_CAP, nrep=B.NREP,
         n_field_nodes=B.NU, n_params=B.PB + B.PT + B.NU)
cal = B.load_calib()
S['calib'] = dict(rel_sd=float(np.sqrt(cal['rel_var'])), spatial_share=float(cal['s_gp'] ** 2 / cal['rel_var']),
                  range_km=float(cal['ell']), corr=[float(c) for c in cal['corr']], mid=[float(c) for c in cal['mid']])
S['host'] = dict(loss=ci([r['L0'] for r in R]), oracle_loss=ci([r['oracle_loss'] for r in R]),
                 allow=ci([r['host_allow'] for r in R]), n_coast=ci([r['n_coast'] for r in R]))

# ------------------------------------------------------------------ candidates
S['candidates'] = []
for j, k in enumerate(B.CAND):
    rows = [r['rows'][j] for r in R]
    S['candidates'].append(dict(
        k=k, name=NAMES[k], n=rows[0]['n'], treated=ci([x['treated'] for x in rows]),
        gain=ci(G[:, j]), value=ci([x['value'] for x in rows]), eig_all=ci([x['eig_all'] for x in rows]),
        eig_cate=ci([x['eig_cate'] for x in rows]), eig_goal=ci([x['eig_goal'] for x in rows]),
        best_share=float(np.mean(np.argmax(G, 1) == j)),
        info_alone=ci([x['overlap']['alone'] for x in rows]), info_merged=ci([x['overlap']['merged'] for x in rows]),
        info_sumsep=ci([x['overlap']['sumsep'] for x in rows]),
        synergy=ci([x['overlap']['merged'] - x['overlap']['sumsep'] for x in rows]),
        superadditive=float(np.mean([x['overlap']['merged'] >= x['overlap']['sumsep'] - 1e-9 for x in rows]))))
S['host_info'] = ci([r['rows'][0]['overlap']['host'] for r in R])

# ------------------------------------------------------------------ criteria
crit = [('n', 'Largest dataset'), ('eig_all', 'EIG of all parameters'),
        ('eig_cate', 'EIG of the CATE parameters (anchor)'), ('eig_goal', 'Mean EIG of the target CATEs'),
        ('value', 'BASHKIMI-GO decision value')]
pv = picks_of('value'); gv = G[np.arange(N), pv]
S['criteria'] = []
for key, lab in crit:
    pk = picks_of(key); g = G[np.arange(N), pk]
    S['criteria'].append(dict(key=key, label=lab, picks={NAMES[B.CAND[j]]: int(np.sum(pk == j)) for j in range(K)},
                              gain=ci(g), regret=ci(best - g), p_best=float(np.mean(g >= best - 1e-12)),
                              diff_vs_value=ci(gv - g), agree_value=float(np.mean(pk == pv))))
rng = np.random.default_rng(0)
S['random'] = dict(gain=ci(G.mean(1)), regret=ci(best - G.mean(1)))
S['oracle'] = dict(gain=ci(best))
# rank agreement with the expected gains
from scipy.stats import kendalltau
S['kendall'] = {}
for key, lab in crit[1:]:
    tt = [kendalltau([x[key] for x in r['rows']], G[i]).statistic for i, r in enumerate(R)]
    S['kendall'][key] = float(np.nanmean(tt))
# calibration of the predicted value
P = np.array([[x['value'] for x in r['rows']] for r in R])
S['calibration'] = dict(pred_mean=float(P.mean()), real_mean=float(G.mean()), corr=float(np.corrcoef(P.ravel(), G.ravel())[0, 1]),
                        slope=float(np.polyfit(P.ravel(), G.ravel(), 1)[0]),
                        by_candidate=[dict(name=NAMES[k], pred=float(P[:, j].mean()), real=float(G[:, j].mean()))
                                      for j, k in enumerate(B.CAND)])
# disagreement analysis: worlds where the decision value and the anchor's criterion choose differently
pa = picks_of('eig_cate'); dis = pa != pv
S['disagree'] = dict(share=float(dis.mean()), diff=ci((gv - G[np.arange(N), pa])[dis]),
                     value_picks={NAMES[B.CAND[j]]: int(np.sum(pv[dis] == j)) for j in range(K)},
                     anchor_picks={NAMES[B.CAND[j]]: int(np.sum(pa[dis] == j)) for j in range(K)})

# ------------------------------------------------------------------ privacy
S['privacy'] = dict(eps=list(B.EPS), delta=B.DELTA, lam=list(B.LAM_CS), gm={str(e): float(B.GM[e]) for e in B.EPS},
                    BE2=float(R[0]['BE2']), dV={lc: ci([r['dV'][lc] for r in R]) for lc in R[0]['dV']})
mech = {}
def eval_pick(vals):
    pk = np.argmax(vals, 1); g = G[np.arange(N), pk]
    return dict(gain=ci(g), agree=float(np.mean(pk == pv)), keep=float(g.mean() / gv.mean()))
for e in B.EPS:
    mech[f'A_{e}'] = eval_pick(np.array([[x['priv'][f'A{e}'] for x in r['rows']] for r in R]))
    for lc in B.LAM_CS:
        mech[f'B{lc}_{e}'] = eval_pick(np.array([[x['priv'][f'B{lc}_{e}'] for x in r['rows']] for r in R]))
        mech[f'C{lc}_{e}'] = eval_pick(np.array([[x['priv'][f'C{lc}_{e}'] for x in r['rows']] for r in R]))
for lc in B.LAM_CS:
    vals = np.array([[x['clip'][str(lc)] for x in r['rows']] for r in R])
    mech[f'clip{lc}'] = eval_pick(vals)
    mech[f'clip{lc}']['bias'] = ci((vals - P).ravel())
    mech[f'clip{lc}']['conservative'] = float(np.mean(vals <= P + 1e-12))
    mech[f'clip{lc}']['clipped_share'] = {NAMES[k]: float(np.mean([r['rows'][j]['clipped_share'][str(lc)] for r in R]))
                                          for j, k in enumerate(B.CAND)}
S['privacy']['mech'] = mech
S['value_mean_gain'] = float(gv.mean())
# go / no-go against a merge cost (decision units): merge with the best candidate only if its value exceeds the cost
S['gonogo'] = []
for cm in (0.01, 0.02, 0.03, 0.04, 0.06):
    pred_best = P[np.arange(N), pv]
    net_rule = np.where(pred_best > cm, gv - cm, 0.0)
    S['gonogo'].append(dict(cost=cm, merge_share=float(np.mean(pred_best > cm)), net_rule=ci(net_rule),
                            net_always=ci(gv - cm), net_never=0.0, net_oracle=ci(np.maximum(best - cm, 0)),
                            net_eig_always=ci(G[np.arange(N), picks_of('eig_cate')] - cm)))

# ------------------------------------------------------------------ MPC
fn = os.path.join(HERE, 'res', f'mpc{B.TAG}_40.json')
if os.path.exists(fn):
    M = json.load(open(fn))
    E = np.array([[x['mpc'] - x['float'] for x in r['rows']] for r in M])
    S['mpc'] = dict(n_worlds=len(M), max_err=float(np.abs(E).max()), mean_err=float(E.mean()),
                    same_choice=float(np.mean([np.argmax([x['mpc'] for x in r['rows']]) == np.argmax([x['float'] for x in r['rows']]) for r in M])),
                    mbytes=float(np.mean([x['mbytes'] for r in M for x in r['rows']])),
                    rounds=float(np.mean([x['rounds'] for r in M for x in r['rows']])),
                    mults=float(np.mean([x['mults'] for r in M for x in r['rows']])),
                    trunc=float(np.mean([x['trunc'] for r in M for x in r['rows']])),
                    cmp=float(np.mean([x['cmp'] for r in M for x in r['rows']])), frac_bits=20)

json.dump(S, open(os.path.join(HERE, 'res', f'bashkimi_summary{B.TAG}.json'), 'w'), indent=1)

# ------------------------------------------------------------------ print
print(f"host: loss {S['host']['loss'][0]:.3f}, oracle {S['host']['oracle_loss'][0]:.3f}, allows {S['host']['allow'][0]:.2f}")
for c in S['candidates']:
    print(f"{c['name']:20s} n {c['n']:3d} treated {c['treated'][0]:.2f} gain {c['gain'][0]:.4f}±{c['gain'][1]:.4f} "
          f"value {c['value'][0]:.4f} eigall {c['eig_all'][0]:.2f} eigcate {c['eig_cate'][0]:.2f} eiggoal {c['eig_goal'][0]:.3f} "
          f"best {c['best_share']:.2f} | info alone {c['info_alone'][0]:.2f} merged {c['info_merged'][0]:.2f} sumsep {c['info_sumsep'][0]:.2f} synergy {c['synergy'][0]:.3f} superadd {c['superadditive']:.2f}")
print('host info', S['host_info'])
for c in S['criteria']:
    print(f"{c['label']:40s} gain {c['gain'][0]:.4f}±{c['gain'][1]:.4f} regret {c['regret'][0]:.4f} P(best) {c['p_best']:.2f} "
          f"value-minus {c['diff_vs_value'][0]:+.4f}±{c['diff_vs_value'][1]:.4f} agree {c['agree_value']:.2f} picks {c['picks']}")
print('random', S['random'], 'oracle', S['oracle'])
print('kendall', S['kendall'])
print('calibration', S['calibration'])
print('disagree', S['disagree'])
print('dV', S['privacy']['dV'], 'BE2', S['privacy']['BE2'])
for e in B.EPS:
    line = f"eps {e:5}: A agree {mech[f'A_{e}']['agree']:.2f} keep {mech[f'A_{e}']['keep']:.2f} | "
    for lc in B.LAM_CS:
        line += f"B{lc} {mech[f'B{lc}_{e}']['agree']:.2f}/{mech[f'B{lc}_{e}']['keep']:.2f} C{lc} {mech[f'C{lc}_{e}']['agree']:.2f}/{mech[f'C{lc}_{e}']['keep']:.2f} | "
    print(line)
for lc in B.LAM_CS:
    x = mech[f'clip{lc}']
    print(f"clip {lc}: agree {x['agree']:.2f} keep {x['keep']:.2f} bias {x['bias'][0]:+.4f} conservative {x['conservative']:.3f} clipped share {x['clipped_share']}")
if 'mpc' in S:
    print('mpc', S['mpc'])
for x in S['gonogo']:
    print(f"merge cost {x['cost']}: rule merges {x['merge_share']:.2f}, net {x['net_rule'][0]:+.4f}±{x['net_rule'][1]:.4f}; always (value pick) {x['net_always'][0]:+.4f}; always (anchor pick) {x['net_eig_always'][0]:+.4f}; never 0; oracle {x['net_oracle'][0]:+.4f}")
