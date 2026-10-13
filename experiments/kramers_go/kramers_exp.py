"""KRAMERS-GO experiments (see kramers2.py for the model).
E1 escape time vs pumping: simulation, 2D Kolmogorov, 1D white-noise reduction, Kramers rule.
E2 return-period-safe pumping Q_T (MFPT = T) at nominal parameters.
E3 Q_T under the prior on K and q0 (60 draws).
E4 elasticities of Q_100 to s (recharge-anomaly sd), theta, tau, K and q0 (one at a time, +-20%).
"""
import json, time
import numpy as np
from multiprocessing import Pool
import kramers2 as KR

FG = np.round(np.arange(0.55, 0.981, 0.025), 3)
TS = [10, 25, 50, 100, 200, 500]
GRID = dict(nx=720, ne=241, emax=5.0)

def lnT_curve(P):
    mu = KR.mu_of(P); lc = KR.lam_crit(mu)
    out = []
    for f in FG:
        Xs, Xu = KR.stable(mu, f * lc)
        out.append(np.log(KR.mfpt2d(mu, f * lc, P, Xs, **GRID)))
    return np.array(out)

def q_safe(P, lnT):
    """pumping fraction f with MFPT = T for each T (lnT decreasing in f)."""
    res = {}
    for T in TS:
        y = np.log(T)
        if y > lnT[0]:
            res[T] = float(FG[0]); continue
        if y < lnT[-1]:
            res[T] = float(FG[-1]); continue
        res[T] = float(np.interp(-y, -lnT, FG))
    return res

def e1_row(f):
    P = dict(KR.P0); mu = KR.mu_of(P); lam = f * KR.lam_crit(mu); Xs, Xu = KR.stable(mu, lam)
    S = KR.simulate(mu, lam, P, Xs, n=2000, tmax=6000.0, dt=0.005, seed=int(1000 * f))
    T2 = KR.mfpt2d(mu, lam, P, Xs, nx=720, ne=481, emax=5.0)
    TR, k, var = KR.kramers_rule(mu, lam, P)
    return dict(f=f, Xs_m=Xs * P['d'], Xu_m=Xu * P['d'], k=k, sd_m=float(np.sqrt(var) * P['d']), T_sim=S['mfpt'], events=S['events'],
                n=S['n'], T_2D=T2, T_1D=KR.mfpt1d(mu, lam, P, Xs), T_kramers=TR)

def e3_draw(seed):
    rng = np.random.default_rng(seed)
    P = dict(KR.P0)
    for key, cv in [('K', 0.3), ('q0', 0.2)]:
        s = np.sqrt(np.log(1 + cv ** 2)); P[key] = KR.P0[key] * np.exp(s * rng.standard_normal() - 0.5 * s * s)
    if KR.mu_of(P) >= 0.95:
        return None
    lnT = lnT_curve(P)
    return dict(K=P['K'], q0=P['q0'], Qc=KR.Qc_of(P), fsafe=q_safe(P, lnT))

def e4_case(args):
    key, fac = args
    P = dict(KR.P0); P[key] = KR.P0[key] * fac
    lnT = lnT_curve(P)
    return dict(key=key, fac=fac, Qc=KR.Qc_of(P), fsafe=q_safe(P, lnT))

if __name__ == '__main__':
    t0 = time.time()
    with Pool(4) as pool:
        E1 = pool.map(e1_row, [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95])
        print('E1 done', round(time.time() - t0), flush=True)
        P = dict(KR.P0); lnT0 = lnT_curve(P); E2 = dict(Qc=KR.Qc_of(P), fsafe=q_safe(P, lnT0), FG=FG.tolist(), lnT=lnT0.tolist())
        print('E2 done', round(time.time() - t0), flush=True)
        E3 = [r for r in pool.map(e3_draw, range(500, 560)) if r is not None]
        print('E3 done', round(time.time() - t0), flush=True)
        E4 = pool.map(e4_case, [(k, f) for k in ['s', 'theta', 'tau', 'K', 'q0'] for f in (0.8, 1.2)])
        print('E4 done', round(time.time() - t0), flush=True)
    json.dump(dict(E1=E1, E2=E2, E3=E3, E4=E4, TS=TS), open('kramers_results.json', 'w'), indent=1)
    for r in E1:
        print(f"f={r['f']:.2f} sim={r['T_sim']:.1f} ({r['events']}/{r['n']}) 2D={r['T_2D']:.1f} 1D={r['T_1D']:.1f} Kramers={r['T_kramers']:.1f}")
    print('nominal Qc', round(E2['Qc']), 'f_safe', E2['fsafe'])
