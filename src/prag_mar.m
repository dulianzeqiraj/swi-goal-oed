function [risk, info] = prag_mar(A, cells, C, mu, hc)
%PRAG_MAR  Risk-oriented managed-aquifer-recharge field (PRAG-MAR closed form).
%
%   [risk, info] = PRAG_MAR(A, cells, C, mu, hc)
%
%   The published pipeline ranks recharge cells by the adjoint of the intruded
%   AREA (MAR_c in FUSHE_KUQE_FIELD_DESIGN). PRAG-MAR ranks them by how much
%   they lower the PROBABILITY that a supply well is salinized.
%
%   For the steady confined model A h = rhs, a recharge Q [m3/day] at cell k
%   adds -Q e_k to rhs, so at fixed conductivity the head is linear in Q:
%       h(Q) = h + Q g_k,      g_w = -A^{-T} e_w   (one transposed solve per well).
%   With Gaussian heads at the supply wells, h_w ~ N(mu_w, C), a well is
%   intruded when h_w < hc (Ghyben-Herzberg: hc = delta*base), and
%     one well : P = Phi(-a),
%                -dP/dQ_k = phi(a)/s g_k
%     two wells: P = 1 - Phi2(a, b; r)                        (A or B intruded)
%                -dP/dQ_k = phi(a)/s_A Phi((b - r a)/sqrt(1-r^2)) g_A,k
%                         + phi(b)/s_B Phi((a - r b)/sqrt(1-r^2)) g_B,k
%   with a = (mu_A - hc)/s_A, b = (mu_B - hc)/s_B, s the standard deviations
%   and r the correlation. Each well is weighted by the probability density of
%   sitting exactly at the threshold, so a well that is surely safe or surely
%   lost gets no weight. The cost is two adjoint solves on the operator that
%   the published MAR field already uses.
%
%   INPUTS
%     A     : Nc-by-Nc sparse flow operator at the linearization point
%     cells : one or two active-cell indices of the supply wells
%     C     : covariance of the heads at those cells, e.g. S(cells,:)*GamF*S(cells,:)'
%     mu    : mean heads at those cells, e.g. h0(cells)
%     hc    : critical head [m]
%
%   OUTPUTS
%     risk  : Nc-by-1, reduction of the intrusion probability per m3/day of
%             recharge at each cell (larger is better)
%     info  : struct with P0 (prior probability that a well is intruded),
%             z = [a b], s, r, weights and the adjoints g (Nc-by-nw)
%
%   Validated by demo/prag_mar_selftest.m; field application in
%   demo/fushe_kuqe_prag_mar.m. See also PRAG_MAR_CHECK, BVN_CDF.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    cells = cells(:); nw = numel(cells); mu = mu(:);
    assert(nw == 1 || nw == 2, 'prag_mar:wells', 'PRAG-MAR takes one or two supply wells.');
    assert(isequal(size(C), [nw nw]) && numel(mu) == nw, 'prag_mar:dim', 'C must be nw-by-nw and mu nw-by-1.');

    Nc = size(A, 1);
    E  = full(sparse(cells, (1:nw)', 1, Nc, nw));
    g  = -(A' \ E);                              % g(k,w) = dh_w / dQ_k

    s  = sqrt(diag(C));
    z  = (mu - hc) ./ s;                         % standardized distance above the threshold
    nphi = @(x) exp(-0.5 * x.^2) / sqrt(2*pi);
    ncdf = @(x) 0.5 * erfc(-x / sqrt(2));
    if nw == 1
        r   = NaN;
        wts = nphi(z) / s;
        P0  = ncdf(-z);
    else
        r   = C(1, 2) / (s(1) * s(2));
        q   = sqrt(1 - r^2);
        wts = [nphi(z(1)) * ncdf((z(2) - r * z(1)) / q) / s(1);
               nphi(z(2)) * ncdf((z(1) - r * z(2)) / q) / s(2)];
        P0  = 1 - bvn_cdf(z(1), z(2), r);
    end
    risk = g * wts;

    info = struct('P0', P0, 'z', z', 's', s', 'r', r, 'weights', wts', 'g', g);
end
