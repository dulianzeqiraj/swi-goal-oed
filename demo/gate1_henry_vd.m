function gate1_henry_vd()
%GATE1_HENRY_VD  Gate 1 (discrete-adjoint gradient check) on the BENCHMARK-VERIFIED
%   variable-density Henry solver, with per-element log-K parameters.
%
%   Confirms that the discrete adjoint is correct on the production physics
%   (the solver that passed Gate 2 against the dissertation Fig. 4.2). This is
%   the prerequisite for the Section-7/8 goal-oriented design: once it prints
%   PASS, G_F and H_F from this solver are trustworthy.
%
%   Recipe verified in reference runs (forward |R| at u* ~ 1e-12):
%     - flow: Neumann freshwater flux on the inland (left) boundary,
%             Dirichlet sea head on the right; transport: C Dirichlet on both;
%     - NO clipping of C in the converged state (clipping breaks consistency);
%     - tight Picard so the coupled residual ~ 0 before forming the adjoint.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    p = struct('phi',0.35,'Cs',35,'rho_s',1025,'rho_f',1000,'K',864, ...
               'Dm',1.62925,'Q',5.702,'L',2.0,'d',1.0);
    m = local_mesh(11,6,p.L,p.d); n = m.n; nE = size(m.elem,1);
    theta0 = zeros(nE,1);

    u = forward_tight(m,p,theta0);
    fprintf('forward |R| at u*: %.2e (should be ~1e-12)\n', norm(residual(u,theta0,m,p)));

    % goal: salt mass in a landward window (toe-localization proxy)
    gx = m.coords(:,1); region = (gx>1.0)&(gx<1.6);
    dqdu = [zeros(n,1); double(region)];

    % discrete adjoint
    J = jac_u(@(uu) residual(uu,theta0,m,p), u);          % central FD, coupled
    dRdth = jac_theta(@(uu,th) residual(uu,th,m,p), u, theta0);
    mu = J'\dqdu; g_adj = -(mu'*dRdth);                   % adjoint gradient wrt log-K

    rng(1); eta = randn(nE,1); eta = eta/norm(eta); dir_adj = g_adj*eta;
    fprintf('\n=== Gate 1: adjoint vs finite-difference (log-K direction) ===\n');
    best = inf;
    for h = [1e-2 1e-3 1e-4]
        up = forward_tight(m,p,theta0+h*eta); um = forward_tight(m,p,theta0-h*eta);
        fd = (sum(up(n+find(region))) - sum(um(n+find(region))))/(2*h);
        re = abs(dir_adj-fd)/max(abs(dir_adj),eps); best = min(best,re);
        fprintf('  h=%.0e  relerr=%.2e\n', h, re);
    end
    fprintf(' min rel.err = %.2e -> %s\n', best, ternary(best<1e-5,'PASS','FAIL'));
end

% ===================== forward (tight, unclipped) =====================
function u = forward_tight(m,p,theta)
    n=m.n; hf=zeros(n,1); C=zeros(n,1); C(m.right)=p.Cs;
    [sh,qin]=bcv(m,p);
    for it=1:3000
        [Af,bz,~]=asm(hf,C,theta,m,p);
        ff=bz; ff(m.left)=ff(m.left)+qin;
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
    eps=(p.rho_s-p.rho_f)/p.rho_f; yR=m.coords(m.right,2);
    sh=m.d+eps*(m.d-yR); qin=p.Q/numel(m.left);
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
function s=ternary(c,a,b), if c, s=a; else, s=b; end, end
