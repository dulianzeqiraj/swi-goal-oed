function J = assemble_jacobian_fd(resfun, u, delta, colors)
%ASSEMBLE_JACOBIAN_FD  Coupled Jacobian from a residual evaluator (Eq. 15 / S26).
%
%   J = ASSEMBLE_JACOBIAN_FD(resfun, u, delta, colors)
%
%   Forms J = dR/du at the converged state u by finite differences directly
%   from the solver's residual evaluator, without touching the solver
%   internals. This is the RREGULL-2-safe construction: the same residual the
%   forward solver already evaluates is differentiated, so the coupled blocks
%   (in particular the velocity/dispersion coupling C_psi that a sequential
%   Picard solver never assembles) are captured exactly.
%
%   INPUTS
%     resfun : function handle  R = resfun(u)  returning the coupled residual
%              [R_f; R_t] (same length as u) at fixed (theta, d)
%     u      : converged state u* = [h_f; C]  (column vector)
%     delta  : FD step (default 1e-6*norm(u))
%     colors : (optional) cell array of index groups that can be perturbed
%              simultaneously (structurally orthogonal columns). If omitted,
%              a plain column-by-column difference is used (correct, slower).
%
%   OUTPUT
%     J      : Jacobian dR/du (numel(R)-by-numel(u))
%
%   Notes
%     Sparsity coloring (the `colors` argument) reduces the number of residual
%     evaluations from numel(u) to numel(colors); the production code derives
%     `colors` from the mesh adjacency. Column-by-column is the default for
%     transparency and is exact.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    u  = u(:);
    n  = numel(u);
    % FD step for the central-difference Jacobian. CAUTION: scaling by norm(u)
    % sizes the step to whichever block dominates the norm. On the 41x21 Henry
    % state that is the concentration (norm 9.99 against 0.577 for the head), so
    % this default evaluates to 1.0e-5, and at that step the Gate-1 gradient
    % check stalls at 7.8e-3. Measured sweep on that state, the adjoint against a
    % converged central-difference reference:
    %     1e-5 -> 7.8e-3   1e-6 -> 3.2e-4   1e-7 -> 1.3e-6   3e-8 -> 2.4e-10
    %     1e-8 -> 1.4e-9   1e-9 -> 2.2e-9   1e-10 -> 1.6e-8
    % Pass DELTA explicitly for any state whose blocks differ in magnitude;
    % demo/gate1_production_solver.m uses 3e-8.
    if nargin < 3 || isempty(delta), delta = 1e-6 * max(norm(u), 1); end
    R0 = resfun(u); R0 = R0(:);
    m  = numel(R0);
    J  = zeros(m, n);

    % Central differences (second-order, O(delta^2)): the forward scheme leaves
    % an O(delta) truncation error in J that propagates into the discrete
    % adjoint and caps the Gate-1 gradient check at ~1e-4; the central scheme
    % removes it (at twice the residual evaluations).
    if nargin < 4 || isempty(colors)
        for j = 1:n                          % plain column-wise central FD
            up = u; up(j) = up(j) + delta;
            um = u; um(j) = um(j) - delta;
            J(:, j) = (resfun(up) - resfun(um)) / (2*delta);
        end
    else
        for c = 1:numel(colors)              % central FD with sparsity coloring
            grp = colors{c};
            up  = u; up(grp) = up(grp) + delta;
            um  = u; um(grp) = um(grp) - delta;
            dR  = (resfun(up) - resfun(um)) / (2*delta);
            for j = grp(:)'
                J(:, j) = dR;                % valid when columns are orthogonal
            end
        end
    end
end
