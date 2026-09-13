function make_cross_section(xlsxPath, outPath)
%MAKE_CROSS_SECTION  Hydrogeological cross-section of the Fushë-Kuqe–Lezhë aquifer.
%
%   make_cross_section(XLSXPATH, OUTPATH)
%
%   (a) A conceptual coast-perpendicular (W to E) section. Every thickness,
%       head and salinity annotated on the panel is a documented value, read from
%       Cenameri and Beqiraj (2016), who attribute the maximum alluvial thickness
%       and the four gravelly layers to Eftimi (2003) and the piezometric heads to
%       Tartari (2001). The lateral geometry is schematic: it is NOT interpolated
%       from borehole logs, because none exist in the dataset, and no toe position
%       is claimed.
%
%       The two salinities are the total groundwater salinity of the first and the
%       second aquifer, NOT the chloride concentration: Cenameri and Beqiraj give
%       chloride in those wells as about 1000 to 1100 mg/L (their Table 2).
%
%   (b) Hydraulic conductivity of the 32 inside-aquifer wells that carry a K
%       measurement, against straight-line distance from the Adriatic (western)
%       boundary of the aquifer polygon. This panel is data only. Facies classes
%       are the K thresholds of demo/gate3_field.m (coarse K >= 150, medium
%       75 <= K < 150, fine K < 75 m/d), a declared proxy: K is quantised to six
%       values in the dataset.
%
%   Author: D. Zeqiraj.  License: MIT.

    if nargin < 1 || isempty(xlsxPath)
        here = fileparts(mfilename('fullpath'));
        xlsxPath = fullfile(here, '..', 'data', 'Fushe_Kuqe_All_Data.xlsx');
    end
    if nargin < 2 || isempty(outPath), outPath = 'Fig_CrossSection.png'; end

    % ---------------- panel (b) data, straight from the workbook -----------
    T = readtable(xlsxPath, 'Sheet', '2_All_Wells');
    keep = ~isnan(T.K_m_per_day) & strcmpi(string(T.Inside_Aquifer), "YES");
    T = T(keep, :);
    Bd = readtable(xlsxPath, 'Sheet', '3_Boundary_Coords');
    bx = Bd.X_GaussKruger; by = Bd.Y_GaussKruger;

    isCoast = true(numel(bx),1);
    for i = 1:numel(bx)
        near = abs(by - by(i)) <= 750;
        if any(bx(near) < bx(i) - 1), isCoast(i) = false; end
    end
    cx = bx(isCoast); cy = by(isCoast);

    d = zeros(height(T),1);
    for i = 1:height(T)
        d(i) = min(hypot(T.X_GaussKruger(i) - cx, T.Y_GaussKruger(i) - cy)) / 1000;
    end
    K = T.K_m_per_day;
    fac = 1*(K >= 150) + 2*(K >= 75 & K < 150) + 3*(K < 75);
    fprintf('panel (b): %d wells, %d coastal vertices\n', height(T), numel(cx));
    fprintf('   facies coarse/medium/fine = [%d %d %d]\n', sum(fac==1), sum(fac==2), sum(fac==3));
    fprintf('   distance from coast: %.2f to %.2f km\n', min(d), max(d));

    % ---------------- geometry ---------------------------------------------
    Lx = 20; Xw = -2.4;
    Ztop = 120; Zbot = -300;
    x  = linspace(0, Lx, 600);

    zs   = 2 + 38*(x/Lx).^1.7;
    tcov = 35*exp(-x/6.0);
    zcov = zs - tcov;
    tgrv = 7 + 183*exp(-x/5.2);
    zgrv = zcov - tgrv;
    zbed = min(zgrv - 10, -272 + 268*(x/Lx).^1.25);

    % ---------------- figure ------------------------------------------------
    W = 19.0; H = 14.4;
    f = figure('Color','w','Units','centimeters','Position',[2 2 W H], ...
               'PaperUnits','centimeters','PaperPosition',[0 0 W H],'PaperSize',[W H]);

    colCoarse = [0.90 0.49 0.13];
    colMedium = [0.33 0.62 0.33];
    colFine   = [0.20 0.35 0.65];
    colSilt   = [0.80 0.78 0.70];
    colGravel = [0.95 0.89 0.74];
    colBed    = [0.60 0.58 0.56];
    colSea    = [0.66 0.83 0.92];
    colWedge  = [0.36 0.58 0.78];
    blue      = [0.13 0.32 0.65];
    navy      = [0.05 0.18 0.38];

    axW = 16.3; axL = 2.20; hA = 7.70;
    ax1 = axes('Units','centimeters','Position',[axL 6.05 axW hA]); hold(ax1,'on');

    fill(ax1, [Xw 0 0 Xw], [Zbot Zbot 0 0], colSea, 'EdgeColor','none');
    fill(ax1, [x fliplr(x)], [zs fliplr(zcov)], colSilt, ...
         'EdgeColor',[0.52 0.50 0.45],'LineWidth',0.5);
    fill(ax1, [x fliplr(x)], [zcov fliplr(zgrv)], colGravel, ...
         'EdgeColor',[0.62 0.55 0.40],'LineWidth',0.5);
    fill(ax1, [x fliplr(x)], [zgrv fliplr(max(zbed, Zbot*ones(size(x))))], colBed, ...
         'EdgeColor','none');

    for k = 1:3
        zi = zcov - tgrv*k/4;
        m  = x <= 10.5;
        plot(ax1, x(m), zi(m), '-', 'Color',[0.60 0.52 0.38], 'LineWidth',0.7);
    end

    xt = 6.0;
    xw = linspace(0, xt, 200);
    zb = interp1(x, zgrv, xw);
    zc = interp1(x, zcov, xw);
    zi = zb + (zc - zb) .* max(0, 1 - (xw/xt)).^0.85;
    fill(ax1, [xw fliplr(xw)], [zb fliplr(zi)], colWedge, ...
         'EdgeColor',[0.20 0.40 0.62],'LineWidth',1.0,'FaceAlpha',0.82);

    zp = 6 + 0.62*x;
    plot(ax1, x, zp, '--', 'Color', blue, 'LineWidth',1.4);

    for xa = [4.6 5.4 6.2]
        ztopw = interp1(x, zs, xa) + 18;
        plot(ax1, [xa xa], [ztopw interp1(x, zgrv, xa)+28], '-', ...
             'Color',[0.1 0.1 0.1],'LineWidth',1.5);
        plot(ax1, xa, ztopw, 'v','MarkerSize',5, ...
             'MarkerFaceColor',[0.1 0.1 0.1],'MarkerEdgeColor',[0.1 0.1 0.1]);
    end

    % --- labels -------------------------------------------------------------
    text(ax1, Xw/2, -150,'Adriatic Sea','FontSize',8.5,'Rotation',90, ...
         'HorizontalAlignment','center','Color',[0.13 0.33 0.52]);
    text(ax1, 3.1, 112, {'Fushë-Kuqe abstraction field', ...
         'artesian head fell from 8.0 to 1.5 m above ground'}, ...
         'FontSize',7.5,'Color',[0.1 0.1 0.1],'VerticalAlignment','top');
    text(ax1, 10.4, 33,'piezometric surface (schematic)','FontSize',7.5,'Color',blue);
    text(ax1, 10.0, -16,'silt-clay cover, 30 to 40 m at the coast', ...
         'FontSize',7.5,'Color',[0.36 0.34 0.28]);
    text(ax1, 8.6, -54, {'gravel-sand aquifer, 180 to 200 m at the coast,', ...
         'thinning to 5 to 10 m at the eastern margin;', ...
         'up to 4 gravelly layers with silt-clay intercalations'}, ...
         'FontSize',7.5,'Color',[0.42 0.35 0.20],'VerticalAlignment','top');
    text(ax1, 0.55, -120,{'seawater','wedge'},'FontSize',8.5,'FontWeight','bold', ...
         'Color',[0.98 0.99 1.00]);
    text(ax1, 6.6, -150, {'groundwater salinity up to 1500 mg L^{-1}', ...
         'in the first aquifer, 3500 mg L^{-1} in the second'}, ...
         'FontSize',7.5,'Color',navy,'VerticalAlignment','top');
    text(ax1, 14.6, -232,'pre-Quaternary basement','FontSize',7.5,'Color',[0.30 0.30 0.30]);
    text(ax1, 19.8, -283,'maximum alluvial thickness about 270 m (Mat delta)', ...
         'FontSize',7,'Color',[0.30 0.30 0.30],'HorizontalAlignment','right');

    arrow(ax1, 18.3, 78, 14.9, 78, blue, 1.3);
    text(ax1, 18.6, 78,'regional flow','FontSize',7.5,'Color',blue, ...
         'HorizontalAlignment','right','VerticalAlignment','bottom');
    arrow(ax1, 1.1, -196, 3.6, -196, navy, 1.3);
    text(ax1, 3.9, -196,'wedge advances landward','FontSize',7.5,'Color',navy, ...
         'VerticalAlignment','middle');

    set(ax1,'XLim',[Xw Lx],'YLim',[Zbot Ztop],'Box','on','FontSize',8.5, ...
        'TickDir','out','Layer','top','FontName','Arial','XTick',0:4:20,'XMinorTick','on', ...
        'YTick',-300:50:100);
    ylabel(ax1,'elevation  [m a.s.l.]','FontSize',9);

    vex = ((Lx - Xw)*1000/axW) / ((Ztop - Zbot)/hA);
    title(ax1, sprintf('(a)  conceptual W–E hydrogeological section (vertical exaggeration %.0f\\times)', vex), ...
          'FontSize',9.5,'FontWeight','bold');
    fprintf('   vertical exaggeration = %.1f\n', vex);

    % ---- (b) measured K along the same direction ---------------------------
    ax2 = axes('Units','centimeters','Position',[axL 1.45 axW 3.30]); hold(ax2,'on');
    plot(ax2,[Xw Lx],[150 150],':','Color',[0.55 0.55 0.55],'LineWidth',0.8);
    plot(ax2,[Xw Lx],[ 75  75],':','Color',[0.55 0.55 0.55],'LineWidth',0.8);
    h1 = plot(ax2, d(fac==1), K(fac==1), 'o','MarkerSize',6, ...
              'MarkerFaceColor',colCoarse,'MarkerEdgeColor',[0.35 0.20 0.05]);
    h2 = plot(ax2, d(fac==2), K(fac==2), 's','MarkerSize',6, ...
              'MarkerFaceColor',colMedium,'MarkerEdgeColor',[0.12 0.30 0.12]);
    h3 = plot(ax2, d(fac==3), K(fac==3), '^','MarkerSize',6, ...
              'MarkerFaceColor',colFine,'MarkerEdgeColor',[0.08 0.15 0.35]);
    text(ax2, Xw+0.3, 161,'K = 150','FontSize',7,'Color',[0.45 0.45 0.45], ...
         'HorizontalAlignment','left','VerticalAlignment','bottom');
    text(ax2, Xw+0.3,  86,'K = 75','FontSize',7,'Color',[0.45 0.45 0.45], ...
         'HorizontalAlignment','left','VerticalAlignment','bottom');
    legend(ax2,[h1 h2 h3], ...
        {sprintf('coarse, K \\geq 150 (n = %d)', sum(fac==1)), ...
         sprintf('medium, 75 \\leq K < 150 (n = %d)', sum(fac==2)), ...
         sprintf('fine, K < 75 (n = %d)', sum(fac==3))}, ...
        'FontSize',7.5,'Box','off','NumColumns',1,'Location','east');
    set(ax2,'XLim',[Xw Lx],'YLim',[0 235],'Box','on','FontSize',8.5,'TickDir','out','FontName','Arial', ...
        'XTick',0:4:20,'XMinorTick','on','YTick',0:50:200);
    xlabel(ax2,'distance inland from the Adriatic boundary of the aquifer  [km]','FontSize',9);
    ylabel(ax2,'K  [m d^{-1}]','FontSize',9);
    title(ax2,'(b)  measured hydraulic conductivity, 32 inside-aquifer wells', ...
          'FontSize',9.5,'FontWeight','bold');

    try, exportgraphics(f, outPath, 'Resolution', 600);
    catch, print(f, outPath(1:end-4), '-dpng','-r600'); end
    fprintf('written: %s\n', outPath);
end

% -------------------------------------------------------------------------
function arrow(ax, x0, y0, x1, y1, col, lw)
%ARROW  Straight arrow in data coordinates.
    plot(ax, [x0 x1], [y0 y1], '-', 'Color', col, 'LineWidth', lw);
    dx = x1 - x0; dy = y1 - y0; L = hypot(dx, dy);
    if L == 0, return; end
    xl = diff(get(ax,'XLim')); yl = diff(get(ax,'YLim'));
    ux = dx/L; uy = dy/L;
    hx = 0.018*xl; hy = 0.018*yl;
    px = -uy; py = ux;
    p2 = [x1 - 1.7*hx*ux + 0.60*hx*px, y1 - 1.7*hy*uy + 0.60*hy*py];
    p3 = [x1 - 1.7*hx*ux - 0.60*hx*px, y1 - 1.7*hy*uy - 0.60*hy*py];
    patch(ax, [x1 p2(1) p3(1)], [y1 p2(2) p3(2)], col, 'EdgeColor', col);
end
