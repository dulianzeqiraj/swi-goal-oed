function g = mar_goal_predict(M, S, st, sites, qSite)
%MAR_GOAL_PREDICT  Goal predictive of a calibrated arm with MAR injection at SITES.
%   Future heads at A and B under the planned pumping plus qSite m3/d at each
%   site: mean at the calibrated parameters, covariance J Sig J' + sd(xi_f)^2
%   hnat hnat' with J by forward differences (n + 1 runs, extra right-hand side)
%   and Sig the Laplace posterior of LM_PREDICT. Risk = 1 - Phi2 (BVN_CDF).
    arm = st.arm; [~, ~, Sig] = lm_predict(st, 1);
    Qm = zeros(M.Nc, 1); Qm(sites) = -qSite; s = M.supCell(:);
    fg = @(th) goal_mar(M, S, arm, th, Qm, s);
    [y0, hn] = fg(st.th); Jg = zeros(2, arm.n);
    for i = 1:arm.n, tp = st.th; tp(i) = tp(i) + S.fdStep; Jg(:, i) = (fg(tp) - y0) / S.fdStep; end
    C = Jg * Sig * Jg' + S.sigXi^2 * (hn * hn'); C = 0.5 * (C + C');
    sd = sqrt(diag(C)); r = min(max(C(1, 2) / (sd(1) * sd(2)), -0.999999), 0.999999);
    a = (y0 - S.hc) ./ sd;
    g = struct('mu', y0, 'C', C, 's', sd, 'r', r, 'risk', 1 - bvn_cdf(a(1), a(2), r), 'runs', arm.n + 1);
end
function [y, hn] = goal_mar(M, S, arm, th, Qm, s)
    u = full(arm.B * th(1:arm.nK)); Rch = M.R0; if arm.hasR, Rch = M.R0 * exp(th(end)); end
    H = fk_solve(M, u, Rch, Qm);
    y = H(s, 1) + S.Q(1) * H(s, 2) + S.Q(2) * H(s, 3) + H(s, 4); hn = H(s, 1);
end
