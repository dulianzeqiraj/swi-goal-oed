"""KURSIM-GO exactness checks (Theorem A and Proposition B of the review), on one million simulated wells per run.

  * causal margin: mean and sd of Y under do(a1, a2) for the four regimes, against theta0 + theta1 a1 + theta2 a2 and s,
    for the baseline and the strong-feedback past and for the Student-t copula;
  * observational regression: Y - E[Y | L1, A1, L2, A2] (Proposition B) regressed on (1, A1, A2, L1, L2) has
    coefficients that are zero up to Monte Carlo error;
  * the confounding seen in the data: observational cell means E[Y | A1 = a1, A2 = a2] minus the causal means;
  * a few rates of the baseline past: P(L2 = 1), P(A2 = 1), P(L2 = 1, A2 = 1).
Writes kursim_check.json.
"""
import json, os
import numpy as np
import kursim_model as K

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
N = 1_000_000
REG = [(0, 0), (1, 0), (0, 1), (1, 1)]
STRONG_PAST = dict(K.PAST, g1=2.0, g2=2.5, b3=-3.0)
STRONG_COP = dict(rho1=0.2, rho2=0.8)


def margins(past, cop, copula, seed):
    rng = np.random.default_rng(seed); out = []
    for a in REG:
        D = K.simulate(N, rng, past=past, cop=cop, copula=copula, regime=a)
        mu = K.CAUSAL['theta0'] + K.CAUSAL['theta1'] * a[0] + K.CAUSAL['theta2'] * a[1]
        out.append(dict(regime=list(a), mean=float(D['Y'].mean()), sd=float(D['Y'].std()), truth=mu,
                        se=float(D['Y'].std() / np.sqrt(N))))
    return out


def main():
    res = dict(N=N)
    res['margin_base'] = margins(K.PAST, K.COPULA, 'gauss', 1)
    res['margin_strong'] = margins(STRONG_PAST, STRONG_COP, 'gauss', 2)
    res['margin_t'] = margins(K.PAST, K.COPULA, 't', 3)
    rng = np.random.default_rng(4)
    D = K.simulate(N, rng)
    resid = D['Y'] - K.cond_mean(D['L1'], D['A1'], D['L2'], D['A2'])
    X = np.column_stack([np.ones(N), D['A1'], D['A2'], D['L1'], D['L2']])
    b = np.linalg.lstsq(X, resid, rcond=None)[0]
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ X)) * resid.var())
    res['propB'] = dict(coef=b.tolist(), se=se.tolist(), max_abs_t=float(np.max(np.abs(b / se))),
                        resid_sd=float(resid.std()))
    cells = []
    for a in REG:
        m = (D['A1'] == a[0]) & (D['A2'] == a[1])
        mu = K.CAUSAL['theta0'] + K.CAUSAL['theta1'] * a[0] + K.CAUSAL['theta2'] * a[1]
        cells.append(dict(regime=list(a), obs=float(D['Y'][m].mean()), causal=mu, diff=float(D['Y'][m].mean() - mu),
                          share=float(m.mean())))
    res['cells'] = cells
    res['rates'] = dict(alarm=float(D['L2'].mean()), high2=float(D['A2'].mean()), high1=float(D['A1'].mean()),
                        risk=float((D['L2'] * D['A2']).mean()),
                        high2_given_alarm=float(D['A2'][D['L2'] == 1].mean()),
                        high2_given_no_alarm=float(D['A2'][D['L2'] == 0].mean()))
    json.dump(res, open('kursim_check.json', 'w'), indent=1)
    worst = max(abs(r['mean'] - r['truth']) / r['se'] for k in ('margin_base', 'margin_strong', 'margin_t') for r in res[k])
    print(f'worst |mean - truth| / se over 12 regimes: {worst:.2f}')
    print('sd under intervention:', [round(r['sd'], 4) for k in ('margin_base', 'margin_strong', 'margin_t') for r in res[k]])
    print(f"Proposition B residual coefficients max |t| = {res['propB']['max_abs_t']:.2f}")
    print('cells:', [(c['regime'], round(c['diff'], 3)) for c in cells]); print('rates:', res['rates'])


if __name__ == '__main__':
    main()
