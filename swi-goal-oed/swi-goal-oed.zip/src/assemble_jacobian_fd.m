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
    % FD step for the central-difference Jacobian. 1e-6 is a robust choice for
    % the coupled head/concentration state (mixed magnitudes: h_f ~ 1e-4,
    % C ~ O(1)); a larger step degrades the tiny-h_f columns.
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
