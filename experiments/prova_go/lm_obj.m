function Phi = lm_obj(st, th, f)
%LM_OBJ  Regularised least-squares objective of LM_INIT.
    r = st.d - f(st.rows); dt = th - st.arm.th0;
    Phi = sum(st.w .* r.^2) + dt' * st.arm.Gi * dt;
end
