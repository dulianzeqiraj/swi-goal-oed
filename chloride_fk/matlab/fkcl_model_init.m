function m = fkcl_model_init(C, D)
%FKCL_MODEL_INIT  Plan grid, conductivity, cover, sea contact and facies prior of the chloride model.
%
%   m = FKCL_MODEL_INIT(C, D) builds the areal model of the coastal Fushe-Kuqe-Lezhe sector:
%     * the 0.25 km grid of src/fushe_kuqe_field_design.m on the 349 km2 polygon (same active-cell
%       order, same IDW conductivity, same 12 pilot zones and facies classes);
%     * the Adriatic contact: rows whose western edge lies within C.gapMax km of the GLOBE
%       shoreline (derived/shoreline_rows.csv) drain to the sea through a Robin link over the gap;
%       every other margin is no-flow (the southern half of the western edge is an inland margin);
%     * the aquifer-top depth from the 43 DRASTIC depth values (IDW, power 2);
%     * the distance of every cell to the shoreline (nearest polyline vertex);
%     * the facies-conditional prior covariance with the field correlation C.rhoF;
%     * the set of valid cells: connected to the sea, north of C.yCut.

    Bk = [(D.B(:, 1) - D.x0) (D.B(:, 2) - D.y0)] / 1000;
    W = D.wells;
    okK = isfinite(W.X) & isfinite(W.Y) & isfinite(W.K);
    Wk = [(W.X(okK) - D.x0) (W.Y(okK) - D.y0)] / 1000; Wk(:, 3) = W.K(okK);
    dx = C.dx;
    xs = 0:dx:max(Bk(:, 1)) + dx; ys = 0:dx:max(Bk(:, 2)) + dx;
    [GX, GY] = meshgrid(xs, ys); [ny, nx] = size(GX);
    inside = inpolygon(GX, GY, Bk(:, 1), Bk(:, 2));
    act = find(inside); [aj, ai] = ind2sub([ny, nx], act); Nc = numel(act);
    idx = zeros(ny, nx); idx(act) = 1:Nc;
    cx = xs(ai)'; cy = ys(aj)';
    % IDW conductivity (power 2), as in the companion model
    Kidw = zeros(Nc, 1);
    for k = 1:Nc
        d = hypot(Wk(:, 1) - cx(k), Wk(:, 2) - cy(k)) + 1e-6; w = 1 ./ d.^2;
        Kidw(k) = (w' * Wk(:, 3)) / sum(w);
    end
    % western and eastern edge of each row, shoreline, sea contact
    west = nan(ny, 1); east = nan(ny, 1);
    for j = 1:ny
        ii = find(inside(j, :));
        if ~isempty(ii), west(j) = xs(ii(1)); east(j) = xs(ii(end)); end
    end
    shore = D.shore(1:ny, 2);
    gap = west - shore;
    sea_row = isfinite(gap) & gap <= C.gapMax;
    gap_row = max(gap, 0);
    westc = false(Nc, 1);
    for j = 1:ny
        ii = find(inside(j, :), 1, 'first');
        if ~isempty(ii), westc(idx(j, ii)) = true; end
    end
    seac = westc & sea_row(aj);
    % distance to the shoreline (nearest vertex of the GLOBE polyline), in chunks
    P = D.coast(:, 2:3); dist = inf(Nc, 1);
    for s0 = 1:2000:Nc
        r = s0:min(s0 + 1999, Nc);
        d2 = (cx(r) - P(:, 1)').^2 + (cy(r) - P(:, 2)').^2;
        dist(r) = sqrt(min(d2, [], 2));
    end
    % cover = DRASTIC depth to the aquifer top, IDW power 2 over the 43 wells with a value
    okD = isfinite(W.depth);
    wx = (W.X(okD) - D.x0) / 1000; wy = (W.Y(okD) - D.y0) / 1000; wd = W.depth(okD);
    cover = zeros(Nc, 1);
    for k = 1:Nc
        d = hypot(wx - cx(k), wy - cy(k)) + 1e-6; w = 1 ./ d.^2;
        cover(k) = (w' * wd) / sum(w);
    end
    % faces (each interior face once: north and east neighbour)
    fI = zeros(2 * Nc, 1); fJ = fI; p = 0;
    for k = 1:Nc
        j = aj(k); i = ai(k);
        if j + 1 <= ny && inside(j + 1, i), p = p + 1; fI(p) = k; fJ(p) = idx(j + 1, i); end
        if i + 1 <= nx && inside(j, i + 1), p = p + 1; fI(p) = k; fJ(p) = idx(j, i + 1); end
    end
    fI = fI(1:p); fJ = fJ(1:p);
    % valid cells: connected to a sea cell, north of yCut, and connected again inside the sector
    lab = components(Nc, fI, fJ);
    valid = ismember(lab, unique(lab(seac))) & cy >= C.yCut;
    keep = valid(fI) & valid(fJ);
    lab = components(Nc, fI(keep), fJ(keep));
    valid = valid & ismember(lab, unique(lab(seac & valid)));
    keep = valid(fI) & valid(fJ);
    % pilot zones and facies prior (src/fushe_kuqe_field_design.m)
    [pgx, pgy] = meshgrid(linspace(1, max(xs) - 1, 5), linspace(2, max(ys) - 2, 8));
    pil = [pgx(:) pgy(:)]; pin = inpolygon(pil(:, 1), pil(:, 2), Bk(:, 1), Bk(:, 2)); pil = pil(pin, :);
    Nz = size(pil, 1); zone = zeros(Nc, 1);
    for k = 1:Nc, [~, zone(k)] = min(hypot(pil(:, 1) - cx(k), pil(:, 2) - cy(k))); end
    zK = arrayfun(@(z) mean(Kidw(zone == z)), (1:Nz)');
    zfac = 1 + (zK <= 150) + (zK <= 80);
    Gam = zeros(Nz);
    for a = 1:Nz
        for b = 1:Nz
            bs = exp(-hypot(pil(a, 1) - pil(b, 1), pil(a, 2) - pil(b, 2)) / 8.0);
            if zfac(a) == zfac(b), Gam(a, b) = bs; else, Gam(a, b) = C.rhoF * bs; end
        end
    end
    st = [0.30 0.45 0.60]; sg = st(zfac)'; Gam = (sg * sg') .* Gam + 1e-9 * eye(Nz);

    m.C = C; m.dx = dx; m.dxm = dx * 1000; m.area = (dx * 1000)^2;
    m.xs = xs; m.ys = ys; m.nx = nx; m.ny = ny; m.inside = inside; m.Bk = Bk; m.Wk = Wk;
    m.act = act; m.aj = aj; m.ai = ai; m.Nc = Nc; m.idx = idx; m.cx = cx; m.cy = cy;
    m.Kidw = Kidw; m.cover = cover; m.dist = dist;
    m.west = west; m.east = east; m.shore = shore; m.sea_row = sea_row; m.gap_row = gap_row;
    m.seac = seac; m.sea_idx = find(seac);
    m.sea_cond = m.dxm ./ (1000 * gap_row(aj(m.sea_idx)) + 0.5 * m.dxm);
    m.fI = fI(keep); m.fJ = fJ(keep); m.valid = valid;
    m.pil = pil; m.Nz = Nz; m.zone = zone; m.zK = zK; m.zfac = zfac; m.Gam = Gam; m.Lgam = chol(Gam, 'lower');
    m.x0 = D.x0; m.y0 = D.y0;
end

function lab = components(n, I, J)
% connected components of the undirected graph (I, J) on n nodes (breadth-first search)
    A = sparse([I; J], [J; I], 1, n, n);
    lab = zeros(n, 1); c = 0;
    for s = 1:n
        if lab(s), continue; end
        c = c + 1; lab(s) = c; front = s;
        while ~isempty(front)
            [nb, ~] = find(A(:, front));
            nb = unique(nb(lab(nb) == 0));
            lab(nb) = c; front = nb;
        end
    end
end
