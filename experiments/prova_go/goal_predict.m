function g = goal_predict(st, S, M)
%GOAL_PREDICT  Goal predictive of a calibrated arm: future heads at A and B.
%   Laplace predictive (LM_PREDICT) of the future heads plus the variance of the
%   future recharge change, sd(xi_f)^2 * hnat*hnat' (heads are affine in xi_f).
%   Returns mean mu (2x1), covariance C, sd s, the 90 % intervals and the
%   intrusion risk P(A or B intruded) = 1 - Phi2(a, b; r) (BVN_CDF of src).
    J = M.J; rows = [3*J+1; 3*J+2];
    [mu, C] = lm_predict(st, rows); hn = st.f(3*J+3:3*J+4);
    C = C + S.sigXi^2 * (hn * hn'); C = 0.5 * (C + C');
    s = sqrt(diag(C)); r = C(1, 2) / (s(1) * s(2)); r = min(max(r, -0.999999), 0.999999);
    a = (mu - S.hc) ./ s;
    g.mu = mu; g.C = C; g.s = s; g.r = r; g.lo = mu - S.z90 * s; g.hi = mu + S.z90 * s;
    g.risk = 1 - bvn_cdf(a(1), a(2), r);
    g.th = st.th; g.Rch = NaN; if st.arm.hasR, g.Rch = M.R0 * exp(st.th(end)); end
end
