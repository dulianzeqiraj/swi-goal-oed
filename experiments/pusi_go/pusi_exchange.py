"""PUSI-GO, part D: which drinking-water standard binds, chloride or sodium, when sea water intrudes and when a recharge
well freshens an intruded aquifer (cation exchange, Gaines-Thomas, Fushe-Kuqe end-members).

A column of NC mixing cells (plug flow, one cell per step; numerical dispersivity = cell length / 2) with cation
exchange in local equilibrium, solved with the exchange routines of GJURMA-GO (../gjurma_go/gjurma_model.py:
selectivities K_Na\\K = 0.2, K_Na\\Ca = 0.4, K_Na\\Mg = 0.5, exchange capacity E in meq per litre of pore water).
End-members: fresh water of well 193 (sheet 5) and Adriatic sea water (standard sea water x 38.3/35 x 1.0285, as in
chloride_fk/python/fkcl_hydrochem.py).
  salinisation: the column holds fresh water in equilibrium with its exchanger; a mixture with sea-water fraction f0
                enters.  Reported: pore volumes (PV) until Cl > 250 mg/L and until Na > 200 mg/L at the outlet.
  freshening:   the column holds the mixture f0 in equilibrium with its exchanger (the state left by intrusion); the
                recharge water (well 193) enters.  Reported: PV until Cl < 250 and until Na < 200 for good, the
                largest Na, Ca+Mg and the sodium adsorption ratio SAR at the outlet.
Output res/exchange.json.   Run: python3 pusi_exchange.py   (about 1 minute)
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'gjurma_go'))
import gjurma_model as G  # noqa: E402

RES = os.path.join(HERE, 'res')
NC = 100                        # cells; 1 PV = NC steps
PV_MAX = 25.0
LIM_CL, LIM_NA = 250.0, 200.0   # mg/L (EU drinking-water indicator values)
FRESH = G.FRESH.copy()
SEA = G.SEA_MGL * 38.3 / 35.0 * 1.0285 / G.MW
LOGK = np.log(G.K_TRUE)


def equilibrate(c, E):
    """Exchanger fractions in equilibrium with solution c, and total cation equivalents T = z y + E beta."""
    beta = G.exchanger(c, LOGK)
    T = G.ZC * c[..., G.IC] + E * beta
    return beta, T


def run(c_init, c_in, E, pv_max=PV_MAX):
    c = np.broadcast_to(c_init, (NC, G.NS)).copy()
    _, T = equilibrate(c, E)                                         # totals per cell (meq/L)
    Earr = np.full(NC, E)
    nstep = int(pv_max * NC)
    out = np.empty((nstep, G.NS))
    for s in range(nstep):
        # advect the solution one cell; the exchanger stays
        anions = c[:, [G.I_CL, G.I_SO4, G.I_HCO3]]
        sol_cat = G.ZC * c[:, G.IC]                                  # solution cation equivalents
        ex = T - sol_cat                                             # exchanger equivalents (E beta)
        sol_cat = np.vstack([G.ZC * c_in[G.IC], sol_cat[:-1]])
        anions = np.vstack([c_in[[G.I_CL, G.I_SO4, G.I_HCO3]], anions[:-1]])
        T = sol_cat + ex
        y = G.solve_cations(T, Earr, LOGK, np.maximum(sol_cat / G.ZC, 1e-6), iters=12)
        c = np.zeros((NC, G.NS)); c[:, G.IC] = y
        c[:, [G.I_CL, G.I_SO4, G.I_HCO3]] = anions
        out[s] = c[-1]
    return out * G.MW                                               # mg/L at the outlet


def first_after(x, cond):
    """first PV after which cond holds for good (np.nan if never)."""
    bad = np.flatnonzero(~cond)
    if len(bad) == 0:
        return 0.0
    if bad[-1] == len(cond) - 1:
        return float('nan')
    return float((bad[-1] + 1) / NC)


def first(cond):
    i = np.flatnonzero(cond)
    return float(i[0] / NC) if len(i) else float('nan')


def sar(o):
    na = o[:, G.I_NA] / G.MW[G.I_NA]; ca = 2 * o[:, G.I_CA] / G.MW[G.I_CA]; mg = 2 * o[:, G.I_MG] / G.MW[G.I_MG]
    return na / np.sqrt(0.5 * (ca + mg))                            # meq/L form


def main():
    os.makedirs(RES, exist_ok=True)
    res = dict(sea_mgL=dict(zip(G.SPECIES, (SEA * G.MW).round(1).tolist())), fresh_mgL=dict(zip(G.SPECIES, (FRESH * G.MW).round(2).tolist())),
               f_cl_limit=float((LIM_CL - FRESH[G.I_CL] * G.MW[G.I_CL]) / ((SEA - FRESH)[G.I_CL] * G.MW[G.I_CL])),
               f_na_limit_mixing=float((LIM_NA - FRESH[G.I_NA] * G.MW[G.I_NA]) / ((SEA - FRESH)[G.I_NA] * G.MW[G.I_NA])),
               runs=[])
    for E in (30.0, 60.0, 120.0):
        for f0 in (0.02, 0.05, 0.10):
            mix = f0 * SEA + (1 - f0) * FRESH
            sal = run(FRESH, mix, E, pv_max=6.0)
            fr = run(mix, FRESH, E)
            r = dict(E=E, f0=f0,
                     sal_pv_cl=first(sal[:, G.I_CL] > LIM_CL), sal_pv_na=first(sal[:, G.I_NA] > LIM_NA),
                     sal_na_at_cl=float(np.interp(first(sal[:, G.I_CL] > LIM_CL) * NC, np.arange(len(sal)), sal[:, G.I_NA])) if np.isfinite(first(sal[:, G.I_CL] > LIM_CL)) else None,
                     fr_pv_cl=first_after(fr, fr[:, G.I_CL] < LIM_CL), fr_pv_na=first_after(fr, fr[:, G.I_NA] < LIM_NA),
                     fr_na_max=float(fr[:, G.I_NA].max()), fr_na_mix_max=float(mix[G.I_NA] * G.MW[G.I_NA]),
                     fr_hard_min_meq=float((2 * fr[:, G.I_CA] / G.MW[G.I_CA] + 2 * fr[:, G.I_MG] / G.MW[G.I_MG]).min()),
                     fr_sar_max=float(sar(fr).max()))
            r['lag_pv'] = r['fr_pv_na'] - r['fr_pv_cl'] if np.isfinite(r['fr_pv_na']) and np.isfinite(r['fr_pv_cl']) else None
            # the freshening tail after chloride is below the limit for good: softened Na-HCO3 water
            i0 = int(round(r['fr_pv_cl'] * NC))
            tail = fr[i0:]
            hard = 2 * tail[:, G.I_CA] / G.MW[G.I_CA] + 2 * tail[:, G.I_MG] / G.MW[G.I_MG]
            hard_f = 2 * FRESH[G.I_CA] + 2 * FRESH[G.I_MG]
            r.update(tail_na_max=float(tail[:, G.I_NA].max()), tail_sar_max=float(sar(tail).max()),
                     tail_hard_min_meq=float(hard.min()), hard_fresh_meq=float(hard_f),
                     tail_pv_soft=float(np.sum(hard < 0.5 * hard_f) / NC),
                     tail_pv_recover=first_after(hard, hard >= 0.9 * hard_f) + r['fr_pv_cl'],
                     tail_pv_sar3=float(np.sum(sar(tail) > 3.0) / NC))
            res['runs'].append(r)
            print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}))
            if E == 60.0 and f0 == 0.05:
                np.savez(os.path.join(RES, 'exchange_curves.npz'), sal=sal, fr=fr, nc=NC)
    json.dump(res, open(os.path.join(RES, 'exchange.json'), 'w'), indent=1)
    print('f at the Cl limit', res['f_cl_limit'], 'f at the Na limit by mixing', res['f_na_limit_mixing'])


if __name__ == '__main__':
    main()
