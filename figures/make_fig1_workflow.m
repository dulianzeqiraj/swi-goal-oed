function make_fig1_workflow(outdir)
%MAKE_FIG1_WORKFLOW  Reproduce manuscript Figure 1 (conceptual workflow).
%
%   Draws the goal-oriented OED workflow as a box-and-arrow diagram and writes
%   Fig1_Workflow.png. Schematic (no data).
%
%   Author: D. Zeqiraj.  License: MIT.

    if nargin < 1 || isempty(outdir), outdir = pwd; end
    f = figure('Color','w','Position',[100 100 740 430]); ax=axes('Position',[0 0 1 1]); axis(ax,[0 12 0 8]); axis off; hold on
    blue=[0.86 0.90 0.95]; green=[0.86 0.93 0.87]; gold=[0.96 0.90 0.77]; rose=[0.96 0.85 0.85];
    box_(0.3,6.0,2.8,1.3,'Facies prior  \Gamma_F=D+\rho_F C',gold);
    box_(0.3,3.2,2.8,1.4,sprintf('Variable-density\nforward model  R(u;\\theta,d)=0'),blue);
    box_(0.3,0.6,2.8,1.3,sprintf('Discrete adjoint:\nassemble J (FD-coloring)'),blue);
    box_(4.0,4.2,3.1,1.2,sprintf('Observation adjoint\nJ^T\\Lambda=(\\partialO/\\partialu)^T  =>  G_F'),green);
    box_(4.0,1.2,3.1,1.2,sprintf('Goal adjoint\nJ^T\\mu=(\\partialq/\\partialu)^T  =>  H_F'),green);
    box_(7.9,2.85,3.8,1.5,sprintf('Information operator\nI_F=H_F\\Gamma_F G_F^T(G_F\\Gamma_F G_F^T+\\Gamma_n)^{-1}G_F\\Gamma_F H_F^T'),blue,7);
    box_(8.3,5.6,3.1,1.1,'EIG_Q=-\onehalf log(1-I_F/\sigma_0^2)',blue);
    box_(8.1,0.5,3.4,1.1,sprintf('Joint objective\nJ(d)=E_F[EIG_Q]-\\lambda C(d)'),rose);
    arr(1.7,6.0,1.7,4.6); arr(1.7,3.2,1.7,1.9);
    arr(3.1,3.95,4.0,4.65); arr(3.1,1.45,4.0,1.7); arr(3.1,1.1,4.0,4.35);
    arr(7.1,4.75,8.6,3.95); arr(7.1,1.75,8.6,3.25);
    arr(9.8,4.35,9.85,5.6); arr(9.7,2.85,9.75,1.6);
    text(6,7.6,'Goal-oriented Bayesian OED for variable-density SWI — workflow', ...
         'HorizontalAlignment','center','FontSize',11);
    try, exportgraphics(f,fullfile(outdir,'Fig1_Workflow.png'),'Resolution',600);
    catch, print(f,fullfile(outdir,'Fig1_Workflow.png'),'-dpng','-r600'); end
    close(f);
end

function box_(x,y,w,h,txt,fc,fs)
    if nargin<7, fs=8.5; end
    rectangle('Position',[x y w h],'Curvature',0.2,'FaceColor',fc,'EdgeColor',[0.3 0.3 0.3],'LineWidth',1.0);
    text(x+w/2,y+h/2,txt,'HorizontalAlignment','center','VerticalAlignment','middle','FontSize',fs,'Interpreter','tex');
end
function arr(x1,y1,x2,y2)
    annotation('arrow','HeadStyle','vback2','LineWidth',1.1,'Color',[0.3 0.3 0.3], ...
        'Position',[]); % placeholder; drawn below in data units
    quiver(x1,y1,x2-x1,y2-y1,0,'Color',[0.3 0.3 0.3],'LineWidth',1.1,'MaxHeadSize',0.4);
end
