"""Prior draws and noise of fk_prag_geo.py, for the MATLAB port (chloride_fk/matlab/fkcl_prag_go.m).

Regenerates, with the same generators and seeds as fk_prag_geo.py (no model solves needed):
  theta_inner  12 000 x Nz   zone log-K multipliers of the inner ensemble (seeds 1000..1039)
  theta_outer   2 000 x Nz   outer ensemble (seeds 5000..5039)
  noise_ns     12 000 x NC   standard normal noise of the normal-score moments (seed 3)
  noise_ex      2 000 x NC   standard normal noise of the outer readings (seed 11)
and writes them, in this order and each row by row, as little-endian float64 to
res_geo/prag_draws_<prior>.bin, with the shapes in res_geo/prag_draws_<prior>.json.
Run: python3 fk_prag_geo_export.py [base|rho805]
"""
import sys, json
import numpy as np
from fk_geo import FKGeo

PRIOR = sys.argv[1] if len(sys.argv) > 1 else 'base'
CFG = {'base': dict(), 'rho805': dict(rhoF=0.805)}[PRIOR]
NC = 16                                         # candidate wells of fk_prag_geo.py

m = FKGeo(**CFG)
LG = np.linalg.cholesky(m.Gam)


def thetas(n, seed0):
    out = []
    for k in range(40):
        rng = np.random.default_rng(seed0 + k)
        out += [LG @ rng.standard_normal(m.Nz) for _ in range(n // 40)]
    return np.array(out)


blocks = {'theta_inner': thetas(12000, 1000), 'theta_outer': thetas(2000, 5000),
          'noise_ns': np.random.default_rng(3).standard_normal((12000, NC)),
          'noise_ex': np.random.default_rng(11).standard_normal((2000, NC))}
with open(f'res_geo/prag_draws_{PRIOR}.bin', 'wb') as f:
    for k, v in blocks.items():
        f.write(np.ascontiguousarray(v, dtype='<f8').tobytes())
json.dump({'order': list(blocks), 'shapes': {k: list(v.shape) for k, v in blocks.items()}, 'dtype': 'float64 little-endian, row by row'},
          open(f'res_geo/prag_draws_{PRIOR}.json', 'w'), indent=1)
print({k: v.shape for k, v in blocks.items()})
