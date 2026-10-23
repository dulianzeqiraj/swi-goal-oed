"""Summary of the MJEGULLA-GO results for the review: mjegulla_summary.json (from mjegulla.json and
mjegulla_budget.json)."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
D = json.load(open('mjegulla.json'))
C = json.load(open('mjegulla_budget.json'))
S = D['setup']
B = D['B']
C_MON, C_PLAN = 3.0, 1.0          # act at the municipal wells if >= 3 expected saline; approve the sites if <= 1


def summ(kind, rule):
    v = [x[kind + ':' + rule] for x in B]
    L1 = np.array([e['L1'] for e in v]); U1 = np.array([e['U1'] for e in v])
    L3 = np.array([e['L3'] for e in v]); U3 = np.array([e['U3'] for e in v])
    g0 = np.array([e['g0'] for e in v]); gs = np.array([e['gs'] for e in v]); A = np.array([e['A'] for e in v])
    box = np.array([e['box'] for e in v]); lr = np.array([e['lr_true'] for e in v])
    jmin = np.array([e['jmin'] for e in v]); floor = 2 * S['K1'] / 9.0 ** 2      # the eigenvalue floor of the region search
    out = dict(width1=float((U1 - L1).mean()), width1_se=float((U1 - L1).std() / np.sqrt(len(v))),
               box=float(box.mean()), lr_over3=float((lr > 2 * S['K3']).mean()), nearsing=float((jmin < floor).mean()),
               width3=float((U3 - L3).mean()), cover1=float(((L1 <= gs) & (gs <= U1)).mean()),
               cover3=float(((L3 <= gs) & (gs <= U3)).mean()), rmse=float(np.sqrt(((g0 - gs) ** 2).mean())),
               A2=float((A ** 2).mean()))
    if kind == 'mon':
        need = gs >= C_MON
        act_r = U1 >= C_MON; act_p = g0 >= C_MON
        out.update(n_need=int(need.sum()),
                   miss_robust=float((need & ~act_r).sum() / max(need.sum(), 1)), miss_plugin=float((need & ~act_p).sum() / max(need.sum(), 1)),
                   false_robust=float((~need & act_r).sum() / max((~need).sum(), 1)), false_plugin=float((~need & act_p).sum() / max((~need).sum(), 1)))
    else:
        ok = gs <= C_PLAN
        app_r = U1 <= C_PLAN; app_p = g0 <= C_PLAN
        out.update(n_ok=int(ok.sum()),
                   bad_approval_robust=float((~ok & app_r).sum() / max((~ok).sum(), 1)), bad_approval_plugin=float((~ok & app_p).sum() / max((~ok).sum(), 1)),
                   good_approval_robust=float((ok & app_r).sum() / max(ok.sum(), 1)), good_approval_plugin=float((ok & app_p).sum() / max(ok.sum(), 1)))
    al = [e['alloc'] for e in v]
    out.update(share_targets=float(np.mean([a['share_targets'] for a in al])), share_hard=float(np.mean([a['share_hard'] for a in al])),
               mean_dist=float(np.mean([a['mean_dist'] for a in al])))
    return out


res = {'mon': {r: summ('mon', r) for r in S['designs_mon']}, 'plan': {r: summ('plan', r) for r in S['designs_plan']}}
# accuracy of Theorem Q: ratio of the exact half-width to the second-order prediction
ratios = {'hard': [], 'gamma1': [], 'gamma2': []}
k1 = S['K1']
for x in B:
    for kind, designs in (('mon', S['designs_mon']), ('plan', S['designs_plan'])):
        for r in designs:
            e = x[kind + ':' + r]
            A = e['A']
            if A < 1e-6 or e['box']:                  # Theorem Q is a statement about regular (interior) fits
                continue
            ratios['hard'].append(((e['U1'] - e['L1']) / 2) / (A * np.sqrt(2 * k1)))
            ratios['gamma1'].append((e['pen']['1.0'][1] - e['g0']) / (k1 / 2 * A ** 2))
            g = 2.0
            pred = (2 * g - 1) * (A * np.sqrt(k1 / 2) / g) ** (2 * g / (2 * g - 1))
            ratios['gamma2'].append((e['pen']['2.0'][1] - e['g0']) / pred)
thq = {k: dict(median=float(np.median(v)), q10=float(np.quantile(v, 0.1)), q90=float(np.quantile(v, 0.9)), n=len(v)) for k, v in ratios.items()}
thq['n_total'] = sum(len(S['designs_mon']) + len(S['designs_plan']) for _ in B)
# rank agreement between expected A^2 and expected width across designs (Corollary)
rank = {}
for kind in ('mon', 'plan'):
    rs = list(res[kind])
    a = np.array([res[kind][r]['A2'] for r in rs]); w = np.array([res[kind][r]['width1'] for r in rs])
    ra = np.argsort(np.argsort(a)); rw = np.argsort(np.argsort(w))
    rank[kind] = float(np.corrcoef(ra, rw)[0, 1])
gs_mon = np.array([x['mon:mjegulla']['gs'] for x in B]); gs_plan = np.array([x['plan:mjegulla']['gs'] for x in B])
out = dict(results=res, theoremQ=thq, rank_corr=rank, thresholds=dict(mon=C_MON, plan=C_PLAN), R=len(B),
           share_need_mon=float((gs_mon >= C_MON).mean()), share_ok_plan=float((gs_plan <= C_PLAN).mean()),
           gs_mon_q=[float(q) for q in np.quantile(gs_mon, [0.1, 0.5, 0.9])], gs_plan_q=[float(q) for q in np.quantile(gs_plan, [0.1, 0.5, 0.9])],
           joint_check=D['A']['joint_check'], budget=C['C'], R_budget=C['R'], setup=S,
           example=dict(G_mon=D['A']['example']['G_mon'],
                        final={r: D['A']['example'][r]['track'][-1] for r in ('random', 'mjegulla')}))
json.dump(out, open('mjegulla_summary.json', 'w'), indent=1)
for kind in ('mon', 'plan'):
    print('==', kind)
    for r, v in res[kind].items():
        print('%-12s w1 %.3f w3 %.3f cov1 %.3f cov3 %.3f rmse %.3f A2 %.3f box %.2f lr>k3 %.3f tgt %.2f hard %.2f dist %.2f' % (r, v['width1'], v['width3'], v['cover1'], v['cover3'], v['rmse'], v['A2'], v['box'], v['lr_over3'], v['share_targets'], v['share_hard'], v['mean_dist']))
print('theorem Q', json.dumps(thq)); print('rank corr', rank)
print({k: v for k, v in out.items() if k in ('share_need_mon', 'share_ok_plan', 'gs_mon_q', 'gs_plan_q')})
for kind in ('mon', 'plan'):
    for r, v in res[kind].items():
        print(kind, r, {k: round(val, 3) for k, val in v.items() if 'robust' in k or 'plugin' in k})
