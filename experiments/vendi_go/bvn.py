"""Vectorized bivariate normal upper probability P(X > h, Y > k), corr(X, Y) = r.

numpy port of A. Genz's bvnu (Drezner-Wesolowsky with Gauss-Legendre quadrature; Genz 2004,
Statistics and Computing 14, 251-260). Accurate to about 1e-15 for all r in (-1, 1).
"""
import numpy as np
from scipy.special import ndtr

_W = np.array([.01761400713915212, .04060142980038694, .06267204833410906, .08327674157670475,
               0.1019301198172404, 0.1181945319615184, 0.1316886384491766, 0.1420961093183821,
               0.1491729864726037, 0.1527533871307259])
_X = np.array([0.9931285991850949, 0.9639719272779138, 0.9122344282513259, 0.8391169718222188,
               0.7463319064601508, 0.6360536807265150, 0.5108670019508271, 0.3737060887154196,
               0.2277858511416451, 0.07652652113349733])
W20 = np.r_[_W, _W]
X20 = np.r_[1 - _X, 1 + _X]
TP = 2 * np.pi


def bvnu(dh, dk, r):
    dh, dk, r = np.broadcast_arrays(np.asarray(dh, float), np.asarray(dk, float), np.asarray(r, float))
    shape = dh.shape
    h, k, r = dh.ravel().copy(), dk.ravel().copy(), r.ravel().copy()
    out = np.empty_like(h)
    lo = np.abs(r) < 0.925
    if lo.any():                                   # |r| < 0.925: integrate over asin(r)
        hh, kk, rr = h[lo], k[lo], r[lo]
        hk = hh * kk; hs = (hh * hh + kk * kk) / 2; asr = np.arcsin(rr) / 2
        sn = np.sin(asr[:, None] * X20[None, :])
        bvn = (np.exp((sn * hk[:, None] - hs[:, None]) / (1 - sn ** 2)) * W20).sum(1)
        out[lo] = bvn * asr / TP + ndtr(-hh) * ndtr(-kk)
    hi = ~lo
    if hi.any():
        hh, kk, rr = h[hi], k[hi].copy(), r[hi]
        neg = rr < 0
        kk[neg] = -kk[neg]
        hk = hh * kk
        bvn = np.zeros_like(hh)
        one = np.abs(rr) < 1
        if one.any():
            H, K, HK, RR = hh[one], kk[one], hk[one], rr[one]
            As = (1 - RR) * (1 + RR); a = np.sqrt(As); bs = (H - K) ** 2
            asr = -(bs / As + HK) / 2; c = (4 - HK) / 8; d = (12 - HK) / 80
            b1 = np.where(asr > -100, a * np.exp(np.maximum(asr, -100)) * (1 - c * (bs - As) * (1 - d * bs) / 3 + c * d * As ** 2), 0.0)
            b = np.sqrt(bs); sp_ = np.sqrt(TP) * ndtr(-b / a)
            b1 = np.where(HK > -100, b1 - np.exp(-np.maximum(HK, -200) / 2) * sp_ * b * (1 - c * bs * (1 - d * bs) / 3), b1)
            a2 = a / 2
            xs = (a2[:, None] * X20[None, :]) ** 2
            asr2 = -(bs[:, None] / xs + HK[:, None]) / 2
            ok = asr2 > -100
            sp2 = 1 + c[:, None] * xs * (1 + 5 * d[:, None] * xs)
            rs = np.sqrt(1 - xs)
            ep = np.exp(-(HK[:, None] / 2) * xs / (1 + rs) ** 2) / rs
            term = np.where(ok, np.exp(np.maximum(asr2, -100)) * (sp2 - ep), 0.0) @ W20
            bvn[one] = (a2 * term - b1) / TP
        pos = rr > 0
        res = np.empty_like(hh)
        res[pos] = bvn[pos] + ndtr(-np.maximum(hh[pos], kk[pos]))
        n_ = ~pos
        if n_.any():
            H, K, B = hh[n_], kk[n_], bvn[n_]
            L = np.where(H < 0, ndtr(K) - ndtr(H), ndtr(-H) - ndtr(-K))
            res[n_] = np.where(H >= K, -B, L - B)
        out[hi] = res
    return np.clip(out, 0.0, 1.0).reshape(shape)


if __name__ == '__main__':
    from scipy.stats import multivariate_normal as mvn
    rng = np.random.default_rng(1)
    worst = 0.0
    for r in [-0.99, -0.95, -0.9, -0.5, -0.1, 0.0, 0.2, 0.6, 0.8, 0.9, 0.93, 0.95, 0.99, 0.999]:
        h = rng.normal(0, 1.5, 40); k = rng.normal(0, 1.5, 40)
        p = bvnu(h, k, np.full(40, r))
        ref = np.array([mvn(mean=[0, 0], cov=[[1, r], [r, 1]]).cdf([-a, -b]) for a, b in zip(h, k)])
        worst = max(worst, np.abs(p - ref).max())
    print(f'max abs error against scipy over 560 points: {worst:.2e}')
