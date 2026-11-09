"""Surface deformation of a rectangular dislocation in an elastic half-space (Okada, 1985), vectorised with numpy.

okada85(e, n, depth, strike, dip, L, W, rake, slip, opening=0, nu=0.25) -> ue, un, uz
    e, n      observation points at the free surface, east and north of the fault centroid (m)
    depth     depth of the fault centroid (m, positive down)
    strike    clockwise from north (deg); the fault dips to the right of the strike direction
    dip       (deg); L along strike, W along dip (m)
    rake      direction of the hanging-wall motion from the strike (deg): 90 reverse, -90 normal, 0 left-lateral
    slip, opening (m)
surface_strain(...) -> exx, eyy, exy and the volumetric strain at the free surface,
    ev = (1 - 2 nu) / (1 - nu) * (exx + eyy), since sigma_zz = 0 there.

Written for TRONDITJA-GO from Okada (1985) in the form of the reference implementation okada85.m (Beauducel);
checked in okada_checks.py: the displacement jumps across surface ruptures equal the slip, the point-source limit,
the independence of Poisson's ratio in plane strain, the sense of motion and the finite-difference step."""
import numpy as np

EPS = 1e-12


def _I1(xi, eta, q, dip, nu, R):
    db = eta * np.sin(dip) - q * np.cos(dip)
    if np.cos(dip) > EPS:
        return (1 - 2 * nu) * (-xi / (np.cos(dip) * (R + db))) - np.sin(dip) / np.cos(dip) * _I5(xi, eta, q, dip, nu, R, db)
    return -(1 - 2 * nu) / 2 * xi * q / (R + db) ** 2


def _I2(eta, q, dip, nu, R):
    return (1 - 2 * nu) * (-np.log(R + eta)) - _I3(eta, q, dip, nu, R)


def _I3(eta, q, dip, nu, R):
    yb = eta * np.cos(dip) + q * np.sin(dip)
    db = eta * np.sin(dip) - q * np.cos(dip)
    if np.cos(dip) > EPS:
        return (1 - 2 * nu) * (yb / (np.cos(dip) * (R + db)) - np.log(R + eta)) + np.sin(dip) / np.cos(dip) * _I4(db, eta, q, dip, nu, R)
    return (1 - 2 * nu) / 2 * (eta / (R + db) + yb * q / (R + db) ** 2 - np.log(R + eta))


def _I4(db, eta, q, dip, nu, R):
    if np.cos(dip) > EPS:
        return (1 - 2 * nu) / np.cos(dip) * (np.log(R + db) - np.sin(dip) * np.log(R + eta))
    return -(1 - 2 * nu) * q / (R + db)


def _I5(xi, eta, q, dip, nu, R, db):
    X = np.sqrt(xi ** 2 + q ** 2)
    if np.cos(dip) > EPS:
        with np.errstate(divide='ignore', invalid='ignore'):
            out = (1 - 2 * nu) * 2 / np.cos(dip) * np.arctan(
                (eta * (X + q * np.cos(dip)) + X * (R + X) * np.sin(dip)) / (xi * (R + X) * np.cos(dip)))
        return np.where(np.abs(xi) < EPS, 0.0, out)
    return -(1 - 2 * nu) * xi * np.sin(dip) / (R + db)


def _atan_term(xi, eta, q, R):
    with np.errstate(divide='ignore', invalid='ignore'):
        a = np.arctan(xi * eta / (q * R))
    return np.where(np.abs(q) < EPS, 0.0, a)


# strike-slip, dip-slip and tensile parts (Okada 1985, Eqs. 25-30)
def _ux_ss(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    return xi * q / (R * (R + eta)) + _atan_term(xi, eta, q, R) + _I1(xi, eta, q, dip, nu, R) * np.sin(dip)


def _uy_ss(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    return ((eta * np.cos(dip) + q * np.sin(dip)) * q / (R * (R + eta)) + q * np.cos(dip) / (R + eta)
            + _I2(eta, q, dip, nu, R) * np.sin(dip))


def _uz_ss(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    db = eta * np.sin(dip) - q * np.cos(dip)
    return db * q / (R * (R + eta)) + q * np.sin(dip) / (R + eta) + _I4(db, eta, q, dip, nu, R) * np.sin(dip)


def _ux_ds(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    return q / R - _I3(eta, q, dip, nu, R) * np.sin(dip) * np.cos(dip)


def _uy_ds(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    return ((eta * np.cos(dip) + q * np.sin(dip)) * q / (R * (R + xi)) + np.cos(dip) * _atan_term(xi, eta, q, R)
            - _I1(xi, eta, q, dip, nu, R) * np.sin(dip) * np.cos(dip))


def _uz_ds(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    db = eta * np.sin(dip) - q * np.cos(dip)
    return (db * q / (R * (R + xi)) + np.sin(dip) * _atan_term(xi, eta, q, R)
            - _I5(xi, eta, q, dip, nu, R, db) * np.sin(dip) * np.cos(dip))


def _ux_tf(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    return q ** 2 / (R * (R + eta)) - _I3(eta, q, dip, nu, R) * np.sin(dip) ** 2


def _uy_tf(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    db = eta * np.sin(dip) - q * np.cos(dip)
    return (-db * q / (R * (R + xi)) - np.sin(dip) * (xi * q / (R * (R + eta)) - _atan_term(xi, eta, q, R))
            - _I1(xi, eta, q, dip, nu, R) * np.sin(dip) ** 2)


def _uz_tf(xi, eta, q, dip, nu):
    R = np.sqrt(xi ** 2 + eta ** 2 + q ** 2)
    db = eta * np.sin(dip) - q * np.cos(dip)
    yb = eta * np.cos(dip) + q * np.sin(dip)
    return (yb * q / (R * (R + xi)) + np.cos(dip) * (xi * q / (R * (R + eta)) - _atan_term(xi, eta, q, R))
            - _I5(xi, eta, q, dip, nu, R, db) * np.sin(dip) ** 2)


def _chinnery(f, x, p, L, W, q, dip, nu):
    return f(x, p, q, dip, nu) - f(x, p - W, q, dip, nu) - f(x - L, p, q, dip, nu) + f(x - L, p - W, q, dip, nu)


def okada85(e, n, depth, strike, dip, L, W, rake, slip, opening=0.0, nu=0.25):
    e, n = np.asarray(e, float), np.asarray(n, float)
    st, dp, rk = np.radians(strike), np.radians(dip), np.radians(rake)
    U1, U2, U3 = np.cos(rk) * slip, np.sin(rk) * slip, opening
    d = depth + np.sin(dp) * W / 2                       # depth of the bottom edge
    ec = e + np.cos(st) * np.cos(dp) * W / 2
    nc = n - np.sin(st) * np.cos(dp) * W / 2
    x = np.cos(st) * nc + np.sin(st) * ec + L / 2
    y = np.sin(st) * nc - np.cos(st) * ec + np.cos(dp) * W
    p = y * np.cos(dp) + d * np.sin(dp)
    q = y * np.sin(dp) - d * np.cos(dp)
    ux = (-U1 / (2 * np.pi) * _chinnery(_ux_ss, x, p, L, W, q, dp, nu)
          - U2 / (2 * np.pi) * _chinnery(_ux_ds, x, p, L, W, q, dp, nu)
          + U3 / (2 * np.pi) * _chinnery(_ux_tf, x, p, L, W, q, dp, nu))
    uy = (-U1 / (2 * np.pi) * _chinnery(_uy_ss, x, p, L, W, q, dp, nu)
          - U2 / (2 * np.pi) * _chinnery(_uy_ds, x, p, L, W, q, dp, nu)
          + U3 / (2 * np.pi) * _chinnery(_uy_tf, x, p, L, W, q, dp, nu))
    uz = (-U1 / (2 * np.pi) * _chinnery(_uz_ss, x, p, L, W, q, dp, nu)
          - U2 / (2 * np.pi) * _chinnery(_uz_ds, x, p, L, W, q, dp, nu)
          + U3 / (2 * np.pi) * _chinnery(_uz_tf, x, p, L, W, q, dp, nu))
    ue = np.sin(st) * ux - np.cos(st) * uy
    un = np.cos(st) * ux + np.sin(st) * uy
    return ue, un, uz


def surface_strain(e, n, *args, h=2.0, **kw):
    """Horizontal strains by fourth-order central differences and the volumetric strain at the free surface."""
    def u(de, dn):
        ue, un, _ = okada85(np.asarray(e) + de, np.asarray(n) + dn, *args, **kw)
        return ue, un
    d1 = lambda f: (-f(2 * h) + 8 * f(h) - 8 * f(-h) + f(-2 * h)) / (12 * h)
    exx = d1(lambda s: u(s, 0)[0])
    eyy = d1(lambda s: u(0, s)[1])
    exy = 0.5 * (d1(lambda s: u(0, s)[0]) + d1(lambda s: u(s, 0)[1]))
    nu = kw.get('nu', 0.25)
    ev = (1 - 2 * nu) / (1 - nu) * (exx + eyy)
    return exx, eyy, exy, ev
