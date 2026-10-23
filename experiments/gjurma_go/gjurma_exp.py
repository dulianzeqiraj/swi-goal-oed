"""GJURMA-GO experiments on the 1D coastal flow line (gjurma_model.py).
  B  twin experiment: R synthetic truths drawn from the oracle prior; the sampling design of the field data (major ions
     at four wells in 2016, Cl at wells 503 and 341 in 1984, 1999 and 2001); four models fitted by the ensemble
     smoother with multiple data assimilation (ES-MDA); goals in 2045: Cl at the well field (5 km), Na and hardness
     (Ca + Mg) at 3 km, and the length of the coastal strip with Cl above 250 mg/L.
  C  identifiability: Fisher information of the 34 data in prior-standardised parameters for the free and the
     stoichiometric closure (and the oracle), at the base truth.
  D  non-Gaussianity of the forecast (proposal N2): distance of the standardised ensemble of Cl in 2016 from N(0, 1)
     along the flow line.
  E  illustration on the field data (sheets 5 and 6), with the assumed geometry and pumping history.
Writes gjurma_twin.json (B, C, D) and gjurma_real.json (E). `python3 gjurma_exp.py B` etc. runs one part.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time
import numpy as np
from multiprocessing import Pool
import gjurma_model as G
import gjurma_field as GF

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
NE, NA, R = 100, 4, 40
SIG_OBS = 0.05                                               # 5% (log scale)
OBS_WELLS = ['503', '341', '340', '193']
CL_TREND = [('503', 1984.0), ('503', 1999.0), ('503', 2001.0), ('341', 1984.0), ('341', 1999.0), ('341', 2001.0)]
OBS_TIMES = [1984.0, 1999.0, 2001.0, 2016.0, 2045.0]
logit = lambda p: np.log(p / (1 - p)); expit = lambda x: 1 / (1 + np.exp(-x))

COMMON = [('log_sv', 0.0, 0.3), ('log_aL', np.log(150.0), 0.4), ('logit_f0', logit(0.07), 0.35)]
MEMORY = [('log_amt', np.log(0.1), 0.6), ('log_bim', np.log(0.5), 0.4)]
ORACLE = [('log_E', np.log(60.0), 0.4), ('log_KK', np.log(0.2), 0.25), ('log_KC', np.log(0.4), 0.25),
          ('log_KM', np.log(0.5), 0.25), ('log_ksr', np.log(0.05), 0.6)]
GJ = [('NaCa_logQ', np.log(15.0), 0.8), ('NaCa_logh', np.log(0.02), 0.8), ('NaCa_logtau', np.log(5.0), 0.8),
      ('NaMg_logQ', np.log(15.0), 0.8), ('NaMg_logh', np.log(0.02), 0.8), ('NaMg_logtau', np.log(5.0), 0.8),
      ('KCa_logQ', np.log(1.0), 0.8), ('KCa_logh', np.log(0.02), 0.8), ('KCa_logtau', np.log(5.0), 0.8),
      ('log_sr', np.log(0.03), 1.0), ('calcite', 0.0, 0.3)]
QS = dict(zip(G.SPECIES, [10.0, 20.0, 1.0, 10.0, 10.0, 3.0, 3.0]))
FREE = [(f'{sp}_{k}', m, s) for sp in G.SPECIES
        for k, m, s in (('logQ', np.log(QS[sp]), 0.8), ('logh', np.log(0.02), 0.8), ('logtau', np.log(5.0), 0.8),
                        ('sign', 0.0, 1.0), ('b', 0.0, 0.05))]
PARAMS = {'classical': COMMON, 'free': COMMON + MEMORY + FREE, 'gjurma': COMMON + MEMORY + GJ, 'oracle': COMMON + MEMORY + ORACLE}
MODELS = ['classical', 'free', 'gjurma', 'gjurma_cut', 'oracle']


def prior(model):
    spec = PARAMS[model]
    return np.array([m for _, m, _ in spec], float), np.array([s for _, _, s in spec], float)


def to_P(model, U):
    """Ensemble of transformed parameters (Ne, p) -> simulator dict."""
    names = [n for n, _, _ in PARAMS[model]]
    u = {n: U[:, i] for i, n in enumerate(names)}
    P = dict(s_v=np.exp(u['log_sv']), alpha_L=np.exp(u['log_aL']), f0=expit(u['logit_f0']))
    if model != 'classical':
        P.update(a_mt=np.exp(u['log_amt']), b_im=np.exp(u['log_bim']))
    if model == 'oracle':
        P.update(E=np.exp(u['log_E']), logK=np.stack([u['log_KK'], u['log_KC'], u['log_KM']], 1), k_sr=np.exp(u['log_ksr']))
    if model == 'gjurma':
        P['theta'] = U[:, [names.index(n) for n, _, _ in GJ]]
    if model == 'free':
        P['theta'] = U[:, [names.index(n) for n, _, _ in FREE]]
    return P


def run(model, U):
    sim = 'truth' if model == 'oracle' else model
    return G.simulate(to_P(model, U), sim, obs_times=OBS_TIMES)


def observe(out):
    """Log concentrations (mg/L) of the 34 data: 7 ions at four wells in 2016, then the Cl trend."""
    c16 = out[2016.0]
    y = [np.log(c16[:, G.I_W[w], :] * G.MW) for w in OBS_WELLS]
    y += [np.log(out[t][:, G.I_W[w], G.I_CL] * G.MW[G.I_CL])[:, None] for w, t in CL_TREND]
    return np.concatenate(y, 1)


def goals(out):
    """Goals in 2045: Cl at 5 km (mg/L), Na at 3 km (mg/L), hardness Ca + Mg at 3 km (meq/L), length with Cl > 250."""
    c = out[2045.0]
    i5, i3 = int(5000 // G.DX), int(3000 // G.DX)
    cl = c[..., G.I_CL] * G.MW[G.I_CL]
    return np.stack([cl[:, i5], c[:, i3, G.I_NA] * G.MW[G.I_NA], 2 * (c[:, i3, G.I_CA] + c[:, i3, G.I_MG]),
                     (cl > 250.0).sum(1) * G.DX / 1000.0], 1)


GOALS = ['Cl at 5 km (mg/L)', 'Na at 3 km (mg/L)', 'Ca + Mg at 3 km (meq/L)', 'strip with Cl > 250 mg/L (km)']


def esmda(model, d, rng, ne=NE, na=NA, U=None, upd=None, obs=None):
    """ES-MDA; upd = indices of the parameters updated (default all), obs = indices of the data used (default all)."""
    m, s = prior(model)
    if U is None:
        U = m + s * rng.standard_normal((ne, m.size))
    upd = np.arange(m.size) if upd is None else np.asarray(upd)
    obs = np.arange(d.size) if obs is None else np.asarray(obs)
    for it in range(na):
        Y = observe(run(model, U))
        bad = ~np.isfinite(Y).all(1)
        if bad.any():                                        # replace failed members by perturbed good ones
            good = np.where(~bad)[0]
            U[bad] = U[rng.choice(good, bad.sum())] + 0.05 * s * rng.standard_normal((bad.sum(), m.size))
            Y = observe(run(model, U))
        Yo = Y[:, obs]
        du = U[:, upd] - U[:, upd].mean(0); dy = Yo - Yo.mean(0)
        Cuy = du.T @ dy / (ne - 1); Cyy = dy.T @ dy / (ne - 1)
        Gm = Cyy + na * SIG_OBS ** 2 * np.eye(obs.size)
        Dp = d[obs] + np.sqrt(na) * SIG_OBS * rng.standard_normal((ne, obs.size))
        U[:, upd] = U[:, upd] + (np.linalg.solve(Gm, (Dp - Yo).T).T @ Cuy.T)
        U = np.clip(U, m - 6 * s, m + 6 * s)
    out = run(model, U)
    return U, observe(out), goals(out), out


CL_OBS = np.array([7 * k + G.I_CL for k in range(len(OBS_WELLS))] + list(range(7 * len(OBS_WELLS), 7 * len(OBS_WELLS) + len(CL_TREND))))


def esmda_cut(d, rng, ne=NE, na=NA):
    """GJURMA with a cut: transport and memory from the Cl data alone (Cl is closure-free), then the stoichiometric
    closure from all data with each member's transport and memory held fixed."""
    m, s = prior('gjurma')
    U = m + s * rng.standard_normal((ne, m.size))
    ntm = len(COMMON) + len(MEMORY)
    U, _, _, _ = esmda('gjurma', d, rng, ne, na, U=U, upd=np.arange(ntm), obs=CL_OBS)
    return esmda('gjurma', d, rng, ne, na, U=U, upd=np.arange(ntm, m.size))


def truth_draw(rng):
    m, s = prior('oracle')
    return (m + s * rng.standard_normal(m.size))[None, :]


def one_B(r):
    rng = np.random.default_rng(9100 + r)
    Ut = truth_draw(rng)
    out_t = run('oracle', Ut)
    y_true = observe(out_t)[0]
    d = y_true + SIG_OBS * rng.standard_normal(y_true.size)
    gt = goals(out_t)[0]
    res = dict(truth_goals=gt.tolist(), truth_u=Ut[0].tolist())
    for model in MODELS:
        if model == 'gjurma_cut':
            U, Y, Gs, _ = esmda_cut(d, np.random.default_rng(5000 + r))
            m, s = prior('gjurma')
        else:
            U, Y, Gs, _ = esmda(model, d, np.random.default_rng(5000 + r))
            m, s = prior(model)
        res[model] = dict(goal_mean=Gs.mean(0).tolist(), goal_q05=np.quantile(Gs, 0.05, 0).tolist(),
                          goal_q95=np.quantile(Gs, 0.95, 0).tolist(), misfit=float(np.sqrt(((Y.mean(0) - d) ** 2).mean()) / SIG_OBS),
                          contraction=(U.std(0) / s).tolist(), u_mean=U.mean(0).tolist())
        if model == 'free':
            names = [n for n, _, _ in PARAMS['free']]
            i1, i2 = names.index('Cl_logQ'), names.index('log_sv')
            res[model]['corr_Cl_Q_sv'] = float(np.corrcoef(U[:, i1], U[:, i2])[0, 1])
            res[model]['corr_Cl_Q_f0'] = float(np.corrcoef(U[:, i1], U[:, names.index('logit_f0')])[0, 1])
    return res


def fisher(model, h=0.02):
    """Eigenvalues of J'J / sigma^2 in prior-standardised parameters at the prior mean (base truth for the oracle)."""
    m, s = prior(model)
    p = m.size
    Z = np.vstack([np.zeros(p)] + [h * np.eye(p)[j] for j in range(p)] + [-h * np.eye(p)[j] for j in range(p)])
    Y = observe(run(model, m + Z * s))
    J = ((Y[1:p + 1] - Y[p + 1:]) / (2 * h)).T                  # (data, parameters)
    ev = np.linalg.eigvalsh(J.T @ J / SIG_OBS ** 2)[::-1]
    return ev


def part_C():
    out = {}
    for model in ('free', 'gjurma', 'oracle'):
        ev = fisher(model)
        out[model] = dict(n_params=int(ev.size), informed=int((ev > 1.0).sum()), eig=ev.tolist())
        print(model, 'parameters', ev.size, 'informed directions', int((ev > 1).sum()), 'top', np.round(ev[:5], 1), flush=True)
    return out


def part_D():
    rng = np.random.default_rng(77)
    m, s = prior('oracle')
    U = m + s * rng.standard_normal((400, m.size))
    out = G.simulate(to_P('oracle', U), 'truth', obs_times=[2016.0])
    cl = np.log(out[2016.0][..., G.I_CL] * G.MW[G.I_CL])          # (400, NX)
    sd = cl.std(0)
    z = (cl - cl.mean(0)) / np.maximum(sd, 1e-12)
    q = (np.arange(400) + 0.5) / 400
    from scipy.stats import norm
    w2 = np.sqrt(((np.sort(z, 0) - norm.ppf(q)[:, None]) ** 2).mean(0))
    # the same distance in units of the observation error: W2 between the forecast of log Cl and its Gaussian fit,
    # divided by the error of a log-Cl measurement (scale-free W2 flags cells whose forecast is almost certain)
    w2_obs = sd * w2 / SIG_OBS
    f_mean = ((np.exp(cl) / G.MW[G.I_CL] - G.FRESH[G.I_CL]) / (G.SEA[G.I_CL] - G.FRESH[G.I_CL])).mean(0)
    return dict(x_km=(G.XC / 1000).tolist(), w2=w2.tolist(), sd_logcl=sd.tolist(), w2_obs=w2_obs.tolist(),
                f_mean=f_mean.tolist())


def part_E():
    S5 = GF.read_sheet5(); S6 = GF.read_sheet6()
    ions = G.SPECIES
    d = [np.log(np.array(S5[w][0])) for w in OBS_WELLS]
    d += [np.array([np.log(S6[w][int(t)])]) for w, t in CL_TREND]
    d = np.concatenate(d)
    out = {}
    for model in MODELS:
        if model == 'gjurma_cut':
            U, Y, Gs, sim = esmda_cut(d, np.random.default_rng(31))
        else:
            U, Y, Gs, sim = esmda(model, d, np.random.default_rng(31))
        resid = (Y.mean(0) - d)[:28].reshape(4, 7)
        out[model] = dict(misfit=float(np.sqrt(((Y.mean(0) - d) ** 2).mean()) / SIG_OBS),
                          misfit_by_ion={ion: float(np.sqrt((resid[:, k] ** 2).mean()) / SIG_OBS) for k, ion in enumerate(ions)},
                          misfit_cl_trend=float(np.sqrt(((Y.mean(0) - d)[28:] ** 2).mean()) / SIG_OBS),
                          goal_mean=Gs.mean(0).tolist(), goal_q05=np.quantile(Gs, 0.05, 0).tolist(),
                          goal_q95=np.quantile(Gs, 0.95, 0).tolist(), u_mean=U.mean(0).tolist(), u_sd=U.std(0).tolist(),
                          names=[n for n, _, _ in PARAMS['gjurma' if model == 'gjurma_cut' else model]],
                          y_mean=Y.mean(0).tolist(), y_q05=np.quantile(Y, 0.05, 0).tolist(),
                          y_q95=np.quantile(Y, 0.95, 0).tolist())
        print(model, 'misfit %.2f' % out[model]['misfit'], {k: round(v, 1) for k, v in out[model]['misfit_by_ion'].items()}, flush=True)
    out['data'] = dict(d=d.tolist(), wells=OBS_WELLS, ions=ions, cl_trend=[[w, t] for w, t in CL_TREND])
    return out


if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'BCDE'
    t0 = time.time()
    res = json.load(open('gjurma_twin.json')) if os.path.exists('gjurma_twin.json') else {}
    res['setup'] = dict(NE=NE, NA=NA, R=R, sig_obs=SIG_OBS, goals=GOALS, models=MODELS, wells=G.WELLS, obs_wells=OBS_WELLS,
                        cl_trend=[[w, t] for w, t in CL_TREND], params={k: [n for n, _, _ in v] for k, v in PARAMS.items()},
                        L=G.L, NX=G.NX, X_P=G.X_P, years=[G.T0, G.T1])
    if 'C' in part:
        res['C'] = part_C()
    if 'D' in part:
        res['D'] = part_D()
    if 'B' in part:
        with Pool(4) as pool:
            res['B'] = pool.map(one_B, range(R), chunksize=1)
        for model in MODELS:
            err = np.array([[x[model]['goal_mean'][k] - x['truth_goals'][k] for k in range(4)] for x in res['B']])
            cov = np.array([[x[model]['goal_q05'][k] <= x['truth_goals'][k] <= x[model]['goal_q95'][k] for k in range(4)] for x in res['B']])
            print(model, 'rmse', np.round(np.sqrt((err ** 2).mean(0)), 2), 'cover90', np.round(cov.mean(0), 2), flush=True)
    if any(p in part for p in 'BCD'):
        json.dump(res, open('gjurma_twin.json', 'w'))
    if 'E' in part:
        json.dump(part_E(), open('gjurma_real.json', 'w'), indent=1)
    print('done in %.0f s' % (time.time() - t0))
