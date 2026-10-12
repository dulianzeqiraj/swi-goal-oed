"""PRAG-GO on the Henry problem.

Stage 1 (ensemble): solve the Henry problem for prior log-K realisations and store the
  concentrations at 32 monitoring candidates, at two supply wells, the salt-mass goal and
  the toe.
Stage 2 (adjoint): linearise at the prior mean with the discrete adjoint (the project's
  pipeline: Lemma 1) and store the sensitivities.
Stage 3 (designs): exhaustive search over all 3-well designs for every criterion, with the
  exact nonlinear EIG of the threshold goals estimated by likelihood re-weighting.
"""
import sys, time, os
import numpy as np
import scipy.sparse.linalg as spla
from multiprocessing import Pool
from henry import Henry

OUT = sys.argv[1] if len(sys.argv) > 1 else 'res_gauss'
PRIOR = sys.argv[2] if len(sys.argv) > 2 else 'gauss'       # 'gauss', 'local' or 'facies'
os.makedirs(OUT, exist_ok=True)

m = Henry(41, 21)
N = m.N
X, Z = np.meshgrid(m.xc, m.yc); X = X.ravel(); Z = Z.ravel()
SIG, LX, LZ = (0.7, 0.2, 0.1) if PRIOR == 'local' else (0.5, 0.5, 0.2)
d2 = ((X[:, None] - X[None]) / LX) ** 2 + ((Z[:, None] - Z[None]) / LZ) ** 2
GAM = SIG ** 2 * np.exp(-np.sqrt(d2))
w, V = np.linalg.eigh(GAM); LCH = V * np.sqrt(np.clip(w, 0, None))
FACIES_SHIFT = 0.5        # facies prior: mean log-K of -0.5 or +0.5 with probability 1/2

TAU = 0.01                                     # 1% of seawater
cell = lambda x, z: int(round(z / m.dy - 0.5)) * m.Nx + int(round(x / m.dx - 0.5))
CAND_X = [0.32, 0.51, 0.71, 0.90, 1.10, 1.29, 1.49, 1.68]
CAND_Z = [0.12, 0.31, 0.50, 0.69]
CAND = np.array([cell(x, z) for x in CAND_X for z in CAND_Z])
WELL_A, WELL_B = cell(0.61, 0.12), cell(0.80, 0.60)
MASS = np.where((X > 1.0) & (X < 1.6))[0]
U0, _, _ = m.solve(np.zeros(N))


def sample_theta(rng):
    th = LCH @ rng.standard_normal(N)
    if PRIOR == 'facies':
        th = th + (FACIES_SHIFT if rng.random() < 0.5 else -FACIES_SHIFT)
    return th


def run_chunk(args):
    seed, n = args
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        th = sample_theta(rng)
        U, nF, _ = m.solve(th, U0=U0)
        c = U[N:]
        rows.append(np.concatenate([c[CAND], [c[WELL_A], c[WELL_B],
                                    m.phi * m.dx * m.dy * c[MASS].sum(), m.toe(U), nF]]))
    return np.array(rows)


def ensemble(n_total, seed0):
    chunks = [(seed0 + k, n_total // 40) for k in range(40)]
    with Pool(4) as p:
        return np.vstack(p.map(run_chunk, chunks))


if __name__ == '__main__':
    t0 = time.time()
    f = f'{OUT}/ens.npz'
    if not os.path.exists(f):
        inner = ensemble(12000, 1000)
        outer = ensemble(2000, 5000)
        np.savez(f, inner=inner, outer=outer)
        print(f'ensemble done {time.time() - t0:.0f}s; max |F| = {max(inner[:, -1].max(), outer[:, -1].max()):.1e}')
    # ---------------- adjoint linearisation at the prior mean (Lemma 1 pipeline)
    th0 = np.zeros(N) + 0.0
    J = m.jacobian(U0, th0)
    dRdth = m.dR_dtheta(U0, th0)
    rhs = np.zeros((2 * N, 32 + 3))
    for k, cidx in enumerate(CAND):
        rhs[N + cidx, k] = 1.0
    rhs[N + WELL_A, 32] = 1.0
    rhs[N + WELL_B, 33] = 1.0
    rhs[N + MASS, 34] = m.phi * m.dx * m.dy
    lu = spla.splu(J.T.tocsc())
    lam = lu.solve(rhs)
    S = -(dRdth.T @ lam).T                          # rows: 32 candidates, A, B, mass
    # finite-difference check of the adjoint sensitivity of the mass goal
    rng = np.random.default_rng(7); eta = rng.standard_normal(N); eta /= np.linalg.norm(eta)
    hs = 1e-4
    Up, _, _ = m.solve(th0 + hs * eta, U0=U0); Um, _, _ = m.solve(th0 - hs * eta, U0=U0)
    qf = lambda U: m.phi * m.dx * m.dy * U[N:][MASS].sum()
    fd = (qf(Up) - qf(Um)) / (2 * hs)
    print(f'adjoint check: adjoint {S[34] @ eta:.6e}  FD {fd:.6e}  rel err {abs(S[34] @ eta - fd) / abs(fd):.2e}')
    mean_shift = np.zeros(N)
    np.savez(f'{OUT}/lin.npz', S=S, GAM=GAM, c0=U0[N:][np.r_[CAND, WELL_A, WELL_B]],
             mass0=qf(U0), CAND=CAND, WELL_A=WELL_A, WELL_B=WELL_B, X=X, Z=Z)
    print(f'saved; {time.time() - t0:.0f}s')
