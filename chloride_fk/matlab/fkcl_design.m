function Des = fkcl_design(m, D, Post, goal, sig, nb)
%FKCL_DESIGN  Goal-oriented design of new chloride samples in existing wells.
%
%   Des = FKCL_DESIGN(m, D, Post, goal) with goal 'sh' (area with upper-layer Cl > 250 mg/L,
%   the primary goal) or 'mid' (the same for the second aquifer). Candidates: the wells inside the
%   polygon and the model sector, each sampled at the upper, middle or base screen. Observation
%   y = log10(Cl) + e, e ~ N(0, sig^2) (default sig = 0.10). Criteria:
%     linear EIG  -1/2 ln(1 - R^2(S)),  R^2(S) = b_S' (C_SS + sig^2 I)^-1 b_S / var(Q)
%                 (ensemble moments; Lemma 1 of the companion study)
%     exact EIG   I(B; Y_S) for the goal discretized in nb equiprobable bins (default 8), by
%                 leave-one-out likelihood reweighting of the posterior ensemble
%   Searches: greedy, pairwise greedy (SINERGO) and the exhaustive best pair and triple among the
%   40 best single samples.

    if nargin < 5 || isempty(sig), sig = 0.10; end
    if nargin < 6 || isempty(nb), nb = 8; end
    [~, uq] = unique(Post.idx, 'first'); uq = sort(uq);
    v = m.valid'; A = m.area / 1e6;
    X = double(Post.(['Cl_' goal])(uq, :));
    q = sum((X > m.C.Cl_lim) & v, 2) * A;
    % candidate wells
    W = D.wells;
    x = (W.X - m.x0) / 1000; y = (W.Y - m.y0) / 1000;
    i = round(x / m.dx) + 1; j = round(y / m.dx) + 1;
    ok = i >= 1 & i <= m.nx & j >= 1 & j <= m.ny;
    wcell = zeros(numel(x), 1); wcell(ok) = m.idx(sub2ind([m.ny m.nx], j(ok), i(ok)));
    good = wcell > 0 & W.inside; good(good) = m.valid(wcell(good));
    wid = W.id(good); wc = wcell(good); nW = numel(wc);
    lay = {'sh', 'mid', 'dp'};
    G = zeros(numel(uq), 3 * nW); lab = cell(1, 3 * nW);
    for d = 1:3
        Y = double(Post.(['Cl_' lay{d}])(uq, wc));
        G(:, (d - 1) * nW + (1:nW)) = log10(Y);
        for k = 1:nW, lab{(d - 1) * nW + k} = [wid{k} ':' lay{d}]; end
    end
    n = numel(q);
    Gc = G - mean(G, 1); qc = q - mean(q);
    Cv = (Gc' * Gc) / (n - 1); b = (Gc' * qc) / (n - 1); vq = (qc' * qc) / (n - 1);
    eigl = @(S) -0.5 * log(max(1 - r2(Cv, b, vq, sig, S), 1e-12));
    single = arrayfun(@(c) eigl(c), 1:size(G, 2));
    [~, ord] = sort(single, 'descend'); top = ord(1:40);
    [~, rk] = sort(q); qb = zeros(n, 1); qb(rk) = 0:n - 1; qb = min(floor(qb * nb / n), nb - 1) + 1;
    exe = @(S) exact_eig(G, qb, S, sig, nb);
    Des.goal = goal; Des.labels = lab; Des.single = single; Des.Q = fkcl_quantile(q, [0.05 0.5 0.95]);
    Des.wells = wid; Des.cells = wc; Des.top = top;
    % exact vs linear for the 40 best single samples and 40 others
    rest = setdiff(1:size(G, 2), top); rng(3); oth = rest(randperm(numel(rest), 40));
    test = [top oth]; ex = arrayfun(@(c) exe(c), test);
    Des.spearman_single = spearman(single(test), ex);
    for k = 1:5
        Sg = greedy(eigl, size(G, 2), k, []);
        if k >= 2, Sp = pairgreedy(eigl, top(1:25), k, size(G, 2)); else, Sp = Sg; end
        Des.k(k).greedy = struct('sites', {lab(Sg)}, 'eig_lin', eigl(Sg), 'eig_exact', exe(Sg));
        Des.k(k).pair = struct('sites', {lab(Sp)}, 'eig_lin', eigl(Sp), 'eig_exact', exe(Sp));
        if k == 2 || k == 3
            cmb = nchoosek(top, k); vals = zeros(size(cmb, 1), 1);
            for r = 1:size(cmb, 1), vals(r) = eigl(cmb(r, :)); end
            [bv, br] = max(vals);
            Des.k(k).exhaustive = struct('sites', {lab(cmb(br, :))}, 'eig_lin', bv, 'eig_exact', exe(cmb(br, :)));
        end
    end
    ref = find(ismember(lab, {'A13:sh', 'A10:sh'}));
    Des.published = struct('sites', {lab(ref)}, 'eig_lin', eigl(ref), 'eig_exact', exe(ref));
    % single-sample EIG field over the sector (upper and middle screens)
    for d = 1:2
        F = log10(double(Post.(['Cl_' lay{d}])(uq, m.valid)));
        Fc = F - mean(F, 1);
        cv = (Fc' * qc) / (n - 1); vg = sum(Fc.^2, 1)' / (n - 1);
        r = cv.^2 ./ (vq * (vg + sig^2));
        fld = nan(m.Nc, 1); fld(m.valid) = -0.5 * log(max(1 - r, 1e-12));
        Des.field.(lay{d}) = fld;
    end
end

function v = r2(Cv, b, vq, sig, S)
    CS = Cv(S, S) + sig^2 * eye(numel(S));
    v = (b(S)' * (CS \ b(S))) / vq;
end

function S = greedy(f, nc, k, S)
    while numel(S) < k
        best = -inf; bc = 0;
        for c = 1:nc
            if any(S == c), continue; end
            val = f([S c]);
            if val > best, best = val; bc = c; end
        end
        S = [S bc]; %#ok<AGROW>
    end
end

function S = pairgreedy(f, pool, k, nc)
    S = [];
    while numel(S) + 2 <= k
        P = setdiff(pool, S, 'stable'); best = -inf; bp = [];
        for a = 1:numel(P)
            for c = a + 1:numel(P)
                val = f([S P(a) P(c)]);
                if val > best, best = val; bp = [P(a) P(c)]; end
            end
        end
        S = [S bp]; %#ok<AGROW>
    end
    if numel(S) < k, S = greedy(f, nc, k, S); end
end

function I = exact_eig(G, qb, S, sig, nb)
% I(B; Y_S) by leave-one-out likelihood reweighting over the ensemble rows of G
    n = size(G, 1); GS = G(:, S);
    pB = accumarray(qb, 1, [nb 1]) / n; HB = -sum(pB(pB > 0) .* log(pB(pB > 0)));
    Y = GS + sig * randn(size(GS));
    Dm = zeros(n);
    for c = 1:size(GS, 2), Dm = Dm + (Y(:, c) - GS(:, c)').^2; end
    Dm = Dm / (2 * sig^2); Dm(1:n + 1:end) = inf;
    Dm = Dm - min(Dm, [], 2);
    Wt = exp(-Dm); Wt = Wt ./ sum(Wt, 2);
    one = full(sparse(1:n, qb, 1, n, nb));
    pb = Wt * one;
    t = pb .* log(max(pb, 1e-300)); t(pb <= 0) = 0;
    I = HB - mean(-sum(t, 2));
end

function r = spearman(a, b)
    ra = tiedrank(a(:)); rb = tiedrank(b(:));
    r = corr1(ra, rb);
end

function r = tiedrank(x)
    [s, o] = sort(x); r = zeros(size(x)); n = numel(x); k = 1;
    while k <= n
        e = k; while e < n && s(e + 1) == s(k), e = e + 1; end
        r(o(k:e)) = 0.5 * (k + e); k = e + 1;
    end
end

function r = corr1(a, b)
    a = a - mean(a); b = b - mean(b); r = (a' * b) / sqrt((a' * a) * (b' * b));
end
