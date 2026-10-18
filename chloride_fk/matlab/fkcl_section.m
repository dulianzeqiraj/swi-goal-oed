function R = fkcl_section(m, p, opt)
%FKCL_SECTION  Variable-density chloride section A-A' (y = m.C.ySec km) for one parameter set.
%
%   R = FKCL_SECTION(m, p, opt) takes the areal model's geometry (aquifer top from the DRASTIC depth,
%   thickness from the shoreline distance), its horizontal conductivity and its freshwater discharge
%   to the sea on the rows within 1 km of the section, and solves the steady variable-density problem
%   from the shoreline to the inland margin. opt fields (defaults): dxs 100 m, dzs 5 m, aT 1 m,
%   aL max(10, 10 aT) m. Returns the solved section R.s, the inflow R.Qin [m2/d], the variable-density
%   toe R.toe_vd [m from the shoreline], the Strack toe of the same member R.toe_strack, the simulated
%   mixing-zone half-width R.w_sim (half the 16-84 % concentration distance) and the plotting arrays.

    C = m.C;
    if nargin < 3, opt = struct(); end
    if ~isfield(opt, 'dxs'), opt.dxs = 100; end
    if ~isfield(opt, 'dzs'), opt.dzs = 5; end
    if ~isfield(opt, 'aT'), opt.aT = C.secAT; end
    if ~isfield(opt, 'aL'), opt.aL = max(C.secAL, 10 * opt.aT); end
    o = fkcl_model_run(m, p);
    K = p.eta * m.Kidw .* exp(p.theta(m.zone));
    j = round(C.ySec / m.dx) + 1;
    rows = m.sea_idx(abs(m.cy(m.sea_idx) - C.ySec) <= 1.0);
    [~, loc] = ismember(rows, m.sea_idx);
    qsea = K(rows) .* m.sea_cond(loc) .* o.phi(rows);
    Qin = sum(qsea) / (numel(rows) * m.dxm);
    shore = m.shore(j);
    cells = find(m.valid & m.aj == j);
    [~, o2] = sort(m.cx(cells)); cells = cells(o2);
    xe_km = m.cx(cells(end)) + 0.5 * m.dx;
    L = (xe_km - shore) * 1000;
    nx = round(L / opt.dxs); xe = linspace(0, L, nx + 1);
    xc_km = shore + 0.5 * (xe(1:end - 1) + xe(2:end)) / 1000;
    pos = zeros(1, nx);
    for i = 1:nx
        k = find(m.cx(cells) - 0.5 * m.dx <= xc_km(i), 1, 'last');   % nearest areal cell; gap -> western edge
        if isempty(k), k = 1; end
        pos(i) = cells(k);
    end
    top = o.d(pos)'; bot = o.d(pos)' + o.B(pos)';
    zmax = ceil(max(bot) / opt.dzs) * opt.dzs; ze = 0:opt.dzs:zmax;
    so = struct('aniso', C.secAniso, 'eps', C.delta, 'phi', C.secPhi, 'Dm', C.secDm, 'aL', opt.aL, 'aT', opt.aT, ...
                'Qin', Qin, 'mode', 'field');
    s = fkcl_vd_init(xe, ze, top, bot, K(pos)', so);
    c0 = 0.5 * (1 + erf((s.zc(s.jj) - o.zeta(pos(s.ii))) / (p.w * sqrt(2))));
    s = fkcl_vd_solve(s, c0);
    wedge = o.wedge(cells);
    if any(wedge), toe_s = (max(m.cx(cells(wedge))) + 0.5 * m.dx - shore) * 1000; else, toe_s = 0; end
    Cf = fkcl_vd_field(s, s.c); wid = [];
    for i = 1:s.nx
        col = Cf(:, i); ok = isfinite(col);
        if nnz(ok) < 5, continue; end
        z = s.zc(ok); cc = col(ok);
        if min(cc) < 0.16 && max(cc) > 0.84 && all(diff(cc) >= -1e-6)
            [cu, iu] = unique(cc); zu = z(iu);
            wid(end + 1) = 0.5 * (interp1(cu, zu, 0.84) - interp1(cu, zu, 0.16)); %#ok<AGROW>
        end
    end
    R.s = s; R.Qin = Qin; R.L = L; R.toe_vd = fkcl_vd_toe(s, 0.5); R.toe_strack = toe_s;
    if isempty(wid), R.w_sim = NaN; else, R.w_sim = median(wid); end
    R.xc_km = xc_km; R.top = top; R.bot = bot; R.zeta = o.zeta(pos)'; R.Cl_s = p.Cl_s; R.w = p.w;
    R.Cl = C.Cl_f + fkcl_vd_field(s, s.c) * (p.Cl_s - C.Cl_f);
end
