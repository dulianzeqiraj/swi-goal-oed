function q = fkcl_quantile(A, p)
%FKCL_QUANTILE  Quantiles along the first dimension with linear interpolation between order
%   statistics (the default of numpy.quantile, R type 7); no toolbox needed.
%   A is n x m, p a vector of probabilities; q is numel(p) x m.
    A = sort(A, 1); n = size(A, 1);
    q = zeros(numel(p), size(A, 2));
    for k = 1:numel(p)
        h = (n - 1) * p(k) + 1; lo = floor(h); hi = min(lo + 1, n); t = h - lo;
        q(k, :) = (1 - t) * A(lo, :) + t * A(hi, :);
    end
end
