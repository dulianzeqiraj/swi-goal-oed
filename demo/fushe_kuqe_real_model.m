function fushe_kuqe_real_model(xlsxfile)
%FUSHE_KUQE_REAL_MODEL  Confined areal flow + Ghyben-Herzberg sharp-interface
%   seawater-intrusion model of the REAL Fushe-Kuqe aquifer, built from the
%   actual field data and grounded in the published site characterization.
%
%   DATA (real):   aquifer boundary polygon and 43 wells (hydraulic
%                  conductivity K, piezometric heads) from Fushe_Kuqe_All_Data.xlsx.
%   CONCEPT (lit.): confined multilayer alluvial aquifer; discharge to the
%                  Adriatic on the W/SW coast; recharge from the Mat (N) and
%                  Droja (S) rivers; transmissivity ~500-8000 m2/day
%                  (Eftimi 2003; Cenameri & Beqiraj 2016, 2018;
%                  Kumanova et al. 2014, Hydrogeol. J. 22(4):883-892).
%   REPRESENTATIVE (labelled): aquifer thickness b, base depth below sea
%                  level, areal recharge R, and the sea boundary as the
%                  western envelope. No chloride data are used here, so the
%                  interface/toe is a MODEL ESTIMATE, not a calibrated fit.
%
%   Reference output (this script, default parameters): T 1.5e3-6.0e3 m2/day;
%   modelled head 0 (coast) to ~14 m (interior); Ghyben-Herzberg toe
%   penetration ~1.4 km mean (3.5 km max).
%
%   Usage:  fushe_kuqe_real_model('Fushe_Kuqe_All_Data.xlsx')
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin<1, xlsxfile='Fushe_Kuqe_All_Data.xlsx'; end

    % ---- representative parameters (EDIT to your site knowledge) -----------
    par.b_thick = 30;        % aquifer thickness [m]   (literature T/K -> 20-40 m)
    par.base    = 40;        % confined base depth below sea level [m]
    par.R       = 0.0005;    % areal recharge [m/day]  (~180 mm/yr)
    par.delta   = 0.025;     % (rho_s-rho_f)/rho_f  (Ghyben-Herzberg)
    par.dx      = 0.5;       % grid spacing [km]

    % ---- read REAL data -----------------------------------------------------
    Braw = readmatrix(xlsxfile,'Sheet','3_Boundary_Coords');
    B = Braw(:,2:3); B = B(all(isfinite(B),2),:);                 % boundary X,Y
    Wraw = readmatrix(xlsxfile,'Sheet','2_All_Wells');
    XY = Wraw(:,2:3); K = Wraw(:,4); H = Wraw(:,7);
    okK = all(isfinite([XY K]),2); WK = [XY(okK,:) K(okK)];        % wells with K
    okH = all(isfinite([XY H]),2); WH = [XY(okH,:) H(okH)];        % wells with head
    fprintf('Real data: %d boundary pts, %d K-wells, %d head-wells\n', size(B,1),size(WK,1),size(WH,1));

    x0=min(B(:,1)); y0=min(B(:,2));
    Bk=[(B(:,1)-x0) (B(:,2)-y0)]/1000;                            % km from SW corner
    WKk=[(WK(:,1)-x0) (WK(:,2)-y0)]/1000 ; WKk(:,3)=WK(:,3);
    WHk=[(WH(:,1)-x0) (WH(:,2)-y0)]/1000 ; WHk(:,3)=WH(:,3);

    % ---- grid + active-cell mask -------------------------------------------
    dx=par.dx; xs=0:dx:max(Bk(:,1))+dx; ys=0:dx:max(Bk(:,2))+dx;
    [GX,GY]=meshgrid(xs,ys); [ny,nx]=size(GX);
    inside = inpolygon(GX,GY,Bk(:,1),Bk(:,2));
    fprintf('grid %dx%d, active cells = %d  (domain %.1f x %.1f km)\n',nx,ny,nnz(inside),max(xs),max(ys));

    % ---- K field by inverse-distance weighting (real well values) ----------
    Kf=nan(ny,nx);
    for j=1:ny, for i=1:nx
        if inside(j,i)
            d=hypot(WKk(:,1)-xs(i),WKk(:,2)-ys(j))+1e-6; w=1./d.^2;
            Kf(j,i)=(w'*WKk(:,3))/sum(w);
        end
    end, end
    T=Kf*par.b_thick;
    fprintf('K [m/day] %.0f..%.0f -> T [m2/day] %.0f..%.0f (lit. 500-8000)\n', ...
            min(Kf(inside)),max(Kf(inside)),min(T(inside)),max(T(inside)));

    % ---- sea boundary = western envelope (per literature: Adriatic, W/SW) --
    coast=false(ny,nx);
    for j=1:ny
        ii=find(inside(j,:)); if ~isempty(ii), coast(j,ii(1))=true; end
    end

    % ---- confined steady flow:  div(T grad h) = -R ;  coast h=0 ------------
    idx=zeros(ny,nx); act=find(inside); idx(act)=1:numel(act); N=numel(act);
    [aj,ai]=ind2sub([ny,nx],act);
    I=[];Jc=[];V=[]; rhs=zeros(N,1); dxm=dx*1000;
    nb=[-1 0;1 0;0 -1;0 1];
    for k=1:N
        j=aj(k); i=ai(k);
        if coast(j,i), I(end+1)=k;Jc(end+1)=k;V(end+1)=1; rhs(k)=0; continue; end %#ok<AGROW>
        diag=0;
        for q=1:4
            jj=j+nb(q,1); ii=i+nb(q,2);
            if jj>=1&&jj<=ny&&ii>=1&&ii<=nx&&inside(jj,ii)
                Tf=0.5*(T(j,i)+T(jj,ii));
                I(end+1)=k;Jc(end+1)=idx(jj,ii);V(end+1)=Tf; %#ok<AGROW>
                diag=diag-Tf;
            end
        end
        I(end+1)=k;Jc(end+1)=k;V(end+1)=diag; rhs(k)=-par.R*dxm^2; %#ok<AGROW>
    end
    A=sparse(I,Jc,V,N,N); h=A\rhs;
    Hf=nan(ny,nx); Hf(act)=h;
    fprintf('head [m]: coast %.2f, interior max %.2f, mean %.2f\n', ...
            mean(Hf(coast)),max(Hf(inside)),mean(Hf(inside)));

    % ---- Ghyben-Herzberg sharp interface + toe -----------------------------
    ZETA=Hf/par.delta;                       % interface depth below sea level [m]
    toe=(ZETA<par.base)&inside;              % seawater present where interface above base
    fprintf('interface depth zeta [m]: %.0f..%.0f ; SWI zone = %.0f%% of active cells\n', ...
            min(ZETA(inside)),max(ZETA(inside)),100*nnz(toe)/nnz(inside));
    fprintf(['  (Ghyben-Herzberg estimate on this 0.5 km conceptual grid. The\n' ...
             '   intruded area reported in the article, 92.7 km^2 = 26.6%% of the\n' ...
             '   349.1 km^2 polygon, is computed by the 0.25 km design model in\n' ...
             '   src/fushe_kuqe_field_design.m; see demo/fushe_kuqe_design.m.)\n']);
    td=[];
    for j=1:ny
        ci=find(coast(j,:)); rw=find(toe(j,:));
        if ~isempty(ci)&&~isempty(rw), td(end+1)=(max(rw)-ci(1))*dx; end %#ok<AGROW>
    end
    if ~isempty(td), fprintf('toe penetration from coast: mean %.1f km, max %.1f km\n',mean(td),max(td)); end

    % ---- figures ------------------------------------------------------------
    figure('Color','w','Position',[60 60 1200 460]);
    % (a) real K field + wells
    subplot(1,3,1);
    Kp=Kf; Kp(~inside)=NaN; pcolor(xs,ys,Kp); shading flat; hold on; colormap(gca,parula);
    plot(Bk(:,1),Bk(:,2),'k-','LineWidth',0.7);
    scatter(WKk(:,1),WKk(:,2),28,WKk(:,3),'filled','MarkerEdgeColor','k');
    cb=colorbar; cb.Label.String='K [m/day]'; axis equal tight;
    xlabel('E [km]'); ylabel('N [km]'); title('(a) Real K field + wells');
    % (b) modelled head + coast
    subplot(1,3,2);
    Hp=Hf; pcolor(xs,ys,Hp); shading flat; hold on;
    plot(Bk(:,1),Bk(:,2),'k-','LineWidth',0.7);
    cx=GX(coast); cy=GY(coast); plot(cx,cy,'.','Color',[0 .3 .8],'MarkerSize',6);
    contour(xs,ys,Hf,0:2:14,'k','LineWidth',0.4);
    cb=colorbar; cb.Label.String='head [m]'; axis equal tight;
    xlabel('E [km]'); ylabel('N [km]'); title('(b) Confined head (coast=blue, h=0)');
    % (c) interface depth + SWI toe zone
    subplot(1,3,3);
    Zp=ZETA; Zp(~inside)=NaN; Zp(Zp>120)=120;
    pcolor(xs,ys,Zp); shading flat; hold on; colormap(gca,flipud(parula));
    plot(Bk(:,1),Bk(:,2),'k-','LineWidth',0.7);
    [tj,ti]=find(toe); plot(xs(ti),ys(tj),'.','Color',[.85 .1 .1],'MarkerSize',5);
    cb=colorbar; cb.Label.String='interface depth \zeta [m]'; axis equal tight;
    xlabel('E [km]'); ylabel('N [km]'); title(sprintf('(c) Ghyben-Herzberg interface; SWI toe (red, \\zeta<%dm)',par.base));
    try, exportgraphics(gcf,'fushe_kuqe_real_model.png','Resolution',200);
    catch, print(gcf,'fushe_kuqe_real_model','-dpng','-r200'); end
    fprintf('\nFigure written: fushe_kuqe_real_model.png\n');
    fprintf(['\nScope: geometry + K REAL; coast/recharge/thickness per published\n' ...
             'conceptual model (Eftimi 2003; Cenameri & Beqiraj 2016/2018); the\n' ...
             'interface/toe is a model estimate (no chloride data used here).\n']);
end
