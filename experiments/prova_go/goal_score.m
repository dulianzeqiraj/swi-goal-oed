function sc = goal_score(g, tr, S)
%GOAL_SCORE  Scores of a goal predictive against the truth: coverage of the 90 %
%   intervals, width, absolute error, CRPS (Gaussian closed form) at A and B,
%   joint negative log density (log score, lower is better), absolute error of
%   the intrusion risk and the decision error of "declare safe if risk < 0.1".
    y = tr.Hfut; z = (y - g.mu) ./ g.s;
    sc.cov = abs(z) <= S.z90; sc.width = 2 * S.z90 * g.s; sc.err = abs(y - g.mu);
    phi = exp(-0.5 * z.^2) / sqrt(2 * pi); Phi = 0.5 * erfc(-z / sqrt(2));
    sc.crps = g.s .* (z .* (2 * Phi - 1) + 2 * phi - 1 / sqrt(pi));
    e = y - g.mu; sc.logs = 0.5 * (e' * (g.C \ e)) + 0.5 * log(det(g.C)) + log(2 * pi);
    sc.riskErr = abs(g.risk - tr.riskTrue);
    sc.decErr = (g.risk < 0.1) ~= (tr.riskTrue < 0.1);
    sc.risk = g.risk; sc.mu = g.mu; sc.s = g.s;
end
