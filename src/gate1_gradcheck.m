function [passed, table_out] = gate1_gradcheck(solve_fwd, resfun_th, goalfun, dqdu_fun, theta, eta, hs)
%GATE1_GRADCHECK  Verify the discrete-adjoint goal gradient (Eq. S31).
%
%   [passed, table_out] = GATE1_GRADCHECK(solve_fwd, resfun_th, goalfun, ...
%                                         dqdu_fun, theta, eta, hs)
%
%   Gate 1 of the three-gate protocol. Compares the discrete-adjoint reduced
%   gradient of the scalar goal r(theta) = goalfun(u(theta)) against a
%   finite-difference directional derivative along eta, over a range of step
%   sizes hs, requiring relative error < 1e-5 at the best step.
%
%   The adjoint gradient is computed as:
%       u   = solve_fwd(theta)
%       J   = dR/du               (via assemble_jacobian_fd on resfun_th(.,theta))
%       mu  : J' mu = dqdu'       (goal adjoint)
%       dr/dtheta = -mu' * dR/dtheta
%   and compared to  ( r(theta + h*eta) - r(theta) ) / h.
%
%   INPUTS
%     solve_fwd  : u = solve_fwd(theta)            converged forward solve
%     resfun_th  : R = resfun_th(u, theta)         coupled residual
%     goalfun    : r = goalfun(u)                  scalar goal
%     dqdu_fun   : g = dqdu_fun(u)                 goal derivative dq/du (1-by-N)
%     theta      : base parameter vector
%     eta        : perturbation direction (default randn, normalized)
%     hs         : FD step sizes (default logspace(-2,-7,6))
%
%   OUTPUTS
%     passed     : true if min relative error < 1e-5
%     table_out  : [hs(:), fd(:), relerr(:)]
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 6 || isempty(eta), eta = randn(numel(theta),1); eta = eta/norm(eta); end
    if nargin < 7 || isempty(hs), hs = logspace(-2,-7,6); end

    % --- adjoint gradient at theta ---------------------------------------
    u   = solve_fwd(theta);
    res = @(uu) resfun_th(uu, theta);
    J   = assemble_jacobian_fd(res, u);
    % dR/dtheta by FD on theta (prototype; production uses analytic where cheap)
    dRdtheta = jac_theta(resfun_th, u, theta);
    g_adj = adjoint_goal_grad(J, dRdtheta, dqdu_fun(u));   % 1-by-n

    dir_adj = g_adj * eta;                                  % directional deriv
    r0 = goalfun(u);

    relerr = zeros(numel(hs),1); fd = zeros(numel(hs),1);
    for i = 1:numel(hs)
        h  = hs(i);
        up = solve_fwd(theta + h*eta);          % central difference: O(h^2),
        um = solve_fwd(theta - h*eta);          % so the FD reference is second
        fd(i)     = (goalfun(up) - goalfun(um)) / (2*h);   % order accurate
        relerr(i) = abs(dir_adj - fd(i)) / max(abs(dir_adj), eps);
    end
    [minerr, k] = min(relerr);
    passed = minerr < 1e-5;
    table_out = [hs(:), fd(:), relerr(:)];

    fprintf('Gate 1 (gradient check): min rel. error = %.3e at h = %.1e -> %s\n', ...
            minerr, hs(k), ternary(passed,'PASS','FAIL'));
end

% ----------------------------------------------------------------------
function g = adjoint_goal_grad(J, dRdtheta, dqdu)
    mu = J' \ dqdu';
    g  = -(mu' * dRdtheta);
end

function dRdtheta = jac_theta(resfun_th, u, theta)
    n  = numel(theta); R0 = resfun_th(u, theta); R0 = R0(:);
    dRdtheta = zeros(numel(R0), n); d = 1e-6*max(norm(theta),1);
    for j = 1:n                                  % central differences O(d^2)
        tp = theta; tp(j) = tp(j)+d;
        tm = theta; tm(j) = tm(j)-d;
        dRdtheta(:,j) = (resfun_th(u, tp) - resfun_th(u, tm))/(2*d);
    end
end

function s = ternary(c,a,b), if c, s=a; else, s=b; end, end
