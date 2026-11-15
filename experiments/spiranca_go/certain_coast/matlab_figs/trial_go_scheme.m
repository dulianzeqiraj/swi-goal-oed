function trial_go_scheme(outDir)
%TRIAL_GO_SCHEME How TRIAL-GO, the robust calibration bandit over model structures, works in the CERTAIN-COAST system.
%   trial_go_scheme(OUTDIR) draws the diagram (16 x 10 cm) and saves fig_trial_go_scheme.png (300 dpi) and .pdf in
%   OUTDIR (default: the folder of this file). Same palette and font scaling as run_all_figures.m.
%   GNU Octave without a display: xvfb-run -a octave --no-gui --eval "trial_go_scheme"
%
%   Copyright 2026 Dulian Zeqiraj. Licensed under the Apache License 2.0.

if nargin < 1 || isempty(outDir)
    outDir = fileparts(mfilename('fullpath'));
end
if exist('OCTAVE_VERSION', 'builtin') ~= 0 && any(strcmp(available_graphics_toolkits(), 'qt'))
    graphics_toolkit('qt');
end
pal = palette();
W = 16; H = 10;
fig = figure('Visible', 'off', 'Color', 'w', 'Units', 'centimeters', 'Position', [2 2 W H], ...
             'PaperUnits', 'centimeters', 'PaperSize', [W H], 'PaperPosition', [0 0 W H], ...
             'PaperPositionMode', 'manual', 'InvertHardcopy', 'off');
ax = axes('Parent', fig, 'Units', 'normalized', 'Position', [0 0 1 1], 'XLim', [0 W], 'YLim', [0 H], ...
          'Visible', 'off', 'NextPlot', 'add');
navy = pal.darkBlue; ink = [0.12 0.12 0.12]; grey = pal.ink2;
fillN = [0.93 0.95 0.98]; fillO = [0.99 0.94 0.90]; fillG = [0.92 0.97 0.94]; fillL = [0.965 0.965 0.955];
B = 6.4;                                         % body text size (pt, before the 8 % scale of fs)

% ---------------------------------------------------------------------------------------------- left column
card(ax, 0.15, 6.30, 4.60, 3.55, fillN, navy, 'DATA');
txt(ax, 0.35, 8.92, {'\bullet  heads at the observation wells', '\bullet  metered pumping stops at the', ...
                     '    supply wells (Stage 0, no drilling)'}, B, ink);
txt(ax, 0.35, 6.85, {'y_{wj} = \DeltaQ_w g_w(j) + \epsilon'}, 7.0, navy, 'bold');

card(ax, 0.15, 0.15, 4.60, 5.85, fillO, pal.orange, 'ARMS: MODEL STRUCTURES');
armc = [pal.red; pal.muted; pal.aqua; pal.blue; pal.darkBlue];
arms = {'A1  zones, recharge fixed', 'A2  uniform conductivity', 'A3  three facies', 'A4  zones + recharge', ...
        'A5  zones + coastal strip'};
note = {'as in common PEST practice', 'with recharge', 'with recharge', 'recharge estimated', 'with recharge'};
for k = 1:5
    y = 4.95 - (k - 1) * 0.98;
    plot(ax, 0.50, y, 'o', 'MarkerSize', 6, 'MarkerFaceColor', armc(k, :), 'MarkerEdgeColor', 'w', 'LineWidth', 0.6);
    text(ax, 0.75, y, arms{k}, 'FontName', 'Helvetica', 'FontSize', fs(7.0), 'Color', ink, 'FontWeight', 'bold', ...
         'VerticalAlignment', 'middle');
    text(ax, 0.75, y - 0.36, note{k}, 'FontName', 'Helvetica', 'FontSize', fs(6.2), 'Color', grey, ...
         'VerticalAlignment', 'middle');
end

% ---------------------------------------------------------------------------------------------- centre: the loop
card(ax, 5.20, 1.85, 5.60, 8.00, fillL, navy, 'TRIAL-GO: ROBUST CALIBRATION BANDIT');
bw = 2.35; bh = 2.70; xl = 5.50; xr = 8.15; yt = 6.15; yb = 2.30;
box(ax, xl, yt, bw, bh, fillN, navy);  step(ax, xl, yt + bh, '1', 'Robust index', navy);
txt(ax, xl + 0.20, yt + bh - 0.95, {'Gittins index', '\gamma_m(p_m, n_m):', 'Cohen and', 'Treetanthiploet', '(2022), App. D'}, B, ink);
box(ax, xr, yt, bw, bh, fillN, navy);  step(ax, xr, yt + bh, '2', 'Play the arm', navy);
txt(ax, xr + 0.20, yt + bh - 0.95, {'of smallest index:', 'one Levenberg-', 'Marquardt step,', 'N_m + 1 model runs'}, B, ink);
box(ax, xr, yb, bw, bh, fillN, navy);  step(ax, xr, yb + bh, '3', 'Check', navy);
txt(ax, xr + 0.20, yb + bh - 0.95, {'a reading new to', 'this arm:', 'miss h = 1 if y_{wj}', 'is outside its', '90% interval'}, B, ink);
box(ax, xl, yb, bw, bh, fillN, navy);  step(ax, xl, yb + bh, '4', 'Update', navy);
txt(ax, xl + 0.20, yb + bh - 0.95, {'s_m \leftarrow s_m + h', 'n_m \leftarrow n_m + 1', 'miss rate p_m:', 'misspecification'}, B, ink);
arrow(ax, [xl + bw, xr], [yt + 1.25, yt + 1.25], navy);                         % 1 -> 2
arrow(ax, [xr + bw / 2, xr + bw / 2], [yt, yb + bh], navy);                     % 2 -> 3
arrow(ax, [xr, xl + bw], [yb + 1.25, yb + 1.25], navy);                         % 3 -> 4
arrow(ax, [xl + bw / 2, xl + bw / 2], [yb + bh, yt], navy);                     % 4 -> 1

rbox(ax, 5.20, 0.15, 5.60, 1.45, fillL, pal.refGray, 0.18);
txt(ax, 5.38, 1.18, {'\bfreciprocity:\rm a reading is the decision''s sensitivity', ...
                     '\bfinvariance:\rm heads cannot fix the flux scale;', ...
                     '    a metered reading can (it scales as 1/c)'}, 6.2, ink);

arrow(ax, [4.75 5.20], [8.05 8.05], grey);                      % data -> loop
arrow(ax, [4.75 5.20], [3.60 3.60], pal.orange);                % arms -> loop

% ---------------------------------------------------------------------------------------------- right column
card(ax, 11.25, 6.30, 4.60, 3.55, fillG, pal.aqua, 'STOP AND CONDITION');
txt(ax, 11.45, 8.92, {'when the budget of runs is spent:', '\bullet  keep the arm of lowest miss', ...
                      '    rate (at least 5 readings)', '\bullet  calibrate it on all data'}, B, ink);
card(ax, 11.25, 0.15, 4.60, 5.85, fillG, pal.aqua, 'DECISIONS');
txt(ax, 11.45, 5.05, {'\bullet  heads and intrusion risk at', '    the supply wells, with a checked', ...
                      '    interval', '\bullet  recharge sites (SITE-GO)', '\bullet  warnings and the decision', ...
                      '    agent of Part 7', '\bullet  the miss rate of every', '    structure, reported'}, B, ink);
arrow(ax, [10.80 11.25], [8.05 8.05], pal.aqua);
text(ax, 11.03, 8.40, 'budget', 'FontName', 'Helvetica', 'FontSize', fs(5.6), 'Color', grey, ...
     'HorizontalAlignment', 'center');
arrow(ax, [13.55 13.55], [6.30 6.00], pal.aqua);

png = fullfile(outDir, 'fig_trial_go_scheme.png');
pdf = fullfile(outDir, 'fig_trial_go_scheme.pdf');
print(fig, '-dpng', '-r375', png);
print(fig, '-dpdf', '-painters', pdf);
close(fig);
fprintf('saved %s and %s\n', png, pdf);
end

% ================================================================================================== helpers
function y = fs(n)
y = 1.08 * n;                     % the font scale of run_all_figures.m
end

function pal = palette()
pal.blue = [42 120 214] / 255; pal.darkBlue = [24 79 149] / 255; pal.orange = [235 104 52] / 255;
pal.aqua = [27 175 122] / 255; pal.red = [208 59 59] / 255; pal.ink2 = [82 81 78] / 255;
pal.muted = [137 135 129] / 255; pal.refGray = [178 177 170] / 255;
end

function rbox(ax, x, y, w, h, face, edge, r)
rectangle('Parent', ax, 'Position', [x y w h], 'Curvature', [min(1, 2 * r / w) min(1, 2 * r / h)], ...
          'FaceColor', face, 'EdgeColor', edge, 'LineWidth', 0.9);
end

function box(ax, x, y, w, h, face, edge)
rbox(ax, x, y, w, h, face, edge, 0.20);
end

function card(ax, x, y, w, h, face, edge, title)
% a rounded box with a coloured title bar
rbox(ax, x, y, w, h, face, edge, 0.20);
rbox(ax, x, y + h - 0.52, w, 0.52, edge, edge, 0.20);
patch('Parent', ax, 'XData', [x x + w x + w x], 'YData', [y + h - 0.52, y + h - 0.52, y + h - 0.28, y + h - 0.28], ...
      'FaceColor', edge, 'EdgeColor', 'none');
text(ax, x + w / 2, y + h - 0.26, title, 'FontName', 'Helvetica', 'FontSize', fs(6.8), 'FontWeight', 'bold', ...
     'Color', 'w', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
end

function step(ax, x, ytop, s, title, col)
% the number of a step in a filled circle and its title, at the top of a box
plot(ax, x + 0.30, ytop - 0.36, 'o', 'MarkerSize', 8.5, 'MarkerFaceColor', col, 'MarkerEdgeColor', col);
text(ax, x + 0.30, ytop - 0.36, s, 'FontName', 'Helvetica', 'FontSize', fs(6.6), 'FontWeight', 'bold', 'Color', 'w', ...
     'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
text(ax, x + 0.58, ytop - 0.36, title, 'FontName', 'Helvetica', 'FontSize', fs(7.0), 'FontWeight', 'bold', ...
     'Color', col, 'VerticalAlignment', 'middle');
end

function txt(ax, x, y, lines, size, col, weight)
if nargin < 7, weight = 'normal'; end
dy = 0.0352 * size * 1.08 * 1.40;            % line pitch in cm for a font of SIZE pt
for k = 1:numel(lines)
    text(ax, x, y - (k - 1) * dy, lines{k}, 'FontName', 'Helvetica', 'FontSize', fs(size), 'Color', col, ...
         'FontWeight', weight, 'VerticalAlignment', 'middle', 'Interpreter', 'tex');
end
end

function arrow(ax, xs, ys, col)
plot(ax, xs, ys, '-', 'Color', col, 'LineWidth', 1.1);
x1 = xs(end - 1); y1 = ys(end - 1); x2 = xs(end); y2 = ys(end);
L = hypot(x2 - x1, y2 - y1); ux = (x2 - x1) / L; uy = (y2 - y1) / L;
a = 0.20; b = 0.085;
patch('Parent', ax, 'XData', [x2, x2 - a * ux + b * uy, x2 - a * ux - b * uy], ...
      'YData', [y2, y2 - a * uy - b * ux, y2 - a * uy + b * ux], 'FaceColor', col, 'EdgeColor', col);
end
