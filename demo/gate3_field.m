function gate3_field(xlsxfile)
%GATE3_FIELD  Gate 3: poolability diagnostic + design on the Fushe-Kuqe prior.
%
%   Recomputes the poolability phase boundary (rho_c) on the field facies
%   prior built from the 32 inside-aquifer wells (facies from K thresholds,
%   a declared PROXY), estimates the field cross-facies correlation rho_F
%   from the spatial log-K structure, places the site relative to rho_c, and
%   reports the goal-information gain of facies-aware over facies-blind
%   sampling, and the field design (N monitoring + M MAR) from the SHARED
%   full-grid model FUSHE_KUQE_FIELD_DESIGN -- the SAME wells as
%   FUSHE_KUQE_DESIGN and FUSHE_KUQE_EIG_MAP.
%
%   HONEST SCOPE: facies are a K-threshold proxy (K is quantised in the data);
%   rho_F is a sparse-data (32-well) spatial estimate. The poolability gain
%   is a linear-Gaussian diagnostic; the N/M well LOCATIONS come from the
%   full-grid spatial model (shared with the maps), so all three agree.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin<1, xlsxfile='Fushe_Kuqe_All_Data.xlsx'; end
    addpath(fullfile(fileparts(mfilename('fullpath')),'..','src'));

    % --- real inside-aquifer wells: [X Y K] (Gauss-Kruger, m; K m/day) -----
    D = [ 4389697.8 4612715.3 200;
4386550.2 4613827.2 200;
4385772.5 4611141.8 200;
4388660.5 4610529.7 200;
4384800.0 4612850.0 200;
4390000.0 4616000.0 200;
4388850.0 4612900.0 200;
4387250.0 4612950.0 200;
4389600.0 4610750.0 200;
4387450.0 4614200.0 200;
4386100.0 4613250.0 200;
4398876.2 4578903.7 130;
4394166.0 4583209.0 130;
4398550.0 4577900.0 130;
4396050.0 4581000.0 130;
4391881.3 4586409.8 100;
4390133.6 4594648.2 100;
4394311.0 4585283.0 100;
4391812.0 4585733.0 100;
4391912.0 4587382.0 100;
4391407.0 4589527.0 100;
4391862.3 4589715.2 100;
4388250.0 4600950.0 100;
4390300.0 4593100.0 100;
4387800.0 4598550.0 100;
4387178.1 4611065.9 50;
4386590.2 4605699.1 50;
4386700.0 4606500.0 50;
4394400.0 4587250.0 50;
4384400.0 4606100.0 50;
4387100.0 4606700.0 50;
4388300.0 4607000.0 50 ];
    X = D(:,1); Y = D(:,2); K = D(:,3); n = numel(K);
    fac = 1*(K>=150) + 2*(K>=75 & K<150) + 3*(K<75);   % 1 coarse,2 medium,3 fine
    cnt = [sum(fac==1) sum(fac==2) sum(fac==3)];
    fprintf('=== Gate 3: Fushe-Kuqe field prior ===\n');
    fprintf('wells=%d  facies coarse/medium/fine = [%d %d %d] (K-threshold proxy)\n', n, cnt);

    % --- field rho_F: spatial IDW-neighbour log-K correlation (proxy) ------
    lK = log(K); pred = zeros(n,1);
    for i=1:n
        d = hypot(X-X(i),Y-Y(i)); d(i)=inf; w=1./(d.^2+1e-9); w=w/sum(w);
        pred(i) = sum(w.*lK);
    end
    cc = corrcoef(lK,pred); rhoF = cc(1,2);

    % --- recompute the phase boundary on the FIELD prior -------------------
    r_within = 0.7; B = 2;
    [ord] = sort(fac,'ascend'); [~,ix]=sort(fac,'ascend'); facO=fac(ix);
    blocks = cell(1,3);
    for k=1:3, nk=cnt(k); blocks{k}=(1-r_within)*eye(nk)+r_within*ones(nk); end
    N3=n; cross=zeros(N3);
    for a=1:N3, for b=1:N3, if facO(a)~=facO(b), cross(a,b)=r_within; end, end, end
    Gcand=eye(N3); nf=[0.05 0.30 0.80]; noise=nf(facO)';
    H=zeros(1,N3); H(find(facO==3,1,'first'))=1.0;

    rho_grid=linspace(0,1,401);
    out = phase_boundary(Gcand,H,blocks,cross,noise,B,rho_grid);
    e_pooled0 = eig_operator(Gcand(out.d0,:),H,facies_prior(0,blocks,cross),diag(noise(out.d0)));
    pct = 100*max(out.L)/max(e_pooled0,eps);

    fprintf('rho_c (field, recomputed)   = %.3f   (synthetic ~0.760)\n', out.rho_c);
    fprintf('max pooling loss            = %.1f%% of pooled EIG\n', pct);
    fprintf('field rho_F (spatial proxy) = %.3f\n', rhoF);
    if rhoF>=out.rho_c
        fprintf('=> POOLABLE: facies-blind sampling admissible (rho_F >= rho_c)\n');
    else
        fprintf('=> STRUCTURE-SENSITIVE: facies-aware sampling needed (rho_F < rho_c)\n');
    end
    fprintf('   margin |rho_F - rho_c| = %.3f (interpret against the sparse-data uncertainty)\n', abs(rhoF-out.rho_c));

    % --- facies-aware vs facies-blind goal-information gain (diagnostic) ----
    Gam = facies_prior(rhoF,blocks,cross);
    Nmon=5; Mmar=3;
    mon = greedy_design(Gcand,H,Gam,noise,Nmon);     % facies-aware
    ig_aware = eig_operator(Gcand(mon,:),H,Gam,diag(noise(mon)));
    Gam1 = facies_prior(1.0,blocks,cross);
    blindS = greedy_design(Gcand,H,Gam1,noise,Nmon); % facies-blind (pooled prior)
    ig_blind = eig_operator(Gcand(blindS,:),H,Gam,diag(noise(blindS)));
    gain = 100*(ig_aware-ig_blind)/max(ig_aware,eps);
    fprintf('goal-info gain facies-aware vs facies-blind = %.0f%%  (EIG %.3f vs %.3f nats)\n', gain, ig_aware, ig_blind);

    % --- field design: SAME shared full-grid model as the maps -------------
    % (the well LOCATIONS come from FUSHE_KUQE_FIELD_DESIGN, so this report
    %  coincides exactly with fushe_kuqe_design and fushe_kuqe_eig_map).
    try
        Rd = fushe_kuqe_field_design(xlsxfile);
        fprintf('\n--- Gate 3 design (full-grid model; matches the maps) ---\n');
        fprintf('N=%d monitoring wells: %s\n', Rd.P.Nmon, strjoin(cellstr(Rd.monID),', '));
        fprintf('M=%d MAR locations:    %s\n', Rd.P.Nmar, strjoin(cellstr(Rd.marID),', '));
    catch err
        fprintf('\n[design] needs %s for the shared full-grid model: %s\n', xlsxfile, err.message);
    end
end
