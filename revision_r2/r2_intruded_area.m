function out = r2_intruded_area()
%R2_INTRUDED_AREA  Modeled intruded-area fraction + spatial-plausibility
%   numbers for the "consistency with published hydrochemical observations"
%   subsection (answers R2-2/R2-3 constructively; sources: Cenameri &
%   Beqiraj 2016 -- transcribed in workbook sheets 5-7).
%
%   Published anchors (sheet 7_Cenameri2016_SWI_Facts):
%     - area affected by SWI ~15% (upper aquifer layer);
%     - wedge direction SW (coast) -> NE;
%     - max salinity 1500 mg/L (first aquifer), 3500 mg/L (second).
%
%   This script computes, on the published baseline model (legacy rule,
%   rhoF = 0.6, i.e. exactly the R1 configuration):
%     1. the modeled baseline intruded area [km^2], the polygon area, and the
%        modeled intruded fraction [%] for comparison with the ~15% figure;
%     2. the mean intrusion indicator binned by distance from the coast
%        (monotone decay = the SW->NE attenuation the literature reports);
%     3. the centroid of the intruded region relative to the domain centroid
%        (wedge side check).
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end
    xlsx = fullfile(root, 'data', 'Fushe_Kuqe_All_Data.xlsx');

    R = fushe_kuqe_field_design(xlsx);            % published R1 configuration
    fprintf('=== R2: modeled intruded area vs published ~15%% ===\n');

    % ---- 1. areas ----------------------------------------------------------
    Apoly = polyarea(R.Bk(:, 1), R.Bk(:, 2));     % km^2 (Bk is in km)
    Acell = R.Nc * R.area / 1e6;                  % active-cell area, km^2
    frac  = 100 * R.baseArea / Apoly;
    fracC = 100 * R.baseArea / Acell;
    fprintf('baseline intruded area   = %.1f km^2\n', R.baseArea);
    fprintf('aquifer polygon area     = %.1f km^2  (active cells: %.1f km^2)\n', Apoly, Acell);
    fprintf('modeled intruded fraction= %.1f%% of polygon (%.1f%% of active cells)\n', frac, fracC);
    fprintf('published (Cenameri & Beqiraj 2016): ~15%% of the upper aquifer layer\n');

    % ---- 2. intrusion indicator vs distance from coast ---------------------
    s = 0.15;
    intr = 1 ./ (1 + exp(-(R.hcrit - R.h0) / s));         % same sigmoid as goalA
    coastXrow = nan(R.ny, 1);
    for j = 1:R.ny
        ii = find(R.inside(j, :), 1, 'first');
        if ~isempty(ii), coastXrow(j) = R.xs(ii); end
    end
    dcoast = arrayfun(@(k) R.xs(R.ai(k)) - coastXrow(R.aj(k)), (1:R.Nc)');
    edges = [0 2 4 6 8 10 14 18 25 40];
    fprintf('\nmean intrusion indicator by distance from the (western) coast:\n');
    prof = nan(numel(edges) - 1, 3);
    for b = 1:numel(edges) - 1
        m = dcoast >= edges(b) & dcoast < edges(b + 1);
        prof(b, :) = [edges(b) edges(b + 1) mean(intr(m))];
        fprintf('  %5.1f-%5.1f km : %6.3f   (n=%d cells)\n', edges(b), edges(b+1), mean(intr(m)), sum(m));
    end
    mono = all(diff(prof(~isnan(prof(:, 3)), 3)) <= 1e-9);
    fprintf('monotone decay with distance from coast: %s\n', tif(mono));

    % ---- 3. intruded-region centroid ---------------------------------------
    w = intr / sum(intr);
    icx = sum(w .* R.xs(R.ai)'); icy = sum(w .* R.ys(R.aj)');
    dcx = mean(R.xs(R.ai)); dcy = mean(R.ys(R.aj));
    fprintf('\nintruded-region centroid vs domain centroid: dx=%+.1f km, dy=%+.1f km -> %s side\n', ...
            icx - dcx, icy - dcy, compass8(icx - dcx, icy - dcy));

    out = struct('baseArea', R.baseArea, 'Apoly', Apoly, 'Acell', Acell, ...
                 'frac_polygon_pct', frac, 'frac_cells_pct', fracC, ...
                 'profile', prof, 'monotone', mono, ...
                 'centroid_shift_km', [icx - dcx, icy - dcy]);
    writematrix(prof, fullfile(outdir, 'r2_intrusion_profile.csv'));
    save(fullfile(outdir, 'r2_intruded_area.mat'), '-struct', 'out');
    fprintf('saved: r2_intrusion_profile.csv, r2_intruded_area.mat\n');
end

function s = tif(c), if c, s = 'YES'; else, s = 'NO'; end, end

function s = compass8(dx, dy)
    ang = atan2d(dy, dx);
    dirs = {'E','NE','N','NW','W','SW','S','SE','E'};
    s = dirs{1 + mod(round(ang / 45), 8)};
end
