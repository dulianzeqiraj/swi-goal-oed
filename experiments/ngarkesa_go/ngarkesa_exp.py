"""NGARKESA-GO experiment: goal-oriented porewater sampling of a coastal aquitard with electroneutral ion transport.
Writes ngarkesa_results.json and ngarkesa_grid.npz.   Run: python3 ngarkesa_exp.py   (about 6 minutes on 4 cores)

Setting. A clay aquitard (3 m) lies under the aquifer of a coastal well field. For 40 years the aquifer carried a
25 % seawater mixture and salt entered the aquitard; the aquifer is now freshened, and salt diffuses back into it.
Goals: the recovery times after which the back-diffusion flux keeps the aquifer below the drinking-water values
(chloride 250 mg/L, sodium 200 mg/L) for a freshwater throughflow of 0.07 m/yr per unit area of aquitard.
Uncertain: the formation factor F (log-uniform 3.5-12) and the cation-exchange capacity CEC (5-30 meq/100 g),
on a 25 x 21 grid (uniform prior over the grid).

Models. 'np': zero-current Nernst-Planck with Gaines-Thomas exchange (the reference, electroneutral by
construction); 'fick_1': every ion with the chloride coefficient (electroneutral, the usual simplification);
'fick_i': every ion with its own coefficient and no electrical coupling.

Designs (data collected today, at the end of the salinization phase):
  R  formation factor from a resistivity log (log-normal error 20 %)
  L  CEC measured on a core (relative error 15 %)
  C  porewater chloride at 4 depths (log-normal error 5 %)
  I  porewater Cl, Na, Ca and Mg at the same 4 depths (log-normal error 5 %)
and their pairs. For each design the preposterior analysis draws a true parameter set from the prior and noisy
data, computes the exact posterior over the grid and records: the posterior standard deviation of each recovery
time, whether the deadline decision (recovered within 20 years?) is correct, and the information gained about
the parameters (the parameter-oriented, D-optimality-type criterion).
"""
import json
import os
import time
from multiprocessing import Pool
import numpy as np
import ngarkesa as N

HERE = os.path.dirname(os.path.abspath(__file__))
NF, NC = 25, 21
FGRID = np.exp(np.linspace(np.log(3.5), np.log(12.0), NF))
CGRID = np.linspace(5.0, 30.0, NC)
DEPTHS = np.array([0.2, 0.5, 0.9, 1.4])
QW = 0.07                                                   # m/yr of fresh throughflow per m2 of aquitard
J_CL = QW * (250.0 / 35.45 - N.FRESH[4])                    # mol/m2/yr: chloride increment to 250 mg/L
J_NA = QW * (200.0 / 22.99 - N.FRESH[0])                    # sodium increment to 200 mg/L
DEADLINE = 20.0
SIG_C, SIG_R, SIG_L = 0.05, 0.20, 0.15
NDRAW = 40


def tstar(t, J, thr):
    """time after which the flux stays below thr, linear interpolation between records."""
    out = np.empty(J.shape[1])
    for p in range(J.shape[1]):
        above = np.where(J[:, p] >= thr)[0]
        if len(above) == 0:
            out[p] = 0.0
        elif above[-1] == len(t) - 1:
            out[p] = np.inf
        else:
            k = above[-1]
            out[p] = t[k] + (t[k + 1] - t[k]) * (J[k, p] - thr) / (J[k, p] - J[k + 1, p])
    return out


def run_chunk(args):
    F, C, mode = args
    o = N.simulate(F, C, mode=mode, sample_depths=DEPTHS)
    return dict(tcl=tstar(o['t2'], o['Jup'][:, :, 4], J_CL), tna=tstar(o['t2'], o['Jup'][:, :, 0], J_NA),
                samples=o['samples'], charge=o['charge_max'], x=o['x'], c1=o['c1'])


def run_grid(mode, FF, CC, pool):
    chunks = np.array_split(np.arange(FF.size), 8)
    res = pool.map(run_chunk, [(FF[ix], CC[ix], mode) for ix in chunks])
    return dict(tcl=np.concatenate([r['tcl'] for r in res]), tna=np.concatenate([r['tna'] for r in res]),
                samples=np.concatenate([r['samples'] for r in res]), charge=max(r['charge'] for r in res),
                c1=np.concatenate([r['c1'] for r in res]), x=res[0]['x'])


def design_loglik(design, data, model):
    """log-likelihood of the data of one draw for every grid point of a model ([G]).
    data: dict with 'logF', 'cec', 'cl' (log Cl at depths), 'ions' (log Cl, Na, Ca, Mg at depths)."""
    ll = 0.0
    if 'R' in design:
        ll = ll - 0.5 * ((data['logF'] - model['logF']) / SIG_R) ** 2
    if 'L' in design:
        ll = ll - 0.5 * ((data['cec'] - model['cec']) / (SIG_L * data['cec'])) ** 2
    if 'I' in design:
        ll = ll - 0.5 * (((data['ions'][None] - model['ions']) / SIG_C) ** 2).sum(axis=1)
    elif 'C' in design:
        ll = ll - 0.5 * (((data['cl'][None] - model['cl']) / SIG_C) ** 2).sum(axis=1)
    return ll


def main():
    t0 = time.time()
    FF, CC = [a.ravel() for a in np.meshgrid(FGRID, CGRID, indexing='ij')]
    G = FF.size
    with Pool(4) as pool:
        R = {m: run_grid(m, FF, CC, pool) for m in ['np', 'fick_1', 'fick_i']}
    print(f'forward runs {time.time() - t0:.0f}s')
    ION = [4, 0, 2, 3]                                       # Cl, Na, Ca, Mg
    mods = {}
    for m in ['np', 'fick_1']:
        s = R[m]['samples']                                  # [G, 7, ndepth]
        mods[m] = dict(logF=np.log(FF), cec=CC, cl=np.log(s[:, 4, :]),
                       ions=np.log(s[:, ION, :]).reshape(G, -1), tcl=R[m]['tcl'], tna=R[m]['tna'])
    truth = mods['np']
    designs = ['R', 'L', 'C', 'I', 'R+L', 'C+L', 'R+C', 'R+I', 'L+I']
    rng = np.random.default_rng(20261020)
    prior_H = np.log(G)
    out = {}
    for d in designs:
        sd_cl, sd_na, ok_cl, ok_na, ig, ok_cl_f1, ok_na_f1, bias_cl_f1, bias_na_f1 = ([] for _ in range(9))
        for g in range(G):
            for _ in range(NDRAW):
                data = dict(logF=truth['logF'][g] + SIG_R * rng.standard_normal(),
                            cec=truth['cec'][g] * (1 + SIG_L * rng.standard_normal()),
                            cl=truth['cl'][g] + SIG_C * rng.standard_normal(len(DEPTHS)),
                            ions=truth['ions'][g] + SIG_C * rng.standard_normal(truth['ions'].shape[1]))
                for m, store in (('np', True), ('fick_1', False)):
                    ll = design_loglik(d, data, mods[m])
                    w = np.exp(ll - ll.max()); w /= w.sum()
                    mcl = (w * mods[m]['tcl']).sum(); mna = (w * mods[m]['tna']).sum()
                    pcl = (w * (mods[m]['tcl'] <= DEADLINE)).sum(); pna = (w * (mods[m]['tna'] <= DEADLINE)).sum()
                    tcl, tna = truth['tcl'][g], truth['tna'][g]
                    if store:
                        sd_cl.append(np.sqrt((w * (mods[m]['tcl'] - mcl) ** 2).sum()))
                        sd_na.append(np.sqrt((w * (mods[m]['tna'] - mna) ** 2).sum()))
                        ok_cl.append((pcl >= 0.5) == (tcl <= DEADLINE))
                        ok_na.append((pna >= 0.5) == (tna <= DEADLINE))
                        ww = w[w > 0]
                        ig.append(prior_H + (ww * np.log(ww)).sum())
                    else:
                        ok_cl_f1.append((pcl >= 0.5) == (tcl <= DEADLINE))
                        ok_na_f1.append((pna >= 0.5) == (tna <= DEADLINE))
                        bias_cl_f1.append(mcl - tcl); bias_na_f1.append(mna - tna)
        out[d] = dict(sd_tcl=float(np.mean(sd_cl)), sd_tna=float(np.mean(sd_na)), correct_cl=float(np.mean(ok_cl)),
                      correct_na=float(np.mean(ok_na)), info_gain_nats=float(np.mean(ig)),
                      fick1_correct_cl=float(np.mean(ok_cl_f1)), fick1_correct_na=float(np.mean(ok_na_f1)),
                      fick1_bias_tcl=float(np.mean(bias_cl_f1)), fick1_bias_tna=float(np.mean(bias_na_f1)))
        print(d, {k: round(v, 3) for k, v in out[d].items()})
    prior = dict(sd_tcl=float(truth['tcl'].std()), sd_tna=float(truth['tna'].std()),
                 p_cl_by_deadline=float(np.mean(truth['tcl'] <= DEADLINE)),
                 p_na_by_deadline=float(np.mean(truth['tna'] <= DEADLINE)))
    struct = {}
    for m in ['fick_1', 'fick_i']:
        rel_cl = R[m]['tcl'] / R['np']['tcl'] - 1; rel_na = R[m]['tna'] / R['np']['tna'] - 1
        struct[m] = dict(rel_tcl_mean=float(rel_cl.mean()), rel_tcl_min=float(rel_cl.min()), rel_tcl_max=float(rel_cl.max()),
                         rel_tna_mean=float(rel_na.mean()), rel_tna_min=float(rel_na.min()), rel_tna_max=float(rel_na.max()),
                         charge_max=float(R[m]['charge']))
    struct['np'] = dict(charge_max=float(R['np']['charge']))
    # sensitivity of the goals to each parameter (range of the goal over the prior range, other parameter at mid)
    T = {k: R['np'][k].reshape(NF, NC) for k in ['tcl', 'tna']}
    sens = {k: dict(over_F=float(T[k][:, NC // 2].max() - T[k][:, NC // 2].min()),
                    over_CEC=float(T[k][NF // 2, :].max() - T[k][NF // 2, :].min())) for k in T}
    res = dict(params=dict(L=3.0, M=60, t1=40.0, t2=60.0, f_sea=0.25, phi=N.PHI, rhob=N.RHOB, qw=QW, J_CL=J_CL, J_NA=J_NA,
                           deadline=DEADLINE, depths=DEPTHS.tolist(), sig_c=SIG_C, sig_r=SIG_R, sig_l=SIG_L, ndraw=NDRAW,
                           Fgrid=FGRID.tolist(), CECgrid=CGRID.tolist(), D0_25C=N.D25.tolist(), temp_factor=N.TFAC,
                           sea=N.SEA.tolist(), fresh=N.FRESH.tolist(), species=N.SP),
               prior=prior, designs=out, structure=struct, sensitivity=sens,
               goal_range=dict(tcl=[float(R['np']['tcl'].min()), float(R['np']['tcl'].max())],
                               tna=[float(R['np']['tna'].min()), float(R['np']['tna'].max())]))
    json.dump(res, open(os.path.join(HERE, 'ngarkesa_results.json'), 'w'), indent=1)
    mid = (NF // 2) * NC + NC // 2
    np.savez_compressed(os.path.join(HERE, 'ngarkesa_grid.npz'), F=FF, CEC=CC, x=R['np']['x'],
                        tcl_np=R['np']['tcl'], tna_np=R['np']['tna'], tcl_f1=R['fick_1']['tcl'], tna_f1=R['fick_1']['tna'],
                        tcl_fi=R['fick_i']['tcl'], tna_fi=R['fick_i']['tna'],
                        c1_mid_np=R['np']['c1'][mid], c1_mid_f1=R['fick_1']['c1'][mid], c1_mid_fi=R['fick_i']['c1'][mid],
                        mid=mid)
    print(f'done {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
