"""Checks of okada85.py that do not depend on the implementation itself.
usage: python okada_checks.py -> res/okada_checks.json

C1  the displacement jumps across a fault that reaches the surface equal the slip vector (strike-slip and dip-slip)
C2  far from a small fault the result equals Okada's (1985) point-source formulas times the fault area
C3  for a very long fault (plane strain) the surface displacement does not depend on Poisson's ratio
C4  sense of motion: reverse slip lifts the hanging wall, normal slip lowers it, left-lateral slip moves the far side left
C5  the free-surface strain by finite differences does not change with the step (2 m against 1 m and 4 m)"""
import json
import os

import numpy as np

from okada85 import okada85, surface_strain

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = {}

# C1: faults reaching the surface (top edge at z = 0): centroid depth = sin(dip) W / 2
L, W = 20e3, 10e3
jumps = {}
for name, dip, rake in (('strike-slip, dip 89.9', 89.9, 0.0), ('reverse, dip 45', 45.0, 90.0)):
    st = 0.0                                                    # strike north: the fault dips to the east
    dp = np.radians(dip)
    depth = np.sin(dp) * W / 2
    e_trace = -np.cos(dp) * W / 2                               # trace (top edge) east of the centroid
    eps = 0.5
    ue1, un1, uz1 = okada85(e_trace - eps, 0.0, depth, st, dip, L, W, rake, 1.0)    # footwall side (west)
    ue2, un2, uz2 = okada85(e_trace + eps, 0.0, depth, st, dip, L, W, rake, 1.0)    # hanging-wall side (east)
    jump = np.array([ue2 - ue1, un2 - un1, uz2 - uz1]).ravel()
    # hanging wall relative to footwall: strike-slip rake 0 (left-lateral): +1 m along strike (north);
    # reverse dip 45: the hanging wall moves up-dip, i.e. west (-cos dip) and up (+sin dip)
    expect = np.array([0.0, 1.0, 0.0]) if rake == 0.0 else np.array([-np.cos(dp), 0.0, np.sin(dp)])
    jumps[name] = dict(jump=jump.round(5).tolist(), expected=expect.round(5).tolist(),
                       max_abs_err=float(np.max(np.abs(jump - expect))))
OUT['C1_jump_equals_slip'] = jumps


# C2: point source (Okada 1985, the formulas for a point source) against a 200 m x 200 m fault at 5 km depth
def point_source(x, y, d, dip, U1, U2, area, nu=0.25):
    dp = np.radians(dip)
    a = 1 - 2 * nu                                              # mu / (lambda + mu)
    p = y * np.cos(dp) + d * np.sin(dp)
    q = y * np.sin(dp) - d * np.cos(dp)
    R = np.sqrt(x ** 2 + y ** 2 + d ** 2)
    I1 = a * y * (1 / (R * (R + d) ** 2) - x ** 2 * (3 * R + d) / (R ** 3 * (R + d) ** 3))
    I2 = a * x * (1 / (R * (R + d) ** 2) - y ** 2 * (3 * R + d) / (R ** 3 * (R + d) ** 3))
    I3 = a * x / R ** 3 - I2
    I4 = a * (-x * y * (2 * R + d) / (R ** 3 * (R + d) ** 2))
    I5 = a * (1 / (R * (R + d)) - x ** 2 * (2 * R + d) / (R ** 3 * (R + d) ** 2))
    ux = -U1 / (2 * np.pi) * (3 * x ** 2 * q / R ** 5 + I1 * np.sin(dp)) \
        - U2 / (2 * np.pi) * (3 * x * p * q / R ** 5 - I3 * np.sin(dp) * np.cos(dp))
    uy = -U1 / (2 * np.pi) * (3 * x * y * q / R ** 5 + I2 * np.sin(dp)) \
        - U2 / (2 * np.pi) * (3 * y * p * q / R ** 5 - I1 * np.sin(dp) * np.cos(dp))
    uz = -U1 / (2 * np.pi) * (3 * x * d * q / R ** 5 + I4 * np.sin(dp)) \
        - U2 / (2 * np.pi) * (3 * d * p * q / R ** 5 - I5 * np.sin(dp) * np.cos(dp))
    return ux * area, uy * area, uz * area


rng = np.random.default_rng(7)
pts = rng.uniform(-12e3, 12e3, size=(40, 2))
c2 = {}
for dip, rake in ((30.0, 90.0), (60.0, 0.0), (75.0, 45.0)):
    a_ = 200.0
    ue, un, uz = okada85(pts[:, 0], pts[:, 1], 5e3, 0.0, dip, a_, a_, rake, 1.0)
    # strike north: x (along strike) = north, y (left of strike) = west
    ux, uy, uzp = point_source(pts[:, 1], -pts[:, 0], 5e3, dip, np.cos(np.radians(rake)), np.sin(np.radians(rake)),
                               a_ * a_)
    fin = np.concatenate([un, -ue, uz]); pnt = np.concatenate([ux, uy, uzp])
    c2[f'dip {dip:g}, rake {rake:g}'] = float(np.max(np.abs(fin - pnt)) / np.max(np.abs(pnt)))
OUT['C2_point_source_rel_err'] = c2

# C3: plane strain (L = 2000 km): surface displacements independent of nu
e = np.linspace(-30e3, 30e3, 61)
u25 = okada85(e, 0.0, 12e3, 0.0, 35.0, 2000e3, 15e3, 90.0, 1.0, nu=0.25)
u40 = okada85(e, 0.0, 12e3, 0.0, 35.0, 2000e3, 15e3, 90.0, 1.0, nu=0.40)
u10 = okada85(e, 0.0, 12e3, 0.0, 35.0, 20e3, 15e3, 90.0, 1.0, nu=0.25)
u10b = okada85(e, 0.0, 12e3, 0.0, 35.0, 20e3, 15e3, 90.0, 1.0, nu=0.40)
scale = max(np.max(np.abs(u25[0])), np.max(np.abs(u25[2])))
OUT['C3_plane_strain'] = dict(
    long_fault_max_change_nu_025_to_040=float(max(np.max(np.abs(u25[i] - u40[i])) for i in (0, 2)) / scale),
    short_fault_max_change_nu_025_to_040=float(max(np.max(np.abs(u10[i] - u10b[i])) for i in (0, 2))
                                               / max(np.max(np.abs(u10[0])), np.max(np.abs(u10[2])))))

# C4: sense of motion above a fault dipping east (strike north), top edge at 2 km depth
dip, W4 = 40.0, 10e3
depth4 = 2e3 + np.sin(np.radians(dip)) * W4 / 2
e_hw = 2e3                                                      # east of the centroid: above the hanging wall
uz_rev = okada85(e_hw, 0.0, depth4, 0.0, dip, 20e3, W4, 90.0, 1.0)[2]
uz_nor = okada85(e_hw, 0.0, depth4, 0.0, dip, 20e3, W4, -90.0, 1.0)[2]
un_ll_e = okada85(15e3, 0.0, depth4, 0.0, 89.9, 20e3, W4, 0.0, 1.0)[1]   # east side of a left-lateral fault
un_ll_w = okada85(-15e3, 0.0, depth4, 0.0, 89.9, 20e3, W4, 0.0, 1.0)[1]
OUT['C4_sense'] = dict(reverse_uz_over_hanging_wall=float(uz_rev), normal_uz_over_hanging_wall=float(uz_nor),
                       left_lateral_un_east_side=float(un_ll_e), left_lateral_un_west_side=float(un_ll_w),
                       passed=bool(uz_rev > 0 and uz_nor < 0 and un_ll_e > 0 and un_ll_w < 0))

# C5: the finite-difference step of the surface strain
args = (16.5e3, 340.0, 23.0, 22e3, 13e3, 90.0, 0.55)
pe = rng.uniform(-25e3, 25e3, 200); pn = rng.uniform(-25e3, 25e3, 200)
ev = {h: surface_strain(pe, pn, *args, h=h)[3] for h in (1.0, 2.0, 4.0)}
OUT['C5_strain_step_rel_change'] = {f'h {h:g} m vs 2 m': float(np.max(np.abs(ev[h] - ev[2.0])) / np.max(np.abs(ev[2.0])))
                                    for h in (1.0, 4.0)}

os.makedirs(os.path.join(HERE, 'res'), exist_ok=True)
with open(os.path.join(HERE, 'res', 'okada_checks.json'), 'w') as fh:
    json.dump(OUT, fh, indent=1)
print(json.dumps(OUT, indent=1))
