"""KRIPA-GO: counterfactual salinity of the Fushe-Kuqe aquifer under a drier recharge regime, and how the dispersion
width enters it.

Model: the areal chloride model of chloride_fk (steady Strack potential, sharp interface with a dispersive transition
zone of width w, screen-averaged chloride; 20 000 prior draws of the calibration of chloride_fk, with the likelihood of
the documented facts: shallow salinized area, littoral head, mid-depth seawater fraction, NE chloride bound).
Counterfactual: the same aquifer (conductivity field, geometry, w, seawater chloride) with the long-term recharge
c R instead of R (drought c = 0.6; dose-response c = 0.5 ... 1.5, c > 1 a managed-recharge regime).
Because the potential is linear in R for fixed K (homogeneous boundary conditions), phi(cR) = c phi(R): the
counterfactual state follows from the factual one without a new solve, and even from the factual heads alone.
Goals: the shallow salinized area (Cl > 250 mg/L, km2), the area of the deep wedge toe (km2) and the median mid-depth
seawater fraction of the SW band (%), factual and counterfactual, and their differences.
Tests:
  T25  exactness of state abduction (re-solved counterfactual vs c phi; counterfactual interface from the heads)
  T26  the Fushe-Kuqe counterfactual with the real facts: interventional (prior) and counterfactual (posterior)
       bands, importance-sampling and conformal; dose-response over c; monotonicity
  T27  coverage on 600 simulated data sets (300 calibration, 300 test): importance sampling vs conformal
  T28  what the counterfactual depends on: facts one group at a time, first-order variance shares of the unknowns,
       and the cross-world law of the dispersion width (w' = w c^-beta, beta = 0, 0.25, 0.5)
usage: python kripa_exp.py   (writes res/kripa.json, res/kripa_maps.npz, res/kripa_log.txt)"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.special import expit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))
import fkcl_model as FM  # noqa: E402
import fkcl_calib as FC  # noqa: E402

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
APOLY = FC.APOLY
OBS = FC.OBS
CGRID = (0.5, 0.6, 0.7, 0.8, 0.9, 1.2, 1.5)
C0 = 0.6
BETAS = (0.25, 0.5)
GOALS = (('A', 0, APOLY, 'shallow salinized area (km²)'), ('T', 5, 1.0, 'toe area (km²)'),
         ('F', 10, 100.0, 'mid-depth seawater fraction, SW band (%)'))
NMAP = 1000
LOG = []
_m = _mk = _P = None


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


def load_ensemble():
    z = np.load(os.path.join(ROOT, 'chloride_fk', 'results', 'calib_ensemble.npz'))
    P = {k: z[k] for k in ('theta', 'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s')}
    return P, z['S'], z['ll']


def _init():
    global _m, _mk, _P
    _m = FM.Model()
    _mk = FC.masks(_m)
    _P, _, _ = load_ensemble()


def counterfactual(m, o, p, c, w=None):
    """the state and chloride of the twin aquifer with recharge c R, from the factual potential (no new solve)."""
    q = dict(p)
    if w is not None:
        q['w'] = w
    h, zeta, d, B = m.state(c * o['phi'], q)
    Cl, f = m.chloride(zeta, d, B, q['w'], q['Cl_s'])
    return dict(phi=c * o['phi'], h=h, zeta=zeta, d=d, B=B, Cl_sh=Cl['sh'], Cl_mid=Cl['mid'], Cl_dp=Cl['dp'],
                f_sh=f['sh'], f_mid=f['mid'], f_dp=f['dp'])


def _work(rows):
    out1 = np.zeros((len(rows), len(FC.SUMNAMES)))
    outc = np.zeros((len(rows), len(CGRID), len(FC.SUMNAMES)))
    outb = np.zeros((len(rows), len(BETAS), len(FC.SUMNAMES)))
    mono = np.zeros(len(rows))
    for r, i in enumerate(rows):
        p = FM.Model.one(_P, i)
        o = _m.run(p)
        out1[r] = FC.summarize(_m, o, _mk)
        for k, c in enumerate(CGRID):
            oc = counterfactual(_m, o, p, c)
            outc[r, k] = FC.summarize(_m, oc, _mk)
            if c < 1:
                mono[r] = min(mono[r], float(np.min(np.where(_m.valid, oc['Cl_sh'] - o['Cl_sh'], 0.0))))
        for k, b in enumerate(BETAS):
            ob = counterfactual(_m, o, p, C0, w=p['w'] * C0 ** (-b))
            outb[r, k] = FC.summarize(_m, ob, _mk)
    return out1, outc, outb, mono


def _maps(rows):
    E1 = np.zeros(_m.Nc); E0 = np.zeros(_m.Nc)
    for i in rows:
        p = FM.Model.one(_P, i)
        o = _m.run(p)
        oc = counterfactual(_m, o, p, C0)
        E1 += (o['Cl_sh'] > FM.CL_LIMIT) & _m.valid
        E0 += (oc['Cl_sh'] > FM.CL_LIMIT) & _m.valid
    return E1, E0


def t25(m, P):
    """exactness of state abduction on 200 draws."""
    rng = np.random.default_rng(25)
    err_phi, err_zeta_h = 0.0, 0.0
    delta = FM.DELTA
    for i in rng.choice(len(P['R']), 200, replace=False):
        p = FM.Model.one(P, i)
        o = m.run(p)
        q = dict(p); q['R'] = C0 * p['R']
        o2 = m.run(q)
        err_phi = max(err_phi, float(np.max(np.abs(o2['phi'] - C0 * o['phi'])) / np.max(np.abs(o['phi']))))
        # the factual heads alone (with the geometry) give the factual potential, hence the twin interface
        d, B = o['d'], o['B']
        ht = delta * (d + B)
        phi_h = np.where(o['h'] < ht, (o['h'] - delta * d) ** 2 / (2 * delta), B * (o['h'] - delta * (d + 0.5 * B)))
        _, zeta_h, _, _ = m.state(C0 * phi_h, p)
        v = m.valid
        err_zeta_h = max(err_zeta_h, float(np.max(np.abs(zeta_h[v] - o2['zeta'][v]))))
    return dict(phi_rel=err_phi, zeta_from_heads_m=err_zeta_h)


def loglik_parts(S, obs):
    """the four facts, one log-likelihood term each (as fkcl_calib.loglik, with a 'below' flag for the NE bound)."""
    lsig = lambda x: -np.logaddexp(0.0, -x)  # noqa: E731
    x = (obs['cl_ne'] - S[:, 4]) / OBS['cl_ne_s']
    return dict(area=-0.5 * ((S[:, 0] - obs['area']) / OBS['area_sd']) ** 2,
                hlit=-0.5 * ((S[:, 1] - obs['hlit']) / OBS['hlit_sd']) ** 2,
                fsw=-0.5 * ((np.log(np.maximum(S[:, 10], 1e-6)) - np.log(obs['f_sw'])) / OBS['logsd']) ** 2,
                ne=lsig(x) if obs['below'] else lsig(-x))


def weights(ll, exclude=None):
    w = np.exp(ll - ll.max())
    if exclude is not None:
        w[exclude] = 0.0
    return w / w.sum()


def wq(x, w, qs):
    o = np.argsort(x); c = np.cumsum(w[o])
    return [float(x[o][min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]


def summary(x, w):
    m = float(np.sum(w * x)); s = float(np.sqrt(np.sum(w * (x - m) ** 2)))
    lo, med, hi = wq(x, w, (ALPHA / 2, 0.5, 1 - ALPHA / 2))
    return dict(mean=m, sd=s, lo=lo, med=med, hi=hi)


def var_share(x, v, w, nb=10):
    """first-order variance share Var(E[x | v]) / Var(x) under the weights w, with nb equal-weight bins of v."""
    o = np.argsort(v); c = np.cumsum(w[o]); b = np.minimum((c * nb).astype(int), nb - 1)
    mx = np.sum(w * x); vx = np.sum(w * (x - mx) ** 2)
    acc = 0.0
    for k in range(nb):
        s = o[b == k]
        if len(s) == 0:
            continue
        wk = w[s].sum()
        if wk > 0:
            acc += wk * (np.sum(w[s] * x[s]) / wk - mx) ** 2
    return float(acc / vx) if vx > 0 else 0.0


def wspearman(x, v, w):
    rx = np.argsort(np.argsort(x)) / (len(x) - 1.0); rv = np.argsort(np.argsort(v)) / (len(v) - 1.0)
    mx, mv = np.sum(w * rx), np.sum(w * rv)
    return float(np.sum(w * (rx - mx) * (rv - mv)) / np.sqrt(np.sum(w * (rx - mx) ** 2) * np.sum(w * (rv - mv) ** 2)))


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    P, S_stored, ll_stored = load_ensemble()
    N = len(P['R'])
    m = FM.Model()
    out = dict(alpha=ALPHA, N=N, cgrid=CGRID, c0=C0, betas=BETAS, obs=OBS)
    out['T25'] = t25(m, P)
    log(f'T25 state abduction: max relative error of c*phi {out["T25"]["phi_rel"]:.2e}; twin interface from the heads '
        f'alone vs re-solved: {out["T25"]["zeta_from_heads_m"]:.2e} m  [{time.time() - t0:.0f}s]')
    chunks = np.array_split(np.arange(N), 80)
    with Pool(4, initializer=_init) as pool:
        parts = pool.map(_work, chunks)
    S1 = np.vstack([a for a, _, _, _ in parts]); SC = np.vstack([b for _, b, _, _ in parts])
    SB = np.vstack([b for _, _, b, _ in parts]); mono = np.concatenate([d for _, _, _, d in parts])
    out['S1_check'] = float(np.max(np.abs(S1 - S_stored)))
    out['monotone_min_dCl'] = float(mono.min())
    log(f'ensemble recomputed (max difference to the stored summaries {out["S1_check"]:.1e}); smallest change of '
        f'shallow chloride under c < 1 over all cells and draws: {mono.min():.2e} mg/L  [{time.time() - t0:.0f}s]')
    real = dict(area=OBS['area'], hlit=OBS['hlit'], f_sw=OBS['f_sw'], cl_ne=OBS['cl_ne'], below=True)
    lp = loglik_parts(S1, real)
    ll = sum(lp.values())
    assert np.allclose(ll, ll_stored), 'likelihood differs from the calibration'
    w_post = weights(ll); w_prior = np.full(N, 1.0 / N)
    out['ess_real'] = float(1 / np.sum(w_post ** 2))
    k0 = CGRID.index(C0)

    def goal(g, Sx, Sref=S1):
        _, col, sc, _ = [G for G in GOALS if G[0] == g][0]
        return sc * (Sx[:, col] - Sref[:, col]) if Sref is not None else sc * Sx[:, col]
    # ------------------------------------------------------------------------------------------ T26
    T26 = dict(goals={}, dose={})
    for g, col, sc, lab in GOALS:
        fac = goal(g, S1, None); cf = goal(g, SC[:, k0], None); eff = cf - fac
        T26['goals'][g] = dict(label=lab, factual_prior=summary(fac, w_prior), factual_post=summary(fac, w_post),
                               cf_prior=summary(cf, w_prior), cf_post=summary(cf, w_post),
                               eff_prior=summary(eff, w_prior), eff_post=summary(eff, w_post),
                               p_increase_post=float(np.sum(w_post * (eff > 1e-12))))
        T26['dose'][g] = {str(c): dict(prior=summary(goal(g, SC[:, k]), w_prior), post=summary(goal(g, SC[:, k]), w_post))
                          for k, c in enumerate(CGRID)}
        e = T26['goals'][g]
        log(f'T26 {g}: factual post med {e["factual_post"]["med"]:.3g} [{e["factual_post"]["lo"]:.3g}, '
            f'{e["factual_post"]["hi"]:.3g}] | counterfactual c={C0} post med {e["cf_post"]["med"]:.3g} | effect '
            f'prior [{e["eff_prior"]["lo"]:.3g}, {e["eff_prior"]["hi"]:.3g}] post med {e["eff_post"]["med"]:.3g} '
            f'[{e["eff_post"]["lo"]:.3g}, {e["eff_post"]["hi"]:.3g}]')
    out['T26'] = T26
    # ------------------------------------------------------------------------------------------ T27
    rng = np.random.default_rng(27)
    idx = rng.choice(N, 600, replace=False)
    recs = []
    for j in idx:
        obs = dict(area=S1[j, 0] + OBS['area_sd'] * rng.standard_normal(),
                   hlit=S1[j, 1] + OBS['hlit_sd'] * rng.standard_normal(),
                   f_sw=np.exp(np.log(max(S1[j, 10], 1e-6)) + OBS['logsd'] * rng.standard_normal()),
                   cl_ne=OBS['cl_ne'], below=bool(rng.random() < expit((OBS['cl_ne'] - S1[j, 4]) / OBS['cl_ne_s'])))
        wj = weights(sum(loglik_parts(S1, obs).values()), exclude=j)
        recs.append(dict(j=int(j), s={g: summary(goal(g, SC[:, k0]), wj) for g, _, _, _ in GOALS},
                         cf={g: summary(goal(g, SC[:, k0], None), wj) for g, _, _, _ in GOALS}))
    cal, test = recs[:300], recs[300:]
    T27 = {}
    for g, _, _, _ in GOALS:
        truth = goal(g, SC[:, k0])
        T27[g] = {}
        for kind in ('s', 'cf'):
            tr = truth if kind == 's' else goal(g, SC[:, k0], None)
            cov_is = float(np.mean([r[kind][g]['lo'] <= tr[r['j']] <= r[kind][g]['hi'] for r in test]))
            sc_ = np.array([abs(tr[r['j']] - r[kind][g]['mean']) / max(r[kind][g]['sd'], 1e-12) for r in cal])
            n = len(sc_)
            q = float(np.sort(sc_)[min(int(np.ceil((n + 1) * (1 - ALPHA))) - 1, n - 1)])
            cov_cp = float(np.mean([abs(tr[r['j']] - r[kind][g]['mean']) <= q * r[kind][g]['sd'] for r in test]))
            w_is = float(np.mean([r[kind][g]['hi'] - r[kind][g]['lo'] for r in test]))
            w_cp = float(np.mean([2 * q * r[kind][g]['sd'] for r in test]))
            T27[g][kind] = dict(cover_is=cov_is, cover_conformal=cov_cp, q=q, width_is=w_is, width_conformal=w_cp)
            e = T26['goals'][g]['eff_post' if kind == 's' else 'cf_post']
            T27[g][kind]['real_conformal'] = [e['mean'] - q * e['sd'], e['mean'] + q * e['sd']]
        log(f'T27 {g}: effect IS coverage {T27[g]["s"]["cover_is"]:.3f} -> conformal {T27[g]["s"]["cover_conformal"]:.3f} '
            f'(q {T27[g]["s"]["q"]:.2f}); level IS {T27[g]["cf"]["cover_is"]:.3f} -> conformal '
            f'{T27[g]["cf"]["cover_conformal"]:.3f}; Fushe-Kuqe conformal effect band '
            f'[{T27[g]["s"]["real_conformal"][0]:.3g}, {T27[g]["s"]["real_conformal"][1]:.3g}]')
    out['T27'] = T27
    # ------------------------------------------------------------------------------------------ T28
    groups = dict(none=[], heads=['hlit'], chloride=['area', 'fsw', 'ne'], all=['area', 'hlit', 'fsw', 'ne'])
    T28 = dict(subsets={}, share={}, rank={}, beta={}, w_cond={})
    for gname, keys in groups.items():
        wg = weights(sum(lp[k] for k in keys)) if keys else w_prior
        T28['subsets'][gname] = {g: summary(goal(g, SC[:, k0]), wg) for g, _, _, _ in GOALS}
        T28['subsets'][gname]['ess'] = float(1 / np.sum(wg ** 2))
        T28['subsets'][gname]['w'] = summary(P['w'], wg)
    unk = dict(w=np.log(P['w']), R=np.log(P['R']), eta=P['eta'], b_c=P['b_c'], b_e=P['b_e'], L_B=P['L_B'],
               ground=P['ground'], Cl_s=P['Cl_s'])
    for g, _, _, _ in GOALS:
        eff = goal(g, SC[:, k0])
        T28['share'][g] = {k: dict(prior=var_share(eff, v, w_prior), post=var_share(eff, v, w_post)) for k, v in unk.items()}
        T28['rank'][g] = {k: wspearman(eff, v, w_post) for k, v in unk.items()}
        T28['beta'][g] = {'0': summary(eff, w_post)}
        for k, b in enumerate(BETAS):
            T28['beta'][g][str(b)] = summary(goal(g, SB[:, k]), w_post)
        # the effect for the lowest and the highest tenth of the posterior of w
        o = np.argsort(P['w']); c = np.cumsum(w_post[o])
        lo_set, hi_set = o[c <= 0.1], o[c >= 0.9]
        T28['w_cond'][g] = dict(low=summary(eff[lo_set], w_post[lo_set] / w_post[lo_set].sum()),
                                high=summary(eff[hi_set], w_post[hi_set] / w_post[hi_set].sum()))
        log(f'T28 {g}: 90% width of the effect, facts none/heads/chloride/all = ' +
            '/'.join(f'{T28["subsets"][s][g]["hi"] - T28["subsets"][s][g]["lo"]:.3g}' for s in groups) +
            ' | posterior variance shares ' + ' '.join(f'{k} {T28["share"][g][k]["post"]:.2f}' for k in unk) +
            ' | beta 0/0.25/0.5 median ' + '/'.join(f'{T28["beta"][g][b]["med"]:.3g}' for b in ('0', '0.25', '0.5')))
    out['T28'] = T28
    # ------------------------------------------------------------------------------------------ maps
    rs = np.random.default_rng(29)
    u = (np.arange(NMAP) + rs.random()) / NMAP
    pick = np.searchsorted(np.cumsum(w_post), u)
    with Pool(4, initializer=_init) as pool:
        mp = pool.map(_maps, np.array_split(pick, 40))
    E1 = sum(a for a, _ in mp) / NMAP; E0 = sum(b for _, b in mp) / NMAP
    np.savez_compressed(os.path.join(RES, 'kripa_maps.npz'), p_fact=E1, p_cf=E0, cx=m.cx, cy=m.cy, valid=m.valid,
                        dist=m.dist, dx=m.dx)
    out['maps'] = dict(area_p50_fact=float(np.sum((E1 >= 0.5) & m.valid) * m.area / 1e6),
                       area_p50_cf=float(np.sum((E0 >= 0.5) & m.valid) * m.area / 1e6))
    log(f'maps: cells with posterior exceedance probability >= 0.5: factual {out["maps"]["area_p50_fact"]:.1f} km2, '
        f'counterfactual {out["maps"]["area_p50_cf"]:.1f} km2')
    out['seconds'] = time.time() - t0
    with open(os.path.join(RES, 'kripa.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'kripa_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
