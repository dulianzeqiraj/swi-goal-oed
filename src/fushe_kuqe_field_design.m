function R = fushe_kuqe_field_design(xlsxfile, P)
%FUSHE_KUQE_FIELD_DESIGN  Shared full-grid model + goal-oriented selection for
%   the Fushe-Kuqe aquifer.
%
%   R = FUSHE_KUQE_FIELD_DESIGN(xlsxfile, P)
%
%   ONE physical model, called by FUSHE_KUQE_DESIGN, FUSHE_KUQE_EIG_MAP and the
%   design section of GATE3_FIELD, so all three report the SAME monitoring and
%   MAR locations -- the consistency is structural (same grid, K field, prior,
%   goal, EIG and MAR fields, and the same top-k selection), not hard-coded.
%
%   Builds: confined areal flow on the real polygon (dx grid, IDW log-K),
%   pilot-zone facies prior Gamma_F, baseline head h0 and intruded area, zonal
%   sensitivities, the marginal goal-oriented EIG field EIG_c and the MAR
%   effectiveness field MAR_c (one adjoint solve). Selects the top-Nmon EIG
%   cells (monitoring) and top-Nmar MAR cells (recharge), spaced by P.space km,
%   and snaps each to the nearest real well ID. Returns everything in R.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin<1 || isempty(xlsxfile), xlsxfile='Fushe_Kuqe_All_Data.xlsx'; end
    if nargin<2 || isempty(P)
        P=struct('b',30,'base',40,'R',5e-4,'delta',0.025,'dx',0.25, ...
                 'sn',0.2,'rhoF',0.6,'Nmon',5,'Nmar',3,'space',6.0);
    end
    P.hcrit=P.base*P.delta;
    if exist('eig_operator','file')~=2, addpath(fileparts(mfilename('fullpath'))); end

    % ---- real data (geometry + K) with well IDs ----------------------------
    Braw=readmatrix(xlsxfile,'Sheet','3_Boundary_Coords'); B=Braw(:,2:3); B=B(all(isfinite(B),2),:);
    [WXY,WKv,wellID]=read_wells(xlsxfile);
    ok=all(isfinite([WXY WKv]),2); WK=[WXY(ok,:) WKv(ok)]; wellID=wellID(ok);
    x0=min(B(:,1)); y0=min(B(:,2));
    Bk=[(B(:,1)-x0) (B(:,2)-y0)]/1000;
    Wk=[(WK(:,1)-x0) (WK(:,2)-y0)]/1000; Wk(:,3)=WK(:,3);

    % ---- grid + IDW K field ------------------------------------------------
    dx=P.dx; xs=0:dx:max(Bk(:,1))+dx; ys=0:dx:max(Bk(:,2))+dx; [GX,GY]=meshgrid(xs,ys); [ny,nx]=size(GX);
    inside=inpolygon(GX,GY,Bk(:,1),Bk(:,2));
    K0=nan(ny,nx);
    for j=1:ny, for i=1:nx
        if inside(j,i), d=hypot(Wk(:,1)-xs(i),Wk(:,2)-ys(j))+1e-6; w=1./d.^2; K0(j,i)=(w'*Wk(:,3))/sum(w); end
    end, end
    act=find(inside); [aj,ai]=ind2sub([ny,nx],act); Nc=numel(act); idx=zeros(ny,nx); idx(act)=1:Nc;
    dxm=dx*1000; area=dxm^2;
    coast=false(ny,nx);
    for j=1:ny, ii=find(inside(j,:)); if ~isempty(ii), coast(j,ii(1))=true; end, end
    K0c=arrayfun(@(k) K0(aj(k),ai(k)), (1:Nc)');

    % ---- baseline head + fixed-K operator (factorised once) ----------------
    [A0,rhs0]=assemble(zeros(0,1),[],K0c,P,act,aj,ai,idx,inside,coast,ny,nx,Nc,dxm,true);
    h0=A0\rhs0; baseArea=goalA(h0,P,area);

    % ---- pilot zones + zonal sensitivities S, goal sensitivity Hg ----------
    [pgx,pgy]=meshgrid(linspace(1,max(xs)-1,5),linspace(2,max(ys)-2,8));
    pil=[pgx(:) pgy(:)]; pin=inpolygon(pil(:,1),pil(:,2),Bk(:,1),Bk(:,2)); pil=pil(pin,:); Nz=size(pil,1);
    zone=zeros(Nc,1);
    for k=1:Nc, [~,zone(k)]=min(hypot(pil(:,1)-xs(ai(k)),pil(:,2)-ys(aj(k)))); end
    zK=arrayfun(@(z) mean(K0c(zone==z)), (1:Nz)');
    if ~isfield(P,'faciesRule'), P.faciesRule='legacy'; end
    switch lower(P.faciesRule)
        case 'harmonized'   % same rule as the gate3_field wells: coarse K>=150, fine K<75
            zfac=1+(zK<150)+(zK<75);
        otherwise           % 'legacy': the rule of the published R1 runs
            zfac=1+(zK<=150)+(zK<=80);
    end
    solve=@(theta) zsolve(theta,zone,K0c,P,act,aj,ai,idx,inside,coast,ny,nx,Nc,dxm);
    S=zeros(Nc,Nz); Hg=zeros(1,Nz); dd=1e-3;
    for z=1:Nz
        tp=zeros(Nz,1);tp(z)=dd; tm=zeros(Nz,1);tm(z)=-dd; hp=solve(tp); hm=solve(tm);
        S(:,z)=(hp-hm)/(2*dd); Hg(z)=(goalA(hp,P,area)-goalA(hm,P,area))/(2*dd);
    end
    GamF=buildGamma(pil,zfac,P.rhoF);

    % ---- marginal goal-oriented EIG field ----------------------------------
    HGH=Hg*GamF*Hg'; EIG_c=zeros(Nc,1);
    for k=1:Nc
        g=S(k,:); v=g*GamF*g'+P.sn^2; ifn=(Hg*GamF*g')*(g*GamF*Hg')/v;
        EIG_c(k)=-0.5*log(max(1-ifn/HGH,1e-12));
    end

    % ---- MAR effectiveness field (one adjoint solve) -----------------------
    s=0.15; sigQ=1./(1+exp(-(P.hcrit-h0)/s));
    w_h = area * (-(sigQ.*(1-sigQ))/s) / 1e6;
    lam = A0' \ w_h; MAR_c = lam; MAR_c(coast(act)) = 0;

    % ---- selections (top-k, spaced) + snap to nearest wells ----------------
    monCell=pick_topk(EIG_c,aj,ys,P.Nmon,P.space);
    marCell=pick_topk(MAR_c,aj,ys,P.Nmar,P.space);
    [monID,monXY]=snap_to_wells(monCell,ai,aj,xs,ys,Wk,wellID);
    [marID,marXY]=snap_to_wells(marCell,ai,aj,xs,ys,Wk,wellID);

    % ---- pack -------------------------------------------------------------
    R.P=P; R.dx=dx; R.xs=xs; R.ys=ys; R.GX=GX; R.GY=GY; R.ny=ny; R.nx=nx;
    R.inside=inside; R.act=act; R.ai=ai; R.aj=aj; R.Nc=Nc; R.idx=idx; R.coast=coast;
    R.Bk=Bk; R.Wk=Wk; R.wellID=wellID; R.K0=K0; R.K0c=K0c; R.dxm=dxm; R.area=area;
    R.h0=h0; R.baseArea=baseArea; R.hcrit=P.hcrit; R.EIG_c=EIG_c; R.MAR_c=MAR_c;
    R.monCell=monCell; R.marCell=marCell; R.monXY=monXY; R.marXY=marXY;
    R.monID=monID; R.marID=marID;
    R.zK=zK; R.zfac=zfac; R.pil=pil; R.zone=zone;
end

% ============================= helpers ==================================
function [XY,K,ID]=read_wells(xlsxfile)
    try
        T=readtable(xlsxfile,'Sheet','2_All_Wells');
        XY=[T{:,2} T{:,3}]; K=T{:,4}; ID=string(T{:,1});
    catch
        M=readmatrix(xlsxfile,'Sheet','2_All_Wells'); XY=M(:,2:3); K=M(:,4);
        ID=string(compose('W%d',(1:size(M,1))'));
    end
end
function A=goalA(h,P,area), s=0.15; A=sum(area*(1./(1+exp(-(P.hcrit-h)/s))))/1e6; end
function [Aop,rhs]=assemble(theta,zone,K0c,P,act,aj,ai,idx,inside,coast,ny,nx,Nc,dxm,fixedK)
    if fixedK, Tc=K0c*P.b; else, Tc=(K0c.*exp(theta(zone)))*P.b; end
    Tg=nan(ny,nx); Tg(act)=Tc;
    I=zeros(5*Nc,1);J=I;V=I; rhs=zeros(Nc,1); p=0; nb=[-1 0;1 0;0 -1;0 1];
    for k=1:Nc
        j=aj(k); i=ai(k);
        if coast(j,i), p=p+1; I(p)=k;J(p)=k;V(p)=1; rhs(k)=0; continue; end
        dg=0;
        for q=1:4
            jj=j+nb(q,1); ii=i+nb(q,2);
            if jj>=1&&jj<=ny&&ii>=1&&ii<=nx&&inside(jj,ii)
                Tf=0.5*(Tg(j,i)+Tg(jj,ii)); p=p+1; I(p)=k;J(p)=idx(jj,ii);V(p)=Tf; dg=dg-Tf;
            end
        end
        p=p+1; I(p)=k;J(p)=k;V(p)=dg; rhs(k)=-P.R*dxm^2;
    end
    Aop=sparse(I(1:p),J(1:p),V(1:p),Nc,Nc);
end
function h=zsolve(theta,zone,K0c,P,act,aj,ai,idx,inside,coast,ny,nx,Nc,dxm)
    [Aop,rhs]=assemble(theta,zone,K0c,P,act,aj,ai,idx,inside,coast,ny,nx,Nc,dxm,false); h=Aop\rhs;
end
function Gm=buildGamma(pil,zfac,rhoF)
    Nz=size(pil,1); Lc=8.0; Gm=zeros(Nz);
    for a=1:Nz, for b=1:Nz
        dd_=hypot(pil(a,1)-pil(b,1),pil(a,2)-pil(b,2)); bs=exp(-dd_/Lc);
        if zfac(a)==zfac(b), Gm(a,b)=bs; else, Gm(a,b)=rhoF*bs; end
    end, end
    st=[0.30 0.45 0.60]; sig=st(zfac)'; Gm=(sig*sig').*Gm + 1e-9*eye(Nz);
end
function sel=pick_topk(vals,aj,ys,k,spaceN)
    [~,ord]=sort(vals,'descend','MissingPlacement','last');
    sel=[]; usedN=[];
    for q=1:numel(ord)
        kk=ord(q); if ~isfinite(vals(kk)), continue; end
        N=ys(aj(kk)); if ~isempty(usedN) && any(abs(N-usedN)<spaceN), continue; end
        sel(end+1)=kk; usedN(end+1)=N; %#ok<AGROW>
        if numel(sel)>=k, break; end
    end
    sel=sel(:);
end
function [ID,XY]=snap_to_wells(cellIdx, ai, aj, xs, ys, Wk, wellID)
    n=numel(cellIdx); XY=zeros(n,2); ID=strings(n,1);
    for q=1:n
        ex=xs(ai(cellIdx(q))); ey=ys(aj(cellIdx(q)));
        [~,w]=min(hypot(Wk(:,1)-ex,Wk(:,2)-ey));
        XY(q,:)=[ex ey]; ID(q)=wellID(w);
    end
end
