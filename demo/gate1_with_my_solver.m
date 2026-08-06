function gate1_with_my_solver(my_forward_solve, ctx, theta0, d, goal_region)
%GATE1_WITH_MY_SOLVER  Run Gate 1 (and a design evaluation) on YOUR solver.
%
%   gate1_with_my_solver(my_forward_solve, ctx, theta0, d, goal_region)
%
%   Once my_solver_residual.m is filled in, this harness verifies the discrete
%   adjoint on YOUR benchmark-verified physics (Gate 1) and computes a goal-oriented
%   design — the step that certifies an external production solver before
%   Section-7/8-style design runs.
%
%   INPUTS
%     my_forward_solve : u = my_forward_solve(theta, d, ctx)  — YOUR solver,
%                        returns the converged state u* = [h_f; C]
%     ctx              : context struct passed to my_solver_residual
%     theta0           : base parameter vector
%     d                : design struct (d.mar_nodes, d.mar_rate)
%     goal_region      : logical mask over the n nodes defining the goal
%                        Q = sum of C over the region (edit for your QoI)
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 5
        fprintf(['gate1_with_my_solver is a template: it runs Gate 1 on YOUR solver.\n' ...
                 'Call it as\n' ...
                 '    gate1_with_my_solver(my_forward_solve, ctx, theta0, d, goal_region)\n' ...
                 'after filling in src/my_solver_residual.m.\n' ...
                 'For the self-contained Gate-1 run of the article, use demo/gate1_henry_vd.\n']);
        return
    end

    addpath(fullfile(fileparts(mfilename('fullpath')), '..', 'src'));

    resT  = @(u,th) my_solver_residual(u, th, d, ctx);
    solve = @(th)   my_forward_solve(th, d, ctx);

    % --- converged state and residual self-test ---------------------------
    u = solve(theta0); n = numel(u)/2;
    rn = norm(resT(u, theta0));
    fprintf('Residual at converged u*: %.2e %s\n', rn, ternary(rn<1e-6,'(ok)','(check: should be ~0)'));

    % --- goal definition --------------------------------------------------
    region = goal_region(:);
    goalfun = @(uu) sum(uu(n + find(region)));      % Q = integrated C over region
    dqdu    = @(uu) [zeros(1,n), double(region)'];  % dq/du

    % --- Gate 1: discrete-adjoint gradient check on YOUR physics ----------
    fprintf('\n=== Gate 1 on the production solver ===\n');
    rng(0); eta = randn(numel(theta0),1); eta = eta/norm(eta);
    [passed,~] = gate1_gradcheck(solve_wrap(solve), resT, goalfun, dqdu, theta0, eta);
    if ~passed
        warning(['Gate 1 did not reach 1e-5. Check: (i) residual is evaluated, not solved; ' ...
                 '(ii) Dirichlet BCs are identity-row; (iii) nodal ordering of u matches the solver.']);
        return
    end

    % --- design sensitivities + EIG (real numbers for Sections 7-8) -------
    fprintf('\n=== Goal-oriented design on the production solver ===\n');
    J        = assemble_jacobian_fd(@(uu) resT(uu, theta0), u);   % central FD, auto step
    dRdtheta = jac_theta(resT, u, theta0);
    cand     = (1:2:n)';                              % EDIT: your candidate monitoring nodes
    dOdu     = zeros(numel(cand), 2*n);
    for i = 1:numel(cand), dOdu(i, n + cand(i)) = 1; end   % observe concentration
    [G, H]   = adjoint_solve(J, dRdtheta, dOdu, dqdu(u));

    % EDIT: replace with your facies-conditional prior GamF and noise model
    GamF  = 0.3*eye(numel(theta0)) + 0.7*ones(numel(theta0));
    noise = 0.05*ones(numel(cand),1);
    [S, eigS] = greedy_design(G, H, GamF, noise, 2, ones(numel(cand),1));
    fprintf('selected monitoring nodes: [%s]\n', num2str(cand(S)'));
    fprintf('goal-oriented EIG = %.4f nats  (REAL — production solver)\n', eigS);
end

% ---------------------------------------------------------------------
function f = solve_wrap(solve)
    f = @(theta) solve(theta);   % gate1_gradcheck expects u = solve_fwd(theta)
end
function dRdtheta = jac_theta(resfun_th, u, theta)
    nT=numel(theta); R0=resfun_th(u,theta); R0=R0(:);
    dRdtheta=zeros(numel(R0),nT); dd=1e-6*max(norm(theta),1);
    for j=1:nT
        tp=theta; tp(j)=tp(j)+dd; tm=theta; tm(j)=tm(j)-dd;
        dRdtheta(:,j)=(resfun_th(u,tp)-resfun_th(u,tm))/(2*dd);
    end
end
function s = ternary(c,a,b), if c, s=a; else, s=b; end, end
