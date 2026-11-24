"""Two readings of the major ions of the four wells of Cenameri & Beqiraj (2016): conservative mixing with seawater,
and fresh water plus sodium chloride.
usage: python -I fk_ions.py WORKBOOK.xlsx OUT.json
The workbook is data of the chloride manuscript; the output is not for the public repository."""
import json
import sys

import openpyxl

MW = dict(Na=22.990, K=39.098, Ca=40.078, Mg=24.305, Cl=35.453, SO4=96.06, HCO3=61.017, NO3=62.005)
Z = dict(Na=1, K=1, Ca=2, Mg=2, Cl=1, SO4=2, HCO3=1, NO3=1)
# reference composition of seawater, g/kg at S = 35.165 (Millero et al. 2008, Table 4): ratios to chloride by mass
SEA = dict(Na=10.78145, Mg=1.28372, Ca=0.41208, K=0.39910, Cl=19.35271, SO4=2.71235, HCO3=0.10481)
CL_SEA = (20500.0, 21000.0, 22000.0)        # mg/L, the interval used for the sea in HYPOTHESIS-GO, and its centre
ERR = 0.05                                  # assumed analytical error of each ion


def meq(ion, mg):
    return mg / MW[ion] * Z[ion]


def main(xlsx, out):
    ws = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)['5_Cenameri2016_Chemistry']
    rows = [r for r in ws.iter_rows(values_only=True)]
    hdr = next(r for r in rows if r and r[0] == 'Well_no')
    col = {h.replace('_mg_L', ''): i for i, h in enumerate(hdr) if h}
    W = {}
    for r in rows:
        if r and str(r[0]) in ('503', '341', '340', '193'):
            W[str(r[0])] = {k: float(r[col[k]]) for k in ('Na', 'K', 'Ca', 'Mg', 'Cl', 'SO4', 'HCO3', 'NO3')}
    f = W['193']
    res = {}
    for w in ('503', '341', '340'):
        x = W[w]
        cat = sum(meq(i, x[i]) for i in ('Na', 'K', 'Ca', 'Mg')); an = sum(meq(i, x[i]) for i in ('Cl', 'SO4', 'HCO3', 'NO3'))
        d = dict(cl=x['Cl'], balance=100 * (cat - an) / (cat + an))
        d['ratio_added'] = ((x['Na'] - f['Na']) / MW['Na']) / ((x['Cl'] - f['Cl']) / MW['Cl'])
        lo = ((x['Na'] * (1 - ERR) - f['Na'] * 1.5) / MW['Na']) / ((x['Cl'] * (1 + ERR) - f['Cl'] * 0.5) / MW['Cl'])
        hi = ((x['Na'] * (1 + ERR) - f['Na'] * 0.5) / MW['Na']) / ((x['Cl'] * (1 - ERR) - f['Cl'] * 1.5) / MW['Cl'])
        d['ratio_range'] = [lo, hi]
        frac = (x['Cl'] - f['Cl']) / (CL_SEA[1] - f['Cl'])
        d['sea_fraction'] = frac
        sea, salt = {}, {}
        for i in ('Na', 'K', 'Ca', 'Mg', 'SO4'):
            xs = SEA[i] / SEA['Cl'] * CL_SEA[1]
            mix = f[i] + frac * (xs - f[i])
            sea[i] = meq(i, x[i]) - meq(i, mix)
            nacl = f[i] + ((x['Cl'] - f['Cl']) * MW['Na'] / MW['Cl'] if i == 'Na' else 0.0)
            salt[i] = meq(i, x[i]) - meq(i, nacl)
        # sign of the sodium departure from seawater mixing over the errors and the interval of the sea
        dn = []
        for cs in (CL_SEA[0], CL_SEA[2]):
            for en in (1 - ERR, 1 + ERR):
                for ec in (1 - ERR, 1 + ERR):
                    for ef in (0.5, 1.5):
                        fr = (x['Cl'] * ec - f['Cl']) / (cs - f['Cl'])
                        mix = f['Na'] * ef + fr * (SEA['Na'] / SEA['Cl'] * cs - f['Na'] * ef)
                        dn.append(meq('Na', x['Na'] * en) - meq('Na', mix))
        d.update(sea=sea, salt=salt, sum_sea=sum(abs(v) for v in sea.values()), sum_salt=sum(abs(v) for v in salt.values()),
                 dNa_range=[min(dn), max(dn)], mg=dict(x))
        res[w] = d
    res['fresh'] = dict(f)
    res['sea_ratio_molar'] = (SEA['Na'] / MW['Na']) / (SEA['Cl'] / MW['Cl'])
    json.dump(res, open(out, 'w'), indent=1)
    for w in ('503', '341', '340'):
        d = res[w]
        print(w, 'Cl %.0f' % d['cl'], 'bal %.1f%%' % d['balance'], 'Na/Cl added %.2f [%.2f, %.2f]' % (d['ratio_added'], *d['ratio_range']),
              'f_sea %.4f' % d['sea_fraction'], '| sea-mixing departures', {k: round(v, 2) for k, v in d['sea'].items()},
              'sum %.2f' % d['sum_sea'], '| NaCl departures', {k: round(v, 2) for k, v in d['salt'].items()}, 'sum %.2f' % d['sum_salt'],
              '| dNa range [%.2f, %.2f]' % tuple(d['dNa_range']))
    print('sea Na/Cl molar %.3f' % res['sea_ratio_molar'])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
