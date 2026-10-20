"""HARTA-GO, stage 2: reference (exact) expected information gain of every 3- and 5-well design for
the three goals, by likelihood re-weighting over the 48 000-member reference ensemble.
Outer samples: the first 4 000 (3-well) or 1 000 (5-well) members of the 'outer' ensemble, each with
one noisy reading per well (noise sd 0.2 m, seed 11). The same outer samples and noise serve every
design (common random numbers), so differences between designs are estimated more precisely than
the values themselves. Run: python3 harta_ref.py   (about 1 hour on 4 cores). Output: harta_ref.npz
"""
import itertools, time
import numpy as np
from multiprocessing import Pool
import harta as H

Z = np.load('harta_ens.npz')
REF = Z['ref'].astype(np.float32)
GREF = H.goal_of(Z['ref']).astype(np.float32)
P0 = GREF.mean(0).astype(np.float64)
rng = np.random.default_rng(11)
OUT = Z['outer'][:, :H.NC] + H.SN * rng.standard_normal((len(Z['outer']), H.NC))
OUT = OUT.astype(np.float32)
NOUT = {3: 4000, 5: 1000}
INV2S2 = np.float32(1.0 / (2 * H.SN * H.SN))


def one(args):
    d, nout = args
    d = list(d); acc = np.zeros(3); ess = 0.0
    G = REF[:, d]
    for s in range(0, nout, 250):
        yo = OUT[s:min(s + 250, nout), d]
        S = np.zeros((len(yo), len(G)), np.float32)
        for j in range(len(d)):
            S += (yo[:, j, None] - G[None, :, j]) ** 2
        S -= S.min(1, keepdims=True)
        S *= -INV2S2
        np.exp(S, out=S)
        sw = S.sum(1, dtype=np.float64)
        p = (S @ GREF).astype(np.float64) / sw[:, None]
        acc += H.hb(p).sum(0)
        ess += (sw ** 2 / np.einsum('ij,ij->i', S, S).astype(np.float64)).sum()
    return np.r_[H.hb(P0) - acc / nout, ess / nout]


if __name__ == '__main__':
    t0 = time.time(); res = {'P0': P0}
    for k in (3, 5):
        D = list(itertools.combinations(range(H.NC), k))
        with Pool(4) as p:
            R = np.array(p.map(one, [(d, NOUT[k]) for d in D], chunksize=4))
        res[f'D{k}'] = np.array(D); res[f'EX{k}'] = R[:, :3]; res[f'ESS{k}'] = R[:, 3]
        b = R[:, :3].argmax(0)
        print(f'{k}-well: {len(D)} designs, {time.time() - t0:.0f}s; optimum per goal',
              [(Z["ids"][list(D[i])].tolist(), round(float(R[i, g]), 3)) for g, i in enumerate(b)],
              f'mean ESS {R[:, 3].mean():.0f}', flush=True)
    np.savez('harta_ref.npz', **res)
