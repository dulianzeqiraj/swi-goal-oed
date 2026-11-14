function run_all_figures(repoRoot, outDir)
%RUN_ALL_FIGURES Publication figures from the six examples of CERTAIN-COAST 0.1.0 (MATLAB or GNU Octave).
%   run_all_figures() adds the CERTAIN-COAST repository to the path, recomputes every example of its folder
%   examples (same package calls, same arguments, same random seeds, same printed lines) and saves one figure per
%   topic, 16 cm wide for an A4 text column, as PNG (300 dpi) and as vector PDF in the folder 'figures' next to this
%   file. Every number shown in a figure is printed and written to figures/run_all_figures_log.txt.
%   run_all_figures(REPOROOT, OUTDIR) uses the given repository folder and output folder. Without REPOROOT the
%   environment variable CERTAINCOAST_ROOT is used, then the local clone named below.
%
%   Topics (a topic that fails is skipped and reported, the others still run)
%       fig1_henry          certaincoast.model          variable-density Henry problem (examples/example_henry.m)
%       fig2_alarm          certaincoast.alarms         certified chloride alarm (examples/example_alarm.m)
%       fig3_betweensamples certaincoast.betweensamples crossing between samples (examples/example_between_samples.m)
%       fig4_boundary       certaincoast.boundary       learned inland boundary (examples/example_boundary.m)
%       fig5_network        certaincoast.network        salinity sensor design (examples/example_network.m)
%       fig6_recharge       certaincoast.recharge       recharge from heads (examples/example_recharge.m)
%
%   MATLAB: run_all_figures. GNU Octave on a machine without a display, with the qt graphics toolkit:
%       xvfb-run -a octave --no-gui --eval "run_all_figures"
%   The random streams of MATLAB and GNU Octave differ, so the synthetic data of the alarm, between-samples,
%   boundary and recharge examples (and the numbers derived from them) differ between the two programs; the
%   Henry and network examples use no random numbers.

%   Synthetic data only, as in the examples. Copyright 2026 Dulian Zeqiraj. Licensed under the Apache License 2.0.

if nargin < 1 || isempty(repoRoot)
    repoRoot = getenv('CERTAINCOAST_ROOT');
    if isempty(repoRoot)
        repoRoot = '/home/user/dulianzeqiraj/certain-coast';
    end
end
if nargin < 2 || isempty(outDir)
    outDir = fullfile(fileparts(mfilename('fullpath')), 'figures');
end
if ~exist(fullfile(repoRoot, '+certaincoast'), 'dir')
    error('run_all_figures:repo', 'CERTAIN-COAST not found in %s: pass its folder as the first argument.', repoRoot);
end
addpath(repoRoot);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end
if exist('OCTAVE_VERSION', 'builtin') ~= 0
    warning('off', 'Octave:print:figure-too-large');     % paper size rounded to whole points by Octave
    if any(strcmp(available_graphics_toolkits(), 'qt'))
        graphics_toolkit('qt');
    end
    program = sprintf('GNU Octave %s (graphics toolkit %s)', version(), graphics_toolkit());
else
    program = sprintf('MATLAB %s', version());
end

lg = fopen(fullfile(outDir, 'run_all_figures_log.txt'), 'w');
say(lg, 'CERTAIN-COAST %s from %s\n%s, %s\n', certaincoast.version(), repoRoot, program, datestr(now, 31));
topics = {'fig1_henry', @figHenry; 'fig2_alarm', @figAlarm; 'fig3_betweensamples', @figBetweenSamples; ...
          'fig4_boundary', @figBoundary; 'fig5_network', @figNetwork; 'fig6_recharge', @figRecharge};
done = {};
skipped = {};
for k = 1:size(topics, 1)
    say(lg, '\n=== %s\n', topics{k, 1});
    t0 = tic;
    try
        f = topics{k, 2};
        f(outDir, topics{k, 1}, lg);
        done{end + 1} = topics{k, 1}; %#ok<AGROW>
        say(lg, '(%.1f s)\n', toc(t0));
    catch err
        skipped{end + 1} = topics{k, 1}; %#ok<AGROW>
        say(lg, 'SKIPPED %s: %s\n', topics{k, 1}, err.message);
        close(findall(0, 'Type', 'figure'));
    end
end
say(lg, '\n%d figure(s) made: %s\n', numel(done), strjoin(done, ', '));
if ~isempty(skipped)
    say(lg, '%d skipped: %s\n', numel(skipped), strjoin(skipped, ', '));
end
if lg > 0
    fclose(lg);
end
end

% ------------------------------------------------------------------------------------------------------------------
function figHenry(outDir, name, lg)
% examples/example_henry.m, then the salinity field of the finest grid and the toe on the four grids.
pal = palette();
P = certaincoast.model.henryParameters();
say(lg, 'Henry benchmark: Henry number phi*Dmol/Q = %.3f\n', P.phi * P.Dmol / P.Q);
toes = zeros(1, 4);
dxs = zeros(1, 4);
names = cell(1, 4);
k = 0;
for s = [16 8; 32 16; 41 21; 61 31].'
    g = certaincoast.model.henryGrid(s(1), s(2));
    t0 = tic;
    [U, normF, it] = certaincoast.model.solveDensity(zeros(g.N, 1), g, P, 1e-12);
    toe = certaincoast.model.toePosition(U, g);
    say(lg, '  %2d x %2d: toe %.4f m (%.3f of the length), residual %.1e, %d Newton steps, %.1f s\n', ...
        s(1), s(2), toe, toe / g.Lx, normF, it, toc(t0));
    k = k + 1;
    toes(k) = toe;
    dxs(k) = g.dx;
    names{k} = sprintf('%d{\\times}%d', s(1), s(2));
end
% g, U and toe now belong to the finest grid (61 x 31)
C = reshape(U(g.N + 1:2 * g.N), g.Nx, g.Ny).';           % C(j, i): row j along y, column i along x
[xp, yp, Cp] = padToEdges(g, C);
[xy, yy, Cy] = padVertically(g, C);

fig = newFigure(16, 7.4);
ax = newAxes(fig, [1.6 1.25 9.3 4.65]);
lev = 0:0.1:1;
cmap = sequential(pal, 10);
[~, hf] = contourf(ax, xp, yp, Cp, lev);
set(hf, 'LineStyle', 'none');
colormap(ax, cmap);
set(ax, 'CLim', [lev(1), lev(end)] - 0.05);            % band [lev(k), lev(k+1)] takes colour k
[M, hi] = contour(ax, xy, yy, Cy, [0.5 0.5]);
set(hi, 'LineColor', pal.ink, 'LineWidth', 1.5);
[xTop, yTop] = topOfContour(M);
plot(ax, toe, 0, 'LineStyle', 'none', 'Marker', '^', 'MarkerSize', 7, 'MarkerFaceColor', pal.ink, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75, 'Clipping', 'off');
text(toe - 0.05, 0.075, sprintf('toe %.4f m', toe), 'Parent', ax, 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'middle', 'FontSize', 9, 'Color', pal.ink);
text(xTop - 0.06, yTop, '0.5 isochlor', 'Parent', ax, 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'middle', 'FontSize', 9, 'Color', pal.ink);
text(0.04, 0.5, {'fresh-water', 'inflow'}, 'Parent', ax, 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink2);
text(1.96, 0.45, 'sea', 'Parent', ax, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle', ...
     'FontSize', 8, 'Color', 'w');
set(ax, 'XLim', [0 g.Lx], 'YLim', [0 g.Ly], 'XTick', 0:0.25:2, 'YTick', 0:0.25:1);
finishAxes(ax, 'Distance from the inland boundary, x (m)', 'Height, y (m)', true);
panelLabel(ax, '(a)', 1.45);
colorbarH(fig, [6.2 6.4 4.7 0.22], cmap, lev, 0:0.2:1, 'Relative salinity, c (-)');
say(lg, '  plotted: field of the %d x %d grid; the 0.5 isochlor meets the base at %.4f m and the sea boundary at y = %.2f m\n', ...
    g.Nx, g.Ny, toe, yTop);

ax2 = newAxes(fig, [13.1 1.25 2.65 4.65]);
plot(ax2, dxs, toes, '-', 'Color', pal.blue, 'LineWidth', 1.0);
plot(ax2, dxs, toes, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 5, 'MarkerFaceColor', pal.blue, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
for k = 1:4
    if k == 1
        text(dxs(k) - 0.007, toes(k), names{k}, 'Parent', ax2, 'HorizontalAlignment', 'right', ...
             'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink2);
    elseif k == 4
        text(dxs(k) + 0.004, toes(k) - 0.0012, names{k}, 'Parent', ax2, 'HorizontalAlignment', 'left', ...
             'VerticalAlignment', 'top', 'FontSize', 8, 'Color', pal.ink2);
    else
        text(dxs(k) + 0.007, toes(k) - 0.0006, names{k}, 'Parent', ax2, 'HorizontalAlignment', 'left', ...
             'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink2);
    end
end
set(ax2, 'XLim', [0 0.14], 'YLim', [1.38 1.43], 'XTick', 0:0.05:0.1, 'YTick', 1.38:0.01:1.43);
grid(ax2, 'on');
finishAxes(ax2, 'Cell size, {\Delta}x (m)', 'Toe of the 0.5 isochlor (m)', false);
panelLabel(ax2, '(b)', 1.25);
saveFigure(fig, outDir, name, lg);
end

% ------------------------------------------------------------------------------------------------------------------
function figAlarm(outDir, name, lg)
% examples/example_alarm.m, then the live period with the alarm and the calibration errors behind the margin.
pal = palette();
rng(1);
threshold = 250;                                          % mg/L, drinking-water limit for chloride
n = 1200;
truth = 180 + 60 * sin(linspace(0, 12 * pi, n)).' + 15 * randn(n, 1);
forecast = truth + 20 * randn(n, 1);                      % an imperfect forecast

cal = 1:600;
live = 601:n;
margin = certaincoast.alarms.conformalMargin(truth(cal) - forecast(cal), 0.10);
alarm = certaincoast.alarms.issueAlarm(forecast(live), threshold, margin);
events = truth(live) >= threshold;
misses = sum(events & ~alarm);
bound = certaincoast.alarms.missRateUpperBound(misses, sum(events));
say(lg, 'margin %.1f mg/L; events %d, missed %d; 95%% upper bound on the miss rate %.3f\n', ...
    margin, sum(events), misses, bound);
res = truth(cal) - forecast(cal);
say(lg, '  plotted: alarm level (limit - margin) %.1f mg/L; alarm on at %d of %d live steps (%d of them without an event)\n', ...
    threshold - margin, sum(alarm), numel(live), sum(alarm & ~events));
say(lg, '  plotted: %d calibration errors (steps %d-%d), %d of them above the margin; live steps %d-%d\n', ...
    numel(res), cal(1), cal(end), sum(res > margin), live(1), live(end));

fig = newFigure(16, 7.7);
ax = newAxes(fig, [1.45 1.25 9.6 4.6]);
yl = [40 345];
[i1, i2] = runs(alarm);
for k = 1:numel(i1)
    patch('Parent', ax, 'XData', live([i1(k) i2(k) i2(k) i1(k)]) + [-0.5 0.5 0.5 -0.5], ...
          'YData', yl([1 1 2 2]), 'FaceColor', pal.alarmTint, 'EdgeColor', 'none');
end
plot(ax, live, forecast(live), '-', 'Color', pal.lightBlue, 'LineWidth', 0.6);
plot(ax, live, truth(live), '-', 'Color', pal.ink2, 'LineWidth', 0.7);
plot(ax, [live(1) - 0.5, live(end) + 0.5], threshold * [1 1], '--', 'Color', pal.ink, 'LineWidth', 0.9);
plot(ax, [live(1) - 0.5, live(end) + 0.5], (threshold - margin) * [1 1], ':', 'Color', pal.darkBlue, 'LineWidth', 1.3);
ev = live(events);
plot(ax, ev, truth(ev), 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 4.5, 'MarkerFaceColor', pal.red, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.6);
text(live(1) + 6, 330, sprintf('%d events, %d missed; 95%% upper bound on the miss rate %.3f', ...
     sum(events), misses, bound), 'Parent', ax, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', ...
     'FontSize', 8.5, 'Color', pal.ink, 'BackgroundColor', 'w', 'Margin', 1);
set(ax, 'XLim', [live(1) - 0.5, live(end) + 0.5], 'YLim', yl, 'XTick', 600:100:1200, 'YTick', 50:50:300);
finishAxes(ax, 'Time step (-)', 'Chloride (mg/L)', false);
panelLabel(ax, '(a)', 1.3);
items = {legendItem('line', 'observed chloride', pal.ink2, '-', 1.0), ...
         legendItem('line', 'forecast', pal.lightBlue, '-', 1.2), ...
         legendItem('line', sprintf('limit %d mg/L', threshold), pal.ink, '--', 0.9), ...
         legendItem('line', sprintf('alarm level = limit - margin (%.1f mg/L)', margin), pal.darkBlue, ':', 1.3), ...
         legendItem('patch', 'alarm issued', pal.alarmTint, '-', 1), ...
         legendItem('marker', 'event: observed at or above the limit', pal.red, 'o', 4.5, 'w')};
drawLegend(fig, [1.45 6.1 9.6 1.4], items, 3, [3.5 6.1]);

ax2 = newAxes(fig, [12.55 1.65 3.2 4.2]);
w = 10;
edges = -60:w:60;
counts = zeros(1, numel(edges) - 1);
for k = 1:numel(counts)
    counts(k) = sum(res >= edges(k) & res < edges(k + 1));
end
for k = 1:numel(counts)
    patch('Parent', ax2, 'XData', edges(k) + [0 w w 0], 'YData', [0 0 counts(k) counts(k)], ...
          'FaceColor', pal.barGray, 'EdgeColor', 'w', 'LineWidth', 0.6);
end
plot(ax2, margin * [1 1], [0 205], ':', 'Color', pal.darkBlue, 'LineWidth', 1.4);
text(margin - 3, 198, {'margin', sprintf('%.1f mg/L', margin)}, 'Parent', ax2, 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'top', 'FontSize', 8, 'Color', pal.ink);
set(ax2, 'XLim', [-60 60], 'YLim', [0 205], 'XTick', -60:30:60, 'YTick', 0:50:200);
finishAxes(ax2, {'Observed - forecast', 'in calibration (mg/L)'}, 'Number of steps', false);
panelLabel(ax2, '(b)', 1.15);
saveFigure(fig, outDir, name, lg);
end

% ------------------------------------------------------------------------------------------------------------------
function figBetweenSamples(outDir, name, lg)
% examples/example_between_samples.m, then the crossing probability and the warning band of each design.
pal = palette();
rng(3);
z = (250 - 180) / 35;
kGrid = exp(linspace(log(1 / 400), log(4), 41));
curve = certaincoast.betweensamples.crossingProbability(kGrid, z, 120, 0.25, 8000);
truth = interp1(log(kGrid), curve, log(1 / 8));
say(lg, 'probability of crossing in the season %.2f; at the samples alone (marginal tail) %.3f\n', ...
    truth, 0.5 * erfc(z / sqrt(2)));
designs = {'quarterly samples', 91; 'monthly samples', 30; 'weekly samples', 7; 'daily logger', 1};
band = zeros(size(designs, 1), 2);
tau = zeros(size(designs, 1), 3);
isOpen = false(size(designs, 1), 1);
for d = 1:size(designs, 1)
    t = certaincoast.betweensamples.sampleTimes(8 * 365, designs{d, 2});
    x = certaincoast.betweensamples.ouAtTimes(t, 1 / 8);
    [kHat, kLo, kHi, ~, openHi] = certaincoast.betweensamples.timeScaleInterval(t, x, kGrid);
    [lo, hi] = certaincoast.betweensamples.crossingBand(kLo, kHi, kGrid, curve);
    note = '';
    if openHi
        note = ' (shortest time scales not excluded)';
    end
    say(lg, '%-18s correlation time %6.1f d, 95%% interval %6.1f-%6.1f d%s; warning band %.2f-%.2f\n', ...
        designs{d, 1}, 1 / kHat, 1 / kHi, 1 / kLo, note, lo, hi);
    band(d, :) = [lo, hi];
    tau(d, :) = [1 / kHat, 1 / kHi, 1 / kLo];
    isOpen(d) = openHi;
end
tail = 0.5 * erfc(z / sqrt(2));
say(lg, '  plotted: crossing curve over correlation times %.2f-%.0f d (%d rates, 8000 paths, season 120 d, z = %.0f)\n', ...
    1 / kGrid(end), 1 / kGrid(1), numel(kGrid), z);

fig = newFigure(16, 7.3);
ax = newAxes(fig, [1.95 1.25 6.0 5.3]);
plot(ax, [0.2 500], tail * [1 1], '--', 'Color', pal.ink2, 'LineWidth', 0.9);
plot(ax, 1 ./ kGrid, curve, '-', 'Color', pal.blue, 'LineWidth', 1.4);
plot(ax, 8, truth, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 6, 'MarkerFaceColor', pal.ink, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
text(8 * 1.3, truth + 0.03, sprintf('1/{\\kappa} = 8 d: %.2f', truth), 'Parent', ax, ...
     'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom', 'FontSize', 8.5, 'Color', pal.ink);
text(0.27, tail + 0.025, sprintf('samples alone: %.3f', tail), 'Parent', ax, ...
     'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom', 'FontSize', 8.5, 'Color', pal.ink2);
set(ax, 'XScale', 'log', 'XLim', [0.2 500], 'YLim', [0 1.05], 'XTick', [1 10 100], ...
    'XTickLabel', {'1', '10', '100'}, 'YTick', 0:0.2:1);
grid(ax, 'on');
set(ax, 'XMinorGrid', 'off', 'YMinorGrid', 'off');
finishAxes(ax, 'Correlation time of chloride, 1/{\kappa} (d)', ...
           {'Probability of crossing', '250 mg/L in 120 days (-)'}, false);
panelLabel(ax, '(a)', 1.8);

ax2 = newAxes(fig, [9.6 1.25 6.15 5.3]);
plot(ax2, [0.4 4.6], truth * [1 1], '-', 'Color', pal.ink, 'LineWidth', 0.9);
plot(ax2, [0.4 4.6], tail * [1 1], '--', 'Color', pal.ink2, 'LineWidth', 0.9);
for d = 1:size(designs, 1)
    patch('Parent', ax2, 'XData', d + 0.2 * [-1 1 1 -1], 'YData', band(d, [1 1 2 2]), 'FaceColor', pal.blue, ...
          'EdgeColor', 'none');
    if isOpen(d)
        lab = {'1/{\kappa}', sprintf('{\\leq}%.1f d', tau(d, 3))};
    else
        lab = {'1/{\kappa}', sprintf('%.1f-%.1f d', tau(d, 2), tau(d, 3))};
    end
    text(d, band(d, 1) - 0.025, lab, 'Parent', ax2, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top', ...
         'FontSize', 8, 'Color', pal.ink2);
end
set(ax2, 'XLim', [0.4 4.6], 'YLim', [0 1.05], 'XTick', 1:4, ...
    'XTickLabel', {'quarterly', 'monthly', 'weekly', 'daily logger'}, 'YTick', 0:0.2:1);
grid(ax2, 'on');
set(ax2, 'XGrid', 'off');
finishAxes(ax2, 'Sampling of an 8-year chloride record', 'Robust warning band (-)', false);
panelLabel(ax2, '(b)', 1.25);
items = {legendItem('line', sprintf('true probability, %.2f', truth), pal.ink, '-', 0.9), ...
         legendItem('line', sprintf('samples alone, %.3f', tail), pal.ink2, '--', 0.9)};
drawLegend(fig, [11.35 1.62 4.3 0.75], items, 2, 4.3);
saveFigure(fig, outDir, name, lg);
end

% ------------------------------------------------------------------------------------------------------------------
function figBoundary(outDir, name, lg)
% examples/example_boundary.m, then the heads at the boundary cell in the prediction and the boundary impedances.
pal = palette();
rng(7);
p = certaincoast.boundary.aquifer();
A = certaincoast.boundary.conductanceMatrix(p.nFull, p, true);
f = zeros(p.nFull, 1);
f(1:p.nModel) = p.R0 * p.dx;
f(p.well) = f(p.well) - p.Q0;
hs = A \ f;
H = hs(p.boundaryCell);
h0 = hs(1:p.nModel);
bc = p.boundaryCell;

nd = round(20 * 365.25);
[~, r, Q] = certaincoast.boundary.forcing(p, nd, 'broadband');
full = certaincoast.boundary.simulateFull(p, r, Q);
rmsBc = @(h, ref) sqrt(mean((h(:, bc) - ref(:, bc)) .^ 2));

[C, w, mu] = certaincoast.boundary.exactExterior(p);
[Cf, wf, muf] = certaincoast.boundary.fitPositive(@(s) certaincoast.boundary.impedance(s, C, w, mu), 12, ...
                                                 [2 * pi / (40 * 365.25), 2 * pi / 5]);
say(lg, '20 years, error at the boundary cell (m, rms):\n');
say(lg, '  exact passive boundary (%d compartments) %.1e\n', numel(mu), ...
    rmsBc(certaincoast.boundary.simulateTruncated(p, r, Q, C, w, mu, H, h0), full));
say(lg, '  reduced passive boundary (12 compartments) %.4f\n', ...
    rmsBc(certaincoast.boundary.simulateTruncated(p, r, Q, Cf, wf, muf, H, h0), full));
say(lg, '  no flow %.4f, fixed head %.4f\n', ...
    rmsBc(certaincoast.boundary.simulateTruncated(p, r, Q, 0, 0, 1, H, h0), full), ...
    rmsBc(certaincoast.boundary.simulateTruncated(p, r, Q, p.c, 0, 1, H, h0), full));

o1 = full(:, p.bandCells(1)) + 0.002 * randn(nd, 1);       % two piezometers with 2 mm noise
o2 = full(:, p.bandCells(2)) + 0.002 * randn(nd, 1);
[Ci, wi, mui] = certaincoast.boundary.identifyFromPiezometers(p, o1, o2, r, H);
[tp, rp, Qp] = certaincoast.boundary.forcing(p, round(10 * 365.25), 'seasonal', [3 * 365.25, 8 * 365.25, 0.3], ...
                                             [2 * 365.25, Inf, 1.2]);
ref = certaincoast.boundary.simulateFull(p, rp, Qp);
hLearned = certaincoast.boundary.simulateTruncated(p, rp, Qp, Ci, wi, mui, H, h0);
hNoFlow = certaincoast.boundary.simulateTruncated(p, rp, Qp, 0, 0, 1, H, h0);
hFixed = certaincoast.boundary.simulateTruncated(p, rp, Qp, p.c, 0, 1, H, h0);
eLearned = rmsBc(hLearned, ref);
eNoFlow = rmsBc(hNoFlow, ref);
eFixed = rmsBc(hFixed, ref);
say(lg, 'Prediction of a drought with doubled pumping, 10 years (m, rms at the boundary cell):\n');
say(lg, '  boundary learned from two piezometers %.4f\n', eLearned);
say(lg, '  no flow %.4f, fixed head %.4f\n', eNoFlow, eFixed);

om = logspace(log10(2 * pi / (40 * 365.25)), log10(2 * pi / 5), 300).';
Zexact = certaincoast.boundary.impedance(1i * om, C, w, mu);
Zlearned = certaincoast.boundary.impedance(1i * om, Ci, wi, mui);
period = 2 * pi ./ om / 365.25;                                       % years
say(lg, '  plotted: heads at the boundary cell (cell %d, centre %.0f m from the sea; model of %.0f m in an aquifer of %.0f m)\n', ...
    bc, (bc - 0.5) * p.dx, p.nModel * p.dx, p.nFull * p.dx);
say(lg, '  plotted: |Z| of the exact exterior and of the learned boundary (m/d), periods 5 d to 40 years:\n');
for T = [40, 10, 1, 0.1, 5 / 365.25]
    s = 1i * 2 * pi / (T * 365.25);
    ze = abs(certaincoast.boundary.impedance(s, C, w, mu));
    zl = abs(certaincoast.boundary.impedance(s, Ci, wi, mui));
    say(lg, '    period %7.4f years: exact %.3f, learned %.3f (%+.0f%%)\n', T, ze, zl, 100 * (zl / ze - 1));
end
say(lg, '  fixed head: |Z| = %.1f m/d at every period; no flow: Z = 0 (not on the log scale)\n', p.c);

fig = newFigure(16, 7.7);
ax = newAxes(fig, [1.6 1.25 8.8 4.6]);
yr = tp / 365.25;
yl = [-2.0 2.0];
patch('Parent', ax, 'XData', [3 8 8 3], 'YData', yl([1 1 2 2]), 'FaceColor', pal.spanGray, 'EdgeColor', 'none');
plot(ax, [2 2], yl, '-', 'Color', pal.muted, 'LineWidth', 0.8);
text(5.5, 1.8, 'drought: recharge \times 0.3', 'Parent', ax, 'HorizontalAlignment', 'center', ...
     'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink2);
text(2.08, 1.45, 'pumping \times 2', 'Parent', ax, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', ...
     'FontSize', 8, 'Color', pal.ink2);
plot(ax, yr, ref(:, bc), '-', 'Color', pal.refGray, 'LineWidth', 2.6);
plot(ax, yr, hFixed(:, bc), '-.', 'Color', pal.aqua, 'LineWidth', 1.0);
plot(ax, yr, hNoFlow(:, bc), '--', 'Color', pal.orange, 'LineWidth', 1.0);
plot(ax, yr, hLearned(:, bc), '-', 'Color', pal.blue, 'LineWidth', 0.9);
set(ax, 'XLim', [0 10], 'YLim', yl, 'XTick', 0:2:10, 'YTick', -2:1:2);
grid(ax, 'on');
finishAxes(ax, 'Time in the prediction (years)', 'Head at the boundary (m)', false);
panelLabel(ax, '(a)', 1.45);
items = {legendItem('line', 'whole aquifer, 10 km (reference)', pal.refGray, '-', 2.6), ...
         legendItem('line', sprintf('2 km model, boundary learned from two piezometers: rms error %.4f m', eLearned), ...
                    pal.blue, '-', 0.9), ...
         legendItem('line', sprintf('2 km model, no-flow boundary: rms error %.4f m', eNoFlow), pal.orange, '--', 1.0), ...
         legendItem('line', sprintf('2 km model, fixed-head boundary: rms error %.4f m', eFixed), pal.aqua, '-.', 1.0)};
drawLegend(fig, [1.6 6.1 14.1 1.45], items, 4, 14.1);

ax2 = newAxes(fig, [12.25 1.25 3.5 4.6]);
plot(ax2, period, abs(Zexact), '-', 'Color', pal.refGray, 'LineWidth', 2.6);
plot(ax2, [period(end) period(1)], p.c * [1 1], '-.', 'Color', pal.aqua, 'LineWidth', 1.0);
plot(ax2, period, abs(Zlearned), '-', 'Color', pal.blue, 'LineWidth', 0.9);
text(0.0115, 1.9, 'exact', 'Parent', ax2, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'top', ...
     'FontSize', 8, 'Color', pal.ink2);
text(0.03, 13, 'learned', 'Parent', ax2, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', ...
     'FontSize', 8, 'Color', pal.ink2);
text(40, 6.6, 'fixed head', 'Parent', ax2, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom', ...
     'FontSize', 8, 'Color', pal.ink2);
set(ax2, 'XScale', 'log', 'YScale', 'log', 'XLim', [0.01 50], 'YLim', [0.08 20], 'XTick', [0.01 0.1 1 10], ...
    'XTickLabel', {'0.01', '0.1', '1', '10'}, 'YTick', [0.1 1 10], 'YTickLabel', {'0.1', '1', '10'});
grid(ax2, 'on');
set(ax2, 'XMinorGrid', 'off', 'YMinorGrid', 'off');
finishAxes(ax2, 'Period (years)', 'Impedance |Z| (m/d)', false);
panelLabel(ax2, '(b)', 1.25);
saveFigure(fig, outDir, name, lg);
end

% ------------------------------------------------------------------------------------------------------------------
function figNetwork(outDir, name, lg)
% examples/example_network.m, then the candidate and chosen sensors on the section and the gain per added sensor.
pal = palette();
g = certaincoast.model.henryGrid(16, 8);
P = certaincoast.model.henryParameters();
theta = zeros(g.N, 1);
U = certaincoast.model.solveDensity(theta, g, P, 1e-12);
[J, ~, Jtheta] = certaincoast.model.densityJacobian(U, theta, g, P);

[X, Y] = ndgrid(g.xc, g.yc);                    % cell centres in the flat order of the state
X = X(:);
Y = Y(:);
cellAt = @(x, y) find(abs(X - x) < g.dx / 2 & abs(Y - y) < g.dy / 2);
cand = zeros(12, 1);
k = 0;
for x = [0.5625 1.0625 1.4375 1.8125]
    for y = [0.0625 0.4375 0.8125]
        k = k + 1;
        cand(k) = cellAt(x, y);
    end
end
supply = cellAt(1.5625, 0.3125);                % a mid-depth well 0.44 m from the sea
zone = find(X > 1.0 & X < 1.6 & Y < 0.25);       % the toe zone

dOdu = sparse(1:12, g.N + cand, 1, 12, 2 * g.N);
dqdu = [zeros(1, g.N), zeros(1, g.N)];
dqdu(g.N + zone) = g.dx * g.dy;                  % salt mass in the toe zone
dsdu = sparse(1, g.N + supply, 1, 1, 2 * g.N);   % salinity at the supply cell
[G, H] = certaincoast.network.adjointSensitivities(J, Jtheta, [dOdu; dsdu], dqdu);
Hs = G(13, :);
G = G(1:12, :);

D = sqrt(bsxfun(@minus, X, X.') .^ 2 + bsxfun(@minus, Y, Y.') .^ 2);
Gam = 0.25 * exp(-D / 0.4);                      % prior covariance of the log-conductivity
noise = 0.02 ^ 2;                                % salinity sensor noise (2% of sea-water salinity)

[S, gain, steps] = certaincoast.network.greedyDesign(G, H, Gam, noise, 3);
combs = nchoosek(1:12, 3);
gains = zeros(size(combs, 1), 1);
Sigma = [G; -Hs] * Gam * [G; -Hs].';             % joint covariance of the 12 sensors and of -salinity at supply
sdS = sqrt(Sigma(13, 13));
limit = U(g.N + supply) + 0.3 * sdS;             % the supply cell is "salinised" above this value
risks = zeros(size(combs, 1), 1);
for c = 1:size(combs, 1)
    gains(c) = certaincoast.network.eigOperator(G(combs(c, :), :), H, Gam, noise * eye(3));
    risks(c) = certaincoast.network.thresholdGoalEig(Sigma, -U(g.N + supply), combs(c, :), noise, 13, -limit);
end
[best, ib] = max(gains);
[bestRisk, ir] = max(risks);
say(lg, 'Salt mass near the toe: greedy design %s gives %.3f nats; exhaustive optimum %s %.3f; median design %.3f\n', ...
    mat2str(sort(S)), gain, mat2str(combs(ib, :)), best, median(gains));
say(lg, 'Supply cell above its limit (prior probability %.2f): best design %s gives %.3f nats;\n', ...
    0.5 * erfc(0.3 / sqrt(2)), mat2str(combs(ir, :)), bestRisk);
say(lg, '  the salt-mass design %s gives it %.3f nats (%.0f%% of that optimum).\n', mat2str(combs(ib, :)), risks(ib), ...
    100 * risks(ib) / bestRisk);
say(lg, '  plotted: greedy order %s; gain after each added sensor %s nats; all %d designs of 3 sensors: %.3f-%.3f nats\n', ...
    mat2str([steps.added]), mat2str([steps.gain], 4), numel(gains), min(gains), max(gains));

C = reshape(U(g.N + 1:2 * g.N), g.Nx, g.Ny).';
[xy, yy, Cy] = padVertically(g, C);
fig = newFigure(16, 7.9);
ax = newAxes(fig, [1.55 1.25 9.0 4.5]);
zx = [min(X(zone)) - g.dx / 2, max(X(zone)) + g.dx / 2];
zy = [min(Y(zone)) - g.dy / 2, max(Y(zone)) + g.dy / 2];
patch('Parent', ax, 'XData', zx([1 2 2 1]), 'YData', zy([1 1 2 2]), 'FaceColor', pal.zoneTint, ...
      'EdgeColor', pal.orange, 'LineWidth', 0.8);
text(zx(1) + 0.02, zy(2) + 0.03, 'toe zone (goal)', 'Parent', ax, 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'bottom', 'FontSize', 8, 'Color', pal.ink);
levels = [0.1 0.5 0.9];
for k = 1:3
    [M, hc] = contour(ax, xy, yy, Cy, levels(k) * [1 1]);
    set(hc, 'LineColor', pal.muted, 'LineWidth', 0.8);
    [xt, yt] = topOfContour(M);
    text(xt, min(yt + 0.06, 0.95), sprintf('%.1f', levels(k)), 'Parent', ax, 'HorizontalAlignment', 'center', ...
         'VerticalAlignment', 'middle', 'FontSize', 7.5, 'Color', pal.ink2, 'BackgroundColor', 'w', 'Margin', 0.5);
end
inR = ismember(1:12, combs(ir, :));
inS = ismember(1:12, S);
for j = 1:12
    if inR(j)
        plot(ax, X(cand(j)), Y(cand(j)), 'LineStyle', 'none', 'Marker', 's', 'MarkerSize', 11, ...
             'MarkerFaceColor', 'none', 'MarkerEdgeColor', pal.orange, 'LineWidth', 1.3);
    end
    if inS(j)
        plot(ax, X(cand(j)), Y(cand(j)), 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 6.5, ...
             'MarkerFaceColor', pal.blue, 'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
    else
        plot(ax, X(cand(j)), Y(cand(j)), 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 5.5, ...
             'MarkerFaceColor', 'w', 'MarkerEdgeColor', pal.ink2, 'LineWidth', 0.8);
    end
    text(X(cand(j)) + 0.045, Y(cand(j)) + 0.05, sprintf('%d', j), 'Parent', ax, 'HorizontalAlignment', 'left', ...
         'VerticalAlignment', 'bottom', 'FontSize', 8, 'Color', pal.ink);
end
plot(ax, X(supply), Y(supply), 'LineStyle', 'none', 'Marker', 'd', 'MarkerSize', 6.5, 'MarkerFaceColor', pal.ink, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
text(X(supply) + 0.045, Y(supply), 'supply', 'Parent', ax, 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink);
set(ax, 'XLim', [0 g.Lx], 'YLim', [0 g.Ly], 'XTick', 0:0.25:2, 'YTick', 0:0.25:1);
finishAxes(ax, 'Distance from the inland boundary, x (m)', 'Height, y (m)', true);
panelLabel(ax, '(a)', 1.4);
items = {legendItem('marker', 'candidate salinity sensor (number)', 'w', 'o', 5.5, pal.ink2), ...
         legendItem('marker', sprintf('greedy design %s for the salt mass = exhaustive optimum', mat2str(sort(S))), ...
                    pal.blue, 'o', 6.5, 'w'), ...
         legendItem('marker', sprintf('best design %s for "supply cell above its limit?"', mat2str(combs(ir, :))), ...
                    'none', 's', 9, pal.orange), ...
         legendItem('marker', 'supply cell', pal.ink, 'd', 6.5, 'w'), ...
         legendItem('line', 'isochlors c = 0.1, 0.5, 0.9', pal.muted, '-', 0.8)};
drawLegend(fig, [1.55 6.15 14.2 1.5], items, 3, [9.6 4.6]);

ax2 = newAxes(fig, [12.2 1.25 3.55 4.5]);
gs = sort(gains);
jit = mod((1:numel(gs)).' * 0.6180339887, 1) - 0.5;      % deterministic spread of the dots, no random numbers
plot(ax2, 3 + 0.36 * jit, gs, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 2.5, ...
     'MarkerFaceColor', pal.dotGray, 'MarkerEdgeColor', 'none');
plot(ax2, 3 + [-0.26 0.26], median(gains) * [1 1], '-', 'Color', pal.ink, 'LineWidth', 1.2);
text(2.7, median(gains), sprintf('median %.3f', median(gains)), 'Parent', ax2, 'HorizontalAlignment', 'right', ...
     'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink);
text(2.7, 0.3, {sprintf('all %d designs', numel(gains)), 'of 3 sensors'}, 'Parent', ax2, ...
     'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle', 'FontSize', 8, 'Color', pal.ink2);
gsteps = [steps.gain];
plot(ax2, 1:numel(gsteps), gsteps, '-', 'Color', pal.blue, 'LineWidth', 1.2);
plot(ax2, 1:numel(gsteps), gsteps, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 6.5, ...
     'MarkerFaceColor', pal.blue, 'MarkerEdgeColor', 'w', 'LineWidth', 0.75);
added = [steps.added];
for k = 1:numel(gsteps)
    if k == 1
        text(k, gsteps(k) - 0.13, sprintf('sensor %d', added(k)), 'Parent', ax2, 'HorizontalAlignment', 'center', ...
             'VerticalAlignment', 'top', 'FontSize', 8, 'Color', pal.ink);
    else
        text(k, gsteps(k) + 0.13, sprintf('+ %d', added(k)), 'Parent', ax2, 'HorizontalAlignment', 'center', ...
             'VerticalAlignment', 'bottom', 'FontSize', 8, 'Color', pal.ink);
    end
end
set(ax2, 'XLim', [0.5 3.5], 'YLim', [0 3], 'XTick', 1:3, 'YTick', 0:0.5:3);
grid(ax2, 'on');
set(ax2, 'XGrid', 'off');
finishAxes(ax2, 'Number of sensors', 'Information gain (nats)', false);
panelLabel(ax2, '(b)', 1.25);
saveFigure(fig, outDir, name, lg);
end

% ------------------------------------------------------------------------------------------------------------------
function figRecharge(outDir, name, lg)
% examples/example_recharge.m, then the true and recovered recharge, daily and in 30-day sums.
pal = palette();
rng(11);
par = struct('m', 1.12, 'k_et', 0.9, 'Ic', 30, 'theta_fc', 150, 'tau_s', 8, 'phi0', 0.25, 'Sy', 0.2, ...
             'tau_a', 150, 'h_b', 0.8, 'h_0', 1.4);
N = 1096;
[P, PET] = certaincoast.recharge.syntheticClimate(N);
Pg = P / par.m;                                           % the gauge catches less than the true rain
o = certaincoast.recharge.soilWaterBalance(par, Pg, PET);
say(lg, 'rain %.0f mm/yr, recharge %.0f mm/yr (%.0f%% of the rain)\n', sum(P) / 3, sum(o.R) / 3, ...
    100 * sum(o.R) / sum(P));

h = o.h + 0.01 * randn(N, 1);
R = certaincoast.recharge.rechargeFromHeads(h, par.Sy, par.tau_a, par.h_b, par.h_0);
monthly = @(x) accumarray(ceil((1:numel(x)).' / 30), x(:));      % sums over 30-day blocks
eDaily = sqrt(mean((R(2:end) - o.R(2:end)) .^ 2));
predicted = 1000 * par.Sy * 0.01 * sqrt(2);
eMonthly = sqrt(mean((monthly(R(2:end)) - monthly(o.R(2:end))) .^ 2));
meanMonthly = mean(monthly(o.R(2:end)));
say(lg, 'recharge from heads: daily error %.1f mm (predicted %.1f); monthly error %.1f mm (mean monthly %.1f)\n', ...
    eDaily, predicted, eMonthly, meanMonthly);

q = par;
names = {'m', 'k_et', 'Ic', 'theta_fc', 'Sy'};
for i = 1:numel(names)
    q.(names{i}) = 1.5 * q.(names{i});
end
o2 = certaincoast.recharge.soilWaterBalance(q, Pg, PET);
say(lg, 'scaled parameters: largest head change %.1e m, recharge %.0f mm/yr instead of %.0f\n', ...
    max(abs(o2.h - o.h)), sum(o2.R) / 3, sum(o.R) / 3);
say(lg, 'so a pumping test (Sy), a soil-moisture probe or a chloride balance is needed to fix the amount.\n');

mTrue = monthly(o.R(2:end));
mFromHeads = monthly(R(2:end));
nb = numel(mTrue);
first = 30 * (0:nb - 1).' + 2;                           % first day of each block (the sums start on day 2)
last = min(first + 29, N);
say(lg, '  plotted: days 2-%d; %d blocks of 30 days (the last one has %d days); largest true daily recharge %.1f mm/d\n', ...
    N, nb, last(end) - first(end) + 1, max(o.R));

fig = newFigure(16, 9.4);
ax = newAxes(fig, [1.6 5.5 14.15 3.0]);
day = (2:N).';
plot(ax, [0 N + 1], [0 0], '-', 'Color', pal.muted, 'LineWidth', 0.5);
plot(ax, day, R(2:end), '-', 'Color', pal.lightBlue, 'LineWidth', 0.5);
plot(ax, day, o.R(2:end), '-', 'Color', pal.ink, 'LineWidth', 0.8);
set(ax, 'XLim', [0 N + 1], 'YLim', [-10 15], 'XTick', 0:100:1100, 'YTick', -10:5:15, 'XTickLabel', {});
grid(ax, 'on');
finishAxes(ax, '', 'Recharge (mm/d)', false);
panelLabel(ax, '(a)', 1.45);
items = {legendItem('line', 'true recharge (soil-water balance)', pal.ink, '-', 1.0), ...
         legendItem('line', sprintf('recharge from heads with 1 cm noise: daily rms error %.1f mm (predicted %.1f mm)', ...
                    eDaily, predicted), pal.lightBlue, '-', 1.2)};
drawLegend(fig, [1.6 8.6 14.15 0.75], items, 2, 14.15);

ax2 = newAxes(fig, [1.6 1.25 14.15 3.85]);
for k = 1:nb
    patch('Parent', ax2, 'XData', [first(k) - 0.5, last(k) + 0.5, last(k) + 0.5, first(k) - 0.5], ...
          'YData', [0 0 mTrue(k) mTrue(k)], 'FaceColor', pal.barGray, 'EdgeColor', 'w', 'LineWidth', 0.6);
end
mid = (first + last) / 2;
plot(ax2, [0 N + 1], [0 0], '-', 'Color', pal.muted, 'LineWidth', 0.5);
plot(ax2, mid, mFromHeads, 'LineStyle', 'none', 'Marker', 'o', 'MarkerSize', 5, 'MarkerFaceColor', pal.blue, ...
     'MarkerEdgeColor', 'w', 'LineWidth', 0.6);
set(ax2, 'XLim', [0 N + 1], 'YLim', [-20 175], 'XTick', 0:100:1100, 'YTick', 0:50:150);
grid(ax2, 'on');
set(ax2, 'XGrid', 'off');
text(14, 166, sprintf('30-day rms error %.1f mm; mean 30-day recharge %.1f mm', eMonthly, meanMonthly), ...
     'Parent', ax2, 'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', 'FontSize', 8.5, 'Color', pal.ink);
finishAxes(ax2, 'Time from 1 September of the first year (days)', '30-day recharge (mm)', false);
panelLabel(ax2, '(b)', 1.45);
items = {legendItem('patch', 'true', pal.barGray, '-', 1), ...
         legendItem('marker', 'from heads', pal.blue, 'o', 5, 'w')};
drawLegend(fig, [13.45 4.05 2.3 0.8], items, 2, 2.3);
saveFigure(fig, outDir, name, lg);
end

% ------------------------------------------------------------------------------------------------------------------
% Helpers: figure, axes, legend, colour scale, output
% ------------------------------------------------------------------------------------------------------------------
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
% n colours of the one-hue sequential ramp, light to dark.
cmap = interp1(linspace(0, 1, size(pal.ramp, 1)).', pal.ramp, linspace(0, 1, n).');
end

function fig = newFigure(w, h)
% Figure of W x H cm, white, printed at that size; Helvetica 9 pt by default.
fig = figure('Visible', 'off', 'Color', 'w', 'Units', 'centimeters', 'Position', [2 2 w h], ...
             'PaperUnits', 'centimeters', 'PaperSize', [w h], 'PaperPosition', [0 0 w h], ...
             'PaperPositionMode', 'manual', 'InvertHardcopy', 'off', ...
             'DefaultAxesFontName', 'Helvetica', 'DefaultAxesFontSize', 9, ...
             'DefaultTextFontName', 'Helvetica', 'DefaultTextFontSize', 9, ...
             'DefaultAxesLineWidth', 0.5, 'DefaultLineLineWidth', 1.0, 'DefaultAxesTickDir', 'out', ...
             'DefaultAxesXColor', [0.15 0.15 0.15], 'DefaultAxesYColor', [0.15 0.15 0.15]);
end

function ax = newAxes(fig, pos)
% Axes at POS = [left bottom width height] (cm), held so that plotting does not reset its properties.
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos);
hold(ax, 'on');
end

function finishAxes(ax, xl, yl, isMap)
% Fonts, ticks and labels (10 pt labels, 9 pt tick labels). A map (ISMAP) is boxed with its axes over the data;
% a chart keeps its light grid under the data.
pal = palette();
set(ax, 'FontName', 'Helvetica', 'FontSize', 9, 'TickDir', 'out', 'LineWidth', 0.5, ...
    'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15], 'Color', 'w', 'GridColor', pal.grid, ...
    'GridAlpha', 1, 'GridLineStyle', '-', 'TickLength', [0.012 0.012]);
if isMap
    set(ax, 'Box', 'on', 'Layer', 'top');
else
    set(ax, 'Box', 'off', 'Layer', 'bottom');
end
if ~isempty(xl)
    xlabel(ax, xl, 'FontName', 'Helvetica', 'FontSize', 10, 'Color', [0.1 0.1 0.1]);
end
if ~isempty(yl)
    ylabel(ax, yl, 'FontName', 'Helvetica', 'FontSize', 10, 'Color', [0.1 0.1 0.1]);
end
end

function panelLabel(ax, s, offsetCm)
% Panel letter at the top left, OFFSETCM to the left of the axes.
pos = get(ax, 'Position');
text('Parent', ax, 'Units', 'normalized', 'Position', [-offsetCm / pos(3), 1 + 0.1 / pos(4), 0], 'String', s, ...
     'FontName', 'Helvetica', 'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'left', ...
     'VerticalAlignment', 'bottom', 'Clipping', 'off');
end

function it = legendItem(kind, label, color, style, width, edge)
% One legend entry: KIND 'line' (STYLE, WIDTH), 'marker' (STYLE = marker, WIDTH = size, EDGE) or 'patch'.
if nargin < 6
    edge = 'none';
end
it = struct('kind', kind, 'label', label, 'color', color, 'style', style, 'width', width);
it.edge = edge;
end

function drawLegend(fig, pos, items, nRows, colWidths)
% Legend drawn in its own invisible axes at POS (cm), filled column by column: the same layout in MATLAB and Octave.
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
    text(x0 + 0.9, y0, it.label, 'Parent', ax, 'FontName', 'Helvetica', 'FontSize', 8, ...
         'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', 'Clipping', 'off');
end
set(ax, 'XLim', [0 pos(3)], 'YLim', [0 pos(4)], 'Visible', 'off');
end

function colorbarH(fig, pos, cmap, lev, ticks, label)
% Horizontal colour scale of filled bands [LEV(k), LEV(k+1)] drawn with patches (clean in vector output).
ax = axes('Parent', fig, 'Units', 'centimeters', 'Position', pos);
hold(ax, 'on');
for k = 1:numel(lev) - 1
    patch('Parent', ax, 'XData', [lev(k) lev(end) lev(end) lev(k)], 'YData', [0 0 1 1], ...
          'FaceColor', cmap(k, :), 'EdgeColor', 'none');
end
set(ax, 'XLim', lev([1 end]), 'YLim', [0 1], 'XTick', ticks, 'YTick', [], 'XAxisLocation', 'top', ...
    'Box', 'on', 'Layer', 'top', 'TickDir', 'out', 'FontName', 'Helvetica', 'FontSize', 9, 'LineWidth', 0.5, ...
    'XColor', [0.15 0.15 0.15], 'YColor', [0.15 0.15 0.15], 'TickLength', [0.03 0.03]);
text('Parent', ax, 'Units', 'normalized', 'Position', [-0.04, 0.5, 0], 'String', label, 'FontName', 'Helvetica', ...
     'FontSize', 10, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle', 'Clipping', 'off');
end

function [xp, yp, Cp] = padToEdges(g, C)
% Cell-centred values extended to the four edges of the section (each edge cell up to its outer face): fills.
xp = [0, g.xc, g.Lx];
yp = [0, g.yc, g.Ly];
Cp = C([1, 1:g.Ny, g.Ny], [1, 1:g.Nx, g.Nx]);
end

function [xy, yy, Cy] = padVertically(g, C)
% Cell-centred values extended to the closed base and top only (zero gradient there, as in densityResidual): lines.
xy = g.xc;
yy = [0, g.yc, g.Ly];
Cy = C([1, 1:g.Ny, g.Ny], :);
end

function [xt, yt] = topOfContour(M)
% Highest vertex of the lines of a contour matrix M = [level, n; x, y; ...].
xt = NaN;
yt = -Inf;
k = 1;
while k < size(M, 2)
    n = M(2, k);
    seg = M(:, k + 1:k + n);
    [ymax, i] = max(seg(2, :));
    if ymax > yt
        yt = ymax;
        xt = seg(1, i);
    end
    k = k + n + 1;
end
end

function [i1, i2] = runs(tf)
% Start and end indices of the runs of true values of the logical vector TF.
d = diff([false; tf(:); false]);
i1 = find(d == 1);
i2 = find(d == -1) - 1;
end

function saveFigure(fig, outDir, name, lg)
png = fullfile(outDir, [name, '.png']);
pdf = fullfile(outDir, [name, '.pdf']);
print(fig, '-dpng', '-r300', png);
print(fig, '-dpdf', '-painters', pdf);
say(lg, 'saved %s and %s\n', png, pdf);
close(fig);
end

function say(lg, varargin)
% Print to the screen and to the log file.
fprintf(1, varargin{:});
if lg > 0
    fprintf(lg, varargin{:});
end
end
