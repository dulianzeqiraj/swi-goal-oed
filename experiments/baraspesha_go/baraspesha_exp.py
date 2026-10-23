"""BARASPESHA-GO experiments.
  A  exactness checks of the equivalences (Theorem M, Theorem N) on one well field, and the spectral form of the
     augmented ridge estimator (penalty lambda delta / (d + lambda + delta) per eigen-direction);
  B  Monte Carlo of the estimators of psi = mean over treated wells of E[Y(0) | X] in five scenarios
     (R well fields each);
  C  goal-oriented choice of the measured control wells: five designs, three budgets, two scenarios.
Writes baraspesha.json (A, B) and baraspesha_design.json (C). `python3 baraspesha_exp.py A`, `B` or `C` runs one part.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time
import numpy as np
from multiprocessing import Pool
from scipy.linalg import solve
import baraspesha_model as M
import baraspesha_est as E
import baraspesha_design as D

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
R_B, R_C = 1000, 300
SCEN = {
    'S1': dict(label='baseline (n = 400)', n=400, alpha1=2.0, s3=False, exact=False),
    'S2': dict(label='weak overlap (n = 400)', n=400, alpha1=3.5, s3=False, exact=False),
    'S3': dict(label='structural error: base depth varies (n = 400)', n=400, alpha1=2.0, s3=True, exact=False),
    'S4': dict(label='near-correct simulator (n = 400)', n=400, alpha1=2.0, s3=False, exact=True),
    'S5': dict(label='small field (n = 150)', n=150, alpha1=2.0, s3=False, exact=False),
}
METHODS = ['naive', 'sim_nominal', 'sim_calib', 'ols', 'bal_generic', 'aug_generic', 'aug_sim', 'baraspesha', 'baraspesha_wald']


# ------------------------------------------------------------------------------------------------------------ A
def part_A():
    rng = np.random.default_rng(7)
    F = M.draw_field(400, rng, alpha1=2.0)
    T = np.where(F['A'] == 1)[0]; C = np.where(F['A'] == 0)[0]
    Z = M.standardize(M.features(F), M.features(F)); Z0, Z1 = Z[C], Z[T]
    Y0 = F['Y'][C]
    # polynomial basis of degree 2 (15 functions)
    def poly(Zx):
        cols = [np.ones(len(Zx))] + [Zx[:, i] for i in range(4)] + [Zx[:, i] * Zx[:, j] for i in range(4) for j in range(i, 4)]
        return np.column_stack(cols)
    P0, P1 = poly(Z0), poly(Z1); p1 = P1.mean(0)
    Gm = P0.T @ P0; I = np.eye(Gm.shape[0])
    lam, dl = 3.0, 0.5
    beta_l = solve(Gm + lam * I, P0.T @ Y0)
    w_d = P0 @ solve(Gm + dl * I, p1)                       # ridge balancing weights (dual form)
    aug = p1 @ beta_l + w_d @ (Y0 - P0 @ beta_l)
    Pen = lam * dl * np.linalg.inv(Gm + (lam + dl) * I)
    gen = p1 @ solve(Gm + Pen, P0.T @ Y0)
    a1 = abs(aug - gen)
    # spectral shrinkage factors
    dgrid = np.geomspace(1e-2, 1e3, 200)
    spec = dict(d=dgrid.tolist(), ridge_lambda=(dgrid / (dgrid + lam)).tolist(), ridge_delta=(dgrid / (dgrid + dl)).tolist(),
                augmented=(dgrid * (dgrid + lam + dl) / ((dgrid + lam) * (dgrid + dl))).tolist(), lam=lam, delta=dl)
    # exact balance with a complex outcome model: OLS plus the out-of-span part of the simulator
    f0 = M.f_sim(F['xw'][C], F['Q0'][C], F['kmeas'][C], np.zeros(3)); f1 = M.f_sim(F['xw'][T], F['Q0'][T], F['kmeas'][T], np.zeros(3))
    dd = 1e-9 * np.trace(Gm) / Gm.shape[0]
    w0 = P0 @ solve(Gm + dd * I, p1)
    aug0 = f1.mean() + w0 @ (Y0 - f0)
    b_ols = solve(Gm, P0.T @ Y0); g_ols = solve(Gm, P0.T @ f0)
    pred = p1 @ b_ols + (f1.mean() - p1 @ g_ols)
    a2 = abs(aug0 - pred)
    out_of_span = float(f1.mean() - p1 @ g_ols)
    # balancing the sensitivities = one Levenberg-Marquardt step
    S0 = M.sens(F['xw'][C], F['Q0'][C], F['kmeas'][C], np.zeros(3)); S1 = M.sens(F['xw'][T], F['Q0'][T], F['kmeas'][T], np.zeros(3))
    mu = 0.3
    wS = S0 @ solve(S0.T @ S0 + mu * np.eye(3), S1.mean(0))
    augS = f1.mean() + wS @ (Y0 - f0)
    step = solve(S0.T @ S0 + mu * np.eye(3), S0.T @ (Y0 - f0))
    lm = (f1 + S1 @ step).mean()
    a3 = abs(augS - lm)
    # at the least-squares optimum, exact balance of the sensitivities reproduces the calibrated simulator
    th, J0, r0 = M.calibrate(F['xw'][C], F['Q0'][C], F['kmeas'][C], Y0, rho=0.0, iters=400, tol=1e-15)
    fc1 = M.f_sim(F['xw'][T], F['Q0'][T], F['kmeas'][T], th); Sc1 = M.sens(F['xw'][T], F['Q0'][T], F['kmeas'][T], th)
    wc = J0 @ solve(J0.T @ J0 + 1e-10 * np.eye(3), Sc1.mean(0))
    a4 = abs((fc1.mean() + wc @ r0) - fc1.mean())
    orth = float(np.max(np.abs(J0.T @ r0)))
    # minimax weights in the physics kernel = simulator + kernel ridge of the residuals with a free intercept
    th2, J2, r2 = M.calibrate(F['xw'][C], F['Q0'][C], F['kmeas'][C], Y0)
    f21 = M.f_sim(F['xw'][T], F['Q0'][T], F['kmeas'][T], th2); S21 = M.sens(F['xw'][T], F['Q0'][T], F['kmeas'][T], th2)
    K00, k01, k11, _ = E.phys_parts(Z, C, T, J2, r2, S21, E.PHYS)
    dvec = np.full(len(C), 0.05)
    w = M.kr_weights(K00, k01, dvec)
    augK = f21.mean() + w @ r2
    # kernel ridge with an unpenalized intercept: [K + D, 1; 1', 0] [a; b] = [r; 0]
    n0 = len(C)
    Asys = np.block([[K00 + np.diag(dvec), np.ones((n0, 1))], [np.ones((1, n0)), np.zeros((1, 1))]])
    sol = solve(Asys, np.r_[r2, 0.0])
    a_c, b_c = sol[:n0], sol[n0]
    krr = f21.mean() + k01 @ a_c + b_c
    a5 = abs(augK - krr)
    return dict(checks=dict(ridge_ridge=a1, exact_balance=a2, lm_step=a3, calibrated=a4, minimax_krr=a5),
                out_of_span=out_of_span, orthogonality=orth, theta_ls=th.tolist(), spectrum=spec,
                n0=int(len(C)), n1=int(len(T)))


# ------------------------------------------------------------------------------------------------------------ B
def one_B(args):
    key, r = args
    sc = SCEN[key]
    rng = np.random.default_rng(100000 * (list(SCEN).index(key) + 1) + r)
    F = M.draw_field(sc['n'], rng, alpha1=sc['alpha1'], s3=sc['s3'])
    T = F['A'] == 1
    psi = float(F['m0'][T].mean()); att = float((F['m1'] - F['m0'])[T].mean())
    out = E.estimate_all(F, rng, exact=sc['exact'])
    row = dict(psi=psi, att=att, meanTY=float(F['Y'][T].mean()), n1=int(T.sum()))
    for k in METHODS:
        e, se, lo, hi = out[k]
        row[k] = (e - psi, se, float(lo <= psi <= hi) if np.isfinite(lo) else np.nan, hi - lo)
    row['maxbias'], row['se_bar'], row['ess'] = out['_bar_maxbias'][0], out['_bar_maxbias'][1], out['_bar_maxbias'][2]
    return key, row


def part_B(pool):
    jobs = [(k, r) for k in SCEN for r in range(R_B)]
    res = {k: [] for k in SCEN}
    for k, row in pool.imap_unordered(one_B, jobs, chunksize=8):
        res[k].append(row)
    summ = {}
    for k, rows in res.items():
        s = dict(label=SCEN[k]['label'], R=len(rows), psi=float(np.mean([x['psi'] for x in rows])),
                 att=float(np.mean([x['att'] for x in rows])), n1=float(np.mean([x['n1'] for x in rows])),
                 maxbias=float(np.mean([x['maxbias'] for x in rows])), se_bar=float(np.mean([x['se_bar'] for x in rows])),
                 ess=float(np.mean([x['ess'] for x in rows])))
        for m in METHODS:
            v = np.array([x[m] for x in rows], float)
            s[m] = dict(bias=float(v[:, 0].mean()), rmse=float(np.sqrt((v[:, 0] ** 2).mean())),
                        sd=float(v[:, 0].std()), cover=float(np.nanmean(v[:, 2])) if np.isfinite(v[:, 2]).any() else None,
                        length=float(np.nanmean(v[:, 3])) if np.isfinite(v[:, 3]).any() else None,
                        mcse_rmse=float(np.sqrt((v[:, 0] ** 2).mean()) / np.sqrt(2 * len(v))))
        summ[k] = s
    return summ


# ------------------------------------------------------------------------------------------------------------ C
BUDGETS = [40, 80, 120]


def one_C(args):
    key, r = args
    sc = SCEN[key]
    rng = np.random.default_rng(900000 + 1000 * (list(SCEN).index(key) + 1) + r)
    F = M.draw_field(sc['n'], rng, alpha1=sc['alpha1'], s3=sc['s3'])
    return key, D.run_designs(F, BUDGETS, rng)


def part_C(pool):
    jobs = [(k, r) for k in ('S1', 'S3') for r in range(R_C)]
    res = {'S1': [], 'S3': []}
    for k, rows in pool.imap_unordered(one_C, jobs, chunksize=2):
        res[k].append(rows)
    summ = {}
    for k, fields in res.items():
        flat = [x for rows in fields for x in rows]
        tab = []
        for m in BUDGETS:
            for d in ('random', 'space_filling', 'nearest', 'calib_D', 'goal'):
                v = [x for x in flat if x['m'] == m and x['design'] == d]
                e = np.array([x['err'] for x in v]); ea = np.array([x['err_aug'] for x in v])
                tab.append(dict(m=m, design=d, rmse=float(np.sqrt((e ** 2).mean())), bias=float(e.mean()),
                                cover=float(np.mean([x['cover'] for x in v])), length=float(np.mean([x['length'] for x in v])),
                                rmse_aug=float(np.sqrt((ea ** 2).mean())), cover_aug=float(np.mean([x['cover_aug'] for x in v])),
                                sqrtV=float(np.sqrt(np.mean([x['V'] for x in v]))),
                                transition=float(np.mean([x['frac_transition'] for x in v])), R=len(v),
                                mcse_rmse=float(np.sqrt((e ** 2).mean()) / np.sqrt(2 * len(e)))))
        # paired comparison: share of fields where the goal design has the smaller squared error than nearest
        win = {}
        for m in BUDGETS:
            g = {i: None for i in range(len(fields))}
            wins = []
            for rows in fields:
                eg = [x['err'] for x in rows if x['m'] == m and x['design'] == 'goal'][0]
                en = [x['err'] for x in rows if x['m'] == m and x['design'] == 'nearest'][0]
                wins.append(eg ** 2 < en ** 2)
            win[str(m)] = float(np.mean(wins))
        summ[k] = dict(label=SCEN[k]['label'], table=tab, goal_beats_nearest=win)
    return summ


def example_field():
    """One field and the wells chosen by the goal design and by matching at m = 40 (for the map figure)."""
    rng = np.random.default_rng(11)
    F = M.draw_field(400, rng, alpha1=2.0)
    T = np.where(F['A'] == 1)[0]; Cand = np.where(F['A'] == 0)[0]
    Z = M.standardize(M.features(F), M.features(F))
    goal = D.sequential(F, Z, Cand, T, 40, 'goal')[0]
    near = D.nearest(Z[Cand], Z[T], 40, rng)
    th, J, r = M.calibrate(F['xw'][Cand], F['Q0'][Cand], F['kmeas'][Cand], F['Y'][Cand])
    fc = M.f_sim(F['xw'], F['Q0'], F['kmeas'], th)
    return dict(xw=F['xw'].tolist(), y=F['y'].tolist(), A=F['A'].tolist(), Y=F['Y'].tolist(), m0=F['m0'].tolist(),
                fcal=fc.tolist(), goal=[int(Cand[i]) for i in goal], nearest=[int(Cand[i]) for i in near])


if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'ABC'
    t0 = time.time()
    out = json.load(open('baraspesha.json')) if os.path.exists('baraspesha.json') else {}
    if 'A' in part:
        out['A'] = part_A(); out['example'] = example_field()
        print('A', json.dumps(out['A']['checks']), 'out-of-span %.4f' % out['A']['out_of_span'], flush=True)
    with Pool(4) as pool:
        if 'B' in part:
            out['B'] = part_B(pool)
            for k, s in out['B'].items():
                print(k, s['label'], 'psi %.3f att %.3f' % (s['psi'], s['att']))
                for m in METHODS:
                    x = s[m]
                    print('   %-16s bias %+.4f rmse %.4f cover %s len %s' % (m, x['bias'], x['rmse'], x['cover'], x['length']))
        if 'A' in part or 'B' in part:
            out['truth'] = dict(q=M.Q_TRUE, q_sim=M.Q0_SIM, omega=M.OMEGA_TRUE, omega_sim=M.OMEGA0_SIM, tau_u=M.TAU_U,
                                tau_e=M.TAU_E, kbias=M.KMEAS_BIAS, sigma=M.SIGMA_EPS, cut=M.CUT, phys=E.PHYS)
            json.dump(out, open('baraspesha.json', 'w'), indent=1)
        if 'C' in part:
            dsg = part_C(pool)
            json.dump(dict(C=dsg, budgets=BUDGETS, pilot=D.PILOT, batch=D.BATCH, R=R_C), open('baraspesha_design.json', 'w'), indent=1)
            for k, s in dsg.items():
                print(k, s['label'], 'goal beats nearest', s['goal_beats_nearest'])
                for x in s['table']:
                    print('   m=%3d %-14s rmse %.4f bias %+.4f cover %.3f len %.3f | aug %.4f %.3f | sqrtV %.4f' % (
                        x['m'], x['design'], x['rmse'], x['bias'], x['cover'], x['length'], x['rmse_aug'], x['cover_aug'], x['sqrtV']))
    out_seconds = time.time() - t0
    print('done in %.0f s' % out_seconds)
