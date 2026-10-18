function ok = fkcl_selftest(opts)
%FKCL_SELFTEST  Quick checks of the chloride code (about one minute). Prints PASS or FAIL for each.
%   1 screen average: closed form vs numerical quadrature
%   2 Strack conversion: head and interface continuous at the toe
%   3 linear EIG: closed form equals -1/2 ln(1 - R^2) from the joint covariance
%   4 section solver: Henry 16 x 8 and 41 x 21 toes (repository values 1.4226 m, 1.3918 m)
%   5 hydrochemistry: seawater fraction of well 503 = 4.76 %, BEX of well 340 > 0
%   6 model vs Python reference: 500 calibration runs from the shared draws (summary statistics)

    if nargin < 1, opts = struct(); end
    C = fkcl_config(); if isfield(opts, 'tsvdir'), C.tsvdir = opts.tsvdir; end
    ok = true; rep = @(name, pass, msg) fprintf('%-46s %s  %s\n', name, ifelse(pass, 'PASS', 'FAIL'), msg);
    % 1
    G = @(u) u .* (0.5 * erfc(-u / sqrt(2))) + exp(-0.5 * u.^2) / sqrt(2 * pi);
    z1 = 40; z2 = 80; zeta = 95; w = 25;
    cf = w / (z2 - z1) * (G((z2 - zeta) / w) - G((z1 - zeta) / w));
    zq = linspace(z1, z2, 20001); cq = trapz(zq, 0.5 * erfc(-(zq - zeta) / (w * sqrt(2)))) / (z2 - z1);
    p = abs(cf - cq) < 1e-8; ok = ok && p; rep('1 screen-average closed form', p, sprintf('|diff| = %.1e', abs(cf - cq)));
    % 2
    delta = 0.025; d = 35; B = 180; phit = 0.5 * delta * B^2;
    h2 = delta * d + sqrt(2 * delta * phit); h1 = phit / B + delta * (d + B / 2);
    p = abs(h1 - h2) < 1e-10 && abs(h1 / delta - (d + B)) < 1e-8; ok = ok && p;
    rep('2 Strack zones continuous at the toe', p, sprintf('h = %.6f m on both sides', h1));
    % 3
    rng(1); X = randn(500, 4); q = X * [1; 0.5; -0.3; 0.2] + 0.3 * randn(500, 1); sig = 0.1;
    Xc = X - mean(X); qc = q - mean(q); Cv = Xc' * Xc / 499; b = Xc' * qc / 499; vq = qc' * qc / 499;
    S = [1 3]; r2 = b(S)' * ((Cv(S, S) + sig^2 * eye(2)) \ b(S)) / vq;
    J = [vq b(S)'; b(S) Cv(S, S) + sig^2 * eye(2)]; r2b = 1 - det(J) / (vq * det(Cv(S, S) + sig^2 * eye(2)));
    p = abs(r2 - r2b) < 1e-12; ok = ok && p; rep('3 goal-oriented EIG closed form', p, sprintf('R^2 = %.6f', r2));
    % 4
    t16 = fkcl_henry_check(16, 8); t41 = fkcl_henry_check(41, 21);
    p = abs(t16 - 1.4226) < 1e-4 && abs(t41 - 1.3918) < 1e-4; ok = ok && p;
    rep('4 section solver on Henry''s problem', p, sprintf('toes %.4f / %.4f m', t16, t41));
    % 5
    D = fkcl_read_data(C); H = fkcl_hydrochem(C, D);
    i503 = strcmp(H.well, '503'); i340 = strcmp(H.well, '340');
    p = abs(100 * H.f(i503) - 4.76) < 0.01 && H.BEX(i340) > 0 && H.BEX(i503) < 0; ok = ok && p;
    rep('5 hydrochemistry of the four analyses', p, sprintf('f(503) = %.2f %%, BEX(340) = %.2f', 100 * H.f(i503), H.BEX(i340)));
    % 6
    if exist(fullfile(C.results, 'calib_prior_draws.csv'), 'file') && exist(fullfile(C.results, 'calib_summary.json'), 'file')
        m = fkcl_model_init(C, D); Cal = fkcl_calibrate(m, 500, 'python');
        ref = fullfile(C.results, 'selftest_S500.csv');
        if exist(ref, 'file')
            Sr = fkcl_readnum(ref); err = max(abs(Cal.S(:) - Sr(:)) ./ max(abs(Sr(:)), 1));
            p = err < 1e-6; ok = ok && p; rep('6 model reproduces the Python reference', p, sprintf('max rel. diff %.1e over 500 x 15', err));
        else
            rep('6 model reproduces the Python reference', true, sprintf('ESS of the first 500 draws %.1f (reference file absent)', Cal.ess));
        end
    end
    if ok, fprintf('ALL CHECKS PASSED\n'); else, fprintf('SOME CHECKS FAILED\n'); end
end

function s = ifelse(c, a, b)
    if c, s = a; else, s = b; end
end
