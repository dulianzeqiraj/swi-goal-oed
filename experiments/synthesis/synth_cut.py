"""Chloride sufficiency and the price of the cut (innovation of the synthesis article).

Linearised at the prior-mean truth of RITMI-GO (../ritmi_go): history (34 data) + five years of status-quo monitoring
(monthly Cl and half-yearly ions at wells 503, 341, 340; 360 data). For the three 2045 goals it compares
  joint      all data inform all 12 parameters;
  Cl only    chloride data only;
  ions only  the six other ions only;
  cut        transport + memory (7 parameters) from chloride alone, exchange + reaction (5) from all data with the
             first block held fixed (linear-Gaussian form of the cut of review 42, Proposition 5);
and the shift of each goal when the ion data carry a systematic error, as a misspecified reactive closure would
produce. Writes synth_cut.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ritmi_go'))
import ritmi_core as C   # noqa: E402
import ritmi_model as R  # noqa: E402

H_FD = 0.05
T_IDX = list(range(7))            # s_v, alpha_L, f_0, a_1, b_1, a_2, b_2: transport and memory
R_IDX = list(range(7, 12))        # E, K_K, K_Ca, K_Mg, k_sr: exchange and reaction
GNAMES = ['Cl at 5 km (mg/L)', 'Na at 3 km (mg/L)', 'Ca + Mg at 3 km (meq/L)']
ION_NAMES = R.SPECIES[1:]


def rows_by_species(n_hist, n_exp):
    """species index (0 = Cl) of every row of [obs_hist; obs_exp]"""
    sp = []
    for _ in range(4):
        sp += list(range(7))                                  # 2016: seven ions at four wells
    sp += [0] * 6                                             # Cl trend at 503 and 341
    assert len(sp) == n_hist
    ncl = 3 * len(C.CL_MONTHS)
    sp += [0] * ncl
    for _ in range(len(C.ION_TIMES)):
        for _ in range(3):
            sp += list(range(1, 7))
    assert len(sp) == n_hist + n_exp
    return np.array(sp)


def cov_joint(Jw):
    return np.linalg.inv(Jw.T @ Jw + np.eye(Jw.shape[1]))


def cov_cut(Jw, cl):
    """linear-Gaussian cut: theta_T from the chloride rows, theta_R from all rows given theta_T"""
    JT, JR = Jw[:, T_IDX], Jw[:, R_IDX]
    S1 = np.linalg.inv(JT[cl].T @ JT[cl] + np.eye(len(T_IDX)))
    S2 = np.linalg.inv(JR.T @ JR + np.eye(len(R_IDX)))
    A = S2 @ JR.T
    p = Jw.shape[1]
    S = np.zeros((p, p))
    S[np.ix_(T_IDX, T_IDX)] = S1
    S[np.ix_(R_IDX, R_IDX)] = A @ JT @ S1 @ JT.T @ A.T + S2
    S[np.ix_(T_IDX, R_IDX)] = -S1 @ JT.T @ A.T
    S[np.ix_(R_IDX, T_IDX)] = S[np.ix_(T_IDX, R_IDX)].T
    return S, A


def main():
    U = C.fd_ensemble(H_FD)
    ref = R.simulate(C.to_P(U), {'kind': 'const'})
    Jh, Je = C.jac(C.obs_hist(ref), H_FD), C.jac(C.obs_exp(ref), H_FD)
    G = C.jac(C.goals(ref), H_FD)[:3]
    J = np.vstack([Jh, Je])
    Jw = J / C.SIG_OBS
    sp = rows_by_species(Jh.shape[0], Je.shape[0])
    cl, io = np.where(sp == 0)[0], np.where(sp > 0)[0]
    out = dict(n_rows=int(J.shape[0]), n_cl=int(cl.size), n_ion=int(io.size))
    out['max_abs_dCl_dR'] = float(np.abs(J[np.ix_(cl, R_IDX)]).max())       # Proposition 2 of review 42: ~0
    out['max_abs_dGcl_dR'] = float(np.abs(G[0, R_IDX]).max())
    sd = lambda S: np.sqrt(np.diag(G @ S @ G.T)).tolist()
    Sj = cov_joint(Jw)
    Sc, A = cov_cut(Jw, cl)
    Sh = cov_joint(Jh / C.SIG_OBS)
    out['goal_sd'] = {
        'prior': sd(np.eye(12)), 'history': sd(Sh), 'Cl only': sd(cov_joint(Jw[cl])),
        'ions only': sd(cov_joint(Jw[io])), 'joint': sd(Sj), 'cut': sd(Sc)}
    # chloride sufficiency at vanishing error: share of the Cl-goal gradient outside the row space of the Cl data
    gT = G[0, T_IDX]
    _, s, Vt = np.linalg.svd(Jw[np.ix_(cl, T_IDX)], full_matrices=False)
    tol = s.max() * 1e-6
    Vr = Vt[s > tol]
    out['cl_goal_unseen_frac'] = float(np.linalg.norm(gT - Vr.T @ (Vr @ gT)) / np.linalg.norm(gT))
    out['cl_rank_T'] = int((s > tol).sum())
    # protection: shift of each goal when one ion's data are all biased by one error sd (5 %), and the worst case
    # over ion-data errors with an RMS of one sd
    shifts = {}
    for k, name in enumerate(ION_NAMES, start=1):
        d = (sp == k).astype(float)                            # whitened: +1 sd on every datum of that ion
        dth = np.zeros(12)
        dth[R_IDX] = A @ d                                     # the cut moves only theta_R (Cl rows carry no error)
        shifts[name] = dict(joint=(G @ Sj @ Jw.T @ d).tolist(), cut=(G @ dth).tolist())
    # worst case: max over d supported on ion rows with ||d|| = sqrt(n_ion)
    Mj = G @ Sj @ Jw[io].T
    Mc = G[:, R_IDX] @ A[:, io]
    worst = dict(joint=(np.linalg.norm(Mj, axis=1) * np.sqrt(io.size)).tolist(),
                 cut=(np.linalg.norm(Mc, axis=1) * np.sqrt(io.size)).tolist())
    out['shift_one_sd'] = shifts
    out['shift_worst_rms1'] = worst
    out['goals'] = GNAMES
    with open(os.path.join(HERE, 'synth_cut.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('shift_one_sd',)}, indent=1))
    for k, v in shifts.items():
        print(k, 'joint', np.round(v['joint'], 2), 'cut', np.round(v['cut'], 2))


if __name__ == '__main__':
    main()
