"""Monitoring designs for MJEGULLA-GO. A baseline survey measures every well in season 0; in each later season B
wells are measured, chosen by one of seven rules:
  round_robin   all wells in turn
  random        B wells at random
  targets       the target (municipal) wells in turn
  entropy       the wells whose predicted state is most uncertain (largest entropy)
  D_opt         greedy D-optimal design for theta (log det of the information)
  c_opt         greedy goal-oriented design for the parameter part only: minimize a'(J + sum I_j)^-1 a
  goal          greedy minimization of the expected squared error of the goal, state part (preposterior variance
                of the target wells) plus parameter part (a'(J + sum I_j)^-1 a), for all B wells
  mjegulla      MJEGULLA: B - 1 wells by the goal criterion and one defensive well by the D criterion, which keeps
                the information matrix nonsingular (a c-optimal design alone is often singular: Elfving)
For the planned-sites goal (kind 'plan') the state part is zero, 'goal' coincides with 'c_opt', and 'targets' is
replaced by 'similar' (hard-pumping wells at the distances of the planned sites).
a is the gradient of the goal in theta and I_j the Fisher information of one measurement of well j next season
(the information of the predictive density of Y_j); by Theorem Q the robust interval's width is an increasing function
of a'J^-1 a for every penalty."""
import numpy as np
import mjegulla_model as Mo

YQ = np.linspace(-2.4, 4.4, 137)
DY = YQ[1] - YQ[0]
PHI = Mo.lik_obs(YQ)                                   # (Q, 3)
RIDGE = 0.05
DESIGNS = ['round_robin', 'random', 'targets', 'entropy', 'D_opt', 'c_opt', 'goal', 'mjegulla']
DESIGNS_PLAN = ['round_robin', 'random', 'similar', 'entropy', 'D_opt', 'goal', 'mjegulla']


def season_quantities(F, Mask, Y, t_now, th, T_end, H, h=1e-3, kind='mon'):
    """Predictive state probabilities for season t_now, Fisher information of one measurement per well, the
    preposterior variance reduction of each target's goal indicator, and the goal gradient."""
    pts = np.vstack([th] + [th + s * h * np.eye(3)[j] for j in range(3) for s in (1, -1)])
    ll, f, P = Mo.filt(pts, F, Mask, Y, t_now)
    pred = np.einsum('kns,knsr->knr', f, P)              # (7, n, 3)
    dpred = np.stack([(pred[1 + 2 * j] - pred[2 + 2 * j]) / (2 * h) for j in range(3)])   # (3, n, 3)
    p = pred[0] @ PHI.T                                   # (n, Q)
    dp = np.einsum('jns,qs->jnq', dpred, PHI)             # (3, n, Q)
    sc = dp / np.maximum(p, 1e-300)[None]
    I = np.einsum('jnq,knq,nq->njk', sc, sc, p) * DY      # (n, 3, 3)
    # state part: v = P^m [:, 2] for the remaining m seasons to the goal season
    m = (T_end - 1 + H) - t_now
    v = np.eye(3)[None].repeat(F['n'], 0)
    for _ in range(m):
        v = np.einsum('nrs,nst->nrt', v, P[0])
    v2 = v[:, :, 2]                                       # (n, 3)
    pc = (pred[0] * v2).sum(1)                            # current P(X_goal = 2)
    num = np.einsum('ns,qs,ns->nq', pred[0], PHI, v2)     # sum_s pred_s phi_s(y) v_s
    py = num / np.maximum(p, 1e-300)
    epv = (p * py * (1 - py)).sum(1) * DY
    dstate = np.zeros(F['n'])
    if kind == 'mon':
        dstate[F['tgt']] = (pc * (1 - pc) - epv)[F['tgt']]
    # goal gradient
    sp = Mo.stencil(th, h)
    gv, _ = Mo.goal(sp, F, Mask, Y, t_now, T_end, H, kind)
    a, _ = Mo.grad_hess(gv, h)
    ent = -(pred[0] * np.log(np.maximum(pred[0], 1e-300))).sum(1)
    return dict(I=I, dstate=dstate, a=a, ent=ent)


def choose(rule, B, F, Q, J, t, rng):
    n = F['n']
    if rule == 'round_robin':
        return [(t * B + b) % n for b in range(B)]
    if rule == 'random':
        return list(rng.choice(n, B, replace=False))
    if rule == 'targets':
        tg = F['tgt']
        return [int(tg[(t * B + b) % len(tg)]) for b in range(B)] if B <= len(tg) else list(tg) + list(rng.choice(np.setdiff1d(np.arange(n), tg), B - len(tg), replace=False))
    if rule == 'similar':
        # wells that pump hard and lie closest (in distance to the coast) to the planned sites, in turn
        cand = np.where(F['u'] == 1)[0]
        dist = np.min(np.abs(F['d'][cand][:, None] - Mo.SITES_D[None]), 1)
        order = cand[np.argsort(dist)][:max(B, 8)]
        return [int(order[(t * B + b) % len(order)]) for b in range(B)]
    if rule == 'entropy':
        return list(np.argsort(-Q['ent'])[:B])
    Jc = J + RIDGE * np.eye(3)
    if rule == 'mjegulla':
        sel, Jc = greedy('goal', B - 1, Q, Jc, [])
        sel, Jc = greedy('D_opt', 1, Q, Jc, sel)      # the defensive measurement keeps every direction identified
        return sel
    return greedy(rule, B, Q, Jc, [])[0]


def greedy(rule, m, Q, Jc, sel):
    """Add m wells one at a time: D_opt maximizes the gain in log det of the information; c_opt the fall of
    a'J^-1 a; goal the fall of a'J^-1 a plus the preposterior fall of the state variance of the targets."""
    sel = list(sel)
    a = Q['a']
    n = Q['I'].shape[0]
    for _ in range(m):
        best, bj = -np.inf, None
        base = a @ np.linalg.solve(Jc, a)
        _, ld0 = np.linalg.slogdet(Jc)
        for j in range(n):
            if j in sel:
                continue
            Jn = Jc + Q['I'][j]
            if rule == 'D_opt':
                val = np.linalg.slogdet(Jn)[1] - ld0
            else:
                val = base - a @ np.linalg.solve(Jn, a)
                if rule == 'goal':
                    val += Q['dstate'][j]
            if val > best:
                best, bj = val, j
        sel.append(bj)
        Jc = Jc + Q['I'][bj]
    return sel, Jc


def run_design(rule, F, Yall, T, H, B, rng, kind='mon'):
    n = F['n']
    Mask = np.zeros((T, n), bool); Mask[0] = True
    Y = np.where(Mask, Yall, np.nan)
    th = None
    for t in range(1, T):
        th, ll, J = Mo.mle(F, Mask, Y, t, th0=th)
        if rule in ('round_robin', 'random', 'targets', 'similar'):
            S = choose(rule, B, F, None, J, t, rng)
        else:
            Q = season_quantities(F, Mask, Y, t, th, T, H, kind=kind)
            S = choose(rule, B, F, Q, J, t, rng)
        Mask[t, S] = True
        Y = np.where(Mask, Yall, np.nan)
    return Mask, Y
