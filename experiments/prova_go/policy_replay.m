function P = policy_replay(policy, Tab, A, tr, S)
%POLICY_REPLAY  One bandit policy over the five arms (TRIAL-GO or a comparator).
%   P = POLICY_REPLAY(policy, Tab, A, tr, S) with policy 'trial' (robust Gittins
%   index of table Tab), 'ucb' (lower confidence bound p - sqrt(2 log N / n)),
%   'ts' (Thompson sampling from Beta(s+0.5, n-s+0.5)) or 'greedy' (lowest p).
%   A play of arm m = one LM iteration on the heads (cost A.cost{m}(i) runs; 0
%   once the arm has converged) + one new validation item, the next one of the
%   arm's own permutation tr.perm(m,:); cost h = 1 if the item lies outside the
%   arm's current 90 % predictive interval (A.miss{m}(i,item)). State: misses
%   s, items n, p = (s+0.5)/(n+1); TRIAL-GO plays the smallest index
%   gamma(p, n+1). Start: one play of each arm. An arm is playable while it has
%   items left and its next iteration fits in the remaining budget S.budget.
%   The LM path of an arm on the heads does not depend on the policy, so it is
%   computed once (A, by PROVA_TRUTH) and replayed here: identical to running it.
%   Final choice: smallest posterior-mean miss rate among arms with at least
%   S.minItems items (ties: smaller index, then smaller arm number).
    nA = numel(A.cost); J2 = size(tr.perm, 2);
    n = zeros(1, nA); s = zeros(1, nA); used = 0;
    if strcmp(policy, 'ts'), rng(tr.tsSeed, 'twister'); end
    Larm = []; Lruns = []; Lmiss = []; Lidx = zeros(0, nA); Lp = zeros(0, nA);
    first = true;
    while true
        c = zeros(1, nA); ok = false(1, nA);
        for m = 1:nA
            if n(m) + 1 <= A.nIter(m), c(m) = A.cost{m}(n(m) + 1); end
            ok(m) = n(m) < J2 && c(m) <= S.budget - used;
        end
        if first                                   % one play of every arm, in order
            first = false; order = find(ok); g = nan(1, nA);
            for m = order
                [n, s, used, Larm, Lruns, Lmiss, Lidx, Lp] = do_play(m, c(m), n, s, used, A, tr, g, Larm, Lruns, Lmiss, Lidx, Lp);
            end
            continue
        end
        if ~any(ok), break; end
        g = inf(1, nA);
        for m = find(ok), g(m) = arm_index(policy, Tab, s(m), n(m), sum(n)); end
        [~, m] = min(g);
        [n, s, used, Larm, Lruns, Lmiss, Lidx, Lp] = do_play(m, c(m), n, s, used, A, tr, g, Larm, Lruns, Lmiss, Lidx, Lp);
    end
    pm = (s + 0.5) ./ (n + 1); gf = inf(1, nA);
    if ~strcmp(policy, 'ts')
        for m = 1:nA, if n(m) > 0, gf(m) = arm_index(policy, Tab, s(m), n(m), sum(n)); end, end
    end
    elig = find(n >= S.minItems);
    if isempty(elig), [~, sel] = max(n);
    else
        key = [pm(elig)' gf(elig)' elig(:)]; [~, o] = sortrows(key); sel = elig(o(1));
    end
    P = struct('policy', policy, 'sel', sel, 'n', n, 's', s, 'pm', pm, 'runs', used, ...
               'logArm', Larm, 'logRuns', Lruns, 'logMiss', Lmiss, 'logIdx', Lidx, 'logP', Lp);
end
function [n, s, used, Larm, Lruns, Lmiss, Lidx, Lp] = do_play(m, c, n, s, used, A, tr, g, Larm, Lruns, Lmiss, Lidx, Lp)
    used = used + c; n(m) = n(m) + 1; it = min(n(m), A.nIter(m));
    h = A.miss{m}(it, tr.perm(m, n(m))); s(m) = s(m) + h;
    Larm(end + 1, 1) = m; Lruns(end + 1, 1) = used; Lmiss(end + 1, 1) = h;
    Lidx(end + 1, :) = g; Lp(end + 1, :) = (s + 0.5) ./ (n + 1);
end
function g = arm_index(policy, Tab, s, n, ntot)
    p = (s + 0.5) / (n + 1);
    switch policy
        case 'trial',  g = gittins_lookup(Tab, p, n + 1);
        case 'ucb',    g = p - sqrt(2 * log(max(ntot, 1)) / max(n, 1));
        case 'ts',     g = beta_rand(s + 0.5, n - s + 0.5, rand);
        case 'greedy', g = p;
        otherwise, error('policy_replay:policy', 'Unknown policy %s.', policy);
    end
end
