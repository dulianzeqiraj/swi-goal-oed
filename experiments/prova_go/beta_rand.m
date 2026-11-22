function x = beta_rand(a, b, u)
%BETA_RAND  Beta(a, b) draw by inversion of u ~ U(0,1) (bisection on betainc; base MATLAB/Octave).
    lo = zeros(size(u)); hi = ones(size(u));
    for it = 1:50
        x = 0.5 * (lo + hi); up = betainc(x, a, b) < u;
        lo(up) = x(up); hi(~up) = x(~up);
    end
    x = 0.5 * (lo + hi);
end
