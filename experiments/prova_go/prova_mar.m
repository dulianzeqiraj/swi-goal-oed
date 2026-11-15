function T = prova_mar(qSite, nSites, exclKm)
%PROVA_MAR  The MAR process on the demonstration truth (numbers for figures P5-P7).
%   T = PROVA_MAR(qSite, nSites, exclKm) (defaults 5000 m3/d per well, [3 6]
%   wells, 1 km exclusion around the supply wells) uses the demonstration truth of
%   res/prova_demo.mat (PROVA_DEMO) and
%     - the TRIAL-GO model (selected arm conditioned on all data) and the PEST
%       standard model (A1 on the heads): each chooses its own MAR sites with
%       PRAG-MAR (MAR_SITES: src/prag_mar.m on its own operator and goal predictive,
%       builder spacing rule of 6 km in northing);
%     - head fields (MAR_FIELDS) of the true aquifer and of each model under the
%       current pumping, the planned pumping and the planned pumping + MAR, at the
%       expected future recharge (xi_f = 0); intruded area = cells with h < h_c;
%     - risks P(A or B intruded): true (over xi_f, exact) and predicted (Laplace,
%       MAR_GOAL_PREDICT);
%     - a W-E section through supply well A: sharp-interface (Ghyben-Herzberg)
%       interface depth = (base/h_c) x head = 40 h, capped at the aquifer base, and
%       the toe position (km from the coast) for the three states.
%   Saves res/prova_mar.mat (T, X, MARJ) and returns T.
    if nargin < 1 || isempty(qSite), qSite = 5000; end
    if nargin < 2 || isempty(nSites), nSites = [3 6]; end
    if nargin < 3 || isempty(exclKm), exclKm = 1.0; end
    here = prova_go_setup(); resDir = fullfile(here, 'res');
    L = load(fullfile(resDir, 'prova_setup.mat')); M = L.M; S = L.S;
    P = load(fullfile(resDir, 'prova_demo.mat')); dm = P.demo; tr = dm.tr;
    pt = dm.pol.trial; m = pt.sel; key = [m min(pt.n(m), dm.A.nIter(m))];
    stT = [];
    for q = 1:numel(dm.cache), if isequal(dm.cache(q).key, key), stT = dm.cache(q).st; end, end
    stP = dm.A.snap{1}{end};
    T.seed = tr.seed; T.trialArm = m; T.qSite = qSite; T.exclKm = exclKm;
    lines = {};
    % TRIAL-GO designs with 3 and 6 wells on the true aquifer
    for q = 1:numel(nSites)
        sites = mar_sites(M, S, stT, nSites(q), exclKm);
        F = mar_fields(M, S, tr.u, tr.Rch, sites, qSite, 0);
        [F.riskPlan, F.riskMar] = true_risks(M, S, tr, sites, qSite);
        T.(sprintf('true%d', nSites(q))) = F;
        lines{end + 1} = sprintf('TRIAL-GO model (A%d), %d MAR wells x %.0f m3/d at %s (E,N km: %s): true intruded area current %.2f, planned %.2f, planned+MAR %.2f km^2 (natural %.2f); true risk planned %.4f -> with MAR %.4f; heads at A,B planned %s -> with MAR %s m', ...
            m, numel(sites), qSite, mat2str(sites), mat2str(round([M.X(sites) M.Y(sites)] * 100) / 100), F.areaCur, F.areaPlan, F.areaMar, F.areaNat, F.riskPlan, F.riskMar, ...
            mat2str(F.hSup(2, :), 3), mat2str(F.hSup(3, :), 3)); %#ok<AGROW>
    end
    % P6: PEST standard vs TRIAL-GO, each with its own 3 sites
    nm = {'pest', 'trial'}; sts = {stP, stT};
    for q = 1:2
        st = sts{q}; arm = st.arm; sites = mar_sites(M, S, st, nSites(1), exclKm);
        u = full(arm.B * st.th(1:arm.nK)); Rch = M.R0; if arm.hasR, Rch = M.R0 * exp(st.th(end)); end
        D.sites = sites; D.trueF = mar_fields(M, S, tr.u, tr.Rch, sites, qSite, 0); D.predF = mar_fields(M, S, u, Rch, sites, qSite, 0);
        g = mar_goal_predict(M, S, st, sites, qSite); [~, D.trueRisk] = true_risks(M, S, tr, sites, qSite);
        D.predRisk = g.risk; D.predMu = g.mu'; D.predSd = g.s'; D.trueArea = D.trueF.areaMar; D.predArea = D.predF.areaMar;
        D.trueH = D.trueF.hSup(3, :); D.predRch = Rch; D.arm = arm.id;
        T.(nm{q}) = D;
        lines{end + 1} = sprintf('%s model (%s, recharge %.2e m/d; true %.2e): own %d sites %s; predicted risk with MAR %.4f, true %.4f; intruded area predicted %.2f, true %.2f km^2; heads A,B predicted %s, true %s m', ...
            upper(nm{q}), arm.id, Rch, tr.Rch, numel(sites), mat2str(sites), D.predRisk, D.trueRisk, D.predArea, D.trueArea, mat2str(D.predMu, 3), mat2str(D.trueH, 3)); %#ok<AGROW>
    end
    % P7: W-E section through supply well A, TRIAL-GO 3-well design
    F = T.(sprintf('true%d', nSites(1)));
    j = M.aj(M.cellA); row = find(M.aj == j); [~, o] = sort(M.ai(row)); row = row(o);
    x = (M.X(row) - M.X(row(1)))';
    X.N = M.ys(j); X.x = x; X.xA = M.X(M.cellA) - M.X(row(1)); X.qSite = qSite; X.vh = 1;
    near = F.sites(abs(M.Y(F.sites) - X.N) <= 3.0);
    X.xMar = (M.X(near) - M.X(row(1)))'; X.marN = M.Y(near)';
    st3 = {'cur', 'plan', 'mar'}; ratio = M.P.base / S.hc;
    for q = 1:3
        h = F.(st3{q})(row)'; X.h.(st3{q}) = h; X.zi.(st3{q}) = max(-ratio * h, -M.P.base);
        k = find(h >= S.hc, 1);
        if isempty(k), X.toe.(st3{q}) = NaN; elseif k == 1, X.toe.(st3{q}) = 0;
        else, X.toe.(st3{q}) = x(k - 1) + (S.hc - h(k - 1)) / (h(k) - h(k - 1)) * (x(k) - x(k - 1)); end
        X.inlandIntruded.(st3{q}) = any(h(k:end) < S.hc);
        X.hA.(st3{q}) = F.(st3{q})(M.cellA);
    end
    X.ve = (max(x) + 1.2) / 13.9 * 1000 / ((M.P.base + 3 + 19) / 7.2);   % (m per cm horizontal)/(m per cm vertical)
    lines{end + 1} = sprintf('section N = %.2f km through A (%s, %.2f km from the coast): toe %.2f km (current), %.2f km (planned), %.2f km (planned + MAR); inland intruded patch (cone at A): %d/%d/%d; head at A %.2f/%.2f/%.2f m; MAR wells within 3 km of the section at %s km from the coast; vertical exaggeration about %.0f', ...
        X.N, M.supID{1}, X.xA, X.toe.cur, X.toe.plan, X.toe.mar, X.inlandIntruded.cur, X.inlandIntruded.plan, X.inlandIntruded.mar, ...
        X.hA.cur, X.hA.plan, X.hA.mar, mat2str(X.xMar, 3), X.ve);
    MARJ = struct('seed', T.seed, 'qSite', qSite, 'exclKm', exclKm, 'trialArm', m, 'lines', {lines});
    for q = 1:numel(nSites)
        F = T.(sprintf('true%d', nSites(q)));
        MARJ.(sprintf('trial%dwells', nSites(q))) = struct('sites', F.sites, 'sitesEN', [M.X(F.sites) M.Y(F.sites)], 'areaCur', F.areaCur, ...
            'areaPlan', F.areaPlan, 'areaMar', F.areaMar, 'areaNat', F.areaNat, 'riskPlan', F.riskPlan, 'riskMar', F.riskMar, 'hSup', F.hSup);
    end
    for q = 1:2
        D = T.(nm{q});
        MARJ.(nm{q}) = struct('arm', D.arm, 'sites', D.sites, 'sitesEN', [M.X(D.sites) M.Y(D.sites)], 'predRisk', D.predRisk, 'trueRisk', D.trueRisk, ...
            'predArea', D.predArea, 'trueArea', D.trueArea, 'predMu', D.predMu, 'predSd', D.predSd, 'trueH', D.trueH, 'predRch', D.predRch, 'trueRch', tr.Rch);
    end
    MARJ.section = struct('N', X.N, 'xA', X.xA, 'toeCur', X.toe.cur, 'toePlan', X.toe.plan, 'toeMar', X.toe.mar, 'xMar', X.xMar, ...
        'inlandIntruded', [X.inlandIntruded.cur X.inlandIntruded.plan X.inlandIntruded.mar], 'verticalExaggeration', X.ve);
    for q = 1:numel(lines), fprintf('%s\n', lines{q}); end
    save(fullfile(resDir, 'prova_mar.mat'), 'T', 'X', 'MARJ', '-v7');
end
function [rPlan, rMar] = true_risks(M, S, tr, sites, qSite)
% P(A or B intruded) over xi_f for the true aquifer, without and with MAR (heads affine in xi_f).
    Qm = zeros(M.Nc, 1); Qm(sites) = -qSite; H = fk_solve(M, tr.u, tr.Rch, Qm); s = M.supCell(:);
    hn = H(s, 1); H0 = hn + S.Q(1) * H(s, 2) + S.Q(2) * H(s, 3); H1 = H0 + H(s, 4);
    rPlan = 0.5 * erfc(-(max((S.hc - H0) ./ hn) / S.sigXi) / sqrt(2));
    rMar = 0.5 * erfc(-(max((S.hc - H1) ./ hn) / S.sigXi) / sqrt(2));
end
