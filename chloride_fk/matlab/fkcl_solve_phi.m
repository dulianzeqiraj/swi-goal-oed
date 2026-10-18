function phi = fkcl_solve_phi(m, K, R)
%FKCL_SOLVE_PHI  Strack potential [m^2] on the valid cells: div(K grad phi) + R = 0.
%   Face conductivity is the arithmetic mean of the two cells (as in the companion model);
%   the western-edge cells of sea-contact rows drain to phi = 0 at the shoreline over the gap.
    n = m.Nc;
    Kf = 0.5 * (K(m.fI) + K(m.fJ));
    dg = accumarray([m.fI; m.fJ], [Kf; Kf], [n 1]);
    dg(m.sea_idx) = dg(m.sea_idx) + K(m.sea_idx) .* m.sea_cond;
    dg(~m.valid) = 1;
    A = sparse([m.fI; m.fJ; (1:n)'], [m.fJ; m.fI; (1:n)'], [-Kf; -Kf; dg], n, n);
    rhs = R * m.area * double(m.valid);
    phi = A \ rhs;
end
