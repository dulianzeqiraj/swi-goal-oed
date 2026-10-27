"""Stability of the update for a karst network (the claim in the innovation band of the diagram).

Matrix-conduit dual continuum on a random conduit graph: laminar-turbulent pipe law f(d) = C d / sqrt(|d| + eps)
(monotone in the head difference d), linear matrix-conduit exchange, a switching spring Q_s = Cs (h - zs)_+ and Darcy flow
in the matrix. Two runs with different initial heads and forcings, implicit Euler. Because every law is monotone, the head
difference obeys ||dh_n|| <= ||dh_0|| + sum_k dt ||S^-1 db_k|| in the storage norm ||v||^2 = sum S v^2.
Prints the largest ratio ||dh_n|| / bound over 30 random networks; it must stay at or below 1."""
import numpy as np


def run_pair(seed):
    r = np.random.default_rng(seed)
    nc, nm = 25, 25                                   # conduit nodes, matrix cells (one per node)
    E = [(i, i + 1) for i in range(nc - 1)] + [tuple(sorted(r.choice(nc, 2, replace=False))) for _ in range(10)]
    E = list({e for e in E if e[0] != e[1]})
    Ce = r.uniform(0.5, 5.0, len(E)); eps = 1e-3
    Sm, Sc = r.uniform(0.05, 0.2, nm), r.uniform(1e-3, 1e-2, nc)
    Km = 0.05; aex = r.uniform(0.01, 0.5, nc); Cs, zs = 3.0, 0.0
    S = np.concatenate([Sm, Sc]); n = nm + nc; dt = 0.1

    def F(h, b):                                      # residual of the implicit step without the storage term
        hm, hc = h[:nm], h[nm:]
        out = np.zeros(n)
        for k in range(nm - 1):                       # matrix Darcy between neighbouring cells
            q = Km * (hm[k] - hm[k + 1]); out[k] += q; out[k + 1] -= q
        ex = aex * (hm - hc); out[:nm] += ex; out[nm:] -= ex
        for (i, j), c in zip(E, Ce):
            d = hc[i] - hc[j]; q = c * d / np.sqrt(abs(d) + eps); out[nm + i] += q; out[nm + j] -= q
        out[nm] += Cs * max(hc[0] - zs, 0.0)          # spring at node 0
        return out - b

    def step(h0, b):
        h = h0.copy()
        for it in range(80):                          # Newton with a numerical Jacobian
            G = S * (h - h0) / dt + F(h, b)
            if np.max(np.abs(G)) < 1e-10:
                break
            J = np.diag(S / dt); e = 1e-7
            for k in range(n):
                hp = h.copy(); hp[k] += e
                J[:, k] += (F(hp, b) - F(h, b)) / e
            h = h - np.linalg.solve(J, G)
        return h

    nst = 40
    b1 = r.normal(0, 0.3, (nst, n)); b1[:, :nm] += 0.2         # diffuse recharge on the matrix
    b1[:, nm + r.integers(1, nc)] += r.uniform(0, 3, nst)       # a sinking stream into one conduit node
    b2 = b1 + r.normal(0, 0.2, b1.shape)
    h1 = r.normal(0.5, 0.3, n); h2 = h1 + r.normal(0, 0.3, n)
    nrm = lambda v: np.sqrt(np.sum(S * v ** 2))
    bound = nrm(h1 - h2); worst = 0.0
    for k in range(nst):
        h1, h2 = step(h1, b1[k]), step(h2, b2[k])
        bound += dt * nrm((b1[k] - b2[k]) / S)
        worst = max(worst, nrm(h1 - h2) / bound)
    return worst


if __name__ == '__main__':
    w = [run_pair(s) for s in range(30)]
    print('largest ratio ||dh_n|| / bound over 30 random networks:', round(max(w), 4), '(must stay <= 1)')
