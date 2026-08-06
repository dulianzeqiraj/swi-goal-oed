function T = r2_rhoc_sensitivity()
%R2_RHOC_SENSITIVITY  rho_c across configurations (answers R2-5).
%
%   Reviewer #2, R2-5: "the critical correlation rho_c ~= 0.76 is derived from
%   the synthetic configuration considered in this study ... clarify that this
%   threshold is configuration-dependent rather than generally applicable and
%   discuss how it may change with different model settings."
%
%   This script sweeps the configuration knobs of the synthetic study of
%   Section 6 (base: K=3 facies, nk=4 params each, r_within=0.7, noise
%   nf=[0.05 0.30 0.80], goal on the first fine-facies parameter, budget B=2,
%   exhaustive design search; identical to demo_phase_boundary), one at a
%   time, and reports rho_c and the maximum pooling loss for each variant --
%   the quantitative content of the "configuration-dependent" statement.
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end

    base = struct('counts', [4 4 4], 'r_within', 0.7, 'nf', [0.05 0.30 0.80], ...
                  'B', 2, 'goal', 'first');
    rho_grid = linspace(0, 1, 401);

    V = {};                                            % {name, cfg}
    V(end+1,:) = {'base (Sec. 6 configuration)',       base};
    for r = [0.5 0.6 0.8 0.9]
        c = base; c.r_within = r;
        V(end+1,:) = {sprintf('r_within = %.1f', r),   c}; %#ok<AGROW>
    end
    c = base; c.nf = [0.80 0.30 0.05];
    V(end+1,:) = {'noise swapped (fine precise)',      c};
    c = base; c.nf = base.nf * 0.5;
    V(end+1,:) = {'noise x0.5',                        c};
    c = base; c.nf = base.nf * 2;
    V(end+1,:) = {'noise x2',                          c};
    c = base; c.B = 3;
    V(end+1,:) = {'budget B = 3',                      c};
    c = base; c.B = 4;
    V(end+1,:) = {'budget B = 4',                      c};
    c = base; c.goal = 'spread';
    V(end+1,:) = {'goal spread over fine facies',      c};
    c = base; c.counts = [8 8 8];
    V(end+1,:) = {'size nk = 8 (24 params)',           c};
    c = base; c.counts = [16 16 16];
    V(end+1,:) = {'size nk = 16 (48 params)',          c};
    c = base; c.counts = [11 14 7];
    V(end+1,:) = {'field facies counts [11 14 7]',     c};

    nV = size(V, 1);
    name = strings(nV, 1); rc = zeros(nV, 1); lossPct = zeros(nV, 1);
    lossNats = zeros(nV, 1); lossPctOpt = zeros(nV, 1);
    fprintf('=== R2: rho_c configuration sensitivity (%d variants) ===\n', nV);
    for v = 1:nV
        cfg = V{v, 2}; tv = tic;
        [Gc, H, blocks, cross, noise] = build_cfg(cfg);
        out = phase_boundary(Gc, H, blocks, cross, noise, cfg.B, rho_grid);
        e0 = eig_operator(Gc(out.d0, :), H, facies_prior(0, blocks, cross), diag(noise(out.d0)));
        eOpt0 = e0 + out.L(1);            % optimal EIG at rho = 0 (= pooled + loss there)
        name(v) = V{v, 1};
        rc(v) = out.rho_c;
        lossNats(v) = max(out.L);
        lossPct(v) = 100 * max(out.L) / max(e0, eps);       % of pooled-design EIG (Sec. 6 convention)
        lossPctOpt(v) = 100 * max(out.L) / max(eOpt0, eps); % of optimal EIG at rho=0 (bounded)
        fprintf('  %-34s  rho_c = %.3f   Lmax = %.4f nats (%5.1f%% of optimal at rho=0)   (%.1f s)\n', ...
                name(v), rc(v), lossNats(v), lossPctOpt(v), toc(tv));
    end

    T = table(name, rc, lossNats, lossPctOpt, lossPct, 'VariableNames', ...
              {'configuration', 'rho_c', 'max_loss_nats', 'max_loss_pct_of_optimal', 'max_loss_pct_of_pooled'});
    writetable(T, fullfile(outdir, 'r2_rhoc_sensitivity.csv'));
    fprintf('\nrho_c range across variants: %.3f .. %.3f  (base %.3f)\n', ...
            min(rc), max(rc), rc(1));
    fprintf('saved: r2_rhoc_sensitivity.csv\n');
end

% ------------------------------------------------------------------------
function [Gcand, H, blocks, cross, noise] = build_cfg(cfg)
%Generalization of demo_phase_boundary/build_config to per-facies counts and
%goal placement; identical to it for counts=[nk nk nk], goal='first'.
    counts = cfg.counts; K = numel(counts); n = sum(counts);
    fac = zeros(n, 1); idx = 1;
    for k = 1:K
        fac(idx:idx+counts(k)-1) = k; idx = idx + counts(k);
    end
    blocks = cell(1, K);
    for k = 1:K
        nk = counts(k);
        blocks{k} = (1 - cfg.r_within) * eye(nk) + cfg.r_within * ones(nk);
    end
    cross = zeros(n);
    for i = 1:n
        for j = 1:n
            if fac(i) ~= fac(j), cross(i, j) = cfg.r_within; end
        end
    end
    Gcand = eye(n);
    noise = cfg.nf(fac)';
    H = zeros(1, n);
    switch cfg.goal
        case 'spread'
            sel = find(fac == K); H(sel) = 1 / numel(sel);
        otherwise
            H(find(fac == K, 1, 'first')) = 1.0;
    end
end
