function s = fkcl_vd_init(xe, ze, top, bot, Kx, opt)
%FKCL_VD_INIT  Masked grid of a steady variable-density section (equivalent-freshwater-head form).
%
%   s = FKCL_VD_INIT(xe, ze, top, bot, Kx, opt)
%     xe, ze    cell edges [m]; x = distance from the sea, z = depth below sea level (positive down)
%     top, bot  aquifer top and base depth per column [m]; cells between them are active
%     Kx        horizontal conductivity per column [m/d]
%     opt       struct: aniso (Kz/Kx), eps (density ratio), phi (porosity), Dm [m2/d],
%               aL, aT (dispersivities [m]), Qin (freshwater inflow at x = L [m2/d]),
%               mode 'field' or 'henry'
%   Discretization of src/vd_residual.m (cell-centred finite volumes, harmonic face K, upwind),
%   on a masked grid with anisotropy and velocity-dependent dispersion (diagonal tensor).

    s.xe = xe(:)'; s.ze = ze(:);
    s.xc = 0.5 * (s.xe(1:end - 1) + s.xe(2:end)); s.zc = 0.5 * (s.ze(1:end - 1) + s.ze(2:end));
    s.dx = diff(s.xe); s.dz = diff(s.ze);
    nx = numel(s.xc); nz = numel(s.zc); s.nx = nx; s.nz = nz;
    s.act = (s.zc >= top(:)') & (s.zc <= bot(:)');
    s.Kx = repmat(Kx(:)', nz, 1); s.Kz = s.Kx * opt.aniso;
    s.eps = opt.eps; s.phi = opt.phi; s.Dm = opt.Dm; s.aL = opt.aL; s.aT = opt.aT; s.Qin = opt.Qin;
    s.mode = opt.mode;
    s.idx = zeros(nz, nx); s.idx(s.act) = 1:nnz(s.act); s.N = nnz(s.act);
    [s.jj, s.ii] = find(s.act);
    % note: find returns column-major order, which is the order of idx above
    mx = s.act(:, 1:end - 1) & s.act(:, 2:end); [s.fx_j, s.fx_i] = find(mx);
    mz = s.act(1:end - 1, :) & s.act(2:end, :); [s.fz_j, s.fz_i] = find(mz);
    hm = @(a, b) 2 * a .* b ./ (a + b);
    s.Kfx = hm(s.Kx(sub2ind([nz nx], s.fx_j, s.fx_i)), s.Kx(sub2ind([nz nx], s.fx_j, s.fx_i + 1)));
    s.Kfz = hm(s.Kz(sub2ind([nz nx], s.fz_j, s.fz_i)), s.Kz(sub2ind([nz nx], s.fz_j + 1, s.fz_i)));
    s.dxf = 0.5 * (s.dx(s.fx_i) + s.dx(s.fx_i + 1))';
    s.dzf = 0.5 * (s.dz(s.fz_j) + s.dz(s.fz_j + 1));
    s.a = s.idx(sub2ind([nz nx], s.fx_j, s.fx_i)); s.b = s.idx(sub2ind([nz nx], s.fx_j, s.fx_i + 1));
    s.u = s.idx(sub2ind([nz nx], s.fz_j, s.fz_i)); s.d = s.idx(sub2ind([nz nx], s.fz_j + 1, s.fz_i));
    s.sea_j = find(s.act(:, 1)); s.hsea = s.eps * s.zc(s.sea_j); s.s0 = s.idx(s.sea_j, 1);
    s.in_j = find(s.act(:, end)); s.e0 = s.idx(s.in_j, end);
    sh = s.Kx(s.in_j, end) .* s.dz(s.in_j);
    s.qin = s.Qin * sh / sum(sh) ./ s.dz(s.in_j);
    s.vol = (s.dx(s.ii))' .* s.dz(s.jj);
end
