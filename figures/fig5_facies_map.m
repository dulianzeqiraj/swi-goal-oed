function fig5_facies_map(xlsxfile, outdir)
%FIG5_FACIES_MAP  Well map of the Tirana-Fushe-Kuqe-Lezhe aquifer, coloured by
%   the K-threshold facies proxy used throughout the paper.
%
%   fig5_facies_map(xlsxfile, outdir)
%
%   Reads the released workbook (sheet 2_All_Wells for well IDs, Gauss-Kruger
%   coordinates and hydraulic conductivity; sheet 3_Boundary_Coords for the
%   aquifer polygon) and plots every well that carries a K value, classified by
%   the same rule the design analysis uses:
%
%       coarse   K >= 150 m/day
%       medium   75 <= K < 150 m/day
%       fine     K <  75 m/day
%
%   Wells inside the aquifer-boundary polygon (the estimation set for the
%   cross-facies correlation) are drawn filled; those outside are drawn open.
%   Class counts and the per-class mean +/- standard deviation printed in the
%   legend are computed from the data at run time; nothing is hardcoded.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1 || isempty(xlsxfile)
        xlsxfile = fullfile(fileparts(mfilename('fullpath')), '..', 'data', 'Fushe_Kuqe_All_Data.xlsx');
    end
    if nargin < 2 || isempty(outdir), outdir = pwd; end

    % ---- data ------------------------------------------------------------
    Braw = readmatrix(xlsxfile, 'Sheet', '3_Boundary_Coords');
    B = Braw(:, 2:3); B = B(all(isfinite(B), 2), :);
    T = readtable(xlsxfile, 'Sheet', '2_All_Wells');
    X = T{:, 2}; Y = T{:, 3}; K = T{:, 4};
    keep = isfinite(X) & isfinite(Y) & isfinite(K);
    X = X(keep); Y = Y(keep); K = K(keep);

    fac = 1 * (K >= 150) + 2 * (K >= 75 & K < 150) + 3 * (K < 75);
    inside = inpolygon(X, Y, B(:, 1), B(:, 2));

    lbl = {'coarse gravel', 'medium gravel in a sandy matrix', 'fine gravel with silty-clay'};
    col = [0.90 0.49 0.13; 0.20 0.60 0.25; 0.16 0.36 0.66];
    mk  = {'o', 's', '^'};

    fprintf('=== Figure 5: well classification by the K-threshold rule ===\n');
    fprintf('wells with K: %d   inside polygon: %d   outside: %d\n', ...
            numel(K), sum(inside), sum(~inside));
    leg = strings(1, 3);
    for c = 1:3
        s = (fac == c);
        leg(c) = sprintf('%s:  K = %.0f \\pm %.0f m d^{-1}  (n = %d)', ...
                         lbl{c}, mean(K(s)), std(K(s)), sum(s));
        fprintf('  %-32s n=%2d  K = %6.1f +/- %4.1f  (range %g-%g)\n', ...
                lbl{c}, sum(s), mean(K(s)), std(K(s)), min(K(s)), max(K(s)));
    end

    % ---- plot (km relative to the polygon origin, Gauss-Kruger preserved) --
    f = figure('Color', 'w', 'Position', [80 60 760 1020], 'Visible', 'off'); hold on
    hB = plot(B(:, 1)/1000, B(:, 2)/1000, 'k-', 'LineWidth', 1.2);
    h = gobjects(1, 3);
    for c = 1:3
        s = fac == c & inside;
        h(c) = plot(X(s)/1000, Y(s)/1000, mk{c}, 'MarkerSize', 7, ...
                    'MarkerFaceColor', col(c, :), 'MarkerEdgeColor', 'k', 'LineWidth', 0.6);
        o = fac == c & ~inside;
        if any(o)
            plot(X(o)/1000, Y(o)/1000, mk{c}, 'MarkerSize', 7, ...
                 'MarkerFaceColor', 'w', 'MarkerEdgeColor', col(c, :), 'LineWidth', 1.1, ...
                 'HandleVisibility', 'off');
        end
    end
    hOut = plot(NaN, NaN, 'o', 'MarkerSize', 7, 'MarkerFaceColor', 'w', ...
                'MarkerEdgeColor', [0.35 0.35 0.35], 'LineWidth', 1.1);

    axis equal
    xl = [min(B(:,1)) max(B(:,1))]/1000 + [-1.5 1.5];
    yl = [min(B(:,2)) max(B(:,2))]/1000 + [-2 2];
    axis([xl yl]); grid on; box on
    set(gca, 'FontSize', 11, 'Layer', 'top');
    xlabel('Easting  [km, Gauss-Kruger zone 4]', 'FontSize', 12);
    ylabel('Northing [km, Gauss-Kruger zone 4]', 'FontSize', 12);
    title(sprintf('Wells with measured K (n = %d), classified by the K-threshold facies proxy', numel(K)), ...
          'FontWeight', 'normal', 'FontSize', 12);
    legend([h hOut], [leg, "outside the aquifer polygon (excluded from \rho_F)"], ...
           'Location', 'southoutside', 'Box', 'off', 'FontSize', 9);

    % north arrow and scale bar, placed inside the axes
    x0 = xl(1) + 0.10*diff(xl); y0 = yl(1) + 0.86*diff(yl);
    annotation('textarrow', normx(gca, [x0 x0]), normy(gca, [y0 y0+0.06*diff(yl)]), ...
               'String', 'N', 'FontSize', 11, 'FontWeight', 'bold');
    xb = xl(1) + 0.08*diff(xl); yb = yl(1) + 0.06*diff(yl);
    plot([xb xb+5], [yb yb], 'k-', 'LineWidth', 2.5, 'HandleVisibility', 'off');
    text(xb+2.5, yb + 0.015*diff(yl), '5 km', 'HorizontalAlignment', 'center', 'FontSize', 10);

    save_figure(f, fullfile(outdir, 'Fig5_FaciesMap.png'), 600);
    fprintf('Fig5_FaciesMap.png written (600 dpi).\n');
end

function n = normx(ax, x)
    p = get(ax, 'Position'); xl = get(ax, 'XLim');
    n = p(1) + (x - xl(1)) / diff(xl) * p(3);
end
function n = normy(ax, y)
    p = get(ax, 'Position'); yl = get(ax, 'YLim');
    n = p(2) + (y - yl(1)) / diff(yl) * p(4);
end
