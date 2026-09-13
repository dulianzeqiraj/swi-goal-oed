function make_fig_wellmap(xlsxPath, outPath)
%MAKE_FIG_WELLMAP  Well map of the Tirana-Fushë-Kuqe-Lezhë aquifer, from data.
%
%   make_fig_wellmap(XLSXPATH, OUTPATH)
%
%   Plots the aquifer-boundary polygon and every well in the dataset that
%   carries a hydraulic conductivity, classified by the SAME K thresholds the
%   design uses (demo/gate3_field.m: coarse K >= 150, medium 75 <= K < 150,
%   fine K < 75 m/d). Wells outside the boundary polygon are drawn open,
%   because the facies prior of Gate 3 is built from the inside wells only.
%
%   Every count and every statistic printed on the panel is computed here from
%   the workbook and echoed to the console, so the figure is reproducible.
%
%   Author: D. Zeqiraj.  License: MIT.

    if nargin < 1 || isempty(xlsxPath)
        here = fileparts(mfilename('fullpath'));
        xlsxPath = fullfile(here, '..', 'data', 'Fushe_Kuqe_All_Data.xlsx');
    end
    if nargin < 2 || isempty(outPath), outPath = 'Fig_WellMap.png'; end

    T  = readtable(xlsxPath, 'Sheet', '2_All_Wells');
    Bd = readtable(xlsxPath, 'Sheet', '3_Boundary_Coords');

    hasK = ~isnan(T.K_m_per_day);
    Tk   = T(hasK, :);
    inside = strcmpi(string(Tk.Inside_Aquifer), "YES");
    K   = Tk.K_m_per_day;
    fac = 1*(K >= 150) + 2*(K >= 75 & K < 150) + 3*(K < 75);

    bx = Bd.X_GaussKruger/1000; by = Bd.Y_GaussKruger/1000;
    wx = Tk.X_GaussKruger/1000; wy = Tk.Y_GaussKruger/1000;

    % polygon area by the shoelace formula, for the reported core area
    A = abs(sum(bx.*circshift(by,-1) - circshift(bx,-1).*by))/2;

    names = {'coarse','medium','fine'};
    fprintf('wells with K: %d   inside the polygon: %d\n', height(Tk), sum(inside));
    fprintf('polygon area (shoelace): %.1f km^2, %d vertices\n', A, height(Bd));
    st = zeros(3,4);
    for q = 1:3
        m = fac == q & inside;
        st(q,:) = [sum(fac==q), sum(m), mean(K(m)), std(K(m))];
        fprintf('  %-7s all %2d, inside %2d, K = %5.1f +- %4.1f m/d (inside wells)\n', ...
                names{q}, st(q,1), st(q,2), st(q,3), st(q,4));
    end

    colC = [0.90 0.49 0.13]; colM = [0.33 0.62 0.33]; colF = [0.20 0.35 0.65];
    cols = {colC, colM, colF};
    mk   = {'o','s','^'};

    W = 17.0; H = 15.0;
    f = figure('Color','w','Units','centimeters','Position',[2 2 W H], ...
               'PaperUnits','centimeters','PaperPosition',[0 0 W H],'PaperSize',[W H]);

    ax = axes('Units','centimeters','Position',[1.75 1.30 8.4 13.1]); hold(ax,'on');
    fill(ax, bx, by, [0.87 0.93 0.97], 'EdgeColor',[0.15 0.35 0.62],'LineWidth',0.9);
    h = gobjects(1,3);
    for q = 1:3
        m = fac == q & inside;
        h(q) = plot(ax, wx(m), wy(m), mk{q}, 'MarkerSize',5.5, ...
                    'MarkerFaceColor',cols{q}, 'MarkerEdgeColor',0.35*cols{q});
        o = fac == q & ~inside;
        plot(ax, wx(o), wy(o), mk{q}, 'MarkerSize',5.5, ...
             'MarkerFaceColor','none','MarkerEdgeColor',cols{q},'LineWidth',1.1);
    end
    set(ax,'FontSize',8.5,'FontName','Arial','Box','on','TickDir','out', ...
        'XGrid','on','YGrid','on','GridLineStyle',':','GridAlpha',0.25,'Layer','top');
    axis(ax,'equal');
    xlabel(ax,'easting  [km, Gauss-Krüger zone 4]','FontSize',9);
    ylabel(ax,'northing  [km, Gauss-Krüger zone 4]','FontSize',9);

    % north arrow and scale bar, in data coordinates
    xl = get(ax,'XLim'); yl = get(ax,'YLim');
    xa = xl(1) + 0.86*diff(xl); ya = yl(1) + 0.90*diff(yl);
    plot(ax,[xa xa],[ya ya+0.055*diff(yl)],'k-','LineWidth',1.3);
    plot(ax, xa, ya+0.055*diff(yl),'k^','MarkerFaceColor','k','MarkerSize',5);
    text(ax, xa, ya-0.012*diff(yl),'N','FontSize',9,'FontWeight','bold', ...
         'HorizontalAlignment','center','VerticalAlignment','top');
    xs = xl(1) + 0.07*diff(xl); ys = yl(1) + 0.035*diff(yl);
    plot(ax,[xs xs+5],[ys ys],'k-','LineWidth',1.8);
    plot(ax,[xs xs],[ys-0.008*diff(yl) ys+0.008*diff(yl)],'k-','LineWidth',1.2);
    plot(ax,[xs+5 xs+5],[ys-0.008*diff(yl) ys+0.008*diff(yl)],'k-','LineWidth',1.2);
    text(ax, xs+2.5, ys+0.012*diff(yl),'5 km','FontSize',8, ...
         'HorizontalAlignment','center','VerticalAlignment','bottom');

    % ---- information panel -------------------------------------------------
    pa = axes('Units','centimeters','Position',[10.55 1.30 6.05 13.1]);
    set(pa,'XLim',[0 1],'YLim',[0 1],'XTick',[],'YTick',[],'Box','on', ...
        'XColor',[0.75 0.75 0.75],'YColor',[0.75 0.75 0.75]); hold(pa,'on');
    set(pa,'Color',[0.985 0.985 0.985]);

    y = 0.955;
    text(pa,0.5,y,'STUDY SITE','FontSize',8.5,'FontWeight','bold', ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.042;
    text(pa,0.5,y,'Tirana–Fushë-Kuqe–Lezhë','FontSize',9,'FontWeight','bold', ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.036;
    text(pa,0.5,y,'alluvial aquifer system','FontSize',8.5,'FontAngle','italic', ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.050;
    rule(pa,y); y = y - 0.042;

    text(pa,0.5,y,'AQUIFER BOUNDARY','FontSize',8.5,'FontWeight','bold', ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.040;
    text(pa,0.5,y,sprintf('%d polygon vertices,  %.0f km^2', height(Bd), A), ...
         'FontSize',8.5,'HorizontalAlignment','center','FontName','Arial'); y = y - 0.050;
    rule(pa,y); y = y - 0.042;

    text(pa,0.5,y,'FACIES, BY K THRESHOLD','FontSize',8.5,'FontWeight','bold', ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.036;
    text(pa,0.5,y,sprintf('%d wells with measured K,  %d inside', height(Tk), sum(inside)), ...
         'FontSize',8,'FontAngle','italic','HorizontalAlignment','center','FontName','Arial');
    y = y - 0.055;

    lab = {sprintf('coarse gravel,  K \\geq 150'), ...
           sprintf('medium gravel,  75 \\leq K < 150'), ...
           sprintf('fine gravel,  K < 75')};
    for q = 1:3
        plot(pa, 0.10, y, mk{q}, 'MarkerSize',6, ...
             'MarkerFaceColor',cols{q}, 'MarkerEdgeColor',0.35*cols{q});
        text(pa,0.19,y,lab{q},'FontSize',8.5,'FontWeight','bold','FontName','Arial');
        y = y - 0.036;
        text(pa,0.19,y,sprintf('inside n = %d  (of %d);  K = %.0f \\pm %.0f m d^{-1}', ...
             st(q,2), st(q,1), st(q,3), st(q,4)),'FontSize',8,'FontName','Arial');
        y = y - 0.052;
    end
    text(pa,0.08,y,'open symbols: wells outside the polygon,','FontSize',7.5, ...
         'FontAngle','italic','FontName','Arial'); y = y - 0.030;
    text(pa,0.08,y,'excluded from the facies prior','FontSize',7.5, ...
         'FontAngle','italic','FontName','Arial'); y = y - 0.046;
    rule(pa,y); y = y - 0.042;

    text(pa,0.5,y,'COORDINATES','FontSize',8.5,'FontWeight','bold', ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.038;
    text(pa,0.5,y,'Gauss-Krüger zone 4','FontSize',8.5, ...
         'HorizontalAlignment','center','FontName','Arial'); y = y - 0.034;
    text(pa,0.5,y,'Krasovsky-1940 datum','FontSize',8.5, ...
         'HorizontalAlignment','center','FontName','Arial');

    try, exportgraphics(f, outPath, 'Resolution', 600);
    catch, print(f, outPath(1:end-4), '-dpng','-r600'); end
    fprintf('written: %s\n', outPath);
end

function rule(pa, y)
    plot(pa,[0.06 0.94],[y y],'-','Color',[0.80 0.80 0.80],'LineWidth',0.7);
end
