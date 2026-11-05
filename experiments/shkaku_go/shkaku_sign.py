"""SHKAKU-GO, side checks on the twins alone (no data needed): for a 40% drought, the share of weeks in which the
drought RAISES the recharge or the head at the pumping well, for the coupling rho of the recharge error across
worlds (Proposition K3); the mean effects; and, for the late season (rain 30 days later), the share of weeks with a
positive effect (the effect changes sign within the year).
usage: python shkaku_sign.py   (writes res/shkaku_sign.json)"""
import json
import os

import numpy as np

import shkaku_exp as S

out = dict(drought={}, late={})
bed = S.Bed()
rng = np.random.default_rng(2209)
cases = [bed.case(rng, 'none') for _ in range(2000)]
for rho in (1.0, 0.9, 0.6, 0.0):
    tw = [bed.twin(cs, 'drought', rho) for cs in cases]
    out['drought'][str(rho)] = {f'up_{k}': float(np.mean([np.mean(t[k] > 0) for t in tw])) for k in ('dr', 'dh')}
    print('drought', rho, out['drought'][str(rho)])
tw = [bed.twin(cs, 'drought', 1.0) for cs in cases]
out['drought']['mean_dr'] = float(np.mean([t['dr'].mean() for t in tw]))
out['drought']['mean_dh'] = float(np.mean([t['dh'].mean() for t in tw]))
out['drought']['mean_r'] = float(np.mean([cs['r'].mean() for cs in cases]))
out['drought']['mean_h'] = float(np.mean([cs['h'][S.IW].mean() for cs in cases]))
tw = [bed.twin(cs, 'late', 1.0) for cs in cases]
out['late']['up_dr'] = float(np.mean([np.mean(t['dr'] > 0) for t in tw]))
out['late']['up_dh'] = float(np.mean([np.mean(t['dh'] > 0) for t in tw]))
out['late']['mean_abs_dh'] = float(np.mean([np.abs(t['dh']).mean() for t in tw]))
print(out)
with open(os.path.join(S.RES, 'shkaku_sign.json'), 'w') as fh:
    json.dump(out, fh, indent=1)
