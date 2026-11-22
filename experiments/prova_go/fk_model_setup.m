function M = fk_model_setup(xlsxfile, opts)
%FK_MODEL_SETUP  The Fushe-Kuqe model of the builder plus everything PROVA-GO needs.
%   M = FK_MODEL_SETUP(xlsxfile) calls src/fushe_kuqe_field_design.m unchanged
%   (grid dx = 0.25 km, IDW log-K K0c, coast = first active cell of each row,
%   R = 5e-4 m/d, b = 30 m, pilot zones, facies prior GamF) and adds:
%     - face lists for the vectorised assembly FK_ASSEMBLE / solver FK_SOLVE;
%     - distance of every cell to the coast and the 1.5 km coastal strip;
%     - the supply wells A and B and J observation wells (snapped to cells with
%       the builder's rule round(Wk/dx)+1), chosen by the rules documented below;
%     - the Gauss-Krueger offsets x0, y0 of the local km frame.
%   Supply wells: for each supply well of the published PRAG-MAR demo (A23 north,
%   R16 south of N = 25 km) the nearest inside well at least opts.supDist km from
%   the coast whose baseline head is at least opts.supHead m (A23 and R16
%   themselves have baseline heads below h_c = 1 m, so no extraction rate can give
%   an intrusion probability near 1/2). Observation wells: farthest-point sample
%   of opts.J wells of the full well list (sheet 2_All_Wells) with a non-coastal
%   active cell, at least 0.5 km from A and B.
    if nargin < 2, opts = struct(); end
    def = struct('J', 25, 'supDist', 3.0, 'supHead', 2.0, 'stripKm', 1.5, 'demoSup', {{'A23', 'R16'}});
    fn = fieldnames(def); for q = 1:numel(fn), if ~isfield(opts, fn{q}), opts.(fn{q}) = def.(fn{q}); end, end
    R = fushe_kuqe_field_design(xlsxfile, struct());
    M = struct();
    keep = {'P', 'dx', 'xs', 'ys', 'ny', 'nx', 'inside', 'act', 'ai', 'aj', 'Nc', 'idx', 'coast', 'Bk', 'Wk', ...
            'K0c', 'dxm', 'area', 'h0', 'hcrit', 'zK', 'zfac', 'pil', 'zone', 'GamF', 'monCell', 'marCell', 'baseArea'};
    for q = 1:numel(keep), M.(keep{q}) = R.(keep{q}); end
    M.wellIDK = cellstr(R.wellID); M.monID = cellstr(R.monID); M.marID = cellstr(R.marID);
    M.b = R.P.b; M.R0 = R.P.R; M.Nz = size(R.pil, 1); M.operator = R.operator;
    % Gauss-Krueger offsets (as in the builder)
    Braw = readmatrix(xlsxfile, 'Sheet', '3_Boundary_Coords'); B = Braw(:, 2:3); B = B(all(isfinite(B), 2), :);
    M.x0 = min(B(:, 1)); M.y0 = min(B(:, 2));
    % ---- links (directed, builder order) and faces (undirected) ------------
    Nc = M.Nc; cst = M.coast(M.act); M.isCoast = cst;
    nb = [-1 0; 1 0; 0 -1; 0 1]; fk = []; fl = [];
    for q = 1:4
        jj = M.aj + nb(q, 1); ii = M.ai + nb(q, 2);
        ok = jj >= 1 & jj <= M.ny & ii >= 1 & ii <= M.nx;
        l = zeros(Nc, 1); l(ok) = M.idx(sub2ind([M.ny M.nx], jj(ok), ii(ok)));
        ok = ok & l > 0; ok(ok) = M.inside(sub2ind([M.ny M.nx], jj(ok), ii(ok)));
        fk = [fk; find(ok)]; fl = [fl; l(ok)]; %#ok<AGROW>
    end
    M.ncst = find(~cst); M.cst = find(cst);
    pos = zeros(Nc, 1); pos(M.ncst) = 1:numel(M.ncst);
    sel = ~cst(fk); [~, o] = sortrows([fk(sel) (1:nnz(sel))']); ff = fk(sel); gg = fl(sel);
    M.fk = ff(o); M.fl = gg(o); M.fk_row = pos(M.fk);   % rows k (non-coastal) in increasing order
    u = fk < fl; M.ek = fk(u); M.el = fl(u);          % each undirected face once
    M.ni = M.ncst; M.pi = pos; M.e_int = ~cst(M.ek) & ~cst(M.el);
    % ---- coast distance and strip --------------------------------------------
    cx = M.xs(M.ai(M.cst)); cy = M.ys(M.aj(M.cst)); X = M.xs(M.ai(:)); Y = M.ys(M.aj(:));
    dc = zeros(Nc, 1); for k = 1:Nc, dc(k) = min(hypot(cx - X(k), cy - Y(k))); end
    M.X = X(:); M.Y = Y(:); M.dcoast = dc; M.strip = dc <= opts.stripKm + 1e-9; M.stripKm = opts.stripKm;
    % ---- full well list ---------------------------------------------------------
    T = readtable(xlsxfile, 'Sheet', '2_All_Wells');
    ids = cellstr(T{:, 1}); wx = (T{:, 2} - M.x0) / 1000; wy = (T{:, 3} - M.y0) / 1000;
    jj = round(wy / M.dx) + 1; ii = round(wx / M.dx) + 1; cell = zeros(numel(ids), 1);
    ok = isfinite(wx) & isfinite(wy) & jj >= 1 & jj <= M.ny & ii >= 1 & ii <= M.nx;
    cell(ok) = M.idx(sub2ind([M.ny M.nx], jj(ok), ii(ok)));
    M.allID = ids; M.allXY = [wx wy]; M.allCell = cell;
    M.allK = T{:, 4};
    % ---- supply wells -------------------------------------------------------------
    cand = find(cell > 0); cand = cand(~cst(cell(cand)) & dc(cell(cand)) >= opts.supDist & M.h0(cell(cand)) >= opts.supHead);
    sup = zeros(1, 2);
    for q = 1:2
        w0 = find(strcmp(ids, opts.demoSup{q}), 1);
        [~, i] = min(hypot(wx(cand) - wx(w0), wy(cand) - wy(w0))); sup(q) = cand(i);
    end
    M.supW = sup; M.supID = ids(sup)'; M.cellA = cell(sup(1)); M.cellB = cell(sup(2)); M.supCell = [M.cellA M.cellB];
    % ---- observation wells (farthest-point sample) -------------------------------
    cand = find(cell > 0 & ~ismember((1:numel(ids))', sup));
    cand = cand(~cst(cell(cand)));
    [~, u1] = unique(cell(cand), 'first'); cand = cand(sort(u1));
    dAB = min(hypot(wx(cand) - wx(sup(1)), wy(cand) - wy(sup(1))), hypot(wx(cand) - wx(sup(2)), wy(cand) - wy(sup(2))));
    cand = cand(dAB >= 0.5);
    P = [M.xs(M.ai(cell(cand)))' M.ys(M.aj(cell(cand)))'];
    [~, s] = min(hypot(P(:, 1) - mean(P(:, 1)), P(:, 2) - mean(P(:, 2)))); pick = s;
    dmin = hypot(P(:, 1) - P(s, 1), P(:, 2) - P(s, 2));
    while numel(pick) < opts.J
        [~, s] = max(dmin); pick(end + 1) = s; %#ok<AGROW>
        dmin = min(dmin, hypot(P(:, 1) - P(s, 1), P(:, 2) - P(s, 2)));
    end
    pick = sort(pick);
    M.obsW = cand(pick)'; M.obsID = ids(M.obsW)'; M.obsCell = cell(M.obsW)'; M.J = opts.J;
    M.demoSup = opts.demoSup; M.demoSupCell = cellfun(@(s) cell(find(strcmp(ids, s), 1)), opts.demoSup);
end
