"""The West Coast Basin data (Land et al., 2004, USGS SIR 2004-5067) and the four-source model built from them.

The data are public (U.S. Geological Survey).  They are not stored in this repository: get_data.sh downloads the report
and the two parsers write appA.csv (Appendix A: well construction and water chemistry) and table2.csv (Table 2: the
authors' source interpretation per well) into the directory named by WRR_DATA (default: ./data).

Sources (the water types of Land et al., 2004): N native ground water, S seawater, I imported water injected at the
seawater barriers, B oil-field brine.  Intervals are set by fixed rules stated next to each one; the rules are the same for every well."""
import csv
import math
import os

import numpy as np

from field_model import Model

DATA = os.environ.get('WRR_DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
SOURCES = ['N', 'S', 'I', 'B']
NAMES = {'N': 'native ground water', 'S': 'seawater', 'I': 'imported (injected) water', 'B': 'oil-field brine'}
TRACERS = ['Cl', 'Br', 'I', 'B', 'd18O', 'd2H', 'H3']

# measurement error (sd = rel * value + abs), our assumption except where Land et al. (2004) state the precision:
# d2H and d18O "better than +-2.0 and 0.2 per mil", read here as two standard deviations
NOISE = {'Cl': (0.03, 0.5), 'Br': (0.05, 0.01), 'I': (0.05, 0.002), 'B': (0.05, 0.01), 'd18O': (0.0, 0.1),
         'd2H': (0.0, 1.0), 'H3': (0.05, 0.05)}
CL_CLASS = {'Br': 'cl', 'I': 'cl', 'B': 'cl', 'd18O': 'w', 'd2H': 'w', 'H3': 'w'}
SIDE = {'Br': 'two', 'I': 'gain', 'B': 'loss', 'd18O': 'two', 'd2H': 'two', 'H3': 'two'}


def _f(r, k):
    v = r.get(k, '')
    return float(v) if v not in ('', None) else math.nan


def load():
    appA = list(csv.DictReader(open(os.path.join(DATA, 'appA.csv'), encoding='utf-8')))
    t2 = {}
    for r in csv.DictReader(open(os.path.join(DATA, 'table2.csv'), encoding='utf-8')):
        name = r['name'].replace('+', '-').replace('Chicago-1', 'Chicago #1')
        t2[name] = r
    return appA, t2


def obs_of(r, flags=None):
    """Observation dict of one Appendix A row: t -> (value, cens) in model units (B in mg/L).  Bromide (and iodide)
    flagged '*' in Table 2 (colorimetric interference, Land et al. 2004) are treated as missing."""
    flags = flags or {}
    o = {}
    for t in TRACERS:
        v = _f(r, t)
        if math.isnan(v):
            continue
        if t == 'B':
            v = v / 1000.0
        if t == 'Br' and flags.get('clbr') == '*':
            continue
        if t == 'I' and flags.get('cli') == '*':
            continue
        o[t] = (v, r.get(t + '_cens', '') or '')
    return o


def sd_of(t, y):
    rel, ab = NOISE[t]
    return rel * abs(y) + ab


def eps_of(obs, k=2.5):
    return {t: k * sd_of(t, v[0]) for t, v in obs.items()}


def sd_dict(obs):
    return {t: sd_of(t, v[0]) for t, v in obs.items()}


def native_wells(t2):
    """Wells that Land et al. (2004) classify as native by all four tracer columns (no interference flags)."""
    return [n for n, r in t2.items() if all(r[c] == 'N' for c in ('clbr', 'cli', 'clb', 'iso'))]


def hull(rows, fun, pad_rel=0.0, pad_abs=0.0):
    x = np.array([fun(r) for r in rows], float)
    x = x[np.isfinite(x)]
    lo, hi = x.min(), x.max()
    return [lo - pad_rel * abs(lo) - pad_abs, hi + pad_rel * abs(hi) + pad_abs]


def build_model(appA=None, t2=None):
    """The four-source model with its interval rules.  Returns (Model, notes) where notes documents each rule."""
    if appA is None:
        appA, t2 = load()
    by = {r['name']: r for r in appA}
    nat = [by[n] for n in native_wells(t2) if n in by]
    imp = [by['WB-#37(imported)'], by['351-E'], by['351-G']]
    ratio = lambda t, scale=1.0: (lambda r: _f(r, t) * scale / _f(r, 'Cl'))
    notes = {}
    # ---- native ground water: hull of the wells the authors call native by every tracer, padded by 2 sd
    N = dict(Cl=hull(nat, lambda r: _f(r, 'Cl'), 0.06),
             Br=hull(nat, ratio('Br'), 0.10), I=hull(nat, ratio('I'), 0.10), B=hull(nat, ratio('B', 1e-3), 0.10),
             d18O=hull(nat, lambda r: _f(r, 'd18O'), 0, 0.2), d2H=hull(nat, lambda r: _f(r, 'd2H'), 0, 2.0),
             d=hull(nat, lambda r: _f(r, 'd2H') - 8 * _f(r, 'd18O'), 0, 2.0), H3=[0.0, 6.0])
    N['I'][0] = 0.0      # iodide can only be gained in the aquifer, so recharge may carry none
    notes['N'] = (f'hull of the {len(nat)} wells classified native by all four tracers in Table 2, padded by two '
                  f'standard deviations; iodide from zero (it can only be gained in the aquifer); tritium up to 6 TU (local '
                  f'recent recharge, Long Beach-2 #5 has 5.2 TU)')
    # ---- seawater: the composition listed in Appendix A (after Hem, 1992), with the standard spread
    S = dict(Cl=[18500.0, 20000.0], Br=[3.35e-3, 3.70e-3], I=[1e-6, 1e-5], B=[2.2e-4, 2.5e-4],
             d18O=[-0.5, 0.5], d2H=[-4.0, 4.0], d=[-5.0, 5.0], H3=[0.0, 3.0])
    notes['S'] = ('Appendix A: Cl 19,000 mg/L, Br 67 mg/L, iodide 0.06 mg/L, boron 4,500 ug/L, d18O and d2H 0 per mil; '
                  'tritium not measured: 0 to 3 TU assumed')
    # ---- imported water: hull of the pipeline sample WB #37 and of 351-E, 351-G (at least 90% imported water)
    I_ = dict(Cl=hull(imp, lambda r: _f(r, 'Cl'), 0.15), Br=hull(imp, ratio('Br'), 0.25),
              I=[0.0, 2e-4], B=hull(imp, ratio('B', 1e-3), 0.15),
              d18O=hull(imp, lambda r: _f(r, 'd18O'), 0, 0.4), d2H=hull(imp, lambda r: _f(r, 'd2H'), 0, 4.0),
              d=hull(imp, lambda r: _f(r, 'd2H') - 8 * _f(r, 'd18O'), 0, 2.0), H3=[0.1, 100.0])
    notes['I'] = ('hull of WB #37 (the pipeline that feeds the Dominguez Gap barrier) and of 351-E and 351-G, which the '
                  'authors find at least 90% imported water; iodide up to 2e-4 of chloride (WB #37 has 1.3e-5); '
                  'tritium 0.1 to 100 TU (11.2 TU at WB #37 in 1999; wells with bomb-era injected water have more, up to 22 TU; '
                  'the upper end allows decayed water injected in the 1960s and is our assumption)')
    # ---- oil-field brine: Appendix A lists one brine (Piper & Garrett, 1953); ranges from the text of the report
    Bv = dict(Cl=[10000.0, 40000.0], Br=[7.77e-3, 3.22e-2], I=[1.0e-3, 5.0e-3], B=[1.5e-3, 4.0e-3],
              d18O=[-8.0, 4.0], d2H=[-65.0, 0.0], d=[-100.0, 100.0], H3=[0.0, 0.2])
    notes['B'] = ('Cl 10,000-40,000 mg/L around the 23,400 mg/L of Appendix A; Cl/Br molar ratio 70 to 290 (the report: '
                  'below 290 is presumptive evidence of brine, as low as 70 in oil-field waste); iodide 30-80 mg/L near '
                  'San Pedro Bay; boron 70,950 ug/L; the isotopic composition is "not well defined" in the study area, '
                  'so d18O and d2H are wide by assumption; old water, tritium below 0.2 TU')
    src = [N, S, I_, Bv]
    cl = np.array([s['Cl'] for s in src])
    tr = {}
    for t in ('Br', 'I', 'B', 'd18O', 'd2H', 'H3'):
        tr[t] = dict(cls=CL_CLASS[t], side=SIDE[t], sig=np.array([s[t] for s in src]))
    tr['Br']['sig'][:, 0] = np.maximum(tr['Br']['sig'][:, 0], 0)
    tr['I']['sig'][:, 0] = np.maximum(tr['I']['sig'][:, 0], 0)
    tr['B']['sig'][:, 0] = np.maximum(tr['B']['sig'][:, 0], 0)
    joint = [dict(a='d2H', b='d18O', coef=8.0, lo=np.array([s['d'][0] for s in src]),
                  hi=np.array([s['d'][1] for s in src]))]
    return Model(SOURCES, cl, tr, joint), notes


# reported end-member values, for the fixed-signature (IsoSource-type) comparator; others at interval midpoints
def fixed_values(appA=None):
    if appA is None:
        appA, _ = load()
    by = {r['name']: r for r in appA}
    wb, sw, ob = by['WB-#37(imported)'], by['Seawater'], by['Oil-field brine']
    nat_ref = [by[n] for n in ('Long Beach-2 #2', 'Long Beach-2 #3', 'Long Beach-2 #4') if n in by]
    mean = lambda rows, fun: float(np.mean([fun(r) for r in rows]))
    vals = {
        'Cl': [mean(nat_ref, lambda r: _f(r, 'Cl')), _f(sw, 'Cl'), _f(wb, 'Cl'), _f(ob, 'Cl')],
        'Br': [mean(nat_ref, lambda r: _f(r, 'Br') / _f(r, 'Cl')), _f(sw, 'Br') / _f(sw, 'Cl'),
               _f(wb, 'Br') / _f(wb, 'Cl'), _f(ob, 'Br') / _f(ob, 'Cl')],
        'I': [mean(nat_ref, lambda r: _f(r, 'I') / _f(r, 'Cl')), _f(sw, 'I') / _f(sw, 'Cl'),
              _f(wb, 'I') / _f(wb, 'Cl'), _f(ob, 'I') / _f(ob, 'Cl')],
        'B': [mean(nat_ref, lambda r: _f(r, 'B') / 1000 / _f(r, 'Cl')), _f(sw, 'B') / 1000 / _f(sw, 'Cl'),
              _f(wb, 'B') / 1000 / _f(wb, 'Cl'), _f(ob, 'B') / 1000 / _f(ob, 'Cl')],
        'd18O': [mean(nat_ref, lambda r: _f(r, 'd18O')), 0.0, _f(wb, 'd18O'), -2.0],
        'd2H': [mean(nat_ref, lambda r: _f(r, 'd2H')), 0.0, _f(wb, 'd2H'), -32.5],
        'H3': [0.05, 1.5, _f(wb, 'H3'), 0.1],
    }
    return vals


def charge_balance(appA=None):
    """Charge balance of the samples with complete major ions (Ca, Mg, Na, alkalinity, Cl), as a check of the extraction.
    The Hawthorne-1 rows are excluded: their printed cation columns repeat the anion values."""
    if appA is None:
        appA, _ = load()
    n = lt4 = b48 = 0
    worse = []
    for r in appA:
        if not r['date'] or r['name'].startswith('WB') or r['name'].startswith('Hawthorne-1'):
            continue
        ca, mg, k, na, alk, cl, so4, br = [_f(r, x) for x in ('Ca', 'Mg', 'K', 'Na', 'Alk', 'Cl', 'SO4', 'Br')]
        if any(math.isnan(x) for x in (ca, mg, na, cl, alk)):
            continue
        cat = ca / 20.039 + mg / 12.153 + (0 if math.isnan(k) else k / 39.098) + na / 22.990
        an = alk / 50.04 + cl / 35.453 + (0 if math.isnan(so4) else so4 / 48.03) + (0 if math.isnan(br) else br / 79.904)
        d = 100 * (cat - an) / (cat + an)
        n += 1
        if abs(d) < 4:
            lt4 += 1
        elif abs(d) < 8:
            b48 += 1
        else:
            worse.append((r['name'], round(d, 1)))
    return dict(n=n, lt4=lt4, b48=b48, worse=worse)
