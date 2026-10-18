function out = fkcl_prag_mar(opts)
%FKCL_PRAG_MAR  PRAG-MAR recomputed with the geolocated sea boundary.
%
%   out = FKCL_PRAG_MAR() repeats the PRAG-MAR experiment of the companion model
%   (demo/fushe_kuqe_prag_mar.m) with the sea boundary of the chloride study: only the rows north
%   of y = 29.5 km are in contact with the Adriatic, through a link over the GLOBE shoreline gap,
%   and the model covers the coastal sector y >= 24 km. Everything else is the companion model:
%   confined flow with T = K b (b = 30 m), recharge R = 5e-4 m/d, the 12 pilot zones with the
%   facies prior (rho_F = 0.6), and a supply well is intruded when its head falls below
%   h_c = delta * base = 1.0 m. MATLAB port of experiments/prag_go_fushe_kuqe/fk_mar_geo.py.
%
%   With this boundary no well is at risk without pumping, so the rules of the experiment are:
%     supply wells   the sector is split at section A-A' (y = 36.5 km, through the Fushe-Kuqe well
%                    field); in each half, the inside K-well with the lowest prior-mean head that
%                    is not in the published monitoring design (A1 and P10)
%     pumping        opts.mode = 'each' (default): Q_A and Q_B such that each well's own prior
%                    intrusion probability is 1/2; 'equal': one rate at both wells with
%                    P(A or B intruded) = 1/2
%     recharge sites the sector cells at least 1 km from both supply wells; top 3, at least 6 km
%                    apart in northing (the published rule)
%   Designs, compared exactly on 2000 prior realizations at 2500, 5000 and 10000 m3/day per site:
%     published (A18, P21, P16 of the companion design; A18 and P21 lie outside the sector),
%     area (area adjoint, recomputed), prag (PRAG-MAR closed form, src/prag_mar.m) and ens (greedy
%     optimum of the exact ensemble risk).
%
%   Options (struct): mode 'each' | 'equal'; src 'python' (default: the prior draws of the Python
%   run, experiments/prag_go_fushe_kuqe/res_geo/mar_geo_draws.csv, so the numbers coincide) or an
%   integer seed; Q recharge per site [m3/day]; figure true | false; tsvdir (GNU Octave).
%   Run time: about 1 minute in MATLAB.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1, opts = struct(); end
    C = fkcl_config();
    if isfield(opts, 'tsvdir'), C.tsvdir = opts.tsvdir; end
    drawFile = fullfile(C.repo, 'experiments', 'prag_go_fushe_kuqe', 'res_geo', 'mar_geo_draws.csv');
    def = struct('mode', 'each', 'Q', [2500 5000 10000], 'figure', true, 'src', 11);
    if exist(drawFile, 'file'), def.src = 'python'; end
    fn = fieldnames(def);
    for q = 1:numel(fn), if ~isfield(opts, fn{q}), opts.(fn{q}) = def.(fn{q}); end, end
    if exist('prag_mar', 'file') ~= 2, addpath(fullfile(C.repo, 'src')); end

    C.rhoF = 0.6;                                       % base prior of the companion model
    D = fkcl_read_data(C); m = fkcl_model_init(C, D);
    b = 30; R = 5e-4; hc = 1.0; ySplit = 36.5; excl = 1.0; space = 6.0; Qref = 5000; Nz = m.Nz;
    rhs0 = R * m.area * double(m.valid);
    goalA = @(h) sum(m.area ./ (1 + exp(-(hc - h(m.valid)) / 0.15))) / 1e6;

    % ------------------------------------------------ supply wells
    W = D.wells; okK = isfinite(W.X) & isfinite(W.Y) & isfinite(W.K);
    ids = W.id(okK); ins = W.inside(okK); Wk = m.Wk;
    cellOf = @(x, y) m.idx(round(y / m.dx) + 1, round(x / m.dx) + 1);
    A0 = fkcl_fk_operator(m, zeros(Nz, 1), b); h0 = A0 \ rhs0;
    cand = zeros(0, 3);
    for k = 1:numel(ids)
        if ~ins(k) || any(strcmp(ids{k}, {'P21', 'A12', 'A13', 'A21', 'A10'})), continue; end
        c = cellOf(Wk(k, 1), Wk(k, 2));
        if c > 0 && m.valid(c), cand(end + 1, :) = [k c h0(c)]; end %#ok<AGROW>
    end
    yk = Wk(cand(:, 1), 2);
    nI = find(yk >= ySplit); [~, a] = min(cand(nI, 3)); iA = cand(nI(a), :);
    sI = find(yk < ySplit);  [~, a] = min(cand(sI, 3)); iB = cand(sI(a), :);
    cA = iA(2); cB = iB(2); idA = ids{iA(1)}; idB = ids{iB(1)};
    fprintf('sector %d cells, intruded area without pumping %.1f km2\n', nnz(m.valid), goalA(h0));
    fprintf('supply wells: A = %s (%.2f, %.2f) h0 %.2f m;  B = %s (%.2f, %.2f) h0 %.2f m\n', ...
            idA, m.cx(cA), m.cy(cA), h0(cA), idB, m.cx(cB), m.cy(cB), h0(cB));

    % ------------------------------------------------ prior draws
    if ischar(opts.src) && strcmpi(opts.src, 'python')
        T = fkcl_readnum(drawFile); THc = T(T(:, 1) == 0, 2:end); THe = T(T(:, 1) == 1, 2:end);
    else
        rng(opts.src); THc = (m.Lgam * randn(Nz, 2000))'; THe = (m.Lgam * randn(Nz, 2000))';
    end

    % ------------------------------------------------ pumping (calibration ensemble)
    E = full(sparse([cA cB], [1 2], 1, m.Nc, 2));
    Hc = zeros(size(THc, 1), 6);
    for i = 1:size(THc, 1)
        F = factor(fkcl_fk_operator(m, THc(i, :)', b));
        h = F.solve(rhs0); U = F.solve(E);
        Hc(i, :) = [h(cA) h(cB) U(cA, 1) U(cA, 2) U(cB, 1) U(cB, 2)];
    end
    [QA, QB] = calibrate(Hc, hc, opts.mode);
    [ha, hb] = pumped(Hc, QA, QB);
    ddA = mean(QA * Hc(:, 3) + QB * Hc(:, 4)); ddB = mean(QA * Hc(:, 5) + QB * Hc(:, 6));
    fprintf('pumping Q_A %.0f, Q_B %.0f m3/d; mean drawdown A %.2f m, B %.2f m; P(A) %.3f P(B) %.3f P(A or B) %.3f\n', ...
            QA, QB, ddA, ddB, mean(ha < hc), mean(hb < hc), mean(min(ha, hb) < hc));
    rhsP = rhs0; rhsP(cA) = rhsP(cA) - QA; rhsP(cB) = rhsP(cB) - QB;

    % ------------------------------------------------ closed forms at the prior mean (pumped)
    h0p = A0 \ rhsP; S = zeros(2, Nz); dz = 1e-3;
    for z = 1:Nz
        tp = zeros(Nz, 1); tp(z) = dz;
        hp = fkcl_fk_operator(m, tp, b) \ rhsP; hm = fkcl_fk_operator(m, -tp, b) \ rhsP;
        S(:, z) = [hp(cA) - hm(cA); hp(cB) - hm(cB)] / (2 * dz);
    end
    Cm = S * m.Gam * S';
    [RISK, info] = prag_mar(-A0, [cA cB], Cm, h0p([cA cB]), hc);   % src/prag_mar.m: sign of src/
    q = 1 ./ (1 + exp(-(hc - h0p) / 0.15));
    wh = double(m.valid) .* m.area .* (-(q .* (1 - q)) / 0.15) / 1e6;
    MARf = -(A0' \ wh);                                 % intruded-area reduction per unit recharge
    dA = hypot(m.cx - m.cx(cA), m.cy - m.cy(cA)); dB = hypot(m.cx - m.cx(cB), m.cy - m.cy(cB));
    ok = m.valid & dA >= excl & dB >= excl;
    pragC = topk(RISK, ok, m.cy, space); areaC = topk(MARf, ok, m.cy, space);
    pubXY = [12.25 12.75; 11.25 18.75; 6.5 51.0];      % cells of the published MAR sites A18, P21, P16
    pubC = arrayfun(@(k) cellOf(pubXY(k, 1), pubXY(k, 2)), 1:3)';
    fprintf('linear moments (pumped): hA %.3f sd %.3f, hB %.3f sd %.3f, r %.3f\n', h0p(cA), info.s(1), h0p(cB), info.s(2), info.r);

    % ------------------------------------------------ exact: evaluation ensemble
    n = size(THe, 1); HA = zeros(n, 1); HB = zeros(n, 1);
    GA = zeros(n, m.Nc, 'single'); GB = zeros(n, m.Nc, 'single');
    for i = 1:n
        F = factor(fkcl_fk_operator(m, THe(i, :)', b));
        h = F.solve(rhsP); g = F.solveT(E);
        HA(i) = h(cA); HB(i) = h(cB); GA(i, :) = g(:, 1)'; GB(i, :) = g(:, 2)';
    end
    sel = [];
    for step = 1:3
        if isempty(sel), ba = HA; bb = HB; else, ba = HA + Qref * sum(double(GA(:, sel)), 2); bb = HB + Qref * sum(double(GB(:, sel)), 2); end
        val = mean(1 ./ (1 + exp(-(hc - min(ba + Qref * double(GA), bb + Qref * double(GB))) / 0.05)), 1)';
        [~, ord] = sort(val, 'ascend');
        for k = ord'
            if ~ok(k) || any(sel == k), continue; end
            if ~isempty(sel) && any(abs(m.cy(k) - m.cy(sel)) < space), continue; end
            sel(end + 1) = k; break; %#ok<AGROW>
        end
    end
    ensC = sel(:);
    names = {'published', 'area', 'prag', 'ens'}; cellsD = {pubC, areaC, pragC, ensC};
    nQ = numel(opts.Q); Ar = zeros(n, 1 + 4 * nQ);
    for i = 1:n
        F = factor(fkcl_fk_operator(m, THe(i, :)', b)); h = F.solve(rhsP); Ar(i, 1) = goalA(h);
        for d = 1:4
            cs = cellsD{d}(m.valid(cellsD{d})); r = zeros(m.Nc, 1); r(cs) = 1; u = F.solve(r);
            for qq = 1:nQ, Ar(i, 1 + (d - 1) * nQ + qq) = goalA(h + opts.Q(qq) * u); end
        end
    end

    % ------------------------------------------------ results
    out = struct('mode', opts.mode, 'supply', struct('A', idA, 'B', idB, 'cellA', cA, 'cellB', cB), ...
                 'QA', QA, 'QB', QB, 'drawdown', [ddA ddB], 'Q', opts.Q, ...
                 'none', [mean(HA < hc) mean(HB < hc) mean(min(HA, HB) < hc) mean(Ar(:, 1))]);
    fprintf('%-10s P(A or B) %.3f, area %.1f km2\n', 'none', out.none(3), out.none(4));
    for d = 1:4
        cs = cellsD{d}; cv = cs(m.valid(cs)); rows = zeros(nQ, 4);
        for qq = 1:nQ
            Q = opts.Q(qq);
            a = HA + Q * sum(double(GA(:, cv)), 2); bq = HB + Q * sum(double(GB(:, cv)), 2);
            rows(qq, :) = [mean(a < hc) mean(bq < hc) mean(min(a, bq) < hc) mean(Ar(:, 1 + (d - 1) * nQ + qq))];
        end
        lab = cell(1, numel(cs));
        for k = 1:numel(cs)
            [~, w] = min(hypot(Wk(:, 1) - m.cx(cs(k)), Wk(:, 2) - m.cy(cs(k))));
            lab{k} = sprintf('%s(%.1f,%.1f)%s', ids{w}, m.cx(cs(k)), m.cy(cs(k)), repmat('*', 1, ~m.valid(cs(k))));
        end
        out.(names{d}) = struct('cells', cs, 'labels', {lab}, 'rows', rows);
        fprintf('%-10s %-40s', names{d}, strjoin(lab, ', '));
        for qq = 1:nQ, fprintf('  Q %5d: P %.3f area %.1f', opts.Q(qq), rows(qq, 3), rows(qq, 4)); end
        fprintf('\n');
    end
    fprintf('(* outside the sector: no effect)\n');
    ref = fullfile(C.repo, 'experiments', 'prag_go_fushe_kuqe', 'res_geo', ['mar_geo' repmat('_equal', 1, strcmpi(opts.mode, 'equal')) '.json']);
    if ischar(opts.src) && exist(ref, 'file')
        J = jsondecode(fileread(ref));
        dP = abs(out.prag.rows(:, 3) - [J.prag.rows.pAB]');
        fprintf('Python reference: PRAG-MAR P(A or B) %s; max |difference| %.3g\n', sprintf('%.3f ', [J.prag.rows.pAB]), max(dP));
    end
    if opts.figure
        f = draw(m, RISK, MARf, out, cA, cB, opts.Q);
        if ~exist(C.figdir, 'dir'), mkdir(C.figdir); end
        fkcl_save_figure(f, C.figdir, ['figS1_prag_mar_geo' repmat('_equal', 1, strcmpi(opts.mode, 'equal'))]); close(f);
    end
end

% ======================================================================= helpers
function F = factor(A)
% one sparse LU, reused for A x = b and A' x = b (works in MATLAB and GNU Octave)
    [L, U, P, Q] = lu(A);
    F.solve  = @(B) Q * (U \ (L \ (P * B)));
    F.solveT = @(B) P' * (L' \ (U' \ (Q' * B)));
end

function [a, b] = pumped(H, QA, QB)
    a = H(:, 1) - QA * H(:, 3) - QB * H(:, 4); b = H(:, 2) - QA * H(:, 5) - QB * H(:, 6);
end

function [QA, QB] = calibrate(H, hc, mode)
    if strcmpi(mode, 'equal')
        lo = 0; hi = 1e6;
        for it = 1:60
            mid = 0.5 * (lo + hi); [a, b] = pumped(H, mid, mid);
            if mean(min(a, b) < hc) < 0.5, lo = mid; else, hi = mid; end
        end
        QA = 0.5 * (lo + hi); QB = QA; return
    end
    QA = 0; QB = 0;
    for outer = 1:60
        lo = 0; hi = 1e6;
        for it = 1:60
            mid = 0.5 * (lo + hi); a = pumped(H, mid, QB);
            if median(a) > hc, lo = mid; else, hi = mid; end
        end
        QA = 0.5 * (lo + hi);
        lo = 0; hi = 1e6;
        for it = 1:60
            mid = 0.5 * (lo + hi); [~, b] = pumped(H, QA, mid);
            if median(b) > hc, lo = mid; else, hi = mid; end
        end
        QBn = 0.5 * (lo + hi);
        if abs(QBn - QB) < 1e-3, QB = QBn; break; end
        QB = QBn;
    end
end

function sel = topk(vals, ok, cy, space)
% three cells, best first, at least `space` km apart in northing (the published rule)
    v = vals; v(~ok) = -inf; [~, ord] = sort(v, 'descend'); sel = [];
    for k = ord'
        if ~isfinite(v(k)), continue; end
        if ~isempty(sel) && any(abs(cy(k) - cy(sel)) < space), continue; end
        sel(end + 1, 1) = k; %#ok<AGROW>
        if numel(sel) == 3, break; end
    end
end

function f = draw(m, RISK, MARf, out, cA, cB, Q)
    P = [0 114 178; 213 94 0; 0 158 115; 204 121 167; 230 159 0; 86 180 233] / 255;
    f = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 19 8.5], 'Color', 'w');
    set(f, 'PaperUnits', 'centimeters', 'PaperSize', [19 8.5], 'PaperPosition', [0 0 19 8.5]);
    fields = {RISK, MARf}; ttl = {'PRAG-MAR field', 'area-adjoint field'};
    sites = {out.prag.cells, out.area.cells};
    for p = 1:2
        ax = axes(f, 'Position', [0.06 + (p - 1) * 0.28, 0.16, 0.22, 0.75]); hold(ax, 'on');
        G = nan(m.ny + 1, m.nx + 1); v = fields{p}; v(~m.valid) = NaN; v = v / max(v(m.valid));
        G(sub2ind([m.ny + 1, m.nx + 1], m.aj, m.ai)) = v;      % pcolor: NaN cells stay blank in MATLAB and Octave
        xe = [m.xs - m.dx / 2, m.xs(end) + m.dx / 2]; ye = [m.ys - m.dx / 2, m.ys(end) + m.dx / 2];
        hp = pcolor(ax, xe, ye, G); set(hp, 'EdgeColor', 'none'); colormap(ax, fkcl_cmap('ylgnbu')); caxis(ax, [0 1]);
        plot(ax, m.Bk(:, 1), m.Bk(:, 2), '-', 'Color', [0.3 0.3 0.3], 'LineWidth', 0.5);
        plot(ax, m.cx([cA cB]), m.cy([cA cB]), 'kv', 'MarkerFaceColor', P(5, :), 'MarkerSize', 6);
        s = sites{p}; plot(ax, m.cx(s), m.cy(s), 'o', 'MarkerEdgeColor', P(2, :), 'LineWidth', 1.4, 'MarkerSize', 7);
        axis(ax, 'equal'); xlim(ax, [-1 14]); ylim(ax, [23.5 53]); box(ax, 'on'); set(ax, 'XTick', 0:5:10);
        title(ax, ttl{p}, 'FontWeight', 'normal', 'FontSize', 7); xlabel(ax, 'Easting from x_0 [km]');
        if p == 1, ylabel(ax, 'Northing from y_0 [km]'); end
        text(ax, -0.02, 1.02, char('a' + p - 1), 'Units', 'normalized', 'FontWeight', 'bold', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
    end
    ax = axes(f, 'Position', [0.68 0.16 0.29 0.72]); hold(ax, 'on');
    nm = {'published', 'area', 'prag', 'ens'}; lb = {'published sites', 'area adjoint', 'PRAG-MAR', 'exact optimum'}; col = P([4 1 2 3], :);
    h = zeros(1, 4);
    for d = 1:4
        h(d) = plot(ax, [0 Q] / 1000, [out.none(3); out.(nm{d}).rows(:, 3)], '-o', 'Color', col(d, :), 'MarkerFaceColor', col(d, :), 'MarkerSize', 3.5);
    end
    xlabel(ax, 'recharge per site [10^3 m^3/day]'); ylabel(ax, 'P(supply well A or B intruded)'); ylim(ax, [0 0.8]); box(ax, 'off');
    legend(ax, h, lb, 'Location', 'northeast', 'Box', 'off', 'Color', 'none', 'FontSize', 6);
    text(ax, -0.02, 1.02, 'c', 'Units', 'normalized', 'FontWeight', 'bold', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
end
