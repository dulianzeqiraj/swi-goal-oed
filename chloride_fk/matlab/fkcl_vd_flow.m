function [h, qx, qz, qs] = fkcl_vd_flow(s, c)
%FKCL_VD_FLOW  Equivalent freshwater head for a given concentration, and the face fluxes [m/d].
%   div[K (grad h + eps c e_z)] = 0; qx > 0 toward +x (inland), qz > 0 downward, qs > 0 = seawater
%   entering through the sea face.
    N = s.N;
    tx = s.Kfx .* s.dz(s.fx_j) ./ s.dxf;
    tz = s.Kfz .* s.dx(s.fz_i)' ./ s.dzf;
    cf = 0.5 * (c(s.u) + c(s.d));
    g = s.Kfz * s.eps .* cf .* s.dx(s.fz_i)';
    rhs = accumarray(s.u, -g, [N 1]) + accumarray(s.d, g, [N 1]);
    ts = s.Kx(s.sea_j, 1) .* s.dz(s.sea_j) / (0.5 * s.dx(1));
    rhs = rhs + accumarray(s.s0, ts .* s.hsea, [N 1]) + accumarray(s.e0, s.qin .* s.dz(s.in_j), [N 1]);
    I = [s.a; s.b; s.a; s.b; s.u; s.d; s.u; s.d; s.s0];
    J = [s.a; s.b; s.b; s.a; s.u; s.d; s.d; s.u; s.s0];
    V = [tx; tx; -tx; -tx; tz; tz; -tz; -tz; ts];
    A = sparse(I, J, V, N, N);
    h = A \ rhs;
    qx = -s.Kfx .* (h(s.b) - h(s.a)) ./ s.dxf;
    qz = -s.Kfz .* (h(s.d) - h(s.u)) ./ s.dzf + s.Kfz * s.eps .* cf;
    qs = -s.Kx(s.sea_j, 1) .* (h(s.s0) - s.hsea) / (0.5 * s.dx(1));
end
