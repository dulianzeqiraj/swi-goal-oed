function make_prova_figures(which, resDir)
%MAKE_PROVA_FIGURES  Figures P1-P7 of PROVA-GO (TRIAL-GO on the Fushe-Kuqe model).
%   make_prova_figures() makes every figure from the results in res/ (run
%   PROVA_GO_RUN and PROVA_MAR first); make_prova_figures({'P2','P4'}) makes a
%   subset. Each figure is 16 cm wide (17 cm for the full-page maps), saved as PNG
%   (300 dpi) and vector PDF in res/. Every number shown is printed and written to
%   res/figures_log.txt.
%     P1 model and misspecification     P2 robust Gittins index (Appendix D)
%     P3 one truth: TRIAL-GO at work    P4 results over all truths
%     P5 MAR process maps               P6 why the structure matters for MAR
%     P7 W-E section: sharp-interface wedge, pumping out and MAR injection in
%   Style: the palette, font scaling fs(), panel letters, axes and legend helpers
%   are those of experiments/spiranca_go/certain_coast/matlab_figs/run_all_figures.m
%   (copied below); the model maps follow Fig. 7 of Zeqiraj (2026, J. Hydrol. 680,
%   136559): local km axes E/N, black polygon outline, turbo colour field with a
%   vertical colour bar, the toe as a black dashed line, MAR wells as green
%   numbered diamonds; supply (extraction) wells as downward triangles.
%   MATLAB or GNU Octave (xvfb-run -a octave --no-gui --eval "make_prova_figures").

    here = prova_go_setup(); if nargin < 2 || isempty(resDir), resDir = fullfile(here, 'res'); end
    if nargin < 1 || isempty(which), which = {'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'}; end
    if exist('OCTAVE_VERSION', 'builtin') ~= 0
        warning('off', 'Octave:print:figure-too-large');
        if any(strcmp(available_graphics_toolkits(), 'qt')), graphics_toolkit('qt'); end
    end
    lg = fopen(fullfile(resDir, 'figures_log.txt'), 'a');
    say(lg, '\n=== make_prova_figures %s\n', datestr(now, 31));
    L = load(fullfile(resDir, 'prova_setup.mat'));
    fun = struct('P1', @figP1, 'P2', @figP2, 'P3', @figP3, 'P4', @figP4, 'P5', @figP5, 'P6', @figP6, 'P7', @figP7);
    for q = 1:numel(which)
        t0 = tic;
        try
            f = fun.(which{q}); f(L, resDir, lg);
            say(lg, '%s done (%.1f s)\n', which{q}, toc(t0));
        catch err
            say(lg, 'FAILED %s: %s (%s line %d)\n', which{q}, err.message, err.stack(1).name, err.stack(1).line);
            close(findall(0, 'Type', 'figure'));
        end
    end
    fclose(lg);
end

% =====================================================================================================================
function figP1(L, resDir, lg)
% The model and the misspecification: (a) one truth's log-K, (b) the five structures, (c)-(d) flux-scale invariance.
pal = palette(); M = L.M; S = L.S; arms = L.arms; C = L.checks;
P = load(fullfile(resDir, 'prova_demo.mat')); tr = P.demo.tr;
fig = newFigure(16, 13.8);
% (a) truth map ------------------------------------------------------------------------------------------------
ax = newAxes(fig, [1.3 1.2 4.4 11.0]);
lk = log10(M.K0c .* exp(tr.u)); cl = [floor(min(lk) * 10) / 10, ceil(max(lk) * 10) / 10];
drawField(ax, M, lk, turbo(256), cl);
Z = nan(M.ny, M.nx); Z(M.act) = M.zone;
contour(ax, M.xs, M.ys, Z, 0.5:1:M.Nz + 0.5, 'LineColor', [1 1 1], 'LineWidth', 0.7);
St = nan(M.ny, M.nx); St(M.act) = M.dcoast;
contour(ax, M.xs, M.ys, St, [M.stripKm M.stripKm], 'LineColor', pal.ink, 'LineStyle', '--', 'LineWidth', 0.9);
plot(ax, M.Bk(:, 1), M.Bk(:, 2), '-', 'Color', pal.ink, 'LineWidth', 0.9);
coastLine(ax, M, coastBlue(), 1.8);
o = M.obsCell;
plot(ax, M.X(o), M.Y(o), 'o', 'MarkerSize', 3.8, 'MarkerFaceColor', pal.red, 'MarkerEdgeColor', 'w', 'LineWidth', 0.4);
wellsOut(ax, M, pal);
set(ax, 'XLim', [0 21], 'YLim', [0 52.5], 'DataAspectRatio', [1 1 1], 'XTick', 0:5:20, 'YTick', 0:10:50);
finishAxes(ax, 'E [km]', 'N [km]', true);
northArrow(ax, 19.3, 44.5, 4.0); scaleBar(ax, 0.8, 2.2, 5);
panelLabel(ax, '(a)', 1.2);
colorbarV(fig, [1.3 + 15.3 * 4.4 / 21, 1.2 + 19.5 * 11 / 52.5, 0.22, 3.1], turbo(256), cl, {'log_{10} K', '[m d^{-1}]'});
say(lg, 'P1a: truth seed %d (strip %d, xi_R %+.3f): log10 K in [%.2f, %.2f]; zones %d; strip cells %d; J = %d wells\n', ...
    tr.seed, tr.hasStrip, tr.xiR, min(lk), max(lk), M.Nz, nnz(M.strip), M.J);
% (b) five structures ------------------------------------------------------------------------------------------
names = {'A1 zones', 'A2 uniform', 'A3 facies', 'A4 zones', 'A5 zones'};
sub = {'R fixed', '+ R', '+ R', '+ R', '+ strip + R'};
w = 1.70; x0 = 7.2; y0 = 8.75; hgt = 4.25;
zc = lines_(M.Nz);
for m = 1:5
    axm = newAxes(fig, [x0 + (m - 1) * (w + 0.06) y0 w hgt]);
    switch m
        case {1, 4}, v = M.zone; cm = zc; clim = [0.5 M.Nz + 0.5];
        case 2, v = ones(M.Nc, 1); cm = pal.lightBlue; clim = [0.5 1.5];
        case 3, v = M.zfac(M.zone); cm = [pal.orange; pal.aqua; pal.blue]; clim = [0.5 3.5];
        case 5, v = M.zone; v(M.strip) = M.Nz + 1; cm = [zc; 0.30 0.30 0.30]; clim = [0.5 M.Nz + 1.5];
    end
    drawField(axm, M, v, cm, clim, true);
    plot(axm, M.Bk(:, 1), M.Bk(:, 2), '-', 'Color', pal.ink, 'LineWidth', 0.6);
    set(axm, 'XLim', [0 21], 'YLim', [0 52.5], 'DataAspectRatio', [1 1 1], 'XTick', [], 'YTick', [], ...
        'Box', 'on', 'XColor', pal.refGray, 'YColor', pal.refGray, 'LineWidth', 0.5, 'Color', 'w');
    text(axm, 0.5, -0.02, names{m}, 'Units', 'normalized', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
         'FontSize', fs(8), 'FontWeight', 'bold', 'Color', armColor(m));
    text(axm, 0.5, -0.115, sub{m}, 'Units', 'normalized', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
         'FontSize', fs(7.5), 'Color', pal.ink2);
    text(axm, 0.5, -0.205, sprintf('%d par.', arms(m).n), 'Units', 'normalized', 'HorizontalAlignment', 'center', ...
         'VerticalAlignment', 'top', 'FontSize', fs(7.5), 'Color', pal.ink2);
    if m == 1, panelLabel(axm, '(b)', 0.35); end
end
say(lg, 'P1b: parameters per arm %s; facies classes present %s\n', mat2str([arms.n]), mat2str(unique(M.zfac)'));
items = {legendItem('line', 'coast (h = 0)', coastBlue(), '-', 1.8), legendItem('line', 'pilot-zone borders (a)', [0.75 0.75 0.75], '-', 0.8), ...
         legendItem('line', sprintf('coastal strip, %.1f km', M.stripKm), pal.ink, '--', 0.9), ...
         legendItem('marker', sprintf('observation wells (J = %d)', M.J), pal.red, 'o', 4, 'w'), ...
         legendItem('marker', 'supply wells A, B (out)', pal.ink, 'v', 6, 'w')};
drawLegend(fig, [7.2 5.85 8.6 1.45], items, 3, [4.0 4.5]);
% (c) heads invariant, (d) metered responses scale as 1/c --------------------------------------------------------
J = M.J; th = zeros(M.Nz, 1); c = C.scale_c;
f1 = fk_forward(M, S, th(M.zone), M.R0); f2 = fk_forward(M, S, th(M.zone) + log(c), c * M.R0);
H1 = fk_solve(M, th(M.zone), M.R0); H2 = fk_solve(M, th(M.zone) + log(c), c * M.R0);
hn1 = H1(M.obsCell, 1); hn2 = H2(M.obsCell, 1);
axc = newAxes(fig, [8.0 1.2 3.0 3.6]);
lim = [0 ceil(max(hn1))];
plot(axc, lim, lim, '-', 'Color', pal.refGray, 'LineWidth', 0.8);
plot(axc, hn1, hn2, 'o', 'MarkerSize', 4, 'MarkerFaceColor', pal.blue, 'MarkerEdgeColor', 'w', 'LineWidth', 0.4);
set(axc, 'XLim', lim, 'YLim', lim, 'XTick', 0:1:lim(2), 'YTick', 0:1:lim(2)); grid(axc, 'on');
finishAxes(axc, 'head, nominal [m]', 'head, scaled [m]', false);
text(axc, 0.97, 0.04, {sprintf('K, R \\times %.1f', c), sprintf('max |\\Deltah| = %.0e m', max(abs(hn1 - hn2)))}, 'Units', 'normalized', ...
     'FontSize', fs(7.5), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', pal.ink2);
panelLabel(axc, '(c)', 1.0);
axd = newAxes(fig, [12.6 1.2 3.0 3.6]);
r1 = f1(J+1:3*J); r2 = f2(J+1:3*J); sel = r1 > 1e-3; lim2 = [1e-3 1];
plot(axd, lim2, lim2, '-', 'Color', pal.refGray, 'LineWidth', 0.8);
plot(axd, lim2, lim2 / c, '--', 'Color', pal.orange, 'LineWidth', 1.0);
plot(axd, r1(sel), r2(sel), 'o', 'MarkerSize', 4, 'MarkerFaceColor', pal.orange, 'MarkerEdgeColor', 'w', 'LineWidth', 0.4);
set(axd, 'XScale', 'log', 'YScale', 'log', 'XLim', lim2, 'YLim', lim2, 'XTick', [1e-3 1e-2 1e-1 1], 'YTick', [1e-3 1e-2 1e-1 1], ...
    'XMinorTick', 'off', 'YMinorTick', 'off'); grid(axd, 'on'); set(axd, 'XMinorGrid', 'off', 'YMinorGrid', 'off');
finishAxes(axd, 'rise, nominal [m]', 'rise, scaled [m]', false);
text(axd, 0.04, 0.97, {'Stage-0 rise', sprintf('ratio %.4f = 1/c', median(r2(sel) ./ r1(sel)))}, 'Units', 'normalized', 'FontSize', fs(7.5), ...
     'VerticalAlignment', 'top', 'Color', pal.ink2);
panelLabel(axd, '(d)', 1.35);
say(lg, 'P1c-d: c = %.2f: natural heads max|dh| %.2e m; Stage-0 ratio median %.6f (min %.6f, max %.6f) for %d items > 1 mm\n', ...
    c, max(abs(hn1 - hn2)), median(r2(sel) ./ r1(sel)), min(r2(sel) ./ r1(sel)), max(r2(sel) ./ r1(sel)), nnz(sel));
saveFigure(fig, resDir, 'figP1_model', lg);
end

% =====================================================================================================================
function figP2(L, resDir, lg)
% Robust Gittins index of Appendix D: gamma - p against p for several n; k and beta effects; convergence in 1/sqrt(n).
pal = palette(); S = L.S; Z = load(fullfile(resDir, 'prova_index_check.mat')); I = Z.I;
fig = newFigure(16, 7.9);
nn = [1 2 5 10 20 80]; cols = sequential(pal, numel(nn) + 2); cols = cols(3:end, :);
T = L.tabs.main; yl = [-0.3 0.3]; yt = [-0.2 -0.1 0 0.1 0.2];
ax = newAxes(fig, [1.45 1.2 4.1 4.6]);
plot(ax, [0 1], [0 0], '-', 'Color', pal.refGray, 'LineWidth', 0.8);
for q = 1:numel(nn)
    plot(ax, T.p, T.gam(:, nn(q)) - T.p(:), '-', 'Color', cols(q, :), 'LineWidth', 1.2);
end
for q = 1:numel(nn)                                   % compact legend, lower right
    yy = -0.105 - 0.032 * (q - 1);
    plot(ax, [0.66 0.76], [yy yy], '-', 'Color', cols(q, :), 'LineWidth', 1.2);
    text(ax, 0.79, yy, sprintf('n = %d', nn(q)), 'FontSize', fs(7), 'VerticalAlignment', 'middle', 'Color', pal.ink2);
end
set(ax, 'XLim', [0 1], 'YLim', yl, 'XTick', 0:0.25:1, 'YTick', yt); grid(ax, 'on');
finishAxes(ax, 'miss-rate estimate, p', '\gamma - p', false);
text(ax, 0.03, 0.97, sprintf('k = %.1f, \\beta = %.2f', S.k, S.beta), 'Units', 'normalized', 'FontSize', fs(8), 'VerticalAlignment', 'top');
panelLabel(ax, '(a)', 1.25);
say(lg, 'P2a: gamma-p at p = 0.3 for n = %s: %s\n', mat2str(nn), mat2str(interp1(T.p, T.gam(:, nn), 0.3) - 0.3, 3));
% (b) k effect at beta = 0.95, n = 5 and 20
ax = newAxes(fig, [6.55 1.2 4.1 4.6]);
plot(ax, [0 1], [0 0], '-', 'Color', pal.refGray, 'LineWidth', 0.8);
tb = {L.tabs.k02, L.tabs.main, L.tabs.k08}; kc = [pal.aqua; pal.blue; pal.orange]; kv = [S.kSens(1) S.k S.kSens(2)];
for a = 1:3
    plot(ax, tb{a}.p, tb{a}.gam(:, 5) - tb{a}.p(:), '-', 'Color', kc(a, :), 'LineWidth', 1.2);
    plot(ax, tb{a}.p, tb{a}.gam(:, 20) - tb{a}.p(:), '--', 'Color', kc(a, :), 'LineWidth', 1.0);
end
set(ax, 'XLim', [0 1], 'YLim', yl, 'XTick', 0:0.25:1, 'YTick', yt); grid(ax, 'on');
finishAxes(ax, 'miss-rate estimate, p', '', false);
text(ax, 0.03, 0.97, '\beta = 0.95', 'Units', 'normalized', 'FontSize', fs(8), 'VerticalAlignment', 'top');
panelLabel(ax, '(b)', 1.0);
for a = 1:3
    say(lg, 'P2b: k %.1f: gamma-p at p = 0.3, n = 5: %.4f, n = 20: %.4f\n', kv(a), interp1(tb{a}.p, tb{a}.gam(:, 5), 0.3) - 0.3, interp1(tb{a}.p, tb{a}.gam(:, 20), 0.3) - 0.3);
end
% (c) gamma - p at p = 0.3 against 1/sqrt(n): k and beta
ax = newAxes(fig, [11.6 1.2 4.1 4.6]);
x = 1 ./ sqrt(I.n);
plot(ax, [0 1], [0 0], '-', 'Color', pal.refGray, 'LineWidth', 0.8);
ik = [2 3 4]; ib = find(I.beta == 0.95);
for a = 1:3
    plot(ax, x, squeeze(I.gamMinusP(ik(a), ib, :, 2)), '-o', 'Color', kc(a, :), 'MarkerSize', 3, 'MarkerFaceColor', kc(a, :), 'LineWidth', 1.1);
end
bst = {'--', '', ':'};
for b = [1 3]
    plot(ax, x, squeeze(I.gamMinusP(3, b, :, 2)), bst{b}, 'Color', pal.blue, 'LineWidth', 1.0);
end
set(ax, 'XLim', [0 1], 'YLim', yl, 'XTick', 0:0.25:1, 'YTick', yt); grid(ax, 'on');
finishAxes(ax, '1/\surdn', '', false);
text(ax, 0.03, 0.97, 'p = 0.3', 'Units', 'normalized', 'FontSize', fs(8), 'VerticalAlignment', 'top');
panelLabel(ax, '(c)', 1.0);
for a = 1:numel(I.k)
    for b = 1:numel(I.beta)
        if any(isnan(I.gamMinusP(a, b, :, 2))), continue; end
        say(lg, 'P2c: k %.1f beta %.2f p 0.3: gamma-p over n = %s: %s\n', I.k(a), I.beta(b), mat2str(I.n), mat2str(squeeze(I.gamMinusP(a, b, :, 2))', 3));
    end
end
items = {legendItem('line', sprintf('k = %.1f', kv(1)), kc(1, :), '-', 1.2), legendItem('line', sprintf('k = %.1f', kv(2)), kc(2, :), '-', 1.2), ...
         legendItem('line', sprintf('k = %.1f', kv(3)), kc(3, :), '-', 1.2), legendItem('line', '(b) n = 5', pal.ink2, '-', 1.0), ...
         legendItem('line', '(b) n = 20', pal.ink2, '--', 1.0)};
drawLegend(fig, [1.45 7.1 14 0.5], items, 1, [2.05 2.05 2.05 2.45 2.5]);
items = {legendItem('line', '(c) k = 0.5, \beta = 0.90', pal.blue, '--', 1.0), legendItem('line', '(c) k = 0.5, \beta = 0.99', pal.blue, ':', 1.0)};
drawLegend(fig, [1.45 6.6 14 0.5], items, 1, [4.1 4.1]);
saveFigure(fig, resDir, 'figP2_index', lg);
end

% =====================================================================================================================
function figP3(L, resDir, lg)
% One truth: plays against runs, posterior miss-rate bands, index trajectories, goal intervals.
pal = palette(); S = L.S; P = load(fullfile(resDir, 'prova_demo.mat')); dm = P.demo; tr = dm.tr;
PL = dm.PL{1}; arm = PL.logArm; runs = PL.logRuns; miss = PL.logMiss;
fig = newFigure(16, 12.9);
% (a) cumulative plays against runs
ax = newAxes(fig, [1.45 6.9 6.0 3.75]);
for m = 1:5
    k = find(arm == m); if isempty(k), continue; end
    stairs(ax, [0; runs(k)], [0; (1:numel(k))'], '-', 'Color', armColor(m), 'LineWidth', 1.3);
    km = k(miss(k) == 1); [~, pos] = ismember(km, k);
    plot(ax, runs(km), pos, 'x', 'Color', armColor(m), 'MarkerSize', 4, 'LineWidth', 0.8);
end
plot(ax, [S.budget S.budget], [0 52], ':', 'Color', pal.ink2, 'LineWidth', 0.9);
text(ax, S.budget - 4, 51, sprintf('budget %d runs', S.budget), 'HorizontalAlignment', 'right', 'FontSize', fs(7.5), 'Color', pal.ink2, 'VerticalAlignment', 'top');
set(ax, 'XLim', [0 10 * ceil(S.budget * 1.05 / 10)], 'YLim', [0 52]); grid(ax, 'on');
finishAxes(ax, 'model runs used', 'plays', false);
panelLabel(ax, '(a)', 1.3);
% (b) posterior miss-rate band per arm against its items
ax = newAxes(fig, [9.55 6.9 6.0 3.75]);
plot(ax, [0 50], [0.1 0.1], '--', 'Color', pal.ink2, 'LineWidth', 0.8);
yl = [];
for m = 1:5
    k = find(arm == m); if isempty(k), continue; end
    sc = cumsum(miss(k)); n = (1:numel(k))'; aa = sc + 0.5; bb = n - sc + 0.5;
    lo = beta_q_(0.05, aa, bb); hi = beta_q_(0.95, aa, bb); pm = aa ./ (n + 1);
    if numel(n) > 1, patch(ax, [n; flipud(n)], [lo; flipud(hi)], armColor(m), 'FaceAlpha', 0.15, 'EdgeColor', 'none'); end
    plot(ax, n, pm, '-', 'Color', armColor(m), 'LineWidth', 1.3);
    if numel(n) >= 5, yl(end + 1, :) = [m pm(end) n(end)]; end %#ok<AGROW>
end
if ~isempty(yl)                                        % end labels, nudged apart
    [~, o] = sort(yl(:, 2)); yl = yl(o, :);
    for q = 2:size(yl, 1), yl(q, 4) = max(yl(q, 2), yl(q - 1, 2) + 0.06); end
    yl(1, 4) = yl(1, 2);
    for q = 1:size(yl, 1)
        text(ax, yl(q, 3) + 0.8, yl(q, 4), sprintf('A%d', yl(q, 1)), 'FontSize', fs(7.5), 'Color', armColor(yl(q, 1)), 'FontWeight', 'bold', 'VerticalAlignment', 'middle');
    end
end
text(ax, 50, 0.085, 'nominal 0.10', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'top', 'FontSize', fs(7.5), 'Color', pal.ink2);
set(ax, 'XLim', [0 55], 'YLim', [0 1], 'XTick', 0:10:50); grid(ax, 'on');
finishAxes(ax, 'items evaluated by the arm', 'miss rate', false);
panelLabel(ax, '(b)', 1.3);
% (c) index trajectories against runs
ax = newAxes(fig, [1.45 1.3 6.0 3.75]);
G = PL.logIdx; G(~isfinite(G)) = NaN;
for m = 1:5
    plot(ax, runs, G(:, m), '.-', 'Color', armColor(m), 'MarkerSize', 6, 'LineWidth', 0.9);
end
set(ax, 'XLim', [0 10 * ceil(S.budget * 1.05 / 10)], 'YLim', [0 1]); grid(ax, 'on');
finishAxes(ax, 'model runs used', 'robust Gittins index \gamma', false);
panelLabel(ax, '(c)', 1.3);
% (d) goal intervals: truth, TRIAL-GO (selected arm, all data), PEST standard, PEST all data
ax = newAxes(fig, [9.55 1.3 6.0 3.75]);
mt = {'pest_std', 'pest_all', 'trial'}; mc = [pal.orange; pal.muted; pal.blue];
for w = 1:2
    plot(ax, w + [-0.42 0.42], tr.Hfut(w) * [1 1], '-', 'Color', pal.ink, 'LineWidth', 1.6);
    for q = 1:3
        x = dm.meth.(mt{q}); xx = w + (q - 2) * 0.22;
        plot(ax, [xx xx], x.mu(w) + S.z90 * x.s(w) * [-1 1], '-', 'Color', mc(q, :), 'LineWidth', 2.2);
        plot(ax, xx, x.mu(w), 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', mc(q, :), 'LineWidth', 1.1);
    end
end
plot(ax, [0.4 2.6], S.hc * [1 1], '--', 'Color', pal.red, 'LineWidth', 0.9);
text(ax, 2.58, S.hc, 'h_c', 'Color', pal.red, 'FontSize', fs(8), 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right');
yr = [min([tr.Hfut(:); S.hc]), max(tr.Hfut(:))];
for q = 1:3, x = dm.meth.(mt{q}); yr = [min(yr(1), min(x.mu - S.z90 * x.s)), max(yr(2), max(x.mu + S.z90 * x.s))]; end
yr = [floor((yr(1) - 0.1) * 2) / 2, ceil((yr(2) + 0.1) * 2) / 2];
set(ax, 'XLim', [0.4 2.6], 'YLim', yr, 'XTick', [1 2], 'XTickLabel', {sprintf('A (%s)', L.M.supID{1}), sprintf('B (%s)', L.M.supID{2})}); grid(ax, 'on');
set(ax, 'XGrid', 'off');
finishAxes(ax, '', 'future head [m]', false);
panelLabel(ax, '(d)', 1.3);
items = {};
for m = 1:5, items{end + 1} = legendItem('line', sprintf('A%d', m), armColor(m), '-', 1.3); end %#ok<AGROW>
items{end + 1} = legendItem('marker', 'miss (item outside the 90% interval)', pal.ink2, 'x', 6, pal.ink2);
drawLegend(fig, [1.45 12.2 14.3 0.5], items, 1, [1.55 1.55 1.55 1.55 1.55 6]);
items = {legendItem('line', '(d) truth', pal.ink, '-', 1.6), legendItem('line', 'PEST standard 90%', pal.orange, '-', 2.2), ...
         legendItem('line', 'PEST all data 90%', pal.muted, '-', 2.2), legendItem('line', 'TRIAL-GO 90%', pal.blue, '-', 2.2)};
drawLegend(fig, [1.45 11.65 14.3 0.5], items, 1, [2.4 4.1 4.0 3.4]);
say(lg, 'P3: seed %d: TRIAL-GO plays %s misses %s, bandit runs %d, selected A%d, conditioning runs %d\n', tr.seed, ...
    mat2str(dm.pol.trial.n), mat2str(dm.pol.trial.s), dm.pol.trial.runs, dm.pol.trial.sel, dm.pol.trial.condRuns);
lab = {'PEST std', 'PEST all', 'TRIAL-GO'};
for q = 1:3
    x = dm.meth.(mt{q});
    say(lg, 'P3d: %-9s A %.3f [%.3f %.3f] B %.3f [%.3f %.3f] risk %.4f; truth A %.3f B %.3f risk %.4f\n', lab{q}, x.mu(1), ...
        x.mu(1) - S.z90 * x.s(1), x.mu(1) + S.z90 * x.s(1), x.mu(2), x.mu(2) - S.z90 * x.s(2), x.mu(2) + S.z90 * x.s(2), x.risk, tr.Hfut, tr.riskTrue);
end
saveFigure(fig, resDir, 'figP3_demo', lg);
end

% =====================================================================================================================
function figP4(L, resDir, lg)
% Results over all truths: coverage, runs, decision error, arm frequencies, misspecification of the arms.
pal = palette(); S = L.S;
J = jsondecode_(fullfile(resDir, 'prova_go_results.json'));
R = J.main; R2 = []; if isfield(J, 'nozeta'), R2 = J.nozeta; end
mt = {'trial', 'trial_k02', 'trial_k08', 'ucb', 'ts', 'greedy', 'bic', 'pest_std', 'pest_rch', 'pest_all', 'oracle'};
lab = {'TRIAL-GO', 'TRIAL-GO k = 0.2', 'TRIAL-GO k = 0.8', 'UCB', 'Thompson', 'greedy', 'all arms + BIC', 'PEST std. (A1)', ...
       'PEST + R (A4)', 'PEST all data (A4)', 'oracle arm'};
mc = [pal.blue; pal.lightBlue; pal.lightBlue; pal.aqua; pal.aqua; pal.aqua; pal.muted; pal.orange; pal.orange; pal.orange; pal.ink];
nm = numel(mt); y = nm:-1:1;
fig = newFigure(16, 15.8);
% (a) coverage A and B
ax = newAxes(fig, [3.6 9.0 6.0 5.55]);
plot(ax, [0.9 0.9], [0.3 nm + 0.7], '--', 'Color', pal.ink2, 'LineWidth', 0.8);
for q = 1:nm
    m = R.m.(mt{q});
    errbarH(ax, m.covA(2:3), y(q) + 0.17, mc(q, :)); plot(ax, m.covA(1), y(q) + 0.17, 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', mc(q, :), 'MarkerEdgeColor', mc(q, :));
    errbarH(ax, m.covB(2:3), y(q) - 0.17, mc(q, :)); plot(ax, m.covB(1), y(q) - 0.17, 's', 'MarkerSize', 4.5, 'MarkerFaceColor', 'w', 'MarkerEdgeColor', mc(q, :), 'LineWidth', 1.0);
    if ~isempty(R2)
        m2 = R2.m.(mt{q});
        plot(ax, m2.covA(1), y(q) + 0.17, 'd', 'MarkerSize', 3.6, 'MarkerFaceColor', pal.red, 'MarkerEdgeColor', 'w', 'LineWidth', 0.3);
        plot(ax, m2.covB(1), y(q) - 0.17, 'd', 'MarkerSize', 3.6, 'MarkerFaceColor', pal.red, 'MarkerEdgeColor', 'w', 'LineWidth', 0.3);
    end
end
set(ax, 'YLim', [0.3 nm + 0.7], 'YTick', 1:nm, 'YTickLabel', fliplr(lab), 'XLim', [0.2 1], 'XTick', 0.2:0.2:1); grid(ax, 'on'); set(ax, 'YGrid', 'off');
finishAxes(ax, 'coverage of the 90% goal intervals', '', false);
panelLabel(ax, '(a)', 3.5);
% (b) model runs
ax = newAxes(fig, [10.25 9.0 2.55 5.55]);
for q = 1:nm
    m = R.m.(mt{q}); errbarH(ax, m.runs(2:3), y(q), mc(q, :));
    plot(ax, m.runs(1), y(q), 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', mc(q, :), 'MarkerEdgeColor', mc(q, :));
end
plot(ax, [S.budget S.budget], [0.3 nm + 0.7], ':', 'Color', pal.ink2, 'LineWidth', 0.9);
set(ax, 'YLim', [0.3 nm + 0.7], 'YTick', 1:nm, 'YTickLabel', {}, 'XLim', [0 600], 'XTick', 0:200:600); grid(ax, 'on'); set(ax, 'YGrid', 'off');
finishAxes(ax, 'model runs', '', false);
panelLabel(ax, '(b)', 0.45);
% (c) decision error
ax = newAxes(fig, [13.4 9.0 2.35 5.55]);
for q = 1:nm
    m = R.m.(mt{q}); errbarH(ax, m.decErr(2:3), y(q), mc(q, :));
    plot(ax, m.decErr(1), y(q), 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', mc(q, :), 'MarkerEdgeColor', mc(q, :));
    if ~isempty(R2), plot(ax, R2.m.(mt{q}).decErr(1), y(q), 'd', 'MarkerSize', 3.6, 'MarkerFaceColor', pal.red, 'MarkerEdgeColor', 'w', 'LineWidth', 0.3); end
end
set(ax, 'YLim', [0.3 nm + 0.7], 'YTick', 1:nm, 'YTickLabel', {}, 'XLim', [0 0.4], 'XTick', 0:0.2:0.4); grid(ax, 'on'); set(ax, 'YGrid', 'off');
finishAxes(ax, 'decision error', '', false);
panelLabel(ax, '(c)', 0.45);
items = {legendItem('marker', 'supply well A', pal.ink2, 'o', 4.5, pal.ink2), legendItem('marker', 'supply well B', 'w', 's', 4.5, pal.ink2), ...
         legendItem('line', 'nominal', pal.ink2, '--', 0.8), legendItem('marker', 'run without sub-zonal field', pal.red, 'd', 4, 'w')};
drawLegend(fig, [1.45 15.1 14.4 0.45], items, 1, [3.0 3.0 2.3 5]);
% (d) arm-selection frequency
ax = newAxes(fig, [1.45 1.55 7.4 5.15]);
ms = {'trial', 'ucb', 'ts', 'greedy', 'bic', 'oracle'}; ls = {'TRIAL-GO', 'UCB', 'Thomp.', 'greedy', 'BIC', 'oracle'};
F = zeros(numel(ms), 5);
for q = 1:numel(ms), F(q, :) = R.m.(ms{q}).armFreq(:)' / R.n; end
for q = 1:numel(ms)
    b0 = 0;
    for m = 1:5
        patch(ax, q + 0.34 * [-1 1 1 -1], b0 + [0 0 F(q, m) F(q, m)], armColor(m), 'EdgeColor', 'w', 'LineWidth', 0.5);
        if F(q, m) >= 0.07
            text(ax, q, b0 + F(q, m) / 2, sprintf('%.0f', 100 * F(q, m)), 'HorizontalAlignment', 'center', 'FontSize', fs(7), 'Color', 'w');
        end
        b0 = b0 + F(q, m);
    end
    text(ax, q, -0.035, ls{q}, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', 'FontSize', fs(7.5));
end
set(ax, 'XLim', [0.4 numel(ms) + 0.6], 'YLim', [0 1], 'XTick', 1:numel(ms), 'XTickLabel', {}, 'YTick', 0:0.25:1);
grid(ax, 'on'); set(ax, 'XGrid', 'off');
finishAxes(ax, '', 'fraction of truths', false);
panelLabel(ax, '(d)', 1.25);
items = {};
for m = 1:5, items{end + 1} = legendItem('patch', sprintf('A%d', m), armColor(m), '', 1); end %#ok<AGROW>
drawLegend(fig, [1.45 7.25 7.4 0.45], items, 1, [1.45 1.45 1.45 1.45 1.45]);
% (e) validation miss rate of each arm at convergence on the heads
ax = newAxes(fig, [10.6 1.55 5.15 5.15]);
plot(ax, [0.4 5.6], [0.1 0.1], '--', 'Color', pal.ink2, 'LineWidth', 0.8);
for m = 1:5
    patch(ax, m - 0.36 + [0 0.34 0.34 0], [0 0 1 1] * R.missConv.strip(m), armColor(m), 'EdgeColor', 'none');
    patch(ax, m + 0.02 + [0 0.34 0.34 0], [0 0 1 1] * R.missConv.nostrip(m), 'w', 'EdgeColor', armColor(m), 'LineWidth', 1.0);
    if ~isempty(R2)
        plot(ax, m - 0.19, R2.missConv.strip(m), 'd', 'MarkerSize', 3.6, 'MarkerFaceColor', pal.red, 'MarkerEdgeColor', 'w', 'LineWidth', 0.3);
        plot(ax, m + 0.19, R2.missConv.nostrip(m), 'd', 'MarkerSize', 3.6, 'MarkerFaceColor', pal.red, 'MarkerEdgeColor', 'w', 'LineWidth', 0.3);
    end
end
set(ax, 'XLim', [0.4 5.6], 'YLim', [0 0.5], 'XTick', 1:5, 'XTickLabel', {'A1', 'A2', 'A3', 'A4', 'A5'}, 'YTick', 0:0.1:0.5);
grid(ax, 'on'); set(ax, 'XGrid', 'off');
finishAxes(ax, '', 'miss rate at convergence', false);
panelLabel(ax, '(e)', 1.25);
items = {legendItem('patch', 'strip truths', pal.muted, '', 1), legendItem('patch', 'no strip', 'w', '', 1, pal.muted)};
drawLegend(fig, [10.6 7.25 5.2 0.45], items, 1, [2.7 2.3]);
say(lg, 'P4: n = %d truths; coverage A/B, runs, decision error per method:\n', R.n);
for q = 1:nm
    m = R.m.(mt{q});
    say(lg, '   %-18s covA %.3f [%.3f %.3f] covB %.3f [%.3f %.3f] runs %.1f decErr %.3f [%.3f %.3f]\n', lab{q}, m.covA, m.covB, m.runs(1), m.decErr);
end
say(lg, 'P4d: selection fractions (A1..A5) for %s: %s\n', strjoin(ls, ', '), mat2str(F, 3));
say(lg, 'P4e: miss rate at convergence strip %s, no strip %s\n', mat2str(R.missConv.strip(:)', 3), mat2str(R.missConv.nostrip(:)', 3));
saveFigure(fig, resDir, 'figP4_results', lg);
end

% =====================================================================================================================
function figP5(L, resDir, lg)
% MAR process maps on the demonstration truth: current, planned, planned + MAR (3 and 6 wells), MAR mound.
pal = palette(); M = L.M; S = L.S; Q = load(fullfile(resDir, 'prova_mar.mat')); T = Q.T;
fig = newFigure(17, 24.2);
F3 = T.true3; F6 = T.true6; n3 = numel(F3.sites); n6 = numel(F6.sites);
fields = {F3.cur, F3.plan, F3.mar, F6.mar};
ttl = {'current pumping', 'planned pumping', sprintf('planned + %d MAR wells', n3), sprintf('planned + %d MAR wells', n6)};
sites = {[], [], F3.sites, F6.sites};
cl = [S.hc 7]; wm = 21 * 9.7 / 52.5;
pos = [1.35 13.3 wm 9.7; 1.35 + wm + 0.35 13.3 wm 9.7; 1.35 + 2 * (wm + 0.35) 13.3 wm 9.7; 1.35 1.4 wm 9.7];
for p = 1:4
    ax = newAxes(fig, pos(p, :));
    mapHeads(ax, M, S, fields{p}, cl, pal);
    wellsOut(ax, M, pal);
    if ~isempty(sites{p}), marWells(ax, M, sites{p}, pal); end
    set(ax, 'XLim', [0 21], 'YLim', [0 52.5], 'DataAspectRatio', [1 1 1], 'XTick', 0:5:20, 'YTick', 0:10:50);
    if p == 1 || p == 4, finishAxes(ax, 'E [km]', 'N [km]', true); off = 1.2; else, finishAxes(ax, 'E [km]', '', true); set(ax, 'YTickLabel', {}); off = 0.3; end
    mapTitle(ax, ttl{p});
    if p == 1, northArrow(ax, 19.3, 44.5, 4.0); scaleBar(ax, 0.8, 2.2, 5); end
    panelLabel(ax, char('(a)' + [0 p - 1 0]), off);
end
colorbarV(fig, [pos(3, 1) + wm + 0.45 15.6 0.25 5.0], turbo(256), cl, {'head h', '[m]'});
% (e) mound of the 6-well MAR configuration
ax = newAxes(fig, [pos(2, 1) 1.4 wm 9.7]);
cm = sequential(pal, 256); clm = [0 ceil(max(F6.mound))];
drawField(ax, M, F6.mound, cm, clm);
G = nan(M.ny, M.nx); G(M.act) = F6.mound;
contour(ax, M.xs, M.ys, G, [0.25 0.5 1 2 3 4], 'LineColor', [1 1 1] * 0.35, 'LineWidth', 0.45);
plot(ax, M.Bk(:, 1), M.Bk(:, 2), '-', 'Color', pal.ink, 'LineWidth', 0.9); coastLine(ax, M, coastBlue(), 1.8);
wellsOut(ax, M, pal); marWells(ax, M, F6.sites, pal);
set(ax, 'XLim', [0 21], 'YLim', [0 52.5], 'DataAspectRatio', [1 1 1], 'XTick', 0:5:20, 'YTick', 0:10:50, 'YTickLabel', {});
finishAxes(ax, 'E [km]', '', true);
mapTitle(ax, 'head rise by MAR');
panelLabel(ax, '(e)', 0.3);
colorbarV(fig, [pos(2, 1) + wm + 0.45 3.2 0.25 5.0], cm, clm, {'\Deltah', '[m]'});
% side legend panel
legendPanel(fig, [11.35 1.4 5.45 9.7], M, S, pal, T);
say(lg, 'P5: intruded area current %.2f, planned %.2f, planned+MAR%d %.2f, planned+MAR%d %.2f km^2; mound max %.2f m; risks %.4f -> %.4f / %.4f\n', ...
    F3.areaCur, F3.areaPlan, n3, F3.areaMar, n6, F6.areaMar, max(F6.mound), F3.riskPlan, F3.riskMar, F6.riskMar);
saveFigure(fig, resDir, 'figP5_mar_process', lg);
end

% =====================================================================================================================
function figP6(L, resDir, lg)
% Why the structure matters: true vs predicted toe for PEST standard and TRIAL-GO, their MAR sites, risks and areas.
pal = palette(); M = L.M; S = L.S; Q = load(fullfile(resDir, 'prova_mar.mat')); T = Q.T;
fig = newFigure(17, 13.4); wm = 21 * 9.7 / 52.5; cl = [S.hc 7];
mm = {'pest', 'trial'}; mlab = {'PEST standard (A1)', sprintf('TRIAL-GO (A%d)', T.trialArm)}; mcol = [pal.orange; pal.blue];
for p = 1:2
    ax = newAxes(fig, [1.35 + (p - 1) * (wm + 0.35) 1.4 wm 9.7]);
    D = T.(mm{p});
    mapHeads(ax, M, S, D.trueF.mar, cl, pal);
    Gp = nan(M.ny, M.nx); Gp(M.act) = D.predF.mar;
    contour(ax, M.xs, M.ys, Gp, [S.hc S.hc], 'LineColor', mcol(p, :), 'LineStyle', '-', 'LineWidth', 1.6);
    wellsOut(ax, M, pal); marWells(ax, M, D.sites, pal);
    set(ax, 'XLim', [0 21], 'YLim', [0 52.5], 'DataAspectRatio', [1 1 1], 'XTick', 0:5:20, 'YTick', 0:10:50);
    if p == 1, finishAxes(ax, 'E [km]', 'N [km]', true); off = 1.2; else, finishAxes(ax, 'E [km]', '', true); set(ax, 'YTickLabel', {}); off = 0.3; end
    mapTitle(ax, mlab{p}, mcol(p, :));
    if p == 1, northArrow(ax, 19.3, 44.5, 4.0); scaleBar(ax, 0.8, 2.2, 5); end
    panelLabel(ax, char('(a)' + [0 p - 1 0]), off);
end
colorbarV(fig, [1.35 + wm + 0.35 + 15.3 * wm / 21, 1.4 + 19.5 * 9.7 / 52.5, 0.22, 3.0], turbo(256), cl, {'true head', '[m]'});
% (c) risk and (d) area: predicted (open) vs true (filled) for both designs
ax = newAxes(fig, [11.95 6.6 4.75 3.85]);
for p = 1:2
    D = T.(mm{p});
    bar_(ax, p - 0.2, D.predRisk, mcol(p, :), 'w'); bar_(ax, p + 0.2, D.trueRisk, mcol(p, :), mcol(p, :));
    text(ax, p - 0.2, D.predRisk + 0.025, sprintf('%.2f', D.predRisk), 'HorizontalAlignment', 'center', 'FontSize', fs(7), 'VerticalAlignment', 'bottom');
    text(ax, p + 0.2, D.trueRisk + 0.025, sprintf('%.2f', D.trueRisk), 'HorizontalAlignment', 'center', 'FontSize', fs(7), 'VerticalAlignment', 'bottom');
end
set(ax, 'XLim', [0.4 2.6], 'XTick', [1 2], 'XTickLabel', {'PEST std.', 'TRIAL-GO'}, 'YLim', [0 1], 'YTick', 0:0.25:1);
grid(ax, 'on'); set(ax, 'XGrid', 'off'); finishAxes(ax, '', 'P(A or B intruded)', false);
panelLabel(ax, '(c)', 1.3);
ax = newAxes(fig, [11.95 1.4 4.75 3.85]);
for p = 1:2
    D = T.(mm{p});
    bar_(ax, p - 0.2, D.predArea, mcol(p, :), 'w'); bar_(ax, p + 0.2, D.trueArea, mcol(p, :), mcol(p, :));
    text(ax, p - 0.2, D.predArea + 1, sprintf('%.1f', D.predArea), 'HorizontalAlignment', 'center', 'FontSize', fs(7), 'VerticalAlignment', 'bottom');
    text(ax, p + 0.2, D.trueArea + 1, sprintf('%.1f', D.trueArea), 'HorizontalAlignment', 'center', 'FontSize', fs(7), 'VerticalAlignment', 'bottom');
end
ymax = 10 * ceil(max([T.pest.predArea T.pest.trueArea T.trial.predArea T.trial.trueArea]) / 10 + 0.2);
set(ax, 'XLim', [0.4 2.6], 'XTick', [1 2], 'XTickLabel', {'PEST std.', 'TRIAL-GO'}, 'YLim', [0 ymax]);
grid(ax, 'on'); set(ax, 'XGrid', 'off'); finishAxes(ax, '', 'intruded area [km^2]', false);
panelLabel(ax, '(d)', 1.3);
items = {legendItem('line', 'true toe (h = h_c)', pal.ink, '--', 1.8), legendItem('line', 'toe, PEST std. model', pal.orange, '-', 1.6), ...
         legendItem('line', 'toe, TRIAL-GO model', pal.blue, '-', 1.6), legendItem('patch', 'intruded zone (true)', intrudedTint(), '', 1, pal.muted), ...
         legendItem('marker', 'supply well (out)', pal.ink, 'v', 6, 'w'), legendItem('marker', 'MAR well (in)', marGreen(), 'd', 6, 'w'), ...
         legendItem('patch', 'predicted (c, d)', 'w', '', 1, pal.ink2), legendItem('patch', 'true (c, d)', pal.muted, '', 1, pal.muted)};
drawLegend(fig, [1.35 11.85 15.6 1.3], items, 2, [4.15 4.15 3.5 3.3]);
for p = 1:2
    D = T.(mm{p});
    say(lg, 'P6: %s: sites %s; risk predicted %.4f true %.4f; area predicted %.2f true %.2f km^2\n', mlab{p}, mat2str(D.sites), D.predRisk, D.trueRisk, D.predArea, D.trueArea);
end
saveFigure(fig, resDir, 'figP6_structure_mar', lg);
end

% =====================================================================================================================
function figP7(L, resDir, lg)
% W-E section through supply well A: sharp-interface (Ghyben-Herzberg) wedge from the model heads; head profiles.
pal = palette(); M = L.M; S = L.S; Q = load(fullfile(resDir, 'prova_mar.mat')); X = Q.X;
fig = newFigure(16, 12.5);
x = X.x; base = -M.P.base; xe = 10; sel = x <= xe + 0.3; x = x(sel);
sea = [0.66 0.83 0.92]; wedge = [0.36 0.58 0.78]; g = marGreen();
cs = {'cur', 'plan', 'mar'}; cc = [pal.muted; pal.red; g];
ax = newAxes(fig, [1.7 5.35 13.8 5.2]);
patch(ax, [-1.0 0 0 -1.0], [base base 0 0], sea, 'EdgeColor', 'none');
patch(ax, [0 xe xe 0], [base base base - 4 base - 4], [0.60 0.58 0.56], 'EdgeColor', 'none');
zP = X.zi.plan(sel);
patch(ax, [x fliplr(x)], [zP base * ones(size(x))], wedge, 'EdgeColor', 'none');
for q = 1:3
    zi = X.zi.(cs{q})(sel);
    plot(ax, x, zi, '-', 'Color', cc(q, :), 'LineWidth', 1.6);
    t = X.toe.(cs{q}); if isfinite(t), plot(ax, t, base, '^', 'MarkerSize', 6, 'MarkerFaceColor', cc(q, :), 'MarkerEdgeColor', 'w'); end
end
plot(ax, [-1 xe], [0 0], '-', 'Color', pal.ink2, 'LineWidth', 0.6);
plot(ax, [0 xe], [base base], '-', 'Color', pal.ink, 'LineWidth', 0.8);
xw = X.xA; ztop = 4;
plot(ax, [xw xw], [base + 1 ztop], '-', 'Color', pal.ink, 'LineWidth', 1.4);
arrowV(ax, xw, ztop + 7, ztop + 1.0, pal.ink);
text(ax, xw - 0.12, ztop + 6, {sprintf('supply well A (%s)', M.supID{1}), sprintf('pumping out, %.0f m^3 d^{-1}', S.Q(1))}, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle', 'FontSize', fs(7.5));
for q = 1:numel(X.xMar)
    xm = X.xMar(q);
    plot(ax, [xm xm], [base + 1 ztop], '-', 'Color', g, 'LineWidth', 1.4);
    arrowV(ax, xm, ztop + 1.0, ztop + 7, g);
    text(ax, xm + 0.12, ztop + 6, {'MAR well', sprintf('injection in, %.0f m^3 d^{-1}', X.qSite)}, 'HorizontalAlignment', 'left', ...
         'VerticalAlignment', 'middle', 'FontSize', fs(7.5), 'Color', g);
end
text(ax, -0.5, base / 2, 'sea', 'Rotation', 90, 'HorizontalAlignment', 'center', 'FontSize', fs(8), 'Color', [0.13 0.33 0.52]);
text(ax, 0.12, base + 7, {'seawater', 'wedge'}, 'FontSize', fs(7.5), 'FontWeight', 'bold', 'Color', 'w', 'VerticalAlignment', 'middle');
gh = 40 * [X.hA.cur X.hA.plan X.hA.mar];
text(ax, 6.35, -18, {'interface depth below A (40 h):', sprintf('%.0f m current, %.0f m planned,', gh(1), gh(2)), ...
     sprintf('%.0f m planned + MAR; base %.0f m', gh(3), M.P.base)}, 'FontSize', fs(7.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle');
set(ax, 'XLim', [-1.0 xe], 'YLim', [base - 4 ztop + 10], 'XTick', 0:1:xe, 'YTick', -40:10:0);
grid(ax, 'on');
finishAxes(ax, '', 'elevation [m a.s.l.]', false);
text(ax, 0.995, 0.17, sprintf('vertical exaggeration \\approx %.0f\\times', X.ve), 'Units', 'normalized', 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'bottom', 'FontSize', fs(7.5), 'Color', pal.ink2);
panelLabel(ax, '(a)', 1.5);
% (b) head profiles
ax = newAxes(fig, [1.7 1.35 13.8 2.75]);
plot(ax, [0 xe], S.hc * [1 1], '--', 'Color', pal.ink, 'LineWidth', 0.9);
for q = 1:3, plot(ax, x, X.h.(cs{q})(sel), '-', 'Color', cc(q, :), 'LineWidth', 1.4); end
plot(ax, xw, X.hA.plan, 'v', 'MarkerSize', 6, 'MarkerFaceColor', pal.ink, 'MarkerEdgeColor', 'w');
for q = 1:numel(X.xMar), plot(ax, X.xMar(q), interp1(x, X.h.mar(sel), X.xMar(q)), 'd', 'MarkerSize', 6, 'MarkerFaceColor', g, 'MarkerEdgeColor', 'w'); end
text(ax, xe - 0.05, S.hc, 'h_c', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom', 'FontSize', fs(8));
hm = max(cellfun(@(c) max(X.h.(c)(sel)), cs));
set(ax, 'XLim', [-1.0 xe], 'YLim', [0 ceil(hm)], 'XTick', 0:1:xe); grid(ax, 'on');
finishAxes(ax, sprintf('distance from the coast along N = %.2f km [km]', X.N), 'head [m]', false);
panelLabel(ax, '(b)', 1.5);
items = {legendItem('line', 'current pumping', pal.muted, '-', 1.6), legendItem('line', 'planned pumping', pal.red, '-', 1.6), ...
         legendItem('line', 'planned + MAR', g, '-', 1.6), legendItem('marker', 'toe (h = h_c)', pal.ink2, '^', 6, 'w')};
drawLegend(fig, [1.7 11.75 13.8 0.5], items, 1, [3.4 3.4 3.2 3]);
say(lg, 'P7: section N = %.2f km: toe at %.2f (current), %.2f (planned), %.2f km (planned + MAR) from the coast; GH depth below A %s m; VE %.0f\n', ...
    X.N, X.toe.cur, X.toe.plan, X.toe.mar, mat2str(gh, 3), X.ve);
saveFigure(fig, resDir, 'figP7_section', lg);
end

% =====================================================================================================================
% ---- map helpers ------------------------------------------------------------------------------------------------------
function drawField(ax, M, v, cmap, clim, categorical)
% Cell values V drawn as one patch of flat-coloured cells (vector output in PDF): colour map CMAP over CLIM, or the
% category index when CATEGORICAL; nothing is drawn outside the aquifer (white background).
if nargin < 6, categorical = false; end
n = size(cmap, 1); v = v(:);
if categorical, k = round(v - clim(1) + 0.5); else, k = 1 + round((min(max(v, clim(1)), clim(2)) - clim(1)) / diff(clim) * (n - 1)); end
k = min(max(k, 1), n);
cellPatch(ax, M, cmap(k, :));
end
function cellPatch(ax, M, C)
% One patch with a square face per active cell, face colours C (Nc-by-3).
d = M.dx / 2; X = M.X(:); Y = M.Y(:); Nc = numel(X);
V = [X - d Y - d; X + d Y - d; X + d Y + d; X - d Y + d];
F = [(1:Nc)' (Nc + 1:2 * Nc)' (2 * Nc + 1:3 * Nc)' (3 * Nc + 1:4 * Nc)'];
patch('Parent', ax, 'Faces', F, 'Vertices', V, 'FaceVertexCData', C, 'FaceColor', 'flat', 'EdgeColor', 'none');
set(ax, 'Color', 'w');
end
function mapHeads(ax, M, S, h, cl, pal)
% Head field (turbo over CL) with the intruded zone h < h_c tinted, light head contours, the toe (h = h_c, black
% dashed), the polygon outline (black) and the coast (blue).
cm = turbo(256); k = 1 + round((min(max(h(:), cl(1)), cl(2)) - cl(1)) / diff(cl) * 255);
C = cm(k, :); in = h(:) < S.hc; C(in, :) = repmat(intrudedTint(), nnz(in), 1);
cellPatch(ax, M, C);
G = nan(M.ny, M.nx); G(M.act) = h;
contour(ax, M.xs, M.ys, G, [2 3 4 5 6 8 10], 'LineColor', [1 1 1] * 0.95, 'LineWidth', 0.35);
contour(ax, M.xs, M.ys, G, [S.hc S.hc], 'LineColor', pal.ink, 'LineStyle', '--', 'LineWidth', 1.8);
plot(ax, M.Bk(:, 1), M.Bk(:, 2), '-', 'Color', pal.ink, 'LineWidth', 0.9);
coastLine(ax, M, coastBlue(), 1.8);
end
function mapTitle(ax, s, col)
if nargin < 3, col = [0.1 0.1 0.1]; end
text(ax, 0.5, 1.012, s, 'Units', 'normalized', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontSize', fs(8), 'Color', col);
end
function c = intrudedTint(k)
t = [0.80 0.86 0.93]; if nargin, c = t(k); else, c = t; end
end
function c = coastBlue()
c = [0.05 0.25 0.65];
end
function c = marGreen()
c = [0.13 0.63 0.30];
end
function coastLine(ax, M, col, lw)
c = M.cst; [~, o] = sort(M.Y(c)); c = c(o); d = M.dx / 2;
x = reshape([M.X(c)' - d; M.X(c)' - d], 1, []); y = reshape([M.Y(c)' - d; M.Y(c)' + d], 1, []);
plot(ax, x, y, '-', 'Color', col, 'LineWidth', lw);
end
function wellsOut(ax, M, pal)
plot(ax, M.X(M.supCell), M.Y(M.supCell), 'v', 'MarkerSize', 7, 'MarkerFaceColor', pal.ink, 'MarkerEdgeColor', 'w', 'LineWidth', 0.6);
lab = {'A', 'B'};
for q = 1:2
    k = M.supCell(q);
    text(ax, M.X(k) - 0.9, M.Y(k), lab{q}, 'FontWeight', 'bold', 'FontSize', fs(7.5), 'Color', pal.ink, ...
         'BackgroundColor', 'w', 'Margin', 0.5, 'VerticalAlignment', 'middle', 'HorizontalAlignment', 'right');
end
end
function marWells(ax, M, sites, ~)
g = marGreen();
for q = 1:numel(sites)
    k = sites(q);
    plot(ax, M.X(k), M.Y(k), 'd', 'MarkerSize', 7.5, 'MarkerFaceColor', g, 'MarkerEdgeColor', 'w', 'LineWidth', 0.6);
    text(ax, M.X(k) + 0.9, M.Y(k), sprintf('%d', q), 'FontWeight', 'bold', 'FontSize', fs(7), 'Color', g, ...
         'BackgroundColor', 'w', 'Margin', 0.5, 'VerticalAlignment', 'middle');
end
end
function northArrow(ax, x, y, len)
patch(ax, x + [-0.9 0 0.9 0], y + len * [0.55 1 0.55 0.7], [0.1 0.1 0.1], 'EdgeColor', 'none');
plot(ax, [x x], [y y + 0.7 * len], '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.4);
text(ax, x, y - 0.4, 'N', 'FontSize', fs(8.5), 'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');
end
function scaleBar(ax, x, y, len)
plot(ax, [x x + len], [y y], 'k-', 'LineWidth', 1.8);
plot(ax, [x x], [y - 0.5 y + 0.5], 'k-', 'LineWidth', 1.0); plot(ax, [x + len x + len], [y - 0.5 y + 0.5], 'k-', 'LineWidth', 1.0);
text(ax, x + len / 2, y + 0.8, sprintf('%d km', len), 'FontSize', fs(7.5), 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
end
function legendPanel(fig, pos, M, S, pal, T)
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos); hold(ax, 'on');
set(ax, 'XLim', [0 pos(3)], 'YLim', [0 pos(4)], 'XTick', [], 'YTick', [], 'Box', 'on', 'XColor', [0.75 0.75 0.75], ...
    'YColor', [0.75 0.75 0.75], 'Color', [0.985 0.985 0.985]);
W = pos(3); y = pos(4) - 0.35; dl = 0.36; xs = 0.25; xt = 0.75; g = marGreen();
F3 = T.true3; F6 = T.true6; n3 = numel(F3.sites); n6 = numel(F6.sites);
    function_head = @(yy, s) text(ax, W / 2, yy, s, 'FontSize', fs(7.5), 'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
function_head(y, 'PUMPING OUT'); y = y - dl;
plot(ax, xs + 0.2, y, 'v', 'MarkerSize', 7, 'MarkerFaceColor', pal.ink, 'MarkerEdgeColor', 'w');
text(ax, xt, y, 'supply well (extraction)', 'FontSize', fs(7), 'VerticalAlignment', 'middle'); y = y - dl;
text(ax, xt, y, sprintf('A %s: %.0f / %.0f m^3 d^{-1}', M.supID{1}, S.Q0(1), S.Q(1)), 'FontSize', fs(6.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - 0.3;
text(ax, xt, y, sprintf('B %s: %.0f / %.0f m^3 d^{-1}', M.supID{2}, S.Q0(2), S.Q(2)), 'FontSize', fs(6.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - 0.3;
text(ax, xt, y, '(current / planned)', 'FontSize', fs(6.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - 0.45;
plot(ax, [0.2 W - 0.2], [y y], '-', 'Color', [0.8 0.8 0.8]); y = y - 0.35;
function_head(y, 'PUMPING IN (MAR)'); y = y - dl;
plot(ax, xs + 0.2, y, 'd', 'MarkerSize', 7.5, 'MarkerFaceColor', g, 'MarkerEdgeColor', 'w');
text(ax, xt, y, 'injection well, number', 'FontSize', fs(7), 'VerticalAlignment', 'middle'); y = y - dl;
text(ax, xt, y, sprintf('%.0f m^3 d^{-1} each; PRAG-MAR', T.qSite), 'FontSize', fs(6.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - 0.3;
text(ax, xt, y, sprintf('sites of the TRIAL-GO model (A%d)', T.trialArm), 'FontSize', fs(6.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - 0.45;
plot(ax, [0.2 W - 0.2], [y y], '-', 'Color', [0.8 0.8 0.8]); y = y - 0.35;
function_head(y, 'SEAWATER WEDGE'); y = y - dl;
plot(ax, [xs xs + 0.4], [y y], '--', 'Color', pal.ink, 'LineWidth', 1.6);
text(ax, xt, y, sprintf('toe: h = h_c = %.1f m', S.hc), 'FontSize', fs(7), 'VerticalAlignment', 'middle'); y = y - 0.3;
text(ax, xt, y, '(interface at the aquifer base)', 'FontSize', fs(6.5), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - dl;
patch(ax, xs + [0 0.4 0.4 0], y + 0.1 * [-1 -1 1 1], intrudedTint(), 'EdgeColor', pal.muted);
text(ax, xt, y, 'intruded zone, h < h_c', 'FontSize', fs(7), 'VerticalAlignment', 'middle'); y = y - dl;
plot(ax, [xs xs + 0.4], [y y], '-', 'Color', coastBlue(), 'LineWidth', 1.8);
text(ax, xt, y, 'coast (h = 0)', 'FontSize', fs(7), 'VerticalAlignment', 'middle'); y = y - dl;
patch(ax, xs + [0 0.4 0.4 0], y + 0.1 * [-1 -1 1 1], [0.55 0.55 0.55], 'EdgeColor', 'none');
plot(ax, [xs xs + 0.4], [y y], '-', 'Color', [0.95 0.95 0.95], 'LineWidth', 0.5);
text(ax, xt, y, 'head contours 2, 3, 4, 5, 6 m', 'FontSize', fs(7), 'VerticalAlignment', 'middle'); y = y - 0.45;
plot(ax, [0.2 W - 0.2], [y y], '-', 'Color', [0.8 0.8 0.8]); y = y - 0.35;
function_head(y, 'TRUE AQUIFER'); y = y - dl;
rows = {'', 'area [km^2]', 'P(A or B)'; 'current', sprintf('%.1f', F3.areaCur), '-'; 'planned', sprintf('%.1f', F3.areaPlan), sprintf('%.2f', F3.riskPlan); ...
        sprintf('+ %d MAR', n3), sprintf('%.1f', F3.areaMar), sprintf('%.3f', F3.riskMar); sprintf('+ %d MAR', n6), sprintf('%.1f', F6.areaMar), sprintf('%.3f', F6.riskMar)};
cx = [0.25 2.35 4.2];
for r = 1:size(rows, 1)
    for c = 1:3
        if c == 1, ha = 'left'; else, ha = 'center'; end
        fw = 'normal'; if r == 1, fw = 'bold'; end
        text(ax, cx(c) + (c > 1) * 0.35, y, rows{r, c}, 'FontSize', fs(6.8), 'HorizontalAlignment', ha, 'VerticalAlignment', 'middle', 'FontWeight', fw);
    end
    y = y - 0.31;
end
text(ax, 0.25, y - 0.05, sprintf('seed %d; P(A or B intruded) over the', T.seed), 'FontSize', fs(6.2), 'Color', pal.ink2, 'VerticalAlignment', 'middle'); y = y - 0.28;
text(ax, 0.25, y - 0.05, 'future recharge change, exact', 'FontSize', fs(6.2), 'Color', pal.ink2, 'VerticalAlignment', 'middle');
end
function bar_(ax, x, v, edgeCol, faceCol)
patch(ax, x + 0.18 * [-1 1 1 -1], [0 0 v v], faceCol, 'EdgeColor', edgeCol, 'LineWidth', 1.0);
end
function errbarH(ax, ci, y, col)
plot(ax, ci, [y y], '-', 'Color', col, 'LineWidth', 1.3);
end
function arrowV(ax, x, y0, y1, col)
plot(ax, [x x], [y0 y1], '-', 'Color', col, 'LineWidth', 1.4);
if y1 < y0, mk = 'v'; else, mk = '^'; end
plot(ax, x, y1, mk, 'MarkerSize', 5.5, 'MarkerFaceColor', col, 'MarkerEdgeColor', col);
end
function c = armColor(m)
pal = palette();
C = [pal.orange; pal.muted; [204 121 167] / 255; pal.blue; pal.aqua];
c = C(m, :);
end
function C = lines_(n)
base = [0.80 0.86 0.94; 0.93 0.85 0.78; 0.82 0.92 0.86; 0.92 0.84 0.90; 0.88 0.88 0.80; 0.78 0.88 0.92];
C = base(mod((0:n - 1), size(base, 1)) + 1, :);
end
function q = beta_q_(prob, a, b)
lo = zeros(size(a)); hi = ones(size(a));
for it = 1:50, x = 0.5 * (lo + hi); up = betainc(x, a, b) < prob; lo(up) = x(up); hi(~up) = x(~up); end
q = 0.5 * (lo + hi);
end
function J = jsondecode_(f)
J = jsondecode(fileread(f));
end
function colorbarV(fig, pos, cmap, lim, label)
% Vertical colour scale drawn with patches; LABEL (string or cell of lines) above the bar.
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos); hold(ax, 'on');
n = size(cmap, 1); v = linspace(lim(1), lim(2), n + 1);
for k = 1:n
    patch('Parent', ax, 'XData', [0 1 1 0], 'YData', [v(k) v(k) v(k + 1) v(k + 1)], 'FaceColor', cmap(k, :), 'EdgeColor', 'none');
end
set(ax, 'XLim', [0 1], 'YLim', lim, 'XTick', [], 'YAxisLocation', 'right', 'Box', 'on', 'Layer', 'top', 'TickDir', 'out', ...
    'FontName', 'Helvetica', 'FontSize', fs(8), 'LineWidth', 0.5, 'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15], 'TickLength', [0.08 0.08]);
text(ax, 0.5, 1.03, label, 'Units', 'normalized', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontName', 'Helvetica', 'FontSize', fs(8));
end

% ---- helpers copied from experiments/spiranca_go/certain_coast/matlab_figs/run_all_figures.m --------------------------
function pal = palette()
% Categorical colours in a fixed order (blue, orange, aqua), status red for events, neutral inks and greys,
% and a one-hue (blue) sequential ramp, light to dark.
pal.blue = [42 120 214] / 255;
pal.lightBlue = [134 182 239] / 255;
pal.darkBlue = [24 79 149] / 255;
pal.orange = [235 104 52] / 255;
pal.aqua = [27 175 122] / 255;
pal.red = [208 59 59] / 255;
pal.ink = [11 11 11] / 255;
pal.ink2 = [82 81 78] / 255;
pal.muted = [137 135 129] / 255;
pal.refGray = [178 177 170] / 255;
pal.barGray = [195 194 183] / 255;
pal.dotGray = [160 159 152] / 255;
pal.spanGray = [240 239 236] / 255;
pal.alarmTint = [254 236 196] / 255;
pal.zoneTint = [252 228 214] / 255;
pal.grid = [225 224 217] / 255;
pal.ramp = [205 226 251; 183 211 246; 158 197 244; 134 182 239; 109 167 236; 85 152 231; 57 135 229; ...
            42 120 214; 37 106 191; 28 92 171; 24 79 149; 16 66 129; 13 54 107] / 255;
end
function cmap = sequential(pal, n)
cmap = interp1(linspace(0, 1, size(pal.ramp, 1)).', pal.ramp, linspace(0, 1, n).');
end
function fig = newFigure(w, h)
fig = figure('Visible', 'off', 'Color', 'w', 'Units', 'centimeters', 'Position', [2 2 w h], ...
             'PaperUnits', 'centimeters', 'PaperSize', [w h], 'PaperPosition', [0 0 w h], ...
             'PaperPositionMode', 'manual', 'InvertHardcopy', 'off', ...
             'DefaultAxesFontName', 'Helvetica', 'DefaultAxesFontSize', fs(9), ...
             'DefaultTextFontName', 'Helvetica', 'DefaultTextFontSize', fs(9), ...
             'DefaultAxesLineWidth', 0.5, 'DefaultLineLineWidth', 1.0, 'DefaultAxesTickDir', 'out', ...
             'DefaultAxesXColor', [0.15 0.15 0.15], 'DefaultAxesYColor', [0.15 0.15 0.15], ...
             'DefaultTextColor', [0.1 0.1 0.1]);
if isprop(fig, 'Theme')
    set(fig, 'Theme', 'light');
end
end
function ax = newAxes(fig, pos)
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos);
hold(ax, 'on');
end
function finishAxes(ax, xl, yl, isMap)
pal = palette();
set(ax, 'FontName', 'Helvetica', 'FontSize', fs(9), 'TickDir', 'out', 'LineWidth', 0.5, ...
    'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15], 'Color', 'w', 'GridColor', pal.grid, ...
    'GridAlpha', 1, 'GridLineStyle', '-', 'TickLength', [0.012 0.012]);
if isMap
    set(ax, 'Box', 'on', 'Layer', 'top');
else
    set(ax, 'Box', 'off', 'Layer', 'bottom');
end
if ~isempty(xl)
    xlabel(ax, xl, 'FontName', 'Helvetica', 'FontSize', fs(10), 'Color', [0.1 0.1 0.1]);
end
if ~isempty(yl)
    ylabel(ax, yl, 'FontName', 'Helvetica', 'FontSize', fs(10), 'Color', [0.1 0.1 0.1]);
end
end
function panelLabel(ax, s, offsetCm)
pos = get(ax, 'Position');
text('Parent', ax, 'Units', 'normalized', 'Position', [-offsetCm / pos(3), 1 + 0.1 / pos(4), 0], 'String', s, ...
     'FontName', 'Helvetica', 'FontSize', fs(10), 'FontWeight', 'bold', 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'bottom', 'Clipping', 'off');
end
function it = legendItem(kind, label, color, style, width, edge)
if nargin < 6
    edge = 'none';
end
it = struct('kind', kind, 'label', label, 'color', color, 'style', style, 'width', width);
it.edge = edge;
end
function drawLegend(fig, pos, items, nRows, colWidths)
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos);
hold(ax, 'on');
x0s = [0, cumsum(colWidths)];
rowH = pos(4) / nRows;
for k = 1:numel(items)
    it = items{k};
    col = floor((k - 1) / nRows) + 1;
    row = mod(k - 1, nRows) + 1;
    x0 = x0s(col);
    y0 = pos(4) - (row - 0.5) * rowH;
    switch it.kind
        case 'line'
            plot(ax, x0 + [0.05 0.75], [y0 y0], 'Color', it.color, 'LineStyle', it.style, 'LineWidth', it.width);
        case 'marker'
            plot(ax, x0 + 0.4, y0, 'LineStyle', 'none', 'Marker', it.style, 'MarkerSize', it.width, ...
                 'MarkerFaceColor', it.color, 'MarkerEdgeColor', it.edge, 'LineWidth', 0.9);
        case 'patch'
            patch('Parent', ax, 'XData', x0 + [0.1 0.7 0.7 0.1], 'YData', y0 + 0.12 * [-1 -1 1 1], ...
                  'FaceColor', it.color, 'EdgeColor', it.edge);
    end
    text(x0 + 0.9, y0, it.label, 'Parent', ax, 'FontName', 'Helvetica', 'FontSize', fs(8), ...
         'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', 'Clipping', 'off');
end
set(ax, 'XLim', [0 pos(3)], 'YLim', [0 pos(4)], 'Visible', 'off');
end
function saveFigure(fig, outDir, name, lg)
png = fullfile(outDir, [name, '.png']);
pdf = fullfile(outDir, [name, '.pdf']);
print(fig, '-dpng', '-r300', png);
print(fig, '-dpdf', '-painters', pdf);
if exist('OCTAVE_VERSION', 'builtin') ~= 0
    [status, out] = system(sprintf('mogrify -units PixelsPerInch -density 300 "%s" 2>&1', png));
    if status ~= 0
        say(lg, '  PNG left without a resolution tag (ImageMagick: %s)\n', strtrim(out));
    end
end
say(lg, 'saved %s and %s\n', png, pdf);
close(fig);
end
function say(lg, varargin)
fprintf(1, varargin{:});
if lg > 0
    fprintf(lg, varargin{:});
end
end
function v = fs(n)
%FS Font size of the figures: the base size N (points) enlarged by 8 %.
v = 1.08 * n;
end
