function prova_go_worker(setupFile, seeds, outFile, demoSeed, override)
%PROVA_GO_WORKER  Run PROVA_TRUTH for a list of seeds and save the results (one process).
%   PROVA_GO_WORKER(setupFile, seeds, outFile, demoSeed, override): override is an
%   optional struct of settings that replace those of the setup (e.g.
%   struct('zetaSd', 0) for the supplementary run without the sub-zonal field;
%   the pumping design and the budget are kept).
    L = load(setupFile); M = L.M; S = L.S; arms = L.arms; tabs = L.tabs;
    if nargin >= 5 && ~isempty(override)
        fn = fieldnames(override); for q = 1:numel(fn), S.(fn{q}) = override.(fn{q}); end
    end
    if nargin < 4, demoSeed = NaN; end
    res = cell(1, numel(seeds)); t0 = tic; demo = [];
    for q = 1:numel(seeds)
        tr = make_truth(M, S, seeds(q));
        keep = seeds(q) == demoSeed;
        o = prova_truth(M, S, arms, tabs, tr, keep);
        if keep, demo = o; demo.tr = tr; o = rmfield(o, {'A', 'PL', 'allc', 'methFull', 'cacheKeys', 'cache'}); end
        res{q} = o;
        fprintf('seed %d done (%.0f s): trial arm %d, pest_std cov %d%d, trial cov %d%d\n', seeds(q), toc(t0), ...
                o.meth.trial.arm, o.meth.pest_std.cov, o.meth.trial.cov);
    end
    tRun = toc(t0);
    save(outFile, 'res', 'seeds', 'tRun', 'demo', 'S', '-v7');
end
