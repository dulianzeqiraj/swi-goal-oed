function p = bvn_cdf(a, b, r)
%BVN_CDF  Standard bivariate normal CDF, P(X < a, Y < b) with corr(X,Y) = r.
%
%   p = BVN_CDF(a, b, r)
%
%   Base MATLAB only (no Statistics Toolbox). Uses the one-dimensional form
%       Phi2(a,b;r) = int_{-inf}^{a} phi(t) Phi((b - r t)/sqrt(1-r^2)) dt
%   with 64-point Gauss-Legendre quadrature on [-9, a]. a and b may be arrays
%   of the same size (or one of them scalar); r is a scalar with |r| < 1.
%   Accuracy is better than 1e-10 against Phi2(0,0;r) = 1/4 + asin(r)/(2 pi).
%
%   Used by PRAG_MAR (risk-oriented MAR siting) for the probability that at
%   least one of two supply wells is intruded, 1 - Phi2(a, b; r).
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    assert(isscalar(r) && abs(r) < 1, 'bvn_cdf:r', 'r must be a scalar with |r| < 1.');
    if isscalar(a), a = a + zeros(size(b)); end
    if isscalar(b), b = b + zeros(size(a)); end
    assert(isequal(size(a), size(b)), 'bvn_cdf:size', 'a and b must have the same size.');

    persistent x w
    if isempty(x), [x, w] = gauss_legendre(64); end

    lo = -9;
    hi = max(a(:), lo + 1e-12);                 % column of upper limits
    t  = 0.5 * (hi - lo) * x' + 0.5 * (hi + lo); % numel(a)-by-64 nodes
    s  = sqrt(1 - r^2);
    f  = exp(-0.5 * t.^2) / sqrt(2*pi) .* ncdf((b(:) - r * t) / s);
    p  = reshape(0.5 * (hi - lo) .* (f * w), size(a));
    p  = min(max(p, 0), 1);
end

function y = ncdf(x)
    y = 0.5 * erfc(-x / sqrt(2));
end

function [x, w] = gauss_legendre(n)
%GAUSS_LEGENDRE  Nodes and weights on [-1, 1] (Golub-Welsch).
    k    = (1:n-1)';
    beta = k ./ sqrt(4 * k.^2 - 1);
    J    = diag(beta, 1) + diag(beta, -1);
    [V, D] = eig(J);
    [x, i] = sort(diag(D));
    w = 2 * V(1, i)'.^2;
end
