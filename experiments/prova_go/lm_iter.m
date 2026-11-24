function st = lm_iter(M, S, st)
%LM_ITER  One Levenberg-Marquardt iteration (PEST-like): finite-difference
%   Jacobian at the current iterate (n runs, forward differences of step
%   S.fdStep in the log-multipliers; skipped when still valid after a rejected
%   step) and one trial run. Accepted when the objective decreases (lambda/4),
%   otherwise lambda*8. Converged when an accepted step changes the objective by
%   less than S.tolRel (relative), when lambda exceeds 1e6, or after S.maxIt
%   iterations. st.costLast = runs of this iteration; once converged a call is free.
    st.costLast = 0;
    if st.conv, return; end
    arm = st.arm; n = arm.n; c = 0;
    if isempty(st.J)
        J = zeros(numel(st.f), n);
        for i = 1:n
            tp = st.th; tp(i) = tp(i) + S.fdStep;
            J(:, i) = (arm_run(M, S, arm, tp) - st.f) / S.fdStep;
        end
        c = c + n; st.J = J;
    end
    Jd = st.J(st.rows, :); r = st.d - st.f(st.rows);
    Hm = Jd' * (st.w .* Jd) + arm.Gi; g = Jd' * (st.w .* r) - arm.Gi * (st.th - arm.th0);
    Hm = 0.5 * (Hm + Hm');
    dth = (Hm + st.lam * diag(diag(Hm))) \ g;
    tt = st.th + dth; ft = arm_run(M, S, arm, tt); c = c + 1;
    Pt = lm_obj(st, tt, ft);
    if Pt < st.Phi
        rel = (st.Phi - Pt) / st.Phi;
        st.Jlast = st.J; st.J = []; st.th = tt; st.f = ft; st.Phi = Pt; st.lam = max(st.lam / 4, 1e-7);
        if rel < S.tolRel, st.conv = true; end
    else
        st.lam = st.lam * 8; if st.lam > 1e6, st.conv = true; end
    end
    st.iter = st.iter + 1; if st.iter >= S.maxIt, st.conv = true; end
    st.runs = st.runs + c; st.costLast = c;
end
