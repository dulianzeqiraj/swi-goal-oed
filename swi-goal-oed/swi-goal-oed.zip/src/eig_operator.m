function [eig, IF, sigma0sq] = eig_operator(G, H, GamF, Gn)
%EIG_OPERATOR  Goal-oriented information operator and expected information gain.
%
%   [eig, IF, sigma0sq] = EIG_OPERATOR(G, H, GamF, Gn)
%
%   Implements the goal-oriented information operator (Eq. 8) and the
%   goal-oriented expected information gain (Lemma 1, Eq. 9) of
%
%     Zeqiraj, D. "Goal-Oriented Bayesian Experimental Design for
%     Variable-Density Seawater Intrusion" (in preparation).
%
%   I_F(d) = H GamF G' (G GamF G' + Gn)^{-1} G GamF H'
%   EIG    = 1/2 log det(H GamF H') / det(H GamF H' - I_F)
%   (scalar goal: EIG = -1/2 log(1 - I_F/sigma0^2),  sigma0^2 = h GamF h')
%
%   INPUTS
%     G    : m-by-n observation sensitivity (rows = monitoring candidates)
%     H    : p-by-n goal sensitivity (p=1 for a scalar goal)
%     GamF : n-by-n facies-conditional prior covariance (SPD)
%     Gn   : m-by-m observation-noise covariance (SPD)
%
%   OUTPUTS
%     eig      : expected information gain [nats]
%     IF       : goal-oriented information operator (p-by-p)
%     sigma0sq : prior goal variance H GamF H' (p-by-p)
%
%   Notes
%     Exact in the linear-Gaussian regime; the Laplace approximation
%     otherwise. See also GREEDY_DESIGN, demo_synthetic.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    % --- input checks -----------------------------------------------------
    [m, n]  = size(G);
    [p, nH] = size(H);
    assert(nH == n,            'eig_operator:dim', 'G and H must share the parameter dimension n.');
    assert(isequal(size(GamF), [n n]), 'eig_operator:dim', 'GamF must be n-by-n.');
    assert(isequal(size(Gn),   [m m]), 'eig_operator:dim', 'Gn must be m-by-m.');

    % --- prior goal covariance -------------------------------------------
    GH       = GamF * H';            % n-by-p
    sigma0sq = H * GH;               % p-by-p, = H GamF H'

    % --- information operator (Eq. 8) ------------------------------------
    GG  = G * GamF * G' + Gn;        % m-by-m posterior data covariance
    GgH = G * GH;                    % m-by-p, = G GamF H'
    % I_F = (G GamF H')' * (G GamF G' + Gn)^{-1} * (G GamF H')
    IF  = GgH' * (GG \ GgH);         % p-by-p, SPD by construction
    IF  = 0.5 * (IF + IF');          % symmetrize against round-off

    % --- expected information gain (Eq. 9) --------------------------------
    post = sigma0sq - IF;            % posterior goal covariance
    if p == 1
        ratio = max(1 - IF / sigma0sq, eps);   % guard against round-off <= 0
        eig   = -0.5 * log(ratio);
    else
        eig   = 0.5 * (logdet_spd(sigma0sq) - logdet_spd(post));
    end
    eig = max(eig, 0);               % EIG is nonnegative
end

% ----------------------------------------------------------------------
function ld = logdet_spd(A)
%LOGDET_SPD  Stable log-determinant of an SPD matrix via Cholesky.
    A = 0.5 * (A + A');
    [R, flag] = chol(A);
    if flag ~= 0
        % nudge onto the SPD cone if marginally indefinite from round-off
        s = svd(A);
        A = A + (eps + abs(min(s))) * eye(size(A));
        R = chol(A);
    end
    ld = 2 * sum(log(diag(R)));
end
