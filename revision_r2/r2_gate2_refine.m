function out = r2_gate2_refine()
%R2_GATE2_REFINE  Mesh-refinement check of the Henry mid-isochlor toe.
%
%   The manuscript states the toe is "stable under refinement, shifting by
%   less than the grid spacing", and the Fig. 4 caption carries a stale value
%   (1.25 m / 0.63 L) while Table 3 and Section 7 report 1.38 m (0.69 L).
%   This script computes the toe on a refinement ladder so the revised text
%   can state the refinement behaviour from actual runs.
%
%   Same physics/solver as demo/gate2_henry.m (functions copied verbatim from
%   gate1_henry_vd/gate2_henry lineage).
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end

    p = struct('phi',0.35,'Cs',35,'rho_s',1025,'rho_f',1000,'K',864, ...
               'Dm',1.62925,'Q',5.702,'L',2.0,'d',1.0);
    ladder = [21 11; 41 21; 61 31; 81 41];
    nL = size(ladder, 1);
    toe = nan(nL, 1); dx = nan(nL, 1); tsec = nan(nL, 1);

    % Indicative single-core run times on the archived runs, so a long wait on
    % the two finest rungs is recognisable as expected rather than as a hang.
    approx = [2 340 1040 2270];   % seconds

    fprintf('=== R2: Gate 2 toe under mesh refinement ===\n');
    fprintf(['This ladder takes about %d minutes in total; the 61x31 rung alone\n' ...
             'runs for roughly %d minutes and 81x41 for roughly %d. The archived\n' ...
             'results are in r2_results/r2_gate2_refine.csv, so the run can be\n' ...
             'interrupted without losing them.\n\n'], ...
            round(sum(approx)/60), round(approx(3)/60), round(approx(4)/60));

    for q = 1:nL
        nx = ladder(q, 1); nz = ladder(q, 2);
        m = local_mesh(nx, nz, p.L, p.d); nE = size(m.elem, 1);
        fprintf('  %2dx%2d ... solving (expect about %.0f s)\n', nx, nz, approx(q));
        tv = tic;
        u = forward_tight(m, p, zeros(nE, 1));
        tsec(q) = toc(tv);
        C = u(m.n+1:2*m.n);
        Cg = reshape(C, m.nx, m.nz)';
        xs = linspace(0, m.L, m.nx); base = Cg(1, :);
        cr = find(diff(sign(base - p.Cs/2)) ~= 0, 1);
        if ~isempty(cr), toe(q) = interp1(base(cr:cr+1), xs(cr:cr+1), p.Cs/2); end
        dx(q) = p.L / (nx - 1);
        fprintf('  %2dx%2d (dx=%.3f m): toe = %.3f m (%.3f L)   [%.1f s]\n', ...
                nx, nz, dx(q), toe(q), toe(q)/p.L, tsec(q));
        % write what is finished so far, so an interrupted run still leaves a file
        writematrix([ladder(1:q,:) dx(1:q) toe(1:q) toe(1:q)/p.L], ...
                    fullfile(outdir, 'r2_gate2_refine.csv'));
    end
    dtoe = abs(diff(toe));
    fprintf('\nsuccessive toe shifts: %s m;  grid spacings: %s m\n', ...
            mat2str(round(dtoe, 3)'), mat2str(round(dx(2:end), 3)'));
    fprintf('shift < spacing at each refinement: %s\n', tif(all(dtoe(:) < dx(2:end))));

    out = struct('ladder', ladder, 'dx', dx, 'toe', toe, 'toeL', toe / p.L, 'tsec', tsec);
    writematrix([ladder dx toe toe/p.L], fullfile(outdir, 'r2_gate2_refine.csv'));
    save(fullfile(outdir, 'r2_gate2_refine.mat'), '-struct', 'out');
    fprintf('saved: r2_gate2_refine.csv\n');
end

% ============ verbatim solver machinery (gate1/gate2 lineage) ============
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
function s=tif(c), if c, s='YES'; else, s='NO'; end, end
