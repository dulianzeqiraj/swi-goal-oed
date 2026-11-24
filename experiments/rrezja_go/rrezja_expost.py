"""RREZJA-GO, ex-post check: after the chloride sample, how often would some belief within the radius rho_env judge
the review-57 (VENDIMI-GO) choice unsafe, and the radius-rule choice? Same truths, sample and grid as rrezja.py.
Output res/expost.json.   Run: python3 rrezja_expost.py   (about 2 minutes)"""
import os, json, time
import numpy as np
import rrezja as RZ

VG, PA = RZ.VG, RZ.PA


def main():
    t0 = time.time()
    D, V, wD, wV = PA.D, PA.V, PA.wD, PA.wV
    NY, SG, QG, ns, nq = RZ.NY, RZ.SG, RZ.QG, RZ.ns, RZ.nq
    rng = np.random.default_rng(57)
    tru = V[rng.choice(len(V), NY, p=wV)]
    FD = np.stack([np.stack([VG.fail(D, s, q) for s in SG], 1) for q in QG], 2)
    noise = rng.standard_normal((NY, 4))
    dM, BM = PA.geom(PA.cM)
    phM = PA.phi0[:, PA.iM] - VG.QA * PA.uA[:, PA.iM] - VG.QB * PA.uB[:, PA.iM]
    clM = np.log10(PA.chloride(phM, dM, BM, 'sh'))
    j = [str(x) for x in PA.Z['mon_ids']].index('A30')
    ycl = clM[tru, j] + 0.1 * noise[:, 0]
    L_cl = -0.5 * ((ycl[:, None] - clM[D, j][None, :]) / 0.1) ** 2
    logw = np.log(np.maximum(wD, 1e-300))
    Zd = RZ.Z8[D]; mu = wD @ Zd; S = (Zd - mu).T @ ((Zd - mu) * wD[:, None]); Si = np.linalg.inv(S)
    LAM8 = np.zeros((RZ.K, 8)); LAM8[:, :2] = VG.LAM
    rho = float(RZ.kl_prior(LAM8, Zd, logw)[0][4])
    out = dict(rho_env=rho)
    for dn, LL in (('none', np.zeros((1, len(D)))), ('chloride sample (A30)', L_cl)):
        WK = np.stack([VG.tilt(D, wD, VG.LAM[k]) for k in range(RZ.K)])
        FF = FD.reshape(len(D), -1).astype(float)
        UK = None
        for k in range(RZ.K):
            E_ = RZ.softmax_rows(LL + np.log(np.maximum(WK[k], 1e-300))[None, :])
            P_ = E_ @ FF; E2 = E_ ** 2
            v_ = (E2 @ FF) * (1 - 2 * P_) + P_ ** 2 * E2.sum(1, keepdims=True)
            U = (P_ + RZ.ZM * np.sqrt(np.maximum(v_, 0))).reshape(-1, ns, nq)
            UK = U if UK is None else np.maximum(UK, U)
        cap = np.cumprod(UK <= RZ.ALPHA + 1e-12, axis=1).sum(1) - 1
        nT = cap.shape[0]
        sU = np.where(cap >= 0, SG[np.maximum(cap, 0)], 0.0)
        net = np.where(cap >= 0, sU * RZ.QSUM - RZ.C_R * 3 * QG[None, :], -np.inf)
        feas = np.isfinite(net).any(1)
        iq = np.where(feas, np.argmax(net, 1), nq - 1)
        idx = np.where(feas, np.maximum(cap[np.arange(nT), iq], 0), 0)
        Fm = FD[np.arange(len(D))[None, :], idx[:, None], iq[:, None]].astype(float) if nT > 1 else FD[:, idx[0], iq[0]][None, :].astype(float)
        P, se, lam, first = RZ.worst_case(LL + logw[None, :], Fm, rho, Zd, S, Si, logw)
        P0 = np.sum(RZ.softmax_rows(LL + logw[None, :]) * Fm, 1)
        out[dn] = dict(worst_median=float(np.median(P)), worst_q90=float(np.quantile(P, 0.9)),
                       share_worst_above_alpha=float(np.mean(P > RZ.ALPHA)), share_worst_plus_margin_above_alpha=float(np.mean(P + RZ.ZM * se > RZ.ALPHA)),
                       calibrated_median=float(np.median(P0)))
        print(dn, out[dn], f'{time.time() - t0:.0f}s', flush=True)
    json.dump(out, open(os.path.join(RZ.RES, 'expost.json'), 'w'), indent=1)
    print('wrote res/expost.json')


if __name__ == '__main__':
    main()
