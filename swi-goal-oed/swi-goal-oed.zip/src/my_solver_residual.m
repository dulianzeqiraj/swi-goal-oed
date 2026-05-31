function R = my_solver_residual(u, theta, d, ctx)
%MY_SOLVER_RESIDUAL  TEMPLATE: residual evaluator wrapping YOUR validated solver.
%
%   R = MY_SOLVER_RESIDUAL(u, theta, d, ctx)
%
%   This is the ONE function you fill in to connect the adjoint OED pipeline
%   to your validated MATLAB/FORTRAN variable-density solver. The pipeline
%   (assemble_jacobian_fd -> adjoint_solve -> eig_operator) depends ONLY on
%   this residual, so once it is correct the whole framework runs on your
%   real physics. Replace the calls to vd_residual with this function.
%
%   ====================== THE CONTRACT (read carefully) ======================
%   You must return the *residual of the discrete coupled system evaluated at
%   the given state u* — NOT the solved state. Do NOT call your iterative
%   (Picard/Newton) solver inside here: assemble the operators at the supplied
%   (h_f, C, theta, d) and return [A_f h_f - b_z - f_mar ; A_c C - f_c].
%   The Jacobian is built by perturbing u component-by-component, so this
%   function MUST be evaluable at an ARBITRARY (non-converged) u.
%
%   INPUTS
%     u     : column vector, length 2n, stacked state  u = [h_f ; C]
%                h_f = u(1:n)        equivalent freshwater head at the n nodes
%                C   = u(n+1:2n)     salt concentration at the n nodes
%             (n = number of nodes; the nodal ordering MUST match your solver)
%     theta : column vector, length n_theta, the uncertain parameters
%             (e.g. nodal or zonal log-conductivity; need not equal n)
%     d     : design struct
%                d.mar_nodes : indices in 1..n of MAR/injection nodes
%                d.mar_rate  : injection rates (same length as d.mar_nodes)
%             (add your own fields as needed; observations do NOT enter here)
%     ctx   : (optional) struct of everything your assembly needs that is NOT
%             being differentiated — mesh, element tables, BC data, physical
%             constants. Bind it once and pass it through (see the example).
%
%   OUTPUT
%     R     : column vector, length 2n, the coupled residual  R = [R_f ; R_t]
%                R_f = A_f(C,theta) * h_f - b_z(C,theta) - f_mar(d)
%                R_t = A_c(h_f,C,theta) * C - f_c
%             At your converged solution u*, norm(R) must be ~0 (self-test below).
%   ==========================================================================
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    n  = numel(u)/2;
    assert(mod(numel(u),2)==0, 'u must have even length 2n = [h_f; C].');
    hf = u(1:n);
    C  = u(n+1:2*n);

    % ----------------------------------------------------------------------
    % TODO 1 — assemble the FLOW operators at the given (C, theta).
    %   A_f : n-by-n conductance (density-weighted), function of C and theta
    %   b_z : n-by-1 buoyancy load,  function of C and theta
    % Call YOUR assembly routine here, e.g.:
    %   [A_f, b_z] = my_assemble_flow(C, theta, ctx);
    % ----------------------------------------------------------------------
    A_f = []; b_z = [];   % <-- replace
    error('my_solver_residual: fill TODO 1 (flow assembly).');

    % ----------------------------------------------------------------------
    % TODO 2 — assemble the TRANSPORT operator at the given (h_f, C, theta).
    %   A_c : n-by-n advection + dispersion (+ stabilization), depends on the
    %         Darcy velocity q(h_f) and on C, theta
    %   f_c : n-by-1 transport load / source
    % Call YOUR assembly routine here, e.g.:
    %   [A_c, f_c] = my_assemble_transport(hf, C, theta, ctx);
    % ----------------------------------------------------------------------
    A_c = []; f_c = [];   % <-- replace

    % ----------------------------------------------------------------------
    % TODO 3 — MAR / injection sources in the flow equation.
    % ----------------------------------------------------------------------
    f_mar = zeros(n,1);
    if isfield(d,'mar_nodes') && ~isempty(d.mar_nodes)
        f_mar(d.mar_nodes) = f_mar(d.mar_nodes) + d.mar_rate(:);
    end

    % ----------------------------------------------------------------------
    % TODO 4 — apply the SAME Dirichlet boundary conditions your solver uses,
    % as IDENTITY rows (not a large penalty), so the Jacobian stays well
    % conditioned:  for each constrained node i,  A(i,:) = e_i,  rhs(i) = value
    % (sea: C = C_sea, h_f = hydrostatic; freshwater inflow: C = 0, h_f = ref).
    % ----------------------------------------------------------------------

    % ---- assemble the coupled residual (do NOT solve) --------------------
    R_f = A_f*hf - b_z - f_mar;
    R_t = A_c*C  - f_c;
    R   = [R_f; R_t];

    % ---- dimension self-checks -------------------------------------------
    assert(isequal(size(A_f),[n n]) && isequal(size(A_c),[n n]), 'A_f, A_c must be n-by-n.');
    assert(numel(R)==2*n, 'R must have length 2n.');
end

% =====================================================================
% HOW TO WIRE IT IN (example; delete once integrated)
% =====================================================================
%   ctx  = my_build_context();                 % mesh, BC data, constants
%   d    = struct('mar_nodes',[], 'mar_rate',[]);
%   res  = @(u)    my_solver_residual(u, theta0, d, ctx);      % fixed theta
%   resT = @(u,th) my_solver_residual(u, th,     d, ctx);      % theta-dependent
%
%   % SELF-TEST: at your solver's converged state u*, the residual is ~0
%   u_star = my_forward_solve(theta0, d, ctx);  % YOUR validated solver
%   fprintf('residual at u*: %.2e (should be ~1e-8 or smaller)\n', norm(res(u_star)));
%
%   % then run Gate 1 on your real physics (see gate1_with_my_solver.m)
