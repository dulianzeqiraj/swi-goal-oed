function g = gittins_lookup(T, p, n)
%GITTINS_LOOKUP  Robust Gittins index at state (p, n) by bilinear interpolation in the table of ROBUST_GITTINS_TABLE (n clipped to 1..N).
    p = min(max(p, 0), 1); n = min(max(n, T.n(1)), T.n(end));
    g = interp2(T.n, T.p, T.gam, n, p, 'linear');
end
