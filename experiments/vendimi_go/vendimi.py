"""VENDIMI-GO (vendimi: the decision): how the Fushe-Kuqe stakeholders reach a decisive joint choice under deep
uncertainty. Innovation of literature review 57 (decisive stakeholder decisions under stochastic and deep
uncertainty; Oxford, Caltech, MIT, ETH Zurich, 2020-2026).

Setting: the calibrated chloride ensemble of PUSI-GO (../pusi_go: Strack potential with a dispersive mixing zone,
20 000 weighted draws; even draws = inner set D, odd draws = truths V). Supply wells A1 and P10 with 20-m screens at
the top of the aquifer; failure = screen chloride above 250 mg/L at either well. Decisions: the pumping scale s
(units of the PUSI-GO rates Q0 = (366, 11 694) m3/d), the recharge rate q per site at the three PUSI-GO recharge
sites, and whether to buy information first (one shallow chloride sample at A30, or the three PRAG-GO heads).

Deep uncertainty: each stakeholder's belief is an exponential tilt of the calibrated posterior along the two disputed
drivers, z1 = standardised log mixing width (wider = salt nearer the screen) and z2 = standardised log recharge:
    p_k(theta) proportional to p(theta) exp(lambda_k . z(theta)).
Group rule (unanimous safety): pump the largest s such that EVERY stakeholder's own posterior probability of failure
is at most ALPHA = 0.10. Compared with the linear-pool rule (average of the stakeholders' probabilities).

Propositions checked here (section 9 of the review):
  V1  disagreement bound: |P_k(F|y) - P_j(F|y)| <= 1/2 max_t sd_{lambda(t)}((lambda_k - lambda_j) . z | y)
  V2  decisiveness: failure is monotone in s and q, so the admissible set is an interval [0, s*] with
      s* = min_k s*_k: one action that no stakeholder can veto and none can improve on
  V3  safe information: under the rule every stakeholder's own ex-ante risk stays <= ALPHA with or without data
Output res/vendimi.json.   Run: python3 vendimi.py   (about 3 minutes)
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pusi_go'))
import pusi_analysis as PA  # noqa: E402  (loads the ensemble of ../pusi_go/res/ens.npz)

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
SCREEN = 20.0
NY = 2000
SG = np.round(np.linspace(0.0, 3.0, 61), 3)                       # pumping scales
QG = np.array([0.0, 2500.0, 5000.0, 10000.0])                    # recharge per site (m3/d)
C_R = 0.5                                                         # price of recharged water relative to delivered water
ZM = 1.645                                                        # certified margin: one-sided 95% on the Monte Carlo error
STAKE = [  # name, lambda on (z_width, z_recharge)
    ('Water utility (calibrated belief)', 0.0, 0.0),
    ('Irrigators and hotels (optimists)', -0.75, 0.75),
    ('Municipality (public health)', 0.5, 0.0),
    ('Regional water agency (drying climate)', 0.0, -0.75),
    ('Environmental groups (pessimists)', 0.75, -0.75),
]
LAM = np.array([[a, b] for _, a, b in STAKE])
K = len(STAKE)

S = json.load(open(os.path.join(HERE, '..', 'pusi_go', 'res', 'pusi.json')))
QA, QB = S['pumping_m3_d']
QSUM = QA + QB
sites_xy = [(p['x'], p['y']) for p in S['B']['designs']['swap_chem']['sites']]
SITES = [int(np.flatnonzero((np.abs(PA.m.cx[PA.cR] - x) < 1e-9) & (np.abs(PA.m.cy[PA.cR] - y) < 1e-9))[0]) for x, y in sites_xy]
RS = PA.RESP[:, SITES, :].sum(1)                                  # (N, 2) rise at A1, P10 per unit recharge at each site
T20 = PA.tau_chem(SCREEN)                                         # (N, 2) chemistry thresholds of 20-m screens


def zstd(x, w):
    mu = np.sum(w * x); sd = np.sqrt(np.sum(w * (x - mu) ** 2)); return (x - mu) / sd


ZZ = np.column_stack([zstd(np.log(PA.P['w']), PA.W), zstd(np.log(PA.P['R']), PA.W)])   # (N, 2)


def fail(idx, s, q):
    ph = PA.phi_sup(s * QA, s * QB)[idx] + q * RS[idx]
    return (ph < T20[idx]).any(1)


def tilt(idx, base_w, lam):
    lw = np.log(np.maximum(base_w, 1e-300)) + ZZ[idx] @ lam
    lw -= lw.max(); w = np.exp(lw); return w / w.sum()


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    D, V, wD, wV = PA.D, PA.V, PA.wD, PA.wV
    # failure tables on D (inner) and on the truths
    rng = np.random.default_rng(57)
    tru = V[rng.choice(len(V), NY, p=wV)]
    FD = np.stack([np.stack([fail(D, s, q) for s in SG], 1) for q in QG], 2).astype(float)   # (ND, ns, nq)
    FT = np.stack([np.stack([fail(tru, s, q) for s in SG], 1) for q in QG], 2)               # (NY, ns, nq)
    ns, nq = len(SG), len(QG)
    # stakeholder priors on D and the stakeholder views of the truths (importance weights over the outer sample)
    WK = np.stack([tilt(D, wD, LAM[k]) for k in range(K)])                                    # (K, ND)
    VIEW = np.stack([tilt(tru, np.full(NY, 1.0 / NY), LAM[k]) for k in range(K)])             # (K, NY)
    out = dict(alpha=ALPHA, screen_m=SCREEN, q0=[QA, QB], sites=sites_xy, c_r=C_R, stakeholders=[dict(name=n, lam=[a, b]) for n, a, b in STAKE],
               shift_of_mean=[[float(WK[k] @ ZZ[D, 0]), float(WK[k] @ ZZ[D, 1])] for k in range(K)],
               view_ess=[float(1.0 / np.sum(VIEW[k] ** 2)) for k in range(K)])
    # ---------------------------------------------------------------- priors: each stakeholder's own cap
    PK0 = np.einsum('kd,dsq->ksq', WK, FD)                                                     # (K, ns, nq)

    def cap(Pk):  # largest admissible scale index along the s-axis (monotone check), -1 if none
        ok = Pk <= ALPHA + 1e-12
        n_ok = np.cumprod(ok, axis=-2).sum(-2)
        return n_ok - 1
    capk0 = cap(PK0)                                                                           # (K, nq)
    out['prior'] = dict(P_at_s1_q0=[float(PK0[k, 20, 0]) for k in range(K)],
                        P_at_s1_q5000=[float(PK0[k, 20, 2]) for k in range(K)],
                        cap_k=[[float(SG[c]) if c >= 0 else None for c in capk0[k]] for k in range(K)],
                        monotone_s=bool(np.all(np.diff(FD, axis=1) >= 0)), monotone_q=bool(np.all(np.diff(FD, axis=2) <= 0)),
                        curves_q0=PK0[:, :, 0].tolist(), curves_q5000=PK0[:, :, 2].tolist(), s_grid=SG.tolist())
    print('prior P(s=1,q=0) by stakeholder', np.round(PK0[:, 20, 0], 3), 'caps (q=0)', [SG[c] if c >= 0 else None for c in capk0[:, 0]],
          'monotone', out['prior']['monotone_s'], out['prior']['monotone_q'])
    # ---------------------------------------------------------------- observations (current pumping s = 1)
    dM, BM = PA.geom(PA.cM)
    phM = PA.phi0[:, PA.iM] - QA * PA.uA[:, PA.iM] - QB * PA.uB[:, PA.iM]
    hM, _ = PA.state(phM, dM, BM)
    clM = np.log10(PA.chloride(phM, dM, BM, 'sh'))
    mon = [str(x) for x in PA.Z['mon_ids']]
    noise = rng.standard_normal((NY, 4))
    def ll(kind, name, col):
        j = mon.index(name)
        g, sd = (clM, 0.1) if kind == 'cl' else (hM, 0.2)
        y = g[tru, j] + sd * noise[:, col]
        return -0.5 * ((y[:, None] - g[D, j][None, :]) / sd) ** 2
    L_cl = ll('cl', 'A30', 0)
    L_h = ll('h', 'A3', 1) + ll('h', 'A10', 2) + ll('h', 'A23', 3)
    designs = {'none': np.zeros_like(L_cl), 'heads (A3, A10, A23)': L_h, 'chloride sample (A30)': L_cl, 'chloride + heads': L_cl + L_h}
    # ---------------------------------------------------------------- per design: posteriors, disagreement, rules
    res = {}
    for dn, LL in designs.items():
        if True:
            Pk = np.empty((NY, K, ns, nq)); SEk = np.empty((NY, K, ns, nq)); essk = np.empty((NY, K))
            FF = FD.reshape(len(D), -1)
            for k in range(K):
                A_ = LL + np.log(np.maximum(WK[k], 1e-300))[None, :]
                A_ -= A_.max(1, keepdims=True); E_ = np.exp(A_); E_ /= E_.sum(1, keepdims=True)
                P_ = E_ @ FF; E2 = E_ ** 2
                v_ = (E2 @ FF) * (1 - 2 * P_) + P_ ** 2 * E2.sum(1, keepdims=True)    # sum_i E_i^2 (F_i - P)^2
                Pk[:, k] = P_.reshape(NY, ns, nq); SEk[:, k] = np.sqrt(np.maximum(v_, 0)).reshape(NY, ns, nq)
                essk[:, k] = 1.0 / E2.sum(1)
        # disagreement at s = 0.5, q = 0 and the bound of V1 (max over pairs; sd along the segment, 11 points)
        i05 = int(np.argmin(np.abs(SG - 0.5)))
        spread = Pk[:, :, i05, 0].max(1) - Pk[:, :, i05, 0].min(1)
        if True:
            # V1 bound for the pair with the largest disagreement in each truth: compute sd of (dlam . z) along the
            # segment between the two tilts, starting from the calibrated posterior (lambda = 0) weights
            A0 = LL + np.log(np.maximum(wD, 1e-300))[None, :]
            A0 -= A0.max(1, keepdims=True); E0 = np.exp(A0); E0 /= E0.sum(1, keepdims=True)
            kmax = Pk[:, :, i05, 0].argmax(1); kmin = Pk[:, :, i05, 0].argmin(1)
            bound = np.zeros(NY); bound2 = np.zeros(NY)
            for ti in np.linspace(0, 1, 11):
                lam_t = LAM[kmin] + ti * (LAM[kmax] - LAM[kmin])                            # (NY, 2)
                dl = LAM[kmax] - LAM[kmin]
                lw = np.log(np.maximum(E0, 1e-300)) + lam_t @ ZZ[D].T
                lw -= lw.max(1, keepdims=True); Et = np.exp(lw); Et /= Et.sum(1, keepdims=True)
                u = (dl[:, :, None] * ZZ[D].T[None, :, :]).sum(1)                               # (NY, ND)
                mu = (Et * u).sum(1); sd = np.sqrt(np.maximum((Et * u * u).sum(1) - mu ** 2, 0))
                pf = Et @ FD[:, i05, 0]
                bound = np.maximum(bound, 0.5 * sd); bound2 = np.maximum(bound2, sd * np.sqrt(np.maximum(pf * (1 - pf), 0.0)))
            viol = float(np.mean(spread > bound + 1e-9)); viol2 = float(np.mean(spread > bound2 + 1e-9))
        # posterior spread of the mixing width (calibrated prior), the disputed quantity
        if True:
            mu = E0 @ ZZ[D, 0]; sdw = float(np.mean(np.sqrt(np.maximum(E0 @ ZZ[D, 0] ** 2 - mu ** 2, 0))))
        # rules with a certified margin: a stakeholder accepts (s, q) if P_k + ZM * se_k <= ALPHA
        ar = np.arange(NY)
        UK = Pk + ZM * SEk                                                                        # (NY, K, ns, nq)
        cU = cap(UK.max(1)); cP = cap(Pk.mean(1) + ZM * SEk.mean(1))                              # (NY, nq)
        sU = np.where(cU >= 0, SG[np.maximum(cU, 0)], 0.0); sP = np.where(cP >= 0, SG[np.maximum(cP, 0)], 0.0)
        rows = []
        for iq, q in enumerate(QG):
            fU = FT[ar, np.maximum(cU[:, iq], 0), iq]
            veto = (UK[ar, :, np.maximum(cP[:, iq], 0), iq] > ALPHA + 1e-12).sum(1)
            rows.append(dict(q=float(q), s_unan=float(sU[:, iq].mean()), water_unan=float(sU[:, iq].mean() * QSUM),
                             s_pool=float(sP[:, iq].mean()), water_pool=float(sP[:, iq].mean() * QSUM),
                             no_admissible=float(np.mean(cU[:, iq] < 0)), mean_vetoes_pool=float(veto.mean()),
                             fail_unan_by_view=[float(VIEW[k] @ fU) for k in range(K)]))
        # the joint decisive choice: recharge level and pumping with the largest net water among admissible pairs
        net = np.where(cU >= 0, sU * QSUM - C_R * 3 * QG[None, :], -np.inf)                       # (NY, nq)
        feas = np.isfinite(net).any(1)
        iq_star = np.where(feas, np.argmax(net, 1), nq - 1)
        s_star = np.where(feas, sU[ar, iq_star], 0.0)
        f_star = FT[ar, np.where(feas, np.maximum(cU[ar, iq_star], 0), 0), iq_star]
        netP = np.where(cP >= 0, sP * QSUM - C_R * 3 * QG[None, :], -np.inf)
        iqP = np.where(np.isfinite(netP).any(1), np.argmax(netP, 1), nq - 1)
        sPs = np.where(np.isfinite(netP).any(1), sP[ar, iqP], 0.0)
        vetoP = (UK[ar, :, np.maximum(cP[ar, iqP], 0), iqP] > ALPHA + 1e-12).sum(1)
        joint = dict(water=float((s_star * QSUM).mean()), recharge=float((3 * QG[iq_star]).mean()),
                     net=float((s_star * QSUM - C_R * 3 * QG[iq_star]).mean()), deadlock=float(1 - feas.mean()),
                     q_share={str(int(q)): float(np.mean(iq_star == i)) for i, q in enumerate(QG)},
                     fail_by_view=[float(VIEW[k] @ f_star) for k in range(K)],
                     fail_se_by_view=[float(np.sqrt(np.sum(VIEW[k] ** 2 * (f_star - VIEW[k] @ f_star) ** 2))) for k in range(K)],
                     net_by_view=[float(VIEW[k] @ (s_star * QSUM - C_R * 3 * QG[iq_star])) for k in range(K)],
                     pool_net=float((sPs * QSUM - C_R * 3 * QG[iqP]).mean()), pool_mean_vetoes=float(vetoP.mean()),
                     pool_p_veto=float(np.mean(vetoP > 0)),
                     pool_fail_by_view=[float(VIEW[k] @ FT[ar, np.maximum(cP[ar, iqP], 0), iqP]) for k in range(K)],
                     ess_min_median=float(np.median(essk.min(1))))
        joint['price_of_unanimity'] = joint['pool_net'] - joint['net']
        res[dn] = dict(spread_mean=float(spread.mean()), spread_q90=float(np.quantile(spread, 0.9)),
                       bound_mean=float(bound.mean()), bound2_mean=float(bound2.mean()), bound_violations=viol, bound2_violations=viol2,
                       sd_zwidth=sdw, rows=rows, joint=joint)
        jj = res[dn]['joint']
        print(f"{dn:24s} spread {spread.mean():.3f} bounds {bound.mean():.3f}/{bound2.mean():.3f} viol {viol}/{viol2} | joint: water {jj['water']:.0f} recharge {jj['recharge']:.0f} net {jj['net']:.0f} deadlock {jj['deadlock']:.3f} q {jj['q_share']} fail(views) {np.round(jj['fail_by_view'], 3)} | pool net {jj['pool_net']:.0f} vetoes {jj['pool_mean_vetoes']:.2f} pool fail {np.round(jj['pool_fail_by_view'], 3)} ess {jj['ess_min_median']:.0f} {time.time() - t0:.0f}s")
    out['designs'] = res
    # value of information in net water, by each stakeholder's own expectation
    out['voi_net_by_view'] = {dn: [res[dn]['joint']['net_by_view'][k] - res['none']['joint']['net_by_view'][k] for k in range(K)]
                              for dn in designs if dn != 'none'}
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(RES, 'vendimi.json'), 'w'), indent=1)
    print('wrote res/vendimi.json', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
