function solution_flowchart(outDir)
%SOLUTION_FLOWCHART The solution of all the problems of CERTAIN-COAST in one flowchart (portrait, 17 x 23.4 cm).
%   solution_flowchart(OUTDIR) saves fig_solution_flowchart.png (300 dpi) and .pdf in OUTDIR (default: the folder of
%   this file): the problems, and how the project observes, models and calibrates, warns, decides and delivers, with
%   the work package and the part of the Additional files behind each step. Palette and font scale of
%   run_all_figures.m. GNU Octave without a display: xvfb-run -a octave --no-gui --eval "solution_flowchart"
%
%   Copyright 2026 Dulian Zeqiraj. Licensed under the Apache License 2.0.

if nargin < 1 || isempty(outDir)
    outDir = fileparts(mfilename('fullpath'));
end
if exist('OCTAVE_VERSION', 'builtin') ~= 0 && any(strcmp(available_graphics_toolkits(), 'qt'))
    graphics_toolkit('qt');
end
pal = palette();
W = 17; H = 23.4;
fig = figure('Visible', 'off', 'Color', 'w', 'Units', 'centimeters', 'Position', [1 1 W H], ...
             'PaperUnits', 'centimeters', 'PaperSize', [W H], 'PaperPosition', [0 0 W H], ...
             'PaperPositionMode', 'manual', 'InvertHardcopy', 'off');
ax = axes('Parent', fig, 'Units', 'normalized', 'Position', [0 0 1 1], 'XLim', [0 W], 'YLim', [0 H], ...
          'Visible', 'off', 'NextPlot', 'add');

% rows: title, work packages, colour, light fill, top of the band, and the boxes {title, body lines, part tag}
rows = {
 {'THE PROBLEMS', 'at the wellfields, the port and the energy landfall', pal.red, [0.99 0.93 0.93], 22.95, {
   {'Seawater intrusion', {'chloride reaches the', 'supply wells, seen weeks', 'late, between two samples'}, 'Parts 1, 3'}, ...
   {'Sinking coast', {'subsidence and a rising', 'relative sea level: the', 'drivers of all three hazards'}, 'Parts 1, 3'}, ...
   {'Earthquakes', {'a step of pore pressure', 'in each layer, and', 'liquefaction of the ground'}, 'Part 6'}, ...
   {'Droughts and floods', {'compound extremes', 'beyond the record;', 'one lever with', 'opposite effects'}, 'Parts 7, 8'}}}
 {'OBSERVE', 'WP1, WP4', pal.blue, [0.92 0.95 0.99], 19.25, {
   {'Coastal motion', {'InSAR, GNSS and tide', 'gauges give the vertical', 'land motion and sea level'}, 'WP1'}, ...
   {'Network for the warnings', {'robust and certified, with', 'sealed reference channels', 'against shared errors'}, 'Part 7'}, ...
   {'Metered pumping stops', {'by reciprocity, the', 'sensitivities of the decision', 'and the flux scale, no drilling'}, 'Part 10'}}}
 {'MODEL AND|CALIBRATE', 'WP2', pal.darkBlue, [0.91 0.93 0.97], 15.55, {
   {'One coupled model', {'flow, salt, compaction and', 'pore pressure, assembled with', 'the wells as the goal'}, 'Part 4'}, ...
   {'Boundaries and shocks', {'the learned inland boundary', '(BEYOND-GO), the earthquake', 'step (SHOCK-GO), forcing'}, 'Parts 2, 5, 6'}, ...
   {'Calibration, model wrong', {'invariance-first calibration', 'and TRIAL-GO, a robust', 'bandit over structures'}, 'Part 10'}}}
 {'WARN', 'WP3', pal.orange, [0.99 0.94 0.90], 11.85, {
   {'Certified alarm', {'one model for the three', 'hazards, each warning with', 'a stated miss rate'}, 'Part 3'}, ...
   {'Between samples', {'the chance that chloride', 'crosses its limit between', 'two samples, certified'}, 'Parts 3, 7'}, ...
   {'Value before buying', {'each sensor, test and well', 'valued by what it is', 'guaranteed to buy'}, 'Parts 1, 7'}}}
 {'DECIDE', 'WP5', pal.aqua, [0.92 0.97 0.94], 8.15, {
   {'Regimes and roles', {'normal, drought, flood,', 'extreme: what each', 'stakeholder does'}, 'Parts 8, 9'}, ...
   {'Safe decisions', {'deep reinforcement', 'learning inside the', 'certified safe window'}, 'Part 7'}, ...
   {'Recharge wells', {'where to pilot-test and', 'build them: SITE-GO,', 'THRESHOLD-MAR'}, 'Parts 4, 10'}, ...
   {'Operating window', {'pumping and dewatering', 'kept safe for the three', 'hazards at once'}, 'Parts 3, 7'}}}
 {'DELIVER', 'WP5, WP6, WP7', pal.muted, [0.95 0.95 0.94], 4.45, {
   {'Bulletins of IGJEO', {'for the water utility,', 'the port and the energy', 'landfall, every season'}, 'WP5'}, ...
   {'Training and transfer', {'early-career researchers,', 'a training school, staff', 'able to run the system'}, 'WP6'}, ...
   {'Open code and data', {'MATLAB code in open', 'repositories; data and', 'risk management'}, 'WP7'}}}
};
x0 = 2.75; x1 = 15.95; gap = 0.22; bandH = 3.15;
for r = 1:numel(rows)
    R = rows{r};
    ytop = R{5}; ybot = ytop - bandH; col = R{3}; face = R{4};
    % the row label on the left
    rbox(ax, 0.15, ybot, 2.35, bandH, col, col, 0.22);
    tl = strsplit(R{1}, '|'); y1 = ybot + bandH / 2 + 0.35 + (numel(tl) - 1) * 0.20;
    for k = 1:numel(tl)
        text(ax, 1.325, y1 - (k - 1) * 0.40, tl{k}, 'FontName', 'Helvetica', 'FontSize', fs(7.0), 'FontWeight', 'bold', ...
             'Color', 'w', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
    end
    wrapped = wrap_label(R{2}, 18);
    for k = 1:numel(wrapped)
        text(ax, 1.325, ybot + bandH / 2 - 0.25 - (k - 1) * 0.36, wrapped{k}, 'FontName', 'Helvetica', ...
             'FontSize', fs(5.8), 'Color', 'w', 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
    end
    % the band and its boxes
    rbox(ax, x0 - 0.12, ybot, x1 - x0 + 0.24, bandH, face, face, 0.22);
    nb = numel(R{6}); bw = (x1 - x0 - (nb - 1) * gap) / nb;
    for b = 1:nb
        B = R{6}{b};
        bx = x0 + (b - 1) * (bw + gap); by = ybot + 0.17; bh = bandH - 0.34;
        rbox(ax, bx, by, bw, bh, 'w', col, 0.18);
        text(ax, bx + 0.18, by + bh - 0.36, B{1}, 'FontName', 'Helvetica', 'FontSize', fs(6.9), 'FontWeight', 'bold', ...
             'Color', darker(col), 'VerticalAlignment', 'middle');
        for k = 1:numel(B{2})
            text(ax, bx + 0.18, by + bh - 0.86 - (k - 1) * 0.40, B{2}{k}, 'FontName', 'Helvetica', 'FontSize', fs(6.1), ...
                 'Color', [0.13 0.13 0.13], 'VerticalAlignment', 'middle');
        end
        % the part tag, bottom right
        tw = 0.11 * numel(B{3}) + 0.30;
        rbox(ax, bx + bw - tw - 0.12, by + 0.12, tw, 0.36, face, col, 0.12);
        text(ax, bx + bw - tw / 2 - 0.12, by + 0.30, B{3}, 'FontName', 'Helvetica', 'FontSize', fs(5.5), ...
             'FontWeight', 'bold', 'Color', darker(col), 'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
    end
    % the arrow to the next row
    if r < numel(rows)
        yn = rows{r + 1}{5};
        xm = (x0 + x1) / 2;
        arrow(ax, [xm xm], [ybot - 0.02, yn + 0.03], [0.35 0.35 0.35], 1.4);
    end
end
% the feedback loop on the right: live operation sends new data back to the observation and calibration
yA = rows{6}{5} - bandH / 2; yB = rows{2}{5} - bandH / 2;
plot(ax, [x1 + 0.12, 16.55, 16.55], [yA, yA, yB], '-', 'Color', pal.aqua, 'LineWidth', 1.3);
arrow(ax, [16.55, x1 + 0.14], [yB, yB], pal.aqua, 1.3);
text(ax, 16.78, (yA + yB) / 2, 'live operation: new readings re-calibrate (TRIAL-GO), re-index the network and the learning step', ...
     'FontName', 'Helvetica', 'FontSize', fs(5.8), 'Color', darker(pal.aqua), 'Rotation', 90, ...
     'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle');
% key
text(ax, 0.20, 0.55, ['Part n: part of the Additional files where the step is derived and tested;  WPn: work package ' ...
     'of the proposal.  End-user: the Institute of Geosciences (IGJEO).'], 'FontName', 'Helvetica', 'FontSize', fs(5.8), ...
     'Color', pal.ink2, 'VerticalAlignment', 'middle');

png = fullfile(outDir, 'fig_solution_flowchart.png');
pdf = fullfile(outDir, 'fig_solution_flowchart.pdf');
print(fig, '-dpng', '-r350', png);
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
pal.muted = [110 108 103] / 255;
end

function c = darker(c)
c = 0.78 * c;
end

function out = wrap_label(s, n)
words = strsplit(s, ' '); out = {}; cur = '';
for k = 1:numel(words)
    if isempty(cur)
        cur = words{k};
    elseif numel(cur) + 1 + numel(words{k}) <= n
        cur = [cur ' ' words{k}];
    else
        out{end + 1} = cur; cur = words{k}; %#ok<AGROW>
    end
end
out{end + 1} = cur;
end

function rbox(ax, x, y, w, h, face, edge, r)
rectangle('Parent', ax, 'Position', [x y w h], 'Curvature', [min(1, 2 * r / w) min(1, 2 * r / h)], ...
          'FaceColor', face, 'EdgeColor', edge, 'LineWidth', 0.8);
end

function arrow(ax, xs, ys, col, lw)
plot(ax, xs, ys, '-', 'Color', col, 'LineWidth', lw);
x1 = xs(end - 1); y1 = ys(end - 1); x2 = xs(end); y2 = ys(end);
L = hypot(x2 - x1, y2 - y1); ux = (x2 - x1) / L; uy = (y2 - y1) / L;
a = 0.24; b = 0.11;
patch('Parent', ax, 'XData', [x2, x2 - a * ux + b * uy, x2 - a * ux - b * uy], ...
      'YData', [y2, y2 - a * uy - b * ux, y2 - a * uy + b * ux], 'FaceColor', col, 'EdgeColor', col);
end
