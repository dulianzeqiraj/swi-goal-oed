function out = prova_go_run(nTruths, seed0, nWorkers, nSupp, budgetAlt)
%PROVA_GO_RUN  TRIAL-GO on the Fushe-Kuqe model: the whole experiment.
%   out = PROVA_GO_RUN(nTruths, seed0, nWorkers, nSupp)
%     nTruths  : number of synthetic truths (default 200), seeds seed0 .. seed0+nTruths-1
%     seed0    : first seed (default 1); even seeds carry the coastal low-K strip
%     nWorkers : parallel GNU Octave processes (default 4; MATLAB runs serially)
%     nSupp    : truths of the supplementary run without the sub-zonal field
%                (same seeds, zeta = 0; default 100; 0 to skip)
%   Steps: PROVA_GO_PREPARE (model, checks, pumping design, robust Gittins
%   tables, budget) -> PROVA_GO_WORKER on subsets of the seeds -> merge ->
%   PROVA_METRICS -> res/prova_go_results.json and res/prova_go_log.txt.
%   Then PROVA_DEMO (demonstration truth) and PROVA_MAR (MAR process numbers).
%   Figures: MAKE_PROVA_FIGURES (after this run).
    if nargin < 1 || isempty(nTruths), nTruths = 200; end
    if nargin < 2 || isempty(seed0), seed0 = 1; end
    if nargin < 3 || isempty(nWorkers), nWorkers = 4; end
    if nargin < 4 || isempty(nSupp), nSupp = 100; end
    if nargin < 5 || isempty(budgetAlt), budgetAlt = 380; end
    here = prova_go_setup(); resDir = fullfile(here, 'res'); if ~exist(resDir, 'dir'), mkdir(resDir); end
    xlsx = fullfile(here, '..', '..', 'data', 'Fushe_Kuqe_All_Data.xlsx');
    tAll = tic;
    setupFile = fullfile(resDir, 'prova_setup.mat');
    if ~exist(setupFile, 'file'), prova_go_prepare(xlsx, resDir); end
    if ~exist(fullfile(resDir, 'prova_index_check.mat'), 'file')     % checks of the robust index (Fig. 1 of the paper)
        prova_index_check(fullfile(resDir, 'prova_index_check.mat'), 60);
    end
    L = load(setupFile);
    seeds = seed0:seed0 + nTruths - 1;
    runs = {struct('tag', 'main', 'seeds', seeds, 'override', struct())};
    if nSupp > 0, runs{end + 1} = struct('tag', 'nozeta', 'seeds', seeds(1:min(nSupp, end)), 'override', struct('zetaSd', 0)); end
    if nSupp > 0 && budgetAlt > 0
        runs{end + 1} = struct('tag', sprintf('budget%d', budgetAlt), 'seeds', seeds(1:min(nSupp, end)), 'override', struct('budget', budgetAlt));
    end
    for r = 1:numel(runs)
        R = runs{r}; parts = run_parts(here, setupFile, R.seeds, nWorkers, NaN, R.override, fullfile(resDir, ['part_' R.tag]));
        res = {}; tRun = 0;
        for p = 1:numel(parts)
            P = load(parts{p}); res = [res P.res]; tRun = tRun + P.tRun; %#ok<AGROW>
            delete(parts{p});
        end
        demo = []; %#ok<NASGU>
        save(fullfile(resDir, ['prova_' R.tag '.mat']), 'res', 'demo', 'tRun', '-v7');
    end
    prova_demo(seeds);                                   % demonstration truth (rule on the truth only)
    prova_mar();                                         % MAR process on the demonstration truth
    out = prova_go_report(resDir, toc(tAll));
end
function parts = run_parts(here, setupFile, seeds, nW, demoSeed, override, stem)
    isOct = exist('OCTAVE_VERSION', 'builtin') ~= 0;
    if ~isOct || nW <= 1
        parts = {[stem '_1.mat']}; prova_go_worker(setupFile, seeds, parts{1}, demoSeed, override); return
    end
    parts = cell(1, nW); ovf = [stem '_override.mat']; save(ovf, 'override', '-v7');
    for w = 1:nW
        sw = seeds(w:nW:end); parts{w} = sprintf('%s_%d.mat', stem, w);
        if exist(parts{w}, 'file'), delete(parts{w}); end
        cmd = sprintf(['cd(''%s''); prova_go_setup(); O = load(''%s''); ' ...
                       'prova_go_worker(''%s'', %s, ''%s'', NaN, O.override);'], here, ovf, setupFile, mat2str(sw), parts{w});
        system(sprintf('octave --no-gui --eval "%s" > "%s_%d.log" 2>&1 &', cmd, stem, w));
    end
    while ~all(cellfun(@(f) exist(f, 'file') == 2, parts)), pause(5); end
    pause(2);
end
