"""Translate the lens leak of LIDHJA-GO into the 2045 chloride goal of RITMI-GO and summarise (lidhja_summary.json).
The relative change of the chloride taken up by a clay lens is read as a relative error of the clay capacity b2 that
chloride sees; the goal shift is then (dg/dlog b2) times that change (linear, approximate)."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ritmi_go'))
import ritmi_core as C   # noqa: E402
import ritmi_model as R  # noqa: E402
import lidhja as L       # noqa: E402

res = json.load(open(os.path.join(HERE, 'lidhja_results.json')))
cut = json.load(open(os.path.join(HERE, '..', 'synthesis', 'synth_cut.json')))
U = C.fd_ensemble(0.05)
ref = R.simulate(C.to_P(U), {'kind': 'const'})
G = C.jac(C.goals(ref), 0.05)[:3]
dg_dlogb2 = float(G[0, 6] / C.S0[6])                          # mg/L per unit of log b2 (Cl at 5 km, 2045)
sd_joint, sd_cut = cut['goal_sd']['joint'][0], cut['goal_sd']['cut'][0]
out = dict(dg_dlogb2=dg_dlogb2, sd_joint=sd_joint, sd_cut=sd_cut, worst_joint=cut['shift_worst_rms1']['joint'][0])
sal = 'salinisation (fresh -> 5 % sea water)'
out['lens'] = {}
for err, r in res['L'][sal].items():
    t = np.array(r['np']['t'])
    rho = np.array(r['np']['rel_uptake'])
    i50, i100 = int(np.argmin(abs(t - 50))), len(t) - 1
    out['lens'][err] = dict(rho50=float(rho[i50]), rho100=float(rho[i100]),
                            dg50=abs(dg_dlogb2 * rho[i50]), dg100=abs(dg_dlogb2 * rho[i100]),
                            max_dcl_mgL=r['np']['max_abs_u'] * 35.453,
                            leak=r['np']['sup_u'], bound=r['np']['bound_t'])
fre = 'freshening (5 % sea water -> fresh)'
out['fresh_max_rel'] = max(abs(np.array(r['np']['rel_uptake'])).max() for r in res['L'][fre].values())
# flow regime: exponent of the leak against 1 + Pe and bound/leak ratios
pe = np.array(sorted(float(p) for p in res['P']))
leak = np.array([res['P'][str(p)]['np']['sup_u'] for p in pe])
bnd = np.array([res['P'][str(p)]['np']['bound_t'] for p in pe])
sl = np.polyfit(np.log(1 + pe[2:]), np.log(leak[2:]), 1)[0]
out['P'] = dict(slope=float(sl), ratio=(bnd / leak).tolist(), pe=pe.tolist(), leak=leak.tolist())
Dcl = 0.5 * L.D_FREE[0]
out['pe_fk'] = 150.0 * 50.0 / Dcl                               # alpha_L |v| / D_Cl in the mobile zone
out['suppression_fk'] = 1.0 / (1.0 + out['pe_fk'])
out['contrast'] = dict(D_free=L.D_FREE.tolist(), dmax=float(np.abs(L.D_FREE[1:] - L.D_FREE[0]).max()),
                       dmin=float(L.D_FREE.min()), dcl=float(L.D_FREE[0]))
json.dump(out, open(os.path.join(HERE, 'lidhja_summary.json'), 'w'), indent=1)
print(json.dumps(out, indent=1)[:2500])
