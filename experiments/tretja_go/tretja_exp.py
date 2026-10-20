"""TRETJA-GO experiment: which kinetic and field data predict calcite dissolution in the coastal mixing zone.
Writes tretja_results.json and tretja_grid.npz.   Run: python3 tretja_exp.py   (about 3 minutes)

Unknown (uniform prior on a grid): the field rate prefactor kappa (log-uniform 1e-6 - 1e-2 mmol/L/day), the
near-equilibrium reaction order n1 (0.5-2), the far-from-equilibrium order n2 (2-5) and the critical saturation of
the mechanism change Omega_c (0.6-0.9).
Goal: G, the calcite dissolved in the first kilometre of the mixing zone (mol per m of coast per year), and the
decision whether the local-equilibrium model is adequate (G >= 0.8 G_LEA).
Designs:
  LF  8 laboratory rates far from equilibrium (Omega = 0.05-0.40), the usual laboratory practice
  LN  8 laboratory rates near equilibrium (Omega = 0.60-0.95)
  LS  8 laboratory rates spread over 0.05-0.97 (a parameter-oriented choice)
  F   calcium excess at 5 depths of one multilevel well across the mixing zone at x = 500 m
  and F combined with each laboratory design.
Laboratory rates have a log-normal error of 20 % and an unknown laboratory prefactor (the laboratory-field scale
gap), so they inform only the shape of the rate law; the field data have an absolute error of 0.02 mmol/L.
"""
import json
import os
import time
import numpy as np
import tretja as T

HERE = os.path.dirname(os.path.abspath(__file__))
LK = np.linspace(-6.0, -2.0, 13)
N1 = np.linspace(0.5, 2.0, 6)
N2 = np.linspace(2.0, 5.0, 5)
OC = np.linspace(0.6, 0.9, 5)
LAB = {'LF': np.linspace(0.05, 0.40, 8), 'LN': np.linspace(0.60, 0.95, 8),
       'LS': np.array([0.05, 0.20, 0.40, 0.55, 0.70, 0.80, 0.90, 0.97])}
SIG_LAB = 0.08                       # log10 units (about 20 %)
SIG_F = {'base': 0.02, 'precise': 0.01, 'coarse': 0.05}
NDRAW = 20
FRAC_LEA = 0.8


def main():
    t0 = time.time()
    chem = T.Chem(T.load_table())
    K, A, B, C = [a.ravel() for a in np.meshgrid(LK, N1, N2, OC, indexing='ij')]
    G_ = K.size
    sims = [T.simulate(10 ** K[ix], A[ix], B[ix], C[ix], chem) for ix in np.array_split(np.arange(G_), 6)]
    obs = np.concatenate([s['obs'] for s in sims]); Gk = np.concatenate([s['G'] for s in sims])
    lea = T.simulate([1.0], [1.0], [3.0], [0.75], chem, law='lea')
    G_lea = float(lea['G'][0])
    lin_k = np.linspace(-6.0, -2.0, 41)
    lin = T.simulate(10 ** lin_k, np.ones(41), np.ones(41) * 3, np.ones(41) * 0.75, chem, law='linear')
    lin_same = T.simulate(10 ** K, A, B, C, chem, law='linear')['G'] if False else None
    print(f'forward runs {time.time() - t0:.0f}s, G_LEA = {G_lea:.2f}')
    # linear law with the same prefactor, for every grid point (structural comparison)
    lin_on_grid = np.interp(K, lin_k, lin['G'])
    eq_ok = Gk >= FRAC_LEA * G_lea
    logG = np.log10(Gk)
    # laboratory rate shapes at the design points
    hlab = {k: np.log10(T.rate_shape(np.asarray(v)[None, :], A[:, None], B[:, None], C[:, None])) for k, v in LAB.items()}
    designs = ['LF', 'LN', 'LS', 'F', 'F+LF', 'F+LN', 'F+LS']
    rng = np.random.default_rng(20261020)
    prior_H = np.log(G_)
    out = {}
    for noise, sf in SIG_F.items():
        out[noise] = {}
        for d in designs:
            sd, ok, ig, ok_lin, bias_lin = [], [], [], [], []
            for g in range(G_):
                ll = np.zeros((NDRAW, G_))
                if 'F' in d.split('+'):
                    y = obs[g][None, :] + sf * rng.standard_normal((NDRAW, obs.shape[1]))
                    ll += -0.5 * (((y[:, None, :] - obs[None, :, :]) / sf) ** 2).sum(axis=2)
                    # the linear-law model read with the same field data (kappa only)
                    lly = -0.5 * (((y[:, None, :] - lin['obs'][None, :, :]) / sf) ** 2).sum(axis=2)
                    wl = np.exp(lly - lly.max(axis=1, keepdims=True)); wl /= wl.sum(axis=1, keepdims=True)
                    gl = (wl * np.log10(lin['G'])[None, :]).sum(axis=1)
                    ok_lin.extend(((10 ** gl >= FRAC_LEA * G_lea) == eq_ok[g]).tolist())
                    bias_lin.extend((gl - logG[g]).tolist())
                for part in d.split('+'):
                    if part in LAB:
                        yl = hlab[part][g][None, :] + SIG_LAB * rng.standard_normal((NDRAW, len(LAB[part])))
                        r = yl[:, None, :] - hlab[part][None, :, :]
                        r = r - r.mean(axis=2, keepdims=True)            # unknown laboratory prefactor
                        ll += -0.5 * ((r / SIG_LAB) ** 2).sum(axis=2)
                w = np.exp(ll - ll.max(axis=1, keepdims=True)); w /= w.sum(axis=1, keepdims=True)
                m = (w * logG[None, :]).sum(axis=1)
                sd.extend(np.sqrt((w * (logG[None, :] - m[:, None]) ** 2).sum(axis=1)).tolist())
                p_ok = (w * eq_ok[None, :]).sum(axis=1)
                ok.extend(((p_ok >= 0.5) == eq_ok[g]).tolist())
                ig.extend((prior_H + np.where(w > 0, w * np.log(np.where(w > 0, w, 1)), 0).sum(axis=1)).tolist())
            rec = dict(sd_log10G=float(np.mean(sd)), correct_regime=float(np.mean(ok)), info_gain_nats=float(np.mean(ig)))
            if ok_lin:
                rec.update(linear_correct_regime=float(np.mean(ok_lin)), linear_bias_log10G=float(np.mean(bias_lin)),
                           linear_abs_bias_log10G=float(np.mean(np.abs(bias_lin))))
            out[noise][d] = rec
            print(noise, d, {k: round(v, 3) for k, v in rec.items()})
    prior = dict(sd_log10G=float(logG.std()), p_eq_ok=float(eq_ok.mean()),
                 correct_regime_prior=float(max(eq_ok.mean(), 1 - eq_ok.mean())))
    # structural comparisons over the prior grid
    struct = dict(lea_over_true_median=float(np.median(G_lea / Gk)), lea_over_true_max=float(np.max(G_lea / Gk)),
                  lea_over_true_q90=float(np.quantile(G_lea / Gk, 0.9)),
                  linear_over_true_median=float(np.median(lin_on_grid / Gk)),
                  linear_over_true_q10=float(np.quantile(lin_on_grid / Gk, 0.1)),
                  linear_over_true_q90=float(np.quantile(lin_on_grid / Gk, 0.9)),
                  frac_kinetic=float(np.mean(Gk < 0.5 * G_lea)))
    # variance decomposition of log10 G by parameter (main effects on the grid)
    LG = logG.reshape(len(LK), len(N1), len(N2), len(OC))
    tot = LG.var()
    main = {name: float(LG.mean(axis=tuple(i for i in range(4) if i != ax)).var() / tot)
            for ax, name in enumerate(['kappa', 'n1', 'n2', 'omega_c'])}
    tab = T.load_table()
    res = dict(params=dict(geom=T.GEOM, logpco2_fresh=T.LOGPCO2_FRESH, logpco2_sea=T.LOGPCO2_SEA, temp=T.TEMP,
                           log10_kappa=LK.tolist(), n1=N1.tolist(), n2=N2.tolist(), omega_c=OC.tolist(), lab=
                           {k: v.tolist() for k, v in LAB.items()}, sig_lab=SIG_LAB, sig_f=SIG_F, ndraw=NDRAW, frac_lea=FRAC_LEA),
               chem=dict(min_omega=float((10 ** tab['logom'][:, 0]).min()), f_at_min=float(tab['F'][np.argmin(tab['logom'][:, 0])]),
                         max_dsat=float(tab['dsat'].max()), fresh_pH=float(tab['fresh_pH']), sea_pH=float(tab['sea_pH']),
                         fresh_Ca=float(tab['fresh_Ca']), sea_Ca=float(tab['sea_Ca']), sea_I=float(tab['sea_I'])),
               G_lea=G_lea, G_range=[float(Gk.min()), float(Gk.max())], prior=prior, structure=struct, main_effects=main,
               designs=out)
    json.dump(res, open(os.path.join(HERE, 'tretja_results.json'), 'w'), indent=1)
    np.savez_compressed(os.path.join(HERE, 'tretja_grid.npz'), logk=K, n1=A, n2=B, omc=C, G=Gk, obs=obs,
                        lin_k=lin_k, lin_G=lin['G'], G_lea=G_lea, z=lea['z'], d_lea=lea['d_end'][0],
                        z_obs=np.array(T.GEOM['z_obs']))
    print(f'done {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
