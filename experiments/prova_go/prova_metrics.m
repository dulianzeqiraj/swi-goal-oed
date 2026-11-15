function R = prova_metrics(res, methods)
%PROVA_METRICS  Metrics over truths, 95 % intervals and paired differences vs TRIAL-GO.
%   R = PROVA_METRICS(res, methods): res is the cell array of PROVA_TRUTH outputs.
%   Coverage and decision-error rates: Wilson 95 % binomial intervals. Means:
%   mean +- 1.96 standard errors. Paired differences TRIAL-GO minus comparator,
%   per truth, then mean +- 1.96 SE (positive = TRIAL-GO larger).
    n = numel(res); R.n = n;
    strip = cellfun(@(o) o.hasStrip, res);
    R.nStrip = nnz(strip);
    for q = 1:numel(methods)
        mn = methods{q};
        X = cellfun(@(o) o.meth.(mn), res);
        cov = reshape([X.cov], 2, n)'; wid = reshape([X.width], 2, n)'; err = reshape([X.err], 2, n)';
        crps = reshape([X.crps], 2, n)'; logs = [X.logs]'; rE = [X.riskErr]'; dE = double([X.decErr]');
        runs = [X.runs]'; arm = [X.arm]';
        m.covA = wilson(sum(cov(:, 1)), n); m.covB = wilson(sum(cov(:, 2)), n);
        m.covAB = wilson(sum(cov(:)), 2 * n);
        m.covA_strip = wilson(sum(cov(strip, 1)), nnz(strip)); m.covB_strip = wilson(sum(cov(strip, 2)), nnz(strip));
        m.covA_nostrip = wilson(sum(cov(~strip, 1)), nnz(~strip)); m.covB_nostrip = wilson(sum(cov(~strip, 2)), nnz(~strip));
        m.widthA = mci(wid(:, 1)); m.widthB = mci(wid(:, 2));
        m.maeA = mci(err(:, 1)); m.maeB = mci(err(:, 2));
        m.crpsA = mci(crps(:, 1)); m.crpsB = mci(crps(:, 2));
        m.logScore = mci(logs); m.logScoreMedian = median(logs);
        m.riskAbsErr = mci(rE); m.decErr = wilson(sum(dE), n); m.runs = mci(runs);
        m.runsMedian = median(runs);
        m.armFreq = histc_(arm, 5);
        R.m.(mn) = m;
        D.cov{q} = mean(cov, 2); D.crps{q} = mean(crps, 2); D.mae{q} = mean(err, 2); D.logs{q} = logs;
        D.rE{q} = rE; D.dE{q} = dE; D.runs{q} = runs; D.wid{q} = mean(wid, 2);
    end
    it = find(strcmp(methods, 'trial'));
    fl = {'cov', 'crps', 'mae', 'logs', 'rE', 'dE', 'runs', 'wid'};
    nm = {'coverage', 'crps', 'mae', 'logScore', 'riskAbsErr', 'decErr', 'runs', 'width'};
    for q = 1:numel(methods)
        if q == it, continue; end
        for f = 1:numel(fl)
            d = D.(fl{f}){it} - D.(fl{f}){q};
            pd.(nm{f}) = mci(d);
        end
        R.paired.(methods{q}) = pd;
    end
    mc = cell2mat(cellfun(@(o) o.missConv, res(:), 'UniformOutput', false));
    R.missConv.all = mean(mc, 1); R.missConv.strip = mean(mc(strip, :), 1); R.missConv.nostrip = mean(mc(~strip, :), 1);
    R.missConv.se = std(mc, 0, 1) / sqrt(n);
    R.costConv = mean(cell2mat(cellfun(@(o) o.costConv, res(:), 'UniformOutput', false)), 1);
    R.nIterConv = mean(cell2mat(cellfun(@(o) o.nIter, res(:), 'UniformOutput', false)), 1);
    R.riskTrue = mci(cellfun(@(o) o.riskTrue, res(:)));
    R.fracTrueSafe = mean(cellfun(@(o) o.riskTrue, res(:)) < 0.1);
    pols = fieldnames(res{1}.pol);
    for q = 1:numel(pols)
        P = cellfun(@(o) o.pol.(pols{q}), res);
        R.pol.(pols{q}).meanItems = mean(reshape([P.n], 5, n), 2)';
        R.pol.(pols{q}).meanBanditRuns = mean([P.runs]); R.pol.(pols{q}).meanCondRuns = mean([P.condRuns]);
        R.pol.(pols{q}).selFreq = histc_([P.sel]', 5);
        R.pol.(pols{q}).selFreqStrip = histc_([P(strip).sel]', 5);
        R.pol.(pols{q}).selFreqNoStrip = histc_([P(~strip).sel]', 5);
    end
end
function w = wilson(k, n)
    z = 1.959963984540054; p = k / max(n, 1);
    c = (p + z^2 / (2 * n)) / (1 + z^2 / n); h = z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2)) / (1 + z^2 / n);
    w = [p c - h c + h];
end
function v = mci(x)
    x = x(isfinite(x)); n = numel(x); m = mean(x); se = std(x) / sqrt(max(n, 1));
    v = [m m - 1.959963984540054 * se m + 1.959963984540054 * se];
end
function h = histc_(a, K)
    h = zeros(1, K); for k = 1:K, h(k) = nnz(a == k); end
end
