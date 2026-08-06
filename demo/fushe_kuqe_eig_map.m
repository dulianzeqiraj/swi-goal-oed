function fushe_kuqe_eig_map(xlsxfile)
%FUSHE_KUQE_EIG_MAP  Publication-quality (Q1) value-of-information and
%   intervention-effectiveness maps for the Fushe-Kuqe aquifer.
%
%   Produces TWO standalone figures, both spatial outputs of the goal-oriented
%   methodology on the real Fushe-Kuqe domain:
%
%     (1) fushe_kuqe_eig_map.png  -- marginal goal-oriented EIG per location
%         (nats). Where a single monitoring well is most informative about
%         the seawater-intrusion toe.  Single-well evaluation of Lemma 1.
%
%     (2) fushe_kuqe_mar_map.png  -- MAR effectiveness map (km^2 per (m^3/day))
%         from one ADJOINT solve: d(intruded area) / d(local recharge).
%
%   The EIG/MAR fields AND the overlaid sites come from the SHARED model
%   FUSHE_KUQE_FIELD_DESIGN, so the markers here coincide exactly with
%   FUSHE_KUQE_DESIGN and the design section of GATE3_FIELD.
%
%   Scope: geometry + K REAL; coast/recharge/thickness per published model
%   (Eftimi 2003; Cenameri & Beqiraj 2016/2018); intrusion/toe is a model
%   estimate (no chloride data).
%
%   Usage:  addpath ../src; fushe_kuqe_eig_map('Fushe_Kuqe_All_Data.xlsx')
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin<1, xlsxfile='Fushe_Kuqe_All_Data.xlsx'; end
    if exist('fushe_kuqe_field_design','file')~=2, addpath(fullfile('..','src')); end

    % ---- ONE shared physical model, SAME default as fushe_kuqe_design and
    %      gate3_field -> the overlays here are byte-identical to those maps.
    R = fushe_kuqe_field_design(xlsxfile);
    fprintf('dx=%.2f km, active cells=%d\n',R.dx,R.Nc);
    fprintf('head max %.2f, baseline intruded area %.1f km^2\n',max(R.h0),R.baseArea);
    fprintf('per-cell EIG range: %.4f .. %.4f nats\n',min(R.EIG_c),max(R.EIG_c));
    fprintf('MAR effectiveness range: %.2e .. %.2e km^2/(m^3/day)\n',min(R.MAR_c),max(R.MAR_c));
    fprintf('monitoring (top-%d EIG): %s\n', R.P.Nmon, strjoin(cellstr(R.monID),', '));
    fprintf('MAR (top-%d): %s\n', R.P.Nmar, strjoin(cellstr(R.marID),', '));

    xs=R.xs; ys=R.ys; ai=R.ai; aj=R.aj; Bk=R.Bk;

    % ---- fine render grid (sharp polygon edge, no staircase) --------------
    dxr=0.05; xsr=0:dxr:max(xs); ysr=0:dxr:max(ys); [GXr,GYr]=meshgrid(xsr,ysr);
    inside_r=inpolygon(GXr,GYr,Bk(:,1),Bk(:,2));
    F_EIG = scatteredInterpolant(xs(ai)',ys(aj)',R.EIG_c,'linear','nearest');
    F_MAR = scatteredInterpolant(xs(ai)',ys(aj)',R.MAR_c,'linear','nearest');
    F_h   = scatteredInterpolant(xs(ai)',ys(aj)',R.h0,   'linear','nearest');
    EIG_r=F_EIG(GXr,GYr); EIG_r(~inside_r)=NaN;
    MAR_r=F_MAR(GXr,GYr); MAR_r(~inside_r)=NaN;
    h_r  =F_h(GXr,GYr);   h_r(~inside_r)=NaN;

    % ---- FIGURE 1: value-of-information (EIG) + monitoring sites -----------
    plot_panel(xsr,ysr,EIG_r,h_r,R.hcrit,Bk,xs,ys,ai,aj,R.monCell, ...
        'marginal goal-oriented EIG [nats]', ...
        '(b)  Value of information: where to MONITOR (toe localization)', ...
        [.85 .1 .1], 'o', 'parula', 'fushe_kuqe_eig_map.png');

    % ---- FIGURE 2: MAR effectiveness + recharge sites ---------------------
    MAR_r_sc = MAR_r * 1e4;  % km^2 per 10^4 m^3/day, for readability
    plot_panel(xsr,ysr,MAR_r_sc,h_r,R.hcrit,Bk,xs,ys,ai,aj,R.marCell, ...
        'MAR effectiveness [km^2 per 10^4 m^3/day]', ...
        '(a)  Intervention effectiveness: where to place MAR barriers', ...
        [.1 .8 .25], 'd', 'turbo', 'fushe_kuqe_mar_map.png');
    fprintf('\nWritten: fushe_kuqe_eig_map.png  and  fushe_kuqe_mar_map.png\n');
end

% ===================== plotting (publication style) =====================
function plot_panel(xsr,ysr,F,h_r,hcrit,Bk,xs,ys,ai,aj,topIdx,cbarLabel,ttl,markerCol,markerSym,cmapName,outpng)
    figW=720; figH=1280;
    figure('Color','w','Position',[60 30 figW figH], 'Visible', 'off');
    aspf=figW/figH; dataAsp=max(xsr)/max(ysr);
    mapH=0.86; mapW=mapH*dataAsp/aspf;
    axM=axes('Position',[0.13 0.07 mapW mapH]);
    pcolor(xsr,ysr,F); shading interp; hold on;
    switch cmapName
        case 'turbo',  try, colormap(axM,turbo); catch, colormap(axM,parula); end
        otherwise,     colormap(axM,parula);
    end
    vals = F(isfinite(F));
    if ~isempty(vals)
        sv = sort(vals(:)); lo = sv(1); hi = sv(max(1,round(0.98*numel(sv))));
        if hi<=lo, hi = lo + 1e-9; end
        try, caxis(axM,[lo hi]); catch, set(axM,'CLim',[lo hi]); end
    end
    [~,hC]=contour(xsr,ysr,h_r,[hcrit hcrit],'LineColor',[1 1 1]*0.05,'LineWidth',1.6,'LineStyle','--');
    plot(Bk(:,1),Bk(:,2),'k-','LineWidth',1.2);
    plot(xs(ai(topIdx)),ys(aj(topIdx)),markerSym,'MarkerSize',12, ...
         'MarkerFaceColor',markerCol,'MarkerEdgeColor','k','LineWidth',1.2);
    for q=1:numel(topIdx)
        text(xs(ai(topIdx(q)))+0.7,ys(aj(topIdx(q))),sprintf('%d',q), ...
             'FontWeight','bold','FontSize',11,'Color','k');
    end
    axis equal; axis([0 max(xsr) 0 max(ysr)]);
    set(axM,'FontSize',11,'LineWidth',1,'Layer','top','Box','on');
    xlabel('E [km]','FontSize',12); ylabel('N [km]','FontSize',12);
    title(ttl,'FontSize',13,'FontWeight','normal');
    cb=colorbar(axM); cb.Label.String=cbarLabel; cb.Label.FontSize=11;
    cb.Position=[0.13+mapW+0.015 0.18 0.025 0.55];
    axM.Position=[0.13 0.07 mapW mapH];
    legend(hC,{'interface at aquifer base (toe)'},'Location','northeast','Box','off','FontSize',10);
    save_figure(gcf, outpng, 600);
end
