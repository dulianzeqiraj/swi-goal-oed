function prova_go_worker(setupFile, seeds, outFile, demoSeed)
%PROVA_GO_WORKER  Run PROVA_TRUTH for a list of seeds and save the results (one process).
    L = load(setupFile); M = L.M; S = L.S; arms = L.arms; tabs = L.tabs;
    res = cell(1, numel(seeds)); t0 = tic; demo = [];
    for q = 1:numel(seeds)
        tr = make_truth(M, S, seeds(q));
        keep = nargin >= 4 && seeds(q) == demoSeed;
        o = prova_truth(M, S, arms, tabs, tr, keep);
        if keep, demo = o; demo.tr = tr; o = rmfield(o, {'A', 'PL', 'allc', 'methFull', 'cacheKeys'}); end
        res{q} = o;
        fprintf('seed %d done (%.0f s): trial arm %d, pest_std cov %d%d, trial cov %d%d\n', seeds(q), toc(t0), ...
                o.meth.trial.arm, o.meth.pest_std.cov, o.meth.trial.cov);
    end
    tRun = toc(t0);
    save(outFile, 'res', 'seeds', 'tRun', 'demo', '-v7');
end
