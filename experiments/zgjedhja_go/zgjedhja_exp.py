"""ZGJEDHJA-GO experiments.
  A  population identified sets of the two policy effects under combinations of information and restrictions,
     and the naive analysis that ignores the unseen salinized state;
  B  goal-oriented monitoring design: a budget is split between sentinel well-seasons at the front (cost 1 each)
     and survey answers on the cost of replacement water (cost 0.05 each); expected width of each identified set;
  C  finite-sample inference: R panels of n wells x T seasons; plug-in identified sets with physics, a survey of
     400 answers and the shape restriction, Imbens-Manski 95% intervals from a well-level bootstrap.
Writes zgjedhja.json (A, B) and zgjedhja_mc.json (C). `python3 zgjedhja_exp.py AB` or `C` runs one part.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time
import numpy as np
from multiprocessing import Pool
from scipy.stats import binom, norm
from scipy.optimize import brentq
import zgjedhja_model as Z
import zgjedhja_ident as I

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
P1_TRUE = Z.solve(Z.THETA, Z.Q_TRUE, Z.W_TRUE)[0]
G1_TRUE = Z.gamma_fee(P1_TRUE, Z.F_TRUE, Z.Q_TRUE)
G2_TRUE = Z.gamma_recharge(P1_TRUE, Z.F_TRUE, Z.Q_TRUE, Z.W_TRUE)
COST_M, COST_S = 1.0, 0.05
BUDGETS = [20, 50, 100, 200, 400]
FRACS = np.round(np.linspace(0, 1, 21), 3)
N_SURVEY_MC = 400


def part_A(T):
    rows = []
    combos = [
        ('Economic data only', I.Q_BOX, I.W_BOX, False),
        ('+ shape restriction', I.Q_BOX, I.W_BOX, True),
        ('+ shape + physics range of q', I.Q_PHYS, I.W_BOX, True),
        ('+ shape + survey (100 answers)', I.Q_BOX, I.survey_interval(Z.W_TRUE, 100), True),
        ('+ shape + physics + survey (100)', I.Q_PHYS, I.survey_interval(Z.W_TRUE, 100), True),
        ('+ shape + sentinel (200, k = 30) + survey (400)', I.clopper_pearson(30, 200), I.survey_interval(Z.W_TRUE, 400), True),
    ]
    for lab, q, w, sh in combos:
        s1, s2 = I.sets(T, q, w, sh)
        rows.append(dict(label=lab, q=list(q), w=list(w), shape=sh, fee=s1, recharge=s2))
    naive_th4 = float(T['c'][0])
    return dict(rows=rows, truth=dict(fee=G1_TRUE, recharge=G2_TRUE, theta4=float(Z.THETA[-1])),
                naive=dict(fee=0.0, recharge=0.0, theta4=naive_th4),
                g1_curve=dict(q=T['q'].tolist(), g1=T['g1'].tolist()))


def expected_widths(T, m, n_s, nodes=11):
    """Expected width of the two identified sets for m sentinel well-seasons and n_s survey answers, averaging over
    k ~ Bin(m, q) and the survey mean; physics range and shape restriction always on."""
    if m > 0:
        ks = np.arange(m + 1)
        pk = binom.pmf(ks, m, Z.Q_TRUE)
        keep = pk > 1e-6
        ks, pk = ks[keep], pk[keep] / pk[keep].sum()
    else:
        ks, pk = np.array([0]), np.array([1.0])
    if n_s > 0:
        u = (np.arange(nodes) + 0.5) / nodes
        wbars = Z.W_TRUE + SIG(n_s) * norm.ppf(u)
    else:
        wbars = np.array([Z.W_TRUE])
    w1 = w2 = cov1 = cov2 = 0.0
    for k, p in zip(ks, pk):
        if m > 0:
            cp = I.clopper_pearson(int(k), m)
            qint = (max(cp[0], I.Q_PHYS[0]), min(cp[1], I.Q_PHYS[1]))
            if qint[0] > qint[1]:
                qint = cp
        else:
            qint = I.Q_PHYS
        for wb in wbars:
            wint = I.survey_interval(wb, n_s)
            s1, s2 = I.sets(T, qint, wint, True)
            if s1 is None:
                s1, s2 = I.sets(T, qint, wint, False)
            w1 += p * (s1[1] - s1[0]) / len(wbars)
            w2 += p * (s2[1] - s2[0]) / len(wbars)
            cov1 += p * (s1[0] - 1e-12 <= G1_TRUE <= s1[1] + 1e-12) / len(wbars)
            cov2 += p * (s2[0] - 1e-12 <= G2_TRUE <= s2[1] + 1e-12) / len(wbars)
    return w1, w2, cov1, cov2


SIG = lambda n_s: I.SIGMA_W / np.sqrt(n_s)


def part_B(T):
    out = []
    for Bud in BUDGETS:
        row = dict(budget=Bud, fracs=FRACS.tolist(), w_fee=[], w_recharge=[], cov_fee=[], cov_recharge=[])
        for f in FRACS:
            m = int(round(f * Bud / COST_M))
            n_s = int(round((1 - f) * Bud / COST_S))
            w1, w2, c1, c2 = expected_widths(T, m, n_s)
            row['w_fee'].append(w1); row['w_recharge'].append(w2); row['cov_fee'].append(c1); row['cov_recharge'].append(c2)
        row['best_fee'] = float(FRACS[int(np.argmin(row['w_fee']))])
        row['best_recharge'] = float(FRACS[int(np.argmin(row['w_recharge']))])
        out.append(row)
        print(f'budget {Bud}: best share on sentinels — fee {row["best_fee"]:.2f}, recharge {row["best_recharge"]:.2f}', flush=True)
    return out


# ------------------------------------------------------------------ part C: finite-sample inference
QG = np.round(np.arange(I.Q_PHYS[0], I.Q_PHYS[1] + 1e-9, 0.01), 4)
NB, N_WELLS, T_SEAS, R = 100, 300, 12, 500


def est_sets(panel, wint):
    P1, F = Z.estimate(panel)
    wg = np.linspace(wint[0], wint[1], 11)
    T = I.tables(P1, F, QG, wg)
    return I.sets(T, I.Q_PHYS, wint, True)


def im_interval(lo, hi, slo, shi, alpha=0.05):
    """Imbens-Manski (2004) interval for a partially identified parameter."""
    s = max(slo, shi, 1e-12)
    d = max(hi - lo, 0.0)
    c = brentq(lambda c: norm.cdf(c + d / s) - norm.cdf(-c) - (1 - alpha), 0.0, 10.0)
    return lo - c * slo, hi + c * shi


def one_rep(rep):
    rng = np.random.default_rng([2039, rep])
    panel = Z.simulate_panel(N_WELLS, T_SEAS, rng)
    wbar = Z.W_TRUE + SIG(N_SURVEY_MC) * rng.standard_normal()
    wint = I.survey_interval(wbar, N_SURVEY_MC)
    s1, s2 = est_sets(panel, wint)
    if s1 is None:
        return None
    nw = panel.reshape(T_SEAS, N_WELLS, 3)
    boots = []
    for b in range(NB):
        idx = rng.integers(0, N_WELLS, N_WELLS)
        pb = nw[:, idx].reshape(-1, 3)
        b1, b2 = est_sets(pb, wint)
        if b1 is not None:
            boots.append([*b1, *b2])
    boots = np.array(boots)
    sd = boots.std(0)
    ci1 = im_interval(s1[0], s1[1], sd[0], sd[1])
    ci2 = im_interval(s2[0], s2[1], sd[2], sd[3])
    P1, F = Z.estimate(panel)
    naive_th4 = float(Z.index_c(P1, F, 0.0))
    return [*s1, *s2, *ci1, *ci2, naive_th4, len(boots)]


def part_C():
    t0 = time.time()
    with Pool(4) as pool:
        rows = [r for r in pool.map(one_rep, range(R), chunksize=4) if r is not None]
    A = np.array(rows)
    res = dict(R=R, n_ok=len(A), n_wells=N_WELLS, seasons=T_SEAS, n_boot=NB, n_survey=N_SURVEY_MC,
               truth=dict(fee=G1_TRUE, recharge=G2_TRUE),
               fee=dict(set_lo_mean=float(A[:, 0].mean()), set_hi_mean=float(A[:, 1].mean()),
                        ci_lo_mean=float(A[:, 4].mean()), ci_hi_mean=float(A[:, 5].mean()),
                        cover=float(np.mean((A[:, 4] <= G1_TRUE) & (G1_TRUE <= A[:, 5]))),
                        set_contains=float(np.mean((A[:, 0] <= G1_TRUE) & (G1_TRUE <= A[:, 1]))),
                        excludes_zero=float(np.mean(A[:, 4] > 0))),
               recharge=dict(set_lo_mean=float(A[:, 2].mean()), set_hi_mean=float(A[:, 3].mean()),
                             ci_lo_mean=float(A[:, 6].mean()), ci_hi_mean=float(A[:, 7].mean()),
                             cover=float(np.mean((A[:, 6] <= G2_TRUE) & (G2_TRUE <= A[:, 7]))),
                             set_contains=float(np.mean((A[:, 2] <= G2_TRUE) & (G2_TRUE <= A[:, 3]))),
                             excludes_zero=float(np.mean(A[:, 6] > 0))),
               naive_theta4=dict(mean=float(A[:, 8].mean()), sd=float(A[:, 8].std())),
               seconds=time.time() - t0)
    json.dump(res, open('zgjedhja_mc.json', 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'ABC'
    if 'A' in which or 'B' in which:
        T = I.tables(P1_TRUE, Z.F_TRUE)
        out = dict(truth=dict(q=Z.Q_TRUE, w=Z.W_TRUE, theta=Z.THETA.tolist(), beta=Z.BETA, tau=Z.TAU, H=Z.H, s0=Z.S0,
                              ccp=P1_TRUE.tolist(), fee=G1_TRUE, recharge=G2_TRUE),
                   A=part_A(T), B=part_B(T), costs=dict(sentinel=COST_M, survey=COST_S), q_phys=list(I.Q_PHYS),
                   theta_min=I.THETA_MIN, sigma_w=I.SIGMA_W)
        json.dump(out, open('zgjedhja.json', 'w'), indent=1)
        for r in out['A']['rows']:
            print(r['label'], np.round(r['fee'], 4), np.round(r['recharge'], 3))
    if 'C' in which:
        part_C()
