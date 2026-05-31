function section8_design()
%SECTION8_DESIGN  Goal-oriented Bayesian design on the VALIDATED variable-
%   density Henry solver, with a facies-conditioned log-K prior whose
%   structure is taken from the real Fushe-Kuqe aquifer (coarse/medium/fine).
%
%   Honest scope (Route 2 / framework demonstration):
%     REAL      : variable-density solver (validated, Gate 2 = dissertation
%                 Fig. 4.2); discrete adjoint (Gate 1 PASS); facies prior
%                 structure from Fushe-Kuqe; goal-oriented method (Lemma 1).
%     SYNTHETIC : salinity scenario / wedge (no chloride data exist),
%                 representative cross-section geometry, candidate well grid.
%
%   Pipeline: validated forward -> discrete adjoint G_F (candidate monitoring
%   nodes) and H_F (toe-localization goal) -> facies prior Gamma_F(rho_F) ->
%   greedy goal-oriented EIG design (Lemma 1) vs random baseline -> Figure 5.
%
%   Requires src/ on the path (eig_operator.m). Run from demo/:
%       addpath ../src; section8_design
%
%   Reference (verified) numbers: toe ~70% of L; greedy 4-well EIG ~1.58 nats
%   vs random mean ~0.71 (rho_F = 0.5); EIG increases with rho_F.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if exist('eig_operator','file')~=2, addpath(fullfile('..','src')); end
    p = struct('phi',0.35,'Cs',35,'rho_s',1025,'rho_f',1000,'K',864, ...
               'Dm',1.62925,'Q',5.702,'L',2.0,'d',1.0);
    m = local_mesh(11,6,p.L,p.d); n = m.n; nE = size(m.elem,1); theta0 = zeros(nE,1);

    % ---- validated forward solve -------------------------------------------
    u = forward_tight(m,p,theta0); C = u(n+1:2*n);
    base = 1:m.nx; xb = m.coords(base,1); Cb = C(base);
    if max(Cb)>p.Cs/2, toe = interp1(Cb,xb,p.Cs/2); else, toe = xb(end); end
    fprintf('forward |R| = %.2e   toe = %.2f m (%.0f%% of L)\n', ...
            norm(residual(u,theta0,m,p)), toe, 100*toe/p.L);

    % ---- discrete adjoint: sensitivities G_F, H_F --------------------------
    J  = jac_u(@(uu) residual(uu,theta0,m,p), u);
    Dth = jac_theta(@(uu,th) residual(uu,th,m,p), u, theta0);
    JT = J';
    sens = @(sel) -(((JT)\sel)' * Dth);            % d(scalar obs)/d theta  (1-by-nE)

    gx = m.coords(:,1); gy = m.coords(:,2);
    region = (gx>1.0)&(gx<1.6);                     % landward window ~ toe
    H = sens([zeros(n,1); double(region)]);         % 1-by-nE goal sensitivity

    cand = find(gx>0.2 & gx<1.8 & gy>0.1 & gy<0.9); % candidate monitoring nodes
    G = zeros(numel(cand),nE);
    for r=1:numel(cand)
        sel = zeros(2*n,1); sel(n+cand(r)) = 1; G(r,:) = sens(sel);
    end
    fprintf('parameters = %d (3 facies),  candidate wells = %d\n', nE, numel(cand));

    % ---- facies-conditioned prior Gamma_F(rho_F)  (Lemma 2 structure) ------
    ecz = arrayfun(@(e) mean(m.coords(m.elem(e,:),2)), 1:nE)';     % element depth
    fac = 1 + (ecz<=0.66) + (ecz<=0.33);          % 1 coarse(top),2 medium,3 fine(base)
    sigtab = [0.30 0.45 0.60]; sig = sigtab(fac)';% per-facies log-K std (Fushe-Kuqe contrast)
    ec  = cell2mat(arrayfun(@(e) mean(m.coords(m.elem(e,:),:),1), (1:nE)','uni',0));
    Lc  = 0.5;
    GammaF = @(rhoF) build_prior(ec,fac,sig,Lc,rhoF,nE);

    sn = 0.05*p.Cs;                                % synthetic obs-noise std

    % ---- greedy goal-oriented design vs rho_F ------------------------------
    fprintf('\n=== greedy design (toe localization), 4 wells ===\n');
    rhos = [0.0 0.5 0.76 0.9]; Ssel = cell(1,numel(rhos));
    for t=1:numel(rhos)
        [S,e] = greedy(G,H,GammaF(rhos(t)),sn,cand,4);
        Ssel{t} = S;
        fprintf(' rho_F=%.2f  EIG(4)=%.4f nats\n', rhos(t), e);
    end

    % ---- EIG vs number of wells + random baseline (rho_F = 0.5) -----------
    Gm = GammaF(0.5); kmax = 6; eig_g = zeros(1,kmax);
    [Sg,~] = greedy(G,H,Gm,sn,cand,kmax);
    for k=1:kmax, eig_g(k) = eig_at(G,H,Gm,sn,Sg(1:k)); end
    rng(0); nrand = 300; eig_r = zeros(nrand,kmax);
    for k=1:kmax
        for b=1:nrand
            S = randperm(numel(cand),k); eig_r(b,k) = eig_at(G,H,Gm,sn,S);
        end
    end
    fprintf('\n greedy 4-well = %.4f  vs random mean %.4f (p90 %.4f)\n', ...
            eig_g(4), mean(eig_r(:,4)), prctile(eig_r(:,4),90));

    % ---- Figure 5 -----------------------------------------------------------
    figure('Color','w','Position',[100 100 1000 380]);
    % Panel A: salinity field + design (use rho_F = 0.5 selection)
    subplot(1,2,1);
    Cg = reshape(C, m.nx, m.nz)';   X = reshape(m.coords(:,1),m.nx,m.nz)'; Z = reshape(m.coords(:,2),m.nx,m.nz)';
    contourf(X,Z,Cg,12,'LineColor','none'); hold on; colormap(parula); cb=colorbar; cb.Label.String='C [kg/m^3]';
    plot(gx(cand),gy(cand),'o','MarkerSize',4,'MarkerEdgeColor',[.5 .5 .5],'MarkerFaceColor','none');
    S = Ssel{2}; plot(gx(cand(S)),gy(cand(S)),'o','MarkerSize',9,'MarkerFaceColor',[.85 .1 .1],'MarkerEdgeColor','k','LineWidth',1);
    plot(toe,0,'^','MarkerSize',11,'MarkerFaceColor','y','MarkerEdgeColor','k');
    xlabel('x [-]'); ylabel('z [-]'); title('(a) Salinity field and EIG-optimal monitoring (toe goal)');
    legend({'isochlors','candidates','selected (4)','toe'},'Location','southoutside','Orientation','horizontal','Box','off');
    axis([0 p.L 0 p.d]);
    % Panel B: EIG vs number of wells, greedy vs random band
    subplot(1,2,2);
    mu = mean(eig_r,1); lo = prctile(eig_r,10,1); hi = prctile(eig_r,90,1); kk=1:kmax;
    fill([kk fliplr(kk)],[lo fliplr(hi)],[.8 .85 .95],'EdgeColor','none'); hold on;
    plot(kk,mu,'--','Color',[.4 .4 .6],'LineWidth',1.2);
    plot(kk,eig_g,'-o','Color',[.85 .1 .1],'LineWidth',1.6,'MarkerFaceColor',[.85 .1 .1]);
    xlabel('number of monitoring wells'); ylabel('goal-oriented EIG [nats]');
    title('(b) Greedy design vs random (\rho_F = 0.5)');
    legend({'random 10-90%','random mean','greedy'},'Location','southeast','Box','off'); grid on;
    try, exportgraphics(gcf,'fig5_section8.png','Resolution',300);
    catch, print(gcf,'fig5_section8','-dpng','-r300'); end
    fprintf('\nFigure 5 written: fig5_section8.png\n');
end

% ====================== design helpers ======================
function e = eig_at(G,H,Gm,sn,S)
    if isempty(S), e=0; return; end
    e = eig_operator(G(S,:), H, Gm, (sn^2)*eye(numel(S)));
end
function [S,e] = greedy(G,H,Gm,sn,cand,k)
    S=[]; nc=size(G,1);
    for it=1:k
        best=-inf; bi=0;
        for i=1:nc
            if any(S==i), continue; end
            v = eig_at(G,H,Gm,sn,[S i]);
            if v>best, best=v; bi=i; end
        end
        S(end+1)=bi; %#ok<AGROW>
    end
    e = eig_at(G,H,Gm,sn,S);
end
function Gm = build_prior(ec,fac,sig,Lc,rhoF,nE)
    Gm=zeros(nE);
    for a=1:nE
        for b=1:nE
            d=norm(ec(a,:)-ec(b,:)); base=exp(-d/Lc);
            if fac(a)==fac(b), corr=base; else, corr=rhoF*base; end
            Gm(a,b)=sig(a)*sig(b)*corr;
        end
    end
    Gm=Gm+1e-9*eye(nE);
end

% ====================== validated physics (= gate1_henry_vd) ======================
function u = forward_tight(m,p,theta)
    n=m.n; hf=zeros(n,1); C=zeros(n,1); C(m.right)=p.Cs; [sh,qin]=bcv(m,p);
    for it=1:3000
        [Af,bz,~]=asm(hf,C,theta,m,p); ff=bz; ff(m.left)=ff(m.left)+qin;
        for j=1:numel(m.right), i=m.right(j); Af(i,:)=0; Af(i,i)=1; ff(i)=sh(j); end
        hf=Af\ff;
        [~,~,Ac]=asm(hf,C,theta,m,p); fc=zeros(n,1);
        for i=m.right(:)', Ac(i,:)=0; Ac(i,i)=1; fc(i)=p.Cs; end
        for i=m.left(:)',  Ac(i,:)=0; Ac(i,i)=1; fc(i)=0;    end
        Cn=Ac\fc;
        if norm(Cn-C)<1e-12, C=Cn; break; end
        C=0.5*Cn+0.5*C;
    end
    u=[hf;C];
end
function R = residual(u,theta,m,p)
    n=m.n; hf=u(1:n); C=u(n+1:2*n); [Af,bz,Ac]=asm(hf,C,theta,m,p); [sh,qin]=bcv(m,p);
    Rf=Af*hf-bz; Rf(m.left)=Rf(m.left)-qin;
    for j=1:numel(m.right), i=m.right(j); Rf(i)=hf(i)-sh(j); end
    Rt=Ac*C;
    for i=m.right(:)', Rt(i)=C(i)-p.Cs; end
    for i=m.left(:)',  Rt(i)=C(i); end
    R=[Rf;Rt];
end
function [sh,qin]=bcv(m,p)
    eps=(p.rho_s-p.rho_f)/p.rho_f; yR=m.coords(m.right,2); sh=m.d+eps*(m.d-yR); qin=p.Q/numel(m.left);
end
function [Af,bz,Ac]=asm(hf,C,theta,m,p)
    n=m.n; eps=(p.rho_s-p.rho_f)/p.rho_f; Af=sparse(n,n); bz=zeros(n,1); Ac=sparse(n,n);
    g=1/sqrt(3); GP=[-g -g; g -g; g g; -g g];
    for e=1:size(m.elem,1)
        nod=m.elem(e,:); xy=m.coords(nod,:); K=p.K*exp(theta(e)); buoy=eps*mean(C(nod))/p.Cs;
        [~,dN0]=shp([0 0],xy); q=-K*(dN0*hf(nod)+buoy*[0;1]); qn=norm(q)+1e-30;
        he=sqrt(abs((xy(2,1)-xy(1,1))*(xy(4,2)-xy(1,2)))); Dt=p.Dm*eye(2);
        Pe=qn*he/(2*p.phi*p.Dm+1e-30); tau=(he/(2*qn))*(coth_s(Pe)-1/Pe);
        Ae=zeros(4); be=zeros(4,1); Ce=zeros(4);
        for gi=1:4
            [N,dN,dJ]=shp(GP(gi,:),xy); w=dJ;
            Ae=Ae+K*(dN'*dN)*w; be=be-K*buoy*dN(2,:)'*w;
            Ce=Ce+(N*(q'*dN)+p.phi*(dN'*(Dt*dN))+tau*((q'*dN)'*(q'*dN)))*w;
        end
        Af(nod,nod)=Af(nod,nod)+Ae; bz(nod)=bz(nod)+be; Ac(nod,nod)=Ac(nod,nod)+Ce;
    end
end
function J = jac_u(res,u)
    N=numel(u); dl=1e-6*max(norm(u),1); J=zeros(N,N);
    for j=1:N, up=u; up(j)=up(j)+dl; um=u; um(j)=um(j)-dl; J(:,j)=(res(up)-res(um))/(2*dl); end
end
function D = jac_theta(res,u,th)
    nT=numel(th); R0=res(u,th); D=zeros(numel(R0),nT); dd=1e-6;
    for j=1:nT, tp=th; tp(j)=tp(j)+dd; tm=th; tm(j)=tm(j)-dd; D(:,j)=(res(u,tp)-res(u,tm))/(2*dd); end
end
function m=local_mesh(nx,nz,L,d)
    xs=linspace(0,L,nx); ys=linspace(0,d,nz); co=zeros(nx*nz,2);
    for k=1:nz, for i=1:nx, co((k-1)*nx+i,:)=[xs(i) ys(k)]; end, end
    el=zeros((nx-1)*(nz-1),4); e=0;
    for k=1:nz-1, for i=1:nx-1, n1=(k-1)*nx+i; e=e+1; el(e,:)=[n1 n1+1 n1+1+nx n1+nx]; end, end
    idx=reshape(1:nx*nz,nx,nz);
    m=struct('coords',co,'elem',el,'n',nx*nz,'nx',nx,'nz',nz,'L',L,'d',d,'left',idx(1,:)','right',idx(nx,:)');
end
function [N,dN,dJ]=shp(xi,xy)
    s=xi(1); t=xi(2);
    N=0.25*[(1-s)*(1-t);(1+s)*(1-t);(1+s)*(1+t);(1-s)*(1+t)];
    dNr=0.25*[-(1-t) (1-t) (1+t) -(1+t); -(1-s) -(1+s) (1+s) (1-s)];
    Jm=dNr*xy; dJ=det(Jm); dN=Jm\dNr;
end
function c=coth_s(x), c=cosh(x)/sinh(x); if ~isfinite(c), c=1.0; end, end
