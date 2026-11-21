"""Text of the review "From chaos in the pores to Darcy's law" (English).  blocks(R) returns the block list; every number
of the experiment comes from res/kaos.json (R), every reference from res/refs.json.  Conventions: $inline math$, **bold**,
*italic*, ==yellow placeholder==, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import copy
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cards_kaos import CARDS, INST_ORDER, ROUTES  # noqa: E402

RES = os.path.join(HERE, 'res')
with open(os.path.join(RES, 'refs.json'), encoding='utf-8') as _fh:
    REFS = json.load(_fh)

TITLE_FIX = {'S2': 'Homogenization of the Stokes flow in a connected porous medium',
             'S49': 'Lyapunov characteristic exponents for smooth dynamical systems and for Hamiltonian systems; a method '
                    'for computing all of them. Part 1: Theory'}
NAME_FIX = {"d'Humi\ufffdres": "d'Humières"}
JOURNAL_FIX = {'S4': 'In J. Bear & M. Y. Corapcioglu (eds), Fundamentals of Transport Phenomena in Porous Media, Springer'}
WEB = [
    dict(key='A6', text='California Institute of Technology, Division of Chemistry and Chemical Engineering: faculty page '
                        'of Sujit S. Datta, and the curriculum vitae on the site of the group (Caltech from September '
                        '2024, Princeton University 2017–2024). Seen through search results, November 2026.',
         url='https://cce.caltech.edu/people/sujit-datta'),
]
OWN = [
    dict(key='D1', text='Zeqiraj, D. (2026). certain-coast: open-source tools for coastal aquifers (MATLAB and GNU Octave; '
                        'variable-density solver with adjoints, goal-oriented design, calibration under misspecification).',
         url='https://github.com/dulianzeqiraj/certain-coast'),
    dict(key='D2', text='Zeqiraj, D. (2026). SALTPROOF: certified decisions for coastal aquifers when every model is wrong. '
                        'ERC-2027-CoG, Part B1, draft of November 2026 (certificates by conformal calibration of '
                        'experiments predicted in advance, transported to a decision by adjoints).', url=None),
    dict(key='D3', text='Zeqiraj, D. (2026). SC-PDE-FIND: equation learning with stability selection, conformal intervals '
                        'and goal-oriented c-optimal design (Section 9 of the note on non-Bayesian equation learning, '
                        '2020–2026).', url=None),
    dict(key='D4', text='The code and results of this review: experiments/kaos_go/ (lbm.py, kaos_run.py, kaos_gates.py, '
                        'kaos_rev.py, kaos_exp.py, kaos_figs.py; results in res/).', url=None),
]


def ref_text(key):
    r = REFS[key]
    au = r['authors']
    def fam(f):
        f = NAME_FIX.get(f, f)
        return f.title() if f.isupper() and len(f) > 2 else f
    names = [f"{fam(a['family'])}, {''.join(p[0] + '.' for p in a['given'].replace('-', ' ').split() if p)}".rstrip(', ') for a in au]
    if len(names) > 8:
        names = names[:7] + ['… ' + names[-1]]
    s = (', '.join(names[:-1]) + ' & ' + names[-1]) if len(names) > 1 else names[0]
    title = TITLE_FIX.get(key, r['title']).rstrip('.')
    j = JOURNAL_FIX.get(key, r['journal'])
    tail = j
    if r.get('volume') and key not in JOURNAL_FIX:
        tail += f" {r['volume']}"
        if r.get('issue'):
            tail += f"({r['issue'].replace('-', '–')})"
    if r.get('page'):
        tail += f", {r['page'].replace('-', '–')}"
    return f"{s} ({r['year']}). {title}. {tail}."


def card_ref(c):
    venue = re.sub(r'\s*\(\d{4}[^)]*\)$', '', c['venue'])
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {venue}.", url=c['links'][0][1])


def all_refs():
    out = [dict(key=k, text=ref_text(k), url='https://doi.org/' + REFS[k]['doi']) for k in REFS if k.startswith('A')]
    out += WEB
    out += [card_ref(c) for c in CARDS]
    out += [dict(key=k, text=ref_text(k), url='https://doi.org/' + REFS[k]['doi'])
            for k in sorted((k for k in REFS if k.startswith('S')), key=lambda k: int(k[1:]))]
    return out + OWN


def pct(x, d=0):
    return f'{100 * x:.{d}f}%'


def num(x, d=2):
    return f'{x:.{d}f}'.replace('-', '−')


def at_re(lev, key, re):
    """log-linear interpolation of a level quantity at a Reynolds number."""
    x = np.log([r['Re'] for r in lev]); y = np.array([r[key] for r in lev])
    return float(np.interp(np.log(re), x, y))


def fill_numbers(R):
    s = {}
    lev = R['levels']
    hi = lev[-1]
    uns = [r for r in lev if r['unsteady']]
    cha = [r for r in lev if r['chaotic']]
    s['n_lev'] = str(len(lev)); s['n_uns'] = str(len(uns)); s['n_cha'] = str(len(cha))
    s['re_lo'] = num(lev[0]['Re'], 2); s['re_hi'] = num(hi['Re'], 0)
    s['K0'] = num(R['K0'], 3)
    rng_ = lambda key: (num(min(r[key] for r in uns if key in r), 0), num(max(r[key] for r in uns if key in r), 0))
    s['samp_lo'], s['samp_hi'] = rng_('samp_transits')
    s['spin_lo'], s['spin_hi'] = rng_('spin_transits')
    s['lyapT_lo'], s['lyapT_hi'] = rng_('lyap_transits')
    s['F_hi'] = num(hi['F'], 1); s['F27'] = num(at_re(lev, 'F', 27.0), 2); s['F10'] = num(at_re(lev, 'F', 10.0), 2)
    s['F1'] = num(at_re(lev, 'F', 1.0), 3)
    s['Fmean_hi'] = num(hi['F_mean'], 1); s['Ffluct_hi'] = num(hi['F_fluct'], 1)
    s['fluct_share_hi'] = pct(hi['fluct_share'] / hi['budget']); s['mean_share_hi'] = pct(hi['mean_share'] / hi['budget'])
    s['budget_worst'] = pct(max(abs(r['budget'] - 1) for r in lev), 1)
    s['budget_hi'] = pct(abs(hi['budget'] - 1), 1)
    o = R['onset_unsteady']; s['onset_lo'] = num(o[0], 0); s['onset_hi'] = num(o[1], 0)
    oc = R.get('onset_chaos')
    s['chaos_lo'] = num(oc[0], 0) if oc else '—'; s['chaos_hi'] = num(oc[1], 0) if oc else '—'
    ly = [r for r in lev if 'lyap_T' in r]
    s['lyap_hi'] = num(hi.get('lyap_T', float('nan')), 2); s['lyap_hi_se'] = num(hi.get('lyap_T_se', float('nan')), 2)
    s['lyap_max'] = num(max(r['lyap_T'] for r in ly), 2) if ly else '—'
    s['patch_lo'] = pct(uns[0]['unsteady_share']) if uns else '—'; s['patch_hi'] = pct(hi.get('unsteady_share', 0))
    gu = [(r['Re'], r['grains_unsteady']) for r in uns if 'grains_unsteady' in r]
    if gu:
        ng = len(uns[0]['grain_tke'])
        s['grains_lo'] = str(gu[0][1]); s['grains_n'] = str(ng)
        full = next((re_ for re_, g in gu if g == ng), None)
        s['grains_full_re'] = num(full, 0) if full else '—'
        s['re_uns_lo'] = num(gu[0][0], 0)
        part = [(re_, g) for re_, g in gu if g < ng]
        s['grain_list'] = ', '.join(f'{g} at Re = {num(re_, 0)}' for re_, g in part)
    s['tke_hi'] = pct(hi['tke_ratio']); s['cv_hi'] = pct(hi['U_cv'], 1)
    s['half_area_lo'] = pct(lev[0].get('half_dissipation_area', float('nan'))); s['half_area_hi'] = pct(hi.get('half_dissipation_area', float('nan')))
    g = R.get('gates')
    if g:
        low = [r for r in g['rows'] if r['Re'] < 1.0]
        d10 = [abs(r['k_sim'] / r['k_SA_nominal'] - 1) for r in low if r['c_nominal'] < 0.15]
        d20 = [abs(r['k_sim'] / r['k_SA_nominal'] - 1) for r in low if r['c_nominal'] >= 0.15]
        s['gate_drag10'] = pct(max(d10), 1); s['gate_drag20'] = f'{100 * min(d20):.1f}–{100 * max(d20):.1f}%'
        s['gate_budget'] = pct(g['budget_dev_max'], 1)
    cv = sorted((r for r in R['conv'] if r['G'] == 1152), key=lambda r: r['a'])
    sg = lambda x: f'{100 * x:+.1f}%'.replace('-', '−')
    s['conv_rows'] = [[f"{r['a']:.0f}", f"{r['L']}", num(r['Re'], 0), num(r['Kstar'], 4), sg(r['budget'] - 1),
                       pct(r['mean_share'] / r['budget']), pct(r['tke_ratio']), f"{num(r['lyap_T'], 2)} ± {num(r['lyap_T_se'], 2)}"]
                      for r in cv]
    if len(cv) >= 2:
        s['conv_K'] = pct(abs(cv[-1]['Kstar'] / cv[-2]['Kstar'] - 1), 1); s['conv_K12'] = pct(abs(cv[-1]['Kstar'] / cv[0]['Kstar'] - 1), 1)
        s['conv_lyap'] = ', '.join(num(r['lyap_T'], 2) for r in cv)
        s['conv_budget'] = ', '.join(sg(r['budget'] - 1) for r in cv)
    sgp = os.path.join(RES, 'stats_gate.json')
    if os.path.exists(sgp):
        with open(sgp) as fh:
            SG = [r for r in json.load(fh) if r['tau'] <= 8]     # the cases run before the long runs were analysed
        cf = [r[k] for r in SG for k in ('conformal_50', 'conformal_200')]
        s['sg_conf'] = f'{100 * min(cf):.0f}–{100 * max(cf):.0f}%'
        s['sg_gk50'] = f"{100 * min(r['gk_50'] for r in SG):.0f}–{100 * max(r['gk_50'] for r in SG):.0f}%"
        s['sg_naive'] = f"{100 * min(r['naive_200'] for r in SG):.0f}–{100 * max(r['naive_200'] for r in SG):.0f}%"
    rv = R.get('rev')
    if rv:
        for r in rv['rows']:
            s[f"rev_cv{r['n']}"] = pct(r['cv'], 1); s[f"rev_m{r['n']}"] = str(r['m']); s[f"rev_K{r['n']}"] = num(r['mean'], 3)
        s['rev_slope'] = num(rv['slope'], 2)
        r16 = next(r for r in rv['rows'] if r['n'] == 16)
        s['cell_z'] = num(abs(R['K0'] - r16['mean']) / r16['sd'], 1)
        s['rev_bias'] = ('+' if rv['bias_small'] > 0 else '−') + pct(abs(rv['bias_small']), 1); s['rev_bias_se'] = pct(rv['bias_small_se'], 1)
    lg = R.get('long') or []
    s['slow_re'] = num(max(lg, key=lambda r: r['tau_int'])['Re'], 0) if lg else '—'
    s['slow_tau'] = num(max(r['tau_int'] for r in lg), 0) if lg else '—'
    for key in ('naive', 'gk', 'conformal'):
        v = [w[key] for r in lg for w in r['windows'] if w[key] is not None]
        s['rng_' + key] = f'{pct(min(v))} to {pct(max(v))}' if v else '—'
    if lg:
        s['long_n'] = str(len(lg)); s['long_T'] = num(min(r['transits'] for r in lg), 0)
        s['long_re'] = ' and '.join(num(r['Re'], 0) for r in lg)
        s['tau'] = ' and '.join(num(r['tau_int'], 1) for r in lg)
        s['slope'] = ' and '.join(num(r['scaling_slope'], 2) for r in lg)
        s['sd10'] = ' and '.join(pct(next(w['sd_rel_window'] for w in r['windows'] if w['W'] == 10 and w['burn'] == 200), 2) for r in lg)
        c = R['coverage']
        for k in c:
            s['cov_' + k] = pct(c[k]['cov']); s['n_' + k] = str(c[k]['n'])
        s['cov_naive'] = s.get('cov_naive_200', s.get('cov_naive_50', '—'))
    cl = R['closures']
    f = cl.get('Forchheimer, 1 + b Re')
    if f and f.get('extrapolation_max') is not None:
        s['forch_err'] = pct(f['extrapolation_max']); s['forch_loo'] = pct(f['loo_rms'], 1)
    best = min((k for k in cl if 'loo_rms' in cl[k]), key=lambda k: cl[k]['loo_rms'])
    law_tex = {'Forchheimer, 1 + b Re': '$F=1+b\\,\\mathrm{Re}$', 'weak inertia, 1 + c Re^2': '$F=1+c\\,\\mathrm{Re}^{2}$',
               '1 + b Re + c Re^2': '$F=1+b\\,\\mathrm{Re}+c\\,\\mathrm{Re}^{2}$', 'power law, 1 + k Re^m': '$F=1+k\\,\\mathrm{Re}^{m}$'}
    s['best_law'] = law_tex[best]; s['best_loo'] = pct(cl[best]['loo_rms'], 1)
    d = R['decision']
    s['I'] = num(d['I'], 2); s['Re_w'] = num(d['Re_w'], 0)
    if 'gain' in d:
        s['alloc_gain'] = pct(d['gain']); s['sd_equal'] = pct(d['sd_equal'] / d['I'], 2); s['sd_opt'] = pct(d['sd_opt'] / d['I'], 2)
        s['Wtot'] = num(d['Wtot'], 0)
    if 'sd_cell' in d:
        s['sd_cell'] = pct(d['sd_cell'] / d['I'], 1)
    return s


def filled_cards(s):
    out = copy.deepcopy(CARDS)
    for c in out:
        for k in ('does', 'route', 'gap', 'step'):
            for key, val in s.items():
                if isinstance(val, str):
                    c[k] = c[k].replace(f'<<{key}>>', val)
            if os.environ.get('KAOS_DRAFT'):                     # a draft before all runs are in: mark what is missing
                c[k] = re.sub(r'<<(\w+)>>', r'==\1==', c[k])
            assert '<<' not in c[k], (c['id'], k, c[k])
    return out



def time_block(A, R, s, lev):
    """Section 7.3, the statistics of the flux in time: the long runs, level by level, and the coverage test."""
    longs = sorted(R['long'], key=lambda r: r['Re'])
    re_ = lambda r: num(r['Re_level'], 0)
    sdW = lambda r, W: pct(next(x['var_rel'] for x in r['scaling'] if x['W'] == W) ** 0.5, 2)
    nW = lambda r, W: next(x['n'] for x in r['scaling'] if x['W'] == W)
    asyW = lambda r, W: pct((r['lrv_rel'] / W) ** 0.5, 2)
    acf = lambda r, lag: num(next(x['rho'] for x in r['acf'] if x['lag'] == lag), 2)
    lyt = lambda r: 1.0 / r['lyap_T_level']                       # predictability time, from the sweep
    below = lambda r, W: pct(1 - (next(x['var_rel'] for x in r['scaling'] if x['W'] == W) / (r['lrv_rel'] / W)) ** 0.5)
    unc = lambda r, W: pct(1 / (2 * (nW(r, W) - 1)) ** 0.5)       # relative standard error of a standard deviation
    slow = max(longs, key=lambda r: r['tau_int'])
    fast = min(longs, key=lambda r: r['tau_int'])
    assert fast is not slow
    SG = {r['tau']: r for r in json.load(open(os.path.join(RES, 'stats_gate.json')))}
    A(('p', f'**The central limit in time** (Figure {{{{clt}}}}). Two chaotic levels, Re = '
            f'{" and ".join(re_(r) for r in longs)}, were run for '
            f'{num(min(r["transits"] for r in longs), 0)} and {num(max(r["transits"] for r in longs), 0)} transit times '
            f'(their mean flux agrees with that of the sweep within '
            f'{pct(max(abs(r["U_over_sweep"] - 1) for r in longs), 1)}). They behave differently, and the difference is '
            f'the most instructive result of the experiment.'))
    A(('p', f'*At Re = {re_(fast)} the chaos is fast.* The largest Lyapunov exponent gives a predictability time '
            f'(the time over which a small error grows by a factor e) of {num(lyt(fast), 0)} transit times, and the '
            f'flux has an integrated correlation time of {num(fast["tau_int"], 1)}. The scatter of its window means '
            f'falls from {sdW(fast, 5)} of the flux over 5 transit times to {sdW(fast, 80)} over 80, with exponent '
            f'{num(fast["scaling_slope"] / 2, 2)} in the window length (central limit: −0.5). From windows of about 20 '
            f'transit times on, the prediction of the measured autocovariance joins the line '
            f'$\\sigma_{{\\infty}}/\\sqrt{{T}}$ of Proposition 2 (Figure {{{{clt}}}}b). The measured scatter at 20, 40 '
            f'and 80 transit times lies {below(fast, 20)}, {below(fast, 40)} and {below(fast, 80)} below that line; '
            f'with {nW(fast, 20)}, {nW(fast, 40)} and {nW(fast, 80)} windows it is uncertain by {unc(fast, 20)}, '
            f'{unc(fast, 40)} and {unc(fast, 80)}.'))
    seg = slow['tau_segments']
    A(('p', f'*At Re = {re_(slow)}, the first chaotic level, the chaos is slow* (predictability time '
            f'{num(lyt(slow), 0)} transit times), and the flux keeps a memory: an integrated correlation time of '
            f'{num(slow["tau_int"], 0)} transit times, with a correlation that is still {acf(slow, 40)} at a lag of 40 '
            f'and {acf(slow, 80)} at 80. Its window means hardly sharpen: {sdW(slow, 5)} over 5 transit times and '
            f'{sdW(slow, 80)} over 80 (exponent {num(slow["scaling_slope"] / 2, 2)}), and the central-limit line, '
            f'{asyW(slow, 80)} at 80 transit times, is not reached within the windows tested. A record of 200 transit '
            f'times, the length of a sweep run, does not see this memory: {len(seg)} consecutive records of that length '
            f'give correlation times between {num(min(seg), 0)} and {num(max(seg), 0)}. '
            f'{pct(slow["slow_share"])} of the variance of the flux lies at periods longer than 20 transit times; a '
            f'likely reason is that the wakes of the grains, which share one frequency at the periodic levels, now '
            f'drift slowly against each other. This is the first failure mode named after Proposition 2, here measured. '
            f'Near its onset the chaos is slow, and in this experiment it is the *rate* of the chaos, not its '
            f'presence, that makes the average sharp.'))
    C = R['coverage']
    g = lambda c, k: (pct(c[k]['cov']) if k in c else '—')
    per_level = '; '.join(
        f'at Re = {re_(r)} they cover {g(r["coverage"], "naive_200")}, {g(r["coverage"], "gk_200")} and '
        f'{g(r["coverage"], "conformal_200")}' for r in longs)
    short = ', and '.join(
        f'{g(r["coverage"], "gk_50")} and {g(r["coverage"], "conformal_50")} at Re = {re_(r)}' for r in longs)
    A(('p', f'**The certificate** (Table {{{{cov}}}}, Figure {{{{clt}}}}c). The mean flux of each next window of 5, 10 or '
            f'20 transit times is predicted from the record so far, with a nominal 90% interval, after a first record '
            f'of 200 transit times. Three intervals are compared: one that takes the flow to forget itself after one '
            f'pore transit, one with the measured correlation (the fluctuation term of [[closure]] on the '
            f'central-limit line), and the conformal one of [[cert]]. Pooled over both levels, as fixed in advance '
            f'({C["gk_200"]["n"]} windows), they cover {g(C, "naive_200")}, {g(C, "gk_200")} and '
            f'{g(C, "conformal_200")}. The pooled figure hides what the levels show apart: {per_level}. When the '
            f'first record is short (50 transit times) the intervals with the measured correlation and the conformal '
            f'ones cover {short}.'))
    cells = [w for r in longs for w in r['windows']]
    rng = lambda key: f'{pct(min(w[key] for w in cells if w[key] is not None))} to {pct(max(w[key] for w in cells if w[key] is not None))}'
    wr = lambda r: (num(min(w['conf_width'] for w in r['windows']), 1), num(max(w['conf_width'] for w in r['windows']), 1))
    gk_slow = {(w['W'], w['burn']): w['gk'] for w in slow['windows']}
    gk_fast = [w['gk'] for w in fast['windows']]
    A(('p', f'Three things follow. *First*, to assume a memory of one transit fails at both levels. *Second*, an '
            f'interval with the measured correlation is right only where the central limit has been reached and the '
            f'record is long enough to show the memory. At Re = {re_(fast)} it is too wide: for windows not much '
            f'longer than the correlation time the central-limit line overstates the scatter (Figure {{{{clt}}}}b), and '
            f'the coverage is {pct(min(gk_fast))} to {pct(max(gk_fast))}. At Re = {re_(slow)} it is too narrow: the '
            f'first record underestimates the memory, and the coverage falls from {pct(gk_slow[(5, 200)])} for windows '
            f'of 5 transit times to {pct(gk_slow[(40, 200)])} for windows of 40, and to {pct(gk_slow[(40, 50)])} with '
            f'the short record. *Third*, the conformal multiplier moves in both directions: the conformal intervals '
            f'are {wr(fast)[0]} to {wr(fast)[1]} times as wide as those with the measured correlation at Re = '
            f'{re_(fast)} and {wr(slow)[0]} to {wr(slow)[1]} times at Re = {re_(slow)}. A ratio far from one is '
            f'itself a sign that the memory was misjudged. Over the {len(cells)} combinations of level, window and '
            f'first record the conformal intervals cover {rng("conformal")}, against {rng("gk")} for the intervals '
            f'with the measured correlation and {rng("naive")} for one transit of memory.'))
    w5s = next(w for w in slow['windows'] if w['W'] == 5 and w['burn'] == 200)
    w5f = next(w for w in fast['windows'] if w['W'] == 5 and w['burn'] == 200)
    g30, g25 = SG[30.0], SG[2.5]
    sf = fast['sd5_stretches']; im = int(np.argmax(sf)); rest = [v for i, v in enumerate(sf) if i != im]
    lo_c = min(r['coverage'][k]['cov'] for r in longs for k in ('conformal_50', 'conformal_200'))
    hi_c = max(r['coverage'][k]['cov'] for r in longs for k in ('conformal_50', 'conformal_200'))
    A(('p', f'**The conformal intervals are not exact.** Over the windows fixed in advance they cover '
            f'{pct(lo_c)} to {pct(hi_c)} at either level, {num(100 * (0.9 - hi_c), 0)} to {num(100 * (0.9 - lo_c), 0)} '
            f'points below their nominal value, and less for the windows of 40 transit times, where few scores are '
            f'available. Synthetic Gaussian series say how much of this is chance and memory (gate 4, 24 records per '
            f'case). With a correlation time of 30 transit times, a case added after the long runs, the same code '
            f'covers {pct(g30["conformal_50"])} to {pct(g30["conformal_200"])} on average, with a standard deviation '
            f'of {num(100 * max(g30["conformal_50_sd"], g30["conformal_200_sd"]), 0)} points between records: the '
            f'result at Re = {re_(slow)} is what a memory of that length gives. There the windows are shorter than the '
            f'memory, the running mean lags behind the slow swings of the flux, and {w5s["conf_miss_above"]} of the '
            f'{w5s["conf_miss"]} misses of the 5-transit windows lie on one side of the prediction. With a '
            f'correlation time of 2.5 the synthetic coverage is {pct(g25["conformal_200"])} and never below '
            f'{pct(min(g25["conformal_50_min"], g25["conformal_200_min"]))}: the result at Re = {re_(fast)} lies below '
            f'every one of those records. A reason visible in the record is intermittency: {w5f["conf_miss_late"]} of the '
            f'{w5f["conf_miss"]} misses of the 5-transit windows fall in the last 200 transit times, where the '
            f'5-transit means scatter by {pct(sf[im], 1)} of the flux in one stretch of 100 transit times, against '
            f'{pct(min(rest), 1)} to {pct(max(rest), 1)} in the others; before that the miss rate is '
            f'{pct(w5f["conf_miss_early"] / w5f["conf_n_early"])}. In both cases the scores are not exchangeable, and '
            f'the guarantee of [[cert]] does not apply as stated. Giving recent scores more weight (S38) is the known '
            f'remedy; it was not tested here.'))
    rows = []
    hdr = ['Window, transit times', 'Number of windows', 'One transit of memory assumed', 'Measured correlation, long record',
           'Conformal, long record', 'Measured correlation, short record', 'Conformal, short record',
           'Width ratio']
    for r in longs:
        rows.append([f'**Re = {re_(r)}: integrated correlation time {num(r["tau_int"], 1)} transit times**'] + [''] * 7)
        for W in ('5', '10', '20', '40'):
            c = r['coverage_by_W'].get(W, {})
            if 'gk_200' not in c:
                continue
            w = next(x for x in r['windows'] if str(x['W']) == W and x['burn'] == 200)
            rows.append([W + (' *' if W == '40' else ''), str(c['gk_200']['n']), g(c, 'naive_200'), g(c, 'gk_200'),
                         g(c, 'conformal_200'), g(c, 'gk_50'), g(c, 'conformal_50'), num(w['conf_width'], 2)])
        c = r['coverage']
        rows.append(['5 to 20', str(c['gk_200']['n']), g(c, 'naive_200'), g(c, 'gk_200'), g(c, 'conformal_200'),
                     g(c, 'gk_50'), g(c, 'conformal_50'), num(r['conf_width']['200'], 2)])
    rows.append(['**Both levels**'] + [''] * 7)
    rows.append(['5 to 20', str(C['gk_200']['n']), g(C, 'naive_200'), g(C, 'gk_200'), g(C, 'conformal_200'), g(C, 'gk_50'),
                 g(C, 'conformal_50'), num(R['conf_width']['200'], 2)])
    A(('table', hdr, rows, [1.9, 1.8, 2.3, 2.4, 2.2, 2.4, 2.2, 1.8], 9.0))
    A(('cap', 'Table {{cov}}. Coverage of nominal 90% intervals for the mean flux of the next window, by level and '
              'window length. Long record: 200 transit times before the first prediction; short record: 50. Number of '
              'windows: those predicted with a long record. Width ratio: mean width of the conformal interval over that of '
              'the interval with the measured correlation (long record). * The window of 40 transit times was added '
              'after the sweep had shown a correlation time of about 12 transit times at one level, before the long '
              'runs were analysed.'))
    A(('img', 'clt', 16.5))
    A(('cap', 'Figure {{clt}}. (a) The Darcy flux of the cell over the whole record of each level; thin line: the flux '
              '(quarter-transit means), thick line: its running mean over 20 transit times. (b) Scatter of the means '
              'over windows of increasing length: measured (points), from the measured autocovariance for a window of '
              'that length (solid), and the central-limit law of Proposition 2 (dashed). (c) Coverage of nominal 90% '
              'intervals for the mean flux of the next window, by level, pooled over the windows of 5, 10 and 20 '
              'transit times; the last two rows use a first record of 50 transit times.'))



def blocks(R):
    s = fill_numbers(R)
    cards = filled_cards(s)
    lev = R['levels']
    B = []
    A = B.append
    A(('title', 'From chaos in the pores to Darcy\'s law'))
    A(('subtitle', 'How the passage from a chaotic small scale to a deterministic large-scale law is explained, what it '
                   'leaves open, and a certified, goal-oriented upscaling (KAOS-GO) with a pore-scale numerical test. '
                   'Twenty-five papers of 2020–2026 from Caltech, Oxford, MIT, Harvard and the Max Planck Society, and '
                   'a map of possible partners'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · code and results: '
                 'experiments/kaos_go/'))
    # ---------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. The answer in brief'))
    A(('bbox', [
        '**The article.** The description fits one article: Browne & Datta, *Elastic turbulence generates anomalous '
        'flow resistance in porous media*, Science Advances 2021, from Princeton University (A1). A polymer solution '
        'flowing through a transparent three-dimensional porous medium shows, above a threshold flow rate, "strong '
        'spatiotemporal fluctuations reminiscent of inertial turbulence, despite the small Reynolds number", and "the '
        'energy dissipated by pore-scale fluctuations generates the anomalous increase in the overall flow resistance" '
        '(abstract).',
        '**The correction.** The large scale does not obey Darcy\'s law unchanged. Its *form* survives: the mean flux '
        'follows the mean pressure gradient. Its *coefficient* stops being a constant of the medium and the fluid: it '
        'depends on the flow rate, through the dissipation of the fluctuations.',
        '**How the passage happens** (Section 3). (1) Darcy\'s law is a statement about averages, and the balances of '
        'mass, momentum and energy survive averaging whatever the trajectories do. (2) The resistance *is* the mean '
        'dissipation: chaos enters the large-scale law only through the dissipation of the fluctuations and the change '
        'it makes to the mean flow (Proposition 1). (3) The average is sharp because a block holds many pores and a '
        'measurement lasts many correlation times: its error falls as $1/\\sqrt{N\\,T}$ (Proposition 2). The '
        'unpredictability of each trajectory is the reason why the average is predictable.',
        '**For water in an aquifer** (Section 8) the pore Reynolds number is far below one: the velocity field in the '
        'pores is steady, Darcy\'s law holds, and chaos lives only in the *paths* of fluid particles, where it governs '
        'mixing and reactions. A chaotic velocity field appears with polymers, near wells in coarse gravel, in '
        'two-phase flow and, one scale up, in unstable density-driven flow and under tides.',
        '**How others explain it** (Section 4, Figure {{map}}, twenty-five cards in Section 10). Five routes: '
        'experiments and resolved simulations, homogenisation, statistical physics and probability, dissipation budgets, '
        'learned closures. None returns the large-scale law together with a tested statement of its error in the '
        'quantity a decision needs, and none chooses the small-scale experiments for that decision.',
        f'**Innovation: KAOS-GO** (Sections 6 and 7). A fluctuating Darcy closure (mean from the dissipation split, '
        f'noise from the pore scale), a certificate calibrated on windows predicted before they are computed, and a '
        f'goal-oriented allocation of the pore-scale effort. In a pore-resolved experiment ({s["n_lev"]} forcing levels, '
        f'Reynolds number {s["re_lo"]} to {s["re_hi"]}): the flow is steady up to Re ≈ {s["onset_lo"]}, periodic from '
        f'Re ≈ {s["onset_hi"]} and chaotic from Re ≈ {s["chaos_hi"]} (Lyapunov exponent {s["lyap_hi"]} per pore transit '
        f'time at the top, the same on three grids); the resistance is {s["F_hi"]} times its Darcy value at Re = {s["re_hi"]}, of '
        f'which the fluctuations carry {s["fluct_share_hi"]}. Just above the onset of chaos the flux keeps a memory '
        f'of {s["slow_tau"]} pore transit times, which a record of 200 does not reveal. Over two levels, four '
        f'window lengths and two record lengths, nominal 90% intervals for the mean flux of the next window cover '
        f'{s["rng_naive"]} if one transit of memory is assumed, {s["rng_gk"]} with the measured correlation and '
        f'{s["rng_conformal"]} with the conformal calibration: the steadiest of the three, and not exact '
        f'(Table {{{{cov}}}}).',
        '**Partners** (Section 9). For the phenomenon itself: S. S. Datta (now at Caltech) and the groups at OIST and '
        'Tufts; for mixing in groundwater: Géosciences Rennes, RMIT and IDAEA-CSIC; for tools that match ours and are '
        'near: Politecnico di Torino, Stuttgart, the Technical University of Crete, BGR Hannover.']))
    # ---------------------------------------------------------------------------------------------- 2 the article
    A(('h', '2. The Princeton article and the question, stated precisely'))
    A(('h2', '2.1 Which article'))
    A(('p', 'Christopher A. Browne and Sujit S. Datta, *Elastic turbulence generates anomalous flow resistance in porous '
            'media*, Science Advances 7(45), eabj2619, 2021 ([doi:10.1126/sciadv.abj2619]'
            '(https://doi.org/10.1126/sciadv.abj2619)); both authors at Princeton University (A1). The abstract states '
            'the puzzle and the answer: the macroscopic flow resistance of polymer solutions "often increases above a '
            'threshold flow rate in a porous medium, but not in bulk solution", a puzzle "for over half a century"; by '
            'directly visualising the flow in a transparent three-dimensional porous medium the authors show that the '
            'increase is due to the onset of an elastic instability in which the flow fluctuates strongly in space and '
            'time although the Reynolds number is small; and their measurements "quantitatively establish that the '
            'energy dissipated by pore-scale fluctuations generates the anomalous increase in the overall flow '
            'resistance". The full text could not be opened from the build environment; everything said here about the '
            'article rests on its abstract, on the abstracts of the conference talks of the authors and on the later '
            'papers of the group.'))
    A(('p', 'The same group studied the instability in arrays of pore constrictions, where distinct pores take distinct '
            'unsteady states (A2, A5, card C2), in stratified media, where it evens out the flow between strata (A3), '
            'and as a tool for mixing and reaction (A4). A later paper of the group cites the onset in the homogeneous '
            'medium at a Weissenberg number of about 2.6, and the conference abstracts describe the unstable pores as '
            'patchy: laminar and unstable pores coexist, each pore with its own onset. S. S. Datta moved from Princeton '
            'to Caltech in September 2024 (A6), so the most recent papers of the group are among the Caltech cards '
            '(C1, C2).'))
    A(('h2', '2.2 What the article says about Darcy\'s law'))
    A(('p', 'In such experiments Darcy\'s law is used as a *definition*: a flow rate $Q$ is imposed through a medium of '
            'cross-section $A$, length $L$ and permeability $k$, the pressure drop $\\Delta P$ is measured, and the '
            'apparent viscosity is what Darcy\'s law would need in order to hold,'))
    A(('eq', 'etaapp', '\\eta_{\\mathrm{app}}=\\frac{k}{Q/A}\\,\\frac{\\Delta P}{L}.'))
    A(('p', 'Below the threshold $\\eta_{\\mathrm{app}}$ equals the shear viscosity $\\eta$ of the solution at the shear '
            'rate of the pores, and Darcy\'s law holds in the ordinary sense. Above it $\\eta_{\\mathrm{app}}$ rises with '
            'the flow rate. If the rate of dissipation per unit volume is written as that of the steady flow plus an '
            'added rate $\\langle\\chi\\rangle$ due to the fluctuations, the definition [[etaapp]] and the balance of '
            'power (Proposition 1 below) give'))
    A(('eq', 'princeton', '\\frac{\\eta_{\\mathrm{app}}}{\\eta}=1+\\frac{k\\,\\langle\\chi\\rangle}{\\eta\\,(Q/A)^{2}}.'))
    A(('p', 'This is the content of the sentence quoted from the abstract, in our notation: the excess of the '
            'resistance is the dissipation of the fluctuations. So the recollection "chaotic at the small scale, Darcy at '
            'the large scale" needs one correction. The large scale keeps the *form* of Darcy\'s law, a mean flux '
            'proportional to a mean gradient, and loses the *constancy* of its coefficient. The interesting statement '
            'is not that the chaos disappears on averaging, but that exactly one number of the chaos survives it.'))
    A(('h2', '2.3 Four things that are called chaos in a porous medium'))
    A(('p', 'The word covers four different situations, and the answer to "does Darcy\'s law hold?" differs between '
            'them (Table {{kinds}}). The second is the one that concerns every aquifer; the third is the Princeton '
            'case.'))
    A(('table', ['Kind', 'Where and when', 'Darcy\'s law', 'What changes at the large scale', 'Sources'], [
        ['1. Molecular motion', 'Always', 'Not affected: it is why a viscosity exists',
         'Nothing above the nanometre scale; the link between fluctuation and dissipation (S34) is the model of all '
         'that follows', 'S34'],
        ['2. Chaotic *paths* in a steady flow', 'Steady three-dimensional flow through grains, water at Re ≪ 1 '
         'included', 'Holds: the velocity field is steady and the Stokes equations are linear',
         'Mixing: fluid elements are stretched exponentially and folded, concentration gradients survive at the pore '
         'scale, reactions are limited by mixing', 'S9–S14, S18'],
        ['3. Chaotic *velocity field* in the pores', '(a) polymer solutions above a critical Weissenberg number, at '
         'Re ≪ 1; (b) any fluid at pore Reynolds numbers of order 100; (c) capillary bursts in two-phase flow',
         'Form kept, coefficient depends on the flow rate',
         '(a) apparent viscosity rises, mixing is enhanced; (b) Forchheimer-type resistance, then unsteady and '
         'turbulent flow; (c) relative permeability depends on rate, pressure fluctuates at the core scale',
         '(a) A1–A5, S19, S20, C1, C2, O5, P5; (b) S3–S8; (c) S21–S25, M2'],
        ['4. Chaos at the Darcy scale', 'Unstable density stratification; flow forced in time through a heterogeneous, '
         'compressible aquifer (tides); steady three-dimensional flow in a heterogeneous medium',
         'Holds locally; the regional law (flux, mixing rate) is statistical again',
         'Convective flux laws, enhanced mixing near the coast, transverse dispersion', 'S15–S17, S28, S29, M3, P3, P4'],
    ], [2.5, 4.0, 2.9, 5.2, 2.4], 8.6, False))
    A(('cap', 'Table {{kinds}}. Four meanings of "chaos" in flow through a porous medium. Keys: A the Princeton group, '
              'S context sources, letters with a digit the twenty-five cards of Section 10.'))
    # ---------------------------------------------------------------------------------------------- 3 how it happens
    A(('h', '3. How the passage happens'))
    A(('h2', '3.1 What Darcy\'s law is a statement about'))
    A(('p', 'Let $V$ be a block of the medium that holds $N$ pores, $V_f$ its pore space, $\\mathbf{u}(\\mathbf{x},t)$ '
            'the velocity of the fluid, zero on the grains. The Darcy velocity is the average '
            '$\\mathbf{q}=|V|^{-1}\\int_{V_f}\\mathbf{u}\\,dV$, and the driving force is the mean pressure gradient with '
            'gravity, $\\mathbf{G}=-\\nabla P+\\rho\\mathbf{g}$. Darcy\'s law,'))
    A(('eq', 'darcy', '\\mathbf{q}=\\frac{K}{\\mu}\\,\\mathbf{G},'))
    A(('p', 'relates two averages over the block and, when the flow is unsteady, over time. It says nothing about any '
            'trajectory. Three properties of the small scale are therefore enough for it: that the balances of mass, '
            'momentum and energy hold at every point, that they are linear in the quantities that are averaged or can '
            'be closed after averaging, and that the block is large and the time long compared with the scales over '
            'which the small-scale motion is correlated.'))
    A(('h2', '3.2 The resistance is the dissipation'))
    A(('p', 'Take a Newtonian fluid of density $\\rho$ and viscosity $\\mu$ in a periodic cell, driven by a uniform '
            'force $\\mathbf{G}$. Multiply the Navier–Stokes equation by $\\mathbf{u}$ and integrate over the pore '
            'space. The advective and the pressure terms integrate to zero, because the flow is incompressible, '
            'vanishes on the grains and is periodic. What remains is the balance of mechanical energy, with '
            '$\\mathbf{S}$ the rate-of-strain tensor:'))
    A(('eq', 'energy', '\\frac{d}{dt}\\int_{V_f}\\frac{\\rho}{2}\\,|\\mathbf{u}|^{2}\\,dV=\\mathbf{G}\\cdot\\int_{V_f}'
                       '\\mathbf{u}\\,dV-2\\mu\\int_{V_f}\\mathbf{S}:\\mathbf{S}\\,dV.'))
    A(('prop', 'Proposition 1 (the resistance is the dissipation).',
       'Let the flow be statistically stationary, $\\overline{\\,\\cdot\\,}$ the time mean, $\\mathbf{u}=\\overline{'
       '\\mathbf{u}}+\\mathbf{u}\'$, $U=|\\overline{\\mathbf{q}}|$ with $\\overline{\\mathbf{q}}$ along $\\mathbf{G}$, and '
       '$\\Phi[\\mathbf{v}]=2\\mu\\,|V|^{-1}\\int_{V_f}\\mathbf{S}(\\mathbf{v}):\\mathbf{S}(\\mathbf{v})\\,dV$. Then '
       '(i) $G\\,U=\\Phi[\\overline{\\mathbf{u}}]+\\overline{\\Phi[\\mathbf{u}\']}$; (ii) the resistance $R=G/U$ is the '
       'sum $R_{\\mathrm{mean}}+R_{\\mathrm{fluct}}$ of the two parts divided by $U^{2}$; (iii) $R\\ge\\mu/K$, with '
       'equality only for the Stokes flow: the Darcy permeability is an upper bound of the apparent permeability of '
       'any flow of a Newtonian fluid through the same medium, steady or chaotic.'))
    A(('proof', 'Average [[energy]] in time: the left side vanishes for a stationary flow, which gives '
                '$\\mathbf{G}\\cdot\\overline{\\mathbf{q}}=\\overline{\\Phi[\\mathbf{u}]}$. $\\Phi$ is quadratic and '
                '$\\overline{\\mathbf{u}\'}=0$, so the cross term drops and (i) follows; (ii) is (i) divided by $U^{2}$. '
                'For (iii): among all incompressible fields that vanish on the grains, are periodic and carry the '
                'flux $U$, the dissipation is least for the solution of the Stokes problem with a uniform force '
                '(Helmholtz\'s minimum-dissipation theorem; the uniform force is the multiplier of the flux '
                'constraint). The time-mean field $\\overline{\\mathbf{u}}$ is such a field, hence '
                '$\\Phi[\\overline{\\mathbf{u}}]\\ge(\\mu/K)U^{2}$, and $\\overline{\\Phi[\\mathbf{u}\']}\\ge 0$. '
                'In an anisotropic cell the mean flux need not be along the force; (i) then holds with $U$ the '
                'component of the mean flux along $\\mathbf{G}$, and (iii) with $K$ the component of the permeability '
                'tensor along $\\mathbf{G}$, by the Cauchy–Schwarz inequality. This is how $U$ and $K$ are measured '
                'in Section 7.'))
    A(('eq', 'split', ['R\\equiv\\frac{G}{U}=R_{\\mathrm{mean}}+R_{\\mathrm{fluct}},',
                       'R_{\\mathrm{mean}}=\\frac{\\Phi[\\overline{\\mathbf{u}}]}{U^{2}}\\;\\ge\\;\\frac{\\mu}{K},'
                       '\\qquad R_{\\mathrm{fluct}}=\\frac{\\overline{\\Phi[\\mathbf{u}\']}}{U^{2}}\\;\\ge\\;0.']))
    A(('p', 'In plain words: the pressure drop across a block is the bill for the energy dissipated inside it. The '
            'bill is a sum over the pores. A pore whose flow has become chaotic pays more, because the fluctuating '
            'velocity gradients dissipate on top of the mean ones; and the sum over many pores and a long time is '
            'steady even though the payment of each pore flickers. Nothing else of the chaos reaches the large scale: '
            'not the trajectories, not the phases, only the mean rate of dissipation.'))
    A(('p', 'The identity is classical mechanics; the use made of it is the point. Darcy\'s law is the statement that '
            'the mean dissipation is a fixed quadratic form of the mean flux, and it is true whenever the velocity '
            'field scales in proportion to the force, as in Stokes flow. A chaotic small scale can change the '
            'large-scale law in two ways only: it adds its own dissipation, $R_{\\mathrm{fluct}}$, and it reshapes the '
            'mean flow, which raises $R_{\\mathrm{mean}}$. For a polymer solution the stress has an elastic part, and '
            'the same balance holds with the work of the polymer stress added; the Princeton measurement [[princeton]] '
            'is that balance with the added term taken from the imaged fluctuations, and card C1 reports the other '
            'term, the stresses of the mean flow at stagnation points.'))
    A(('h2', '3.3 Why the average is sharp'))
    A(('p', 'The flux of a block at a fixed force is a sum over its pores, and a measurement is an average over a '
            'time $T$. If the contributions of distant pores and of distant times are weakly correlated, the two '
            'classical limit theorems apply.'))
    A(('prop', 'Proposition 2 (law of large numbers and central limit for the Darcy flux).',
       'Let $Q(t)$ be the flux of a cell at fixed force, stationary with autocovariance $C(\\tau)$ and finite '
       '$\\sigma_{\\infty}^{2}=\\int_{-\\infty}^{\\infty}C(\\tau)\\,d\\tau$. Then the mean over a window $T$ satisfies '
       '$\\mathrm{Var}\\,\\overline{Q}_{T}\\simeq\\sigma_{\\infty}^{2}/T$, and for a block of $M$ independent cells '
       '$\\mathrm{Var}\\simeq\\sigma_{\\infty}^{2}/(M\\,T)$, with a Gaussian limit when the correlations decay fast '
       'enough. In a random medium at rest the same holds in space: the conductivity of a block of $N$ grains scatters '
       'as $N^{-1/2}$ around its limit (cards P1, P2).'))
    A(('eq', 'clt', '\\overline{q}_{N,T}=\\langle q\\rangle+\\sqrt{\\frac{\\sigma_{\\mathrm{cell}}^{2}}{N}+\\frac{\\sigma_{'
                    '\\infty}^{2}}{N\\,T}}\\;\\xi,\\qquad\\sigma_{\\infty}^{2}=2\\int_{0}^{\\infty}C(\\tau)\\,d\\tau,'
                    '\\qquad\\xi\\sim\\mathcal{N}(0,1).'))
    A(('p', 'Equation [[clt]] is Darcy\'s law with its error term: $\\sigma_{\\mathrm{cell}}$ is the scatter between '
            'realisations of the medium and $\\sigma_{\\infty}^{2}$ the integral of the autocovariance of '
            'the flux, the form that Green and Kubo gave to transport coefficients (S34); both are referred to one pore. Three remarks. First, chaos '
            'is not an obstacle to the second term but its reason: a chaotic flow forgets its initial state, its '
            'correlations decay, and its time averages converge to values that do not depend on where the flow '
            'started (S35 models the error of such averages). Second, in the first term disorder plays the role of '
            'chaos. Third, the statement fails in recognisable ways: near the onset, where few pores are unstable, '
            'their bursts are rare and long and the flow forgets slowly (Section 7.3 measures this case); when pores '
            'are coupled (C2); when a threshold makes one fluctuation decisive (P5); and when the block is not much '
            'larger than a pore.'))
    A(('h2', '3.4 What chaos does change at the large scale'))
    A(('b', '**The resistance law becomes nonlinear**: an apparent viscosity that grows with the flow rate for polymer '
            'solutions (A1), a Forchheimer term for inertia (S3–S8), a rate-dependent relative permeability for two '
            'phases (S21).'))
    A(('b', '**Mixing and reaction rates rise**: chaotic paths stretch and fold the fluid (S9–S14), and an elastic '
            'instability does the same at low Reynolds number (A4).'))
    A(('b', '**The flow redistributes**: an instability that starts in the fast stratum raises its resistance and evens '
            'out the flow between strata (A3); retention of polymer diverts the flow between pores (H1, H2).'))
    A(('b', '**Thresholds are crossed by fluctuations**: a trapped drop is mobilised by the fluctuating pressure, not '
            'by its mean (P5).'))
    A(('b', '**Patterns stop being repeatable while integrals stay so**: sixteen runs of one injection differ in their '
            'fingers (M5), yet the flux and the dissipation of convective mixing are reproduced by simulation (M3).'))
    # ---------------------------------------------------------------------------------------------- 4 routes
    A(('h', '4. How others explain it: five routes'))
    A(('p', 'The twenty-five papers of Section 10 (five per institution, Figure {{map}}) and the context sources fall '
            'into five routes of explanation. A paper can serve two.'))
    A(('img', 'map', 16.5))
    A(('cap', 'Figure {{map}}. The twenty-five papers of the review against the five routes by which the passage from '
              'the small to the large scale is explained. Colours mark the institutions; the short titles are ours.'))
    A(('p', '**Seeing it.** Experiments in transparent media and microfluidic devices, and simulations that resolve '
            'the pores, show the mechanism and give the dimensionless numbers that organise it: the Weissenberg and '
            'Deborah numbers for polymers (A1, C1, C2, S19), the Reynolds number for inertia (S4–S8), the capillary '
            'number and the wettability for two phases (M2, S21). Disorder can suppress the chaos in two dimensions '
            '(S20) and does not in three (A1). This route explains by exhibiting, and it produces regime diagrams. It '
            'does not produce a law with an error bar for another medium.'))
    A(('p', '**Homogenisation.** For steady Stokes flow in a periodic or slowly varying microstructure the passage is '
            'a theorem: Darcy\'s law is the solvability condition of a cell problem, the permeability an average of its '
            'solution (S1, S2, O1), with a cubic correction at weak inertia (S3) and a Darcy-type law with a '
            'state-dependent tensor for nonlinear network flows (O4). The cell problem can be learned (C3) and a '
            'learned small-scale solver can be carried inside the large-scale model (C4). The route needs a separation '
            'of scales and a cell problem that has a steady solution.'))
    A(('p', '**Statistical physics and probability.** Here the large-scale law is a law of large numbers and the '
            'question becomes how large its fluctuations are. In a random medium at rest all fluctuations come from one '
            'local object (P1), and the error of a representative volume has a random and a systematic part with '
            'known rates (P2, S32, S33). A velocity field that is ergodic in space and time gives a diffusion with a '
            'noise term of deterministic covariance (O2), and rare deviations have a rate function (O3). Networks '
            'homogenise or channel across a phase transition (H3), permeability scales critically at percolation '
            '(S26), invasion proceeds by avalanches (S25), and the multiphase community has replaced the '
            'representative volume by a volume in space and time (S22–S24).'))
    A(('p', '**Dissipation budgets.** Exact global balances fix the large-scale law once the dissipation is split into '
            'parts that scale differently: boundary layer and bulk for convection in a porous medium (P4, after S30), '
            'steady flow and fluctuations for the Princeton experiment (A1). Proposition 1 belongs here.'))
    A(('p', '**Learned closures.** The law is not derived but learned from small-scale data: stochastic closures from '
            'time averages (C5), hydrodynamic equations from particles (M4), latent dynamics that alternate with the '
            'small-scale solver (H5), corrections to coarse solvers (S42), closures with memory (S41), terms of model '
            'error (S40), and derivatives through the resolved flow (H4). These methods predict; they do not say how '
            'wrong the prediction is for a given decision.'))
    A(('table', ['Route', 'What it delivers', 'What it needs', 'What it does not deliver'], [
        ['Seeing it', 'Mechanism, onset, regime diagram', 'A transparent medium or a resolved simulation',
         'A law for another medium, with its error'],
        ['Homogenisation', 'The mean law and its coefficients', 'Scale separation; a steady cell problem',
         'Fluctuations; unsteady small scales'],
        ['Statistics', 'Rates of convergence, the form of the noise', 'Stationarity, decay of correlations',
         'Numbers for a given medium and decision'],
        ['Dissipation', 'Exact identities, scaling laws', 'A stationary state and a split that scales',
         'The split itself, without data or theory'],
        ['Learning', 'Fast predictions, discovered equations', 'Small-scale data that cover the use',
         'A guarantee; a choice of the data for a goal'],
    ], [3.1, 4.5, 4.4, 5.0], 9.0))
    A(('cap', 'Table {{routes}}. The five routes: what each gives and what each leaves out.'))
    # ---------------------------------------------------------------------------------------------- 5 gap
    A(('h', '5. What remains open'))
    A(('p', 'Put together, the routes explain why a large-scale law exists and what form it takes. Three things are '
            'missing, and they are the ones a user of the law needs.'))
    A(('b', '**The error of the law for a finite block and a finite time**, as a number for a given medium and not as '
            'a rate. The theory of fluctuations (P1, P2, O2) is for media at rest or for transport; the chaos of the '
            'momentum balance, the Princeton case, has no such theory, and none of the abstracts read here reports '
            'the error of the upscaled law.'))
    A(('b', '**A tested guarantee in the quantity a decision needs.** A drawdown at a well, a time to an alarm or the '
            'pressure of an injection depend on the closure through weights that none of the twenty-five papers '
            'computes; learned closures come without coverage statements.'))
    A(('b', '**A rule for the small-scale effort.** Which flow rates to simulate or to measure, for how long, on how '
            'many samples of the medium: today this is chosen by habit, not for a goal.'))
    # ---------------------------------------------------------------------------------------------- 6 KAOS-GO
    A(('h', '6. Our contribution: KAOS-GO'))
    A(('box', [
        '**Innovation.** KAOS-GO is an upscaling in which the large-scale law carries its own tested error. '
        '(1) *A fluctuating Darcy closure*: the mean resistance from the dissipation split of Proposition 1, the noise '
        'from the pore-scale integral of Proposition 2, the scatter between realisations from the finite block. '
        '(2) *A certificate*: each new window of the small-scale flow, each new forcing level and each new realisation '
        'is predicted before it is computed or measured; the standardised errors calibrate a conformal multiplier that '
        'needs no Gaussian assumption; the adjoint of the Darcy-scale model carries the interval to the decision. '
        '(3) *A goal-oriented design of the small scale*: the adjoint weights say at which flux levels the decision '
        'listens, and the computing and laboratory effort is allocated by Proposition 3. The adjoint is taken at the '
        'Darcy scale only: KAOS-GO never differentiates through the chaos (card H4).']))
    A(('h2', '6.1 The closure'))
    A(('p', 'Write the resistance relative to its Darcy value as a function of the pore Reynolds number (or, for a '
            'polymer solution, of the Weissenberg number), $F=K/K_{\\mathrm{app}}=F_{\\mathrm{mean}}+F_{\\mathrm{fluct}}$. '
            'The closure used by a Darcy-scale model with blocks of $N$ pores and steps of length $T$ is'))
    A(('eq', 'closure', '\\overline{\\mathbf{q}}_{N,T}=\\frac{K}{\\mu\\,F(\\mathrm{Re})}\\,\\mathbf{G}\\,\\Big[1+'
                        '\\sqrt{c_{\\mathrm{cell}}^{2}(N)+\\frac{2\\,\\tau_{\\mathrm{int}}\\,c_{t}^{2}}{T}}\\;\\xi\\Big],'
                        '\\qquad F=F_{\\mathrm{mean}}+F_{\\mathrm{fluct}},'))
    A(('p', 'where $c_{\\mathrm{cell}}(N)$ is the coefficient of variation of the conductivity between realisations of '
            'a block, $c_{t}$ that of the flux of one block in time at a fixed force, and $\\tau_{\\mathrm{int}}$ its '
            'integrated correlation time. All three are measured at the pore scale (Section 7). The factor in front of '
            'the bracket is the usual nonlinear Darcy law; the bracket is what the twenty-five papers do not carry.'))
    A(('h2', '6.2 The certificate'))
    A(('p', 'Let $\\hat q_{k}$ be the prediction of the next window, level or realisation and $s_{k}$ its predicted '
            'standard deviation from [[closure]]. The scores $w_{k}=|q_{k}-\\hat q_{k}|/s_{k}$ of the cases already '
            'seen give the multiplier'))
    A(('eq', 'cert', '\\hat Q_{\\alpha}=\\text{the }\\lceil(1-\\alpha)(n+1)\\rceil\\text{-th smallest of }w_{1},\\dots,'
                     'w_{n},\\qquad q_{n+1}\\in\\hat q_{n+1}\\pm\\hat Q_{\\alpha}\\,s_{n+1}.'))
    A(('p', 'If the scores are exchangeable the interval covers with probability at least $1-\\alpha$ whatever their '
            'law; under the dependence of a mixing series the loss of coverage is bounded by the distance from '
            'exchangeability (S38), which is why the scores should be taken on windows longer than the correlation '
            'time; Section 7.3 shows what happens when that time is longer than the record suggests. For '
            'a decision $J$ of a Darcy-scale model the errors of the closure are transported by the adjoint, as in '
            'SALTPROOF (D2): $\\delta J=\\int w(q)\\,\\delta F(q)\\,d\\ln q$, with a weight $w$ that the adjoint '
            'solution gives.'))
    A(('h2', '6.3 The design'))
    A(('prop', 'Proposition 3 (where to spend the small-scale effort).',
       'Let the decision be $J=\\sum_{j}a_{j}F_{j}$ over the levels $j$ of the closure, and let level $j$, run for a '
       'time $T_{j}$ at a cost $c_{j}$ per unit time, have the variance $\\sigma_{j}^{2}/T_{j}$. For a fixed budget '
       '$\\sum_{j}c_{j}T_{j}$ the variance of $J$ is least for $T_{j}\\propto|a_{j}|\\,\\sigma_{j}/\\sqrt{c_{j}}$, and '
       'the gain over an equal split is $1-(\\sum_{j}|a_{j}|\\sigma_{j})^{2}/(n\\sum_{j}a_{j}^{2}\\sigma_{j}^{2})$ for '
       'equal costs.'))
    A(('proof', 'Minimise $\\sum_{j}a_{j}^{2}\\sigma_{j}^{2}/T_{j}$ under the budget with a multiplier; the stationarity '
                'condition is $a_{j}^{2}\\sigma_{j}^{2}/T_{j}^{2}\\propto c_{j}$. This is the c-optimal design for a '
                'linear functional (S60), here with weights from an adjoint.'))
    A(('p', 'Steady levels need no averaging and receive nothing; the chaotic levels receive effort in proportion to '
            'their weight in the decision times their noise. When candidate laws compete (Forchheimer, a power law, '
            'an onset), the next level is the one where they differ most relative to the noise, the T-optimal choice '
            '(S59); stability selection (S61) keeps only the terms that survive resampling. This is SC-PDE-FIND (D3) '
            'applied to the closure of an upscaling.'))
    A(('h2', '6.4 Why this is ours to do'))
    A(('p', 'The three parts are the tools of the certain-coast code and of the SALTPROOF proposal (D1, D2): adjoints '
            'of a Darcy-scale model, goal-oriented design, certificates from experiments predicted in advance. What is '
            'new here is their object. In SALTPROOF the model error lives in the fields of an aquifer and its geometry '
            'is assumed; in KAOS-GO the error comes from an unresolved scale and its geometry is *computed*: the theory '
            'of card P1 says that the fluctuation of any decision is an adjoint-weighted integral of a local noise with '
            'a computable covariance. That is a physically derived family of geometries for objective O1 of SALTPROOF.'))
    # ---------------------------------------------------------------------------------------------- 7 experiment
    A(('h', '7. A pore-scale experiment'))
    A(('h2', '7.1 Setting'))
    hi = lev[-1]
    A(('p', f'A periodic two-dimensional cell holds 16 circular grains of radius $a$, placed at random on the torus '
            f'(random sequential addition, minimum gap $a/3$; solid fraction {pct(1 - hi["porosity"])}). A Newtonian fluid is '
            f'driven by a uniform force. The flow is solved with a lattice-Boltzmann method (nine velocities, two '
            f'relaxation times, S48; force after S47; halfway bounce-back on the grains) on a lattice with '
            f'{hi["a"]:.0f} nodes per grain radius ({hi["L"]} × {hi["L"]} nodes). The force is kept and the viscosity is '
            f'lowered through {s["n_lev"]} levels, so that the Reynolds number $\\mathrm{{Re}}=U\\,2a/\\nu$, with $U$ the '
            f'Darcy velocity, runs from {s["re_lo"]} to {s["re_hi"]}. Time is counted in pore transit times, $2a$ over '
            f'the pore velocity. Each unsteady level is sampled over 384 000 time steps ({s["samp_lo"]} to '
            f'{s["samp_hi"]} transit times, depending on the level) after a spin-up of {s["spin_lo"]} to {s["spin_hi"]}; '
            f'the largest Lyapunov exponent is measured on a twin run of {s["lyapT_lo"]} to {s["lyapT_hi"]} transit '
            f'times with renormalisation (S49), from its second half. Figure {{{{scheme}}}} shows the loop that the '
            f'experiment exercises.'))
    A(('img', 'scheme', 15.5))
    A(('cap', 'Figure {{scheme}}. KAOS-GO. The pore scale is resolved only to produce a closure with its error; the '
              'adjoint of the Darcy-scale model says where the decision needs the closure, and the next pore-scale runs '
              'are chosen there.'))
    A(('p', 'The experiment is not the Princeton system. There a polymer solution becomes chaotic through elasticity '
            'at vanishing Reynolds number; here a Newtonian fluid becomes chaotic through inertia. A reliable '
            'simulation of elastic turbulence was out of reach for this note. The balance of Proposition 1 and the '
            'statistics of Proposition 2 have the same form in both, and it is those that are tested.'))
    A(('h2', '7.2 Gates'))
    A(('p', f'Four checks guard the results: three of the solver, run before any result was read, and one of the '
            f'statistics code, run before the long runs were analysed. (1) *Drag.* For a square array of cylinders in Stokes '
            f'flow the computed drag differs from the series of Sangani & Acrivos (S46) by {s.get("gate_drag10", "—")} at a '
            f'solid fraction of 0.10 and by {s.get("gate_drag20", "—")} at 0.20, where the truncated series is itself '
            f'less accurate (four lattices). (2) *Energy.* The dissipation computed from the '
            f'non-equilibrium populations equals the power of the force within {s.get("gate_budget", "—")} in those runs. '
            f'(3) *Resolution in the chaotic regime* (Table {{{{conv}}}}): the same cell at $\\mathrm{{Re}}\\approx 120$ on '
            f'three lattices. The flux and the Lyapunov exponent are already converged on the coarsest lattice '
            f'(permeability within {s.get("conv_K12", "—")} of the finest, exponents {s.get("conv_lyap", "—")}), but the '
            f'dissipation is not: its budget is off by {s.get("conv_budget", "—")}. The coarsest lattice fails this '
            f'gate and was not used; all results below are for 18 nodes per radius, where the budget closes within '
            f'{s["budget_worst"]} at every level. (4) *Statistics.* The interval code of Section 7.3 was run on synthetic '
            f'Gaussian series with a known correlation time of 1, 2.5 and 8 transit times, 24 records of 1200 transit '
            f'times each: it recovers the correlation time, and nominal 90% intervals cover {s.get("sg_conf", "—")} '
            f'when conformal, {s.get("sg_gk50", "—")} when the correlation is taken from a short record, and '
            f'{s.get("sg_naive", "—")} when one transit of memory is assumed. A correlation time of 30 was added '
            f'after the long runs (Section 7.3).'))
    A(('table', ['Nodes per grain radius', 'Cell, nodes', 'Re', 'K / a²', 'Dissipation minus power', 'Share of the mean flow',
                 'Fluctuation energy / mean-flow energy', 'Lyapunov exponent per transit'],
       s['conv_rows'], [2.0, 1.7, 1.3, 1.7, 2.4, 2.4, 2.9, 2.6], 9.0))
    A(('cap', 'Table {{conv}}. The same cell and the same dimensionless force on three lattices. The Lyapunov exponent is '
              'given with its standard error from batch means.'))
    A(('h2', '7.3 What the experiment shows'))
    A(('img', 'fields', 17.0))
    A(('cap', 'Figure {{fields}}. The cell (grains in grey; the force points to the right). (a) Mean speed in the Darcy '
              'regime. (b) Mean speed in the chaotic regime: the flow has reorganised into jets and wakes. (c) Energy of '
              'the velocity fluctuations in the same run: the unsteadiness is patchy.'))
    uns = [r for r in lev if r['unsteady']]
    ly = [r for r in lev if 'lyap_T' in r]
    per = [r for r in ly if not r['chaotic']]
    cha = [r for r in ly if r['chaotic']]
    lc = R.get('lyap_control')
    ctl_txt = (f' As a control, the same twin run at the steady level Re = {num(lc["Re"], 0)} gives '
               f'{num(lc["lyap_T"], 2)}: there a perturbation decays.') if lc else ''
    lyap_list = ', '.join(f"{num(r['lyap_T'], 2)} ± {num(r['lyap_T_se'], 2)} at Re = {num(r['Re'], 0)}" for r in cha)
    A(('p', f'**Regimes** (Figure {{{{macro}}}}). The resistance exceeds its Darcy value by only '
            f'{pct(at_re(lev, "F", 1.0) - 1, 1)} at $\\mathrm{{Re}}\\approx 1$ and then grows while the flow is still steady: '
            f'$F={s["F10"]}$ at Re = 10 and {s["F27"]} at Re = 27. The flow is steady up to Re = {s["onset_lo"]} and '
            f'unsteady from Re = {s["onset_hi"]}. It is first periodic: at Re = '
            f'{", ".join(num(r["Re"], 0) for r in per)} the largest Lyapunov exponent is zero within '
            f'{num(max(2 * r["lyap_T_se"] for r in per), 2)} per pore transit time, and one spectral line, at '
            f'{num(min(r["f_peak"] for r in per), 2)} to {num(max(r["f_peak"] for r in per), 2)} cycles per transit '
            f'time, carries more than {int(100 * min(r["peak_share"] for r in per))}% of the '
            f'variance of the flux. Then it is chaotic: the exponent is {lyap_list}, and the strongest line carries '
            f'at most {pct(max(r["peak_share"] for r in cha))}.{ctl_txt} '
            f'At the highest level two states that differ by one part in a million differ completely '
            f'after about {num(np.log(1e6) / max(float(hi.get("lyap_T", 1e-9)), 1e-9), 0)} transit times. There the '
            f'resistance is {s["F_hi"]} times the Darcy value.'))
    A(('img', 'macro', 16.5))
    A(('cap', 'Figure {{macro}}. Top: the resistance of the cell over its Darcy value, measured (circles) and split by '
              'Proposition 1 into the dissipation of the time-mean flow and of the fluctuations. Middle: the largest '
              'Lyapunov exponent per pore transit time, with two standard errors. Bottom: the number of grains around '
              'which the fluctuation energy of the fluid exceeds 5% of the kinetic energy at the pore velocity.'))
    A(('p', f'**Proposition 1.** The measured dissipation equals the power of the force within {s["budget_worst"]} at '
            f'every level. Part (iii) holds: the resistance is never below the Darcy value. At the highest level the '
            f'time-mean flow dissipates {s["mean_share_hi"]} and the fluctuations {s["fluct_share_hi"]}; in units of the '
            f'Darcy resistance the mean-flow part is {s["Fmean_hi"]} and the fluctuations add {s["Ffluct_hi"]}. '
            f'So in this inertial case most of the excess is the reshaped mean flow and a smaller '
            f'part the fluctuations, the reverse of the emphasis of the Princeton abstract and close to that of card C1; '
            f'the identity holds both. The fluctuation part appears with the first periodic level '
            f'({pct(uns[0]["fluct_share"] / uns[0]["budget"], 1)} of the dissipation at Re = {num(uns[0]["Re"], 0)}): '
            f'Proposition 1 needs an unsteady flow, not a chaotic one. It is Proposition 2 that needs the chaos.'))
    A(('p', f'**Patchiness.** The unsteadiness does not start everywhere. It spreads from grain to grain, as in the '
            f'Princeton medium, where each pore has its own onset: of the {s["grains_n"]} grains, the fluid around '
            f'{s["grain_list"]}, and around all of them from Re = {s["grains_full_re"]}, fluctuates strongly (a grain '
            f'counts when the fluctuation energy of the fluid nearest to it exceeds 5% of the kinetic energy at the '
            f'pore velocity; Figure {{{{fields}}}}c). At the highest level the fluctuation energy reaches '
            f'{s["tke_hi"]} of the energy of the mean flow. The dissipation is concentrated in every regime: half of '
            f'it takes place in {s["half_area_lo"]} of the pore space in the Darcy regime and in {s["half_area_hi"]} '
            f'at the highest level.'))
    if 'rev_slope' in s:
        A(('p', f'**The law of large numbers in space** (Figure {{{{rev}}}}). In the Darcy regime the coefficient '
                f'$K/a^{{2}}$ was computed for {s["rev_m4"]} cells of 4 grains, {s["rev_m16"]} of 16 and {s["rev_m64"]} of '
                f'64. It scatters between cells by {s["rev_cv4"]}, {s["rev_cv16"]} and {s["rev_cv64"]}: the scatter decays '
                f'with exponent {s["rev_slope"]} in the number of grains, against −0.5 for independent grains. The mean '
                f'of the smallest cells differs from that of the largest by {s["rev_bias"]} (standard error '
                f'{s["rev_bias_se"]}): the systematic error of a small periodic cell, the subject of card P2. A '
                f'16-grain cell, the size used above, therefore fixes the Darcy coefficient of "the medium" only '
                f'to {s["rev_cv16"]}; the cell of the sweep itself ($K/a^{{2}}={s["K0"]}$) lies {s["cell_z"]} standard '
                f'deviations below the mean of its size class.'))
        A(('img', 'rev', 16.5))
        A(('cap', 'Figure {{rev}}. The Darcy coefficient of finite periodic cells of randomly placed grains. (a) One '
                  'point per cell; the dashed line is the mean of the largest cells. (b) The scatter between cells '
                  'against the number of grains.'))
    if R.get('long'):
        time_block(A, R, s, lev)
    A(('p', f'**The closure and its form error.** A Forchheimer law, $F=1+b\\,\\mathrm{{Re}}$, fitted to the steady '
            f'levels misses the unsteady levels by up to {s.get("forch_err", "—")}; left out one at a time, the levels '
            f'are predicted with a root-mean-square error of {s.get("forch_loo", "—")} by the Forchheimer law and of '
            f'{s["best_loo"]} by the best of four candidate laws, {s["best_law"]}. These leave-one-out errors are the '
            f'scores from which a certificate of the closure between levels takes its width.'))
    d = R['decision']
    if 'gain' in d:
        A(('p', f'**A decision and the design** (Figure {{{{design}}}}). Take the head loss of radial flow towards a '
                f'well, the Reynolds number falling from {s["Re_w"]} at the screen to {s["re_lo"]} far away. The loss '
                f'over its Darcy value is the average of $F$ over the logarithm of the radius, here {s["I"]}: a '
                f'non-Darcy well loss of {pct(d["I"] - 1)}. Each level enters with a weight (panel a). With the '
                f'{s["Wtot"]} transit times that the unsteady levels received in the sweep, split equally, the '
                f'time-averaging error of the loss is {s["sd_equal"]}; allocated by Proposition 3 it is {s["sd_opt"]}, '
                f'a variance lower by {s["alloc_gain"]} (the noise of each level is taken from its longest record; '
                f'where that is a sweep run it is a lower estimate, as the long run at Re = {s["slow_re"]} shows). '
                f'Both are small beside the error that comes from having one cell of 16 '
                f'grains: the Darcy coefficient, which multiplies the whole loss, scatters by {s.get("sd_cell", "—")} '
                f'between such cells (the scatter of $F$ itself between cells was not measured). The design '
                f'conclusion is therefore not "run longer" but "run more cells": the goal-oriented view changes what '
                f'the next experiment is.'))
        A(('img', 'design', 16.5))
        A(('cap', 'Figure {{design}}. (a) Share of each level in the non-Darcy head loss of a well. (b) Sampling time of '
                  'the unsteady levels under an equal split and under Proposition 3.'))
    A(('h2', '7.4 What the experiment does not show'))
    A(('b', 'It is two-dimensional, with one arrangement of 16 grains in the unsteady regime; the scatter between '
            'cells was measured in the Darcy regime only.'))
    A(('b', 'The chaos is inertial, not elastic. The dissipation split of a polymer solution has a further term, the '
            'work of the elastic stress.'))
    A(('b', 'The certificate was tested on window means of the flux, where the truth is known. Its transfer to a '
            'field decision by adjoints is the subject of SALTPROOF and is not tested here.'))
    A(('b', f'The long memory at Re = {s["slow_re"]} was measured on one lattice and in one record of '
            f'{s["long_T"]} transit times, which amounts to only about seventeen independent samples; it was not repeated on '
            f'another lattice or cell, and its length is uncertain.'))
    A(('b', 'The Lyapunov exponent is that of the lattice-Boltzmann dynamics. It agrees between three lattices, which '
            'speaks against a numerical origin, but no continuum reference exists for this cell.'))
    A(('b', f'The lattice-Boltzmann fluid is weakly compressible. The Mach number of the root-mean-square velocity '
            f'reaches {num(max(r["umax"] for r in lev) * 3 ** 0.5, 2)} at the fastest point of the highest level, and it '
            f'is the same on the three lattices: the resolution study does not test this error, which is of the order '
            f'of the square of the Mach number, about 1%.'))
    # ---------------------------------------------------------------------------------------------- 8 coastal aquifers
    A(('h', '8. What it means for a coastal aquifer'))
    A(('p', 'Where does any of this touch a coastal alluvial aquifer? In five places, in decreasing order of '
            'certainty.'))
    A(('b', '**In the body of the aquifer nothing changes for the flow.** With a Darcy velocity of a metre per day '
            'and grains of two millimetres the Reynolds number is about 0.02: the velocity field in the pores is '
            'steady and Darcy\'s law holds. What is chaotic is the path of a fluid particle (kind 2 of Table '
            '{{kinds}}), and it controls the width of the mixing zone between fresh and salt water and the rate of '
            'the reactions in it (S11, S14, S18). A transverse dispersivity that is treated as a constant of the '
            'medium is a summary of this chaos.'))
    A(('b', f'**Near a supply well in gravel the flow leaves the Darcy regime.** A well that yields 50 litres per '
            f'second through a screen of 0.15 m radius and 20 m length has a Darcy velocity of 2.7 mm/s at the '
            f'screen; in a gravel pack of 10 mm grains the Reynolds number is about 27. In our cell the resistance at '
            f'that Reynolds number is {s["F27"]} times the Darcy value. This is the term $CQ^{{2}}$ of the '
            f'step-drawdown test (S44, S45): the one place where pore-scale inertia is routinely seen in field data. '
            f'The numbers of a two-dimensional array are indicative only.'))
    A(('b', '**Polymer and biopolymer injections** for remediation or for the control of clogging are the Princeton '
            'case in an aquifer: an apparent viscosity that rises with the rate, and better mixing (A1, A4, S50).'))
    A(('b', '**Salinisation from above**, after overwash or a storm surge, is an unstable density stratification: '
            'chaotic fingers with a reproducible flux law (M3, P4, S28, S29).'))
    A(('b', '**Tides** force the flow in time through a heterogeneous, compressible aquifer and can make the '
            'Darcy-scale paths chaotic near the shore (S16, S17).'))
    A(('p', 'This suggests four papers, in the order of what can be done first. (A) *Step-drawdown tests designed to '
            'discriminate non-Darcy laws*, with certified well-loss predictions: T-optimal pumping steps (S59), the '
            'tools of certain-coast, field tests on supply wells; low risk, of direct use to an operator. (B) '
            '*Certified upscaling*: KAOS-GO on three-dimensional pore-scale simulations, with a partner who has the '
            'solver. (C) *Reading the pore scale from the column scale*: a Bayesian inversion of the distribution of '
            'pore-scale onsets from the resistance curve and its fluctuations, with designed flow rates, on data of '
            'the Princeton type. Section 7.3 adds a hypothesis that needs no imaging: if the memory of the flux is '
            'longest just above the onset, as in our cell, the correlation time of the pressure drop across a core '
            'marks the onset and measures the rate of the chaos. (D) *The geometry of model error from homogenisation* (card P1), as the theory part '
            'of SALTPROOF.'))
    # ---------------------------------------------------------------------------------------------- 9 partners
    A(('h', '9. With whom to work'))
    A(('p', 'Table {{partners}} lists groups whose published work, cited in this review, matches one of the four '
            'papers. Affiliations are those on the cited papers (OpenAlex records, November 2026) and should be '
            'checked before writing; no contact has been made. The order within each block is the order in which we '
            'would write.'))
    A(('table', ['Group (affiliation on the cited paper)', 'Evidence here', 'What they have', 'What we bring', 'A first step'], [
        ['**The phenomenon**', '', '', '', ''],
        ['S. S. Datta (Caltech since 2024; Princeton before)', 'A1–A5, C1, C2',
         'Imaging of pore-scale flow in 3-D media; resistance curves with the pore-scale dissipation',
         'The fluctuation term and the certificate; design of the flow rates; the inverse problem of paper C',
         'Ask for the data behind the resistance curve of A1; send the two-page idea of paper C'],
        ['S. J. Haward, A. Q. Shen (Okinawa Institute of Science and Technology)', 'S19, C1',
         'Microfabricated ordered 3-D media; control of the geometry', 'Designs that discriminate onset laws', 'After the first'],
        ['J. S. Guasto (Tufts University)', 'S20, M1', 'Microfluidic arrays with controlled disorder',
         'Statistics of patchy onsets; certificates in disorder', 'After the first'],
        ['**Mixing in groundwater**', '', '', '', ''],
        ['T. Le Borgne, J. Heyman, Y. Méheust (Géosciences Rennes, CNRS); D. R. Lester (RMIT University)', 'S11–S15',
         'Experiments and theory of chaotic mixing in porous media, pore to Darcy scale',
         'A coastal variable-density model with adjoints; mixing-zone data needs',
         'Ask how the Lyapunov exponent of S14 enters a transverse dispersivity for the Henry problem'],
        ['M. Dentz (IDAEA-CSIC, Barcelona)', 'S15, S18, S58', 'Upscaling of mixing and transport', 'Certified versions of upscaled transport laws',
         'Same question, from the upscaling side'],
        ['**Tools that match ours, and near**', '', '', '', ''],
        ['R. Sethi, T. Tosco, D. L. Marchisio, G. Boccardo (Politecnico di Torino)', 'S50, S51',
         'Darcy–Forchheimer laws of shear-thinning fluids from pore-scale simulation; aquifer remediation',
         'Certificates and designs for those laws', 'Paper B on their pore-scale simulations: the most direct match'],
        ['G. J. Houben (Federal Institute for Geosciences and Natural Resources, Hannover)', 'S45',
         'Hydraulics of water wells, non-Darcy flow near screens', 'T-optimal step tests; field wells', 'Paper A: ask for comments on the test design'],
        ['W. Nowak, A. Guthke (University of Stuttgart); H. Steeb, H. Class, I. Rybak (Stuttgart)', 'S52–S54',
         'Bayesian model selection and design in hydrogeology; pore-scale benchmarks and microfluidics',
         'Decision-level guarantees; the coastal case', 'A visit or a joint student on design under model error'],
        ['A. G. Yiotis (Technical University of Crete)', 'S55', 'Pore-scale experiments and lattice-Boltzmann simulation',
         'KAOS-GO analysis of their data', 'The nearest laboratory: propose a joint test of Figure {{clt}} on a micromodel'],
        ['M. S. Valavanides (University of West Attica)', 'S56', 'Rate dependence of steady two-phase flow in pore networks',
         'Certificates for rate-dependent laws', 'Exchange of notes'],
        ['G. Porta, A. Guadagnini (Politecnico di Milano)', 'S57', 'Pore-to-continuum transport with uncertainty', 'Goal-oriented design',
         'Exchange of notes'],
        ['**Theory and learned closures**', '', '', '', ''],
        ['F. Otto (Max Planck Institute for Mathematics in the Sciences, Leipzig)', 'P1, P2, S31–S33', 'The theory of fluctuations in homogenisation',
         'A use of it: geometry of model error for decisions', 'Paper D: send a short note with the question, not a request'],
        ['B. Fehrman (Oxford on O2, O3); B. Gess (Bielefeld and MPI Leipzig)', 'O2, O3', 'Noise terms and large deviations of upscaled laws',
         'A physical case and numbers', 'After paper D exists'],
        ['K. Bhattacharya, A. M. Stuart (Caltech)', 'C3–C5, S40', 'Learned homogenisation and closures', 'Guarantees and design for them', 'Cite; write when paper B has results'],
        ['I. M. Griffiths, C. W. MacMinn, M. P. Dalwadi (Oxford)', 'O1, O5, M2, S43', 'Homogenisation of structured media; polymer flow',
         'Fluctuation and certificate', 'Cite; write when paper B has results'],
        ['R. Juanes (MIT)', 'M2, M3, M5', 'Pore-scale and metre-scale experiments, repeated runs', 'Certificates from repeated runs', 'Cite'],
        ['X. Zhu (MPI for Solar System Research), M. De Paoli (TU Wien, Twente), D. Lohse (Twente, MPI Göttingen)', 'P3, P4, S29',
         'Convection in porous media, resolved and Darcy', 'The coastal salinisation case', 'Cite; ask about the flux law for a Henry-type model'],
        ['D. A. Weitz, A. Amir, M. P. Brenner (Harvard)', 'H1–H4', 'Micromodels; network theory; differentiable simulation', 'Design and guarantees', 'Cite'],
    ], [3.6, 1.7, 3.9, 3.9, 3.9], 8.6, False))
    A(('cap', 'Table {{partners}}. Possible partners, tied to the papers cited in this review. The existing partner of '
              'CERTAIN-COAST at Qatar University could be asked whether its petroleum-engineering laboratories run '
              'polymer core floods, which are the Princeton experiment at the core scale.'))
    A(('p', 'Three contacts are worth making first, because each needs little from the other side. Politecnico di '
            'Torino has pore-scale simulations of non-Newtonian flow on which paper B can be done at once. G. J. '
            'Houben wrote the review of well hydraulics on which paper A rests. S. S. Datta has the data of the '
            'article that started the question; a precise request for the resistance curve and the measured '
            'dissipation, with one page on what we would do with them, is a reasonable first letter. Staff exchanges '
            'and joint doctoral supervision under the usual European instruments would follow results, not precede '
            'them.'))
    # ---------------------------------------------------------------------------------------------- 10 cards
    A(('h', '10. The twenty-five papers'))
    A(('p', 'Five papers per institution, 2020–2026, each with its link. Selection: about forty candidates from a '
            'Crossref sweep by topic and affiliation and from web searches were verified one by one; those kept are '
            'the ones that bear most directly on the passage from an irregular small scale to a large-scale law in a '
            'porous medium, across the five routes. Every card states what the paper does (from its abstract), how it '
            'explains the passage, what it leaves open for our question, and the innovation step for us.'))
    rname = dict(see='seeing it', hom='homogenisation', stat='statistics', diss='dissipation', learn='learning')

    def short_authors(c):
        fam = [a.strip().split(' ')[-1] for a in c['authors'].split(',')]
        return fam[0] + ' et al.' if len(fam) > 3 else (', '.join(fam[:-1]) + ' & ' + fam[-1] if len(fam) > 1 else fam[0])
    A(('table', ['', 'Paper', 'Journal', 'Route'],
       [[c['id'], f"{short_authors(c)} ({c['year']}). [{c['title']}]({c['links'][0][1]})",
         re.sub(r'\s*\(\d{4}[^)]*\)$', '', c['venue']), ', '.join(rname[r] for r in c['routes'])] for c in cards],
       [0.9, 9.1, 4.1, 2.9], 8.6, False))
    A(('cap', 'Table {{list}}. The twenty-five papers at a glance; the titles are links to the DOI. C Caltech, O Oxford, M '
              'MIT, H Harvard, P Max Planck Society.'))
    for inst in INST_ORDER:
        A(('h2', {'Caltech': '10.1 California Institute of Technology', 'Oxford': '10.2 University of Oxford',
                  'MIT': '10.3 Massachusetts Institute of Technology', 'Harvard': '10.4 Harvard University',
                  'Max Planck': '10.5 Max Planck Society'}[inst]))
        for c in cards:
            if c['inst'] == inst:
                A(('card', c))
    A(('refs',))
    return B, s, cards
