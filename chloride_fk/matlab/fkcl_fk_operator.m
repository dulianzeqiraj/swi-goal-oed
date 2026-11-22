function A = fkcl_fk_operator(m, theta, b)
%FKCL_FK_OPERATOR  Flow operator of the companion design model on the geolocated sector.
%
%   A = FKCL_FK_OPERATOR(m, theta, b) assembles the confined-flow operator of the companion model
%   (src/fushe_kuqe_field_design.m: T = K_IDW exp(theta_zone) b, arithmetic face means) with the
%   geolocated sea boundary of the chloride study: the western-edge cells of the sea-contact rows
%   drain to h = 0 at the shoreline over the GLOBE gap, every other margin is no-flow, and cells
%   outside the coastal sector are identity rows. m is the struct of FKCL_MODEL_INIT. A is
%   positive definite on the sector: A h = rhs, with recharge entering rhs with a positive sign.
%   Used by FKCL_PRAG_MAR and FKCL_PRAG_GO (Python: experiments/prag_go_fushe_kuqe/fk_geo.py).

    n = m.Nc; T = m.Kidw .* exp(theta(m.zone)) * b;
    Tf = 0.5 * (T(m.fI) + T(m.fJ));
    dg = accumarray([m.fI; m.fJ], [Tf; Tf], [n 1]);
    dg(m.sea_idx) = dg(m.sea_idx) + T(m.sea_idx) .* m.sea_cond;
    dg(~m.valid) = 1;
    A = sparse([m.fI; m.fJ; (1:n)'], [m.fJ; m.fI; (1:n)'], [-Tf; -Tf; dg], n, n);
end
