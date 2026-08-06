function fushe_kuqe_design(xlsxfile)
%FUSHE_KUQE_DESIGN  Goal-oriented design on the REAL Fushe-Kuqe aquifer,
%   rendered as a SINGLE publication-quality map in the style of
%   FUSHE_KUQE_EIG_MAP: the value-of-information (EIG) field as the coloured
%   background, with the recommended design overlaid --
%       o  red  : the next MONITORING wells (max goal-oriented EIG),
%       d  green: the MANAGED-AQUIFER-RECHARGE (MAR) sites (max effectiveness),
%   each snapped to and labelled with the nearest real well ID, with the SWI
%   toe contour, the aquifer boundary and the (Dirichlet) coast for context.
%
%   The model, fields and selections come from the SHARED builder
%   FUSHE_KUQE_FIELD_DESIGN, so the markers here coincide exactly with
%   FUSHE_KUQE_EIG_MAP and the design section of GATE3_FIELD; sizes match
%   Gate 3: N=5 monitoring wells and M=3 MAR sites.
%
%   Scope: geometry + K REAL; coast/recharge/thickness per published model
%   (Eftimi 2003; Cenameri & Beqiraj 2016/2018); intrusion/toe is a model
%   estimate (no chloride data) -- a methodological recommendation.
%
%   Usage:  addpath ../src; fushe_kuqe_design('Fushe_Kuqe_All_Data.xlsx')
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin<1, xlsxfile='Fushe_Kuqe_All_Data.xlsx'; end
    if exist('fushe_kuqe_field_design','file')~=2, addpath(fullfile('..','src')); end

    % ---- ONE shared physical model (identical to eig_map / gate3_field) ----
    R = fushe_kuqe_field_design(xlsxfile);
    fprintf('dx=%.2f km, active cells=%d, baseline intruded area=%.1f km^2\n', R.dx, R.Nc, R.baseArea);
    fprintf('MONITORING (top-%d marginal EIG): %s\n', R.P.Nmon, strjoin(cellstr(R.monID),', '));
    fprintf('RECHARGE / MAR (top-%d effectiveness): %s\n', R.P.Nmar, strjoin(cellstr(R.marID),', '));

    xs=R.xs; ys=R.ys; ai=R.ai; aj=R.aj; Bk=R.Bk;
    monXY=R.monXY; marXY=R.marXY; monID=R.monID; marID=R.marID;

    % ---- fine render grid (sharp edge) + toe contour (eig_map style) -------
    dxr=0.05; xsr=0:dxr:max(xs); ysr=0:dxr:max(ys); [GXr,GYr]=meshgrid(xsr,ysr);
    inside_r=inpolygon(GXr,GYr,Bk(:,1),Bk(:,2));
    F_EIG=scatteredInterpolant(xs(ai)',ys(aj)',R.EIG_c,'linear','nearest'); EIG_r=F_EIG(GXr,GYr); EIG_r(~inside_r)=NaN;
    F_h  =scatteredInterpolant(xs(ai)',ys(aj)',R.h0,   'linear','nearest'); h_r  =F_h(GXr,GYr);   h_r(~inside_r)=NaN;

    % ============================ MAP (eig_map style) ======================
    figW=760; figH=1180; figure('Color','w','Position',[60 30 figW figH]);
    aspf=figW/figH; dataAsp=max(xsr)/max(ysr);
    mapH=0.82; mapW=mapH*dataAsp/aspf;
    axM=axes('Position',[0.14 0.14 mapW mapH]);
    pcolor(xsr,ysr,EIG_r); shading interp; hold on; colormap(axM,parula);
    vals=EIG_r(isfinite(EIG_r));
    if ~isempty(vals)
        sv=sort(vals(:)); lo=sv(1); hi=sv(max(1,round(0.98*numel(sv)))); if hi<=lo, hi=lo+1e-9; end
        try, caxis(axM,[lo hi]); catch, set(axM,'CLim',[lo hi]); end
    end
    [~,hToe]=contour(xsr,ysr,h_r,[R.hcrit R.hcrit],'LineColor',[1 1 1]*0.05,'LineWidth',1.6,'LineStyle','--');
    hB=plot(Bk(:,1),Bk(:,2),'k-','LineWidth',1.2);
    hMon=plot(monXY(:,1),monXY(:,2),'o','MarkerSize',12,'MarkerFaceColor',[.88 .12 .12], ...
              'MarkerEdgeColor','k','LineWidth',1.2);
    hMar=plot(marXY(:,1),marXY(:,2),'d','MarkerSize',13,'MarkerFaceColor',[.13 .72 .30], ...
              'MarkerEdgeColor','k','LineWidth',1.2);
    for q=1:size(monXY,1), text(monXY(q,1)+0.6,monXY(q,2),char(monID(q)),'FontWeight','bold','FontSize',10,'Color','k'); end
    for q=1:size(marXY,1), text(marXY(q,1)+0.6,marXY(q,2),char(marID(q)),'FontWeight','bold','FontSize',10,'Color','k'); end
    axis equal; axis([0 max(xsr) 0 max(ysr)]);
    set(axM,'FontSize',11,'LineWidth',1,'Layer','top','Box','on');
    xlabel('E [km]','FontSize',12); ylabel('N [km]','FontSize',12);
    title('Goal-oriented design: where to MONITOR and where to RECHARGE','FontSize',13,'FontWeight','normal');
    cb=colorbar(axM); cb.Label.String='marginal goal-oriented EIG [nats]'; cb.Label.FontSize=11;
    cb.Position=[0.14+mapW+0.015 0.26 0.025 0.50];
    axM.Position=[0.14 0.14 mapW mapH];

    % ---- centred legend below the map, listing BOTH well sets -------------
    monList=strjoin(cellstr(monID),', '); marList=strjoin(cellstr(marID),', ');
    lg=legend([hMon hMar hToe hB], ...
        {sprintf('Monitoring (max EIG): %s', monList), ...
         sprintf('MAR recharge (max effect.): %s', marList), ...
         'SWI toe (interface at base)','aquifer boundary'}, ...
        'Orientation','vertical','Box','off','FontSize',9);
    try, lg.NumColumns=1; catch, end
    set(lg,'Units','normalized');
    lp=get(lg,'Position'); set(lg,'Position',[0.5-lp(3)/2, 0.015, lp(3), lp(4)]);  % centred

    try, exportgraphics(gcf,'fushe_kuqe_design.png','Resolution',600);
    catch, print(gcf,'fushe_kuqe_design','-dpng','-r600'); end
    fprintf('\nFigure written: fushe_kuqe_design.png\n');
end
