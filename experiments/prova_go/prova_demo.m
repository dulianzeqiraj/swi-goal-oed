function dm = prova_demo(seeds)
%PROVA_DEMO  The demonstration truth of figures P1, P3, P5-P7, recomputed in full.
%   dm = PROVA_DEMO(seeds) takes, among the given seeds (default 1:200), the first
%   even seed (coastal strip present) whose true risk under the planned pumping
%   lies in [0.2, 0.8] and whose recharge error |xi_R| >= 0.15 -- a rule on the
%   truth only (an undecided supply question with a recharge-scale error), fixed
%   before looking at any method -- runs PROVA_TRUTH on it keeping every log and
%   iterate, and saves res/prova_demo.mat.
    if nargin < 1 || isempty(seeds), seeds = 1:200; end
    here = prova_go_setup(); resDir = fullfile(here, 'res');
    L = load(fullfile(resDir, 'prova_setup.mat')); M = L.M; S = L.S;
    pick = NaN;
    for s = seeds(mod(seeds, 2) == 0)
        tr = make_truth(M, S, s);
        if tr.riskTrue >= 0.2 && tr.riskTrue <= 0.8 && abs(tr.xiR) >= 0.15, pick = s; break; end
    end
    if isnan(pick)                                        % small test runs: first even seed
        ev = seeds(mod(seeds, 2) == 0); pick = ev(1); tr = make_truth(M, S, pick);
        warning('prova_demo:rule', 'No seed satisfies the demonstration rule; seed %d is used.', pick);
    end
    o = prova_truth(M, S, L.arms, L.tabs, tr, true); dm = o; dm.tr = tr;
    demo = dm; save(fullfile(resDir, 'prova_demo.mat'), 'demo', '-v7');
    fprintf('demonstration truth: seed %d, xi_R %+.3f, true risk %.3f, TRIAL-GO selects A%d\n', pick, tr.xiR, tr.riskTrue, o.pol.trial.sel);
end
