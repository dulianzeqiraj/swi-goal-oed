"""DARA-GO experiment: certified design bounds from one order-preserving tensor-train transport map.

Steps
 1. Exact reference information curves (quadrature, dara_ref.py) for 24 well positions.
 2. Four maps of the joint law of (design, head, goal, parameters), ordered design -> data -> goal -> parameters:
      A  tensor train in the raw coordinates, rank <= 20 (no preconditioning);
      B  affine (Gaussian Knothe-Rosenblatt) layer + tensor train, rank <= 8;
      C  affine layer + tensor train, rank <= 20;
      D  affine layer + tensor train, rank <= 40.
    Each tensor train is built by two-site cross approximation of the square root of the joint density and
    turned into a density by the squared inverse Rosenblatt transport (dara_tt.py).
 3. For every map and design, with N exact prior-predictive samples (one model run each):
      U   = E[log p(y|z,xi) - log p~(y|xi)]                  >= I(z; y | xi)      (evidence bound)
      L   = E[log p~(q,z|y,xi) - log p(q,z)]                 <= I(z; y | xi)      (posterior bound)
      Lq  = E[log p~(q|y,xi) - log p(q)]                     <= I(q; y | xi)      (goal posterior bound)
      G   = U - L = KL( p(y,q,z|xi) || p~(y,q,z|xi) ),  and  I(q; y | xi) <= Lq + G   (one gap for every goal)
    plus the pure-map (plug-in) estimates computed with samples drawn from the map, and a nested Monte Carlo
    baseline with 2 000 + 2 000 model runs per design.
 4. Certified sets: designs that can still be optimal given the bounds (two standard errors).
Writes dara_results.json and dara_maps.npz (cores of map D, for the figures).
"""
import json, os, time
import numpy as np
import dara_model as M
import dara_setup as S
from dara_tt import tt_cross, SIRT, ProductDensity
from dara_ref import Reference

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
DESIGNS = np.arange(200.0, 4801.0, 100.0)
NB, NMAP, NNMC = 40000, 5000, 2000
TAU_REL = 1e-3


class MapRaw:
    name = 'raw'

    def __init__(self, cores):
        self.sirt = SIRT(cores, S.GRIDS, S.defensive(), TAU_REL)

    def log_lead(self, X):
        return self.sirt.log_marginal(X)

    def sample(self, xi, n, rng):
        return self.sirt.sample_rest(np.full((n, 1), float(xi)), rng, tt_only=True)


class MapAff:
    name = 'affine'

    def __init__(self, cores, aff):
        self.aff = aff
        xa, xb = S.XI[0], S.XI[-1]
        g2 = (lambda x: -0.5 * (x / 2.0) ** 2 - np.log(2.0 * np.sqrt(2 * np.pi)), lambda n, rng: 2.0 * rng.standard_normal(n))
        lam = ProductDensity([(lambda x: np.where((x >= xa) & (x <= xb), -np.log(xb - xa), -np.inf),
                               lambda n, rng: rng.uniform(xa, xb, n))] + [g2] * 5)
        self.sirt = SIRT(cores, aff.grids, lam, TAU_REL)

    def log_lead(self, X):
        W, logjac = self.aff.to_w(X)
        return self.sirt.log_marginal(W) - logjac

    def sample(self, xi, n, rng):
        W = self.sirt.sample_rest(np.full((n, 1), float(xi)), rng, tt_only=True)
        i0 = self.aff.node(W[:, 0])
        v = self.aff.to_x(i0, [W[:, j] for j in range(1, 6)])
        return np.column_stack([W[:, 0]] + v)


def build(level, rng_seed=1):
    rng = np.random.default_rng(rng_seed)
    Xs = S.exact_samples(20000, rng)
    t0 = time.time()
    if level['coords'] == 'raw':
        idx = S.snap(Xs); f = S.f_index; n = S.N; aff = None
    else:
        aff = S.Affine(); idx = aff.snap(Xs); f = aff.f_index; n = aff.n
    vi = idx[:3000]; vv = f([vi[:, j] for j in range(6)])
    cnt = S.EvalCounter()
    cores, hist = tt_cross(f, n, level['rmax'], init=idx[3000:], tol=level['tol'], nswp=level['nswp'],
                           val=(vi, vv), counter=cnt, log=lambda s: print(s, flush=True))
    mp = MapRaw(cores) if aff is None else MapAff(cores, aff)
    return mp, dict(build_s=time.time() - t0, evals=cnt.evals, ranks=hist[-1]['ranks'], val_err=hist[-1]['err'],
                    storage=int(sum(c.size for c in cores)), history=hist), cores


def stats(a):
    return float(np.mean(a)), float(np.std(a) / np.sqrt(len(a)))


def design_bounds(mp, xi, R, rng):
    X = S.exact_samples(NB, rng, xi)
    lp1 = mp.log_lead(X[:, :1]); lp2 = mp.log_lead(X[:, :2]); lp3 = mp.log_lead(X[:, :3]); lp6 = mp.log_lead(X)
    z = X[:, 3:]
    ll = S.log_norm(X[:, 1], M.head(xi, *z.T), M.SIG)
    lqz = S.log_norm(X[:, 2], M.goal(*z.T), M.TAU)
    lpz = S.log_prior_z(z); lpq = R.logpq(X[:, 2])
    u = ll - (lp2 - lp1)
    l = (lp6 - lp2) - lpz - lqz
    lq = (lp3 - lp2) - lpq
    g = (ll + lqz + lpz) - (lp6 - lp1)
    out = {k: stats(v) for k, v in (('U', u), ('L', l), ('Lq', lq), ('G', g))}
    out['Lq_plus_G'] = stats(lq + g)
    # pure-map (plug-in) estimates: the same integrands under samples drawn from the map
    Xm = mp.sample(xi, NMAP, rng)
    zm = Xm[:, 3:]
    m2 = mp.log_lead(Xm[:, :2]); m3 = mp.log_lead(Xm[:, :3]); m6 = mp.log_lead(Xm)
    out['plug'] = stats((m6 - m2) - S.log_prior_z(zm) - S.log_norm(Xm[:, 2], M.goal(*zm.T), M.TAU))
    out['plug_goal'] = stats((m3 - m2) - R.logpq(Xm[:, 2]))
    return out


def nmc(xi, R, rng, n=NNMC, m=NNMC):
    """Nested Monte Carlo with shared inner samples (n + m model runs)."""
    zo = rng.standard_normal((n, 3)); zi = rng.standard_normal((m, 3))
    ho = M.head(xi, *zo.T); hi = M.head(xi, *zi.T); Qo = M.goal(*zo.T); Qi = M.goal(*zi.T)
    y = ho + M.SIG * rng.standard_normal(n); q = Qo + M.TAU * rng.standard_normal(n)
    ky = np.exp(S.log_norm(y[:, None], hi[None, :], M.SIG)); kq = np.exp(S.log_norm(q[:, None], Qi[None, :], M.TAU))
    lpy = np.log(ky.mean(1)); lpqy = np.log((ky * kq).mean(1))
    eig = S.log_norm(y, ho, M.SIG) - lpy
    ig = lpqy - lpy - R.logpq(q)
    return stats(eig), stats(ig)


def certified(lo, slo, hi, shi):
    lstar = np.max(np.asarray(lo) - 2 * np.asarray(slo))
    return [bool(h + 2 * s >= lstar) for h, s in zip(hi, shi)]


def main():
    t0 = time.time()
    R = Reference()
    ref = [R.info(xi) for xi in DESIGNS]
    print(f'reference ready {time.time() - t0:.0f}s', flush=True)
    levels = [dict(key='A', label='raw coordinates, rank 20', coords='raw', rmax=20, tol=1e-6, nswp=5),
              dict(key='B', label='affine layer + rank 8', coords='affine', rmax=8, tol=1e-4, nswp=4),
              dict(key='C', label='affine layer + rank 20', coords='affine', rmax=20, tol=1e-6, nswp=4),
              dict(key='D', label='affine layer + rank 40', coords='affine', rmax=40, tol=1e-7, nswp=4)]
    res = dict(designs=DESIGNS.tolist(), ref_eig=[r['eig'] for r in ref], ref_goal=[r['info_goal'] for r in ref],
               Hq=R.Hq, model=dict(L=M.L, edges=M.EDGES.tolist(), B=M.B, D=M.D, DELTA=M.DELTA, HL=M.HL, K0=M.K0, SK=M.SK,
                                   SIG=M.SIG, TAU=M.TAU), NB=NB, NMAP=NMAP, NNMC=NNMC, tau_rel=TAU_REL, levels={})
    rng = np.random.default_rng(2024)
    for lv in levels:
        print(f"level {lv['key']}: {lv['label']}", flush=True)
        mp, info, cores = build(lv)
        if lv['key'] == 'D':
            np.savez('dara_maps.npz', *cores)
        t1 = time.time()
        per = [design_bounds(mp, xi, R, rng) for xi in DESIGNS]
        info['bounds_s'] = time.time() - t1
        arr = lambda key, j: [p[key][j] for p in per]
        out = dict(label=lv['label'], coords=lv['coords'], rmax=lv['rmax'], **info,
                   **{k: arr(k, 0) for k in ('U', 'L', 'Lq', 'G', 'Lq_plus_G', 'plug', 'plug_goal')},
                   **{'se_' + k: arr(k, 1) for k in ('U', 'L', 'Lq', 'G', 'Lq_plus_G', 'plug', 'plug_goal')})
        out['cert_param'] = certified(out['L'], out['se_L'], out['U'], out['se_U'])
        out['cert_goal'] = certified(out['Lq'], out['se_Lq'], out['Lq_plus_G'], out['se_Lq_plus_G'])
        for c in (2, 3):
            out[f'contains_ref_param_{c}se'] = float(np.mean([(l - c * sl <= r <= u + c * su) for l, sl, u, su, r in
                                                            zip(out['L'], out['se_L'], out['U'], out['se_U'], res['ref_eig'])]))
            out[f'contains_ref_goal_{c}se'] = float(np.mean([(l - c * sl <= r <= u + c * su) for l, sl, u, su, r in
                                                           zip(out['Lq'], out['se_Lq'], out['Lq_plus_G'], out['se_Lq_plus_G'], res['ref_goal'])]))
        out['contains_ref_param'] = out['contains_ref_param_2se']; out['contains_ref_goal'] = out['contains_ref_goal_2se']
        out['argmax'] = {k: float(DESIGNS[int(np.argmax(out[k]))]) for k in ('U', 'L', 'Lq', 'Lq_plus_G', 'plug', 'plug_goal')}
        res['levels'][lv['key']] = out
        best = lambda v: float(DESIGNS[int(np.argmax(v))])
        print(f"  build {info['build_s']:.0f}s, bounds {info['bounds_s']:.0f}s, evals {info['evals']:.2e}, val err {info['val_err']:.3f}")
        print(f"  gap median {np.median(out['G']):.4f} max {np.max(out['G']):.4f}; contains ref: param {out['contains_ref_param']:.2f} goal {out['contains_ref_goal']:.2f}")
        print(f"  optimum: plug-in {best(out['plug'])} / goal {best(out['plug_goal'])}; certified param {DESIGNS[out['cert_param']].tolist()}")
        print(f"  certified goal {DESIGNS[out['cert_goal']].tolist()}", flush=True)
    # nested Monte Carlo baseline
    t1 = time.time()
    nm = [nmc(xi, R, rng) for xi in DESIGNS]
    res['nmc'] = dict(eig=[a[0][0] for a in nm], se_eig=[a[0][1] for a in nm], goal=[a[1][0] for a in nm], se_goal=[a[1][1] for a in nm],
                      runs_per_design=2 * NNMC, seconds=time.time() - t1)
    res['opt_ref_param'] = float(DESIGNS[int(np.argmax(res['ref_eig']))])
    res['opt_ref_goal'] = float(DESIGNS[int(np.argmax(res['ref_goal']))])
    json.dump(res, open('dara_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
