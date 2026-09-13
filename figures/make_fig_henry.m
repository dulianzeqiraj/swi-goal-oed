function toe = make_fig_henry(Nx, Nz, outPath)
%MAKE_FIG_HENRY  Henry benchmark figure at journal print size, validated solver.
%
%   toe = make_fig_henry(NX, NZ, OUTPATH)
%
%   Uses the solver that carries the discrete adjoint and passes Gate 1
%   (src/vd_residual.m through src/vd_solve_forward.m), so the figure, the
%   gradient check and the design all rest on one discretization.
%
%   Panel (a) is the steady relative-salinity field with isochlors and the toe
%   of the mid-isochlor at the base. Panel (b) is the mesh-refinement sequence
%   of that toe, recomputed here, which is the evidence for the stability claim.
%
%   Author: D. Zeqiraj.  License: MIT.

    if nargin < 1 || isempty(Nx), Nx = 41; end
    if nargin < 2 || isempty(Nz), Nz = 21; end
    if nargin < 3 || isempty(outPath), outPath = 'Fig_Henry.png'; end
    here = fileparts(mfilename('fullpath'));
    addpath(fullfile(here,'..','src'));

    [C, g, nF] = solve_at(Nx, Nz);
    toe = toe_at_base(C, g);
    fprintf('Henry %dx%d: toe = %.4f m (%.4f L), |F| = %.2e\n', Nx, Nz, toe, toe/g.Lx, nF);

    meshes = [16 8; 32 16; 41 21; 61 31; 81 41];
    tt = zeros(size(meshes,1),1); dd = zeros(size(meshes,1),1);
    for k = 1:size(meshes,1)
        [Ck, gk] = solve_at(meshes(k,1), meshes(k,2));
        tt(k) = toe_at_base(Ck, gk);
        dd(k) = gk.Lx/meshes(k,1);
        fprintf('   %2dx%2d  dx = %.4f m  toe = %.4f m  (%.4f L)\n', ...
                meshes(k,1), meshes(k,2), dd(k), tt(k), tt(k)/gk.Lx);
    end

    [Xc,Yc] = meshgrid(g.xc, g.yc);
    xr = linspace(0,g.Lx,401); yr = linspace(0,g.Ly,201);
    [Xr,Yr] = meshgrid(xr,yr);
    Cr = interp2(Xc,Yc,C,Xr,Yr,'linear');
    Cr(Cr<0) = 0; Cr(Cr>1) = 1;

    W = 19.0; H = 9.0;
    f = figure('Color','w','Units','centimeters','Position',[2 2 W H], ...
               'PaperUnits','centimeters','PaperPosition',[0 0 W H],'PaperSize',[W H]);

    ax1 = axes('Units','centimeters','Position',[1.65 1.45 10.5 6.35]); hold(ax1,'on');
    contourf(ax1, Xr, Yr, Cr, 0:0.05:1, 'LineStyle','none');
    try, colormap(ax1, turbo); catch, colormap(ax1, jet); end
    try, clim(ax1,[0 1]); catch, caxis(ax1,[0 1]); end
    [Ci,hi] = contour(ax1, Xr, Yr, Cr, 0.1:0.2:0.9, 'LineColor','k','LineWidth',0.5);
    try, clabel(Ci, hi, 'FontSize',7,'Color','k','LabelSpacing',260); catch, end
    contour(ax1, Xr, Yr, Cr, [0.5 0.5], 'LineColor','w','LineWidth',2.0);
    plot(ax1, toe, 0, 'v','MarkerSize',9,'MarkerFaceColor','w','MarkerEdgeColor','k','LineWidth',1.1);
    % with the corrected diffusivity the toe sits past mid-domain, so the label has to
    % hang to the left of the marker or it runs off the axes
    if toe > 0.6*g.Lx
        text(ax1, toe-0.05, 0.085, sprintf('toe = %.2f m  (%.3f L_x)', toe, toe/g.Lx), ...
             'Color','w','FontWeight','bold','FontSize',8.5,'FontName','Arial', ...
             'HorizontalAlignment','right');
    else
        text(ax1, toe+0.03, 0.085, sprintf('toe = %.2f m  (%.3f L_x)', toe, toe/g.Lx), ...
             'Color','w','FontWeight','bold','FontSize',8.5,'FontName','Arial');
    end
    text(ax1, 0.05, 0.93, sprintf('%d \\times %d grid', g.Nx, g.Ny), ...
         'Color','w','FontSize',8.5,'FontName','Arial');
    axis(ax1,'equal'); axis(ax1,[0 g.Lx 0 g.Ly]);
    set(ax1,'FontSize',8.5,'FontName','Arial','Layer','top','Box','on','TickDir','out');
    xlabel(ax1,'x  [m]    (freshwater inflow at left, sea at right)','FontSize',9);
    ylabel(ax1,'z  [m]','FontSize',9);
    title(ax1,'(a)  steady relative salinity  c = C/C_s','FontSize',9.5,'FontWeight','bold');
    cb = colorbar(ax1,'Units','centimeters');
    set(cb,'Position',[12.35 1.45 0.28 6.35],'FontSize',8,'FontName','Arial');
    try, cb.Label.String = 'c = C/C_s'; cb.Label.FontSize = 8.5; catch, ylabel(cb,'c = C/C_s'); end

    ax2 = axes('Units','centimeters','Position',[15.05 1.45 3.45 6.35]); hold(ax2,'on');
    % The independent finite-element solution of demo/gate2_henry.m on the same 41 by 21
    % cell, drawn as a line rather than a literature "band": it is a run in this
    % repository, so it can be quoted, whereas the 1.1 to 1.3 m band the earlier version
    % showed was uncited and belonged to the parameter set Voss (1984) warns against.
    FE_41x21 = 1.3776;
    plot(ax2, [0 0.14], FE_41x21*[1 1], '--', 'LineWidth', 1.0, 'Color',[0.55 0.35 0.15]);
    text(ax2, 0.137, FE_41x21-0.004, 'finite-element solver, 41\times21', ...
         'FontSize',7,'Color',[0.55 0.35 0.15], ...
         'HorizontalAlignment','right','VerticalAlignment','top','FontName','Arial');
    plot(ax2, dd, tt, 'o-','LineWidth',1.3,'MarkerSize',5, ...
         'Color',[0.13 0.32 0.65],'MarkerFaceColor',[0.13 0.32 0.65]);
    for k = 1:numel(tt)
        if ismember(k,[1 numel(tt)])
            text(ax2, dd(k), tt(k)+0.006, sprintf('%d\\times%d', meshes(k,1), meshes(k,2)), ...
                 'FontSize',7,'HorizontalAlignment','center','VerticalAlignment','bottom', ...
                 'FontName','Arial');
        end
    end
    set(ax2,'FontSize',8.5,'FontName','Arial','Box','on','TickDir','out', ...
        'XLim',[0 0.14],'YLim',[1.36 1.44]);
    xlabel(ax2,'grid spacing  \Deltax  [m]','FontSize',9);
    ylabel(ax2,'toe  [m]','FontSize',9);
    title(ax2,'(b)  mesh refinement','FontSize',9.5,'FontWeight','bold');

    try, exportgraphics(f, outPath, 'Resolution', 600);
    catch, print(f, outPath(1:end-4), '-dpng','-r600'); end
    fprintf('written: %s\n', outPath);
end

% -------------------------------------------------------------------------
function [C, g, nF] = solve_at(Nx, Nz)
    P = vd_params(); g = make_grid(Nx, Nz, 2.0, 1.0);
    [U, nF] = vd_solve_forward(zeros(g.N,1), g, P, 1e-12);
    C = reshape(U(g.N+1:2*g.N), g.Nx, g.Ny).';
end

function toe = toe_at_base(C, g)
    xc = g.xc; cb = C(1,:); toe = NaN;
    for i = 1:g.Nx-1
        if (cb(i)-0.5)*(cb(i+1)-0.5) < 0
            toe = xc(i) + (0.5-cb(i))/(cb(i+1)-cb(i))*(xc(i+1)-xc(i)); return;
        end
    end
end
