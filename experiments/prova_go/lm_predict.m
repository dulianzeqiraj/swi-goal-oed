function [mu, C, Sig] = lm_predict(st, rows)
%LM_PREDICT  Laplace (linearised) predictive of outputs ROWS at the current iterate.
%   Posterior covariance Sig = (J_d' W J_d + Gam^-1)^-1 with the most recent
%   finite-difference Jacobian (the one at the current iterate if available,
%   else at the previous iterate, as PEST); mu = f(rows), C = J_r Sig J_r'.
%   No structural-error term. Observation noise is added by the caller.
    J = st.J; if isempty(J), J = st.Jlast; end
    Jd = J(st.rows, :);
    Hm = Jd' * (st.w .* Jd) + st.arm.Gi; Hm = 0.5 * (Hm + Hm');
    Sig = inv(Hm); Sig = 0.5 * (Sig + Sig');
    mu = st.f(rows); Jr = J(rows, :); C = Jr * Sig * Jr'; C = 0.5 * (C + C');
end
