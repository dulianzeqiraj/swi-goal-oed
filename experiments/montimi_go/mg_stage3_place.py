"""MONTIMI-GO stage 3: the critical (largest safe) pumping rate of every layout for every parameter draw, for one
assembly. Usage: python3 mg_stage3_place.py ASSEMBLY SET WORKERS   (ASSEMBLY in F, G, U, S, N; SET in DES, EVA)
Output res/qcrit_<ASSEMBLY>_<SET>.npz: Q (draws x layouts), number of runs, CPU seconds, toe of the present state."""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M
import mg_setup as S

RES = os.path.join(HERE, 'res')


def grid_of(name):
    if name == 'F':
        return S.GF
    if name == 'U':
        return S.GU
    d = json.load(open(os.path.join(RES, 'grid_G.json')))
    return M.Grid(d['xf'], d['zf'])


def q_crit(fJ, thr, guess, tol=0.01, maxev=10):
    """largest Q in [0, Q_MAX] with J(Q) <= thr, J increasing: secant on log J from a guess, bracketed."""
    ev = {}

    def f(q):
        q = float(min(max(q, 0.0), S.Q_MAX))
        if q not in ev:
            ev[q] = fJ(q)
        return q, ev[q]
    lo, hi = 0.0, S.Q_MAX
    lt = np.log(thr)
    pts = []
    q, j = f(guess)
    pts.append((q, j))
    if j <= thr: lo = q
    else: hi = q
    q, j = f(q * 1.15 + 0.1 if j <= thr else q * 0.85 - 0.1)
    pts.append((q, j))
    if j <= thr: lo = max(lo, q)
    else: hi = min(hi, q)
    while len(ev) < maxev:
        if hi - lo < tol:
            break
        if abs(np.log(max(pts[-1][1], 1e-300)) - lt) < 2e-3:
            return pts[-1][0], len(ev)
        (qa, ja), (qb, jb) = pts[-2], pts[-1]
        la, lb = np.log(max(ja, 1e-300)), np.log(max(jb, 1e-300))
        qn = qb + (lt - lb) * (qb - qa) / (lb - la) if abs(lb - la) > 1e-12 else 0.5 * (lo + hi)
        if not np.isfinite(qn) or qn <= lo or qn >= hi:
            qn = 0.5 * (lo + hi)
        q, j = f(qn)
        pts.append((q, j))
        if j <= thr: lo = q
        else: hi = q
        if lo >= S.Q_MAX:
            return S.Q_MAX, len(ev)
    if hi < 0.25 and lo == 0.0:
        q0, j0 = f(0.0)
        if j0 > thr:
            return 0.0, len(ev)
    return lo, len(ev)


def task(args):
    asm, setname, d = args
    P = dict((S.DES if setname == 'DES' else S.EVA)[d])
    cfg = S.ASSEMBLIES[asm]
    g = grid_of(cfg['grid'])
    opts = cfg['opts']
    t = time.time()
    try:
        y0, yp, zp, toe_hist = S.present_state(g, P, opts)
    except Exception as e:
        return d, None, None, None, str(e)
    Qs, nev = [], []
    guess = {}
    for li, L in enumerate(S.LAYOUTS):
        gs = guess.get(L['xs'], 5.0)
        try:
            q, n = q_crit(lambda Q: S.forecast(g, P, opts, yp, zp, L, Q)[0], M.EPS_LIM, gs)
        except Exception as e:
            q, n = np.nan, -1
        Qs.append(q); nev.append(n)
        if np.isfinite(q) and q > 0:
            guess[L['xs']] = q
    return d, Qs, nev, time.time() - t, float(toe_hist[-1])


def main():
    asm, setname, workers = sys.argv[1], sys.argv[2], int(sys.argv[3])
    nd = len(S.DES if setname == 'DES' else S.EVA)
    if asm in ('S', 'N'):                 # the two counter-examples run on the first 10 design draws
        nd, workers = min(nd, 10), max(workers, 2)
    os.makedirs(RES, exist_ok=True)
    Q = np.full((nd, len(S.LAYOUTS)), np.nan); NEV = np.zeros_like(Q); CPU = np.zeros(nd); TOE = np.zeros(nd)
    t0 = time.time()
    with Pool(workers) as pool:
        for d, Qs, nev, cpu, toe in pool.imap_unordered(task, [(asm, setname, d) for d in range(nd)]):
            if Qs is None:
                print('draw', d, 'failed', toe, flush=True)
                continue
            Q[d] = Qs; NEV[d] = nev; CPU[d] = cpu; TOE[d] = toe
            print(f'{asm} {setname} draw {d:2d} done in {cpu:.0f}s, mean runs {np.mean(nev):.1f}, toe {toe:.0f}, Q {np.round(Qs, 2).tolist()}', flush=True)
            np.savez(os.path.join(RES, f'qcrit_{asm}_{setname}.npz'), Q=Q, nev=NEV, cpu=CPU, toe=TOE,
                     layouts=json.dumps([S.lay_name(L) for L in S.LAYOUTS]))
    print('total wall', time.time() - t0)


if __name__ == '__main__':
    main()
