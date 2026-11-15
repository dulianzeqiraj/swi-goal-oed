function setupFile = prova_go_prepare(xlsxfile, outDir)
%PROVA_GO_PREPARE  Model, checks, pumping design, robust Gittins tables and the run budget.
%   Saves everything the truth runs need in outDir/prova_setup.mat.
    t0 = tic;
    M = fk_model_setup(xlsxfile); S = prova_settings(M);
    D = pumping_design(M, S); S.Q = D.Q; S.Q0 = D.Q0;
    checks = fk_checks(M, S);
    arms = fk_arms(M, S);
    tabs.main = robust_gittins_table(S.k, S.beta, S.Hor, 101, 80, 401);
    tabs.k02 = robust_gittins_table(S.kSens(1), S.beta, S.Hor, 101, 80, 401);
    tabs.k08 = robust_gittins_table(S.kSens(2), S.beta, S.Hor, 101, 80, 401);
    % qualitative checks of the index (Cohen & Treetanthiploet 2022, Fig. 1)
    nl = [1 2 5 10 20 50 100 200 500 1000]; ks = [0 0.2 0.5 0.8]; bs = [0.9 0.95 0.99];
    G = zeros(numel(ks), numel(bs), numel(nl), 3); pq = [0.1 0.3 0.5];
    for a = 1:numel(ks)
        for b = 1:numel(bs)
            T = robust_gittins_table(ks(a), bs(b), S.Hor, 101, nl, 201);
            for c = 1:3, G(a, b, :, c) = interp1(T.p, T.gam, pq(c)) - pq(c); end
        end
    end
    idxCheck = struct('n', nl, 'k', ks, 'beta', bs, 'p', pq, 'gamMinusP', G);
    % budget: 2.5 x the median cost of calibrating A4 on the heads (pilot truths 100001..100010)
    J = M.J; cst = zeros(10, 1);
    for i = 1:10
        tr = make_truth(M, S, 100000 + i);
        st = lm_init(M, S, arms(4), arms(4).th0, (1:J)', tr.dH, S.sigH * ones(J, 1));
        while ~st.conv, st = lm_iter(M, S, st); end
        cst(i) = st.runs;
    end
    S.costA4pilot = cst'; S.budget = round(S.budgetFactor * median(cst));
    setupFile = fullfile(outDir, 'prova_setup.mat');
    tPrep = toc(t0);
    save(setupFile, 'M', 'S', 'D', 'checks', 'arms', 'tabs', 'idxCheck', 'tPrep', '-v7');
end
