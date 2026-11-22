function [H, nrun] = fk_solve(M, u, Rch, Q)
%FK_SOLVE  One model run: assemble, factorise once, solve for several right-hand sides.
%   H = FK_SOLVE(M, u, Rch) returns Nc-by-3 columns [h_R, g_A, g_B]: the head under
%   recharge Rch alone, and the head per m3/d of EXTRACTION at the supply wells A
%   and B (negative: pumping lowers the head). Any pumping state is the linear
%   combination h = h_R + Q_A g_A + Q_B g_B. H = FK_SOLVE(M,u,Rch,Q) with Q an
%   Nc-by-m matrix of extra extraction rates [m3/d] returns [h_R, g_A, g_B, h_Q]
%   with h_Q the head change due to each column of Q (injection: negative Q).
%   The interior (non-coastal) block is symmetric positive definite after a sign
%   change, so it is solved by a sparse Cholesky factorisation; FK_CHECKS
%   verifies the result against A\rhs of the builder's own operator. nrun = 1.
    T  = M.K0c .* exp(u(:)) * M.b;
    Tf = 0.5 * (T(M.ek) + T(M.el));                       % one value per undirected active face
    d  = accumarray([M.ek; M.el], [Tf; Tf], [M.Nc 1]);    % sum of face transmissivities per cell
    ii = M.ni;                                            % interior (non-coastal) cells
    inn = M.e_int;                                        % faces with both cells interior
    Kd = sparse([M.pi(M.ek(inn)); M.pi(M.el(inn))], [M.pi(M.el(inn)); M.pi(M.ek(inn))], -[Tf(inn); Tf(inn)], numel(ii), numel(ii)) ...
         + sparse(1:numel(ii), 1:numel(ii), d(ii), numel(ii), numel(ii));
    nq = 0; if nargin >= 4 && ~isempty(Q), nq = size(Q, 2); end
    B = zeros(numel(ii), 3 + nq);
    B(:, 1) = Rch * M.dxm^2;                              % (-A) h = -rhs  ->  recharge enters as +R dx^2
    B(M.pi(M.cellA), 2) = -1;                             % extraction of 1 m3/d at A
    B(M.pi(M.cellB), 3) = -1;
    if nq > 0, B(:, 4:end) = -Q(ii, :); end
    [L, p, q] = chol(Kd, 'lower', 'vector');
    if p ~= 0, error('fk_solve:spd', 'Flow matrix not positive definite.'); end
    X = zeros(size(B)); X(q, :) = L' \ (L \ B(q, :));
    H = zeros(M.Nc, size(B, 2)); H(ii, :) = X;            % coastal cells: h = 0
    nrun = 1;
end
