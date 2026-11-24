"""Summary of GJURMA-GO used by review 42 -> gjurma_summary.json.
Reads gjurma_field.json (field split), gjurma_twin.json (B twin experiment, C identifiability, D non-Gaussianity)
and gjurma_real.json (E field-data illustration)."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
F = json.load(open('gjurma_field.json'))
T = json.load(open('gjurma_twin.json'))
E = json.load(open('gjurma_real.json')) if os.path.exists('gjurma_real.json') else None
S = T['setup']; MODELS = S['models']; GOALS = S['goals']
B = T['B']
R = len(B)
rng = np.random.default_rng(42)
NTRANS = 5                                    # log_sv, log_aL, logit_f0, log_amt, log_bim (first in every model)


def sig(x, n=6):
    """Round floats to n significant digits, recursively."""
    if isinstance(x, float):
        return float(f'{x:.{n}g}') if np.isfinite(x) else None
    if isinstance(x, dict):
        return {k: sig(v, n) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [sig(v, n) for v in x]
    if isinstance(x, np.ndarray):
        return sig(x.tolist(), n)
    if isinstance(x, (np.floating,)):
        return sig(float(x), n)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def boot_mean_ci(x, n=4000):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), (n, len(x)))
    m = x[idx].mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def arrays(model):
    truth = np.array([x['truth_goals'] for x in B])
    mean = np.array([x[model]['goal_mean'] for x in B])
    q05 = np.array([x[model]['goal_q05'] for x in B]); q95 = np.array([x[model]['goal_q95'] for x in B])
    return truth, mean, q05, q95


out = dict(R=R, models=MODELS, goals=GOALS)

# ------------------------------------------------------------------ field split (sheets 5 and 6)
out['field'] = dict(source=F['source'], reactions=F['reactions'], rank=F['rank'], left_null=F['left_null'],
                    cbe_pct=F['cbe_pct'], cl_trend=F['cl_trend'],
                    wells={w: dict(position=v['position'], f=v['f'], f_q=v['f_q'], delta_meq=v['delta_meq'],
                                   extents_meq=v['extents_meq'], extents_q=v['extents_q'],
                                   residual_meq=v['residual_meq'], delta_norm=v['delta_norm'])
                           for w, v in F['wells'].items()})

# ------------------------------------------------------------------ B: twin experiment
tw = {}
abserr = {}
for model in MODELS:
    truth, mean, q05, q95 = arrays(model)
    e = np.abs(mean - truth); abserr[model] = e
    cov = (q05 <= truth) & (truth <= q95)
    wid = q95 - q05
    mis = np.array([x[model]['misfit'] for x in B])
    nt = 3 if model == 'classical' else NTRANS
    tu = np.array([x['truth_u'][:nt] for x in B]); um = np.array([x[model]['u_mean'][:nt] for x in B])
    con = np.array([x[model]['contraction'][:nt] for x in B])
    tw[model] = dict(mae=e.mean(0), mae_ci=[boot_mean_ci(e[:, k]) for k in range(4)], rmse=np.sqrt((e ** 2).mean(0)),
                     cover90=cov.mean(0), width_mean=wid.mean(0), width_median=np.median(wid, 0),
                     misfit_median=float(np.median(mis)), misfit_q90=float(np.quantile(mis, 0.9)),
                     transport_rmse=np.sqrt(((um - tu) ** 2).mean(0)), transport_contraction=np.median(con, 0))
    if model in ('gjurma', 'gjurma_cut', 'free'):
        conc = np.array([x[model]['contraction'][nt:] for x in B])
        tw[model]['closure_contraction_median'] = float(np.median(conc))
    if model == 'free':
        tw[model]['abs_corr_Cl_Q_sv_median'] = float(np.median(np.abs([x['free']['corr_Cl_Q_sv'] for x in B])))
        tw[model]['abs_corr_Cl_Q_f0_median'] = float(np.median(np.abs([x['free']['corr_Cl_Q_f0'] for x in B])))
out['twin'] = tw
out['transport_names'] = S['params']['oracle'][:NTRANS]

# relative reductions of the mean absolute error and paired comparisons
pairs = [('gjurma', 'classical'), ('gjurma', 'free'), ('gjurma_cut', 'gjurma'), ('gjurma_cut', 'free'),
         ('oracle', 'gjurma'), ('free', 'classical')]
pc = {}
for a, b in pairs:
    d = abserr[a] - abserr[b]
    pc[f'{a}_vs_{b}'] = dict(frac_better=(d < 0).mean(0), mean_diff=d.mean(0),
                             mean_diff_ci=[boot_mean_ci(d[:, k]) for k in range(4)],
                             rel_reduction=1 - abserr[a].mean(0) / abserr[b].mean(0))
out['paired'] = pc

# ------------------------------------------------------------------ C: identifiability
C = T['C']
out['C'] = {m: dict(n_params=v['n_params'], informed=v['informed'], frac_informed=v['informed'] / v['n_params'],
                    eig_top=v['eig'][:8], eig_min=min(v['eig'])) for m, v in C.items()}

# ------------------------------------------------------------------ D: non-Gaussianity of the forecast (N2)
D = T['D']
x = np.array(D['x_km']); w2 = np.array(D['w2']); f = np.array(D['f_mean'])
dd = dict(argmax_w2_km=float(x[w2.argmax()]), max_w2=float(w2.max()))
if 'w2_obs' in D:
    wo = np.array(D['w2_obs']); sd = np.array(D['sd_logcl'])
    on = x[wo > 1.0]
    dd.update(argmax_w2obs_km=float(x[wo.argmax()]), max_w2obs=float(wo.max()),
              switch_km=[float(on.min()), float(on.max())] if on.size else None, switch_cells=int(on.size),
              frac_cells_switch=float(on.size / x.size),
              f_at_max=float(f[wo.argmax()]), sd_at_max=float(sd[wo.argmax()]))
    dd['at_wells'] = {w: dict(x_km=float(x[int(p // (S['L'] / S['NX']))]), w2=float(w2[int(p // (S['L'] / S['NX']))]),
                              w2_obs=float(wo[int(p // (S['L'] / S['NX']))]), f=float(f[int(p // (S['L'] / S['NX']))]))
                      for w, p in S['wells'].items()}
out['D'] = dd

# ------------------------------------------------------------------ E: field data
if E is not None:
    out['E'] = {m: dict(misfit=v['misfit'], misfit_by_ion=v['misfit_by_ion'], misfit_cl_trend=v['misfit_cl_trend'],
                        goal_mean=v['goal_mean'], goal_q05=v['goal_q05'], goal_q95=v['goal_q95'])
                for m, v in E.items() if m != "data"}

json.dump(sig(out), open('gjurma_summary.json', 'w'), indent=1)

# ------------------------------------------------------------------ print
print(f'twin experiment: {R} truths')
for model in MODELS:
    t = tw[model]
    print(f'{model:11s} MAE', np.round(t['mae'], 3), 'cover90', np.round(t['cover90'], 2), 'width', np.round(t['width_mean'], 2),
          'misfit %.2f' % t['misfit_median'], 'transport rmse', np.round(t['transport_rmse'], 2))
for k, v in pc.items():
    print(k, 'frac better', np.round(v['frac_better'], 2), 'rel reduction', np.round(v['rel_reduction'], 2))
print('C', {m: (v['n_params'], v['informed']) for m, v in C.items()})
print('D', {k: v for k, v in dd.items() if k != 'at_wells'})
if E is not None:
    for m, v in ((m, v) for m, v in E.items() if m != "data"):
        print('E', m, 'misfit %.2f' % v['misfit'], {k: round(z, 1) for k, z in v['misfit_by_ion'].items()},
              'Cl trend %.1f' % v['misfit_cl_trend'])
