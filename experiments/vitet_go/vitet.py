"""VITET-GO (vitet: the years). Innovation of review 52 (the landmark papers of deep reinforcement learning theory).

How many years of logs does ANY learner, deep or not, need before its pumping rule is within a given excess cost of the
optimum, and how should a recorded dither be designed to shorten that? The landmark sample-complexity bounds of offline
RL are worst-case and grow with the cube of the effective horizon; for an aquifer whose clays remember for decades they
are uninformative. VITET-GO computes the local minimax answer for the aquifer of reviews 48-51.

Aquifer and operators as in PASQYRA-GO (review 51), here WITHOUT private information (the mirror removed, e.g. by
logging what the operators see), so that the logs are causal and only statistics remains. The physical model has p
uncertain parameters theta (4 or 8). With N months of logs:
  * Fisher information per month I(theta*) = Hessian of the asymptotic negative log-likelihood (pumping as forcing);
  * cost Hessian H = Hessian of J(pi_theta) on the true aquifer, pi_theta the optimal records-only rule of model theta;
Proposition V (section 9 of the review): for any learner whose rule is a regular function of the logs,
    liminf_N N sup_{|theta - theta*| < c / sqrt(N)} E[J(pi_hat) - J*] >= (1/2) tr(H I^{-1})     (Hajek-Le Cam),
attained by likelihood calibration + plug-in; so the months needed for relative excess eps are
    N_eps = tr(H I^{-1}) / (2 eps J*).
Goal-oriented design: a recorded AR(1) dither d_t = phi d_{t-1} + sd sqrt(1 - phi^2) eta_t adds information at a cost
dJ_op(sd, phi) per month; at a fixed dither cost the goal-oriented criterion tr(H I^{-1}) and the D-optimal criterion
log det I can choose different dithers (for this aquifer both choose the slowest, phi = 0.98). Part A (this file) is exact; part B (vitet_mc.py) checks the formula by Monte Carlo.
Writes vitet_results.json and vitet.log.
"""
import json
import os
import sys

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from scipy.linalg import solve_discrete_lyapunov
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pasqyra_go'))
import pasqyra as p  # noqa: E402

NX = 4


class LoggedAR(p.Logged):
    """Logged world of PASQYRA-GO with an AR(1) recorded dither: an extra state d_{t-1};
    d_t = phi d_{t-1} + sd sqrt(1 - phi^2) eta_t enters the pumping."""

    def __init__(self, sd_s, sd_e, sd_d=0.0, gamma=1.0, phi=0.0):
        super().__init__(sd_s, sd_e, sd_d, gamma)
        if sd_d == 0.0 or phi == 0.0:
            self.phi = 0.0
            return
        self.phi = phi
        n = self.Phi.shape[0]
        nn = self.nn
        s = np.sqrt(1 - phi ** 2)                       # the white part of the dither: eta_t with sd sd_d sqrt(1 - phi^2)
        N = self.N.copy(); N[8, 8] = (sd_d * s) ** 2
        Phi = np.zeros((n + 1, n + 1)); Gam = np.zeros((n + 1, nn))
        # d_t = phi * dstate + eta_t ; in the base system the dither was eta_t alone (Jd picks it)
        Hd_extra = np.zeros((1, n + 1)); Hd_extra[0, n] = phi
        def ext(H):
            return np.hstack([H, np.zeros((H.shape[0], 1))])
        # every place where d_t entered through Jd now also gets phi * dstate: q and the operators' prior update
        Bq = self.Hq.copy()
        self.Hq = ext(self.Hq); self.Hq[0, n] = phi
        self.Hz, self.Hy, self.Hzh = ext(self.Hz), ext(self.Hy), ext(self.Hzh)
        self.Hd = Hd_extra.copy()
        Phi[:n, :n] = self.Phi
        Gam[:n] = self.Gam
        # z' gets B * phi * dstate; p' gets B * phi * dstate (as in the base: p' = (A-BK) zh + B (e + d))
        Phi[:NX, n] = p.B0[:, 0] * phi
        Phi[NX:2 * NX, n] = p.B0[:, 0] * phi
        Phi[n, n] = phi
        Gam[n, 8] = 1.0
        self.Phi, self.Gam, self.N = Phi, Gam, N
        self.Sig = solve_discrete_lyapunov(Phi, Gam @ N @ Gam.T)
        self.J = float(np.trace(p.Q @ self.Sig[:NX, :NX]) + np.trace(p.R @ (self.Hq @ self.Sig @ self.Hq.T + self.Jq @ self.N @ self.Jq.T)))


def innovation_cov(L, theta, kind):
    """Stationary covariance of the model's one-step prediction errors on the logged world L (any state dimension)."""
    A, B, Kp, Sth = p.predictor_matrices(theta, kind)
    n1 = L.Phi.shape[0]
    Phi = np.zeros((n1 + NX, n1 + NX)); Gam = np.zeros((n1 + NX, L.nn))
    Phi[:n1, :n1] = L.Phi; Gam[:n1] = L.Gam
    Phi[n1:, :n1] = B @ L.Hq + Kp @ L.Hy
    Phi[n1:, n1:] = A - Kp @ p.C
    Gam[n1:] = B @ L.Jq + Kp @ L.Jy
    if np.max(np.abs(np.linalg.eigvals(Phi))) >= 1:
        return None, Sth
    Sg = solve_discrete_lyapunov(Phi, Gam @ L.N @ Gam.T)
    He = np.hstack([L.Hy, -p.C])
    return He @ Sg @ He.T + L.Jy @ L.N @ L.Jy.T, Sth


def nll(theta, L, kind):
    Se, Sth = innovation_cov(L, theta, kind)
    if Se is None:
        return 1e6
    return 0.5 * np.linalg.slogdet(Sth)[1] + 0.5 * np.trace(np.linalg.solve(Sth, Se))


def hessian(f, x0, h):
    """Central finite-difference Hessian."""
    n = len(x0); Hm = np.zeros((n, n)); f0 = f(x0)
    for i in range(n):
        for j in range(i, n):
            if i == j:
                e = np.zeros(n); e[i] = h[i]
                Hm[i, i] = (f(x0 + e) - 2 * f0 + f(x0 - e)) / h[i] ** 2
            else:
                ei = np.zeros(n); ei[i] = h[i]; ej = np.zeros(n); ej[j] = h[j]
                Hm[i, j] = Hm[j, i] = (f(x0 + ei + ej) - f(x0 + ei - ej) - f(x0 - ei + ej) + f(x0 - ei - ej)) / (4 * h[i] * h[j])
    return Hm


def fisher(L, kind, rel=2e-3):
    th = p.theta_true(kind)
    return hessian(lambda t: nll(t, L, kind), th, rel * np.maximum(np.abs(th), 0.02))


def cost_hessian(kind, rel=2e-3):
    th = p.theta_true(kind)
    f = lambda t: p.J_of(p.lqg_controller(*p.model(t, kind)))
    return hessian(f, th, rel * np.maximum(np.abs(th), 0.02))


def years(H, I, eps, Js):
    return float(np.trace(H @ np.linalg.inv(I)) / (2 * eps * Js) / 12.0)


def contributions(H, I, names):
    """Split tr(H I^{-1}) into the parameters' diagonal shares (H_ii (I^{-1})_ii) and the cross terms."""
    Ii = np.linalg.inv(I)
    tot = float(np.trace(H @ Ii))
    diag = {n: float(H[i, i] * Ii[i, i]) / tot for i, n in enumerate(names)}
    return tot, diag


NAMES4 = ['pumping -> head', 'head -> toe', 'toe retention', 'clay -> toe']
NAMES8 = NAMES4 + ['head retention', 'recharge -> head', 'toe -> clay', 'clay retention']


def run():
    log, res = [], {}
    Js = p.J_of(p.lqg_controller(p.A0, p.B0))
    res['J_star'] = Js
    H4, H8 = cost_hessian('phys4'), cost_hessian('phys8')
    # check of the finite-difference step
    H4b = cost_hessian('phys4', rel=5e-3)
    res['H_step_check'] = float(np.max(np.abs(H4 - H4b)) / np.max(np.abs(H4)))
    res['H4'] = H4.tolist(); res['H8'] = H8.tolist()
    log.append(f'J* = {Js:.4f}; cost Hessian of the 4-parameter model (relative change with the step: {res["H_step_check"]:.1e}); '
               f'eigenvalues {np.round(np.linalg.eigvalsh(H4), 4)}')
    base = {}
    for name, gamma in [('near-optimal', 1.0), ('timid', 0.4)]:
        for sd_e in [0.03, 0.1, 0.3]:
            L = p.Logged(np.inf, sd_e, 0.0, gamma)
            I4 = fisher(L, 'phys4'); I8 = fisher(L, 'phys8')
            I4b = fisher(L, 'phys4', rel=5e-3)
            row = dict(gamma=gamma, sd_e=sd_e, J_op=L.J, I4=I4.tolist(), I_step_check=float(np.max(np.abs(I4 - I4b)) / np.max(np.abs(I4))),
                       years4_1pct=years(H4, I4, 0.01, Js), years4_01pct=years(H4, I4, 0.001, Js),
                       years8_1pct=years(H8, I8, 0.01, Js), years8_01pct=years(H8, I8, 0.001, Js),
                       contrib4=contributions(H4, I4, NAMES4)[1], contrib8=contributions(H8, I8, NAMES8)[1],
                       crlb_sd4=np.sqrt(np.diag(np.linalg.inv(I4)) / 120).tolist())
            base[f'{name}_{sd_e}'] = row
            log.append(f'operators {name:12s} unrecorded variation sd {sd_e:.2f} (cost {100 * (L.J - Js) / Js:+.1f}%): years of logs for 1% / 0.1% excess, '
                       f'4-parameter model {row["years4_1pct"]:.1f} / {row["years4_01pct"]:.0f}, 8-parameter model {row["years8_1pct"]:.1f} / {row["years8_01pct"]:.0f}; '
                       f'shares of tr(H I^-1) (4 par.) ' + ', '.join(f'{k} {100 * v:.0f}%' for k, v in row['contrib4'].items()) +
                       f'; Fisher step check {row["I_step_check"]:.1e}')
    res['base'] = base

    # slow clay memory: vary the clay retention (true value 0.995) for the 4-parameter model, near-optimal operators
    clay = []
    A_save = p.A0.copy()
    for acc in [0.95, 0.98, 0.99, 0.995, 0.998]:
        p.A0[3, 3] = acc
        try:
            Jsa = p.J_of(p.lqg_controller(p.A0, p.B0))
            Ha = cost_hessian('phys4')
            La = p.Logged(np.inf, 0.1, 0.0, 1.0)
            Ia = fisher(La, 'phys4')
            clay.append(dict(a_cc=acc, J_star=Jsa, years_1pct=years(Ha, Ia, 0.01, Jsa), contrib=contributions(Ha, Ia, NAMES4)[1],
                             open_loop=float(np.max(np.abs(np.linalg.eigvals(p.A0))))))
            log.append(f'clay retention {acc}: memory {1 / (1 - acc):.0f} months, open-loop radius {clay[-1]["open_loop"]:.4f}, J* {Jsa:.4f}; '
                       f'years for 1% excess {clay[-1]["years_1pct"]:.1f}; share of clay -> toe {100 * clay[-1]["contrib"]["clay -> toe"]:.0f}%')
        finally:
            p.A0[:] = A_save
    res['clay'] = clay

    # goal-oriented dither design: near-optimal operators, sd_e 0.1; dithers of equal cost to the operators
    L0 = p.Logged(np.inf, 0.1, 0.0, 1.0)
    I0 = fisher(L0, 'phys4')
    y0 = years(H4, I0, 0.01, Js)
    design = []
    for budget in [0.005, 0.02]:                       # extra cost to the operators, fraction of J*
        for phi in [0.0, 0.5, 0.8, 0.9, 0.95, 0.98]:
            f = lambda sd: (LoggedAR(np.inf, 0.1, sd, 1.0, phi).J - L0.J) / Js - budget
            sd = brentq(f, 1e-4, 3.0, xtol=1e-6)
            Ld = LoggedAR(np.inf, 0.1, sd, 1.0, phi)
            Id = fisher(Ld, 'phys4')
            design.append(dict(budget=budget, phi=phi, sd_d=sd, years_1pct=years(H4, Id, 0.01, Js), logdetI=float(np.linalg.slogdet(Id)[1]),
                               trHI=float(np.trace(H4 @ np.linalg.inv(Id)))))
            log.append(f'dither cost {100 * budget:.1f}% of J*, AR(1) phi {phi:.2f}: sd {sd:.3f}; years for 1% {design[-1]["years_1pct"]:.2f} '
                       f'(no dither {y0:.2f}); log det I {design[-1]["logdetI"]:.2f}')
    res['design'] = design
    res['years_no_dither'] = y0
    for budget in [0.005, 0.02]:
        rows = [d for d in design if d['budget'] == budget]
        go = min(rows, key=lambda d: d['years_1pct']); dopt = max(rows, key=lambda d: d['logdetI'])
        res[f'choice_{budget}'] = dict(goal_oriented_phi=go['phi'], goal_years=go['years_1pct'], d_optimal_phi=dopt['phi'], d_years=dopt['years_1pct'],
                                       white_years=[d for d in rows if d['phi'] == 0.0][0]['years_1pct'])
        log.append(f'budget {100 * budget:.1f}%: goal-oriented choice phi {go["phi"]} ({go["years_1pct"]:.2f} years), D-optimal choice phi {dopt["phi"]} '
                   f'({dopt["years_1pct"]:.2f} years), white dither {res[f"choice_{budget}"]["white_years"]:.2f} years')
    # what shortens the years: monitoring networks and how firmly the operators control (general module)
    import vitet_monitor as vm
    a0 = vm.analyse(vm.BASE_NET)
    res['check_general_vs_base'] = abs(a0['years_1pct'] - base['near-optimal_0.1']['years4_1pct'])
    nets = [vm.BASE_NET,
            vm.Net([[0, 1, 0, 0], [0, 0, 1, 0.5]], [0.05, 0.15], 'sentinel chloride noise halved'),
            vm.Net([[0, 1, 0, 0], [0, 0, 1, 0.5], [0, 0, 1, 0]], [0.05, 0.3, 0.1], 'the operators\' toe reading logged'),
            vm.Net([[0, 1, 0, 0], [0, 0, 1, 0.5], [0, 0, 1, 2.0]], [0.05, 0.3, 0.3], 'a second sentinel that sees more clay salt'),
            vm.Net([[0, 1, 0, 0], [0, 0, 1, 0.5]], [0.02, 0.3], 'head noise 0.02 instead of 0.05'),
            vm.Net([[0, 1, 0, 0], [0, 0, 1, 0.5], [1, 0, 0, 0]], [0.05, 0.3, 0.1], 'a soil-moisture probe')]
    mon = []
    for n in nets:
        r = vm.analyse(n)
        mon.append(dict(net=n.name, J_star=r['J_star'], years_1pct=r['years_1pct'], years_01pct=r['years_01pct'], logdetI=r['logdetI'],
                        trHI=r['trHI'], abs_excess_10y=r['trHI'] / (2 * 120)))
        log.append(f'monitoring: {n.name:45s} J* {r["J_star"]:.4f}; years for 1% {r["years_1pct"]:.1f}; absolute excess after 10 years '
                   f'{r["trHI"] / 240:.5f}; log det I {r["logdetI"]:.2f}')
    res['monitoring'] = mon
    gam = []
    for g in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]:
        r = vm.analyse(vm.BASE_NET, gamma=g)
        gam.append(dict(gamma=g, J_op_rel=(r['J_op'] - r['J_star']) / r['J_star'], years_1pct=r['years_1pct']))
        log.append(f'operators at {g:.1f} x the optimal gain: their cost {100 * gam[-1]["J_op_rel"]:+.1f}%, years for 1% {r["years_1pct"]:.1f}')
    res['gamma'] = gam
    # an equal-cost comparison: dither versus detuned operators (extra cost over optimal operators, % of J*)
    g08 = [x for x in gam if x['gamma'] == 0.8][0]
    extra = g08['J_op_rel'] - gam[0]['J_op_rel']
    f = lambda sd: (LoggedAR(np.inf, 0.1, sd, 1.0, 0.98).J - L0.J) / Js - extra
    sd_eq = brentq(f, 1e-4, 3.0, xtol=1e-6)
    y_eq = years(H4, fisher(LoggedAR(np.inf, 0.1, sd_eq, 1.0, 0.98), 'phys4'), 0.01, Js)
    res['equal_cost'] = dict(extra_cost=extra, gamma08_years=g08['years_1pct'], dither_sd=sd_eq, dither_years=y_eq)
    log.append(f'equal extra cost {100 * extra:.1f}% of J*: operators at 0.8 x gain -> {g08["years_1pct"]:.1f} years; slow dither (phi 0.98, sd {sd_eq:.3f}) -> {y_eq:.1f} years')
    res['worst_case_horizon_factor'] = (1 / (1 - 0.995)) ** 3
    json.dump(p.clean(res), open(os.path.join(HERE, 'vitet_results.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'vitet.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
