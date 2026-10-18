function out = fkcl_prag_go(opts)
%FKCL_PRAG_GO  PRAG-GO (threshold-risk monitoring design) with the geolocated sea boundary.
%
%   out = FKCL_PRAG_GO() repeats the PRAG-GO field test of the companion model on the coastal
%   sector with the sea boundary of the chloride study (sea contact only on the northern 23 km,
%   through the GLOBE shoreline gap; sector y >= 24 km). MATLAB port of
%   experiments/prag_go_fushe_kuqe/fk_prag_geo.py; with the exported prior draws (opts.src =
%   'python', the default when res_geo/prag_draws_<prior>.bin exists) the numbers coincide.
%
%   Setting (as FKCL_PRAG_MAR): companion physics (confined, b = 30 m, R = 5e-4 m/d, 12 pilot
%   zones with the facies prior), supply wells A1 and P10 pumped so that each well's own prior
%   intrusion probability is 1/2 (rates read from res_geo/mar_geo.json, or computed by
%   FKCL_PRAG_MAR), intrusion when h < 1.0 m. Goals:
%     rA     supply well A intruded
%     rAB    A or B intruded
%     rArea  intruded area of the sector above its prior median, rounded to 1 km^2
%   Candidates: the 16 other inside K-wells of the sector, read with head noise sd 0.2 m.
%   Every design of opts.budgets wells (default 2, 3 and 5: 120, 560 and 4368 designs) is ranked
%   by eight criteria and scored by its exact EIG (likelihood re-weighting of 12 000 inner and
%   2 000 outer prior realizations):
%     area, areaEns    Lemma 1 EIG of the intruded area (linearized, ensemble moments): the
%                      published pipeline
%     hA, meanAB       Lemma 1 EIG of the head at A and of the mean head at A and B
%     pragLin, pragEns PRAG-GO closed form for rAB (linearized, ensemble moments)
%     pragNSA, pragNS  PRAG-GO for rA and rAB after the normal-score transform
%   Each criterion's best design is reported as a percentage of the exact optimum.
%
%   Options (struct): prior 'base' (rho_F = 0.6) | 'rho805'; budgets (subset of [2 3 5]);
%   src 'python' | integer seed; figure true | false; tsvdir (GNU Octave).
%   Run time in MATLAB: about 2 minutes for 2 and 3 wells; the 4368 five-well designs add about
%   15 minutes. Memory: about 2 GB. Base MATLAB only.
%
%   Author: D. Zeqiraj.  License: MIT (see LICENSE).

    if nargin < 1, opts = struct(); end
    C = fkcl_config();
    if isfield(opts, 'tsvdir'), C.tsvdir = opts.tsvdir; end
    RG = fullfile(C.repo, 'experiments', 'prag_go_fushe_kuqe', 'res_geo');
    userSrc = isfield(opts, 'src');
    def = struct('prior', 'base', 'budgets', [2 3 5], 'figure', true, 'src', 11);
    fn = fieldnames(def);
    for q = 1:numel(fn), if ~isfield(opts, fn{q}), opts.(fn{q}) = def.(fn{q}); end, end
    % without an explicit opts.src, use the exported Python draws when they exist
    if ~userSrc && exist(fullfile(RG, ['prag_draws_' opts.prior '.bin']), 'file'), opts.src = 'python'; end
    C.rhoF = 0.6; if strcmpi(opts.prior, 'rho805'), C.rhoF = 0.805; end
    D = fkcl_read_data(C); m = fkcl_model_init(C, D);
    b = 30; R = 5e-4; hc = 1.0; SN = 0.2; Nz = m.Nz;
    goalA = @(h) sum(m.area ./ (1 + exp(-(hc - h(m.valid)) / 0.15))) / 1e6;

    % ------------------------------------------------ supply wells and pumping (as FKCL_PRAG_MAR)
    js = fullfile(RG, 'mar_geo.json');
    if exist(js, 'file')
        J = jsondecode(fileread(js)); idA = J.supply.A.id; idB = J.supply.B.id; QA = J.pumping.QA; QB = J.pumping.QB;
    else
        o = fkcl_prag_mar(struct('figure', false, 'tsvdir', C.tsvdir));
        idA = o.supply.A; idB = o.supply.B; QA = o.QA; QB = o.QB;
    end
    W = D.wells; okK = isfinite(W.X) & isfinite(W.Y) & isfinite(W.K);
    ids = W.id(okK); ins = W.inside(okK); Wk = m.Wk;
    cellOf = @(k) m.idx(round(Wk(k, 2) / m.dx) + 1, round(Wk(k, 1) / m.dx) + 1);
    kA = find(strcmp(ids, idA), 1); kB = find(strcmp(ids, idB), 1);
    cand = [];
    for k = 1:numel(ids)
        if ~ins(k) || k == kA || k == kB, continue; end
        c = cellOf(k);
        if c > 0 && m.valid(c), cand(end + 1) = k; end %#ok<AGROW>
    end
    NC = numel(cand); IA = NC + 1; IB = NC + 2; IR = NC + 3;
    WC = [arrayfun(cellOf, cand(:)); cellOf(kA); cellOf(kB)];
    cid = ids(cand);
    rhsP = R * m.area * double(m.valid); rhsP(cellOf(kA)) = rhsP(cellOf(kA)) - QA; rhsP(cellOf(kB)) = rhsP(cellOf(kB)) - QB;
    heads = @(theta) headsAt(fkcl_fk_operator(m, theta, b) \ rhsP, WC, goalA);
    fprintf('%s: supply A = %s, B = %s, pumping %.0f / %.0f m3/d; %d candidate wells: %s\n', ...
            opts.prior, idA, idB, QA, QB, NC, strjoin(cid', ' '));

    % ------------------------------------------------ prior draws
    if ischar(opts.src) && strcmpi(opts.src, 'python')
        fid = fopen(fullfile(RG, ['prag_draws_' opts.prior '.bin']), 'r', 'ieee-le');
        THi = fread(fid, [Nz 12000], 'double')'; THo = fread(fid, [Nz 2000], 'double')';
        NSn = fread(fid, [NC 12000], 'double')'; NSe = fread(fid, [NC 2000], 'double')';
        fclose(fid);
    else
        rng(opts.src);
        THi = (m.Lgam * randn(Nz, 12000))'; THo = (m.Lgam * randn(Nz, 2000))';
        NSn = randn(12000, NC); NSe = randn(2000, NC);
    end

    % ------------------------------------------------ ensembles
    t0 = tic;
    inner = zeros(size(THi, 1), NC + 3); outer = zeros(size(THo, 1), NC + 3);
    for i = 1:size(THi, 1), inner(i, :) = heads(THi(i, :)')'; end
    for i = 1:size(THo, 1), outer(i, :) = heads(THo(i, :)')'; end
    fprintf('ensembles %.0f s\n', toc(t0));
    T = round(median(inner(:, IR)));
    gi = inner(:, 1:NC); go = outer(:, 1:NC);
    hAi = inner(:, IA); hBi = inner(:, IB); ari = inner(:, IR);
    QIN = double([hAi < hc, min(hAi, hBi) < hc, ari > T]);
    P0 = mean(QIN, 1);
    fprintf('area threshold %d km2; prior P(rA, rAB, rArea) = %s\n', T, mat2str(round(1000 * P0) / 1000));

    % ------------------------------------------------ moments for the criteria
    S = zeros(NC + 3, Nz); dz = 1e-3;
    for z = 1:Nz
        tp = zeros(Nz, 1); tp(z) = dz;
        S(:, z) = (heads(tp) - heads(-tp)) / (2 * dz);
    end
    M.Alin = S * m.Gam * S'; M.mulin = heads(zeros(Nz, 1));
    M.Aens = cov(inner); M.muens = mean(inner, 1)';
    yno = gi + SN * NSn;
    nsY = zeros(size(inner));
    for k = 1:NC, nsY(:, k) = nscore(yno(:, k), yno(:, k)); end
    nsY(:, IA) = nscore(hAi, hAi); nsY(:, IB) = nscore(hBi, hBi); nsY(:, IR) = nscore(ari, ari);
    M.Ans = cov(nsY); M.muns = mean(nsY, 1)';
    M.tA = nscore(hc, hAi); M.tB = nscore(hc, hBi);
    Q = quadrature(); M.IA = IA; M.IB = IB; M.IR = IR; M.NC = NC; M.s2 = SN^2; M.hc = hc;

    % ------------------------------------------------ exact EIG: distances outer readings - inner heads
    y = go + SN * NSe;
    DK = zeros(size(go, 1), size(gi, 1), NC, 'single');
    for k = 1:NC, DK(:, :, k) = single((y(:, k) - gi(:, k)').^2); end
    QW = single(QIN); H0 = hbin(P0);
    names = {'area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS'};
    goals = {'rA', 'rAB', 'rArea'};
    out = struct('prior', opts.prior, 'supply', struct('A', idA, 'B', idB), 'QA', QA, 'QB', QB, ...
                 'area_threshold_km2', T, 'P0', P0, 'candidates', {cid'});
    for kb = opts.budgets(:)'
        Dd = nchoosek(1:NC, kb); nD = size(Dd, 1);
        LIN = zeros(nD, 8); EX = NaN(nD, 4);
        for r = 1:nD
            LIN(r, :) = criteria(M, Q, Dd(r, :));
            EX(r, :) = exact(DK, Dd(r, :), SN, QW, H0, false);
        end
        for gk = 1:3                        % effective sample size of each optimum
            [~, ib] = max(EX(:, gk)); e = exact(DK, Dd(ib, :), SN, QW, H0, true); EX(ib, 4) = e(4);
        end
        fprintf('%d-well designs (%d): criteria and exact EIG %.0f s\n', kb, nD, toc(t0));
        B = struct('n_designs', nD, 'designs', Dd, 'LIN', LIN, 'EX', EX);
        for gk = 1:3
            ex = EX(:, gk); [eb, ib] = max(ex);
            G = struct('optimum', struct('wells', {cid(Dd(ib, :))'}, 'eig', eb, 'ess', EX(ib, 4)));
            line = sprintf('  [%d] %s: optimum %s %.3f nats (H0 %.3f);', kb, goals{gk}, strjoin(cid(Dd(ib, :))', ' '), eb, H0(gk));
            for j = 1:8
                [~, i] = max(LIN(:, j));
                G.criteria.(names{j}) = struct('wells', {cid(Dd(i, :))'}, 'eig', ex(i), 'pct_opt', 100 * ex(i) / eb, ...
                                               'spearman', spearman(LIN(:, j), ex));
                line = [line sprintf(' %s %.0f%%', names{j}, 100 * ex(i) / eb)]; %#ok<AGROW>
            end
            if kb == 2
                pub = sort([find(strcmp(cid, 'A10')) find(strcmp(cid, 'A13'))]);
                ip = find(all(Dd == pub, 2));
                G.published_in_sector = struct('wells', {{'A10', 'A13'}}, 'eig', ex(ip), 'pct_opt', 100 * ex(ip) / eb);
                line = [line sprintf('; published pair %.0f%%', 100 * ex(ip) / eb)]; %#ok<AGROW>
            end
            B.goals.(goals{gk}) = G;
            fprintf('%s\n', line);
        end
        out.(sprintf('k%d', kb)) = B;
    end
    % ------------------------------------------------ comparison with the Python reference
    ref = fullfile(RG, ['prag_' opts.prior '.json']);
    if ischar(opts.src) && exist(ref, 'file')
        Jr = jsondecode(fileread(ref)); dmax = 0;
        for kb = opts.budgets(:)'
            for gk = 1:3
                Gp = Jr.budgets.(sprintf('x%d', kb)).goals.(goals{gk}); Gm = out.(sprintf('k%d', kb)).goals.(goals{gk});
                dmax = max(dmax, abs(Gp.optimum.eig - Gm.optimum.eig));
                for j = 1:8, dmax = max(dmax, abs(Gp.criteria.(names{j}).pct_opt - Gm.criteria.(names{j}).pct_opt) / 100); end
            end
        end
        fprintf('Python reference (%s): max |difference| of optimum EIG and of the percentages/100: %.2g\n', ref, dmax);
    end
    if opts.figure && isfield(out, 'k3')
        % five-well marks: the 48 000-realization re-check of fk_prag_geo_check.py when present
        c5 = fullfile(RG, ['prag_' opts.prior '_check5.json']); C5 = [];
        if exist(c5, 'file'), C5 = jsondecode(fileread(c5)); end
        f = draw(m, D, out, cid, ids, Wk, kA, kB, names, C5);
        if ~exist(C.figdir, 'dir'), mkdir(C.figdir); end
        fkcl_save_figure(f, C.figdir, ['figS2_prag_go_geo' repmat('_rho805', 1, strcmpi(opts.prior, 'rho805'))]); close(f);
    end
end

% ======================================================================= helpers
function y = headsAt(h, WC, goalA)
    y = [h(WC); goalA(h)];
end

function v = hbin(p)
% binary entropy [nats]
    p = min(max(p, 0), 1); v = zeros(size(p));
    k = p > 0 & p < 1; v(k) = -(p(k) .* log(p(k)) + (1 - p(k)) .* log(1 - p(k)));
end

function z = nscore(v, ref)
% normal scores: Phi^-1(#{ref <= v} / (n + 1)), clipped to [1e-6, 1 - 1e-6]
    s = sort(ref(:)); v = v(:); n = numel(s); mv = numel(v);
    [~, ord] = sortrows([[s; v], [zeros(n, 1); ones(mv, 1)]]);
    isv = ord > n; pos = find(isv); r = zeros(mv, 1);
    r(ord(isv) - n) = pos - (1:mv)';
    p = min(max(r / (n + 1), 1e-6), 1 - 1e-6);
    z = -sqrt(2) * erfcinv(2 * p);
end

function Q = quadrature()
% Gauss-Hermite (probabilists', 24 nodes, normalized weights) and Gauss-Legendre (64 nodes)
    n = 24; J = diag(sqrt(1:n - 1), 1) + diag(sqrt(1:n - 1), -1);
    [V, Dg] = eig(J); [Q.hx, o] = sort(diag(Dg)); Q.hw = V(1, o)'.^2; Q.hw = Q.hw / sum(Q.hw);
    [U1, U2] = ndgrid(Q.hx, Q.hx); Q.UU = [U1(:)'; U2(:)']; Q.W2 = reshape(Q.hw * Q.hw', 1, []);
    n = 64; k = 1:n - 1; bk = k ./ sqrt(4 * k.^2 - 1);
    [V, Dg] = eig(diag(bk, 1) + diag(bk, -1)); [Q.gx, o] = sort(diag(Dg)); Q.gw = 2 * V(1, o)'.^2;
end

function v = Phi(x), v = 0.5 * erfc(-x / sqrt(2)); end
function v = phi(x), v = exp(-0.5 * x.^2) / sqrt(2 * pi); end

function P = Phi2(a, b, r, Q)
% P(X < a, Y < b) for a standard bivariate normal with correlation r (Gauss-Legendre in x)
    a = a(:); b = b(:); lo = -9; hi = max(a, lo + 1e-9);
    t = 0.5 * (hi - lo) * Q.gx' + 0.5 * (hi + lo);
    f = phi(t) .* Phi((b - r * t) / sqrt(1 - r^2));
    P = 0.5 * (hi - lo) .* (f * Q.gw);
end

function e = lin_eig(A, d, g, s2)
    Sy = A(d, d) + s2 * eye(numel(d));
    if isscalar(g), cg = A(g, d); vg = A(g, g); else, cg = g' * A(:, d); vg = g' * A * g; end
    R2 = cg * (Sy \ cg') / vg;
    e = -0.5 * log(1 - min(R2, 1 - 1e-12));
end

function e = prag(A, mu, d, s2, tA, tB, two, M, Q)
    Sy = A(d, d) + s2 * eye(numel(d));
    Cz = A([M.IA M.IB], d);
    K = Cz * (Sy \ Cz'); Sz = A([M.IA M.IB], [M.IA M.IB]); P = Sz - K;
    if ~two
        R2 = min(K(1, 1) / Sz(1, 1), 1 - 1e-12); t = (tA - mu(M.IA)) / sqrt(Sz(1, 1));
        p = Phi((t - sqrt(R2) * Q.hx) / sqrt(1 - R2));
        e = hbin(Phi(t)) - sum(Q.hw .* hbin(p));
        return
    end
    K = 0.5 * (K + K'); [V, Dg] = eig(K); Lk = V * diag(sqrt(max(diag(Dg), 0))); mm = Lk * Q.UU;
    s = sqrt(max(diag(P), 1e-12)); r = min(max(P(1, 2) / (s(1) * s(2)), -0.999), 0.999);
    p = 1 - Phi2((mu(M.IA) + mm(1, :) - tA) / s(1), (mu(M.IB) + mm(2, :) - tB) / s(2), r, Q);
    r0 = Sz(1, 2) / sqrt(Sz(1, 1) * Sz(2, 2));
    p0 = 1 - Phi2((mu(M.IA) - tA) / sqrt(Sz(1, 1)), (mu(M.IB) - tB) / sqrt(Sz(2, 2)), r0, Q);
    e = hbin(p0) - Q.W2 * hbin(p);
end

function c = criteria(M, Q, d)
    g = zeros(M.NC + 3, 1); g(M.IA) = 0.5; g(M.IB) = 0.5;
    c = [lin_eig(M.Alin, d, M.IR, M.s2), lin_eig(M.Aens, d, M.IR, M.s2), lin_eig(M.Alin, d, M.IA, M.s2), ...
         lin_eig(M.Alin, d, g, M.s2), prag(M.Alin, M.mulin, d, M.s2, M.hc, M.hc, true, M, Q), ...
         prag(M.Aens, M.muens, d, M.s2, M.hc, M.hc, true, M, Q), prag(M.Ans, M.muns, d, 0, M.tA, M.tB, false, M, Q), ...
         prag(M.Ans, M.muns, d, 0, M.tA, M.tB, true, M, Q)];
end

function e = exact(DK, d, SN, QW, H0, wantEss)
% exact EIG of the three goals by likelihood re-weighting; with wantEss also the mean effective
% sample size (otherwise NaN). Same operations, in the same order and precision, as fk_prag_geo.py.
    if isscalar(d), S = DK(:, :, d); else, S = DK(:, :, d(1)) + DK(:, :, d(2)); end
    for k = d(3:end), S = S + DK(:, :, k); end
    S = S - min(S, [], 2);
    S = S * single(-1 / (2 * SN * SN));
    S = max(S, single(-80));
    w = exp(S);
    sw = sum(w, 2, 'double'); p = double(w * QW) ./ sw;
    ess = NaN;
    if wantEss, ess = mean(sw.^2 ./ double(sum(w .* w, 2))); end
    e = [H0 - mean(hbin(p), 1), ess];
end

function r = spearman(a, b)
    ra = tiedrank_(a(:)); rb = tiedrank_(b(:));
    ra = ra - mean(ra); rb = rb - mean(rb); r = (ra' * rb) / sqrt((ra' * ra) * (rb' * rb));
end

function r = tiedrank_(x)
    [s, o] = sort(x); r = zeros(size(x)); n = numel(x); k = 1;
    while k <= n
        e = k; while e < n && s(e + 1) == s(k), e = e + 1; end
        r(o(k:e)) = 0.5 * (k + e); k = e + 1;
    end
end

function f = draw(m, D, out, cid, ids, Wk, kA, kB, names, C5)
    P = [0 114 178; 213 94 0; 0 158 115; 204 121 167; 230 159 0; 86 180 233] / 255;
    f = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 19 9.5], 'Color', 'w');
    set(f, 'PaperUnits', 'centimeters', 'PaperSize', [19 9.5], 'PaperPosition', [0 0 19 9.5]);
    set(f, 'DefaultAxesFontSize', 7, 'DefaultTextFontSize', 7, 'DefaultAxesLineWidth', 0.6);
    xy = @(w) Wk(find(strcmp(ids, w), 1), 1:2);
    % (a) map
    ax = axes(f, 'Position', [0.05 0.14 0.22 0.78]); hold(ax, 'on');
    plot(ax, m.Bk(:, 1), m.Bk(:, 2), '-', 'Color', [0.3 0.3 0.3], 'LineWidth', 0.5);
    sc = m.sea_idx; [ys, o] = sort(m.cy(sc)); plot(ax, m.cx(sc(o)) - m.dx / 2, ys, '-', 'Color', P(2, :), 'LineWidth', 1.6);
    for k = 1:numel(cid), p = xy(cid{k}); plot(ax, p(1), p(2), 'o', 'MarkerSize', 3, 'MarkerFaceColor', [0.45 0.45 0.45], 'MarkerEdgeColor', 'none'); end
    plot(ax, Wk([kA kB], 1), Wk([kA kB], 2), 'kv', 'MarkerFaceColor', P(5, :), 'MarkerSize', 6);
    G = out.k3.goals.rAB;
    for k = 1:3
        p = xy(G.criteria.pragLin.wells{k}); plot(ax, p(1), p(2), 'o', 'MarkerSize', 9, 'MarkerEdgeColor', P(2, :), 'LineWidth', 1.4);
        p = xy(G.criteria.area.wells{k}); plot(ax, p(1), p(2), 's', 'MarkerSize', 10, 'MarkerEdgeColor', P(1, :), 'LineWidth', 1.1);
    end
    for w = {'A10', 'A13'}, p = xy(w{1}); plot(ax, p(1), p(2), 'd', 'MarkerFaceColor', P(4, :), 'MarkerEdgeColor', 'k', 'MarkerSize', 5); end
    for w = unique([G.criteria.pragLin.wells(:); G.criteria.area.wells(:); {'A13'}])'
        p = xy(w{1}); text(ax, p(1) + 0.5, p(2) + 0.25, w{1}, 'FontSize', 6);
    end
    axis(ax, 'equal'); xlim(ax, [-2.5 14]); ylim(ax, [23.5 53.5]); box(ax, 'on');
    xlabel(ax, 'Easting from x_0 [km]'); ylabel(ax, 'Northing from y_0 [km]');
    text(ax, -0.02, 1.02, 'a', 'Units', 'normalized', 'FontWeight', 'bold', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
    % (b) percent of the optimum
    ax = axes(f, 'Position', [0.36 0.2 0.3 0.72]); hold(ax, 'on');
    crit = {'area', 'hA', 'meanAB', 'pragLin', 'pragNS'}; col = P([1 6 3 2 4], :); goals = {'rA', 'rAB', 'rArea'}; wb = 0.15;
    hb = zeros(1, 5); h5 = [];
    for j = 1:5
        for g = 1:3
            xx = g + (j - 3) * wb;
            v3 = out.k3.goals.(goals{g}).criteria.(crit{j}).pct_opt;
            hb(j) = patch(ax, xx + [-1 1 1 -1] * wb * 0.46, [0 0 v3 v3], col(j, :), 'EdgeColor', 'none');
            v5 = [];
            if ~isempty(C5), v5 = C5.goals.(goals{g}).criteria.(crit{j}).pct_best;
            elseif isfield(out, 'k5'), v5 = out.k5.goals.(goals{g}).criteria.(crit{j}).pct_opt; end
            if ~isempty(v5), h5 = plot(ax, xx + [-1 1] * wb * 0.46, [v5 v5], 'k-', 'LineWidth', 1.2); end
        end
    end
    set(ax, 'XTick', 1:3, 'XTickLabel', {'A intruded', 'A or B', sprintf('area > %d km^2', out.area_threshold_km2)}); xlim(ax, [0.5 3.5]); ylim(ax, [0 118]);
    ylabel(ax, 'exact EIG of the chosen design [% of optimum]');
    labs = {'area (published)', 'head at A', 'mean head A, B', 'PRAG-GO', 'PRAG-GO, normal scores'};
    if ~isempty(h5), hb = [hb h5]; labs{end + 1} = '5 wells'; end
    legend(ax, hb, labs, 'Location', 'southoutside', ...
           'NumColumns', 3, 'FontSize', 5.6, 'Box', 'off', 'Color', 'none');
    text(ax, -0.02, 1.02, 'b', 'Units', 'normalized', 'FontWeight', 'bold', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
    % (c) criterion against the exact EIG, three wells, goal rAB
    ax = axes(f, 'Position', [0.75 0.2 0.22 0.72]); hold(ax, 'on');
    LIN = out.k3.LIN; ex = out.k3.EX(:, 2);
    ja = find(strcmp(names, 'area')); jp = find(strcmp(names, 'pragLin'));
    h1 = plot(ax, LIN(:, ja) / max(LIN(:, ja)), ex, 'o', 'MarkerSize', 2, 'MarkerFaceColor', P(1, :), 'MarkerEdgeColor', 'none');
    h2 = plot(ax, LIN(:, jp) / max(LIN(:, jp)), ex, 'o', 'MarkerSize', 2, 'MarkerFaceColor', P(2, :), 'MarkerEdgeColor', 'none');
    xlabel(ax, 'criterion / max'); ylabel(ax, 'exact EIG, A or B intruded [nats]');
    legend(ax, [h1 h2], {sprintf('area (\\rho_s = %.2f)', out.k3.goals.rAB.criteria.area.spearman), ...
           sprintf('PRAG-GO (\\rho_s = %.2f)', out.k3.goals.rAB.criteria.pragLin.spearman)}, 'Location', 'northwest', 'FontSize', 5.8, 'Box', 'off', 'Color', 'none');
    text(ax, -0.02, 1.02, 'c', 'Units', 'normalized', 'FontWeight', 'bold', 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
end
