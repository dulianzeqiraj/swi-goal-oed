function out = fushe_kuqe_prag_mar(xlsxfile, supplyIDs, Q, N)
%FUSHE_KUQE_PRAG_MAR  PRAG-MAR on the real Fushe-Kuqe aquifer: recharge sites
%   chosen for the risk that a supply well is salinized, against the published
%   sites chosen for the intruded area.
%
%   out = FUSHE_KUQE_PRAG_MAR(xlsxfile, supplyIDs, Q, N)
%
%   xlsxfile  : field dataset (default data/Fushe_Kuqe_All_Data.xlsx)
%   supplyIDs : one or two supply-well IDs (default {'A23','R16'}: in each
%               sector, north and south of N = 25 km, the inside well whose prior
%               intrusion probability is closest to 1/2, outside the published
%               monitoring design; see experiments/prag_go_fushe_kuqe)
%   Q         : recharge per site [m3/day] (default [2500 5000 10000])
%   N         : prior realizations for the exact check (default 2000)
%
%   1. FUSHE_KUQE_FIELD_DESIGN builds the shared model and, with P.supplyIDs,
%      the PRAG-MAR field RISK_c (closed form, two adjoint solves) and its
%      three sites. The published rule is used: top 3, 6 km apart, snapped.
%   2. PRAG_MAR_CHECK evaluates the published and the PRAG-MAR sites exactly on
%      N prior realizations: P(A), P(B), P(A or B) intruded and the mean area.
%   3. A two-panel map (area adjoint vs PRAG-MAR) is written to
%      fushe_kuqe_prag_mar.png.
%
%   Reference output (Python port, 2 000 realizations, 5 000 m3/day per site):
%   P(A or B) 0.79 without MAR, 0.62 with the published sites (A18, P21, P16),
%   0.04 with the PRAG-MAR sites (A23, R16, P21); mean area 98.4 -> 87.2 vs
%   89.5 km^2. Exact numbers here differ by Monte Carlo error only.
%
%   Scope: as FUSHE_KUQE_DESIGN, an uncalibrated model; the supply wells stand
%   in for the Gorre / Fushe-Kuqe pumping stations, whose coordinates are not
%   in the dataset. The model treats the whole western margin as the sea; with
%   the geolocated sea boundary of the chloride study (contact only on the
%   northern 23 km) the setting changes, and PRAG-MAR is recomputed for pumped
%   supply wells by chloride_fk/matlab/fkcl_prag_mar.m.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    here = fileparts(mfilename('fullpath'));
    if nargin < 1 || isempty(xlsxfile), xlsxfile = fullfile(here, '..', 'data', 'Fushe_Kuqe_All_Data.xlsx'); end
    if nargin < 2 || isempty(supplyIDs), supplyIDs = {'A23', 'R16'}; end
    if nargin < 3 || isempty(Q), Q = [2500 5000 10000]; end
    if nargin < 4 || isempty(N), N = 2000; end
    if exist('prag_mar', 'file') ~= 2, addpath(fullfile(here, '..', 'src')); end

    R = fushe_kuqe_field_design(xlsxfile, struct('supplyIDs', {cellstr(supplyIDs)}));
    I = R.pragInfo;
    fprintf('supply wells: %s   (h < %.2f m means intruded)\n', strjoin(R.supplyID', ', '), R.hcrit);
    fprintf('linear moments: mean head %s m, sd %s m, r = %.3f; P(intruded) = %.3f\n', ...
            mat2str(R.h0(R.supplyCell)', 3), mat2str(I.s, 3), I.r, I.P0);
    fprintf('published MAR (area adjoint): %s\n', strjoin(cellstr(R.marID), ', '));
    fprintf('PRAG-MAR (supply-well risk):  %s\n', strjoin(cellstr(R.pragID), ', '));

    tic;
    out = prag_mar_check(R, {R.marCell, R.pragCell}, Q, N);
    fprintf('\nexact check on %d prior realizations (%.0f s, assembly rel. diff %.1e)\n', N, toc, out.assemblyRelErr);
    fprintf('%-28s %10s %7s %7s %10s %12s\n', 'sites', 'Q [m3/d]', 'P(A)', 'P(B)', 'P(A or B)', 'area [km2]');
    fprintf('%-28s %10s %7.3f %7.3f %10.3f %12.1f\n', 'none', '-', out.none.pA, out.none.pB, out.none.pAB, out.none.area);
    names = {['published: ' strjoin(cellstr(R.marID), ',')], ['PRAG-MAR: ' strjoin(cellstr(R.pragID), ',')]};
    for d = 1:2
        D = out.design(d);
        for q = 1:numel(Q)
            fprintf('%-28s %10.0f %7.3f %7.3f %10.3f %12.1f\n', names{d}, Q(q), D.pA(q), D.pB(q), D.pAB(q), D.area(q));
        end
    end
    out.R = R;

    % ---- map: area adjoint (published) vs PRAG-MAR ---------------------------
    try
        [~, qr] = min(abs(Q - 5000));
        fig = figure('Color', 'w', 'Position', [60 60 900 760], 'Visible', 'off');
        fields = {R.MAR_c, R.RISK_c}; sites = {R.marCell, R.pragCell};
        ttl = {sprintf('(a) area adjoint (published)\nP(A or B) %.2f -> %.2f', out.none.pAB, out.design(1).pAB(qr)), ...
               sprintf('(b) PRAG-MAR, supply-well risk\nP(A or B) %.2f -> %.2f', out.none.pAB, out.design(2).pAB(qr))};
        G0 = nan(R.ny, R.nx); G0(R.act) = R.h0;
        for p = 1:2
            subplot(1, 2, p);
            f = fields{p} / max(fields{p}); f(f < 0) = 0; f(R.coast(R.act)) = NaN;
            G = nan(R.ny, R.nx); G(R.act) = sqrt(f);         % square-root scale
            pcolor(R.xs, R.ys, G); shading flat; hold on; colormap(parula);
            contour(R.xs, R.ys, G0, [R.hcrit R.hcrit], 'k--', 'LineWidth', 1.0);
            plot(R.Bk(:, 1), R.Bk(:, 2), 'k-', 'LineWidth', 0.8);
            c = sites{p};
            plot(R.xs(R.ai(c)), R.ys(R.aj(c)), 'd', 'MarkerSize', 10, 'MarkerFaceColor', [.92 .41 .20], 'MarkerEdgeColor', 'w');
            sx = R.xs(R.ai(R.supplyCell)); sy = R.ys(R.aj(R.supplyCell));
            plot(sx, sy, 'v', 'MarkerSize', 8, 'MarkerFaceColor', 'k', 'MarkerEdgeColor', 'w');
            text(sx - 0.6, sy + 1.2, R.supplyID, 'FontWeight', 'bold', 'FontSize', 9);
            axis equal; axis([0 max(R.xs) 0 max(R.ys)]); box on;
            xlabel('E [km]'); ylabel('N [km]'); title(ttl{p}, 'FontWeight', 'normal');
            cb = colorbar; ylabel(cb, 'relative effect (sqrt scale)');
        end
        save_figure(fig, 'fushe_kuqe_prag_mar.png', 300);
        fprintf('\nFigure written: fushe_kuqe_prag_mar.png\n');
    catch err
        warning('fushe_kuqe_prag_mar:figure', 'Figure skipped: %s', err.message);
    end
end
