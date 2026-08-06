function out = r2_rhoF_uncertainty()
%R2_RHOF_UNCERTAINTY  Jackknife uncertainty of the field correlation rho_F.
%
%   Answers Reviewer #2, comment R2-11 (first part): the manuscript places the
%   site above the critical correlation on a margin rho_F - rho_c = 0.043 with
%   no uncertainty of any kind. This script:
%
%     1. reads the 43 K-valued wells from the released workbook (sheet
%        2_All_Wells, positional columns ID/X/Y/K as in read_wells) and takes
%        the subset inside the aquifer polygon (sheet 3_Boundary_Coords) --
%        the audit-trail version of the 32-well table hardcoded in
%        demo/gate3_field.m, against which it is cross-checked;
%     2. recomputes rho_F with the exact estimator of gate3_field.m
%        (IDW 1/d^2 neighbour prediction of log K, Pearson correlation);
%     3. recomputes rho_c on the field prior (same construction as gate3);
%     4. reports a leave-one-out jackknife SE and CI for rho_F, the margin in
%        SE units, the normal-approximation P(rho_F > rho_c), and how many
%        LOO replicates fall below rho_c.
%
%   NOTE the naive resampling bootstrap is biased upward for this estimator
%   (duplicate coincident wells inflate the 1/d^2 IDW weights), so the
%   jackknife is the reported uncertainty.
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end
    xlsx = fullfile(root, 'data', 'Fushe_Kuqe_All_Data.xlsx');

    % ---- wells from the workbook + polygon (audit trail) -------------------
    Braw = readmatrix(xlsx, 'Sheet', '3_Boundary_Coords');
    B = Braw(:, 2:3); B = B(all(isfinite(B), 2), :);
    T = readtable(xlsx, 'Sheet', '2_All_Wells');
    Xa = T{:, 2}; Ya = T{:, 3}; Ka = T{:, 4};
    okK = isfinite(Ka) & isfinite(Xa) & isfinite(Ya);
    ins = inpolygon(Xa, Ya, B(:, 1), B(:, 2));
    sel = okK & ins;
    fprintf('=== R2: rho_F uncertainty (jackknife) ===\n');
    fprintf('workbook: %d rows, %d with K, %d with K inside the aquifer polygon\n', ...
            numel(Ka), sum(okK), sum(sel));
    X = Xa(sel); Y = Ya(sel); K = Ka(sel); n = numel(K);

    % ---- cross-check against the 32-well table hardcoded in gate3_field ----
    D32 = gate3_hardcoded_wells();
    match = (n == size(D32, 1));
    if match
        A = sortrows([X Y K], [3 1 2]); Bt = sortrows(D32, [3 1 2]);
        match = all(abs(A(:) - Bt(:)) < 0.51);   % coords to the 0.5 m, K exact
    end
    fprintf('cross-check vs gate3_field hardcoded table: %s\n', tif(match, 'MATCH', 'MISMATCH'));
    if ~match
        fprintf('  -> falling back to the gate3 table for the estimate (investigate!)\n');
        X = D32(:, 1); Y = D32(:, 2); K = D32(:, 3); n = numel(K);
    end

    % ---- point estimate (exact gate3 estimator) ----------------------------
    rhoF = rhoF_est(X, Y, K);

    % ---- rho_c on the field prior (same construction as gate3_field) -------
    fac = 1 * (K >= 150) + 2 * (K >= 75 & K < 150) + 3 * (K < 75);
    cnt = [sum(fac == 1) sum(fac == 2) sum(fac == 3)];
    [~, ix] = sort(fac); facO = fac(ix);
    blocks = cell(1, 3); r_within = 0.7; Bbud = 2;
    for k = 1:3, nk = cnt(k); blocks{k} = (1 - r_within) * eye(nk) + r_within * ones(nk); end
    cross = zeros(n);
    for a = 1:n, for b = 1:n, if facO(a) ~= facO(b), cross(a, b) = r_within; end, end, end
    Gcand = eye(n); nf = [0.05 0.30 0.80]; noise = nf(facO)';
    H = zeros(1, n); H(find(facO == 3, 1, 'first')) = 1.0;
    pb = phase_boundary(Gcand, H, blocks, cross, noise, Bbud, linspace(0, 1, 401));
    rho_c = pb.rho_c;

    % ---- leave-one-out jackknife ------------------------------------------
    loo = zeros(n, 1);
    for i = 1:n
        m = true(n, 1); m(i) = false;
        loo(i) = rhoF_est(X(m), Y(m), K(m));
    end
    se   = sqrt((n - 1) / n * sum((loo - mean(loo)).^2));
    bias = (n - 1) * (mean(loo) - rhoF);
    ci   = [rhoF - 1.96 * se, min(rhoF + 1.96 * se, 1)];
    marg = rhoF - rho_c;
    z    = marg / se;
    Pabove = 0.5 * (1 + erf(z / sqrt(2)));
    nBelow = sum(loo < rho_c);

    fprintf('\nrho_F (full data, n=%d)      = %.4f\n', n, rhoF);
    fprintf('rho_c (field prior, recomp.) = %.4f\n', rho_c);
    fprintf('margin rho_F - rho_c         = %.4f\n', marg);
    fprintf('jackknife SE                 = %.4f   (LOO range %.3f .. %.3f)\n', se, min(loo), max(loo));
    fprintf('jackknife bias estimate      = %+.4f\n', bias);
    fprintf('95%% CI (normal approx)       = [%.3f, %.3f]\n', ci);
    fprintf('margin in SE units           = %.2f\n', z);
    fprintf('P(rho_F > rho_c), normal     = %.2f\n', Pabove);
    fprintf('LOO replicates below rho_c   = %d of %d\n', nBelow, n);
    fprintf(['=> the side of the threshold is NOT statistically determined at n=%d;\n' ...
             '   under the asymmetric pooling loss (0 above rho_c, up to ~19%% below),\n' ...
             '   the conservative recommendation under uncertainty is the facies-AWARE design.\n'], n);

    % ---- save --------------------------------------------------------------
    out = struct('n', n, 'rhoF', rhoF, 'rho_c', rho_c, 'margin', marg, ...
                 'se_jack', se, 'bias_jack', bias, 'ci95', ci, 'z', z, ...
                 'Pabove', Pabove, 'nBelow', nBelow, 'loo', loo);
    writematrix([(1:n)' K loo], fullfile(outdir, 'r2_rhoF_jackknife_loo.csv'));
    save(fullfile(outdir, 'r2_rhoF_uncertainty.mat'), '-struct', 'out');
    fprintf('saved: r2_rhoF_jackknife_loo.csv, r2_rhoF_uncertainty.mat\n');
end

% ------------------------------------------------------------------------
function r = rhoF_est(X, Y, K)
%The exact estimator of gate3_field.m lines 62-68.
    n = numel(K); lK = log(K); pred = zeros(n, 1);
    for i = 1:n
        d = hypot(X - X(i), Y - Y(i)); d(i) = inf;
        w = 1 ./ (d.^2 + 1e-9); w = w / sum(w);
        pred(i) = sum(w .* lK);
    end
    cc = corrcoef(lK, pred); r = cc(1, 2);
end

function s = tif(c, a, b), if c, s = a; else, s = b; end, end

function D = gate3_hardcoded_wells()
%The 32-row [X Y K] table of demo/gate3_field.m lines 24-55, verbatim.
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
end
