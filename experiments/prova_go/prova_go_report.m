function out = prova_go_report(resDir, tTotal)
%PROVA_GO_REPORT  Metrics, paired differences, log file and JSON of a PROVA-GO run.
%   out = PROVA_GO_REPORT(resDir, tTotal) reads res/prova_setup.mat,
%   res/prova_main.mat, res/prova_nozeta.mat (if present) and res/prova_mar.mat
%   (if present) and writes res/prova_go_log.txt and res/prova_go_results.json.
    if nargin < 2, tTotal = NaN; end
    L = load(fullfile(resDir, 'prova_setup.mat')); M = L.M; S = L.S;
    methods = {'trial', 'pest_std', 'pest_rch', 'pest_all', 'bic', 'ucb', 'ts', 'greedy', 'oracle', 'trial_k02', 'trial_k08'};
    labels = {'TRIAL-GO (k=0.5)', 'PEST standard (A1, heads)', 'PEST + recharge (A4, heads)', 'PEST all data (A4)', ...
              'all arms + BIC, then all data', 'bandit UCB', 'bandit Thompson', 'bandit greedy', 'oracle arm (hindsight)', ...
              'TRIAL-GO k=0.2', 'TRIAL-GO k=0.8'};
    lg = fopen(fullfile(resDir, 'prova_go_log.txt'), 'w');
    if exist('OCTAVE_VERSION', 'builtin'), prog = ['GNU Octave ' version()]; else, prog = ['MATLAB ' version()]; end
    say(lg, 'PROVA-GO / TRIAL-GO on the Fushe-Kuqe model -- %s, %s\n', prog, datestr(now, 31));
    say(lg, '\n== Model (src/fushe_kuqe_field_design.m, unchanged)\n');
    say(lg, 'grid %d x %d (ny x nx), dx = %.2f km, active cells Nc = %d, coastal cells %d, pilot zones Nz = %d\n', ...
        M.ny, M.nx, M.dx, M.Nc, numel(M.cst), M.Nz);
    say(lg, 'facies class of the zones (zfac): %s (class 3 absent with the legacy rule)\n', mat2str(M.zfac'));
    say(lg, 'wells with K used by the builder: %d; wells in the list: %d, with an active cell: %d\n', numel(M.wellIDK), numel(M.allID), nnz(M.allCell > 0));
    say(lg, 'builder outputs: monitoring %s; MAR %s; baseline intruded area %.1f km^2\n', strjoin(M.monID, ','), strjoin(M.marID, ','), M.baseArea);
    say(lg, 'supply wells: A = %s (E %.2f, N %.2f km, %.2f km from the coast, baseline head %.2f m), B = %s (E %.2f, N %.2f, %.2f km, %.2f m)\n', ...
        M.supID{1}, M.X(M.cellA), M.Y(M.cellA), M.dcoast(M.cellA), M.h0(M.cellA), M.supID{2}, M.X(M.cellB), M.Y(M.cellB), M.dcoast(M.cellB), M.h0(M.cellB));
    say(lg, '  (demo supply wells %s have baseline heads %s m < h_c = %.1f m: no extraction can give P(intruded) ~ 1/2)\n', ...
        strjoin(M.demoSup, ','), mat2str(M.h0(M.demoSupCell)', 3), S.hc);
    say(lg, 'observation wells (J = %d): %s\n', M.J, strjoin(M.obsID, ' '));
    say(lg, 'coastal strip: %d cells within %.1f km of the coast\n', nnz(M.strip), M.stripKm);
    D = L.D;
    say(lg, '\n== Pumping design (prior, %d draws)\n', D.nPrior);
    say(lg, 'planned Q_A = %.0f, Q_B = %.0f m3/d; current Q_A0 = %.0f, Q_B0 = %.0f m3/d (= %.1f x planned)\n', D.Q, D.Q0, S.q0frac);
    say(lg, 'prior P(intruded): planned A %.3f, B %.3f, A or B %.3f; current A %.3f, B %.3f, A or B %.3f\n', D.pA, D.pB, D.pAB, D.pA0, D.pB0, D.pAB0);
    say(lg, 'prior median heads at A, B: natural %s, current %s, planned %s m\n', mat2str(D.medNat, 3), mat2str(D.medCur, 3), mat2str(D.medFut, 3));
    C = L.checks;
    say(lg, '\n== Checks\n');
    say(lg, 'assembly vs R.operator(theta), 5 random zonal theta: max|dA| = %.3g, max|drhs| = %.3g, bitwise identical = %d; FK_SOLVE vs A\\rhs: max rel diff %.2e\n', ...
        C.assembly_maxAbsDiffA, C.assembly_maxAbsDiffRhs, C.assembly_identical, C.solve_maxRelDiff);
    say(lg, 'sign of pumping: head at A %.4f m without pumping, %.4f m with %.0f m3/d extracted (+Q in rhs) -> lowered: %d; FK_SOLVE match %.1e\n', ...
        C.sign_hA_noPump, C.sign_hA_pumped, S.Q(1), C.sign_ok, C.sign_fksolve_match);
    say(lg, 'reciprocity: max rel |g_A(j) - g_j(A)| over the %d observation wells = %.2e\n', M.J, C.recip_maxRelDiff);
    say(lg, 'flux-scale invariance (all K and recharge x c = %.2f): natural heads max|dh| = %.2e m (max head %.2f m);\n', C.scale_c, C.scale_naturalHeads_maxAbsDiff, C.scale_naturalHeads_maxHead);
    say(lg, '  metered Stage-0 responses ratio scaled/original: min %.6f max %.6f (1/c = %.6f); self response at A ratio %.6f\n', C.scale_responseRatio_minmax, 1 / C.scale_c, C.scale_selfResponse_ratio);
    say(lg, '  heads under the current metered pumping change only through the pumping term: max|dh| %.3f m, rms %.3f m (pumping term max %.3f m)\n', ...
        C.scale_curHeads_maxAbsDiff, C.scale_curHeads_rmsDiff, C.scale_curHeads_pumpTerm_maxAbs);
    fi = fullfile(resDir, 'prova_index_check.mat'); I = []; if exist(fi, 'file'), Z = load(fi); I = Z.I; end
    if ~isempty(I)
    say(lg, '\n== Robust Gittins index (Appendix D), H = %d; gamma - p\n', S.Hor);
    for a = 1:numel(I.k)
        for b = 1:numel(I.beta)
            if any(isnan(I.gamMinusP(a, b, :, 2))), continue; end
            for c = 1:3
                say(lg, '  k = %.1f beta = %.2f, p = %.1f: n = %s -> %s\n', I.k(a), I.beta(b), I.p(c), mat2str(I.n), mat2str(squeeze(I.gamMinusP(a, b, :, c))', 3));
            end
        end
    end
    end
    say(lg, 'main table: k = %.1f, beta = %.2f, H = %d, p grid 101, n = 1..80, gamma grid 401\n', S.k, S.beta, S.Hor);
    say(lg, '\n== Budget and LM\nA4 heads-calibration cost on 10 pilot truths: %s runs -> budget = %.1f x median = %d runs\n', mat2str(S.costA4pilot), S.budgetFactor, S.budget);
    J = struct('settings', struct('sigH', S.sigH, 'sigV', S.sigV, 'sigXi', S.sigXi, 'sigR', S.sigR, 'zetaSd', S.zetaSd, ...
        'zetaCorrLengthKm', S.zetaL, 'stripLog', S.stripLog, 'stripKm', M.stripKm, 'hc', S.hc, 'Q', S.Q, 'Q0', S.Q0, ...
        'budget', S.budget, 'costA4pilot', S.costA4pilot, 'k', S.k, 'beta', S.beta, 'H', S.Hor, 'kSens', S.kSens, ...
        'fdStep', S.fdStep, 'tolRel', S.tolRel, 'maxIt', S.maxIt, 'minItems', S.minItems, 'J', M.J, 'nItems', 2 * M.J, ...
        'supplyIDs', {M.supID}, 'obsIDs', {M.obsID}, 'Nc', M.Nc, 'grid', [M.ny M.nx], 'Nz', M.Nz, 'dx', M.dx), ...
        'pumpingDesign', D, 'checks', C, 'indexCheck', I);
    tags = {'main', 'nozeta'}; fb = dir(fullfile(resDir, 'prova_budget*.mat'));
    for q = 1:numel(fb), [~, nmq] = fileparts(fb(q).name); tags{end + 1} = nmq(7:end); end %#ok<AGROW>
    for t = 1:numel(tags)
        f = fullfile(resDir, ['prova_' tags{t} '.mat']); if ~exist(f, 'file'), continue; end
        P = load(f); R = prova_metrics(P.res, methods);
        if t == 1, say(lg, '\n== MAIN RUN: %d truths (%d with the coastal strip), sub-zonal field sd %.2f\n', R.n, R.nStrip, S.zetaSd);
        elseif t == 2, say(lg, '\n== SUPPLEMENTARY RUN without the sub-zonal field (zeta = 0), same seeds: %d truths\n', R.n);
        else, say(lg, '\n== SUPPLEMENTARY EQUAL-COST RUN: bandit budget %s runs (about the mean cost of all arms + BIC), same seeds: %d truths\n', tags{t}(7:end), R.n); end
        say(lg, 'true risk P(A or B intruded): mean %.3f; fraction of truths truly safe (risk < 0.1): %.3f\n', R.riskTrue(1), R.fracTrueSafe);
        say(lg, 'validation miss rate of each arm at convergence on the heads (nominal 0.10): all %s, strip %s, no strip %s\n', ...
            mat2str(R.missConv.all, 3), mat2str(R.missConv.strip, 3), mat2str(R.missConv.nostrip, 3));
        say(lg, 'mean LM iterations to convergence %s, mean runs %s\n', mat2str(R.nIterConv, 3), mat2str(R.costConv, 4));
        say(lg, '%-31s %-19s %-19s %-7s %-7s %-7s %-7s %-6s %-19s %-7s %s\n', 'method', 'cov A [95% CI]', 'cov B [95% CI]', 'width', 'MAE', 'CRPS', 'logS*', 'riskE', 'dec.err [95% CI]', 'runs', 'arm freq A1..A5');
        for q = 1:numel(methods)
            m = R.m.(methods{q});
            say(lg, '%-31s %.3f [%.3f %.3f] %.3f [%.3f %.3f] %.3f   %.3f   %.3f   %6.2f  %.3f  %.3f [%.3f %.3f] %6.1f  %s\n', labels{q}, ...
                m.covA, m.covB, mean([m.widthA(1) m.widthB(1)]), mean([m.maeA(1) m.maeB(1)]), mean([m.crpsA(1) m.crpsB(1)]), ...
                m.logScoreMedian, m.riskAbsErr(1), m.decErr, m.runs(1), mat2str(m.armFreq));
        end
        say(lg, '(width, MAE, CRPS: mean over A and B, m; logS*: median joint negative log density of (H_A, H_B); riskE: mean |predicted - true risk|)\n');
        say(lg, 'coverage by truth type (A, B): strip / no strip\n');
        for q = 1:numel(methods)
            m = R.m.(methods{q});
            say(lg, '  %-31s strip %.3f %.3f   no strip %.3f %.3f\n', labels{q}, m.covA_strip(1), m.covB_strip(1), m.covA_nostrip(1), m.covB_nostrip(1));
        end
        say(lg, 'paired differences TRIAL-GO minus comparator, mean [95%% CI] over truths:\n');
        say(lg, '  %-31s %-24s %-24s %-24s %-24s %-24s\n', 'comparator', 'coverage (A,B avg)', 'CRPS', '|risk err|', 'decision err', 'runs');
        for q = 2:numel(methods)
            d = R.paired.(methods{q});
            say(lg, '  %-31s %+.3f [%+.3f %+.3f]  %+.3f [%+.3f %+.3f]  %+.3f [%+.3f %+.3f]  %+.3f [%+.3f %+.3f]  %+6.1f [%+.1f %+.1f]\n', labels{q}, ...
                d.coverage, d.crps, d.riskAbsErr, d.decErr, d.runs);
        end
        pn = fieldnames(R.pol);
        say(lg, 'bandit policies: mean items per arm, mean runs (bandit + conditioning), selection frequency A1..A5 (strip / no strip)\n');
        for q = 1:numel(pn)
            p = R.pol.(pn{q});
            say(lg, '  %-10s items %s runs %.1f + %.1f  sel %s (strip %s, no strip %s)\n', pn{q}, mat2str(p.meanItems, 3), p.meanBanditRuns, p.meanCondRuns, ...
                mat2str(p.selFreq), mat2str(p.selFreqStrip), mat2str(p.selFreqNoStrip));
        end
        say(lg, 'runtime of the truth runs: %.0f s CPU (sum over workers)\n', P.tRun);
        R.tRunCPU = P.tRun; R.methodLabels = labels; R.methods = methods;
        J.(tags{t}) = R;
        fd = fullfile(resDir, 'prova_demo.mat');
        if t == 1 && exist(fd, 'file')
            Z = load(fd); dm = Z.demo; tr = dm.tr; say(lg, '\n== Demonstration truth: seed %d (strip %d, xi_R = %+.3f, xi_f = %+.3f)\n', tr.seed, tr.hasStrip, tr.xiR, tr.xif);
            say(lg, 'true future heads A, B: %.3f %.3f m (xi_f = 0: %.3f %.3f); true risk %.4f\n', tr.Hfut, tr.Hfut0, tr.riskTrue);
            dd = struct('seed', tr.seed, 'hasStrip', tr.hasStrip, 'xiR', tr.xiR, 'xif', tr.xif, 'Hfut', tr.Hfut', 'riskTrue', tr.riskTrue);
            for q = 1:numel(methods)
                x = dm.meth.(methods{q});
                say(lg, '  %-31s arm A%d runs %4d: A %.3f [%.3f %.3f]  B %.3f [%.3f %.3f]  risk %.4f\n', labels{q}, x.arm, x.runs, ...
                    x.mu(1), x.mu(1) - S.z90 * x.s(1), x.mu(1) + S.z90 * x.s(1), x.mu(2), x.mu(2) - S.z90 * x.s(2), x.mu(2) + S.z90 * x.s(2), x.risk);
                dd.(methods{q}) = x;
            end
            pt = dm.pol.trial; say(lg, '  TRIAL-GO plays per arm %s, misses %s, bandit runs %d + conditioning %d\n', mat2str(pt.n), mat2str(pt.s), pt.runs, pt.condRuns);
            say(lg, '  validation miss rate at convergence (heads only) %s\n', mat2str(dm.missConv, 3));
            dd.trialPlays = pt.n; dd.trialMisses = pt.s; dd.missConv = dm.missConv;
            J.demo = dd;
        end
    end
    fm = fullfile(resDir, 'prova_mar.mat');
    if exist(fm, 'file')
        Q = load(fm); J.mar = Q.MARJ;
        say(lg, '\n== MAR scenario on the demonstration truth (sharp-interface reading: toe = h_c contour)\n');
        for q = 1:numel(Q.MARJ.lines), say(lg, '%s\n', Q.MARJ.lines{q}); end
    end
    if exist(fullfile(resDir, 'figures_log.txt'), 'file'), J.figures = 'see res/figures_log.txt'; end
    J.runtime = struct('totalSeconds', tTotal, 'prepareSeconds', L.tPrep);
    say(lg, '\nruntime: prepare %.0f s, total wall %.0f s\n', L.tPrep, tTotal);
    fclose(lg);
    try, txt = jsonencode(J, 'PrettyPrint', true); catch, txt = jsonencode(J); end
    fid = fopen(fullfile(resDir, 'prova_go_results.json'), 'w'); fprintf(fid, '%s\n', txt); fclose(fid);
    out = J;
end
function say(lg, varargin)
    fprintf(1, varargin{:}); if lg > 0, fprintf(lg, varargin{:}); end
end
