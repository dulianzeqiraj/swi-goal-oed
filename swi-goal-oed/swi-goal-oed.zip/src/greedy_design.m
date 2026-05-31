function [S, eig_S, trace_out] = greedy_design(Gcand, H, GamF, noise_var, budget, cost)
%GREEDY_DESIGN  Cost-aware greedy maximization of goal-oriented EIG.
%
%   [S, eig_S, trace_out] = GREEDY_DESIGN(Gcand, H, GamF, noise_var, budget, cost)
%
%   Greedily selects monitoring candidates to maximize the goal-oriented
%   expected information gain per unit cost, subject to a budget
%   (knapsack-type) constraint, evaluating the objective J(d) of Eq. (10)
%   through EIG_OPERATOR (Lemma 1).
%
%   At each step the candidate with the largest marginal gain
%       Delta_j / cost_j ,   Delta_j = EIG(S U {j}) - EIG(S)
%   is added, until the budget is exhausted.
%
%   INPUTS
%     Gcand     : M-by-n matrix; row j is the observation sensitivity of
%                 candidate monitoring location j
%     H         : p-by-n goal sensitivity (p=1 for scalar goal)
%     GamF      : n-by-n facies-conditional prior covariance (SPD)
%     noise_var : scalar observation-noise variance (i.i.d.) OR
%                 M-by-1 per-candidate variances
%     budget    : scalar total budget B (knapsack constraint sum(cost(S))<=B)
%     cost      : M-by-1 per-candidate costs (default: ones -> cardinality)
%
%   OUTPUTS
%     S         : selected candidate indices (row vector)
%     eig_S     : EIG of the selected design
%     trace_out : struct with per-step .added, .eig, .marginal, .cost
%
%   Notes
%     The goal-oriented, correlated objective is only weakly submodular in
%     general (see the companion paper); the greedy guarantee should be
%     reported as a curvature-bounded bound, not the classical (1-1/e).
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    M = size(Gcand, 1);
    if nargin < 6 || isempty(cost), cost = ones(M, 1); end
    if isscalar(noise_var), noise_var = noise_var * ones(M, 1); end
    cost = cost(:); noise_var = noise_var(:);

    S = []; spent = 0; cur_eig = 0;
    trace_out = struct('added', {}, 'eig', {}, 'marginal', {}, 'cost', {});

    remaining = true(M, 1);
    while true
        best_j = 0; best_ratio = -inf; best_eig = cur_eig;
        for j = find(remaining)'
            if spent + cost(j) > budget, continue; end
            Stry = [S, j];
            Gtry = Gcand(Stry, :);
            Gn   = diag(noise_var(Stry));
            e    = eig_operator(Gtry, H, GamF, Gn);
            ratio = (e - cur_eig) / cost(j);
            if ratio > best_ratio
                best_ratio = ratio; best_j = j; best_eig = e;
            end
        end
        if best_j == 0, break; end           % nothing affordable improves
        S = [S, best_j];                     %#ok<AGROW>
        spent = spent + cost(best_j);
        trace_out(end+1) = struct('added', best_j, 'eig', best_eig, ...
                                  'marginal', best_eig - cur_eig, ...
                                  'cost', cost(best_j)); %#ok<AGROW>
        remaining(best_j) = false;
        cur_eig = best_eig;
    end
    eig_S = cur_eig;
end
