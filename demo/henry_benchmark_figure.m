function toe = henry_benchmark_figure(Nx, Ny, solver)
%HENRY_BENCHMARK_FIGURE  Display the Henry-problem salinity field for benchmark
%   validation of the variable-density solver, and write a publication figure.
%
%   toe = HENRY_BENCHMARK_FIGURE(Nx, Ny, solver)
%
%   Solves the classic Henry seawater-intrusion problem (dissertation §4.1,
%   eqs 1.1/1.2/4.1; phi=0.35, K=1e-2 m/s, eps=0.025, drho/dC=0.7143,
%   Q=6.6e-5 m^2/s, D=6.6e-6 m^2/s, 2 m x 1 m) and plots the relative-salinity
%   field c=C/Cs with isochlors and the 0.5-isochlor toe at the aquifer base.
%   The classic-Henry reference toe band is annotated for benchmark comparison.
%
%   INPUTS (all optional)
%     Nx, Ny : grid (default 32 x 16; finer = smoother, slower)
%     solver : function handle  c = solver(g, P)  returning the Ny-by-Nx
%              relative-salinity field on grid g. DEFAULT = the reference
%              coupled solver (vd_residual + vd_solve_forward). To validate
%              YOUR production solver, pass your own handle here (or wire it
%              through my_solver_residual.m) so this figure certifies YOUR
%              solver against the benchmark.
%
%   OUTPUT
%     toe : x-position [m] of the 0.5-isochlor at the aquifer base.
%
%   Author: D. Zeqiraj.  License: MIT.
    here = fileparts(mfilename('fullpath')); addpath(fullfile(here,'..','src'));
    if nargin<1 || isempty(Nx), Nx=32; end
    if nargin<2 || isempty(Ny), Ny=16; end
    if nargin<3 || isempty(solver), solver=@reference_solver; end
    P = vd_params(); g = make_grid(Nx,Ny,2.0,1.0);

    C = solver(g,P);                       % Ny-by-Nx relative salinity in [0,1]

    % --- 0.5-isochlor toe at the base (bottom row) -------------------------
    xc = g.xc; cb = C(1,:); toe = NaN;
    for i=1:g.Nx-1
        if (cb(i)-0.5)*(cb(i+1)-0.5) < 0
            toe = xc(i) + (0.5-cb(i))/(cb(i+1)-cb(i))*(xc(i+1)-xc(i)); break;
        end
    end
    fprintf('Henry solve: 0.5-isochlor toe at base x_toe = %.3f m  (L = %.1f m)\n', toe, g.Lx);
    fprintf('Classic-Henry reference toe (0.5 isochlor at base): ~1.1-1.3 m.\n');

    % --- smooth render grid ------------------------------------------------
    [Xc,Yc] = meshgrid(g.xc,g.yc);
    xr = linspace(0,g.Lx,201); yr = linspace(0,g.Ly,101); [Xr,Yr] = meshgrid(xr,yr);
    Cr = interp2(Xc,Yc,C,Xr,Yr,'linear');
    Cr(Cr<0)=0; Cr(Cr>1)=1;

    % --- figure ------------------------------------------------------------
    figure('Color','w','Position',[80 80 760 440]);
    contourf(Xr,Yr,Cr,0:0.05:1,'LineStyle','none'); hold on;
    try, colormap(turbo); catch, colormap(jet); end
    caxis([0 1]);
    [Ciso,hiso] = contour(Xr,Yr,Cr,0.1:0.2:0.9,'LineColor',[0 0 0],'LineWidth',0.5);
    try, clabel(Ciso,hiso,'FontSize',8,'Color','k'); catch, end
    contour(Xr,Yr,Cr,[0.5 0.5],'LineColor','w','LineWidth',2.2);     % 0.5 isochlor
    if isfinite(toe)
        plot(toe,0,'v','MarkerSize',11,'MarkerFaceColor','w','MarkerEdgeColor','k','LineWidth',1.2);
        text(toe,0.06,sprintf(' toe = %.2f m',toe),'Color','w','FontWeight','bold','FontSize',10);
    end
    axis equal; axis([0 g.Lx 0 g.Ly]);
    set(gca,'FontSize',11,'Layer','top','Box','on');
    xlabel('x [m]   (freshwater inflow at left, sea at right)','FontSize',12);
    ylabel('z [m]','FontSize',12);
    title('Henry problem - variable-density benchmark validation','FontSize',13,'FontWeight','normal');
    cb_ = colorbar;
    try, cb_.Label.String = 'relative salinity  c = C/C_s';
    catch, try, ylabel(cb_,'relative salinity  c = C/C_s'); catch, end; end
    text(0.05,0.92,sprintf('%dx%d grid',g.Nx,g.Ny),'Color','w','FontSize',10);
    try, legend(hiso,{'isochlors (0.1:0.2:0.9)'},'Location','southwest','Box','off'); catch, end

    out = 'henry_benchmark.png';
    try, exportgraphics(gcf,out,'Resolution',200);
    catch, print(gcf,out(1:end-4),'-dpng','-r200'); end
    fprintf('Written: %s\n', out);
end

% ----------------------------------------------------------------------
function C = reference_solver(g, P)
%REFERENCE_SOLVER  Default: coupled vd_residual + Newton (verified, Gate 1/2).
    N = g.N;
    U = vd_solve_forward(zeros(N,1), g, P, 1e-12);
    C = reshape(U(N+1:2*N), g.Nx, g.Ny).';     % Ny-by-Nx
end
