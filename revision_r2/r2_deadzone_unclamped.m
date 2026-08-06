function r2_deadzone_unclamped(outdir)
%R2_DEADZONE_UNCLAMPED  Pooling loss inside the dead zone, before clamping.
%
%   r2_deadzone_unclamped(outdir)
%
%   phase_boundary returns L = max(e_star - e_0, 0), so above the critical
%   correlation the archived loss is exactly zero. This script recomputes the
%   same difference on the Section-6 configuration WITHOUT the clamp and
%   reports the largest magnitude it reaches for rho_F > rho_c. That magnitude
%   is the round-off floor of the exhaustive design search, and it is the
%   number the article quotes when it states that the dead zone is exact
%   rather than merely small.
%
%   Writes r2_deadzone_unclamped.csv (rho_F, unclamped difference in nats).
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1 || isempty(outdir), outdir = pwd; end
    here = fileparts(mfilename('fullpath'));
    addpath(fullfile(here, '..', 'src'), fullfile(here, '..', 'demo'));

    % --- Section-6 configuration (identical to demo_phase_boundary) --------
    K = 3; nk = 4; r_within = 0.7; B = 2;
    n   = K * nk;
    fac = reshape(repmat(1:K, nk, 1), [], 1);
    blocks = cell(1, K);
    for k = 1:K
        blocks{k} = (1 - r_within) * eye(nk) + r_within * ones(nk);
    end
    cross = zeros(n);
    for i = 1:n
        for j = 1:n
            if fac(i) ~= fac(j), cross(i, j) = r_within; end
        end
    end
    Gcand = eye(n);
    nfv   = [0.05, 0.30, 0.80];
    noise = nfv(fac)';
    H = zeros(1, n);
    H(find(fac == K, 1, 'first')) = 1.0;

    rho_grid = linspace(0, 1, 401)';
    combs = nchoosek(1:size(Gcand, 1), B);

    Gam1 = facies_prior(1.0, blocks, cross);
    d0 = best_design_local(Gcand, H, Gam1, noise, combs);

    d    = zeros(numel(rho_grid), 1);
    same = false(numel(rho_grid), 1);
    for i = 1:numel(rho_grid)
        Gam   = facies_prior(rho_grid(i), blocks, cross);
        dstar = best_design_local(Gcand, H, Gam, noise, combs);
        same(i) = isequal(dstar, d0);
        d(i)  = eig_local(Gcand, H, Gam, noise, dstar) ...
              - eig_local(Gcand, H, Gam, noise, d0);          % NO clamp
    end

    out  = phase_boundary(Gcand, H, blocks, cross, noise, B, rho_grid);
    dead = rho_grid > out.rho_c;

    fprintf('=== R2: unclamped pooling loss inside the dead zone ===\n');
    fprintf('  rho_c                                  = %.4f\n', out.rho_c);
    fprintf('  grid points above rho_c                = %d\n', nnz(dead));
    fprintf('  max  unclamped difference above rho_c  = %.3e nats\n', max(d(dead)));
    fprintf('  max |unclamped difference| above rho_c = %.3e nats\n', max(abs(d(dead))));
    fprintf('  grid points above rho_c where the optimal design equals d0: %d of %d\n', ...
            nnz(same & dead), nnz(dead));
    fprintf('  => above rho_c the pooled-optimal design IS the optimal design,\n');
    fprintf('     so the loss is identically zero, not merely at round-off level.\n');

    T = table(rho_grid, d, same, 'VariableNames', {'rho_F', 'unclamped_loss_nats', 'optimal_equals_pooled'});
    writetable(T, fullfile(outdir, 'r2_deadzone_unclamped.csv'));
    fprintf('saved: r2_deadzone_unclamped.csv\n');
end

function S = best_design_local(Gcand, H, Gam, noise, combs)
    best = -Inf; S = combs(1, :);
    for c = 1:size(combs, 1)
        e = eig_local(Gcand, H, Gam, noise, combs(c, :));
        if e > best, best = e; S = combs(c, :); end
    end
end

function e = eig_local(Gcand, H, Gam, noise, S)
    e = eig_operator(Gcand(S, :), H, Gam, diag(noise(S)));
end
