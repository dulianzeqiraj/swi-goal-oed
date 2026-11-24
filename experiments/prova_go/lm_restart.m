function st = lm_restart(S, st, rows, d, sig)
%LM_RESTART  Continue an LM calibration from its current iterate on new data.
%   st = LM_RESTART(S, st, rows, d, sig) keeps the iterate, its outputs and its
%   Jacobian (they cover every output, so no new run is needed), replaces the
%   data (ROWS, values D, noise sd SIG), recomputes the objective and restarts
%   the iteration counter and lambda. Used to condition an arm on all data.
    st.rows = rows(:); st.d = d(:); st.w = 1 ./ sig(:).^2;
    st.Phi = lm_obj(st, st.th, st.f); st.lam = S.lam0; st.iter = 0; st.conv = false; st.runs = 0;
    if isempty(st.J) && ~isempty(st.Jlast), st.J = []; end
end
