function st = lm_init(M, S, arm, th, rows, d, sig)
%LM_INIT  Start a Levenberg-Marquardt (Gauss-Newton) MAP calibration of one arm.
%   st = LM_INIT(M, S, arm, th, rows, d, sig) evaluates the arm at th (1 run)
%   for the data d (values of outputs ROWS, noise sd SIG). The objective is
%       Phi(th) = sum(((d - f(rows))./sig).^2) + (th - th0)' Gam^-1 (th - th0)
%   (the prior acts as Tikhonov regularisation). See LM_ITER, LM_PREDICT.
    st.arm = arm; st.rows = rows(:); st.d = d(:); st.w = 1 ./ sig(:).^2;
    st.th = th(:); st.f = arm_run(M, S, arm, st.th); st.runs = 1;
    st.Phi = lm_obj(st, st.th, st.f); st.J = []; st.Jlast = []; st.lam = S.lam0;
    st.iter = 0; st.conv = false; st.costLast = 1;
end
