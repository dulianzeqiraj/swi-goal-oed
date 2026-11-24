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
    M = rmfield(M, 'operator');                     % function handles are not saved
    save(setupFile, 'M', 'S', 'D', 'checks', 'arms', 'tabs', 'tPrep', '-v7');
end
