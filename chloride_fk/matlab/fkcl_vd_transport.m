function c = fkcl_vd_transport(s, qx, qz, qs, dt, cold)
%FKCL_VD_TRANSPORT  Concentration for given fluxes: div(q c) - div(phi D grad c) = 0
%   (with dt and cold: one implicit Euler step of phi dc/dt + ...). Upwind advection; D diagonal,
%   D_xx = phi Dm + aL qx^2/|q| + aT qz^2/|q| on x-faces and the converse on z-faces.
%   Sea face: c = 1 on inflow, outflow carries the cell value; inland face: c = 0 inflow.
    N = s.N; a = s.a; b = s.b; u = s.u; d = s.d;
    Ax = s.dz(s.fx_j); Az = s.dx(s.fz_i)';
    if strcmpi(s.mode, 'henry')
        Dx = s.phi * s.Dm * ones(size(qx)); Dz = s.phi * s.Dm * ones(size(qz)); Dsea = s.phi * s.Dm * ones(size(qs));
    else
        qxc = (accumarray(a, qx, [N 1]) + accumarray(b, qx, [N 1])) ./ max(accumarray(a, 1, [N 1]) + accumarray(b, 1, [N 1]), 1);
        qzc = (accumarray(u, qz, [N 1]) + accumarray(d, qz, [N 1])) ./ max(accumarray(u, 1, [N 1]) + accumarray(d, 1, [N 1]), 1);
        qzx = 0.5 * (qzc(a) + qzc(b)); qxz = 0.5 * (qxc(u) + qxc(d));
        vx = sqrt(qx.^2 + qzx.^2) + 1e-30; vz = sqrt(qxz.^2 + qz.^2) + 1e-30;
        Dx = s.phi * s.Dm + s.aL * qx.^2 ./ vx + s.aT * qzx.^2 ./ vx;
        Dz = s.phi * s.Dm + s.aT * qxz.^2 ./ vz + s.aL * qz.^2 ./ vz;
        Dsea = s.phi * s.Dm + s.aL * abs(qs);
    end
    I = []; J = []; V = []; rhs = zeros(N, 1);
    % advection (upwind)
    for f = 1:2
        if f == 1, p = a; q = b; F = qx .* Ax; else, p = u; q = d; F = qz .* Az; end
        pos = F > 0; ng = ~pos;
        I = [I; p(pos); q(pos); q(ng); p(ng)]; %#ok<AGROW>
        J = [J; p(pos); p(pos); q(ng); q(ng)]; %#ok<AGROW>
        V = [V; F(pos); -F(pos); -F(ng); F(ng)]; %#ok<AGROW>
    end
    % dispersion
    tdx = Dx .* Ax ./ s.dxf; tdz = Dz .* Az ./ s.dzf;
    I = [I; a; b; a; b; u; d; u; d]; J = [J; a; b; b; a; u; d; d; u];
    V = [V; tdx; tdx; -tdx; -tdx; tdz; tdz; -tdz; -tdz];
    % sea face
    s0 = s.s0; Fs = qs .* s.dz(s.sea_j); in = Fs > 0;
    rhs = rhs + accumarray(s0(in), Fs(in), [N 1]);
    I = [I; s0(~in)]; J = [J; s0(~in)]; V = [V; -Fs(~in)];
    if strcmpi(s.mode, 'henry')
        td = Dsea .* s.dz(s.sea_j) / s.dx(1);
        I = [I; s0]; J = [J; s0]; V = [V; td]; rhs = rhs + accumarray(s0, td, [N 1]);
        e0 = s.e0; te = Dsea(1) * s.dz(s.in_j) / s.dx(end);
        I = [I; e0]; J = [J; e0]; V = [V; te];
    else
        td = Dsea .* s.dz(s.sea_j) / (0.5 * s.dx(1));
        I = [I; s0(in)]; J = [J; s0(in)]; V = [V; td(in)]; rhs = rhs + accumarray(s0(in), td(in), [N 1]);
    end
    if nargin >= 5 && ~isempty(dt)
        st = s.phi * s.vol / dt;
        I = [I; (1:N)']; J = [J; (1:N)']; V = [V; st]; rhs = rhs + st .* cold;
    end
    A = sparse(I, J, V, N, N);
    c = min(max(A \ rhs, 0), 1);
end
