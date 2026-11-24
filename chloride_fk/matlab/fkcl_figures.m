function fkcl_figures(R, which)
%FKCL_FIGURES  The eight figures of the chloride manuscript, drawn from the MATLAB results.
%
%   FKCL_FIGURES(R) draws every figure; FKCL_FIGURES(R, [2 5 7]) draws a subset. R is the struct
%   returned by FKCL_RUN_ALL (fields C, D, m, H, Cal, Post, Des, Sec). Figures go to R.C.figdir as
%   PNG (600 dpi) and PDF. Only base-MATLAB graphics are used (pcolor, contour, patch, bar, legend),
%   so the same code runs in GNU Octave.
%     1 framework   2 site and data   3 hydrochemistry   4 calibration   5 chloride maps
%     6 variable-density section      7 sampling design  8 decision modules

    if nargin < 2, which = 1:8; end
    set(0, 'DefaultAxesFontSize', 8, 'DefaultTextFontSize', 8, 'DefaultAxesLineWidth', 0.6);
    for k = which
        switch k
            case 1, f = fig1(); case 2, f = fig2(R); case 3, f = fig3(R); case 4, f = fig4(R);
            case 5, f = fig5(R); case 6, f = fig6(R); case 7, f = fig7(R); case 8, f = fig8(R);
        end
        names = {'fig1_framework', 'fig2_site', 'fig3_hydrochem', 'fig4_calib', 'fig5_maps', ...
                 'fig6_section', 'fig7_design', 'fig8_toolkit'};
        fkcl_save_figure(f, R.C.figdir, names{k});
        close(f);
    end
end

% ======================================================================= helpers
function c = oi(k)
    P = [0 114 178; 213 94 0; 0 158 115; 204 121 167; 230 159 0; 86 180 233; 240 228 66; 0 0 0] / 255;
    c = P(k, :);
end

function f = newfig(wmm, hmm)
    f = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 wmm / 10 hmm / 10], 'Color', 'w');
    set(f, 'PaperUnits', 'centimeters', 'PaperSize', [wmm hmm] / 10, 'PaperPosition', [0 0 wmm hmm] / 10);
end

function letter(ax, s)
    text(ax, -0.02, 1.02, s, 'Units', 'normalized', 'FontWeight', 'bold', 'FontSize', 9, ...
         'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
end

function G = gridof(m, v, mask)
% cell values on the plan grid, padded for PCOLOR with flat shading (one face per cell)
    if nargin < 3, mask = true(m.Nc, 1); end
    v = double(v(:)); v(~mask) = NaN;
    G = nan(m.ny + 1, m.nx + 1);
    G(sub2ind([m.ny + 1, m.nx + 1], m.aj, m.ai)) = v;
end

function [xe, ye] = edges(m)
    xe = [m.xs - m.dx / 2, m.xs(end) + m.dx / 2]; ye = [m.ys - m.dx / 2, m.ys(end) + m.dx / 2];
end

function h = mapfield(ax, m, v, mask, cm, lim)
    [xe, ye] = edges(m);
    h = pcolor(ax, xe, ye, gridof(m, v, mask)); set(h, 'EdgeColor', 'none');
    colormap(ax, cm); caxis(ax, lim);
end

function outline(ax, R)
    m = R.m; D = R.D;
    plot(ax, m.Bk(:, 1), m.Bk(:, 2), '-', 'Color', [0.15 0.15 0.15], 'LineWidth', 0.7);
    seg = D.coast(:, 1); xy = D.coast(:, 2:3);
    for s = unique(seg)'
        q = seg == s;
        if nnz(q) < 20, continue, end
        plot(ax, smooth3(xy(q, 1)), smooth3(xy(q, 2)), '-', 'Color', oi(1), 'LineWidth', 0.6);
    end
end

function y = smooth3(x)
    k = 3; x = x(:); p = [flipud(x(1:k)); x; flipud(x(end - k + 1:end))];
    y = conv(p, ones(2 * k + 1, 1) / (2 * k + 1), 'valid');
end

function maplims(ax, xl, yl)
    axis(ax, 'equal'); xlim(ax, xl); ylim(ax, yl); box(ax, 'on'); set(ax, 'Layer', 'top');
end

function cb = cbar(ax, lab, ticks, ticklabels, pos)
% colorbar at position pos (figure units); the axes keep their position
    p0 = get(ax, 'Position');
    cb = colorbar(ax);
    ylabel(cb, lab);
    if nargin >= 3 && ~isempty(ticks)
        try, set(cb, 'Ticks', ticks, 'TickLabels', ticklabels); catch, set(cb, 'YTick', ticks, 'YTickLabel', ticklabels); end
    end
    set(ax, 'Position', p0);
    if nargin >= 5, set(cb, 'Position', pos); end      % after the axes, or GNU Octave re-attaches it
end

function histw(ax, x, w, e, col, alpha)
% weighted density histogram drawn as a filled patch (values beyond the last edge go to the last bin)
    x = min(max(x(:), e(1)), e(end) - 1e-12); w = w(:) / sum(w);
    b = discretize_(x, e); d = accumarray(b, w, [numel(e) - 1 1]) ./ diff(e(:));
    X = reshape([e(1:end - 1); e(2:end)], 1, []); Y = reshape([d'; d'], 1, []);
    patch(ax, [X(1) X X(end)], [0 Y 0], col, 'FaceAlpha', alpha, 'EdgeColor', 'none');
end

function b = discretize_(x, e)
    b = zeros(size(x));
    for k = 1:numel(x), b(k) = find(x(k) >= e(1:end - 1), 1, 'last'); end
end

% ======================================================================= figure 1
function f = fig1()
    f = newfig(190, 84); ax = axes(f, 'Position', [0 0 1 1]); hold(ax, 'on'); axis(ax, [0 190 0 84]); axis(ax, 'off');
    T = {sprintf('Where is the\nchloride now?'), sprintf('Where should\nwe measure?'), sprintf('How much can\nwe pump?'), ...
         sprintf('What caused a\nsalinization event?'), sprintf('Does information\nreach the decision?')};
    B = {sprintf('Hydrochemistry: mixing,\nion exchange, BEX\nStrack interface with a\ntransition zone, calibrated\nto documented facts\nVariable-density section\nSAFE-GO, KALIB-GO:\nrobust learning rates'), ...
         sprintf('Goal-oriented EIG with\nadjoint sensitivities\nPRAG-GO, PRAG-MAR:\nthreshold-risk design\nSINERGO: pairwise synergy\nKRITIK-GO: early warning\nChloride sampling design'), ...
         sprintf('KRAMERS-GO: return-\nperiod-safe pumping\n(an escape problem)\nKUFI-GO: safe threshold\nwith simultaneous bands\nand randomized thresholds'), ...
         sprintf('ATRIB-GO: probability of\nnecessity (twin worlds)\nTMLE-GO: targeted risk\nof pumping regimes from\noperating records'), ...
         sprintf('RRJEDHA-GO: causal\ninformation flow\nKANAL-GO: design of the\npumping experiment\nKTHIMI-GO: feedback\ninformation as a\nmonitoring criterion')};
    fc = [232 241 250; 233 246 241; 253 241 230; 248 234 242; 251 237 230] / 255; ec = [oi(1); oi(3); oi(5); oi(4); oi(2)];
    w = 35; g = 2.75; x0 = (190 - 5 * w - 4 * g) / 2;
    for k = 1:5
        x = x0 + (k - 1) * (w + g);
        rectangle(ax, 'Position', [x 30 w 46], 'Curvature', [0.08 0.08], 'FaceColor', fc(k, :), 'EdgeColor', ec(k, :), 'LineWidth', 0.9);
        text(ax, x + w / 2, 74.5, T{k}, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', 'FontWeight', 'bold', 'FontSize', 7.2);
        text(ax, x + w / 2, 64.5, B{k}, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', 'FontSize', 6.2);
        plot(ax, [x x] + w / 2, [29.3 21.5], '-', 'Color', ec(k, :), 'LineWidth', 1.0);
        patch(ax, x + w / 2 + [-1.2 1.2 0], [21.8 21.8 19.6], ec(k, :), 'EdgeColor', 'none');
    end
    rectangle(ax, 'Position', [x0 3 5 * w + 4 * g 16.5], 'Curvature', [0.03 0.12], 'FaceColor', [0.953 0.953 0.953], 'EdgeColor', [0.35 0.35 0.35], 'LineWidth', 0.9);
    text(ax, 95, 17.6, 'Management decision: monitoring network, sampling depth, pumping and recharge rules', ...
         'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', 'FontWeight', 'bold', 'FontSize', 7.2);
    text(ax, 95, 11.6, sprintf(['Decision-relevant quantities: P(Cl > 250 mg/L), affected area, goal-oriented EIG (nats), safe pumping rate,\n' ...
         'probability of necessity, risk of a pumping regime, information that reaches the operator (bits)']), ...
         'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', 'FontSize', 6.2);
    text(ax, 95, 83, 'A decision chain for seawater-intrusion monitoring and management', 'HorizontalAlignment', 'center', ...
         'VerticalAlignment', 'top', 'FontWeight', 'bold', 'FontSize', 8.5);
end

% ======================================================================= figure 2
function f = fig2(R)
    m = R.m; D = R.D; W = D.wells; C = R.C;
    f = newfig(190, 125);
    ax = axes(f, 'Position', [0.07 0.2 0.38 0.77]); hold(ax, 'on');
    patch(ax, m.Bk(:, 1), m.Bk(:, 2), [0.918 0.949 0.918], 'EdgeColor', 'none');
    outline(ax, R);
    ys = m.cy(m.seac); xs = m.cx(m.seac) - m.dx / 2; [ys, o] = sort(ys); xs = xs(o);
    hs = plot(ax, xs, ys, '-', 'Color', oi(2), 'LineWidth', 2.6);
    wx = []; wy = [];
    for j = 1:m.ny
        ii = find(m.inside(j, :), 1, 'first');
        if ~isempty(ii) && ~m.sea_row(j), wx(end + 1) = m.xs(ii) - m.dx / 2 - 0.45; wy(end + 1) = m.ys(j); end %#ok<AGROW>
    end
    hm = plot(ax, wx, wy, '--', 'Color', [0.2 0.2 0.2], 'LineWidth', 1.2);
    plot(ax, [-6 22], [C.yCut C.yCut], ':', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.5);
    text(ax, -5.6, C.yCut + 0.4, sprintf('chloride model\nsector: y \\geq 24 km'), 'FontSize', 6, 'Color', [0.3 0.3 0.3], 'VerticalAlignment', 'bottom');
    x = (W.X - m.x0) / 1000; y = (W.Y - m.y0) / 1000; hasK = isfinite(W.K);
    ho = plot(ax, x(~hasK), y(~hasK), '.', 'Color', [0.55 0.55 0.55], 'MarkerSize', 5);
    c1 = hasK & W.K >= 150; c2 = hasK & W.K >= 75 & W.K < 150; c3 = hasK & W.K < 75;
    h1 = plot(ax, x(c1), y(c1), 'o', 'MarkerFaceColor', [0.549 0.318 0.039], 'MarkerEdgeColor', 'w', 'MarkerSize', 4);
    h2 = plot(ax, x(c2), y(c2), 's', 'MarkerFaceColor', oi(3), 'MarkerEdgeColor', 'w', 'MarkerSize', 4);
    h3 = plot(ax, x(c3), y(c3), '^', 'MarkerFaceColor', oi(1), 'MarkerEdgeColor', 'w', 'MarkerSize', 4);
    j = round(C.ySec / m.dx) + 1; cells = find(m.valid & m.aj == j);
    plot(ax, [m.shore(j) max(m.cx(cells)) + 0.125], [C.ySec C.ySec], 'k-', 'LineWidth', 1.0);
    text(ax, m.shore(j) - 0.4, C.ySec + 0.9, 'A', 'FontWeight', 'bold', 'HorizontalAlignment', 'right');
    text(ax, max(m.cx(cells)) + 0.5, C.ySec + 0.9, 'A''', 'FontWeight', 'bold');
    P = D.places;
    for k = 1:numel(P.name)
        if strncmp(P.name{k}, 'Durr', 4), continue, end
        plot(ax, P.x(k), P.y(k), 'kd', 'MarkerFaceColor', 'k', 'MarkerSize', 3);
        if strcmp(P.name{k}, 'Patok lagoon')
            text(ax, P.x(k) - 0.6, P.y(k), P.name{k}, 'FontSize', 6.4, 'HorizontalAlignment', 'right');
        else
            text(ax, P.x(k) + 0.6, P.y(k), P.name{k}, 'FontSize', 6.4);
        end
    end
    text(ax, -5, 45, sprintf('Adriatic\nSea'), 'Color', oi(1), 'FontAngle', 'italic', 'FontSize', 7.5);
    maplims(ax, [-6 22], [-1.5 55]); xlabel(ax, 'Easting from x_0 [km]'); ylabel(ax, 'Northing from y_0 [km]'); letter(ax, 'a');
    lg = legend(ax, [hs hm ho h1 h2 h3], {'Adriatic contact (this study)', 'inland margin (sea boundary in the companion model)', ...
           'other wells (DRASTIC survey)', 'K \geq 150 m d^{-1}', '75 \leq K < 150', 'K < 75'}, ...
           'Orientation', 'horizontal', 'NumColumns', 3, 'FontSize', 6, 'Box', 'off', 'Color', 'none');
    set(lg, 'Position', [0.06 0.005 0.88 0.07]);
    ax2 = axes(f, 'Position', [0.47 0.2 0.38 0.77]); hold(ax2, 'on');
    cm = fkcl_cmap('cividis_r');
    mapfield(ax2, m, m.cover, true(m.Nc, 1), cm, [0 55]);
    [xe, ye] = edges(m); xc = 0.5 * (xe(1:end - 1) + xe(2:end)); yc = 0.5 * (ye(1:end - 1) + ye(2:end));
    Gc = gridof(m, m.cover); Gc = Gc(1:end - 1, 1:end - 1);
    contour(ax2, xc, yc, Gc, [10 20 30 40], 'LineColor', 'w', 'LineWidth', 0.4);
    outline(ax2, R);
    ok = isfinite(W.depth);
    scatter(ax2, x(ok), y(ok), 18, W.depth(ok), 'filled', 'MarkerEdgeColor', 'k');
    maplims(ax2, [-6 22], [-1.5 55]); xlabel(ax2, 'Easting from x_0 [km]'); set(ax2, 'YTickLabel', []);
    cbar(ax2, 'depth to the aquifer top (DRASTIC depth) [m]', [], [], [0.89 0.3 0.014 0.6]); letter(ax2, 'b');
end

% ======================================================================= figure 3
function f = fig3(R)
    H = R.H; C = R.C; sw = H.sw; ch = R.D.chem; ifr = find(strcmp(ch.well, '193'));
    col = containers.Map({'503', '341', '340', '193'}, {oi(2), oi(5), oi(3), oi(1)});
    f = newfig(190, 56);
    ax = axes(f, 'Position', [0.06 0.2 0.17 0.72]); hold(ax, 'on');
    fm = logspace(-4, 0, 200); clm = ch.Cl(ifr) + fm * (sw.Cl - ch.Cl(ifr)); nam = ch.Na(ifr) + fm * (sw.Na - ch.Na(ifr));
    k = clm <= 3e4; hl = loglog(ax, clm(k), nam(k), '-', 'Color', [0.3 0.3 0.3], 'LineWidth', 0.8);
    set(ax, 'XScale', 'log', 'YScale', 'log');
    for fx = [0.01 0.05]
        c_ = ch.Cl(ifr) + fx * (sw.Cl - ch.Cl(ifr)); n_ = ch.Na(ifr) + fx * (sw.Na - ch.Na(ifr));
        plot(ax, c_, n_, 'o', 'MarkerSize', 2, 'MarkerFaceColor', [0.3 0.3 0.3], 'Color', [0.3 0.3 0.3]);
        text(ax, c_ * 0.55, n_ * 1.25, sprintf('%d %%', round(100 * fx)), 'FontSize', 5.8, 'Color', [0.3 0.3 0.3], 'VerticalAlignment', 'bottom');
    end
    off = containers.Map({'503', '341', '340', '193'}, {[1.35 0.62], [1.35 1.15], [0.18 1.25], [1.3 0.72]});
    for q = 1:numel(H.well)
        w = H.well{q}; plot(ax, ch.Cl(q), ch.Na(q), 'o', 'MarkerSize', 5, 'MarkerFaceColor', col(w), 'MarkerEdgeColor', 'k');
        o = off(w); text(ax, ch.Cl(q) * o(1), ch.Na(q) * o(2), w, 'FontSize', 6.2);
    end
    xlim(ax, [8 3e4]); ylim(ax, [8 2e4]); xlabel(ax, 'Cl [mg L^{-1}]'); ylabel(ax, 'Na [mg L^{-1}]');
    legend(ax, hl, {'conservative mixing'}, 'Location', 'northwest', 'Box', 'off', 'Color', 'none', 'FontSize', 6); letter(ax, 'a');
    ax = axes(f, 'Position', [0.32 0.2 0.2 0.72]); hold(ax, 'on');
    Y = [H.dNa(1:3) H.dCa(1:3) H.dMg(1:3) H.dK(1:3) H.dSO4(1:3)]';
    hb = bar(ax, 1:5, Y, 1.0);
    for q = 1:3, set(hb(q), 'FaceColor', col(H.well{q}), 'EdgeColor', 'w'); end
    plot(ax, [0.4 5.6], [0 0], 'k-', 'LineWidth', 0.5);
    set(ax, 'XTick', 1:5, 'XTickLabel', {'Na', 'Ca', 'Mg', 'K', 'SO_4'}); xlim(ax, [0.4 5.6]);
    ylabel(ax, sprintf('observed - mixing\n[meq L^{-1}]'));
    legend(ax, hb, strcat('well', {' '}, H.well(1:3)'), 'Location', 'southeast', 'Box', 'off', 'Color', 'none', 'FontSize', 6); letter(ax, 'b');
    ax = axes(f, 'Position', [0.6 0.2 0.16 0.72]); hold(ax, 'on');
    patch(ax, [-0.3 5.8 5.8 -0.3], [0 0 4 4], [0.914 0.965 0.945], 'EdgeColor', 'none');
    patch(ax, [-0.3 5.8 5.8 -0.3], [-4 -4 0 0], [0.984 0.929 0.902], 'EdgeColor', 'none');
    text(ax, 0.2, 3.3, 'freshening', 'FontSize', 6.2, 'Color', [0.25 0.25 0.25]); text(ax, 0.2, -3.6, 'salinization', 'FontSize', 6.2, 'Color', [0.25 0.25 0.25]);
    offc = containers.Map({'503', '341', '340', '193'}, {[0.15 -0.55], [-0.95 0.35], [0.15 0.3], [0.15 0.3]});
    for q = 1:numel(H.well)
        w = H.well{q}; plot(ax, 100 * H.f(q), H.BEX(q), 'o', 'MarkerSize', 5, 'MarkerFaceColor', col(w), 'MarkerEdgeColor', 'k');
        o = offc(w); text(ax, 100 * H.f(q) + o(1), H.BEX(q) + o(2), w, 'FontSize', 6.2);
    end
    plot(ax, [-0.3 5.8], [0 0], 'k-', 'LineWidth', 0.5); xlim(ax, [-0.3 5.8]); ylim(ax, [-4 4]);
    xlabel(ax, 'seawater fraction f [%]'); ylabel(ax, 'BEX [meq L^{-1}]'); letter(ax, 'c');
    ax = axes(f, 'Position', [0.84 0.2 0.14 0.72]); hold(ax, 'on');
    hh = zeros(1, 2);
    for q = 1:2
        w = H.trend.well{q}; hh(q) = plot(ax, H.trend.years, H.trend.Cl(q, :), '-o', 'Color', col(w), 'MarkerFaceColor', col(w), 'MarkerSize', 3.5, 'LineWidth', 1);
    end
    xlim(ax, [1982 2003]); ylim(ax, [900 1200]); set(ax, 'XTick', [1985 1995]);
    xlabel(ax, 'year'); ylabel(ax, 'Cl [mg L^{-1}]');
    legend(ax, hh, strcat('well', {' '}, H.trend.well'), 'Location', 'northeast', 'Box', 'off', 'Color', 'none', 'FontSize', 6); letter(ax, 'd');
end

% ======================================================================= figure 4
function f = fig4(R)
    Cal = R.Cal; S = Cal.S; w = Cal.w; n = size(S, 1); u = ones(n, 1) / n;
    f = newfig(190, 92);
    spec = {1, sprintf('upper-layer area with\nCl > 250 mg L^{-1} [%% of aquifer]'), 100, linspace(0, 45, 46), 15, 'T1: ~15 %';
            2, sprintf('littoral head\n[m a.s.l.]'), 1, linspace(0, 9, 46), 3, 'T2: ~3 m';
            11, sprintf('seawater fraction, second\naquifer, 0.5-2.5 km [%%]'), 100, linspace(0, 40, 41), 4.7, 'T3a: 341, 503';
            5, sprintf('upper-layer Cl, NE\nrecharge band [mg L^{-1}]'), 1, linspace(12, 40, 29), NaN, 'T3c: < 30';
            4, sprintf('seawater fraction, first\naquifer, 3-6 km [%%]'), 100, linspace(0, 2.4, 49), 1.86, 'well 340 (held out)';
            15, sprintf('seawater fraction, second\naquifer, 3-6 km [%%]'), 100, linspace(0, 2.4, 49), 1.86, 'well 340 (held out)'};
    pos = @(r, c) [0.05 + (c - 1) * 0.245, 0.66 - (r - 1) * 0.47, 0.19, 0.28];
    L = 'abcdefgh';
    for k = 1:6
        r = 1 + (k > 4); c = k - 4 * (k > 4);
        ax = axes(f, 'Position', pos(r, c)); hold(ax, 'on');
        x = S(:, spec{k, 1}) * spec{k, 3}; e = spec{k, 4};
        histw(ax, x, u, e, [0.8 0.8 0.8], 1); histw(ax, x, w, e, oi(1), 0.75);
        yl = get(ax, 'YLim');
        if isnan(spec{k, 5}), hv = plot(ax, [30 30], yl, '--', 'Color', oi(2), 'LineWidth', 1.2);
        else, hv = plot(ax, [1 1] * spec{k, 5}, yl, '-', 'Color', oi(2), 'LineWidth', 1.2); end
        xlim(ax, [e(1) e(end)]); set(ax, 'YTick', []); xlabel(ax, spec{k, 2});
        legend(ax, hv, spec(k, 6), 'Location', 'northeast', 'Box', 'off', 'Color', 'none', 'FontSize', 5.8); letter(ax, L(k));
    end
    ax = axes(f, 'Position', pos(2, 3)); hold(ax, 'on');
    Rm = Cal.P.R * 365.25 * 1000; e = linspace(0, 1000, 41);
    histw(ax, Rm, u, e, [0.8 0.8 0.8], 1); histw(ax, Rm, w, e, oi(3), 0.8);
    yl = get(ax, 'YLim'); plot(ax, [1 1] * 5e-4 * 365.25 * 1000, yl, 'k:'); text(ax, 200, yl(2) * 0.85, 'companion model', 'FontSize', 5.8);
    xlim(ax, [0 1000]); set(ax, 'YTick', []); xlabel(ax, 'net recharge R [mm yr^{-1}]'); letter(ax, 'g');
    ax = axes(f, 'Position', pos(2, 4)); hold(ax, 'on');
    e = linspace(0, 100, 41); histw(ax, Cal.P.w, u, e, [0.8 0.8 0.8], 1); histw(ax, Cal.P.w, w, e, oi(3), 0.8);
    xlim(ax, [0 100]); set(ax, 'YTick', []); xlabel(ax, 'transition-zone half-width w [m]'); letter(ax, 'h');
end

% ======================================================================= figure 5
function f = fig5(R)
    m = R.m; c = R.Post.cells;
    f = newfig(190, 158);
    lay = {'sh', 'mid', 'dp'}; ttl = {'first aquifer (upper screens)', 'second aquifer (mid-depth)', 'aquifer base'};
    cmv = fkcl_cmap('viridis'); cmp = fkcl_cmap('magma_r');
    [xe, ye] = edges(m); xc = 0.5 * (xe(1:end - 1) + xe(2:end)); yc = 0.5 * (ye(1:end - 1) + ye(2:end));
    L = 'abcdef';
    for k = 1:3
        for r = 1:2
            ax = axes(f, 'Position', [0.07 + (k - 1) * 0.255, 0.555 - (r - 1) * 0.435, 0.24, 0.385]); hold(ax, 'on');
            if r == 1
                mapfield(ax, m, log10(c.(['Cl_' lay{k} '_p50'])), m.valid, cmv, [1 log10(21000)]);
                title(ax, ttl{k}, 'FontWeight', 'normal');
            else
                P = c.(['P250_' lay{k}]);
                mapfield(ax, m, P, m.valid, cmp, [0 1]);
                G = gridof(m, P, m.valid); G = G(1:end - 1, 1:end - 1); G(isnan(G)) = 0;
                contour(ax, xc, yc, G, [0.5 0.5], 'LineColor', 'w', 'LineWidth', 0.8);
                if k == 3
                    Gw = gridof(m, c.P_wedge, m.valid); Gw = Gw(1:end - 1, 1:end - 1); Gw(isnan(Gw)) = 0;
                    contour(ax, xc, yc, Gw, [0.5 0.5], 'LineColor', oi(1), 'LineWidth', 1.0);
                    contour(ax, xc, yc, Gw, [0.05 0.95], '--', 'LineColor', oi(6), 'LineWidth', 0.6);
                end
            end
            outline(ax, R); maplims(ax, [-2.5 16.5], [23.5 53.5]);
            text(ax, 0.03, 0.97, L((r - 1) * 3 + k), 'Units', 'normalized', 'FontWeight', 'bold', 'FontSize', 9, 'VerticalAlignment', 'top');
            if k > 1, set(ax, 'YTickLabel', []); else, ylabel(ax, 'Northing from y_0 [km]'); end
            if r == 1, set(ax, 'XTickLabel', []); else, xlabel(ax, 'Easting from x_0 [km]'); end
            if k == 3 && r == 1, cbar(ax, 'posterior median chloride [mg L^{-1}]', 1:4, {'10', '100', '1000', '10000'}, [0.86 0.59 0.014 0.31]); end
            if k == 3 && r == 2, cbar(ax, 'P(Cl > 250 mg L^{-1})', [], [], [0.86 0.155 0.014 0.31]); end
        end
    end
    annotation(f, 'textbox', [0.06 0.0 0.8 0.04], 'String', ['white line: P(Cl > 250 mg/L) = 0.5;  blue: seawater wedge at the base, ' ...
               'P = 0.5;  dashed: P = 0.05 and 0.95'], 'EdgeColor', 'none', 'FontSize', 6.2, 'HorizontalAlignment', 'center');
end

% ======================================================================= figure 6
function f = fig6(R)
    Sec = R.Sec; s = Sec.p50_fine.s; C = R.C;
    f = newfig(190, 70);
    ax = axes(f, 'Position', [0.07 0.17 0.55 0.72]); hold(ax, 'on');
    Cl = Sec.p50_fine.Cl;
    xe = s.xe / 1000; ze = s.ze;
    Gp = nan(s.nz + 1, s.nx + 1); Gp(1:end - 1, 1:end - 1) = log10(Cl);
    h = pcolor(ax, xe, ze, Gp); set(h, 'EdgeColor', 'none'); colormap(ax, fkcl_cmap('viridis')); caxis(ax, [1 log10(21000)]);
    xc = s.xc / 1000; zc = s.zc; G0 = Cl; G0(isnan(G0)) = 0;
    [cc, hc] = contour(ax, xc, zc, G0, [250 1000 5000 10000], 'LineColor', 'w', 'LineWidth', 0.6); clabel(cc, hc, 'FontSize', 5.6, 'Color', 'w');
    % sharp interface of the same member, through the areal cell centres
    p = fkcl_member(R.Cal.P, R.Post.idx(Sec.p50_fine.member));
    o = fkcl_model_run(R.m, p); m = R.m;
    j = round(C.ySec / m.dx) + 1; cells = find(m.valid & m.aj == j); [~, q] = sort(m.cx(cells)); cells = cells(q);
    xs = m.cx(cells) - m.shore(j); zb = o.d(cells) + o.B(cells); zt = o.d(cells); zz = o.zeta(cells);
    ok = find(zz < zb);
    if ~isempty(ok)
        last = max(ok); xi = [xs(1:last); xs(last) + m.dx / 2]; zi = [zz(1:last); zb(last)];
        lo = max(zi - p.w, interp1(xs, zt, xi, 'linear', 'extrap')); hi = min(zi + p.w, interp1(xs, zb, xi, 'linear', 'extrap'));
        hb = patch(ax, [xi; flipud(xi)], [lo; flipud(hi)], oi(2), 'FaceAlpha', 0.2, 'EdgeColor', 'none');
        hl = plot(ax, xi, zi, '-', 'Color', oi(2), 'LineWidth', 1.1);
        legend(ax, [hl hb], {'sharp interface, areal model', sprintf('\\pm w = %.0f m (calibrated)', p.w)}, 'Location', 'southeast', 'FontSize', 6);
    end
    set(ax, 'YDir', 'reverse'); xlim(ax, [0 xe(end)]); ylim(ax, [0 ze(end)]); box(ax, 'on'); set(ax, 'Layer', 'top', 'Color', [0.937 0.937 0.937]);
    xlabel(ax, 'distance from the shoreline along A-A'' [km]'); ylabel(ax, 'depth below sea level [m]');
    text(ax, 0.15, 12, 'clay-silt cover (inactive)', 'FontSize', 6.2, 'Color', [0.3 0.3 0.3]);
    cbar(ax, 'chloride [mg L^{-1}]', 1:4, {'10', '100', '1000', '10000'}, [0.635 0.17 0.012 0.72]); letter(ax, 'a');
    ax2 = axes(f, 'Position', [0.83 0.17 0.15 0.6]); hold(ax2, 'on');
    tags = {'p05', 'p50', 'p95'};
    ts = cellfun(@(t) Sec.(t).toe_strack, tags) / 1000; tv = cellfun(@(t) Sec.(t).toe_vd, tags) / 1000;
    h1 = plot(ax2, ts, 1:3, 's', 'MarkerFaceColor', oi(2), 'MarkerEdgeColor', oi(2));
    h2 = plot(ax2, tv, 1:3, 'o', 'MarkerFaceColor', oi(1), 'MarkerEdgeColor', oi(1));
    if isfield(Sec, 'aT01'), plot(ax2, Sec.aT01.toe_vd / 1000, 1.78, 'v', 'MarkerFaceColor', oi(6), 'MarkerEdgeColor', oi(6)); text(ax2, Sec.aT01.toe_vd / 1000 + 0.12, 1.78, '\alpha_T = 0.1 m', 'FontSize', 5.6); end
    if isfield(Sec, 'aT3'), plot(ax2, Sec.aT3.toe_vd / 1000, 2.22, '^', 'MarkerFaceColor', oi(6), 'MarkerEdgeColor', oi(6)); text(ax2, Sec.aT3.toe_vd / 1000 + 0.12, 2.22, '\alpha_T = 3 m', 'FontSize', 5.6); end
    set(ax2, 'YTick', 1:3, 'YTickLabel', {'P5 member', 'P50 member', 'P95 member'}); ylim(ax2, [0.4 3.6]);
    xlim(ax2, [0 max(5, 1.15 * max([ts tv]))]); xlabel(ax2, 'toe from the shoreline [km]');
    legend(ax2, [h1 h2], {'sharp interface (areal)', 'variable density'}, 'Location', 'northoutside', 'FontSize', 5.8, 'Box', 'off', 'Color', 'none'); letter(ax2, 'b');
end

% ======================================================================= figure 7
function f = fig7(R)
    m = R.m; Ds = R.Des.sh; Dm = R.Des.mid; W = R.D.wells;
    f = newfig(190, 100);
    ax = axes(f, 'Position', [0.07 0.21 0.27 0.76]); hold(ax, 'on');
    mapfield(ax, m, Ds.field.sh, m.valid, fkcl_cmap('ylgnbu'), [0 1.4]); outline(ax, R);
    nW = numel(Ds.wells); e1 = Ds.single(1:nW);
    xw = (m.cx(Ds.cells)); yw = (m.cy(Ds.cells));
    scatter(ax, xw, yw, 4 + 18 * e1, [0.2 0.2 0.2], 'filled');
    best = Ds.k(3).exhaustive.sites; gr = Ds.k(3).greedy.sites;
    for q = 1:numel(best)
        wn = strtok(best{q}, ':'); i = find(strcmp(Ds.wells, wn), 1);
        hb = plot(ax, xw(i), yw(i), 'o', 'MarkerSize', 8, 'MarkerEdgeColor', oi(2), 'LineWidth', 1.4);
        text(ax, xw(i) + 0.5, yw(i), wn, 'FontSize', 6.2, 'Color', oi(2), 'FontWeight', 'bold');
    end
    for q = 1:numel(gr)
        wn = strtok(gr{q}, ':'); i = find(strcmp(Ds.wells, wn), 1);
        hg = plot(ax, xw(i), yw(i), 'x', 'MarkerSize', 6, 'Color', oi(5), 'LineWidth', 1.2);
    end
    for wn = {'A13', 'A10'}
        i = find(strcmp(W.id, wn{1}), 1);
        hp = plot(ax, (W.X(i) - m.x0) / 1000, (W.Y(i) - m.y0) / 1000, 'd', 'MarkerFaceColor', oi(4), 'MarkerEdgeColor', 'k', 'MarkerSize', 5);
        text(ax, (W.X(i) - m.x0) / 1000 + 0.5, (W.Y(i) - m.y0) / 1000, wn{1}, 'FontSize', 6, 'Color', oi(4));
    end
    maplims(ax, [-2.5 16.5], [23.5 53.5]); xlabel(ax, 'Easting from x_0 [km]'); ylabel(ax, 'Northing from y_0 [km]');
    cbar(ax, 'EIG of one upper-screen sample [nats]', [], [], [0.355 0.3 0.011 0.55]); letter(ax, 'a');
    lg = legend(ax, [hb hg hp], {'best triple (exhaustive)', 'greedy triple', 'companion design, in sector'}, ...
           'FontSize', 5.8, 'Box', 'off', 'Color', 'none', 'NumColumns', 2);
    set(lg, 'Position', [0.03 0.005 0.36 0.07]);
    ax = axes(f, 'Position', [0.515 0.6 0.19 0.34]); hold(ax, 'on');
    K = 1:5; ge = arrayfun(@(k) Ds.k(k).greedy.eig_exact, K); pe = arrayfun(@(k) Ds.k(k).pair.eig_exact, K);
    h1 = plot(ax, K, ge, '-x', 'Color', oi(5)); h2 = plot(ax, K, pe, '-s', 'Color', oi(3), 'MarkerSize', 4);
    h3 = plot(ax, [2 3], [Ds.k(2).exhaustive.eig_exact Ds.k(3).exhaustive.eig_exact], 'p', 'MarkerFaceColor', oi(2), 'MarkerEdgeColor', oi(2), 'MarkerSize', 8);
    plot(ax, [0.8 5.2], [1 1] * Ds.published.eig_exact, '--', 'Color', oi(4)); text(ax, 5, Ds.published.eig_exact + 0.06, 'A13 + A10', 'FontSize', 6, 'Color', oi(4), 'HorizontalAlignment', 'right');
    xlim(ax, [0.8 5.2]); ylim(ax, [0 1.85]); set(ax, 'XTick', K); xlabel(ax, 'number of samples'); ylabel(ax, 'exact EIG of the goal [nats]');
    legend(ax, [h1 h2 h3], {'greedy', 'pairwise greedy (SINERGO)', 'exhaustive'}, 'Location', 'southeast', 'FontSize', 5.6, 'Box', 'off', 'Color', 'none'); letter(ax, 'b');
    ax = axes(f, 'Position', [0.79 0.6 0.19 0.34]); hold(ax, 'on');
    bs = zeros(3, 2);
    for d = 1:3, bs(d, 1) = max(Ds.single((d - 1) * nW + (1:nW))); bs(d, 2) = max(Dm.single((d - 1) * nW + (1:nW))); end
    hb2 = bar(ax, 1:3, bs, 0.8); set(hb2(1), 'FaceColor', oi(1)); set(hb2(2), 'FaceColor', oi(2));
    set(ax, 'XTick', 1:3, 'XTickLabel', {'upper', 'middle', 'base'}); ylim(ax, [0 2.05]); xlabel(ax, 'sampled depth'); ylabel(ax, 'best single-sample EIG [nats]');
    legend(ax, hb2, {'goal: first-aquifer area', 'goal: second-aquifer area'}, 'Location', 'northeast', 'FontSize', 5.6, 'Box', 'off', 'Color', 'none'); letter(ax, 'c');
    ax = axes(f, 'Position', [0.515 0.12 0.19 0.32]); hold(ax, 'on');
    for g = 1:2
        if g == 1, Dd = Ds; cl = oi(1); else, Dd = Dm; cl = oi(2); end
        L = []; E = [];
        for k = 1:5, L = [L Dd.k(k).greedy.eig_lin Dd.k(k).pair.eig_lin]; E = [E Dd.k(k).greedy.eig_exact Dd.k(k).pair.eig_exact]; end %#ok<AGROW>
        hh(g) = plot(ax, L, E, 'o', 'MarkerFaceColor', cl, 'MarkerEdgeColor', cl, 'MarkerSize', 3); %#ok<AGROW>
    end
    plot(ax, [0 2.1], [0 2.1], ':', 'Color', [0.5 0.5 0.5]); xlim(ax, [1 2.05]); ylim(ax, [1 2.05]);
    xlabel(ax, 'linear (ensemble) EIG [nats]'); ylabel(ax, 'exact EIG [nats]');
    legend(ax, hh, {sprintf('first aquifer, \\rho_s = %.2f', Ds.spearman_single), sprintf('second aquifer, \\rho_s = %.2f', Dm.spearman_single)}, ...
           'Location', 'northwest', 'FontSize', 5.4, 'Box', 'off', 'Color', 'none'); letter(ax, 'd');
    ax = axes(f, 'Position', [0.79 0.12 0.19 0.32]); hold(ax, 'on');
    A = R.Post.area; e = linspace(0, 160, 41); u = ones(size(A, 1), 1);
    histw(ax, A(:, 1), u, e, oi(1), 0.75); histw(ax, A(:, 2), u, e, oi(2), 0.6);
    yl = get(ax, 'YLim'); set(ax, 'YLim', [0 yl(2) * 1.35]); plot(ax, [1 1] * 0.15 * 349.09, [0 yl(2) * 1.35], 'k--');
    set(ax, 'YTick', []); xlabel(ax, 'area with Cl > 250 mg L^{-1} [km^2]'); letter(ax, 'e');
    text(ax, 0.98, 0.95, 'first aquifer', 'Units', 'normalized', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top', 'FontSize', 5.8, 'Color', oi(1));
    text(ax, 0.98, 0.83, 'second aquifer', 'Units', 'normalized', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top', 'FontSize', 5.8, 'Color', oi(2));
end

% ======================================================================= figure 8
function f = fig8(R)
    E = fullfile(R.C.repo, 'experiments');
    f = newfig(190, 108);
    pos = @(r, c) [0.07 + (c - 1) * 0.33, 0.6 - (r - 1) * 0.5, 0.25, 0.32];
    % (a) KRITIK-GO
    k2 = fkcl_json(fullfile(E, 'kritik_go', 'kritik2_results.json')); k1 = fkcl_json(fullfile(E, 'kritik_go', 'kritik_results.json'));
    ax = axes(f, 'Position', pos(1, 1)); hold(ax, 'on');
    patch(ax, [k1.xm_p10 k1.xm_p90 k1.xm_p90 k1.xm_p10], [0 0 1.45 1.45], [0.9 0.9 0.9], 'EdgeColor', 'none');
    s = k2.S_POS(:); J = k2.J_io(:); J0 = k2.J0(:);
    h1 = plot(ax, s, J / max(J), '-o', 'Color', oi(1), 'MarkerFaceColor', oi(1), 'MarkerSize', 3);
    h2 = plot(ax, s, J0 / max(J0), '-s', 'Color', [0.5 0.5 0.5], 'MarkerFaceColor', [0.5 0.5 0.5], 'MarkerSize', 3);
    text(ax, mean([k1.xm_p10 k1.xm_p90]), 0.55, sprintf('critical\ntoe'), 'HorizontalAlignment', 'center', 'FontSize', 5.6);
    ylim(ax, [0 1.45]); xlabel(ax, 'logger distance from the coast [m]'); ylabel(ax, 'criterion / max');
    legend(ax, [h1 h2], {sprintf('KRITIK-GO (\\rho_s = %.2f)', k2.spearman_Jio_acc), sprintf('status (\\rho_s = %.2f)', k2.spearman_J0_acc)}, 'Location', 'northwest', 'FontSize', 5.4, 'Box', 'off', 'Color', 'none');
    title(ax, 'a  KRITIK-GO: early warning', 'FontWeight', 'bold', 'FontSize', 7.6);
    % (b) KRAMERS-GO
    kr = fkcl_json(fullfile(E, 'kramers_go', 'kramers_results.json'));
    ax = axes(f, 'Position', pos(1, 2)); hold(ax, 'on');
    T = kr.TS(:)'; med = arrayfun(@(t) fkcl_json(kr, 'E2', 'fsafe', num2str(t)), T);
    F3 = zeros(numel(kr.E3), numel(T));
    for q = 1:numel(kr.E3), for t = 1:numel(T), F3(q, t) = fkcl_json(kr.E3(q), 'fsafe', num2str(T(t))); end, end
    Q = fkcl_quantile(F3, [0.1 0.9]);
    patch(ax, [T fliplr(T)], [Q(1, :) fliplr(Q(2, :))], oi(5), 'FaceAlpha', 0.25, 'EdgeColor', 'none');
    plot(ax, T, med, '-o', 'Color', oi(5), 'MarkerFaceColor', oi(5), 'MarkerSize', 3); set(ax, 'XScale', 'log');
    ylim(ax, [0.4 1]); xlabel(ax, 'return period T [yr]'); ylabel(ax, 'safe pumping Q_T / Q_c');
    title(ax, 'b  KRAMERS-GO: safe pumping', 'FontWeight', 'bold', 'FontSize', 7.6);
    % (c) SAFE-GO / KALIB-GO
    sg = fkcl_json(fullfile(E, 'safe_go', 'safego_results.json')); kg = fkcl_json(fullfile(E, 'kalib_go', 'kalibgo_results.json'));
    ax = axes(f, 'Position', pos(1, 3)); hold(ax, 'on');
    ne = [0 15 30 60 120 240];
    cb = arrayfun(@(n) fkcl_json(sg, 'E1', num2str(n), 'bayes', 'cov'), ne);
    cs = arrayfun(@(n) fkcl_json(sg, 'E1', num2str(n), 'safe10', 'cov'), ne);
    ck = arrayfun(@(n) fkcl_json(kg, 'E1', num2str(n), 'kalib', 'cov'), ne);
    plot(ax, [0 240], [0.9 0.9], ':', 'Color', [0.6 0.6 0.6]);
    h1 = plot(ax, ne, cb, '-o', 'Color', [0.4 0.4 0.4], 'MarkerSize', 3); h2 = plot(ax, ne, cs, '-s', 'Color', oi(3), 'MarkerSize', 3);
    h3 = plot(ax, ne, ck, '-^', 'Color', oi(1), 'MarkerSize', 3);
    ylim(ax, [0.4 1.02]); xlabel(ax, 'exact coastal readings'); ylabel(ax, sprintf('coverage of the 90 %%\ntoe interval'));
    legend(ax, [h1 h2 h3], {'Bayes', 'SAFE-GO', 'KALIB-GO'}, 'Location', 'southwest', 'FontSize', 5.6, 'Box', 'off', 'Color', 'none');
    title(ax, 'c  SAFE-GO / KALIB-GO', 'FontWeight', 'bold', 'FontSize', 7.6);
    % (d) ATRIB-GO
    at = fkcl_json(fullfile(E, 'atrib_go', 'atrib_results.json'), 'A2', 'designs');
    keys = {'none', 'time', 'toe_100', 'toe_50', 'rain_y_0.10', 'rain_y_0.05', 'rain_y_0.02', 'rain_q_0.02'};
    lab = {'event only', '+ date', 'toe, 100 m', 'toe, 50 m', 'recharge, yr, 10 %', 'recharge, yr, 5 %', 'recharge, yr, 2 %', 'recharge, qtr, 2 %'};
    v = cellfun(@(k) 100 * fkcl_json(at, k, 'conf'), keys);
    ax = axes(f, 'Position', pos(2, 1) + [0.04 0 -0.04 0]); hold(ax, 'on');
    cl = [0.6 0.6 0.6; 0.6 0.6 0.6; oi(1); oi(1); oi(3); oi(3); oi(3); oi(3)];
    for q = 1:8, patch(ax, [0 v(q) v(q) 0], q + [-0.38 -0.38 0.38 0.38], cl(q, :), 'EdgeColor', 'none'); end   % bars as patches: same in MATLAB and Octave
    set(ax, 'YDir', 'reverse', 'YTick', 1:8, 'YTickLabel', lab, 'FontSize', 6); ylim(ax, [0.4 8.6]);
    xlabel(ax, 'events attributed with confidence [%]'); title(ax, 'd  ATRIB-GO: attribution', 'FontWeight', 'bold', 'FontSize', 7.6);
    % (e) KUFI-GO
    ku = fkcl_json(fullfile(E, 'kufi_go', 'kufi_results.json'), 'res', '1000|op+D', '0.35');
    rules = {'plugin', 'point', 'band', 'msm', 'band_first'};
    v = cellfun(@(r) 100 * fkcl_json(ku, r, 'viol'), rules);
    ax = axes(f, 'Position', pos(2, 2)); hold(ax, 'on');
    cl = [oi(2); oi(5); oi(1); oi(6); oi(3)];
    for q = 1:5, patch(ax, q + [-0.38 0.38 0.38 -0.38], [0 0 v(q) v(q)], cl(q, :), 'EdgeColor', 'none'); end
    plot(ax, [0.4 5.6], [5 5], ':', 'Color', [0.5 0.5 0.5]);
    set(ax, 'XTick', 1:5, 'XTickLabel', {'plug-in', 'point', 'band', 'MSM', 'first'}); xlim(ax, [0.4 5.6]); ylim(ax, [0 80]);
    ylabel(ax, 'chosen threshold unsafe [%]'); title(ax, 'e  KUFI-GO: threshold choice', 'FontWeight', 'bold', 'FontSize', 7.6);
    % (f) KTHIMI-GO
    kt = fkcl_json(fullfile(E, 'kthimi_go', 'kthimi_results.json'));
    d = kt.designs; if iscell(d), d = [d{:}]; end
    nm = [d.nomon]; d0 = d(nm); d = d(~nm);
    ax = axes(f, 'Position', pos(2, 3)); hold(ax, 'on');
    kap = unique([d.kappa]); hh = zeros(1, numel(kap) + 1); lb = cell(1, numel(kap) + 1);
    for q = 1:numel(kap)
        dd = d([d.kappa] == kap(q)); c0 = oi(1) * (0.45 + 0.55 * q / numel(kap)) + (1 - (0.45 + 0.55 * q / numel(kap))) * [1 1 1];
        hh(q) = plot(ax, 1000 * [dd.feedback], 100 * [dd.risk], 'o', 'MarkerFaceColor', c0, 'MarkerEdgeColor', c0, 'MarkerSize', 3.2);
        lb{q} = sprintf('\\kappa = %g', kap(q));
    end
    hh(end) = plot(ax, 0, 100 * d0.risk, 'd', 'MarkerFaceColor', oi(2), 'MarkerEdgeColor', oi(2), 'MarkerSize', 4); lb{end} = 'no monitoring';
    text(ax, 0.97, 0.97, sprintf('\\rho_s = %.2f\n(sensor: %.2f)', kt.rho_feedback, kt.rho_sensor), 'Units', 'normalized', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top', 'FontSize', 6);
    xlabel(ax, 'feedback information [mbit per decision]'); ylabel(ax, '10-yr salinization risk [%]');
    legend(ax, hh, lb, 'Location', 'southwest', 'FontSize', 5.4, 'Box', 'off', 'Color', 'none');
    title(ax, 'f  KTHIMI-GO: feedback', 'FontWeight', 'bold', 'FontSize', 7.6);
end
