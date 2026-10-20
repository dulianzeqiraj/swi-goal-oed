"""VEGLA-GO: goal-oriented measurement design for certifying an instrument, with optimization-based causal
discovery over graphs with latent confounders and feedback cycles (after Eberhardt, Kaynar & Siddiq, 2025).

The well field is a linear structural model X = B X + e with correlated errors (bidirected edges = latent
confounders) and directed cycles (feedback). Six variables:
    Z  candidate instrument: an exogenous shift of well-field pumping (tariff / rotation schedule)
    Q  pumping of the well field
    C  chloride at the supply well
    H  head at a coastal observation well          (candidate measurement)
    A  agricultural pumping in the plain            (candidate measurement)
    R  recharge (rain gauge / recharge estimate)     (candidate measurement)
Z, Q and C are always observed. The question is whether Z is a valid instrument for the effect of pumping on
chloride: Z must be d-separated from C once the edges out of Q are removed (no side path, no confounding).

Search space: three directed edges are fixed by design or physics (Z->Q, Q->H, H->C); fourteen edges are
optional (9 directed, 5 bidirected), so the space has 2^14 = 16384 graphs. For linear models with cycles and
correlated errors the global Markov property is d-separation (Spirtes 1995; Koster 1996), so each graph has a
signature: the d-separation status of every statement X _||_ Y | S over the six variables (240 statements).
Discovery maximizes the weighted agreement between a graph's signature and conditional-independence tests,
as in the base paper; with 16384 graphs the optimum is found exactly by enumeration.
"""
import itertools
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ['Z', 'Q', 'C', 'H', 'A', 'R']
IDX = {v: i for i, v in enumerate(NAMES)}
NV = len(NAMES)
FIXED = [('Z', 'Q'), ('Q', 'H'), ('H', 'C')]
OPT_DIR = [('Z', 'A'), ('Z', 'H'), ('R', 'H'), ('R', 'Q'), ('R', 'A'), ('A', 'H'), ('Q', 'C'), ('C', 'Q'), ('A', 'C')]
OPT_BI = [('Z', 'R'), ('Z', 'C'), ('Q', 'A'), ('H', 'C'), ('Q', 'C')]
OPT = [('->',) + e for e in OPT_DIR] + [('<->',) + e for e in OPT_BI]
NOPT = len(OPT)
# prior probability of each optional edge ("physical" prior); the flat prior uses 0.3 for every edge
P_PHYS = {('->', 'Z', 'A'): 0.15, ('->', 'Z', 'H'): 0.15, ('->', 'R', 'H'): 0.6, ('->', 'R', 'Q'): 0.35,
          ('->', 'R', 'A'): 0.35, ('->', 'A', 'H'): 0.5, ('->', 'Q', 'C'): 0.35, ('->', 'C', 'Q'): 0.5,
          ('->', 'A', 'C'): 0.15, ('<->', 'Z', 'R'): 0.15, ('<->', 'Z', 'C'): 0.15, ('<->', 'Q', 'A'): 0.35,
          ('<->', 'H', 'C'): 0.35, ('<->', 'Q', 'C'): 0.35}
DESIGNS = {'none': [], 'H': ['H'], 'A': ['A'], 'R': ['R'], 'H+A': ['H', 'A'], 'H+R': ['H', 'R'],
           'A+R': ['A', 'R'], 'H+A+R': ['H', 'A', 'R']}

# statements X _||_ Y | S, X < Y, S subset of the other four variables
STMTS = []
for x, y in itertools.combinations(range(NV), 2):
    rest = [v for v in range(NV) if v not in (x, y)]
    for k in range(len(rest) + 1):
        for S in itertools.combinations(rest, k):
            STMTS.append((x, y, sum(1 << s for s in S)))
NST = len(STMTS)


def graph_edges(code):
    """directed edge list and bidirected edge list of graph number code (bit i = optional edge i)."""
    d = [(IDX[a], IDX[b]) for a, b in FIXED]
    bi = []
    for i, (t, a, b) in enumerate(OPT):
        if code >> i & 1:
            (d if t == '->' else bi).append((IDX[a], IDX[b]))
    return d, bi


def masks(d, bi):
    pa = [0] * NV; ch = [0] * NV; sib = [0] * NV
    for a, b in d:
        pa[b] |= 1 << a; ch[a] |= 1 << b
    for a, b in bi:
        sib[a] |= 1 << b; sib[b] |= 1 << a
    return pa, ch, sib


def ancestors(pa, S):
    A = S
    while True:
        B = A
        for v in range(NV):
            if A >> v & 1:
                B |= pa[v]
        if B == A:
            return A
        A = B


def reach(x, S, anS, pa, ch, sib):
    """bitmask of nodes d-connected to x given S (walk-based reachability for mixed cyclic graphs)."""
    seen = set()
    stack = []
    for w in range(NV):                      # leave x along each edge; flag = arrowhead at the node reached
        if ch[x] >> w & 1: stack.append((w, True))
        if pa[x] >> w & 1: stack.append((w, False))
        if sib[x] >> w & 1: stack.append((w, True))
    out = 0
    while stack:
        v, ah = stack.pop()
        if (v, ah) in seen:
            continue
        seen.add((v, ah))
        out |= 1 << v
        for w in range(NV):
            nxt = []
            if ch[v] >> w & 1: nxt.append((False, True))     # v -> w: tail at v, arrowhead at w
            if pa[v] >> w & 1: nxt.append((True, False))     # v <- w: arrowhead at v, tail at w
            if sib[v] >> w & 1: nxt.append((True, True))     # v <-> w
            for ah_out, ah_w in nxt:
                collider = ah and ah_out
                if collider:
                    if not (anS >> v & 1):
                        continue
                elif S >> v & 1:
                    continue
                if (w, ah_w) not in seen:
                    stack.append((w, ah_w))
    return out


def signature(d, bi):
    """boolean vector over STMTS: True = d-separated."""
    pa, ch, sib = masks(d, bi)
    res = {}
    for S in range(1 << NV):
        anS = ancestors(pa, S)
        for x in range(NV):
            if S >> x & 1:
                continue
            res[(x, S)] = reach(x, S, anS, pa, ch, sib)
    return np.array([not (res[(x, S)] >> y & 1) for x, y, S in STMTS], bool)


def valid_instrument(d, bi):
    """Z valid for the effect of Q on C: Z _||_ C in the graph without the edges out of Q."""
    d2 = [(a, b) for a, b in d if a != IDX['Q']]
    pa, ch, sib = masks(d2, bi)
    return not (reach(IDX['Z'], 0, 0, pa, ch, sib) >> IDX['C'] & 1)


def open_paths(d, bi, src='Z', dst='C', cut='Q'):
    """simple paths from Z to C, unconditioned and open, in the graph without the edges out of Q
    (the pathways that would invalidate the instrument)."""
    q = IDX[cut]
    d2 = [(a, b) for a, b in d if a != q]
    adj = {v: [] for v in range(NV)}
    for a, b in d2:
        adj[a].append((b, '->', True)); adj[b].append((a, '<-', False))
    for a, b in bi:
        adj[a].append((b, '<->', True)); adj[b].append((a, '<->', True))
    out = []

    def walk(v, ah_in, path, used):
        if v == IDX[dst]:
            out.append(path); return
        for w, sym, ah_w in adj[v]:
            if w in used:
                continue
            ah_out = sym in ('<-', '<->')
            if len(path) > 1 and ah_in and ah_out:     # collider, unconditioned: blocked
                continue
            walk(w, ah_w, path + [sym, NAMES[w]], used | {w})
    walk(IDX[src], False, [src], {IDX[src]})
    return [' '.join(p) for p in out]


def enumerate_space(cache=os.path.join(HERE, 'vegla_space.npz')):
    if os.path.exists(cache):
        z = np.load(cache)
        return z['sig'], z['valid']
    G = 1 << NOPT
    sig = np.zeros((G, NST), bool)
    valid = np.zeros(G, bool)
    for code in range(G):
        d, bi = graph_edges(code)
        sig[code] = signature(d, bi)
        valid[code] = valid_instrument(d, bi)
    np.savez_compressed(cache, sig=sig, valid=valid)
    return sig, valid


def prior_weights(kind='phys'):
    G = 1 << NOPT
    w = np.ones(G)
    bits = (np.arange(G)[:, None] >> np.arange(NOPT)[None, :]) & 1
    for i, e in enumerate(OPT):
        p = P_PHYS[e] if kind == 'phys' else 0.3
        w *= np.where(bits[:, i] == 1, p, 1 - p)
    return w / w.sum()


def design_columns(obs):
    o = {IDX[v] for v in ['Z', 'Q', 'C'] + list(obs)}
    return np.array([x in o and y in o and all((S >> s & 1) == 0 or s in o for s in range(NV))
                     for x, y, S in STMTS])


def exact_design_value(sig, valid, w, obs):
    """population (large-sample) value of observing obs: partition of the space by observable signature."""
    cols = design_columns(obs)
    sub = np.packbits(sig[:, cols], axis=1)
    keys = np.unique(sub, axis=0, return_inverse=True)[1].ravel()
    ng = keys.max() + 1
    pg = np.bincount(keys, weights=w, minlength=ng)
    pv = np.bincount(keys, weights=w * valid, minlength=ng)
    h = lambda p: np.where((p > 0) & (p < 1), -p * np.log2(np.clip(p, 1e-300, 1)) - (1 - p) * np.log2(np.clip(1 - p, 1e-300, 1)), 0.0)
    pV = (w * valid).sum()
    cond = np.where(pg > 0, pv / np.maximum(pg, 1e-300), 0)
    I_valid = float(h(np.array(pV)) - (pg * h(cond)).sum())
    H_sig = float(-(pg[pg > 0] * np.log2(pg[pg > 0])).sum())
    risk = float(np.minimum(pv, pg - pv).sum())                      # Bayes risk of the validity decision
    resolved = float(pg[(pv < 1e-15) | (pg - pv < 1e-15)].sum())      # prior mass whose validity is determined
    exp_class = float((pg * np.bincount(keys, minlength=ng)).sum())   # expected size of the equivalence class
    return dict(I_valid=I_valid, H_sig=H_sig, bayes_risk=risk, resolved=resolved, exp_class=exp_class,
                n_classes=int(ng), n_statements=int(cols.sum()))
