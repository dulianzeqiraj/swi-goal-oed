"""Summary of the VENDI-GO run for review 53: per-policy means with 95% intervals, paired differences of the cost
J = risk + kappa * tests against VENDI-GO, calibration of the posterior risk, the value of Stage 0, the number of
tests, and the checks of Proposition V1. Writes res/vendi_summary.json.
Run: python3 vendi_summary.py res/runs_0_200.json
"""
import os, sys, json
import numpy as np
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vendi as V


def main(path):
    D = json.load(open(path)); rows = D['rows']; kappa = D['constants']['KAPPA']
    by = {}
    for r in rows:
        by.setdefault(r['policy'], {})[r['truth']] = r
    T = sorted(by['vendi']); n = len(T)
    arr = lambda p, f: np.array([by[p][t][f] for t in T], float)
    out = {'n_truths': n, 'kappa': kappa, 'constants': D['constants'], 'policies': {}}
    Jv = arr('vendi', 'risk') + kappa * arr('vendi', 'tests'); Rv = arr('vendi', 'risk')
    for p in by:
        r, k = arr(p, 'risk'), arr(p, 'tests'); J = r + kappa * k
        d, dr = J - Jv, r - Rv
        e = dict(risk=r.mean(), risk_ci=1.96 * r.std(ddof=1) / np.sqrt(n), tests=k.mean(), tests_min=int(k.min()), tests_max=int(k.max()),
                 J=J.mean(), dJ=d.mean(), dJ_ci=1.96 * d.std(ddof=1) / np.sqrt(n), drisk=dr.mean(), drisk_ci=1.96 * dr.std(ddof=1) / np.sqrt(n),
                 frac_better_than_vendi=float(np.mean(d < -1e-9)), frac_worse_than_vendi=float(np.mean(d > 1e-9)))
        if 'post_risk' in by[p][T[0]]:
            pr = arr(p, 'post_risk'); e['post_risk'] = pr.mean()
            # reliability in three bins of the posterior risk
            bins = [0, 0.05, 0.3, 1.0001]; rel = []
            for lo, hi in zip(bins[:-1], bins[1:]):
                s = (pr >= lo) & (pr < hi)
                if s.sum():
                    rel.append(dict(lo=lo, hi=hi, n=int(s.sum()), post=float(pr[s].mean()), real=float(r[s].mean())))
            e['reliability'] = rel
        out['policies'][p] = {k_: (float(v) if isinstance(v, (np.floating, float)) else v) for k_, v in e.items()}
    # oracle match
    orc = {t: set(by['oracle'][t]['sites']) for t in T}
    for p in ('vendi', 'vendi_noS0', 'confirm', 'thompson', 'prag_s0', 'prag_prior'):
        same = np.mean([set(by[p][t]['sites']) == orc[t] for t in T])
        close = np.mean([by[p][t]['risk'] - by['oracle'][t]['risk'] <= 0.005 for t in T])
        out['policies'][p]['oracle_same'] = float(same); out['policies'][p]['oracle_within_0005'] = float(close)
    # gap closed: (prag_prior - vendi) / (prag_prior - oracle)
    g = lambda p: out['policies'][p]['risk']
    out['gap_closed_vs_prag_prior'] = (g('prag_prior') - g('vendi')) / (g('prag_prior') - g('oracle'))
    out['gap_closed_vs_prag_s0'] = (g('prag_s0') - g('vendi')) / (g('prag_s0') - g('oracle'))
    out['frac_prag_cells_below_oracle'] = float(np.mean(arr('prag_cells', 'risk') < arr('oracle', 'risk') - 1e-9))
    # tests and reasons
    why = [w for t in T for w in by['vendi'][t].get('why', [])]
    out['vendi_why'] = {'kg': why.count('kg'), 'confirm': why.count('confirm')}
    k = arr('vendi', 'tests')
    out['vendi_tests_hist'] = {int(v): int((k == v).sum()) for v in np.unique(k)}
    out['vendi_s0_obs'] = float(np.mean([by['vendi'][t].get('s0_obs', 0) for t in T]))
    # hard and easy truths
    none = arr('none', 'risk')
    out['strata'] = {}
    for nm, s in (('none_below_0.5', none < 0.5), ('none_above_0.5', none >= 0.5)):
        out['strata'][nm] = dict(n=int(s.sum()), **{p: float(arr(p, 'risk')[s].mean()) for p in ('prag_prior', 'prag_s0', 'confirm', 'vendi', 'oracle')})
    # Proposition V1 checks
    V.load_setup(); V.zeta_chol()
    rng = np.random.default_rng(5)
    th = V.LG @ rng.standard_normal(V.NZ); ze = V.draw_zeta(rng)
    A = V.matrix(th, ze); lu = spla.splu(A)
    u = lu.solve(V.EAB); gT = lu.solve(V.EAB, trans='T')
    out['reciprocity'] = dict(max_abs_u_minus_g=float(np.abs(u - gT).max()), max_g=float(gT.max()),
                              max_asym=float(abs(A - A.T).max()))
    S = V._S
    sdY = np.sqrt(np.diag(S['C']))
    out['approx_error'] = dict(sd_log_g_sites_median=float(np.median(np.r_[sdY[:V.K], sdY[V.NJ:V.NJ + V.K]])),
                               sd_log_hn=[float(sdY[V.PHA]), float(sdY[V.PHB])], bias_log_g_median=float(np.median(S['mu'][:V.K])))
    a, b = V.heads_sup(S['S1'], V.QA, V.QB, S['xi'])
    out['pumping'] = dict(QA=V.QA, QB=V.QB, pA=float(np.mean(a < V.HC)), pB=float(np.mean(b < V.HC)), pAB=float(np.mean(np.minimum(a, b) < V.HC)))
    out['geometry'] = dict(K=int(V.K), NO=int(V.NO), DZ=int(V.DZ), n_triples=int(len(V.triples())))
    json.dump(out, open(os.path.join(HERE, 'res', 'vendi_summary.json'), 'w'), indent=1)
    for p, e in out['policies'].items():
        print(f"{p:16s} risk {e['risk']:.4f}±{e['risk_ci']:.4f} tests {e['tests']:5.2f} J {e['J']:.4f} dJ {e['dJ']:+.4f}±{e['dJ_ci']:.4f}"
              + (f" post {e['post_risk']:.4f}" if 'post_risk' in e else '') + (f" oracle-same {e['oracle_same']:.2f} within {e['oracle_within_0005']:.2f}" if 'oracle_same' in e else ''))
    print(json.dumps({k_: out[k_] for k_ in ('gap_closed_vs_prag_prior', 'gap_closed_vs_prag_s0', 'vendi_why', 'vendi_tests_hist', 'strata', 'reciprocity', 'approx_error', 'pumping')}, indent=1))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'res', 'runs_0_200.json'))
