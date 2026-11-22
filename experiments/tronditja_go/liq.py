"""Liquefaction triggering from CPT (Boulanger and Idriss, 2014) and the liquefaction potential index, with the pore
pressure at the moment of the earthquake as an input, so that the water table and the coseismic step enter directly.

Profile arrays are given at cell centres z (m, positive down) with thickness dz:
    qc1ncs   clean-sand normalised tip resistance, a density index normalised with the effective stress at the time
             of the CPT (it does not change when the water table moves later)
    liq      True where the soil is liquefiable (sand, silty sand; I_c below 2.6); False for clays and silts
    gamma    total unit weight (kN/m3)
Units: kPa, m, kN/m3; a_max in g.

Equations (numbers of the TERMETET note): (4.2)-(4.8); the earthquake-time pore pressure
    u(z) = gamma_w (z - z_w)_+ + dp(z)                      (corrected 4.1-4.2: the coseismic step enters u, not z_w)
the static step in a layer under the free surface, dp0 = -kappa (de_xx + de_yy) with kappa = (2GB/3)(1+nu_u)/(1-nu_u)
(areal_kappa), and the closed-form sensitivity of the factor of safety to the depth of the water table
    d ln FS / d z_w = (gamma_w / sigma'_v) (1 - C_sigma / K_sigma)  (below the water table; where K_sigma is at its
    cap of 1.1 the second term vanishes)."""
import numpy as np

PA = 101.325            # atmospheric pressure, kPa
GW = 9.81               # unit weight of water, kN/m3


def rd(z, M):
    a = -1.012 - 1.126 * np.sin(z / 11.73 + 5.133)
    b = 0.106 + 0.118 * np.sin(z / 11.28 + 5.142)
    return np.exp(a + b * M)


def crr75(q):
    q = np.clip(q, 21.0, 211.0)
    return np.exp(q / 113 + (q / 1000) ** 2 - (q / 140) ** 3 + (q / 137) ** 4 - 2.80)


def msf(q, M):
    msfmax = np.minimum(1.09 + (np.clip(q, 21, 211) / 180) ** 3, 2.2)
    return 1 + (msfmax - 1) * (8.64 * np.exp(-M / 4) - 1.325)


def c_sigma(q):
    return np.minimum(1.0 / (37.3 - 8.27 * np.clip(q, 21, 211) ** 0.264), 0.3)


def k_sigma(q, svp):
    return np.minimum(1 - c_sigma(q) * np.log(svp / PA), 1.1)


def stresses(z, dz, gamma, zw, dp=0.0):
    gamma = np.broadcast_to(gamma, np.broadcast_shapes(np.shape(gamma), np.shape(z)))
    sv = np.cumsum(gamma * dz, axis=-1) - gamma * dz / 2
    u = GW * np.clip(z - zw, 0, None) + np.where(z > zw, dp, 0.0)
    return sv, u, sv - u


def fs_profile(z, dz, qc1ncs, liq, gamma, zw, amax, M, dp=0.0):
    """Factor of safety; np.inf where the soil cannot liquefy (non-liquefiable or above the water table)."""
    sv, u, svp = stresses(z, dz, gamma, zw, dp)
    svp = np.maximum(svp, 1.0)
    csr = 0.65 * sv / svp * amax * rd(z, M)
    crr = crr75(qc1ncs) * msf(qc1ncs, M) * k_sigma(qc1ncs, svp)
    fs = np.where(liq & (z > zw), crr / csr, np.inf)
    return fs, csr, crr, svp


def lpi(z, dz, fs):
    F = np.where(fs <= 1.0, 1.0 - fs, 0.0)
    w = np.where(z <= 20.0, 10.0 - 0.5 * z, 0.0)
    return np.sum(F * w * dz, axis=-1)


def lpi_profile(z, dz, qc1ncs, liq, gamma, zw, amax, M, dp=0.0):
    fs, *_ = fs_profile(z, dz, qc1ncs, liq, gamma, zw, amax, M, dp)
    return lpi(z, dz, fs)


def dlnfs_dzw(z, dz, qc1ncs, gamma, zw, amax, M):
    """Closed form of d ln FS / d z_w below the water table (uniform unit weight, K_sigma below 1.1)."""
    _, _, svp = stresses(z, dz, gamma, zw)
    ks_raw = 1 - c_sigma(qc1ncs) * np.log(svp / PA)
    capped = ks_raw >= 1.1                     # where K_sigma sits on its cap it does not change with z_w
    return GW / svp * (1 - np.where(capped, 0.0, c_sigma(qc1ncs) / np.minimum(ks_raw, 1.1)))


def cn_renormalise(q0, svp0, svp1, iters=30):
    """What one would get by wrongly re-normalising a clean-sand q_c1Ncs measured at sigma'_v0 with the effective stress
    sigma'_v1 of the earthquake (C_N = (Pa/sigma'_v)^m <= 1.7, m = 1.338 - 0.249 q^0.264). Used only to show the error."""
    def cn(sv, q):
        m = 1.338 - 0.249 * np.clip(q, 21, 254) ** 0.264
        return np.minimum((PA / np.maximum(sv, 1.0)) ** m, 1.7)
    qc_pa = q0 / cn(svp0, q0)
    q1 = np.array(q0, float)
    for _ in range(iters):
        q1 = cn(svp1, q1) * qc_pa
    return q1


def areal_kappa(G, B, nu_u):
    """Pore-pressure change per unit areal strain of an undrained layer under a free surface (sigma_zz = 0):
    dp = -kappa (de_xx + de_yy), kappa = (2 G B / 3) (1 + nu_u) / (1 - nu_u). From (1.1)-(1.2) with zeta = 0: the
    layer takes the horizontal strain of the crust below it, and its vertical strain adjusts so that sigma_zz = 0.
    A soft, nearly incompressible layer (nu_u near 1/2) then deforms at almost constant volume, and kappa scales with
    its shear modulus G, not with the stiffness of its pore water."""
    return 2.0 * G * B / 3.0 * (1.0 + nu_u) / (1.0 - nu_u)


def drainage_factor(z, liq, zw, D=1.0, t=15.0):
    """Share of the coseismic step left after the shaking: erf(L / (2 sqrt(D t))) for sand connected to the water table
    through sand only (L its depth below the water table, D in m2/s, t in s); 1 below a clay layer (undrained)."""
    from scipy.special import erf
    zw = np.asarray(zw, float)[..., None] if np.ndim(zw) else zw
    below = z > zw
    clay_below = (~liq) & below
    sealed = np.cumsum(clay_below, axis=-1) > 0
    L = np.clip(z - zw, 0, None)
    f = np.where(sealed, 1.0, erf(L / (2 * np.sqrt(D * t))))
    return np.where(below, f, 0.0)
