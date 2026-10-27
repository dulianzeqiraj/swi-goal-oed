"""MOTI-GO (moti: the weather): one decisive rule for all weathers, with margins for human error and objective
triggers. Innovation of literature review 59 (decisive stakeholder decisions from normal to extreme conditions, with
objective and subjective human factors; Oxford, Caltech, MIT, ETH Zurich, 2020-2026).

Setting: the calibrated chloride ensemble of PUSI-GO and the stakeholders, actions, risk limit and certified margin of
VENDIMI-GO (../vendimi_go). The steady potential is linear in the recharge and in every pumping or injection, so a
weather regime r is a storyline of four numbers applied to the same ensemble:
    phi = f_R * phi0 - s (1 + eps) * dd + q * RS - E * RH,      eps ~ N(mu_r, sigma_r)
f_R: recharge factor (drought), eps: the utility's implementation slippage (operators overshoot the licence; objective
human factor), E: unlicensed coastal pumping by hotels and irrigators at four coastal cells near the supply wells
(objective human factor), q_max: recharge capacity (source water). Subjective human factors act on decisions taken in
the crisis: polarisation of the stakeholders' tilts (kappa_r), a common pessimistic shift along the width (delta_r)
and probability weighting of the perceived risk (Prelec, gamma_r).

Rules compared in each regime (no new data):
  FW  fair-weather plan: the VENDIMI-GO choice of a normal year, used in every regime
  IC  in-crisis decision: VENDIMI-GO rule taken when the regime arrives, with the regime's recharge but crisis beliefs
      and perceived risks, and no allowance for slippage or unlicensed pumping
  PC0 pre-committed plan, physics only (regime recharge and capacity, calm beliefs)
  PC  pre-committed plan (MOTI-GO): regime physics, calm beliefs, exact allowance for slippage (Gauss-Hermite
      convolution) and for unlicensed pumping; deadlock = emergency stop (no pumping, largest recharge)
Also: the emergency-stop threshold f* (Proposition S3), the rule curve s*(f), trigger misclassification (S2) and a
Shapley attribution of the fair-weather plan's risk to climate, operational error and unlicensed pumping.
Output res/moti.json.   Run: python3 moti.py   (a few minutes)
"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vendimi_go'))
import vendimi as VG  # noqa: E402

PA = VG.PA
RES = os.path.join(HERE, 'res')
ALPHA, ZM, SG, QG, C_R, QSUM, K, NY = VG.ALPHA, VG.ZM, VG.SG, VG.QG, VG.C_R, VG.QSUM, VG.K, VG.NY
ns, nq = len(SG), len(QG)
DD = VG.QA * PA.uA[:, PA.iS] + VG.QB * PA.uB[:, PA.iS]                       # (N, 2) drawdown at A1, P10 per unit scale
PHI0 = PA.phi0[:, PA.iS]
HOTEL = [(3.25, 34.25), (2.0, 38.0), (2.0, 33.0), (1.0, 38.0)]               # coastal cells near the supply wells
HK = [int(np.flatnonzero((np.abs(PA.m.cx[PA.cR] - x) < 1e-9) & (np.abs(PA.m.cy[PA.cR] - y) < 1e-9))[0]) for x, y in HOTEL]
RH = PA.RESP[:, HK, :].mean(1)                                              # (N, 2) response per unit pumping, averaged
REG = [  # name, f_R, mu, sigma, E (m3/d), q_max, kappa, delta, gamma
    dict(key='N', name='Normal year', fR=1.00, mu=0.00, sd=0.05, E=0.0, qmax=10000.0, kappa=1.00, delta=0.00, gamma=1.00),
    dict(key='D', name='Dry year', fR=0.75, mu=0.05, sd=0.10, E=1000.0, qmax=10000.0, kappa=1.25, delta=0.15, gamma=0.90),
    dict(key='X', name='Extreme drought', fR=0.50, mu=0.10, sd=0.15, E=2000.0, qmax=5000.0, kappa=1.50, delta=0.30, gamma=0.80),
    dict(key='H', name='Extreme drought with heatwave', fR=0.50, mu=0.20, sd=0.25, E=4000.0, qmax=5000.0, kappa=2.00, delta=0.50, gamma=0.70),
]
CLIM = {'present': [0.60, 0.25, 0.10, 0.05], 'drier future': [0.35, 0.30, 0.20, 0.15]}
GH_X, GH_W = np.polynomial.hermite.hermgauss(15)
GH_W = GH_W / np.sqrt(np.pi)


def fail(idx, s_act, q, fR, E):
    s_act = np.asarray(s_act, float)
    ph = fR * PHI0[idx] - (s_act[:, None] if s_act.ndim else s_act) * DD[idx] + q * VG.RS[idx] - E * RH[idx]
    return (ph < VG.T20[idx]).any(1)


def prelec(p, g):
    p = np.clip(p, 1e-12, 1.0)
    return np.exp(-(-np.log(p)) ** g)


def cap_of(U):
    """U (ns, nq) certified risks; largest admissible s index per q with every smaller s admissible, -1 if none."""
    return np.cumprod(U <= ALPHA + 1e-12, axis=0).sum(0) - 1


def choose(cap, qmax):
    """joint decisive choice (s, q) from caps; emergency stop if nothing is admissible."""
    best, arg = -np.inf, None
    for iq, q in enumerate(QG):
        if q > qmax + 1e-9 or cap[iq] < 0:
            continue
        net = SG[cap[iq]] * QSUM - C_R * 3 * q
        if net > best:
            best, arg = net, (float(SG[cap[iq]]), float(q))
    if arg is None:
        return dict(s=0.0, q=float(qmax), stop=True)
    return dict(s=arg[0], q=arg[1], stop=False)


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    D, V, wD, wV = PA.D, PA.V, PA.wD, PA.wV
    rng = np.random.default_rng(57)
    tru = V[rng.choice(len(V), NY, p=wV)]                                   # the truths of VENDIMI-GO
    rng2 = np.random.default_rng(59)
    Zeps = rng2.standard_normal(NY)                                          # one slippage draw per truth, scaled per regime
    WK = np.stack([VG.tilt(D, wD, VG.LAM[k]) for k in range(K)])
    VIEW = np.stack([VG.tilt(tru, np.full(NY, 1.0 / NY), VG.LAM[k]) for k in range(K)])
    out = dict(alpha=ALPHA, zm=ZM, regimes=REG, climatology=CLIM, hotel_cells=HOTEL, gh_nodes=len(GH_X),
               phi0_positive=bool(np.all(PHI0 > 0)), monotone=dict())

    def risk_table(fR, mu, sd, E, qmax, weights, slip=True):
        """certified risk of every (s, q) under each belief in `weights` (K', ND): exact convolution over the slippage."""
        P = np.zeros((len(weights), ns, nq)); S2 = np.zeros_like(P)
        for iq, q in enumerate(QG):
            for i_s, s in enumerate(SG):
                if slip:
                    F = np.zeros(len(D))
                    for x, w in zip(GH_X, GH_W):
                        e = max(mu + np.sqrt(2) * sd * x, -0.9)
                        F += w * fail(D, s * (1 + e), q, fR, E)
                else:
                    F = fail(D, s, q, fR, E).astype(float)
                p = weights @ F
                P[:, i_s, iq] = p
                S2[:, i_s, iq] = np.sum(weights ** 2 * (F[None, :] - p[:, None]) ** 2, 1)
        return P, np.sqrt(S2)

    def evaluate(plan, r):
        e = np.maximum(r['mu'] + r['sd'] * Zeps, -0.9)
        F = fail(tru, plan['s'] * (1 + e), plan['q'], r['fR'], r['E']).astype(float)
        rv = VIEW @ F; se = np.sqrt(np.sum(VIEW ** 2 * (F[None, :] - rv[:, None]) ** 2, 1))
        return dict(s=plan['s'], q=plan['q'], stop=plan['stop'], water=plan['s'] * QSUM, net=plan['s'] * QSUM - C_R * 3 * plan['q'],
                    risk=float(F.mean()), risk_se=float(F.std() / np.sqrt(NY)), risk_by_view=rv.tolist(), se_by_view=se.tolist())

    # ---------------------------------------------------------------- plans per regime
    N0 = REG[0]
    P, Se = risk_table(1.0, 0.0, 0.0, 0.0, 1e9, WK, slip=False)
    fw = choose(cap_of((P + ZM * Se).max(0)), 1e9)
    out['monotone']['normal_physics'] = bool(np.all(np.diff(P, axis=1) >= -1e-12))
    rows = []
    for r in REG:
        row = dict(key=r['key'], name=r['name'])
        # PC0: physics only
        P0, S0 = risk_table(r['fR'], 0.0, 0.0, 0.0, r['qmax'], WK, slip=False)
        pc0 = choose(cap_of((P0 + ZM * S0).max(0)), r['qmax'])
        # PC: physics + slippage convolution + unlicensed pumping
        P1, S1 = risk_table(r['fR'], r['mu'], r['sd'], r['E'], r['qmax'], WK, slip=True)
        pc = choose(cap_of((P1 + ZM * S1).max(0)), r['qmax'])
        out['monotone'][r['key']] = bool(np.all(np.diff(P1, axis=1) >= -1e-9) and np.all(np.diff(P1, axis=2) <= 1e-9))
        # IC: crisis beliefs and perceived risks, regime recharge only
        lam_c = r['kappa'] * VG.LAM + np.array([r['delta'], 0.0])[None, :]
        WC = np.stack([VG.tilt(D, wD, lam_c[k]) for k in range(K)])
        P2, S2 = risk_table(r['fR'], 0.0, 0.0, 0.0, r['qmax'], WC, slip=False)
        ic = choose(cap_of(prelec(P2 + ZM * S2, r['gamma']).max(0)), r['qmax'])
        # subjective factors one at a time (for the crisis decision)
        sub = {}
        for nm, kap, dl, gm in (('polarisation', r['kappa'], 0.0, 1.0), ('salience', 1.0, r['delta'], 1.0), ('weighting', 1.0, 0.0, r['gamma'])):
            lc = kap * VG.LAM + np.array([dl, 0.0])[None, :]
            Wc = np.stack([VG.tilt(D, wD, lc[k]) for k in range(K)])
            Pc, Sc = risk_table(r['fR'], 0.0, 0.0, 0.0, r['qmax'], Wc, slip=False)
            sub[nm] = evaluate(choose(cap_of(prelec(Pc + ZM * Sc, gm).max(0)), r['qmax']), r)
        row.update(FW=evaluate(fw, r), PC0=evaluate(pc0, r), PC=evaluate(pc, r), IC=evaluate(ic, r), IC_one_factor=sub)
        # Shapley attribution of the fair-weather plan's realised risk: climate, operational error, unlicensed pumping
        def R_of(c, o, u):
            rr = dict(fR=r['fR'] if c else 1.0, mu=r['mu'] if o else 0.0, sd=r['sd'] if o else 0.0, E=r['E'] if u else 0.0)
            return evaluate(fw, rr)['risk']
        Rv = {(c, o, u): R_of(c, o, u) for c in (0, 1) for o in (0, 1) for u in (0, 1)}
        def shap(i):
            tot = 0.0
            for S in [(a, b) for a in (0, 1) for b in (0, 1)]:
                key = [None, None, None]; others = [j for j in range(3) if j != i]
                key[others[0]], key[others[1]] = S
                size = sum(S)
                wgt = [1 / 3, 1 / 6, 1 / 3][size] if size != 1 else 1 / 6
                k1 = list(key); k1[i] = 1; k0 = list(key); k0[i] = 0
                tot += wgt * (Rv[tuple(k1)] - Rv[tuple(k0)])
            return tot
        row['attribution_FW'] = dict(base=Rv[(0, 0, 0)], climate=shap(0), operational=shap(1), unlicensed=shap(2), total=Rv[(1, 1, 1)])
        rows.append(row)
        print(r['key'], 'FW', round(row['FW']['risk'], 3), 'PC0', pc0, round(row['PC0']['risk'], 3), 'PC', pc, round(row['PC']['risk'], 3),
              round(max(row['PC']['risk_by_view']), 3), 'IC', ic, round(row['IC']['risk'], 3), f'{time.time() - t0:.0f}s', flush=True)
    out['plans'] = rows

    # ---------------------------------------------------------------- annual risk, climatologies, trigger errors
    ann = {}
    for cn, pi in CLIM.items():
        a = {}
        for rule in ('FW', 'IC', 'PC0', 'PC'):
            a[rule] = dict(risk=float(sum(p * rw[rule]['risk'] for p, rw in zip(pi, rows))),
                           worst_view=float(max(sum(p * rw[rule]['risk_by_view'][k] for p, rw in zip(pi, rows)) for k in range(K))),
                           net=float(sum(p * rw[rule]['net'] for p, rw in zip(pi, rows))),
                           stops=float(sum(p * rw[rule]['stop'] for p, rw in zip(pi, rows))))
        for m in (0.1, 0.2, 0.3):
            for kind, step in (('milder', -1), ('severer', +1)):
                tot = 0.0; totv = np.zeros(K); net = 0.0
                for j, (p, r) in enumerate(zip(pi, REG)):
                    jj = min(max(j + step, 0), len(REG) - 1)
                    pj = rows[jj]['PC']                                          # plan of the regime the trigger declares
                    qa = r['qmax'] if pj['stop'] else min(pj['q'], r['qmax'])     # a stop uses the largest recharge available
                    alt = evaluate(dict(s=pj['s'], q=qa, stop=pj['stop']), r)
                    own = rows[j]['PC']
                    mm = m if jj != j else 0.0
                    tot += p * ((1 - mm) * own['risk'] + mm * alt['risk'])
                    totv += p * ((1 - mm) * np.array(own['risk_by_view']) + mm * np.array(alt['risk_by_view']))
                    net += p * ((1 - mm) * own['net'] + mm * alt['net'])
                a[f'PC_trigger_{kind}_{m}'] = dict(risk=float(tot), worst_view=float(totv.max()), net=float(net))
        ann[cn] = a
    out['annual'] = ann

    # ---------------------------------------------------------------- emergency-stop threshold (S3) and rule curve
    fi = {}
    for q in (0.0, 5000.0, 10000.0):
        for E in (0.0, 2000.0, 4000.0):
            f_i = ((VG.T20[D] - q * VG.RS[D] + E * RH[D]) / PHI0[D]).max(1)                  # zero pumping fails iff f < f_i
            row = []
            for k in range(K):
                o = np.argsort(f_i); c = np.cumsum(WK[k][o])
                row.append(float(f_i[o][np.searchsorted(c, 1 - ALPHA)]))                       # P_k(f_i > f) <= alpha
            fi[f'q{int(q)}_E{int(E)}'] = dict(by_view=row, group=max(row))
    out['emergency_threshold'] = fi
    # check S3 against the direct computation at q = 5000, E = 2000
    th = fi['q5000_E2000']['group']
    chk = []
    for f in (th - 0.02, th + 0.02):
        F = fail(D, 0.0, 5000.0, f, 2000.0).astype(float)
        chk.append(float(max(WK[k] @ F for k in range(K))))
    out['emergency_check'] = dict(below=chk[0], above=chk[1])
    FG = np.round(np.arange(0.30, 1.201, 0.05), 3)
    curve = {}
    for heat in (False, True):
        cs = []
        for f in FG:
            t = np.clip((1.0 - f) / 0.5, 0.0, 1.2)                                               # 0 at f = 1, 1 at f = 0.5
            mu = 0.10 * t + (0.10 if heat else 0.0); sd = 0.05 + 0.10 * t + (0.10 if heat else 0.0)
            E = 2000.0 * t + (2000.0 if heat else 0.0); qmax = 10000.0 if f > 0.6 else 5000.0
            Pc, Sc = risk_table(f, mu, sd, E, qmax, WK, slip=True)
            cp = cap_of((Pc + ZM * Sc).max(0))
            pl = choose(cp, qmax)
            cs.append(dict(f=float(f), s=pl['s'], q=pl['q'], stop=pl['stop'], net=pl['s'] * QSUM - C_R * 3 * pl['q'],
                           cap_by_q={str(int(q)): (float(SG[cp[iq]]) if cp[iq] >= 0 else None) for iq, q in enumerate(QG)}))
        curve['heatwave' if heat else 'no heatwave'] = cs
        print('rule curve', 'heat' if heat else 'no heat', [(c['f'], c['s'], c['q'], c['stop']) for c in cs], f'{time.time() - t0:.0f}s', flush=True)
    out['rule_curve'] = curve
    # ---------------------------------------------------------------- what it takes: emergency recharge needed for a safe stop
    need, needc = {}, {}
    for f in (0.5, 0.6, 0.75):
        for E in (0.0, 2000.0, 4000.0):
            for certified, store in ((False, need), (True, needc)):
                lo, hi = 0.0, 60000.0
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    F = fail(D, 0.0, mid, f, E).astype(float)
                    p = WK @ F
                    if certified:
                        p = p + ZM * np.sqrt(np.sum(WK ** 2 * (F[None, :] - p[:, None]) ** 2, 1))
                    if p.max() <= ALPHA: hi = mid
                    else: lo = mid
                store[f'f{f}_E{int(E)}'] = hi
    out['recharge_needed_for_safe_stop'] = need                                  # nominal, as in Proposition S4
    out['recharge_needed_for_safe_stop_certified'] = needc                       # with the certified Monte Carlo margin
    for r in REG[2:]:
        rr = dict(r); rr['E'] = 0.0
        out.setdefault('stop_with_ban', {})[r['key']] = evaluate(dict(s=0.0, q=r['qmax'], stop=True), rr)['risk']
    print('recharge needed', need, out['stop_with_ban'], flush=True)
    # ---------------------------------------------------------------- S3: are the plans nested (severer plan safer in every regime)?
    nest = []
    for j, r in enumerate(REG):
        for jj in range(j + 1, len(REG)):
            pj = rows[jj]['PC']; qa = r['qmax'] if pj['stop'] else min(pj['q'], r['qmax'])
            nest.append(dict(true=r['key'], plan=REG[jj]['key'], s=pj['s'], q=qa, own_s=rows[j]['PC']['s'], own_q=rows[j]['PC']['q'],
                             componentwise=bool(pj['s'] <= rows[j]['PC']['s'] and qa >= rows[j]['PC']['q'])))
    out['nested'] = nest
    # ---------------------------------------------------------------- what it takes: the stop with emergency recharge capacity
    cap = {}
    for r in REG[2:]:
        qn = needc[f"f{r['fR']}_E{int(r['E'])}"]
        ev = evaluate(dict(s=0.0, q=qn, stop=True), r)
        kw = int(np.argmax(ev['risk_by_view']))
        cap[r['key']] = dict(q=qn, risk=ev['risk'], risk_se=ev['risk_se'], worst_view=max(ev['risk_by_view']), se_worst_view=ev['se_by_view'][kw], net=ev['net'])
    out['stop_with_capacity'] = cap
    ac = {}
    for cn, pi in CLIM.items():
        rk = [rows[0]['PC']['risk'], rows[1]['PC']['risk'], cap['X']['risk'], cap['H']['risk']]
        rv = [max(rows[0]['PC']['risk_by_view']), max(rows[1]['PC']['risk_by_view']), cap['X']['worst_view'], cap['H']['worst_view']]
        vv = np.array([rows[0]['PC']['risk_by_view'], rows[1]['PC']['risk_by_view'],
                       evaluate(dict(s=0.0, q=cap['X']['q'], stop=True), REG[2])['risk_by_view'],
                       evaluate(dict(s=0.0, q=cap['H']['q'], stop=True), REG[3])['risk_by_view']])
        ac[cn] = dict(risk=float(np.dot(pi, rk)), worst_view=float((np.array(pi) @ vv).max()),
                      net=float(np.dot(pi, [rows[0]['PC']['net'], rows[1]['PC']['net'], cap['X']['net'], cap['H']['net']])))
    out['annual_with_capacity'] = ac
    # ---------------------------------------------------------------- S1 bound and S2 equivalence, checked on the design ensemble
    chk = {}
    beta = 0.05
    for r in (REG[1], REG[3]):
        eb = r['mu'] + 1.6448536269514722 * r['sd']                                      # upper 5% quantile of the slippage
        qq = 10000.0 if r['qmax'] >= 10000 else 5000.0
        rows_b = []
        for s_ in (0.2, 0.4, 0.6, 0.8, 1.0):
            Fc = np.zeros(len(D))
            for x, w in zip(GH_X, GH_W):
                e = max(r['mu'] + np.sqrt(2) * r['sd'] * x, -0.9)
                Fc += w * fail(D, s_ * (1 + e), qq, r['fR'], r['E'])
            Fb = fail(D, s_ * (1 + eb), qq, r['fR'], r['E']).astype(float)
            conv = float(max(WK[k] @ Fc for k in range(K))); bnd = float(max(WK[k] @ Fb for k in range(K)))
            rows_b.append(dict(s=s_, conv=conv, bound=bnd + beta, quantile_only=bnd))
        chk[r['key']] = dict(q=qq, e_beta=eb, rows=rows_b)
    out['S1_bound'] = dict(beta=beta, regimes=chk)
    eqv = {}
    for r in REG[1:]:
        ag = float(np.exp(-(-np.log(ALPHA)) ** (1.0 / r['gamma'])))
        P0, S0 = risk_table(r['fR'], 0.0, 0.0, 0.0, r['qmax'], WK, slip=False)
        U = (P0 + ZM * S0).max(0)
        a1 = cap_of(prelec(U, r['gamma'])); a2 = np.cumprod(U <= ag + 1e-12, axis=0).sum(0) - 1
        eqv[r['key']] = dict(gamma=r['gamma'], alpha_gamma=ag, same_caps=bool(np.all(a1 == a2)))
    out['S2_weighting'] = eqv
    print('nested', [n['componentwise'] for n in nest], 'capacity', cap, ac, chk, eqv, flush=True)
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(RES, 'moti.json'), 'w'), indent=1)
    print('wrote res/moti.json', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
