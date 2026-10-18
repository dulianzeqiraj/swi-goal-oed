"""Sensitivity of the calibration to the reading of the documented facts: the same 20 000 draws re-weighted
under alternative likelihoods. Writes ../results/calib_sensitivity.json."""
import os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')
SECTOR, APOLY = 221.5625, 349.09
NAMES = ['area250_sh', 'h_lit', 'f_sw', 'f_c', 'cl_ne', 'toe_area_km2', 'area250_dp', 'fdp_sw', 'clmax_sh_transect',
         'clmax_dp_transect', 'fmid_sw', 'clsh_sw', 'clmid_sw', 'area250_mid', 'fmid_c']

def main():
    E = np.load(os.path.join(RES, 'calib_ensemble.npz')); S = E['S']; c = {n: S[:, i] for i, n in enumerate(NAMES)}
    g = lambda x, mu, sd: -0.5 * ((x - mu) / sd) ** 2
    lg = lambda x, mu: -0.5 * ((np.log(np.maximum(x, 1e-6)) - np.log(mu)) / 0.7) ** 2
    T = dict(A=g(c['area250_sh'], 0.15, 0.05), Asec=g(c['area250_sh'] * APOLY / SECTOR, 0.15, 0.05), H=g(c['h_lit'], 3, 1),
             MID=lg(c['fmid_sw'], 0.047), SH=lg(c['f_sw'], 0.047), NE=-np.logaddexp(0, (c['cl_ne'] - 30) / 5),
             C_SH=lg(c['f_c'], 0.0186), C_MID=lg(c['fmid_c'], 0.0186))
    variants = {'primary (T1, T2, T3a second aquifer, T3c)': ['A', 'H', 'MID', 'NE'],
                'wells 341/503 in the first aquifer': ['A', 'H', 'SH', 'NE'],
                'T1 relative to the sector area': ['Asec', 'H', 'MID', 'NE'],
                'central well 340 included (first aquifer)': ['A', 'H', 'MID', 'NE', 'C_SH'],
                'central well 340 included (second aquifer)': ['A', 'H', 'MID', 'NE', 'C_MID'],
                'without the area target T1': ['H', 'MID', 'NE']}
    def wq(x, w):
        o = np.argsort(x); cc = np.cumsum(w[o]); return [float(x[o][np.searchsorted(cc, q)]) for q in (0.05, 0.5, 0.95)]
    out = {}
    for name, keys in variants.items():
        ll = sum(T[k] for k in keys); w = np.exp(ll - ll.max()); w /= w.sum()
        out[name] = dict(ess=float(1 / np.sum(w ** 2)), area_sh_km2=[a * APOLY for a in wq(c['area250_sh'], w)],
                         area_mid_km2=[a * APOLY for a in wq(c['area250_mid'], w)], toe_area_km2=wq(c['toe_area_km2'], w),
                         h_lit=wq(c['h_lit'], w), fmid_sw_pct=[100 * a for a in wq(c['fmid_sw'], w)],
                         f_c_pct=[100 * a for a in wq(c['f_c'], w)], fmid_c_pct=[100 * a for a in wq(c['fmid_c'], w)],
                         R_mm_yr=[a * 365.25e3 for a in wq(E['R'], w)], w_m=wq(E['w'], w))
    json.dump(out, open(os.path.join(RES, 'calib_sensitivity.json'), 'w'), indent=1)
    for k, v in out.items():
        print(f"{k:45s} ESS {v['ess']:7.0f}  area_sh {[round(a,1) for a in v['area_sh_km2']]}  area_mid {[round(a,1) for a in v['area_mid_km2']]}  h {[round(a,2) for a in v['h_lit']]}  f_c {[round(a,3) for a in v['f_c_pct']]}")

if __name__ == '__main__':
    main()
