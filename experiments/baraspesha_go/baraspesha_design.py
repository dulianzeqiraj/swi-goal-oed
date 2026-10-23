"""Goal-oriented choice of the control wells at which chloride is measured (BARASPESHA-GO, part C).

All treated wells are measured. A pilot of 20 control wells (space-filling) is measured first and calibrates the
simulator; the remaining budget is spent by one of five rules:
  random          m wells at random (no pilot)
  space_filling   greedy maximin distance in the standardized covariates (no pilot)
  nearest         nearest unmeasured control to each treated well in turn (matching; no pilot)
  calib_D         pilot + greedy D-optimal design for the three calibration parameters
  goal            pilot + greedy minimization of the worst-case mean squared error of psi in the physics kernel,
                  V(D) = sup over the unit ball of (bias)^2 + variance, which for the minimax weights equals
                  k11 - c_D' (K_DD + Sigma_D)^-1 c_D (Proposition O); rank-one updates make each step O(N0^2).
The design-stage noise model is the physics one, var = sigma_eps^2 + v_post s_K^2, with the measurement-error
variances known from the pumping tests (v_post = posterior variance of log K given the test).
"""
import numpy as np
import baraspesha_model as M
import baraspesha_est as E

PILOT = 10
C0 = 1.0                       # constant kernel component (weights summing to one)
V_POST = 1.0 / (1 / M.TAU_U ** 2 + 1 / M.TAU_E ** 2)


def maximin(Zc, m, start):
    sel = [start]
    d = ((Zc - Zc[start]) ** 2).sum(1)
    while len(sel) < m:
        j = int(np.argmax(d))
        sel.append(j)
        d = np.minimum(d, ((Zc - Zc[j]) ** 2).sum(1))
    return sel


def nearest(Zc, Zt, m, rng):
    sel, taken = [], np.zeros(len(Zc), bool)
    order = rng.permutation(len(Zt))
    while len(sel) < m:
        for t in order:
            d = ((Zc - Zt[t]) ** 2).sum(1)
            d[taken] = np.inf
            j = int(np.argmin(d))
            sel.append(j); taken[j] = True
            if len(sel) == m:
                break
    return sel


def design_kernel(F, Z, Cand, T, th, J_c, S1, r_pilot, J_pilot, P=E.PHYS):
    """Physics kernel over all candidate controls and the treated wells, at the pilot calibration."""
    Zm = Z[:, [1, 3]]
    s2c = r_pilot @ r_pilot / max(len(r_pilot) - 3, 1)
    G = P['kcal'] ** 2 * s2c * np.linalg.pinv(J_pilot.T @ J_pilot)
    Kcc = E.phys_kernel(J_c, J_c, Zm[Cand], Zm[Cand], Z[Cand], Z[Cand], P, G) + C0
    kc1 = E.phys_kernel(J_c, S1, Zm[Cand], Zm[T], Z[Cand], Z[T], P, G).mean(1) + C0
    k11 = E.phys_kernel(S1, S1, Zm[T], Zm[T], Z[T], Z[T], P, G).mean() + C0
    return Kcc, kc1, k11


def goal_greedy(Kcc, kc1, k11, d, pilot, m):
    """Greedy minimization of V(D) = k11 - c_D'(K_DD + diag d_D)^-1 c_D, starting from the pilot."""
    R = Kcc.copy(); r = kc1.copy(); V = k11
    sel = []
    def add(j):
        nonlocal R, r, V
        den = R[j, j] + d[j]
        V -= r[j] ** 2 / den
        rj, Rj = r[j], R[:, j].copy()
        r = r - Rj * rj / den
        R = R - np.outer(Rj, Rj) / den
        sel.append(j)
    for j in pilot:
        add(j)
    path = [V]
    while len(sel) < m:
        score = r ** 2 / (np.diag(R) + d)
        score[sel] = -np.inf
        add(int(np.argmax(score)))
        path.append(V)
    return sel, V


def V_of(Kcc, kc1, k11, d, sel):
    sel = np.asarray(sel)
    A = Kcc[np.ix_(sel, sel)] + np.diag(d[sel])
    c = kc1[sel]
    return float(k11 - c @ np.linalg.solve(A, c))


def calib_greedy(J_c, d, pilot, m, eps=1e-6):
    Minf = eps * np.eye(3)
    sel = []
    for j in pilot:
        Minf += np.outer(J_c[j], J_c[j]) / d[j]; sel.append(j)
    while len(sel) < m:
        Mi = np.linalg.inv(Minf)
        score = np.einsum('ij,jk,ik->i', J_c, Mi, J_c) / d
        score[sel] = -np.inf
        j = int(np.argmax(score))
        Minf += np.outer(J_c[j], J_c[j]) / d[j]; sel.append(j)
    return sel


BATCH = 10


def sequential(F, Z, Cand, T, m, rule, P=E.PHYS):
    """Batch-sequential design: measure the pilot, calibrate, choose the next batch by the rule (goal or calib_D) at
    the current calibration and noise model, measure it, recalibrate, and so on until m wells are measured."""
    Zc = Z[Cand]
    start = int(np.argmin(((Zc - Zc.mean(0)) ** 2).sum(1)))
    sel = maximin(Zc, PILOT, start)
    while len(sel) < m:
        idx = Cand[np.asarray(sel)]
        th, J_s, r_s = M.calibrate(F['xw'][idx], F['Q0'][idx], F['kmeas'][idx], F['Y'][idx])
        J_c = M.sens(F['xw'][Cand], F['Q0'][Cand], F['kmeas'][Cand], th)
        d = M.SIGMA_EPS ** 2 + V_POST * J_c[:, 0] ** 2
        nxt = min(m, len(sel) + BATCH)
        if rule == 'goal':
            S1 = M.sens(F['xw'][T], F['Q0'][T], F['kmeas'][T], th)
            Kcc, kc1, k11 = design_kernel(F, Z, Cand, T, th, J_c, S1, r_s, J_s, P)
            sel = goal_greedy(Kcc, kc1, k11, d, sel, nxt)[0]
        else:
            sel = calib_greedy(J_c, d, sel, nxt)
    return sel, th if m > PILOT else None


def final_V(F, Z, Cand, T, sel, P=E.PHYS):
    """Design criterion of a finished design, evaluated at the calibration on the measured wells."""
    idx = Cand[np.asarray(sel)]
    th, J_s, r_s = M.calibrate(F['xw'][idx], F['Q0'][idx], F['kmeas'][idx], F['Y'][idx])
    J_c = M.sens(F['xw'][Cand], F['Q0'][Cand], F['kmeas'][Cand], th)
    S1 = M.sens(F['xw'][T], F['Q0'][T], F['kmeas'][T], th)
    d = M.SIGMA_EPS ** 2 + V_POST * J_c[:, 0] ** 2
    Kcc, kc1, k11 = design_kernel(F, Z, Cand, T, th, J_c, S1, r_s, J_s, P)
    return V_of(Kcc, kc1, k11, d, sel), float(np.mean(np.abs(J_c[sel, 0]) > 0.05))


def run_designs(F, budgets, rng, P=E.PHYS):
    """For one well field: the five designs at each budget, BARASPESHA (and aug_sim) estimates on the measured
    control wells."""
    A = F['A']; T = np.where(A == 1)[0]; Cand = np.where(A == 0)[0]
    Z = M.standardize(M.features(F), M.features(F))
    Zc, Zt = Z[Cand], Z[T]
    psi = F['m0'][T].mean()
    start = int(np.argmin(((Zc - Zc.mean(0)) ** 2).sum(1)))
    rows = []
    for m in budgets:
        designs = {
            'random': list(rng.choice(len(Cand), m, replace=False)),
            'space_filling': maximin(Zc, m, start),
            'nearest': nearest(Zc, Zt, m, rng),
            'calib_D': sequential(F, Z, Cand, T, m, 'calib_D', P)[0],
            'goal': sequential(F, Z, Cand, T, m, 'goal', P)[0],
        }
        for name, sel in designs.items():
            idx0 = Cand[np.asarray(sel)]
            out = E.estimate_all(F, rng, P=P, idx0=idx0, methods=['baraspesha', 'aug_sim'])
            b = out['baraspesha']; a = out['aug_sim']
            V, ftr = final_V(F, Z, Cand, T, sel, P)
            rows.append(dict(m=m, design=name, V=V, err=b[0] - psi,
                             cover=float(b[2] <= psi <= b[3]), length=b[3] - b[2], err_aug=a[0] - psi,
                             cover_aug=float(a[2] <= psi <= a[3]), frac_transition=ftr))
    return rows
