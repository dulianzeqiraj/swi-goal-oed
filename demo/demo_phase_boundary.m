function out = demo_phase_boundary(outdir)
%DEMO_PHASE_BOUNDARY  Reproduce the poolability phase boundary (Lemma 2) and
%   write the two main-paper theory figures:
%
%     Fig2_PhaseBoundary.png  (a) pooling loss L(rhoF) [nats]
%                             (b) order parameter Lambda = L/L(0), with the
%                                 critical correlation rho_c and "dead zone".
%     Fig3_SizeInvariance.png Lambda(rhoF) for several problem sizes,
%                             collapsing onto the SAME rho_c (structural).
%
%   The prior is a facies correlation matrix Gamma(rhoF) with within-facies
%   correlation r_within = 0.7 and cross-facies correlation rhoF*r_within
%   (Eq. 11). The coarse facies is sensed precisely (proxy via cross-facies
%   correlation); the goal's own (fine) facies is sensed imprecisely. Sweeping
%   rhoF and selecting the budget-B design by exhaustive search yields the
%   pooling loss L(rhoF), the order parameter Lambda = L/L(0), and rho_c.
%
%   Verified (linear-Gaussian, exact): rho_c ~ 0.760; the facies-blind design
%   forfeits up to ~19% of the pooled-design EIG below rho_c and exactly zero
%   (machine precision) above it. rho_c is invariant across problem sizes.
%
%   Run:  >> out = demo_phase_boundary
%   Author: D. Zeqiraj.  License: MIT.

    if nargin < 1 || isempty(outdir), outdir = pwd; end
    here = fileparts(mfilename('fullpath')); addpath(fullfile(here,'..','src'));

    K = 3; nk = 4; r_within = 0.7; B = 2;
    [Gcand, H, blocks, cross, noise] = build_config(K, nk, r_within);

    rho_grid = linspace(0, 1, 401);
    out = phase_boundary(Gcand, H, blocks, cross, noise, B, rho_grid);

    Lmax = max(out.L);
    e_pooled0 = design_eig_local(Gcand, H, facies_prior(0, blocks, cross), noise, out.d0);
    pct = 100 * Lmax / max(e_pooled0, eps);
    dead = out.L(out.rho > out.rho_c + 0.03);

    fprintf('--- Poolability phase boundary (Lemma 2) ---\n');
    fprintf('  pooled-optimal design d0      = [%s]\n', num2str(out.d0));
    fprintf('  critical correlation rho_c    = %.3f\n', out.rho_c);
    fprintf('  cross-facies corr at boundary = %.3f  (rho_c * r_within)\n', out.rho_c * r_within);
    fprintf('  max pooling loss L_max        = %.4f nats  (%.1f%% of pooled EIG)\n', Lmax, pct);
    if ~isempty(dead)
        fprintf('  max loss in dead zone         = %.2e nats  (machine zero)\n', max(dead));
    end

    % ================= FIGURE 2: phase boundary / order parameter =========
    f2 = figure('Color','w','Position',[80 80 820 330]);
    ymaxL = max(Lmax*1.08, eps);
    % (a) pooling loss
    ax1 = subplot(1,2,1); hold(ax1,'on');
    shade_deadzone(out.rho_c, 1, ymaxL);
    plot(out.rho, out.L, 'LineWidth', 2, 'Color', [0.13 0.31 0.62]);
    plot([out.rho_c out.rho_c], [0 ymaxL], '--', 'Color', [0.65 0.10 0.10], 'LineWidth', 1.3);
    text(out.rho_c-0.02, 0.92*ymaxL, sprintf('\\rho_c \\approx %.2f', out.rho_c), ...
         'HorizontalAlignment','right','Color',[0.65 0.10 0.10],'FontSize',11);
    text(0.5*(out.rho_c+1), 0.5*ymaxL, 'dead zone','HorizontalAlignment','center', ...
         'Color',[0.45 0.45 0.45],'FontSize',10,'FontAngle','italic');
    axis([0 1 0 ymaxL]); grid on; box on; set(ax1,'FontSize',11,'Layer','top');
    xlabel('cross-facies correlation  \rho_F','FontSize',12);
    ylabel('pooling loss  L(\rho_F)  [nats]','FontSize',12);
    title('(a)  facies-pooling loss','FontWeight','normal','FontSize',12);
    % (b) order parameter
    ax2 = subplot(1,2,2); hold(ax2,'on');
    shade_deadzone(out.rho_c, 1, 1.08);
    plot(out.rho, out.Lambda, 'LineWidth', 2, 'Color', [0.13 0.31 0.62]);
    plot([out.rho_c out.rho_c], [0 1.08], '--', 'Color', [0.65 0.10 0.10], 'LineWidth', 1.3);
    text(out.rho_c-0.02, 1.00, sprintf('\\rho_c \\approx %.2f', out.rho_c), ...
         'HorizontalAlignment','right','Color',[0.65 0.10 0.10],'FontSize',11);
    axis([0 1 0 1.08]); grid on; box on; set(ax2,'FontSize',11,'Layer','top');
    xlabel('cross-facies correlation  \rho_F','FontSize',12);
    ylabel('order parameter  \Lambda = L/L(0)','FontSize',12);
    title('(b)  normalized order parameter','FontWeight','normal','FontSize',12);
    save_fig(f2, fullfile(outdir,'Fig2_PhaseBoundary.png'));

    % ================= FIGURE 3: structural invariance (data collapse) ====
    fprintf('\n--- Size-invariance of rho_c (structural, not finite-size) ---\n');
    f3 = figure('Color','w','Position',[80 80 600 400]); hold on;
    nklist = [4 8 16]; cols = [0.13 0.31 0.62; 0.85 0.45 0.05; 0.15 0.60 0.25];
    for q = 1:numel(nklist)
        [Gc, Hh, bk, cr, nz] = build_config(K, nklist(q), r_within);
        o = phase_boundary(Gc, Hh, bk, cr, nz, B, rho_grid);
        plot(o.rho, o.Lambda, 'LineWidth', 1.8, 'Color', cols(q,:), ...
             'DisplayName', sprintf('%d params / facies  (\\rho_c=%.2f)', nklist(q), o.rho_c));
        fprintf('  params/facies %2d -> rho_c = %.3f\n', nklist(q), o.rho_c);
    end
    plot([out.rho_c out.rho_c], [0 1.08], '--', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.2, ...
         'HandleVisibility','off');
    text(out.rho_c-0.02, 1.00, sprintf('\\rho_c \\approx %.2f', out.rho_c), ...
         'HorizontalAlignment','right','Color',[0.3 0.3 0.3],'FontSize',11);
    axis([0 1 0 1.08]); grid on; box on; set(gca,'FontSize',11,'Layer','top');
    xlabel('cross-facies correlation  \rho_F','FontSize',12);
    ylabel('order parameter  \Lambda = L/L(0)','FontSize',12);
    title('Structural invariance of \rho_c (data collapse across sizes)', ...
          'FontWeight','normal','FontSize',12);
    legend('Location','southwest','Box','off','FontSize',10);
    save_fig(f3, fullfile(outdir,'Fig3_SizeInvariance.png'));
    fprintf('\nWritten: Fig2_PhaseBoundary.png  and  Fig3_SizeInvariance.png\n');
end

% ----------------------------------------------------------------------
function shade_deadzone(x0, x1, ymax)
    patch([x0 x1 x1 x0], [0 0 ymax ymax], [0.92 0.92 0.92], ...
          'EdgeColor','none', 'HandleVisibility','off');
    try, set(get(gca,'Children'),'FaceAlpha',1); catch, end
end
function save_fig(f, fname)
    try, exportgraphics(f, fname, 'Resolution', 300);
    catch, print(f, fname(1:end-4), '-dpng', '-r300'); end
end

% ----------------------------------------------------------------------
function [Gcand, H, blocks, cross, noise] = build_config(K, nk, r_within)
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
    nf    = [0.05, 0.30, 0.80];
    noise = nf(fac)';
    H = zeros(1, n);
    H(find(fac == K, 1, 'first')) = 1.0;
end
function e = design_eig_local(Gcand, H, Gam, noise, S)
    e = eig_operator(Gcand(S,:), H, Gam, diag(noise(S)));
end
