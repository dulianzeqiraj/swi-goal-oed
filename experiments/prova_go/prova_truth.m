function out = prova_truth(M, S, arms, tabs, tr, keepAll)
%PROVA_TRUTH  Everything for one truth: arm calibrations, comparators, bandits, scores.
%   out = PROVA_TRUTH(M, S, arms, tabs, tr) for the truth tr (MAKE_TRUTH):
%   1. each arm calibrated on the heads by LM to convergence (its path is stored:
%      cost, iterate and validation misses after every iteration);
%   2. comparators: PEST standard (A1, heads), PEST with recharge (A4, heads),
%      PEST on all data (A4 from the prior mean on heads + 2J items), all arms on
%      heads + BIC selection then conditioned on all data, oracle (best joint log
%      score among the five arms conditioned on all data);
%   3. bandits (POLICY_REPLAY): TRIAL-GO (tabs.main: k = 0.5, beta = 0.95, H = 60),
%      TRIAL-GO with k = 0.2 and 0.8, UCB, Thompson, greedy; the selected arm is
%      conditioned on all data from its last iterate (runs counted);
%   4. goal scores (GOAL_SCORE) of every method. keepAll = true keeps the logs.
    if nargin < 6, keepAll = false; end
    J = M.J; rH = (1:J)'; rV = (J+1:3*J)'; rAll = (1:3*J)';
    sigH = S.sigH * ones(J, 1); sigAll = [sigH; S.sigV * ones(2*J, 1)]; dAll = [tr.dH; tr.dV];
    nA = numel(arms);
    % ---- 1. heads-only LM path of every arm ---------------------------------
    A.cost = cell(1, nA); A.miss = cell(1, nA); A.snap = cell(1, nA); A.nIter = zeros(1, nA);
    for m = 1:nA
        st = lm_init(M, S, arms(m), arms(m).th0, rH, tr.dH, sigH); c0 = st.runs;
        cost = []; miss = false(0, 2*J); snap = {};
        while ~st.conv
            st = lm_iter(M, S, st);
            cost(end + 1) = st.costLast + c0; c0 = 0; %#ok<AGROW>
            [mu, C] = lm_predict(st, rV); sd = sqrt(max(diag(C), 0) + S.sigV^2);
            miss(end + 1, :) = (abs(tr.dV - mu) > S.z90 * sd)'; %#ok<AGROW>
            snap{end + 1} = st; %#ok<AGROW>
        end
        A.cost{m} = cost; A.miss{m} = miss; A.snap{m} = snap; A.nIter(m) = numel(cost);
    end
    out.seed = tr.seed; out.hasStrip = tr.hasStrip; out.xiR = tr.xiR; out.xif = tr.xif;
    out.riskTrue = tr.riskTrue; out.Hfut = tr.Hfut'; out.Hfut0 = tr.Hfut0'; out.hnat = tr.hnat';
    out.nIter = A.nIter; out.costConv = cellfun(@sum, A.cost);
    out.missConv = cellfun(@(x) mean(x(end, :)), A.miss);       % validation miss rate at convergence (heads only)
    % ---- all-data continuation from the heads-converged iterate (cached) ----
    cache = struct('key', {}, 'st', {});
    function_dummy = []; %#ok<NASGU>
    allc = cell(1, nA);
    for m = 1:nA
        [allc{m}, cache] = cond_all(M, S, A, m, A.nIter(m), rAll, dAll, sigAll, cache);
    end
    meth = struct('name', {}, 'g', {}, 'runs', {}, 'arm', {});
    % (i) PEST standard, (ii) PEST with recharge
    meth(end + 1) = struct('name', 'pest_std', 'g', goal_predict(A.snap{1}{end}, S, M), 'runs', out.costConv(1), 'arm', 1);
    meth(end + 1) = struct('name', 'pest_rch', 'g', goal_predict(A.snap{4}{end}, S, M), 'runs', out.costConv(4), 'arm', 4);
    % (iii) PEST on all data: A4 from the prior mean on heads + items
    st = lm_init(M, S, arms(4), arms(4).th0, rAll, dAll, sigAll);
    while ~st.conv, st = lm_iter(M, S, st); end
    meth(end + 1) = struct('name', 'pest_all', 'g', goal_predict(st, S, M), 'runs', st.runs, 'arm', 4);
    % (iv) BIC over the heads-converged arms, then all data
    bic = zeros(1, nA);
    for m = 1:nA
        sm = A.snap{m}{end}; r = (tr.dH - sm.f(rH)) ./ sigH; bic(m) = sum(r.^2) + arms(m).n * log(J);
    end
    [~, mb] = min(bic);
    meth(end + 1) = struct('name', 'bic', 'g', goal_predict(allc{mb}, S, M), 'runs', sum(out.costConv) + allc{mb}.runs, 'arm', mb);
    out.bic = bic;
    % (viii) oracle: best joint log score among the arms conditioned on all data
    ls = zeros(1, nA); gall = cell(1, nA);
    for m = 1:nA, gall{m} = goal_predict(allc{m}, S, M); sc = goal_score(gall{m}, tr, S); ls(m) = sc.logs; end
    [~, mo] = min(ls);
    meth(end + 1) = struct('name', 'oracle', 'g', gall{mo}, 'runs', sum(out.costConv) + sum(cellfun(@(x) x.runs, allc)), 'arm', mo);
    out.logsAll = ls;
    % ---- 3. bandit policies -------------------------------------------------
    pols = {'trial', tabs.main; 'trial_k02', tabs.k02; 'trial_k08', tabs.k08; 'ucb', []; 'ts', []; 'greedy', []};
    PL = cell(1, size(pols, 1));
    for q = 1:size(pols, 1)
        pn = pols{q, 1}; pk = pn; if strncmp(pn, 'trial', 5), pk = 'trial'; end
        Pq = policy_replay(pk, pols{q, 2}, A, tr, S); m = Pq.sel;
        [stc, cache] = cond_all(M, S, A, m, min(Pq.n(m), A.nIter(m)), rAll, dAll, sigAll, cache);
        meth(end + 1) = struct('name', pn, 'g', goal_predict(stc, S, M), 'runs', Pq.runs + stc.runs, 'arm', m); %#ok<AGROW>
        Pq.condRuns = stc.runs; PL{q} = Pq;
    end
    % ---- 4. scores ------------------------------------------------------------
    for q = 1:numel(meth)
        sc = goal_score(meth(q).g, tr, S);
        out.meth.(meth(q).name) = struct('cov', sc.cov', 'width', sc.width', 'err', sc.err', 'crps', sc.crps', ...
            'logs', sc.logs, 'riskErr', sc.riskErr, 'decErr', sc.decErr, 'risk', sc.risk, 'runs', meth(q).runs, ...
            'arm', meth(q).arm, 'mu', sc.mu', 's', sc.s', 'r', meth(q).g.r);
    end
    for q = 1:numel(PL)
        P = PL{q}; out.pol.(pols{q, 1}) = struct('sel', P.sel, 'n', P.n, 's', P.s, 'pm', P.pm, 'runs', P.runs, 'condRuns', P.condRuns);
    end
    if keepAll
        out.A = A; out.PL = PL; out.allc = allc; out.methFull = meth; out.cacheKeys = {cache.key};
    end
end
function [st, cache] = cond_all(M, S, A, m, it, rAll, dAll, sigAll, cache)
% Arm m conditioned on all data, from its heads iterate after iteration it (cached).
    key = [m it];
    for q = 1:numel(cache)
        if isequal(cache(q).key, key), st = cache(q).st; return; end
    end
    st = lm_restart(S, A.snap{m}{it}, rAll, dAll, sigAll);
    while ~st.conv, st = lm_iter(M, S, st); end
    cache(end + 1) = struct('key', key, 'st', st);
end
