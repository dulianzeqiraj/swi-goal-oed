function out = r2_fit_extras()
%R2_FIT_EXTRAS  Recompute the descriptive transition statistics quoted in
%   Section 6 of the manuscript (left slope of the order parameter at rho_c
%   and the log-log exponent of Lambda below rho_c), so that every number in
%   the text traces to an archived output. Values that this script cannot
%   reproduce are removed from the manuscript.
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end

    % base Section-6 configuration (identical to demo_phase_boundary)
    K = 3; nk = 4; r_within = 0.7; B = 2;
    n = K * nk; fac = reshape(repmat(1:K, nk, 1), [], 1);
    blocks = cell(1, K);
    for k = 1:K, blocks{k} = (1 - r_within) * eye(nk) + r_within * ones(nk); end
    cross = zeros(n);
    for i = 1:n, for j = 1:n, if fac(i) ~= fac(j), cross(i, j) = r_within; end, end, end
    Gcand = eye(n); nf = [0.05 0.30 0.80]; noise = nf(fac)';
    H = zeros(1, n); H(find(fac == K, 1, 'first')) = 1.0;

    rho = linspace(0, 1, 401);
    pb = phase_boundary(Gcand, H, blocks, cross, noise, B, rho);
    rho_v = pb.rho(:); Lam_v = pb.Lambda(:); rc = pb.rho_c;
    ic = find(rho_v == rc);

    % left-sided slope of Lambda at rho_c (one-grid-step finite difference)
    slopeL = (Lam_v(ic) - Lam_v(ic - 1)) / (rho_v(ic) - rho_v(ic - 1));
    % and over a 5-point left window for robustness
    p5 = polyfit(rho_v(ic-4:ic), Lam_v(ic-4:ic), 1);
    slopeL5 = p5(1);

    % log-log exponent of Lambda vs (rho_c - rho) below the boundary
    win = rho_v >= rc - 0.30 & rho_v <= rc - 0.0125 & Lam_v > 0;
    pfit = polyfit(log(rc - rho_v(win)), log(Lam_v(win)), 1);
    beta = pfit(1);

    fprintf('=== R2: descriptive transition statistics (base configuration) ===\n');
    fprintf('rho_c (grid step 0.0025)          = %.4f\n', rc);
    fprintf('left slope of Lambda at rho_c     = %.3f (1-step), %.3f (5-point)\n', slopeL, slopeL5);
    fprintf('log-log exponent beta below rho_c = %.3f (window rho in [rho_c-0.30, rho_c-0.0125])\n', beta);
    fprintf('above rho_c: Lambda identically 0 (machine zero) -> slope 0\n');

    out = struct('rho_c', rc, 'slopeL', slopeL, 'slopeL5', slopeL5, 'beta', beta);
    writematrix([rc slopeL slopeL5 beta], fullfile(outdir, 'r2_fit_extras.csv'));
    save(fullfile(outdir, 'r2_fit_extras.mat'), '-struct', 'out');
    fprintf('saved: r2_fit_extras.csv\n');
end
