function L = zeta_factor(M, S)
%ZETA_FACTOR  Lower Cholesky factor of the covariance of the sub-zonal log-K field
%   (sd S.zetaSd, exponential correlation exp(-d/S.zetaL), d in km) over the Nc
%   active cells, plus 1e-9 on the diagonal. Cached per session.
    persistent Lc key
    k = [M.Nc S.zetaSd S.zetaL];
    if isempty(Lc) || ~isequal(key, k)
        D = hypot(M.X - M.X', M.Y - M.Y');
        C = S.zetaSd^2 * exp(-D / S.zetaL); clear D
        C(1:M.Nc+1:end) = C(1:M.Nc+1:end) + 1e-9;
        Lc = chol(C, 'lower'); key = k;
    end
    L = Lc;
end
