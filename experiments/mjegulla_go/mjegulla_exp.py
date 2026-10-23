"""MJEGULLA-GO experiments.
  A  exactness of the per-well decomposition (a 27-state joint chain against three filters) and one example field
     followed season by season (point filter, robust interval, oracle);
  B  Monte Carlo over R fields (true parameters drawn per field): eight monitoring designs for the goal on the
     municipal wells and seven for the planned well sites; robust intervals with the goal-specific penalty
     (k = chi2_1(0.95)/2) and the simultaneous one (k = chi2_3(0.95)/2), finite penalties gamma = 1, 2, and the
     second-order prediction of Theorem Q;
  C  budget: 2, 4 and 8 measurements per season for four designs (planned sites).
Writes mjegulla.json and mjegulla_budget.json. `python3 mjegulla_exp.py A`, `B` or `C` runs one part.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time
import numpy as np
from multiprocessing import Pool
import mjegulla_model as Mo
import mjegulla_design as D

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
T, H, B, N = 20, 4, 4, 40
R_B, R_C = 300, 150
KS = [Mo.K1, Mo.K_REGION]
GAMMAS = [1.0, 2.0]
C_DESIGNS = ('random', 'D_opt', 'goal', 'mjegulla')


def rounded(x, sig=6):
    """Floats to six significant digits for the stored results."""
    if isinstance(x, float):
        return float(f'{x:.{sig}g}')
    if isinstance(x, dict):
        return {k: rounded(v, sig) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rounded(v, sig) for v in x]
    return x


def final_eval(F, Mask, Y, kind, th_true):
    th, ll, J = Mo.mle(F, Mask, Y, T)
    L1, U1, g0 = Mo.robust_interval(F, Mask, Y, T, T, H, th, ll, J, k=Mo.K1, kind=kind)
    L3, U3, _ = Mo.robust_interval(F, Mask, Y, T, T, H, th, ll, J, k=Mo.K_REGION, kind=kind)
    gs = float(Mo.goal(th_true, F, Mask, Y, T, T, H, kind)[0][0])
    h = 1e-3
    gv, _ = Mo.goal(Mo.stencil(th, h), F, Mask, Y, T, T, H, kind)
    a, _ = Mo.grad_hess(gv, h)
    A = float(np.sqrt(max(a @ np.linalg.solve(J + 1e-9 * np.eye(3), a), 0)))
    pen = Mo.penalized_sup(F, Mask, Y, T, T, H, th, ll, J, [Mo.K1], GAMMAS, kind=kind)
    box = bool(np.any(np.isclose(th, Mo.LO, atol=0.05) | np.isclose(th, Mo.HI, atol=0.05)))
    lr_true = float(2 * (ll - Mo.filt(th_true, F, Mask, Y, T)[0][0]))
    return dict(L1=L1, U1=U1, L3=L3, U3=U3, g0=float(g0), gs=gs, A=A,
                pen={str(gm): pen[(Mo.K1, gm)] for gm in GAMMAS}, th=th.tolist(), box=box, lr_true=lr_true,
                jmin=float(np.linalg.eigvalsh(0.5 * (J + J.T))[0]))


def alloc(F, Mask):
    m = Mask[1:]
    cnt = m.sum(0)
    dist = np.repeat(F['d'], cnt)
    return dict(share_targets=float(cnt[F['tgt']].sum() / cnt.sum()), share_hard=float(cnt[F['u'] == 1].sum() / cnt.sum()),
                mean_dist=float(dist.mean()), counts=cnt.tolist(), d=F['d'].tolist(), u=F['u'].tolist(), tgt=F['tgt'].tolist())


def one_B(r):
    rng = np.random.default_rng(31000 + r)
    th_true = Mo.theta_draw(rng)
    F = Mo.field(N, rng)
    X, Yall = Mo.simulate(F, T, H, rng, theta=th_true)
    out = dict(th_true=th_true.tolist(), G_mon=int((X[T + H - 1, F['tgt']] == 2).sum()))
    for kind, designs in (('mon', D.DESIGNS), ('plan', D.DESIGNS_PLAN)):
        for rule in designs:
            Mask, Y = D.run_design(rule, F, Yall, T, H, B, np.random.default_rng(500 + r), kind=kind)
            e = final_eval(F, Mask, Y, kind, th_true)
            e['alloc'] = alloc(F, Mask)
            out[kind + ':' + rule] = e
    return out


def one_C(args):
    r, b = args
    rng = np.random.default_rng(61000 + r)
    th_true = Mo.theta_draw(rng)
    F = Mo.field(N, rng)
    X, Yall = Mo.simulate(F, T, H, rng, theta=th_true)
    out = {}
    for rule in C_DESIGNS:
        Mask, Y = D.run_design(rule, F, Yall, T, H, b, np.random.default_rng(800 + r), kind='plan')
        th, ll, J = Mo.mle(F, Mask, Y, T)
        L1, U1, g0 = Mo.robust_interval(F, Mask, Y, T, T, H, th, ll, J, k=Mo.K1, kind='plan')
        gs = float(Mo.goal(th_true, F, Mask, Y, T, T, H, 'plan')[0][0])
        out[rule] = (L1, U1, float(g0), gs)
    return b, out


def part_A():
    checks = [Mo.joint_check(np.random.default_rng(s), T=10) for s in range(20)]
    jc = dict(loglik=float(max(c[0] for c in checks)), goal=float(max(c[1] for c in checks)))
    # one example field followed season by season under two designs
    rng = np.random.default_rng(4242)
    th_true = Mo.THETA_TRUE.copy()
    F = Mo.field(N, rng)
    X, Yall = Mo.simulate(F, T, H, rng, theta=th_true)
    ex = dict(d=F['d'].tolist(), u=F['u'].tolist(), tgt=F['tgt'].tolist(), G_mon=int((X[T + H - 1, F['tgt']] == 2).sum()))
    for rule in ('random', 'mjegulla'):
        Mask, Y = D.run_design(rule, F, Yall, T, H, B, np.random.default_rng(7), kind='mon')
        track = []
        for t in range(2, T + 1):
            th, ll, J = Mo.mle(F, Mask, Y, t)
            L1, U1, g0 = Mo.robust_interval(F, Mask, Y, t, T, H, th, ll, J, k=Mo.K1, kind='mon')
            gs = float(Mo.goal(th_true, F, Mask, Y, t, T, H, 'mon')[0][0])
            track.append([t, float(L1), float(U1), float(g0), gs])
        ex[rule] = dict(track=track, counts=Mask[1:].sum(0).tolist())
    return dict(joint_check=jc, example=ex)


if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'ABC'
    t0 = time.time()
    out = json.load(open('mjegulla.json')) if os.path.exists('mjegulla.json') else {}
    out['setup'] = dict(T=T, H=H, B=B, N=N, K1=Mo.K1, K3=Mo.K_REGION, gammas=GAMMAS, theta_example=Mo.THETA_TRUE.tolist(),
                        sites_d=Mo.SITES_D.tolist(), H_plan=Mo.H_PLAN, kappa=Mo.KAPPA, eta=Mo.ETA, M=Mo.M.tolist(), sigma=Mo.SIGMA,
                        designs_mon=D.DESIGNS, designs_plan=D.DESIGNS_PLAN)
    if 'A' in part:
        out['A'] = part_A()
        print('A', out['A']['joint_check'], flush=True)
    with Pool(4) as pool:
        if 'B' in part:
            res = pool.map(one_B, range(R_B), chunksize=2)
            out['B'] = res
            for kind, designs in (('mon', D.DESIGNS), ('plan', D.DESIGNS_PLAN)):
                print('==', kind)
                for rule in designs:
                    v = [x[kind + ':' + rule] for x in res]
                    w1 = np.mean([e['U1'] - e['L1'] for e in v]); w3 = np.mean([e['U3'] - e['L3'] for e in v])
                    c1 = np.mean([e['L1'] <= e['gs'] <= e['U1'] for e in v]); c3 = np.mean([e['L3'] <= e['gs'] <= e['U3'] for e in v])
                    rm = np.sqrt(np.mean([(e['g0'] - e['gs']) ** 2 for e in v]))
                    print('%-12s width k1 %.3f k3 %.3f | cover %.3f %.3f | rmse %.3f' % (rule, w1, w3, c1, c3, rm), flush=True)
        if 'A' in part or 'B' in part:
            json.dump(rounded(out), open('mjegulla.json', 'w'))
        if 'C' in part:
            jobs = [(r, b) for b in (2, 4, 8) for r in range(R_C)]
            resC = pool.map(one_C, jobs, chunksize=2)
            summ = {}
            for b in (2, 4, 8):
                rows = [o for bb, o in resC if bb == b]
                summ[str(b)] = {rule: dict(width=float(np.mean([x[rule][1] - x[rule][0] for x in rows])),
                                           cover=float(np.mean([x[rule][0] <= x[rule][3] <= x[rule][1] for x in rows])),
                                           rmse=float(np.sqrt(np.mean([(x[rule][2] - x[rule][3]) ** 2 for x in rows]))))
                                for rule in C_DESIGNS}
                print('budget', b, {k: round(v['width'], 3) for k, v in summ[str(b)].items()}, flush=True)
            json.dump(rounded(dict(C=summ, R=R_C)), open('mjegulla_budget.json', 'w'), indent=1)
    print('done in %.0f s' % (time.time() - t0))
