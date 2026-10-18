function q = fkcl_wquantile(x, w, p)
%FKCL_WQUANTILE  Weighted quantiles: the smallest x whose cumulative weight reaches p
%   (the rule of the Python reference, numpy.searchsorted on the cumulative weights).
    [xs, o] = sort(x(:)); c = cumsum(w(o)); c = c / c(end);
    q = zeros(size(p));
    for k = 1:numel(p)
        i = find(c >= p(k) - 1e-15, 1, 'first');
        if isempty(i), i = numel(xs); end
        q(k) = xs(i);
    end
end
