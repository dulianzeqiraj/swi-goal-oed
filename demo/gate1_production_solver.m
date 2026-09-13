function gate1_production_solver(Nx, Ny, delta)
%GATE1_PRODUCTION_SOLVER  Gate 1 on the solver that also passes Gate 2.
%
%   GATE1_PRODUCTION_SOLVER(NX, NY, DELTA)
%
%   demo/gate1_henry_vd.m carries its own finite-element assembly on an 11 by 6 mesh,
%   while the Henry results reported in the article come from src/vd_residual.m through
%   src/vd_solve_forward.m, a cell-centred finite-volume discretization solved by damped
%   Newton. This driver puts the discrete adjoint of THAT solver through the Gate-1
%   gradient check, so the adjoint that is verified is the adjoint of the solver whose toe
%   is reported.
%
%   The goal functional is the one demo/gate1_henry_vd.m uses: salt mass in the landward
%   window 1.0 < x < 1.6.
%
%   DELTA is the finite-difference step for the Jacobian. Do not leave it to
%   assemble_jacobian_fd's default here: that default scales with norm(u), which on this
%   state is dominated by the concentration block, giving a step two orders too coarse for
%   the head block. See the comment in src/assemble_jacobian_fd.m for the measured sweep.
%
%   On the 41 by 21 mesh with DELTA = 3e-8 this reports
%       min relative error = 2.442e-10  (tolerance 1e-5)
%   on the same solve that gives the Gate-2 toe 1.1919 m (0.5959 of the cell length) and
%   the coupled residual 5.782e-16.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1 || isempty(Nx),    Nx = 41;    end
    if nargin < 2 || isempty(Ny),    Ny = 21;    end
    if nargin < 3 || isempty(delta), delta = 3e-8; end

    here = fileparts(fileparts(mfilename('fullpath')));
    addpath(fullfile(here,'src'), fullfile(here,'demo'));

    g = make_grid(Nx, Ny, 2.0, 1.0);
    P = vd_params();
    theta0 = zeros(g.N,1);
    fprintf('=== Gate 1 on the production solver ===\n');
    fprintf('grid %dx%d (N = %d, state 2N = %d), Jacobian FD step %.1e\n', ...
            g.Nx, g.Ny, g.N, 2*g.N, delta);

    [U0, nF0, it0] = vd_solve_forward(theta0, g, P, 1e-12, 80);
    fprintf('forward: %d Newton steps, coupled |F| = %.3e\n', it0, nF0);

    % goal: salt mass in 1.0 < x < 1.6. Packing is k = (j-1)*Nx + i, i the column.
    icol = mod((1:g.N)'-1, g.Nx) + 1;
    mask = (g.xc(icol)' > 1.0) & (g.xc(icol)' < 1.6);
    goalfun = @(UU) sum(UU(g.N + find(mask)));
    dqdu    = [zeros(1,g.N), double(mask(:)')];
    fprintf('goal window: %d of %d cells, goal = %.10g\n', sum(mask), g.N, goalfun(U0));

    res = @(uu) vd_residual(uu, theta0, g, P);
    J   = assemble_jacobian_fd(res, U0, delta);
    dRdtheta = jac_theta(@(uu,th) vd_residual(uu,th,g,P), U0, theta0);
    mu    = J' \ dqdu';
    g_adj = -(mu' * dRdtheta);

    rng(1); eta = randn(g.N,1); eta = eta/norm(eta);
    dir_adj = g_adj * eta;
    fprintf('adjoint directional derivative = %.12g\n\n', dir_adj);

    fprintf('      h            central FD            rel. error\n');
    best = inf;
    for h = [1e-3 1e-4 1e-5]
        up = vd_solve_forward(theta0 + h*eta, g, P, 1e-12, 80);
        um = vd_solve_forward(theta0 - h*eta, g, P, 1e-12, 80);
        fd = (goalfun(up) - goalfun(um)) / (2*h);
        re = abs(dir_adj - fd) / max(abs(dir_adj), eps);
        best = min(best, re);
        fprintf('  %8.1e   %18.12g   %10.3e\n', h, fd, re);
    end
    if best < 1e-5, verdict = 'PASS'; else, verdict = 'FAIL'; end
    fprintf('\nmin relative error = %.3e  ->  %s  (tolerance 1e-5)\n', best, verdict);

    C = reshape(U0(g.N+1:2*g.N), g.Nx, g.Ny).';
    fprintf('Gate-2 quantities from the same solve: toe x = %.4f m (%.4f L), |F| = %.3e\n', ...
            toe_at_base(C, g), toe_at_base(C, g)/g.Lx, nF0);
end

% -------------------------------------------------------------------------
function dRdtheta = jac_theta(resfun_th, u, theta)
    n = numel(theta); R0 = resfun_th(u, theta); R0 = R0(:);
    dRdtheta = zeros(numel(R0), n); d = 1e-6*max(norm(theta),1);
    for j = 1:n                                  % central differences
        tp = theta; tp(j) = tp(j)+d;
        tm = theta; tm(j) = tm(j)-d;
        dRdtheta(:,j) = (resfun_th(u, tp) - resfun_th(u, tm))/(2*d);
    end
end

function toe = toe_at_base(C, g)
    xc = g.xc; cb = C(1,:); toe = NaN;
    for i = 1:numel(xc)-1
        if (cb(i)-0.5)*(cb(i+1)-0.5) <= 0 && cb(i) ~= cb(i+1)
            toe = xc(i) + (0.5-cb(i))/(cb(i+1)-cb(i))*(xc(i+1)-xc(i)); return;
        end
    end
end
