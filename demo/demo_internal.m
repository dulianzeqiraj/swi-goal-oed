function demo_internal()
%DEMO_  Full variable-density goal-oriented OED pipeline on the
%   BENCHMARK-VERIFIED Henry solver (the one that passes Gate 1 at <1e-5 and Gate 2
%   against the dissertation Fig. 4). Per-element log-conductivity theta.
%
%     forward (tight Picard) -> assemble_jacobian_fd -> adjoint_solve
%                            -> eig_operator -> greedy_design
%     plus Gate 1 (gate1_gradcheck) on the discrete adjoint.
%
%   The consistency that makes Gate 1 pass (vs the old prototype): the
%   residual uses proper Dirichlet identity rows and a Neumann freshwater
%   flux, with NO clipping of C in the converged state, and a tight Picard
%   (coupled |R| ~ 1e-12) before the adjoint is formed.
%
%   Run:  >> demo_internal
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    here = fileparts(mfilename('fullpath'));
    addpath(fullfile(here, '..', 'src'));

    % ---- benchmark-verified physics + mesh (per-element log-K) ---------------------
    p = struct('phi',0.35,'Cs',35,'rho_s',1025,'rho_f',1000,'K',864, ...
               'Dm',1.62925,'Q',5.702,'L',2.0,'d',1.0);
    m = local_mesh(11,6,p.L,p.d); n = m.n; nE = size(m.elem,1);
    theta0 = zeros(nE,1);

    solve_fwd = @(th) forward_tight(m,p,th);
    resfun_th = @(uu,th) residual(uu,th,m,p);

    % scalar goal: salt mass in a landward (toe-localization) window
    gx = m.coords(:,1); region = (gx>1.0)&(gx<1.6);
    goalfun = @(u) sum(u(n + find(region)));
    dqdu    = @(u) [zeros(1,n), double(region(:))'];     % 1-by-2n

    % ---- Gate 1: discrete-adjoint gradient check --------------------------
    fprintf('=== Gate 1: discrete-adjoint gradient check (benchmark-verified solver) ===\n');
    rng(1); eta = randn(nE,1); eta = eta/norm(eta);
    [passed, ~] = gate1_gradcheck(solve_fwd, resfun_th, goalfun, dqdu, theta0, eta, [1e-2 1e-3 1e-4]);
    if ~passed, warning('Gate 1 did not pass at 1e-5 — check Picard tolerance / mesh.'); end

    % ---- one design evaluation: G_F, H_F via the adjoint ------------------
    fprintf('\n=== Sensitivities via the coupled adjoint ===\n');
    u  = solve_fwd(theta0);
    J  = assemble_jacobian_fd(@(uu) resfun_th(uu, theta0), u);
    dRdtheta = jac_theta(resfun_th, u, theta0);
    cand = (1:2:n)';                                     % candidate monitoring nodes
    dOdu = sparse(numel(cand), 2*n);
    for i = 1:numel(cand), dOdu(i, n + cand(i)) = 1; end % observe concentration
    [G, H] = adjoint_solve(J, dRdtheta, full(dOdu), dqdu(u));

    % ---- goal-oriented EIG + greedy design (per-element prior) ------------
    GamF  = facies_prior(0.6, {0.3*eye(nE)+0.7*ones(nE)}, []);
    noise = 0.05*ones(numel(cand),1);
    sel   = greedy_design(G, H, GamF, noise, 2);
    fprintf('selected candidate monitoring nodes: %s\n', mat2str(cand(sel)'));
    fprintf('goal-oriented EIG of selected design = %.4f nats\n', ...
            eig_operator(G(sel,:), H, GamF, diag(noise(sel))));
end

% ===================== benchmark-verified solver (per-element log-K) ============
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
function dRdtheta = jac_theta(resfun_th, u, theta)
    nT=numel(theta); R0=resfun_th(u,theta); R0=R0(:);
    dRdtheta=zeros(numel(R0),nT); dd=1e-6;
    for j=1:nT, tp=theta; tp(j)=tp(j)+dd; tm=theta; tm(j)=tm(j)-dd;
        dRdtheta(:,j)=(resfun_th(u,tp)-resfun_th(u,tm))/(2*dd); end
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
