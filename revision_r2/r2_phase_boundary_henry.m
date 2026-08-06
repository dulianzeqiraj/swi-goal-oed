function out = r2_phase_boundary_henry()
%R2_PHASE_BOUNDARY_HENRY  Poolability phase boundary recomputed from
%   PHYSICS-DERIVED sensitivities on a facies-striped variable-density Henry
%   domain (answers R2-5 and R2-12, addition (c)).
%
%   The synthetic study of Section 6 derives rho_c ~ 0.76 from an abstract
%   factor-model prior with identity candidate sensitivities. Here the same
%   diagnostic (src/phase_boundary.m, unchanged) is fed sensitivities computed
%   by the discrete adjoint of the nonlinear variable-density Henry solver
%   (same machinery as demo/gate1_henry_vd.m, functions copied verbatim):
%
%     - 11x6 mesh, 50 per-element log-K parameters in three horizontal bands
%       (coarse/medium/fine: theta offsets +0.4 / 0 / -0.7, i.e. a
%       heterogeneous linearization point);
%     - goal H: adjoint gradient of the landward salt-mass window (as Gate 1);
%     - candidates Gcand: adjoint gradients of 12 head observations on a
%       4x3 station grid;
%     - observation noise: scalar, sigma = 0.2 x median candidate row norm;
%     - facies prior: same construction as Sections 6/8 (within-facies
%       correlation r_within = 0.7), blocks = the three element bands.
%
%   Variants probe configuration-dependence ON the physics: noise x4,
%   budget B = 3, and the band order inverted. This shows the dead-zone
%   structure surviving on real variable-density physics while the VALUE of
%   rho_c moves with configuration -- the substance of R2-5.
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end

    p = struct('phi',0.35,'Cs',35,'rho_s',1025,'rho_f',1000,'K',864, ...
               'Dm',1.62925,'Q',5.702,'L',2.0,'d',1.0);
    m = local_mesh(11,6,p.L,p.d); n = m.n; nE = size(m.elem,1);
    erow = ceil((1:nE)' / (m.nx - 1));                 % 1 (bottom) .. 5 (top)
    band = 1 * (erow <= 2) + 2 * (erow == 3) + 3 * (erow >= 4);   % contiguous
    counts = [sum(band == 1) sum(band == 2) sum(band == 3)];
    fprintf('=== R2: poolability boundary on facies-striped Henry physics ===\n');
    fprintf('mesh 11x6, nE = %d, bands [coarse med fine] = [%d %d %d]\n', nE, counts);

    offs = [+0.4 0 -0.7];
    theta0 = offs(band)';

    % ---- adjoint sensitivities at the banded base point --------------------
    tS = tic;
    u = forward_tight(m, p, theta0);
    fprintf('forward |R| at u* = %.2e\n', norm(residual(u, theta0, m, p)));
    J = jac_u(@(uu) residual(uu, theta0, m, p), u);
    dRdth = jac_theta(@(uu, th) residual(uu, th, m, p), u, theta0);

    gx = m.coords(:, 1); region = (gx > 1.0) & (gx < 1.6);
    dqdu = [zeros(n, 1); double(region)];
    H = -((J' \ dqdu)' * dRdth);                       % 1 x nE goal sensitivity

    [sx, sy] = meshgrid([0.3 0.7 1.1 1.5], [0.25 0.5 0.75]);
    st = [sx(:) sy(:)]; Mc = size(st, 1);
    Gcand = zeros(Mc, nE); nodeId = zeros(Mc, 1);
    for i = 1:Mc
        [~, nd] = min(hypot(m.coords(:, 1) - st(i, 1), m.coords(:, 2) - st(i, 2)));
        nodeId(i) = nd;
        e_i = zeros(2 * n, 1); e_i(nd) = 1;            % head observation at node nd
        Gcand(i, :) = -((J' \ e_i)' * dRdth);
    end
    assert(numel(unique(nodeId)) == Mc, 'duplicate observation nodes');
    fprintf('sensitivities assembled in %.1f s (12 head candidates, 1 goal)\n', toc(tS));

    % ---- facies prior over the bands, diagnostic variants ------------------
    r_within = 0.7;
    sn = 0.2 * median(vecnorm(Gcand, 2, 2));
    rho_grid = linspace(0, 1, 401);

    V = { 'base (B=2)',            band,  sn^2,       2;
          'noise x4',              band,  (4*sn)^2,   2;
          'budget B=3',            band,  sn^2,       3 };
    % band order inverted: fine at the bottom, coarse at the top
    band_inv = 4 - band;   % 1<->3, 2 stays -- NOT contiguous by construction
    [bsrt, isrt] = sort(band_inv);                     % sort params so blocks are contiguous
    V(end+1, :) = {'bands inverted', bsrt, sn^2, 2};

    nV = size(V, 1);
    name = strings(nV, 1); rc = zeros(nV, 1); lossPct = zeros(nV, 1);
    curves = cell(nV, 1);
    for v = 1:nV
        bd = V{v, 2}; nv = V{v, 3}; Bb = V{v, 4};
        if v == 4, Gc = Gcand(:, isrt); Hh = H(isrt); else, Gc = Gcand; Hh = H; end
        cts = [sum(bd == 1) sum(bd == 2) sum(bd == 3)];
        blocks = cell(1, 3);
        for k = 1:3, nk = cts(k); blocks{k} = (1 - r_within) * eye(nk) + r_within * ones(nk); end
        cross = zeros(nE);
        for a = 1:nE, for b = 1:nE, if bd(a) ~= bd(b), cross(a, b) = r_within; end, end, end
        o = phase_boundary(Gc, Hh, blocks, cross, nv, Bb, rho_grid);
        e0 = eig_operator(Gc(o.d0, :), Hh, facies_prior(0, blocks, cross), nv * eye(numel(o.d0)));
        name(v) = V{v, 1}; rc(v) = o.rho_c; lossPct(v) = 100 * max(o.L) / max(e0, eps);
        curves{v} = o;
        fprintf('  %-16s rho_c = %.3f   max loss = %5.1f%% of pooled EIG\n', name(v), rc(v), lossPct(v));
    end
    fprintf('synthetic Section-6 value for comparison: rho_c ~ 0.760-0.762\n');

    % ---- figure ------------------------------------------------------------
    f = figure('Color', 'w', 'Position', [80 80 640 420]); hold on
    cols = [0.13 0.31 0.62; 0.85 0.45 0.05; 0.15 0.60 0.25; 0.55 0.25 0.55];
    stys = {'-', '--', ':', '-.'}; mks = {'o', 's', '^', 'd'};
    for v = 1:nV
        % base and bands-inverted coincide by construction; distinct styles
        % and staggered markers keep every legend entry visible
        plot(curves{v}.rho, curves{v}.Lambda, stys{v}, 'LineWidth', 1.8, 'Color', cols(v, :), ...
             'Marker', mks{v}, 'MarkerSize', 5, ...
             'MarkerIndices', (6 + 10*v):40:numel(curves{v}.rho), ...
             'DisplayName', sprintf('%s  (\\rho_c = %.3f)', name(v), rc(v)));
    end
    plot([0.762 0.762], [0 1.08], '--', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.1, ...
         'DisplayName', 'synthetic \rho_c = 0.762');
    axis([0 1 0 1.08]); grid on; box on; set(gca, 'FontSize', 11, 'Layer', 'top');
    xlabel('cross-facies correlation  \rho_F', 'FontSize', 12);
    ylabel('order parameter  \Lambda = L/L(0)', 'FontSize', 12);
    title('Poolability boundary from variable-density Henry adjoint sensitivities', ...
          'FontWeight', 'normal', 'FontSize', 11);
    legend('Location', 'southwest', 'Box', 'off', 'FontSize', 9);
    try, exportgraphics(f, fullfile(outdir, 'r2_FigS_PhaseBoundary_Henry.png'), 'Resolution', 600);
    catch, print(f, fullfile(outdir, 'r2_FigS_PhaseBoundary_Henry'), '-dpng', '-r600'); end

    T = table(name, rc, lossPct, 'VariableNames', {'variant', 'rho_c', 'max_loss_pct'});
    writetable(T, fullfile(outdir, 'r2_phase_boundary_henry.csv'));
    out = struct('table', T, 'counts', counts, 'sn', sn, 'offs', offs);
    save(fullfile(outdir, 'r2_phase_boundary_henry.mat'), '-struct', 'out');
    fprintf('saved: r2_phase_boundary_henry.csv, r2_FigS_PhaseBoundary_Henry.png\n');
end

% ============ verbatim solver/adjoint machinery of gate1_henry_vd ============
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
