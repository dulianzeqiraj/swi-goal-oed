function [G, H] = adjoint_solve(J, dRdtheta, dOdu, dqdu)
%ADJOINT_SOLVE  Observation and goal sensitivities via two adjoint solves (Eq. 16 / S27).
%
%   [G, H] = ADJOINT_SOLVE(J, dRdtheta, dOdu, dqdu)
%
%   Given the coupled Jacobian J = dR/du, solves the two discrete adjoint
%   systems that share the transpose operator J' (one sparse factorization,
%   two back-substitutions),
%
%       J' Lambda = dOdu'   ->  G = -Lambda' * dRdtheta     (observation sensitivity)
%       J' mu     = dqdu'   ->  H = -mu'     * dRdtheta     (goal sensitivity)
%
%   INPUTS
%     J        : coupled Jacobian dR/du (N-by-N), N = numel(u)
%     dRdtheta : parameter derivative of the residual, dR/dtheta (N-by-n)
%     dOdu     : observation operator derivative dO/du (m-by-N), one row per
%                monitoring candidate
%     dqdu     : goal derivative dq/du (p-by-N), p = 1 for a scalar goal
%
%   OUTPUTS
%     G        : observation sensitivity (m-by-n)  -> rows feed eig_operator
%     H        : goal sensitivity (p-by-n)
%
%   Notes
%     Use a single factorization of J' for efficiency:
%       [L,U,P,Q] = lu(J');  Lambda = Q*(U\(L\(P*dOdu')));  mu = Q*(U\(L\(P*dqdu')));
%     The straightforward backslash below is used for clarity.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    Jt     = J';
    Lambda = Jt \ dOdu';            % N-by-m
    mu     = Jt \ dqdu';            % N-by-p
    G      = -(Lambda' * dRdtheta); % m-by-n
    H      = -(mu'     * dRdtheta); % p-by-n
end
