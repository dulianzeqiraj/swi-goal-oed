"""Hydrochemistry of the four analyses of Cenameri and Beqiraj (2016): seawater fraction, deviations from
conservative mixing, Na/Cl, Revelle ratio and base-exchange index. Writes results/hydrochem.json.

    f   = (Cl - Cl_f) / (Cl_sw - Cl_f)                   fresh end-member: well 193
    dX  = X_obs - [X_f + f (X_sw - X_f)]  [meq/L]        X = Na, Ca, Mg, K, SO4
    BEX = Na + K + Mg - 1.0716 Cl         [meq/L]        Stuyfzand (2008): < 0 salinization, > 0 freshening
Seawater: standard seawater (Millero et al., 2008) scaled to the southern Adriatic, S = 38.3, rho = 1.0285.
Same formulas as matlab/fkcl_hydrochem.m.
"""
import json
import os
import pandas as pd
import fkcl_model as M

SW35 = dict(Cl=19353, Na=10781, Mg=1284, Ca=412, K=399, SO4=2712, HCO3=145)     # mg/kg at S = 35
S_ADR, RHO_SW = 38.3, 1.0285
MOLAR = dict(Cl=35.453, Na=22.990, Ca=40.078, Mg=24.305, K=39.098, HCO3=61.017, SO4=96.06)
CHARGE = dict(Cl=1, Na=1, Ca=2, Mg=2, K=1, HCO3=1, SO4=2)
RES = os.path.join(os.path.dirname(__file__), '..', 'results')


def meq(ion, mg):
    return mg / MOLAR[ion] * CHARGE[ion]


def main():
    sw = {k: v * S_ADR / 35 * RHO_SW for k, v in SW35.items()}
    raw = pd.read_excel(M.fk.default_xlsx(), sheet_name='5_Cenameri2016_Chemistry', header=None)
    hdr = raw.index[raw[0].astype(str).str.strip() == 'Well_no'][0]
    ch = raw.iloc[hdr + 1:].copy(); ch.columns = raw.iloc[hdr].astype(str).str.strip()
    ch = ch[pd.to_numeric(ch['Well_no'], errors='coerce').notna()]
    col = lambda ion: ch[f'{ion}_mg_L'].astype(float).to_numpy()
    well = ch['Well_no'].astype(int).astype(str).tolist()
    X = {ion: col(ion) for ion in ['Cl', 'Na', 'Ca', 'Mg', 'K', 'SO4', 'HCO3']}
    i0 = well.index('193')
    f = (X['Cl'] - X['Cl'][i0]) / (sw['Cl'] - X['Cl'][i0])
    out = []
    for k, w in enumerate(well):
        d = {}
        for ion in ['Na', 'Ca', 'Mg', 'K', 'SO4']:
            mix = X[ion][i0] + f[k] * (sw[ion] - X[ion][i0])
            d['d' + ion] = round(float(meq(ion, X[ion][k]) - meq(ion, mix)), 4)
        d.update(well=w, f=round(float(f[k]), 4), Cl=float(X['Cl'][k]), Na=float(X['Na'][k]),
                 TDS=float(ch['Mp_TDS_mg_L'].astype(float).iloc[k]),
                 NaCl=round(float((X['Na'][k] / MOLAR['Na']) / (X['Cl'][k] / MOLAR['Cl'])), 4),
                 revelle=round(float(meq('Cl', X['Cl'][k]) / meq('HCO3', X['HCO3'][k])), 4),
                 BEX=round(float(meq('Na', X['Na'][k]) + meq('K', X['K'][k]) + meq('Mg', X['Mg'][k])
                                 - 1.0716 * meq('Cl', X['Cl'][k])), 4))
        out.append(d)
    pos = dict(zip(well, ch['Transect_position'].astype(str)))
    res = dict(seawater_mgL={k: round(v, 1) for k, v in sw.items()}, wells=out, positions=pos)
    with open(os.path.join(RES, 'hydrochem.json'), 'w') as fh:
        json.dump(res, fh, indent=1)
    for d in out:
        print(f"{d['well']}: f = {100 * d['f']:.2f} %, BEX = {d['BEX']:+.2f} meq/L")


if __name__ == '__main__':
    main()
