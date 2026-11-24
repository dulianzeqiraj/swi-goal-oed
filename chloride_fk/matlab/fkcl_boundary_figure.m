function out = fkcl_boundary_figure(opts)
%FKCL_BOUNDARY_FIGURE  Fig. 9: the full-margin and the geolocated sea boundary of the design model.
%
%   out = FKCL_BOUNDARY_FIGURE() draws Fig. 9 of the paper to figures_matlab/fig9_boundary:
%     (a) the design model of the companion study (src/fushe_kuqe_field_design.m), in which every
%         row of the aquifer polygon drains to h = 0 at its westernmost cell;
%     (b) the same physics with the geolocated sea contact of Section 2.3 (FKCL_FK_OPERATOR), on the
%         coastal sector y >= 24 km.
%   Both panels show the zone intruded at the prior mean (h < h_c = 1 m), the supply wells of the
%   threshold-risk test (A23 and R16 with the full margin; A1 and P10 here) and the published MAR
%   sites. Panel (b) also shows the zone that is intruded only when A1 and P10 are pumped at the
%   rates of FKCL_PRAG_MAR, read from experiments/prag_go_fushe_kuqe/res_geo/mar_geo.json or given
%   as opts.QA and opts.QB [m3/day].
%
%   out.area = intruded area [km2]: full margin; geolocated without and with pumping (the smoothed
%   indicator of the companion code, as in the text: 92.7, 10.1 and 11.6 km2).
%   Options (struct): QA, QB; figure true | false; tsvdir (GNU Octave). Run time: a few seconds.
%   Python: experiments/prag_go_fushe_kuqe/fk_geo_figs.py.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1, opts = struct(); end
    if ~isfield(opts, 'figure'), opts.figure = true; end
    C = fkcl_config();
    if isfield(opts, 'tsvdir'), C.tsvdir = opts.tsvdir; end
    C.rhoF = 0.6;                                       % base prior of the companion model
    D = fkcl_read_data(C); m = fkcl_model_init(C, D);
    b = 30; R = 5e-4; hc = 1.0; n = m.Nc;
    goalA = @(h, v) sum(m.area ./ (1 + exp(-(hc - h(v)) / 0.15))) / 1e6;

    % ------------------------------------------------ (a) full margin: src/fushe_kuqe_field_design.m
    west = false(m.ny, m.nx);
    for j = 1:m.ny
        i = find(m.inside(j, :), 1);
        if ~isempty(i), west(j, i) = true; end
    end
    cst = west(sub2ind([m.ny m.nx], m.aj, m.ai));
    [fI, fJ] = faces(m);
    T = m.Kidw * b; Tf = 0.5 * (T(fI) + T(fJ));
    dg = accumarray([fI; fJ], [Tf; Tf], [n 1]);
    I = [fI; fJ; (1:n)']; J = [fJ; fI; (1:n)']; V = [-Tf; -Tf; dg];
    keep = ~cst(I);                                     % coast rows: h = 0
    c0 = find(cst);
    Af = sparse([I(keep); c0], [J(keep); c0], [V(keep); ones(numel(c0), 1)], n, n);
    rf = R * m.area * double(~cst);
    hF = Af \ rf;

    % ------------------------------------------------ (b) geolocated boundary, without and with pumping
    A0 = fkcl_fk_operator(m, zeros(m.Nz, 1), b);
    rhs0 = R * m.area * double(m.valid);
    h0 = A0 \ rhs0;
    ref = fullfile(C.repo, 'experiments', 'prag_go_fushe_kuqe', 'res_geo', 'mar_geo.json');
    sup = {'A1', 'P10'};
    if exist(ref, 'file')
        Jr = jsondecode(fileread(ref)); sup = {Jr.supply.A.id, Jr.supply.B.id};
        if ~isfield(opts, 'QA'), opts.QA = Jr.pumping.QA; end
        if ~isfield(opts, 'QB'), opts.QB = Jr.pumping.QB; end
    end
    if ~isfield(opts, 'QA') || ~isfield(opts, 'QB')
        error('fkcl_boundary_figure:pumping', 'Run fkcl_prag_mar first or give opts.QA and opts.QB.');
    end
    W = D.wells; okK = isfinite(W.X) & isfinite(W.Y) & isfinite(W.K); ids = W.id(okK);
    cellOf = @(x, y) m.idx(round(y / m.dx) + 1, round(x / m.dx) + 1);
    wxy = @(w) m.Wk(find(strcmp(ids, w), 1), 1:2);
    pA = wxy(sup{1}); pB = wxy(sup{2}); cA = cellOf(pA(1), pA(2)); cB = cellOf(pB(1), pB(2));
    rhsP = rhs0; rhsP(cA) = rhsP(cA) - opts.QA; rhsP(cB) = rhsP(cB) - opts.QB;
    hP = A0 \ rhsP;

    out = struct('area', [goalA(hF, true(n, 1)) goalA(h0, m.valid) goalA(hP, m.valid)], ...
                 'supply', {sup}, 'QA', opts.QA, 'QB', opts.QB);
    fprintf('intruded area: full margin %.1f km2; geolocated %.1f km2, %.1f km2 with %s and %s pumped\n', ...
            out.area(1), out.area(2), out.area(3), sup{1}, sup{2});
    if ~opts.figure, return; end

    % ------------------------------------------------ figure
    pub = [12.25 12.75; 11.25 18.75; 6.5 51.0]; pubID = {'A18', 'P21', 'P16'};   % published MAR cells
    pubC = arrayfun(@(k) cellOf(pub(k, 1), pub(k, 2)), 1:3);
    old = [wxy('A23'); wxy('R16')];
    col = struct('land', [238 243 234] / 255, 'out', [228 228 228] / 255, 'salt', [0 114 178] / 255, ...
                 'pump', [156 203 234] / 255, 'sea', [213 94 0] / 255, 'well', [230 159 0] / 255);
    cmap = [1 1 1; col.land; col.pump; col.salt; col.out];        % 0 outside the polygon, 1-4 classes
    f = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 13 15.5], 'Color', 'w');
    set(f, 'PaperUnits', 'centimeters', 'PaperSize', [13 15.5], 'PaperPosition', [0 0 13 15.5]);
    set(f, 'DefaultAxesFontSize', 7, 'DefaultTextFontSize', 7, 'DefaultAxesLineWidth', 0.6);
    cls = {1 + 2 * (hF < hc), 1 + 2 * (h0 < hc) + (h0 >= hc & hP < hc)};
    cls{2}(~m.valid) = 4;
    ttl = {'a  Full western margin as sea', 'b  Geolocated Adriatic contact, 23 km'};
    note = {{'intruded area', sprintf('%.1f km^2, no pumping', out.area(1))}, ...
            {sprintf('intruded area %.1f km^2,', out.area(2)), sprintf('%.1f km^2 with %s and %s', out.area(3), sup{1}, sup{2}), 'pumped'}};
    xe = [m.xs - m.dx / 2, m.xs(end) + m.dx / 2]; ye = [m.ys - m.dx / 2, m.ys(end) + m.dx / 2];
    for p = 1:2
        ax = axes(f, 'Position', [0.09 + (p - 1) * 0.46, 0.22, 0.42, 0.7]); hold(ax, 'on');
        G = zeros(m.ny + 1, m.nx + 1); G(sub2ind([m.ny + 1, m.nx + 1], m.aj, m.ai)) = cls{p};
        hp = pcolor(ax, xe, ye, G); set(hp, 'EdgeColor', 'none'); colormap(ax, cmap); caxis(ax, [-0.5 4.5]);
        plot(ax, m.Bk(:, 1), m.Bk(:, 2), '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 0.5);
        if p == 1, sc = find(cst); else, sc = m.sea_idx(:); end
        [~, o] = sort(m.cy(sc)); plot(ax, m.cx(sc(o)) - m.dx / 2, m.cy(sc(o)), '-', 'Color', col.sea, 'LineWidth', 1.6);
        if p == 1
            wv = old; wl = {'A23', 'R16'}; dxl = [0.7 -0.7]; ha = {'left', 'right'};
        else
            wv = [pA; pB]; wl = sup; dxl = [0.7 0.9]; ha = {'left', 'left'};
            plot(ax, [-2.5 17], [C.yCut C.yCut], ':', 'Color', [0.35 0.35 0.35], 'LineWidth', 0.6);
            text(ax, -2.2, C.yCut - 0.9, 'sector limit', 'FontSize', 6, 'Color', [0.25 0.25 0.25]);
            text(ax, -2.2, C.yCut - 2.6, sprintf('y = %g km', C.yCut), 'FontSize', 6, 'Color', [0.25 0.25 0.25]);
        end
        plot(ax, wv(:, 1), wv(:, 2), 'kv', 'MarkerFaceColor', col.well, 'MarkerSize', 6);
        for k = 1:2
            text(ax, wv(k, 1) + dxl(k), wv(k, 2) + 0.5 - 1.3 * (k == 2 && p == 2), wl{k}, 'FontSize', 6.5, 'HorizontalAlignment', ha{k});
        end
        for k = 1:3
            inS = p == 1 || m.valid(pubC(k));
            ec = [0 0 0] * inS + [0.45 0.45 0.45] * ~inS;
            plot(ax, pub(k, 1), pub(k, 2), 'd', 'MarkerEdgeColor', ec, 'MarkerFaceColor', 'w', 'MarkerSize', 5, 'LineWidth', 1);
            text(ax, pub(k, 1) + 0.6, pub(k, 2) - 1.0, pubID{k}, 'FontSize', 6, 'Color', ec);
            if ~inS, text(ax, pub(k, 1) + 0.6, pub(k, 2) - 2.6, '(no sea contact)', 'FontSize', 6, 'Color', ec); end
        end
        for k = 1:numel(note{p}), text(ax, -2.0, 7.6 - 1.8 * (k - 1), note{p}{k}, 'FontSize', 6.5); end
        axis(ax, 'equal'); xlim(ax, [-2.5 17]); ylim(ax, [-1.5 54.5]); box(ax, 'off');
        title(ax, ttl{p}, 'FontWeight', 'normal', 'FontSize', 7.5);
        xlabel(ax, 'Easting from x_0 [km]');
        if p == 1, ylabel(ax, 'Northing from y_0 [km]'); else, set(ax, 'YTickLabel', []); end
    end
    % legend drawn by hand: two columns in MATLAB and in GNU Octave
    ax = axes(f, 'Position', [0.06 0.02 0.9 0.1], 'Visible', 'off'); hold(ax, 'on'); xlim(ax, [0 1]); ylim(ax, [0 1]);
    lab = {'intruded at the prior mean (h < 1 m)', 'intruded only with the supply wells pumped', ...
           'outside the model sector (b)', 'sea boundary of the model', 'supply wells', 'published MAR sites'};
    for k = 1:6
        x0 = 0.02 + 0.52 * (k > 3); y0 = 0.85 - 0.35 * mod(k - 1, 3);
        switch k
            case {1, 2, 3}
                fc = {col.salt, col.pump, col.out};
                plot(ax, x0, y0, 's', 'MarkerFaceColor', fc{k}, 'MarkerEdgeColor', 'none', 'MarkerSize', 8);
            case 4, plot(ax, x0 + [-0.015 0.015], [y0 y0], '-', 'Color', col.sea, 'LineWidth', 1.6);
            case 5, plot(ax, x0, y0, 'kv', 'MarkerFaceColor', col.well, 'MarkerSize', 6);
            case 6, plot(ax, x0, y0, 'kd', 'MarkerFaceColor', 'w', 'MarkerSize', 5);
        end
        text(ax, x0 + 0.035, y0, lab{k}, 'FontSize', 6.5, 'VerticalAlignment', 'middle');
    end
    if ~exist(C.figdir, 'dir'), mkdir(C.figdir); end
    fkcl_save_figure(f, C.figdir, 'fig9_boundary'); close(f);
end

function [fI, fJ] = faces(m)
    % each interior face of the polygon once (north and east neighbour), as in FKCL_MODEL_INIT
    fI = zeros(2 * m.Nc, 1); fJ = fI; p = 0;
    for k = 1:m.Nc
        j = m.aj(k); i = m.ai(k);
        if j + 1 <= m.ny && m.inside(j + 1, i), p = p + 1; fI(p) = k; fJ(p) = m.idx(j + 1, i); end
        if i + 1 <= m.nx && m.inside(j, i + 1), p = p + 1; fI(p) = k; fJ(p) = m.idx(j, i + 1); end
    end
    fI = fI(1:p); fJ = fJ(1:p);
end
