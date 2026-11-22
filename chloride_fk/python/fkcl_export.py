"""Export the shared random inputs so the MATLAB code can reproduce the Python numbers exactly:
   ../results/calib_prior_draws.csv  (the N prior draws of fkcl_calib.py, one row per draw)
   ../results/post_idx.csv           (1-based indices of the posterior resample of fkcl_post.py)
and, with --tsv DIR, tab-separated copies of the workbook sheets for GNU Octave (which has no readcell)."""
import os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, '..', 'results')
sys.path.insert(0, HERE)
import fkcl_model as M  # noqa: E402

def main():
    # the shared draws are rewritten only when the ensembles exist (post_ensemble.npz is not in git:
    # run fkcl_calib.py and fkcl_post.py first); the TSV export needs only the workbook
    fc, fp = os.path.join(RES, 'calib_ensemble.npz'), os.path.join(RES, 'post_ensemble.npz')
    if os.path.exists(fc):
        E = np.load(fc)
        th = E['theta']
        cols = {f'theta{k + 1}': th[:, k] for k in range(th.shape[1])}
        for k in ['R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s']:
            cols[k] = E[k]
        pd.DataFrame(cols).to_csv(os.path.join(RES, 'calib_prior_draws.csv'), index=False, float_format='%.9g')
    if os.path.exists(fp):
        P = np.load(fp)
        pd.DataFrame({'idx1': P['idx'] + 1}).to_csv(os.path.join(RES, 'post_idx.csv'), index=False)
    if '--tsv' in sys.argv:
        out = sys.argv[sys.argv.index('--tsv') + 1]; os.makedirs(out, exist_ok=True)
        x = pd.ExcelFile(M.fk.default_xlsx())
        for sh in x.sheet_names:
            d = pd.read_excel(x, sheet_name=sh, header=None)
            d.to_csv(os.path.join(out, sh + '.tsv'), sep='\t', header=False, index=False)
    print('exported')

if __name__ == '__main__':
    main()
