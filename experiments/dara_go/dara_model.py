"""DARA-GO test model: a confined coastal aquifer cross-section with three conductivity zones.

Coast at x = 0 (freshwater head 0), inland boundary at x = L (head HL). Steady Darcy flow gives the head
    h(x) = HL * R(x) / R(L),   R(x) = sum_i overlap([0, x], zone i) / K_i,
which depends only on conductivity ratios. The seaward freshwater discharge per metre of coast is
q = HL * B / R(L), and the toe of the saltwater wedge follows Glover (1959):
    x_toe = K1 * DELTA * D**2 / (2 q) - q / (2 K1 DELTA),
with K1 the coastal-zone conductivity, DELTA = (rho_s - rho_f) / rho_f and D the depth of the aquifer base.

Unknowns: z = (z1, z2, z3) ~ N(0, I), ln K_i = ln K0 + SK z_i.  Design: the position xi of one observation
well.  Data: y = h(xi; z) + eps, eps ~ N(0, SIG^2).  Goal: the log toe position at resolution TAU,
q_tau = ln x_toe(z) + eta, eta ~ N(0, TAU^2).
"""
import numpy as np

L = 5000.0                                   # m, coast to inland boundary
EDGES = np.array([0.0, 1000.0, 2500.0, 5000.0])
LZ = np.diff(EDGES)                          # zone lengths
B = 30.0                                     # m, aquifer thickness
D = 30.0                                     # m, depth of the aquifer base below sea level
DELTA = 0.025                                # density contrast (rho_s - rho_f) / rho_f
HL = 5.0                                     # m, inland head
K0, SK = 20.0, 0.5                           # m/day, median conductivity and log-sd
SIG = 0.10                                   # m, head error
TAU = 0.08                                   # goal resolution (log units)


def invK(z):
    return np.exp(-SK * np.asarray(z)) / K0


def head(xi, z1, z2, z3):
    """Head at xi for (broadcastable) z1, z2, z3."""
    xi = np.asarray(xi, float)
    k1, k2, k3 = invK(z1), invK(z2), invK(z3)
    o1 = np.clip(xi - EDGES[0], 0.0, LZ[0]); o2 = np.clip(xi - EDGES[1], 0.0, LZ[1]); o3 = np.clip(xi - EDGES[2], 0.0, LZ[2])
    return HL * (o1 * k1 + o2 * k2 + o3 * k3) / (LZ[0] * k1 + LZ[1] * k2 + LZ[2] * k3)


def toe(z1, z2, z3):
    k1, k2, k3 = invK(z1), invK(z2), invK(z3)
    S = LZ[0] * k1 + LZ[1] * k2 + LZ[2] * k3          # integral of 1/K
    q = HL * B / S
    K1 = 1.0 / k1
    return K1 * DELTA * D ** 2 / (2.0 * q) - q / (2.0 * K1 * DELTA)


def goal(z1, z2, z3):
    return np.log(toe(z1, z2, z3))


def prior_samples(n, rng):
    return rng.standard_normal((n, 3))
