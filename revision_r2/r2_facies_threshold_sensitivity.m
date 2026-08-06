function out = r2_facies_threshold_sensitivity()
%R2_FACIES_THRESHOLD_SENSITIVITY  Facies-rule harmonization + classification
%   uncertainty for the field application (answers R2-6, feeds R2-11).
%
%   The released code carries TWO facies rules:
%     gate3_field.m (wells):            coarse K>=150, medium 75<=K<150, fine K<75
%     fushe_kuqe_field_design.m (zones, legacy): coarse zK>150, medium 80<zK<=150, fine zK<=80
%   This script quantifies what harmonizing to the gate3 rule changes:
%     A. zone classification flips and their zK values;
%     B. the design outputs (monitoring/MAR IDs, baseline intruded area,
%        EIG field) under legacy vs harmonized rule, at the published prior
%        rhoF=0.6 AND at the data-estimated rhoF=0.805;
%     C. the well-level (43-well) classification flips between the two rules
%        (only wells at K=150 and K=70 can flip);
%     D. facies-class centroids and the aquifer polygon/coast geometry, to
%        settle the Fig. 5 caption direction (southeast vs northeast).
%
%   Part of the HYDROL82304R1 -> R2 revision. Author: D. Zeqiraj.

    here = fileparts(mfilename('fullpath'));
    root = fullfile(here, '..');
    addpath(fullfile(root, 'src'));
    outdir = fullfile(here, 'r2_results');
    if ~exist(outdir, 'dir'), mkdir(outdir); end
    xlsx = fullfile(root, 'data', 'Fushe_Kuqe_All_Data.xlsx');

    Pdef = struct('b',30,'base',40,'R',5e-4,'delta',0.025,'dx',0.25, ...
                  'sn',0.2,'rhoF',0.6,'Nmon',5,'Nmar',3,'space',6.0);

    fprintf('=== R2: facies-rule harmonization and design sensitivity ===\n');

    % ---- B. four design runs ----------------------------------------------
    runs = { 'legacy,     rhoF=0.600', 'legacy',     0.600;
             'harmonized, rhoF=0.600', 'harmonized', 0.600;
             'legacy,     rhoF=0.805', 'legacy',     0.805;
             'harmonized, rhoF=0.805', 'harmonized', 0.805 };
    R = cell(4, 1);
    for q = 1:4
        P = Pdef; P.faciesRule = runs{q, 2}; P.rhoF = runs{q, 3};
        tv = tic; R{q} = fushe_kuqe_field_design(xlsx, P);
        fprintf('\n[%s]  (%.1f s)\n', runs{q, 1}, toc(tv));
        fprintf('  monitoring: %s\n', strjoin(cellstr(R{q}.monID), ', '));
        fprintf('  MAR:        %s\n', strjoin(cellstr(R{q}.marID), ', '));
        fprintf('  baseline intruded area = %.1f km^2\n', R{q}.baseArea);
    end

    % ---- A. zone flips between the two rules (same rhoF) -------------------
    z1 = R{1}.zfac; z2 = R{2}.zfac; zK = R{1}.zK;
    flips = find(z1 ~= z2);
    fprintf('\n--- zone-rule comparison (legacy vs harmonized) ---\n');
    fprintf('zones: %d;  flipped: %d\n', numel(z1), numel(flips));
    for f = flips(:)'
        fprintf('  zone %2d: zK = %7.2f m/d   legacy class %d -> harmonized class %d\n', ...
                f, zK(f), z1(f), z2(f));
    end
    fprintf('design IDs identical (legacy vs harmonized, rhoF=0.6)?   mon: %s   MAR: %s\n', ...
            tif(isequal(R{1}.monID, R{2}.monID)), tif(isequal(R{1}.marID, R{2}.marID)));
    fprintf('design IDs identical (rhoF 0.600 vs 0.805, harmonized)?  mon: %s   MAR: %s\n', ...
            tif(isequal(R{2}.monID, R{4}.monID)), tif(isequal(R{2}.marID, R{4}.marID)));
    c12 = corr_safe(R{1}.EIG_c, R{2}.EIG_c);
    c24 = corr_safe(R{2}.EIG_c, R{4}.EIG_c);
    fprintf('EIG-field correlation: legacy-vs-harmonized %.4f;  rho 0.6-vs-0.805 %.4f\n', c12, c24);

    % ---- C. well-level flips ----------------------------------------------
    T = readtable(xlsx, 'Sheet', '2_All_Wells');
    Xa = T{:, 2}; Ya = T{:, 3}; Ka = T{:, 4};
    ok = isfinite(Ka) & isfinite(Xa) & isfinite(Ya);
    X = Xa(ok); Y = Ya(ok); K = Ka(ok);
    facA = 1 * (K >= 150) + 2 * (K >= 75 & K < 150) + 3 * (K < 75);    % gate3 rule
    facB = 1 * (K > 150)  + 2 * (K > 80  & K <= 150) + 3 * (K <= 80);  % legacy-style rule
    wf = find(facA ~= facB);
    fprintf('\n--- well-level classification (43 K-valued wells) ---\n');
    fprintf('counts gate3 rule [coarse med fine] = [%d %d %d]\n', ...
            sum(facA == 1), sum(facA == 2), sum(facA == 3));
    fprintf('wells flipping between rules: %d', numel(wf));
    if ~isempty(wf), fprintf('  (K values: %s)', mat2str(K(wf)')); end
    fprintf('\n');

    % ---- D. class centroids and geometry (Fig. 5 caption check) ------------
    Braw = readmatrix(xlsx, 'Sheet', '3_Boundary_Coords');
    Bpoly = Braw(:, 2:3); Bpoly = Bpoly(all(isfinite(Bpoly), 2), :);
    cx = mean(Bpoly(:, 1)); cy = mean(Bpoly(:, 2));
    fprintf('\n--- geometry (Gauss-Kruger; X = easting, Y = northing) ---\n');
    fprintf('polygon centroid: X = %.0f, Y = %.0f;  X range %.0f..%.0f, Y range %.0f..%.0f\n', ...
            cx, cy, min(Bpoly(:,1)), max(Bpoly(:,1)), min(Bpoly(:,2)), max(Bpoly(:,2)));
    lbl = {'coarse', 'medium', 'fine'};
    for k = 1:3
        s = (facA == k);
        fprintf('  %-6s (n=%2d): centroid X = %.0f (%+.1f km), Y = %.0f (%+.1f km)  -> %s\n', ...
                lbl{k}, sum(s), mean(X(s)), (mean(X(s)) - cx)/1000, ...
                mean(Y(s)), (mean(Y(s)) - cy)/1000, compass8(mean(X(s)) - cx, mean(Y(s)) - cy));
    end
    coastMask = R{1}.coast(R{1}.act);
    ccx = mean(R{1}.Wk(:,1)); %#ok<NASGU>
    coastX = mean(R{1}.xs(R{1}.ai(coastMask))); coastY = mean(R{1}.ys(R{1}.aj(coastMask)));
    domX = mean(R{1}.xs(R{1}.ai)); domY = mean(R{1}.ys(R{1}.aj));
    fprintf('  model coast-cell centroid vs domain centroid: %s (dx=%+.1f km, dy=%+.1f km)\n', ...
            compass8(coastX - domX, coastY - domY), coastX - domX, coastY - domY);

    % ---- save ---------------------------------------------------------------
    out = struct('runs', {runs}, 'monIDs', {cellfun(@(r) cellstr(r.monID), R, 'uni', 0)}, ...
                 'marIDs', {cellfun(@(r) cellstr(r.marID), R, 'uni', 0)}, ...
                 'baseArea', cellfun(@(r) r.baseArea, R), 'zoneFlips', flips, ...
                 'zK', zK, 'wellFlips', numel(wf), 'eigCorr_rule', c12, 'eigCorr_rho', c24);
    save(fullfile(outdir, 'r2_facies_threshold_sensitivity.mat'), '-struct', 'out');
    fprintf('\nsaved: r2_facies_threshold_sensitivity.mat\n');
end

% ------------------------------------------------------------------------
function s = tif(c), if c, s = 'YES'; else, s = 'NO'; end, end

function c = corr_safe(a, b)
    m = isfinite(a) & isfinite(b);
    cc = corrcoef(a(m), b(m)); c = cc(1, 2);
end

function s = compass8(dx, dy)
    ang = atan2d(dy, dx);                       % 0 = East, 90 = North
    dirs = {'E','NE','N','NW','W','SW','S','SE','E'};
    s = dirs{1 + mod(round(ang / 45), 8)};
end
