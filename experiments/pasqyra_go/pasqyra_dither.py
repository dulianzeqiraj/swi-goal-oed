"""PASQYRA-GO, part B: the mirror test. How large a recorded dither, for how many years, reveals a deluded world model?

Protocol. A world model has been trained on long historical logs without any dither (here its population limit: the
black-box ARX model with 32 lags of head, chloride and pumping, or the 4-parameter physical model calibrated by likelihood
with pumping as forcing). The utility then runs a test period of N months in which a recorded random variation d_t of
standard deviation sd_d is added to the operators' pumping, and compares the model's one-step predictions with what happens.
If the model is causal its one-step errors eps_{t+1} are innovations of the aquifer, independent of d_t, d_{t-1}, ...
Two tests at the 5% level:
  targeted: the lag-0 moment of the chloride error, z = sqrt(N) mean(eps_Cl,t+1 d_t) / (sd(eps_Cl) sd(d)), |z| > 1.96;
            its mean, divided by sd_d^2, is the error of the model's one-step effect of pumping on chloride;
  omnibus:  J = N sum_{j<12} m_j^T (s_d^2 S_eps)^{-1} m_j against chi-square with 24 degrees of freedom.
Size: operators without private information (the model is then causal); power: operators with private information.
The extra cost of the dither to the operators is exact. Writes pasqyra_dither.json and pasqyra_dither.log.
"""
import json
import os
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from multiprocessing import Pool
from scipy.optimize import minimize
from scipy.stats import chi2

import pasqyra as p
import pasqyra_neural as pn

HERE = os.path.dirname(os.path.abspath(__file__))
NS = [60, 120, 240, 360]
SDS = [0.02, 0.05, 0.1, 0.2]
SETTINGS = [('near-optimal, private', 1.0, True), ('near-optimal, no private', 1.0, False), ('timid, private', 0.4, True),
            ('timid, no private', 0.4, False)]
REPS, K, P_ARX = 500, 12, 32
JSTAR = pn.JSTAR
CRIT = float(chi2.ppf(0.95, 2 * K))


def models(si):
    """Population limits of the two world models trained on long logs without dither."""
    name, gamma, private = SETTINGS[si]
    L = p.Logged(p.BASE['sd_s'] if private else np.inf, p.BASE['sd_e'], 0.0, gamma)
    coef, _ = p.regress(L, ('y', 0), [('y', k) for k in range(1, P_ARX + 1)] + [('q', k) for k in range(1, P_ARX + 1)])
    th, _ = p.calibrate_ml(L, 'phys4')
    return coef, th


def tests(E, D):
    n = len(E)
    sd2 = np.mean(D ** 2); S = np.cov(E.T)
    m0 = np.mean(E * D[:, None], axis=0)
    z = np.sqrt(n) * m0[1] / np.sqrt(S[1, 1] * sd2)
    Si = np.linalg.inv(S * sd2); J = 0.0
    for j in range(K):
        m = np.mean(E[j:] * D[:n - j, None], axis=0)
        J += (n - j) * m @ Si @ m
    return float(z), float(J), (m0 / sd2).tolist()


def job(args):
    si, N, sd_d, rep, coef, th = args
    name, gamma, private = SETTINGS[si]
    rng = np.random.default_rng(800000 + 100000 * si + 1000 * NS.index(N) + 100 * SDS.index(sd_d) + rep)
    L = p.Logged(p.BASE['sd_s'] if private else np.inf, p.BASE['sd_e'], sd_d, gamma)
    pre = P_ARX + 40
    Y, Q, D = pn.simulate_logs(L, N + pre, rng)
    # ARX world model: prediction of y_t from y_{t-1..t-P}, q_{t-1..t-P}; error at t aligned with d_{t-1}
    E = []
    for t in range(pre, N + pre):
        x = np.concatenate([Y[t - P_ARX:t][::-1].ravel(), Q[t - P_ARX:t][::-1]])
        E.append(Y[t] - coef @ x)
    E = np.array(E); Dl = D[pre - 1:N + pre - 1]
    za, Ja, ma = tests(E, Dl)
    # physical model: Kalman predictor with pumping as forcing, run from the start of the record
    A, B, Kp, _ = p.predictor_matrices(th)
    F = A - Kp @ p.C; x = np.zeros(4); Ep = []
    for t in range(N + pre):
        if t >= pre:
            Ep.append(Y[t] - p.C @ x)
        x = F @ x + B[:, 0] * Q[t] + Kp @ Y[t]
    zp, Jp, mp = tests(np.array(Ep), Dl)
    return dict(si=si, N=N, sd_d=sd_d, rep=rep, z_arx=za, J_arx=Ja, m0_arx=ma, z_phys=zp, J_phys=Jp, m0_phys=mp)


def run():
    t0 = time.time()
    pn.P['burn_log'] = 600
    M = {si: models(si) for si in range(len(SETTINGS))}
    jobs = [(si, N, s, r, M[si][0], M[si][1]) for si in range(len(SETTINGS)) for N in NS for s in SDS for r in range(REPS)]
    with Pool(4) as pool:
        res = pool.map(job, jobs, chunksize=20)
    log, table = [], {}
    for si, (name, gamma, private) in enumerate(SETTINGS):
        L0 = p.Logged(p.BASE['sd_s'] if private else np.inf, p.BASE['sd_e'], 0.0, gamma)
        dJ = {s: (p.Logged(p.BASE['sd_s'] if private else np.inf, p.BASE['sd_e'], s, gamma).J - L0.J) / JSTAR for s in SDS}
        bq = float(M[si][0][1, NY * P_ARX])
        log.append(f'== operators {name}: the ARX world model\'s one-step effect of pumping on chloride {bq:+.3f} (true 0); physical model '
                   f'head->toe {M[si][1][1]:.3f} (true 0.5); extra cost of the dither to the operators (% of J*): ' +
                   ', '.join(f'sd {s}: {100 * dJ[s]:.2f}' for s in SDS))
        table[str(si)] = dict(name=name, beta_cl_arx=bq, theta_phys=M[si][1].tolist(), dJ=dJ, cells={})
        for N in NS:
            parts = []
            for s in SDS:
                rows = [r for r in res if r['si'] == si and r['N'] == N and r['sd_d'] == s]
                c = dict(targeted_arx=float(np.mean([abs(r['z_arx']) > 1.96 for r in rows])),
                         omnibus_arx=float(np.mean([r['J_arx'] > CRIT for r in rows])),
                         targeted_phys=float(np.mean([abs(r['z_phys']) > 1.96 for r in rows])),
                         omnibus_phys=float(np.mean([r['J_phys'] > CRIT for r in rows])),
                         m0_cl_arx=float(np.mean([r['m0_arx'][1] for r in rows])), m0_cl_phys=float(np.mean([r['m0_phys'][1] for r in rows])))
                table[str(si)]['cells'][f'{N}_{s}'] = c
                parts.append(f'sd {s}: ARX {100 * c["targeted_arx"]:.0f}/{100 * c["omnibus_arx"]:.0f}%, physical {100 * c["targeted_phys"]:.0f}/{100 * c["omnibus_phys"]:.0f}%')
            log.append(f'  {N:3d} months, rejection rate (targeted/omnibus): ' + '; '.join(parts))
    log.append(f'{REPS} test periods per cell; chi-square critical value {CRIT:.2f} ({2 * K} degrees of freedom); {time.time() - t0:.0f} s')
    json.dump(p.clean(dict(NS=NS, SDS=SDS, settings=[s[0] for s in SETTINGS], K=K, p_arx=P_ARX, reps=REPS, crit=CRIT, table=table)),
              open(os.path.join(HERE, 'pasqyra_dither.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'pasqyra_dither.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


NY = 2

if __name__ == '__main__':
    run()
